declare module '*.css' {
  const content: Record<string, string>;
  export default content;
}

declare module 'react-original' {
  import type * as ReactNamespace from 'react';
  const React: typeof ReactNamespace;
  export default React;
  export * from 'react';
}
