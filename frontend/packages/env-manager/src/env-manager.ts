/**
 * Environment variable manager for TraceRTM frontend
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

  /**
   * Load environment variables from process.env
   */
  private loadFromProcess(): void {
    if (typeof process !== 'undefined' && process.env) {
      Object.entries(process.env).forEach(([key, value]) => {
        if (value !== undefined) {
          this.vars.set(key, String(value));
        }
      });
    }
  }

  /**
   * Load environment variables from config object
   */
  private loadFromConfig(config: EnvConfig): void {
    Object.entries(config).forEach(([key, value]) => {
      if (value !== undefined) {
        this.vars.set(key, String(value));
      }
    });
  }

  /**
   * Get environment variable as string
   */
  get(key: string, defaultValue?: string): string | undefined {
    return this.vars.get(key) ?? defaultValue;
  }

  /**
   * Get required environment variable
   */
  getRequired(key: string): string {
    const value = this.vars.get(key);
    if (!value) {
      throw new Error(`Required environment variable ${key} not set`);
    }
    return value;
  }

  /**
   * Get environment variable as number
   */
  getNumber(key: string, defaultValue?: number): number | undefined {
    const value = this.vars.get(key);
    if (!value) return defaultValue;
    const num = Number(value);
    if (Number.isNaN(num)) {
      throw new TypeError(`Environment variable ${key} is not a valid number: ${value}`);
    }
    return num;
  }

  /**
   * Get environment variable as boolean
   */
  getBoolean(key: string, defaultValue = false): boolean {
    const value = this.vars.get(key);
    if (!value) return defaultValue;
    return ['true', '1', 'yes', 'on'].includes(value.toLowerCase());
  }

  /**
   * Get environment variable as array
   */
  getArray(key: string, separator = ','): string[] {
    const value = this.vars.get(key);
    if (!value) return [];
    return value.split(separator).map((item) => item.trim());
  }

  /**
   * Get environment variable as JSON
   */
  getJSON<T = any>(key: string, defaultValue?: T): T | undefined {
    const value = this.vars.get(key);
    if (!value) return defaultValue;
    try {
      return JSON.parse(value);
    } catch (_error) {
      throw new Error(`Environment variable ${key} is not valid JSON: ${value}`, { cause: _error });
    }
  }

  /**
   * Set environment variable
   */
  set(key: string, value: string | number | boolean): void {
    this.vars.set(key, String(value));
  }

  /**
   * Check if environment variable exists
   */
  has(key: string): boolean {
    return this.vars.has(key);
  }

  /**
   * Validate that all required variables are set
   */
  validate(requiredVars: string[]): void {
    const missing = requiredVars.filter((key) => !this.vars.has(key));
    if (missing.length > 0) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
  }

  /**
   * Get all environment variables
   */
  getAll(): Record<string, string> {
    return Object.fromEntries(this.vars);
  }

  /**
   * Get environment variables by prefix
   */
  getByPrefix(prefix: string): Record<string, string> {
    const result: Record<string, string> = {};
    this.vars.forEach((value, key) => {
      if (key.startsWith(prefix)) {
        result[key] = value;
      }
    });
    return result;
  }

  /**
   * Clear all environment variables
   */
  clear(): void {
    this.vars.clear();
  }
}

// Export singleton instance
export const envManager = new EnvManager();
