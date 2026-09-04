import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
java_dir = root / "app/src/main/java/com/pebblebridge/poc"
activity_path = java_dir / "NativeAdapterProofActivity.java"
store_path = java_dir / "NativeAdapterProofStore.java"
service_path = java_dir / "NativeProbeAccessibilityService.java"
gradle_path = root / "app/build.gradle"

# P1c is deliberately READ-ONLY with respect to ChatGPT. It opens the proven
# deep link, injects a unique draft marker, snapshots the Accessibility subtree
# around the editable composer, persists the snapshot, and returns to the
# companion. It never performs an Accessibility action on a ChatGPT node.

# ---- store ---------------------------------------------------------------
store = store_path.read_text()
store = store.replace(
    '    public static final String SEND_CONFIRMED = "SEND_CONFIRMED";\n',
    '    public static final String SEND_CONFIRMED = "SEND_CONFIRMED";\n'
    '    public static final String WAITING_ACCESSIBILITY_DUMP = "WAITING_ACCESSIBILITY_DUMP";\n'
    '    public static final String ACCESSIBILITY_DUMP_CAPTURED = "ACCESSIBILITY_DUMP_CAPTURED";\n',
    1,
)

pending_old = '''    public static boolean isPending(Context c) {\n        String s = state(c);\n        return WAITING_NOTIFICATION.equals(s) || CANDIDATE_CAPTURED.equals(s) || VERIFYING.equals(s) ||\n                WAITING_SEMANTIC_SEND.equals(s) || SEND_DISPATCHED.equals(s);\n    }\n'''
pending_new = '''    public static boolean isPending(Context c) {\n        String s = state(c);\n        return WAITING_NOTIFICATION.equals(s) || CANDIDATE_CAPTURED.equals(s) || VERIFYING.equals(s) ||\n                WAITING_SEMANTIC_SEND.equals(s) || SEND_DISPATCHED.equals(s) ||\n                WAITING_ACCESSIBILITY_DUMP.equals(s);\n    }\n'''
if pending_old not in store:
    raise SystemExit("P1c expected P1b isPending block missing")
store = store.replace(pending_old, pending_new, 1)

anchor = '''    public static boolean semanticSendConfirmed(Context c) {\n        return p(c).getBoolean("semanticSendConfirmed", false);\n    }\n\n'''
if anchor not in store:
    raise SystemExit("P1c store insertion anchor missing")
store = store.replace(
    anchor,
    anchor + '''    public static void markWaitingAccessibilityDump(Context c) {\n        p(c).edit()\n                .putString("state", WAITING_ACCESSIBILITY_DUMP)\n                .putString("accessibilityDump", "")\n                .apply();\n    }\n\n    public static boolean isAwaitingAccessibilityDump(Context c) {\n        return WAITING_ACCESSIBILITY_DUMP.equals(state(c));\n    }\n\n    public static void captureAccessibilityDump(Context c, String dump) {\n        String safe = dump == null ? "" : dump;\n        if (safe.length() > 20000) safe = safe.substring(0, 20000) + "\\n...[truncated]";\n        p(c).edit()\n                .putString("accessibilityDump", safe)\n                .putString("state", ACCESSIBILITY_DUMP_CAPTURED)\n                .apply();\n    }\n\n    public static String accessibilityDump(Context c) {\n        return p(c).getString("accessibilityDump", "");\n    }\n\n''',
    1,
)
store_path.write_text(store)

# ---- activity ------------------------------------------------------------
s = activity_path.read_text()
s = s.replace('title.setText("Native Chat Adapter P1b");', 'title.setText("Native Chat Adapter P1c");', 1)
s = s.replace(
    'subtitle.setText("Strict semantic Send proof. Deep link opens a new native chat and sets the draft; Accessibility may click ONLY the exact APK-derived semantic Send message node after the unique marker is visible in the editable composer. No coordinates, gesture taps, Search, or ancestor guessing.");',
    'subtitle.setText("Read-only Accessibility diagnostic. Deep link opens a new native chat and sets a unique draft. P1c then snapshots the composer Accessibility subtree (labels, IDs, actions and structure) and automatically returns here. It performs NO Send/click/gesture action on ChatGPT.");',
    1,
)
s = s.replace('startButton.setText("Start P1b semantic Send proof");', 'startButton.setText("Start P1c read-only diagnostic");', 1)
s = s.replace(
    'NativeAdapterProofStore.markWaitingSemanticSend(this);',
    'NativeAdapterProofStore.markWaitingAccessibilityDump(this);',
    1,
)
s = s.replace(
    'String prompt = "Native adapter P1b semantic Send proof. Reply with exactly this marker and no other text: " + marker;',
    'String prompt = "Native adapter P1c read-only diagnostic. Reply with exactly this marker and no other text: " + marker;',
    1,
)
s = s.replace(
    '        // P1b leaves ChatGPT foreground. The Accessibility service observes the\n        // exact editable marker and may invoke only the exact semantic Send message node.\n        // The user returns manually after observing whether submission occurred.\n',
    '        // P1c is read-only: the Accessibility service snapshots the composer tree\n        // after the marker appears, then returns this companion to foreground.\n',
    1,
)

