import React from 'react'
import { BaseEdge, EdgeLabelRenderer, getSmoothStepPath } from '@xyflow/react'

export default function EnergyEdge(props) {
  const {
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    data = {}
  } = props

  const [path] = getSmoothStepPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    borderRadius: 24
  })

  const power = Math.max(0, Number(data.power || 0))
  const strokeWidth = Math.max(1, Math.min(14, power / 800))
  const opacity = power === 0 ? 0.08 : Math.min(1, 0.22 + power / 7000)
  const color = data.color || '#66e3ff'

  return (
    <>
      <BaseEdge id={id} path={path} style={{ stroke: color, strokeWidth, opacity }} />
      {power > 0 && (
        <EdgeLabelRenderer>
          <svg className="edge-particle-layer">
            <circle r="3.5" fill={color} filter="url(#glow)">
              <animateMotion dur={`${Math.max(0.9, 4 - power / 2500)}s`} repeatCount="indefinite" path={path} />
            </circle>
            <defs>
              <filter id="glow">
                <feGaussianBlur stdDeviation="2.5" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
          </svg>
        </EdgeLabelRenderer>
      )}
    </>
  )
}
