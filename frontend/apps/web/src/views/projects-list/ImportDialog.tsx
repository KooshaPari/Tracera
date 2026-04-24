import { useMutation } from '@tanstack/react-query';
import { useCallback, useMemo, useState } from 'react';
import { toast } from 'sonner';

import type { CanonicalExport } from '@/api/endpoints';
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

type ImportMode = 'into-existing' | 'full';

interface ImportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projects: Project[];
}

const EMPTY_STRING = '';

const getImportFileLabel = (mode: ImportMode, file?: File): string => {
  if (file) {
    return file.name;
  }
  if (mode === 'full') {
    return 'Canonical JSON';
  }
  return 'JSON or CSV';
};

const getImportAccept = (mode: ImportMode): string | undefined => {
  if (mode === 'full') {
    return 'application/json,.json';
  }
  return undefined;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;

const readString = (record: Record<string, unknown>, key: string): string | undefined => {
  const value = record[key];
  if (typeof value === 'string') {
    return value;
  }
  return undefined;
};

const readOptionalString = (record: Record<string, unknown>, key: string): string | undefined => {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }
  if (typeof value === 'string') {
    return value;
  }
  return undefined;
};

const readOptionalNumber = (record: Record<string, unknown>, key: string): number | undefined => {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }
  if (typeof value === 'number') {
    return value;
  }
  return undefined;
};

const safeJsonParse = (jsonText: string): unknown => {
  try {
    return JSON.parse(jsonText) as unknown;
  } catch {
    return undefined;
  }
};

const parseCanonicalProject = (value: unknown): CanonicalExport['project'] | undefined => {
  if (!isRecord(value)) {
    return undefined;
  }

  const projectId = readString(value, 'id');
  const projectName = readString(value, 'name');
  if (projectId === undefined || projectName === undefined) {
    return undefined;
  }

  const project: CanonicalExport['project'] = {
    id: projectId,
    name: projectName,
  };
  const description = readOptionalString(value, 'description');
  if (description !== undefined) {
    project.description = description;
  }
  const created_at = readOptionalString(value, 'created_at');
  if (created_at !== undefined) {
    project.created_at = created_at;
  }
  return project;
};

const parseCanonicalItem = (value: unknown): CanonicalExport['items'][number] | undefined => {
  if (!isRecord(value)) {
    return undefined;
  }

  const id = readString(value, 'id');
  const title = readString(value, 'title');
  const view = readString(value, 'view');
  const type = readString(value, 'type');
  const status = readString(value, 'status');
  if (
    id === undefined ||
    title === undefined ||
    view === undefined ||
    type === undefined ||
    status === undefined
  ) {
    return undefined;
  }

  const canonicalItem: CanonicalExport['items'][number] = {
    id,
    status,
    title,
    type,
    view,
  };

  const description = readOptionalString(value, 'description');
  if (description !== undefined) {
    canonicalItem.description = description;
  }

  const version = readOptionalNumber(value, 'version');
  if (version !== undefined) {
    canonicalItem.version = version;
  }

  return canonicalItem;
};

const parseCanonicalItems = (value: unknown): CanonicalExport['items'] | undefined => {
  if (!Array.isArray(value)) {
    return undefined;
  }

  const items: CanonicalExport['items'] = [];
  for (const itemValue of value) {
    const canonicalItem = parseCanonicalItem(itemValue);
    if (canonicalItem === undefined) {
      return undefined;
    }
    items.push(canonicalItem);
  }
  return items;
};

const parseCanonicalLinks = (value: unknown): CanonicalExport['links'] | undefined => {
  if (!Array.isArray(value)) {
    return undefined;
  }

  const links: CanonicalExport['links'] = [];
  for (const linkValue of value) {
    if (!isRecord(linkValue)) {
      return undefined;
    }
    const source_id = readString(linkValue, 'source_id');
    const target_id = readString(linkValue, 'target_id');
    const type = readString(linkValue, 'type');
    if (source_id === undefined || target_id === undefined || type === undefined) {
      return undefined;
    }
    links.push({ source_id, target_id, type });
  }
  return links;
};

const parseCanonicalExport = (jsonText: string): CanonicalExport | undefined => {
  const parsed = safeJsonParse(jsonText);
  if (!isRecord(parsed)) {
    return undefined;
  }

  const project = parseCanonicalProject(parsed['project']);
  const items = parseCanonicalItems(parsed['items']);
  const links = parseCanonicalLinks(parsed['links']);
  if (project === undefined || items === undefined || links === undefined) {
    return undefined;
  }
  return { items, links, project };
};

