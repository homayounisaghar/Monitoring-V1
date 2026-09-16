import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
java_path = root / "app/src/main/java/com/pebblebridge/poc/NativeProbeAccessibilityService.java"
gradle_path = root / "app/build.gradle"
text = java_path.read_text()

old_guard = '''        // PEBBLE_V027_REJECT_EXTERNAL_SEARCH_LAUNCH
        if (ProbeState.isContinueChatRun(this) && "VERIFY_SEARCH_LAUNCH".equals(ProbeState.sessionRecoveryState(this))) {
            String activePkg = packageOf(getRootInActiveWindow());
            if (!activePkg.isEmpty() && !ProbeState.TARGET.equals(activePkg)) {
                String fingerprint = ProbeState.getString(this, "recoverySearchCandidateFingerprint");
                rememberRejectedRecoverySearchFingerprint(fingerprint);
                boolean back = performGlobalAction(GLOBAL_ACTION_BACK);
                ProbeState.log(this, "RECOVERY SEARCH REJECTED: candidate left ChatGPT and opened package=" + activePkg + "; GLOBAL_BACK=" + back + ". Candidate added to the rejected set.");
                ProbeState.setSessionRecoveryState(this, "FIND_SEARCH");
                return;
            }
        }

'''
new_guard = '''        // PEBBLE_V028_RESTORE_AFTER_EXTERNAL_SEARCH_LAUNCH
        if (ProbeState.isContinueChatRun(this) && "VERIFY_SEARCH_LAUNCH".equals(ProbeState.sessionRecoveryState(this))) {
            String activePkg = packageOf(getRootInActiveWindow());
            if (!activePkg.isEmpty() && !ProbeState.TARGET.equals(activePkg)) {
                String fingerprint = ProbeState.getString(this, "recoverySearchCandidateFingerprint");
                rememberRejectedRecoverySearchFingerprint(fingerprint);
                ProbeState.setBoolean(this, "recoverySearchRetrying", true);
                boolean back = performGlobalAction(GLOBAL_ACTION_BACK);
                ProbeState.setSessionRecoveryState(this, "RESTORE_CHATGPT_AFTER_BAD_SEARCH");
                ProbeState.setLong(this, "nextRecoveryForegroundAt", now + 250L);
                ProbeState.log(this, "RECOVERY SEARCH REJECTED: candidate left ChatGPT and opened package=" + activePkg + "; GLOBAL_BACK=" + back + ". Candidate stays rejected; ChatGPT will be explicitly restored before reopening navigation.");
                return;
            }
        }

        if (ProbeState.isContinueChatRun(this) && "RESTORE_CHATGPT_AFTER_BAD_SEARCH".equals(ProbeState.sessionRecoveryState(this))) {
            String activePkg = packageOf(getRootInActiveWindow());
            if (ProbeState.TARGET.equals(activePkg)) {
                ProbeState.setSessionRecoveryState(this, "OPEN_NAV");
                ProbeState.log(this, "RECOVERY CONTEXT RESTORED: ChatGPT is active again; reopening navigation while preserving rejected Search candidates.");
            } else {
                long next = ProbeState.getLong(this, "nextRecoveryForegroundAt");
                if (now >= next) {
                    boolean launched = bringChatGptForwardForRecovery();
                    ProbeState.setLong(this, "nextRecoveryForegroundAt", now + 900L);
                    ProbeState.log(this, "RECOVERY CONTEXT RESTORE: requested ChatGPT foreground; activePackage=" + activePkg + "; launch=" + launched + ".");
                }
                return;
            }
        }

'''
if old_guard not in text:
    raise SystemExit("v0.27 external-search guard not found")
text = text.replace(old_guard, new_guard, 1)

old_clear = '                ProbeState.setString(this, "rejectedRecoverySearchFingerprints", "");\n'
new_clear = '''                if (!ProbeState.getBoolean(this, "recoverySearchRetrying")) {
                    ProbeState.setString(this, "rejectedRecoverySearchFingerprints", "");
                }
'''
if old_clear not in text:
    raise SystemExit("v0.27 rejected-set reset not found")
text = text.replace(old_clear, new_clear, 1)

