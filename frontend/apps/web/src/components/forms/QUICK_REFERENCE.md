# Form Components Quick Reference

## Import Statement
```tsx
import {
  FormField,
  FormInput,
  FormSelect,
  FormTextarea,
  FormCheckbox,
  FormArrayField,
} from "@/components/forms";
```

## Component Cheatsheet

### FormField - Wrapper for all form fields
```tsx
<FormField
  label="Field Label"
  htmlFor="fieldId"
  error={errors.field?.message}
  helpText="Optional help text"
  required
>
  {/* Your input component */}
</FormField>
```

### FormInput - Text input
```tsx
<FormInput
  {...register("fieldName")}
  placeholder="Enter text"
  error={!!errors.fieldName}
/>
```

### FormSelect - Dropdown
```tsx
<Controller
  name="fieldName"
  control={control}
  render={({ field }) => (
    <FormSelect
      value={field.value}
      onValueChange={field.onChange}
      options={[
        { label: "Option 1", value: "opt1" },
        { label: "Option 2", value: "opt2" },
      ]}
      placeholder="Select option"
      error={!!errors.fieldName}
    />
  )}
/>
```

### FormTextarea - Multi-line text
```tsx
<FormTextarea
  {...register("fieldName")}
  rows={4}
  placeholder="Enter description"
  error={!!errors.fieldName}
/>
```

### FormCheckbox - Boolean checkbox
```tsx
<FormCheckbox
  {...register("fieldName")}
  label="Check this option"
  error={!!errors.fieldName}
/>
```

### FormArrayField - Dynamic array
```tsx
<FormArrayField
  control={control}
  name="arrayField"
  label="Items"
  addButtonLabel="Add Item"
  defaultValue={{ name: "" }}
  minItems={1}
  maxItems={10}
  renderField={(index) => (
    <FormInput
      {...register(`arrayField.${index}.name`)}
      placeholder="Item name"
    />
  )}
/>
```

## Common Patterns

### Basic Form Setup
```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  field: z.string().min(1, "Required"),
});

const { register, control, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema),
});
```

### Error Handling
```tsx
// Show error message
error={errors.fieldName?.message}

// Show error styling
error={!!errors.fieldName}
```

### Required Fields
```tsx
<FormField required label="Required Field" htmlFor="field">
  <FormInput {...register("field")} />
</FormField>
```

## Accessibility Checklist

- ✅ All inputs have labels
- ✅ Error messages linked with aria-describedby
- ✅ Required fields marked with aria-required
- ✅ Invalid fields marked with aria-invalid
- ✅ Keyboard navigation supported
- ✅ Focus states visible

## TypeScript Tips

```tsx
// Define form schema
type FormData = z.infer<typeof schema>;

// Type-safe field names
register("fieldName") // auto-complete works!

// Type-safe options
const options: FormSelectOption[] = [
  { label: "Label", value: "value" }
];
```

## Styling Tips

```tsx
// Add custom classes
<FormInput className="mt-2" />

// Error states automatically styled
error={true} // adds red border + focus ring

// Custom wrapper styling
<FormField className="mb-4">
  {/* content */}
</FormField>
```
