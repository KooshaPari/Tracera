import type { ComponentType, CSSProperties, ReactElement } from 'react';

import { motion } from 'framer-motion';
import { AlertCircle, AlertTriangle, CheckCircle, Clock, HelpCircle } from 'lucide-react';

import { Badge } from '../../ui/badge';
import { VerificationStatus } from './verificationStatus';

const HOURS_PER_DAY = Number('24');
const MILLISECONDS_PER_SECOND = Number('1000');
const MINUTES_PER_HOUR = Number('60');
const SECONDS_PER_MINUTE = Number('60');
const MINUTE_IN_MS = SECONDS_PER_MINUTE * MILLISECONDS_PER_SECOND;
const HOUR_IN_MS = MINUTES_PER_HOUR * MINUTE_IN_MS;
const DAY_IN_MS = HOURS_PER_DAY * HOUR_IN_MS;

const PULSE_DIM_OPACITY = Number('0.6');
const PULSE_OPACITY: number[] = [1, PULSE_DIM_OPACITY, 1];
const PULSE_DURATION_SECONDS = Number('2');
const HOVER_ANIMATION_DURATION = Number('0.2');
const ZERO_OFFSET = Number('0');
const NEGATIVE_OFFSET = Number('-10');

const TOOLTIP_STYLE = { pointerEvents: 'none' } as const;
const PULSE_ANIMATION = {
  opacity: PULSE_OPACITY,
  transition: { duration: PULSE_DURATION_SECONDS, repeat: Infinity },
};

const TOOLTIP_INITIAL = { opacity: 0, y: NEGATIVE_OFFSET };
const TOOLTIP_HOVER = { opacity: 1, y: ZERO_OFFSET };
const TOOLTIP_TRANSITION = { duration: HOVER_ANIMATION_DURATION };

const DEFAULT_TIMESTAMP = 'just now';
const DEFAULT_CLASSNAME = '';

const BADGE_STATUS_LABELS = {
  error: 'Error',
  fail: 'Failed',
  pass: 'Verified',
  pending: 'Pending',
  unknown: 'Unverified',
} as const;

interface VerificationStatusConfig {
  bgColor: string;
  color: string;
  icon: ComponentType<{ className?: string }>;
  label: string;
}

