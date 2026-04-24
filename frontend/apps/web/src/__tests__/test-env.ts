/**
 * Custom test environment setup
 */

import type { Environment, EnvironmentOptions } from 'vitest';

import { JSDOM } from 'jsdom';
import { populateGlobal } from 'vitest/environments';

export default class CustomTestEnvironment implements Environment {
  name = 'custom-test-env';
  dom!: JSDOM;
  transformMode = 'ssr' as const;

  async setup(global: typeof globalThis, { jsdom = {} }: EnvironmentOptions) {
    this.dom = new JSDOM('<!DOCTYPE html>', {
      ...(jsdom as any),
      pretendToBeVisual: true,
      url: 'http://localhost/',
    });

    const { window } = this.dom;
    const globalWindow = window as typeof globalThis;

    // Populate global with DOM
    populateGlobal(global, globalWindow, { bindFunctions: true });

    // Setup localStorage BEFORE anything else
    const localStorageMock = (() => {
      let store: Record<string, string> = {};

      return {
        clear: () => {
          store = {};
        },
        getItem: (key: string) => store[key] || null,
        key: (index: number) => {
          const keys = Object.keys(store);
          return keys[index] || null;
        },
        get length() {
          return Object.keys(store).length;
        },
        removeItem: (key: string) => {
          delete store[key];
        },
        setItem: (key: string, value: string) => {
          store[key] = value.toString();
        },
      };
    })();

    Object.defineProperty(global, 'localStorage', {
      configurable: true,
      value: localStorageMock,
      writable: true,
    });

    Object.defineProperty(global.window, 'localStorage', {
      configurable: true,
      value: localStorageMock,
      writable: true,
    });

    return {
      teardown: () => {
        this.dom.window.close();
      },
    };
  }
}
