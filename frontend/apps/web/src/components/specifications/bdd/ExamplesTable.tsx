import { Badge, Button, Card, cn } from "@tracertm/ui";
import { Plus, Trash2, X } from "lucide-react";
import { useState } from "react";

export type TableExample = Record<string, string>;

interface ExamplesTableProps {
	data: TableExample[];
	columns: string[];
	onDataChange?: (data: TableExample[]) => void;
	onColumnsChange?: (columns: string[]) => void;
	editable?: boolean;
	className?: string;
	title?: string;
}

export function ExamplesTable({
	data,
	columns,
	onDataChange,
	onColumnsChange,
	editable = true,
	className,
	title = "Examples",
}: ExamplesTableProps) {
	const [editingCell, setEditingCell] = useState<{
		rowIndex: number;
		colName: string;
	} | null>(null);
	const [editValue, setEditValue] = useState("");

	const handleCellChange = (
		rowIndex: number,
		colName: string,
		value: string,
	) => {
		const newData = [...data];
		if (!newData[rowIndex]) {
			newData[rowIndex] = {};
		}
		newData[rowIndex][colName] = value;
		onDataChange?.(newData);
	};

	const handleAddRow = () => {
		const newRow: TableExample = {};
		columns.forEach((col) => {
			newRow[col] = "";
		});
		onDataChange?.([...data, newRow]);
	};

	const handleRemoveRow = (rowIndex: number) => {
		const newData = data.filter((_, idx) => idx !== rowIndex);
		onDataChange?.(newData);
	};

	const handleAddColumn = () => {
		const newColName = `Column ${columns.length + 1}`;
		onColumnsChange?.([...columns, newColName]);

		// Add empty values to all rows
		const newData = data.map((row) => ({
			...row,
			[newColName]: "",
		}));
		onDataChange?.(newData);
	};

	const handleRemoveColumn = (colName: string) => {
		const newColumns = columns.filter((c) => c !== colName);
		onColumnsChange?.(newColumns);

		// Remove column from all rows
		const newData = data.map((row) => {
			const { [colName]: _, ...rest } = row;
			return rest;
		});
		onDataChange?.(newData);
	};

	const handleRenameColumn = (oldName: string, newName: string) => {
		if (!newName.trim() || newName === oldName) {
			return;
		}

		const newColumns = columns.map((c) => (c === oldName ? newName : c));
		onColumnsChange?.(newColumns);

		// Update keys in all rows
		const newData = data.map((row) => {
			const { [oldName]: value, ...rest } = row;
			return {
				...rest,
				[newName]: value || "",
			};
		});
		onDataChange?.(newData);
	};

	return (
		<div className={cn("space-y-3", className)}>
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-2">
					<Badge variant="secondary" className="text-xs">
						<span className="font-semibold">{data.length}</span>
						<span className="ml-1">examples</span>
					</Badge>
				</div>
				{title && (
					<h3 className="text-sm font-semibold text-muted-foreground">
						{title}
					</h3>
				)}
			</div>

			<Card className="overflow-hidden border border-border/50">
				<div className="overflow-x-auto">
					<table className="w-full text-sm">
						{/* Header */}
						<thead className="bg-muted/50 border-b border-border/50">
							<tr>
								{editable && (
									<th className="px-3 py-2 w-10 text-center text-xs font-medium text-muted-foreground">
										#
									</th>
								)}
								{columns.map((col) => (
									<th
										key={col}
										className="px-3 py-2 text-left font-medium text-muted-foreground bg-muted/30 relative group"
									>
										<div className="flex items-center justify-between gap-2 min-w-max">
											<input
												type="text"
												value={col}
												onChange={(e) =>
													handleRenameColumn(col, e.target.value)
												}
												className={cn(
													"text-xs font-semibold bg-transparent border-0 outline-none",
													editable ? "cursor-text" : "cursor-default",
												)}
												disabled={!editable}
											/>
											{editable && (
												<button
													onClick={() => handleRemoveColumn(col)}
													className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-destructive/10 rounded"
													title="Remove column"
												>
													<X className="w-3 h-3 text-destructive" />
												</button>
											)}
										</div>
									</th>
								))}
								{editable && (
									<th className="px-3 py-2 w-10 text-center">
										<button
											onClick={handleAddColumn}
											className="p-1 hover:bg-muted rounded transition-colors"
											title="Add column"
										>
											<Plus className="w-3 h-3 text-muted-foreground" />
										</button>
									</th>
								)}
							</tr>
						</thead>

						{/* Body */}
						<tbody>
							{data.map((row, rowIndex) => (
								<tr
									key={rowIndex}
									className="border-b border-border/50 hover:bg-muted/30 transition-colors"
								>
									{editable && (
										<td className="px-3 py-2 text-center text-xs text-muted-foreground font-mono">
											{rowIndex + 1}
										</td>
									)}
									{columns.map((col) => (
										<td
											key={`${rowIndex}-${col}`}
											className="px-3 py-2 text-xs border-r border-border/25 last:border-r-0"
										>
											{editingCell?.rowIndex === rowIndex &&
											editingCell?.colName === col ? (
												<input
													type="text"
													value={editValue}
													onChange={(e) => setEditValue(e.target.value)}
													onBlur={() => {
														handleCellChange(rowIndex, col, editValue);
														setEditingCell(null);
													}}
													onKeyDown={(e) => {
														if (e.key === "Enter") {
															handleCellChange(rowIndex, col, editValue);
															setEditingCell(null);
														} else if (e.key === "Escape") {
															setEditingCell(null);
														}
													}}
													className="w-full bg-primary/10 border border-primary/30 rounded px-2 py-1 outline-none"
												/>
											) : (
												<div
													onClick={() => {
														if (editable) {
															setEditingCell({ colName: col, rowIndex });
															setEditValue(row[col] || "");
														}
													}}
													className={cn(
														"px-2 py-1 rounded",
														editable ? "cursor-text hover:bg-muted/50" : "",
													)}
												>
													{row[col] || (
														<span className="text-muted-foreground/50">—</span>
													)}
												</div>
											)}
										</td>
									))}
									{editable && (
										<td className="px-3 py-2 text-center">
											<button
												onClick={() => handleRemoveRow(rowIndex)}
												className="p-1 hover:bg-destructive/10 rounded transition-colors"
												title="Remove row"
											>
												<Trash2 className="w-3 h-3 text-destructive" />
											</button>
										</td>
									)}
								</tr>
							))}
						</tbody>
					</table>
				</div>
			</Card>

			{editable && data.length === 0 && (
				<div className="text-center py-6 text-sm text-muted-foreground">
					<p>No examples yet</p>
				</div>
			)}

			{editable && (
				<Button
					onClick={handleAddRow}
					variant="outline"
					size="sm"
					className="w-full gap-2"
				>
					<Plus className="w-4 h-4" />
					Add Example
				</Button>
			)}
		</div>
	);
}
