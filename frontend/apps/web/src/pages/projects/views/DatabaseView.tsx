import {
	ChevronDown,
	ChevronRight,
	Database,
	Key,
	Link2,
	Table2,
} from "lucide-react";
import { useState } from "react";

interface Column {
	name: string;
	type: string;
	nullable: boolean;
	isPrimary?: boolean;
	isForeign?: boolean;
	references?: string;
}

interface TableDef {
	id: string;
	name: string;
	description: string;
	columns: Column[];
	rowCount: number;
}

const tables: TableDef[] = [
	{
		id: "1",
		name: "projects",
		description: "Project containers",
		rowCount: 12,
		columns: [
			{ name: "id", type: "UUID", nullable: false, isPrimary: true },
			{ name: "name", type: "VARCHAR(255)", nullable: false },
			{ name: "description", type: "TEXT", nullable: true },
			{ name: "created_at", type: "TIMESTAMP", nullable: false },
			{ name: "updated_at", type: "TIMESTAMP", nullable: false },
		],
	},
	{
		id: "2",
		name: "items",
		description: "Requirements, code, tests - all item types",
		rowCount: 1847,
		columns: [
			{ name: "id", type: "UUID", nullable: false, isPrimary: true },
			{
				name: "project_id",
				type: "UUID",
				nullable: false,
				isForeign: true,
				references: "projects.id",
			},
			{ name: "view", type: "VARCHAR(50)", nullable: false },
			{ name: "type", type: "VARCHAR(50)", nullable: false },
			{ name: "title", type: "VARCHAR(500)", nullable: false },
			{ name: "description", type: "TEXT", nullable: true },
			{ name: "status", type: "VARCHAR(50)", nullable: false },
			{ name: "priority", type: "VARCHAR(20)", nullable: true },
			{
				name: "parent_id",
				type: "UUID",
				nullable: true,
				isForeign: true,
				references: "items.id",
			},
			{ name: "owner", type: "VARCHAR(255)", nullable: true },
			{ name: "metadata", type: "JSONB", nullable: true },
			{ name: "version", type: "INTEGER", nullable: false },
			{ name: "created_at", type: "TIMESTAMP", nullable: false },
			{ name: "updated_at", type: "TIMESTAMP", nullable: false },
		],
	},
	{
		id: "3",
		name: "links",
		description: "Traceability relationships between items",
		rowCount: 523,
		columns: [
			{ name: "id", type: "UUID", nullable: false, isPrimary: true },
			{
				name: "project_id",
				type: "UUID",
				nullable: false,
				isForeign: true,
				references: "projects.id",
			},
			{
				name: "source_id",
				type: "UUID",
				nullable: false,
				isForeign: true,
				references: "items.id",
			},
			{
				name: "target_id",
				type: "UUID",
				nullable: false,
				isForeign: true,
				references: "items.id",
			},
			{ name: "type", type: "VARCHAR(50)", nullable: false },
			{ name: "description", type: "TEXT", nullable: true },
			{ name: "metadata", type: "JSONB", nullable: true },
			{ name: "created_at", type: "TIMESTAMP", nullable: false },
		],
	},
	{
		id: "4",
		name: "item_history",
		description: "Version history for items",
		rowCount: 4521,
		columns: [
			{ name: "id", type: "UUID", nullable: false, isPrimary: true },
			{
				name: "item_id",
				type: "UUID",
				nullable: false,
				isForeign: true,
				references: "items.id",
			},
			{ name: "version", type: "INTEGER", nullable: false },
			{ name: "data", type: "JSONB", nullable: false },
			{ name: "changed_by", type: "VARCHAR(255)", nullable: true },
			{ name: "created_at", type: "TIMESTAMP", nullable: false },
		],
	},
];

export function DatabaseView() {
	const [expanded, setExpanded] = useState<Set<string>>(new Set(["2"]));

	const toggle = (id: string) => {
		const next = new Set(expanded);
		if (next.has(id)) {
			next.delete(id);
		} else {
			next.add(id);
		}
		setExpanded(next);
	};

	return (
		<div className="space-y-4">
			<div className="flex items-center justify-between">
				<h3 className="text-lg font-semibold">Database View</h3>
				<div className="flex items-center gap-4 text-sm text-muted-foreground">
					<span className="flex items-center gap-1">
						<Database className="h-4 w-4" /> SQLite
					</span>
					<span>{tables.length} tables</span>
					<span>
						{tables.reduce((acc, t) => acc + t.rowCount, 0).toLocaleString()}{" "}
						total rows
					</span>
				</div>
			</div>

			<div className="rounded-lg border">
				{tables.map((table) => (
					<div key={table.id} className="border-b last:border-b-0">
						<div
							className="flex cursor-pointer items-center gap-3 p-4 hover:bg-accent/50"
							onClick={() => toggle(table.id)}
						>
							{expanded.has(table.id) ? (
								<ChevronDown className="h-4 w-4" />
							) : (
								<ChevronRight className="h-4 w-4" />
							)}
							<Table2 className="h-5 w-5 text-emerald-500" />
							<code className="font-medium">{table.name}</code>
							<span className="text-sm text-muted-foreground">
								{table.description}
							</span>
							<span className="ml-auto text-xs text-muted-foreground">
								{table.rowCount.toLocaleString()} rows
							</span>
						</div>
						{expanded.has(table.id) && (
							<div className="border-t bg-muted/20">
								<table className="w-full text-sm">
									<thead>
										<tr className="border-b text-left text-xs text-muted-foreground">
											<th className="p-2 pl-12">Column</th>
											<th className="p-2">Type</th>
											<th className="p-2">Nullable</th>
											<th className="p-2">Constraints</th>
										</tr>
									</thead>
									<tbody>
										{table.columns.map((col) => (
											<tr key={col.name} className="border-b last:border-b-0">
												<td className="p-2 pl-12 font-mono">{col.name}</td>
												<td className="p-2 font-mono text-xs text-blue-600">
													{col.type}
												</td>
												<td className="p-2">{col.nullable ? "YES" : "NO"}</td>
												<td className="p-2 flex items-center gap-2">
													{col.isPrimary && (
														<span className="flex items-center gap-1 text-xs text-yellow-600">
															<Key className="h-3 w-3" /> PK
														</span>
													)}
													{col.isForeign && (
														<span className="flex items-center gap-1 text-xs text-purple-600">
															<Link2 className="h-3 w-3" /> → {col.references}
														</span>
													)}
												</td>
											</tr>
										))}
									</tbody>
								</table>
							</div>
						)}
					</div>
				))}
			</div>
		</div>
	);
}
