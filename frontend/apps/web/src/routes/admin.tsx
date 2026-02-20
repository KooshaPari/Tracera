import { createFileRoute } from '@tanstack/react-router';
import { Shield } from 'lucide-react';

import { requireAdmin } from '@/lib/route-guards';

function AdminPage() {
  return (
    <div className='flex-1 space-y-6 p-6'>
      <div className='flex items-center gap-3'>
        <Shield className='text-primary h-8 w-8' aria-hidden />
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Admin Panel</h1>
          <p className='text-muted-foreground'>System administration and platform settings</p>
        </div>
      </div>

      <div className='bg-card text-card-foreground rounded-lg border p-6 shadow-sm'>
        <h2 className='mb-2 text-lg font-semibold'>System admin access</h2>
        <p className='text-muted-foreground text-sm'>
          You are signed in as a system administrator. Admin-only features and full access to
          projects and resources are available.
        </p>
      </div>

      <div className='bg-muted/50 text-muted-foreground rounded-lg border p-6 text-sm'>
        <p>
          Additional admin tools (e.g. user management, audit logs, feature flags) can be added here
          as needed.
        </p>
      </div>
    </div>
  );
}

export const Route = createFileRoute('/admin')({
  beforeLoad: async () => {
    await requireAdmin();
  },
  component: AdminPage,
});
