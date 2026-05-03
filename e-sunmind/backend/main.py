import asyncio
import json
import time
from datetime import datetime
from math import cos, pi
from pathlib import Path
from typing import Any

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

APP_VERSION = "0.2.3"
app = FastAPI(title="e-SunMind", version=APP_VERSION)
app.mount("/web", StaticFiles(directory="/app/web"), name="web")

DATA_FILE = Path("/data/suncalc_data.json")
OPTIONS_FILE = Path("/data/options.json")


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


def _load_options() -> dict[str, Any]:
    defaults = {
        "latitude": 44.6973,
        "longitude": 7.8683,
        "timezone": "Europe/Rome",
        "interval_minutes": 15,
        "location_query": "",
        "mqtt": {
            "enabled": False,
            "host": "core-mosquitto",
            "port": 1883,
            "username": "",
            "password": "",
            "base_topic": "sunmind",
            "discovery_prefix": "homeassistant",
            "client_id": "sunmind-addon",
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
    return defaults


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
        ("sun_altitude", "Sun Altitude", "°", None),
        ("sun_azimuth", "Sun Azimuth", "°", None),
        ("moon_altitude", "Moon Altitude", "°", None),
        ("moon_azimuth", "Moon Azimuth", "°", None),
        ("moon_fraction", "Moon Illumination", "%", None),
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
    client.publish(f"{base}/availability", "online", retain=True)
    for key, value in mapping.items():
        if value is not None:
            client.publish(f"{base}/state/{key}", f"{value}", retain=True)


async def _worker() -> None:
    mqtt_client: mqtt.Client | None = None
    mqtt_ready = False
    while True:
        cfg = _load_options()
        data = _compute_data(cfg)
        DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

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
    asyncio.create_task(_worker())


@app.get("/")
async def index():
    return FileResponse("/app/web/index.html")


@app.get("/api/status")
async def status():
    return JSONResponse({"ok": True, "version": APP_VERSION})


@app.get("/api/data")
async def data():
    if not DATA_FILE.exists():
        return JSONResponse({"ok": False, "error": "data_not_ready"})
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return JSONResponse(payload)
