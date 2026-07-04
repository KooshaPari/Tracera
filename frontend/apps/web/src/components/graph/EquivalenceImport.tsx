// EquivalenceImport.tsx - Import component for equivalence mappings and canonical concepts
// Supports JSON/CSV import with validation, preview, and merge/replace options

import { AlertTriangle, ChevronDown, ChevronRight, Trash2, Upload } from 'lucide-react';
import { memo, useCallback, useState } from 'react';

import type { CanonicalConcept, CanonicalProjection, EquivalenceLink } from '@tracertm/types';

import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription, AlertTitle } from '@tracertm/ui/components/Alert';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@tracertm/ui/components/Card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@tracertm/ui/components/Dialog';
import { ScrollArea } from '@tracertm/ui/components/ScrollArea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';
import { Separator } from '@tracertm/ui/components/Separator';

import type { EquivalenceExportPackage, EquivalenceImportOptions } from './utils/equivalenceIO';

import {
  deserializeFromJSON,
  mergeExportPackages,
  validateExportPackage,
} from './utils/equivalenceIO';

// =============================================================================
// TYPES
// =============================================================================

export interface EquivalenceImportProps {
  /** Existing equivalence links */
  existingLinks: EquivalenceLink[];
  /** Existing canonical concepts */
  existingConcepts: CanonicalConcept[];
  /** Existing canonical projections */
  existingProjections: CanonicalProjection[];
  /** Project ID for context */
  projectId: string;
  /** Callback when import is ready to apply */
  onApplyImport?: (
    links: EquivalenceLink[],
    concepts: CanonicalConcept[],
    projections: CanonicalProjection[],
  ) => void | Promise<void>;
  /** Whether import operation is in progress */
  isLoading?: boolean | undefined;
}

interface ImportState {
  fileContent?: string | undefined;
  fileType?: 'json' | 'csv' | undefined;
  parsedData?: EquivalenceExportPackage | undefined;
  validationErrors: string[];
  conflicts: ConflictInfo[];
  options: EquivalenceImportOptions;
  showPreview: boolean;
}

interface ConflictInfo {
  type: 'link' | 'concept' | 'projection';
  existingId: string;
  incomingId: string;
  existingData: unknown;
  incomingData: unknown;
}

// =============================================================================
// CONSTANTS
// =============================================================================

const DEFAULT_IMPORT_OPTIONS: EquivalenceImportOptions = {
  conflictResolution: 'skip',
  mode: 'merge',
  preserveTimestamps: false,
  targetProjectId: undefined,
  updateProjectId: true,
  validateReferences: true,
};

// =============================================================================
// COMPONENT
// =============================================================================

