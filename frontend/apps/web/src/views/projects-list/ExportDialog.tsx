import { useMutation } from '@tanstack/react-query';
import { useCallback, useMemo, useState } from 'react';
import { toast } from 'sonner';

import type { Project } from '@tracertm/types';

import { exportImportApi } from '@/api/endpoints';
import { getProjectDisplayName } from '@/lib/project-name-utils';
import {
  Button,
  Dialog,
  DialogContent,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui';

type ExportFormat = 'json' | 'csv' | 'full';

interface ExportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projects: Project[];
}

const EMPTY_STRING = '';

const getExportSuccessMessage = (format: ExportFormat): string => {
  if (format === 'full') {
    return 'Full project export completed';
  }
  return 'Registry backup completed';
};

const getExportExtension = (format: ExportFormat): string => {
  if (format === 'csv') {
    return 'csv';
  }
  return 'json';
};

const getExportTargetId = (
  selectedId: string | undefined,
  projects: Project[],
): string | undefined => {
  if (typeof selectedId === 'string' && selectedId.length > 0) {
    return selectedId;
  }
  if (projects.length > 0) {
    return projects[0]?.id;
  }
  return undefined;
};

interface ExportDialogModel {
  exportFormat: ExportFormat;
  exportTargetId: string | undefined;
  isExportDisabled: boolean;
  isExporting: boolean;
  onExport: () => void;
  onFormatChange: (value: ExportFormat) => void;
  onProjectChange: (value: string) => void;
  projectSelectValue: string;
}

const buildExportDownloadName = (format: ExportFormat, extension: string): string => {
  const [day] = new Date().toISOString().split('T');
  return `tracertm-export-${format}-${day}.${extension}`;
};

const downloadBlob = (blob: Blob, filename: string): void => {
  const url = globalThis.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  globalThis.URL.revokeObjectURL(url);
  anchor.remove();
};

const getExportBlob = async (projectId: string, format: ExportFormat): Promise<Blob> => {
  if (format === 'full') {
    const canonical = await exportImportApi.exportFull(projectId);
    return new Blob([JSON.stringify(canonical)], { type: 'application/json' });
  }
  return exportImportApi.exportProject(projectId, format);
};

function useExportDialogModel({ onOpenChange, projects }: ExportDialogProps): ExportDialogModel {
  const [exportFormat, setExportFormat] = useState<ExportFormat>('json');
  const [exportProjectId, setExportProjectId] = useState<string | undefined>();

  const exportTargetId = useMemo<string | undefined>(
    () => getExportTargetId(exportProjectId, projects),
    [exportProjectId, projects],
  );

  const exportMutation = useMutation({
    mutationFn: async ({
      format,
      projectId,
    }: {
      format: ExportFormat;
      projectId: string;
    }): Promise<{ blob: Blob; format: ExportFormat }> => {
      const blob = await getExportBlob(projectId, format);
      return { blob, format };
    },
    onError: () => {
      toast.error('Export sequence failed');
    },
    onSuccess: ({ blob, format }) => {
      const extension = getExportExtension(format);
      downloadBlob(blob, buildExportDownloadName(format, extension));
      toast.success(getExportSuccessMessage(format));
      onOpenChange(false);
    },
  });

  const onProjectChange = useCallback((value: string): void => {
    if (value === EMPTY_STRING) {
      setExportProjectId(undefined);
      return;
    }
    setExportProjectId(value);
  }, []);

  const onFormatChange = useCallback((value: ExportFormat): void => {
    setExportFormat(value);
  }, []);

  const onExport = useCallback((): void => {
    if (typeof exportTargetId !== 'string' || exportTargetId.length === 0) {
      toast.error('Select a project to export');
      return;
    }
    exportMutation.mutate({ format: exportFormat, projectId: exportTargetId });
  }, [exportFormat, exportMutation, exportTargetId]);

  let projectSelectValue = EMPTY_STRING;
  if (typeof exportTargetId === 'string' && exportTargetId.length > 0) {
    projectSelectValue = exportTargetId;
  }

  const isExporting = exportMutation.isPending;
  let isExportDisabled = isExporting;
  if (!isExportDisabled && !(typeof exportTargetId === 'string' && exportTargetId.length > 0)) {
    isExportDisabled = true;
  }

  return {
    exportFormat,
    exportTargetId,
    isExportDisabled,
    isExporting,
    onExport,
    onFormatChange,
    onProjectChange,
    projectSelectValue,
  };
}

function renderExportDialogContent(
  {
    exportFormat,
    isExportDisabled,
    isExporting,
    onExport,
    onFormatChange,
    onProjectChange,
    projectSelectValue,
  }: ExportDialogModel,
  projects: Project[],
): JSX.Element {
  let exportLabel = 'Initialize Dispatch';
  if (isExporting) {
    exportLabel = 'Exporting…';
  }

  return (
    <DialogContent className='bg-card rounded-[2rem] border-none p-8 shadow-2xl'>
      <h2 className='mb-2 text-xl font-black tracking-tight uppercase'>Export Protocol</h2>
      <p className='text-muted-foreground mb-6 text-xs font-medium tracking-widest uppercase'>
        Select project and format
      </p>
      <div className='space-y-6'>
        <div>
          <Label className='text-muted-foreground text-xs font-bold tracking-widest uppercase'>
            Project
          </Label>
          <Select value={projectSelectValue} onValueChange={onProjectChange}>
            <SelectTrigger className='bg-muted/30 mt-1 h-12 rounded-xl border-none font-bold'>
              <SelectValue placeholder='Select project' />
            </SelectTrigger>
            <SelectContent>
              {projects.map((project) => (
                <SelectItem key={project.id} value={project.id}>
                  {getProjectDisplayName(project)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label className='text-muted-foreground text-xs font-bold tracking-widest uppercase'>
            Format
          </Label>
          <Select value={exportFormat} onValueChange={onFormatChange}>
            <SelectTrigger className='bg-muted/30 mt-1 h-12 rounded-xl border-none font-bold'>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='json'>JSON (items)</SelectItem>
              <SelectItem value='csv'>CSV</SelectItem>
              <SelectItem value='full'>Full (project + items + links)</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button
          onClick={onExport}
          disabled={isExportDisabled}
          className='h-12 w-full rounded-xl font-black tracking-widest uppercase shadow-lg'
        >
          {exportLabel}
        </Button>
      </div>
    </DialogContent>
  );
}

export function ExportDialog({ open, onOpenChange, projects }: ExportDialogProps): JSX.Element {
  const model = useExportDialogModel({ onOpenChange, open, projects });
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {renderExportDialogContent(model, projects)}
    </Dialog>
  );
}
