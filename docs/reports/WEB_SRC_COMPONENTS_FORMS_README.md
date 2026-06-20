# Form Components

Reusable form component abstractions for use with react-hook-form.

## Components

### FormField

Base wrapper component that provides consistent layout with label, error handling, and help text.

```tsx
import { FormField, FormInput } from '@/components/forms';

<FormField
  label='Username'
  htmlFor='username'
  error={errors.username?.message}
  helpText='Enter your unique username'
  required
>
  <FormInput {...register('username')} error={!!errors.username} />
</FormField>;
```

### FormInput

Text input with error state styling.

```tsx
import { FormInput } from '@/components/forms';
import { useForm } from 'react-hook-form';

const {
  register,
  formState: { errors },
} = useForm();

<FormInput
  {...register('email')}
  type='email'
  placeholder='you@example.com'
  error={!!errors.email}
/>;
```

### FormSelect

Dropdown select with Radix UI Select component.

```tsx
import { FormSelect } from '@/components/forms';
import { Controller } from 'react-hook-form';

const options = [
  { label: 'Option 1', value: 'opt1' },
  { label: 'Option 2', value: 'opt2' },
];

<Controller
  name='preference'
  control={control}
  render={({ field }) => (
    <FormSelect
      value={field.value}
      onValueChange={field.onChange}
      options={options}
      error={!!errors.preference}
      placeholder='Select your preference'
    />
  )}
/>;
```

### FormTextarea

Multi-line textarea with error state styling.

```tsx
import { FormTextarea } from '@/components/forms';

<FormTextarea
  {...register('description')}
  rows={4}
  placeholder='Describe your issue...'
  error={!!errors.description}
/>;
```

### FormCheckbox

Boolean checkbox with optional label.

```tsx
import { FormCheckbox } from '@/components/forms';

<FormCheckbox
  {...register('acceptTerms')}
  label='I accept the terms and conditions'
  error={!!errors.acceptTerms}
/>;
```

### FormArrayField

Dynamic array manager with add/remove functionality using useFieldArray.

```tsx
import { FormArrayField, FormInput } from '@/components/forms';
import { useForm } from 'react-hook-form';

const { control } = useForm({
  defaultValues: {
    tags: [{ name: '' }],
  },
});

<FormArrayField
  control={control}
  name='tags'
  label='Tags'
  helpText='Add tags to categorize this item'
  addButtonLabel='Add Tag'
  defaultValue={{ name: '' }}
  minItems={1}
  maxItems={10}
  renderField={(index) => <FormInput {...register(`tags.${index}.name`)} placeholder='Tag name' />}
/>;
```

## Complete Form Example

```tsx
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  FormField,
  FormInput,
  FormSelect,
  FormTextarea,
  FormCheckbox,
  FormArrayField,
} from '@/components/forms';
import { Button } from '@tracertm/ui';

const formSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  category: z.string().min(1, 'Category is required'),
  description: z.string().optional(),
  isPublic: z.boolean(),
  tags: z.array(z.object({ name: z.string().min(1) })),
});

type FormData = z.infer<typeof formSchema>;

function MyForm() {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      isPublic: false,
      tags: [{ name: '' }],
    },
  });

  const onSubmit = (data: FormData) => {
    console.log(data);
  };

  const categoryOptions = [
    { label: 'Feature', value: 'feature' },
    { label: 'Bug', value: 'bug' },
    { label: 'Enhancement', value: 'enhancement' },
  ];

  return (
    <form onSubmit={handleSubmit(onSubmit)} className='space-y-4'>
      <FormField label='Title' htmlFor='title' error={errors.title?.message} required>
        <FormInput {...register('title')} placeholder='Enter title' error={!!errors.title} />
      </FormField>

      <FormField label='Category' htmlFor='category' error={errors.category?.message} required>
        <Controller
          name='category'
          control={control}
          render={({ field }) => (
            <FormSelect
              value={field.value}
              onValueChange={field.onChange}
              options={categoryOptions}
              error={!!errors.category}
            />
          )}
        />
      </FormField>

      <FormField
        label='Description'
        htmlFor='description'
        helpText='Optional details about this item'
      >
        <FormTextarea {...register('description')} rows={3} placeholder='Describe...' />
      </FormField>

      <FormCheckbox {...register('isPublic')} label='Make this public' />

      <FormArrayField
        control={control}
        name='tags'
        label='Tags'
        addButtonLabel='Add Tag'
        defaultValue={{ name: '' }}
        renderField={(index) => (
          <FormInput {...register(`tags.${index}.name`)} placeholder='Tag name' />
        )}
      />

      <Button type='submit'>Submit</Button>
    </form>
  );
}
```

## Accessibility Features

All form components include:

- Proper ARIA attributes (aria-describedby, aria-invalid, aria-required)
- Screen reader announcements for errors
- Keyboard navigation support
- Focus management
- Error state indicators (visual + semantic)

## Styling

Components use Tailwind CSS with Class Variance Authority (CVA) for consistent styling:

- Error states: Red border and error message
- Help text: Muted color and smaller font
- Required fields: Red asterisk with aria-label
- Focus states: Ring outline for keyboard navigation
