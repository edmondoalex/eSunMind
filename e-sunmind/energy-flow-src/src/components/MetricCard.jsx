import React from 'react'

export default function MetricCard({ title, value, hint }) {
  return (
    <article className="metric-card">
      <h3>{title}</h3>
      <div className="metric-value">{value}</div>
      <p>{hint}</p>
    </article>
  )
}