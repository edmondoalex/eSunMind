import React from 'react'

export default function EnergyScene({ energy }) {
  const pvToHome = Math.max(0, Math.min(energy.pv, energy.house))
  const pvExtra = Math.max(0, energy.pv - energy.house)
  const batteryCharge = Math.max(0, energy.batteryPower)
  const batteryDischarge = Math.max(0, -energy.batteryPower)
  const gridImport = Math.max(0, energy.gridImport)
  const gridExport = Math.max(0, energy.gridExport)

  const flowHomeToLoads = Math.max(0, energy.genericLoads)
  const flowHomeToHp = Math.max(0, energy.heatPump)

  const pathOpacity = (v) => (v <= 0.01 ? 0.14 : Math.min(0.9, 0.25 + v * 0.16))

  return (
    <div className="scene-root">
      <svg viewBox="0 0 1200 675" className="energy-svg" role="img" aria-label="Schema energetico premium">
        <defs>
          <linearGradient id="scene-bg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#f9fbff" />
            <stop offset="100%" stopColor="#eef3ff" />
          </linearGradient>

          <linearGradient id="line-main" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#d4defe" />
            <stop offset="100%" stopColor="#b9ccff" />
          </linearGradient>

          <filter id="line-soft" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="1.2" />
          </filter>

          <symbol id="icon-pv" viewBox="0 0 120 120">
            <g fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="24,52 78,36 102,64 48,80" fill="#f5f8ff" />
              <path d="M36 48 L84 34 M44 60 L92 46 M52 72 L100 58" stroke="#8ba8df" />
              <path d="M46 44 L54 72 M62 39 L70 68 M78 35 L86 63" stroke="#8ba8df" />
              <path d="M56 80L56 95M67 77L67 93" stroke="#95a9d6" />
            </g>
          </symbol>

          <symbol id="icon-house" viewBox="0 0 120 120">
            <polygon points="26,58 60,34 94,58 94,92 26,92" fill="#ffffff" stroke="#b9c9e9" strokeWidth="2.4"/>
            <polygon points="22,58 60,30 98,58" fill="#e8effc" stroke="#b9c9e9" strokeWidth="2.4"/>
            <rect x="52" y="67" width="16" height="25" rx="2" fill="#e7eefb" stroke="#b9c9e9" strokeWidth="2"/>
            <rect x="34" y="66" width="12" height="10" rx="2" fill="#d8e4fb"/>
            <rect x="74" y="66" width="12" height="10" rx="2" fill="#d8e4fb"/>
          </symbol>

          <symbol id="icon-battery" viewBox="0 0 120 120">
            <rect x="40" y="28" width="38" height="64" rx="8" fill="#fff" stroke="#b9c9e9" strokeWidth="2.5"/>
            <rect x="52" y="22" width="14" height="7" rx="2" fill="#c4d4f5"/>
            <rect x="45" y="36" width="28" height="12" rx="3" fill="#dce8ff"/>
            <rect x="45" y="52" width="28" height="12" rx="3" fill="#cfe0ff"/>
            <rect x="45" y="68" width="28" height="12" rx="3" fill="#bfd5ff"/>
          </symbol>

          <symbol id="icon-grid" viewBox="0 0 120 120">
            <g fill="none" stroke="#b7c6e3" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M60 22L84 94H36z" />
              <path d="M40 48h40M34 62h52M30 77h60" />
              <path d="M60 22v72" />
            </g>
          </symbol>

          <symbol id="icon-hp" viewBox="0 0 120 120">
            <rect x="32" y="38" width="56" height="42" rx="8" fill="#fff" stroke="#b9c9e9" strokeWidth="2.3"/>
            <circle cx="60" cy="59" r="11" fill="none" stroke="#9fb5dc" strokeWidth="2.2"/>
            <path d="M60 48v22M49 59h22" stroke="#9fb5dc" strokeWidth="2.2"/>
            <rect x="44" y="83" width="32" height="4" rx="2" fill="#c8d6f1"/>
          </symbol>

          <symbol id="icon-load" viewBox="0 0 120 120">
            <path d="M62 28L46 58h16l-4 30 16-32H58z" fill="#9eb5df" />
          </symbol>

          {pathDef('path-pv-home', 'M560 130 C560 195 560 225 560 270')}
          {pathDef('path-home-load', 'M500 326 C438 324 390 304 346 272')}
          {pathDef('path-home-hp', 'M620 326 C682 324 732 304 776 272')}
          {pathDef('path-bat-home', 'M448 472 C488 414 505 380 530 346')}
          {pathDef('path-grid-home', 'M674 472 C640 414 624 380 596 346')}
          {pathDef('path-pv-bat', 'M532 140 C478 222 455 332 446 442')}
          {pathDef('path-pv-grid', 'M588 140 C640 222 664 332 676 442')}
        </defs>

        <rect x="0" y="0" width="1200" height="675" rx="24" fill="url(#scene-bg)" />

        <Flow d="M560 130 C560 195 560 225 560 270" opacity={pathOpacity(pvToHome)} />
        <Flow d="M500 326 C438 324 390 304 346 272" opacity={pathOpacity(flowHomeToLoads)} />
        <Flow d="M620 326 C682 324 732 304 776 272" opacity={pathOpacity(flowHomeToHp)} />
        <Flow d="M448 472 C488 414 505 380 530 346" opacity={pathOpacity(Math.max(batteryCharge, batteryDischarge))} />
        <Flow d="M674 472 C640 414 624 380 596 346" opacity={pathOpacity(Math.max(gridImport, gridExport))} />
        <Flow d="M532 140 C478 222 455 332 446 442" opacity={pathOpacity(pvExtra)} />
        <Flow d="M588 140 C640 222 664 332 676 442" opacity={pathOpacity(gridExport)} />

        <Dot href="#path-pv-home" active={pvToHome > 0.02} dur="2.6s" />
        <Dot href="#path-home-load" active={flowHomeToLoads > 0.02} dur="2.4s" />
        <Dot href="#path-home-hp" active={flowHomeToHp > 0.02} dur="2.4s" />
        <Dot href="#path-bat-home" active={Math.max(batteryCharge, batteryDischarge) > 0.02} dur="2.3s" />
        <Dot href="#path-grid-home" active={Math.max(gridImport, gridExport) > 0.02} dur="2.3s" />

        <FlowText x={568} y={210} v={pvToHome} />
        <FlowText x={410} y={303} v={flowHomeToLoads} />
        <FlowText x={708} y={303} v={flowHomeToHp} />
        <FlowText x={470} y={421} v={Math.max(batteryCharge, batteryDischarge)} />
        <FlowText x={630} y={421} v={Math.max(gridImport, gridExport)} />

        <Device x={560} y={110} icon="icon-pv" label="Fotovoltaico" value={energy.pv} />
        <Device x={330} y={262} icon="icon-load" label="Carichi" value={energy.genericLoads} small />
        <Device x={790} y={262} icon="icon-hp" label="Pompa di calore" value={energy.heatPump} small />
        <Device x={438} y={492} icon="icon-battery" label="Batteria" value={Math.abs(energy.batteryPower)} suffix={`${Math.round(energy.batterySoc)}%`} small />
        <Device x={682} y={492} icon="icon-grid" label="Rete" value={Math.max(gridImport, gridExport)} suffix={gridImport > 0 ? 'import' : 'export'} small />

        <g transform="translate(560 326)">
          <ellipse rx="126" ry="124" fill="#edf3ff" />
          <use href="#icon-house" x={-60} y={-72} width="120" height="120" />
          <text x="0" y="72" textAnchor="middle" className="home-value-main">{fmt(energy.house)}</text>
          <text x="42" y="72" className="unit-main">kW</text>
          <text x="0" y="92" textAnchor="middle" className="home-caption">Consumo casa</text>
        </g>

        <g transform="translate(900 158)" className="scene-metrics">
          <MetricRow y={0} label="Real-time Power" value={energy.pv} unit="kW" />
          <MetricRow y={70} label="Installed Power" value={energy.installedKwp} unit="kWp" />
          <MetricRow y={140} label="Produzione Oggi" value={energy.pvToday} unit="kWh" />
          <MetricRow y={210} label="Consumo Oggi" value={energy.homeToday} unit="kWh" />
        </g>
      </svg>
    </div>
  )
}

