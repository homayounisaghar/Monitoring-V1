import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
java_dir = root / "app/src/main/java/com/pebblebridge/poc"
activity_path = java_dir / "NativeAdapterProofActivity.java"
store_path = java_dir / "NativeAdapterProofStore.java"
service_path = java_dir / "NativeProbeAccessibilityService.java"
listener_path = java_dir / "NativeAdapterNotificationListenerService.java"
manifest_path = root / "app/src/main/AndroidManifest.xml"
gradle_path = root / "app/build.gradle"

# P1e is a READ-ONLY observer of the actual manual Send transition.
# The only write into ChatGPT is the already-proven software-addressed draft injection.
# After the draft appears, the user manually presses ChatGPT's real Send button exactly once.
# P1e records Accessibility events/source nodes/tree transitions and ChatGPT notifications.
# It never invokes performAction/dispatchGesture/global actions/coordinates on ChatGPT.

# ---- store ---------------------------------------------------------------
store = store_path.read_text()
const_anchor = '    public static final String ACCESSIBILITY_DUMP_CAPTURED = "ACCESSIBILITY_DUMP_CAPTURED";\n'
if const_anchor not in store:
    raise SystemExit("P1e store constants anchor missing")
store = store.replace(
    const_anchor,
    const_anchor +
    '    public static final String MANUAL_SEND_TRACE_ARMED = "MANUAL_SEND_TRACE_ARMED";\n'
    '    public static final String MANUAL_SEND_TRACE_COMPLETE = "MANUAL_SEND_TRACE_COMPLETE";\n',
    1,
)

method_anchor = '''    public static String accessibilityDump(Context c) {\n        return p(c).getString("accessibilityDump", "");\n    }\n\n'''
if method_anchor not in store:
    raise SystemExit("P1e store method anchor missing")
store = store.replace(
    method_anchor,
    method_anchor + r'''    public static void markManualSendTraceArmed(Context c) {
        p(c).edit()
                .putString("state", MANUAL_SEND_TRACE_ARMED)
                .putString("manualTrace", "")
                .putString("manualBaseline", "")
                .putString("manualAfter", "")
                .putBoolean("manualBaselineCaptured", false)
                .putLong("manualTraceLastAt", 0L)
                .apply();
    }

    public static boolean isManualSendTraceActive(Context c) {
        return MANUAL_SEND_TRACE_ARMED.equals(state(c));
    }

    public static void appendManualTrace(Context c, String line) {
        if (line == null || line.isEmpty()) return;
        String old = p(c).getString("manualTrace", "");
        String next = old + line + "\n";
        if (next.length() > 30000) next = "...[older trace truncated]\n" + next.substring(next.length() - 28000);
        p(c).edit().putString("manualTrace", next).putLong("manualTraceLastAt", System.currentTimeMillis()).apply();
    }

    public static String manualTrace(Context c) { return p(c).getString("manualTrace", ""); }
    public static String manualBaseline(Context c) { return p(c).getString("manualBaseline", ""); }
    public static String manualAfter(Context c) { return p(c).getString("manualAfter", ""); }
    public static boolean manualBaselineCaptured(Context c) { return p(c).getBoolean("manualBaselineCaptured", false); }

    public static void captureManualBaseline(Context c, String snapshot) {
        String safe = snapshot == null ? "" : snapshot;
        if (safe.length() > 14000) safe = safe.substring(0, 14000) + "\n...[truncated]";
        p(c).edit().putString("manualBaseline", safe).putBoolean("manualBaselineCaptured", true).apply();
    }

    public static void completeManualSendTrace(Context c, String after) {
        String safe = after == null ? "" : after;
        if (safe.length() > 14000) safe = safe.substring(0, 14000) + "\n...[truncated]";
        p(c).edit().putString("manualAfter", safe).putString("state", MANUAL_SEND_TRACE_COMPLETE).apply();
    }

''',
    1,
)
store_path.write_text(store)

