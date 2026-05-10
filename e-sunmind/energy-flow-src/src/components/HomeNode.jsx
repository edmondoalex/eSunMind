import React from 'react'
import { Handle, Position } from '@xyflow/react'

export default function HomeNode({ data }) {
  return (
    <div className="tile tile-home">
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />

      <div className="home-hero">🏠</div>
      <div className="home-title">Casa</div>
      <div className="home-value">{data.value}</div>
      <div className="tile-pill">{data.state}</div>
    </div>
  )
}
