# Changelog

## 0.3.324
- Energy Time: nella vista Giorno i valori dei cerchi usano prima i sensori giornalieri `*_today`, lasciando le statistiche storiche a grafico, mese e anno.
- Bump versione addon/backend a `0.3.324`.

## 0.3.323
- Energy Time: ripristinate le linee originali del flow storico K Flow, mantenendo le nuove icone dentro i cerchi.
- Bump versione addon/backend a `0.3.323`.

## 0.3.322
- Energy Time: rifinite le linee del flow storico K Flow, rimuovendo i nodi intermedi e usando curve piu pulite tra i cerchi principali.
- Bump versione addon/backend a `0.3.322`.

## 0.3.321
- Energy Time: ridisegnato il flow storico K Flow in stile Home Assistant Energy, con icone SVG nei nodi e valori import/export e carica/scarica dentro i cerchi.
- KFlow/Livoltek: aggiunti promemoria diagnostici su Remaining batteria, integrali `unknown`, doppio conteggio consumi e utility meter giornalieri.
- Bump versione addon/backend a `0.3.321`.

## 0.3.320
- UI: rimosso il link Livoltek iniettato a runtime dal backend; ora resta solo il tab Livoltek nativo della UI.
- Bump versione addon/backend a `0.3.320`.

## 0.3.319
- Livoltek: ripristinato come tab interno della UI principale, coerente con `Energy`, `Energy Setup`, `Setting` e `Tecnica`.
- Bump versione addon/backend a `0.3.319`.

## 0.3.318
- Livoltek: aggiunta pagina statica `energy-dashboard/livoltek.html`, accessibile da remoto come gli altri wrapper Energy Dashboard.
- UI: il link Livoltek punta alla pagina statica pubblica per evitare riscritture Ingress sulla SPA.
- Bump versione addon/backend a `0.3.318`.

## 0.3.317
- Livoltek: aggiunto alias HTML `/api/livoltek/page` per accesso remoto via Ingress quando i path custom vengono riscritti alla UI principale.
- Bump versione addon/backend a `0.3.317`.

## 0.3.316
- Livoltek: aggiunta pagina backend autonoma `/livoltek`, indipendente dal bundle Vue, per debug/config anche se Home Assistant serve asset UI vecchi.
- UI: aggiunta iniezione runtime del link `Livoltek` nella topbar dell'index servito dall'add-on.
- Bump versione addon/backend a `0.3.316`.

## 0.3.315
- UI: servito `index.html` senza cache per evitare vecchi menu in Home Assistant Ingress dopo aggiornamento add-on.
- Livoltek: aggiunto supporto diretto a `?view=livoltek`.
- Bump versione addon/backend a `0.3.315`.

## 0.3.314
- Livoltek: aggiunta sezione separata in UI con switch di abilitazione, configurazione, stato runtime e JSON grezzo redatto.
- Livoltek: aggiunti client/polling separati e endpoint debug per refresh, probe API e reinvio MQTT Discovery.
- Livoltek: aggiunti sensori Home Assistant via MQTT Discovery retained su topic dedicati `e-sunmind/livoltek`.
- Bump versione addon/backend a `0.3.314`.

## 0.3.313
- Energy Dashboard: i grafici PV del bottone `Grafici` ora si espandono per ogni PV configurato, invece di mostrare solo il primo sensore.
- Energy Dashboard: supportata la stessa espansione anche per le tensioni PV multiple.
- Bump versione addon/backend a `0.3.313`.

## 0.3.312
- Energy Dashboard: rimosso il drill-down fragile sul click dei valori dentro la card K Flow.
- Energy Dashboard: aggiunto bottone `Grafici` che apre una vista unica con i grafici singoli richiesti in elenco.
- Energy Dashboard: la vista grafici include PV W, casa/load W, rete W, batteria W, batteria %, batteria V, PV V e inverter V.
- Bump versione addon/backend a `0.3.312`.

## 0.3.311
- Energy Dashboard: il drill-down dei valori istantanei K Flow non usa piu testo interno della web component.
- Energy Dashboard: mappati click diretti su zone strette dei valori istantanei per PV W, batteria W/%/V, rete W e carico/casa W, senza bottoni/overlay.
- Bump versione addon/backend a `0.3.311`.

## 0.3.310
- Energy Time: la lettura statistiche HA richiede anche `sum` e `state`, non solo `change`.
- Energy Time: aggiunto fallback a delta progressivo da `sum/state` per evitare grafici Giorno/Mese tutti a zero quando HA non restituisce `change`.
- Bump versione addon/backend a `0.3.310`.

## 0.3.309
- Energy Time: ripristinato il popolamento di Giorno e Mese quando Home Assistant restituisce statistiche senza timestamp di bucket; la vista Anno resta vincolata ai timestamp per evitare mesi fittizi.
- Energy Dashboard: corretto il drill-down dei click su valori `W`, evitando che `PV1 500 W` venga interpretato come tensione PV.
- Bump versione addon/backend a `0.3.309`.

## 0.3.308
- Energy Dashboard: corretto il drill-down dei valori W usando solo la posizione del click sul dispositivo, evitando aperture di grafici errati dovute al testo aggregato della card.
- Energy Dashboard: mantenuto il riconoscimento testuale solo per metriche non-W come SOC `%` e tensioni `V`.
- Bump versione addon/backend a `0.3.308`.

## 0.3.307
- Energy Dashboard: aggiunto drill-down sul click della card istantanea con grafico giornaliero del singolo dispositivo.
- Energy Dashboard: supportati grafici separati per potenza W di PV, rete, casa/load e batteria, piu SOC batteria `%` e tensioni `V`.
- Backend: aggiunto endpoint `/api/energy/metric-history` basato sullo storico Home Assistant del singolo sensore.
- Bump versione addon/backend a `0.3.307`.

## 0.3.306
- Energy Time: gestito lo storico parziale evitando che righe senza timestamp riempiano artificialmente i primi giorni o mesi.
- Energy Time: le finestre mensili HA marcano esplicitamente il bucket richiesto per mantenere Apr/Mag/Giu nei mesi corretti.
- Bump versione addon/backend a `0.3.306`.

## 0.3.305
- Energy Time: per la vista Anno usa aggregati mensili HA interrogati per singola finestra mensile, evitando calcoli giornalieri.
- Energy Time: mantenuto l'allineamento dei bucket tramite timestamp reale delle statistiche.
- Bump versione addon/backend a `0.3.305`.

## 0.3.304
- Energy Time: corretto l'allineamento dei bucket annuali usando il timestamp reale delle statistiche HA.
- Energy Time: aggiunto controllo locale per verificare mesi non contigui nelle statistiche storiche.
- Bump versione addon/backend a `0.3.304`.

## 0.3.303
- Energy Time: aumentata l'altezza del grafico barre storico e aggiunta linea zero centrale.
- Energy Time: import/produzione/casa restano positivi, export e batteria sono mostrati come valori negativi.
- Energy Time: tooltip hover sulle barre con dettaglio dei valori per fascia.
- Bump versione addon/backend a `0.3.303`.

## 0.3.302
- Energy Time: corretti i simboli corrotti nella vista storico K Flow (frecce, icone solare/rete/casa/batteria e menu periodo).
- Energy Wrapper: riallineato il marker/cache-buster `energyMindWrapperVersion` alla versione addon.
- Bump versione addon/backend a `0.3.302`.

## 0.3.301
- Energy Time: aggiunta serie opzionale `Solare termico`, visibile nel grafico storico solo se popolata.
- Admin Energy: aggiunto campo `Solare termico statistic_id` per configurare le statistiche storiche dedicate.
- Bump versione addon/backend a `0.3.301`.

## 0.3.300
- Energy Time: grafico a barre separato in serie nette con legenda colore per solare, import, export, batteria, casa e gas.
- Energy Time: barre storiche ora mostrano segmenti distinti per intervallo invece di una sola barra aggregata.
- Bump versione addon/backend a `0.3.300`.

## 0.3.299
- Energy Dashboard Sunsynk: nascosta l'icona meteo residua lungo il tragitto del sole tramite filtro runtime sullo shadow DOM della card.
- Bump versione addon/backend a `0.3.299`.

## 0.3.298
- Energy Dashboard K Flow: rimosso definitivamente il vecchio logo lungo il tragitto del sole direttamente dal componente SVG.
- Bump versione addon/backend a `0.3.298`.

## 0.3.297
- Stabilizzato `GET /api/weather/irrigation` per e-Dry con tutti i campi root sempre presenti e valori mancanti restituiti come `null`.
- `source` per irrigazione ora distingue in modo semplice `local_station` e `fallback_web`; `age_seconds` e `available` restano sempre nel payload.
- Open-Meteo per irrigazione esteso con probabilita pioggia, ET0, temperatura/umidita suolo e forecast orario/giornaliero piu coerente.
- README aggiornato con contratto dell'endpoint irrigazione.
- Bump versione addon/backend a `0.3.297`.

## 0.3.296
- Energy Dashboard K Flow: raddoppiata la dimensione responsive del logo EKONEX in testata.
- Bump versione addon/backend a `0.3.296`.

## 0.3.295
- Energy Dashboard K Flow: rimosso il logo interno sopra l'arco sole.
- Energy Dashboard K Flow: logo/titolo mostrato sopra la card come testata esterna.
- Bump versione addon/backend a `0.3.295`.

## 0.3.294
- Energy Time: rimossa la nota sotto il grafico barre e aggiunte le etichette giorno/mese sotto ogni barra.
- Bump versione addon/backend a `0.3.294`.

## 0.3.293
- Admin Energy: aggiunti campi `Energy Time - statistic_id storici` per configurare manualmente PV, casa, rete, batteria e gas per ogni sito.
- Energy Time: i campi manuali hanno priorita sulle deduzioni da HA Energy/site name, cosi i dati storici non dipendono da match automatici.
- Bump versione addon/backend a `0.3.293`.

## 0.3.292
- Energy Time: per `?site=...` filtra le sorgenti HA Energy globali per nome/id del sito, evitando di usare i soli sensori daily quando esistono statistiche HA dedicate.
- Energy Time: conversione automatica Wh/kWh/MWh verso kWh sui `change` recorder, cosi sensori batteria in MWh non risultano 1000x piu piccoli.
- Bump versione addon/backend a `0.3.292`.

## 0.3.291
- Energy Time: i `change` statistici HA vengono trattati come magnitudine, cosi carica batteria/export con segno negativo non finiscono a `0 kWh`.
- Bump versione addon/backend a `0.3.291`.

## 0.3.290
- Energy Time: separata la vista per sito; con `?site=...` usa solo i sensori energia configurati per quel sito e non la dashboard Energy globale di Home Assistant.
- Energy Time: la sorgente globale HA resta usata solo quando non viene richiesto un sito specifico.
- Bump versione addon/backend a `0.3.290`.

## 0.3.289
- Energy Time: corretta sorgente dati per Giorno/Mese/Anno usando `energy/get_prefs` e `recorder/statistics_during_period` di Home Assistant.
- Energy Time: i totali ora usano le statistiche HA `change` dei sensori configurati nella dashboard Energy, invece dei soli contatori daily della card.
- Build: aggiunta dipendenza `websockets` per accedere alla WebSocket API interna di Home Assistant.
- Bump versione addon/backend a `0.3.289`.

## 0.3.288
- Energy Time: aggiunta vista storica kWh stile K Flow con selezione Giorno/Mese/Anno, pulsante `Adesso` e frecce periodo.
- Energy Time: nuovo endpoint `/api/energy/history` che legge la history di Home Assistant per i sensori energia configurati.
- Bump versione addon/backend a `0.3.288`.

