/**
 * Merkle Proof Viewer Component
 * Displays Merkle tree proof for baseline verification
 */

import { cn } from '@/lib/utils';

interface MerkleProofViewerProps {
  root: string;
  proof: string[];
  leafIndex: number;
  leafHash: string;
  verified: boolean;
  verificationPath?: { direction: string; hash: string }[];
  treeSize?: number;
  algorithm?: string;
  className?: string;
}

export function MerkleProofViewer({
  root,
  proof,
  leafIndex,
  leafHash,
  verified,
  verificationPath,
  treeSize,
  algorithm = 'SHA-256',
  className,
}: MerkleProofViewerProps) {
  return (
    <div className={cn('rounded-lg border p-4 space-y-4', className)}>
      {/* Header */}
      <div className='flex items-start justify-between'>
        <div>
          <h3 className='flex items-center gap-2 text-lg font-semibold'>
            <span>🌳</span>
            Merkle Proof
          </h3>
          <p className='text-muted-foreground text-sm'>
            {algorithm} • {treeSize ?? proof.length + 1} items in tree
          </p>
        </div>
        <div>
          {verified ? (
            <span className='flex items-center gap-1.5 rounded-md bg-green-100 px-3 py-1.5 text-sm font-medium text-green-700'>
              <span className='text-green-600'>✓</span>
              Verified
            </span>
          ) : (
            <span className='flex items-center gap-1.5 rounded-md bg-red-100 px-3 py-1.5 text-sm font-medium text-red-700'>
              <span className='text-red-600'>✕</span>
              Verification Failed
            </span>
          )}
        </div>
      </div>

      {/* Root Hash */}
      <div className='bg-primary/5 border-primary/20 rounded-lg border p-3'>
        <div className='text-muted-foreground mb-1 text-xs'>Merkle Root</div>
        <code className='font-mono text-sm break-all'>{root}</code>
      </div>

      {/* Leaf Info */}
      <div className='grid grid-cols-2 gap-3'>
        <div className='bg-muted rounded-lg p-3'>
          <div className='text-muted-foreground mb-1 text-xs'>Leaf Index</div>
          <div className='font-mono text-lg'>{leafIndex}</div>
        </div>
        <div className='bg-muted rounded-lg p-3'>
          <div className='text-muted-foreground mb-1 text-xs'>Leaf Hash</div>
          <code className='font-mono text-xs break-all'>{leafHash}</code>
        </div>
      </div>

      {/* Proof Visualization */}
      {verificationPath && verificationPath.length > 0 && (
        <div className='space-y-2'>
          <h4 className='text-sm font-medium'>Verification Path</h4>
          <div className='relative pl-8'>
            {/* Vertical line */}
            <div className='bg-border absolute top-2 bottom-2 left-3 w-0.5' />

            {/* Leaf */}
            <div className='relative mb-3'>
              <div className='absolute top-2 left-[-20px] h-2 w-2 rounded-full bg-green-500' />
              <div className='rounded border border-green-200 bg-green-50 p-2 text-sm'>
                <div className='mb-1 text-xs font-medium text-green-600'>
                  Leaf (Index {leafIndex})
                </div>
                <code className='font-mono text-xs break-all'>{leafHash.slice(0, 32)}...</code>
              </div>
            </div>

            {/* Path nodes */}
            {verificationPath.map((node, idx) => (
              <div key={idx} className='relative mb-3'>
                <div className='absolute top-2 left-[-20px] h-2 w-2 rounded-full bg-blue-500' />
                <div className='rounded border border-blue-200 bg-blue-50 p-2 text-sm'>
                  <div className='mb-1 flex items-center gap-2'>
                    <span className='text-xs font-medium text-blue-600'>Level {idx + 1}</span>
                    <span
                      className={cn(
                        'px-1.5 py-0.5 text-xs rounded',
                        node.direction === 'left'
                          ? 'bg-orange-100 text-orange-700'
                          : 'bg-purple-100 text-purple-700',
                      )}
                    >
                      {node.direction === 'left' ? '← Left sibling' : '→ Right sibling'}
                    </span>
                  </div>
                  <code className='font-mono text-xs break-all'>{node.hash.slice(0, 32)}...</code>
                </div>
              </div>
            ))}

            {/* Root */}
            <div className='relative'>
              <div className='bg-primary absolute top-2 left-[-20px] h-2 w-2 rounded-full' />
              <div className='bg-primary/10 border-primary/30 rounded border p-2 text-sm'>
                <div className='text-primary mb-1 text-xs font-medium'>Root</div>
                <code className='font-mono text-xs break-all'>{root.slice(0, 32)}...</code>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Proof Hashes */}
      <div className='space-y-2'>
        <h4 className='text-sm font-medium'>Proof ({proof.length} hashes)</h4>
        <div className='bg-muted max-h-48 space-y-1 overflow-y-auto rounded-lg p-2'>
          {proof.map((hash, idx) => (
            <div key={idx} className='flex items-center gap-2 text-xs'>
              <span className='text-muted-foreground w-4'>{idx}</span>
              <code className='flex-1 font-mono break-all'>{hash}</code>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

interface MerkleVerificationBadgeProps {
  verified: boolean;
  proofLength?: number;
  className?: string;
}

export function MerkleVerificationBadge({
  verified,
  proofLength,
  className,
}: MerkleVerificationBadgeProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-sm font-medium',
        verified ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700',
        className,
      )}
    >
      <span>🌳</span>
      {verified ? (
        <>
          <span>Merkle Verified</span>
          <span className='text-green-600'>✓</span>
        </>
      ) : (
        <>
          <span>Verification Failed</span>
          <span className='text-red-600'>✕</span>
        </>
      )}
      {proofLength !== undefined && <span className='opacity-70'>({proofLength} hashes)</span>}
    </div>
  );
}
