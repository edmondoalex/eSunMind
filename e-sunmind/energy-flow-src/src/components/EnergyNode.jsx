import React from 'react'
import { Handle, Position } from '@xyflow/react'

export default function EnergyNode({ data }) {
  return (
    <div className="energy-node">
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
      <div className="node-icon">{data.icon}</div>
      <div className="node-name">{data.label}</div>
      <div className="node-value">{data.value}</div>
      <div className="node-state">{data.state}</div>
    </div>
  )
}
