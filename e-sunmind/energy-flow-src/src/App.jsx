import React, { useEffect, useMemo, useState } from 'react'
import { Background, Position, ReactFlow, useEdgesState, useNodesState } from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import EnergyNode from './components/EnergyNode'
import HomeNode from './components/HomeNode'
import EnergyEdge from './components/EnergyEdge'
import { simulateEnergy } from './data/simulateEnergy'

const nodeTypes = {
  energyNode: EnergyNode,
  homeNode: HomeNode
}

const edgeTypes = {
  energyEdge: EnergyEdge
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
  installedKwp: 0,
  pvToday: 0,
  homeToday: 0,
  source: 'live'
}

export default function App() {
  const [energy, setEnergy] = useState(EMPTY)
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  useEffect(() => {
    let stop = false
    let fallback = { ...EMPTY, batterySoc: 62, source: 'sim' }

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
        const heatPump = Math.max(0, house * 0.34)
        const genericLoads = Math.max(0, house - heatPump)
        const pvToday = num(n.pv_energy_today_kwh)
        const homeToday = num(n.home_energy_today_kwh)

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
            installedKwp,
            pvToday,
            homeToday,
            source: 'live'
          })
        }
      } catch (_) {
        fallback = simulateEnergy(fallback)
        if (!stop) {
          setEnergy({ ...fallback, installedKwp: fallback.installedKwp || 6.0, source: 'sim' })
        }
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
    const gridLabel = energy.gridImport > 0 ? `Import ${fmt(energy.gridImport)} kW` : `Export ${fmt(energy.gridExport)} kW`
    return {
      pv: `${fmt(energy.pv)} kW`,
      house: `${fmt(energy.house)} kW`,
      soc: `${Math.round(energy.batterySoc)}%`,
      grid: gridLabel
    }
  }, [energy])

  useEffect(() => {
    const deviceNodes = [
      mkNode('pv', 'energyNode', 'Fotovoltaico', '☀️', `${fmt(energy.pv)} kW`, energy.pv > 0.2 ? 'produzione' : 'idle', 520, 64),
      mkNode('battery', 'energyNode', 'Batteria', '🔋', `${fmt(Math.abs(energy.batteryPower))} kW`, energy.batteryPower >= 0 ? 'carica' : 'scarica', 190, 438),
      mkNode('grid', 'energyNode', 'Rete elettrica', '⚡', `${fmt(energy.gridImport > 0 ? energy.gridImport : energy.gridExport)} kW`, energy.gridImport > 0 ? 'import' : 'export', 850, 438),
      mkNode('heatpump', 'energyNode', 'Pompa di calore', '🔥', `${fmt(energy.heatPump)} kW`, energy.heatPump > 0 ? 'attiva' : 'off', 1028, 226),
      mkNode('loads', 'energyNode', 'Carichi generici', '💡', `${fmt(energy.genericLoads)} kW`, 'consumo', 34, 226),
      {
        id: 'home',
        type: 'homeNode',
        position: { x: 515, y: 314 },
        data: {
          value: `${fmt(energy.house)} kW`,
          state: 'consumo centrale'
        },
        draggable: false,
        sourcePosition: Position.Right,
        targetPosition: Position.Left
      }
    ]

    const flowEdges = [
      mkEdge('pv-home', 'pv', 'home', energy.pv * 0.58, '#ffd54a', '#ffb84a'),
      mkEdge('pv-bat', 'pv', 'battery', Math.max(0, energy.batteryPower), '#ffe45e', '#5fd3ff'),
      mkEdge('pv-grid', 'pv', 'grid', Math.max(0, energy.gridExport), '#ffd84f', '#7f8dff'),
      mkEdge('bat-home', 'battery', 'home', Math.max(0, -energy.batteryPower), '#47e7c6', '#64d2ff'),
      mkEdge('grid-home', 'grid', 'home', Math.max(0, energy.gridImport), '#5ba7ff', '#8e74ff'),
      mkEdge('home-hp', 'home', 'heatpump', Math.max(0, energy.heatPump), '#aa75ff', '#ff9b5f'),
      mkEdge('home-load', 'home', 'loads', Math.max(0, energy.genericLoads), '#9b6dff', '#ffad60')
    ]

    setNodes(deviceNodes)
    setEdges(flowEdges)
  }, [energy, setNodes, setEdges])

  return (
    <div className="energy-app">
      <header className="dash-header">
        <h1>Energy Dashboard</h1>
        <div className="header-pills">
          <div className="pill"><span>Produzione FV</span><strong>{summary.pv}</strong></div>
          <div className="pill"><span>Consumo casa</span><strong>{summary.house}</strong></div>
          <div className="pill"><span>Batteria</span><strong>{summary.soc}</strong></div>
          <div className="pill"><span>Rete</span><strong>{summary.grid}</strong></div>
        </div>
      </header>

      <section className="scene-wrap">
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
          panOnScroll={false}
          preventScrolling={true}
          proOptions={{ hideAttribution: true }}
          fitView
          fitViewOptions={{ padding: 0.12, minZoom: 0.65, maxZoom: 1 }}
          defaultEdgeOptions={{ type: 'energyEdge' }}
        >
          <Background gap={40} size={1} color="rgba(255,255,255,0.03)" />
        </ReactFlow>
      </section>

      <section className="bottom-cards">
        <div className="mini-card">
          <span>Oggi prodotto</span>
          <strong>{fmt(energy.pvToday)} kWh</strong>
        </div>
        <div className="mini-card">
          <span>Oggi consumato</span>
          <strong>{fmt(energy.homeToday)} kWh</strong>
        </div>
        <div className="mini-card">
          <span>Autonomia batteria</span>
          <strong>{Math.round(energy.batterySoc)}%</strong>
        </div>
      </section>
    </div>
  )
}

function mkNode(id, type, label, icon, value, state, x, y) {
  return {
    id,
    type,
    position: { x, y },
    draggable: false,
    data: { label, icon, value, state },
    sourcePosition: Position.Right,
    targetPosition: Position.Left
  }
}

function mkEdge(id, source, target, power, c1, c2) {
  return {
    id,
    source,
    target,
    type: 'energyEdge',
    data: { power, c1, c2 }
  }
}

function num(v) {
  return Number.isFinite(Number(v)) ? Number(v) : 0
}

function fmt(v) {
  if (!Number.isFinite(Number(v))) return '0.0'
  return Number(v).toFixed(1)
}
