/**
 * Environment variable manager for TraceRTM frontend.
 */

export type EnvConfig = Record<string, string | number | boolean | undefined>;

export class EnvManager {
  private vars: Map<string, string>;

  constructor(config?: EnvConfig) {
    this.vars = new Map();
    this.loadFromProcess();
    if (config) {
      this.loadFromConfig(config);
    }
  }

  private loadFromProcess(): void {
    if (typeof process !== 'undefined' && process.env) {
      Object.entries(process.env).forEach(([key, value]) => {
        if (value !== undefined) {
          this.vars.set(key, String(value));
        }
      });
    }
  }

  private loadFromConfig(config: EnvConfig): void {
    Object.entries(config).forEach(([key, value]) => {
      if (value !== undefined) {
        this.vars.set(key, String(value));
      }
    });
  }

  get(key: string, defaultValue?: string): string | undefined {
    return this.vars.get(key) ?? defaultValue;
  }

  getRequired(key: string): string {
    const value = this.vars.get(key);
    if (!value) {
      throw new Error(`Required environment variable ${key} not set`);
    }

    return value;
  }

  getNumber(key: string, defaultValue?: number): number | undefined {
    const value = this.vars.get(key);
    if (!value) {
      return defaultValue;
    }

    const parsedNumber = Number(value);
    if (Number.isNaN(parsedNumber)) {
      throw new TypeError(`Environment variable ${key} is not a valid number: ${value}`);
    }

    return parsedNumber;
  }

  getBoolean(key: string, defaultValue = false): boolean {
    const value = this.vars.get(key);
    if (!value) {
      return defaultValue;
    }

    return ['true', '1', 'yes', 'on'].includes(value.toLowerCase());
  }

  getArray(key: string, separator = ','): string[] {
    const value = this.vars.get(key);
    if (!value) {
      return [];
    }

    return value.split(separator).map((item) => item.trim());
  }

  getJSON<TValue>(key: string, defaultValue?: TValue): TValue | undefined {
    const value = this.vars.get(key);
    if (!value) {
      return defaultValue;
    }

    try {
      return JSON.parse(value) as TValue;
    } catch (error: unknown) {
      throw new Error(`Environment variable ${key} is not valid JSON: ${value}`, { cause: error });
    }
  }

  set(key: string, value: string | number | boolean): void {
    this.vars.set(key, String(value));
  }

  has(key: string): boolean {
    return this.vars.has(key);
  }

  validate(requiredVars: string[]): void {
    const missing = requiredVars.filter((key) => !this.vars.has(key));
    if (missing.length > 0) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
  }

  getAll(): Record<string, string> {
    return Object.fromEntries(this.vars);
  }

  getByPrefix(prefix: string): Record<string, string> {
    const result: Record<string, string> = {};
    this.vars.forEach((value, key) => {
      if (key.startsWith(prefix)) {
        result[key] = value;
      }
    });

    return result;
  }

  clear(): void {
    this.vars.clear();
  }
}

export const envManager = new EnvManager();
