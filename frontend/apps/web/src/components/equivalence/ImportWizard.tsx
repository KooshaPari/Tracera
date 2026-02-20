import type { ChangeEvent, FC, ReactNode } from 'react';

import { AlertCircle, AlertTriangle, CheckCircle2, FileText, Loader2, Upload } from 'lucide-react';
import { useState } from 'react';

import { clientCore } from '@/api/client-core';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const { getAuthHeaders } = clientCore;

const BYTES_PER_KB = 1024;
const SIZE_DECIMALS = 2;

type ImportStep = 'upload' | 'validate' | 'conflicts' | 'confirm' | 'complete';

export interface ImportWizardProps {
  projectId: string;
  projectName: string;
  isOpen: boolean;
  onClose: () => void;
  onImport?: ((file: File, strategy: ConflictStrategy) => Promise<void>) | undefined;
}

export type ConflictStrategy = 'skip' | 'replace' | 'merge';

interface ValidationError {
  field: string;
  message: string;
  index?: number | undefined;
}

const EMPTY_ERRORS: ValidationError[] = [];
const EMPTY_WARNINGS: ValidationError[] = [];

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
  status?: string | undefined;
  concepts_imported?: number | undefined;
  projections_imported?: number | undefined;
  links_imported?: number | undefined;
  errors?: unknown[] | undefined;
  summary?: string | undefined;
}

const formatFileSize = (bytes: number): string =>
  `${(bytes / BYTES_PER_KB).toFixed(SIZE_DECIMALS)} KB`;

const buildValidationKey = (item: ValidationError, index: number): string =>
  `${item.field}-${item.message}-${item.index ?? index}`;

const buildFormData = (file: File, strategy?: ConflictStrategy): FormData => {
  const formData = new FormData();
  formData.append('file', file);
  if (strategy) {
    formData.append('strategy', strategy);
  }
  return formData;
};

const parseErrorMessage = (data: unknown, fallback: string): string => {
  if (data && typeof data === 'object' && 'error' in data) {
    const errorValue = (data as { error?: unknown }).error;
    if (typeof errorValue === 'string') {
      return errorValue;
    }
  }
  return fallback;
};

const validateImportFile = async (projectId: string, file: File): Promise<ValidationResult> => {
  const response = await fetch(`/api/v1/projects/${projectId}/equivalence/validate`, {
    body: buildFormData(file),
    headers: getAuthHeaders(),
    method: 'POST',
  });
  const data = (await response.json()) as ValidationResult & { error?: string };
  if (!response.ok) {
    throw new Error(parseErrorMessage(data, 'Validation failed'));
  }
  return data;
};

const runImport = async (
  projectId: string,
  file: File,
  strategy: ConflictStrategy,
): Promise<ImportResult> => {
  const response = await fetch(`/api/v1/projects/${projectId}/equivalence/import`, {
    body: buildFormData(file, strategy),
    headers: getAuthHeaders(),
    method: 'POST',
  });
  const data = (await response.json()) as ImportResult & { error?: string };
  if (!response.ok) {
    throw new Error(parseErrorMessage(data, 'Import failed'));
  }
  return data;
};

type SetState<Value> = (value: Value) => void;
type SetStep = (value: ImportStep | ((prev: ImportStep) => ImportStep)) => void;

const createHandleFileSelect =
  (setFile: SetState<File | null>, setError: SetState<string | null>) =>
  (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0] ?? null;
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

const createHandleValidate =
  (params: {
    file: File | null;
    projectId: string;
    setError: SetState<string | null>;
    setIsLoading: SetState<boolean>;
    setStep: SetStep;
    setValidation: SetState<ValidationResult | null>;
  }) =>
  async () => {
    if (!params.file) {
      params.setError('Please select a file');
      return;
    }
    params.setIsLoading(true);
    params.setError(null);
    try {
      const result = await validateImportFile(params.projectId, params.file);
      params.setValidation(result);
      params.setStep('validate');
    } catch (validationError) {
      params.setError(
        validationError instanceof Error ? validationError.message : 'Validation failed',
      );
      params.setValidation(null);
      params.setStep('upload');
    } finally {
      params.setIsLoading(false);
    }
  };

