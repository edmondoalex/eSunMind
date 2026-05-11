import React from 'react'

export default function EnergyScene({ energy }) {
  const pvToHome = Math.max(0, Math.min(energy.pv, energy.house))
  const pvExtra = Math.max(0, energy.pv - energy.house)
  const batteryCharge = Math.max(0, energy.batteryPower)
  const batteryDischarge = Math.max(0, -energy.batteryPower)
  const gridImport = Math.max(0, energy.gridImport)
  const gridExport = Math.max(0, energy.gridExport)

  const homeAuxLoads = Math.max(0, energy.genericLoads)
  const heatPumpLoad = Math.max(0, energy.heatPump)
  const rackLoad = Math.max(0, homeAuxLoads * 0.28)
  const wallboxLoad = Math.max(0, homeAuxLoads * 0.24)
  const houseLoads = Math.max(0, homeAuxLoads - rackLoad - wallboxLoad)

  const pathOpacity = (v) => (v <= 0.01 ? 0.16 : Math.min(0.95, 0.34 + v * 0.16))
  const pvState = energy.pv > 1.8 ? 'sun' : energy.pv > 0.15 ? 'cloud' : 'moon'
  const pvSign = pvExtra > 0.01 ? '+' : '-'

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

          <symbol id="icon-pv-sun" viewBox="0 0 120 120">
            <g fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="60" cy="28" r="16" fill="#ffcb54" stroke="#f0b13d" />
              <path d="M18 28h22M80 28h22M60 6v10M60 40v10M30 12l8 8M90 12l-8 8" stroke="#f1b545" />
              <polygon points="20,64 80,46 104,76 44,94" fill="#f5f8ff" stroke="#7fa2df" />
              <path d="M32 60 L86 44 M40 72 L94 56 M48 84 L102 68" stroke="#7fa2df" />
              <path d="M42 56 L50 86 M58 51 L66 81 M74 47 L82 77" stroke="#7fa2df" />
            </g>
          </symbol>
          <symbol id="icon-pv-cloud" viewBox="0 0 120 120">
            <g fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <path d="M30 28c5-8 18-9 25-2 3-7 13-10 21-5 6 3 9 10 8 17 8 0 14 6 14 14s-7 14-15 14H31c-9 0-16-7-16-16s7-16 15-16z" fill="#e4ecfa" stroke="#93add6" />
              <polygon points="20,74 80,56 104,86 44,104" fill="#f5f8ff" stroke="#7fa2df" />
              <path d="M32 70 L86 54 M40 82 L94 66 M48 94 L102 78" stroke="#7fa2df" />
              <path d="M42 66 L50 96 M58 61 L66 91 M74 57 L82 87" stroke="#7fa2df" />
            </g>
          </symbol>
          <symbol id="icon-pv-moon" viewBox="0 0 120 120">
            <g fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <path d="M66 9c-10 4-17 14-17 26 0 17 14 31 31 31 6 0 12-2 17-5-6 10-17 16-29 16-19 0-35-16-35-35 0-15 10-29 24-33 3-1 6-1 9 0z" fill="#d8deec" stroke="#99a6c2"/>
              <polygon points="20,74 80,56 104,86 44,104" fill="#f5f8ff" stroke="#7fa2df" />
              <path d="M32 70 L86 54 M40 82 L94 66 M48 94 L102 78" stroke="#7fa2df" />
              <path d="M42 66 L50 96 M58 61 L66 91 M74 57 L82 87" stroke="#7fa2df" />
            </g>
          </symbol>

          <symbol id="icon-house" viewBox="0 0 120 120">
            <path d="M18 58 L60 20 L102 58" fill="none" stroke="#3d4451" strokeWidth="4" strokeLinecap="round" />
            <path d="M46 58 L60 90 L74 58" fill="none" stroke="#c8b67a" strokeWidth="4" strokeLinecap="round" />
            <rect x="54" y="44" width="12" height="12" fill="none" stroke="#6f7783" strokeWidth="2" />
            <path d="M60 44V56M54 50H66" stroke="#6f7783" strokeWidth="1.8" />
          </symbol>

          <symbol id="icon-battery" viewBox="0 0 120 120">
            <rect x="38" y="20" width="44" height="78" rx="8" fill="#fff" stroke="#242932" strokeWidth="3"/>
            <rect x="52" y="14" width="16" height="7" rx="2" fill="#242932"/>
          </symbol>

          <symbol id="icon-grid" viewBox="0 0 120 120">
            <g fill="none" stroke="#1f2430" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M60 12L92 104H28z" />
              <path d="M35 42h50M30 58h60M25 76h70" />
              <path d="M60 12v92" />
              <path d="M8 52c6 0 10 6 14 6s8-6 14-6" strokeWidth="2" />
              <path d="M84 58c5 0 9 6 13 6s8-6 13-6" strokeWidth="2" />
            </g>
          </symbol>

          <symbol id="icon-hp" viewBox="0 0 120 120">
            <rect x="26" y="34" width="68" height="48" rx="10" fill="#fff" stroke="#8aa6d8" strokeWidth="2.6"/>
            <circle cx="54" cy="58" r="13" fill="none" stroke="#8aa6d8" strokeWidth="2.3"/>
            <path d="M54 45v26M41 58h26" stroke="#8aa6d8" strokeWidth="2.1" />
            <rect x="72" y="44" width="14" height="28" rx="2" fill="none" stroke="#8aa6d8" strokeWidth="2"/>
            <rect x="40" y="85" width="38" height="4" rx="2" fill="#c4d4f0"/>
          </symbol>

          <symbol id="icon-rack" viewBox="0 0 120 120">
            <rect x="36" y="18" width="48" height="84" rx="5" fill="#eef2fb" stroke="#4a5160" strokeWidth="2.4"/>
            <rect x="40" y="28" width="40" height="10" rx="2" fill="#1d2330"/>
            <rect x="40" y="44" width="40" height="10" rx="2" fill="#1d2330"/>
            <rect x="40" y="60" width="40" height="10" rx="2" fill="#1d2330"/>
            <rect x="40" y="76" width="40" height="10" rx="2" fill="#1d2330"/>
            <circle cx="44" cy="33" r="1.5" fill="#30b8ff"/>
            <circle cx="44" cy="49" r="1.5" fill="#30b8ff"/>
            <circle cx="44" cy="65" r="1.5" fill="#30b8ff"/>
            <circle cx="44" cy="81" r="1.5" fill="#30b8ff"/>
          </symbol>

          <symbol id="icon-wallbox" viewBox="0 0 120 120">
            <rect x="32" y="24" width="44" height="62" rx="12" fill="#fff" stroke="#6e7480" strokeWidth="3"/>
            <path d="M76 40c12 0 20 9 20 21v20" fill="none" stroke="#6e7480" strokeWidth="3" />
            <path d="M96 81c-9 0-14 7-17 15" fill="none" stroke="#6e7480" strokeWidth="3" />
            <path d="M53 50l-8 11h9l-6 10 13-14h-8l5-7z" fill="#6e7480" />
          </symbol>

          <symbol id="icon-load" viewBox="0 0 120 120">
            <path d="M63 28L45 60h17l-5 32 18-34H58z" fill="#7fa2df" />
            <circle cx="34" cy="34" r="8" fill="none" stroke="#7fa2df" strokeWidth="2" />
          </symbol>

          {pathDef('path-pv-home', 'M560 132 C560 194 560 232 560 278')}
          {pathDef('path-home-load', 'M498 330 C438 326 392 306 340 264')}
          {pathDef('path-home-rack', 'M498 350 C430 362 380 388 346 430')}
          {pathDef('path-home-wallbox', 'M620 350 C684 366 732 394 766 434')}
          {pathDef('path-home-hp', 'M622 330 C680 326 726 306 780 266')}
          {pathDef('path-bat-home', 'M450 484 C490 420 510 388 534 352')}
          {pathDef('path-grid-home', 'M676 484 C642 420 624 388 598 352')}
          {pathDef('path-pv-bat', 'M532 142 C480 226 458 340 450 454')}
          {pathDef('path-pv-grid', 'M588 142 C638 226 660 340 670 454')}
        </defs>

        <rect x="0" y="0" width="1200" height="675" rx="24" fill="url(#scene-bg)" />

        <Flow d="M560 132 C560 194 560 232 560 278" opacity={pathOpacity(pvToHome)} />
        <Flow d="M498 330 C438 326 392 306 340 264" opacity={pathOpacity(houseLoads)} />
        <Flow d="M498 350 C430 362 380 388 346 430" opacity={pathOpacity(rackLoad)} />
        <Flow d="M620 350 C684 366 732 394 766 434" opacity={pathOpacity(wallboxLoad)} />
        <Flow d="M622 330 C680 326 726 306 780 266" opacity={pathOpacity(heatPumpLoad)} />
        <Flow d="M450 484 C490 420 510 388 534 352" opacity={pathOpacity(Math.max(batteryCharge, batteryDischarge))} />
        <Flow d="M676 484 C642 420 624 388 598 352" opacity={pathOpacity(Math.max(gridImport, gridExport))} />
        <Flow d="M532 142 C480 226 458 340 450 454" opacity={pathOpacity(pvExtra)} />
        <Flow d="M588 142 C638 226 660 340 670 454" opacity={pathOpacity(gridExport)} />

        <Dot href="#path-pv-home" active={pvToHome > 0.02} dur="2.4s" />
        <Dot href="#path-home-load" active={houseLoads > 0.02} dur="2.3s" />
        <Dot href="#path-home-rack" active={rackLoad > 0.02} dur="2.4s" />
        <Dot href="#path-home-wallbox" active={wallboxLoad > 0.02} dur="2.4s" />
        <Dot href="#path-home-hp" active={heatPumpLoad > 0.02} dur="2.3s" />
        <Dot href="#path-bat-home" active={Math.max(batteryCharge, batteryDischarge) > 0.02} dur="2.2s" />
        <Dot href="#path-grid-home" active={Math.max(gridImport, gridExport) > 0.02} dur="2.2s" />

        <FlowText x={572} y={214} v={pvToHome} />
        <FlowText x={406} y={286} v={houseLoads} />
        <FlowText x={398} y={406} v={rackLoad} />
        <FlowText x={710} y={404} v={wallboxLoad} />
        <FlowText x={708} y={286} v={heatPumpLoad} />
        <FlowText x={476} y={414} v={Math.max(batteryCharge, batteryDischarge)} />
        <FlowText x={624} y={414} v={Math.max(gridImport, gridExport)} />

        <Device x={560} y={102} icon={`icon-pv-${pvState}`} label={`Fotovoltaico ${pvSign}`} value={energy.pv} scale={1.22} />
        <Device x={322} y={258} icon="icon-load" label="Carichi Casa" value={houseLoads} small />
        <Device x={324} y={448} icon="icon-rack" label="Rack Dati" value={rackLoad} small />
        <Device x={792} y={258} icon="icon-hp" label="Pompa di calore" value={heatPumpLoad} small />
        <Device x={790} y={450} icon="icon-wallbox" label="Wall Box" value={wallboxLoad} small />
        <BatteryDevice x={446} y={510} value={Math.abs(energy.batteryPower)} soc={energy.batterySoc} />
        <Device x={676} y={510} icon="icon-grid" label="Rete" value={Math.max(gridImport, gridExport)} suffix={gridImport > 0 ? 'import' : 'export'} scale={1.12} />

        <g transform="translate(560 336)">
          <ellipse rx="152" ry="148" fill="#e4edff" opacity="0.78" />
          <use href="#icon-house" x={-72} y={-92} width="144" height="144" />
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

function Device({ x, y, icon, label, value, suffix, small, scale = 1 }) {
  const s = small ? 0.93 * scale : 1 * scale
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`} className="device-lite">
      <use href={`#${icon}`} x={-34} y={-34} width="68" height="68" />
      <text x="0" y="50" textAnchor="middle" className="device-val">{fmt(value)}</text>
      <text x="30" y="50" className="device-unit">kW</text>
      <text x="0" y="70" textAnchor="middle" className="device-label">{label}</text>
      {suffix ? <text x="0" y="86" textAnchor="middle" className="device-suffix">{suffix}</text> : null}
    </g>
  )
}

function BatteryDevice({ x, y, value, soc }) {
  const level = Math.max(0, Math.min(100, Number(soc || 0)))
  const color = level >= 75 ? '#65c81d' : level >= 45 ? '#d2df22' : level >= 20 ? '#f3a20b' : '#ec3f3f'
  const fillHeight = 56 * (level / 100)
  const fillY = 30 + (56 - fillHeight)

  return (
    <g transform={`translate(${x} ${y})`} className="device-lite battery-live">
      <use href="#icon-battery" x={-34} y={-34} width="68" height="68" />
      <rect x={-11} y={fillY - 34} width="22" height={fillHeight} rx="3" fill={color} opacity="0.9" />
      <text x="0" y="50" textAnchor="middle" className="device-val">{fmt(value)}</text>
      <text x="30" y="50" className="device-unit">kW</text>
      <text x="0" y="70" textAnchor="middle" className="device-label">Batteria</text>
      <text x="0" y="86" textAnchor="middle" className="device-suffix">{Math.round(level)}%</text>
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
