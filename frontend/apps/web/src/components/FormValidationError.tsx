interface FormValidationErrorProps {
	message: string;
	testId?: string;
}

export function FormValidationError({
	message,
	testId = "form-error",
}: FormValidationErrorProps) {
	if (!message) return null;

	return (
		<div
			className="rounded-md bg-destructive/10 p-3 text-sm text-destructive border border-destructive/20"
			data-testid={testId}
			role="alert"
		>
			{message}
		</div>
	);
}
