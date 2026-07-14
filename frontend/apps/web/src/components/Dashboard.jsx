import { useState, useEffect } from 'react'
import { loadDashboardData, normalizeApiBase } from '../api.js'
import './Dashboard.css'

function Dashboard() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sprints, setSprints] = useState([])
  const [teams, setTeams] = useState([])
  const apiBase = normalizeApiBase(import.meta.env.VITE_API_BASE)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)

        const data = await loadDashboardData(apiBase)
        setHealth(data.health)
        setSprints(data.sprints || [])
        setTeams(data.teams || [])
        setError(
          data.failures.length > 0
            ? data.failures
                .map((failure) => `${failure.endpoint}: ${failure.message}`)
                .join('; ')
            : null,
        )
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Tracera</h1>
          <p className="subtitle">Traceability & Evidence Platform</p>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="container">
          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Loading data...</p>
            </div>
          )}

          {error && (
            <div className="error-banner">
              <strong>Error:</strong> {error}
            </div>
          )}

          {!loading && (
            <>
              {/* Status Section */}
              <section className="status-section">
                <h2>System Status</h2>
                <div className="status-grid">
                  <div className="status-card">
                    <div className="status-icon">
                      {health?.status === 'ok' ? '✓' : '?'}
                    </div>
                    <div className="status-info">
                      <h3>Backend Health</h3>
                      <p className={health?.status === 'ok' ? 'status-ok' : 'status-unknown'}>
                        {health?.status === 'ok' ? 'Healthy' : 'Checking...'}
                      </p>
                    </div>
                  </div>

                  <div className="status-card">
                    <div className="status-icon">{teams.length}</div>
                    <div className="status-info">
                      <h3>Teams</h3>
                      <p>{teams.length} team{teams.length !== 1 ? 's' : ''} registered</p>
                    </div>
                  </div>

                  <div className="status-card">
                    <div className="status-icon">{sprints.length}</div>
                    <div className="status-info">
                      <h3>Active Sprints</h3>
                      <p>{sprints.length} sprint{sprints.length !== 1 ? 's' : ''} configured</p>
                    </div>
                  </div>
                </div>
              </section>

              {/* Teams Section */}
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
                          <span className="team-members">
                            {team.members?.length || 0} members
                          </span>
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

              {/* Sprints Section */}
              <section className="data-section">
                <h2>Sprints</h2>
                {sprints.length > 0 ? (
                  <div className="sprints-list">
                    {sprints.map((sprint) => (
                      <div key={sprint.id} className="sprint-card">
                        <div className="sprint-header">
                          <h3>{sprint.name}</h3>
                          <span className={`sprint-status ${sprint.status}`}>
                            {sprint.status}
                          </span>
                        </div>
                        <p className="sprint-goal">{sprint.goal}</p>
                        <div className="sprint-dates">
                          <span>
                            {new Date(sprint.start_date).toLocaleDateString()}
                            {' '}-{' '}
                            {new Date(sprint.end_date).toLocaleDateString()}
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

              {/* API Info */}
              <section className="info-section">
                <h2>API Configuration</h2>
                <div className="info-card">
                  <p>
                    <strong>API Base:</strong> {apiBase || 'same origin'}
                  </p>
                  <p className="api-note">
                    Available endpoints: /health, /sdlc-pm/sprints, /org-intel/teams, /api/v1/coverage-matrix
                  </p>
                </div>
              </section>
            </>
          )}
        </div>
      </main>

      <footer className="dashboard-footer">
        <p>Tracera © 2024 - Traceability & Governance Platform</p>
      </footer>
    </div>
  )
}

export default Dashboard
