import { zodResolver } from "@hookform/resolvers/zod";
import { logger } from '@/lib/logger';
import { Plus, Trash2, X } from "lucide-react";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";
import { useCreateTestCase } from "../../hooks/useTestCases";

const testTypes = [
	"functional",
	"integration",
	"unit",
	"e2e",
	"performance",
	"security",
	"accessibility",
	"regression",
	"smoke",
	"exploratory",
] as const;

const priorities = ["critical", "high", "medium", "low"] as const;

const automationStatuses = [
	"not_automated",
	"in_progress",
	"automated",
	"cannot_automate",
] as const;

const testStepSchema = z.object({
	action: z.string().min(1, "Action is required"),
	expectedResult: z.string().optional(),
	testData: z.string().optional(),
});

const testCaseSchema = z.object({
	title: z.string().min(1, "Title is required").max(500, "Title too long"),
	description: z.string().max(5000).optional(),
	objective: z.string().max(2000).optional(),
	testType: z.enum(testTypes),
	priority: z.enum(priorities),
	category: z.string().max(100).optional(),
	tags: z.string().optional(),
	preconditions: z.string().max(2000).optional(),
	testSteps: z.array(testStepSchema).optional(),
	expectedResult: z.string().max(2000).optional(),
	postconditions: z.string().max(2000).optional(),
	automationStatus: z.enum(automationStatuses),
	automationScriptPath: z.string().max(500).optional(),
	automationFramework: z.string().max(100).optional(),
	automationNotes: z.string().max(2000).optional(),
	estimatedDurationMinutes: z.coerce.number().min(1).optional(),
	assignedTo: z.string().max(255).optional(),
});

type TestCaseFormData = z.infer<typeof testCaseSchema>;

interface CreateTestCaseFormProps {
	projectId: string;
	onCancel: () => void;
	onSuccess: () => void;
}

const categoryOptions = [
	"User Authentication",
	"User Interface",
	"API",
	"Database",
	"Integration",
	"Performance",
	"Security",
	"Accessibility",
	"Mobile",
	"Desktop",
	"Other",
];

const typeLabels: Record<(typeof testTypes)[number], string> = {
	functional: "Functional",
	integration: "Integration",
	unit: "Unit",
	e2e: "End-to-End",
	performance: "Performance",
	security: "Security",
	accessibility: "Accessibility",
	regression: "Regression",
	smoke: "Smoke",
	exploratory: "Exploratory",
};

const automationLabels: Record<(typeof automationStatuses)[number], string> = {
	not_automated: "Not Automated (Manual)",
	in_progress: "Automation In Progress",
	automated: "Fully Automated",
	cannot_automate: "Cannot Be Automated",
};

