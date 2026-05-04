<template>
  <div class="wrap">
    <transition name="splash-fade">
      <div v-if="showSplash" class="splash-screen">
        <img src="/logo.png" alt="e-SunMind splash logo" class="splash-logo" />
      </div>
    </transition>

    <header class="topbar">
      <div class="brand">
        <img src="/logo.png" alt="e-SunMind logo" class="brand-logo" />
        <span>e-SunMind</span>
      </div>
      <div class="actions">
        <button class="btn ghost" :class="{active: tab==='user'}" @click="tab='user'">User UI</button>
        <button class="btn ghost" :class="{active: tab==='tech'}" @click="tab='tech'">Tecnica</button>
        <button class="btn" @click="loadData">Aggiorna</button>
      </div>
    </header>

    <div v-show="tab==='user'">
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
          <label><input type="checkbox" v-model="showPvAzLine" @change="drawSolarOverlay" /> Linea Azimut FV</label>
        </div>
        <div class="pv-az-controls" v-if="showPvAzLine">
          <label>Azimut FV:
            <input type="range" min="-180" max="180" step="1" v-model.number="pvAzimuthDeg" @input="drawSolarOverlay" />
          </label>
          <input class="pv-az-input" type="number" min="-180" max="180" step="1" v-model.number="pvAzimuthDeg" @change="drawSolarOverlay" />
          <span class="pv-az-value">{{ pvAzimuthDeg }} deg</span>
        </div>
      </div>

      <div class="map-wrap">
        <div id="solar-map"></div>
      </div>

      <div class="panel">
        <div class="kpi">Lat/Lon: {{ lat?.toFixed(5) }} , {{ lon?.toFixed(5) }}</div>
        <div class="kpi">Sun Altitude LIVE (reale): {{ fmt(data?.sun_position?.altitude_deg) }} deg</div>
        <div class="kpi">Sun Azimuth LIVE (reale): {{ fmt(data?.sun_position?.azimuth_compass_deg) }} deg</div>
        <div class="kpi">Sun Altitude SIM: {{ fmt(currentSun.altitudeDeg) }} deg</div>
        <div class="kpi">Sun Azimuth SIM: {{ fmt(currentSun.azimuthDeg) }} deg</div>
        <div class="kpi">Data locale: {{ data?.timestamp_local || '-' }}</div>
      </div>

      <div class="panel">
        <div class="kpi"><strong>Meteo provider:</strong> {{ weatherProvider || '-' }}</div>
        <div class="kpi"><strong>Meteo aggiornamento:</strong> {{ weatherTime || '-' }}</div>
        <div class="kpi"><strong>Temperatura:</strong> {{ fmt(weatherTempC) }} degC</div>
        <div class="kpi"><strong>Umidita:</strong> {{ fmt(weatherHumidityPct) }} %</div>
        <div class="kpi"><strong>Vento:</strong> {{ fmt(weatherWindMs) }} m/s ({{ fmt(weatherWindDirDeg) }} deg)</div>
        <div class="kpi"><strong>Nuvolosita:</strong> {{ fmt(weatherCloudPct) }} %</div>
        <div class="kpi"><strong>Pioggia prossima 1h:</strong> {{ fmt(weatherNext1hMm) }} mm</div>
        <div class="kpi"><strong>Condizione:</strong> {{ weatherSymbol || '-' }}</div>
      </div>
      <div class="panel">
        <div class="kpi chart-kpi">
          <strong>Meteo Prossime 24h</strong>
          <svg
            class="weather-chart"
            viewBox="0 0 900 250"
            preserveAspectRatio="none"
            role="img"
            aria-label="Grafico meteo 24 ore: temperatura e pioggia"
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

            <line v-if="weatherHoverPoint" :x1="weatherHoverPoint.x" :x2="weatherHoverPoint.x" y1="24" y2="190" class="chart-hover-line" />
            <g v-if="weatherHoverPoint" :transform="`translate(${weatherHoverTooltipX},${weatherHoverTooltipY})`">
              <rect class="chart-tip-bg" x="0" y="0" rx="6" ry="6" width="180" height="54" />
              <text x="8" y="15" class="chart-tip-t1">{{ weatherHoverPoint.label }}</text>
              <text x="8" y="30" class="chart-tip-t2">Temp: {{ fmt(weatherHoverPoint.temp) }} degC</text>
              <text x="8" y="45" class="chart-tip-t2">Pioggia: {{ fmt(weatherHoverPoint.rain) }} mm/h</text>
            </g>

            <text v-for="t in weatherTempTicks" :key="`wl-${t}`" x="42" :y="weatherYFromTemp(t) + 3" class="axis-label-y">{{ fmt0(t) }}</text>
            <text x="18" y="20" class="axis-title">degC</text>
            <text x="876" y="20" class="axis-title">mm/h</text>
            <text v-for="(p, i) in weatherSeries" v-if="i % 3 === 0" :key="`wxl-${i}`" :x="weatherXFromIdx(i)" y="208" class="axis-label-x">{{ p.hhmm }}</text>
          </svg>
          <div class="chart-meta">
            Linea gialla: temperatura | Barre azzurre: pioggia oraria | Range temp: {{ fmt(weatherTempMin) }}..{{ fmt(weatherTempMax) }} degC
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="kpi"><strong>Solar FV stato:</strong> {{ forecastOk ? 'OK' : 'N/D' }}</div>
        <div class="kpi"><strong>FV Oggi:</strong> {{ fmt0(fvTodayWh) }} Wh</div>
        <div class="kpi"><strong>FV Domani:</strong> {{ fmt0(fvTomorrowWh) }} Wh</div>
        <div class="kpi"><strong>FV Attuale:</strong> {{ fmt0(fvCurrentW) }} W</div>
        <div class="kpi"><strong>FV Picco oggi:</strong> {{ fmt0(fvPeakTodayW) }} W</div>
        <div class="kpi"><strong>Ultimo fetch:</strong> {{ forecastFetchedAtText }}</div>
      </div>

      <div class="panel">
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
            0:00 → 23:59 | picco: {{ fmt0(fvPeakSelectedW) }} W
            <span v-if="hoverPoint"> | punto: {{ hoverPoint.time }} -> {{ fmt0(hoverPoint.w) }} W</span>
          </div>
        </div>
      </div>

      <div class="panel">
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

    <div v-show="tab==='tech'">
      <main class="tech-main">
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
          <div class="actions-inline">
            <button class="btn" @click="saveForecastSettings">Salva Tarature Forecast</button>
            <span class="note">{{ fsSaveStatus }}</span>
          </div>
          <div class="mono small">{{ forecastConfigText }}</div>
          <p class="note">Le tarature forecast sono modificabili e salvabili direttamente da questa UI tecnica.</p>
        </section>

        <section class="card">
          <h3>Risposta completa Forecast Solar (raw)</h3>
          <pre class="json">{{ forecastRawText }}</pre>
        </section>

        <section class="card">
          <h3>Risposta completa Meteo MET (raw)</h3>
          <pre class="json">{{ weatherRawText }}</pre>
        </section>

        <section class="card">
          <h3>JSON runtime</h3>
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

