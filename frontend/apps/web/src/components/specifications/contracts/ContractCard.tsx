import { motion } from 'framer-motion';
import {
  ArrowRight,
  Code,
  FileCode,
  GitBranch,
  Shield,
  ShieldAlert,
  ShieldCheck,
} from 'lucide-react';

import type { Contract } from '@tracertm/types';

import { Badge, Button, Card, CardContent, CardFooter, CardHeader, CardTitle } from '@tracertm/ui';

import { VerificationBadge } from './VerificationBadge';
import { VerificationStatus } from './verificationStatus';

interface ContractCardProps {
  contract: Contract;
  onClick?: () => void;
  className?: string;
  isSelected?: boolean;
}

/**
 * Status color mapping
 */
interface StatusColorMap {
  draft: string;
  active: string;
  verified: string;
  violated: string;
  deprecated: string;
}

/**
 * Icon component type
 */
type IconComponent = typeof FileCode;

/**
 * Status icon mapping
 */
interface StatusIconMap {
  draft: IconComponent;
  active: IconComponent;
  verified: IconComponent;
  violated: IconComponent;
  deprecated: IconComponent;
}

/**
 * Type icon labels
 */
type TypeIconMap = Record<string, string>;

const statusColors: StatusColorMap = {
  active: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  deprecated: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
  draft: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
  verified: 'bg-green-500/10 text-green-500 border-green-500/20',
  violated: 'bg-red-500/10 text-red-500 border-red-500/20',
};

const statusIcons: StatusIconMap = {
  active: Shield,
  deprecated: Shield,
  draft: FileCode,
  verified: ShieldCheck,
  violated: ShieldAlert,
};

const typeIcons: TypeIconMap = {
  api: 'API',
  data: '∑',
  function: 'fn',
  integration: '⟷',
  invariant: '∀',
};

export function ContractCard({
  contract,
  onClick,
  className,
  isSelected = false,
}: ContractCardProps) {
  const StatusIcon = statusIcons[contract.status] || Shield;
  const totalConditions =
    (contract.preconditions?.length || 0) +
    (contract.postconditions?.length || 0) +
    (contract.invariants?.length || 0);

  const verificationStatus = contract.verificationResult?.status ?? VerificationStatus.Unknown;
  const passedCount = contract.verificationResult?.passedConditions ?? 0;
  const failedCount = contract.verificationResult?.failedConditions ?? 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        className={`hover:bg-muted/30 hover:border-primary/30 cursor-pointer border-2 transition-all duration-200 hover:shadow-md ${
          isSelected ? 'border-primary bg-primary/5' : 'border-border'
        } ${className}`}
        onClick={onClick}
      >
        <CardHeader className='pb-2'>
          <div className='flex items-start justify-between gap-2'>
            <div className='flex min-w-0 flex-1 items-center gap-2'>
              <Badge variant='outline' className='flex-shrink-0 font-mono text-xs'>
                {contract.contractNumber}
              </Badge>
              <motion.div whileHover={{ scale: 1.05 }} className={statusColors[contract.status]}>
                <Badge className={statusColors[contract.status]}>
                  <StatusIcon className='mr-1 h-3 w-3' />
                  {contract.status}
                </Badge>
              </motion.div>
            </div>
            <Badge variant='secondary' className='flex-shrink-0 text-[10px]'>
              {typeIcons[contract.contractType] ?? contract.contractType}
            </Badge>
          </div>
          <CardTitle className='mt-2 truncate text-base'>{contract.title}</CardTitle>
        </CardHeader>

        <CardContent className='space-y-3 pb-4'>
          {contract.description && (
            <p className='text-muted-foreground line-clamp-2 text-sm'>{contract.description}</p>
          )}

          {/* Condition Counts */}
          <div className='text-muted-foreground flex gap-3 text-xs'>
            <div className='flex items-center gap-1'>
              <Shield className='h-3.5 w-3.5 text-blue-600' />
              <span>
                <span className='text-foreground font-bold'>
                  {contract.preconditions?.length || 0}
                </span>
                <span className='hidden sm:inline'> pre</span>
              </span>
            </div>
            <div className='flex items-center gap-1'>
              <Shield className='h-3.5 w-3.5 text-green-600' />
              <span>
                <span className='text-foreground font-bold'>
                  {contract.postconditions?.length || 0}
                </span>
                <span className='hidden sm:inline'> post</span>
              </span>
            </div>
            <div className='flex items-center gap-1'>
              <Shield className='h-3.5 w-3.5 text-purple-600' />
              <span>
                <span className='text-foreground font-bold'>
                  {contract.invariants?.length || 0}
                </span>
                <span className='hidden sm:inline'> inv</span>
              </span>
            </div>
          </div>

          {/* State Machine Info */}
          {contract.states && contract.states.length > 0 && (
            <div className='text-muted-foreground bg-muted/50 flex items-center gap-1.5 rounded px-2 py-1.5 text-xs'>
              <GitBranch className='h-3 w-3' />
              <span>
                {contract.states.length} state
                {contract.states.length !== 1 ? 's' : ''}
              </span>
            </div>
          )}
        </CardContent>

        <CardFooter className='text-muted-foreground flex items-center justify-between gap-2 pt-0 text-xs'>
          <div className='flex items-center gap-1.5'>
            {contract.executableSpec && (
              <Badge variant='outline' className='h-5 gap-1 px-1.5 text-[10px]'>
                <Code className='h-3 w-3' />
                <span className='hidden sm:inline'>Executable</span>
              </Badge>
            )}
          </div>

          {/* Verification Status */}
          {totalConditions > 0 && (
            <VerificationBadge
              status={
                verificationStatus === 'pass'
                  ? VerificationStatus.Pass
                  : verificationStatus === 'fail'
                    ? VerificationStatus.Fail
                    : verificationStatus === 'error'
                      ? VerificationStatus.Error
                      : VerificationStatus.Unknown
              }
              lastVerifiedAt={contract.lastVerifiedAt}
              passedCount={passedCount}
              failedCount={failedCount}
              totalCount={totalConditions}
              showTimestamp
              showDetails
            />
          )}

          <Button
            variant='ghost'
            size='sm'
            className='hover:bg-muted/50 ml-auto h-8 flex-shrink-0 gap-1 transition-colors'
          >
            <ArrowRight className='h-3 w-3' />
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
}
