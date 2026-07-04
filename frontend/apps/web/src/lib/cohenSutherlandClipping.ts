/**
 * Cohen-Sutherland Line Clipping Algorithm
 *
 * Efficient line segment vs rectangle intersection detection.
 * Used for edge viewport culling with partial visibility support.
 *
 * Performance:
 * - O(1) rejection for fully outside edges (90%+ of cases)
 * - O(1) acceptance for fully inside edges
 * - O(1) clipping for partially visible edges
 *
 * Algorithm:
 * 1. Compute outcodes for both endpoints
 * 2. If both outcodes are 0 → fully inside (trivial accept)
 * 3. If outcodes have common bit → fully outside (trivial reject)
 * 4. Otherwise → clip against rectangle edges
 *
 * Outcodes (bitfield):
 * - Bit 0 (LEFT): x < minX
 * - Bit 1 (RIGHT): x > maxX
 * - Bit 2 (BOTTOM): y < minY
 * - Bit 3 (TOP): y > maxY
 */

export interface Point {
  x: number;
  y: number;
}

export interface Rectangle {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
}

export interface LineSegment {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface ClipResult {
  /** True if line intersects rectangle */
  intersects: boolean;
  /** True if line is fully inside rectangle */
  fullyInside: boolean;
  /** True if line is partially visible (clipped) */
  partiallyVisible: boolean;
  /** Clipped line segment (if intersects=true) */
  clipped?: LineSegment;
  /** Visibility ratio: 0.0 = fully outside, 1.0 = fully inside */
  visibilityRatio: number;
}

// Outcode bits
const INSIDE = 0; // 0000
const LEFT = 1; // 0001
const RIGHT = 2; // 0010
const BOTTOM = 4; // 0100
const TOP = 8; // 1000

/**
 * Compute outcode for a point
 * Returns bitfield indicating which region the point is in
 */
function computeOutcode(x: number, y: number, rect: Rectangle): number {
  let code = INSIDE;

  if (x < rect.minX) {
    code |= LEFT;
  } else if (x > rect.maxX) {
    code |= RIGHT;
  }

  if (y < rect.minY) {
    code |= BOTTOM;
  } else if (y > rect.maxY) {
    code |= TOP;
  }

  return code;
}

/**
 * Cohen-Sutherland line clipping
 *
 * Clips a line segment against a rectangle.
 * Returns clipped segment and visibility information.
 *
 * @param line - Line segment to clip
 * @param rect - Clipping rectangle
 * @returns Clip result with intersection info
 */
export function clipLineCohenSutherland(line: LineSegment, rect: Rectangle): ClipResult {
  let x1 = line.x1;
  let y1 = line.y1;
  let x2 = line.x2;
  let y2 = line.y2;

  // Original line length (for visibility ratio)
  const originalLength = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);

  let outcode1 = computeOutcode(x1, y1, rect);
  let outcode2 = computeOutcode(x2, y2, rect);

  let accept = false;
  let clipped = false;

  // Track original outcodes to determine if line was clipped
  const origOutcode1 = outcode1;
  const origOutcode2 = outcode2;

  while (true) {
    if ((outcode1 | outcode2) === 0) {
      // Trivial accept: both points inside
      accept = true;
      break;
    } else if ((outcode1 & outcode2) !== 0) {
      // Trivial reject: both points in same outside region
      break;
    } else {
      // Line crosses boundary - clip it
      let x = 0;
      let y = 0;

      // Pick the point that is outside
      const outcodeOut = outcode1 !== 0 ? outcode1 : outcode2;

      // Find intersection point using line equation y = y1 + slope * (x - x1)
      if ((outcodeOut & TOP) !== 0) {
        // Point is above rectangle
        x = x1 + ((x2 - x1) * (rect.maxY - y1)) / (y2 - y1);
        y = rect.maxY;
      } else if ((outcodeOut & BOTTOM) !== 0) {
        // Point is below rectangle
        x = x1 + ((x2 - x1) * (rect.minY - y1)) / (y2 - y1);
        y = rect.minY;
      } else if ((outcodeOut & RIGHT) !== 0) {
        // Point is to the right
        y = y1 + ((y2 - y1) * (rect.maxX - x1)) / (x2 - x1);
        x = rect.maxX;
      } else if ((outcodeOut & LEFT) !== 0) {
        // Point is to the left
        y = y1 + ((y2 - y1) * (rect.minX - x1)) / (x2 - x1);
        x = rect.minX;
      }

      // Replace the outside point with the intersection point
      if (outcodeOut === outcode1) {
        x1 = x;
        y1 = y;
        outcode1 = computeOutcode(x1, y1, rect);
      } else {
        x2 = x;
        y2 = y;
        outcode2 = computeOutcode(x2, y2, rect);
      }

      clipped = true;
    }
  }

