import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
java_path = root / "app/src/main/java/com/pebblebridge/poc/NativeProbeAccessibilityService.java"
gradle_path = root / "app/build.gradle"
text = java_path.read_text()

# Preserve the already-proven relaxed unlabeled top-left navigation opener.
nav_start = "    private NodeRecord findRecoveryNavOpener(List<NodeRecord> nodes) {"
search_start = "    private NodeRecord findRecoverySearchLauncher(List<NodeRecord> nodes) {"
ns = text.find(nav_start)
ss = text.find(search_start, ns + 1)
if ns < 0 or ss < 0:
    raise SystemExit("recovery method boundaries not found")
nav_block = text[ns:ss]
if "return bestScore >= 120 ? best : null;" not in nav_block:
    raise SystemExit("v0.19 nav threshold not found")
nav_block = nav_block.replace(
    "return bestScore >= 120 ? best : null;",
    "// PEBBLE_V020_UNLABELED_TOP_LEFT_NAV_FALLBACK\n        return bestScore >= 90 ? best : null;",
    1,
)
text = text[:ns] + nav_block + text[ss:]

# If a tentative Search candidate leaves ChatGPT, back out, remember it, and
# continue candidate sequencing. Never advance to query entry without a
# verified Search EditText.
process_anchor = "        AccessibilityNodeInfo root = findTargetRoot();"
process_at = text.find(process_anchor)
if process_at < 0:
    raise SystemExit("processTargetWindow root anchor not found")
process_guard = '''        // PEBBLE_V027_REJECT_EXTERNAL_SEARCH_LAUNCH\n        if (ProbeState.isContinueChatRun(this) && "VERIFY_SEARCH_LAUNCH".equals(ProbeState.sessionRecoveryState(this))) {\n            String activePkg = packageOf(getRootInActiveWindow());\n            if (!activePkg.isEmpty() && !ProbeState.TARGET.equals(activePkg)) {\n                String fingerprint = ProbeState.getString(this, "recoverySearchCandidateFingerprint");\n                rememberRejectedRecoverySearchFingerprint(fingerprint);\n                boolean back = performGlobalAction(GLOBAL_ACTION_BACK);\n                ProbeState.log(this, "RECOVERY SEARCH REJECTED: candidate left ChatGPT and opened package=" + activePkg + "; GLOBAL_BACK=" + back + ". Candidate added to the rejected set.");\n                ProbeState.setSessionRecoveryState(this, "FIND_SEARCH");\n                return;\n            }\n        }\n\n'''
text = text[:process_at] + process_guard + text[process_at:]

# Save the proven navigation opener's header band before opening the drawer.
old_nav_click = '''            NodeRecord nav = findRecoveryNavOpener(nodes);\n            if (nav != null) {\n                boolean clicked = nav.node.performAction(AccessibilityNodeInfo.ACTION_CLICK);\n                ProbeState.log(this, "RECOVERY: navigation/history opener selected: " + nav.describe() + "; click=" + clicked + ".");\n                if (clicked) ProbeState.setSessionRecoveryState(this, "FIND_SEARCH");\n                return false;\n            }'''
new_nav_click = '''            NodeRecord nav = findRecoveryNavOpener(nodes);\n            if (nav != null) {\n                ProbeState.setString(this, "recoveryNavHeaderBand", nav.bounds.top + "," + nav.bounds.bottom + "," + nav.bounds.right);\n                ProbeState.setString(this, "rejectedRecoverySearchFingerprints", "");\n                boolean clicked = nav.node.performAction(AccessibilityNodeInfo.ACTION_CLICK);\n                ProbeState.log(this, "RECOVERY: navigation/history opener selected: " + nav.describe() + "; savedHeaderBand=" + ProbeState.getString(this, "recoveryNavHeaderBand") + "; click=" + clicked + ".");\n                if (clicked) ProbeState.setSessionRecoveryState(this, "FIND_SEARCH");\n                return false;\n            }'''
if old_nav_click not in text:
    raise SystemExit("OPEN_NAV navigation click block not found")
