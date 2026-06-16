import type {
  CoverageMatrixRequest,
  CoverageMatrixResponse,
  TraceLinkInput,
} from '@tracertm/types';

export type { CoverageMatrixRequest, CoverageMatrixResponse, TraceLinkInput };

export interface TraceraApiClientOptions {
  baseUrl: string;
  fetchImpl?: typeof fetch;
}

/** Minimal Tracera REST client for traceability endpoints. */
export class TraceraApiClient {
  private readonly baseUrl: string;
  private readonly fetchImpl: typeof fetch;

  constructor(options: TraceraApiClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/$/, '');
    this.fetchImpl = options.fetchImpl ?? fetch;
  }

  /** Round-trip one trace link through POST /api/v1/coverage-matrix. */
  async roundTripTraceLink(link: TraceLinkInput): Promise<CoverageMatrixResponse> {
    return this.buildCoverageMatrix({ links: [link] });
  }

  async buildCoverageMatrix(
    request: CoverageMatrixRequest = {},
  ): Promise<CoverageMatrixResponse> {
    const response = await this.fetchImpl(`${this.baseUrl}/api/v1/coverage-matrix`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`coverage-matrix failed (${response.status})`);
    }
    return (await response.json()) as CoverageMatrixResponse;
  }
}

export function createTraceraApiClient(baseUrl: string): TraceraApiClient {
  return new TraceraApiClient({ baseUrl });
}
