import { useEffect, useRef, useState } from 'react'
import { traceraClient } from '../services/traceraClient'
import { isHealthOk, mergeDashboardFetchResults } from './dashboardState'
import './Dashboard.css'

const activeEndpoints = [
  '/health',
  '/readyz',
  '/sdlc-pm/sprints',
  '/org-intel/teams',
  '/org-intel/metrics',
  '/evidence',
]

function asDate(value) {
  if (!value) return '—'
  try {
    return new Date(value).toLocaleDateString()
  } catch {
    return String(value)
  }
}

function Dashboard() {
  const [health, setHealth] = useState(null)
  const [readiness, setReadiness] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sprints, setSprints] = useState([])
  const [teams, setTeams] = useState([])
  const [metrics, setMetrics] = useState(null)
  const [evidenceCount, setEvidenceCount] = useState(0)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    let stopped = false
    let inFlight = false
    const controller = new AbortController()

    const fetchData = async () => {
      if (stopped || inFlight || document.visibilityState === 'hidden') return
      inFlight = true
      setLoading(true)
      setError(null)

      try {
        const results = await Promise.allSettled([
          traceraClient.getHealth({ signal: controller.signal }),
          traceraClient.getReadiness({ signal: controller.signal }),
          traceraClient.getSprints({ signal: controller.signal }),
          traceraClient.getTeams({ signal: controller.signal }),
          traceraClient.getMetrics({ signal: controller.signal }),
          traceraClient.getEvidence({ signal: controller.signal }),
        ])
        const merged = mergeDashboardFetchResults(results)
        // Keep last-known-good values when one endpoint is temporarily unavailable.
        // The aggregated error remains visible so stale data is never mistaken for fresh data.
        setHealth((previous) => results[0].status === 'fulfilled' ? merged.health : previous)
        setReadiness((previous) => results[1].status === 'fulfilled' ? merged.readiness : previous)
        setSprints((previous) => results[2].status === 'fulfilled' ? merged.sprints : previous)
        setTeams((previous) => results[3].status === 'fulfilled' ? merged.teams : previous)
        setMetrics((previous) => results[4].status === 'fulfilled' ? merged.metrics : previous)
        setEvidenceCount((previous) => results[5].status === 'fulfilled' ? merged.evidenceCount : previous)
        setError(merged.error)
      } catch (err) {
        if (!stopped) {
          setError(err?.message || 'Unable to load dashboard data')
        }
      } finally {
        if (!stopped) {
          setLoading(false)
        }
        inFlight = false
      }
    }

    fetchData()
    const timer = setInterval(fetchData, 30000)
    const onVisibilityChange = () => {
      if (document.visibilityState === 'visible') fetchData()
    }
    document.addEventListener('visibilitychange', onVisibilityChange)
    return () => {
      stopped = true
      controller.abort()
      clearInterval(timer)
      document.removeEventListener('visibilitychange', onVisibilityChange)
    }
  }, [refreshKey])

  const activeSprints = sprints.filter((sprint) => sprint.status === 'active').length
  const isHealthy = isHealthOk(health)
  const isReady = readiness?.status === 'ready'
  const endpointListText = activeEndpoints.join(', ')
  const coverageRatio = Number(metrics?.coverage_ratio)
  const displayCoverageRatio = Number.isFinite(coverageRatio) ? (coverageRatio * 100).toFixed(1) : '0.0'

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Tracera</h1>
          <p className="subtitle">Traceability &amp; Evidence Platform</p>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="container">
          {loading && (
            <div className="loading" role="status" aria-live="polite">
              <div className="spinner"></div>
              <p>Loading data...</p>
            </div>
          )}

          {error && (
            <div className="error-banner" role="alert" aria-busy={loading}>
              <strong>Error:</strong> {error}
              <button
                type="button"
                className="retry-button"
                disabled={loading}
                onClick={() => setRefreshKey((key) => key + 1)}
              >
                {loading ? 'Retrying…' : 'Retry'}
              </button>
            </div>
          )}

          <section className="status-section">
            <h2>System Status</h2>
            <div className="status-grid">
              <div className="status-card">
                <div className="status-icon" aria-hidden="true">{isHealthy ? '✓' : '?'}</div>
                <div className="status-info">
                  <h3>Backend Health</h3>
                  <p className={isHealthy ? 'status-ok' : 'status-unknown'}>
                    {isHealthy ? 'Healthy' : 'Checking...'}
                  </p>
                </div>
              </div>

              <div className="status-card">
                <div className="status-icon" aria-hidden="true">{isReady ? '✓' : '?'}</div>
                <div className="status-info">
                  <h3>Backend Readiness</h3>
                  <p className={isReady ? 'status-ok' : 'status-unknown'}>
                    {isReady ? 'Ready' : 'Waiting...'}
                  </p>
                </div>
              </div>

              <div className="status-card">
                <div className="status-icon" aria-hidden="true">{teams.length}</div>
                <div className="status-info">
                  <h3>Teams</h3>
                  <p>{teams.length} team{teams.length !== 1 ? 's' : ''} registered</p>
                </div>
              </div>

              <div className="status-card">
                <div className="status-icon" aria-hidden="true">{sprints.length}</div>
                <div className="status-info">
                  <h3>Active Sprints</h3>
                  <p>{activeSprints} active / {sprints.length} total</p>
                </div>
              </div>

              <div className="status-card">
                <div className="status-icon" aria-hidden="true">{evidenceCount}</div>
                <div className="status-info">
                  <h3>Evidence Items</h3>
                  <p>{evidenceCount} available</p>
                </div>
              </div>
            </div>
          </section>

          {metrics ? (
            <section className="data-section">
              <h2>Org Metrics</h2>
              <div className="sprints-list">
                <div className="sprint-card">
                  <div className="sprint-header">
                    <h3>Total artifacts</h3>
                  </div>
                  <p className="sprint-goal">{metrics?.total_artifacts ?? 0}</p>
                </div>
                <div className="sprint-card">
                  <div className="sprint-header">
                    <h3>Coverage ratio</h3>
                  </div>
                  <p className="sprint-goal">{displayCoverageRatio}%</p>
                </div>
                <div className="sprint-card">
                  <div className="sprint-header">
                    <h3>Open gaps</h3>
                  </div>
                  <p className="sprint-goal">{metrics?.open_gaps ?? 0}</p>
                </div>
              </div>
            </section>
          ) : null}

          <section className="data-section">
            <h2>Teams</h2>
            {teams.length > 0 ? (
              <div className="teams-grid">
                {teams.map((team) => (
                  <div key={team.id} className="team-card">
                    <h3>{team.name}</h3>
                    <p>{team.description}</p>
                    <div className="team-meta">
                      <span className="team-id">{team.id}</span>
                      <span className="team-members">{(team.members?.length || 0)} members</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>No teams configured yet</p>
              </div>
            )}
          </section>

          <section className="data-section">
            <h2>Sprints</h2>
            {sprints.length > 0 ? (
              <div className="sprints-list">
                {sprints.map((sprint) => (
                  <div key={sprint.id} className="sprint-card">
                    <div className="sprint-header">
                      <h3>{sprint.name}</h3>
                      <span className={`sprint-status ${sprint.status || 'unknown'}`}>
                        {sprint.status || 'unknown'}
                      </span>
                    </div>
                    <p className="sprint-goal">{sprint.goal}</p>
                    <div className="sprint-dates">
                      <span>
                        {asDate(sprint.start_date)} - {asDate(sprint.end_date)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>No sprints configured yet</p>
              </div>
            )}
          </section>

          <section className="info-section">
            <h2>API Configuration</h2>
            <div className="info-card">
              <p>
                <strong>API Base:</strong> {import.meta.env.VITE_API_BASE || 'http://localhost:8080'}
              </p>
              <p className="api-note">Active backend endpoints: {endpointListText}</p>
            </div>
          </section>
        </div>
      </main>

      <footer className="dashboard-footer">
        <p>Tracera © 2024 - Traceability &amp; Governance Platform</p>
      </footer>
    </div>
  )
}

export default Dashboard
