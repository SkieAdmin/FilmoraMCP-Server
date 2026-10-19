# Validation record

Validated locally on **October 19, 2026 (Asia/Manila)** with Windows, Python **3.14.7**, Filmora **13.6.13.9072** and MCP Python SDK **1.30.0**.

## Verified

- Real stdio MCP initialization negotiated protocol `2025-11-25`.
- All **33 tools**, **2 resources** and **1 prompt** were discovered through the official MCP client.
- Capabilities/resource reads and prompt retrieval worked; an invalid editing command returned an MCP tool error.
- Process-based discovery found the actual installed/running Filmora executable.
- Real `filmora_screenshot` returned native MCP `image/png` content at **1200 × 712**, with correct original window dimensions **1920 × 1140**, coordinate metadata, image hash and saved PNG.
- Both `mode="window"` and default `mode="visible"` completed real stdio round trips. The visible capture was visually checked against the foreground editor and correctly showed its rendered video preview.
- The PNG was visually inspected. Native window capture can have stale/overlapping GPU surfaces while the app is obscured; the optional visible capture mode is supplied for foreground rendered previews. A successful PNG response alone does not establish visual fidelity of GPU video frames.
- Real `filmora_inspect` found all **8 library tabs**. A deeper read enumerated **205 controls**, without traversal errors or truncation; **36 of 39** named controls matched both name and type in that layout. Speech-to-text, AI translation and the project-settings Edit button were not exposed in that later snapshot and need the appropriate layout/toolbar context. The main Edit menu is deliberately not accepted in place of the project-settings button.
- **66 automated tests passed**, covering protocol round trips, configured/default chord parsing, input cleanup and focus/coordinate guards, file/dialog validation, client registration/relocation preservation and backups, plus compatibility policies for X/10 through 16, unknown/future versions, metadata/path detection, legacy shortcut differences, feature-generation boundaries, localized selectors, correct fallback behavior and minimum-version enforcement.
- `pip check` reported no broken requirements. Python compile checks passed.

## Client registration

- Added Filmora to the existing user configurations for **Claude Code, Claude Desktop, Codex and Google Antigravity**; original files were backed up under `logs/client-backups`.
- **Claude Code:** `claude mcp get filmora` reported `Connected` at user scope.
- **Codex:** `codex mcp get filmora --json` reported the stdio entry enabled with the expected command and timeouts.
- `scripts/check_clients.py` launched each of the four entries from its actual saved client configuration through the official MCP client. All four initialized and discovered **33 tools, 2 resources and 1 prompt**, and successfully called the capabilities tool.
- A second registration run reported `already-configured` for all four clients, without duplicate entries or new backups.
- Host application UI refresh/restart is still required for already-running clients. The four configuration-based checks do not establish an editing session or screenshot rendering inside each host application. No model chats were dispatched.

Client check details are saved in `logs/client-validation.json` (excluded from source ZIPs).

## X/10+ compatibility release

Version **0.2.0** targets Filmora X/10 and newer. Read-only diagnostics detected the installed editor as `13.6.13.9072` from its executable ProductVersion and selected the `filmora-13` profile. The X profile and modern/unknown/future adapters are covered by automated fixtures; no Filmora X, 11, 12, 14, 15 or 16 installation was run locally. A version profile does not establish live availability of a feature or correctness of every shortcut in every build. See `COMPATIBILITY.md` for exact policies and evidence.

All four saved client entries completed MCP round trips again after the upgrade, reported minimum Filmora major **10**, and resolved the installed runtime to `filmora-13`. Existing registrations continue to point at the same module; restart/reload clients to replace any previously running server process.

## Verification limits

The existing editor contained a user's project. Validation did not replace, save, trim, delete, export, upload, record or otherwise edit that project. Input cleanup/focus guards were tested with a simulated backend. **A complete create → import → edit → save → export workflow has not been run live**, nor have the 94 documented shortcuts and 102 feature routes each been individually exercised.

The server provides generic UI interaction for those workflows, not a guarantee of full feature availability or unattended end-to-end editing. Test a representative workflow on a disposable project before using unattended editing. Premium/AI operations, custom dialogs, numeric control modification and native file-dialog submission should be validated in the user's chosen editing session.

Raw read-only smoke-test results are in `logs/smoke-test.json`; captures are local under `captures/`. These files are excluded from the source distribution because they contain local window/project context.

## Repository relocation

The full project was imported into the FilmoraMCP-Server Git repository. Its existing Git history and owner license were preserved, and its short initial README was backed up locally before replacement with the complete project README. Source/document/local artifact copies were checked by content hashes; the virtual environment was recreated rather than copied.

The rebuilt environment imports `filmora_mcp` from the new repository's `src` directory. All 66 tests passed there and `pip check` reported no broken requirements. Matching Claude Code, Claude Desktop, Codex and Antigravity registrations were relocated with backups, and each passed the standard MCP round-trip check using the new environment. Claude Code's native check reported Connected from the new path. Reload/restart already-running clients to use the relocated server process. The original project copy remains available as a local backup.
