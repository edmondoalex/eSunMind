import React, { useEffect, useMemo, useState } from 'react'
import { Background, ReactFlow, useEdgesState, useNodesState, Position } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import EnergyNode from './components/EnergyNode'
import EnergyEdge from './components/EnergyEdge'

const nodeTypes = { energyNode: EnergyNode }
const edgeTypes = { energyEdge: EnergyEdge }

const COLORS = {
  solar: '#ffd84f',
  battery: '#64d2ff',
  grid: '#b48dff',
  load: '#ff9d57'
}

const EMPTY = {
  pv: 0,
  house: 0,
  batteryPower: 0,
  batterySoc: 0,
  gridImport: 0,
  gridExport: 0,
  heatPump: 0,
  genericLoads: 0,
  installedKwp: 0
}

export default function App() {
  const [energy, setEnergy] = useState(EMPTY)
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  useEffect(() => {
    let stop = false
    const load = async () => {
      try {
        const r = await fetch('../api/data', { cache: 'no-store' })
        if (!r.ok) throw new Error(`api_data_http_${r.status}`)
        const j = await r.json()
        const n = j?.energy?.normalized || {}
        const pv = num(n.pv_power_w) / 1000
        const house = num(n.home_power_w) / 1000
        const batteryPower = num(n.battery_power_w) / 1000
        const batterySoc = num(n.battery_soc_pct)
        const gridRaw = num(n.grid_power_w) / 1000
        const gridImport = Math.max(0, gridRaw)
        const gridExport = Math.max(0, -gridRaw)
        const installedKwp = num(n.pv_installed_kwp)
        const heatPump = Math.max(0, house * 0.35)
        const genericLoads = Math.max(0, house - heatPump)
        if (!stop) {
          setEnergy({
            pv,
            house,
            batteryPower,
            batterySoc,
            gridImport,
            gridExport,
            heatPump,
            genericLoads,
            installedKwp
          })
        }
      } catch (_) {
        if (!stop) setEnergy((prev) => ({ ...prev }))
      }
    }
    load()
    const id = setInterval(load, 2000)
    return () => {
      stop = true
      clearInterval(id)
    }
  }, [])

  const summary = useMemo(() => {
    const net = energy.gridImport > 0 ? `Import ${fmt(energy.gridImport)} kW` : `Export ${fmt(energy.gridExport)} kW`
    return {
      pv: fmt(energy.pv),
      house: fmt(energy.house),
      soc: `${Math.round(energy.batterySoc)}%`,
      net
    }
  }, [energy])

  useEffect(() => {
    const n = [
      node('pv', 'Fotovoltaico', '☀️', `${fmt(energy.pv)} kW`, energy.pv > 0.2 ? 'produzione' : 'idle', 540, 120),
      node('house', 'Casa', '🏠', `${fmt(energy.house)} kW`, 'consumo', 540, 320),
      node('battery', 'Batteria', '🔋', `${fmt(Math.abs(energy.batteryPower))} kW`, energy.batteryPower >= 0 ? 'carica' : 'scarica', 300, 320),
      node('grid', 'Rete', '⚡', `${fmt(energy.gridImport > 0 ? energy.gridImport : energy.gridExport)} kW`, energy.gridImport > 0 ? 'import' : 'export', 780, 320),
      node('heatpump', 'Pompa di calore', '🔥', `${fmt(energy.heatPump)} kW`, energy.heatPump > 0 ? 'attiva' : 'off', 920, 180),
      node('loads', 'Carichi generici', '💡', `${fmt(energy.genericLoads)} kW`, 'consumo', 920, 430)
    ]

    const e = [
      edge('pv-house', 'pv', 'house', Math.max(0, energy.pv * 0.55), COLORS.solar),
      edge('pv-battery', 'pv', 'battery', Math.max(0, energy.batteryPower), COLORS.solar),
      edge('pv-grid', 'pv', 'grid', Math.max(0, energy.gridExport), COLORS.solar),
      edge('battery-house', 'battery', 'house', Math.max(0, -energy.batteryPower), COLORS.battery),
      edge('grid-house', 'grid', 'house', Math.max(0, energy.gridImport), COLORS.grid),
      edge('house-heatpump', 'house', 'heatpump', Math.max(0, energy.heatPump), COLORS.load),
      edge('house-loads', 'house', 'loads', Math.max(0, energy.genericLoads), COLORS.load)
    ]

    setNodes(n)
    setEdges(e)
  }, [energy, setNodes, setEdges])

  return (
    <div className="app">
      <header className="top">
        <h1>Energy Dashboard</h1>
        <div className="summary">
          <div className="pill"><span>Produzione FV</span><strong>{summary.pv} kW</strong></div>
          <div className="pill"><span>Consumo casa</span><strong>{summary.house} kW</strong></div>
          <div className="pill"><span>Batteria</span><strong>{summary.soc}</strong></div>
          <div className="pill"><span>Rete</span><strong>{summary.net}</strong></div>
        </div>
      </header>

      <main className="flow-wrap">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={false}
          panOnDrag={false}
          zoomOnScroll={false}
          zoomOnPinch={false}
          zoomOnDoubleClick={false}
          proOptions={{ hideAttribution: true }}
          fitView
          fitViewOptions={{ padding: 0.1 }}
          defaultEdgeOptions={{ type: 'energyEdge' }}
        >
          <Background gap={24} size={1} color="rgba(120,160,255,.12)" />
        </ReactFlow>
      </main>
    </div>
  )
}

function node(id, label, icon, value, state, x, y) {
  return {
    id,
    type: 'energyNode',
    position: { x, y },
    draggable: false,
    data: { label, icon, value, state },
    sourcePosition: Position.Right,
    targetPosition: Position.Left
  }
}

function edge(id, source, target, power, color) {
  return {
    id,
    source,
    target,
    type: 'energyEdge',
    animated: false,
    data: { power, color }
  }
}

function fmt(v) {
  if (!Number.isFinite(Number(v))) return '0.0'
  return Number(v).toFixed(1)
}

function num(v) {
  return Number.isFinite(Number(v)) ? Number(v) : 0
}
