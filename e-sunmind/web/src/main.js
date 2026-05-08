import { createApp } from 'vue'
import App from './App.vue'
import '@mdi/font/css/materialdesignicons.min.css'
import 'leaflet/dist/leaflet.css'

let appMounted = false
const BOOT_GUARD_MS = 8000
let bootGuardTimer = 0

function renderBootError(err) {
  const root = document.getElementById('app')
  if (!root) return
  const msg = (err && (err.stack || err.message || String(err))) || 'unknown_boot_error'
  root.innerHTML = `
    <div style="padding:16px;background:#0b1220;color:#e7eefc;font-family:Arial,sans-serif;min-height:100vh;">
      <h2 style="margin:0 0 10px 0;color:#ffb4b4;">e-SunMind UI bootstrap error</h2>
      <p style="margin:0 0 10px 0;">L'interfaccia non e riuscita ad avviarsi. Copia questo errore e invialo al supporto.</p>
      <pre style="white-space:pre-wrap;background:#111a2b;border:1px solid #2a3958;border-radius:8px;padding:10px;overflow:auto;">${String(msg).replace(/</g, '&lt;')}</pre>
    </div>
  `
}

function isLikelySunMindError(evtOrReason) {
  const text = String(
    evtOrReason?.stack ||
    evtOrReason?.message ||
    evtOrReason?.reason?.stack ||
    evtOrReason?.reason?.message ||
    evtOrReason?.filename ||
    evtOrReason ||
    ''
  )
  if (!text) return false
  return (
    text.includes('/ext/e-SunMind/') ||
    text.includes('/assets/index-') ||
    text.includes('e-SunMind')
  )
}

function onWindowError(evt) {
  if (appMounted) return
  if (!isLikelySunMindError(evt)) return
  renderBootError(evt?.error || evt)
}

function onUnhandledRejection(evt) {
  if (appMounted) return
  if (!isLikelySunMindError(evt)) return
  renderBootError(evt?.reason || 'unhandled_promise_rejection')
}

window.addEventListener('error', onWindowError)
window.addEventListener('unhandledrejection', onUnhandledRejection)

function mountWithRetry(maxTry = 3, delayMs = 250) {
  let attempt = 0
  const run = () => {
    attempt += 1
    try {
      createApp(App).mount('#app')
      appMounted = true
      if (bootGuardTimer) {
        clearTimeout(bootGuardTimer)
        bootGuardTimer = 0
      }
      window.removeEventListener('error', onWindowError)
      window.removeEventListener('unhandledrejection', onUnhandledRejection)
    } catch (err) {
      if (attempt < maxTry) {
        setTimeout(run, delayMs)
        return
      }
      renderBootError(err)
    }
  }
  run()
}

bootGuardTimer = setTimeout(() => {
  appMounted = true
  window.removeEventListener('error', onWindowError)
  window.removeEventListener('unhandledrejection', onUnhandledRejection)
}, BOOT_GUARD_MS)

mountWithRetry()