## 0.3.287
- Energy Dashboard K Flow: logo alto default servito da asset interno `vendor/k-flow-card/logo.png`.
- Energy Dashboard K Flow: logo riposizionato più in alto, separato dalla linea del sole.
- Energy Dashboard K Flow: badge PV alzato meno aggressivamente verso il bordo alto, per evitare sovrapposizione col logo.
- Bump versione addon/backend a `0.3.287`.

## 0.3.286
- Energy Dashboard K Flow: logo alto default impostato su asset addon esistente `/energy-dashboard/logo.png`.
- Bump versione addon/backend a `0.3.286`.

## 0.3.285
- Energy Dashboard K Flow: righe PV (`PV1..PV4`) escluse dallo scaling globale per evitare testi ammassati/sovrapposti.
- Energy Dashboard K Flow: logo alto default impostato su `logo only translucent.png` (asset interno addon).
- Bump versione addon/backend a `0.3.285`.

## 0.3.284
- Energy Setup K Flow: aggiunto campo `Logo alto (URL o /local/...)` per mostrare un logo personalizzato in testata card.
- Energy Dashboard K Flow: area logo dedicata in alto e badge PV riposizionato con margine superiore per evitare sovrapposizioni.
- Bump versione addon/backend a `0.3.284`.

## 0.3.283
- Energy Dashboard K Flow: fix clipping testo `PV3/PV4` (riposizionamento verticale nel canvas).
- Bump versione addon/backend a `0.3.283`.

## 0.3.282
- Energy Setup/Wizard: rimossa inferenza automatica PV da entita mappate (`pv2/pv3/...`).
- I campi PV lasciati vuoti in UI restano vuoti, senza ripopolamento automatico.
- Bump versione addon/backend a `0.3.282`.

## 0.3.281
- Energy Dashboard K Flow: migliorato layout blocco PV (righe distanziate e riposizionate) per evitare sovrapposizioni.
- Energy Dashboard K Flow: badge produzione istantanea sopra il sole abbassato e allargato per non risultare schiacciato/tagliato.
- Energy Setup K Flow: aggiunto campo `Min SOC manuale (%)`.
- Energy Dashboard K Flow: priorita soglia SOC minima = entity > manuale > valore base battery.
- Bump versione addon/backend a `0.3.281`.

## 0.3.280
- Energy Dashboard K Flow: aumentata la spaziatura delle righe PV a sinistra per evitare sovrapposizioni.
- Energy Dashboard K Flow: abbassata la label produzione istantanea sopra il sole per evitare taglio superiore.
- Energy Dashboard K Flow: `Remaining` reso alla stessa dimensione dei valori principali.
- Bump versione addon/backend a `0.3.280`.

## 0.3.279
- Energy Dashboard K Flow: fix definitivo scaling font globale `1.7x` (forzato anche su `font-size` SVG).
- Energy Dashboard K Flow: rimosso override runtime che riportava piccolo il testo secondario `Remaining`.
- Bump versione addon/backend a `0.3.279`.

## 0.3.278
- Energy Dashboard K Flow: applicato scaling font globale `1.7x` a tutti i testi principali (SVG + riquadri HTML) con override esplicito dei valori critici.
- Bump versione addon/backend a `0.3.278`.

## 0.3.277
- Energy Dashboard K Flow: aumento globale font `1.7x` su tutta la card (testi SVG + riquadri HTML) per migliorare la leggibilita.
- Bump versione addon/backend a `0.3.277`.

## 0.3.276
- Energy Setup K Flow: aggiunto campo `Min SOC entity (%)` per pilotare la soglia minima batteria da sensore.
- Energy Dashboard K Flow: `Remaining` mostra la soglia attiva come `MIN SOC xx%` e usa il sensore quando configurato.
- Bump versione addon/backend a `0.3.276`.

## 0.3.275
- Energy Setup K Flow: aggiunti `Riquadro basso destra label/entity` per personalizzare `SCARICA OGGI` come Min/Max cell.
- Energy Dashboard K Flow: uniformata la dimensione testo `CARICA` e `SCARICA` nella card `CHG / DIS`.
- Bump versione addon/backend a `0.3.275`.

## 0.3.274
- Energy Setup: estesi gli AUX a 8 totali per dashboard (`AUX principale` + `AUX load 1-7`).
- Energy Dashboard K Flow: visualizza fino a 8 righe AUX configurate.
- Bump versione addon/backend a `0.3.274`.

## 0.3.273
- UI Admin: rimossi i due pulsanti separati `Energy Flow` e `Energy` dalla topbar.
- UI Admin: aggiunta pagina interna unica `Energy` con accesso alle dashboard Energy Flow dei siti configurati.
- Bump versione addon/backend a `0.3.273`.

## 0.3.272
- Energy Dashboard K Flow: migliorata leggibilita della percentuale batteria con testo bianco e contorno scuro anche a SOC basso.
- Bump versione addon/backend a `0.3.272`.

## 0.3.271
- Energy Dashboard K Flow: aggiunte 8 nuove varianti icona casa generate dai riferimenti forniti.
- Energy Setup K Flow: le nuove varianti sono selezionabili dal menu `Icona casa`.
- Bump versione addon/backend a `0.3.271`.

## 0.3.270
- Energy Dashboard K Flow: aggiunta icona casa `Villa moderna` con sfondo trasparente.
- Energy Setup K Flow: aggiunta la scelta `Villa moderna` nel menu `Icona casa`.
- Bump versione addon/backend a `0.3.270`.

## 0.3.269
- Energy Setup K Flow: `Icona casa` ora e una scelta tra default K Flow, smart-glass e smart-glass 2 piani.
- Energy Dashboard K Flow: ripristinata l'icona casa default originale come default base, mantenendo entrambe le varianti smart-glass selezionabili.
- Bump versione addon/backend a `0.3.269`.

## 0.3.268
- Energy Dashboard K Flow: sostituita l'icona casa smart-glass con una versione compatta a due piani stile alloggio.
- Bump versione addon/backend a `0.3.268`.

## 0.3.267
- Energy Dashboard K Flow: aggiunta icona casa smart-glass con sfondo trasparente e impostata come default.
- Bump versione addon/backend a `0.3.267`.

## 0.3.266
- Energy Dashboard K Flow: l'animazione rete parte anche esattamente a `10 W` in ingresso/uscita, non solo sopra i `10 W`.
- Bump versione addon/backend a `0.3.266`.

## 0.3.265
- Energy Dashboard K Flow: invertita la freccia verticale della potenza rete sotto il traliccio per allinearla alla direzione visiva del flusso.
- Bump versione addon/backend a `0.3.265`.

## 0.3.264
- Energy Dashboard K Flow: AUX supporta fino a tre righe separate (`aux_power_166`, `aux_load1`, `aux_load2`) invece di un solo valore.
- Energy Setup K Flow: aggiunti override separati per `AUX 1` e `AUX 2`.
- Bump versione addon/backend a `0.3.264`.

## 0.3.263
- Energy Dashboard K Flow: aggiunta visualizzazione AUX opzionale vicino alla casa con nome e potenza.
- Energy Setup K Flow: aggiunti campi `AUX nome`, `AUX potenza` e `Icona casa`.
- Energy Dashboard K Flow: l'icona casa puo essere sovrascritta con un file locale o URL custom.
- Bump versione addon/backend a `0.3.263`.

## 0.3.262
- Energy Dashboard K Flow: gli Ampere batteria visualizzati sono calcolati da potenza/tensione quando disponibili, evitando valori uguali o stale dal sensore corrente.
- Bump versione addon/backend a `0.3.262`.

## 0.3.261
- Energy Dashboard K Flow: import/export rete usano frecce orizzontali (`←` import, `→` export) e la potenza sotto il traliccio usa frecce verticali (`↓` entra, `↑` esce).
- Bump versione addon/backend a `0.3.261`.

## 0.3.260
- Energy Dashboard K Flow: nascosti PV2/PV3/PV4 quando la relativa entita `pvX_power` non e configurata, evitando righe a `0 W` su impianti con un solo PV.
- Bump versione addon/backend a `0.3.260`.

## 0.3.259
- Energy Dashboard K Flow: rimosso il nome sito sovrapposto all'arco sole; il nome resta solo nel riquadro inverter centrale.
- Energy Dashboard K Flow: spostata e ridimensionata l'icona casa per evitare il taglio nella parte bassa della card.
- Bump versione addon/backend a `0.3.259`.

## 0.3.258
- Energy Dashboard K Flow: rinominato il riquadro `BATT DIS.` in `SCARICA OGGI` per chiarire che legge la scarica giornaliera, non il valore istantaneo/residuo della batteria.
- Bump versione addon/backend a `0.3.258`.

## 0.3.257
- Energy Dashboard K Flow: il riquadro inverter centrale mostra tensione e frequenza al posto della temperatura.
- Energy Dashboard K Flow: la percentuale centrale ora e etichettata come `CARICO`, cioe carico casa rispetto alla potenza massima inverter.
- Energy Setup K Flow: aggiunto campo `Label barra potenza`; il default standalone e `BATT` al posto di `PWR`.
- Bump versione addon/backend a `0.3.257`.

## 0.3.256
- Energy Setup Batterie: default `Soglia scarica batterie` portato al 10% e reso esplicito in UI.
- Energy Dashboard K Flow: `ENDURANCE` e `Remaining` calcolano l'energia utilizzabile fino alla soglia scarica configurata.
- Energy Dashboard K Flow: il riquadro `Chg / Dis` ora mostra `CARICA:` e `SCARICA:` davanti ai valori.
- Bump versione addon/backend a `0.3.256`.

## 0.3.255
- Energy Setup Solar: i blocchi PV1-PV6 ora sono mostrati in base al valore `Numero stringhe solari (MPPT)`, cosi un impianto con 1 PV mostra solo PV1.
- Generazione JSON Energy: quando `MPPT` e inferiore, le vecchie entita PV2-PV6 e i relativi nomi/potenze vengono rimossi dal JSON salvato invece di tornare alla riapertura.
- Energy Setup: le entita cancellate dal JSON non vengono piu ripopolate dal vecchio stato della UI.
- Bump versione addon/backend a `0.3.255`.

## 0.3.254
- Energy Dashboard K Flow: il backend ora legge anche le entita inserite nel JSON/config K Flow, cosi temperature e riquadri custom ricevono valori reali invece di restare a zero.
- Bump versione addon/backend a `0.3.254`.

## 0.3.253
- Energy Setup K Flow: rinominato `Total PV generation` in `PV totale storico`, per distinguerlo dai valori giornalieri gia presenti.
- Energy Setup K Flow: resi personalizzabili i due riquadri bassi sinistra/centro con label + entity, cosi possono mostrare sensori diversi da min/max cell voltage.
- Bump versione addon/backend a `0.3.253`.

## 0.3.252
- Energy Setup: aggiunta scheda dedicata `K Flow` in Configurazione completa per mostrare chiaramente entita mancanti e flag inversione rete/batteria.
- Bump versione addon/backend a `0.3.252`.

## 0.3.251
- Energy Setup: aggiunti campi UI K Flow per entita opzionali mancanti e flag `Inverti verso batteria` / `Inverti verso rete`, sincronizzati nel JSON override K Flow.
- Bump versione addon/backend a `0.3.251`.

## 0.3.250
- Energy Dashboard K Flow: l'arco sole usa `sun_times` e `sun_position` reali di e-SunMind da `/api/data`, non piu solo il mock `sun.sun`.
- Bump versione addon/backend a `0.3.250`.

