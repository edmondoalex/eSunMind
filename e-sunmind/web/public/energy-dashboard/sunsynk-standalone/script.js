(() => {
  const cfg = {
    solar: { animation_speed: 6, max_power: 7000, invert_flow: false, color: '#f59e0b' },
    battery: { animation_speed: 8, max_power: 5000, invert_flow: false, color: '#a855f7' },
    grid: { animation_speed: 9, max_power: 8000, invert_flow: false, color: '#06b6d4' },
    load: { animation_speed: 6, max_power: 9000, invert_flow: false, color: '#cbd5e1' },
    endpoint: '../api/data',
    poll_ms: 2000,
  };

  const state = { solarPower: 0, pv1Power: 0, pv2Power: 0, inverterPower: 0, batteryPower: 0, batterySoc: 0, loadPower: 0, gridPower: 0 };

  const fmt = (w) => Math.abs(w) >= 1000 ? `${(w / 1000).toFixed(2)} kW` : `${Math.round(w)} W`;
  const invPts = (s) => s.split(';').reverse().join(';');
  const duration = (base, power, maxPower) => {
    const p = Math.abs(Number(power) || 0);
    const m = Math.max(1, Number(maxPower) || 1);
    const d = base - (base - 1) * Math.min(1, p / m);
    return Math.max(1, Number(d.toFixed(3)));
  };

  const NS = 'http://www.w3.org/2000/svg';
  const flowsRoot = document.getElementById('flows');
  const flowDefs = {
    // Path presi dal layout full del repo
    solar: { id: 'solar-line', d: 'M 155 250 L 96 250 Q 86 250 86 240 L 86 192', color: cfg.solar.color },
    battery: { id: 'bat-line', d: 'M 155 280 L 96 280 Q 86 280 86 290 L 86 297', color: cfg.battery.color },
    gridA: { id: 'grid-line', d: 'M 304 188 L 411 188 Q 421 188 421 198 L421 265', color: cfg.grid.color },
    gridB: { id: 'grid2-line', d: 'M215 187 234 187', color: cfg.grid.color },
    load: { id: 'load-line', d: 'M 304 118 L 386 118', color: cfg.load.color },
  };

  const runtime = {};

  function makePath(id, d, color) {
    const p = document.createElementNS(NS, 'path');
    p.setAttribute('id', id);
    p.setAttribute('d', d);
    p.setAttribute('class', 'flow-line');
    p.setAttribute('stroke', color);
    p.setAttribute('stroke-width', '2.8');
    p.setAttribute('filter', `drop-shadow(0 0 6px ${color})`);
    return p;
  }

  function makeDot(id, color) {
    const c = document.createElementNS(NS, 'circle');
    c.setAttribute('id', id);
    c.setAttribute('r', '4');
    c.setAttribute('fill', color);
    c.setAttribute('class', 'dot');
    return c;
  }

  function setDotAnim(dot, href, dur, keyPoints) {
    while (dot.firstChild) dot.removeChild(dot.firstChild);
    const am = document.createElementNS(NS, 'animateMotion');
    am.setAttribute('dur', `${dur}s`);
    am.setAttribute('repeatCount', 'indefinite');
    am.setAttribute('keyPoints', keyPoints);
    am.setAttribute('keyTimes', '0;1');
    am.setAttribute('calcMode', 'linear');
    const mp = document.createElementNS(NS, 'mpath');
    mp.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', `#${href}`);
    mp.setAttribute('href', `#${href}`);
    am.appendChild(mp);
    dot.appendChild(am);
  }

  function initFlows() {
    flowsRoot.innerHTML = '';
    Object.entries(flowDefs).forEach(([k, v]) => {
      const g = document.createElementNS(NS, 'g');
      const path = makePath(v.id, v.d, v.color);
      const dotA = makeDot(`${v.id}-dot-a`, v.color);
      const dotB = makeDot(`${v.id}-dot-b`, v.color);
      g.append(path, dotA, dotB);
      flowsRoot.appendChild(g);
      runtime[k] = { path, dotA, dotB, lineId: v.id };
    });
  }

  function applyFlow(key, power, baseSpeed, maxPower, invertFlow, dischargeKey = '1;0', chargeKey = '0;1') {
    const f = runtime[key]; if (!f) return;
    const p = Number(power) || 0;
    const show = Math.abs(p) > 1;
    f.path.style.display = show ? '' : 'none';
    f.dotA.style.display = 'none';
    f.dotB.style.display = 'none';
    if (!show) return;

    const d = duration(baseSpeed, p, maxPower);
    const kpPos = invertFlow ? invPts(dischargeKey) : dischargeKey;
    const kpNeg = invertFlow ? invPts(chargeKey) : chargeKey;

    if (p > 0) {
      f.dotA.style.display = '';
      setDotAnim(f.dotA, f.lineId, d, kpPos);
    } else {
      f.dotB.style.display = '';
      setDotAnim(f.dotB, f.lineId, d, kpNeg);
    }
  }

  function render() {
    document.getElementById('solar_val').textContent = fmt(state.solarPower);
    document.getElementById('pv1_val').textContent = fmt(state.pv1Power);
    document.getElementById('pv2_val').textContent = fmt(state.pv2Power);
    document.getElementById('inv_val').textContent = fmt(state.inverterPower);
    document.getElementById('bat_val').textContent = fmt(state.batteryPower);
    document.getElementById('bat_soc').textContent = `SOC ${Math.round(state.batterySoc)}%`;
    document.getElementById('load_val').textContent = fmt(state.loadPower);
    document.getElementById('grid_val').textContent = fmt(state.gridPower);

    applyFlow('solar', state.solarPower, cfg.solar.animation_speed, cfg.solar.max_power, cfg.solar.invert_flow, '1;0', '0;1');
    applyFlow('battery', state.batteryPower, cfg.battery.animation_speed, cfg.battery.max_power, cfg.battery.invert_flow, '1;0', '0;1');
    applyFlow('gridA', state.gridPower, cfg.grid.animation_speed, cfg.grid.max_power, cfg.grid.invert_flow, '1;0', '0;1');
    applyFlow('gridB', state.gridPower, cfg.grid.animation_speed, cfg.grid.max_power, cfg.grid.invert_flow, '1;0', '0;1');
    applyFlow('load', state.loadPower, cfg.load.animation_speed, cfg.load.max_power, cfg.load.invert_flow, '0;1', '1;0');
  }

  window.setPowerData = (json) => {
    Object.assign(state, {
      solarPower: Number(json?.solarPower ?? state.solarPower),
      pv1Power: Number(json?.pv1Power ?? state.pv1Power),
      pv2Power: Number(json?.pv2Power ?? state.pv2Power),
      inverterPower: Number(json?.inverterPower ?? state.inverterPower),
      batteryPower: Number(json?.batteryPower ?? state.batteryPower),
      batterySoc: Number(json?.batterySoc ?? state.batterySoc),
      loadPower: Number(json?.loadPower ?? state.loadPower),
      gridPower: Number(json?.gridPower ?? state.gridPower),
    });
    render();
  };

  async function pollApi() {
    try {
      const r = await fetch(cfg.endpoint, { cache: 'no-store' });
      if (!r.ok) return;
      const j = await r.json();
      const n = j?.energy?.normalized || {};
      const pv = Number(n.pv_power_w || 0);
      setPowerData({
        solarPower: pv,
        pv1Power: pv * 0.52,
        pv2Power: pv * 0.48,
        inverterPower: Number(n.home_power_w || 0),
        batteryPower: Number(n.battery_power_w || 0),
        batterySoc: Number(n.battery_soc_pct || 0),
        loadPower: Number(n.home_power_w || 0),
        gridPower: Number(n.grid_power_w || 0),
      });
    } catch {}
  }

  initFlows();
  setPowerData({ solarPower: 5370, pv1Power: 2792, pv2Power: 2578, inverterPower: 1160, batteryPower: -3040, batterySoc: 26, loadPower: 1160, gridPower: 1150 });
  pollApi();
  setInterval(pollApi, cfg.poll_ms);
})();
