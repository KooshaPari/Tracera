import { useEffect, useState } from 'react'
import { traceraClient } from '../services/traceraClient'
import './Dashboard.css'

function TraceViewer() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [items, setItems] = useState([])
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    let stopped = false
    const controller = new AbortController()

    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const evidence = await traceraClient.getEvidence({ signal: controller.signal })
        if (!stopped) {
          setItems(evidence.items || [])
        }
      } catch (err) {
        if (!stopped) {
          setError(err?.message || 'Unable to load evidence')
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
      controller.abort()
    }
  }, [refreshKey])

  return (
    <main className="dashboard-main">
      <div className="container">
        <section className="data-section">
          <h2>Evidence Trace Viewer</h2>
          {loading && <p role="status" aria-live="polite">Loading evidence...</p>}
          {error && <div className="error-banner" role="alert"><strong>Error:</strong> {error} <button type="button" className="retry-button" onClick={() => setRefreshKey((key) => key + 1)}>Retry</button></div>}
          {!loading && !error && !items.length && <p>No evidence items available.</p>}
          <ul className="sprints-list">
            {items.map((item, index) => (
              <li className="sprint-card" key={item.id || `${item.type || 'item'}-${index}`}>
                <div className="sprint-header">
                  <h3>{item.kind || item.type || 'evidence'}</h3>
                  <span className="sprint-status unknown">{item.id || 'local-id'}</span>
                </div>
                <p className="sprint-goal">{item.summary || item.note || item.description || 'No detail provided'}</p>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </main>
  )
}

export default TraceViewer
