import type { Feature, FeatureStatus } from "@tracertm/types";
import {
	Badge,
	Button,
	Card,
	CardContent,
	CardFooter,
	CardHeader,
	CardTitle,
	Progress,
} from "@tracertm/ui";
import {
	ArrowRight,
	BookOpen,
	CheckCircle2,
	ListTodo,
	XCircle,
} from "lucide-react";

interface FeatureCardProps {
	feature: Feature;
	onClick?: () => void;
	className?: string;
}

const statusColors: Record<FeatureStatus, string> = {
	active: "bg-blue-500/10 text-blue-500 border-blue-500/20",
	archived: "bg-muted text-muted-foreground border-border",
	deprecated: "bg-orange-500/10 text-orange-500 border-orange-500/20",
	draft: "bg-gray-500/10 text-gray-500 border-gray-500/20",
};

export function FeatureCard({ feature, onClick, className }: FeatureCardProps) {
	const total = feature.scenarioCount || 0;
	const passed = feature.passedScenarios || 0;
	const failed = feature.failedScenarios || 0;
	const pending = feature.pendingScenarios || 0;

	const passRate = total > 0 ? (passed / total) * 100 : 0;

	return (
		<Card
			className={`hover:shadow-md hover:bg-muted/30 hover:border-primary/30 transition-all duration-200 cursor-pointer ${className}`}
			onClick={onClick}
		>
			<CardHeader className="pb-2">
				<div className="flex justify-between items-start">
					<div className="flex items-center gap-2">
						<Badge variant="outline" className="font-mono text-xs">
							{feature.featureNumber}
						</Badge>
						<Badge className={statusColors[feature.status]}>
							{feature.status}
						</Badge>
					</div>
				</div>
				<CardTitle className="text-lg mt-2 flex items-center gap-2">
					<BookOpen className="w-4 h-4 text-muted-foreground" />
					{feature.name}
				</CardTitle>
			</CardHeader>
			<CardContent className="pb-4">
				<div className="space-y-4">
					{feature.asA && (
						<div className="text-sm italic text-muted-foreground bg-muted/30 p-2 rounded border border-border/50">
							"As a{" "}
							<span className="font-medium text-foreground">{feature.asA}</span>
							, I want{" "}
							<span className="font-medium text-foreground">
								{feature.iWant}
							</span>
							, so that{" "}
							<span className="font-medium text-foreground">
								{feature.soThat}
							</span>
							"
						</div>
					)}

					<div className="space-y-1.5">
						<div className="flex justify-between text-xs">
							<span className="font-medium">Scenario Status</span>
							<span className="text-muted-foreground">
								{passed}/{total} Passing
							</span>
						</div>
						<Progress value={passRate} className="h-2" />
						<div className="flex gap-3 text-[10px] text-muted-foreground pt-1">
							{passed > 0 && (
								<span className="flex items-center gap-1 text-green-600">
									<CheckCircle2 className="w-3 h-3" /> {passed} Pass
								</span>
							)}
							{failed > 0 && (
								<span className="flex items-center gap-1 text-red-600">
									<XCircle className="w-3 h-3" /> {failed} Fail
								</span>
							)}
							{pending > 0 && (
								<span className="flex items-center gap-1">
									<ListTodo className="w-3 h-3" /> {pending} Pending
								</span>
							)}
						</div>
					</div>
				</div>
			</CardContent>
			<CardFooter className="pt-0 flex justify-between items-center text-xs text-muted-foreground">
				<div className="flex items-center gap-1">
					{feature.tags && feature.tags.length > 0 && (
						<div className="flex gap-1">
							{feature.tags.slice(0, 2).map((tag) => (
								<Badge
									key={tag}
									variant="secondary"
									className="text-[10px] px-1 h-5"
								>
									{tag}
								</Badge>
							))}
							{feature.tags.length > 2 && (
								<Badge variant="secondary" className="text-[10px] px-1 h-5">
									+{feature.tags.length - 2}
								</Badge>
							)}
						</div>
					)}
				</div>
				<Button
					variant="ghost"
					size="sm"
					className="h-8 gap-1 hover:bg-muted/50 transition-colors"
				>
					View Feature <ArrowRight className="w-3 h-3" />
				</Button>
			</CardFooter>
		</Card>
	);
}
