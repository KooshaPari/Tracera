import type { ReactNode } from 'react';

interface PageShellProps {
  children: ReactNode;
}

export function PageShell({ children }: PageShellProps): JSX.Element {
  return (
    <div className='relative flex min-h-screen flex-col'>
      <div className='pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_15%_15%,rgba(249,115,22,0.18),transparent_45%),radial-gradient(circle_at_80%_10%,rgba(14,116,144,0.2),transparent_45%),radial-gradient(circle_at_20%_80%,rgba(16,185,129,0.18),transparent_40%)]' />
      <div className='pointer-events-none absolute inset-0 bg-[linear-gradient(120deg,rgba(15,23,42,0.08),transparent_55%,rgba(2,132,199,0.08))]' />
      <div className='animate-in-fade-up relative mx-auto flex min-h-0 w-full max-w-[1600px] flex-1 flex-col px-6 py-6 md:py-10'>
        {children}
      </div>
    </div>
  );
}
