import react from '@vitejs/plugin-react'
import path from 'path'
import type { PluginOption } from 'vite'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()] as PluginOption[],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.ts'],
    environmentOptions: {
      jsdom: {
        resources: 'usable',
      },
    },
    poolOptions: {
      threads: {
        singleThread: true,
      },
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'src/__tests__/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
        '**/dist',
      ],
      thresholds: {
        branches: 80,
        statements: 80,
        functions: 80,
        lines: 80,
      },
      all: true,
      lines: 80,
      functions: 80,
      branches: 80,
      statements: 80,
      // Use 'all' mode for coverage
      sourceMap: true,
      // Properly handle transform mode for jsdom
      transformMode: {
        web: [/\.[jt]sx?$/],
      },
    },
    include: ['src/__tests__/**/*.test.{ts,tsx}'],
    exclude: ['node_modules', 'dist', '.turbo'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
