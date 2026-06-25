#!/usr/bin/env python3
"""Local Livoltek API feasibility probe.

This script intentionally does not publish MQTT, touch Home Assistant, or map
sensor fields. It only verifies authentication/probe endpoints and stores raw
responses for later inspection.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, build_opener


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SECRETS = ROOT / "e-sunmind" / "livoltek_secrets.json"
DEFAULT_OUTPUT = ROOT / "livoltek_probe_output.json"


COMMON_LOGIN_PATHS = ("/api/login", "/login")
COMMON_TOKEN_PATHS = ("/api/token", "/token")
COMMON_PROBE_PATHS = ("/", "/status", "/api/status")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Secrets file not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from None
    if not isinstance(payload, dict):
        raise SystemExit(f"Secrets file must contain a JSON object: {path}")
    return payload


def _clean_base_url(value: Any) -> str:
    base_url = str(value or "").strip()
    if not base_url or base_url == "https://example.livoltek.com":
        raise SystemExit("Set base_url in livoltek_secrets.json before running the probe.")
    if not base_url.startswith(("http://", "https://")):
        base_url = "https://" + base_url
    return base_url.rstrip("/") + "/"


def _unique(values: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _render_path(path: str, cfg: dict[str, Any]) -> str:
    replacements = {
        "plant_id": str(cfg.get("plant_id") or ""),
        "device_id": str(cfg.get("device_id") or ""),
    }
    try:
        return path.format(**replacements)
    except Exception:
        return path


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def _login_payloads(username: str, password: str, cfg: dict[str, Any], path: str) -> list[dict[str, Any]]:
    mode = str(cfg.get("login_payload") or "").strip().lower()
    payloads: list[dict[str, Any]] = []
    if mode in {"livoltek_customer", "livoltek", ""} or "login/customer" in path:
        payloads.append(
            {
                "login_account": username,
                "password": hashlib.md5(password.encode("utf-8")).hexdigest(),
                "account_type": "account",
                "language": str(cfg.get("language") or "en"),
                "device_type": 0,
            }
        )
    if mode in {"generic", ""}:
        payloads.append({"username": username, "password": password})
    return payloads


def _short_text(value: str, max_len: int = 500) -> str:
    text = " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split())
    return text[:max_len] + ("..." if len(text) > max_len else "")


def _redact_text(value: str) -> str:
    text = str(value or "")
    sensitive_keys = (
        "password",
        "token",
        "access_token",
        "accessToken",
        "id_token",
        "idToken",
        "jwt",
        "authorization",
    )
    for key in sensitive_keys:
        text = re.sub(
            rf'("{re.escape(key)}"\s*:\s*")[^"]+(")',
            rf'\1***\2',
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            rf"({re.escape(key)}\s*[:=]\s*)[^\s,;]+",
            rf"\1***",
            text,
            flags=re.IGNORECASE,
        )
    text = re.sub(r"(Bearer\s+)[A-Za-z0-9._~+/=-]+", r"\1***", text, flags=re.IGNORECASE)
    return text


def _decode_body(data: bytes) -> tuple[Any, str]:
    text = data.decode("utf-8", errors="replace")
    try:
        return json.loads(text), text
    except Exception:
        return None, text


def _request(
    opener: Any,
    method: str,
    url: str,
    *,
    json_payload: dict[str, Any] | None = None,
    token: str = "",
    timeout: int = 20,
) -> dict[str, Any]:
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "e-sunmind-livoltek-probe/1.0",
        "language": "en",
    }
    data = None
    if json_payload is not None:
        data = _json_bytes(json_payload)
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = Request(url, data=data, headers=headers, method=method.upper())
    started = datetime.now(timezone.utc).isoformat()
    try:
        with opener.open(req, timeout=timeout) as resp:
            raw = resp.read()
            parsed, text = _decode_body(raw)
            return {
                "ok": True,
                "started_at": started,
                "method": method.upper(),
                "url": url,
                "status": int(resp.status),
                "reason": getattr(resp, "reason", ""),
                "headers": dict(resp.headers.items()),
                "json": parsed,
                "text": text,
                "short": _short_text(text),
            }
    except HTTPError as exc:
        raw = exc.read()
        parsed, text = _decode_body(raw)
        return {
            "ok": False,
            "started_at": started,
            "method": method.upper(),
            "url": url,
            "status": int(exc.code),
            "reason": str(exc.reason),
            "headers": dict(exc.headers.items()) if exc.headers else {},
            "json": parsed,
            "text": text,
            "short": _short_text(text),
        }
    except URLError as exc:
        return {
            "ok": False,
            "started_at": started,
            "method": method.upper(),
            "url": url,
            "status": None,
            "reason": str(exc.reason),
            "headers": {},
            "json": None,
            "text": "",
            "short": str(exc.reason),
        }
    except Exception as exc:
        return {
            "ok": False,
            "started_at": started,
            "method": method.upper(),
            "url": url,
            "status": None,
            "reason": repr(exc),
            "headers": {},
            "json": None,
            "text": "",
            "short": repr(exc),
        }


def _find_token(value: Any) -> str:
    token_keys = {
        "token",
        "access_token",
        "accessToken",
        "id_token",
        "idToken",
        "jwt",
        "authorization",
    }
    if isinstance(value, dict):
        for key, item in value.items():
            if key in token_keys and isinstance(item, str) and item.strip():
                raw = item.strip()
                return raw.removeprefix("Bearer ").strip()
        for item in value.values():
            found = _find_token(item)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _find_token(item)
            if found:
                return found
    return ""


def _print_result(label: str, result: dict[str, Any]) -> None:
    status = result.get("status")
    status_text = str(status) if status is not None else "ERR"
    print(f"[{label}] {result.get('method')} {result.get('url')}")
    print(f"  status={status_text} reason={result.get('reason')}")
    if result.get("short"):
        print(f"  response={_redact_text(result['short'])}")


def _join(base_url: str, path: str) -> str:
    return urljoin(base_url, path.lstrip("/"))


def run_probe(secrets_path: Path, output_path: Path) -> int:
    cfg = _load_json(secrets_path)
    base_url = _clean_base_url(cfg.get("base_url"))
    timeout = int(cfg.get("timeout_seconds") or 20)
    opener = build_opener()

    username = str(cfg.get("username") or "").strip()
    password = str(cfg.get("password") or "")
    token = str(cfg.get("token") or "").strip()

    output: dict[str, Any] = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "secrets_file": str(secrets_path),
        "results": [],
        "token_source": "configured" if token else "",
    }

    if username and password and not token:
        login_candidates = _unique([str(cfg.get("login_path") or ""), *COMMON_LOGIN_PATHS])
        for path in login_candidates:
            url = _join(base_url, path)
            for payload in _login_payloads(username, password, cfg, path):
                result = _request(opener, "POST", url, json_payload=payload, timeout=timeout)
                result["label"] = "login"
                result["path"] = path
                result["payload_shape"] = sorted(payload.keys())
                output["results"].append(result)
                _print_result("login", result)
                token = _find_token(result.get("json"))
                if token:
                    output["token_source"] = f"login:{path}"
                    break
            if token:
                break

    if username and password and not token:
        token_candidates = _unique([str(cfg.get("token_path") or ""), *COMMON_TOKEN_PATHS])
        for path in token_candidates:
            url = _join(base_url, path)
            payload = {"username": username, "password": password}
            result = _request(opener, "POST", url, json_payload=payload, timeout=timeout)
            result["label"] = "token"
            result["path"] = path
            output["results"].append(result)
            _print_result("token", result)
            token = _find_token(result.get("json"))
            if token:
                output["token_source"] = f"token:{path}"
                break

    configured_probe_paths = cfg.get("probe_paths")
    if not isinstance(configured_probe_paths, list):
        configured_probe_paths = []
    probe_paths = _unique([*map(str, configured_probe_paths), *COMMON_PROBE_PATHS])
    for raw_path in probe_paths:
        path = _render_path(raw_path, cfg)
        url = _join(base_url, path)
        result = _request(opener, "GET", url, token=token, timeout=timeout)
        result["label"] = "probe"
        result["path"] = raw_path
        output["results"].append(result)
        _print_result("probe", result)

    probe_requests = cfg.get("probe_requests")
    if isinstance(probe_requests, list):
        for idx, item in enumerate(probe_requests, 1):
            if not isinstance(item, dict):
                continue
            method = str(item.get("method") or "GET").upper()
            path = _render_path(str(item.get("path") or ""), cfg)
            if not path:
                continue
            body = item.get("body")
            if not isinstance(body, dict):
                body = None
            url = _join(base_url, path)
            result = _request(opener, method, url, json_payload=body, token=token, timeout=timeout)
            result["label"] = "probe_request"
            result["path"] = path
            result["probe_request_index"] = idx
            output["results"].append(result)
            _print_result(f"probe_request#{idx}", result)

    output["finished_at"] = datetime.now(timezone.utc).isoformat()
    output["token_acquired"] = bool(token)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nFull raw output saved to: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe Livoltek API feasibility.")
    parser.add_argument("--secrets", type=Path, default=DEFAULT_SECRETS, help="Path to livoltek_secrets.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to save raw probe output JSON")
    args = parser.parse_args()
    return run_probe(args.secrets.resolve(), args.output.resolve())


if __name__ == "__main__":
    sys.exit(main())
