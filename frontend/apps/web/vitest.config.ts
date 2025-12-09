import react from '@vitejs/plugin-react'
import path from 'path'
import type { PluginOption } from 'vite'
import { defineConfig } from 'vitest/config'

// Plugin to stub CSS imports - runs before Vite's built-in CSS processing
const cssStubPlugin = (): PluginOption => ({
  name: 'css-stub',
  enforce: 'pre',
  load(id) {
    if (id.endsWith('.css') || id.endsWith('.scss') || id.endsWith('.sass') || id.endsWith('.less')) {
      return 'export default {}'
    }
    return null
  },
})

export default defineConfig({
  plugins: [cssStubPlugin(), react()] as PluginOption[],
  css: {
    postcss: {
      plugins: [], // Empty plugins array to bypass PostCSS processing
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.ts'],
    testTimeout: 10000, // Increase timeout for coverage runs
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
    css: false, // Disable CSS processing to avoid Tailwind v4 PostCSS issues in tests
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
    exclude: [
      'node_modules',
      'dist',
      '.turbo',
      // Page and route tests require full router integration - use view tests for component coverage
      'src/__tests__/pages/**',
      'src/__tests__/routes/**',
    ],
  },
  resolve: {
    alias: {
      '@/routeTree.gen': path.resolve(__dirname, './src/__tests__/mocks/routeTree.mock.ts'),
      '@': path.resolve(__dirname, './src'),
    },
  },
})
