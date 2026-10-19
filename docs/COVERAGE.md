# Tool and feature coverage

94 shortcut commands, 39 named UI targets and 102 feature routes.

Shortcut commands are input dispatches. Named targets are live accessibility lookups. Feature routes are guidance for real UI interaction, not single-call feature implementations.

Filmora X/10 is the minimum target. See COMPATIBILITY.md for release policies and validation status.

## Shortcut command candidates

| Command | X/10 | Modern candidate | Context |
| --- | --- | --- | --- |
| `new_project` | `ctrl+n` | `ctrl+n` | project |
| `open_project` | `ctrl+o` | `ctrl+o` | project |
| `save_project` | `ctrl+s` | `ctrl+s` | project |
| `save_project_as` | `ctrl+shift+s` | `ctrl+shift+s` | project |
| `archive_project` | `ctrl+shift+a` | `ctrl+shift+a` | project |
| `import_media` | `ctrl+i` | `ctrl+i` | project |
| `new_media_folder` | `UI/configured override` | `ctrl+alt+n` | project |
| `preferences` | `ctrl+,` | `ctrl+shift+,` | project |
| `keyboard_shortcuts` | `UI/configured override` | `ctrl+alt+k` | project |
| `open_export` | `ctrl+e` | `ctrl+e` | project |
| `record_voiceover` | `alt+r` | `alt+r` | project |
| `undo` | `ctrl+z` | `ctrl+z` | edit |
| `redo` | `ctrl+y` | `ctrl+y` | edit |
| `cut` | `ctrl+x` | `ctrl+x` | edit |
| `copy` | `ctrl+c` | `ctrl+c` | edit |
| `paste` | `ctrl+v` | `ctrl+v` | edit |
| `delete` | `delete` | `delete` | edit |
| `ripple_delete` | `shift+delete` | `shift+delete` | edit |
| `close_gap` | `UI/configured override` | `alt+delete` | edit |
| `select_all` | `ctrl+a` | `ctrl+a` | edit |
| `copy_effects` | `UI/configured override` | `ctrl+alt+c` | edit |
| `paste_effects` | `ctrl+alt+v` | `ctrl+alt+v` | edit |
| `duplicate` | `UI/configured override` | `ctrl+d` | edit |
| `select_clip_range` | `UI/configured override` | `x` | edit |
| `cancel_clip_range` | `UI/configured override` | `shift+x` | edit |
| `nudge_left` | `UI/configured override` | `alt+left` | edit |
| `nudge_right` | `UI/configured override` | `alt+right` | edit |
| `nudge_up` | `UI/configured override` | `alt+up` | edit |
| `nudge_down` | `UI/configured override` | `alt+down` | edit |
| `rename` | `enter` | `f2` | edit |
| `properties` | `alt+e` | `alt+e` | clip |
| `split` | `ctrl+b` | `ctrl+b` | clip |
| `trim_start` | `alt+[` | `alt+[` | clip |
| `trim_end` | `alt+]` | `alt+]` | clip |
| `crop_zoom` | `alt+c` | `alt+c` | clip |
| `rotate_clockwise` | `ctrl+alt+right` | `ctrl+alt+right` | clip |
| `rotate_counterclockwise` | `ctrl+alt+left` | `ctrl+alt+left` | clip |
| `group` | `UI/configured override` | `ctrl+g` | clip |
| `ungroup` | `UI/configured override` | `ctrl+alt+g` | clip |
| `speed` | `ctrl+r` | `ctrl+r` | clip |
| `freeze_frame` | `alt+f` | `alt+f` | clip |
| `detach_audio` | `ctrl+alt+d` | `ctrl+alt+d` | clip |
| `mute` | `ctrl+shift+m` | `ctrl+shift+m` | clip |
| `stabilization` | `alt+s` | `alt+s` | clip |
| `color_correction` | `UI/configured override` | `ctrl+shift+c` | clip |
| `chroma_key` | `ctrl+alt+g` | `ctrl+shift+g` | clip |
| `motion_tracking` | `UI/configured override` | `alt+x` | clip |
| `color_match` | `UI/configured override` | `alt+m` | clip |
| `keyframing` | `UI/configured override` | `alt+k` | clip |
| `crop_to_fit` | `UI/configured override` | `ctrl+f` | clip |
| `select_mode` | `UI/configured override` | `v` | clip |
| `audio_remix_mode` | `UI/configured override` | `s` | clip |
| `close_audio_remix_mode` | `UI/configured override` | `shift+s` | clip |
| `previous_keyframe` | `UI/configured override` | `[` | clip |
| `next_keyframe` | `UI/configured override` | `]` | clip |
| `insert` | `shift+i` | `shift+i` | media |
| `overwrite` | `shift+o` | `shift+o` | media |
| `apply_asset` | `alt+a` | `alt+a` | media |
| `favorite_asset` | `UI/configured override` | `shift+f` | media |
| `play_pause` | `space` | `space` | playback |
| `stop` | `ctrl+/` | `ctrl+/` | playback |
| `fullscreen` | `alt+enter` | `alt+enter` | playback |
| `previous_frame` | `left` | `left` | playback |
| `next_frame` | `right` | `right` | playback |
| `previous_edit` | `up` | `up` | playback |
| `next_edit` | `down` | `down` | playback |
| `previous_second` | `shift+left` | `shift+left` | playback |
| `next_second` | `shift+right` | `shift+right` | playback |
| `previous_marker` | `shift+up` | `shift+up` | playback |
| `next_marker` | `shift+down` | `shift+down` | playback |
| `project_start` | `home` | `home` | playback |
| `project_end` | `end` | `end` | playback |
| `clip_start` | `shift+home` | `shift+home` | playback |
| `clip_end` | `shift+end` | `shift+end` | playback |
| `snapshot_frame` | `UI/configured override` | `ctrl+alt+s` | playback |
| `render_preview` | `UI/configured override` | `enter` | playback |
| `zoom_in` | `ctrl+=` | `ctrl+=` | playback |
| `zoom_out` | `ctrl+-` | `ctrl+-` | playback |
| `zoom_fit` | `shift+z` | `shift+z` | playback |
| `select_previous_clip` | `UI/configured override` | `ctrl+left` | playback |
| `select_next_clip` | `UI/configured override` | `ctrl+right` | playback |
| `mark_in` | `i` | `i` | markers |
| `mark_out` | `o` | `o` | markers |
| `clear_in_out` | `UI/configured override` | `ctrl+shift+x` | markers |
| `add_marker` | `m` | `m` | markers |
| `edit_marker` | `shift+m` | `shift+m` | markers |
| `marker_red` | `UI/configured override` | `alt+1` | markers |
| `marker_orange` | `UI/configured override` | `alt+2` | markers |
| `marker_yellow` | `UI/configured override` | `alt+3` | markers |
| `marker_green` | `UI/configured override` | `alt+4` | markers |
| `marker_cyan` | `UI/configured override` | `alt+5` | markers |
| `marker_blue` | `UI/configured override` | `alt+6` | markers |
| `marker_purple` | `UI/configured override` | `alt+7` | markers |
| `marker_gray` | `UI/configured override` | `alt+8` | markers |