# ---- activity ------------------------------------------------------------
activity = activity_path.read_text()
activity = activity.replace('title.setText("Native Chat Adapter P1d");', 'title.setText("Native Chat Adapter P1e");', 1)
activity = activity.replace(
    'subtitle.setText("Bounded IME submit proof selected from the stabilized P1c2 dump. After the injected draft settles for about 4 seconds, P1d may invoke exactly one ACTION_IME_ENTER on the same enabled editable marker node, then only observes whether the marker becomes a sent native message. No coordinates, Search, gesture taps, or Send-button guessing.");',
    'subtitle.setText("Manual Send black-box tracer. P1e opens a new native ChatGPT draft, then performs NO submit action. When the draft is visible, manually press ChatGPT Send exactly once. P1e records the real Accessibility click source, ancestor/action surface, composer transition and any ChatGPT notification, then returns with the trace.");',
    1,
)
activity = activity.replace('startButton.setText("Start P1d IME submit proof");', 'startButton.setText("Start P1e manual Send trace");', 1)
activity = activity.replace('NativeAdapterProofStore.markWaitingImeSubmit(this);', 'NativeAdapterProofStore.markManualSendTraceArmed(this);', 1)
activity = activity.replace(
    'String prompt = "Native adapter P1d IME submit proof. Reply with exactly this marker and no other text: " + marker;',
    'String prompt = "Native adapter P1e manual Send trace. Reply with exactly this marker and no other text: " + marker;',
    1,
)
activity = activity.replace(
    '        // P1d leaves ChatGPT foreground. After a bounded stabilization window,\n        // Accessibility may invoke only ACTION_IME_ENTER on the exact editable marker node.\n',
    '        // P1e leaves ChatGPT foreground and performs no submit action.\n        // The user manually presses the real ChatGPT Send button exactly once.\n',
    1,
)

p1d_status = '''        String semanticSendNode = NativeAdapterProofStore.semanticSendNode(this);\n        if (!semanticSendNode.isEmpty()) b.append("IME target = ").append(semanticSendNode).append('\\n');\n        if (NativeAdapterProofStore.SEND_CONFIRMED.equals(state)) {\n            b.append("\\nPASS: ACTION_IME_ENTER was accepted and the marker left the editable composer and appeared as a non-editable native chat message.\\n");\n        } else if (NativeAdapterProofStore.SEND_DISPATCHED.equals(state)) {\n            b.append("\\nACTION_IME_ENTER was accepted. Waiting for read-only confirmation that the marker became a sent message.\\n");\n        } else if (NativeAdapterProofStore.WAITING_SEMANTIC_SEND.equals(state)) {\n            b.append("\\nWaiting for the editable marker, then a 4-second stabilization window and exact ACTION_IME_ENTER availability. No fallback action exists.\\n");\n        }\n'''
p1e_status = '''        if (NativeAdapterProofStore.MANUAL_SEND_TRACE_ARMED.equals(state)) {\n            b.append("\\nTRACE ARMED: ChatGPT stays foreground. When the injected draft is visible and Send is active, press the REAL ChatGPT Send button exactly once. Do not tap anything else.\\n");\n        } else if (NativeAdapterProofStore.MANUAL_SEND_TRACE_COMPLETE.equals(state)) {\n            b.append("\\nTRACE COMPLETE: manual Send transition captured. This does NOT mean an automated submit path is proven.\\n");\n        }\n        String manualTrace = NativeAdapterProofStore.manualTrace(this);\n        String manualBaseline = NativeAdapterProofStore.manualBaseline(this);\n        String manualAfter = NativeAdapterProofStore.manualAfter(this);\n        if (!manualBaseline.isEmpty()) b.append("\\n=== BEFORE MANUAL SEND ===\\n").append(manualBaseline).append('\\n');\n        if (!manualTrace.isEmpty()) b.append("\\n=== EVENT TRACE ===\\n").append(manualTrace);\n        if (!manualAfter.isEmpty()) b.append("\\n=== AFTER MANUAL SEND ===\\n").append(manualAfter).append('\\n');\n'''
if p1d_status not in activity:
    raise SystemExit("P1e P1d status block missing")
