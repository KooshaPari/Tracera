import { AnimatePresence, motion } from 'framer-motion';
import { AlertCircle, AlertTriangle, CheckCircle, Circle, Code, Shield } from 'lucide-react';

import type { ContractCondition } from '@tracertm/types';

import { Card } from '@tracertm/ui';

interface ConditionListProps {
  preconditions?: ContractCondition[];
  postconditions?: ContractCondition[];
  invariants?: ContractCondition[];
  onConditionClick?: (condition: ContractCondition) => void;
  className?: string;
}

/**
 * Severity style configuration
 */
interface SeverityStyle {
  bg: string;
  text: string;
  icon: React.ComponentType<{ className?: string }>;
}

/**
 * Severity styles map
 */
interface ConditionSeverityStyleMap {
  critical: SeverityStyle;
  high: SeverityStyle;
  medium: SeverityStyle;
  low: SeverityStyle;
  [key: string]: SeverityStyle;
}

/**
 * Verification status icon map
 */
interface VerificationStatusIconMap {
  pass: React.ComponentType<{ className?: string; title?: string }>;
  fail: React.ComponentType<{ className?: string; title?: string }>;
  skip: React.ComponentType<{ className?: string; title?: string }>;
  undefined: React.ComponentType<{ className?: string; title?: string }>;
  [key: string]: React.ComponentType<{ className?: string; title?: string }>;
}

const conditionSeverityStyles: ConditionSeverityStyleMap = {
  critical: {
    bg: 'bg-red-500/10',
    icon: AlertCircle,
    text: 'text-red-600',
  },
  high: {
    bg: 'bg-orange-500/10',
    icon: AlertTriangle,
    text: 'text-orange-600',
  },
  low: {
    bg: 'bg-blue-500/10',
    icon: Circle,
    text: 'text-blue-600',
  },
  medium: {
    bg: 'bg-yellow-500/10',
    icon: Circle,
    text: 'text-yellow-600',
  },
};

const verificationStatusIcons: VerificationStatusIconMap = {
  fail: AlertCircle,
  pass: CheckCircle,
  skip: Circle,
  undefined: Circle,
};

const verificationStatusColors: Record<string, string> = {
  fail: 'text-red-600',
  pass: 'text-green-600',
  skip: 'text-gray-600',
  undefined: 'text-gray-400',
};

interface ConditionItemProps {
  condition: ContractCondition;
  type: 'precondition' | 'postcondition' | 'invariant';
  onClick?: () => void;
}

