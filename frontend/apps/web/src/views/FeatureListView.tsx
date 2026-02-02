import { useNavigate, useSearch } from "@tanstack/react-router";
import type { Feature, FeatureStatus } from "@tracertm/types";
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
	BookOpen,
	CheckCircle2,
	Filter,
	ListTodo,
	Plus,
	Search,
	TrendingUp,
	XCircle,
} from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";
import { FeatureCard } from "@/components/specifications/bdd/FeatureCard";
import { useFeatures } from "@/hooks/useSpecifications";

interface FeatureListViewProps {
	projectId: string;
}

export function FeatureListView({ projectId }: FeatureListViewProps) {
	const navigate = useNavigate();
	const searchParams = useSearch({ strict: false }) as { status?: string } | undefined;

	const { data: featuresData, isLoading } = useFeatures({ projectId });
	const features = featuresData?.features ?? [];

	const [showCreateModal, setShowCreateModal] = useState(false);
	const [searchQuery, setSearchQuery] = useState("");
	const [statusFilter, setStatusFilter] = useState<FeatureStatus | "all">(
		(searchParams?.status as FeatureStatus) || "all",
	);

	const [newName, setNewName] = useState("");
	const [newStatus, setNewStatus] = useState<FeatureStatus>("draft");
	const [newDescription, setNewDescription] = useState("");

	const filteredFeatures = useMemo(() => features.filter((feature: Feature) => {
			const matchesStatus =
				statusFilter === "all" || feature.status === statusFilter;
			const matchesQuery =
				feature.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
				feature.featureNumber
					.toLowerCase()
					.includes(searchQuery.toLowerCase()) ||
				(feature.description
					?.toLowerCase()
					.includes(searchQuery.toLowerCase()) ??
					false);

			return matchesStatus && matchesQuery;
		}), [features, statusFilter, searchQuery]);

	const statusCounts = useMemo(() => ({
			active: features.filter((f: Feature) => f.status === "active").length,
			all: features.length,
			archived: features.filter((f: Feature) => f.status === "archived").length,
			deprecated: features.filter((f: Feature) => f.status === "deprecated")
				.length,
			draft: features.filter((f: Feature) => f.status === "draft").length,
		}), [features]);

	const overallPassRate = useMemo(() => {
		if (features.length === 0) {return 0;}
		const totalScenarios = features.reduce(
			(sum: number, f: Feature) => sum + (f.scenarioCount || 0),
			0,
		);
		const passedScenarios = features.reduce(
			(sum: number, f: Feature) => sum + (f.passedScenarios || 0),
			0,
		);
		return totalScenarios > 0
			? ((passedScenarios / totalScenarios) * 100).toFixed(1)
			: "0";
	}, [features]);

	const scenarioSummary = useMemo(() => {
		const summary = {
			failed: features.reduce(
				(sum: number, f: Feature) => sum + (f.failedScenarios || 0),
				0,
			),
			passed: features.reduce(
				(sum: number, f: Feature) => sum + (f.passedScenarios || 0),
				0,
			),
			pending: features.reduce(
				(sum: number, f: Feature) => sum + (f.pendingScenarios || 0),
				0,
			),
			total: features.reduce(
				(sum: number, f: Feature) => sum + (f.scenarioCount || 0),
				0,
			),
		};
		return summary;
	}, [features]);

	const handleCreate = async () => {
		if (!newName.trim()) {
			toast.error("Feature name is required");
			return;
		}
		try {
			// API call would go here
			toast.success("Feature created successfully");
			setNewName("");
			setNewDescription("");
			setNewStatus("draft");
			setShowCreateModal(false);
        } catch {
            toast.error("Failed to create feature");
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
						BDD Features
					</h1>
					<p className="text-sm text-muted-foreground font-medium">
						Manage Gherkin features and test scenarios.
					</p>
				</div>
				<Button
					size="sm"
					onClick={() => setShowCreateModal(true)}
					className="gap-2 rounded-xl shadow-lg shadow-primary/20"
				>
					<Plus className="h-4 w-4" /> New Feature
				</Button>
			</div>

			{/* Scenario Summary */}
			<div className="grid gap-4 md:grid-cols-5">
				<Card className="border-none bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-950/20 dark:to-blue-900/20">
					<div className="p-4 space-y-2">
						<div className="flex items-center justify-between">
							<span className="text-xs font-medium text-muted-foreground">
								Total Scenarios
							</span>
							<BookOpen className="h-4 w-4 text-blue-600" />
						</div>
						<div className="text-2xl font-bold">{scenarioSummary.total}</div>
					</div>
				</Card>

				<Card className="border-none bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-950/20 dark:to-green-900/20">
					<div className="p-4 space-y-2">
						<div className="flex items-center justify-between">
							<span className="text-xs font-medium text-muted-foreground">
								Passing
							</span>
							<CheckCircle2 className="h-4 w-4 text-green-600" />
						</div>
						<div className="text-2xl font-bold">{scenarioSummary.passed}</div>
					</div>
				</Card>

				<Card className="border-none bg-gradient-to-br from-red-50 to-red-100/50 dark:from-red-950/20 dark:to-red-900/20">
					<div className="p-4 space-y-2">
						<div className="flex items-center justify-between">
							<span className="text-xs font-medium text-muted-foreground">
								Failing
							</span>
							<XCircle className="h-4 w-4 text-red-600" />
						</div>
						<div className="text-2xl font-bold">{scenarioSummary.failed}</div>
					</div>
				</Card>

				<Card className="border-none bg-gradient-to-br from-yellow-50 to-yellow-100/50 dark:from-yellow-950/20 dark:to-yellow-900/20">
					<div className="p-4 space-y-2">
						<div className="flex items-center justify-between">
							<span className="text-xs font-medium text-muted-foreground">
								Pending
							</span>
							<ListTodo className="h-4 w-4 text-yellow-600" />
						</div>
						<div className="text-2xl font-bold">{scenarioSummary.pending}</div>
					</div>
				</Card>

				<Card className="border-none bg-gradient-to-br from-purple-50 to-purple-100/50 dark:from-purple-950/20 dark:to-purple-900/20">
					<div className="p-4 space-y-2">
						<div className="flex items-center justify-between">
							<span className="text-xs font-medium text-muted-foreground">
								Pass Rate
							</span>
							<TrendingUp className="h-4 w-4 text-purple-600" />
						</div>
						<div className="text-2xl font-bold">{overallPassRate}%</div>
					</div>
				</Card>
			</div>

			{/* Filters Bar */}
			<Card className="p-3 border-none bg-muted/30 rounded-2xl flex flex-wrap items-center gap-3">
				<div className="relative flex-1 min-w-[250px]">
					<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
					<Input
						placeholder="Search by name or feature number..."
						className="pl-10 h-10 border-none bg-transparent focus-visible:ring-0"
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
					/>
				</div>

				<div className="h-6 w-px bg-border/50 hidden md:block" />

				<Select
					value={statusFilter}
					onValueChange={(v) => setStatusFilter(v as FeatureStatus | "all")}
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
						<SelectItem value="deprecated">
							Deprecated ({statusCounts.deprecated})
						</SelectItem>
						<SelectItem value="archived">
							Archived ({statusCounts.archived})
						</SelectItem>
					</SelectContent>
				</Select>
			</Card>

			{/* Features Grid */}
			{filteredFeatures.length > 0 ? (
				<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
					{filteredFeatures.map((feature: Feature) => (
						<button
							key={feature.id}
							onClick={() =>
								navigate({
									params: { featureId: feature.id, projectId },
									to: "/projects/$projectId/features/$featureId",
								})
							}
							className="text-left"
						>
							<FeatureCard feature={feature} />
						</button>
					))}
				</div>
			) : (
				<Card className="border-none bg-muted/20 py-12">
					<div className="flex flex-col items-center justify-center text-muted-foreground/40">
						<BookOpen className="h-12 w-12 mb-4" />
						<p className="text-sm font-medium">No features found</p>
						<p className="text-xs text-muted-foreground/50">
							{searchQuery || statusFilter !== "all"
								? "Try adjusting your filters"
								: "Create your first feature to get started"}
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
						aria-labelledby="create-feature-title"
					>
						<div className="flex items-center justify-between mb-6">
							<h2 id="create-feature-title" className="text-lg font-semibold">
								Create New Feature
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
								<label className="block text-sm font-medium mb-1">
									Feature Name
								</label>
								<Input
									value={newName}
									onChange={(e) => setNewName(e.target.value)}
									placeholder="e.g., User Authentication"
									className="h-10"
								/>
							</div>

							<div>
								<label className="block text-sm font-medium mb-1">Status</label>
								<Select
									value={newStatus}
									onValueChange={(v) => setNewStatus(v as FeatureStatus)}
								>
									<SelectTrigger className="h-10">
										<SelectValue />
									</SelectTrigger>
									<SelectContent>
										<SelectItem value="draft">Draft</SelectItem>
										<SelectItem value="active">Active</SelectItem>
										<SelectItem value="deprecated">Deprecated</SelectItem>
										<SelectItem value="archived">Archived</SelectItem>
									</SelectContent>
								</Select>
							</div>

							<div>
								<label className="block text-sm font-medium mb-1">
									Description
								</label>
								<textarea
									value={newDescription}
									onChange={(e) => setNewDescription(e.target.value)}
									placeholder="Describe the feature in business terms..."
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
								<Button onClick={handleCreate} disabled={!newName.trim()}>
									Create Feature
								</Button>
							</div>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}
