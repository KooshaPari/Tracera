const DEFAULT_API_BASE =
  (typeof import.meta !== 'undefined' &&
    import.meta.env &&
    import.meta.env.VITE_API_BASE) ||
  'http://localhost:8080'

export const DEFAULT_REQUEST_TIMEOUT_MS = 15_000

async function parseJson(response) {
  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) {
    return {}
  }
  return response.json()
}

async function parseResponse(response, defaultValue) {
  if (!response.ok) {
    const body = await parseJson(response)
    throw new Error(
      `HTTP ${response.status} ${response.statusText} ${body?.error || ''}`.trim(),
    )
  }
  const payload = await parseJson(response)
  if (payload == null) {
    return defaultValue
  }

  if (
    payload &&
    typeof payload === 'object' &&
    !Array.isArray(payload) &&
    defaultValue &&
    typeof defaultValue === 'object' &&
    Object.keys(payload).length === 0
  ) {
    return defaultValue
  }

  return payload
}

async function safeRequest(url, options = {}) {
  const { timeoutMs = DEFAULT_REQUEST_TIMEOUT_MS, signal: externalSignal, ...fetchOptions } = options
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), timeoutMs)
  const abortExternal = () => controller.abort(externalSignal.reason)
  externalSignal?.addEventListener('abort', abortExternal, { once: true })
  try {
    const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(fetchOptions.headers || {}),
    },
      ...fetchOptions,
      signal: controller.signal,
    })
    return response
  } catch (error) {
    if (controller.signal.aborted) {
      const timeoutMessage = `Request timed out after ${timeoutMs}ms`
      throw new Error(externalSignal?.aborted ? 'Request aborted' : timeoutMessage, { cause: error })
    }
    throw error
  } finally {
    clearTimeout(timeout)
    externalSignal?.removeEventListener('abort', abortExternal)
  }
}

export const traceraClient = {
  async getHealth(options) {
    const response = await safeRequest(`${DEFAULT_API_BASE}/health`, options)
    return parseResponse(response, { status: 'unknown' })
  },

  async getSprints(options) {
    const response = await safeRequest(`${DEFAULT_API_BASE}/sdlc-pm/sprints`, options)
    return parseResponse(response, [])
  },

  async getTeams(options) {
    const response = await safeRequest(`${DEFAULT_API_BASE}/org-intel/teams`, options)
    return parseResponse(response, [])
  },

  async getMetrics(options) {
    const response = await safeRequest(`${DEFAULT_API_BASE}/org-intel/metrics`, options)
    return parseResponse(response, {
      total_artifacts: 0,
      coverage_ratio: 0,
      open_gaps: 0,
    })
  },

  async getEvidence(options) {
    const response = await safeRequest(`${DEFAULT_API_BASE}/evidence`, options)
    const payload = await parseResponse(response, { count: 0, items: [] })
    return {
      count: payload.count ?? (Array.isArray(payload) ? payload.length : 0),
      items: Array.isArray(payload?.items) ? payload.items : [],
    }
  },

  async postCoverageMatrix(payload = { links: [], stale_after_days: 7 }) {
    const response = await safeRequest(`${DEFAULT_API_BASE}/api/v1/coverage-matrix`, {
      method: 'POST',
      body: JSON.stringify({
        links: payload.links || [],
        stale_after_days: payload.stale_after_days ?? 7,
      }),
    })
    return parseResponse(response, {
      generated_at: new Date().toISOString(),
      link_count: 0,
      cell_count: 0,
      stale_links: 0,
      cells: [],
    })
  },

  async postImpact(payload = { links: [], changed_artifact_ids: [], max_depth: 3 }) {
    const response = await safeRequest(`${DEFAULT_API_BASE}/api/v1/impact`, {
      method: 'POST',
      body: JSON.stringify({
        links: payload.links || [],
        changed_artifact_ids: payload.changed_artifact_ids || [],
        max_depth: payload.max_depth ?? 3,
      }),
    })
    return parseResponse(response, {
      seeds: [],
      affected: [],
      total_score: 0,
      truncated: false,
      max_depth_seen: 0,
      conflicts: [],
    })
  },

  async postConfidence(payload = { requirement_text: '', artifact_text: '' }) {
    const response = await safeRequest(`${DEFAULT_API_BASE}/api/v1/confidence`, {
      method: 'POST',
      body: JSON.stringify({
        requirement_text: payload.requirement_text || '',
        artifact_text: payload.artifact_text || '',
      }),
    })
    return parseResponse(response, {
      confidence: 0,
      rationale: 'No confidence available',
    })
  },

  async postSpecCheck(payload = { specs: [], traces: [] }) {
    const response = await safeRequest(`${DEFAULT_API_BASE}/api/v1/governance/spec-check`, {
      method: 'POST',
      body: JSON.stringify({
        specs: payload.specs || [],
        traces: payload.traces || [],
      }),
    })
    return parseResponse(response, {
      status: 'pass',
      spec_count: 0,
      trace_count: 0,
      violations: [],
    })
  },

  async postBlastRadius(payload = { links: [], changed_artifact_ids: [] }) {
    const response = await safeRequest(`${DEFAULT_API_BASE}/api/v1/blast-radius`, {
      method: 'POST',
      body: JSON.stringify({
        links: payload.links || [],
        changed_artifact_ids: payload.changed_artifact_ids || [],
      }),
    })
    return parseResponse(response, {
      seeds: [],
      blast_radius: [],
      total: 0,
    })
  },

  async postTraceForward(artifactId, payload = { links: [] }) {
    const response = await safeRequest(
      `${DEFAULT_API_BASE}/api/v1/trace/forward/${encodeURIComponent(String(artifactId))}`,
      {
        method: 'POST',
        body: JSON.stringify({
          links: payload.links || [],
        }),
      },
    )
    return parseResponse(response, {
      artifact_id: artifactId,
      direction: 'forward',
      neighbors: [],
    })
  },

  async postTraceReverse(artifactId, payload = { links: [] }) {
    const response = await safeRequest(
      `${DEFAULT_API_BASE}/api/v1/trace/reverse/${encodeURIComponent(String(artifactId))}`,
      {
        method: 'POST',
        body: JSON.stringify({
          links: payload.links || [],
        }),
      },
    )
    return parseResponse(response, {
      artifact_id: artifactId,
      direction: 'reverse',
      neighbors: [],
    })
  },
}
