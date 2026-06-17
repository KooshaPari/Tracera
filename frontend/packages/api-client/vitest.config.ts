import { defineConfig } from 'vitest/config';

export default defineConfig({
  resolve: {
    alias: {
      '@tracertm/types': new URL('../types/src/index.ts', import.meta.url).pathname,
    },
  },
  test: {
    include: ['src/**/*.test.ts'],
  },
});
