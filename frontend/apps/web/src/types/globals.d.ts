/* eslint-disable import/no-named-export, import/group-exports, import/unambiguous */
// Global type definitions

/// <reference types="vite/client" />

declare global {
  // Vite environment variables
  interface ImportMetaEnv {
    readonly VITE_API_URL: string;
    readonly VITE_WS_URL: string;
    readonly VITE_APP_NAME: string;
    readonly VITE_APP_VERSION: string;
    readonly MODE: string;
    readonly DEV: boolean;
    readonly PROD: boolean;
    readonly SSR: boolean;
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }

  // Window extensions
  interface Window {
    __TRACERTM_DEVTOOLS__?: boolean;
    __wsCheckInterval?: ReturnType<typeof setInterval>;
  }

  // Test setup: user-event instance (see test/setup.ts)
  interface GlobalThis {
    user?: ReturnType<typeof import('@testing-library/user-event').default.setup>;
  }
}

// Module declarations
declare module '*.svg' {
  import React from 'react';
  export const ReactComponent: React.FC<React.SVGProps<SVGSVGElement>>;
  const src: string;
  export default src;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

declare module '*.jpeg' {
  const content: string;
  export default content;
}

declare module '*.gif' {
  const content: string;
  export default content;
}

declare module '*.webp' {
  const content: string;
  export default content;
}

declare module '*.css' {
  const content: Record<string, string>;
  export default content;
}

declare module '*.module.css' {
  const classes: Record<string, string>;
  export default classes;
}

// Extend JSX namespace for React components
declare namespace JSX {
  interface Element extends React.ReactElement<unknown, unknown> {}
  interface ElementClass extends React.Component<unknown> {
    render(): React.ReactNode;
  }
  type ElementAttributesProperty = Record<string, unknown>;
  type ElementChildrenAttribute = Record<string, unknown>;
  type IntrinsicElements = Record<string, unknown>;
}

export type GlobalTypesModule = Record<string, unknown>;