## 0.3.249
- Energy Dashboard K Flow: corretta la capacita batteria automatica in kWh, cosi `Remaining` non resta `-- Ah`.
- Energy Dashboard K Flow: aggiunti mapping opzionali da Sunsynk per temperature batteria/inverter, seconda batteria, discharge e total PV generation quando presenti nel JSON.
- Bump versione addon/backend a `0.3.249`.

## 0.3.248
- Energy Dashboard K Flow: aggiunto cache-buster al modulo `k-flow-card.js` per evitare che il browser riusi la versione con path icone HACS `/local/community/k-flow-card`.
- Bump versione addon/backend a `0.3.248`.

## 0.3.247
- Energy Dashboard K Flow: evitato il reset visuale a ogni polling API; `setConfig()` ora viene richiamato solo se cambia davvero la configurazione.
- Energy Dashboard K Flow: vendorizzate anche le icone PNG e corretto il path asset per standalone addon.
- Bump versione addon/backend a `0.3.247`.

## 0.3.246
- Energy Dashboard K Flow: la config automatica usa direttamente gli entity_id reali della vecchia configurazione Sunsynk, evitando valori a zero nei mirror `sensor.mock_*`.
- Bump versione addon/backend a `0.3.246`.

## 0.3.245
- Energy Dashboard: aggiunta scelta layout per-site tra Sunsynk Power Flow e `k-flow-card`.
- Energy Dashboard: vendorizzata `k-flow-card` e generata automaticamente la config dai campi energy/Sunsynk, con override JSON dedicato.
- Energy Sankey: aggiunti 16 carichi extra per ogni site, configurabili da UI con nome, entity_id e colore, usati solo dal grafico Sankey.
- Energy Sankey: gli extra load vengono letti dal wrapper come sensori di potenza aggiuntivi senza modificare la card Sunsynk.
- Bump versione addon/backend a `0.3.245`.

## 0.3.244
- Energy Sankey: aggiunti 16 carichi extra per ogni site, configurabili da UI con nome, entity_id e colore, usati solo dal grafico Sankey.
- Energy Sankey: gli extra load vengono letti dal wrapper come sensori di potenza aggiuntivi senza modificare la card Sunsynk.
- Bump versione addon/backend a `0.3.244`.

## 0.3.243
- Energy Sankey: il totale `Carico casa` non viene piu gonfiato dai figli load duplicati; i figli vengono scalati quando superano il totale reale.
- Energy Setup: aggiunto flag per-site `Mostra Sankey Card` per abilitare/disabilitare il Sankey su ogni dashboard.
- Bump versione addon/backend a `0.3.243`.

## 0.3.242
- Energy Sankey: corretta la lettura import/export rete rispettando `grid.invert_grid`, cosi il grid positivo configurato come import alimenta il ramo `Import rete` invece di sparire.
- Energy Sankey: abbassata la soglia minima e riallocati i flussi live in ordine FV, rete, batteria verso casa, con eccedenza FV verso batteria/export.
- Bump versione addon/backend a `0.3.242`.

## 0.3.241
- Energy Sankey: sostituito il nodo speciale `remaining_parent_state` con un sensore esplicito `Altri carichi`, cosi il grafico standalone mostra correttamente i rami sotto `Carico casa`.
- Bump versione addon/backend a `0.3.241`.

## 0.3.240
- Energy Dashboard: aggiunto sotto la Sunsynk card il grafico live `ha-sankey-chart` v5.0.1, caricato localmente da `energy-dashboard/vendor`.
- Sankey: il grafico e separato per `site`, usa gli stessi sensori mock del wrapper e include PV, rete, batteria, casa, export/carica batteria e tutti i carichi `load`, `AUX` e `non-essential` mappati.
- Bump versione addon/backend a `0.3.240`.

## 0.3.239
- Energy Dashboard: vendorizzata e caricata localmente la Sunsynk Power Flow Card `v6.9.2`, allineata alla versione installata in Home Assistant.
- Energy Dashboard: i CDN restano solo come fallback dopo la copia locale.
- Bump versione addon/backend a `0.3.239`.

## 0.3.238
- Energy Dashboard standalone: aggiunto fallback `ha-icon` con path SVG MDI nativi per rete/import/export/off e icone load comuni.
- Energy Dashboard: ripristinata la visibilita delle icone rete quando la card Sunsynk usa `import_icon`, `export_icon` o `disconnected_icon`.
- Bump versione addon/backend a `0.3.238`.

## 0.3.237
- Energy Dashboard: rimosso lo shim custom delle torri rete, cosi le icone passano dalla stessa famiglia MDI usata dalla card Sunsynk.
- Energy Setup: aggiunti controlli espliciti per dynamic icon/colour, colori/off colour, AUX type/load/icon e nomi load non-essential.
- Energy Setup: limitato il conteggio batterie UI a 2, coerente con la card Sunsynk.
- Energy Dashboard: ridotto lo spam console quando l'API addon non risponde.
- Bump versione addon/backend a `0.3.237`.

## 0.3.236
- Energy Setup: riordinate le sezioni Solar, Battery, Load, AUX, Grid e Giornalieri in sottoblocchi leggibili.
- Energy Setup: ogni PV ora espone Nome, P nominale, entita potenza, entita tensione ed entita corrente.
- Energy Setup: batterie 1/2/3 con Nome, potenza, tensione, corrente e SOC; i contatori kWh giornalieri sono solo nella sezione Giornalieri.
- Energy Dashboard: il colore sfondo configurato viene applicato anche a pagina/body/frame e variabili HA mock.
- Bump versione addon/backend a `0.3.236`.

## 0.3.235
- Energy Dashboard: aumentati i riquadri responsive dei loghi EnergyMind/EKONEX per occupare lo spazio indicato nel layout.
- Energy Dashboard: aggiunta etichetta overlay con nome site/dashboard corrente, letta da `site_name`/`name`/`id`.
- Bump versione addon/backend a `0.3.235`.

## 0.3.234
- Energy multi-site: ogni dashboard usa solo le entita del proprio sito; rimosso il fallback che poteva far ereditare a `privato` i sensori del sito selezionato/top-level.
- Energy Wrapper: la config Sunsynk viene ricreata da base pulita a ogni reload opzioni, evitando residui di entita/config tra dashboard diverse.
- Energy Wrapper: reset degli stati mock interni prima di applicare i dati live del sito, cosi valori mancanti non restano appesi dal sito precedente.
- Energy icone: ripristinato `load.dynamic_icon=true` come default Sunsynk per usare le icone dinamiche originali della card.
- Test: aggiunto controllo `tools/check_energy_site_isolation.py` per bloccare regressioni su `?site=privato`/`?site=sas`.
- Bump versione addon/backend a `0.3.234`.

## 0.3.233
- Energy Wrapper/Setup: la Home non forza piu `load.dynamic_icon=true`, cosi la Sunsynk card usa l'icona load originale invece della casa con freccia dinamica.
- Energy Wrapper: le icone Grid import/export/disconnected vengono mantenute come configurate (`mdi:transmission-tower-*`) senza riscrittura verso varianti generiche.
- Bump versione addon/backend a `0.3.233`.

## 0.3.232
- Energy Wrapper: con URL `?site=...`, `/api/data?site=...` viene usato direttamente come snapshot principale invece di riselezionare dentro `energy.sites`; risolve PV/load a zero solo nelle dashboard dedicate.
- Bump versione addon/backend a `0.3.232`.

## 0.3.231
- Energy Wrapper: il lookup dei valori mirror ora cerca anche in `energy.entities` top-level, non solo in `card_entities`; risolve PV singoli a zero quando l'entita reale e letta come `pv_power_entity_id`/campo rapido.
- Bump versione addon/backend a `0.3.231`.

## 0.3.230
- Energy Wrapper: se sono configurate entita daily PV/batteria/load/grid, il wrapper forza automaticamente i relativi `show_daily`, cosi i kWh giornalieri non restano nascosti.
- Bump versione addon/backend a `0.3.230`.

## 0.3.229
- Energy Wrapper: lookup dei valori runtime reso tollerante anche quando `card_entities` arriva indicizzato per entity_id reale invece che per chiave Sunsynk.
- Energy Wrapper: PV singoli e daily ora vengono copiati nei mock cercando prima per chiave (`pv1_power_186`) e poi per entity_id sorgente reale salvato prima del mirror.
- Bump versione addon/backend a `0.3.229`.

## 0.3.228
- Energy Wrapper: `setConfig()` ora riceve sempre una copia runtime gia normalizzata e mirrorata, impedendo alla card di ricevere entita reali al posto di `sensor.mock_*`.
- Energy Wrapper: aggiunto marker `window.energyMindWrapperVersion` per verificare in console la versione del wrapper caricata dal browser/addon.
- Bump versione addon/backend a `0.3.228`.

## 0.3.227
- Energy Wrapper: la card Sunsynk ora usa entita interne mirror controllate dal wrapper, mentre il backend continua a leggere le entita reali configurate.
- Energy Wrapper: separato definitivamente `pv_total` dai PV1-PV6, evitando che il totale azzeri o sporchi i valori dei singoli PV.
- Energy Wrapper: i daily PV/batteria/load/grid vengono pubblicati sugli stessi ID interni usati dalla card, cosi non restano a zero dopo `setConfig`.
- Bump versione addon/backend a `0.3.227`.

## 0.3.226
- Energy Wrapper: PV3-PV6 vengono aggiornati esplicitamente dal backend come PV1/PV2, evitando valori a zero quando e configurato `pv_total`.
- Energy Wrapper: tensione/corrente PV sono trattate come opzionali e vengono rimosse dalla config se non mappate, senza bloccare la potenza del PV.
- Energy Wrapper/API: aggiunti fallback daily interni per PV/load/grid/batteria e normalizzati `battery_charge_today_kwh`/`battery_discharge_today_kwh`.
- Bump versione addon/backend a `0.3.226`.

## 0.3.225
- Energy Wrapper: ripristinati i default originali della Sunsynk card per colori dinamici (`load.dynamic_colour`, `load.dynamic_icon`, `aux_dynamic_colour`, `solar.dynamic_colour`, battery gradient).
- Energy Setup: il JSON generato ora include i flag dinamici principali, cosi il nodo casa torna a comportarsi come nella card HASS originale.
- Bump versione addon/backend a `0.3.225`.

## 0.3.224
- Energy Wrapper: corretta taratura flussi PV per usare anche `pv_total` e PV1-PV6 nei segni/inversioni, non solo PV1.
- Energy Wrapper: il rilevamento presenza PV ora considera `pv_total` e PV1-PV6, evitando spegnimenti errati della sezione Solar.
- Energy Wrapper: corretti lookup site-specific per tensione inverter/frequenza e impedita scrittura di stati HA browser con entity id vuoto.
- Bump versione addon/backend a `0.3.224`.

## 0.3.223
- Energy Setup: aggiunto campo UI `PV totale live (entity_id)` per pilotare direttamente il riquadro totale PV della dashboard.
- Energy API/Wrapper: `pv_total` ha priorita sul totale PV; se manca, resta il fallback alla somma PV1-PV6.
- Bump versione addon/backend a `0.3.223`.

## 0.3.222
- Energy Dashboard: `?site=...` ora risolve sia l'ID link sia il nome dashboard normalizzato, evitando fallback errati quando il nome e l'ID non coincidono.
- Bump versione addon/backend a `0.3.222`.

## 0.3.221
- Performance: la dashboard Energy standalone usa `/api/data?site=...`, evitando di ricostruire tutti gli impianti e snapshot meteo/tende a ogni polling.
- Performance UI: `loadData()` non ricarica piu `/api/options` a ogni refresh realtime e non esegue piu autofill stazione meteo durante il polling.
- Bump versione addon/backend a `0.3.221`.

