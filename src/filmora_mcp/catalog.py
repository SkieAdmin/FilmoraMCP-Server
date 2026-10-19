"""Version-resolved command candidates and live UI routes for Filmora X/10+.

Shortcuts are commands to dispatch, not proof that an edit succeeded. The active
panel, selection, installed release and customized shortcut preset matter.
"""

SOURCE = "https://filmora.wondershare.com/guide/keyboard-shortcuts-on-windows.html"

# name: (chord, group, prerequisite)
COMMANDS = {}


def _add(group: str, prerequisite: str, entries: dict[str, str]):
    for name, keys in entries.items():
        COMMANDS[name] = {"keys": keys, "group": group, "prerequisite": prerequisite,
                          "verification": "Documented default; inspect UI after dispatch"}


_add("project", "Editor active; handle save prompts before continuing", {
    "new_project": "ctrl+n", "open_project": "ctrl+o", "save_project": "ctrl+s",
    "save_project_as": "ctrl+shift+s", "archive_project": "ctrl+shift+a",
    "import_media": "ctrl+i", "new_media_folder": "ctrl+alt+n",
    "preferences": "ctrl+shift+,", "keyboard_shortcuts": "ctrl+alt+k",
    "open_export": "ctrl+e", "record_voiceover": "alt+r",
})
_add("edit", "Focus the intended timeline or media panel; select clips where needed", {
    "undo": "ctrl+z", "redo": "ctrl+y", "cut": "ctrl+x", "copy": "ctrl+c",
    "paste": "ctrl+v", "delete": "delete", "ripple_delete": "shift+delete",
    "close_gap": "alt+delete", "select_all": "ctrl+a", "copy_effects": "ctrl+alt+c",
    "paste_effects": "ctrl+alt+v", "duplicate": "ctrl+d", "select_clip_range": "x",
    "cancel_clip_range": "shift+x", "nudge_left": "alt+left", "nudge_right": "alt+right",
    "nudge_up": "alt+up", "nudge_down": "alt+down", "rename": "f2",
})
_add("clip", "Select the intended timeline clip; inspect opened panel before changing values", {
    "properties": "alt+e", "split": "ctrl+b", "trim_start": "alt+[", "trim_end": "alt+]",
    "crop_zoom": "alt+c", "rotate_clockwise": "ctrl+alt+right",
    "rotate_counterclockwise": "ctrl+alt+left", "group": "ctrl+g", "ungroup": "ctrl+alt+g",
    "speed": "ctrl+r", "freeze_frame": "alt+f", "detach_audio": "ctrl+alt+d",
    "mute": "ctrl+shift+m", "stabilization": "alt+s", "color_correction": "ctrl+shift+c",
    "chroma_key": "ctrl+shift+g", "motion_tracking": "alt+x", "color_match": "alt+m",
    "keyframing": "alt+k", "crop_to_fit": "ctrl+f", "select_mode": "v",
    "audio_remix_mode": "s", "close_audio_remix_mode": "shift+s",
    "previous_keyframe": "[", "next_keyframe": "]",
})
_add("media", "Select an item in the media/assets library", {
    "insert": "shift+i", "overwrite": "shift+o", "apply_asset": "alt+a", "favorite_asset": "shift+f",
})
_add("playback", "Focus timeline/player; arrow keys can move selected clips in other contexts", {
    "play_pause": "space", "stop": "ctrl+/", "fullscreen": "alt+enter",
    "previous_frame": "left", "next_frame": "right", "previous_edit": "up", "next_edit": "down",
    "previous_second": "shift+left", "next_second": "shift+right",
    "previous_marker": "shift+up", "next_marker": "shift+down", "project_start": "home",
    "project_end": "end", "clip_start": "shift+home", "clip_end": "shift+end",
    "snapshot_frame": "ctrl+alt+s", "render_preview": "enter",
    "zoom_in": "ctrl+=", "zoom_out": "ctrl+-", "zoom_fit": "shift+z",
    "select_previous_clip": "ctrl+left", "select_next_clip": "ctrl+right",
})
_add("markers", "Focus the timeline or source monitor as appropriate", {
    "mark_in": "i", "mark_out": "o", "clear_in_out": "ctrl+shift+x",
    "add_marker": "m", "edit_marker": "shift+m",
    **{f"marker_{color}": f"alt+{i}" for i, color in enumerate(
        ["red", "orange", "yellow", "green", "cyan", "blue", "purple", "gray"], 1)},
})

