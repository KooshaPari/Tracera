import * as React from "react";
import type { CheckboxProps } from "@/components/ui/checkbox";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";

export interface FormCheckboxProps extends CheckboxProps {
	label?: string;
	error?: boolean;
	errorMessage?: string;
	required?: boolean;
}

export const FormCheckbox = React.forwardRef<
	HTMLInputElement,
	FormCheckboxProps
>(
	(
		{
			className,
			label,
			error,
			errorMessage,
			required,
			id,
			...props
		},
		ref,
	) => {
		const checkboxId = id || `checkbox-${Math.random().toString(36).slice(2, 9)}`;
		const errorId = errorMessage
			? `${checkboxId}-error`
			: undefined;

		return (
			<div className="flex flex-col">
				<div className="flex items-center space-x-2">
					<Checkbox
						ref={ref}
						id={checkboxId}
						className={cn(error && "border-red-500", className)}
						aria-invalid={error}
						aria-describedby={errorId}
						aria-required={required}
						{...props}
					/>
					{label && (
						<label
							htmlFor={checkboxId}
							className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
						>
							{label}
							{required && (
								<span
									className="text-red-500 ml-1"
									aria-label="required"
								>
									*
								</span>
							)}
						</label>
					)}
				</div>
				{errorMessage && error && (
					<span
						id={errorId}
						className="text-sm text-red-500 mt-1"
						role="alert"
					>
						{errorMessage}
					</span>
				)}
			</div>
		);
	},
);

FormCheckbox.displayName = "FormCheckbox";
