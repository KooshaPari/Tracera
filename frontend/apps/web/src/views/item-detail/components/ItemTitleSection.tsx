import type { ChangeEvent } from 'react';

import { useCallback } from 'react';

import { Input, Textarea } from '@tracertm/ui';

const TITLE_STYLE = {
  fontFamily: '"Space Grotesk","Sora","IBM Plex Sans",sans-serif',
} as const;

interface ItemTitleSectionProps {
  isEditing: boolean;
  subtitle: string;
  title: string;
  description: string;
  onChangeTitle: (value: string) => void;
  onChangeDescription: (value: string) => void;
}

export function ItemTitleSection({
  description,
  isEditing,
  onChangeDescription,
  onChangeTitle,
  subtitle,
  title,
}: ItemTitleSectionProps): JSX.Element {
  const handleTitleChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>): void => {
      onChangeTitle(event.target.value);
    },
    [onChangeTitle],
  );
  const handleDescriptionChange = useCallback(
    (event: ChangeEvent<HTMLTextAreaElement>): void => {
      onChangeDescription(event.target.value);
    },
    [onChangeDescription],
  );

  if (!isEditing) {
    return (
      <>
        <p className='text-muted-foreground mb-1 text-sm font-semibold tracking-widest uppercase'>
          {subtitle}
        </p>
        <h1
          className='text-4xl leading-tight font-black tracking-tight md:text-5xl'
          style={TITLE_STYLE}
        >
          {title}
        </h1>
        <p className='text-muted-foreground text-lg leading-relaxed'>{description}</p>
      </>
    );
  }

  return (
    <div className='space-y-3'>
      <Input
        value={title}
        onChange={handleTitleChange}
        placeholder='Item title'
        className='h-12 text-2xl font-black'
      />
      <Textarea
        value={description}
        onChange={handleDescriptionChange}
        placeholder='Describe the item...'
        className='min-h-[120px]'
      />
    </div>
  );
}
