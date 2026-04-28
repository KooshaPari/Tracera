import React from 'react';

import type { ADR } from '@tracertm/types';

import { ADREditor } from '@/components/specifications/adr/ADREditor';

interface ADRDraft {
  consequences?: string;
  context?: string;
  decision?: string;
  title?: string;
}

interface ADRCreateMutation {
  mutate: (
    payload: {
      consequences: string;
      context: string;
      decision: string;
      projectId: string;
      title: string;
    },
    options?: {
      onSuccess?: () => void;
    },
  ) => void;
}

interface ADRViewEditorProps {
  createADR: ADRCreateMutation;
  onClose: () => void;
  projectId: string;
}

const ADRViewEditor = ({
  createADR,
  onClose,
  projectId,
}: ADRViewEditorProps): React.ReactElement => {
  const handleCancel = React.useCallback(() => {
    onClose();
  }, [onClose]);

  const handleSave = React.useCallback(
    async (data: Partial<ADR>) =>
      new Promise<void>((resolve) => {
        createADR.mutate(
          {
            consequences: data.consequences ?? '',
            context: data.context ?? '',
            decision: data.decision ?? '',
            projectId,
            title: data.title ?? '',
          },
          {
            onSuccess: () => {
              onClose();
              resolve();
            },
          },
        );
      }),
    [createADR, onClose, projectId],
  );

  return (
    <div className='p-6'>
      <ADREditor onSave={handleSave} onCancel={handleCancel} />
    </div>
  );
};

export default ADRViewEditor;
