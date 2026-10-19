from __future__ import annotations

import ctypes
from ctypes import wintypes
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import threading
import time
import uuid

from .catalog import COMMANDS, UI_TARGETS, UI_TARGET_TYPES
from .compatibility import (EDITOR_NAMES, MIN_MAJOR, TARGET_FEATURES, SHORTCUT_FALLBACKS,
                            version_info, command_policy, selector_levels, match_selectors, deduplicate_installations)
from .config import ROOT, load_config


class FilmoraError(RuntimeError):
    pass


def bounded(value, low, high, label):
    if not math.isfinite(value) or not low <= value <= high:
        raise FilmoraError(f"{label} must be between {low} and {high}")
    return value


def parse_chord(chord: str):
    parts = [x.strip().lower() for x in chord.split("+")]
    aliases = {"control": "ctrl", "return": "enter", "esc": "escape", "del": "delete"}
    parts = [aliases.get(p, p) for p in parts]
    modifiers = {"ctrl": 0x11, "alt": 0x12, "shift": 0x10}
    keys = {"enter": 13, "tab": 9, "space": 32, "escape": 27, "backspace": 8,
            "delete": 46, "left": 37, "up": 38, "right": 39, "down": 40,
            "home": 36, "end": 35, "pageup": 33, "pagedown": 34, "insert": 45,
            "[": 0xDB, "]": 0xDD, ",": 0xBC, ".": 0xBE, "/": 0xBF,
            "-": 0xBD, "=": 0xBB, "`": 0xC0, ";": 0xBA, "'": 0xDE, "\\": 0xDC}
    keys.update({f"f{i}": 0x6F + i for i in range(1, 25)})
    keys.update({c: ord(c.upper()) for c in "abcdefghijklmnopqrstuvwxyz0123456789"})
    if not parts or parts[-1] not in keys or any(p not in modifiers for p in parts[:-1]):
        raise FilmoraError("Use a chord such as ctrl+shift+s, left, f2, or escape. Windows/system keys are unsupported.")
    if len(set(parts[:-1])) != len(parts[:-1]):
        raise FilmoraError("Duplicate modifier")
    return [modifiers[p] for p in parts[:-1]], keys[parts[-1]]


def local_file(path: str, suffixes=None) -> Path:
    p = Path(path).expanduser()
    if not p.is_absolute() or str(p).startswith(("\\\\", "//")):
        raise FilmoraError("Provide an absolute local file path, not a network path")
    p = p.resolve(strict=True)
    if not p.is_file():
        raise FilmoraError("Path must identify a file")
    if suffixes and p.suffix.lower() not in suffixes:
        raise FilmoraError(f"Expected a file ending in {', '.join(suffixes)}")
    return p


