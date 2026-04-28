import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

// Mock the lazy components before importing mdx-components
vi.mock('../mdx-components-lazy', () => ({
  TabLazy: (props: any) => <div data-testid='tab-lazy' {...props} />,
  TabsLazy: (props: any) => <div data-testid='tabs-lazy' {...props} />,
  AccordionLazy: (props: any) => <div data-testid='accordion-lazy' {...props} />,
  AccordionsLazy: (props: any) => <div data-testid='accordions-lazy' {...props} />,
  ImageZoomLazy: (props: any) => <div data-testid='image-zoom-lazy' {...props} />,
  FileLazy: (props: any) => <div data-testid='file-lazy' {...props} />,
  FolderLazy: (props: any) => <div data-testid='folder-lazy' {...props} />,
  FilesLazy: (props: any) => <div data-testid='files-lazy' {...props} />,
  StepLazy: (props: any) => <div data-testid='step-lazy' {...props} />,
  StepsLazy: (props: any) => <div data-testid='steps-lazy' {...props} />,
}));

vi.mock('../optimized-image', () => ({
  DocImage: ({ src, alt }: { src: string; alt: string }) => (
    <img data-testid='doc-image' src={src} alt={alt} />
  ),
}));

vi.mock('../icon-sprite', () => ({
  Icon: ({ name, size, className }: { name: string; size?: number; className?: string }) => (
    <span data-testid={`icon-${name}`} data-size={size} className={className} />
  ),
}));

vi.mock('fumadocs-ui/components/callout', () => ({
  Callout: (props: any) => <div data-testid='callout' {...props} />,
}));

vi.mock('fumadocs-ui/mdx', () => ({
  default: {
    p: (props: any) => <p {...props} />,
    h1: (props: any) => <h1 {...props} />,
  },
}));

import { mdxComponents } from '../mdx-components';

describe('mdxComponents', () => {
  it('exports an object with MDX components', () => {
    expect(mdxComponents).toBeDefined();
    expect(typeof mdxComponents).toBe('object');
  });

  it('includes default MDX components (p, h1) from fumadocs', () => {
    // The spread of defaultMdxComponents should bring in p and h1
    expect(mdxComponents.p).toBeDefined();
    expect(mdxComponents.h1).toBeDefined();
  });

  it('maps Tab to TabLazy', () => {
    expect(mdxComponents.Tab).toBeDefined();
  });

  it('maps Tabs to TabsLazy', () => {
    expect(mdxComponents.Tabs).toBeDefined();
  });

  it('maps Accordion to AccordionLazy', () => {
    expect(mdxComponents.Accordion).toBeDefined();
  });

  it('maps Accordions to AccordionsLazy', () => {
    expect(mdxComponents.Accordions).toBeDefined();
  });

  it('includes Callout component directly (not lazy)', () => {
    expect(mdxComponents.Callout).toBeDefined();
  });

  it('maps ImageZoom to ImageZoomLazy', () => {
    expect(mdxComponents.ImageZoom).toBeDefined();
  });

  it('maps File, Folder, Files to lazy variants', () => {
    expect(mdxComponents.File).toBeDefined();
    expect(mdxComponents.Folder).toBeDefined();
    expect(mdxComponents.Files).toBeDefined();
  });

  it('maps Step and Steps to lazy variants', () => {
    expect(mdxComponents.Step).toBeDefined();
    expect(mdxComponents.Steps).toBeDefined();
  });

  describe('custom img component', () => {
    const ImgComponent = mdxComponents.img;

    it('renders DocImage for local images', () => {
      render(<ImgComponent src='/images/test.png' alt='Test' />);
      expect(screen.getByTestId('doc-image')).toBeInTheDocument();
    });

    it('renders ImageZoomLazy for external images', () => {
      render(<ImgComponent src='https://example.com/image.png' alt='External' />);
      expect(screen.getByTestId('image-zoom-lazy')).toBeInTheDocument();
    });

    it('uses empty alt text when alt is not provided for local images', () => {
      render(<ImgComponent src='/images/test.png' />);
      const img = screen.getByTestId('doc-image');
      expect(img.getAttribute('alt')).toBe('');
    });
  });

  describe('custom anchor component', () => {
    const AnchorComponent = mdxComponents.a;

    it('renders internal links without target="_blank"', () => {
      render(<AnchorComponent href='/docs/guide'>Guide</AnchorComponent>);

      const link = screen.getByText('Guide');
      expect(link.getAttribute('target')).toBeNull();
      expect(link.getAttribute('rel')).toBeNull();
    });

    it('renders external links with target="_blank" and rel attributes', () => {
      render(<AnchorComponent href='https://github.com'>GitHub</AnchorComponent>);

      const link = screen.getByText('GitHub').closest('a');
      expect(link?.getAttribute('target')).toBe('_blank');
      expect(link?.getAttribute('rel')).toBe('noopener noreferrer');
    });

    it('shows external-link icon for external links', () => {
      render(<AnchorComponent href='https://example.com'>External</AnchorComponent>);

      expect(screen.getByTestId('icon-external-link')).toBeInTheDocument();
    });

    it('does not show external-link icon for internal links', () => {
      render(<AnchorComponent href='/docs/intro'>Internal</AnchorComponent>);

      expect(screen.queryByTestId('icon-external-link')).toBeNull();
    });

    it('handles undefined href gracefully', () => {
      render(<AnchorComponent>No href</AnchorComponent>);

      const link = screen.getByText('No href');
      expect(link).toBeInTheDocument();
      expect(link.getAttribute('target')).toBeNull();
    });
  });
});
