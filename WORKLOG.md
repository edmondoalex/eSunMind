# WORKLOG

## 2026-05-13
- Energy Flow wrapper: sostituito caricamento CDN statico Sunsynk con loader a fallback (`v7.3.3`, poi `master`) per evitare pagina rotta su 404 jsDelivr.
- Bump versione addon/backend a `0.3.210` con changelog aggiornato.

## 2026-05-12
- Energy Setup/Flow: corretto caso `full + AUX`, ora il JSON elimina `essential_load3..6` e il wrapper mantiene AUX visibile limitando i load essenziali a 2.
- Bump versione addon/backend a `0.3.209` con changelog aggiornato.

- Energy Setup UI: pagina resa piu user friendly con larghezza leggibile, avvio rapido in 3 passi e configurazione completa a sezioni cliccabili.
- Energy Flow wrapper: ripristinata direzione flussi tramite flag `invert_*` calcolati da `entity_signs_json`, mantenendo gli stati HA raw.
- Bump versione addon/backend a `0.3.208` con changelog aggiornato.

- Energy Flow wrapper: sanitizzazione generale delle entita opzionali mancanti per daily solar/load/grid/battery e AUX daily.
- Aggiunto retry difensivo di `setConfig()` dopo sanitizzazione per non fermare il sync dati con config parziali.
- Bump versione addon/backend a `0.3.207` con changelog aggiornato.

- Energy Flow wrapper: disattivazione automatica `battery.show_daily` quando mancano le entita daily charge/discharge richieste dalla card Sunsynk.
- Risolto errore `day_battery_charge_70` / `day_battery_discharge_71` in config parziali o test.
- Bump versione addon/backend a `0.3.206` con changelog aggiornato.

- Energy Flow wrapper: corretta pubblicazione degli stati HA reali da `card_entities` verso `window.hass.states`, utile anche quando piu chiavi puntano allo stesso sensore di test.
- Aggiunto warning console per errori di sync Energy non gestiti.
- Bump versione addon/backend a `0.3.205` con changelog aggiornato.

- Energy Flow wrapper: aggiunti fallback batteria richiesti da Sunsynk Power Flow Card 6.9.2 (`shutdown_soc`, `energy`, `max_power`, speed, auto-scale).
- Risolto crash `setConfig()` quando il JSON utente contiene `battery: {}` o omette `battery.shutdown_soc`.
- Bump versione addon/backend a `0.3.204` con changelog aggiornato.

- Energy Setup UI: aggiunto pannello rapido con campi essenziali e azioni dirette.
- Energy Setup UI: nascosta la configurazione completa dentro sezione espandibile per rendere leggibili load, AUX, grid, segni e JSON avanzato.
- Bump versione addon/backend a `0.3.203` con changelog aggiornato.

- Energy Sunsynk wrapper: corretta doppia inversione dei flussi, lasciando i valori gia normalizzati dal wrapper e neutralizzando gli `invert_*` della card.
- Energy Sunsynk wrapper: corretto caso `full + show_aux + 4 load`, che nella card originale azzerava i carichi aggiuntivi; ora AUX viene disattivato automaticamente per mostrare i load essenziali.
- Bump versione addon/backend a `0.3.202` con changelog aggiornato.

## 2026-05-11
- Fix critico wizard Energy: campi colore allineati ai parametri reali Sunsynk (colour).
- Risolto il caso in cui le modifiche visive sembravano non applicarsi nonostante JSON aggiornato.
- Bump versione addon a .3.124 con changelog aggiornato.

- Wizard Energy esteso con step Icone per personalizzare icone load/grid (default/boiler/aircon/pump/oven).
- Generatore JSON card aggiornato: include override load.load1_icon..load6_icon e grid.load1_icon..load3_icon.
- Bump versione addon a .3.123 con changelog aggiornato.