const STATUS_CONFIG: Record<VerificationStatus, VerificationStatusConfig> = {
  [VerificationStatus.Error]: {
    bgColor: 'bg-orange-500/10 border-orange-500/20',
    color: 'text-orange-600',
    icon: AlertTriangle,
    label: BADGE_STATUS_LABELS.error,
  },
  [VerificationStatus.Fail]: {
    bgColor: 'bg-red-500/10 border-red-500/20',
    color: 'text-red-600',
    icon: AlertCircle,
    label: BADGE_STATUS_LABELS.fail,
  },
  [VerificationStatus.Pass]: {
    bgColor: 'bg-green-500/10 border-green-500/20',
    color: 'text-green-600',
    icon: CheckCircle,
    label: BADGE_STATUS_LABELS.pass,
  },
  [VerificationStatus.Pending]: {
    bgColor: 'bg-yellow-500/10 border-yellow-500/20',
    color: 'text-yellow-600',
    icon: Clock,
    label: BADGE_STATUS_LABELS.pending,
  },
  [VerificationStatus.Unknown]: {
    bgColor: 'bg-gray-500/10 border-gray-500/20',
    color: 'text-gray-600',
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
  Icon: ComponentType<{ className?: string }>;
  iconClassName: string;
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

const getNonEmptyString = (value: string | undefined): string | undefined => {
  if (value === undefined) {
    return undefined;
  }
  if (value.length === 0) {
    return undefined;
  }
  return value;
};

const ResultRow = ({ count, Icon, iconClassName, label }: ResultRowProps): ReactElement => (
  <div className='flex items-center gap-1'>
    <Icon className={iconClassName} />
    <span className='text-xs'>
      <span className='font-semibold'>{count}</span> {label}
    </span>
  </div>
);

const ResultSummary = ({
  failedCount,
  passedCount,
  totalCount,
}: {
  failedCount?: number | undefined;
  passedCount?: number | undefined;
  totalCount?: number | undefined;
}): ReactElement | undefined => {
  if (totalCount === undefined) {
    return undefined;
  }

  let passedRow: ReactElement | undefined = undefined;
  if (passedCount !== undefined) {
    passedRow = (
      <ResultRow
        count={passedCount}
        Icon={CheckCircle}
        iconClassName='h-3 w-3 text-green-600'
        label='passed'
      />
    );
  }

  let failedRow: ReactElement | undefined = undefined;
  if (failedCount !== undefined) {
    failedRow = (
      <ResultRow
        count={failedCount}
        Icon={AlertCircle}
        iconClassName='h-3 w-3 text-red-600'
        label='failed'
      />
    );
  }

  let totalLabel: ReactElement | undefined = undefined;
  if (totalCount > 0) {
    let countLabel = '';
    if (totalCount !== 1) {
      countLabel = 's';
    }
    totalLabel = (
      <p className='text-muted-foreground text-xs'>
        {totalCount} total condition{countLabel}
      </p>
    );
  }

  return (
    <div className='space-y-1'>
      <p className='text-muted-foreground text-xs font-semibold uppercase'>Results</p>
      <div className='grid grid-cols-2 gap-2'>
        {passedRow}
        {failedRow}
      </div>
      {totalLabel}
    </div>
  );
};

const DetailsBlock = ({ details }: { details?: string | undefined }): ReactElement | undefined => {
  const message = getNonEmptyString(details);
  if (message === undefined) {
    return undefined;
  }

  return (
    <div className='border-border border-t pt-2'>
      <p className='text-muted-foreground mb-1 text-xs font-medium'>Details</p>
      <p className='text-foreground max-w-xs text-xs break-words'>{message}</p>
    </div>
  );
};

const TimestampBlock = ({
  lastVerifiedAt,
  showTimestamp,
}: {
  lastVerifiedAt?: string | undefined;
  showTimestamp: boolean;
}): ReactElement | undefined => {
  const timestamp = getNonEmptyString(lastVerifiedAt);
  if (showTimestamp) {
    if (timestamp === undefined) {
      return undefined;
    }
  } else {
    return undefined;
  }

  return (
    <div className='border-border text-muted-foreground flex items-center gap-1 border-t pt-2 text-xs'>
      <Clock className='h-3 w-3' />
      <span>Verified {formatTimestamp(timestamp)}</span>
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
  details?: string | undefined;
  failedCount?: number | undefined;
  lastVerifiedAt?: string | undefined;
  passedCount?: number | undefined;
  showDetails: boolean;
  showTimestamp: boolean;
  totalCount?: number | undefined;
}): ReactElement | undefined => {
  const detailMessage = getNonEmptyString(details);
  const timestamp = getNonEmptyString(lastVerifiedAt);
  const shouldShowDetails = showDetails;
  const hasSummary = totalCount !== undefined;
  const hasDetails = detailMessage !== undefined;
  const hasTimestamp = timestamp !== undefined;
  const hasAnyDetail = hasSummary || hasDetails || hasTimestamp;

  if (!shouldShowDetails) {
    return undefined;
  }

  if (!hasAnyDetail) {
    return undefined;
  }

  let detailBlock: ReactElement | undefined = undefined;
  detailBlock = <DetailsBlock details={detailMessage} />;

  return (
    <motion.div
      initial={TOOLTIP_INITIAL}
      whileHover={TOOLTIP_HOVER}
      transition={TOOLTIP_TRANSITION}
      className='bg-popover border-border invisible absolute left-0 z-10 mt-2 w-max rounded-lg border p-3 text-sm shadow-lg group-hover:visible'
      style={TOOLTIP_STYLE}
    >
      <div className='space-y-2'>
        <ResultSummary
          failedCount={failedCount}
          passedCount={passedCount}
          totalCount={totalCount}
        />
        {detailBlock}
        <TimestampBlock lastVerifiedAt={timestamp} showTimestamp={showTimestamp} />
      </div>
    </motion.div>
  );
};

const VerificationBadge = ({
  status,
  lastVerifiedAt,
  details,
  passedCount,
  failedCount,
  totalCount,
  showTimestamp = true,
  showDetails = true,
  className = DEFAULT_CLASSNAME,
}: VerificationBadgeProps): ReactElement => {
  const config = STATUS_CONFIG[status];
  const Icon = config.icon;
  let animation: typeof PULSE_ANIMATION | undefined = undefined;
  if (status === VerificationStatus.Pending) {
    animation = PULSE_ANIMATION;
  }

  return (
    <div className={`group relative ${className}`}>
      <motion.div {...(animation !== undefined ? { animate: animation } : {})}>
        <Badge
          className={`${config.bgColor} ${config.color} flex cursor-help items-center gap-1.5 border font-medium`}
        >
          <Icon className='h-3.5 w-3.5' />
          {config.label}
        </Badge>
      </motion.div>

      <TooltipContent
        details={details}
        failedCount={failedCount}
        lastVerifiedAt={lastVerifiedAt}
        passedCount={passedCount}
        showDetails={showDetails}
        showTimestamp={showTimestamp}
        totalCount={totalCount}
      />

      <div
        className='bg-primary/5 invisible absolute -inset-2 -z-10 rounded-lg transition-colors group-hover:visible'
        aria-hidden='true'
      />
    </div>
  );
};

interface PassVerificationBadgeProps {
  lastVerifiedAt?: string | undefined;
  passedCount?: number | undefined;
  showTimestamp?: boolean | undefined;
  totalCount?: number | undefined;
}

const PassVerificationBadge = ({
  lastVerifiedAt,
  passedCount,
  totalCount,
  showTimestamp = true,
}: PassVerificationBadgeProps): ReactElement => (
  <VerificationBadge
    status={VerificationStatus.Pass}
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

const FailVerificationBadge = ({
  lastVerifiedAt,
  passedCount,
  failedCount,
  totalCount,
  details,
  showTimestamp = true,
}: FailVerificationBadgeProps): ReactElement => (
  <VerificationBadge
    status={VerificationStatus.Fail}
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

const PendingVerificationBadge = ({
  lastVerifiedAt,
  showTimestamp = true,
}: PendingVerificationBadgeProps): ReactElement => (
  <VerificationBadge
    status={VerificationStatus.Pending}
    lastVerifiedAt={lastVerifiedAt}
    showTimestamp={showTimestamp}
    showDetails={false}
  />
);

const UnverifiedBadge = (): ReactElement => (
  <VerificationBadge
    status={VerificationStatus.Unknown}
    showTimestamp={false}
    showDetails={false}
  />
);

export {
  FailVerificationBadge,
  PassVerificationBadge,
  PendingVerificationBadge,
  UnverifiedBadge,
  VerificationBadge,
};
