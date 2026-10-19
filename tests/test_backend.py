import time
from types import SimpleNamespace

import pytest

from filmora_mcp.backend import FilmoraDesktop, FilmoraError, local_file, parse_chord
from filmora_mcp.catalog import COMMANDS


@pytest.fixture
def desk():
    d = FilmoraDesktop({"observation_ttl_seconds": 60, "shortcut_overrides": {}, "max_text_length": 20000})
    row = {"hwnd": 42, "pid": 99, "rect": [100, 200, 2100, 1200]}
    d.target = lambda hwnd=None: dict(row)
    return d


def test_all_shipped_shortcuts_are_dispatchable():
    for entry in COMMANDS.values():
        parse_chord(entry["keys"])


@pytest.mark.parametrize("chord", ["win+r", "ctrl+ctrl+s", "ctrl++", "alt+unknown", "", "powershell.exe"])
def test_rejects_malformed_or_system_chords(chord):
    with pytest.raises(FilmoraError):
        parse_chord(chord)


def test_cropped_resized_image_coordinates_map_to_desktop(desk):
    row = desk.target()
    token = desk._remember(row, screenshot={"image_size": [800, 400], "source_size": [1600, 800], "crop_offset": [20, 30]})
    obs, _ = desk.observed(token, "screenshot")
    assert desk.point(obs, 100, 50) == (320, 330)
    with pytest.raises(FilmoraError):
        desk.point(obs, 800, 50)
    with pytest.raises(FilmoraError):
        desk.point(obs, float("nan"), 50)


def test_expired_moved_and_invalidated_observations_are_rejected(desk):
    token = desk._remember(desk.target(), screenshot={})
    desk.observations[token]["created"] = time.monotonic() - 61
    with pytest.raises(FilmoraError, match="expired"):
        desk.observed(token, "screenshot")
    token = desk._remember(desk.target(), screenshot={})
    desk.target = lambda hwnd=None: {"hwnd": 42, "pid": 99, "rect": [0, 0, 2000, 1000]}
    with pytest.raises(FilmoraError, match="changed"):
        desk.observed(token, "screenshot")
    desk.invalidate()
    with pytest.raises(FilmoraError, match="stale"):
        desk.observed(token, "screenshot")


def test_key_modifiers_release_when_focus_is_lost(desk):
    events = []
    desk.activate = lambda row: None
    desk._key_event = lambda key, up=False: events.append((key, up))
    count = 0
    def foreground(row):
        nonlocal count
        count += 1
        if count == 3:
            raise FilmoraError("lost focus")
    desk.foreground = foreground
    with pytest.raises(FilmoraError):
        desk.press("ctrl+shift+s")
    assert events == [(17, False), (16, False), (16, True), (17, True)]


def test_drag_releases_button_and_modifiers_after_interruption(desk):
    token = desk._remember(desk.target(), screenshot={"image_size": [2000, 1000], "source_size": [2000, 1000], "crop_offset": [0, 0]})
    events = []
    desk.activate = lambda row: None
    desk.mouse_target = lambda row, point: None
    desk.foreground = lambda row: (_ for _ in ()).throw(FilmoraError("interrupted"))
    desk._key_event = lambda key, up=False: events.append((key, up))
    desk.api = SimpleNamespace(SetCursorPos=lambda p: None,
                               mouse_event=lambda flag, *args: events.append(("mouse", flag)))
    with pytest.raises(FilmoraError):
        desk.drag(token, 10, 10, 100, 100, modifiers=["alt"])
    assert events == [(18, False), ("mouse", 2), ("mouse", 4), (18, True)]


def test_local_file_validation(tmp_path):
    p = tmp_path / "sample.wfp"
    p.write_bytes(b"test")
    assert local_file(str(p), {".wfp"}) == p
    with pytest.raises(FilmoraError):
        local_file(str(p), {".mp4"})
    with pytest.raises(FilmoraError):
        local_file("relative.wfp")
    with pytest.raises(FilmoraError):
        local_file(r"\\server\share\project.wfp")


def test_named_target_does_not_guess_when_ambiguous(desk):
    desk.inspect = lambda **kw: {"observation_id": "test", "elements": [
        {"element_id": "1", "name": "Tab_Media", "automation_id": "", "control_type": "CheckBox"},
        {"element_id": "2", "name": "Tab_Media", "automation_id": "", "control_type": "CheckBox"}]}
    with pytest.raises(FilmoraError, match="not uniquely"):
        desk.named_target("media")


def test_named_target_requires_the_correct_control_type(desk):
    desk.inspect = lambda **kw: {"observation_id": "test", "elements": [
        {"element_id": "1", "name": "Edit", "automation_id": "", "control_type": "MenuItem"}]}
    with pytest.raises(FilmoraError, match="not uniquely"):
        desk.named_target("project_settings")


def test_visible_capture_refuses_an_unrelated_foreground_app(desk):
    desk.target = lambda hwnd=None: {"hwnd": 42, "pid": 99, "rect": [0, 0, 1000, 700], "minimized": False}
    desk.gui = SimpleNamespace(GetForegroundWindow=lambda: 88)
    with pytest.raises(FilmoraError, match="foreground"):
        desk.screenshot(mode="visible")


def test_save_dialog_will_not_replace_an_existing_file(desk, tmp_path):
    target = tmp_path / "existing.wfp"
    target.write_bytes(b"original project")
    with pytest.raises(FilmoraError, match="exists"):
        desk.file_dialog([str(target)], save_as=True)
    assert target.read_bytes() == b"original project"


def test_mouse_target_refuses_another_window(desk):
    desk.foreground = lambda row: None
    desk.gui = SimpleNamespace(WindowFromPoint=lambda p: 77, GetAncestor=lambda hwnd, flag: 77)
    with pytest.raises(FilmoraError, match="covered"):
        desk.mouse_target(desk.target(), (150, 250))
