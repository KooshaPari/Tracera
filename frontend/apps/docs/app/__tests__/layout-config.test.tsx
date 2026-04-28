import { describe, it, expect, vi } from 'vitest';

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  BookOpenIcon: () => <span data-testid='book-open-icon' />,
  CodeIcon: () => <span data-testid='code-icon' />,
  HomeIcon: () => <span data-testid='home-icon' />,
}));

import { baseOptions } from '../layout.config';

describe('layout.config baseOptions', () => {
  it('exports a baseOptions object', () => {
    expect(baseOptions).toBeDefined();
    expect(typeof baseOptions).toBe('object');
  });

  it('has a githubUrl configured', () => {
    expect(baseOptions.githubUrl).toBeDefined();
    expect(typeof baseOptions.githubUrl).toBe('string');
    expect(baseOptions.githubUrl).toContain('github.com');
  });

  it('has navigation title set to TracerTM', () => {
    expect(baseOptions.nav?.title).toBe('TracerTM');
  });

  it('has transparent mode set to top', () => {
    expect(baseOptions.nav?.transparentMode).toBe('top');
  });

  it('defines three navigation links', () => {
    expect(baseOptions.links).toHaveLength(3);
  });

  it('has a Documentation link pointing to /docs', () => {
    const docLink = baseOptions.links?.find((link: any) => link.text === 'Documentation');
    expect(docLink).toBeDefined();
    expect((docLink as any).url).toBe('/docs');
  });

  it('has an API link pointing to /api', () => {
    const apiLink = baseOptions.links?.find((link: any) => link.text === 'API');
    expect(apiLink).toBeDefined();
    expect((apiLink as any).url).toBe('/api');
  });

  it('has a Home link pointing to /', () => {
    const homeLink = baseOptions.links?.find((link: any) => link.text === 'Home');
    expect(homeLink).toBeDefined();
    expect((homeLink as any).url).toBe('/');
  });

  it('Documentation and API links use nested-url active mode', () => {
    const docLink = baseOptions.links?.find((link: any) => link.text === 'Documentation') as any;
    const apiLink = baseOptions.links?.find((link: any) => link.text === 'API') as any;

    expect(docLink.active).toBe('nested-url');
    expect(apiLink.active).toBe('nested-url');
  });
});
