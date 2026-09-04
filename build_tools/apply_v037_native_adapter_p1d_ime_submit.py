import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
java_dir = root / "app/src/main/java/com/pebblebridge/poc"
activity_path = java_dir / "NativeAdapterProofActivity.java"
store_path = java_dir / "NativeAdapterProofStore.java"
service_path = java_dir / "NativeProbeAccessibilityService.java"
gradle_path = root / "app/build.gradle"

# P1d is selected directly from the stabilized P1c2 real-device dump.
# That dump proved the actual populated ChatGPT EditText exposes an enabled
# ACTION_IME_ENTER after stabilization. P1d performs exactly one bounded
# semantic IME action on that exact editable marker node. No coordinates,
# Search, gestures, ancestor guessing, or Send-button guessing are allowed.

# ---- store ---------------------------------------------------------------
store = store_path.read_text()
anchor = '''    public static int p1cMarkerObservations(Context c) {\n        return p(c).getInt("p1cMarkerObservations", 0);\n    }\n\n'''
if anchor not in store:
    raise SystemExit("P1d P1c2 stabilization anchor missing")
store = store.replace(
    anchor,
    anchor + '''    public static void markWaitingImeSubmit(Context c) {\n        p(c).edit()\n                .putString("state", WAITING_SEMANTIC_SEND)\n                .putBoolean("semanticSendDispatched", false)\n                .putBoolean("semanticSendConfirmed", false)\n                .putString("semanticSendNode", "")\n                .putLong("p1cFirstMarkerAt", 0L)\n                .putInt("p1cMarkerObservations", 0)\n                .apply();\n    }\n\n''',
    1,
)
store_path.write_text(store)

# ---- activity ------------------------------------------------------------
activity = activity_path.read_text()
activity = activity.replace('title.setText("Native Chat Adapter P1c2");', 'title.setText("Native Chat Adapter P1d");', 1)
activity = activity.replace(
    'subtitle.setText("Stabilized read-only Accessibility diagnostic. After the injected draft first appears, P1c2 deliberately leaves ChatGPT foreground for about 4 seconds so the composer and Send control can finish updating. It then snapshots the final Accessibility tree and returns. No ChatGPT click/Send/gesture action is performed.");',
    'subtitle.setText("Bounded IME submit proof selected from the stabilized P1c2 dump. After the injected draft settles for about 4 seconds, P1d may invoke exactly one ACTION_IME_ENTER on the same enabled editable marker node, then only observes whether the marker becomes a sent native message. No coordinates, Search, gesture taps, or Send-button guessing.");',
    1,
)
activity = activity.replace('startButton.setText("Start P1c2 stabilized diagnostic");', 'startButton.setText("Start P1d IME submit proof");', 1)
activity = activity.replace('NativeAdapterProofStore.markWaitingAccessibilityDump(this);', 'NativeAdapterProofStore.markWaitingImeSubmit(this);', 1)
activity = activity.replace(
    'String prompt = "Native adapter P1c2 stabilized read-only diagnostic. Reply with exactly this marker and no other text: " + marker;',
    'String prompt = "Native adapter P1d IME submit proof. Reply with exactly this marker and no other text: " + marker;',
    1,
)
activity = activity.replace(
    '        // P1c is read-only: the Accessibility service snapshots the composer tree\n        // after the marker appears, then returns this companion to foreground.\n',
    '        // P1d leaves ChatGPT foreground. After a bounded stabilization window,\n        // Accessibility may invoke only ACTION_IME_ENTER on the exact editable marker node.\n',
    1,
)

old_status = '''        String accessibilityDump = NativeAdapterProofStore.accessibilityDump(this);\n        if (NativeAdapterProofStore.ACCESSIBILITY_DUMP_CAPTURED.equals(state)) {\n            b.append("\\nPASS: read-only composer Accessibility snapshot captured.\\n\\n");\n            b.append(accessibilityDump);\n        } else if (NativeAdapterProofStore.WAITING_ACCESSIBILITY_DUMP.equals(state)) {\n            b.append("\\nWaiting for the marker, then a 4-second composer stabilization window. No ChatGPT action will be invoked.\\n");\n        }\n'''
new_status = '''        String semanticSendNode = NativeAdapterProofStore.semanticSendNode(this);\n        if (!semanticSendNode.isEmpty()) b.append("IME target = ").append(semanticSendNode).append('\\n');\n        if (NativeAdapterProofStore.SEND_CONFIRMED.equals(state)) {\n            b.append("\\nPASS: ACTION_IME_ENTER was accepted and the marker left the editable composer and appeared as a non-editable native chat message.\\n");\n        } else if (NativeAdapterProofStore.SEND_DISPATCHED.equals(state)) {\n            b.append("\\nACTION_IME_ENTER was accepted. Waiting for read-only confirmation that the marker became a sent message.\\n");\n        } else if (NativeAdapterProofStore.WAITING_SEMANTIC_SEND.equals(state)) {\n            b.append("\\nWaiting for the editable marker, then a 4-second stabilization window and exact ACTION_IME_ENTER availability. No fallback action exists.\\n");\n        }\n'''
if old_status not in activity:
    raise SystemExit("P1d P1c2 status block missing")
