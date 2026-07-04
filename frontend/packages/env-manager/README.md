# @tracertm/env-manager

Environment variable manager for TraceRTM frontend with type-safe access and validation.

## Installation

```bash
npm install @tracertm/env-manager
# or
yarn add @tracertm/env-manager
# or
pnpm add @tracertm/env-manager
```

## Quick Start

```typescript
import { EnvManager, loadFrontendConfig, validateFrontendConfig } from '@tracertm/env-manager';

// Create manager
const env = new EnvManager();

// Get environment variables
const apiUrl = env.get('VITE_API_URL');
const timeout = env.getNumber('VITE_API_TIMEOUT', 30000);
const debug = env.getBoolean('VITE_DEBUG', false);

// Or use configuration loader
const config = loadFrontendConfig();
validateFrontendConfig(config);

console.log(config.apiUrl);
console.log(config.logLevel);
```

## API

### EnvManager

#### `get(key: string, defaultValue?: string): string | undefined`

Get environment variable as string.

#### `getRequired(key: string): string`

Get required environment variable. Throws if not set.

#### `getNumber(key: string, defaultValue?: number): number | undefined`

Get environment variable as number.

#### `getBoolean(key: string, defaultValue?: boolean): boolean`

Get environment variable as boolean.

#### `getArray(key: string, separator?: string): string[]`

Get environment variable as array.

#### `getJSON<T>(key: string, defaultValue?: T): T | undefined`

Get environment variable as JSON.

#### `set(key: string, value: string | number | boolean): void`

Set environment variable.

#### `has(key: string): boolean`

Check if environment variable exists.

#### `validate(requiredVars: string[]): void`

Validate that all required variables are set.

#### `getAll(): Record<string, string>`

Get all environment variables.

#### `getByPrefix(prefix: string): Record<string, string>`

Get environment variables by prefix.

#### `clear(): void`

Clear all environment variables.

## Configuration

Use `loadFrontendConfig()` to load typed configuration:

```typescript
import { loadFrontendConfig, validateFrontendConfig } from '@tracertm/env-manager';

const config = loadFrontendConfig();
validateFrontendConfig(config);

// Access typed properties
console.log(config.apiUrl); // string
console.log(config.apiTimeout); // number
console.log(config.appDebug); // boolean
console.log(config.logLevel); // "debug" | "info" | "warn" | "error"
```

## Environment Variables

### Required

- `VITE_API_URL` - Backend API URL
- `VITE_WS_URL` - WebSocket URL
- `VITE_WORKOS_CLIENT_ID` - WorkOS client ID

### Optional

- `VITE_ENVIRONMENT` - Environment (development/staging/production)
- `VITE_DEBUG` - Debug mode (true/false)
- `VITE_API_TIMEOUT` - API timeout in ms (default: 30000)
- `VITE_API_RETRIES` - API retries (default: 3)
- `VITE_SUPABASE_URL` - Supabase URL
- `VITE_SUPABASE_ANON_KEY` - Supabase anon key
- `VITE_ENABLE_ANALYTICS` - Enable analytics (default: true)
- `VITE_ENABLE_SENTRY` - Enable Sentry (default: false)
- `VITE_ENABLE_DATADOG` - Enable Datadog (default: false)
- `VITE_LOG_LEVEL` - Log level (default: info)
- `VITE_LOG_FORMAT` - Log format (default: json)
- `VITE_THEME` - Theme (light/dark/auto, default: auto)
- `VITE_LOCALE` - Locale (default: en-US)

## Examples

### Type-safe access

```typescript
const env = new EnvManager();

// String
const apiUrl: string | undefined = env.get('VITE_API_URL');

// Number with default
const timeout: number = env.getNumber('VITE_API_TIMEOUT', 30000);

// Boolean
const debug: boolean = env.getBoolean('VITE_DEBUG', false);

// Array
const items: string[] = env.getArray('VITE_ITEMS', ',');

// JSON
const config: any = env.getJSON('VITE_CONFIG', {});
```

### Validation

```typescript
const env = new EnvManager();

try {
  env.validate(['VITE_API_URL', 'VITE_WS_URL']);
  console.log('All required variables are set');
} catch (error) {
  console.error('Missing required variables:', error.message);
}
```

### Prefix filtering

```typescript
const env = new EnvManager();

// Get all VITE_ variables
const viteVars = env.getByPrefix('VITE_');
console.log(viteVars);
```

## License

MIT
