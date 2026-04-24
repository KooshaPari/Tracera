import { XCircle } from 'lucide-react';

import { Button } from '@tracertm/ui';

interface NotFoundViewProps {
  message?: string | undefined;
  onBack: () => void;
}

export function NotFoundView({ message, onBack }: NotFoundViewProps): JSX.Element {
  let detail: JSX.Element = <span className='hidden' />;
  if (message !== undefined) {
    detail = <p className='text-muted-foreground text-sm'>{message}</p>;
  }

  return (
    <div className='flex flex-col items-center justify-center space-y-4 p-20'>
      <XCircle className='text-destructive h-12 w-12 opacity-20' />
      <h2 className='text-xl font-bold'>Item Not Found</h2>
      {detail}
      <Button variant='outline' onClick={onBack}>
        Return to Items
      </Button>
    </div>
  );
}
