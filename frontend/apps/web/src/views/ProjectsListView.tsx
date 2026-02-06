import { Link, useNavigate, useSearch } from '@tanstack/react-router';
import {
  Activity,
  ArrowRight,
  Calendar,
  Copy,
  Download,
  Edit,
  ExternalLink,
  Folder,
  MoreVertical,
  Plus,
  Search,
  Trash2,
  Upload,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { toast } from 'sonner';

import type { Project } from '@tracertm/types';

import { client } from '@/api/client';
import { getProjectDisplayName } from '@/lib/project-name-utils';
import { cn } from '@/lib/utils';
import {
  Badge,
  Button,
  Card,
  Dialog,
  DialogContent,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  Input,
  Label,
  Progress,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
} from '@tracertm/ui';

import type { CanonicalExport } from '../api/endpoints';

import { exportImportApi } from '../api/endpoints';
import {
  useCreateProject,
  useDeleteProject,
  useProjects,
  useUpdateProject,
} from '../hooks/useProjects';

const { getAuthHeaders } = client;

interface ProjectCardProps {
  project: Project;
  itemCount: number;
  onDelete?: (projectId: string) => void;
  onEdit?: (project: Project) => void;
}

function ProjectCard({ project, itemCount, onDelete, onEdit }: ProjectCardProps) {
  const navigate = useNavigate();
  const deleteProject = useDeleteProject();
  // Mock progress for visual flair
  const progress = useMemo(() => Math.floor(Math.random() * 40) + 60, []);

  const handleDelete = async () => {
    const displayName = getProjectDisplayName(project);
    if (
      !confirm(`Are you sure you want to delete "${displayName}"? This action cannot be undone.`)
    ) {
      return;
    }
    try {
      await deleteProject.mutateAsync(project.id);
      toast.success(`Project "${displayName}" deleted`);
      onDelete?.(project.id);
    } catch {
      toast.error('Failed to delete project');
    }
  };

  const handleCopyId = () => {};

  return (
    <Card className='group border-border bg-card hover:border-primary/30 hover:bg-card relative cursor-pointer overflow-hidden rounded-[2rem] border p-5 shadow-lg backdrop-blur-sm transition-all duration-300 ease-out hover:-translate-y-0.5 hover:shadow-2xl active:translate-y-0 active:scale-[0.99] sm:p-6'>
      {/* Status Indicator */}
      <div className='bg-primary/30 group-hover:bg-primary absolute top-0 left-0 h-full w-1 transition-colors' />

      <div className='flex h-full flex-col space-y-6'>
        {/* Header with icon, badge, and menu */}
        <div className='flex items-start justify-between'>
          <div className='bg-primary/5 group-hover:bg-primary group-hover:text-primary-foreground flex h-12 w-12 items-center justify-center rounded-2xl transition-all duration-500'>
            <Folder className='h-6 w-6' />
          </div>
          <div className='flex items-center gap-2'>
            <Badge
              variant='secondary'
              className='shrink-0 px-2 text-[10px] font-black tracking-tighter uppercase'
            >
              {itemCount} Items
            </Badge>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <span>
                  <Button
                    variant='ghost'
                    size='icon'
                    className='text-muted-foreground hover:text-foreground hover:bg-muted z-10 h-8 w-8 shrink-0 transition-colors'
                    onClick={(e) => e.stopPropagation()}
                    aria-label='Project options'
                  >
                    <MoreVertical className='h-4 w-4' />
                    <span className='sr-only'>Open project menu</span>
                  </Button>
                </span>
              </DropdownMenuTrigger>
              <DropdownMenuContent align='end' className='w-48'>
                <DropdownMenuItem
                  onClick={() => {}}
                  className='hover:bg-accent hover:text-accent-foreground cursor-pointer gap-2 transition-colors'
                >
                  <ExternalLink className='h-4 w-4' />
                  Open Project
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation();
                    onEdit?.(project);
                  }}
                  className='hover:bg-accent hover:text-accent-foreground cursor-pointer gap-2 transition-colors'
                >
                  <Edit className='h-4 w-4' />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation();
                    handleCopyId();
                  }}
                  className='hover:bg-accent hover:text-accent-foreground cursor-pointer gap-2 transition-colors'
                >
                  <Copy className='h-4 w-4' />
                  Copy ID
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => {}}
                  className='text-destructive focus:text-destructive focus:bg-destructive/10 hover:bg-destructive/10 hover:text-destructive cursor-pointer gap-2 transition-colors'
                >
                  <Trash2 className='h-4 w-4' />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Project Info */}
        <div className='flex-1'>
          <Link to={`/projects/${project.id}`} className='block'>
            <h3 className='group-hover:text-primary line-clamp-2 text-xl font-black tracking-tight break-words transition-colors'>
              {getProjectDisplayName(project)}
            </h3>
          </Link>
          <p className='text-muted-foreground mt-2 line-clamp-4 text-xs leading-relaxed font-medium sm:line-clamp-3'>
            {project.description ||
              'Distributed traceability graph for requirements and implementation mapping.'}
          </p>
        </div>

        {/* Progress Section */}
        <div className='space-y-3'>
          <div className='text-muted-foreground flex items-center justify-between text-[10px] font-black tracking-widest uppercase'>
            <span>Integrity Ratio</span>
            <span>{progress}%</span>
          </div>
          <Progress value={progress} className='bg-muted h-1.5' />
        </div>

        {/* Footer with date and action */}
        <div className='flex items-center justify-between pt-2'>
          <div className='text-muted-foreground/60 flex items-center gap-2 text-[10px] font-bold uppercase'>
            <Calendar className='h-3 w-3' />
            {project.createdAt ? new Date(project.createdAt).toLocaleDateString() : 'N/A'}
          </div>
          <Link to={`/projects/${project.id}`}>
            <Button
              variant='ghost'
              size='sm'
              className='group/btn gap-2 text-[10px] font-black tracking-widest uppercase'
            >
              Connect{' '}
              <ArrowRight className='h-3 w-3 transition-transform group-hover/btn:translate-x-1' />
            </Button>
          </Link>
        </div>
      </div>
    </Card>
  );
}

