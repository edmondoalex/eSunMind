import asyncio
import json
import os
import threading
import time
import uuid
from datetime import datetime
from math import cos, pi
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import paho.mqtt.client as mqtt
import pytz
from astral import Observer
from astral.moon import azimuth as moon_azimuth_deg
from astral.moon import elevation as moon_altitude_deg
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from geopy.geocoders import Nominatim
from suncalc import get_position, get_times

try:
    from suncalc import get_moon_position as _get_moon_position  # type: ignore
except Exception:
    _get_moon_position = None

try:
    from suncalc import get_moon_times as _get_moon_times  # type: ignore
except Exception:
    _get_moon_times = None

APP_VERSION = "0.2.92"
app = FastAPI(title="e-SunMind", version=APP_VERSION)
app.mount("/assets", StaticFiles(directory="/app/static/assets"), name="assets")

DATA_FILE = Path("/data/suncalc_data.json")
OPTIONS_FILE = Path("/data/options.json")
LOCAL_OPTIONS_FILE = Path("/data/local_options.json")
FORECAST_FILE = Path("/data/forecast_solar.json")
WEATHER_FILE = Path("/data/weather_met.json")
WEATHER_OPEN_METEO_FILE = Path("/data/weather_open_meteo.json")
AIR_QUALITY_FILE = Path("/data/air_quality_openmeteo.json")
TENDE_MAP_FILE = Path("/data/tende_map.json")
STATE_FILE = Path("/data/state.json")
FORECAST_MIN_INTERVAL_SECONDS = 3600
WEATHER_MIN_INTERVAL_SECONDS = 900
AIR_QUALITY_MIN_INTERVAL_SECONDS = 1800
WORKER_STATE: dict[str, Any] = {
    "last_loop_ts": 0.0,
    "last_ok_ts": 0.0,
    "last_error": None,
    "forecast_last_fetch_ts": 0.0,
    "forecast_last_error": None,
    "forecast_backoff_until_ts": 0.0,
    "mqtt_connected": False,
    "mqtt_last_error": None,
    "tende_map_connected": False,
    "tende_map_last_error": None,
    "tende_map_last_msg_ts": 0.0,
    "tende_map_availability": "unknown",
}

TENDE_MAP_RUNTIME: dict[str, Any] = {
    "client": None,
    "cfg_key": None,
    "thread": None,
    "stop_event": None,
    "lock": threading.Lock(),
}


def _dt_to_iso(value):
    if value is None:
        return None
    return value.isoformat()


def _parse_forecast_dt(value: str) -> datetime | None:
    s = str(value or "").strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None


def _moon_illumination(now_utc: datetime) -> dict[str, float]:
    # Approximation independent from suncalc package internals.
    # Synodic month ~29.53058867 days, known new moon reference.
    ref_new_moon = datetime(2000, 1, 6, 18, 14, tzinfo=pytz.utc)
    days = (now_utc - ref_new_moon).total_seconds() / 86400.0
    synodic = 29.53058867
    phase = (days % synodic) / synodic
    fraction = 0.5 * (1.0 - cos(2.0 * pi * phase))
    return {"fraction": float(fraction), "phase": float(phase)}


def _rad_to_deg(value):
    if value is None:
        return None
    return float(value) * 180.0 / pi


def _suncalc_azimuth_to_compass_deg(azimuth_rad):
    if azimuth_rad is None:
        return None
    return (float(azimuth_rad) * 180.0 / pi + 180.0) % 360.0


