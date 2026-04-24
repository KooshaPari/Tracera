// EquivalenceExport.tsx - Export component for equivalence mappings and canonical concepts
// Supports JSON/CSV export with filtering, confidence score inclusion, and shareable format generation

import {
  Check,
  ChevronDown,
  ChevronRight,
  Copy,
  Download,
  FileJson,
  FileText,
  Filter,
} from 'lucide-react';
import { memo, useCallback, useState } from 'react';

import type { CanonicalConcept, CanonicalProjection, EquivalenceLink } from '@tracertm/types';

import { Checkbox } from '@/components/ui/checkbox';
import { logger } from '@/lib/logger';
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
import { Input } from '@tracertm/ui/components/Input';
import { ScrollArea } from '@tracertm/ui/components/ScrollArea';
import { Separator } from '@tracertm/ui/components/Separator';

import { createExportSummary, serializeToCSV, serializeToJSON } from './utils/equivalenceIO';

// =============================================================================
// TYPES
// =============================================================================

export interface EquivalenceExportProps {
  /** All equivalence links to export */
  equivalenceLinks: EquivalenceLink[];
  /** All canonical concepts to export */
  canonicalConcepts: CanonicalConcept[];
  /** All canonical projections to export */
  canonicalProjections: CanonicalProjection[];
  /** Project ID for context */
  projectId: string;
  /** Current user ID for export attribution */
  userId?: string | undefined;
}

interface ExportOptions {
  format: 'json' | 'csv';
  includeLinks: boolean;
  includeConcepts: boolean;
  includeProjections: boolean;
  includeConfidenceScores: boolean;
  includeSources: boolean;
  minConfidence: number;
  statuses: ('suggested' | 'confirmed' | 'rejected' | 'auto_confirmed')[];
  domains: string[];
}

interface FilterState {
  showFilters: boolean;
  selectedDomains: Set<string>;
  selectedStatuses: Set<string>;
  minConfidence: number;
}

// =============================================================================
// CONSTANTS
// =============================================================================

const DEFAULT_EXPORT_OPTIONS: ExportOptions = {
  domains: [],
  format: 'json',
  includeConcepts: true,
  includeConfidenceScores: true,
  includeLinks: true,
  includeProjections: true,
  includeSources: true,
  minConfidence: 0,
  statuses: ['confirmed', 'auto_confirmed', 'suggested'],
};

// =============================================================================
// COMPONENT
// =============================================================================

