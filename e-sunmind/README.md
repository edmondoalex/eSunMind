# e-SunMind Add-on

## Energy card setup

- Configurazione completa Sunsynk card in UI Admin -> Setting -> Energy.
- Wizard e campi avanzati permettono di impostare topologia, colori, icone, linee, velocita animazioni e tutte le entita principali.
- La dashboard energy-dashboard/sunsynk-wrapper.html carica automaticamente questa configurazione.

## API for integrations

Endpoint stabile per integrazione componenti esterni (es. e-Tende Intelligenti):

- `GET /api/sun/live`

Risposta `200`:

```json
{
  "ok": true,
  "azimuth_compass_deg": 134.25,
  "altitude_deg": 53.74,
  "updated_at": "2026-05-04T11:41:08.399000+02:00",
  "source": "e-sunmind"
}
```

Risposta `503` quando dati non pronti:

```json
{
  "ok": false,
  "error": "data_not_ready"
}
```

Esempio curl:

```bash
curl -sS http://192.168.3.24:1980/api/sun/live
```

### Tende/Cover centralizzate

La pagina `Tende/Cover` usa il payload MQTT di e-Tende per mostrare ogni cover con:

- `settings`: tarature modificabili della cover
- `sensors`: diagnostica runtime della cover
- stato reale cover letto da e-Control

Il salvataggio usa `POST /api/tende/map/update`, invia un comando MQTT a e-Tende e considera la modifica applicata solo dopo ACK positivo.
Da `0.3.32` il comando attende la connessione MQTT e la registrazione delle subscribe ACK prima del publish, evitando timeout causati da ACK troppo veloci.
Da `0.3.33` `/api/sun/live` e reale nel backend e il `runtime_json` MQTT resta compatto: i payload raw completi rimangono disponibili in API/UI tecnica ma non come attributi MQTT.
Da `0.3.34` il comando invia anche il nome cover e accetta target senza `id` quando e presente `cover_entity`, per allinearsi al lookup robusto di e-Tende 0.1.69.
Da `0.3.35` un ACK negativo duplicato non blocca piu il salvataggio se entro timeout arriva anche l'ACK positivo.
Da `0.3.36` il comando viene pubblicato su un solo topic primario e, se l'ACK non arriva, il salvataggio viene confermato dal payload mappa aggiornato.
Da `0.3.37` l'assenza di ACK non genera piu HTTP 504 se il comando e stato pubblicato; la UI segnala `inviato senza ACK` e aggiorna la mappa dopo un breve ritardo.
Da `0.3.38` la UI mantiene l'ultima lista valida di cover durante refresh temporanei e segnala `applicata` quando i valori ricaricati dalla mappa coincidono.
Da `0.3.39` la UI fonde i payload mappa parziali con l'ultima lista valida, quindi una cover non viene rimossa solo perche manca in un refresh temporaneo.
Da `0.3.40` il salvataggio riprova anche sul topic MQTT fallback storico se il topic primario non produce ACK/conferma mappa, e la UI non rimuove piu cover presenti in cache quando il payload live e parziale.

### Weather guard per e-Tende

Endpoint sicurezza meteo:

- `GET /api/weather/guard`

Risposta `200`:

```json
{
  "ok": true,
  "enabled": true,
  "wind_speed_ms": 4.3,
  "wind_gust_ms": null,
  "wind_dir_deg": 287.6,
  "rain_rate_mm_h": 0.2,
  "rain_1h_mm": 0.2,
  "facade_rain_risk": false,
  "wind_alarm": false,
  "rain_alarm": false,
  "severe_weather_alarm": false,
  "updated_at": "2026-05-05T12:00:00+02:00"
}
```

Risposta `503` quando il runtime non ha ancora prodotto dati:

```json
{
  "ok": false,
  "error": "data_not_ready"
}
```

Gli stessi dati sono inclusi in `GET /api/data` nel blocco `weather_guard` e quindi anche nel payload MQTT `runtime_json`.

e-Tende deve leggere:

- `wind_alarm`: protezione vento forte.
- `rain_alarm`: protezione pioggia.
- `facade_rain_risk`: stravento, cioe pioggia con vento nel cono della facciata.
- `severe_weather_alarm`: allarme aggregato, vero se uno dei tre allarmi e attivo.
- `station.used`: `true` quando gli allarmi derivano dalla stazione reale e-Control/Ecowitt.
- `station.used`: `false` quando e-SunMind sta usando fallback MET/Open-Meteo oppure la stazione non e valida.

Nota config: `facade_azimuth_deg = -1` significa facciata non configurata; in API viene restituito `null`.

Contratto stabile per e-Tende: i campi root di `/api/weather/guard` restano retrocompatibili e l'oggetto `station` contiene sempre `enabled`, `ok`, `used`, `error`, `age_seconds`.

### Weather irrigation per e-Dry

Endpoint meteo stabile per irrigazione:

- `GET /api/weather/irrigation`

Contratto:

- tutti i campi root sono sempre presenti;
- i valori non disponibili vengono restituiti come `null`;
- `source` vale `local_station` quando il dato arriva dalla stazione meteo locale valida, altrimenti `fallback_web`;
- `age_seconds` e `available` permettono a e-Dry di capire se il dato e fresco;
- `hourly_forecast[]` e `daily_forecast[]` sono inclusi quando disponibili dal provider web.

Risposta `200` esempio:

