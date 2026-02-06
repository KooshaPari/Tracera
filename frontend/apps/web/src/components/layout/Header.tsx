import { useLocation, useNavigate, useParams } from '@tanstack/react-router';
import {
  Activity,
  AlertTriangle,
  Bell,
  CheckCircle,
  Info,
  LogIn,
  LogOut,
  Search,
  Settings,
  Shield,
  XCircle,
} from 'lucide-react';
import { useCallback, useMemo } from 'react';

import { MobileMenu } from '@/components/mobile/MobileMenu';
import { useNotifications } from '@/hooks/useNotifications';
import { useProject } from '@/hooks/useProjects';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/stores/authStore';
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  ScrollArea,
} from '@tracertm/ui';

import { Breadcrumbs } from './Breadcrumb';

const AVATAR_INITIALS_MAX = 2;

const getNotificationIcon = function getNotificationIcon(type: string) {
  switch (type) {
    case 'success': {
      return <CheckCircle className='h-4 w-4 text-green-500' />;
    }
    case 'warning': {
      return <AlertTriangle className='h-4 w-4 text-amber-500' />;
    }
    case 'error': {
      return <XCircle className='h-4 w-4 text-red-500' />;
    }
    default: {
      return <Info className='h-4 w-4 text-blue-500' />;
    }
  }
};