function EquivalenceExportComponent({
  equivalenceLinks,
  canonicalConcepts,
  canonicalProjections,
  projectId,
  userId,
}: EquivalenceExportProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [options, setOptions] = useState<ExportOptions>(DEFAULT_EXPORT_OPTIONS);
  const [filters, setFilters] = useState<FilterState>({
    minConfidence: DEFAULT_EXPORT_OPTIONS.minConfidence,
    selectedDomains: new Set(DEFAULT_EXPORT_OPTIONS.domains),
    selectedStatuses: new Set(DEFAULT_EXPORT_OPTIONS.statuses),
    showFilters: false,
  });
  const [copied, setCopied] = useState(false);

  // Get unique domains from concepts
  const uniqueDomains = [...new Set(canonicalConcepts.map((c) => c.domain))].toSorted((a, b) =>
    String(a).localeCompare(String(b)),
  );

  // Filter data based on options
  const filteredLinks = equivalenceLinks.filter(
    (link) => link.confidence >= filters.minConfidence && filters.selectedStatuses.has(link.status),
  );

  const filteredConcepts = canonicalConcepts.filter(
    (concept) => filters.selectedDomains.size === 0 || filters.selectedDomains.has(concept.domain),
  );

  const filteredProjections = canonicalProjections.filter((proj) => {
    const concept = filteredConcepts.find((c) => c.id === proj.canonicalId);
    return concept !== undefined && proj.confidence >= filters.minConfidence;
  });

  // Create export package
  const createExportPackage = useCallback(() => {
    const baseData = {
      exportedAt: new Date().toISOString(),
      exportedBy: userId,
      projectId,
      version: '1.0' as const,
    };

    const data = {
      ...baseData,
      metadata: createExportSummary({
        canonicalConcepts: filteredConcepts,
        canonicalProjections: filteredProjections,
        equivalenceLinks: filteredLinks,
        exportedAt: baseData.exportedAt,
        exportedBy: userId,
        projectId,
        version: '1.0',
      }),
      equivalenceLinks: options.includeLinks ? filteredLinks : [],
      canonicalConcepts: options.includeConcepts ? filteredConcepts : [],
      canonicalProjections: options.includeProjections ? filteredProjections : [],
    };

    return data;
  }, [projectId, userId, filteredLinks, filteredConcepts, filteredProjections, options]);

  // Export as JSON
  const handleExportJSON = useCallback(() => {
    const data = createExportPackage();
    const json = serializeToJSON(data);
    downloadFile(json, 'equivalence-export.json', 'application/json');
    setIsOpen(false);
  }, [createExportPackage]);

  // Export as CSV files
  const handleExportCSV = useCallback(() => {
    const data = createExportPackage();
    const csvData = serializeToCSV({
      canonicalConcepts: data.canonicalConcepts,
      canonicalProjections: data.canonicalProjections,
      equivalenceLinks: data.equivalenceLinks,
      exportedAt: data.exportedAt,
      exportedBy: data.exportedBy,
      metadata: data.metadata,
      projectId: data.projectId,
      version: '1.0',
    });

    if (options.includeLinks && data.equivalenceLinks.length > 0) {
      downloadFile(csvData.links, 'equivalence-links.csv', 'text/csv');
    }
    if (options.includeConcepts && data.canonicalConcepts.length > 0) {
      downloadFile(csvData.concepts, 'canonical-concepts.csv', 'text/csv');
    }
    if (options.includeProjections && data.canonicalProjections.length > 0) {
      downloadFile(csvData.projections, 'canonical-projections.csv', 'text/csv');
    }

    setIsOpen(false);
  }, [createExportPackage, options]);

  // Copy to clipboard
  const handleCopyJSON = useCallback(() => {
    const data = createExportPackage();
    const json = serializeToJSON(data);
    navigator.clipboard
      .writeText(json)
      .then(() => {
        setCopied(true);
        setTimeout(() => {
          setCopied(false);
        }, 2000);
      })
      .catch((error) => {
        logger.error('Failed to copy:', error);
      });
  }, [createExportPackage]);

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant='outline' size='sm' className='gap-2'>
          <Download className='h-4 w-4' />
          Export
        </Button>
      </DialogTrigger>

      <DialogContent className='max-h-[80vh] max-w-2xl'>
        <DialogHeader>
          <DialogTitle>Export Equivalence Data</DialogTitle>
          <DialogDescription>
            Export equivalence mappings and canonical concepts with filtering options
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className='h-auto max-h-[calc(80vh-120px)]'>
          <div className='space-y-6 pr-4'>
            {/* Export Format Selection */}
            <Card>
              <CardHeader>
                <CardTitle className='text-base'>Export Format</CardTitle>
              </CardHeader>
              <CardContent className='space-y-3'>
                <div className='grid grid-cols-2 gap-3'>
                  <Button
                    variant={options.format === 'json' ? 'default' : 'outline'}
                    className='gap-2'
                    onClick={() => {
                      setOptions({ ...options, format: 'json' });
                    }}
                  >
                    <FileJson className='h-4 w-4' />
                    JSON
                  </Button>
                  <Button
                    variant={options.format === 'csv' ? 'default' : 'outline'}
                    className='gap-2'
                    onClick={() => {
                      setOptions({ ...options, format: 'csv' });
                    }}
                  >
                    <FileText className='h-4 w-4' />
                    CSV
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Content Selection */}
            <Card>
              <CardHeader>
                <CardTitle className='text-base'>Data to Include</CardTitle>
                <CardDescription>Select which data types to include in the export</CardDescription>
              </CardHeader>
              <CardContent className='space-y-3'>
                <div className='flex items-center gap-2'>
                  <Checkbox
                    id='include-links'
                    checked={options.includeLinks}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                      setOptions({
                        ...options,
                        includeLinks: e.target.checked,
                      });
                    }}
                    className='h-4 w-4'
                  />
                  <label
                    htmlFor='include-links'
                    className='flex-1 cursor-pointer text-sm font-medium'
                  >
                    Equivalence Links
                  </label>
                  <Badge variant='secondary'>{filteredLinks.length}</Badge>
                </div>

                <div className='flex items-center gap-2'>
                  <Checkbox
                    id='include-concepts'
                    checked={options.includeConcepts}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                      setOptions({
                        ...options,
                        includeConcepts: e.target.checked,
                      });
                    }}
                  />
                  <label
                    htmlFor='include-concepts'
                    className='flex-1 cursor-pointer text-sm font-medium'
                  >
                    Canonical Concepts
                  </label>
                  <Badge variant='secondary'>{filteredConcepts.length}</Badge>
                </div>

                <div className='flex items-center gap-2'>
                  <Checkbox
                    id='include-projections'
                    checked={options.includeProjections}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                      setOptions({
                        ...options,
                        includeProjections: e.target.checked,
                      });
                    }}
                  />
                  <label
                    htmlFor='include-projections'
                    className='flex-1 cursor-pointer text-sm font-medium'
                  >
                    Canonical Projections
                  </label>
                  <Badge variant='secondary'>{filteredProjections.length}</Badge>
                </div>
              </CardContent>
            </Card>

            {/* Advanced Options */}
            <Card>
              <CardHeader>
                <CardTitle className='text-base'>Advanced Options</CardTitle>
              </CardHeader>
              <CardContent className='space-y-3'>
                <div className='flex items-center gap-2'>
                  <Checkbox
                    id='include-confidence'
                    checked={options.includeConfidenceScores}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                      setOptions({
                        ...options,
                        includeConfidenceScores: e.target.checked,
                      });
                    }}
                  />
                  <label
                    htmlFor='include-confidence'
                    className='cursor-pointer text-sm font-medium'
                  >
                    Include Confidence Scores
                  </label>
                </div>

                <div className='flex items-center gap-2'>
                  <Checkbox
                    id='include-sources'
                    checked={options.includeSources}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                      setOptions({
                        ...options,
                        includeSources: e.target.checked,
                      });
                    }}
                  />
                  <label htmlFor='include-sources' className='cursor-pointer text-sm font-medium'>
                    Include Sources and Strategies
                  </label>
                </div>
              </CardContent>
            </Card>

            {/* Filters */}
            <Card>
              <CardHeader className='pb-3'>
                <Button
                  variant='ghost'
                  className='h-auto w-full justify-between px-0 py-0'
                  onClick={() => {
                    setFilters({
                      ...filters,
                      showFilters: !filters.showFilters,
                    });
                  }}
                >
                  <div className='flex items-center gap-2'>
                    <Filter className='h-4 w-4' />
                    <span className='text-base font-semibold'>Filters</span>
                  </div>
                  {filters.showFilters ? (
                    <ChevronDown className='h-4 w-4' />
                  ) : (
                    <ChevronRight className='h-4 w-4' />
                  )}
                </Button>
              </CardHeader>

              {filters.showFilters && (
                <CardContent className='space-y-4'>
                  {/* Confidence Filter */}
                  <div className='space-y-2'>
                    <label className='text-sm font-medium'>
                      Minimum Confidence: {Math.round(filters.minConfidence * 100)}%
                    </label>
                    <input
                      type='range'
                      min='0'
                      max='1'
                      step='0.1'
                      value={filters.minConfidence}
                      onChange={(e) => {
                        setFilters({
                          ...filters,
                          minConfidence: Number.parseFloat(e.target.value),
                        });
                      }}
                      className='w-full'
                    />
                  </div>

                  <Separator />

                  {/* Status Filter */}
                  <div className='space-y-2'>
                    <label className='text-sm font-medium'>Link Status</label>
                    {(['confirmed', 'auto_confirmed', 'suggested', 'rejected'] as const).map(
                      (status) => (
                        <div key={status} className='flex items-center gap-2'>
                          <Checkbox
                            id={`status-${status}`}
                            checked={filters.selectedStatuses.has(status)}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                              const newStatuses = new Set(filters.selectedStatuses);
                              if (e.target.checked) {
                                newStatuses.add(status);
                              } else {
                                newStatuses.delete(status);
                              }
                              setFilters({
                                ...filters,
                                selectedStatuses: newStatuses,
                              });
                            }}
                          />
                          <label
                            htmlFor={`status-${status}`}
                            className='cursor-pointer text-sm capitalize'
                          >
                            {status.replace('_', ' ')}
                          </label>
                        </div>
                      ),
                    )}
                  </div>

                  {uniqueDomains.length > 0 && (
                    <>
                      <Separator />

                      {/* Domain Filter */}
                      <div className='space-y-2'>
                        <label className='text-sm font-medium'>Domains</label>
                        {uniqueDomains.map((domain) => (
                          <div key={domain} className='flex items-center gap-2'>
                            <Checkbox
                              id={`domain-${domain}`}
                              checked={
                                filters.selectedDomains.size === 0 ||
                                filters.selectedDomains.has(domain)
                              }
                              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                                const newDomains = new Set(
                                  filters.selectedDomains.size === 0
                                    ? uniqueDomains
                                    : filters.selectedDomains,
                                );
                                if (e.target.checked) {
                                  newDomains.add(domain);
                                } else {
                                  newDomains.delete(domain);
                                }
                                setFilters({
                                  ...filters,
                                  selectedDomains: newDomains,
                                });
                              }}
                            />
                            <label htmlFor={`domain-${domain}`} className='cursor-pointer text-sm'>
                              {domain}
                            </label>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </CardContent>
              )}
            </Card>

            {/* Export Summary */}
            <Card>
              <CardHeader>
                <CardTitle className='text-base'>Export Summary</CardTitle>
              </CardHeader>
              <CardContent className='space-y-2 text-sm'>
                <div className='flex justify-between'>
                  <span className='text-muted-foreground'>Equivalence Links:</span>
                  <span className='font-medium'>
                    {options.includeLinks ? filteredLinks.length : 0}
                  </span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-muted-foreground'>Canonical Concepts:</span>
                  <span className='font-medium'>
                    {options.includeConcepts ? filteredConcepts.length : 0}
                  </span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-muted-foreground'>Canonical Projections:</span>
                  <span className='font-medium'>
                    {options.includeProjections ? filteredProjections.length : 0}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </ScrollArea>

        {/* Action Buttons */}
        <div className='flex items-center justify-end gap-2 border-t pt-4'>
          {options.format === 'json' && (
            <Button variant='outline' size='sm' className='gap-2' onClick={handleCopyJSON}>
              {copied ? (
                <>
                  <Check className='h-4 w-4' />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className='h-4 w-4' />
                  Copy JSON
                </>
              )}
            </Button>
          )}
          <Button
            variant='default'
            size='sm'
            className='gap-2'
            onClick={options.format === 'json' ? handleExportJSON : handleExportCSV}
          >
            <Download className='h-4 w-4' />
            {options.format === 'json' ? 'Download JSON' : 'Download CSVs'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// =============================================================================
// UTILITIES
// =============================================================================

/**
 * Download a file to user's machine
 */
function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// =============================================================================
// EXPORTS
// =============================================================================

export const EquivalenceExport = memo(EquivalenceExportComponent);
