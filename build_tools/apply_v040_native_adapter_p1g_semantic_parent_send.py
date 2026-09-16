import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
java_dir = root / "app/src/main/java/com/pebblebridge/poc"
activity_path = java_dir / "NativeAdapterProofActivity.java"
store_path = java_dir / "NativeAdapterProofStore.java"
service_path = java_dir / "NativeProbeAccessibilityService.java"
manifest_path = root / "app/src/main/AndroidManifest.xml"
gradle_path = root / "app/build.gradle"

# P1g is selected directly from the P1f real-device TXT evidence.
# The physical Send tap emitted no TYPE_VIEW_CLICKED, but the BEFORE tree exposed:
#   semantic leaf: desc="Send Message", non-clickable
#   direct parent: enabled + visible + clickable + ACTION_CLICK
# P1g invokes exactly that bounded semantic relation inside the marker composer's
# up+2 subtree. It performs one ACTION_CLICK only after a durable claim and then
# verifies the editable-marker -> non-editable-message transition read-only.

# ---- store: dedicated no-retry states -----------------------------------
store = store_path.read_text()
const_anchor = '    public static final String MANUAL_SEND_TRACE_COMPLETE = "MANUAL_SEND_TRACE_COMPLETE";\n'
if const_anchor not in store:
    raise SystemExit("P1g store constant anchor missing")
store = store.replace(
    const_anchor,
    const_anchor +
    '    public static final String WAITING_SEMANTIC_PARENT_SEND = "WAITING_SEMANTIC_PARENT_SEND";\n'
    '    public static final String SEMANTIC_PARENT_SEND_CLAIMED = "SEMANTIC_PARENT_SEND_CLAIMED";\n'
    '    public static final String SEMANTIC_PARENT_SEND_CONFIRMED = "SEMANTIC_PARENT_SEND_CONFIRMED";\n',
    1,
)

method_anchor = '    public static String manualClickSummary(Context c) { return p(c).getString("manualClickSummary", ""); }\n'
if method_anchor not in store:
    raise SystemExit("P1g store method anchor missing")
p1g_store_methods = r'''    public static void markWaitingSemanticParentSend(Context c) {
        p(c).edit()
                .putString("state", WAITING_SEMANTIC_PARENT_SEND)
                .putString("manualTrace", "")
                .putString("manualBaseline", "")
                .putString("manualAfter", "")
                .putString("manualClickSummary", "")
                .putBoolean("manualBaselineCaptured", false)
                .putString("semanticSendNode", "")
                .apply();
    }

    public static boolean isSemanticParentSendHot(Context c) {
        String s = state(c);
        return WAITING_SEMANTIC_PARENT_SEND.equals(s) || SEMANTIC_PARENT_SEND_CLAIMED.equals(s);
    }

    public static boolean isWaitingSemanticParentSend(Context c) {
        return WAITING_SEMANTIC_PARENT_SEND.equals(state(c));
    }

    public static boolean isSemanticParentSendClaimed(Context c) {
        return SEMANTIC_PARENT_SEND_CLAIMED.equals(state(c));
    }

    public static void markSemanticParentSendClaimed(Context c, String target) {
        p(c).edit()
                .putString("semanticSendNode", target == null ? "" : target)
                .putString("state", SEMANTIC_PARENT_SEND_CLAIMED)
                .apply();
    }

    public static void markSemanticParentSendConfirmed(Context c) {
        p(c).edit().putString("state", SEMANTIC_PARENT_SEND_CONFIRMED).apply();
    }

'''
store = store.replace(method_anchor, p1g_store_methods + method_anchor, 1)
store_path.write_text(store)