activity = activity.replace(p1d_status, p1e_status, 1)
activity_path.write_text(activity)

# ---- accessibility service ---------------------------------------------
service = service_path.read_text()
service = service.replace(
    '''            if (NativeAdapterProofStore.isSemanticSendHot(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterP1dImeSubmit(null);\n            }\n''',
    '''            if (NativeAdapterProofStore.isManualSendTraceActive(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterP1eManualSendTrace(null);\n            }\n''',
    1,
)
service = service.replace(
    '''                    NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this) ||\n                    NativeAdapterProofStore.isSemanticSendHot(NativeProbeAccessibilityService.this);\n''',
    '''                    NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this) ||\n                    NativeAdapterProofStore.isManualSendTraceActive(NativeProbeAccessibilityService.this);\n''',
    1,
)
service = service.replace(
    '''        // NATIVE_ADAPTER_P1D_BOUNDED_IME_SUBMIT\n        observeNativeAdapterP1dImeSubmit(event);\n''',
    '''        // NATIVE_ADAPTER_P1E_MANUAL_SEND_READ_ONLY_TRACE\n        observeNativeAdapterP1eManualSendTrace(event);\n''',
    1,
)

insert_anchor = '    private static final long P1D_STABILIZATION_MS = 4000L;\n'
if insert_anchor not in service:
    raise SystemExit("P1e service insertion anchor missing")

