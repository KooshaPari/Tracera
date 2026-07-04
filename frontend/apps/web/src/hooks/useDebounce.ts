import { useEffect, useState } from 'react';

const DEFAULT_DELAY = 300;

export const useDebounce = <Value>(value: Value, delay = DEFAULT_DELAY): Value => {
  const [debouncedValue, setDebouncedValue] = useState<Value>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
};
