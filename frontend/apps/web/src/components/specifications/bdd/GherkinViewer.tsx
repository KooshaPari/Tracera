import Editor from '@monaco-editor/react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';

import { Badge, Button, Card, cn } from '@tracertm/ui';

import type { StepType } from './StepBadge';

import { StepBadge } from './StepBadge';

interface GherkinViewerProps {
  content: string;
  className?: string;
  height?: string;
  collapsible?: boolean;
  showLineNumbers?: boolean;
}

interface ParsedGherkin {
  feature?: string;
  background?: string[];
  scenarios: {
    type: 'Scenario' | 'Scenario Outline';
    title: string;
    steps: {
      keyword: StepType;
      text: string;
    }[];
    examples?: string;
  }[];
}

function parseGherkin(content: string): ParsedGherkin {
  const result: ParsedGherkin = { scenarios: [] };
  const lines = content.split('\n');

  let currentScenario: (typeof result.scenarios)[0] | null = null;
  let inBackground = false;
  const background: string[] = [];

  for (const line of lines) {
    const trimmed = line.trim();

    if (!trimmed || trimmed.startsWith('#')) {
      continue;
    }

    // Feature
    if (trimmed.startsWith('Feature:')) {
      result.feature = trimmed.replace('Feature:', '').trim();
    }

    // Background
    if (trimmed.startsWith('Background:')) {
      inBackground = true;
      continue;
    }

    if (inBackground) {
      if (trimmed.startsWith('Scenario')) {
        inBackground = false;
        result.background = background;
      } else if (
        trimmed.startsWith('Given') ||
        trimmed.startsWith('When') ||
        trimmed.startsWith('Then') ||
        trimmed.startsWith('And') ||
        trimmed.startsWith('But')
      ) {
        background.push(trimmed);
      }
    }

    // Scenario
    if (trimmed.startsWith('Scenario:') || trimmed.startsWith('Scenario Outline:')) {
      if (currentScenario) {
        result.scenarios.push(currentScenario);
      }

      const isOutline = trimmed.startsWith('Scenario Outline:');
      currentScenario = {
        steps: [],
        title: trimmed.replace('Scenario Outline:', '').replace('Scenario:', '').trim(),
        type: isOutline ? 'Scenario Outline' : 'Scenario',
      };
    }

    // Steps
    if (
      currentScenario &&
      (trimmed.startsWith('Given') ||
        trimmed.startsWith('When') ||
        trimmed.startsWith('Then') ||
        trimmed.startsWith('And') ||
        trimmed.startsWith('But'))
    ) {
      const keyword = trimmed.split(/\s+/)[0] as StepType;
      const text = trimmed.slice(keyword.length).trim();
      currentScenario.steps.push({ keyword, text });
    }

    // Examples
    if (trimmed.startsWith('Examples:') && currentScenario) {
      currentScenario.examples = trimmed;
    }
  }

  if (currentScenario) {
    result.scenarios.push(currentScenario);
  }

  return result;
}

