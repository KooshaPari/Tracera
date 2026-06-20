/**
 * Digital Signature Badge Component
 * Displays signature verification status
 */

import { cn } from '@/lib/utils';

interface DigitalSignatureBadgeProps {
  signature?: string | null | undefined;
  valid?: boolean | null | undefined;
  signedBy?: string | null | undefined;
  signedAt?: string | null | undefined;
  algorithm?: string | undefined;
  size?: 'sm' | 'md' | 'lg' | undefined;
  showDetails?: boolean | undefined;
  className?: string | undefined;
}

interface StatusConfig {
  bg: string;
  border: string;
  icon: string;
  label: string;
  text: string;
}

const getStatusConfig = (valid: boolean | null | undefined): StatusConfig => {
  if (valid === true) {
    return {
      bg: 'bg-green-100',
      border: 'border-green-300',
      icon: '✓',
      label: 'Verified',
      text: 'text-green-700',
    };
  }
  if (valid === false) {
    return {
      bg: 'bg-red-100',
      border: 'border-red-300',
      icon: '✕',
      label: 'Invalid',
      text: 'text-red-700',
    };
  }
  return {
    bg: 'bg-yellow-100',
    border: 'border-yellow-300',
    icon: '?',
    label: 'Unverified',
    text: 'text-yellow-700',
  };
};

const renderUnsignedBadge = (size: 'sm' | 'md' | 'lg', className?: string) => (
  <div
    className={cn(
      'inline-flex items-center gap-1.5 rounded-md border font-medium',
      'bg-gray-100 text-gray-600 border-gray-300',
      sizeClasses[size],
      className,
    )}
  >
    <span>📝</span>
    <span>Unsigned</span>
  </div>
);

const renderSimpleStatus = (
  statusConfig: StatusConfig,
  size: 'sm' | 'md' | 'lg',
  className?: string,
  signature?: string,
) => (
  <div
    className={cn(
      'inline-flex items-center gap-1.5 rounded-md border font-medium',
      statusConfig.bg,
      statusConfig.text,
      statusConfig.border,
      sizeClasses[size],
      className,
    )}
    title={signature ? `Signature: ${signature.slice(0, 20)}...` : undefined}
  >
    <span>🔏</span>
    <span>{statusConfig.label}</span>
    <span>{statusConfig.icon}</span>
  </div>
);

interface DetailsViewOptions {
  algorithm: string;
  signedBy: string | null | undefined;
  signedAt: string | null | undefined;
  signature: string;
  className?: string | undefined;
}

const renderDetailsView = (statusConfig: StatusConfig, options: DetailsViewOptions) => (
  <div className={cn('rounded-lg border p-3 space-y-2', options.className)}>
    <div className='flex items-center justify-between'>
      <div className='flex items-center gap-2'>
        <span className='text-lg'>🔏</span>
        <span className='font-medium'>Digital Signature</span>
      </div>
      <div
        className={cn(
          'px-2 py-0.5 rounded text-xs font-medium',
          statusConfig.bg,
          statusConfig.text,
        )}
      >
        {statusConfig.label} {statusConfig.icon}
      </div>
    </div>

    <div className='space-y-1.5 text-sm'>
      <div className='flex justify-between'>
        <span className='text-muted-foreground'>Algorithm</span>
        <span className='font-mono text-xs'>{options.algorithm}</span>
      </div>

      {options.signedBy && (
        <div className='flex justify-between'>
          <span className='text-muted-foreground'>Signed By</span>
          <span>{options.signedBy}</span>
        </div>
      )}

      {options.signedAt && (
        <div className='flex justify-between'>
          <span className='text-muted-foreground'>Signed At</span>
          <span>{new Date(options.signedAt).toLocaleString()}</span>
        </div>
      )}

      <div className='border-t pt-2'>
        <div className='text-muted-foreground mb-1 text-xs'>Signature</div>
        <code className='bg-muted block rounded p-2 font-mono text-xs break-all'>
          {options.signature}
        </code>
      </div>
    </div>
  </div>
);

export const DigitalSignatureBadge = ({
  signature,
  valid,
  signedBy,
  signedAt,
  algorithm = 'ECDSA',
  size = 'md',
  showDetails = false,
  className,
}: DigitalSignatureBadgeProps) => {
  if (!signature) {
    return renderUnsignedBadge(size, className);
  }

  const statusConfig = getStatusConfig(valid);

  if (!showDetails) {
    return renderSimpleStatus(statusConfig, size, className, signature);
  }

  return renderDetailsView(statusConfig, {
    algorithm,
    className,
    signature,
    signedAt,
    signedBy,
  });
};

const sizeClasses = {
  lg: 'text-base px-3 py-1.5',
  md: 'text-sm px-2.5 py-1',
  sm: 'text-xs px-2 py-0.5',
};

interface SignatureVerificationStatusProps {
  hasSignature: boolean;
  isValid?: boolean | null | undefined;
  className?: string | undefined;
}

export const SignatureVerificationStatus = ({
  hasSignature,
  isValid,
  className,
}: SignatureVerificationStatusProps) => {
  if (!hasSignature) {
    return (
      <div className={cn('flex items-center gap-1.5 text-sm text-muted-foreground', className)}>
        <span className='h-2 w-2 rounded-full bg-gray-400' />
        <span>Not signed</span>
      </div>
    );
  }

  if (isValid === true) {
    return (
      <div className={cn('flex items-center gap-1.5 text-sm text-green-600', className)}>
        <span className='h-2 w-2 rounded-full bg-green-500' />
        <span>Signature verified</span>
      </div>
    );
  }

  if (isValid === false) {
    return (
      <div className={cn('flex items-center gap-1.5 text-sm text-red-600', className)}>
        <span className='h-2 w-2 rounded-full bg-red-500' />
        <span>Invalid signature</span>
      </div>
    );
  }

  return (
    <div className={cn('flex items-center gap-1.5 text-sm text-yellow-600', className)}>
      <span className='h-2 w-2 rounded-full bg-yellow-500' />
      <span>Signature pending verification</span>
    </div>
  );
};

interface SignatureHistoryProps {
  signatures: {
    signature: string;
    signedBy: string;
    signedAt: string;
    valid: boolean;
    algorithm?: string | undefined;
  }[];
  className?: string | undefined;
}

export const SignatureHistory = ({ signatures, className }: SignatureHistoryProps) => {
  if (signatures.length === 0) {
    return (
      <div className={cn('text-sm text-muted-foreground p-4 text-center', className)}>
        No signature history available
      </div>
    );
  }

  return (
    <div className={cn('space-y-2', className)}>
      {signatures.map((sig, idx) => (
        <div
          key={idx}
          className={cn(
            'p-3 rounded-lg border',
            sig.valid ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200',
          )}
        >
          <div className='mb-2 flex items-center justify-between'>
            <div className='flex items-center gap-2'>
              <span>{sig.valid ? '✓' : '✕'}</span>
              <span className='font-medium'>{sig.signedBy}</span>
            </div>
            <span className='text-muted-foreground text-xs'>
              {new Date(sig.signedAt).toLocaleString()}
            </span>
          </div>
          <code className='font-mono text-xs break-all opacity-70'>
            {sig.signature.slice(0, 40)}...
          </code>
        </div>
      ))}
    </div>
  );
};