const createHandleProceedToConflicts =
  (validation: ValidationResult | null, setStep: SetStep) => () => {
    if (validation?.conflicts?.length) {
      setStep('conflicts');
    } else {
      setStep('confirm');
    }
  };

const createHandleImport =
  (params: {
    conflictStrategy: ConflictStrategy;
    file: File | null;
    onImport?: ((file: File, strategy: ConflictStrategy) => Promise<void>) | undefined;
    projectId: string;
    setError: SetState<string | null>;
    setImportResult: SetState<ImportResult | null>;
    setIsLoading: SetState<boolean>;
    setStep: SetStep;
  }) =>
  async () => {
    if (!params.file) {
      return;
    }
    params.setIsLoading(true);
    params.setError(null);
    try {
      if (params.onImport) {
        await params.onImport(params.file, params.conflictStrategy);
      } else {
        const result = await runImport(params.projectId, params.file, params.conflictStrategy);
        params.setImportResult(result);
        params.setStep('complete');
      }
    } catch (importError) {
      params.setError(importError instanceof Error ? importError.message : 'Import failed');
    } finally {
      params.setIsLoading(false);
    }
  };

const createHandleClose =
  (params: {
    onClose: () => void;
    setError: SetState<string | null>;
    setFile: SetState<File | null>;
    setImportResult: SetState<ImportResult | null>;
    setStep: SetStep;
    setValidation: SetState<ValidationResult | null>;
  }) =>
  () => {
    params.setStep('upload');
    params.setFile(null);
    params.setError(null);
    params.setValidation(null);
    params.setImportResult(null);
    params.onClose();
  };

const createHandleStrategyChange =
  (setConflictStrategy: SetState<ConflictStrategy>) => (value: string) => {
    setConflictStrategy(value as ConflictStrategy);
  };

const createHandleBackFromConflicts = (setStep: SetStep) => () => {
  setStep((prevStep) => (prevStep === 'conflicts' ? 'validate' : 'conflicts'));
};

const buildBodyProps = (params: {
  conflictStrategy: ConflictStrategy;
  error: string | null;
  file: File | null;
  importResult: ImportResult | null;
  onFileSelect: (event: ChangeEvent<HTMLInputElement>) => void;
  onStrategyChange: (value: string) => void;
  projectName: string;
  step: ImportStep;
  validation: ValidationResult | null;
}): ImportWizardBodyProps => ({
  completeProps: { result: params.importResult },
  confirmProps: {
    conflictStrategy: params.conflictStrategy,
    projectName: params.projectName,
    validation: params.validation,
  },
  conflictProps: {
    conflictsCount: params.validation?.conflicts?.length ?? 0,
    conflictStrategy: params.conflictStrategy,
    onStrategyChange: params.onStrategyChange,
  },
  step: params.step,
  uploadProps: { error: params.error, file: params.file, onFileSelect: params.onFileSelect },
  validationProps: { validation: params.validation },
});

const buildFooterProps = (params: {
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
}): ImportFooterProps => ({
  isLoading: params.isLoading,
  isValid: params.isValid,
  onBackFromConflicts: params.onBackFromConflicts,
  onBackFromValidate: params.onBackFromValidate,
  onCancel: params.onCancel,
  onClose: params.onClose,
  onImport: params.onImport,
  onNextFromConflicts: params.onNextFromConflicts,
  onNextFromValidate: params.onNextFromValidate,
  onValidate: params.onValidate,
  step: params.step,
});

interface FileDropZoneProps {
  onFileSelect: (event: ChangeEvent<HTMLInputElement>) => void;
}

interface SelectedFileProps {
  file: File;
}

interface ErrorAlertProps {
  message: string;
}

interface UploadStepProps {
  error: string | null;
  file: File | null;
  onFileSelect: (event: ChangeEvent<HTMLInputElement>) => void;
}

interface ValidationStatusProps {
  validation: ValidationResult | null;
}

