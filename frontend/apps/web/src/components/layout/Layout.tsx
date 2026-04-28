import { Outlet, useLocation, useMatches } from '@tanstack/react-router';
import { useCallback, useEffect, useRef } from 'react';

import { ChatBubble } from '@/components/chat/ChatBubble';
import { cn } from '@/lib/utils';

import { Header } from './Header';
import { Sidebar } from './Sidebar';

export const Layout = function Layout() {
  const location = useLocation();
  const matches = useMatches();
  const path = location.pathname;
  const isItemDetail =
    /\/items\/[^/]+$/.test(path) || /\/projects\/[^/]+\/views\/[^/]+\/[^/]+$/.test(path);
  const isE2E = typeof navigator !== 'undefined' && navigator.webdriver;

  // Check if any active route is an auth route
  const isAuthRoute = matches.some((match) => match.routeId.startsWith('/auth'));

  const shelllessRouteIds = new Set<string>();

  const isShelllessRoute = matches.some((match) => shelllessRouteIds.has(String(match.routeId)));
  const isLandingRoute = path === '/' || path.startsWith('/landing');

  const isErrorState = matches.some((match) =>
    ['error', 'notFound', 'redirected'].includes(match.status),
  );
  const hasHandledFirstTabRef = useRef(false);

  const handleSkipToMain = useCallback((e: React.SyntheticEvent) => {
    e.preventDefault();
    hasHandledFirstTabRef.current = true;
    const mainContent = document.querySelector('main');
    if (mainContent) {
      mainContent.setAttribute('tabindex', '-1');
      mainContent.focus();
      mainContent.addEventListener(
        'blur',
        () => {
          mainContent.removeAttribute('tabindex');
        },
        { once: true },
      );
    }
  }, []);

  const handleSkipKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (event.key === 'Enter' || event.key === ' ') {
        handleSkipToMain(event);
      }
    },
    [handleSkipToMain],
  );

  useEffect(() => {
    const shouldRenderShell = !(
      (path === '/' && !isE2E) ||
      path.startsWith('/auth/') ||
      isAuthRoute ||
      isShelllessRoute ||
      isErrorState
    );
    if (!shouldRenderShell) {
      return;
    }
    const handleFirstTab = (event: KeyboardEvent) => {
      if (event.key !== 'Tab' || event.shiftKey) {
        return;
      }
      if (hasHandledFirstTabRef.current) {
        return;
      }
      if (document.querySelector('[role="dialog"][aria-modal="true"]')) {
        return;
      }
      const skipLink = document.querySelector('#skip-to-main');
      if (skipLink) {
        event.preventDefault();
        hasHandledFirstTabRef.current = true;
        (skipLink as HTMLElement).focus();
      }
    };
    const handleFirstFocus = (event: FocusEvent) => {
      if (hasHandledFirstTabRef.current) {
        return;
      }
      if (document.querySelector('[role="dialog"][aria-modal="true"]')) {
        return;
      }
      const skipLink = document.querySelector('#skip-to-main');
      if (!skipLink || event.target === skipLink) {
        return;
      }
      hasHandledFirstTabRef.current = true;
      (skipLink as HTMLElement).focus();
    };
    document.addEventListener('keydown', handleFirstTab, true);
    document.addEventListener('focusin', handleFirstFocus, true);
    return () => {
      document.removeEventListener('keydown', handleFirstTab, true);
      document.removeEventListener('focusin', handleFirstFocus, true);
    };
  }, [isAuthRoute, isE2E, isErrorState, isShelllessRoute, path]);

  // Landing page, auth, redirects, and error states should not render the shell
  if (path.startsWith('/auth/') || isAuthRoute || isShelllessRoute || isErrorState) {
    return <Outlet />;
  }

  // 404 check - If only the root route matches, it's a global 404
  // (Root route is always matches[0])
  const isGlobal404 = matches.length === 1 && matches[0]?.routeId === '__root__';

  if (isGlobal404) {
    return (
      <div className='bg-background flex h-screen overflow-hidden'>
        <main className='relative z-10 flex-1 overflow-auto'>
          <Outlet />
        </main>
      </div>
    );
  }

  if (isLandingRoute) {
    return (
      <main
        id='main-content'
        role='main'
        tabIndex={-1}
        className='custom-scrollbar min-h-0 flex-1 overflow-auto'
      >
        <Outlet />
      </main>
    );
  }

  return (
    <div className='selection:bg-primary/20 selection:text-primary flex h-screen overflow-hidden bg-transparent'>
      <div className='pointer-events-none fixed inset-0 z-0 bg-[radial-gradient(circle_at_10%_15%,rgba(249,115,22,0.28),transparent_45%),radial-gradient(circle_at_85%_8%,rgba(14,116,144,0.3),transparent_42%),radial-gradient(circle_at_20%_75%,rgba(16,185,129,0.24),transparent_40%)]' />
      <div className='pointer-events-none fixed inset-0 z-0 bg-[linear-gradient(135deg,rgba(15,23,42,0.08),transparent_55%,rgba(8,47,73,0.12))]' />
      {!isItemDetail && (
        <div className='pointer-events-none fixed inset-0 z-0 bg-[radial-gradient(circle_at_30%_40%,rgba(148,163,184,0.08),transparent_55%)]' />
      )}
      {/* Skip to main content - visually hidden but focusable */}
      <a
        id='skip-to-main'
        href='#main-content'
        onClick={handleSkipToMain}
        onKeyDown={handleSkipKeyDown}
        tabIndex={0}
        className='focus-visible:bg-primary focus-visible:text-primary-foreground sr-only focus-visible:not-sr-only focus-visible:fixed focus-visible:top-4 focus-visible:left-4 focus-visible:z-[10000] focus-visible:rounded-lg focus-visible:px-4 focus-visible:py-2'
      >
        Skip to main content
      </a>

      <Sidebar />
      <div className='relative flex min-w-0 flex-1 flex-col overflow-hidden bg-transparent'>
        <div className='bg-grid-white/[0.02] pointer-events-none absolute inset-0 bg-[size:32px_32px]' />

        <Header />
        <main
          id='main-content'
          role='main'
          tabIndex={-1}
          className='custom-scrollbar relative z-10 min-h-0 min-w-0 flex-1 overflow-auto'
        >
          <div className='pointer-events-none absolute inset-x-0 top-0 h-44 bg-[radial-gradient(circle_at_20%_0%,rgba(59,130,246,0.18),transparent_65%),radial-gradient(circle_at_80%_0%,rgba(249,115,22,0.16),transparent_55%)]' />
          <div
            key={path}
            className={cn(
              isItemDetail ? 'p-0' : 'py-6 pr-4 sm:pr-6 lg:pr-8',
              'min-w-0 w-full max-w-full animate-in-fade-up',
            )}
          >
            <Outlet />
          </div>
        </main>
      </div>
      {/* Chat Sidebar - hidden on small screens to avoid horizontal overflow */}
      <div className='hidden xl:flex'>
        <ChatBubble />
      </div>
    </div>
  );
};

export default Layout;
