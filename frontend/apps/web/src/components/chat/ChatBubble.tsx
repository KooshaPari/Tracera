/**
 * ChatSidebar - Permanent right sidebar with resize functionality
 */

import type { CSSProperties, MouseEvent as ReactMouseEvent } from 'react';

import { motion } from 'framer-motion';
import { ChevronRight, MessageCircle } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { useChatStore } from '@/stores/chat-store';
import { Button, cn } from '@tracertm/ui';

import { ChatPanel } from './ChatPanel';

const MAX_SIDEBAR_WIDTH = 800;
const MIN_SIDEBAR_WIDTH = 300;
const RESIZE_CURSOR = 'ew-resize';
const SIDEBAR_COLLAPSE_KEY = 'chat-sidebar-collapsed';
const SIDEBAR_WIDTH_KEY = 'chat-sidebar-width';
const RESIZE_HANDLE_STYLE: CSSProperties = { cursor: RESIZE_CURSOR };
const COLLAPSED_ANIMATION = { opacity: 1, scale: 1 };
const COLLAPSED_EXIT = { opacity: 0, scale: 0 };
const COLLAPSED_INITIAL = { opacity: 0, scale: 0 };
const COLLAPSED_TRANSITION = { damping: 20, stiffness: 300, type: 'spring' };
const noop = () => {};

const readCollapsedState = (): boolean => {
  if (typeof localStorage === 'undefined') {
    return false;
  }
  return localStorage.getItem(SIDEBAR_COLLAPSE_KEY) === 'true';
};

const writeCollapsedState = (value: boolean) => {
  if (typeof localStorage === 'undefined') {
    return;
  }
  localStorage.setItem(SIDEBAR_COLLAPSE_KEY, String(value));
};

const writeSidebarWidth = (value: number) => {
  if (typeof localStorage === 'undefined') {
    return;
  }
  localStorage.setItem(SIDEBAR_WIDTH_KEY, value.toString());
};

const SidebarResizeHandle = ({
  isResizing,
  onMouseDown,
  onToggleCollapse,
}: {
  isResizing: boolean;
  onMouseDown: (event: ReactMouseEvent<HTMLDivElement>) => void;
  onToggleCollapse: () => void;
}) => {
  const handleToggleClick = useCallback(
    (event: ReactMouseEvent<HTMLButtonElement>) => {
      event.stopPropagation();
      onToggleCollapse();
    },
    [onToggleCollapse],
  );

  const handleToggleMouseDown = useCallback((event: ReactMouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
  }, []);

  return (
    <div
      onMouseDown={onMouseDown}
      className={cn(
        'w-2 cursor-ew-resize bg-transparent hover:bg-primary/30 transition-all flex items-center justify-center group shrink-0 relative',
        'active:cursor-ew-resize',
        isResizing && 'bg-primary/50 cursor-ew-resize',
      )}
      role='separator'
      aria-label='Resize chat sidebar'
      aria-orientation='vertical'
      style={RESIZE_HANDLE_STYLE}
    >
      <div className='bg-muted-foreground/10 group-hover:bg-primary/40 h-full w-0.5 rounded-full transition-all' />
      <div className='bg-primary/0 group-hover:bg-primary/60 absolute top-1/2 left-1/2 h-8 w-1 -translate-x-1/2 -translate-y-1/2 rounded-full opacity-0 transition-all group-hover:opacity-100' />
      <Button
        size='icon'
        variant='ghost'
        onClick={handleToggleClick}
        onMouseDown={handleToggleMouseDown}
        className={cn(
          'absolute top-1/2 -translate-y-1/2 -left-3 h-6 w-6 rounded-full shadow-md transition-all duration-150 z-10',
          'bg-background/70 backdrop-blur-md hover:bg-primary hover:text-primary-foreground',
          'border border-white/20 hover:border-primary',
        )}
        aria-label='Collapse chat'
      >
        <ChevronRight className='h-3 w-3' />
      </Button>
    </div>
  );
};

