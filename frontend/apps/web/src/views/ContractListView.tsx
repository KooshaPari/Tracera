import { useNavigate, useSearch } from "@tanstack/react-router";
import type { FC } from "react";
import type { Contract, ContractStatus } from "@tracertm/types";
import {
	Button,
	Card,
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
	Skeleton,
} from "@tracertm/ui";
import { AlertCircle, Filter, Plus, Search, Shield } from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { toast } from "sonner";
import { ContractCard } from "@/components/specifications/contracts/ContractCard";
import { ContractFiltersBar } from "@/components/specifications/contracts/ContractFiltersBar";
import { CreateContractModal } from "@/components/specifications/contracts/CreateContractModal";
import { VerificationSummaryCards } from "@/components/specifications/contracts/VerificationSummaryCards";
import { useContracts } from "@/hooks/useSpecifications";

interface ContractListViewProps {
	projectId: string;
}

const ContractListView: FC<ContractListViewProps> = ({ projectId }) => {
	const navigate = useNavigate();
	const searchParams = useSearch({ strict: false }) as {
		status?: string;
		type?: string;
	};

	const { data: contractsData, isLoading } = useContracts({ projectId });

	const contracts = useMemo(() => {
		const rawContracts = contractsData?.contracts;
		return Array.isArray(rawContracts) ? rawContracts : [];
	}, [contractsData?.contracts]);

	const [searchQuery, setSearchQuery] = useState("");
	const [statusFilter, setStatusFilter] = useState<ContractStatus | "all">(
		(searchParams.status as ContractStatus) || "all",
	);
	const [typeFilter, setTypeFilter] = useState<string>(
		searchParams.type || "all",
	);
	const [showCreateModal, setShowCreateModal] = useState(false);

	const filteredContracts = useMemo(
		() =>
			contracts.filter((contract) => {
				const matchesStatus =
					statusFilter === "all" || contract.status === statusFilter;
				const matchesType =
					typeFilter === "all" || contract.contractType === typeFilter;
				const query = searchQuery.toLowerCase();
				const matchesQuery =
					contract.title.toLowerCase().includes(query) ||
					contract.contractNumber.toLowerCase().includes(query) ||
					(contract.description?.toLowerCase().includes(query) ?? false);

				return matchesStatus && matchesType && matchesQuery;
			}),
		[contracts, statusFilter, typeFilter, searchQuery],
	);

	const handleContractClick = useCallback(
		(contract: Contract) => {
			navigate({
				params: { contractId: contract.id, projectId },
				to: "/projects/$projectId/contracts/$contractId",
			});
		},
		[navigate, projectId],
	);

	const handleNavigateCreate = useCallback(() => {
		setShowCreateModal(true);
	}, []);

	if (isLoading) {
		return (
			<div className="p-6 space-y-8 animate-pulse">
				<Skeleton className="h-10 w-48" />
				<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
					{[1, 2, 3, 4, 5, 6].map((num) => (
						<Skeleton key={num} className="h-40 rounded-xl" />
					))}
				</div>
			</div>
		);
	}

	return (
		<div className="p-6 space-y-8 max-w-[1600px] mx-auto animate-in fade-in duration-500 pb-20">
			{/* Header */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div>
					<h1 className="text-2xl font-black tracking-tight uppercase">
						Contract Specifications
					</h1>
					<p className="text-sm text-muted-foreground font-medium">
						Manage API contracts, function signatures, and invariants.
					</p>
				</div>
				<Button
					size="sm"
					onClick={handleNavigateCreate}
					className="gap-2 rounded-xl shadow-lg shadow-primary/20"
				>
					<Plus className="h-4 w-4" /> New Contract
				</Button>
			</div>

			{/* Verification Summary */}
			<VerificationSummaryCards contracts={contracts} />

			{/* Filters Bar */}
			<ContractFiltersBar
				searchQuery={searchQuery}
				setSearchQuery={setSearchQuery}
				statusFilter={statusFilter}
				setStatusFilter={setStatusFilter}
				typeFilter={typeFilter}
				setTypeFilter={setTypeFilter}
				contracts={contracts}
			/>

			{/* Contracts Grid */}
			{filteredContracts.length > 0 ? (
				<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
					{filteredContracts.map((contract) => (
						<button
							key={contract.id}
							type="button"
							onClick={() => handleContractClick(contract)}
							className="text-left"
						>
							<ContractCard contract={contract} />
						</button>
					))}
				</div>
			) : (
				<Card className="border-none bg-muted/20 py-12">
					<div className="flex flex-col items-center justify-center text-muted-foreground/40">
						<AlertCircle className="h-12 w-12 mb-4" />
						<p className="text-sm font-medium">No contracts found</p>
						<p className="text-xs text-muted-foreground/50">
							{searchQuery || statusFilter !== "all" || typeFilter !== "all"
								? "Try adjusting your filters"
								: "Create your first contract to get started"}
						</p>
					</div>
				</Card>
			)}

			{/* Create Modal */}
			<CreateContractModal
				isOpen={showCreateModal}
				onClose={() => setShowCreateModal(false)}
			/>
		</div>
	);
};

export default ContractListView;
