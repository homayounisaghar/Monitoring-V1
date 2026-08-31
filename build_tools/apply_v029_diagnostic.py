import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
java_path = root / "app/src/main/java/com/pebblebridge/poc/NativeProbeAccessibilityService.java"
gradle_path = root / "app/build.gradle"
text = java_path.read_text()

# v0.29 is deliberately diagnostic-only at FIND_SEARCH. It must never click
# an inferred Search candidate. Instead it derives the drawer boundary from
# real drawer rows, computes a target relative to that boundary and the proven
# navigation header band, and paints that target with the accessibility overlay.
find_start = '        if ("FIND_SEARCH".equals(state)) {'
verify_start = '        if ("VERIFY_SEARCH_LAUNCH".equals(state)) {'
fs = text.find(find_start)
vs = text.find(verify_start, fs + 1)
if fs < 0 or vs < 0:
    raise SystemExit("FIND_SEARCH/VERIFY_SEARCH_LAUNCH boundaries not found")

old_find = text[fs:vs]
if "findRecoveryDrawerSearchLauncher" not in old_find:
    raise SystemExit("v0.28 FIND_SEARCH block not recognized")

new_find = '''        if ("FIND_SEARCH".equals(state)) {\n            NodeRecord field = findRecoverySearchField(nodes);\n            if (field != null) {\n                ProbeState.setSessionRecoveryState(this, "ENTER_QUERY");\n                return false;\n            }\n\n            // PEBBLE_V029_NONCLICKING_SEARCH_TARGET_DIAGNOSTIC\n            Rect target = computeRecoverySearchVisualTarget(nodes);\n            if (target != null) {\n                showRecoveryVisualTarget(target, "V0.29 SEARCH TARGET");\n                if (!ProbeState.getBoolean(this, "v029SearchTargetLogged")) {\n                    ProbeState.setBoolean(this, "v029SearchTargetLogged", true);\n                    ProbeState.log(this, "V0.29 SEARCH TARGET DIAGNOSTIC: no candidate was clicked. Computed target=" + target.toShortString() + "; drawerEvidence=" + ProbeState.getString(this, "v029DrawerEvidence") + "; savedHeaderBand=" + ProbeState.getString(this, "recoveryNavHeaderBand") + ". Capture a screenshot showing the overlay and verify whether it sits on the visible Search icon.");\n                }\n                if (now - stateAt > 6500L) {\n                    ProbeState.markSessionVerificationFailed(this);\n                    fail("V0.29_DIAGNOSTIC_COMPLETE: Search target was displayed but intentionally not clicked. The user request was never injected.");\n                }\n                return false;\n            }\n\n            if (now - stateAt > 7000L) {\n                ProbeState.markSessionVerificationFailed(this);\n                fail("V0.29_DIAGNOSTIC_FAILED: drawer was open but a safe relative Search target could not be derived. The user request was never injected.");\n            } else {\n                maybeLogRecovery(nodes, now, "FIND_SEARCH v0.29 diagnostic: deriving drawer-relative Search target; no click is permitted");\n            }\n            return false;\n        }\n\n'''
text = text[:fs] + new_find + text[vs:]

# Add visual-target helpers before the old accessibility Search field helper.
anchor = "    private NodeRecord findRecoverySearchField(List<NodeRecord> nodes) {"
at = text.find(anchor)
if at < 0:
    raise SystemExit("search-field helper anchor not found")

helper = '''    // PEBBLE_V029_DRAWER_RELATIVE_VISUAL_TARGET\n    private Rect computeRecoverySearchVisualTarget(List<NodeRecord> nodes) {\n        String band = ProbeState.getString(this, "recoveryNavHeaderBand");\n        String[] parts = band.split(",");\n        if (parts.length != 3) return null;\n        int bandTop, bandBottom;\n        try {\n            bandTop = Integer.parseInt(parts[0]);\n            bandBottom = Integer.parseInt(parts[1]);\n        } catch (Exception ignored) {\n            return null;\n        }\n        int bandHeight = Math.max(1, bandBottom - bandTop);\n        int drawerLeft = Integer.MAX_VALUE;\n        int drawerRight = -1;\n        int evidenceCount = 0;\n        StringBuilder evidence = new StringBuilder();\n\n        for (NodeRecord n : nodes) {\n            String label = n.labelLower();\n            if (!(label.equals("images") || label.equals("library") || label.equals("projects") ||\n                    label.equals("remote") || label.equals("scheduled") || label.equals("temporary") ||\n                    label.equals("plugins") || label.equals("recents"))) continue;\n\n            AccessibilityNodeInfo cur = n.node;\n            for (int depth = 0; cur != null && depth <= 4; depth++) {\n                if (cur.isVisibleToUser() && cur.isClickable()) {\n                    Rect b = new Rect();\n                    cur.getBoundsInScreen(b);\n                    if (!b.isEmpty() && b.width() > bandHeight * 2) {\n                        drawerLeft = Math.min(drawerLeft, b.left);\n                        if (drawerRight < 0) drawerRight = b.right;\n                        else drawerRight = Math.min(drawerRight, b.right);\n                        if (evidenceCount++ > 0) evidence.append(" | ");\n                        evidence.append(label).append("->").append(b.toShortString());\n                        break;\n                    }\n                }\n                cur = cur.getParent();\n            }\n        }\n\n        if (evidenceCount < 2 || drawerRight <= 0 || drawerLeft == Integer.MAX_VALUE) return null;\n        int drawerWidth = drawerRight - drawerLeft;\n        if (drawerWidth < bandHeight * 3) return null;\n\n        // The target is expressed only in terms of the verified drawer and header geometry.\n        // It is intentionally not clicked in v0.29. The real-device screenshot will calibrate\n        // this profile once, after which any gesture remains guarded by Search-field verification.\n        int cx = drawerRight - bandHeight;\n        int cy = (bandTop + bandBottom) / 2;\n        int half = Math.max(36, bandHeight * 38 / 100);\n        Rect target = new Rect(cx - half, cy - half, cx + half, cy + half);\n        ProbeState.setString(this, "v029DrawerEvidence", "left=" + drawerLeft + ",right=" + drawerRight + ",width=" + drawerWidth + ",rows=" + evidence);\n        return target;\n    }\n\n    private void showRecoveryVisualTarget(Rect r, String label) {\n        ensureOverlay();\n        if (overlay != null && r != null && !r.isEmpty()) overlay.show(r, label);\n    }\n\n'''
text = text[:at] + helper + text[at:]

java_path.write_text(text)

gradle = gradle_path.read_text()
gradle, n = re.subn(r"versionCode\s+28\b", "versionCode 29", gradle, count=1)
if n != 1:
    raise SystemExit("versionCode 28 replacement failed")
if "0.28-right-first-context-restore" not in gradle:
    raise SystemExit("v0.28 versionName not found")
gradle = gradle.replace("0.28-right-first-context-restore", "0.29-nonclicking-search-target-diagnostic", 1)
gradle_path.write_text(gradle)
