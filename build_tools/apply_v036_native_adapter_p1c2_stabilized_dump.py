import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
java_dir = root / "app/src/main/java/com/pebblebridge/poc"
activity_path = java_dir / "NativeAdapterProofActivity.java"
store_path = java_dir / "NativeAdapterProofStore.java"
service_path = java_dir / "NativeProbeAccessibilityService.java"
gradle_path = root / "app/build.gradle"

# P1c2 fixes the real-device P1c race: P1c returned as soon as the injected
# marker became visible, before ChatGPT had time to transition its Send control
# from disabled to enabled. P1c2 remains fully read-only, but holds the official
# ChatGPT activity in foreground for a bounded stabilization window after the
# first editable-marker observation, then captures the final Accessibility tree.

# ---- store: track first marker observation and observation count ----------
store = store_path.read_text()
old_wait = '''    public static void markWaitingAccessibilityDump(Context c) {\n        p(c).edit()\n                .putString("state", WAITING_ACCESSIBILITY_DUMP)\n                .putString("accessibilityDump", "")\n                .apply();\n    }\n'''
new_wait = '''    public static void markWaitingAccessibilityDump(Context c) {\n        p(c).edit()\n                .putString("state", WAITING_ACCESSIBILITY_DUMP)\n                .putString("accessibilityDump", "")\n                .putLong("p1cFirstMarkerAt", 0L)\n                .putInt("p1cMarkerObservations", 0)\n                .apply();\n    }\n'''
if old_wait not in store:
    raise SystemExit("P1c2 markWaitingAccessibilityDump block missing")
store = store.replace(old_wait, new_wait, 1)

anchor = '''    public static String accessibilityDump(Context c) {\n        return p(c).getString("accessibilityDump", "");\n    }\n\n'''
if anchor not in store:
    raise SystemExit("P1c2 accessibilityDump anchor missing")
store = store.replace(
    anchor,
    anchor + '''    public static long noteP1cMarkerObservation(Context c) {\n        SharedPreferences prefs = p(c);\n        long first = prefs.getLong("p1cFirstMarkerAt", 0L);\n        if (first <= 0L) first = System.currentTimeMillis();\n        int observations = prefs.getInt("p1cMarkerObservations", 0) + 1;\n        prefs.edit()\n                .putLong("p1cFirstMarkerAt", first)\n                .putInt("p1cMarkerObservations", observations)\n                .apply();\n        return first;\n    }\n\n    public static long p1cFirstMarkerAt(Context c) {\n        return p(c).getLong("p1cFirstMarkerAt", 0L);\n    }\n\n    public static int p1cMarkerObservations(Context c) {\n        return p(c).getInt("p1cMarkerObservations", 0);\n    }\n\n''',
    1,
)
store_path.write_text(store)

# ---- activity labels/status ----------------------------------------------
activity = activity_path.read_text()
activity = activity.replace('title.setText("Native Chat Adapter P1c");', 'title.setText("Native Chat Adapter P1c2");', 1)
activity = activity.replace(
    'subtitle.setText("Read-only Accessibility diagnostic. Deep link opens a new native chat and sets a unique draft. P1c then snapshots the composer Accessibility subtree (labels, IDs, actions and structure) and automatically returns here. It performs NO Send/click/gesture action on ChatGPT.");',
    'subtitle.setText("Stabilized read-only Accessibility diagnostic. After the injected draft first appears, P1c2 deliberately leaves ChatGPT foreground for about 4 seconds so the composer and Send control can finish updating. It then snapshots the final Accessibility tree and returns. No ChatGPT click/Send/gesture action is performed.");',
    1,
)
activity = activity.replace('startButton.setText("Start P1c read-only diagnostic");', 'startButton.setText("Start P1c2 stabilized diagnostic");', 1)
activity = activity.replace(
    'String prompt = "Native adapter P1c read-only diagnostic. Reply with exactly this marker and no other text: " + marker;',
    'String prompt = "Native adapter P1c2 stabilized read-only diagnostic. Reply with exactly this marker and no other text: " + marker;',
    1,
)
activity = activity.replace(
    'b.append("\\nWaiting for the unique marker to appear in an editable ChatGPT node. No ChatGPT action will be invoked.\\n");',
    'b.append("\\nWaiting for the marker, then a 4-second composer stabilization window. No ChatGPT action will be invoked.\\n");',
    1,
)
activity_path.write_text(activity)

