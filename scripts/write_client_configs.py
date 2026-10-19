"""Generate client-specific snippets; does not register them globally."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
folder = root / "client-configs"
folder.mkdir(exist_ok=True)
exe = str(root / ".venv" / "Scripts" / "python.exe")
server = {"command": exe, "args": ["-m", "filmora_mcp.server"]}
for filename in ["claude-desktop.json", "cursor.json", "antigravity.json"]:
    (folder / filename).write_text(json.dumps({"mcpServers": {"filmora": server}}, indent=2) + "\n", encoding="utf-8")
(folder / "claude-code.json").write_text(
    json.dumps({"mcpServers": {"filmora": {"type": "stdio", **server}}}, indent=2) + "\n", encoding="utf-8")
(folder / "codex.toml").write_text(
    '[mcp_servers.filmora]\ncommand = ' + json.dumps(exe)
    + '\nargs = ["-m", "filmora_mcp.server"]\nstartup_timeout_sec = 60\ntool_timeout_sec = 120\n', encoding="utf-8")
print("Generated client snippets in", folder)