- Energy: introdotto wizard wow passo-passo per configurazione card Sunsynk direttamente da UI (impianti, batterie, carichi, colori, entita).
- Implementata generazione automatica JSON sunsynk_card_config_json con bottone Applica alla card.
- Aggiunto prefill wizard dai campi gia presenti in Setting > Energy per setup rapido.
- Bump versione addon a .3.122 con changelog aggiornato.

- Energy settings: aggiunto editor JSON sunsynk_card_config_json per gestire tutta la configurazione card direttamente da Setting > Energy.
- Backend/schema aggiornati per persistere la nuova chiave energy senza hardcode nel wrapper.
- Wrapper Sunsynk ora legge /api/options all'avvio e applica il JSON custom alla cardConfig runtime.
- Bump versione addon a .3.121 con changelog aggiornato.

- Sunsynk wrapper: passaggio a dati reali addon (../api/data) con polling continuo ogni 2s.
- Rimossa simulazione random automatica: il random resta solo azionabile manualmente come fallback/test.
- Mappati campi realtime da energy.normalized verso sensori mock della card originale (PV, batteria, rete, potenza casa, SOC).
- Aggiornati anche i totali giornalieri quando presenti nel payload energia normalizzato.
- Bump versione addon a .3.120 con changelog aggiornato.

