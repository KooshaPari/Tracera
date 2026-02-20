import { render } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

// Capture loaders and options from dynamic() calls
interface DynamicCallCapture {
  loader: () => Promise<any>;
  options: any;
}

vi.mock('next/dynamic', () => ({
  default: (loader: () => Promise<any>, options?: any) => {
    const LoadingFallback = options?.loading;
    const DynamicComponent = (props: any) => <div data-testid='dynamic-component' {...props} />;
    DynamicComponent._loading = LoadingFallback;
    DynamicComponent._options = options;
    DynamicComponent._loader = loader;
    return DynamicComponent;
  },
}));

// Mock fumadocs components that the loaders will import
vi.mock('fumadocs-ui/components/tabs', () => ({
  Tabs: (props: any) => <div {...props} />,
  Tab: (props: any) => <div {...props} />,
}));

vi.mock('fumadocs-ui/components/accordion', () => ({
  Accordions: (props: any) => <div {...props} />,
  Accordion: (props: any) => <div {...props} />,
}));

vi.mock('fumadocs-ui/components/image-zoom', () => ({
  ImageZoom: (props: any) => <div {...props} />,
}));

vi.mock('fumadocs-ui/components/files', () => ({
  Files: (props: any) => <div {...props} />,
  Folder: (props: any) => <div {...props} />,
  File: (props: any) => <div {...props} />,
}));

vi.mock('fumadocs-ui/components/steps', () => ({
  Steps: (props: any) => <div {...props} />,
  Step: (props: any) => <div {...props} />,
}));

import {
  TabsLazy,
  TabLazy,
  AccordionsLazy,
  AccordionLazy,
  ImageZoomLazy,
  FilesLazy,
  FolderLazy,
  FileLazy,
  StepsLazy,
  StepLazy,
} from '../mdx-components-lazy';