function EditProjectDialog({
  project,
  open,
  onOpenChange,
}: {
  project: Project | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [name, setName] = useState(project?.name || '');
  const [description, setDescription] = useState(project?.description || '');
  const updateProject = useUpdateProject();

  useEffect(() => {
    if (project) {
      setName(project.name || '');
      setDescription(project.description || '');
    }
  }, [project]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !project) {
      toast.error('Project identity sequence required');
      return;
    }

    try {
      await updateProject.mutateAsync({
        data: {
          name: name.trim(),
          ...(description.trim() ? { description: description.trim() } : {}),
        },
        id: project.id,
      });
      toast.success(`Project "${getProjectDisplayName({ ...project, name })}" updated`);
      setName('');
      setDescription('');
      onOpenChange(false);
    } catch {
      toast.error('Cluster reject: Failed to update project');
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className='bg-card overflow-hidden rounded-[2rem] border-none p-0 shadow-2xl sm:max-w-[500px]'>
        <div className='bg-primary text-primary-foreground p-8'>
          <div className='mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/20'>
            <Edit className='h-6 w-6' />
          </div>
          <h2 className='text-2xl font-black tracking-tight uppercase'>Edit Registry</h2>
          <p className='text-primary-foreground/70 mt-1 text-xs font-bold tracking-widest uppercase'>
            Modify project container details
          </p>
        </div>
        <form onSubmit={handleSubmit} className='space-y-6 p-8'>
          <div className='space-y-4'>
            <div className='space-y-2'>
              <Label
                htmlFor='edit-project-name'
                className='ml-1 text-[10px] font-black tracking-widest uppercase'
              >
                Project Identifier
              </Label>
              <Input
                id='edit-project-name'
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder='e.g. PROJECT-X-ALPHA'
                className='bg-muted/30 h-12 rounded-xl border-none px-4 font-bold'
              />
            </div>

            <div className='space-y-2'>
              <Label
                htmlFor='edit-project-description'
                className='ml-1 text-[10px] font-black tracking-widest uppercase'
              >
                Technical Brief
              </Label>
              <Textarea
                id='edit-project-description'
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder='Context and scope definition...'
                className='bg-muted/30 min-h-[120px] rounded-xl border-none p-4 font-medium'
              />
            </div>
          </div>

          <div className='flex gap-3 pt-2'>
            <Button
              type='button'
              variant='ghost'
              onClick={() => onOpenChange(false)}
              className='flex-1 rounded-xl text-[10px] font-black tracking-widest uppercase'
            >
              Cancel
            </Button>
            <Button
              type='submit'
              disabled={updateProject.isPending}
              className='shadow-primary/20 h-12 flex-1 rounded-xl text-[10px] font-black tracking-widest uppercase shadow-lg'
            >
              {updateProject.isPending ? 'Syncing...' : 'Update'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function CreateProjectDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [openIntegrations, setOpenIntegrations] = useState(true);
  const createProject = useCreateProject();
  const _navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      toast.error('Project identity sequence required');
      return;
    }

    try {
      const project = await createProject.mutateAsync({
        name: name.trim(),
        ...(description.trim() ? { description: description.trim() } : {}),
      });
      toast.success(`Project "${getProjectDisplayName(project)}" initialized`);
      setName('');
      setDescription('');
      onOpenChange(false);
      undefined;
    } catch {
      toast.error('Cluster reject: Failed to initialize project');
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className='bg-card overflow-hidden rounded-[2rem] border-none p-0 shadow-2xl sm:max-w-[500px]'>
        <div className='bg-primary text-primary-foreground p-8'>
          <div className='mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/20'>
            <Plus className='h-6 w-6' />
          </div>
          <h2 className='text-2xl font-black tracking-tight uppercase'>New Registry</h2>
          <p className='text-primary-foreground/70 mt-1 text-xs font-bold tracking-widest uppercase'>
            Initialize a new project container
          </p>
        </div>
        <form onSubmit={handleSubmit} className='space-y-6 p-8'>
          <div className='space-y-4'>
            <div className='space-y-2'>
              <Label
                htmlFor='project-name'
                className='ml-1 text-[10px] font-black tracking-widest uppercase'
              >
                Project Identifier
              </Label>
              <Input
                id='project-name'
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder='e.g. PROJECT-X-ALPHA'
                className='bg-muted/30 h-12 rounded-xl border-none px-4 font-bold'
              />
            </div>

            <div className='space-y-2'>
              <Label
                htmlFor='project-description'
                className='ml-1 text-[10px] font-black tracking-widest uppercase'
              >
                Technical Brief
              </Label>
              <Textarea
                id='project-description'
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder='Context and scope definition...'
                className='bg-muted/30 min-h-[120px] rounded-xl border-none p-4 font-medium'
              />
            </div>
          </div>

          <div className='flex gap-3 pt-4'>
            <label className='text-muted-foreground flex items-center gap-2 text-[10px] font-bold tracking-widest uppercase'>
              <input
                type='checkbox'
                checked={openIntegrations}
                onChange={(e) => setOpenIntegrations(e.target.checked)}
              />
              Open integrations after create
            </label>
          </div>

          <div className='flex gap-3 pt-2'>
            <Button
              type='button'
              variant='ghost'
              onClick={() => onOpenChange(false)}
              className='flex-1 rounded-xl text-[10px] font-black tracking-widest uppercase'
            >
              Cancel
            </Button>
            <Button
              type='submit'
              disabled={createProject.isPending}
              className='shadow-primary/20 h-12 flex-1 rounded-xl text-[10px] font-black tracking-widest uppercase shadow-lg'
            >
              {createProject.isPending ? 'Syncing...' : 'Initialize'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function ProjectsListView() {
  const _navigate = useNavigate();
  const searchParams = useSearch({ strict: false }) as any;
  const { data: projects, isLoading: projectsLoading } = useProjects();
  const [projectItemCounts, _setProjectItemCounts] = useState<Record<string, number>>({});

  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'items'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [exportFormat, setExportFormat] = useState<'json' | 'csv' | 'full'>('json');
  const [exportProjectId, setExportProjectId] = useState<string | null>(null);
  const [importFormat] = useState<'json' | 'csv'>('json');
  const [importMode, setImportMode] = useState<'into-existing' | 'full'>('full');
  const [importProjectId, setImportProjectId] = useState<string | null>(null);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);

  const showCreateDialog = searchParams?.action === 'create';

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      undefined;
    }
  };

  const handleExport = async () => {
    const projectId = exportProjectId ?? projectsArray[0]?.id;
    if (!projectId) {
      toast.error('Select a project to export');
      return;
    }
    setIsExporting(true);
    try {
      const result = await exportImportApi.export(projectId, exportFormat);
      const blob =
        result instanceof Blob
          ? result
          : new Blob([JSON.stringify(result)], { type: 'application/json' });
      const ext = exportFormat === 'full' ? 'json' : exportFormat === 'csv' ? 'csv' : 'json';
      const url = globalThis.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `tracertm-export-${exportFormat}-${new Date().toISOString().split('T')[0]}.${ext}`;
      document.body.append(a);
      a.click();
      globalThis.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success(
        exportFormat === 'full' ? 'Full project export completed' : 'Registry backup completed',
      );
      setShowExportDialog(false);
    } catch {
      toast.error('Export sequence failed');
    } finally {
      setIsExporting(false);
    }
  };

  const handleImport = async () => {
    if (!importFile) {
      return;
    }
    setIsImporting(true);
    try {
      const content = await importFile.text();
      if (importMode === 'full') {
        const parsed = JSON.parse(content) as {
          project?: unknown;
          items?: unknown[];
          links?: unknown[];
        };
        if (!parsed.project || !Array.isArray(parsed.items)) {
          toast.error('Invalid canonical format: need project and items');
          return;
        }
        const canonical = {
          items: parsed.items as CanonicalExport['items'],
          links: (parsed.links ?? []) as CanonicalExport['links'],
          project: parsed.project as {
            id: string;
            name: string;
            description?: string;
            created_at?: string;
          },
        };
        const result = await exportImportApi.importFull(canonical);
        toast.success(
          `New project created: ${result.items_imported} items, ${result.links_imported} links`,
        );
        setShowImportDialog(false);
        setImportFile(null);
        undefined;
      } else {
        const projectId = importProjectId ?? projectsArray[0]?.id;
        if (!projectId) {
          toast.error('Select a project to import into');
          return;
        }
        const result = await exportImportApi.import(projectId, importFormat, content);
        toast.success(`Imported ${result.imported_count} nodes successfully`);
        setShowImportDialog(false);
        setImportFile(null);
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Import integrity failure');
    } finally {
      setIsImporting(false);
    }
  };

  const projectsArray = Array.isArray(projects) ? projects : [];

  useEffect(() => {}, [projectsArray]);

  const filteredAndSortedProjects = useMemo(() => {
    const filtered = projectsArray.filter((p) => {
      const displayName = getProjectDisplayName(p);
      return displayName.toLowerCase().includes(searchQuery.toLowerCase());
    });

    return filtered
      .map((p) => ({ itemCount: projectItemCounts[p.id] || 0, project: p }))
      .toSorted((a, b) => {
        let comp = 0;
        if (sortBy === 'name') {
          const aName = getProjectDisplayName(a.project);
          const bName = getProjectDisplayName(b.project);
          comp = aName.localeCompare(bName);
        } else if (sortBy === 'date') {
          comp =
            new Date(a.project.createdAt || 0).getTime() -
            new Date(b.project.createdAt || 0).getTime();
        } else {
          comp = a.itemCount - b.itemCount;
        }
        return sortOrder === 'asc' ? comp : -comp;
      });
  }, [projectsArray, searchQuery, sortBy, sortOrder, projectItemCounts]);

  if (projectsLoading) {
    return (
      <div className='animate-pulse space-y-8 p-6'>
        <Skeleton className='h-10 w-48' />
        <div className='grid grid-cols-1 gap-6 md:grid-cols-3'>
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className='h-64 rounded-[2rem]' />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className='animate-in-fade-up mx-auto max-w-[1600px] space-y-8 p-6'>
      {/* Header */}
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-2xl font-black tracking-tight uppercase'>Project Registry</h1>
          <p className='text-muted-foreground text-sm font-medium'>
            Coordinate and scale multiple traceability domains from a single interface.
          </p>
        </div>
        <div className='flex items-center gap-2'>
          <Button
            variant='ghost'
            size='sm'
            onClick={() => setShowExportDialog(true)}
            className='gap-2 rounded-xl text-[10px] font-black tracking-widest uppercase'
          >
            <Download className='h-3.5 w-3.5' /> Export
          </Button>
          <Button
            variant='ghost'
            size='sm'
            onClick={() => setShowImportDialog(true)}
            className='gap-2 rounded-xl text-[10px] font-black tracking-widest uppercase'
          >
            <Upload className='h-3.5 w-3.5' /> Import
          </Button>
          <Button
            size='sm'
            onClick={() => {}}
            className='shadow-primary/20 gap-2 rounded-xl text-[10px] font-black tracking-widest uppercase shadow-lg'
          >
            <Plus className='h-4 w-4' /> New Registry
          </Button>
        </div>
      </div>

      {/* Filters Bar */}
      <Card className='bg-muted/30 flex flex-wrap items-center gap-2 rounded-2xl border-none p-2'>
        <div className='relative min-w-[200px] flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <Input
            placeholder='Filter registries...'
            className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className='bg-border/50 mx-2 hidden h-6 w-px md:block' />
        <Select value={sortBy} onValueChange={(v: any) => setSortBy(v)}>
          <SelectTrigger className='hover:bg-background/50 h-10 w-[150px] border-none bg-transparent transition-colors'>
            <SelectValue placeholder='Sort Parameters' />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='date'>Sync Date</SelectItem>
            <SelectItem value='name'>Identifier</SelectItem>
            <SelectItem value='items'>Node Density</SelectItem>
          </SelectContent>
        </Select>
        <Button
          variant='ghost'
          size='icon'
          onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          className='h-10 w-10 rounded-xl'
        >
          <Activity
            className={cn('h-4 w-4 transition-transform', sortOrder === 'desc' ? 'rotate-180' : '')}
          />
        </Button>
      </Card>

      {/* Grid Content */}
      {filteredAndSortedProjects.length > 0 ? (
        <div className='stagger-children grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'>
          {filteredAndSortedProjects.map(({ project, itemCount }) => (
            <ProjectCard
              key={project.id}
              project={project}
              itemCount={itemCount}
              onEdit={(p) => setEditingProject(p)}
            />
          ))}
        </div>
      ) : (
        <div className='text-muted-foreground/30 flex flex-col items-center justify-center py-32'>
          <Folder className='mb-6 h-20 w-20 opacity-10' />
          <p className='text-sm font-black tracking-[0.2em] uppercase'>Registry Vacant</p>
          {searchQuery && (
            <Button
              variant='link'
              onClick={() => setSearchQuery('')}
              className='text-primary mt-2 font-bold'
            >
              Clear Filters
            </Button>
          )}
        </div>
      )}

      <CreateProjectDialog open={showCreateDialog} onOpenChange={handleOpenChange} />

      <EditProjectDialog
        project={editingProject}
        open={Boolean(editingProject)}
        onOpenChange={(open) => {
          if (!open) {
            setEditingProject(null);
          }
        }}
      />

      {/* Simplified Export/Import Dialogs with same style */}
      <Dialog open={showExportDialog} onOpenChange={setShowExportDialog}>
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
              <Select
                value={exportProjectId ?? projectsArray[0]?.id ?? ''}
                onValueChange={(v) => setExportProjectId(v || null)}
              >
                <SelectTrigger className='bg-muted/30 mt-1 h-12 rounded-xl border-none font-bold'>
                  <SelectValue placeholder='Select project' />
                </SelectTrigger>
                <SelectContent>
                  {projectsArray.map((p) => (
                    <SelectItem key={p.id} value={p.id}>
                      {getProjectDisplayName(p)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className='text-muted-foreground text-xs font-bold tracking-widest uppercase'>
                Format
              </Label>
              <Select
                value={exportFormat}
                onValueChange={(v: 'json' | 'csv' | 'full') => setExportFormat(v)}
              >
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
              onClick={handleExport}
              disabled={isExporting || !(exportProjectId ?? projectsArray[0]?.id)}
              className='h-12 w-full rounded-xl font-black tracking-widest uppercase shadow-lg'
            >
              {isExporting ? 'Exporting…' : 'Initialize Dispatch'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showImportDialog} onOpenChange={setShowImportDialog}>
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
              <Select
                value={importMode}
                onValueChange={(v: 'into-existing' | 'full') => setImportMode(v)}
              >
                <SelectTrigger className='bg-muted/30 mt-1 h-12 rounded-xl border-none font-bold'>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='full'>As new project (canonical JSON)</SelectItem>
                  <SelectItem value='into-existing'>
                    Into existing project (items JSON/CSV)
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            {importMode === 'into-existing' && (
              <div>
                <Label className='text-muted-foreground text-xs font-bold tracking-widest uppercase'>
                  Target project
                </Label>
                <Select
                  value={importProjectId ?? projectsArray[0]?.id ?? ''}
                  onValueChange={(v) => setImportProjectId(v || null)}
                >
                  <SelectTrigger className='bg-muted/30 mt-1 h-12 rounded-xl border-none font-bold'>
                    <SelectValue placeholder='Select project' />
                  </SelectTrigger>
                  <SelectContent>
                    {projectsArray.map((p) => (
                      <SelectItem key={p.id} value={p.id}>
                        {getProjectDisplayName(p)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
            <div className='bg-muted/10 group hover:border-primary/50 flex flex-col items-center justify-center rounded-[2rem] border-2 border-dashed p-8 text-center transition-colors'>
              <Upload className='text-muted-foreground group-hover:text-primary mb-4 h-10 w-10 transition-colors' />
              <input
                type='file'
                id='f-up'
                className='hidden'
                accept={importMode === 'full' ? 'application/json,.json' : undefined}
                onChange={(e) => setImportFile(e.target.files?.[0] || null)}
              />
              <Label htmlFor='f-up' className='cursor-pointer'>
                <span className='text-primary text-sm font-bold'>Browse Files</span>
                <p className='text-muted-foreground mt-1 text-[10px] font-medium'>
                  {importFile
                    ? importFile.name
                    : importMode === 'full'
                      ? 'Canonical JSON'
                      : 'JSON or CSV'}
                </p>
              </Label>
            </div>
            <Button
              onClick={handleImport}
              disabled={
                isImporting ||
                !importFile ||
                (importMode === 'into-existing' && !(importProjectId ?? projectsArray[0]?.id))
              }
              className='h-12 w-full rounded-xl font-black tracking-widest uppercase shadow-lg'
            >
              {isImporting ? 'Importing…' : 'Execute Ingestion'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