export const Header = function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const params = useParams({ strict: false });
  const { user, logout } = useAuthStore();
  const { notifications, unreadCount, markAsRead, markAllRead } = useNotifications();
  const projectId = params.projectId as string | undefined;
  const { data: project } = useProject(projectId || '');

  const handleLogout = useCallback(() => {
    logout()
      .then(() => {
        navigate({ to: '/auth/login' });
      })
      .catch(() => {});
  }, [logout, navigate]);

  // Get initials for avatar
  const initials = user?.name
    ? user.name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, AVATAR_INITIALS_MAX)
    : 'U';

  // Dynamic header content based on route
  const headerContext = useMemo(() => {
    const path = location.pathname;

    if (path.startsWith('/projects/') && projectId) {
      if (path.includes('/views/')) {
        const viewType = path.split('/views/')[1]?.split('/')[0];
        return {
          project,
          subtitle: viewType
            ? `${viewType.charAt(0).toUpperCase() + viewType.slice(1)} View`
            : undefined,
          title: project?.name || 'Project',
          type: 'project-view',
          viewType,
        };
      }
      return {
        project,
        subtitle: project?.description || undefined,
        title: project?.name || 'Project',
        type: 'project',
      };
    }

    if (path === '/projects') {
      return {
        subtitle: '',
        title: 'Projects',
        type: 'projects-list',
      };
    }

    if (path === '/' || path === '/home') {
      return {
        subtitle: undefined,
        title: 'Dashboard',
        type: 'dashboard',
      };
    }

    return {
      subtitle: undefined,
      title: 'TraceRTM',
      type: 'default',
    };
  }, [location.pathname, project, projectId]);

  return (
    <header
      role='banner'
      className='sticky top-0 z-50 flex h-16 items-center justify-between border-b border-white/0 bg-[linear-gradient(90deg,rgba(2,6,23,0.65),rgba(2,6,23,0.35)_60%,rgba(15,23,42,0.25))] pr-4 pl-4 shadow-[0_1px_0_rgba(15,23,42,0.6)] backdrop-blur-2xl transition-all duration-300 sm:pr-6 sm:pl-6'
    >
      {/* Left: Mobile menu & Context & Breadcrumbs */}
      <div className='flex min-w-0 flex-1 items-center gap-2 overflow-hidden sm:gap-4'>
        <MobileMenu />
        {/* Dynamic Context Info */}
        {headerContext.type === 'project' || headerContext.type === 'project-view' ? (
          <div className='flex min-w-0 items-center gap-3'>
            <div className='bg-primary/10 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg'>
              <Activity className='text-primary h-4 w-4' />
            </div>
            <div className='min-w-0'>
              <h2 className='truncate text-sm font-bold'>{headerContext.title}</h2>
              {headerContext.subtitle && (
                <p className='text-muted-foreground truncate text-xs'>{headerContext.subtitle}</p>
              )}
            </div>
            {/* Simplified Date Display */}
            {project?.createdAt && (
              <span className='text-muted-foreground/50 hidden shrink-0 text-[10px] xl:inline-block'>
                Created {new Date(project.createdAt).toLocaleDateString()}
              </span>
            )}
          </div>
        ) : (
          <div className='flex min-w-0 items-center gap-3'>
            <h2 className='text-sm font-bold'>{headerContext.title}</h2>
            {headerContext.subtitle && (
              <p className='text-muted-foreground hidden text-xs sm:block'>
                {headerContext.subtitle}
              </p>
            )}
          </div>
        )}

        <div className='ml-4 hidden lg:block'>
          <Breadcrumbs />
        </div>
      </div>

      {/* Actions */}
      <div className='flex items-center gap-2'>
        {/* Search */}
        <div className='group relative mr-2 hidden md:block'>
          <Search className='text-muted-foreground group-focus-within:text-primary absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 transition-colors' />
          <input
            type='text'
            placeholder='Search... (⌘K)'
            className='bg-muted/50 focus:ring-primary focus:bg-background h-9 w-48 rounded-full border pr-4 pl-9 text-xs transition-all focus:ring-1 focus:outline-none lg:w-64'
          />
        </div>

        {/* Notifications Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <span>
              <Button variant='ghost' size='icon' className='relative h-9 w-9 rounded-full'>
                <Bell className='h-4 w-4' />
                {unreadCount > 0 && (
                  <span className='bg-primary ring-background absolute top-2 right-2 flex h-2 w-2 animate-pulse items-center justify-center rounded-full ring-2' />
                )}
              </Button>
            </span>
          </DropdownMenuTrigger>
          <DropdownMenuContent align='end' className='w-80'>
            <div className='flex items-center justify-between px-2 py-1.5'>
              <DropdownMenuLabel className='p-0'>Notifications</DropdownMenuLabel>
              {unreadCount > 0 && (
                <Button
                  variant='ghost'
                  size='xs'
                  className='text-primary hover:text-primary/80 h-6 text-[10px]'
                  onClick={(e) => {
                    e.preventDefault();
                    markAllRead.mutate();
                  }}
                >
                  Mark all read
                </Button>
              )}
            </div>
            <DropdownMenuSeparator />
            <ScrollArea className='h-[300px]'>
              {notifications.length === 0 ? (
                <div className='text-muted-foreground py-8 text-center text-xs'>
                  <Bell className='mx-auto mb-2 h-8 w-8 opacity-20' />
                  <p>No new notifications</p>
                </div>
              ) : (
                <div className='space-y-1 p-1'>
                  {notifications.map((notification) => (
                    <button
                      key={notification.id}
                      className={cn(
                        'relative flex items-start gap-3 p-2 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer group w-full text-left',
                        !notification.read_at && 'bg-muted/30',
                      )}
                      onClick={() => {
                        if (!notification.read_at) {
                          markAsRead.mutate(notification.id);
                        }
                        if (notification.link) {
                          navigate({ to: notification.link });
                        }
                      }}
                    >
                      <div className='mt-1 shrink-0'>{getNotificationIcon(notification.type)}</div>
                      <div className='min-w-0 flex-1'>
                        <div className='flex items-center justify-between gap-2'>
                          <p
                            className={cn(
                              'text-xs font-medium',
                              !notification.read_at && 'text-foreground',
                            )}
                          >
                            {notification.title}
                          </p>
                          <span className='text-muted-foreground text-[10px] whitespace-nowrap'>
                            {new Date(notification.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className='text-muted-foreground mt-0.5 line-clamp-2 text-[11px]'>
                          {notification.message}
                        </p>
                      </div>
                      {!notification.read_at && (
                        <div className='bg-primary absolute top-1/2 right-2 h-1.5 w-1.5 -translate-y-1/2 rounded-full' />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </ScrollArea>
            <DropdownMenuSeparator />
            <DropdownMenuItem className='text-muted-foreground cursor-pointer justify-center text-xs'>
              View all notifications
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* User Profile / Sign in */}
        <div className='bg-border mx-1 hidden h-8 w-px sm:block' />

        {!user ? (
          <Button
            variant='default'
            size='sm'
            className='gap-2 rounded-full font-semibold'
            onClick={() => navigate({ to: '/auth/login' })}
          >
            <LogIn className='h-4 w-4' />
            <span className='hidden sm:inline'>Sign in</span>
          </Button>
        ) : (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant='ghost'
                size='sm'
                className='hover:bg-muted ml-1 gap-2 rounded-full px-1'
              >
                <Avatar className='border-border h-8 w-8 border'>
                  <AvatarImage src={user?.avatar} alt={user?.name || 'User'} />
                  <AvatarFallback className='bg-primary/10 text-primary text-xs font-bold'>
                    {initials}
                  </AvatarFallback>
                </Avatar>
                <div className='mr-1 flex hidden flex-col items-start text-left md:flex'>
                  <span className='max-w-[100px] truncate text-xs leading-none font-semibold'>
                    {user?.name || 'User'}
                  </span>
                  <span className='text-muted-foreground mt-0.5 max-w-[100px] truncate text-[10px] leading-none'>
                    {user?.email}
                  </span>
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align='end' className='w-56'>
              <DropdownMenuLabel>
                <div className='flex flex-col space-y-1'>
                  <p className='text-sm leading-none font-medium'>{user?.name || 'User'}</p>
                  <p className='text-muted-foreground text-xs leading-none'>{user?.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className='cursor-pointer'
                onClick={() => navigate({ to: '/settings' })}
              >
                <Settings className='mr-2 h-4 w-4' />
                <span>Settings</span>
              </DropdownMenuItem>
              {user?.role === 'admin' && (
                <DropdownMenuItem
                  className='cursor-pointer'
                  onClick={() => navigate({ to: '/admin' })}
                >
                  <Shield className='mr-2 h-4 w-4' />
                  <span>Admin Panel</span>
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className='text-destructive focus:text-destructive cursor-pointer'
                onClick={handleLogout}
              >
                <LogOut className='mr-2 h-4 w-4' />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    </header>
  );
};
