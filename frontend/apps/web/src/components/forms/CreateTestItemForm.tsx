import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { FormInput, FormSelect, FormTextarea } from "./index";

// Status and Priority options (matching Item model)
const statusOptions = [
	{ label: "Todo", value: "todo" },
	{ label: "In Progress", value: "in_progress" },
	{ label: "Done", value: "done" },
	{ label: "Blocked", value: "blocked" },
	{ label: "Cancelled", value: "cancelled" },
] as const;

const priorityOptions = [
	{ label: "Low", value: "low" },
	{ label: "Medium", value: "medium" },
	{ label: "High", value: "high" },
	{ label: "Critical", value: "critical" },
] as const;

// Test Spec specific options (matching TestSpec model)
const testTypeOptions = [
	{ label: "Unit", value: "unit" },
	{ label: "Integration", value: "integration" },
	{ label: "End-to-End", value: "e2e" },
	{ label: "Performance", value: "performance" },
	{ label: "Security", value: "security" },
	{ label: "Smoke", value: "smoke" },
	{ label: "Regression", value: "regression" },
	{ label: "Acceptance", value: "acceptance" },
] as const;

const oracleTypeOptions = [
	{ label: "Assertion", value: "assertion" },
	{ label: "Golden (Reference)", value: "golden" },
	{ label: "Metamorphic", value: "metamorphic" },
	{ label: "Property-Based", value: "property" },
	{ label: "Differential", value: "differential" },
] as const;

const coverageTypeOptions = [
	{ label: "Statement", value: "statement" },
	{ label: "Branch", value: "branch" },
	{ label: "MC/DC", value: "mcdc" },
	{ label: "Path", value: "path" },
	{ label: "Condition", value: "condition" },
] as const;

const safetyLevelOptions = [
	{ label: "DAL-A (Catastrophic)", value: "DAL-A" },
	{ label: "DAL-B (Hazardous)", value: "DAL-B" },
	{ label: "DAL-C (Major)", value: "DAL-C" },
	{ label: "DAL-D (Minor)", value: "DAL-D" },
	{ label: "DAL-E (No Effect)", value: "DAL-E" },
] as const;

// Zod schema matching backend TestSpec fields
const testItemSchema = z.object({
	// Base Item fields
	title: z.string().min(1, "Title is required").max(500, "Title too long"),
	description: z.string().max(5000).optional(),
	status: z.enum(["todo", "in_progress", "done", "blocked", "cancelled"]),
	priority: z.enum(["low", "medium", "high", "critical"]),
	owner: z.string().max(255).optional(),

	// Test Spec fields
	test_type: z.enum([
		"unit",
		"integration",
		"e2e",
		"performance",
		"security",
		"smoke",
		"regression",
		"acceptance",
	]),
	test_framework: z.string().max(100).optional(),
	language: z.string().max(50).optional(),
	oracle_type: z
		.enum(["assertion", "golden", "metamorphic", "property", "differential"])
		.optional(),
	coverage_type: z
		.enum(["statement", "branch", "mcdc", "path", "condition"])
		.optional(),
	safety_level: z
		.enum(["DAL-A", "DAL-B", "DAL-C", "DAL-D", "DAL-E"])
		.optional(),
	expected_duration_ms: z.coerce.number().int().positive().optional(),
	is_critical_path: z.boolean().optional(),
});

type TestItemFormData = z.infer<typeof testItemSchema>;

interface CreateTestItemFormProps {
	onSubmit: (data: TestItemFormData) => void;
	onCancel: () => void;
	isLoading?: boolean;
}

