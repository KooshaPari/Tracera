import { useEffect } from 'react'
import { useAuth } from '@workos-inc/authkit-react'
import './App.css'
import Dashboard from './components/Dashboard'

function App() {
  const { getAccessToken, isLoading, signIn, signOut, signUp, user } = useAuth()

  useEffect(() => {
    if (!isLoading && !user && window.location.pathname === '/login') {
      void signIn()
    }
  }, [isLoading, signIn, user])

  if (isLoading) {
    return (
      <main className="app" aria-busy="true">
        <p>Loading secure session...</p>
      </main>
    )
  }

  if (!user) {
    return (
      <main className="app">
        <section className="auth-panel">
          <h1>Tracera</h1>
          <p>Sign in to access traceability and evidence dashboards.</p>
          <div className="auth-actions">
            <button type="button" onClick={() => void signIn()}>
              Sign in
            </button>
            <button type="button" onClick={() => void signUp()}>
              Create account
            </button>
          </div>
        </section>
      </main>
    )
  }

  return (
    <div className="app">
      <Dashboard getAccessToken={getAccessToken} />
      <button className="sign-out" type="button" onClick={() => signOut()}>
        Sign out {user.email}
      </button>
    </div>
  )
}

export default App