activity = activity.replace(old_status, new_status, 1)
activity_path.write_text(activity)

# ---- accessibility service ---------------------------------------------
service = service_path.read_text()
service = service.replace(
    '''            if (NativeAdapterProofStore.isAwaitingAccessibilityDump(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterP1cAccessibilityDump(null);\n            }\n''',
    '''            if (NativeAdapterProofStore.isSemanticSendHot(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterP1dImeSubmit(null);\n            }\n''',
    1,
)
service = service.replace(
    '''                    NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this) ||\n                    NativeAdapterProofStore.isAwaitingAccessibilityDump(NativeProbeAccessibilityService.this);\n''',
    '''                    NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this) ||\n                    NativeAdapterProofStore.isSemanticSendHot(NativeProbeAccessibilityService.this);\n''',
    1,
)
service = service.replace(
    '''        // NATIVE_ADAPTER_P1C2_STABILIZED_READ_ONLY_ACCESSIBILITY_DUMP\n        observeNativeAdapterP1cAccessibilityDump(event);\n''',
    '''        // NATIVE_ADAPTER_P1D_BOUNDED_IME_SUBMIT\n        observeNativeAdapterP1dImeSubmit(event);\n''',
    1,
)

insert_anchor = '    private static final long P1C2_STABILIZATION_MS = 4000L;\n'
if insert_anchor not in service:
    raise SystemExit("P1d P1c2 service anchor missing")

