/**
 * IncrementalGraphBuilder - Builds graph incrementally from streaming data
 *
 * Features:
 * - NDJSON stream parsing
 * - Incremental node/edge addition
 * - Progress tracking
 * - Predictive prefetch
 * - Memory-efficient batching
 */

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  position: { x: number; y: number };
  data: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  sourceId: string;
  targetId: string;
  type: string;
  label: string;
}

export interface StreamChunk {
  type: 'metadata' | 'node' | 'edge' | 'progress' | 'complete' | 'error';
  data: any;
  progress?: ProgressInfo | undefined;
  timestamp: number;
}

export interface ProgressInfo {
  current: number;
  total: number;
  percentage: number;
  stage: 'nodes' | 'edges' | 'complete';
}

export interface StreamMetadata {
  projectId: string;
  totalNodes: number;
  totalEdges: number;
  viewport: ViewportBounds;
  estimatedTime: number;
  chunkSize: number;
}

export interface ViewportBounds {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
}

export interface GraphBuildResult {
  nodes: Map<string, GraphNode>;
  edges: Map<string, GraphEdge>;
  metadata?: StreamMetadata | undefined;
}

export interface BuildOptions {
  onProgress?: ((info: ProgressInfo) => void) | undefined;
  onNode?: ((node: GraphNode) => void) | undefined;
  onEdge?: ((edge: GraphEdge) => void) | undefined;
  onComplete?: ((result: GraphBuildResult) => void) | undefined;
  onError?: ((error: Error) => void) | undefined;
  batchSize?: number | undefined; // Batch render updates
  batchDelay?: number | undefined; // ms between batch renders
}

export class IncrementalGraphBuilder {
  private nodes: Map<string, GraphNode> = new Map();
  private edges: Map<string, GraphEdge> = new Map();
  private metadata?: StreamMetadata | undefined;
  private options: BuildOptions;

  private nodeBatch: GraphNode[] = [];
  private edgeBatch: GraphEdge[] = [];
  private batchTimer?: ReturnType<typeof setTimeout> | undefined;

  private abortController?: AbortController;
  private isComplete = false;

  constructor(options: BuildOptions = {}) {
    this.options = {
      batchSize: 10,
      batchDelay: 16, // ~60fps
      ...options,
    };
  }

