import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
java_path = root / "app/src/main/java/com/pebblebridge/poc/NativeProbeAccessibilityService.java"
gradle_path = root / "app/build.gradle"
text = java_path.read_text()

# v0.30 uses the v0.29 real-device screenshot calibration. The target remains
# drawer-relative: x = drawerRight - 0.8 * saved band height; y = saved band
# top - 0.25 * saved band height. The inferred point is tapped only once and
# is never trusted unless a real ChatGPT Search EditText appears afterwards.

if "import android.accessibilityservice.GestureDescription;" not in text:
    text = text.replace(
        "import android.accessibilityservice.AccessibilityService;\n",
        "import android.accessibilityservice.AccessibilityService;\nimport android.accessibilityservice.GestureDescription;\n",
        1,
    )
if "import android.graphics.Path;" not in text:
    text = text.replace(
        "import android.graphics.Paint;\n",
        "import android.graphics.Paint;\nimport android.graphics.Path;\n",
        1,
    )

find_start = '        if ("FIND_SEARCH".equals(state)) {'
verify_start = '        if ("VERIFY_SEARCH_LAUNCH".equals(state)) {'
fs = text.find(find_start)
vs = text.find(verify_start, fs + 1)
if fs < 0 or vs < 0:
    raise SystemExit("FIND_SEARCH/VERIFY_SEARCH_LAUNCH boundaries not found")
old_find = text[fs:vs]
if "PEBBLE_V029_NONCLICKING_SEARCH_TARGET_DIAGNOSTIC" not in old_find:
    raise SystemExit("v0.29 diagnostic FIND_SEARCH block not recognized")

new_find = '''        if ("FIND_SEARCH".equals(state)) {\n            NodeRecord field = findRecoverySearchField(nodes);\n            if (field != null) {\n                ProbeState.setSessionRecoveryState(this, "ENTER_QUERY");\n                return false;\n            }\n\n            // PEBBLE_V030_CALIBRATED_DRAWER_RELATIVE_SEARCH_GESTURE\n            Rect target = computeRecoverySearchVisualTarget(nodes);\n            if (target != null) {\n                showRecoveryVisualTarget(target, "V0.30 SEARCH TAP");\n                String fingerprint = "gesture-v030|" + target.toShortString();\n                boolean dispatched = dispatchRecoverySearchTap(target);\n                ProbeState.log(this, "V0.30 CALIBRATED SEARCH TAP: target=" + target.toShortString() + "; dispatched=" + dispatched + "; drawerEvidence=" + ProbeState.getString(this, "v029DrawerEvidence") + "; savedHeaderBand=" + ProbeState.getString(this, "recoveryNavHeaderBand") + ". Search EditText verification is mandatory before any query entry.");\n                if (dispatched) {\n                    ProbeState.setString(this, "recoverySearchCandidateFingerprint", fingerprint);\n                    ProbeState.setSessionRecoveryState(this, "VERIFY_SEARCH_LAUNCH");\n                } else {\n                    ProbeState.markSessionVerificationFailed(this);\n                    fail("V0.30_SEARCH_GESTURE_FAILED: calibrated Search tap could not be dispatched. The user request was never injected.");\n                }\n                return false;\n            }\n\n            if (now - stateAt > 7000L) {\n                ProbeState.markSessionVerificationFailed(this);\n                fail("V0.30_SEARCH_TARGET_FAILED: drawer was open but a safe calibrated Search point could not be derived. The user request was never injected.");\n            } else {\n                maybeLogRecovery(nodes, now, "FIND_SEARCH v0.30: deriving calibrated drawer-relative Search point");\n            }\n            return false;\n        }\n\n'''
text = text[:fs] + new_find + text[vs:]

# Fail closed if the one calibrated gesture escapes ChatGPT instead of using
# v0.28's generic candidate-retry path, which could otherwise repeat the same
# gesture after restoring the app.
old_external = '''                String fingerprint = ProbeState.getString(this, "recoverySearchCandidateFingerprint");\n                rememberRejectedRecoverySearchFingerprint(fingerprint);\n                ProbeState.setBoolean(this, "recoverySearchRetrying", true);\n                boolean back = performGlobalAction(GLOBAL_ACTION_BACK);\n                ProbeState.setSessionRecoveryState(this, "RESTORE_CHATGPT_AFTER_BAD_SEARCH");\n                ProbeState.setLong(this, "nextRecoveryForegroundAt", now + 250L);\n                ProbeState.log(this, "RECOVERY SEARCH REJECTED: candidate left ChatGPT and opened package=" + activePkg + "; GLOBAL_BACK=" + back + ". Candidate stays rejected; ChatGPT will be explicitly restored before reopening navigation.");\n                return;\n'''
new_external = '''                String fingerprint = ProbeState.getString(this, "recoverySearchCandidateFingerprint");\n                if (fingerprint.startsWith("gesture-v030|")) {\n                    ProbeState.markSessionVerificationFailed(this);\n                    fail("V0.30_SEARCH_GESTURE_ESCAPED_CHATGPT: calibrated Search tap opened package=" + activePkg + ". No retry was attempted and the user request was never injected.");\n                    return;\n                }\n                rememberRejectedRecoverySearchFingerprint(fingerprint);\n                ProbeState.setBoolean(this, "recoverySearchRetrying", true);\n                boolean back = performGlobalAction(GLOBAL_ACTION_BACK);\n                ProbeState.setSessionRecoveryState(this, "RESTORE_CHATGPT_AFTER_BAD_SEARCH");\n                ProbeState.setLong(this, "nextRecoveryForegroundAt", now + 250L);\n                ProbeState.log(this, "RECOVERY SEARCH REJECTED: candidate left ChatGPT and opened package=" + activePkg + "; GLOBAL_BACK=" + back + ". Candidate stays rejected; ChatGPT will be explicitly restored before reopening navigation.");\n                return;\n'''
if old_external not in text:
    raise SystemExit("v0.28 external-search guard block not found")
