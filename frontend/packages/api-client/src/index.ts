import type {
  ConfidenceRequest,
  ConfidenceResponse,
  CoverageMatrixRequest,
  CoverageMatrixResponse,
  EvidenceCreate,
  EvidenceResponse,
  GovernanceCheckRequest,
  GovernanceReport,
  ImpactRequest,
  ImpactResponse,
  TraceLinkInput,
} from '@tracertm/types';

export type {
  ConfidenceRequest,
  ConfidenceResponse,
  CoverageMatrixRequest,
  CoverageMatrixResponse,
  EvidenceCreate,
  EvidenceResponse,
  GovernanceCheckRequest,
  GovernanceReport,
  ImpactRequest,
  ImpactResponse,
  TraceLinkInput,
};

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

  /** POST /api/v1/impact */
  async analyzeImpact(request: ImpactRequest): Promise<ImpactResponse> {
    return this.postJson<ImpactResponse>(
      '/api/v1/impact',
      request,
      'impact',
    );
  }

  /** POST /api/v1/governance/spec-check */
  async specCheck(
    request: GovernanceCheckRequest = {},
  ): Promise<GovernanceReport> {
    return this.postJson<GovernanceReport>(
      '/api/v1/governance/spec-check',
      request,
      'spec-check',
    );
  }

  /** POST /api/v1/confidence */
  async computeConfidence(
    request: ConfidenceRequest,
  ): Promise<ConfidenceResponse> {
    return this.postJson<ConfidenceResponse>(
      '/api/v1/confidence',
      request,
      'confidence',
    );
  }

  /** GET /api/v1/evidence */
  async listEvidence(): Promise<EvidenceResponse[]> {
    const response = await this.fetchImpl(`${this.baseUrl}/api/v1/evidence`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) {
      throw new Error(`evidence failed (${response.status})`);
    }
    return (await response.json()) as EvidenceResponse[];
  }

  /** POST /api/v1/evidence */
  async createEvidence(payload: EvidenceCreate): Promise<EvidenceResponse> {
    return this.postJson<EvidenceResponse>(
      '/api/v1/evidence',
      payload,
      'evidence',
    );
  }

  private async postJson<T>(
    path: string,
    body: unknown,
    label: string,
  ): Promise<T> {
    const response = await this.fetchImpl(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error(`${label} failed (${response.status})`);
    }
    return (await response.json()) as T;
  }
}

export function createTraceraApiClient(baseUrl: string): TraceraApiClient {
  return new TraceraApiClient({ baseUrl });
}

/**
 * Standalone typed wrapper for POST /api/v1/coverage-matrix.
 * Mirrors `CoverageMatrixRequest` / `CoverageMatrixResponse` from `@tracertm/types`
 * (derived from the FastAPI router at `src/tracertm/api/routers/traceability.py`).
 */
export async function fetchCoverageMatrix(
  baseUrl: string,
  request: CoverageMatrixRequest = {},
  fetchImpl: typeof fetch = fetch,
): Promise<CoverageMatrixResponse> {
  const url = `${baseUrl.replace(/\/$/, '')}/api/v1/coverage-matrix`;
  const response = await fetchImpl(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`coverage-matrix failed (${response.status})`);
  }
  return (await response.json()) as CoverageMatrixResponse;
}
