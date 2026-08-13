import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'

function UseCaseList({ API_BASE }) {
  const navigate = useNavigate()
  const [useCases, setUseCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)

  useEffect(() => {
    fetchUseCases()
  }, [API_BASE])

  const fetchUseCases = () => {
    fetch(`${API_BASE}/use-cases`)
      .then(res => res.json())
      .then(data => {
        setUseCases(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  const handleDelete = async (id, name) => {
    if (!confirm(`Delete "${name}" and all its assessments?`)) return
    setDeleting(id)
    try {
      await fetch(`${API_BASE}/use-cases/${id}`, { method: 'DELETE' })
      fetchUseCases()
    } catch (err) {
      alert('Failed to delete')
    } finally {
      setDeleting(null)
    }
  }

  const handleReAssess = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/assessments/${id}`, { method: 'POST' })
      const result = await res.json()
      navigate(`/assessment/${result.assessment_id}`)
    } catch (err) {
      alert('Failed to run assessment')
    }
  }

  if (loading) return <div className="loading">Loading use cases...</div>

  return (
    <div>
      <div className="dashboard-header">
        <h1>AI Use Cases</h1>
        <Link to="/new" className="btn btn-primary">New Use Case</Link>
      </div>

      {useCases.length === 0 ? (
        <div className="card empty-state">
          <h3>No use cases yet</h3>
          <p>Create your first AI use case to get started.</p>
          <Link to="/new" className="btn btn-primary" style={{ marginTop: '1rem' }}>Create Use Case</Link>
        </div>
      ) : (
        <div className="card">
          <table className="use-case-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Industry</th>
                <th>Decision Type</th>
                <th>Model Type</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {useCases.map(uc => (
                <tr key={uc.id}>
                  <td><strong>{uc.name}</strong></td>
                  <td>{uc.industry}</td>
                  <td>{uc.decision_type.replace('_', ' ')}</td>
                  <td>{uc.model_type}</td>
                  <td>{uc.deployment_status}</td>
                  <td>
                    <button
                      className="btn btn-primary"
                      style={{ marginRight: '0.5rem', padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
                      onClick={() => handleReAssess(uc.id)}
                    >
                      Re-Assess
                    </button>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
                      onClick={() => handleDelete(uc.id, uc.name)}
                      disabled={deleting === uc.id}
                    >
                      {deleting === uc.id ? 'Deleting...' : 'Delete'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default UseCaseList