const SidebarPanel = ({
  isResizing,
  width,
  onToggleCollapse,
}: {
  isResizing: boolean;
  width: number;
  onToggleCollapse: () => void;
}) => {
  const animation = useMemo(
    () => ({
      opacity: 1,
      width: `${width}px`,
    }),
    [width],
  );

  const transition = useMemo(
    () =>
      isResizing ? { duration: 0, type: 'tween' } : { damping: 25, stiffness: 300, type: 'spring' },
    [isResizing],
  );

  const style = useMemo(
    () =>
      ({
        maxWidth: `${width}px`,
        minWidth: `${width}px`,
        width: `${width}px`,
      }) as const,
    [width],
  );

  return (
    <motion.div
      initial={false}
      animate={animation}
      transition={transition}
      className='bg-card/60 relative flex h-full min-w-0 shrink-0 flex-col overflow-hidden border-l border-white/10 backdrop-blur-xl'
      style={style}
    >
      <ChatPanel
        onClose={noop}
        onToggleMode={onToggleCollapse}
        mode='sidebar'
        className='h-full flex-1 rounded-none border-0'
      />
    </motion.div>
  );
};

const CollapsedBubble = ({ onToggle }: { onToggle: () => void }) => (
  <motion.div
    initial={COLLAPSED_INITIAL}
    animate={COLLAPSED_ANIMATION}
    exit={COLLAPSED_EXIT}
    transition={COLLAPSED_TRANSITION}
    className='fixed right-6 bottom-6 z-50'
  >
    <Button
      size='icon'
      onClick={onToggle}
      className={cn(
        'h-14 w-14 rounded-full shadow-2xl transition-all duration-200',
        'bg-primary hover:bg-primary/90 text-primary-foreground',
        'hover:scale-110 active:scale-95',
        'border-0',
      )}
      aria-label='Open chat'
    >
      <MessageCircle className='h-6 w-6' />
    </Button>
  </motion.div>
);

export const ChatBubble = () => {
  const { sidebarWidth, setSidebarWidth } = useChatStore();
  const [isResizing, setIsResizing] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(readCollapsedState);

  const handleSidebarResize = useCallback(
    (event: ReactMouseEvent<HTMLDivElement>) => {
      event.preventDefault();
      event.stopPropagation();
      setIsResizing(true);
      const startX = event.clientX;
      const startWidth = sidebarWidth;

      document.body.style.userSelect = 'none';
      document.body.style.cursor = RESIZE_CURSOR;

      const handleMouseMove = (moveEvent: globalThis.MouseEvent) => {
        moveEvent.preventDefault();
        const delta = startX - moveEvent.clientX;
        const nextWidth = Math.max(
          MIN_SIDEBAR_WIDTH,
          Math.min(MAX_SIDEBAR_WIDTH, startWidth + delta),
        );
        setSidebarWidth(nextWidth);
        writeSidebarWidth(nextWidth);
      };

      const handleMouseUp = () => {
        setIsResizing(false);
        document.body.style.userSelect = '';
        document.body.style.cursor = '';
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };

      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    },
    [sidebarWidth, setSidebarWidth],
  );

  const handleToggleCollapse = useCallback(() => {
    setIsCollapsed((prev) => {
      const next = !prev;
      writeCollapsedState(next);
      return next;
    });
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.shiftKey && event.key === 'k') {
        event.preventDefault();
        handleToggleCollapse();
      }
    };

    globalThis.addEventListener('keydown', handleKeyDown);
    return () => {
      globalThis.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleToggleCollapse]);

  return !isCollapsed ? (
    <div className='relative flex h-full shrink-0'>
      <SidebarResizeHandle
        isResizing={isResizing}
        onMouseDown={handleSidebarResize}
        onToggleCollapse={handleToggleCollapse}
      />
      <SidebarPanel
        isResizing={isResizing}
        width={sidebarWidth}
        onToggleCollapse={handleToggleCollapse}
      />
    </div>
  ) : (
    <CollapsedBubble onToggle={handleToggleCollapse} />
  );
};
