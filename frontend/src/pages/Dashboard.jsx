import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

function Dashboard({ API_BASE }) {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/dashboard`)
      .then(res => res.json())
      .then(data => {
        setStats(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [API_BASE])

  if (loading) return <div className="loading">Loading dashboard...</div>
  if (!stats) return <div className="loading">Failed to load dashboard</div>

  const chartData = Object.entries(stats.risk_distribution).map(([key, value]) => ({
    name: key,
    count: value,
  }))

  return (
    <div>
      <div className="dashboard-header">
        <h1>AI Governance Dashboard</h1>
        <Link to="/new" className="btn btn-primary">New Assessment</Link>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total_use_cases}</div>
          <div className="stat-label">Total AI Systems</div>
        </div>
        <div className="stat-card risk-high">
          <div className="stat-value">{stats.high_risk_count}</div>
          <div className="stat-label">High Risk</div>
        </div>
        <div className="stat-card risk-critical">
          <div className="stat-value">{stats.very_high_risk_count}</div>
          <div className="stat-label">Very High / Critical</div>
        </div>
        <div className="stat-card risk-low">
          <div className="stat-value">{stats.low_risk_count}</div>
          <div className="stat-label">Low / Moderate</div>
        </div>
        <div className="stat-card risk-avg">
          <div className="stat-value">{stats.average_score || 'N/A'}</div>
          <div className="stat-label">Average Score</div>
        </div>
      </div>

      <div className="content-grid">
        <div className="card">
          <h2>Risk Distribution</h2>
          {stats.total_assessments > 0 ? (
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#00d4ff" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="empty-state">
              <p>No assessments yet. Create your first assessment!</p>
            </div>
          )}
        </div>

        <div className="card">
          <h2>Recent Assessments</h2>
          {stats.recent_assessments.length > 0 ? (
            <table className="use-case-table">
              <thead>
                <tr>
                  <th>Use Case</th>
                  <th>Score</th>
                  <th>Risk Level</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_assessments.map(a => (
                  <tr key={a.id}>
                    <td>
                      <Link to={`/assessment/${a.id}`}>{a.use_case_name}</Link>
                    </td>
                    <td>{a.overall_score}/10</td>
                    <td>
                      <span className={`risk-badge ${a.risk_level.replace(' ', '-')}`}>
                        {a.risk_level}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">
              <p>No assessments yet</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