  if (!accept) {
    return {
      intersects: false,
      fullyInside: false,
      partiallyVisible: false,
      visibilityRatio: 0.0,
    };
  }

  // Determine if line was fully inside or clipped
  const fullyInside = origOutcode1 === INSIDE && origOutcode2 === INSIDE;
  const partiallyVisible = clipped || !fullyInside;

  // Calculate visibility ratio
  const clippedLength = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
  const visibilityRatio = originalLength > 0 ? clippedLength / originalLength : 1.0;

  return {
    intersects: true,
    fullyInside,
    partiallyVisible,
    clipped: { x1, y1, x2, y2 },
    visibilityRatio,
  };
}

/**
 * Fast rejection test without clipping
 *
 * Returns true if line MIGHT intersect rectangle.
 * Returns false if line is DEFINITELY outside.
 *
 * Faster than full clipping when you only need yes/no.
 *
 * @param line - Line segment to test
 * @param rect - Test rectangle
 * @returns True if line might intersect
 */
export function lineIntersectsRectFast(line: LineSegment, rect: Rectangle): boolean {
  const outcode1 = computeOutcode(line.x1, line.y1, rect);
  const outcode2 = computeOutcode(line.x2, line.y2, rect);

  // Trivial reject
  if ((outcode1 & outcode2) !== 0) {
    return false;
  }

  // Trivial accept or needs clipping
  return true;
}

/**
 * Calculate edge visibility score
 *
 * Returns a normalized score [0, 1] indicating how visible an edge is:
 * - 1.0: Fully inside viewport
 * - 0.5-0.9: Partially visible
 * - 0.0: Fully outside viewport
 *
 * Uses Cohen-Sutherland clipping for accurate calculation.
 *
 * @param sourceX - Source node X
 * @param sourceY - Source node Y
 * @param targetX - Target node X
 * @param targetY - Target node Y
 * @param viewport - Viewport rectangle
 * @returns Visibility score [0, 1]
 */
export function calculateEdgeVisibility(
  sourceX: number,
  sourceY: number,
  targetX: number,
  targetY: number,
  viewport: Rectangle,
): number {
  const line: LineSegment = {
    x1: sourceX,
    y1: sourceY,
    x2: targetX,
    y2: targetY,
  };

  const result = clipLineCohenSutherland(line, viewport);
  return result.visibilityRatio;
}

/**
 * Batch visibility test for multiple edges
 *
 * More efficient than calling clipLineCohenSutherland repeatedly.
 * Uses early rejection for fully outside edges.
 *
 * @param edges - Array of line segments
 * @param viewport - Viewport rectangle
 * @returns Array of visibility ratios [0, 1]
 */
export function batchEdgeVisibility(edges: LineSegment[], viewport: Rectangle): number[] {
  return edges.map((edge) => {
    // Fast rejection first
    if (!lineIntersectsRectFast(edge, viewport)) {
      return 0.0;
    }

    // Full clipping for potentially visible edges
    const result = clipLineCohenSutherland(edge, viewport);
    return result.visibilityRatio;
  });
}

/**
 * Statistics for culling performance analysis
 */
export interface CullingStats {
  totalEdges: number;
  fullyInside: number;
  partiallyVisible: number;
  fullyOutside: number;
  cullingAccuracy: number;
}

/**
 * Analyze culling performance
 *
 * Computes statistics about edge visibility for performance tuning.
 *
 * @param edges - Array of line segments
 * @param viewport - Viewport rectangle
 * @returns Culling statistics
 */
export function analyzeCullingPerformance(edges: LineSegment[], viewport: Rectangle): CullingStats {
  let fullyInside = 0;
  let partiallyVisible = 0;
  let fullyOutside = 0;

  for (const edge of edges) {
    const result = clipLineCohenSutherland(edge, viewport);

    if (!result.intersects) {
      fullyOutside++;
    } else if (result.fullyInside) {
      fullyInside++;
    } else {
      partiallyVisible++;
    }
  }

  return {
    totalEdges: edges.length,
    fullyInside,
    partiallyVisible,
    fullyOutside,
    cullingAccuracy: fullyOutside / edges.length,
  };
}
