import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function NewAssessment({ API_BASE }) {
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    industry: '',
    purpose: '',
    ai_capability: '',
    data_types: [],
    decision_type: '',
    human_oversight: '',
    model_type: '',
    deployment_status: 'Planning',
    affected_population: 0,
  })

  const industries = [
    'Human Resources', 'Banking', 'Insurance', 'Healthcare', 'Technology',
    'Education', 'Retail', 'Government', 'Law Enforcement', 'Manufacturing',
    'Transportation', 'Energy', 'Telecommunications',
  ]

  const handleCheckboxChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter(v => v !== value)
        : [...prev[field], value],
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)

    try {
      const useCaseRes = await fetch(`${API_BASE}/use-cases`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })
      const useCase = await useCaseRes.json()

      const assessRes = await fetch(`${API_BASE}/assessments/${useCase.id}`, {
        method: 'POST',
      })
      const result = await assessRes.json()

      navigate(`/assessment/${result.assessment_id}`)
    } catch (err) {
      console.error('Error:', err)
      alert('Failed to create assessment')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="form-container">
      <h1>New AI Use Case Assessment</h1>
      <p className="subtitle">Describe your AI system to receive a governance risk assessment</p>

      <form onSubmit={handleSubmit}>
        <div className="form-section">
          <h3>Basic Information</h3>
          <div className="form-group">
            <label>Use Case Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={e => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., AI Recruitment Screening"
              required
            />
          </div>
          <div className="form-group">
            <label>Industry *</label>
            <select
              value={formData.industry}
              onChange={e => setFormData({ ...formData, industry: e.target.value })}
              required
            >
              <option value="">Select industry</option>
              {industries.map(ind => (
                <option key={ind} value={ind}>{ind}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Business Purpose *</label>
            <textarea
              value={formData.purpose}
              onChange={e => setFormData({ ...formData, purpose: e.target.value })}
              placeholder="Describe what this AI system does and why"
              rows={3}
              required
            />
          </div>
          <div className="form-group">
            <label>AI Capability *</label>
            <input
              type="text"
              value={formData.ai_capability}
              onChange={e => setFormData({ ...formData, ai_capability: e.target.value })}
              placeholder="e.g., Resume screening, Credit scoring, Fraud detection"
              required
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Data Information</h3>
          <div className="form-group">
            <label>Data Types Used * (select all that apply)</label>
            <div className="checkbox-group">
              {[
                { value: 'personal_data', label: 'Personal Data' },
                { value: 'sensitive_data', label: 'Sensitive Data' },
                { value: 'financial_data', label: 'Financial Data' },
                { value: 'health_data', label: 'Health Data' },
                { value: 'biometric_data', label: 'Biometric Data' },
              ].map(item => (
                <label key={item.value} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.data_types.includes(item.value)}
                    onChange={() => handleCheckboxChange('data_types', item.value)}
                  />
                  {item.label}
                </label>
              ))}
            </div>
          </div>
          <div className="form-group">
            <label>Number of People Affected</label>
            <input
              type="number"
              value={formData.affected_population}
              onChange={e => setFormData({ ...formData, affected_population: parseInt(e.target.value) || 0 })}
              min="0"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Decision Information</h3>
          <div className="form-group">
            <label>Decision Type *</label>
            <div className="radio-group">
              {[
                { value: 'informational', label: 'Informational' },
                { value: 'advisory', label: 'Advisory' },
                { value: 'decision_support', label: 'Decision Support' },
                { value: 'automated', label: 'Automated Decision' },
                { value: 'high_impact_automated', label: 'High-Impact Automated' },
              ].map(item => (
                <label key={item.value} className="radio-label">
                  <input
                    type="radio"
                    name="decision_type"
                    value={item.value}
                    checked={formData.decision_type === item.value}
                    onChange={e => setFormData({ ...formData, decision_type: e.target.value })}
                  />
                  {item.label}
                </label>
              ))}
            </div>
          </div>
          <div className="form-group">
            <label>Human Oversight *</label>
            <div className="radio-group">
              {[
                { value: 'required', label: 'Required' },
                { value: 'optional', label: 'Optional' },
                { value: 'none', label: 'None' },
              ].map(item => (
                <label key={item.value} className="radio-label">
                  <input
                    type="radio"
                    name="human_oversight"
                    value={item.value}
                    checked={formData.human_oversight === item.value}
                    onChange={e => setFormData({ ...formData, human_oversight: e.target.value })}
                  />
                  {item.label}
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Model Information</h3>
          <div className="form-group">
            <label>Model Type *</label>
            <div className="radio-group">
              {[
                { value: 'classification', label: 'Classification' },
                { value: 'regression', label: 'Regression' },
                { value: 'generative_ai', label: 'Generative AI' },
                { value: 'recommendation', label: 'Recommendation' },
                { value: 'other', label: 'Other' },
              ].map(item => (
                <label key={item.value} className="radio-label">
                  <input
                    type="radio"
                    name="model_type"
                    value={item.value}
                    checked={formData.model_type === item.value}
                    onChange={e => setFormData({ ...formData, model_type: e.target.value })}
                  />
                  {item.label}
                </label>
              ))}
            </div>
          </div>
          <div className="form-group">
            <label>Deployment Status</label>
            <select
              value={formData.deployment_status}
              onChange={e => setFormData({ ...formData, deployment_status: e.target.value })}
            >
              <option value="Planning">Planning</option>
              <option value="Development">Development</option>
              <option value="Testing">Testing</option>
              <option value="Pilot">Pilot</option>
              <option value="Production">Production</option>
            </select>
          </div>
        </div>

        <button type="submit" className="btn btn-primary" disabled={submitting} style={{ width: '100%' }}>
          {submitting ? 'Running Assessment...' : 'Run Governance Assessment'}
        </button>
      </form>
    </div>
  )
}

export default NewAssessment
