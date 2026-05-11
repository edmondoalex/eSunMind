# Changelog

## 0.3.114

- Energy Dashboard: ridotto affollamento UI con gerarchia visiva piu netta (label piu piccole, valori principali piu grandi) e rimozione overlap testi.
- Layout convertito in griglia fissa 3 colonne (`Solar/Legnaia` | `Inverter/Battery/Status` | `CED/Consumo/Grid`) per lettura immediata.
- Flussi SVG rifiniti: linee piu sottili (max ~3px), curve morbide e animazione `stroke-dasharray` in stile trailing light.
- Card uniformate in glassmorphism high-end: `backdrop-filter: blur(10px)`, gradiente leggero, bordo 1px con opacita 20%.
- Icone integrate nei box con glow coerente al flusso energetico associato (gold/violet/cyan/slate).

## 0.3.113

- Energy Dashboard: sostituita pagina `/energy-dashboard` con versione single-file HTML5 Neon Cyberpunk (Tailwind CDN + Framer Motion).
- Nuovo layout glassmorphism dark (`#080a10`) con flussi SVG neon animati (`stroke-dasharray`) e glow aggressivo per sorgenti/consumi/rete/batteria.
- Implementata responsivita completa con scaling dinamico della scena (desktop/tablet/mobile) mantenendo il posizionamento relativo del mock originale.
- Mantenuti valori statici e nodi di stato principali del pannello (`1,16 kW`, `231,5 V`, `50,02 Hz`) e codifica colori energia per linea funzionale.

## 0.3.112

- Energy Dashboard: refactor completo icone in stile soft isometric premium (SVG inline) per casa, fotovoltaico, batteria, rete, pompa di calore, rack dati, wall box e carichi casa.
- Migliorata coerenza grafica dispositivi (ombre morbide, palette chiara uniforme, dettaglio visivo allineato).
- Batteria dinamica per SOC mantenuta e integrata nel nuovo design isometrico.
- Flussi energetici azzurri animati con profondita/glow leggermente aumentati.

## 0.3.111

- Fix publish Energy Dashboard: riallineato `web/public/energy-dashboard/index.html` al bundle JS corrente.
- Applicate in release le modifiche grafiche Energy (`rack dati`, `wall box`, `carichi casa`, FV dinamico, batteria SOC dinamica).

## 0.3.110

- Energy scene: fotovoltaico dinamico con icona meteo/produzione (`sole`, `nuvola`, `luna`) e indicatore `+/-`.
- Aggiunti nuovi device nel diagramma: `Rack Dati`, `Wall Box` e `Carichi Casa` separati.
- Batteria resa dinamica: livello riempimento e colore in funzione del SOC.
- Aggiornati flussi energetici e label per i nuovi rami (rack/wallbox/carichi).

## 0.3.109

- Energy Dashboard light: contrasto aumentato (testi, icone, flussi) e leggibilita generale migliorata.
- Scena centrale ingrandita (~25-30%) con casa, FV, batteria e rete piu evidenti.
- Flussi energetici resi piu chiari: linee piu spesse, particelle piu visibili e label riposizionate.
- Metriche integrate in scena allineate a destra con spaziatura/unita migliorate; `Real-time Power` allineato al consumo casa.
- Pannello UI ottimizzato: larghezza utile maggiore (`94vw`) e altezza compatta (`~78vh`) con riduzione vuoti laterali.

## 0.3.108

- Energy Dashboard: abbandonato React Flow nella scena centrale, ora rendering SVG custom puro.
- Nuovo stile light premium (sfondo chiaro, pannello ghiaccio, ombre morbide) in linea con app inverter.
- Layout scena ripulito: FV alto, casa centrale, batteria basso-sx, rete basso-dx, pompa lato dx.
- Metriche principali integrate nella scena a destra (`Real-time Power`, `Installed Power`, `Produzione Oggi`, `Consumo Oggi`).
- Flussi energetici SVG alleggeriti (linee sottili azzurre, particelle animate soft, meno glow).

## 0.3.107