# ---- activity: P1g starts automatic bounded proof; keep TXT export -------
activity = activity_path.read_text()
activity = activity.replace('title.setText("Native Chat Adapter P1f");', 'title.setText("Native Chat Adapter P1g");', 1)
activity = activity.replace(
    'subtitle.setText("Manual Send black-box tracer with portable TXT export. P1f performs NO submit action. When the draft is visible, manually press ChatGPT Send exactly once; after the trace returns, tap EXPORT TRACE TXT and upload that file for analysis.");',
    'subtitle.setText("Bounded semantic-parent Send proof selected from the P1f real-device trace. P1g opens the proven native draft route, finds exactly one Send Message semantic leaf inside the marker composer, requires its DIRECT parent to be enabled/visible/clickable with ACTION_CLICK, durably claims the write, clicks once, then verifies the marker became a sent native message. No coordinates, gestures, Search, retries, or fallback writes.");',
    1,
)
activity = activity.replace('startButton.setText("Start P1f manual Send trace");', 'startButton.setText("Start P1g semantic-parent Send proof");', 1)
activity = activity.replace('NativeAdapterProofStore.markManualSendTraceArmed(this);', 'NativeAdapterProofStore.markWaitingSemanticParentSend(this);', 1)
activity = activity.replace(
    'String prompt = "Native adapter P1f manual Send trace. Reply with exactly this marker and no other text: " + marker;',
    'String prompt = "Native adapter P1g semantic-parent Send proof. Reply with exactly this marker and no other text: " + marker;',
    1,
)
activity = activity.replace(
    '        // P1e leaves ChatGPT foreground and performs no submit action.\n        // The user manually presses the real ChatGPT Send button exactly once.\n',
    '        // P1g leaves ChatGPT foreground. The Accessibility service may invoke exactly\n        // one ACTION_CLICK only on the P1f-proven direct clickable parent of the unique\n        // Send Message semantic leaf inside the marker composer subtree.\n',
    1,
)

status_anchor = '        if (started > 0) b.append("age = ").append(age).append(" s\\n");\n'
if status_anchor not in activity:
    raise SystemExit("P1g status anchor missing")
activity = activity.replace(
    status_anchor,
    status_anchor + '''        if (NativeAdapterProofStore.WAITING_SEMANTIC_PARENT_SEND.equals(state)) {\n            b.append("\\nP1g ARMED: waiting for the editable marker and exactly one P1f-proven Send Message -> direct clickable-parent target. No fallback exists.\\n");\n        } else if (NativeAdapterProofStore.SEMANTIC_PARENT_SEND_CLAIMED.equals(state)) {\n            b.append("\\nP1g CLAIMED: the one allowed ACTION_CLICK was attempted. P1g will NOT retry; waiting only for read-only sent-message verification.\\n");\n        } else if (NativeAdapterProofStore.SEMANTIC_PARENT_SEND_CONFIRMED.equals(state)) {\n            b.append("\\nPASS: P1g semantic-parent ACTION_CLICK sent the marker and the editable -> non-editable transition was verified.\\n");\n        }\n''',
    1,
)

# Re-label the retained export so a failed/uncertain P1g proof is portable too.
activity = activity.replace('Native Chat Adapter P1f - manual Send trace export', 'Native Chat Adapter P1g - semantic-parent Send proof export')
activity = activity.replace('adapterVersion: 0.39-native-adapter-p1f-export-trace', 'adapterVersion: 0.40-native-adapter-p1g-semantic-parent-send')
activity = activity.replace('native-chat-adapter-p1f-', 'native-chat-adapter-p1g-')
activity = activity.replace('=== DURABLE MANUAL CLICK SUMMARY ===', '=== DISCOVERED SEMANTIC TARGET ===')
activity = activity.replace('<no TYPE_VIEW_CLICKED source captured>', '<no semantic-parent target claimed>')
activity = activity.replace('=== BEFORE MANUAL SEND ===', '=== BEFORE P1G AUTO SEND ===')
activity = activity.replace('=== AFTER MANUAL SEND ===', '=== AFTER P1G AUTO SEND ===')
activity_path.write_text(activity)

# ---- service: bounded semantic leaf -> direct clickable parent -----------
service = service_path.read_text()
old_watch = '''            if (NativeAdapterProofStore.isManualSendTraceActive(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterP1eManualSendTrace(null);\n            }\n'''
new_watch = '''            if (NativeAdapterProofStore.isSemanticParentSendHot(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterP1gSemanticParentSend(null);\n            }\n'''
if old_watch not in service:
    raise SystemExit("P1g watchdog observer anchor missing")
service = service.replace(old_watch, new_watch, 1)
service = service.replace(
    '                    NativeAdapterProofStore.isManualSendTraceActive(NativeProbeAccessibilityService.this);\n',
    '                    NativeAdapterProofStore.isSemanticParentSendHot(NativeProbeAccessibilityService.this);\n',
    1,
)
old_event = '''        // NATIVE_ADAPTER_P1E_MANUAL_SEND_READ_ONLY_TRACE\n        observeNativeAdapterP1eManualSendTrace(event);\n'''
new_event = '''        // NATIVE_ADAPTER_P1G_BOUNDED_SEMANTIC_PARENT_SEND\n        observeNativeAdapterP1gSemanticParentSend(event);\n'''
if old_event not in service:
    raise SystemExit("P1g event observer anchor missing")
service = service.replace(old_event, new_event, 1)

