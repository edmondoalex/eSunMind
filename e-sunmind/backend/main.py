import asyncio
import hashlib
import json
import os
import re
import threading
import time
import uuid
from datetime import datetime, timedelta
from math import cos, pi
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import quote, urlencode
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

APP_VERSION = "0.3.300"
app = FastAPI(title="e-SunMind", version=APP_VERSION)
app.mount("/assets", StaticFiles(directory="/app/static/assets"), name="assets")
app.mount("/energy-dashboard", StaticFiles(directory="/app/static/energy-dashboard", html=True), name="energy_dashboard")
STATIC_ROOT = Path("/app/static")
STATIC_ASSETS_ROOT = STATIC_ROOT / "assets"

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


def _sha256_file(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def _static_file_meta(path: Path, public_path: str) -> dict[str, Any]:
    exists = path.exists() and path.is_file()
    size = path.stat().st_size if exists else None
    return {
        "public_path": public_path,
        "exists": bool(exists),
        "size_bytes": size,
        "sha256": _sha256_file(path) if exists else None,
    }


def _extract_index_asset_refs(index_html_text: str) -> dict[str, str | None]:
    import re

    js_m = re.search(r'src="(\./assets/index-[^"]+\.js)"', index_html_text)
    css_m = re.search(r'href="(\./assets/index-[^"]+\.css)"', index_html_text)
    return {
        "index_js_rel": js_m.group(1) if js_m else None,
        "index_css_rel": css_m.group(1) if css_m else None,
    }


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
        "coordinates_source_mode": "e_tende",
        "interval_minutes": 15,
        "overlay": {
            "pathRadiusM": 102,
            "sectorRadiusM": 110,
            "sunRadiusM": 95,
            "mapZoom": 18,
        },
        "location_query": "",
        "pv_actual_entity_id": "sensor.zcs_easas_1_activepower_pv_ext",
        "external_temp_entity_id": "sensor.temperature_and_humidity_sensor_lite_eterna_terrazzo_temperature",
        "external_humidity_entity_id": "sensor.temperature_and_humidity_sensor_lite_eterna_terrazzo_humidity",
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
        "weather_station": {
            "enabled": False,
            "provider": "e_control",
            "stale_seconds": 180,
            "device_id": "",
            "wind_speed_entity_id": "",
            "wind_gust_entity_id": "",
            "wind_direction_entity_id": "",
            "rain_rate_entity_id": "",
            "rain_1h_entity_id": "",
            "rain_today_entity_id": "",
            "rain_24h_entity_id": "",
            "outdoor_temp_entity_id": "",
            "outdoor_humidity_entity_id": "",
            "pressure_entity_id": "",
            "uv_index_entity_id": "",
            "dewpoint_entity_id": "",
            "feels_like_entity_id": "",
            "solar_lux_entity_id": "",
            "solar_radiation_entity_id": "",
            "soil_moisture_entity_id": "",
            "soil_temperature_entity_id": "",
            "vpd_entity_id": "",
        },
        "weather_guard": {
            "enabled": True,
            "wind_alarm_ms": 12.0,
            "rain_alarm_mm_h": 1.5,
            "facade_rain_min_wind_ms": 6.0,
            "facade_rain_min_mm_h": 0.8,
            "facade_azimuth_deg": -1.0,
            "facade_half_fov_deg": 60.0,
            "stale_seconds": 180,
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
        "energy": {
            "enabled": True,
            "theme": "classic_flow",
            "dashboard_background_color": "#080a10",
            "show_sankey": True,
            "energy_dashboard_layout": "sunsynk",
            "pv_power_entity_id": "sensor.zcs_easas_1_activepower_pv_ext",
            "pv_power_sign": "positive",
            "home_power_entity_id": "",
            "home_power_sign": "positive",
            "grid_power_entity_id": "",
            "grid_power_sign": "positive",
            "battery_power_entity_id": "",
            "battery_power_sign": "positive",
            "battery_soc_entity_id": "",
            "inverter_voltage_entity_id": "",
            "load_frequency_entity_id": "",
            "pv_installed_kwp": 6.6,
            "pv_energy_today_entity_id": "",
            "home_energy_today_entity_id": "",
            "grid_import_today_entity_id": "",
            "grid_export_today_entity_id": "",
            "energy_time_pv_stat_ids": "",
            "energy_time_load_stat_ids": "",
            "energy_time_grid_import_stat_ids": "",
            "energy_time_grid_export_stat_ids": "",
            "energy_time_battery_charge_stat_ids": "",
            "energy_time_battery_discharge_stat_ids": "",
            "energy_time_gas_stat_ids": "",
            "sunsynk_card_config_json": "",
            "k_flow_card_config_json": "",
            "entity_signs_json": "",
            "selected_site_id": "default",
            "sites": [],
        },
    }
    if not OPTIONS_FILE.exists():
        _normalize_energy_sites_inplace(defaults["energy"])
        return defaults
    try:
        payload = json.loads(OPTIONS_FILE.read_text(encoding="utf-8"))
    except Exception:
        _normalize_energy_sites_inplace(defaults["energy"])
        return defaults
    for key in ("latitude", "longitude", "timezone", "coordinates_source_mode", "interval_minutes", "location_query", "pv_actual_entity_id", "external_temp_entity_id", "external_humidity_entity_id"):
        if key in payload:
            defaults[key] = payload[key]
    if isinstance(payload.get("mqtt"), dict):
        defaults["mqtt"].update(payload["mqtt"])
    if isinstance(payload.get("forecast_solar"), dict):
        defaults["forecast_solar"].update(payload["forecast_solar"])
    if isinstance(payload.get("weather"), dict):
        defaults["weather"].update(payload["weather"])
    if isinstance(payload.get("weather_station"), dict):
        defaults["weather_station"].update(payload["weather_station"])
    if isinstance(payload.get("weather_guard"), dict):
        defaults["weather_guard"].update(payload["weather_guard"])
    if isinstance(payload.get("air_quality"), dict):
        defaults["air_quality"].update(payload["air_quality"])
    if isinstance(payload.get("tende_map"), dict):
        defaults["tende_map"].update(payload["tende_map"])
    if isinstance(payload.get("energy"), dict):
        defaults["energy"].update(payload["energy"])
    if isinstance(payload.get("overlay"), dict):
        defaults["overlay"].update(payload["overlay"])
    # Local overrides are owned by addon UI and persist independently from HA-managed options.
    local = _load_local_options_raw()
    if isinstance(local.get("mqtt"), dict):
        defaults["mqtt"].update(local["mqtt"])
    if isinstance(local.get("forecast_solar"), dict):
        defaults["forecast_solar"].update(local["forecast_solar"])
    if isinstance(local.get("weather"), dict):
        defaults["weather"].update(local["weather"])
    if isinstance(local.get("weather_station"), dict):
        defaults["weather_station"].update(local["weather_station"])
    if isinstance(local.get("weather_guard"), dict):
        defaults["weather_guard"].update(local["weather_guard"])
    if isinstance(local.get("air_quality"), dict):
        defaults["air_quality"].update(local["air_quality"])
    if isinstance(local.get("tende_map"), dict):
        defaults["tende_map"].update(local["tende_map"])
    if isinstance(local.get("energy"), dict):
        defaults["energy"].update(local["energy"])
    if isinstance(local.get("overlay"), dict):
        defaults["overlay"].update(local["overlay"])
    defaults["interval_minutes"] = max(1, min(1440, int(defaults.get("interval_minutes", 15) or 15)))
    mode = str(defaults.get("coordinates_source_mode") or "e_tende").strip().lower()
    if mode not in {"e_tende", "ha_core", "local"}:
        mode = "e_tende"
    defaults["coordinates_source_mode"] = mode
    defaults["forecast_solar"]["declination"] = max(0, min(90, int(defaults["forecast_solar"].get("declination", 30) or 30)))
    defaults["forecast_solar"]["azimuth"] = max(-180, min(180, int(defaults["forecast_solar"].get("azimuth", 0) or 0)))
    defaults["forecast_solar"]["kwp"] = max(0.1, min(1000.0, float(defaults["forecast_solar"].get("kwp", 6.0) or 6.0)))
    defaults["weather"]["provider"] = str(defaults["weather"].get("provider") or "met").strip().lower()
    ws = defaults["weather_station"]
    ws["enabled"] = bool(ws.get("enabled", False))
    ws["provider"] = str(ws.get("provider") or "e_control").strip().lower()
    ws["stale_seconds"] = max(30, min(86400, int(ws.get("stale_seconds", 180) or 180)))
    wg = defaults["weather_guard"]
    wg["enabled"] = bool(wg.get("enabled", True))
    wg["wind_alarm_ms"] = max(0.0, min(80.0, float(wg.get("wind_alarm_ms", 12.0) or 12.0)))
    wg["rain_alarm_mm_h"] = max(0.0, min(200.0, float(wg.get("rain_alarm_mm_h", 1.5) or 1.5)))
    wg["facade_rain_min_wind_ms"] = max(0.0, min(80.0, float(wg.get("facade_rain_min_wind_ms", 6.0) or 6.0)))
    wg["facade_rain_min_mm_h"] = max(0.0, min(200.0, float(wg.get("facade_rain_min_mm_h", 0.8) or 0.8)))
    try:
        facade_az = wg.get("facade_azimuth_deg")
        facade_value = None if facade_az in (None, "") else float(facade_az)
        wg["facade_azimuth_deg"] = None if facade_value is None or facade_value < 0 else facade_value % 360.0
    except Exception:
        wg["facade_azimuth_deg"] = None
    wg["facade_half_fov_deg"] = max(0.0, min(180.0, float(wg.get("facade_half_fov_deg", 60.0) or 60.0)))
    wg["stale_seconds"] = max(30, min(86400, int(wg.get("stale_seconds", 180) or 180)))
    defaults["air_quality"]["provider"] = str(defaults["air_quality"].get("provider") or "open_meteo").strip().lower()
    defaults["tende_map"]["stale_seconds"] = max(30, min(86400, int(defaults["tende_map"].get("stale_seconds", 180) or 180)))
    defaults["overlay"]["pathRadiusM"] = max(30, min(300, int(defaults["overlay"].get("pathRadiusM", 102) or 102)))
    defaults["overlay"]["sectorRadiusM"] = max(30, min(300, int(defaults["overlay"].get("sectorRadiusM", 110) or 110)))
    defaults["overlay"]["sunRadiusM"] = max(30, min(300, int(defaults["overlay"].get("sunRadiusM", 95) or 95)))
    defaults["overlay"]["mapZoom"] = max(14, min(22, int(defaults["overlay"].get("mapZoom", 18) or 18)))
    _normalize_energy_sites_inplace(defaults["energy"])
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


ENERGY_SITE_KEYS = (
    "enabled",
    "theme",
    "dashboard_background_color",
    "show_sankey",
    "energy_dashboard_layout",
    "pv_power_entity_id",
    "pv_power_sign",
    "home_power_entity_id",
    "home_power_sign",
    "grid_power_entity_id",
    "grid_power_sign",
    "battery_power_entity_id",
    "battery_power_sign",
    "battery_soc_entity_id",
    "inverter_voltage_entity_id",
    "load_frequency_entity_id",
    "pv_installed_kwp",
    "pv_energy_today_entity_id",
    "home_energy_today_entity_id",
    "grid_import_today_entity_id",
    "grid_export_today_entity_id",
    "energy_time_pv_stat_ids",
    "energy_time_load_stat_ids",
    "energy_time_grid_import_stat_ids",
    "energy_time_grid_export_stat_ids",
    "energy_time_battery_charge_stat_ids",
    "energy_time_battery_discharge_stat_ids",
    "energy_time_gas_stat_ids",
    "sunsynk_card_config_json",
    "k_flow_card_config_json",
    "entity_signs_json",
    "sankey_extra_loads",
)


def _energy_site_slug(value: Any, fallback: str = "default") -> str:
    raw = str(value or "").strip().lower()
    slug = re.sub(r"[^a-z0-9_-]+", "-", raw).strip("-_")
    return slug or fallback


def _energy_site_from_flat(e_cfg: dict[str, Any], site_id: str = "default", name: str = "Impianto 1") -> dict[str, Any]:
    site = {"id": site_id, "name": name}
    for key in ENERGY_SITE_KEYS:
        if key in e_cfg:
            site[key] = e_cfg.get(key)
    return site


def _normalize_energy_sites_inplace(e_cfg: dict[str, Any]) -> list[dict[str, Any]]:
    raw_sites = e_cfg.get("sites")
    sites_in = raw_sites if isinstance(raw_sites, list) else []
    fallback = _energy_site_from_flat(e_cfg)
    sites: list[dict[str, Any]] = []
    used: set[str] = set()
    for idx, raw in enumerate(sites_in):
        if not isinstance(raw, dict):
            continue
        # Once multi-site is enabled, each site must be isolated. Do not
        # inherit entity mappings from the selected/top-level site, otherwise
        # dashboards can leak PV/load/grid values into each other.
        base = {
            "enabled": raw.get("enabled", e_cfg.get("enabled", True)),
            "theme": raw.get("theme", e_cfg.get("theme", "classic_flow")),
            "dashboard_background_color": raw.get("dashboard_background_color", e_cfg.get("dashboard_background_color", "#080a10")),
            "show_sankey": raw.get("show_sankey", e_cfg.get("show_sankey", True)),
        }
        base.update(raw)
        sid = _energy_site_slug(base.get("id") or base.get("name"), f"impianto-{idx + 1}")
        if sid in used:
            sid = f"{sid}-{idx + 1}"
        used.add(sid)
        base["id"] = sid
        base["name"] = str(base.get("name") or sid).strip() or sid
        sites.append(base)
    if not sites:
        fallback["id"] = _energy_site_slug(e_cfg.get("selected_site_id") or fallback.get("id"), "default")
        fallback["name"] = str(e_cfg.get("site_name") or fallback.get("name") or "Impianto 1").strip() or "Impianto 1"
        sites.append(fallback)
    selected_id = _energy_site_slug(e_cfg.get("selected_site_id") or sites[0].get("id"), str(sites[0].get("id") or "default"))
    if not any(str(s.get("id")) == selected_id for s in sites):
        selected_id = str(sites[0].get("id") or "default")
    selected = next((s for s in sites if str(s.get("id")) == selected_id), sites[0])
    e_cfg["selected_site_id"] = selected_id
    e_cfg["sites"] = sites
    for key in ENERGY_SITE_KEYS:
        if key in selected:
            e_cfg[key] = selected.get(key)
    return sites


def _coerce_float(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except Exception:
        try:
            return float(str(v).strip().replace(",", "."))
        except Exception:
            return None


def _extract_geo_from_payload(payload: dict[str, Any]) -> tuple[float | None, float | None, str | None]:
    lat = payload.get("latitude")
    lon = payload.get("longitude")
    tz = payload.get("timezone")
    if lat is None:
        lat = payload.get("lat")
    if lon is None:
        lon = payload.get("lon")
    if tz is None:
        tz = payload.get("tz")
    coords = payload.get("coordinates")
    if isinstance(coords, dict):
        if lat is None:
            lat = coords.get("latitude", coords.get("lat"))
        if lon is None:
            lon = coords.get("longitude", coords.get("lon"))
        if tz is None:
            tz = coords.get("timezone", coords.get("tz"))
    lat_f = _coerce_float(lat)
    lon_f = _coerce_float(lon)
    tz_s = str(tz).strip() if tz is not None and str(tz).strip() else None
    return lat_f, lon_f, tz_s


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
        az_start = None
        az_end = None
        try:
            if item.get("azimuth_start_deg") is not None:
                az_start = float(item.get("azimuth_start_deg"))
            if item.get("azimuth_end_deg") is not None:
                az_end = float(item.get("azimuth_end_deg"))
        except Exception:
            az_start = az_start if isinstance(az_start, float) else None
            az_end = az_end if isinstance(az_end, float) else None
        alt_min = item.get("altitude_min_deg")
        alt_max = item.get("altitude_max_deg")
        shades_out.append(
            {
                "id": shade_id,
                "name": str(item.get("name") or shade_id),
                "cover_entity": (str(item.get("cover_entity")).strip() if item.get("cover_entity") else None),
                "enabled": bool(item.get("enabled", True)),
                "active": bool(item.get("active", False)),
                "azimuth_start_deg": (az_start % 360.0) if isinstance(az_start, float) else None,
                "azimuth_end_deg": (az_end % 360.0) if isinstance(az_end, float) else None,
                "altitude_min_deg": float(alt_min) if alt_min is not None else None,
                "altitude_max_deg": float(alt_max) if alt_max is not None else None,
                "settings": item.get("settings") if isinstance(item.get("settings"), dict) else {},
                "sensors": item.get("sensors") if isinstance(item.get("sensors"), dict) else {},
                "priority": int(item.get("priority")) if item.get("priority") is not None else None,
                "color": (str(item.get("color")).strip() if item.get("color") else None),
            }
        )
    if not shades_out:
        return None
    out = {
        "updated_at": str(payload.get("updated_at") or datetime.utcnow().isoformat()),
        "source": str(payload.get("source") or "e-tendeintelligenti"),
        "shades": shades_out,
    }
    lat, lon, tz = _extract_geo_from_payload(payload)
    if lat is not None and lon is not None:
        out["latitude"] = lat
        out["longitude"] = lon
    if tz is not None:
        out["timezone"] = tz
    return out


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
        "wind_gust_ms": instant.get("wind_speed_of_gust"),
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
    vars_hourly = (
        "temperature_2m,relative_humidity_2m,dew_point_2m,pressure_msl,cloud_cover,"
        "precipitation_probability,precipitation,rain,wind_speed_10m,wind_gusts_10m,"
        "wind_direction_10m,uv_index,weather_code,et0_fao_evapotranspiration,"
        "soil_temperature_0cm,soil_moisture_0_to_1cm"
    )
    vars_current = (
        "temperature_2m,relative_humidity_2m,dew_point_2m,pressure_msl,cloud_cover,"
        "precipitation,wind_speed_10m,wind_gusts_10m,wind_direction_10m,uv_index,weather_code"
    )
    vars_daily = (
        "precipitation_sum,rain_sum,precipitation_probability_max,"
        "et0_fao_evapotranspiration_sum,temperature_2m_max,temperature_2m_min"
    )
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&current={vars_current}&hourly={vars_hourly}&daily={vars_daily}&timezone=auto&forecast_days=3"
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
        "dew_point_c": cur.get("dew_point_2m"),
        "wind_speed_ms": (float(cur.get("wind_speed_10m")) / 3.6) if cur.get("wind_speed_10m") is not None else None,
        "wind_gust_ms": (float(cur.get("wind_gusts_10m")) / 3.6) if cur.get("wind_gusts_10m") is not None else None,
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


def _to_float_or_none(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        if isinstance(value, (int, float)):
            return float(value)
        s = str(value).strip()
        if not s:
            return None
        # Accept common HA string formats like "1,23", "231.5 V", "-42W".
        s_norm = s.replace(",", ".")
        try:
            return float(s_norm)
        except Exception:
            import re

            m = re.search(r"[-+]?\d+(?:\.\d+)?", s_norm)
            if not m:
                return None
            return float(m.group(0))
    except Exception:
        return None


def _angular_diff_deg(a: float, b: float) -> float:
    return abs((float(a) - float(b) + 180.0) % 360.0 - 180.0)


def _parse_ha_ts(value: Any) -> float | None:
    try:
        if not value:
            return None
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def _normalize_wind_to_ms(value: Any, unit: Any) -> float | None:
    v = _to_float_or_none(value)
    if v is None:
        return None
    u = str(unit or "").strip().lower()
    if u in {"m/s", "mps", "meter/s", "meters/s", "metri/s"}:
        return v
    if u in {"km/h", "kmh", "kph"}:
        return v / 3.6
    if u in {"mph", "mi/h"}:
        return v * 0.44704
    if u in {"kn", "kt", "kts", "knot", "knots"}:
        return v * 0.514444
    return v


def _normalize_rain_rate_to_mm_h(value: Any, unit: Any) -> float | None:
    v = _to_float_or_none(value)
    if v is None:
        return None
    u = str(unit or "").strip().lower()
    if u in {"in/h", "inch/h", "inches/h"}:
        return v * 25.4
    return v


def _normalize_rain_to_mm(value: Any, unit: Any) -> float | None:
    v = _to_float_or_none(value)
    if v is None:
        return None
    u = str(unit or "").strip().lower()
    if u in {"in", "inch", "inches"}:
        return v * 25.4
    return v


def _normalize_pressure_to_hpa(value: Any, unit: Any) -> float | None:
    v = _to_float_or_none(value)
    if v is None:
        return None
    u = str(unit or "").strip().lower()
    if u in {"pa", "pascal", "pascals"}:
        return v / 100.0
    if u in {"kpa"}:
        return v * 10.0
    if u in {"inhg", "in hg", "in_hg"}:
        return v * 33.8638866667
    if u in {"mmhg", "mm hg"}:
        return v * 1.3332236842
    return v


def _normalize_power_to_w(value: Any, unit: Any) -> float | None:
    v = _to_float_or_none(value)
    if v is None:
        return None
    u = str(unit or "").strip().lower()
    if u in {"w", "watt", "watts"}:
        return v
    if u in {"kw", "kilowatt", "kilowatts"}:
        return v * 1000.0
    if u in {"mw"}:
        return v * 1000000.0
    return v


def _normalize_energy_to_kwh(value: Any, unit: Any) -> float | None:
    v = _to_float_or_none(value)
    if v is None:
        return None
    u = str(unit or "").strip().lower()
    if u in {"kwh"}:
        return v
    if u in {"wh"}:
        return v / 1000.0
    if u in {"mwh"}:
        return v * 1000.0
    return v


def _parse_energy_card_entities(e_cfg: dict[str, Any]) -> dict[str, str]:
    entities: dict[str, str] = {}
    for raw_key in ("sunsynk_card_config_json", "k_flow_card_config_json"):
        try:
            parsed = json.loads(str(e_cfg.get(raw_key) or "").strip() or "{}")
        except Exception:
            parsed = {}
        if not isinstance(parsed, dict):
            continue

        def _walk(value: Any, prefix: str = "") -> None:
            if isinstance(value, dict):
                for k, v in value.items():
                    _walk(v, str(k or prefix))
                return
            if isinstance(value, list):
                for i, item in enumerate(value):
                    _walk(item, f"{prefix}_{i}" if prefix else str(i))
                return
            ent = str(value or "").strip()
            if prefix and re.match(r"^[a-z0-9_]+\.[a-z0-9_]+$", ent, re.I):
                entities.setdefault(prefix, ent)

        _walk(parsed)
        if isinstance(parsed.get("entities"), dict):
            for k, v in parsed["entities"].items():
                ent = str(v or "").strip()
                if re.match(r"^[a-z0-9_]+\.[a-z0-9_]+$", ent, re.I):
                    entities.setdefault(str(k), ent)
    return entities


def _energy_site_config(cfg: dict[str, Any], site_id: str | None = None) -> dict[str, Any]:
    e_cfg = dict(cfg.get("energy") or {})
    sites = _normalize_energy_sites_inplace(e_cfg)
    if not sites:
        return e_cfg
    wanted = str(site_id or e_cfg.get("selected_site_id") or sites[0].get("site_id") or sites[0].get("id") or "").strip().lower()

    def _norm(value: Any) -> str:
        return re.sub(r"[^a-z0-9_-]+", "-", str(value or "").strip().lower()).strip("-")

    for site in sites:
        if _norm(site.get("site_id") or site.get("id")) == _norm(wanted) or _norm(site.get("site_name") or site.get("name")) == _norm(wanted):
            return dict(site)
    return dict(sites[0])


def _energy_history_range(period: str, date_text: str, tz_name: str) -> tuple[datetime, datetime, str]:
    tz = pytz.timezone(tz_name or "Europe/Rome")
    now = datetime.now(tz)
    period_norm = str(period or "day").strip().lower()
    if period_norm not in {"day", "month", "year"}:
        period_norm = "day"
    try:
        if period_norm == "year":
            year = int(date_text[:4]) if date_text else now.year
            start = tz.localize(datetime(year, 1, 1, 0, 0, 0))
            end = tz.localize(datetime(year + 1, 1, 1, 0, 0, 0))
        elif period_norm == "month":
            if date_text and len(date_text) >= 7:
                year, month = [int(x) for x in date_text[:7].split("-")]
            else:
                year, month = now.year, now.month
            start = tz.localize(datetime(year, month, 1, 0, 0, 0))
            end = tz.localize(datetime(year + (month // 12), (month % 12) + 1, 1, 0, 0, 0))
        else:
            if date_text:
                year, month, day = [int(x) for x in date_text[:10].split("-")]
            else:
                year, month, day = now.year, now.month, now.day
            start = tz.localize(datetime(year, month, day, 0, 0, 0))
            end = start + timedelta(days=1)
    except Exception:
        start = tz.localize(datetime(now.year, now.month, now.day, 0, 0, 0))
        end = start + timedelta(days=1)
        period_norm = "day"
    return start, end, period_norm


def _fetch_ha_history_points(entity_id: str, start: datetime, end: datetime) -> tuple[list[dict[str, Any]], str | None]:
    ent = str(entity_id or "").strip()
    if not ent:
        return [], None
    token = _get_supervisor_token()
    if not token:
        return [], "missing_supervisor_token"
    query = urlencode({"filter_entity_id": ent, "end_time": end.isoformat(), "no_attributes": ""})
    url = f"http://supervisor/core/api/history/period/{quote(start.isoformat(), safe='')}?{query}"
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return [], str(exc)
    rows = payload[0] if isinstance(payload, list) and payload and isinstance(payload[0], list) else []
    points: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        value = _to_float_or_none(row.get("state"))
        ts_raw = row.get("last_updated") or row.get("last_changed")
        if value is None or not ts_raw:
            continue
        try:
            ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
        except Exception:
            continue
        points.append({"ts": ts, "value": value})
    points.sort(key=lambda x: x["ts"])
    return points, None


async def _ha_ws_call(message: dict[str, Any], timeout_seconds: float = 30.0) -> dict[str, Any]:
    token = _get_supervisor_token()
    if not token:
        raise RuntimeError("missing_supervisor_token")
    try:
        import websockets  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"missing_websockets_dependency: {exc}") from exc

    msg = dict(message)
    msg["id"] = int(msg.get("id") or 1)
    async with websockets.connect("ws://supervisor/core/websocket", open_timeout=timeout_seconds) as ws:
        auth_msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=timeout_seconds))
        if auth_msg.get("type") != "auth_required":
            raise RuntimeError(f"unexpected_ws_auth_message:{auth_msg.get('type')}")
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        auth_ok = json.loads(await asyncio.wait_for(ws.recv(), timeout=timeout_seconds))
        if auth_ok.get("type") != "auth_ok":
            raise RuntimeError(str(auth_ok.get("message") or auth_ok.get("type") or "websocket_auth_failed"))
        await ws.send(json.dumps(msg))
        while True:
            res = json.loads(await asyncio.wait_for(ws.recv(), timeout=timeout_seconds))
            if res.get("id") != msg["id"]:
                continue
            if not res.get("success", False):
                err = res.get("error") if isinstance(res.get("error"), dict) else {}
                raise RuntimeError(str(err.get("message") or err.get("code") or "websocket_call_failed"))
            return res.get("result") if isinstance(res.get("result"), dict) else {"result": res.get("result")}


async def _fetch_ha_energy_prefs() -> dict[str, Any]:
    return await _ha_ws_call({"id": 1, "type": "energy/get_prefs"})


async def _fetch_ha_statistics(
    statistic_ids: list[str],
    start: datetime,
    end: datetime,
    period: str,
) -> dict[str, list[dict[str, Any]]]:
    ids = sorted({str(x or "").strip() for x in statistic_ids if str(x or "").strip()})
    if not ids:
        return {}
    res = await _ha_ws_call(
        {
            "id": 2,
            "type": "recorder/statistics_during_period",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "statistic_ids": ids,
            "period": period,
            "types": ["change"],
            "units": {"energy": "kWh"},
        }
    )
    return {str(k): v for k, v in res.items() if isinstance(v, list)}


def _energy_pref_stat_ids(prefs: dict[str, Any], e_cfg: dict[str, Any], card_entities: dict[str, str]) -> dict[str, list[str]]:
    sources: dict[str, list[str]] = {
        "pv": [],
        "load": [],
        "grid_import": [],
        "grid_export": [],
        "battery_charge": [],
        "battery_discharge": [],
        "gas": [],
    }

    def _add(key: str, value: Any) -> None:
        ent = str(value or "").strip()
        if ent and ent not in sources[key]:
            sources[key].append(ent)

    for src in prefs.get("energy_sources") or []:
        if not isinstance(src, dict):
            continue
        typ = str(src.get("type") or "").strip().lower()
        if typ == "solar":
            _add("pv", src.get("stat_energy_from"))
        elif typ == "grid":
            _add("grid_import", src.get("stat_energy_from"))
            _add("grid_export", src.get("stat_energy_to"))
        elif typ == "battery":
            _add("battery_discharge", src.get("stat_energy_from"))
            _add("battery_charge", src.get("stat_energy_to"))
        elif typ == "gas":
            _add("gas", src.get("stat_energy_from"))

    for dev in prefs.get("device_consumption") or []:
        if not isinstance(dev, dict):
            continue
        _add("load", dev.get("stat_consumption"))

    # Fallbacks keep custom/non-HA-Energy setups usable, but HA Energy prefs win.
    if not sources["pv"]:
        _add("pv", e_cfg.get("pv_energy_today_entity_id") or card_entities.get("day_pv_energy_108"))
    if not sources["load"]:
        _add("load", e_cfg.get("home_energy_today_entity_id") or card_entities.get("day_load_energy_84"))
    if not sources["grid_import"]:
        _add("grid_import", e_cfg.get("grid_import_today_entity_id") or card_entities.get("day_grid_import_76"))
    if not sources["grid_export"]:
        _add("grid_export", e_cfg.get("grid_export_today_entity_id") or card_entities.get("day_grid_export_77"))
    if not sources["battery_charge"]:
        _add("battery_charge", card_entities.get("day_battery_charge_70"))
    if not sources["battery_discharge"]:
        _add("battery_discharge", card_entities.get("day_battery_discharge_71"))
    return sources


def _energy_site_stat_ids(e_cfg: dict[str, Any], card_entities: dict[str, str]) -> dict[str, list[str]]:
    sources: dict[str, list[str]] = {
        "pv": [],
        "load": [],
        "grid_import": [],
        "grid_export": [],
        "battery_charge": [],
        "battery_discharge": [],
        "gas": [],
    }

    def _add(key: str, value: Any) -> None:
        ent = str(value or "").strip()
        if ent and ent not in sources[key]:
            sources[key].append(ent)

    _add("pv", e_cfg.get("pv_energy_today_entity_id") or card_entities.get("day_pv_energy_108"))
    _add("load", e_cfg.get("home_energy_today_entity_id") or card_entities.get("day_load_energy_84"))
    _add("grid_import", e_cfg.get("grid_import_today_entity_id") or card_entities.get("day_grid_import_76"))
    _add("grid_export", e_cfg.get("grid_export_today_entity_id") or card_entities.get("day_grid_export_77"))
    _add("battery_charge", card_entities.get("day_battery_charge_70"))
    _add("battery_discharge", card_entities.get("day_battery_discharge_71"))
    return sources


def _split_stat_ids(value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    parts = re.split(r"[\s,;]+", text)
    out: list[str] = []
    for part in parts:
        sid = part.strip()
        if sid and sid not in out:
            out.append(sid)
    return out


def _energy_time_manual_stat_ids(e_cfg: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "pv": _split_stat_ids(e_cfg.get("energy_time_pv_stat_ids")),
        "load": _split_stat_ids(e_cfg.get("energy_time_load_stat_ids")),
        "grid_import": _split_stat_ids(e_cfg.get("energy_time_grid_import_stat_ids")),
        "grid_export": _split_stat_ids(e_cfg.get("energy_time_grid_export_stat_ids")),
        "battery_charge": _split_stat_ids(e_cfg.get("energy_time_battery_charge_stat_ids")),
        "battery_discharge": _split_stat_ids(e_cfg.get("energy_time_battery_discharge_stat_ids")),
        "gas": _split_stat_ids(e_cfg.get("energy_time_gas_stat_ids")),
    }


def _empty_energy_sources() -> dict[str, list[str]]:
    return {
        "pv": [],
        "load": [],
        "grid_import": [],
        "grid_export": [],
        "battery_charge": [],
        "battery_discharge": [],
        "gas": [],
    }


def _site_match_tokens(e_cfg: dict[str, Any]) -> list[str]:
    raw = [
        e_cfg.get("site_id"),
        e_cfg.get("id"),
        e_cfg.get("site_name"),
        e_cfg.get("name"),
    ]
    tokens: list[str] = []
    for value in raw:
        text = str(value or "").strip().lower()
        if len(text) >= 3 and text not in tokens:
            tokens.append(text)
        compact = re.sub(r"[^a-z0-9]+", "", text)
        if len(compact) >= 3 and compact not in tokens:
            tokens.append(compact)
    return tokens


def _entity_matches_site(entity_id: str, tokens: list[str]) -> bool:
    ent = str(entity_id or "").strip()
    if not ent or not tokens:
        return False
    info = _fetch_ha_entity_state(ent)
    friendly = str((info or {}).get("friendly_name") or "").lower()
    haystack = f"{ent.lower()} {friendly} {re.sub(r'[^a-z0-9]+', '', ent.lower())} {re.sub(r'[^a-z0-9]+', '', friendly)}"
    return any(token in haystack for token in tokens)


def _filter_energy_sources_by_site(sources: dict[str, list[str]], e_cfg: dict[str, Any]) -> dict[str, list[str]]:
    tokens = _site_match_tokens(e_cfg)
    if not tokens:
        return _empty_energy_sources()
    out = _empty_energy_sources()
    for key, ids in sources.items():
        if key not in out:
            continue
        for sid in ids:
            if _entity_matches_site(sid, tokens):
                out[key].append(sid)
    return out


def _stat_unit_to_kwh_factor(unit: Any) -> float:
    u = str(unit or "").strip().lower()
    if u == "wh":
        return 0.001
    if u == "mwh":
        return 1000.0
    return 1.0


def _stat_unit_factors(statistic_ids: list[str]) -> dict[str, float]:
    factors: dict[str, float] = {}
    for sid in statistic_ids:
        info = _fetch_ha_entity_state(sid)
        factors[sid] = _stat_unit_to_kwh_factor((info or {}).get("unit"))
    return factors


def _stat_change_values(rows: list[dict[str, Any]], count: int, factor: float = 1.0) -> list[float]:
    vals = [0.0] * count
    for idx, row in enumerate(rows[:count]):
        if not isinstance(row, dict):
            continue
        vals[idx] = abs(float(_to_float_or_none(row.get("change")) or 0.0)) * factor
    return vals


def _combine_stat_ids(stats: dict[str, list[dict[str, Any]]], ids: list[str], count: int, factors: dict[str, float]) -> list[float]:
    out = [0.0] * count
    for sid in ids:
        vals = _stat_change_values(stats.get(sid) or [], count, factors.get(sid, 1.0))
        out = [a + b for a, b in zip(out, vals)]
    return out


def _bucket_energy_day(points: list[dict[str, Any]], start: datetime) -> list[float]:
    out: list[float] = []
    values = [(p["ts"], float(p["value"])) for p in points]
    for hour in range(24):
        b0 = start + timedelta(hours=hour)
        b1 = b0 + timedelta(hours=1)
        before = [v for ts, v in values if ts <= b0]
        inside = [v for ts, v in values if b0 < ts <= b1]
        if not inside:
            out.append(0.0)
            continue
        start_val = before[-1] if before else min(inside)
        end_val = inside[-1]
        out.append(max(0.0, end_val - start_val) if end_val >= start_val else max(0.0, end_val))
    return out


def _bucket_energy_daily_max(points: list[dict[str, Any]], start: datetime, end: datetime) -> dict[str, float]:
    days: dict[str, float] = {}
    cur = start
    while cur < end:
        days[cur.date().isoformat()] = 0.0
        cur += timedelta(days=1)
    for p in points:
        local_ts = p["ts"].astimezone(start.tzinfo)
        key = local_ts.date().isoformat()
        if key in days:
            days[key] = max(days[key], float(p["value"]))
    return days


async def _build_energy_history_snapshot(cfg: dict[str, Any], site_id: str | None, period: str, date_text: str) -> dict[str, Any]:
    e_cfg = _energy_site_config(cfg, site_id)
    tz_name = str(cfg.get("timezone") or e_cfg.get("timezone") or "Europe/Rome")
    start, end, period_norm = _energy_history_range(period, date_text, tz_name)
    card_entities = _parse_energy_card_entities(e_cfg)
    errors: dict[str, str] = {}
    if period_norm == "day":
        labels = [f"{h:02d}:00" for h in range(24)]
        stat_period = "hour"
        count = 24
    elif period_norm == "month":
        day_keys = []
        cur = start
        while cur < end:
            day_keys.append(cur.date().isoformat())
            cur += timedelta(days=1)
        labels = [k[-2:] for k in day_keys]
        stat_period = "day"
        count = len(labels)
    else:
        labels = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]
        stat_period = "month"
        count = 12

    prefs: dict[str, Any] = {}
    site_requested = bool(str(site_id or "").strip())
    manual_sources = _energy_time_manual_stat_ids(e_cfg)
    has_manual_sources = any(bool(ids) for ids in manual_sources.values())
    if site_requested:
        if has_manual_sources:
            fallback_sources = _energy_site_stat_ids(e_cfg, card_entities)
            sources = _empty_energy_sources()
            for key in sources:
                sources[key] = manual_sources.get(key) or fallback_sources.get(key) or []
        else:
            try:
                prefs = await _fetch_ha_energy_prefs()
            except Exception as exc:
                errors["energy_prefs"] = str(exc)
            ha_site_sources = _filter_energy_sources_by_site(_energy_pref_stat_ids(prefs if isinstance(prefs, dict) else {}, e_cfg, card_entities), e_cfg)
            site_sources = _energy_site_stat_ids(e_cfg, card_entities)
            sources = _empty_energy_sources()
            for key in sources:
                sources[key] = ha_site_sources.get(key) or site_sources.get(key) or []
    else:
        if has_manual_sources:
            sources = manual_sources
        else:
            try:
                prefs = await _fetch_ha_energy_prefs()
            except Exception as exc:
                errors["energy_prefs"] = str(exc)
            sources = _energy_pref_stat_ids(prefs if isinstance(prefs, dict) else {}, e_cfg, card_entities)

    all_stat_ids = sorted({sid for ids in sources.values() for sid in ids})
    stats: dict[str, list[dict[str, Any]]] = {}
    factors: dict[str, float] = {}
    if all_stat_ids:
        factors = _stat_unit_factors(all_stat_ids)
        try:
            stats = await _fetch_ha_statistics(all_stat_ids, start, end, stat_period)
        except Exception as exc:
            errors["statistics"] = str(exc)

    series = {
        "pv": _combine_stat_ids(stats, sources["pv"], count, factors),
        "load": _combine_stat_ids(stats, sources["load"], count, factors),
        "grid_import": _combine_stat_ids(stats, sources["grid_import"], count, factors),
        "grid_export": _combine_stat_ids(stats, sources["grid_export"], count, factors),
        "battery_charge": _combine_stat_ids(stats, sources["battery_charge"], count, factors),
        "battery_discharge": _combine_stat_ids(stats, sources["battery_discharge"], count, factors),
        "gas": _combine_stat_ids(stats, sources["gas"], count, factors),
    }

    if not any(v > 0 for v in series["load"]):
        series["load"] = [
            max(0.0, pv + grid_in + batt_out - grid_out - batt_in)
            for pv, grid_in, batt_out, grid_out, batt_in in zip(
                series["pv"],
                series["grid_import"],
                series["battery_discharge"],
                series["grid_export"],
                series["battery_charge"],
            )
        ]

    totals = {key: round(sum(float(v or 0.0) for v in vals), 3) for key, vals in series.items()}
    return {
        "ok": True,
        "site_id": e_cfg.get("site_id") or e_cfg.get("id") or site_id or "default",
        "site_name": e_cfg.get("site_name") or e_cfg.get("name") or e_cfg.get("site_id") or "Energy",
        "period": period_norm,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "labels": labels,
        "series": series,
        "totals": totals,
        "sources": sources,
        "source_units_factor_to_kwh": factors,
        "source_mode": "manual_energy_time_statistics" if has_manual_sources else ("ha_energy_site_filtered" if site_requested and prefs else ("site_config_statistics" if site_requested else ("ha_energy_statistics" if prefs else "configured_statistics"))),
        "errors": errors,
    }


def _build_energy_site_snapshot(e_cfg: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "ok": False,
        "enabled": bool(e_cfg.get("enabled", True)),
        "show_sankey": bool(e_cfg.get("show_sankey", True)),
        "energy_dashboard_layout": "k_flow" if str(e_cfg.get("energy_dashboard_layout") or "sunsynk").strip().lower() == "k_flow" else "sunsynk",
        "entities": {},
        "card_entities": {},
        "normalized": {
            "pv_power_w": None,
            "home_power_w": None,
            "grid_power_w": None,
            "battery_power_w": None,
            "battery_soc_pct": None,
            "pv_installed_kwp": _to_float_or_none(e_cfg.get("pv_installed_kwp")),
            "pv_energy_today_kwh": None,
            "home_energy_today_kwh": None,
            "grid_import_today_kwh": None,
            "grid_export_today_kwh": None,
            "inverter_voltage_v": None,
            "load_frequency_hz": None,
        },
        "theme": str(e_cfg.get("theme") or "classic_flow"),
        "dashboard_background_color": str(e_cfg.get("dashboard_background_color") or "#080a10"),
        "errors": {},
    }
    if not out["enabled"]:
        return out

    entity_keys = (
        "pv_power_entity_id",
        "home_power_entity_id",
        "grid_power_entity_id",
        "battery_power_entity_id",
        "battery_soc_entity_id",
        "inverter_voltage_entity_id",
        "load_frequency_entity_id",
        "pv_energy_today_entity_id",
        "home_energy_today_entity_id",
        "grid_import_today_entity_id",
        "grid_export_today_entity_id",
    )
    for key in entity_keys:
        ent = str(e_cfg.get(key) or "").strip()
        if not ent:
            out["entities"][key] = {"ok": False, "entity_id": "", "error": "empty_entity_id"}
            continue
        st = _fetch_ha_entity_state(ent)
        if not st or not st.get("ok"):
            out["entities"][key] = st or {"ok": False, "entity_id": ent, "error": "read_failed"}
            out["errors"][key] = (st or {}).get("error", "read_failed")
            continue
        out["entities"][key] = st

    def _val(k: str) -> tuple[Any, Any]:
        st = out["entities"].get(k) or {}
        return st.get("value"), st.get("unit")

    def _is_missing(v: Any) -> bool:
        return v is None

    card_entities: dict[str, Any] = {}
    try:
        raw_cfg = str(e_cfg.get("sunsynk_card_config_json") or "").strip()
        if raw_cfg:
            parsed = json.loads(raw_cfg)
            if isinstance(parsed, dict) and isinstance(parsed.get("entities"), dict):
                card_entities = parsed.get("entities") or {}
    except Exception:
        card_entities = {}

    def _collect_config_entity_ids(value: Any, prefix: str = "") -> dict[str, str]:
        found: dict[str, str] = {}
        if isinstance(value, dict):
            for k, v in value.items():
                key = str(k or "").strip()
                child_prefix = key or prefix
                for ck, ent in _collect_config_entity_ids(v, child_prefix).items():
                    out_key = ck
                    n = 2
                    while out_key in found and found[out_key] != ent:
                        out_key = f"{ck}_{n}"
                        n += 1
                    found[out_key] = ent
        elif isinstance(value, list):
            for i, item in enumerate(value):
                for ck, ent in _collect_config_entity_ids(item, f"{prefix}_{i}" if prefix else str(i)).items():
                    found[ck] = ent
        else:
            ent = str(value or "").strip()
            if re.match(r"^[a-z0-9_]+\.[a-z0-9_]+$", ent, re.I):
                found[prefix or ent.replace(".", "_")] = ent
        return found

    try:
        raw_kflow_cfg = str(e_cfg.get("k_flow_card_config_json") or "").strip()
        if raw_kflow_cfg:
            parsed_kflow = json.loads(raw_kflow_cfg)
            if isinstance(parsed_kflow, dict):
                for card_key, ent in _collect_config_entity_ids(parsed_kflow).items():
                    card_entities.setdefault(card_key, ent)
    except Exception:
        pass

    def _card_state(card_key: str) -> dict[str, Any] | None:
        ent = str(card_entities.get(card_key) or "").strip()
        if not ent:
            return None
        st = _fetch_ha_entity_state(ent)
        if not st or not st.get("ok"):
            return None
        out["card_entities"][card_key] = {
            "entity_id": ent,
            "value": st.get("value"),
            "unit": st.get("unit"),
            "state": st.get("state"),
            "attributes": st.get("attributes") if isinstance(st.get("attributes"), dict) else {},
        }
        return st

    def _card_power_w(card_key: str) -> float | None:
        st = _card_state(card_key)
        if not st:
            return None
        return _normalize_power_to_w(st.get("value"), st.get("unit"))

    def _card_energy_kwh(card_key: str) -> float | None:
        st = _card_state(card_key)
        if not st:
            return None
        return _normalize_energy_to_kwh(st.get("value"), st.get("unit"))

    # Preload all card entity states for diagnostics and frontend fallback rendering.
    for ck in list(card_entities.keys()):
        try:
            _card_state(str(ck))
        except Exception:
            continue

    out["normalized"]["pv_power_w"] = _normalize_power_to_w(*_val("pv_power_entity_id"))
    out["normalized"]["home_power_w"] = _normalize_power_to_w(*_val("home_power_entity_id"))
    out["normalized"]["grid_power_w"] = _normalize_power_to_w(*_val("grid_power_entity_id"))
    out["normalized"]["battery_power_w"] = _normalize_power_to_w(*_val("battery_power_entity_id"))
    out["normalized"]["battery_soc_pct"] = _to_float_or_none((out["entities"].get("battery_soc_entity_id") or {}).get("value"))
    out["normalized"]["pv_energy_today_kwh"] = _normalize_energy_to_kwh(*_val("pv_energy_today_entity_id"))
    out["normalized"]["home_energy_today_kwh"] = _normalize_energy_to_kwh(*_val("home_energy_today_entity_id"))
    out["normalized"]["grid_import_today_kwh"] = _normalize_energy_to_kwh(*_val("grid_import_today_entity_id"))
    out["normalized"]["grid_export_today_kwh"] = _normalize_energy_to_kwh(*_val("grid_export_today_entity_id"))
    out["normalized"]["battery_charge_today_kwh"] = None
    out["normalized"]["battery_discharge_today_kwh"] = None
    out["normalized"]["inverter_voltage_v"] = _to_float_or_none((out["entities"].get("inverter_voltage_entity_id") or {}).get("value"))
    out["normalized"]["load_frequency_hz"] = _to_float_or_none((out["entities"].get("load_frequency_entity_id") or {}).get("value"))

    # PV total: prefer explicit Sunsynk pv_total when configured; otherwise use
    # the legacy base PV entity and finally sum the mapped PV strings.
    pv_total = _card_power_w("pv_total")
    if pv_total is not None:
        out["normalized"]["pv_power_w"] = pv_total
    elif _is_missing(out["normalized"]["pv_power_w"]):
        pv_values = [_card_power_w(k) for k in ("pv1_power_186", "pv2_power_187", "pv3_power_188", "pv4_power_189", "pv5_power", "pv6_power")]
        if any(v is not None for v in pv_values):
            out["normalized"]["pv_power_w"] = sum(float(v or 0.0) for v in pv_values)
    if _is_missing(out["normalized"]["home_power_w"]):
        out["normalized"]["home_power_w"] = _card_power_w("inverter_power_175")
    if _is_missing(out["normalized"]["grid_power_w"]):
        out["normalized"]["grid_power_w"] = _card_power_w("grid_power_169")
    if _is_missing(out["normalized"]["battery_power_w"]):
        out["normalized"]["battery_power_w"] = _card_power_w("battery_power_190")
    if _is_missing(out["normalized"]["battery_soc_pct"]):
        st_soc = _card_state("battery_soc_184")
        out["normalized"]["battery_soc_pct"] = _to_float_or_none((st_soc or {}).get("value"))
    if _is_missing(out["normalized"]["pv_energy_today_kwh"]):
        out["normalized"]["pv_energy_today_kwh"] = _card_energy_kwh("day_pv_energy_108")
    if _is_missing(out["normalized"]["home_energy_today_kwh"]):
        out["normalized"]["home_energy_today_kwh"] = _card_energy_kwh("day_load_energy_84")
    if _is_missing(out["normalized"]["grid_import_today_kwh"]):
        out["normalized"]["grid_import_today_kwh"] = _card_energy_kwh("day_grid_import_76")
    if _is_missing(out["normalized"]["grid_export_today_kwh"]):
        out["normalized"]["grid_export_today_kwh"] = _card_energy_kwh("day_grid_export_77")
    if _is_missing(out["normalized"]["battery_charge_today_kwh"]):
        out["normalized"]["battery_charge_today_kwh"] = _card_energy_kwh("day_battery_charge_70")
    if _is_missing(out["normalized"]["battery_discharge_today_kwh"]):
        out["normalized"]["battery_discharge_today_kwh"] = _card_energy_kwh("day_battery_discharge_71")
    if _is_missing(out["normalized"]["inverter_voltage_v"]):
        st_v = _card_state("inverter_voltage_154")
        out["normalized"]["inverter_voltage_v"] = _to_float_or_none((st_v or {}).get("value"))
    if _is_missing(out["normalized"]["load_frequency_hz"]):
        st_hz = _card_state("load_frequency_192")
        out["normalized"]["load_frequency_hz"] = _to_float_or_none((st_hz or {}).get("value"))

    out["ok"] = out["normalized"]["pv_power_w"] is not None
    return out


def _build_energy_snapshot(cfg: dict[str, Any], selected_site_id: str | None = None, include_sites: bool = True) -> dict[str, Any]:
    e_cfg = dict(cfg.get("energy") or {})
    sites = _normalize_energy_sites_inplace(e_cfg)
    selected_id = _energy_site_slug(selected_site_id or e_cfg.get("selected_site_id") or (sites[0].get("id") if sites else "default"), "default")
    selected_site = next(
        (
            s
            for s in sites
            if str(s.get("id")) == selected_id
            or _energy_site_slug(s.get("name") or s.get("site_name"), "") == selected_id
        ),
        sites[0] if sites else e_cfg,
    )
    out = _build_energy_site_snapshot(selected_site)
    out["site_id"] = str(selected_site.get("id") or selected_id or "default")
    out["site_name"] = str(selected_site.get("name") or out["site_id"])
    out["selected_site_id"] = out["site_id"]
    site_out: list[dict[str, Any]] = []
    if include_sites:
        for site in sites:
            sid = str(site.get("id") or "default")
            if sid == out["site_id"]:
                snap = dict(out)
                snap.pop("sites", None)
            else:
                snap = _build_energy_site_snapshot(site)
                snap["site_id"] = sid
                snap["site_name"] = str(site.get("name") or snap["site_id"])
            site_out.append(snap)
    else:
        site_out.append({
            "site_id": out["site_id"],
            "site_name": out["site_name"],
            "ok": out.get("ok"),
            "enabled": out.get("enabled"),
            "theme": out.get("theme"),
            "normalized": out.get("normalized"),
        })
    out["sites"] = site_out
    return out


def _weather_payload_ts(payload: dict[str, Any] | None) -> float | None:
    if not isinstance(payload, dict):
        return None
    fetched = _to_float_or_none(payload.get("_fetched_at_ts"))
    if fetched is not None:
        return fetched
    try:
        t = ((payload.get("normalized") or {}).get("time")) if isinstance(payload.get("normalized"), dict) else None
        if not t:
            return None
        dt = datetime.fromisoformat(str(t).replace("Z", "+00:00"))
        return dt.timestamp()
    except Exception:
        return None


def _build_weather_station_snapshot(cfg: dict[str, Any]) -> dict[str, Any]:
    ws_cfg = cfg.get("weather_station") or {}
    enabled = bool(ws_cfg.get("enabled", False))
    out: dict[str, Any] = {
        "ok": False,
        "enabled": enabled,
        "provider": str(ws_cfg.get("provider") or "e_control"),
        "source": "e-Control",
        "normalized": {},
        "entities": {},
        "entities_all": [],
        "error": None,
    }
    if not enabled:
        out["error"] = "disabled"
        return out

    auto_mapped = _auto_map_weather_station_entities(str(ws_cfg.get("device_id") or ""))
    out["auto_mapped_entities"] = auto_mapped
    did = str(ws_cfg.get("device_id") or "").strip()
    if did:
        all_entities = _fetch_ha_device_entities(did)
        all_states: list[dict[str, Any]] = []
        for ent in all_entities:
            st = _fetch_ha_entity_state(ent)
            if isinstance(st, dict):
                all_states.append(st)
            else:
                all_states.append({"ok": False, "entity_id": ent, "error": "read_failed"})
        out["entities_all"] = all_states

    fields = {
        "wind_speed_ms": ("wind_speed_entity_id", _normalize_wind_to_ms),
        "wind_gust_ms": ("wind_gust_entity_id", _normalize_wind_to_ms),
        "wind_from_direction_deg": ("wind_direction_entity_id", lambda v, _u: _to_float_or_none(v)),
        "rain_rate_mm_h": ("rain_rate_entity_id", _normalize_rain_rate_to_mm_h),
        "rain_1h_mm": ("rain_1h_entity_id", _normalize_rain_to_mm),
        "rain_today_mm": ("rain_today_entity_id", _normalize_rain_to_mm),
        "rain_24h_mm": ("rain_24h_entity_id", _normalize_rain_to_mm),
        "air_temperature_c": ("outdoor_temp_entity_id", lambda v, _u: _to_float_or_none(v)),
        "relative_humidity_pct": ("outdoor_humidity_entity_id", lambda v, _u: _to_float_or_none(v)),
        "air_pressure_hpa": ("pressure_entity_id", _normalize_pressure_to_hpa),
        "uv_index": ("uv_index_entity_id", lambda v, _u: _to_float_or_none(v)),
        "dew_point_c": ("dewpoint_entity_id", lambda v, _u: _to_float_or_none(v)),
        "feels_like_temperature_c": ("feels_like_entity_id", lambda v, _u: _to_float_or_none(v)),
        "solar_lux_lx": ("solar_lux_entity_id", lambda v, _u: _to_float_or_none(v)),
        "solar_radiation_w_m2": ("solar_radiation_entity_id", lambda v, _u: _to_float_or_none(v)),
        "soil_moisture_pct": ("soil_moisture_entity_id", lambda v, _u: _to_float_or_none(v)),
        "soil_temperature_c": ("soil_temperature_entity_id", lambda v, _u: _to_float_or_none(v)),
        "vapour_pressure_deficit_hpa": ("vpd_entity_id", lambda v, _u: _to_float_or_none(v)),
    }
    normalized: dict[str, Any] = {}
    timestamps: list[float] = []
    errors: dict[str, Any] = {}
    for target_key, (cfg_key, normalizer) in fields.items():
        entity_id = str(ws_cfg.get(cfg_key) or "").strip()
        if not entity_id:
            entity_id = str(auto_mapped.get(cfg_key) or "").strip()
        if not entity_id:
            continue
        st = _fetch_ha_entity_state(entity_id)
        out["entities"][cfg_key] = st
        if not isinstance(st, dict) or not st.get("ok"):
            errors[cfg_key] = (st or {}).get("error") if isinstance(st, dict) else "read_failed"
            continue
        value = normalizer(st.get("value"), st.get("unit"))
        if value is None:
            errors[cfg_key] = "non_numeric"
            continue
        normalized[target_key] = value
        ts = _parse_ha_ts(st.get("last_updated"))
        if ts is not None:
            timestamps.append(ts)

    if "wind_from_direction_deg" in normalized:
        normalized["wind_from_direction_deg"] = normalized["wind_from_direction_deg"] % 360.0
    if "rain_rate_mm_h" in normalized:
        normalized["precipitation_next_1h_mm"] = normalized["rain_rate_mm_h"]
    if "rain_1h_mm" in normalized and "precipitation_next_1h_mm" not in normalized:
        normalized["precipitation_next_1h_mm"] = normalized["rain_1h_mm"]

    stale_seconds = int(ws_cfg.get("stale_seconds", 180) or 180)
    latest_ts = max(timestamps) if timestamps else None
    age = None if latest_ts is None else time.time() - latest_ts
    stale = latest_ts is None or age > stale_seconds
    out["normalized"] = normalized
    out["stale"] = stale
    out["age_seconds"] = None if age is None else round(age, 1)
    out["errors"] = errors
    out["ok"] = bool(normalized) and not stale
    if out["ok"]:
        out["provider"] = "weather_station"
        out["_fetched_at_ts"] = latest_ts
        out["error"] = None
    else:
        out["error"] = "station_stale_or_empty" if stale else "station_fields_missing"
    return out


def _build_weather_guard(data: dict[str, Any] | None, cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    now = time.time()
    cfg = cfg or _load_options()
    wg_cfg = (cfg.get("weather_guard") or {})
    updated_at = datetime.now(pytz.timezone(str(cfg.get("timezone") or "Europe/Rome"))).isoformat()
    base = {
        "ok": False,
        "enabled": bool(wg_cfg.get("enabled", True)),
        "wind_speed_ms": 0.0,
        "wind_gust_ms": None,
        "wind_dir_deg": None,
        "rain_rate_mm_h": 0.0,
        "rain_1h_mm": None,
        "facade_rain_risk": False,
        "wind_alarm": False,
        "rain_alarm": False,
        "severe_weather_alarm": False,
        "updated_at": updated_at,
        "station": {
            "enabled": False,
            "ok": False,
            "used": False,
            "error": None,
            "age_seconds": None,
        },
    }
    if not base["enabled"]:
        base["error"] = "disabled"
        return base
    if not isinstance(data, dict):
        base["error"] = "data_not_ready"
        return base

    weather_station = data.get("weather_station") if isinstance(data.get("weather_station"), dict) else None
    base["station"] = {
        "enabled": bool((weather_station or {}).get("enabled", False)) if isinstance(weather_station, dict) else False,
        "ok": bool((weather_station or {}).get("ok", False)) if isinstance(weather_station, dict) else False,
        "used": False,
        "error": (weather_station or {}).get("error") if isinstance(weather_station, dict) else None,
        "age_seconds": (weather_station or {}).get("age_seconds") if isinstance(weather_station, dict) else None,
    }
    weather = data.get("weather") if isinstance(data.get("weather"), dict) else None
    weather_open = data.get("weather_open_meteo") if isinstance(data.get("weather_open_meteo"), dict) else None
    stale_seconds = int(wg_cfg.get("stale_seconds", 180) or 180)
    selected = None
    weather_ts = None
    candidates: list[tuple[dict[str, Any], float]] = []
    # Priority rule: use real weather station when available and fresh, otherwise use web APIs.
    if isinstance(weather_station, dict) and weather_station.get("ok"):
        station_ts = _weather_payload_ts(weather_station)
        if station_ts is not None and (now - station_ts) <= stale_seconds:
            selected = weather_station
            weather_ts = station_ts
    if selected is None:
        for candidate in (weather, weather_open):
            if not (isinstance(candidate, dict) and candidate.get("ok")):
                continue
            candidate_ts = _weather_payload_ts(candidate)
            if candidate_ts is not None:
                candidates.append((candidate, candidate_ts))
        candidates.sort(key=lambda item: item[1], reverse=True)
        for candidate, candidate_ts in candidates:
            if (now - candidate_ts) <= stale_seconds:
                selected = candidate
                weather_ts = candidate_ts
                break
        if selected is None and candidates:
            selected, weather_ts = candidates[0]
    if weather_ts is None or (now - weather_ts) > stale_seconds:
        base["error"] = "weather_stale_or_missing"
        base["stale"] = True
        base["age_seconds"] = None if weather_ts is None else round(now - weather_ts, 1)
        return base

    norm = (selected.get("normalized") if selected else None) or {}
    fallback_norms = [
        (candidate.get("normalized") if isinstance(candidate.get("normalized"), dict) else {})
        for candidate, _candidate_ts in candidates
        if candidate is not selected
    ]

    wind_speed = _to_float_or_none(norm.get("wind_speed_ms"))
    wind_gust = _to_float_or_none(norm.get("wind_gust_ms"))
    wind_dir = _to_float_or_none(norm.get("wind_from_direction_deg"))
    rain_1h = _to_float_or_none(norm.get("precipitation_next_1h_mm"))
    for fb_norm in fallback_norms:
        if wind_speed is None:
            wind_speed = _to_float_or_none(fb_norm.get("wind_speed_ms"))
        if wind_gust is None:
            wind_gust = _to_float_or_none(fb_norm.get("wind_gust_ms"))
        if wind_dir is None:
            wind_dir = _to_float_or_none(fb_norm.get("wind_from_direction_deg"))
        if rain_1h is None:
            rain_1h = _to_float_or_none(fb_norm.get("precipitation_next_1h_mm"))

    if wind_speed is None or rain_1h is None:
        base["error"] = "weather_fields_missing"
        base["stale"] = False
        return base

    rain_rate = max(0.0, rain_1h)
    wind_for_alarm = wind_gust if wind_gust is not None else wind_speed
    wind_alarm = wind_for_alarm >= float(wg_cfg.get("wind_alarm_ms", 12.0) or 12.0)
    rain_alarm = rain_rate >= float(wg_cfg.get("rain_alarm_mm_h", 1.5) or 1.5)
    facade_az = _to_float_or_none(wg_cfg.get("facade_azimuth_deg"))
    facade_half = float(wg_cfg.get("facade_half_fov_deg", 60.0) or 60.0)
    in_facade_cone = False
    if facade_az is not None and wind_dir is not None:
        in_facade_cone = _angular_diff_deg(wind_dir, facade_az) <= facade_half
    facade_rain_risk = (
        rain_rate >= float(wg_cfg.get("facade_rain_min_mm_h", 0.8) or 0.8)
        and wind_speed >= float(wg_cfg.get("facade_rain_min_wind_ms", 6.0) or 6.0)
        and in_facade_cone
    )

    base.update(
        {
            "ok": True,
            "stale": False,
            "age_seconds": round(now - weather_ts, 1),
            "source": (selected or {}).get("provider"),
            "station": {
                "enabled": bool(base["station"].get("enabled")),
                "ok": bool(base["station"].get("ok")),
                "used": (selected is weather_station),
                "error": base["station"].get("error"),
                "age_seconds": base["station"].get("age_seconds"),
            },
            "wind_speed_ms": wind_speed,
            "wind_gust_ms": wind_gust,
            "wind_dir_deg": None if wind_dir is None else wind_dir % 360.0,
            "rain_rate_mm_h": rain_rate,
            "rain_1h_mm": rain_1h,
            "facade_azimuth_deg": None if facade_az is None else facade_az % 360.0,
            "facade_half_fov_deg": facade_half,
            "facade_wind_in_cone": in_facade_cone,
            "facade_rain_risk": facade_rain_risk,
            "wind_alarm": wind_alarm,
            "rain_alarm": rain_alarm,
            "severe_weather_alarm": bool(wind_alarm or rain_alarm or facade_rain_risk),
        }
    )
    return base


def _selected_weather_for_irrigation(data: dict[str, Any], guard: dict[str, Any]) -> dict[str, Any]:
    station = data.get("weather_station") if isinstance(data.get("weather_station"), dict) else None
    if isinstance(station, dict) and station.get("ok") and ((guard.get("station") or {}).get("used")):
        return station
    weather = data.get("weather") if isinstance(data.get("weather"), dict) else None
    if isinstance(weather, dict) and weather.get("ok"):
        return weather
    weather_open = data.get("weather_open_meteo") if isinstance(data.get("weather_open_meteo"), dict) else None
    if isinstance(weather_open, dict) and weather_open.get("ok"):
        return weather_open
    return station or weather or weather_open or {}


def _weather_code_to_condition(code: Any) -> str | None:
    if code is None:
        return None
    text = str(code).strip().lower()
    if not text:
        return None
    if any(k in text for k in ("rain", "piogg", "drizzle", "shower")):
        return "rainy"
    if any(k in text for k in ("snow", "sleet")):
        return "snowy"
    if any(k in text for k in ("thunder", "storm")):
        return "stormy"
    if any(k in text for k in ("fog", "mist")):
        return "fog"
    if any(k in text for k in ("cloud", "overcast", "partly")):
        return "cloudy"
    if any(k in text for k in ("clear", "fair", "sun")):
        return "sunny"
    try:
        n = int(float(text))
    except Exception:
        return text
    if n in (0, 1):
        return "sunny"
    if n in (2, 3):
        return "cloudy"
    if 45 <= n <= 48:
        return "fog"
    if 51 <= n <= 67 or 80 <= n <= 82:
        return "rainy"
    if 71 <= n <= 77 or 85 <= n <= 86:
        return "snowy"
    if 95 <= n <= 99:
        return "stormy"
    return text


def _iso_from_unix_ts(ts: Any, timezone_name: str) -> str | None:
    value = _to_float_or_none(ts)
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(value, pytz.timezone(str(timezone_name or "Europe/Rome"))).isoformat()
    except Exception:
        return None


def _irrigation_source_label(selected: dict[str, Any], guard: dict[str, Any]) -> str | None:
    if bool(((guard.get("station") or {}).get("used"))):
        return "local_station"
    provider = str(selected.get("provider") or guard.get("source") or "").strip().lower()
    if provider:
        return "fallback_web"
    return None


def _empty_irrigation_weather_payload(cfg: dict[str, Any] | None = None, *, error: str | None = None) -> dict[str, Any]:
    timezone_name = str((cfg or {}).get("timezone") or "Europe/Rome")
    payload = {
        "temperature_c": None,
        "humidity_pct": None,
        "pressure_hpa": None,
        "dew_point_c": None,
        "wind_speed_ms": None,
        "wind_gust_ms": None,
        "wind_bearing_deg": None,
        "rain_rate_mm_h": None,
        "rain_today_mm": None,
        "rain_last_24h_mm": None,
        "precip_probability_pct": None,
        "forecast_rain_24h_mm": None,
        "solar_radiation_w_m2": None,
        "uv_index": None,
        "cloud_cover_pct": None,
        "soil_moisture_pct": None,
        "soil_temperature_c": None,
        "et0_mm_day": None,
        "weather_code": None,
        "condition": None,
        "last_update": None,
        "source": None,
        "age_seconds": None,
        "available": False,
        "is_raining": False,
        "rain_block": False,
        "wind_block": False,
        "freeze_block": False,
        "hot_day": False,
        "dry_day": False,
        "irrigation_weather_score": 0,
        "irrigation_weather_reason": error or "weather_unavailable",
        "hourly_forecast": [],
        "daily_forecast": [],
        "generated_at": datetime.now(pytz.timezone(timezone_name)).isoformat(),
        "schema": "e_sunmind_irrigation_weather.v1",
    }
    if error:
        payload["error"] = error
    return payload


def _forecast_from_open_meteo_payload(payload: dict[str, Any] | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw = (payload or {}).get("payload") if isinstance(payload, dict) else None
    hourly = (raw or {}).get("hourly") if isinstance(raw, dict) else None
    daily = (raw or {}).get("daily") if isinstance(raw, dict) else None
    if not isinstance(hourly, dict) and not isinstance(daily, dict):
        return [], []

    times = hourly.get("time") if isinstance(hourly, dict) and isinstance(hourly.get("time"), list) else []
    hourly_out: list[dict[str, Any]] = []
    for idx, ts in enumerate(times[:48]):
        def at(name: str):
            values = hourly.get(name)
            return values[idx] if isinstance(values, list) and idx < len(values) else None

        item = {
            "time": ts,
            "temperature_c": at("temperature_2m"),
            "humidity_pct": at("relative_humidity_2m"),
            "dew_point_c": at("dew_point_2m"),
            "pressure_hpa": at("pressure_msl"),
            "wind_speed_ms": (float(at("wind_speed_10m")) / 3.6) if at("wind_speed_10m") is not None else None,
            "wind_gust_ms": (float(at("wind_gusts_10m")) / 3.6) if at("wind_gusts_10m") is not None else None,
            "wind_bearing_deg": at("wind_direction_10m"),
            "rain_mm": at("precipitation"),
            "precip_probability_pct": at("precipitation_probability"),
            "uv_index": at("uv_index"),
            "cloud_cover_pct": at("cloud_cover"),
            "soil_moisture_pct": None if at("soil_moisture_0_to_1cm") is None else float(at("soil_moisture_0_to_1cm")) * 100.0,
            "soil_temperature_c": at("soil_temperature_0cm"),
            "et0_mm": at("et0_fao_evapotranspiration"),
            "weather_code": at("weather_code"),
            "condition": _weather_code_to_condition(at("weather_code")),
        }
        hourly_out.append(item)

    daily_out = []
    if isinstance(daily, dict):
        daily_times = daily.get("time") if isinstance(daily.get("time"), list) else []
        for idx, day in enumerate(daily_times[:7]):
            def daily_at(name: str):
                values = daily.get(name)
                return values[idx] if isinstance(values, list) and idx < len(values) else None

            daily_out.append({
                "date": day,
                "forecast_rain_24h_mm": daily_at("precipitation_sum"),
                "rain_sum_mm": daily_at("rain_sum"),
                "precip_probability_pct": daily_at("precipitation_probability_max"),
                "et0_mm_day": daily_at("et0_fao_evapotranspiration_sum"),
                "temperature_max_c": daily_at("temperature_2m_max"),
                "temperature_min_c": daily_at("temperature_2m_min"),
            })
    elif hourly_out:
        daily_acc: dict[str, dict[str, Any]] = {}
        for item in hourly_out:
            day = str(item.get("time") or "")[:10]
            if not day:
                continue
            acc = daily_acc.setdefault(day, {"date": day, "forecast_rain_24h_mm": 0.0, "hour_count": 0})
            rain = _to_float_or_none(item.get("rain_mm"))
            if rain is not None:
                acc["forecast_rain_24h_mm"] += rain
            acc["hour_count"] += 1
        for item in daily_acc.values():
            item["forecast_rain_24h_mm"] = round(float(item["forecast_rain_24h_mm"]), 2)
            item.setdefault("rain_sum_mm", item["forecast_rain_24h_mm"])
            item.setdefault("precip_probability_pct", None)
            item.setdefault("et0_mm_day", None)
            item.setdefault("temperature_max_c", None)
            item.setdefault("temperature_min_c", None)
            daily_out.append(item)
    return hourly_out, daily_out


def _forecast_from_met_payload(payload: dict[str, Any] | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw = (payload or {}).get("payload") if isinstance(payload, dict) else None
    ts = (((raw or {}).get("properties") or {}).get("timeseries")) if isinstance(raw, dict) else None
    if not isinstance(ts, list):
        return [], []
    hourly_out: list[dict[str, Any]] = []
    daily_acc: dict[str, dict[str, Any]] = {}
    for row in ts[:48]:
        if not isinstance(row, dict):
            continue
        data = row.get("data") if isinstance(row.get("data"), dict) else {}
        instant = ((data.get("instant") or {}).get("details") or {}) if isinstance(data, dict) else {}
        next1 = (data.get("next_1_hours") or {}) if isinstance(data, dict) else {}
        summary = (next1.get("summary") or {}) if isinstance(next1, dict) else {}
        details = (next1.get("details") or {}) if isinstance(next1, dict) else {}
        item = {
            "time": row.get("time"),
            "temperature_c": instant.get("air_temperature"),
            "humidity_pct": instant.get("relative_humidity"),
            "dew_point_c": None,
            "pressure_hpa": instant.get("air_pressure_at_sea_level"),
            "wind_speed_ms": instant.get("wind_speed"),
            "wind_gust_ms": instant.get("wind_speed_of_gust"),
            "wind_bearing_deg": instant.get("wind_from_direction"),
            "rain_mm": details.get("precipitation_amount"),
            "precip_probability_pct": None,
            "uv_index": instant.get("ultraviolet_index_clear_sky"),
            "cloud_cover_pct": instant.get("cloud_area_fraction"),
            "soil_moisture_pct": None,
            "soil_temperature_c": None,
            "et0_mm": None,
            "weather_code": summary.get("symbol_code"),
            "condition": _weather_code_to_condition(summary.get("symbol_code")),
        }
        hourly_out.append(item)
        day = str(row.get("time") or "")[:10]
        if day:
            acc = daily_acc.setdefault(day, {"date": day, "forecast_rain_24h_mm": 0.0, "hour_count": 0})
            rain = _to_float_or_none(item.get("rain_mm"))
            if rain is not None:
                acc["forecast_rain_24h_mm"] += rain
            acc["hour_count"] += 1
    daily_out = []
    for item in daily_acc.values():
        item["forecast_rain_24h_mm"] = round(float(item["forecast_rain_24h_mm"]), 2)
        daily_out.append(item)
    return hourly_out, daily_out


def _build_irrigation_weather_payload(data: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    data = _attach_weather_cache_for_guard(data if isinstance(data, dict) else {})
    data["weather_station"] = _build_weather_station_snapshot(cfg)
    guard = _build_weather_guard(data, cfg)
    selected = _selected_weather_for_irrigation(data, guard)
    norm = selected.get("normalized") if isinstance(selected.get("normalized"), dict) else {}
    station_norm = ((data.get("weather_station") or {}).get("normalized") or {}) if isinstance(data.get("weather_station"), dict) else {}
    now_ts = time.time()
    age = guard.get("age_seconds")
    available = bool(guard.get("ok")) and not bool(guard.get("stale")) and (age is None or float(age) <= float(((cfg.get("weather_guard") or {}).get("stale_seconds", 180) or 180)))

    weather_code = norm.get("symbol_code")
    condition = _weather_code_to_condition(weather_code)
    rain_rate = _to_float_or_none(guard.get("rain_rate_mm_h"))
    rain_1h = _to_float_or_none(guard.get("rain_1h_mm"))
    wind_speed = _to_float_or_none(guard.get("wind_speed_ms"))
    wind_gust = _to_float_or_none(guard.get("wind_gust_ms"))
    temp = _to_float_or_none(norm.get("air_temperature_c"))
    humidity = _to_float_or_none(norm.get("relative_humidity_pct"))

    hourly, daily = _forecast_from_open_meteo_payload(data.get("weather_open_meteo") if isinstance(data.get("weather_open_meteo"), dict) else None)
    if not hourly:
        hourly, daily = _forecast_from_met_payload(data.get("weather") if isinstance(data.get("weather"), dict) else None)
    forecast_rain_24h = None
    if daily:
        forecast_rain_24h = _to_float_or_none(daily[0].get("forecast_rain_24h_mm"))
    first_hour = hourly[0] if hourly else {}
    precip_probability = _to_float_or_none(first_hour.get("precip_probability_pct")) if isinstance(first_hour, dict) else None
    soil_moisture = _to_float_or_none(station_norm.get("soil_moisture_pct"))
    if soil_moisture is None and isinstance(first_hour, dict):
        soil_moisture = _to_float_or_none(first_hour.get("soil_moisture_pct"))
    soil_temperature = _to_float_or_none(station_norm.get("soil_temperature_c"))
    if soil_temperature is None and isinstance(first_hour, dict):
        soil_temperature = _to_float_or_none(first_hour.get("soil_temperature_c"))
    et0_mm_day = _to_float_or_none(daily[0].get("et0_mm_day")) if daily else None
    dew_point = _to_float_or_none(norm.get("dew_point_c"))
    if dew_point is None:
        dew_point = _to_float_or_none(station_norm.get("dew_point_c"))
    rain_today = _to_float_or_none(station_norm.get("rain_today_mm"))
    rain_last_24h = _to_float_or_none(station_norm.get("rain_24h_mm"))
    source = _irrigation_source_label(selected if isinstance(selected, dict) else {}, guard)
    last_update = (
        norm.get("time")
        or _iso_from_unix_ts(selected.get("_fetched_at_ts") if isinstance(selected, dict) else None, str(cfg.get("timezone") or "Europe/Rome"))
        or _iso_from_unix_ts((data.get("weather_station") or {}).get("_fetched_at_ts") if isinstance(data.get("weather_station"), dict) else None, str(cfg.get("timezone") or "Europe/Rome"))
        or guard.get("updated_at")
        or data.get("timestamp_local")
    )

    dry_day = bool(available and (rain_rate or 0.0) <= 0.05 and (forecast_rain_24h is None or forecast_rain_24h < 1.0) and (humidity is None or humidity < 60.0))
    hot_day = bool(available and temp is not None and temp >= 30.0)
    freeze_block = bool(available and temp is not None and temp <= 2.0)
    rain_block = bool(available and (guard.get("rain_alarm") or ((rain_1h or 0.0) > 0.0 and (rain_rate or 0.0) >= 1.0)))
    wind_block = bool(available and guard.get("wind_alarm"))
    is_raining = bool(available and ((rain_rate or 0.0) > 0.0 or (rain_1h or 0.0) > 0.0))

    score = 100
    reasons: list[str] = []
    if not available:
        score = 0
        reasons.append(str(guard.get("error") or "weather_unavailable"))
    if rain_block:
        score -= 50
        reasons.append("rain_block")
    if wind_block:
        score -= 30
        reasons.append("wind_block")
    if freeze_block:
        score -= 80
        reasons.append("freeze_block")
    if hot_day:
        score += 10
        reasons.append("hot_day")
    if dry_day:
        score += 10
        reasons.append("dry_day")
    score = max(0, min(100, int(score)))

    base = _empty_irrigation_weather_payload(cfg)
    base.update({
        "temperature_c": temp,
        "humidity_pct": humidity,
        "pressure_hpa": _to_float_or_none(norm.get("air_pressure_hpa")),
        "dew_point_c": dew_point,
        "wind_speed_ms": wind_speed,
        "wind_gust_ms": wind_gust,
        "wind_bearing_deg": _to_float_or_none(guard.get("wind_dir_deg")),
        "rain_rate_mm_h": rain_rate,
        "rain_today_mm": rain_today,
        "rain_last_24h_mm": rain_last_24h,
        "precip_probability_pct": precip_probability,
        "forecast_rain_24h_mm": forecast_rain_24h,
        "solar_radiation_w_m2": _to_float_or_none(station_norm.get("solar_radiation_w_m2")),
        "uv_index": _to_float_or_none(norm.get("uv_index")),
        "cloud_cover_pct": _to_float_or_none(norm.get("cloud_area_fraction_pct")),
        "soil_moisture_pct": soil_moisture,
        "soil_temperature_c": soil_temperature,
        "et0_mm_day": et0_mm_day,
        "weather_code": weather_code,
        "condition": condition,
        "last_update": last_update,
        "source": source,
        "age_seconds": age,
        "available": available,
        "is_raining": is_raining,
        "rain_block": rain_block,
        "wind_block": wind_block,
        "freeze_block": freeze_block,
        "hot_day": hot_day,
        "dry_day": dry_day,
        "irrigation_weather_score": score,
        "irrigation_weather_reason": ", ".join(reasons) if reasons else "ok",
        "hourly_forecast": hourly,
        "daily_forecast": daily,
        "generated_at": datetime.now(pytz.timezone(str(cfg.get("timezone") or "Europe/Rome"))).isoformat(),
        "schema": "e_sunmind_irrigation_weather.v1",
    })
    if not available:
        base["error"] = str(guard.get("error") or "weather_unavailable")
    return base


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
    numeric_value = _to_float_or_none(state_raw)
    return {
        "ok": True,
        "entity_id": entity,
        "state": state_raw,
        "value": numeric_value,
        "unit": attrs.get("unit_of_measurement"),
        "device_class": attrs.get("device_class"),
        "state_class": attrs.get("state_class"),
        "watts": numeric_value,
        "friendly_name": attrs.get("friendly_name"),
        "last_updated": payload.get("last_updated"),
    }


def _get_supervisor_token() -> str:
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
    return token or ""


def _fetch_ha_device_entities(device_id: str) -> list[str]:
    did = str(device_id or "").strip()
    if not did:
        return []
    token = _get_supervisor_token()
    if not token:
        return []
    url = "http://supervisor/core/api/template"
    template = "{{ device_entities('" + did.replace("'", "\\'") + "') | join('\\n') }}"
    req = Request(
        url,
        data=json.dumps({"template": template}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
    except Exception:
        return []
    out: list[str] = []
    for line in body.splitlines():
        ent = line.strip()
        if ent and "." in ent:
            out.append(ent)
    return out


def _auto_map_weather_station_entities(device_id: str) -> dict[str, str]:
    ents = _fetch_ha_device_entities(device_id)
    if not ents:
        return {}
    infos: list[dict[str, Any]] = []
    for ent in ents:
        st = _fetch_ha_entity_state(ent)
        if isinstance(st, dict) and st.get("ok"):
            infos.append(st)

    def _txt(info: dict[str, Any]) -> str:
        return f"{str(info.get('entity_id') or '').lower()} {str(info.get('friendly_name') or '').lower()}"

    def _unit(info: dict[str, Any]) -> str:
        return str(info.get("unit") or "").strip().lower()

    def _dclass(info: dict[str, Any]) -> str:
        return str(info.get("device_class") or "").strip().lower()

    def _pick(pred) -> str:
        for info in infos:
            if pred(info):
                return str(info.get("entity_id") or "")
        return ""

    mapped: dict[str, str] = {}

    # Wind
    mapped["wind_gust_entity_id"] = _pick(
        lambda i: ("gust" in _txt(i)) or ("raffica" in _txt(i))
    )
    mapped["wind_speed_entity_id"] = _pick(
        lambda i: ("wind" in _txt(i) or "vento" in _txt(i))
        and ("speed" in _txt(i) or "veloc" in _txt(i))
        and ("gust" not in _txt(i) and "raffica" not in _txt(i))
    ) or _pick(
        lambda i: _dclass(i) == "wind_speed"
        and ("gust" not in _txt(i) and "raffica" not in _txt(i))
    )
    mapped["wind_direction_entity_id"] = _pick(
        lambda i: ("wind" in _txt(i) or "vento" in _txt(i))
        and ("direction" in _txt(i) or "dir" in _txt(i) or "direzione" in _txt(i))
    )

    # Rain
    mapped["rain_rate_entity_id"] = _pick(
        lambda i: ("rain" in _txt(i) or "pioggia" in _txt(i))
        and ("rate" in _txt(i) or "/h" in _unit(i) or "mm/h" in _unit(i))
    )
    mapped["rain_1h_entity_id"] = _pick(
        lambda i: ("rain" in _txt(i) or "pioggia" in _txt(i))
        and ("hour" in _txt(i) or "1h" in _txt(i) or "hourly" in _txt(i) or "oraria" in _txt(i))
        and ("rate" not in _txt(i))
    )
    mapped["rain_today_entity_id"] = _pick(
        lambda i: ("rain" in _txt(i) or "pioggia" in _txt(i))
        and ("today" in _txt(i) or "oggi" in _txt(i) or "daily" in _txt(i) or "giornal" in _txt(i))
        and ("rate" not in _txt(i))
    )
    mapped["rain_24h_entity_id"] = _pick(
        lambda i: ("rain" in _txt(i) or "pioggia" in _txt(i))
        and ("24h" in _txt(i) or "24 h" in _txt(i) or "last 24" in _txt(i) or "ultime 24" in _txt(i))
        and ("rate" not in _txt(i))
    )

    # Extra
    mapped["outdoor_temp_entity_id"] = _pick(
        lambda i: _dclass(i) == "temperature"
        and ("outdoor" in _txt(i) or "esterna" in _txt(i) or "outside" in _txt(i))
    )
    mapped["outdoor_humidity_entity_id"] = _pick(
        lambda i: _dclass(i) == "humidity"
        and ("outdoor" in _txt(i) or "esterna" in _txt(i) or "outside" in _txt(i))
    )
    mapped["pressure_entity_id"] = _pick(
        lambda i: _dclass(i) in {"atmospheric_pressure", "pressure"}
        or ("pressure" in _txt(i) or "pressione" in _txt(i))
    )
    mapped["uv_index_entity_id"] = _pick(
        lambda i: ("uv" in _txt(i))
    )
    mapped["dewpoint_entity_id"] = _pick(
        lambda i: ("dewpoint" in _txt(i)) or ("dew point" in _txt(i))
    )
    mapped["feels_like_entity_id"] = _pick(
        lambda i: ("feels like" in _txt(i)) or ("apparent" in _txt(i))
    )
    mapped["solar_lux_entity_id"] = _pick(
        lambda i: ("solar lux" in _txt(i)) or ("illuminance" in _txt(i)) or ("lux" in _txt(i) and "solar" in _txt(i))
    )
    mapped["solar_radiation_entity_id"] = _pick(
        lambda i: ("solar radiation" in _txt(i)) or ("irradiance" in _txt(i))
    )
    mapped["soil_moisture_entity_id"] = _pick(
        lambda i: ("soil" in _txt(i) or "suolo" in _txt(i) or "ground" in _txt(i))
        and ("moisture" in _txt(i) or "humidity" in _txt(i) or "umid" in _txt(i))
    )
    mapped["soil_temperature_entity_id"] = _pick(
        lambda i: (_dclass(i) == "temperature")
        and ("soil" in _txt(i) or "suolo" in _txt(i) or "ground" in _txt(i))
    )
    mapped["vpd_entity_id"] = _pick(
        lambda i: ("vapour pressure deficit" in _txt(i)) or ("vapor pressure deficit" in _txt(i)) or ("vpd" in _txt(i))
    )

    # Fallbacks to reduce empty fields with integrations that do not expose "outdoor" in entity names.
    if not mapped.get("outdoor_temp_entity_id"):
        mapped["outdoor_temp_entity_id"] = _pick(
            lambda i: _dclass(i) == "temperature"
            and ("indoor" not in _txt(i) and "internal" not in _txt(i) and "inside" not in _txt(i))
        )
    if not mapped.get("outdoor_humidity_entity_id"):
        mapped["outdoor_humidity_entity_id"] = _pick(
            lambda i: _dclass(i) == "humidity"
            and ("indoor" not in _txt(i) and "internal" not in _txt(i) and "inside" not in _txt(i))
        )
    if not mapped.get("solar_radiation_entity_id"):
        mapped["solar_radiation_entity_id"] = _pick(
            lambda i: ("solar" in _txt(i) and "radiation" in _txt(i))
            or ("w/m" in _unit(i))
            or ("irradiance" in _txt(i))
        )
    if not mapped.get("solar_lux_entity_id"):
        mapped["solar_lux_entity_id"] = _pick(
            lambda i: ("lux" in _txt(i)) or (_unit(i) == "lx")
        )
    if not mapped.get("feels_like_entity_id"):
        mapped["feels_like_entity_id"] = _pick(
            lambda i: ("feelslike" in _txt(i)) or ("percepita" in _txt(i))
        )

    return {k: v for k, v in mapped.items() if v}


def _fetch_ha_core_config() -> dict[str, Any] | None:
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
        return None
    req = Request(
        "http://supervisor/core/api/config",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


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
        payload = json.loads(WEATHER_FILE.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and payload.get("_fetched_at_ts") is None:
            payload["_fetched_at_ts"] = WEATHER_FILE.stat().st_mtime
        return payload
    except Exception:
        return None


def _read_weather_open_meteo_cache() -> dict[str, Any] | None:
    if not WEATHER_OPEN_METEO_FILE.exists():
        return None
    try:
        payload = json.loads(WEATHER_OPEN_METEO_FILE.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and payload.get("_fetched_at_ts") is None:
            payload["_fetched_at_ts"] = WEATHER_OPEN_METEO_FILE.stat().st_mtime
        return payload
    except Exception:
        return None


def _attach_weather_cache_for_guard(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return payload
    weather = payload.get("weather")
    if not (isinstance(weather, dict) and weather.get("ok") and _weather_payload_ts(weather) is not None):
        cached = _read_weather_cache()
        if isinstance(cached, dict) and cached.get("ok"):
            payload["weather"] = cached
    weather_open = payload.get("weather_open_meteo")
    if not (isinstance(weather_open, dict) and weather_open.get("ok") and _weather_payload_ts(weather_open) is not None):
        cached_open = _read_weather_open_meteo_cache()
        if isinstance(cached_open, dict) and cached_open.get("ok"):
            payload["weather_open_meteo"] = cached_open
    return payload


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
            az_start = None
            az_end = None
            try:
                if item.get("azimuth_start_deg") is not None:
                    az_start = float(item.get("azimuth_start_deg"))
                if item.get("azimuth_end_deg") is not None:
                    az_end = float(item.get("azimuth_end_deg"))
            except Exception:
                az_start = az_start if isinstance(az_start, float) else None
                az_end = az_end if isinstance(az_end, float) else None
            alt_min = item.get("altitude_min_deg")
            alt_max = item.get("altitude_max_deg")
            shades_out.append(
                {
                    "id": sid,
                    "name": str(item.get("name") or sid),
                    "cover_entity": (str(item.get("cover_entity")).strip() if item.get("cover_entity") else None),
                    "enabled": bool(item.get("enabled", True)),
                    "active": bool(item.get("active", False)),
                    "azimuth_start_deg": (az_start % 360.0) if isinstance(az_start, float) else None,
                    "azimuth_end_deg": (az_end % 360.0) if isinstance(az_end, float) else None,
                    "altitude_min_deg": float(alt_min) if alt_min is not None else None,
                    "altitude_max_deg": float(alt_max) if alt_max is not None else None,
                    "settings": item.get("settings") if isinstance(item.get("settings"), dict) else {},
                    "sensors": item.get("sensors") if isinstance(item.get("sensors"), dict) else {},
                    "priority": int(item.get("priority")) if item.get("priority") is not None else None,
                    "color": (str(item.get("color")).strip() if item.get("color") else None),
                }
            )
    out = {
        "ok": True,
        "source": str(payload.get("source") or "e-tendeintelligenti"),
        "updated_at": payload.get("updated_at"),
        "shades": shades_out,
    }
    lat, lon, tz = _extract_geo_from_payload(payload)
    if lat is not None and lon is not None:
        out["latitude"] = lat
        out["longitude"] = lon
    if tz is not None:
        out["timezone"] = tz
    return out


def _lookup_tende_map_shade(
    payload: dict[str, Any] | None,
    shade_id: str,
    cover_entity: str,
    name: str,
) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    shades = payload.get("shades")
    if not isinstance(shades, list):
        return None
    wanted_id = str(shade_id or "").strip()
    wanted_cover = str(cover_entity or "").strip().casefold()
    wanted_name = str(name or "").strip().casefold()
    for shade in shades:
        if not isinstance(shade, dict):
            continue
        if wanted_id and str(shade.get("id") or "").strip() == wanted_id:
            return shade
        if wanted_cover and str(shade.get("cover_entity") or "").strip().casefold() == wanted_cover:
            return shade
        if wanted_name and str(shade.get("name") or "").strip().casefold() == wanted_name:
            return shade
    return None


def _values_equivalent(expected: Any, actual: Any) -> bool:
    if isinstance(expected, bool):
        return bool(actual) is expected
    exp_num = _coerce_float(expected)
    act_num = _coerce_float(actual)
    if exp_num is not None and act_num is not None:
        return abs(exp_num - act_num) <= 0.05
    return str(expected).strip() == str(actual).strip()


def _shade_settings_confirm(shade: dict[str, Any] | None, expected_settings: dict[str, Any]) -> bool:
    if not isinstance(shade, dict) or not isinstance(expected_settings, dict):
        return False
    shade_settings = shade.get("settings") if isinstance(shade.get("settings"), dict) else {}
    checked = 0
    for key, expected in expected_settings.items():
        if key in {"id", "name", "cover_entity", "settings", "sensors"} or expected is None:
            continue
        actual = shade_settings.get(key, shade.get(key))
        if actual is None and key == "azimuth_start":
            actual = shade_settings.get("azimuth_start_deg", shade.get("azimuth_start_deg"))
        if actual is None and key == "azimuth_stop":
            actual = shade_settings.get("azimuth_end_deg", shade.get("azimuth_end_deg"))
        if actual is None:
            continue
        checked += 1
        if not _values_equivalent(expected, actual):
            return False
    return checked > 0


def _wait_for_tende_map_confirmation(
    shade_id: str,
    cover_entity: str,
    name: str,
    expected_settings: dict[str, Any],
    timeout_seconds: float = 4.0,
) -> dict[str, Any] | None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        raw = _read_tende_map_cache()
        if isinstance(raw, dict):
            norm = _normalize_tende_map_payload(raw)
            shade = _lookup_tende_map_shade(norm, shade_id, cover_entity, name)
            if _shade_settings_confirm(shade, expected_settings):
                return shade
        time.sleep(0.2)
    return None


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


def _resolve_runtime_geo(cfg: dict[str, Any]) -> tuple[float, float, str, str]:
    lat = float(cfg.get("latitude", 44.6973))
    lon = float(cfg.get("longitude", 7.8683))
    tz = str(cfg.get("timezone", "Europe/Rome"))
    source = "local_config"
    mode = str(cfg.get("coordinates_source_mode") or "e_tende").strip().lower()
    if mode not in {"e_tende", "ha_core", "local"}:
        mode = "e_tende"

    def _to_float_maybe(v: Any) -> float | None:
        if v is None:
            return None
        try:
            return float(v)
        except Exception:
            try:
                return float(str(v).strip().replace(",", "."))
            except Exception:
                return None

    def _extract_tende_geo(tm_payload: dict[str, Any]) -> tuple[float | None, float | None, str | None]:
        tlat = tm_payload.get("latitude")
        tlon = tm_payload.get("longitude")
        ttz = tm_payload.get("timezone")
        # Compatibility aliases
        if tlat is None:
            tlat = tm_payload.get("lat")
        if tlon is None:
            tlon = tm_payload.get("lon")
        if ttz is None:
            ttz = tm_payload.get("tz")
        coords = tm_payload.get("coordinates")
        if isinstance(coords, dict):
            if tlat is None:
                tlat = coords.get("latitude", coords.get("lat"))
            if tlon is None:
                tlon = coords.get("longitude", coords.get("lon"))
            if ttz is None:
                ttz = coords.get("timezone", coords.get("tz"))
        out_lat = None
        out_lon = None
        out_tz = None
        out_lat = _to_float_maybe(tlat)
        out_lon = _to_float_maybe(tlon)
        if ttz is not None and str(ttz).strip():
            out_tz = str(ttz).strip()
        return out_lat, out_lon, out_tz

    if mode == "e_tende":
        tm = _read_tende_map_cache()
        if isinstance(tm, dict):
            tlat, tlon, ttz = _extract_tende_geo(tm)
            if tlat is not None and tlon is not None:
                lat = tlat
                lon = tlon
                source = "e-tendeintelligenti"
            if ttz is not None:
                tz = ttz
                source = "e-tendeintelligenti"
        if mode == "e_tende":
            if source != "e-tendeintelligenti":
                source = "e-tende_missing_coords"
            return lat, lon, tz, source

    if mode == "ha_core" and source != "e-tendeintelligenti":
        ha_cfg = _fetch_ha_core_config()
        if isinstance(ha_cfg, dict):
            try:
                hlat = ha_cfg.get("latitude")
                hlon = ha_cfg.get("longitude")
                if hlat is not None and hlon is not None:
                    lat = float(hlat)
                    lon = float(hlon)
                    source = "home_assistant_core"
                htz = ha_cfg.get("time_zone")
                if htz is not None and str(htz).strip():
                    tz = str(htz).strip()
                    source = "home_assistant_core"
            except Exception:
                pass
        if mode == "ha_core":
            return lat, lon, tz, source

    return lat, lon, tz, source


def _compute_data(cfg: dict[str, Any]) -> dict[str, Any]:
    latitude, longitude, resolved_tz, coord_source = _resolve_runtime_geo(cfg)
    location_query = str(cfg.get("location_query") or "").strip()
    resolved_location = None

    if location_query:
        try:
            geolocator = Nominatim(user_agent="e-sunmind-addon")
            found = geolocator.geocode(location_query, language="it")
            if found is not None:
                latitude = float(found.latitude)
                longitude = float(found.longitude)
                coord_source = "location_query"
                resolved_location = {
                    "query": location_query,
                    "display_name": found.address,
                    "latitude": latitude,
                    "longitude": longitude,
                }
        except Exception:
            resolved_location = {"query": location_query, "error": "geocoding_failed_using_manual_coordinates"}

    tz = pytz.timezone(str(resolved_tz))
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
        "timezone": str(resolved_tz),
        "coordinates_source": coord_source,
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
        json.dumps(_slim_runtime_payload(data), ensure_ascii=False),
        retain=True,
    )


def _slim_runtime_payload(data: dict[str, Any]) -> dict[str, Any]:
    """Keep MQTT diagnostic attributes small enough for HA recorder."""
    slim = json.loads(json.dumps(data, ensure_ascii=False, default=str))
    for key in ("weather", "weather_open_meteo", "air_quality", "forecast_solar"):
        block = slim.get(key)
        if isinstance(block, dict) and "payload" in block:
            block["payload_omitted_from_mqtt"] = True
            block.pop("payload", None)
    return slim


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
            humidity_live = _fetch_ha_entity_state(str(cfg.get("external_humidity_entity_id") or ""))
            weather_station = _build_weather_station_snapshot(cfg)
            data["pv_live"] = pv_live
            data["external_temp_live"] = temp_live
            data["external_humidity_live"] = humidity_live
            data["weather_station"] = weather_station
            data["weather"] = weather
            data["weather_open_meteo"] = weather_open_meteo
            data["air_quality"] = airq
            data["forecast_solar"] = forecast
            data["tende_map"] = _build_tende_map_snapshot(cfg)
            data["weather_guard"] = _build_weather_guard(data, cfg)
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


@app.get("/api/diag/static_hashes")
async def static_hashes():
    index_path = STATIC_ROOT / "index.html"
    index_text = ""
    try:
        index_text = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    except Exception:
        index_text = ""

    refs = _extract_index_asset_refs(index_text)
    js_rel = refs.get("index_js_rel")
    css_rel = refs.get("index_css_rel")

    files: list[dict[str, Any]] = []
    files.append(_static_file_meta(index_path, "index.html"))
    files.append(_static_file_meta(STATIC_ROOT / "favicon.png", "favicon.png"))
    files.append(_static_file_meta(STATIC_ROOT / "logo.png", "logo.png"))

    if isinstance(js_rel, str) and js_rel.startswith("./"):
        files.append(_static_file_meta(STATIC_ROOT / js_rel[2:], js_rel[2:]))
    if isinstance(css_rel, str) and css_rel.startswith("./"):
        files.append(_static_file_meta(STATIC_ROOT / css_rel[2:], css_rel[2:]))

    return JSONResponse(
        {
            "ok": True,
            "version": APP_VERSION,
            "index_refs": refs,
            "files": files,
        }
    )


@app.get("/api/diag/static_hash")
async def static_hash(path: str = ""):
    rel = str(path or "").strip().lstrip("/")
    if not rel or ".." in rel:
        return JSONResponse({"ok": False, "error": "invalid_path"}, status_code=400)
    full = STATIC_ROOT / rel
    if not full.exists() or not full.is_file():
        return JSONResponse({"ok": False, "error": "not_found", "path": rel}, status_code=404)
    return JSONResponse({"ok": True, "version": APP_VERSION, "file": _static_file_meta(full, rel)})


@app.get("/api/sun/live")
async def sun_live():
    if not DATA_FILE.exists():
        return JSONResponse({"ok": False, "error": "data_not_ready"}, status_code=503)
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    sp = payload.get("sun_position") if isinstance(payload, dict) else None
    if not isinstance(sp, dict):
        return JSONResponse({"ok": False, "error": "data_not_ready"}, status_code=503)
    az = sp.get("azimuth_compass_deg")
    alt = sp.get("altitude_deg")
    if az is None or alt is None:
        return JSONResponse({"ok": False, "error": "data_not_ready"}, status_code=503)
    return JSONResponse(
        {
            "ok": True,
            "azimuth_compass_deg": float(az),
            "altitude_deg": float(alt),
            "updated_at": str(payload.get("timestamp_local") or datetime.utcnow().isoformat()),
            "source": "e-sunmind",
        }
    )


@app.get("/api/data")
async def data(site: str | None = None):
    if not DATA_FILE.exists():
        return JSONResponse({"ok": False, "error": "data_not_ready"})
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    payload = _attach_weather_cache_for_guard(payload)
    cfg = _load_options()
    if site:
        payload["energy"] = _build_energy_snapshot(cfg, site, include_sites=False)
        return JSONResponse(payload)
    payload["tende_map"] = _build_tende_map_snapshot(cfg)
    payload["weather_station"] = _build_weather_station_snapshot(cfg)
    payload["weather_guard"] = _build_weather_guard(payload, cfg)
    payload["energy"] = _build_energy_snapshot(cfg)
    return JSONResponse(payload)


@app.get("/api/energy/debug")
async def energy_debug():
    cfg = _load_options()
    e_cfg = cfg.get("energy") if isinstance(cfg, dict) else {}
    if not isinstance(e_cfg, dict):
        e_cfg = {}
    snapshot = _build_energy_snapshot(cfg)
    raw = str(e_cfg.get("sunsynk_card_config_json") or "")
    parse_error = None
    parsed: dict[str, Any] = {}
    try:
        j = json.loads(raw) if raw.strip() else {}
        if isinstance(j, dict):
            parsed = j
        else:
            parse_error = "card_config_not_object"
    except Exception as exc:
        parse_error = str(exc)
    entities = parsed.get("entities") if isinstance(parsed.get("entities"), dict) else {}
    return JSONResponse(
        {
            "ok": True,
            "energy_config": e_cfg,
            "card_config_parse_error": parse_error,
            "card_config_entities": entities,
            "snapshot": snapshot,
        }
    )


@app.get("/api/energy/history")
async def energy_history(site: str | None = None, period: str = "day", date: str = ""):
    cfg = _load_options()
    try:
        return JSONResponse(await _build_energy_history_snapshot(cfg, site, period, date))
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


@app.get("/api/data_demo")
async def data_demo():
    now_local = datetime.now().astimezone().isoformat()
    # Prefer real snapshot when available, but never fail the demo endpoint.
    if DATA_FILE.exists():
        try:
            payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            payload = _attach_weather_cache_for_guard(payload)
            cfg = _load_options()
            payload["tende_map"] = _build_tende_map_snapshot(cfg)
            payload["weather_station"] = _build_weather_station_snapshot(cfg)
            payload["weather_guard"] = _build_weather_guard(payload, cfg)
            payload["energy"] = _build_energy_snapshot(cfg)
            payload["demo_mode"] = True
            payload["demo_source"] = "live_snapshot"
            return JSONResponse(payload)
        except Exception:
            pass
    # Guaranteed fallback for customer demo.
    fallback = {
        "timestamp_local": now_local,
        "timezone": "Europe/Rome",
        "coordinates_source": "demo",
        "coordinates": {"latitude": 44.6973, "longitude": 7.8683},
        "sun_position": {"azimuth_compass_deg": 245.0, "altitude_deg": 34.0},
        "external_temp_live": {"ok": True, "value": 24.2, "unit": "°C"},
        "external_humidity_live": {"ok": True, "value": 48.0, "unit": "%"},
        "pv_live": {"ok": True, "watts": 4200.0, "unit": "W"},
        "weather": {
            "ok": True,
            "provider": "met",
            "normalized": {
                "time": now_local,
                "air_temperature_c": 20.4,
                "relative_humidity_pct": 52.0,
                "wind_speed_ms": 2.2,
                "wind_gust_ms": 3.4,
                "wind_from_direction_deg": 118.0,
                "air_pressure_hpa": 1012.0,
                "cloud_area_fraction_pct": 22.0,
                "uv_index": 3.0,
                "symbol_code": "fair_day",
                "precipitation_next_1h_mm": 0.0,
            },
        },
        "weather_open_meteo": {
            "ok": True,
            "provider": "open_meteo",
            "normalized": {
                "time": now_local,
                "air_temperature_c": 20.8,
                "relative_humidity_pct": 50.0,
                "wind_speed_ms": 2.4,
                "wind_gust_ms": 3.3,
                "wind_from_direction_deg": 124.0,
                "air_pressure_hpa": 1011.8,
                "cloud_area_fraction_pct": 18.0,
                "uv_index": 3.6,
                "symbol_code": 1,
                "precipitation_next_1h_mm": 0.0,
            },
        },
        "weather_station": {
            "ok": True,
            "enabled": True,
            "source": "e-Control",
            "normalized": {
                "wind_speed_ms": 1.8,
                "wind_gust_ms": 2.9,
                "wind_from_direction_deg": 112.0,
                "rain_rate_mm_h": 0.0,
                "rain_1h_mm": 0.0,
                "air_temperature_c": 24.6,
                "relative_humidity_pct": 46.0,
                "air_pressure_hpa": 984.2,
                "uv_index": 2.0,
                "dew_point_c": 11.6,
                "feels_like_temperature_c": 24.6,
                "solar_lux_lx": 38200.0,
                "solar_radiation_w_m2": 305.0,
                "vapour_pressure_deficit_hpa": 15.0,
                "precipitation_next_1h_mm": 0.0,
            },
            "entities_all": [],
        },
        "weather_guard": {
            "ok": True,
            "enabled": True,
            "wind_speed_ms": 2.2,
            "wind_gust_ms": 3.4,
            "wind_dir_deg": 118.0,
            "rain_rate_mm_h": 0.0,
            "rain_1h_mm": 0.0,
            "facade_rain_risk": False,
            "wind_alarm": False,
            "rain_alarm": False,
            "severe_weather_alarm": False,
            "updated_at": now_local,
            "station": {"enabled": True, "ok": True, "used": True, "error": None, "age_seconds": 0.0},
            "stale": False,
            "age_seconds": 0.0,
            "source": "weather_station_demo",
        },
        "energy": {
            "ok": True,
            "enabled": True,
            "site_id": "default",
            "site_name": "Impianto 1",
            "selected_site_id": "default",
            "theme": "classic_flow",
            "dashboard_background_color": "#080a10",
            "entities": {},
            "normalized": {
                "pv_power_w": 4200.0,
                "home_power_w": 1580.0,
                "grid_power_w": 1400.0,
                "battery_power_w": 1220.0,
                "battery_soc_pct": 74.0,
                "pv_installed_kwp": 6.6,
                "pv_energy_today_kwh": 26.5,
                "home_energy_today_kwh": 45.2,
                "grid_import_today_kwh": 18.7,
                "grid_export_today_kwh": 9.1,
            },
            "errors": {},
            "sites": [],
        },
        "tende_map": {"ok": True, "availability": "online", "stale": False, "updated_at": now_local, "source": "demo", "shades": [], "cover_states": {}},
        "demo_mode": True,
        "demo_source": "fallback_payload",
    }
    return JSONResponse(fallback)


@app.get("/api/weather/guard")
async def weather_guard_get():
    if not DATA_FILE.exists():
        return JSONResponse({"ok": False, "error": "data_not_ready"}, status_code=503)
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    payload = _attach_weather_cache_for_guard(payload)
    cfg = _load_options()
    payload["weather_station"] = _build_weather_station_snapshot(cfg)
    return JSONResponse(_build_weather_guard(payload, cfg))


@app.get("/api/weather/irrigation")
async def weather_irrigation_get():
    cfg = _load_options()
    if not DATA_FILE.exists():
        return JSONResponse(_empty_irrigation_weather_payload(cfg, error="data_not_ready"), status_code=503)
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return JSONResponse(_build_irrigation_weather_payload(payload, cfg))


@app.get("/api/weather_station/autofill")
async def weather_station_autofill(device_id: str = ""):
    did = str(device_id or "").strip()
    if not did:
        return JSONResponse({"ok": False, "error": "missing_device_id"}, status_code=400)
    mapped = _auto_map_weather_station_entities(did)
    return JSONResponse({"ok": bool(mapped), "device_id": did, "mapped": mapped})


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
    cover_entity = str(payload.get("cover_entity") or "").strip()
    shade_name = str(payload.get("name") or payload.get("profile_name") or "").strip()
    if not shade_id and not cover_entity:
        return JSONResponse({"ok": False, "error": "missing_target"}, status_code=400)

    settings = payload.get("settings") if isinstance(payload.get("settings"), dict) else {}
    merged_settings = dict(settings)
    for key, value in payload.items():
        if key not in {"settings", "sensors"}:
            merged_settings[key] = value

    # Backward compatible aliases for existing e-Tende parser and UI.
    if merged_settings.get("azimuth_start_deg") is not None:
        try:
            merged_settings["azimuth_start_deg"] = float(merged_settings["azimuth_start_deg"]) % 360.0
        except Exception:
            return JSONResponse({"ok": False, "error": "invalid_azimuth_start"}, status_code=400)
    if merged_settings.get("azimuth_end_deg") is not None:
        try:
            merged_settings["azimuth_end_deg"] = float(merged_settings["azimuth_end_deg"]) % 360.0
        except Exception:
            return JSONResponse({"ok": False, "error": "invalid_azimuth_end"}, status_code=400)

    cfg = _load_options()
    tm_cfg = (cfg.get("tende_map") or {})
    host = str(tm_cfg.get("mqtt_host") or "192.168.3.13").strip()
    port = int(tm_cfg.get("mqtt_port") or 1883)
    username = str(tm_cfg.get("mqtt_username") or "").strip()
    password = str(tm_cfg.get("mqtt_password") or "")
    cmd_topics = ["e-tendeintelligenti/cmd/shades/update"]
    fallback_cmd_topics = ["e-tendeintelligenti/cmd/map/shades/update"]
    ack_topics = [
        "e-tendeintelligenti/cmd/shades/update/ack",
        "e-tendeintelligenti/cmd/map/shades/update/ack",
    ]
    request_id = uuid.uuid4().hex
    shade_payload = {
        "id": shade_id,
        "cover_entity": cover_entity or None,
        "settings": merged_settings,
        **merged_settings,
    }
    msg = {
        "source": "e-sunmind",
        "request_id": request_id,
        "updated_at": datetime.utcnow().isoformat(),
        "id": shade_id,
        "cover_entity": cover_entity or None,
        "settings": merged_settings,
        **merged_settings,
        "shade": shade_payload,
        "shades": [shade_payload],
    }
    client = None
    ack_result: dict[str, Any] | None = None
    ack_errors: list[dict[str, Any]] = []
    try:
        connected = threading.Event()
        client = mqtt.Client(client_id=f"e-sunmind-cmd-{int(time.time())}")
        if username:
            client.username_pw_set(username, password)
        def _on_connect(_c: mqtt.Client, _u: Any, _flags: Any, rc: int) -> None:
            if rc == 0:
                connected.set()
        def _on_message(_c: mqtt.Client, _u: Any, m: mqtt.MQTTMessage) -> None:
            nonlocal ack_result, ack_errors
            try:
                parsed = json.loads(m.payload.decode("utf-8", errors="ignore"))
                if isinstance(parsed, dict) and str(parsed.get("request_id") or "") == request_id:
                    if parsed.get("ok") is True or str(parsed.get("status") or "").lower() == "ok":
                        ack_result = parsed
                    else:
                        ack_errors.append(parsed)
            except Exception:
                pass
        client.on_connect = _on_connect
        client.on_message = _on_message
        client.connect(host, port, 60)
        client.loop_start()
        if not connected.wait(3.0):
            return JSONResponse({"ok": False, "error": "mqtt_connect_timeout", "host": host, "port": port}, status_code=504)
        for at in ack_topics:
            client.subscribe(at, qos=1)
        # Give the broker time to register subscriptions before e-Tende can answer.
        # Without this, a very fast ACK can be published before this client is listening.
        time.sleep(0.35)
        def _publish_to_topics(topics: list[str]) -> None:
            encoded = json.dumps(msg, ensure_ascii=False)
            for topic in topics:
                info = client.publish(topic, encoded, qos=1, retain=False)
                try:
                    info.wait_for_publish(timeout=2.0)
                except Exception:
                    pass

        def _wait_for_ack_or_map(timeout_seconds: float) -> dict[str, Any] | None:
            t_start = time.time()
            while (time.time() - t_start) < timeout_seconds and ack_result is None:
                time.sleep(0.05)
            if ack_result is not None:
                return {"mode": "ack", "ack": ack_result}
            confirmed = _wait_for_tende_map_confirmation(
                shade_id,
                cover_entity,
                shade_name,
                merged_settings,
                timeout_seconds=2.0,
            )
            if confirmed is not None:
                return {"mode": "map", "confirmed_shade": confirmed}
            return None

        _publish_to_topics(cmd_topics)
        result = _wait_for_ack_or_map(4.0)
        if result is None:
            _publish_to_topics(fallback_cmd_topics)
            result = _wait_for_ack_or_map(4.0)
        if result is not None and result.get("mode") == "map":
            return JSONResponse(
                {
                    "ok": True,
                    "status": "confirmed_by_map",
                    "topics": cmd_topics + fallback_cmd_topics,
                    "payload": msg,
                    "ack": None,
                    "ack_errors": ack_errors[-5:],
                    "confirmed_shade": result.get("confirmed_shade"),
                }
            )
        if not ack_result:
            if ack_errors:
                last_error = ack_errors[-1]
                return JSONResponse(
                    {
                        "ok": False,
                        "error": "ack_negative",
                        "topics": cmd_topics + fallback_cmd_topics,
                        "payload": msg,
                        "ack": last_error,
                        "ack_errors": ack_errors[-5:],
                    },
                    status_code=502,
                )
            return JSONResponse(
                {
                    "ok": True,
                    "status": "sent_no_ack",
                    "warning": "ack_timeout",
                    "topics": cmd_topics + fallback_cmd_topics,
                    "ack_topics": ack_topics,
                    "payload": msg,
                    "ack": None,
                    "ack_errors": ack_errors[-5:],
                }
            )
        return JSONResponse({"ok": True, "topics": cmd_topics, "payload": msg, "ack": ack_result, "ack_errors": ack_errors[-5:]})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)
    finally:
        try:
            if client is not None:
                client.loop_stop()
                client.disconnect()
        except Exception:
            pass

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

    keys = ("latitude", "longitude", "timezone", "coordinates_source_mode", "interval_minutes", "location_query", "pv_actual_entity_id", "external_temp_entity_id", "external_humidity_entity_id", "weather", "weather_station", "weather_guard", "air_quality", "tende_map", "energy")

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
        now_data["external_humidity_live"] = _fetch_ha_entity_state(str(cfg.get("external_humidity_entity_id") or ""))
        now_data["weather_station"] = _build_weather_station_snapshot(cfg)
        now_data["weather_guard"] = _build_weather_guard(now_data, cfg)
        DATA_FILE.write_text(json.dumps(now_data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        refresh_error = str(exc)

    return JSONResponse({
        "ok": True,
        "saved_to": str(LOCAL_OPTIONS_FILE),
        "mirrored_to_ha_options": saved_ha,
        "refresh_error": refresh_error,
    })


@app.post("/api/options/overlay")
async def options_set_overlay(payload: dict):
    if not isinstance(payload, dict):
        return JSONResponse({"ok": False, "error": "invalid_payload"}, status_code=400)

    overlay = {
        "pathRadiusM": max(30, min(300, int(payload.get("pathRadiusM", 102) or 102))),
        "sectorRadiusM": max(30, min(300, int(payload.get("sectorRadiusM", 110) or 110))),
        "sunRadiusM": max(30, min(300, int(payload.get("sunRadiusM", 95) or 95))),
        "mapZoom": max(14, min(22, int(payload.get("mapZoom", 18) or 18))),
    }

    raw = _load_local_options_raw()
    raw_overlay = raw.get("overlay", {})
    if not isinstance(raw_overlay, dict):
        raw_overlay = {}
    raw_overlay.update(overlay)
    raw["overlay"] = raw_overlay
    _save_local_options_raw(raw)

    ha_raw = _load_options_raw()
    ha_overlay = ha_raw.get("overlay", {})
    if not isinstance(ha_overlay, dict):
        ha_overlay = {}
    ha_overlay.update(overlay)
    ha_raw["overlay"] = ha_overlay
    try:
        _save_options_raw(ha_raw)
        saved_ha = True
    except Exception:
        saved_ha = False

    return JSONResponse({
        "ok": True,
        "overlay": overlay,
        "saved_to": str(LOCAL_OPTIONS_FILE),
        "mirrored_to_ha_options": saved_ha,
    })
