import {
	AlertCircle,
	AlertTriangle,
	CheckCircle2,
	FileText,
	Loader2,
	Upload,
} from "lucide-react";
import type { ChangeEvent, FC } from "react";
import { useState } from "react";
import { clientCore } from "@/api/client-core";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const { getAuthHeaders } = clientCore;

const BYTES_PER_KB = 1024;
const SIZE_DECIMALS = 2;

type ImportStep = "upload" | "validate" | "conflicts" | "confirm" | "complete";

export interface ImportWizardProps {
	projectId: string;
	projectName: string;
	isOpen: boolean;
	onClose: () => void;
	onImport?: (file: File, strategy: ConflictStrategy) => Promise<void>;
}

export type ConflictStrategy = "skip" | "replace" | "merge";

interface ValidationError {
	field: string;
	message: string;
	index?: number;
}

interface ValidationResult {
	valid: boolean;
	errors: ValidationError[];
	warnings: ValidationError[];
	summary: {
		concepts: number;
		projections: number;
		links: number;
	};
	conflicts?: {
		type: string;
		severity: string;
		message: string;
	}[];
}

interface ImportResult {
	status?: string;
	concepts_imported?: number;
	projections_imported?: number;
	links_imported?: number;
	errors?: unknown[];
	summary?: string;
}

const formatFileSize = (bytes: number): string =>
	`${(bytes / BYTES_PER_KB).toFixed(SIZE_DECIMALS)} KB`;

const buildValidationKey = (item: ValidationError, index: number): string =>
	`${item.field}-${item.message}-${item.index ?? index}`;

const buildFormData = (file: File, strategy?: ConflictStrategy): FormData => {
	const formData = new FormData();
	formData.append("file", file);
	if (strategy) {
		formData.append("strategy", strategy);
	}
	return formData;
};

const parseErrorMessage = (data: unknown, fallback: string): string => {
	if (data && typeof data === "object" && "error" in data) {
		const errorValue = (data as { error?: unknown }).error;
		if (typeof errorValue === "string") {
			return errorValue;
		}
	}
	return fallback;
};

const validateImportFile = async (
	projectId: string,
	file: File,
): Promise<ValidationResult> => {
	const response = await fetch(
		`/api/v1/projects/${projectId}/equivalence/validate`,
		{
			body: buildFormData(file),
			headers: getAuthHeaders(),
			method: "POST",
		},
	);
	const data = (await response.json()) as ValidationResult & { error?: string };
	if (!response.ok) {
		throw new Error(parseErrorMessage(data, "Validation failed"));
	}
	return data;
};

const runImport = async (
	projectId: string,
	file: File,
	strategy: ConflictStrategy,
): Promise<ImportResult> => {
	const response = await fetch(
		`/api/v1/projects/${projectId}/equivalence/import`,
		{
			body: buildFormData(file, strategy),
			headers: getAuthHeaders(),
			method: "POST",
		},
	);
	const data = (await response.json()) as ImportResult & { error?: string };
	if (!response.ok) {
		throw new Error(parseErrorMessage(data, "Import failed"));
	}
	return data;
};

type FileDropZoneProps = {
	onFileSelect: (event: ChangeEvent<HTMLInputElement>) => void;
};

type SelectedFileProps = {
	file: File;
};

type ErrorAlertProps = {
	message: string;
};

type UploadStepProps = {
	error: string | null;
	file: File | null;
	onFileSelect: (event: ChangeEvent<HTMLInputElement>) => void;
};

type ValidationStatusProps = {
	validation: ValidationResult | null;
};

type ValidationTabsProps = {
	validation: ValidationResult | null;
};

type ValidationListProps = {
	items: ValidationError[];
	variant: "errors" | "warnings";
};

type ConflictStepProps = {
	conflictStrategy: ConflictStrategy;
	conflictsCount: number;
	onStrategyChange: (value: string) => void;
};

type ConfirmStepProps = {
	conflictStrategy: ConflictStrategy;
	projectName: string;
	validation: ValidationResult | null;
};

type CompleteStepProps = {
	result: ImportResult | null;
};

