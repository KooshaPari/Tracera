import { AnimatePresence, motion } from 'framer-motion';
import { AlertCircle, Plus, Save, Trash2, X } from 'lucide-react';
import { useState } from 'react';

import type {
  Contract,
  ContractCondition,
  ContractTransition,
  ContractType,
} from '@tracertm/types';

import {
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
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  Textarea,
} from '@tracertm/ui';

interface ContractEditorProps {
  initialData?: Partial<Contract>;
  onSave: (data: Partial<Contract>) => Promise<void>;
  onCancel: () => void;
}

const contractTypes: ContractType[] = ['api', 'function', 'invariant', 'data', 'integration'];

export function ContractEditor({ initialData, onSave, onCancel }: ContractEditorProps) {
  const [formData, setFormData] = useState<Partial<Contract>>({
    title: '',
    contractType: 'function',
    status: 'draft',
    preconditions: [],
    postconditions: [],
    invariants: [],
    states: [],
    transitions: [],
    specLanguage: 'typescript',
    ...initialData,
  });
  const [isSaving, setIsSaving] = useState(false);
  const [newCondition, setNewCondition] = useState<Partial<ContractCondition>>({
    description: '',
    expression: '',
    isRequired: true,
  });
  const [newTransition, setNewTransition] = useState<Partial<ContractTransition>>({
    actions: [],
    fromState: '',
    guards: [],
    toState: '',
    trigger: '',
  });
  const [newState, setNewState] = useState('');

  const handleChange = (field: keyof Contract, value: Contract[typeof field]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const addCondition = (type: 'preconditions' | 'postconditions' | 'invariants') => {
    if (!newCondition.description?.trim()) {
      return;
    }

    const condition = {
      description: newCondition.description,
      expression: newCondition.expression,
      id: `cond_${Date.now()}`,
      isRequired: newCondition.isRequired ?? true,
    } as ContractCondition;

    setFormData((prev) => ({
      ...prev,
      [type]: [...(prev[type] ?? []), condition],
    }));

    setNewCondition({ description: '', expression: '', isRequired: true });
  };

  const removeCondition = (type: 'preconditions' | 'postconditions' | 'invariants', id: string) => {
    setFormData((prev) => ({
      ...prev,
      [type]: prev[type]?.filter((c) => c.id !== id) ?? [],
    }));
  };

  const addState = () => {
    if (!newState.trim()) {
      return;
    }

    setFormData((prev) => ({
      ...prev,
      states: [...(prev.states ?? []), newState],
    }));

    setNewState('');
  };

  const removeState = (state: string) => {
    setFormData((prev) => ({
      ...prev,
      states: prev.states?.filter((s) => s !== state) ?? [],
    }));
  };

  const addTransition = () => {
    if (!newTransition.fromState || !newTransition.toState || !newTransition.trigger) {
      return;
    }

    const transition = {
      actions: newTransition.actions,
      fromState: newTransition.fromState,
      guards: newTransition.guards,
      id: `trans_${Date.now()}`,
      toState: newTransition.toState,
      trigger: newTransition.trigger,
    } as ContractTransition;

    setFormData((prev) => ({
      ...prev,
      transitions: [...(prev.transitions ?? []), transition],
    }));

    setNewTransition({
      actions: [],
      fromState: '',
      guards: [],
      toState: '',
      trigger: '',
    });
  };

  const removeTransition = (id: string) => {
    setFormData((prev) => ({
      ...prev,
      transitions: prev.transitions?.filter((t) => t.id !== id) ?? [],
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
    <Card className='mx-auto w-full max-w-6xl'>
      <form onSubmit={handleSubmit}>
        <CardHeader>
          <CardTitle>{initialData?.id ? 'Edit Contract' : 'Create New Contract'}</CardTitle>
          <CardDescription>
            Define a design-by-contract specification with preconditions, postconditions, and
            invariants.
          </CardDescription>
        </CardHeader>

        <CardContent className='space-y-6'>
          {/* Basic Information */}
          <div className='grid grid-cols-1 gap-4 md:grid-cols-2'>
            <div className='space-y-2'>
              <Label htmlFor='title'>Contract Title</Label>
              <Input
                id='title'
                placeholder='e.g., Array Sort Function Contract'
                value={formData.title}
                onChange={(e) => {
                  handleChange('title', e.target.value);
                }}
                required
              />
            </div>
            <div className='space-y-2'>
              <Label htmlFor='contractType'>Contract Type</Label>
              <Select
                value={formData.contractType ?? 'function'}
                onValueChange={(value) => {
                  handleChange('contractType', value as ContractType);
                }}
              >
                <SelectTrigger id='contractType'>
                  <SelectValue placeholder='Select type' />
                </SelectTrigger>
                <SelectContent>
                  {contractTypes.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className='space-y-2'>
            <Label htmlFor='description'>Description</Label>
            <Textarea
              id='description'
              placeholder='Describe what this contract specifies...'
              className='min-h-[80px]'
              value={formData.description}
              onChange={(e) => {
                handleChange('description', e.target.value);
              }}
            />
          </div>

          {/* Conditions Tabs */}
          <Tabs defaultValue='preconditions' className='w-full'>
            <TabsList className='grid w-full grid-cols-3'>
              <TabsTrigger value='preconditions'>
                Preconditions ({formData.preconditions?.length ?? 0})
              </TabsTrigger>
              <TabsTrigger value='postconditions'>
                Postconditions ({formData.postconditions?.length ?? 0})
              </TabsTrigger>
              <TabsTrigger value='invariants'>
                Invariants ({formData.invariants?.length ?? 0})
              </TabsTrigger>
            </TabsList>

            {['preconditions', 'postconditions', 'invariants'].map((conditionType) => (
              <TabsContent key={conditionType} value={conditionType} className='mt-4 space-y-4'>
                {/* Existing Conditions */}
                <div className='space-y-2'>
                  <h4 className='text-sm font-semibold'>Existing Conditions</h4>
                  <AnimatePresence mode='popLayout'>
                    {(formData[conditionType as keyof Contract] as ContractCondition[])?.map(
                      (condition) => (
                        <motion.div
                          key={condition.id}
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          className='bg-muted space-y-2 rounded-lg border p-3'
                        >
                          <div className='flex items-start justify-between'>
                            <p className='text-sm font-medium'>{condition.description}</p>
                            <Button
                              type='button'
                              variant='ghost'
                              size='sm'
                              onClick={() => {
                                removeCondition(
                                  conditionType as
                                    | 'preconditions'
                                    | 'postconditions'
                                    | 'invariants',
                                  condition.id,
                                );
                              }}
                            >
                              <Trash2 className='text-destructive h-4 w-4' />
                            </Button>
                          </div>
                          {condition.expression && (
                            <code className='bg-background block rounded border p-2 font-mono text-xs'>
                              {condition.expression}
                            </code>
                          )}
                          <div className='flex items-center gap-2'>
                            {!condition.isRequired && (
                              <span className='rounded bg-yellow-500/10 px-2 py-1 text-xs text-yellow-600'>
                                Optional
                              </span>
                            )}
                          </div>
                        </motion.div>
                      ),
                    )}
                  </AnimatePresence>
                </div>

                {/* Add New Condition */}
                <div className='space-y-3 border-t pt-4'>
                  <h4 className='text-sm font-semibold'>Add New Condition</h4>
                  <div className='space-y-2'>
                    <Label>Description</Label>
                    <Input
                      placeholder='Describe this condition...'
                      value={newCondition.description}
                      onChange={(e) => {
                        setNewCondition((prev) => ({
                          ...prev,
                          description: e.target.value,
                        }));
                      }}
                    />
                  </div>
                  <div className='space-y-2'>
                    <Label>Expression (optional)</Label>
                    <Textarea
                      placeholder="e.g., array.length > 0 && typeof array[0] === 'number'"
                      className='min-h-[60px] font-mono text-xs'
                      value={newCondition.expression}
                      onChange={(e) => {
                        setNewCondition((prev) => ({
                          ...prev,
                          expression: e.target.value,
                        }));
                      }}
                    />
                  </div>
                  <div className='flex items-center gap-2'>
                    <input
                      type='checkbox'
                      id='isRequired'
                      checked={newCondition.isRequired ?? true}
                      onChange={(e) => {
                        setNewCondition((prev) => ({
                          ...prev,
                          isRequired: e.target.checked,
                        }));
                      }}
                    />
                    <Label htmlFor='isRequired' className='font-normal'>
                      Required
                    </Label>
                  </div>
                  <Button
                    type='button'
                    size='sm'
                    variant='outline'
                    onClick={() => {
                      addCondition(
                        conditionType as 'preconditions' | 'postconditions' | 'invariants',
                      );
                    }}
                  >
                    <Plus className='mr-2 h-4 w-4' />
                    Add Condition
                  </Button>
                </div>
              </TabsContent>
            ))}
          </Tabs>

          {/* State Machine */}
          <Tabs defaultValue='states' className='w-full'>
            <TabsList className='grid w-full grid-cols-2'>
              <TabsTrigger value='states'>States ({formData.states?.length ?? 0})</TabsTrigger>
              <TabsTrigger value='transitions'>
                Transitions ({formData.transitions?.length ?? 0})
              </TabsTrigger>
            </TabsList>

            <TabsContent value='states' className='mt-4 space-y-4'>
              {/* Existing States */}
              {formData.states && formData.states.length > 0 && (
                <div className='space-y-2'>
                  <h4 className='text-sm font-semibold'>Defined States</h4>
                  <div className='flex flex-wrap gap-2'>
                    <AnimatePresence mode='popLayout'>
                      {formData.states.map((state) => (
                        <motion.div
                          key={state}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.8 }}
                          className='bg-primary/10 text-primary flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium'
                        >
                          {state}
                          <button
                            type='button'
                            onClick={() => {
                              removeState(state);
                            }}
                            className='text-primary/60 hover:text-primary'
                          >
                            <X className='h-3 w-3' />
                          </button>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                </div>
              )}

              {/* Add New State */}
              <div className='space-y-2 border-t pt-4'>
                <Label>Add State</Label>
                <div className='flex gap-2'>
                  <Input
                    placeholder='e.g., Active, Pending, Closed'
                    value={newState}
                    onChange={(e) => {
                      setNewState(e.target.value);
                    }}
                  />
                  <Button type='button' size='sm' onClick={addState}>
                    <Plus className='mr-2 h-4 w-4' />
                    Add
                  </Button>
                </div>
              </div>
            </TabsContent>

            <TabsContent value='transitions' className='mt-4 space-y-4'>
              {/* Existing Transitions */}
              <div className='space-y-2'>
                <h4 className='text-sm font-semibold'>State Transitions</h4>
                <AnimatePresence mode='popLayout'>
                  {formData.transitions?.map((transition) => (
                    <motion.div
                      key={transition.id}
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className='bg-muted space-y-2 rounded-lg border p-3'
                    >
                      <div className='flex items-start justify-between'>
                        <div>
                          <p className='font-mono text-sm'>
                            {transition.fromState} → {transition.toState}
                          </p>
                          <p className='text-muted-foreground text-xs'>
                            Trigger: {transition.trigger}
                          </p>
                        </div>
                        <Button
                          type='button'
                          variant='ghost'
                          size='sm'
                          onClick={() => {
                            removeTransition(transition.id);
                          }}
                        >
                          <Trash2 className='text-destructive h-4 w-4' />
                        </Button>
                      </div>
                      {(transition.guards?.length ?? 0) > 0 && (
                        <div className='text-xs'>
                          <span className='font-semibold'>Guards:</span>{' '}
                          {transition.guards?.join(', ')}
                        </div>
                      )}
                      {(transition.actions?.length ?? 0) > 0 && (
                        <div className='text-xs'>
                          <span className='font-semibold'>Actions:</span>{' '}
                          {transition.actions?.join(', ')}
                        </div>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>

              {/* Add New Transition */}
              <div className='space-y-3 border-t pt-4'>
                <h4 className='text-sm font-semibold'>Add Transition</h4>
                <div className='grid grid-cols-2 gap-2'>
                  <div className='space-y-1'>
                    <Label className='text-xs'>From State</Label>
                    <Select
                      value={newTransition.fromState ?? ''}
                      onValueChange={(value) => {
                        setNewTransition((prev) => ({
                          ...prev,
                          fromState: value,
                        }));
                      }}
                    >
                      <SelectTrigger className='h-8'>
                        <SelectValue placeholder='Select' />
                      </SelectTrigger>
                      <SelectContent>
                        {formData.states?.map((state) => (
                          <SelectItem key={state} value={state}>
                            {state}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className='space-y-1'>
                    <Label className='text-xs'>To State</Label>
                    <Select
                      value={newTransition.toState ?? ''}
                      onValueChange={(value) => {
                        setNewTransition((prev) => ({
                          ...prev,
                          toState: value,
                        }));
                      }}
                    >
                      <SelectTrigger className='h-8'>
                        <SelectValue placeholder='Select' />
                      </SelectTrigger>
                      <SelectContent>
                        {formData.states?.map((state) => (
                          <SelectItem key={state} value={state}>
                            {state}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className='space-y-1'>
                  <Label className='text-xs'>Trigger Event</Label>
                  <Input
                    placeholder='e.g., submit, complete, cancel'
                    className='h-8'
                    value={newTransition.trigger ?? ''}
                    onChange={(e) => {
                      setNewTransition((prev) => ({
                        ...prev,
                        trigger: e.target.value,
                      }));
                    }}
                  />
                </div>
                <Button
                  type='button'
                  size='sm'
                  variant='outline'
                  onClick={addTransition}
                  disabled={
                    !newTransition.fromState || !newTransition.toState || !newTransition.trigger
                  }
                >
                  <Plus className='mr-2 h-4 w-4' />
                  Add Transition
                </Button>
              </div>
            </TabsContent>
          </Tabs>

          {/* Executable Specification */}
          <div className='space-y-2'>
            <div className='flex items-center gap-2'>
              <Label htmlFor='specLanguage'>Executable Specification Language</Label>
              <AlertCircle className='text-muted-foreground h-4 w-4' />
            </div>
            <Select
              value={formData.specLanguage ?? 'typescript'}
              onValueChange={(value) => {
                handleChange('specLanguage', value as 'typescript' | 'python' | 'gherkin');
              }}
            >
              <SelectTrigger id='specLanguage'>
                <SelectValue placeholder='Select language' />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='typescript'>TypeScript</SelectItem>
                <SelectItem value='python'>Python</SelectItem>
                <SelectItem value='gherkin'>Gherkin</SelectItem>
              </SelectContent>
            </Select>
            <Textarea
              placeholder='// Executable specification code for contract verification...'
              className='min-h-[200px] font-mono text-xs'
              value={formData.executableSpec}
              onChange={(e) => {
                handleChange('executableSpec', e.target.value);
              }}
            />
            <p className='text-muted-foreground text-xs'>
              Code that can be executed to verify contract compliance during testing.
            </p>
          </div>
        </CardContent>

        <CardFooter className='flex justify-end gap-2'>
          <Button type='button' variant='outline' onClick={onCancel} disabled={isSaving}>
            <X className='mr-2 h-4 w-4' />
            Cancel
          </Button>
          <Button type='submit' disabled={isSaving}>
            <Save className='mr-2 h-4 w-4' />
            {isSaving ? 'Saving...' : 'Save Contract'}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
