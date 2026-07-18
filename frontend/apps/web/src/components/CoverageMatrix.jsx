import { useEffect, useState } from 'react'
import { traceraClient } from '../services/traceraClient'
import './Dashboard.css'

function CoverageMatrix() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [metrics, setMetrics] = useState(null)

  useEffect(() => {
    let stopped = false

    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const nextMetrics = await traceraClient.getMetrics()
        if (!stopped) {
          setMetrics(nextMetrics)
        }
      } catch (err) {
        if (!stopped) {
          setError(err?.message || 'Unable to load metrics')
        }
      } finally {
        if (!stopped) {
          setLoading(false)
        }
      }
    }

    load()
    return () => {
      stopped = true
    }
  }, [])

  const coverageRatio = Number(metrics?.coverage_ratio)
  const displayCoverageRatio = Number.isFinite(coverageRatio) ? `${(coverageRatio * 100).toFixed(1)}%` : '0.0%'

  return (
    <main className="dashboard-main">
      <div className="container">
        <section className="data-section">
          <h2>Coverage Matrix (Runtime)</h2>
          {loading && <p>Loading coverage metrics...</p>}
          {error && <div className="error-banner"><strong>Error:</strong> {error}</div>}
          {metrics ? (
            <div className="sprints-list">
              <div className="sprint-card">
                <div className="sprint-header">
                  <h3>Coverage Ratio</h3>
                </div>
                <p className="sprint-goal">{displayCoverageRatio}</p>
              </div>
              <div className="sprint-card">
                <div className="sprint-header">
                  <h3>Open Gaps</h3>
                </div>
                <p className="sprint-goal">{metrics?.open_gaps ?? 0}</p>
              </div>
              <div className="sprint-card">
                <div className="sprint-header">
                  <h3>Total Artifacts</h3>
                </div>
                <p className="sprint-goal">{metrics?.total_artifacts ?? 0}</p>
              </div>
            </div>
          ) : (
            <p>No coverage metrics available.</p>
          )}
        </section>
      </div>
    </main>
  )
}

export default CoverageMatrix
