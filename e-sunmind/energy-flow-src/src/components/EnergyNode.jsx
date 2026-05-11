import React from 'react'
import { Handle, Position } from '@xyflow/react'

export default function EnergyNode({ data }) {
  return (
    <div className={`device-badge ${data.kind || ''}`}>
      <Handle type="target" position={Position.Left} style={{ opacity: 0, width: 0, height: 0 }} />
      <Handle type="source" position={Position.Right} style={{ opacity: 0, width: 0, height: 0 }} />

      <div className="db-icon-wrap">
        <span className="db-icon">{data.icon}</span>
      </div>
      <div className="db-value">{data.value}</div>
      <div className="db-label">{data.label}</div>

      {data.kind === 'battery' && (
        <div className="db-battery-row">
          <div className="db-battery-track">
            <div className="db-battery-fill" style={{ width: `${Math.max(0, Math.min(100, Number(data.soc || 0)))}%` }} />
          </div>
          <span className="db-battery-pct">{Math.round(Number(data.soc || 0))}%</span>
        </div>
      )}

      {data.kind === 'grid' && (
        <div className="db-grid-dir">{data.gridDir === 'import' ? '↓ import' : '↑ export'}</div>
      )}
    </div>
  )
}
