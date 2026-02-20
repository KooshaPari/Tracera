import { createFileRoute } from '@tanstack/react-router';

import { requireAuth } from '@/lib/route-guards';
import { SettingsView } from '@/views/SettingsView';

function SettingsComponent() {
  return (
    <div className='flex-1 space-y-6 p-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Settings</h1>
          <p className='text-muted-foreground'>
            Configure your TraceRTM platform preferences and integrations
          </p>
        </div>
      </div>

      <SettingsView />
    </div>
  );
}

export const Route = createFileRoute('/settings')({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: SettingsComponent,
  loader: async () => ({}),
});