type ImportWizardBodyProps = {
	step: ImportStep;
	uploadProps: UploadStepProps;
	validationProps: ValidationTabsProps;
	conflictProps: ConflictStepProps;
	confirmProps: ConfirmStepProps;
	completeProps: CompleteStepProps;
};

type ImportFooterProps = {
	isLoading: boolean;
	isValid: boolean;
	onBackFromConflicts: () => void;
	onBackFromValidate: () => void;
	onCancel: () => void;
	onClose: () => void;
	onImport: () => void;
	onNextFromConflicts: () => void;
	onNextFromValidate: () => void;
	onValidate: () => void;
	step: ImportStep;
};

type ImportWizardLayoutProps = {
	bodyProps: ImportWizardBodyProps;
	footerProps: ImportFooterProps;
	isOpen: boolean;
	onClose: () => void;
	projectName: string;
};

const FileDropZone: FC<FileDropZoneProps> = ({ onFileSelect }) => (
	<div className="border-2 border-dashed rounded-lg p-8 text-center hover:border-blue-400 transition">
		<label htmlFor="file-input" className="cursor-pointer">
			<div className="flex flex-col items-center gap-2">
				<Upload className="h-8 w-8 text-gray-400" />
				<span className="font-semibold">Choose a file or drag and drop</span>
				<span className="text-sm text-gray-500">JSON or YAML format</span>
			</div>
			<input
				id="file-input"
				type="file"
				accept=".json,.yaml,.yml"
				onChange={onFileSelect}
				className="hidden"
			/>
		</label>
	</div>
);

const SelectedFile: FC<SelectedFileProps> = ({ file }) => (
	<div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
		<FileText className="h-5 w-5 text-blue-600" />
		<div className="flex-1">
			<div className="font-medium text-sm">{file.name}</div>
			<div className="text-xs text-gray-600">{formatFileSize(file.size)}</div>
		</div>
	</div>
);

const ErrorAlert: FC<ErrorAlertProps> = ({ message }) => (
	<Alert variant="destructive">
		<AlertCircle className="h-4 w-4" />
		<AlertDescription>{message}</AlertDescription>
	</Alert>
);

const UploadStep: FC<UploadStepProps> = ({ error, file, onFileSelect }) => (
	<div className="space-y-4">
		<FileDropZone onFileSelect={onFileSelect} />
		{file && <SelectedFile file={file} />}
		{error && <ErrorAlert message={error} />}
	</div>
);

const ValidationStatus: FC<ValidationStatusProps> = ({ validation }) =>
	validation?.valid ? (
		<Alert className="border-green-200 bg-green-50">
			<CheckCircle2 className="h-4 w-4 text-green-600" />
			<AlertDescription className="text-green-800">
				File validation passed
			</AlertDescription>
		</Alert>
	) : (
		<Alert variant="destructive">
			<AlertCircle className="h-4 w-4" />
			<AlertDescription>
				{validation?.errors.length || 0} validation errors found
			</AlertDescription>
		</Alert>
	);

const ValidationSummary: FC<{ validation: ValidationResult | null }> = ({
	validation,
}) => (
	<div className="grid grid-cols-3 gap-4">
		<div className="rounded-lg bg-gray-50 p-3">
			<div className="font-semibold text-lg">
				{validation?.summary.concepts}
			</div>
			<div className="text-xs text-gray-600">Concepts</div>
		</div>
		<div className="rounded-lg bg-gray-50 p-3">
			<div className="font-semibold text-lg">
				{validation?.summary.projections}
			</div>
			<div className="text-xs text-gray-600">Projections</div>
		</div>
		<div className="rounded-lg bg-gray-50 p-3">
			<div className="font-semibold text-lg">{validation?.summary.links}</div>
			<div className="text-xs text-gray-600">Links</div>
		</div>
	</div>
);

const ValidationList: FC<ValidationListProps> = ({ items, variant }) => (
	<div className="space-y-2 max-h-64 overflow-y-auto">
		{items.map((item, index) => (
			<div
				key={buildValidationKey(item, index)}
				className={`text-sm border-l-4 pl-3 py-2 ${
					variant === "errors" ? "border-red-400" : "border-yellow-400"
				}`}
			>
				<div
					className={`font-medium ${
						variant === "errors" ? "text-red-700" : "text-yellow-700"
					}`}
				>
					{item.field}
				</div>
				<div className="text-gray-600">{item.message}</div>
			</div>
		))}
	</div>
);

