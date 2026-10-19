# FilmoraMCP-Server

A local Windows MCP server targeting **Wondershare Filmora X / version 10 and newer**. It detects the selected editor at runtime, chooses compatible shortcut policies and resolves live UI controls instead of requiring one Filmora build. It gives an MCP assistant actual PNG screenshots, accessibility inspection, mouse/keyboard input, project dialogs, timeline commands, clip panels, media libraries, audio tools and export workflows.

Release **0.2.0** includes profiles for X/10 and 11–16, plus conservative adaptation for unknown/future versions. Local editor validation is currently on 13.6.13; other releases have adapter/policy tests and still need live editor validation. See [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md) for the matrix and limits.

This is independent software, not an official Wondershare integration. FilmoraMCP operates the visible editor. It does not expose a private editing API or rewrite undocumented `.wfp` files.

## Product scope

| Item | Current scope |
| --- | --- |
| Filmora target | Filmora X/v10 and newer on Windows; runtime detection selects the applicable profile |
| Version policies | X/10 legacy commands; release profiles for 11–16; conservative unknown/future adaptation |
| MCP clients | Claude Code, Claude Desktop, Codex and Google Antigravity; additional Cursor snippet |
| Interface | Local stdio MCP: 33 tools, 2 resources, 1 editing prompt |
| Catalog | 94 command candidates, 39 named UI targets, 102 feature guides; availability varies by version/context |
| Evidence | 66 automated tests passed; native editor testing on 13.6.13; complete edit/export validation remains outstanding |

The product requirement is broad access to editing features through the live editor. Version-dependent features remain conditional on the installed build, selection, assets, account and license. See the [PRD](PRD.md) for requirements and acceptance criteria, and the [roadmap](docs/ROADMAP.md) for remaining validation work.

## Quickstart

From an extracted source folder, install the environment and preview client registration:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\connect-clients.ps1 -Preview
```

Register the selected clients with `connect-clients.ps1` as described below, then reload their MCP connections. Run diagnostics with:

```powershell
.\.venv\Scripts\python.exe -m filmora_mcp.server --diagnose
```

For stdio MCP, use the absolute Python executable and module argument from `client-configs/`. **The MCP client starts the server**; you normally do not double-click `run.cmd` first. Running `run.cmd` alone waits silently for JSON-RPC on stdin.

### Connect a client

- **Claude Code / Claude Desktop / Codex / Google Antigravity:** run `connect-clients.ps1` to register Filmora in all four local clients. Existing settings and MCP servers are preserved; original configs are backed up under `logs/client-backups`. Repeat runs are safe and do not duplicate the server. Use `connect-clients.ps1 -Preview` to inspect target paths first.
- For a specific client: `.\.venv\Scripts\python.exe scripts\install_clients.py --clients antigravity --apply` (choices: `claude-code`, `claude-desktop`, `codex`, `antigravity`).
- Manual configurations are in `client-configs/claude-code.json`, `claude-desktop.json`, `codex.toml` and `antigravity.json`. Cursor's snippet remains included.

Reload MCP servers or restart each client after registration. Setup installs dependencies/snippets; registration is a separate step. The installer does not change trust/approval policies and refuses to replace a different existing `filmora` server. Claude support here means local Claude Code and Claude Desktop. See [docs/CLIENTS.md](docs/CLIENTS.md) for client paths, verification and troubleshooting.

## Coverage

| Area | Implemented control |
| --- | --- |
| Vision | Window PNG images returned as MCP ImageContent; crop, resize, saved captures; image-to-window coordinate mapping |
| Inspection | Window enumeration, process validation, accessibility names/IDs/types/geometry/focus, searchable control trees |
| Interaction | Single/double/right click, modifier-click, drag, scrolling, bounded shortcut repetition, literal Unicode text |
| UI controls | Focus, invoke, click, set text/value, select list/combo items, toggle, expand/collapse, numeric slider ranges |
| Project/media | Launch, new/open/save/save-as/archive commands, native file-dialog paths, import, media libraries, folders |
| Timeline | Split/trim, ripple delete, duplicate, grouping, insert/overwrite, navigation, markers, zoom, track toolbar |
| Video/color | Open properties, crop/zoom, speed, stabilization, chroma key, tracking, color correction/match and keyframes |
| Audio/text/assets | Audio mixer/recorder, detach/mute, titles, effects, transitions, filters, stickers, captions and AI toolbar targets |
| Export | Open export settings, inspect/configure/start through real controls, inspect progress and verify resulting file size |
| Advanced features | Feature-route catalog for masks, speed ramps, LUTs, denoise, ducking, subtitles, AI and other version-dependent tools |

Run `filmora_status` for detected executable versions and `filmora_capabilities(probe_ui=true)` for version-resolved commands plus exposed/disabled UI targets. `filmora_commands` filters commands by group/text and omits unavailable ones by default. Its `include_unavailable=true` option explains blocked commands.

**Coverage means access through Filmora's UI, not that every feature has a one-call editing API.** Detailed effect parameters, exact clip timing, text styling, export settings and AI operations are configured using live inspected controls or screenshots. Feature guides describe navigation; they do not execute edits. Version checks flag known newer features on older editors; other features remain unverified until inspected. The installed release, shortcut preset, clip selection, layout, assets and license determine availability. Premium/AI features may require login, network processing, credits or downloads; the server does not supply those entitlements.

## Typical request

> Inspect my Filmora project, import these clips, arrange them on the timeline, trim the first clip, add a title and transition, adjust audio, save as a new project, and export a local MP4. Check screenshots after each important change.

The assistant starts with `filmora_status`, `filmora_windows`, `filmora_screenshot` and `filmora_inspect`, acts once, and checks the result. See [docs/WORKFLOWS.md](docs/WORKFLOWS.md) for tool sequences.

## Install or move to another computer

Requires 64-bit Windows, Python 3.11+ and installed Filmora X/10 or newer in an unlocked interactive desktop session. Filmora 9 and earlier are outside the target range. Tested here on Python 3.14.7; this server's OS requirements also apply when an older Filmora release supports older Windows versions.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
```