- Refactor completo `Energy Flow` in stile dashboard premium (non piu look flowchart tecnico).
- Nuovi `nodeTypes`: `energyNode` compatto e `homeNode` centrale enfatizzato.
- Nuovo `edgeType` premium: gradient brillante, glow e particella animata direzionale su path.
- Layout fisso: FV alto, casa centro, batteria basso-sx, rete basso-dx, pompa/carichi laterali.
- UI pulita: header minimal, pill metriche top, mini-card bottom (`oggi prodotto`, `oggi consumato`, `autonomia batteria`).
- Dati live da `../api/data` con fallback simulato solo in assenza API.

## 0.3.106

- Fix critico `Energy Flow`: rimossa simulazione fake React.
- La dashboard flow ora legge i dati reali da `../api/data` (payload `energy.normalized`).
- Allineamento con entita configurate in `Setting > Energy` (potenze, SOC, import/export, kWp).

## 0.3.105

- Integrata dashboard energetica standalone React (`Energy Flow`) direttamente nell'addon.
- Nuovo mount backend: `/energy-dashboard` (statico interno addon, compatibile ingress/proxy).
- Aggiunto link rapido `Energy Flow` in UI Admin (apertura nuova scheda).
- Build React copiata in `web/public/energy-dashboard` e pubblicata insieme alla UI principale.

## 0.3.104

- Energy UI: introdotti temi selezionabili (`Classic Inverter`, `Technical Dark`, `Minimal Light`).
- Nuovo layout `Classic Inverter` piu vicino al mock: flow board con nodi FV/Casa/Rete/Batteria e KPI laterali.
- Tema impostabile da `Setting > Energy` e forzabile da URL `?view=energy&theme=...`.
- Persistenza tema nelle opzioni addon (`energy.theme`) e disponibilita nel payload backend.

## 0.3.103

- Nuova pagina dedicata `Energy` per UI User, accessibile via `?view=energy` (layout senza pulsanti locali di navigazione).
- Dashboard energia con potenze realtime (FV, casa, rete, batteria), SOC batteria e KPI giornalieri.
- Nuova sezione `Setting > Energy` per taratura entita Home Assistant:
  `pv_power`, `home_power`, `grid_power`, `battery_power`, `battery_soc`,
  `pv_energy_today`, `home_energy_today`, `grid_import_today`, `grid_export_today`, `pv_installed_kwp`.
- Backend esteso con snapshot energia (`payload.energy`) e normalizzazione unita W/kW e Wh/kWh.

## 0.3.101

- Fix layout smartphone UI User (`?view=user`): ridisegnati breakpoint mobile per logo, mappa, controlli simulazione e card KPI.
- Timeline mobile resa leggibile (etichette orarie diradate), toggle impilati su singola colonna e spaziatura migliorata.
- Ordine blocchi ottimizzato su schermi piccoli: mappa prima, legenda subito sotto, niente overlap/affollamento.

## 0.3.100

- Hardening polling UI User/Admin su proxy instabile: `loadData()` ora evita richieste concorrenti a `api/data`.
- Aggiunto backoff esponenziale (fino a 60s) dopo errori HTTP/fetch su `api/data` per ridurre 502 ripetuti e stabilizzare la UI.
- Nessun crash UI: in caso di errore dati, la pagina resta attiva e riprova automaticamente con ritmo degradato.

## 0.3.99

- Rimossa la vista `user-lite`: ripristinata `UI User` standard con mappa come configurazione principale.
- Test stabilita WebView: disattivato splash su `view=user` (delay 0) per eliminare possibili race iniziali overlay/render.

## 0.3.98

- Aggiunta nuova vista `UI User Lite` senza mappa/Leaflet per ambienti WebView instabili.
- Accesso via query string: `?view=user-lite` (alias: `ui-user-lite`, `user_public_lite`).
- Vista lite mantiene KPI e dati meteo/stazione principali ma evita completamente bootstrap mappa.

## 0.3.97

- Aggiunti endpoint diagnostici static asset per validazione proxy/WebView:
  - `GET /api/diag/static_hashes` (hash/size dei file statici principali e riferimenti `index-*.js/css`)
  - `GET /api/diag/static_hash?path=...` (hash/size di un file statico specifico)
- Scopo: confronto oggettivo hash/size tra upstream e proxy per individuare truncation/alterazioni.

## 0.3.96

- Hardening WebView: build frontend non minificata (`minify: false`, `cssMinify: false`) per ridurre rischi di parse-error su ambienti embedded/proxy.
- Compatibilita runtime: bootstrap app con retry mount (fino a 3 tentativi) prima di mostrare errore bloccante.
- Target build impostato a `es2018` per maggiore compatibilita con WebView legacy.

