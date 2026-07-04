import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowRight, X } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

const linkTypes = [
  'implements',
  'tests',
  'depends_on',
  'related_to',
  'blocks',
  'parent_of',
] as const;

const linkSchema = z.object({
  description: z.string().max(1000).optional(),
  sourceId: z.string().uuid('Select a source item'),
  targetId: z.string().uuid('Select a target item'),
  type: z.enum(linkTypes),
});

type LinkFormData = z.infer<typeof linkSchema>;

interface Item {
  id: string;
  title: string;
  view: string;
  type: string;
}

interface CreateLinkFormProps {
  onSubmit: (data: LinkFormData) => void;
  onCancel: () => void;
  items: Item[];
  isLoading?: boolean;
  preselectedSource?: string;
}

export function CreateLinkForm({
  onSubmit,
  onCancel,
  items,
  isLoading,
  preselectedSource,
}: CreateLinkFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<LinkFormData>({
    defaultValues: { sourceId: preselectedSource ?? '', type: 'implements' },
    resolver: zodResolver(linkSchema),
  });

  const sourceId = watch('sourceId');
  const targetId = watch('targetId');
  const sourceItem = items.find((i) => i.id === sourceId);
  const targetItem = items.find((i) => i.id === targetId);

  const groupedItems = items.reduce<Record<string, Item[]>>((acc: Record<string, Item[]>, item) => {
    acc[item.view] ??= [];
    acc[item.view]?.push(item);
    return acc;
  }, {});

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      <div className='fixed inset-0 bg-black/50 backdrop-blur-sm' onClick={onCancel} />
      <div className='bg-background relative w-full max-w-lg rounded-xl border p-6 shadow-2xl'>
        <div className='flex items-center justify-between'>
          <h2 className='text-lg font-semibold'>Create Traceability Link</h2>
          <button onClick={onCancel} className='hover:bg-accent rounded-lg p-1'>
            <X className='h-5 w-5' />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className='mt-6 space-y-4'>
          <div className='flex items-center gap-4'>
            <div className='flex-1'>
              <label className='block text-sm font-medium'>
                Source Item <span className='text-red-500'>*</span>
              </label>
              <select
                {...register('sourceId')}
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              >
                <option value=''>Select source...</option>
                {Object.entries(groupedItems).map(([view, viewItems]) => (
                  <optgroup key={view} label={view}>
                    {viewItems.map((i) => (
                      <option key={i.id} value={i.id}>
                        [{i.type}] {i.title}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
              {errors.sourceId && (
                <p className='mt-1 text-sm text-red-500'>{errors.sourceId.message}</p>
              )}
            </div>
            <ArrowRight className='text-muted-foreground mt-6 h-5 w-5' />
            <div className='flex-1'>
              <label className='block text-sm font-medium'>
                Target Item <span className='text-red-500'>*</span>
              </label>
              <select
                {...register('targetId')}
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              >
                <option value=''>Select target...</option>
                {Object.entries(groupedItems).map(([view, viewItems]) => (
                  <optgroup key={view} label={view}>
                    {viewItems
                      .filter((i) => i.id !== sourceId)
                      .map((i) => (
                        <option key={i.id} value={i.id}>
                          [{i.type}] {i.title}
                        </option>
                      ))}
                  </optgroup>
                ))}
              </select>
              {errors.targetId && (
                <p className='mt-1 text-sm text-red-500'>{errors.targetId.message}</p>
              )}
            </div>
          </div>

          {sourceItem && targetItem && (
            <div className='bg-muted/30 rounded-lg border p-3 text-sm'>
              <span className='font-medium'>{sourceItem.title}</span>
              <span className='text-muted-foreground mx-2'>→</span>
              <span className='font-medium'>{targetItem.title}</span>
            </div>
          )}

          <div>
            <label className='block text-sm font-medium'>
              Link Type <span className='text-red-500'>*</span>
            </label>
            <select
              {...register('type')}
              className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
            >
              {linkTypes.map((t) => (
                <option key={t} value={t}>
                  {t.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className='block text-sm font-medium'>Description</label>
            <textarea
              {...register('description')}
              rows={2}
              placeholder='Why are these items linked?'
              className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
            />
          </div>

          <div className='flex gap-3 pt-4'>
            <button
              type='button'
              onClick={onCancel}
              className='hover:bg-accent flex-1 rounded-lg border px-4 py-2'
            >
              Cancel
            </button>
            <button
              type='submit'
              disabled={isLoading}
              className='bg-primary text-primary-foreground flex-1 rounded-lg px-4 py-2 disabled:opacity-50'
            >
              {isLoading ? 'Creating...' : 'Create Link'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