insert_anchor = '    private void observeNativeAdapterP1eManualSendTrace(AccessibilityEvent event) {\n'
if insert_anchor not in service:
    raise SystemExit("P1g service insertion anchor missing")
p1g_methods = r'''    private void observeNativeAdapterP1gSemanticParentSend(AccessibilityEvent event) {
        if (!NativeAdapterProofStore.isSemanticParentSendHot(this)) return;
        if (event != null) {
            CharSequence pkg = event.getPackageName();
            if (pkg != null && !ProbeState.TARGET.equals(pkg.toString())) return;
        }

        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (!ProbeState.TARGET.equals(packageOf(root))) return;
        String marker = NativeAdapterProofStore.marker(this);
        if (marker == null || marker.isEmpty()) return;

        AccessibilityNodeInfo editable = findEditableMarkerNode(root, marker, 800);
        AccessibilityNodeInfo sent = findNonEditableMarkerNodeP1e(root, marker, 800);

        if (NativeAdapterProofStore.isWaitingSemanticParentSend(this)) {
            if (editable == null) {
                if (System.currentTimeMillis() - NativeAdapterProofStore.startedAt(this) > 10000L) {
                    NativeAdapterProofStore.fail(this,
                            "P1g did not find the unique injected marker in an editable ChatGPT composer within 10 seconds. No submit action was attempted.");
                }
                return;
            }

            // First observation only captures evidence. The watchdog/event loop must make
            // a second pass before any write, giving the projected tree one extra settle.
            if (!NativeAdapterProofStore.manualBaselineCaptured(this)) {
                NativeAdapterProofStore.captureManualBaseline(this,
                        p1eSnapshotAround(editable, "BEFORE P1G SEMANTIC-PARENT SEND"));
                NativeAdapterProofStore.appendManualTrace(this,
                        p1eTs() + " P1G BASELINE editable marker found; deferring write to next pass");
                return;
            }

            // P1f evidence showed the minimal composer scope is exactly marker.up+2.
            AccessibilityNodeInfo scope1 = editable.getParent();
            AccessibilityNodeInfo composerScope = scope1 == null ? null : scope1.getParent();
            if (composerScope == null) return;

            AccessibilityNodeInfo targetParent = null;
            AccessibilityNodeInfo targetLeaf = null;
            int matches = 0;
            ArrayList<AccessibilityNodeInfo> queue = new ArrayList<>();
            queue.add(composerScope);
            for (int i = 0; i < queue.size() && i < 140; i++) {
                AccessibilityNodeInfo n = queue.get(i);
                if (n == null) continue;
                CharSequence textCs = n.getText();
                CharSequence descCs = n.getContentDescription();
                String text = textCs == null ? "" : textCs.toString().trim();
                String desc = descCs == null ? "" : descCs.toString().trim();
                boolean semanticLeaf = "Send Message".equalsIgnoreCase(text) ||
                        "Send Message".equalsIgnoreCase(desc);
                if (semanticLeaf && n.isEnabled() && n.isVisibleToUser()) {
                    AccessibilityNodeInfo directParent = n.getParent();
                    if (directParent != null && directParent.isEnabled() &&
                            directParent.isVisibleToUser() && directParent.isClickable() &&
                            hasActionP1g(directParent, AccessibilityNodeInfo.ACTION_CLICK)) {
                        matches++;
                        if (matches == 1) {
                            targetLeaf = n;
                            targetParent = directParent;
                        }
                    }
                }
                int children = n.getChildCount();
                for (int c = 0; c < children && queue.size() < 140; c++) {
                    AccessibilityNodeInfo child = n.getChild(c);
                    if (child != null) queue.add(child);
                }
            }

            if (matches != 1 || targetParent == null || targetLeaf == null) {
                if (System.currentTimeMillis() - NativeAdapterProofStore.startedAt(this) > 10000L) {
                    NativeAdapterProofStore.fail(this,
                            "P1g requires exactly one Send Message semantic leaf whose DIRECT parent is enabled, visible, clickable and exposes ACTION_CLICK inside marker.up+2. Observed matches=" + matches + ". No action was attempted.");
                }
                return;
            }

            String targetSummary = "scope=marker.up+2; matches=1; semanticLeaf={" +
                    describeP1cNode(targetLeaf) + "}; directParent={" +
                    describeP1cNode(targetParent) + "}";
            NativeAdapterProofStore.recordManualClickSummary(this, targetSummary);

            // Durable claim BEFORE the sole write-side action. Never replay automatically.
            NativeAdapterProofStore.markSemanticParentSendClaimed(this, targetSummary);
            boolean clicked = targetParent.performAction(AccessibilityNodeInfo.ACTION_CLICK);
            NativeAdapterProofStore.appendManualTrace(this,
                    p1eTs() + " P1G CLAIMED direct-parent ACTION_CLICK result=" + clicked +
                            " | " + targetSummary);
            ProbeState.log(this, "NATIVE_ADAPTER_P1G one semantic-parent ACTION_CLICK result=" + clicked + ".");
            if (!clicked) {
                NativeAdapterProofStore.fail(this,
                        "P1g found and durably claimed the exact semantic-parent target, but ACTION_CLICK returned false. No retry or fallback action was attempted.");
            }
            return;
        }

        if (NativeAdapterProofStore.isSemanticParentSendClaimed(this)) {
            if (editable == null && sent != null) {
                NativeAdapterProofStore.appendManualTrace(this,
                        p1eTs() + " P1G CONFIRMED marker left editable composer and is now non-editable");
                NativeAdapterProofStore.completeManualSendTrace(this,
                        p1eSnapshotAround(sent, "AFTER P1G SEMANTIC-PARENT SEND"));
                NativeAdapterProofStore.markSemanticParentSendConfirmed(this);
                ProbeState.log(this, "NATIVE_ADAPTER_P1G SEND CONFIRMED read-only after one claimed ACTION_CLICK.");
                returnToP1eTraceApp();
            }
            // Intentionally no timeout-triggered retry. A claimed-but-unverified write is
            // left visible for reconciliation/export rather than blindly replayed.
        }
    }

    private boolean hasActionP1g(AccessibilityNodeInfo node, int actionId) {
        if (node == null) return false;
        for (AccessibilityNodeInfo.AccessibilityAction a : node.getActionList()) {
            if (a != null && a.getId() == actionId) return true;
        }
        return false;
    }

'''
service = service.replace(insert_anchor, p1g_methods + insert_anchor, 1)
service_path.write_text(service)

