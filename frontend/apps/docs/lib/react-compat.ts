import * as ReactType from 'react';
import * as ReactOriginal from 'react-original';

const React = ReactOriginal as unknown as typeof ReactType;

export * from 'react-original';
export default React;

export const useEffectEvent =
  (React as typeof ReactType & { useEffectEvent?: typeof ReactType.useEffect }).useEffectEvent ??
  ((handler: (...args: unknown[]) => unknown) => handler as typeof ReactType.useEffectEvent);
