import { zodResolver } from "@hookform/resolvers/zod";
import { logger } from '@/lib/logger';
import { Plus, Trash2, X } from "lucide-react";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";
import { useCreateProcess } from "../../hooks/useProcesses";

const categoryOptions = [
	"operational",
	"support",
	"management",
	"development",
	"integration",
	"compliance",
	"other",
] as const;

const stageSchema = z.object({
	id: z.string(),
	name: z.string().min(1, "Stage name required"),
	description: z.string().optional(),
	order: z.number(),
	required: z.boolean().default(true),
	estimatedDurationMinutes: z.coerce.number().optional(),
	assignedRole: z.string().optional(),
});

const swimlaneSchema = z.object({
	id: z.string(),
	name: z.string().min(1, "Swimlane name required"),
	role: z.string().optional(),
	description: z.string().optional(),
});

const processSchema = z.object({
	name: z.string().min(1, "Name is required").max(500, "Name too long"),
	description: z.string().max(5000).optional(),
	purpose: z.string().max(2000).optional(),
	category: z.enum(categoryOptions).optional(),
	owner: z.string().max(255).optional(),
	responsibleTeam: z.string().max(255).optional(),
	expectedDurationHours: z.coerce.number().optional(),
	slaHours: z.coerce.number().optional(),
	exitCriteria: z.string().optional(),
	stages: z.array(stageSchema).optional(),
	swimlanes: z.array(swimlaneSchema).optional(),
});

type ProcessFormData = z.infer<typeof processSchema>;

interface CreateProcessFormProps {
	projectId: string;
	onCancel: () => void;
	onSuccess: () => void;
}