## 0.3.95

- WebView hardening: `loadData()` ora gestisce errori fetch (`ERR_EMPTY_RESPONSE`) senza eccezioni non catturate.
- Ridotto rumore/retry mappa durante polling: su refresh periodico non parte piu la catena retry aggressiva se container non presente.
- Retry mappa resta attivo su mount/cambio vista, ma con fallback non bloccante.

## 0.3.94

- Fix bootstrap mappa (WebView/Control4/Android): inizializzazione resa lazy e solo su viste `user`/`user_public`.
- Aggiunte guardie robuste su container DOM mappa con retry controllato (max 20 tentativi, 100ms) senza crash globale UI.
- Aggiunta protezione idempotente (`dataset.mapInit`) contro doppia inizializzazione e race su tab switch.
- Migliorata gestione tab switch: `invalidateSize()` e redraw solo quando mappa realmente pronta.
- Fallback non bloccante: in assenza container la UI continua ad avviarsi e logga warning.

## 0.3.93

- Fix encoding UI: corretti caratteri corrotti/mojibake in tutte le schermate (`Â°`, `Ã`, frecce, simboli unita).
- Tooltip mappa e testi meteo ripuliti (es. `Az ... -> ...`, `°C`, `W/m²`, `Tiles © Esri`).
- Corrette anche le unita MQTT diagnostiche backend (`°`, `°C`, `µg/m³`).

## 0.3.92

- Fix logo UI Admin in Ingress: il logo principale ora e bundlato da `src/assets/logo-main.png` (niente richiesta `GET /logo.png` su root Home Assistant).
- Eliminato errore browser `logo.png 404` in apertura da Ingress.

## 0.3.91

- Fix Ingress Home Assistant: build frontend con path relativi (`base: './'`) per evitare richieste errate a `/assets/...` su root HA.
- Fix Ingress API: endpoint frontend chiamati con path relativi (`api/...`) invece di assoluti (`/api/...`).
- Corretto riferimento logo UI Admin per evitare errore di build frontend.

## 0.3.90

- Fix compatibilita manifest addon: rimosso `ingress_entry` da `config.yaml` (chiave non supportata su alcune installazioni Home Assistant).
- Ripristinata visibilita addon nella raccolta/repository.

## 0.3.89

- Bump versione correttivo: riallineata release dopo numerazione gia in uso.
- Confermato fix accesso ingress/sidebar Home Assistant (`ingress_entry: true`).

## 0.3.88

- Addon: aggiunto `ingress_entry: true` in configurazione per rendere stabile l'apertura da sidebar Home Assistant (ingress).
- Fix accesso UI da Home Assistant: allineata configurazione ingresso pannello addon.

## 0.3.87

- UI User: aumentata la spaziatura tra mappa e controlli orari (simulazione/flag) per evitare elementi troppo a ridosso della mappa.
- UI User: aggiunto contenitore visivo dedicato ai controlli mappa sotto la vista Leaflet per separazione piu chiara.

## 0.3.86

- UI User: aggiunto slider simulazione oraria (stesso `timeIndex` della UI Admin) con orario simulato visibile.
- UI User: aggiunti toggle flag mappa visibili in pagina user (allineati ai controlli Admin).

## 0.3.85

- UI User mappa: ora usa lo stesso renderer della UI Admin (`drawSolarOverlay`) con stessi overlay e stessa geometria (linee, cerchi, settori, assi, arco solare, vento).
- Uniformato il comportamento tra `UI Admin` e `UI User` passando sul medesimo motore grafico.

## 0.3.84

- UI User: logo e-Tende portato al doppio delle dimensioni.
- UI User: splash iniziale con logo e-Tende per 3 secondi su apertura pagina user (`/?view=user`).
- UI User: alzata l'altezza header per evitare taglio logo.

## 0.3.83

- UI User: logo e-Tende ingrandito in testata.

## 0.3.82

- UI User header: logo e-Tende centrato.
- Rimossi ora e data dalla UI User.
- Corrette proporzioni header per evitare taglio elementi.

## 0.3.81

