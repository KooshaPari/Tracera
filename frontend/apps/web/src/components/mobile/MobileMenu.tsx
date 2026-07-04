import { useLocation, useNavigate } from '@tanstack/react-router';
import { ChevronRight, FolderOpen, Home, LogIn, LogOut, Menu, Settings, X } from 'lucide-react';
import { useCallback, useState } from 'react';

import type { User } from '@/stores/authStore';

import { cn } from '@/lib/utils';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@tracertm/ui';

interface MobileMenuProps {
  className?: string;
}

const SignInButton = function SignInButton({
  onClick,
}: {
  onClick: (e: React.MouseEvent<HTMLButtonElement>) => void;
}) {
  return (
    <button
      type='button'
      data-href='/auth/login'
      onClick={onClick}
      className={cn(
        'w-full flex items-center gap-3 px-4 py-3 rounded-lg',
        'min-h-[52px] transition-all duration-200',
        'bg-primary text-primary-foreground hover:bg-primary/90',
        'focus:outline-none focus:ring-2 focus:ring-primary',
        'active:scale-95 transition-transform',
      )}
    >
      <LogIn className='h-5 w-5 shrink-0' />
      <span className='flex-1 text-left text-sm font-medium'>Sign in to your account</span>
    </button>
  );
};

const AccountAndLogout = function AccountAndLogout({
  user,
  onLogout,
}: {
  user: User;
  onLogout: () => void;
}) {
  return (
    <>
      <div className='bg-muted/50 rounded-lg px-4 py-3'>
        <p className='text-muted-foreground mb-1 text-xs font-semibold tracking-widest uppercase'>
          Account
        </p>
        <p className='text-foreground truncate text-sm font-medium'>{user?.name ?? 'User'}</p>
        <p className='text-muted-foreground mt-0.5 truncate text-xs'>{user?.email}</p>
      </div>
      <button
        type='button'
        onClick={onLogout}
        className={cn(
          'w-full flex items-center gap-3 px-4 py-3 rounded-lg',
          'min-h-[52px] transition-all duration-200',
          'bg-destructive/10 text-destructive hover:bg-destructive/20',
          'border border-destructive/30',
          'focus:outline-none focus:ring-2 focus:ring-destructive',
          'active:scale-95 transition-transform',
        )}
      >
        <LogOut className='h-5 w-5 shrink-0' />
        <span className='flex-1 text-left text-sm font-medium'>Log out</span>
      </button>
    </>
  );
};

const MENU_ITEMS = [
  { href: '/home', icon: Home, label: 'Dashboard' },
  { href: '/projects', icon: FolderOpen, label: 'Projects' },
  { href: '/settings', icon: Settings, label: 'Settings' },
] as const;

interface MenuPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onMenuClick: (e: React.MouseEvent<HTMLButtonElement>) => void;
  onLogout: () => void;
  user: User | null;
  isActive: (href: string) => boolean;
}

const MenuPanel = function MenuPanel({
  isOpen,
  onClose,
  onMenuClick,
  onLogout,
  user,
  isActive,
}: MenuPanelProps) {
  return (
    <>
      <div
        className='fixed inset-0 z-40 bg-black/50 md:hidden'
        onClick={onClose}
        aria-hidden='true'
      />
      <div
        id='mobile-menu'
        className={cn(
          'fixed top-16 left-0 right-0 bottom-0 z-50 bg-background/95 backdrop-blur-sm',
          'md:hidden transform transition-all duration-300 ease-in-out',
          'flex flex-col overflow-y-auto',
          isOpen ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0 pointer-events-none',
        )}
      >
        <div className='border-border/30 border-b p-4 sm:p-6'>
          <h2 className='text-muted-foreground text-sm font-semibold tracking-widest uppercase'>
            Menu
          </h2>
        </div>
        <nav className='flex-1 space-y-2 p-4 sm:p-6'>
          {MENU_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <button
                key={item.href}
                type='button'
                data-href={item.href}
                onClick={onMenuClick}
                className={cn(
                  'w-full flex items-center gap-3 px-4 py-3 rounded-lg',
                  'min-h-[52px] transition-all duration-200',
                  'focus:outline-none focus:ring-2 focus:ring-primary',
                  'active:scale-95 transition-transform',
                  active
                    ? 'bg-primary/10 text-primary font-semibold border border-primary/30'
                    : 'text-foreground hover:bg-muted border border-transparent',
                )}
              >
                <Icon className='h-5 w-5 shrink-0' />
                <span className='flex-1 text-left text-sm font-medium'>{item.label}</span>
                {active && <ChevronRight className='h-4 w-4 shrink-0' />}
              </button>
            );
          })}
        </nav>
        <div className='border-border/30 space-y-3 border-t p-4 sm:p-6'>
          {!user ? (
            <SignInButton onClick={onMenuClick} />
          ) : (
            <AccountAndLogout user={user} onLogout={onLogout} />
          )}
        </div>
      </div>
    </>
  );
};

/**
 * Mobile hamburger menu with proper 44px+ touch targets
 * Compliant with WCAG accessibility guidelines
 */
export const MobileMenu = function MobileMenu({ className }: MobileMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const handleNavigate = useCallback(
    async (to: string) => {
      setIsOpen(false);
      await navigate({ to } as Parameters<typeof navigate>[0]);
    },
    [navigate],
  );

  const handleClose = useCallback(() => {
    setIsOpen(false);
  }, []);

  const handleLogout = useCallback(() => {
    setIsOpen(false);
    logout()
      .then(async () => navigate({ to: '/auth/login' }))
      .catch(() => {});
  }, [logout, navigate]);

  const isActive = useCallback(
    (href: string) => location.pathname === href || location.pathname.startsWith(`${href}/`),
    [location.pathname],
  );

  const handleToggleOpen = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const handleMenuClick = useCallback(
    (e: React.MouseEvent<HTMLButtonElement>) => {
      const href = e.currentTarget.getAttribute('data-href');
      if (href) {
        handleNavigate(href).catch(() => {});
      }
    },
    [handleNavigate],
  );

  return (
    <>
      <Button
        variant='ghost'
        size='icon'
        onClick={handleToggleOpen}
        className={cn(
          'h-11 w-11 rounded-lg md:hidden',
          'focus:ring-2 focus:ring-primary focus:ring-offset-0',
          'active:scale-95 transition-transform',
          className,
        )}
        aria-label={isOpen ? 'Close menu' : 'Open menu'}
        aria-expanded={isOpen}
        aria-controls='mobile-menu'
      >
        {isOpen ? <X className='h-6 w-6' /> : <Menu className='h-6 w-6' />}
      </Button>
      {isOpen && (
        <MenuPanel
          isOpen={isOpen}
          onClose={handleClose}
          onMenuClick={handleMenuClick}
          onLogout={handleLogout}
          user={user}
          isActive={isActive}
        />
      )}
    </>
  );
};
