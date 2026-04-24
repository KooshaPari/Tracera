import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { logger } from '@/lib/logger';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { Label } from '@tracertm/ui/components/Label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';
import { Textarea } from '@tracertm/ui/components/Textarea';

import { api } from '../api/endpoints';

type ImportFormat = 'json' | 'csv';

export const ImportView = () => {
  // Note: projectId would come from route params in actual implementation
  // For now, we'll use state
  const [projectId, setProjectId] = useState<string>('');
  const [format, setFormat] = useState<ImportFormat>('json');
  const [data, setData] = useState('');
  const [_file, setFile] = useState<File | null>(null);

  const projectsQuery = useQuery({
    queryFn: async () => api.projects.list(),
    queryKey: ['projects'],
  });

  const importMutation = useMutation({
    mutationFn: async ({
      projectId,
      format,
      data,
    }: {
      projectId: string;
      format: ImportFormat;
      data: string;
    }) => api.exportImport.import(projectId, format, data),
    onError: (error) => {
      logger.error('Import failed:', error);
      alert('Import failed. Please check your data format and try again.');
    },
    onSuccess: (result) => {
      alert(`Import completed!\nImported: ${result.imported_count}\nErrors: ${result.error_count}`);
      if (result.errors.length > 0) {
        logger.error('Import errors:', result.errors);
      }
      setData('');
      setFile(null);
    },
  });

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) {
      return;
    }

    setFile(selectedFile);
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setData(content);
    };
    reader.readAsText(selectedFile);
  };

  const handleImport = () => {
    if (!projectId) {
      alert('Please select a project');
      return;
    }

    if (!data.trim()) {
      alert('Please provide data to import');
      return;
    }

    importMutation.mutate({ data, format, projectId });
  };

  const handleProjectSelect = (value: string) => {
    setProjectId(value === 'none' ? '' : value);
  };

  const handleFormatChange = (v: string) => {
    setFormat(v as ImportFormat);
  };

  const handleDataChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setData(e.target.value);
  };

  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-3xl font-bold'>Import Project Data</h1>
        <p className='text-muted-foreground'>Import project data from JSON or CSV files</p>
      </div>

      <Card className='p-6'>
        <div className='space-y-4'>
          <div>
            <label htmlFor='project-select' className='mb-2 block text-sm font-medium'>
              Project
            </label>
            <Select value={projectId || 'none'} onValueChange={handleProjectSelect}>
              <SelectTrigger id='project-select' className='mt-2'>
                <SelectValue placeholder='Select a project' />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='none'>Select a project</SelectItem>
                {projectsQuery.data?.map((project) => (
                  <SelectItem key={project.id} value={project.id}>
                    {project.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <label htmlFor='format-select' className='mb-2 block text-sm font-medium'>
              Import Format
            </label>
            <Select value={format} onValueChange={handleFormatChange}>
              <SelectTrigger id='format-select' className='mt-2'>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='json'>JSON</SelectItem>
                <SelectItem value='csv'>CSV</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label htmlFor='file-input' className='mb-2 block text-sm font-medium'>
              Upload File (Optional)
            </label>
            <input
              id='file-input'
              type='file'
              accept={format === 'json' ? '.json' : '.csv'}
              onChange={handleFileSelect}
              className='text-muted-foreground file:bg-primary/10 file:text-primary hover:file:bg-primary/20 mt-2 block w-full text-sm file:mr-4 file:rounded-md file:border-0 file:px-4 file:py-2 file:text-sm file:font-semibold'
            />
          </div>

          <div>
            <Label htmlFor='data-input'>Or Paste Data</Label>
            <Textarea
              id='data-input'
              value={data}
              onChange={handleDataChange}
              placeholder={format === 'json' ? 'Paste JSON data here...' : 'Paste CSV data here...'}
              className='mt-2 min-h-[200px] font-mono text-sm'
            />
          </div>

          <div className='space-y-2'>
            <h3 className='font-medium'>Format Requirements:</h3>
            <ul className='text-muted-foreground list-inside list-disc space-y-1 text-sm'>
              {format === 'json' ? (
                <>
                  <li>JSON must contain an "items" array</li>
                  <li>Each item should have: title, view, type, status</li>
                  <li>
                    Example:{' '}
                    {
                      '{"items": [{"title": "Item 1", "view": "FEATURE", "type": "feature", "status": "todo"}]}'
                    }
                  </li>
                </>
              ) : (
                <>
                  <li>CSV must have headers: ID, Title, View, Type, Status, Description</li>
                  <li>First row should be column headers</li>
                  <li>Each subsequent row is an item</li>
                </>
              )}
            </ul>
          </div>

          <Button
            onClick={handleImport}
            disabled={!projectId || !data.trim() || importMutation.isPending}
          >
            {importMutation.isPending ? 'Importing...' : 'Import Data'}
          </Button>
        </div>
      </Card>

      {importMutation.data && (
        <Card className='bg-green-50 p-6 dark:bg-green-900/20'>
          <h3 className='mb-2 font-medium'>Import Results</h3>
          <div className='space-y-1 text-sm'>
            <p>
              <strong>Imported:</strong> {importMutation.data.imported_count} items
            </p>
            <p>
              <strong>Errors:</strong> {importMutation.data.error_count}
            </p>
            {importMutation.data.errors.length > 0 && (
              <div className='mt-2'>
                <p className='font-medium'>Error Details:</p>
                <ul className='list-inside list-disc text-red-600'>
                  {importMutation.data.errors.map((error, idx) => (
                    <li key={idx}>{error}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};
