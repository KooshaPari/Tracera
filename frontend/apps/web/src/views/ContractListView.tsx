import { useNavigate, useSearch } from "@tanstack/react-router";
import type { Contract, ContractStatus } from "@tracertm/types";
import {
	Button,
	Card,
	Input,
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
	Skeleton,
} from "@tracertm/ui";
import {
	AlertCircle,
	CheckCircle2,
	Filter,
	Plus,
	Search,
	Shield,
	ShieldAlert,
	ShieldCheck,
} from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";
import { ContractCard } from "@/components/specifications/contracts/ContractCard";
import { useContracts } from "@/hooks/useSpecifications";

interface ContractListViewProps {
	projectId: string;
}

export function ContractListView({ projectId }: ContractListViewProps) {
	const navigate = useNavigate();
	const searchParams = useSearch({ strict: false }) as any;

	const { data: contractsData, isLoading } = useContracts({ projectId });
	const contracts = contractsData?.contracts ?? [];

	const [showCreateModal, setShowCreateModal] = useState(false);
	const [searchQuery, setSearchQuery] = useState("");
	const [statusFilter, setStatusFilter] = useState<ContractStatus | "all">(
		(searchParams?.status as ContractStatus) || "all",
	);
	const [typeFilter, setTypeFilter] = useState<string | "all">(
		(searchParams?.type as string) || "all",
	);

	const [newTitle, setNewTitle] = useState("");
	const [newType, setNewType] = useState<string>("api");
	const [newStatus, setNewStatus] = useState<ContractStatus>("draft");
	const [newDescription, setNewDescription] = useState("");

	const filteredContracts = useMemo(() => contracts.filter((contract: Contract) => {
			const matchesStatus =
				statusFilter === "all" || contract.status === statusFilter;
			const matchesType =
				typeFilter === "all" || contract.contractType === typeFilter;
			const matchesQuery =
				contract.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
				contract.contractNumber
					.toLowerCase()
					.includes(searchQuery.toLowerCase()) ||
				(contract.description
					?.toLowerCase()
					.includes(searchQuery.toLowerCase()) ??
					false);

			return matchesStatus && matchesType && matchesQuery;
		}), [contracts, statusFilter, typeFilter, searchQuery]);

	const statusCounts = useMemo(() => ({
			active: contracts.filter((c: Contract) => c.status === "active").length,
			all: contracts.length,
			deprecated: contracts.filter((c: Contract) => c.status === "deprecated")
				.length,
			draft: contracts.filter((c: Contract) => c.status === "draft").length,
			verified: contracts.filter((c: Contract) => c.status === "verified")
				.length,
			violated: contracts.filter((c: Contract) => c.status === "violated")
				.length,
		}), [contracts]);

	const typeCounts = useMemo(() => {
		const counts: Record<string, number> = {};
		contracts.forEach((c: Contract) => {
			counts[c.contractType] = (counts[c.contractType] || 0) + 1;
		});
		return counts;
	}, [contracts]);

	const verificationSummary = useMemo(() => {
		const total = contracts.length;
		const verified = contracts.filter(
			(c: Contract) => c.status === "verified",
		).length;
		const violated = contracts.filter(
			(c: Contract) => c.status === "violated",
		).length;
		const passRate = total > 0 ? ((verified / total) * 100).toFixed(1) : "0";

		return { passRate, total, verified, violated };
	}, [contracts]);

	const handleCreate = async () => {
		if (!newTitle.trim()) {
			toast.error("Title is required");
			return;
		}
		try {
			// API call would go here
			toast.success("Contract created successfully");
			setNewTitle("");
			setNewDescription("");
			setNewType("api");
			setNewStatus("draft");
			setShowCreateModal(false);
		} catch {
			toast.error("Failed to create contract");
		}
	};

	if (isLoading) {
		return (
			<div className="p-6 space-y-8 animate-pulse">
				<Skeleton className="h-10 w-48" />
				<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
					{[1, 2, 3, 4, 5, 6].map((i) => (
						<Skeleton key={i} className="h-40 rounded-xl" />
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
					onClick={() => setShowCreateModal(true)}
					className="gap-2 rounded-xl shadow-lg shadow-primary/20"
				>
					<Plus className="h-4 w-4" /> New Contract
				</Button>
			</div>

			{/* Verification Summary */}
			<div className="grid gap-4 md:grid-cols-4">
				<Card className="border-none bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-950/20 dark:to-blue-900/20">
					<div className="p-4 space-y-2">
						<div className="flex items-center justify-between">
							<span className="text-xs font-medium text-muted-foreground">
								Total Contracts
							</span>
							<Shield className="h-4 w-4 text-blue-600" />
						</div>
						<div className="text-2xl font-bold">
							{verificationSummary.total}
						</div>
					</div>
				</Card>

				<Card className="border-none bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-950/20 dark:to-green-900/20">
					<div className="p-4 space-y-2">
						<div className="flex items-center justify-between">
							<span className="text-xs font-medium text-muted-foreground">
								Verified
							</span>
							<ShieldCheck className="h-4 w-4 text-green-600" />
						</div>
						<div className="text-2xl font-bold">
							{verificationSummary.verified}
						</div>
					</div>
				</Card>

				<Card className="border-none bg-gradient-to-br from-red-50 to-red-100/50 dark:from-red-950/20 dark:to-red-900/20">
					<div className="p-4 space-y-2">
						<div className="flex items-center justify-between">
							<span className="text-xs font-medium text-muted-foreground">
								Violated
							</span>
							<ShieldAlert className="h-4 w-4 text-red-600" />
						</div>
						<div className="text-2xl font-bold">
							{verificationSummary.violated}
						</div>
					</div>
				</Card>

				<Card className="border-none bg-gradient-to-br from-purple-50 to-purple-100/50 dark:from-purple-950/20 dark:to-purple-900/20">
					<div className="p-4 space-y-2">
						<div className="flex items-center justify-between">
							<span className="text-xs font-medium text-muted-foreground">
								Pass Rate
							</span>
							<CheckCircle2 className="h-4 w-4 text-purple-600" />
						</div>
						<div className="text-2xl font-bold">
							{verificationSummary.passRate}%
						</div>
					</div>
				</Card>
			</div>

			{/* Filters Bar */}
			<Card className="p-3 border-none bg-muted/30 rounded-2xl flex flex-wrap items-center gap-3">
				<div className="relative flex-1 min-w-[250px]">
					<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
					<Input
						placeholder="Search by title, number, or description..."
						className="pl-10 h-10 border-none bg-transparent focus-visible:ring-0"
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
					/>
				</div>

				<div className="h-6 w-px bg-border/50 hidden md:block" />

				<Select
					value={statusFilter}
					onValueChange={(v) => setStatusFilter(v as ContractStatus | "all")}
				>
					<SelectTrigger className="w-[140px] h-10 border-none bg-transparent hover:bg-background/50">
						<div className="flex items-center gap-2">
							<Filter className="h-3.5 w-3.5 text-muted-foreground" />
							<SelectValue placeholder="Status" />
						</div>
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="all">All ({statusCounts.all})</SelectItem>
						<SelectItem value="draft">Draft ({statusCounts.draft})</SelectItem>
						<SelectItem value="active">
							Active ({statusCounts.active})
						</SelectItem>
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

				<Select value={typeFilter} onValueChange={(v) => setTypeFilter(v)}>
					<SelectTrigger className="w-[140px] h-10 border-none bg-transparent hover:bg-background/50">
						<div className="flex items-center gap-2">
							<Shield className="h-3.5 w-3.5 text-muted-foreground" />
							<SelectValue placeholder="Type" />
						</div>
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="all">All Types ({contracts.length})</SelectItem>
						<SelectItem value="api">API ({typeCounts.api || 0})</SelectItem>
						<SelectItem value="function">
							Function ({typeCounts.function || 0})
						</SelectItem>
						<SelectItem value="invariant">
							Invariant ({typeCounts.invariant || 0})
						</SelectItem>
						<SelectItem value="data">Data ({typeCounts.data || 0})</SelectItem>
						<SelectItem value="integration">
							Integration ({typeCounts.integration || 0})
						</SelectItem>
					</SelectContent>
				</Select>
			</Card>

			{/* Contracts Grid */}
			{filteredContracts.length > 0 ? (
				<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
					{filteredContracts.map((contract: Contract) => (
						<button
							key={contract.id}
							onClick={() =>
								navigate({
									params: { contractId: contract.id, projectId },
									to: "/projects/$projectId/contracts/$contractId",
								})
							}
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
			{showCreateModal && (
				<div className="fixed inset-0 z-50 flex items-center justify-center">
					<div
						className="fixed inset-0 bg-black/50 backdrop-blur-sm"
						onClick={() => setShowCreateModal(false)}
					/>
					<div
						className="relative w-full max-w-2xl rounded-xl border bg-background p-6 shadow-2xl"
						role="dialog"
						aria-modal="true"
						aria-labelledby="create-contract-title"
					>
						<div className="flex items-center justify-between mb-6">
							<h2 id="create-contract-title" className="text-lg font-semibold">
								Create New Contract
							</h2>
							<button
								type="button"
								onClick={() => setShowCreateModal(false)}
								aria-label="Close dialog"
								className="rounded-lg p-1 hover:bg-accent"
							>
								✕
							</button>
						</div>

						<div className="space-y-4">
							<div>
								<label className="block text-sm font-medium mb-1">Title</label>
								<Input
									value={newTitle}
									onChange={(e) => setNewTitle(e.target.value)}
									placeholder="e.g., User API Contract"
									className="h-10"
								/>
							</div>

							<div className="grid gap-4 sm:grid-cols-2">
								<div>
									<label className="block text-sm font-medium mb-1">Type</label>
									<Select value={newType} onValueChange={setNewType}>
										<SelectTrigger className="h-10">
											<SelectValue />
										</SelectTrigger>
										<SelectContent>
											<SelectItem value="api">API</SelectItem>
											<SelectItem value="function">Function</SelectItem>
											<SelectItem value="invariant">Invariant</SelectItem>
											<SelectItem value="data">Data</SelectItem>
											<SelectItem value="integration">Integration</SelectItem>
										</SelectContent>
									</Select>
								</div>

								<div>
									<label className="block text-sm font-medium mb-1">
										Status
									</label>
									<Select
										value={newStatus}
										onValueChange={(v) => setNewStatus(v as ContractStatus)}
									>
										<SelectTrigger className="h-10">
											<SelectValue />
										</SelectTrigger>
										<SelectContent>
											<SelectItem value="draft">Draft</SelectItem>
											<SelectItem value="active">Active</SelectItem>
											<SelectItem value="verified">Verified</SelectItem>
											<SelectItem value="violated">Violated</SelectItem>
											<SelectItem value="deprecated">Deprecated</SelectItem>
										</SelectContent>
									</Select>
								</div>
							</div>

							<div>
								<label className="block text-sm font-medium mb-1">
									Description
								</label>
								<textarea
									value={newDescription}
									onChange={(e) => setNewDescription(e.target.value)}
									placeholder="Describe the contract..."
									className="w-full h-24 px-3 py-2 rounded-lg border border-input bg-background"
								/>
							</div>

							<div className="flex justify-end gap-2 pt-4">
								<Button
									variant="ghost"
									onClick={() => setShowCreateModal(false)}
								>
									Cancel
								</Button>
								<Button onClick={handleCreate} disabled={!newTitle.trim()}>
									Create Contract
								</Button>
							</div>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}
