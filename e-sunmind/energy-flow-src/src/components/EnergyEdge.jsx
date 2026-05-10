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
    borderRadius: 28
  })

  const power = Math.max(0, Number(data.power || 0))
  const width = Math.max(1.2, Math.min(10, 1.2 + power / 900))
  const opacity = power <= 0 ? 0.06 : Math.min(1, 0.2 + power / 6000)

  const c1 = data.c1 || '#ffd84f'
  const c2 = data.c2 || '#ff9d57'
  const gradId = `grad-${id}`
  const glowId = `glow-${id}`

  return (
    <>
      <svg className="edge-defs" width="0" height="0" aria-hidden="true" focusable="false">
        <defs>
          <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={c1} />
            <stop offset="100%" stopColor={c2} />
          </linearGradient>
          <filter id={glowId} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2.4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
      </svg>

      <BaseEdge id={id} path={path} style={{ stroke: `url(#${gradId})`, strokeWidth: width, opacity, filter: `url(#${glowId})` }} />

      {power > 0 && (
        <EdgeLabelRenderer>
          <svg className="edge-particle-layer" aria-hidden="true">
            <circle r="3.2" fill={c2} filter={`url(#${glowId})`}>
              <animateMotion dur={`${Math.max(0.8, 3.6 - power / 2800)}s`} repeatCount="indefinite" path={path} />
            </circle>
          </svg>
        </EdgeLabelRenderer>
      )}
    </>
  )
}