## 0.3.220
- Energy Setup: aggiunta select esplicita per scegliere l'impianto attivo oltre ai tab.
- Energy Setup: quando si cambia impianto il wizard corrente viene serializzato nel JSON del site prima dello switch, evitando perdita dei campi tecnici non ancora salvati.
- Bump versione addon/backend a `0.3.220`.

## 0.3.219
- Energy Setup: aggiunti campi UI per nominale PV1-PV6 (`pv*_max_power`) usati dalla card per calcolare la percentuale stringa.
- Bump versione addon/backend a `0.3.219`.

## 0.3.218
- Energy Setup: aggiunti campi UI per nome visuale PV1-PV6.
- Energy Setup: aggiunti campi UI Batteria per tensione, corrente, carica giornaliera e scarica giornaliera.
- Bump versione addon/backend a `0.3.218`.

## 0.3.217
- Energy Setup: aggiunta gestione multi-impianto con dashboard separate per site (`?site=...`).
- Energy API/Wrapper: `/api/data` espone `energy.sites[]` e la dashboard standalone seleziona sensori/configurazione in base al site richiesto.
- Bump versione addon/backend a `0.3.217`.

## 0.3.216
- Energy Dashboard: aumentata la scala interna dei loghi originali dentro i riquadri responsive, senza modificare i PNG.
- Bump versione addon/backend a `0.3.216`.

## 0.3.215
- Energy Dashboard: corretto crop dei loghi originali per evitare tagli su simbolo EnergyMind e logo EKONEX.
- Energy Setup: aggiunto colore sfondo configurabile per la dashboard Energy.
- Bump versione addon/backend a `0.3.215`.

## 0.3.214
- Energy Dashboard: aumentate le dimensioni visuali dei loghi originali con crop CSS dello spazio trasparente, senza modificare i PNG.
- Adattate misure logo per layout full, compact, lite, minimal e mobile.
- Bump versione addon/backend a `0.3.214`.

## 0.3.213
- Energy Dashboard: aggiunti i PNG originali `energymind.png` in alto e `logo only translucent.png`/EKONEX in basso come overlay responsive.
- I loghi originali non vengono ridisegnati o filtrati; viene applicato solo dimensionamento/posizionamento CSS per layout full, compact, lite, minimal e mobile.
- Bump versione addon/backend a `0.3.213`.

## 0.3.212
- Energy Dashboard: aggiunto logo `EnergyMind` nell'area alta libera della card Sunsynk.
- Il logo e dedicato alla dashboard Energy e non modifica la UI principale.
- Bump versione addon/backend a `0.3.212`.

## 0.3.211
- Energy Dashboard: aggiunta favicon dedicata rosso/blu per `energy-dashboard/sunsynk-wrapper.html`.
- La favicon della UI principale e-SunMind resta invariata.
- Bump versione addon/backend a `0.3.211`.

## 0.3.210
- Energy Flow: rimosso script CDN statico su `@master` e aggiunto loader con fallback.
- Sunsynk Power Flow Card caricata prima da versione pinata `v7.3.3`, poi da `master` se il CDN fallisce.
- Bump versione addon/backend a `0.3.210`.

## 0.3.209
- Energy Setup: in layout `full` con AUX attivo, il generatore JSON rimuove `essential_load3..6` invece di farli tornare al salvataggio.
- Energy Flow: in layout `full + AUX`, il wrapper mantiene AUX visibile e limita i load essenziali a 2, evitando che la card Sunsynk nasconda AUX.
- Bump versione addon/backend a `0.3.209`.

## 0.3.208
- Energy Setup piu leggibile: pagina limitata in larghezza, avvio rapido guidato e configurazione completa divisa in sezioni cliccabili.
- Energy Setup: applicati gli stili dedicati anche alla pagina principale, evitando griglie enormi e campi illeggibili su monitor larghi.
- Energy Flow: valori HA passati raw alla card Sunsynk e flag `invert_*` impostati dai segni configurati, cosi i pallini seguono la direzione della card.
- Bump versione addon/backend a `0.3.208`.

## 0.3.207
- Energy Flow wrapper piu tollerante: disattiva automaticamente tutte le opzioni daily/aux/grid opzionali quando mancano le entita richieste.
- `setConfig()` ora ritenta dopo sanitizzazione e non blocca il polling dati se la card Sunsynk rifiuta una configurazione parziale.
- Bump versione addon/backend a `0.3.207`.

## 0.3.206
- Fix Energy Flow: se `battery.show_daily` e attivo ma mancano `day_battery_charge_70` o `day_battery_discharge_71`, il wrapper disattiva automaticamente il daily batteria prima di `setConfig()`.
- Compatibilita Sunsynk Power Flow Card 6.9.2: evitato errore bloccante sulle entita daily charge/discharge batteria durante test o config parziali.
- Bump versione addon/backend a `0.3.206`.

## 0.3.205
- Fix Energy Flow test/mapping: il wrapper ora pubblica direttamente in `window.hass.states` gli stati HA reali letti da `energy.card_entities`, evitando che restino i seed a `0`.
- Aggiunto log `console.warn` quando il sync Energy fallisce, per non nascondere errori runtime del wrapper.
- Bump versione addon/backend a `0.3.205`.

## 0.3.204
- Fix Energy Flow: aggiunti fallback obbligatori `battery.shutdown_soc`, `battery.energy`, `battery.max_power` e valori equivalenti per `battery2` prima di chiamare `setConfig()` sulla card Sunsynk.
- Compatibilita Sunsynk Power Flow Card 6.9.2: evitato errore bloccante `Please include the battery shutdown_soc attribute`.
- Bump versione addon/backend a `0.3.204`.

## 0.3.203
- Energy Setup: aggiunto pannello `Configurazione rapida` con solo entita principali, tema, layout e azioni operative.
- Energy Setup: spostata la configurazione completa in sezione apribile per ridurre rumore visivo e separare topologia/load/grid/segni/JSON avanzato.
- Energy Setup: aggiunto warning leggibile per incompatibilita `full + AUX + 4+ load` della card Sunsynk.
- Bump versione addon/backend a `0.3.203`.

## 0.3.202
- Fix Energy Sunsynk: neutralizzati gli `invert_*` della card dopo la normalizzazione dei segni per evitare flussi animati in direzioni incoerenti.
- Fix carichi aggiuntivi: nel layout `full`, se sono mappati 4+ load essenziali, il wrapper disattiva automaticamente AUX per evitare che la card originale annulli `additional_loads`.
- Bump versione addon/backend a `0.3.202`.

## 0.3.198
- Fix segno flussi: la direzione animazioni ora segue i segni impostati in UI (sezione unica `Segno Entita (+/-)`).
- Wrapper ricarica i segni senza refresh manuale pagina e riapplica la config card al volo.
- Allineati anche i flag flow principali (`solar.invert_flow`, `battery.invert_power`, `load.invert_load`, `load.invert_aux`, `grid.invert_grid`) in base ai segni configurati.

## 0.3.197
- UI Energy: rimossi i selettori segno duplicati nei blocchi (`Solar`, `Load`, `Grid`, `Battery`).
- Segno ora centralizzato solo nella sezione unica `Segno Entita (+/-)` per evitare configurazione sparsa/confusa.

## 0.3.196
- Segno `+/-` ora configurabile in UI per tutte le principali entita di potenza (PV1..PV6, Home/Essential, Battery1/2, Grid/CT, AUX, Non-Essential, load dedicati).
- Aggiunta sezione UI `Segno Entita (+/-)` con dropdown per chiave; generazione automatica di `entity_signs_json` (non serve piu scriverlo a mano).
- Persistenza backend del nuovo campo `energy.entity_signs_json`.
- Fix mapping UI allineato chiavi Sunsynk reali: aggiunti campi e serializzazione per `essential_load3..6`, `aux_load1..2`, `non_essential_load1..3`, `pv6_*` e `pv5_*` standard.

## 0.3.195
- Fix profondo mappatura entita Sunsynk: aggiunte chiavi realtime mancanti per `essential_load3..6`, `aux_load1..2`, `non_essential_load1..3`, `pv5/pv6` (power/voltage/current).
- UI Energy aggiornata con i nuovi campi entita nei blocchi `Load`, `AUX`, `Grid`, `Solar` (PV6 incluso).
- Corretto naming chiavi PV non standard: rimossi mapping custom errati (`pv5_power_247`, `pv5_voltage_117`, `pv5_current_118`) e allineato alle chiavi card reali.
- Aggiunta configurazione segno per tutte le entita tramite `entity_signs_json` (override per chiave entita, `positive|negative`), applicata nel wrapper.
- Topology allineata alle capacita reali card per batterie (`count` max 2).

## 0.3.194
- Energy UI riorganizzata in blocchi chiari: `Generale/Topology`, `Inverter`, `Solar`, `Battery`, `Load`, `AUX`, `Grid`, `Entita Giornaliere`.
- Rinominati i campi principali con nomi piu leggibili (PV1/PV2, Casa/Home, Rete/Grid, Batteria 1/2, Essential/AUX).
- Wrapper Sunsynk allineato alla card originale: rimossa la manipolazione interna dei segni `+/-` (niente inversioni extra nel wrapper).

## 0.3.193
- Fix root-cause strict entities: rimossa inizializzazione cardConfig.entities con mock defaults nel wrapper.
- Ora entita vuota in UI resta davvero vuota lato card (niente slot considerati mappati per errore).

## 0.3.192
- Essential fix: se essential_power non e mappata ma essential_load1 e mappata, il riquadro Essential usa essential_load1 (sempre entita reale, nessuna stima).
- Confermato strict mode: nessun valore sintetico per entita non mappate.

## 0.3.191
- Wrapper strict hard-mode: rimosso fallback sensor.mock_* per entita non mappate (entityId restituisce vuoto).
- Canali non mappati ora vengono eliminati dalla config passata alla card (PV2+/battery2), non solo messi a stringa vuota.
- attery.count forzato a 1 se attery2_power_190 non e mappata.

## 0.3.190
- Grid tower icon: aumentata dimensione fissa a 64px e tratto SVG piu spesso per renderla chiaramente visibile.

## 0.3.189
- Wrapper strict mode: rimossi fallback impliciti da energy_config (niente auto-mapping entita).
- Rimossa stima PV split da totale (solar_power non viene piu diviso su PV2+).
- Rimossa auto-attivazione additional_loads basata su entita presenti.
- Risultato: solo entita mappate esplicitamente; il resto resta a zero/disattivato.

## 0.3.188
- Energy wrapper: disattivata stima canali PV non mappati. Ora vengono mostrati solo MPPT con entita reale configurata (niente valori sintetici su PV2/PV3/PV4/PV5).

## 0.3.187
- Grid tower icon: dimensione resa fissa in px (--grid-tower-size: 46px) per avere resa esatta e coerente.

## 0.3.186
- Energy UI: aggiunta mappatura diretta entita per PV2/PV3/PV4/PV5 e Battery2 power.
- Energy UI: aggiunto blocco Entita extra JSON (chiave->entity_id) per coprire tutte le entities supportate dalla card senza altri buchi UI.
- Caricamento config: import automatico in UI delle chiavi entita extra non standard.

## 0.3.185
- Energy: aggiunti campi UI per rinominare Essential, Auxiliary, Daily Load, Load 1 name, Load 2 name (salvati nel JSON della card).
- Wrapper: fallback entita per ramo load (essential_power <- home_power se vuoto) e auto dditional_loads quando ci sono essential_load1/2 mappati.
- Wrapper: icona Grid tower ingrandita e intercettata anche per varianti senza prefisso mdi:.

