import type { ReactNode } from 'react';

interface FullScreenPageProps {
  children: ReactNode;
}

export const FullScreenPage = ({ children }: FullScreenPageProps) => (
  <div className='bg-background fixed inset-0 z-[100] overflow-auto'>{children}</div>
);
