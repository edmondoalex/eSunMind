(() => {
  // Simulazione config/hass (senza dipendenze Home Assistant)
  const config = {
    solar: { animation_speed: 6, max_power: 7000, invert_flow: false, color: '#f59e0b' },
    battery: { animation_speed: 8, max_power: 5000, invert_flow: false, color: '#a855f7' },
    grid: { animation_speed: 9, max_power: 8000, invert_flow: false, color: '#06b6d4' },
    load: { animation_speed: 6, max_power: 9000, invert_flow: false, color: '#cbd5e1' },
    layout: {
      // Coordinate modificabili via CSS variables in styles.css
      solar: { x: 200, y: 220 },
      inverter: { x: 600, y: 290 },
      battery: { x: 600, y: 500 },
      load: { x: 600, y: 380 },
      grid: { x: 980, y: 290 }
    },
    dataSource: {
      enabled: true,
      endpoint: '../api/data',
      intervalMs: 2000
    }
  };

  const hass = { states: {} };

  const state = {
    solarPower: 0,
    pv1Power: 0,
    pv2Power: 0,
    inverterPower: 0,
    batteryPower: 0,
    batterySoc: 0,
    loadPower: 0,
    gridPower: 0,
  };

  const fmt = (w) => {
    const n = Number(w) || 0;
    if (Math.abs(n) >= 1000) return `${(n / 1000).toFixed(2)} kW`;
    return `${Math.round(n)} W`;
  };

  // Logica speed presa dal repo: speed = base - (base-1)*(abs(power)/maxPower)
  const calcDuration = (baseSpeed, powerAbs, maxPower) => {
    const safeMax = Math.max(1, Number(maxPower) || 1);
    const ratio = Math.min(1, Math.abs(powerAbs) / safeMax);
    const speed = baseSpeed - (baseSpeed - 1) * ratio;
    return Math.max(1, Number(speed.toFixed(3)));
  };

  // Logica inversione direzione stile invertKeyPoints (0;1 <-> 1;0)
  const dir = (forward, invertFlow = false) => {
    const base = forward ? '0;1' : '1;0';
    return invertFlow ? base.split(';').reverse().join(';') : base;
  };

  const icons = {
    sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>',
    zap: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h7l-1 8 10-12h-7l1-8z"/></svg>',
    battery: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="18" height="10" rx="2"/><path d="M22 11v2"/></svg>',
    cpu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/></svg>',
    home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 10.5L12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/></svg>',
    tower: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l4 20M12 2L8 22M4 12h16M6 18h12"/></svg>'
  };

  function mountIcons() {
    document.querySelectorAll('[data-icon]').forEach((el) => {
      const k = el.getAttribute('data-icon');
      if (k && icons[k]) el.innerHTML = icons[k];
    });
  }

  function makeFlowPath(id, d, color, width = 3) {
    const ns = 'http://www.w3.org/2000/svg';
    const g = document.createElementNS(ns, 'g');
    g.setAttribute('data-flow-id', id);

    const base = document.createElementNS(ns, 'path');
    base.setAttribute('d', d);
    base.setAttribute('class', 'flow-path');
    base.setAttribute('stroke', color);
    base.setAttribute('stroke-width', String(width));
    base.setAttribute('filter', `drop-shadow(0 0 10px ${color})`);

    const trail = document.createElementNS(ns, 'path');
    trail.setAttribute('d', d);
    trail.setAttribute('class', 'flow-trail');
    trail.style.color = color;

    g.appendChild(base);
    g.appendChild(trail);
    return { g, trail };
  }

  const flows = {};

  function readCssNumberVar(name, fallback) {
    const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    const n = Number(v);
    return Number.isFinite(n) ? n : fallback;
  }

  function syncLayoutFromCssVars() {
    config.layout.solar.x = readCssNumberVar('--solar-x', config.layout.solar.x);
    config.layout.solar.y = readCssNumberVar('--solar-y', config.layout.solar.y);
    config.layout.inverter.x = readCssNumberVar('--inverter-x', config.layout.inverter.x);
    config.layout.inverter.y = readCssNumberVar('--inverter-y', config.layout.inverter.y);
    config.layout.battery.x = readCssNumberVar('--battery-x', config.layout.battery.x);
    config.layout.battery.y = readCssNumberVar('--battery-y', config.layout.battery.y);
    config.layout.load.x = readCssNumberVar('--load-x', config.layout.load.x);
    config.layout.load.y = readCssNumberVar('--load-y', config.layout.load.y);
    config.layout.grid.x = readCssNumberVar('--grid-x', config.layout.grid.x);
    config.layout.grid.y = readCssNumberVar('--grid-y', config.layout.grid.y);
  }

  function initFlows() {
    syncLayoutFromCssVars();
    const svg = document.getElementById('flow-layer');
    svg.innerHTML = '';

    const { solar, inverter, battery, load, grid } = config.layout;
    const defs = [
      ['solar_to_inverter', `M ${solar.x} ${solar.y} C 330 220, 420 260, ${inverter.x} ${inverter.y}`, config.solar.color],
      ['battery_to_inverter', `M ${battery.x} ${battery.y} C ${battery.x} 460, ${inverter.x} 430, ${inverter.x} ${inverter.y}`, config.battery.color],
      ['grid_to_inverter', `M ${grid.x} ${grid.y} C 860 290, 760 290, ${inverter.x} ${inverter.y}`, config.grid.color],
      ['inverter_to_load', `M ${inverter.x} ${inverter.y} C ${inverter.x} 330, ${load.x} 340, ${load.x} ${load.y}`, config.load.color],
    ];

    defs.forEach(([id, d, color]) => {
      const f = makeFlowPath(id, d, color, 2.8);
      svg.appendChild(f.g);
      flows[id] = f;
    });
  }

  function applyFlowDirectionAndSpeed(flowId, power, baseSpeed, maxPower, invertFlow = false, naturalForward = true) {
    const f = flows[flowId];
    if (!f) return;

    const absP = Math.abs(Number(power) || 0);
    const show = absP > 1;
    f.g.style.display = show ? 'block' : 'none';
    if (!show) return;

    const forward = naturalForward ? power >= 0 : power < 0;
    const keyPoints = dir(forward, invertFlow);
    const duration = calcDuration(baseSpeed, absP, maxPower);

    // Simula invertKeyPoints modificando segno dashoffset animation
    f.trail.style.animationDuration = `${duration}s`;
    f.trail.style.animationDirection = keyPoints === '0;1' ? 'normal' : 'reverse';
  }

  function render() {
    document.getElementById('solar-value').textContent = fmt(state.solarPower);
    document.getElementById('pv1-value').textContent = fmt(state.pv1Power);
    document.getElementById('pv2-value').textContent = fmt(state.pv2Power);
    document.getElementById('inverter-value').textContent = fmt(state.inverterPower);
    document.getElementById('battery-value').textContent = fmt(state.batteryPower);
    document.getElementById('battery-soc').textContent = `SOC ${Math.round(state.batterySoc)}%`;
    document.getElementById('load-value').textContent = fmt(state.loadPower);
    document.getElementById('grid-value').textContent = fmt(state.gridPower);

    // Flow directions compatibili con logica Sunsynk
    // solar: positivo => verso inverter
    applyFlowDirectionAndSpeed('solar_to_inverter', state.solarPower, config.solar.animation_speed, config.solar.max_power, config.solar.invert_flow, true);

    // battery: default positivo = scarica verso inverter, negativo = carica
    // invert_flow ribalta (stile repo)
    applyFlowDirectionAndSpeed('battery_to_inverter', state.batteryPower, config.battery.animation_speed, config.battery.max_power, config.battery.invert_flow, true);

    // grid: positivo = import da rete verso inverter; negativo = export
    applyFlowDirectionAndSpeed('grid_to_inverter', state.gridPower, config.grid.animation_speed, config.grid.max_power, config.grid.invert_flow, true);

    // load: assume positivo verso carico
    applyFlowDirectionAndSpeed('inverter_to_load', state.loadPower, config.load.animation_speed, config.load.max_power, config.load.invert_flow, true);

    document.getElementById('status-line').textContent = `S:${fmt(state.solarPower)} | B:${fmt(state.batteryPower)} | G:${fmt(state.gridPower)} | L:${fmt(state.loadPower)}`;
    document.getElementById('debug-line').textContent = `solar:${calcDuration(config.solar.animation_speed, state.solarPower, config.solar.max_power)}s battery:${calcDuration(config.battery.animation_speed, state.batteryPower, config.battery.max_power)}s grid:${calcDuration(config.grid.animation_speed, state.gridPower, config.grid.max_power)}s`;
  }

  // API pubblica richiesta
  window.setPowerData = function setPowerData(json) {
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

    if (json?.hassStates && typeof json.hassStates === 'object') {
      hass.states = { ...hass.states, ...json.hassStates };
    }

    render();
  };

  // API opzionale per cambiare config runtime
  window.setDashboardConfig = function setDashboardConfig(partial) {
    if (!partial || typeof partial !== 'object') return;
    Object.assign(config.solar, partial.solar || {});
    Object.assign(config.battery, partial.battery || {});
    Object.assign(config.grid, partial.grid || {});
    Object.assign(config.load, partial.load || {});
    Object.assign(config.layout, partial.layout || {});
    initFlows();
    render();
  };

  window.__sunsynkStandalone = { config, hass, state };

  mountIcons();
  initFlows();

  // Dati demo iniziali
  setPowerData({
    solarPower: 5370,
    pv1Power: 2950,
    pv2Power: 2420,
    inverterPower: 1160,
    batteryPower: -3040,
    batterySoc: 26,
    loadPower: 1160,
    gridPower: 1150,
  });

  let apiTimer = null;
  async function pollApiData() {
    if (!config.dataSource.enabled) return;
    try {
      const r = await fetch(config.dataSource.endpoint, { cache: 'no-store' });
      if (!r.ok) throw new Error(`api_data_http_${r.status}`);
      const j = await r.json();
      const n = j?.energy?.normalized || {};
      setPowerData({
        solarPower: Number(n.pv_power_w || 0),
        pv1Power: Number(n.pv_power_w || 0) * 0.55,
        pv2Power: Number(n.pv_power_w || 0) * 0.45,
        inverterPower: Number(n.home_power_w || 0),
        batteryPower: Number(n.battery_power_w || 0),
        batterySoc: Number(n.battery_soc_pct || 0),
        loadPower: Number(n.home_power_w || 0),
        gridPower: Number(n.grid_power_w || 0),
      });
    } catch (_) {
      // Keep last known values on temporary API failures.
    }
  }

  if (config.dataSource.enabled) {
    pollApiData();
    apiTimer = setInterval(pollApiData, config.dataSource.intervalMs);
    window.addEventListener('beforeunload', () => {
      if (apiTimer) clearInterval(apiTimer);
    });
  }
})();
