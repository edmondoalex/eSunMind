export function simulateEnergy(prev) {
  const t = Date.now() / 1000
  const pv = clamp(0, 11, 4.8 + Math.sin(t / 14) * 3.2 + rand(-0.35, 0.35))
  const heatPump = Math.sin(t / 11) > 0.2 ? clamp(0.5, 2.4, 1.3 + rand(-0.3, 0.3)) : 0
  const genericLoads = clamp(0.4, 3.8, 1.2 + Math.sin(t / 8) * 0.9 + rand(-0.35, 0.35))
  const house = Math.max(0.4, heatPump + genericLoads)

  const net = pv - house
  let batteryPower = 0
  let batterySoc = prev.batterySoc

  if (net > 0) {
    batteryPower = clamp(0, 3.2, net * 0.62)
    batterySoc = clamp(10, 98, batterySoc + batteryPower * 0.09)
  } else {
    batteryPower = -clamp(0, 3.2, Math.abs(net) * 0.5)
    batterySoc = clamp(10, 98, batterySoc + batteryPower * 0.06)
  }

  const grid = house - pv - (-batteryPower)
  const gridImport = Math.max(0, grid)
  const gridExport = Math.max(0, -grid)

  return {
    pv,
    house,
    heatPump,
    genericLoads,
    batteryPower,
    batterySoc,
    gridImport,
    gridExport,
    pvToday: Math.max(0, (prev.pvToday || 0) + pv / 1800),
    homeToday: Math.max(0, (prev.homeToday || 0) + house / 1800)
  }
}

function rand(min, max) {
  return Math.random() * (max - min) + min
}

function clamp(min, max, value) {
  return Math.max(min, Math.min(max, value))
}