status_anchor = '        if (started > 0) b.append("age = ").append(age).append(" s\\n");\n'
if status_anchor not in s:
    raise SystemExit("P1c status anchor missing")
s = s.replace(
    status_anchor,
    status_anchor + '''        String accessibilityDump = NativeAdapterProofStore.accessibilityDump(this);\n        if (NativeAdapterProofStore.ACCESSIBILITY_DUMP_CAPTURED.equals(state)) {\n            b.append("\\nPASS: read-only composer Accessibility snapshot captured.\\n\\n");\n            b.append(accessibilityDump);\n        } else if (NativeAdapterProofStore.WAITING_ACCESSIBILITY_DUMP.equals(state)) {\n            b.append("\\nWaiting for the unique marker to appear in an editable ChatGPT node. No ChatGPT action will be invoked.\\n");\n        }\n''',
    1,
)
activity_path.write_text(s)

# ---- Accessibility service ---------------------------------------------
service = service_path.read_text()
old_watchdog = '''        @Override public void run() {\n            if (NativeAdapterProofStore.isSemanticSendHot(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterSemanticSend(null);\n            }\n            if (NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterProof(null);\n            }\n            if (isActiveProbe()) processTargetWindow("watchdog");\n            boolean hot = isActiveProbe() ||\n                    NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this) ||\n                    NativeAdapterProofStore.isSemanticSendHot(NativeProbeAccessibilityService.this);\n            handler.postDelayed(this, hot ? 250 : 900);\n        }\n'''
new_watchdog = '''        @Override public void run() {\n            if (NativeAdapterProofStore.isAwaitingAccessibilityDump(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterP1cAccessibilityDump(null);\n            }\n            if (NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterProof(null);\n            }\n            if (isActiveProbe()) processTargetWindow("watchdog");\n            boolean hot = isActiveProbe() ||\n                    NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this) ||\n                    NativeAdapterProofStore.isAwaitingAccessibilityDump(NativeProbeAccessibilityService.this);\n            handler.postDelayed(this, hot ? 250 : 900);\n        }\n'''
if old_watchdog not in service:
    raise SystemExit("P1c watchdog block missing")
service = service.replace(old_watchdog, new_watchdog, 1)

old_event = '''        // NATIVE_ADAPTER_P1B_STRICT_SEMANTIC_SEND\n        observeNativeAdapterSemanticSend(event);\n        // NATIVE_ADAPTER_P1_READ_ONLY_RECEIPT_OBSERVER\n        observeNativeAdapterProof(event);\n'''
new_event = '''        // NATIVE_ADAPTER_P1C_READ_ONLY_ACCESSIBILITY_DUMP\n        observeNativeAdapterP1cAccessibilityDump(event);\n        // NATIVE_ADAPTER_P1_READ_ONLY_RECEIPT_OBSERVER\n        observeNativeAdapterProof(event);\n'''
if old_event not in service:
    raise SystemExit("P1c event observer block missing")
service = service.replace(old_event, new_event, 1)

insert_anchor = '    private void observeNativeAdapterSemanticSend(AccessibilityEvent event) {\n'
if insert_anchor not in service:
    raise SystemExit("P1c insertion anchor missing")

