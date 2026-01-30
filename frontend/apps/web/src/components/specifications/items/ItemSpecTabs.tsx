/**
 * ItemSpecTabs Component
 *
 * Tabbed interface for viewing different item specifications
 * associated with a single item. Automatically detects and displays
 * available spec types.
 */

import { cn } from "@/lib/utils";
import {
	Badge,
	Button,
	Card,
	Skeleton,
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui";
import {
	Bug,
	CheckCircle2,
	FileCode,
	FileText,
	Layers,
	ListTodo,
	Plus,
	Users,
} from "lucide-react";
import {
	useRequirementSpecByItem,
	useTestSpecByItem,
	useEpicSpecByItem,
	useUserStorySpecByItem,
	useTaskSpecByItem,
	useDefectSpecByItem,
} from "@/hooks/useItemSpecs";
import { RequirementSpecCard } from "./RequirementSpecCard";
import { TestSpecCard } from "./TestSpecCard";
import { EpicSpecCard } from "./EpicSpecCard";
import { UserStorySpecCard } from "./UserStorySpecCard";
import { TaskSpecCard } from "./TaskSpecCard";
import { DefectSpecCard } from "./DefectSpecCard";

interface ItemSpecTabsProps {
	projectId: string;
	itemId: string;
	itemType?: string;
	onCreateSpec?: (specType: string) => void;
	className?: string;
}

const specTypes = [
	{
		id: "requirement",
		label: "Requirement",
		icon: FileText,
		description: "EARS patterns, constraints, quality metrics",
	},
	{
		id: "test",
		label: "Test",
		icon: FileCode,
		description: "Test cases, flakiness, coverage",
	},
	{
		id: "epic",
		label: "Epic",
		icon: Layers,
		description: "Business value, timeline, stories",
	},
	{
		id: "user_story",
		label: "User Story",
		icon: Users,
		description: "As a/I want/So that, acceptance criteria",
	},
	{
		id: "task",
		label: "Task",
		icon: ListTodo,
		description: "Time tracking, subtasks, blockers",
	},
	{
		id: "defect",
		label: "Defect",
		icon: Bug,
		description: "Severity, reproduction, root cause",
	},
];

function getRecommendedSpecs(itemType?: string): string[] {
	switch (itemType?.toLowerCase()) {
		case "requirement":
		case "functional_requirement":
		case "non_functional_requirement":
			return ["requirement"];
		case "test":
		case "test_case":
			return ["test", "requirement"];
		case "epic":
			return ["epic"];
		case "user_story":
		case "story":
			return ["user_story", "requirement"];
		case "task":
			return ["task"];
		case "bug":
		case "defect":
			return ["defect"];
		default:
			return ["requirement", "test"];
	}
}

export function ItemSpecTabs({
	projectId,
	itemId,
	itemType,
	onCreateSpec,
	className,
}: ItemSpecTabsProps) {
	// Fetch all specs for this item (by item ID)
	const { data: reqSpec, isLoading: reqLoading } = useRequirementSpecByItem(
		projectId,
		itemId,
	);
	const { data: testSpec, isLoading: testLoading } = useTestSpecByItem(
		projectId,
		itemId,
	);
	const { data: epicSpec, isLoading: epicLoading } = useEpicSpecByItem(
		projectId,
		itemId,
	);
	const { data: storySpec, isLoading: storyLoading } = useUserStorySpecByItem(
		projectId,
		itemId,
	);
	const { data: taskSpec, isLoading: taskLoading } = useTaskSpecByItem(
		projectId,
		itemId,
	);
	const { data: defectSpec, isLoading: defectLoading } = useDefectSpecByItem(
		projectId,
		itemId,
	);

	const isLoading =
		reqLoading ||
		testLoading ||
		epicLoading ||
		storyLoading ||
		taskLoading ||
		defectLoading;

	// Determine which specs exist
	const existingSpecs = {
		requirement: !!reqSpec,
		test: !!testSpec,
		epic: !!epicSpec,
		user_story: !!storySpec,
		task: !!taskSpec,
		defect: !!defectSpec,
	};

	// Note: hasAnySpec could be used for conditional UI rendering
	// const hasAnySpec = Object.values(existingSpecs).some(Boolean);
	const recommendedSpecs = getRecommendedSpecs(itemType);

	// Find first existing spec for default tab
	const defaultTab =
		specTypes.find((s) => existingSpecs[s.id as keyof typeof existingSpecs])
			?.id ||
		recommendedSpecs[0] ||
		"requirement";

	if (isLoading) {
		return (
			<Card className={cn("p-4 space-y-4", className)}>
				<Skeleton className="h-10 w-full" />
				<Skeleton className="h-48 w-full" />
			</Card>
		);
	}

	return (
		<div className={cn("space-y-4", className)}>
			<Tabs defaultValue={defaultTab} className="w-full">
				<TabsList className="w-full justify-start flex-wrap h-auto gap-1 bg-muted/50 p-1 rounded-xl">
					{specTypes.map((spec) => {
						const Icon = spec.icon;
						const exists = existingSpecs[spec.id as keyof typeof existingSpecs];
						const isRecommended = recommendedSpecs.includes(spec.id);

						return (
							<TabsTrigger
								key={spec.id}
								value={spec.id}
								className={cn(
									"rounded-lg gap-1.5 text-xs data-[state=active]:bg-background",
									!exists && "opacity-50",
								)}
							>
								<Icon className="w-3.5 h-3.5" />
								{spec.label}
								{exists && <CheckCircle2 className="w-3 h-3 text-green-500" />}
								{!exists && isRecommended && (
									<Badge variant="outline" className="text-[8px] px-1 py-0 h-4">
										Suggested
									</Badge>
								)}
							</TabsTrigger>
						);
					})}
				</TabsList>

				{/* Requirement Tab */}
				<TabsContent value="requirement" className="pt-4">
					{reqSpec ? (
						<RequirementSpecCard spec={reqSpec} showQuality />
					) : (
						<EmptySpecState
							specType="requirement"
							description="Add EARS patterns, constraints, and quality metrics"
							onCreateSpec={onCreateSpec}
						/>
					)}
				</TabsContent>

				{/* Test Tab */}
				<TabsContent value="test" className="pt-4">
					{testSpec ? (
						<TestSpecCard spec={testSpec} showCoverage />
					) : (
						<EmptySpecState
							specType="test"
							description="Link test cases with flakiness detection and coverage tracking"
							onCreateSpec={onCreateSpec}
						/>
					)}
				</TabsContent>

				{/* Epic Tab */}
				<TabsContent value="epic" className="pt-4">
					{epicSpec ? (
						<EpicSpecCard spec={epicSpec} showRisks />
					) : (
						<EmptySpecState
							specType="epic"
							description="Define business value, timeline, and user stories"
							onCreateSpec={onCreateSpec}
						/>
					)}
				</TabsContent>

				{/* User Story Tab */}
				<TabsContent value="user_story" className="pt-4">
					{storySpec ? (
						<UserStorySpecCard spec={storySpec} showAcceptanceCriteria />
					) : (
						<EmptySpecState
							specType="user_story"
							description="Capture As a/I want/So that format with acceptance criteria"
							onCreateSpec={onCreateSpec}
						/>
					)}
				</TabsContent>

				{/* Task Tab */}
				<TabsContent value="task" className="pt-4">
					{taskSpec ? (
						<TaskSpecCard spec={taskSpec} showBlockers />
					) : (
						<EmptySpecState
							specType="task"
							description="Track time, subtasks, and blockers"
							onCreateSpec={onCreateSpec}
						/>
					)}
				</TabsContent>

				{/* Defect Tab */}
				<TabsContent value="defect" className="pt-4">
					{defectSpec ? (
						<DefectSpecCard spec={defectSpec} showReproSteps />
					) : (
						<EmptySpecState
							specType="defect"
							description="Document bugs with severity, reproduction steps, and root cause"
							onCreateSpec={onCreateSpec}
						/>
					)}
				</TabsContent>
			</Tabs>
		</div>
	);
}

interface EmptySpecStateProps {
	specType: string;
	description: string;
	onCreateSpec: ((specType: string) => void) | undefined;
}

function EmptySpecState({
	specType,
	description,
	onCreateSpec,
}: EmptySpecStateProps) {
	const spec = specTypes.find((s) => s.id === specType);
	const Icon = spec?.icon || FileText;

	return (
		<Card className="p-8 border-2 border-dashed flex flex-col items-center justify-center text-center space-y-4">
			<div className="h-12 w-12 rounded-full bg-muted/50 flex items-center justify-center">
				<Icon className="h-6 w-6 text-muted-foreground" />
			</div>
			<div className="space-y-1">
				<h3 className="font-semibold text-sm">
					No {spec?.label} Specification
				</h3>
				<p className="text-xs text-muted-foreground max-w-[300px]">
					{description}
				</p>
			</div>
			{onCreateSpec && (
				<Button
					size="sm"
					onClick={() => onCreateSpec(specType)}
					className="gap-1"
				>
					<Plus className="w-3.5 h-3.5" />
					Create {spec?.label} Spec
				</Button>
			)}
		</Card>
	);
}