interface ValidationTabsProps {
  validation: ValidationResult | null;
}

interface ValidationListProps {
  items: ValidationError[];
  variant: 'errors' | 'warnings';
}

interface OptionalTabsTriggerProps {
  className?: string | undefined;
  label: string;
  show: boolean;
  value: string;
}

interface OptionalTabsContentProps {
  children: ReactNode;
  show: boolean;
  value: string;
}

interface ConflictStepProps {
  conflictStrategy: ConflictStrategy;
  conflictsCount: number;
  onStrategyChange: (value: string) => void;
}

interface ConfirmStepProps {
  conflictStrategy: ConflictStrategy;
  projectName: string;
  validation: ValidationResult | null;
}

interface CompleteStepProps {
  result: ImportResult | null;
}

interface ImportWizardBodyProps {
  step: ImportStep;
  uploadProps: UploadStepProps;
  validationProps: ValidationTabsProps;
  conflictProps: ConflictStepProps;
  confirmProps: ConfirmStepProps;
  completeProps: CompleteStepProps;
}

interface ImportFooterProps {
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
}

interface ImportWizardLayoutProps {
  bodyProps: ImportWizardBodyProps;
  footerProps: ImportFooterProps;
  isOpen: boolean;
  onClose: () => void;
  projectName: string;
}

interface ConflictOptionProps {
  description: string;
  id: string;
  label: string;
  value: ConflictStrategy;
}

interface ResultStatProps {
  label: string;
  value: number | undefined;
}

interface UploadFooterProps {
  isLoading: boolean;
  onCancel: () => void;
  onValidate: () => void;
}

interface ValidateFooterProps {
  isValid: boolean;
  onBack: () => void;
  onNext: () => void;
}

interface ConflictFooterProps {
  isLoading: boolean;
  onBack: () => void;
  onPrimary: () => void;
  primaryLabel: string;
}

interface CompleteFooterProps {
  onClose: () => void;
}

const FileDropZone: FC<FileDropZoneProps> = ({ onFileSelect }) => (
  <div className='rounded-lg border-2 border-dashed p-8 text-center transition hover:border-blue-400'>
    <label htmlFor='file-input' className='cursor-pointer'>
      <div className='flex flex-col items-center gap-2'>
        <Upload className='h-8 w-8 text-gray-400' />
        <span className='font-semibold'>Choose a file or drag and drop</span>
        <span className='text-sm text-gray-500'>JSON or YAML format</span>
      </div>
      <input
        id='file-input'
        type='file'
        accept='.json,.yaml,.yml'
        onChange={onFileSelect}
        className='hidden'
      />
    </label>
  </div>
);

const SelectedFile: FC<SelectedFileProps> = ({ file }) => (
  <div className='flex items-center gap-2 rounded-lg bg-blue-50 p-3'>
    <FileText className='h-5 w-5 text-blue-600' />
    <div className='flex-1'>
      <div className='text-sm font-medium'>{file.name}</div>
      <div className='text-xs text-gray-600'>{formatFileSize(file.size)}</div>
    </div>
  </div>
);

const ErrorAlert: FC<ErrorAlertProps> = ({ message }) => (
  <Alert variant='destructive'>
    <AlertCircle className='h-4 w-4' />
    <AlertDescription>{message}</AlertDescription>
  </Alert>
);

const UploadStep: FC<UploadStepProps> = ({ error, file, onFileSelect }) => (
  <div className='space-y-4'>
    <FileDropZone onFileSelect={onFileSelect} />
    {file && <SelectedFile file={file} />}
    {error && <ErrorAlert message={error} />}
  </div>
);

const ValidationStatus: FC<ValidationStatusProps> = ({ validation }) =>
  validation?.valid ? (
    <Alert className='border-green-200 bg-green-50'>
      <CheckCircle2 className='h-4 w-4 text-green-600' />
      <AlertDescription className='text-green-800'>File validation passed</AlertDescription>
    </Alert>
  ) : (
    <Alert variant='destructive'>
      <AlertCircle className='h-4 w-4' />
      <AlertDescription>{validation?.errors.length ?? 0} validation errors found</AlertDescription>
    </Alert>
  );

