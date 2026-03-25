import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import * as Vitest from 'vitest';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/Tabs';

Vitest.describe('Tabs component', () => {
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

  Vitest.it('renders tab triggers', () => {
    renderTabs();
    Vitest.expect(screen.getByRole('tab', { name: 'Tab 1' })).toBeInTheDocument();
    Vitest.expect(screen.getByRole('tab', { name: 'Tab 2' })).toBeInTheDocument();
  });

  Vitest.it('renders the tablist', () => {
    renderTabs();
    Vitest.expect(screen.getByRole('tablist')).toBeInTheDocument();
  });

  Vitest.it('shows the default tab content', () => {
    renderTabs();
    Vitest.expect(screen.getByText('Content 1')).toBeInTheDocument();
  });

  Vitest.it('renders second tab content when set as default', () => {
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
    Vitest.expect(screen.getByText('Content 2')).toBeInTheDocument();
    Vitest.expect(screen.getByRole('tab', { name: 'Tab 2' })).toHaveAttribute(
      'data-state',
      'active',
    );
  });

  Vitest.it('marks the active tab with data-state=active', () => {
    renderTabs();
    const tab1 = screen.getByRole('tab', { name: 'Tab 1' });
    Vitest.expect(tab1).toHaveAttribute('data-state', 'active');
  });

  Vitest.it('marks inactive tab with data-state=inactive', () => {
    renderTabs();
    const tab2 = screen.getByRole('tab', { name: 'Tab 2' });
    Vitest.expect(tab2).toHaveAttribute('data-state', 'inactive');
  });

  Vitest.it('renders tabpanel for active content', () => {
    renderTabs();
    Vitest.expect(screen.getByRole('tabpanel')).toBeInTheDocument();
  });

  Vitest.it('renders controlled tabs with value prop', () => {
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
    Vitest.expect(screen.getByText('Content 2')).toBeInTheDocument();
    Vitest.expect(screen.getByRole('tab', { name: 'Tab 2' })).toHaveAttribute(
      'data-state',
      'active',
    );
  });
});

Vitest.describe('TabsList component', () => {
  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(
      <Tabs defaultValue='t1'>
        <TabsList ref={ref}>
          <TabsTrigger value='t1'>T</TabsTrigger>
        </TabsList>
      </Tabs>,
    );
    Vitest.expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  Vitest.it('applies custom className', () => {
    render(
      <Tabs defaultValue='t1'>
        <TabsList className='custom-tabslist'>
          <TabsTrigger value='t1'>T</TabsTrigger>
        </TabsList>
      </Tabs>,
    );
    Vitest.expect(screen.getByRole('tablist').className).toContain('custom-tabslist');
  });
});

Vitest.describe('TabsTrigger component', () => {
  Vitest.it('can be disabled', () => {
    render(
      <Tabs defaultValue='t1'>
        <TabsList>
          <TabsTrigger value='t1' disabled>
            Disabled Tab
          </TabsTrigger>
        </TabsList>
      </Tabs>,
    );
    Vitest.expect(screen.getByRole('tab', { name: 'Disabled Tab' })).toBeDisabled();
  });
});

Vitest.describe('TabsContent component', () => {
  Vitest.it('forwards ref', () => {
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
    Vitest.expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  Vitest.it('applies custom className', () => {
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
    Vitest.expect(screen.getByRole('tabpanel').className).toContain('custom-content');
  });
});
