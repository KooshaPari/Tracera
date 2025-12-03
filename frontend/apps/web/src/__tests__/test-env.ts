/**
 * Custom test environment setup
 */

// @ts-expect-error - jsdom types may not be available
import { JSDOM } from 'jsdom'
import type { Environment, EnvironmentOptions } from 'vitest'
import { vi } from 'vitest'
import { populateGlobal } from 'vitest/environments'

export default class CustomTestEnvironment implements Environment {
  name = 'custom-test-env'
  dom: JSDOM
  transformMode = 'ssr' as const

  async setup(global: any, { jsdom = {} }: EnvironmentOptions) {
    this.dom = new JSDOM('<!DOCTYPE html>', {
      ...(jsdom as any),
      pretendToBeVisual: true,
      url: 'http://localhost/',
    })

    const { window } = this.dom
    const globalWindow = window as typeof globalThis

    // Populate global with DOM
    populateGlobal(global, globalWindow, { bindFunctions: true })

    // Setup localStorage BEFORE anything else
    const localStorageMock = (() => {
      let store: Record<string, string> = {}

      return {
        getItem: (key: string) => store[key] || null,
        setItem: (key: string, value: string) => {
          store[key] = value.toString()
        },
        removeItem: (key: string) => {
          delete store[key]
        },
        clear: () => {
          store = {}
        },
        get length() {
          return Object.keys(store).length
        },
        key: (index: number) => {
          const keys = Object.keys(store)
          return keys[index] || null
        },
      }
    })()

    Object.defineProperty(global, 'localStorage', {
      value: localStorageMock,
      writable: true,
      configurable: true,
    })

    Object.defineProperty(global.window, 'localStorage', {
      value: localStorageMock,
      writable: true,
      configurable: true,
    })

    return {
      teardown: () => {
        this.dom.window.close()
      },
    }
  }
}
