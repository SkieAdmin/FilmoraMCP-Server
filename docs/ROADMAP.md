# Roadmap

This roadmap records work outstanding after 0.2.0. Items are planned priorities, not shipped features or promised dates. The product target remains Windows Filmora X/v10 and newer with Claude Code/Desktop, Codex and Antigravity.

## Shipped foundation

- Local stdio MCP surface: 33 tools, 2 resources and 1 editing prompt.
- Screenshots, accessible-control inspection, generic input and editing/workflow primitives.
- Runtime version detection, X/10 legacy policy, 11–16 profiles, unknown/future conservative adaptation and live selector fallbacks.
- Version-aware feature reporting, custom shortcuts/selectors and primary-client registration with backups.
- 66 passing automated tests, including client relocation; native version/inspection/capture evidence on 13.6.13.

## Priority 1: complete live editing evidence

| Work | Exit criterion |
| --- | --- |
| Validate Filmora X/10 on a disposable project | Recorded discovery/profile, screenshot, import, split/trim, title/effect/audio adjustment, Save As, local export and output playback |
| Validate representative newer releases | The same workflow recorded on representative 11–12, 13 and 14–16 builds, including observed differences/overrides |
| Verify native client behavior | Each primary client loads tools and handles screenshot content; a bounded editing scenario is verified in its own host |
| Record reproducible fixtures | Each live run records editor build, Windows/Python version, locale, layout, shortcut preset, media fixture and actual results |

## Priority 2: refine compatibility from evidence

| Work | Exit criterion |
| --- | --- |
| Validate modern command candidates by build | Observed assignments become documented profile entries; conflicting/absent ones are gated or routed through UI |
| Expand layout/locale selectors | Exact selectors are backed by observed control trees and regression fixtures |
| Improve feature checks | Add supported generation boundaries and live-route checks without treating eligibility as entitlement |
| Cover modal and file-dialog variations | Import/save/export dialogs across validated versions have documented routes and recoverable failure behavior |

## Priority 3: improve reliability and distribution

| Work | Exit criterion |
| --- | --- |
| Native-call deadlines and timing diagnostics | Slow/hung accessibility operations have bounded handling and useful diagnostics |
| Cross-process desktop coordination | Competing client-launched server processes cannot interleave editing inputs silently |
| Export completion validation | Rendering completion and audiovisual output checks have a reproducible workflow beyond file existence/size |
| Portable installation packaging | Resource lookup, setup and configuration relocation are verified beyond the current editable-source installation |
| Documentation/version maintenance | Release evidence, compatibility policy, PRD, catalog and changelog stay aligned |

macOS/mobile, headless operation and a semantic timeline backend would require separate product/architecture decisions. They are not implied by the X/v10+ Windows compatibility target.
