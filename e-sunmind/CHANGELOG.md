# Changelog

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
