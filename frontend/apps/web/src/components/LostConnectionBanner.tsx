import { Loader2, WifiOff } from 'lucide-react';

import type { ConnectionStatusState } from '@/stores/connection-status-store';

import { useConnectionStatusStore } from '@/stores/connection-status-store';

/**
 * Full-page overlay when connection is lost or reconnecting.
 * Matches server readiness (preflight) design: same dark bg (#0b0f14), card (#0f1720),
 * amber strip for connecting/reconnecting, red accent for lost.
 */
export function LostConnectionBanner() {
  const status = useConnectionStatusStore((s: ConnectionStatusState) => s.status);
  const lastError = useConnectionStatusStore((s: ConnectionStatusState) => s.lastError);

  if (status === 'online') {
    return null;
  }

  const isConnecting = status === 'connecting';
  const isReconnecting = status === 'reconnecting';
  const isWaiting = isConnecting || isReconnecting;
  // 	Const _isLost = !isWaiting;

  // Same palette as preflight: connecting = amber, lost = red (unhealthy)
  const stripStyle = isWaiting
    ? {
        backgroundImage:
          'linear-gradient(120deg, rgba(245,158,11,0.35), rgba(245,158,11,0.08) 55%, rgba(251,191,36,0.22))',
        borderColor: 'rgba(245,158,11,0.45)',
        color: '#fde68a',
      }
    : {
        backgroundImage:
          'linear-gradient(120deg, rgba(239,68,68,0.25), rgba(239,68,68,0.06) 55%, rgba(248,113,113,0.15))',
        borderColor: 'rgba(239,68,68,0.4)',
        color: '#fca5a5',
      };

  return (
    <div
      className='fixed inset-0 z-[100] flex min-h-screen items-center justify-center p-4 font-sans text-[#e6edf3]'
      role='status'
      aria-live='polite'
      aria-atomic='true'
      aria-label={isWaiting ? 'Connecting to server…' : 'Connection lost'}
      style={{ background: '#0b0f14' }}
    >
      {/* Card: same as preflight (max-width, padding, border, bg) */}
      <div
        className='w-full max-w-[480px] rounded-2xl border px-8 py-6 shadow-xl'
        style={{
          background: '#0f1720',
          borderColor: '#1f2a37',
        }}
      >
        <h1 className='mb-1 text-xl font-semibold' style={{ color: '#e6edf3' }}>
          {isWaiting ? 'Connecting to server' : 'Connection lost'}
        </h1>
        <p className='mb-4 text-sm' style={{ color: '#9aa4b2' }}>
          {isWaiting
            ? 'Checking backend readiness. This may take a moment.'
            : "The connection to the server was lost. We'll retry automatically."}
        </p>
        {/* Status strip: same treatment as preflight "Connecting" strip */}
        <div
          className='flex items-center gap-2 rounded-xl border px-4 py-3 font-semibold'
          style={stripStyle}
        >
          {isWaiting ? (
            <Loader2 className='h-5 w-5 shrink-0 animate-spin' aria-hidden />
          ) : (
            <WifiOff className='h-5 w-5 shrink-0' aria-hidden />
          )}
          <span>
            {isConnecting ? 'Connecting' : isReconnecting ? 'Reconnecting' : 'Disconnected'}
          </span>
          {isWaiting && (
            <span className='animate-[connection-dots_1.2s_steps(4)_infinite]' aria-hidden>
              …
            </span>
          )}
        </div>
        {lastError && (
          <p className='mt-3 truncate text-xs' style={{ color: '#9aa4b2' }}>
            {lastError}
          </p>
        )}
        {/* Progress bar: same track as preflight (#111827), amber fill when waiting */}
        <div className='mt-4 h-1.5 overflow-hidden rounded-full' style={{ background: '#111827' }}>
          {isWaiting && (
            <div
              className='h-full rounded-full'
              style={{
                animation: 'connection-shimmer 1.2s ease-in-out infinite',
                background: 'linear-gradient(90deg, #1f2a37 25%, #f59e0b 37%, #1f2a37 63%)',
                backgroundSize: '400px 100%',
                width: '100%',
              }}
              aria-hidden
            />
          )}
        </div>
        {/* Skeleton lines when waiting: same shimmer as preflight .preflight-skeleton */}
        {isWaiting && (
          <ul className='mt-4 list-none space-y-3 p-0' aria-hidden>
            {[60, 85, 45].map((w, i) => (
              <li key={i} className='flex items-center gap-3'>
                <span
                  className='h-4 w-4 shrink-0 rounded-full'
                  style={{
                    animation: 'connection-shimmer 1.2s ease-in-out infinite',
                    background: 'linear-gradient(90deg, #1f2a37 25%, #273444 37%, #1f2a37 63%)',
                    backgroundSize: '400px 100%',
                  }}
                />
                <span
                  className='h-3 rounded-full'
                  style={{
                    animation: 'connection-shimmer 1.2s ease-in-out infinite',
                    animationDelay: `${i * 0.15}s`,
                    background: 'linear-gradient(90deg, #1f2a37 25%, #273444 37%, #1f2a37 63%)',
                    backgroundSize: '400px 100%',
                    width: `${w}%`,
                  }}
                />
              </li>
            ))}
          </ul>
        )}
      </div>
      <style>{`
				@keyframes connection-dots {
					0% { opacity: 0.3; }
					50% { opacity: 1; }
					100% { opacity: 0.3; }
				}
				@keyframes connection-shimmer {
					0% { background-position: -400px 0; }
					100% { background-position: 400px 0; }
				}
			`}</style>
    </div>
  );
}
