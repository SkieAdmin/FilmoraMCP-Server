# FilmoraMCP product requirements

| Field | Value |
| --- | --- |
| Product | FilmoraMCP |
| Release baseline | 0.2.0 |
| Last updated | October 19, 2026 (Asia/Manila) |
| Target editor | Wondershare Filmora X / v10 and newer on Windows |
| Primary clients | Claude Code, Claude Desktop, Codex and Google Antigravity |
| Status | Implemented local MCP foundation; broader live editor validation outstanding |

## 1. Product purpose

Enable an MCP assistant to inspect and operate Filmora using the user's installed editor. The assistant must be able to see screenshots, inspect controls, select the appropriate version policy, perform editing actions and check the resulting UI. The product must target Filmora X/v10 onward rather than depend on the version installed on one development machine.

The intended coverage spans most editing work accessible through Filmora's desktop UI. Coverage consists of direct tool operations, documented shortcut candidates, live control interaction and guided multi-step workflows. A catalog entry is not evidence that a feature is available or that an edit completed.

## 2. Users and use cases

| User | Need | Example workflow |
| --- | --- | --- |
| Video creator | Complete editing tasks using an assistant | Import clips, arrange/trim, add titles/transitions, adjust audio, save a copy and export |
| Existing Filmora user | Use a currently owned Filmora release | Detect X/10 or a newer version and adapt commands/control selection |
| MCP user | Connect through an existing local client | Register FilmoraMCP with Claude, Codex or Antigravity without replacing other servers |
| Integration maintainer | Extend compatibility without rewriting the backend | Add evidence-based selectors, command policies and regression fixtures for a release or locale |

## 3. Goals and boundaries

### Goals

1. Provide a usable local MCP interface to Windows Filmora X/v10 and newer.
2. Cover project/media management, timeline work, video/color/audio/text editing, assets, advanced-feature navigation and local export through observable UI operations.
3. Return real MCP images and enough version/control metadata for an assistant to choose actions and verify results.
4. Adapt to version, layout and localization differences using live controls, compatible shortcuts, explicit overrides and screenshot coordinates.
5. Separate implementation coverage, version eligibility, current UI visibility, license availability and actual validation evidence.
6. Preserve existing client settings during registration and make failed/partial UI operations recoverable through reinspection.

### Current boundaries

- The implementation is Windows-only; macOS, mobile and headless/service execution are outside this release.
- Filmora 9 and earlier are outside the target range. Unknown versions use conservative routing; they are not reported as confirmed compatible.
- The server does not convert `.wfp` formats, modify undocumented project internals or provide an official Wondershare API.
- Premium assets, AI credits, cloud processing and newer-version features remain Filmora dependencies. The integration does not backport features or provide entitlements.
- No frame-accurate timeline model, semantic clip-ID API or guaranteed unattended editing is provided by the current UI backend.
- Future releases receive generic adaptation, not a promise that their UI and shortcut assignments remain unchanged.

## 4. Compatibility requirements

| Editor family | Required behavior | Evidence at this release |
| --- | --- | --- |
| X/10 | Legacy shortcut subset, known older assignments and live UI/screenshot routes | Automated policy/adapter tests; official legacy reference; live validation pending |
| 11–12 | Detect release, select its profile and use live control resolution | Automated policy/adapter tests; live validation pending |
| 13 | Same version-aware behavior; retain the locally observed selectors as candidates | Native status, inspection and screenshots verified on 13.6.13; full editing validation pending |
| 14–16 | Select release profile and report known newer-feature boundaries | Automated policy/adapter tests; live validation pending |
| Unknown/future | Conservative shared commands, generic controls and explicit overrides | Automated fallback tests; actual compatibility requires verification |

Executable version metadata takes precedence over adjacent installation-folder hints. A manual version fallback is permitted only when it does not contradict detected metadata. Multiple installations/instances require an explicit executable/window choice. The complete policy and sources are in [COMPATIBILITY.md](docs/COMPATIBILITY.md).

## 5. Functional requirements and traceability

“Implemented” below means the routing/tool mechanism exists. It does not mean every resulting editing workflow has been run in every Filmora release.

