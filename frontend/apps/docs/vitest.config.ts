import react from '@vitejs/plugin-react';
import path from 'node:path';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
    },
  },
  test: {
    coverage: {
      exclude: [
        '**/*.{test,spec}.{ts,tsx}',
        '**/test/**',
        '**/e2e/**',
        '**/*.config.*',
        '**/scripts/**',
        '**/.next/**',
        '**/content/**',
        '**/react-compat.ts',
      ],
      include: ['app/**/*.{ts,tsx}', 'components/**/*.{ts,tsx}', 'lib/**/*.{ts,tsx}'],
      provider: 'v8',
      reporter: ['text', 'json', 'lcov'],
      thresholds: {
        branches: 85,
        functions: 85,
        lines: 85,
        statements: 85,
      },
    },
    environment: 'jsdom',
    exclude: ['**/e2e/**', '**/node_modules/**'],
    globals: true,
    include: ['**/*.{test,spec}.{ts,tsx}'],
    setupFiles: ['./src/test/setup.ts'],
  },
});
