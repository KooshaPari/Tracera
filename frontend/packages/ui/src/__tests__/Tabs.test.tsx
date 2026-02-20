import { fireEvent, render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { describe, expect, it } from 'vitest';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/Tabs';

describe('Tabs', () => {
  const renderTabs = () =>
    render(
      <Tabs defaultValue='tab1'>
        <TabsList>
          <TabsTrigger value='tab1'>Tab 1</TabsTrigger>
          <TabsTrigger value='tab2'>Tab 2</TabsTrigger>
        </TabsList>
        <TabsContent value='tab1'>Content 1</TabsContent>
        <TabsContent value='tab2'>Content 2</TabsContent>
      </Tabs>,
    );

  it('renders tab triggers', () => {
    renderTabs();
    expect(screen.getByRole('tab', { name: 'Tab 1' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Tab 2' })).toBeInTheDocument();
  });

  it('renders the tablist', () => {
    renderTabs();
    expect(screen.getByRole('tablist')).toBeInTheDocument();
  });

  it('shows the default tab content', () => {
    renderTabs();
    expect(screen.getByText('Content 1')).toBeInTheDocument();
  });

  it('renders second tab content when set as default', () => {
    render(
      <Tabs defaultValue='tab2'>
        <TabsList>
          <TabsTrigger value='tab1'>Tab 1</TabsTrigger>
          <TabsTrigger value='tab2'>Tab 2</TabsTrigger>
        </TabsList>
        <TabsContent value='tab1'>Content 1</TabsContent>
        <TabsContent value='tab2'>Content 2</TabsContent>
      </Tabs>,
    );
    expect(screen.getByText('Content 2')).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Tab 2' })).toHaveAttribute('data-state', 'active');
  });

  it('marks the active tab with data-state=active', () => {
    renderTabs();
    const tab1 = screen.getByRole('tab', { name: 'Tab 1' });
    expect(tab1).toHaveAttribute('data-state', 'active');
  });

  it('marks inactive tab with data-state=inactive', () => {
    renderTabs();
    const tab2 = screen.getByRole('tab', { name: 'Tab 2' });
    expect(tab2).toHaveAttribute('data-state', 'inactive');
  });

  it('renders tabpanel for active content', () => {
    renderTabs();
    expect(screen.getByRole('tabpanel')).toBeInTheDocument();
  });

  it('renders controlled tabs with value prop', () => {
    render(
      <Tabs value='tab2'>
        <TabsList>
          <TabsTrigger value='tab1'>Tab 1</TabsTrigger>
          <TabsTrigger value='tab2'>Tab 2</TabsTrigger>
        </TabsList>
        <TabsContent value='tab1'>Content 1</TabsContent>
        <TabsContent value='tab2'>Content 2</TabsContent>
      </Tabs>,
    );
    expect(screen.getByText('Content 2')).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Tab 2' })).toHaveAttribute('data-state', 'active');
  });
});

describe('TabsList', () => {
  it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(
      <Tabs defaultValue='t1'>
        <TabsList ref={ref}>
          <TabsTrigger value='t1'>T</TabsTrigger>
        </TabsList>
      </Tabs>,
    );
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('applies custom className', () => {
    render(
      <Tabs defaultValue='t1'>
        <TabsList className='custom-tabslist'>
          <TabsTrigger value='t1'>T</TabsTrigger>
        </TabsList>
      </Tabs>,
    );
    expect(screen.getByRole('tablist').className).toContain('custom-tabslist');
  });
});

describe('TabsTrigger', () => {
  it('can be disabled', () => {
    render(
      <Tabs defaultValue='t1'>
        <TabsList>
          <TabsTrigger value='t1' disabled>
            Disabled Tab
          </TabsTrigger>
        </TabsList>
      </Tabs>,
    );
    expect(screen.getByRole('tab', { name: 'Disabled Tab' })).toBeDisabled();
  });
});

describe('TabsContent', () => {
  it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(
      <Tabs defaultValue='t1'>
        <TabsList>
          <TabsTrigger value='t1'>T</TabsTrigger>
        </TabsList>
        <TabsContent ref={ref} value='t1'>
          Content
        </TabsContent>
      </Tabs>,
    );
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('applies custom className', () => {
    render(
      <Tabs defaultValue='t1'>
        <TabsList>
          <TabsTrigger value='t1'>T</TabsTrigger>
        </TabsList>
        <TabsContent className='custom-content' value='t1'>
          Content
        </TabsContent>
      </Tabs>,
    );
    expect(screen.getByRole('tabpanel').className).toContain('custom-content');
  });
});