- UI User: risolto logo e-Tende usando import asset compilato (`src/assets/logo-etende.png`).
- UI User: rimosso il menu superiore (`PANORAMICA/TENDE/...`) come richiesto.
- UI Admin: mantenuto un solo accesso a UI User (`/?view=user`).

## 0.3.80

- UI Admin: unificato accesso `UI User` in un solo elemento (rimosso duplicato tasto+link).
- UI User: sostituito logo con asset ufficiale e-Tende (`logo-etende.png`) dal componente.
- Corretto rendering caratteri speciali in UI (`°`, `°C`).

## 0.3.79

- Aggiunto link dedicato alla `UI User`: `/?view=user`.
- `UI User` ora apre direttamente via query string (`view=user`, `view=ui-user`, `view=user_public`).
- Integrato logo `e-Tende Intelligenti` nella `UI User` (`/logo-etende.png`).

## 0.3.78

- `UI User` resa molto piu vicina al layout di riferimento: pagina standalone senza barra admin, top header dedicato, sidebar legenda colori per tende e vento.
- Mappa `UI User` potenziata con overlay grafici (raggi alba/tramonto, arco solare, etichette `Alba`/`Tramonto`, settori tende).
- Migliorata gerarchia visiva della schermata utente (proporzioni titolo/ora, blocchi laterali e card stato).

## 0.3.77

- Aggiunta nuova pagina `UI User` dedicata, senza pulsanti/link verso le altre sezioni.
- Rinominata pagina esistente in `UI Admin` e aggiunto accesso a `UI User` dalla barra admin.
- Nuova `UI User` con layout dashboard ispirato al mock richiesto: header dedicato, sidebar meteo, mappa grande e cards stato in basso.

## 0.3.76

- User UI meteo: migliorato layout dashboard con cards compatte e allineamento `start` per eliminare i grandi vuoti verticali.
- Corretto stretch dei badge in header card (`source-head`) e resa leggibile uniforme delle metriche.
- Rifinita gerarchia visiva (titoli card, sfondi, separatori) per una lettura molto piu chiara.

## 0.3.75

- Fix backend `api/data` 500: risolto `UnboundLocalError` in `_build_weather_guard` quando la stazione meteo reale risulta gia selezionata e la lista candidati web non veniva inizializzata.

## 0.3.74

- Restyling User UI meteo con layout piu pulito e leggibile: metriche allineate in righe chiave/valore.
- Migliorata sezione `Reali Stazione Meteo` con badge stato chiari (`WG`, `Stazione SI/NO`) e pannello Weather Guard separato.
- Elenco completo entita stazione spostato in blocco espandibile, per ridurre rumore visivo mantenendo tutti i dati disponibili.

## 0.3.73

- Fix disponibilita stazione meteo: il calcolo freschezza ora usa il timestamp piu recente tra le entita lette, non il piu vecchio.
- Risolto falso `Stazione disponibile: NO` quando alcuni sensori (tipicamente pioggia a zero) non aggiornano spesso il `last_updated`.

## 0.3.72

- Weather Station auto-discovery migliorato: fallback piu robusti per evitare campi vuoti (in particolare temperatura/umidita esterna quando i nomi entita non contengono `outdoor`).
- Estesa configurazione Weather Station in Setting con campi completi: `Dew Point`, `Feels Like`, `Solar Lux`, `Solar Radiation`, `VPD`.
- User UI: sezione `Reali Stazione Meteo` ora mostra anche l'elenco completo delle entita rilevate dalla stazione con valore e unita.
- Migliorata lettura dati reali stazione/web mantenendo fallback automatico Weather Guard.

## 0.3.71

- User UI: aggiunto auto-refresh periodico dati (polling ogni 15 secondi) quando la tab attiva e `User UI`.
- Eliminata necessità di refresh manuale continuo per aggiornare meteo/sonde/stazione/FV.

## 0.3.70

- User UI chiarezza sorgenti: testi stato WG/stazione resi espliciti (`fallback`, `stazione disponibile SI/NO`, allarmi meteo leggibili).
- Stazione meteo: aggiunti sensori importanti in mapping/visualizzazione (`Dew Point`, `Temperatura percepita`, `Solar Lux`, `Solar Radiation`, `VPD`).
- Auto-discovery `device_id` esteso ai nuovi sensori Ecowitt.

