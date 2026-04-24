import type { ReactElement } from 'react';

import { useCallback, useMemo, useState } from 'react';

import type { IntegrationCredential } from '@tracertm/types';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';
import { useDeleteCredential, useValidateCredential } from '@/hooks/useIntegrations';
import CredentialRow from '@/pages/projects/views/integrations-view/tabs/credentials/CredentialRow';

interface CredentialsTabProps {
  credentials: IntegrationCredential[];
  isLoading: boolean;
}

interface CredentialActionsState {
  confirmDeleteId: string | undefined;
  isValidating: boolean;
  onCancelDelete: () => void;
  onConfirmDelete: (credentialId: string) => void;
  onRequestDelete: (credentialId: string) => void;
  onValidate: (credentialId: string) => void;
}

function useCredentialActions(): CredentialActionsState {
  const deleteCredential = useDeleteCredential();
  const validateCredential = useValidateCredential();
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | undefined>();

  const onRequestDelete = useCallback((credentialId: string) => {
    setConfirmDeleteId(credentialId);
  }, []);

  const onCancelDelete = useCallback(() => {
    setConfirmDeleteId(undefined);
  }, []);

  const onConfirmDelete = useCallback(
    (credentialId: string) => {
      deleteCredential.mutate(credentialId);
      setConfirmDeleteId(undefined);
    },
    [deleteCredential],
  );

  const onValidate = useCallback(
    (credentialId: string) => {
      validateCredential.mutate(credentialId);
    },
    [validateCredential],
  );

  return {
    confirmDeleteId,
    isValidating: validateCredential.isPending,
    onCancelDelete,
    onConfirmDelete,
    onRequestDelete,
    onValidate,
  };
}

function renderEmptyState(): ReactElement {
  return (
    <div className='py-12 text-center text-gray-500'>
      No credentials configured. Connect a provider from the Overview tab.
    </div>
  );
}

function previewCredentialIdentifier(credential: IntegrationCredential): string {
  const previewLength = 8;
  if (credential.providerUserId !== undefined && credential.providerUserId !== '') {
    return credential.providerUserId;
  }
  return credential.id.slice(0, previewLength);
}

export default function CredentialsTab({
  credentials,
  isLoading,
}: CredentialsTabProps): ReactElement {
  const {
    confirmDeleteId,
    isValidating,
    onCancelDelete,
    onConfirmDelete,
    onRequestDelete,
    onValidate,
  } = useCredentialActions();

  const sortedCredentials = useMemo(
    () =>
      credentials.toSorted((left, right) =>
        previewCredentialIdentifier(left).localeCompare(previewCredentialIdentifier(right)),
      ),
    [credentials],
  );

  if (isLoading) {
    return (
      <div className='flex justify-center py-8'>
        <LoadingSpinner text='Loading credentials...' />
      </div>
    );
  }

  if (sortedCredentials.length === 0) {
    return renderEmptyState();
  }

  return (
    <div className='space-y-4'>
      {sortedCredentials.map((credential) => (
        <CredentialRow
          key={credential.id}
          credential={credential}
          isConfirmingDelete={confirmDeleteId === credential.id}
          isValidating={isValidating}
          onCancelDelete={onCancelDelete}
          onConfirmDelete={onConfirmDelete}
          onRequestDelete={onRequestDelete}
          onValidate={onValidate}
        />
      ))}
    </div>
  );
}
