// React 19-compatible shim for react-is.
//
// React 19 dropped the bitmask-based API that react-redux v7, styled-components,
// react-router, and many other libraries still import. This shim re-exports the
// legacy API by deriving the missing pieces from React 19's official symbol table.
//
// Sources:
//   - https://github.com/facebook/react/blob/main/packages/shared/ReactSymbols.js
//   - https://legacy.reactjs.org/docs/react-api.html#isvalidelementtype
//   - https://github.com/facebook/react/issues/20089#issuecomment-714713444

// React 19 exposes the symbols on React itself.
import * as React from 'react';

const REACT_ELEMENT_TYPE = Symbol.for('react.element');
const REACT_PORTAL_TYPE = Symbol.for('react.portal');
const REACT_FRAGMENT_TYPE = Symbol.for('react.fragment');
const REACT_STRICT_MODE_TYPE = Symbol.for('react.strict_mode');
const REACT_PROFILER_TYPE = Symbol.for('react.profiler');
const REACT_PROVIDER_TYPE = Symbol.for('react.provider');
const REACT_CONTEXT_TYPE = Symbol.for('react.context');
const REACT_CONCURRENT_MODE_TYPE = Symbol.for('react.concurrent_mode');
const REACT_FORWARD_REF_TYPE = Symbol.for('react.forward_ref');
const REACT_SUSPENSE_TYPE = Symbol.for('react.suspense');
const REACT_SUSPENSE_LIST_TYPE = Symbol.for('react.suspense_list');
const REACT_MEMO_TYPE = Symbol.for('react.memo');
const REACT_LAZY_TYPE = Symbol.for('react.lazy');
const REACT_SCOPE_TYPE = Symbol.for('react.scope');
const REACT_OFFSCREEN_TYPE = Symbol.for('react.offscreen');
const REACT_CACHE_TYPE = Symbol.for('react.cache');

const ContextConsumer = REACT_CONTEXT_TYPE;
const ContextProvider = REACT_PROVIDER_TYPE;
const Element = REACT_ELEMENT_TYPE;
const ForwardRef = REACT_FORWARD_REF_TYPE;
const Fragment = REACT_FRAGMENT_TYPE;
const Lazy = REACT_LAZY_TYPE;
const Memo = REACT_MEMO_TYPE;
const Portal = REACT_PORTAL_TYPE;
const Profiler = REACT_PROFILER_TYPE;
const StrictMode = REACT_STRICT_MODE_TYPE;
const Suspense = REACT_SUSPENSE_TYPE;
const SuspenseList = REACT_SUSPENSE_LIST_TYPE;
const Scope = REACT_SCOPE_TYPE;
const Offscreen = REACT_OFFSCREEN_TYPE;
const Cache = REACT_CACHE_TYPE;
const AsyncMode = REACT_CONCURRENT_MODE_TYPE;

function typeOf(node: unknown): string | null {
  if (node === null || typeof node !== 'object') return null;
  const t = (node as { $$typeof?: symbol }).$$typeof;
  if (t === REACT_ELEMENT_TYPE) return 'Element';
  if (t === REACT_PORTAL_TYPE) return 'Portal';
  if (t === REACT_FRAGMENT_TYPE) return 'Fragment';
  if (t === REACT_STRICT_MODE_TYPE) return 'StrictMode';
  if (t === REACT_PROFILER_TYPE) return 'Profiler';
  if (t === REACT_PROVIDER_TYPE) return 'ContextProvider';
  if (t === REACT_CONTEXT_TYPE) return 'ContextConsumer';
  if (t === REACT_CONCURRENT_MODE_TYPE) return 'AsyncMode';
  if (t === REACT_FORWARD_REF_TYPE) return 'ForwardRef';
  if (t === REACT_SUSPENSE_TYPE) return 'Suspense';
  if (t === REACT_SUSPENSE_LIST_TYPE) return 'SuspenseList';
  if (t === REACT_MEMO_TYPE) return 'Memo';
  if (t === REACT_LAZY_TYPE) return 'Lazy';
  if (t === REACT_SCOPE_TYPE) return 'Scope';
  if (t === REACT_OFFSCREEN_TYPE) return 'Offscreen';
  return null;
}