## 0.3.69

- User UI dati meteo: visualizzazione completa di tutti i campi `normalized` disponibili per `Meteo Web` e `Stazione Meteo`, non piu solo subset fisso.
- Aggiunte etichette leggibili, unita automatiche e ordinamento coerente dei campi per migliorare chiarezza origine dati.

## 0.3.68

- User UI: riorganizzata sezione dati in blocchi chiari per sorgente (`Meteo Web`, `Reali Sonde`, `Reali Stazione Meteo`, `Fotovoltaico`).
- Migliorata leggibilita origine dati con etichette esplicite e stato sorgente attiva per Weather Guard.

## 0.3.67

- User UI mappa vento: migliorata chiarezza visiva della linea con label esplicita `VENTO DA ...` e testa linea evidenziata.
- Rimossa mini-legenda accanto al toggle per mantenere interfaccia pulita, spostando il significato direttamente sulla traccia mappa.

## 0.3.66

- Completata fix toggle vento mappa: render del layer vento reso indipendente da `drawSolarOverlay` con `ensureWindDirectionLayer()`.
- Aggiunto cleanup/retry timer dedicato e watcher diretto su vento (`mapWindDirDeg/mapWindMs`) per ri-disegno affidabile dopo OFF/ON.
- Corretto caso residuo in cui la linea non tornava nonostante il ri-enable del flag.

## 0.3.65

- User UI mappa vento: fix definitivo toggle OFF/ON con inizializzazione immediata cache vento (`watch ... immediate`) e doppio redraw anti-race al ri-enable.
- Migliorata persistenza visiva della linea vento usando ultimo valore valido direzione/velocita.

## 0.3.64

- User UI mappa vento: fix toggle OFF/ON della direzione vento con fallback robusto su `weather_guard` e ultimo valore valido noto.
- Aggiunti watcher dedicati per forzare ridisegno overlay vento al cambio flag, evitando casi in cui la linea non riappare.

## 0.3.63

- Fix runtime Leaflet: esteso guard anti-race anche a `Control.addTo(...)` (non solo `Layer.addTo(...)`) per evitare crash su target mappa/control temporaneamente null.
- Stabilizzata User UI nei toggle/refresh rapidi della mappa.

## 0.3.62

- Fix runtime User UI: introdotto guard globale Leaflet su `Layer.addTo(...)` per evitare crash quando il target mappa risulta temporaneamente `null` durante race di rendering/tab switch.
- Risolto errore bootstrap: `TypeError: Cannot read properties of null (reading 'addLayer')`.

## 0.3.61

- Frontend bootstrap hardening: aggiunto fail-safe in `main.js` con gestione errori globali (`error` e `unhandledrejection`) e pannello errore a schermo.
- In caso di crash runtime iniziale, la UI non resta piu su pagina blu vuota: mostra il messaggio tecnico da condividere per diagnosi immediata.

## 0.3.60

- Fix User UI: aggiunto failsafe splash screen per evitare pagina blu vuota in caso di errore JS durante init (`onMounted`).
- La splash viene chiusa comunque dopo timeout breve e l'init e protetto con `try/catch`.

## 0.3.59

- User UI Meteo: etichette stazione reale rese esplicite (`WS Temperatura esterna`, `WS Umidita esterna`, `WS Pressione`, `WS Indice UV`, `WS Pioggia`, `WS Vento`).
- User UI Mappa: aggiunto flag `Direzione vento su mappa` per mostrare/nascondere freccia vento con velocita.
- Rendering vento su mappa: priorita ai dati stazione reale, fallback ai dati meteo web.

## 0.3.58

- Weather Station UI: auto-fill da `device_id` eseguito anche al caricamento della pagina Settings quando il campo e gia valorizzato.
- Risolto caso in cui i campi restavano vuoti finche l'utente non modificava manualmente il campo `device_id`.

## 0.3.57

- Weather Station UI: auto-compilazione campi sensori quando viene impostato `device_id` (auto-discovery), senza sovrascrivere valori manuali gia presenti.
- Nuovo endpoint `GET /api/weather_station/autofill` per preview/mapping automatico entita da `device_id`.
- Auto-mapping Ecowitt migliorato con criteri ibridi (nome entita + `device_class` + unita), riducendo i casi di campi vuoti.

## 0.3.56

