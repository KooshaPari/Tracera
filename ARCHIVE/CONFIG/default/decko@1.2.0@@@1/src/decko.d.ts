/**
 *
 */
export function bind<T>(
    target: object,
    propertyKey: string | symbol,
    descriptor?: TypedPropertyDescriptor<T>
): TypedPropertyDescriptor<T> | void;
export function bind(): MethodDecorator;

/**
 * @param caseSensitive Makes cache keys case-insensitive
 * @param cache Presupply cache storage, for seeding or sharing entries
 */

export function memoize<T>(
    target: object,
    propertyKey: string | symbol,
    descriptor?: TypedPropertyDescriptor<T>
): TypedPropertyDescriptor<T> | void;
export function memoize(caseSensitive?: boolean, cache?: object): MethodDecorator;
/**
 * @param delay number
 */
export function debounce<T>(
    target: object,
    propertyKey: string | symbol,
    descriptor?: TypedPropertyDescriptor<T>
): TypedPropertyDescriptor<T> | void;
export function debounce(delay?: number): MethodDecorator;