text = text.replace(old_nav_click, new_nav_click, 1)

# Tentative Search launch: semantic Search first, then v0.27 header-band
# candidate sequence. Failed ACTION_CLICK candidates are rejected immediately.
fs_anchor = '        if ("FIND_SEARCH".equals(state)) {'
fs_at = text.find(fs_anchor)
if fs_at < 0:
    raise SystemExit("FIND_SEARCH state not found")
old = '''            NodeRecord search = findRecoverySearchLauncher(nodes);\n            if (search != null) {\n                boolean clicked = search.node.performAction(AccessibilityNodeInfo.ACTION_CLICK);\n                ProbeState.log(this, "RECOVERY: ChatGPT Search control selected: " + search.describe() + "; click=" + clicked + ".");\n                if (clicked) ProbeState.setSessionRecoveryState(this, "ENTER_QUERY");\n                return false;\n            }'''
new = '''            NodeRecord search = findRecoverySearchLauncher(nodes);\n            if (search == null) search = findRecoveryDrawerSearchLauncher(nodes);\n            if (search != null) {\n                String fingerprint = recoverySearchFingerprint(search);\n                boolean clicked = search.node.performAction(AccessibilityNodeInfo.ACTION_CLICK);\n                ProbeState.log(this, "RECOVERY: tentative ChatGPT Search candidate selected: " + search.describe() + "; fingerprint=" + fingerprint + "; click=" + clicked + ". A verified Search field is mandatory before query entry.");\n                if (clicked) {\n                    ProbeState.setString(this, "recoverySearchCandidateFingerprint", fingerprint);\n                    ProbeState.setSessionRecoveryState(this, "VERIFY_SEARCH_LAUNCH");\n                } else {\n                    rememberRejectedRecoverySearchFingerprint(fingerprint);\n                }\n                return false;\n            }'''
at = text.find(old, fs_at)
if at < 0:
    raise SystemExit("FIND_SEARCH baseline block not found")
text = text[:at] + new + text[at + len(old):]

# Verify every tentative click. If it was not Search, back to the drawer and
# try the next non-rejected header-band candidate.
enter_anchor = '        if ("ENTER_QUERY".equals(state)) {'
enter_at = text.find(enter_anchor, fs_at)
if enter_at < 0:
    raise SystemExit("ENTER_QUERY state not found")
verify_block = '''        if ("VERIFY_SEARCH_LAUNCH".equals(state)) {\n            NodeRecord field = findRecoverySearchField(nodes);\n            if (field != null) {\n                ProbeState.setString(this, "recoverySearchCandidateFingerprint", "");\n                ProbeState.setSessionRecoveryState(this, "ENTER_QUERY");\n                ProbeState.log(this, "RECOVERY SEARCH VERIFIED: editable ChatGPT Search field appeared after candidate click: " + field.describe());\n                return false;\n            }\n            if (now - stateAt > 1800L) {\n                String fingerprint = ProbeState.getString(this, "recoverySearchCandidateFingerprint");\n                rememberRejectedRecoverySearchFingerprint(fingerprint);\n                boolean back = performGlobalAction(GLOBAL_ACTION_BACK);\n                ProbeState.log(this, "RECOVERY SEARCH REJECTED: candidate did not expose a verified Search field; GLOBAL_BACK=" + back + ". Candidate added to rejected set; trying the next header candidate.");\n                ProbeState.setSessionRecoveryState(this, "FIND_SEARCH");\n            }\n            return false;\n        }\n\n'''
text = text[:enter_at] + verify_block + text[enter_at:]

# Header-band selector. The band comes from the navigation opener that was
# actually clicked on this device/run, so there are no fixed absolute screen
# coordinates. Current real-device evidence exposes Search and the adjacent
# control as unlabeled same-band Views; selecting left-to-right and verifying
# the resulting EditText disambiguates them safely.
marker = "    private NodeRecord findRecoverySearchField(List<NodeRecord> nodes) {"
at = text.find(marker)
if at < 0:
    raise SystemExit("search field method not found")