old_verified = '''                ProbeState.setString(this, "recoverySearchCandidateFingerprint", "");
                ProbeState.setSessionRecoveryState(this, "ENTER_QUERY");
                ProbeState.log(this, "RECOVERY SEARCH VERIFIED: editable ChatGPT Search field appeared after candidate click: " + field.describe());
'''
new_verified = '''                ProbeState.setString(this, "recoverySearchCandidateFingerprint", "");
                ProbeState.setBoolean(this, "recoverySearchRetrying", false);
                ProbeState.setSessionRecoveryState(this, "ENTER_QUERY");
                ProbeState.log(this, "RECOVERY SEARCH VERIFIED: editable ChatGPT Search field appeared after candidate click: " + field.describe());
'''
if old_verified not in text:
    raise SystemExit("v0.27 verified-search block not found")
text = text.replace(old_verified, new_verified, 1)

old_same_package = '''                rememberRejectedRecoverySearchFingerprint(fingerprint);
                boolean back = performGlobalAction(GLOBAL_ACTION_BACK);
                ProbeState.log(this, "RECOVERY SEARCH REJECTED: candidate did not expose a verified Search field; GLOBAL_BACK=" + back + ". Candidate added to rejected set; trying the next header candidate.");
                ProbeState.setSessionRecoveryState(this, "FIND_SEARCH");
'''
new_same_package = '''                rememberRejectedRecoverySearchFingerprint(fingerprint);
                ProbeState.setBoolean(this, "recoverySearchRetrying", true);
                boolean back = performGlobalAction(GLOBAL_ACTION_BACK);
                ProbeState.log(this, "RECOVERY SEARCH REJECTED: candidate did not expose a verified Search field; GLOBAL_BACK=" + back + ". Candidate added to rejected set; trying the next header candidate.");
                ProbeState.setSessionRecoveryState(this, "FIND_SEARCH");
'''
if old_same_package not in text:
    raise SystemExit("v0.27 same-package rejection block not found")
text = text.replace(old_same_package, new_same_package, 1)

text = text.replace("// PEBBLE_V027_HEADER_BAND_CANDIDATE_SEQUENCE", "// PEBBLE_V028_HEADER_BAND_CANDIDATE_SEQUENCE", 1)
text = text.replace("NodeRecord leftmost = null;", "NodeRecord rightmost = null;", 1)
old_choice = '''            } else if (leftmost == null || n.bounds.left < leftmost.bounds.left) {
                leftmost = n;
            }
        }

        NodeRecord chosen = semantic != null ? semantic : leftmost;
'''
new_choice = '''            } else if (rightmost == null || n.bounds.right > rightmost.bounds.right) {
                rightmost = n;
            }
        }

        NodeRecord chosen = semantic != null ? semantic : rightmost;
'''
if old_choice not in text:
    raise SystemExit("v0.27 left-to-right selector block not found")
text = text.replace(old_choice, new_choice, 1)
text = text.replace("DRAWER HEADER-BAND CANDIDATES:", "DRAWER HEADER-BAND CANDIDATES v0.28 RIGHT-FIRST:", 1)

helper_anchor = "    private AccessibilityNodeInfo findTargetRoot() {"
helper_at = text.find(helper_anchor)
if helper_at < 0:
    raise SystemExit("findTargetRoot helper anchor not found")
helper = '''    private boolean bringChatGptForwardForRecovery() {
        try {
            Intent i = getPackageManager().getLaunchIntentForPackage(ProbeState.TARGET);
            if (i == null) return false;
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(i);
            return true;
        } catch (Exception e) {
            ProbeState.log(this, "RECOVERY CONTEXT RESTORE FAILED: " + e.getClass().getSimpleName() + ": " + e.getMessage());
            return false;
        }
    }

'''
text = text[:helper_at] + helper + text[helper_at:]

java_path.write_text(text)

gradle = gradle_path.read_text()
gradle, n = re.subn(r"versionCode\s+27\b", "versionCode 28", gradle, count=1)
if n != 1:
    raise SystemExit("versionCode 27 replacement failed")
if "0.27-header-band-candidate-sequence" not in gradle:
    raise SystemExit("v0.27 versionName not found")
gradle = gradle.replace("0.27-header-band-candidate-sequence", "0.28-right-first-context-restore", 1)
gradle_path.write_text(gradle)
