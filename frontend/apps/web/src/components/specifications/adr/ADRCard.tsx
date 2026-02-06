import { format } from 'date-fns';
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
} from 'lucide-react';

import type { ADR } from '@tracertm/types';

import { Badge, Button, Card, CardContent, CardFooter, CardHeader, CardTitle } from '@tracertm/ui';

import { ComplianceGauge } from './ComplianceGauge';

interface ADRCardProps {
  adr: ADR;
  onClick?: () => void;
  className?: string;
  compact?: boolean;
  showComplianceGauge?: boolean;
}

const statusColors = {
  accepted: 'bg-green-500/10 text-green-500 border-green-500/20',
  deprecated: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
  proposed: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  rejected: 'bg-red-500/10 text-red-500 border-red-500/20',
  superseded: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
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
  const StatusIcon = statusIcons[adr.status as keyof typeof statusIcons] || Clock;

  if (compact) {
    return (
      <Card
        className={`hover:bg-muted/30 hover:border-primary/30 cursor-pointer transition-all duration-200 hover:shadow-md ${className}`}
        onClick={onClick}
      >
        <CardContent className='p-3'>
          <div className='flex items-start justify-between gap-2'>
            <div className='flex-1'>
              <div className='mb-1 flex items-center gap-2'>
                <Badge variant='outline' className='font-mono text-xs'>
                  {adr.adrNumber}
                </Badge>
                <Badge className={statusColors[adr.status as keyof typeof statusColors]}>
                  <StatusIcon className='mr-1 h-2.5 w-2.5' />
                  {adr.status}
                </Badge>
              </div>
              <h4 className='line-clamp-1 text-sm font-semibold'>{adr.title}</h4>
              {adr.complianceScore !== undefined && (
                <p className='text-muted-foreground mt-1 text-xs'>
                  Compliance:{' '}
                  <span className='font-medium'>{Math.round(adr.complianceScore)}%</span>
                </p>
              )}
            </div>
            <Button
              variant='ghost'
              size='sm'
              className='hover:bg-muted/50 h-7 gap-1 text-xs'
              onClick={(e) => {
                e.stopPropagation();
                onClick?.();
              }}
            >
              <ArrowRight className='h-3 w-3' />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      className={`hover:bg-muted/30 hover:border-primary/30 cursor-pointer transition-all duration-200 hover:shadow-md ${className}`}
      onClick={onClick}
    >
      <CardHeader className='pb-2'>
        <div className='flex items-start justify-between'>
          <div className='flex-1'>
            <div className='mb-2 flex items-center gap-2'>
              <Badge variant='outline' className='font-mono text-xs'>
                {adr.adrNumber}
              </Badge>
              <Badge className={statusColors[adr.status as keyof typeof statusColors]}>
                <StatusIcon className='mr-1 h-3 w-3' />
                {adr.status}
              </Badge>
              {adr.supersedes && (
                <Badge variant='outline' className='border-blue-500/20 text-[10px] text-blue-600'>
                  <GitBranch className='mr-0.5 h-2.5 w-2.5' />
                  Supersedes
                </Badge>
              )}
            </div>
            <CardTitle className='text-base'>{adr.title}</CardTitle>
          </div>

          {showComplianceGauge && adr.complianceScore !== undefined && (
            <ComplianceGauge score={adr.complianceScore} size={64} showLabel={false} />
          )}
        </div>

        {adr.date && (
          <span className='text-muted-foreground mt-1 text-xs'>
            {format(new Date(adr.date), 'MMM d, yyyy')}
          </span>
        )}
      </CardHeader>

      <CardContent className='pb-4'>
        <div className='space-y-3'>
          {adr.context && (
            <div>
              <h4 className='text-muted-foreground mb-1 text-xs font-semibold uppercase'>
                Context
              </h4>
              <p className='text-muted-foreground line-clamp-2 text-sm'>{adr.context}</p>
            </div>
          )}

          {adr.decision && (
            <div>
              <h4 className='text-muted-foreground mb-1 text-xs font-semibold uppercase'>
                Decision
              </h4>
              <p className='line-clamp-2 text-sm font-medium'>{adr.decision}</p>
            </div>
          )}

          {/* Metadata indicators */}
          <div className='text-muted-foreground flex flex-wrap gap-3 pt-2 text-xs'>
            {adr.decisionDrivers && adr.decisionDrivers.length > 0 && (
              <div className='flex items-center gap-1'>
                <TrendingUp className='h-3 w-3' />
                <span>{adr.decisionDrivers.length} drivers</span>
              </div>
            )}
            {adr.relatedRequirements && adr.relatedRequirements.length > 0 && (
              <div className='flex items-center gap-1'>
                <Link2 className='h-3 w-3' />
                <span>{adr.relatedRequirements.length} reqs</span>
              </div>
            )}
            {adr.consideredOptions && adr.consideredOptions.length > 0 && (
              <div className='flex items-center gap-1'>
                <FileText className='h-3 w-3' />
                <span>{adr.consideredOptions.length} options</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>

      <CardFooter className='text-muted-foreground flex items-center justify-between pt-0 text-xs'>
        <div className='flex items-center gap-2'>
          {adr.tags && adr.tags.length > 0 && (
            <div className='flex gap-1'>
              {adr.tags.slice(0, 2).map((tag) => (
                <Badge key={tag} variant='secondary' className='h-5 px-1.5 text-[10px]'>
                  {tag}
                </Badge>
              ))}
              {adr.tags.length > 2 && (
                <Badge variant='secondary' className='h-5 px-1.5 text-[10px]'>
                  +{adr.tags.length - 2}
                </Badge>
              )}
            </div>
          )}
        </div>
        <Button variant='ghost' size='sm' className='hover:bg-muted/50 h-8 gap-1 transition-colors'>
          View Details <ArrowRight className='h-3 w-3' />
        </Button>
      </CardFooter>
    </Card>
  );
}