diag_methods = r'''    private void observeNativeAdapterP1cAccessibilityDump(AccessibilityEvent event) {
        if (!NativeAdapterProofStore.isAwaitingAccessibilityDump(this)) return;
        if (event != null) {
            CharSequence pkg = event.getPackageName();
            if (pkg != null && !ProbeState.TARGET.equals(pkg.toString())) return;
        }
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (!ProbeState.TARGET.equals(packageOf(root))) return;
        String marker = NativeAdapterProofStore.marker(this);
        if (marker == null || marker.isEmpty()) return;

        AccessibilityNodeInfo editableMarkerNode = findEditableMarkerNode(root, marker, 800);
        if (editableMarkerNode == null) return;

        AccessibilityNodeInfo scope = editableMarkerNode;
        StringBuilder ancestors = new StringBuilder();
        ancestors.append("EDITABLE MARKER NODE\n");
        ancestors.append(describeP1cNode(editableMarkerNode)).append("\n\nANCESTOR CHAIN\n");
        for (int up = 0; up < 5; up++) {
            AccessibilityNodeInfo parent = scope.getParent();
            if (parent == null) break;
            scope = parent;
            ancestors.append("up+").append(up + 1).append(": ")
                    .append(describeP1cNode(scope)).append('\n');
        }

        StringBuilder tree = new StringBuilder();
        int[] count = new int[] {0};
        dumpP1cSubtree(scope, 0, 8, 180, tree, count);

        String dump = "P1c READ-ONLY COMPOSER SNAPSHOT\n" +
                "ChatGPT target=1.2026.237\n" +
                "marker=" + marker + "\n" +
                "nodesDumped=" + count[0] + "\n\n" +
                ancestors + "\nSUBTREE\n" + tree;
        NativeAdapterProofStore.captureAccessibilityDump(this, dump);
        ProbeState.log(this, "NATIVE_ADAPTER_P1C SNAPSHOT CAPTURED read-only; nodes=" + count[0] + ".");

        try {
            Intent back = new Intent(this, NativeAdapterProofActivity.class);
            back.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(back);
        } catch (Exception e) {
            ProbeState.log(this, "NATIVE_ADAPTER_P1C snapshot captured; automatic return blocked: " + e.getClass().getSimpleName());
        }
    }

    private AccessibilityNodeInfo findEditableMarkerNode(AccessibilityNodeInfo root, String marker, int limit) {
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
            if (contains && n.isEditable()) return n;
            int children = n.getChildCount();
            for (int c = 0; c < children && queue.size() < limit; c++) {
                AccessibilityNodeInfo child = n.getChild(c);
                if (child != null) queue.add(child);
            }
        }
        return null;
    }

    private void dumpP1cSubtree(AccessibilityNodeInfo n, int depth, int maxDepth, int maxNodes,
                                StringBuilder out, int[] count) {
        if (n == null || depth > maxDepth || count[0] >= maxNodes) return;
        count[0]++;
        for (int i = 0; i < depth; i++) out.append("  ");
        out.append('[').append(count[0]).append("] ").append(describeP1cNode(n)).append('\n');
        int children = n.getChildCount();
        for (int c = 0; c < children && count[0] < maxNodes; c++) {
            AccessibilityNodeInfo child = n.getChild(c);
            if (child != null) dumpP1cSubtree(child, depth + 1, maxDepth, maxNodes, out, count);
        }
    }

    private String describeP1cNode(AccessibilityNodeInfo n) {
        if (n == null) return "<null>";
        String cls = n.getClassName() == null ? "" : n.getClassName().toString();
        String text = n.getText() == null ? "" : p1cAbbrev(n.getText().toString(), 120);
        String desc = n.getContentDescription() == null ? "" : p1cAbbrev(n.getContentDescription().toString(), 120);
        String id = n.getViewIdResourceName() == null ? "" : n.getViewIdResourceName();
        android.graphics.Rect r = new android.graphics.Rect();
        n.getBoundsInScreen(r);
        StringBuilder actions = new StringBuilder();
        for (AccessibilityNodeInfo.AccessibilityAction a : n.getActionList()) {
            if (a == null) continue;
            if (actions.length() > 0) actions.append(" | ");
            actions.append(a.toString()).append("#").append(a.getId());
            CharSequence label = a.getLabel();
            if (label != null && label.length() > 0) actions.append("(").append(label).append(")");
        }
        return "class=" + cls +
                "; text=" + text +
                "; desc=" + desc +
                "; id=" + id +
                "; editable=" + n.isEditable() +
                "; clickable=" + n.isClickable() +
                "; enabled=" + n.isEnabled() +
                "; focusable=" + n.isFocusable() +
                "; visible=" + n.isVisibleToUser() +
                "; children=" + n.getChildCount() +
                "; bounds=" + r.toShortString() +
                "; actions=[" + actions + "]";
    }

    private String p1cAbbrev(String s, int max) {
        if (s == null) return "";
        String one = s.replace('\n', ' ').replace('\r', ' ');
        return one.length() <= max ? one : one.substring(0, max) + "...";
    }

'''
service = service.replace(insert_anchor, diag_methods + insert_anchor, 1)
service_path.write_text(service)

# ---- version -------------------------------------------------------------
g = gradle_path.read_text()
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 35', g, count=1)
g, n2 = re.subn(r'versionName\s+["\'][^"\']+["\']', 'versionName "0.35-native-adapter-p1c"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("Could not update P1c version metadata")
gradle_path.write_text(g)

# Safety assertions: P1c diagnostic method itself is read-only with respect to
# ChatGPT. Bounds are recorded only as diagnostics; they are never used to select
# or actuate a node.
activity = activity_path.read_text()
service = service_path.read_text()
assert 'Start P1c read-only diagnostic' in activity
assert 'markWaitingAccessibilityDump' in activity
assert 'NATIVE_ADAPTER_P1C_READ_ONLY_ACCESSIBILITY_DUMP' in service
assert 'observeNativeAdapterP1cAccessibilityDump' in service
assert 'performAction' not in diag_methods
assert 'dispatchGesture' not in diag_methods
assert 'GLOBAL_ACTION' not in diag_methods
assert 'versionCode 35' in g
assert 'versionName "0.35-native-adapter-p1c"' in g
