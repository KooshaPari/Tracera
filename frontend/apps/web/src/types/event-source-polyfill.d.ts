declare module 'event-source-polyfill' {
  export interface EventSourceInit {
    headers?: Record<string, string>;
    heartbeatTimeout?: number;
    [key: string]: unknown;
  }

  export class EventSource extends EventTarget {
    constructor(url: string, init?: EventSourceInit);
    readonly url: string;
    readonly readyState: number;
    readonly withCredentials: boolean;
    onopen: ((this: EventSource, ev: Event) => unknown) | null;
    onmessage: ((this: EventSource, ev: MessageEvent) => unknown) | null;
    onerror: ((this: EventSource, ev: Event) => unknown) | null;
    addEventListener(
      type: string,
      listener: EventListenerOrEventListenerObject,
      options?: boolean | AddEventListenerOptions,
    ): void;
    removeEventListener(
      type: string,
      listener: EventListenerOrEventListenerObject,
      options?: boolean | EventListenerOptions,
    ): void;
    close(): void;
  }

  export const CONNECTING: number;
  export const OPEN: number;
  export const CLOSED: number;

  /** Polyfill constructor (default export). */
  export default EventSource;
}

export type EventSourcePolyfillModule = Record<string, unknown>;