class FilmoraDesktop:
    """Serialized, process-scoped Windows input and short-lived observations."""

    def __init__(self, config=None):
        self.config = config or load_config()
        self.lock = threading.RLock()
        self.observations = {}
        self.selected_hwnd = None
        self._native_loaded = False
        self._version_cache = {}

    def native(self):
        if self._native_loaded:
            return
        if os.name != "nt":
            raise FilmoraError("Filmora desktop automation requires an interactive Windows session")
        import psutil
        import win32api
        import win32con
        import win32gui
        import win32process
        self.psutil, self.api, self.con = psutil, win32api, win32con
        self.gui, self.process = win32gui, win32process
        # Do this before importing UIA or capturing pixels.
        try:
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except (AttributeError, OSError):
            pass
        self._native_loaded = True

    def installations(self):
        roots = [Path(os.environ.get("LOCALAPPDATA", "")) / "Wondershare",
                 Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Wondershare",
                 Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Wondershare"]
        for variable in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
            base = Path(os.environ.get(variable, "C:/Program Files"))
            if base.is_dir():
                roots.extend(p for pattern in ("Wondershare Filmora*", "Filmora*") for p in base.glob(pattern) if p.is_dir())
        paths = []
        if self.config.get("executable"):
            paths.append(Path(self.config["executable"]))
        for root in roots:
            if root.is_dir():
                for filename in ("Wondershare Filmora.exe", "Filmora.exe"):
                    paths.extend(root.glob(f"**/{filename}"))
        # Non-default installations can advertise their editor through Windows App Paths.
        if os.name == "nt":
            import winreg
            for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                for name in ("Wondershare Filmora.exe", "Filmora.exe"):
                    for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
                        try:
                            key_name = "Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\" + name
                            with winreg.OpenKey(hive, key_name, 0, winreg.KEY_READ | view) as key:
                                value = winreg.QueryValueEx(key, "")[0]
                                paths.append(Path(os.path.expandvars(value.strip('"'))))
                        except OSError:
                            pass
        return deduplicate_installations({str(p.resolve()) for p in paths if p.is_file()})

    def executable_version(self, path):
        p = Path(path)
        try:
            stat = p.stat()
            key = (str(p), stat.st_mtime_ns, stat.st_size, str(self.config.get("filmora_major_version")))
        except OSError:
            key = (str(p), None, None, str(self.config.get("filmora_major_version")))
        if key in self._version_cache:
            return self._version_cache[key]
        metadata = {}
        if os.name == "nt":
            try:
                import win32api
                raw = win32api.GetFileVersionInfo(str(p), chr(92))
                for name in ("ProductVersion", "FileVersion"):
                    high, low = raw[name + "MS"], raw[name + "LS"]
                    if high or low:
                        metadata[name] = ".".join(str(n) for n in (high >> 16, high & 65535, low >> 16, low & 65535))
            except Exception:
                pass
        try:
            info = version_info(p, metadata, self.config.get("filmora_major_version"))
        except ValueError as exc:
            raise FilmoraError(str(exc)) from exc
        self._version_cache[key] = info
        return info

    def runtime_version(self):
        rows = self.windows()
        if self.selected_hwnd is not None:
            rows = [r for r in rows if r["hwnd"] == self.selected_hwnd]
        paths = {r["executable"] for r in rows}
        if not paths and self.selected_hwnd is None:
            paths = set(self.installations())
        if len(paths) == 1:
            return self.executable_version(next(iter(paths)))
        return {**version_info("", override=self.config.get("filmora_major_version")),
                "selection_required": len(paths) > 1,
                "note": "Select an installed/running editor when multiple installations are present"}

    def runtime_capabilities(self, probe_ui=False):
        from .catalog import capabilities
        version = self.runtime_version()
        result = capabilities(self.config["shortcut_overrides"], version["major"], version)
        if probe_ui:
            state = self.inspect(max_depth=25, max_elements=2500)
            probes = {}
            for target, internal in UI_TARGETS.items():
                probes[target] = {"status": "not-exposed-in-current-view"}
                for selectors in selector_levels(target, internal, UI_TARGET_TYPES[target], self.config.get("ui_target_overrides")):
                    matches = match_selectors(state["elements"], selectors)
                    if matches:
                        status = ("ambiguous" if len(matches) > 1 else
                                  "exposed-enabled" if matches[0]["enabled"] else "exposed-disabled")
                        probes[target] = {"status": status, "matches": matches}
                        break
            result["live_ui"] = {"observation_id": state["observation_id"], "truncated": state["truncated"], "targets": probes}
            for target, feature in TARGET_FEATURES.items():
                result["features"][feature]["live_status"] = probes[target]["status"]
        return result

    def windows(self):
        self.native()
        rows = []
        def visit(hwnd, _):
            if not self.gui.IsWindowVisible(hwnd):
                return
            try:
                _, pid = self.process.GetWindowThreadProcessId(hwnd)
                proc = self.psutil.Process(pid)
                name = proc.name().lower()
                # Never attach based solely on a misleading window title.
                if name not in EDITOR_NAMES:
                    return
                rect = list(self.gui.GetWindowRect(hwnd))
                if rect[2] <= rect[0] or rect[3] <= rect[1]:
                    return
                rows.append({"hwnd": hwnd, "pid": pid, "title": self.gui.GetWindowText(hwnd),
                             "executable": proc.exe(), "rect": rect,
                             "minimized": bool(self.gui.IsIconic(hwnd)),
                             "owner": self.gui.GetWindow(hwnd, self.con.GW_OWNER),
                             "enabled": bool(self.gui.IsWindowEnabled(hwnd)),
                             "version": self.executable_version(proc.exe())})
            except (self.psutil.Error, OSError):
                return
        self.gui.EnumWindows(visit, None)
        return rows

    def target(self, hwnd=None):
        rows = self.windows()
        handle = hwnd if hwnd is not None else self.selected_hwnd
        if handle is not None:
            candidates = [r for r in rows if r["hwnd"] == handle]
            if len(candidates) != 1:
                raise FilmoraError("Selected Filmora window disappeared. List windows and select again.")
            return candidates[0]
        # Prefer the single main window; require explicit choice with multiple instances.
        candidates = [r for r in rows if not r["owner"]]
        if len(candidates) != 1:
            if len(rows) == 1:
                return rows[0]
            raise FilmoraError(f"Expected one Filmora main window, found {len(candidates)}. Use filmora_windows/select_window.")
        return candidates[0]

    def select(self, hwnd):
        row = self.target(hwnd)
        self.selected_hwnd = row["hwnd"]
        self.invalidate()
        return row

    def launch(self):
        existing = self.windows()
        if existing:
            return {"already_running": True, "windows": existing}
        paths = self.installations()
        if not paths:
            raise FilmoraError("Filmora executable not found. Set FILMORA_EXE or config.local.json executable.")
        configured = self.config.get("executable")
        if not configured and len(paths) > 1:
            raise FilmoraError(f"Multiple installations found; set executable in config.local.json: {paths}")
        exe = local_file(configured or paths[0], {".exe"})
        if exe.name.lower() not in EDITOR_NAMES:
            raise FilmoraError("Executable must be Filmora.exe or Wondershare Filmora.exe")
        version = self.executable_version(exe)
        if version["supported_range"] is False:
            raise FilmoraError("Minimum supported Filmora is X / version 10")
        subprocess.Popen([str(exe)], cwd=str(exe.parent), shell=False)
        return {"launched": str(exe), "version": version,
                "next": "Wait, then list windows; startup/recovery dialogs may require attention."}

    def guard(self):
        self.native()
        if (ROOT / "PAUSE").exists():
            raise FilmoraError("Input paused: remove the FilmoraMCP/PAUSE file to resume")
        if self.gui.GetCursorPos() == (0, 0):
            raise FilmoraError("Mouse is at the emergency-stop corner (0,0); move it to resume")

    def activate(self, row):
        self.guard()
        if row.get("version", {}).get("supported_range") is False:
            raise FilmoraError("Minimum supported Filmora is X / version 10")
        hwnd = row["hwnd"]
        if self.gui.IsIconic(hwnd):
            self.gui.ShowWindow(hwnd, self.con.SW_RESTORE)
        self.gui.SetForegroundWindow(hwnd)
        time.sleep(0.12)
        self.foreground(row)

    def foreground(self, row):
        self.guard()
        if row.get("version", {}).get("supported_range") is False:
            raise FilmoraError("Minimum supported Filmora is X / version 10")
        if not self.gui.IsWindowEnabled(row["hwnd"]):
            raise FilmoraError("Window is blocked by a modal. List/select the dialog first.")
        active = self.gui.GetForegroundWindow()
        if active != row["hwnd"]:
            raise FilmoraError("Filmora target is not foreground. Select/activate its actual dialog and reobserve.")

    def invalidate(self):
        self.observations.clear()

    def _remember(self, row, **extra):
        now = time.monotonic()
        ttl = self.config["observation_ttl_seconds"]
        self.observations = {k: v for k, v in self.observations.items() if now - v["created"] < ttl}
        token = uuid.uuid4().hex
        self.observations[token] = {"created": now, "row": row, **extra}
        return token

    def observed(self, token, kind):
        obs = self.observations.get(token)
        if not obs or kind not in obs:
            raise FilmoraError(f"Missing/stale {kind} observation. Capture/inspect again.")
        if time.monotonic() - obs["created"] > self.config["observation_ttl_seconds"]:
            raise FilmoraError("Observation expired. Capture/inspect again.")
        row = self.target(obs["row"]["hwnd"])
        if row["rect"] != obs["row"]["rect"] or row["pid"] != obs["row"]["pid"]:
            raise FilmoraError("Window changed size/position/process. Capture/inspect again.")
        return obs, row

    def screenshot(self, hwnd=None, max_width=1600, crop=None, save=False, mode="visible"):
        from PIL import ImageGrab
        bounded(max_width, 320, 7680, "max_width")
        row = self.target(hwnd)
        if row["minimized"]:
            raise FilmoraError("Restore the Filmora window before capture")
        if mode == "window":
            im = ImageGrab.grab(window=row["hwnd"], all_screens=True).convert("RGB")
        elif mode == "visible":
            # Desktop pixels include GPU-rendered previews more reliably. Do not bring
            # windows forward in a read tool or capture an unrelated foreground app.
            if self.gui.GetForegroundWindow() != row["hwnd"]:
                raise FilmoraError("Visible capture requires the selected Filmora window in foreground; activate it first")
            left, top, right, bottom = row["rect"]
            for x, y in [(left + 10, top + 10), (right - 11, top + 10),
                         (left + 10, bottom - 11), (right - 11, bottom - 11),
                         ((left + right) // 2, (top + bottom) // 2)]:
                hit = self.gui.WindowFromPoint((x, y))
                if self.gui.GetAncestor(hit, 2) != row["hwnd"]:
                    raise FilmoraError("Window is partly covered/offscreen; use mode=window or reveal the target and retry")
            im = ImageGrab.grab(bbox=tuple(row["rect"]), all_screens=True).convert("RGB")
        else:
            raise FilmoraError("Screenshot mode must be window or visible")
        full_size = im.size
        offset = [0, 0]
        if crop is not None:
            if len(crop) != 4:
                raise FilmoraError("crop must be [left,top,right,bottom] in original window pixels")
            l, t, r, b = crop
            if not (0 <= l < r <= im.width and 0 <= t < b <= im.height):
                raise FilmoraError("Crop falls outside the captured window")
            offset = [l, t]
            im = im.crop(tuple(crop))
        original = im.size
        if im.width > max_width:
            h = max(1, round(im.height * max_width / im.width))
            im = im.resize((max_width, h))
        stream = io.BytesIO()
        im.save(stream, format="PNG")
        data = stream.getvalue()
        geometry = {"image_size": list(im.size), "source_size": list(original),
                    "full_window_size": list(full_size), "crop_offset": offset}
        token = self._remember(row, screenshot=geometry)
        meta = {"observation_id": token, "window": row, "capture_mode": mode, **geometry,
                "coordinate_space": "Displayed image pixels; use this observation_id with click/drag/scroll.",
                "expires_seconds": self.config["observation_ttl_seconds"],
                "sha256": hashlib.sha256(data).hexdigest()}
        if save:
            folder = Path(self.config["capture_dir"]).resolve()
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / f"filmora-{time.strftime('%Y%m%d-%H%M%S')}-{token[:8]}.png"
            with path.open("xb") as out:
                out.write(data)
            meta["saved_path"] = str(path)
        return meta, data

    def point(self, obs, x, y):
        g = obs["screenshot"]
        w, h = g["image_size"]
        bounded(x, 0, w - 1, "x")
        bounded(y, 0, h - 1, "y")
        # PrintWindow/ImageGrab window includes non-client frame, unlike UIA client coords.
        ox, oy = g["crop_offset"]
        sx, sy = g["source_size"][0] / w, g["source_size"][1] / h
        r = obs["row"]["rect"]
        return round(r[0] + ox + x * sx), round(r[1] + oy + y * sy)

    def mouse_target(self, row, point):
        self.foreground(row)
        hit = self.gui.WindowFromPoint(point)
        root = self.gui.GetAncestor(hit, 2)  # GA_ROOT
        if root != row["hwnd"]:
            raise FilmoraError("Coordinate is covered by another window/menu; select it and capture again")

    def _modifiers(self, names):
        table = {"ctrl": 17, "alt": 18, "shift": 16}
        if len(names) != len(set(names)) or any(k not in table for k in names):
            raise FilmoraError("modifiers may contain ctrl, alt, shift once each")
        return [table[k] for k in names]

    def _key_event(self, vk, up=False):
        self.api.keybd_event(vk, 0, self.con.KEYEVENTF_KEYUP if up else 0, 0)

    def press(self, chord, repeat=1):
        mods, key = parse_chord(chord)
        bounded(repeat, 1, 100, "repeat")
        row = self.target()
        self.activate(row)
        self.invalidate()
        pressed = []
        try:
            for m in mods:
                self.foreground(row)
                self._key_event(m)
                pressed.append(m)
            for _ in range(repeat):
                self.foreground(row)
                self._key_event(key)
                self._key_event(key, True)
                time.sleep(0.04)
        finally:
            for m in reversed(pressed):
                self._key_event(m, True)
        return {"dispatched": chord, "repeat": repeat, "verified": False,
                "next": "Inspect state/screenshot; dispatched input is not proof of a completed edit."}

    def command(self, action, repeat=1):
        if action not in COMMANDS:
            raise FilmoraError("Unknown command; use filmora_commands")
        version = self.target().get("version", {})
        candidate = command_policy(COMMANDS, version.get("major"), self.config["shortcut_overrides"])[action]
        if not candidate["dispatchable"]:
            raise FilmoraError(candidate["reason"])
        return {"action": action, "profile": candidate["profile"], **self.press(candidate["keys"], repeat)}

    def click(self, token, x, y, button="left", count=1, modifiers=None):
        obs, row = self.observed(token, "screenshot")
        p = self.point(obs, x, y)
        flags = {"left": (2, 4), "right": (8, 16), "middle": (32, 64)}
        if button not in flags or count not in {1, 2}:
            raise FilmoraError("button: left/right/middle; count: 1/2")
        mods = self._modifiers(modifiers or [])
        self.activate(row)
        self.mouse_target(row, p)
        self.invalidate()
        pressed = []
        try:
            for m in mods:
                self._key_event(m)
                pressed.append(m)
            self.api.SetCursorPos(p)
            for _ in range(count):
                self.mouse_target(row, p)
                self.api.mouse_event(flags[button][0], 0, 0, 0, 0)
                self.api.mouse_event(flags[button][1], 0, 0, 0, 0)
                time.sleep(0.07)
        finally:
            for m in reversed(pressed):
                self._key_event(m, True)
        return {"dispatched": "click", "verified": False}

    def drag(self, token, start_x, start_y, end_x, end_y, duration=0.8, modifiers=None):
        bounded(duration, 0.2, 10, "duration")
        obs, row = self.observed(token, "screenshot")
        start, end = self.point(obs, start_x, start_y), self.point(obs, end_x, end_y)
        mods = self._modifiers(modifiers or [])
        self.activate(row)
        self.mouse_target(row, start)
        self.mouse_target(row, end)
        self.invalidate()
        pressed, down = [], False
        try:
            for m in mods:
                self._key_event(m)
                pressed.append(m)
            self.api.SetCursorPos(start)
            self.api.mouse_event(2, 0, 0, 0, 0)
            down = True
            steps = max(10, round(duration * 40))
            for i in range(1, steps + 1):
                self.foreground(row)
                p = tuple(round(a + (b - a) * i / steps) for a, b in zip(start, end))
                self.mouse_target(row, p)
                self.api.SetCursorPos(p)
                time.sleep(duration / steps)
        finally:
            if down:
                self.api.mouse_event(4, 0, 0, 0, 0)
            for m in reversed(pressed):
                self._key_event(m, True)
        return {"dispatched": "drag", "verified": False}

    def scroll(self, token, x, y, ticks, horizontal=False, modifiers=None):
        bounded(ticks, -30, 30, "ticks")
        obs, row = self.observed(token, "screenshot")
        p = self.point(obs, x, y)
        mods = self._modifiers(modifiers or [])
        self.activate(row)
        self.mouse_target(row, p)
        self.invalidate()
        pressed = []
        try:
            for m in mods:
                self._key_event(m)
                pressed.append(m)
            self.api.SetCursorPos(p)
            self.api.mouse_event(0x1000 if horizontal else 0x800, 0, 0, ticks * 120, 0)
        finally:
            for m in reversed(pressed):
                self._key_event(m, True)
        return {"dispatched": "scroll", "verified": False}

    def _uia(self, hwnd):
        from pywinauto import Desktop
        return Desktop(backend="uia").window(handle=hwnd).wrapper_object()

    def inspect(self, hwnd=None, max_depth=12, max_elements=600, query=""):
        bounded(max_depth, 1, 30, "max_depth")
        bounded(max_elements, 1, 3000, "max_elements")
        row = self.target(hwnd)
        root = self._uia(row["hwnd"])
        elements, records, errors = {}, [], []
        pending, visited = [(root, 0)], 0
        while pending and visited < max_elements:
            control, depth = pending.pop()
            visited += 1
            try:
                info = control.element_info
                name, auto_id = info.name or "", info.automation_id or ""
                rect = info.rectangle
                record = {"element_id": str(visited), "name": name, "automation_id": auto_id,
                          "control_type": info.control_type, "depth": depth,
                          "enabled": bool(control.is_enabled()), "visible": bool(control.is_visible()),
                          "rect": [rect.left, rect.top, rect.right, rect.bottom]}
                try:
                    record["focused"] = bool(control.has_keyboard_focus())
                except Exception:
                    record["focused"] = False
                # Read the values needed to configure actual editing/export fields.
                # Qt controls expose different UIA patterns; unavailable patterns are
                # reported by omission instead of pretending the control is writable.
                if info.control_type in {"Edit", "Document", "ComboBox"}:
                    try:
                        iface = control.iface_value
                        record["value"] = str(iface.CurrentValue)[:self.config["max_text_length"]]
                        record["read_only"] = bool(iface.CurrentIsReadOnly)
                    except Exception:
                        pass
                if info.control_type in {"Slider", "Spinner", "ProgressBar", "ScrollBar"}:
                    try:
                        iface = control.iface_range_value
                        record["range"] = {"value": iface.CurrentValue, "minimum": iface.CurrentMinimum,
                                           "maximum": iface.CurrentMaximum, "small_change": iface.CurrentSmallChange,
                                           "large_change": iface.CurrentLargeChange,
                                           "read_only": bool(iface.CurrentIsReadOnly)}
                    except Exception:
                        pass
                if info.control_type in {"CheckBox", "RadioButton", "ListItem", "TabItem", "TreeItem"}:
                    try:
                        record["selected"] = bool(control.iface_selection_item.CurrentIsSelected)
                    except Exception:
                        pass
                    try:
                        record["toggle_state"] = int(control.iface_toggle.CurrentToggleState)
                    except Exception:
                        pass
                if info.control_type in {"ComboBox", "TreeItem"}:
                    try:
                        record["expand_state"] = int(control.iface_expand_collapse.CurrentExpandCollapseState)
                    except Exception:
                        pass
                if not query or query.casefold() in (name + " " + auto_id + " " + info.control_type).casefold():
                    records.append(record)
                    elements[str(visited)] = control
                if depth < max_depth:
                    pending.extend((c, depth + 1) for c in reversed(control.children()))
            except Exception as exc:
                errors.append(type(exc).__name__)
        token = self._remember(row, elements=elements)
        return {"observation_id": token, "window": row, "elements": records,
                "truncated": bool(pending), "visited": visited, "errors": errors[:10],
                "expires_seconds": self.config["observation_ttl_seconds"],
                "next": "Use element_id with this observation_id. Increase depth/budget if truncated; use screenshots for canvas items."}

    def _element(self, token, element_id):
        obs, row = self.observed(token, "elements")
        control = obs["elements"].get(str(element_id))
        if control is None:
            raise FilmoraError("Element not present in this observation")
        if not control.is_visible() or not control.is_enabled():
            raise FilmoraError("Element is disabled/hidden; select a clip or resolve dialog first")
        # Check runtime ID rather than accepting detached objects from old trees.
        if control.element_info.process_id != row["pid"]:
            raise FilmoraError("Element no longer belongs to target Filmora process")
        return control, row

    def ui_action(self, token, element_id, action="click", value=None):
        control, row = self._element(token, element_id)
        self.activate(row)
        self.invalidate()
        self.foreground(row)
        if action == "click":
            rect = control.rectangle()
            self.mouse_target(row, (rect.mid_point().x, rect.mid_point().y))
            control.click_input()
        elif action == "invoke":
            control.iface_invoke.Invoke()
        elif action == "focus":
            control.set_focus()
        elif action == "set_value":
            if value is None or len(value) > self.config["max_text_length"]:
                raise FilmoraError("Provide a bounded value")
            iface = control.iface_value
            if iface.CurrentIsReadOnly:
                raise FilmoraError("Element is read-only")
            iface.SetValue(value)
        elif action == "select":
            control.select(value)
        elif action == "toggle":
            control.iface_toggle.Toggle()
        elif action == "expand":
            control.iface_expand_collapse.Expand()
        elif action == "collapse":
            control.iface_expand_collapse.Collapse()
        elif action == "set_range":
            number = float(value)
            iface = control.iface_range_value
            if iface.CurrentIsReadOnly:
                raise FilmoraError("Range is read-only")
            bounded(number, iface.CurrentMinimum, iface.CurrentMaximum, "range value")
            iface.SetValue(number)
        else:
            raise FilmoraError("Unsupported UI action")
        return {"dispatched": action, "element_id": element_id, "verified": False}

    def named_target(self, target):
        if target not in UI_TARGETS:
            raise FilmoraError("Unknown target; use filmora_capabilities for names")
        state = self.inspect(max_depth=25, max_elements=2500)
        if state.get("truncated"):
            raise FilmoraError("Control inspection truncated; inspect a specific control or use screenshot pixels")
        levels = selector_levels(target, UI_TARGETS[target], UI_TARGET_TYPES[target], self.config.get("ui_target_overrides"))
        for selectors in levels:
            matches = match_selectors(state["elements"], selectors)
            if not matches:
                continue
            if len(matches) != 1:
                raise FilmoraError(f"Target {target} not uniquely exposed ({len(matches)} matches). Inspect live UI/screenshots.")
            if not matches[0].get("enabled", True):
                raise FilmoraError(f"Target {target} is disabled; select relevant media/clip. No shortcut fallback was sent.")
            return {"target": target, "route": "live-control",
                    **self.ui_action(state["observation_id"], matches[0]["element_id"])}
        fallback = SHORTCUT_FALLBACKS.get(target)
        if fallback and target not in self.config.get("ui_target_overrides", {}):
            return {"target": target, "route": "version-profile-shortcut", **self.command(fallback)}
        raise FilmoraError(f"Target {target} not uniquely exposed (0 matches). Use screenshot pixels or ui_target_overrides for this version/language.")

    def type_text(self, token, element_id, text):
        if not text or len(text) > self.config["max_text_length"]:
            raise FilmoraError("Provide non-empty text within max_text_length")
        control, row = self._element(token, element_id)
        if control.element_info.control_type not in {"Edit", "Document"}:
            raise FilmoraError("Text typing requires an observed Edit/Document control; focus and inspect an editable field")
        if not control.has_keyboard_focus():
            raise FilmoraError("Field is not focused. Use UI focus, re-inspect, then type")
        self.activate(row)
        if not control.has_keyboard_focus():
            raise FilmoraError("Focus changed during activation; re-inspect")
        self.invalidate()
        # UTF-16 SendInput inserts literal Unicode without clipboard changes or shortcut syntax.
        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                        ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]
        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                        ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]
        class UNION(ctypes.Union):
            _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT)]
        class INPUT(ctypes.Structure):
            _anonymous_ = ("u",)
            _fields_ = [("type", wintypes.DWORD), ("u", UNION)]
        raw = text.encode("utf-16-le")
        for i in range(0, len(raw), 2):
            self.foreground(row)
            if not control.has_keyboard_focus():
                raise FilmoraError("Text input focus changed; some text may have been inserted. Inspect before retrying.")
            unit = int.from_bytes(raw[i:i+2], "little")
            pair = (INPUT * 2)(INPUT(type=1, ki=KEYBDINPUT(wScan=unit, dwFlags=4)),
                               INPUT(type=1, ki=KEYBDINPUT(wScan=unit, dwFlags=6)))
            if ctypes.windll.user32.SendInput(2, pair, ctypes.sizeof(INPUT)) != 2:
                raise FilmoraError("SendInput failed; check integrity level and inspect before retrying")
        return {"dispatched": "type_text", "characters": len(text), "verified": False}

    def file_dialog(self, paths, submit=False, save_as=False):
        if not 1 <= len(paths) <= 100:
            raise FilmoraError("Provide 1 to 100 paths")
        if save_as:
            if len(paths) != 1:
                raise FilmoraError("Save dialog accepts one path")
            p = Path(paths[0]).expanduser()
            if not p.is_absolute() or str(p).startswith(("\\\\", "//")) or not p.parent.is_dir():
                raise FilmoraError("Save path must be absolute and its local parent directory must exist")
            if p.exists():
                raise FilmoraError("Save target exists; choose a new filename")
            valid = [p.resolve()]
        else:
            valid = [local_file(p) for p in paths]
        row = self.target()
        # Only conventional native dialogs with an unambiguous filename field.
        if self.gui.GetClassName(row["hwnd"]) != "#32770":
            raise FilmoraError("Select the native Open/Save/Import dialog first. Use explicit UI controls for custom Filmora dialogs.")
        root = self._uia(row["hwnd"])
        fields = [c for c in root.descendants(control_type="Edit")
                  if c.element_info.automation_id == "1148" and c.is_visible() and c.is_enabled()]
        if len(fields) != 1:
            raise FilmoraError("Filename field not unique. Inspect and set a specific control.")
        self.activate(row)
        self.invalidate()
        text = str(valid[0]) if len(valid) == 1 else " ".join('"' + str(p) + '"' for p in valid)
        fields[0].set_edit_text(text)
        if submit:
            self.foreground(row)
            buttons = [c for c in root.descendants(control_type="Button")
                       if c.element_info.automation_id == "1" and c.is_enabled()]
            if len(buttons) != 1:
                raise FilmoraError("Filename set, but submit button ambiguous; inspect dialog")
            buttons[0].invoke()
        return {"paths": [str(p) for p in valid], "submitted": submit,
                "next": "Inspect for prompts, media matching settings, or overwrite warnings. Verify project title/media list."}


desktop = FilmoraDesktop()