describe('mdx-components-lazy', () => {
  const allComponents = [
    { name: 'TabsLazy', Component: TabsLazy },
    { name: 'TabLazy', Component: TabLazy },
    { name: 'AccordionsLazy', Component: AccordionsLazy },
    { name: 'AccordionLazy', Component: AccordionLazy },
    { name: 'ImageZoomLazy', Component: ImageZoomLazy },
    { name: 'FilesLazy', Component: FilesLazy },
    { name: 'FolderLazy', Component: FolderLazy },
    { name: 'FileLazy', Component: FileLazy },
    { name: 'StepsLazy', Component: StepsLazy },
    { name: 'StepLazy', Component: StepLazy },
  ];

  for (const { name, Component } of allComponents) {
    it(`exports ${name} as a function`, () => {
      expect(Component).toBeDefined();
      expect(typeof Component).toBe('function');
    });
  }

  it('renders loading skeleton for standard components (TabsLazy)', () => {
    const LoadingComponent = (TabsLazy as any)._loading;
    expect(LoadingComponent).toBeDefined();
    const { container } = render(<LoadingComponent />);
    expect(container.querySelector('.animate-pulse')).not.toBeNull();
  });

  it('renders loading skeleton for TabLazy', () => {
    const LoadingComponent = (TabLazy as any)._loading;
    const { container } = render(<LoadingComponent />);
    expect(container.querySelector('.animate-pulse')).not.toBeNull();
  });

  it('renders loading skeleton for AccordionsLazy', () => {
    const LoadingComponent = (AccordionsLazy as any)._loading;
    const { container } = render(<LoadingComponent />);
    expect(container.querySelector('.animate-pulse')).not.toBeNull();
  });

  it('renders loading skeleton for AccordionLazy', () => {
    const LoadingComponent = (AccordionLazy as any)._loading;
    const { container } = render(<LoadingComponent />);
    expect(container.querySelector('.animate-pulse')).not.toBeNull();
  });

  it('renders loading skeleton for FilesLazy', () => {
    const LoadingComponent = (FilesLazy as any)._loading;
    const { container } = render(<LoadingComponent />);
    expect(container.querySelector('.animate-pulse')).not.toBeNull();
  });

  it('renders loading skeleton for FolderLazy', () => {
    const LoadingComponent = (FolderLazy as any)._loading;
    const { container } = render(<LoadingComponent />);
    expect(container.querySelector('.animate-pulse')).not.toBeNull();
  });

  it('renders loading skeleton for FileLazy', () => {
    const LoadingComponent = (FileLazy as any)._loading;
    const { container } = render(<LoadingComponent />);
    expect(container.querySelector('.animate-pulse')).not.toBeNull();
  });

  it('renders loading skeleton for StepsLazy', () => {
    const LoadingComponent = (StepsLazy as any)._loading;
    const { container } = render(<LoadingComponent />);
    expect(container.querySelector('.animate-pulse')).not.toBeNull();
  });

  it('renders loading skeleton for StepLazy', () => {
    const LoadingComponent = (StepLazy as any)._loading;
    const { container } = render(<LoadingComponent />);
    expect(container.querySelector('.animate-pulse')).not.toBeNull();
  });

  it('renders aspect-video loading skeleton for ImageZoomLazy', () => {
    const LoadingComponent = (ImageZoomLazy as any)._loading;
    const { container } = render(<LoadingComponent />);
    expect(container.querySelector('.aspect-video')).not.toBeNull();
  });

  it('ImageZoomLazy has SSR disabled', () => {
    const options = (ImageZoomLazy as any)._options;
    expect(options?.ssr).toBe(false);
  });

  it('TabsLazy has SSR enabled', () => {
    const options = (TabsLazy as any)._options;
    expect(options?.ssr).toBe(true);
  });

  it('all non-ImageZoom components have SSR enabled', () => {
    const ssrComponents = allComponents.filter(({ name }) => name !== 'ImageZoomLazy');
    for (const { name, Component } of ssrComponents) {
      const options = (Component as any)._options;
      expect(options?.ssr, `${name} should have SSR enabled`).toBe(true);
    }
  });

  // Exercise the loader functions to get coverage on the dynamic import callbacks
  describe('loader functions', () => {
    it('TabsLazy loader resolves to the Tabs component', async () => {
      const loader = (TabsLazy as any)._loader;
      const result = await loader();
      expect(result).toBeDefined();
    });

    it('TabLazy loader resolves to the Tab component', async () => {
      const loader = (TabLazy as any)._loader;
      const result = await loader();
      expect(result).toBeDefined();
    });

    it('AccordionsLazy loader resolves', async () => {
      const loader = (AccordionsLazy as any)._loader;
      const result = await loader();
      expect(result).toBeDefined();
    });

    it('AccordionLazy loader resolves', async () => {
      const loader = (AccordionLazy as any)._loader;
      const result = await loader();
      expect(result).toBeDefined();
    });

    it('ImageZoomLazy loader resolves', async () => {
      const loader = (ImageZoomLazy as any)._loader;
      const result = await loader();
      expect(result).toBeDefined();
    });

    it('FilesLazy loader resolves', async () => {
      const loader = (FilesLazy as any)._loader;
      const result = await loader();
      expect(result).toBeDefined();
    });

    it('FolderLazy loader resolves', async () => {
      const loader = (FolderLazy as any)._loader;
      const result = await loader();
      expect(result).toBeDefined();
    });

    it('FileLazy loader resolves', async () => {
      const loader = (FileLazy as any)._loader;
      const result = await loader();
      expect(result).toBeDefined();
    });

    it('StepsLazy loader resolves', async () => {
      const loader = (StepsLazy as any)._loader;
      const result = await loader();
      expect(result).toBeDefined();
    });

    it('StepLazy loader resolves', async () => {
      const loader = (StepLazy as any)._loader;
      const result = await loader();
      expect(result).toBeDefined();
    });
  });
});
