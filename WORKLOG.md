# WORKLOG

## 2026-05-06
- UI Tende/Cover: aggiunta linea mappa `Facciata` per visualizzare l'azimut stravento separato dal sole.
- Bump versione addon a `0.3.45` con changelog aggiornato.
- UI Tende/Cover: aggiunto `Azimut facciata stravento` per separare pioggia/vento da `Azimut finestra` usato dal sole.
- Bump versione addon a `0.3.44` con changelog aggiornato.
- UI Tende/Cover: raggruppati i quattro campi `Posizione sicurezza` sulla stessa riga desktop.
- Bump versione addon a `0.3.43` con changelog aggiornato.
- Allineato addon e-SunMind a e-Tende 0.1.72: aggiunti controlli `Usa logica sole` e `Inverti logica sole` nella pagina Tende/Cover.
- Il salvataggio taratura ora invia anche `sun_logic_enabled` e `invert_sun_logic` verso e-Tende.
- Bump versione addon a `0.3.42` con changelog aggiornato.
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
