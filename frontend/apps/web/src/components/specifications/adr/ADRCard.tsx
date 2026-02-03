import type { ADR } from "@tracertm/types";
import {
	Badge,
	Button,
	Card,
	CardContent,
	CardFooter,
	CardHeader,
	CardTitle,
} from "@tracertm/ui";
import { format } from "date-fns";
import {
	AlertTriangle,
	ArrowRight,
	CheckCircle,
	Clock,
	FileText,
	GitBranch,
	Link2,
	TrendingUp,
	XCircle,
} from "lucide-react";
import { ComplianceGauge } from "./ComplianceGauge";

interface ADRCardProps {
	adr: ADR;
	onClick?: () => void;
	className?: string;
	compact?: boolean;
	showComplianceGauge?: boolean;
}

const statusColors = {
	accepted: "bg-green-500/10 text-green-500 border-green-500/20",
	deprecated: "bg-gray-500/10 text-gray-500 border-gray-500/20",
	proposed: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
	rejected: "bg-red-500/10 text-red-500 border-red-500/20",
	superseded: "bg-orange-500/10 text-orange-500 border-orange-500/20",
};

const statusIcons = {
	accepted: CheckCircle,
	deprecated: XCircle,
	proposed: Clock,
	rejected: XCircle,
	superseded: AlertTriangle,
};

export function ADRCard({
	adr,
	onClick,
	className,
	compact = false,
	showComplianceGauge = true,
}: ADRCardProps) {
	const StatusIcon =
		statusIcons[adr.status as keyof typeof statusIcons] || Clock;

	if (compact) {
		return (
			<Card
				className={`hover:shadow-md hover:bg-muted/30 hover:border-primary/30 transition-all duration-200 cursor-pointer ${className}`}
				onClick={onClick}
			>
				<CardContent className="p-3">
					<div className="flex items-start justify-between gap-2">
						<div className="flex-1">
							<div className="flex items-center gap-2 mb-1">
								<Badge variant="outline" className="font-mono text-xs">
									{adr.adrNumber}
								</Badge>
								<Badge
									className={
										statusColors[adr.status as keyof typeof statusColors]
									}
								>
									<StatusIcon className="w-2.5 h-2.5 mr-1" />
									{adr.status}
								</Badge>
							</div>
							<h4 className="text-sm font-semibold line-clamp-1">
								{adr.title}
							</h4>
							{adr.complianceScore !== undefined && (
								<p className="text-xs text-muted-foreground mt-1">
									Compliance:{" "}
									<span className="font-medium">
										{Math.round(adr.complianceScore)}%
									</span>
								</p>
							)}
						</div>
						<Button
							variant="ghost"
							size="sm"
							className="h-7 gap-1 text-xs hover:bg-muted/50"
							onClick={(e) => {
								e.stopPropagation();
								onClick?.();
							}}
						>
							<ArrowRight className="w-3 h-3" />
						</Button>
					</div>
				</CardContent>
			</Card>
		);
	}

	return (
		<Card
			className={`hover:shadow-md hover:bg-muted/30 hover:border-primary/30 transition-all duration-200 cursor-pointer ${className}`}
			onClick={onClick}
		>
			<CardHeader className="pb-2">
				<div className="flex justify-between items-start">
					<div className="flex-1">
						<div className="flex items-center gap-2 mb-2">
							<Badge variant="outline" className="font-mono text-xs">
								{adr.adrNumber}
							</Badge>
							<Badge
								className={
									statusColors[adr.status as keyof typeof statusColors]
								}
							>
								<StatusIcon className="w-3 h-3 mr-1" />
								{adr.status}
							</Badge>
							{adr.supersedes && (
								<Badge
									variant="outline"
									className="text-blue-600 border-blue-500/20 text-[10px]"
								>
									<GitBranch className="w-2.5 h-2.5 mr-0.5" />
									Supersedes
								</Badge>
							)}
						</div>
						<CardTitle className="text-base">{adr.title}</CardTitle>
					</div>

					{showComplianceGauge && adr.complianceScore !== undefined && (
						<ComplianceGauge
							score={adr.complianceScore}
							size={64}
							showLabel={false}
						/>
					)}
				</div>

				{adr.date && (
					<span className="text-xs text-muted-foreground mt-1">
						{format(new Date(adr.date), "MMM d, yyyy")}
					</span>
				)}
			</CardHeader>

			<CardContent className="pb-4">
				<div className="space-y-3">
					{adr.context && (
						<div>
							<h4 className="text-xs font-semibold uppercase text-muted-foreground mb-1">
								Context
							</h4>
							<p className="text-sm line-clamp-2 text-muted-foreground">
								{adr.context}
							</p>
						</div>
					)}

					{adr.decision && (
						<div>
							<h4 className="text-xs font-semibold uppercase text-muted-foreground mb-1">
								Decision
							</h4>
							<p className="text-sm line-clamp-2 font-medium">{adr.decision}</p>
						</div>
					)}

					{/* Metadata indicators */}
					<div className="flex flex-wrap gap-3 text-xs text-muted-foreground pt-2">
						{adr.decisionDrivers && adr.decisionDrivers.length > 0 && (
							<div className="flex items-center gap-1">
								<TrendingUp className="w-3 h-3" />
								<span>{adr.decisionDrivers.length} drivers</span>
							</div>
						)}
						{adr.relatedRequirements && adr.relatedRequirements.length > 0 && (
							<div className="flex items-center gap-1">
								<Link2 className="w-3 h-3" />
								<span>{adr.relatedRequirements.length} reqs</span>
							</div>
						)}
						{adr.consideredOptions && adr.consideredOptions.length > 0 && (
							<div className="flex items-center gap-1">
								<FileText className="w-3 h-3" />
								<span>{adr.consideredOptions.length} options</span>
							</div>
						)}
					</div>
				</div>
			</CardContent>

			<CardFooter className="pt-0 flex justify-between items-center text-xs text-muted-foreground">
				<div className="flex items-center gap-2">
					{adr.tags && adr.tags.length > 0 && (
						<div className="flex gap-1">
							{adr.tags.slice(0, 2).map((tag) => (
								<Badge
									key={tag}
									variant="secondary"
									className="text-[10px] px-1.5 h-5"
								>
									{tag}
								</Badge>
							))}
							{adr.tags.length > 2 && (
								<Badge variant="secondary" className="text-[10px] px-1.5 h-5">
									+{adr.tags.length - 2}
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
					View Details <ArrowRight className="w-3 h-3" />
				</Button>
			</CardFooter>
		</Card>
	);
}
