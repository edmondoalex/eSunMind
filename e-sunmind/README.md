# e-SunMind Add-on

## API for integrations

Endpoint stabile per integrazione componenti esterni (es. e-Tende Intelligenti):

- `GET /api/sun/live`

Risposta `200`:

```json
{
  "ok": true,
  "azimuth_compass_deg": 134.25,
  "altitude_deg": 53.74,
  "updated_at": "2026-05-04T11:41:08.399000+02:00",
  "source": "e-sunmind"
}
```

Risposta `503` quando dati non pronti:

```json
{
  "ok": false,
  "error": "data_not_ready"
}
```

Esempio curl:

```bash
curl -sS http://192.168.3.24:1980/api/sun/live
```
