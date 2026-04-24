// tests/e2e/support/config/environments.ts
// Configuration: Environment Settings
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
export type Environment = 'local' | 'staging' | 'production';

export interface EnvironmentConfig {
  baseUrl: string;
  apiUrl: string;
  timeout: number;
  retries: number;
}

export const environments: Record<Environment, EnvironmentConfig> = {
  local: {
    baseUrl: 'http://localhost:3000',
    apiUrl: 'http://localhost:4000/api',
    timeout: 30000,
    retries: 2,
  },
  staging: {
    baseUrl: 'https://staging.example.com',
    apiUrl: 'https://staging-api.example.com/api',
    timeout: 60000,
    retries: 3,
  },
  production: {
    baseUrl: 'https://app.example.com',
    apiUrl: 'https://api.example.com/api',
    timeout: 90000,
    retries: 1,
  },
};

export function getEnvironment(): Environment {
  const env = process.env.TEST_ENV || 'local';
  return env as Environment;
}

export function getEnvironmentConfig(): EnvironmentConfig {
  return environments[getEnvironment()];
}
