import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_backend():
    Path("/app/static/assets").mkdir(parents=True, exist_ok=True)
    Path("/app/static/energy-dashboard").mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location("sunmind_main", ROOT / "e-sunmind" / "backend" / "main.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def main():
    mod = load_backend()
    states = {
        "sensor.privato_load": (111.0, "W"),
        "sensor.sas_load": (222.0, "W"),
        "sensor.privato_pv": (1000.0, "W"),
        "sensor.sas_pv": (2000.0, "W"),
        "sensor.privato_grid": (10.0, "W"),
        "sensor.sas_grid": (20.0, "W"),
        "sensor.privato_batt": (30.0, "W"),
        "sensor.sas_batt": (40.0, "W"),
        "sensor.privato_soc": (55.0, "%"),
        "sensor.sas_soc": (66.0, "%"),
    }

    def fake_fetch(entity_id):
        value, unit = states[str(entity_id)]
        return {
            "ok": True,
            "entity_id": entity_id,
            "state": str(value),
            "value": value,
            "unit": unit,
            "attributes": {"unit_of_measurement": unit},
        }

    mod._fetch_ha_entity_state = fake_fetch
    cfg = {
        "energy": {
            "enabled": True,
            "selected_site_id": "sas",
            "home_power_entity_id": "sensor.sas_load",
            "pv_power_entity_id": "sensor.sas_pv",
            "grid_power_entity_id": "sensor.sas_grid",
            "battery_power_entity_id": "sensor.sas_batt",
            "battery_soc_entity_id": "sensor.sas_soc",
            "sites": [
                {
                    "id": "privato",
                    "name": "PRIVATO",
                    "home_power_entity_id": "sensor.privato_load",
                    "pv_power_entity_id": "sensor.privato_pv",
                    "grid_power_entity_id": "sensor.privato_grid",
                    "battery_power_entity_id": "sensor.privato_batt",
                    "battery_soc_entity_id": "sensor.privato_soc",
                },
                {
                    "id": "sas",
                    "name": "SAS",
                    "home_power_entity_id": "sensor.sas_load",
                    "pv_power_entity_id": "sensor.sas_pv",
                    "grid_power_entity_id": "sensor.sas_grid",
                    "battery_power_entity_id": "sensor.sas_batt",
                    "battery_soc_entity_id": "sensor.sas_soc",
                },
            ],
        }
    }

    privato = mod._build_energy_snapshot(cfg, "privato", include_sites=False)
    sas = mod._build_energy_snapshot(cfg, "sas", include_sites=False)

    assert privato["site_id"] == "privato"
    assert sas["site_id"] == "sas"
    assert privato["normalized"]["home_power_w"] == 111.0
    assert sas["normalized"]["home_power_w"] == 222.0
    assert privato["normalized"]["pv_power_w"] == 1000.0
    assert sas["normalized"]["pv_power_w"] == 2000.0
    assert privato["entities"]["home_power_entity_id"]["entity_id"] == "sensor.privato_load"
    assert sas["entities"]["home_power_entity_id"]["entity_id"] == "sensor.sas_load"
    print("OK energy site isolation")


if __name__ == "__main__":
    main()