function ConditionItem({ condition, type, onClick }: ConditionItemProps) {
  const severity = (condition as ContractCondition & { severity?: string }).severity ?? 'medium';
  const status = condition.lastVerifiedResult ?? 'undefined';
  const StatusIcon = (verificationStatusIcons[status] || Circle) as React.ComponentType<{
    className?: string;
    title?: string;
  }>;
  const severityStyle = conditionSeverityStyles[severity];

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -10 }}
      transition={{ duration: 0.2 }}
      className={`cursor-pointer rounded-lg border p-4 transition-colors hover:shadow-sm ${severityStyle?.bg}`}
      onClick={onClick}
    >
      <div className='space-y-3'>
        {/* Header with Type, Severity, and Status */}
        <div className='flex items-start justify-between gap-3'>
          <div className='flex min-w-0 flex-1 items-center gap-2'>
            {/* Type Icon */}
            {type === 'precondition' && <Shield className='h-4 w-4 flex-shrink-0 text-blue-600' />}
            {type === 'postcondition' && (
              <Shield className='h-4 w-4 flex-shrink-0 text-green-600' />
            )}
            {type === 'invariant' && <Shield className='h-4 w-4 flex-shrink-0 text-purple-600' />}

            {/* Condition Description */}
            <p className={`text-sm font-medium ${severityStyle?.text} truncate`}>
              {condition.description}
            </p>
          </div>

          {/* Verification Status */}
          <div className='flex flex-shrink-0 items-center gap-1'>
            <StatusIcon
              className={`h-4 w-4 ${verificationStatusColors[status]}`}
              title={`Verification: ${status}`}
            />
          </div>
        </div>

        {/* Expression (if available) */}
        {condition.expression && (
          <div className='bg-background/60 border-border/50 overflow-x-auto rounded border p-2'>
            <code className='text-muted-foreground font-mono text-xs whitespace-nowrap'>
              {condition.expression}
            </code>
          </div>
        )}

        {/* Metadata Row */}
        <div className='text-muted-foreground flex items-center justify-between text-xs'>
          <div className='flex items-center gap-2'>
            {!condition.isRequired && (
              <span className='rounded bg-yellow-500/10 px-1.5 py-0.5 text-[10px] font-medium text-yellow-600'>
                Optional
              </span>
            )}
            <span className='flex items-center gap-1'>
              <Code className='h-3 w-3' />
              {condition.expression ? 'Expression' : 'Descriptive'}
            </span>
          </div>
          {status !== 'undefined' && (
            <span className={`font-medium ${verificationStatusColors[status]}`}>
              {status === 'pass' ? '✓ Verified' : status === 'fail' ? '✗ Failed' : '⊘ Skipped'}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
}

export function ConditionList({
  preconditions,
  postconditions,
  invariants,
  onConditionClick,
  className = '',
}: ConditionListProps) {
  const hasAnyConditions =
    (preconditions?.length ?? 0) > 0 ||
    (postconditions?.length ?? 0) > 0 ||
    (invariants?.length ?? 0) > 0;

  if (!hasAnyConditions) {
    return (
      <Card className={`text-muted-foreground p-6 text-center ${className}`}>
        <Shield className='mx-auto mb-2 h-8 w-8 opacity-50' />
        <p className='text-sm'>No conditions defined yet.</p>
        <p className='text-xs'>
          Add preconditions, postconditions, or invariants to this contract.
        </p>
      </Card>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Preconditions Section */}
      {preconditions && preconditions.length > 0 && (
        <div className='space-y-3'>
          <div className='flex items-center gap-2'>
            <Shield className='h-4 w-4 text-blue-600' />
            <h3 className='text-sm font-semibold text-blue-600'>
              Preconditions ({preconditions.length})
            </h3>
          </div>
          <div className='grid gap-3'>
            <AnimatePresence mode='popLayout'>
              {preconditions.map((condition) => (
                <ConditionItem
                  key={condition.id}
                  condition={condition}
                  type='precondition'
                  onClick={() => onConditionClick?.(condition)}
                />
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Postconditions Section */}
      {postconditions && postconditions.length > 0 && (
        <div className='space-y-3'>
          <div className='flex items-center gap-2'>
            <Shield className='h-4 w-4 text-green-600' />
            <h3 className='text-sm font-semibold text-green-600'>
              Postconditions ({postconditions.length})
            </h3>
          </div>
          <div className='grid gap-3'>
            <AnimatePresence mode='popLayout'>
              {postconditions.map((condition) => (
                <ConditionItem
                  key={condition.id}
                  condition={condition}
                  type='postcondition'
                  onClick={() => onConditionClick?.(condition)}
                />
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Invariants Section */}
      {invariants && invariants.length > 0 && (
        <div className='space-y-3'>
          <div className='flex items-center gap-2'>
            <Shield className='h-4 w-4 text-purple-600' />
            <h3 className='text-sm font-semibold text-purple-600'>
              Invariants ({invariants.length})
            </h3>
          </div>
          <div className='grid gap-3'>
            <AnimatePresence mode='popLayout'>
              {invariants.map((condition) => (
                <ConditionItem
                  key={condition.id}
                  condition={condition}
                  type='invariant'
                  onClick={() => onConditionClick?.(condition)}
                />
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}
    </div>
  );
}
