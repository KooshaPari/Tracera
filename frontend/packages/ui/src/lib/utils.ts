import * as Clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: Clsx.ClassValue[]): string {
  return twMerge(Clsx.clsx(inputs));
}