## 0.3.184
- Energy UI: aggiunto selettore icone per tutti i campi load/grid mantenendo input testo libero per valori mdi:... custom.

## 0.3.183
- Grid icon fix (size): forzata dimensione minima della tower icon nel wrapper standalone (ha-icon) per evitare rendering microscopico.

## 0.3.182
- Fix definitivo icona Grid: ha-icon standalone ora disegna SVG tower interno per mdi:transmission-tower*, quindi la torre rete e sempre visibile anche quando il font mdi non risolve in shadow DOM.

## 0.3.181
- Fix icona Grid nel wrapper Sunsynk: rimosso fallback che la nascondeva, normalizzazione verso icone tower visibili (mdi:transmission-tower, mdi:transmission-tower-off-outline).

## 0.3.180
- Rimossa completamente la UI Wizard Energy (e popup collegati): ora la configurazione e diretta e lineare.
- Nuova pagina Energy a blocchi grandi e leggibili (Generale, Solar/Battery, Load/Grid, Icone, Entita Potenza, Entita Giornaliere, JSON).
- Aggiunti in UI diretta tutti i campi principali mancanti del wizard: topologia (MPPT/batterie/carichi/AUX), colori, icone load/grid/import/export/disconnected.
- Migliorata leggibilita: card piu grandi, griglia 2 colonne desktop, input/font piu grandi, mobile 1 colonna.

## 0.3.179

- Fix persistenza entita Energy da UI: durante `Salva` i campi `energyForm` (entita potenza/giornaliere) vengono prima sincronizzati nel wizard, poi serializzati nel JSON card.
- Risolto il caso in cui le entita inserite manualmente sparivano dopo salvataggio per sovrascrittura con stato wizard non aggiornato.

## 0.3.178

- Versione UI allineata: aggiornato `APP_VERSION` backend, ora `api/status` e badge in topbar mostrano release reale.
- Wrapper Sunsynk standalone: aggiunto shim `ha-icon` per compatibilita icone MDI in assenza del runtime Home Assistant completo.
- Energy Setup: layout ulteriormente semplificato a 2 colonne stabili per ridurre l'effetto “insalata”.

## 0.3.177

- Energy Setup restyle strutturale: layout a blocchi con griglia fissa (non più riga infinita “insalata”).
- Nuove breakpoints responsive per mantenere leggibilità su desktop/laptop/tablet.
- Sezione campi entità più ordinata con distribuzione 4/3/2/1 colonne in base alla larghezza.

## 0.3.176

- UI Energy migliorata: campi mappatura entita allargati e font monospace per visualizzare interamente gli `entity_id` senza troncamenti ambigui.
- Include i fix della 0.3.175 (persistenza wizard su save + fallback icona grid tower in standalone).

## 0.3.175

- Persistenza UI Energy corretta: `Salva configurazione Energy` e `Salva tutto` applicano automaticamente il wizard prima del payload, evitando ritorni ai valori precedenti.
- Wrapper standalone: fallback robusto icone torre rete (`mdi:transmission-tower-*`) a `default` per garantire icona Grid visibile.

## 0.3.174

- Wizard icone Energy esteso: aggiunti preset aggiuntivi e campi testo custom per tutte le icone Load/Non-Essential.
- Aggiunti controlli UI per `grid_nonessential_icon`, `grid_import_icon`, `grid_export_icon`, `grid_disconnected_icon`.
- Wrapper: rimosso filtro whitelist rigido sulle icone, ora passa i valori icona configurati da UI/JSON senza forzare `default`.

## 0.3.173

- Fix icona Grid mancante in wrapper standalone: fallback automatico a `default` per `grid.import_icon`, `grid.export_icon`, `grid.disconnected_icon` quando impostati come `mdi:*`.
- In ambiente senza resolver completo Home Assistant, la torre grid torna sempre visibile.

## 0.3.172

- Fix definitivo race `config.entities` su Sunsynk wrapper: la card non e piu nel DOM statico all'avvio.
- Bootstrap nuovo: creazione dinamica `<sunsynk-power-flow-card>` via JS, `setConfig()` prima del mount, poi `appendChild`.
- Evitato render iniziale con `config` undefined che causava `Cannot read properties of undefined (reading 'entities')`.

## 0.3.171

- Fix crash startup card Sunsynk 6.9.2: inizializzazione `window.customCards` forzata ad array prima del load script (fix errore `push`).
- Fix render race: rimosso set `hass` prima di `setConfig` nel wrapper per evitare `config/entities undefined` durante il primo ciclo render.

## 0.3.170

- Hotfix crash runtime Sunsynk (`Cannot read properties of undefined: push/entities`): introdotta normalizzazione hard della config prima di `setConfig`.
- Garantita presenza di tutte le sezioni oggetto richieste dalla card (`solar`, `battery`, `load`, `grid`, `inverter`, `entities`) e serializzazione stringa dei valori entita.
- Aggiunto fallback protetto su `setConfig`: se la config utente e invalida/parziale, viene applicata una config minima safe senza bloccare il rendering.

## 0.3.169

- Wrapper Sunsynk riallineato alla card originale: rimossi override aggressivi che alteravano topologia/entita rispetto al JSON.
- Fallback entita Energy ora non sovrascrive campi gia mappati nel JSON (`card.entities` ha priorita completa).
- Coerenza visibilita rami: `grid.show_nonessential` e `load.show_aux` rispettati con default sicuri (`false`) quando non impostati.
- Seed stati mock migliorato: entita configurate inizializzate in modo stabile (`binary_sensor` on, status `Normal`) per evitare stati grafici incoerenti/icone mancanti.

## 0.3.168

- Hotfix crash Sunsynk card (`entities undefined` / `push undefined`): normalizzazione hard della config nel wrapper prima di `setConfig`.
- Garantiti tipi validi per `entities`, `solar`, `battery`, `load`, `grid`, `inverter` e fallback coerenti per i campi base della card.

## 0.3.167

- Hotfix stabilita configurazione card: aggiornamento UI del `cardstyle` ora parte sempre da una base config completa e valida.
- Evitato JSON parziale che causava crash runtime della card (`Cannot read properties of undefined (reading 'entities'/'push')`).

## 0.3.166

- UI Energy `Entita Potenza` estesa con campi prima mancanti per parita con card originale:
  - `grid_ct_power_172`, `grid_connected_status_194`
  - `essential_power`, `nonessential_power`
  - `essential_load1`, `essential_load2`
  - `aux_power_166`
- I nuovi campi sono letti dal JSON esistente e scritti nel JSON generato dal wizard.

## 0.3.165

- UI Energy `Load & Grid` estesa con opzioni avanzate prima disponibili solo via JSON:
  - `show_daily_sell`, `invert_grid`, `show_absolute`, `show_nonessential`, `additional_loads`
  - `grid_name`, label daily buy/sell, `nonessential_name`, `invert_flow`, `energy_cost_decimals`
  - colori `export/off/no-grid`.
- Mapping bidirezionale completo: i nuovi campi vengono letti dal JSON esistente e salvati nel JSON generato dal wizard.

## 0.3.164

- UI Energy completata su `Load & Grid`: aggiunti controlli dedicati `Show non-essential` e `Grid additional loads`.
- I nuovi campi sono collegati al JSON card (`grid.show_nonessential`, `grid.additional_loads`) e persistono via wizard/salvataggio.

## 0.3.163

- Restyling pagina Energy: configurazione divisa in blocchi funzionali (`Generale`, `Solar & Battery`, `Load & Grid`, `Entita Potenza`, `Entita Giornaliere`, `JSON Avanzato`).
- Migliorata leggibilita e spacing della UI, eliminando l'effetto "griglia unica insalata".

## 0.3.162

- Wizard Energy: `Applica alla card` ora fa merge non distruttivo con il JSON esistente invece di sostituirlo.
- Le opzioni avanzate della card originale (es. `show_nonessential`, nomi custom, icone, label) non vengono più perse quando usi il wizard.

## 0.3.161

- Compatibilita config Sunsynk originale: nel wrapper energy i valori entita `none/null/unknown/unavailable` ora sono trattati come non configurati.
- Coerenza con card reale: i rami Solar/Battery/Grid non vengono considerati mappati quando nel JSON hai `none`.

## 0.3.160

- Regola strict mapping nel wrapper energy: se un'entita non e mappata, non vengono piu seedati valori fake e non vengono piu applicati fallback numerici a `0`.
- Rami Solar/Battery/Grid ora si disattivano automaticamente se le rispettive entita principali non sono configurate.
- Rimossi fallback forzati di stato grid (`on`) quando l'entita non e presente.

## 0.3.158

- Mappatura entita realtime semplificata: rimossi marker cliccabili sovrapposti alla card (fonte principale di disallineamento).
- Selezione ora solo da lista strutturata con evidenza forte della riga attiva.
- Aggiunta barra visiva "Stai mappando: ..." sopra la preview della card reale per capire sempre il campo corrente.

## 0.3.157

- Wrapper standalone: aggiunta sanitizzazione icone `load/grid` con fallback automatico a `default` per evitare icone mancanti/non renderizzate.

## 0.3.156

- Nuovo flusso mappatura entita (popup realtime): mantenuta card reale come preview, ma selezione entita spostata su lista strutturata con pulsante `Seleziona`.
- Quando selezioni un campo, viene evidenziato il punto corrispondente sul grafico (marker glow + riga attiva), evitando click diretti disallineati sulla card.

## 0.3.155

- Mapper dashboard (`map=1`): aggiunto auto-fit dinamico della card Sunsynk al viewport del frame.
- Rimosse scrollbar interne del frame in modalita mappa e stabilizzato l'allineamento hotspot con resize.

## 0.3.154

- Mapper entita su dashboard reale: sostituiti hotspot a pixel fissi con coordinate normalizzate (0..1) rispetto alla card.
- Aggiunte mappature dedicate anche per `day_grid_export_77` oltre a `day_grid_import_76`.
- Risultato: allineamento consistente dei pulsanti su diverse risoluzioni senza ritocchi manuali.

## 0.3.153

- Popup mappatura energy: aumentata altezza preview card per includere la parte bassa della dashboard.
- Wrapper `map=1`: rimosso crop verticale rigido (`100vh + overflow hidden`) che tagliava la sezione inferiore.

## 0.3.152

- Fix salvataggio JSON fuori wizard: rimosso override globale del `sunsynk_card_config_json` durante `Salva`.
- Il selettore `Cardstyle` ora aggiorna solo il campo `cardstyle` dentro il JSON corrente (`on change`), senza sovrascrivere le altre personalizzazioni manuali.

## 0.3.151

- Fix persistenza cardstyle wizard: durante `Salva` viene sempre rigenerato `sunsynk_card_config_json` dal wizard, evitando il ritorno a `full` quando era selezionato `compact/lite/minimal`.

## 0.3.150

- Popup mappatura entita energy: ripristinato scroll del modal/backdrop.
- Overlay hotspot ricalibrato con coordinate fisse su canvas mappa dedicato (ridotto il disallineamento percepito).

## 0.3.149

- Mapper popup energy: eliminato overflow interno nella modalita `map=1` del wrapper (niente doppie scrollbar nel frame), per ridurre disallineamento hotspot.

## 0.3.148

- Wrapper map mode: layout full-frame dedicato per la preview di mappatura entita nel wizard.

## 0.3.147

- Fix popup wizard energy: ripristinato scroll verticale nel modal di mappatura entita.
- Mapper card full reso responsive con altezza dinamica (`min(56vh, 520px)`) per evitare blocchi su schermi bassi.

## 0.3.146

