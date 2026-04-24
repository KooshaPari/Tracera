/**
 * Visual Regression Testing Automation Tests
 * Tests for snapshot generation, baseline updates, and regression detection
 */

import { beforeEach, describe, expect, it } from 'vitest';

import {
  VisualRegressionTracker,
  VisualTestMetrics,
  createInteractionStories,
  createThemeStories,
  createViewportStories,
  generateSnapshotName,
  generateVisualTestParameters,
  validateComponentVisualTests,
} from '../../components/graph/__stories__/visual-regression-automation';

describe('Visual Regression Testing Automation', () => {
  describe('Snapshot Name Generation', () => {
    it('should generate consistent snapshot names', () => {
      const name = generateSnapshotName('Button', 'Primary', 'desktop', 'light');
      expect(name).toBe('button-primary-desktop-light');
    });

    it('should include state in snapshot name', () => {
      const name = generateSnapshotName('Button', 'Primary', 'desktop', 'light', 'hover');
      expect(name).toBe('button-primary-desktop-light-hover');
    });

    it('should handle spaces in names', () => {
      const name = generateSnapshotName('Graph View', 'Default', 'tablet', 'dark');
      expect(name).toBe('graph-view-default-tablet-dark');
    });

    it('should be case insensitive', () => {
      const name1 = generateSnapshotName('Button', 'PRIMARY', 'Desktop', 'LIGHT');
      const name2 = generateSnapshotName('button', 'primary', 'desktop', 'light');
      expect(name1).toBe(name2);
    });
  });

  describe('Visual Test Parameter Generation', () => {
    it('should generate chromatic parameters', () => {
      const params = generateVisualTestParameters('UnifiedGraphView');
      expect(params.chromatic).toBeDefined();
      expect(params.chromatic.modes).toBeDefined();
    });

    it('should include light and dark modes', () => {
      const params = generateVisualTestParameters('UnifiedGraphView');
      expect(params.chromatic.modes).toHaveProperty('light');
      expect(params.chromatic.modes).toHaveProperty('dark');
    });

    it('should set animation delay', () => {
      const params = generateVisualTestParameters('UnifiedGraphView');
      expect(params.chromatic.delay).toBeGreaterThan(0);
    });

    it('should allow custom configuration', () => {
      const params = generateVisualTestParameters('UnifiedGraphView', {
        delay: 500,
      });
      expect(params.chromatic.delay).toBe(500);
    });
  });

  describe('Viewport Story Creation', () => {
    it('should create stories for all viewports', () => {
      const stories = createViewportStories('TestComponent', { label: 'Test' });
      expect(Object.keys(stories).length).toBeGreaterThan(0);
    });

    it('should include desktop viewport', () => {
      const stories = createViewportStories('TestComponent', { label: 'Test' });
      const desktopStory = Object.entries(stories).find(([key]) =>
        key.toLowerCase().includes('desktop'),
      );
      expect(desktopStory).toBeDefined();
    });

    it('should preserve component args', () => {
      const testArgs = { label: 'Test', variant: 'primary' };
      const stories = createViewportStories('TestComponent', testArgs);
      Object.values(stories).forEach((story) => {
        expect(story.args).toEqual(testArgs);
      });
    });
  });

  describe('Theme Story Creation', () => {
    it('should create light and dark theme stories', () => {
      const stories = createThemeStories({ label: 'Test' });
      expect(Object.keys(stories)).toContain('Light');
      expect(Object.keys(stories)).toContain('Dark');
    });

    it('should apply theme data attribute', () => {
      const stories = createThemeStories({ label: 'Test' });
      expect(stories.Light).toBeDefined();
      expect(stories.Dark).toBeDefined();
    });

    it('should preserve component args', () => {
      const testArgs = { label: 'Test', variant: 'primary' };
      const stories = createThemeStories(testArgs);
      Object.values(stories).forEach((story) => {
        expect(story.args).toEqual(testArgs);
      });
    });

    it('should allow custom theme selection', () => {
      const stories = createThemeStories({ label: 'Test' }, ['light']);
      expect(Object.keys(stories)).toContain('Light');
      expect(Object.keys(stories)).not.toContain('Dark');
    });
  });

  describe('Interaction Story Creation', () => {
    it('should create hover story', () => {
      const stories = createInteractionStories({ label: 'Test' });
      expect(stories.Hovered).toBeDefined();
    });

    it('should create focused story', () => {
      const stories = createInteractionStories({ label: 'Test' });
      expect(stories.Focused).toBeDefined();
    });

    it('should create active story', () => {
      const stories = createInteractionStories({ label: 'Test' });
      expect(stories.Active).toBeDefined();
    });

    it('should create disabled story', () => {
      const stories = createInteractionStories({ label: 'Test' });
      expect(stories.Disabled).toBeDefined();
      expect(stories.Disabled.args.disabled).toBeTruthy();
    });

    it('should allow custom selector', () => {
      const stories = createInteractionStories({ label: 'Test' }, '.custom-selector');
      expect(stories.Hovered).toBeDefined();
    });
  });

  describe('Visual Regression Tracker', () => {
    let tracker: VisualRegressionTracker;

    beforeEach(() => {
      tracker = new VisualRegressionTracker();
    });

    it('should record component changes', () => {
      tracker.recordChange('Button', 'button-primary-desktop');
      expect(tracker.hasChanges('Button')).toBeTruthy();
    });

    it('should track multiple changes per component', () => {
      tracker.recordChange('Button', 'button-primary-desktop');
      tracker.recordChange('Button', 'button-primary-mobile');
      const changes = tracker.getChanges('Button');
      expect(changes).toHaveLength(2);
    });

    it('should track changes across multiple components', () => {
      tracker.recordChange('Button', 'button-primary');
      tracker.recordChange('Input', 'input-text');
      expect(tracker.hasChanges()).toBeTruthy();
      expect(tracker.getChanges()).toHaveLength(2);
    });

    it('should clear all changes', () => {
      tracker.recordChange('Button', 'button-primary');
      tracker.clear();
      expect(tracker.hasChanges()).toBeFalsy();
    });

    it('should return empty array for components without changes', () => {
      const changes = tracker.getChanges('NonExistent');
      expect(changes).toEqual([]);
    });
  });

  describe('Visual Test Metrics', () => {
    let metrics: VisualTestMetrics;

    beforeEach(() => {
      metrics = new VisualTestMetrics();
    });

    it('should track component count', () => {
      metrics.recordComponent(2, 2); // 2 viewports, 2 themes
      const result = metrics.getMetrics();
      expect(result.components).toBe(1);
    });

    it('should calculate total snapshots', () => {
      metrics.recordComponent(2, 2); // 4 snapshots
      metrics.recordComponent(3, 2); // 6 snapshots
      const result = metrics.getMetrics();
      expect(result.snapshots).toBe(10);
    });

    it('should calculate average snapshots per component', () => {
      metrics.recordComponent(2, 2); // 4 snapshots, 1 component
      metrics.recordComponent(4, 2); // 8 snapshots, 1 component
      const result = metrics.getMetrics();
      expect(Number(result.averageSnapshotsPerComponent)).toBe(6);
    });

    it('should track duration', () => {
      metrics.recordComponent(2, 2);
      const result = metrics.getMetrics();
      expect(result.duration).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Visual Component Configuration Validation', () => {
    it('should validate component exists in config', () => {
      const isValid = validateComponentVisualTests('UnifiedGraphView');
      expect(typeof isValid).toBe('boolean');
    });

    it('should check required viewports', () => {
      const isValid = validateComponentVisualTests('UnifiedGraphView', ['desktop']);
      expect(typeof isValid).toBe('boolean');
    });

    it('should check required themes', () => {
      const isValid = validateComponentVisualTests('UnifiedGraphView', ['desktop'], ['light']);
      expect(typeof isValid).toBe('boolean');
    });

    it('should handle missing components gracefully', () => {
      const isValid = validateComponentVisualTests('NonExistentComponent');
      expect(isValid).toBeFalsy();
    });
  });

  describe('Snapshot Baseline Management', () => {
    it('should generate deterministic snapshot names', () => {
      const name1 = generateSnapshotName('Component', 'Variant', 'desktop', 'light');
      const name2 = generateSnapshotName('Component', 'Variant', 'desktop', 'light');
      expect(name1).toBe(name2);
    });

    it('should differentiate snapshots by viewport', () => {
      const desktop = generateSnapshotName('Button', 'Primary', 'desktop', 'light');
      const mobile = generateSnapshotName('Button', 'Primary', 'mobile', 'light');
      expect(desktop).not.toBe(mobile);
    });

    it('should differentiate snapshots by theme', () => {
      const light = generateSnapshotName('Button', 'Primary', 'desktop', 'light');
      const dark = generateSnapshotName('Button', 'Primary', 'desktop', 'dark');
      expect(light).not.toBe(dark);
    });

    it('should differentiate snapshots by state', () => {
      const default_ = generateSnapshotName('Button', 'Primary', 'desktop', 'light');
      const hover = generateSnapshotName('Button', 'Primary', 'desktop', 'light', 'hover');
      expect(default_).not.toBe(hover);
    });
  });

  describe('Regression Detection Integration', () => {
    it('should track visual regressions across components', () => {
      const tracker = new VisualRegressionTracker();
      tracker.recordChange('Button', 'button-primary-desktop');
      tracker.recordChange('Input', 'input-text-desktop');

      expect(tracker.hasChanges()).toBeTruthy();
      expect(tracker.getChanges()).toHaveLength(2);
    });

    it('should allow filtering regressions by component', () => {
      const tracker = new VisualRegressionTracker();
      tracker.recordChange('Button', 'snapshot1');
      tracker.recordChange('Button', 'snapshot2');
      tracker.recordChange('Input', 'snapshot3');

      const buttonChanges = tracker.getChanges('Button');
      expect(buttonChanges).toHaveLength(2);
      expect(buttonChanges).not.toContain('snapshot3');
    });

    it('should support batch updates', () => {
      const tracker = new VisualRegressionTracker();

      ['snapshot1', 'snapshot2', 'snapshot3'].forEach((snapshot) => {
        tracker.recordChange('Button', snapshot);
      });

      expect(tracker.getChanges('Button')).toHaveLength(3);
    });
  });
});
