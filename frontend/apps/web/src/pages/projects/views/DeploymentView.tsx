import {
  CheckCircle,
  Clock,
  Cloud,
  ExternalLink,
  GitBranch,
  Play,
  RefreshCw,
  XCircle,
} from 'lucide-react';
import { useState } from 'react';

interface Deployment {
  id: string;
  environment: 'production' | 'staging' | 'development';
  status: 'success' | 'failed' | 'in_progress' | 'pending';
  version: string;
  branch: string;
  commit: string;
  deployedAt: string;
  deployedBy: string;
  duration: string;
}

interface Environment {
  name: string;
  url: string;
  status: 'healthy' | 'degraded' | 'down';
  lastDeploy: Deployment | null;
}

const environments: Environment[] = [
  {
    lastDeploy: {
      branch: 'main',
      commit: 'a3b4c5d',
      deployedAt: '2024-11-29 14:30',
      deployedBy: 'GitHub Actions',
      duration: '2m 34s',
      environment: 'production',
      id: '1',
      status: 'success',
      version: 'v1.2.0',
    },
    name: 'Production',
    status: 'healthy',
    url: 'https://tracertm.dev',
  },
  {
    lastDeploy: {
      branch: 'develop',
      commit: 'f6e7d8c',
      deployedAt: '2024-11-29 16:45',
      deployedBy: 'KooshaPari',
      duration: '2m 12s',
      environment: 'staging',
      id: '2',
      status: 'success',
      version: 'v1.3.0-rc1',
    },
    name: 'Staging',
    status: 'healthy',
    url: 'https://staging.tracertm.dev',
  },
  {
    lastDeploy: {
      branch: 'feature/new-ui',
      commit: 'b9c0d1e',
      deployedAt: '2024-11-29 17:00',
      deployedBy: 'KooshaPari',
      duration: '1m 45s',
      environment: 'development',
      id: '3',
      status: 'failed',
      version: 'v1.3.0-dev',
    },
    name: 'Development',
    status: 'degraded',
    url: 'https://dev.tracertm.dev',
  },
];

const recentDeploys: Deployment[] = [
  {
    branch: 'develop',
    commit: 'f6e7d8c',
    deployedAt: '2024-11-29 16:45',
    deployedBy: 'KooshaPari',
    duration: '2m 12s',
    environment: 'staging',
    id: '4',
    status: 'success',
    version: 'v1.3.0-rc1',
  },
  {
    branch: 'feature/new-ui',
    commit: 'b9c0d1e',
    deployedAt: '2024-11-29 17:00',
    deployedBy: 'KooshaPari',
    duration: '1m 45s',
    environment: 'development',
    id: '5',
    status: 'failed',
    version: 'v1.3.0-dev',
  },
  {
    branch: 'main',
    commit: 'a3b4c5d',
    deployedAt: '2024-11-29 14:30',
    deployedBy: 'GitHub Actions',
    duration: '2m 34s',
    environment: 'production',
    id: '6',
    status: 'success',
    version: 'v1.2.0',
  },
  {
    branch: 'develop',
    commit: '123abc4',
    deployedAt: '2024-11-28 10:15',
    deployedBy: 'GitHub Actions',
    duration: '2m 05s',
    environment: 'staging',
    id: '7',
    status: 'success',
    version: 'v1.2.0-rc2',
  },
];

const statusIcons = {
  failed: XCircle,
  in_progress: RefreshCw,
  pending: Clock,
  success: CheckCircle,
};
const statusColors = {
  failed: 'text-red-500',
  in_progress: 'text-blue-500 animate-spin',
  pending: 'text-yellow-500',
  success: 'text-green-500',
};
const envColors = {
  development: 'bg-blue-100 text-blue-700',
  production: 'bg-red-100 text-red-700',
  staging: 'bg-yellow-100 text-yellow-700',
};
const healthColors = {
  degraded: 'bg-yellow-500',
  down: 'bg-red-500',
  healthy: 'bg-green-500',
};

export const DeploymentView = () => {
  const [deploying, setDeploying] = useState<string | null>(null);

  const triggerDeploy = (env: string) => {
    setDeploying(env);
    setTimeout(() => {
      setDeploying(null);
    }, 3000);
  };

  return (
    <div className='space-y-6'>
      <div className='flex items-center justify-between'>
        <h3 className='text-lg font-semibold'>Deployment View</h3>
        <button className='hover:bg-accent flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm'>
          <RefreshCw className='h-4 w-4' /> Refresh
        </button>
      </div>

      <div className='grid gap-4 md:grid-cols-3'>
        {environments.map((env) => (
          <div key={env.name} className='rounded-lg border p-4'>
            <div className='flex items-center justify-between'>
              <div className='flex items-center gap-2'>
                <Cloud className='h-5 w-5' />
                <span className='font-semibold'>{env.name}</span>
                <span
                  className={`h-2 w-2 rounded-full ${healthColors[env.status]}`}
                  title={env.status}
                />
              </div>
              <a
                href={env.url}
                target='_blank'
                rel='noopener'
                className='text-muted-foreground hover:text-primary'
              >
                <ExternalLink className='h-4 w-4' />
              </a>
            </div>
            {env.lastDeploy && (
              <div className='mt-3 space-y-2 text-sm'>
                <div className='flex items-center gap-2'>
                  {(() => {
                    const Icon = statusIcons[env.lastDeploy.status];
                    return <Icon className={`h-4 w-4 ${statusColors[env.lastDeploy.status]}`} />;
                  })()}
                  <span className='font-mono'>{env.lastDeploy.version}</span>
                </div>
                <div className='text-muted-foreground flex items-center gap-2'>
                  <GitBranch className='h-3 w-3' />
                  <span>{env.lastDeploy.branch}</span>
                  <span className='font-mono text-xs'>{env.lastDeploy.commit}</span>
                </div>
                <div className='text-muted-foreground text-xs'>
                  {env.lastDeploy.deployedAt} by {env.lastDeploy.deployedBy}
                </div>
              </div>
            )}
            <button
              onClick={() => {
                triggerDeploy(env.name);
              }}
              disabled={deploying === env.name}
              className='bg-primary text-primary-foreground mt-4 flex w-full items-center justify-center gap-2 rounded-lg py-2 text-sm disabled:opacity-50'
            >
              {deploying === env.name ? (
                <>
                  <RefreshCw className='h-4 w-4 animate-spin' /> Deploying...
                </>
              ) : (
                <>
                  <Play className='h-4 w-4' /> Deploy
                </>
              )}
            </button>
          </div>
        ))}
      </div>

      <div>
        <h4 className='mb-3 font-medium'>Recent Deployments</h4>
        <div className='rounded-lg border'>
          {recentDeploys.map((d) => {
            const Icon = statusIcons[d.status];
            return (
              <div key={d.id} className='flex items-center gap-4 border-b p-3 last:border-b-0'>
                <Icon className={`h-5 w-5 ${statusColors[d.status]}`} />
                <span
                  className={`rounded px-2 py-0.5 text-xs font-medium ${envColors[d.environment]}`}
                >
                  {d.environment}
                </span>
                <span className='font-mono text-sm'>{d.version}</span>
                <div className='text-muted-foreground flex items-center gap-1 text-sm'>
                  <GitBranch className='h-3 w-3' /> {d.branch}
                </div>
                <span className='text-muted-foreground ml-auto text-xs'>{d.deployedAt}</span>
                <span className='text-muted-foreground text-xs'>{d.duration}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
