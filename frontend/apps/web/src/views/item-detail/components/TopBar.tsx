import { ChevronRight, ExternalLink, MoreVertical, Trash2 } from 'lucide-react';

import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  Separator,
} from '@tracertm/ui';

import { TopBarEditingActions } from './TopBarEditingActions';
import { TopBarViewActions } from './TopBarViewActions';

interface TopBarProps {
  isEditing: boolean;
  onBack: () => void;
  onStartEdit: () => void;
  onCancelEdit: () => void;
  onSave: () => void;
  onDelete: () => void;
  onShare: () => void;
  onOpenNewTab: () => void;
}

export function TopBar({
  isEditing,
  onBack,
  onCancelEdit,
  onDelete,
  onOpenNewTab,
  onSave,
  onShare,
  onStartEdit,
}: TopBarProps): JSX.Element {
  let editActions: JSX.Element = <TopBarViewActions onStartEdit={onStartEdit} />;
  if (isEditing) {
    editActions = <TopBarEditingActions onSave={onSave} onCancelEdit={onCancelEdit} />;
  }

  return (
    <header className='border-border/50 shrink-0 border-b pb-6'>
      <div className='flex items-center justify-between'>
        <Button
          variant='ghost'
          size='sm'
          onClick={onBack}
          className='text-muted-foreground hover:text-foreground gap-2'
        >
          <ChevronRight className='h-4 w-4 rotate-180' />
          Back
        </Button>
        <div className='flex items-center gap-2'>
          <Button variant='outline' size='sm' className='gap-2 rounded-full' onClick={onShare}>
            <ExternalLink className='h-3.5 w-3.5' />
            Share
          </Button>
          {editActions}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <span>
                <Button variant='ghost' size='icon' className='rounded-full'>
                  <MoreVertical className='h-4 w-4' />
                </Button>
              </span>
            </DropdownMenuTrigger>
            <DropdownMenuContent align='end' className='w-48'>
              <DropdownMenuItem
                className='hover:bg-accent hover:text-accent-foreground cursor-pointer gap-2 transition-colors'
                onClick={onOpenNewTab}
              >
                <ChevronRight className='h-4 w-4' /> Open in New Tab
              </DropdownMenuItem>
              <Separator className='my-1' />
              <DropdownMenuItem
                className='text-destructive focus:text-destructive focus:bg-destructive/10 hover:bg-destructive/10 hover:text-destructive cursor-pointer gap-2 transition-colors'
                onClick={onDelete}
              >
                <Trash2 className='h-4 w-4' /> Delete Item
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
