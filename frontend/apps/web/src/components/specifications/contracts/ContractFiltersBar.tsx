import { type FC, useCallback, useMemo } from "react";
import { Card, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@tracertm/ui";
import { Filter, Search, Shield } from "lucide-react";
import type { Contract, ContractStatus } from "@tracertm/types";

interface ContractFiltersBarProps {
	readonly searchQuery: string;
	readonly setSearchQuery: (query: string) => void;
	readonly statusFilter: ContractStatus | "all";
	readonly setStatusFilter: (filter: ContractStatus | "all") => void;
	readonly typeFilter: string;
	readonly setTypeFilter: (filter: string) => void;
	readonly contracts: readonly Contract[];
}

export const ContractFiltersBar: FC<ContractFiltersBarProps> = ({
	searchQuery,
	setSearchQuery,
	statusFilter,
	setStatusFilter,
	typeFilter,
	setTypeFilter,
	contracts,
}) => {
	const statusCounts = useMemo(
		() => ({
			active: contracts.filter((c) => c.status === "active").length,
			all: contracts.length,
			deprecated: contracts.filter((c) => c.status === "deprecated").length,
			draft: contracts.filter((c) => c.status === "draft").length,
			verified: contracts.filter((c) => c.status === "verified").length,
			violated: contracts.filter((c) => c.status === "violated").length,
		}),
		[contracts],
	);

	const typeCounts = useMemo(() => {
		const counts: Record<string, number> = {};
		for (const contract of contracts) {
			const type = contract.contractType;
			counts[type] = (counts[type] || 0) + 1;
		}
		return counts;
	}, [contracts]);

	const handleSearchChange = useCallback(
		(event: React.ChangeEvent<HTMLInputElement>) =>
			setSearchQuery(event.target.value),
		[setSearchQuery],
	);

	const handleStatusChange = useCallback(
		(value: string) => setStatusFilter(value as ContractStatus | "all"),
		[setStatusFilter],
	);

	const handleTypeChange = useCallback(
		(value: string) => setTypeFilter(value),
		[setTypeFilter],
	);

	return (
		<Card className="p-3 border-none bg-muted/30 rounded-2xl flex flex-wrap items-center gap-3">
			<div className="relative flex-1 min-w-[250px]">
				<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
				<Input
					placeholder="Search by title, number, or description..."
					className="pl-10 h-10 border-none bg-transparent focus-visible:ring-0"
					value={searchQuery}
					onChange={handleSearchChange}
				/>
			</div>

			<div className="h-6 w-px bg-border/50 hidden md:block" />

			<Select value={statusFilter} onValueChange={handleStatusChange}>
				<SelectTrigger className="w-[140px] h-10 border-none bg-transparent hover:bg-background/50">
					<div className="flex items-center gap-2">
						<Filter className="h-3.5 w-3.5 text-muted-foreground" />
						<SelectValue placeholder="Status" />
					</div>
				</SelectTrigger>
				<SelectContent>
					<SelectItem value="all">All ({statusCounts.all})</SelectItem>
					<SelectItem value="draft">Draft ({statusCounts.draft})</SelectItem>
					<SelectItem value="active">Active ({statusCounts.active})</SelectItem>
					<SelectItem value="verified">
						Verified ({statusCounts.verified})
					</SelectItem>
					<SelectItem value="violated">
						Violated ({statusCounts.violated})
					</SelectItem>
					<SelectItem value="deprecated">
						Deprecated ({statusCounts.deprecated})
					</SelectItem>
				</SelectContent>
			</Select>

			<Select value={typeFilter} onValueChange={handleTypeChange}>
				<SelectTrigger className="w-[140px] h-10 border-none bg-transparent hover:bg-background/50">
					<div className="flex items-center gap-2">
						<Shield className="h-3.5 w-3.5 text-muted-foreground" />
						<SelectValue placeholder="Type" />
					</div>
				</SelectTrigger>
				<SelectContent>
					<SelectItem value="all">All Types ({contracts.length})</SelectItem>
					<SelectItem value="api">API ({typeCounts["api"] ?? 0})</SelectItem>
					<SelectItem value="function">
						Function ({typeCounts["function"] ?? 0})
					</SelectItem>
					<SelectItem value="invariant">
						Invariant ({typeCounts["invariant"] ?? 0})
					</SelectItem>
					<SelectItem value="data">Data ({typeCounts["data"] ?? 0})</SelectItem>
					<SelectItem value="integration">
						Integration ({typeCounts["integration"] ?? 0})
					</SelectItem>
				</SelectContent>
			</Select>
		</Card>
	);
};