# ---- visible naming ------------------------------------------------------
ANDROID_NS = 'http://schemas.android.com/apk/res/android'
ET.register_namespace('android', ANDROID_NS)
tree = ET.parse(manifest_path)
manifest = tree.getroot()
app = manifest.find('application')
if app is None:
    raise SystemExit("P1g manifest application missing")
label_key = '{%s}label' % ANDROID_NS
name_key = '{%s}name' % ANDROID_NS
app.set(label_key, 'Native Chat Adapter P1g')
for node in list(app):
    name = node.get(name_key, '')
    if name.endswith('NativeAdapterProofActivity') or name.endswith('NativeProbeAccessibilityService') or name.endswith('NativeAdapterNotificationListenerService'):
        node.set(label_key, 'Native Chat Adapter P1g')
tree.write(manifest_path, encoding='utf-8', xml_declaration=True)

# ---- version -------------------------------------------------------------
g = gradle_path.read_text()
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 40', g, count=1)
g, n2 = re.subn(r'versionName\s+["\'][^"\']+["\']', 'versionName "0.40-native-adapter-p1g-semantic-parent-send"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("Could not update P1g version metadata")
gradle_path.write_text(g)

# ---- build-time safety assertions ---------------------------------------
activity = activity_path.read_text()
service = service_path.read_text()
a = service.index('    private void observeNativeAdapterP1gSemanticParentSend')
b = service.index('    private void observeNativeAdapterP1eManualSendTrace', a)
proof = service[a:b]
assert '"Send Message".equalsIgnoreCase' in proof
assert 'scope1 = editable.getParent()' in proof
assert 'scope1 == null ? null : scope1.getParent()' in proof
assert 'matches != 1' in proof
assert 'directParent.isClickable()' in proof
assert 'hasActionP1g(directParent, AccessibilityNodeInfo.ACTION_CLICK)' in proof
assert proof.count('performAction(AccessibilityNodeInfo.ACTION_CLICK)') == 1
assert 'markSemanticParentSendClaimed' in proof
assert 'dispatchGesture' not in proof
assert 'performGlobalAction' not in proof
assert 'GLOBAL_ACTION_' not in proof
assert 'getBoundsInScreen' not in proof
assert 'Start P1g semantic-parent Send proof' in activity
assert 'EXPORT TRACE TXT' in activity
assert 'Native Chat Adapter P1g' in manifest_path.read_text()
assert 'versionCode 40' in g
assert 'versionName "0.40-native-adapter-p1g-semantic-parent-send"' in g
