import { Edit3 } from 'lucide-react';

import { Button } from '@tracertm/ui';

interface TopBarViewActionsProps {
  onStartEdit: () => void;
}

export function TopBarViewActions({ onStartEdit }: TopBarViewActionsProps): JSX.Element {
  return (
    <Button variant='outline' size='sm' className='gap-2 rounded-full' onClick={onStartEdit}>
      <Edit3 className='h-3.5 w-3.5' />
      Edit
    </Button>
  );
}