text = text.replace(old_external, new_external, 1)

# A calibrated gesture gets exactly one attempt. If ChatGPT remains foreground
# but no Search field appears, stop safely rather than backing out and looping.
old_verify_tail = '''            if (now - stateAt > 1800L) {\n                String fingerprint = ProbeState.getString(this, "recoverySearchCandidateFingerprint");\n                rememberRejectedRecoverySearchFingerprint(fingerprint);\n                ProbeState.setBoolean(this, "recoverySearchRetrying", true);\n                boolean back = performGlobalAction(GLOBAL_ACTION_BACK);\n                ProbeState.log(this, "RECOVERY SEARCH REJECTED: candidate did not expose a verified Search field; GLOBAL_BACK=" + back + ". Candidate added to rejected set; trying the next header candidate.");\n                ProbeState.setSessionRecoveryState(this, "FIND_SEARCH");\n            }\n            return false;\n'''
new_verify_tail = '''            if (now - stateAt > 2200L) {\n                String fingerprint = ProbeState.getString(this, "recoverySearchCandidateFingerprint");\n                if (fingerprint.startsWith("gesture-v030|")) {\n                    ProbeState.markSessionVerificationFailed(this);\n                    fail("V0.30_SEARCH_GESTURE_UNVERIFIED: calibrated Search tap did not expose a verified ChatGPT Search field. No retry was attempted and the user request was never injected.");\n                    return false;\n                }\n                rememberRejectedRecoverySearchFingerprint(fingerprint);\n                ProbeState.setBoolean(this, "recoverySearchRetrying", true);\n                boolean back = performGlobalAction(GLOBAL_ACTION_BACK);\n                ProbeState.log(this, "RECOVERY SEARCH REJECTED: candidate did not expose a verified Search field; GLOBAL_BACK=" + back + ". Candidate added to rejected set; trying the next header candidate.");\n                ProbeState.setSessionRecoveryState(this, "FIND_SEARCH");\n            }\n            return false;\n'''
if old_verify_tail not in text:
    raise SystemExit("VERIFY_SEARCH_LAUNCH rejection tail not found")
text = text.replace(old_verify_tail, new_verify_tail, 1)

old_target = '''        int cx = drawerRight - bandHeight;\n        int cy = (bandTop + bandBottom) / 2;\n        int half = Math.max(36, bandHeight * 38 / 100);\n'''
new_target = '''        // PEBBLE_V030_SCREENSHOT_CALIBRATION\n        // Real-device v0.29 overlay was ~0.19H left and ~0.74H below the\n        // visible magnifier center. Keep the correction proportional to the\n        // proven runtime band rather than hard-coding pixels.\n        int cx = drawerRight - (bandHeight * 4 / 5);\n        int cy = bandTop - (bandHeight / 4);\n        int half = Math.max(36, bandHeight * 38 / 100);\n'''
if old_target not in text:
    raise SystemExit("v0.29 target formula not found")
text = text.replace(old_target, new_target, 1)

helper_anchor = '''    private void showRecoveryVisualTarget(Rect r, String label) {\n'''
helper_at = text.find(helper_anchor)
if helper_at < 0:
    raise SystemExit("showRecoveryVisualTarget helper anchor not found")
helper = '''    private boolean dispatchRecoverySearchTap(Rect target) {\n        if (target == null || target.isEmpty() || Build.VERSION.SDK_INT < Build.VERSION_CODES.N) return false;\n        try {\n            Path p = new Path();\n            p.moveTo(target.centerX(), target.centerY());\n            GestureDescription.StrokeDescription stroke = new GestureDescription.StrokeDescription(p, 0L, 90L);\n            GestureDescription.Builder builder = new GestureDescription.Builder();\n            builder.addStroke(stroke);\n            return dispatchGesture(builder.build(), null, null);\n        } catch (Exception e) {\n            ProbeState.log(this, "V0.30 SEARCH GESTURE ERROR: " + e.getClass().getSimpleName() + ": " + e.getMessage());\n            return false;\n        }\n    }\n\n'''
text = text[:helper_at] + helper + text[helper_at:]

java_path.write_text(text)

gradle = gradle_path.read_text()
gradle, n = re.subn(r"versionCode\s+29\b", "versionCode 30", gradle, count=1)
if n != 1:
    raise SystemExit("versionCode 29 replacement failed")
if "0.29-nonclicking-search-target-diagnostic" not in gradle:
    raise SystemExit("v0.29 versionName not found")
gradle = gradle.replace("0.29-nonclicking-search-target-diagnostic", "0.30-calibrated-search-gesture", 1)
gradle_path.write_text(gradle)
