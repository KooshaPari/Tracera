import { ChevronRight, X } from 'lucide-react';

import { Button } from '@tracertm/ui';

interface TopBarEditingActionsProps {
  onCancelEdit: () => void;
  onSave: () => void;
}

export function TopBarEditingActions({
  onCancelEdit,
  onSave,
}: TopBarEditingActionsProps): JSX.Element {
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
