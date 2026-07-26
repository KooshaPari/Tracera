import type { ChangeEvent, MouseEvent, ReactElement } from 'react';

import type { MappingFormState } from '@/pages/projects/views/integrations-view/tabs/mappings/useMappingFormState';
import type { GitHubProject, GitHubRepo, LinearProject } from '@tracertm/types';

import { logger } from '@/lib/logger';
import { useMappingSourceHandlers } from '@/pages/projects/views/integrations-view/tabs/mappings/useMappingSourceHandlers';

interface MappingSourcesProps {
  formState: MappingFormState;
}

function renderRepoGrid({
  repos,
  onLinkClick,
}: {
  repos: GitHubRepo[];
  onLinkClick: (event: MouseEvent<HTMLButtonElement>) => void;
}): ReactElement {
  return (
    <div className='grid grid-cols-1 gap-3 md:grid-cols-2'>
      {repos.map((repo) => (
        <div
          key={repo.id}
          className='flex items-center justify-between gap-3 rounded-lg border p-3'
        >
          <div>
            <div className='text-sm font-medium'>{repo.fullName}</div>
            <div className='text-xs text-gray-500'>{repo.description ?? 'No description'}</div>
          </div>
          <button
            type='button'
            data-repo-full-name={repo.fullName}
            data-repo-url={repo.htmlUrl}
            onClick={onLinkClick}
            className='rounded bg-blue-100 px-3 py-1 text-xs text-blue-700 hover:bg-blue-200'
          >
            Link
          </button>
        </div>
      ))}
    </div>
  );
}

function renderGitHubRepoList({
  repos,
  repoSearch,
  onRepoSearchChange,
  onRepoLinkClick,
}: {
  repos: GitHubRepo[];
  repoSearch: string;
  onRepoSearchChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onRepoLinkClick: (event: MouseEvent<HTMLButtonElement>) => void;
}): ReactElement {
  return (
    <div className='space-y-3'>
      <input
        className='w-full rounded-md border bg-white px-3 py-2 text-sm dark:bg-gray-900'
        placeholder='Search repositories...'
        value={repoSearch}
        onChange={onRepoSearchChange}
      />
      {renderRepoGrid({ repos, onLinkClick: onRepoLinkClick })}
    </div>
  );
}

function renderOwnerControls({
  projectOwner,
  projectOwnerIsOrg,
  onOwnerChange,
  onOrgToggle,
}: {
  projectOwner: string;
  projectOwnerIsOrg: boolean;
  onOwnerChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onOrgToggle: (event: ChangeEvent<HTMLInputElement>) => void;
}): ReactElement {
  return (
    <div className='grid grid-cols-1 gap-3 md:grid-cols-3'>
      <input
        className='w-full rounded-md border bg-white px-3 py-2 text-sm md:col-span-2 dark:bg-gray-900'
        placeholder='Owner or org (e.g. vercel)'
        value={projectOwner}
        onChange={onOwnerChange}
      />
      <label className='flex items-center gap-2 text-xs text-gray-600'>
        <input type='checkbox' checked={projectOwnerIsOrg} onChange={onOrgToggle} />
        Org owner
      </label>
    </div>
  );
}

function renderProjectGrid({
  projects,
  onLinkClick,
}: {
  projects: GitHubProject[];
  onLinkClick: (event: MouseEvent<HTMLButtonElement>) => void;
}): ReactElement {
  return (
    <div className='grid grid-cols-1 gap-3 md:grid-cols-2'>
      {projects.map((project) => (
        <div
          key={project.id}
          className='flex items-center justify-between gap-3 rounded-lg border p-3'
        >
          <div>
            <div className='text-sm font-medium'>{project.title}</div>
            <div className='text-xs text-gray-500'>{project.description ?? 'No description'}</div>
          </div>
          <button
            type='button'
            data-project-id={project.id}
            data-project-title={project.title}
            data-project-url={project.url ?? ''}
            onClick={onLinkClick}
            className='rounded bg-blue-100 px-3 py-1 text-xs text-blue-700 hover:bg-blue-200'
          >
            Link
          </button>
        </div>
      ))}
    </div>
  );
}

function renderGitHubProjectList({
  projects,
  projectOwner,
  projectOwnerIsOrg,
  onOwnerChange,
  onOrgToggle,
  onProjectLinkClick,
}: {
  projects: GitHubProject[];
  projectOwner: string;
  projectOwnerIsOrg: boolean;
  onOwnerChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onOrgToggle: (event: ChangeEvent<HTMLInputElement>) => void;
  onProjectLinkClick: (event: MouseEvent<HTMLButtonElement>) => void;
}): ReactElement {
  return (
    <div className='space-y-3'>
      {renderOwnerControls({ projectOwner, projectOwnerIsOrg, onOwnerChange, onOrgToggle })}
      {renderProjectGrid({ projects, onLinkClick: onProjectLinkClick })}
    </div>
  );
}

function renderLinearProjectGrid({
  projects,
  onLinkClick,
}: {
  projects: LinearProject[];
  onLinkClick: (event: MouseEvent<HTMLButtonElement>) => void;
}): ReactElement {
  return (
    <div className='grid grid-cols-1 gap-3 md:grid-cols-2'>
      {projects.map((project) => (
        <div
          key={project.id}
          className='flex items-center justify-between gap-3 rounded-lg border p-3'
        >
          <div>
            <div className='text-sm font-medium'>{project.name}</div>
            <div className='text-xs text-gray-500'>{project.description ?? 'No description'}</div>
          </div>
          <button
            type='button'
            data-linear-project-id={project.id}
            data-linear-project-name={project.name}
            data-linear-project-url={project.url ?? ''}
            onClick={onLinkClick}
            className='rounded bg-blue-100 px-3 py-1 text-xs text-blue-700 hover:bg-blue-200'
          >
            Link
          </button>
        </div>
      ))}
    </div>
  );
}

export default function MappingSources({ formState }: MappingSourcesProps): ReactElement {
  const {
    githubProjects,
    githubRepos,
    linearProjects,
    projectOwner,
    projectOwnerIsOrg,
    provider,
    repoSearch,
  } = formState;

  const {
    onRepoLinkClick,
    onRepoSearchChange,
    onOwnerChange,
    onOrgToggle,
    onProjectLinkClick,
    onLinearProjectLinkClick,
  } = useMappingSourceHandlers(formState);

  if (provider === 'github') {
    return renderGitHubRepoList({
      repos: githubRepos,
      repoSearch,
      onRepoSearchChange,
      onRepoLinkClick,
    });
  }

  if (provider === 'github_projects') {
    return renderGitHubProjectList({
      projects: githubProjects,
      projectOwner,
      projectOwnerIsOrg,
      onOwnerChange,
      onOrgToggle,
      onProjectLinkClick,
    });
  }

  if (provider === 'linear') {
    return renderLinearProjectGrid({
      projects: linearProjects,
      onLinkClick: onLinearProjectLinkClick,
    });
  }

  logger.warn('Unknown integration provider selected:', provider);
  return <div className='text-sm text-gray-500'>Select a provider to view sources.</div>;
}
