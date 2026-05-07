# Changelog

## 0.3.47

- UI Tende/Cover: aggiunto campo `Anti-loop comandi sec.` e diagnostica blocco/rate-limit ricevuta da e-Tende.

## 0.3.46

- UI Tende/Cover: aggiunta heatmap `sole-finestra` sotto la mappa taratura con fasce orarie, durata utile, picco e prossima esposizione.

## 0.3.45

- UI Tende/Cover: aggiunta linea visibile `Facciata` sulla mappa taratura usando `facade_azimuth_deg`.

## 0.3.44

- UI Tende/Cover: aggiunto campo `Azimut facciata stravento`, separato da `Azimut finestra`.
- Salvataggio Tende/Cover: il payload verso e-Tende include `facade_azimuth_deg` per la logica pioggia/vento.

## 0.3.43

- UI Tende/Cover: i quattro campi `Posizione sicurezza` sono raggruppati sulla stessa riga desktop.
- UI Tende/Cover: layout responsive del gruppo posizioni sicurezza mantenuto a due colonne su mobile.

## 0.3.42

- UI Tende/Cover: aggiunti controlli `Usa logica sole` e `Inverti logica sole` per allineamento con e-Tende 0.1.72.
- Salvataggio Tende/Cover: il payload verso e-Tende include `sun_logic_enabled` e `invert_sun_logic`.
- Diagnostica Tende/Cover: mostrato lo stato runtime della logica sole quando presente nei sensori mappa.

## 0.3.41

- UI Tende/Cover: selezione e rendering lista cover ora usano una chiave robusta (`id|cover_entity|name`), evitando sparizioni quando il payload live non contiene `id` stabile.
- UI Tende/Cover: dopo `Salva taratura`, e-SunMind applica subito l'aggiornamento in cache locale pagina (optimistic update), senza richiedere refresh manuale.
- UI Tende/Cover: migliorato messaggio stato `sent_no_ack`, con conferma applicazione locale e attesa automatica della conferma mappa.

## 0.3.40

- Salvataggio Tende/Cover: `/api/tende/map/update` pubblica sul topic primario, attende ACK o conferma mappa, poi riprova sul topic fallback storico se non arriva conferma.
- Salvataggio Tende/Cover: il publish MQTT attende l'accodamento QoS prima di aspettare ACK/mappa, riducendo falsi `ack_timeout`.
- UI Tende/Cover: la lista visualizzata fonde sempre cache valida e payload live, quindi un refresh parziale non nasconde piu la cover selezionata.

## 0.3.39

- UI Tende/Cover: la cache cover valida viene aggiornata in merge e non sostituita da payload parziali, evitando che una cover sparisca dopo il salvataggio e resti assente fino al refresh pagina.

## 0.3.38

- UI Tende/Cover: dopo un salvataggio senza ACK, la pagina verifica i valori ricaricati dalla mappa e mostra `applicata` se coincidono.
- UI Tende/Cover: mantiene l'ultima lista valida di cover durante refresh temporanei vuoti/stale, evitando che la cover selezionata sparisca e ritorni solo dopo refresh pagina.

## 0.3.37

- `/api/tende/map/update` non risponde piu 504 quando il comando MQTT e stato pubblicato ma l'ACK non arriva: torna `ok=true`, `status=sent_no_ack`.
- UI Tende/Cover distingue `ACK ricevuto`, `confermato da mappa` e `inviato senza ACK`, evitando errore rosso su salvataggi applicati ma con ACK perso.

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
