/**
 * Ambient module declarations for `d3-quadtree`.
 *
 * The runtime npm package ships pure JavaScript with no bundled type
 * definitions, and `@types/d3-quadtree` is not installed. The shapes below
 * mirror the upstream DefinitelyTyped definitions so that consumers
 * (e.g. `quadTreeIndex.ts`) can use `Quadtree<T>`, `QuadtreeLeaf<T>`, and
 * `QuadtreeInternalNode<T>` for fully typed callbacks.
 *
 * @see https://github.com/DefinitelyTyped/DefinitelyTyped/blob/master/types/d3-quadtree/index.d.ts
 */

declare module 'd3-quadtree' {
  /**
   * Leaf node of the quadtree.
   */
  export interface QuadtreeLeaf<T> {
    data: T;
    next?: QuadtreeLeaf<T> | undefined;
    length?: undefined;
  }

  /**
   * Internal nodes of the quadtree are four-element arrays.
   * A child quadrant may be undefined if it is empty.
   */
  export interface QuadtreeInternalNode<T> extends Array<QuadtreeInternalNode<T> | QuadtreeLeaf<T> | undefined> {
    length: 4;
  }

  export type QuadtreeNode<T> = QuadtreeInternalNode<T> | QuadtreeLeaf<T>;

  export interface Quadtree<T> {
    x(): (d: T) => number;
    x(x: (d: T) => number): this;

    y(): (d: T) => number;
    y(y: (d: T) => number): this;

    extent(): [[number, number], [number, number]] | undefined;
    extent(extend: [[number, number], [number, number]]): this;

    cover(x: number, y: number): this;

    add(datum: T): this;
    addAll(data: T[]): this;
    remove(datum: T): this;
    removeAll(data: T[]): this;

    copy(): Quadtree<T>;

    root(): QuadtreeInternalNode<T> | QuadtreeLeaf<T>;

    data(): T[];

    size(): number;

    find(x: number, y: number, radius?: number): T | undefined;

    visit(
      callback: (
        node: QuadtreeInternalNode<T> | QuadtreeLeaf<T>,
        x0: number,
        y0: number,
        x1: number,
        y1: number,
      ) => void | boolean,
    ): this;

    visitAfter(
      callback: (
        node: QuadtreeInternalNode<T> | QuadtreeLeaf<T>,
        x0: number,
        y0: number,
        x1: number,
        y1: number,
      ) => void,
    ): this;
  }

  export function quadtree<T = [number, number]>(data?: T[]): Quadtree<T>;
  export function quadtree<T = [number, number]>(
    data: T[],
    x: (d: T) => number,
    y: (d: T) => number,
  ): Quadtree<T>;
}