helper = '''    // PEBBLE_V027_HEADER_BAND_CANDIDATE_SEQUENCE\n    private NodeRecord findRecoveryDrawerSearchLauncher(List<NodeRecord> nodes) {\n        String band = ProbeState.getString(this, "recoveryNavHeaderBand");\n        String[] parts = band.split(",");\n        if (parts.length != 3) return null;\n        int bandTop, bandBottom, navRight;\n        try {\n            bandTop = Integer.parseInt(parts[0]);\n            bandBottom = Integer.parseInt(parts[1]);\n            navRight = Integer.parseInt(parts[2]);\n        } catch (Exception ignored) {\n            return null;\n        }\n        int bandHeight = Math.max(1, bandBottom - bandTop);\n        int bandCenter = (bandTop + bandBottom) / 2;\n        NodeRecord semantic = null;\n        NodeRecord leftmost = null;\n        StringBuilder summary = new StringBuilder();\n        int seen = 0;\n\n        for (NodeRecord n : nodes) {\n            if (!n.clickable || !n.visible || n.bounds.isEmpty()) continue;\n            String fingerprint = recoverySearchFingerprint(n);\n            if (isRejectedRecoverySearchFingerprint(fingerprint)) continue;\n            String label = n.labelLower();\n            if (label.contains("attach") || label.contains("upload") || label.contains("file") ||\n                    label.contains("camera") || label.contains("photo") || label.contains("voice") ||\n                    label.contains("profile") || label.contains("settings")) continue;\n            if (!label.trim().isEmpty() && !label.contains("search")) continue;\n\n            int h = Math.max(1, n.bounds.height());\n            int w = Math.max(1, n.bounds.width());\n            if (Math.abs(n.bounds.centerY() - bandCenter) > bandHeight / 2) continue;\n            if (h < bandHeight / 2 || h > bandHeight * 2) continue;\n            if (w < bandHeight / 3 || w > bandHeight * 2) continue;\n            if (n.bounds.centerX() <= navRight + bandHeight) continue;\n\n            if (seen++ > 0) summary.append(" | ");\n            summary.append(n.describe());\n            if (label.contains("search")) {\n                if (semantic == null || n.bounds.left < semantic.bounds.left) semantic = n;\n            } else if (leftmost == null || n.bounds.left < leftmost.bounds.left) {\n                leftmost = n;\n            }\n        }\n\n        NodeRecord chosen = semantic != null ? semantic : leftmost;\n        if (chosen != null) {\n            ProbeState.log(this, "DRAWER HEADER-BAND CANDIDATES: savedBand=" + band + "; candidates=" + summary + "; chosen=" + chosen.describe());\n        } else if (!ProbeState.getBoolean(this, "headerBandEmptyLogged")) {\n            ProbeState.setBoolean(this, "headerBandEmptyLogged", true);\n            ProbeState.log(this, "DRAWER HEADER-BAND EMPTY: savedBand=" + band + "; no non-rejected safe candidate matched the navigation header band.");\n        }\n        return chosen;\n    }\n\n    private String recoverySearchFingerprint(NodeRecord n) {\n        if (n == null) return "";\n        return n.className + "|" + n.viewId + "|" + n.bounds.toShortString();\n    }\n\n    private boolean isRejectedRecoverySearchFingerprint(String fingerprint) {\n        if (fingerprint == null || fingerprint.isEmpty()) return false;\n        String all = ProbeState.getString(this, "rejectedRecoverySearchFingerprints");\n        return ("\\n" + all).contains("\\n" + fingerprint + "\\n");\n    }\n\n    private void rememberRejectedRecoverySearchFingerprint(String fingerprint) {\n        if (fingerprint == null || fingerprint.isEmpty() || isRejectedRecoverySearchFingerprint(fingerprint)) return;\n        String all = ProbeState.getString(this, "rejectedRecoverySearchFingerprints");\n        ProbeState.setString(this, "rejectedRecoverySearchFingerprints", all + fingerprint + "\\n");\n    }\n\n'''
text = text[:at] + helper + text[at:]