export function CreateProcessForm({
	projectId,
	onCancel,
	onSuccess,
}: CreateProcessFormProps) {
	const createProcess = useCreateProcess();

	const {
		register,
		handleSubmit,
		control,
		formState: { errors },
	} = useForm<ProcessFormData>({
		resolver: zodResolver(processSchema),
		defaultValues: {
			stages: [],
			swimlanes: [],
		},
	});

	const {
		fields: stageFields,
		append: appendStage,
		remove: removeStage,
	} = useFieldArray({
		control,
		name: "stages",
	});

	const {
		fields: swimlaneFields,
		append: appendSwimlane,
		remove: removeSwimlane,
	} = useFieldArray({
		control,
		name: "swimlanes",
	});

	const onSubmit = async (data: ProcessFormData) => {
		try {
			const payload: Parameters<typeof createProcess.mutateAsync>[0] = {
				projectId,
				name: data.name,
			};
			if (data.description) payload.description = data.description;
			if (data.purpose) payload.purpose = data.purpose;
			if (data.category) payload.category = data.category;
			if (data.owner) payload.owner = data.owner;
			if (data.responsibleTeam) payload.responsibleTeam = data.responsibleTeam;
			if (data.expectedDurationHours)
				payload.expectedDurationHours = data.expectedDurationHours;
			if (data.slaHours) payload.slaHours = data.slaHours;
			if (data.exitCriteria) {
				payload.exitCriteria = data.exitCriteria
					.split("\n")
					.filter((c) => c.trim());
			}
			if (data.stages?.length) {
				payload.stages = data.stages.map((s) => ({
					id: s.id,
					name: s.name,
					order: s.order,
					required: s.required,
					...(s.description && { description: s.description }),
					...(s.estimatedDurationMinutes && {
						estimatedDurationMinutes: s.estimatedDurationMinutes,
					}),
					...(s.assignedRole && { assignedRole: s.assignedRole }),
				}));
			}
			if (data.swimlanes?.length) {
				payload.swimlanes = data.swimlanes.map((sw) => ({
					id: sw.id,
					name: sw.name,
					...(sw.role && { role: sw.role }),
					...(sw.description && { description: sw.description }),
				}));
			}

			await createProcess.mutateAsync(payload);
			onSuccess();
		} catch (error) {
			logger.error("Failed to create process:", error);
		}
	};

	const addStage = () => {
		appendStage({
			id: crypto.randomUUID(),
			name: "",
			order: stageFields.length + 1,
			required: true,
		});
	};

	const addSwimlane = () => {
		appendSwimlane({
			id: crypto.randomUUID(),
			name: "",
		});
	};

	return (
		<div className="fixed inset-0 z-50 flex items-center justify-center">
			<div
				className="fixed inset-0 bg-black/50 backdrop-blur-sm"
				onClick={onCancel}
			/>
			<div
				className="relative max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl border bg-background p-6 shadow-2xl"
				role="dialog"
				aria-modal="true"
				aria-labelledby="create-process-title"
			>
				<div className="flex items-center justify-between">
					<h2 id="create-process-title" className="text-lg font-semibold">
						Create Process
					</h2>
					<button
						type="button"
						onClick={onCancel}
						aria-label="Close dialog"
						className="rounded-lg p-1 hover:bg-accent"
					>
						<X className="h-5 w-5" />
					</button>
				</div>

				<form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-6">
					{/* Basic Info */}
					<div className="space-y-4">
						<h3 className="font-medium">Basic Information</h3>

						<div>
							<label className="block text-sm font-medium">
								Name <span className="text-red-500">*</span>
							</label>
							<input
								{...register("name")}
								placeholder="Process name"
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							/>
							{errors.name && (
								<p className="mt-1 text-sm text-red-500">
									{errors.name.message}
								</p>
							)}
						</div>

						<div>
							<label className="block text-sm font-medium">Description</label>
							<textarea
								{...register("description")}
								rows={3}
								placeholder="Describe this process..."
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							/>
						</div>

						<div>
							<label className="block text-sm font-medium">Purpose</label>
							<textarea
								{...register("purpose")}
								rows={2}
								placeholder="What is the purpose of this process?"
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							/>
						</div>

						<div className="grid gap-4 sm:grid-cols-2">
							<div>
								<label className="block text-sm font-medium">Category</label>
								<select
									{...register("category")}
									className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
								>
									<option value="">Select category...</option>
									{categoryOptions.map((cat) => (
										<option key={cat} value={cat}>
											{cat.charAt(0).toUpperCase() + cat.slice(1)}
										</option>
									))}
								</select>
							</div>
							<div>
								<label className="block text-sm font-medium">Owner</label>
								<input
									{...register("owner")}
									placeholder="Process owner..."
									className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
								/>
							</div>
						</div>

						<div className="grid gap-4 sm:grid-cols-3">
							<div>
								<label className="block text-sm font-medium">
									Responsible Team
								</label>
								<input
									{...register("responsibleTeam")}
									placeholder="Team..."
									className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
								/>
							</div>
							<div>
								<label className="block text-sm font-medium">
									Expected Duration (hours)
								</label>
								<input
									{...register("expectedDurationHours")}
									type="number"
									min={0}
									placeholder="Hours..."
									className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
								/>
							</div>
							<div>
								<label className="block text-sm font-medium">SLA (hours)</label>
								<input
									{...register("slaHours")}
									type="number"
									min={0}
									placeholder="Hours..."
									className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
								/>
							</div>
						</div>
					</div>

					{/* Stages */}
					<div className="space-y-4">
						<div className="flex items-center justify-between">
							<h3 className="font-medium">Stages</h3>
							<button
								type="button"
								onClick={addStage}
								className="flex items-center gap-1 text-sm text-primary hover:underline"
							>
								<Plus className="h-4 w-4" /> Add Stage
							</button>
						</div>

						{stageFields.length === 0 ? (
							<p className="text-sm text-muted-foreground">
								No stages defined. Click "Add Stage" to define process steps.
							</p>
						) : (
							<div className="space-y-3">
								{stageFields.map((field, index) => (
									<div
										key={field.id}
										className="flex items-start gap-3 rounded-lg border p-3"
									>
										<span className="mt-2 text-sm font-medium text-muted-foreground">
											{index + 1}.
										</span>
										<div className="flex-1 grid gap-3 sm:grid-cols-2">
											<input
												{...register(`stages.${index}.name`)}
												placeholder="Stage name"
												className="rounded-lg border bg-background px-3 py-2"
											/>
											<input
												{...register(`stages.${index}.assignedRole`)}
												placeholder="Assigned role"
												className="rounded-lg border bg-background px-3 py-2"
											/>
											<input
												{...register(`stages.${index}.description`)}
												placeholder="Description"
												className="rounded-lg border bg-background px-3 py-2 sm:col-span-2"
											/>
										</div>
										<button
											type="button"
											onClick={() => removeStage(index)}
											className="mt-2 text-red-500 hover:text-red-700"
										>
											<Trash2 className="h-4 w-4" />
										</button>
									</div>
								))}
							</div>
						)}
					</div>

					{/* Swimlanes */}
					<div className="space-y-4">
						<div className="flex items-center justify-between">
							<h3 className="font-medium">Swimlanes (Actors/Roles)</h3>
							<button
								type="button"
								onClick={addSwimlane}
								className="flex items-center gap-1 text-sm text-primary hover:underline"
							>
								<Plus className="h-4 w-4" /> Add Swimlane
							</button>
						</div>

						{swimlaneFields.length === 0 ? (
							<p className="text-sm text-muted-foreground">
								No swimlanes defined. Click "Add Swimlane" to define actors.
							</p>
						) : (
							<div className="space-y-3">
								{swimlaneFields.map((field, index) => (
									<div
										key={field.id}
										className="flex items-center gap-3 rounded-lg border p-3"
									>
										<div className="flex-1 grid gap-3 sm:grid-cols-2">
											<input
												{...register(`swimlanes.${index}.name`)}
												placeholder="Swimlane name"
												className="rounded-lg border bg-background px-3 py-2"
											/>
											<input
												{...register(`swimlanes.${index}.role`)}
												placeholder="Role"
												className="rounded-lg border bg-background px-3 py-2"
											/>
										</div>
										<button
											type="button"
											onClick={() => removeSwimlane(index)}
											className="text-red-500 hover:text-red-700"
										>
											<Trash2 className="h-4 w-4" />
										</button>
									</div>
								))}
							</div>
						)}
					</div>

					{/* Exit Criteria */}
					<div>
						<label className="block text-sm font-medium">
							Exit Criteria (one per line)
						</label>
						<textarea
							{...register("exitCriteria")}
							rows={3}
							placeholder="Conditions that must be met to complete the process..."
							className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
						/>
					</div>

					{/* Actions */}
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
							disabled={createProcess.isPending}
							className="flex-1 rounded-lg bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
						>
							{createProcess.isPending ? "Creating..." : "Create Process"}
						</button>
					</div>

					{createProcess.isError && (
						<p className="text-sm text-red-500">
							Error: {createProcess.error.message}
						</p>
					)}
				</form>
			</div>
		</div>
	);
}
