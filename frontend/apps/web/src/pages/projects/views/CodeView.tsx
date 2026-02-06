import { FileCode, Folder } from 'lucide-react';

const modules = [
  {
    files: ['main.tsx', 'App.tsx', 'index.css'],
    id: '1',
    name: 'apps/web',
    type: 'module',
  },
  {
    files: ['main.ts', 'preload.ts'],
    id: '2',
    name: 'apps/desktop',
    type: 'module',
  },
  {
    files: ['Button.tsx', 'Dialog.tsx', 'index.ts'],
    id: '3',
    name: 'packages/ui',
    type: 'module',
  },
  {
    files: ['stores.ts', 'sync.ts'],
    id: '4',
    name: 'packages/state',
    type: 'module',
  },
];

export function CodeView() {
  return (
    <div className='space-y-4'>
      <h3 className='text-lg font-semibold'>Code View</h3>
      <div className='grid gap-4 md:grid-cols-2'>
        {modules.map((mod) => (
          <div key={mod.id} className='rounded-lg border p-4'>
            <div className='flex items-center gap-2'>
              <Folder className='h-5 w-5 text-yellow-500' />
              <span className='font-medium'>{mod.name}</span>
            </div>
            <div className='mt-3 space-y-1 pl-7'>
              {mod.files.map((file) => (
                <div key={file} className='text-muted-foreground flex items-center gap-2 text-sm'>
                  <FileCode className='h-4 w-4' />
                  {file}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
