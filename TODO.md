# TODO

## Alta priorita
- Verificare build addon in Home Assistant Supervisor.
- Verificare apertura UI via Ingress e via porta 1977.
- Verificare aggiornamento periodico `/api/data`.
- Verificare discovery MQTT sensori in HA con `mqtt.enabled: true`.
- [KFlow/Livoltek] Correggere widget Remaining batteria: usare soglia scarica configurata (es. 10%) invece di mostrare/calcolare MIN SOC 0%.
- [KFlow/Livoltek] Verificare sorgenti `sensor.kflow_grid_import_power`, `sensor.kflow_battery_charge_power`, `sensor.kflow_battery_discharge_power`: gli integrali restano `unknown` finche le sorgenti non sono numeriche.

## Media priorita
- Aggiungere piu sensori publish (sunrise, sunset, moonrise, moonset).
- Aggiungere endpoint health check esteso (`/api/health`).
- Aggiungere logging strutturato con livelli coerenti su opzione `log_level`.
- [KFlow/Livoltek] Evitare doppio conteggio in Home Assistant Energy: usare o le 3 energie Shelly separate o `sensor.kflow_load_energy_total`, non entrambe.
- [KFlow/Livoltek] Creare/validare Utility Meter giornaliero `sensor.kflow_load_energy_today` da `sensor.kflow_load_energy_total` per il campo Today Load.

## Bassa priorita
- Migliorare UI (filtri, viste compatte, export dati).
- Aggiungere test automatici minimi backend.
