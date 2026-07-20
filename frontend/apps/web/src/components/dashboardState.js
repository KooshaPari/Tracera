export const FALLBACK_ENDPOINT_ERROR_MESSAGES = {
  health: 'health check failed',
  readiness: 'readiness check failed',
  sprints: 'sprints load failed',
  teams: 'teams load failed',
  metrics: 'metrics load failed',
  evidence: 'evidence load failed',
}

const asNumber = (value) => {
  const num = Number(value)
  return Number.isFinite(num) ? num : 0
}

export const mergeDashboardFetchResults = (results) => {
  const [healthRes, readinessRes, sprintsRes, teamsRes, metricsRes, evidenceRes] = results
  const errors = []

  const health = healthRes.status === 'fulfilled' ? healthRes.value ?? { status: 'unknown' } : { status: 'unknown' }
  const readiness = readinessRes.status === 'fulfilled' ? readinessRes.value ?? { status: 'unknown' } : { status: 'unknown' }
  const sprints = sprintsRes.status === 'fulfilled' && Array.isArray(sprintsRes.value) ? sprintsRes.value : []
  const teams = teamsRes.status === 'fulfilled' && Array.isArray(teamsRes.value) ? teamsRes.value : []
  const metrics = metricsRes.status === 'fulfilled' ? metricsRes.value || null : null
  const evidenceCount = evidenceRes.status === 'fulfilled' ? asNumber(evidenceRes.value?.count) : 0

  if (healthRes.status !== 'fulfilled') {
    errors.push(healthRes.reason?.message || FALLBACK_ENDPOINT_ERROR_MESSAGES.health)
  }
  if (readinessRes.status !== 'fulfilled') {
    errors.push(readinessRes.reason?.message || FALLBACK_ENDPOINT_ERROR_MESSAGES.readiness)
  }
  if (sprintsRes.status !== 'fulfilled') {
    errors.push(sprintsRes.reason?.message || FALLBACK_ENDPOINT_ERROR_MESSAGES.sprints)
  }
  if (teamsRes.status !== 'fulfilled') {
    errors.push(teamsRes.reason?.message || FALLBACK_ENDPOINT_ERROR_MESSAGES.teams)
  }
  if (metricsRes.status !== 'fulfilled') {
    errors.push(metricsRes.reason?.message || FALLBACK_ENDPOINT_ERROR_MESSAGES.metrics)
  }
  if (evidenceRes.status !== 'fulfilled') {
    errors.push(evidenceRes.reason?.message || FALLBACK_ENDPOINT_ERROR_MESSAGES.evidence)
  }

  return {
    health,
    readiness,
    sprints,
    teams,
    metrics,
    evidenceCount,
    error: errors.length > 0 ? errors.join(' | ') : null,
  }
}

export const isHealthOk = (health) => health?.status === 'ok'
