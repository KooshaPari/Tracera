/**
 * Figma API Client
 *
 * Wrapper around figma-api for TracerTM design sync
 * Handles authentication, rate limiting, and common operations
 */

import * as Figma from 'figma-api';

export interface FigmaFile {
  name: string;
  lastModified: string;
  thumbnailUrl: string;
  version: string;
  document: Figma.Node;
  components: Record<string, Figma.Component>;
  styles: Record<string, Figma.Style>;
}

export interface Component {
  id: string;
  name: string;
  description: string;
  type: string;
  properties: Record<string, unknown>;
  styles: ComponentStyles;
}

export interface ComponentStyles {
  fills?: Figma.Paint[];
  strokes?: Figma.Paint[];
  effects?: Figma.Effect[];
  layoutMode?: 'NONE' | 'HORIZONTAL' | 'VERTICAL';
  primaryAxisSizingMode?: 'FIXED' | 'AUTO';
  counterAxisSizingMode?: 'FIXED' | 'AUTO';
  paddingLeft?: number;
  paddingRight?: number;
  paddingTop?: number;
  paddingBottom?: number;
  itemSpacing?: number;
}

export type ImageMap = Record<string, string>;

export interface Variables {
  colors: Record<string, string>;
  typography: Record<string, TypographyToken>;
  spacing: Record<string, number>;
  borderRadius: Record<string, number>;
  shadows: Record<string, string>;
}

export interface TypographyToken {
  fontFamily: string;
  fontSize: number;
  fontWeight: number;
  lineHeight: number;
  letterSpacing?: number;
}

export interface FigmaClientConfig {
  personalAccessToken: string;
  rateLimit?: {
    maxRequests: number;
    perMilliseconds: number;
  };
}

/**
 * TracerTM Figma API Client
 *
 * Provides type-safe access to Figma API with rate limiting and error handling
 */
export class FigmaClient {
  private api: Figma.Api;
  private rateLimiter: RateLimiter;

  constructor(config: FigmaClientConfig) {
    this.api = new Figma.Api({
      personalAccessToken: config.personalAccessToken,
    });

    this.rateLimiter = new RateLimiter(
      config.rateLimit?.maxRequests || 100,
      config.rateLimit?.perMilliseconds || 60_000,
    );
  }

  /**
   * Get complete file data including document tree
   */
  async getFile(fileKey: string): Promise<FigmaFile> {
    await this.rateLimiter.acquire();

    try {
      const file = await this.api.getFile(fileKey, {
        geometry: 'paths',
      });

      return {
        components: file.components || {},
        document: file.document,
        lastModified: file.lastModified,
        name: file.name,
        styles: file.styles || {},
        thumbnailUrl: file.thumbnailUrl,
        version: file.version,
      };
    } catch (error) {
      throw new FigmaAPIError(
        `Failed to fetch file ${fileKey}: ${error instanceof Error ? error.message : 'Unknown error'}`,
        error,
      );
    }
  }

  /**
   * Get all components from a file
   */
  async getComponents(fileKey: string): Promise<Component[]> {
    const file = await this.getFile(fileKey);
    const components: Component[] = [];

    this.traverseNode(file.document, (node) => {
      if (node.type === 'COMPONENT' || node.type === 'COMPONENT_SET') {
        components.push(this.nodeToComponent(node));
      }
    });

    return components;
  }

  /**
   * Export images for specific nodes
   */
  async exportImages(
    fileKey: string,
    nodeIds: string[],
    options: {
      format?: 'png' | 'jpg' | 'svg' | 'pdf';
      scale?: number;
    } = {},
  ): Promise<ImageMap> {
    await this.rateLimiter.acquire();

    try {
      const { format = 'png', scale = 2 } = options;

      const response = await this.api.getImage(fileKey, {
        format,
        ids: nodeIds,
        scale,
      });

      return response.images;
    } catch (error) {
      throw new FigmaAPIError(
        `Failed to export images: ${error instanceof Error ? error.message : 'Unknown error'}`,
        error,
      );
    }
  }

  /**
   * Extract design tokens/variables from file
   */
  async getVariables(fileKey: string): Promise<Variables> {
    const file = await this.getFile(fileKey);

    const variables: Variables = {
      borderRadius: {},
      colors: {},
      shadows: {},
      spacing: {},
      typography: {},
    };

    // Extract color styles
    for (const [_id, style] of Object.entries(file.styles)) {
      if (style.styleType === 'FILL') {
        const paint = style.fills?.[0];
        if (paint?.type === 'SOLID') {
          variables.colors[style.name] = this.rgbToHex(paint.color);
        }
      }
    }

    // Extract typography from text styles
    for (const [_id, style] of Object.entries(file.styles)) {
      if (style.styleType === 'TEXT') {
        variables.typography[style.name] = {
          fontFamily: style.fontFamily || 'Inter',
          fontSize: style.fontSize || 16,
          fontWeight: style.fontWeight || 400,
          letterSpacing: style.letterSpacing,
          lineHeight: style.lineHeightPx || style.fontSize || 16,
        };
      }
    }

    return variables;
  }

