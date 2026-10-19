# Filmora tool workflows

## Observe, act, verify

1. Call `filmora_status` and `filmora_windows`. Launch with `filmora_launch` if needed.
2. Select a returned handle with `filmora_select_window`. When there is one main window, automatic selection works.
3. Call `filmora_activate` if minimized or obscured, then `filmora_state` for accessibility + an image.
4. Check the detected version/profile in `filmora_status`; use `filmora_capabilities(probe_ui=true)`, `filmora_commands` or `filmora_feature_guide` for compatible routes. Feature eligibility is not proof that its UI/license is available.
5. Execute one action. Input tools invalidate observations. Inspect again to verify.

Screenshot coordinates use pixels of the returned image, including resized/cropped images. Use the screenshot's `observation_id` with clicks, drags and scrolls. UI actions use the separate accessibility observation ID and a string `element_id` from `filmora_inspect`. Do not interchange IDs. Do not infer clip selection or field focus from the window title.

## Open/import/save

Open project: `filmora_open_project_dialog` → `filmora_windows` → select chooser → inspect/screenshot → `filmora_fill_file_dialog(paths=["C:\\...\\project.wfp"], submit=false)` → inspect → submit using the observed Open button → list/select editor → verify title/timeline. `.wfp` is a project; importing it as media is a different operation.

Import media: `filmora_import_media_dialog` → select chooser → fill file paths → inspect/submit → resolve media/project matching dialog if present → select editor → inspect media list. The import helper can fill multiple local files. Imported media is not automatically placed on the timeline.

Save copy: `filmora_save_project(save_as=true)` → select Save As dialog → fill one NEW `.wfp` path with `save_as=true` → inspect/submit → select editor → check title. The helper will not overwrite an existing destination. A normal `filmora_save_project()` updates the active project.

## Timeline editing

Select an observed clip using fresh image coordinates. To position playhead, click the observed ruler or use playback navigation in the correct focus context. Split with `filmora_edit("split")`; trim with `trim_start`/`trim_end`; inspect the result. These depend on the active selection and playhead. There is no invented timeline clip ID or guessed time-to-pixel calculation.

Use `filmora_drag` for clip arrangement, library-to-timeline placement, trim handles, fades and keyframe handles. `modifiers=["alt"]` supports replacement gestures; Alt-click can add a keyframe. Dragging changes observations: capture again immediately. Track header controls may need pixels because timeline accessibility can be incomplete.

Use `filmora_clip_panel` for crop/zoom, speed, properties, color or tracking. Then inspect actual fields. Set editable values with `filmora_ui_action(..., action="set_value", value="...")`, select a combo with `select`, or use `set_range` for an exposed slider. Inspect and confirm its displayed value. Unsupported UIA patterns raise errors: use a fresh screenshot and keyboard/mouse to continue.

## Titles, transitions and effects

Open `titles`, `transitions`, `effects`, `filters`, `stickers` or `audio` using `filmora_open_panel`. Inspect its search Edit control, focus with `filmora_ui_action(action="focus")`, inspect again and type using `filmora_type_text`. Alternatively use `set_value` if supported. Inspect results; select/apply an asset or drag it to the intended timeline track/boundary. Configure the selected asset in its actual properties. If an asset requires a download, subscription or credits, inspect that state before continuing.

Advanced text fields normally expose Edit controls. For any field that does not, use screenshot focus and editor-supported shortcuts, then inspect the resulting controls. Do not type into a field whose focus has not been observed.

## Audio and advanced features

`filmora_open_panel("audio_mixer")`, `audio_recorder`, `speech_to_text`, `ai_translation`, `ai_object_remover` and `more_tools` resolve live controls using internal-name candidates, exact-label alternatives or configured selectors. Applicable version-resolved shortcut fallbacks are used only when controls are absent; disabled or ambiguous controls never trigger a fallback. Disabled controls require a relevant selection. These actions open a workflow; they do not prove generation, translation or recording finished.

Use `filmora_feature_guide` for route hints for masking, denoise, normalization, ducking, LUTs, subtitles, AI, proxy, screen recording and other features. These routes are intentionally not fixed coordinate macros. Check that the feature actually exists in the installed Filmora version; later-release features are not backported by this server. Recording/AI/cloud workflows can acquire or transmit data; perform only the requested operation after checking the shown destination/settings.

## Export

1. `filmora_open_export()` opens export settings.
2. List/select the actual export dialog; inspect and screenshot it.
3. Choose the local destination/format and configure name/path, resolution, frame rate, quality and encoder using the actual observed controls. Do not guess field indexes.
4. Inspect the completed settings. Start rendering by clicking the observed Export button when the user's request includes export. Do not dismiss license/account prompts blindly.
5. Use short `filmora_wait` calls and screenshots/inspection to monitor progress. A newly created output file alone does not establish rendering is complete.
6. When the UI shows completion, call `filmora_verify_output` with the explicit destination. This confirms existence/size only; play the exported file to validate audiovisual content.

## Recovery

If a tool errors after input, the outcome may be partial. Re-list windows, reselect the correct editor/dialog, and reobserve before retrying. If Filmora has an unsaved/recovery prompt, inspect it and preserve work. Do not close/restart the editor as a generic recovery step. Avoid simultaneous MCP clients operating this desktop; the server serializes calls within one process, not across independent server processes.
