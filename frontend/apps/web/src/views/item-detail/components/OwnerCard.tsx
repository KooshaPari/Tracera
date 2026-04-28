import type { ChangeEvent } from 'react';

import { User } from 'lucide-react';
import { useCallback } from 'react';

import { Card, Input } from '@tracertm/ui';

interface OwnerCardProps {
  isEditing: boolean;
  owner: string;
  onChangeOwner: (value: string) => void;
}

export function OwnerCard({ isEditing, onChangeOwner, owner }: OwnerCardProps): JSX.Element {
  const handleChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>): void => {
      onChangeOwner(event.target.value);
    },
    [onChangeOwner],
  );

  const trimmedOwner = owner.trim();
  let content: JSX.Element = <span className='text-xs font-bold'>Unassigned</span>;
  if (trimmedOwner.length > 0) {
    content = <span className='text-xs font-bold'>{owner}</span>;
  }
  if (isEditing) {
    content = (
      <Input
        value={owner}
        onChange={handleChange}
        placeholder='Owner name'
        className='h-8 text-xs'
      />
    );
  }

  return (
    <Card className='bg-muted/40 border-0 px-4 py-3'>
      <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
        Owner
      </p>
      <div className='mt-2 flex items-center gap-2'>
        <div className='bg-primary/10 flex h-7 w-7 items-center justify-center rounded-full'>
          <User className='text-primary h-3 w-3' />
        </div>
        {content}
      </div>
    </Card>
  );
}
