import type { FC } from 'react';

import { AlertCircle, Download, Loader2 } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import { clientCore } from '@/api/client-core';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
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
import { logger } from '@/lib/logger';

const { getAuthHeaders } = clientCore;

const BYTES_PER_KB = 1024;
const EMBEDDING_BYTES_PER_CONCEPT = 12_800;
const ESTIMATED_BYTES_PER_ITEM = 500;
const SIZE_DECIMALS = 2;
const SIZE_UNITS = ['B', 'KB', 'MB', 'GB'] as const;

type ExportStep = 'options' | 'review';

type ExportFormat = 'json' | 'yaml';

export interface ExportWizardProps {
  projectId: string;
  projectName: string;
  isOpen: boolean;
  onClose: () => void;
  onExport?: (config: ExportConfig) => Promise<void>;
}

export interface ExportConfig {
  format: ExportFormat;
  includeEmbeddings: boolean;
  includeMetadata: boolean;
  includeItemInfo: boolean;
  pretty: boolean;
  filters?: {
    status?: string;
    minConfidence?: number;
    perspective?: string;
  };
}

interface ExportStats {
  concepts: number;
  projections: number;
  links: number;
  perspectives: number;
  averageConfidence: number;
}

const toBoolean = (checked: boolean | 'indeterminate'): boolean => Boolean(checked);

const formatSize = (bytes: number): string => {
  let size = bytes;
  let unitIndex = 0;
  while (size >= BYTES_PER_KB && unitIndex < SIZE_UNITS.length - 1) {
    size /= BYTES_PER_KB;
    unitIndex += 1;
  }
  return `${size.toFixed(SIZE_DECIMALS)} ${SIZE_UNITS[unitIndex]}`;
};

const downloadExportBlob = (blob: Blob, filename: string): void => {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};

const buildExportUrl = (projectId: string, config: ExportConfig): string => {
  const params = new URLSearchParams({
    format: config.format,
    include_embeddings: String(config.includeEmbeddings),
    include_metadata: String(config.includeMetadata),
  });
  return `/api/v1/projects/${projectId}/equivalence/export?${params.toString()}`;
};

const fetchExportStats = async (projectId: string): Promise<ExportStats> => {
  const response = await fetch(`/api/v1/projects/${projectId}/equivalence/export-statistics`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error('Failed to fetch statistics');
  }
  return (await response.json()) as ExportStats;
};

const runDefaultExport = async (
  projectId: string,
  projectName: string,
  config: ExportConfig,
): Promise<void> => {
  const response = await fetch(buildExportUrl(projectId, config), {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error('Export failed');
  }
  const blob = await response.blob();
  const date = new Date().toISOString().split('T')[0];
  downloadExportBlob(blob, `equivalence-${projectName}-${date}.${config.format}`);
};

const useExportStats = (isOpen: boolean, projectId: string) => {
  const [stats, setStats] = useState<ExportStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    if (!isOpen || stats) {
      return () => {
        isMounted = false;
      };
    }
    fetchExportStats(projectId)
      .then((data) => {
        if (isMounted) {
          setStats(data);
        }
      })
      .catch((fetchError) => {
        logger.error('Failed to fetch export statistics:', fetchError);
        if (isMounted) {
          setError('Failed to load export statistics');
        }
      });
    return () => {
      isMounted = false;
    };
  }, [isOpen, projectId, stats]);

  return { error, setError, stats };
};