- Energy Wizard mapping popup: riallineati hotspot su card Sunsynk Full con area a rapporto fisso e iframe non interattivo dietro overlay.
- Ridotti/semplificati i marker visivi per evitare sovrapposizioni e disallineamenti con icone/nodi.

## 0.3.145

- Wizard Energy: popup mappatura realtime ora mostra la card reale Sunsynk Full (iframe) con hotspot cliccabili sui nodi principali per assegnare direttamente le entita.

## 0.3.144

- Energy Wizard: aggiunto selettore `Cardstyle` (non più fisso su `full`) con opzioni `full`, `compact`, `lite`, `minimal`.
- Il valore scelto viene scritto nel JSON Sunsynk generato dal wizard e mostrato nello step di conferma.

## 0.3.143

- Wizard Energy: popup mappatura realtime aggiornato con preview visuale tipo dashboard (nodi cliccabili) per assegnare le entita direttamente da una vista coerente con la card.

## 0.3.142

- Energy Wizard: step `Entita realtime` e `Entita giornaliere` ora aprono popup dedicato di mappatura (meno incasinato, flusso guidato).
- Popup mappatura: aggiunti pulsanti rapidi “clicca valore” per assegnare `entity_id` con prompt immediato.
- `applyEnergyWizard` ora sincronizza anche i campi top-level energy (`pv/home/grid/battery`, `inverter_voltage_entity_id`, `load_frequency_entity_id`, daily entities).
- Backend snapshot energy: aggiunti `inverter_voltage_entity_id` e `load_frequency_entity_id` + normalizzati `inverter_voltage_v`/`load_frequency_hz`.
- Wrapper Sunsynk: mapping automatico dei nuovi entity id per tensione/frequenza e lettura da `energy.normalized`.

## 0.3.141

- Energy wrapper: rimossi elementi UI di debug/fallback (`Random` e barra stato testuale) dalla pagina dashboard.
- Fix critico binding entita: il wrapper aggiorna gli stati usando gli `entity_id` reali definiti in `cardConfig.entities` (non più solo `sensor.mock_*`), così i valori reali appaiono nella card.

## 0.3.140

- Aggiunto endpoint diagnostico `GET /api/energy/debug` per vedere config energy, entita card parse-ate e snapshot energia effettivo letto dal backend.
- Utile per identificare subito entita non lette/parse error senza dover fare debug a mano nel wrapper.

## 0.3.139

- Fix critico lettura entita HA: `_fetch_ha_entity_state` ora usa parser numerico robusto (`_to_float_or_none`) invece di parse float rigido.
- Corretto caso in cui lo stato entita e presente ma non veniva convertito, causando `value=None` e dashboard a zero.

## 0.3.138

- Hotfix zero persistente: il wrapper Energy ora applica direttamente i valori raw da `energy.card_entities` ai sensori mock della card a ogni polling.
- Bypassate eventuali perdite nella sola pipeline `normalized`, mantenendo popolate anche tensioni/correnti/status/daily quando presenti nelle entita card.

## 0.3.137

- Hotfix dashboard valori a zero: backend espone `energy.card_entities` con valori raw delle entita Sunsynk dal JSON card.
- Wrapper Energy usa fallback diretto da `card_entities` quando i campi `energy.normalized` non sono valorizzati.
- Aggiunto status debug live nel wrapper (PV/HOME/GRID/BAT) per verifica immediata dati in ingresso.

## 0.3.136

- Nuova pagina dedicata `Energy Setup` separata da `Setting`, accessibile dalla topbar come tab vero.
- In `Energy Setup` rimane solo la configurazione Energy (wizard + opzioni card + entita + segni) con pulsante salvataggio dedicato.
- `Setting` torna pulito con sole configurazioni generali (meteo/sistema/tende).

## 0.3.135

- UI Energy piu leggibile: aumentati font, padding e dimensioni controlli nella sezione `Setting -> Energy`.
- Topbar: aggiunto link `Energy Setup` (come gli altri link) che apre direttamente la sezione energy di configurazione.

## 0.3.134

- Fix definitivo parsing valori entita HA: supportati formati stringa comuni (`1,23`, `231.5 V`, `-42W`) nel backend.
- Questo evita `None` nei normalizzati e blocco dashboard a zero quando le entita non sono float puri.

## 0.3.133

- Wizard Energy: aggiunto campo mancante `Daily grid export entity` (`day_grid_export_77`) per completare la mappatura entita giornaliere.
- Wrapper dashboard aggiornato: supporta `day_grid_export_77` in sensorIds, fallback da Setting e aggiornamento realtime da `grid_export_today_kwh`.

## 0.3.132

- UI semplificata: rimossa la pagina duplicata `Energy Wizard` dal top menu.
- Rimane un solo wizard ufficiale in `Setting -> Energy` per evitare confusione.

## 0.3.131

- Fix valori a zero dashboard energy: backend ora usa fallback automatico dalle entita di `sunsynk_card_config_json` quando i campi base `energy.*` sono vuoti.
- Mapping fallback copre potenze principali (PV, Home/Inverter, Grid, Battery), SOC e contatori daily principali.

## 0.3.130

- Fix persistenza topologia FV: senza JSON esplicito, il wrapper ora forza fallback a 1 FV (pv2 vuoto) invece di riaprire a 2 FV di default.
- La dashboard resta coerente con i Setting salvati finche non viene configurato un secondo MPPT nel JSON card.

## 0.3.129

- Fix topologia dashboard Sunsynk: ora il wrapper applica sempre la configurazione reale del wizard per MPPT/entita.
- Se `solar.mppts=1` (o manca PV2), il secondo FV viene disattivato automaticamente.
- Fallback robusto: anche con JSON card incompleto/malfomato, la dashboard non torna a 2 FV di default.

## 0.3.128

- Setting > Energy: aggiunti flag segno `+/-` accanto alle entita di potenza (PV, Home, Grid, Battery).
- La dashboard Sunsynk applica i flag direttamente al mapping realtime, correggendo subito valori invertiti.
- Compatibilita mantenuta con i vecchi toggle invert_grid_sign/invert_battery_sign.

## 0.3.127

- Hotfix startup: corretto encoding UTF-8 di `backend/main.py` (errore SyntaxError su byte non UTF-8).
- Add-on torna avviabile su Home Assistant OS senza crash all'import di uvicorn.

## 0.3.126

- Fix segni potenza in dashboard Sunsynk: aggiunti toggle in Setting > Energy per invertire convenzione Grid e Battery.
- Nuove opzioni: invert_grid_sign e invert_battery_sign salvate in configurazione addon.
- Wrapper energy applica i toggle in tempo reale sul mapping da /api/data (grid_power_w, attery_power_w).

## 0.3.125

- Setting > Energy: estesa la customizzazione completa della Sunsynk card senza JSON manuale.
- Aggiunti controlli avanzati card: visibilita rami, line width dinamico/min/max, layout wide, opzioni inverter (modern/auto-scale/three-phase).
- Aggiunti parametri Solar/Battery/Load/Grid: max power, animation speed, show daily, auto-scale, capacita batteria e shutdown SOC.
- Wizard entita ampliato con mappature complete runtime (status, tensioni/correnti, frequenza, CT grid, stato connessione grid, PV V/A).
- Migliorato prefill dal JSON esistente: alla riapertura ricarica automaticamente topologia/colori/icone/opzioni/entita avanzate.

## 0.3.124

- Fix wizard Energy: corretta serializzazione colori per Sunsynk card (colour invece di color).
- Ora le modifiche palette impostate nel wizard vengono applicate realmente a solar/battery/load/grid nella card originale.

## 0.3.123

- Wizard Energy: aggiunto step Icone con selettori per icone carichi essenziali (load1..load6) e non essenziali (grid.load1..load3).
- Supportate icone native Sunsynk: default, oiler, ircon, pump, oven.
- Il JSON generato include ora anche gli override icona per load e grid oltre a topologia/colori/entita.

## 0.3.122

- Setting > Energy: aggiunto wizard step-by-step per generare automaticamente la sunsynk_card_config_json (topologia, colori, entita realtime/daily, review).
- Il wizard costruisce una card config Full coerente con Sunsynk e scrive il JSON pronto nel campo configurazione card.
- Aggiunto prefill iniziale del wizard dai campi Energy gia configurati (power/SOC/daily).

## 0.3.121

- Setting > Energy: aggiunto campo JSON sunsynk_card_config_json per configurare tutta la card Sunsynk (mppt, batterie, carichi, entities, opzioni full) dalla UI addon.
- Wrapper standalone: carica la configurazione da /api/options e la applica in deep-merge alla cardConfig runtime prima dell'inizializzazione.
- Persistenza completa: nuova chiave supportata in backend defaults, salvataggio opzioni e schema addon (config.yaml).

## 0.3.120

- Sunsynk Wrapper: disattivato update random automatico e attivato polling dati reali da addon (../api/data) ogni 2 secondi.
- Mapping realtime su sensori mock da energy.normalized (PV, battery power/SOC, grid, home/inverter) con render live della card originale.
- Aggiornamento daily energy quando disponibili (pv_energy_today_kwh, home_energy_today_kwh, grid_import_today_kwh).
- Random lasciato come fallback manuale tramite pulsante UI.

## 0.3.119

