import {
  Activity,
  CheckCircle2,
  Copy,
  Eye,
  EyeOff,
  PauseCircle,
  Plus,
  RefreshCw,
  Search,
  Trash2,
  Webhook,
  XCircle,
} from 'lucide-react';
import { useState } from 'react';

import type { CreateWebhookData } from '@/hooks/useWebhooks';
import type { WebhookProvider, WebhookStatus } from '@tracertm/types';

import { Checkbox } from '@/components/ui/checkbox';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  useCreateWebhook,
  useDeleteWebhook,
  useRegenerateWebhookSecret,
  useSetWebhookStatus,
  useWebhookStats,
  useWebhooks,
} from '@/hooks/useWebhooks';
import {
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Input,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Skeleton,
  Textarea,
} from '@tracertm/ui';

interface WebhookIntegrationsViewProps {
  projectId: string;
}

const providerLabels: Record<WebhookProvider, string> = {
  azure_devops: 'Azure DevOps',
  circleci: 'CircleCI',
  custom: 'Custom',
  github_actions: 'GitHub Actions',
  gitlab_ci: 'GitLab CI',
  jenkins: 'Jenkins',
  travis_ci: 'Travis CI',
};

const statusColors: Record<WebhookStatus, string> = {
  active: 'bg-green-500/10 text-green-600 border-green-500/30',
  disabled: 'bg-red-500/10 text-red-600 border-red-500/30',
  paused: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/30',
};

const statusIcons: Record<WebhookStatus, React.ReactNode> = {
  active: <CheckCircle2 className='h-4 w-4' />,
  disabled: <XCircle className='h-4 w-4' />,
  paused: <PauseCircle className='h-4 w-4' />,
};

function copyToClipboard(text: string): void {
  undefined;
}