p1e_methods = r'''    private void observeNativeAdapterP1eManualSendTrace(AccessibilityEvent event) {
        if (!NativeAdapterProofStore.isManualSendTraceActive(this)) return;
        if (event != null) {
            CharSequence pkg = event.getPackageName();
            if (pkg != null && !ProbeState.TARGET.equals(pkg.toString())) return;
            recordP1eEvent(event);
        }

        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (!ProbeState.TARGET.equals(packageOf(root))) return;
        String marker = NativeAdapterProofStore.marker(this);
        if (marker == null || marker.isEmpty()) return;

        AccessibilityNodeInfo editable = findEditableMarkerNode(root, marker, 800);
        if (editable != null && !NativeAdapterProofStore.manualBaselineCaptured(this)) {
            String baseline = p1eSnapshotAround(editable, "BEFORE MANUAL SEND");
            NativeAdapterProofStore.captureManualBaseline(this, baseline);
            NativeAdapterProofStore.appendManualTrace(this, p1eTs() + " BASELINE marker became editable; tracer armed for one manual Send tap");
            ProbeState.log(this, "NATIVE_ADAPTER_P1E baseline captured; waiting for one manual ChatGPT Send tap.");
            return;
        }

        AccessibilityNodeInfo sent = findNonEditableMarkerNodeP1e(root, marker, 800);
        if (NativeAdapterProofStore.manualBaselineCaptured(this) && editable == null && sent != null) {
            NativeAdapterProofStore.appendManualTrace(this, p1eTs() + " TRANSITION marker left editable composer and is now non-editable");
            String after = p1eSnapshotAround(sent, "AFTER MANUAL SEND");
            NativeAdapterProofStore.completeManualSendTrace(this, after);
            ProbeState.log(this, "NATIVE_ADAPTER_P1E manual Send transition captured read-only.");
            returnToP1eTraceApp();
        }
    }

    private void recordP1eEvent(AccessibilityEvent event) {
        if (event == null) return;
        int type = event.getEventType();
        boolean interesting = type == AccessibilityEvent.TYPE_VIEW_CLICKED ||
                type == AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED ||
                type == AccessibilityEvent.TYPE_VIEW_FOCUSED ||
                type == AccessibilityEvent.TYPE_VIEW_TEXT_SELECTION_CHANGED ||
                type == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED ||
                type == AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED ||
                type == AccessibilityEvent.TYPE_WINDOWS_CHANGED ||
                type == AccessibilityEvent.TYPE_VIEW_ACCESSIBILITY_FOCUSED;
        if (!interesting) return;

        StringBuilder line = new StringBuilder();
        line.append(p1eTs()).append(' ')
                .append(AccessibilityEvent.eventTypeToString(type))
                .append(" class=").append(event.getClassName() == null ? "" : event.getClassName())
                .append(" action=").append(event.getAction())
                .append(" contentChangeTypes=").append(event.getContentChangeTypes());
        if (event.getContentDescription() != null) {
            line.append(" desc=").append(p1cAbbrev(event.getContentDescription().toString(), 100));
        }
        if (event.getText() != null && !event.getText().isEmpty()) {
            line.append(" text=").append(p1cAbbrev(event.getText().toString(), 120));
        }

        AccessibilityNodeInfo src = event.getSource();
        if (src != null) {
            line.append(" | source{").append(describeP1cNode(src)).append('}');
        }
        NativeAdapterProofStore.appendManualTrace(this, line.toString());

        if (type == AccessibilityEvent.TYPE_VIEW_CLICKED && src != null) {
            StringBuilder click = new StringBuilder();
            click.append(p1eTs()).append(" MANUAL CLICK SOURCE CHAIN\n");
            AccessibilityNodeInfo cur = src;
            for (int up = 0; up < 6 && cur != null; up++) {
                click.append("  up+").append(up).append(": ").append(describeP1cNode(cur)).append('\n');
                cur = cur.getParent();
            }
            AccessibilityNodeInfo scope = src.getParent();
            if (scope == null) scope = src;
            StringBuilder subtree = new StringBuilder();
            int[] count = new int[] {0};
            dumpP1cSubtree(scope, 0, 5, 120, subtree, count);
            click.append("  CLICK NEIGHBORHOOD nodes=").append(count[0]).append('\n').append(subtree);
            NativeAdapterProofStore.appendManualTrace(this, click.toString());
        }
    }

    private AccessibilityNodeInfo findNonEditableMarkerNodeP1e(AccessibilityNodeInfo root, String marker, int limit) {
        if (root == null || marker == null || marker.isEmpty()) return null;
        ArrayList<AccessibilityNodeInfo> queue = new ArrayList<>();
        queue.add(root);
        for (int i = 0; i < queue.size() && i < limit; i++) {
            AccessibilityNodeInfo n = queue.get(i);
            if (n == null) continue;
            CharSequence text = n.getText();
            CharSequence desc = n.getContentDescription();
            boolean contains = (text != null && text.toString().contains(marker)) ||
                    (desc != null && desc.toString().contains(marker));
            if (contains && !n.isEditable()) return n;
            int children = n.getChildCount();
            for (int c = 0; c < children && queue.size() < limit; c++) {
                AccessibilityNodeInfo child = n.getChild(c);
                if (child != null) queue.add(child);
            }
        }
        return null;
    }

    private String p1eSnapshotAround(AccessibilityNodeInfo node, String heading) {
        AccessibilityNodeInfo scope = node;
        StringBuilder ancestors = new StringBuilder();
        ancestors.append(heading).append('\n');
        ancestors.append("MARKER NODE: ").append(describeP1cNode(node)).append("\n\nANCESTOR CHAIN\n");
        for (int up = 0; up < 5; up++) {
            AccessibilityNodeInfo parent = scope.getParent();
            if (parent == null) break;
            scope = parent;
            ancestors.append("up+").append(up + 1).append(": ").append(describeP1cNode(scope)).append('\n');
        }
        StringBuilder tree = new StringBuilder();
        int[] count = new int[] {0};
        dumpP1cSubtree(scope, 0, 8, 180, tree, count);
        return ancestors + "\nSUBTREE nodes=" + count[0] + "\n" + tree;
    }

    private String p1eTs() {
        long start = NativeAdapterProofStore.startedAt(this);
        long delta = start <= 0 ? 0 : Math.max(0L, System.currentTimeMillis() - start);
        return "+" + delta + "ms";
    }

    private void returnToP1eTraceApp() {
        try {
            Intent back = new Intent(this, NativeAdapterProofActivity.class);
            back.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(back);
        } catch (Exception e) {
            ProbeState.log(this, "NATIVE_ADAPTER_P1E trace complete; automatic return blocked: " + e.getClass().getSimpleName());
        }
    }

'''
service = service.replace(insert_anchor, p1e_methods + insert_anchor, 1)
service_path.write_text(service)

