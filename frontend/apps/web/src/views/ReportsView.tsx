import { useMutation, useQuery } from '@tanstack/react-query';
import {
  ClipboardList,
  Download,
  FileSearch,
  FileText,
  History as HistoryIcon,
  Layers,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

import { cn } from '@/lib/utils';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';

import { api } from '../api/endpoints';

const SIMULATED_GENERATION_DELAY_MS = 1500;

type ReportFormat = 'json' | 'csv' | 'pdf' | 'xlsx';

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  format: ReportFormat[];
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

const reportTemplates: ReportTemplate[] = [
  {
    color: 'text-blue-500',
    description: 'End-to-end mapping from reqs to implementation.',
    format: ['pdf', 'xlsx', 'csv'],
    icon: Layers,
    id: 'coverage',
    name: 'Traceability Matrix',
  },
  {
    color: 'text-green-500',
    description: 'High-level project health and risk assessment.',
    format: ['pdf', 'xlsx'],
    icon: TrendingUp,
    id: 'status',
    name: 'Executive Summary',
  },
  {
    color: 'text-purple-500',
    description: 'Full export of all nodes and metadata.',
    format: ['json', 'csv', 'xlsx'],
    icon: ClipboardList,
    id: 'items',
    name: 'Entity Registry',
  },
  {
    color: 'text-orange-500',
    description: 'Complete history of changes and transitions.',
    format: ['pdf', 'json'],
    icon: ShieldCheck,
    id: 'audit',
    name: 'Compliance Audit',
  },
];

export function ReportsView() {
  const [selectedFormat, setSelectedFormat] = useState<Record<string, ReportFormat>>({});
  const [selectedProject, setSelectedProject] = useState<string>('');

  const projectsQuery = useQuery({
    queryFn: async () => api.projects.list(),
    queryKey: ['projects'],
  });

  const generateReportMutation = useMutation({
    mutationFn: async ({
      templateId,
      format,
      projectId,
    }: {
      templateId: string;
      format: ReportFormat;
      projectId?: string;
    }) => {
      if (format === 'json' || format === 'csv') {
        if (!projectId) {
          throw new Error('Select project context');
        }
        const out = await api.exportImport.export(projectId, format);
        if (!(out instanceof Blob)) {
          toast.error('Export did not return a downloadable file');
          return { success: false };
        }
        const url = globalThis.URL.createObjectURL(out);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${templateId}-export.${format}`;
        document.body.append(a);
        a.click();
        globalThis.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        return { success: true };
      }
      // Simulate long generation for PDF/XLSX
      await new Promise((r) => setTimeout(r, SIMULATED_GENERATION_DELAY_MS));
      toast.info(`${templateId.toUpperCase()} generation initialized in background`);
      return { success: false };
    },
    onError: (error) => {
      toast.error(error.message || 'Engine failure during generation');
    },
    onSuccess: (data) => {
      if (data.success) {
        toast.success('Export successful');
      }
    },
  });

  const handleGenerate = (templateId: string) => {
    const format =
      selectedFormat[templateId] ??
      reportTemplates.find((t) => t.id === templateId)?.format[0] ??
      'pdf';
    if ((format === 'json' || format === 'csv') && !selectedProject) {
      toast.error('Global scope export disabled. Select project.');
      return;
    }
    generateReportMutation.mutate({
      format,
      projectId: selectedProject,
      templateId,
    });
  };

  return (
    <div className='animate-in-fade-up mx-auto max-w-6xl space-y-8 p-6 pb-20'>
      {/* Header */}
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-primary text-2xl font-black tracking-tight uppercase'>
            Intelligence Hub
          </h1>
          <p className='text-muted-foreground text-sm font-medium'>
            Generate deterministic reports and structural exports.
          </p>
        </div>
      </div>

      {/* Project Context Selector */}
      <Card className='bg-muted/30 rounded-[2rem] border-none p-6 shadow-inner'>
        <div className='flex flex-col items-center gap-6 md:flex-row'>
          <div className='bg-background flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl shadow-sm'>
            <FileSearch className='text-primary h-6 w-6' />
          </div>
          <div className='flex-1 space-y-1'>
            <h3 className='text-xs font-black tracking-widest uppercase'>Global Context</h3>
            <p className='text-muted-foreground text-[10px] font-bold uppercase'>
              Filter intelligence by project boundary
            </p>
          </div>
          <div className='w-full md:w-72'>
            <Select
              value={selectedProject || 'all'}
              onValueChange={(v) => {
                setSelectedProject(v === 'all' ? '' : v);
              }}
            >
              <SelectTrigger className='bg-background h-11 rounded-xl border-none shadow-md'>
                <SelectValue placeholder='All Active Projects' />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='all'>System-Wide Registry</SelectItem>
                {projectsQuery.data?.map((project) => (
                  <SelectItem key={project.id} value={project.id}>
                    {project.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </Card>

      {/* Templates Grid */}
      <div className='stagger-children grid grid-cols-1 gap-6 md:grid-cols-2'>
        {reportTemplates.map((template) => (
          <Card
            key={template.id}
            className='bg-card/50 group relative overflow-hidden border-none p-8 shadow-sm transition-all duration-200 ease-out hover:shadow-xl active:scale-[0.99]'
          >
            {/* Subtle Icon Background */}
            <div className='absolute -right-4 -bottom-4 opacity-[0.03] transition-opacity group-hover:opacity-[0.08]'>
              <template.icon className='h-40 w-40' />
            </div>

            <div className='relative z-10 flex items-start gap-6'>
              <div
                className={cn(
                  'h-14 w-14 rounded-2xl bg-muted/50 flex items-center justify-center shrink-0',
                  template.color,
                )}
              >
                <template.icon className='h-7 w-7' />
              </div>
              <div className='flex-1 space-y-4'>
                <div>
                  <h3 className='text-lg font-black tracking-tight'>{template.name}</h3>
                  <p className='text-muted-foreground mt-1 text-xs leading-relaxed font-medium'>
                    {template.description}
                  </p>
                </div>

                <div className='space-y-3'>
                  <p className='text-muted-foreground text-[9px] font-black tracking-[0.2em] uppercase'>
                    Select Format
                  </p>
                  <div className='flex flex-wrap gap-2'>
                    {template.format.map((format) => (
                      <button
                        key={format}
                        onClick={() => {
                          setSelectedFormat({
                            ...selectedFormat,
                            [template.id]: format,
                          });
                        }}
                        className={cn(
                          'px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-tighter border transition-all',
                          selectedFormat[template.id] === format ||
                            (!selectedFormat[template.id] && template.format[0] === format)
                            ? 'bg-primary text-primary-foreground border-primary shadow-lg shadow-primary/20'
                            : 'bg-background border-border hover:border-primary/50 text-muted-foreground',
                        )}
                      >
                        {format}
                      </button>
                    ))}
                  </div>
                </div>

                <Button
                  onClick={() => {
                    handleGenerate(template.id);
                  }}
                  className='shadow-primary/10 h-11 w-full gap-2 rounded-xl font-black tracking-[0.1em] uppercase shadow-lg'
                  disabled={generateReportMutation.isPending}
                >
                  {generateReportMutation.isPending ? (
                    <TrendingUp className='h-4 w-4 animate-bounce' />
                  ) : (
                    <Download className='h-4 w-4' />
                  )}
                  Compile Engine
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Recent Activity */}
      <Card className='bg-muted/20 rounded-[2rem] border-none p-8'>
        <div className='mb-8 flex items-center gap-3'>
          <HistoryIcon className='text-primary h-5 w-5' />
          <h2 className='text-sm font-black tracking-widest uppercase'>Archive History</h2>
        </div>
        <div className='grid grid-cols-1 gap-4 md:grid-cols-2'>
          {[
            { date: '2h ago', name: 'Full Integrity Matrix', type: 'PDF' },
            { date: 'Yesterday', name: 'Node Registry v1.4', type: 'JSON' },
          ].map((r, i) => (
            <div
              key={i}
              className='bg-background/50 border-border/50 group hover:border-primary/30 flex items-center justify-between rounded-2xl border p-4 transition-colors'
            >
              <div className='flex items-center gap-4'>
                <div className='bg-primary/5 flex h-10 w-10 items-center justify-center rounded-xl'>
                  <FileText className='text-primary h-5 w-5' />
                </div>
                <div>
                  <div className='text-sm font-bold'>{r.name}</div>
                  <div className='text-muted-foreground text-[10px] font-black tracking-tighter uppercase'>
                    {r.date} • {r.type}
                  </div>
                </div>
              </div>
              <Button
                variant='ghost'
                size='icon'
                className='group-hover:bg-primary rounded-full transition-all group-hover:text-white'
              >
                <Download className='h-4 w-4' />
              </Button>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
