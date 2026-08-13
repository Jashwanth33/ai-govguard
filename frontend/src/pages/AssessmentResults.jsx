import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts'

function AssessmentResults({ API_BASE }) {
  const { id } = useParams()
  const [assessment, setAssessment] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/assessments/${id}`)
      .then(res => res.json())
      .then(data => {
        setAssessment(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [API_BASE, id])

  if (loading) return <div className="loading">Loading assessment results...</div>
  if (!assessment) return <div className="loading">Assessment not found</div>

  const getRiskClass = (score) => {
    if (score <= 3) return 'low'
    if (score <= 6) return 'moderate'
    if (score <= 8) return 'high'
    return 'critical'
  }

  const radarData = assessment.risk_scores.map(rs => ({
    dimension: rs.dimension.replace('_', ' ').toUpperCase(),
    score: rs.score,
    fullMark: 10,
  }))

  const exportJSON = () => {
    const data = {
      use_case: assessment.use_case,
      overall_score: assessment.overall_score,
      risk_level: assessment.risk_level,
      confidence: assessment.confidence,
      executive_summary: assessment.executive_summary,
      risk_scores: assessment.risk_scores,
      top_risks: assessment.top_risks,
      recommended_controls: assessment.recommended_controls,
      evidence: assessment.evidence,
      exported_at: new Date().toISOString(),
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `assessment-${assessment.use_case.name.replace(/\s+/g, '-').toLowerCase()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const exportCSV = () => {
    const rows = [['Dimension', 'Score', 'Weight', 'Reason', 'Recommendation']]
    assessment.risk_scores.forEach(rs => {
      rows.push([rs.dimension, rs.score, rs.weight, `"${rs.reason || ''}"`, `"${rs.recommendation || ''}"`])
    })
    rows.push([])
    rows.push(['Overall Score', assessment.overall_score])
    rows.push(['Risk Level', assessment.risk_level])
    rows.push(['Confidence', assessment.confidence])
    const csv = rows.map(r => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `assessment-${assessment.use_case.name.replace(/\s+/g, '-').toLowerCase()}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="results-container">
      <div className="results-header">
        <div>
          <Link to="/" style={{ color: '#00d4ff', textDecoration: 'none', marginBottom: '1rem', display: 'inline-block' }}>
            Back to Dashboard
          </Link>
          <h1>{assessment.use_case.name}</h1>
          <p style={{ color: '#666' }}>{assessment.use_case.industry} | {assessment.use_case.purpose}</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
          <button className="btn btn-secondary" onClick={exportJSON} style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
            Export JSON
          </button>
          <button className="btn btn-secondary" onClick={exportCSV} style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
            Export CSV
          </button>
          <div className="overall-risk">
            <div className="risk-label">OVERALL RISK</div>
            <div className="risk-value" style={{ color: getRiskClass(assessment.overall_score) === 'critical' ? '#dc3545' : getRiskClass(assessment.overall_score) === 'high' ? '#ff6b6b' : '#fcc419' }}>
              {assessment.risk_level}
            </div>
            <div className="risk-score">{assessment.overall_score}/10</div>
            <div className="confidence">Confidence: {assessment.confidence}%</div>
          </div>
        </div>
      </div>

      <div className="detail-section">
        <h2>Risk Dimensions</h2>
        <div className="risk-dimensions">
          {assessment.risk_scores.map(rs => (
            <div key={rs.id} className={`risk-card ${getRiskClass(rs.score)}`}>
              <div className="dimension">{rs.dimension.replace('_', ' ')}</div>
              <div className="score">{rs.score}/10</div>
            </div>
          ))}
        </div>
        <div className="chart-container" style={{ height: '400px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 12 }} />
              <PolarRadiusAxis angle={30} domain={[0, 10]} />
              <Radar name="Risk Score" dataKey="score" stroke="#ff6b6b" fill="#ff6b6b" fillOpacity={0.3} />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="detail-section">
        <h2>Executive Summary</h2>
        <p>{assessment.executive_summary}</p>
      </div>

      <div className="detail-section">
        <h2>Top Risks</h2>
        {assessment.top_risks.length > 0 ? (
          assessment.top_risks.map((risk, idx) => (
            <div key={idx} className="risk-item">
              <strong>{risk.dimension}</strong> - Score: {risk.score}/10
              <p>{risk.risk}</p>
            </div>
          ))
        ) : (
          <p>No significant risks identified</p>
        )}
      </div>

      <div className="detail-section">
        <h2>Recommended Controls</h2>
        {assessment.recommended_controls.map((ctrl, idx) => (
          <div key={idx} className="control-item">
            <div>
              <strong>{ctrl.dimension}</strong>: {ctrl.control}
            </div>
            <span className={`priority-badge ${ctrl.priority}`}>{ctrl.priority}</span>
          </div>
        ))}
      </div>

      <div className="detail-section">
        <h2>Detailed Dimension Analysis</h2>
        {assessment.risk_scores.map(rs => (
          <div key={rs.id} className="dimension-detail">
            <h4>
              <span>{rs.dimension.replace('_', ' ').toUpperCase()}</span>
              <span style={{ color: getRiskClass(rs.score) === 'critical' ? '#dc3545' : getRiskClass(rs.score) === 'high' ? '#ff6b6b' : '#333' }}>
                {rs.score}/10
              </span>
            </h4>
            <p className="reason">{rs.reason}</p>
            <p className="recommendation">{rs.recommendation}</p>
          </div>
        ))}
      </div>

      {assessment.evidence && assessment.evidence.length > 0 && (
        <div className="detail-section">
          <h2>Evidence & Sources</h2>
          {assessment.evidence.map((ev, idx) => (
            <div key={idx} className="evidence-item">
              <span className={`source-type ${ev.source.source_type.toLowerCase().replace(/[\s\/]+/g, '-')}`}>
                {ev.source.source_type}
              </span>
              <h4>{ev.source.title}</h4>
              <p style={{ color: '#666', fontSize: '0.9rem' }}>
                {ev.source.organization} | {ev.source.authority_level}
              </p>
              <p style={{ marginTop: '0.5rem' }}>{ev.finding}</p>
              {ev.source.url && (
                <a href={ev.source.url} target="_blank" rel="noopener noreferrer" style={{ color: '#00d4ff' }}>
                  View Source
                </a>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="detail-section" style={{ background: '#fff3cd', borderLeft: '4px solid #ffc107' }}>
        <p style={{ fontStyle: 'italic', color: '#856404' }}>
          This assessment is a governance decision-support tool and does not constitute legal advice or a formal regulatory determination.
          Results should be reviewed by the organization's governance, legal, and compliance functions.
        </p>
      </div>
    </div>
  )
}

export default AssessmentResults