export function WebhookIntegrationsView({ projectId }: WebhookIntegrationsViewProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<WebhookStatus | 'all'>('all');
  const [providerFilter, setProviderFilter] = useState<WebhookProvider | 'all'>('all');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});

  const { data, isLoading, error } = useWebhooks({
    projectId,
    provider: (providerFilter !== 'all' ? providerFilter : undefined) as any,
    status: statusFilter !== 'all' ? statusFilter : undefined,
  });

  const { data: stats } = useWebhookStats(projectId);
  const createMutation = useCreateWebhook();
  const setStatusMutation = useSetWebhookStatus();
  const regenerateSecretMutation = useRegenerateWebhookSecret();
  const deleteMutation = useDeleteWebhook();

  // Create form state
  const [formData, setFormData] = useState({
    autoCompleteRun: true,
    autoCreateRun: true,
    callbackUrl: '' as string | undefined,
    description: '' as string | undefined,
    name: '',
    provider: 'custom' as WebhookProvider,
    rateLimitPerMinute: 60,
    verifySignatures: true,
  });

  const handleCreate = async () => {
    const payload: CreateWebhookData = {
      autoCompleteRun: formData.autoCompleteRun,
      autoCreateRun: formData.autoCreateRun,
      name: formData.name,
      projectId,
      provider: formData.provider,
      rateLimitPerMinute: formData.rateLimitPerMinute,
      verifySignatures: formData.verifySignatures,
    };
    if (formData.description) {
      payload.description = formData.description;
    }
    if (formData.callbackUrl) {
      payload.callbackUrl = formData.callbackUrl;
    }

    await createMutation.mutateAsync(payload);
    setShowCreateDialog(false);
    setFormData({
      autoCompleteRun: true,
      autoCreateRun: true,
      callbackUrl: '',
      description: '',
      name: '',
      provider: 'custom',
      rateLimitPerMinute: 60,
      verifySignatures: true,
    });
  };

  const toggleSecretVisibility = (id: string) => {
    setShowSecrets((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const filteredWebhooks =
    data?.webhooks.filter((w) => w.name.toLowerCase().includes(searchTerm.toLowerCase())) ?? [];

  if (error) {
    return (
      <div className='p-6'>
        <Card className='border-destructive'>
          <CardContent className='pt-6'>
            <p className='text-destructive'>Error loading webhooks: {error.message}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className='space-y-6 p-6'>
      {/* Header */}
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Webhook Integrations</h1>
          <p className='text-muted-foreground mt-1'>
            Configure CI/CD integrations for automated test result submission
          </p>
        </div>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className='mr-2 h-4 w-4' />
              New Webhook
            </Button>
          </DialogTrigger>
          <DialogContent className='sm:max-w-[500px]'>
            <DialogHeader>
              <DialogTitle>Create Webhook Integration</DialogTitle>
              <DialogDescription>
                Set up a new webhook to receive test results from CI/CD pipelines.
              </DialogDescription>
            </DialogHeader>
            <div className='space-y-4 py-4'>
              <div className='space-y-2'>
                <Label htmlFor='name'>Name</Label>
                <Input
                  id='name'
                  placeholder='e.g., GitHub Actions - Main Pipeline'
                  value={formData.name}
                  onChange={(e) => {
                    setFormData((prev) => ({ ...prev, name: e.target.value }));
                  }}
                />
              </div>
              <div className='space-y-2'>
                <Label htmlFor='description'>Description</Label>
                <Textarea
                  id='description'
                  placeholder='Optional description...'
                  value={formData.description}
                  onChange={(e) => {
                    setFormData((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }));
                  }}
                />
              </div>
              <div className='space-y-2'>
                <Label htmlFor='provider'>Provider</Label>
                <Select
                  value={formData.provider}
                  onValueChange={(v) => {
                    setFormData((prev) => ({
                      ...prev,
                      provider: v as WebhookProvider,
                    }));
                  }}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(providerLabels).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className='space-y-2'>
                <Label htmlFor='callbackUrl'>Callback URL (optional)</Label>
                <Input
                  id='callbackUrl'
                  placeholder='https://...'
                  value={formData.callbackUrl}
                  onChange={(e) => {
                    setFormData((prev) => ({
                      ...prev,
                      callbackUrl: e.target.value,
                    }));
                  }}
                />
              </div>
              <div className='space-y-2'>
                <Label htmlFor='rateLimit'>Rate Limit (requests/min)</Label>
                <Input
                  id='rateLimit'
                  type='number'
                  min={1}
                  max={1000}
                  value={formData.rateLimitPerMinute}
                  onChange={(e) => {
                    setFormData((prev) => ({
                      ...prev,
                      rateLimitPerMinute: Number.parseInt(e.target.value, 10) || 60,
                    }));
                  }}
                />
              </div>
              <div className='flex items-center justify-between'>
                <Label htmlFor='autoCreateRun'>Auto-create test runs</Label>
                <Checkbox
                  id='autoCreateRun'
                  checked={formData.autoCreateRun}
                  onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                    setFormData((prev) => ({ ...prev, autoCreateRun: event.target.checked }));
                  }}
                />
              </div>
              <div className='flex items-center justify-between'>
                <Label htmlFor='autoCompleteRun'>Auto-complete runs</Label>
                <Checkbox
                  id='autoCompleteRun'
                  checked={formData.autoCompleteRun}
                  onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                    setFormData((prev) => ({ ...prev, autoCompleteRun: event.target.checked }));
                  }}
                />
              </div>
              <div className='flex items-center justify-between'>
                <Label htmlFor='verifySignatures'>Require signature verification</Label>
                <Checkbox
                  id='verifySignatures'
                  checked={formData.verifySignatures}
                  onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                    setFormData((prev) => ({ ...prev, verifySignatures: event.target.checked }));
                  }}
                />
              </div>
            </div>
            <DialogFooter>
              <Button
                variant='outline'
                onClick={() => {
                  setShowCreateDialog(false);
                }}
              >
                Cancel
              </Button>
              <Button onClick={handleCreate} disabled={!formData.name || createMutation.isPending}>
                {createMutation.isPending ? 'Creating...' : 'Create Webhook'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className='grid gap-4 md:grid-cols-4'>
        <Card>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
            <CardTitle className='text-sm font-medium'>Total Webhooks</CardTitle>
            <Webhook className='text-muted-foreground h-4 w-4' />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className='h-8 w-16' />
            ) : (
              <div className='text-2xl font-bold'>{stats?.total ?? 0}</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
            <CardTitle className='text-sm font-medium'>Active</CardTitle>
            <CheckCircle2 className='h-4 w-4 text-green-500' />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className='h-8 w-16' />
            ) : (
              <div className='text-2xl font-bold'>{stats?.byStatus?.['active' as any] ?? 0}</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
            <CardTitle className='text-sm font-medium'>Total Requests</CardTitle>
            <Activity className='text-muted-foreground h-4 w-4' />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className='h-8 w-16' />
            ) : (
              <div className='text-2xl font-bold'>{stats?.totalRequests ?? 0}</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
            <CardTitle className='text-sm font-medium'>Success Rate</CardTitle>
            <CheckCircle2 className='text-muted-foreground h-4 w-4' />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className='h-8 w-16' />
            ) : (
              <div className='text-2xl font-bold'>
                {stats && stats.totalRequests > 0
                  ? `${Math.round((stats.successfulRequests / stats.totalRequests) * 100)}%`
                  : 'N/A'}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Webhooks</CardTitle>
          <CardDescription>Manage your webhook integrations for CI/CD pipelines</CardDescription>
        </CardHeader>
        <CardContent>
          <div className='mb-6 flex flex-wrap gap-4'>
            <div className='relative min-w-[200px] flex-1'>
              <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
              <Input
                placeholder='Search webhooks...'
                className='pl-9'
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                }}
              />
            </div>
            <Select
              value={statusFilter}
              onValueChange={(v) => {
                setStatusFilter(v as WebhookStatus | 'all');
              }}
            >
              <SelectTrigger className='w-[140px]'>
                <SelectValue placeholder='Status' />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='all'>All Status</SelectItem>
                <SelectItem value='active'>Active</SelectItem>
                <SelectItem value='paused'>Paused</SelectItem>
                <SelectItem value='disabled'>Disabled</SelectItem>
              </SelectContent>
            </Select>
            <Select
              value={providerFilter}
              onValueChange={(v) => {
                setProviderFilter(v as WebhookProvider | 'all');
              }}
            >
              <SelectTrigger className='w-[160px]'>
                <SelectValue placeholder='Provider' />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='all'>All Providers</SelectItem>
                {Object.entries(providerLabels).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {isLoading ? (
            <div className='space-y-2'>
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className='h-16 w-full' />
              ))}
            </div>
          ) : filteredWebhooks.length === 0 ? (
            <div className='py-12 text-center'>
              <Webhook className='text-muted-foreground/50 mx-auto mb-4 h-12 w-12' />
              <h3 className='text-lg font-semibold'>No webhooks found</h3>
              <p className='text-muted-foreground'>
                {data?.webhooks.length === 0
                  ? 'Create your first webhook to integrate with CI/CD'
                  : 'Try adjusting your filters'}
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Provider</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Secret</TableHead>
                  <TableHead>Requests</TableHead>
                  <TableHead className='text-right'>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredWebhooks.map((webhook) => (
                  <TableRow key={webhook.id}>
                    <TableCell>
                      <div className='font-medium'>{webhook.name}</div>
                      {webhook.description && (
                        <div className='text-muted-foreground max-w-[200px] truncate text-sm'>
                          {webhook.description}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge variant='outline'>{providerLabels[webhook.provider]}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={statusColors[webhook.status]}>
                        <span className='flex items-center gap-1'>
                          {statusIcons[webhook.status]}
                          {webhook.status}
                        </span>
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className='flex items-center gap-2'>
                        <code className='bg-muted rounded px-2 py-1 text-xs'>
                          {showSecrets[webhook.id] ? webhook.webhookSecret : '••••••••••••'}
                        </code>
                        <Button
                          variant='ghost'
                          size='icon'
                          className='h-6 w-6'
                          onClick={() => {
                            toggleSecretVisibility(webhook.id);
                          }}
                        >
                          {showSecrets[webhook.id] ? (
                            <EyeOff className='h-3 w-3' />
                          ) : (
                            <Eye className='h-3 w-3' />
                          )}
                        </Button>
                        <Button
                          variant='ghost'
                          size='icon'
                          className='h-6 w-6'
                          onClick={() => {
                            copyToClipboard(webhook.webhookSecret);
                          }}
                        >
                          <Copy className='h-3 w-3' />
                        </Button>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className='text-sm'>
                        <span className='text-green-600'>{webhook.successfulRequests}</span>
                        {' / '}
                        <span className='text-red-600'>{webhook.failedRequests}</span>
                        {' / '}
                        <span>{webhook.totalRequests}</span>
                      </div>
                    </TableCell>
                    <TableCell className='text-right'>
                      <div className='flex items-center justify-end gap-1'>
                        {webhook.status === 'active' ? (
                          <Button
                            variant='ghost'
                            size='icon'
                            className='h-8 w-8'
                            onClick={() => {
                              setStatusMutation.mutate({
                                id: webhook.id,
                                status: 'paused',
                              });
                            }}
                            title='Pause'
                          >
                            <PauseCircle className='h-4 w-4' />
                          </Button>
                        ) : (
                          <Button
                            variant='ghost'
                            size='icon'
                            className='h-8 w-8'
                            onClick={() => {
                              setStatusMutation.mutate({
                                id: webhook.id,
                                status: 'active',
                              });
                            }}
                            title='Activate'
                          >
                            <CheckCircle2 className='h-4 w-4' />
                          </Button>
                        )}
                        <Button
                          variant='ghost'
                          size='icon'
                          className='h-8 w-8'
                          onClick={() => {
                            regenerateSecretMutation.mutate(webhook.id);
                          }}
                          title='Regenerate Secret'
                        >
                          <RefreshCw className='h-4 w-4' />
                        </Button>
                        <Button
                          variant='ghost'
                          size='icon'
                          className='text-destructive hover:text-destructive h-8 w-8'
                          onClick={() => {
                            if (confirm('Are you sure you want to delete this webhook?')) {
                              deleteMutation.mutate(webhook.id);
                            }
                          }}
                          title='Delete'
                        >
                          <Trash2 className='h-4 w-4' />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