# ---- notification listener: observe notifications during manual trace ----
listener = listener_path.read_text()
old_guard = '        if (!NativeAdapterProofStore.isAwaitingNotification(this)) return;\n\n'
new_guard = '''        boolean manualTrace = NativeAdapterProofStore.isManualSendTraceActive(this);\n        if (!NativeAdapterProofStore.isAwaitingNotification(this) && !manualTrace) return;\n\n'''
if old_guard not in listener:
    raise SystemExit("P1e notification guard anchor missing")
listener = listener.replace(old_guard, new_guard, 1)
old_record = '''        NativeAdapterProofStore.recordNotification(this, tag, text);\n\n        if (!isPlausibleConversationId(tag)) return;\n'''
new_record = '''        NativeAdapterProofStore.recordNotification(this, tag, text);\n        if (manualTrace) {\n            long start = NativeAdapterProofStore.startedAt(this);\n            long delta = start <= 0 ? 0 : Math.max(0L, System.currentTimeMillis() - start);\n            NativeAdapterProofStore.appendManualTrace(this, "+" + delta + "ms CHATGPT NOTIFICATION tag=" +\n                    (tag == null ? "" : tag) + " text=" + text);\n            return;\n        }\n\n        if (!isPlausibleConversationId(tag)) return;\n'''
if old_record not in listener:
    raise SystemExit("P1e notification record anchor missing")
listener = listener.replace(old_record, new_record, 1)
listener_path.write_text(listener)

# ---- visible Android naming: launcher + Settings use one name ------------
ANDROID_NS = 'http://schemas.android.com/apk/res/android'
ET.register_namespace('android', ANDROID_NS)
tree = ET.parse(manifest_path)
manifest = tree.getroot()
app = manifest.find('application')
if app is None:
    raise SystemExit("P1e manifest application missing")
label_key = '{%s}label' % ANDROID_NS
name_key = '{%s}name' % ANDROID_NS
app.set(label_key, 'Native Chat Adapter P1e')
for node in list(app):
    name = node.get(name_key, '')
    if name.endswith('NativeAdapterProofActivity') or name.endswith('NativeProbeAccessibilityService') or name.endswith('NativeAdapterNotificationListenerService'):
        node.set(label_key, 'Native Chat Adapter P1e')
tree.write(manifest_path, encoding='utf-8', xml_declaration=True)

# ---- version -------------------------------------------------------------
g = gradle_path.read_text()
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 38', g, count=1)
g, n2 = re.subn(r'versionName\s+["\'][^"\']+["\']', 'versionName "0.38-native-adapter-p1e-manual-send-trace"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("Could not update P1e version metadata")
gradle_path.write_text(g)

# Build-time safety assertions. P1e's manual-trace observer must be read-only.
activity = activity_path.read_text()
service = service_path.read_text()
a = service.index('    private void observeNativeAdapterP1eManualSendTrace')
b = service.index('    private static final long P1D_STABILIZATION_MS', a)
p1e = service[a:b]
for forbidden in ('performAction(', 'dispatchGesture', 'performGlobalAction', 'GLOBAL_ACTION_'):
    assert forbidden not in p1e, forbidden
assert 'TYPE_VIEW_CLICKED' in p1e
assert 'MANUAL CLICK SOURCE CHAIN' in p1e
assert 'findNonEditableMarkerNodeP1e' in p1e
assert 'Start P1e manual Send trace' in activity
assert 'markManualSendTraceArmed' in activity
assert 'Native Chat Adapter P1e' in manifest_path.read_text()
assert 'versionCode 38' in g
assert 'versionName "0.38-native-adapter-p1e-manual-send-trace"' in g
