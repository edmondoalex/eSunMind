<template>
  <div class="wrap">
    <header class="top">
      <div class="brand">e-SunMind</div>
      <div class="top-actions">
        <button class="action-btn" @click="loadData">Aggiorna</button>
      </div>
    </header>

    <main class="main">
      <section class="card hero">
        <img src="/logo.png" alt="e-SunMind" class="logo" />
        <div class="statusline">
          <span class="badge" :class="ok ? 'ok' : 'off'">{{ ok ? 'Online' : 'Offline' }}</span>
          <span class="muted">{{ meta }}</span>
        </div>
      </section>

      <section class="card inner">
        <h2>Dati Sole/Luna</h2>
        <div class="grid">
          <div class="kpi"><div class="k">Sun Altitude</div><div class="v">{{ fmt(data?.sun_position?.altitude_deg) }}°</div></div>
          <div class="kpi"><div class="k">Sun Azimuth</div><div class="v">{{ fmt(data?.sun_position?.azimuth_compass_deg) }}°</div></div>
          <div class="kpi"><div class="k">Moon Altitude</div><div class="v">{{ fmt(data?.moon_position?.altitude_deg) }}°</div></div>
          <div class="kpi"><div class="k">Moon Azimuth</div><div class="v">{{ fmt(data?.moon_position?.azimuth_deg) }}°</div></div>
          <div class="kpi"><div class="k">Moon Illumination</div><div class="v">{{ fmt((data?.moon_illumination?.fraction ?? 0) * 100) }}%</div></div>
        </div>
      </section>

      <section class="card inner">
        <h2>JSON Completo</h2>
        <pre class="json">{{ pretty }}</pre>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'

const data = ref(null)
const ok = ref(false)
const err = ref('')
let timer = null

const meta = computed(() => {
  if (!data.value) return err.value || 'Caricamento dati...'
  const c = data.value.coordinates || {}
  return `${data.value.timestamp_local} | ${data.value.timezone} | lat ${c.latitude}, lon ${c.longitude}`
})

const pretty = computed(() => (data.value ? JSON.stringify(data.value, null, 2) : 'Nessun dato'))

function fmt(v) {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return '-'
  return Number(v).toFixed(2)
}

async function loadData() {
  try {
    const r = await fetch('/api/data', { cache: 'no-store' })
    const j = await r.json()
    if (!r.ok || j.error) throw new Error(j.error || 'Errore API')
    data.value = j
    ok.value = true
    err.value = ''
  } catch (e) {
    ok.value = false
    err.value = `Errore: ${e.message}`
  }
}

onMounted(async () => {
  await loadData()
  timer = setInterval(loadData, 10000)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<style>
:root{--bg:#070a0f;--card:#0b101a;--muted:#9fb0c7;--text:#e8f1ff;--accent:#57e3d6;--border:rgba(255,255,255,.08)}
*{box-sizing:border-box}
body{margin:0;font-family:"Space Grotesk","IBM Plex Sans","Trebuchet MS",sans-serif;background:radial-gradient(1200px 500px at 20% -10%, rgba(122,167,255,.08), transparent),radial-gradient(900px 500px at 80% 0%, rgba(87,227,214,.06), transparent),var(--bg);color:var(--text)}
.wrap{min-height:100vh;display:flex;flex-direction:column}
.top{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--border);position:sticky;top:0;background:rgba(10,15,22,.85);backdrop-filter:blur(14px);gap:12px}
.brand{font-weight:800;letter-spacing:.3px;font-size:16px}
.main{padding:18px;max-width:1100px;margin:0 auto;width:100%}
.card{background:linear-gradient(180deg, rgba(11,16,26,.98), rgba(9,14,22,.98));border:1px solid var(--border);border-radius:20px;padding:18px;box-shadow:0 18px 40px rgba(0,0,0,.38)}
.card.inner{margin-top:14px}
.hero{text-align:center}
.logo{max-width:220px;width:100%;height:auto}
.muted{color:var(--muted)}
.statusline{display:flex;align-items:center;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:8px}
.badge{font-size:12px;padding:4px 8px;border-radius:999px;border:1px solid var(--border)}
.badge.ok{color:#0b1f1c;background:var(--accent)}
.badge.off{color:#f5f7fa;background:#3b3f46}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:10px}
@media(min-width:760px){.grid{grid-template-columns:repeat(5,minmax(0,1fr))}}
.kpi{border:1px solid var(--border);border-radius:14px;padding:10px;background:rgba(10,15,22,.6)}
.k{font-size:12px;color:var(--muted)}
.v{font-size:18px;font-weight:700;margin-top:2px}
.action-btn{background:linear-gradient(135deg, var(--accent), #6cf1c9);border:none;color:#062524;padding:6px 12px;border-radius:999px;font-weight:700;cursor:pointer;font-size:12px}
h2{margin:0 0 10px 0;font-size:16px}
.json{white-space:pre-wrap;word-break:break-word;background:#0c141b;border:1px solid var(--border);border-radius:10px;padding:10px;max-height:420px;overflow:auto}
</style>