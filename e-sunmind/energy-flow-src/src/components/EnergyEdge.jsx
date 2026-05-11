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
    borderRadius: 34
  })

  const power = Math.max(0, Number(data.power || 0))
  const strokeWidth = power <= 0 ? 1.2 : Math.min(18, 5 + power * 2.1)
  const opacity = power <= 0 ? 0.06 : Math.min(1, 0.35 + power * 0.2)
  const c1 = data.c1 || '#ffd84f'
  const c2 = data.c2 || '#ff9a5a'
  const speed = Math.max(0.55, 2.6 - power * 0.65)

  const gradId = `g-${id}`
  const glowId = `f-${id}`

  return (
    <>
      <svg width="0" height="0" className="edge-defs" aria-hidden="true" focusable="false">
        <defs>
          <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={c1} />
            <stop offset="100%" stopColor={c2} />
          </linearGradient>
          <filter id={glowId} x="-80%" y="-80%" width="260%" height="260%">
            <feGaussianBlur stdDeviation="4.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
      </svg>

      <BaseEdge
        id={id}
        path={path}
        style={{
          stroke: `url(#${gradId})`,
          strokeWidth,
          opacity,
          filter: `url(#${glowId})`,
          strokeLinecap: 'round'
        }}
      />

      {power > 0 && (
        <EdgeLabelRenderer>
          <svg className="edge-particle-layer" aria-hidden="true">
            <circle r="4" fill={c2} filter={`url(#${glowId})`}>
              <animateMotion dur={`${speed}s`} repeatCount="indefinite" path={path} />
            </circle>
            <circle r="2.4" fill={c1} filter={`url(#${glowId})`}>
              <animateMotion dur={`${speed * 1.18}s`} repeatCount="indefinite" path={path} />
            </circle>
          </svg>
        </EdgeLabelRenderer>
      )}
    </>
  )
}
