export function simulateEnergy(prev) {
  const t = Date.now() / 1000

  const daylight = Math.max(0, Math.sin((t % 90) / 90 * Math.PI))
  const pv = clamp(0, 10.5, daylight * 8.8 + rand(-0.25, 0.35))

  const baseLoads = clamp(0.4, 2.4, 1.1 + Math.sin(t / 9) * 0.5 + rand(-0.2, 0.25))
  const heatPump = Math.sin(t / 13) > 0.3 ? clamp(0.3, 2.0, 1.1 + rand(-0.3, 0.3)) : 0
  const house = Math.max(0.4, baseLoads + heatPump)

  const net = pv - house
  let batterySoc = clamp(8, 98, toNum(prev.batterySoc) || 62)
  let batteryPower = 0

  if (net > 0) {
    batteryPower = clamp(0, 3.4, net * 0.62)
    batterySoc = clamp(8, 98, batterySoc + batteryPower * 0.08)
  } else {
    batteryPower = -clamp(0, 3.4, Math.abs(net) * 0.56)
    batterySoc = clamp(8, 98, batterySoc + batteryPower * 0.06)
  }

  const gridPower = house - pv - (-batteryPower)
  const gridImport = Math.max(0, gridPower)
  const gridExport = Math.max(0, -gridPower)

  return {
    pv,
    house,
    batteryPower,
    batterySoc,
    gridImport,
    gridExport,
    heatPump,
    genericLoads: baseLoads,
    installedKwp: toNum(prev.installedKwp) || 6.6,
    pvToday: Math.max(0, toNum(prev.pvToday) + pv / 1800),
    homeToday: Math.max(0, toNum(prev.homeToday) + house / 1800)
  }
}

function clamp(min, max, value) {
  return Math.max(min, Math.min(max, value))
}

function rand(min, max) {
  return Math.random() * (max - min) + min
}

function toNum(v) {
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}