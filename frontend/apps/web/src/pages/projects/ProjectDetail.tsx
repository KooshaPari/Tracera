import { Outlet, useParams } from '@tanstack/react-router';

import { useRealtimeUpdates } from '@/hooks/useRealtime';

export const ProjectDetail = () => {
  const params = useParams({ strict: false });
  const projectId = params.projectId as string | undefined;

  // Enable real-time updates for this project
  useRealtimeUpdates(projectId);

  return (
    <div className='space-y-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h2 className='text-2xl font-bold'>Project: {projectId}</h2>
          <p className='text-muted-foreground'>TraceRTM Frontend - Desktop App + Website</p>
        </div>
      </div>
      <Outlet />
    </div>
  );
};