- Weather Station: aggiunto supporto `device_id` con auto-discovery entita meteo da Home Assistant (`device_entities`), mantenendo priorita ai campi `entity_id` manuali quando compilati.
- Weather Station: aggiunti campi opzionali extra per Ecowitt (`outdoor_temp_entity_id`, `outdoor_humidity_entity_id`, `pressure_entity_id`, `uv_index_entity_id`).
- Weather Guard: priorita esplicita ai dati stazione reale quando validi e freschi; fallback API web (MET/Open-Meteo) solo se stazione assente/non valida/stale.
- UI Settings: estesa sezione `Weather Station e-Control` con `device_id` e campi sensori extra.

## 0.3.55

- UI Wizard Tende/Cover: rinominato titolo in `Wizard taratura cover`.

## 0.3.54

- UI Wizard Tende/Cover: aggiunto simulatore `What-if` nello step Verifica per confrontare configurazione attuale e proposta prima del salvataggio.

## 0.3.53

- UI Wizard Tende/Cover: nascosto il pulsante `Avanti` nell'ultimo step.

## 0.3.52

- UI Wizard Tende/Cover: aggiunte spiegazioni brevi per ogni parametro e per i preset guidati.

## 0.3.51

- UI Tende/Cover: aggiunto wizard guidato per taratura cover con step Base, Sole, Posizioni, Meteo, Termico e Verifica.

## 0.3.50

- UI grafici: ridotta la dimensione dei font SVG per assi, titoli asse e tooltip su grafici aria/FV/meteo.

## 0.3.49

- UI Tende/Cover: aggiunta configurazione strategia termica da termostato climate condivisibile tra piu cover.
- Diagnostica Tende/Cover: mostrati termostato, modalita, temperatura interna, setpoint e decisione termica.

## 0.3.48

- Fix versione UI/API: allineato `APP_VERSION` backend a `0.3.48`, così il titolo mostra la release reale invece di `0.3.40`.

## 0.3.47

- UI Tende/Cover: aggiunto campo `Anti-loop comandi sec.` e diagnostica blocco/rate-limit ricevuta da e-Tende.

## 0.3.46

- UI Tende/Cover: aggiunta heatmap `sole-finestra` sotto la mappa taratura con fasce orarie, durata utile, picco e prossima esposizione.

## 0.3.45

- UI Tende/Cover: aggiunta linea visibile `Facciata` sulla mappa taratura usando `facade_azimuth_deg`.

## 0.3.44

- UI Tende/Cover: aggiunto campo `Azimut facciata stravento`, separato da `Azimut finestra`.
- Salvataggio Tende/Cover: il payload verso e-Tende include `facade_azimuth_deg` per la logica pioggia/vento.

## 0.3.43

- UI Tende/Cover: i quattro campi `Posizione sicurezza` sono raggruppati sulla stessa riga desktop.
- UI Tende/Cover: layout responsive del gruppo posizioni sicurezza mantenuto a due colonne su mobile.

## 0.3.42

- UI Tende/Cover: aggiunti controlli `Usa logica sole` e `Inverti logica sole` per allineamento con e-Tende 0.1.72.
- Salvataggio Tende/Cover: il payload verso e-Tende include `sun_logic_enabled` e `invert_sun_logic`.
- Diagnostica Tende/Cover: mostrato lo stato runtime della logica sole quando presente nei sensori mappa.

## 0.3.41

- UI Tende/Cover: selezione e rendering lista cover ora usano una chiave robusta (`id|cover_entity|name`), evitando sparizioni quando il payload live non contiene `id` stabile.
- UI Tende/Cover: dopo `Salva taratura`, e-SunMind applica subito l'aggiornamento in cache locale pagina (optimistic update), senza richiedere refresh manuale.
- UI Tende/Cover: migliorato messaggio stato `sent_no_ack`, con conferma applicazione locale e attesa automatica della conferma mappa.

## 0.3.40

- Salvataggio Tende/Cover: `/api/tende/map/update` pubblica sul topic primario, attende ACK o conferma mappa, poi riprova sul topic fallback storico se non arriva conferma.
- Salvataggio Tende/Cover: il publish MQTT attende l'accodamento QoS prima di aspettare ACK/mappa, riducendo falsi `ack_timeout`.
- UI Tende/Cover: la lista visualizzata fonde sempre cache valida e payload live, quindi un refresh parziale non nasconde piu la cover selezionata.

