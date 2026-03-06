/**
 * Simple logging utility for examples and development
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

type ConsoleMethod = (...args: unknown[]) => void;

type ConsoleGroupMethod = (label?: string, ...args: unknown[]) => void;

const consoleApi = globalThis.console;

const debugConsole: ConsoleMethod = consoleApi.debug.bind(consoleApi);
const errorConsole: ConsoleMethod = consoleApi.error.bind(consoleApi);
const groupConsole: ConsoleGroupMethod | undefined =
  typeof consoleApi.group === 'function' ? consoleApi.group.bind(consoleApi) : undefined;
const groupEndConsole: (() => void) | undefined =
  typeof consoleApi.groupEnd === 'function' ? consoleApi.groupEnd.bind(consoleApi) : undefined;
const infoConsole: ConsoleMethod = consoleApi.info.bind(consoleApi);
const warnConsole: ConsoleMethod = consoleApi.warn.bind(consoleApi);

export const logger = {
  debug: (message: string, ...args: unknown[]): void => {
    if (import.meta.env.DEV) {
      debugConsole(`[DEBUG] ${message}`, ...args);
    }
  },
  info: (message: string, ...args: unknown[]): void => {
    infoConsole(`[INFO] ${message}`, ...args);
  },
  warn: (message: string, ...args: unknown[]): void => {
    warnConsole(`[WARN] ${message}`, ...args);
  },
  error: (message: string, ...args: unknown[]): void => {
    errorConsole(`[ERROR] ${message}`, ...args);
  },
  group: (message: string, ...args: unknown[]): void => {
    if (import.meta.env.DEV && groupConsole) {
      groupConsole(message, ...args);
    } else {
      infoConsole(message, ...args);
    }
  },
  groupEnd: (): void => {
    if (import.meta.env.DEV && groupEndConsole) {
      groupEndConsole();
    }
  },
};
