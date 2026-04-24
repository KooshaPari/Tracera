/**
 * WSJF Calculator Component
 * Weighted Shortest Job First scoring for SAFe prioritization
 */

import { useState } from 'react';

import { cn } from '@/lib/utils';

interface WSJFScore {
  business_value: number;
  time_criticality: number;
  risk_reduction: number;
  job_size: number;
  wsjf_score: number;
}

interface WSJFCalculatorProps {
  initialValues?: Partial<WSJFScore>;
  onCalculate?: (score: WSJFScore) => void;
  readOnly?: boolean;
  className?: string;
}

const fibonacciScale = [1, 2, 3, 5, 8, 13, 21];

function getScoreColor(score: number): string {
  if (score >= 5) {
    return 'text-green-600';
  }
  if (score >= 3) {
    return 'text-blue-600';
  }
  if (score >= 1) {
    return 'text-yellow-600';
  }
  return 'text-gray-600';
}

export function WSJFCalculator({
  initialValues,
  onCalculate,
  readOnly = false,
  className,
}: WSJFCalculatorProps) {
  const [businessValue, setBusinessValue] = useState(initialValues?.business_value ?? 5);
  const [timeCriticality, setTimeCriticality] = useState(initialValues?.time_criticality ?? 5);
  const [riskReduction, setRiskReduction] = useState(initialValues?.risk_reduction ?? 5);
  const [jobSize, setJobSize] = useState(initialValues?.job_size ?? 5);

  // Calculate Cost of Delay (CoD) and WSJF
  const costOfDelay = businessValue + timeCriticality + riskReduction;
  const wsjfScore = jobSize > 0 ? costOfDelay / jobSize : 0;

  const handleCalculate = () => {
    if (onCalculate) {
      onCalculate({
        business_value: businessValue,
        job_size: jobSize,
        risk_reduction: riskReduction,
        time_criticality: timeCriticality,
        wsjf_score: wsjfScore,
      });
    }
  };

  return (
    <div className={cn('rounded-lg border p-4 space-y-4', className)}>
      {/* Header */}
      <div className='flex items-center justify-between'>
        <div>
          <h3 className='text-lg font-semibold'>WSJF Score</h3>
          <p className='text-muted-foreground text-sm'>Weighted Shortest Job First</p>
        </div>
        <div className='text-right'>
          <div className={cn('text-3xl font-bold', getScoreColor(wsjfScore))}>
            {wsjfScore.toFixed(2)}
          </div>
          <div className='text-muted-foreground text-sm'>WSJF Score</div>
        </div>
      </div>

      {/* Formula Display */}
      <div className='bg-muted rounded-lg p-3 text-sm'>
        <div className='text-center font-mono'>
          WSJF = Cost of Delay / Job Size = {costOfDelay} / {jobSize} = {wsjfScore.toFixed(2)}
        </div>
      </div>

      {/* Input Sliders */}
      <div className='space-y-4'>
        {/* Cost of Delay Components */}
        <div className='space-y-3'>
          <h4 className='text-muted-foreground text-sm font-medium'>
            Cost of Delay (CoD = {costOfDelay})
          </h4>

          <SliderInput
            label='Business Value'
            description='Value delivered to customer/business'
            value={businessValue}
            onChange={setBusinessValue}
            readOnly={readOnly}
            scale={fibonacciScale}
          />

          <SliderInput
            label='Time Criticality'
            description='How urgently is it needed?'
            value={timeCriticality}
            onChange={setTimeCriticality}
            readOnly={readOnly}
            scale={fibonacciScale}
          />

          <SliderInput
            label='Risk Reduction / Opportunity Enablement'
            description='Reduces risk or enables other work'
            value={riskReduction}
            onChange={setRiskReduction}
            readOnly={readOnly}
            scale={fibonacciScale}
          />
        </div>

        {/* Job Size */}
        <div className='border-t pt-3'>
          <SliderInput
            label='Job Size'
            description='Estimated effort (lower = smaller)'
            value={jobSize}
            onChange={setJobSize}
            readOnly={readOnly}
            scale={fibonacciScale}
          />
        </div>
      </div>

      {/* Calculate Button */}
      {!readOnly && onCalculate && (
        <button
          onClick={handleCalculate}
          className='bg-primary text-primary-foreground hover:bg-primary/90 w-full rounded-md px-4 py-2 transition-colors'
        >
          Save WSJF Score
        </button>
      )}
    </div>
  );
}

interface SliderInputProps {
  label: string;
  description: string;
  value: number;
  onChange: (value: number) => void;
  readOnly?: boolean;
  scale: number[];
}

function SliderInput({ label, description, value, onChange, readOnly, scale }: SliderInputProps) {
  return (
    <div className='space-y-1.5'>
      <div className='flex justify-between text-sm'>
        <span className='font-medium'>{label}</span>
        <span className='font-mono'>{value}</span>
      </div>
      <p className='text-muted-foreground text-xs'>{description}</p>
      {readOnly ? (
        <div className='bg-muted h-2 overflow-hidden rounded-full'>
          <div
            className='bg-primary h-full rounded-full'
            style={{ width: `${(value / Math.max(...scale)) * 100}%` }}
          />
        </div>
      ) : (
        <div className='flex gap-1'>
          {scale.map((scaleValue) => (
            <button
              key={scaleValue}
              onClick={() => {
                onChange(scaleValue);
              }}
              className={cn(
                'flex-1 py-1 text-xs rounded border transition-colors',
                value === scaleValue
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-muted hover:bg-muted/80 border-transparent',
              )}
            >
              {scaleValue}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

interface WSJFScoreBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function WSJFScoreBadge({ score, size = 'md', className }: WSJFScoreBadgeProps) {
  let color = 'bg-gray-100 text-gray-700 border-gray-300';
  if (score >= 5) {
    color = 'bg-green-100 text-green-700 border-green-300';
  } else if (score >= 3) {
    color = 'bg-blue-100 text-blue-700 border-blue-300';
  } else if (score >= 1) {
    color = 'bg-yellow-100 text-yellow-700 border-yellow-300';
  }

  const sizeClass = {
    lg: 'text-base px-3 py-1.5',
    md: 'text-sm px-2 py-1',
    sm: 'text-xs px-1.5 py-0.5',
  }[size];

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded border font-medium',
        color,
        sizeClass,
        className,
      )}
    >
      <span>⚖</span>
      <span>WSJF: {score.toFixed(2)}</span>
    </span>
  );
}