# Search-field fallback for the current accessibility profile: if Search's
# EditText itself is unlabeled, accept only a top-region EditText while the
# recovery state explicitly expects Search. The ordinary composer is near the
# bottom and is therefore excluded.
field_start = text.find(marker)
field_end_marker = "    private NodeRecord findRecoveryResult(List<NodeRecord> nodes) {"
field_end = text.find(field_end_marker, field_start)
if field_start < 0 or field_end < 0:
    raise SystemExit("search field/result boundaries not found")
field_block = text[field_start:field_end]
old_field_return = "        return bestScore >= 170 ? best : null;\n    }\n\n"
if old_field_return not in field_block:
    raise SystemExit("baseline search-field return not found")
field_fallback = '''        if (bestScore >= 170) return best;\n\n        String recoveryState = ProbeState.sessionRecoveryState(this);\n        if ("VERIFY_SEARCH_LAUNCH".equals(recoveryState) || "ENTER_QUERY".equals(recoveryState)) {\n            int screenBottom = 0;\n            for (NodeRecord n : nodes) if (n.visible && !n.bounds.isEmpty()) screenBottom = Math.max(screenBottom, n.bounds.bottom);\n            NodeRecord topEdit = null;\n            for (NodeRecord n : nodes) {\n                if (!(n.editable || n.canSetText) || !n.visible || n.bounds.isEmpty()) continue;\n                String cls = n.className.toString().toLowerCase(Locale.US);\n                if (!cls.contains("edittext")) continue;\n                if (screenBottom > 0 && n.bounds.centerY() >= screenBottom / 3) continue;\n                if (topEdit == null || n.bounds.top < topEdit.bounds.top) topEdit = n;\n            }\n            if (topEdit != null) {\n                ProbeState.log(this, "RECOVERY SEARCH FIELD PROFILE FALLBACK: top-region EditText accepted only during Search verification: " + topEdit.describe());\n                return topEdit;\n            }\n        }\n        return null;\n    }\n\n'''
field_block = field_block.replace(old_field_return, field_fallback, 1)
text = text[:field_start] + field_block + text[field_end:]

# Preserve deterministic return-to-Bridge behavior from v0.24.
text = re.sub(
    r'handler\.postDelayed\(this::bringUiForward,\s*(\d+)\);',
    r'scheduleReturnToBridge(\1L);',
    text,
)
marker_return = "    private void bringUiForward() {"
at = text.find(marker_return)
if at < 0:
    raise SystemExit("bringUiForward method not found")
return_helper = '''    // PEBBLE_V024_DETERMINISTIC_RETURN\n    private void scheduleReturnToBridge(long delayMs) {\n        handler.postDelayed(() -> {\n            bringUiForward();\n            handler.postDelayed(() -> ensureReturnFromChatGpt(0), 350L);\n        }, delayMs);\n    }\n\n    private void ensureReturnFromChatGpt(int attempt) {\n        AccessibilityNodeInfo active = getRootInActiveWindow();\n        if (!ProbeState.TARGET.equals(packageOf(active))) return;\n        if (attempt >= 3) {\n            bringUiForward();\n            return;\n        }\n        boolean back = performGlobalAction(GLOBAL_ACTION_BACK);\n        ProbeState.log(this, "RETURN FALLBACK: ChatGPT still active after bring-to-front; GLOBAL_BACK attempt=" + (attempt + 1) + "; result=" + back + ".");\n        handler.postDelayed(() -> {\n            bringUiForward();\n            handler.postDelayed(() -> ensureReturnFromChatGpt(attempt + 1), 300L);\n        }, 300L);\n    }\n\n'''
text = text[:at] + return_helper + text[at:]
java_path.write_text(text)

gradle = gradle_path.read_text()
gradle, n = re.subn(r"versionCode\s+19\b", "versionCode 27", gradle, count=1)
if n != 1:
    raise SystemExit("versionCode replacement failed")
if "0.19-thread-recovery" not in gradle:
    raise SystemExit("baseline versionName not found")
gradle = gradle.replace("0.19-thread-recovery", "0.27-header-band-candidate-sequence", 1)
gradle_path.write_text(gradle)
