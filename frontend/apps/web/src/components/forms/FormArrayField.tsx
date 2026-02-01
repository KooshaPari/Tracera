import { Button } from "@tracertm/ui";
import { Plus, Trash2 } from "lucide-react";
import type * as React from "react";
import type { ArrayPath, Control, FieldValues } from "react-hook-form";
import { useFieldArray } from "react-hook-form";
import { cn } from "@/lib/utils";

export interface FormArrayFieldProps<T extends FieldValues> {
	control: Control<T>;
	name: ArrayPath<T>;
	label: string;
	helpText?: string;
	renderField: (index: number) => React.ReactNode;
	defaultValue?: any;
	addButtonLabel?: string;
	removeButtonLabel?: string;
	minItems?: number;
	maxItems?: number;
	className?: string;
}

export function FormArrayField<T extends FieldValues>({
	control,
	name,
	label,
	helpText,
	renderField,
	defaultValue,
	addButtonLabel = "Add item",
	removeButtonLabel = "Remove",
	minItems = 0,
	maxItems,
	className,
}: FormArrayFieldProps<T>) {
	const { fields, append, remove } = useFieldArray({
		control,
		name,
	});

	const canAdd = !maxItems || fields.length < maxItems;
	const canRemove = fields.length > minItems;

	return (
		<div className={cn("space-y-4", className)}>
			<div className="flex items-center justify-between">
				<div>
					<label className="block text-sm font-medium text-foreground">
						{label}
					</label>
					{helpText && (
						<p className="text-xs text-muted-foreground mt-1">{helpText}</p>
					)}
				</div>
				<Button
					type="button"
					variant="outline"
					size="sm"
					onClick={() => append(defaultValue)}
					disabled={!canAdd}
					aria-label={addButtonLabel}
				>
					<Plus className="h-4 w-4 mr-1" aria-hidden="true" />
					{addButtonLabel}
				</Button>
			</div>

			<div className="space-y-3">
				{fields.length === 0 ? (
					<p className="text-sm text-muted-foreground italic">
						No items added yet. Click "{addButtonLabel}" to get started.
					</p>
				) : (
					fields.map((field, index) => (
						<div
							key={field.id}
							className="flex items-start gap-2 p-3 border rounded-lg bg-muted/50"
						>
							<div className="flex-1">{renderField(index)}</div>
							<Button
								type="button"
								variant="ghost"
								size="icon"
								onClick={() => remove(index)}
								disabled={!canRemove}
								aria-label={`${removeButtonLabel} item ${index + 1}`}
								className="mt-1 shrink-0"
							>
								<Trash2
									className="h-4 w-4 text-destructive"
									aria-hidden="true"
								/>
							</Button>
						</div>
					))
				)}
			</div>

			{maxItems && (
				<p className="text-xs text-muted-foreground">
					{fields.length} / {maxItems} items
				</p>
			)}
		</div>
	);
}

FormArrayField.displayName = "FormArrayField";
