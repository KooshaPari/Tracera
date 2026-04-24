/**
 * Flakiness Indicator Component
 * Displays test flakiness probability and patterns based on Meta's model
 */

import type { CSSProperties, ReactElement } from 'react';

import { useMemo } from 'react';

import type { FlakinessPattern } from '@/hooks/useItemSpecAnalytics';

import { cn } from '@/lib/utils';

interface FlakinessIndicatorProps {
  probability: number;
  pattern?: FlakinessPattern | null | undefined;
  quarantineRecommended?: boolean | undefined;
  className?: string | undefined;
}

interface FlakinessDetailCardProps {
  probability: number;
  entropy: number;
  pattern?: FlakinessPattern | null | undefined;
  patternConfidence?: number | undefined;
  contributingFactors?: Factor[] | undefined;
  recentRuns?: number | undefined;
  flakyRuns?: number | undefined;
  passRate?: number | undefined;
  quarantineRecommended?: boolean | undefined;
  recommendationReason?: string | null | undefined;
  className?: string | undefined;
}

interface Factor {
  factor: string;
  weight: number;
  evidence: string | null;
}

interface PatternConfig {
  label: string;
  description: string;
  icon: string;
}

interface ProbabilityLevel {
  label: string;
  textColor: string;
  barColor: string;
}

const HIGH_THRESHOLD = 0.7;
const MEDIUM_THRESHOLD = 0.4;
const LOW_THRESHOLD = 0.2;
const PERCENT_MULTIPLIER = 100;
const GAUGE_SIZE = 36;
const GAUGE_RADIUS = 16;
const GAUGE_STROKE = 3;
const HALF = 2;
const ENTROPY_PRECISION = 3;
const ENTROPY_MAX = 1;
const FACTOR_HIGH_THRESHOLD = 0.5;
const FACTOR_MEDIUM_THRESHOLD = 0.25;

const patternLabels: Record<FlakinessPattern, PatternConfig> = {
  async: {
    description: 'Asynchronous operation handling issues',
    icon: '⟳',
    label: 'Async',
  },
  environment: {
    description: 'Environment-specific configuration issues',
    icon: '🌍',
    label: 'Environment',
  },
  network: {
    description: 'Network connectivity or latency issues',
    icon: '🌐',
    label: 'Network',
  },
  order_dependent: {
    description: 'Test execution order dependencies',
    icon: '📋',
    label: 'Order Dependent',
  },
  random: {
    description: 'Random or non-deterministic behavior',
    icon: '🎲',
    label: 'Random',
  },
  resource: {
    description: 'Resource contention or availability issues',
    icon: '💾',
    label: 'Resource',
  },
  timing: {
    description: 'Race conditions or timeout issues',
    icon: '⏱',
    label: 'Timing',
  },
};

const getProbabilityLevel = (probability: number): ProbabilityLevel => {
  if (probability >= HIGH_THRESHOLD) {
    return { barColor: 'bg-red-500', label: 'High', textColor: 'text-red-600' };
  }
  if (probability >= MEDIUM_THRESHOLD) {
    return { barColor: 'bg-orange-500', label: 'Medium', textColor: 'text-orange-500' };
  }
  if (probability >= LOW_THRESHOLD) {
    return { barColor: 'bg-yellow-500', label: 'Low', textColor: 'text-yellow-600' };
  }
  return { barColor: 'bg-green-500', label: 'Minimal', textColor: 'text-green-600' };
};

const getPatternConfig = (
  pattern: FlakinessPattern | null | undefined,
): PatternConfig | undefined => {
  if (pattern === undefined || pattern === null) {
    return undefined;
  }
  return patternLabels[pattern];
};

const getNonEmptyString = (value: string | null | undefined): string | undefined => {
  if (value === undefined || value === null) {
    return undefined;
  }
  if (value.length === 0) {
    return undefined;
  }
  return value;
};

const buildEvidenceElement = (evidence: string | undefined): ReactElement | undefined => {
  if (evidence !== undefined) {
    return <span className='text-muted-foreground'> - {evidence}</span>;
  }
  return undefined;
};

const getPercentage = (probability: number): number => Math.round(probability * PERCENT_MULTIPLIER);

const buildFactorKey = (factor: Factor): string => {
  const evidence = factor.evidence ?? 'none';
  return `${factor.factor}-${factor.weight}-${evidence}`;
};