export function CreateTestCaseForm({
	projectId,
	onCancel,
	onSuccess,
}: CreateTestCaseFormProps) {
	const createTestCase = useCreateTestCase();

	const {
		register,
		handleSubmit,
		control,
		formState: { errors },
	} = useForm<TestCaseFormData>({
		resolver: zodResolver(testCaseSchema) as any,
		defaultValues: {
			testType: "functional",
			priority: "medium",
			automationStatus: "not_automated",
			testSteps: [],
		},
	});

	const { fields, append, remove } = useFieldArray({
		control,
		name: "testSteps",
	});

	const onSubmit = async (data: TestCaseFormData) => {
		try {
			const payload: Parameters<typeof createTestCase.mutateAsync>[0] = {
				projectId,
				title: data.title,
				testType: data.testType,
				priority: data.priority,
				automationStatus: data.automationStatus,
			};
			if (data.description) payload.description = data.description;
			if (data.objective) payload.objective = data.objective;
			if (data.category) payload.category = data.category;
			if (data.tags) {
				payload.tags = data.tags
					.split(",")
					.map((s) => s.trim())
					.filter(Boolean);
			}
			if (data.preconditions) payload.preconditions = data.preconditions;
			if (data.testSteps && data.testSteps.length > 0) {
				payload.testSteps = data.testSteps.map((step, index) => ({
					stepNumber: index + 1,
					action: step.action,
					expectedResult: step.expectedResult || "",
					testData: step.testData || "",
				}));
			}
			if (data.expectedResult) payload.expectedResult = data.expectedResult;
			if (data.postconditions) payload.postconditions = data.postconditions;
			if (data.automationScriptPath)
				payload.automationScriptPath = data.automationScriptPath;
			if (data.automationFramework)
				payload.automationFramework = data.automationFramework;
			if (data.automationNotes) payload.automationNotes = data.automationNotes;
			if (data.estimatedDurationMinutes)
				payload.estimatedDurationMinutes = data.estimatedDurationMinutes;
			if (data.assignedTo) payload.assignedTo = data.assignedTo;

			await createTestCase.mutateAsync(payload);
			onSuccess();
		} catch (error) {
			logger.error("Failed to create test case:", error);
		}
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
				aria-labelledby="create-test-case-title"
			>
				<div className="flex items-center justify-between">
					<h2 id="create-test-case-title" className="text-lg font-semibold">
						Create Test Case
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

				<form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
					{/* Title */}
					<div>
						<label className="block text-sm font-medium">
							Title <span className="text-red-500">*</span>
						</label>
						<input
							{...register("title")}
							placeholder="Brief description of the test case"
							className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
						/>
						{errors.title && (
							<p className="mt-1 text-sm text-red-500">
								{errors.title.message}
							</p>
						)}
					</div>

					{/* Description & Objective */}
					<div className="grid gap-4 sm:grid-cols-2">
						<div>
							<label className="block text-sm font-medium">Description</label>
							<textarea
								{...register("description")}
								rows={3}
								placeholder="Detailed description of what this test case covers..."
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							/>
						</div>
						<div>
							<label className="block text-sm font-medium">Objective</label>
							<textarea
								{...register("objective")}
								rows={3}
								placeholder="What is the goal of this test?"
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							/>
						</div>
					</div>

					{/* Type, Priority, Category */}
					<div className="grid gap-4 sm:grid-cols-3">
						<div>
							<label className="block text-sm font-medium">
								Test Type <span className="text-red-500">*</span>
							</label>
							<select
								{...register("testType")}
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							>
								{testTypes.map((type) => (
									<option key={type} value={type}>
										{typeLabels[type]}
									</option>
								))}
							</select>
						</div>
						<div>
							<label className="block text-sm font-medium">
								Priority <span className="text-red-500">*</span>
							</label>
							<select
								{...register("priority")}
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							>
								{priorities.map((p) => (
									<option key={p} value={p}>
										{p.charAt(0).toUpperCase() + p.slice(1)}
									</option>
								))}
							</select>
						</div>
						<div>
							<label className="block text-sm font-medium">Category</label>
							<select
								{...register("category")}
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							>
								<option value="">Select category...</option>
								{categoryOptions.map((cat) => (
									<option key={cat} value={cat}>
										{cat}
									</option>
								))}
							</select>
						</div>
					</div>

					{/* Tags */}
					<div>
						<label className="block text-sm font-medium">Tags</label>
						<input
							{...register("tags")}
							placeholder="Comma-separated tags (e.g., smoke, login, api)"
							className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
						/>
					</div>

					{/* Preconditions */}
					<div>
						<label className="block text-sm font-medium">Preconditions</label>
						<textarea
							{...register("preconditions")}
							rows={2}
							placeholder="What conditions must be met before running this test?"
							className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
						/>
					</div>

					{/* Test Steps */}
					<div>
						<div className="flex items-center justify-between">
							<label className="block text-sm font-medium">Test Steps</label>
							<button
								type="button"
								onClick={() =>
									append({ action: "", expectedResult: "", testData: "" })
								}
								className="flex items-center gap-1 text-sm text-primary hover:text-primary/80"
							>
								<Plus className="h-4 w-4" /> Add Step
							</button>
						</div>
						<div className="mt-2 space-y-3">
							{fields.map((field, index) => (
								<div key={field.id} className="rounded-lg border p-3">
									<div className="flex items-center justify-between mb-2">
										<span className="text-sm font-medium text-muted-foreground">
											Step {index + 1}
										</span>
										<button
											type="button"
											onClick={() => remove(index)}
											className="text-red-500 hover:text-red-700"
										>
											<Trash2 className="h-4 w-4" />
										</button>
									</div>
									<div className="space-y-2">
										<input
											{...register(`testSteps.${index}.action`)}
											placeholder="Action to perform..."
											className="w-full rounded-lg border bg-background px-3 py-2 text-sm"
										/>
										<input
											{...register(`testSteps.${index}.expectedResult`)}
											placeholder="Expected result..."
											className="w-full rounded-lg border bg-background px-3 py-2 text-sm"
										/>
										<input
											{...register(`testSteps.${index}.testData`)}
											placeholder="Test data (optional)..."
											className="w-full rounded-lg border bg-background px-3 py-2 text-sm"
										/>
									</div>
								</div>
							))}
							{fields.length === 0 && (
								<p className="text-sm text-muted-foreground italic">
									No test steps defined. Click "Add Step" to add one.
								</p>
							)}
						</div>
					</div>

					{/* Expected Result & Postconditions */}
					<div className="grid gap-4 sm:grid-cols-2">
						<div>
							<label className="block text-sm font-medium">
								Overall Expected Result
							</label>
							<textarea
								{...register("expectedResult")}
								rows={2}
								placeholder="Expected overall outcome of the test..."
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							/>
						</div>
						<div>
							<label className="block text-sm font-medium">
								Postconditions
							</label>
							<textarea
								{...register("postconditions")}
								rows={2}
								placeholder="State after test completion..."
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							/>
						</div>
					</div>

					{/* Automation */}
					<div className="rounded-lg border p-4 bg-muted/30">
						<h3 className="text-sm font-medium mb-3">Automation Settings</h3>
						<div className="grid gap-4 sm:grid-cols-2">
							<div>
								<label className="block text-sm font-medium">
									Automation Status
								</label>
								<select
									{...register("automationStatus")}
									className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
								>
									{automationStatuses.map((status) => (
										<option key={status} value={status}>
											{automationLabels[status]}
										</option>
									))}
								</select>
							</div>
							<div>
								<label className="block text-sm font-medium">Framework</label>
								<input
									{...register("automationFramework")}
									placeholder="e.g., Playwright, Cypress, Jest..."
									className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
								/>
							</div>
							<div className="sm:col-span-2">
								<label className="block text-sm font-medium">Script Path</label>
								<input
									{...register("automationScriptPath")}
									placeholder="Path to automation script..."
									className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
								/>
							</div>
							<div className="sm:col-span-2">
								<label className="block text-sm font-medium">
									Automation Notes
								</label>
								<textarea
									{...register("automationNotes")}
									rows={2}
									placeholder="Any notes about automation..."
									className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
								/>
							</div>
						</div>
					</div>

					{/* Estimates & Assignment */}
					<div className="grid gap-4 sm:grid-cols-2">
						<div>
							<label className="block text-sm font-medium">
								Estimated Duration (minutes)
							</label>
							<input
								{...register("estimatedDurationMinutes")}
								type="number"
								min={1}
								placeholder="e.g., 15"
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							/>
						</div>
						<div>
							<label className="block text-sm font-medium">Assigned To</label>
							<input
								{...register("assignedTo")}
								placeholder="Person responsible..."
								className="mt-1 w-full rounded-lg border bg-background px-3 py-2"
							/>
						</div>
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
							disabled={createTestCase.isPending}
							className="flex-1 rounded-lg bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
						>
							{createTestCase.isPending ? "Creating..." : "Create Test Case"}
						</button>
					</div>

					{createTestCase.isError && (
						<p className="text-sm text-red-500">
							Error: {createTestCase.error.message}
						</p>
					)}
				</form>
			</div>
		</div>
	);
}
