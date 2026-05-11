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

  const pathOpacity = (v) => (v <= 0.01 ? 0.16 : Math.min(0.95, 0.34 + v * 0.16))

  return (
    <div className="scene-root">
      <svg viewBox="0 0 1200 675" className="energy-svg" role="img" aria-label="Schema energetico premium">
        <defs>
          <linearGradient id="scene-bg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#f7f9fe" />
            <stop offset="100%" stopColor="#f1f5fc" />
          </linearGradient>

          <linearGradient id="line-main" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#d4defe" />
            <stop offset="100%" stopColor="#b7c8ff" />
          </linearGradient>

          <filter id="line-soft" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="1.25" />
          </filter>

          <symbol id="icon-pv" viewBox="0 0 120 120">
            <g fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="20,54 80,36 104,66 44,84" fill="#f5f8ff" />
              <path d="M32 50 L86 34 M40 62 L94 46 M48 74 L102 58" stroke="#7fa2df" />
              <path d="M42 46 L50 76 M58 41 L66 71 M74 37 L82 67" stroke="#7fa2df" />
              <path d="M54 84L54 99M67 80L67 97" stroke="#92abd8" />
            </g>
          </symbol>

          <symbol id="icon-house" viewBox="0 0 120 120">
            <polygon points="24,58 60,32 96,58 96,95 24,95" fill="#ffffff" stroke="#a9bfdf" strokeWidth="2.5"/>
            <polygon points="20,58 60,28 100,58" fill="#e5eefc" stroke="#a9bfdf" strokeWidth="2.5"/>
            <rect x="52" y="70" width="16" height="25" rx="2" fill="#e2ebfb" stroke="#a9bfdf" strokeWidth="2"/>
            <rect x="33" y="67" width="13" height="10" rx="2" fill="#d3e1fa"/>
            <rect x="74" y="67" width="13" height="10" rx="2" fill="#d3e1fa"/>
          </symbol>

          <symbol id="icon-battery" viewBox="0 0 120 120">
            <rect x="38" y="24" width="42" height="68" rx="8" fill="#fff" stroke="#a8bfdf" strokeWidth="2.6"/>
            <rect x="52" y="18" width="14" height="7" rx="2" fill="#c0d0f0"/>
            <rect x="44" y="32" width="30" height="12" rx="3" fill="#dce8ff"/>
            <rect x="44" y="48" width="30" height="12" rx="3" fill="#cfe0ff"/>
            <rect x="44" y="64" width="30" height="12" rx="3" fill="#bfd5ff"/>
          </symbol>

          <symbol id="icon-grid" viewBox="0 0 120 120">
            <g fill="none" stroke="#7fa2df" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M60 20L88 98H32z" />
              <path d="M36 48h48M30 64h60M26 80h68" />
              <path d="M60 20v78" />
            </g>
          </symbol>

          <symbol id="icon-hp" viewBox="0 0 120 120">
            <rect x="30" y="36" width="60" height="44" rx="9" fill="#fff" stroke="#a9bfdf" strokeWidth="2.3"/>
            <circle cx="60" cy="58" r="12" fill="none" stroke="#7fa2df" strokeWidth="2.3"/>
            <path d="M60 46v24M48 58h24" stroke="#7fa2df" strokeWidth="2.3"/>
            <rect x="43" y="83" width="34" height="4" rx="2" fill="#c4d4f0"/>
          </symbol>

          <symbol id="icon-load" viewBox="0 0 120 120">
            <path d="M63 27L45 60h17l-5 32 18-34H58z" fill="#7fa2df" />
          </symbol>

          {pathDef('path-pv-home', 'M560 132 C560 194 560 232 560 278')}
          {pathDef('path-home-load', 'M498 330 C438 326 392 306 350 276')}
          {pathDef('path-home-hp', 'M622 330 C680 326 726 306 768 276')}
          {pathDef('path-bat-home', 'M450 484 C490 420 510 388 534 352')}
          {pathDef('path-grid-home', 'M676 484 C642 420 624 388 598 352')}
          {pathDef('path-pv-bat', 'M532 142 C480 226 458 340 450 454')}
          {pathDef('path-pv-grid', 'M588 142 C638 226 660 340 670 454')}
        </defs>

        <rect x="0" y="0" width="1200" height="675" rx="24" fill="url(#scene-bg)" />

        <Flow d="M560 132 C560 194 560 232 560 278" opacity={pathOpacity(pvToHome)} />
        <Flow d="M498 330 C438 326 392 306 350 276" opacity={pathOpacity(flowHomeToLoads)} />
        <Flow d="M622 330 C680 326 726 306 768 276" opacity={pathOpacity(flowHomeToHp)} />
        <Flow d="M450 484 C490 420 510 388 534 352" opacity={pathOpacity(Math.max(batteryCharge, batteryDischarge))} />
        <Flow d="M676 484 C642 420 624 388 598 352" opacity={pathOpacity(Math.max(gridImport, gridExport))} />
        <Flow d="M532 142 C480 226 458 340 450 454" opacity={pathOpacity(pvExtra)} />
        <Flow d="M588 142 C638 226 660 340 670 454" opacity={pathOpacity(gridExport)} />

        <Dot href="#path-pv-home" active={pvToHome > 0.02} dur="2.4s" />
        <Dot href="#path-home-load" active={flowHomeToLoads > 0.02} dur="2.3s" />
        <Dot href="#path-home-hp" active={flowHomeToHp > 0.02} dur="2.3s" />
        <Dot href="#path-bat-home" active={Math.max(batteryCharge, batteryDischarge) > 0.02} dur="2.2s" />
        <Dot href="#path-grid-home" active={Math.max(gridImport, gridExport) > 0.02} dur="2.2s" />

        <FlowText x={572} y={214} v={pvToHome} />
        <FlowText x={414} y={300} v={flowHomeToLoads} />
        <FlowText x={700} y={300} v={flowHomeToHp} />
        <FlowText x={476} y={414} v={Math.max(batteryCharge, batteryDischarge)} />
        <FlowText x={624} y={414} v={Math.max(gridImport, gridExport)} />

        <Device x={560} y={104} icon="icon-pv" label="Fotovoltaico" value={energy.pv} scale={1.22} />
        <Device x={332} y={270} icon="icon-load" label="Carichi" value={energy.genericLoads} small />
        <Device x={788} y={270} icon="icon-hp" label="Pompa di calore" value={energy.heatPump} small />
        <Device x={446} y={508} icon="icon-battery" label="Batteria" value={Math.abs(energy.batteryPower)} suffix={`${Math.round(energy.batterySoc)}%`} small soc={energy.batterySoc} />
        <Device x={676} y={508} icon="icon-grid" label="Rete" value={Math.max(gridImport, gridExport)} suffix={gridImport > 0 ? 'import' : 'export'} scale={1.12} />

        <g transform="translate(560 336)">
          <ellipse rx="152" ry="148" fill="#e4edff" opacity="0.78" />
          <use href="#icon-house" x={-72} y={-88} width="144" height="144" />
          <text x="0" y="86" textAnchor="middle" className="home-value-main">{fmt(energy.house)}</text>
          <text x="54" y="86" className="unit-main">kW</text>
          <text x="0" y="109" textAnchor="middle" className="home-caption">Consumo casa</text>
        </g>

        <g transform="translate(940 146)" className="scene-metrics">
          <MetricRow y={0} label="Real-time Power" value={energy.house} unit="kW" />
          <MetricRow y={88} label="Installed Power" value={energy.installedKwp} unit="kWp" />
          <MetricRow y={176} label="Produzione Oggi" value={energy.pvToday} unit="kWh" />
          <MetricRow y={264} label="Consumo Oggi" value={energy.homeToday} unit="kWh" />
        </g>
      </svg>
    </div>
  )
}

