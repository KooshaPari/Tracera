import react from '@vitejs/plugin-react';
import path from 'node:path';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    coverage: {
      exclude: ['src/**/*.{test,spec,stories}.{ts,tsx}', 'src/test/**'],
      include: ['src/**/*.{ts,tsx}'],
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      thresholds: {
        branches: 90,
        functions: 90,
        lines: 90,
        statements: 90,
      },
    },
    environment: 'jsdom',
    globals: true,
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    reporters: [
      'verbose',
      ['json', { outputFile: './test-results/api-routes.json' }],
      ['html', { outputFile: './test-results/api-routes.html' }],
    ],
    setupFiles: ['./src/test/setup.ts'],
    testTimeout: 30000,
    ui: true,
  },
});
