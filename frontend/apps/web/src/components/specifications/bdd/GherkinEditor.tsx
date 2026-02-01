import Editor, { useMonaco } from "@monaco-editor/react";
import { Card, cn } from "@tracertm/ui";
import { AlertCircle, CheckCircle2 } from "lucide-react";
import { useEffect, useState } from "react";

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
	severity: "error" | "warning";
}

const STEP_DEFINITIONS = [
	"Given I am on the login page",
	"Given I have entered valid credentials",
	"Given the system is initialized",
	"When I click the login button",
	"When I enter the password",
	"When I wait for the page to load",
	"Then I should see the dashboard",
	"Then I should be logged in",
	"Then the error message should be displayed",
	"And I should see a confirmation message",
	"But I should not have access to admin features",
];

const KEYWORDS = [
	"Feature:",
	"Background:",
	"Scenario:",
	"Scenario Outline:",
	"Examples:",
	"Given",
	"When",
	"Then",
	"And",
	"But",
];

export function GherkinEditor({
	content,
	onChange,
	onValidation,
	className,
	height = "400px",
	showSuggestions = true,
	readOnly = false,
}: GherkinEditorProps) {
	const monaco = useMonaco();
	const [validationErrors, setValidationErrors] = useState<ValidationError[]>(
		[],
	);

	// Setup Monaco editor configuration
	useEffect(() => {
		if (!monaco) return;

		// Register custom language for Gherkin if needed
		monaco.languages.register({ id: "gherkin" });

		// Setup auto-completion
		if (showSuggestions) {
			monaco.languages.registerCompletionItemProvider("gherkin", {
				provideCompletionItems: (_model, position) => {
					const wordRange = {
						startLineNumber: position.lineNumber,
						endLineNumber: position.lineNumber,
						startColumn: 1,
						endColumn: position.column,
					};
					const suggestions = [
						...KEYWORDS.map((keyword) => ({
							label: keyword,
							kind: monaco.languages.CompletionItemKind.Keyword,
							insertText: keyword,
							sortText: `1-${keyword}`,
							range: wordRange,
						})),
						...STEP_DEFINITIONS.map((step) => ({
							label: step,
							kind: monaco.languages.CompletionItemKind.Snippet,
							insertText: step,
							sortText: `2-${step}`,
							range: wordRange,
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
		const lines = text.split("\n");

		lines.forEach((line, index) => {
			const trimmed = line.trim();
			const lineNumber = index + 1;

			// Check for unmatched quotes
			if ((trimmed.match(/"/g) || []).length % 2 !== 0) {
				errors.push({
					line: lineNumber,
					message: 'Unmatched quote mark (")',
					severity: "error",
				});
			}

			// Check for invalid step keywords
			const stepKeywords = ["Given", "When", "Then", "And", "But"];
			const hasValidKeyword = stepKeywords.some((kw) => trimmed.startsWith(kw));

			if (
				trimmed &&
				!trimmed.startsWith("#") &&
				!trimmed.startsWith("Feature:") &&
				!trimmed.startsWith("Scenario:") &&
				!trimmed.startsWith("Scenario Outline:") &&
				!trimmed.startsWith("Background:") &&
				!trimmed.startsWith("Examples:") &&
				!trimmed.startsWith("|") &&
				!hasValidKeyword &&
				trimmed.length > 0
			) {
				if (!trimmed.startsWith("@")) {
					errors.push({
						line: lineNumber,
						message: "Line should start with a Gherkin keyword or tag",
						severity: "warning",
					});
				}
			}
		});

		setValidationErrors(errors);
		onValidation?.(errors.length === 0, errors);
	};

	const handleEditorChange = (value: string | undefined) => {
		if (value === undefined) return;
		onChange?.(value);
		validateGherkin(value);
	};

	const hasErrors = validationErrors.some((e) => e.severity === "error");
	const hasWarnings = validationErrors.some((e) => e.severity === "warning");

	return (
		<div className={cn("space-y-3", className)}>
			<Card className="overflow-hidden border border-border/50">
				<Editor
					height={height}
					defaultLanguage="gherkin"
					value={content}
					onChange={handleEditorChange}
					theme="vs-dark"
					options={{
						readOnly,
						minimap: { enabled: false },
						scrollBeyondLastLine: false,
						fontSize: 13,
						fontFamily: "'JetBrains Mono','Fira Code',monospace",
						lineNumbers: "on",
						renderLineHighlight: "none",
						padding: { top: 16, bottom: 16 },
						suggestOnTriggerCharacters: showSuggestions,
						quickSuggestions: {
							other: showSuggestions,
							comments: false,
							strings: false,
						},
						wordWrap: "on",
						bracketPairColorization: {
							enabled: true,
						},
					}}
				/>
			</Card>

			{/* Validation Indicators */}
			{validationErrors.length > 0 && (
				<div className="space-y-2">
					<div className="flex items-center gap-2">
						{hasErrors && (
							<div className="flex items-center gap-1 text-sm text-red-600">
								<AlertCircle className="w-4 h-4" />
								<span>
									{
										validationErrors.filter((e) => e.severity === "error")
											.length
									}{" "}
									errors
								</span>
							</div>
						)}
						{hasWarnings && !hasErrors && (
							<div className="flex items-center gap-1 text-sm text-amber-600">
								<AlertCircle className="w-4 h-4" />
								<span>
									{
										validationErrors.filter((e) => e.severity === "warning")
											.length
									}{" "}
									warnings
								</span>
							</div>
						)}
						{validationErrors.length === 0 && (
							<div className="flex items-center gap-1 text-sm text-green-600">
								<CheckCircle2 className="w-4 h-4" />
								<span>Valid Gherkin</span>
							</div>
						)}
					</div>

					{/* Error List */}
					{validationErrors.length > 0 && (
						<Card className="bg-muted/30 p-3 border border-border/50">
							<div className="space-y-1 max-h-48 overflow-y-auto">
								{validationErrors.map((error, idx) => (
									<div key={idx} className="text-xs">
										<span className="font-mono text-muted-foreground">
											Line {error.line}:
										</span>
										<span
											className={cn(
												"ml-2",
												error.severity === "error"
													? "text-red-600"
													: "text-amber-600",
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
				<Card className="bg-muted/30 p-4 border border-border/50">
					<div className="space-y-2">
						<h4 className="text-xs font-semibold uppercase text-muted-foreground">
							Available Steps
						</h4>
						<div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
							{STEP_DEFINITIONS.slice(0, 8).map((step) => (
								<button
									key={step}
									onClick={() => {
										const newContent = `${content}\n${step}`;
										handleEditorChange(newContent);
									}}
									className="text-left text-xs px-2 py-1 rounded border border-border/50 hover:bg-muted/50 transition-colors truncate"
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