function Device({ x, y, icon, label, value, suffix, small, scale = 1, soc }) {
  const s = small ? 0.94 * scale : 1 * scale
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`} className="device-lite">
      <use href={`#${icon}`} x={-34} y={-34} width="68" height="68" />
      <text x="0" y="50" textAnchor="middle" className="device-val">{fmt(value)}</text>
      <text x="30" y="50" className="device-unit">kW</text>
      <text x="0" y="70" textAnchor="middle" className="device-label">{label}</text>
      {typeof soc === 'number' ? (
        <g transform="translate(-24 78)">
          <rect x="0" y="0" width="48" height="5" rx="3" className="soc-track" />
          <rect x="0" y="0" width={`${Math.max(0, Math.min(100, soc)) * 0.48}`} height="5" rx="3" className="soc-fill" />
        </g>
      ) : null}
      {suffix ? <text x="0" y="93" textAnchor="middle" className="device-suffix">{suffix}</text> : null}
    </g>
  )
}

function MetricRow({ y, label, value, unit }) {
  return (
    <g transform={`translate(0 ${y})`}>
      <text x="0" y="0" className="metric-label">{label}</text>
      <text x="0" y="42" className="metric-value-scene">{fmt(value)}</text>
      <text x="90" y="42" className="metric-unit-scene">{unit}</text>
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
    <circle r="3.2" className="flow-dot-light">
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
      <text x="34" y="0" className="flow-unit">kW</text>
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