# Accessible names seen in the installed Filmora 13.6.13 editor.
UI_TARGETS = {
    "media": "Tab_Media", "stock_media": "Tab_Stock", "audio": "Tab_Audio",
    "titles": "Tab_Title", "transitions": "Tab_Transition", "effects": "Tab_Effect",
    "filters": "Tab_Filter", "stickers": "Tab_Element", "more_libraries": "FMediaTabBar_More",
    "import": "importBtn", "record": "recordBtn", "add_media_folder": "FMediaFolderEditWidget_AddFolderBtn",
    "add_track": "FTracksManageToolbar_AddTrack", "auto_ripple": "FTracksManageToolbar_AutoRipple",
    "quick_text": "FTimelineToolbar_QuickText", "text_shapes": "FTimelineToolbar_btTextShape",
    "speech_to_text": "FTimelineToolbar_SpeechToText", "ai_translation": "FTimelineToolbar_btAITranslate",
    "ai_object_remover": "FTimelineToolbar_btSmartObjectRemover", "advanced_color": "FTimelineToolbar_AdvancedColor",
    "zoom_in": "ZoomIn", "zoom_out": "ZoomOut", "zoom_fit": "FTimelineToolbar_FitTimeline",
    "quick_preview": "FTimelineToolbar_QuickPreview", "auto_snap": "FTimelineToolbar_AutoSnap",
    "audio_mixer": "FTimelineToolbar_AudioMixer", "audio_recorder": "FTimelineToolbar_AudioRecorder",
    "marker": "FTimelineToolbar_Marker", "render_preview": "FTimelineToolbar_Prerender",
    "ai_copilot": "FTimelineToolbar_AICopilot", "switch_layout": "FilmoraTitleBar_SwitchLayout",
    "more_tools": "FilmoraTitleBar_MoreTools", "export": "FilmoraTitleBar_Export",
    "snapshot_frame": "FFMainPlayerToolBar_SnapShot", "player_settings": "FFPlaySettingWidget_pButtonSetting",
    "video_scopes": "FFPlayerToolBarBase_Histogram", "play_pause": "FFPlayerToolBarBase_PlayPause",
    "stop": "FFPlayerToolBarBase_Stop", "project_settings": "Edit",
}
UI_TARGET_TYPES = {name: "Button" for name in UI_TARGETS}
UI_TARGET_TYPES.update({name: "CheckBox" for name in
                        ("media", "stock_media", "audio", "titles", "transitions", "effects", "filters", "stickers")})

# Guides expose a route through the UI, not fictitious direct APIs for Qt internals.
FEATURES = {}


def _features(category, names, route):
    for name in names.split("|"):
        FEATURES[name] = {"category": category, "route": route,
                          "execution": "UI workflow; inspect live controls and screenshots at every step",
                          "availability": "Depends on Filmora version, selection, installed assets and license"}


_features("video", "transform|position_scale_rotation|opacity_compositing|crop_pan_zoom|speed_ramping|reverse|freeze_frame|masking|picture_in_picture|split_screen|keyframe_animation|motion_blur|chroma_key|stabilization|lens_correction|motion_tracking|planar_tracking|compound_clips|multicam|adjustment_layer",
          "Select a clip, open properties or Tools, inspect Video/Animation/Speed tabs; expand the relevant section.")
_features("timeline", "split_trim|ripple_editing|track_management|track_lock_mute_visibility|markers|snapping|timeline_zoom|in_out_range|render_preview|clip_grouping|replace_media",
          "Focus timeline; use command catalog or inspect track headers and timeline toolbar. Drag only from a fresh screenshot.")
_features("color", "basic_color|advanced_color|lut|color_wheels|curves|hsl|color_match|color_scopes|hdr",
          "Select video clip, open color_correction or advanced_color; inspect Color panel and applicable controls.")
_features("audio", "volume_fades|audio_keyframes|equalizer|audio_mixer|ducking|denoise|normalization|pitch|voice_changer|detach_audio|silence_detection|beat_detection|audio_stretch|audio_sync|voiceover_recording|vocal_removal",
          "Select audio-bearing clip; inspect Audio properties or Tools > Audio. Audio mixer and recorder have named UI targets.")
_features("assets", "titles|advanced_text|text_animation|subtitles|srt_import_export|transitions|effects|filters|stickers|templates|stock_media|favorites",
          "Open appropriate library with filmora_open_panel, inspect search/categories, select asset and apply or drag to timeline; inspect settings.")
_features("ai", "smart_cutout|portrait_cutout|smart_mask|object_remover|auto_reframe|scene_detection|text_based_editing|speech_to_text|text_to_speech|ai_translation|ai_music|ai_image|ai_copilot|video_denoise|video_enhancer|ai_thumbnail|smart_short_clips",
          "Select appropriate media/clip; inspect Tools, AI tools or clip properties. Some features need newer Filmora, login, credits or network uploads. Check the visible UI before starting.")
_features("project", "new_open_save|archive_relink|project_settings|proxy|preferences|keyboard_shortcuts|workspace_layout|media_import|media_search|screen_recording|webcam_recording",
          "Use project commands or named UI target, inspect dialog, set actual observed fields. Media stays local unless an online feature is started.")
_features("export", "local_video_export|audio_export|image_sequence|export_selection|export_settings|export_progress",
          "Open export dialog, inspect Local destination and actual format/resolution/frame-rate/encoder/path controls; configure and verify before activating Export. Wait for completion and verify output file.")


def capabilities(overrides=None, major=None, version=None):
    from .compatibility import command_policy, feature_policy, profile, LEGACY_SOURCE
    overrides = overrides or {}
    return {"target": "Windows Wondershare Filmora X / 10 and newer",
            "minimum_major": 10, "detected_version": version, "profile": profile(major),
            "validation_scope": "Local editor testing: 13.6.13. Other versions: policy/adapter tests; live validation still required.",
            "architecture": "Desktop UI automation; no private Filmora project mutation or invented editing API",
            "shortcut_sources": [LEGACY_SOURCE, SOURCE],
            "commands": command_policy(COMMANDS, major, overrides),
            "ui_targets": UI_TARGETS, "ui_target_control_types": UI_TARGET_TYPES,
            "selector_provenance": "Internal names observed on v13; exact live-label/configured selectors and safe shortcut fallbacks cover other layouts.",
            "features": feature_policy(FEATURES, major),
            "limitations": ["Timeline items may not expose semantic clip IDs; use screenshot coordinates.",
                            "Commands dispatch input; verify resulting state before claiming edits completed.",
                            "AI/cloud/premium/newer-version features depend on the installed editor and account."]}
