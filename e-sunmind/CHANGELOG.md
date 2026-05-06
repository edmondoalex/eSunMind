# Changelog

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