const ValidationSummary: FC<{ validation: ValidationResult | null }> = ({ validation }) => (
  <div className='grid grid-cols-3 gap-4'>
    <div className='rounded-lg bg-gray-50 p-3'>
      <div className='text-lg font-semibold'>{validation?.summary.concepts}</div>
      <div className='text-xs text-gray-600'>Concepts</div>
    </div>
    <div className='rounded-lg bg-gray-50 p-3'>
      <div className='text-lg font-semibold'>{validation?.summary.projections}</div>
      <div className='text-xs text-gray-600'>Projections</div>
    </div>
    <div className='rounded-lg bg-gray-50 p-3'>
      <div className='text-lg font-semibold'>{validation?.summary.links}</div>
      <div className='text-xs text-gray-600'>Links</div>
    </div>
  </div>
);

const ValidationList: FC<ValidationListProps> = ({ items, variant }) => (
  <div className='max-h-64 space-y-2 overflow-y-auto'>
    {items.map((item, index) => (
      <div
        key={buildValidationKey(item, index)}
        className={`border-l-4 py-2 pl-3 text-sm ${
          variant === 'errors' ? 'border-red-400' : 'border-yellow-400'
        }`}
      >
        <div className={`font-medium ${variant === 'errors' ? 'text-red-700' : 'text-yellow-700'}`}>
          {item.field}
        </div>
        <div className='text-gray-600'>{item.message}</div>
      </div>
    ))}
  </div>
);

const OptionalTabsTrigger: FC<OptionalTabsTriggerProps> = ({ className, label, show, value }) =>
  show ? (
    <TabsTrigger value={value} className={className}>
      {label}
    </TabsTrigger>
  ) : null;

const OptionalTabsContent: FC<OptionalTabsContentProps> = ({ children, show, value }) =>
  show ? <TabsContent value={value}>{children}</TabsContent> : null;

const ValidationTabs: FC<ValidationTabsProps> = ({ validation }) => (
  <Tabs defaultValue='summary' className='w-full'>
    <TabsList>
      <TabsTrigger value='summary'>Summary</TabsTrigger>
      <OptionalTabsTrigger
        show={Boolean((validation?.errors?.length ?? 0) > 0)}
        value='errors'
        className='text-red-600'
        label={`Errors (${validation?.errors.length ?? 0})`}
      />
      <OptionalTabsTrigger
        show={Boolean((validation?.warnings?.length ?? 0) > 0)}
        value='warnings'
        className='text-yellow-600'
        label={`Warnings (${validation?.warnings.length ?? 0})`}
      />
    </TabsList>
    <TabsContent value='summary' className='space-y-3'>
      <ValidationSummary validation={validation} />
    </TabsContent>
    <OptionalTabsContent show={Boolean((validation?.errors?.length ?? 0) > 0)} value='errors'>
      <ValidationList items={validation?.errors ?? EMPTY_ERRORS} variant='errors' />
    </OptionalTabsContent>
    <OptionalTabsContent show={Boolean((validation?.warnings?.length ?? 0) > 0)} value='warnings'>
      <ValidationList items={validation?.warnings ?? EMPTY_WARNINGS} variant='warnings' />
    </OptionalTabsContent>
  </Tabs>
);

const ValidateStep: FC<ValidationTabsProps> = ({ validation }) => (
  <div className='space-y-4'>
    <ValidationStatus validation={validation} />
    <ValidationTabs validation={validation} />
  </div>
);

const ConflictOption: FC<ConflictOptionProps> = ({ description, id, label, value }) => (
  <div className='flex items-start space-x-2'>
    <RadioGroupItem value={value} id={id} className='mt-1' />
    <div className='flex-1'>
      <Label htmlFor={id} className='cursor-pointer font-normal'>
        {label}
      </Label>
      <div className='text-sm text-gray-600'>{description}</div>
    </div>
  </div>
);

