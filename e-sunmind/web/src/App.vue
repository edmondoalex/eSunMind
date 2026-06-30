<template>
  <div class="wrap">
    <transition name="splash-fade">
      <div v-if="showSplash" class="splash-screen">
        <img :src="(tab==='user_public' || tab==='energy_public') ? logoEtende : logoMain" alt="Splash logo" class="splash-logo" />
      </div>
    </transition>

    <header class="topbar" v-if="tab!=='user_public' && tab!=='energy_public'">
      <div class="brand">
        <img :src="logoMain" alt="e-SunMind logo" class="brand-logo" />
        <span>e-SunMind <small class="brand-version">v{{ appVersion }}</small></span>
      </div>
      <div class="actions">
        <button class="btn ghost" :class="{active: tab==='user'}" @click="tab='user'">UI Admin</button>
        <a class="btn ghost" href="?view=user">UI User</a>
        <button class="btn ghost" :class="{active: tab==='energy'}" @click="tab='energy'">Energy</button>
        <button class="btn ghost" :class="{active: tab==='energy_setup'}" @click="tab='energy_setup'">Energy Setup</button>
        <button class="btn ghost" :class="{active: tab==='livoltek'}" @click="tab='livoltek'">Livoltek</button>
        <button class="btn ghost" :class="{active: tab==='tende'}" @click="tab='tende'">Tende/Cover</button>
        <button class="btn ghost" :class="{active: tab==='setting'}" @click="tab='setting'">Setting</button>
        <button class="btn ghost" :class="{active: tab==='tech'}" @click="tab='tech'">Tecnica</button>
        <button class="btn" @click="loadData">Aggiorna</button>
      </div>
    </header>

    <div v-show="tab==='user_public'" class="user-public">
      <div class="user-public-head">
        <div class="up-brand">
          <img :src="logoEtende" alt="e-Tende Intelligenti" class="up-logo" />
        </div>
      </div>

      <div class="user-public-main">
        <aside class="up-side">
          <h3>Mappa taratura tenda</h3>
          <div class="up-legend-item" v-for="item in publicLegendItems" :key="item.key">
            <span class="dot" :style="{ background: item.color }"></span>
            <div class="up-legend-body">
              <strong>{{ item.title }}</strong>
              <span>{{ item.subtitle }}</span>
              <small>Stato: {{ item.state }}</small>
            </div>
          </div>
          <div class="up-wind">
            <strong>Vento</strong>
            <span>{{ fmt(mapWindDirDeg) }}° - {{ fmt(mapWindMs) }} m/s</span>
          </div>
        </aside>

        <section class="up-map-wrap">
          <div id="solar-map-public" data-map-container="solar-map-public"></div>
        </section>
      </div>
      <div class="up-map-controls">
        <div class="up-time-sim">
          <div class="time-labels">
            <span v-for="(h, i) in hours" :key="`uph-${i}`">{{ `${String(h).padStart(2,'0')}:00` }}</span>
          </div>
          <input type="range" :min="0" :max="timeSteps.length - 1" step="1" v-model.number="timeIndex" @input="drawSolarOverlay" />
          <div class="time-meta">Orario simulato: <strong>{{ selectedTimeLabel }}</strong></div>
        </div>
        <div class="toggles">
          <label><input type="checkbox" v-model="showLiveLine" @change="drawSolarOverlay" /> Linea LIVE (reale)</label>
          <label><input type="checkbox" v-model="showSimLine" @change="drawSolarOverlay" /> Linea SIMULATA</label>
          <label><input type="checkbox" v-model="showAxisNS" @change="drawSolarOverlay" /> Asse N-S</label>
          <label><input type="checkbox" v-model="showAxisWE" @change="drawSolarOverlay" /> Asse W-E</label>
          <label><input type="checkbox" v-model="showSunRefs" @change="drawSolarOverlay" /> Label Alba/Tramonto</label>
          <label><input type="checkbox" v-model="showPvAzLine" @change="drawSolarOverlay" /> Linea Azimut FV</label>
          <label><input type="checkbox" v-model="showAnnualElevationBand" @change="drawSolarOverlay" /> Fascia elevazione annua</label>
          <label><input type="checkbox" v-model="showTendeSectors" @change="drawSolarOverlay" /> Spicchi Cover</label>
          <label><input type="checkbox" v-model="showWindDirectionOnMap" @change="drawSolarOverlay" /> Direzione vento</label>
        </div>
        <div class="pv-az-controls" v-if="showPvAzLine">
          <label>Azimut FV:
            <input type="range" min="-180" max="180" step="1" v-model.number="pvAzimuthDeg" @input="drawSolarOverlay" />
          </label>
          <input class="pv-az-input" type="number" min="-180" max="180" step="1" v-model.number="pvAzimuthDeg" @change="drawSolarOverlay" />
          <span class="pv-az-value">{{ pvAzimuthDeg }}°</span>
        </div>
      </div>

      <div class="up-bottom">
        <div class="up-card"><h4>Sole attuale</h4><div>Azimut: <strong>{{ fmt(data?.sun_position?.azimuth_compass_deg) }}°</strong></div><div>Elevazione: <strong>{{ fmt(data?.sun_position?.altitude_deg) }}°</strong></div></div>
        <div class="up-card"><h4>Weather Guard</h4><div>Stato: <strong>{{ weatherGuardOk ? 'ATTIVO' : 'OFF' }}</strong></div><div>Vento: <strong>{{ weatherGuardWindAlarm ? 'ALLARME' : 'ok' }}</strong></div><div>Pioggia: <strong>{{ weatherGuardRainAlarm ? 'ALLARME' : 'ok' }}</strong></div></div>
        <div class="up-card"><h4>Termoregolazione</h4><div>Temperatura interna: <strong>{{ fmt(externalTempC) }}°C</strong></div><div>Umidita interna: <strong>{{ fmt(externalHumidityPct) }}%</strong></div></div>
        <div class="up-card"><h4>Fotovoltaico</h4><div>Reale: <strong>{{ fmt0(pvMeasuredW) }} W</strong></div><div>Atteso: <strong>{{ fmt0(pvForecastNowW) }} W</strong></div><div>Rapporto: <strong>{{ fmt2(pvLiveRatio) }}</strong></div></div>
      </div>
    </div>

    <div v-show="tab==='energy_public' || tab==='energy'" class="energy-public" :class="energyThemeClass">
      <div v-if="tab==='energy'" class="energy-page-head">
        <div>
          <h2>Energy</h2>
          <p>Riepilogo impianto e accesso alle dashboard Energy Flow configurate.</p>
        </div>
        <a
          class="btn"
          :href="`energy-dashboard/sunsynk-wrapper.html?site=${selectedEnergySiteId}`"
          target="_blank"
          rel="noopener noreferrer"
        >Apri Energy Flow</a>
      </div>
      <div class="energy-hero">
        <div class="energy-status">Status: <strong>{{ energyEnabled ? 'Normal' : 'Spento' }}</strong></div>
        <div class="energy-temp">{{ fmt(externalTempC) }}°C</div>
      </div>
      <div class="energy-flow-board">
        <div class="ef-link ef-link-bat"></div>
        <div class="ef-link ef-link-grid"></div>
        <div class="ef-link ef-link-home"></div>

        <div class="ef-node ef-node-pv">
          <div class="ef-icon">☀</div>
          <div class="ef-name">FV</div>
          <div class="ef-val">{{ fmtKw(energyPvPowerW) }} kW</div>
        </div>
        <div class="ef-node ef-node-home">
          <div class="ef-icon">⌂</div>
          <div class="ef-name">Casa</div>
          <div class="ef-val">{{ fmtKw(energyHomePowerW) }} kW</div>
        </div>
        <div class="ef-node ef-node-grid">
          <div class="ef-icon">⚡</div>
          <div class="ef-name">Rete</div>
          <div class="ef-val">{{ fmtKw(energyGridPowerW) }} kW</div>
        </div>
        <div class="ef-node ef-node-bat">
          <div class="ef-icon">▣</div>
          <div class="ef-name">Batteria</div>
          <div class="ef-val">{{ fmtKw(energyBatteryPowerW) }} kW</div>
          <div class="ef-sub">SOC {{ fmt(energyBatterySocPct) }}%</div>
        </div>
        <div class="ef-kpi-side">
          <div class="ef-kpi"><span>Real-time Power</span><strong>{{ fmtKw(energyPvPowerW) }} kW</strong></div>
          <div class="ef-kpi"><span>Installed Power</span><strong>{{ fmt(energyInstalledKwp) }} kWp</strong></div>
        </div>
      </div>

      <div class="energy-kpi-grid">
        <div class="energy-kpi"><span>Real-time Power</span><strong>{{ fmtKw(energyPvPowerW) }} kW</strong></div>
        <div class="energy-kpi"><span>Installed Power</span><strong>{{ fmt(energyInstalledKwp) }} kWp</strong></div>
        <div class="energy-kpi"><span>Produzione Oggi</span><strong>{{ fmt(energyPvTodayKwh) }} kWh</strong></div>
        <div class="energy-kpi"><span>Consumo Oggi</span><strong>{{ fmt(energyHomeTodayKwh) }} kWh</strong></div>
        <div class="energy-kpi"><span>Import Rete Oggi</span><strong>{{ fmt(energyGridImportTodayKwh) }} kWh</strong></div>
        <div class="energy-kpi"><span>Export Rete Oggi</span><strong>{{ fmt(energyGridExportTodayKwh) }} kWh</strong></div>
      </div>
      <div v-if="tab==='energy' || energySiteCards.length > 1" class="energy-site-link-grid">
        <a
          v-for="site in energySiteCards"
          :key="site.id"
          class="energy-site-link"
          :href="`energy-dashboard/sunsynk-wrapper.html?site=${site.id}`"
          target="_blank"
          rel="noopener noreferrer"
        >
          <strong>{{ site.name }}</strong>
          <span>PV {{ fmtKw(site.pv) }} kW · Casa {{ fmtKw(site.home) }} kW</span>
        </a>
      </div>
    </div>


    <div v-show="tab==='livoltek'">
      <main class="tech-main">
        <section class="card livoltek-head-card">
          <div class="livoltek-title-row">
            <div>
              <h2>Livoltek</h2>
              <p>Integrazione separata per probe, polling e dati grezzi inverter.</p>
            </div>
            <label class="switch-line">
              <input type="checkbox" v-model="livoltekForm.enabled" @change="saveLivoltekConfig" />
              <span>{{ livoltekForm.enabled ? 'Abilitato' : 'Disabilitato' }}</span>
            </label>
          </div>
          <div class="actions-inline">
            <button class="btn ghost" @click="refreshLivoltek" :disabled="!livoltekForm.enabled">Refresh</button>
            <button class="btn ghost" @click="probeLivoltek" :disabled="!livoltekForm.enabled">Probe API</button>
            <button class="btn ghost" @click="resendLivoltekDiscovery" :disabled="!livoltekForm.enabled || !livoltekForm.mqtt_discovery_enabled">Rispedisci MQTT Discovery</button>
            <button class="btn" @click="saveLivoltekConfig">Salva Livoltek</button>
            <span class="note">{{ livoltekSaveStatus }}</span>
          </div>
          <p v-if="!livoltekForm.enabled" class="note">Livoltek e spento: nessun login, polling, API o MQTT viene eseguito.</p>
        </section>

        <section class="card">
          <h3>Configurazione</h3>
          <div class="form-grid">
            <label>Base URL
              <input type="text" v-model="livoltekForm.base_url" />
            </label>
            <label>Username
              <input type="text" v-model="livoltekForm.username" autocomplete="off" />
            </label>
            <label>Password
              <input type="password" v-model="livoltekForm.password" autocomplete="new-password" placeholder="lascia *** per non cambiare" />
            </label>
            <label>Token opzionale
              <input type="password" v-model="livoltekForm.token" autocomplete="off" placeholder="vuoto = login username/password" />
            </label>
            <label>Station ID
              <input type="text" v-model="livoltekForm.station_id" />
            </label>
            <label>Device ID
              <input type="text" v-model="livoltekForm.device_id" />
            </label>
            <label>Inverter SN
              <input type="text" v-model="livoltekForm.inverter_sn" />
            </label>
            <label>Device serial
              <input type="text" v-model="livoltekForm.device_serial" />
            </label>
            <label>Polling secondi
              <input type="number" min="30" max="86400" v-model.number="livoltekForm.poll_interval_seconds" />
            </label>
            <label>Timeout secondi
              <input type="number" min="5" max="120" v-model.number="livoltekForm.timeout_seconds" />
            </label>
            <label>MQTT Discovery Livoltek
              <input type="checkbox" v-model="livoltekForm.mqtt_discovery_enabled" />
            </label>
          </div>
        </section>

        <section class="card">
          <h3>Stato runtime</h3>
          <div class="form-grid">
            <div class="kpi"><strong>Connessione:</strong> {{ livoltekStatus?.connected ? 'online' : (livoltekForm.enabled ? 'offline' : 'disabilitato') }}</div>
            <div class="kpi"><strong>Ultimo update:</strong> {{ fmtTs(livoltekStatus?.last_update_ts) }}</div>
            <div class="kpi"><strong>Ultimo probe:</strong> {{ fmtTs(livoltekStatus?.last_probe_ts) }}</div>
            <div class="kpi"><strong>Ultimo errore:</strong> {{ livoltekStatus?.last_error || '-' }}</div>
            <div class="kpi"><strong>Errore MQTT:</strong> {{ livoltekStatus?.mqtt_last_error || '-' }}</div>
          </div>
          <div class="energy-kpi-grid">
            <div class="energy-kpi"><span>PV live</span><strong>{{ fmt0(livoltekNorm.pv_power_w) }} W</strong></div>
            <div class="energy-kpi"><span>PV oggi</span><strong>{{ fmt2(livoltekNorm.pv_energy_today_kwh) }} kWh</strong></div>
            <div class="energy-kpi"><span>PV totale</span><strong>{{ fmt2(livoltekNorm.pv_energy_total_kwh) }} kWh</strong></div>
            <div class="energy-kpi"><span>Batteria</span><strong>{{ fmt0(livoltekNorm.battery_soc_pct) }} %</strong></div>
            <div class="energy-kpi"><span>Battery power</span><strong>{{ fmt0(livoltekNorm.battery_power_w) }} W</strong></div>
            <div class="energy-kpi"><span>Rete</span><strong>{{ fmt0(livoltekNorm.grid_power_w) }} W</strong></div>
            <div class="energy-kpi"><span>Carichi</span><strong>{{ fmt0(livoltekNorm.load_power_w) }} W</strong></div>
            <div class="energy-kpi"><span>Inverter</span><strong>{{ livoltekNorm.inverter_status ?? '-' }}</strong></div>
          </div>
        </section>

        <section class="card">
          <h3>JSON grezzo</h3>
          <pre class="mono raw-json">{{ livoltekRawText }}</pre>
        </section>
      </main>
    </div>



    <div v-show="tab==='user'">
      <div class="view-tools">
        <button class="btn ghost" @click="userExpanded = !userExpanded">{{ userExpanded ? 'Riduci campi' : 'Allarga campi' }}</button>
      </div>
      <div class="map-block-group">
      <div class="map-group-title">Mappa + controlli simulazione</div>
      <div class="timeline">
        <div class="time-labels">
          <span v-for="(h, i) in hours" :key="`h-${i}`">{{ `${String(h).padStart(2,'0')}:00` }}</span>
        </div>
        <input type="range" :min="0" :max="timeSteps.length - 1" step="1" v-model.number="timeIndex" @input="drawSolarOverlay" />
        <div class="time-meta">Orario simulato: <strong>{{ selectedTimeLabel }}</strong></div>
        <div class="toggles">
          <label><input type="checkbox" v-model="showLiveLine" @change="drawSolarOverlay" /> Linea LIVE (reale)</label>
          <label><input type="checkbox" v-model="showSimLine" @change="drawSolarOverlay" /> Linea SIMULATA</label>
          <label><input type="checkbox" v-model="showAxisNS" @change="drawSolarOverlay" /> Asse N-S</label>
          <label><input type="checkbox" v-model="showAxisWE" @change="drawSolarOverlay" /> Asse W-E</label>
          <label><input type="checkbox" v-model="showSunRefs" @change="drawSolarOverlay" /> Label Alba/Tramonto</label>
          <label><input type="checkbox" v-model="showPvAzLine" @change="drawSolarOverlay" /> Linea Azimut FV</label>
          <label><input type="checkbox" v-model="showAnnualElevationBand" @change="drawSolarOverlay" /> Fascia elevazione annua</label>
          <label><input type="checkbox" v-model="showTendeSectors" @change="drawSolarOverlay" /> Spicchi Cover (e_Tende Intelligenti)</label>
          <label><input type="checkbox" v-model="showWindDirectionOnMap" @change="drawSolarOverlay" /> Direzione vento su mappa</label>
          <label><input type="checkbox" v-model="weatherAnimEnabled" /> Animazione meteo</label>
        </div>
        <div class="pv-az-controls" v-if="showPvAzLine">
          <label>Azimut FV:
            <input type="range" min="-180" max="180" step="1" v-model.number="pvAzimuthDeg" @input="drawSolarOverlay" />
          </label>
          <input class="pv-az-input" type="number" min="-180" max="180" step="1" v-model.number="pvAzimuthDeg" @change="drawSolarOverlay" />
          <span class="pv-az-value">{{ pvAzimuthDeg }}°</span>
        </div>
      </div>

      <div class="map-wrap">
        <div class="map-block-title">Mappa Sole/Meteo</div>
        <div id="solar-map" data-map-container="solar-map"></div>
        <div v-if="tendeMapWarning" class="tende-badge">{{ tendeMapWarning }}</div>
        <canvas
          v-show="weatherAnimEnabled"
          ref="weatherCanvasEl"
          class="weather-overlay-canvas"
          aria-hidden="true"
        ></canvas>
        <div v-if="weatherAnimEnabled" class="wind-compass-chip">
          <span class="wind-compass-arrow" :style="{ transform: `rotate(${weatherWindDirDeg || 0}deg)` }">↑</span>
          <span>Vento da {{ fmt(weatherWindDirDeg) }}° ({{ weatherWindCardinal }})</span>
        </div>
      </div>
      </div>

      <div class="panel" v-show="userExpanded">
        <div class="kpi">Lat/Lon: {{ lat?.toFixed(5) }} , {{ lon?.toFixed(5) }}</div>
        <div class="kpi">Sorgente coordinate: {{ coordinatesSourceLabel }}</div>
        <div class="kpi">Sun Altitude LIVE (reale): {{ fmt(data?.sun_position?.altitude_deg) }}°</div>
        <div class="kpi">Sun Azimuth LIVE (reale): {{ fmt(data?.sun_position?.azimuth_compass_deg) }}°</div>
        <div class="kpi">Sun Altitude SIM: {{ fmt(currentSun.altitudeDeg) }}°</div>
        <div class="kpi">Sun Azimuth SIM: {{ fmt(currentSun.azimuthDeg) }}°</div>
        <div class="kpi">Data locale: {{ localTimestampLabel }}</div>
      </div>

      <div class="panel source-panel" v-show="userExpanded">
        <div class="source-card source-card--web">
          <h4>Meteo Web</h4>
          <div class="source-head">
            <span class="chip">Provider: {{ weatherProvider || '-' }}</span>
            <span class="chip">Aggiornamento: {{ weatherTime || '-' }}</span>
          </div>
          <div class="metric-grid">
            <div class="metric-row" v-for="m in weatherWebMetrics" :key="`wweb-${m.key}`">
              <span class="metric-key">{{ m.label }}</span>
              <span class="metric-val">{{ m.value }}</span>
            </div>
          </div>
        </div>

        <div class="source-card source-card--probe">
          <h4>Reali Sonde</h4>
          <div class="metric-grid">
            <div class="metric-row"><span class="metric-key">Temperatura reale</span><span class="metric-val">{{ fmt(externalTempC) }}°C</span></div>
            <div class="metric-row"><span class="metric-key">Umidita reale</span><span class="metric-val">{{ fmt(externalHumidityPct) }} %</span></div>
            <div class="metric-row"><span class="metric-key">Delta T (sonda - web)</span><span class="metric-val">{{ fmt(tempDeltaC) }}°C</span></div>
          </div>
        </div>

        <div class="source-card source-card--station">
          <h4>Reali Stazione Meteo</h4>
          <div class="source-head">
            <span class="chip">WG: {{ weatherStationUsed ? 'STAZIONE REALE' : 'METEO WEB (fallback)' }}</span>
            <span class="chip" :class="weatherStationOk ? 'chip-ok' : 'chip-bad'">Stazione: {{ weatherStationOk ? 'SI' : 'NO' }}</span>
          </div>
          <div class="metric-grid">
            <div class="metric-row" v-for="m in weatherStationMetrics" :key="`wsta-${m.key}`">
              <span class="metric-key">{{ m.label }}</span>
              <span class="metric-val">{{ m.value }}</span>
            </div>
          </div>
          <div class="guard-line">
            Weather Guard: {{ weatherGuardOk ? 'ATTIVO' : 'NON ATTIVO' }} | Vento {{ weatherGuardWindAlarm ? 'ALLARME' : 'ok' }} | Pioggia {{ weatherGuardRainAlarm ? 'ALLARME' : 'ok' }} | Facciata {{ weatherGuardFacadeRisk ? 'RISCHIO' : 'ok' }}
          </div>
          <details class="station-all-details">
            <summary>Entita stazione rilevate ({{ weatherStationAllEntities.length }})</summary>
            <div class="metric-grid metric-grid--compact">
              <div class="metric-row" v-for="ent in weatherStationAllEntities" :key="`wraw-${ent.entity_id}`">
                <span class="metric-key">{{ ent.friendly_name || ent.entity_id }}</span>
                <span class="metric-val">{{ ent.value_text }}</span>
              </div>
            </div>
          </details>
        </div>

        <div class="source-card source-card--pv">
          <h4>Fotovoltaico</h4>
          <div class="metric-grid">
            <div class="metric-row"><span class="metric-key">FV reale e-Control</span><span class="metric-val">{{ fmt0(pvMeasuredW) }} W</span></div>
            <div class="metric-row"><span class="metric-key">FV atteso (ora)</span><span class="metric-val">{{ fmt0(pvForecastNowW) }} W</span></div>
            <div class="metric-row"><span class="metric-key">Rapporto reale/atteso</span><span class="metric-val">{{ fmt2(pvLiveRatio) }}</span></div>
          </div>
        </div>
      </div>
      <div class="panel" v-show="userExpanded">
        <div class="kpi chart-kpi">
          <strong>Meteo Prossime 24h</strong>
          <svg
            class="weather-chart"
            viewBox="0 0 900 250"
            preserveAspectRatio="none"
            role="img"
            aria-label="Grafico meteo 24 ore: temperatura, pioggia e vento"
            @mousemove="onWeatherChartMove"
            @mouseleave="onWeatherChartLeave"
          >
            <line x1="50" y1="190" x2="870" y2="190" class="chart-axis" />
            <line x1="50" y1="24" x2="50" y2="190" class="chart-axis" />
            <line x1="870" y1="24" x2="870" y2="190" class="chart-axis" />

            <line v-for="t in weatherTempTicks" :key="`wt-${t}`" x1="50" :y1="weatherYFromTemp(t)" x2="870" :y2="weatherYFromTemp(t)" class="chart-grid" />
            <line v-for="(_, i) in weatherSeries" v-if="i % 3 === 0" :key="`wx-${i}`" :x1="weatherXFromIdx(i)" y1="24" :x2="weatherXFromIdx(i)" y2="190" class="chart-grid-v" />

            <rect
              v-for="(p, i) in weatherSeries"
              :key="`wr-${i}`"
              :x="weatherXFromIdx(i) - weatherBarHalfWidth"
              :y="weatherYFromRain(p.rain)"
              :width="weatherBarHalfWidth * 2"
              :height="Math.max(0, 190 - weatherYFromRain(p.rain))"
              class="weather-rain-bar"
            />

            <polyline :points="weatherTempPoints" class="weather-temp-line" />
            <circle v-for="(p, i) in weatherSeries" :key="`wd-${i}`" :cx="weatherXFromIdx(i)" :cy="weatherYFromTemp(p.temp)" r="2.8" class="weather-temp-dot" />
            <polyline v-if="weatherRealTempPoints" :points="weatherRealTempPoints" class="weather-real-temp-line" />
            <polyline :points="weatherWindPoints" class="weather-wind-line" />
            <circle v-for="(p, i) in weatherSeries" :key="`wwd-${i}`" :cx="weatherXFromIdx(i)" :cy="weatherYFromWind(p.wind)" r="2.2" class="weather-wind-dot" />
            <polyline :points="weatherHumidityPoints" class="weather-humidity-line" />
            <circle v-for="(p, i) in weatherSeries" :key="`whd-${i}`" :cx="weatherXFromIdx(i)" :cy="weatherYFromHumidity(p.humidity)" r="2" class="weather-humidity-dot" />
            <polyline :points="weatherPressurePoints" class="weather-pressure-line" />
            <circle v-for="(p, i) in weatherSeries" :key="`wpd-${i}`" :cx="weatherXFromIdx(i)" :cy="weatherYFromPressure(p.pressure)" r="1.8" class="weather-pressure-dot" />

            <line v-if="weatherHoverPoint" :x1="weatherHoverPoint.x" :x2="weatherHoverPoint.x" y1="24" y2="190" class="chart-hover-line" />
            <g v-if="weatherHoverPoint" :transform="`translate(${weatherHoverTooltipX},${weatherHoverTooltipY})`">
              <rect class="chart-tip-bg" x="0" y="0" rx="6" ry="6" width="250" height="82" />
              <text x="8" y="15" class="chart-tip-t1">{{ weatherHoverPoint.label }}</text>
              <text x="8" y="30" class="chart-tip-t2">Temp: {{ fmt(weatherHoverPoint.temp) }}°C</text>
              <text x="8" y="45" class="chart-tip-t2">Pioggia: {{ fmt(weatherHoverPoint.rain) }} mm/h | Vento: {{ fmt(weatherHoverPoint.wind) }} m/s</text>
              <text x="8" y="60" class="chart-tip-t2">Umid: {{ fmt(weatherHoverPoint.humidity) }} % | Press: {{ fmt(weatherHoverPoint.pressure) }} hPa</text>
              <text x="8" y="74" class="chart-tip-t2">T reale: {{ fmt(externalTempC) }}°C | Delta: {{ fmt(weatherHoverPoint.deltaRealTemp) }}°C</text>
            </g>

            <text v-for="t in weatherTempTicks" :key="`wl-${t}`" x="42" :y="weatherYFromTemp(t) + 3" class="axis-label-y">{{ fmt0(t) }}</text>
            <text v-for="t in weatherRainTicks" :key="`wrl-${t}`" x="876" :y="weatherYFromRain(t) + 3" class="axis-label-y axis-label-y-right-rain">{{ fmt1(t) }}</text>
            <text v-for="t in weatherWindTicks" :key="`wwl-${t}`" x="836" :y="weatherYFromWind(t) + 3" class="axis-label-y axis-label-y-right-wind">{{ fmt1(t) }}</text>
            <text x="18" y="20" class="axis-title">°C</text>
            <text x="876" y="20" class="axis-title">mm/h</text>
            <text x="836" y="20" class="axis-title axis-title-wind">m/s</text>
            <text v-for="(p, i) in weatherSeries" v-if="i % 3 === 0 || i === weatherSeries.length - 1" :key="`wxl-${i}`" :x="weatherXFromIdx(i)" y="206" class="axis-label-x axis-label-x-strong">{{ p.hhmm }}</text>
            <text x="872" y="224" class="axis-title-x">Ora (asse X)</text>
          </svg>
          <div class="weather-x-hours">
            <span v-for="p in weatherXAxisHours" :key="`wxh-${p.time}`">{{ p.hhmm }}</span>
          </div>
          <div class="chart-meta">
            Linea gialla: temp meteo | Magenta: temp reale | Barre azzurre: pioggia | Ciano: vento | Verde: umidita | Viola: pressione | Range temp: {{ fmt(weatherTempMin) }}..{{ fmt(weatherTempMax) }}°C
          </div>
        </div>
      </div>

      <div class="panel" v-show="userExpanded">
        <div class="kpi"><strong>Qualita aria provider:</strong> {{ airqProvider || '-' }}</div>
        <div class="kpi"><strong>AQI EU:</strong> {{ fmt0(airqEu) }}</div>
        <div class="kpi"><strong>AQI US:</strong> {{ fmt0(airqUs) }}</div>
        <div class="kpi"><strong>PM2.5:</strong> {{ fmt(airqPm25) }} ug/m3</div>
        <div class="kpi"><strong>PM10:</strong> {{ fmt(airqPm10) }} ug/m3</div>
        <div class="kpi"><strong>NO2:</strong> {{ fmt(airqNo2) }} ug/m3</div>
        <div class="kpi"><strong>O3:</strong> {{ fmt(airqO3) }} ug/m3</div>
        <div class="kpi"><strong>CO:</strong> {{ fmt(airqCo) }} ug/m3</div>
        <div class="kpi"><strong>SO2:</strong> {{ fmt(airqSo2) }} ug/m3</div>
      </div>

      <div class="panel" v-show="userExpanded">
        <div class="kpi chart-kpi">
          <strong>Qualita aria - Grafico 24h</strong>
          <svg
            class="airq-chart"
            viewBox="0 0 900 250"
            preserveAspectRatio="none"
            role="img"
            aria-label="Grafico qualita aria 24 ore"
            @mousemove="onAirqChartMove"
            @mouseleave="onAirqChartLeave"
          >
            <line x1="50" y1="190" x2="870" y2="190" class="chart-axis" />
            <line x1="50" y1="24" x2="50" y2="190" class="chart-axis" />
            <line x1="870" y1="24" x2="870" y2="190" class="chart-axis" />
            <line v-for="t in airqTicks" :key="`aqt-${t}`" x1="50" :y1="airqY(t)" x2="870" :y2="airqY(t)" class="chart-grid" />
            <line v-for="(_, i) in airqSeries" v-if="i % 3 === 0" :key="`aqx-${i}`" :x1="airqX(i)" y1="24" :x2="airqX(i)" y2="190" class="chart-grid-v" />

            <polyline :points="airqEuPoints" class="airq-eu-line" />
            <polyline :points="airqPm25Points" class="airq-pm25-line" />
            <polyline :points="airqPm10Points" class="airq-pm10-line" />

            <line v-if="airqHover" :x1="airqHover.x" :x2="airqHover.x" y1="24" y2="190" class="chart-hover-line" />
            <g v-if="airqHover" :transform="`translate(${airqTipX},${airqTipY})`">
              <rect class="chart-tip-bg" x="0" y="0" rx="6" ry="6" width="220" height="66" />
              <text x="8" y="15" class="chart-tip-t1">{{ airqHover.time }}</text>
              <text x="8" y="31" class="chart-tip-t2">AQI EU: {{ fmt0(airqHover.eu) }}</text>
              <text x="8" y="47" class="chart-tip-t2">PM2.5: {{ fmt(airqHover.pm25) }} | PM10: {{ fmt(airqHover.pm10) }}</text>
              <text x="8" y="61" class="chart-tip-t2">AQI US: {{ fmt0(airqHover.us) }}</text>
            </g>

            <text v-for="t in airqTicks" :key="`aql-${t}`" x="42" :y="airqY(t) + 3" class="axis-label-y">{{ fmt0(t) }}</text>
            <text v-for="(p, i) in airqSeries" v-if="i % 3 === 0 || i === airqSeries.length - 1" :key="`aqxl-${i}`" :x="airqX(i)" y="206" class="axis-label-x axis-label-x-strong">{{ p.hhmm }}</text>
            <text x="18" y="20" class="axis-title">indice</text>
            <text x="872" y="224" class="axis-title-x">Ora</text>
          </svg>
          <div class="chart-meta">
            Giallo: AQI EU | Azzurro: PM2.5 | Arancio: PM10
          </div>
        </div>
      </div>

      <div class="panel" v-show="userExpanded">
        <div class="kpi"><strong>Solar FV stato:</strong> {{ forecastOk ? 'OK' : 'N/D' }}</div>
        <div class="kpi"><strong>FV Oggi:</strong> {{ fmt0(fvTodayWh) }} Wh</div>
        <div class="kpi"><strong>FV Domani:</strong> {{ fmt0(fvTomorrowWh) }} Wh</div>
        <div class="kpi"><strong>FV Attuale:</strong> {{ fmt0(fvCurrentW) }} W</div>
        <div class="kpi"><strong>FV Picco oggi:</strong> {{ fmt0(fvPeakTodayW) }} W</div>
        <div class="kpi"><strong>Ultimo fetch:</strong> {{ forecastFetchedAtText }}</div>
      </div>

      <div class="panel" v-show="userExpanded">
        <div class="kpi chart-kpi">
          <strong>Grafico FV Oggi (W)</strong>
          <div class="actions-inline">
            <label>Giorno curva:
              <select v-model="selectedForecastDate">
                <option v-for="d in fvDayRows" :key="`sel-${d.date}`" :value="d.date">{{ d.dayName }} {{ d.dateLabel }}</option>
              </select>
            </label>
          </div>
          <svg
            class="fv-chart"
            viewBox="0 0 700 220"
            preserveAspectRatio="none"
            role="img"
            aria-label="Curva produzione FV giornaliera"
            @mousemove="onChartMove"
            @mouseleave="onChartLeave"
          >
            <line v-for="t in yTicks" :key="`y-${t}`" x1="40" :y1="yFromW(t)" x2="680" :y2="yFromW(t)" class="chart-grid" />
            <line v-for="t in xTicks" :key="`x-${t}`" :x1="xFromMinute(t)" y1="20" :x2="xFromMinute(t)" y2="150" class="chart-grid-v" />
            <line x1="40" y1="150" x2="680" y2="150" class="chart-axis" />
            <line x1="40" y1="20" x2="40" y2="150" class="chart-axis" />
            <polyline :points="fvChartPoints" class="chart-line" />
            <line :x1="fvNowX" :x2="fvNowX" y1="20" y2="150" class="chart-now" />
            <line v-if="hoverPoint" :x1="hoverPoint.x" :x2="hoverPoint.x" y1="20" y2="150" class="chart-hover-line" />
            <circle v-if="hoverPoint" :cx="hoverPoint.x" :cy="hoverPoint.y" r="4.5" class="chart-hover-dot" />
            <g v-if="hoverPoint" :transform="`translate(${hoverTooltipX},${hoverTooltipY})`">
              <rect class="chart-tip-bg" x="0" y="0" rx="6" ry="6" width="130" height="36" />
              <text x="8" y="15" class="chart-tip-t1">{{ hoverPoint.time }}</text>
              <text x="8" y="29" class="chart-tip-t2">{{ fmt0(hoverPoint.w) }} W</text>
            </g>

            <text v-for="t in yTicks" :key="`yl-${t}`" x="34" :y="yFromW(t) + 3" class="axis-label-y">{{ Math.round(t) }}</text>
            <text v-for="t in xTicks" :key="`xl-${t}`" :x="xFromMinute(t)" y="168" class="axis-label-x">{{ fmtHourTick(t) }}</text>
            <text x="8" y="16" class="axis-title">W</text>
            <text x="672" y="184" class="axis-title-x">Ora</text>
          </svg>
          <div class="chart-meta">
            0:00 -> 23:59 | picco: {{ fmt0(fvPeakSelectedW) }} W
            <span v-if="hoverPoint"> | punto: {{ hoverPoint.time }} -> {{ fmt0(hoverPoint.w) }} W</span>
          </div>
        </div>
      </div>

      <div class="panel" v-show="userExpanded">
        <div class="kpi chart-kpi">
          <strong>Fotovoltaico - Potenza prevista ora per ora</strong>
          <div class="actions-inline">
            <label>Giorno barre:
              <select v-model="selectedForecastDate">
                <option v-for="d in fvDayRows" :key="`bars-${d.date}`" :value="d.date">{{ d.dayName }} {{ d.dateLabel }}</option>
              </select>
            </label>
            <span class="note">Giorni disponibili: {{ fvDayRows.length }}</span>
          </div>
          <div class="bar-chart-area">
            <div class="bar-y-axis">
              <div v-for="t in yTicksBars" :key="`by-${t}`" class="bar-y-tick">{{ fmt0(t) }}</div>
            </div>
            <div class="day-bars">
              <div v-for="d in fvHourBars" :key="`h-${d.time}`" class="day-bar-item">
                <div
                  class="day-bar-wrap"
                  @mouseenter="hoverHourBar = d"
                  @mouseleave="hoverHourBar = null"
                >
                  <div class="day-bar" :style="{ height: `${d.pct}%` }"></div>
                  <div v-if="hoverHourBar && hoverHourBar.time === d.time" class="bar-tooltip">
                    {{ d.time }} -> {{ fmt0(d.w) }} W | {{ fmt2(d.kwh) }} kWh
                  </div>
                </div>
                <div class="day-bar-label">{{ d.time }}</div>
              </div>
            </div>
          </div>
          <div class="chart-meta">Asse Y: potenza oraria (W) normalizzata al picco del giorno selezionato.</div>
        </div>
      </div>

      <div class="panel">
        <div class="kpi chart-kpi">
          <strong>Tabella giorni forecast</strong>
          <table class="day-table">
            <thead>
              <tr>
                <th>Giorno</th>
                <th>Data</th>
                <th>Wh</th>
                <th>kWh</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in fvDayRows" :key="`row-${d.date}`">
                <td>{{ d.dayName }}</td>
                <td>{{ d.dateLabel }}</td>
                <td>{{ fmt0(d.wh) }}</td>
                <td>{{ (d.wh / 1000).toFixed(2) }}</td>
              </tr>
              <tr v-if="!fvDayRows.length">
                <td colspan="4">Nessun dato giornaliero disponibile.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-show="tab==='tende'" class="tende-page">
      <div class="tende-toolbar">
        <button class="btn ghost" :class="{active: tendeEditMode}" @click="toggleTendeEditMode">{{ tendeEditMode ? 'Fine modifica' : 'Modifica su mappa' }}</button>
        <button class="btn" @click="saveSelectedShade" :disabled="!selectedShadeEdit">Salva taratura</button>
        <span class="note">{{ tendeSaveStatus }}</span>
      </div>
      <div class="card" v-if="selectedShadeEdit">
        <h3>Taratura {{ selectedShadeEdit.name || selectedShadeEdit.id }}</h3>
        <div class="tende-wizard">
          <div class="wizard-head">
            <div>
              <strong>Wizard taratura cover</strong>
              <p>{{ wizardSteps[tendeWizardStep]?.hint }}</p>
            </div>
            <div class="wizard-step-count">Step {{ tendeWizardStep + 1 }} / {{ wizardSteps.length }}</div>
          </div>
          <div class="wizard-tabs">
            <button
              v-for="(step, idx) in wizardSteps"
              :key="step.key"
              class="wizard-tab"
              :class="{active: idx === tendeWizardStep}"
              @click="tendeWizardStep = idx"
            >{{ step.label }}</button>
          </div>
          <div class="wizard-body">
            <div v-if="wizardSteps[tendeWizardStep]?.key === 'base'" class="wizard-grid">
              <label>Automazione
                <input type="checkbox" v-model="selectedShadeEdit.enabled" />
                <small>Abilita o disabilita i comandi automatici per questa cover.</small>
              </label>
              <label>Logica sole
                <input type="checkbox" v-model="selectedShadeEdit.sun_logic_enabled" />
                <small>Usa azimut/elevazione sole per decidere la posizione.</small>
              </label>
              <label>Apri se sole assente
                <input type="checkbox" v-model="selectedShadeEdit.open_when_no_sun" />
                <small>Quando il sole non e piu utile, torna alla posizione di riposo.</small>
              </label>
              <button class="btn ghost wizard-preset" @click="applyWizardPreset('base_safe')">
                <strong>Preset base sicuro</strong>
                <small>Automazione ON, logica sole ON, apertura se sole assente e comando Open/Close.</small>
              </button>
            </div>
            <div v-else-if="wizardSteps[tendeWizardStep]?.key === 'sun'" class="wizard-grid">
              <label>Azimut finestra
                <input type="number" min="0" max="360" step="0.1" v-model.number="selectedShadeEdit.window_azimuth" @change="drawTendeEditor" />
                <small>Direzione perpendicolare alla finestra: guida la logica sole.</small>
              </label>
              <label>Modalita Start/Stop
                <input type="checkbox" v-model="selectedShadeEdit.use_start_stop_azimuth" @change="drawTendeEditor" />
                <small>Se attiva, usa due angoli netti di ingresso/uscita sole.</small>
              </label>
              <label>Azimuth start
                <input type="number" min="0" max="360" step="0.1" v-model.number="selectedShadeEdit.azimuth_start_deg" @change="drawTendeEditor" />
                <small>Angolo in cui il sole inizia a colpire la finestra.</small>
              </label>
              <label>Azimuth end
                <input type="number" min="0" max="360" step="0.1" v-model.number="selectedShadeEdit.azimuth_end_deg" @change="drawTendeEditor" />
                <small>Angolo in cui il sole esce dalla finestra.</small>
              </label>
              <label>Campo visivo sinistro
                <input type="number" min="0" max="180" step="0.1" v-model.number="selectedShadeEdit.fov_left" @change="drawTendeEditor" />
                <small>Ampiezza a sinistra dell'azimut finestra, se non usi Start/Stop.</small>
              </label>
              <label>Campo visivo destro
                <input type="number" min="0" max="180" step="0.1" v-model.number="selectedShadeEdit.fov_right" @change="drawTendeEditor" />
                <small>Ampiezza a destra dell'azimut finestra, se non usi Start/Stop.</small>
              </label>
              <button class="btn ghost wizard-preset" @click="applyWizardPreset('sun_fov')">
                <strong>Usa campo visivo ±70°</strong>
                <small>Disattiva Start/Stop e usa una finestra angolare larga 140°.</small>
              </button>
            </div>
            <div v-else-if="wizardSteps[tendeWizardStep]?.key === 'positions'" class="wizard-grid">
              <label>Posizione riposo
                <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.default_position" />
                <small>Posizione usata quando il sole non richiede protezione.</small>
              </label>
              <label>Posizione notte
                <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.sunset_position" />
                <small>Posizione dopo tramonto, se la cover deve chiudere o aprire di notte.</small>
              </label>
              <label>Posizione minima sole
                <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.min_position" />
                <small>Posizione di protezione quando il sole e utile e va schermato.</small>
              </label>
              <label>Delta minimo
                <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.min_delta" />
                <small>Evita micro-movimenti se la differenza posizione e troppo piccola.</small>
              </label>
              <label>Anti-loop comandi sec.
                <input type="number" min="0" max="3600" step="10" v-model.number="selectedShadeEdit.min_command_interval_seconds" />
                <small>Blocca comandi motore troppo ravvicinati.</small>
              </label>
              <button class="btn ghost wizard-preset" @click="applyWizardPreset('positions_balanced')">
                <strong>Preset bilanciato</strong>
                <small>Riposo 100%, notte 0%, sole 10%, delta 3%, anti-loop 120s.</small>
              </button>
            </div>
            <div v-else-if="wizardSteps[tendeWizardStep]?.key === 'weather'" class="wizard-grid">
              <label>Protezione Meteo Guard
                <input type="checkbox" v-model="selectedShadeEdit.weather_guard_enabled" />
                <small>Abilita priorita sicurezza da vento, pioggia e stravento.</small>
              </label>
              <label>Azimut facciata stravento
                <input type="number" min="0" max="360" step="0.1" v-model.number="selectedShadeEdit.facade_azimuth_deg" @change="drawTendeEditor" />
                <small>Direzione reale della facciata per rischio pioggia spinta dal vento.</small>
              </label>
              <label>Posizione sicurezza vento
                <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.weather_wind_safe_position" />
                <small>Posizione comandata quando c'e allarme vento.</small>
              </label>
              <label>Posizione sicurezza pioggia
                <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.weather_rain_safe_position" />
                <small>Posizione comandata quando c'e allarme pioggia.</small>
              </label>
              <button class="btn ghost wizard-preset" @click="applyWizardPreset('weather_safe')">
                <strong>Preset sicurezza meteo</strong>
                <small>Attiva tutte le protezioni meteo e porta le posizioni sicurezza a 0%.</small>
              </button>
            </div>
            <div v-else-if="wizardSteps[tendeWizardStep]?.key === 'thermal'" class="wizard-grid">
              <label>Strategia termica
                <input type="checkbox" v-model="selectedShadeEdit.thermal_enabled" />
                <small>Usa il termostato per rifinire la decisione quando il sole e utile.</small>
              </label>
              <label>Termostato ambiente
                <input type="text" placeholder="climate.sala" v-model.trim="selectedShadeEdit.thermal_climate_entity" />
                <small>Puo essere lo stesso climate per piu cover della stessa zona.</small>
              </label>
              <label>Isteresi termica °C
                <input type="number" min="0" max="5" step="0.1" v-model.number="selectedShadeEdit.thermal_hysteresis" />
                <small>Margine intorno al setpoint per evitare rimbalzi.</small>
              </label>
              <label>Posizione guadagno calore
                <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.thermal_heat_gain_position" />
                <small>In modalita heat, sotto setpoint, lascia entrare sole fino a questa posizione.</small>
              </label>
              <label>Posizione blocco calore
                <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.thermal_cool_block_position" />
                <small>In modalita cool, sopra setpoint, scherma il sole fino a questa posizione.</small>
              </label>
              <button class="btn ghost wizard-preset" @click="applyWizardPreset('thermal_conservative')">
                <strong>Preset termico conservativo</strong>
                <small>Isteresi 0.5°C, guadagno calore 70%, blocco calore come posizione sole.</small>
              </button>
            </div>
            <div v-else class="wizard-review">
              <div class="what-if-panel">
                <div class="what-if-head">
                  <strong>Simulatore What-if</strong>
                  <span>Confronta configurazione attuale e proposta prima di salvare.</span>
                </div>
                <div class="what-if-grid">
                  <div class="what-if-card">
                    <h4>Attuale</h4>
                    <span>Sole utile: {{ whatIfPreview.current.usefulLabel }}</span>
                    <span>Picco: {{ whatIfPreview.current.peakLabel }}</span>
                    <span>Posizione sole: {{ whatIfPreview.current.sunPositionLabel }}</span>
                    <span>Riposo: {{ whatIfPreview.current.defaultPositionLabel }}</span>
                    <span>Termico: {{ whatIfPreview.current.thermalLabel }}</span>
                  </div>
                  <div class="what-if-card proposed">
                    <h4>Proposta</h4>
                    <span>Sole utile: {{ whatIfPreview.proposed.usefulLabel }}</span>
                    <span>Picco: {{ whatIfPreview.proposed.peakLabel }}</span>
                    <span>Posizione sole: {{ whatIfPreview.proposed.sunPositionLabel }}</span>
                    <span>Riposo: {{ whatIfPreview.proposed.defaultPositionLabel }}</span>
                    <span>Termico: {{ whatIfPreview.proposed.thermalLabel }}</span>
                  </div>
                  <div class="what-if-card delta">
                    <h4>Differenza</h4>
                    <span>{{ whatIfPreview.deltaUsefulLabel }}</span>
                    <span>{{ whatIfPreview.deltaSunPositionLabel }}</span>
                    <span>{{ whatIfPreview.deltaDefaultPositionLabel }}</span>
                    <span>{{ whatIfPreview.thermalDeltaLabel }}</span>
                  </div>
                </div>
              </div>
              <span>Heatmap: verifica le ore di sole utile sotto la mappa.</span>
              <span>Se `Decisione termica` resta `missing_climate`, controlla il nome `climate.xxx`.</span>
              <span>Se il motore si muove troppo spesso, aumenta `Anti-loop comandi sec.`.</span>
              <button class="btn" @click="saveSelectedShade">Salva taratura</button>
            </div>
          </div>
          <div class="wizard-actions">
            <button class="btn ghost" @click="prevWizardStep" :disabled="tendeWizardStep <= 0">Indietro</button>
            <button v-if="tendeWizardStep < wizardSteps.length - 1" class="btn ghost" @click="nextWizardStep">Avanti</button>
          </div>
        </div>
        <div class="tende-cal-grid">
          <label>Automazione
            <input type="checkbox" v-model="selectedShadeEdit.enabled" />
          </label>
          <label>Usa logica sole
            <input type="checkbox" v-model="selectedShadeEdit.sun_logic_enabled" />
          </label>
          <label>Inverti logica sole
            <input type="checkbox" v-model="selectedShadeEdit.invert_sun_logic" />
          </label>
          <label>Apri se sole assente
            <input type="checkbox" v-model="selectedShadeEdit.open_when_no_sun" />
          </label>
          <label>Modalita Start/Stop
            <input type="checkbox" v-model="selectedShadeEdit.use_start_stop_azimuth" />
          </label>
          <label>Modalita Open/Close
            <input type="checkbox" v-model="selectedShadeEdit.command_mode_open_close" />
          </label>
          <label>Azimut finestra
            <input type="number" min="0" max="360" step="0.1" v-model.number="selectedShadeEdit.window_azimuth" @change="drawTendeEditor" />
          </label>
          <label>Azimut facciata stravento
            <input type="number" min="0" max="360" step="0.1" v-model.number="selectedShadeEdit.facade_azimuth_deg" />
          </label>
          <label>Azimuth start
            <input type="number" min="0" max="360" step="0.1" v-model.number="selectedShadeEdit.azimuth_start_deg" @change="drawTendeEditor" />
          </label>
          <label>Azimuth end
            <input type="number" min="0" max="360" step="0.1" v-model.number="selectedShadeEdit.azimuth_end_deg" @change="drawTendeEditor" />
          </label>
          <label>Campo visivo sinistro
            <input type="number" min="0" max="180" step="0.1" v-model.number="selectedShadeEdit.fov_left" @change="drawTendeEditor" />
          </label>
          <label>Campo visivo destro
            <input type="number" min="0" max="180" step="0.1" v-model.number="selectedShadeEdit.fov_right" @change="drawTendeEditor" />
          </label>
          <label>Altitudine min
            <input type="number" min="-10" max="90" step="0.1" v-model.number="selectedShadeEdit.altitude_min_deg" @change="drawTendeEditor" />
          </label>
          <label>Altitudine max
            <input type="number" min="-10" max="90" step="0.1" v-model.number="selectedShadeEdit.altitude_max_deg" @change="drawTendeEditor" />
          </label>
          <label>Posizione riposo
            <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.default_position" />
          </label>
          <label>Posizione notte
            <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.sunset_position" />
          </label>
          <label>Posizione minima
            <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.min_position" />
          </label>
          <label>Posizione massima
            <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.max_position" />
          </label>
          <label>Delta minimo
            <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.min_delta" />
          </label>
          <label>Intervallo minuti
            <input type="number" min="1" max="120" step="1" v-model.number="selectedShadeEdit.interval_minutes" />
          </label>
          <label>Anti-loop comandi sec.
            <input type="number" min="0" max="3600" step="10" v-model.number="selectedShadeEdit.min_command_interval_seconds" />
          </label>
          <label>Strategia termica
            <input type="checkbox" v-model="selectedShadeEdit.thermal_enabled" />
          </label>
          <label>Termostato ambiente
            <input type="text" placeholder="climate.sala" v-model.trim="selectedShadeEdit.thermal_climate_entity" />
          </label>
          <label>Isteresi termica °C
            <input type="number" min="0" max="5" step="0.1" v-model.number="selectedShadeEdit.thermal_hysteresis" />
          </label>
          <label>Posizione guadagno calore
            <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.thermal_heat_gain_position" />
          </label>
          <label>Posizione blocco calore
            <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.thermal_cool_block_position" />
          </label>
          <label>Soglia Open/Close
            <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.open_close_threshold" />
          </label>
          <label>Soglia sonda FV
            <input type="number" min="0" max="20000" step="10" v-model.number="selectedShadeEdit.sun_probe_threshold" />
          </label>
          <label>Protezione Meteo Guard
            <input type="checkbox" v-model="selectedShadeEdit.weather_guard_enabled" />
          </label>
          <label>Proteggi vento
            <input type="checkbox" v-model="selectedShadeEdit.protect_on_wind_alarm" />
          </label>
          <label>Proteggi pioggia
            <input type="checkbox" v-model="selectedShadeEdit.protect_on_rain_alarm" />
          </label>
          <label>Proteggi stravento facciata
            <input type="checkbox" v-model="selectedShadeEdit.protect_on_facade_rain_risk" />
          </label>
          <div class="tende-position-row">
            <label>Posizione sicurezza meteo
              <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.weather_safe_position" />
            </label>
            <label>Posizione sicurezza vento
              <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.weather_wind_safe_position" />
            </label>
            <label>Posizione sicurezza pioggia
              <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.weather_rain_safe_position" />
            </label>
            <label>Posizione sicurezza stravento
              <input type="number" min="0" max="100" step="1" v-model.number="selectedShadeEdit.weather_facade_rain_safe_position" />
            </label>
          </div>
        </div>
        <div class="tende-sensors" v-if="selectedShadeEdit.sensors">
          <span>Sole: {{ fmt(selectedShadeEdit.sensors.sun_azimuth) }}&deg; / {{ fmt(selectedShadeEdit.sensors.sun_elevation) }}&deg;</span>
          <span>Sole davanti: {{ boolLabel(selectedShadeEdit.sensors.sun_in_front) }}</span>
          <span>Range elevazione: {{ boolLabel(selectedShadeEdit.sensors.sun_in_elevation_range) }}</span>
          <span>Logica sole: {{ boolLabel(selectedShadeEdit.sensors.sun_logic_enabled) }} / invertita {{ boolLabel(selectedShadeEdit.sensors.invert_sun_logic) }}</span>
          <span>Allarme meteo: {{ selectedShadeEdit.sensors.weather_active_alarm || 'none' }}</span>
          <span>Target meteo: {{ targetValue(selectedShadeEdit.sensors.weather_target_position) }}</span>
          <span>Rischio facciata: {{ boolLabel(selectedShadeEdit.sensors.weather_cover_facade_rain_risk) }}</span>
          <span>Ultimo comando: {{ targetValue(selectedShadeEdit.sensors.last_command_at) }} / {{ targetValue(selectedShadeEdit.sensors.last_command_reason) }}</span>
          <span>Anti-loop: {{ boolLabel(selectedShadeEdit.sensors.command_blocked) }} - {{ targetValue(selectedShadeEdit.sensors.command_blocked_reason) }}</span>
          <span>Rate limit residuo: {{ targetValue(selectedShadeEdit.sensors.command_blocked_remaining_seconds) }} s / target {{ targetValue(selectedShadeEdit.sensors.command_blocked_target_position) }}</span>
          <span>Termostato: {{ targetValue(selectedShadeEdit.sensors.thermal_climate_entity) }} / {{ targetValue(selectedShadeEdit.sensors.thermal_mode) }}</span>
          <span>Temperatura interna: {{ targetValue(selectedShadeEdit.sensors.thermal_temperature) }} °C / set {{ targetValue(selectedShadeEdit.sensors.thermal_setpoint) }} °C</span>
          <span>Decisione termica: {{ targetValue(selectedShadeEdit.sensors.thermal_decision) }} / attiva {{ boolLabel(selectedShadeEdit.sensors.thermal_active) }}</span>
        </div>
      </div>
      <div class="tende-layout">
        <div class="tende-list card">
          <h3>Cover da e-Tende Intelligenti</h3>
          <div v-if="!tendeMapShades.length" class="note">Nessuna tenda ricevuta.</div>
          <button
            v-for="s in tendeMapShades"
            :key="shadeKey(s)"
            class="shade-item"
            :class="{active: selectedShadeId===shadeKey(s)}"
            @click="selectShade(shadeKey(s))"
          >
            <strong>{{ s.name || s.id }}</strong>
            <span>{{ s.cover_entity || '-' }}</span>
            <span>Az {{ fmt(s.azimuth_start_deg) }}° -> {{ fmt(s.azimuth_end_deg) }}°</span>
            <span>Stato: {{ coverStateLabel(s.cover_entity) }}</span>
          </button>
        </div>
        <div class="tende-map-wrap card">
          <h3>Mappa taratura tenda</h3>
          <div id="tende-map" data-map-container="tende-map"></div>
          <div class="sun-window-heatmap" v-if="sunWindowHeatmap.slots.length">
            <div class="heatmap-head">
              <div>
                <h3>Heatmap sole-finestra oggi</h3>
                <p>{{ sunWindowHeatmap.subtitle }}</p>
              </div>
              <div class="heatmap-summary">
                <strong>{{ sunWindowHeatmap.usefulLabel }}</strong>
                <span>Picco {{ sunWindowHeatmap.peakLabel }}</span>
                <span>Prossima {{ sunWindowHeatmap.nextLabel }}</span>
              </div>
            </div>
            <div class="heatmap-strip" :style="{ gridTemplateColumns: `repeat(${sunWindowHeatmap.slots.length}, minmax(3px, 1fr))` }">
              <span
                v-for="slot in sunWindowHeatmap.slots"
                :key="slot.key"
                class="heatmap-cell"
                :class="{now: slot.isNow}"
                :style="{ background: slot.color }"
                :title="slot.title"
              ></span>
            </div>
            <div class="heatmap-axis">
              <span>{{ sunWindowHeatmap.startLabel }}</span>
              <span>Ora</span>
              <span>{{ sunWindowHeatmap.endLabel }}</span>
            </div>
          </div>
          <div class="sun-window-heatmap empty" v-else>
            Heatmap sole-finestra non disponibile: servono coordinate e una cover selezionata.
          </div>
        </div>
      </div>
    </div>


    <div v-show="tab==='setting' || tab==='energy_setup'">
      <main class="tech-main">
        <template v-if="tab==='setting'">
        <section class="card setting-save-card">
          <div class="actions-inline">
            <button class="btn" @click="saveAllSettings">Salva tutto</button>
            <span class="note">{{ allSaveStatus }}</span>
          </div>
        </section>

        <section class="card energy-settings-card">
          <h3>Configurazione Base Addon</h3>
          <div class="form-grid">
            <label>Latitude
              <input type="number" step="0.000001" v-model.number="baseForm.latitude" />
            </label>
            <label>Longitude
              <input type="number" step="0.000001" v-model.number="baseForm.longitude" />
            </label>
            <label>Timezone
              <input type="text" v-model="baseForm.timezone" />
            </label>
            <label>Sorgente coordinate
              <select v-model="baseForm.coordinates_source_mode">
                <option value="e_tende">Forza e-Tende</option>
                <option value="ha_core">Forza e-Control</option>
                <option value="local">Forza Config locale</option>
              </select>
            </label>
            <label>Interval minutes
              <input type="number" min="1" max="1440" v-model.number="baseForm.interval_minutes" />
            </label>
            <label>Location query
              <input type="text" v-model="baseForm.location_query" />
            </label>
            <label>PV actual entity id
              <input type="text" v-model="baseForm.pv_actual_entity_id" />
            </label>
            <label>External temp entity id
              <input type="text" v-model="baseForm.external_temp_entity_id" />
            </label>
            <label>External humidity entity id
              <input type="text" v-model="baseForm.external_humidity_entity_id" />
            </label>
          </div>
          <div class="form-grid">
            <div class="kpi"><strong>Entita temp reale:</strong> {{ externalTempEntityId || '-' }}</div>
            <div class="kpi"><strong>Stato lettura temp:</strong> {{ externalTempStatus }}</div>
            <div class="kpi"><strong>Errore temp reale:</strong> {{ externalTempError || '-' }}</div>
            <div class="kpi"><strong>Entita FV reale:</strong> {{ pvLiveEntityId || '-' }}</div>
            <div class="kpi"><strong>Stato lettura FV:</strong> {{ pvLiveStatus }}</div>
            <div class="kpi"><strong>Errore FV reale:</strong> {{ pvLiveError || '-' }}</div>
          </div>
        </section>

        <section class="card">
          <h3>Tarature Overlay</h3>
          <div class="form-grid">
            <label>Raggio percorso sole (m)
              <input type="number" v-model.number="cfg.pathRadiusM" min="30" max="300" @change="drawSolarOverlay" />
            </label>
            <label>Raggio settore giorno (m)
              <input type="number" v-model.number="cfg.sectorRadiusM" min="30" max="300" @change="drawSolarOverlay" />
            </label>
            <label>Raggio linea sole attuale (m)
              <input type="number" v-model.number="cfg.sunRadiusM" min="30" max="300" @change="drawSolarOverlay" />
            </label>
            <label>Zoom mappa
              <input type="number" v-model.number="cfg.mapZoom" min="14" max="22" @change="applyMapView" />
            </label>
          </div>
        </section>

        <section class="card">
          <h3>Tarature Forecast Solar (attuali)</h3>
          <div class="form-grid">
            <label>Enabled
              <input type="checkbox" v-model="fsForm.enabled" />
            </label>
            <label>API key
              <input type="text" v-model="fsForm.api_key" placeholder="vuota = public API" />
            </label>
            <label>Declination (0-90)
              <input type="number" min="0" max="90" v-model.number="fsForm.declination" />
            </label>
            <label>Azimuth (-180..180)
              <input type="number" min="-180" max="180" v-model.number="fsForm.azimuth" />
            </label>
            <label>kWp
              <input type="number" min="0.1" step="0.1" v-model.number="fsForm.kwp" />
            </label>
          </div>
          <div class="mono small">{{ forecastConfigText }}</div>
          <p class="note">Le tarature forecast sono modificabili e salvabili direttamente da Setting.</p>
        </section>

        <section class="card">
          <h3>Weather</h3>
          <div class="form-grid">
            <label>Enabled
              <input type="checkbox" v-model="weatherForm.enabled" />
            </label>
            <label>Provider
              <select v-model="weatherForm.provider">
                <option value="met">MET</option>
                <option value="open_meteo">Open-Meteo</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </label>
          </div>
        </section>

        </template>

        <template v-if="tab==='setting'">
        <section class="card energy-settings-card">
          <h3>Weather Station e-Control</h3>
          <div class="form-grid">
            <label>Enabled
              <input type="checkbox" v-model="weatherStationForm.enabled" />
            </label>
            <label>Stale seconds
              <input type="number" min="30" max="86400" v-model.number="weatherStationForm.stale_seconds" />
            </label>
            <label>Device id (auto-discovery)
              <input type="text" v-model="weatherStationForm.device_id" @change="autofillWeatherStationFromDevice" />
            </label>
            <label>Wind speed entity id
              <input type="text" v-model="weatherStationForm.wind_speed_entity_id" />
            </label>
            <label>Wind gust entity id
              <input type="text" v-model="weatherStationForm.wind_gust_entity_id" />
            </label>
            <label>Wind direction entity id
              <input type="text" v-model="weatherStationForm.wind_direction_entity_id" />
            </label>
            <label>Rain rate entity id
              <input type="text" v-model="weatherStationForm.rain_rate_entity_id" />
            </label>
            <label>Rain 1h entity id
              <input type="text" v-model="weatherStationForm.rain_1h_entity_id" />
            </label>
            <label>Outdoor temperature entity id
              <input type="text" v-model="weatherStationForm.outdoor_temp_entity_id" />
            </label>
            <label>Outdoor humidity entity id
              <input type="text" v-model="weatherStationForm.outdoor_humidity_entity_id" />
            </label>
            <label>Pressure entity id
              <input type="text" v-model="weatherStationForm.pressure_entity_id" />
            </label>
            <label>UV index entity id
              <input type="text" v-model="weatherStationForm.uv_index_entity_id" />
            </label>
            <label>Dew point entity id
              <input type="text" v-model="weatherStationForm.dewpoint_entity_id" />
            </label>
            <label>Feels like entity id
              <input type="text" v-model="weatherStationForm.feels_like_entity_id" />
            </label>
            <label>Solar lux entity id
              <input type="text" v-model="weatherStationForm.solar_lux_entity_id" />
            </label>
            <label>Solar radiation entity id
              <input type="text" v-model="weatherStationForm.solar_radiation_entity_id" />
            </label>
            <label>VPD entity id
              <input type="text" v-model="weatherStationForm.vpd_entity_id" />
            </label>
          </div>
        </section>
        </template>

        <template v-if="tab==='energy_setup'">
        <section class="card setting-save-card">
          <div class="actions-inline">
            <button class="btn" @click="saveAllSettings">Salva configurazione Energy</button>
            <span class="note">{{ allSaveStatus }}</span>
          </div>
        </section>
        <section class="card energy-settings-card energy-setup-page">
          <h3>Energy</h3>
          <p class="note energy-note">
            Configura prima i sensori principali. Le opzioni tecniche sono divise per area, cosi non devi scorrere una pagina enorme.
          </p>
          <div class="energy-sites-panel">
            <div class="energy-sites-head">
              <div>
                <strong>Dashboard / impianti</strong>
                <span>Ogni impianto ha sensori, JSON card, colori e sfondo separati.</span>
              </div>
              <div class="energy-site-actions">
                <button class="btn ghost" type="button" @click="addEnergySite">Aggiungi</button>
                <button class="btn ghost" type="button" @click="duplicateEnergySite">Duplica</button>
                <button class="btn ghost" type="button" @click="deleteEnergySite" :disabled="energySites.length <= 1">Elimina</button>
              </div>
            </div>
            <div class="energy-site-tabs">
              <button
                v-for="site in energySites"
                :key="site.id"
                type="button"
                class="energy-site-tab"
                :class="{active: normalizeEnergySiteId(site.id, 'default') === selectedEnergySiteId}"
                @click="selectEnergySite(site.id)"
              >
                <strong>{{ site.name || site.id }}</strong>
                <small>?site={{ site.id }}</small>
              </button>
            </div>
            <div class="energy-quick-grid">
              <label>Impianto attivo
                <select :value="selectedEnergySiteId" @change="selectEnergySite($event.target.value)">
                  <option v-for="site in energySites" :key="`sel-${site.id}`" :value="site.id">{{ site.name || site.id }}</option>
                </select>
              </label>
              <label>Nome dashboard
                <input
                  type="text"
                  :value="(energySites.find((s) => normalizeEnergySiteId(s.id, 'default') === selectedEnergySiteId) || {}).name || ''"
                  @input="(ev) => { const s = energySites.find((x) => normalizeEnergySiteId(x.id, 'default') === selectedEnergySiteId); if (s) s.name = ev.target.value }"
                />
              </label>
              <label>ID link
                <input
                  type="text"
                  :value="selectedEnergySiteId"
                  @change="(ev) => { const oldId = selectedEnergySiteId; const next = normalizeEnergySiteId(ev.target.value, oldId || 'default'); const s = energySites.find((x) => normalizeEnergySiteId(x.id, 'default') === oldId); if (s) s.id = next; selectedEnergySiteId = next }"
                />
              </label>
              <label>Link dashboard
                <input type="text" readonly :value="`energy-dashboard/sunsynk-wrapper.html?site=${selectedEnergySiteId}`" />
              </label>
              <a class="btn ghost" :href="`energy-dashboard/sunsynk-wrapper.html?site=${selectedEnergySiteId}`" target="_blank" rel="noopener noreferrer">Apri questa dashboard</a>
            </div>
          </div>
          <div class="energy-quick-panel">
            <div class="energy-quick-head">
              <div>
                <strong>Avvio rapido</strong>
                <span>{{ energyQuickMappedCount }}/6 campi principali compilati</span>
              </div>
              <div class="energy-status-pills">
                <span :class="{ok: energyForm.enabled}">{{ energyForm.enabled ? 'Energy ON' : 'Energy OFF' }}</span>
                <span>{{ energyWizardForm.cardstyle }}</span>
                <span>{{ energyWizardForm.show_aux ? 'AUX visibile' : 'AUX nascosto' }}</span>
              </div>
            </div>
            <div class="energy-setup-steps">
              <div><strong>1</strong><span>Metti PV, casa, rete e batteria</span></div>
              <div><strong>2</strong><span>Premi Genera JSON card</span></div>
              <div><strong>3</strong><span>Salva e apri Energy Flow</span></div>
            </div>
            <div class="energy-quick-grid">
              <label class="toggle-line">Energy attivo<input type="checkbox" v-model="energyForm.enabled" /></label>
              <label>Tema
                <select v-model="energyForm.theme">
                  <option value="classic_flow">Classic Inverter</option>
                  <option value="technical_dark">Technical Dark</option>
                  <option value="minimal_light">Minimal Light</option>
                </select>
              </label>
              <label>Sfondo dashboard
                <input type="color" v-model="energyForm.dashboard_background_color" />
              </label>
              <label class="toggle-line">Mostra Sankey<input type="checkbox" v-model="energyForm.show_sankey" /></label>
              <label>Layout dashboard
                <select v-model="energyForm.energy_dashboard_layout">
                  <option value="sunsynk">Sunsynk Power Flow</option>
                  <option value="k_flow">K Flow Card</option>
                </select>
              </label>
              <label>Layout card
                <select v-model="energyWizardForm.cardstyle" @change="onEnergyCardstyleChange">
                  <option value="full">full</option><option value="compact">compact</option><option value="lite">lite</option><option value="minimal">minimal</option>
                </select>
              </label>
              <label>PV1 produzione<input type="text" v-model="energyForm.pv_power_entity_id" placeholder="sensor... activepower_pv" /></label>
              <label>Casa / inverter<input type="text" v-model="energyForm.home_power_entity_id" placeholder="sensor... activepower_load" /></label>
              <label>Rete / grid<input type="text" v-model="energyForm.grid_power_entity_id" placeholder="sensor... activepower_pcc" /></label>
              <label>Batteria potenza<input type="text" v-model="energyForm.battery_power_entity_id" placeholder="sensor... battery_power" /></label>
              <label>Batteria SOC<input type="text" v-model="energyForm.battery_soc_entity_id" placeholder="sensor... battery" /></label>
              <label>PV installato kWp<input type="number" min="0" step="0.1" v-model.number="energyForm.pv_installed_kwp" /></label>
            </div>
            <div class="energy-quick-actions">
              <button class="btn ghost" @click="openEnergyEntityPopup('realtime')">Mappa entita da schema</button>
              <button class="btn ghost" @click="syncWizardFromEnergyForm(); applyEnergyWizard()">Genera JSON card</button>
              <a class="btn ghost" :href="`energy-dashboard/sunsynk-wrapper.html?site=${selectedEnergySiteId}`" target="_blank" rel="noopener noreferrer">Apri Energy Flow</a>
            </div>
            <div v-if="energyFullAuxLoadConflict" class="energy-warning">
              Layout full + AUX: la card Sunsynk mostra al massimo 2 load essenziali. Load 3-6 verranno tolti dal JSON generato.
            </div>
          </div>

          <details class="energy-advanced-details">
            <summary>
              <span>Configurazione completa</span>
              <small>Scegli una sezione: non viene piu mostrato tutto insieme</small>
            </summary>
          <div class="energy-section-nav">
            <button
              v-for="section in energySetupSections"
              :key="section.key"
              type="button"
              class="energy-section-tab"
              :class="{active: energySetupSection === section.key}"
              @click="energySetupSection = section.key"
            >
              <strong>{{ section.label }}</strong>
              <small>{{ section.hint }}</small>
            </button>
          </div>
          <div class="energy-layout">
            <section class="energy-group" v-show="energySetupSection === 'topology'">
              <h4>Generale / Topology</h4>
              <div class="form-grid">
                <label>Enabled<input type="checkbox" v-model="energyForm.enabled" /></label>
                <label>Theme
                  <select v-model="energyForm.theme">
                    <option value="classic_flow">Classic Inverter</option>
                    <option value="technical_dark">Technical Dark</option>
                    <option value="minimal_light">Minimal Light</option>
                  </select>
                </label>
                <label>Sfondo dashboard Energy<input type="color" v-model="energyForm.dashboard_background_color" /></label>
                <label>Mostra Sankey Card<input type="checkbox" v-model="energyForm.show_sankey" /></label>
                <label>Cardstyle
                  <select v-model="energyWizardForm.cardstyle" @change="onEnergyCardstyleChange">
                    <option value="full">full</option><option value="compact">compact</option><option value="lite">lite</option><option value="minimal">minimal</option>
                  </select>
                </label>
                <label>Show Solar<input type="checkbox" v-model="energyWizardForm.show_solar" /></label>
                <label>Show Battery<input type="checkbox" v-model="energyWizardForm.show_battery" /></label>
                <label>Show Grid<input type="checkbox" v-model="energyWizardForm.show_grid" /></label>
                <label>Dynamic line width<input type="checkbox" v-model="energyWizardForm.dynamic_line_width" /></label>
                <label>Line width min<input type="number" min="1" max="6" step="1" v-model.number="energyWizardForm.min_line_width" /></label>
                <label>Line width max<input type="number" min="1" max="8" step="1" v-model.number="energyWizardForm.max_line_width" /></label>
                <label>Wide layout<input type="checkbox" v-model="energyWizardForm.wide" /></label>
                <label>Numero stringhe solari (MPPT)<input type="number" min="1" max="6" v-model.number="energyWizardForm.solar_mppts" /></label>
                <label>Numero batterie<input type="number" min="1" max="2" v-model.number="energyWizardForm.battery_count" /></label>
                <label>Numero carichi casa (additional_loads)<input type="number" min="0" max="6" v-model.number="energyWizardForm.additional_loads" /></label>
              </div>
              <div class="energy-subblock">
                <h4>Carichi extra solo Sankey</h4>
                <small>Fino a 16 sensori di potenza aggiunti solo al grafico Sankey, senza comparire nella card Sunsynk.</small>
                <div class="energy-repeat-grid">
                  <div v-for="n in 16" :key="`sankey-extra-${n}`" class="energy-mini-block">
                    <strong>Extra {{ n }}</strong>
                    <label>Nome<input type="text" v-model="energyForm.sankey_extra_loads[n - 1].name" /></label>
                    <label>Entity ID<input type="text" v-model="energyForm.sankey_extra_loads[n - 1].entity_id" placeholder="sensor..." /></label>
                    <label>Colore<input type="color" v-model="energyForm.sankey_extra_loads[n - 1].color" /></label>
                  </div>
                </div>
              </div>
            </section>

            <section class="energy-group" v-show="energySetupSection === 'inverter'">
              <h4>Inverter</h4>
              <div class="form-grid">
                <label>Inverter modern<input type="checkbox" v-model="energyWizardForm.inverter_modern" /></label>
                <label>Inverter auto-scale<input type="checkbox" v-model="energyWizardForm.inverter_auto_scale" /></label>
                <label>Inverter three-phase<input type="checkbox" v-model="energyWizardForm.inverter_three_phase" /></label>
                <label>Inverter tensione (V) (entity_id)<input type="text" v-model="energyForm.inverter_voltage_entity_id" /></label>
                <label>Frequenza carico (Hz) (entity_id)<input type="text" v-model="energyForm.load_frequency_entity_id" /></label>
              </div>
            </section>

            <section class="energy-group" v-show="energySetupSection === 'solar'">
              <h4>Solar</h4>
              <div class="energy-subblock">
                <strong>Impostazioni solare</strong>
                <div class="form-grid">
                  <label>Colore Solar<input type="color" v-model="energyWizardForm.color_solar" /></label>
                  <label>Solar max power (W)<input type="number" min="100" step="100" v-model.number="energyWizardForm.solar_max_power" /></label>
                  <label>Solar speed<input type="number" min="1" max="20" step="1" v-model.number="energyWizardForm.solar_animation_speed" /></label>
                  <label>Solar show daily<input type="checkbox" v-model="energyWizardForm.solar_show_daily" /></label>
                  <label>PV installed kWp<input type="number" min="0" step="0.1" v-model.number="energyForm.pv_installed_kwp" /></label>
                  <label>PV totale live (entity_id)<input type="text" v-model="energyWizardForm.pv_total" placeholder="sensor.totale_pv" /></label>
                </div>
              </div>
              <div class="energy-subblock" v-if="solarMpptCount >= 1">
                <strong>PV1</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Nome<input type="text" v-model="energyWizardForm.pv1_name" placeholder="Privato" /></label>
                  <label>P nominale (W)<input type="number" min="0" step="10" v-model.number="energyWizardForm.pv1_max_power" /></label>
                  <label>Entita potenza<input type="text" v-model="energyForm.pv_power_entity_id" /></label>
                  <label>Entita tensione<input type="text" v-model="energyWizardForm.pv1_voltage_109" /></label>
                  <label>Entita corrente<input type="text" v-model="energyWizardForm.pv1_current_110" /></label>
                </div>
              </div>
              <div class="energy-subblock" v-if="solarMpptCount >= 2">
                <strong>PV2</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Nome<input type="text" v-model="energyWizardForm.pv2_name" placeholder="Portoni" /></label>
                  <label>P nominale (W)<input type="number" min="0" step="10" v-model.number="energyWizardForm.pv2_max_power" /></label>
                  <label>Entita potenza<input type="text" v-model="energyWizardForm.pv2_power_187" /></label>
                  <label>Entita tensione<input type="text" v-model="energyWizardForm.pv2_voltage_111" /></label>
                  <label>Entita corrente<input type="text" v-model="energyWizardForm.pv2_current_112" /></label>
                </div>
              </div>
              <div class="energy-subblock" v-if="solarMpptCount >= 3">
                <strong>PV3</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Nome<input type="text" v-model="energyWizardForm.pv3_name" placeholder="Legnaia" /></label>
                  <label>P nominale (W)<input type="number" min="0" step="10" v-model.number="energyWizardForm.pv3_max_power" /></label>
                  <label>Entita potenza<input type="text" v-model="energyWizardForm.pv3_power_188" /></label>
                  <label>Entita tensione<input type="text" v-model="energyWizardForm.pv3_voltage_113" /></label>
                  <label>Entita corrente<input type="text" v-model="energyWizardForm.pv3_current_114" /></label>
                </div>
              </div>
              <div class="energy-subblock" v-if="solarMpptCount >= 4">
                <strong>PV4</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Nome<input type="text" v-model="energyWizardForm.pv4_name" /></label>
                  <label>P nominale (W)<input type="number" min="0" step="10" v-model.number="energyWizardForm.pv4_max_power" /></label>
                  <label>Entita potenza<input type="text" v-model="energyWizardForm.pv4_power_189" /></label>
                  <label>Entita tensione<input type="text" v-model="energyWizardForm.pv4_voltage_115" /></label>
                  <label>Entita corrente<input type="text" v-model="energyWizardForm.pv4_current_116" /></label>
                </div>
              </div>
              <div class="energy-subblock" v-if="solarMpptCount >= 5">
                <strong>PV5</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Nome<input type="text" v-model="energyWizardForm.pv5_name" /></label>
                  <label>P nominale (W)<input type="number" min="0" step="10" v-model.number="energyWizardForm.pv5_max_power" /></label>
                  <label>Entita potenza<input type="text" v-model="energyWizardForm.pv5_power" /></label>
                  <label>Entita tensione<input type="text" v-model="energyWizardForm.pv5_voltage" /></label>
                  <label>Entita corrente<input type="text" v-model="energyWizardForm.pv5_current" /></label>
                </div>
              </div>
              <div class="energy-subblock" v-if="solarMpptCount >= 6">
                <strong>PV6</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Nome<input type="text" v-model="energyWizardForm.pv6_name" /></label>
                  <label>P nominale (W)<input type="number" min="0" step="10" v-model.number="energyWizardForm.pv6_max_power" /></label>
                  <label>Entita potenza<input type="text" v-model="energyWizardForm.pv6_power" /></label>
                  <label>Entita tensione<input type="text" v-model="energyWizardForm.pv6_voltage" /></label>
                  <label>Entita corrente<input type="text" v-model="energyWizardForm.pv6_current" /></label>
                </div>
              </div>
            </section>

            <section class="energy-group" v-show="energySetupSection === 'battery'">
              <h4>Battery</h4>
              <div class="energy-subblock">
                <strong>Impostazioni batterie</strong>
                <div class="form-grid">
                  <label>Colore Battery<input type="color" v-model="energyWizardForm.color_battery" /></label>
                  <label>Numero batterie<input type="number" min="1" max="2" v-model.number="energyWizardForm.battery_count" /></label>
                  <label>Battery capacity (Wh)<input type="number" min="100" step="100" v-model.number="energyWizardForm.battery_energy_wh" /></label>
                  <label>Soglia scarica batterie (%)<input type="number" min="0" max="100" step="1" v-model.number="energyWizardForm.battery_shutdown_soc" /></label>
                  <label>Battery max power (W)<input type="number" min="100" step="100" v-model.number="energyWizardForm.battery_max_power" /></label>
                  <label>Battery speed<input type="number" min="1" max="20" step="1" v-model.number="energyWizardForm.battery_animation_speed" /></label>
                  <label>Battery auto-scale<input type="checkbox" v-model="energyWizardForm.battery_auto_scale" /></label>
                  <label>Battery show daily<input type="checkbox" v-model="energyWizardForm.battery_show_daily" /></label>
                </div>
              </div>
              <div class="energy-subblock">
                <strong>Batteria 1</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Nome<input type="text" v-model="energyWizardForm.battery1_name" placeholder="Batteria" /></label>
                  <label>Entita potenza<input type="text" v-model="energyForm.battery_power_entity_id" /></label>
                  <label>Entita tensione<input type="text" v-model="energyWizardForm.battery_voltage_183" /></label>
                  <label>Entita corrente<input type="text" v-model="energyWizardForm.battery_current_191" /></label>
                  <label>Entita SOC<input type="text" v-model="energyForm.battery_soc_entity_id" /></label>
                </div>
              </div>
              <div class="energy-subblock">
                <strong>Batteria 2</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Nome<input type="text" v-model="energyWizardForm.battery2_name" placeholder="Batteria 2" /></label>
                  <label>Entita potenza<input type="text" v-model="energyWizardForm.battery2_power_190" /></label>
                  <label>Entita tensione<input type="text" v-model="energyWizardForm.battery2_voltage_183" /></label>
                  <label>Entita corrente<input type="text" v-model="energyWizardForm.battery2_current_191" /></label>
                  <label>Entita SOC<input type="text" v-model="energyWizardForm.battery2_soc_184" /></label>
                </div>
              </div>
              <div class="energy-subblock">
                <strong>Batteria 3</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Nome<input type="text" v-model="energyWizardForm.battery3_name" placeholder="Batteria 3" /></label>
                  <label>Entita potenza<input type="text" v-model="energyWizardForm.battery3_power_190" /></label>
                  <label>Entita tensione<input type="text" v-model="energyWizardForm.battery3_voltage_183" /></label>
                  <label>Entita corrente<input type="text" v-model="energyWizardForm.battery3_current_191" /></label>
                  <label>Entita SOC<input type="text" v-model="energyWizardForm.battery3_soc_184" /></label>
                </div>
              </div>
            </section>

            <section class="energy-group" v-show="energySetupSection === 'load'">
              <h4>Load</h4>
              <div class="energy-subblock">
                <strong>Impostazioni carichi</strong>
                <div class="form-grid">
                  <label>Colore Load<input type="color" v-model="energyWizardForm.color_load" /></label>
                  <label>Load max power (W)<input type="number" min="100" step="100" v-model.number="energyWizardForm.load_max_power" /></label>
                  <label>Load speed<input type="number" min="1" max="20" step="1" v-model.number="energyWizardForm.load_animation_speed" /></label>
                  <label>Load auto-scale<input type="checkbox" v-model="energyWizardForm.load_auto_scale" /></label>
                  <label>Load show daily<input type="checkbox" v-model="energyWizardForm.load_show_daily" /></label>
                  <label>Load dynamic colour<input type="checkbox" v-model="energyWizardForm.load_dynamic_colour" /></label>
                  <label>Load dynamic icon<input type="checkbox" v-model="energyWizardForm.load_dynamic_icon" /></label>
                  <label>Load invert flow<input type="checkbox" v-model="energyWizardForm.load_invert_flow" /></label>
                  <label>Load max colour<input type="color" v-model="energyWizardForm.load_max_colour" /></label>
                  <label>Load off colour<input type="color" v-model="energyWizardForm.load_off_colour" /></label>
                  <label>Numero load essenziali<input type="number" min="0" max="6" step="1" v-model.number="energyWizardForm.additional_loads" /></label>
                  <label>Nome gruppo Home<input type="text" v-model="energyWizardForm.load_essential_name" /></label>
                  <label>Etichetta daily load<input type="text" v-model="energyWizardForm.load_label_daily" /></label>
                </div>
              </div>
              <div class="energy-subblock">
                <strong>Casa / Home principale</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Potenza casa/inverter (entity_id)<input type="text" v-model="energyForm.home_power_entity_id" /></label>
                  <label>Essential principale (entity_id)<input type="text" v-model="energyWizardForm.essential_power" /></label>
                </div>
              </div>
              <div class="energy-subblock">
                <strong>Load essenziali 1-6</strong>
                <div class="energy-load-grid">
                  <div class="energy-load-row" v-for="n in 6" :key="`load-${n}`">
                    <strong>Load {{ n }}</strong>
                    <label>Nome<input type="text" v-model="energyWizardForm[`load${n}_name`]" /></label>
                    <label>Entita potenza<input type="text" v-model="energyWizardForm[`essential_load${n}`]" /></label>
                    <label>Icona
                      <select v-model="energyWizardForm[`load${n}_icon`]">
                        <option v-for="i in energyIconOptions" :key="`l${n}-${i}`" :value="i">{{ i }}</option>
                      </select>
                    </label>
                    <label>Icona custom<input type="text" v-model="energyWizardForm[`load${n}_icon`]" placeholder="default oppure mdi:..." /></label>
                  </div>
                </div>
              </div>
            </section>

            <section class="energy-group" v-show="energySetupSection === 'aux'">
              <h4>AUX</h4>
              <div class="energy-subblock">
                <strong>Ramo AUX</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Mostra ramo AUX<input type="checkbox" v-model="energyWizardForm.show_aux" /></label>
                  <label>Nome AUX<input type="text" v-model="energyWizardForm.load_aux_name" /></label>
                  <label>AUX type<input type="text" v-model="energyWizardForm.load_aux_type" placeholder="default" /></label>
                  <label>AUX colour<input type="color" v-model="energyWizardForm.load_aux_colour" /></label>
                  <label>AUX off colour<input type="color" v-model="energyWizardForm.load_aux_off_colour" /></label>
                  <label>AUX dynamic colour<input type="checkbox" v-model="energyWizardForm.load_aux_dynamic_colour" /></label>
                  <label>AUX show absolute<input type="checkbox" v-model="energyWizardForm.load_show_absolute_aux" /></label>
                  <label>AUX show daily<input type="checkbox" v-model="energyWizardForm.load_show_daily_aux" /></label>
                  <label>Numero AUX load<input type="number" min="0" max="7" step="1" v-model.number="energyWizardForm.load_aux_loads" /></label>
                  <label>AUX principale (entity_id)<input type="text" v-model="energyWizardForm.aux_power_166" /></label>
                  <template v-for="n in 7" :key="`aux-wizard-${n}`">
                    <label>AUX load {{ n }} nome<input type="text" v-model="energyWizardForm[`load_aux_load${n}_name`]" /></label>
                    <label>AUX load {{ n }} entity_id<input type="text" v-model="energyWizardForm[`aux_load${n}`]" /></label>
                    <label>AUX load {{ n }} icon<input type="text" v-model="energyWizardForm[`load_aux_load${n}_icon`]" placeholder="default oppure mdi:..." /></label>
                  </template>
                </div>
              </div>
            </section>

            <section class="energy-group" v-show="energySetupSection === 'grid'">
              <h4>Grid</h4>
              <div class="energy-subblock">
                <strong>Rete principale</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Nome rete<input type="text" v-model="energyWizardForm.grid_name" /></label>
                  <label>Rete/Grid potenza (entity_id)<input type="text" v-model="energyForm.grid_power_entity_id" /></label>
                  <label>Rete CT potenza (entity_id)<input type="text" v-model="energyWizardForm.grid_ct_power_172" /></label>
                  <label>Rete connessa stato (entity_id)<input type="text" v-model="energyWizardForm.grid_connected_status_194" /></label>
                </div>
              </div>
              <div class="energy-subblock">
                <strong>Impostazioni rete</strong>
                <div class="form-grid">
                  <label>Colore Grid<input type="color" v-model="energyWizardForm.color_grid" /></label>
                  <label>Grid export color<input type="color" v-model="energyWizardForm.color_grid_export" /></label>
                  <label>Grid off color<input type="color" v-model="energyWizardForm.color_grid_off" /></label>
                  <label>No-grid color<input type="color" v-model="energyWizardForm.color_no_grid" /></label>
                  <label>Grid max power (W)<input type="number" min="100" step="100" v-model.number="energyWizardForm.grid_max_power" /></label>
                  <label>Grid speed<input type="number" min="1" max="20" step="1" v-model.number="energyWizardForm.grid_animation_speed" /></label>
                  <label>Grid auto-scale<input type="checkbox" v-model="energyWizardForm.grid_auto_scale" /></label>
                  <label>Grid invert<input type="checkbox" v-model="energyWizardForm.grid_invert_grid" /></label>
                  <label>Grid show absolute<input type="checkbox" v-model="energyWizardForm.grid_show_absolute" /></label>
                  <label>Grid invert flow<input type="checkbox" v-model="energyWizardForm.grid_invert_flow" /></label>
                  <label>Energy cost decimals<input type="number" min="0" max="4" step="1" v-model.number="energyWizardForm.grid_energy_cost_decimals" /></label>
                </div>
              </div>
              <div class="energy-subblock">
                <strong>Non-Essential</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Mostra non-essential<input type="checkbox" v-model="energyWizardForm.grid_show_nonessential" /></label>
                  <label>Nome non-essential<input type="text" v-model="energyWizardForm.grid_nonessential_name" /></label>
                  <label>Non-Essential principale<input type="text" v-model="energyWizardForm.nonessential_power" /></label>
                  <label>Non-Essential load 1 nome<input type="text" v-model="energyWizardForm.grid_load1_name" /></label>
                  <label>Non-Essential load 1<input type="text" v-model="energyWizardForm.non_essential_load1" /></label>
                  <label>Non-Essential load 2 nome<input type="text" v-model="energyWizardForm.grid_load2_name" /></label>
                  <label>Non-Essential load 2<input type="text" v-model="energyWizardForm.non_essential_load2" /></label>
                  <label>Non-Essential load 3 nome<input type="text" v-model="energyWizardForm.grid_load3_name" /></label>
                  <label>Non-Essential load 3<input type="text" v-model="energyWizardForm.non_essential_load3" /></label>
                  <label>Grid additional loads<input type="number" min="0" max="3" step="1" v-model.number="energyWizardForm.grid_additional_loads" /></label>
                </div>
              </div>
              <div class="energy-subblock">
                <strong>Icone rete</strong>
                <div class="energy-load-grid">
                  <label>Non-essential icon<select v-model="energyWizardForm.grid_nonessential_icon"><option v-for="i in energyIconOptions" :key="`gn-${i}`" :value="i">{{ i }}</option></select><input type="text" v-model="energyWizardForm.grid_nonessential_icon" placeholder="mdi:home-outline" /></label>
                  <label>Grid load 1 icon<select v-model="energyWizardForm.grid_load1_icon"><option v-for="i in energyIconOptions" :key="`g1-${i}`" :value="i">{{ i }}</option></select><input type="text" v-model="energyWizardForm.grid_load1_icon" placeholder="default" /></label>
                  <label>Grid load 2 icon<select v-model="energyWizardForm.grid_load2_icon"><option v-for="i in energyIconOptions" :key="`g2-${i}`" :value="i">{{ i }}</option></select><input type="text" v-model="energyWizardForm.grid_load2_icon" placeholder="default" /></label>
                  <label>Grid load 3 icon<select v-model="energyWizardForm.grid_load3_icon"><option v-for="i in energyIconOptions" :key="`g3-${i}`" :value="i">{{ i }}</option></select><input type="text" v-model="energyWizardForm.grid_load3_icon" placeholder="default" /></label>
                  <label>Grid import icon<select v-model="energyWizardForm.grid_import_icon"><option v-for="i in energyIconOptions" :key="`gi-${i}`" :value="i">{{ i }}</option></select><input type="text" v-model="energyWizardForm.grid_import_icon" placeholder="mdi:transmission-tower-import" /></label>
                  <label>Grid export icon<select v-model="energyWizardForm.grid_export_icon"><option v-for="i in energyIconOptions" :key="`ge-${i}`" :value="i">{{ i }}</option></select><input type="text" v-model="energyWizardForm.grid_export_icon" placeholder="mdi:transmission-tower-export" /></label>
                  <label>Grid disconnected icon<select v-model="energyWizardForm.grid_disconnected_icon"><option v-for="i in energyIconOptions" :key="`gd-${i}`" :value="i">{{ i }}</option></select><input type="text" v-model="energyWizardForm.grid_disconnected_icon" placeholder="mdi:transmission-tower-off" /></label>
                </div>
              </div>
            </section>

            <section class="energy-group" v-show="energySetupSection === 'daily'">
              <h4>Entita Giornaliere</h4>
              <div class="energy-subblock">
                <strong>Produzione / carichi</strong>
                <div class="form-grid energy-entity-grid">
                  <label>PV energy today entity id<input type="text" v-model="energyForm.pv_energy_today_entity_id" /></label>
                  <label>Home energy today entity id<input type="text" v-model="energyForm.home_energy_today_entity_id" /></label>
                </div>
              </div>
              <div class="energy-subblock">
                <strong>Batteria giornaliera</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Battery charge today entity id<input type="text" v-model="energyWizardForm.day_battery_charge_70" /></label>
                  <label>Battery discharge today entity id<input type="text" v-model="energyWizardForm.day_battery_discharge_71" /></label>
                </div>
              </div>
              <div class="energy-subblock">
                <strong>Rete giornaliera</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Grid import today entity id<input type="text" v-model="energyForm.grid_import_today_entity_id" /></label>
                  <label>Grid export today entity id<input type="text" v-model="energyForm.grid_export_today_entity_id" /></label>
                  <label>Grid show daily buy<input type="checkbox" v-model="energyWizardForm.grid_show_daily_buy" /></label>
                  <label>Grid show daily sell<input type="checkbox" v-model="energyWizardForm.grid_show_daily_sell" /></label>
                  <label>Label daily buy<input type="text" v-model="energyWizardForm.grid_label_daily_buy" /></label>
                  <label>Label daily sell<input type="text" v-model="energyWizardForm.grid_label_daily_sell" /></label>
                </div>
              </div>
              <div class="energy-subblock">
                <strong>Energy Time - statistic_id storici</strong>
                <div class="form-grid energy-entity-grid">
                  <label>Solare statistic_id<input type="text" v-model="energyForm.energy_time_pv_stat_ids" placeholder="sensor.xxx_total_production" /></label>
                  <label>Casa statistic_id<input type="text" v-model="energyForm.energy_time_load_stat_ids" placeholder="sensor.xxx_total_load" /></label>
                  <label>Rete import statistic_id<input type="text" v-model="energyForm.energy_time_grid_import_stat_ids" placeholder="sensor.xxx_total_energy_import" /></label>
                  <label>Rete export statistic_id<input type="text" v-model="energyForm.energy_time_grid_export_stat_ids" placeholder="sensor.xxx_total_energy_export" /></label>
                  <label>Batteria carica statistic_id<input type="text" v-model="energyForm.energy_time_battery_charge_stat_ids" placeholder="sensor.xxx_total_battery_charge" /></label>
                  <label>Batteria scarica statistic_id<input type="text" v-model="energyForm.energy_time_battery_discharge_stat_ids" placeholder="sensor.xxx_total_battery_discharge" /></label>
                  <label>Gas statistic_id<input type="text" v-model="energyForm.energy_time_gas_stat_ids" placeholder="sensor.xxx_gas" /></label>
                  <label>Solare termico statistic_id<input type="text" v-model="energyForm.energy_time_solar_thermal_stat_ids" placeholder="sensor.xxx_solar_thermal" /></label>
                </div>
                <small>Prioritari per Energy Time. Puoi inserire piu statistic_id separati da virgola o spazio.</small>
              </div>
            </section>

            <section class="energy-group" v-show="energySetupSection === 'signs'">
              <h4>Segno Entita (+/-)</h4>
              <div class="form-grid">
                <label v-for="f in energySignFields" :key="`sg-${f.key}`">
                  {{ f.label }}
                  <select v-model="energyEntitySigns[f.key]" @change="syncEnergySignsJsonFromUi">
                    <option value="positive">Positivo (+)</option>
                    <option value="negative">Negativo (-)</option>
                  </select>
                </label>
              </div>
            </section>

            <section class="energy-group" v-show="energySetupSection === 'kflow'">
              <h4>K Flow</h4>
              <div class="energy-subblock">
                <strong>Versi flusso</strong>
                <div class="form-grid energy-entity-grid">
                  <label class="toggle-line">Inverti verso batteria<input type="checkbox" v-model="energyForm.k_flow_invert_battery_power" @change="syncKFlowJsonFromUi" /></label>
                  <label class="toggle-line">Inverti verso rete<input type="checkbox" v-model="energyForm.k_flow_invert_grid_power" @change="syncKFlowJsonFromUi" /></label>
                </div>
              </div>
              <div class="energy-subblock">
                <strong>Entita mancanti K Flow</strong>
                <div class="form-grid energy-entity-grid">
                  <label>PV totale storico<input type="text" v-model="energyForm.k_flow_total_pv_gen_entity" @change="syncKFlowJsonFromUi" placeholder="sensor.xxx_total_pv_generation" /></label>
                  <label>Battery temp 1<input type="text" v-model="energyForm.k_flow_battery_temp1" @change="syncKFlowJsonFromUi" placeholder="sensor.xxx_battery_temp_1" /></label>
                  <label>Battery temp 2<input type="text" v-model="energyForm.k_flow_battery_temp2" @change="syncKFlowJsonFromUi" placeholder="sensor.xxx_battery_temp_2" /></label>
                  <label>BMS / MOS temp<input type="text" v-model="energyForm.k_flow_battery_mos" @change="syncKFlowJsonFromUi" placeholder="sensor.xxx_bms_temp" /></label>
                  <label>Min SOC entity (%)<input type="text" v-model="energyForm.k_flow_battery_shutdown_soc_entity" @change="syncKFlowJsonFromUi" placeholder="sensor.xxx_battery_min_soc" /></label>
                  <label>Min SOC manuale (%)<input type="number" min="0" max="100" step="1" v-model.number="energyForm.k_flow_battery_shutdown_soc_manual" @change="syncKFlowJsonFromUi" placeholder="10" /></label>
                  <label>Logo alto (URL o /local/...)<input type="text" v-model="energyForm.k_flow_brand_logo" @change="syncKFlowJsonFromUi" placeholder="/local/ekonex-logo.png" /></label>
                  <label>Label barra potenza<input type="text" v-model="energyForm.k_flow_pwr_bar_label" @change="syncKFlowJsonFromUi" placeholder="BATT" /></label>
                  <label>AUX nome<input type="text" v-model="energyForm.k_flow_aux_name" @change="syncKFlowJsonFromUi" placeholder="AUX" /></label>
                  <label>AUX potenza<input type="text" v-model="energyForm.k_flow_aux_power" @change="syncKFlowJsonFromUi" placeholder="sensor.xxx_aux_power" /></label>
                  <template v-for="n in 7" :key="`kflow-aux-${n}`">
                    <label>AUX {{ n }} nome<input type="text" v-model="energyForm[`k_flow_aux_load${n}_name`]" @change="syncKFlowJsonFromUi" :placeholder="`AUX ${n}`" /></label>
                    <label>AUX {{ n }} potenza<input type="text" v-model="energyForm[`k_flow_aux_load${n}`]" @change="syncKFlowJsonFromUi" :placeholder="`sensor.xxx_aux_${n}`" /></label>
                  </template>
                  <label>Icona casa
                    <select v-model="energyForm.k_flow_home_icon" @change="syncKFlowJsonFromUi">
                      <option value="">Default</option>
                      <option value="home-icon.png">Default K Flow</option>
                      <option value="home-smart-glass.png">Smart glass</option>
                      <option value="home-smart-glass-2floor.png">Smart glass 2 piani</option>
                      <option value="home-modern-villa.png">Villa moderna</option>
                      <option value="home-ref-farmhouse.png">Farmhouse classica</option>
                      <option value="home-ref-modern-orange.png">Moderna arancio</option>
                      <option value="home-ref-angular-luxury.png">Luxury angolare</option>
                      <option value="home-ref-flat-roof.png">Tetto piano</option>
                      <option value="home-ref-orange-cottage.png">Cottage arancio</option>
                      <option value="home-ref-suburban-garage.png">Villetta garage</option>
                      <option value="home-ref-isometric-cottage.png">Cottage isometrico</option>
                      <option value="home-ref-flat-roof-alt.png">Tetto piano alt</option>
                    </select>
                  </label>
                  <label>Riquadro basso sinistra label<input type="text" v-model="energyForm.k_flow_min_cell_label" @change="syncKFlowJsonFromUi" placeholder="Min cell" /></label>
                  <label>Riquadro basso sinistra entity<input type="text" v-model="energyForm.k_flow_min_cell_entity" @change="syncKFlowJsonFromUi" placeholder="sensor..." /></label>
                  <label>Riquadro basso centro label<input type="text" v-model="energyForm.k_flow_max_cell_label" @change="syncKFlowJsonFromUi" placeholder="Max cell" /></label>
                  <label>Riquadro basso centro entity<input type="text" v-model="energyForm.k_flow_max_cell_entity" @change="syncKFlowJsonFromUi" placeholder="sensor..." /></label>
                  <label>Riquadro basso destra label<input type="text" v-model="energyForm.k_flow_batt_dis_label" @change="syncKFlowJsonFromUi" placeholder="Scarica oggi" /></label>
                  <label>Riquadro basso destra entity<input type="text" v-model="energyForm.k_flow_batt_dis_entity" @change="syncKFlowJsonFromUi" placeholder="sensor..." /></label>
                </div>
              </div>
              <div class="energy-subblock">
                <strong>Scala / capacità</strong>
                <div class="form-grid">
                  <label>PV max power (W)<input type="number" min="0" step="100" v-model.number="energyForm.kflow_solar_max_power_w" @change="syncKFlowScaleToWizard" /></label>
                  <label>Load max power (W)<input type="number" min="0" step="100" v-model.number="energyForm.kflow_load_max_power_w" @change="syncKFlowScaleToWizard" /></label>
                  <label>Grid max power (W)<input type="number" min="0" step="100" v-model.number="energyForm.kflow_grid_max_power_w" @change="syncKFlowScaleToWizard" /></label>
                  <label>Battery capacity (Wh)<input type="number" min="0" step="100" v-model.number="energyForm.kflow_battery_capacity_wh" @change="syncKFlowScaleToWizard" /></label>
                  <label>Battery max power (W)<input type="number" min="0" step="100" v-model.number="energyForm.kflow_battery_max_power_w" @change="syncKFlowScaleToWizard" /></label>
                  <label>Battery min SOC (%)<input type="number" min="0" max="100" step="1" v-model.number="energyForm.kflow_battery_shutdown_soc" @change="syncKFlowScaleToWizard" /></label>
                </div>
                <small>Questi valori sono usati direttamente dalla dashboard K Flow. Il JSON avanzato resta solo per override speciali.</small>
              </div>
            </section>

            <section class="energy-group" v-show="energySetupSection === 'json'">
              <h4>JSON Avanzato</h4>
              <div class="form-grid">
                <label style="grid-column: 1 / -1;">
                  <small>I flag segno (+/-) regolano la convenzione per ogni entita di potenza nella dashboard.</small>
                </label>
                <label style="grid-column: 1 / -1;">Sunsynk card config JSON (wrapper standalone)
                  <textarea v-model="energyForm.sunsynk_card_config_json" rows="10" placeholder='{"solar":{"mppts":2},"battery":{"count":1},"load":{"additional_loads":2}}'></textarea>
                  <small>Configurazione completa card Sunsynk. Valido JSON object. Viene applicata al wrapper `energy-dashboard/sunsynk-wrapper.html`.</small>
                </label>
                <div class="energy-subblock" style="grid-column: 1 / -1;">
                  <strong>Entita aggiuntive K Flow</strong>
                  <div class="form-grid energy-entity-grid">
                    <label class="toggle-line">Inverti verso batteria<input type="checkbox" v-model="energyForm.k_flow_invert_battery_power" @change="syncKFlowJsonFromUi" /></label>
                    <label class="toggle-line">Inverti verso rete<input type="checkbox" v-model="energyForm.k_flow_invert_grid_power" @change="syncKFlowJsonFromUi" /></label>
                    <label>PV totale storico<input type="text" v-model="energyForm.k_flow_total_pv_gen_entity" @change="syncKFlowJsonFromUi" placeholder="sensor.xxx_total_pv_generation" /></label>
                    <label>Battery temp 1<input type="text" v-model="energyForm.k_flow_battery_temp1" @change="syncKFlowJsonFromUi" placeholder="sensor.xxx_battery_temp_1" /></label>
                    <label>Battery temp 2<input type="text" v-model="energyForm.k_flow_battery_temp2" @change="syncKFlowJsonFromUi" placeholder="sensor.xxx_battery_temp_2" /></label>
                    <label>BMS / MOS temp<input type="text" v-model="energyForm.k_flow_battery_mos" @change="syncKFlowJsonFromUi" placeholder="sensor.xxx_bms_temp" /></label>
                    <label>Min SOC entity (%)<input type="text" v-model="energyForm.k_flow_battery_shutdown_soc_entity" @change="syncKFlowJsonFromUi" placeholder="sensor.xxx_battery_min_soc" /></label>
                    <label>Min SOC manuale (%)<input type="number" min="0" max="100" step="1" v-model.number="energyForm.k_flow_battery_shutdown_soc_manual" @change="syncKFlowJsonFromUi" placeholder="10" /></label>
                    <label>Logo alto (URL o /local/...)<input type="text" v-model="energyForm.k_flow_brand_logo" @change="syncKFlowJsonFromUi" placeholder="/local/ekonex-logo.png" /></label>
                    <label>Label barra potenza<input type="text" v-model="energyForm.k_flow_pwr_bar_label" @change="syncKFlowJsonFromUi" placeholder="BATT" /></label>
                    <label>AUX nome<input type="text" v-model="energyForm.k_flow_aux_name" @change="syncKFlowJsonFromUi" placeholder="AUX" /></label>
                    <label>AUX potenza<input type="text" v-model="energyForm.k_flow_aux_power" @change="syncKFlowJsonFromUi" placeholder="sensor.xxx_aux_power" /></label>
                    <template v-for="n in 7" :key="`json-kflow-aux-${n}`">
                      <label>AUX {{ n }} nome<input type="text" v-model="energyForm[`k_flow_aux_load${n}_name`]" @change="syncKFlowJsonFromUi" :placeholder="`AUX ${n}`" /></label>
                      <label>AUX {{ n }} potenza<input type="text" v-model="energyForm[`k_flow_aux_load${n}`]" @change="syncKFlowJsonFromUi" :placeholder="`sensor.xxx_aux_${n}`" /></label>
                    </template>
                    <label>Icona casa
                      <select v-model="energyForm.k_flow_home_icon" @change="syncKFlowJsonFromUi">
                        <option value="">Default</option>
                        <option value="home-icon.png">Default K Flow</option>
                        <option value="home-smart-glass.png">Smart glass</option>
                        <option value="home-smart-glass-2floor.png">Smart glass 2 piani</option>
                        <option value="home-modern-villa.png">Villa moderna</option>
                        <option value="home-ref-farmhouse.png">Farmhouse classica</option>
                        <option value="home-ref-modern-orange.png">Moderna arancio</option>
                        <option value="home-ref-angular-luxury.png">Luxury angolare</option>
                        <option value="home-ref-flat-roof.png">Tetto piano</option>
                        <option value="home-ref-orange-cottage.png">Cottage arancio</option>
                        <option value="home-ref-suburban-garage.png">Villetta garage</option>
                        <option value="home-ref-isometric-cottage.png">Cottage isometrico</option>
                        <option value="home-ref-flat-roof-alt.png">Tetto piano alt</option>
                      </select>
                    </label>
                    <label>Riquadro basso sinistra label<input type="text" v-model="energyForm.k_flow_min_cell_label" @change="syncKFlowJsonFromUi" placeholder="Min cell" /></label>
                    <label>Riquadro basso sinistra entity<input type="text" v-model="energyForm.k_flow_min_cell_entity" @change="syncKFlowJsonFromUi" placeholder="sensor..." /></label>
                    <label>Riquadro basso centro label<input type="text" v-model="energyForm.k_flow_max_cell_label" @change="syncKFlowJsonFromUi" placeholder="Max cell" /></label>
                    <label>Riquadro basso centro entity<input type="text" v-model="energyForm.k_flow_max_cell_entity" @change="syncKFlowJsonFromUi" placeholder="sensor..." /></label>
                    <label>Riquadro basso destra label<input type="text" v-model="energyForm.k_flow_batt_dis_label" @change="syncKFlowJsonFromUi" placeholder="Scarica oggi" /></label>
                    <label>Riquadro basso destra entity<input type="text" v-model="energyForm.k_flow_batt_dis_entity" @change="syncKFlowJsonFromUi" placeholder="sensor..." /></label>
                  </div>
                </div>
                <label style="grid-column: 1 / -1;">K Flow card config JSON (override opzionale)
                  <textarea v-model="energyForm.k_flow_card_config_json" rows="8" placeholder='{"_show_ev":false,"pv_max_power":7500}' @change="syncKFlowUiFromJson"></textarea>
                  <small>Override per `custom:k-flow-card`. Se vuoto, viene generato dai campi sopra e dal JSON Sunsynk.</small>
                </label>
                <label style="grid-column: 1 / -1;">Entita extra JSON (chiave -> entity_id)
                  <textarea v-model="energyWizardForm.entities_extra_json" rows="5" placeholder='{"pv3_power_188":"sensor.xxx","use_timer_248":"sensor.yyy"}'></textarea>
                  <small>Qui puoi mappare qualsiasi chiave entities supportata dalla card, anche se non ha ancora un campo dedicato sopra.</small>
                </label>
                <label style="grid-column: 1 / -1;">Segno entita JSON (chiave -> positive/negative)
                  <textarea v-model="energyForm.entity_signs_json" rows="4" placeholder='{"grid_power_169":"negative","essential_load1":"positive","aux_power_166":"negative"}'></textarea>
                  <small>Override segno per singola entita di potenza nel wrapper (`positive` o `negative`).</small>
                </label>
              </div>
            </section>
          </div>
          </details>
        </section>
        </template>

        <template v-if="tab==='setting'">
        <section class="card">
          <h3>Weather Guard</h3>
          <p class="note">
            Qui imposti quando e-SunMind deve segnalare pericolo meteo a e-Tende.
            Se non sai il valore della facciata, lascia <strong>-1</strong>: vento forte e pioggia funzionano comunque, viene disattivato solo lo stravento verso finestra.
          </p>
          <div class="form-grid">
            <label>Enabled
              <input type="checkbox" v-model="weatherGuardForm.enabled" />
            </label>
            <label>Wind alarm m/s
              <input type="number" min="0" max="80" step="0.1" v-model.number="weatherGuardForm.wind_alarm_ms" />
              <small>Allarme vento forte. 12 m/s = circa 43 km/h.</small>
            </label>
            <label>Rain alarm mm/h
              <input type="number" min="0" max="200" step="0.1" v-model.number="weatherGuardForm.rain_alarm_mm_h" />
              <small>Allarme pioggia. 1.5 mm/h = pioggia moderata.</small>
            </label>
            <label>Stravento min wind m/s
              <input type="number" min="0" max="80" step="0.1" v-model.number="weatherGuardForm.facade_rain_min_wind_ms" />
              <small>Vento minimo per considerare pioggia spinta verso facciata.</small>
            </label>
            <label>Stravento min rain mm/h
              <input type="number" min="0" max="200" step="0.1" v-model.number="weatherGuardForm.facade_rain_min_mm_h" />
              <small>Pioggia minima per attivare controllo stravento.</small>
            </label>
            <label>Facciata azimuth deg (-1 = non configurata)
              <input type="number" min="-1" max="360" step="0.1" v-model.number="weatherGuardForm.facade_azimuth_deg" />
              <small>Direzione verso cui guarda la finestra/facciata: N=0, E=90, S=180, W=270. -1 disattiva stravento.</small>
            </label>
            <label>Facciata half FOV deg
              <input type="number" min="0" max="180" step="0.1" v-model.number="weatherGuardForm.facade_half_fov_deg" />
              <small>Ampiezza cono vento. 60 significa +/-60 gradi rispetto alla facciata.</small>
            </label>
            <label>Stale seconds
              <input type="number" min="30" max="86400" v-model.number="weatherGuardForm.stale_seconds" />
              <small>Dopo quanti secondi i dati meteo diventano vecchi.</small>
            </label>
          </div>
          <p class="note">
            Esempio: facciata verso sud = 180, half FOV = 60. Lo stravento scatta se piove, c'e vento sufficiente e il vento arriva nel cono 120..240 gradi.
          </p>
        </section>

        <section class="card">
          <h3>Air Quality</h3>
          <div class="form-grid">
            <label>Enabled
              <input type="checkbox" v-model="airQualityForm.enabled" />
            </label>
            <label>Provider
              <select v-model="airQualityForm.provider">
                <option value="open_meteo">Open-Meteo</option>
              </select>
            </label>
          </div>
        </section>

        <section class="card">
          <h3>Tende Map MQTT</h3>
          <div class="form-grid">
            <label>Enabled
              <input type="checkbox" v-model="tendeMapForm.enabled" />
            </label>
            <label>MQTT host
              <input type="text" v-model="tendeMapForm.mqtt_host" />
            </label>
            <label>MQTT port
              <input type="number" min="1" max="65535" v-model.number="tendeMapForm.mqtt_port" />
            </label>
            <label>MQTT username
              <input type="text" v-model="tendeMapForm.mqtt_username" />
            </label>
            <label>MQTT password
              <input type="password" v-model="tendeMapForm.mqtt_password" />
            </label>
            <label>Topic state
              <input type="text" v-model="tendeMapForm.topic_state" />
            </label>
            <label>Topic availability
              <input type="text" v-model="tendeMapForm.topic_availability" />
            </label>
            <label>Stale seconds
              <input type="number" min="30" max="86400" v-model.number="tendeMapForm.stale_seconds" />
            </label>
          </div>
        </section>
        </template>

      </main>
    </div>

    <div v-show="tab==='tech'">
      <div class="view-tools">
        <button class="btn ghost" @click="techExpanded = !techExpanded">{{ techExpanded ? 'Riduci campi' : 'Allarga campi' }}</button>
      </div>
      <main class="tech-main">

        <section class="card" v-show="techExpanded">
          <h3>Risposta completa Forecast Solar (raw)</h3>
          <pre class="json">{{ forecastRawText }}</pre>
        </section>

        <section class="card" v-show="techExpanded">
          <h3>Risposta completa Meteo MET (raw)</h3>
          <pre class="json">{{ weatherRawText }}</pre>
        </section>

        <section class="card" v-show="techExpanded">
          <h3>Risposta completa Meteo Open-Meteo (raw)</h3>
          <pre class="json">{{ weatherOpenMeteoRawText }}</pre>
        </section>

        <section class="card" v-show="techExpanded">
          <h3>Risposta completa Air Quality (raw)</h3>
          <pre class="json">{{ airqRawText }}</pre>
        </section>

        <section class="card" v-show="techExpanded">
          <h3>Risposta completa SunCalc (raw)</h3>
          <pre class="json">{{ sunCalcRawText }}</pre>
        </section>

        <section class="card" v-show="techExpanded">
          <h3>Risposta completa JSON runtime (raw)</h3>
          <pre class="json">{{ pretty }}</pre>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import SunCalc from 'suncalc'
import logoEtende from './assets/logo-etende.png'
import logoMain from './assets/logo-main.png'

// Guard against transient null map targets during UI race conditions.
const _leafletLayerAddTo = L.Layer.prototype.addTo
L.Layer.prototype.addTo = function patchedAddTo(target) {
  if (!target || typeof target.addLayer !== 'function') return this
  return _leafletLayerAddTo.call(this, target)
}
const _leafletControlAddTo = L.Control.prototype.addTo
L.Control.prototype.addTo = function patchedControlAddTo(target) {
  if (!target || typeof target.addControl !== 'function') return this
  return _leafletControlAddTo.call(this, target)
}

const tab = ref('user')
const showSplash = ref(true)
const userExpanded = ref(true)
const techExpanded = ref(true)
const appVersion = ref('0.0.0')
const data = ref(null)
const lat = ref(null)
const lon = ref(null)
const timeIndex = ref(10)
const hours = Array.from({ length: 19 }, (_, i) => i + 3)
const timeSteps = Array.from({ length: ((21 - 3) * 4) + 1 }, (_, i) => {
  const total = (3 * 60) + (i * 15)
  return { h: Math.floor(total / 60), m: total % 60 }
})
const cfg = ref({
  pathRadiusM: 102,
  sectorRadiusM: 110,
  sunRadiusM: 95,
  mapZoom: 18,
})

let map = null
let centerMarker = null
let pathLine = null
let horizonCircle = null
let sunLine = null
let sunMarker = null
let sunLineLive = null
let sunMarkerLive = null
let sunriseRay = null
let sunsetRay = null
let sunriseLabel = null
let sunsetLabel = null
let altitudeRing = null
let altitudeGuideLine = null
let altitudeGuideLabel = null
let axisNS = null
let axisWE = null
let pvAzLine = null
let pvAzMarker = null
let windDirLine = null
let windDirMarker = null
let annualElevationBand = null
let annualElevationBandLayers = []
let compassMarkers = []
let tendeSectorLayers = []
let windLayerRetryTimer = 0
const weatherAnimEnabled = ref(false)
const weatherCanvasEl = ref(null)
let weatherRafId = 0
let weatherLastTs = 0
let weatherClouds = []
let weatherRain = []
let weatherMist = []
let blockTogglesInited = false
let tendeMapObj = null
let tendeCenter = null
let tendeRing = null
let tendePoly = null
let tendeStartMarker = null
let tendeEndMarker = null
let tendeEditorExtraLayers = []
let userAutoRefreshTimer = 0
const userAutoRefreshMs = 15000
let loadDataInFlight = false
let loadDataFailStreak = 0
let loadDataBackoffUntilTs = 0
let optionsLoadedOnce = false
let optionsLastLoadTs = 0
let mapInitRetryTimer = 0
let mapInitAttempts = 0
const MAP_INIT_MAX_RETRIES = 20
const MAP_INIT_RETRY_MS = 100
const MAP_CONTAINER_SELECTOR = '[data-map-container]'

const selectedTime = computed(() => timeSteps[timeIndex.value] ?? { h: 12, m: 0 })
const selectedTimeLabel = computed(() => `${String(selectedTime.value.h).padStart(2, '0')}:${String(selectedTime.value.m).padStart(2, '0')}`)
const currentSun = ref({ altitudeDeg: null, azimuthDeg: null })
const showLiveLine = ref(true)
const showSimLine = ref(true)
const showAxisNS = ref(true)
const showAxisWE = ref(true)
const showSunRefs = ref(true)
const showPvAzLine = ref(false)
const showAnnualElevationBand = ref(true)
const showTendeSectors = ref(true)
const showWindDirectionOnMap = ref(true)
const tendeEditMode = ref(false)
const selectedShadeId = ref('')
const selectedShadeEdit = ref(null)
const tendeSaveStatus = ref('')
const tendeWizardStep = ref(0)
const lastValidTendeShades = ref([])
const lastValidTendeCoverStates = ref({})
const pvAzimuthDeg = ref(0)
const selectedForecastDate = ref('')
const hoverHourBar = ref(null)
const fsForm = ref({ enabled: false, api_key: '', declination: 30, azimuth: 0, kwp: 6.0 })
const fsSaveStatus = ref('')
const allSaveStatus = ref('')
const weatherForm = ref({ enabled: true, provider: 'met' })
const weatherStationForm = ref({
  enabled: false,
  stale_seconds: 180,
  device_id: '',
  wind_speed_entity_id: '',
  wind_gust_entity_id: '',
  wind_direction_entity_id: '',
  rain_rate_entity_id: '',
  rain_1h_entity_id: '',
  outdoor_temp_entity_id: '',
  outdoor_humidity_entity_id: '',
  pressure_entity_id: '',
  uv_index_entity_id: '',
  dewpoint_entity_id: '',
  feels_like_entity_id: '',
  solar_lux_entity_id: '',
  solar_radiation_entity_id: '',
  vpd_entity_id: '',
})
const weatherGuardForm = ref({
  enabled: true,
  wind_alarm_ms: 12.0,
  rain_alarm_mm_h: 1.5,
  facade_rain_min_wind_ms: 6.0,
  facade_rain_min_mm_h: 0.8,
  facade_azimuth_deg: -1.0,
  facade_half_fov_deg: 60.0,
  stale_seconds: 180,
})
const airQualityForm = ref({ enabled: true, provider: 'open_meteo' })
const tendeMapForm = ref({
  enabled: true,
  mqtt_host: '192.168.3.13',
  mqtt_port: 1883,
  mqtt_username: '',
  mqtt_password: '',
  topic_state: 'e-tendeintelligenti/map/shades',
  topic_availability: 'e-tendeintelligenti/availability',
  stale_seconds: 180,
})
const livoltekForm = ref({
  enabled: false,
  base_url: 'https://evs.livoltek-portal.com',
  username: '',
  password: '',
  token: '',
  station_id: '13299',
  device_id: '11237',
  inverter_sn: 'HP10603HSB280050',
  device_serial: 'P20A230300586',
  poll_interval_seconds: 300,
  timeout_seconds: 20,
  mqtt_discovery_enabled: false,
})
const livoltekStatus = ref(null)
const livoltekSaveStatus = ref('')
const energyForm = ref({
  enabled: true,
  theme: 'classic_flow',
  dashboard_background_color: '#080a10',
  show_sankey: true,
  energy_dashboard_layout: 'sunsynk',
  cardstyle: 'full',
  pv_power_entity_id: 'sensor.zcs_easas_1_activepower_pv_ext',
  pv_power_sign: 'positive',
  home_power_entity_id: '',
  home_power_sign: 'positive',
  grid_power_entity_id: '',
  grid_power_sign: 'positive',
  battery_power_entity_id: '',
  battery_power_sign: 'positive',
  battery_soc_entity_id: '',
  inverter_voltage_entity_id: '',
  load_frequency_entity_id: '',
  pv_installed_kwp: 6.6,
  pv_energy_today_entity_id: '',
  home_energy_today_entity_id: '',
  grid_import_today_entity_id: '',
  grid_export_today_entity_id: '',
  energy_time_pv_stat_ids: '',
  energy_time_load_stat_ids: '',
  energy_time_grid_import_stat_ids: '',
  energy_time_grid_export_stat_ids: '',
  energy_time_battery_charge_stat_ids: '',
  energy_time_battery_discharge_stat_ids: '',
  energy_time_gas_stat_ids: '',
  energy_time_solar_thermal_stat_ids: '',
  kflow_solar_max_power_w: 7000,
  kflow_load_max_power_w: 9000,
  kflow_grid_max_power_w: 8000,
  kflow_battery_capacity_wh: 15360,
  kflow_battery_max_power_w: 5000,
  kflow_battery_shutdown_soc: 10,
  sunsynk_card_config_json: '',
  k_flow_card_config_json: '',
  k_flow_invert_battery_power: false,
  k_flow_invert_grid_power: false,
  k_flow_total_pv_gen_entity: '',
  k_flow_battery_temp1: '',
  k_flow_battery_temp2: '',
  k_flow_battery_mos: '',
  k_flow_battery_shutdown_soc_entity: '',
  k_flow_battery_shutdown_soc_manual: '',
  k_flow_brand_logo: '',
  k_flow_pwr_bar_label: '',
  k_flow_aux_name: '',
  k_flow_aux_power: '',
  k_flow_aux_load1_name: '',
  k_flow_aux_load1: '',
  k_flow_aux_load2_name: '',
  k_flow_aux_load2: '',
  k_flow_aux_load3_name: '',
  k_flow_aux_load3: '',
  k_flow_aux_load4_name: '',
  k_flow_aux_load4: '',
  k_flow_aux_load5_name: '',
  k_flow_aux_load5: '',
  k_flow_aux_load6_name: '',
  k_flow_aux_load6: '',
  k_flow_aux_load7_name: '',
  k_flow_aux_load7: '',
  k_flow_home_icon: '',
  k_flow_min_cell_label: '',
  k_flow_min_cell_entity: '',
  k_flow_max_cell_label: '',
  k_flow_max_cell_entity: '',
  k_flow_batt_dis_label: '',
  k_flow_batt_dis_entity: '',
  entity_signs_json: '',
  sankey_extra_loads: Array.from({ length: 16 }, () => ({ name: '', entity_id: '', color: '#64748b' })),
})
const energySites = ref([])
const selectedEnergySiteId = ref('default')
const normalizeEnergySiteId = (value, fallback = 'impianto') => {
  const slug = String(value || '').trim().toLowerCase().replace(/[^a-z0-9_-]+/g, '-').replace(/^-+|-+$/g, '')
  return slug || fallback
}
const normalizeSankeyExtraLoads = (value) => {
  const src = Array.isArray(value) ? value : []
  return Array.from({ length: 16 }, (_, idx) => {
    const item = src[idx] || {}
    return {
      name: String(item?.name || '').trim(),
      entity_id: String(item?.entity_id || item?.entity || '').trim(),
      color: /^#[0-9a-f]{6}$/i.test(String(item?.color || '').trim()) ? String(item.color).trim() : '#64748b',
    }
  })
}
const energyWizardStep = ref(0)
const energySetupSection = ref('topology')
const energySetupSections = [
  { key: 'topology', label: 'Base', hint: 'layout e numeri' },
  { key: 'solar', label: 'Solare', hint: 'PV e MPPT' },
  { key: 'battery', label: 'Batteria', hint: 'SOC e potenza' },
  { key: 'load', label: 'Carichi', hint: 'casa e load' },
  { key: 'grid', label: 'Rete', hint: 'import/export' },
  { key: 'daily', label: 'Giornalieri', hint: 'kWh oggi' },
  { key: 'signs', label: 'Segni', hint: '+ / - valori' },
  { key: 'inverter', label: 'Inverter', hint: 'V, Hz, stato' },
  { key: 'aux', label: 'AUX', hint: 'ramo extra' },
  { key: 'kflow', label: 'K Flow', hint: 'extra e versi' },
  { key: 'json', label: 'JSON', hint: 'avanzato' },
]
const energyWizardSteps = [
  { key: 'topology', label: 'Topologia', hint: 'Definisci numero pannelli/batterie/carichi.' },
  { key: 'colors', label: 'Colori', hint: 'Scegli palette della card.' },
  { key: 'icons', label: 'Icone', hint: 'Scegli icone per carichi essenziali e non essenziali.' },
  { key: 'entities', label: 'Entita realtime', hint: 'Mappa sensori principali di potenza e batteria.' },
  { key: 'daily', label: 'Entita giornaliere', hint: 'Mappa i contatori energia daily.' },
  { key: 'review', label: 'Conferma', hint: 'Genera automaticamente il JSON completo.' },
]
const energyIconOptions = [
  'default',
  'boiler',
  'aircon',
  'pump',
  'oven',
  'home',
  'battery',
  'solar-panel',
  'flash',
  'ev-station',
  'server',
  'water-pump',
  'radiator',
  'fan',
]
const energyEntityPopupOpen = ref(false)
const energyEntityPopupMode = ref('realtime')
const energyEntityPreviewLoading = ref(false)
const energyEntityPreview = ref({})
const energyMapTargets = [
  { key: 'pv_total', label: 'PV Total Power' },
  { key: 'pv1_power_186', label: 'PV1 Power' },
  { key: 'pv2_power_187', label: 'PV2 Power' },
  { key: 'inverter_power_175', label: 'Home/Inverter Power' },
  { key: 'grid_power_169', label: 'Grid Power' },
  { key: 'battery_power_190', label: 'Battery Power' },
  { key: 'battery_soc_184', label: 'Battery SOC' },
  { key: 'battery_voltage_183', label: 'Battery Voltage' },
  { key: 'battery_current_191', label: 'Battery Current' },
  { key: 'inverter_voltage_154', label: 'Inverter Voltage' },
  { key: 'load_frequency_192', label: 'Load Frequency' },
  { key: 'day_pv_energy_108', label: 'PV Energy Today' },
  { key: 'day_battery_charge_70', label: 'Battery Charge Today' },
  { key: 'day_battery_discharge_71', label: 'Battery Discharge Today' },
  { key: 'day_load_energy_84', label: 'Load Energy Today' },
  { key: 'day_grid_import_76', label: 'Grid Import Today' },
]
const energyHotspots = [
  { key: 'pv_total', label: 'PV Total Power' },
  { key: 'pv1_power_186', label: 'PV1 Power' },
  { key: 'day_pv_energy_108', label: 'PV Energy Today' },
  { key: 'inverter_power_175', label: 'Home/Inverter Power' },
  { key: 'day_load_energy_84', label: 'Load Energy Today' },
  { key: 'inverter_voltage_154', label: 'Inverter Voltage' },
  { key: 'load_frequency_192', label: 'Load Frequency' },
  { key: 'battery_power_190', label: 'Battery Power' },
  { key: 'battery_soc_184', label: 'Battery SOC' },
  { key: 'battery_voltage_183', label: 'Battery Voltage' },
  { key: 'battery_current_191', label: 'Battery Current' },
  { key: 'day_battery_charge_70', label: 'Battery Charge Today' },
  { key: 'day_battery_discharge_71', label: 'Battery Discharge Today' },
  { key: 'grid_power_169', label: 'Grid Power' },
  { key: 'day_grid_import_76', label: 'Grid Import Today' },
  { key: 'day_grid_export_77', label: 'Grid Export Today' },
]
const selectedEnergyMapKey = ref('')
const realtimeEntityKeys = [
  'pv_total',
  'pv1_power_186','pv2_power_187','pv1_voltage_109','pv1_current_110','pv2_voltage_111','pv2_current_112',
  'pv3_power_188','pv4_power_189','pv5_power','pv6_power','pv3_voltage_113','pv3_current_114','pv4_voltage_115','pv4_current_116','pv5_voltage','pv5_current','pv6_voltage','pv6_current',
  'grid_power_169','grid_ct_power_172','grid_connected_status_194','inverter_status_59','inverter_power_175',
  'inverter_voltage_154','inverter_current_164','load_frequency_192','battery_soc_184','battery_power_190',
  'battery_current_191','battery_voltage_183','battery2_power_190','battery2_soc_184','battery2_current_191','battery2_voltage_183',
  'battery3_power_190','battery3_soc_184','battery3_current_191','battery3_voltage_183',
  'essential_power','essential_load1','essential_load2','essential_load3','essential_load4','essential_load5','essential_load6',
  'nonessential_power','non_essential_load1','non_essential_load2','non_essential_load3',
  'aux_power_166','aux_load1','aux_load2','aux_load3','aux_load4','aux_load5','aux_load6','aux_load7',
]
const dailyEntityKeys = [
  'day_pv_energy_108','day_battery_charge_70','day_battery_discharge_71','day_load_energy_84','day_grid_import_76','day_grid_export_77',
]
const knownEnergyEntityKeys = [
  ...realtimeEntityKeys,
  ...dailyEntityKeys,
  'essential_power','nonessential_power','essential_load1','essential_load2','essential_load3','essential_load4','essential_load5','essential_load6',
  'non_essential_load1','non_essential_load2','non_essential_load3',
  'aux_power_166','aux_load1','aux_load2','aux_load3','aux_load4','aux_load5','aux_load6','aux_load7','battery2_power_190','battery2_soc_184','battery2_current_191','battery2_voltage_183',
  'battery3_power_190','battery3_soc_184','battery3_current_191','battery3_voltage_183',
  'pv3_power_188','pv4_power_189','pv5_power','pv6_power','pv3_voltage_113','pv3_current_114','pv4_voltage_115','pv4_current_116','pv5_voltage','pv5_current','pv6_voltage','pv6_current',
  'use_timer_248','priority_load_243',
]
const energyWizardForm = ref({
  cardstyle: 'full',
  show_solar: true,
  show_battery: true,
  show_grid: true,
  dynamic_line_width: true,
  min_line_width: 1,
  max_line_width: 4,
  wide: false,
  inverter_modern: true,
  inverter_auto_scale: true,
  inverter_three_phase: false,
  solar_mppts: 2,
  solar_show_daily: true,
  solar_animation_speed: 6,
  solar_max_power: 7000,
  pv1_name: '',
  pv2_name: '',
  pv3_name: '',
  pv4_name: '',
  pv5_name: '',
  pv6_name: '',
  pv1_max_power: 0,
  pv2_max_power: 0,
  pv3_max_power: 0,
  pv4_max_power: 0,
  pv5_max_power: 0,
  pv6_max_power: 0,
  battery_count: 1,
  battery_energy_wh: 15960,
  battery_shutdown_soc: 10,
  battery_show_daily: true,
  battery_animation_speed: 8,
  battery_max_power: 5000,
  battery_auto_scale: true,
  additional_loads: 2,
  show_aux: false,
  load_essential_name: 'Essential',
  load_aux_name: 'Auxiliary',
  load_label_daily: 'Daily Load',
  load1_name: '',
  load2_name: '',
  load3_name: '',
  load4_name: '',
  load5_name: '',
  load6_name: '',
  load_show_daily: true,
  load_animation_speed: 6,
  load_max_power: 9000,
  load_auto_scale: true,
  load_dynamic_colour: true,
  load_dynamic_icon: true,
  load_invert_flow: false,
  load_max_colour: '#f59e0b',
  load_off_colour: '#808080',
  load_aux_colour: '#cbd5e1',
  load_aux_off_colour: '#808080',
  load_aux_dynamic_colour: true,
  load_aux_type: 'default',
  load_show_absolute_aux: false,
  load_show_daily_aux: false,
  load_aux_loads: 0,
  load_aux_load1_name: '',
  load_aux_load2_name: '',
  load_aux_load3_name: '',
  load_aux_load4_name: '',
  load_aux_load5_name: '',
  load_aux_load6_name: '',
  load_aux_load7_name: '',
  load_aux_load1_icon: 'default',
  load_aux_load2_icon: 'default',
  load_aux_load3_icon: 'default',
  load_aux_load4_icon: 'default',
  load_aux_load5_icon: 'default',
  load_aux_load6_icon: 'default',
  load_aux_load7_icon: 'default',
  grid_show_daily_buy: true,
  grid_show_daily_sell: true,
  grid_invert_grid: false,
  grid_show_absolute: true,
  grid_show_nonessential: false,
  grid_additional_loads: 0,
  grid_name: 'Linea Sas',
  grid_label_daily_buy: 'Consumo Giornaliero',
  grid_label_daily_sell: 'Vendita Giornaliera',
  grid_nonessential_name: 'Non Essential',
  grid_load1_name: '',
  grid_load2_name: '',
  grid_load3_name: '',
  grid_invert_flow: false,
  grid_energy_cost_decimals: 0,
  grid_animation_speed: 9,
  grid_max_power: 8000,
  grid_auto_scale: true,
  color_solar: '#f59e0b',
  color_battery: '#a855f7',
  color_grid: '#06b6d4',
  color_grid_export: '#6a7ac8',
  color_grid_off: '#3a8d53',
  color_no_grid: '#49ab6a',
  color_load: '#cbd5e1',
  load1_icon: 'default',
  load2_icon: 'default',
  load3_icon: 'default',
  load4_icon: 'default',
  load5_icon: 'default',
  load6_icon: 'default',
  grid_nonessential_icon: 'default',
  grid_load1_icon: 'default',
  grid_load2_icon: 'default',
  grid_load3_icon: 'default',
  grid_import_icon: 'mdi:transmission-tower-import',
  grid_export_icon: 'mdi:transmission-tower-export',
  grid_disconnected_icon: 'mdi:transmission-tower-off',
  grid_ct_power_172: '',
  grid_connected_status_194: '',
  essential_power: '',
  nonessential_power: '',
  essential_load1: '',
  essential_load2: '',
  essential_load3: '',
  essential_load4: '',
  essential_load5: '',
  essential_load6: '',
  aux_power_166: '',
  aux_load1: '',
  aux_load2: '',
  aux_load3: '',
  aux_load4: '',
  aux_load5: '',
  aux_load6: '',
  aux_load7: '',
  non_essential_load1: '',
  non_essential_load2: '',
  non_essential_load3: '',
  inverter_status_59: '',
  inverter_voltage_154: '',
  inverter_current_164: '',
  load_frequency_192: '',
  pv_total: '',
  pv1_power_186: '',
  pv2_power_187: '',
  pv1_voltage_109: '',
  pv1_current_110: '',
  pv2_voltage_111: '',
  pv2_current_112: '',
  grid_power_169: '',
  inverter_power_175: '',
  battery_soc_184: '',
  battery_power_190: '',
  battery_current_191: '',
  battery_voltage_183: '',
  battery1_name: '',
  battery2_name: '',
  battery3_name: '',
  day_pv_energy_108: '',
  day_battery_charge_70: '',
  day_battery_discharge_71: '',
  day_load_energy_84: '',
  day_grid_import_76: '',
  day_grid_export_77: '',
  pv3_power_188: '',
  pv4_power_189: '',
  pv5_power: '',
  pv6_power: '',
  pv3_voltage_113: '',
  pv3_current_114: '',
  pv4_voltage_115: '',
  pv4_current_116: '',
  pv5_voltage: '',
  pv5_current: '',
  pv6_voltage: '',
  pv6_current: '',
  battery2_power_190: '',
  battery2_soc_184: '',
  battery2_current_191: '',
  battery2_voltage_183: '',
  battery3_power_190: '',
  battery3_soc_184: '',
  battery3_current_191: '',
  battery3_voltage_183: '',
  use_timer_248: '',
  priority_load_243: '',
  entities_extra_json: '',
})
const baseForm = ref({
  latitude: 44.6973,
  longitude: 7.8683,
  timezone: 'Europe/Rome',
  coordinates_source_mode: 'e_tende',
  interval_minutes: 15,
  location_query: '',
  pv_actual_entity_id: 'sensor.zcs_easas_1_activepower_pv_ext',
  external_temp_entity_id: 'sensor.temperature_and_humidity_sensor_lite_eterna_terrazzo_temperature',
  external_humidity_entity_id: 'sensor.temperature_and_humidity_sensor_lite_eterna_terrazzo_humidity',
})
const baseSaveStatus = ref('')
const overlaySaveStatus = ref('')
const energyEntitySigns = ref({})
const energySignFields = [
  { key: 'pv_total', label: 'PV totale' },
  { key: 'pv1_power_186', label: 'PV1' },
  { key: 'pv2_power_187', label: 'PV2' },
  { key: 'pv3_power_188', label: 'PV3' },
  { key: 'pv4_power_189', label: 'PV4' },
  { key: 'pv5_power', label: 'PV5' },
  { key: 'pv6_power', label: 'PV6' },
  { key: 'inverter_power_175', label: 'Casa/Home' },
  { key: 'essential_power', label: 'Essential principale' },
  { key: 'essential_load1', label: 'Essential load 1' },
  { key: 'essential_load2', label: 'Essential load 2' },
  { key: 'essential_load3', label: 'Essential load 3' },
  { key: 'essential_load4', label: 'Essential load 4' },
  { key: 'essential_load5', label: 'Essential load 5' },
  { key: 'essential_load6', label: 'Essential load 6' },
  { key: 'aux_power_166', label: 'AUX principale' },
  { key: 'aux_load1', label: 'AUX load 1' },
  { key: 'aux_load2', label: 'AUX load 2' },
  { key: 'aux_load3', label: 'AUX load 3' },
  { key: 'aux_load4', label: 'AUX load 4' },
  { key: 'aux_load5', label: 'AUX load 5' },
  { key: 'aux_load6', label: 'AUX load 6' },
  { key: 'aux_load7', label: 'AUX load 7' },
  { key: 'grid_power_169', label: 'Rete/Grid' },
  { key: 'grid_ct_power_172', label: 'Rete CT' },
  { key: 'nonessential_power', label: 'Non-Essential principale' },
  { key: 'non_essential_load1', label: 'Non-Essential load 1' },
  { key: 'non_essential_load2', label: 'Non-Essential load 2' },
  { key: 'non_essential_load3', label: 'Non-Essential load 3' },
  { key: 'battery_power_190', label: 'Batteria 1' },
  { key: 'battery2_power_190', label: 'Batteria 2' },
]

function makeEnergySiteFromForm(base = {}) {
  syncKFlowJsonFromUi()
  const name = String(base.name || energyForm.value.site_name || 'Impianto 1').trim() || 'Impianto 1'
  const id = normalizeEnergySiteId(base.id || selectedEnergySiteId.value || name, 'default')
  return {
    ...base,
    id,
    name,
    enabled: Boolean(energyForm.value.enabled),
    theme: String(energyForm.value.theme || 'classic_flow'),
    dashboard_background_color: String(energyForm.value.dashboard_background_color || '#080a10'),
    show_sankey: Boolean(energyForm.value.show_sankey ?? true),
    energy_dashboard_layout: String(energyForm.value.energy_dashboard_layout || 'sunsynk') === 'k_flow' ? 'k_flow' : 'sunsynk',
    pv_power_entity_id: String(energyForm.value.pv_power_entity_id || ''),
    pv_power_sign: String(energyForm.value.pv_power_sign || 'positive'),
    home_power_entity_id: String(energyForm.value.home_power_entity_id || ''),
    home_power_sign: String(energyForm.value.home_power_sign || 'positive'),
    grid_power_entity_id: String(energyForm.value.grid_power_entity_id || ''),
    grid_power_sign: String(energyForm.value.grid_power_sign || 'positive'),
    battery_power_entity_id: String(energyForm.value.battery_power_entity_id || ''),
    battery_power_sign: String(energyForm.value.battery_power_sign || 'positive'),
    battery_soc_entity_id: String(energyForm.value.battery_soc_entity_id || ''),
    inverter_voltage_entity_id: String(energyForm.value.inverter_voltage_entity_id || ''),
    load_frequency_entity_id: String(energyForm.value.load_frequency_entity_id || ''),
    pv_installed_kwp: Number(energyForm.value.pv_installed_kwp ?? 6.6),
    pv_energy_today_entity_id: String(energyForm.value.pv_energy_today_entity_id || ''),
    home_energy_today_entity_id: String(energyForm.value.home_energy_today_entity_id || ''),
    grid_import_today_entity_id: String(energyForm.value.grid_import_today_entity_id || ''),
    grid_export_today_entity_id: String(energyForm.value.grid_export_today_entity_id || ''),
    energy_time_pv_stat_ids: String(energyForm.value.energy_time_pv_stat_ids || ''),
    energy_time_load_stat_ids: String(energyForm.value.energy_time_load_stat_ids || ''),
    energy_time_grid_import_stat_ids: String(energyForm.value.energy_time_grid_import_stat_ids || ''),
    energy_time_grid_export_stat_ids: String(energyForm.value.energy_time_grid_export_stat_ids || ''),
    energy_time_battery_charge_stat_ids: String(energyForm.value.energy_time_battery_charge_stat_ids || ''),
    energy_time_battery_discharge_stat_ids: String(energyForm.value.energy_time_battery_discharge_stat_ids || ''),
    energy_time_gas_stat_ids: String(energyForm.value.energy_time_gas_stat_ids || ''),
    energy_time_solar_thermal_stat_ids: String(energyForm.value.energy_time_solar_thermal_stat_ids || ''),
    kflow_solar_max_power_w: Number(energyForm.value.kflow_solar_max_power_w ?? 7000),
    kflow_load_max_power_w: Number(energyForm.value.kflow_load_max_power_w ?? 9000),
    kflow_grid_max_power_w: Number(energyForm.value.kflow_grid_max_power_w ?? 8000),
    kflow_battery_capacity_wh: Number(energyForm.value.kflow_battery_capacity_wh ?? 15360),
    kflow_battery_max_power_w: Number(energyForm.value.kflow_battery_max_power_w ?? 5000),
    kflow_battery_shutdown_soc: Number(energyForm.value.kflow_battery_shutdown_soc ?? 10),
    sunsynk_card_config_json: String(energyForm.value.sunsynk_card_config_json || ''),
    k_flow_card_config_json: String(energyForm.value.k_flow_card_config_json || ''),
    entity_signs_json: String(energyForm.value.entity_signs_json || ''),
    sankey_extra_loads: normalizeSankeyExtraLoads(energyForm.value.sankey_extra_loads)
      .filter((item) => item.entity_id || item.name),
  }
}

function applyEnergySiteToForm(site = {}) {
  selectedEnergySiteId.value = normalizeEnergySiteId(site.id || site.name || 'default', 'default')
  energyForm.value = {
    ...energyForm.value,
    enabled: Boolean(site.enabled ?? true),
    theme: String(site.theme || 'classic_flow'),
    dashboard_background_color: String(site.dashboard_background_color || '#080a10'),
    show_sankey: Boolean(site.show_sankey ?? true),
    energy_dashboard_layout: String(site.energy_dashboard_layout || 'sunsynk') === 'k_flow' ? 'k_flow' : 'sunsynk',
    cardstyle: 'full',
    pv_power_entity_id: String(site.pv_power_entity_id || 'sensor.zcs_easas_1_activepower_pv_ext'),
    pv_power_sign: String(site.pv_power_sign || 'positive'),
    home_power_entity_id: String(site.home_power_entity_id || ''),
    home_power_sign: String(site.home_power_sign || 'positive'),
    grid_power_entity_id: String(site.grid_power_entity_id || ''),
    grid_power_sign: String(site.grid_power_sign || 'positive'),
    battery_power_entity_id: String(site.battery_power_entity_id || ''),
    battery_power_sign: String(site.battery_power_sign || 'positive'),
    battery_soc_entity_id: String(site.battery_soc_entity_id || ''),
    inverter_voltage_entity_id: String(site.inverter_voltage_entity_id || ''),
    load_frequency_entity_id: String(site.load_frequency_entity_id || ''),
    pv_installed_kwp: Number(site.pv_installed_kwp ?? 6.6),
    pv_energy_today_entity_id: String(site.pv_energy_today_entity_id || ''),
    home_energy_today_entity_id: String(site.home_energy_today_entity_id || ''),
    grid_import_today_entity_id: String(site.grid_import_today_entity_id || ''),
    grid_export_today_entity_id: String(site.grid_export_today_entity_id || ''),
    energy_time_pv_stat_ids: String(site.energy_time_pv_stat_ids || ''),
    energy_time_load_stat_ids: String(site.energy_time_load_stat_ids || ''),
    energy_time_grid_import_stat_ids: String(site.energy_time_grid_import_stat_ids || ''),
    energy_time_grid_export_stat_ids: String(site.energy_time_grid_export_stat_ids || ''),
    energy_time_battery_charge_stat_ids: String(site.energy_time_battery_charge_stat_ids || ''),
    energy_time_battery_discharge_stat_ids: String(site.energy_time_battery_discharge_stat_ids || ''),
    energy_time_gas_stat_ids: String(site.energy_time_gas_stat_ids || ''),
    energy_time_solar_thermal_stat_ids: String(site.energy_time_solar_thermal_stat_ids || ''),
    kflow_solar_max_power_w: Number(site.kflow_solar_max_power_w ?? 7000),
    kflow_load_max_power_w: Number(site.kflow_load_max_power_w ?? 9000),
    kflow_grid_max_power_w: Number(site.kflow_grid_max_power_w ?? 8000),
    kflow_battery_capacity_wh: Number(site.kflow_battery_capacity_wh ?? 15360),
    kflow_battery_max_power_w: Number(site.kflow_battery_max_power_w ?? 5000),
    kflow_battery_shutdown_soc: Number(site.kflow_battery_shutdown_soc ?? 10),
    sunsynk_card_config_json: String(site.sunsynk_card_config_json || ''),
    k_flow_card_config_json: String(site.k_flow_card_config_json || ''),
    k_flow_invert_battery_power: false,
    k_flow_invert_grid_power: false,
    k_flow_total_pv_gen_entity: '',
    k_flow_battery_temp1: '',
    k_flow_battery_temp2: '',
    k_flow_battery_mos: '',
    k_flow_battery_shutdown_soc_entity: '',
    k_flow_battery_shutdown_soc_manual: '',
    k_flow_brand_logo: '',
    k_flow_pwr_bar_label: '',
    k_flow_aux_name: '',
    k_flow_aux_power: '',
    k_flow_aux_load1_name: '',
    k_flow_aux_load1: '',
    k_flow_aux_load2_name: '',
    k_flow_aux_load2: '',
    k_flow_aux_load3_name: '',
    k_flow_aux_load3: '',
    k_flow_aux_load4_name: '',
    k_flow_aux_load4: '',
    k_flow_aux_load5_name: '',
    k_flow_aux_load5: '',
    k_flow_aux_load6_name: '',
    k_flow_aux_load6: '',
    k_flow_aux_load7_name: '',
    k_flow_aux_load7: '',
    k_flow_home_icon: '',
    k_flow_min_cell_label: '',
    k_flow_min_cell_entity: '',
    k_flow_max_cell_label: '',
    k_flow_max_cell_entity: '',
    k_flow_batt_dis_label: '',
    k_flow_batt_dis_entity: '',
    entity_signs_json: String(site.entity_signs_json || ''),
    sankey_extra_loads: normalizeSankeyExtraLoads(site.sankey_extra_loads),
  }
  syncEnergySignsUiFromJson()
  syncKFlowUiFromJson()
  hydrateEnergyWizardFromOptions(site)
  syncKFlowScaleToWizard()
}

function persistCurrentEnergySiteFromEditor() {
  syncWizardFromEnergyForm()
  applyEnergyWizard(true)
  return syncCurrentEnergySiteFromForm()
}

function syncCurrentEnergySiteFromForm() {
  const currentId = normalizeEnergySiteId(selectedEnergySiteId.value || 'default', 'default')
  const idx = energySites.value.findIndex((s) => normalizeEnergySiteId(s?.id, 'default') === currentId)
  const prev = idx >= 0 ? energySites.value[idx] : { id: currentId, name: currentId === 'default' ? 'Impianto 1' : currentId }
  const next = makeEnergySiteFromForm(prev)
  if (idx >= 0) energySites.value.splice(idx, 1, next)
  else energySites.value.push(next)
  return next
}

function buildEnergyPayload() {
  syncCurrentEnergySiteFromForm()
  const currentId = normalizeEnergySiteId(selectedEnergySiteId.value || 'default', 'default')
  const sites = energySites.value.map((s, idx) => ({
    ...s,
    id: normalizeEnergySiteId(s?.id || s?.name, `impianto-${idx + 1}`),
    name: String(s?.name || s?.id || `Impianto ${idx + 1}`).trim(),
  }))
  const selected = sites.find((s) => s.id === currentId) || sites[0] || makeEnergySiteFromForm({ id: 'default', name: 'Impianto 1' })
  return {
    ...selected,
    selected_site_id: selected.id,
    sites,
  }
}

function selectEnergySite(id) {
  persistCurrentEnergySiteFromEditor()
  const wanted = normalizeEnergySiteId(id, 'default')
  const site = energySites.value.find((s) => normalizeEnergySiteId(s?.id, 'default') === wanted)
  if (site) applyEnergySiteToForm(site)
}

function addEnergySite() {
  persistCurrentEnergySiteFromEditor()
  const n = energySites.value.length + 1
  const site = makeEnergySiteFromForm({ id: `impianto-${n}`, name: `Impianto ${n}` })
  energySites.value.push(site)
  applyEnergySiteToForm(site)
}

function duplicateEnergySite() {
  persistCurrentEnergySiteFromEditor()
  const n = energySites.value.length + 1
  const site = makeEnergySiteFromForm({ id: `impianto-${n}`, name: `Impianto ${n}` })
  energySites.value.push(site)
  applyEnergySiteToForm(site)
}

function deleteEnergySite() {
  if (energySites.value.length <= 1) return
  persistCurrentEnergySiteFromEditor()
  const currentId = normalizeEnergySiteId(selectedEnergySiteId.value || 'default', 'default')
  energySites.value = energySites.value.filter((s) => normalizeEnergySiteId(s?.id, 'default') !== currentId)
  applyEnergySiteToForm(energySites.value[0])
}

function hydrateEnergyWizardFromOptions(eo = {}) {
  const wizardSeed = {
    ...energyWizardForm.value,
    cardstyle: 'full',
    pv1_power_186: String(eo.pv_power_entity_id || ''),
    pv2_power_187: '',
    grid_power_169: String(eo.grid_power_entity_id || ''),
    inverter_power_175: String(eo.home_power_entity_id || ''),
    battery_soc_184: String(eo.battery_soc_entity_id || ''),
    battery_power_190: String(eo.battery_power_entity_id || ''),
    inverter_voltage_154: String(eo.inverter_voltage_entity_id || ''),
    load_frequency_192: String(eo.load_frequency_entity_id || ''),
    day_pv_energy_108: String(eo.pv_energy_today_entity_id || ''),
    day_load_energy_84: String(eo.home_energy_today_entity_id || ''),
    day_grid_import_76: String(eo.grid_import_today_entity_id || ''),
    day_grid_export_77: String(eo.grid_export_today_entity_id || ''),
  }
  try {
    const parsed = JSON.parse(String(eo.sunsynk_card_config_json || '{}'))
    const ents = parsed?.entities || {}
    const solar = parsed?.solar || {}
    const battery = parsed?.battery || {}
    const battery2 = parsed?.battery2 || {}
    const battery3 = parsed?.battery3 || {}
    const load = parsed?.load || {}
    const grid = parsed?.grid || {}
    energyWizardForm.value = {
      ...wizardSeed,
      cardstyle: String(parsed?.cardstyle || wizardSeed.cardstyle || 'full'),
      show_solar: Boolean(parsed?.show_solar ?? wizardSeed.show_solar),
      show_battery: Boolean(parsed?.show_battery ?? wizardSeed.show_battery),
      show_grid: Boolean(parsed?.show_grid ?? wizardSeed.show_grid),
      dynamic_line_width: Boolean(parsed?.dynamic_line_width ?? wizardSeed.dynamic_line_width),
      min_line_width: Number(parsed?.min_line_width ?? wizardSeed.min_line_width),
      max_line_width: Number(parsed?.max_line_width ?? wizardSeed.max_line_width),
      wide: Boolean(parsed?.wide ?? wizardSeed.wide),
      inverter_modern: Boolean(parsed?.inverter?.modern ?? wizardSeed.inverter_modern),
      inverter_auto_scale: Boolean(parsed?.inverter?.auto_scale ?? wizardSeed.inverter_auto_scale),
      inverter_three_phase: Boolean(parsed?.inverter?.three_phase ?? wizardSeed.inverter_three_phase),
      solar_mppts: Number(solar.mppts ?? wizardSeed.solar_mppts ?? 1),
      solar_show_daily: Boolean(solar.show_daily ?? wizardSeed.solar_show_daily),
      solar_animation_speed: Number(solar.animation_speed ?? wizardSeed.solar_animation_speed),
      solar_max_power: Number(solar.max_power ?? wizardSeed.solar_max_power),
      pv1_name: String(solar.pv1_name || wizardSeed.pv1_name),
      pv2_name: String(solar.pv2_name || wizardSeed.pv2_name),
      pv3_name: String(solar.pv3_name || wizardSeed.pv3_name),
      pv4_name: String(solar.pv4_name || wizardSeed.pv4_name),
      pv5_name: String(solar.pv5_name || wizardSeed.pv5_name),
      pv6_name: String(solar.pv6_name || wizardSeed.pv6_name),
      pv1_max_power: Number(solar.pv1_max_power ?? wizardSeed.pv1_max_power ?? 0),
      pv2_max_power: Number(solar.pv2_max_power ?? wizardSeed.pv2_max_power ?? 0),
      pv3_max_power: Number(solar.pv3_max_power ?? wizardSeed.pv3_max_power ?? 0),
      pv4_max_power: Number(solar.pv4_max_power ?? wizardSeed.pv4_max_power ?? 0),
      pv5_max_power: Number(solar.pv5_max_power ?? wizardSeed.pv5_max_power ?? 0),
      pv6_max_power: Number(solar.pv6_max_power ?? wizardSeed.pv6_max_power ?? 0),
      battery_count: Number(battery.count ?? wizardSeed.battery_count),
      battery1_name: String(battery.name || wizardSeed.battery1_name),
      battery2_name: String(battery2.name || wizardSeed.battery2_name),
      battery3_name: String(battery3.name || wizardSeed.battery3_name),
      battery_energy_wh: Number(battery.energy ?? wizardSeed.battery_energy_wh),
      battery_shutdown_soc: Number(battery.shutdown_soc ?? wizardSeed.battery_shutdown_soc),
      battery_show_daily: Boolean(battery.show_daily ?? wizardSeed.battery_show_daily),
      battery_animation_speed: Number(battery.animation_speed ?? wizardSeed.battery_animation_speed),
      battery_max_power: Number(battery.max_power ?? wizardSeed.battery_max_power),
      battery_auto_scale: Boolean(battery.auto_scale ?? wizardSeed.battery_auto_scale),
      additional_loads: Number(load.additional_loads ?? wizardSeed.additional_loads),
      show_aux: Boolean(load.show_aux ?? wizardSeed.show_aux),
      load_essential_name: String(load.essential_name || wizardSeed.load_essential_name),
      load_aux_name: String(load.aux_name || wizardSeed.load_aux_name),
      load_label_daily: String(load.label_daily_load || wizardSeed.load_label_daily),
      load1_name: String(load.load1_name || wizardSeed.load1_name),
      load2_name: String(load.load2_name || wizardSeed.load2_name),
      load3_name: String(load.load3_name || wizardSeed.load3_name),
      load4_name: String(load.load4_name || wizardSeed.load4_name),
      load5_name: String(load.load5_name || wizardSeed.load5_name),
      load6_name: String(load.load6_name || wizardSeed.load6_name),
      load_show_daily: Boolean(load.show_daily ?? wizardSeed.load_show_daily),
      load_animation_speed: Number(load.animation_speed ?? wizardSeed.load_animation_speed),
      load_max_power: Number(load.max_power ?? wizardSeed.load_max_power),
      load_auto_scale: Boolean(load.auto_scale ?? wizardSeed.load_auto_scale),
      load_dynamic_colour: Boolean(load.dynamic_colour ?? wizardSeed.load_dynamic_colour),
      load_dynamic_icon: Boolean(load.dynamic_icon ?? wizardSeed.load_dynamic_icon),
      load_invert_flow: Boolean(load.invert_flow ?? wizardSeed.load_invert_flow),
      load_max_colour: String(load.max_colour || wizardSeed.load_max_colour),
      load_off_colour: String(load.off_colour || wizardSeed.load_off_colour),
      load_aux_colour: String(load.aux_colour || wizardSeed.load_aux_colour),
      load_aux_off_colour: String(load.aux_off_colour || wizardSeed.load_aux_off_colour),
      load_aux_dynamic_colour: Boolean(load.aux_dynamic_colour ?? wizardSeed.load_aux_dynamic_colour),
      load_aux_type: String(load.aux_type || wizardSeed.load_aux_type),
      load_show_absolute_aux: Boolean(load.show_absolute_aux ?? wizardSeed.load_show_absolute_aux),
      load_show_daily_aux: Boolean(load.show_daily_aux ?? wizardSeed.load_show_daily_aux),
      load_aux_loads: Number(load.aux_loads ?? wizardSeed.load_aux_loads),
      load_aux_load1_name: String(load.aux_load1_name || wizardSeed.load_aux_load1_name),
      load_aux_load2_name: String(load.aux_load2_name || wizardSeed.load_aux_load2_name),
      load_aux_load3_name: String(load.aux_load3_name || wizardSeed.load_aux_load3_name),
      load_aux_load4_name: String(load.aux_load4_name || wizardSeed.load_aux_load4_name),
      load_aux_load5_name: String(load.aux_load5_name || wizardSeed.load_aux_load5_name),
      load_aux_load6_name: String(load.aux_load6_name || wizardSeed.load_aux_load6_name),
      load_aux_load7_name: String(load.aux_load7_name || wizardSeed.load_aux_load7_name),
      load_aux_load1_icon: String(load.aux_load1_icon || wizardSeed.load_aux_load1_icon),
      load_aux_load2_icon: String(load.aux_load2_icon || wizardSeed.load_aux_load2_icon),
      load_aux_load3_icon: String(load.aux_load3_icon || wizardSeed.load_aux_load3_icon),
      load_aux_load4_icon: String(load.aux_load4_icon || wizardSeed.load_aux_load4_icon),
      load_aux_load5_icon: String(load.aux_load5_icon || wizardSeed.load_aux_load5_icon),
      load_aux_load6_icon: String(load.aux_load6_icon || wizardSeed.load_aux_load6_icon),
      load_aux_load7_icon: String(load.aux_load7_icon || wizardSeed.load_aux_load7_icon),
      grid_show_daily_buy: Boolean(grid.show_daily_buy ?? wizardSeed.grid_show_daily_buy),
      grid_show_daily_sell: Boolean(grid.show_daily_sell ?? wizardSeed.grid_show_daily_sell),
      grid_invert_grid: Boolean(grid.invert_grid ?? wizardSeed.grid_invert_grid),
      grid_show_absolute: Boolean(grid.show_absolute ?? wizardSeed.grid_show_absolute),
      grid_show_nonessential: Boolean(grid.show_nonessential ?? wizardSeed.grid_show_nonessential),
      grid_additional_loads: Number(grid.additional_loads ?? wizardSeed.grid_additional_loads),
      grid_name: String(grid.grid_name || wizardSeed.grid_name),
      grid_label_daily_buy: String(grid.label_daily_grid_buy || wizardSeed.grid_label_daily_buy),
      grid_label_daily_sell: String(grid.label_daily_grid_sell || wizardSeed.grid_label_daily_sell),
      grid_nonessential_name: String(grid.nonessential_name || wizardSeed.grid_nonessential_name),
      grid_load1_name: String(grid.load1_name || wizardSeed.grid_load1_name),
      grid_load2_name: String(grid.load2_name || wizardSeed.grid_load2_name),
      grid_load3_name: String(grid.load3_name || wizardSeed.grid_load3_name),
      grid_invert_flow: Boolean(grid.invert_flow ?? wizardSeed.grid_invert_flow),
      grid_energy_cost_decimals: Number(grid.energy_cost_decimals ?? wizardSeed.grid_energy_cost_decimals),
      grid_animation_speed: Number(grid.animation_speed ?? wizardSeed.grid_animation_speed),
      grid_max_power: Number(grid.max_power ?? wizardSeed.grid_max_power),
      grid_auto_scale: Boolean(grid.auto_scale ?? wizardSeed.grid_auto_scale),
      color_solar: String(solar.colour || wizardSeed.color_solar),
      color_battery: String(battery.colour || wizardSeed.color_battery),
      color_grid: String(grid.colour || wizardSeed.color_grid),
      color_grid_export: String(grid.export_colour || wizardSeed.color_grid_export),
      color_grid_off: String(grid.grid_off_colour || wizardSeed.color_grid_off),
      color_no_grid: String(grid.no_grid_colour || wizardSeed.color_no_grid),
      color_load: String(load.colour || wizardSeed.color_load),
      load1_icon: String(load.load1_icon || wizardSeed.load1_icon),
      load2_icon: String(load.load2_icon || wizardSeed.load2_icon),
      load3_icon: String(load.load3_icon || wizardSeed.load3_icon),
      load4_icon: String(load.load4_icon || wizardSeed.load4_icon),
      load5_icon: String(load.load5_icon || wizardSeed.load5_icon),
      load6_icon: String(load.load6_icon || wizardSeed.load6_icon),
      grid_nonessential_icon: String(grid.nonessential_icon || wizardSeed.grid_nonessential_icon),
      grid_load1_icon: String(grid.load1_icon || wizardSeed.grid_load1_icon),
      grid_load2_icon: String(grid.load2_icon || wizardSeed.grid_load2_icon),
      grid_load3_icon: String(grid.load3_icon || wizardSeed.grid_load3_icon),
      grid_import_icon: String(grid.import_icon || wizardSeed.grid_import_icon),
      grid_export_icon: String(grid.export_icon || wizardSeed.grid_export_icon),
      grid_disconnected_icon: String(grid.disconnected_icon || wizardSeed.grid_disconnected_icon),
      ...Object.fromEntries(realtimeEntityKeys.map((k) => [k, String(ents[k] || wizardSeed[k] || '')])),
      ...Object.fromEntries(dailyEntityKeys.map((k) => [k, String(ents[k] || wizardSeed[k] || '')])),
      entities_extra_json: JSON.stringify(Object.fromEntries(Object.entries(ents || {}).filter(([k]) => !knownEnergyEntityKeys.includes(String(k)))), null, 2),
    }
  } catch (_) {
    energyWizardForm.value = wizardSeed
  }
}

function syncEnergySignsUiFromJson() {
  let parsed = {}
  try {
    const raw = String(energyForm.value?.entity_signs_json || '').trim()
    if (raw) {
      const obj = JSON.parse(raw)
      if (obj && typeof obj === 'object' && !Array.isArray(obj)) parsed = obj
    }
  } catch (_) {}
  const next = {}
  for (const f of energySignFields) {
    const v = String(parsed[f.key] || '').toLowerCase()
    next[f.key] = v === 'negative' ? 'negative' : 'positive'
  }
  energyEntitySigns.value = next
}

function syncEnergySignsJsonFromUi() {
  const out = {}
  for (const f of energySignFields) {
    const v = String(energyEntitySigns.value?.[f.key] || 'positive')
    if (v === 'negative') out[f.key] = 'negative'
    else out[f.key] = 'positive'
  }
  energyForm.value.entity_signs_json = JSON.stringify(out, null, 2)
}

const kFlowUiKeys = {
  k_flow_total_pv_gen_entity: 'total_pv_gen_entity',
  k_flow_battery_temp1: 'battery_temp1',
  k_flow_battery_temp2: 'battery_temp2',
  k_flow_battery_mos: 'battery_mos',
  k_flow_battery_shutdown_soc_entity: 'battery_shutdown_soc_entity',
  k_flow_battery_shutdown_soc_manual: 'battery_shutdown_soc_manual',
  k_flow_brand_logo: 'brand_logo',
  k_flow_pwr_bar_label: 'label_pwr_bar',
  k_flow_aux_name: 'aux_name',
  k_flow_aux_power: 'aux_power',
  k_flow_aux_load1_name: 'aux_load1_name',
  k_flow_aux_load1: 'aux_load1',
  k_flow_aux_load2_name: 'aux_load2_name',
  k_flow_aux_load2: 'aux_load2',
  k_flow_aux_load3_name: 'aux_load3_name',
  k_flow_aux_load3: 'aux_load3',
  k_flow_aux_load4_name: 'aux_load4_name',
  k_flow_aux_load4: 'aux_load4',
  k_flow_aux_load5_name: 'aux_load5_name',
  k_flow_aux_load5: 'aux_load5',
  k_flow_aux_load6_name: 'aux_load6_name',
  k_flow_aux_load6: 'aux_load6',
  k_flow_aux_load7_name: 'aux_load7_name',
  k_flow_aux_load7: 'aux_load7',
  k_flow_home_icon: 'home_icon',
  k_flow_min_cell_label: 'label_min_cell',
  k_flow_min_cell_entity: 'label_entity_min_cell',
  k_flow_max_cell_label: 'label_max_cell',
  k_flow_max_cell_entity: 'label_entity_max_cell',
  k_flow_batt_dis_label: 'label_batt_dis',
  k_flow_batt_dis_entity: 'label_entity_batt_dis',
}

function parseKFlowConfigJson() {
  try {
    const raw = String(energyForm.value?.k_flow_card_config_json || '').trim()
    if (!raw) return {}
    const obj = JSON.parse(raw)
    return obj && typeof obj === 'object' && !Array.isArray(obj) ? obj : {}
  } catch (_) {
    return {}
  }
}

function syncKFlowUiFromJson() {
  const obj = parseKFlowConfigJson()
  energyForm.value.k_flow_invert_battery_power = Boolean(obj.invert_battery_power)
  energyForm.value.k_flow_invert_grid_power = Boolean(obj.invert_grid_power)
  for (const [formKey, jsonKey] of Object.entries(kFlowUiKeys)) {
    energyForm.value[formKey] = String(obj[jsonKey] || '')
  }
}

function syncKFlowJsonFromUi() {
  const obj = parseKFlowConfigJson()
  obj.invert_battery_power = Boolean(energyForm.value.k_flow_invert_battery_power)
  obj.invert_grid_power = Boolean(energyForm.value.k_flow_invert_grid_power)
  for (const [formKey, jsonKey] of Object.entries(kFlowUiKeys)) {
    const value = String(energyForm.value[formKey] || '').trim()
    if (value) obj[jsonKey] = value
    else delete obj[jsonKey]
  }
  if (obj.label_entity_min_cell && !obj.label_min_cell) obj.label_min_cell = 'Dato 1'
  if (obj.label_entity_max_cell && !obj.label_max_cell) obj.label_max_cell = 'Dato 2'
  if (obj.label_entity_batt_dis && !obj.label_batt_dis) obj.label_batt_dis = 'Scarica oggi'
  energyForm.value.k_flow_card_config_json = JSON.stringify(obj, null, 2)
}

function syncKFlowScaleToWizard() {
  energyWizardForm.value.solar_max_power = Number(energyForm.value.kflow_solar_max_power_w ?? energyWizardForm.value.solar_max_power ?? 7000)
  energyWizardForm.value.load_max_power = Number(energyForm.value.kflow_load_max_power_w ?? energyWizardForm.value.load_max_power ?? 9000)
  energyWizardForm.value.grid_max_power = Number(energyForm.value.kflow_grid_max_power_w ?? energyWizardForm.value.grid_max_power ?? 8000)
  energyWizardForm.value.battery_energy_wh = Number(energyForm.value.kflow_battery_capacity_wh ?? energyWizardForm.value.battery_energy_wh ?? 15360)
  energyWizardForm.value.battery_max_power = Number(energyForm.value.kflow_battery_max_power_w ?? energyWizardForm.value.battery_max_power ?? 5000)
  energyWizardForm.value.battery_shutdown_soc = Number(energyForm.value.kflow_battery_shutdown_soc ?? energyWizardForm.value.battery_shutdown_soc ?? 10)
}

function inferSolarMpptsFromEntities(entities = {}, fallback = 1) {
  const pvKeys = ['pv1_power_186', 'pv2_power_187', 'pv3_power_188', 'pv4_power_189', 'pv5_power', 'pv6_power']
  let highest = 0
  pvKeys.forEach((key, index) => {
    if (String(entities?.[key] || '').trim()) highest = index + 1
  })
  return Math.max(1, Math.min(6, highest || Number(fallback || 1)))
}

function entityFromConfig(entities = {}, key) {
  return String(Object.prototype.hasOwnProperty.call(entities || {}, key) ? entities[key] || '' : '')
}

const pretty = computed(() => (data.value ? JSON.stringify(data.value, null, 2) : 'Nessun dato'))
const solarMpptCount = computed(() => Math.max(1, Math.min(6, Number(energyWizardForm.value?.solar_mppts || 1))))
const energyRealtimeMappedCount = computed(() => realtimeEntityKeys.filter((k) => String(energyWizardForm.value?.[k] || '').trim()).length)
const energyDailyMappedCount = computed(() => dailyEntityKeys.filter((k) => String(energyWizardForm.value?.[k] || '').trim()).length)
const energyQuickMappedCount = computed(() => [
  energyForm.value.pv_power_entity_id,
  energyForm.value.home_power_entity_id,
  energyForm.value.grid_power_entity_id,
  energyForm.value.battery_power_entity_id,
  energyForm.value.battery_soc_entity_id,
  energyForm.value.pv_installed_kwp,
].filter((v) => String(v ?? '').trim()).length)
const energyEssentialLoadMappedCount = computed(() => [
  energyWizardForm.value.essential_load1,
  energyWizardForm.value.essential_load2,
  energyWizardForm.value.essential_load3,
  energyWizardForm.value.essential_load4,
  energyWizardForm.value.essential_load5,
  energyWizardForm.value.essential_load6,
].filter((v) => String(v || '').trim()).length)
const energyFullAuxLoadConflict = computed(() =>
  String(energyWizardForm.value.cardstyle || 'full') === 'full' &&
  Boolean(energyWizardForm.value.show_aux) &&
  energyEssentialLoadMappedCount.value >= 4
)

function openEnergyEntityPopup(mode = 'realtime') {
  energyEntityPopupMode.value = mode === 'daily' ? 'daily' : 'realtime'
  energyEntityPopupOpen.value = true
}

function editEnergyEntity(key, label) {
  const current = String(energyWizardForm.value?.[key] || '')
  const next = window.prompt(`Entity ID per: ${label}`, current)
  if (next === null) return
  energyWizardForm.value[key] = String(next || '').trim()
}

function selectEnergyEntityFromList(key, label) {
  selectedEnergyMapKey.value = String(key || '')
  editEnergyEntity(key, label)
}
const localTimestampLabel = computed(() => {
  const raw = data.value?.timestamp_local
  if (!raw) return '-'
  try {
    const d = new Date(raw)
    if (Number.isNaN(d.getTime())) return String(raw)
    return d.toLocaleString('it-IT', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    })
  } catch (_) {
    return String(raw)
  }
})
const sunCalcRawText = computed(() => {
  if (!data.value) return 'Nessun dato'
  const src = data.value
  const suncalcOnly = {
    timestamp_local: src.timestamp_local,
    timezone: src.timezone,
    coordinates: src.coordinates,
    resolved_location: src.resolved_location,
    sun_times: src.sun_times,
    sun_position: src.sun_position,
    moon_position: src.moon_position,
    moon_illumination: src.moon_illumination,
    moon_times: src.moon_times,
  }
  return JSON.stringify(suncalcOnly, null, 2)
})
const forecastConfigText = computed(() => {
  const fs = data.value?.forecast_solar
  if (!fs) return 'forecast_solar non disponibile nel payload corrente.'
  return JSON.stringify({
    enabled: true,
    url: fs.url || null,
    ok: fs.ok,
    cache_hit: fs._cache_hit,
    fetched_at_ts: fs._fetched_at_ts,
    error: fs.error || null,
  }, null, 2)
})
const forecastRawText = computed(() => {
  const raw = data.value?.forecast_solar
  if (!raw) return 'Nessun payload forecast_solar disponibile.'
  return JSON.stringify(raw, null, 2)
})
const weatherRawText = computed(() => {
  const raw = data.value?.weather
  if (!raw) return 'Nessun payload weather disponibile.'
  return JSON.stringify(raw, null, 2)
})
const weatherOpenMeteoRawText = computed(() => {
  const raw = data.value?.weather_open_meteo
  if (!raw) return 'Nessun payload weather_open_meteo disponibile.'
  return JSON.stringify(raw, null, 2)
})
const airqRawText = computed(() => {
  const raw = data.value?.air_quality
  if (!raw) return 'Nessun payload air_quality disponibile.'
  return JSON.stringify(raw, null, 2)
})
const airqNorm = computed(() => data.value?.air_quality?.normalized || null)
const tendeMap = computed(() => data.value?.tende_map || null)
const tendeMapShades = computed(() => {
  const arr = tendeMap.value?.shades
  const live = Array.isArray(arr) ? arr.filter((s) => s) : []
  return mergeTendeShades(lastValidTendeShades.value, live)
})
const tendeCoverStates = computed(() => {
  const states = tendeMap.value?.cover_states
  return states && Object.keys(states).length ? states : lastValidTendeCoverStates.value
})
const coordinatesSourceLabel = computed(() => {
  const raw = String(data.value?.coordinates_source || '').trim().toLowerCase()
  if (raw === 'e-tendeintelligenti') return 'e-Tende Intelligenti'
  if (raw === 'e-tende_missing_coords') return 'e-Tende (coordinate mancanti nel payload)'
  if (raw === 'home_assistant_core') return 'e-Control Core'
  if (raw === 'location_query') return 'Location query'
  if (raw === 'local_config') return 'Config locale e-SunMind'
  return raw || '-'
})
const tendeMapWarning = computed(() => {
  const tm = tendeMap.value
  if (!showTendeSectors.value) return ''
  if (!tm || !tm.ok) return 'Dati tende non pronti'
  if (tm.availability && tm.availability !== 'online') return `Tende ${tm.availability}`
  if (tm.stale) return 'Dati tende non aggiornati'
  return ''
})
const publicLegendItems = computed(() => {
  const items = []
  const shades = tendeMapShades.value.slice(0, 4)
  shades.forEach((s, idx) => {
    items.push({
      key: shadeKey(s) || `shade-${idx}`,
      title: s.name || `Tenda ${idx + 1}`,
      subtitle: `Az ${fmt(s.azimuth_start_deg)}° - ${fmt(s.azimuth_end_deg)}°`,
      state: (s.sensors?.calculated_command || s.sensors?.sun_state || '-'),
      color: String(s.color || colorFromIndex(idx)),
    })
  })
  return items
})
const sunWindowHeatmap = computed(() => buildSunWindowHeatmap())
const whatIfPreview = computed(() => buildWhatIfPreview())
const wizardSteps = [
  { key: 'base', label: 'Base', hint: 'Abilita automazione e scegli il comportamento quando il sole non e utile.' },
  { key: 'sun', label: 'Sole', hint: 'Allinea finestra, campo visivo e Start/Stop guardando mappa e heatmap.' },
  { key: 'positions', label: 'Posizioni', hint: 'Definisci riposo, notte, protezione sole e anti-loop motore.' },
  { key: 'weather', label: 'Meteo', hint: 'Configura facciata e posizioni di sicurezza per vento/pioggia.' },
  { key: 'thermal', label: 'Termico', hint: 'Associa il termostato climate; puo essere condiviso tra piu cover.' },
  { key: 'review', label: 'Verifica', hint: 'Controlla diagnostica, heatmap e salva la taratura.' },
]
const airqProvider = computed(() => data.value?.air_quality?.provider || null)
const airqEu = computed(() => airqNorm.value?.european_aqi)
const airqUs = computed(() => airqNorm.value?.us_aqi)
const airqPm25 = computed(() => airqNorm.value?.pm2_5)
const airqPm10 = computed(() => airqNorm.value?.pm10)
const airqNo2 = computed(() => airqNorm.value?.nitrogen_dioxide)
const airqO3 = computed(() => airqNorm.value?.ozone)
const airqCo = computed(() => airqNorm.value?.carbon_monoxide)
const airqSo2 = computed(() => airqNorm.value?.sulphur_dioxide)
const airqSeries = computed(() => {
  const h = data.value?.air_quality?.payload?.hourly
  if (!h || !Array.isArray(h.time)) return []
  const times = h.time
  const eu = h.european_aqi || []
  const us = h.us_aqi || []
  const pm25 = h.pm2_5 || []
  const pm10 = h.pm10 || []
  const rows = []
  for (let i = 0; i < Math.min(24, times.length); i += 1) {
    const t = String(times[i] || '')
    rows.push({
      time: t,
      hhmm: t.length >= 16 ? t.slice(11, 16) : '--:--',
      eu: Number(eu[i]),
      us: Number(us[i]),
      pm25: Number(pm25[i]),
      pm10: Number(pm10[i]),
    })
  }
  return rows
})
const airqMax = computed(() => {
  if (!airqSeries.value.length) return 100
  const vals = []
  for (const r of airqSeries.value) {
    for (const v of [r.eu, r.pm25, r.pm10]) {
      if (Number.isFinite(v)) vals.push(v)
    }
  }
  return vals.length ? Math.max(20, ...vals) : 100
})
const airqTicks = computed(() => {
  const m = airqMax.value
  return [0, m * 0.25, m * 0.5, m * 0.75, m]
})
const airqEuPoints = computed(() => airqSeries.value.map((p, i) => `${airqX(i).toFixed(1)},${airqY(p.eu).toFixed(1)}`).join(' '))
const airqPm25Points = computed(() => airqSeries.value.map((p, i) => `${airqX(i).toFixed(1)},${airqY(p.pm25).toFixed(1)}`).join(' '))
const airqPm10Points = computed(() => airqSeries.value.map((p, i) => `${airqX(i).toFixed(1)},${airqY(p.pm10).toFixed(1)}`).join(' '))
const airqHover = ref(null)
const airqTipX = computed(() => {
  if (!airqHover.value) return 0
  return airqHover.value.x > 690 ? airqHover.value.x - 228 : airqHover.value.x + 8
})
const airqTipY = computed(() => {
  if (!airqHover.value) return 0
  const y = airqHover.value.y - 74
  return y < 24 ? 24 : y
})
const weatherNorm = computed(() => data.value?.weather?.normalized || null)
const weatherProvider = computed(() => data.value?.weather?.provider || null)
const weatherTime = computed(() => weatherNorm.value?.time || null)
const weatherTempC = computed(() => weatherNorm.value?.air_temperature_c)
const weatherHumidityPct = computed(() => weatherNorm.value?.relative_humidity_pct)
const weatherWindMs = computed(() => weatherNorm.value?.wind_speed_ms)
const weatherWindDirDeg = computed(() => weatherNorm.value?.wind_from_direction_deg)
const weatherCloudPct = computed(() => weatherNorm.value?.cloud_area_fraction_pct)
const weatherNext1hMm = computed(() => weatherNorm.value?.precipitation_next_1h_mm)
const weatherSymbol = computed(() => weatherNorm.value?.symbol_code)
const weatherPressureHpa = computed(() => weatherNorm.value?.air_pressure_hpa)
const weatherUvIndex = computed(() => weatherNorm.value?.uv_index)
const weatherStation = computed(() => data.value?.weather_station || null)
const weatherStationNorm = computed(() => weatherStation.value?.normalized || null)
const weatherStationAllEntities = computed(() => {
  const rows = Array.isArray(weatherStation.value?.entities_all) ? weatherStation.value.entities_all : []
  return rows
    .map((e) => {
      const entityId = String(e?.entity_id || '')
      const friendlyName = String(e?.friendly_name || '')
      const raw = e?.value
      const unit = String(e?.unit || '').trim()
      const valueText = raw === null || raw === undefined || raw === '' ? '-' : `${String(raw)}${unit ? ` ${unit}` : ''}`
      return { entity_id: entityId, friendly_name: friendlyName, value_text: valueText }
    })
    .sort((a, b) => a.entity_id.localeCompare(b.entity_id))
})
const weatherStationOk = computed(() => Boolean(weatherStation.value?.ok))
const weatherStationUsed = computed(() => Boolean(data.value?.weather_guard?.station?.used))
const weatherStationTempC = computed(() => weatherStationNorm.value?.air_temperature_c)
const weatherStationHumidityPct = computed(() => weatherStationNorm.value?.relative_humidity_pct)
const weatherStationPressureHpa = computed(() => weatherStationNorm.value?.air_pressure_hpa)
const weatherStationUvIndex = computed(() => weatherStationNorm.value?.uv_index)
const weatherStationRainRateMmH = computed(() => weatherStationNorm.value?.rain_rate_mm_h)
const weatherStationWindMs = computed(() => weatherStationNorm.value?.wind_speed_ms)
const lastKnownWindDirDeg = ref(null)
const lastKnownWindMs = ref(null)
const mapWindDirDeg = computed(() => {
  const ws = Number(weatherStationNorm.value?.wind_from_direction_deg)
  if (Number.isFinite(ws)) return ws
  const wg = Number(data.value?.weather_guard?.wind_dir_deg)
  if (Number.isFinite(wg)) return wg
  const w = Number(weatherWindDirDeg.value)
  return Number.isFinite(w) ? w : null
})
const mapWindMs = computed(() => {
  const ws = Number(weatherStationNorm.value?.wind_speed_ms)
  if (Number.isFinite(ws)) return ws
  const wg = Number(data.value?.weather_guard?.wind_speed_ms)
  if (Number.isFinite(wg)) return wg
  const w = Number(weatherWindMs.value)
  return Number.isFinite(w) ? w : null
})
const weatherGuard = computed(() => data.value?.weather_guard || null)
const weatherGuardOk = computed(() => Boolean(weatherGuard.value?.ok))
const weatherGuardWindAlarm = computed(() => Boolean(weatherGuard.value?.wind_alarm))
const weatherGuardRainAlarm = computed(() => Boolean(weatherGuard.value?.rain_alarm))
const weatherGuardFacadeRisk = computed(() => Boolean(weatherGuard.value?.facade_rain_risk))
const weatherMetricLabelMap = {
  air_temperature_c: 'Temperatura',
  relative_humidity_pct: 'Umidita',
  wind_speed_ms: 'Vento',
  wind_gust_ms: 'Raffica vento',
  wind_from_direction_deg: 'Direzione vento',
  air_pressure_hpa: 'Pressione',
  cloud_area_fraction_pct: 'Nuvolosita',
  uv_index: 'Indice UV',
  symbol_code: 'Condizione',
  precipitation_next_1h_mm: 'Pioggia prossima 1h',
  rain_rate_mm_h: 'Pioggia (rate)',
  rain_1h_mm: 'Pioggia 1h',
  dew_point_c: 'Dew Point',
  feels_like_temperature_c: 'Temperatura percepita',
  solar_lux_lx: 'Solar Lux',
  solar_radiation_w_m2: 'Solar Radiation',
  vapour_pressure_deficit_hpa: 'VPD',
  time: 'Timestamp',
}
function metricUnitForKey(key) {
  if (key.includes('temperature')) return '°C'
  if (key.includes('humidity')) return '%'
  if (key.includes('wind_speed') || key.includes('wind_gust')) return 'm/s'
  if (key.includes('wind_from_direction')) return '°'
  if (key.includes('pressure')) return 'hPa'
  if (key.includes('cloud_area_fraction')) return '%'
  if (key.includes('uv_index')) return ''
  if (key.includes('precipitation') || key.includes('rain_1h')) return 'mm'
  if (key.includes('rain_rate')) return 'mm/h'
  if (key.includes('dew_point')) return '°C'
  if (key.includes('feels_like')) return '°C'
  if (key.includes('solar_lux')) return 'lx'
  if (key.includes('solar_radiation')) return 'W/m²'
  if (key.includes('vapour_pressure_deficit')) return 'hPa'
  return ''
}
function metricToDisplayValue(key, raw) {
  if (raw === null || raw === undefined || raw === '') return '-'
  if (key === 'symbol_code' || key === 'time') return String(raw)
  const n = Number(raw)
  if (!Number.isFinite(n)) return String(raw)
  const unit = metricUnitForKey(key)
  return `${fmt(n)}${unit ? ` ${unit}` : ''}`
}
function buildMetricsFromNormalized(norm) {
  if (!norm || typeof norm !== 'object') return []
  const preferredOrder = [
    'air_temperature_c',
    'feels_like_temperature_c',
    'dew_point_c',
    'relative_humidity_pct',
    'wind_speed_ms',
    'wind_gust_ms',
    'wind_from_direction_deg',
    'air_pressure_hpa',
    'cloud_area_fraction_pct',
    'precipitation_next_1h_mm',
    'rain_rate_mm_h',
    'rain_1h_mm',
    'uv_index',
    'solar_lux_lx',
    'solar_radiation_w_m2',
    'vapour_pressure_deficit_hpa',
    'symbol_code',
    'time',
  ]
  const keys = Object.keys(norm)
  const ordered = [
    ...preferredOrder.filter((k) => keys.includes(k)),
    ...keys.filter((k) => !preferredOrder.includes(k)),
  ]
  return ordered.map((key) => ({
    key,
    label: weatherMetricLabelMap[key] || key,
    value: metricToDisplayValue(key, norm[key]),
  }))
}
const weatherWebMetrics = computed(() => buildMetricsFromNormalized(weatherNorm.value))
const weatherStationMetrics = computed(() => buildMetricsFromNormalized(weatherStationNorm.value))
const externalTempC = computed(() => {
  const v = Number(data.value?.external_temp_live?.state)
  return Number.isFinite(v) ? v : null
})
const externalHumidityPct = computed(() => {
  const v = Number(data.value?.external_humidity_live?.state)
  return Number.isFinite(v) ? v : null
})
const externalTempEntityId = computed(() => String(data.value?.external_temp_live?.entity_id || ''))
const externalTempStatus = computed(() => (data.value?.external_temp_live?.ok ? 'ok' : 'errore'))
const externalTempError = computed(() => String(data.value?.external_temp_live?.error || ''))
const pvLiveEntityId = computed(() => String(data.value?.pv_live?.entity_id || ''))
const pvLiveStatus = computed(() => (data.value?.pv_live?.ok ? 'ok' : 'errore'))
const pvLiveError = computed(() => String(data.value?.pv_live?.error || ''))
const tempDeltaC = computed(() => {
  if (externalTempC.value === null || externalTempC.value === undefined) return null
  if (weatherTempC.value === null || weatherTempC.value === undefined) return null
  const r = Number(externalTempC.value)
  const m = Number(weatherTempC.value)
  if (!Number.isFinite(r) || !Number.isFinite(m)) return null
  return r - m
})
const weatherWindCardinal = computed(() => {
  const d = Number(weatherWindDirDeg.value)
  if (!Number.isFinite(d)) return '-'
  const dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
  const idx = Math.round((((d % 360) + 360) % 360) / 45) % 8
  return dirs[idx]
})
const pvMeasuredW = computed(() => {
  const v = Number(data.value?.pv_live?.watts)
  return Number.isFinite(v) ? Math.max(0, v) : null
})
const pvForecastNowW = computed(() => {
  const w = data.value?.forecast_solar?.payload?.result?.watts
  if (!w || typeof w !== 'object') return null
  const now = new Date()
  const key = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:00:00`
  const v = Number(w[key])
  if (Number.isFinite(v)) return Math.max(0, v)
  return null
})
const pvLiveRatio = computed(() => {
  const m = Number(pvMeasuredW.value)
  const f = Number(pvForecastNowW.value)
  if (!Number.isFinite(m) || !Number.isFinite(f) || f <= 0) return 0.7
  return Math.max(0, Math.min(1.25, m / f))
})
const energyNorm = computed(() => data.value?.energy?.normalized || null)
const livoltekNorm = computed(() => livoltekStatus.value?.normalized || {})
const livoltekRawText = computed(() => {
  const raw = livoltekStatus.value?.raw
  if (!raw) return 'Nessun JSON disponibile. Abilita Livoltek e usa Probe API o Refresh.'
  try {
    return JSON.stringify(raw, null, 2)
  } catch {
    return String(raw)
  }
})
const energySiteCards = computed(() => {
  const rows = Array.isArray(data.value?.energy?.sites) ? data.value.energy.sites : []
  return rows.map((s, idx) => ({
    id: normalizeEnergySiteId(s?.site_id || s?.id || `impianto-${idx + 1}`, `impianto-${idx + 1}`),
    name: String(s?.site_name || s?.name || `Impianto ${idx + 1}`),
    pv: Number(s?.normalized?.pv_power_w),
    home: Number(s?.normalized?.home_power_w),
  }))
})
const energyEnabled = computed(() => Boolean(data.value?.energy?.enabled ?? energyForm.value.enabled))
const energyTheme = computed(() => {
  const qp = new URLSearchParams(window.location.search || '')
  const qTheme = String(qp.get('theme') || '').trim().toLowerCase()
  if (qTheme === 'classic' || qTheme === 'classic_flow') return 'classic_flow'
  if (qTheme === 'dark' || qTheme === 'technical_dark') return 'technical_dark'
  if (qTheme === 'minimal' || qTheme === 'minimal_light') return 'minimal_light'
  const fromData = String(data.value?.energy?.theme || energyForm.value.theme || 'classic_flow').trim().toLowerCase()
  if (fromData === 'technical_dark' || fromData === 'minimal_light' || fromData === 'classic_flow') return fromData
  return 'classic_flow'
})
const energyThemeClass = computed(() => `energy-theme-${energyTheme.value}`)
const energyPvPowerW = computed(() => Number.isFinite(Number(energyNorm.value?.pv_power_w)) ? Number(energyNorm.value?.pv_power_w) : null)
const energyHomePowerW = computed(() => Number.isFinite(Number(energyNorm.value?.home_power_w)) ? Number(energyNorm.value?.home_power_w) : null)
const energyGridPowerW = computed(() => Number.isFinite(Number(energyNorm.value?.grid_power_w)) ? Number(energyNorm.value?.grid_power_w) : null)
const energyBatteryPowerW = computed(() => Number.isFinite(Number(energyNorm.value?.battery_power_w)) ? Number(energyNorm.value?.battery_power_w) : null)
const energyBatterySocPct = computed(() => Number.isFinite(Number(energyNorm.value?.battery_soc_pct)) ? Number(energyNorm.value?.battery_soc_pct) : null)
const energyInstalledKwp = computed(() => Number.isFinite(Number(energyNorm.value?.pv_installed_kwp)) ? Number(energyNorm.value?.pv_installed_kwp) : Number(energyForm.value.pv_installed_kwp || 0))
const energyPvTodayKwh = computed(() => Number.isFinite(Number(energyNorm.value?.pv_energy_today_kwh)) ? Number(energyNorm.value?.pv_energy_today_kwh) : null)
const energyHomeTodayKwh = computed(() => Number.isFinite(Number(energyNorm.value?.home_energy_today_kwh)) ? Number(energyNorm.value?.home_energy_today_kwh) : null)
const energyGridImportTodayKwh = computed(() => Number.isFinite(Number(energyNorm.value?.grid_import_today_kwh)) ? Number(energyNorm.value?.grid_import_today_kwh) : null)
const energyGridExportTodayKwh = computed(() => Number.isFinite(Number(energyNorm.value?.grid_export_today_kwh)) ? Number(energyNorm.value?.grid_export_today_kwh) : null)
const weatherWindVec = computed(() => {
  const dir = Number(weatherWindDirDeg.value)
  const speed = Number(weatherWindMs.value)
  const s = Number.isFinite(speed) ? Math.max(0, Math.min(16, speed)) : 2
  const a = Number.isFinite(dir) ? (dir * Math.PI) / 180 : 180 * (Math.PI / 180)
  return {
    vx: Math.sin(a) * s * 0.5,
    vy: Math.cos(a) * s * 0.5,
  }
})
const weatherCloudIntensity = computed(() => {
  const c = Number(weatherCloudPct.value)
  const cloudBase = Number.isFinite(c) ? Math.max(0.08, Math.min(0.85, c / 100)) : 0.35
  const ratio = pvLiveRatio.value
  // If real PV is low vs forecast, increase cloud aggressiveness.
  const factor = ratio >= 1 ? 0.72 : (1 + (1 - ratio) * 0.9)
  return Math.max(0.05, Math.min(0.92, cloudBase * factor))
})
const weatherRainIntensity = computed(() => {
  const r = Number(weatherNext1hMm.value)
  if (!Number.isFinite(r) || r <= 0) return 0
  const ratio = pvLiveRatio.value
  const factor = ratio >= 1 ? 0.8 : (1 + (1 - ratio) * 0.6)
  return Math.max(0.06, Math.min(1, (r / 3) * factor))
})
const weatherSeries = computed(() => {
  const ts = data.value?.weather?.payload?.properties?.timeseries
  if (!Array.isArray(ts)) return []
  return ts.slice(0, 24).map((row) => {
    const d = row?.data || {}
    const inst = d?.instant?.details || {}
    const n1 = d?.next_1_hours || {}
    const rain = Number(n1?.details?.precipitation_amount ?? 0)
    const temp = Number(inst?.air_temperature)
    const wind = Number(inst?.wind_speed)
    const humidity = Number(inst?.relative_humidity)
    const pressure = Number(inst?.air_pressure_at_sea_level)
    const time = String(row?.time || '')
    const hhmm = time.length >= 16 ? time.slice(11, 16) : '--:--'
    return {
      time,
      hhmm,
      temp: Number.isFinite(temp) ? temp : 0,
      rain: Number.isFinite(rain) ? rain : 0,
      wind: Number.isFinite(wind) ? wind : 0,
      humidity: Number.isFinite(humidity) ? humidity : 0,
      pressure: Number.isFinite(pressure) ? pressure : 0,
    }
  })
})
const weatherTempMin = computed(() => {
  if (!weatherSeries.value.length) return 0
  return Math.min(...weatherSeries.value.map((x) => x.temp))
})
const weatherTempMax = computed(() => {
  if (!weatherSeries.value.length) return 1
  return Math.max(...weatherSeries.value.map((x) => x.temp))
})
const weatherRainMax = computed(() => {
  if (!weatherSeries.value.length) return 1
  return Math.max(0.1, ...weatherSeries.value.map((x) => x.rain))
})
const weatherWindMax = computed(() => {
  if (!weatherSeries.value.length) return 1
  return Math.max(0.1, ...weatherSeries.value.map((x) => x.wind))
})
const weatherPressureMin = computed(() => {
  if (!weatherSeries.value.length) return 1000
  return Math.min(...weatherSeries.value.map((x) => x.pressure))
})
const weatherPressureMax = computed(() => {
  if (!weatherSeries.value.length) return 1020
  return Math.max(...weatherSeries.value.map((x) => x.pressure))
})
const weatherTempTicks = computed(() => {
  const mn = weatherTempMin.value
  const mx = weatherTempMax.value
  const span = Math.max(1, mx - mn)
  return [mn, mn + span * 0.33, mn + span * 0.66, mx]
})
const weatherRainTicks = computed(() => {
  const mx = weatherRainMax.value
  return [0, mx * 0.33, mx * 0.66, mx]
})
const weatherWindTicks = computed(() => {
  const mx = weatherWindMax.value
  return [0, mx * 0.33, mx * 0.66, mx]
})
const weatherTempPoints = computed(() => {
  const s = weatherSeries.value
  if (!s.length) return ''
  return s.map((p, i) => `${weatherXFromIdx(i).toFixed(1)},${weatherYFromTemp(p.temp).toFixed(1)}`).join(' ')
})
const weatherRealTempPoints = computed(() => {
  const s = weatherSeries.value
  const rt = Number(externalTempC.value)
  if (!s.length || !Number.isFinite(rt)) return ''
  return s.map((_, i) => `${weatherXFromIdx(i).toFixed(1)},${weatherYFromTemp(rt).toFixed(1)}`).join(' ')
})
const weatherWindPoints = computed(() => {
  const s = weatherSeries.value
  if (!s.length) return ''
  return s.map((p, i) => `${weatherXFromIdx(i).toFixed(1)},${weatherYFromWind(p.wind).toFixed(1)}`).join(' ')
})
const weatherHumidityPoints = computed(() => {
  const s = weatherSeries.value
  if (!s.length) return ''
  return s.map((p, i) => `${weatherXFromIdx(i).toFixed(1)},${weatherYFromHumidity(p.humidity).toFixed(1)}`).join(' ')
})
const weatherPressurePoints = computed(() => {
  const s = weatherSeries.value
  if (!s.length) return ''
  return s.map((p, i) => `${weatherXFromIdx(i).toFixed(1)},${weatherYFromPressure(p.pressure).toFixed(1)}`).join(' ')
})
const weatherXAxisHours = computed(() => {
  const s = weatherSeries.value
  if (!s.length) return []
  return s.filter((_, i) => i % 3 === 0 || i === s.length - 1)
})
const weatherHoverPoint = ref(null)
const weatherBarHalfWidth = computed(() => {
  const n = weatherSeries.value.length || 1
  return Math.max(3, Math.min(10, (820 / n) * 0.32))
})
const weatherHoverTooltipX = computed(() => {
  if (!weatherHoverPoint.value) return 0
  return weatherHoverPoint.value.x > 700 ? weatherHoverPoint.value.x - 188 : weatherHoverPoint.value.x + 8
})
const weatherHoverTooltipY = computed(() => {
  if (!weatherHoverPoint.value) return 0
  const y = weatherHoverPoint.value.y - 60
  return y < 24 ? 24 : y
})

const forecastResult = computed(() => data.value?.forecast_solar?.payload?.result || null)
const forecastOk = computed(() => Boolean(data.value?.forecast_solar?.ok))
const fvTodayWh = computed(() => {
  const d = forecastResult.value?.watt_hours_day
  if (!d || typeof d !== 'object') return null
  const keys = Object.keys(d).sort()
  return keys.length ? Number(d[keys[0]]) : null
})
const fvTomorrowWh = computed(() => {
  const d = forecastResult.value?.watt_hours_day
  if (!d || typeof d !== 'object') return null
  const keys = Object.keys(d).sort()
  return keys.length > 1 ? Number(d[keys[1]]) : null
})
const fvCurrentW = computed(() => {
  const w = forecastResult.value?.watts
  if (!w || typeof w !== 'object') return null
  const now = new Date()
  const mk = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:00:00`
  if (mk in w) return Number(w[mk])
  const keys = Object.keys(w).sort()
  return keys.length ? Number(w[keys[0]]) : null
})
const fvPeakTodayW = computed(() => {
  const w = forecastResult.value?.watts
  if (!w || typeof w !== 'object') return null
  const today = new Date().toISOString().slice(0, 10)
  const vals = Object.entries(w)
    .filter(([k]) => String(k).startsWith(today))
    .map(([, v]) => Number(v))
    .filter((x) => Number.isFinite(x))
  if (vals.length) return Math.max(...vals)
  const all = Object.values(w).map((v) => Number(v)).filter((x) => Number.isFinite(x))
  return all.length ? Math.max(...all) : null
})
const fvTodaySeries = computed(() => {
  const w = forecastResult.value?.watts
  const whp = forecastResult.value?.watt_hours_period
  if (!w || typeof w !== 'object') return []
  const dayPrefix = selectedForecastDate.value || (new Date().toISOString().slice(0, 10))
  const series = Object.entries(w)
    .filter(([k]) => String(k).startsWith(dayPrefix))
    .map(([k, v]) => {
      const hh = Number(String(k).slice(11, 13))
      const mm = Number(String(k).slice(14, 16))
      const wh = whp && typeof whp === 'object' ? Number(whp[k]) : null
      return {
        minute: (hh * 60) + mm,
        w: Number(v),
        wh: Number.isFinite(wh) ? wh : null,
      }
    })
    .filter((x) => Number.isFinite(x.minute) && Number.isFinite(x.w))
    .sort((a, b) => a.minute - b.minute)
  return series
})
const fvPeakSelectedW = computed(() => {
  const s = fvTodaySeries.value
  if (!s.length) return null
  return Math.max(...s.map((x) => x.w))
})
const fvChartPoints = computed(() => {
  const s = fvTodaySeries.value
  if (!s.length) return ''
  const maxW = Math.max(1, ...s.map((x) => x.w))
  return s.map((p) => {
    const x = 40 + (p.minute / 1440) * 640
    const y = 150 - (p.w / maxW) * 130
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
})
const fvNowX = computed(() => {
  const now = new Date()
  const minute = (now.getHours() * 60) + now.getMinutes()
  return 40 + (minute / 1440) * 640
})
const forecastFetchedAtText = computed(() => {
  const ts = Number(data.value?.forecast_solar?._fetched_at_ts)
  if (!Number.isFinite(ts) || ts <= 0) return '-'
  return new Date(ts * 1000).toLocaleString()
})
const fvDayRows = computed(() => {
  const d = forecastResult.value?.watt_hours_day
  if (!d || typeof d !== 'object') return []
  const entries = Object.entries(d)
    .map(([date, wh]) => ({ date: String(date), wh: Number(wh) }))
    .filter((x) => Number.isFinite(x.wh))
    .sort((a, b) => a.date.localeCompare(b.date))
  if (!entries.length) return []
  const maxWh = Math.max(...entries.map((x) => x.wh), 1)
  return entries.map((x) => {
    const dt = new Date(`${x.date}T12:00:00`)
    const dayName = dt.toLocaleDateString('it-IT', { weekday: 'long' })
    const dayShort = dt.toLocaleDateString('it-IT', { weekday: 'short' })
    const dateLabel = dt.toLocaleDateString('it-IT')
    return {
      ...x,
      dayName,
      dayShort,
      dateLabel,
      pct: Math.max(4, (x.wh / maxWh) * 100),
    }
  })
})
const fvHourBars = computed(() => {
  const s = fvTodaySeries.value
  if (!s.length) return []
  const maxW = Math.max(...s.map((x) => x.w), 1)
  return s.map((x) => {
    const hh = Math.floor(x.minute / 60)
    const mm = x.minute % 60
    return {
      w: x.w,
      pct: Math.max(3, (x.w / maxW) * 100),
      kwh: Number.isFinite(x.wh) ? Number(x.wh) / 1000 : (Number(x.w) / 1000),
      time: `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`,
    }
  })
})
const yTicks = computed(() => {
  const maxW = Math.max(1, Number(fvPeakSelectedW.value || 1))
  return [0, maxW * 0.25, maxW * 0.5, maxW * 0.75, maxW]
})
const yTicksBars = computed(() => [...yTicks.value].reverse())
const xTicks = [0, 180, 360, 540, 720, 900, 1080, 1260, 1440]
const hoverPoint = ref(null)
const hoverTooltipX = computed(() => {
  if (!hoverPoint.value) return 0
  return hoverPoint.value.x > 560 ? hoverPoint.value.x - 138 : hoverPoint.value.x + 8
})
const hoverTooltipY = computed(() => {
  if (!hoverPoint.value) return 0
  const y = hoverPoint.value.y - 44
  return y < 22 ? 22 : y
})

function fmt(v) {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return '-'
  return Number(v).toFixed(2)
}
function fmt0(v) {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return '-'
  return Math.round(Number(v)).toString()
}
function fmt2(v) {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return '-'
  return Number(v).toFixed(2)
}
function fmt1(v) {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return '-'
  return Number(v).toFixed(1)
}
function fmtKw(w) {
  if (w === null || w === undefined || Number.isNaN(Number(w))) return '-'
  return (Number(w) / 1000).toFixed(2)
}
function fmtTs(ts) {
  const n = Number(ts)
  if (!Number.isFinite(n) || n <= 0) return '-'
  return new Date(n * 1000).toLocaleString('it-IT')
}
function xFromMinute(minute) {
  return 40 + (Number(minute) / 1440) * 640
}
function yFromW(w) {
  const maxW = Math.max(1, Number(fvPeakSelectedW.value || 1))
  return 150 - (Number(w) / maxW) * 130
}
function fmtHourTick(minute) {
  const h = Math.floor(Number(minute) / 60)
  return `${String(h).padStart(2, '0')}:00`
}
function airqX(i) {
  const n = Math.max(1, airqSeries.value.length - 1)
  return 50 + (Number(i) / n) * 820
}
function airqY(v) {
  const m = Math.max(1, airqMax.value)
  const vv = Number(v)
  const val = Number.isFinite(vv) ? vv : 0
  return 190 - (val / m) * 166
}
function onAirqChartMove(evt) {
  const s = airqSeries.value
  if (!s.length) {
    airqHover.value = null
    return
  }
  const rect = evt.currentTarget.getBoundingClientRect()
  const relX = evt.clientX - rect.left
  const x = (relX / rect.width) * 900
  const idx = Math.max(0, Math.min(s.length - 1, Math.round(((x - 50) / 820) * (s.length - 1))))
  const p = s[idx]
  airqHover.value = { ...p, x: airqX(idx), y: airqY(p.eu) }
}
function onAirqChartLeave() {
  airqHover.value = null
}
function weatherXFromIdx(idx) {
  const n = Math.max(1, weatherSeries.value.length - 1)
  return 50 + (Number(idx) / n) * 820
}
function weatherYFromTemp(temp) {
  const mn = weatherTempMin.value
  const mx = weatherTempMax.value
  const span = Math.max(1, mx - mn)
  return 190 - ((Number(temp) - mn) / span) * 166
}
function weatherYFromRain(rain) {
  const mx = Math.max(0.1, weatherRainMax.value)
  return 190 - (Number(rain) / mx) * 90
}
function weatherYFromWind(wind) {
  const mx = Math.max(0.1, weatherWindMax.value)
  return 190 - (Number(wind) / mx) * 160
}
function weatherYFromHumidity(humidity) {
  return 190 - (Math.max(0, Math.min(100, Number(humidity))) / 100) * 160
}
function weatherYFromPressure(pressure) {
  const mn = weatherPressureMin.value
  const mx = weatherPressureMax.value
  const span = Math.max(0.1, mx - mn)
  return 190 - ((Number(pressure) - mn) / span) * 160
}
function onWeatherChartMove(evt) {
  const s = weatherSeries.value
  if (!s.length) {
    weatherHoverPoint.value = null
    return
  }
  const rect = evt.currentTarget.getBoundingClientRect()
  const relX = evt.clientX - rect.left
  const x = (relX / rect.width) * 900
  const idx = Math.max(0, Math.min(s.length - 1, Math.round(((x - 50) / 820) * (s.length - 1))))
  const p = s[idx]
  const rt = Number(externalTempC.value)
  weatherHoverPoint.value = {
    ...p,
    x: weatherXFromIdx(idx),
    y: weatherYFromTemp(p.temp),
    label: p.time ? p.time.replace('T', ' ').replace('Z', ' UTC') : p.hhmm,
    deltaRealTemp: Number.isFinite(rt) ? (rt - Number(p.temp)) : null,
  }
}
function onWeatherChartLeave() {
  weatherHoverPoint.value = null
}

function resizeWeatherCanvas() {
  const cv = weatherCanvasEl.value
  if (!cv) return
  const rect = cv.getBoundingClientRect()
  const ratio = window.devicePixelRatio || 1
  const w = Math.max(1, Math.floor(rect.width * ratio))
  const h = Math.max(1, Math.floor(rect.height * ratio))
  if (cv.width !== w || cv.height !== h) {
    cv.width = w
    cv.height = h
  }
}

function seedWeatherParticles() {
  const cv = weatherCanvasEl.value
  if (!cv) return
  const w = cv.width
  const h = cv.height
  weatherClouds = Array.from({ length: 7 }, () => ({
    x: Math.random() * w,
    y: (Math.random() * h * 0.5) + h * 0.05,
    r: 70 + Math.random() * 140,
    a: 0.035 + Math.random() * 0.055,
    phase: Math.random() * Math.PI * 2,
  }))
  weatherMist = Array.from({ length: 5 }, () => ({
    x: Math.random() * w,
    y: Math.random() * h,
    r: 180 + Math.random() * 260,
    a: 0.018 + Math.random() * 0.028,
  }))
  weatherRain = Array.from({ length: 90 }, () => ({
    x: Math.random() * w,
    y: Math.random() * h,
    l: 10 + Math.random() * 18,
    v: 70 + Math.random() * 110,
    a: 0.055 + Math.random() * 0.12,
  }))
}

function drawWeatherOverlayFrame(ts) {
  const cv = weatherCanvasEl.value
  if (!cv || !weatherAnimEnabled.value || tab.value !== 'user') return
  if (!weatherLastTs) weatherLastTs = ts
  const dt = Math.max(0.001, Math.min(0.05, (ts - weatherLastTs) / 1000))
  weatherLastTs = ts

  const ctx = cv.getContext('2d')
  if (!ctx) return
  const w = cv.width
  const h = cv.height
  ctx.clearRect(0, 0, w, h)

  const wind = weatherWindVec.value
  const cloudI = weatherCloudIntensity.value
  const rainI = weatherRainIntensity.value

  if (!weatherClouds.length || !weatherRain.length || !weatherMist.length) seedWeatherParticles()

  const daylight = Math.max(0.08, Math.min(1, Number(data.value?.sun_position?.altitude_deg ?? currentSun.value.altitudeDeg ?? 0) / 65))
  const sunVisibility = Math.max(0, Math.min(1, (1 - cloudI * 0.82) * (1 - rainI * 0.45) * daylight))
  if (sunVisibility > 0.04) {
    const cx = w * 0.5
    const cy = h * 0.42
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(w, h) * 0.72)
    g.addColorStop(0, `rgba(255,224,92,${(0.12 * sunVisibility).toFixed(3)})`)
    g.addColorStop(0.35, `rgba(255,204,65,${(0.055 * sunVisibility).toFixed(3)})`)
    g.addColorStop(1, 'rgba(255,204,65,0)')
    ctx.fillStyle = g
    ctx.fillRect(0, 0, w, h)
  }

  if (cloudI > 0.08) {
    ctx.fillStyle = `rgba(170,188,198,${(0.045 * cloudI).toFixed(3)})`
    ctx.fillRect(0, 0, w, h)
  }

  for (const m of weatherMist) {
    m.x += wind.vx * dt * 4
    if (m.x > w + m.r) m.x = -m.r
    if (m.x < -m.r) m.x = w + m.r
    const g = ctx.createRadialGradient(m.x, m.y, 0, m.x, m.y, m.r)
    g.addColorStop(0, `rgba(205,222,230,${(m.a * cloudI).toFixed(3)})`)
    g.addColorStop(1, 'rgba(205,222,230,0)')
    ctx.fillStyle = g
    ctx.fillRect(m.x - m.r, m.y - m.r, m.r * 2, m.r * 2)
  }

  for (const c of weatherClouds) {
    c.phase += dt * 0.22
    c.x += wind.vx * dt * 7
    c.y += Math.sin(c.phase) * dt * 3 + wind.vy * dt * 0.8
    if (c.x > w + c.r) c.x = -c.r
    if (c.x < -c.r) c.x = w + c.r
    if (c.y > h * 0.72) c.y = h * 0.12
    if (c.y < h * 0.04) c.y = h * 0.62
    const g = ctx.createRadialGradient(c.x, c.y, c.r * 0.1, c.x, c.y, c.r)
    g.addColorStop(0, `rgba(196,213,220,${(c.a * cloudI).toFixed(3)})`)
    g.addColorStop(0.58, `rgba(154,174,184,${(c.a * cloudI * 0.55).toFixed(3)})`)
    g.addColorStop(1, 'rgba(154,174,184,0)')
    ctx.fillStyle = g
    ctx.fillRect(c.x - c.r, c.y - c.r, c.r * 2, c.r * 2)
  }

  if (rainI > 0.02) {
    const sx = wind.vx * 7
    const sy = 115 + Math.abs(wind.vy * 4)
    ctx.lineCap = 'round'
    for (const p of weatherRain) {
      p.x += sx * dt + wind.vx * dt * 10
      p.y += (p.v + sy) * dt
      if (p.y > h + 20) {
        p.y = -10
        p.x = Math.random() * w
      }
      if (p.x > w + 20) p.x = -10
      if (p.x < -20) p.x = w + 10
      ctx.strokeStyle = `rgba(160,205,222,${(p.a * rainI * 0.62).toFixed(3)})`
      ctx.lineWidth = 0.75
      ctx.beginPath()
      ctx.moveTo(p.x, p.y)
      ctx.lineTo(p.x + sx * 0.05, p.y + p.l)
      ctx.stroke()
    }
  }

  // Directional air movement, intentionally faint to avoid flicker.
  const windStrength = Math.min(1, Math.hypot(wind.vx, wind.vy) / 5)
  if (windStrength > 0.12 && rainI < 0.35) {
    ctx.strokeStyle = `rgba(185,225,235,${(0.018 + windStrength * 0.035).toFixed(3)})`
    ctx.lineWidth = 1
    for (let i = 0; i < 9; i += 1) {
      const bx = ((ts * 0.0035 + i * 173) % (w + 100)) - 50
      const by = (i * 83) % (h * 0.78)
      const lx = wind.vx * 2.3
      const ly = wind.vy * 2.3
      ctx.beginPath()
      ctx.moveTo(bx, by)
      ctx.lineTo(bx + lx * 9, by + ly * 9)
      ctx.stroke()
    }
  }

  weatherRafId = requestAnimationFrame(drawWeatherOverlayFrame)
}

function startWeatherAnimation() {
  if (weatherRafId) cancelAnimationFrame(weatherRafId)
  weatherLastTs = 0
  resizeWeatherCanvas()
  seedWeatherParticles()
  weatherRafId = requestAnimationFrame(drawWeatherOverlayFrame)
}

function stopWeatherAnimation() {
  if (weatherRafId) {
    cancelAnimationFrame(weatherRafId)
    weatherRafId = 0
  }
  const cv = weatherCanvasEl.value
  const ctx = cv?.getContext('2d')
  if (ctx && cv) ctx.clearRect(0, 0, cv.width, cv.height)
}

function initBlockToggles() {
  if (blockTogglesInited) return
  const roots = document.querySelectorAll('.panel, .card, .map-block-group')
  roots.forEach((el) => {
    if (!(el instanceof HTMLElement)) return
    if (el.querySelector(':scope > .block-toggle-inline')) return
    el.classList.add('collapsible-block')
    const t = document.createElement('div')
    t.className = 'block-toggle-inline'
    t.title = 'Click per ridurre/allargare'
    t.addEventListener('click', () => {
      el.classList.toggle('is-collapsed')
    })
    el.prepend(t)
  })
  blockTogglesInited = true
}
function onChartMove(evt) {
  const series = fvTodaySeries.value
  if (!series.length) {
    hoverPoint.value = null
    return
  }
  const rect = evt.currentTarget.getBoundingClientRect()
  const relX = evt.clientX - rect.left
  const x = (relX / rect.width) * 700
  const minute = Math.max(0, Math.min(1440, ((x - 40) / 640) * 1440))
  let best = series[0]
  let d = Math.abs(series[0].minute - minute)
  for (const p of series) {
    const nd = Math.abs(p.minute - minute)
    if (nd < d) {
      d = nd
      best = p
    }
  }
  const hh = Math.floor(best.minute / 60)
  const mm = best.minute % 60
  hoverPoint.value = {
    minute: best.minute,
    w: best.w,
    x: xFromMinute(best.minute),
    y: yFromW(best.w),
    time: `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`,
  }
}
function onChartLeave() {
  hoverPoint.value = null
}
function toDeg(rad) { return (rad * 180) / Math.PI }
function suncalcAzToCompassDeg(azimuthRad) { return (toDeg(azimuthRad) + 180 + 360) % 360 }

function destinationPoint(latDeg, lonDeg, bearingDeg, distanceM) {
  const R = 6378137
  const brng = (bearingDeg * Math.PI) / 180
  const lat1 = (latDeg * Math.PI) / 180
  const lon1 = (lonDeg * Math.PI) / 180
  const lat2 = Math.asin(Math.sin(lat1) * Math.cos(distanceM / R) + Math.cos(lat1) * Math.sin(distanceM / R) * Math.cos(brng))
  const lon2 = lon1 + Math.atan2(Math.sin(brng) * Math.sin(distanceM / R) * Math.cos(lat1), Math.cos(distanceM / R) - Math.sin(lat1) * Math.sin(lat2))
  return [(lat2 * 180) / Math.PI, (lon2 * 180) / Math.PI]
}

function targetValue(value) {
  return value === null || value === undefined || value === '' ? '-' : value
}

function boolLabel(value) {
  if (value === true) return 'Acceso'
  if (value === false) return 'Spento'
  return '-'
}

function colorFromIndex(index) {
  const hue = (index * 137.508) % 360
  return `hsl(${hue.toFixed(1)}, 82%, 56%)`
}

function buildSectorPolygonPoints(azStart, azEnd, radiusM) {
  const pts = [[lat.value, lon.value]]
  const a0 = ((Number(azStart) % 360) + 360) % 360
  let a1 = ((Number(azEnd) % 360) + 360) % 360
  if (a1 < a0) a1 += 360
  const step = 3
  for (let a = a0; a <= a1; a += step) {
    pts.push(destinationPoint(lat.value, lon.value, a % 360, radiusM))
  }
  pts.push(destinationPoint(lat.value, lon.value, a1 % 360, radiusM))
  pts.push([lat.value, lon.value])
  return pts
}

function buildSectorBandPolygonPoints(azStart, azEnd, radiusOuterM, radiusInnerM) {
  const pts = []
  const a0 = ((Number(azStart) % 360) + 360) % 360
  let a1 = ((Number(azEnd) % 360) + 360) % 360
  if (a1 < a0) a1 += 360
  const step = 3
  for (let a = a0; a <= a1; a += step) pts.push(destinationPoint(lat.value, lon.value, a % 360, radiusOuterM))
  pts.push(destinationPoint(lat.value, lon.value, a1 % 360, radiusOuterM))
  for (let a = a1; a >= a0; a -= step) pts.push(destinationPoint(lat.value, lon.value, a % 360, radiusInnerM))
  pts.push(destinationPoint(lat.value, lon.value, a0 % 360, radiusInnerM))
  return pts
}

function buildRingPoints(radiusM) {
  const pts = []
  for (let a = 0; a <= 360; a += 2) {
    pts.push(destinationPoint(lat.value, lon.value, a, radiusM))
  }
  return pts
}

function baseDateAtHour(hour, minute = 0) {
  const base = data.value?.timestamp_local ? new Date(data.value.timestamp_local) : new Date()
  const d = new Date(base)
  d.setHours(hour, minute, 0, 0)
  return d
}

function altitudeToRadius(altDeg) {
  // Sky-dome projection on horizontal plane: r = R * cos(altitude)
  const a = Math.max(0, Math.min(90, Number(altDeg)))
  return cfg.value.sectorRadiusM * Math.cos((a * Math.PI) / 180)
}

function buildSunPathPoints() {
  const points = []
  const sunrise = data.value?.sun_times?.sunrise ? new Date(data.value.sun_times.sunrise) : baseDateAtHour(6)
  const sunset = data.value?.sun_times?.sunset ? new Date(data.value.sun_times.sunset) : baseDateAtHour(20)
  const srPos = SunCalc.getPosition(sunrise, lat.value, lon.value)
  const ssPos = SunCalc.getPosition(sunset, lat.value, lon.value)
  const azStart = suncalcAzToCompassDeg(srPos.azimuth)
  const azEndRaw = suncalcAzToCompassDeg(ssPos.azimuth)
  const azEnd = azEndRaw < azStart ? azEndRaw + 360 : azEndRaw
  const step = 2
  const r = cfg.value.pathRadiusM
  for (let a = azStart; a <= azEnd; a += step) {
    const real = a >= 360 ? a - 360 : a
    points.push(destinationPoint(lat.value, lon.value, real, r))
  }
  return points
}

function buildElevationCurvePoints(sunrise, sunset, steps = 72) {
  const points = []
  const srMs = sunrise.getTime()
  const ssMs = sunset.getTime()
  const total = Math.max(1, ssMs - srMs)
  for (let i = 0; i <= steps; i += 1) {
    const t = srMs + (total * i) / steps
    const dt = new Date(t)
    const p = SunCalc.getPosition(dt, lat.value, lon.value)
    const az = suncalcAzToCompassDeg(p.azimuth)
    const alt = Math.max(0, toDeg(p.altitude))
    const r = altitudeToRadius(alt)
    points.push(destinationPoint(lat.value, lon.value, az, r))
  }
  return points
}

function buildElevationCurveForDate(baseDate, steps = 96) {
  const times = SunCalc.getTimes(baseDate, lat.value, lon.value)
  const sunrise = times?.sunrise instanceof Date ? times.sunrise : baseDateAtHour(6)
  const sunset = times?.sunset instanceof Date ? times.sunset : baseDateAtHour(20)
  return buildElevationCurvePoints(sunrise, sunset, steps)
}

function norm360(v) {
  return ((Number(v) % 360) + 360) % 360
}

function angleDeltaDeg(a, b) {
  return Math.abs((((Number(a) - Number(b) + 540) % 360) + 360) % 360 - 180)
}

function isAzimuthInRange(az, start, end) {
  const a = norm360(az)
  const s = norm360(start)
  const e = norm360(end)
  if (s <= e) return a >= s && a <= e
  return a >= s || a <= e
}

function shadeSunSector(shade) {
  if (!shade) return { start: 0, end: 0, center: 0 }
  if (shade.use_start_stop_azimuth) {
    const start = Number(shade.azimuth_start_deg)
    const end = Number(shade.azimuth_end_deg)
    const s = Number.isFinite(start) ? start : 0
    const e = Number.isFinite(end) ? end : s
    return { start: s, end: e, center: norm360(s + (((norm360(e) - norm360(s) + 360) % 360) / 2)) }
  }
  const center = Number.isFinite(Number(shade.window_azimuth)) ? Number(shade.window_azimuth) : 0
  const left = Number.isFinite(Number(shade.fov_left)) ? Number(shade.fov_left) : 0
  const right = Number.isFinite(Number(shade.fov_right)) ? Number(shade.fov_right) : left
  return { start: center - left, end: center + right, center: norm360(center) }
}

function fmtTime(d) {
  if (!(d instanceof Date) || Number.isNaN(d.getTime())) return '-'
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function fmtDuration(totalMinutes) {
  const min = Math.max(0, Math.round(Number(totalMinutes) || 0))
  const h = Math.floor(min / 60)
  const m = min % 60
  if (h <= 0) return `${m} min`
  if (m <= 0) return `${h}h`
  return `${h}h ${m}m`
}

function fmtDeltaDuration(totalMinutes) {
  const raw = Math.round(Number(totalMinutes) || 0)
  const sign = raw > 0 ? '+' : raw < 0 ? '-' : ''
  return `${sign}${fmtDuration(Math.abs(raw))}`
}

function heatColor(score) {
  const s = Math.max(0, Math.min(100, Number(score) || 0))
  if (s <= 0) return 'linear-gradient(180deg,#172033,#0b1220)'
  if (s < 25) return 'linear-gradient(180deg,#164e63,#083344)'
  if (s < 50) return 'linear-gradient(180deg,#ca8a04,#713f12)'
  if (s < 75) return 'linear-gradient(180deg,#f97316,#9a3412)'
  return 'linear-gradient(180deg,#ef4444,#7f1d1d)'
}

function buildSunWindowHeatmap(shadeArg = null) {
  const empty = {
    slots: [],
    subtitle: '',
    usefulLabel: '0 min',
    usefulMinutes: 0,
    peakLabel: '-',
    nextLabel: '-',
    startLabel: '-',
    endLabel: '-',
  }
  const shade = shadeArg || selectedShadeEdit.value
  if (!shade || lat.value == null || lon.value == null) return empty
  const base = data.value?.timestamp_local ? new Date(data.value.timestamp_local) : new Date()
  const times = SunCalc.getTimes(base, lat.value, lon.value)
  const sunrise = data.value?.sun_times?.sunrise ? new Date(data.value.sun_times.sunrise) : times.sunrise
  const sunset = data.value?.sun_times?.sunset ? new Date(data.value.sun_times.sunset) : times.sunset
  if (!(sunrise instanceof Date) || !(sunset instanceof Date) || Number.isNaN(sunrise.getTime()) || Number.isNaN(sunset.getTime()) || sunset <= sunrise) return empty

  const sector = shadeSunSector(shade)
  const altMin = Number.isFinite(Number(shade.altitude_min_deg)) ? Number(shade.altitude_min_deg) : -10
  const altMax = Number.isFinite(Number(shade.altitude_max_deg)) ? Number(shade.altitude_max_deg) : 90
  const low = Math.min(altMin, altMax)
  const high = Math.max(altMin, altMax)
  const invert = Boolean(shade.invert_sun_logic)
  const now = new Date()
  const stepMin = 10
  const slots = []
  let usefulMinutes = 0
  let peak = null
  let next = null
  for (let t = sunrise.getTime(); t <= sunset.getTime(); t += stepMin * 60000) {
    const dt = new Date(t)
    const pos = SunCalc.getPosition(dt, lat.value, lon.value)
    const az = suncalcAzToCompassDeg(pos.azimuth)
    const alt = toDeg(pos.altitude)
    const inAz = isAzimuthInRange(az, sector.start, sector.end)
    const inAlt = alt >= low && alt <= high
    const rawActive = inAz && inAlt
    const active = invert ? !rawActive : rawActive
    const centerFactor = Math.max(0, 1 - angleDeltaDeg(az, sector.center) / 90)
    const altFactor = Math.max(0, Math.min(1, (alt - low) / Math.max(1, high - low)))
    const score = active ? Math.round(30 + (altFactor * 45) + (centerFactor * 25)) : 0
    if (score > 0) usefulMinutes += stepMin
    if (!peak || score > peak.score) peak = { score, time: dt }
    if (score > 0 && !next && dt >= now) next = dt
    slots.push({
      key: `${dt.getHours()}-${dt.getMinutes()}`,
      score,
      color: heatColor(score),
      isNow: Math.abs(dt.getTime() - now.getTime()) < stepMin * 60000,
      title: `${fmtTime(dt)} - Az ${az.toFixed(1)} deg - Elev ${alt.toFixed(1)} deg - utile ${score}%${invert ? ' - logica invertita' : ''}`,
    })
  }
  return {
    slots,
    subtitle: `${fmtTime(sunrise)} - ${fmtTime(sunset)} | ${invert ? 'logica sole invertita' : 'logica sole diretta'}`,
    usefulLabel: `Sole utile ${fmtDuration(usefulMinutes)}`,
    usefulMinutes,
    peakLabel: peak && peak.score > 0 ? `${fmtTime(peak.time)} (${peak.score}%)` : '-',
    nextLabel: next ? fmtTime(next) : '-',
    startLabel: fmtTime(sunrise),
    endLabel: fmtTime(sunset),
  }
}

function simulationShadeFromRaw(shade) {
  if (!shade) return null
  return {
    use_start_stop_azimuth: Boolean(pickSetting(shade, 'use_start_stop_azimuth', true)),
    invert_sun_logic: Boolean(pickSetting(shade, 'invert_sun_logic', false)),
    window_azimuth: Number(pickSetting(shade, 'window_azimuth', 0)),
    azimuth_start_deg: Number(pickSetting(shade, 'azimuth_start_deg', shade.azimuth_start_deg ?? 0)),
    azimuth_end_deg: Number(pickSetting(shade, 'azimuth_end_deg', shade.azimuth_end_deg ?? 0)),
    fov_left: Number(pickSetting(shade, 'fov_left', 70)),
    fov_right: Number(pickSetting(shade, 'fov_right', 70)),
    altitude_min_deg: Number(pickSetting(shade, 'altitude_min_deg', shade.altitude_min_deg ?? 8)),
    altitude_max_deg: Number(pickSetting(shade, 'altitude_max_deg', shade.altitude_max_deg ?? 80)),
    default_position: Number(pickSetting(shade, 'default_position', 100)),
    min_position: Number(pickSetting(shade, 'min_position', 0)),
    thermal_enabled: Boolean(pickSetting(shade, 'thermal_enabled', false)),
    thermal_climate_entity: String(pickSetting(shade, 'thermal_climate_entity', '') || ''),
  }
}

function simulationSummary(shade) {
  const hm = buildSunWindowHeatmap(shade)
  return {
    usefulLabel: hm.usefulLabel || 'Sole utile 0 min',
    usefulMinutes: Number(hm.usefulMinutes || 0),
    peakLabel: hm.peakLabel || '-',
    sunPosition: Number(shade?.min_position ?? 0),
    defaultPosition: Number(shade?.default_position ?? 100),
    sunPositionLabel: `${targetValue(shade?.min_position)} %`,
    defaultPositionLabel: `${targetValue(shade?.default_position)} %`,
    thermalEnabled: Boolean(shade?.thermal_enabled),
    thermalLabel: shade?.thermal_enabled ? `ON ${shade?.thermal_climate_entity || '(climate mancante)'}` : 'OFF',
  }
}

function buildWhatIfPreview() {
  const currentRaw = tendeMapShades.value.find((s) => shadeKey(s) === selectedShadeId.value || String(s.id || '').trim() === String(selectedShadeId.value || '').trim())
  const currentShade = simulationShadeFromRaw(currentRaw) || simulationShadeFromRaw(selectedShadeEdit.value)
  const proposedShade = selectedShadeEdit.value || currentShade || {}
  const current = simulationSummary(currentShade || {})
  const proposed = simulationSummary(proposedShade || {})
  const deltaMin = proposed.usefulMinutes - current.usefulMinutes
  const deltaSun = proposed.sunPosition - current.sunPosition
  const deltaDefault = proposed.defaultPosition - current.defaultPosition
  const sign = (n) => (n > 0 ? '+' : '')
  return {
    current,
    proposed,
    deltaUsefulLabel: `Sole utile: ${fmtDeltaDuration(deltaMin)}`,
    deltaSunPositionLabel: `Posizione sole: ${sign(deltaSun)}${deltaSun} %`,
    deltaDefaultPositionLabel: `Riposo: ${sign(deltaDefault)}${deltaDefault} %`,
    thermalDeltaLabel: current.thermalEnabled === proposed.thermalEnabled ? 'Termico: invariato' : `Termico: ${current.thermalEnabled ? 'ON' : 'OFF'} -> ${proposed.thermalEnabled ? 'ON' : 'OFF'}`,
  }
}

function unwrapAzimuthSeries(arr) {
  const out = []
  let prev = null
  for (const a0 of arr) {
    let a = Number(a0)
    if (!Number.isFinite(a)) continue
    if (prev == null) {
      out.push(a)
      prev = a
      continue
    }
    while ((a - prev) > 180) a -= 360
    while ((a - prev) < -180) a += 360
    out.push(a)
    prev = a
  }
  return out
}

function buildAzAltSamplesForDate(baseDate, steps = 240) {
  const times = SunCalc.getTimes(baseDate, lat.value, lon.value)
  const sunrise = times?.sunrise instanceof Date ? times.sunrise : baseDateAtHour(6)
  const sunset = times?.sunset instanceof Date ? times.sunset : baseDateAtHour(20)
  const sMs = sunrise.getTime()
  const eMs = sunset.getTime()
  const total = Math.max(1, eMs - sMs)
  const azRaw = []
  const alt = []
  for (let i = 0; i <= steps; i += 1) {
    const t = sMs + (total * i) / steps
    const p = SunCalc.getPosition(new Date(t), lat.value, lon.value)
    azRaw.push(suncalcAzToCompassDeg(p.azimuth))
    alt.push(Math.max(0, toDeg(p.altitude)))
  }
  const azUnwrapped = unwrapAzimuthSeries(azRaw)
  return azUnwrapped.map((a, i) => ({ az: a, alt: alt[i] ?? 0 }))
}

function interpAltByAz(samples, azTarget) {
  if (!Array.isArray(samples) || samples.length < 2) return 0
  for (let i = 0; i < samples.length - 1; i += 1) {
    const a0 = samples[i].az
    const a1 = samples[i + 1].az
    if ((azTarget >= a0 && azTarget <= a1) || (azTarget <= a0 && azTarget >= a1)) {
      const den = (a1 - a0)
      const t = Math.abs(den) < 1e-9 ? 0 : (azTarget - a0) / den
      return (samples[i].alt || 0) + ((samples[i + 1].alt || 0) - (samples[i].alt || 0)) * t
    }
  }
  if (azTarget < samples[0].az) return samples[0].alt || 0
  return samples[samples.length - 1].alt || 0
}

function drawSolarOverlay() {
  if (!map || lat.value == null || lon.value == null) return
  ;[centerMarker, pathLine, horizonCircle, sunLine, sunMarker, sunLineLive, sunMarkerLive, sunriseRay, sunsetRay, sunriseLabel, sunsetLabel, altitudeRing, altitudeGuideLine, altitudeGuideLabel, axisNS, axisWE, pvAzLine, pvAzMarker, annualElevationBand].forEach((l) => { if (l) map.removeLayer(l) })
  for (const l of annualElevationBandLayers) map.removeLayer(l)
  annualElevationBandLayers = []
  for (const m of compassMarkers) map.removeLayer(m)
  for (const l of tendeSectorLayers) map.removeLayer(l)
  compassMarkers = []
  tendeSectorLayers = []

  centerMarker = L.circleMarker([lat.value, lon.value], { radius: 4, color: '#ffd24a', fillColor: '#ffd24a', fillOpacity: 1, weight: 1 }).addTo(map)

  // Horizon ring (SunCalc-like base circle)
  horizonCircle = L.circle([lat.value, lon.value], {
    radius: cfg.value.sectorRadiusM,
    color: '#7f8a95',
    weight: 1.2,
    opacity: 0.78,
    fillOpacity: 0,
  }).addTo(map)

  if (showAxisNS.value) {
    const nPt = destinationPoint(lat.value, lon.value, 0, cfg.value.sectorRadiusM)
    const sPt = destinationPoint(lat.value, lon.value, 180, cfg.value.sectorRadiusM)
    axisNS = L.polyline([nPt, sPt], {
      color: '#8ea1b5',
      weight: 1.6,
      opacity: 0.75,
      dashArray: '6,6',
    }).addTo(map)
  }
  if (showAxisWE.value) {
    const ePt = destinationPoint(lat.value, lon.value, 90, cfg.value.sectorRadiusM)
    const wPt = destinationPoint(lat.value, lon.value, 270, cfg.value.sectorRadiusM)
    axisWE = L.polyline([wPt, ePt], {
      color: '#8ea1b5',
      weight: 1.6,
      opacity: 0.75,
      dashArray: '6,6',
    }).addTo(map)
  }

  if (showPvAzLine.value) {
    const bearing = (Number(pvAzimuthDeg.value) + 180 + 360) % 360
    const pvPt = destinationPoint(lat.value, lon.value, bearing, cfg.value.sectorRadiusM)
    pvAzLine = L.polyline([[lat.value, lon.value], pvPt], {
      color: '#ff6a00',
      weight: 4,
      opacity: 0.95,
      lineCap: 'round',
    }).addTo(map)
    pvAzMarker = L.marker(pvPt, {
      icon: L.divIcon({
        className: 'fv-icon-wrap',
        html: '<span class="fv-icon">FV</span>',
        iconSize: [28, 20],
        iconAnchor: [14, 10],
      }),
      interactive: false,
    }).addTo(map)
  }

  // Real daily path (projected by azimuth+altitude)
  pathLine = L.polyline(buildSunPathPoints(), {
    color: '#f2c235',
    weight: 3.2,
    opacity: 0.95,
    lineCap: 'round',
    lineJoin: 'round',
  }).addTo(map)

  const dt = baseDateAtHour(selectedTime.value.h, selectedTime.value.m)
  const sunrise = data.value?.sun_times?.sunrise ? new Date(data.value.sun_times.sunrise) : baseDateAtHour(6)
  const sunset = data.value?.sun_times?.sunset ? new Date(data.value.sun_times.sunset) : baseDateAtHour(20)
  const srPos = SunCalc.getPosition(sunrise, lat.value, lon.value)
  const ssPos = SunCalc.getPosition(sunset, lat.value, lon.value)
  const srAz = suncalcAzToCompassDeg(srPos.azimuth)
  const ssAz = suncalcAzToCompassDeg(ssPos.azimuth)

  if (showAnnualElevationBand.value) {
    const year = (data.value?.timestamp_local ? new Date(data.value.timestamp_local) : new Date()).getFullYear()
    const summerDay = new Date(year, 5, 21, 12, 0, 0) // 21 Jun
    const winterDay = new Date(year, 11, 21, 12, 0, 0) // 21 Dec
    const summerSamples = buildAzAltSamplesForDate(summerDay, 280)
    const winterSamples = buildAzAltSamplesForDate(winterDay, 280)
    if (summerSamples.length > 3 && winterSamples.length > 3) {
      let start = norm360(srAz)
      let end = norm360(ssAz)
      if (end < start) end += 360
      const steps = 160
      const winterCurve = []
      const summerCurve = []
      for (let i = 0; i <= steps; i += 1) {
        const azU = start + ((end - start) * i) / steps
        const altW = interpAltByAz(winterSamples, azU)
        const altS = interpAltByAz(summerSamples, azU)
        const azN = norm360(azU)
        winterCurve.push(destinationPoint(lat.value, lon.value, azN, altitudeToRadius(altW)))
        summerCurve.push(destinationPoint(lat.value, lon.value, azN, altitudeToRadius(altS)))
      }
      for (let i = 0; i < steps; i += 1) {
        const q = L.polygon([winterCurve[i], winterCurve[i + 1], summerCurve[i + 1], summerCurve[i]], {
          color: '#facc15',
          weight: 0,
          opacity: 0,
          fillColor: '#facc15',
          fillOpacity: 0.16,
        }).addTo(map)
        annualElevationBandLayers.push(q)
      }
      annualElevationBand = L.polyline(winterCurve, {
        color: '#facc15',
        weight: 0.8,
        opacity: 0.32,
        dashArray: '4,6',
      }).addTo(map)
      const annualElevationBandTop = L.polyline(summerCurve, {
        color: '#facc15',
        weight: 0.8,
        opacity: 0.32,
        dashArray: '4,6',
      }).addTo(map)
      annualElevationBandLayers.push(annualElevationBandTop)
    }
  }

  const pos = SunCalc.getPosition(dt, lat.value, lon.value)
  const az = suncalcAzToCompassDeg(pos.azimuth)
  const alt = toDeg(pos.altitude)
  currentSun.value = { azimuthDeg: az, altitudeDeg: alt }
  const simRadius = altitudeToRadius(alt)
  const sunPt = destinationPoint(lat.value, lon.value, az, simRadius)
  // Real elevation curve from sunrise to sunset (time-sampled), instead of concentric ring.
  altitudeRing = L.polyline(buildElevationCurvePoints(sunrise, sunset, 96), {
    color: '#fff1a8',
    weight: 3.4,
    opacity: 0.98,
    dashArray: '8,5',
    lineCap: 'round',
    lineJoin: 'round',
  }).addTo(map)

  const horizonPtSameAz = destinationPoint(lat.value, lon.value, az, cfg.value.sectorRadiusM)
  const srPt = destinationPoint(lat.value, lon.value, srAz, cfg.value.sectorRadiusM)
  const ssPt = destinationPoint(lat.value, lon.value, ssAz, cfg.value.sectorRadiusM)
  sunriseRay = L.polyline([[lat.value, lon.value], srPt], { color: '#f97316', weight: 3.2, opacity: 0.95 }).addTo(map)
  sunsetRay = L.polyline([[lat.value, lon.value], ssPt], { color: '#facc15', weight: 3.2, opacity: 0.95 }).addTo(map)
  const srLblPt = destinationPoint(lat.value, lon.value, srAz, cfg.value.sectorRadiusM + 10)
  const ssLblPt = destinationPoint(lat.value, lon.value, ssAz, cfg.value.sectorRadiusM + 10)
  if (showSunRefs.value) {
    sunriseLabel = L.marker(srLblPt, {
      icon: L.divIcon({
        className: 'sun-ref-label-wrap',
        html: '<span class="sun-ref-label sunrise">Alba</span>',
        iconSize: [52, 18],
        iconAnchor: [26, 9],
      }),
      interactive: false,
    }).addTo(map)
    sunsetLabel = L.marker(ssLblPt, {
      icon: L.divIcon({
        className: 'sun-ref-label-wrap',
        html: '<span class="sun-ref-label sunset">Tramonto</span>',
        iconSize: [72, 18],
        iconAnchor: [36, 9],
      }),
      interactive: false,
    }).addTo(map)
  }

  if (showSimLine.value) {
    // Azimuth line (center -> horizon)
    sunLine = L.polyline([[lat.value, lon.value], horizonPtSameAz], {
      color: '#d86a2a',
      weight: 2.2,
      opacity: 0.85,
      lineCap: 'round',
      dashArray: '7,5',
    }).addTo(map)
    // Elevation segment (horizon -> current sun point)
    altitudeGuideLine = L.polyline([horizonPtSameAz, sunPt], {
      color: '#f8f8f8',
      weight: 3.4,
      opacity: 0.98,
      lineCap: 'round',
    }).addTo(map)
    sunMarker = L.marker(sunPt, {
      icon: L.divIcon({
        className: 'sun-icon-wrap',
        html: `<span class="sun-icon" style="transform:scale(${(0.9 + Math.max(0, Math.min(alt, 90)) / 180).toFixed(2)})"></span>`,
        iconSize: [26, 26],
        iconAnchor: [13, 13],
      }),
      interactive: false,
    }).addTo(map)
    const mid = destinationPoint(lat.value, lon.value, az, (simRadius + cfg.value.sectorRadiusM) / 2)
    altitudeGuideLabel = L.marker(mid, {
      icon: L.divIcon({
        className: 'altitude-label-wrap',
        html: `<span class="altitude-label">Elev ${fmt(Math.max(0, alt))}°</span>`,
        iconSize: [86, 18],
        iconAnchor: [43, 9],
      }),
      interactive: false,
    }).addTo(map)
  }

  if (showLiveLine.value) {
      const liveAz = Number(data.value?.sun_position?.azimuth_compass_deg)
      const liveAlt = Number(data.value?.sun_position?.altitude_deg)
      if (Number.isFinite(liveAz)) {
      const liveRadius = Number.isFinite(liveAlt) ? altitudeToRadius(liveAlt) : cfg.value.sectorRadiusM
      const livePt = destinationPoint(lat.value, lon.value, liveAz, liveRadius)
      sunLineLive = L.polyline([[lat.value, lon.value], livePt], {
        color: '#2dd4bf',
        weight: 2.6,
        opacity: 0.95,
        dashArray: '8,6',
        lineCap: 'round',
      }).addTo(map)
      sunMarkerLive = L.circleMarker(livePt, { radius: 6, color: '#2dd4bf', fillColor: '#2dd4bf', fillOpacity: 1, weight: 2 }).addTo(map)
    }
  }

  const card = [
    { t: 'N', b: 0 },
    { t: 'E', b: 90 },
    { t: 'S', b: 180 },
    { t: 'W', b: 270 },
  ]
  for (const c of card) {
    const pt = destinationPoint(lat.value, lon.value, c.b, cfg.value.sectorRadiusM + 6)
    const mk = L.marker(pt, {
      icon: L.divIcon({
        className: 'cardinal',
        html: `<span>${c.t}</span>`,
        iconSize: [18, 18],
        iconAnchor: [9, 9],
      }),
      interactive: false,
    }).addTo(map)
    compassMarkers.push(mk)
  }

  if (showTendeSectors.value) {
    const stale = Boolean(tendeMap.value?.stale) || (tendeMap.value?.availability && tendeMap.value?.availability !== 'online')
    const shades = tendeMapShades.value
    shades.forEach((shade, idx) => {
      const azStart = Number(shade.azimuth_start_deg)
      const azEnd = Number(shade.azimuth_end_deg)
      if (!Number.isFinite(azStart) || !Number.isFinite(azEnd)) return
      const altMin = Number(shade.altitude_min_deg)
      const altMax = Number(shade.altitude_max_deg)
      const hasAltBand = Number.isFinite(altMin) && Number.isFinite(altMax)
      const rOuter = hasAltBand ? altitudeToRadius(Math.min(altMin, altMax)) : cfg.value.sectorRadiusM
      const rInner = hasAltBand ? altitudeToRadius(Math.max(altMin, altMax)) : 0
      const color = String(shade.color || colorFromIndex(idx))
      const active = Boolean(shade.active)
      const opacity = stale ? 0.14 : (active ? 0.34 : 0.2)
      const points = hasAltBand
        ? buildSectorBandPolygonPoints(azStart, azEnd, rOuter, rInner)
        : buildSectorPolygonPoints(azStart, azEnd, cfg.value.sectorRadiusM)
      const poly = L.polygon(points, {
        color,
        weight: active ? 2.4 : 1.4,
        opacity: stale ? 0.5 : 0.9,
        fillColor: color,
        fillOpacity: opacity,
      }).addTo(map)
      const tip = `${shade.name || shade.id}<br>${shade.cover_entity || ''}<br>Az: ${fmt(azStart)}° -> ${fmt(azEnd)}°<br>Active: ${active ? 'yes' : 'no'}`
      poly.bindTooltip(tip)
      tendeSectorLayers.push(poly)
    })
  }
}

function applyMapView() {
  if (map && lat.value != null && lon.value != null) map.setView([lat.value, lon.value], cfg.value.mapZoom)
  drawSolarOverlay()
}

function coverStateLabel(entityId) {
  const st = tendeCoverStates.value?.[entityId]
  if (!st) return '-'
  if (st.error) return `errore (${st.error})`
  return st.state || '-'
}

function pickSetting(shade, key, fallback = null) {
  const st = shade?.settings || {}
  if (st[key] !== undefined && st[key] !== null) return st[key]
  return fallback
}

function activeMainMapId() {
  if (tab.value === 'user_public') return 'solar-map-public'
  if (tab.value === 'user') return 'solar-map'
  return null
}

function findMapContainerById(id) {
  return document.getElementById(id) || document.querySelector(`[data-map-container="${id}"]`)
}

async function waitForMapEl({ id = null, maxTry = MAP_INIT_MAX_RETRIES, delay = MAP_INIT_RETRY_MS } = {}) {
  for (let i = 0; i < maxTry; i += 1) {
    const scoped = id ? document.getElementById(id) || document.querySelector(`[data-map-container="${id}"]`) : null
    const generic = document.getElementById('map') || document.querySelector(MAP_CONTAINER_SELECTOR)
    const el = scoped || generic
    if (el) return el
    await new Promise((resolve) => setTimeout(resolve, delay))
  }
  return null
}

function clearMainMapRetry() {
  if (!mapInitRetryTimer) return
  clearTimeout(mapInitRetryTimer)
  mapInitRetryTimer = 0
}

function scheduleMainMapRetry(reason = 'container_missing') {
  if (mapInitAttempts >= MAP_INIT_MAX_RETRIES) {
    console.warn(`[e-SunMind] map init skipped after ${MAP_INIT_MAX_RETRIES} retries (${reason})`)
    return
  }
  clearMainMapRetry()
  mapInitAttempts += 1
  mapInitRetryTimer = setTimeout(async () => {
    mapInitRetryTimer = 0
    await ensureMainMapReady('retry')
  }, MAP_INIT_RETRY_MS)
}

async function ensureMainMapReady(source = 'unknown', opts = {}) {
  const retryOnMissing = opts.retryOnMissing !== false
  if (!Number.isFinite(lat.value) || !Number.isFinite(lon.value)) return false
  const targetId = activeMainMapId()
  if (!targetId) return false
  await nextTick()
  const el = await waitForMapEl({ id: targetId })
  if (!el) {
    console.warn(`[e-SunMind] main map container not found (${targetId}) from ${source}`)
    if (retryOnMissing) scheduleMainMapRetry(`no_dom_${targetId}_${source}`)
    return false
  }
  const currentId = map && map.getContainer ? (map.getContainer()?.id || '') : ''
  if (map && currentId !== targetId) {
    try {
      const oldEl = map.getContainer?.()
      if (oldEl?.dataset) oldEl.dataset.mapInit = '0'
      map.remove()
    } catch (_) {}
    map = null
  }
  if (!map) {
    if (el.dataset.mapInit === '1') {
      if (retryOnMissing) scheduleMainMapRetry(`init_in_progress_${targetId}_${source}`)
      return false
    }
    el.dataset.mapInit = '1'
    try {
      map = L.map(el, { zoomControl: true }).setView([lat.value, lon.value], cfg.value.mapZoom)
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles (C) Esri',
        maxZoom: 20,
      }).addTo(map)
    } catch (e) {
      el.dataset.mapInit = '0'
      map = null
      console.warn('[e-SunMind] map bootstrap deferred:', e?.message || e)
      if (retryOnMissing) scheduleMainMapRetry(`leaflet_init_failed_${targetId}_${source}`)
      return false
    }
  }
  clearMainMapRetry()
  mapInitAttempts = 0
  try { map.invalidateSize() } catch (_) {}
  map.setView([lat.value, lon.value], cfg.value.mapZoom)
  drawSolarOverlay()
  return true
}

function shadeKey(shade) {
  return String(shade?.id || shade?.cover_entity || shade?.name || '').trim()
}

function mergeTendeShades(previous, incoming) {
  const merged = new Map()
  for (const shade of Array.isArray(previous) ? previous : []) {
    const key = shadeKey(shade)
    if (key) merged.set(key, shade)
  }

  ensureWindDirectionLayer()
  for (const shade of Array.isArray(incoming) ? incoming : []) {
    const key = shadeKey(shade)
    if (!key) continue
    merged.set(key, { ...(merged.get(key) || {}), ...shade })
  }
  return Array.from(merged.values())
}

function ensureWindDirectionLayer() {
  if (windLayerRetryTimer) {
    clearTimeout(windLayerRetryTimer)
    windLayerRetryTimer = 0
  }
  if (windDirLine && map) {
    try {
      const head = (windDirLine)._windDirHead
      if (head) map.removeLayer(head)
    } catch (_) {}
    try { map.removeLayer(windDirLine) } catch (_) {}
  }
  if (windDirMarker && map) {
    try { map.removeLayer(windDirMarker) } catch (_) {}
  }
  windDirLine = null
  windDirMarker = null
  if (!showWindDirectionOnMap.value) return
  if (!map || lat.value == null || lon.value == null) {
    windLayerRetryTimer = setTimeout(() => ensureWindDirectionLayer(), 150)
    return
  }
  const dirRaw = Number.isFinite(Number(mapWindDirDeg.value)) ? Number(mapWindDirDeg.value) : Number(lastKnownWindDirDeg.value)
  if (!Number.isFinite(dirRaw)) {
    windLayerRetryTimer = setTimeout(() => ensureWindDirectionLayer(), 500)
    return
  }
  const dir = ((Number(dirRaw) % 360) + 360) % 360
  lastKnownWindDirDeg.value = dir
  const speedRaw = Number.isFinite(Number(mapWindMs.value)) ? Number(mapWindMs.value) : Number(lastKnownWindMs.value)
  if (Number.isFinite(speedRaw)) lastKnownWindMs.value = Number(speedRaw)
  const windPt = destinationPoint(lat.value, lon.value, dir, cfg.value.sectorRadiusM * 0.92)
  const headPt = destinationPoint(lat.value, lon.value, dir, cfg.value.sectorRadiusM * 0.98)
  windDirLine = L.polyline([[lat.value, lon.value], windPt], {
    color: '#36d5ff',
    weight: 2.8,
    opacity: 0.95,
    dashArray: '5,5',
    lineCap: 'round',
  }).addTo(map)
  const dirMarker = L.circleMarker(headPt, {
    radius: 3.5,
    color: '#c8f3ff',
    fillColor: '#36d5ff',
    fillOpacity: 1,
    weight: 1.6,
  }).addTo(map)
  windDirMarker = L.marker(windPt, {
    icon: L.divIcon({
      className: 'wind-map-icon-wrap',
      html: `<span class="wind-map-label">VENTO DA ${fmt(dir)}° · ${fmt(lastKnownWindMs.value)} m/s</span>`,
      iconSize: [170, 20],
      iconAnchor: [0, 10],
    }),
    interactive: false,
  }).addTo(map)
  ;(windDirLine)._windDirHead = dirMarker
}

function selectShade(id) {
  selectedShadeId.value = id
  const shade = tendeMapShades.value.find((s) => shadeKey(s) === id || String(s.id || '').trim() === String(id || '').trim())
  if (!shade) return
  selectedShadeEdit.value = {
    id: shade.id,
    name: shade.name,
    cover_entity: shade.cover_entity,
    enabled: Boolean(pickSetting(shade, 'enabled', shade.enabled)),
    sun_logic_enabled: Boolean(pickSetting(shade, 'sun_logic_enabled', true)),
    invert_sun_logic: Boolean(pickSetting(shade, 'invert_sun_logic', false)),
    open_when_no_sun: Boolean(pickSetting(shade, 'open_when_no_sun', true)),
    use_start_stop_azimuth: Boolean(pickSetting(shade, 'use_start_stop_azimuth', true)),
    command_mode_open_close: String(pickSetting(shade, 'command_mode', 'open_close')) === 'open_close',
    window_azimuth: Number(pickSetting(shade, 'window_azimuth', 0)),
    facade_azimuth_deg: Number(pickSetting(shade, 'facade_azimuth_deg', pickSetting(shade, 'window_azimuth', 0))),
    azimuth_start_deg: Number.isFinite(Number(pickSetting(shade, 'azimuth_start_deg', shade.azimuth_start_deg))) ? Number(pickSetting(shade, 'azimuth_start_deg', shade.azimuth_start_deg)) : 0,
    azimuth_end_deg: Number.isFinite(Number(pickSetting(shade, 'azimuth_end_deg', shade.azimuth_end_deg))) ? Number(pickSetting(shade, 'azimuth_end_deg', shade.azimuth_end_deg)) : 0,
    fov_left: Number(pickSetting(shade, 'fov_left', 70)),
    fov_right: Number(pickSetting(shade, 'fov_right', 70)),
    altitude_min_deg: Number(pickSetting(shade, 'altitude_min_deg', shade.altitude_min_deg ?? 8)),
    altitude_max_deg: Number(pickSetting(shade, 'altitude_max_deg', shade.altitude_max_deg ?? 80)),
    default_position: Number(pickSetting(shade, 'default_position', 100)),
    sunset_position: Number(pickSetting(shade, 'sunset_position', 0)),
    min_position: Number(pickSetting(shade, 'min_position', 0)),
    max_position: Number(pickSetting(shade, 'max_position', 100)),
    min_delta: Number(pickSetting(shade, 'min_delta', 3)),
    interval_minutes: Number(pickSetting(shade, 'interval_minutes', 5)),
    min_command_interval_seconds: Number(pickSetting(shade, 'min_command_interval_seconds', 120)),
    thermal_enabled: Boolean(pickSetting(shade, 'thermal_enabled', false)),
    thermal_climate_entity: String(pickSetting(shade, 'thermal_climate_entity', '') || ''),
    thermal_hysteresis: Number(pickSetting(shade, 'thermal_hysteresis', 0.5)),
    thermal_heat_gain_position: Number(pickSetting(shade, 'thermal_heat_gain_position', pickSetting(shade, 'default_position', 100))),
    thermal_cool_block_position: Number(pickSetting(shade, 'thermal_cool_block_position', pickSetting(shade, 'min_position', 0))),
    open_close_threshold: Number(pickSetting(shade, 'open_close_threshold', 50)),
    sun_probe_threshold: Number(pickSetting(shade, 'sun_probe_threshold', 300)),
    weather_guard_enabled: Boolean(pickSetting(shade, 'weather_guard_enabled', false)),
    protect_on_wind_alarm: Boolean(pickSetting(shade, 'protect_on_wind_alarm', true)),
    protect_on_rain_alarm: Boolean(pickSetting(shade, 'protect_on_rain_alarm', true)),
    protect_on_facade_rain_risk: Boolean(pickSetting(shade, 'protect_on_facade_rain_risk', true)),
    weather_safe_position: Number(pickSetting(shade, 'weather_safe_position', 100)),
    weather_wind_safe_position: Number(pickSetting(shade, 'weather_wind_safe_position', pickSetting(shade, 'weather_safe_position', 100))),
    weather_rain_safe_position: Number(pickSetting(shade, 'weather_rain_safe_position', pickSetting(shade, 'weather_safe_position', 100))),
    weather_facade_rain_safe_position: Number(pickSetting(shade, 'weather_facade_rain_safe_position', pickSetting(shade, 'weather_safe_position', 100))),
    sensors: shade.sensors || {},
  }
  drawTendeEditor()
}

function angleFromCenter(latlng) {
  const dx = latlng.lng - lon.value
  const dy = latlng.lat - lat.value
  const raw = (Math.atan2(dx, dy) * 180 / Math.PI + 360) % 360
  return raw
}

function ensureTendeMap() {
  if (tendeMapObj || lat.value == null || lon.value == null) return
  waitForMapEl({ id: 'tende-map' }).then((el) => {
    if (!el) {
      console.warn('[e-SunMind] tende map container not found; skip init')
      return
    }
    if (el.dataset.mapInit === '1') return
    el.dataset.mapInit = '1'
    try {
      tendeMapObj = L.map(el, { zoomControl: true, attributionControl: true }).setView([lat.value, lon.value], cfg.value.mapZoom)
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles (C) Esri',
        maxZoom: 20,
      }).addTo(tendeMapObj)
    } catch (e) {
      el.dataset.mapInit = '0'
      tendeMapObj = null
      console.warn('[e-SunMind] tende map init deferred:', e?.message || e)
    }
  }).catch((e) => {
    console.warn('[e-SunMind] tende map wait aborted:', e?.message || e)
  })
}

function drawTendeEditor() {
  if (!tendeMapObj || !selectedShadeEdit.value || lat.value == null || lon.value == null) return
  ;[tendeCenter, tendeRing, tendePoly, tendeStartMarker, tendeEndMarker].forEach((l) => { if (l) tendeMapObj.removeLayer(l) })
  for (const l of tendeEditorExtraLayers) tendeMapObj.removeLayer(l)
  tendeEditorExtraLayers = []
  const s = selectedShadeEdit.value
  const color = colorFromIndex(tendeMapShades.value.findIndex((x) => x.id === s.id))
  tendeCenter = L.circleMarker([lat.value, lon.value], { radius: 4, color: '#ffd24a', fillColor: '#ffd24a', fillOpacity: 1 }).addTo(tendeMapObj)
  tendeRing = L.circle([lat.value, lon.value], { radius: cfg.value.sectorRadiusM, color: '#7f8a95', weight: 1.2, fillOpacity: 0 }).addTo(tendeMapObj)
  const sunrise = data.value?.sun_times?.sunrise ? new Date(data.value.sun_times.sunrise) : baseDateAtHour(6)
  const sunset = data.value?.sun_times?.sunset ? new Date(data.value.sun_times.sunset) : baseDateAtHour(20)
  const srAz = suncalcAzToCompassDeg(SunCalc.getPosition(sunrise, lat.value, lon.value).azimuth)
  const ssAz = suncalcAzToCompassDeg(SunCalc.getPosition(sunset, lat.value, lon.value).azimuth)
  const srPt = destinationPoint(lat.value, lon.value, srAz, cfg.value.sectorRadiusM)
  const ssPt = destinationPoint(lat.value, lon.value, ssAz, cfg.value.sectorRadiusM)
  tendeEditorExtraLayers.push(L.polyline([[lat.value, lon.value], srPt], { color: '#f97316', weight: 2.4, opacity: 0.95 }).addTo(tendeMapObj))
  tendeEditorExtraLayers.push(L.polyline([[lat.value, lon.value], ssPt], { color: '#facc15', weight: 2.4, opacity: 0.95 }).addTo(tendeMapObj))
  tendeEditorExtraLayers.push(L.polyline(buildElevationCurvePoints(sunrise, sunset, 96), { color: '#fff1a8', weight: 2.6, opacity: 0.9, dashArray: '8,5' }).addTo(tendeMapObj))
  tendeEditorExtraLayers.push(L.marker(destinationPoint(lat.value, lon.value, srAz, cfg.value.sectorRadiusM + 10), { icon: L.divIcon({ className: 'sun-ref-label-wrap', html: '<span class="sun-ref-label sunrise">Alba</span>', iconSize: [52, 18], iconAnchor: [26, 9] }), interactive: false }).addTo(tendeMapObj))
  tendeEditorExtraLayers.push(L.marker(destinationPoint(lat.value, lon.value, ssAz, cfg.value.sectorRadiusM + 10), { icon: L.divIcon({ className: 'sun-ref-label-wrap', html: '<span class="sun-ref-label sunset">Tramonto</span>', iconSize: [72, 18], iconAnchor: [36, 9] }), interactive: false }).addTo(tendeMapObj))
  const hasAltBand = Number.isFinite(Number(s.altitude_min_deg)) && Number.isFinite(Number(s.altitude_max_deg))
  const rOuter = hasAltBand ? altitudeToRadius(Math.min(Number(s.altitude_min_deg), Number(s.altitude_max_deg))) : cfg.value.sectorRadiusM
  const rInner = hasAltBand ? altitudeToRadius(Math.max(Number(s.altitude_min_deg), Number(s.altitude_max_deg))) : 0
  const pts = hasAltBand ? buildSectorBandPolygonPoints(s.azimuth_start_deg, s.azimuth_end_deg, rOuter, rInner) : buildSectorPolygonPoints(s.azimuth_start_deg, s.azimuth_end_deg, cfg.value.sectorRadiusM)
  tendePoly = L.polygon(pts, { color, weight: 2.6, fillColor: color, fillOpacity: 0.3 }).addTo(tendeMapObj)
  const windowPt = destinationPoint(lat.value, lon.value, s.window_azimuth, cfg.value.sectorRadiusM)
  tendeEditorExtraLayers.push(L.polyline([[lat.value, lon.value], windowPt], { color: '#38bdf8', weight: 2.2, opacity: 0.9, dashArray: '7,5' }).addTo(tendeMapObj))
  const facadeAz = Number(s.facade_azimuth_deg)
  if (Number.isFinite(facadeAz) && facadeAz >= 0) {
    const facadePt = destinationPoint(lat.value, lon.value, facadeAz, cfg.value.sectorRadiusM)
    tendeEditorExtraLayers.push(L.polyline([[lat.value, lon.value], facadePt], { color: '#f43f5e', weight: 3, opacity: 0.95, dashArray: '10,5' }).addTo(tendeMapObj))
    tendeEditorExtraLayers.push(L.circleMarker(facadePt, { radius: 5, color: '#fff1f2', fillColor: '#f43f5e', fillOpacity: 1, weight: 2 }).addTo(tendeMapObj))
    tendeEditorExtraLayers.push(L.marker(destinationPoint(lat.value, lon.value, facadeAz, cfg.value.sectorRadiusM + 16), { icon: L.divIcon({ className: 'sun-ref-label-wrap', html: '<span class="sun-ref-label facade">Facciata</span>', iconSize: [82, 18], iconAnchor: [41, 9] }), interactive: false }).addTo(tendeMapObj))
  }
  const p1 = destinationPoint(lat.value, lon.value, s.azimuth_start_deg, cfg.value.sectorRadiusM)
  const p2 = destinationPoint(lat.value, lon.value, s.azimuth_end_deg, cfg.value.sectorRadiusM)
  tendeStartMarker = L.marker(p1, { draggable: tendeEditMode.value, icon: L.divIcon({ className: 'tende-handle-wrap', html: '<span class="tende-handle tende-handle-start"></span>', iconSize: [18, 18], iconAnchor: [9, 9] }) }).addTo(tendeMapObj)
  tendeEndMarker = L.marker(p2, { draggable: tendeEditMode.value, icon: L.divIcon({ className: 'tende-handle-wrap', html: '<span class="tende-handle tende-handle-end"></span>', iconSize: [18, 18], iconAnchor: [9, 9] }) }).addTo(tendeMapObj)
  const liveAz = Number(s.sensors?.sun_azimuth ?? data.value?.sun_position?.azimuth_compass_deg)
  const liveAlt = Number(s.sensors?.sun_elevation ?? data.value?.sun_position?.altitude_deg)
  if (Number.isFinite(liveAz)) {
    const sunPt = destinationPoint(lat.value, lon.value, liveAz, Number.isFinite(liveAlt) ? altitudeToRadius(liveAlt) : cfg.value.sectorRadiusM)
    tendeEditorExtraLayers.push(L.polyline([[lat.value, lon.value], sunPt], { color: '#2dd4bf', weight: 2.3, opacity: 0.9, dashArray: '8,6' }).addTo(tendeMapObj))
    tendeEditorExtraLayers.push(L.circleMarker(sunPt, { radius: 6, color: '#2dd4bf', fillColor: '#2dd4bf', fillOpacity: 1, weight: 2 }).addTo(tendeMapObj))
  }
  if (tendeEditMode.value) {
    const updatePreview = () => {
      if (!tendePoly || !selectedShadeEdit.value) return
      const band = Number.isFinite(Number(selectedShadeEdit.value.altitude_min_deg)) && Number.isFinite(Number(selectedShadeEdit.value.altitude_max_deg))
      const outer = band ? altitudeToRadius(Math.min(Number(selectedShadeEdit.value.altitude_min_deg), Number(selectedShadeEdit.value.altitude_max_deg))) : cfg.value.sectorRadiusM
      const inner = band ? altitudeToRadius(Math.max(Number(selectedShadeEdit.value.altitude_min_deg), Number(selectedShadeEdit.value.altitude_max_deg))) : 0
      tendePoly.setLatLngs(band ? buildSectorBandPolygonPoints(selectedShadeEdit.value.azimuth_start_deg, selectedShadeEdit.value.azimuth_end_deg, outer, inner) : buildSectorPolygonPoints(selectedShadeEdit.value.azimuth_start_deg, selectedShadeEdit.value.azimuth_end_deg, cfg.value.sectorRadiusM))
    }
    tendeStartMarker.on('dragstart', () => { tendeMapObj.dragging.disable() })
    tendeEndMarker.on('dragstart', () => { tendeMapObj.dragging.disable() })
    tendeStartMarker.on('drag', (e) => { s.azimuth_start_deg = angleFromCenter(e.latlng); updatePreview() })
    tendeEndMarker.on('drag', (e) => { s.azimuth_end_deg = angleFromCenter(e.latlng); updatePreview() })
    tendeStartMarker.on('dragend', () => { tendeMapObj.dragging.enable(); drawTendeEditor() })
    tendeEndMarker.on('dragend', () => { tendeMapObj.dragging.enable(); drawTendeEditor() })
  }
}

function toggleTendeEditMode() {
  tendeEditMode.value = !tendeEditMode.value
  drawTendeEditor()
}

function nextWizardStep() {
  tendeWizardStep.value = Math.min(wizardSteps.length - 1, tendeWizardStep.value + 1)
}

function prevWizardStep() {
  tendeWizardStep.value = Math.max(0, tendeWizardStep.value - 1)
}

function energyWizardNext() {
  energyWizardStep.value = Math.min(energyWizardSteps.length - 1, energyWizardStep.value + 1)
}

function energyWizardPrev() {
  energyWizardStep.value = Math.max(0, energyWizardStep.value - 1)
}

function buildSunsynkConfigFromWizard() {
  const w = energyWizardForm.value
  const entities = {
    inverter_status_59: String(w.inverter_status_59 || ''),
    inverter_power_175: String(w.inverter_power_175 || ''),
    inverter_voltage_154: String(w.inverter_voltage_154 || ''),
    inverter_current_164: String(w.inverter_current_164 || ''),
    load_frequency_192: String(w.load_frequency_192 || ''),
    grid_power_169: String(w.grid_power_169 || ''),
    grid_ct_power_172: String(w.grid_ct_power_172 || ''),
    grid_connected_status_194: String(w.grid_connected_status_194 || ''),
    essential_power: String(w.essential_power || ''),
    nonessential_power: String(w.nonessential_power || ''),
    essential_load1: String(w.essential_load1 || ''),
    essential_load2: String(w.essential_load2 || ''),
    essential_load3: String(w.essential_load3 || ''),
    essential_load4: String(w.essential_load4 || ''),
    essential_load5: String(w.essential_load5 || ''),
    essential_load6: String(w.essential_load6 || ''),
    aux_power_166: String(w.aux_power_166 || ''),
    aux_load1: String(w.aux_load1 || ''),
    aux_load2: String(w.aux_load2 || ''),
    aux_load3: String(w.aux_load3 || ''),
    aux_load4: String(w.aux_load4 || ''),
    aux_load5: String(w.aux_load5 || ''),
    aux_load6: String(w.aux_load6 || ''),
    aux_load7: String(w.aux_load7 || ''),
    non_essential_load1: String(w.non_essential_load1 || ''),
    non_essential_load2: String(w.non_essential_load2 || ''),
    non_essential_load3: String(w.non_essential_load3 || ''),
    battery_soc_184: String(w.battery_soc_184 || ''),
    battery_power_190: String(w.battery_power_190 || ''),
    battery_current_191: String(w.battery_current_191 || ''),
    battery_voltage_183: String(w.battery_voltage_183 || ''),
    battery2_soc_184: String(w.battery2_soc_184 || ''),
    battery2_current_191: String(w.battery2_current_191 || ''),
    battery2_voltage_183: String(w.battery2_voltage_183 || ''),
    battery3_power_190: String(w.battery3_power_190 || ''),
    battery3_soc_184: String(w.battery3_soc_184 || ''),
    battery3_current_191: String(w.battery3_current_191 || ''),
    battery3_voltage_183: String(w.battery3_voltage_183 || ''),
    pv_total: String(w.pv_total || ''),
    pv1_power_186: String(w.pv1_power_186 || ''),
    pv2_power_187: String(w.pv2_power_187 || ''),
    pv1_voltage_109: String(w.pv1_voltage_109 || ''),
    pv1_current_110: String(w.pv1_current_110 || ''),
    pv2_voltage_111: String(w.pv2_voltage_111 || ''),
    pv2_current_112: String(w.pv2_current_112 || ''),
    pv3_power_188: String(w.pv3_power_188 || ''),
    pv4_power_189: String(w.pv4_power_189 || ''),
    pv5_power: String(w.pv5_power || ''),
    pv6_power: String(w.pv6_power || ''),
    pv3_voltage_113: String(w.pv3_voltage_113 || ''),
    pv3_current_114: String(w.pv3_current_114 || ''),
    pv4_voltage_115: String(w.pv4_voltage_115 || ''),
    pv4_current_116: String(w.pv4_current_116 || ''),
    pv5_voltage: String(w.pv5_voltage || ''),
    pv5_current: String(w.pv5_current || ''),
    pv6_voltage: String(w.pv6_voltage || ''),
    pv6_current: String(w.pv6_current || ''),
    battery2_power_190: String(w.battery2_power_190 || ''),
    use_timer_248: String(w.use_timer_248 || ''),
    priority_load_243: String(w.priority_load_243 || ''),
    day_pv_energy_108: String(w.day_pv_energy_108 || ''),
    day_battery_charge_70: String(w.day_battery_charge_70 || ''),
    day_battery_discharge_71: String(w.day_battery_discharge_71 || ''),
    day_load_energy_84: String(w.day_load_energy_84 || ''),
    day_grid_import_76: String(w.day_grid_import_76 || ''),
    day_grid_export_77: String(w.day_grid_export_77 || ''),
  }
  try {
    const extraRaw = String(w.entities_extra_json || '').trim()
    if (extraRaw) {
      const extraObj = JSON.parse(extraRaw)
      if (extraObj && typeof extraObj === 'object' && !Array.isArray(extraObj)) {
        for (const [k, v] of Object.entries(extraObj)) entities[String(k)] = String(v ?? '')
      }
    }
  } catch (_) {}
  Object.keys(entities).forEach((k) => {
    if (!String(entities[k] || '').trim()) delete entities[k]
  })
  const fullWithAux = String(w.cardstyle || 'full') === 'full' && Boolean(w.show_aux)
  if (fullWithAux) {
    delete entities.essential_load3
    delete entities.essential_load4
    delete entities.essential_load5
    delete entities.essential_load6
  }
  const solarMppts = Math.max(1, Math.min(6, Number(w.solar_mppts || 1)))

  return {
    cardstyle: String(w.cardstyle || 'full'),
    show_solar: Boolean(w.show_solar),
    show_battery: Boolean(w.show_battery),
    show_grid: Boolean(w.show_grid),
    dynamic_line_width: Boolean(w.dynamic_line_width),
    min_line_width: Math.max(1, Math.min(6, Number(w.min_line_width || 1))),
    max_line_width: Math.max(1, Math.min(8, Number(w.max_line_width || 4))),
    wide: Boolean(w.wide),
    inverter: {
      modern: Boolean(w.inverter_modern),
      auto_scale: Boolean(w.inverter_auto_scale),
      three_phase: Boolean(w.inverter_three_phase),
    },
    solar: {
      mppts: solarMppts,
      colour: String(w.color_solar || '#f59e0b'),
      show_daily: Boolean(w.solar_show_daily),
      animation_speed: Math.max(1, Math.min(20, Number(w.solar_animation_speed || 6))),
      max_power: Math.max(100, Number(w.solar_max_power || 7000)),
      dynamic_colour: true,
      pv1_name: String(w.pv1_name || ''),
      pv2_name: String(w.pv2_name || ''),
      pv3_name: String(w.pv3_name || ''),
      pv4_name: String(w.pv4_name || ''),
      pv5_name: String(w.pv5_name || ''),
      pv6_name: String(w.pv6_name || ''),
      ...(Number(w.pv1_max_power) > 0 ? { pv1_max_power: Number(w.pv1_max_power) } : {}),
      ...(Number(w.pv2_max_power) > 0 ? { pv2_max_power: Number(w.pv2_max_power) } : {}),
      ...(Number(w.pv3_max_power) > 0 ? { pv3_max_power: Number(w.pv3_max_power) } : {}),
      ...(Number(w.pv4_max_power) > 0 ? { pv4_max_power: Number(w.pv4_max_power) } : {}),
      ...(Number(w.pv5_max_power) > 0 ? { pv5_max_power: Number(w.pv5_max_power) } : {}),
      ...(Number(w.pv6_max_power) > 0 ? { pv6_max_power: Number(w.pv6_max_power) } : {}),
    },
    battery: {
      count: Math.max(1, Math.min(2, Number(w.battery_count || 1))),
      colour: String(w.color_battery || '#a855f7'),
      name: String(w.battery1_name || ''),
      energy: Math.max(100, Number(w.battery_energy_wh || 15960)),
      shutdown_soc: Math.max(0, Math.min(100, Number(w.battery_shutdown_soc ?? 10))),
      show_daily: Boolean(w.battery_show_daily),
      animation_speed: Math.max(1, Math.min(20, Number(w.battery_animation_speed || 8))),
      max_power: Math.max(100, Number(w.battery_max_power || 5000)),
      auto_scale: Boolean(w.battery_auto_scale),
      dynamic_colour: true,
      linear_gradient: true,
      animate: true,
    },
    battery2: {
      name: String(w.battery2_name || ''),
      energy: Math.max(100, Number(w.battery_energy_wh || 15960)),
      shutdown_soc: Math.max(0, Math.min(100, Number(w.battery_shutdown_soc ?? 10))),
      max_power: Math.max(100, Number(w.battery_max_power || 5000)),
      animation_speed: Math.max(1, Math.min(20, Number(w.battery_animation_speed || 8))),
      auto_scale: Boolean(w.battery_auto_scale),
      dynamic_colour: true,
      linear_gradient: true,
      animate: true,
    },
    battery3: {
      name: String(w.battery3_name || ''),
      energy: Math.max(100, Number(w.battery_energy_wh || 15960)),
      shutdown_soc: Math.max(0, Math.min(100, Number(w.battery_shutdown_soc ?? 10))),
      max_power: Math.max(100, Number(w.battery_max_power || 5000)),
      animation_speed: Math.max(1, Math.min(20, Number(w.battery_animation_speed || 8))),
      auto_scale: Boolean(w.battery_auto_scale),
      dynamic_colour: true,
      linear_gradient: true,
      animate: true,
    },
    load: {
      colour: String(w.color_load || '#cbd5e1'),
      additional_loads: fullWithAux ? Math.max(0, Math.min(2, Number(w.additional_loads || 2))) : Math.max(0, Math.min(6, Number(w.additional_loads || 2))),
      show_aux: Boolean(w.show_aux),
      essential_name: String(w.load_essential_name || 'Essential'),
      aux_name: String(w.load_aux_name || 'Auxiliary'),
      label_daily_load: String(w.load_label_daily || 'Daily Load'),
      load1_name: String(w.load1_name || ''),
      load2_name: String(w.load2_name || ''),
      load3_name: String(w.load3_name || ''),
      load4_name: String(w.load4_name || ''),
      load5_name: String(w.load5_name || ''),
      load6_name: String(w.load6_name || ''),
      show_daily: Boolean(w.load_show_daily),
      animation_speed: Math.max(1, Math.min(20, Number(w.load_animation_speed || 6))),
      max_power: Math.max(100, Number(w.load_max_power || 9000)),
      auto_scale: Boolean(w.load_auto_scale),
      dynamic_colour: Boolean(w.load_dynamic_colour),
      dynamic_icon: Boolean(w.load_dynamic_icon),
      invert_flow: Boolean(w.load_invert_flow),
      max_colour: String(w.load_max_colour || '#f59e0b'),
      off_colour: String(w.load_off_colour || '#808080'),
      aux_colour: String(w.load_aux_colour || '#cbd5e1'),
      aux_off_colour: String(w.load_aux_off_colour || '#808080'),
      aux_dynamic_colour: Boolean(w.load_aux_dynamic_colour),
      aux_type: String(w.load_aux_type || 'default'),
      show_absolute_aux: Boolean(w.load_show_absolute_aux),
      show_daily_aux: Boolean(w.load_show_daily_aux),
      aux_loads: Math.max(0, Math.min(7, Number(w.load_aux_loads || 0))),
      aux_load1_name: String(w.load_aux_load1_name || ''),
      aux_load2_name: String(w.load_aux_load2_name || ''),
      aux_load3_name: String(w.load_aux_load3_name || ''),
      aux_load4_name: String(w.load_aux_load4_name || ''),
      aux_load5_name: String(w.load_aux_load5_name || ''),
      aux_load6_name: String(w.load_aux_load6_name || ''),
      aux_load7_name: String(w.load_aux_load7_name || ''),
      aux_load1_icon: String(w.load_aux_load1_icon || 'default'),
      aux_load2_icon: String(w.load_aux_load2_icon || 'default'),
      aux_load3_icon: String(w.load_aux_load3_icon || 'default'),
      aux_load4_icon: String(w.load_aux_load4_icon || 'default'),
      aux_load5_icon: String(w.load_aux_load5_icon || 'default'),
      aux_load6_icon: String(w.load_aux_load6_icon || 'default'),
      aux_load7_icon: String(w.load_aux_load7_icon || 'default'),
      load1_icon: String(w.load1_icon || 'default'),
      load2_icon: String(w.load2_icon || 'default'),
      load3_icon: String(w.load3_icon || 'default'),
      load4_icon: String(w.load4_icon || 'default'),
      load5_icon: String(w.load5_icon || 'default'),
      load6_icon: String(w.load6_icon || 'default'),
    },
    grid: {
      colour: String(w.color_grid || '#06b6d4'),
      show_daily_buy: Boolean(w.grid_show_daily_buy),
      show_daily_sell: Boolean(w.grid_show_daily_sell),
      invert_grid: Boolean(w.grid_invert_grid),
      show_absolute: Boolean(w.grid_show_absolute),
      show_nonessential: Boolean(w.grid_show_nonessential),
      additional_loads: Math.max(0, Math.min(3, Number(w.grid_additional_loads || 0))),
      grid_name: String(w.grid_name || 'Linea Sas'),
      label_daily_grid_buy: String(w.grid_label_daily_buy || 'Consumo Giornaliero'),
      label_daily_grid_sell: String(w.grid_label_daily_sell || 'Vendita Giornaliera'),
      nonessential_name: String(w.grid_nonessential_name || 'Non Essential'),
      load1_name: String(w.grid_load1_name || ''),
      load2_name: String(w.grid_load2_name || ''),
      load3_name: String(w.grid_load3_name || ''),
      invert_flow: Boolean(w.grid_invert_flow),
      energy_cost_decimals: Math.max(0, Math.min(4, Number(w.grid_energy_cost_decimals || 0))),
      animation_speed: Math.max(1, Math.min(20, Number(w.grid_animation_speed || 9))),
      max_power: Math.max(100, Number(w.grid_max_power || 8000)),
      auto_scale: Boolean(w.grid_auto_scale),
      no_grid_colour: String(w.color_no_grid || '#49ab6a'),
      grid_off_colour: String(w.color_grid_off || '#3a8d53'),
      export_colour: String(w.color_grid_export || '#6a7ac8'),
      nonessential_icon: String(w.grid_nonessential_icon || 'default'),
      load1_icon: String(w.grid_load1_icon || 'default'),
      load2_icon: String(w.grid_load2_icon || 'default'),
      load3_icon: String(w.grid_load3_icon || 'default'),
      import_icon: String(w.grid_import_icon || 'mdi:transmission-tower-import'),
      export_icon: String(w.grid_export_icon || 'mdi:transmission-tower-export'),
      disconnected_icon: String(w.grid_disconnected_icon || 'mdi:transmission-tower-off'),
    },
    entities,
  }
}

function mergeObjectsDeep(base, patch) {
  const out = { ...(base || {}) }
  for (const [k, v] of Object.entries(patch || {})) {
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      out[k] = mergeObjectsDeep((base || {})[k] || {}, v)
    } else {
      out[k] = v
    }
  }
  return out
}

function pruneSunsynkPvByMppts(cfg) {
  const mppts = Math.max(1, Math.min(6, Number(cfg?.solar?.mppts || 1)))
  const byPv = {
    2: ['pv2_power_187', 'pv2_voltage_111', 'pv2_current_112'],
    3: ['pv3_power_188', 'pv3_voltage_113', 'pv3_current_114'],
    4: ['pv4_power_189', 'pv4_voltage_115', 'pv4_current_116'],
    5: ['pv5_power', 'pv5_voltage', 'pv5_current'],
    6: ['pv6_power', 'pv6_voltage', 'pv6_current'],
  }
  cfg.entities = (cfg.entities && typeof cfg.entities === 'object' && !Array.isArray(cfg.entities)) ? cfg.entities : {}
  cfg.solar = (cfg.solar && typeof cfg.solar === 'object' && !Array.isArray(cfg.solar)) ? cfg.solar : {}
  for (let n = 2; n <= 6; n += 1) {
    if (n <= mppts) continue
    for (const key of byPv[n] || []) delete cfg.entities[key]
    delete cfg.solar[`pv${n}_name`]
    delete cfg.solar[`pv${n}_max_power`]
  }
  return cfg
}

function applyEnergyWizard(silent = false) {
  const cfg = buildSunsynkConfigFromWizard()
  let merged = cfg
  try {
    const raw = String(energyForm.value.sunsynk_card_config_json || '').trim()
    const current = raw ? JSON.parse(raw) : {}
    if (current && typeof current === 'object' && !Array.isArray(current)) {
      merged = mergeObjectsDeep(current, cfg)
      merged.entities = { ...(cfg.entities || {}) }
    }
  } catch (_) {}
  pruneSunsynkPvByMppts(merged)
  energyForm.value.sunsynk_card_config_json = JSON.stringify(merged, null, 2)
  energyForm.value.pv_power_entity_id = String(energyWizardForm.value.pv1_power_186 || '')
  energyForm.value.home_power_entity_id = String(energyWizardForm.value.inverter_power_175 || '')
  energyForm.value.grid_power_entity_id = String(energyWizardForm.value.grid_power_169 || '')
  energyForm.value.battery_power_entity_id = String(energyWizardForm.value.battery_power_190 || '')
  energyForm.value.battery_soc_entity_id = String(energyWizardForm.value.battery_soc_184 || '')
  energyForm.value.inverter_voltage_entity_id = String(energyWizardForm.value.inverter_voltage_154 || '')
  energyForm.value.load_frequency_entity_id = String(energyWizardForm.value.load_frequency_192 || '')
  energyForm.value.pv_energy_today_entity_id = String(energyWizardForm.value.day_pv_energy_108 || '')
  energyForm.value.home_energy_today_entity_id = String(energyWizardForm.value.day_load_energy_84 || '')
  energyForm.value.grid_import_today_entity_id = String(energyWizardForm.value.day_grid_import_76 || '')
  energyForm.value.grid_export_today_entity_id = String(energyWizardForm.value.day_grid_export_77 || '')
  energyForm.value.kflow_solar_max_power_w = Number(energyWizardForm.value.solar_max_power ?? energyForm.value.kflow_solar_max_power_w ?? 7000)
  energyForm.value.kflow_load_max_power_w = Number(energyWizardForm.value.load_max_power ?? energyForm.value.kflow_load_max_power_w ?? 9000)
  energyForm.value.kflow_grid_max_power_w = Number(energyWizardForm.value.grid_max_power ?? energyForm.value.kflow_grid_max_power_w ?? 8000)
  energyForm.value.kflow_battery_capacity_wh = Number(energyWizardForm.value.battery_energy_wh ?? energyForm.value.kflow_battery_capacity_wh ?? 15360)
  energyForm.value.kflow_battery_max_power_w = Number(energyWizardForm.value.battery_max_power ?? energyForm.value.kflow_battery_max_power_w ?? 5000)
  energyForm.value.kflow_battery_shutdown_soc = Number(energyWizardForm.value.battery_shutdown_soc ?? energyForm.value.kflow_battery_shutdown_soc ?? 10)
  if (!silent) baseSaveStatus.value = 'Wizard Energy applicato: JSON card generato.'
}

function syncWizardFromEnergyForm() {
  // Keep direct UI edits (Entita Potenza/Giornaliere) in sync before JSON generation.
  energyWizardForm.value.pv1_power_186 = String(energyForm.value.pv_power_entity_id || '')
  energyWizardForm.value.inverter_power_175 = String(energyForm.value.home_power_entity_id || '')
  energyWizardForm.value.grid_power_169 = String(energyForm.value.grid_power_entity_id || '')
  energyWizardForm.value.battery_power_190 = String(energyForm.value.battery_power_entity_id || '')
  energyWizardForm.value.battery_soc_184 = String(energyForm.value.battery_soc_entity_id || '')
  energyWizardForm.value.inverter_voltage_154 = String(energyForm.value.inverter_voltage_entity_id || '')
  energyWizardForm.value.load_frequency_192 = String(energyForm.value.load_frequency_entity_id || '')
  energyWizardForm.value.day_pv_energy_108 = String(energyForm.value.pv_energy_today_entity_id || '')
  energyWizardForm.value.day_load_energy_84 = String(energyForm.value.home_energy_today_entity_id || '')
  energyWizardForm.value.day_grid_import_76 = String(energyForm.value.grid_import_today_entity_id || '')
  energyWizardForm.value.day_grid_export_77 = String(energyForm.value.grid_export_today_entity_id || '')
  syncKFlowScaleToWizard()
}

function onEnergyCardstyleChange() {
  const selected = String(energyWizardForm.value.cardstyle || 'full')
  const baseCfg = buildSunsynkConfigFromWizard()
  try {
    const raw = String(energyForm.value.sunsynk_card_config_json || '').trim()
    const parsed = raw ? JSON.parse(raw) : {}
    const obj = (parsed && typeof parsed === 'object' && !Array.isArray(parsed))
      ? mergeObjectsDeep(baseCfg, parsed)
      : baseCfg
    obj.cardstyle = selected
    if (!obj.entities || typeof obj.entities !== 'object' || Array.isArray(obj.entities)) obj.entities = { ...baseCfg.entities }
    energyForm.value.sunsynk_card_config_json = JSON.stringify(obj, null, 2)
  } catch (_) {
    baseCfg.cardstyle = selected
    energyForm.value.sunsynk_card_config_json = JSON.stringify(baseCfg, null, 2)
  }
}

function applyWizardPreset(kind) {
  const e = selectedShadeEdit.value
  if (!e) return
  if (kind === 'base_safe') {
    e.enabled = true
    e.sun_logic_enabled = true
    e.open_when_no_sun = true
    e.command_mode_open_close = true
  } else if (kind === 'sun_fov') {
    e.use_start_stop_azimuth = false
    e.fov_left = 70
    e.fov_right = 70
  } else if (kind === 'positions_balanced') {
    e.default_position = 100
    e.sunset_position = 0
    e.min_position = 10
    e.min_delta = 3
    e.min_command_interval_seconds = 120
  } else if (kind === 'weather_safe') {
    e.weather_guard_enabled = true
    e.protect_on_wind_alarm = true
    e.protect_on_rain_alarm = true
    e.protect_on_facade_rain_risk = true
    e.weather_wind_safe_position = 0
    e.weather_rain_safe_position = 0
    e.weather_facade_rain_safe_position = 0
  } else if (kind === 'thermal_conservative') {
    e.thermal_enabled = true
    e.thermal_hysteresis = 0.5
    e.thermal_heat_gain_position = 70
    e.thermal_cool_block_position = Number(e.min_position ?? 10)
  }
  drawTendeEditor()
}

function applySavedShadeLocally(editShade, settings) {
  const key = shadeKey(editShade)
  if (!key) return
  const prev = Array.isArray(lastValidTendeShades.value) ? lastValidTendeShades.value : []
  const idx = prev.findIndex((s) => shadeKey(s) === key)
  const base = idx >= 0 ? prev[idx] : {}
  const merged = {
    ...base,
    id: editShade.id || base.id || null,
    name: editShade.name || base.name || editShade.id || editShade.cover_entity || 'cover',
    cover_entity: editShade.cover_entity || base.cover_entity || null,
    ...settings,
    settings: { ...(base.settings || {}), ...settings },
  }
  if (idx >= 0) {
    const copy = prev.slice()
    copy[idx] = merged
    lastValidTendeShades.value = copy
  } else {
    lastValidTendeShades.value = mergeTendeShades(prev, [merged])
  }
}

function valuesEquivalent(expected, actual) {
  if (typeof expected === 'boolean') return Boolean(actual) === expected
  const en = Number(expected)
  const an = Number(actual)
  if (Number.isFinite(en) && Number.isFinite(an)) return Math.abs(en - an) <= 0.05
  return String(expected ?? '').trim() === String(actual ?? '').trim()
}

function findSavedShade(target) {
  return tendeMapShades.value.find((s) => {
    if (target.id && s.id === target.id) return true
    if (target.cover_entity && String(s.cover_entity || '').trim() === String(target.cover_entity).trim()) return true
    if (target.name && String(s.name || '').trim() === String(target.name).trim()) return true
    return false
  }) || null
}

function shadeConfirmsSettings(shade, settings) {
  if (!shade || !settings) return false
  const st = shade.settings || {}
  let checked = 0
  for (const [key, expected] of Object.entries(settings)) {
    const actual = st[key] ?? shade[key]
    if (actual === undefined || actual === null) continue
    checked += 1
    if (!valuesEquivalent(expected, actual)) return false
  }
  return checked > 0
}

async function saveSelectedShade() {
  if (!selectedShadeEdit.value) return
  tendeSaveStatus.value = 'Salvataggio...'
  try {
    const e = selectedShadeEdit.value
    const settings = {
      enabled: Boolean(e.enabled),
      sun_logic_enabled: Boolean(e.sun_logic_enabled),
      invert_sun_logic: Boolean(e.invert_sun_logic),
      open_when_no_sun: Boolean(e.open_when_no_sun),
      use_start_stop_azimuth: Boolean(e.use_start_stop_azimuth),
      command_mode: e.command_mode_open_close ? 'open_close' : 'percentage',
      window_azimuth: Number(e.window_azimuth),
      facade_azimuth_deg: Number(e.facade_azimuth_deg),
      azimuth_start_deg: Number(e.azimuth_start_deg),
      azimuth_end_deg: Number(e.azimuth_end_deg),
      fov_left: Number(e.fov_left),
      fov_right: Number(e.fov_right),
      altitude_min_deg: Number(e.altitude_min_deg),
      altitude_max_deg: Number(e.altitude_max_deg),
      default_position: Number(e.default_position),
      sunset_position: Number(e.sunset_position),
      min_position: Number(e.min_position),
      max_position: Number(e.max_position),
      min_delta: Number(e.min_delta),
      interval_minutes: Number(e.interval_minutes),
      min_command_interval_seconds: Number(e.min_command_interval_seconds),
      thermal_enabled: Boolean(e.thermal_enabled),
      thermal_climate_entity: String(e.thermal_climate_entity || '').trim(),
      thermal_hysteresis: Number(e.thermal_hysteresis),
      thermal_heat_gain_position: Number(e.thermal_heat_gain_position),
      thermal_cool_block_position: Number(e.thermal_cool_block_position),
      open_close_threshold: Number(e.open_close_threshold),
      sun_probe_threshold: Number(e.sun_probe_threshold),
      weather_guard_enabled: Boolean(e.weather_guard_enabled),
      protect_on_wind_alarm: Boolean(e.protect_on_wind_alarm),
      protect_on_rain_alarm: Boolean(e.protect_on_rain_alarm),
      protect_on_facade_rain_risk: Boolean(e.protect_on_facade_rain_risk),
      weather_safe_position: Number(e.weather_safe_position),
      weather_wind_safe_position: Number(e.weather_wind_safe_position),
      weather_rain_safe_position: Number(e.weather_rain_safe_position),
      weather_facade_rain_safe_position: Number(e.weather_facade_rain_safe_position),
    }
    const r = await fetch('api/tende/map/update', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: e.id,
        name: e.name || null,
        cover_entity: e.cover_entity || null,
        settings,
      }),
    })
    const j = await r.json()
    if (!r.ok || !j.ok) { const err = new Error(j.error || 'save_failed'); err.cause = j; throw err }
    if (j.status === 'confirmed_by_map') tendeSaveStatus.value = 'Configurazione cover applicata (confermata dalla mappa).'
    else if (j.status === 'sent_no_ack') tendeSaveStatus.value = 'Configurazione inviata a e-Tende (verifica applicazione...).'
    else if (j.ack && (j.ack.status === 'ok' || j.ack.ok === true)) tendeSaveStatus.value = 'Configurazione cover applicata (ACK ricevuto).'
    else if (j.ack) tendeSaveStatus.value = `ACK: ${j.ack.status || 'ricevuto'}`
    else tendeSaveStatus.value = 'Configurazione inviata (ACK non ricevuto).'
    applySavedShadeLocally(e, settings)
    if (selectedShadeId.value) selectShade(selectedShadeId.value)
    if (j.status === 'sent_no_ack') await new Promise((resolve) => setTimeout(resolve, 1500))
    await loadData()
    if (j.status === 'sent_no_ack') {
      const confirmed = shadeConfirmsSettings(findSavedShade(e), settings)
      tendeSaveStatus.value = confirmed
        ? 'Configurazione cover applicata (verificata dalla mappa, ACK non ricevuto).'
        : 'Configurazione applicata in pagina. ACK non ricevuto: in attesa conferma mappa automatica.'
    }
  } catch (e) {
    let extra = ''
    try { if (e?.cause?.ack?.error) extra = ` (${e.cause.ack.error})`; else if (e?.cause?.error) extra = ` (${e.cause.error})` } catch (_) {}
    tendeSaveStatus.value = `Errore: ${e.message}${extra}`
  }
}

async function loadData() {
  const nowTs = Date.now()
  if (loadDataInFlight) return
  if (nowTs < loadDataBackoffUntilTs) return
  loadDataInFlight = true
  let j = null
  try {
    const r = await fetch('api/data', { cache: 'no-store' })
    if (!r.ok) throw new Error(`api_data_http_${r.status}`)
    j = await r.json()
    loadDataFailStreak = 0
    loadDataBackoffUntilTs = 0
  } catch (e) {
    console.warn('[e-SunMind] loadData failed:', e?.message || e)
    loadDataFailStreak = Math.min(loadDataFailStreak + 1, 6)
    // Exponential backoff to avoid hammering proxy/gateway on transient 5xx.
    const backoffMs = Math.min(60000, 2000 * (2 ** (loadDataFailStreak - 1)))
    loadDataBackoffUntilTs = Date.now() + backoffMs
    loadDataInFlight = false
    return
  }
  try {
    data.value = j
    const incomingShades = j?.tende_map?.shades
    if (Array.isArray(incomingShades) && incomingShades.filter((s) => s).length) {
      lastValidTendeShades.value = mergeTendeShades(lastValidTendeShades.value, incomingShades.filter((s) => s))
    }
    const incomingCoverStates = j?.tende_map?.cover_states
    if (incomingCoverStates && Object.keys(incomingCoverStates).length) {
      lastValidTendeCoverStates.value = incomingCoverStates
    }
    lat.value = Number(j?.coordinates?.latitude)
    lon.value = Number(j?.coordinates?.longitude)

    if (Number.isFinite(lat.value) && Number.isFinite(lon.value) && (tab.value === 'user' || tab.value === 'user_public')) {
      // Polling refresh should not start aggressive retry loops on missing containers.
      await ensureMainMapReady('loadData', { retryOnMissing: false })
    }
    // Keep forms in sync without reloading heavy options on every realtime poll.
    const shouldLoadOptions = !optionsLoadedOnce || tab.value === 'setting' || tab.value === 'energy_setup' || (Date.now() - optionsLastLoadTs > 60000)
    if (shouldLoadOptions) try {
      const ro = await fetch('api/options', { cache: 'no-store' })
      const oj = await ro.json()
      optionsLoadedOnce = true
      optionsLastLoadTs = Date.now()
      const fso = oj?.forecast_solar || {}
      fsForm.value = {
        enabled: Boolean(fso.enabled),
        api_key: String(fso.api_key || ''),
        declination: Number(fso.declination ?? 30),
        azimuth: Number(fso.azimuth ?? 0),
        kwp: Number(fso.kwp ?? 6.0),
      }
      baseForm.value = {
        latitude: Number(oj?.latitude ?? 44.6973),
        longitude: Number(oj?.longitude ?? 7.8683),
        timezone: String(oj?.timezone || 'Europe/Rome'),
        coordinates_source_mode: String(oj?.coordinates_source_mode || 'e_tende'),
        interval_minutes: Number(oj?.interval_minutes ?? 15),
        location_query: String(oj?.location_query || ''),
        pv_actual_entity_id: String(oj?.pv_actual_entity_id || 'sensor.zcs_easas_1_activepower_pv_ext'),
        external_temp_entity_id: String(oj?.external_temp_entity_id || 'sensor.temperature_and_humidity_sensor_lite_eterna_terrazzo_temperature'),
        external_humidity_entity_id: String(oj?.external_humidity_entity_id || 'sensor.temperature_and_humidity_sensor_lite_eterna_terrazzo_humidity'),
      }
      const wo = oj?.weather || {}
      weatherForm.value = {
        enabled: Boolean(wo.enabled ?? true),
        provider: String(wo.provider || 'met'),
      }
      const wso = oj?.weather_station || {}
      weatherStationForm.value = {
        enabled: Boolean(wso.enabled),
        stale_seconds: Number(wso.stale_seconds ?? 180),
        device_id: String(wso.device_id || ''),
        wind_speed_entity_id: String(wso.wind_speed_entity_id || ''),
        wind_gust_entity_id: String(wso.wind_gust_entity_id || ''),
        wind_direction_entity_id: String(wso.wind_direction_entity_id || ''),
        rain_rate_entity_id: String(wso.rain_rate_entity_id || ''),
        rain_1h_entity_id: String(wso.rain_1h_entity_id || ''),
        outdoor_temp_entity_id: String(wso.outdoor_temp_entity_id || ''),
        outdoor_humidity_entity_id: String(wso.outdoor_humidity_entity_id || ''),
        pressure_entity_id: String(wso.pressure_entity_id || ''),
        uv_index_entity_id: String(wso.uv_index_entity_id || ''),
        dewpoint_entity_id: String(wso.dewpoint_entity_id || ''),
        feels_like_entity_id: String(wso.feels_like_entity_id || ''),
        solar_lux_entity_id: String(wso.solar_lux_entity_id || ''),
        solar_radiation_entity_id: String(wso.solar_radiation_entity_id || ''),
        vpd_entity_id: String(wso.vpd_entity_id || ''),
      }
      // Autofill is intentionally not run during periodic refresh; it is triggered by device_id changes.
      const wgo = oj?.weather_guard || {}
      weatherGuardForm.value = {
        enabled: Boolean(wgo.enabled ?? true),
        wind_alarm_ms: Number(wgo.wind_alarm_ms ?? 12.0),
        rain_alarm_mm_h: Number(wgo.rain_alarm_mm_h ?? 1.5),
        facade_rain_min_wind_ms: Number(wgo.facade_rain_min_wind_ms ?? 6.0),
        facade_rain_min_mm_h: Number(wgo.facade_rain_min_mm_h ?? 0.8),
        facade_azimuth_deg: Number(wgo.facade_azimuth_deg ?? -1.0),
        facade_half_fov_deg: Number(wgo.facade_half_fov_deg ?? 60.0),
        stale_seconds: Number(wgo.stale_seconds ?? 180),
      }
      const aqo = oj?.air_quality || {}
      airQualityForm.value = {
        enabled: Boolean(aqo.enabled ?? true),
        provider: String(aqo.provider || 'open_meteo'),
      }
      const tmo = oj?.tende_map || {}
      tendeMapForm.value = {
        enabled: Boolean(tmo.enabled ?? true),
        mqtt_host: String(tmo.mqtt_host || '192.168.3.13'),
        mqtt_port: Number(tmo.mqtt_port ?? 1883),
        mqtt_username: String(tmo.mqtt_username || ''),
        mqtt_password: String(tmo.mqtt_password || ''),
        topic_state: String(tmo.topic_state || 'e-tendeintelligenti/map/shades'),
        topic_availability: String(tmo.topic_availability || 'e-tendeintelligenti/availability'),
        stale_seconds: Number(tmo.stale_seconds ?? 180),
      }
      const energyRoot = oj?.energy || {}
      const rawEnergySites = Array.isArray(energyRoot.sites) ? energyRoot.sites : []
      const selectedEnergyId = normalizeEnergySiteId(energyRoot.selected_site_id || rawEnergySites[0]?.id || 'default', 'default')
      energySites.value = rawEnergySites.length
        ? rawEnergySites.map((s, idx) => ({
            ...s,
            id: normalizeEnergySiteId(s?.id || s?.name, `impianto-${idx + 1}`),
            name: String(s?.name || s?.id || `Impianto ${idx + 1}`).trim(),
            show_sankey: Boolean(s?.show_sankey ?? true),
            sankey_extra_loads: normalizeSankeyExtraLoads(s?.sankey_extra_loads),
          }))
        : [{ ...energyRoot, id: selectedEnergyId, name: String(energyRoot.site_name || 'Impianto 1'), show_sankey: Boolean(energyRoot.show_sankey ?? true), sankey_extra_loads: normalizeSankeyExtraLoads(energyRoot.sankey_extra_loads) }]
      selectedEnergySiteId.value = energySites.value.some((s) => normalizeEnergySiteId(s.id, 'default') === selectedEnergyId)
        ? selectedEnergyId
        : normalizeEnergySiteId(energySites.value[0]?.id || 'default', 'default')
      const eo = energySites.value.find((s) => normalizeEnergySiteId(s.id, 'default') === selectedEnergySiteId.value) || energyRoot
      energyForm.value = {
        enabled: Boolean(eo.enabled ?? true),
        theme: String(eo.theme || 'classic_flow'),
        dashboard_background_color: String(eo.dashboard_background_color || '#080a10'),
        show_sankey: Boolean(eo.show_sankey ?? true),
        energy_dashboard_layout: String(eo.energy_dashboard_layout || 'sunsynk') === 'k_flow' ? 'k_flow' : 'sunsynk',
        cardstyle: 'full',
        pv_power_entity_id: String(eo.pv_power_entity_id || 'sensor.zcs_easas_1_activepower_pv_ext'),
        pv_power_sign: String(eo.pv_power_sign || 'positive'),
        home_power_entity_id: String(eo.home_power_entity_id || ''),
        home_power_sign: String(eo.home_power_sign || 'positive'),
        grid_power_entity_id: String(eo.grid_power_entity_id || ''),
        grid_power_sign: String(eo.grid_power_sign || 'positive'),
        battery_power_entity_id: String(eo.battery_power_entity_id || ''),
        battery_power_sign: String(eo.battery_power_sign || 'positive'),
        battery_soc_entity_id: String(eo.battery_soc_entity_id || ''),
        inverter_voltage_entity_id: String(eo.inverter_voltage_entity_id || ''),
        load_frequency_entity_id: String(eo.load_frequency_entity_id || ''),
        pv_installed_kwp: Number(eo.pv_installed_kwp ?? 6.6),
        pv_energy_today_entity_id: String(eo.pv_energy_today_entity_id || ''),
        home_energy_today_entity_id: String(eo.home_energy_today_entity_id || ''),
        grid_import_today_entity_id: String(eo.grid_import_today_entity_id || ''),
        grid_export_today_entity_id: String(eo.grid_export_today_entity_id || ''),
        energy_time_pv_stat_ids: String(eo.energy_time_pv_stat_ids || ''),
        energy_time_load_stat_ids: String(eo.energy_time_load_stat_ids || ''),
        energy_time_grid_import_stat_ids: String(eo.energy_time_grid_import_stat_ids || ''),
        energy_time_grid_export_stat_ids: String(eo.energy_time_grid_export_stat_ids || ''),
        energy_time_battery_charge_stat_ids: String(eo.energy_time_battery_charge_stat_ids || ''),
        energy_time_battery_discharge_stat_ids: String(eo.energy_time_battery_discharge_stat_ids || ''),
        energy_time_gas_stat_ids: String(eo.energy_time_gas_stat_ids || ''),
        energy_time_solar_thermal_stat_ids: String(eo.energy_time_solar_thermal_stat_ids || ''),
        kflow_solar_max_power_w: Number(eo.kflow_solar_max_power_w ?? 7000),
        kflow_load_max_power_w: Number(eo.kflow_load_max_power_w ?? 9000),
        kflow_grid_max_power_w: Number(eo.kflow_grid_max_power_w ?? 8000),
        kflow_battery_capacity_wh: Number(eo.kflow_battery_capacity_wh ?? 15360),
        kflow_battery_max_power_w: Number(eo.kflow_battery_max_power_w ?? 5000),
        kflow_battery_shutdown_soc: Number(eo.kflow_battery_shutdown_soc ?? 10),
        sunsynk_card_config_json: String(eo.sunsynk_card_config_json || ''),
        k_flow_card_config_json: String(eo.k_flow_card_config_json || ''),
        k_flow_invert_battery_power: false,
        k_flow_invert_grid_power: false,
        k_flow_total_pv_gen_entity: '',
        k_flow_battery_temp1: '',
        k_flow_battery_temp2: '',
        k_flow_battery_mos: '',
        k_flow_battery_shutdown_soc_entity: '',
        k_flow_battery_shutdown_soc_manual: '',
        k_flow_brand_logo: '',
        k_flow_pwr_bar_label: '',
        k_flow_aux_name: '',
        k_flow_aux_power: '',
        k_flow_aux_load1_name: '',
        k_flow_aux_load1: '',
        k_flow_aux_load2_name: '',
        k_flow_aux_load2: '',
        k_flow_aux_load3_name: '',
        k_flow_aux_load3: '',
        k_flow_aux_load4_name: '',
        k_flow_aux_load4: '',
        k_flow_aux_load5_name: '',
        k_flow_aux_load5: '',
        k_flow_aux_load6_name: '',
        k_flow_aux_load6: '',
        k_flow_aux_load7_name: '',
        k_flow_aux_load7: '',
        k_flow_home_icon: '',
        k_flow_min_cell_label: '',
        k_flow_min_cell_entity: '',
        k_flow_max_cell_label: '',
        k_flow_max_cell_entity: '',
        k_flow_batt_dis_label: '',
        k_flow_batt_dis_entity: '',
        entity_signs_json: String(eo.entity_signs_json || ''),
        sankey_extra_loads: normalizeSankeyExtraLoads(eo.sankey_extra_loads),
      }
      syncEnergySignsUiFromJson()
      syncKFlowUiFromJson()
      const wizardSeed = {
        ...energyWizardForm.value,
        cardstyle: 'full',
        pv1_power_186: String(eo.pv_power_entity_id || ''),
        pv2_power_187: '',
        grid_power_169: String(eo.grid_power_entity_id || ''),
        inverter_power_175: String(eo.home_power_entity_id || ''),
        battery_soc_184: String(eo.battery_soc_entity_id || ''),
        battery_power_190: String(eo.battery_power_entity_id || ''),
        inverter_voltage_154: String(eo.inverter_voltage_entity_id || ''),
        load_frequency_192: String(eo.load_frequency_entity_id || ''),
        day_pv_energy_108: String(eo.pv_energy_today_entity_id || ''),
        day_load_energy_84: String(eo.home_energy_today_entity_id || ''),
        day_grid_import_76: String(eo.grid_import_today_entity_id || ''),
        day_grid_export_77: String(eo.grid_export_today_entity_id || ''),
      }
      try {
        const parsed = JSON.parse(String(eo.sunsynk_card_config_json || '{}'))
        const ents = parsed?.entities || {}
        const solar = parsed?.solar || {}
        const battery = parsed?.battery || {}
        const battery2 = parsed?.battery2 || {}
        const battery3 = parsed?.battery3 || {}
        const load = parsed?.load || {}
        const grid = parsed?.grid || {}
        energyWizardForm.value = {
          ...wizardSeed,
          cardstyle: String(parsed?.cardstyle || wizardSeed.cardstyle || 'full'),
          show_solar: Boolean(parsed?.show_solar ?? wizardSeed.show_solar),
          show_battery: Boolean(parsed?.show_battery ?? wizardSeed.show_battery),
          show_grid: Boolean(parsed?.show_grid ?? wizardSeed.show_grid),
          dynamic_line_width: Boolean(parsed?.dynamic_line_width ?? wizardSeed.dynamic_line_width),
          min_line_width: Number(parsed?.min_line_width ?? wizardSeed.min_line_width),
          max_line_width: Number(parsed?.max_line_width ?? wizardSeed.max_line_width),
          wide: Boolean(parsed?.wide ?? wizardSeed.wide),
          inverter_modern: Boolean(parsed?.inverter?.modern ?? wizardSeed.inverter_modern),
          inverter_auto_scale: Boolean(parsed?.inverter?.auto_scale ?? wizardSeed.inverter_auto_scale),
          inverter_three_phase: Boolean(parsed?.inverter?.three_phase ?? wizardSeed.inverter_three_phase),
          solar_mppts: Number(solar.mppts ?? wizardSeed.solar_mppts ?? 1),
          solar_show_daily: Boolean(solar.show_daily ?? wizardSeed.solar_show_daily),
          solar_animation_speed: Number(solar.animation_speed ?? wizardSeed.solar_animation_speed),
          solar_max_power: Number(solar.max_power ?? wizardSeed.solar_max_power),
          pv1_name: String(solar.pv1_name || wizardSeed.pv1_name),
          pv2_name: String(solar.pv2_name || wizardSeed.pv2_name),
          pv3_name: String(solar.pv3_name || wizardSeed.pv3_name),
          pv4_name: String(solar.pv4_name || wizardSeed.pv4_name),
          pv5_name: String(solar.pv5_name || wizardSeed.pv5_name),
          pv6_name: String(solar.pv6_name || wizardSeed.pv6_name),
          pv1_max_power: Number(solar.pv1_max_power ?? wizardSeed.pv1_max_power ?? 0),
          pv2_max_power: Number(solar.pv2_max_power ?? wizardSeed.pv2_max_power ?? 0),
          pv3_max_power: Number(solar.pv3_max_power ?? wizardSeed.pv3_max_power ?? 0),
          pv4_max_power: Number(solar.pv4_max_power ?? wizardSeed.pv4_max_power ?? 0),
          pv5_max_power: Number(solar.pv5_max_power ?? wizardSeed.pv5_max_power ?? 0),
          pv6_max_power: Number(solar.pv6_max_power ?? wizardSeed.pv6_max_power ?? 0),
          battery_count: Number(battery.count ?? wizardSeed.battery_count),
          battery1_name: String(battery.name || wizardSeed.battery1_name),
          battery2_name: String(battery2.name || wizardSeed.battery2_name),
          battery3_name: String(battery3.name || wizardSeed.battery3_name),
          battery_energy_wh: Number(battery.energy ?? wizardSeed.battery_energy_wh),
          battery_shutdown_soc: Number(battery.shutdown_soc ?? wizardSeed.battery_shutdown_soc),
          battery_show_daily: Boolean(battery.show_daily ?? wizardSeed.battery_show_daily),
          battery_animation_speed: Number(battery.animation_speed ?? wizardSeed.battery_animation_speed),
          battery_max_power: Number(battery.max_power ?? wizardSeed.battery_max_power),
          battery_auto_scale: Boolean(battery.auto_scale ?? wizardSeed.battery_auto_scale),
          additional_loads: Number(load.additional_loads ?? wizardSeed.additional_loads),
          show_aux: Boolean(load.show_aux ?? wizardSeed.show_aux),
          load_essential_name: String(load.essential_name || wizardSeed.load_essential_name),
          load_aux_name: String(load.aux_name || wizardSeed.load_aux_name),
          load_label_daily: String(load.label_daily_load || wizardSeed.load_label_daily),
          load1_name: String(load.load1_name || wizardSeed.load1_name),
          load2_name: String(load.load2_name || wizardSeed.load2_name),
          load3_name: String(load.load3_name || wizardSeed.load3_name),
          load4_name: String(load.load4_name || wizardSeed.load4_name),
          load5_name: String(load.load5_name || wizardSeed.load5_name),
          load6_name: String(load.load6_name || wizardSeed.load6_name),
          load_show_daily: Boolean(load.show_daily ?? wizardSeed.load_show_daily),
          load_animation_speed: Number(load.animation_speed ?? wizardSeed.load_animation_speed),
          load_max_power: Number(load.max_power ?? wizardSeed.load_max_power),
          load_auto_scale: Boolean(load.auto_scale ?? wizardSeed.load_auto_scale),
          load_dynamic_colour: Boolean(load.dynamic_colour ?? wizardSeed.load_dynamic_colour),
          load_dynamic_icon: Boolean(load.dynamic_icon ?? wizardSeed.load_dynamic_icon),
          load_invert_flow: Boolean(load.invert_flow ?? wizardSeed.load_invert_flow),
          load_max_colour: String(load.max_colour || wizardSeed.load_max_colour),
          load_off_colour: String(load.off_colour || wizardSeed.load_off_colour),
          load_aux_colour: String(load.aux_colour || wizardSeed.load_aux_colour),
          load_aux_off_colour: String(load.aux_off_colour || wizardSeed.load_aux_off_colour),
          load_aux_dynamic_colour: Boolean(load.aux_dynamic_colour ?? wizardSeed.load_aux_dynamic_colour),
          load_aux_type: String(load.aux_type || wizardSeed.load_aux_type),
          load_show_absolute_aux: Boolean(load.show_absolute_aux ?? wizardSeed.load_show_absolute_aux),
          load_show_daily_aux: Boolean(load.show_daily_aux ?? wizardSeed.load_show_daily_aux),
          load_aux_loads: Number(load.aux_loads ?? wizardSeed.load_aux_loads),
          load_aux_load1_name: String(load.aux_load1_name || wizardSeed.load_aux_load1_name),
          load_aux_load2_name: String(load.aux_load2_name || wizardSeed.load_aux_load2_name),
          load_aux_load3_name: String(load.aux_load3_name || wizardSeed.load_aux_load3_name),
          load_aux_load4_name: String(load.aux_load4_name || wizardSeed.load_aux_load4_name),
          load_aux_load5_name: String(load.aux_load5_name || wizardSeed.load_aux_load5_name),
          load_aux_load6_name: String(load.aux_load6_name || wizardSeed.load_aux_load6_name),
          load_aux_load7_name: String(load.aux_load7_name || wizardSeed.load_aux_load7_name),
          load_aux_load1_icon: String(load.aux_load1_icon || wizardSeed.load_aux_load1_icon),
          load_aux_load2_icon: String(load.aux_load2_icon || wizardSeed.load_aux_load2_icon),
          load_aux_load3_icon: String(load.aux_load3_icon || wizardSeed.load_aux_load3_icon),
          load_aux_load4_icon: String(load.aux_load4_icon || wizardSeed.load_aux_load4_icon),
          load_aux_load5_icon: String(load.aux_load5_icon || wizardSeed.load_aux_load5_icon),
          load_aux_load6_icon: String(load.aux_load6_icon || wizardSeed.load_aux_load6_icon),
          load_aux_load7_icon: String(load.aux_load7_icon || wizardSeed.load_aux_load7_icon),
          grid_show_daily_buy: Boolean(grid.show_daily_buy ?? wizardSeed.grid_show_daily_buy),
          grid_show_daily_sell: Boolean(grid.show_daily_sell ?? wizardSeed.grid_show_daily_sell),
          grid_invert_grid: Boolean(grid.invert_grid ?? wizardSeed.grid_invert_grid),
          grid_show_absolute: Boolean(grid.show_absolute ?? wizardSeed.grid_show_absolute),
          grid_show_nonessential: Boolean(grid.show_nonessential ?? wizardSeed.grid_show_nonessential),
          grid_additional_loads: Number(grid.additional_loads ?? wizardSeed.grid_additional_loads),
          grid_name: String(grid.grid_name || wizardSeed.grid_name),
          grid_label_daily_buy: String(grid.label_daily_grid_buy || wizardSeed.grid_label_daily_buy),
          grid_label_daily_sell: String(grid.label_daily_grid_sell || wizardSeed.grid_label_daily_sell),
          grid_nonessential_name: String(grid.nonessential_name || wizardSeed.grid_nonessential_name),
          grid_load1_name: String(grid.load1_name || wizardSeed.grid_load1_name),
          grid_load2_name: String(grid.load2_name || wizardSeed.grid_load2_name),
          grid_load3_name: String(grid.load3_name || wizardSeed.grid_load3_name),
          grid_invert_flow: Boolean(grid.invert_flow ?? wizardSeed.grid_invert_flow),
          grid_energy_cost_decimals: Number(grid.energy_cost_decimals ?? wizardSeed.grid_energy_cost_decimals),
          grid_animation_speed: Number(grid.animation_speed ?? wizardSeed.grid_animation_speed),
          grid_max_power: Number(grid.max_power ?? wizardSeed.grid_max_power),
          grid_auto_scale: Boolean(grid.auto_scale ?? wizardSeed.grid_auto_scale),
          color_solar: String(solar.colour || wizardSeed.color_solar),
          color_battery: String(battery.colour || wizardSeed.color_battery),
          color_grid: String(grid.colour || wizardSeed.color_grid),
          color_grid_export: String(grid.export_colour || wizardSeed.color_grid_export),
          color_grid_off: String(grid.grid_off_colour || wizardSeed.color_grid_off),
          color_no_grid: String(grid.no_grid_colour || wizardSeed.color_no_grid),
          color_load: String(load.colour || wizardSeed.color_load),
          load1_icon: String(load.load1_icon || wizardSeed.load1_icon),
          load2_icon: String(load.load2_icon || wizardSeed.load2_icon),
          load3_icon: String(load.load3_icon || wizardSeed.load3_icon),
          load4_icon: String(load.load4_icon || wizardSeed.load4_icon),
          load5_icon: String(load.load5_icon || wizardSeed.load5_icon),
          load6_icon: String(load.load6_icon || wizardSeed.load6_icon),
          grid_nonessential_icon: String(grid.nonessential_icon || wizardSeed.grid_nonessential_icon),
          grid_load1_icon: String(grid.load1_icon || wizardSeed.grid_load1_icon),
          grid_load2_icon: String(grid.load2_icon || wizardSeed.grid_load2_icon),
          grid_load3_icon: String(grid.load3_icon || wizardSeed.grid_load3_icon),
          grid_import_icon: String(grid.import_icon || wizardSeed.grid_import_icon),
          grid_export_icon: String(grid.export_icon || wizardSeed.grid_export_icon),
          grid_disconnected_icon: String(grid.disconnected_icon || wizardSeed.grid_disconnected_icon),
          inverter_status_59: entityFromConfig(ents, 'inverter_status_59'),
          inverter_power_175: entityFromConfig(ents, 'inverter_power_175'),
          inverter_voltage_154: entityFromConfig(ents, 'inverter_voltage_154'),
          inverter_current_164: entityFromConfig(ents, 'inverter_current_164'),
          load_frequency_192: entityFromConfig(ents, 'load_frequency_192'),
          grid_power_169: entityFromConfig(ents, 'grid_power_169'),
          grid_ct_power_172: entityFromConfig(ents, 'grid_ct_power_172'),
          grid_connected_status_194: entityFromConfig(ents, 'grid_connected_status_194'),
          essential_power: entityFromConfig(ents, 'essential_power'),
          nonessential_power: entityFromConfig(ents, 'nonessential_power'),
          essential_load1: entityFromConfig(ents, 'essential_load1'),
          essential_load2: entityFromConfig(ents, 'essential_load2'),
          essential_load3: entityFromConfig(ents, 'essential_load3'),
          essential_load4: entityFromConfig(ents, 'essential_load4'),
          essential_load5: entityFromConfig(ents, 'essential_load5'),
          essential_load6: entityFromConfig(ents, 'essential_load6'),
          aux_power_166: entityFromConfig(ents, 'aux_power_166'),
          aux_load1: entityFromConfig(ents, 'aux_load1'),
          aux_load2: entityFromConfig(ents, 'aux_load2'),
          aux_load3: entityFromConfig(ents, 'aux_load3'),
          aux_load4: entityFromConfig(ents, 'aux_load4'),
          aux_load5: entityFromConfig(ents, 'aux_load5'),
          aux_load6: entityFromConfig(ents, 'aux_load6'),
          aux_load7: entityFromConfig(ents, 'aux_load7'),
          non_essential_load1: entityFromConfig(ents, 'non_essential_load1'),
          non_essential_load2: entityFromConfig(ents, 'non_essential_load2'),
          non_essential_load3: entityFromConfig(ents, 'non_essential_load3'),
          battery_soc_184: entityFromConfig(ents, 'battery_soc_184'),
          battery_power_190: entityFromConfig(ents, 'battery_power_190'),
          battery_current_191: entityFromConfig(ents, 'battery_current_191'),
          battery_voltage_183: entityFromConfig(ents, 'battery_voltage_183'),
          pv_total: entityFromConfig(ents, 'pv_total'),
          pv1_power_186: entityFromConfig(ents, 'pv1_power_186'),
          pv2_power_187: entityFromConfig(ents, 'pv2_power_187'),
          pv1_voltage_109: entityFromConfig(ents, 'pv1_voltage_109'),
          pv1_current_110: entityFromConfig(ents, 'pv1_current_110'),
          pv2_voltage_111: entityFromConfig(ents, 'pv2_voltage_111'),
          pv2_current_112: entityFromConfig(ents, 'pv2_current_112'),
          pv3_power_188: entityFromConfig(ents, 'pv3_power_188'),
          pv4_power_189: entityFromConfig(ents, 'pv4_power_189'),
          pv5_power: entityFromConfig(ents, 'pv5_power'),
          pv6_power: entityFromConfig(ents, 'pv6_power'),
          pv3_voltage_113: entityFromConfig(ents, 'pv3_voltage_113'),
          pv3_current_114: entityFromConfig(ents, 'pv3_current_114'),
          pv4_voltage_115: entityFromConfig(ents, 'pv4_voltage_115'),
          pv4_current_116: entityFromConfig(ents, 'pv4_current_116'),
          pv5_voltage: entityFromConfig(ents, 'pv5_voltage'),
          pv5_current: entityFromConfig(ents, 'pv5_current'),
          pv6_voltage: entityFromConfig(ents, 'pv6_voltage'),
          pv6_current: entityFromConfig(ents, 'pv6_current'),
          battery2_power_190: entityFromConfig(ents, 'battery2_power_190'),
          use_timer_248: entityFromConfig(ents, 'use_timer_248'),
          priority_load_243: entityFromConfig(ents, 'priority_load_243'),
          day_pv_energy_108: entityFromConfig(ents, 'day_pv_energy_108'),
          day_battery_charge_70: entityFromConfig(ents, 'day_battery_charge_70'),
          day_battery_discharge_71: entityFromConfig(ents, 'day_battery_discharge_71'),
          day_load_energy_84: entityFromConfig(ents, 'day_load_energy_84'),
          day_grid_import_76: entityFromConfig(ents, 'day_grid_import_76'),
          day_grid_export_77: entityFromConfig(ents, 'day_grid_export_77'),
          ...Object.fromEntries(realtimeEntityKeys.map((k) => [k, String(ents[k] || wizardSeed[k] || '')])),
          ...Object.fromEntries(dailyEntityKeys.map((k) => [k, String(ents[k] || wizardSeed[k] || '')])),
          entities_extra_json: JSON.stringify(Object.fromEntries(Object.entries(ents || {}).filter(([k]) => !knownEnergyEntityKeys.includes(String(k)))), null, 2),
        }
      } catch (_) {
        energyWizardForm.value = wizardSeed
      }
      const ov = oj?.overlay || {}
      cfg.value = {
        pathRadiusM: Number(ov?.pathRadiusM ?? cfg.value.pathRadiusM ?? 102),
        sectorRadiusM: Number(ov?.sectorRadiusM ?? cfg.value.sectorRadiusM ?? 110),
        sunRadiusM: Number(ov?.sunRadiusM ?? cfg.value.sunRadiusM ?? 95),
        mapZoom: Number(ov?.mapZoom ?? cfg.value.mapZoom ?? 18),
      }
      if (Number.isFinite(fsForm.value.azimuth)) pvAzimuthDeg.value = fsForm.value.azimuth
      if (!selectedForecastDate.value && fvDayRows.value.length) selectedForecastDate.value = fvDayRows.value[0].date
    } catch (_) {
      // no-op
    }
    if (!selectedShadeId.value && tendeMapShades.value.length) {
      selectShade(shadeKey(tendeMapShades.value[0]))
    } else if (selectedShadeId.value) {
      const ex = tendeMapShades.value.find((s) => shadeKey(s) === selectedShadeId.value || String(s.id || '').trim() === String(selectedShadeId.value || '').trim())
      if (ex) selectShade(shadeKey(ex))
    }
  } finally {
    loadDataInFlight = false
  }
}

async function loadStatusVersion() {
  try {
    const r = await fetch('api/status', { cache: 'no-store' })
    const j = await r.json()
    if (j?.version) appVersion.value = String(j.version)
  } catch (_) {
    // keep fallback
  }
}

function applyLivoltekStatus(payload) {
  if (!payload || typeof payload !== 'object') return
  livoltekStatus.value = payload
  const c = payload.config
  if (c && typeof c === 'object') {
    livoltekForm.value = {
      ...livoltekForm.value,
      enabled: Boolean(c.enabled),
      base_url: String(c.base_url || 'https://evs.livoltek-portal.com'),
      username: String(c.username || ''),
      password: String(c.password || ''),
      token: String(c.token || ''),
      station_id: String(c.station_id || ''),
      device_id: String(c.device_id || ''),
      inverter_sn: String(c.inverter_sn || ''),
      device_serial: String(c.device_serial || ''),
      poll_interval_seconds: Number(c.poll_interval_seconds ?? 300),
      timeout_seconds: Number(c.timeout_seconds ?? 20),
      mqtt_discovery_enabled: Boolean(c.mqtt_discovery_enabled),
    }
  }
}

async function loadLivoltekStatus() {
  try {
    const r = await fetch('api/livoltek/status', { cache: 'no-store' })
    const j = await r.json()
    if (!r.ok || !j.ok) throw new Error(j.error || 'livoltek_status_failed')
    applyLivoltekStatus(j)
  } catch (e) {
    livoltekSaveStatus.value = `Livoltek stato: ${e.message}`
  }
}

async function saveLivoltekConfig() {
  livoltekSaveStatus.value = 'Salvataggio Livoltek...'
  try {
    const payload = {
      enabled: Boolean(livoltekForm.value.enabled),
      base_url: String(livoltekForm.value.base_url || '').trim(),
      username: String(livoltekForm.value.username || '').trim(),
      password: String(livoltekForm.value.password || ''),
      token: String(livoltekForm.value.token || '').trim(),
      station_id: String(livoltekForm.value.station_id || '').trim(),
      device_id: String(livoltekForm.value.device_id || '').trim(),
      inverter_sn: String(livoltekForm.value.inverter_sn || '').trim(),
      device_serial: String(livoltekForm.value.device_serial || '').trim(),
      poll_interval_seconds: Number(livoltekForm.value.poll_interval_seconds ?? 300),
      timeout_seconds: Number(livoltekForm.value.timeout_seconds ?? 20),
      mqtt_discovery_enabled: Boolean(livoltekForm.value.mqtt_discovery_enabled),
    }
    const r = await fetch('api/livoltek/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const j = await r.json()
    if (!r.ok || !j.ok) throw new Error(j.error || 'livoltek_save_failed')
    applyLivoltekStatus({ ...(livoltekStatus.value || {}), ok: true, config: j.config })
    livoltekSaveStatus.value = payload.enabled
      ? 'Livoltek salvato. Il polling parte al prossimo ciclo.'
      : 'Livoltek disabilitato: niente login, polling o MQTT.'
    await loadLivoltekStatus()
  } catch (e) {
    livoltekSaveStatus.value = `Errore Livoltek: ${e.message}`
  }
}

async function runLivoltekAction(endpoint, label) {
  livoltekSaveStatus.value = `${label}...`
  try {
    const r = await fetch(endpoint, { method: 'POST', cache: 'no-store' })
    const j = await r.json()
    if (!r.ok || !j.ok) throw new Error(j.error || `${label}_failed`)
    applyLivoltekStatus(j)
    livoltekSaveStatus.value = `${label} completato.`
  } catch (e) {
    livoltekSaveStatus.value = `${label}: ${e.message}`
    try {
      await loadLivoltekStatus()
    } catch (_) {
      // keep visible error
    }
  }
}

async function refreshLivoltek() {
  await runLivoltekAction('api/livoltek/refresh', 'Refresh Livoltek')
}

async function probeLivoltek() {
  await runLivoltekAction('api/livoltek/probe', 'Probe Livoltek')
}

async function resendLivoltekDiscovery() {
  await runLivoltekAction('api/livoltek/mqtt_discovery', 'MQTT Discovery Livoltek')
}

async function autofillWeatherStationFromDevice() {
  const did = String(weatherStationForm.value.device_id || '').trim()
  if (!did) return
  try {
    const r = await fetch(`api/weather_station/autofill?device_id=${encodeURIComponent(did)}`, { cache: 'no-store' })
    const j = await r.json()
    if (!r.ok || !j?.mapped) throw new Error(j?.error || 'autofill_failed')
    const mapped = j.mapped || {}
    const keys = [
      'wind_speed_entity_id',
      'wind_gust_entity_id',
      'wind_direction_entity_id',
      'rain_rate_entity_id',
      'rain_1h_entity_id',
      'outdoor_temp_entity_id',
      'outdoor_humidity_entity_id',
      'pressure_entity_id',
      'uv_index_entity_id',
      'dewpoint_entity_id',
      'feels_like_entity_id',
      'solar_lux_entity_id',
      'solar_radiation_entity_id',
      'vpd_entity_id',
    ]
    let filled = 0
    for (const k of keys) {
      const v = String(mapped[k] || '').trim()
      if (v && !String(weatherStationForm.value[k] || '').trim()) {
        weatherStationForm.value[k] = v
        filled += 1
      }
    }
    if (filled > 0) baseSaveStatus.value = `Auto-fill device completato: ${filled} campi compilati.`
    else baseSaveStatus.value = 'Auto-fill device: nessun nuovo campo compilato.'
  } catch (e) {
    baseSaveStatus.value = `Auto-fill device errore: ${e.message}`
  }
}

async function saveBaseSettings() {
  baseSaveStatus.value = 'Salvataggio...'
  try {
    // Keep both edit paths aligned before save (wizard + direct fields).
    syncWizardFromEnergyForm()
    applyEnergyWizard()
    const payload = {
      latitude: Number(baseForm.value.latitude),
      longitude: Number(baseForm.value.longitude),
      timezone: String(baseForm.value.timezone || 'Europe/Rome').trim(),
      coordinates_source_mode: String(baseForm.value.coordinates_source_mode || 'e_tende').trim(),
      interval_minutes: Number(baseForm.value.interval_minutes ?? 15),
      location_query: String(baseForm.value.location_query || ''),
      pv_actual_entity_id: String(baseForm.value.pv_actual_entity_id || ''),
      external_temp_entity_id: String(baseForm.value.external_temp_entity_id || ''),
      external_humidity_entity_id: String(baseForm.value.external_humidity_entity_id || ''),
      weather: {
        enabled: Boolean(weatherForm.value.enabled),
        provider: String(weatherForm.value.provider || 'met'),
      },
      weather_station: {
        enabled: Boolean(weatherStationForm.value.enabled),
        provider: 'e_control',
        stale_seconds: Number(weatherStationForm.value.stale_seconds ?? 180),
        device_id: String(weatherStationForm.value.device_id || ''),
        wind_speed_entity_id: String(weatherStationForm.value.wind_speed_entity_id || ''),
        wind_gust_entity_id: String(weatherStationForm.value.wind_gust_entity_id || ''),
        wind_direction_entity_id: String(weatherStationForm.value.wind_direction_entity_id || ''),
        rain_rate_entity_id: String(weatherStationForm.value.rain_rate_entity_id || ''),
        rain_1h_entity_id: String(weatherStationForm.value.rain_1h_entity_id || ''),
        outdoor_temp_entity_id: String(weatherStationForm.value.outdoor_temp_entity_id || ''),
        outdoor_humidity_entity_id: String(weatherStationForm.value.outdoor_humidity_entity_id || ''),
        pressure_entity_id: String(weatherStationForm.value.pressure_entity_id || ''),
        uv_index_entity_id: String(weatherStationForm.value.uv_index_entity_id || ''),
        dewpoint_entity_id: String(weatherStationForm.value.dewpoint_entity_id || ''),
        feels_like_entity_id: String(weatherStationForm.value.feels_like_entity_id || ''),
        solar_lux_entity_id: String(weatherStationForm.value.solar_lux_entity_id || ''),
        solar_radiation_entity_id: String(weatherStationForm.value.solar_radiation_entity_id || ''),
        vpd_entity_id: String(weatherStationForm.value.vpd_entity_id || ''),
      },
      weather_guard: {
        enabled: Boolean(weatherGuardForm.value.enabled),
        wind_alarm_ms: Number(weatherGuardForm.value.wind_alarm_ms ?? 12.0),
        rain_alarm_mm_h: Number(weatherGuardForm.value.rain_alarm_mm_h ?? 1.5),
        facade_rain_min_wind_ms: Number(weatherGuardForm.value.facade_rain_min_wind_ms ?? 6.0),
        facade_rain_min_mm_h: Number(weatherGuardForm.value.facade_rain_min_mm_h ?? 0.8),
        facade_azimuth_deg: Number(weatherGuardForm.value.facade_azimuth_deg ?? -1.0),
        facade_half_fov_deg: Number(weatherGuardForm.value.facade_half_fov_deg ?? 60.0),
        stale_seconds: Number(weatherGuardForm.value.stale_seconds ?? 180),
      },
      air_quality: {
        enabled: Boolean(airQualityForm.value.enabled),
        provider: String(airQualityForm.value.provider || 'open_meteo'),
      },
      tende_map: {
        enabled: Boolean(tendeMapForm.value.enabled),
        mqtt_host: String(tendeMapForm.value.mqtt_host || ''),
        mqtt_port: Number(tendeMapForm.value.mqtt_port ?? 1883),
        mqtt_username: String(tendeMapForm.value.mqtt_username || ''),
        mqtt_password: String(tendeMapForm.value.mqtt_password || ''),
        topic_state: String(tendeMapForm.value.topic_state || ''),
        topic_availability: String(tendeMapForm.value.topic_availability || ''),
        stale_seconds: Number(tendeMapForm.value.stale_seconds ?? 180),
      },
      energy: buildEnergyPayload(),
    }
    const r = await fetch('api/options/base', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const j = await r.json()
    if (!r.ok || !j.ok) throw new Error(j.error || 'save_failed')
    baseSaveStatus.value = 'Salvato e applicato.'
    await loadData()
  } catch (e) {
    baseSaveStatus.value = `Errore salvataggio: ${e.message}`
  }
}

async function saveAllSettings() {
  allSaveStatus.value = 'Salvataggio...'
  baseSaveStatus.value = ''
  fsSaveStatus.value = ''
  overlaySaveStatus.value = ''
  try {
    // Keep both edit paths aligned before save (wizard + direct fields).
    syncWizardFromEnergyForm()
    applyEnergyWizard()
    const basePayload = {
      latitude: Number(baseForm.value.latitude),
      longitude: Number(baseForm.value.longitude),
      timezone: String(baseForm.value.timezone || 'Europe/Rome').trim(),
      coordinates_source_mode: String(baseForm.value.coordinates_source_mode || 'e_tende').trim(),
      interval_minutes: Number(baseForm.value.interval_minutes ?? 15),
      location_query: String(baseForm.value.location_query || ''),
      pv_actual_entity_id: String(baseForm.value.pv_actual_entity_id || ''),
      external_temp_entity_id: String(baseForm.value.external_temp_entity_id || ''),
      external_humidity_entity_id: String(baseForm.value.external_humidity_entity_id || ''),
      weather: {
        enabled: Boolean(weatherForm.value.enabled),
        provider: String(weatherForm.value.provider || 'met'),
      },
      weather_station: {
        enabled: Boolean(weatherStationForm.value.enabled),
        provider: 'e_control',
        stale_seconds: Number(weatherStationForm.value.stale_seconds ?? 180),
        device_id: String(weatherStationForm.value.device_id || ''),
        wind_speed_entity_id: String(weatherStationForm.value.wind_speed_entity_id || ''),
        wind_gust_entity_id: String(weatherStationForm.value.wind_gust_entity_id || ''),
        wind_direction_entity_id: String(weatherStationForm.value.wind_direction_entity_id || ''),
        rain_rate_entity_id: String(weatherStationForm.value.rain_rate_entity_id || ''),
        rain_1h_entity_id: String(weatherStationForm.value.rain_1h_entity_id || ''),
        outdoor_temp_entity_id: String(weatherStationForm.value.outdoor_temp_entity_id || ''),
        outdoor_humidity_entity_id: String(weatherStationForm.value.outdoor_humidity_entity_id || ''),
        pressure_entity_id: String(weatherStationForm.value.pressure_entity_id || ''),
        uv_index_entity_id: String(weatherStationForm.value.uv_index_entity_id || ''),
        dewpoint_entity_id: String(weatherStationForm.value.dewpoint_entity_id || ''),
        feels_like_entity_id: String(weatherStationForm.value.feels_like_entity_id || ''),
        solar_lux_entity_id: String(weatherStationForm.value.solar_lux_entity_id || ''),
        solar_radiation_entity_id: String(weatherStationForm.value.solar_radiation_entity_id || ''),
        vpd_entity_id: String(weatherStationForm.value.vpd_entity_id || ''),
      },
      weather_guard: {
        enabled: Boolean(weatherGuardForm.value.enabled),
        wind_alarm_ms: Number(weatherGuardForm.value.wind_alarm_ms ?? 12.0),
        rain_alarm_mm_h: Number(weatherGuardForm.value.rain_alarm_mm_h ?? 1.5),
        facade_rain_min_wind_ms: Number(weatherGuardForm.value.facade_rain_min_wind_ms ?? 6.0),
        facade_rain_min_mm_h: Number(weatherGuardForm.value.facade_rain_min_mm_h ?? 0.8),
        facade_azimuth_deg: Number(weatherGuardForm.value.facade_azimuth_deg ?? -1.0),
        facade_half_fov_deg: Number(weatherGuardForm.value.facade_half_fov_deg ?? 60.0),
        stale_seconds: Number(weatherGuardForm.value.stale_seconds ?? 180),
      },
      air_quality: {
        enabled: Boolean(airQualityForm.value.enabled),
        provider: String(airQualityForm.value.provider || 'open_meteo'),
      },
      tende_map: {
        enabled: Boolean(tendeMapForm.value.enabled),
        mqtt_host: String(tendeMapForm.value.mqtt_host || ''),
        mqtt_port: Number(tendeMapForm.value.mqtt_port ?? 1883),
        mqtt_username: String(tendeMapForm.value.mqtt_username || ''),
        mqtt_password: String(tendeMapForm.value.mqtt_password || ''),
        topic_state: String(tendeMapForm.value.topic_state || ''),
        topic_availability: String(tendeMapForm.value.topic_availability || ''),
        stale_seconds: Number(tendeMapForm.value.stale_seconds ?? 180),
      },
      energy: buildEnergyPayload(),
    }
    const overlayPayload = {
      pathRadiusM: Number(cfg.value.pathRadiusM ?? 102),
      sectorRadiusM: Number(cfg.value.sectorRadiusM ?? 110),
      sunRadiusM: Number(cfg.value.sunRadiusM ?? 95),
      mapZoom: Number(cfg.value.mapZoom ?? 18),
    }
    const forecastPayload = {
      enabled: Boolean(fsForm.value.enabled),
      api_key: String(fsForm.value.api_key || ''),
      declination: Number(fsForm.value.declination ?? 30),
      azimuth: Number(fsForm.value.azimuth ?? 0),
      kwp: Number(fsForm.value.kwp ?? 6.0),
    }
    const steps = [
      ['api/options/base', basePayload],
      ['api/options/overlay', overlayPayload],
      ['api/options/forecast_solar', forecastPayload],
    ]
    for (const [url, payload] of steps) {
      const r = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const j = await r.json()
      if (!r.ok || !j.ok) throw new Error(`${url}: ${j.error || 'save_failed'}`)
    }
    allSaveStatus.value = 'Tutto salvato e applicato.'
    await loadData()
  } catch (e) {
    allSaveStatus.value = `Errore salvataggio: ${e.message}`
  }
}

async function saveForecastSettings() {
  fsSaveStatus.value = 'Salvataggio...'
  try {
    const payload = {
      enabled: Boolean(fsForm.value.enabled),
      api_key: String(fsForm.value.api_key || ''),
      declination: Number(fsForm.value.declination ?? 30),
      azimuth: Number(fsForm.value.azimuth ?? 0),
      kwp: Number(fsForm.value.kwp ?? 6.0),
    }
    const r = await fetch('api/options/forecast_solar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const j = await r.json()
    if (!r.ok || !j.ok) throw new Error(j.error || 'save_failed')
    const urlNow = j?.forecast_url_now ? ` URL: ${j.forecast_url_now}` : ''
    fsSaveStatus.value = `Salvato e applicato subito.${urlNow}`
    await loadData()
  } catch (e) {
    fsSaveStatus.value = `Errore salvataggio: ${e.message}`
  }
}

async function saveOverlaySettings() {
  overlaySaveStatus.value = 'Salvataggio...'
  try {
    const payload = {
      pathRadiusM: Number(cfg.value.pathRadiusM ?? 102),
      sectorRadiusM: Number(cfg.value.sectorRadiusM ?? 110),
      sunRadiusM: Number(cfg.value.sunRadiusM ?? 95),
      mapZoom: Number(cfg.value.mapZoom ?? 18),
    }
    const r = await fetch('api/options/overlay', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const j = await r.json()
    if (!r.ok || !j.ok) throw new Error(j.error || 'save_failed')
    overlaySaveStatus.value = 'Tarature overlay salvate.'
    await loadData()
  } catch (e) {
    overlaySaveStatus.value = `Errore salvataggio overlay: ${e.message}`
  }
}

onMounted(() => {
  try {
    const qp = new URLSearchParams(window.location.search || '')
    const view = String(qp.get('view') || '').trim().toLowerCase()
    if (view === 'user' || view === 'ui-user' || view === 'user_public') tab.value = 'user_public'
    if (view === 'energy' || view === 'ui-energy') tab.value = 'energy'
    if (view === 'energy_public') tab.value = 'energy_public'
    if (view === 'livoltek') tab.value = 'livoltek'
    if (view === 'energy_setup' || view === 'energy-setup' || view === 'ui-energy-setup') {
      tab.value = 'energy_setup'
    }
  } catch (_) {
    // no-op
  }
  // Failsafe splash: disabled on UI User for WebView stability.
  setTimeout(() => {
    showSplash.value = false
  }, (tab.value === 'user_public' || tab.value === 'energy_public') ? 0 : 1200)
  try {
    const now = new Date()
    const total = (now.getHours() * 60) + now.getMinutes()
    const base = 3 * 60
    const clamped = Math.max(base, Math.min(21 * 60, total))
    const rounded = Math.round((clamped - base) / 15)
    const idx = rounded
    if (idx >= 0) timeIndex.value = idx
    loadData()
    loadStatusVersion()
    loadLivoltekStatus()
    window.addEventListener('resize', resizeWeatherCanvas)
    startWeatherAnimation()
    initBlockToggles()
    userAutoRefreshTimer = setInterval(() => {
      if (tab.value === 'user' || tab.value === 'user_public' || tab.value === 'energy_public') loadData()
    }, userAutoRefreshMs)
  } catch (e) {
    console.error('onMounted init error', e)
    showSplash.value = false
  }
})
onBeforeUnmount(() => {
  if (map) { map.remove(); map = null }
  if (tendeMapObj) { tendeMapObj.remove(); tendeMapObj = null }
  clearMainMapRetry()
  if (windLayerRetryTimer) {
    clearTimeout(windLayerRetryTimer)
    windLayerRetryTimer = 0
  }
  if (userAutoRefreshTimer) {
    clearInterval(userAutoRefreshTimer)
    userAutoRefreshTimer = 0
  }
  stopWeatherAnimation()
  window.removeEventListener('resize', resizeWeatherCanvas)
})

watch(tab, async (val) => {
  if (val === 'user') {
    await ensureMainMapReady('tab_user')
    if (!map) return
    initBlockToggles()
    try { map.invalidateSize() } catch (_) {}
    drawSolarOverlay()
    resizeWeatherCanvas()
    if (weatherAnimEnabled.value) startWeatherAnimation()
  } else if (val === 'tende') {
    await nextTick()
    ensureTendeMap()
    if (tendeMapObj && lat.value != null && lon.value != null) {
      tendeMapObj.setView([lat.value, lon.value], cfg.value.mapZoom)
      tendeMapObj.invalidateSize()
      if (!selectedShadeId.value && tendeMapShades.value.length) selectShade(shadeKey(tendeMapShades.value[0]))
      else drawTendeEditor()
    }
  } else if (val === 'user_public') {
    await ensureMainMapReady('tab_user_public')
    if (map) {
      try { map.invalidateSize() } catch (_) {}
    }
  } else if (val === 'livoltek') {
    await loadLivoltekStatus()
  } else {
    clearMainMapRetry()
    stopWeatherAnimation()
  }
})

watch(weatherAnimEnabled, (enabled) => {
  if (enabled && tab.value === 'user') startWeatherAnimation()
  else stopWeatherAnimation()
})
watch([mapWindDirDeg, mapWindMs], ([dir, speed]) => {
  if (Number.isFinite(Number(dir))) lastKnownWindDirDeg.value = Number(dir)
  if (Number.isFinite(Number(speed))) lastKnownWindMs.value = Number(speed)
}, { immediate: true })
watch(showWindDirectionOnMap, async () => {
  if (tab.value !== 'user') return
  await nextTick()
  ensureWindDirectionLayer()
  setTimeout(() => {
    if (tab.value === 'user') ensureWindDirectionLayer()
  }, 120)
})
watch([mapWindDirDeg, mapWindMs], async () => {
  if (tab.value !== 'user') return
  await nextTick()
  ensureWindDirectionLayer()
})
</script>

<style>
:root{--bg:#070a0f;--muted:#9fb0c7;--text:#e8f1ff;--accent:#57e3d6;--border:rgba(255,255,255,.08)}
*{box-sizing:border-box}
body{margin:0;font-family:"Space Grotesk","IBM Plex Sans","Trebuchet MS",sans-serif;background:var(--bg);color:var(--text)}
.wrap{min-height:100dvh;display:flex;flex-direction:column}
.splash-screen{
  position:fixed;
  inset:0;
  z-index:9999;
  display:flex;
  align-items:center;
  justify-content:center;
  background:
    radial-gradient(circle at center, rgba(255,233,140,.22), rgba(7,10,15,.82) 60%),
    rgba(7,10,15,.65);
  backdrop-filter: blur(2px);
}
.splash-logo{
  width:min(70vw,300px);
  display:block;
  height:auto;
  filter:drop-shadow(0 0 28px rgba(255,214,82,.45));
}
.splash-fade-enter-active,.splash-fade-leave-active{transition:opacity .6s ease}
.splash-fade-enter-from,.splash-fade-leave-to{opacity:0}
.splash-fade-enter-to,.splash-fade-leave-from{opacity:1}
.topbar{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-bottom:1px solid var(--border);background:rgba(10,15,22,.9)}
.brand{font-weight:700;display:flex;align-items:center;gap:8px}
.brand-logo{width:28px;height:28px;object-fit:contain;border-radius:6px}
.brand-version{font-weight:600;opacity:.85}
.actions{display:flex;gap:8px;align-items:center}
.btn{background:linear-gradient(135deg, var(--accent), #6cf1c9);border:none;color:#062524;padding:6px 12px;border-radius:999px;font-weight:700;cursor:pointer}
.btn.ghost{background:transparent;border:1px solid var(--border);color:var(--text)}
.btn.ghost.active{border-color:var(--accent);color:#cffff5}
.timeline{padding:8px 12px;background:#232830;border-bottom:1px solid #3b4048}
.map-block-group{
  position:relative;
}
.map-group-title{
  padding:8px 12px;
  font-size:12px;
  font-weight:700;
  color:#dfe8f6;
  background:#1b2028;
  border-bottom:1px solid #2f3640;
}
.view-tools{display:none}
.collapsible-block{
  position:relative;
}
.block-toggle-inline{
  position:absolute;
  top:2px;
  left:2px;
  z-index:2;
  cursor:pointer;
  user-select:none;
  width:34px;
  height:24px;
  border:none;
  border-radius:6px;
  background:transparent;
  color:transparent;
}
.collapsible-block.is-collapsed > :not(.block-toggle-inline):not(:nth-child(2)){
  display:none !important;
}
.map-wrap.collapsible-block.is-collapsed > :not(.block-toggle-inline):not(.map-block-title){
  display:none !important;
}
.map-wrap.collapsible-block.is-collapsed{
  height:62px;
  min-height:62px;
}
.time-labels{display:grid;grid-template-columns:repeat(19,1fr);font-size:11px;color:#c9d2df;gap:4px;margin-bottom:4px}
input[type='range']{width:100%}
.time-meta{font-size:12px;color:#dfe8f6;margin-top:4px}
.toggles{display:flex;gap:14px;margin-top:6px;font-size:12px;color:#dfe8f6}
.toggles label{display:flex;align-items:center;gap:6px}
.pv-az-controls{display:flex;align-items:center;gap:10px;margin-top:8px;font-size:12px;color:#dfe8f6}
.pv-az-controls label{display:flex;align-items:center;gap:8px;min-width:280px}
.pv-az-controls input[type='range']{width:220px}
.pv-az-input{width:84px;padding:6px 8px;border-radius:8px;border:1px solid var(--border);background:#0f1621;color:var(--text)}
.pv-az-value{min-width:70px;color:#ffd7a8}
.fv-icon-wrap{background:transparent;border:none}
.fv-icon{
  display:inline-block;
  padding:2px 6px;
  border-radius:8px;
  font-size:10px;
  font-weight:700;
  color:#092018;
  background:linear-gradient(180deg,#7bf7d5,#2dd4bf);
  border:1px solid rgba(175,255,240,.8);
  box-shadow:0 0 8px rgba(45,212,191,.45);
}
.map-wrap{height:68vh;min-height:420px}
#solar-map{width:100%;height:100%}
.map-wrap{position:relative}
.map-block-title{
  position:absolute;
  top:8px;
  left:44px;
  z-index:510;
  font-size:12px;
  font-weight:700;
  color:#dfe8f6;
  padding:3px 8px;
  border-radius:8px;
  border:1px solid rgba(170,210,255,.35);
  background:rgba(8,16,26,.68);
}
.weather-overlay-canvas{
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  pointer-events:none;
  z-index:450;
  mix-blend-mode:normal;
  opacity:.48;
}
.wind-compass-chip{
  position:absolute;
  top:10px;
  right:10px;
  z-index:520;
  display:flex;
  align-items:center;
  gap:8px;
  padding:6px 10px;
  border-radius:10px;
  border:1px solid rgba(130,200,255,.45);
  background:rgba(8,18,30,.72);
  color:#d7ecff;
  font-size:12px;
  font-weight:700;
  backdrop-filter: blur(2px);
}
.tende-badge{
  position:absolute;
  top:10px;
  right:10px;
  z-index:420;
  background:rgba(114, 28, 36, .86);
  color:#ffd9de;
  border:1px solid rgba(255, 180, 190, .45);
  border-radius:10px;
  padding:6px 10px;
  font-size:12px;
  font-weight:700;
}
.wind-compass-arrow{
  display:inline-block;
  width:18px;
  height:18px;
  line-height:18px;
  text-align:center;
  color:#5ee7ff;
  text-shadow:0 0 8px rgba(94,231,255,.55);
}
.wind-map-icon-wrap{background:transparent;border:none}
.wind-map-icon{
  display:inline-block;
  color:#5ee7ff;
  font-size:14px;
  font-weight:800;
  text-shadow:0 0 8px rgba(94,231,255,.6);
  margin-right:4px;
}
.wind-map-label{
  color:#d7ecff;
  font-size:11px;
  font-weight:700;
  text-shadow:0 1px 2px rgba(0,0,0,.8);
}
.user-public{padding:10px;background:radial-gradient(circle at top,#0d2035 0%,#081422 42%,#060d17 100%);min-height:calc(100dvh - 56px)}
.user-public-head{display:flex;justify-content:center;align-items:center;border:1px solid rgba(255,210,80,.25);border-radius:14px;padding:12px 16px;background:linear-gradient(90deg,rgba(3,10,18,.9),rgba(6,18,31,.88));min-height:190px}
.up-brand{display:flex;align-items:center;justify-content:center;width:100%}
.up-logo{width:1040px;max-width:96vw;height:168px;object-fit:contain;display:block}
.up-brand-text{font-size:42px;font-weight:700;color:#e8f2ff;line-height:.95}
.up-brand-text span{color:#ffc840}
.user-public-main{display:grid;grid-template-columns:270px 1fr;gap:10px;margin-top:10px}
.up-side{border:1px solid rgba(133,175,220,.22);border-radius:12px;background:rgba(5,14,25,.72);padding:12px;display:grid;gap:10px;align-content:start}
.up-side h3{margin:0;color:#e8f2ff}
.up-legend-item{display:grid;grid-template-columns:12px 1fr;gap:10px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.07)}
.dot{width:12px;height:12px;border-radius:999px;align-self:start;box-shadow:0 0 10px rgba(255,255,255,.25)}
.up-legend-body{display:grid;gap:2px}
.up-legend-body strong{color:#f7fbff}
.up-legend-body span{color:#9fbbd8;font-size:13px}
.up-legend-body small{color:#8aa2bb;font-size:12px}
.up-wind{margin-top:6px;padding:10px;border-radius:10px;border:1px solid rgba(74,188,255,.34);background:rgba(8,24,38,.55);display:grid;gap:2px}
.up-wind strong{color:#66d2ff}
.up-wind span{color:#b8dcff}
.up-map-wrap{border:1px solid rgba(133,175,220,.22);border-radius:12px;overflow:hidden;background:rgba(4,12,22,.8);min-height:520px}
#solar-map-public{height:100%;min-height:520px}
.up-map-controls{margin-top:14px;padding:10px 12px;border:1px solid rgba(133,175,220,.22);border-radius:12px;background:rgba(5,14,25,.72)}
.up-time-sim{margin-bottom:8px}
.user-public .time-labels{display:grid;grid-template-columns:repeat(19,1fr);font-size:11px;color:#c9d2df;gap:4px;margin-bottom:4px}
.up-bottom{display:grid;grid-template-columns:repeat(4,minmax(220px,1fr));gap:10px;margin-top:10px}
.up-card{border:1px solid rgba(133,175,220,.22);border-radius:12px;background:rgba(5,14,25,.72);padding:12px;color:#b8cce3;display:grid;gap:6px}
.up-card h4{margin:0 0 4px 0;color:#e8f2ff}
.up-card strong{color:#fff}
.energy-public{
  padding:14px;
  background:linear-gradient(180deg,#f2f4f8 0%,#ebedf2 100%);
  min-height:100dvh;
  color:#1f2733;
}
.energy-page-head{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
  margin-bottom:14px;
  padding:12px 14px;
  border:1px solid #d6dbe5;
  border-radius:12px;
  background:#fff;
}
.energy-page-head h2{
  margin:0;
  font-size:24px;
  letter-spacing:0;
  color:#121926;
}
.energy-page-head p{
  margin:3px 0 0;
  color:#5b6574;
}
.energy-hero{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:12px;
}
.energy-status{
  font-size:18px;
  font-weight:700;
}
.energy-temp{
  font-size:32px;
  font-weight:700;
}
.energy-flow-board{
  position:relative;
  border:1px solid #d6dbe5;
  border-radius:14px;
  background:linear-gradient(180deg,#f5f6f8 0%,#f0f1f4 100%);
  min-height:360px;
  margin-bottom:12px;
  overflow:hidden;
}
.ef-link{
  position:absolute;
  border:2px solid #cfd7e9;
  border-radius:18px;
  opacity:.9;
}
.ef-link-bat{
  left:140px;
  top:90px;
  width:190px;
  height:150px;
  border-right:none;
  border-bottom:none;
}
.ef-link-grid{
  right:220px;
  top:90px;
  width:190px;
  height:150px;
  border-left:none;
  border-bottom:none;
}
.ef-link-home{
  left:308px;
  top:150px;
  width:2px;
  height:78px;
  background:#cfd7e9;
  border:none;
}
.ef-node{
  position:absolute;
  border:1px solid #d6dbe5;
  border-radius:12px;
  background:#fff;
  padding:10px 12px;
  min-width:110px;
  box-shadow:0 4px 12px rgba(16,24,40,.06);
}
.ef-node .ef-icon{font-size:20px;opacity:.85}
.ef-node .ef-name{font-size:12px;color:#5b6574;margin-top:3px}
.ef-node .ef-val{font-size:30px;font-weight:700;letter-spacing:-.4px;line-height:1.1}
.ef-node .ef-sub{font-size:12px;color:#5b6574}
.ef-node-pv{left:255px;top:44px}
.ef-node-home{left:255px;top:180px}
.ef-node-grid{left:430px;top:222px}
.ef-node-bat{left:85px;top:222px}
.ef-kpi-side{
  position:absolute;
  right:26px;
  top:128px;
  width:250px;
  display:grid;
  gap:10px;
}
.ef-kpi{
  border:1px solid #d6dbe5;
  border-radius:12px;
  background:#fff;
  padding:10px 12px;
  display:grid;
  gap:3px;
}
.ef-kpi span{font-size:12px;color:#5b6574}
.ef-kpi strong{font-size:28px;color:#121926}
.energy-kpi-grid{
  display:grid;
  grid-template-columns:repeat(3,minmax(220px,1fr));
  gap:10px;
}
.energy-kpi{
  border:1px solid #d6dbe5;
  border-radius:12px;
  background:#ffffff;
  padding:12px 14px;
  display:grid;
  gap:4px;
}
.energy-kpi span{
  color:#5b6574;
  font-size:13px;
}
.energy-kpi strong{
  color:#121926;
  font-size:28px;
  letter-spacing:-.4px;
}
.energy-site-link-grid{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:10px;
  margin-top:12px;
}
.energy-site-link{
  text-decoration:none;
  border:1px solid #d6dbe5;
  border-radius:12px;
  background:#fff;
  color:#121926;
  padding:12px 14px;
  display:grid;
  gap:4px;
}
.energy-site-link strong{font-size:16px}
.energy-site-link span{font-size:13px;color:#5b6574}
.energy-theme-technical_dark{
  background:radial-gradient(circle at top,#14273d 0%,#0a1320 48%,#060c15 100%);
  color:#d9e8ff;
}
.energy-theme-technical_dark .energy-page-head{
  background:#0f1b2e;
  border-color:#355377;
}
.energy-theme-technical_dark .energy-page-head h2{
  color:#f2f7ff;
}
.energy-theme-technical_dark .energy-page-head p{
  color:#9fb7d3;
}
.energy-theme-technical_dark .energy-flow-board{
  background:linear-gradient(180deg,#0f1b2e 0%,#0a1422 100%);
  border-color:#355377;
}
.energy-theme-technical_dark .ef-link,
.energy-theme-technical_dark .ef-link-home{
  border-color:#476991;
  background:#476991;
}
.energy-theme-technical_dark .ef-node,
.energy-theme-technical_dark .ef-kpi,
.energy-theme-technical_dark .energy-kpi,
.energy-theme-technical_dark .energy-site-link{
  background:#0d1a2b;
  border-color:#355377;
  box-shadow:none;
}
.energy-theme-technical_dark .ef-node .ef-name,
.energy-theme-technical_dark .ef-node .ef-sub,
.energy-theme-technical_dark .ef-kpi span,
.energy-theme-technical_dark .energy-kpi span,
.energy-theme-technical_dark .energy-site-link span{
  color:#9cb7d8;
}
.energy-theme-technical_dark .ef-node .ef-val,
.energy-theme-technical_dark .ef-kpi strong,
.energy-theme-technical_dark .energy-kpi strong,
.energy-theme-technical_dark .energy-site-link strong{
  color:#eef6ff;
}
.energy-theme-technical_dark .energy-status,
.energy-theme-technical_dark .energy-temp{
  color:#eef6ff;
}
.energy-theme-minimal_light .energy-flow-board{
  background:#ffffff;
}
.energy-theme-minimal_light .ef-node,
.energy-theme-minimal_light .ef-kpi,
.energy-theme-minimal_light .energy-kpi{
  box-shadow:none;
}
.panel{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px;padding:10px;background:#111722;border-top:1px solid var(--border)}
.kpi{border:1px solid var(--border);border-radius:10px;padding:8px;background:rgba(10,15,22,.7);font-size:13px}
.source-panel{grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:10px;align-items:start}
.source-card{border:1px solid var(--border);border-radius:12px;background:linear-gradient(180deg,rgba(10,16,24,.86),rgba(7,12,19,.82));padding:10px;display:grid;gap:8px;align-content:start}
.source-card h4{margin:0;color:#d8ecff;font-size:15px;letter-spacing:.2px;border-bottom:1px solid rgba(146,196,255,.18);padding-bottom:6px}
.source-head{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.chip{display:inline-flex;align-items:center;padding:4px 8px;border-radius:999px;border:1px solid rgba(175,210,255,.28);background:rgba(20,30,45,.55);font-size:12px;color:#dbeeff}
.chip-ok{border-color:rgba(90,220,160,.45);color:#c8ffe3}
.chip-bad{border-color:rgba(255,115,115,.45);color:#ffd4d4}
.metric-grid{display:grid;grid-template-columns:1fr;gap:6px;align-content:start}
.metric-grid--compact{max-height:260px;overflow:auto;padding-right:4px}
.metric-row{display:flex;justify-content:space-between;gap:10px;padding:8px 10px;border:1px solid rgba(255,255,255,.08);border-radius:9px;background:rgba(11,18,28,.64)}
.metric-key{color:#a9bed6;font-size:12px}
.metric-val{color:#f0f7ff;font-weight:600;font-size:13px;text-align:right}
.guard-line{padding:8px 10px;border:1px dashed rgba(130,180,235,.35);border-radius:9px;background:rgba(18,28,40,.4);font-size:12px;color:#d8e8f8}
.station-all-details summary{cursor:pointer;color:#cde5ff;font-size:12px}
.station-all-details[open] summary{margin-bottom:6px}
.tech-main{padding:14px;display:grid;gap:12px}
.card{border:1px solid var(--border);border-radius:14px;padding:12px;background:rgba(10,15,22,.75)}
.form-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}
label{display:flex;flex-direction:column;gap:6px;font-size:12px;color:var(--muted)}
input{padding:8px;border-radius:8px;border:1px solid var(--border);background:#0f1621;color:var(--text)}
.mono{font-family:Consolas,Monaco,monospace}
.livoltek-title-row{display:flex;align-items:flex-start;justify-content:space-between;gap:14px}
.switch-line{display:flex;flex-direction:row;align-items:center;gap:8px;white-space:nowrap;color:var(--text)}
.raw-json{white-space:pre-wrap;word-break:break-word;background:#0c141b;border:1px solid var(--border);border-radius:8px;padding:10px;max-height:520px;overflow:auto}
.small{font-size:12px}
.note{font-size:12px;color:var(--muted)}
.json{white-space:pre-wrap;word-break:break-word;background:#0c141b;border:1px solid var(--border);border-radius:10px;padding:10px;max-height:420px;overflow:auto}
.chart-kpi{grid-column:1 / -1}
.fv-chart{width:100%;height:250px;display:block;margin-top:8px;border:1px solid var(--border);border-radius:8px;background:rgba(12,20,28,.7)}
.weather-chart{width:100%;height:270px;display:block;margin-top:8px;border:1px solid var(--border);border-radius:8px;background:rgba(12,20,28,.7)}
.airq-chart{width:100%;height:270px;display:block;margin-top:8px;border:1px solid var(--border);border-radius:8px;background:rgba(12,20,28,.7)}
.chart-axis{stroke:#607086;stroke-width:1}
.chart-grid{stroke:#2d3b4d;stroke-width:.8;opacity:.55}
.chart-grid-v{stroke:#243244;stroke-width:.8;opacity:.4}
.chart-line{fill:none;stroke:#f2c235;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}
.weather-temp-line{fill:none;stroke:#f2c235;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}
.weather-temp-dot{fill:#ffe68f;stroke:#f2c235;stroke-width:1}
.weather-real-temp-line{fill:none;stroke:#ff4dc4;stroke-width:2;stroke-dasharray:7,4;opacity:.95}
.weather-wind-line{fill:none;stroke:#36d5ff;stroke-width:2;stroke-dasharray:5,4;stroke-linecap:round;stroke-linejoin:round;opacity:.95}
.weather-wind-dot{fill:#8cecff;stroke:#36d5ff;stroke-width:.9}
.weather-humidity-line{fill:none;stroke:#6ee7b7;stroke-width:1.8;stroke-dasharray:3,3;opacity:.9}
.weather-humidity-dot{fill:#b8f8df;stroke:#6ee7b7;stroke-width:.8}
.weather-pressure-line{fill:none;stroke:#a78bfa;stroke-width:1.8;stroke-dasharray:2,4;opacity:.9}
.weather-pressure-dot{fill:#ddd6fe;stroke:#a78bfa;stroke-width:.8}
.weather-rain-bar{fill:rgba(45,212,191,.46);stroke:rgba(125,242,228,.65);stroke-width:.8}
.airq-eu-line{fill:none;stroke:#f2c235;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.airq-pm25-line{fill:none;stroke:#4ad2ff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;opacity:.95}
.airq-pm10-line{fill:none;stroke:#ff9f43;stroke-width:2;stroke-dasharray:6,4;stroke-linecap:round;stroke-linejoin:round;opacity:.95}
.axis-label-y-right-rain{text-anchor:start;fill:#7df2e4}
.axis-label-y-right-wind{text-anchor:start;fill:#8cecff}
.axis-title-wind{fill:#8cecff}
.chart-now{stroke:#2dd4bf;stroke-width:1.5;stroke-dasharray:6,5}
.chart-hover-line{stroke:#e5edf8;stroke-width:1.2;stroke-dasharray:3,4;opacity:.85}
.chart-hover-dot{fill:#ffffff;stroke:#f2c235;stroke-width:2}
.chart-tip-bg{fill:rgba(8,14,22,.92);stroke:#5f738d;stroke-width:1}
.chart-tip-t1{fill:#dfe8f6;font-size:8px;font-weight:700}
.chart-tip-t2{fill:#f2c235;font-size:8px;font-weight:700}
.axis-label-y{fill:#9fb0c7;font-size:6.5px;text-anchor:end;font-weight:600}
.axis-label-x{fill:#9fb0c7;font-size:6.5px;text-anchor:middle;font-weight:600}
.axis-label-x-strong{fill:#dfe8f6;font-size:7px;font-weight:700}
.axis-title{fill:#c9d4e2;font-size:7px;font-weight:700}
.axis-title-x{fill:#c9d4e2;font-size:7px;font-weight:700;text-anchor:end}
.chart-meta{margin-top:6px;font-size:12px;color:var(--muted)}
.weather-x-hours{
  margin-top:4px;
  display:flex;
  justify-content:space-between;
  gap:8px;
  padding:0 46px 0 54px;
  color:#dfe8f6;
  font-size:11px;
  font-weight:700;
}
.weather-x-hours span{
  min-width:34px;
  text-align:center;
}
.bar-chart-area{
  display:flex;
  gap:10px;
  align-items:flex-end;
}
.bar-y-axis{
  height:140px;
  min-width:44px;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
  align-items:flex-end;
  color:#9fb0c7;
  font-size:11px;
  padding-bottom:2px;
}
.bar-y-tick{
  line-height:1;
}
.day-bars{
  margin-top:10px;
  display:flex;
  flex-wrap:nowrap;
  overflow-x:auto;
  overflow-y:visible;
  gap:8px;
  align-items:end;
  padding-bottom:2px;
}
.day-bar-item{
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:6px;
  flex:0 0 72px;
}
.day-bar-wrap{
  position:relative;
  width:100%;
  height:140px;
  border:1px solid var(--border);
  border-radius:8px;
  background:rgba(10,16,24,.65);
  display:flex;
  align-items:flex-end;
  justify-content:center;
  padding:4px;
}
.day-bar{
  width:70%;
  border-radius:6px 6px 3px 3px;
  background:linear-gradient(180deg,#f7cf44,#e89f10);
  box-shadow:0 0 10px rgba(242,194,53,.35);
}
.day-bar-label{font-size:11px;color:var(--muted);text-transform:capitalize}
.bar-tooltip{
  position:absolute;
  left:50%;
  transform:translateX(-50%);
  top:6px;
  background:rgba(8,14,22,.95);
  border:1px solid #5f738d;
  border-radius:8px;
  padding:4px 8px;
  font-size:11px;
  color:#dfe8f6;
  white-space:nowrap;
  pointer-events:none;
  z-index:5;
}
.day-table{
  width:100%;
  border-collapse:collapse;
  margin-top:10px;
  font-size:13px;
}
.day-table th,.day-table td{
  border-bottom:1px solid var(--border);
  padding:8px 6px;
  text-align:left;
}
.day-table th{color:#cdd9ea;font-weight:700}
.actions-inline{display:flex;align-items:center;gap:10px;margin:10px 0}
.cardinal{
  color:#d8e1eb;
  font-size:11px;
  font-weight:700;
  text-shadow:0 1px 2px rgba(0,0,0,.8);
}
.cardinal span{
  display:inline-block;
  width:18px;
  text-align:center;
}
.sun-ref-label{
  display:inline-block;
  padding:1px 6px;
  border-radius:10px;
  font-size:11px;
  font-weight:700;
  border:1px solid rgba(255,255,255,.25);
  text-shadow:0 1px 2px rgba(0,0,0,.8);
}
.sun-ref-label.sunrise{
  color:#ffd8be;
  background:rgba(249,115,22,.35);
}
.sun-ref-label.sunset{
  color:#fff3be;
  background:rgba(250,204,21,.30);
}
.sun-ref-label.facade{
  color:#ffe4e6;
  background:rgba(244,63,94,.42);
}
.sun-icon-wrap{
  background:transparent;
  border:none;
}
.sun-icon{
  display:block;
  width:22px;
  height:22px;
  border-radius:50%;
  background:radial-gradient(circle at 35% 35%, #fff6b5 0%, #f7d63c 38%, #f3b315 100%);
  border:2px solid rgba(255, 220, 90, 0.95);
  box-shadow:
    0 0 0 3px rgba(255, 214, 67, 0.22),
    0 0 14px rgba(255, 192, 48, 0.7);
}
.tende-page{padding:10px}
.tende-toolbar{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.tende-wizard{
  border:1px solid rgba(87,227,214,.28);
  border-radius:14px;
  padding:12px;
  margin-bottom:12px;
  background:
    radial-gradient(circle at 0% 0%, rgba(87,227,214,.14), transparent 34%),
    linear-gradient(135deg, rgba(12,21,36,.96), rgba(9,14,22,.92));
}
.wizard-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.wizard-head p{margin:4px 0 0;color:#9fb0c8;font-size:12px}
.wizard-step-count{color:#fde68a;font-size:12px;font-weight:700;white-space:nowrap}
.wizard-tabs{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}
.wizard-tab{border:1px solid var(--border);background:#0c1524;color:#cfe0f8;border-radius:999px;padding:6px 10px;font-weight:700;font-size:12px;cursor:pointer}
.wizard-tab.active{background:#57e3d6;color:#041016;border-color:#57e3d6}
.wizard-body{border-top:1px solid var(--border);padding-top:10px}
.wizard-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px}
.wizard-grid label{display:flex;flex-direction:column;gap:4px;color:#dbe7ff;font-size:13px}
.wizard-grid label small{color:#9fb0c8;font-size:11px;line-height:1.25}
.wizard-preset{display:flex;flex-direction:column;align-items:flex-start;justify-content:center;gap:3px;min-height:58px;text-align:left}
.wizard-preset small{color:#9fb0c8;font-size:11px;line-height:1.25;font-weight:600}
.wizard-review{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:8px;align-items:center}
.wizard-review span{background:#0c1524;border:1px solid var(--border);border-radius:10px;padding:8px;color:#dbe7ff;font-size:13px}
.what-if-panel{grid-column:1/-1;border:1px solid rgba(250,204,21,.24);border-radius:14px;padding:12px;background:linear-gradient(135deg,rgba(24,18,8,.78),rgba(8,14,22,.92))}
.what-if-head{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:10px}
.what-if-head span{background:transparent;border:none;padding:0;color:#9fb0c8}
.what-if-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:8px}
.what-if-card{display:flex;flex-direction:column;gap:6px;background:#0c1524;border:1px solid var(--border);border-radius:12px;padding:10px}
.what-if-card h4{margin:0;color:#fde68a}
.what-if-card span{border:none;background:transparent;padding:0;color:#dbe7ff}
.what-if-card.proposed{border-color:rgba(87,227,214,.38)}
.what-if-card.delta{border-color:rgba(250,204,21,.38)}
.wizard-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:10px}

/* Energy readability boost */
.energy-settings-card .tende-wizard{padding:16px;border-radius:14px}
.energy-settings-card .wizard-head strong{font-size:18px;letter-spacing:.2px}
.energy-settings-card .wizard-head p{font-size:14px;line-height:1.35}
.energy-settings-card .wizard-step-count{font-size:14px}
.energy-settings-card .wizard-tab{padding:9px 14px;font-size:14px}
.energy-settings-card .wizard-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.energy-settings-card .wizard-grid label{font-size:15px;gap:6px}
.energy-settings-card .wizard-grid label small{font-size:12px;line-height:1.35}
.energy-settings-card .wizard-review span{font-size:14px;padding:10px}
.energy-settings-card .form-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.energy-settings-card label{font-size:15px;color:#cfe0f7;gap:7px}
.energy-settings-card input,
.energy-settings-card select,
.energy-settings-card textarea{
  min-height:44px;
  padding:10px 12px;
  font-size:15px;
  border-radius:10px;
}
.energy-settings-card input[type="text"]{
  font-family: Consolas, "Courier New", monospace;
  font-size: 14px;
}
@media (max-width: 1280px){
  .energy-settings-card .wizard-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .energy-settings-card .form-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media (max-width: 820px){
  .energy-settings-card .wizard-grid{grid-template-columns:1fr}
  .energy-settings-card .form-grid{grid-template-columns:1fr}
}
.energy-settings-card textarea{min-height:220px;line-height:1.45}
.tende-cal-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px}
.tende-cal-grid label{display:flex;flex-direction:column;gap:4px;color:#cfe0f8;font-size:13px}
.tende-position-row{grid-column:1/-1;display:grid;grid-template-columns:repeat(4,minmax(160px,1fr));gap:8px}
.tende-sensors{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px;margin-top:10px}
.tende-sensors span{background:#0c1524;border:1px solid var(--border);border-radius:10px;padding:8px;color:#dbe7ff}
.tende-layout{display:grid;grid-template-columns:320px 1fr;gap:10px}
.tende-list{padding:10px;display:flex;flex-direction:column;gap:8px;max-height:74vh;overflow:auto}
.shade-item{background:#0c1524;border:1px solid var(--border);border-radius:10px;padding:8px;display:flex;flex-direction:column;gap:2px;text-align:left;color:#dbe7ff}
.shade-item.active{outline:2px solid #41d6c3}
.tende-map-wrap{padding:10px}
#tende-map{height:68vh;min-height:420px;border:1px solid var(--border);border-radius:10px;overflow:hidden}
.sun-window-heatmap{
  margin-top:12px;
  padding:12px;
  border:1px solid rgba(125,211,252,.24);
  border-radius:14px;
  background:
    radial-gradient(circle at 18% 0%, rgba(250,204,21,.18), transparent 34%),
    linear-gradient(135deg, rgba(8,14,22,.98), rgba(15,23,42,.94));
}
.sun-window-heatmap.empty{
  color:#9fb0c8;
  font-size:13px;
}
.heatmap-head{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:12px;
  margin-bottom:10px;
}
.heatmap-head h3{
  margin:0;
  color:#fff7d6;
}
.heatmap-head p{
  margin:3px 0 0;
  color:#9fb0c8;
  font-size:12px;
}
.heatmap-summary{
  display:flex;
  flex-wrap:wrap;
  justify-content:flex-end;
  gap:7px;
  color:#dbe7ff;
  font-size:12px;
}
.heatmap-summary strong,
.heatmap-summary span{
  background:rgba(12,21,36,.86);
  border:1px solid rgba(255,255,255,.12);
  border-radius:999px;
  padding:5px 8px;
}
.heatmap-summary strong{
  color:#fde68a;
}
.heatmap-strip{
  display:grid;
  gap:2px;
  min-height:34px;
  align-items:stretch;
}
.heatmap-cell{
  min-width:3px;
  border-radius:5px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.16);
}
.heatmap-cell.now{
  outline:2px solid #e0f2fe;
  outline-offset:1px;
}
.heatmap-axis{
  display:flex;
  justify-content:space-between;
  margin-top:7px;
  color:#9fb0c8;
  font-size:11px;
}
.tende-handle{
  display:block;
  width:16px;
  height:16px;
  border-radius:50%;
  border:2px solid #fff;
  box-shadow:0 0 8px rgba(0,0,0,.45);
}
.tende-handle-start{background:#22c55e}
.tende-handle-end{background:#ef4444}
.altitude-label{
  display:inline-block;
  background:rgba(8,14,22,.92);
  border:1px solid rgba(255,255,255,.42);
  color:#f5f8ff;
  border-radius:8px;
  padding:1px 7px;
  font-size:11px;
  font-weight:700;
  text-shadow:0 1px 2px rgba(0,0,0,.75);
}
.energy-popup-backdrop{
  position:fixed;
  inset:0;
  background:rgba(2,6,18,.72);
  z-index:1200;
  display:block;
  overflow:auto;
  padding:14px;
}
.energy-popup-card{
  width:min(1180px,98vw);
  max-height:none;
  margin:8px auto;
  overflow:auto;
  overscroll-behavior:contain;
  background:linear-gradient(160deg,rgba(8,17,33,.98),rgba(3,9,20,.98));
  border:1px solid rgba(100,116,139,.45);
  border-radius:12px;
  padding:12px;
}
.energy-popup-head{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:10px;
}
.energy-map-grid{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  gap:8px;
}
.energy-map-grid .btn{
  text-align:left;
  white-space:normal;
}
.energy-map-board{
  display:grid;
  grid-template-columns:repeat(3,minmax(220px,1fr));
  gap:8px;
}
.energy-map-node{
  background:rgba(15,23,42,.7);
  border:1px solid rgba(148,163,184,.45);
  color:#e5e7eb;
  border-radius:10px;
  padding:8px 10px;
  text-align:left;
  font-size:13px;
  cursor:pointer;
}
.energy-map-node small{
  display:block;
  margin-top:4px;
  color:#93c5fd;
  font-size:11px;
  word-break:break-all;
}
.energy-map-node.solar,.energy-map-node.solar2,.energy-map-node.home{ border-color:rgba(245,158,11,.6); }
.energy-map-node.grid,.energy-map-node.volt,.energy-map-node.hz,.energy-map-node.dailygrid{ border-color:rgba(6,182,212,.6); }
.energy-map-node.battery,.energy-map-node.soc{ border-color:rgba(99,102,241,.6); }
.energy-map-node.dailypv,.energy-map-node.dailyload{ border-color:rgba(148,163,184,.6); }
.energy-live-map{
  position:relative;
  border:1px solid rgba(71,85,105,.5);
  border-radius:10px;
  overflow:hidden;
  background:#040b1a;
  width:960px;
  height:760px;
  min-width:960px;
  min-height:760px;
  max-width:none;
}
.energy-live-frame{
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  border:0;
  display:block;
  pointer-events:none;
}
.map-selected-banner{
  position:absolute;
  left:10px;
  top:10px;
  z-index:4;
  padding:8px 10px;
  border-radius:8px;
  border:1px solid rgba(34,211,238,.75);
  background:rgba(8,47,73,.8);
  color:#e0f2fe;
  font-weight:700;
}
.energy-map-list{
  margin-top:10px;
  display:grid;
  grid-template-columns:repeat(2,minmax(280px,1fr));
  gap:8px;
}
.energy-map-row{
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:10px;
  padding:8px;
  border:1px solid rgba(71,85,105,.45);
  border-radius:8px;
  background:rgba(15,23,42,.55);
}
.energy-map-row small{
  display:block;
  color:#93c5fd;
  margin-top:2px;
  word-break:break-all;
}
.energy-map-row.active{
  border-color:#22d3ee;
  box-shadow:inset 0 0 0 1px rgba(34,211,238,.45), 0 0 0 2px rgba(34,211,238,.2);
  background:rgba(8,47,73,.38);
}
.energy-layout{
  display:grid;
  grid-template-columns:1fr;
  gap:16px;
}
.energy-setup-page{
  max-width:1280px;
  margin-left:auto;
  margin-right:auto;
}
.energy-group{
  border:1px solid rgba(71,85,105,.42);
  border-radius:14px;
  background:linear-gradient(180deg,rgba(8,17,33,.78),rgba(4,10,22,.78));
  padding:14px 14px 12px;
  box-shadow:0 0 0 1px rgba(8,18,36,.2) inset;
}
.energy-group h4{
  margin:0 0 12px 0;
  padding:0 0 8px 0;
  border-bottom:1px solid rgba(71,85,105,.4);
  font-size:18px;
  color:#dbeafe;
  letter-spacing:.2px;
}
.energy-subblock{
  border:1px solid rgba(51,65,85,.72);
  border-radius:12px;
  background:rgba(2,6,23,.32);
  padding:12px;
  margin-top:12px;
}
.energy-subblock:first-of-type{
  margin-top:0;
}
.energy-subblock > strong{
  display:block;
  margin-bottom:10px;
  color:#bfdbfe;
  font-size:15px;
  font-weight:800;
}
.energy-entity-grid{
  grid-template-columns:repeat(5,minmax(160px,1fr));
}
.energy-load-grid{
  display:grid;
  grid-template-columns:repeat(2,minmax(280px,1fr));
  gap:12px;
}
.energy-load-row{
  border:1px solid rgba(71,85,105,.48);
  border-radius:12px;
  background:#071122;
  padding:12px;
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:10px;
}
.energy-load-row > strong{
  grid-column:1 / -1;
  color:#bfdbfe;
}
.energy-note{
  font-size:14px;
  color:#9fb0c8;
  margin:0 0 14px 0;
}
.energy-setup-steps{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:10px;
  margin:0 0 14px 0;
}
.energy-setup-steps div{
  display:flex;
  align-items:center;
  gap:10px;
  min-height:46px;
  padding:10px 12px;
  border:1px solid rgba(56,189,248,.22);
  border-radius:12px;
  background:rgba(2,6,23,.35);
}
.energy-setup-steps strong{
  display:grid;
  place-items:center;
  width:26px;
  height:26px;
  border-radius:999px;
  background:#155e75;
  color:#cffafe;
  flex:0 0 auto;
}
.energy-setup-steps span{
  color:#cbd5e1;
  font-size:13px;
  line-height:1.25;
}
.energy-quick-panel{
  border:1px solid rgba(34,211,238,.32);
  border-radius:14px;
  background:linear-gradient(180deg,rgba(8,30,52,.82),rgba(7,16,31,.88));
  padding:16px;
  margin-bottom:16px;
}
.energy-sites-panel{
  border:1px solid rgba(148,163,184,.28);
  border-radius:14px;
  background:rgba(15,23,42,.62);
  padding:16px;
  margin-bottom:16px;
}
.energy-sites-head{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:14px;
  margin-bottom:12px;
}
.energy-sites-head strong{
  display:block;
  font-size:18px;
  color:#e2e8f0;
}
.energy-sites-head span{
  display:block;
  margin-top:4px;
  color:#94a3b8;
  font-size:13px;
}
.energy-site-actions,
.energy-site-tabs{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
}
.energy-site-tabs{
  margin-bottom:12px;
}
.energy-site-tab{
  appearance:none;
  text-align:left;
  border:1px solid rgba(71,85,105,.55);
  border-radius:12px;
  background:#0a1424;
  color:#cbd5e1;
  padding:10px 12px;
  min-width:150px;
  cursor:pointer;
}
.energy-site-tab strong,
.energy-site-tab small{
  display:block;
}
.energy-site-tab small{
  margin-top:3px;
  color:#8aa0bb;
}
.energy-site-tab.active{
  border-color:rgba(34,211,238,.85);
  box-shadow:0 0 0 2px rgba(34,211,238,.16);
}
.energy-quick-head{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:14px;
  margin-bottom:14px;
}
.energy-quick-head strong{
  display:block;
  font-size:19px;
  color:#e0f2fe;
}
.energy-quick-head span{
  display:block;
  margin-top:4px;
  color:#93c5fd;
  font-size:13px;
}
.energy-status-pills{
  display:flex;
  flex-wrap:wrap;
  justify-content:flex-end;
  gap:8px;
}
.energy-status-pills span{
  margin:0;
  padding:7px 10px;
  border:1px solid rgba(148,163,184,.28);
  border-radius:999px;
  background:rgba(15,23,42,.7);
  color:#cbd5e1;
  font-size:12px;
  font-weight:700;
}
.energy-status-pills span.ok{
  border-color:rgba(34,197,94,.45);
  color:#bbf7d0;
  background:rgba(20,83,45,.36);
}
.energy-quick-grid{
  display:grid;
  grid-template-columns:repeat(2,minmax(280px,1fr));
  gap:12px 14px;
}
.energy-quick-grid label{
  display:flex;
  flex-direction:column;
  gap:6px;
  color:#dbeafe;
  font-size:13px;
}
.energy-quick-grid .toggle-line{
  flex-direction:row;
  align-items:center;
  justify-content:space-between;
  min-height:42px;
  padding:0 10px;
  border:1px solid rgba(71,85,105,.55);
  border-radius:10px;
  background:#0a1424;
}
.energy-quick-actions{
  display:flex;
  flex-wrap:wrap;
  gap:10px;
  margin-top:14px;
}
.energy-warning{
  margin-top:12px;
  padding:10px 12px;
  border-radius:10px;
  border:1px solid rgba(245,158,11,.45);
  background:rgba(120,53,15,.32);
  color:#fde68a;
  font-size:13px;
}
.energy-advanced-details{
  border:1px solid rgba(71,85,105,.4);
  border-radius:14px;
  background:rgba(2,6,23,.36);
  padding:0;
  overflow:hidden;
}
.energy-advanced-details > summary{
  cursor:pointer;
  list-style:none;
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:12px;
  padding:14px 16px;
  background:rgba(15,23,42,.72);
  border-bottom:1px solid rgba(71,85,105,.35);
}
.energy-advanced-details > summary::-webkit-details-marker{display:none}
.energy-advanced-details > summary span{
  color:#e2e8f0;
  font-weight:800;
  font-size:16px;
}
.energy-advanced-details > summary small{
  color:#93a4bb;
  font-size:12px;
}
.energy-advanced-details .energy-layout{
  padding:16px;
}
.energy-section-nav{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(145px,1fr));
  gap:10px;
  padding:14px 16px 0;
}
.energy-section-tab{
  appearance:none;
  text-align:left;
  border:1px solid rgba(71,85,105,.55);
  border-radius:12px;
  background:rgba(15,23,42,.72);
  color:#cbd5e1;
  padding:11px 12px;
  cursor:pointer;
}
.energy-section-tab strong,
.energy-section-tab small{
  display:block;
}
.energy-section-tab strong{
  font-size:14px;
  color:#e2e8f0;
}
.energy-section-tab small{
  margin-top:3px;
  font-size:11px;
  color:#91a4bd;
}
.energy-section-tab.active{
  border-color:rgba(34,211,238,.8);
  background:linear-gradient(180deg,rgba(8,47,73,.72),rgba(15,23,42,.86));
  box-shadow:0 0 0 2px rgba(34,211,238,.18);
}
.energy-section-tab.active strong{
  color:#a5f3fc;
}
.energy-settings-card .form-grid{
  grid-template-columns:repeat(2,minmax(280px,1fr));
  gap:12px 14px;
}
.energy-settings-card label{
  display:flex;
  flex-direction:column;
  gap:6px;
  font-size:13px;
  color:#cbd5e1;
}
.energy-settings-card label small{
  color:#8aa0bb;
  font-size:12px;
  line-height:1.3;
}
.energy-settings-card input,
.energy-settings-card select,
.energy-settings-card textarea{
  min-height:42px;
  font-size:15px;
  padding:10px 12px;
  border-radius:10px;
  border:1px solid rgba(71,85,105,.55);
  background:#0a1424;
  color:#e2e8f0;
}
.energy-settings-card input:focus,
.energy-settings-card select:focus,
.energy-settings-card textarea:focus{
  outline:none;
  border-color:#22d3ee;
  box-shadow:0 0 0 2px rgba(34,211,238,.22);
}
.energy-settings-card input[type="checkbox"]{
  min-height:auto;
  width:18px;
  height:18px;
  margin-top:4px;
  accent-color:#56e6d8;
}
.energy-settings-card textarea{
  min-height:180px;
  line-height:1.45;
}

@media (max-width: 768px){
  .topbar{
    flex-wrap:wrap;
    gap:8px;
    padding:10px 10px;
  }
  .brand{
    width:100%;
  }
  .actions{
    width:100%;
    display:grid;
    grid-template-columns:1fr 1fr 1fr;
    gap:6px;
  }
  .btn{
    width:100%;
    padding:8px 10px;
    font-size:12px;
  }
  .timeline{
    padding:8px 10px;
  }
  .time-labels{
    font-size:10px;
  }
  .map-wrap{
    height:52dvh;
    min-height:340px;
  }
  .panel{
    grid-template-columns:1fr 1fr;
  }
  .tende-layout{
    grid-template-columns:1fr;
  }
  .tende-position-row{
    grid-template-columns:1fr 1fr;
  }
  .energy-layout{
    grid-template-columns:1fr;
  }
  .energy-quick-head{
    flex-direction:column;
  }
  .energy-sites-head{
    flex-direction:column;
  }
  .energy-site-actions{
    width:100%;
  }
  .energy-site-tab{
    min-width:0;
    flex:1 1 150px;
  }
  .energy-status-pills{
    justify-content:flex-start;
  }
  .energy-setup-steps{
    grid-template-columns:1fr;
  }
  .energy-quick-grid{
    grid-template-columns:1fr;
  }
  .energy-section-nav{
    grid-template-columns:1fr 1fr;
  }
  .energy-advanced-details > summary{
    flex-direction:column;
    align-items:flex-start;
  }
  .energy-settings-card .form-grid{
    grid-template-columns:1fr;
  }
  .energy-entity-grid{
    grid-template-columns:1fr;
  }
  .energy-load-grid{
    grid-template-columns:1fr;
  }
  .energy-load-row{
    grid-template-columns:1fr;
  }
  .heatmap-head{
    flex-direction:column;
  }
  .heatmap-summary{
    justify-content:flex-start;
  }
  #tende-map{
    height:56dvh;
    min-height:320px;
  }
  .bar-y-axis{
    min-width:38px;
    font-size:10px;
  }
  .user-public{
    padding:8px;
    min-height:100dvh;
  }
  .user-public-head{
    min-height:118px;
    padding:8px 10px;
    border-radius:12px;
  }
  .up-logo{
    width:92vw;
    max-width:92vw;
    height:96px;
  }
  .user-public-main{
    grid-template-columns:1fr;
    gap:8px;
    margin-top:8px;
  }
  .up-side{
    order:2;
    padding:10px;
  }
  .up-map-wrap{
    order:1;
    min-height:330px;
    border-radius:12px;
  }
  #solar-map-public{
    min-height:330px;
  }
  .up-map-controls{
    margin-top:8px;
    padding:8px 10px;
  }
  .user-public .time-labels{
    grid-template-columns:repeat(7,1fr);
    gap:2px;
    font-size:10px;
  }
  .user-public .time-labels span{
    text-align:center;
  }
  .user-public .time-labels span:nth-child(2n){
    display:none;
  }
  .up-time-sim input[type="range"]{
    width:100%;
  }
  .up-time-sim .time-meta{
    margin-top:6px;
    font-size:13px;
  }
  .user-public .toggles{
    display:grid;
    grid-template-columns:1fr;
    gap:6px;
  }
  .user-public .toggles label{
    font-size:12px;
    line-height:1.3;
  }
  .user-public .pv-az-controls{
    grid-template-columns:1fr;
    gap:6px;
  }
  .user-public .pv-az-input{
    width:100%;
  }
  .up-bottom{
    grid-template-columns:1fr;
    gap:8px;
    margin-top:8px;
  }
  .up-card{
    padding:10px;
  }
  .energy-public{
    padding:10px;
  }
  .energy-hero{
    margin-bottom:10px;
  }
  .energy-status{
    font-size:15px;
  }
  .energy-temp{
    font-size:26px;
  }
  .energy-flow{
    grid-template-columns:1fr 1fr;
  }
  .energy-flow-board{
    min-height:420px;
  }
  .ef-kpi-side{
    position:static;
    width:auto;
    padding:10px;
    margin-top:260px;
  }
  .ef-node .ef-val{font-size:24px}
  .ef-node-pv{left:50%;transform:translateX(-50%);top:20px}
  .ef-node-home{left:50%;transform:translateX(-50%);top:145px}
  .ef-node-bat{left:10px;top:250px}
  .ef-node-grid{right:10px;left:auto;top:250px}
  .ef-link-bat{left:78px;top:78px;width:120px;height:205px}
  .ef-link-grid{right:78px;top:78px;width:120px;height:205px}
  .ef-link-home{left:50%;transform:translateX(-50%);top:120px;height:64px}
  .energy-kpi-grid{
    grid-template-columns:1fr;
  }
  .energy-kpi strong{
    font-size:24px;
  }
  .metric-row{
    flex-direction:column;
    align-items:flex-start;
  }
  .metric-val{
    text-align:left;
  }
}
@media (max-width: 1500px){
  .energy-settings-card .form-grid{
    grid-template-columns:repeat(3,minmax(220px,1fr));
  }
}
@media (max-width: 1180px){
  .energy-settings-card .form-grid{
    grid-template-columns:repeat(2,minmax(220px,1fr));
  }
}
</style>
