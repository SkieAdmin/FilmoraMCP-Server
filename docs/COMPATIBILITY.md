# Filmora X / 10 and newer

FilmoraMCP **0.2.0** targets Windows Filmora **X (10) and later**, independently of the version installed on the developer's computer. The MCP clients remain Claude Code/Desktop, Codex and Antigravity; their connection commands do not need changing when Filmora upgrades.

The [PRD](../PRD.md) defines this compatibility target as a product requirement. [VALIDATION.md](VALIDATION.md) records completed checks; [ROADMAP.md](ROADMAP.md) tracks additional live editor/client validation.

## Compatibility matrix

| Editor | Resolution policy | Validation evidence |
| --- | --- | --- |
| Filmora X / 10.x | Legacy documented shortcut subset; older shortcut assignments; adaptive live selectors; generic screenshot/input controls | Automated adapter tests + official legacy reference; no live X installation tested |
| Filmora 11.x, 12.x | Release-labeled modern command candidates, live UI resolution and configured overrides | Automated policy/adapter tests; no live editor run |
| Filmora 13.x | Modern command candidates + live UI resolution | Live status, version metadata, UI inspection and screenshots on 13.6.13; full edit/export run not yet tested |
| Filmora 14.x–16.x | Release-labeled modern command candidates, newer-feature eligibility checks and live UI resolution | Automated policy/adapter tests; no live editor run |
| Versions newer than the last known profile | Conservative shared shortcuts plus generic inspection/input and live selectors | Future-adapter tests; no guarantee of unchanged future UI or shortcuts |
| Unknown executable version | Conservative shared shortcuts and generic/live UI routes; explicit version fallback available | Unknown-version tests; version-dependent shortcuts blocked until resolved/configured |
| Filmora 9 and earlier | Outside target range; versioned command dispatch/launch/input refused | Minimum-version tests |

This matrix describes implemented compatibility strategies. It is not certification that every release, build, feature, locale or plugin has been exercised. A version profile is a set of routing policies, not a bundled copy of Filmora.

## Runtime detection

`filmora_status` returns installation details and `runtime_version`, including `major`, `version`, detection `source`, profile and whether the version is known/in range. Each enumerated window also carries executable-version metadata.

Detection checks Windows executable ProductVersion/FileVersion first, then adjacent version-shaped installation folder names. It does not infer Filmora's version from arbitrary digits in usernames or project titles. Discovery covers Wondershare locations under LocalAppData/Program Files, Filmora-named installation directories and Windows App Paths. When `Filmora.exe` is beside `Wondershare Filmora.exe`, the full editor is preferred to avoid reporting its bootstrapper as a second installation. Custom locations can use `FILMORA_EXE` or `executable` in configuration.

When more than one installation/instance is available, select the intended window or configure the executable. The server does not silently choose between different installed versions.

## Commands and fallback behavior

- X/10 uses its legacy documented command subset. Preferences resolves to `ctrl+,`, Rename to `enter`, and Chroma Key to `ctrl+alt+g`. Modern profiles use their modern candidate assignments. These can still vary by Filmora build and custom shortcut preset. [Wondershare legacy shortcut reference](https://filmora.wondershare.com/guide/filmora-keyboard-shortcuts-for-windows.html), [modern shortcut reference](https://filmora.wondershare.com/guide/keyboard-shortcuts-on-windows.html)
- The legacy reference assigns `Ctrl+Alt+C` to both Copy Effects and Color Correction. The X profile blocks both automatic assignments until the actual shortcut is configured; use observed UI controls meanwhile.
- A command not documented in the legacy subset is not automatically sent on X. `filmora_commands(include_unavailable=true)` explains why; an explicit `shortcut_overrides` entry can supply the actual locally configured key.
- Unknown/future versions automatically enable only the conservative intersection of common legacy/modern commands. Generic screenshot, mouse, keyboard and accessibility tools remain available; version-specific commands need explicit confirmation through detected version or configuration.
- Panel navigation tries exact internal names/IDs, then exact visible-label/control-type candidates. Candidate internal names were observed on v13; they are not asserted to be stable across releases. A small set of missing controls can fall back to a permitted profile shortcut (for example, Export uses `Ctrl+E`). Hidden controls are not clicked. Disabled or ambiguous visible matches never trigger a shortcut fallback.
- No fixed coordinate maps are stored for any release. Canvas interaction uses fresh screenshots. Localized or changed controls can be supplied in `ui_target_overrides`.

## Feature availability

`filmora_capabilities(probe_ui=true)` reports exposed/enabled/disabled/ambiguous controls for the current window. Absence means **not exposed in the current view**, not necessarily missing from the installed product. Choose the right panel/clip and inspect again. Probes return an observation ID for the live controls.

Feature guides report `version_status` and `live_status`. Selected documented boundaries flag clearly newer capabilities on older editors: Smart Cutout (12), AI Copilot/text-based editing/AI music (13), and Planar Tracking/multicam/Smart Short Clips/video enhancement/video denoise (14). Unlisted features intentionally have no invented introduction version. Eligibility never establishes entitlement, successful generation or visible controls. [Wondershare release history](https://filmora.wondershare.com/whats-new-in-filmora-video-editor.html), [Filmora 13 features](https://filmora.wondershare.com/answers/latest-features-in-filmora-13.html), [Filmora 14 features](https://support.wondershare.com/how-tos/filmora/whats-new-in-filmora-14.html)

## Configuration examples

Normally keep `filmora_major_version` at `null`. If a custom installation exposes no usable executable/path metadata, a fallback can be specified:

```json
{
  "executable": "D:\\Editors\\Filmora\\Wondershare Filmora.exe",
  "filmora_major_version": "X",
  "shortcut_overrides": {
    "color_correction": "ctrl+shift+c"
  },
  "ui_target_overrides": {
    "export": [
      {"name": "Exporter", "control_type": "Button"}
    ]
  }
}
```

The shortcut/label above are examples: use values observed/configured in that editor. An override contradicting a known detected version is rejected. A custom selector is authoritative for that target and will not silently fall through to an English label or shortcut if it fails. A selector requires `control_type` plus exact `name` and/or `automation_id`; regular expressions and substring matching are not used.

## Validation on additional versions

On a disposable project, verify discovery/version/profile, screenshot scaling, accessible controls, import, the active shortcut preset, split/trim, a title/effect/audio adjustment, Save As to a new filename, then local export and playback. Record build, locale, layout and any overrides. Older project compatibility with newer Filmora, and opening newer `.wfp` projects in older versions, is governed by Filmora itself; this server does not convert project formats.
