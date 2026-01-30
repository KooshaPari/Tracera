import { useNavigate, useSearch } from "@tanstack/react-router";
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
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui";
import {
	Plus,
	Search,
	Filter,
	Clock,
	TrendingUp,
	Zap,
	Calendar,
	ChevronRight,
} from "lucide-react";
import { useState, useMemo } from "react";
import { toast } from "sonner";
import { ADRCard } from "@/components/specifications/adr/ADRCard";
import { ADRTimeline } from "@/components/specifications/adr/ADRTimeline";
import { ADRGraph } from "@/components/specifications/adr/ADRGraph";
import { useADRs, useCreateADR } from "@/hooks/useSpecifications";
import type { ADR, ADRStatus } from "@tracertm/types";

interface ADRListViewProps {
	projectId: string;
}

export function ADRListView({ projectId }: ADRListViewProps) {
	const navigate = useNavigate();
	const searchParams = useSearch({ strict: false }) as any;

	const { data: adrsData, isLoading } = useADRs({ projectId });
	const adrs = adrsData?.adrs ?? [];
	const createADR = useCreateADR();

	const [showCreateModal, setShowCreateModal] = useState(false);
	const [searchQuery, setSearchQuery] = useState("");
	const [statusFilter, setStatusFilter] = useState<ADRStatus | "all">(
		(searchParams?.status as ADRStatus) || "all",
	);
	const [dateRange, setDateRange] = useState<
		"all" | "week" | "month" | "quarter"
	>((searchParams?.dateRange as any) || "all");
	const [viewMode, setViewMode] = useState<"cards" | "timeline" | "graph">(
		(searchParams?.view as any) || "cards",
	);

	const [newTitle, setNewTitle] = useState("");
	const [newStatus, setNewStatus] = useState<ADRStatus>("proposed");
	const [newContext, setNewContext] = useState("");
	const [newDecision, setNewDecision] = useState("");

	const filteredADRs = useMemo(() => {
		const filtered = adrs.filter((adr: ADR) => {
			const matchesStatus =
				statusFilter === "all" || adr.status === statusFilter;
			const matchesQuery =
				adr.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
				adr.adrNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
				(adr.context?.toLowerCase().includes(searchQuery.toLowerCase()) ??
					false);

			if (!matchesStatus || !matchesQuery) return false;

			// Date range filtering
			if (dateRange !== "all" && adr.date) {
				const adrDate = new Date(adr.date);
				const now = new Date();
				const daysAgo =
					dateRange === "week"
						? 7
						: dateRange === "month"
							? 30
							: dateRange === "quarter"
								? 90
								: 0;

				const cutoffDate = new Date(
					now.getTime() - daysAgo * 24 * 60 * 60 * 1000,
				);
				if (adrDate < cutoffDate) return false;
			}

			return true;
		});

		return filtered.sort((a: ADR, b: ADR) => {
			const dateA = a.date ? new Date(a.date).getTime() : 0;
			const dateB = b.date ? new Date(b.date).getTime() : 0;
			return dateB - dateA;
		});
	}, [adrs, statusFilter, searchQuery, dateRange]);

	const handleCreate = async () => {
		if (!newTitle.trim()) {
			toast.error("Title is required");
			return;
		}
		try {
			await createADR.mutateAsync({
				projectId,
				title: newTitle,
				context: newContext,
				decision: newDecision,
				consequences: "", // Required by CreateADRData
			});
			toast.success("ADR created successfully");
			setNewTitle("");
			setNewContext("");
			setNewDecision("");
			setNewStatus("proposed");
			setShowCreateModal(false);
		} catch {
			toast.error("Failed to create ADR");
		}
	};

	const statusCounts = useMemo(() => {
		const counts = {
			all: filteredADRs.length,
			proposed: filteredADRs.filter((a: ADR) => a.status === "proposed").length,
			accepted: filteredADRs.filter((a: ADR) => a.status === "accepted").length,
			deprecated: filteredADRs.filter((a: ADR) => a.status === "deprecated")
				.length,
			superseded: filteredADRs.filter((a: ADR) => a.status === "superseded")
				.length,
			rejected: filteredADRs.filter((a: ADR) => a.status === "rejected").length,
		};
		return counts;
	}, [filteredADRs]);

	if (isLoading) {
		return (
			<div className="p-6 space-y-8 animate-pulse">
				<Skeleton className="h-10 w-48" />
				<div className="space-y-4">
					{[1, 2, 3, 4, 5].map((i) => (
						<Skeleton key={i} className="h-32 w-full rounded-xl" />
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
						Architecture Decision Records
					</h1>
					<p className="text-sm text-muted-foreground font-medium">
						Track architectural decisions and their compliance status.
					</p>
				</div>
				<Button
					size="sm"
					onClick={() => setShowCreateModal(true)}
					className="gap-2 rounded-xl shadow-lg shadow-primary/20"
				>
					<Plus className="h-4 w-4" /> New ADR
				</Button>
			</div>

			{/* Filters Bar */}
			<Card className="p-3 border-none bg-muted/30 rounded-2xl flex flex-wrap items-center gap-3">
				<div className="relative flex-1 min-w-[250px]">
					<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
					<Input
						placeholder="Search by title, number, or context..."
						className="pl-10 h-10 border-none bg-transparent focus-visible:ring-0"
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
					/>
				</div>

				<div className="h-6 w-px bg-border/50 hidden md:block" />

				<Select
					value={statusFilter}
					onValueChange={(v) => setStatusFilter(v as ADRStatus | "all")}
				>
					<SelectTrigger className="w-[160px] h-10 border-none bg-transparent hover:bg-background/50">
						<div className="flex items-center gap-2">
							<Filter className="h-3.5 w-3.5 text-muted-foreground" />
							<SelectValue placeholder="Status" />
						</div>
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="all">
							All Statuses ({statusCounts.all})
						</SelectItem>
						<SelectItem value="proposed">
							Proposed ({statusCounts.proposed})
						</SelectItem>
						<SelectItem value="accepted">
							Accepted ({statusCounts.accepted})
						</SelectItem>
						<SelectItem value="deprecated">
							Deprecated ({statusCounts.deprecated})
						</SelectItem>
						<SelectItem value="superseded">
							Superseded ({statusCounts.superseded})
						</SelectItem>
						<SelectItem value="rejected">
							Rejected ({statusCounts.rejected})
						</SelectItem>
					</SelectContent>
				</Select>

				<Select
					value={dateRange}
					onValueChange={(v) =>
						setDateRange(v as "all" | "week" | "month" | "quarter")
					}
				>
					<SelectTrigger className="w-[140px] h-10 border-none bg-transparent hover:bg-background/50">
						<div className="flex items-center gap-2">
							<Calendar className="h-3.5 w-3.5 text-muted-foreground" />
							<SelectValue placeholder="Date" />
						</div>
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="all">Any Time</SelectItem>
						<SelectItem value="week">This Week</SelectItem>
						<SelectItem value="month">This Month</SelectItem>
						<SelectItem value="quarter">This Quarter</SelectItem>
					</SelectContent>
				</Select>
			</Card>

			{/* View Mode Tabs */}
			<Tabs value={viewMode} onValueChange={(v: any) => setViewMode(v)}>
				<TabsList className="w-full justify-start bg-transparent border-b border-border/50 rounded-none h-auto p-0">
					<TabsTrigger
						value="cards"
						className="data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
					>
						<TrendingUp className="h-4 w-4 mr-2" />
						Cards
					</TabsTrigger>
					<TabsTrigger
						value="timeline"
						className="data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
					>
						<Clock className="h-4 w-4 mr-2" />
						Timeline
					</TabsTrigger>
					<TabsTrigger
						value="graph"
						className="data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
					>
						<Zap className="h-4 w-4 mr-2" />
						Graph
					</TabsTrigger>
				</TabsList>

				<TabsContent value="cards" className="mt-6">
					{filteredADRs.length > 0 ? (
						<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
							{filteredADRs.map((adr: ADR) => (
								<button
									key={adr.id}
									onClick={() =>
										navigate({
											to: "/projects/$projectId/adrs/$adrId",
											params: { projectId, adrId: adr.id },
										})
									}
									className="text-left"
								>
									<ADRCard adr={adr} showComplianceGauge={true} />
								</button>
							))}
						</div>
					) : (
						<Card className="border-none bg-muted/20 py-12">
							<div className="flex flex-col items-center justify-center text-muted-foreground/40">
								<Zap className="h-12 w-12 mb-4" />
								<p className="text-sm font-medium">No ADRs found</p>
								<p className="text-xs text-muted-foreground/50">
									Create your first ADR to get started
								</p>
							</div>
						</Card>
					)}
				</TabsContent>

				<TabsContent value="timeline" className="mt-6">
					{filteredADRs.length > 0 ? (
						<Card className="border-none bg-card/50 rounded-2xl">
							<ADRTimeline
								adrs={filteredADRs}
								onADRClick={(adr) =>
									navigate({
										to: "/projects/$projectId/adrs/$adrId",
										params: { projectId, adrId: adr.id },
									})
								}
							/>
						</Card>
					) : (
						<Card className="border-none bg-muted/20 py-12">
							<div className="flex flex-col items-center justify-center text-muted-foreground/40">
								<Clock className="h-12 w-12 mb-4" />
								<p className="text-sm font-medium">No timeline data</p>
							</div>
						</Card>
					)}
				</TabsContent>

				<TabsContent value="graph" className="mt-6">
					{filteredADRs.length > 0 ? (
						<Card className="border-none bg-card/50 rounded-2xl h-[600px]">
							<ADRGraph adrs={filteredADRs} />
						</Card>
					) : (
						<Card className="border-none bg-muted/20 py-12">
							<div className="flex flex-col items-center justify-center text-muted-foreground/40">
								<Zap className="h-12 w-12 mb-4" />
								<p className="text-sm font-medium">No graph data</p>
							</div>
						</Card>
					)}
				</TabsContent>
			</Tabs>

			{/* Create Modal */}
			{showCreateModal && (
				<div className="fixed inset-0 z-50 flex items-center justify-center">
					<div
						className="fixed inset-0 bg-black/50 backdrop-blur-sm"
						onClick={() => setShowCreateModal(false)}
					/>
					<div className="relative w-full max-w-2xl rounded-xl border bg-background p-6 shadow-2xl">
						<div className="flex items-center justify-between mb-6">
							<h2 className="text-lg font-semibold">Create New ADR</h2>
							<button
								onClick={() => setShowCreateModal(false)}
								className="rounded-lg p-1 hover:bg-accent"
							>
								<ChevronRight className="h-5 w-5" />
							</button>
						</div>

						<div className="space-y-4">
							<div>
								<label className="block text-sm font-medium mb-1">Title</label>
								<Input
									value={newTitle}
									onChange={(e) => setNewTitle(e.target.value)}
									placeholder="e.g., Use PostgreSQL for persistence"
									className="h-10"
								/>
							</div>

							<div className="grid gap-4 sm:grid-cols-2">
								<div>
									<label className="block text-sm font-medium mb-1">
										Status
									</label>
									<Select
										value={newStatus}
										onValueChange={(v) => setNewStatus(v as ADRStatus)}
									>
										<SelectTrigger className="h-10">
											<SelectValue />
										</SelectTrigger>
										<SelectContent>
											<SelectItem value="proposed">Proposed</SelectItem>
											<SelectItem value="accepted">Accepted</SelectItem>
											<SelectItem value="deprecated">Deprecated</SelectItem>
											<SelectItem value="superseded">Superseded</SelectItem>
											<SelectItem value="rejected">Rejected</SelectItem>
										</SelectContent>
									</Select>
								</div>
							</div>

							<div>
								<label className="block text-sm font-medium mb-1">
									Context
								</label>
								<textarea
									value={newContext}
									onChange={(e) => setNewContext(e.target.value)}
									placeholder="Describe the issue or context that led to this decision..."
									className="w-full h-24 px-3 py-2 rounded-lg border border-input bg-background"
								/>
							</div>

							<div>
								<label className="block text-sm font-medium mb-1">
									Decision
								</label>
								<textarea
									value={newDecision}
									onChange={(e) => setNewDecision(e.target.value)}
									placeholder="Describe the decision that was made..."
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
								<Button
									onClick={handleCreate}
									disabled={createADR.isPending || !newTitle.trim()}
								>
									{createADR.isPending ? "Creating..." : "Create ADR"}
								</Button>
							</div>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}
