/**
 * PageHeader Component Tests
 *
 * Comprehensive tests covering:
 * - Title and description rendering
 * - Icon display
 * - Actions rendering
 * - Breadcrumbs navigation
 * - Layout and styling
 * - Edge cases
 */

import type { ComponentProps } from 'react';

import { render, screen } from '@testing-library/react';
import { FileText, Plus } from 'lucide-react';
import { describe, expect, it } from 'vitest';

import { PageHeader } from '@/components/layout/PageHeader';

const renderHeader = (props: ComponentProps<typeof PageHeader>) =>
  render(<PageHeader {...props} />);

describe('PageHeader Component', () => {
  describe('Basic Rendering', () => {
    it('should render with title only', () => {
      renderHeader({ title: 'Dashboard' });

      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });

    it('should render title with correct styling', () => {
      renderHeader({ title: 'Dashboard' });

      const title = screen.getByText('Dashboard');
      expect(title).toHaveClass('text-2xl', 'font-bold');
    });

    it('should render description when provided', () => {
      renderHeader({
        description: 'Manage all your requirements projects',
        title: 'Projects',
      });

      expect(screen.getByText('Manage all your requirements projects')).toBeInTheDocument();
    });

    it('should not render description when not provided', () => {
      const { container } = renderHeader({ title: 'Dashboard' });

      const description = container.querySelector('.text-sm.text-gray-600');
      expect(description).not.toBeInTheDocument();
    });
  });

  describe('Icon Display', () => {
    it('should render icon when provided', () => {
      renderHeader({
        icon: <FileText data-testid='header-icon' />,
        title: 'Documents',
      });

      expect(screen.getByTestId('header-icon')).toBeInTheDocument();
    });

    it('should not render icon container when icon not provided', () => {
      const { container } = renderHeader({ title: 'Dashboard' });

      const iconContainer = container.querySelector('.w-10.h-10');
      expect(iconContainer).not.toBeInTheDocument();
    });

    it('should render icon with correct container styles', () => {
      const { container } = renderHeader({
        icon: <FileText data-testid='header-icon' />,
        title: 'Documents',
      });

      const iconContainer = container.querySelector('.w-10.h-10');
      expect(iconContainer).toHaveClass('rounded-lg', 'bg-primary-100', 'dark:bg-primary-900');
    });

    it('should render icon with proper color classes', () => {
      const { container } = renderHeader({
        icon: <FileText data-testid='header-icon' />,
        title: 'Documents',
      });

      const iconContainer = container.querySelector('.text-primary-600');
      expect(iconContainer).toBeInTheDocument();
    });
  });

  describe('Actions', () => {
    it('should render actions when provided', () => {
      renderHeader({
        actions: (
          <button data-testid='create-button'>
            <Plus /> Create
          </button>
        ),
        title: 'Projects',
      });

      expect(screen.getByTestId('create-button')).toBeInTheDocument();
    });

    it('should render multiple actions', () => {
      renderHeader({
        actions: (
          <>
            <button data-testid='action-1'>Action 1</button>
            <button data-testid='action-2'>Action 2</button>
            <button data-testid='action-3'>Action 3</button>
          </>
        ),
        title: 'Projects',
      });

      expect(screen.getByTestId('action-1')).toBeInTheDocument();
      expect(screen.getByTestId('action-2')).toBeInTheDocument();
      expect(screen.getByTestId('action-3')).toBeInTheDocument();
    });

    it('should not render actions container when actions not provided', () => {
      const { container } = renderHeader({ title: 'Dashboard' });

      const actionsContainer = container.querySelector('.flex.items-center.space-x-2');
      expect(actionsContainer).not.toBeInTheDocument();
    });

    it('should render complex action components', () => {
      renderHeader({
        actions: (
          <div data-testid='complex-actions' className='flex gap-2'>
            <button>Export</button>
            <button>Import</button>
          </div>
        ),
        title: 'Projects',
      });

      expect(screen.getByTestId('complex-actions')).toBeInTheDocument();
    });
  });

  describe('Breadcrumbs', () => {
    it('should render breadcrumbs when provided', () => {
      renderHeader({
        breadcrumbs: [
          { href: '/', label: 'Home' },
          { href: '/projects', label: 'Projects' },
          { label: 'Project 1' },
        ],
        title: 'Project Details',
      });

      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByText('Projects')).toBeInTheDocument();
      expect(screen.getByText('Project 1')).toBeInTheDocument();
    });

    it('should render clickable breadcrumb links', () => {
      renderHeader({
        breadcrumbs: [{ href: '/', label: 'Home' }, { label: 'Projects' }],
        title: 'Project Details',
      });

      const homeLink = screen.getByText('Home');
      expect(homeLink).toBeInTheDocument();
      expect(homeLink.tagName).toBe('A');
      expect(homeLink).toHaveAttribute('href', '/');
    });

    it('should render current breadcrumb without link', () => {
      renderHeader({
        breadcrumbs: [{ href: '/', label: 'Home' }, { label: 'Current Page' }],
        title: 'Project Details',
      });

      const currentCrumb = screen.getByText('Current Page');
      expect(currentCrumb.tagName).toBe('SPAN');
      expect(currentCrumb).not.toHaveAttribute('href');
    });

    it('should render breadcrumb separators', () => {
      const { container } = renderHeader({
        breadcrumbs: [
          { href: '/', label: 'Home' },
          { href: '/projects', label: 'Projects' },
          { label: 'Current' },
        ],
        title: 'Project Details',
      });

      const separators = container.querySelectorAll('svg');
      // Should have 2 separators (between 3 items)
      expect(separators.length).toBeGreaterThanOrEqual(2);
    });

    it('should not render breadcrumbs when not provided', () => {
      const { container } = renderHeader({ title: 'Dashboard' });

      const nav = container.querySelector('nav[aria-label="Breadcrumb"]');
      expect(nav).not.toBeInTheDocument();
    });

    it('should not render breadcrumbs when empty array', () => {
      const { container } = renderHeader({ breadcrumbs: [], title: 'Dashboard' });

      const nav = container.querySelector('nav[aria-label="Breadcrumb"]');
      expect(nav).not.toBeInTheDocument();
    });

    it('should have proper breadcrumb styling', () => {
      const { container } = renderHeader({
        breadcrumbs: [{ href: '/', label: 'Home' }, { label: 'Projects' }],
        title: 'Project Details',
      });

      const breadcrumbList = container.querySelector('.flex.items-center.space-x-2');
      expect(breadcrumbList).toBeInTheDocument();
    });
  });

  describe('Combined Props', () => {
    it('should render all props together', () => {
      renderHeader({
        actions: <button data-testid='edit-button'>Edit</button>,
        breadcrumbs: [
          { href: '/', label: 'Home' },
          { href: '/projects', label: 'Projects' },
          { label: 'Project 1' },
        ],
        description: 'View and manage project requirements',
        icon: <FileText data-testid='project-icon' />,
        title: 'Project Details',
      });

      expect(screen.getByText('Project Details')).toBeInTheDocument();
      expect(screen.getByText('View and manage project requirements')).toBeInTheDocument();
      expect(screen.getByTestId('project-icon')).toBeInTheDocument();
      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByTestId('edit-button')).toBeInTheDocument();
    });

    it('should render title and icon only', () => {
      renderHeader({
        icon: <FileText data-testid='icon' />,
        title: 'Documents',
      });

      expect(screen.getByText('Documents')).toBeInTheDocument();
      expect(screen.getByTestId('icon')).toBeInTheDocument();
    });

    it('should render title and description only', () => {
      renderHeader({
        description: 'Configure your application preferences',
        title: 'Settings',
      });

      expect(screen.getByText('Settings')).toBeInTheDocument();
      expect(screen.getByText('Configure your application preferences')).toBeInTheDocument();
    });
  });

  describe('Layout and Styling', () => {
    it('should have border at bottom', () => {
      const { container } = renderHeader({ title: 'Dashboard' });

      const header = container.querySelector('.border-b');
      expect(header).toBeInTheDocument();
    });

    it('should have correct background color', () => {
      const { container } = renderHeader({ title: 'Dashboard' });

      const header = container.querySelector('.bg-white');
      expect(header).toBeInTheDocument();
    });

    it('should have correct padding', () => {
      const { container } = renderHeader({ title: 'Dashboard' });

      const contentContainer = container.querySelector('.px-6.py-4');
      expect(contentContainer).toBeInTheDocument();
    });

    it('should have flex layout for title and actions', () => {
      const { container } = renderHeader({
        actions: <button>Action</button>,
        title: 'Dashboard',
      });

      const flexContainer = container.querySelector('.flex.items-start.justify-between');
      expect(flexContainer).toBeInTheDocument();
    });
  });

  describe('Dark Mode', () => {
    it('should have dark mode classes for border', () => {
      const { container } = renderHeader({ title: 'Dashboard' });

      const header = container.querySelector(String.raw`.dark\:border-gray-800`);
      expect(header).toBeInTheDocument();
    });

    it('should have dark mode classes for background', () => {
      const { container } = renderHeader({ title: 'Dashboard' });

      const header = container.querySelector(String.raw`.dark\:bg-gray-900`);
      expect(header).toBeInTheDocument();
    });

    it('should have dark mode classes for title', () => {
      renderHeader({ title: 'Dashboard' });

      const title = screen.getByText('Dashboard');
      expect(title).toHaveClass('dark:text-gray-100');
    });

    it('should have dark mode classes for description', () => {
      renderHeader({ description: 'Welcome back', title: 'Dashboard' });

      const description = screen.getByText('Welcome back');
      expect(description).toHaveClass('dark:text-gray-400');
    });
  });

  describe('Edge Cases', () => {
    it('should handle very long titles', () => {
      const longTitle = 'A'.repeat(200);
      renderHeader({ title: longTitle });

      expect(screen.getByText(longTitle)).toBeInTheDocument();
    });

    it('should handle very long descriptions', () => {
      const longDescription = 'B'.repeat(500);
      renderHeader({ description: longDescription, title: 'Title' });

      expect(screen.getByText(longDescription)).toBeInTheDocument();
    });

    it('should handle special characters in title', () => {
      renderHeader({ title: "<Project> & 'Details'" });

      expect(screen.getByText("<Project> & 'Details'")).toBeInTheDocument();
    });

    it('should handle special characters in description', () => {
      renderHeader({ description: "<Data> & 'information'", title: 'Title' });

      expect(screen.getByText("<Data> & 'information'")).toBeInTheDocument();
    });

    it('should handle empty string title', () => {
      const { container } = renderHeader({ title: '' });
      const title = container.querySelector('.text-2xl');
      expect(title).toBeInTheDocument();
    });

    it('should handle complex React nodes in actions', () => {
      renderHeader({
        actions: (
          <div data-testid='complex'>
            <button>A</button>
            <div>B</div>
            <span>C</span>
          </div>
        ),
        title: 'Dashboard',
      });

      expect(screen.getByTestId('complex')).toBeInTheDocument();
    });

    it('should handle single breadcrumb', () => {
      render(<PageHeader title='Current Page' breadcrumbs={[{ label: 'Home' }]} />);

      expect(screen.getByText('Home')).toBeInTheDocument();
    });

    it('should handle breadcrumb without href', () => {
      render(
        <PageHeader title='Page' breadcrumbs={[{ label: 'No Link 1' }, { label: 'No Link 2' }]} />,
      );

      expect(screen.getByText('No Link 1')).toBeInTheDocument();
      expect(screen.getByText('No Link 2')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have semantic heading element', () => {
      render(<PageHeader title='Dashboard' />);

      const heading = container.querySelector('h1');
      expect(heading).toBeInTheDocument();
      expect(heading?.textContent).toBe('Dashboard');
    });

    it('should have proper breadcrumb navigation', () => {
      render(
        <PageHeader
          title='Page'
          breadcrumbs={[{ href: '/', label: 'Home' }, { label: 'Projects' }]}
        />,
      );

      const nav = container.querySelector('nav[aria-label="Breadcrumb"]');
      expect(nav).toBeInTheDocument();
    });

    it('should have ordered list for breadcrumbs', () => {
      render(
        <PageHeader
          title='Page'
          breadcrumbs={[{ href: '/', label: 'Home' }, { label: 'Projects' }]}
        />,
      );

      const ol = container.querySelector('ol');
      expect(ol).toBeInTheDocument();
    });

    it('should have descriptive link text', () => {
      render(
        <PageHeader
          title='Page'
          breadcrumbs={[
            { href: '/', label: 'Home' },
            { href: '/projects', label: 'Projects' },
          ]}
        />,
      );

      const homeLink = screen.getByText('Home');
      expect(homeLink).toHaveAttribute('href', '/');
    });
  });

  describe('Real-world Scenarios', () => {
    it('should render dashboard header', () => {
      render(<PageHeader title='Dashboard' description='Welcome to your TracerTM dashboard' />);

      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Welcome to your TracerTM dashboard')).toBeInTheDocument();
    });

    it('should render project list header with action', () => {
      render(
        <PageHeader
          title='Projects'
          description='Manage all your requirements projects'
          actions={<button>New Project</button>}
        />,
      );

      expect(screen.getByText('Projects')).toBeInTheDocument();
      expect(screen.getByText('New Project')).toBeInTheDocument();
    });

    it('should render nested page with breadcrumbs', () => {
      render(
        <PageHeader
          title='Feature Details'
          breadcrumbs={[
            { href: '/', label: 'Dashboard' },
            { href: '/projects', label: 'Projects' },
            { href: '/projects/1', label: 'Project 1' },
            { label: 'Features' },
          ]}
          actions={<button>Edit</button>}
        />,
      );

      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Projects')).toBeInTheDocument();
      expect(screen.getByText('Project 1')).toBeInTheDocument();
      expect(screen.getByText('Features')).toBeInTheDocument();
    });
  });
});
