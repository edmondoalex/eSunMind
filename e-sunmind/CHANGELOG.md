# Changelog

## 0.3.28

- Stabilizzato contratto `/api/weather/guard` per e-Tende 0.1.55.
- Confermati campi root: `wind_alarm`, `rain_alarm`, `facade_rain_risk`, `severe_weather_alarm`.
- Oggetto debug `station` sempre presente con: `enabled`, `ok`, `used`, `error`, `age_seconds`.
- `station.used=true`: dati da stazione reale e-Control/Ecowitt.
- `station.used=false`: fallback MET/Open-Meteo o stazione non valida.

