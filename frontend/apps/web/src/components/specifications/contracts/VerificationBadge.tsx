import { Badge } from "@tracertm/ui";
import { motion } from "framer-motion";
import {
	AlertCircle,
	AlertTriangle,
	CheckCircle,
	Clock,
	HelpCircle,
} from "lucide-react";

type VerificationStatus = "pass" | "fail" | "pending" | "error" | "unknown";

interface VerificationBadgeProps {
	status: VerificationStatus;
	lastVerifiedAt?: string | undefined;
	details?: string | undefined;
	passedCount?: number | undefined;
	failedCount?: number | undefined;
	totalCount?: number | undefined;
	showTimestamp?: boolean | undefined;
	showDetails?: boolean | undefined;
	className?: string | undefined;
}

const statusConfig: Record<
	VerificationStatus,
	{ icon: any; color: string; bgColor: string; label: string }
> = {
	pass: {
		icon: CheckCircle,
		color: "text-green-600",
		bgColor: "bg-green-500/10 border-green-500/20",
		label: "Verified",
	},
	fail: {
		icon: AlertCircle,
		color: "text-red-600",
		bgColor: "bg-red-500/10 border-red-500/20",
		label: "Failed",
	},
	pending: {
		icon: Clock,
		color: "text-yellow-600",
		bgColor: "bg-yellow-500/10 border-yellow-500/20",
		label: "Pending",
	},
	error: {
		icon: AlertTriangle,
		color: "text-orange-600",
		bgColor: "bg-orange-500/10 border-orange-500/20",
		label: "Error",
	},
	unknown: {
		icon: HelpCircle,
		color: "text-gray-600",
		bgColor: "bg-gray-500/10 border-gray-500/20",
		label: "Unverified",
	},
};

function formatTimestamp(isoString: string): string {
	try {
		const date = new Date(isoString);
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
		const diffHours = Math.floor(
			(diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60),
		);
		const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

		if (diffDays > 0) return `${diffDays}d ago`;
		if (diffHours > 0) return `${diffHours}h ago`;
		if (diffMins > 0) return `${diffMins}m ago`;
		return "just now";
	} catch {
		return new Date(isoString).toLocaleDateString();
	}
}

export function VerificationBadge({
	status,
	lastVerifiedAt,
	details,
	passedCount,
	failedCount,
	totalCount,
	showTimestamp = true,
	showDetails = true,
	className = "",
}: VerificationBadgeProps) {
	const config = statusConfig[status];
	const Icon = config.icon;
	const hasTooltipContent =
		showDetails && (lastVerifiedAt || details || totalCount);

	const pulseAnimation =
		status === "pending"
			? {
					opacity: [1, 0.6, 1],
					transition: { duration: 2, repeat: Infinity },
				}
			: undefined;

	return (
		<div className={`relative group ${className}`}>
			{/* Main Badge */}
			<motion.div animate={pulseAnimation ?? {}}>
				<Badge
					className={`${config.bgColor} ${config.color} border font-medium flex items-center gap-1.5 cursor-help`}
				>
					<Icon className="w-3.5 h-3.5" />
					{config.label}
				</Badge>
			</motion.div>

			{/* Tooltip */}
			{hasTooltipContent && (
				<motion.div
					initial={{ opacity: 0, y: -10 }}
					whileHover={{ opacity: 1, y: 0 }}
					transition={{ duration: 0.2 }}
					className="invisible group-hover:visible absolute left-0 mt-2 z-10 w-max bg-popover border border-border rounded-lg shadow-lg p-3 text-sm"
					style={{ pointerEvents: "none" }}
				>
					<div className="space-y-2">
						{/* Status Details */}
						{totalCount !== undefined && (
							<div className="space-y-1">
								<p className="font-semibold text-xs text-muted-foreground uppercase">
									Results
								</p>
								<div className="grid grid-cols-2 gap-2">
									{passedCount !== undefined && (
										<div className="flex items-center gap-1">
											<CheckCircle className="w-3 h-3 text-green-600" />
											<span className="text-xs">
												<span className="font-semibold">{passedCount}</span>{" "}
												passed
											</span>
										</div>
									)}
									{failedCount !== undefined && (
										<div className="flex items-center gap-1">
											<AlertCircle className="w-3 h-3 text-red-600" />
											<span className="text-xs">
												<span className="font-semibold">{failedCount}</span>{" "}
												failed
											</span>
										</div>
									)}
								</div>
								{totalCount && (
									<p className="text-xs text-muted-foreground">
										{totalCount} total condition{totalCount !== 1 ? "s" : ""}
									</p>
								)}
							</div>
						)}

						{/* Details */}
						{details && (
							<div className="border-t border-border pt-2">
								<p className="text-xs text-muted-foreground font-medium mb-1">
									Details
								</p>
								<p className="text-xs text-foreground break-words max-w-xs">
									{details}
								</p>
							</div>
						)}

						{/* Last Verified */}
						{lastVerifiedAt && showTimestamp && (
							<div className="border-t border-border pt-2 flex items-center gap-1 text-xs text-muted-foreground">
								<Clock className="w-3 h-3" />
								<span>Verified {formatTimestamp(lastVerifiedAt)}</span>
							</div>
						)}
					</div>
				</motion.div>
			)}

			{/* Background hover effect for tooltip visibility hint */}
			<div
				className="invisible group-hover:visible absolute -inset-2 bg-primary/5 rounded-lg -z-10 transition-colors"
				aria-hidden="true"
			/>
		</div>
	);
}

// Preset verification badge components for common scenarios
interface PassVerificationBadgeProps {
	lastVerifiedAt?: string | undefined;
	passedCount?: number | undefined;
	totalCount?: number | undefined;
	showTimestamp?: boolean | undefined;
}

export function PassVerificationBadge({
	lastVerifiedAt,
	passedCount,
	totalCount,
	showTimestamp = true,
}: PassVerificationBadgeProps) {
	return (
		<VerificationBadge
			status="pass"
			lastVerifiedAt={lastVerifiedAt}
			passedCount={passedCount}
			failedCount={0}
			totalCount={totalCount}
			showTimestamp={showTimestamp}
		/>
	);
}

interface FailVerificationBadgeProps {
	lastVerifiedAt?: string | undefined;
	passedCount?: number | undefined;
	failedCount?: number | undefined;
	totalCount?: number | undefined;
	details?: string | undefined;
	showTimestamp?: boolean | undefined;
}

export function FailVerificationBadge({
	lastVerifiedAt,
	passedCount,
	failedCount,
	totalCount,
	details,
	showTimestamp = true,
}: FailVerificationBadgeProps) {
	return (
		<VerificationBadge
			status="fail"
			lastVerifiedAt={lastVerifiedAt}
			details={details}
			passedCount={passedCount}
			failedCount={failedCount}
			totalCount={totalCount}
			showTimestamp={showTimestamp}
		/>
	);
}

interface PendingVerificationBadgeProps {
	lastVerifiedAt?: string | undefined;
	showTimestamp?: boolean | undefined;
}

export function PendingVerificationBadge({
	lastVerifiedAt,
	showTimestamp = true,
}: PendingVerificationBadgeProps) {
	return (
		<VerificationBadge
			status="pending"
			lastVerifiedAt={lastVerifiedAt}
			showTimestamp={showTimestamp}
			showDetails={false}
		/>
	);
}

export function UnverifiedBadge() {
	return (
		<VerificationBadge
			status="unknown"
			showTimestamp={false}
			showDetails={false}
		/>
	);
}
