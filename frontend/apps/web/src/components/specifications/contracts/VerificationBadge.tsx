import { Badge } from "@tracertm/ui";
import { motion } from "framer-motion";
import {
	AlertCircle,
	AlertTriangle,
	CheckCircle,
	Clock,
	HelpCircle,
} from "lucide-react";

const HOURS_PER_DAY = Number("24");
const MILLISECONDS_PER_SECOND = Number("1000");
const MINUTES_PER_HOUR = Number("60");
const SECONDS_PER_MINUTE = Number("60");
const MINUTE_IN_MS = SECONDS_PER_MINUTE * MILLISECONDS_PER_SECOND;
const HOUR_IN_MS = MINUTES_PER_HOUR * MINUTE_IN_MS;
const DAY_IN_MS = HOURS_PER_DAY * HOUR_IN_MS;

const PULSE_OPACITY = [1, 0.6, 1];
const PULSE_DURATION_SECONDS = Number("2");
const HOVER_ANIMATION_DURATION = Number("0.2");
const ZERO_OFFSET = Number("0");
const NEGATIVE_OFFSET = Number("-10");

const TOOLTIP_STYLE: React.CSSProperties = { pointerEvents: "none" };

const PULSE_ANIMATION = {
	opacity: PULSE_OPACITY,
	transition: { duration: PULSE_DURATION_SECONDS, repeat: Infinity },
};

const TOOLTIP_INITIAL = { opacity: 0, y: NEGATIVE_OFFSET };
const TOOLTIP_HOVER = { opacity: 1, y: ZERO_OFFSET };
const TOOLTIP_TRANSITION = { duration: HOVER_ANIMATION_DURATION };

const DEFAULT_TIMESTAMP = "just now";
const DEFAULT_FALLBACK_FORMAT = "Last run: —";

const DEFAULT_CLASSNAME = "";

const STATUS_COLOR_FALLBACK = "#94a3b8";
const PRIORITY_COLOR_FALLBACK = "#64748b";

const BADGE_STATUS_LABELS = {
	error: "Error",
	fail: "Failed",
	pass: "Verified",
	pending: "Pending",
	unknown: "Unverified",
} as const;

type VerificationStatus = "pass" | "fail" | "pending" | "error" | "unknown";

type VerificationStatusConfig = {
	bgColor: string;
	color: string;
	icon: React.ComponentType<{ className?: string }>;
	label: string;
};

const STATUS_CONFIG: Record<VerificationStatus, VerificationStatusConfig> = {
	error: {
		bgColor: "bg-orange-500/10 border-orange-500/20",
		color: "text-orange-600",
		icon: AlertTriangle,
		label: BADGE_STATUS_LABELS.error,
	},
	fail: {
		bgColor: "bg-red-500/10 border-red-500/20",
		color: "text-red-600",
		icon: AlertCircle,
		label: BADGE_STATUS_LABELS.fail,
	},
	pass: {
		bgColor: "bg-green-500/10 border-green-500/20",
		color: "text-green-600",
		icon: CheckCircle,
		label: BADGE_STATUS_LABELS.pass,
	},
	pending: {
		bgColor: "bg-yellow-500/10 border-yellow-500/20",
		color: "text-yellow-600",
		icon: Clock,
		label: BADGE_STATUS_LABELS.pending,
	},
	unknown: {
		bgColor: "bg-gray-500/10 border-gray-500/20",
		color: "text-gray-600",
		icon: HelpCircle,
		label: BADGE_STATUS_LABELS.unknown,
	},
};

interface VerificationBadgeProps {
	className?: string | undefined;
	details?: string | undefined;
	failedCount?: number | undefined;
	lastVerifiedAt?: string | undefined;
	passedCount?: number | undefined;
	showDetails?: boolean | undefined;
	showTimestamp?: boolean | undefined;
	status: VerificationStatus;
	totalCount?: number | undefined;
}

interface ResultRowProps {
	count: number;
	icon: React.ReactNode;
	label: string;
}

const formatTimestamp = (isoString: string): string => {
	try {
		const date = new Date(isoString);
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffDays = Math.floor(diffMs / DAY_IN_MS);
		const diffHours = Math.floor((diffMs % DAY_IN_MS) / HOUR_IN_MS);
		const diffMinutes = Math.floor((diffMs % HOUR_IN_MS) / MINUTE_IN_MS);

		if (diffDays > 0) {
			return `${diffDays}d ago`;
		}
		if (diffHours > 0) {
			return `${diffHours}h ago`;
		}
		if (diffMinutes > 0) {
			return `${diffMinutes}m ago`;
		}
		return DEFAULT_TIMESTAMP;
	} catch {
		return new Date(isoString).toLocaleDateString();
	}
};

const ResultRow = ({ count, icon, label }: ResultRowProps): JSX.Element => (
	<div className="flex items-center gap-1">
		{icon}
		<span className="text-xs">
			<span className="font-semibold">{count}</span> {label}
		</span>
	</div>
);

const ResultSummary = ({
	failedCount,
	passedCount,
	totalCount,
}: {
	failedCount?: number;
	passedCount?: number;
	totalCount?: number;
}): JSX.Element | null => {
	if (totalCount === undefined) {
		return null;
	}

	return (
		<div className="space-y-1">
			<p className="font-semibold text-xs text-muted-foreground uppercase">
				Results
			</p>
			<div className="grid grid-cols-2 gap-2">
				{passedCount !== undefined ? (
					<ResultRow
						count={passedCount}
						icon={<CheckCircle className="w-3 h-3 text-green-600" />}
						label="passed"
					/>
				) : null}
				{failedCount !== undefined ? (
					<ResultRow
						count={failedCount}
						icon={<AlertCircle className="w-3 h-3 text-red-600" />}
						label="failed"
					/>
				) : null}
			</div>
			{totalCount ? (
				<p className="text-xs text-muted-foreground">
					{totalCount} total condition{totalCount !== 1 ? "s" : ""}
				</p>
			) : null}
		</div>
	);
};