- Sunsynk wrapper: tema scuro riallineato allo sfondo addon (#080a10) con variabili colore base coerenti.
- Toolbar e controlli wrapper uniformati alla palette dark dell'interfaccia principale.
- Bump versione addon a .3.119 con changelog aggiornato.

- Sunsynk wrapper: aggiunto mock temi HA (	hemes.dark=true) per coerenza dark mode.
- Sensori mock allineati al formato HA completo (state string + attributi unita/device_class/state_class).
- Refinement updateSensors per update realtime con metadati sensore preservati.
- README esteso con documentazione entry point standalone e integrazione backend via updateSensors.
- Bump versione addon a .3.118 con changelog aggiornato.

- Energy Dashboard: aggiunto sunsynk-wrapper.html standalone con caricamento card originale sunsynk-power-flow-card.js da jsDelivr.
- Creato mock window.hass completo (states/localize) per esecuzione card fuori da Home Assistant.
- Implementata funzione globale updateSensors(newData) per aggiornamento realtime dei sensori mock e refresh UI.
- Impostato update demo ogni secondo + pulsante manuale random per validare animazioni/flussi.
- Routing aggiornato: energy-dashboard/index.html ora redirige a sunsynk-wrapper.html; link UI Admin riallineato.
- Bump versione addon a .3.117 con changelog aggiornato.

- Sunsynk Standalone: rifatto il frontend in modalita Full coerente col repo originale (coordinate/struttura SVG 720x405).
- Portata la logica flussi reale: pallini su path con nimateMotion, inversione verso con keyPoints e invert_flow per ogni ramo.
- Portata formula speed originale per scaling dinamico animazioni in base a potenza e soglia max.
- Mantenute API standalone (setPowerData) e polling dati addon da ../api/data (energy.normalized).
- Bump versione addon a .3.116 con changelog aggiornato.

- Energy Dashboard: avviata migrazione da `sunsynk-power-flow-card` verso versione standalone addon-native senza dipendenze HA.
- Creata nuova cartella `web/public/energy-dashboard/sunsynk-standalone/` con `index.html`, `styles.css`, `script.js`.
- Portata logica flussi core: direzione invertibile (`invert_flow`) e speed dinamica da formula `animation_speed/max_power` in funzione potenza istantanea.
- Implementata funzione globale `setPowerData(json)` per aggiornare valori e animazioni in realtime dal backend.
- Agganciato polling automatico a `../api/data` con mapping dati da `energy.normalized` (PV/Home/Grid/Battery/SOC).
- Layout reso facilmente tarabile tramite variabili CSS coordinate (`--solar-x`, `--inverter-y`, ecc.).
- Bump versione addon a `0.3.115` con changelog aggiornato.

- Energy Dashboard: applicato refactor visuale \"Cyber-Tech\" richiesto per ridurre clutter e aumentare leggibilita.
- Gerarchia/spacing corretti: ogni valore principale (kW, V, Hz) confinato nella propria glass-card, niente overlap tra testi.
- Flussi SVG rifiniti: spessore ridotto (max ~3px), curve morbide e animazione trailing-light via `stroke-dasharray`.
- Card glassmorphism uniformate con `blur(10px)`, gradiente leggero e bordo 1px a opacita 20%.
- Layout forzato su griglia chiara a 3 colonne (sinistra solar/legnaia, centro inverter/battery/status, destra CED/consumi/grid).
- Bump versione addon a `0.3.114` con changelog aggiornato.

- Energy Dashboard: sostituito `web/public/energy-dashboard/index.html` con nuova UI single-file Neon Cyberpunk (Tailwind CDN + Framer Motion).
- Layout allineato al mock con nodi glassmorphism e flussi SVG neon animati (solare giallo, pannelli giallo chiaro, batteria viola, consumi bianco/blu-grigio, rete ciano).
- Aggiunta responsivita completa con scaling dinamico della scena per desktop/tablet/mobile, preservando geometria e proporzioni originali.
- Verifica preview locale effettuata via server HTTP su `http://localhost:8787/index.html`.
- Bump versione addon a `0.3.113` con changelog aggiornato.

- Energy Dashboard: abbandonato React Flow nella scena centrale e introdotto rendering SVG custom puro.
- Nuovo stile light premium con layout scena ripulito (FV alto, casa centrale, batteria/rete in basso, pompa lato destro) e metriche integrate.
- Flussi energetici alleggeriti e poi progressivamente migliorati in leggibilita (linee, particelle, contrasto, posizionamento label/KPI).
- Aggiunti device dedicati `Rack Dati`, `Wall Box` e `Carichi Casa`; fotovoltaico reso dinamico (`sole/nuvola/luna`, indicatore `+/-`).
- Batteria resa dinamica in funzione del SOC (riempimento e colore) e mantenuta nel redesign successivo.
- Rifinito il publish dashboard statico con riallineamento `web/public/energy-dashboard/index.html` al bundle JS corrente.
- Refactor grafico finale in stile soft isometric premium con icone SVG inline coerenti (casa, FV, batteria, rete, pompa, rack, wall box, carichi).
- Flussi azzurri animati resi piu profondi con glow leggermente aumentato nel tema finale.
- Bump versioni addon completato fino a `0.3.112` (`0.3.108` -> `0.3.112`) con changelog aggiornato.

## 2026-05-10
- Rework totale `Energy Flow` su richiesta: eliminato look da diagramma tecnico.
- Implementati componenti separati richiesti: `EnergyNode`, `HomeNode`, `EnergyEdge`, `simulateEnergy`.
- Layout premium fisso 16:9 con casa centrale e device tiles compatti glassmorphism.
- Edge premium con gradient/glow e particella animata su `animateMotion`.
- Dati live da `../api/data`; fallback simulazione mantenuto solo se API non disponibile.
- Build aggiornata e pubblicata in `web/public/energy-dashboard`.
- Bump versione addon a `0.3.107`.

## 2026-05-10
- Correzione richiesta utente: `Energy Flow` mostrava valori fake non coerenti con entita reali.
- Rebuild dashboard React flow con polling `../api/data` ogni 2s e mapping da `energy.normalized`.
- Aggiornato pacchetto statico in `web/public/energy-dashboard` con nuova build live-data.
- Bump versione addon a `0.3.106`.

## 2026-05-10
- Integrazione opzione `1`: dashboard React standalone incorporata nell'addon e servita da FastAPI.
- Aggiunto mount statico `/energy-dashboard` e link `Energy Flow` in UI Admin.
- Build `energy-dashboard-standalone` resa relativa (`base: './'`) e copiata in `web/public/energy-dashboard`.
- Verificata presenza asset in `web/dist/energy-dashboard` dopo build Vue.
- Bump versione addon a `0.3.105` con changelog aggiornato.

## 2026-05-10
- Energy UI: aggiunti temi selezionabili (`classic_flow`, `technical_dark`, `minimal_light`) con salvataggio in `Setting > Energy`.
- Nuova resa `Classic Inverter` con flow board visivo (nodi/linee/KPI) piu vicina al riferimento grafico.
- Supporto override tema via query string (`?view=energy&theme=classic|dark|minimal`).
- Bump versione addon a `0.3.104` con changelog aggiornato.

## 2026-05-10
- Aggiunta nuova pagina UI User `Energy` (query `?view=energy`) separata dal flusso meteo/mappa.
- Implementata vista energia senza pulsanti interni con KPI produzione/consumo/rete/batteria e SOC.
- Aggiunta sezione `Setting > Energy` per mappare tutte le entita energetiche HA.
- Backend: aggiunto snapshot `energy` in `/api/data` e `/api/data_demo` con normalizzazione potenza/energia.
- Estesi defaults/salvataggio opzioni addon (`energy`) e schema `config.yaml`.
- Bump versione addon a `0.3.103` con changelog aggiornato.

## 2026-05-08
- UI User mobile: fix completo layout smartphone (`view=user_public`) con regole responsive dedicate.
- Migliorati proporzioni header/logo, altezza mappa, ordine blocchi, slider timeline e griglia toggle su schermi <=768px.
- Ridotte collisioni visive (orari/toggle troppo stretti) con etichette orarie diradate e spaziatura coerente.
- Bump versione addon a `0.3.101` con changelog aggiornato.

## 2026-05-08
- Mitigazione errori proxy `502 Bad Gateway` su `api/data` in UI: introdotto lock `loadDataInFlight` per evitare richieste concorrenti.
- Aggiunto backoff esponenziale automatico su errori fetch/http (2s -> max 60s) per non saturare proxy/WebView in condizioni degradate.
- Mantenuto comportamento non bloccante: UI resta avviata anche con errori temporanei di rete/API.
- Bump versione addon a `0.3.100` con changelog aggiornato.

## 2026-05-07
- Rollback `user-lite`: ripristinata UI User con mappa come default.
- Test ipotesi splash: disattivato delay splash su `view=user` per evitare race WebView in bootstrap.
- Bump versione addon a `0.3.99` con changelog aggiornato.
- Aggiunta `UI User Lite` (`?view=user-lite`) senza mappa/Leaflet per bypass definitivo crash WebView su parsing/bootstrap mappa.
- Bump versione addon a `0.3.98` con changelog aggiornato.
- Diagnostica anti-proxy/truncation: aggiunti endpoint hash statici (`/api/diag/static_hashes`, `/api/diag/static_hash`) per confronto upstream vs proxy.
- Bump versione addon a `0.3.97` con changelog aggiornato.
- Hardening ulteriore per WebView/Control4: build frontend senza minify + target `es2018` e mount app con retry per avvio robusto.
- Bump versione addon a `0.3.96` con changelog aggiornato.
- Fix WebView/proxy: gestito `ERR_EMPTY_RESPONSE` su `api/data` con fallback non bloccante (no unhandled promise).
- Mappa: retry non piu rilanciato in modo aggressivo dal polling periodico; retry conservato solo su init/tab switch.
- Bump versione addon a `0.3.95` con changelog aggiornato.
- Fix robusto bootstrap mappa su WebView/Ingress: init lazy su tab attiva, guardia container DOM, idempotenza `dataset.mapInit`, retry limitato e fallback senza crash.
- Bump versione addon a `0.3.94` con changelog aggiornato.
- Fix encoding globale UI/backend: rimossi simboli corrotti (mojibake) da mappe, tooltip, labels e unita (`Ã‚Â°`, `Ãƒ`, `Ã‚Âµg/mÃ‚Â³`).
- Bump versione addon a `0.3.93` con changelog aggiornato.
- Hotfix logo Ingress: logo UI Admin spostato su asset bundlato `src/assets/logo-main.png` per rimuovere 404 su `/logo.png`.
- Bump versione addon a `0.3.92` con changelog aggiornato.
- Hotfix Ingress web UI: risolti path assoluti frontend (`/assets` e `/api`) che sotto HA Ingress causavano 404/MIME error e pagina non caricata.
- Vite configurato con `base: './'` e chiamate API rese relative (`api/...`) per compatibilita con prefisso ingress.
- Bump versione addon a `0.3.91` con changelog aggiornato.
- Hotfix addon store: rimosso `ingress_entry` da `config.yaml` (incompatibile su alcune versioni HA, causava scomparsa addon dalla raccolta).
- Bump versione addon a `0.3.90` con changelog aggiornato.
- Bump versione addon a `0.3.89` per riallineamento numerazione release (fix ingress gia incluso).
- Fix accesso addon da Home Assistant: aggiunto `ingress_entry: true` a `config.yaml` per voce sidebar/pannello ingress.
- Bump versione addon a `0.3.88` con changelog aggiornato.
- UI User: aumentato il distacco verticale tra mappa e controlli orari/flag per migliorare leggibilita e usabilita.
- UI User: aggiunto box dedicato ai controlli mappa (`up-map-controls`) con padding e bordo.
- Bump versione addon a `0.3.87` con changelog aggiornato.
- UI User: resi visibili i flag mappa e aggiunto slider simulazione con orario simulato.
- Bump versione addon a `0.3.86` con changelog aggiornato.
- UI User: mappa portata sullo stesso renderer della UI Admin (stesse linee/cerchi/overlay e medesimo comportamento grafico).
- Bump versione addon a `0.3.85` con changelog aggiornato.
- UI User: logo e-Tende aumentato 2x e fix altezza testata per evitare clipping.
- UI User: splash d'ingresso 3s con logo e-Tende quando si apre da link dedicato.
- Bump versione addon a `0.3.84` con changelog aggiornato.
- UI User: logo e-Tende ulteriormente ingrandito in header.
- Bump versione addon a `0.3.83` con changelog aggiornato.
- UI User: logo e-Tende centrato in testata, rimossi ora/data, fix proporzioni header per eliminare tagli.
- Bump versione addon a `0.3.82` con changelog aggiornato.
- UI User: fix definitivo logo e-Tende con asset bundlato (`src/assets/logo-etende.png`) e rimozione menu top `PANORAMICA/TENDE/CLIMA/METEO`.
- UI Admin: accesso a UI User unificato in singolo link.
- Bump versione addon a `0.3.81` con changelog aggiornato.
- UI User/UI Admin: rimosso doppio accesso, lasciato unico link dedicato `UI User`.
- UI User: aggiornato logo e-Tende con file del componente e corretti simboli grado/temperatura (`Â°`, `Â°C`).
- Bump versione addon a `0.3.80` con changelog aggiornato.
- UI User: aggiunto link diretto dedicato `/?view=user` e apertura automatica pagina user via query param.
- UI User: sostituito logo con asset `e-Tende Intelligenti` (`logo-etende.png`).
- Bump versione addon a `0.3.79` con changelog aggiornato.
- UI User: redesign forte per avvicinamento al mock (header dedicato, sidebar legenda, mappa con overlay alba/tramonto/arco solare/settori).
- Bump versione addon a `0.3.78` con changelog aggiornato.
- Nuova esperienza UI: introdotta pagina separata `UI User` (standalone, senza link a sezioni tecniche) con look dashboard stile e-Tende.
- Rinominata UI corrente in `UI Admin` e aggiunto link di ingresso a `UI User`.
- Bump versione addon a `0.3.77` con changelog aggiornato.
- User UI meteo: migliorata fortemente la leggibilita con cards compatte, niente stretch verticale e badge stato non deformati.
- Bump versione addon a `0.3.76` con changelog aggiornato.
- Fix urgente runtime backend: risolto crash `api/data` (`UnboundLocalError: candidates`) in weather guard.
- Bump versione addon a `0.3.75` con changelog aggiornato.
- User UI: restyling completo pannello meteo/sensori con righe metrica piu leggibili, badge stato e sezione entita stazione collassabile.
- Bump versione addon a `0.3.74` con changelog aggiornato.
- Fix stale Weather Station: freschezza calcolata su timestamp piu recente (`max`) invece del piu vecchio (`min`) per evitare falsi `Stazione disponibile: NO`.
- Bump versione addon a `0.3.73` con changelog aggiornato.
- Weather Station: aggiunti fallback auto-mapping per ridurre entita vuote (outdoor temp/umidita e sensori solar/vpd in naming non standard).
- Setting Weather Station esteso con tutti i campi entita reali (dew point, feels like, solar lux, solar radiation, vpd) anche in salvataggio/autofill.
- User UI: aggiunta lista completa `Entita stazione rilevate` con tutti i valori disponibili da `device_id`.
- Bump versione addon a `0.3.72` con changelog aggiornato.
- User UI: introdotto auto-refresh dati ogni 15s sulla tab utente per evitare refresh manuale.
- Bump versione addon a `0.3.71` con changelog aggiornato.
- User UI: chiariti testi stato sorgenti meteo e Weather Guard (niente piu diciture ambigue tipo "Spento" per stato qualitÃ ).
- Aggiunti valori meteo importanti Ecowitt in mapping/visualizzazione: Dew Point, Feels Like, Solar Lux, Solar Radiation, VPD.
- Bump versione addon a `0.3.70` con changelog aggiornato.
- User UI meteo: resa completa la visualizzazione valori Web/Stazione mostrando tutti i campi `normalized` con label e unitÃ  coerenti.
- Bump versione addon a `0.3.69` con changelog aggiornato.
- User UI mappa vento: linea resa auto-esplicativa con testo `VENTO DA` e marker testa direzione, senza legenda aggiuntiva.
- Bump versione addon a `0.3.67` con changelog aggiornato.
- Fix toggle vento mappa (final): separato rendering layer vento con funzione dedicata e watcher diretti su direzione/velocita.
- Aggiunto cleanup timer retry su unmount per evitare stati incoerenti dopo toggle e cambi tab.
- Bump versione addon a `0.3.66` con changelog aggiornato.
- Fix toggle vento mappa (secondo step): inizializzazione cache immediata + doppio redraw al ri-enable per assorbire race data/map.
- Bump versione addon a `0.3.65` con changelog aggiornato.
- Fix toggle vento mappa User UI: la linea direzione ora riappare correttamente dopo OFF/ON grazie a fallback su `weather_guard` + ultimo valore valido.
- Aggiunti watcher reattivi per ridisegno immediato overlay vento al cambio flag.
- Bump versione addon a `0.3.64` con changelog aggiornato.
- Fix runtime mappa User UI: aggiunto guard anche su `Leaflet.Control.addTo` per race condition con target null.
- Bump versione addon a `0.3.63` con changelog aggiornato.
- Fix crash Leaflet User UI: patch globale su `Layer.addTo` per ignorare target mappa null temporanei, eliminando il bootstrap error `reading 'addLayer'`.
- Bump versione addon a `0.3.62` con changelog aggiornato.
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
- Fix UI integrazione e-SunMind â†” e-Tende: la cover non sparisce piu dopo salvataggio anche con payload mappa parziale/senza `id` stabile.
- Aggiornata selezione cover in pagina su chiave robusta (`id|cover_entity|name`).
- Aggiunto aggiornamento ottimistico locale dopo `POST /api/tende/map/update` per evitare refresh manuale.
- Bump versione addon a `0.3.41` con changelog aggiornato.

## 2026-05-03
- Portato addon e-SunMind a architettura stile e-ThermoMind.
- Aggiunta Web UI con FastAPI + pagina integrata.
- Aggiunto calcolo dati sole/luna con coordinate manuali o `location_query`.
- Aggiunta pubblicazione entita su Home Assistant via MQTT Discovery.
- Aggiornata porta web addon da 8098 a 1977 (ingress + expose + uvicorn).














