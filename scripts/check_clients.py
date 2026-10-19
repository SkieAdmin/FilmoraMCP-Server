"""Check each saved client configuration by launching its Filmora entry over stdio.

This tests the configured launch command with the official MCP SDK, not each
client's model/image renderer. Does not start a model chat or edit a project.
"""
import argparse
import asyncio
import importlib.util
import json
import os
from pathlib import Path
import sys
import tomllib

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", ROOT / "scripts" / "install_clients.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


async def check(client, path):
    text = path.read_text(encoding="utf-8-sig")
    doc = tomllib.loads(text) if client == "codex" else json.loads(text)
    key = "mcp_servers" if client == "codex" else "mcpServers"
    entry = doc[key]["filmora"]
    params = StdioServerParameters(command=entry["command"], args=entry.get("args", []),
                                   env=entry.get("env"), cwd=str(ROOT.parent))
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()
            caps = await session.call_tool("filmora_capabilities", {})
            assert not caps.isError, "Capabilities tool failed"
            cap_data = json.loads(next(c.text for c in caps.content if c.type == "text"))
            assert cap_data["minimum_major"] == 10
            assert len(tools.tools) == 33
            resources = await session.list_resources()
            prompts = await session.list_prompts()
            return {"client": client, "config": str(path), "status": "stdio-roundtrip-passed",
                    "protocol": initialized.protocolVersion, "tools": len(tools.tools),
                    "resources": len(resources.resources), "prompts": len(prompts.prompts),
                    "minimum_filmora_major": cap_data["minimum_major"], "profile": cap_data["profile"]}


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    paths = installer.locations(Path.home(), Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")))
    if os.environ.get("CODEX_HOME"):
        paths["codex"] = Path(os.environ["CODEX_HOME"]) / "config.toml"
    results = []
    for client, path in paths.items():
        try:
            results.append(await check(client, path))
        except Exception as exc:
            results.append({"client": client, "status": "failed", "error": str(exc)})
    result = {"results": results, "scope": "Actual config launch commands validated through official MCP SDK; host app UI reload still required."}
    encoded = json.dumps(result, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 1 if any(r["status"] == "failed" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
