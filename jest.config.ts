/**
 * Canonical jest.config.ts — fleet-wide baseline (jest@8, ts-jest).
 *
 * Conventions:
 *   - TypeScript-first via ts-jest preset
 *   - Node test environment (no jsdom overhead for backend services)
 *   - Glob patterns: **\/*.test.ts and **\/*.spec.ts
 *   - Coverage collected from src/**/*.ts only
 *
 * To override per repo (e.g. Next.js, jsdom), fork this file or import the
 * default and spread overrides. Do not edit in place — regenerate from
 * .claude/templates/jest.config.ts.
 */
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/*.test.ts', '**/*.spec.ts'],
  collectCoverageFrom: ['src/**/*.ts'],
};

export default config;
