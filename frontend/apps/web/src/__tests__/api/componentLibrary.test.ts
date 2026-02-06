import { describe, expect, it } from 'vitest';

import type {
  ComponentLibrary,
  ComponentUsage,
  DesignToken,
  LibraryComponent,
} from '@tracertm/types';

import { componentLibraryApi } from '../../api/component-library';

interface CreateComponentLibraryInput {
  projectId: string;
  name: string;
  description?: string;
  version?: string;
}

interface CreateLibraryComponentInput {
  libraryId: string;
  name: string;
  description?: string;
  category: string;
  properties?: Record<string, unknown>;
  variant?: string;
}

interface CreateDesignTokenInput {
  libraryId: string;
  name: string;
  type: string;
  value: unknown;
  category: string;
  description?: string;
}

const { componentLibraryQueryKeys } = componentLibraryApi;

describe('component library API hooks', () => {
  describe('queryKeys', () => {
    it('should generate correct query key for all component libraries', () => {
      const key = componentLibraryQueryKeys.all;
      expect(key).toEqual(['componentLibrary']);
    });

    it('should generate correct query key for list', () => {
      const key = componentLibraryQueryKeys.list('project-1');
      expect(key).toEqual(['componentLibrary', 'list', 'project-1']);
    });

    it('should generate correct query key for detail', () => {
      const key = componentLibraryQueryKeys.detail('library-1');
      expect(key).toEqual(['componentLibrary', 'detail', 'library-1']);
    });

    it('should generate correct query key for components', () => {
      const key = componentLibraryQueryKeys.components('library-1');
      expect(key).toEqual(['componentLibrary', 'components', 'library-1']);
    });

    it('should generate correct query key for single component', () => {
      const key = componentLibraryQueryKeys.component('component-1');
      expect(key).toEqual(['componentLibrary', 'component', 'component-1']);
    });

    it('should generate correct query key for usage', () => {
      const key = componentLibraryQueryKeys.usage('component-1');
      expect(key).toEqual(['componentLibrary', 'usage', 'component-1']);
    });

    it('should generate correct query key for tokens', () => {
      const key = componentLibraryQueryKeys.tokens('library-1');
      expect(key).toEqual(['componentLibrary', 'tokens', 'library-1']);
    });
  });

  describe('ComponentLibrary type', () => {
    it('should validate component library structure', () => {
      const library: ComponentLibrary = {
        componentCount: 25,
        createdAt: '2024-01-01T00:00:00Z',
        description: 'Core UI component library',
        id: 'library-1',
        name: 'UI Components',
        projectId: 'project-1',
        slug: 'ui-components',
        source: 'manual',
        syncStatus: 'synced',
        tokenCount: 10,
        updatedAt: '2024-01-02T00:00:00Z',
        version: '1.0.0',
      };

      expect(library.id).toBeDefined();
      expect(library.projectId).toBeDefined();
      expect(library.name).toBeDefined();
      expect(library.version).toBeDefined();
      expect(library.componentCount).toBeGreaterThanOrEqual(0);
    });

    it('should allow optional description', () => {
      const library: ComponentLibrary = {
        componentCount: 0,
        createdAt: '2024-01-01T00:00:00Z',
        id: 'library-1',
        name: 'UI Components',
        projectId: 'project-1',
        slug: 'ui-components',
        source: 'manual',
        syncStatus: 'synced',
        tokenCount: 0,
        updatedAt: '2024-01-01T00:00:00Z',
        version: '1.0.0',
      };

      expect(library.description).toBeUndefined();
    });
  });

  describe('LibraryComponent type', () => {
    it('should validate library component structure', () => {
      const component: LibraryComponent = {
        category: 'atom',
        createdAt: '2024-01-01T00:00:00Z',
        description: 'Primary action button',
        displayName: 'Primary Button',
        id: 'component-1',
        libraryId: 'library-1',
        name: 'Button',
        projectId: 'project-1',
        status: 'stable',
        updatedAt: '2024-01-02T00:00:00Z',
        usageCount: 150,
      };

      expect(component.id).toBeDefined();
      expect(component.libraryId).toBeDefined();
      expect(component.name).toBeDefined();
      expect(component.category).toBeDefined();
      expect(component.usageCount).toBeGreaterThanOrEqual(0);
    });

    it('should allow optional variant', () => {
      const component: LibraryComponent = {
        category: 'atom',
        createdAt: '2024-01-01T00:00:00Z',
        displayName: 'Button',
        id: 'component-1',
        libraryId: 'library-1',
        name: 'Button',
        projectId: 'project-1',
        status: 'stable',
        updatedAt: '2024-01-01T00:00:00Z',
        usageCount: 0,
      };

      expect(component.variants).toBeUndefined();
    });
  });

  describe('ComponentUsage type', () => {
    it('should validate component usage structure', () => {
      const usage: ComponentUsage = {
        componentId: 'component-1',
        detectedAt: '2024-01-02T00:00:00Z',
        id: 'usage-1',
        libraryId: 'library-1',
        projectId: 'project-1',
        usedInItemId: 'item-1',
      };

      expect(usage.usedInItemId).toBeDefined();
      expect(usage.componentId).toBeDefined();
      expect(usage.detectedAt).toBeDefined();
    });
  });

  describe('DesignToken type', () => {
    it('should validate design token structure', () => {
      const token: DesignToken = {
        createdAt: '2024-01-01T00:00:00Z',
        description: 'Primary brand color',
        id: 'token-1',
        libraryId: 'library-1',
        name: 'colors.primary.500',
        path: ['colors', 'primary', '500'],
        projectId: 'project-1',
        type: 'color',
        updatedAt: '2024-01-02T00:00:00Z',
        usageCount: 5,
        value: '#0066CC',
      };

      expect(token.id).toBeDefined();
      expect(token.libraryId).toBeDefined();
      expect(token.name).toBeDefined();
      expect(token.type).toBeDefined();
      expect(token.value).toBeDefined();
      expect(token.usageCount).toBeGreaterThanOrEqual(0);
    });

    it('should store design token values as strings', () => {
      const colorToken: DesignToken = {
        createdAt: '2024-01-01T00:00:00Z',
        id: 'token-1',
        libraryId: 'library-1',
        name: 'colors.primary.500',
        path: ['colors', 'primary', '500'],
        projectId: 'project-1',
        type: 'color',
        updatedAt: '2024-01-01T00:00:00Z',
        usageCount: 0,
        value: '#0066CC',
      };

      const spacingToken: DesignToken = {
        createdAt: '2024-01-01T00:00:00Z',
        id: 'token-2',
        libraryId: 'library-1',
        name: 'spacing.sm',
        path: ['spacing', 'sm'],
        projectId: 'project-1',
        type: 'spacing',
        updatedAt: '2024-01-01T00:00:00Z',
        usageCount: 0,
        value: '8',
      };

      const typographyToken: DesignToken = {
        createdAt: '2024-01-01T00:00:00Z',
        id: 'token-3',
        libraryId: 'library-1',
        name: 'typography.body',
        path: ['typography', 'body'],
        projectId: 'project-1',
        type: 'typography',
        updatedAt: '2024-01-01T00:00:00Z',
        usageCount: 0,
        value: 'Inter/16/1.5',
      };

      expect(typeof colorToken.value).toBe('string');
      expect(typeof spacingToken.value).toBe('string');
      expect(typeof typographyToken.value).toBe('string');
    });
  });

  describe('Input types', () => {
    it('should validate CreateComponentLibraryInput', () => {
      const input: CreateComponentLibraryInput = {
        description: 'Complete design system',
        name: 'Design System',
        projectId: 'project-1',
        version: '2.0.0',
      };

      expect(input.projectId).toBeDefined();
      expect(input.name).toBeDefined();
    });

    it('should validate CreateLibraryComponentInput', () => {
      const input: CreateLibraryComponentInput = {
        category: 'layout',
        description: 'Container component',
        libraryId: 'library-1',
        name: 'Card',
        properties: { padding: '16px' },
        variant: 'default',
      };

      expect(input.libraryId).toBeDefined();
      expect(input.name).toBeDefined();
      expect(input.category).toBeDefined();
    });

    it('should validate CreateDesignTokenInput', () => {
      const input: CreateDesignTokenInput = {
        category: 'radius',
        description: 'Small border radius',
        libraryId: 'library-1',
        name: 'radius-sm',
        type: 'radius',
        value: '4',
      };

      expect(input.libraryId).toBeDefined();
      expect(input.name).toBeDefined();
      expect(input.type).toBeDefined();
      expect(input.value).toBeDefined();
      expect(input.category).toBeDefined();
    });
  });

  describe('Query key hierarchies', () => {
    it('should create consistent component query keys', () => {
      const key1 = componentLibraryQueryKeys.component('component-1');
      const key2 = componentLibraryQueryKeys.component('component-2');

      expect(key1).not.toEqual(key2);
      expect(key1.slice(0, 2)).toEqual(key2.slice(0, 2)); // Same prefix
    });

    it('should create consistent library component keys', () => {
      const key1 = componentLibraryQueryKeys.components('library-1');
      const key2 = componentLibraryQueryKeys.components('library-2');

      expect(key1).not.toEqual(key2);
      expect(key1[1]).toEqual(key2[1]); // Same operation
    });

    it('should create independent token keys', () => {
      const key1 = componentLibraryQueryKeys.tokens('library-1');
      const key2 = componentLibraryQueryKeys.tokens('library-2');

      expect(key1).not.toEqual(key2);
      expect(key1[1]).toEqual(key2[1]); // Same operation
    });

    it('should create separate keys for usage', () => {
      const key1 = componentLibraryQueryKeys.usage('component-1');
      const key2 = componentLibraryQueryKeys.usage('component-2');

      expect(key1).not.toEqual(key2);
      expect(key1[1]).toEqual(key2[1]); // Same operation
    });
  });
});