Setup creates a local virtual environment, installs pinned direct dependencies and regenerates client snippets using the current folder. Do not copy `.venv` between computers; rerun setup. `requirements-lock.txt` records the complete tested environment. For an exact environment, install it with `.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt` and then install this project with `-m pip install --no-deps -e .`.

To use a non-default Filmora executable or custom shortcuts, copy `config.example.json` to `config.local.json`. Set `executable` to the actual Filmora editor EXE, or set `FILMORA_EXE`. `FILMORA_MCP_CONFIG` selects a config file; `FILMORA_CAPTURE_DIR` changes the captures folder. Shortcuts use names like `ctrl+shift+s`; see `filmora_commands`. Configuration is read at server startup.

Version detection uses executable product/file metadata, then adjacent installation version folders. `filmora_major_version` is normally `null` (auto); set it only for an otherwise unknown installation. Conflicts with a detected version are rejected. `ui_target_overrides` supplies exact names/automation IDs and control types for localized or changed layouts. See the compatibility guide for examples. Multiple installations require explicit executable/window selection.

After relocating the project, recreate its virtual environment with `setup.ps1`, then update registrations that still point at the previous folder:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\connect-clients.ps1 -RelocateFrom 'D:\Previous\FilmoraMCP' -Preview
powershell -NoProfile -ExecutionPolicy Bypass -File .\connect-clients.ps1 -RelocateFrom 'D:\Previous\FilmoraMCP'
```

Replace the example with the actual previous project path. Relocation updates only matching Filmora registrations, preserves other server settings, and creates backups. A conflicting command or different arguments are left for review.

## Operation and limits

- Run the server as the same Windows user and integrity level as Filmora. Keep the desktop unlocked and avoid competing mouse/keyboard input.
- Input is scoped to validated Filmora processes. If a modal opens, list windows and select that dialog; reselect the editor when it closes.
- Screenshot/UI observations expire after 60 seconds and are invalidated by input, window selection or changed window geometry. Get a fresh observation after every action. Manual UI changes can also stale an observation: always refresh.
- Screenshots include the selected Filmora window. They may contain project content; `save=True` writes a local capture. Screenshot images are sent to the requesting MCP client. Default `mode="visible"` captures displayed pixels; activate/reveal Filmora first. This refuses capture when another app is foreground. Optional `mode="window"` uses native window capture while obscured, but may show stale GPU surfaces.
- To stop input, move the mouse to desktop `(0,0)` or create an empty `PAUSE` file in this folder. Remove the file/move the pointer to resume. Restarting the server is unnecessary.
- A successful input tool means **dispatched**, not a verified edit. Inspect selection, playhead, dialog and output before claiming completion. Pixel operations cannot promise frame-exact editing without visual verification.
- Native file-dialog helper requires an unambiguous standard filename field. For Filmora custom dialogs, inspect and edit explicit controls instead. The helper refuses an existing Save As destination; ordinary Save commands and explicit UI interactions can still modify existing projects.
- Input does not work from a headless service or locked desktop. Accessibility may be incomplete for Qt canvas items; use screenshots. Capture may fail/appear blank with particular GPU/window states; activate and restore Filmora before retrying. Display scaling and external dialogs require fresh observations.
- The server uses stdio only, opens no listening network port, and has no arbitrary shell/code-execution tool. It does not automate authentication or automatically dismiss save/overwrite/license prompts. General UI controls can still start recording, rendering or online features when instructed; inspect the visible state first.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\smoke_test.py --report logs\smoke-test.json
```

The first command includes protocol, compatibility, client-registration and input-guard tests. The second requires Filmora to be open and checks real MCP status, native screenshots and exposed accessible controls without editing the current project. Use `--no-desktop` for protocol-only checks. See [docs/VALIDATION.md](docs/VALIDATION.md) for actual run results and untested workflows.

## Documentation

- [Product requirements](PRD.md): target users, scope, functional requirements and acceptance criteria.
- [Compatibility](docs/COMPATIBILITY.md): X/10+ version policies, discovery, fallbacks and evidence by release.
- [Client setup](docs/CLIENTS.md): Claude Code/Desktop, Codex and Antigravity registration.
- [Editing workflows](docs/WORKFLOWS.md): observe, act, verify sequences through the editor.
- [Coverage catalog](docs/COVERAGE.md): command candidates, target names and feature routes.
- [Architecture](docs/ARCHITECTURE.md): MCP surface, backend, configuration and data flow.
- [Validation record](docs/VALIDATION.md): completed checks and practical limits.
- [Roadmap](docs/ROADMAP.md) and [changelog](CHANGELOG.md): remaining work and shipped changes.
- [Documentation index](docs/README.md): navigation and documentation maintenance rules.

## Sources

- [Wondershare Windows shortcut reference](https://filmora.wondershare.com/guide/keyboard-shortcuts-on-windows.html)
- [Wondershare Windows user guide](https://filmora.wondershare.com/guide/)
- [Official MCP Python SDK, pinned v1.30.0](https://github.com/modelcontextprotocol/python-sdk/tree/v1.30.0)
- [pywinauto UI Automation documentation](https://pywinauto.readthedocs.io/en/latest/)

MIT licensed. Wondershare and Filmora are trademarks of their respective owners.