def _load_options() -> dict[str, Any]:
    defaults = {
        "latitude": 44.6973,
        "longitude": 7.8683,
        "timezone": "Europe/Rome",
        "interval_minutes": 15,
        "location_query": "",
        "pv_actual_entity_id": "sensor.zcs_easas_1_activepower_pv_ext",
        "external_temp_entity_id": "sensor.temperature_and_humidity_sensor_lite_eterna_terrazzo_temperature",
        "mqtt": {
            "enabled": False,
            "host": "192.168.3.13",
            "port": 1883,
            "username": "",
            "password": "",
            "base_topic": "e-sunmind",
            "discovery_prefix": "homeassistant",
            "client_id": "e-sunmind-addon",
        },
        "forecast_solar": {
            "enabled": False,
            "api_key": "",
            "declination": 30,
            "azimuth": 0,
            "kwp": 6.0,
        },
        "weather": {
            "enabled": True,
            "provider": "met",
        },
        "air_quality": {
            "enabled": True,
            "provider": "open_meteo",
        },
        "tende_map": {
            "enabled": True,
            "mqtt_host": "192.168.3.13",
            "mqtt_port": 1883,
            "mqtt_username": "",
            "mqtt_password": "",
            "topic_state": "e-tendeintelligenti/map/shades",
            "topic_availability": "e-tendeintelligenti/availability",
            "stale_seconds": 180,
        },
    }
    if not OPTIONS_FILE.exists():
        return defaults
    try:
        payload = json.loads(OPTIONS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return defaults
    for key in ("latitude", "longitude", "timezone", "interval_minutes", "location_query", "pv_actual_entity_id", "external_temp_entity_id"):
        if key in payload:
            defaults[key] = payload[key]
    if isinstance(payload.get("mqtt"), dict):
        defaults["mqtt"].update(payload["mqtt"])
    if isinstance(payload.get("forecast_solar"), dict):
        defaults["forecast_solar"].update(payload["forecast_solar"])
    if isinstance(payload.get("weather"), dict):
        defaults["weather"].update(payload["weather"])
    if isinstance(payload.get("air_quality"), dict):
        defaults["air_quality"].update(payload["air_quality"])
    if isinstance(payload.get("tende_map"), dict):
        defaults["tende_map"].update(payload["tende_map"])
    # Local overrides are owned by addon UI and persist independently from HA-managed options.
    local = _load_local_options_raw()
    if isinstance(local.get("mqtt"), dict):
        defaults["mqtt"].update(local["mqtt"])
    if isinstance(local.get("forecast_solar"), dict):
        defaults["forecast_solar"].update(local["forecast_solar"])
    if isinstance(local.get("weather"), dict):
        defaults["weather"].update(local["weather"])
    if isinstance(local.get("air_quality"), dict):
        defaults["air_quality"].update(local["air_quality"])
    if isinstance(local.get("tende_map"), dict):
        defaults["tende_map"].update(local["tende_map"])
    defaults["interval_minutes"] = max(1, min(1440, int(defaults.get("interval_minutes", 15) or 15)))
    defaults["forecast_solar"]["declination"] = max(0, min(90, int(defaults["forecast_solar"].get("declination", 30) or 30)))
    defaults["forecast_solar"]["azimuth"] = max(-180, min(180, int(defaults["forecast_solar"].get("azimuth", 0) or 0)))
    defaults["forecast_solar"]["kwp"] = max(0.1, min(1000.0, float(defaults["forecast_solar"].get("kwp", 6.0) or 6.0)))
    defaults["weather"]["provider"] = str(defaults["weather"].get("provider") or "met").strip().lower()
    defaults["air_quality"]["provider"] = str(defaults["air_quality"].get("provider") or "open_meteo").strip().lower()
    defaults["tende_map"]["stale_seconds"] = max(30, min(86400, int(defaults["tende_map"].get("stale_seconds", 180) or 180)))
    return defaults


def _load_options_raw() -> dict[str, Any]:
    if not OPTIONS_FILE.exists():
        return {}
    try:
        raw = json.loads(OPTIONS_FILE.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _load_local_options_raw() -> dict[str, Any]:
    if not LOCAL_OPTIONS_FILE.exists():
        return {}
    try:
        raw = json.loads(LOCAL_OPTIONS_FILE.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _save_local_options_raw(payload: dict[str, Any]) -> None:
    LOCAL_OPTIONS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def _save_options_raw(payload: dict[str, Any]) -> None:
    OPTIONS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _validate_tende_map_payload(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    shades_in = payload.get("shades")
    if not isinstance(shades_in, list):
        return None
    shades_out: list[dict[str, Any]] = []
    for item in shades_in:
        if not isinstance(item, dict):
            continue
        shade_id = str(item.get("id") or "").strip()
        if not shade_id:
            continue
        try:
            az_start = float(item.get("azimuth_start_deg"))
            az_end = float(item.get("azimuth_end_deg"))
        except Exception:
            continue
        alt_min = item.get("altitude_min_deg")
        alt_max = item.get("altitude_max_deg")
        shades_out.append(
            {
                "id": shade_id,
                "name": str(item.get("name") or shade_id),
                "cover_entity": (str(item.get("cover_entity")).strip() if item.get("cover_entity") else None),
                "enabled": bool(item.get("enabled", True)),
                "active": bool(item.get("active", False)),
                "azimuth_start_deg": az_start % 360.0,
                "azimuth_end_deg": az_end % 360.0,
                "altitude_min_deg": float(alt_min) if alt_min is not None else None,
                "altitude_max_deg": float(alt_max) if alt_max is not None else None,
                "priority": int(item.get("priority")) if item.get("priority") is not None else None,
                "color": (str(item.get("color")).strip() if item.get("color") else None),
            }
        )
    if not shades_out:
        return None
    return {
        "updated_at": str(payload.get("updated_at") or datetime.utcnow().isoformat()),
        "source": str(payload.get("source") or "e-tendeintelligenti"),
        "shades": shades_out,
    }


def _read_tende_map_payload() -> dict[str, Any] | None:
    if not TENDE_MAP_FILE.exists():
        return None
    try:
        raw = json.loads(TENDE_MAP_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None
    return _validate_tende_map_payload(raw)


def _build_tende_map_snapshot(cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    if cfg is None:
        cfg = _load_options()
    tm_cfg = (cfg.get("tende_map") or {}) if isinstance(cfg, dict) else {}
    stale_seconds_cfg = max(30, int(tm_cfg.get("stale_seconds", 180) or 180))
    payload = _read_tende_map_payload()
    last_msg_ts = float(WORKER_STATE.get("tende_map_last_msg_ts", 0.0) or 0.0)
    stale = True if last_msg_ts <= 0 else (time.time() - last_msg_ts) > stale_seconds_cfg
    availability = str(WORKER_STATE.get("tende_map_availability") or "unknown")
    if payload is None:
        return {
            "ok": False,
            "availability": availability,
            "stale": True,
            "updated_at": None,
            "source": "e-tendeintelligenti",
            "shades": [],
        }
    shades = payload.get("shades") or []
    cover_states: dict[str, Any] = {}
    for s in shades:
        if not isinstance(s, dict):
            continue
        ce = str(s.get("cover_entity") or "").strip()
        if not ce or ce in cover_states:
            continue
        st = _fetch_ha_entity_state(ce)
        if isinstance(st, dict):
            cover_states[ce] = {
                "ok": bool(st.get("ok")),
                "state": st.get("state"),
                "value": st.get("value"),
                "unit": st.get("unit"),
                "error": st.get("error"),
                "last_updated": st.get("last_updated"),
            }
    return {
        "ok": True,
        "availability": availability,
        "stale": stale,
        "updated_at": payload.get("updated_at"),
        "source": payload.get("source") or "e-tendeintelligenti",
        "shades": shades,
        "cover_states": cover_states,
    }


def _start_tende_map_subscriber(cfg: dict[str, Any]) -> None:
    tm_cfg = (cfg.get("tende_map") or {}) if isinstance(cfg, dict) else {}
    if not tm_cfg.get("enabled", True):
        return
    cfg_key = json.dumps(tm_cfg, sort_keys=True)
    with TENDE_MAP_RUNTIME["lock"]:
        if TENDE_MAP_RUNTIME.get("thread") is not None and TENDE_MAP_RUNTIME.get("cfg_key") == cfg_key:
            return
        stop_event = TENDE_MAP_RUNTIME.get("stop_event")
        if isinstance(stop_event, threading.Event):
            stop_event.set()
        TENDE_MAP_RUNTIME["stop_event"] = threading.Event()
        TENDE_MAP_RUNTIME["cfg_key"] = cfg_key

    def _runner(local_cfg: dict[str, Any], local_stop: threading.Event) -> None:
        host = str(local_cfg.get("mqtt_host") or "core-mosquitto")
        port = int(local_cfg.get("mqtt_port") or 1883)
        username = str(local_cfg.get("mqtt_username") or "").strip()
        password = str(local_cfg.get("mqtt_password") or "")
        topic_state = str(local_cfg.get("topic_state") or "e-tendeintelligenti/map/shades")
        topic_av = str(local_cfg.get("topic_availability") or "e-tendeintelligenti/availability")

        def _on_connect(client: mqtt.Client, _userdata: Any, _flags: Any, rc: int) -> None:
            if rc == 0:
                WORKER_STATE["tende_map_connected"] = True
                WORKER_STATE["tende_map_last_error"] = None
                client.subscribe(topic_state, qos=1)
                client.subscribe(topic_av, qos=1)
            else:
                WORKER_STATE["tende_map_connected"] = False
                WORKER_STATE["tende_map_last_error"] = f"connect_rc_{rc}"

        def _on_disconnect(_client: mqtt.Client, _userdata: Any, _rc: int) -> None:
            WORKER_STATE["tende_map_connected"] = False

        def _on_message(_client: mqtt.Client, _userdata: Any, msg: mqtt.MQTTMessage) -> None:
            topic = str(msg.topic or "")
            text = ""
            try:
                text = msg.payload.decode("utf-8", errors="replace")
            except Exception:
                text = ""
            if topic == topic_av:
                val = text.strip().lower()
                WORKER_STATE["tende_map_availability"] = val if val in {"online", "offline"} else "unknown"
                _save_state()
                return
            if topic != topic_state:
                return
            try:
                parsed = json.loads(text)
                validated = _validate_tende_map_payload(parsed)
                if validated is None:
                    raise ValueError("invalid_payload")
                TENDE_MAP_FILE.write_text(json.dumps(validated, ensure_ascii=False, indent=2), encoding="utf-8")
                WORKER_STATE["tende_map_last_msg_ts"] = time.time()
                # If state payload is valid, assume source is online even if availability topic is missing.
                if str(WORKER_STATE.get("tende_map_availability") or "unknown") == "unknown":
                    WORKER_STATE["tende_map_availability"] = "online"
                WORKER_STATE["tende_map_last_error"] = None
            except Exception as exc:
                WORKER_STATE["tende_map_last_error"] = str(exc)
            finally:
                _save_state()

        while not local_stop.is_set():
            client: mqtt.Client | None = None
            try:
                client = mqtt.Client(client_id=f"e-sunmind-tende-map-{int(time.time())}")
                if username:
                    client.username_pw_set(username, password)
                client.on_connect = _on_connect
                client.on_disconnect = _on_disconnect
                client.on_message = _on_message
                client.connect(host, port, 60)
                with TENDE_MAP_RUNTIME["lock"]:
                    TENDE_MAP_RUNTIME["client"] = client
                client.loop_start()
                while not local_stop.is_set():
                    time.sleep(1.0)
            except Exception as exc:
                WORKER_STATE["tende_map_connected"] = False
                WORKER_STATE["tende_map_last_error"] = str(exc)
                _save_state()
                time.sleep(5.0)
            finally:
                try:
                    if client is not None:
                        client.loop_stop()
                        client.disconnect()
                except Exception:
                    pass
                with TENDE_MAP_RUNTIME["lock"]:
                    if TENDE_MAP_RUNTIME.get("client") is client:
                        TENDE_MAP_RUNTIME["client"] = None

    thread = threading.Thread(
        target=_runner,
        args=(dict(tm_cfg), TENDE_MAP_RUNTIME["stop_event"]),
        name="tende-map-subscriber",
        daemon=True,
    )
    with TENDE_MAP_RUNTIME["lock"]:
        TENDE_MAP_RUNTIME["thread"] = thread
    thread.start()


def _fetch_forecast_solar(cfg: dict[str, Any], latitude: float, longitude: float) -> dict[str, Any] | None:
    fs = cfg.get("forecast_solar", {})
    if not fs or not fs.get("enabled"):
        return None

    api_key = str(fs.get("api_key") or "").strip()
    key_seg = quote(api_key) if api_key else ""
    decl = int(fs.get("declination", 30))
    azim = int(fs.get("azimuth", 0))
    kwp = float(fs.get("kwp", 6.0))

    # Public API works without key: omit key segment completely.
    if key_seg:
        url = f"https://api.forecast.solar/{key_seg}/estimate/{latitude}/{longitude}/{decl}/{azim}/{kwp}"
    else:
        url = f"https://api.forecast.solar/estimate/{latitude}/{longitude}/{decl}/{azim}/{kwp}"
    try:
        with urlopen(url, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return {"ok": True, "url": url, "payload": payload}
    except URLError as exc:
        return {"ok": False, "url": url, "error": str(exc)}


def _fetch_weather_met(cfg: dict[str, Any], latitude: float, longitude: float) -> dict[str, Any] | None:
    wc = cfg.get("weather", {}) or {}
    if not wc.get("enabled", True):
        return None
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={latitude}&lon={longitude}"
    req = Request(url, headers={"User-Agent": "e-SunMind/0.2 (+https://github.com/edmondoalex/eSunMind)"})
    try:
        with urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except URLError as exc:
        return {"ok": False, "provider": "met", "url": url, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "provider": "met", "url": url, "error": str(exc)}

    ts = (((payload or {}).get("properties") or {}).get("timeseries")) or []
    if not isinstance(ts, list) or not ts:
        return {"ok": False, "provider": "met", "url": url, "error": "invalid_payload_timeseries"}

    first = ts[0] if isinstance(ts[0], dict) else {}
    first_data = (first.get("data") or {}) if isinstance(first, dict) else {}
    instant = ((first_data.get("instant") or {}).get("details") or {}) if isinstance(first_data, dict) else {}
    next1 = ((first_data.get("next_1_hours") or {}) if isinstance(first_data, dict) else {})
    summary = ((next1.get("summary") or {}) if isinstance(next1, dict) else {})
    details_1h = ((next1.get("details") or {}) if isinstance(next1, dict) else {})

    normalized = {
        "time": first.get("time"),
        "air_temperature_c": instant.get("air_temperature"),
        "relative_humidity_pct": instant.get("relative_humidity"),
        "wind_speed_ms": instant.get("wind_speed"),
        "wind_from_direction_deg": instant.get("wind_from_direction"),
        "air_pressure_hpa": instant.get("air_pressure_at_sea_level"),
        "cloud_area_fraction_pct": instant.get("cloud_area_fraction"),
        "uv_index": instant.get("ultraviolet_index_clear_sky"),
        "symbol_code": summary.get("symbol_code"),
        "precipitation_next_1h_mm": details_1h.get("precipitation_amount"),
    }

    return {
        "ok": True,
        "provider": "met",
        "url": url,
        "normalized": normalized,
        "payload": payload,
    }


def _fetch_weather_open_meteo(cfg: dict[str, Any], latitude: float, longitude: float) -> dict[str, Any] | None:
    wc = cfg.get("weather", {}) or {}
    if not wc.get("enabled", True):
        return None
    vars_hourly = "temperature_2m,relative_humidity_2m,pressure_msl,cloud_cover,precipitation,wind_speed_10m,wind_direction_10m,uv_index,weather_code"
    vars_current = "temperature_2m,relative_humidity_2m,pressure_msl,cloud_cover,precipitation,wind_speed_10m,wind_direction_10m,uv_index,weather_code"
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&current={vars_current}&hourly={vars_hourly}&timezone=auto&forecast_days=2"
    )
    try:
        with urlopen(url, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"ok": False, "provider": "open_meteo", "url": url, "error": str(exc)}

    cur = payload.get("current") or {}
    normalized = {
        "time": cur.get("time"),
        "air_temperature_c": cur.get("temperature_2m"),
        "relative_humidity_pct": cur.get("relative_humidity_2m"),
        "wind_speed_ms": (float(cur.get("wind_speed_10m")) / 3.6) if cur.get("wind_speed_10m") is not None else None,
        "wind_from_direction_deg": cur.get("wind_direction_10m"),
        "air_pressure_hpa": cur.get("pressure_msl"),
        "cloud_area_fraction_pct": cur.get("cloud_cover"),
        "uv_index": cur.get("uv_index"),
        "symbol_code": cur.get("weather_code"),
        "precipitation_next_1h_mm": cur.get("precipitation"),
    }
    return {
        "ok": True,
        "provider": "open_meteo",
        "url": url,
        "normalized": normalized,
        "payload": payload,
    }


def _fetch_weather(cfg: dict[str, Any], latitude: float, longitude: float) -> dict[str, Any] | None:
    wc = cfg.get("weather", {}) or {}
    if not wc.get("enabled", True):
        return None
    provider = str(wc.get("provider") or "met").strip().lower()
    if provider == "met":
        return _fetch_weather_met(cfg, latitude, longitude)
    if provider == "open_meteo":
        return _fetch_weather_open_meteo(cfg, latitude, longitude)
    if provider == "hybrid":
        res = _fetch_weather_met(cfg, latitude, longitude)
        if isinstance(res, dict) and res.get("ok"):
            return res
        fb = _fetch_weather_open_meteo(cfg, latitude, longitude)
        if isinstance(fb, dict):
            fb["_fallback_from"] = "met"
        return fb
    return {"ok": False, "provider": provider, "error": "provider_not_supported"}


def _fetch_ha_entity_state(entity_id: str) -> dict[str, Any] | None:
    entity = str(entity_id or "").strip()
    if not entity:
        return None
    token = os.environ.get("SUPERVISOR_TOKEN", "").strip() or os.environ.get("HASSIO_TOKEN", "").strip()
    if not token:
        for path in (
            "/run/s6/container_environment/SUPERVISOR_TOKEN",
            "/var/run/s6/container_environment/SUPERVISOR_TOKEN",
        ):
            try:
                token = Path(path).read_text(encoding="utf-8").strip()
            except Exception:
                token = token or ""
            if token:
                break
    if not token:
        return {"ok": False, "entity_id": entity, "error": "missing_supervisor_token"}
    url = f"http://supervisor/core/api/states/{quote(entity)}"
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"ok": False, "entity_id": entity, "error": str(exc)}

    state_raw = payload.get("state")
    attrs = payload.get("attributes") or {}
    numeric_value = None
    try:
        numeric_value = float(state_raw)
    except Exception:
        try:
            numeric_value = float(str(state_raw).replace(",", "."))
        except Exception:
            numeric_value = None
    return {
        "ok": True,
        "entity_id": entity,
        "state": state_raw,
        "value": numeric_value,
        "unit": attrs.get("unit_of_measurement"),
        "watts": numeric_value,
        "friendly_name": attrs.get("friendly_name"),
        "last_updated": payload.get("last_updated"),
    }


def _fetch_air_quality_open_meteo(cfg: dict[str, Any], latitude: float, longitude: float) -> dict[str, Any] | None:
    aq = cfg.get("air_quality", {}) or {}
    if not aq.get("enabled", True):
        return None
    provider = str(aq.get("provider") or "open_meteo").strip().lower()
    if provider != "open_meteo":
        return {"ok": False, "provider": provider, "error": "provider_not_supported"}

    current_vars = "european_aqi,us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone"
    hourly_vars = "european_aqi,us_aqi,pm10,pm2_5,ozone,nitrogen_dioxide"
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={latitude}&longitude={longitude}"
        f"&current={current_vars}&hourly={hourly_vars}&timezone=auto"
    )
    try:
        with urlopen(url, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"ok": False, "provider": "open_meteo", "url": url, "error": str(exc)}

    cur = payload.get("current") or {}
    normalized = {
        "time": cur.get("time"),
        "european_aqi": cur.get("european_aqi"),
        "us_aqi": cur.get("us_aqi"),
        "pm10": cur.get("pm10"),
        "pm2_5": cur.get("pm2_5"),
        "carbon_monoxide": cur.get("carbon_monoxide"),
        "nitrogen_dioxide": cur.get("nitrogen_dioxide"),
        "sulphur_dioxide": cur.get("sulphur_dioxide"),
        "ozone": cur.get("ozone"),
    }
    return {
        "ok": True,
        "provider": "open_meteo",
        "url": url,
        "normalized": normalized,
        "payload": payload,
    }


def _read_forecast_cache() -> dict[str, Any] | None:
    if not FORECAST_FILE.exists():
        return None
    try:
        return json.loads(FORECAST_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_weather_cache() -> dict[str, Any] | None:
    if not WEATHER_FILE.exists():
        return None
    try:
        return json.loads(WEATHER_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_weather_open_meteo_cache() -> dict[str, Any] | None:
    if not WEATHER_OPEN_METEO_FILE.exists():
        return None
    try:
        return json.loads(WEATHER_OPEN_METEO_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_air_quality_cache() -> dict[str, Any] | None:
    if not AIR_QUALITY_FILE.exists():
        return None
    try:
        return json.loads(AIR_QUALITY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_tende_map_cache() -> dict[str, Any] | None:
    if not TENDE_MAP_FILE.exists():
        return None
    try:
        raw = json.loads(TENDE_MAP_FILE.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else None
    except Exception:
        return None


def _normalize_tende_map_payload(payload: dict[str, Any]) -> dict[str, Any]:
    shades_in = payload.get("shades") if isinstance(payload, dict) else None
    shades_out = []
    if isinstance(shades_in, list):
        for item in shades_in:
            if not isinstance(item, dict):
                continue
            sid = str(item.get("id") or "").strip()
            if not sid:
                continue
            try:
                az_start = float(item.get("azimuth_start_deg"))
                az_end = float(item.get("azimuth_end_deg"))
            except Exception:
                continue
            alt_min = item.get("altitude_min_deg")
            alt_max = item.get("altitude_max_deg")
            shades_out.append(
                {
                    "id": sid,
                    "name": str(item.get("name") or sid),
                    "cover_entity": (str(item.get("cover_entity")).strip() if item.get("cover_entity") else None),
                    "enabled": bool(item.get("enabled", True)),
                    "active": bool(item.get("active", False)),
                    "azimuth_start_deg": az_start % 360.0,
                    "azimuth_end_deg": az_end % 360.0,
                    "altitude_min_deg": float(alt_min) if alt_min is not None else None,
                    "altitude_max_deg": float(alt_max) if alt_max is not None else None,
                    "priority": int(item.get("priority")) if item.get("priority") is not None else None,
                    "color": (str(item.get("color")).strip() if item.get("color") else None),
                }
            )
    return {
        "ok": True,
        "source": str(payload.get("source") or "e-tendeintelligenti"),
        "updated_at": payload.get("updated_at"),
        "shades": shades_out,
    }


def _tende_map_mqtt_start_or_refresh(cfg: dict[str, Any]) -> None:
    tc = (cfg.get("tende_map") or {})
    if not tc.get("enabled", True):
        with TENDE_MAP_RUNTIME["lock"]:
            client = TENDE_MAP_RUNTIME.get("client")
            if client is not None:
                try:
                    client.loop_stop()
                    client.disconnect()
                except Exception:
                    pass
                TENDE_MAP_RUNTIME["client"] = None
                TENDE_MAP_RUNTIME["cfg_key"] = None
        WORKER_STATE["tende_map_connected"] = False
        return

    cfg_key = "|".join(
        [
            str(tc.get("mqtt_host") or ""),
            str(tc.get("mqtt_port") or 1883),
            str(tc.get("mqtt_username") or ""),
            str(tc.get("topic_state") or ""),
            str(tc.get("topic_availability") or ""),
        ]
    )
    with TENDE_MAP_RUNTIME["lock"]:
        if TENDE_MAP_RUNTIME.get("client") is not None and TENDE_MAP_RUNTIME.get("cfg_key") == cfg_key:
            return
        old = TENDE_MAP_RUNTIME.get("client")
        if old is not None:
            try:
                old.loop_stop()
                old.disconnect()
            except Exception:
                pass

        host = str(tc.get("mqtt_host") or "192.168.3.13").strip()
        port = int(tc.get("mqtt_port") or 1883)
        username = str(tc.get("mqtt_username") or "").strip()
        password = str(tc.get("mqtt_password") or "")
        topic_state = str(tc.get("topic_state") or "e-tendeintelligenti/map/shades").strip()
        topic_av = str(tc.get("topic_availability") or "e-tendeintelligenti/availability").strip()

        client = mqtt.Client(client_id="e-sunmind-tende-map")
        if username:
            client.username_pw_set(username, password)

        def _on_connect(c, _u, _f, rc):
            try:
                c.subscribe(topic_state, qos=0)
                c.subscribe(topic_av, qos=0)
                WORKER_STATE["tende_map_connected"] = True
                WORKER_STATE["tende_map_last_error"] = None
            except Exception as exc:
                WORKER_STATE["tende_map_last_error"] = str(exc)

        def _on_disconnect(_c, _u, _rc):
            WORKER_STATE["tende_map_connected"] = False

        def _on_message(_c, _u, msg):
            now_ts = time.time()
            WORKER_STATE["tende_map_last_msg_ts"] = now_ts
            try:
                if msg.topic == topic_av:
                    val = (msg.payload.decode("utf-8", errors="ignore").strip().lower() or "unknown")
                    WORKER_STATE["tende_map_availability"] = val if val in {"online", "offline"} else "unknown"
                    return
                if msg.topic != topic_state:
                    return
                decoded = msg.payload.decode("utf-8", errors="ignore")
                parsed = json.loads(decoded)
                norm = _normalize_tende_map_payload(parsed if isinstance(parsed, dict) else {})
                norm["_received_at_ts"] = now_ts
                TENDE_MAP_FILE.write_text(json.dumps(norm, ensure_ascii=False, indent=2), encoding="utf-8")
                WORKER_STATE["tende_map_last_error"] = None
            except Exception as exc:
                WORKER_STATE["tende_map_last_error"] = str(exc)

        client.on_connect = _on_connect
        client.on_disconnect = _on_disconnect
        client.on_message = _on_message
        try:
            client.connect(host, port, 60)
            client.loop_start()
            TENDE_MAP_RUNTIME["client"] = client
            TENDE_MAP_RUNTIME["cfg_key"] = cfg_key
        except Exception as exc:
            WORKER_STATE["tende_map_connected"] = False
            WORKER_STATE["tende_map_last_error"] = str(exc)
            TENDE_MAP_RUNTIME["client"] = None
            TENDE_MAP_RUNTIME["cfg_key"] = None


def _build_tende_map_data(cfg: dict[str, Any]) -> dict[str, Any]:
    tc = (cfg.get("tende_map") or {})
    if not tc.get("enabled", True):
        return {"ok": False, "error": "disabled", "availability": "unknown", "stale": True, "shades": []}
    cached = _read_tende_map_cache()
    if cached is None:
        return {"ok": False, "error": "data_not_ready", "availability": WORKER_STATE.get("tende_map_availability", "unknown"), "stale": True, "shades": []}
    last_ts = float(cached.get("_received_at_ts", 0.0) or 0.0)
    stale_seconds = int(tc.get("stale_seconds") or 180)
    stale = (time.time() - last_ts) > stale_seconds if last_ts > 0 else True
    return {
        "ok": True,
        "source": cached.get("source") or "e-tendeintelligenti",
        "updated_at": cached.get("updated_at"),
        "availability": WORKER_STATE.get("tende_map_availability", "unknown"),
        "stale": stale,
        "shades": cached.get("shades") if isinstance(cached.get("shades"), list) else [],
        "_received_at_ts": last_ts,
        "_stale_seconds": stale_seconds,
    }


def _save_state() -> None:
    try:
        STATE_FILE.write_text(json.dumps(WORKER_STATE, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def _load_state() -> None:
    if not STATE_FILE.exists():
        return
    try:
        raw = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            WORKER_STATE.update(raw)
    except Exception:
        pass


def _compute_data(cfg: dict[str, Any]) -> dict[str, Any]:
    latitude = float(cfg["latitude"])
    longitude = float(cfg["longitude"])
    location_query = str(cfg.get("location_query") or "").strip()
    resolved_location = None

    if location_query:
        try:
            geolocator = Nominatim(user_agent="e-sunmind-addon")
            found = geolocator.geocode(location_query, language="it")
            if found is not None:
                latitude = float(found.latitude)
                longitude = float(found.longitude)
                resolved_location = {
                    "query": location_query,
                    "display_name": found.address,
                    "latitude": latitude,
                    "longitude": longitude,
                }
        except Exception:
            resolved_location = {"query": location_query, "error": "geocoding_failed_using_manual_coordinates"}

    tz = pytz.timezone(str(cfg["timezone"]))
    now = datetime.now(tz)
    now_utc = now.astimezone(pytz.utc)

    sun_times = {k: _dt_to_iso(v.astimezone(tz)) for k, v in get_times(now_utc, longitude, latitude).items()}
    sun_position_raw = get_position(now_utc, longitude, latitude)
    sun_position = {
        "azimuth_deg": _rad_to_deg(sun_position_raw.get("azimuth")),
        "azimuth_compass_deg": _suncalc_azimuth_to_compass_deg(sun_position_raw.get("azimuth")),
        "altitude_deg": _rad_to_deg(sun_position_raw.get("altitude")),
        "azimuth_rad": sun_position_raw.get("azimuth"),
        "altitude_rad": sun_position_raw.get("altitude"),
    }
    if _get_moon_position is not None:
        moon_position_raw = _get_moon_position(now_utc, longitude, latitude)
        moon_position = {
            "azimuth_deg": _rad_to_deg(moon_position_raw.get("azimuth")),
            "altitude_deg": _rad_to_deg(moon_position_raw.get("altitude")),
            "azimuth_rad": moon_position_raw.get("azimuth"),
            "altitude_rad": moon_position_raw.get("altitude"),
        }
    else:
        try:
            obs = Observer(latitude=latitude, longitude=longitude)
            moon_position = {
                "azimuth_deg": float(moon_azimuth_deg(obs, now)),
                "altitude_deg": float(moon_altitude_deg(obs, now)),
                "azimuth_rad": None,
                "altitude_rad": None,
            }
        except Exception:
            moon_position = {"azimuth_deg": None, "altitude_deg": None, "azimuth_rad": None, "altitude_rad": None}
    moon_illumination = _moon_illumination(now_utc)
    moon_times = {}
    if _get_moon_times is not None:
        moon_times_raw = _get_moon_times(now_utc, longitude, latitude)
        for key, value in moon_times_raw.items():
            moon_times[key] = _dt_to_iso(value.astimezone(tz)) if hasattr(value, "astimezone") else value

    return {
        "timestamp_local": now.isoformat(),
        "timezone": str(cfg["timezone"]),
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "resolved_location": resolved_location,
        "sun_times": sun_times,
        "sun_position": sun_position,
        "moon_position": moon_position,
        "moon_illumination": moon_illumination,
        "moon_times": moon_times,
    }


def _mqtt_publish_discovery(client: mqtt.Client, cfg: dict[str, Any]) -> None:
    prefix = str(cfg["mqtt"]["discovery_prefix"]).strip() or "homeassistant"
    base = str(cfg["mqtt"]["base_topic"]).strip() or "sunmind"
    device = {
        "identifiers": ["e-sunmind-addon"],
        "name": "e-SunMind",
        "manufacturer": "EA SAS",
        "model": "e-SunMind Add-on",
        "sw_version": APP_VERSION,
    }
    sensors = [
        ("sun_altitude", "Sun Altitude", "°", None, "measurement"),
        ("sun_azimuth", "Sun Azimuth", "°", None, "measurement"),
        ("sun_azimuth_compass", "Sun Azimuth Compass", "°", None, "measurement"),
        ("moon_altitude", "Moon Altitude", "°", None, "measurement"),
        ("moon_azimuth", "Moon Azimuth", "°", None, "measurement"),
        ("moon_fraction", "Moon Illumination", "%", None, "measurement"),
        ("moon_phase", "Moon Phase", None, None, "measurement"),
        ("pv_today_wh", "PV Forecast Today", "Wh", "energy", "total"),
        ("pv_tomorrow_wh", "PV Forecast Tomorrow", "Wh", "energy", "total"),
        ("pv_now_w", "PV Forecast Current", "W", "power", "measurement"),
        ("pv_live_w", "PV Real Power", "W", "power", "measurement"),
        ("pv_live_ratio", "PV Real/Forecast Ratio", None, None, "measurement"),
        ("external_temp_c", "External Temperature Real", "°C", "temperature", "measurement"),
        ("weather_temp_c", "Weather Temperature", "°C", "temperature", "measurement"),
        ("weather_humidity_pct", "Weather Humidity", "%", "humidity", "measurement"),
        ("weather_pressure_hpa", "Weather Pressure", "hPa", "atmospheric_pressure", "measurement"),
        ("weather_cloud_pct", "Weather Cloud Cover", "%", None, "measurement"),
        ("weather_wind_ms", "Weather Wind Speed", "m/s", "wind_speed", "measurement"),
        ("weather_wind_dir_deg", "Weather Wind Direction", "°", None, "measurement"),
        ("weather_precip_1h_mm", "Weather Rain Next 1h", "mm", "precipitation", "measurement"),
        ("weather_uv_index", "Weather UV Index", None, None, "measurement"),
        ("airq_eu_aqi", "Air Quality EU AQI", None, "aqi", "measurement"),
        ("airq_us_aqi", "Air Quality US AQI", None, "aqi", "measurement"),
        ("airq_pm25", "Air Quality PM2.5", "µg/m³", "pm25", "measurement"),
        ("airq_pm10", "Air Quality PM10", "µg/m³", "pm10", "measurement"),
        ("airq_no2", "Air Quality NO2", "µg/m³", "nitrogen_dioxide", "measurement"),
        ("airq_o3", "Air Quality O3", "µg/m³", "ozone", "measurement"),
    ]
    for key, name, unit, dclass, state_class in sensors:
        topic = f"{prefix}/sensor/sunmind/{key}/config"
        payload = {
            "name": name,
            "object_id": f"sunmind_{key}",
            "unique_id": f"sunmind_{key}",
            "state_topic": f"{base}/state/{key}",
            "availability_topic": f"{base}/availability",
            "device": device,
            "state_class": state_class,
        }
        if unit:
            payload["unit_of_measurement"] = unit
        if dclass:
            payload["device_class"] = dclass
        client.publish(topic, json.dumps(payload), retain=True)

    diag_text_sensors = [
        ("pv_read_status", "PV Read Status"),
        ("temp_read_status", "External Temp Read Status"),
    ]
    for key, name in diag_text_sensors:
        topic = f"{prefix}/sensor/sunmind/{key}/config"
        payload = {
            "name": name,
            "object_id": f"sunmind_{key}",
            "unique_id": f"sunmind_{key}",
            "state_topic": f"{base}/state/{key}",
            "availability_topic": f"{base}/availability",
            "icon": "mdi:information-outline",
            "entity_category": "diagnostic",
            "device": device,
        }
        client.publish(topic, json.dumps(payload), retain=True)

    # Diagnostic payloads for other addons/components.
    diag_sensor = {
        "name": "Runtime JSON",
        "object_id": "sunmind_runtime_json",
        "unique_id": "sunmind_runtime_json",
        "state_topic": f"{base}/state/runtime_status",
        "json_attributes_topic": f"{base}/state/runtime_json",
        "availability_topic": f"{base}/availability",
        "icon": "mdi:code-json",
        "entity_category": "diagnostic",
        "device": device,
    }
    client.publish(
        f"{prefix}/sensor/sunmind/runtime_json/config",
        json.dumps(diag_sensor),
        retain=True,
    )


def _mqtt_publish_state(client: mqtt.Client, cfg: dict[str, Any], data: dict[str, Any]) -> None:
    base = str(cfg["mqtt"]["base_topic"]).strip() or "sunmind"
    sp = data.get("sun_position", {})
    mp = data.get("moon_position", {})
    mi = data.get("moon_illumination", {})
    weather = (data.get("weather") or {}).get("normalized") or {}
    airq = (data.get("air_quality") or {}).get("normalized") or {}
    pv_live = data.get("pv_live") or {}
    temp_live = data.get("external_temp_live") or {}
    mapping = {
        "sun_altitude": sp.get("altitude_deg"),
        "sun_azimuth": sp.get("azimuth_deg"),
        "sun_azimuth_compass": sp.get("azimuth_compass_deg"),
        "moon_altitude": mp.get("altitude_deg"),
        "moon_azimuth": mp.get("azimuth_deg"),
        "moon_fraction": (float(mi.get("fraction", 0.0)) * 100.0),
        "moon_phase": mi.get("phase"),
        "external_temp_c": temp_live.get("value"),
        "weather_temp_c": weather.get("air_temperature_c"),
        "weather_humidity_pct": weather.get("relative_humidity_pct"),
        "weather_pressure_hpa": weather.get("air_pressure_hpa"),
        "weather_cloud_pct": weather.get("cloud_area_fraction_pct"),
        "weather_wind_ms": weather.get("wind_speed_ms"),
        "weather_wind_dir_deg": weather.get("wind_from_direction_deg"),
        "weather_precip_1h_mm": weather.get("precipitation_next_1h_mm"),
        "weather_uv_index": weather.get("uv_index"),
        "airq_eu_aqi": airq.get("european_aqi"),
        "airq_us_aqi": airq.get("us_aqi"),
        "airq_pm25": airq.get("pm2_5"),
        "airq_pm10": airq.get("pm10"),
        "airq_no2": airq.get("nitrogen_dioxide"),
        "airq_o3": airq.get("ozone"),
    }
    fs = data.get("forecast_solar", {}) or {}
    fs_result = ((fs.get("payload") or {}).get("result") or {})
    day = fs_result.get("watt_hours_day") or {}
    if isinstance(day, dict) and day:
        keys = sorted(day.keys())
        if len(keys) >= 1:
            mapping["pv_today_wh"] = day.get(keys[0])
        if len(keys) >= 2:
            mapping["pv_tomorrow_wh"] = day.get(keys[1])
    watts = fs_result.get("watts") or {}
    if isinstance(watts, dict) and watts:
        now_local = None
        try:
            ts = str(data.get("timestamp_local") or "")
            if ts:
                now_local = datetime.fromisoformat(ts)
        except Exception:
            now_local = None
        selected_key = None
        selected_dt = None
        for k in watts.keys():
            kd = _parse_forecast_dt(k)
            if kd is None:
                continue
            if now_local is None:
                if selected_dt is None or kd > selected_dt:
                    selected_dt = kd
                    selected_key = k
                continue
            # choose latest point not in the future; fallback to nearest future if needed
            if kd <= now_local.replace(tzinfo=None):
                if selected_dt is None or kd > selected_dt:
                    selected_dt = kd
                    selected_key = k
        if selected_key is None:
            # all points are in the future: choose earliest one
            for k in sorted(watts.keys()):
                if _parse_forecast_dt(k) is not None:
                    selected_key = k
                    break
        if selected_key is not None:
            mapping["pv_now_w"] = watts.get(selected_key)
    if isinstance(pv_live, dict):
        mapping["pv_live_w"] = pv_live.get("value")
    pv_now = mapping.get("pv_now_w")
    pv_real = mapping.get("pv_live_w")
    try:
        if pv_now is not None and float(pv_now) > 0 and pv_real is not None:
            mapping["pv_live_ratio"] = float(pv_real) / float(pv_now)
    except Exception:
        pass

    client.publish(f"{base}/availability", "online", retain=True)
    for key, value in mapping.items():
        if value is not None:
            client.publish(f"{base}/state/{key}", f"{value}", retain=True)
    if mapping.get("pv_live_w") is None:
        client.publish(f"{base}/state/pv_live_w", "unknown", retain=True)
    if mapping.get("external_temp_c") is None:
        client.publish(f"{base}/state/external_temp_c", "unknown", retain=True)
    if mapping.get("pv_live_ratio") is None:
        client.publish(f"{base}/state/pv_live_ratio", "unknown", retain=True)
    client.publish(
        f"{base}/state/pv_read_status",
        str((pv_live.get("error") if isinstance(pv_live, dict) else None) or "ok"),
        retain=True,
    )
    client.publish(
        f"{base}/state/temp_read_status",
        str((temp_live.get("error") if isinstance(temp_live, dict) else None) or "ok"),
        retain=True,
    )
    client.publish(
        f"{base}/state/runtime_status",
        str(data.get("timestamp_local") or "ok"),
        retain=True,
    )
    client.publish(
        f"{base}/state/runtime_json",
        json.dumps(data, ensure_ascii=False),
        retain=True,
    )


async def _worker() -> None:
    mqtt_client: mqtt.Client | None = None
    mqtt_ready = False
    while True:
        WORKER_STATE["last_loop_ts"] = time.time()
        cfg = _load_options()
        _start_tende_map_subscriber(cfg)
        try:
            data = _compute_data(cfg)
            coords = data.get("coordinates", {})
            forecast = None
            fs_cfg = cfg.get("forecast_solar", {}) or {}
            if fs_cfg.get("enabled"):
                now_ts = time.time()
                cache = _read_forecast_cache()
                last_ts = float((cache or {}).get("_fetched_at_ts", 0.0) or 0.0)
                persistent_last_ts = float(WORKER_STATE.get("forecast_last_fetch_ts", 0.0) or 0.0)
                last_effective_ts = max(last_ts, persistent_last_ts)
                backoff_until = float(WORKER_STATE.get("forecast_backoff_until_ts", 0.0) or 0.0)
                if now_ts < backoff_until and cache is not None:
                    forecast = dict(cache)
                    forecast["_cache_hit"] = True
                    forecast["_backoff_active"] = True
                elif (cache is not None) and (now_ts - last_effective_ts < FORECAST_MIN_INTERVAL_SECONDS):
                    forecast = dict(cache)
                    forecast["_cache_hit"] = True
                else:
                    forecast = _fetch_forecast_solar(cfg, float(coords["latitude"]), float(coords["longitude"]))
                    if isinstance(forecast, dict):
                        forecast["_fetched_at_ts"] = now_ts
                        forecast["_cache_hit"] = False
                        WORKER_STATE["forecast_last_fetch_ts"] = now_ts
                        if forecast.get("ok"):
                            WORKER_STATE["forecast_last_error"] = None
                            WORKER_STATE["forecast_backoff_until_ts"] = 0.0
                        else:
                            WORKER_STATE["forecast_last_error"] = str(forecast.get("error"))
                            WORKER_STATE["forecast_backoff_until_ts"] = now_ts + FORECAST_MIN_INTERVAL_SECONDS

            weather = None
            weather_open_meteo = None
            w_cfg = cfg.get("weather", {}) or {}
            if w_cfg.get("enabled", True):
                now_ts = time.time()
                w_cache = _read_weather_cache()
                w_last_ts = float((w_cache or {}).get("_fetched_at_ts", 0.0) or 0.0)
                if (w_cache is not None) and (now_ts - w_last_ts < WEATHER_MIN_INTERVAL_SECONDS):
                    weather = dict(w_cache)
                    weather["_cache_hit"] = True
                else:
                    weather = _fetch_weather(cfg, float(coords["latitude"]), float(coords["longitude"]))
                    if isinstance(weather, dict):
                        weather["_fetched_at_ts"] = now_ts
                        weather["_cache_hit"] = False
                        WEATHER_FILE.write_text(json.dumps(weather, ensure_ascii=False, indent=2), encoding="utf-8")

                # Always keep a dedicated Open-Meteo raw payload for technical comparison.
                wom_cache = _read_weather_open_meteo_cache()
                wom_last_ts = float((wom_cache or {}).get("_fetched_at_ts", 0.0) or 0.0)
                if (wom_cache is not None) and (now_ts - wom_last_ts < WEATHER_MIN_INTERVAL_SECONDS):
                    weather_open_meteo = dict(wom_cache)
                    weather_open_meteo["_cache_hit"] = True
                else:
                    weather_open_meteo = _fetch_weather_open_meteo(cfg, float(coords["latitude"]), float(coords["longitude"]))
                    if isinstance(weather_open_meteo, dict):
                        weather_open_meteo["_fetched_at_ts"] = now_ts
                        weather_open_meteo["_cache_hit"] = False
                        WEATHER_OPEN_METEO_FILE.write_text(
                            json.dumps(weather_open_meteo, ensure_ascii=False, indent=2), encoding="utf-8"
                        )
            airq = None
            aq_cfg = cfg.get("air_quality", {}) or {}
            if aq_cfg.get("enabled", True):
                now_ts = time.time()
                aq_cache = _read_air_quality_cache()
                aq_last_ts = float((aq_cache or {}).get("_fetched_at_ts", 0.0) or 0.0)
                if (aq_cache is not None) and (now_ts - aq_last_ts < AIR_QUALITY_MIN_INTERVAL_SECONDS):
                    airq = dict(aq_cache)
                    airq["_cache_hit"] = True
                else:
                    airq = _fetch_air_quality_open_meteo(cfg, float(coords["latitude"]), float(coords["longitude"]))
                    if isinstance(airq, dict):
                        airq["_fetched_at_ts"] = now_ts
                        airq["_cache_hit"] = False
                        AIR_QUALITY_FILE.write_text(json.dumps(airq, ensure_ascii=False, indent=2), encoding="utf-8")
            pv_live = _fetch_ha_entity_state(str(cfg.get("pv_actual_entity_id") or ""))
            temp_live = _fetch_ha_entity_state(str(cfg.get("external_temp_entity_id") or ""))
            data["pv_live"] = pv_live
            data["external_temp_live"] = temp_live
            data["weather"] = weather
            data["weather_open_meteo"] = weather_open_meteo
            data["air_quality"] = airq
            data["forecast_solar"] = forecast
            data["tende_map"] = _build_tende_map_snapshot(cfg)
            DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            if forecast is not None and isinstance(forecast, dict) and not forecast.get("_cache_hit", False):
                FORECAST_FILE.write_text(json.dumps(forecast, ensure_ascii=False, indent=2), encoding="utf-8")
            WORKER_STATE["last_ok_ts"] = time.time()
            WORKER_STATE["last_error"] = None
        except Exception as exc:
            WORKER_STATE["last_error"] = str(exc)
        finally:
            _save_state()

        mqtt_cfg = cfg.get("mqtt", {})
        if mqtt_cfg.get("enabled"):
            try:
                if mqtt_client is None:
                    mqtt_client = mqtt.Client(client_id=str(mqtt_cfg.get("client_id") or "sunmind-addon"))
                    username = str(mqtt_cfg.get("username") or "").strip()
                    password = str(mqtt_cfg.get("password") or "")
                    if username:
                        mqtt_client.username_pw_set(username, password)
                    mqtt_client.connect(str(mqtt_cfg.get("host") or "core-mosquitto"), int(mqtt_cfg.get("port") or 1883), 60)
                    mqtt_client.loop_start()
                    mqtt_ready = False
                if not mqtt_ready:
                    _mqtt_publish_discovery(mqtt_client, cfg)
                    mqtt_ready = True
                _mqtt_publish_state(mqtt_client, cfg, data)
                WORKER_STATE["mqtt_connected"] = True
                WORKER_STATE["mqtt_last_error"] = None
            except Exception:
                mqtt_ready = False
                WORKER_STATE["mqtt_connected"] = False
                WORKER_STATE["mqtt_last_error"] = "publish_or_connect_failed"
        else:
            WORKER_STATE["mqtt_connected"] = False

        interval = int(cfg.get("interval_minutes") or 15)
        await asyncio.sleep(max(60, interval * 60))


@app.on_event("startup")
async def _startup():
    _load_state()
    asyncio.create_task(_worker())


@app.get("/")
async def index():
    return FileResponse("/app/static/index.html")


@app.get("/logo.png")
async def logo():
    return FileResponse("/app/static/logo.png")


@app.get("/favicon.png")
async def favicon():
    return FileResponse("/app/static/favicon.png")


@app.get("/api/status")
async def status():
    return JSONResponse({"ok": True, "version": APP_VERSION, "state": WORKER_STATE})


@app.get("/api/data")
async def data():
    if not DATA_FILE.exists():
        return JSONResponse({"ok": False, "error": "data_not_ready"})
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    payload["tende_map"] = _build_tende_map_snapshot(_load_options())
    return JSONResponse(payload)


@app.get("/api/tende/map")
async def tende_map_get():
    snapshot = _build_tende_map_snapshot(_load_options())
    if not snapshot.get("ok"):
        return JSONResponse({"ok": False, "error": "data_not_ready"}, status_code=503)
    return JSONResponse(snapshot)


@app.post("/api/tende/map/update")
async def tende_map_update(payload: dict):
    if not isinstance(payload, dict):
        return JSONResponse({"ok": False, "error": "invalid_payload"}, status_code=400)
    shade_id = str(payload.get("id") or "").strip()
    if not shade_id:
        return JSONResponse({"ok": False, "error": "missing_id"}, status_code=400)
    try:
        az_start = float(payload.get("azimuth_start_deg"))
        az_end = float(payload.get("azimuth_end_deg"))
    except Exception:
        return JSONResponse({"ok": False, "error": "invalid_azimuth"}, status_code=400)

    cfg = _load_options()
    tm_cfg = (cfg.get("tende_map") or {})
    host = str(tm_cfg.get("mqtt_host") or "192.168.3.13").strip()
    port = int(tm_cfg.get("mqtt_port") or 1883)
    username = str(tm_cfg.get("mqtt_username") or "").strip()
    password = str(tm_cfg.get("mqtt_password") or "")
    cmd_topics = [
        "e-tendeintelligenti/cmd/shades/update",
        "e-tendeintelligenti/cmd/map/shades/update",
    ]
    ack_topic = "e-tendeintelligenti/cmd/shades/update/ack"
    request_id = uuid.uuid4().hex
    msg = {
        "source": "e-sunmind",
        "request_id": request_id,
        "updated_at": datetime.utcnow().isoformat(),
        "id": shade_id,
        "azimuth_start_deg": az_start % 360.0,
        "azimuth_end_deg": az_end % 360.0,
        "altitude_min_deg": payload.get("altitude_min_deg"),
        "altitude_max_deg": payload.get("altitude_max_deg"),
        "shade": {
            "id": shade_id,
            "azimuth_start_deg": az_start % 360.0,
            "azimuth_end_deg": az_end % 360.0,
            "altitude_min_deg": payload.get("altitude_min_deg"),
            "altitude_max_deg": payload.get("altitude_max_deg"),
        },
        "shades": [
            {
                "id": shade_id,
                "azimuth_start_deg": az_start % 360.0,
                "azimuth_end_deg": az_end % 360.0,
                "altitude_min_deg": payload.get("altitude_min_deg"),
                "altitude_max_deg": payload.get("altitude_max_deg"),
            }
        ],
    }
    client = None
    ack_result: dict[str, Any] | None = None
    try:
        client = mqtt.Client(client_id=f"e-sunmind-cmd-{int(time.time())}")
        if username:
            client.username_pw_set(username, password)
        def _on_message(_c: mqtt.Client, _u: Any, m: mqtt.MQTTMessage) -> None:
            nonlocal ack_result
            try:
                parsed = json.loads(m.payload.decode("utf-8", errors="ignore"))
                if isinstance(parsed, dict) and str(parsed.get("request_id") or "") == request_id:
                    ack_result = parsed
            except Exception:
                pass
        client.on_message = _on_message
        client.connect(host, port, 60)
        client.loop_start()
        client.subscribe(ack_topic, qos=1)
        for topic in cmd_topics:
            client.publish(topic, json.dumps(msg, ensure_ascii=False), qos=1, retain=False)
        t0 = time.time()
        while (time.time() - t0) < 2.2 and ack_result is None:
            time.sleep(0.05)
        if not ack_result:
            return JSONResponse(
                {"ok": False, "error": "ack_timeout", "topics": cmd_topics, "payload": msg},
                status_code=504,
            )
        if not (ack_result.get("ok") is True or str(ack_result.get("status") or "").lower() == "ok"):
            return JSONResponse(
                {"ok": False, "error": "ack_negative", "topics": cmd_topics, "payload": msg, "ack": ack_result},
                status_code=502,
            )
        return JSONResponse({"ok": True, "topics": cmd_topics, "payload": msg, "ack": ack_result})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)
    finally:
        try:
            if client is not None:
                client.loop_stop()
                client.disconnect()
        except Exception:
            pass


@app.get("/api/sun/live")
async def sun_live():
    if not DATA_FILE.exists():
        return JSONResponse({"ok": False, "error": "data_not_ready"}, status_code=503)
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    sp = payload.get("sun_position", {}) if isinstance(payload, dict) else {}
    az = sp.get("azimuth_compass_deg")
    alt = sp.get("altitude_deg")
    updated_at = payload.get("timestamp_local") if isinstance(payload, dict) else None
    if az is None or alt is None or not updated_at:
        return JSONResponse({"ok": False, "error": "data_not_ready"}, status_code=503)
    return JSONResponse(
        {
            "ok": True,
            "azimuth_compass_deg": float(az),
            "altitude_deg": float(alt),
            "updated_at": str(updated_at),
            "source": "e-sunmind",
        }
    )


@app.get("/api/solar_forecast")
async def solar_forecast():
    if not FORECAST_FILE.exists():
        return JSONResponse({"ok": False, "error": "forecast_not_ready"})
    payload = json.loads(FORECAST_FILE.read_text(encoding="utf-8"))
    return JSONResponse(payload)


@app.get("/api/health")
async def health():
    now_ts = time.time()
    stale_seconds = int(now_ts - float(WORKER_STATE.get("last_ok_ts", 0.0) or 0.0))
    return JSONResponse(
        {
            "ok": WORKER_STATE.get("last_error") is None,
            "version": APP_VERSION,
            "stale_seconds": stale_seconds,
            "worker_state": WORKER_STATE,
            "files": {
                "data_exists": DATA_FILE.exists(),
                "forecast_exists": FORECAST_FILE.exists(),
                "state_exists": STATE_FILE.exists(),
            },
        }
    )


@app.get("/api/mqtt/status")
async def mqtt_status():
    cfg = _load_options()
    mc = (cfg.get("mqtt") or {})
    return JSONResponse(
        {
            "ok": True,
            "enabled": bool(mc.get("enabled")),
            "host": str(mc.get("host") or ""),
            "port": int(mc.get("port") or 1883),
            "base_topic": str(mc.get("base_topic") or "e-sunmind"),
            "discovery_prefix": str(mc.get("discovery_prefix") or "homeassistant"),
            "client_id": str(mc.get("client_id") or "e-sunmind-addon"),
            "connected": bool(WORKER_STATE.get("mqtt_connected")),
            "last_error": WORKER_STATE.get("mqtt_last_error"),
        }
    )


@app.get("/api/options")
async def options_get():
    merged = _load_options()
    merged["_meta"] = {
        "ha_options_file": str(OPTIONS_FILE),
        "local_options_file": str(LOCAL_OPTIONS_FILE),
    }
    return JSONResponse(merged)


@app.post("/api/options/forecast_solar")
async def options_set_forecast_solar(payload: dict):
    if not isinstance(payload, dict):
        return JSONResponse({"ok": False, "error": "invalid_payload"}, status_code=400)
    raw = _load_local_options_raw()
    fs = raw.get("forecast_solar", {})
    if not isinstance(fs, dict):
        fs = {}
    for k in ("enabled", "api_key", "declination", "azimuth", "kwp"):
        if k in payload:
            fs[k] = payload[k]
    raw["forecast_solar"] = fs
    _save_local_options_raw(raw)

    # Mirror the same values into HA options file so Add-on Configuration UI shows updated values too.
    ha_raw = _load_options_raw()
    ha_fs = ha_raw.get("forecast_solar", {})
    if not isinstance(ha_fs, dict):
        ha_fs = {}
    for k in ("enabled", "api_key", "declination", "azimuth", "kwp"):
        if k in fs:
            ha_fs[k] = fs[k]
    ha_raw["forecast_solar"] = ha_fs
    try:
        _save_options_raw(ha_raw)
        saved_ha = True
    except Exception:
        saved_ha = False

    # Force immediate refresh on new forecast settings:
    # reset throttling state and clear cached forecast snapshot.
    WORKER_STATE["forecast_last_fetch_ts"] = 0.0
    WORKER_STATE["forecast_backoff_until_ts"] = 0.0
    WORKER_STATE["forecast_last_error"] = None
    try:
        if FORECAST_FILE.exists():
            FORECAST_FILE.unlink()
    except Exception:
        pass

    # Apply settings right away (without waiting next worker interval).
    refreshed = False
    refresh_error = None
    refreshed_url = None
    try:
        cfg = _load_options()
        now_data = _compute_data(cfg)
        coords = now_data.get("coordinates", {}) or {}
        forecast = None
        if cfg.get("forecast_solar", {}).get("enabled"):
            forecast = _fetch_forecast_solar(cfg, float(coords["latitude"]), float(coords["longitude"]))
            if isinstance(forecast, dict):
                now_ts = time.time()
                forecast["_fetched_at_ts"] = now_ts
                forecast["_cache_hit"] = False
                refreshed_url = forecast.get("url")
                if forecast.get("ok"):
                    WORKER_STATE["forecast_last_fetch_ts"] = now_ts
                    WORKER_STATE["forecast_last_error"] = None
                else:
                    WORKER_STATE["forecast_last_error"] = str(forecast.get("error"))
                    WORKER_STATE["forecast_backoff_until_ts"] = now_ts + FORECAST_MIN_INTERVAL_SECONDS
                FORECAST_FILE.write_text(json.dumps(forecast, ensure_ascii=False, indent=2), encoding="utf-8")
        now_data["forecast_solar"] = forecast
        DATA_FILE.write_text(json.dumps(now_data, ensure_ascii=False, indent=2), encoding="utf-8")
        refreshed = True
    except Exception as exc:
        refresh_error = str(exc)

    return JSONResponse({
        "ok": True,
        "forecast_solar": fs,
        "saved_to": str(LOCAL_OPTIONS_FILE),
        "mirrored_to_ha_options": saved_ha,
        "forecast_refreshed_now": refreshed,
        "forecast_refresh_error": refresh_error,
        "forecast_url_now": refreshed_url,
    })


@app.post("/api/options/base")
async def options_set_base(payload: dict):
    if not isinstance(payload, dict):
        return JSONResponse({"ok": False, "error": "invalid_payload"}, status_code=400)

    keys = ("latitude", "longitude", "timezone", "interval_minutes", "location_query", "pv_actual_entity_id", "external_temp_entity_id", "tende_map")

    raw = _load_local_options_raw()
    for k in keys:
        if k in payload:
            raw[k] = payload[k]
    _save_local_options_raw(raw)

    ha_raw = _load_options_raw()
    for k in keys:
        if k in payload:
            ha_raw[k] = payload[k]
    try:
        _save_options_raw(ha_raw)
        saved_ha = True
    except Exception:
        saved_ha = False

    refresh_error = None
    try:
        cfg = _load_options()
        now_data = _compute_data(cfg)
        coords = now_data.get("coordinates", {}) or {}

        forecast = None
        if cfg.get("forecast_solar", {}).get("enabled"):
            forecast = _fetch_forecast_solar(cfg, float(coords["latitude"]), float(coords["longitude"]))
            if isinstance(forecast, dict):
                forecast["_fetched_at_ts"] = time.time()
                forecast["_cache_hit"] = False
                now_data["forecast_solar"] = forecast
                FORECAST_FILE.write_text(json.dumps(forecast, ensure_ascii=False, indent=2), encoding="utf-8")

        weather = None
        weather_open_meteo = None
        if cfg.get("weather", {}).get("enabled", True):
            weather = _fetch_weather(cfg, float(coords["latitude"]), float(coords["longitude"]))
            if isinstance(weather, dict):
                weather["_fetched_at_ts"] = time.time()
                weather["_cache_hit"] = False
                now_data["weather"] = weather
                WEATHER_FILE.write_text(json.dumps(weather, ensure_ascii=False, indent=2), encoding="utf-8")

            weather_open_meteo = _fetch_weather_open_meteo(cfg, float(coords["latitude"]), float(coords["longitude"]))
            if isinstance(weather_open_meteo, dict):
                weather_open_meteo["_fetched_at_ts"] = time.time()
                weather_open_meteo["_cache_hit"] = False
                now_data["weather_open_meteo"] = weather_open_meteo
                WEATHER_OPEN_METEO_FILE.write_text(
                    json.dumps(weather_open_meteo, ensure_ascii=False, indent=2), encoding="utf-8"
                )

        now_data["pv_live"] = _fetch_ha_entity_state(str(cfg.get("pv_actual_entity_id") or ""))
        now_data["external_temp_live"] = _fetch_ha_entity_state(str(cfg.get("external_temp_entity_id") or ""))
        DATA_FILE.write_text(json.dumps(now_data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        refresh_error = str(exc)

    return JSONResponse({
        "ok": True,
        "saved_to": str(LOCAL_OPTIONS_FILE),
        "mirrored_to_ha_options": saved_ha,
        "refresh_error": refresh_error,
    })