function EquivalenceImportComponent({
  existingLinks,
  existingConcepts,
  existingProjections,
  projectId,
  onApplyImport,
  isLoading = false,
}: EquivalenceImportProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [state, setState] = useState<ImportState>({
    conflicts: [],
    options: { ...DEFAULT_IMPORT_OPTIONS, targetProjectId: projectId },
    showPreview: false,
    validationErrors: [],
  });
  const [isApplying, setIsApplying] = useState(false);

  // Handle file selection
  const handleFileSelect = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) {
        return;
      }

      try {
        const content = await file.text();
        const fileType = file.name.endsWith('.json') ? 'json' : 'csv';

        let parsedData: EquivalenceExportPackage | null = null;
        let validationErrors: string[] = [];

        if (fileType === 'json') {
          try {
            parsedData = deserializeFromJSON(content);
            const validation = validateExportPackage(parsedData);
            if (!validation.valid) {
              validationErrors = validation.errors;
            }
          } catch (error) {
            validationErrors = [error instanceof Error ? error.message : 'Failed to parse JSON'];
          }
        } else {
          // CSV parsing - would need separate file handling
          validationErrors = ['CSV import requires separate file selection'];
        }

        // Check for conflicts
        const conflicts = findConflicts(
          existingLinks,
          existingConcepts,
          existingProjections,
          parsedData ?? undefined,
        );

        setState({
          conflicts,
          fileContent: content,
          fileType,
          options: { ...state.options, targetProjectId: projectId },
          parsedData: parsedData ?? undefined,
          showPreview: true,
          validationErrors,
        });
      } catch (error) {
        setState({
          ...state,
          validationErrors: [error instanceof Error ? error.message : 'Failed to read file'],
        });
      }
    },
    [existingLinks, existingConcepts, existingProjections, projectId, state],
  );

  // Apply import
  const handleApplyImport = useCallback(async () => {
    const { parsedData } = state;
    if (!parsedData) {
      return;
    }

    setIsApplying(true);
    try {
      const targetProjectId = state.options.targetProjectId ?? projectId;

      // Merge data if needed
      let finalLinks = parsedData.equivalenceLinks;
      let finalConcepts = parsedData.canonicalConcepts;
      let finalProjections = parsedData.canonicalProjections;

      if (state.options.mode === 'merge' && state.options.updateProjectId) {
        const merged = mergeExportPackages(
          {
            canonicalConcepts: existingConcepts,
            canonicalProjections: existingProjections,
            equivalenceLinks: existingLinks,
            exportedAt: new Date().toISOString(),
            projectId: targetProjectId,
            version: '1.0',
          },
          {
            canonicalConcepts: finalConcepts,
            canonicalProjections: finalProjections,
            equivalenceLinks: finalLinks,
            exportedAt: parsedData.exportedAt,
            projectId: targetProjectId,
            version: '1.0',
          },
          state.options,
        );

        finalLinks = merged.equivalenceLinks;
        finalConcepts = merged.canonicalConcepts;
        finalProjections = merged.canonicalProjections;
      } else if (state.options.updateProjectId) {
        // Replace mode - update project IDs
        finalLinks = finalLinks.map((l) => ({
          ...l,
          projectId: targetProjectId,
        }));
        finalConcepts = finalConcepts.map((c) => ({
          ...c,
          projectId: targetProjectId,
        }));
        finalProjections = finalProjections.map((p) => ({
          ...p,
          projectId: targetProjectId,
        }));
      }

      // Call callback
      if (onApplyImport) {
        await onApplyImport(finalLinks, finalConcepts, finalProjections);
      }

      setIsOpen(false);
      setState({
        conflicts: [],
        options: { ...DEFAULT_IMPORT_OPTIONS, targetProjectId: projectId },
        showPreview: false,
        validationErrors: [],
      });
    } catch (error) {
      setState({
        ...state,
        validationErrors: [error instanceof Error ? error.message : 'Failed to apply import'],
      });
    } finally {
      setIsApplying(false);
    }
  }, [state, projectId, existingLinks, existingConcepts, existingProjections, onApplyImport]);

  const isReady =
    state.parsedData && state.validationErrors.length === 0 && !isLoading && !isApplying;

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant='outline' size='sm' className='gap-2'>
          <Upload className='h-4 w-4' />
          Import
        </Button>
      </DialogTrigger>

      <DialogContent className='max-h-[80vh] max-w-2xl'>
        <DialogHeader>
          <DialogTitle>Import Equivalence Data</DialogTitle>
          <DialogDescription>
            Import equivalence mappings and canonical concepts from JSON or CSV
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className='h-auto max-h-[calc(80vh-120px)]'>
          <div className='space-y-6 pr-4'>
            {/* File Selection */}
            {!state.fileContent ? (
              <Card>
                <CardHeader>
                  <CardTitle className='text-base'>Select File</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className='flex w-full items-center justify-center'>
                    <label className='border-muted-foreground hover:bg-accent flex h-64 w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed'>
                      <div className='flex flex-col items-center justify-center pt-5 pb-6'>
                        <Upload className='text-muted-foreground mb-2 h-10 w-10' />
                        <p className='text-sm font-medium'>Click to select file or drag and drop</p>
                        <p className='text-muted-foreground text-xs'>JSON or CSV files supported</p>
                      </div>
                      <input
                        type='file'
                        className='hidden'
                        accept='.json,.csv'
                        onChange={handleFileSelect}
                      />
                    </label>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <>
                {/* File Information */}
                <Card>
                  <CardHeader>
                    <div className='flex items-center justify-between'>
                      <div>
                        <CardTitle className='text-base'>File Information</CardTitle>
                      </div>
                      <Button
                        variant='ghost'
                        size='sm'
                        onClick={() => {
                          setState({
                            ...state,
                            fileContent: undefined,
                            parsedData: undefined,
                            validationErrors: [],
                          });
                        }}
                      >
                        <Trash2 className='h-4 w-4' />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className='space-y-2 text-sm'>
                    <div className='flex justify-between'>
                      <span className='text-muted-foreground'>File Type:</span>
                      <Badge>{state.fileType?.toUpperCase()}</Badge>
                    </div>
                    {state.parsedData && (
                      <>
                        <div className='flex justify-between'>
                          <span className='text-muted-foreground'>Exported:</span>
                          <span>{new Date(state.parsedData.exportedAt).toLocaleString()}</span>
                        </div>
                        <div className='flex justify-between'>
                          <span className='text-muted-foreground'>Source Project:</span>
                          <span>{state.parsedData.projectId}</span>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>

                {/* Validation Errors */}
                {state.validationErrors.length > 0 && (
                  <Alert variant='destructive'>
                    <AlertTriangle className='h-4 w-4' />
                    <AlertTitle>Validation Error</AlertTitle>
                    <AlertDescription>
                      <ul className='mt-2 list-disc space-y-1 pl-5'>
                        {state.validationErrors.map((error, idx) => (
                          <li key={idx} className='text-xs'>
                            {error}
                          </li>
                        ))}
                      </ul>
                    </AlertDescription>
                  </Alert>
                )}

                {/* Conflicts */}
                {state.conflicts.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className='flex items-center gap-2 text-base'>
                        <AlertTriangle className='h-4 w-4 text-amber-500' />
                        Conflicts Found ({state.conflicts.length})
                      </CardTitle>
                      <CardDescription>These items already exist in your project</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className='max-h-[200px] space-y-2 overflow-y-auto'>
                        {state.conflicts.map((conflict, idx) => (
                          <div
                            key={idx}
                            className='bg-accent flex items-start gap-2 rounded p-2 text-sm'
                          >
                            <AlertTriangle className='mt-0.5 h-4 w-4 shrink-0 text-amber-500' />
                            <div className='flex-1'>
                              <p className='font-medium'>
                                {conflict.type} ({conflict.existingId})
                              </p>
                              <p className='text-muted-foreground text-xs'>
                                Will be{' '}
                                {state.options.conflictResolution === 'overwrite'
                                  ? 'overwritten'
                                  : state.options.conflictResolution === 'merge_metadata'
                                    ? 'merged'
                                    : 'skipped'}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Import Options */}
                <Card>
                  <CardHeader>
                    <CardTitle className='text-base'>Import Options</CardTitle>
                  </CardHeader>
                  <CardContent className='space-y-4'>
                    {/* Mode Selection */}
                    <div className='space-y-2'>
                      <label className='text-sm font-medium'>Import Mode</label>
                      <Select
                        value={state.options.mode}
                        onValueChange={(mode) => {
                          setState({
                            ...state,
                            options: {
                              ...state.options,
                              mode: mode as 'merge' | 'replace',
                            },
                          });
                        }}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value='merge'>Merge (combine with existing)</SelectItem>
                          <SelectItem value='replace'>Replace (overwrite all)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <Separator />

                    {/* Conflict Resolution */}
                    {state.options.mode === 'merge' && (
                      <div className='space-y-2'>
                        <label className='text-sm font-medium'>Conflict Resolution</label>
                        <Select
                          value={state.options.conflictResolution}
                          onValueChange={(resolution) => {
                            setState({
                              ...state,
                              options: {
                                ...state.options,
                                conflictResolution: resolution as
                                  | 'skip'
                                  | 'overwrite'
                                  | 'merge_metadata',
                              },
                            });
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value='skip'>Skip existing items</SelectItem>
                            <SelectItem value='overwrite'>Overwrite with imported data</SelectItem>
                            <SelectItem value='merge_metadata'>Merge metadata only</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    )}

                    <Separator />

                    {/* Other Options */}
                    <div className='space-y-2'>
                      <div className='flex items-center gap-2'>
                        <Checkbox
                          id='validate-refs'
                          checked={state.options.validateReferences}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                            setState({
                              ...state,
                              options: {
                                ...state.options,
                                validateReferences: e.target.checked,
                              },
                            });
                          }}
                        />
                        <label
                          htmlFor='validate-refs'
                          className='cursor-pointer text-sm font-medium'
                        >
                          Validate References
                        </label>
                      </div>

                      <div className='flex items-center gap-2'>
                        <Checkbox
                          id='preserve-timestamps'
                          checked={state.options.preserveTimestamps}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                            setState({
                              ...state,
                              options: {
                                ...state.options,
                                preserveTimestamps: e.target.checked,
                              },
                            });
                          }}
                        />
                        <label
                          htmlFor='preserve-timestamps'
                          className='cursor-pointer text-sm font-medium'
                        >
                          Preserve Original Timestamps
                        </label>
                      </div>

                      <div className='flex items-center gap-2'>
                        <Checkbox
                          id='update-project'
                          checked={state.options.updateProjectId}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                            setState({
                              ...state,
                              options: {
                                ...state.options,
                                updateProjectId: e.target.checked,
                              },
                            });
                          }}
                        />
                        <label
                          htmlFor='update-project'
                          className='cursor-pointer text-sm font-medium'
                        >
                          Update Project ID to Current
                        </label>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Import Preview */}
                {state.showPreview && state.parsedData && (
                  <Card>
                    <CardHeader>
                      <Button
                        variant='ghost'
                        className='h-auto w-full justify-between px-0 py-0'
                        onClick={() => {
                          setState({
                            ...state,
                            showPreview: !state.showPreview,
                          });
                        }}
                      >
                        <span className='text-base font-semibold'>Import Preview</span>
                        {state.showPreview ? (
                          <ChevronDown className='h-4 w-4' />
                        ) : (
                          <ChevronRight className='h-4 w-4' />
                        )}
                      </Button>
                    </CardHeader>

                    {state.showPreview && (
                      <CardContent className='space-y-3 text-sm'>
                        <div className='grid grid-cols-2 gap-4'>
                          <div>
                            <p className='text-muted-foreground mb-1'>Equivalence Links</p>
                            <p className='text-lg font-semibold'>
                              {state.parsedData.equivalenceLinks.length}
                            </p>
                          </div>
                          <div>
                            <p className='text-muted-foreground mb-1'>Canonical Concepts</p>
                            <p className='text-lg font-semibold'>
                              {state.parsedData.canonicalConcepts.length}
                            </p>
                          </div>
                          <div>
                            <p className='text-muted-foreground mb-1'>Projections</p>
                            <p className='text-lg font-semibold'>
                              {state.parsedData.canonicalProjections.length}
                            </p>
                          </div>
                          <div>
                            <p className='text-muted-foreground mb-1'>Conflicts</p>
                            <p className='text-lg font-semibold'>{state.conflicts.length}</p>
                          </div>
                        </div>
                      </CardContent>
                    )}
                  </Card>
                )}
              </>
            )}
          </div>
        </ScrollArea>

        {/* Action Buttons */}
        <div className='flex items-center justify-end gap-2 border-t pt-4'>
          {state.fileContent && (
            <>
              <Button
                variant='outline'
                size='sm'
                onClick={() => {
                  setState({
                    ...state,
                    fileContent: undefined,
                    parsedData: undefined,
                    validationErrors: [],
                  });
                }}
              >
                Clear
              </Button>
              <Button
                variant='default'
                size='sm'
                disabled={!isReady}
                className='gap-2'
                onClick={handleApplyImport}
              >
                {isApplying && (
                  <div className='h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent' />
                )}
                {isApplying ? 'Importing...' : 'Apply Import'}
              </Button>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

// =============================================================================
// UTILITIES
// =============================================================================

/**
 * Find conflicts between existing and incoming data
 */
function findConflicts(
  existingLinks: EquivalenceLink[],
  existingConcepts: CanonicalConcept[],
  existingProjections: CanonicalProjection[],
  parsedData?: EquivalenceExportPackage,
): ConflictInfo[] {
  if (!parsedData) {
    return [];
  }

  const conflicts: ConflictInfo[] = [];
  const existingLinkIds = new Set(existingLinks.map((l) => l.id));
  const existingConceptIds = new Set(existingConcepts.map((c) => c.id));
  const existingProjectionIds = new Set(existingProjections.map((p) => p.id));

  // Check for link conflicts
  for (const link of parsedData.equivalenceLinks) {
    if (existingLinkIds.has(link.id)) {
      const existing = existingLinks.find((l) => l.id === link.id);
      conflicts.push({
        existingData: existing,
        existingId: link.id,
        incomingData: link,
        incomingId: link.id,
        type: 'link',
      });
    }
  }

  // Check for concept conflicts
  for (const concept of parsedData.canonicalConcepts) {
    if (existingConceptIds.has(concept.id)) {
      const existing = existingConcepts.find((c) => c.id === concept.id);
      conflicts.push({
        existingData: existing,
        existingId: concept.id,
        incomingData: concept,
        incomingId: concept.id,
        type: 'concept',
      });
    }
  }

  // Check for projection conflicts
  for (const projection of parsedData.canonicalProjections) {
    if (existingProjectionIds.has(projection.id)) {
      const existing = existingProjections.find((p) => p.id === projection.id);
      conflicts.push({
        existingData: existing,
        existingId: projection.id,
        incomingData: projection,
        incomingId: projection.id,
        type: 'projection',
      });
    }
  }

  return conflicts;
}

// =============================================================================
// EXPORTS
// =============================================================================

export const EquivalenceImport = memo(EquivalenceImportComponent);
