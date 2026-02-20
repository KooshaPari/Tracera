import type { ChangeEvent } from 'react';

import { FileEdit, Link2, Tag } from 'lucide-react';
import { memo, useCallback, useState } from 'react';

import { Button } from '@tracertm/ui/components/Button';
import { Input } from '@tracertm/ui/components/Input';
import { Label } from '@tracertm/ui/components/Label';
import { Popover, PopoverContent, PopoverTrigger } from '@tracertm/ui/components/Popover';

interface NodeQuickActionsProps {
  nodeId: string;
  onAddLink: (nodeId: string, targetId: string) => void;
  onAddTag: (nodeId: string, tag: string) => void;
  onEditNote: (nodeId: string, note: string) => void;
}

interface ActionPopoverProps {
  buttonLabel: string;
  buttonTitle: string;
  children: React.ReactNode;
  icon: React.ReactNode;
}

const ActionPopover = ({ buttonLabel, buttonTitle, children, icon }: ActionPopoverProps) => (
  <Popover>
    <PopoverTrigger asChild>
      <Button
        size='sm'
        variant='ghost'
        className='h-6 w-6 p-0'
        aria-label={buttonLabel}
        title={buttonTitle}
      >
        {icon}
      </Button>
    </PopoverTrigger>
    <PopoverContent className='w-64'>{children}</PopoverContent>
  </Popover>
);

interface ActionInputProps {
  buttonLabel: string;
  buttonTitle: string;
  icon: React.ReactNode;
  inputId: string;
  inputLabel: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
  onConfirm: () => void;
}

const ActionInput = ({
  buttonLabel,
  buttonTitle,
  icon,
  inputId,
  inputLabel,
  placeholder,
  value,
  onChange,
  onConfirm,
}: ActionInputProps) => {
  const handleChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      onChange(event.target.value);
    },
    [onChange],
  );

  return (
    <ActionPopover buttonLabel={buttonLabel} buttonTitle={buttonTitle} icon={icon}>
      <div className='space-y-2'>
        <Label htmlFor={inputId}>{inputLabel}</Label>
        <div className='flex gap-2'>
          <Input
            id={inputId}
            placeholder={placeholder}
            value={value}
            onChange={handleChange}
            aria-label={inputLabel}
          />
          <Button size='sm' onClick={onConfirm} aria-label={buttonLabel}>
            Add
          </Button>
        </div>
      </div>
    </ActionPopover>
  );
};

interface NoteActionProps {
  note: string;
  onChange: (value: string) => void;
  onSave: () => void;
}

const NoteAction = ({ note, onChange, onSave }: NoteActionProps) => {
  const handleNoteChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      onChange(event.target.value);
    },
    [onChange],
  );

  return (
    <ActionPopover
      buttonLabel='Edit note for node'
      buttonTitle='Edit note for node'
      icon={<FileEdit className='h-3 w-3' aria-hidden='true' />}
    >
      <div className='space-y-2'>
        <Label htmlFor='note'>Quick note</Label>
        <div className='flex gap-2'>
          <Input
            id='note'
            placeholder='Add note...'
            value={note}
            onChange={handleNoteChange}
            aria-label='Quick note for node'
          />
          <Button size='sm' onClick={onSave} aria-label='Save node note'>
            Save
          </Button>
        </div>
      </div>
    </ActionPopover>
  );
};

const NodeQuickActions = memo(function NodeQuickActions({
  nodeId,
  onAddLink,
  onAddTag,
  onEditNote,
}: NodeQuickActionsProps) {
  const [linkTarget, setLinkTarget] = useState('');
  const [tag, setTag] = useState('');
  const [note, setNote] = useState('');

  const handleAddLink = useCallback(() => {
    onAddLink(nodeId, linkTarget);
    setLinkTarget('');
  }, [linkTarget, nodeId, onAddLink]);

  const handleAddTag = useCallback(() => {
    onAddTag(nodeId, tag);
    setTag('');
  }, [nodeId, onAddTag, tag]);

  const handleSaveNote = useCallback(() => {
    onEditNote(nodeId, note);
    setNote('');
  }, [nodeId, note, onEditNote]);

  return (
    <div className='flex gap-1' role='group' aria-label='Node quick actions'>
      <ActionInput
        buttonLabel='Add link to another node'
        buttonTitle='Add link to another node'
        icon={<Link2 className='h-3 w-3' aria-hidden='true' />}
        inputId='link-target'
        inputLabel='Link to node'
        placeholder='Node ID'
        value={linkTarget}
        onChange={setLinkTarget}
        onConfirm={handleAddLink}
      />
      <ActionInput
        buttonLabel='Add tag to node'
        buttonTitle='Add tag to node'
        icon={<Tag className='h-3 w-3' aria-hidden='true' />}
        inputId='tag'
        inputLabel='Add tag'
        placeholder='Tag name'
        value={tag}
        onChange={setTag}
        onConfirm={handleAddTag}
      />
      <NoteAction note={note} onChange={setNote} onSave={handleSaveNote} />
    </div>
  );
});

export { NodeQuickActions };
