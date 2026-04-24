import { afterEach, beforeEach, describe, expect, test } from 'vitest';

import type {
  FrontendConfig,
  loadFrontendConfig as LoadFrontendConfigFunction,
  validateFrontendConfig as ValidateFrontendConfigFunction,
} from '../config';

import { EnvManager } from '../env-manager';

/**
 * Helper: assert that a function throws an Error whose message contains the expected substring.
 * Vitest 4.x toThrow() is broken on Node 25, so we use try/catch.
 *
 * @param {() => unknown} fn Function expected to throw.
 * @param {string} expectedMessage Substring expected in the error message.
 */
function expectThrow(fn: () => unknown, expectedMessage: string): void {
  let caught: unknown;
  try {
    fn();
  } catch (error) {
    caught = error;
  }
  expect(caught).toBeDefined();
  expect(caught).toBeInstanceOf(Error);
  expect((caught as Error).message).toContain(expectedMessage);
}

// We import loadFrontendConfig and validateFrontendConfig lazily to avoid
// The module-level singleton `frontendConfig` from throwing when required
// Env vars are not set during module evaluation.
async function getConfigModule(): ReturnType<typeof importConfigModule> {
  return await import('../config');
}

function importConfigModule() {
  return import('../config');
}

/**
 * Helper to create an EnvManager seeded with the minimum required env vars
 * for loadFrontendConfig to succeed without throwing.
 *
 * @param {Record<string, string | number | boolean | undefined>} overrides Optional values that override defaults.
 * @returns {EnvManager} A configured EnvManager instance.
 */
function makeEnvWithRequired(
  overrides: Record<string, string | number | boolean | undefined> = {},
): EnvManager {
  const mgr = new EnvManager({
    VITE_API_URL: 'http://localhost:8080',
    VITE_WS_URL: 'ws://localhost:8080',
    VITE_WORKOS_CLIENT_ID: 'client_test_id',
    ...overrides,
  });
  return mgr;
}