| ID | Requirement | Implementation/evidence | Status |
| --- | --- | --- | --- |
| FR-01 | Discover supported editor executables and enumerate their windows/dialogs by process | `backend.py`; native diagnostics and discovery fixtures | Implemented; expanded installation matrix pending |
| FR-02 | Detect runtime version and report detection source, profile and minimum-version policy | `compatibility.py`, `filmora_status`; metadata/path/profile tests | Implemented; native detection verified on 13.6.13 |
| FR-03 | Resolve commands by release and avoid silently sending unsupported/ambiguous defaults | `command_policy`, `filmora_commands`, `filmora_command`; legacy/modern/unknown fixtures | Implemented; per-build shortcut verification pending |
| FR-04 | Return PNG screenshots with crop/resize geometry and optional local persistence | `filmora_screenshot`, `filmora_state`; real MCP image round trips and coordinate tests | Implemented; GPU/window-mode limitations documented |
| FR-05 | Inspect accessible names, IDs, types, geometry, focus and supported value/state patterns | `filmora_inspect`; native tree read and backend tests | Implemented; canvas accessibility varies |
| FR-06 | Support mouse clicks, drags, scrolls, key chords and literal Unicode in observed editable controls | Backend input methods and input tools; cleanup/focus/coordinate tests | Implemented; live editing validation pending |
| FR-07 | Resolve UI targets from live names/IDs, labels or configured selectors; use permitted shortcut fallbacks when absent | `named_target`, selector policies; ambiguity/disabled/localization/fallback fixtures | Implemented; selectors require validation on additional versions |
| FR-08 | Support new/open/save/save-as, import and conventional local file-dialog interaction | Project tools and native filename-field helper; path/overwrite tests | Implemented; full live file-dialog workflow pending |
| FR-09 | Expose timeline edit, navigation, marker and zoom operations | Editing/playback/marker/zoom tools and command catalog | Implemented as context-dependent command/UI dispatch |
| FR-10 | Provide video, color, audio, text, asset and advanced-feature access through actual controls and guided routes | Clip/panel tools and feature guides | Implemented generic access; individual feature validation pending |
| FR-11 | Report version eligibility and optionally probe visible/enabled/disabled/ambiguous targets | Feature policies and `filmora_capabilities(probe_ui=true)` | Implemented; not an entitlement or completion check |
| FR-12 | Open/configure/start/monitor local export through the UI and check an explicit output file | Export UI tools, general controls and `filmora_verify_output` | Implemented primitives; completed export/playback validation pending |
| FR-13 | Register Claude Code/Desktop, Codex and Antigravity without replacing unrelated MCP settings | Client snippets/installer/checker; preservation, backup and idempotency tests | Implemented; all four saved entries passed SDK round trips |
| FR-14 | Refuse stale observations and non-target/blocked input, release pressed inputs after interruption and expose a pause mechanism | Backend guards, observation cache and cleanup tests | Implemented; serialization is per server process |
| FR-15 | Describe supported scope and validation limits consistently across docs and MCP capabilities | README, PRD, compatibility/coverage/validation docs and runtime catalog | Maintained for 0.2.0 |

## 6. Interaction contract

The expected loop is **observe → choose one action → dispatch → reobserve → verify**. The assistant must select the actual Filmora editor or modal dialog, establish relevant focus/selection, and use a fresh observation before acting on coordinates or control IDs.

Screenshot and accessibility observations have distinct IDs. Inputs invalidate observations; expiry and changed window geometry also invalidate them. A successful input result records dispatch, not a completed edit. A failure after input may be partial and requires reinspection before retrying.

Absent controls are reported as unexposed in the current view. Disabled or ambiguous visible controls must not silently trigger shortcut fallbacks. Known feature-generation checks and live control probes must not be interpreted as proof of account entitlement or successful processing.

## 7. Operational requirements

| Area | Requirement / current constraint |
| --- | --- |
| Runtime | 64-bit Windows, Python 3.11+, installed Filmora, unlocked interactive session and compatible privilege level |
| Transport | Local stdio MCP; clean protocol stdout; diagnostics/errors outside the MCP data stream |
| Client interoperability | Standard tool/resource/prompt discovery and PNG image content; native client rendering remains host-dependent |
| Data handling | Screenshots may contain project content and are returned to the requesting client; optional captures remain local; logs/config backups are excluded from source ZIPs |
| Execution scope | Operate validated Filmora processes; no arbitrary shell/code-execution tool is exposed |
| Configuration | Per-installation executable/version/shortcut/selector overrides; no embedded personal username or fixed editor build in core routing |
| Client installation | Validate config before write, preserve unrelated values, back up originals, refuse conflicting Filmora entries and detect concurrent changes |
| Concurrency | Serialize calls within one server process; clients share the desktop and should operate one at a time |
| Performance | Bounded input repetitions/waits; accessibility duration depends on the editor. No measured latency SLA is claimed; native-call timeouts/instrumentation remain future work |

The supplied Codex configuration allows 60 seconds for startup and 120 seconds per tool. Those are client settings, not a universal server-side execution deadline.

## 8. Acceptance criteria and present results

| ID | Acceptance check | Result / remaining work |
| --- | --- | --- |
| AC-01 | Discover the MCP surface and call capabilities without editing the project | Passed with the official SDK: 33 tools, 2 resources, 1 prompt |
| AC-02 | Launch from each primary client's saved configuration | Passed for Claude Code/Desktop, Codex and Antigravity through SDK round trips; native Claude Code health check connected |
| AC-03 | Detect the actual installed editor and select its matching profile | Passed on 13.6.13 via executable ProductVersion |
| AC-04 | Exercise X/10–16, unknown/future, minimum-version and selector/fallback policies | Passed automated fixtures; not a substitute for native runs on those releases |
| AC-05 | Return actual screenshot images and correctly map resized/cropped coordinates | Native images and coordinate fixtures passed; foreground visible capture checked visually |
| AC-06 | Reject malformed/stale/ambiguous/wrong-target operations and preserve client settings | Covered by the passing automated suite |
| AC-07 | Create a disposable project, import clips, edit video/audio/title/effect, Save As and complete a local export verified by playback | Outstanding; must be recorded separately for each validated editor family |
| AC-08 | Confirm host image presentation and editing behavior inside each primary client | Outstanding beyond protocol/configuration checks |

The recorded suite contains **66 passing tests**, including explicit client-relocation coverage. See [VALIDATION.md](docs/VALIDATION.md) for the environment, observations and limitations. New live results must identify build, locale, layout, active shortcut preset and overrides.

## 9. Roadmap and release discipline

Prioritize disposable-project end-to-end validation on X/10 and representative newer releases, followed by client-native image/editing checks, evidence-based profile refinements and runtime reliability improvements. [ROADMAP.md](docs/ROADMAP.md) tracks these as outstanding work rather than shipped capability.

Changes to the minimum version, client list, routing policy, MCP surface or validation claims require coordinated updates to README, this PRD, the compatibility guide, coverage reference, validation record and changelog. Feature or version claims must distinguish policy tests from a live editor run. Generated coverage must be refreshed from the catalog when its entries change.
