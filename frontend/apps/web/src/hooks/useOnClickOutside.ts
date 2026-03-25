import { useCallback, useEffect } from 'react';

const isNodeTarget = (target: EventTarget | null): target is Node => target instanceof Node;

export const useOnClickOutside = <ElementType extends HTMLElement = HTMLElement>(
  ref: React.RefObject<ElementType | null>,
  handler: (event: MouseEvent | TouchEvent) => void,
): void => {
  const listener = useCallback(
    (event: MouseEvent | TouchEvent): void => {
      const element = ref.current;
      const { target } = event;

      if (element === null || !isNodeTarget(target) || element.contains(target)) {
        return;
      }

      handler(event);
    },
    [handler, ref],
  );

  useEffect((): (() => void) => {
    if (typeof document === 'undefined') {
      return () => {};
    }

    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    return (): void => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [listener]);
};