const ConflictStep: FC<ConflictStepProps> = ({
  conflictStrategy,
  conflictsCount,
  onStrategyChange,
}) => (
  <div className='space-y-4'>
    <Alert className='border-yellow-200 bg-yellow-50'>
      <AlertTriangle className='h-4 w-4 text-yellow-600' />
      <AlertDescription className='text-yellow-800'>
        {conflictsCount} conflicts detected with existing data
      </AlertDescription>
    </Alert>

    <div>
      <Label className='mb-3 block text-base font-semibold'>Conflict Resolution Strategy</Label>
      <RadioGroup value={conflictStrategy} onValueChange={onStrategyChange}>
        <div className='space-y-3'>
          <ConflictOption
            id='skip'
            value='skip'
            label='Skip conflicting items'
            description="Keep existing data, don't import conflicts"
          />
          <ConflictOption
            id='replace'
            value='replace'
            label='Replace existing data'
            description='Overwrite with imported data'
          />
          <ConflictOption
            id='merge'
            value='merge'
            label='Merge intelligently'
            description='Keep highest confidence, most recent data'
          />
        </div>
      </RadioGroup>
    </div>
  </div>
);

const ConfirmStep: FC<ConfirmStepProps> = ({ conflictStrategy, projectName, validation }) => (
  <div className='space-y-4'>
    <Alert>
      <AlertCircle className='h-4 w-4' />
      <AlertDescription>
        Ready to import {validation?.summary.concepts} concepts, {validation?.summary.projections}{' '}
        projections, and {validation?.summary.links} links.
      </AlertDescription>
    </Alert>

    <div className='space-y-2 rounded-lg bg-gray-50 p-4 text-sm'>
      <div>
        <span className='text-gray-600'>Strategy:</span>
        <span className='ml-2 font-semibold'>{conflictStrategy}</span>
      </div>
      <div>
        <span className='text-gray-600'>Target Project:</span>
        <span className='ml-2 font-semibold'>{projectName}</span>
      </div>
    </div>
  </div>
);

const ResultStat: FC<ResultStatProps> = ({ label, value }) => (
  <div className='rounded-lg bg-gray-50 p-3'>
    <div className='text-lg font-semibold'>{value}</div>
    <div className='text-gray-600'>{label}</div>
  </div>
);