## Named UI target candidates

Internal names below were observed on v13. Other releases can resolve exact labels, automation IDs, configured selectors or eligible shortcut fallbacks.

| Target | Candidate internal name |
| --- | --- |
| `media` | `Tab_Media` |
| `stock_media` | `Tab_Stock` |
| `audio` | `Tab_Audio` |
| `titles` | `Tab_Title` |
| `transitions` | `Tab_Transition` |
| `effects` | `Tab_Effect` |
| `filters` | `Tab_Filter` |
| `stickers` | `Tab_Element` |
| `more_libraries` | `FMediaTabBar_More` |
| `import` | `importBtn` |
| `record` | `recordBtn` |
| `add_media_folder` | `FMediaFolderEditWidget_AddFolderBtn` |
| `add_track` | `FTracksManageToolbar_AddTrack` |
| `auto_ripple` | `FTracksManageToolbar_AutoRipple` |
| `quick_text` | `FTimelineToolbar_QuickText` |
| `text_shapes` | `FTimelineToolbar_btTextShape` |
| `speech_to_text` | `FTimelineToolbar_SpeechToText` |
| `ai_translation` | `FTimelineToolbar_btAITranslate` |
| `ai_object_remover` | `FTimelineToolbar_btSmartObjectRemover` |
| `advanced_color` | `FTimelineToolbar_AdvancedColor` |
| `zoom_in` | `ZoomIn` |
| `zoom_out` | `ZoomOut` |
| `zoom_fit` | `FTimelineToolbar_FitTimeline` |
| `quick_preview` | `FTimelineToolbar_QuickPreview` |
| `auto_snap` | `FTimelineToolbar_AutoSnap` |
| `audio_mixer` | `FTimelineToolbar_AudioMixer` |
| `audio_recorder` | `FTimelineToolbar_AudioRecorder` |
| `marker` | `FTimelineToolbar_Marker` |
| `render_preview` | `FTimelineToolbar_Prerender` |
| `ai_copilot` | `FTimelineToolbar_AICopilot` |
| `switch_layout` | `FilmoraTitleBar_SwitchLayout` |
| `more_tools` | `FilmoraTitleBar_MoreTools` |
| `export` | `FilmoraTitleBar_Export` |
| `snapshot_frame` | `FFMainPlayerToolBar_SnapShot` |
| `player_settings` | `FFPlaySettingWidget_pButtonSetting` |
| `video_scopes` | `FFPlayerToolBarBase_Histogram` |
| `play_pause` | `FFPlayerToolBarBase_PlayPause` |
| `stop` | `FFPlayerToolBarBase_Stop` |
| `project_settings` | `Edit` |

