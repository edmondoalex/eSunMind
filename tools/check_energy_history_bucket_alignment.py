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

    missing_ts_values = mod._stat_change_values([{"change": 10}, {"change": 20}, {"change": 30}], 12, 1.0, start, "month")
    if any(missing_ts_values):
        raise SystemExit(f"missing timestamp rows should not fill leading buckets: {missing_ts_values!r}")

    april = tz.localize(datetime(2026, 4, 1, 0, 0, 0))
    missing_ts_days = mod._stat_change_values([{"change": i} for i in range(1, 13)], 30, 1.0, april, "day")
    if any(missing_ts_days):
        raise SystemExit(f"missing timestamp rows should not fill first days: {missing_ts_days!r}")

    marked_rows = [
        {"_bucket_start": "2026-04-01T00:00:00+02:00", "change": 40},
        {"_bucket_start": "2026-05-01T00:00:00+02:00", "change": 50},
        {"_bucket_start": "2026-06-01T00:00:00+02:00", "change": 60},
    ]
    marked_values = mod._stat_change_values(marked_rows, 12, 1.0, start, "month")
    marked_expected = [0.0, 0.0, 0.0, 40.0, 50.0, 60.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    if marked_values != marked_expected:
        raise SystemExit(f"marked monthly rows failed: {marked_values!r}")

    print("energy history bucket alignment ok")


if __name__ == "__main__":
    main()