export function CreateTestItemForm({
	onSubmit,
	onCancel,
	isLoading,
}: CreateTestItemFormProps) {
	const {
		register,
		handleSubmit,
		formState: { errors, isSubmitting },
	} = useForm<TestItemFormData>({
		defaultValues: {
			is_critical_path: false,
			priority: "medium",
			status: "todo",
			test_type: "unit",
		},
		mode: "onBlur",
		resolver: zodResolver(testItemSchema),
	});

	const handleFormSubmit = (data: TestItemFormData) => {
		onSubmit(data);
	};

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
				role="dialog"
				aria-modal="true"
				aria-labelledby="dialog-title"
				className="relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl border bg-background p-6 shadow-2xl"
			>
				<div className="mb-6">
					<h2 id="dialog-title" className="text-lg font-semibold">
						Create Test Item
					</h2>
					<p className="text-sm text-muted-foreground mt-1">
						Create a new test specification with detailed configuration
					</p>
				</div>

				<form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
					{/* Test Details Section */}
					<div className="space-y-4">
						<h3 className="text-sm font-medium border-b pb-2">Test Details</h3>

						<FormInput
							label="Title"
							name="title"
							register={register}
							error={Boolean(errors.title)}
							placeholder="Enter test title"
							required
						/>

						<FormTextarea
							label="Description"
							name="description"
							register={register}
							error={Boolean(errors.description)}
							placeholder="Describe this test..."
							rows={3}
						/>

						<div className="grid gap-4 sm:grid-cols-2">
							<FormSelect
								label="Status"
								name="status"
								register={register}
								error={Boolean(errors.status)}
								options={statusOptions}
								required
							/>

							<FormSelect
								label="Priority"
								name="priority"
								register={register}
								error={Boolean(errors.priority)}
								options={priorityOptions}
								required
							/>
						</div>

						<FormInput
							label="Owner"
							name="owner"
							register={register}
							error={Boolean(errors.owner)}
							placeholder="Assigned to..."
						/>
					</div>

					{/* Test Specification Section */}
					<div className="space-y-4">
						<h3 className="text-sm font-medium border-b pb-2">
							Test Specification
						</h3>

						<div className="grid gap-4 sm:grid-cols-2">
							<FormSelect
								label="Test Type"
								name="test_type"
								register={register}
								error={Boolean(errors.test_type)}
								options={testTypeOptions}
								required
							/>

							<FormInput
								label="Test Framework"
								name="test_framework"
								register={register}
								error={Boolean(errors.test_framework)}
								placeholder="e.g., Vitest, Jest, Pytest"
							/>
						</div>

						<div className="grid gap-4 sm:grid-cols-2">
							<FormInput
								label="Language"
								name="language"
								register={register}
								error={Boolean(errors.language)}
								placeholder="e.g., TypeScript, Python"
							/>

							<FormSelect
								label="Oracle Type"
								name="oracle_type"
								register={register}
								error={Boolean(errors.oracle_type)}
								options={oracleTypeOptions}
							/>
						</div>

						<div className="grid gap-4 sm:grid-cols-2">
							<FormSelect
								label="Coverage Type"
								name="coverage_type"
								register={register}
								error={Boolean(errors.coverage_type)}
								options={coverageTypeOptions}
							/>

							<FormSelect
								label="Safety Level (DO-178C)"
								name="safety_level"
								register={register}
								error={Boolean(errors.safety_level)}
								options={safetyLevelOptions}
							/>
						</div>

						<div className="grid gap-4 sm:grid-cols-2">
							<FormInput
								label="Expected Duration (ms)"
								name="expected_duration_ms"
								type="number"
								register={register}
								error={Boolean(errors.expected_duration_ms)}
								placeholder="Expected execution time"
							/>

							<div className="flex items-center pt-6">
								<input
									type="checkbox"
									id="is_critical_path"
									{...register("is_critical_path")}
									className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
								/>
								<label
									htmlFor="is_critical_path"
									className="ml-2 text-sm font-medium"
								>
									Critical Path Test
								</label>
							</div>
						</div>
					</div>

					{/* Action Buttons */}
					<div className="flex gap-3 pt-4 border-t">
						<button
							type="button"
							onClick={onCancel}
							className="flex-1 rounded-lg border px-4 py-2 hover:bg-accent focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
						>
							Cancel
						</button>
						<button
							type="submit"
							disabled={isLoading || isSubmitting}
							className="flex-1 rounded-lg bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
						>
							{isLoading || isSubmitting ? "Creating..." : "Create Test Item"}
						</button>
					</div>
				</form>
			</div>
		</div>
	);
}
