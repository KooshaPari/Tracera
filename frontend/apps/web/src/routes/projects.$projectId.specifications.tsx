import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { ItemSpecsOverview } from "@/components/specifications/items";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@tracertm/ui";
import {
	FileText,
	BookOpen,
	Shield,
	ClipboardList,
	LayoutGrid,
} from "lucide-react";
import { SpecificationsDashboardView } from "@/views/SpecificationsDashboardView";
import { ADRListView } from "@/views/ADRListView";
import { ContractListView } from "@/views/ContractListView";
import { FeatureListView } from "@/views/FeatureListView";
import { ComplianceView } from "@/views/ComplianceView";

export const Route = createFileRoute("/projects/$projectId/specifications")({
	validateSearch: (search: Record<string, unknown>) => ({
		tab: typeof search.tab === "string" ? search.tab : "overview",
	}),
	component: SpecificationsRoute,
});

function SpecificationsRoute() {
	const { projectId } = Route.useParams();
	const { tab } = Route.useSearch();
	const navigate = useNavigate();
	const allowedTabs = new Set([
		"overview",
		"item-specs",
		"adrs",
		"contracts",
		"features",
		"compliance",
	]);
	const currentTab = allowedTabs.has(tab) ? tab : "overview";

	const handleTabChange = (value: string) => {
		navigate({
			search: (prev) => ({ ...prev, tab: value }),
		});
	};

	return (
		<div className="p-6">
			<Tabs
				value={currentTab}
				onValueChange={handleTabChange}
				className="w-full"
			>
				<TabsList className="w-full justify-start mb-6 bg-muted/50 p-1">
					<TabsTrigger value="overview" className="gap-2">
						<LayoutGrid className="w-4 h-4" />
						Overview Dashboard
					</TabsTrigger>
					<TabsTrigger value="item-specs" className="gap-2">
						<ClipboardList className="w-4 h-4" />
						Item Specs
					</TabsTrigger>
					<TabsTrigger value="adrs" className="gap-2">
						<FileText className="w-4 h-4" />
						ADRs
					</TabsTrigger>
					<TabsTrigger value="contracts" className="gap-2">
						<Shield className="w-4 h-4" />
						Contracts
					</TabsTrigger>
					<TabsTrigger value="features" className="gap-2">
						<BookOpen className="w-4 h-4" />
						Features
					</TabsTrigger>
					<TabsTrigger value="compliance" className="gap-2">
						<Shield className="w-4 h-4" />
						Compliance
					</TabsTrigger>
				</TabsList>

				{/* Overview Dashboard */}
				<TabsContent value="overview">
					<SpecificationsDashboardView projectId={projectId} />
				</TabsContent>

				{/* Item Specifications */}
				<TabsContent value="item-specs">
					<ItemSpecsOverview projectId={projectId} />
				</TabsContent>

				{/* ADRs */}
				<TabsContent value="adrs">
					<ADRListView projectId={projectId} />
				</TabsContent>

				{/* Contracts */}
				<TabsContent value="contracts">
					<ContractListView projectId={projectId} />
				</TabsContent>

				{/* Features */}
				<TabsContent value="features">
					<FeatureListView projectId={projectId} />
				</TabsContent>

				{/* Compliance */}
				<TabsContent value="compliance">
					<ComplianceView />
				</TabsContent>
			</Tabs>
		</div>
	);
}
