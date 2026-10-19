"""Register FilmoraMCP without changing unrelated servers or permission policies.

Preview by default. --apply writes validated configs atomically with backups.
No credentials or full client configurations are printed to stdout.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import tomllib
import uuid

ROOT = Path(__file__).resolve().parents[1]
CLIENTS = ("claude-code", "claude-desktop", "codex", "antigravity")


def locations(home: Path, appdata: Path) -> dict[str, Path]:
    return {
        "claude-code": home / ".claude.json",
        "claude-desktop": appdata / "Claude" / "claude_desktop_config.json",
        "codex": home / ".codex" / "config.toml",
        "antigravity": home / ".gemini" / "config" / "mcp_config.json",
    }


def entry(client: str, root=ROOT) -> dict:
    base = {"command": str(root / ".venv" / "Scripts" / "python.exe"),
            "args": ["-m", "filmora_mcp.server"]}
    return {"type": "stdio", **base} if client == "claude-code" else base


def same_path(left, right):
    if not isinstance(left, str):
        return False
    return os.path.normcase(os.path.abspath(left)) == os.path.normcase(os.path.abspath(right))


def relocate_entry(client, text, doc, servers, desired, root, relocate_from):
    existing = servers["filmora"]
    old_command = Path(relocate_from) / ".venv" / "Scripts" / "python.exe"
    if not isinstance(existing, dict) or not same_path(existing.get("command"), old_command):
        raise ValueError("Existing filmora command does not match --relocate-from; preserving it")
    if existing.get("args") != desired["args"] or existing.get("type", "stdio") != "stdio":
        raise ValueError("Existing filmora transport/arguments differ; preserving it for manual review")
    updated = {**existing, **desired}
    if same_path(existing.get("cwd"), relocate_from):
        updated["cwd"] = str(root)
    key = "mcp_servers" if client == "codex" else "mcpServers"
    expected = {**doc, key: {**servers, "filmora": updated}}
    if client == "codex":
        section = re.search(r"(?m)^\[mcp_servers\.filmora\][ \t]*(?:\r?\n|$)", text)
        if section is None:
            raise ValueError("Filmora TOML table uses an unsupported layout; original preserved")
        next_section = re.search(r"(?m)^\[", text[section.end():])
        end = section.end() + next_section.start() if next_section else len(text)
        body = text[section.end():end]
        for field in ("command", "cwd"):
            if updated.get(field) == existing.get(field):
                continue
            body, count = re.subn(r"(?m)^([ \t]*" + field + r"[ \t]*=[ \t]*)[^\r\n]*",
                                  lambda m: m[1] + json.dumps(updated[field]), body)
            if count != 1:
                raise ValueError(f"Cannot safely relocate TOML {field}; original preserved")
        result = text[:section.end()] + body + text[end:]
        if tomllib.loads(result) != expected:
            raise ValueError("TOML relocation would change unrelated settings; original preserved")
    else:
        result = json.dumps(expected, ensure_ascii=False, indent=2) + "\n"
        if json.loads(result) != expected:
            raise ValueError("JSON relocation verification failed")
    return result.encode("utf-8"), "relocated"


def prepare(client: str, original: bytes | None, root=ROOT, relocate_from=None):
    text = original.decode("utf-8-sig") if original is not None else ""
    doc = (tomllib.loads(text) if client == "codex" else json.loads(text)) if text.strip() else {}
    if not isinstance(doc, dict):
        raise ValueError("Client configuration must be an object")
    key = "mcp_servers" if client == "codex" else "mcpServers"
    servers = doc.get(key, {})
    if not isinstance(servers, dict):
        raise ValueError(f"{key} must be an object")
    desired = entry(client, root)
    if "filmora" in servers:
        existing = servers["filmora"]
        if isinstance(existing, dict) and all(existing.get(k) == v for k, v in desired.items()):
            return None, "already-configured"
        if relocate_from is not None:
            return relocate_entry(client, text, doc, servers, desired, root, relocate_from)
        raise ValueError("A different filmora server already exists; preserving it. Review its entry before registering.")
    if client == "codex":
        addition = ('\n[mcp_servers.filmora]\ncommand = ' + json.dumps(desired["command"])
                    + '\nargs = ["-m", "filmora_mcp.server"]\nstartup_timeout_sec = 60\ntool_timeout_sec = 120\n')
        result = text.rstrip() + "\n" + addition
        parsed = tomllib.loads(result)  # also rejects incompatible inline/duplicate tables
        expected = {**doc, key: {**servers, "filmora": {**desired, "startup_timeout_sec": 60, "tool_timeout_sec": 120}}}
        if parsed != expected:
            raise ValueError("TOML merge would change unrelated settings")
    else:
        expected = {**doc, key: {**servers, "filmora": desired}}
        result = json.dumps(expected, ensure_ascii=False, indent=2) + "\n"
        if json.loads(result) != expected:
            raise ValueError("JSON merge verification failed")
    return result.encode("utf-8"), "added"


def install(client: str, path: Path, apply=False, backup_dir=None, root=ROOT, relocate_from=None):
    before = path.read_bytes() if path.exists() else None
    updated, status = prepare(client, before, root, relocate_from)
    result = {"client": client, "config": str(path), "status": status if apply else f"preview:{status}"}
    if updated is None or not apply:
        return result
    # Compare again immediately before mutation to avoid silently overwriting an app's concurrent update.
    current = path.read_bytes() if path.exists() else None
    if current != before:
        raise RuntimeError("Configuration changed while preparing the update; retry")
    backup = None
    if before is not None:
        backup_dir = Path(backup_dir or root / "logs" / "client-backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = backup_dir / f"{client}-{stamp}-{uuid.uuid4().hex[:8]}{path.suffix}"
        with backup.open("xb") as out:
            out.write(before)
        result["backup"] = str(backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".filmora-", suffix=".tmp", delete=False) as out:
            temp = Path(out.name)
            out.write(updated)
            out.flush()
            os.fsync(out.fileno())
        if path.exists():
            shutil.copymode(path, temp)
        current = path.read_bytes() if path.exists() else None
        if current != before:
            raise RuntimeError("Configuration changed before commit; original preserved")
        os.replace(temp, path)
        temp = None
    finally:
        if temp is not None and temp.exists():
            temp.unlink()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clients", nargs="+", choices=CLIENTS, default=list(CLIENTS))
    parser.add_argument("--apply", action="store_true", help="Write configs after creating backups; otherwise preview")
    parser.add_argument("--relocate-from", type=Path, help="Update only an existing Filmora registration matching this former project folder")
    args = parser.parse_args()
    if args.relocate_from is not None and not args.relocate_from.is_absolute():
        parser.error("--relocate-from must be an absolute project path")
    if not (ROOT / ".venv" / "Scripts" / "python.exe").is_file():
        parser.error("Run setup.ps1 first: virtual environment is missing")
    paths = locations(Path.home(), Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")))
    if os.environ.get("CODEX_HOME"):
        paths["codex"] = Path(os.environ["CODEX_HOME"]) / "config.toml"
    # If a legacy Antigravity config exists, preserve compatibility with that installation as well.
    targets = [(c, paths[c]) for c in dict.fromkeys(args.clients)]
    legacy = Path.home() / ".gemini" / "antigravity" / "mcp_config.json"
    if "antigravity" in args.clients and legacy.is_file():
        targets.append(("antigravity", legacy))
    results = []
    for client, path in targets:
        try:
            results.append(install(client, path, apply=args.apply, relocate_from=args.relocate_from))
        except Exception as exc:
            results.append({"client": client, "config": str(path), "status": "error", "error": str(exc)})
    print(json.dumps({"applied": args.apply, "results": results,
                      "next": "Reload MCP servers or restart clients. No approval/trust policies were changed."}, indent=2))
    return 1 if any(r["status"] == "error" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
