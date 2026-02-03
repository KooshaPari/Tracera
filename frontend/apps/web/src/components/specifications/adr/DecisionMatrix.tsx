import type { ADROption } from "@tracertm/types";
import {
	Badge,
	Button,
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@tracertm/ui";
import { ArrowUp, Check, Edit2, Plus, X } from "lucide-react";
import { useState } from "react";

interface DecisionMatrixProps {
	options: ADROption[];
	onOptionEdit?: (option: ADROption) => void;
	onOptionAdd?: () => void;
	onOptionRemove?: (optionId: string) => void;
	className?: string;
	editable?: boolean;
	showScoring?: boolean;
}

function calculateScore(option: ADROption): number {
	const prosCount = option.pros?.length || 0;
	const consCount = option.cons?.length || 0;
	return Math.max(0, (prosCount - consCount) * 10);
}

export function DecisionMatrix({
	options,
	onOptionEdit,
	onOptionAdd,
	onOptionRemove,
	className,
	editable = false,
	showScoring = false,
}: DecisionMatrixProps) {
	const [sortBy, setSortBy] = useState<"chosen" | "pros" | "cons">("chosen");

	if (!options || options.length === 0) {
		return (
			<Card className={className}>
				<CardContent className="flex items-center justify-center h-40">
					<div className="text-center text-muted-foreground">
						<Plus className="h-8 w-8 mx-auto mb-2 opacity-20" />
						<p className="text-sm">No options considered yet</p>
						{editable && onOptionAdd && (
							<Button
								variant="outline"
								size="sm"
								className="mt-3 gap-1"
								onClick={onOptionAdd}
							>
								<Plus className="w-3 h-3" />
								Add Option
							</Button>
						)}
					</div>
				</CardContent>
			</Card>
		);
	}

	// Sort options
	const sortedOptions = [...options].toSorted((a, b) => {
		switch (sortBy) {
			case "chosen": {
				return a.isChosen ? -1 : (b.isChosen ? 1 : 0);
			}
			case "pros": {
				return (b.pros?.length || 0) - (a.pros?.length || 0);
			}
			case "cons": {
				return (a.cons?.length || 0) - (b.cons?.length || 0);
			}
			default: {
				return 0;
			}
		}
	});

	return (
		<Card className={className}>
			<CardHeader className="flex flex-row items-center justify-between pb-3">
				<CardTitle className="text-sm font-medium uppercase tracking-wider text-muted-foreground">
					Considered Options
				</CardTitle>
				<div className="flex items-center gap-2">
					<span className="text-xs text-muted-foreground">Sort by:</span>
					<select
						value={sortBy}
						onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
						className="text-xs border border-border rounded px-2 py-1 bg-background"
					>
						<option value="chosen">Chosen First</option>
						<option value="pros">Most Pros</option>
						<option value="cons">Fewest Cons</option>
					</select>
					{editable && onOptionAdd && (
						<Button
							variant="outline"
							size="sm"
							className="h-7 gap-1 text-xs ml-2"
							onClick={onOptionAdd}
						>
							<Plus className="w-3 h-3" />
							Add
						</Button>
					)}
				</div>
			</CardHeader>

			<CardContent className="overflow-x-auto">
				<table className="w-full text-sm">
					<thead>
						<tr className="border-b border-border">
							<th className="text-left p-3 font-semibold w-[25%]">Option</th>
							<th className="text-left p-3 font-semibold w-[25%]">Pros</th>
							<th className="text-left p-3 font-semibold w-[25%]">Cons</th>
							{showScoring && (
								<th className="text-right p-3 font-semibold w-[15%]">Score</th>
							)}
							{editable && (
								<th className="text-right p-3 font-semibold w-[10%]">
									Actions
								</th>
							)}
						</tr>
					</thead>
					<tbody>
						{sortedOptions.map((option) => (
							<tr
								key={option.id}
								className={`border-b border-border/50 hover:bg-muted/30 transition-colors ${
									option.isChosen
										? "bg-primary/5 border-l-2 border-l-primary"
										: ""
								}`}
							>
								{/* Option Name */}
								<td className="align-top p-3">
									<div className="flex items-start gap-2">
										{option.isChosen && (
											<ArrowUp className="w-4 h-4 text-primary shrink-0 mt-0.5" />
										)}
										<div>
											<div className="flex items-center gap-2">
												<span className="font-semibold">{option.title}</span>
												{option.isChosen && (
													<Badge
														variant="default"
														className="text-[10px] h-5 px-1.5 gap-1"
													>
														<Check className="w-3 h-3" />
														Chosen
													</Badge>
												)}
											</div>
											<p className="text-xs text-muted-foreground mt-1">
												{option.description}
											</p>
										</div>
									</div>
								</td>

								{/* Pros */}
								<td className="align-top p-3">
									<ul className="space-y-1.5">
										{option.pros && option.pros.length > 0 ? (
											option.pros.map((pro, i) => (
												<li
													key={i}
													className="text-xs flex items-start gap-1.5 text-muted-foreground"
												>
													<Check className="w-3 h-3 text-green-500 shrink-0 mt-0.5" />
													<span>{pro}</span>
												</li>
											))
										) : (
											<li className="text-xs text-muted-foreground italic opacity-50">
												No pros listed
											</li>
										)}
									</ul>
								</td>

								{/* Cons */}
								<td className="align-top p-3">
									<ul className="space-y-1.5">
										{option.cons && option.cons.length > 0 ? (
											option.cons.map((con, i) => (
												<li
													key={i}
													className="text-xs flex items-start gap-1.5 text-muted-foreground"
												>
													<X className="w-3 h-3 text-red-500 shrink-0 mt-0.5" />
													<span>{con}</span>
												</li>
											))
										) : (
											<li className="text-xs text-muted-foreground italic opacity-50">
												No cons listed
											</li>
										)}
									</ul>
								</td>

								{/* Score */}
								{showScoring && (
									<td className="align-top text-right p-3">
										<div className="flex flex-col items-end gap-1">
											<span
												className={`text-sm font-bold ${
													calculateScore(option) > 0
														? "text-green-600"
														: (calculateScore(option) < 0
															? "text-red-600"
															: "text-muted-foreground")
												}`}
											>
												{calculateScore(option) > 0 ? "+" : ""}
												{calculateScore(option)}
											</span>
											<span className="text-xs text-muted-foreground">
												{(option.pros?.length || 0) -
													(option.cons?.length || 0)}{" "}
												net
											</span>
										</div>
									</td>
								)}

								{/* Actions */}
								{editable && (
									<td className="align-top text-right p-3">
										<div className="flex items-center justify-end gap-1">
											{onOptionEdit && (
												<Button
													variant="ghost"
													size="sm"
													className="h-6 w-6 p-0"
													onClick={() => onOptionEdit(option)}
													title="Edit option"
												>
													<Edit2 className="w-3 h-3" />
												</Button>
											)}
											{onOptionRemove && (
												<Button
													variant="ghost"
													size="sm"
													className="h-6 w-6 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
													onClick={() => onOptionRemove(option.id)}
													title="Remove option"
												>
													<X className="w-3 h-3" />
												</Button>
											)}
										</div>
									</td>
								)}
							</tr>
						))}
					</tbody>
				</table>
			</CardContent>
		</Card>
	);
}
