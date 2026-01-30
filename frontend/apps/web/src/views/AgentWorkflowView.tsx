import {
	Button,
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@tracertm/ui";
import { Bot, GitMerge, FileText, Zap } from "lucide-react";

export function AgentWorkflowView() {
	return (
		<div className="space-y-4">
			<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
				<Card className="hover:border-primary/50 cursor-pointer transition-colors border-none bg-card/50">
					<CardHeader className="pb-3">
						<CardTitle className="flex items-center gap-2 text-sm">
							<GitMerge className="w-4 h-4 text-primary" />
							Task Decomposition
						</CardTitle>
						<CardDescription className="text-xs">
							Break down Epics into User Stories automatically.
						</CardDescription>
					</CardHeader>
					<CardContent className="pt-0">
						<Button size="sm" className="w-full text-xs">
							Start Agent
						</Button>
					</CardContent>
				</Card>

				<Card className="hover:border-primary/50 cursor-pointer transition-colors border-none bg-card/50">
					<CardHeader className="pb-3">
						<CardTitle className="flex items-center gap-2 text-sm">
							<FileText className="w-4 h-4 text-primary" />
							Scenario Generation
						</CardTitle>
						<CardDescription className="text-xs">
							Generate BDD scenarios from requirements using RAG.
						</CardDescription>
					</CardHeader>
					<CardContent className="pt-0">
						<Button size="sm" className="w-full text-xs">
							Start Agent
						</Button>
					</CardContent>
				</Card>

				<Card className="hover:border-primary/50 cursor-pointer transition-colors border-none bg-card/50">
					<CardHeader className="pb-3">
						<CardTitle className="flex items-center gap-2 text-sm">
							<Bot className="w-4 h-4 text-primary" />
							Impact Analysis
						</CardTitle>
						<CardDescription className="text-xs">
							Analyze blast radius of proposed changes.
						</CardDescription>
					</CardHeader>
					<CardContent className="pt-0">
						<Button size="sm" className="w-full text-xs">
							Start Agent
						</Button>
					</CardContent>
				</Card>

				<Card className="hover:border-primary/50 cursor-pointer transition-colors border-none bg-card/50">
					<CardHeader className="pb-3">
						<CardTitle className="flex items-center gap-2 text-sm">
							<Zap className="w-4 h-4 text-primary" />
							Auto-Link Recovery
						</CardTitle>
						<CardDescription className="text-xs">
							Recover missing traceability links from code.
						</CardDescription>
					</CardHeader>
					<CardContent className="pt-0">
						<Button size="sm" className="w-full text-xs">
							Start Agent
						</Button>
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
