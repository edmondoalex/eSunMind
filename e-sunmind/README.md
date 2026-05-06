# e-SunMind Add-on

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