const getImportTargetId = (
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

interface ImportDialogModel {
  importAccept: string | undefined;
  importFileLabel: string;
  importMode: ImportMode;
  importTargetId: string | undefined;
  isImportDisabled: boolean;
  isImporting: boolean;
  handleFileChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  handleImport: () => void;
  handleModeChange: (value: ImportMode) => void;
  handleProjectChange: (value: string) => void;
  showTargetProject: boolean;
}

interface ImportMutationVariables {
  file: File;
  mode: ImportMode;
  targetProjectId: string | undefined;
}

interface ImportMutationResult {
  importedCount: number;
  linksImported?: number;
  mode: ImportMode;
}

function useImportMutation(
  onOpenChange: (open: boolean) => void,
  clearImportFile: () => void,
): ReturnType<typeof useMutation<ImportMutationResult, unknown, ImportMutationVariables>> {
  return useMutation({
    mutationFn: async ({
      file,
      mode,
      targetProjectId,
    }: ImportMutationVariables): Promise<ImportMutationResult> => {
      const content = await file.text();
      if (mode === 'full') {
        const canonical = parseCanonicalExport(content);
        if (canonical === undefined) {
          throw new Error('Invalid canonical format: need project, items, and links');
        }
        const result = await exportImportApi.importFull(canonical);
        return { importedCount: result.items_imported, linksImported: result.links_imported, mode };
      }

      if (typeof targetProjectId !== 'string' || targetProjectId.length === 0) {
        throw new Error('Select a project to import into');
      }
      const result = await exportImportApi.import(targetProjectId, 'json', content);
      return { importedCount: result.imported_count, mode };
    },
    onError: (error) => {
      let message = 'Import integrity failure';
      if (error instanceof Error) {
        const { message: errorMessage } = error;
        message = errorMessage;
      }
      toast.error(message);
    },
    onSuccess: ({ importedCount, linksImported, mode }: ImportMutationResult) => {
      if (mode === 'full') {
        let links = 0;
        if (typeof linksImported === 'number') {
          links = linksImported;
        }
        toast.success(`New project created: ${importedCount} items, ${links} links`);
      } else {
        toast.success(`Imported ${importedCount} nodes successfully`);
      }
      onOpenChange(false);
      clearImportFile();
    },
  });
}

function renderImportDialogContent(model: ImportDialogModel, projects: Project[]): JSX.Element {
  let importLabel = 'Execute Ingestion';
  if (model.isImporting) {
    importLabel = 'Importing…';
  }

  return (
    <DialogContent className='bg-card rounded-[2rem] border-none p-8 shadow-2xl'>
      <h2 className='mb-2 text-xl font-black tracking-tight uppercase'>Ingestion Protocol</h2>
      <p className='text-muted-foreground mb-6 text-xs font-medium tracking-widest uppercase'>
        Upload file: create new project (full) or add to existing
      </p>
      <div className='space-y-6'>
        <div>
          <Label className='text-muted-foreground text-xs font-bold tracking-widest uppercase'>
            Mode
          </Label>
          <Select value={model.importMode} onValueChange={model.handleModeChange}>
            <SelectTrigger className='bg-muted/30 mt-1 h-12 rounded-xl border-none font-bold'>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='full'>As new project (canonical JSON)</SelectItem>
              <SelectItem value='into-existing'>Into existing project (items JSON/CSV)</SelectItem>
            </SelectContent>
          </Select>
        </div>
        {model.showTargetProject && (
          <div>
            <Label className='text-muted-foreground text-xs font-bold tracking-widest uppercase'>
              Target project
            </Label>
            <Select
              value={model.importTargetId ?? EMPTY_STRING}
              onValueChange={model.handleProjectChange}
            >
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
        )}
        <div className='bg-muted/10 group hover:border-primary/50 flex flex-col items-center justify-center rounded-[2rem] border-2 border-dashed p-8 text-center transition-colors'>
          <input
            type='file'
            id='project-import-file'
            className='hidden'
            accept={model.importAccept}
            onChange={model.handleFileChange}
          />
          <Label htmlFor='project-import-file' className='cursor-pointer'>
            <span className='text-primary text-sm font-bold'>Browse Files</span>
            <p className='text-muted-foreground mt-1 text-[10px] font-medium'>
              {model.importFileLabel}
            </p>
          </Label>
        </div>
        <Button
          onClick={model.handleImport}
          disabled={model.isImportDisabled}
          className='h-12 w-full rounded-xl font-black tracking-widest uppercase shadow-lg'
        >
          {importLabel}
        </Button>
      </div>
    </DialogContent>
  );
}

function useImportDialogModel({ onOpenChange, projects }: ImportDialogProps): ImportDialogModel {
  const [importMode, setImportMode] = useState<ImportMode>('full');
  const [importProjectId, setImportProjectId] = useState<string | undefined>();
  const [importFile, setImportFile] = useState<File | undefined>();

  const importTargetId = useMemo<string | undefined>(
    () => getImportTargetId(importProjectId, projects),
    [importProjectId, projects],
  );

  const importAccept = useMemo<string | undefined>(() => getImportAccept(importMode), [importMode]);
  const importFileLabel = useMemo<string>(
    () => getImportFileLabel(importMode, importFile),
    [importFile, importMode],
  );

  const handleModeChange = useCallback((value: ImportMode): void => {
    setImportMode(value);
  }, []);

  const handleProjectChange = useCallback((value: string): void => {
    if (value === EMPTY_STRING) {
      setImportProjectId(undefined);
      return;
    }
    setImportProjectId(value);
  }, []);

  const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>): void => {
    const file = event.target.files?.[0];
    setImportFile(file);
  }, []);

  const clearImportFile = useCallback((): void => {
    setImportFile(undefined);
  }, []);

  const importMutation = useImportMutation(onOpenChange, clearImportFile);

  const showTargetProject = importMode === 'into-existing';
  const isImporting = importMutation.isPending;

  const importTargetPresent = typeof importTargetId === 'string' && importTargetId.length > 0;
  const filePresent = importFile !== undefined;
  const isTargetMissing = showTargetProject && !importTargetPresent;
  const isImportDisabled = isImporting || !filePresent || isTargetMissing;

  const handleImport = useCallback((): void => {
    if (importFile === undefined) {
      return;
    }
    importMutation.mutate({
      file: importFile,
      mode: importMode,
      targetProjectId: importTargetId,
    });
  }, [importFile, importMode, importMutation, importTargetId]);

  return {
    importAccept,
    importFileLabel,
    importMode,
    importTargetId,
    isImportDisabled,
    isImporting,
    handleFileChange,
    handleImport,
    handleModeChange,
    handleProjectChange,
    showTargetProject,
  };
}

export function ImportDialog({ open, onOpenChange, projects }: ImportDialogProps): JSX.Element {
  const model = useImportDialogModel({ onOpenChange, open, projects });
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {renderImportDialogContent(model, projects)}
    </Dialog>
  );
}
