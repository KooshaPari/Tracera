// Global type definitions

/// <reference types="vite/client" />
/// <reference types="react" />

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

// Re-export types for packages without proper 'exports' field (bundler resolution workaround)
declare module 'prop-types' {
  export * from '@types/prop-types/index.d.ts';
}

declare module 'react-is' {
  export * from '@types/react-is/index.d.ts';
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

// Merge React's JSX namespace into global scope for element type support
declare global {
  namespace JSX {
    type Element = React.JSX.Element;
    type ElementClass = React.JSX.ElementClass;
    type ElementAttributesProperty = React.JSX.ElementAttributesProperty;
    type ElementChildrenAttribute = React.JSX.ElementChildrenAttribute;
    type IntrinsicElements = React.JSX.IntrinsicElements;
  }
}

export type GlobalTypesModule = Record<string, unknown>;