  /**
   * Reset builder state for new graph
   */
  reset(): void {
    this.nodes.clear();
    this.edges.clear();
    this.metadata = undefined;
    this.nodeBatch = [];
    this.edgeBatch = [];
    this.isComplete = false;

    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = undefined;
    }
  }

  /**
   * Add a single node to the graph
   */
  addNode(node: GraphNode): void {
    this.nodes.set(node.id, node);
    this.nodeBatch.push(node);

    this.scheduleBatchFlush();
  }

  /**
   * Add a single edge to the graph
   */
  addEdge(edge: GraphEdge): void {
    this.edges.set(edge.id, edge);
    this.edgeBatch.push(edge);

    this.scheduleBatchFlush();
  }

  /**
   * Schedule batch flush with debouncing
   */
  private scheduleBatchFlush(): void {
    const shouldFlush =
      this.nodeBatch.length >= (this.options.batchSize || 10) ||
      this.edgeBatch.length >= (this.options.batchSize || 10);

    if (shouldFlush) {
      this.flushBatch();
    } else if (!this.batchTimer) {
      this.batchTimer = setTimeout(() => {
        this.flushBatch();
      }, this.options.batchDelay || 16);
    }
  }

  /**
   * Flush pending batch updates
   */
  private flushBatch(): void {
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = undefined;
    }

    // Notify callbacks
    if (this.options.onNode && this.nodeBatch.length > 0) {
      this.nodeBatch.forEach((node) => this.options.onNode?.(node));
      this.nodeBatch = [];
    }

    if (this.options.onEdge && this.edgeBatch.length > 0) {
      this.edgeBatch.forEach((edge) => this.options.onEdge?.(edge));
      this.edgeBatch = [];
    }
  }

  /**
   * Process a stream chunk
   */
  processChunk(chunk: StreamChunk): void {
    switch (chunk.type) {
      case 'metadata':
        this.metadata = chunk.data as StreamMetadata;
        break;

      case 'node':
        this.addNode(chunk.data as GraphNode);
        if (chunk.progress) {
          this.options.onProgress?.(chunk.progress);
        }
        break;

      case 'edge':
        this.addEdge(chunk.data as GraphEdge);
        if (chunk.progress) {
          this.options.onProgress?.(chunk.progress);
        }
        break;

      case 'progress':
        if (chunk.progress) {
          this.options.onProgress?.(chunk.progress);
        }
        break;

      case 'complete':
        this.flushBatch();
        this.isComplete = true;
        this.options.onComplete?.(this.getResult());
        break;

      case 'error':
        this.options.onError?.(new Error(chunk.data.error || 'Stream error'));
        break;
    }
  }

  /**
   * Get current graph state
   */
  getResult(): GraphBuildResult {
    return {
      nodes: new Map(this.nodes),
      edges: new Map(this.edges),
      metadata: this.metadata,
    };
  }

  /**
   * Get graph statistics
   */
  getStats() {
    return {
      nodeCount: this.nodes.size,
      edgeCount: this.edges.size,
      isComplete: this.isComplete,
      metadata: this.metadata,
    };
  }

  /**
   * Load graph from streaming endpoint
   */
  async loadFromStream(
    url: string,
    viewportRequest: any,
    options: RequestInit = {},
  ): Promise<GraphBuildResult> {
    this.reset();
    this.abortController = new AbortController();

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        body: JSON.stringify(viewportRequest),
        signal: this.abortController.signal,
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      // Parse NDJSON stream
      await this.parseNDJSONStream(response.body);

      return this.getResult();
    } catch (err) {
      if (err instanceof Error) {
        this.options.onError?.(err);
      }
      throw err;
    }
  }

  /**
   * Parse NDJSON stream from ReadableStream
   */
  private async parseNDJSONStream(stream: ReadableStream<Uint8Array>): Promise<void> {
    const reader = stream.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        // Append to buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete lines
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line

        for (const line of lines) {
          if (line.trim()) {
            try {
              const chunk = JSON.parse(line) as StreamChunk;
              this.processChunk(chunk);
            } catch (err) {
              console.error('Failed to parse chunk:', err, line);
            }
          }
        }
      }

      // Process remaining buffer
      if (buffer.trim()) {
        try {
          const chunk = JSON.parse(buffer) as StreamChunk;
          this.processChunk(chunk);
        } catch (err) {
          console.error('Failed to parse final chunk:', err);
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Cancel ongoing stream
   */
  abort(): void {
    this.abortController?.abort();
    this.flushBatch();
  }

  /**
   * Check if a node exists
   */
  hasNode(id: string): boolean {
    return this.nodes.has(id);
  }

  /**
   * Check if an edge exists
   */
  hasEdge(id: string): boolean {
    return this.edges.has(id);
  }

  /**
   * Get a specific node
   */
  getNode(id: string): GraphNode | undefined {
    return this.nodes.get(id);
  }

  /**
   * Get a specific edge
   */
  getEdge(id: string): GraphEdge | undefined {
    return this.edges.get(id);
  }

  /**
   * Get all nodes as array
   */
  getNodes(): GraphNode[] {
    return Array.from(this.nodes.values());
  }

  /**
   * Get all edges as array
   */
  getEdges(): GraphEdge[] {
    return Array.from(this.edges.values());
  }
}

/**
 * Parse NDJSON stream utility
 */
export async function* parseNDJSON<T = any>(response: Response): AsyncGenerator<T, void, unknown> {
  if (!response.body) {
    throw new Error('Response body is null');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.trim()) {
          try {
            yield JSON.parse(line) as T;
          } catch (err) {
            console.error('Failed to parse NDJSON line:', err, line);
          }
        }
      }
    }

    if (buffer.trim()) {
      try {
        yield JSON.parse(buffer) as T;
      } catch (err) {
        console.error('Failed to parse final NDJSON:', err);
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Estimate stream completion time
 */
export function estimateStreamTime(metadata: StreamMetadata): number {
  return metadata.estimatedTime || 0;
}

/**
 * Format progress for display
 */
export function formatProgress(progress: ProgressInfo): string {
  const pct = Math.round(progress.percentage);
  return `${progress.stage}: ${progress.current}/${progress.total} (${pct}%)`;
}