export function GherkinViewer({
  content,
  className,
  height = '400px',
  collapsible = true,
  showLineNumbers = true,
}: GherkinViewerProps) {
  const [expandedScenarios, setExpandedScenarios] = useState<Set<number>>(new Set([0]));

  const toggleScenario = (index: number) => {
    const newExpanded = new Set(expandedScenarios);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedScenarios(newExpanded);
  };

  const parsed = parseGherkin(content);

  // If no parsed structure, show raw editor
  if (!parsed.feature && parsed.scenarios.length === 0) {
    return (
      <Card className={cn('overflow-hidden border border-border/50', className)}>
        <Editor
          height={height}
          defaultLanguage='gherkin'
          value={content}
          theme='vs-dark'
          options={{
            fontFamily: "'JetBrains Mono','Fira Code',monospace",
            fontSize: 13,
            lineNumbers: showLineNumbers ? 'on' : 'off',
            minimap: { enabled: false },
            padding: { bottom: 16, top: 16 },
            readOnly: true,
            renderLineHighlight: 'none',
            scrollBeyondLastLine: false,
          }}
        />
      </Card>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Feature Header */}
      {parsed.feature && (
        <Card className='border-primary/20 bg-primary/5 border p-4'>
          <div className='space-y-2'>
            <Badge className='w-fit'>Feature</Badge>
            <h2 className='text-xl font-semibold'>{parsed.feature}</h2>
          </div>
        </Card>
      )}

      {/* Background */}
      {parsed.background && parsed.background.length > 0 && (
        <Card className='border-border/50 bg-muted/30 border p-4'>
          <div className='space-y-3'>
            <h3 className='flex items-center gap-2 text-sm font-semibold'>
              <Badge variant='secondary'>Background</Badge>
            </h3>
            <div className='space-y-2'>
              {parsed.background.map((step, idx) => {
                const keyword = step.split(/\s+/)[0] as StepType;
                const text = step.slice(keyword.length).trim();
                return (
                  <div key={idx} className='flex items-start gap-3'>
                    <StepBadge type={keyword} compact />
                    <span className='text-muted-foreground text-sm'>{text}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </Card>
      )}

      {/* Scenarios */}
      {parsed.scenarios.length > 0 && (
        <div className='space-y-2'>
          {parsed.scenarios.map((scenario, idx) => {
            const isExpanded = expandedScenarios.has(idx);

            return (
              <Card
                key={idx}
                className='border-border/50 hover:border-primary/30 overflow-hidden border transition-colors'
              >
                {/* Scenario Header */}
                {collapsible ? (
                  <button
                    onClick={() => {
                      toggleScenario(idx);
                    }}
                    className='hover:bg-muted/30 flex w-full items-center justify-between px-4 py-3 text-left transition-colors'
                  >
                    <div className='flex min-w-0 flex-1 items-center gap-3'>
                      {isExpanded ? (
                        <ChevronDown className='text-muted-foreground h-4 w-4 flex-shrink-0' />
                      ) : (
                        <ChevronRight className='text-muted-foreground h-4 w-4 flex-shrink-0' />
                      )}
                      <Badge variant='outline' className='font-mono text-xs'>
                        {scenario.type === 'Scenario Outline' ? 'Outline' : 'Scenario'}
                      </Badge>
                      <h4 className='truncate text-sm font-semibold'>{scenario.title}</h4>
                    </div>
                    <Badge variant='secondary' className='ml-2 text-xs'>
                      {scenario.steps.length} steps
                    </Badge>
                  </button>
                ) : (
                  <div className='bg-muted/20 flex items-center justify-between px-4 py-3'>
                    <div className='flex min-w-0 flex-1 items-center gap-3'>
                      <Badge variant='outline' className='font-mono text-xs'>
                        {scenario.type === 'Scenario Outline' ? 'Outline' : 'Scenario'}
                      </Badge>
                      <h4 className='truncate text-sm font-semibold'>{scenario.title}</h4>
                    </div>
                    <Badge variant='secondary' className='ml-2 text-xs'>
                      {scenario.steps.length} steps
                    </Badge>
                  </div>
                )}

                {/* Scenario Content */}
                {(!collapsible || isExpanded) && (
                  <div className='border-border/50 bg-background space-y-3 border-t px-4 py-4'>
                    {/* Steps */}
                    <div className='space-y-2'>
                      {scenario.steps.map((step, stepIdx) => (
                        <div
                          key={stepIdx}
                          className='hover:bg-muted/30 flex items-start gap-3 rounded p-2 transition-colors'
                        >
                          <StepBadge type={step.keyword} compact />
                          <span className='text-muted-foreground flex-1 text-sm leading-relaxed'>
                            {step.text}
                          </span>
                        </div>
                      ))}
                    </div>

                    {/* Examples Note */}
                    {scenario.examples && (
                      <div className='border-border/50 border-t pt-2'>
                        <Button variant='outline' size='sm' className='h-7 text-xs'>
                          {scenario.examples}
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}

      {/* Raw Editor Fallback */}
      {parsed.scenarios.length === 0 && !parsed.feature && (
        <Card className='border-border/50 overflow-hidden border'>
          <Editor
            height={height}
            defaultLanguage='gherkin'
            value={content}
            theme='vs-dark'
            options={{
              fontFamily: "'JetBrains Mono','Fira Code',monospace",
              fontSize: 13,
              lineNumbers: showLineNumbers ? 'on' : 'off',
              minimap: { enabled: false },
              padding: { bottom: 16, top: 16 },
              readOnly: true,
              renderLineHighlight: 'none',
              scrollBeyondLastLine: false,
            }}
          />
        </Card>
      )}
    </div>
  );
}
