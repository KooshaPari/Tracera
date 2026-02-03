import {
	Button,
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@tracertm/ui";
import type { LucideIcon } from "lucide-react";
import { Bot, FileText, GitMerge, Zap } from "lucide-react";

interface WorkflowCardProps {
	description: string;
	icon: LucideIcon;
	title: string;
}

const WorkflowCard = ({ icon: Icon, title, description }: WorkflowCardProps) => (
	<Card className="hover:border-primary/50 cursor-pointer transition-colors border-none bg-card/50">
		<CardHeader className="pb-3">
			<CardTitle className="flex items-center gap-2 text-sm">
				<Icon className="w-4 h-4 text-primary" />
				{title}
			</CardTitle>
			<CardDescription className="text-xs">{description}</CardDescription>
		</CardHeader>
		<CardContent className="pt-0">
			<Button size="sm" className="w-full text-xs">
				Start Agent
			</Button>
		</CardContent>
	</Card>
);

export const AgentWorkflowView = () => (
	<div className="space-y-4">
		<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
			<WorkflowCard
				icon={GitMerge}
				title="Task Decomposition"
				description="Break down Epics into User Stories automatically."
			/>
			<WorkflowCard
				icon={FileText}
				title="Scenario Generation"
				description="Generate BDD scenarios from requirements using RAG."
			/>
			<WorkflowCard
				icon={Bot}
				title="Impact Analysis"
				description="Analyze blast radius of proposed changes."
			/>
			<WorkflowCard
				icon={Zap}
				title="Auto-Link Recovery"
				description="Recover missing traceability links from code."
			/>
		</div>
	</div>
);
