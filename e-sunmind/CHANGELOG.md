# Changelog

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
