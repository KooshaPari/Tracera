import type { ReactElement } from 'react';

export default function PageHeader(): ReactElement {
  return (
    <div className='mb-6'>
      <h1 className='text-2xl font-bold text-gray-900 dark:text-white'>External Integrations</h1>
      <p className='text-gray-600 dark:text-gray-400'>
        Connect GitHub, GitHub Projects, and Linear to sync items bidirectionally.
      </p>
    </div>
  );
}