const getFactorColor = (weight: number): string => {
  if (weight > FACTOR_HIGH_THRESHOLD) {
    return 'bg-red-500';
  }
  if (weight > FACTOR_MEDIUM_THRESHOLD) {
    return 'bg-yellow-500';
  }
  return 'bg-gray-400';
};

const FlakinessGauge = ({
  percentage,
  barColor,
}: {
  percentage: number;
  barColor: string;
}): ReactElement => (
  <div className='relative h-16 w-16'>
    <svg viewBox={`0 0 ${GAUGE_SIZE} ${GAUGE_SIZE}`} className='h-full w-full -rotate-90'>
      <circle
        cx={GAUGE_SIZE / HALF}
        cy={GAUGE_SIZE / HALF}
        r={GAUGE_RADIUS}
        fill='none'
        stroke='currentColor'
        strokeWidth={GAUGE_STROKE}
        className='text-muted'
      />
      <circle
        cx={GAUGE_SIZE / HALF}
        cy={GAUGE_SIZE / HALF}
        r={GAUGE_RADIUS}
        fill='none'
        stroke='currentColor'
        strokeWidth={GAUGE_STROKE}
        strokeDasharray={`${percentage} ${PERCENT_MULTIPLIER}`}
        strokeLinecap='round'
        className={barColor.replace('bg-', 'text-')}
      />
    </svg>
    <div className='absolute inset-0 flex items-center justify-center'>
      <span className='text-sm font-bold'>{percentage}%</span>
    </div>
  </div>
);

const PatternSummary = ({ config }: { config: PatternConfig }): ReactElement => (
  <div className='text-muted-foreground mt-1 flex items-center gap-1.5 text-sm'>
    <span>{config.icon}</span>
    <span>{config.label}</span>
    <span className='text-xs'>- {config.description}</span>
  </div>
);

const PatternDetails = ({
  config,
  confidence,
}: {
  config: PatternConfig;
  confidence: number | undefined;
}): ReactElement => {
  let confidenceElement: ReactElement | undefined = undefined;
  if (confidence !== undefined) {
    confidenceElement = (
      <span className='text-muted-foreground text-sm'>
        ({Math.round(confidence * PERCENT_MULTIPLIER)}% confidence)
      </span>
    );
  }

  return (
    <div className='bg-muted rounded-lg p-3'>
      <div className='mb-2 flex items-center gap-2'>
        <span className='text-lg'>{config.icon}</span>
        <span className='font-medium'>{config.label} Pattern</span>
        {confidenceElement}
      </div>
      <p className='text-muted-foreground text-sm'>{config.description}</p>
    </div>
  );
};

const FlakinessStats = ({
  recentRuns,
  flakyRuns,
  passRate,
}: {
  recentRuns: number | undefined;
  flakyRuns: number | undefined;
  passRate: number | undefined;
}): ReactElement => {
  let passRateDisplay = '-';
  if (passRate !== undefined) {
    passRateDisplay = `${Math.round(passRate * PERCENT_MULTIPLIER)}%`;
  }

  return (
    <div className='grid grid-cols-3 gap-4 text-center'>
      <div className='bg-muted rounded p-2'>
        <div className='text-lg font-semibold'>{recentRuns ?? '-'}</div>
        <div className='text-muted-foreground text-xs'>Recent Runs</div>
      </div>
      <div className='bg-muted rounded p-2'>
        <div className='text-lg font-semibold'>{flakyRuns ?? '-'}</div>
        <div className='text-muted-foreground text-xs'>Flaky Runs</div>
      </div>
      <div className='bg-muted rounded p-2'>
        <div className='text-lg font-semibold'>{passRateDisplay}</div>
        <div className='text-muted-foreground text-xs'>Pass Rate</div>
      </div>
    </div>
  );
};

const EntropySection = ({
  entropy,
  barColor,
}: {
  entropy: number;
  barColor: string;
}): ReactElement => {
  const normalizedEntropy = Math.min(
    entropy * PERCENT_MULTIPLIER,
    ENTROPY_MAX * PERCENT_MULTIPLIER,
  );
  const barStyle = useMemo<CSSProperties>(
    () => ({ width: `${normalizedEntropy}%` }),
    [normalizedEntropy],
  );

  return (
    <div>
      <div className='mb-1 flex justify-between text-sm'>
        <span className='text-muted-foreground'>Entropy Score</span>
        <span className='font-medium'>{entropy.toFixed(ENTROPY_PRECISION)}</span>
      </div>
      <div className='bg-muted h-2 overflow-hidden rounded-full'>
        <div className={cn('h-full rounded-full', barColor)} style={barStyle} />
      </div>
      <p className='text-muted-foreground mt-1 text-xs'>
        Higher entropy indicates more unpredictable behavior
      </p>
    </div>
  );
};

