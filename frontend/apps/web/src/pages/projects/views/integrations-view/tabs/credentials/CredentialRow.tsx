import type { ReactElement } from 'react';

import { useCallback } from 'react';

import type { IntegrationCredential } from '@tracertm/types';

import ProviderIcon from '@/pages/projects/views/integrations-view/components/ProviderIcon';
import StatusBadge from '@/pages/projects/views/integrations-view/components/StatusBadge';

function credentialScopesText(scopes: string[] | undefined): string {
  if (scopes === undefined) {
    return 'none';
  }
  if (scopes.length === 0) {
    return 'none';
  }
  return scopes.join(', ');
}

function lastValidatedText(lastValidatedAt: string | undefined): string | undefined {
  if (lastValidatedAt === undefined) {
    return undefined;
  }
  return `Last validated: ${new Date(lastValidatedAt).toLocaleString()}`;
}

function renderDeleteActions({
  isConfirmingDelete,
  onCancelDelete,
  onConfirmDelete,
  onDelete,
}: {
  isConfirmingDelete: boolean;
  onCancelDelete: () => void;
  onConfirmDelete: () => void;
  onDelete: () => void;
}): ReactElement {
  if (isConfirmingDelete) {
    return (
      <div className='flex items-center space-x-2'>
        <button
          type='button'
          onClick={onConfirmDelete}
          className='rounded bg-red-100 px-3 py-1 text-sm text-red-700 hover:bg-red-200'
        >
          Confirm
        </button>
        <button
          type='button'
          onClick={onCancelDelete}
          className='rounded bg-gray-100 px-3 py-1 text-sm text-gray-700 hover:bg-gray-200'
        >
          Cancel
        </button>
      </div>
    );
  }

  return (
    <button
      type='button'
      onClick={onDelete}
      className='rounded bg-red-100 px-3 py-1 text-sm text-red-700 hover:bg-red-200'
    >
      Delete
    </button>
  );
}

interface CredentialRowProps {
  credential: IntegrationCredential;
  isConfirmingDelete: boolean;
  isValidating: boolean;
  onCancelDelete: () => void;
  onConfirmDelete: (credentialId: string) => void;
  onRequestDelete: (credentialId: string) => void;
  onValidate: (credentialId: string) => void;
}

export default function CredentialRow({
  credential,
  isConfirmingDelete,
  isValidating,
  onCancelDelete,
  onConfirmDelete,
  onRequestDelete,
  onValidate,
}: CredentialRowProps): ReactElement {
  const validatedText = lastValidatedText(credential.lastValidatedAt);
  const scopesText = credentialScopesText(credential.scopes);

  const handleValidateClick = useCallback(() => {
    onValidate(credential.id);
  }, [credential.id, onValidate]);

  const handleDeleteClick = useCallback(() => {
    onRequestDelete(credential.id);
  }, [credential.id, onRequestDelete]);

  const handleConfirmDeleteClick = useCallback(() => {
    onConfirmDelete(credential.id);
  }, [credential.id, onConfirmDelete]);

  return (
    <div className='rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800'>
      <div className='flex items-center justify-between'>
        <div className='flex items-center space-x-4'>
          <ProviderIcon provider={credential.provider} />
          <div>
            <div className='font-medium capitalize'>{credential.provider.replace('_', ' ')}</div>
            <div className='text-sm text-gray-500'>
              Type: {credential.credentialType} | Scopes: {scopesText}
            </div>
            {validatedText !== undefined && (
              <div className='text-xs text-gray-400'>{validatedText}</div>
            )}
          </div>
        </div>
        <div className='flex items-center space-x-2'>
          <StatusBadge status={credential.status} />
          <button
            type='button'
            onClick={handleValidateClick}
            disabled={isValidating}
            className='rounded bg-blue-100 px-3 py-1 text-sm text-blue-700 hover:bg-blue-200'
          >
            Validate
          </button>
          {renderDeleteActions({
            isConfirmingDelete,
            onCancelDelete,
            onConfirmDelete: handleConfirmDeleteClick,
            onDelete: handleDeleteClick,
          })}
        </div>
      </div>
    </div>
  );
}