const ValidationTabs: FC<ValidationTabsProps> = ({ validation }) => (
	<Tabs defaultValue="summary" className="w-full">
		<TabsList>
			<TabsTrigger value="summary">Summary</TabsTrigger>
			{validation?.errors?.length ? (
				<TabsTrigger value="errors" className="text-red-600">
					Errors ({validation.errors.length})
				</TabsTrigger>
			) : null}
			{validation?.warnings?.length ? (
				<TabsTrigger value="warnings" className="text-yellow-600">
					Warnings ({validation.warnings.length})
				</TabsTrigger>
			) : null}
		</TabsList>
		<TabsContent value="summary" className="space-y-3">
			<ValidationSummary validation={validation} />
		</TabsContent>
		{validation?.errors?.length ? (
			<TabsContent value="errors">
				<ValidationList items={validation.errors} variant="errors" />
			</TabsContent>
		) : null}
		{validation?.warnings?.length ? (
			<TabsContent value="warnings">
				<ValidationList items={validation.warnings} variant="warnings" />
			</TabsContent>
		) : null}
	</Tabs>
);

const ValidateStep: FC<ValidationTabsProps> = ({ validation }) => (
	<div className="space-y-4">
		<ValidationStatus validation={validation} />
		<ValidationTabs validation={validation} />
	</div>
);

const ConflictStep: FC<ConflictStepProps> = ({
	conflictStrategy,
	conflictsCount,
	onStrategyChange,
}) => (
	<div className="space-y-4">
		<Alert className="border-yellow-200 bg-yellow-50">
			<AlertTriangle className="h-4 w-4 text-yellow-600" />
			<AlertDescription className="text-yellow-800">
				{conflictsCount} conflicts detected with existing data
			</AlertDescription>
		</Alert>

		<div>
			<Label className="text-base font-semibold mb-3 block">
				Conflict Resolution Strategy
			</Label>
			<RadioGroup value={conflictStrategy} onValueChange={onStrategyChange}>
				<div className="space-y-3">
					<div className="flex items-start space-x-2">
						<RadioGroupItem value="skip" id="skip" className="mt-1" />
						<div className="flex-1">
							<Label htmlFor="skip" className="font-normal cursor-pointer">
								Skip conflicting items
							</Label>
							<div className="text-sm text-gray-600">
								Keep existing data, don't import conflicts
							</div>
						</div>
					</div>
					<div className="flex items-start space-x-2">
						<RadioGroupItem value="replace" id="replace" className="mt-1" />
						<div className="flex-1">
							<Label htmlFor="replace" className="font-normal cursor-pointer">
								Replace existing data
							</Label>
							<div className="text-sm text-gray-600">
								Overwrite with imported data
							</div>
						</div>
					</div>
					<div className="flex items-start space-x-2">
						<RadioGroupItem value="merge" id="merge" className="mt-1" />
						<div className="flex-1">
							<Label htmlFor="merge" className="font-normal cursor-pointer">
								Merge intelligently
							</Label>
							<div className="text-sm text-gray-600">
								Keep highest confidence, most recent data
							</div>
						</div>
					</div>
				</div>
			</RadioGroup>
		</div>
	</div>
);

const ConfirmStep: FC<ConfirmStepProps> = ({
	conflictStrategy,
	projectName,
	validation,
}) => (
	<div className="space-y-4">
		<Alert>
			<AlertCircle className="h-4 w-4" />
			<AlertDescription>
				Ready to import {validation?.summary.concepts} concepts,{" "}
				{validation?.summary.projections} projections, and{" "}
				{validation?.summary.links} links.
			</AlertDescription>
		</Alert>

		<div className="rounded-lg bg-gray-50 p-4 space-y-2 text-sm">
			<div>
				<span className="text-gray-600">Strategy:</span>
				<span className="font-semibold ml-2">{conflictStrategy}</span>
			</div>
			<div>
				<span className="text-gray-600">Target Project:</span>
				<span className="font-semibold ml-2">{projectName}</span>
			</div>
		</div>
	</div>
);

