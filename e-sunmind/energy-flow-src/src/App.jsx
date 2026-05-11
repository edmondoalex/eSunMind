import React, { useEffect, useState } from 'react'
import EnergyScene from './components/EnergyScene'
import { simulateEnergy } from './data/simulateEnergy'
import './App.css'

const INITIAL = {
  pv: 0,
  house: 0,
  batteryPower: 0,
  batterySoc: 62,
  gridImport: 0,
  gridExport: 0,
  heatPump: 0,
  genericLoads: 0,
  installedKwp: 6.6,
  pvToday: 0,
  homeToday: 0,
  source: 'sim'
}

export default function App() {
  const [energy, setEnergy] = useState(INITIAL)

  useEffect(() => {
    let stop = false
    let fallback = { ...INITIAL, pvToday: 18.4, homeToday: 23.7 }

    const load = async () => {
      try {
        const r = await fetch('../api/data', { cache: 'no-store' })
        if (!r.ok) throw new Error(`api_data_http_${r.status}`)
        const j = await r.json()
        const n = j?.energy?.normalized || {}

        const pv = toNum(n.pv_power_w) / 1000
        const house = toNum(n.home_power_w) / 1000
        const batteryPower = toNum(n.battery_power_w) / 1000
        const batterySoc = toNum(n.battery_soc_pct) || 62
        const gridRaw = toNum(n.grid_power_w) / 1000
        const gridImport = Math.max(0, gridRaw)
        const gridExport = Math.max(0, -gridRaw)
        const installedKwp = toNum(n.pv_installed_kwp) || 6.6
        const heatPump = Math.max(0, house * 0.34)
        const genericLoads = Math.max(0, house - heatPump)
        const pvToday = toNum(n.pv_energy_today_kwh)
        const homeToday = toNum(n.home_energy_today_kwh)

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
        if (!stop) setEnergy({ ...fallback, source: 'sim' })
      }
    }

    load()
    const id = setInterval(load, 2000)
    return () => {
      stop = true
      clearInterval(id)
    }
  }, [])

  return (
    <div className="energy-page">
      <header className="page-header">
        <h1>Energy Dashboard</h1>
        <p>{energy.source === 'live' ? 'Dati reali' : 'Simulazione fallback'}</p>
      </header>

      <main className="scene-panel">
        <EnergyScene energy={energy} />
      </main>
    </div>
  )
}

function toNum(v) {
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}