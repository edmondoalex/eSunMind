# WORKLOG

## 2026-05-07
- Hardening frontend boot: aggiunto fail-safe globale in `web/src/main.js` per intercettare crash iniziali e mostrare errore a schermo.
- Eliminata condizione "pagina blu vuota" senza diagnostica: ora la UI espone direttamente stack/message runtime.
- Bump versione addon a `0.3.61` con changelog aggiornato.
- Fix runtime User UI: aggiunto failsafe splash (chiusura garantita) e `try/catch` su init `onMounted` per evitare schermata blu vuota.
- Bump versione addon a `0.3.60` con changelog aggiornato.
- User UI Meteo: rinominate le metriche WS con etichette estese e piu chiare.
- User UI Mappa: aggiunto toggle `Direzione vento su mappa` con freccia/velocita vento visualizzabile e disattivabile.
- Vento mappa: sorgente prioritaria da stazione reale, fallback meteo web.
- Bump versione addon a `0.3.59` con changelog aggiornato.
- Fix UX Weather Station: auto-fill da `device_id` ora parte anche al load della pagina Settings, senza richiedere modifica manuale del campo.
- Bump versione addon a `0.3.58` con changelog aggiornato.
- Weather Station: aggiunto endpoint `GET /api/weather_station/autofill` per mappatura automatica entita da `device_id`.
- Weather Station UI: auto-fill campi sensori al cambio `device_id`, con preservazione override manuali.
- Auto-mapping Ecowitt reso piu robusto usando anche `device_class` e unita.
- Bump versione addon a `0.3.57` con changelog aggiornato.
- Integrazione stazione reale Ecowitt/e-Control: aggiunto `weather_station.device_id` con auto-discovery entita da Home Assistant.
- Estesa configurazione Weather Station con sensori extra: temperatura esterna, umidita esterna, pressione, UV index.
- Regola sorgente meteo resa esplicita: usa stazione reale se valida/fresca, altrimenti fallback API web.
- Bump versione addon a `0.3.56` con changelog aggiornato.
- UI Wizard Tende/Cover: rinominato titolo in `Wizard taratura cover`.
- Bump versione addon a `0.3.55` con changelog aggiornato.
- UI Wizard Tende/Cover: aggiunto simulatore `What-if` nello step Verifica.
- Bump versione addon a `0.3.54` con changelog aggiornato.
- UI Wizard Tende/Cover: nascosto `Avanti` nello step finale.
- Bump versione addon a `0.3.53` con changelog aggiornato.
- UI Wizard Tende/Cover: aggiunte descrizioni per parametri e preset.
- Bump versione addon a `0.3.52` con changelog aggiornato.
- UI Tende/Cover: aggiunto wizard guidato per taratura cover selezionata.
- Bump versione addon a `0.3.51` con changelog aggiornato.
- UI grafici: ridotta dimensione font SVG per evitare label troppo grandi su pannelli larghi.
- Bump versione addon a `0.3.50` con changelog aggiornato.
- UI Tende/Cover: aggiunti campi strategia termica per termostato `climate` condivisibile tra piu cover.
- UI Tende/Cover: mostrata diagnostica termica con temperatura interna, setpoint e decisione.
- Bump versione addon a `0.3.49` con changelog aggiornato.
- Fix versione pannello addon: allineato `APP_VERSION` backend alla release `0.3.48`.
- Bump versione addon a `0.3.48` con changelog aggiornato.
- UI Tende/Cover: aggiunto controllo `Anti-loop comandi sec.` per configurare `min_command_interval_seconds` di e-Tende.
- UI Tende/Cover: mostrata diagnostica anti-loop/rate-limit nei sensori cover.
- Bump versione addon a `0.3.47` con changelog aggiornato.
- UI Tende/Cover: aggiunta heatmap `sole-finestra` giornaliera sotto la mappa taratura.
- La heatmap mostra durata sole utile, picco, prossima esposizione e tooltip per slot con azimut/elevazione.
- Bump versione addon a `0.3.46` con changelog aggiornato.

## 2026-05-06
- UI Tende/Cover: aggiunta linea mappa `Facciata` per visualizzare l'azimut stravento separato dal sole.
- Bump versione addon a `0.3.45` con changelog aggiornato.
- UI Tende/Cover: aggiunto `Azimut facciata stravento` per separare pioggia/vento da `Azimut finestra` usato dal sole.
- Bump versione addon a `0.3.44` con changelog aggiornato.
- UI Tende/Cover: raggruppati i quattro campi `Posizione sicurezza` sulla stessa riga desktop.
- Bump versione addon a `0.3.43` con changelog aggiornato.
- Allineato addon e-SunMind a e-Tende 0.1.72: aggiunti controlli `Usa logica sole` e `Inverti logica sole` nella pagina Tende/Cover.
- Il salvataggio taratura ora invia anche `sun_logic_enabled` e `invert_sun_logic` verso e-Tende.
- Bump versione addon a `0.3.42` con changelog aggiornato.
- Fix UI integrazione e-SunMind ↔ e-Tende: la cover non sparisce piu dopo salvataggio anche con payload mappa parziale/senza `id` stabile.
- Aggiornata selezione cover in pagina su chiave robusta (`id|cover_entity|name`).
- Aggiunto aggiornamento ottimistico locale dopo `POST /api/tende/map/update` per evitare refresh manuale.
- Bump versione addon a `0.3.41` con changelog aggiornato.

## 2026-05-03
- Portato addon e-SunMind a architettura stile e-ThermoMind.
- Aggiunta Web UI con FastAPI + pagina integrata.
- Aggiunto calcolo dati sole/luna con coordinate manuali o `location_query`.
- Aggiunta pubblicazione entita su Home Assistant via MQTT Discovery.
- Aggiornata porta web addon da 8098 a 1977 (ingress + expose + uvicorn).
