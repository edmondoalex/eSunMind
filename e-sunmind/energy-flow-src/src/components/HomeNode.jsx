import React from 'react'
import { Handle, Position } from '@xyflow/react'

export default function HomeNode({ data }) {
  return (
    <div className="home-core">
      <Handle type="target" position={Position.Left} style={{ opacity: 0, width: 0, height: 0 }} />
      <Handle type="source" position={Position.Right} style={{ opacity: 0, width: 0, height: 0 }} />

      <div className="home-glow" />
      <div className="home-surface">
        <div className="home-icon" aria-hidden="true">
          <svg viewBox="0 0 120 120" role="img">
            <path d="M18 54 L60 20 L102 54" fill="none" stroke="currentColor" strokeWidth="7" strokeLinecap="round" strokeLinejoin="round"/>
            <rect x="28" y="54" width="64" height="48" rx="8" fill="none" stroke="currentColor" strokeWidth="7"/>
            <rect x="52" y="70" width="16" height="32" rx="4" fill="none" stroke="currentColor" strokeWidth="6"/>
          </svg>
        </div>
        <div className="home-title">CASA</div>
        <div className="home-value">{data.value}</div>
        <div className="home-meta">
          <span>Base: {data.baseLoad}</span>
          <span>HP: {data.heatPump}</span>
        </div>
        <div className="home-pill">{data.state}</div>
      </div>
    </div>
  )
}
