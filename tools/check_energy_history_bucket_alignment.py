import importlib.util
from datetime import datetime
from pathlib import Path

import pytz


ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = ROOT / "e-sunmind" / "backend" / "main.py"


def load_backend_module():
    spec = importlib.util.spec_from_file_location("sunmind_backend_main", MAIN_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def main():
    mod = load_backend_module()
    tz = pytz.timezone("Europe/Rome")
    start = tz.localize(datetime(2026, 1, 1, 0, 0, 0))
    rows = [
        {"start": "2026-02-01T00:00:00+01:00", "change": 20},
        {"start": "2026-04-01T00:00:00+02:00", "change": 40},
        {"start": "2026-06-01T00:00:00+02:00", "change": 60},
    ]
    values = mod._stat_change_values(rows, 12, 1.0, start, "month")
    expected = [0.0, 20.0, 0.0, 40.0, 0.0, 60.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    if values != expected:
        raise SystemExit(f"bucket alignment failed: {values!r}")
    print("energy history bucket alignment ok")


if __name__ == "__main__":
    main()
