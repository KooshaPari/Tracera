/**
 * GitHub App installation component.
 */

import { Github, Trash2 } from 'lucide-react';
import { useCallback, useState } from 'react';
import { toast } from 'sonner';

import type { GitHubAppInstallation, GitHubRepo } from '@/api/github';

import { ConfirmationDialog } from '@/components/ui/confirmation-dialog';
import { Button } from '@/components/ui/enterprise-button';
import {
  useDeleteGitHubAppInstallation,
  useGitHubAppInstallUrl,
  useGitHubAppInstallations,
} from '@/hooks/useGitHub';
import { Badge, Card } from '@tracertm/ui';

import { CreateRepoModal } from './CreateRepoModal';
import { RepoSearchCombobox } from './RepoSearchCombobox';

export interface GitHubAppInstallProps {
  accountId: string;
  onRepoSelect?: (repo: GitHubRepo | null) => void;
  selectedRepo?: GitHubRepo | null;
}

function getUninstallErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (
    error &&
    typeof error === 'object' &&
    'message' in error &&
    typeof (error as { message?: string }).message === 'string'
  ) {
    return (error as { message: string }).message;
  }
  return 'Failed to remove installation';
}

export const GitHubAppInstall = function GitHubAppInstall({
  accountId,
  onRepoSelect,
  selectedRepo,
}: GitHubAppInstallProps) {
  const [createRepoOpen, setCreateRepoOpen] = useState(false);
  const [uninstallConfirmId, setUninstallConfirmId] = useState<string | null>(null);
  const [_selectedInstallation, setSelectedInstallation] = useState<string | null>(null);

  const { data: installUrlData, isLoading: installUrlLoading } = useGitHubAppInstallUrl(accountId);
  const { data: installationsData, isLoading: _installationsLoading } =
    useGitHubAppInstallations(accountId);
  const deleteInstallation = useDeleteGitHubAppInstallation();

  const installations: GitHubAppInstallation[] = installationsData?.installations ?? [];

  const handleInstall = useCallback(() => {
    if (installUrlData?.install_url) {
      globalThis.location.href = installUrlData.install_url;
    }
  }, [installUrlData?.install_url]);

  const handleUninstallClick = useCallback((installationId: string) => {
    setUninstallConfirmId(installationId);
  }, []);

  const handleUninstallConfirm = useCallback(async () => {
    if (!uninstallConfirmId) {
      return;
    }
    try {
      await deleteInstallation.mutateAsync(uninstallConfirmId);
      toast.success('GitHub App installation removed');
      setUninstallConfirmId(null);
    } catch (error) {
      toast.error(getUninstallErrorMessage(error));
    }
  }, [deleteInstallation, uninstallConfirmId]);

  const handleUninstallCancel = useCallback(() => {
    setUninstallConfirmId(null);
  }, []);

  const activeInstallation = installations.find(
    (inst: GitHubAppInstallation) => !inst.suspended_at,
  );
  const installationForCreate = activeInstallation ?? installations[0];

  const handleCreateRepoOpen = useCallback((installationId: string) => {
    setSelectedInstallation(installationId);
    setCreateRepoOpen(true);
  }, []);

  const handleRepoSuccess = useCallback(
    (repo: GitHubRepo) => {
      onRepoSelect?.(repo);
    },
    [onRepoSelect],
  );

  const handleUninstallClickFromEvent = useCallback(
    (e: React.MouseEvent<HTMLButtonElement>) => {
      const id = (e.currentTarget as HTMLButtonElement).dataset['installationId'];
      if (id) {
        handleUninstallClick(id);
      }
    },
    [handleUninstallClick],
  );

  const handleConfirmOpenChange = useCallback((open: boolean) => {
    if (!open) {
      setUninstallConfirmId(null);
    }
  }, []);

  const handleOpenCreateRepo = useCallback(() => {
    if (activeInstallation) {
      handleCreateRepoOpen(activeInstallation.id);
    }
  }, [activeInstallation, handleCreateRepoOpen]);

  return (
    <div className='space-y-4'>
      {installations.length === 0 ? (
        <Card className='p-6'>
          <div className='flex items-center justify-between'>
            <div>
              <h3 className='mb-2 text-lg font-semibold'>GitHub App Installation</h3>
              <p className='text-muted-foreground mb-4 text-sm'>
                Install the GitHub App to access repositories and create new ones.
              </p>
            </div>
            <Button onClick={handleInstall} disabled={installUrlLoading} className='gap-2'>
              <Github className='h-4 w-4' />
              {installUrlLoading ? 'Loading...' : 'Install GitHub App'}
            </Button>
          </div>
        </Card>
      ) : (
        <div className='space-y-4'>
          {installations.map((installation: GitHubAppInstallation) => (
            <Card key={installation.id} className='p-4'>
              <div className='flex items-start justify-between'>
                <div className='flex-1'>
                  <div className='mb-2 flex items-center gap-2'>
                    <Github className='h-5 w-5' />
                    <h3 className='font-semibold'>{installation.account_login}</h3>
                    <Badge variant={installation.suspended_at ? 'destructive' : 'default'}>
                      {installation.suspended_at ? 'Suspended' : 'Active'}
                    </Badge>
                    <Badge variant='outline'>{installation.target_type}</Badge>
                  </div>
                  <p className='text-muted-foreground text-sm'>
                    Repository selection: {installation.repository_selection}
                  </p>
                </div>
                <div className='flex items-center gap-2'>
                  <Button
                    variant='ghost'
                    size='sm'
                    data-installation-id={installation.id}
                    onClick={handleUninstallClickFromEvent}
                    disabled={deleteInstallation.isPending}
                  >
                    <Trash2 className='h-4 w-4' />
                  </Button>
                </div>
              </div>
            </Card>
          ))}

          {activeInstallation && (
            <Card className='p-4'>
              <h3 className='mb-4 font-semibold'>Select Repository</h3>
              <RepoSearchCombobox
                accountId={accountId}
                installationId={activeInstallation.id}
                value={selectedRepo ?? null}
                {...(onRepoSelect ? { onSelect: onRepoSelect } : {})}
                onCreateRepo={handleOpenCreateRepo}
                placeholder='Search or select a repository...'
              />
            </Card>
          )}

          {installationForCreate && (
            <CreateRepoModal
              open={createRepoOpen}
              onOpenChange={setCreateRepoOpen}
              installation={installationForCreate}
              accountId={accountId}
              onSuccess={handleRepoSuccess}
            />
          )}
        </div>
      )}

      <ConfirmationDialog
        open={uninstallConfirmId !== null}
        onOpenChange={handleConfirmOpenChange}
        title='Uninstall GitHub App?'
        description='Are you sure you want to uninstall this GitHub App installation? You can reinstall it later.'
        onConfirm={handleUninstallConfirm}
        onCancel={handleUninstallCancel}
        confirmText='Uninstall'
        isLoading={deleteInstallation.isPending}
      />
    </div>
  );
};