- Sunsynk Wrapper: allineato tema scuro al background addon (#080a10) per continuita visiva tra UI principale e dashboard energia.
- Aggiornate variabili colore base (primary-background/card/text) e toolbar wrapper per coerenza dark mode.

## 0.3.118

- Sunsynk Wrapper: migliorato mock window.hass con supporto temi (	hemes.dark = true) per resa grafica dark consistente.
- Rafforzata struttura sensori mock: stati stringa + attributi completi (unit_of_measurement, device_class, state_class) per rendering unita/icone piu affidabile.
- Rifinita updateSensors(newData) per preservare metadati entita durante gli update realtime.
- README aggiornato con sezione dedicata alla dashboard standalone basata su card originale Slipx06.

## 0.3.117

- Energy Dashboard: aggiunto wrapper standalone sunsynk-wrapper.html che esegue la card originale Sunsynk da CDN senza Home Assistant installato.
- Implementato window.hass mock globale con states, localize() e utilita minime per compatibilita runtime della card.
- Aggiunta API frontend updateSensors(newData) per aggiornare i sensori mock e forzare re-render realtime.
- Demo live inclusa con refresh dati ogni secondo e bottone Random Update per test rapido.
- Aggiornato routing dashboard: energy-dashboard/ ora punta al wrapper e il link Energy Flow in UI Admin apre energy-dashboard/sunsynk-wrapper.html.

## 0.3.116

- Sunsynk Standalone: rework completo verso layout Full fedele al repository di riferimento (iewBox 720x405, geometrie e path principali allineati).
- Flussi energia riallineati alla logica originale: animazione a pallino su path SVG con nimateMotion, inversione direzione tramite keyPoints (;1 / 1;0) e supporto invert_flow.
- Velocita animazioni auto-scalata con formula originale (nimation_speed, max_power, potenza istantanea) su solar/battery/grid/load.
- Confermato supporto aggiornamento realtime con setPowerData(json) e polling nativo ../api/data da energy.normalized.

## 0.3.115

- Energy Dashboard: aggiunta nuova variante standalone Sunsynk in `web/public/energy-dashboard/sunsynk-standalone/` (HTML/CSS/JS puro, nessuna dipendenza Home Assistant/LitElement/custom-card).
- Estratta e applicata la logica core di flusso dal progetto Sunsynk: inversione direzione (`invert_flow`) e auto-scaling velocita animazioni in base alla potenza (`animation_speed`/`max_power`).
- Introdotta API frontend `setPowerData(json)` per aggiornamento realtime da backend addon.
- Aggiunto polling nativo su `../api/data` con mapping automatico da `energy.normalized` (`pv_power_w`, `home_power_w`, `grid_power_w`, `battery_power_w`, `battery_soc_pct`).
- Separato il layout in `styles.css` con coordinate modificabili via CSS variables (`--solar-x`, `--solar-y`, `--inverter-x`, ecc.) per tuning rapido posizioni nodi/linee.

## 0.3.114

- Energy Dashboard: ridotto affollamento UI con gerarchia visiva piu netta (label piu piccole, valori principali piu grandi) e rimozione overlap testi.
- Layout convertito in griglia fissa 3 colonne (`Solar/Legnaia` | `Inverter/Battery/Status` | `CED/Consumo/Grid`) per lettura immediata.
- Flussi SVG rifiniti: linee piu sottili (max ~3px), curve morbide e animazione `stroke-dasharray` in stile trailing light.
- Card uniformate in glassmorphism high-end: `backdrop-filter: blur(10px)`, gradiente leggero, bordo 1px con opacita 20%.
- Icone integrate nei box con glow coerente al flusso energetico associato (gold/violet/cyan/slate).

## 0.3.113

- Energy Dashboard: sostituita pagina `/energy-dashboard` con versione single-file HTML5 Neon Cyberpunk (Tailwind CDN + Framer Motion).
- Nuovo layout glassmorphism dark (`#080a10`) con flussi SVG neon animati (`stroke-dasharray`) e glow aggressivo per sorgenti/consumi/rete/batteria.
- Implementata responsivita completa con scaling dinamico della scena (desktop/tablet/mobile) mantenendo il posizionamento relativo del mock originale.
- Mantenuti valori statici e nodi di stato principali del pannello (`1,16 kW`, `231,5 V`, `50,02 Hz`) e codifica colori energia per linea funzionale.

## 0.3.112

- Energy Dashboard: refactor completo icone in stile soft isometric premium (SVG inline) per casa, fotovoltaico, batteria, rete, pompa di calore, rack dati, wall box e carichi casa.
- Migliorata coerenza grafica dispositivi (ombre morbide, palette chiara uniforme, dettaglio visivo allineato).
- Batteria dinamica per SOC mantenuta e integrata nel nuovo design isometrico.
- Flussi energetici azzurri animati con profondita/glow leggermente aumentati.

## 0.3.111

- Fix publish Energy Dashboard: riallineato `web/public/energy-dashboard/index.html` al bundle JS corrente.
- Applicate in release le modifiche grafiche Energy (`rack dati`, `wall box`, `carichi casa`, FV dinamico, batteria SOC dinamica).

## 0.3.110

- Energy scene: fotovoltaico dinamico con icona meteo/produzione (`sole`, `nuvola`, `luna`) e indicatore `+/-`.
- Aggiunti nuovi device nel diagramma: `Rack Dati`, `Wall Box` e `Carichi Casa` separati.
- Batteria resa dinamica: livello riempimento e colore in funzione del SOC.
- Aggiornati flussi energetici e label per i nuovi rami (rack/wallbox/carichi).

## 0.3.109

- Energy Dashboard light: contrasto aumentato (testi, icone, flussi) e leggibilita generale migliorata.
- Scena centrale ingrandita (~25-30%) con casa, FV, batteria e rete piu evidenti.
- Flussi energetici resi piu chiari: linee piu spesse, particelle piu visibili e label riposizionate.
- Metriche integrate in scena allineate a destra con spaziatura/unita migliorate; `Real-time Power` allineato al consumo casa.
- Pannello UI ottimizzato: larghezza utile maggiore (`94vw`) e altezza compatta (`~78vh`) con riduzione vuoti laterali.

## 0.3.108

- Energy Dashboard: abbandonato React Flow nella scena centrale, ora rendering SVG custom puro.
- Nuovo stile light premium (sfondo chiaro, pannello ghiaccio, ombre morbide) in linea con app inverter.
- Layout scena ripulito: FV alto, casa centrale, batteria basso-sx, rete basso-dx, pompa lato dx.
- Metriche principali integrate nella scena a destra (`Real-time Power`, `Installed Power`, `Produzione Oggi`, `Consumo Oggi`).
- Flussi energetici SVG alleggeriti (linee sottili azzurre, particelle animate soft, meno glow).

## 0.3.107

- Refactor completo `Energy Flow` in stile dashboard premium (non piu look flowchart tecnico).
- Nuovi `nodeTypes`: `energyNode` compatto e `homeNode` centrale enfatizzato.
- Nuovo `edgeType` premium: gradient brillante, glow e particella animata direzionale su path.
- Layout fisso: FV alto, casa centro, batteria basso-sx, rete basso-dx, pompa/carichi laterali.
- UI pulita: header minimal, pill metriche top, mini-card bottom (`oggi prodotto`, `oggi consumato`, `autonomia batteria`).
- Dati live da `../api/data` con fallback simulato solo in assenza API.

## 0.3.106

- Fix critico `Energy Flow`: rimossa simulazione fake React.
- La dashboard flow ora legge i dati reali da `../api/data` (payload `energy.normalized`).
- Allineamento con entita configurate in `Setting > Energy` (potenze, SOC, import/export, kWp).

## 0.3.105

- Integrata dashboard energetica standalone React (`Energy Flow`) direttamente nell'addon.
- Nuovo mount backend: `/energy-dashboard` (statico interno addon, compatibile ingress/proxy).
- Aggiunto link rapido `Energy Flow` in UI Admin (apertura nuova scheda).
- Build React copiata in `web/public/energy-dashboard` e pubblicata insieme alla UI principale.

## 0.3.104

- Energy UI: introdotti temi selezionabili (`Classic Inverter`, `Technical Dark`, `Minimal Light`).
- Nuovo layout `Classic Inverter` piu vicino al mock: flow board con nodi FV/Casa/Rete/Batteria e KPI laterali.
- Tema impostabile da `Setting > Energy` e forzabile da URL `?view=energy&theme=...`.
- Persistenza tema nelle opzioni addon (`energy.theme`) e disponibilita nel payload backend.

## 0.3.103

- Nuova pagina dedicata `Energy` per UI User, accessibile via `?view=energy` (layout senza pulsanti locali di navigazione).
- Dashboard energia con potenze realtime (FV, casa, rete, batteria), SOC batteria e KPI giornalieri.
- Nuova sezione `Setting > Energy` per taratura entita Home Assistant:
  `pv_power`, `home_power`, `grid_power`, `battery_power`, `battery_soc`,
  `pv_energy_today`, `home_energy_today`, `grid_import_today`, `grid_export_today`, `pv_installed_kwp`.
- Backend esteso con snapshot energia (`payload.energy`) e normalizzazione unita W/kW e Wh/kWh.

## 0.3.101

- Fix layout smartphone UI User (`?view=user`): ridisegnati breakpoint mobile per logo, mappa, controlli simulazione e card KPI.
- Timeline mobile resa leggibile (etichette orarie diradate), toggle impilati su singola colonna e spaziatura migliorata.
- Ordine blocchi ottimizzato su schermi piccoli: mappa prima, legenda subito sotto, niente overlap/affollamento.

## 0.3.100

- Hardening polling UI User/Admin su proxy instabile: `loadData()` ora evita richieste concorrenti a `api/data`.
- Aggiunto backoff esponenziale (fino a 60s) dopo errori HTTP/fetch su `api/data` per ridurre 502 ripetuti e stabilizzare la UI.
- Nessun crash UI: in caso di errore dati, la pagina resta attiva e riprova automaticamente con ritmo degradato.

## 0.3.99

- Rimossa la vista `user-lite`: ripristinata `UI User` standard con mappa come configurazione principale.
- Test stabilita WebView: disattivato splash su `view=user` (delay 0) per eliminare possibili race iniziali overlay/render.

## 0.3.98

- Aggiunta nuova vista `UI User Lite` senza mappa/Leaflet per ambienti WebView instabili.
- Accesso via query string: `?view=user-lite` (alias: `ui-user-lite`, `user_public_lite`).
- Vista lite mantiene KPI e dati meteo/stazione principali ma evita completamente bootstrap mappa.

## 0.3.97

- Aggiunti endpoint diagnostici static asset per validazione proxy/WebView:
  - `GET /api/diag/static_hashes` (hash/size dei file statici principali e riferimenti `index-*.js/css`)
  - `GET /api/diag/static_hash?path=...` (hash/size di un file statico specifico)
- Scopo: confronto oggettivo hash/size tra upstream e proxy per individuare truncation/alterazioni.

## 0.3.96

- Hardening WebView: build frontend non minificata (`minify: false`, `cssMinify: false`) per ridurre rischi di parse-error su ambienti embedded/proxy.
- Compatibilita runtime: bootstrap app con retry mount (fino a 3 tentativi) prima di mostrare errore bloccante.
- Target build impostato a `es2018` per maggiore compatibilita con WebView legacy.

## 0.3.95

- WebView hardening: `loadData()` ora gestisce errori fetch (`ERR_EMPTY_RESPONSE`) senza eccezioni non catturate.
- Ridotto rumore/retry mappa durante polling: su refresh periodico non parte piu la catena retry aggressiva se container non presente.
- Retry mappa resta attivo su mount/cambio vista, ma con fallback non bloccante.

## 0.3.94

- Fix bootstrap mappa (WebView/Control4/Android): inizializzazione resa lazy e solo su viste `user`/`user_public`.
- Aggiunte guardie robuste su container DOM mappa con retry controllato (max 20 tentativi, 100ms) senza crash globale UI.
- Aggiunta protezione idempotente (`dataset.mapInit`) contro doppia inizializzazione e race su tab switch.
- Migliorata gestione tab switch: `invalidateSize()` e redraw solo quando mappa realmente pronta.
- Fallback non bloccante: in assenza container la UI continua ad avviarsi e logga warning.

## 0.3.93

- Fix encoding UI: corretti caratteri corrotti/mojibake in tutte le schermate (`Â°`, `Ã`, frecce, simboli unita).
- Tooltip mappa e testi meteo ripuliti (es. `Az ... -> ...`, `°C`, `W/m²`, `Tiles © Esri`).
- Corrette anche le unita MQTT diagnostiche backend (`°`, `°C`, `µg/m³`).

## 0.3.92

- Fix logo UI Admin in Ingress: il logo principale ora e bundlato da `src/assets/logo-main.png` (niente richiesta `GET /logo.png` su root Home Assistant).
- Eliminato errore browser `logo.png 404` in apertura da Ingress.

## 0.3.91

- Fix Ingress Home Assistant: build frontend con path relativi (`base: './'`) per evitare richieste errate a `/assets/...` su root HA.
- Fix Ingress API: endpoint frontend chiamati con path relativi (`api/...`) invece di assoluti (`/api/...`).
- Corretto riferimento logo UI Admin per evitare errore di build frontend.

## 0.3.90

- Fix compatibilita manifest addon: rimosso `ingress_entry` da `config.yaml` (chiave non supportata su alcune installazioni Home Assistant).
- Ripristinata visibilita addon nella raccolta/repository.

## 0.3.89

- Bump versione correttivo: riallineata release dopo numerazione gia in uso.
- Confermato fix accesso ingress/sidebar Home Assistant (`ingress_entry: true`).

## 0.3.88

- Addon: aggiunto `ingress_entry: true` in configurazione per rendere stabile l'apertura da sidebar Home Assistant (ingress).
- Fix accesso UI da Home Assistant: allineata configurazione ingresso pannello addon.

## 0.3.87

- UI User: aumentata la spaziatura tra mappa e controlli orari (simulazione/flag) per evitare elementi troppo a ridosso della mappa.
- UI User: aggiunto contenitore visivo dedicato ai controlli mappa sotto la vista Leaflet per separazione piu chiara.

## 0.3.86

- UI User: aggiunto slider simulazione oraria (stesso `timeIndex` della UI Admin) con orario simulato visibile.
- UI User: aggiunti toggle flag mappa visibili in pagina user (allineati ai controlli Admin).

## 0.3.85

- UI User mappa: ora usa lo stesso renderer della UI Admin (`drawSolarOverlay`) con stessi overlay e stessa geometria (linee, cerchi, settori, assi, arco solare, vento).
- Uniformato il comportamento tra `UI Admin` e `UI User` passando sul medesimo motore grafico.

## 0.3.84

- UI User: logo e-Tende portato al doppio delle dimensioni.
- UI User: splash iniziale con logo e-Tende per 3 secondi su apertura pagina user (`/?view=user`).
- UI User: alzata l'altezza header per evitare taglio logo.

## 0.3.83

- UI User: logo e-Tende ingrandito in testata.

## 0.3.82

- UI User header: logo e-Tende centrato.
- Rimossi ora e data dalla UI User.
- Corrette proporzioni header per evitare taglio elementi.

## 0.3.81

- UI User: risolto logo e-Tende usando import asset compilato (`src/assets/logo-etende.png`).
- UI User: rimosso il menu superiore (`PANORAMICA/TENDE/...`) come richiesto.
- UI Admin: mantenuto un solo accesso a UI User (`/?view=user`).

## 0.3.80

- UI Admin: unificato accesso `UI User` in un solo elemento (rimosso duplicato tasto+link).
- UI User: sostituito logo con asset ufficiale e-Tende (`logo-etende.png`) dal componente.
- Corretto rendering caratteri speciali in UI (`°`, `°C`).

## 0.3.79

- Aggiunto link dedicato alla `UI User`: `/?view=user`.
- `UI User` ora apre direttamente via query string (`view=user`, `view=ui-user`, `view=user_public`).
- Integrato logo `e-Tende Intelligenti` nella `UI User` (`/logo-etende.png`).

## 0.3.78

- `UI User` resa molto piu vicina al layout di riferimento: pagina standalone senza barra admin, top header dedicato, sidebar legenda colori per tende e vento.
- Mappa `UI User` potenziata con overlay grafici (raggi alba/tramonto, arco solare, etichette `Alba`/`Tramonto`, settori tende).
- Migliorata gerarchia visiva della schermata utente (proporzioni titolo/ora, blocchi laterali e card stato).

## 0.3.77

- Aggiunta nuova pagina `UI User` dedicata, senza pulsanti/link verso le altre sezioni.
- Rinominata pagina esistente in `UI Admin` e aggiunto accesso a `UI User` dalla barra admin.
- Nuova `UI User` con layout dashboard ispirato al mock richiesto: header dedicato, sidebar meteo, mappa grande e cards stato in basso.

## 0.3.76

- User UI meteo: migliorato layout dashboard con cards compatte e allineamento `start` per eliminare i grandi vuoti verticali.
- Corretto stretch dei badge in header card (`source-head`) e resa leggibile uniforme delle metriche.
- Rifinita gerarchia visiva (titoli card, sfondi, separatori) per una lettura molto piu chiara.

## 0.3.75

- Fix backend `api/data` 500: risolto `UnboundLocalError` in `_build_weather_guard` quando la stazione meteo reale risulta gia selezionata e la lista candidati web non veniva inizializzata.

## 0.3.74

- Restyling User UI meteo con layout piu pulito e leggibile: metriche allineate in righe chiave/valore.
- Migliorata sezione `Reali Stazione Meteo` con badge stato chiari (`WG`, `Stazione SI/NO`) e pannello Weather Guard separato.
- Elenco completo entita stazione spostato in blocco espandibile, per ridurre rumore visivo mantenendo tutti i dati disponibili.

## 0.3.73

- Fix disponibilita stazione meteo: il calcolo freschezza ora usa il timestamp piu recente tra le entita lette, non il piu vecchio.
- Risolto falso `Stazione disponibile: NO` quando alcuni sensori (tipicamente pioggia a zero) non aggiornano spesso il `last_updated`.

## 0.3.72

- Weather Station auto-discovery migliorato: fallback piu robusti per evitare campi vuoti (in particolare temperatura/umidita esterna quando i nomi entita non contengono `outdoor`).
- Estesa configurazione Weather Station in Setting con campi completi: `Dew Point`, `Feels Like`, `Solar Lux`, `Solar Radiation`, `VPD`.
- User UI: sezione `Reali Stazione Meteo` ora mostra anche l'elenco completo delle entita rilevate dalla stazione con valore e unita.
- Migliorata lettura dati reali stazione/web mantenendo fallback automatico Weather Guard.

## 0.3.71

- User UI: aggiunto auto-refresh periodico dati (polling ogni 15 secondi) quando la tab attiva e `User UI`.
- Eliminata necessità di refresh manuale continuo per aggiornare meteo/sonde/stazione/FV.

## 0.3.70

- User UI chiarezza sorgenti: testi stato WG/stazione resi espliciti (`fallback`, `stazione disponibile SI/NO`, allarmi meteo leggibili).
- Stazione meteo: aggiunti sensori importanti in mapping/visualizzazione (`Dew Point`, `Temperatura percepita`, `Solar Lux`, `Solar Radiation`, `VPD`).
- Auto-discovery `device_id` esteso ai nuovi sensori Ecowitt.

## 0.3.69

- User UI dati meteo: visualizzazione completa di tutti i campi `normalized` disponibili per `Meteo Web` e `Stazione Meteo`, non piu solo subset fisso.
- Aggiunte etichette leggibili, unita automatiche e ordinamento coerente dei campi per migliorare chiarezza origine dati.

## 0.3.68

- User UI: riorganizzata sezione dati in blocchi chiari per sorgente (`Meteo Web`, `Reali Sonde`, `Reali Stazione Meteo`, `Fotovoltaico`).
- Migliorata leggibilita origine dati con etichette esplicite e stato sorgente attiva per Weather Guard.

## 0.3.67

- User UI mappa vento: migliorata chiarezza visiva della linea con label esplicita `VENTO DA ...` e testa linea evidenziata.
- Rimossa mini-legenda accanto al toggle per mantenere interfaccia pulita, spostando il significato direttamente sulla traccia mappa.

## 0.3.66

- Completata fix toggle vento mappa: render del layer vento reso indipendente da `drawSolarOverlay` con `ensureWindDirectionLayer()`.
- Aggiunto cleanup/retry timer dedicato e watcher diretto su vento (`mapWindDirDeg/mapWindMs`) per ri-disegno affidabile dopo OFF/ON.
- Corretto caso residuo in cui la linea non tornava nonostante il ri-enable del flag.

## 0.3.65

- User UI mappa vento: fix definitivo toggle OFF/ON con inizializzazione immediata cache vento (`watch ... immediate`) e doppio redraw anti-race al ri-enable.
- Migliorata persistenza visiva della linea vento usando ultimo valore valido direzione/velocita.

## 0.3.64

- User UI mappa vento: fix toggle OFF/ON della direzione vento con fallback robusto su `weather_guard` e ultimo valore valido noto.
- Aggiunti watcher dedicati per forzare ridisegno overlay vento al cambio flag, evitando casi in cui la linea non riappare.

## 0.3.63

- Fix runtime Leaflet: esteso guard anti-race anche a `Control.addTo(...)` (non solo `Layer.addTo(...)`) per evitare crash su target mappa/control temporaneamente null.
- Stabilizzata User UI nei toggle/refresh rapidi della mappa.

## 0.3.62

- Fix runtime User UI: introdotto guard globale Leaflet su `Layer.addTo(...)` per evitare crash quando il target mappa risulta temporaneamente `null` durante race di rendering/tab switch.
- Risolto errore bootstrap: `TypeError: Cannot read properties of null (reading 'addLayer')`.

## 0.3.61

- Frontend bootstrap hardening: aggiunto fail-safe in `main.js` con gestione errori globali (`error` e `unhandledrejection`) e pannello errore a schermo.
- In caso di crash runtime iniziale, la UI non resta piu su pagina blu vuota: mostra il messaggio tecnico da condividere per diagnosi immediata.

## 0.3.60

- Fix User UI: aggiunto failsafe splash screen per evitare pagina blu vuota in caso di errore JS durante init (`onMounted`).
- La splash viene chiusa comunque dopo timeout breve e l'init e protetto con `try/catch`.

## 0.3.59

- User UI Meteo: etichette stazione reale rese esplicite (`WS Temperatura esterna`, `WS Umidita esterna`, `WS Pressione`, `WS Indice UV`, `WS Pioggia`, `WS Vento`).
- User UI Mappa: aggiunto flag `Direzione vento su mappa` per mostrare/nascondere freccia vento con velocita.
- Rendering vento su mappa: priorita ai dati stazione reale, fallback ai dati meteo web.

## 0.3.58

- Weather Station UI: auto-fill da `device_id` eseguito anche al caricamento della pagina Settings quando il campo e gia valorizzato.
- Risolto caso in cui i campi restavano vuoti finche l'utente non modificava manualmente il campo `device_id`.

## 0.3.57

- Weather Station UI: auto-compilazione campi sensori quando viene impostato `device_id` (auto-discovery), senza sovrascrivere valori manuali gia presenti.
- Nuovo endpoint `GET /api/weather_station/autofill` per preview/mapping automatico entita da `device_id`.
- Auto-mapping Ecowitt migliorato con criteri ibridi (nome entita + `device_class` + unita), riducendo i casi di campi vuoti.

## 0.3.56

- Weather Station: aggiunto supporto `device_id` con auto-discovery entita meteo da Home Assistant (`device_entities`), mantenendo priorita ai campi `entity_id` manuali quando compilati.
- Weather Station: aggiunti campi opzionali extra per Ecowitt (`outdoor_temp_entity_id`, `outdoor_humidity_entity_id`, `pressure_entity_id`, `uv_index_entity_id`).
- Weather Guard: priorita esplicita ai dati stazione reale quando validi e freschi; fallback API web (MET/Open-Meteo) solo se stazione assente/non valida/stale.
- UI Settings: estesa sezione `Weather Station e-Control` con `device_id` e campi sensori extra.

## 0.3.55

- UI Wizard Tende/Cover: rinominato titolo in `Wizard taratura cover`.

## 0.3.54

- UI Wizard Tende/Cover: aggiunto simulatore `What-if` nello step Verifica per confrontare configurazione attuale e proposta prima del salvataggio.

## 0.3.53

- UI Wizard Tende/Cover: nascosto il pulsante `Avanti` nell'ultimo step.

## 0.3.52

- UI Wizard Tende/Cover: aggiunte spiegazioni brevi per ogni parametro e per i preset guidati.

## 0.3.51

- UI Tende/Cover: aggiunto wizard guidato per taratura cover con step Base, Sole, Posizioni, Meteo, Termico e Verifica.

## 0.3.50

- UI grafici: ridotta la dimensione dei font SVG per assi, titoli asse e tooltip su grafici aria/FV/meteo.

## 0.3.49

- UI Tende/Cover: aggiunta configurazione strategia termica da termostato climate condivisibile tra piu cover.
- Diagnostica Tende/Cover: mostrati termostato, modalita, temperatura interna, setpoint e decisione termica.

## 0.3.48

- Fix versione UI/API: allineato `APP_VERSION` backend a `0.3.48`, così il titolo mostra la release reale invece di `0.3.40`.

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