function isContextConsumer(value: unknown): boolean {
  return typeOf(value) === 'ContextConsumer';
}
function isContextProvider(value: unknown): boolean {
  return typeOf(value) === 'ContextProvider';
}
function isElement(value: unknown): boolean {
  return typeOf(value) === 'Element';
}
function isForwardRef(value: unknown): boolean {
  return typeOf(value) === 'ForwardRef';
}
function isFragment(value: unknown): boolean {
  return typeOf(value) === 'Fragment';
}
function isLazy(value: unknown): boolean {
  return typeOf(value) === 'Lazy';
}
function isMemo(value: unknown): boolean {
  return typeOf(value) === 'Memo';
}
function isPortal(value: unknown): boolean {
  return typeOf(value) === 'Portal';
}
function isProfiler(value: unknown): boolean {
  return typeOf(value) === 'Profiler';
}
function isStrictMode(value: unknown): boolean {
  return typeOf(value) === 'StrictMode';
}
function isSuspense(value: unknown): boolean {
  return typeOf(value) === 'Suspense';
}
function isSuspenseList(value: unknown): boolean {
  return typeOf(value) === 'SuspenseList';
}
function isAsyncMode(value: unknown): boolean {
  return typeOf(value) === 'AsyncMode';
}
function isConcurrentMode(value: unknown): boolean {
  // React 19 retired the named "ConcurrentMode"; legacy "AsyncMode" is treated
  // as an alias.
  return isAsyncMode(value);
}
function isValidElementType(value: unknown): boolean {
  if (typeof value === 'string') return true;
  if (typeof value === 'function') return true;
  if (typeof value !== 'object' || value === null) return false;
  const t = typeOf(value);
  if (t === null) return false;
  // Reject Symbol-only / cache entries; everything else is renderable.
  return t !== 'Cache';
}

const ReactIs = {
  ContextConsumer,
  ContextProvider,
  Element,
  ForwardRef,
  Fragment,
  Lazy,
  Memo,
  Portal,
  Profiler,
  StrictMode,
  Suspense,
  SuspenseList,
  AsyncMode,
  isAsyncMode,
  isConcurrentMode,
  isContextConsumer,
  isContextProvider,
  isElement,
  isForwardRef,
  isFragment,
  isLazy,
  isMemo,
  isPortal,
  isProfiler,
  isStrictMode,
  isSuspense,
  isSuspenseList,
  isValidElementType,
  typeOf,
  // React 19 compatibility.
  REACT_ELEMENT_TYPE,
  REACT_PORTAL_TYPE,
  REACT_FRAGMENT_TYPE,
  REACT_STRICT_MODE_TYPE,
  REACT_PROFILER_TYPE,
  REACT_PROVIDER_TYPE,
  REACT_CONTEXT_TYPE,
  REACT_FORWARD_REF_TYPE,
  REACT_SUSPENSE_TYPE,
  REACT_SUSPENSE_LIST_TYPE,
  REACT_MEMO_TYPE,
  REACT_LAZY_TYPE,
  REACT_CONCURRENT_MODE_TYPE,
};

// Suppress unused-React import warnings while keeping the runtime handy for
// debugging.
void React;

export {
  ContextConsumer,
  ContextProvider,
  Element,
  ForwardRef,
  Fragment,
  Lazy,
  Memo,
  Portal,
  Profiler,
  StrictMode,
  Suspense,
  SuspenseList,
  AsyncMode,
  Scope,
  Offscreen,
  Cache,
  isAsyncMode,
  isConcurrentMode,
  isContextConsumer,
  isContextProvider,
  isElement,
  isForwardRef,
  isFragment,
  isLazy,
  isMemo,
  isPortal,
  isProfiler,
  isStrictMode,
  isSuspense,
  isSuspenseList,
  isValidElementType,
  typeOf,
  REACT_ELEMENT_TYPE,
  REACT_PORTAL_TYPE,
  REACT_FRAGMENT_TYPE,
  REACT_STRICT_MODE_TYPE,
  REACT_PROFILER_TYPE,
  REACT_PROVIDER_TYPE,
  REACT_CONTEXT_TYPE,
  REACT_FORWARD_REF_TYPE,
  REACT_SUSPENSE_TYPE,
  REACT_SUSPENSE_LIST_TYPE,
  REACT_MEMO_TYPE,
  REACT_LAZY_TYPE,
  REACT_CONCURRENT_MODE_TYPE,
};

export default ReactIs;
