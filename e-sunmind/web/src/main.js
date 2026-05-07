import { createApp } from 'vue'
import App from './App.vue'
import '@mdi/font/css/materialdesignicons.min.css'
import 'leaflet/dist/leaflet.css'

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

window.addEventListener('error', (evt) => {
  if (evt?.error) renderBootError(evt.error)
})
window.addEventListener('unhandledrejection', (evt) => {
  renderBootError(evt?.reason || 'unhandled_promise_rejection')
})

try {
  createApp(App).mount('#app')
} catch (err) {
  renderBootError(err)
}