# ---- service: replace immediate capture with bounded stabilization --------
service = service_path.read_text()
method_start = service.find('    private void observeNativeAdapterP1cAccessibilityDump(AccessibilityEvent event) {')
next_method = service.find('    private AccessibilityNodeInfo findEditableMarkerNode(', method_start)
if method_start < 0 or next_method < 0:
    raise SystemExit("P1c2 could not locate P1c observer method boundaries")

new_method = r'''    private static final long P1C2_STABILIZATION_MS = 4000L;

    private void observeNativeAdapterP1cAccessibilityDump(AccessibilityEvent event) {
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

        // P1c2 real-device race fix: seeing the injected text is not sufficient
        // evidence that ChatGPT has finished recomputing the composer actions.
        // Start the clock on the first marker observation and keep ChatGPT in
        // foreground until the bounded stabilization window has elapsed.
        long firstSeenAt = NativeAdapterProofStore.noteP1cMarkerObservation(this);
        long now = System.currentTimeMillis();
        long settledFor = Math.max(0L, now - firstSeenAt);
        if (settledFor < P1C2_STABILIZATION_MS) {
            return;
        }

        // Re-read the active tree after the wait instead of reusing a stale node.
        root = getRootInActiveWindow();
        if (!ProbeState.TARGET.equals(packageOf(root))) return;
        editableMarkerNode = findEditableMarkerNode(root, marker, 800);
        if (editableMarkerNode == null) return;

        AccessibilityNodeInfo scope = editableMarkerNode;
        StringBuilder ancestors = new StringBuilder();
        ancestors.append("EDITABLE MARKER NODE AFTER STABILIZATION\n");
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

        String dump = "P1c2 STABILIZED READ-ONLY COMPOSER SNAPSHOT\n" +
                "ChatGPT target=1.2026.237\n" +
                "marker=" + marker + "\n" +
                "stabilizationTargetMs=" + P1C2_STABILIZATION_MS + "\n" +
                "settledForMs=" + settledFor + "\n" +
                "markerObservations=" + NativeAdapterProofStore.p1cMarkerObservations(this) + "\n" +
                "nodesDumped=" + count[0] + "\n\n" +
                ancestors + "\nSUBTREE\n" + tree;
        NativeAdapterProofStore.captureAccessibilityDump(this, dump);
        ProbeState.log(this, "NATIVE_ADAPTER_P1C2 STABILIZED SNAPSHOT CAPTURED read-only; settledForMs=" +
                settledFor + "; observations=" + NativeAdapterProofStore.p1cMarkerObservations(this) +
                "; nodes=" + count[0] + ".");

        try {
            Intent back = new Intent(this, NativeAdapterProofActivity.class);
            back.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(back);
        } catch (Exception e) {
            ProbeState.log(this, "NATIVE_ADAPTER_P1C2 snapshot captured; automatic return blocked: " + e.getClass().getSimpleName());
        }
    }

'''
service = service[:method_start] + new_method + service[next_method:]
service = service.replace('        // NATIVE_ADAPTER_P1C_READ_ONLY_ACCESSIBILITY_DUMP\n',
                          '        // NATIVE_ADAPTER_P1C2_STABILIZED_READ_ONLY_ACCESSIBILITY_DUMP\n', 1)
service_path.write_text(service)

# ---- version: same applicationId as P1c, install-over --------------------
g = gradle_path.read_text()
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 36', g, count=1)
g, n2 = re.subn(r'versionName\s+["\'][^"\']+["\']', 'versionName "0.36-native-adapter-p1c2-stabilized"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("Could not update P1c2 version metadata")
gradle_path.write_text(g)

# Safety assertions: the diagnostic remains read-only with respect to ChatGPT.
activity = activity_path.read_text()
service = service_path.read_text()
a = service.index('    private static final long P1C2_STABILIZATION_MS')
b = service.index('    private AccessibilityNodeInfo findEditableMarkerNode(', a)
diag = service[a:b]
assert 'P1C2_STABILIZATION_MS = 4000L' in diag
assert 'noteP1cMarkerObservation' in diag
assert 'getRootInActiveWindow()' in diag
assert 'performAction' not in diag
assert 'dispatchGesture' not in diag
assert 'GLOBAL_ACTION' not in diag
assert 'Start P1c2 stabilized diagnostic' in activity
assert 'versionCode 36' in g
assert 'versionName "0.36-native-adapter-p1c2-stabilized"' in g
