# Documentation index

FilmoraMCP 0.2.0 targets Windows Filmora X/v10 and newer. Claude Code/Desktop, Codex and Google Antigravity are the primary local MCP clients. The current native editor validation environment is 13.6.13; broader compatibility policies and their tests are documented separately from live verification.

| Document | Purpose |
| --- | --- |
| [Project README](../README.md) | Product overview, installation, clients, scope and operating limits |
| [PRD](../PRD.md) | Users, requirements, compatibility contract, acceptance criteria and evidence |
| [Compatibility](COMPATIBILITY.md) | Version policies, detection, selectors/shortcuts and validation matrix |
| [Client setup](CLIENTS.md) | Registration paths and steps for Claude Code/Desktop, Codex and Antigravity |
| [Workflows](WORKFLOWS.md) | Observe–act–verify sequences for editing through the real UI |
| [Coverage](COVERAGE.md) | Generated command candidates, UI target names and feature routes |
| [Architecture](ARCHITECTURE.md) | Components, routing, state, input/capture and configuration |
| [Validation](VALIDATION.md) | Recorded checks, environment and what remains untested |
| [Roadmap](ROADMAP.md) | Outstanding validation and reliability work |
| [Changelog](../CHANGELOG.md) | Changes by release |

## Maintaining these documents

Minimum-version and client-scope changes belong in README, PRD and compatibility/client docs. Catalog changes require rerunning `.\.venv\Scripts\python.exe scripts\build_reference.py` from the project root; do not hand-edit generated coverage rows.

Validation claims must distinguish automated fixture results, SDK/configuration round trips, native client checks, native editor operations and complete editing/export runs. Add the tested build/environment and any overrides when recording new live results. Use the roadmap for planned work rather than listing it as current capability.

Machine-specific paths belong in generated client snippets or local setup/validation context, not in product requirements or core version-routing logic. Local captures, private configs and client backups must remain excluded from source distributions.
