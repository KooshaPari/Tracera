/**
 * Simple logging utility for examples and development
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export const logger = {
  debug: (message: string, ...args: unknown[]) => {
    if (import.meta.env.DEV) {
      console.debug(`[DEBUG] ${message}`, ...args);
    }
  },
  info: (message: string, ...args: unknown[]) => {
    console.info(`[INFO] ${message}`, ...args);
  },
  warn: (message: string, ...args: unknown[]) => {
    console.warn(`[WARN] ${message}`, ...args);
  },
  error: (message: string, ...args: unknown[]) => {
    console.error(`[ERROR] ${message}`, ...args);
  },
  group: (message: string, ...args: unknown[]) => {
    if (import.meta.env.DEV && typeof console.group === 'function') {
      console.group(message, ...args);
    } else {
      console.info(message, ...args);
    }
  },
  groupEnd: () => {
    if (import.meta.env.DEV && typeof console.groupEnd === 'function') {
      console.groupEnd();
    }
  },
};
