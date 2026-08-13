import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import NewAssessment from './pages/NewAssessment'
import AssessmentResults from './pages/AssessmentResults'
import UseCaseList from './pages/UseCaseList'
import './App.css'

const API_BASE = 'https://ai-govguard2.onrender.com/api'

function Navigation() {
  const location = useLocation()
  return (
    <nav className="nav">
      <div className="nav-brand">
        <Link to="/">AI-GovGuard</Link>
      </div>
      <div className="nav-links">
        <Link to="/" className={location.pathname === '/' ? 'active' : ''}>Dashboard</Link>
        <Link to="/use-cases" className={location.pathname === '/use-cases' ? 'active' : ''}>Use Cases</Link>
        <Link to="/new" className={location.pathname === '/new' ? 'active' : ''}>New Assessment</Link>
      </div>
    </nav>
  )
}

function App() {
  const [seeded, setSeeded] = useState(false)

  useEffect(() => {
    fetch(`${API_BASE}/seed`, { method: 'POST' })
      .then(() => setSeeded(true))
      .catch(() => setSeeded(true))
  }, [])

  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="main">
          <Routes>
            <Route path="/" element={<Dashboard API_BASE={API_BASE} />} />
            <Route path="/use-cases" element={<UseCaseList API_BASE={API_BASE} />} />
            <Route path="/new" element={<NewAssessment API_BASE={API_BASE} />} />
            <Route path="/assessment/:id" element={<AssessmentResults API_BASE={API_BASE} />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>This assessment is a governance decision-support tool and does not constitute legal advice or a formal regulatory determination.</p>
        </footer>
      </div>
    </Router>
  )
}

export default App
