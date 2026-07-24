import './App.css'
import { useState } from 'react'
import Dashboard from './components/Dashboard'
import CoverageMatrix from './components/CoverageMatrix'
import TraceViewer from './components/TraceViewer'
import TopNav from './components/TopNav'

function App() {
  const [page, setPage] = useState('dashboard')
  let PageComponent = Dashboard
  if (page === 'trace') PageComponent = TraceViewer
  if (page === 'coverage') PageComponent = CoverageMatrix

  return (
    <div className="app">
      <TopNav current={page} onNavigate={setPage} />
      <PageComponent />
    </div>
  )
}

export default App
