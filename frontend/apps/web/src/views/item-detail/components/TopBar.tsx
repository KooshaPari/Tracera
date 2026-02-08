import { ChevronRight, Edit3, ExternalLink, MoreVertical, Trash2, X } from 'lucide-react';

import { Button, DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, Separator } from '@tracertm/ui';

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

interface EditingActionsProps {
  onCancelEdit: () => void;
  onSave: () => void;
}

function EditingActions({ onCancelEdit, onSave }: EditingActionsProps): JSX.Element {
  return (
    <>
      <Button size='sm' className='gap-2 rounded-full' onClick={onSave}>
        <ChevronRight className='h-4 w-4' />
        Save
      </Button>
      <Button variant='outline' size='sm' className='gap-2 rounded-full' onClick={onCancelEdit}>
        <X className='h-4 w-4' />
        Cancel
      </Button>
    </>
  );
}

interface ViewActionsProps {
  onStartEdit: () => void;
}

function ViewActions({ onStartEdit }: ViewActionsProps): JSX.Element {
  return (
    <Button variant='outline' size='sm' className='gap-2 rounded-full' onClick={onStartEdit}>
      <Edit3 className='h-3.5 w-3.5' />
      Edit
    </Button>
  );
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
  let editActions: JSX.Element;
  if (isEditing) {
    editActions = <EditingActions onSave={onSave} onCancelEdit={onCancelEdit} />;
  } else {
    editActions = <ViewActions onStartEdit={onStartEdit} />;
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
