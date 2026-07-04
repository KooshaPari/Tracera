/**
 * Content Address Card Component
 * Displays IPFS-style content addressing information
 */

import { useCallback, useMemo, useState } from 'react';

import { cn } from '@/lib/utils';

const CID_PREVIEW_LENGTH = 12;
const COPY_RESET_MS = 2000;

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  return date.toLocaleString();
};

interface ContentAddressCardProps {
  contentHash: string;
  contentCid: string;
  versionChainHead?: string | null | undefined;
  previousVersionHash?: string | null | undefined;
  versionNumber: number;
  digitalSignature?: string | null | undefined;
  signatureValid?: boolean | null | undefined;
  createdAt: string;
  lastModifiedAt: string;
  className?: string | undefined;
}

interface HashFieldProps {
  label: string;
  value: string;
  icon?: string | undefined;
  fieldId: string;
  onCopy?: ((text: string, field: string) => void) | undefined;
  copied?: boolean | undefined;
  highlight?: boolean | undefined;
}

interface ContentAddressBadgeProps {
  contentCid: string;
  versionNumber: number;
  signed?: boolean | undefined;
  className?: string | undefined;
}

interface ContentHashComparisonProps {
  currentHash: string;
  baselineHash: string;
  className?: string | undefined;
}

const SignatureBadge = ({ signatureValid }: { signatureValid: boolean | null | undefined }) => {
  if (signatureValid === true) {
    return (
      <span className='flex items-center gap-1 rounded-md bg-green-100 px-2 py-1 text-xs font-medium text-green-700'>
        <span>🔏</span>
        Signed & Valid
      </span>
    );
  }
  if (signatureValid === false) {
    return (
      <span className='flex items-center gap-1 rounded-md bg-red-100 px-2 py-1 text-xs font-medium text-red-700'>
        <span>⚠</span>
        Invalid Signature
      </span>
    );
  }
  return (
    <span className='flex items-center gap-1 rounded-md bg-yellow-100 px-2 py-1 text-xs font-medium text-yellow-700'>
      <span>🔏</span>
      Signed
    </span>
  );
};

const ContentAddressCardHeader = ({
  versionNumber,
  digitalSignature,
  signatureValid,
}: Pick<ContentAddressCardProps, 'versionNumber' | 'digitalSignature' | 'signatureValid'>) => (
  <div className='flex items-start justify-between'>
    <div>
      <h3 className='flex items-center gap-2 text-lg font-semibold'>
        <span>📍</span>
        Content Address
      </h3>
      <p className='text-muted-foreground text-sm'>
        Version {versionNumber} • Immutable content identifier
      </p>
    </div>
    {digitalSignature ? (
      <div>
        <SignatureBadge signatureValid={signatureValid} />
      </div>
    ) : null}
  </div>
);

const HashField = ({ label, value, icon, fieldId, onCopy, copied, highlight }: HashFieldProps) => {
  const handleClick = useCallback(() => {
    onCopy?.(value, fieldId);
  }, [fieldId, onCopy, value]);

  return (
    <div
      className={cn(
        'p-3 rounded-lg',
        highlight ? 'bg-primary/5 border border-primary/20' : 'bg-muted',
      )}
    >
      <div className='mb-1 flex items-center justify-between'>
        <div className='text-muted-foreground flex items-center gap-1.5 text-xs'>
          {icon ? <span>{icon}</span> : null}
          <span>{label}</span>
        </div>
        {onCopy ? (
          <button
            type='button'
            onClick={handleClick}
            className='hover:bg-muted-foreground/10 rounded px-2 py-0.5 text-xs transition-colors'
          >
            {copied ? 'Copied!' : 'Copy'}
          </button>
        ) : null}
      </div>
      <code className='font-mono text-xs break-all'>{value}</code>
    </div>
  );
};

const HashFieldsSection = ({
  contentCid,
  contentHash,
  copiedField,
  onCopy,
}: {
  contentCid: string;
  contentHash: string;
  copiedField: string | null;
  onCopy: (text: string, field: string) => void;
}) => (
  <div className='space-y-3'>
    <HashField
      copied={copiedField === 'cid'}
      fieldId='cid'
      highlight
      icon='📦'
      label='Content CID (IPFS-style)'
      onCopy={onCopy}
      value={contentCid}
    />
    <HashField
      copied={copiedField === 'hash'}
      fieldId='hash'
      icon='🔒'
      label='Content Hash (SHA-256)'
      onCopy={onCopy}
      value={contentHash}
    />
  </div>
);

const VersionChainSection = ({
  copiedField,
  onCopy,
  previousVersionHash,
  versionChainHead,
}: {
  copiedField: string | null;
  onCopy: (text: string, field: string) => void;
  previousVersionHash?: string | null | undefined;
  versionChainHead?: string | null | undefined;
}) => {
  if (!versionChainHead && !previousVersionHash) {
    return null;
  }

  return (
    <div className='space-y-3 border-t pt-4'>
      <h4 className='text-sm font-medium'>Version Chain</h4>
      {versionChainHead ? (
        <HashField
          copied={copiedField === 'chain'}
          fieldId='chain'
          icon='⛓'
          label='Chain Head'
          onCopy={onCopy}
          value={versionChainHead}
        />
      ) : null}
      {previousVersionHash ? (
        <HashField
          copied={copiedField === 'prev'}
          fieldId='prev'
          icon='⬅'
          label='Previous Version'
          onCopy={onCopy}
          value={previousVersionHash}
        />
      ) : null}
    </div>
  );
};