const DetailsBlock = ({ details }: { details?: string }): JSX.Element | null => {
	if (!details) {
		return null;
	}

	return (
		<div className="border-t border-border pt-2">
			<p className="text-xs text-muted-foreground font-medium mb-1">Details</p>
			<p className="text-xs text-foreground break-words max-w-xs">{details}</p>
		</div>
	);
};

const TimestampBlock = ({
	lastVerifiedAt,
	showTimestamp,
}: {
	lastVerifiedAt?: string;
	showTimestamp: boolean;
}): JSX.Element | null => {
	if (!lastVerifiedAt || !showTimestamp) {
		return null;
	}

	return (
		<div className="border-t border-border pt-2 flex items-center gap-1 text-xs text-muted-foreground">
			<Clock className="w-3 h-3" />
			<span>Verified {formatTimestamp(lastVerifiedAt)}</span>
		</div>
	);
};

const TooltipContent = ({
	details,
	failedCount,
	lastVerifiedAt,
	passedCount,
	showDetails,
	showTimestamp,
	totalCount,
}: {
	details?: string;
	failedCount?: number;
	lastVerifiedAt?: string;
	passedCount?: number;
	showDetails: boolean;
	showTimestamp: boolean;
	totalCount?: number;
}): JSX.Element | null => {
	const hasDetails = showDetails && (lastVerifiedAt || details || totalCount);
	if (!hasDetails) {
		return null;
	}

	return (
		<motion.div
			initial={TOOLTIP_INITIAL}
			whileHover={TOOLTIP_HOVER}
			transition={TOOLTIP_TRANSITION}
			className="invisible group-hover:visible absolute left-0 mt-2 z-10 w-max bg-popover border border-border rounded-lg shadow-lg p-3 text-sm"
			style={TOOLTIP_STYLE}
		>
			<div className="space-y-2">
				<ResultSummary
					failedCount={failedCount}
					passedCount={passedCount}
					totalCount={totalCount}
				/>
				{showDetails ? <DetailsBlock details={details} /> : null}
				<TimestampBlock
					lastVerifiedAt={lastVerifiedAt}
					showTimestamp={showTimestamp}
				/>
			</div>
		</motion.div>
	);
};

export const VerificationBadge = ({
	status,
	lastVerifiedAt,
	details,
	passedCount,
	failedCount,
	totalCount,
	showTimestamp = true,
	showDetails = true,
	className = DEFAULT_CLASSNAME,
}: VerificationBadgeProps): JSX.Element => {
	const config = STATUS_CONFIG[status];
	const Icon = config.icon;
	const animation = status === "pending" ? PULSE_ANIMATION : undefined;

	return (
		<div className={`relative group ${className}`}>
			{/* Main Badge */}
			<motion.div animate={animation ?? {}}>
				<Badge
					className={`${config.bgColor} ${config.color} border font-medium flex items-center gap-1.5 cursor-help`}
				>
					<Icon className="w-3.5 h-3.5" />
					{config.label}
				</Badge>
			</motion.div>

			{/* Tooltip */}
			<TooltipContent
				details={details}
				failedCount={failedCount}
				lastVerifiedAt={lastVerifiedAt}
				passedCount={passedCount}
				showDetails={showDetails}
				showTimestamp={showTimestamp}
				totalCount={totalCount}
			/>

			{/* Background hover effect for tooltip visibility hint */}
			<div
				className="invisible group-hover:visible absolute -inset-2 bg-primary/5 rounded-lg -z-10 transition-colors"
				aria-hidden="true"
			/>
		</div>
	);
};

// Preset verification badge components for common scenarios
interface PassVerificationBadgeProps {
	lastVerifiedAt?: string | undefined;
	passedCount?: number | undefined;
	showTimestamp?: boolean | undefined;
	totalCount?: number | undefined;
}

export const PassVerificationBadge = ({
	lastVerifiedAt,
	passedCount,
	totalCount,
	showTimestamp = true,
}: PassVerificationBadgeProps): JSX.Element => (
	<VerificationBadge
		status="pass"
		lastVerifiedAt={lastVerifiedAt}
		passedCount={passedCount}
		failedCount={0}
		totalCount={totalCount}
		showTimestamp={showTimestamp}
	/>
);

interface FailVerificationBadgeProps {
	details?: string | undefined;
	failedCount?: number | undefined;
	lastVerifiedAt?: string | undefined;
	passedCount?: number | undefined;
	showTimestamp?: boolean | undefined;
	totalCount?: number | undefined;
}

export const FailVerificationBadge = ({
	lastVerifiedAt,
	passedCount,
	failedCount,
	totalCount,
	details,
	showTimestamp = true,
}: FailVerificationBadgeProps): JSX.Element => (
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

interface PendingVerificationBadgeProps {
	lastVerifiedAt?: string | undefined;
	showTimestamp?: boolean | undefined;
}

export const PendingVerificationBadge = ({
	lastVerifiedAt,
	showTimestamp = true,
}: PendingVerificationBadgeProps): JSX.Element => (
	<VerificationBadge
		status="pending"
		lastVerifiedAt={lastVerifiedAt}
		showTimestamp={showTimestamp}
		showDetails={false}
	/>
);

export const UnverifiedBadge = (): JSX.Element => (
	<VerificationBadge
		status="unknown"
		showTimestamp={false}
		showDetails={false}
	/>
);

// Explicit exports used elsewhere
export const statusColorFallback = STATUS_COLOR_FALLBACK;
export const priorityColorFallback = PRIORITY_COLOR_FALLBACK;
