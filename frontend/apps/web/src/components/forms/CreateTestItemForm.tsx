import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { FormInput, FormSelect, FormTextarea } from "./index";

// Status and Priority options (matching Item model)
const statusOptions = [
	{ value: "todo", label: "Todo" },
	{ value: "in_progress", label: "In Progress" },
	{ value: "done", label: "Done" },
	{ value: "blocked", label: "Blocked" },
	{ value: "cancelled", label: "Cancelled" },
] as const;

const priorityOptions = [
	{ value: "low", label: "Low" },
	{ value: "medium", label: "Medium" },
	{ value: "high", label: "High" },
	{ value: "critical", label: "Critical" },
] as const;

// Test Spec specific options (matching TestSpec model)
const testTypeOptions = [
	{ value: "unit", label: "Unit" },
	{ value: "integration", label: "Integration" },
	{ value: "e2e", label: "End-to-End" },
	{ value: "performance", label: "Performance" },
	{ value: "security", label: "Security" },
	{ value: "smoke", label: "Smoke" },
	{ value: "regression", label: "Regression" },
	{ value: "acceptance", label: "Acceptance" },
] as const;

const oracleTypeOptions = [
	{ value: "assertion", label: "Assertion" },
	{ value: "golden", label: "Golden (Reference)" },
	{ value: "metamorphic", label: "Metamorphic" },
	{ value: "property", label: "Property-Based" },
	{ value: "differential", label: "Differential" },
] as const;

const coverageTypeOptions = [
	{ value: "statement", label: "Statement" },
	{ value: "branch", label: "Branch" },
	{ value: "mcdc", label: "MC/DC" },
	{ value: "path", label: "Path" },
	{ value: "condition", label: "Condition" },
] as const;

const safetyLevelOptions = [
	{ value: "DAL-A", label: "DAL-A (Catastrophic)" },
	{ value: "DAL-B", label: "DAL-B (Hazardous)" },
	{ value: "DAL-C", label: "DAL-C (Major)" },
	{ value: "DAL-D", label: "DAL-D (Minor)" },
	{ value: "DAL-E", label: "DAL-E (No Effect)" },
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
		resolver: zodResolver(testItemSchema),
		defaultValues: {
			status: "todo",
			priority: "medium",
			test_type: "unit",
			is_critical_path: false,
		},
		mode: "onBlur",
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
							error={!!errors.title}
							placeholder="Enter test title"
							required
						/>

						<FormTextarea
							label="Description"
							name="description"
							register={register}
							error={!!errors.description}
							placeholder="Describe this test..."
							rows={3}
						/>

						<div className="grid gap-4 sm:grid-cols-2">
							<FormSelect
								label="Status"
								name="status"
								register={register}
								error={!!errors.status}
								options={statusOptions}
								required
							/>

							<FormSelect
								label="Priority"
								name="priority"
								register={register}
								error={!!errors.priority}
								options={priorityOptions}
								required
							/>
						</div>

						<FormInput
							label="Owner"
							name="owner"
							register={register}
							error={!!errors.owner}
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
								error={!!errors.test_type}
								options={testTypeOptions}
								required
							/>

							<FormInput
								label="Test Framework"
								name="test_framework"
								register={register}
								error={!!errors.test_framework}
								placeholder="e.g., Vitest, Jest, Pytest"
							/>
						</div>

						<div className="grid gap-4 sm:grid-cols-2">
							<FormInput
								label="Language"
								name="language"
								register={register}
								error={!!errors.language}
								placeholder="e.g., TypeScript, Python"
							/>

							<FormSelect
								label="Oracle Type"
								name="oracle_type"
								register={register}
								error={!!errors.oracle_type}
								options={oracleTypeOptions}
							/>
						</div>

						<div className="grid gap-4 sm:grid-cols-2">
							<FormSelect
								label="Coverage Type"
								name="coverage_type"
								register={register}
								error={!!errors.coverage_type}
								options={coverageTypeOptions}
							/>

							<FormSelect
								label="Safety Level (DO-178C)"
								name="safety_level"
								register={register}
								error={!!errors.safety_level}
								options={safetyLevelOptions}
							/>
						</div>

						<div className="grid gap-4 sm:grid-cols-2">
							<FormInput
								label="Expected Duration (ms)"
								name="expected_duration_ms"
								type="number"
								register={register}
								error={!!errors.expected_duration_ms}
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