const ContributingFactorsSection = ({
  factors,
}: {
  factors: Factor[] | undefined;
}): ReactElement | undefined => {
  if (!factors || factors.length === 0) {
    return;
  }

  return (
    <div>
      <h4 className='mb-2 text-sm font-medium'>Contributing Factors</h4>
      <ul className='space-y-1.5'>
        {factors.map((factor) => {
          const badgeColor = getFactorColor(factor.weight);
          const evidence = getNonEmptyString(factor.evidence);
          const evidenceElement = buildEvidenceElement(evidence);

          return (
            <li key={buildFactorKey(factor)} className='flex items-start gap-2 text-sm'>
              <div className={cn('w-2 h-2 rounded-full mt-1.5 flex-shrink-0', badgeColor)} />
              <div>
                <span className='font-medium'>{factor.factor}</span>
                {evidenceElement}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

const QuarantineNotice = ({ reason }: { reason: string }): ReactElement => (
  <div className='rounded-lg border border-red-200 bg-red-50 p-3'>
    <div className='mb-1 flex items-center gap-2 font-medium text-red-700'>
      <span>⚠</span>
      <span>Quarantine Recommended</span>
    </div>
    <p className='text-sm text-red-600'>{reason}</p>
  </div>
);

const FlakinessIndicator = ({
  probability,
  pattern,
  quarantineRecommended,
  className,
}: FlakinessIndicatorProps): ReactElement => {
  const percentage = getPercentage(probability);
  const level = getProbabilityLevel(probability);
  const patternConfig = getPatternConfig(pattern);

  let quarantineElement: ReactElement | undefined = undefined;
  if (quarantineRecommended === true) {
    quarantineElement = (
      <span className='rounded bg-red-100 px-1.5 py-0.5 text-xs font-medium text-red-700'>
        Quarantine Recommended
      </span>
    );
  }

  let patternElement: ReactElement | undefined = undefined;
  if (patternConfig !== undefined) {
    patternElement = <PatternSummary config={patternConfig} />;
  }

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <FlakinessGauge percentage={percentage} barColor={level.barColor} />
      <div className='flex-1'>
        <div className='flex items-center gap-2'>
          <span className={cn('font-semibold', level.textColor)}>{level.label} Flakiness</span>
          {quarantineElement}
        </div>
        {patternElement}
      </div>
    </div>
  );
};

const FlakinessDetailCard = ({
  probability,
  entropy,
  pattern,
  patternConfidence,
  contributingFactors,
  recentRuns,
  flakyRuns,
  passRate,
  quarantineRecommended,
  recommendationReason,
  className,
}: FlakinessDetailCardProps): ReactElement => {
  const level = getProbabilityLevel(probability);
  const patternConfig = getPatternConfig(pattern);
  const factorsSection = <ContributingFactorsSection factors={contributingFactors} />;
  const recommendation = getNonEmptyString(recommendationReason);

  let patternDetails: ReactElement | undefined = undefined;
  if (patternConfig !== undefined) {
    patternDetails = <PatternDetails config={patternConfig} confidence={patternConfidence} />;
  }

  let quarantineElement: ReactElement | undefined = undefined;
  if (quarantineRecommended === true && recommendation !== undefined) {
    quarantineElement = <QuarantineNotice reason={recommendation} />;
  }

  return (
    <div className={cn('rounded-lg border p-4 space-y-4', className)}>
      <div className='flex items-start justify-between'>
        <FlakinessIndicator
          probability={probability}
          pattern={pattern}
          quarantineRecommended={quarantineRecommended}
        />
      </div>
      <FlakinessStats recentRuns={recentRuns} flakyRuns={flakyRuns} passRate={passRate} />
      <EntropySection entropy={entropy} barColor={level.barColor} />
      {patternDetails}
      {factorsSection}
      {quarantineElement}
    </div>
  );
};

export { FlakinessDetailCard, FlakinessIndicator };