describe('loadFrontendConfig', () => {
  let originalEnv: NodeJS.ProcessEnv;
  let loadFrontendConfig: LoadFrontendConfigFunction;

  beforeEach(async () => {
    originalEnv = { ...process.env };
    // Set required env vars so the module-level singleton does not throw on import.
    process.env.VITE_API_URL = 'http://import-guard';
    process.env.VITE_WS_URL = 'ws://import-guard';
    process.env.VITE_WORKOS_CLIENT_ID = 'import_guard_id';
    const mod = await getConfigModule();
    loadFrontendConfig = mod.loadFrontendConfig;
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  test('loads config with all required variables present', () => {
    const env = makeEnvWithRequired();
    const config = loadFrontendConfig(env);
    expect(config.apiUrl).toBe('http://localhost:8080');
    expect(config.wsUrl).toBe('ws://localhost:8080');
    expect(config.workosClientId).toBe('client_test_id');
  });

  test('throws when VITE_API_URL is missing', () => {
    const env = new EnvManager({
      VITE_WS_URL: 'ws://localhost',
      VITE_WORKOS_CLIENT_ID: 'id',
    });
    env.clear();
    env.set('VITE_WS_URL', 'ws://localhost');
    env.set('VITE_WORKOS_CLIENT_ID', 'id');
    expectThrow(
      () => loadFrontendConfig(env),
      'Required environment variable VITE_API_URL not set',
    );
  });

  test('throws when VITE_WS_URL is missing', () => {
    const env = new EnvManager({});
    env.clear();
    env.set('VITE_API_URL', 'http://localhost');
    env.set('VITE_WORKOS_CLIENT_ID', 'id');
    expectThrow(() => loadFrontendConfig(env), 'Required environment variable VITE_WS_URL not set');
  });

  test('throws when VITE_WORKOS_CLIENT_ID is missing', () => {
    const env = new EnvManager({});
    env.clear();
    env.set('VITE_API_URL', 'http://localhost');
    env.set('VITE_WS_URL', 'ws://localhost');
    expectThrow(
      () => loadFrontendConfig(env),
      'Required environment variable VITE_WORKOS_CLIENT_ID not set',
    );
  });

  test('applies default values for optional config', () => {
    const env = makeEnvWithRequired();
    const config = loadFrontendConfig(env);
    expect(config.appEnv).toBe('development');
    expect(config.appDebug).toBeFalsy();
    expect(config.apiTimeout).toBe(30_000);
    expect(config.apiRetries).toBe(3);
    expect(config.enableAnalytics).toBeTruthy();
    expect(config.enableSentry).toBeFalsy();
    expect(config.enableDatadog).toBeFalsy();
    expect(config.logLevel).toBe('info');
    expect(config.logFormat).toBe('json');
    expect(config.theme).toBe('auto');
    expect(config.locale).toBe('en-US');
  });

  test('respects overridden optional values', () => {
    const env = makeEnvWithRequired({
      VITE_ENVIRONMENT: 'production',
      VITE_DEBUG: 'true',
      VITE_API_TIMEOUT: '5000',
      VITE_API_RETRIES: '5',
      VITE_ENABLE_ANALYTICS: 'false',
      VITE_ENABLE_SENTRY: '1',
      VITE_ENABLE_DATADOG: 'yes',
      VITE_LOG_LEVEL: 'debug',
      VITE_LOG_FORMAT: 'text',
      VITE_THEME: 'dark',
      VITE_LOCALE: 'fr-FR',
      VITE_SUPABASE_URL: 'https://supabase.example.com',
      VITE_SUPABASE_ANON_KEY: 'anon_key_123',
    });
    const config = loadFrontendConfig(env);
    expect(config.appEnv).toBe('production');
    expect(config.appDebug).toBeTruthy();
    expect(config.apiTimeout).toBe(5000);
    expect(config.apiRetries).toBe(5);
    expect(config.enableAnalytics).toBeFalsy();
    expect(config.enableSentry).toBeTruthy();
    expect(config.enableDatadog).toBeTruthy();
    expect(config.logLevel).toBe('debug');
    expect(config.logFormat).toBe('text');
    expect(config.theme).toBe('dark');
    expect(config.locale).toBe('fr-FR');
    expect(config.supabaseUrl).toBe('https://supabase.example.com');
    expect(config.supabaseAnonKey).toBe('anon_key_123');
  });

  test('defaults supabaseUrl and supabaseAnonKey to empty strings', () => {
    const env = makeEnvWithRequired();
    const config = loadFrontendConfig(env);
    expect(config.supabaseUrl).toBe('');
    expect(config.supabaseAnonKey).toBe('');
  });

  test('creates a new EnvManager when none is provided', () => {
    process.env.VITE_API_URL = 'http://from-process';
    process.env.VITE_WS_URL = 'ws://from-process';
    process.env.VITE_WORKOS_CLIENT_ID = 'from_process_id';
    const config = loadFrontendConfig();
    expect(config.apiUrl).toBe('http://from-process');
    expect(config.wsUrl).toBe('ws://from-process');
    expect(config.workosClientId).toBe('from_process_id');
  });
});

describe('validateFrontendConfig', () => {
  let validateFrontendConfig: ValidateFrontendConfigFunction;

  beforeEach(async () => {
    // Set required env vars so the module-level singleton does not throw on import.
    process.env.VITE_API_URL = 'http://import-guard';
    process.env.VITE_WS_URL = 'ws://import-guard';
    process.env.VITE_WORKOS_CLIENT_ID = 'import_guard_id';
    const mod = await getConfigModule();
    validateFrontendConfig = mod.validateFrontendConfig;
  });

  function makeValidConfig(overrides: Partial<FrontendConfig> = {}): FrontendConfig {
    return {
      appEnv: 'development',
      appDebug: false,
      apiUrl: 'http://localhost:8080',
      wsUrl: 'ws://localhost:8080',
      apiTimeout: 30_000,
      apiRetries: 3,
      workosClientId: 'client_id',
      supabaseUrl: '',
      supabaseAnonKey: '',
      enableAnalytics: true,
      enableSentry: false,
      enableDatadog: false,
      logLevel: 'info',
      logFormat: 'json',
      theme: 'auto',
      locale: 'en-US',
      ...overrides,
    };
  }

  test('does not throw for a valid config', () => {
    validateFrontendConfig(makeValidConfig());
  });

  test('throws when apiUrl is empty', () => {
    expectThrow(
      () => validateFrontendConfig(makeValidConfig({ apiUrl: '' })),
      'VITE_API_URL is required',
    );
  });

  test('throws when wsUrl is empty', () => {
    expectThrow(
      () => validateFrontendConfig(makeValidConfig({ wsUrl: '' })),
      'VITE_WS_URL is required',
    );
  });

  test('throws when workosClientId is empty', () => {
    expectThrow(
      () => validateFrontendConfig(makeValidConfig({ workosClientId: '' })),
      'VITE_WORKOS_CLIENT_ID is required',
    );
  });

  test('throws when apiTimeout is below 1000', () => {
    expectThrow(
      () => validateFrontendConfig(makeValidConfig({ apiTimeout: 500 })),
      'VITE_API_TIMEOUT must be at least 1000ms',
    );
  });

  test('throws when apiRetries is negative', () => {
    expectThrow(
      () => validateFrontendConfig(makeValidConfig({ apiRetries: -1 })),
      'VITE_API_RETRIES must be non-negative',
    );
  });

  test('throws for invalid appEnv', () => {
    expectThrow(
      () =>
        validateFrontendConfig(
          makeValidConfig({ appEnv: 'invalid' as unknown as FrontendConfig['appEnv'] }),
        ),
      'Invalid VITE_ENVIRONMENT: invalid',
    );
  });

  test('throws for invalid logLevel', () => {
    expectThrow(
      () =>
        validateFrontendConfig(
          makeValidConfig({ logLevel: 'verbose' as unknown as FrontendConfig['logLevel'] }),
        ),
      'Invalid VITE_LOG_LEVEL: verbose',
    );
  });

  test('throws for invalid theme', () => {
    expectThrow(
      () =>
        validateFrontendConfig(
          makeValidConfig({ theme: 'midnight' as unknown as FrontendConfig['theme'] }),
        ),
      'Invalid VITE_THEME: midnight',
    );
  });

  test('collects multiple errors and reports all of them', () => {
    const badConfig = makeValidConfig({
      apiUrl: '',
      wsUrl: '',
      workosClientId: '',
      apiTimeout: 100,
      apiRetries: -2,
      appEnv: 'bogus' as unknown as FrontendConfig['appEnv'],
      logLevel: 'trace' as unknown as FrontendConfig['logLevel'],
      theme: 'neon' as unknown as FrontendConfig['theme'],
    });
    let caught: unknown;
    try {
      validateFrontendConfig(badConfig);
    } catch (error) {
      caught = error;
    }
    expect(caught).toBeDefined();
    const message = (caught as Error).message;
    expect(message).toContain('Configuration validation failed:');
    expect(message).toContain('VITE_API_URL is required');
    expect(message).toContain('VITE_WS_URL is required');
    expect(message).toContain('VITE_WORKOS_CLIENT_ID is required');
    expect(message).toContain('VITE_API_TIMEOUT must be at least 1000ms');
    expect(message).toContain('VITE_API_RETRIES must be non-negative');
    expect(message).toContain('Invalid VITE_ENVIRONMENT: bogus');
    expect(message).toContain('Invalid VITE_LOG_LEVEL: trace');
    expect(message).toContain('Invalid VITE_THEME: neon');
  });

  test('accepts valid appEnv values: staging and production', () => {
    validateFrontendConfig(makeValidConfig({ appEnv: 'staging' }));
    validateFrontendConfig(makeValidConfig({ appEnv: 'production' }));
  });

  test('accepts valid logLevel values', () => {
    for (const level of ['debug', 'info', 'warn', 'error'] as const) {
      validateFrontendConfig(makeValidConfig({ logLevel: level }));
    }
  });

  test('accepts valid theme values', () => {
    for (const theme of ['light', 'dark', 'auto'] as const) {
      validateFrontendConfig(makeValidConfig({ theme }));
    }
  });

  test('accepts apiRetries of zero', () => {
    validateFrontendConfig(makeValidConfig({ apiRetries: 0 }));
  });

  test('accepts apiTimeout of exactly 1000', () => {
    validateFrontendConfig(makeValidConfig({ apiTimeout: 1000 }));
  });
});
