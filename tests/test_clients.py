import importlib.util
import json
from pathlib import Path
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("install_clients", ROOT / "scripts" / "install_clients.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


@pytest.mark.parametrize("client", installer.CLIENTS)
def test_registration_preserves_existing_settings_and_is_idempotent(client, tmp_path):
    if client == "codex":
        old = b'# keep this comment\nmodel = "configured-model"\n[mcp_servers.existing]\ncommand = "old.exe"\n'
        key, parser = "mcp_servers", tomllib.loads
    else:
        old = json.dumps({"preferences": {"keep": True}, "mcpServers": {"existing": {"command": "old.exe"}}}).encode()
        key, parser = "mcpServers", json.loads
    encoded, status = installer.prepare(client, old, tmp_path)
    before, after = parser(old.decode()), parser(encoded.decode())
    assert status == "added"
    assert after[key]["existing"] == before[key]["existing"]
    assert {k:v for k,v in before.items() if k != key} == {k:v for k,v in after.items() if k != key}
    assert installer.prepare(client, encoded, tmp_path) == (None, "already-configured")
    if client == "codex":
        assert encoded.startswith(b"# keep this comment")


def test_conflicting_filmora_entry_is_preserved():
    old = json.dumps({"mcpServers": {"filmora": {"command": "some-other-server.exe"}}}).encode()
    with pytest.raises(ValueError, match="different filmora"):
        installer.prepare("antigravity", old)


def test_preview_writes_nothing_and_apply_creates_exact_backup(tmp_path):
    path = tmp_path / "client.json"
    old = b'{"mcpServers":{},"other":1}'
    path.write_bytes(old)
    backups = tmp_path / "backups"
    installer.install("claude-desktop", path, root=tmp_path, backup_dir=backups)
    assert path.read_bytes() == old and not backups.exists()
    result = installer.install("claude-desktop", path, apply=True, root=tmp_path, backup_dir=backups)
    assert Path(result["backup"]).read_bytes() == old
    assert "filmora" in json.loads(path.read_text())["mcpServers"]


def test_invalid_client_config_is_not_overwritten(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_bytes(b"{broken")
    with pytest.raises(ValueError):
        installer.install("antigravity", path, apply=True, root=tmp_path)
    assert path.read_bytes() == b"{broken"


def test_antigravity_path_uses_current_config_location(tmp_path):
    paths = installer.locations(tmp_path, tmp_path / "AppData" / "Roaming")
    assert paths["antigravity"] == tmp_path / ".gemini" / "config" / "mcp_config.json"


@pytest.mark.parametrize("client", installer.CLIENTS)
def test_explicit_relocation_preserves_other_servers_and_custom_fields(client, tmp_path):
    old_root, new_root = tmp_path / "old", tmp_path / "new"
    old_entry = {**installer.entry(client, old_root), "env":{"KEEP":"yes"}, "cwd":str(old_root)}
    if client == "codex":
        old = ('# retained\nmodel = "existing-model"\n[mcp_servers.filmora]\ncommand = '
               + json.dumps(old_entry["command"]) + '\nargs = ["-m", "filmora_mcp.server"]\n'
               + 'cwd = ' + json.dumps(str(old_root)) + '\ntool_timeout_sec = 150\n'
               + '[mcp_servers.filmora.env]\nKEEP = "yes"\n[mcp_servers.other]\ncommand = "other.exe"\n').encode()
        parser, key = tomllib.loads, "mcp_servers"
    else:
        old = json.dumps({"mcpServers":{"filmora":old_entry,"other":{"command":"other.exe"}},"keep":True}).encode()
        parser, key = json.loads, "mcpServers"
    encoded, status = installer.prepare(client, old, new_root, relocate_from=old_root)
    before, after = parser(old.decode()), parser(encoded.decode())
    assert status == "relocated"
    assert after[key]["filmora"]["command"] == installer.entry(client,new_root)["command"]
    assert after[key]["filmora"]["cwd"] == str(new_root)
    assert after[key]["filmora"]["env"] == {"KEEP":"yes"}
    assert after[key]["other"] == before[key]["other"]
    assert installer.prepare(client, encoded, new_root, relocate_from=old_root) == (None,"already-configured")
    if client == "codex":
        assert after[key]["filmora"]["tool_timeout_sec"] == 150
        assert encoded.startswith(b"# retained")


def test_relocation_refuses_an_unrelated_source(tmp_path):
    old = json.dumps({"mcpServers":{"filmora":installer.entry("claude-code",tmp_path/"other")}}).encode()
    with pytest.raises(ValueError,match="does not match"):
        installer.prepare("claude-code",old,tmp_path/"new",relocate_from=tmp_path/"old")


def test_relocation_refuses_custom_arguments(tmp_path):
    old_entry = installer.entry("claude-code",tmp_path/"old")
    old_entry["args"] = ["-m","different.module"]
    old = json.dumps({"mcpServers":{"filmora":old_entry}}).encode()
    with pytest.raises(ValueError,match="arguments differ"):
        installer.prepare("claude-code",old,tmp_path/"new",relocate_from=tmp_path/"old")
