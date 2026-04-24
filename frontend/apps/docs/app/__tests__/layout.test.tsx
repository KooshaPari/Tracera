import { describe, it, expect, vi } from 'vitest';

// Mock fumadocs RootProvider
vi.mock('fumadocs-ui/provider/next', () => ({
  RootProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock next/font/google
vi.mock('next/font/google', () => ({
  Inter: () => ({
    className: 'mock-inter-class',
    variable: '--font-inter',
  }),
}));

// Mock IconSprite
vi.mock('@/components/icon-sprite', () => ({
  IconSprite: () => <div data-testid='icon-sprite' />,
}));

import Layout, { metadata, viewport } from '../layout';

describe('Layout component', () => {
  it('is a function (React component)', () => {
    expect(typeof Layout).toBe('function');
  });

  it('is exported as default', () => {
    expect(Layout).toBeDefined();
  });
});

describe('metadata export', () => {
  it('has a title with default and template', () => {
    expect(metadata.title).toBeDefined();
    expect((metadata.title as any).default).toBe('TracerTM Documentation');
    expect((metadata.title as any).template).toBe('%s | TracerTM');
  });

  it('has a description', () => {
    expect(metadata.description).toBe('Complete documentation for the TracerTM platform');
  });

  it('has icon configuration', () => {
    expect(metadata.icons).toBeDefined();
    expect((metadata.icons as any).icon).toBeDefined();
    expect((metadata.icons as any).apple).toBeDefined();
  });

  it('has apple web app configuration', () => {
    expect(metadata.appleWebApp).toBeDefined();
    expect((metadata.appleWebApp as any).title).toBe('TracerTM Docs');
    expect((metadata.appleWebApp as any).capable).toBe(true);
    expect((metadata.appleWebApp as any).statusBarStyle).toBe('default');
  });

  it('has a manifest reference', () => {
    expect(metadata.manifest).toBe('/manifest.json');
  });
});

describe('viewport export', () => {
  it('has themeColor set to black', () => {
    expect(viewport.themeColor).toBe('#000000');
  });
});