const CompleteStep: FC<CompleteStepProps> = ({ result }) => (
	<div className="space-y-4">
		{result?.status === "success" ? (
			<Alert className="border-green-200 bg-green-50">
				<CheckCircle2 className="h-4 w-4 text-green-600" />
				<AlertDescription className="text-green-800">
					Import completed successfully
				</AlertDescription>
			</Alert>
		) : (
			<Alert className="border-yellow-200 bg-yellow-50">
				<AlertTriangle className="h-4 w-4 text-yellow-600" />
				<AlertDescription className="text-yellow-800">
					Import completed with warnings
				</AlertDescription>
			</Alert>
		)}

		<div className="grid grid-cols-2 gap-4 text-sm">
			<div className="rounded-lg bg-gray-50 p-3">
				<div className="font-semibold text-lg">
					{result?.concepts_imported}
				</div>
				<div className="text-gray-600">Concepts imported</div>
			</div>
			<div className="rounded-lg bg-gray-50 p-3">
				<div className="font-semibold text-lg">
					{result?.projections_imported}
				</div>
				<div className="text-gray-600">Projections imported</div>
			</div>
			<div className="rounded-lg bg-gray-50 p-3">
				<div className="font-semibold text-lg">
					{result?.links_imported}
				</div>
				<div className="text-gray-600">Links imported</div>
			</div>
			<div className="rounded-lg bg-gray-50 p-3">
				<div className="font-semibold text-lg">
					{result?.errors?.length || 0}
				</div>
				<div className="text-gray-600">Errors</div>
			</div>
		</div>

		{result?.summary ? (
			<div className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
				{result.summary}
			</div>
		) : null}
	</div>
);

const ImportWizardBody: FC<ImportWizardBodyProps> = ({
	step,
	uploadProps,
	validationProps,
	conflictProps,
	confirmProps,
	completeProps,
}) => {
	if (step === "upload") {
		return <UploadStep {...uploadProps} />;
	}
	if (step === "validate") {
		return <ValidateStep {...validationProps} />;
	}
	if (step === "conflicts") {
		return <ConflictStep {...conflictProps} />;
	}
	if (step === "confirm") {
		return <ConfirmStep {...confirmProps} />;
	}
	return <CompleteStep {...completeProps} />;
};

const ImportFooter: FC<ImportFooterProps> = ({
	isLoading,
	isValid,
	onBackFromConflicts,
	onBackFromValidate,
	onCancel,
	onClose,
	onImport,
	onNextFromConflicts,
	onNextFromValidate,
	onValidate,
	step,
}) => (
	<DialogFooter>
		{step === "upload" ? (
			<>
				<Button variant="outline" onClick={onCancel}>
					Cancel
				</Button>
				<Button onClick={onValidate} disabled={isLoading} className="gap-2">
					{isLoading ? (
						<>
							<Loader2 className="h-4 w-4 animate-spin" />
							Validating...
						</>
					) : (
						"Validate"
					)}
				</Button>
			</>
		) : null}
		{step === "validate" ? (
			<>
				<Button variant="outline" onClick={onBackFromValidate}>
					Back
				</Button>
				<Button onClick={onNextFromValidate} disabled={!isValid}>
					Next
				</Button>
			</>
		) : null}
		{step === "conflicts" || step === "confirm" ? (
			<>
				<Button variant="outline" onClick={onBackFromConflicts}>
					Back
				</Button>
				<Button
					onClick={step === "conflicts" ? onNextFromConflicts : onImport}
					disabled={isLoading}
					className="gap-2"
				>
					{isLoading ? (
						<>
							<Loader2 className="h-4 w-4 animate-spin" />
							Importing...
						</>
					) : step === "conflicts" ? (
						"Next"
					) : (
						"Import"
					)}
				</Button>
			</>
		) : null}
		{step === "complete" ? <Button onClick={onClose}>Close</Button> : null}
	</DialogFooter>
);

