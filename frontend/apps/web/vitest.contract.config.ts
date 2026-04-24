import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    fileParallelism: false,
    globals: true,
    include: ['../../../tests/contracts/consumer/**/*.contract.test.ts'],
    maxWorkers: 1,
    minWorkers: 1,
    testTimeout: 60_000,
  },
});
