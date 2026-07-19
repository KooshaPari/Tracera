import './App.css'
import { useState } from 'react'
import Dashboard from './components/Dashboard'
import CoverageMatrix from './components/CoverageMatrix'
import TraceViewer from './components/TraceViewer'
import TopNav from './components/TopNav'

function App() {
  const [page, setPage] = useState('dashboard')

  return (
    <div className="app">
      <TopNav current={page} onNavigate={setPage} />
      {page === 'trace' ? <TraceViewer /> : page === 'coverage' ? <CoverageMatrix /> : <Dashboard />}
    </div>
  )
}

export default App
