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
        <span>e-SunMind <small class="brand-version">v{{ appVersion }}</small></span>
      </div>
      <div class="actions">
        <button class="btn ghost" :class="{active: tab==='user'}" @click="tab='user'">User UI</button>
        <button class="btn ghost" :class="{active: tab==='tende'}" @click="tab='tende'">Tende/Cover</button>
        <button class="btn ghost" :class="{active: tab==='tech'}" @click="tab='tech'">Tecnica</button>
        <button class="btn" @click="loadData">Aggiorna</button>
      </div>
    </header>

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
          <label><input type="checkbox" v-model="showPvAzLine" @change="drawSolarOverlay" /> Linea Azimut FV</label>
          <label><input type="checkbox" v-model="showAnnualElevationBand" @change="drawSolarOverlay" /> Fascia elevazione annua</label>
          <label><input type="checkbox" v-model="showTendeSectors" @change="drawSolarOverlay" /> Spicchi Cover (e_Tende Intelligenti)</label>
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
        <div id="solar-map"></div>
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

      <div class="panel" v-show="userExpanded">
        <div class="kpi"><strong>Meteo provider:</strong> {{ weatherProvider || '-' }}</div>
        <div class="kpi"><strong>Meteo aggiornamento:</strong> {{ weatherTime || '-' }}</div>
        <div class="kpi"><strong>Temperatura:</strong> {{ fmt(weatherTempC) }}°C</div>
        <div class="kpi"><strong>Temperatura reale:</strong> {{ fmt(externalTempC) }}°C</div>
        <div class="kpi"><strong>Delta T reale-meteo:</strong> {{ fmt(tempDeltaC) }}°C</div>
        <div class="kpi"><strong>Umidita reale:</strong> {{ fmt(externalHumidityPct) }} %</div>
        <div class="kpi"><strong>Umidita meteo:</strong> {{ fmt(weatherHumidityPct) }} %</div>
        <div class="kpi"><strong>Vento:</strong> {{ fmt(weatherWindMs) }} m/s ({{ fmt(weatherWindDirDeg) }}°)</div>
        <div class="kpi"><strong>Pressione:</strong> {{ fmt(weatherPressureHpa) }} hPa</div>
        <div class="kpi"><strong>Nuvolosita:</strong> {{ fmt(weatherCloudPct) }} %</div>
        <div class="kpi"><strong>Pioggia prossima 1h:</strong> {{ fmt(weatherNext1hMm) }} mm</div>
        <div class="kpi"><strong>UV index:</strong> {{ fmt(weatherUvIndex) }}</div>
        <div class="kpi"><strong>Condizione:</strong> {{ weatherSymbol || '-' }}</div>
        <div class="kpi"><strong>FV reale e-Control:</strong> {{ fmt0(pvMeasuredW) }} W</div>
        <div class="kpi"><strong>FV atteso (ora):</strong> {{ fmt0(pvForecastNowW) }} W</div>
        <div class="kpi"><strong>Rapporto reale/atteso:</strong> {{ fmt2(pvLiveRatio) }}</div>
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
              <text x="8" y="74" class="chart-tip-t2">T reale: {{ fmt(externalTempC) }}Â°C | Delta: {{ fmt(weatherHoverPoint.deltaRealTemp) }}Â°C</text>
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
            aria-label="Grafico qualità aria 24 ore"
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
            0:00 → 23:59 | picco: {{ fmt0(fvPeakSelectedW) }} W
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
        <div class="tende-cal-grid">
          <label>Azimuth start
            <input type="number" min="0" max="360" step="0.1" v-model.number="selectedShadeEdit.azimuth_start_deg" @change="drawTendeEditor" />
          </label>
          <label>Azimuth end
            <input type="number" min="0" max="360" step="0.1" v-model.number="selectedShadeEdit.azimuth_end_deg" @change="drawTendeEditor" />
          </label>
          <label>Altitudine min
            <input type="number" min="-10" max="90" step="0.1" v-model.number="selectedShadeEdit.altitude_min_deg" />
          </label>
          <label>Altitudine max
            <input type="number" min="-10" max="90" step="0.1" v-model.number="selectedShadeEdit.altitude_max_deg" />
          </label>
        </div>
      </div>
      <div class="tende-layout">
        <div class="tende-list card">
          <h3>Cover da e-Tende Intelligenti</h3>
          <div v-if="!tendeMapShades.length" class="note">Nessuna tenda ricevuta.</div>
          <button
            v-for="s in tendeMapShades"
            :key="s.id"
            class="shade-item"
            :class="{active: selectedShadeId===s.id}"
            @click="selectShade(s.id)"
          >
            <strong>{{ s.name || s.id }}</strong>
            <span>{{ s.cover_entity || '-' }}</span>
            <span>Az {{ fmt(s.azimuth_start_deg) }}° → {{ fmt(s.azimuth_end_deg) }}°</span>
            <span>Stato: {{ coverStateLabel(s.cover_entity) }}</span>
          </button>
        </div>
        <div class="tende-map-wrap card">
          <h3>Mappa taratura tenda</h3>
          <div id="tende-map"></div>
        </div>
      </div>
    </div>

    <div v-show="tab==='tech'">
      <div class="view-tools">
        <button class="btn ghost" @click="techExpanded = !techExpanded">{{ techExpanded ? 'Riduci campi' : 'Allarga campi' }}</button>
      </div>
      <main class="tech-main">
        <section class="card">
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
          <div class="actions-inline">
            <button class="btn" @click="saveBaseSettings">Salva Config Base</button>
            <span class="note">{{ baseSaveStatus }}</span>
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

        <section class="card" v-show="techExpanded">
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
          <div class="actions-inline">
            <button class="btn" @click="saveOverlaySettings">Salva Tarature Overlay</button>
            <span class="note">{{ overlaySaveStatus }}</span>
          </div>
        </section>

        <section class="card" v-show="techExpanded">
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
let annualElevationBand = null
let annualElevationBandLayers = []
let compassMarkers = []
let tendeSectorLayers = []
const weatherAnimEnabled = ref(false)
const weatherCanvasEl = ref(null)
let weatherRafId = 0
let weatherLastTs = 0
let weatherClouds = []
let weatherRain = []
let blockTogglesInited = false
let tendeMapObj = null
let tendeCenter = null
let tendeRing = null
let tendePoly = null
let tendeStartMarker = null
let tendeEndMarker = null

