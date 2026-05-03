# e-SunMind Add-on Repository

Addon Home Assistant con stile operativo simile a e-ThermoMind:
- Web UI via Ingress/porta
- calcolo dati sole/luna con coordinate o ricerca localita
- pubblicazione entita su HA via MQTT Discovery

## Accesso UI

- Ingress HA: pannello addon
- Porta diretta: `1977`

## Configurazione

- `latitude`, `longitude`, `timezone`
- `location_query` (opzionale: se valorizzato, usa ricerca coordinate)
- `interval_minutes` (intervallo aggiornamento)
- blocco `mqtt` per pubblicare entita in Home Assistant

## Entita pubblicate (MQTT Discovery)

- `sensor.sun_altitude`
- `sensor.sun_azimuth`
- `sensor.moon_altitude`
- `sensor.moon_azimuth`
- `sensor.moon_illumination`

## API locale

- `GET /api/status`
- `GET /api/data`
