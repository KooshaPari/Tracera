import Editor, { useMonaco } from '@monaco-editor/react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { useEffect, useState } from 'react';

import { Card, cn } from '@tracertm/ui';

interface GherkinEditorProps {
  content: string;
  onChange?: (content: string) => void;
  onValidation?: (isValid: boolean, errors: ValidationError[]) => void;
  className?: string;
  height?: string;
  showSuggestions?: boolean;
  readOnly?: boolean;
}

export interface ValidationError {
  line: number;
  message: string;
  severity: 'error' | 'warning';
}

const STEP_DEFINITIONS = [
  'Given I am on the login page',
  'Given I have entered valid credentials',
  'Given the system is initialized',
  'When I click the login button',
  'When I enter the password',
  'When I wait for the page to load',
  'Then I should see the dashboard',
  'Then I should be logged in',
  'Then the error message should be displayed',
  'And I should see a confirmation message',
  'But I should not have access to admin features',
];

const KEYWORDS = [
  'Feature:',
  'Background:',
  'Scenario:',
  'Scenario Outline:',
  'Examples:',
  'Given',
  'When',
  'Then',
  'And',
  'But',
];

export function GherkinEditor({
  content,
  onChange,
  onValidation,
  className,
  height = '400px',
  showSuggestions = true,
  readOnly = false,
}: GherkinEditorProps) {
  const monaco = useMonaco();
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);

  // Setup Monaco editor configuration
  useEffect(() => {
    if (!monaco) {
      return;
    }

    // Register custom language for Gherkin if needed
    monaco.languages.register({ id: 'gherkin' });

    // Setup auto-completion
    if (showSuggestions) {
      monaco.languages.registerCompletionItemProvider('gherkin', {
        provideCompletionItems: (_model, position) => {
          const wordRange = {
            endColumn: position.column,
            endLineNumber: position.lineNumber,
            startColumn: 1,
            startLineNumber: position.lineNumber,
          };
          const suggestions = [
            ...KEYWORDS.map((keyword) => ({
              insertText: keyword,
              kind: monaco.languages.CompletionItemKind.Keyword,
              label: keyword,
              range: wordRange,
              sortText: `1-${keyword}`,
            })),
            ...STEP_DEFINITIONS.map((step) => ({
              insertText: step,
              kind: monaco.languages.CompletionItemKind.Snippet,
              label: step,
              range: wordRange,
              sortText: `2-${step}`,
            })),
          ];
          return { suggestions };
        },
      });
    }
  }, [monaco, showSuggestions]);

  // Validate Gherkin content
  const validateGherkin = (text: string) => {
    const errors: ValidationError[] = [];
    const lines = text.split('\n');

    lines.forEach((line, index) => {
      const trimmed = line.trim();
      const lineNumber = index + 1;

      // Check for unmatched quotes
      if ((trimmed.match(/"/g) ?? []).length % 2 !== 0) {
        errors.push({
          line: lineNumber,
          message: 'Unmatched quote mark (")',
          severity: 'error',
        });
      }

      // Check for invalid step keywords
      const stepKeywords = ['Given', 'When', 'Then', 'And', 'But'];
      const hasValidKeyword = stepKeywords.some((kw) => trimmed.startsWith(kw));

      if (
        trimmed &&
        !trimmed.startsWith('#') &&
        !trimmed.startsWith('Feature:') &&
        !trimmed.startsWith('Scenario:') &&
        !trimmed.startsWith('Scenario Outline:') &&
        !trimmed.startsWith('Background:') &&
        !trimmed.startsWith('Examples:') &&
        !trimmed.startsWith('|') &&
        !hasValidKeyword &&
        trimmed.length > 0
      ) {
        if (!trimmed.startsWith('@')) {
          errors.push({
            line: lineNumber,
            message: 'Line should start with a Gherkin keyword or tag',
            severity: 'warning',
          });
        }
      }
    });

    setValidationErrors(errors);
    onValidation?.(errors.length === 0, errors);
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value === undefined) {
      return;
    }
    onChange?.(value);
    validateGherkin(value);
  };

  const hasErrors = validationErrors.some((e) => e.severity === 'error');
  const hasWarnings = validationErrors.some((e) => e.severity === 'warning');

  return (
    <div className={cn('space-y-3', className)}>
      <Card className='border-border/50 overflow-hidden border'>
        <Editor
          height={height}
          defaultLanguage='gherkin'
          value={content}
          onChange={handleEditorChange}
          theme='vs-dark'
          options={{
            bracketPairColorization: {
              enabled: true,
            },
            fontFamily: "'JetBrains Mono','Fira Code',monospace",
            fontSize: 13,
            lineNumbers: 'on',
            minimap: { enabled: false },
            padding: { bottom: 16, top: 16 },
            quickSuggestions: {
              comments: false,
              other: showSuggestions,
              strings: false,
            },
            readOnly,
            renderLineHighlight: 'none',
            scrollBeyondLastLine: false,
            suggestOnTriggerCharacters: showSuggestions,
            wordWrap: 'on',
          }}
        />
      </Card>

      {/* Validation Indicators */}
      {validationErrors.length > 0 && (
        <div className='space-y-2'>
          <div className='flex items-center gap-2'>
            {hasErrors && (
              <div className='flex items-center gap-1 text-sm text-red-600'>
                <AlertCircle className='h-4 w-4' />
                <span>{validationErrors.filter((e) => e.severity === 'error').length} errors</span>
              </div>
            )}
            {hasWarnings && !hasErrors && (
              <div className='flex items-center gap-1 text-sm text-amber-600'>
                <AlertCircle className='h-4 w-4' />
                <span>
                  {validationErrors.filter((e) => e.severity === 'warning').length} warnings
                </span>
              </div>
            )}
            {validationErrors.length === 0 && (
              <div className='flex items-center gap-1 text-sm text-green-600'>
                <CheckCircle2 className='h-4 w-4' />
                <span>Valid Gherkin</span>
              </div>
            )}
          </div>

          {/* Error List */}
          {validationErrors.length > 0 && (
            <Card className='bg-muted/30 border-border/50 border p-3'>
              <div className='max-h-48 space-y-1 overflow-y-auto'>
                {validationErrors.map((error, idx) => (
                  <div key={idx} className='text-xs'>
                    <span className='text-muted-foreground font-mono'>Line {error.line}:</span>
                    <span
                      className={cn(
                        'ml-2',
                        error.severity === 'error' ? 'text-red-600' : 'text-amber-600',
                      )}
                    >
                      {error.message}
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      )}

      {/* Suggestions Panel */}
      {showSuggestions && (
        <Card className='bg-muted/30 border-border/50 border p-4'>
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-xs font-semibold uppercase'>
              Available Steps
            </h4>
            <div className='grid max-h-40 grid-cols-2 gap-2 overflow-y-auto'>
              {STEP_DEFINITIONS.slice(0, 8).map((step) => (
                <button
                  key={step}
                  onClick={() => {
                    const newContent = `${content}\n${step}`;
                    handleEditorChange(newContent);
                  }}
                  className='border-border/50 hover:bg-muted/50 truncate rounded border px-2 py-1 text-left text-xs transition-colors'
                  title={step}
                >
                  {step}
                </button>
              ))}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