  /**
   * Get file version history
   */
  async getVersions(fileKey: string, limit = 10): Promise<Figma.Version[]> {
    await this.rateLimiter.acquire();

    try {
      const response = await this.api.getFileVersions(fileKey);
      return response.versions.slice(0, limit);
    } catch (error) {
      throw new FigmaAPIError(
        `Failed to get versions: ${error instanceof Error ? error.message : 'Unknown error'}`,
        error,
      );
    }
  }

  /**
   * Get comments from file
   */
  async getComments(fileKey: string): Promise<Figma.Comment[]> {
    await this.rateLimiter.acquire();

    try {
      const response = await this.api.getComments(fileKey);
      return response.comments;
    } catch (error) {
      throw new FigmaAPIError(
        `Failed to get comments: ${error instanceof Error ? error.message : 'Unknown error'}`,
        error,
      );
    }
  }

  // Helper methods

  private traverseNode(node: Figma.Node, callback: (node: Figma.Node) => void): void {
    callback(node);
    if ('children' in node && Array.isArray(node.children)) {
      for (const child of node.children) {
        this.traverseNode(child, callback);
      }
    }
  }

  private nodeToComponent(node: Figma.Node): Component {
    return {
      description: 'description' in node ? (node.description as string) || '' : '',
      id: node.id,
      name: node.name,
      properties: this.extractNodeProperties(node),
      styles: this.extractNodeStyles(node),
      type: node.type,
    };
  }

  private extractNodeProperties(node: Figma.Node): Record<string, unknown> {
    const props: Record<string, unknown> = {
      locked: 'locked' in node ? node.locked : false,
      visible: 'visible' in node ? node.visible : true,
    };

    if ('absoluteBoundingBox' in node) {
      props.boundingBox = node.absoluteBoundingBox;
    }

    if ('constraints' in node) {
      props.constraints = node.constraints;
    }

    return props;
  }

  private extractNodeStyles(node: Figma.Node): ComponentStyles {
    const styles: ComponentStyles = {};

    if ('fills' in node) {
      styles.fills = node.fills as Figma.Paint[];
    }

    if ('strokes' in node) {
      styles.strokes = node.strokes as Figma.Paint[];
    }

    if ('effects' in node) {
      styles.effects = node.effects as Figma.Effect[];
    }

    if ('layoutMode' in node) {
      styles.layoutMode = node.layoutMode as 'NONE' | 'HORIZONTAL' | 'VERTICAL';
      styles.primaryAxisSizingMode = node.primaryAxisSizingMode as 'FIXED' | 'AUTO';
      styles.counterAxisSizingMode = node.counterAxisSizingMode as 'FIXED' | 'AUTO';

      if ('paddingLeft' in node) {
        styles.paddingLeft = node.paddingLeft as number;
      }
      if ('paddingRight' in node) {
        styles.paddingRight = node.paddingRight as number;
      }
      if ('paddingTop' in node) {
        styles.paddingTop = node.paddingTop as number;
      }
      if ('paddingBottom' in node) {
        styles.paddingBottom = node.paddingBottom as number;
      }
      if ('itemSpacing' in node) {
        styles.itemSpacing = node.itemSpacing as number;
      }
    }

    return styles;
  }

  private rgbToHex(color: Figma.Color): string {
    const r = Math.round(color.r * 255);
    const g = Math.round(color.g * 255);
    const b = Math.round(color.b * 255);
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  }
}

/**
 * Simple token bucket rate limiter
 */
class RateLimiter {
  private tokens: number;
  private lastRefill: number;
  private maxTokens: number;
  private refillRate: number;

  constructor(maxRequests: number, perMilliseconds: number) {
    this.maxTokens = maxRequests;
    this.tokens = maxRequests;
    this.lastRefill = Date.now();
    this.refillRate = perMilliseconds / maxRequests;
  }

  async acquire(): Promise<void> {
    this.refill();

    if (this.tokens < 1) {
      const waitTime = this.refillRate;
      await new Promise((resolve) => setTimeout(resolve, waitTime));
      this.refill();
    }

    this.tokens -= 1;
  }

  private refill(): void {
    const now = Date.now();
    const timePassed = now - this.lastRefill;
    const tokensToAdd = Math.floor(timePassed / this.refillRate);

    if (tokensToAdd > 0) {
      this.tokens = Math.min(this.maxTokens, this.tokens + tokensToAdd);
      this.lastRefill = now;
    }
  }
}

/**
 * Custom error for Figma API operations
 */
export class FigmaAPIError extends Error {
  constructor(
    message: string,
    public cause?: unknown,
  ) {
    super(message);
    this.name = 'FigmaAPIError';
  }
}

/**
 * Create a Figma client instance
 */
export function createFigmaClient(config: FigmaClientConfig): FigmaClient {
  return new FigmaClient(config);
}