```json
{
  "temperature_c": 27.4,
  "humidity_pct": 48.0,
  "pressure_hpa": 1014.2,
  "dew_point_c": 15.6,
  "wind_speed_ms": 3.8,
  "wind_gust_ms": 5.1,
  "wind_bearing_deg": 220.0,
  "rain_rate_mm_h": 0.0,
  "rain_today_mm": null,
  "rain_last_24h_mm": null,
  "precip_probability_pct": 35.0,
  "forecast_rain_24h_mm": 4.8,
  "solar_radiation_w_m2": 640.0,
  "uv_index": 6.1,
  "cloud_cover_pct": 28.0,
  "soil_moisture_pct": 31.0,
  "soil_temperature_c": 21.8,
  "et0_mm_day": 4.2,
  "weather_code": 2,
  "condition": "cloudy",
  "last_update": "2026-06-03T14:10:00+02:00",
  "source": "local_station",
  "age_seconds": 42.0,
  "available": true,
  "is_raining": false,
  "rain_block": false,
  "wind_block": false,
  "freeze_block": false,
  "hot_day": false,
  "dry_day": true,
  "irrigation_weather_score": 100,
  "irrigation_weather_reason": "dry_day",
  "hourly_forecast": [],
  "daily_forecast": [],
  "schema": "e_sunmind_irrigation_weather.v1"
}
```

Risposta `503` quando il runtime non e ancora pronto:

```json
{
  "temperature_c": null,
  "humidity_pct": null,
  "pressure_hpa": null,
  "dew_point_c": null,
  "wind_speed_ms": null,
  "wind_gust_ms": null,
  "wind_bearing_deg": null,
  "rain_rate_mm_h": null,
  "rain_today_mm": null,
  "rain_last_24h_mm": null,
  "precip_probability_pct": null,
  "forecast_rain_24h_mm": null,
  "solar_radiation_w_m2": null,
  "uv_index": null,
  "cloud_cover_pct": null,
  "soil_moisture_pct": null,
  "soil_temperature_c": null,
  "et0_mm_day": null,
  "weather_code": null,
  "condition": null,
  "last_update": null,
  "source": null,
  "age_seconds": null,
  "available": false,
  "is_raining": false,
  "rain_block": false,
  "wind_block": false,
  "freeze_block": false,
  "hot_day": false,
  "dry_day": false,
  "irrigation_weather_score": 0,
  "irrigation_weather_reason": "data_not_ready",
  "hourly_forecast": [],
  "daily_forecast": [],
  "schema": "e_sunmind_irrigation_weather.v1",
  "error": "data_not_ready"
}
```

### Stazione meteo reale opzionale

Il weather guard funziona anche senza stazione meteo, usando MET/Open-Meteo. Se e disponibile una stazione Ecowitt/GW1101 integrata in e-Control, si possono configurare le entita reali:

```yaml
weather_station:
  enabled: true
  provider: "e_control"
  stale_seconds: 180
  wind_speed_entity_id: "sensor.ecowitt_wind_speed"
  wind_gust_entity_id: "sensor.ecowitt_wind_gust"
  wind_direction_entity_id: "sensor.ecowitt_wind_direction"
  rain_rate_entity_id: "sensor.ecowitt_rain_rate"
  rain_1h_entity_id: "sensor.ecowitt_hourly_rain"
```

Priorita:

- stazione reale e-Control, se configurata e non stale;
- MET/Open-Meteo come fallback automatico;
- fail safe con `ok=false` e allarmi a `false` se non ci sono dati validi.

Le unita vengono normalizzate:

- vento sempre in `m/s`;
- rain rate sempre in `mm/h`;
- pioggia 1h sempre in `mm`.

## Energy Dashboard Standalone

Da .3.118 la dashboard energia usa di default un wrapper standalone basato sulla card originale di Slipx06 (sunsynk-power-flow-card) eseguita senza Home Assistant installato.
Da .3.245 ogni impianto puo scegliere il layout dashboard tra Sunsynk Power Flow e `k-flow-card`.

- Entry point: web/public/energy-dashboard/sunsynk-wrapper.html
- Routing default: web/public/energy-dashboard/index.html (redirect al wrapper)
- Runtime: mock window.hass con states, localize(), 	hemes e API minime necessarie
- Aggiornamento dati: funzione globale updateSensors(newData) per integrazione backend real-time
- Layout per-site: `energy_dashboard_layout` (`sunsynk` oppure `k_flow`)


### Config card da UI Addon

In Setting > Energy e disponibile il campo JSON sunsynk_card_config_json per impostare tutta la cardConfig del wrapper (solar, attery, load, grid, entities, ecc.) senza modificare file statici.
Il wrapper sunsynk-wrapper.html legge questa configurazione da /api/options all'avvio e la applica automaticamente.
Per `k-flow-card` il wrapper genera automaticamente la configurazione dai campi Energy/Sunsynk; il campo `k_flow_card_config_json` permette override avanzati.

### Wizard Energy (Sunsynk)

Da .3.122 in Setting > Energy e disponibile un wizard passo-passo per costruire la configurazione completa della card Sunsynk (sunsynk_card_config_json) senza edit manuale JSON.


- Wizard Energy: supporta anche selezione icone carichi (default, oiler, ircon, pump, oven) per nodi essenziali e non essenziali.

- Nota: la card Sunsynk usa colour (non color) nelle opzioni tema; il wizard Energy e allineato a questa sintassi.