## Feature routes

Some routes refer to newer Filmora features. Confirm availability in the installed editor.

| Feature | Category |
| --- | --- |
| `transform` | video |
| `position_scale_rotation` | video |
| `opacity_compositing` | video |
| `crop_pan_zoom` | video |
| `speed_ramping` | video |
| `reverse` | video |
| `freeze_frame` | video |
| `masking` | video |
| `picture_in_picture` | video |
| `split_screen` | video |
| `keyframe_animation` | video |
| `motion_blur` | video |
| `chroma_key` | video |
| `stabilization` | video |
| `lens_correction` | video |
| `motion_tracking` | video |
| `planar_tracking` | video |
| `compound_clips` | video |
| `multicam` | video |
| `adjustment_layer` | video |
| `split_trim` | timeline |
| `ripple_editing` | timeline |
| `track_management` | timeline |
| `track_lock_mute_visibility` | timeline |
| `markers` | timeline |
| `snapping` | timeline |
| `timeline_zoom` | timeline |
| `in_out_range` | timeline |
| `render_preview` | timeline |
| `clip_grouping` | timeline |
| `replace_media` | timeline |
| `basic_color` | color |
| `advanced_color` | color |
| `lut` | color |
| `color_wheels` | color |
| `curves` | color |
| `hsl` | color |
| `color_match` | color |
| `color_scopes` | color |
| `hdr` | color |
| `volume_fades` | audio |
| `audio_keyframes` | audio |
| `equalizer` | audio |
| `audio_mixer` | audio |
| `ducking` | audio |
| `denoise` | audio |
| `normalization` | audio |
| `pitch` | audio |
| `voice_changer` | audio |
| `detach_audio` | audio |
| `silence_detection` | audio |
| `beat_detection` | audio |
| `audio_stretch` | audio |
| `audio_sync` | audio |
| `voiceover_recording` | audio |
| `vocal_removal` | audio |
| `titles` | assets |
| `advanced_text` | assets |
| `text_animation` | assets |
| `subtitles` | assets |
| `srt_import_export` | assets |
| `transitions` | assets |
| `effects` | assets |
| `filters` | assets |
| `stickers` | assets |
| `templates` | assets |
| `stock_media` | assets |
| `favorites` | assets |
| `smart_cutout` | ai |
| `portrait_cutout` | ai |
| `smart_mask` | ai |
| `object_remover` | ai |
| `auto_reframe` | ai |
| `scene_detection` | ai |
| `text_based_editing` | ai |
| `speech_to_text` | ai |
| `text_to_speech` | ai |
| `ai_translation` | ai |
| `ai_music` | ai |
| `ai_image` | ai |
| `ai_copilot` | ai |
| `video_denoise` | ai |
| `video_enhancer` | ai |
| `ai_thumbnail` | ai |
| `smart_short_clips` | ai |
| `new_open_save` | project |
| `archive_relink` | project |
| `project_settings` | project |
| `proxy` | project |
| `preferences` | project |
| `keyboard_shortcuts` | project |
| `workspace_layout` | project |
| `media_import` | project |
| `media_search` | project |
| `screen_recording` | project |
| `webcam_recording` | project |
| `local_video_export` | export |
| `audio_export` | export |
| `image_sequence` | export |
| `export_selection` | export |
| `export_settings` | export |
| `export_progress` | export |