## 0.3.39

- UI Tende/Cover: la cache cover valida viene aggiornata in merge e non sostituita da payload parziali, evitando che una cover sparisca dopo il salvataggio e resti assente fino al refresh pagina.

## 0.3.38

- UI Tende/Cover: dopo un salvataggio senza ACK, la pagina verifica i valori ricaricati dalla mappa e mostra `applicata` se coincidono.
- UI Tende/Cover: mantiene l'ultima lista valida di cover durante refresh temporanei vuoti/stale, evitando che la cover selezionata sparisca e ritorni solo dopo refresh pagina.

## 0.3.37

- `/api/tende/map/update` non risponde piu 504 quando il comando MQTT e stato pubblicato ma l'ACK non arriva: torna `ok=true`, `status=sent_no_ack`.
- UI Tende/Cover distingue `ACK ricevuto`, `confermato da mappa` e `inviato senza ACK`, evitando errore rosso su salvataggi applicati ma con ACK perso.

## 0.3.36

- Salvataggio Tende/Cover: pubblicazione comando su un solo topic primario per evitare doppia elaborazione dello stesso `request_id`.
- Se l'ACK manca o arriva negativo ma il payload mappa conferma che le tarature sono state applicate, `/api/tende/map/update` risponde OK con `status=confirmed_by_map`.

## 0.3.35

- Fix gestione ACK salvataggio Tende/Cover: e-SunMind ora attende un ACK positivo e non fallisce subito se riceve prima un ACK negativo duplicato.
- La risposta `/api/tende/map/update` include eventuali ACK negativi secondari in `ack_errors` solo come diagnostica.

## 0.3.34

- Salvataggio Tende/Cover piu robusto: il comando verso e-Tende include anche il nome cover.
- `/api/tende/map/update` accetta come target anche `cover_entity` quando manca l'ID, mantenendo retrocompatibilita.
- Migliorata compatibilita con e-Tende 0.1.69 per evitare `ack_negative shade_not_found` quando l'ID runtime non e allineato.

## 0.3.33

- Aggiunto endpoint stabile `GET /api/sun/live` usato da e-Tende per azimut/elevazione sole.
- Alleggerito MQTT `runtime_json`: i payload raw meteo/FV/aria restano in API/UI tecnica ma non vengono piu pubblicati come attributi MQTT per evitare limite recorder 16 KB.

## 0.3.32

- Fix salvataggio Tende/Cover: e-SunMind ora attende la connessione MQTT e registra le subscribe ACK prima di pubblicare il comando verso e-Tende.
- Migliorata diagnostica errore quando il broker MQTT non risponde in fase di comando.

## 0.3.31

- Pagina `Tende/Cover`: editor completo della cover selezionata con tarature, protezioni meteo e diagnostica runtime.
- `/api/tende/map/update` ora invia a e-Tende anche `settings` completi, mantenendo compatibilita con i campi flat esistenti.
- Payload tende normalizzato con `settings` e `sensors` per ogni cover.
- Mappa taratura cover focalizzata sulla sola cover selezionata con linea alba, tramonto, curva elevazione reale e linea sole live.

## 0.3.30

- Weather guard piu robusto quando il runtime non contiene meteo valido.
- `/api/weather/guard` e `/api/data` recuperano fallback da cache MET/Open-Meteo.
- Se la cache meteo non contiene timestamp, viene usato il timestamp del file cache.

## 0.3.29

- Aggiunta pagina `Setting` con salvataggio unico `Salva tutto`.
- Spostati i form di configurazione fuori dalla pagina `Tecnica`.
- Aggiunti testi guida per `Weather Guard` e configurazione stravento.

## 0.3.28

- Stabilizzato contratto `/api/weather/guard` per e-Tende 0.1.55.
- Confermati campi root: `wind_alarm`, `rain_alarm`, `facade_rain_risk`, `severe_weather_alarm`.
- Oggetto debug `station` sempre presente con: `enabled`, `ok`, `used`, `error`, `age_seconds`.
- `station.used=true`: dati da stazione reale e-Control/Ecowitt.
- `station.used=false`: fallback MET/Open-Meteo o stazione non valida.
