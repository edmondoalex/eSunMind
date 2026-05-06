# WORKLOG

## 2026-05-06
- Fix UI integrazione e-SunMind ↔ e-Tende: la cover non sparisce piu dopo salvataggio anche con payload mappa parziale/senza `id` stabile.
- Aggiornata selezione cover in pagina su chiave robusta (`id|cover_entity|name`).
- Aggiunto aggiornamento ottimistico locale dopo `POST /api/tende/map/update` per evitare refresh manuale.
- Bump versione addon a `0.3.41` con changelog aggiornato.

## 2026-05-03
- Portato addon e-SunMind a architettura stile e-ThermoMind.
- Aggiunta Web UI con FastAPI + pagina integrata.
- Aggiunto calcolo dati sole/luna con coordinate manuali o `location_query`.
- Aggiunta pubblicazione entita su Home Assistant via MQTT Discovery.
- Aggiornata porta web addon da 8098 a 1977 (ingress + expose + uvicorn).
