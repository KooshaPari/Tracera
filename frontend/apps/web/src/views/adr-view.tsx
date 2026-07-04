import { useParams } from '@tanstack/react-router';
import React from 'react';

import type { ADR } from '@tracertm/types';

import { useADRs, useCreateADR } from '@/hooks/useSpecifications';

import ADRViewContent from './adr-view-content';
import ADRViewEditor from './adr-view-editor';
import ADRViewHeader from './adr-view-header';

const EMPTY_ADRS: ADR[] = [];

interface ADRViewState {
  isEditing: boolean;
  viewMode: 'list' | 'timeline';
}

interface ADRViewHandlers {
  handleCloseEditor: () => void;
  handleCreate: () => void;
  handleViewChange: (nextView: 'list' | 'timeline') => void;
}

const resolveAdrs = (adrsData: { adrs?: ADR[] } | undefined): ADR[] => {
  if (adrsData && Array.isArray(adrsData.adrs)) {
    return adrsData.adrs;
  }

  return EMPTY_ADRS;
};

const buildHandlers = (
  setViewState: React.Dispatch<React.SetStateAction<ADRViewState>>,
): ADRViewHandlers => ({
  handleCloseEditor: (): void => {
    setViewState((prevState) => ({
      isEditing: false,
      viewMode: prevState.viewMode,
    }));
  },
  handleCreate: (): void => {
    setViewState((prevState) => ({
      isEditing: true,
      viewMode: prevState.viewMode,
    }));
  },
  handleViewChange: (nextView: 'list' | 'timeline'): void => {
    setViewState(() => ({
      isEditing: false,
      viewMode: nextView,
    }));
  },
});

const ADRView = (): React.ReactNode => {
  const { projectId } = useParams({ strict: false });
  const normalizedProjectId = projectId ?? '';
  const { data: adrsData } = useADRs({
    projectId: normalizedProjectId,
  });
  const adrs = React.useMemo(() => resolveAdrs(adrsData), [adrsData]);
  const createADR = useCreateADR();
  const [viewState, setViewState] = React.useState<ADRViewState>(() => ({
    isEditing: false,
    viewMode: 'list',
  }));
  const handlers = React.useMemo(() => buildHandlers(setViewState), [setViewState]);

  if (viewState.isEditing) {
    return (
      <ADRViewEditor
        createADR={createADR}
        onClose={handlers.handleCloseEditor}
        projectId={normalizedProjectId}
      />
    );
  }

  return (
    <div className='space-y-6 p-6'>
      <ADRViewHeader
        onCreate={handlers.handleCreate}
        onViewChange={handlers.handleViewChange}
        viewMode={viewState.viewMode}
      />
      <ADRViewContent adrs={adrs} viewMode={viewState.viewMode} />
    </div>
  );
};

export default ADRView;