const useExportOptions = () => {
  const [format, setFormat] = useState<ExportFormat>('json');
  const [includeEmbeddings, setIncludeEmbeddings] = useState(false);
  const [includeMetadata, setIncludeMetadata] = useState(true);
  const [includeItemInfo, setIncludeItemInfo] = useState(true);
  const [pretty, setPretty] = useState(true);

  const handleFormatChange = (value: string) => {
    setFormat(value as ExportFormat);
  };

  const handleEmbeddingsChange = (checked: boolean | 'indeterminate') => {
    setIncludeEmbeddings(toBoolean(checked));
  };

  const handleItemInfoChange = (checked: boolean | 'indeterminate') => {
    setIncludeItemInfo(toBoolean(checked));
  };

  const handleMetadataChange = (checked: boolean | 'indeterminate') => {
    setIncludeMetadata(toBoolean(checked));
  };

  const handlePrettyChange = (checked: boolean | 'indeterminate') => {
    setPretty(toBoolean(checked));
  };

  return {
    format,
    handleEmbeddingsChange,
    handleFormatChange,
    handleItemInfoChange,
    handleMetadataChange,
    handlePrettyChange,
    includeEmbeddings,
    includeItemInfo,
    includeMetadata,
    pretty,
  };
};

const useExportStep = () => {
  const [step, setStep] = useState<ExportStep>('options');
  const goToOptions = () => {
    setStep('options');
  };
  const goToReview = () => {
    setStep('review');
  };
  return { goToOptions, goToReview, step };
};

const useEstimatedSize = (stats: ExportStats | null, includeEmbeddings: boolean): string =>
  useMemo(() => {
    if (!stats) {
      return 'Calculating...';
    }
    const baseSize = (stats.concepts + stats.projections + stats.links) * ESTIMATED_BYTES_PER_ITEM;
    const embeddingsSize = includeEmbeddings ? stats.concepts * EMBEDDING_BYTES_PER_CONCEPT : 0;
    return formatSize(baseSize + embeddingsSize);
  }, [includeEmbeddings, stats]);

