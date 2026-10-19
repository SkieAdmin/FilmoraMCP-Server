"""Version-aware policies for Windows Filmora X/10 and newer.

Version numbers choose candidate routes; they never establish live feature availability.
Only 13.6.13 has been exercised against a local editor so far.
"""
from __future__ import annotations

from pathlib import PureWindowsPath
import re

MIN_MAJOR = 10
LAST_PROFILE_MAJOR = 16
EDITOR_NAMES = {"wondershare filmora.exe", "filmora.exe"}
LEGACY_SOURCE = "https://filmora.wondershare.com/guide/filmora-keyboard-shortcuts-for-windows.html"
MODERN_SOURCE = "https://filmora.wondershare.com/guide/keyboard-shortcuts-on-windows.html"

# Commands explicitly present in Wondershare's Filmora 9/10 Windows reference.
LEGACY_COMMANDS = set("""new_project open_project save_project save_project_as archive_project import_media
record_voiceover preferences undo redo cut copy paste delete ripple_delete select_all copy_effects paste_effects
properties split trim_start trim_end crop_zoom rotate_clockwise rotate_counterclockwise speed freeze_frame
detach_audio mute stabilization color_correction chroma_key insert overwrite rename apply_asset play_pause stop
fullscreen previous_frame next_frame previous_edit next_edit previous_second next_second previous_marker
next_marker project_start project_end clip_start clip_end zoom_in zoom_out zoom_fit mark_in mark_out add_marker
edit_marker open_export""".split())
LEGACY_OVERRIDES = {"preferences": "ctrl+,", "rename": "enter", "chroma_key": "ctrl+alt+g"}
# This old table assigns Ctrl+Alt+C to both Copy Effects and Color Correction.
# Dispatch neither ambiguous action on X unless a user supplies an explicit override.
LEGACY_AMBIGUOUS = {"copy_effects", "color_correction"}
COMMON_COMMANDS = LEGACY_COMMANDS - LEGACY_AMBIGUOUS - {"rename", "preferences", "chroma_key"}

# Conservative, documented feature-generation boundaries. Unlisted features are
# deliberately unverified by version instead of assigned a fabricated introduction.
FEATURE_MINIMUMS = {"smart_cutout": 12, "ai_copilot": 13, "text_based_editing": 13, "ai_music": 13,
                    "planar_tracking": 14, "multicam": 14, "smart_short_clips": 14,
                    "video_enhancer": 14, "video_denoise": 14}
FEATURE_SOURCES = {
    12: "https://filmora.wondershare.com/whats-new-in-filmora-video-editor.html",
    13: "https://filmora.wondershare.com/answers/latest-features-in-filmora-13.html",
    14: "https://support.wondershare.com/how-tos/filmora/whats-new-in-filmora-14.html",
}
TARGET_FEATURES = {"ai_copilot": "ai_copilot", "speech_to_text": "speech_to_text",
                   "ai_translation": "ai_translation", "ai_object_remover": "object_remover"}

# Exact labels are candidates, not substring matches or fixed coordinates.
TEXT_ALIASES = {
    "media": ("Media",), "stock_media": ("Stock Media", "Stock"), "audio": ("Audio",),
    "titles": ("Titles", "Text/Credit"), "transitions": ("Transitions",), "effects": ("Effects",),
    "filters": ("Filters",), "stickers": ("Stickers", "Elements"), "import": ("Import",),
    "export": ("Export",), "audio_mixer": ("Audio Mixer",), "audio_recorder": ("Record Voiceover", "Record Voice-Over"),
    "snapshot_frame": ("Snapshot", "Take Snapshot"), "zoom_fit": ("Zoom to Fit Timeline",),
}
LIBRARIES = {"media", "stock_media", "audio", "titles", "transitions", "effects", "filters", "stickers"}
SHORTCUT_FALLBACKS = {"export": "open_export", "import": "import_media", "advanced_color": "color_correction",
                      "audio_recorder": "record_voiceover", "snapshot_frame": "snapshot_frame",
                      "zoom_in": "zoom_in", "zoom_out": "zoom_out", "zoom_fit": "zoom_fit"}


def deduplicate_installations(paths):
    """Filmora.exe can be a bootstrapper beside the real editor; prefer the editor in that directory."""
    grouped = {}
    for value in paths:
        p = PureWindowsPath(str(value))
        if p.name.casefold() not in EDITOR_NAMES:
            continue
        key = str(p.parent).casefold()
        previous = grouped.get(key)
        if previous is None or p.name.casefold() == "wondershare filmora.exe":
            grouped[key] = str(value)
    return sorted(grouped.values(), reverse=True)