const SignatureSection = ({
  copiedField,
  digitalSignature,
  onCopy,
}: {
  copiedField: string | null;
  digitalSignature?: string | null | undefined;
  onCopy: (text: string, field: string) => void;
}) =>
  digitalSignature ? (
    <div className='border-t pt-4'>
      <HashField
        copied={copiedField === 'sig'}
        fieldId='sig'
        icon='🔏'
        label='Digital Signature'
        onCopy={onCopy}
        value={digitalSignature}
      />
    </div>
  ) : null;

const TimestampsSection = ({
  createdAt,
  lastModifiedAt,
}: {
  createdAt: string;
  lastModifiedAt: string;
}) => (
  <div className='grid grid-cols-2 gap-4 border-t pt-4 text-sm'>
    <div>
      <div className='text-muted-foreground mb-1'>Created</div>
      <div>{formatDate(createdAt)}</div>
    </div>
    <div>
      <div className='text-muted-foreground mb-1'>Last Modified</div>
      <div>{formatDate(lastModifiedAt)}</div>
    </div>
  </div>
);

export const ContentAddressCard = ({
  contentHash,
  contentCid,
  versionChainHead,
  previousVersionHash,
  versionNumber,
  digitalSignature,
  signatureValid,
  createdAt,
  lastModifiedAt,
  className,
}: ContentAddressCardProps) => {
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const copyToClipboard = useCallback(async (text: string, field: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      setTimeout(() => {
        setCopiedField(null);
      }, COPY_RESET_MS);
    } catch {
      // Clipboard API not available
    }
  }, []);

  const stableCopy = useCallback(
    (text: string, field: string) => {
      copyToClipboard(text, field).catch(() => {});
    },
    [copyToClipboard],
  );

  const versionChainProps = useMemo(
    () => ({
      copiedField,
      onCopy: stableCopy,
      previousVersionHash,
      versionChainHead,
    }),
    [copiedField, previousVersionHash, stableCopy, versionChainHead],
  );

  return (
    <div className={cn('rounded-lg border p-4 space-y-4', className)}>
      <ContentAddressCardHeader
        digitalSignature={digitalSignature}
        signatureValid={signatureValid}
        versionNumber={versionNumber}
      />
      <HashFieldsSection
        contentCid={contentCid}
        contentHash={contentHash}
        copiedField={copiedField}
        onCopy={stableCopy}
      />
      <VersionChainSection {...versionChainProps} />
      <SignatureSection
        copiedField={copiedField}
        digitalSignature={digitalSignature}
        onCopy={stableCopy}
      />
      <TimestampsSection createdAt={createdAt} lastModifiedAt={lastModifiedAt} />
    </div>
  );
};

export const ContentAddressBadge = ({
  contentCid,
  versionNumber,
  signed,
  className,
}: ContentAddressBadgeProps) => (
  <div
    className={cn(
      'inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-muted text-sm',
      className,
    )}
  >
    <span>📍</span>
    <code className='font-mono text-xs'>{contentCid.slice(0, CID_PREVIEW_LENGTH)}...</code>
    <span className='text-muted-foreground'>v{versionNumber}</span>
    {signed ? <span title='Digitally signed'>🔏</span> : null}
  </div>
);

export const ContentHashComparison = ({
  currentHash,
  baselineHash,
  className,
}: ContentHashComparisonProps) => {
  const matches = currentHash === baselineHash;
  return (
    <div className={cn('rounded-lg border p-4 space-y-3', className)}>
      <div className='flex items-center justify-between'>
        <h4 className='text-sm font-medium'>Content Hash Comparison</h4>
        {matches ? (
          <span className='rounded-md bg-green-100 px-2 py-1 text-xs font-medium text-green-700'>
            ✓ Matches
          </span>
        ) : (
          <span className='rounded-md bg-red-100 px-2 py-1 text-xs font-medium text-red-700'>
            ✕ Modified
          </span>
        )}
      </div>

      <div className='grid grid-cols-1 gap-3 md:grid-cols-2'>
        <div className='bg-muted rounded p-2'>
          <div className='text-muted-foreground mb-1 text-xs'>Current</div>
          <code className='font-mono text-xs break-all'>{currentHash}</code>
        </div>
        <div className='bg-muted rounded p-2'>
          <div className='text-muted-foreground mb-1 text-xs'>Baseline</div>
          <code className='font-mono text-xs break-all'>{baselineHash}</code>
        </div>
      </div>

      {!matches ? (
        <p className='text-sm text-amber-600'>
          ⚠ Content has been modified since baseline was established
        </p>
      ) : null}
    </div>
  );
};
