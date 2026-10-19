from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_config() -> dict:
    defaults = {
        "executable": "",
        "capture_dir": str(ROOT / "captures"),
        "observation_ttl_seconds": 60,
        "max_text_length": 20000,
        "shortcut_overrides": {},
        "filmora_major_version": None,
        "ui_target_overrides": {},
    }
    path = Path(os.environ.get("FILMORA_MCP_CONFIG", ROOT / "config.local.json"))
    if path.exists():
        defaults.update(json.loads(path.read_text(encoding="utf-8-sig")))
    if os.environ.get("FILMORA_EXE"):
        defaults["executable"] = os.environ["FILMORA_EXE"]
    if os.environ.get("FILMORA_CAPTURE_DIR"):
        defaults["capture_dir"] = os.environ["FILMORA_CAPTURE_DIR"]
    ttl = float(defaults["observation_ttl_seconds"])
    if not 1 <= ttl <= 300:
        raise ValueError("observation_ttl_seconds must be between 1 and 300")
    if not isinstance(defaults["shortcut_overrides"], dict):
        raise ValueError("shortcut_overrides must be an object")
    from .compatibility import parse_major
    manual = defaults["filmora_major_version"]
    if manual is not None and (parse_major(manual) is None or parse_major(manual) < 10):
        raise ValueError("filmora_major_version must be null (auto), X, or a version >=10")
    selectors = defaults["ui_target_overrides"]
    if not isinstance(selectors, dict):
        raise ValueError("ui_target_overrides must be an object")
    for target, entries in selectors.items():
        if not isinstance(entries, list) or not entries:
            raise ValueError(f"UI target {target} must contain a nonempty selector list")
        for entry in entries:
            if not isinstance(entry, dict) or not (entry.get("name") or entry.get("automation_id")):
                raise ValueError("Selectors require an exact name or automation_id")
            if not set(entry) <= {"name", "automation_id", "control_type"} or not entry.get("control_type"):
                raise ValueError("Selectors require control_type and support only name/automation_id/control_type")
            if any(not isinstance(v, str) or not v for v in entry.values()):
                raise ValueError("Selector values must be nonempty strings")
    return defaults
