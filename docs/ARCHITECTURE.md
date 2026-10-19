# Architecture

FilmoraMCP 0.2.0 is a local Windows stdio MCP server targeting Filmora X/v10 and newer. Product requirements are in [PRD.md](../PRD.md); version policies and their evidence are in [COMPATIBILITY.md](COMPATIBILITY.md).

## Components

| Component | Responsibility |
| --- | --- |
| `src/filmora_mcp/server.py` | FastMCP tools, resources, editing prompt, result formatting and serialized tool calls |
| `src/filmora_mcp/backend.py` | Executable/window discovery, version reads, screenshots, UI Automation, native input, observations and guards |
| `src/filmora_mcp/compatibility.py` | Version parsing/profiles, legacy/modern/shared command policies, feature boundaries and selector/fallback candidates |
| `src/filmora_mcp/catalog.py` | Command candidates, named UI targets, guided feature routes and composed capability data |
| `src/filmora_mcp/config.py` | Local defaults, environment overrides and configuration validation |
| `scripts/write_client_configs.py` | Generate absolute-path client snippets for the current installation |
| `scripts/install_clients.py` | Preview/apply client registration while preserving existing settings and saving backups |
| `scripts/check_clients.py` | Launch actual saved client entries through the official MCP SDK and check discovery/capabilities |
| `scripts/smoke_test.py` | Protocol checks and optional read-only native screenshot/accessibility checks |
| `scripts/build_reference.py` | Regenerate the human-readable coverage catalog |

## Request flow

1. A local MCP client launches the project's Python module and negotiates stdio MCP.
2. The assistant reads status/windows/capabilities and selects the intended editor or modal.
3. Executable metadata and installation hints resolve the runtime version. The compatibility layer chooses command candidates and reports feature eligibility.
4. Screenshot capture or UI inspection creates a short-lived observation tied to the selected window and its geometry.
5. An action resolves a compatible shortcut, live selector or observed pixel/control. Target/focus/observation guards check applicability before input.
6. Input invalidates observations. The assistant captures new state and verifies the resulting edit or dialog.

No timeline/project data model sits behind these operations. Timeline canvas items may need screenshot-driven selection and movement. Feature guides are navigation instructions; they do not invoke a hidden Filmora API.

## Version and UI resolution

Discovery searches expected installation roots, Filmora-named directories, configured paths and Windows App Paths. A full editor executable takes precedence over its adjacent bootstrapper. ProductVersion/FileVersion metadata takes precedence over adjacent version folder hints. Conflicting manual version declarations fail rather than silently changing routing.

The X profile uses a documented legacy subset and handles known shortcut differences. Modern release profiles use documented command candidates. Unknown/future profiles retain conservative shared shortcuts and generic UI tools. All require verification against the active build, shortcut preset and selection.

Named-target resolution uses exact internal names/IDs, exact visible-label/control-type candidates or authoritative configured selectors. Eligible missing controls can use version-resolved shortcut fallbacks. Disabled/ambiguous visible controls do not trigger those fallbacks. No stored coordinate map is specific to the development machine or a Filmora release.

## Observations and input

- An observation records window/process identity, geometry, creation time and screenshot mapping or inspected controls.
- Default expiry is 60 seconds. Input and window selection clear cached observations; geometry/process changes reject them.
- Resized/cropped screenshot coordinates map through source size and crop offset to desktop pixels.
- Input requires the target foreground window; pointer operations also check the window under the pointer. A modal may require explicit selection.
- Keys/modifiers and mouse buttons are released through cleanup paths after interrupted operations.
- An empty project-root `PAUSE` file or pointer at desktop `(0,0)` stops input.
- The server uses a reentrant lock for serialization within its process. Separate client-launched server processes do not share that lock.

Manual interaction can invalidate the meaning of an observation before its expiry. Fresh state remains necessary even when a token has not expired.

## Capture and data flow

Visible capture reads displayed Filmora pixels and requires the target foreground/unobscured. Native window capture is available when obscured, with documented stale GPU-surface risks. PNG bytes are returned as MCP image content with geometry metadata. `save=true` additionally writes a unique file in the configured capture directory.

The server opens no listening network port. Screenshot/project context is returned to the requesting MCP client, whose model/data handling is separate. Generic UI actions can activate Filmora's online features when instructed; local stdio does not make those editor operations offline.

Client backups and captures can contain private local context. They remain in ignored directories and are excluded from the distributed source ZIP. The installer does not change client trust policies or grant approval for tools.

## Configuration and distribution

`config.local.json` or `FILMORA_MCP_CONFIG` supplies executable, version fallback, observation TTL, text limit, shortcut overrides and exact UI selector overrides. `FILMORA_EXE` and `FILMORA_CAPTURE_DIR` override their corresponding settings. Configuration is loaded at startup.

The current setup uses an editable Python installation with project-relative resources. Run `setup.ps1` after extracting/moving the source and regenerate client snippets; do not move an existing virtual environment between machines. Source ZIPs include code, docs, tests and setup/client files, while omitting local environments, caches, captures, logs and private configuration.

## Validation and remaining work

The automated suite covers protocol, compatibility/routing, registration preservation and input guards. Native version/inspection/capture evidence is currently limited to 13.6.13. Full project creation/edit/save/export, broader editor releases and client-native image rendering remain validation work. Hard deadlines around native UI calls and cross-process coordination are future reliability work, not current guarantees. See [VALIDATION.md](VALIDATION.md) and [ROADMAP.md](ROADMAP.md).
