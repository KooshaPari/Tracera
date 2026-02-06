// Mock elkjs before any imports
import { vi } from 'vitest';

vi.mock('elkjs', () => ({
  default: class MockELK {
    private readonly version = 'mock';

    async layout(): Promise<{ children: unknown[]; edges: unknown[]; version: string }> {
      await Promise.resolve();
      return { children: [], edges: [], version: this.version };
    }
  },
}));

// Mock clipboard
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn(async (): Promise<void> => {
      await Promise.resolve();
    }),
  },
});
