# ISTRUZIONI

## Installazione addon repository
1. Home Assistant -> Impostazioni -> Add-on -> Add-on Store.
2. Menu (tre puntini) -> Repositories.
3. Aggiungi `https://github.com/edmondoalex/eSunMind`.
4. Apri addon `e-SunMind` e installa.

## Configurazione minima
- `timezone`: es. `Europe/Rome`
- `location_query`: es. `Cuneo, Italy` (opzionale)
- oppure `latitude` + `longitude` manuali
- `interval_minutes`: intervallo aggiornamento dati

## Pubblicazione entita in Home Assistant
- Imposta `mqtt.enabled: true`
- Configura host/porta/credenziali broker MQTT
- Riavvia addon
- Controlla in HA la comparsa dei sensori discovery `sunmind_*`

## Accesso web
- Ingress addon da Home Assistant
- Porta diretta container: `1977`

## API locali
- `GET /api/status`
- `GET /api/data`