const ImportWizardLayout: FC<ImportWizardLayoutProps> = ({
	bodyProps,
	footerProps,
	isOpen,
	onClose,
	projectName,
}) => (
	<Dialog open={isOpen} onOpenChange={onClose}>
		<DialogContent className="max-w-2xl">
			<DialogHeader>
				<DialogTitle>Import Equivalence Data</DialogTitle>
				<DialogDescription>
					Import equivalence data into {projectName}
				</DialogDescription>
			</DialogHeader>
			<div className="min-h-64">
				<ImportWizardBody {...bodyProps} />
			</div>
			<ImportFooter {...footerProps} />
		</DialogContent>
	</Dialog>
);

export const ImportWizard: FC<ImportWizardProps> = ({
	projectId,
	projectName,
	isOpen,
	onClose,
	onImport,
}) => {
	const [step, setStep] = useState<ImportStep>("upload");
	const [file, setFile] = useState<File | null>(null);
	const [conflictStrategy, setConflictStrategy] =
		useState<ConflictStrategy>("skip");
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [validation, setValidation] = useState<ValidationResult | null>(null);
	const [importResult, setImportResult] = useState<ImportResult | null>(null);

	const handleFileSelect = (event: ChangeEvent<HTMLInputElement>) => {
		const selectedFile = event.target.files?.[0] ?? null;
		if (selectedFile) {
			setFile(selectedFile);
			setError(null);
		}
	};

	const handleValidate = async () => {
		if (!file) {
			setError("Please select a file");
			return;
		}
		setIsLoading(true);
		setError(null);
		try {
			const result = await validateImportFile(projectId, file);
			setValidation(result);
			setStep("validate");
		} catch (validationError) {
			setError(
				validationError instanceof Error
					? validationError.message
					: "Validation failed",
			);
			setValidation(null);
			setStep("upload");
		} finally {
			setIsLoading(false);
		}
	};

	const handleProceedToConflicts = () => {
		if (validation?.conflicts?.length) {
			setStep("conflicts");
		} else {
			setStep("confirm");
		}
	};

	const handleImport = async () => {
		if (!file) {
			return;
		}
		setIsLoading(true);
		setError(null);
		try {
			if (onImport) {
				await onImport(file, conflictStrategy);
			} else {
				const result = await runImport(projectId, file, conflictStrategy);
				setImportResult(result);
				setStep("complete");
			}
		} catch (importError) {
			setError(
				importError instanceof Error ? importError.message : "Import failed",
			);
		} finally {
			setIsLoading(false);
		}
	};

	const handleClose = () => {
		setStep("upload");
		setFile(null);
		setError(null);
		setValidation(null);
		setImportResult(null);
		onClose();
	};

	const handleStrategyChange = (value: string) => {
		setConflictStrategy(value as ConflictStrategy);
	};

	const handleBackFromValidate = () => {
		setStep("upload");
	};

	const handleBackFromConflicts = () => {
		setStep((prevStep) =>
			prevStep === "conflicts" ? "validate" : "conflicts",
		);
	};

	const handleNextFromConflicts = () => {
		setStep("confirm");
	};

	const bodyProps = {
		step,
		uploadProps: { error, file, onFileSelect: handleFileSelect },
		validationProps: { validation },
		conflictProps: {
			conflictStrategy,
			conflictsCount: validation?.conflicts?.length ?? 0,
			onStrategyChange: handleStrategyChange,
		},
		confirmProps: { conflictStrategy, projectName, validation },
		completeProps: { result: importResult },
	};

	const footerProps = {
		isLoading,
		isValid: Boolean(validation?.valid),
		onBackFromConflicts: handleBackFromConflicts,
		onBackFromValidate: handleBackFromValidate,
		onCancel: handleClose,
		onClose: handleClose,
		onImport: handleImport,
		onNextFromConflicts: handleNextFromConflicts,
		onNextFromValidate: handleProceedToConflicts,
		onValidate: handleValidate,
		step,
	};

	return (
		<ImportWizardLayout
			bodyProps={bodyProps}
			footerProps={footerProps}
			isOpen={isOpen}
			onClose={handleClose}
			projectName={projectName}
		/>
	);
};
