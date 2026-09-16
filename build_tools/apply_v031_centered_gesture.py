import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
java_path = root / "app/src/main/java/com/pebblebridge/poc/NativeProbeAccessibilityService.java"
gradle_path = root / "app/build.gradle"
text = java_path.read_text()

# v0.31 uses the v0.30 real-device screenshot as a second calibration.
# The v0.30 overlay center was about 0.24 header-band heights left of the
# visible magnifier center and vertically almost correct. Keep the point fully
# drawer/header-relative, and do not draw an overlay over the tap in this run.
old_formula = '''        // PEBBLE_V030_SCREENSHOT_CALIBRATION\n        // Real-device v0.29 overlay was ~0.19H left and ~0.74H below the\n        // visible magnifier center. Keep the correction proportional to the\n        // proven runtime band rather than hard-coding pixels.\n        int cx = drawerRight - (bandHeight * 4 / 5);\n        int cy = bandTop - (bandHeight / 4);\n'''
new_formula = '''        // PEBBLE_V031_SCREENSHOT_RECALIBRATION\n        // v0.30 landed about 0.24H left of the visible magnifier center and\n        // was vertically within a few pixels. Shift only by proportional\n        // runtime geometry; no absolute screen coordinates are stored.\n        int cx = drawerRight - (bandHeight * 14 / 25);\n        int cy = bandTop - (bandHeight * 2 / 9);\n'''
if old_formula not in text:
    raise SystemExit("v0.30 calibrated formula not found")
text = text.replace(old_formula, new_formula, 1)

old_find = '''            // PEBBLE_V030_CALIBRATED_DRAWER_RELATIVE_SEARCH_GESTURE\n            Rect target = computeRecoverySearchVisualTarget(nodes);\n            if (target != null) {\n                showRecoveryVisualTarget(target, "V0.30 SEARCH TAP");\n                String fingerprint = "gesture-v030|" + target.toShortString();\n                boolean dispatched = dispatchRecoverySearchTap(target);\n                ProbeState.log(this, "V0.30 CALIBRATED SEARCH TAP: target=" + target.toShortString() + "; dispatched=" + dispatched + "; drawerEvidence=" + ProbeState.getString(this, "v029DrawerEvidence") + "; savedHeaderBand=" + ProbeState.getString(this, "recoveryNavHeaderBand") + ". Search EditText verification is mandatory before any query entry.");\n                if (dispatched) {\n                    ProbeState.setString(this, "recoverySearchCandidateFingerprint", fingerprint);\n                    ProbeState.setSessionRecoveryState(this, "VERIFY_SEARCH_LAUNCH");\n                } else {\n                    ProbeState.markSessionVerificationFailed(this);\n                    fail("V0.30_SEARCH_GESTURE_FAILED: calibrated Search tap could not be dispatched. The user request was never injected.");\n                }\n                return false;\n            }\n'''
new_find = '''            // PEBBLE_V031_OVERLAY_FREE_CENTERED_SEARCH_GESTURE\n            Rect target = computeRecoverySearchVisualTarget(nodes);\n            if (target != null) {\n                String fingerprint = "gesture-v031|" + target.toShortString();\n                boolean dispatched = dispatchRecoverySearchTap(target);\n                ProbeState.log(this, "V0.31 CENTERED SEARCH TAP: target=" + target.toShortString() + "; dispatched=" + dispatched + "; overlay=off; drawerEvidence=" + ProbeState.getString(this, "v029DrawerEvidence") + "; savedHeaderBand=" + ProbeState.getString(this, "recoveryNavHeaderBand") + ". Search EditText verification is mandatory before any query entry.");\n                if (dispatched) {\n                    ProbeState.setString(this, "recoverySearchCandidateFingerprint", fingerprint);\n                    ProbeState.setSessionRecoveryState(this, "VERIFY_SEARCH_LAUNCH");\n                } else {\n                    ProbeState.markSessionVerificationFailed(this);\n                    fail("V0.31_SEARCH_GESTURE_FAILED: centered Search tap could not be dispatched. The user request was never injected.");\n                }\n                return false;\n            }\n'''
if old_find not in text:
    raise SystemExit("v0.30 FIND_SEARCH gesture block not found")
text = text.replace(old_find, new_find, 1)

# Retarget the one-shot fail-closed guards to the v0.31 gesture fingerprint.
text = text.replace('fingerprint.startsWith("gesture-v030|")', 'fingerprint.startsWith("gesture-v031|")')
text = text.replace('V0.30_SEARCH_GESTURE_ESCAPED_CHATGPT', 'V0.31_SEARCH_GESTURE_ESCAPED_CHATGPT')
text = text.replace('V0.30_SEARCH_GESTURE_UNVERIFIED', 'V0.31_SEARCH_GESTURE_UNVERIFIED')
text = text.replace('V0.30_SEARCH_TARGET_FAILED', 'V0.31_SEARCH_TARGET_FAILED')
text = text.replace('FIND_SEARCH v0.30: deriving calibrated drawer-relative Search point', 'FIND_SEARCH v0.31: deriving centered drawer-relative Search point')

java_path.write_text(text)

gradle = gradle_path.read_text()
gradle, n = re.subn(r"versionCode\s+30\b", "versionCode 31", gradle, count=1)
if n != 1:
    raise SystemExit("versionCode 30 replacement failed")
if "0.30-calibrated-search-gesture" not in gradle:
    raise SystemExit("v0.30 versionName not found")
gradle = gradle.replace("0.30-calibrated-search-gesture", "0.31-centered-overlay-free-search-gesture", 1)
gradle_path.write_text(gradle)
