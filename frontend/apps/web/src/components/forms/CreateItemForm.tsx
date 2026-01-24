import { zodResolver } from "@hookform/resolvers/zod";
import { X } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

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

	return (
		<div className="fixed inset-0 z-50 flex items-center justify-center">
			<div
				className="fixed inset-0 bg-black/50 backdrop-blur-sm"
				onClick={onCancel}
			/>
			<div className="relative max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl border bg-background p-6 shadow-2xl">
				<div className="flex items-center justify-between">
					<h2 className="text-lg font-semibold">Create Item</h2>
					<button onClick={onCancel} className="rounded-lg p-1 hover:bg-accent">
						<X className="h-5 w-5" />
					</button>
				</div>

				<form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
					<div className="grid gap-4 sm:grid-cols-2">
						<div>
							<label className="block text-sm font-medium">
								View <span className="text-red-500">*</span>
							</label>
							<select
								{...register("view")}
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							>
								{viewTypes.map((v) => (
									<option key={v} value={v}>
										{v}
									</option>
								))}
							</select>
						</div>
						<div>
							<label className="block text-sm font-medium">
								Type <span className="text-red-500">*</span>
							</label>
							<select
								{...register("type")}
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							>
								{typeOptions[selectedView]?.map((t) => (
									<option key={t} value={t}>
										{t}
									</option>
								))}
							</select>
							{errors.type && (
								<p className="mt-1 text-sm text-red-500">
									{errors.type.message}
								</p>
							)}
						</div>
					</div>

					<div>
						<label className="block text-sm font-medium">
							Title <span className="text-red-500">*</span>
						</label>
						<input
							{...register("title")}
							placeholder="Enter item title"
							className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
						/>
						{errors.title && (
							<p className="mt-1 text-sm text-red-500">
								{errors.title.message}
							</p>
						)}
					</div>

					<div>
						<label className="block text-sm font-medium">Description</label>
						<textarea
							{...register("description")}
							rows={3}
							placeholder="Describe this item..."
							className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
						/>
					</div>

					<div className="grid gap-4 sm:grid-cols-2">
						<div>
							<label className="block text-sm font-medium">Status</label>
							<select
								{...register("status")}
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							>
								{statusOptions.map((s) => (
									<option key={s} value={s}>
										{s.replace("_", " ")}
									</option>
								))}
							</select>
						</div>
						<div>
							<label className="block text-sm font-medium">Priority</label>
							<select
								{...register("priority")}
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
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
						<label className="block text-sm font-medium">Owner</label>
						<input
							{...register("owner")}
							placeholder="Assigned to..."
							className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
						/>
					</div>

					<div className="flex gap-3 pt-4">
						<button
							type="button"
							onClick={onCancel}
							className="flex-1 rounded-lg border px-4 py-2 hover:bg-accent"
						>
							Cancel
						</button>
						<button
							type="submit"
							disabled={isLoading}
							className="flex-1 rounded-lg bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
						>
							{isLoading ? "Creating..." : "Create Item"}
						</button>
					</div>
				</form>
			</div>
		</div>
	);
}
