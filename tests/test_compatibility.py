from types import SimpleNamespace

import pytest

from filmora_mcp.backend import FilmoraDesktop, FilmoraError, parse_chord
from filmora_mcp.catalog import COMMANDS, FEATURES, UI_TARGETS, UI_TARGET_TYPES, capabilities
from filmora_mcp.compatibility import (parse_major, version_info, profile, command_policy, feature_policy,
                                      selector_levels, match_selectors, deduplicate_installations)


@pytest.mark.parametrize("value,major", [("X",10), ("Filmora X",10), ("Wondershare Filmora X",10),
    ("10.7.0.2",10), ("11",11), ("v12",12), ("Filmora 14",14), ("16,1,0,1",16),
    (None,None), (True,None), ("something13",None), ("",None)])
def test_version_labels(value, major):
    assert parse_major(value) == major


@pytest.mark.parametrize("major", range(10,17))
def test_each_release_selects_a_profile_and_valid_dispatchable_chords(major):
    assert profile(major) == ("filmora-x-10" if major == 10 else f"filmora-{major}")
    for cmd in command_policy(COMMANDS, major).values():
        if cmd["dispatchable"]:
            parse_chord(cmd["keys"])
    assert capabilities(major=major)["minimum_major"] == 10


def test_metadata_beats_directory_and_conflicting_override_is_rejected():
    path = r"C:\Apps\Filmora 12\Wondershare Filmora.exe"
    info = version_info(path, {"ProductVersion":"13.6.13.9072"})
    assert info["major"] == 13 and info["source"] == "executable-ProductVersion"
    with pytest.raises(ValueError, match="conflicts"):
        version_info(path, {"ProductVersion":"13.6.13.9072"}, override=10)


def test_unknown_metadata_has_careful_path_and_manual_fallbacks():
    assert version_info(r"D:\Apps\Wondershare Filmora X\Filmora.exe")["major"] == 10
    assert version_info(r"D:\Apps\Filmora\12.3.4.5\Filmora.exe")["major"] == 12
    assert version_info(r"C:\Users\user13\Apps\Filmora.exe")["major"] is None
    assert version_info(r"C:\Users\user13\Apps\Filmora.exe")["supported_range"] is None
    assert version_info(r"D:\Custom\Filmora.exe", override="X")["major"] == 10
    assert version_info(r"D:\Custom\Filmora.exe", {"FileVersion":"9.5.0.0"})["supported_range"] is False


def test_legacy_shortcuts_and_ambiguous_reference_are_handled():
    legacy, modern = command_policy(COMMANDS,10), command_policy(COMMANDS,13)
    assert legacy["preferences"]["keys"] == "ctrl+,"
    assert legacy["rename"]["keys"] == "enter"
    assert legacy["chroma_key"]["keys"] == "ctrl+alt+g"
    assert modern["preferences"]["keys"] == "ctrl+shift+,"
    assert modern["rename"]["keys"] == "f2"
    assert modern["chroma_key"]["keys"] == "ctrl+shift+g"
    assert not legacy["color_correction"]["dispatchable"]
    assert not legacy["copy_effects"]["dispatchable"]
    assert not legacy["select_clip_range"]["dispatchable"]
    assert command_policy(COMMANDS,10,{"color_correction":"ctrl+shift+c"})["color_correction"]["dispatchable"]


@pytest.mark.parametrize("major", [None,17,25])
def test_unknown_future_profiles_keep_generic_input_but_do_not_guess_version_shortcuts(major):
    cmds = command_policy(COMMANDS, major)
    assert cmds["save_project"]["dispatchable"]
    assert not cmds["rename"]["dispatchable"]
    assert not cmds["chroma_key"]["dispatchable"]


def test_pre_x_profile_never_dispatches_even_with_override():
    assert all(not v["dispatchable"] for v in command_policy(COMMANDS,9,{"split":"ctrl+b"}).values())


def test_new_features_are_gated_without_claiming_license_or_ui_availability():
    legacy = feature_policy(FEATURES,10)
    modern = feature_policy(FEATURES,14)
    assert legacy["ai_copilot"]["version_status"] == "version-ineligible"
    assert modern["ai_copilot"]["version_status"] == "requires-live-verification"
    assert legacy["planar_tracking"]["minimum_major"] == 14
    assert modern["planar_tracking"]["live_status"] == "unprobed"
    assert legacy["split_trim"]["version_status"] == "requires-live-verification"


def desk_with(elements, major=10):
    d = FilmoraDesktop({"shortcut_overrides":{}, "ui_target_overrides":{}})
    d.target = lambda: {"version":{"major":major}}
    d.inspect = lambda **kw: {"elements":elements,"observation_id":"fresh","truncated":False}
    d.ui_action = lambda token, eid: {"clicked":eid}
    d.press = lambda keys, repeat: {"dispatched":keys}
    return d


def test_older_library_label_can_open_without_v13_internal_id():
    d = desk_with([{"name":"Titles","control_type":"TabItem","visible":True,"enabled":True,"element_id":"2"}])
    assert d.named_target("titles")["clicked"] == "2"


def test_internal_id_can_be_an_automation_id_on_other_releases():
    levels = selector_levels("media", UI_TARGETS["media"], UI_TARGET_TYPES["media"])
    rows = [{"name":"","automation_id":"Tab_Media","control_type":"TabItem"}]
    assert match_selectors(rows, levels[0]) == rows


def test_missing_export_button_falls_back_to_correct_legacy_shortcut():
    result = desk_with([]).named_target("export")
    assert result["route"] == "version-profile-shortcut" and result["dispatched"] == "ctrl+e"


def test_disabled_or_ambiguous_control_never_triggers_shortcut_fallback():
    row = {"name":"Export","control_type":"Button","enabled":False,"element_id":"3"}
    with pytest.raises(FilmoraError,match="disabled"):
        desk_with([row]).named_target("export")
    row["enabled"] = True
    with pytest.raises(FilmoraError,match="not uniquely"):
        desk_with([row,dict(row,element_id="4")]).named_target("export")


def test_localized_selector_override_does_not_fall_through_to_english():
    rows = [{"name":"Exporter","control_type":"Button","enabled":True,"element_id":"6"}]
    d = desk_with(rows)
    d.config["ui_target_overrides"] = {"export":[{"name":"Exporter","control_type":"Button"}]}
    assert d.named_target("export")["clicked"] == "6"
    d.config["ui_target_overrides"] = {"export":[{"name":"Wrong label","control_type":"Button"}]}
    with pytest.raises(FilmoraError):
        d.named_target("export")


def test_launcher_and_editor_in_same_folder_are_one_installation():
    paths = [r"D:\Filmora 10\Filmora.exe",r"D:\Filmora 13\Filmora.exe",r"D:\Filmora 13\Wondershare Filmora.exe"]
    resolved = deduplicate_installations(paths)
    assert len(resolved) == 2 and paths[1] not in resolved


def test_pre_x_input_is_rejected_before_foreground_mutation():
    d = desk_with([],9)
    d.guard = lambda: None
    with pytest.raises(FilmoraError,match="Minimum"):
        d.activate({"version":{"supported_range":False}})
