from __future__ import annotations

import argparse
import functools
import json
from pathlib import Path
import sys
import time
from typing import Literal

from mcp.server.fastmcp import FastMCP, Image
from mcp.types import ToolAnnotations

from . import __version__
from .backend import desktop, bounded, local_file
from .catalog import COMMANDS, FEATURES, UI_TARGETS, capabilities
from .config import ROOT

mcp = FastMCP(
    "FilmoraMCP",
    instructions=("Control Windows Filmora X/version 10 and newer. Start with filmora_status, filmora_windows, "
                  "filmora_capabilities and filmora_screenshot. Select the actual window/dialog. "
                  "Use fresh observation IDs for pixels and accessibility controls. All input invalidates observations. "
                  "Commands dispatch input; verify state before claiming an edit succeeded. "
                  "Prefer accessible names over guessed coordinates. Use feature guides for advanced workflows. "
                  "Respect unsaved projects, selected clips, premium assets and online AI/upload/credit actions. "
                  "No automatic upload, payment, sign-in, or overwrite handling. "
                  "The server shares the interactive desktop; avoid simultaneous manual input."),
)

READ = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
EDIT = ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=False)


def serialized(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        with desktop.lock:
            return fn(*args, **kwargs)
    return wrapped


@mcp.tool(annotations=READ)
@serialized
def filmora_status() -> dict:
    """Read installed executables, running Filmora windows, pause state and server version."""
    paths = desktop.installations()
    return {"server_version": __version__, "minimum_filmora_major": 10, "installations": paths,
            "installation_details": [{"executable": p, "version": desktop.executable_version(p)} for p in paths],
            "windows": desktop.windows(), "runtime_version": desktop.runtime_version(),
            "input_paused": (ROOT / "PAUSE").exists(),
            "selected_hwnd": desktop.selected_hwnd, "transport": "stdio", "platform": sys.platform}


@mcp.tool(annotations=READ)
@serialized
def filmora_windows() -> list[dict]:
    """List visible Filmora windows/dialogs by validated process, with handles and geometry."""
    return desktop.windows()


@mcp.tool(annotations=EDIT)
@serialized
def filmora_select_window(hwnd: int) -> dict:
    """Select a handle returned by filmora_windows. Select modal dialogs explicitly."""
    return desktop.select(hwnd)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_launch() -> dict:
    """Launch installed Filmora if it is not running; does not open or replace a project."""
    return desktop.launch()


@mcp.tool(annotations=EDIT)
@serialized
def filmora_activate() -> dict:
    """Restore/foreground the selected Filmora window. Does not maximize or resize it."""
    row = desktop.target()
    desktop.activate(row)
    return row


@mcp.tool(annotations=READ)
@serialized
def filmora_capabilities(probe_ui: bool = False) -> dict:
    """Resolve commands/features for detected Filmora X/10+; probe_ui checks exposed controls, not account entitlements."""
    return desktop.runtime_capabilities(probe_ui)


@mcp.tool(annotations=READ)
@serialized
def filmora_commands(group: str = "", query: str = "", include_unavailable: bool = False) -> dict:
    """Find version-resolved shortcuts. Unavailable/ambiguous commands are omitted unless requested."""
    commands = desktop.runtime_capabilities()["commands"]
    return {k: v for k, v in commands.items() if (not group or v["group"] == group)
            and (include_unavailable or v["dispatchable"])
            and (not query or query.casefold() in (k + " " + v["prerequisite"]).casefold())}


@mcp.tool(annotations=READ)
@serialized
def filmora_feature_guide(feature: str) -> dict:
    """Get a UI route for an advanced feature. Guidance is not an executed edit or guaranteed availability."""
    if feature not in FEATURES:
        raise ValueError(f"Unknown feature. Choose from: {', '.join(FEATURES)}")
    entry = desktop.runtime_capabilities()["features"][feature]
    return {"feature": feature, **entry,
            "next": "Check version_status, inspect actual UI, act once, then inspect the result. Guidance does not establish availability."}


def shot(hwnd=None, max_width=1600, crop=None, save=False, mode="visible"):
    meta, data = desktop.screenshot(hwnd=hwnd, max_width=max_width, crop=crop, save=save, mode=mode)
    return [json.dumps(meta, ensure_ascii=False), Image(data=data, format="png")]


@mcp.tool(annotations=READ)
@serialized
def filmora_screenshot(hwnd: int | None = None, max_width: int = 1600,
                       crop: list[int] | None = None, save: bool = False,
                       mode: Literal["window", "visible"] = "visible") -> list:
    """Return actual MCP PNG image + coordinate metadata. Optional crop uses original window pixels.

    Click/drag/scroll coordinates use displayed image pixels, including resize/crop mapping.
    save=True stores a uniquely named PNG in captures. Restore minimized windows first.
    window mode captures the app even when obscured, but GPU previews may have artifacts.
    visible mode captures displayed pixels; Filmora must be foreground and unobscured.
    """
    return shot(hwnd, max_width, crop, save, mode)


@mcp.tool(annotations=READ)
@serialized
def filmora_inspect(hwnd: int | None = None, max_depth: int = 16,
                    max_elements: int = 900, query: str = "") -> dict:
    """Read UI Automation controls and focus. IDs expire; query filters returned names, not tree traversal."""
    return desktop.inspect(hwnd, max_depth, max_elements, query)


@mcp.tool(annotations=READ)
@serialized
def filmora_state(max_width: int = 1600, max_elements: int = 600) -> list:
    """Return a screenshot plus accessible controls, each with its own observation ID."""
    tree = desktop.inspect(max_depth=20, max_elements=max_elements)
    return [json.dumps(tree, ensure_ascii=False), *shot(max_width=max_width)]


@mcp.tool(annotations=EDIT)
@serialized
def filmora_click(observation_id: str, x: float, y: float,
                   button: Literal["left", "right", "middle"] = "left", count: int = 1,
                   modifiers: list[str] | None = None) -> dict:
    """Click screenshot pixels. Double-click count=2; Alt-click adds a keyframe where supported."""
    return desktop.click(observation_id, x, y, button, count, modifiers)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_drag(observation_id: str, start_x: float, start_y: float,
                  end_x: float, end_y: float, duration: float = 0.8,
                  modifiers: list[str] | None = None) -> dict:
    """Drag clips/assets/trim handles/keyframes using fresh screenshot pixels. Alt-drag can replace media."""
    return desktop.drag(observation_id, start_x, start_y, end_x, end_y, duration, modifiers)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_scroll(observation_id: str, x: float, y: float, ticks: int,
                    horizontal: bool = False, modifiers: list[str] | None = None) -> dict:
    """Scroll a pane at screenshot pixels. Positive ticks scroll up/right; negative down/left."""
    return desktop.scroll(observation_id, x, y, ticks, horizontal, modifiers)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_key(chord: str, repeat: int = 1) -> dict:
    """Dispatch one key/chord, e.g. ctrl+b, escape, tab, left. No raw script or Windows key support."""
    return desktop.press(chord, repeat)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_command(action: str, repeat: int = 1) -> dict:
    """Dispatch a named command from filmora_commands. Focus/selection determines its effect; verify afterward."""
    return desktop.command(action, repeat)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_ui_action(observation_id: str, element_id: str,
                      action: Literal["click", "invoke", "focus", "set_value", "select", "toggle",
                                      "expand", "collapse", "set_range"] = "click",
                      value: str | None = None) -> dict:
    """Operate one freshly inspected control. set_value sets text; set_range uses a slider's native numeric range.

    select chooses a combo/list item by exact visible text. Unsupported accessibility patterns raise an error;
    capture a screenshot and use pixels instead. Value parameter is a string, including numeric ranges.
    """
    return desktop.ui_action(observation_id, element_id, action, value)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_type_text(observation_id: str, element_id: str, text: str) -> dict:
    """Insert literal Unicode into a focused observed Edit/Document control. Reinspect after focusing first."""
    return desktop.type_text(observation_id, element_id, text)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_open_panel(panel: str) -> dict:
    """Open a Filmora X/10+ panel using live controls, exact-label selectors, or a version-resolved shortcut.

    Includes toolbar toggles such as auto_snap and auto_ripple: these toggle state, not ensure enabled.
    Configure ui_target_overrides for localized/different layouts. Disabled/ambiguous controls never trigger fallbacks.
    """
    return desktop.named_target(panel)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_new_project() -> dict:
    """Open new-project workflow. Existing project may prompt to save; inspect before proceeding."""
    return desktop.command("new_project")


@mcp.tool(annotations=EDIT)
@serialized
def filmora_open_project_dialog() -> dict:
    """Open Filmora's project chooser. List/select the dialog, then fill_file_dialog with an existing .wfp."""
    return desktop.command("open_project")


@mcp.tool(annotations=EDIT)
@serialized
def filmora_save_project(save_as: bool = False) -> dict:
    """Save project or open Save As. Inspect dialogs; use a new filename to preserve the original."""
    return desktop.command("save_project_as" if save_as else "save_project")


@mcp.tool(annotations=EDIT)
@serialized
def filmora_import_media_dialog() -> dict:
    """Open the import chooser; list/select its window before filling paths."""
    return desktop.command("import_media")


@mcp.tool(annotations=EDIT)
@serialized
def filmora_fill_file_dialog(paths: list[str], submit: bool = False, save_as: bool = False) -> dict:
    """Fill an observed native file chooser (no shell). Default leaves it open for inspection.

    paths are absolute local paths. Existing files required for Open/Import; Save As requires a new filename.
    Select the actual dialog via filmora_select_window first. Custom Qt dialogs need explicit UI actions.
    """
    return desktop.file_dialog(paths, submit, save_as)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_playback(action: Literal["play_pause", "stop", "previous_frame", "next_frame",
                      "previous_second", "next_second", "project_start", "project_end",
                      "previous_edit", "next_edit", "previous_marker", "next_marker"],
                      repeat: int = 1) -> dict:
    """Playback/navigation shortcuts. Focus the timeline/player before navigation."""
    return desktop.command(action, repeat)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_edit(action: Literal["split", "trim_start", "trim_end", "cut", "copy", "paste",
                  "duplicate", "delete", "ripple_delete", "close_gap", "undo", "redo",
                  "group", "ungroup", "detach_audio", "mute", "freeze_frame"], repeat: int = 1) -> dict:
    """Edit selected timeline clips; inspect selection and playhead first, then verify the result."""
    return desktop.command(action, repeat)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_zoom(direction: Literal["in", "out", "fit"], repeat: int = 1) -> dict:
    """Zoom timeline using Filmora's default shortcuts."""
    return desktop.command({"in": "zoom_in", "out": "zoom_out", "fit": "zoom_fit"}[direction], repeat)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_marker(action: Literal["add", "edit", "red", "orange", "yellow", "green", "cyan",
                      "blue", "purple", "gray", "mark_in", "mark_out", "clear_in_out"] = "add") -> dict:
    """Add/edit marker, assign color mark, or control in/out range in the focused timeline/player."""
    name = {"add": "add_marker", "edit": "edit_marker"}.get(action, action)
    if action in {"red", "orange", "yellow", "green", "cyan", "blue", "purple", "gray"}:
        name = "marker_" + action
    return desktop.command(name)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_clip_panel(panel: Literal["properties", "crop_zoom", "speed", "stabilization",
                       "color_correction", "chroma_key", "motion_tracking", "color_match", "keyframing"]) -> dict:
    """Open a selected clip's editing panel. Inspect and adjust actual controls with ui_action/pixels."""
    return desktop.command(panel)


@mcp.tool(annotations=EDIT)
@serialized
def filmora_snapshot_frame() -> dict:
    """Ask Filmora to save a source/player frame via its Snapshot command (different from UI screenshot)."""
    return desktop.named_target("snapshot_frame")


@mcp.tool(annotations=EDIT)
@serialized
def filmora_open_export() -> dict:
    """Open export settings; inspect/set real fields. Does not start rendering, upload, or bypass license dialogs."""
    return desktop.named_target("export")


@mcp.tool(annotations=READ)
def filmora_wait(seconds: float = 1) -> dict:
    """Bounded wait for UI/render changes; follow with screenshot or inspection."""
    bounded(seconds, 0, 10, "seconds")
    time.sleep(seconds)
    return {"waited_seconds": seconds}


@mcp.tool(annotations=READ)
def filmora_verify_output(path: str, minimum_bytes: int = 1) -> dict:
    """Check a specific exported local file's size/timestamps; does not assert codec/content validity."""
    bounded(minimum_bytes, 1, 10**15, "minimum_bytes")
    p = local_file(path)
    stat = p.stat()
    return {"path": str(p), "bytes": stat.st_size, "modified_unix": stat.st_mtime,
            "meets_minimum_size": stat.st_size >= minimum_bytes,
            "verification": "File exists and size checked; inspect export completion and play output for content validation."}


@mcp.resource("filmora://capabilities")
def capabilities_resource() -> str:
    """Filmora command and feature catalog."""
    with desktop.lock:
        return json.dumps(desktop.runtime_capabilities(), indent=2)


@mcp.resource("filmora://workflow")
def workflow_resource() -> str:
    """Recommended observe-act-verify workflow."""
    return (ROOT / "docs" / "WORKFLOWS.md").read_text(encoding="utf-8")


@mcp.prompt()
def edit_video(task: str) -> str:
    """Plan and execute a visible, verified Filmora edit."""
    return (f"Edit in Filmora: {task}\nStart with status/windows and screenshot. Preserve existing work. "
            "Use capabilities and feature guides to choose tools. Inspect selection and focus before commands. "
            "Observe, perform one action, then inspect. Treat tool success as input dispatch, not completed editing. "
            "Use a separate Save As filename and verify the project title. Configure local export through real UI controls, "
            "verify settings before starting render, and verify the output after completion. Report unsupported features honestly.")


def main():
    parser = argparse.ArgumentParser(description="FilmoraMCP local Windows stdio server")
    parser.add_argument("--diagnose", action="store_true", help="Print JSON diagnostics without running MCP")
    args = parser.parse_args()
    if args.diagnose:
        print(json.dumps(filmora_status(), indent=2))
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
