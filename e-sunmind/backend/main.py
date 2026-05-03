import asyncio
import json
import time
from datetime import datetime
from math import cos, pi
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import urlopen

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

APP_VERSION = "0.2.23"
app = FastAPI(title="e-SunMind", version=APP_VERSION)
app.mount("/assets", StaticFiles(directory="/app/static/assets"), name="assets")

DATA_FILE = Path("/data/suncalc_data.json")
OPTIONS_FILE = Path("/data/options.json")
FORECAST_FILE = Path("/data/forecast_solar.json")
STATE_FILE = Path("/data/state.json")
FORECAST_MIN_INTERVAL_SECONDS = 3600
WORKER_STATE: dict[str, Any] = {
    "last_loop_ts": 0.0,
    "last_ok_ts": 0.0,
    "last_error": None,
    "forecast_last_fetch_ts": 0.0,
    "forecast_last_error": None,
    "forecast_backoff_until_ts": 0.0,
}


def _dt_to_iso(value):
    if value is None:
        return None
    return value.isoformat()


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
    }
    if not OPTIONS_FILE.exists():
        return defaults
    try:
        payload = json.loads(OPTIONS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return defaults
    for key in ("latitude", "longitude", "timezone", "interval_minutes", "location_query"):
        if key in payload:
            defaults[key] = payload[key]
    if isinstance(payload.get("mqtt"), dict):
        defaults["mqtt"].update(payload["mqtt"])
    if isinstance(payload.get("forecast_solar"), dict):
        defaults["forecast_solar"].update(payload["forecast_solar"])
    defaults["interval_minutes"] = max(1, min(1440, int(defaults.get("interval_minutes", 15) or 15)))
    defaults["forecast_solar"]["declination"] = max(0, min(90, int(defaults["forecast_solar"].get("declination", 30) or 30)))
    defaults["forecast_solar"]["azimuth"] = max(-180, min(180, int(defaults["forecast_solar"].get("azimuth", 0) or 0)))
    defaults["forecast_solar"]["kwp"] = max(0.1, min(1000.0, float(defaults["forecast_solar"].get("kwp", 6.0) or 6.0)))
    return defaults


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
    except Exception as exc:
        return {"ok": False, "url": url, "error": str(exc)}


def _read_forecast_cache() -> dict[str, Any] | None:
    if not FORECAST_FILE.exists():
        return None
    try:
        return json.loads(FORECAST_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


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
        ("sun_altitude", "Sun Altitude", "deg", None),
        ("sun_azimuth", "Sun Azimuth", "deg", None),
        ("moon_altitude", "Moon Altitude", "deg", None),
        ("moon_azimuth", "Moon Azimuth", "deg", None),
        ("moon_fraction", "Moon Illumination", "%", None),
        ("pv_today_wh", "PV Forecast Today", "Wh", None),
        ("pv_tomorrow_wh", "PV Forecast Tomorrow", "Wh", None),
    ]
    for key, name, unit, dclass in sensors:
        topic = f"{prefix}/sensor/sunmind/{key}/config"
        payload = {
            "name": name,
            "unique_id": f"sunmind_{key}",
            "state_topic": f"{base}/state/{key}",
            "availability_topic": f"{base}/availability",
            "device": device,
        }
        if unit:
            payload["unit_of_measurement"] = unit
        if dclass:
            payload["device_class"] = dclass
        client.publish(topic, json.dumps(payload), retain=True)


def _mqtt_publish_state(client: mqtt.Client, cfg: dict[str, Any], data: dict[str, Any]) -> None:
    base = str(cfg["mqtt"]["base_topic"]).strip() or "sunmind"
    sp = data.get("sun_position", {})
    mp = data.get("moon_position", {})
    mi = data.get("moon_illumination", {})
    mapping = {
        "sun_altitude": sp.get("altitude_deg"),
        "sun_azimuth": sp.get("azimuth_deg"),
        "moon_altitude": mp.get("altitude_deg"),
        "moon_azimuth": mp.get("azimuth_deg"),
        "moon_fraction": (float(mi.get("fraction", 0.0)) * 100.0),
    }
    fs = data.get("forecast_solar", {}) or {}
    day = ((fs.get("payload") or {}).get("result") or {}).get("watt_hours_day") or {}
    if isinstance(day, dict) and day:
        keys = sorted(day.keys())
        if len(keys) >= 1:
            mapping["pv_today_wh"] = day.get(keys[0])
        if len(keys) >= 2:
            mapping["pv_tomorrow_wh"] = day.get(keys[1])

    client.publish(f"{base}/availability", "online", retain=True)
    for key, value in mapping.items():
        if value is not None:
            client.publish(f"{base}/state/{key}", f"{value}", retain=True)


async def _worker() -> None:
    mqtt_client: mqtt.Client | None = None
    mqtt_ready = False
    while True:
        WORKER_STATE["last_loop_ts"] = time.time()
        cfg = _load_options()
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
            data["forecast_solar"] = forecast
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
            except Exception:
                mqtt_ready = False

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
    return JSONResponse(payload)


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

