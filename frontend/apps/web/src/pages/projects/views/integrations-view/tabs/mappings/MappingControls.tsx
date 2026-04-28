import type { ChangeEvent, ReactElement } from 'react';

import { useCallback } from 'react';

import type { MappingFormState } from '@/pages/projects/views/integrations-view/tabs/mappings/useMappingFormState';
import type { IntegrationCredential, IntegrationProvider } from '@tracertm/types';

const PROVIDER_SELECT_ID = 'integration-provider';
const CREDENTIAL_SELECT_ID = 'integration-credential';
const ID_PREVIEW_LENGTH = 8;

function credentialLabel(credential: IntegrationCredential): string {
  const { providerUserId, id } = credential;
  if (providerUserId !== undefined && providerUserId !== '') {
    return providerUserId;
  }
  return id.slice(0, ID_PREVIEW_LENGTH);
}

function renderProviderOptions(): ReactElement[] {
  return [
    <option key='github' value='github'>
      GitHub
    </option>,
    <option key='github_projects' value='github_projects'>
      GitHub Projects
    </option>,
    <option key='linear' value='linear'>
      Linear
    </option>,
  ];
}

function renderCredentialOptions({
  provider,
  credentials,
}: {
  provider: IntegrationProvider;
  credentials: IntegrationCredential[];
}): ReactElement[] {
  if (credentials.length === 0) {
    return [
      <option key='none' value=''>
        No credentials for {provider}.
      </option>,
    ];
  }

  return credentials.map((credential) => (
    <option key={credential.id} value={credential.id}>
      {credentialLabel(credential)}
    </option>
  ));
}

interface MappingControlsProps {
  formState: MappingFormState;
}

export default function MappingControls({ formState }: MappingControlsProps): ReactElement {
  const { activeCredentialId, credentials, provider, setCredentialId, setProviderFromString } =
    formState;

  const handleProviderChange = useCallback(
    (event: ChangeEvent<HTMLSelectElement>) => {
      setProviderFromString(event.target.value);
    },
    [setProviderFromString],
  );

  const handleCredentialChange = useCallback(
    (event: ChangeEvent<HTMLSelectElement>) => {
      setCredentialId(event.target.value);
    },
    [setCredentialId],
  );

  return (
    <div className='grid grid-cols-1 gap-4 md:grid-cols-3'>
      <div className='space-y-2'>
        <label htmlFor={PROVIDER_SELECT_ID} className='text-xs font-semibold text-gray-500'>
          Provider
        </label>
        <select
          id={PROVIDER_SELECT_ID}
          className='w-full rounded-md border bg-white px-3 py-2 text-sm dark:bg-gray-900'
          value={provider}
          onChange={handleProviderChange}
        >
          {renderProviderOptions()}
        </select>
      </div>

      <div className='space-y-2 md:col-span-2'>
        <label htmlFor={CREDENTIAL_SELECT_ID} className='text-xs font-semibold text-gray-500'>
          Credential
        </label>
        <select
          id={CREDENTIAL_SELECT_ID}
          className='w-full rounded-md border bg-white px-3 py-2 text-sm dark:bg-gray-900'
          value={activeCredentialId}
          onChange={handleCredentialChange}
        >
          {renderCredentialOptions({ provider, credentials })}
        </select>
      </div>
    </div>
  );
}
