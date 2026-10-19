# Changelog

Dates use Asia/Manila. Entries describe implemented changes separately from validation limits.

## Unreleased

- Import the full project into the FilmoraMCP-Server repository while preserving its Git history and owner license.
- Add explicit `--relocate-from` / `-RelocateFrom` client-registration updates for a moved project, retaining custom settings and creating backups.
- Add six relocation regression cases (66 total passing tests) and document environment recreation plus client reconnection after a move.

## 0.2.0 — 2026-10-19

### Added

- Filmora X/v10+ product target with runtime executable-version detection and installation discovery across common locations and Windows App Paths.
- X/10 legacy shortcut policy, profiles for 11–16, and conservative unknown/future routing.
- Version-aware command/feature reporting, optional live control probes, exact-label/ID alternatives and configured UI selectors.
- Compatible shortcut fallbacks when a named target is absent; disabled/ambiguous visible targets do not trigger fallbacks.
- Compatibility regression fixtures, bringing the recorded suite to 60 passing tests.
- Product requirements, architecture, roadmap and a documentation index; README and supporting guides aligned with the broader target.

### Changed

- Product identity and docs no longer target a single installed Filmora build. Version 13.6.13 is retained as the local validation environment.
- Command enumeration resolves the selected profile and can explain unavailable/ambiguous commands.
- Discovery prefers the editor over an adjacent bootstrapper and reports detection provenance.
- Client configuration checks verify the X/10 minimum target and runtime profile.

### Validation limits

Native editor testing remains on 13.6.13. Other version profiles have policy/adapter tests, not live certification. A complete create/import/edit/save/export run and host-native screenshot/editing validation across all clients remain outstanding.

## 0.1.0 — 2026-10-19

### Added

- Initial Windows stdio server with 33 tools, 2 resources and 1 editing prompt.
- Screenshot capture, accessible-control inspection, mouse/keyboard operations, project/media dialogs and editing/export workflow primitives.
- Catalog of 94 shortcut candidates, 39 named UI targets and 102 feature guides.
- Setup scripts and client snippets; registration for Claude Code, Claude Desktop, Codex and Antigravity with config validation, backups and idempotency.
- Initial native status/inspection/screenshot evidence on the installed Filmora editor and automated guard/protocol/registration tests.