p1d_methods = r'''    private static final long P1D_STABILIZATION_MS = 4000L;
    private static final long P1D_CONFIRM_TIMEOUT_MS = 15000L;

    private void observeNativeAdapterP1dImeSubmit(AccessibilityEvent event) {
        if (!NativeAdapterProofStore.isSemanticSendHot(this)) return;
        if (event != null) {
            CharSequence pkg = event.getPackageName();
            if (pkg != null && !ProbeState.TARGET.equals(pkg.toString())) return;
        }
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (!ProbeState.TARGET.equals(packageOf(root))) return;
        String marker = NativeAdapterProofStore.marker(this);
        if (marker == null || marker.isEmpty()) return;

        if (NativeAdapterProofStore.isAwaitingSemanticSend(this)) {
            AccessibilityNodeInfo editable = findEditableMarkerNode(root, marker, 800);
            if (editable == null) return;

            long firstSeenAt = NativeAdapterProofStore.noteP1cMarkerObservation(this);
            long settledFor = Math.max(0L, System.currentTimeMillis() - firstSeenAt);
            if (settledFor < P1D_STABILIZATION_MS) return;

            // Re-read from scratch after stabilization so the action set cannot be stale.
            root = getRootInActiveWindow();
            if (!ProbeState.TARGET.equals(packageOf(root))) return;
            editable = findEditableMarkerNode(root, marker, 800);
            if (editable == null) return;

            boolean hasImeEnter = false;
            for (AccessibilityNodeInfo.AccessibilityAction action : editable.getActionList()) {
                if (action != null && action.getId() == AccessibilityNodeInfo.AccessibilityAction.ACTION_IME_ENTER.getId()) {
                    hasImeEnter = true;
                    break;
                }
            }
            if (!editable.isEditable() || !editable.isEnabled() || !editable.isVisibleToUser() || !hasImeEnter) {
                NativeAdapterProofStore.fail(this,
                        "Stabilized editable marker node did not satisfy the exact P1d IME gate: editable/enabled/visible + ACTION_IME_ENTER. No fallback action was attempted.");
                ProbeState.log(this, "NATIVE_ADAPTER_P1D FAIL-CLOSED: stabilized marker node missing exact IME gate.");
                returnToP1dProofApp();
                return;
            }

            String summary = "class=" + editable.getClassName() +
                    "; editable=" + editable.isEditable() +
                    "; enabled=" + editable.isEnabled() +
                    "; visible=" + editable.isVisibleToUser() +
                    "; action=ACTION_IME_ENTER";

            // Durable claim BEFORE the one write-side action. Never blindly replay.
            NativeAdapterProofStore.markSemanticSendDispatched(this, summary);
            boolean accepted = editable.performAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_IME_ENTER.getId());
            ProbeState.log(this, "NATIVE_ADAPTER_P1D IME SUBMIT: " + summary + "; accepted=" + accepted + ".");
            if (!accepted) {
                NativeAdapterProofStore.fail(this,
                        "Exact stabilized ACTION_IME_ENTER was present but performAction returned false. No fallback action was attempted.");
                returnToP1dProofApp();
            }
            return;
        }

        if (!NativeAdapterProofStore.isSemanticSendDispatched(this)) return;

        boolean editableMarker = false;
        boolean nonEditableMarker = false;
        ArrayList<AccessibilityNodeInfo> queue = new ArrayList<>();
        queue.add(root);
        for (int i = 0; i < queue.size() && i < 800; i++) {
            AccessibilityNodeInfo n = queue.get(i);
            if (n == null) continue;
            CharSequence text = n.getText();
            CharSequence desc = n.getContentDescription();
            boolean contains = (text != null && text.toString().contains(marker)) ||
                    (desc != null && desc.toString().contains(marker));
            if (contains) {
                if (n.isEditable()) editableMarker = true;
                else nonEditableMarker = true;
            }
            int children = n.getChildCount();
            for (int c = 0; c < children && queue.size() < 800; c++) {
                AccessibilityNodeInfo child = n.getChild(c);
                if (child != null) queue.add(child);
            }
        }

        if (!editableMarker && nonEditableMarker) {
            NativeAdapterProofStore.markSemanticSendConfirmed(this);
            ProbeState.log(this, "NATIVE_ADAPTER_P1D SEND CONFIRMED read-only: marker became a non-editable native chat message.");
            returnToP1dProofApp();
            return;
        }

        if (System.currentTimeMillis() - NativeAdapterProofStore.startedAt(this) > P1D_CONFIRM_TIMEOUT_MS) {
            NativeAdapterProofStore.fail(this,
                    "ACTION_IME_ENTER was dispatched but the marker was not confirmed as a sent non-editable native message within the bounded verification window. No retry/fallback was attempted.");
            ProbeState.log(this, "NATIVE_ADAPTER_P1D FAIL-CLOSED: IME action unconfirmed within bounded window; editableMarker=" + editableMarker + "; nonEditableMarker=" + nonEditableMarker + ".");
            returnToP1dProofApp();
        }
    }

    private void returnToP1dProofApp() {
        try {
            Intent back = new Intent(this, NativeAdapterProofActivity.class);
            back.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(back);
        } catch (Exception e) {
            ProbeState.log(this, "NATIVE_ADAPTER_P1D result ready; automatic return blocked: " + e.getClass().getSimpleName());
        }
    }

'''
service = service.replace(insert_anchor, p1d_methods + insert_anchor, 1)
service_path.write_text(service)

# ---- version -------------------------------------------------------------
g = gradle_path.read_text()
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 37', g, count=1)
g, n2 = re.subn(r'versionName\s+["\'][^"\']+["\']', 'versionName "0.37-native-adapter-p1d-ime-submit"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("Could not update P1d version metadata")
gradle_path.write_text(g)

# Build-time assertions: one bounded semantic IME write, no geometry/UI guessing.
activity = activity_path.read_text()
service = service_path.read_text()
a = service.index('    private static final long P1D_STABILIZATION_MS')
b = service.index('    private static final long P1C2_STABILIZATION_MS', a)
p1d = service[a:b]
assert 'P1D_STABILIZATION_MS = 4000L' in p1d
assert 'ACTION_IME_ENTER' in p1d
assert 'markSemanticSendDispatched' in p1d
assert 'performAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_IME_ENTER.getId())' in p1d
assert 'ACTION_CLICK' not in p1d
assert 'dispatchGesture' not in p1d
assert 'GLOBAL_ACTION' not in p1d
assert 'bounds' not in p1d.lower()
assert 'Start P1d IME submit proof' in activity
assert 'markWaitingImeSubmit' in activity
assert 'versionCode 37' in g
assert 'versionName "0.37-native-adapter-p1d-ime-submit"' in g