const useExportActions = (params: {
  config: ExportConfig;
  onClose: () => void;
  onExport: ExportWizardProps['onExport'];
  projectId: string;
  projectName: string;
  resetStep: () => void;
  setError: (value: string | null) => void;
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleClose = () => {
    params.resetStep();
    params.setError(null);
    params.onClose();
  };

  const handleExport = async () => {
    setIsLoading(true);
    params.setError(null);
    try {
      if (params.onExport) {
        await params.onExport(params.config);
      } else {
        await runDefaultExport(params.projectId, params.projectName, params.config);
      }
      params.onClose();
    } catch (exportError) {
      params.setError(exportError instanceof Error ? exportError.message : 'Export failed');
    } finally {
      setIsLoading(false);
    }
  };

  return { handleClose, handleExport, isLoading };
};

interface FormatSelectorProps {
  format: ExportFormat;
  onChange: (value: string) => void;
}

interface CheckboxRowProps {
  id: string;
  label: string;
  checked: boolean;
  onChange: (checked: boolean | 'indeterminate') => void;
}

interface OptionsSectionProps {
  includeEmbeddings: boolean;
  includeItemInfo: boolean;
  includeMetadata: boolean;
  pretty: boolean;
  onEmbeddingsChange: (checked: boolean | 'indeterminate') => void;
  onItemInfoChange: (checked: boolean | 'indeterminate') => void;
  onMetadataChange: (checked: boolean | 'indeterminate') => void;
  onPrettyChange: (checked: boolean | 'indeterminate') => void;
}

interface OptionsStepProps {
  error: string | null;
  stats: ExportStats | null;
  format: ExportFormat;
  includeEmbeddings: boolean;
  includeItemInfo: boolean;
  includeMetadata: boolean;
  pretty: boolean;
  estimatedSize: string;
  onFormatChange: (value: string) => void;
  onEmbeddingsChange: (checked: boolean | 'indeterminate') => void;
  onItemInfoChange: (checked: boolean | 'indeterminate') => void;
  onMetadataChange: (checked: boolean | 'indeterminate') => void;
  onPrettyChange: (checked: boolean | 'indeterminate') => void;
}

interface ReviewOptionsListProps {
  includeEmbeddings: boolean;
  includeItemInfo: boolean;
  includeMetadata: boolean;
  pretty: boolean;
}

interface ReviewStepProps {
  format: ExportFormat;
  estimatedSize: string;
  includeEmbeddings: boolean;
  includeItemInfo: boolean;
  includeMetadata: boolean;
  pretty: boolean;
}

interface ExportFooterProps {
  step: ExportStep;
  isLoading: boolean;
  onBack: () => void;
  onClose: () => void;
  onExport: () => void;
  onNext: () => void;
}

interface ExportWizardBodyProps {
  optionsProps: OptionsStepProps;
  reviewProps: ReviewStepProps;
  step: ExportStep;
}

interface ExportWizardLayoutProps {
  bodyProps: ExportWizardBodyProps;
  footerProps: ExportFooterProps;
  isOpen: boolean;
  onClose: () => void;
  projectName: string;
}

interface ExportOptionsState {
  format: ExportFormat;
  includeEmbeddings: boolean;
  includeItemInfo: boolean;
  includeMetadata: boolean;
  pretty: boolean;
  handleEmbeddingsChange: (checked: boolean | 'indeterminate') => void;
  handleFormatChange: (value: string) => void;
  handleItemInfoChange: (checked: boolean | 'indeterminate') => void;
  handleMetadataChange: (checked: boolean | 'indeterminate') => void;
  handlePrettyChange: (checked: boolean | 'indeterminate') => void;
}

const buildBodyProps = (params: {
  error: string | null;
  estimatedSize: string;
  options: ExportOptionsState;
  stats: ExportStats | null;
  step: ExportStep;
}): ExportWizardBodyProps => ({
  optionsProps: {
    error: params.error,
    estimatedSize: params.estimatedSize,
    format: params.options.format,
    includeEmbeddings: params.options.includeEmbeddings,
    includeItemInfo: params.options.includeItemInfo,
    includeMetadata: params.options.includeMetadata,
    onEmbeddingsChange: params.options.handleEmbeddingsChange,
    onFormatChange: params.options.handleFormatChange,
    onItemInfoChange: params.options.handleItemInfoChange,
    onMetadataChange: params.options.handleMetadataChange,
    onPrettyChange: params.options.handlePrettyChange,
    pretty: params.options.pretty,
    stats: params.stats,
  },
  reviewProps: {
    estimatedSize: params.estimatedSize,
    format: params.options.format,
    includeEmbeddings: params.options.includeEmbeddings,
    includeItemInfo: params.options.includeItemInfo,
    includeMetadata: params.options.includeMetadata,
    pretty: params.options.pretty,
  },
  step: params.step,
});

const buildFooterProps = (params: {
  isLoading: boolean;
  onBack: () => void;
  onClose: () => void;
  onExport: () => void;
  onNext: () => void;
  step: ExportStep;
}): ExportFooterProps => ({
  isLoading: params.isLoading,
  onBack: params.onBack,
  onClose: params.onClose,
  onExport: params.onExport,
  onNext: params.onNext,
  step: params.step,
});

const SummaryItem: FC<{ label: string; value: number }> = ({ label, value }) => (
  <div>
    <div className='font-medium'>{value}</div>
    <div className='text-xs'>{label}</div>
  </div>
);

const ExportSummary: FC<{ stats: ExportStats }> = ({ stats }) => (
  <div className='rounded-lg border border-blue-200 bg-blue-50 p-4'>
    <h3 className='mb-2 font-semibold text-blue-900'>Export Summary</h3>
    <div className='grid grid-cols-2 gap-4 text-sm text-blue-800'>
      <SummaryItem label='Canonical Concepts' value={stats.concepts} />
      <SummaryItem label='Projections' value={stats.projections} />
      <SummaryItem label='Equivalence Links' value={stats.links} />
      <SummaryItem label='Perspectives' value={stats.perspectives} />
    </div>
  </div>
);

const FormatSelector: FC<FormatSelectorProps> = ({ format, onChange }) => (
  <div>
    <Label className='mb-3 block text-base font-semibold'>Format</Label>
    <RadioGroup value={format} onValueChange={onChange}>
      <div className='mb-2 flex items-center space-x-2'>
        <RadioGroupItem value='json' id='json' />
        <Label htmlFor='json' className='cursor-pointer font-normal'>
          JSON - Universal format with detailed structure
        </Label>
      </div>
      <div className='flex items-center space-x-2'>
        <RadioGroupItem value='yaml' id='yaml' />
        <Label htmlFor='yaml' className='cursor-pointer font-normal'>
          YAML - Human-readable format
        </Label>
      </div>
    </RadioGroup>
  </div>
);

const CheckboxRow: FC<CheckboxRowProps> = ({ id, label, checked, onChange }) => (
  <div className='flex items-center space-x-2'>
    <Checkbox
      id={id}
      checked={checked}
      onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
        onChange(e.target.checked);
      }}
    />
    <Label htmlFor={id} className='cursor-pointer font-normal'>
      {label}
    </Label>
  </div>
);