function Device({ x, y, icon, label, value, suffix, small }) {
  return (
    <g transform={`translate(${x} ${y})`} className={`device-lite ${small ? 'small' : ''}`}>
      <use href={`#${icon}`} x={-34} y={-34} width="68" height="68" />
      <text x="0" y="48" textAnchor="middle" className="device-val">{fmt(value)}</text>
      <text x="30" y="48" className="device-unit">kW</text>
      <text x="0" y="66" textAnchor="middle" className="device-label">{label}</text>
      {suffix ? <text x="0" y="81" textAnchor="middle" className="device-suffix">{suffix}</text> : null}
    </g>
  )
}

function MetricRow({ y, label, value, unit }) {
  return (
    <g transform={`translate(0 ${y})`}>
      <text x="0" y="0" className="metric-label">{label}</text>
      <text x="0" y="34" className="metric-value-scene">{fmt(value)}</text>
      <text x="72" y="34" className="metric-unit-scene">{unit}</text>
    </g>
  )
}

function Flow({ d, opacity }) {
  return (
    <g style={{ opacity }}>
      <path d={d} className="flow-base" />
      <path d={d} className="flow-top" />
    </g>
  )
}

function Dot({ href, active, dur }) {
  if (!active) return null
  return (
    <circle r="2.8" className="flow-dot-light">
      <animateMotion dur={dur} repeatCount="indefinite">
        <mpath href={href} />
      </animateMotion>
    </circle>
  )
}

function FlowText({ x, y, v }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <text x="0" y="0" className="flow-num">{fmt(v)}</text>
      <text x="33" y="0" className="flow-unit">kW</text>
    </g>
  )
}

function pathDef(id, d) {
  return <path id={id} d={d} fill="none" stroke="none" />
}

function fmt(v) {
  const n = Number(v)
  return Number.isFinite(n) ? n.toFixed(2) : '0.00'
}