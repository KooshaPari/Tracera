import { useNavigate, useSearch } from '@tanstack/react-router';
import { Save } from 'lucide-react';
import { Suspense, lazy, useEffect, useMemo, useState } from 'react';
import { toast } from 'sonner';

import { useProject, useUpdateProject } from '@/hooks/useProjects';
import { ChunkLoadingSkeleton } from '@/lib/lazy-loading';
import { getProjectDisplayName } from '@/lib/project-name-utils';
import { Button } from '@tracertm/ui/components/Button';
import { Input } from '@tracertm/ui/components/Input';
import { Label } from '@tracertm/ui/components/Label';
import { Separator } from '@tracertm/ui/components/Separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui/components/Tabs';
import { Textarea } from '@tracertm/ui/components/Textarea';

const IntegrationsView = lazy(async () =>
  import('@/pages/projects/views/IntegrationsView').then((m) => ({
    default: m.default ?? m.IntegrationsView,
  })),
);

export function ProjectSettingsView({ projectId }: { projectId: string }) {
  const { data: project } = useProject(projectId);
  const navigate = useNavigate();
  const search = useSearch({ strict: false });
  const updateProject = useUpdateProject();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  useEffect(() => {
    if (project) {
      setName(project.name || '');
      setDescription(project.description ?? '');
    }
  }, [project]);

  const activeTab = useMemo(() => {
    if (search?.tab === 'integrations') {
      return 'integrations';
    }
    return 'general';
  }, [search]);

  const handleSave = async () => {
    if (!project) {
      return;
    }
    try {
      await updateProject.mutateAsync({
        data: { description: description.trim(), name: name.trim() },
        id: project.id,
      });
      toast.success('Project settings updated');
    } catch {
      toast.error('Failed to update project settings');
    }
  };

  if (!project) {
    return <ChunkLoadingSkeleton message='Loading project settings...' />;
  }

  return (
    <div className='animate-in fade-in mx-auto max-w-5xl space-y-8 p-6 pb-24 duration-500'>
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-black tracking-tight uppercase'>Project Settings</h1>
          <p className='text-muted-foreground text-[10px] font-medium tracking-widest uppercase'>
            {getProjectDisplayName(project)}
          </p>
        </div>
        <Button
          variant='ghost'
          className='text-[10px] font-black tracking-widest uppercase'
          onClick={async () => navigate({ to: `/projects/${project.id}` })}
        >
          Back to Overview
        </Button>
      </div>

      <Tabs defaultValue={activeTab} className='space-y-6'>
        <TabsList className='w-full justify-start gap-2 bg-transparent'>
          <TabsTrigger value='general'>General</TabsTrigger>
          <TabsTrigger value='integrations'>Integrations</TabsTrigger>
        </TabsList>

        <TabsContent value='general' className='space-y-6'>
          <div className='space-y-1'>
            <h2 className='text-xl font-black tracking-tight uppercase'>Project Identity</h2>
            <p className='text-muted-foreground text-sm font-medium'>
              Edit project metadata and registry details.
            </p>
          </div>
          <Separator className='bg-border/50' />
          <div className='space-y-4'>
            <div className='space-y-2'>
              <Label className='text-muted-foreground ml-1 text-[10px] font-black tracking-widest uppercase'>
                Project Name
              </Label>
              <Input
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                }}
                className='bg-muted/30 h-12 rounded-xl border-none font-bold'
              />
            </div>
            <div className='space-y-2'>
              <Label className='text-muted-foreground ml-1 text-[10px] font-black tracking-widest uppercase'>
                Description
              </Label>
              <Textarea
                value={description}
                onChange={(e) => {
                  setDescription(e.target.value);
                }}
                className='bg-muted/30 min-h-[120px] rounded-xl border-none p-4 font-medium'
              />
            </div>
            <div className='flex justify-end'>
              <Button
                onClick={handleSave}
                disabled={updateProject.isPending}
                className='h-12 gap-2 rounded-xl px-8 text-[10px] font-black tracking-widest uppercase'
              >
                <Save className='h-4 w-4' />
                Save
              </Button>
            </div>
          </div>
        </TabsContent>

        <TabsContent value='integrations' className='space-y-4'>
          <div className='space-y-1'>
            <h2 className='text-xl font-black tracking-tight uppercase'>Project Integrations</h2>
            <p className='text-muted-foreground text-sm font-medium'>
              Link repositories or planning systems and manage sync operations.
            </p>
          </div>
          <Separator className='bg-border/50' />
          <Suspense fallback={<ChunkLoadingSkeleton message='Loading integrations...' />}>
            <IntegrationsView projectId={project.id} mode='project' initialTab='mappings' />
          </Suspense>
        </TabsContent>
      </Tabs>
    </div>
  );
}
