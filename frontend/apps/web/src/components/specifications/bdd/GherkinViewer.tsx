import Editor from "@monaco-editor/react";
import { Badge, Button, Card } from "@tracertm/ui";
import { ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";
import { cn } from "@tracertm/ui";
import { StepBadge } from "./StepBadge";
import type { StepType } from "./StepBadge";

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
	scenarios: Array<{
		type: "Scenario" | "Scenario Outline";
		title: string;
		steps: Array<{
			keyword: StepType;
			text: string;
		}>;
		examples?: string;
	}>;
}

function parseGherkin(content: string): ParsedGherkin {
	const result: ParsedGherkin = { scenarios: [] };
	const lines = content.split("\n");

	let currentScenario: (typeof result.scenarios)[0] | null = null;
	let inBackground = false;
	const background: string[] = [];

	for (const line of lines) {
		const trimmed = line.trim();

		if (!trimmed || trimmed.startsWith("#")) continue;

		// Feature
		if (trimmed.startsWith("Feature:")) {
			result.feature = trimmed.replace("Feature:", "").trim();
		}

		// Background
		if (trimmed.startsWith("Background:")) {
			inBackground = true;
			continue;
		}

		if (inBackground) {
			if (trimmed.startsWith("Scenario")) {
				inBackground = false;
				result.background = background;
			} else if (
				trimmed.startsWith("Given") ||
				trimmed.startsWith("When") ||
				trimmed.startsWith("Then") ||
				trimmed.startsWith("And") ||
				trimmed.startsWith("But")
			) {
				background.push(trimmed);
			}
		}

		// Scenario
		if (
			trimmed.startsWith("Scenario:") ||
			trimmed.startsWith("Scenario Outline:")
		) {
			if (currentScenario) {
				result.scenarios.push(currentScenario);
			}

			const isOutline = trimmed.startsWith("Scenario Outline:");
			currentScenario = {
				type: isOutline ? "Scenario Outline" : "Scenario",
				title: trimmed
					.replace("Scenario Outline:", "")
					.replace("Scenario:", "")
					.trim(),
				steps: [],
			};
		}

		// Steps
		if (
			currentScenario &&
			(trimmed.startsWith("Given") ||
				trimmed.startsWith("When") ||
				trimmed.startsWith("Then") ||
				trimmed.startsWith("And") ||
				trimmed.startsWith("But"))
		) {
			const keyword = trimmed.split(/\s+/)[0] as StepType;
			const text = trimmed.substring(keyword.length).trim();
			currentScenario.steps.push({ keyword, text });
		}

		// Examples
		if (trimmed.startsWith("Examples:") && currentScenario) {
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
	height = "400px",
	collapsible = true,
	showLineNumbers = true,
}: GherkinViewerProps) {
	const [expandedScenarios, setExpandedScenarios] = useState<Set<number>>(
		new Set([0]),
	);

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
			<Card
				className={cn("overflow-hidden border border-border/50", className)}
			>
				<Editor
					height={height}
					defaultLanguage="gherkin"
					value={content}
					theme="vs-dark"
					options={{
						readOnly: true,
						minimap: { enabled: false },
						scrollBeyondLastLine: false,
						fontSize: 13,
						fontFamily: "'JetBrains Mono','Fira Code',monospace",
						lineNumbers: showLineNumbers ? "on" : "off",
						renderLineHighlight: "none",
						padding: { top: 16, bottom: 16 },
					}}
				/>
			</Card>
		);
	}

	return (
		<div className={cn("space-y-4", className)}>
			{/* Feature Header */}
			{parsed.feature && (
				<Card className="p-4 border border-primary/20 bg-primary/5">
					<div className="space-y-2">
						<Badge className="w-fit">Feature</Badge>
						<h2 className="text-xl font-semibold">{parsed.feature}</h2>
					</div>
				</Card>
			)}

			{/* Background */}
			{parsed.background && parsed.background.length > 0 && (
				<Card className="p-4 border border-border/50 bg-muted/30">
					<div className="space-y-3">
						<h3 className="font-semibold text-sm flex items-center gap-2">
							<Badge variant="secondary">Background</Badge>
						</h3>
						<div className="space-y-2">
							{parsed.background.map((step, idx) => {
								const keyword = step.split(/\s+/)[0] as StepType;
								const text = step.substring(keyword.length).trim();
								return (
									<div key={idx} className="flex items-start gap-3">
										<StepBadge type={keyword} compact />
										<span className="text-sm text-muted-foreground">
											{text}
										</span>
									</div>
								);
							})}
						</div>
					</div>
				</Card>
			)}

			{/* Scenarios */}
			{parsed.scenarios.length > 0 && (
				<div className="space-y-2">
					{parsed.scenarios.map((scenario, idx) => {
						const isExpanded = expandedScenarios.has(idx);

						return (
							<Card
								key={idx}
								className="border border-border/50 overflow-hidden hover:border-primary/30 transition-colors"
							>
								{/* Scenario Header */}
								{collapsible ? (
									<button
										onClick={() => toggleScenario(idx)}
										className="w-full px-4 py-3 flex items-center justify-between hover:bg-muted/30 transition-colors text-left"
									>
										<div className="flex items-center gap-3 flex-1 min-w-0">
											{isExpanded ? (
												<ChevronDown className="w-4 h-4 flex-shrink-0 text-muted-foreground" />
											) : (
												<ChevronRight className="w-4 h-4 flex-shrink-0 text-muted-foreground" />
											)}
											<Badge variant="outline" className="font-mono text-xs">
												{scenario.type === "Scenario Outline"
													? "Outline"
													: "Scenario"}
											</Badge>
											<h4 className="font-semibold text-sm truncate">
												{scenario.title}
											</h4>
										</div>
										<Badge variant="secondary" className="ml-2 text-xs">
											{scenario.steps.length} steps
										</Badge>
									</button>
								) : (
									<div className="px-4 py-3 flex items-center justify-between bg-muted/20">
										<div className="flex items-center gap-3 flex-1 min-w-0">
											<Badge variant="outline" className="font-mono text-xs">
												{scenario.type === "Scenario Outline"
													? "Outline"
													: "Scenario"}
											</Badge>
											<h4 className="font-semibold text-sm truncate">
												{scenario.title}
											</h4>
										</div>
										<Badge variant="secondary" className="ml-2 text-xs">
											{scenario.steps.length} steps
										</Badge>
									</div>
								)}

								{/* Scenario Content */}
								{(!collapsible || isExpanded) && (
									<div className="px-4 py-4 space-y-3 border-t border-border/50 bg-background">
										{/* Steps */}
										<div className="space-y-2">
											{scenario.steps.map((step, stepIdx) => (
												<div
													key={stepIdx}
													className="flex items-start gap-3 p-2 rounded hover:bg-muted/30 transition-colors"
												>
													<StepBadge type={step.keyword} compact />
													<span className="text-sm text-muted-foreground leading-relaxed flex-1">
														{step.text}
													</span>
												</div>
											))}
										</div>

										{/* Examples Note */}
										{scenario.examples && (
											<div className="pt-2 border-t border-border/50">
												<Button
													variant="outline"
													size="sm"
													className="text-xs h-7"
												>
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
				<Card className="overflow-hidden border border-border/50">
					<Editor
						height={height}
						defaultLanguage="gherkin"
						value={content}
						theme="vs-dark"
						options={{
							readOnly: true,
							minimap: { enabled: false },
							scrollBeyondLastLine: false,
							fontSize: 13,
							fontFamily: "'JetBrains Mono','Fira Code',monospace",
							lineNumbers: showLineNumbers ? "on" : "off",
							renderLineHighlight: "none",
							padding: { top: 16, bottom: 16 },
						}}
					/>
				</Card>
			)}
		</div>
	);
}