const selectedTime = computed(() => timeSteps[timeIndex.value] ?? { h: 12, m: 0 })
const selectedTimeLabel = computed(() => `${String(selectedTime.value.h).padStart(2, '0')}:${String(selectedTime.value.m).padStart(2, '0')}`)
const currentSun = ref({ altitudeDeg: null, azimuthDeg: null })
const showLiveLine = ref(true)
const showSimLine = ref(true)
const showAxisNS = ref(true)
const showAxisWE = ref(true)
const showPvAzLine = ref(false)
const showAnnualElevationBand = ref(true)
const showTendeSectors = ref(true)
const tendeEditMode = ref(false)
const selectedShadeId = ref('')
const selectedShadeEdit = ref(null)
const tendeSaveStatus = ref('')
const pvAzimuthDeg = ref(0)
const selectedForecastDate = ref('')
const hoverHourBar = ref(null)
const fsForm = ref({ enabled: false, api_key: '', declination: 30, azimuth: 0, kwp: 6.0 })
const fsSaveStatus = ref('')
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

const pretty = computed(() => (data.value ? JSON.stringify(data.value, null, 2) : 'Nessun dato'))
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
  return Array.isArray(arr) ? arr.filter((s) => s) : []
})
const tendeCoverStates = computed(() => tendeMap.value?.cover_states || {})
const coordinatesSourceLabel = computed(() => {
  const raw = String(data.value?.coordinates_source || '').trim().toLowerCase()
  if (raw === 'e-tendeintelligenti') return 'e-Tende Intelligenti'
  if (raw === 'e-tende_missing_coords') return 'e-Tende (coordinate mancanti nel payload)'
  if (raw === 'home_assistant_core') return 'Home Assistant Core'
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
  weatherClouds = Array.from({ length: 10 }, () => ({
    x: Math.random() * w,
    y: (Math.random() * h * 0.45) + 10,
    r: 18 + Math.random() * 34,
    a: 0.02 + Math.random() * 0.05,
  }))
  weatherRain = Array.from({ length: 120 }, () => ({
    x: Math.random() * w,
    y: Math.random() * h,
    l: 8 + Math.random() * 14,
    v: 120 + Math.random() * 180,
    a: 0.10 + Math.random() * 0.25,
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

  if (!weatherClouds.length || !weatherRain.length) seedWeatherParticles()

  for (const c of weatherClouds) {
    c.x += wind.vx * dt * 18
    c.y += wind.vy * dt * 3
    if (c.x > w + c.r) c.x = -c.r
    if (c.x < -c.r) c.x = w + c.r
    if (c.y > h * 0.55) c.y = 5
    if (c.y < 5) c.y = h * 0.45
    ctx.fillStyle = `rgba(176,205,220,${(c.a * cloudI * 0.9).toFixed(3)})`
    ctx.beginPath()
    ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2)
    ctx.fill()
  }

  if (rainI > 0.02) {
    const sx = wind.vx * 14
    const sy = 220 + Math.abs(wind.vy * 10)
    for (const p of weatherRain) {
      p.x += sx * dt + wind.vx * dt * 20
      p.y += (p.v + sy) * dt
      if (p.y > h + 20) {
        p.y = -10
        p.x = Math.random() * w
      }
      if (p.x > w + 20) p.x = -10
      if (p.x < -20) p.x = w + 10
      ctx.strokeStyle = `rgba(86,201,240,${(p.a * rainI * 0.8).toFixed(3)})`
      ctx.lineWidth = 0.9
      ctx.beginPath()
      ctx.moveTo(p.x, p.y)
      ctx.lineTo(p.x + sx * 0.08, p.y + p.l)
      ctx.stroke()
    }
  }

  // Wind streaks, subtle and directional.
  const windStrength = Math.min(1, Math.hypot(wind.vx, wind.vy) / 5)
  if (windStrength > 0.04) {
    ctx.strokeStyle = `rgba(70,210,255,${(0.12 + windStrength * 0.22).toFixed(3)})`
    ctx.lineWidth = 1.2
    for (let i = 0; i < 42; i += 1) {
      const bx = ((ts * 0.025 + i * 47) % (w + 40)) - 20
      const by = (i * 23) % (h * 0.75)
      const lx = wind.vx * 2.3
      const ly = wind.vy * 2.3
      ctx.beginPath()
      ctx.moveTo(bx, by)
      ctx.lineTo(bx + lx * 6, by + ly * 6)
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
      const color = String(shade.color || colorFromIndex(idx))
      const active = Boolean(shade.active)
      const opacity = stale ? 0.14 : (active ? 0.34 : 0.2)
      const poly = L.polygon(buildSectorPolygonPoints(azStart, azEnd, cfg.value.sectorRadiusM), {
        color,
        weight: active ? 2.4 : 1.4,
        opacity: stale ? 0.5 : 0.9,
        fillColor: color,
        fillOpacity: opacity,
      }).addTo(map)
      const tip = `${shade.name || shade.id}<br>${shade.cover_entity || ''}<br>Az: ${fmt(azStart)}° → ${fmt(azEnd)}°<br>Active: ${active ? 'yes' : 'no'}`
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

function selectShade(id) {
  selectedShadeId.value = id
  const shade = tendeMapShades.value.find((s) => s.id === id)
  if (!shade) return
  selectedShadeEdit.value = {
    id: shade.id,
    name: shade.name,
    cover_entity: shade.cover_entity,
    azimuth_start_deg: Number.isFinite(Number(shade.azimuth_start_deg)) ? Number(shade.azimuth_start_deg) : 0,
    azimuth_end_deg: Number.isFinite(Number(shade.azimuth_end_deg)) ? Number(shade.azimuth_end_deg) : 0,
    altitude_min_deg: shade.altitude_min_deg,
    altitude_max_deg: shade.altitude_max_deg,
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
  tendeMapObj = L.map('tende-map', { zoomControl: true, attributionControl: true }).setView([lat.value, lon.value], cfg.value.mapZoom)
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles © Esri',
    maxZoom: 20,
  }).addTo(tendeMapObj)
}

function drawTendeEditor() {
  if (!tendeMapObj || !selectedShadeEdit.value || lat.value == null || lon.value == null) return
  ;[tendeCenter, tendeRing, tendePoly, tendeStartMarker, tendeEndMarker].forEach((l) => { if (l) tendeMapObj.removeLayer(l) })
  const s = selectedShadeEdit.value
  tendeCenter = L.circleMarker([lat.value, lon.value], { radius: 4, color: '#ffd24a', fillColor: '#ffd24a', fillOpacity: 1 }).addTo(tendeMapObj)
  tendeRing = L.circle([lat.value, lon.value], { radius: cfg.value.sectorRadiusM, color: '#7f8a95', weight: 1.2, fillOpacity: 0 }).addTo(tendeMapObj)
  const color = colorFromIndex(tendeMapShades.value.findIndex((x) => x.id === s.id))
  tendePoly = L.polygon(buildSectorPolygonPoints(s.azimuth_start_deg, s.azimuth_end_deg, cfg.value.sectorRadiusM), {
    color,
    weight: 2.4,
    fillColor: color,
    fillOpacity: 0.28,
  }).addTo(tendeMapObj)
  const p1 = destinationPoint(lat.value, lon.value, s.azimuth_start_deg, cfg.value.sectorRadiusM)
  const p2 = destinationPoint(lat.value, lon.value, s.azimuth_end_deg, cfg.value.sectorRadiusM)
  tendeStartMarker = L.marker(p1, {
    draggable: tendeEditMode.value,
    icon: L.divIcon({
      className: 'tende-handle-wrap',
      html: '<span class="tende-handle tende-handle-start"></span>',
      iconSize: [18, 18],
      iconAnchor: [9, 9],
    }),
  }).addTo(tendeMapObj)
  tendeEndMarker = L.marker(p2, {
    draggable: tendeEditMode.value,
    icon: L.divIcon({
      className: 'tende-handle-wrap',
      html: '<span class="tende-handle tende-handle-end"></span>',
      iconSize: [18, 18],
      iconAnchor: [9, 9],
    }),
  }).addTo(tendeMapObj)

  if (tendeEditMode.value) {
    const updatePreview = () => {
      if (!tendePoly || !selectedShadeEdit.value) return
      const pts = buildSectorPolygonPoints(
        selectedShadeEdit.value.azimuth_start_deg,
        selectedShadeEdit.value.azimuth_end_deg,
        cfg.value.sectorRadiusM
      )
      tendePoly.setLatLngs(pts)
    }
    tendeStartMarker.on('dragstart', () => { tendeMapObj.dragging.disable() })
    tendeEndMarker.on('dragstart', () => { tendeMapObj.dragging.disable() })
    tendeStartMarker.on('drag', (e) => {
      s.azimuth_start_deg = angleFromCenter(e.latlng)
      updatePreview()
    })
    tendeEndMarker.on('drag', (e) => {
      s.azimuth_end_deg = angleFromCenter(e.latlng)
      updatePreview()
    })
    tendeStartMarker.on('dragend', () => { tendeMapObj.dragging.enable(); drawTendeEditor() })
    tendeEndMarker.on('dragend', () => { tendeMapObj.dragging.enable(); drawTendeEditor() })
  }
}

function toggleTendeEditMode() {
  tendeEditMode.value = !tendeEditMode.value
  drawTendeEditor()
}

async function saveSelectedShade() {
  if (!selectedShadeEdit.value) return
  tendeSaveStatus.value = 'Salvataggio...'
  try {
    const payload = {
      id: selectedShadeEdit.value.id,
      cover_entity: selectedShadeEdit.value.cover_entity || null,
      azimuth_start_deg: selectedShadeEdit.value.azimuth_start_deg,
      azimuth_end_deg: selectedShadeEdit.value.azimuth_end_deg,
      altitude_min_deg: selectedShadeEdit.value.altitude_min_deg,
      altitude_max_deg: selectedShadeEdit.value.altitude_max_deg,
    }
    const r = await fetch('/api/tende/map/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const j = await r.json()
    if (!r.ok || !j.ok) {
      const err = new Error(j.error || 'save_failed')
      err.cause = j
      throw err
    }
    if (j.ack && (j.ack.status === 'ok' || j.ack.ok === true)) tendeSaveStatus.value = 'Taratura applicata (ACK ricevuto).'
    else if (j.ack) tendeSaveStatus.value = `ACK: ${j.ack.status || 'ricevuto'}`
    else tendeSaveStatus.value = 'Taratura inviata (ACK non ricevuto).'
    await loadData()
  } catch (e) {
    let extra = ''
    try {
      if (e?.cause?.ack?.error) extra = ` (${e.cause.ack.error})`
      else if (e?.cause?.error) extra = ` (${e.cause.error})`
    } catch (_) {}
    tendeSaveStatus.value = `Errore: ${e.message}${extra}`
  }
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
  // Keep forms in sync with current persisted options, independent from forecast availability.
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
    selectShade(tendeMapShades.value[0].id)
  } else if (selectedShadeId.value) {
    const ex = tendeMapShades.value.find((s) => s.id === selectedShadeId.value)
    if (ex) selectShade(ex.id)
  }
}

async function loadStatusVersion() {
  try {
    const r = await fetch('/api/status', { cache: 'no-store' })
    const j = await r.json()
    if (j?.version) appVersion.value = String(j.version)
  } catch (_) {
    // keep fallback
  }
}

async function saveBaseSettings() {
  baseSaveStatus.value = 'Salvataggio...'
  try {
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
    }
    const r = await fetch('/api/options/base', {
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

async function saveOverlaySettings() {
  overlaySaveStatus.value = 'Salvataggio...'
  try {
    const payload = {
      pathRadiusM: Number(cfg.value.pathRadiusM ?? 102),
      sectorRadiusM: Number(cfg.value.sectorRadiusM ?? 110),
      sunRadiusM: Number(cfg.value.sunRadiusM ?? 95),
      mapZoom: Number(cfg.value.mapZoom ?? 18),
    }
    const r = await fetch('/api/options/overlay', {
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
  const now = new Date()
  const total = (now.getHours() * 60) + now.getMinutes()
  const base = 3 * 60
  const clamped = Math.max(base, Math.min(21 * 60, total))
  const rounded = Math.round((clamped - base) / 15)
  const idx = rounded
  if (idx >= 0) timeIndex.value = idx
  loadData()
  loadStatusVersion()
  window.addEventListener('resize', resizeWeatherCanvas)
  startWeatherAnimation()
  initBlockToggles()
  setTimeout(() => {
    showSplash.value = false
  }, 3000)
})
onBeforeUnmount(() => {
  if (map) { map.remove(); map = null }
  if (tendeMapObj) { tendeMapObj.remove(); tendeMapObj = null }
  stopWeatherAnimation()
  window.removeEventListener('resize', resizeWeatherCanvas)
})

watch(tab, async (val) => {
  if (val === 'user' && map) {
    await nextTick()
    initBlockToggles()
    map.invalidateSize()
    drawSolarOverlay()
    resizeWeatherCanvas()
    if (weatherAnimEnabled.value) startWeatherAnimation()
  } else if (val === 'tende') {
    await nextTick()
    ensureTendeMap()
    if (tendeMapObj && lat.value != null && lon.value != null) {
      tendeMapObj.setView([lat.value, lon.value], cfg.value.mapZoom)
      tendeMapObj.invalidateSize()
      if (!selectedShadeId.value && tendeMapShades.value.length) selectShade(tendeMapShades.value[0].id)
      else drawTendeEditor()
    }
  } else {
    stopWeatherAnimation()
  }
})

watch(weatherAnimEnabled, (enabled) => {
  if (enabled && tab.value === 'user') startWeatherAnimation()
  else stopWeatherAnimation()
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
  opacity:.65;
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
.chart-tip-t1{fill:#dfe8f6;font-size:11px;font-weight:700}
.chart-tip-t2{fill:#f2c235;font-size:11px;font-weight:700}
.axis-label-y{fill:#9fb0c7;font-size:10px;text-anchor:end}
.axis-label-x{fill:#9fb0c7;font-size:10px;text-anchor:middle}
.axis-label-x-strong{fill:#dfe8f6;font-size:11px;font-weight:700}
.axis-title{fill:#c9d4e2;font-size:11px;font-weight:700}
.axis-title-x{fill:#c9d4e2;font-size:11px;font-weight:700;text-anchor:end}
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
.tende-cal-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px}
.tende-cal-grid label{display:flex;flex-direction:column;gap:4px;color:#cfe0f8;font-size:13px}
.tende-layout{display:grid;grid-template-columns:320px 1fr;gap:10px}
.tende-list{padding:10px;display:flex;flex-direction:column;gap:8px;max-height:74vh;overflow:auto}
.shade-item{background:#0c1524;border:1px solid var(--border);border-radius:10px;padding:8px;display:flex;flex-direction:column;gap:2px;text-align:left;color:#dbe7ff}
.shade-item.active{outline:2px solid #41d6c3}
.tende-map-wrap{padding:10px}
#tende-map{height:68vh;min-height:420px;border:1px solid var(--border);border-radius:10px;overflow:hidden}
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
  #tende-map{
    height:56dvh;
    min-height:320px;
  }
  .bar-y-axis{
    min-width:38px;
    font-size:10px;
  }
}
</style>
