import { zodResolver } from "@hookform/resolvers/zod";
import { X } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useEffect, useRef, useCallback } from "react";

const viewTypes = [
	"FEATURE",
	"CODE",
	"TEST",
	"API",
	"DATABASE",
	"WIREFRAME",
	"DOCUMENTATION",
	"DEPLOYMENT",
] as const;
const statusOptions = [
	"todo",
	"in_progress",
	"done",
	"blocked",
	"cancelled",
] as const;
const priorityOptions = ["low", "medium", "high", "critical"] as const;

const itemSchema = z.object({
	title: z.string().min(1, "Title is required").max(500, "Title too long"),
	description: z.string().max(5000).optional(),
	view: z.enum(viewTypes),
	type: z.string().min(1, "Type is required"),
	status: z.enum(statusOptions),
	priority: z.enum(priorityOptions),
	parentId: z.string().uuid().optional().or(z.literal("")),
	owner: z.string().max(255).optional(),
});

type ItemFormData = z.infer<typeof itemSchema>;

interface CreateItemFormProps {
	onSubmit: (data: ItemFormData) => void;
	onCancel: () => void;
	isLoading?: boolean;
	defaultView?: (typeof viewTypes)[number];
}

export function CreateItemForm({
	onSubmit,
	onCancel,
	isLoading,
	defaultView = "FEATURE",
}: CreateItemFormProps) {
	const dialogRef = useRef<HTMLDivElement>(null);
	const firstFocusableRef = useRef<HTMLInputElement>(null);
	const lastFocusableRef = useRef<HTMLButtonElement>(null);

	const {
		register,
		handleSubmit,
		watch,
		formState: { errors },
	} = useForm<ItemFormData>({
		resolver: zodResolver(itemSchema),
		defaultValues: { view: defaultView, status: "todo", priority: "medium" },
	});

	const selectedView = watch("view");
	const typeOptions: Record<string, string[]> = {
		FEATURE: ["epic", "feature", "story", "task"],
		CODE: ["module", "file", "function", "class"],
		TEST: ["suite", "case", "scenario"],
		API: ["endpoint", "schema", "model"],
		DATABASE: ["table", "column", "index"],
		WIREFRAME: ["screen", "component", "flow"],
		DOCUMENTATION: ["guide", "reference", "tutorial", "changelog"],
		DEPLOYMENT: ["environment", "release", "config"],
	};

	// Handle Escape key to close dialog
	const handleKeyDown = useCallback(
		(e: KeyboardEvent) => {
			if (e.key === "Escape") {
				onCancel();
			}
		},
		[onCancel],
	);

	// Focus trap: keep focus within the dialog
	const handleDialogKeyDown = useCallback(
		(e: KeyboardEvent) => {
			if (e.key !== "Tab" || !dialogRef.current) {
				return;
			}

			const focusableElements = dialogRef.current.querySelectorAll(
				"button, [href], input, select, textarea",
			);
			const focusableArray = Array.from(focusableElements);

			if (focusableArray.length === 0) return;

			const firstElement = focusableArray[0] as HTMLElement;
			const lastElement = focusableArray[focusableArray.length - 1] as HTMLElement;

			if (e.shiftKey) {
				// Shift+Tab
				if (document.activeElement === firstElement) {
					e.preventDefault();
					lastElement.focus();
				}
			} else {
				// Tab
				if (document.activeElement === lastElement) {
					e.preventDefault();
					firstElement.focus();
				}
			}
		},
		[],
	);

	useEffect(() => {
		document.addEventListener("keydown", handleKeyDown);

		// Focus first input on mount
		if (firstFocusableRef.current) {
			firstFocusableRef.current.focus();
		}

		// Trap focus within dialog
		dialogRef.current?.addEventListener("keydown", handleDialogKeyDown);

		return () => {
			document.removeEventListener("keydown", handleKeyDown);
			dialogRef.current?.removeEventListener("keydown", handleDialogKeyDown);
		};
	}, [handleKeyDown, handleDialogKeyDown]);

	return (
		<div className="fixed inset-0 z-50 flex items-center justify-center">
			{/* Backdrop */}
			<div
				className="fixed inset-0 bg-black/50 backdrop-blur-sm"
				onClick={onCancel}
				aria-hidden="true"
			/>

			{/* Dialog */}
			<div
				ref={dialogRef}
				role="dialog"
				aria-modal="true"
				aria-labelledby="dialog-title"
				className="relative max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl border bg-background p-6 shadow-2xl focus:outline-none"
				tabIndex={-1}
			>
				<div className="flex items-center justify-between">
					<h2 id="dialog-title" className="text-lg font-semibold">
						Create Item
					</h2>
					<button
						onClick={onCancel}
						aria-label="Close dialog"
						className="rounded-lg p-1 hover:bg-accent focus:outline-none focus:ring-2 focus:ring-primary"
					>
						<X className="h-5 w-5" />
					</button>
				</div>

				<form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
					<div className="grid gap-4 sm:grid-cols-2">
						<div>
							<label htmlFor="view" className="block text-sm font-medium">
								View <span className="text-red-500">*</span>
							</label>
							<select
								id="view"
								role="combobox"
								aria-expanded="false"
								{...register("view")}
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
							>
								{viewTypes.map((v) => (
									<option key={v} value={v}>
										{v}
									</option>
								))}
							</select>
						</div>
						<div>
							<label htmlFor="type" className="block text-sm font-medium">
								Type <span className="text-red-500">*</span>
							</label>
							<select
								id="type"
								role="combobox"
								aria-expanded="false"
								{...register("type")}
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
							>
								{typeOptions[selectedView]?.map((t) => (
									<option key={t} value={t}>
										{t}
									</option>
								))}
							</select>
							{errors.type && (
								<p
									role="alert"
									className="mt-1 text-sm text-red-500"
									aria-live="polite"
								>
									{errors.type.message}
								</p>
							)}
						</div>
					</div>

					<div>
						<label htmlFor="title" className="block text-sm font-medium">
							Title <span className="text-red-500">*</span>
						</label>
						<input
							id="title"
							name="title"
							{...register("title")}
							placeholder="Enter item title"
							className="mt-1 w-full rounded-lg border bg-background px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
							ref={(el) => {
								if (el && !firstFocusableRef.current) {
									firstFocusableRef.current = el;
								}
							}}
						/>
						{errors.title && (
							<p
								role="alert"
								className="mt-1 text-sm text-red-500"
								aria-live="polite"
							>
								{errors.title.message}
							</p>
						)}
					</div>

					<div>
						<label htmlFor="description" className="block text-sm font-medium">
							Description
						</label>
						<textarea
							id="description"
							name="description"
							{...register("description")}
							rows={3}
							placeholder="Describe this item..."
							className="mt-1 w-full rounded-lg border bg-background px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
						/>
					</div>

					<div className="grid gap-4 sm:grid-cols-2">
						<div>
							<label htmlFor="status" className="block text-sm font-medium">
								Status
							</label>
							<select
								id="status"
								role="combobox"
								aria-expanded="false"
								{...register("status")}
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
							>
								{statusOptions.map((s) => (
									<option key={s} value={s}>
										{s.replace("_", " ")}
									</option>
								))}
							</select>
						</div>
						<div>
							<label htmlFor="priority" className="block text-sm font-medium">
								Priority
							</label>
							<select
								id="priority"
								role="combobox"
								aria-expanded="false"
								{...register("priority")}
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
							>
								{priorityOptions.map((p) => (
									<option key={p} value={p}>
										{p}
									</option>
								))}
							</select>
						</div>
					</div>

					<div>
						<label htmlFor="owner" className="block text-sm font-medium">
							Owner
						</label>
						<input
							id="owner"
							name="owner"
							{...register("owner")}
							placeholder="Assigned to..."
							className="mt-1 w-full rounded-lg border bg-background px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
						/>
					</div>

					<div className="flex gap-3 pt-4">
						<button
							type="button"
							onClick={onCancel}
							className="flex-1 rounded-lg border px-4 py-2 hover:bg-accent focus:outline-none focus:ring-2 focus:ring-primary"
						>
							Cancel
						</button>
						<button
							ref={lastFocusableRef}
							type="submit"
							disabled={isLoading}
							className="flex-1 rounded-lg bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-primary"
						>
							{isLoading ? "Creating..." : "Create Item"}
						</button>
					</div>
				</form>
			</div>
		</div>
	);
}
