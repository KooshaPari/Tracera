import type React from "react";
import { useState, useCallback } from "react";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
	DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import {
	AlertCircle,
	Upload,
	Loader2,
	CheckCircle2,
	AlertTriangle,
	FileText,
} from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface ImportWizardProps {
	projectId: string;
	projectName: string;
	isOpen: boolean;
	onClose: () => void;
	onImport?: (file: File, strategy: ConflictStrategy) => Promise<void>;
}

type ConflictStrategy = "skip" | "replace" | "merge";

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
	conflicts?: Array<{
		type: string;
		severity: string;
		message: string;
	}>;
}

type ImportStep = "upload" | "validate" | "conflicts" | "confirm" | "complete";

export const ImportWizard: React.FC<ImportWizardProps> = ({
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
	const [importResult, setImportResult] = useState<any>(null);

	const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
		const selectedFile = e.target.files?.[0];
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
			const formData = new FormData();
			formData.append("file", file);

			const response = await fetch(
				`/api/v1/projects/${projectId}/equivalence/validate`,
				{
					method: "POST",
					body: formData,
				},
			);

			const data = await response.json();

			if (!response.ok) {
				setError(data.error || "Validation failed");
				setValidation(null);
				setStep("upload");
				return;
			}

			setValidation(data);
			setStep("validate");
		} catch (err) {
			setError(err instanceof Error ? err.message : "Validation failed");
		} finally {
			setIsLoading(false);
		}
	};

	const handleProceedToConflicts = () => {
		if (validation?.conflicts && validation.conflicts.length > 0) {
			setStep("conflicts");
		} else {
			setStep("confirm");
		}
	};

	const handleImport = async () => {
		if (!file) return;

		setIsLoading(true);
		setError(null);

		try {
			const formData = new FormData();
			formData.append("file", file);
			formData.append("strategy", conflictStrategy);

			if (onImport) {
				await onImport(file, conflictStrategy);
			} else {
				const response = await fetch(
					`/api/v1/projects/${projectId}/equivalence/import`,
					{
						method: "POST",
						body: formData,
					},
				);

				const data = await response.json();

				if (!response.ok) {
					setError(data.error || "Import failed");
					return;
				}

				setImportResult(data);
				setStep("complete");
			}
		} catch (err) {
			setError(err instanceof Error ? err.message : "Import failed");
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

	const renderUploadStep = () => (
		<div className="space-y-4">
			<div className="border-2 border-dashed rounded-lg p-8 text-center hover:border-blue-400 transition">
				<label htmlFor="file-input" className="cursor-pointer">
					<div className="flex flex-col items-center gap-2">
						<Upload className="h-8 w-8 text-gray-400" />
						<span className="font-semibold">
							Choose a file or drag and drop
						</span>
						<span className="text-sm text-gray-500">JSON or YAML format</span>
					</div>
					<input
						id="file-input"
						type="file"
						accept=".json,.yaml,.yml"
						onChange={handleFileSelect}
						className="hidden"
					/>
				</label>
			</div>

			{file && (
				<div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
					<FileText className="h-5 w-5 text-blue-600" />
					<div className="flex-1">
						<div className="font-medium text-sm">{file.name}</div>
						<div className="text-xs text-gray-600">
							{(file.size / 1024).toFixed(2)} KB
						</div>
					</div>
				</div>
			)}

			{error && (
				<Alert variant="destructive">
					<AlertCircle className="h-4 w-4" />
					<AlertDescription>{error}</AlertDescription>
				</Alert>
			)}
		</div>
	);

	const renderValidateStep = () => (
		<div className="space-y-4">
			{validation?.valid ? (
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
			)}

			<Tabs defaultValue="summary" className="w-full">
				<TabsList>
					<TabsTrigger value="summary">Summary</TabsTrigger>
					{validation?.errors && validation.errors.length > 0 && (
						<TabsTrigger value="errors" className="text-red-600">
							Errors ({validation.errors.length})
						</TabsTrigger>
					)}
					{validation?.warnings && validation.warnings.length > 0 && (
						<TabsTrigger value="warnings" className="text-yellow-600">
							Warnings ({validation.warnings.length})
						</TabsTrigger>
					)}
				</TabsList>

				<TabsContent value="summary" className="space-y-3">
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
							<div className="font-semibold text-lg">
								{validation?.summary.links}
							</div>
							<div className="text-xs text-gray-600">Links</div>
						</div>
					</div>
				</TabsContent>

				{validation?.errors && validation.errors.length > 0 && (
					<TabsContent
						value="errors"
						className="space-y-2 max-h-64 overflow-y-auto"
					>
						{validation.errors.map((err, i) => (
							<div
								key={i}
								className="text-sm border-l-4 border-red-400 pl-3 py-2"
							>
								<div className="font-medium text-red-700">{err.field}</div>
								<div className="text-gray-600">{err.message}</div>
							</div>
						))}
					</TabsContent>
				)}

				{validation?.warnings && validation.warnings.length > 0 && (
					<TabsContent
						value="warnings"
						className="space-y-2 max-h-64 overflow-y-auto"
					>
						{validation.warnings.map((warn, i) => (
							<div
								key={i}
								className="text-sm border-l-4 border-yellow-400 pl-3 py-2"
							>
								<div className="font-medium text-yellow-700">{warn.field}</div>
								<div className="text-gray-600">{warn.message}</div>
							</div>
						))}
					</TabsContent>
				)}
			</Tabs>
		</div>
	);

	const renderConflictsStep = () => (
		<div className="space-y-4">
			<Alert className="border-yellow-200 bg-yellow-50">
				<AlertTriangle className="h-4 w-4 text-yellow-600" />
				<AlertDescription className="text-yellow-800">
					{validation?.conflicts?.length || 0} conflicts detected with existing
					data
				</AlertDescription>
			</Alert>

			<div>
				<Label className="text-base font-semibold mb-3 block">
					Conflict Resolution Strategy
				</Label>
				<RadioGroup
					value={conflictStrategy}
					onValueChange={(v) => setConflictStrategy(v as ConflictStrategy)}
				>
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

	const renderConfirmStep = () => (
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

	const renderCompleteStep = () => (
		<div className="space-y-4">
			{importResult?.status === "success" ? (
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
						{importResult?.concepts_imported}
					</div>
					<div className="text-gray-600">Concepts imported</div>
				</div>
				<div className="rounded-lg bg-gray-50 p-3">
					<div className="font-semibold text-lg">
						{importResult?.projections_imported}
					</div>
					<div className="text-gray-600">Projections imported</div>
				</div>
				<div className="rounded-lg bg-gray-50 p-3">
					<div className="font-semibold text-lg">
						{importResult?.links_imported}
					</div>
					<div className="text-gray-600">Links imported</div>
				</div>
				<div className="rounded-lg bg-gray-50 p-3">
					<div className="font-semibold text-lg">
						{importResult?.errors?.length || 0}
					</div>
					<div className="text-gray-600">Errors</div>
				</div>
			</div>

			{importResult?.summary && (
				<div className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
					{importResult.summary}
				</div>
			)}
		</div>
	);

	return (
		<Dialog open={isOpen} onOpenChange={handleClose}>
			<DialogContent className="max-w-2xl">
				<DialogHeader>
					<DialogTitle>Import Equivalence Data</DialogTitle>
					<DialogDescription>
						Import equivalence data into {projectName}
					</DialogDescription>
				</DialogHeader>

				<div className="min-h-64">
					{step === "upload" && renderUploadStep()}
					{step === "validate" && renderValidateStep()}
					{step === "conflicts" && renderConflictsStep()}
					{step === "confirm" && renderConfirmStep()}
					{step === "complete" && renderCompleteStep()}
				</div>

				<DialogFooter>
					{step === "upload" && (
						<>
							<Button variant="outline" onClick={handleClose}>
								Cancel
							</Button>
							<Button
								onClick={handleValidate}
								disabled={!file || isLoading}
								className="gap-2"
							>
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
					)}

					{step === "validate" && (
						<>
							<Button variant="outline" onClick={() => setStep("upload")}>
								Back
							</Button>
							<Button
								onClick={handleProceedToConflicts}
								disabled={!validation?.valid}
							>
								Next
							</Button>
						</>
					)}

					{(step === "conflicts" || step === "confirm") && (
						<>
							<Button
								variant="outline"
								onClick={() =>
									setStep(step === "conflicts" ? "validate" : "conflicts")
								}
							>
								Back
							</Button>
							<Button
								onClick={
									step === "conflicts" ? () => setStep("confirm") : handleImport
								}
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
					)}

					{step === "complete" && <Button onClick={handleClose}>Close</Button>}
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
};