const CompleteStep: FC<CompleteStepProps> = ({ result }) => (
  <div className='space-y-4'>
    {result?.status === 'success' ? (
      <Alert className='border-green-200 bg-green-50'>
        <CheckCircle2 className='h-4 w-4 text-green-600' />
        <AlertDescription className='text-green-800'>
          Import completed successfully
        </AlertDescription>
      </Alert>
    ) : (
      <Alert className='border-yellow-200 bg-yellow-50'>
        <AlertTriangle className='h-4 w-4 text-yellow-600' />
        <AlertDescription className='text-yellow-800'>
          Import completed with warnings
        </AlertDescription>
      </Alert>
    )}

    <div className='grid grid-cols-2 gap-4 text-sm'>
      <ResultStat label='Concepts imported' value={result?.concepts_imported} />
      <ResultStat label='Projections imported' value={result?.projections_imported} />
      <ResultStat label='Links imported' value={result?.links_imported} />
      <ResultStat label='Errors' value={result?.errors?.length ?? 0} />
    </div>

    {result?.summary ? (
      <div className='rounded-lg bg-gray-50 p-3 text-sm text-gray-600'>{result.summary}</div>
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
  if (step === 'upload') {
    return <UploadStep {...uploadProps} />;
  }
  if (step === 'validate') {
    return <ValidateStep {...validationProps} />;
  }
  if (step === 'conflicts') {
    return <ConflictStep {...conflictProps} />;
  }
  if (step === 'confirm') {
    return <ConfirmStep {...confirmProps} />;
  }
  return <CompleteStep {...completeProps} />;
};

const UploadFooter: FC<UploadFooterProps> = ({ isLoading, onCancel, onValidate }) => (
  <>
    <Button variant='outline' onClick={onCancel}>
      Cancel
    </Button>
    <Button onClick={onValidate} disabled={isLoading} className='gap-2'>
      {isLoading ? (
        <>
          <Loader2 className='h-4 w-4 animate-spin' />
          Validating...
        </>
      ) : (
        'Validate'
      )}
    </Button>
  </>
);

const ValidateFooter: FC<ValidateFooterProps> = ({ isValid, onBack, onNext }) => (
  <>
    <Button variant='outline' onClick={onBack}>
      Back
    </Button>
    <Button onClick={onNext} disabled={!isValid}>
      Next
    </Button>
  </>
);

const ConflictFooter: FC<ConflictFooterProps> = ({
  isLoading,
  onBack,
  onPrimary,
  primaryLabel,
}) => (
  <>
    <Button variant='outline' onClick={onBack}>
      Back
    </Button>
    <Button onClick={onPrimary} disabled={isLoading} className='gap-2'>
      {isLoading ? (
        <>
          <Loader2 className='h-4 w-4 animate-spin' />
          Importing...
        </>
      ) : (
        primaryLabel
      )}
    </Button>
  </>
);

const CompleteFooter: FC<CompleteFooterProps> = ({ onClose }) => (
  <Button onClick={onClose}>Close</Button>
);

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
}) => {
  const footerByStep: Record<ImportStep, ReactNode> = {
    complete: <CompleteFooter onClose={onClose} />,
    confirm: (
      <ConflictFooter
        isLoading={isLoading}
        onBack={onBackFromConflicts}
        onPrimary={onImport}
        primaryLabel='Import'
      />
    ),
    conflicts: (
      <ConflictFooter
        isLoading={isLoading}
        onBack={onBackFromConflicts}
        onPrimary={onNextFromConflicts}
        primaryLabel='Next'
      />
    ),
    upload: <UploadFooter isLoading={isLoading} onCancel={onCancel} onValidate={onValidate} />,
    validate: (
      <ValidateFooter isValid={isValid} onBack={onBackFromValidate} onNext={onNextFromValidate} />
    ),
  };

  return <DialogFooter>{footerByStep[step]}</DialogFooter>;
};

const ImportWizardLayout: FC<ImportWizardLayoutProps> = ({
  bodyProps,
  footerProps,
  isOpen,
  onClose,
  projectName,
}) => (
  <Dialog open={isOpen} onOpenChange={onClose}>
    <DialogContent className='max-w-2xl'>
      <DialogHeader>
        <DialogTitle>Import Equivalence Data</DialogTitle>
        <DialogDescription>Import equivalence data into {projectName}</DialogDescription>
      </DialogHeader>
      <div className='min-h-64'>
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
  const [step, setStep] = useState<ImportStep>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [conflictStrategy, setConflictStrategy] = useState<ConflictStrategy>('skip');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);
  const handleFileSelect = createHandleFileSelect(setFile, setError);
  const handleValidate = createHandleValidate({
    file,
    projectId,
    setError,
    setIsLoading,
    setStep,
    setValidation,
  });
  const handleProceedToConflicts = createHandleProceedToConflicts(validation, setStep);
  const handleImport = createHandleImport({
    conflictStrategy,
    file,
    onImport,
    projectId,
    setError,
    setImportResult,
    setIsLoading,
    setStep,
  });
  const handleClose = createHandleClose({
    onClose,
    setError,
    setFile,
    setImportResult,
    setStep,
    setValidation,
  });
  const handleStrategyChange = createHandleStrategyChange(setConflictStrategy);
  const handleBackFromValidate = () => {
    setStep('upload');
  };
  const handleBackFromConflicts = createHandleBackFromConflicts(setStep);
  const handleNextFromConflicts = () => {
    setStep('confirm');
  };
  const bodyProps = buildBodyProps({
    conflictStrategy,
    error,
    file,
    importResult,
    onFileSelect: handleFileSelect,
    onStrategyChange: handleStrategyChange,
    projectName,
    step,
    validation,
  });
  const footerProps = buildFooterProps({
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
  });
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
