import type { SmellType } from "@tracertm/types";
import { Badge, Tooltip, TooltipContent, TooltipTrigger } from "@tracertm/ui";
import { ShieldAlert } from "lucide-react";

interface SmellIndicatorProps {
	smells: SmellType[];
	className?: string;
}

const smellLabels: Record<SmellType, string> = {
	superlative: "Superlative",
	comparative: "Comparative",
	subjective: "Subjective",
	loopholes: "Loophole",
	ambiguous_adverbs: "Ambiguous Adverb",
	negative_statements: "Negative",
	vague_pronouns: "Vague Pronoun",
	open_ended: "Open Ended",
	incomplete_references: "Incomplete Ref",
};

const smellDescriptions: Record<SmellType, string> = {
	superlative: "Avoid absolute terms like 'best', 'fastest', 'highest'.",
	comparative: "Avoid relative terms like 'better', 'faster' without baseline.",
	subjective: "Avoid user-dependent terms like 'user-friendly', 'easy'.",
	loopholes: "Avoid optionality terms like 'if possible', 'as appropriate'.",
	ambiguous_adverbs:
		"Avoid vague qualifiers like 'usually', 'often', 'significantly'.",
	negative_statements:
		"Avoid negative constraints; state what the system SHALL do.",
	vague_pronouns: "Avoid 'it', 'this', 'that' without clear antecedent.",
	open_ended: "Avoid unquantifiable terms like 'et cetera', 'and so on'.",
	incomplete_references: "Avoid 'see documentation' without specific link/ID.",
};

export function SmellIndicator({ smells, className }: SmellIndicatorProps) {
	if (!smells || smells.length === 0) {
		return null;
	}

	return (
		<div className={`flex flex-wrap gap-2 ${className}`}>
			{smells.map((smell) => (
				<Tooltip key={smell}>
					<TooltipTrigger asChild>
						<Badge
							variant="destructive"
							className="cursor-help bg-red-50 text-red-600 border-red-200 hover:bg-red-100 pl-1.5 pr-2 gap-1"
						>
							<ShieldAlert className="w-3 h-3" />
							{smellLabels[smell] || smell}
						</Badge>
					</TooltipTrigger>
					<TooltipContent className="max-w-xs">
						<p className="font-semibold mb-1">{smellLabels[smell]}</p>
						<p className="text-xs text-muted-foreground">
							{smellDescriptions[smell]}
						</p>
					</TooltipContent>
				</Tooltip>
			))}
		</div>
	);
}