def parse_major(value):
    if isinstance(value, bool) or value is None:
        return None
    text = str(value).strip()
    if text.casefold() in {"x", "filmora x", "wondershare filmora x"}:
        return 10
    match = re.fullmatch(r"(?:(?:wondershare\s+)?filmora\s*|v)?(\d{1,3})(?:[.,]\d+){0,3}", text, re.I)
    return int(match[1]) if match and int(match[1]) > 0 else None


def path_version(path):
    # Only adjacent version-shaped folder names, never any digits in a user path.
    for part in reversed(PureWindowsPath(str(path)).parts[:-1][-3:]):
        if re.fullmatch(r"\d{1,3}(?:\.\d+){1,3}", part) or re.fullmatch(
                r"(?:Wondershare\s+)?Filmora\s*(?:X|\d{1,3})", part, re.I):
            major = parse_major(part)
            if major:
                return {"major": major, "version": part, "source": "installation-directory"}
    return {"major": None, "version": None, "source": "unknown"}


def version_info(path, metadata=None, override=None):
    metadata = metadata or {}
    for key in ("ProductVersion", "FileVersion"):
        major = parse_major(metadata.get(key))
        if major:
            info = {"major": major, "version": str(metadata[key]), "source": f"executable-{key}"}
            break
    else:
        info = path_version(path)
    manual = parse_major(override)
    if override is not None and (manual is None or manual < MIN_MAJOR):
        raise ValueError("filmora_major_version must be X or an integer/version >=10, or null for auto")
    if manual is not None:
        if info["major"] is not None and manual != info["major"]:
            raise ValueError("Configured Filmora version conflicts with the detected executable/version directory")
        if info["major"] is None:
            info = {"major": manual, "version": str(override), "source": "configuration"}
    return {**info, "supported_range": None if info["major"] is None else info["major"] >= MIN_MAJOR,
            "version_known": info["major"] is not None, "profile": profile(info["major"])}


def profile(major):
    if major is None:
        return "unknown-adaptive"
    if major < MIN_MAJOR:
        return "unsupported-pre-x"
    if major == 10:
        return "filmora-x-10"
    if major <= LAST_PROFILE_MAJOR:
        return f"filmora-{major}"
    return "future-adaptive"


def command_policy(commands, major=None, overrides=None):
    overrides = overrides or {}
    result = {}
    for name, entry in commands.items():
        keys, reason = entry["keys"], None
        source = MODERN_SOURCE
        if major is not None and major < MIN_MAJOR:
            reason = "Filmora releases older than X/10 are outside the target range"
        elif name in overrides:
            keys, source = overrides[name], "configuration"
        elif major == 10:
            source = LEGACY_SOURCE
            if name not in LEGACY_COMMANDS:
                reason = "No verified Filmora X default shortcut; use live UI or an explicit shortcut override"
            elif name in LEGACY_AMBIGUOUS:
                reason = "Conflicting assignments in the legacy reference; use live UI or configure the actual shortcut"
            keys = LEGACY_OVERRIDES.get(name, keys)
        elif major is None or major > LAST_PROFILE_MAJOR:
            if name not in COMMON_COMMANDS:
                reason = "Unknown/future version: only common documented commands are enabled automatically"
            source = "shared-legacy-and-modern-references"
        result[name] = {**entry, "keys": keys if reason is None else None, "dispatchable": reason is None,
                        "reason": reason, "source": source, "profile": profile(major),
                        "verification": "Candidate shortcut; focus, selection and custom presets still require live verification"}
    return result


def feature_policy(features, major=None):
    result = {}
    for name, entry in features.items():
        minimum = FEATURE_MINIMUMS.get(name)
        ineligible = major is not None and (major < MIN_MAJOR or (minimum is not None and major < minimum))
        result[name] = {**entry, "minimum_major": minimum,
                        "version_status": "version-ineligible" if ineligible else "requires-live-verification",
                        "availability": "Not confirmed: inspect actual UI, clip selection, license and assets",
                        "boundary_source": FEATURE_SOURCES.get(minimum), "live_status": "unprobed"}
    return result


def selector_levels(target, internal_name, internal_type, overrides=None):
    levels = []
    if overrides and target in overrides:
        # A customization is authoritative; do not silently fall through to unrelated English labels.
        return [[dict(s) for s in overrides[target]]]
    types = ("CheckBox", "TabItem", "Button", "RadioButton") if target in LIBRARIES else ("Button",)
    internal_types = types if target in LIBRARIES else (internal_type,)
    levels.append([{key: internal_name, "control_type": kind}
                   for key in ("name", "automation_id") for kind in internal_types])
    levels.append([{"name": label, "control_type": kind}
                   for label in TEXT_ALIASES.get(target, ()) for kind in types])
    return levels


def match_selectors(elements, selectors):
    return [e for e in elements if e.get("visible", True) and any(
        all(e.get(key) == value for key, value in selector.items()) for selector in selectors)]