const OptionsSection: FC<OptionsSectionProps> = ({
  includeEmbeddings,
  includeItemInfo,
  includeMetadata,
  onEmbeddingsChange,
  onItemInfoChange,
  onMetadataChange,
  onPrettyChange,
  pretty,
}) => (
  <div className='space-y-3'>
    <Label className='text-base font-semibold'>Options</Label>
    <div className='space-y-2'>
      <CheckboxRow
        id='embeddings'
        label='Include embeddings (larger file size)'
        checked={includeEmbeddings}
        onChange={onEmbeddingsChange}
      />
      <CheckboxRow
        id='metadata'
        label='Include metadata and evidence'
        checked={includeMetadata}
        onChange={onMetadataChange}
      />
      <CheckboxRow
        id='iteminfo'
        label='Include item information (titles, types)'
        checked={includeItemInfo}
        onChange={onItemInfoChange}
      />
      <CheckboxRow
        id='pretty'
        label='Pretty print (larger but human-readable)'
        checked={pretty}
        onChange={onPrettyChange}
      />
    </div>
  </div>
);

const EstimatedSizeRow: FC<{ size: string }> = ({ size }) => (
  <div className='border-t pt-2 pb-2'>
    <div className='flex items-center justify-between'>
      <span className='text-sm text-gray-600'>Estimated file size:</span>
      <span className='font-semibold'>{size}</span>
    </div>
  </div>
);

const OptionsStep: FC<OptionsStepProps> = ({
  error,
  stats,
  format,
  includeEmbeddings,
  includeItemInfo,
  includeMetadata,
  pretty,
  estimatedSize,
  onFormatChange,
  onEmbeddingsChange,
  onItemInfoChange,
  onMetadataChange,
  onPrettyChange,
}) => (
  <div className='space-y-6'>
    {error && (
      <Alert variant='destructive'>
        <AlertCircle className='h-4 w-4' />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )}
    {stats && <ExportSummary stats={stats} />}
    <div className='space-y-4'>
      <FormatSelector format={format} onChange={onFormatChange} />
      <OptionsSection
        includeEmbeddings={includeEmbeddings}
        includeItemInfo={includeItemInfo}
        includeMetadata={includeMetadata}
        onEmbeddingsChange={onEmbeddingsChange}
        onItemInfoChange={onItemInfoChange}
        onMetadataChange={onMetadataChange}
        onPrettyChange={onPrettyChange}
        pretty={pretty}
      />
      <EstimatedSizeRow size={estimatedSize} />
    </div>
  </div>
);

const ReviewOptionsList: FC<ReviewOptionsListProps> = ({
  includeEmbeddings,
  includeItemInfo,
  includeMetadata,
  pretty,
}) => (
  <ul className='list-inside list-disc space-y-1 text-sm'>
    {includeEmbeddings && <li>Embeddings</li>}
    {includeMetadata && <li>Metadata & Evidence</li>}
    {includeItemInfo && <li>Item Information</li>}
    {pretty && <li>Pretty Print</li>}
  </ul>
);