const tab = ref('user')
const showSplash = ref(true)
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
let axisNS = null
let axisWE = null
let pvAzLine = null
let pvAzMarker = null
let compassMarkers = []

const selectedTime = computed(() => timeSteps[timeIndex.value] ?? { h: 12, m: 0 })
const selectedTimeLabel = computed(() => `${String(selectedTime.value.h).padStart(2, '0')}:${String(selectedTime.value.m).padStart(2, '0')}`)
const currentSun = ref({ altitudeDeg: null, azimuthDeg: null })
const showLiveLine = ref(true)
const showSimLine = ref(true)
const showAxisNS = ref(true)
const showAxisWE = ref(true)
const showPvAzLine = ref(false)
const pvAzimuthDeg = ref(0)
const selectedForecastDate = ref('')
const hoverHourBar = ref(null)
const fsForm = ref({ enabled: false, api_key: '', declination: 30, azimuth: 0, kwp: 6.0 })
const fsSaveStatus = ref('')

const pretty = computed(() => (data.value ? JSON.stringify(data.value, null, 2) : 'Nessun dato'))
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
const weatherSeries = computed(() => {
  const ts = data.value?.weather?.payload?.properties?.timeseries
  if (!Array.isArray(ts)) return []
  return ts.slice(0, 24).map((row) => {
    const d = row?.data || {}
    const inst = d?.instant?.details || {}
    const n1 = d?.next_1_hours || {}
    const rain = Number(n1?.details?.precipitation_amount ?? 0)
    const temp = Number(inst?.air_temperature)
    const time = String(row?.time || '')
    const hhmm = time.length >= 16 ? time.slice(11, 16) : '--:--'
    return {
      time,
      hhmm,
      temp: Number.isFinite(temp) ? temp : 0,
      rain: Number.isFinite(rain) ? rain : 0,
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
const weatherTempTicks = computed(() => {
  const mn = weatherTempMin.value
  const mx = weatherTempMax.value
  const span = Math.max(1, mx - mn)
  return [mn, mn + span * 0.33, mn + span * 0.66, mx]
})
const weatherTempPoints = computed(() => {
  const s = weatherSeries.value
  if (!s.length) return ''
  return s.map((p, i) => `${weatherXFromIdx(i).toFixed(1)},${weatherYFromTemp(p.temp).toFixed(1)}`).join(' ')
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
  weatherHoverPoint.value = {
    ...p,
    x: weatherXFromIdx(idx),
    y: weatherYFromTemp(p.temp),
    label: p.time ? p.time.replace('T', ' ').replace('Z', ' UTC') : p.hhmm,
  }
}
function onWeatherChartLeave() {
  weatherHoverPoint.value = null
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

function baseDateAtHour(hour, minute = 0) {
  const base = data.value?.timestamp_local ? new Date(data.value.timestamp_local) : new Date()
  const d = new Date(base)
  d.setHours(hour, minute, 0, 0)
  return d
}

function altitudeToRadius(altDeg) {
  // Sky-dome projection: horizon on outer ring, zenith at center.
  const a = Math.max(-6, Math.min(90, Number(altDeg)))
  const normalized = 1 - Math.sin((Math.max(0, a) * Math.PI) / 180)
  return cfg.value.sectorRadiusM * normalized
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

function drawSolarOverlay() {
  if (!map || lat.value == null || lon.value == null) return
  ;[centerMarker, pathLine, horizonCircle, sunLine, sunMarker, sunLineLive, sunMarkerLive, sunriseRay, sunsetRay, axisNS, axisWE, pvAzLine, pvAzMarker].forEach((l) => { if (l) map.removeLayer(l) })
  for (const m of compassMarkers) map.removeLayer(m)
  compassMarkers = []

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
  const pos = SunCalc.getPosition(dt, lat.value, lon.value)
  const az = suncalcAzToCompassDeg(pos.azimuth)
  const alt = toDeg(pos.altitude)
  currentSun.value = { azimuthDeg: az, altitudeDeg: alt }

  const sunPt = destinationPoint(lat.value, lon.value, az, cfg.value.sectorRadiusM)
  const srPt = destinationPoint(lat.value, lon.value, srAz, cfg.value.pathRadiusM)
  const ssPt = destinationPoint(lat.value, lon.value, ssAz, cfg.value.pathRadiusM)
  sunriseRay = L.polyline([[lat.value, lon.value], srPt], { color: '#f97316', weight: 3.2, opacity: 0.95 }).addTo(map)
  sunsetRay = L.polyline([[lat.value, lon.value], ssPt], { color: '#facc15', weight: 3.2, opacity: 0.95 }).addTo(map)

  if (showSimLine.value) {
    sunLine = L.polyline([[lat.value, lon.value], sunPt], {
      color: '#d86a2a',
      weight: 2.8,
      opacity: 0.9,
      lineCap: 'round',
    }).addTo(map)
    sunMarker = L.marker(sunPt, {
      icon: L.divIcon({
        className: 'sun-icon-wrap',
        html: '<span class="sun-icon"></span>',
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      }),
      interactive: false,
    }).addTo(map)
  }

  if (showLiveLine.value) {
      const liveAz = Number(data.value?.sun_position?.azimuth_compass_deg)
      if (Number.isFinite(liveAz)) {
      const livePt = destinationPoint(lat.value, lon.value, liveAz, cfg.value.sectorRadiusM)
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
}

function applyMapView() {
  if (map && lat.value != null && lon.value != null) map.setView([lat.value, lon.value], cfg.value.mapZoom)
  drawSolarOverlay()
}

async function loadData() {
  const r = await fetch('/api/data', { cache: 'no-store' })
  const j = await r.json()
  data.value = j
  lat.value = Number(j?.coordinates?.latitude)
  lon.value = Number(j?.coordinates?.longitude)

  if (Number.isFinite(lat.value) && Number.isFinite(lon.value)) {
    await nextTick()
    if (!map) {
      map = L.map('solar-map', { zoomControl: true }).setView([lat.value, lon.value], cfg.value.mapZoom)
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles © Esri',
        maxZoom: 20,
      }).addTo(map)
    } else {
      map.setView([lat.value, lon.value], cfg.value.mapZoom)
    }
    drawSolarOverlay()
  }
  const fs = data.value?.forecast_solar
  if (fs && data.value) {
    // Keep form in sync with current option defaults when available via options API fallback.
    try {
      const ro = await fetch('/api/options', { cache: 'no-store' })
      const oj = await ro.json()
      const fso = oj?.forecast_solar || {}
      fsForm.value = {
        enabled: Boolean(fso.enabled),
        api_key: String(fso.api_key || ''),
        declination: Number(fso.declination ?? 30),
        azimuth: Number(fso.azimuth ?? 0),
        kwp: Number(fso.kwp ?? 6.0),
      }
      if (Number.isFinite(fsForm.value.azimuth)) pvAzimuthDeg.value = fsForm.value.azimuth
      if (!selectedForecastDate.value && fvDayRows.value.length) selectedForecastDate.value = fvDayRows.value[0].date
    } catch (_) {
      // no-op
    }
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
    const r = await fetch('/api/options/forecast_solar', {
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

onMounted(() => {
  const now = new Date()
  const total = (now.getHours() * 60) + now.getMinutes()
  const base = 3 * 60
  const clamped = Math.max(base, Math.min(21 * 60, total))
  const rounded = Math.round((clamped - base) / 15)
  const idx = rounded
  if (idx >= 0) timeIndex.value = idx
  loadData()
  setTimeout(() => {
    showSplash.value = false
  }, 3000)
})
onBeforeUnmount(() => { if (map) { map.remove(); map = null } })

watch(tab, async (val) => {
  if (val === 'user' && map) {
    await nextTick()
    map.invalidateSize()
    drawSolarOverlay()
  }
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
.actions{display:flex;gap:8px;align-items:center}
.btn{background:linear-gradient(135deg, var(--accent), #6cf1c9);border:none;color:#062524;padding:6px 12px;border-radius:999px;font-weight:700;cursor:pointer}
.btn.ghost{background:transparent;border:1px solid var(--border);color:var(--text)}
.btn.ghost.active{border-color:var(--accent);color:#cffff5}
.timeline{padding:8px 12px;background:#232830;border-bottom:1px solid #3b4048}
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
.panel{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px;padding:10px;background:#111722;border-top:1px solid var(--border)}
.kpi{border:1px solid var(--border);border-radius:10px;padding:8px;background:rgba(10,15,22,.7);font-size:13px}
.tech-main{padding:14px;display:grid;gap:12px}
.card{border:1px solid var(--border);border-radius:14px;padding:12px;background:rgba(10,15,22,.75)}
.form-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}
label{display:flex;flex-direction:column;gap:6px;font-size:12px;color:var(--muted)}
input{padding:8px;border-radius:8px;border:1px solid var(--border);background:#0f1621;color:var(--text)}
.mono{font-family:Consolas,Monaco,monospace}
.small{font-size:12px}
.note{font-size:12px;color:var(--muted)}
.json{white-space:pre-wrap;word-break:break-word;background:#0c141b;border:1px solid var(--border);border-radius:10px;padding:10px;max-height:420px;overflow:auto}
.chart-kpi{grid-column:1 / -1}
.fv-chart{width:100%;height:250px;display:block;margin-top:8px;border:1px solid var(--border);border-radius:8px;background:rgba(12,20,28,.7)}
.weather-chart{width:100%;height:270px;display:block;margin-top:8px;border:1px solid var(--border);border-radius:8px;background:rgba(12,20,28,.7)}
.chart-axis{stroke:#607086;stroke-width:1}
.chart-grid{stroke:#2d3b4d;stroke-width:.8;opacity:.55}
.chart-grid-v{stroke:#243244;stroke-width:.8;opacity:.4}
.chart-line{fill:none;stroke:#f2c235;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}
.weather-temp-line{fill:none;stroke:#f2c235;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}
.weather-temp-dot{fill:#ffe68f;stroke:#f2c235;stroke-width:1}
.weather-rain-bar{fill:rgba(45,212,191,.46);stroke:rgba(125,242,228,.65);stroke-width:.8}
.chart-now{stroke:#2dd4bf;stroke-width:1.5;stroke-dasharray:6,5}
.chart-hover-line{stroke:#e5edf8;stroke-width:1.2;stroke-dasharray:3,4;opacity:.85}
.chart-hover-dot{fill:#ffffff;stroke:#f2c235;stroke-width:2}
.chart-tip-bg{fill:rgba(8,14,22,.92);stroke:#5f738d;stroke-width:1}
.chart-tip-t1{fill:#dfe8f6;font-size:11px;font-weight:700}
.chart-tip-t2{fill:#f2c235;font-size:11px;font-weight:700}
.axis-label-y{fill:#9fb0c7;font-size:10px;text-anchor:end}
.axis-label-x{fill:#9fb0c7;font-size:10px;text-anchor:middle}
.axis-title{fill:#c9d4e2;font-size:11px;font-weight:700}
.axis-title-x{fill:#c9d4e2;font-size:11px;font-weight:700;text-anchor:end}
.chart-meta{margin-top:6px;font-size:12px;color:var(--muted)}
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
  .bar-y-axis{
    min-width:38px;
    font-size:10px;
  }
}
</style>
