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

          <filter id="line-soft" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="2.1" />
          </filter>

          <filter id="icon-shadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="2.4" stdDeviation="2.2" floodColor="#90a9d4" floodOpacity="0.35" />
          </filter>

          <symbol id="icon-pv-sun" viewBox="0 0 120 120">
            <g filter="url(#icon-shadow)">
              <circle cx="76" cy="28" r="14" fill="#ffd267" />
              <path d="M58 30a18 18 0 0 1 33 -9" fill="none" stroke="#ffb74d" strokeWidth="3" />
              <polygon points="18,68 72,48 102,68 48,88" fill="#2f78c9" />
              <polygon points="20,66 74,46 104,66 50,86" fill="#54a8e8" />
              <line x1="31" y1="60" x2="85" y2="40" stroke="#dff1ff" strokeWidth="2.2" />
              <line x1="39" y1="70" x2="93" y2="50" stroke="#dff1ff" strokeWidth="2.2" />
              <line x1="47" y1="80" x2="101" y2="60" stroke="#dff1ff" strokeWidth="2.2" />
              <line x1="41" y1="56" x2="55" y2="82" stroke="#dff1ff" strokeWidth="2.2" />
              <line x1="58" y1="50" x2="72" y2="76" stroke="#dff1ff" strokeWidth="2.2" />
              <line x1="75" y1="44" x2="89" y2="70" stroke="#dff1ff" strokeWidth="2.2" />
              <polygon points="50,86 63,93 72,90 59,83" fill="#1e5ea8" />
            </g>
          </symbol>
          <symbol id="icon-pv-cloud" viewBox="0 0 120 120">
            <g filter="url(#icon-shadow)">
              <path d="M30 30c6-8 19-9 26-1 3-7 13-11 22-6 6 4 9 10 8 18 9 0 15 6 15 14s-7 14-16 14H33c-9 0-17-7-17-16s8-16 14-16z" fill="#e6effb" stroke="#a2b8dc" strokeWidth="2.2" />
              <polygon points="18,76 72,56 102,76 48,96" fill="#4f9fde" />
              <line x1="30" y1="68" x2="84" y2="48" stroke="#e5f4ff" strokeWidth="2.2" />
              <line x1="38" y1="78" x2="92" y2="58" stroke="#e5f4ff" strokeWidth="2.2" />
              <line x1="46" y1="88" x2="100" y2="68" stroke="#e5f4ff" strokeWidth="2.2" />
              <polygon points="48,96 61,103 70,100 57,93" fill="#2f7bbe" />
            </g>
          </symbol>
          <symbol id="icon-pv-moon" viewBox="0 0 120 120">
            <g filter="url(#icon-shadow)">
              <path d="M69 12c-10 5-16 15-16 26 0 16 13 29 29 29 5 0 11-1 16-4-6 10-17 16-29 16-19 0-34-15-34-34 0-15 10-28 24-33 3-1 6-1 10 0z" fill="#d9e1ee" stroke="#9cabca" strokeWidth="2.2"/>
              <polygon points="18,76 72,56 102,76 48,96" fill="#4f9fde" />
              <line x1="30" y1="68" x2="84" y2="48" stroke="#e5f4ff" strokeWidth="2.2" />
              <line x1="38" y1="78" x2="92" y2="58" stroke="#e5f4ff" strokeWidth="2.2" />
              <line x1="46" y1="88" x2="100" y2="68" stroke="#e5f4ff" strokeWidth="2.2" />
              <polygon points="48,96 61,103 70,100 57,93" fill="#2f7bbe" />
            </g>
          </symbol>

          <symbol id="icon-house" viewBox="0 0 120 120">
            <g filter="url(#icon-shadow)">
              <ellipse cx="60" cy="98" rx="30" ry="8" fill="#d9e5f9" />
              <polygon points="30,66 64,46 92,62 58,83" fill="#eef3fb" stroke="#afc0dc" strokeWidth="1.8"/>
              <polygon points="30,66 30,88 58,104 58,83" fill="#dde7f6" stroke="#afc0dc" strokeWidth="1.8"/>
              <polygon points="58,83 92,62 92,84 58,104" fill="#f7faff" stroke="#afc0dc" strokeWidth="1.8"/>
              <polygon points="24,59 58,38 98,58 64,78" fill="#7f899a" stroke="#6e7686" strokeWidth="1.8"/>
              <polygon points="58,38 98,58 88,64 50,44" fill="#5f6877"/>
              <polygon points="52,50 78,62 70,67 44,55" fill="#59a8e6" stroke="#dff4ff" strokeWidth="1.3"/>
              <line x1="56" y1="52" x2="72" y2="60" stroke="#def4ff" strokeWidth="1.2"/>
              <line x1="52" y1="56" x2="68" y2="64" stroke="#def4ff" strokeWidth="1.2"/>
              <rect x="42" y="76" width="7" height="8" fill="#8ba5ce"/>
              <rect x="80" y="70" width="7" height="12" fill="#8ba5ce"/>
            </g>
          </symbol>

          <symbol id="icon-battery" viewBox="0 0 120 120">
            <g filter="url(#icon-shadow)">
              <ellipse cx="60" cy="102" rx="18" ry="6" fill="#d9e5f9" />
              <rect x="40" y="20" width="40" height="78" rx="10" fill="#f7faff" stroke="#8ea2c5" strokeWidth="2.4"/>
              <rect x="52" y="14" width="16" height="7" rx="2" fill="#64789d"/>
              <rect x="44" y="26" width="32" height="68" rx="6" fill="#e8eef9" />
              <rect x="44" y="26" width="32" height="68" rx="6" fill="none" stroke="#bcc9df" strokeWidth="1.1" />
            </g>
          </symbol>

          <symbol id="icon-grid" viewBox="0 0 120 120">
            <g fill="none" stroke="#7f9ecb" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" filter="url(#icon-shadow)">
              <path d="M60 14L86 98H34z" />
              <path d="M42 42h36M36 56h48M30 72h60M25 88h70" />
              <path d="M60 14v84M44 30l16 14 16-14M40 64l20 18 20-18" />
            </g>
          </symbol>

          <symbol id="icon-hp" viewBox="0 0 120 120">
            <g filter="url(#icon-shadow)">
              <ellipse cx="60" cy="99" rx="22" ry="6" fill="#d9e5f9" />
              <polygon points="30,42 80,36 96,48 46,54" fill="#eef3fb" stroke="#a4bbdd" strokeWidth="1.8"/>
              <polygon points="30,42 30,82 46,92 46,54" fill="#dce7f6" stroke="#a4bbdd" strokeWidth="1.8"/>
              <polygon points="46,54 96,48 96,88 46,92" fill="#f7faff" stroke="#a4bbdd" strokeWidth="1.8"/>
              <circle cx="67" cy="69" r="12" fill="#e9f1fc" stroke="#86a7d8" strokeWidth="2.2"/>
              <circle cx="67" cy="69" r="2.5" fill="#7fa2df"/>
              <path d="M67 57v24M55 69h24M58 60l18 18M76 60l-18 18" stroke="#86a7d8" strokeWidth="1.5"/>
              <rect x="84" y="58" width="8" height="22" rx="2" fill="#d6e2f5"/>
            </g>
          </symbol>

          <symbol id="icon-rack" viewBox="0 0 120 120">
            <g filter="url(#icon-shadow)">
              <ellipse cx="60" cy="99" rx="20" ry="6" fill="#d9e5f9" />
              <polygon points="40,26 76,22 86,30 50,34" fill="#cfdbee" />
              <polygon points="40,26 40,88 50,96 50,34" fill="#bccbe2" />
              <polygon points="50,34 86,30 86,92 50,96" fill="#e9effa" />
              <rect x="54" y="39" width="28" height="9" rx="2" fill="#202735" />
              <rect x="54" y="51" width="28" height="9" rx="2" fill="#202735" />
              <rect x="54" y="63" width="28" height="9" rx="2" fill="#202735" />
              <rect x="54" y="75" width="28" height="9" rx="2" fill="#202735" />
              <circle cx="57" cy="43.5" r="1.6" fill="#34c0ff"/>
              <circle cx="57" cy="55.5" r="1.6" fill="#34c0ff"/>
              <circle cx="57" cy="67.5" r="1.6" fill="#34c0ff"/>
              <circle cx="57" cy="79.5" r="1.6" fill="#34c0ff"/>
            </g>
          </symbol>

          <symbol id="icon-wallbox" viewBox="0 0 120 120">
            <g filter="url(#icon-shadow)">
              <ellipse cx="60" cy="100" rx="20" ry="6" fill="#d9e5f9" />
              <rect x="36" y="24" width="40" height="62" rx="12" fill="#f8fbff" stroke="#8b97ab" strokeWidth="2.6"/>
              <rect x="48" y="36" width="16" height="8" rx="4" fill="#d3dcea"/>
              <path d="M76 40c12 0 20 9 20 21v20" fill="none" stroke="#8b97ab" strokeWidth="2.8" />
              <path d="M96 81c-9 0-14 7-17 15" fill="none" stroke="#8b97ab" strokeWidth="2.8" />
              <path d="M56 50l-8 11h9l-6 10 13-14h-8l5-7z" fill="#6f7f9c" />
            </g>
          </symbol>

          <symbol id="icon-load" viewBox="0 0 120 120">
            <g filter="url(#icon-shadow)">
              <ellipse cx="60" cy="98" rx="19" ry="5.5" fill="#d9e5f9" />
              <circle cx="60" cy="56" r="21" fill="#fff9de" stroke="#e3d08d" strokeWidth="2.2"/>
              <path d="M63 40L52 60h12l-6 18 16-23H61z" fill="#7fa2df" />
              <path d="M60 20v8M42 28l5 6M78 28l-5 6" stroke="#e3d08d" strokeWidth="2" strokeLinecap="round"/>
            </g>
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