const ReviewStep: FC<ReviewStepProps> = ({
  format,
  estimatedSize,
  includeEmbeddings,
  includeItemInfo,
  includeMetadata,
  pretty,
}) => (
  <div className='space-y-4'>
    <div className='space-y-3 rounded-lg bg-gray-50 p-4'>
      <div className='grid grid-cols-2 gap-4 text-sm'>
        <div>
          <span className='text-gray-600'>Format:</span>
          <span className='ml-2 font-semibold'>{format.toUpperCase()}</span>
        </div>
        <div>
          <span className='text-gray-600'>File size:</span>
          <span className='ml-2 font-semibold'>{estimatedSize}</span>
        </div>
      </div>
      <div className='border-t pt-3'>
        <div className='mb-2 text-sm text-gray-600'>Options enabled:</div>
        <ReviewOptionsList
          includeEmbeddings={includeEmbeddings}
          includeItemInfo={includeItemInfo}
          includeMetadata={includeMetadata}
          pretty={pretty}
        />
      </div>
    </div>
    <Alert>
      <AlertCircle className='h-4 w-4' />
      <AlertDescription>
        The export file will contain all equivalence data for this project. You can import it later
        into another project or keep it as a backup.
      </AlertDescription>
    </Alert>
  </div>
);

const ExportFooter: FC<ExportFooterProps> = ({
  step,
  isLoading,
  onBack,
  onClose,
  onExport,
  onNext,
}) => (
  <DialogFooter>
    {step === 'options' ? (
      <>
        <Button variant='outline' onClick={onClose}>
          Cancel
        </Button>
        <Button onClick={onNext} disabled={isLoading}>
          Next
        </Button>
      </>
    ) : (
      <>
        <Button variant='outline' onClick={onBack} disabled={isLoading}>
          Back
        </Button>
        <Button onClick={onExport} disabled={isLoading} className='gap-2'>
          {isLoading ? (
            <>
              <Loader2 className='h-4 w-4 animate-spin' />
              Exporting...
            </>
          ) : (
            <>
              <Download className='h-4 w-4' />
              Export
            </>
          )}
        </Button>
      </>
    )}
  </DialogFooter>
);

const ExportWizardBody: FC<ExportWizardBodyProps> = ({ optionsProps, reviewProps, step }) =>
  step === 'options' ? <OptionsStep {...optionsProps} /> : <ReviewStep {...reviewProps} />;

const ExportWizardLayout: FC<ExportWizardLayoutProps> = ({
  bodyProps,
  footerProps,
  isOpen,
  onClose,
  projectName,
}) => (
  <Dialog open={isOpen} onOpenChange={onClose}>
    <DialogContent className='max-w-2xl'>
      <DialogHeader>
        <DialogTitle>Export Equivalence Data</DialogTitle>
        <DialogDescription>
          Export canonical concepts, projections, and equivalence links from {projectName}
        </DialogDescription>
      </DialogHeader>
      <ExportWizardBody {...bodyProps} />
      <ExportFooter {...footerProps} />
    </DialogContent>
  </Dialog>
);

export const ExportWizard: FC<ExportWizardProps> = ({
  projectId,
  projectName,
  isOpen,
  onClose,
  onExport,
}) => {
  const { stats, error, setError } = useExportStats(isOpen, projectId);
  const { step, goToOptions, goToReview } = useExportStep();
  const options = useExportOptions();
  const estimatedSize = useEstimatedSize(stats, options.includeEmbeddings);
  const config: ExportConfig = {
    format: options.format,
    includeEmbeddings: options.includeEmbeddings,
    includeItemInfo: options.includeItemInfo,
    includeMetadata: options.includeMetadata,
    pretty: options.pretty,
  };
  const { handleClose, handleExport, isLoading } = useExportActions({
    config,
    onClose,
    onExport,
    projectId,
    projectName,
    resetStep: goToOptions,
    setError,
  });
  const bodyProps = buildBodyProps({ error, estimatedSize, options, stats, step });
  const footerProps = buildFooterProps({
    isLoading,
    onBack: goToOptions,
    onClose: handleClose,
    onExport: handleExport,
    onNext: goToReview,
    step,
  });
  return (
    <ExportWizardLayout
      bodyProps={bodyProps}
      footerProps={footerProps}
      isOpen={isOpen}
      onClose={handleClose}
      projectName={projectName}
    />
  );
};
