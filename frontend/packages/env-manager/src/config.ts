/**
 * Configuration loader for TraceRTM frontend
 */

import { EnvManager } from './env-manager';

const DEFAULT_API_TIMEOUT_MS = 30_000;
const DEFAULT_API_RETRIES = 3;
const MIN_API_TIMEOUT_MS = 1000;

const APP_ENVIRONMENTS = ['development', 'staging', 'production'] as const;
const LOG_LEVELS = ['debug', 'info', 'warn', 'error'] as const;
const LOG_FORMATS = ['json', 'text'] as const;
const THEMES = ['light', 'dark', 'auto'] as const;

type AppEnvironment = (typeof APP_ENVIRONMENTS)[number];
type LogLevel = (typeof LOG_LEVELS)[number];
type LogFormat = (typeof LOG_FORMATS)[number];
type Theme = (typeof THEMES)[number];

export interface FrontendConfig {
  // Application
  appEnv: AppEnvironment;
  appDebug: boolean;

  // API
  apiUrl: string;
  wsUrl: string;
  apiTimeout: number;
  apiRetries: number;

  // Authentication
  workosClientId: string;
  supabaseUrl: string;
  supabaseAnonKey: string;

  // Features
  enableAnalytics: boolean;
  enableSentry: boolean;
  enableDatadog: boolean;

  // Logging
  logLevel: LogLevel;
  logFormat: LogFormat;

  // UI
  theme: Theme;
  locale: string;
}

function readAllowedValue<TAllowedValues extends readonly string[]>(
  env: EnvManager,
  key: string,
  fallback: TAllowedValues[number],
  allowedValues: TAllowedValues,
): TAllowedValues[number] {
  const value = env.get(key, fallback) ?? fallback;
  return allowedValues.includes(value as TAllowedValues[number])
    ? (value as TAllowedValues[number])
    : fallback;
}

export function loadFrontendConfig(envManager?: EnvManager): FrontendConfig {
  const env = envManager || new EnvManager();

  const config: FrontendConfig = {
    // Application
    appEnv: readAllowedValue(env, 'VITE_ENVIRONMENT', 'development', APP_ENVIRONMENTS),
    appDebug: env.getBoolean('VITE_DEBUG', false),

    // API
    apiUrl: env.getRequired('VITE_API_URL'),
    wsUrl: env.getRequired('VITE_WS_URL'),
    apiTimeout: env.getNumber('VITE_API_TIMEOUT', DEFAULT_API_TIMEOUT_MS) || DEFAULT_API_TIMEOUT_MS,
    apiRetries: env.getNumber('VITE_API_RETRIES', DEFAULT_API_RETRIES) || DEFAULT_API_RETRIES,

    // Authentication
    workosClientId: env.getRequired('VITE_WORKOS_CLIENT_ID'),
    supabaseUrl: env.get('VITE_SUPABASE_URL') || '',
    supabaseAnonKey: env.get('VITE_SUPABASE_ANON_KEY') || '',

    // Features
    enableAnalytics: env.getBoolean('VITE_ENABLE_ANALYTICS', true),
    enableSentry: env.getBoolean('VITE_ENABLE_SENTRY', false),
    enableDatadog: env.getBoolean('VITE_ENABLE_DATADOG', false),

    // Logging
    logLevel: readAllowedValue(env, 'VITE_LOG_LEVEL', 'info', LOG_LEVELS),
    logFormat: readAllowedValue(env, 'VITE_LOG_FORMAT', 'json', LOG_FORMATS),

    // UI
    theme: readAllowedValue(env, 'VITE_THEME', 'auto', THEMES),
    locale: env.get('VITE_LOCALE') || 'en-US',
  };

  return config;
}

export function validateFrontendConfig(config: FrontendConfig): void {
  const errors: string[] = [];

  if (!config.apiUrl) {
    errors.push('VITE_API_URL is required');
  }

  if (!config.wsUrl) {
    errors.push('VITE_WS_URL is required');
  }

  if (!config.workosClientId) {
    errors.push('VITE_WORKOS_CLIENT_ID is required');
  }

  if (config.apiTimeout < MIN_API_TIMEOUT_MS) {
    errors.push('VITE_API_TIMEOUT must be at least 1000ms');
  }

  if (config.apiRetries < 0) {
    errors.push('VITE_API_RETRIES must be non-negative');
  }

  if (!APP_ENVIRONMENTS.includes(config.appEnv)) {
    errors.push(`Invalid VITE_ENVIRONMENT: ${config.appEnv}`);
  }

  if (!LOG_LEVELS.includes(config.logLevel)) {
    errors.push(`Invalid VITE_LOG_LEVEL: ${config.logLevel}`);
  }

  if (!THEMES.includes(config.theme)) {
    errors.push(`Invalid VITE_THEME: ${config.theme}`);
  }

  if (errors.length > 0) {
    throw new Error(`Configuration validation failed:\n${errors.join('\n')}`);
  }
}

// Export singleton instance
export const frontendConfig = loadFrontendConfig();
