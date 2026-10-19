# Claude, Codex and Antigravity

FilmoraMCP uses local **stdio MCP** and standard PNG image content. Each client launches the same installed Python server. No HTTP proxy, API key or separate long-running service is required.

The editor target is Windows Filmora X/v10 and newer. Client registration is independent of the installed editor version; runtime detection selects its compatibility policy. See [COMPATIBILITY.md](COMPATIBILITY.md) for the version matrix and [PRD.md](../PRD.md) for requirements and acceptance limits.

## Register

From the FilmoraMCP directory:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\connect-clients.ps1 -Preview
powershell -NoProfile -ExecutionPolicy Bypass -File .\connect-clients.ps1
```

This registers Claude Code, Claude Desktop, Codex and Antigravity. Use `scripts/install_clients.py --clients <client> --apply` to select fewer clients. The Python installer previews by default; the PowerShell wrapper applies by default. A different existing Filmora launch command is normally preserved and reported as a conflict.

After moving the project, rebuild its virtual environment and regenerate snippets using `setup.ps1`. Then use `connect-clients.ps1 -RelocateFrom 'D:\Previous\FilmoraMCP' -Preview` to inspect the proposed updates and repeat without `-Preview` to apply them. Replace the example path with the original project folder. Only the matching old Python command with the expected Filmora module arguments is relocated. Custom settings, unrelated servers and the existing timeout values are retained; an explicitly matching old `cwd` is also updated. Original configs are backed up before writing.

| Client | Configuration target | Snippet | Verification |
| --- | --- | --- | --- |
| Claude Code | `%USERPROFILE%\.claude.json`, user-scoped `mcpServers.filmora` | `client-configs/claude-code.json` | `claude mcp get filmora`, then `/mcp` in a new session |
| Claude Desktop | `%APPDATA%\Claude\claude_desktop_config.json` | `client-configs/claude-desktop.json` | Restart Claude Desktop and inspect its local MCP server status |
| Codex CLI/app/IDE | `%USERPROFILE%\.codex\config.toml` (`CODEX_HOME` honored) | `client-configs/codex.toml` | `codex mcp get filmora --json`; reload MCP or start a new chat |
| Google Antigravity | `%USERPROFILE%\.gemini\config\mcp_config.json` | `client-configs/antigravity.json` | Refresh MCP Servers or restart Antigravity, then inspect `filmora` |

Antigravity's current documented global path is `.gemini/config/mcp_config.json`; workspace configurations use `.agents/mcp_config.json`. If an existing legacy `.gemini/antigravity/mcp_config.json` is found, the installer also adds Filmora there. It does not create a second legacy configuration unnecessarily. [Official Antigravity MCP documentation](https://www.antigravity.google/docs/mcp)

Claude Code user-scoped servers are stored under the top-level `mcpServers` key in `.claude.json`. The generated entry explicitly sets `type: stdio`; the CLI can health-check it with `claude mcp get filmora`. [Official Claude Code MCP documentation](https://code.claude.com/docs/en/mcp)

Codex uses `mcp_servers.filmora` in TOML. The supplied timeouts allow 60 seconds for startup and 120 seconds per tool, accommodating native accessibility reads. [Official Codex MCP documentation](https://developers.openai.com/codex/mcp)

## Preservation and backups

The installer merges only Filmora's entry, validates JSON/TOML before writing, preserves existing Codex comments, and uses atomic replacement. It checks for concurrent changes before committing. Original files are saved under `logs/client-backups` with unique names. Backups can contain private settings: they are excluded from source ZIPs and Git. Existing unrelated servers, environment variables, client settings and permission policies are preserved.

To undo, remove just the Filmora entry through the client or its configuration. Backups are available for recovery; restoring a whole backup after later client changes could discard those changes.

## Start editing

After reload, ask:

> Use FilmoraMCP to inspect my current editor. Run filmora_status, select Filmora, activate it, and show filmora_state. Explain the current timeline before changing anything.

Then provide explicit source media paths, desired changes, a new project filename and an export destination. All clients can discover the same 33 tools. Screenshots are standard MCP images; whether a client displays them directly or passes them to its model depends on that client's image support/settings.

Use one client at a time to operate Filmora. Multiple connected clients can inspect the server, but simultaneous mouse/keyboard editing shares one desktop and can invalidate observations.

## Troubleshooting

- **Server missing:** reload MCP servers/new session; confirm the correct configuration path and matching entry name `filmora`.
- **Python not found:** rerun `setup.ps1` from the actual project location, then regenerate snippets. Review/update any old Filmora registration after moving the folder.
- **Connected but input/capture fails:** keep Filmora and the MCP process on the same unlocked Windows desktop, at the same privilege level. Default screenshots require Filmora foreground.
- **Claude scope precedence:** a project/local entry named `filmora` can override the user entry; inspect `/mcp` if a different command appears.
- **Antigravity available-tool limits:** enable Filmora's tools in the client's MCP manager if needed; the installer does not change disabled-tool lists or client permission settings.
- **Tool errors after input:** inspect again before retrying. An input error can leave a partially completed UI action.

## Validation scope

Automated configuration tests verify preservation, idempotency, conflicts, backup contents and malformed-file refusal. Standard MCP initialization, discovery, resources, prompts and image responses were validated with the official SDK. Configuration registration and a successful Claude Code CLI health-check are distinct from a complete editing run inside every client. No AI-model chat was launched for validation and no current video project was edited.

Run `.\.venv\Scripts\python.exe scripts\check_clients.py --report logs\client-validation.json` to verify all four actual saved launch entries through MCP without editing Filmora. This check works even when the host apps have not yet reloaded.
