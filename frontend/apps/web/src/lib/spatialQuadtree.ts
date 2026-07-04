/**
 * Spatial Quadtree for O(log n) Node Lookup
 *
 * Used for efficient spatial queries in large graphs.
 * Replaces O(n) linear searches with O(log n) quadtree queries.
 *
 * Example:
 * ```
 * const tree = new SpatialQuadtree(nodes);
 * const nearbyNodes = tree.query({ minX: 100, maxX: 200, minY: 50, maxY: 150 });
 * ```
 */

export interface Point {
  x: number;
  y: number;
}

export interface Bounds {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
}

export interface QuadtreeNode<T> {
  id: string;
  position: Point;
  data: T;
}

/**
 * Calculate bounds from array of nodes
 */
export function calculateBounds<T>(nodes: QuadtreeNode<T>[]): Bounds {
  if (nodes.length === 0) {
    return { minX: 0, maxX: 0, minY: 0, maxY: 0 };
  }

  const first = nodes[0]!;
  let minX = first.position.x;
  let maxX = first.position.x;
  let minY = first.position.y;
  let maxY = first.position.y;

  for (const node of nodes) {
    minX = Math.min(minX, node.position.x);
    maxX = Math.max(maxX, node.position.x);
    minY = Math.min(minY, node.position.y);
    maxY = Math.max(maxY, node.position.y);
  }

  // Add padding to prevent division by zero
  const padding = 1;
  if (minX === maxX) {
    minX -= padding;
    maxX += padding;
  }
  if (minY === maxY) {
    minY -= padding;
    maxY += padding;
  }

  return { minX, maxX, minY, maxY };
}

/**
 * Test if a point is inside bounds
 */
export function isPointInBounds(point: Point, bounds: Bounds): boolean {
  return (
    point.x >= bounds.minX &&
    point.x <= bounds.maxX &&
    point.y >= bounds.minY &&
    point.y <= bounds.maxY
  );
}

/**
 * Test if two bounds overlap
 */
export function boundsOverlap(bounds1: Bounds, bounds2: Bounds): boolean {
  return !(
    bounds1.maxX < bounds2.minX ||
    bounds1.minX > bounds2.maxX ||
    bounds1.maxY < bounds2.minY ||
    bounds1.minY > bounds2.maxY
  );
}

class QuadtreeInternal<T> {
  private readonly bounds: Bounds;
  private readonly capacity: number = 4; // Max nodes per quadrant
  private nodes: QuadtreeNode<T>[] = [];
  private divided: boolean = false;

  private northeast?: QuadtreeInternal<T>;
  private northwest?: QuadtreeInternal<T>;
  private southeast?: QuadtreeInternal<T>;
  private southwest?: QuadtreeInternal<T>;

  constructor(bounds: Bounds) {
    this.bounds = bounds;
  }

  insert(node: QuadtreeNode<T>): boolean {
    // Check if node is in bounds
    if (!isPointInBounds(node.position, this.bounds)) {
      return false;
    }

    // If not divided yet
    if (!this.divided) {
      // Add to current node
      this.nodes.push(node);

      // Divide if we've exceeded capacity
      if (this.nodes.length > this.capacity) {
        this.subdivide();
      }

      return true;
    }

    // Otherwise, insert into appropriate quadrant
    return (
      this.northeast!.insert(node) ||
      this.northwest!.insert(node) ||
      this.southeast!.insert(node) ||
      this.southwest!.insert(node)
    );
  }

  private subdivide(): void {
    const x = (this.bounds.minX + this.bounds.maxX) / 2;
    const y = (this.bounds.minY + this.bounds.maxY) / 2;

    const ne = {
      minX: x,
      maxX: this.bounds.maxX,
      minY: y,
      maxY: this.bounds.maxY,
    };
    const nw = {
      minX: this.bounds.minX,
      maxX: x,
      minY: y,
      maxY: this.bounds.maxY,
    };
    const se = {
      minX: x,
      maxX: this.bounds.maxX,
      minY: this.bounds.minY,
      maxY: y,
    };
    const sw = {
      minX: this.bounds.minX,
      maxX: x,
      minY: this.bounds.minY,
      maxY: y,
    };

    this.northeast = new QuadtreeInternal(ne);
    this.northwest = new QuadtreeInternal(nw);
    this.southeast = new QuadtreeInternal(se);
    this.southwest = new QuadtreeInternal(sw);

    // Redistribute existing nodes
    const existingNodes = this.nodes;
    this.nodes = [];
    this.divided = true;

    for (const node of existingNodes) {
      this.northeast.insert(node) ||
        this.northwest.insert(node) ||
        this.southeast.insert(node) ||
        this.southwest.insert(node);
    }
  }

  query(bounds: Bounds): QuadtreeNode<T>[] {
    const result: QuadtreeNode<T>[] = [];

    // Check if search bounds overlap this node's bounds
    if (!boundsOverlap(bounds, this.bounds)) {
      return result;
    }

    // If not divided, return nodes that are in search bounds
    if (!this.divided) {
      for (const node of this.nodes) {
        if (isPointInBounds(node.position, bounds)) {
          result.push(node);
        }
      }
      return result;
    }

    // Otherwise, query all quadrants
    result.push(...this.northeast!.query(bounds));
    result.push(...this.northwest!.query(bounds));
    result.push(...this.southeast!.query(bounds));
    result.push(...this.southwest!.query(bounds));

    return result;
  }
}

/**
 * Spatial Quadtree - O(log n) spatial queries
 *
 * Provides efficient spatial indexing and querying for nodes.
 * Use for viewport culling and proximity queries.
 *
 * Complexity:
 * - insert: O(log n)
 * - query: O(log n + k) where k is number of results
 */
export class SpatialQuadtree<T> {
  private root: QuadtreeInternal<T>;

  constructor(nodes: QuadtreeNode<T>[]) {
    const bounds = calculateBounds(nodes);
    this.root = new QuadtreeInternal(bounds);

    for (const node of nodes) {
      this.root.insert(node);
    }
  }

  /**
   * Query nodes within bounds
   * Returns O(log n + k) where k is number of results
   */
  query(bounds: Bounds): QuadtreeNode<T>[] {
    return this.root.query(bounds);
  }
}
