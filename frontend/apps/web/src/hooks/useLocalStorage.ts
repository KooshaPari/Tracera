import { useEffect, useState } from 'react';

import { logger } from '@/lib/logger';

export function useLocalStorage<T>(
  key: string,
  initialValue: T,
): [T, (value: T | ((val: T) => T)) => void] {
  // Get from local storage then parse stored json or return initialValue
  const readValue = (): T => {
    if (typeof globalThis.window === 'undefined') {
      return initialValue;
    }

    try {
      const item = globalThis.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      logger.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  };

  const [storedValue, setStoredValue] = useState<T>(readValue);

  // Return a wrapped version of useState's setter function that persists to localStorage
  const setValue = (value: T | ((val: T) => T)) => {
    try {
      // Allow value to be a function so we have same API as useState
      const valueToStore =
        typeof value === 'function' ? (value as (val: T) => T)(storedValue) : value;

      // Save state
      setStoredValue(valueToStore);

      // Save to local storage
      if (typeof globalThis.window !== 'undefined') {
        globalThis.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      logger.warn(`Error setting localStorage key "${key}":`, error);
    }
  };

  // Listen for changes from other tabs/windows
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue) {
        try {
          setStoredValue(JSON.parse(e.newValue));
        } catch (error) {
          logger.warn(`Error parsing storage event for key "${key}":`, error);
        }
      }
    };

    if (typeof globalThis.window === 'undefined') {
      return;
    }

    globalThis.addEventListener('storage', handleStorageChange);
    return () => {
      globalThis.removeEventListener('storage', handleStorageChange);
    };
  }, [key]);

  return [storedValue, setValue];
}
