# 3D Viewer Extractor

Current release: **v1.2.1** (versionCode 4)
Status: **paused by user after successful two-site validation**

Canonical project state lives in:
`homayounisaghar/capability-fabric:project/traceparts-preview-extractor:projects/traceparts-preview-extractor/PROJECT_STATE.md`

Detailed milestone/checkpoint:
`projects/traceparts-preview-extractor/checkpoints/2026-09-05_GENERALIZED_VIEWER_EXTRACTOR_CHECKPOINT.md`

## Purpose
Android WebView utility for capturing the model/geometry resources delivered to an interactive 3D viewer in the user's active browser session. The user supplies any `http(s)` page URL; the app targets the uppermost visible 3D viewer and packages captured resources into one ZIP for downstream decoding/conversion.

## Normal use
1. Paste URL and press `GO`.
2. Scroll until the desired 3D viewer is visible.
3. Press `EXTRACT ZIP`.
4. Wait for automatic completion.
5. Retrieve `Viewer3DCapture_<host>_<timestamp>.zip` from Downloads.

There is intentionally no `FINISH NOW`: user feedback established that manual early finish creates unnecessary risk of incomplete captures.

## Current UX invariants
- Android status/navigation bar insets must be respected; controls must not sit under system bars.
- One output ZIP, not a loose folder.
- If several viewers are stacked vertically, select the uppermost currently visible viewer.
- During capture, show `EXTRACTING...` and disable the extract button until completion.

## Capture paths
See `android/app/src/main/assets/viewer_hook.js` and `MainActivity.java` for implementation. Current paths include WebGL/canvas/model-viewer detection, iframe position mapping, fetch/XHR capture, Blob/object-URL capture, Performance Resource Timing enumeration, session-context recapture, and native candidate download.

Resource limits: 150 MB per item, up to 120 candidate resources.

## Proven validations
- **TraceParts XPEA110:** generic capture reproduced the known-good 18,919-byte `foot_switch_xpea110.zip` Preview package.
- **RIMOWA Cabin:** generic capture ZIP from `www.rimowa.com` yielded geometry converted to `RIMOWA_Cabin_92553004_viewer_geometry.stl`; the user confirmed the STL was correct. Envelope was approximately 398 x 548 x 233 mm.

## Release/build identity
- applicationId: `com.capabilityfabric.viewer3dextractor`
- launch activity class: `com.capabilityfabric.tracepartsgrabber.MainActivity`
- workflow: `.github/workflows/build-viewer3d-extractor.yml`
- successful v1.2.1 run: `33970962962`
- artifact ID: `9970923491`
- APK SHA-256: `3ceac68c964a4d65c103e067a7d6b7277aa7bf36f5031667017c8eed4b63a340`

v1.2.0 and v1.2.1 share the generic signing lineage and update each other in place. The generic app has a different applicationId from the older dedicated TraceParts extractor, so it installs side-by-side with that legacy app.

## Boundaries
The app does not bypass authentication, CAPTCHA, WAF, DRM, signed-access controls, or other access controls. It captures resources available to the active user-authorized/public WebView session.

A captured viewer model may be tessellated mesh data rather than native CAD/B-rep. Direct conversion to STL/OBJ/GLB is therefore different from reconstructing STEP. STEP/B-rep reconstruction is downstream CAD work, not proof that a hidden native STEP existed.

## Resume rule
Do not continue implementation until explicitly requested. When resumed, start from this branch and preserve the current UX invariants above.