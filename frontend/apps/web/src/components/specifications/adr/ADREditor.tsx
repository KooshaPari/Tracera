import { Plus, Save, Trash2, X } from 'lucide-react';
import { useState } from 'react';

import type { ADR, ADRStatus } from '@tracertm/types';

import {
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  Input,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
} from '@tracertm/ui';

interface ADREditorProps {
  initialData?: Partial<ADR>;
  onSave: (data: Partial<ADR>) => Promise<void>;
  onCancel: () => void;
  showDecisionDrivers?: boolean;
  showRelatedRequirements?: boolean;
}

export function ADREditor({
  initialData,
  onSave,
  onCancel,
  showDecisionDrivers = true,
  showRelatedRequirements = true,
}: ADREditorProps) {
  const [formData, setFormData] = useState<Partial<ADR>>({
    title: '',
    status: 'proposed',
    context: '',
    decision: '',
    consequences: '',
    decisionDrivers: [],
    consideredOptions: [],
    relatedRequirements: [],
    tags: [],
    ...initialData,
  });
  const [isSaving, setIsSaving] = useState(false);
  const [newDriver, setNewDriver] = useState('');
  const [newTag, setNewTag] = useState('');
  const [newRequirement, setNewRequirement] = useState('');

  const handleChange = (field: keyof ADR, value: ADR[typeof field]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const addDriver = () => {
    if (newDriver.trim()) {
      setFormData((prev) => ({
        ...prev,
        decisionDrivers: [...(prev.decisionDrivers ?? []), newDriver],
      }));
      setNewDriver('');
    }
  };

  const removeDriver = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      decisionDrivers: (prev.decisionDrivers ?? []).filter((_, i) => i !== index),
    }));
  };

  const addTag = () => {
    if (newTag.trim()) {
      setFormData((prev) => ({
        ...prev,
        tags: [...(prev.tags ?? []), newTag],
      }));
      setNewTag('');
    }
  };

  const removeTag = (tag: string) => {
    setFormData((prev) => ({
      ...prev,
      tags: (prev.tags ?? []).filter((t) => t !== tag),
    }));
  };

  const addRequirement = () => {
    if (newRequirement.trim()) {
      setFormData((prev) => ({
        ...prev,
        relatedRequirements: [...(prev.relatedRequirements ?? []), newRequirement],
      }));
      setNewRequirement('');
    }
  };

  const removeRequirement = (req: string) => {
    setFormData((prev) => ({
      ...prev,
      relatedRequirements: (prev.relatedRequirements ?? []).filter((r) => r !== req),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await onSave(formData);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card className='mx-auto w-full max-w-4xl'>
      <form onSubmit={handleSubmit}>
        <CardHeader>
          <CardTitle>{initialData?.id ? 'Edit ADR' : 'Create New ADR'}</CardTitle>
          <CardDescription>
            Record an architectural decision using the MADR 4.0 format.
          </CardDescription>
        </CardHeader>
        <CardContent className='space-y-6'>
          {/* Title and Status */}
          <div className='grid grid-cols-1 gap-4 md:grid-cols-2'>
            <div className='space-y-2'>
              <Label htmlFor='title'>Title</Label>
              <Input
                id='title'
                placeholder='e.g., Use PostgreSQL for primary storage'
                value={formData.title}
                onChange={(e) => {
                  handleChange('title', e.target.value);
                }}
                required
              />
            </div>
            <div className='space-y-2'>
              <Label htmlFor='status'>Status</Label>
              <Select
                value={formData.status ?? 'proposed'}
                onValueChange={(value) => {
                  handleChange('status', value as ADRStatus);
                }}
              >
                <SelectTrigger id='status'>
                  <SelectValue placeholder='Select status' />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='proposed'>Proposed</SelectItem>
                  <SelectItem value='accepted'>Accepted</SelectItem>
                  <SelectItem value='deprecated'>Deprecated</SelectItem>
                  <SelectItem value='superseded'>Superseded</SelectItem>
                  <SelectItem value='rejected'>Rejected</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* MADR Core Sections */}
          <div className='space-y-2'>
            <Label htmlFor='context'>Context</Label>
            <Textarea
              id='context'
              placeholder="What is the issue that we're seeing that is motivating this decision or change?"
              className='min-h-[100px]'
              value={formData.context}
              onChange={(e) => {
                handleChange('context', e.target.value);
              }}
              required
            />
            <p className='text-muted-foreground text-xs'>
              Describe the problem statement and decision drivers.
            </p>
          </div>

          <div className='space-y-2'>
            <Label htmlFor='decision'>Decision</Label>
            <Textarea
              id='decision'
              placeholder="What is the change that we're proposing and/or doing?"
              className='min-h-[100px]'
              value={formData.decision}
              onChange={(e) => {
                handleChange('decision', e.target.value);
              }}
              required
            />
            <p className='text-muted-foreground text-xs'>The outcome of the decision.</p>
          </div>

          <div className='space-y-2'>
            <Label htmlFor='consequences'>Consequences</Label>
            <Textarea
              id='consequences'
              placeholder='What becomes easier or more difficult to do because of this change?'
              className='min-h-[100px]'
              value={formData.consequences}
              onChange={(e) => {
                handleChange('consequences', e.target.value);
              }}
              required
            />
            <p className='text-muted-foreground text-xs'>Positive and negative implications.</p>
          </div>

          {/* Decision Drivers */}
          {showDecisionDrivers && (
            <div className='bg-muted/20 border-border space-y-2 rounded-lg border p-4'>
              <Label>Decision Drivers</Label>
              <div className='space-y-2'>
                {(formData.decisionDrivers ?? []).map((driver, idx) => (
                  <div
                    key={idx}
                    className='bg-background border-border/50 flex items-center justify-between gap-2 rounded border p-2'
                  >
                    <span className='text-sm'>{driver}</span>
                    <Button
                      type='button'
                      variant='ghost'
                      size='sm'
                      className='h-6 w-6 p-0'
                      onClick={() => {
                        removeDriver(idx);
                      }}
                    >
                      <Trash2 className='h-3 w-3' />
                    </Button>
                  </div>
                ))}
                <div className='flex gap-2'>
                  <Input
                    placeholder='Add a decision driver...'
                    value={newDriver}
                    onChange={(e) => {
                      setNewDriver(e.target.value);
                    }}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        addDriver();
                      }
                    }}
                    className='text-sm'
                  />
                  <Button
                    type='button'
                    variant='outline'
                    size='sm'
                    onClick={addDriver}
                    className='gap-1'
                  >
                    <Plus className='h-3 w-3' />
                    Add
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Related Requirements */}
          {showRelatedRequirements && (
            <div className='bg-muted/20 border-border space-y-2 rounded-lg border p-4'>
              <Label>Related Requirements</Label>
              <div className='space-y-2'>
                {(formData.relatedRequirements ?? []).map((req) => (
                  <Badge key={req} variant='secondary' className='flex w-fit items-center gap-1'>
                    {req}
                    <Button
                      type='button'
                      variant='ghost'
                      size='sm'
                      className='ml-1 h-4 w-4 p-0 hover:bg-transparent'
                      onClick={() => {
                        removeRequirement(req);
                      }}
                    >
                      <X className='h-3 w-3' />
                    </Button>
                  </Badge>
                ))}
                <div className='flex gap-2'>
                  <Input
                    placeholder='e.g., REQ-001'
                    value={newRequirement}
                    onChange={(e) => {
                      setNewRequirement(e.target.value);
                    }}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        addRequirement();
                      }
                    }}
                    className='text-sm'
                  />
                  <Button
                    type='button'
                    variant='outline'
                    size='sm'
                    onClick={addRequirement}
                    className='gap-1'
                  >
                    <Plus className='h-3 w-3' />
                    Link
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Tags */}
          <div className='bg-muted/20 border-border space-y-2 rounded-lg border p-4'>
            <Label>Tags</Label>
            <div className='space-y-2'>
              {(formData.tags ?? []).map((tag) => (
                <Badge key={tag} variant='outline' className='flex w-fit items-center gap-1'>
                  {tag}
                  <Button
                    type='button'
                    variant='ghost'
                    size='sm'
                    className='ml-1 h-4 w-4 p-0 hover:bg-transparent'
                    onClick={() => {
                      removeTag(tag);
                    }}
                  >
                    <X className='h-3 w-3' />
                  </Button>
                </Badge>
              ))}
              <div className='flex gap-2'>
                <Input
                  placeholder='Add a tag...'
                  value={newTag}
                  onChange={(e) => {
                    setNewTag(e.target.value);
                  }}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addTag();
                    }
                  }}
                  className='text-sm'
                />
                <Button
                  type='button'
                  variant='outline'
                  size='sm'
                  onClick={addTag}
                  className='gap-1'
                >
                  <Plus className='h-3 w-3' />
                  Add
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
        <CardFooter className='flex justify-end gap-2'>
          <Button type='button' variant='outline' onClick={onCancel} disabled={isSaving}>
            <X className='mr-2 h-4 w-4' />
            Cancel
          </Button>
          <Button type='submit' disabled={isSaving}>
            <Save className='mr-2 h-4 w-4' />
            {isSaving ? 'Saving...' : 'Save ADR'}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
