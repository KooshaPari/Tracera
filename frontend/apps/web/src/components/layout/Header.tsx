import { useLocation, useNavigate } from '@tanstack/react-router';
import { Activity, Bell, LogIn, LogOut } from 'lucide-react';
import { useCallback, useMemo } from 'react';

import { MobileMenu } from '@/components/mobile/MobileMenu';
import { useNotifications } from '@/hooks/useNotifications';
import { useProject } from '@/hooks/useProjects';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@tracertm/ui';

import { Breadcrumbs } from './Breadcrumb';

const HOME_PATH = '/';
const HOME_ALIAS_PATH = '/home';
const LOGIN_PATH = '/auth/login';
const PROJECTS_PATH = '/projects';
const PROJECTS_PREFIX = '/projects/';

const getProjectIdFromPathname = function getProjectIdFromPathname(pathname: string): string {
  if (!pathname.startsWith(PROJECTS_PREFIX)) {
    return '';
  }
  const [, projectId = ''] = pathname.split(PROJECTS_PREFIX);
  const [cleanProjectId = ''] = projectId.split('/');
  return cleanProjectId;
};

const getHeaderTitle = function getHeaderTitle(pathname: string, projectName?: string): string {
  if (pathname === HOME_PATH || pathname === HOME_ALIAS_PATH) {
    return 'Dashboard';
  }
  if (pathname === PROJECTS_PATH) {
    return 'Projects';
  }
  if (pathname.startsWith(PROJECTS_PREFIX)) {
    return projectName ?? 'Project';
  }
  return 'TraceRTM';
};

export const Header = function Header(): JSX.Element {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { unreadCount } = useNotifications();

  const projectId = getProjectIdFromPathname(location.pathname);
  const { data: project } = useProject(projectId);

  const title = useMemo(
    () => getHeaderTitle(location.pathname, project?.name),
    [location.pathname, project?.name],
  );

  const handleLogin = useCallback((): void => {
    navigate({ to: LOGIN_PATH }).catch(() => null);
  }, [navigate]);

  const handleLogout = useCallback((): void => {
    logout()
      .finally(() => {
        navigate({ to: LOGIN_PATH }).catch(() => null);
      })
      .catch(() => null);
  }, [logout, navigate]);

  return (
    <header
      role='banner'
      className='sticky top-0 z-50 flex h-16 items-center justify-between border-b px-4 sm:px-6'
    >
      <div className='flex min-w-0 flex-1 items-center gap-3'>
        <MobileMenu />
        <div className='flex min-w-0 items-center gap-2'>
          <div className='bg-primary/10 text-primary flex h-8 w-8 shrink-0 items-center justify-center rounded-lg'>
            <Activity className='h-4 w-4' />
          </div>
          <h2 className='truncate text-sm font-semibold'>{title}</h2>
        </div>
        <div className='ml-2 hidden lg:block'>
          <Breadcrumbs />
        </div>
      </div>

      <div className='flex items-center gap-2'>
        <div className='text-muted-foreground hidden items-center gap-1 text-xs sm:flex'>
          <Bell className='h-4 w-4' />
          <span>{unreadCount}</span>
        </div>

        {!user ? (
          <Button size='sm' className='gap-2 rounded-full font-semibold' onClick={handleLogin}>
            <LogIn className='h-4 w-4' />
            <span className='hidden sm:inline'>Sign in</span>
          </Button>
        ) : (
          <Button
            variant='ghost'
            size='sm'
            className='gap-2 rounded-full px-3 font-semibold'
            onClick={handleLogout}
          >
            <span className='max-w-[160px] truncate'>{user.name ?? user.email}</span>
            <LogOut className='h-4 w-4' />
          </Button>
        )}
      </div>
    </header>
  );
};
