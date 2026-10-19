"""Regenerate human-readable command/UI/feature coverage reference."""
from pathlib import Path
from filmora_mcp.catalog import COMMANDS, FEATURES, UI_TARGETS
from filmora_mcp.compatibility import command_policy

root = Path(__file__).resolve().parents[1]
lines = ["# Tool and feature coverage", "",
         f"{len(COMMANDS)} shortcut commands, {len(UI_TARGETS)} named UI targets and {len(FEATURES)} feature routes.", "",
         "Shortcut commands are input dispatches. Named targets are live accessibility lookups. Feature routes are guidance for real UI interaction, not single-call feature implementations.", "",
         "Filmora X/10 is the minimum target. See COMPATIBILITY.md for release policies and validation status.", "",
         "## Shortcut command candidates", "", "| Command | X/10 | Modern candidate | Context |", "| --- | --- | --- | --- |"]
legacy = command_policy(COMMANDS, 10)
for name, cmd in COMMANDS.items():
    keys = legacy[name]["keys"] or "UI/configured override"
    lines.append(f"| `{name}` | `{keys}` | `{cmd['keys']}` | {cmd['group']} |")
lines.extend(["", "## Named UI target candidates", "", "Internal names below were observed on v13. Other releases can resolve exact labels, automation IDs, configured selectors or eligible shortcut fallbacks.", "",
              "| Target | Candidate internal name |", "| --- | --- |"])
for name, control in UI_TARGETS.items():
    lines.append(f"| `{name}` | `{control}` |")
lines.extend(["", "## Feature routes", "", "Some routes refer to newer Filmora features. Confirm availability in the installed editor.", "",
              "| Feature | Category |", "| --- | --- |"])
for name, feature in FEATURES.items():
    lines.append(f"| `{name}` | {feature['category']} |")
(root / "docs" / "COVERAGE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("Generated docs/COVERAGE.md")
