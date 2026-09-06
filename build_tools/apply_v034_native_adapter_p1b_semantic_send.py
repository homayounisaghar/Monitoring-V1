import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
java_dir = root / "app/src/main/java/com/pebblebridge/poc"
activity_path = java_dir / "NativeAdapterProofActivity.java"
store_path = java_dir / "NativeAdapterProofStore.java"
service_path = java_dir / "NativeProbeAccessibilityService.java"
gradle_path = root / "app/build.gradle"

# P1b deliberately abandons external autosend for logged-in sessions.
# The deep link is used only to open a new native chat and populate the draft.
# Submission is one strict APK-derived semantic Accessibility ACTION_CLICK on
# the exact "Send message" node, with no coordinates, gestures, or ancestor guessing.

# ---- proof store ---------------------------------------------------------
store = store_path.read_text()
store = store.replace(
    '    public static final String FAILED = "FAILED";\n',
    '    public static final String FAILED = "FAILED";\n'
    '    public static final String WAITING_SEMANTIC_SEND = "WAITING_SEMANTIC_SEND";\n'
    '    public static final String SEND_DISPATCHED = "SEND_DISPATCHED";\n'
    '    public static final String SEND_CONFIRMED = "SEND_CONFIRMED";\n',
    1,
)
anchor = '    public static boolean isAwaitingNotification(Context c) {\n        return WAITING_NOTIFICATION.equals(state(c));\n    }\n\n'
if anchor not in store:
    raise SystemExit("P1b store anchor missing")
store = store.replace(
    anchor,
    anchor + '''    public static void markWaitingSemanticSend(Context c) {\n        p(c).edit()\n                .putString("state", WAITING_SEMANTIC_SEND)\n                .putBoolean("semanticSendDispatched", false)\n                .putBoolean("semanticSendConfirmed", false)\n                .putString("semanticSendNode", "")\n                .apply();\n    }\n\n    public static boolean isAwaitingSemanticSend(Context c) {\n        return WAITING_SEMANTIC_SEND.equals(state(c));\n    }\n\n    public static boolean isSemanticSendDispatched(Context c) {\n        return SEND_DISPATCHED.equals(state(c));\n    }\n\n    public static boolean isSemanticSendHot(Context c) {\n        String s = state(c);\n        return WAITING_SEMANTIC_SEND.equals(s) || SEND_DISPATCHED.equals(s);\n    }\n\n    public static void markSemanticSendDispatched(Context c, String node) {\n        p(c).edit()\n                .putString("semanticSendNode", node == null ? "" : node)\n                .putBoolean("semanticSendDispatched", true)\n                .putString("state", SEND_DISPATCHED)\n                .apply();\n    }\n\n    public static void markSemanticSendConfirmed(Context c) {\n        p(c).edit()\n                .putBoolean("semanticSendConfirmed", true)\n                .putString("state", SEND_CONFIRMED)\n                .apply();\n    }\n\n    public static String semanticSendNode(Context c) {\n        return p(c).getString("semanticSendNode", "");\n    }\n\n    public static boolean semanticSendConfirmed(Context c) {\n        return p(c).getBoolean("semanticSendConfirmed", false);\n    }\n\n''',
    1,
)
store_path.write_text(store)

# ---- proof activity ------------------------------------------------------
s = activity_path.read_text()
s = s.replace('title.setText("Native Chat Adapter P1a");', 'title.setText("Native Chat Adapter P1b");', 1)
s = s.replace(
    'subtitle.setText("Autosend-isolation proof. ChatGPT is opened by the APK-derived deep link and is NOT forced back to this app. Stay in ChatGPT long enough to see whether the draft actually sends, then return here manually.");',
    'subtitle.setText("Strict semantic Send proof. Deep link opens a new native chat and sets the draft; Accessibility may click ONLY the exact APK-derived semantic Send message node after the unique marker is visible in the editable composer. No coordinates, gesture taps, Search, or ancestor guessing.");',
    1,
)
s = s.replace('startButton.setText("Start P1a autosend proof");', 'startButton.setText("Start P1b semantic Send proof");', 1)

# Notification access is not a prerequisite for this isolated submit proof.
notification_gate = '''        if (!hasNotificationAccess()) {\n            NativeAdapterProofStore.fail(this, "Notification access is not enabled. Grant it, return here, reset, and start again.");\n            refreshUi();\n            return;\n        }\n'''
if notification_gate not in s:
    raise SystemExit("P1b notification prerequisite block missing")
s = s.replace(notification_gate, '', 1)

s = s.replace(
    'String marker = NativeAdapterProofStore.start(this);\n        String prompt = "Native adapter P1a autosend proof. Reply with exactly this marker and no other text: " + marker;',
    'String marker = NativeAdapterProofStore.start(this);\n        NativeAdapterProofStore.markWaitingSemanticSend(this);\n        String prompt = "Native adapter P1b semantic Send proof. Reply with exactly this marker and no other text: " + marker;',
    1,
)
s = s.replace('                .appendQueryParameter("autosend", "true")\n', '', 1)
s = s.replace(
    'NativeAdapterProofStore.fail(this, "Could not launch the official ChatGPT deeplink activity for new-chat autosend.");',
    'NativeAdapterProofStore.fail(this, "Could not launch the official ChatGPT deeplink activity for new-chat draft injection.");',
    1,
)
s = s.replace(
    '        // P1a intentionally leaves ChatGPT in the foreground. Do not interrupt\n        // the app while its own deep-link autosend pipeline decides whether to submit.\n        // The user returns to this companion manually after observing the result.\n',
    '        // P1b leaves ChatGPT foreground. The Accessibility service observes the\n        // exact editable marker and may invoke only the exact semantic Send message node.\n        // The user returns manually after observing whether submission occurred.\n',
    1,
)

# Extend status without disturbing later conversation-id proof fields.
status_anchor = '        if (started > 0) b.append("age = ").append(age).append(" s\\n");\n'
if status_anchor not in s:
    raise SystemExit("P1b status anchor missing")
s = s.replace(
    status_anchor,
    status_anchor + '''        String semanticSendNode = NativeAdapterProofStore.semanticSendNode(this);\n        if (!semanticSendNode.isEmpty()) b.append("semantic Send node = ").append(semanticSendNode).append('\\n');\n        if (NativeAdapterProofStore.SEND_CONFIRMED.equals(state)) {\n            b.append("\\nPASS: marker left the editable composer and appeared as a non-editable native chat message after the strict semantic Send action.\\n");\n        } else if (NativeAdapterProofStore.SEND_DISPATCHED.equals(state)) {\n            b.append("\\nSemantic Send ACTION_CLICK was accepted. Waiting for read-only confirmation that the marker became a sent message.\\n");\n        } else if (NativeAdapterProofStore.WAITING_SEMANTIC_SEND.equals(state)) {\n            b.append("\\nWaiting for the injected marker plus the exact semantic Send message control. No coordinate fallback exists.\\n");\n        }\n''',
    1,
)
activity_path.write_text(s)

# ---- Accessibility strict semantic submit -------------------------------
service = service_path.read_text()
old_watchdog = '''        @Override public void run() {\n            if (NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterProof(null);\n            }\n            if (isActiveProbe()) processTargetWindow("watchdog");\n            boolean hot = isActiveProbe() || NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this);\n            handler.postDelayed(this, hot ? 300 : 900);\n        }\n'''
new_watchdog = '''        @Override public void run() {\n            if (NativeAdapterProofStore.isSemanticSendHot(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterSemanticSend(null);\n            }\n            if (NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterProof(null);\n            }\n            if (isActiveProbe()) processTargetWindow("watchdog");\n            boolean hot = isActiveProbe() ||\n                    NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this) ||\n                    NativeAdapterProofStore.isSemanticSendHot(NativeProbeAccessibilityService.this);\n            handler.postDelayed(this, hot ? 250 : 900);\n        }\n'''
if old_watchdog not in service:
    raise SystemExit("P1b watchdog block missing")
service = service.replace(old_watchdog, new_watchdog, 1)

old_event = '''        // NATIVE_ADAPTER_P1_READ_ONLY_RECEIPT_OBSERVER\n        observeNativeAdapterProof(event);\n'''
new_event = '''        // NATIVE_ADAPTER_P1B_STRICT_SEMANTIC_SEND\n        observeNativeAdapterSemanticSend(event);\n        // NATIVE_ADAPTER_P1_READ_ONLY_RECEIPT_OBSERVER\n        observeNativeAdapterProof(event);\n'''
if old_event not in service:
    raise SystemExit("P1b event observer anchor missing")
service = service.replace(old_event, new_event, 1)

insert_anchor = '    private void observeNativeAdapterProof(AccessibilityEvent event) {\n'
if insert_anchor not in service:
    raise SystemExit("P1b native proof observer anchor missing")
semantic_methods = r'''    private void observeNativeAdapterSemanticSend(AccessibilityEvent event) {
        if (!NativeAdapterProofStore.isSemanticSendHot(this)) return;
        if (event != null) {
            CharSequence pkg = event.getPackageName();
            if (pkg != null && !ProbeState.TARGET.equals(pkg.toString())) return;
        }
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (!ProbeState.TARGET.equals(packageOf(root))) return;
        String marker = NativeAdapterProofStore.marker(this);
        if (marker == null || marker.isEmpty()) return;

        boolean editableMarker = false;
        boolean nonEditableMarker = false;
        AccessibilityNodeInfo exactSend = null;
        String exactSendSummary = "";
        ArrayList<AccessibilityNodeInfo> queue = new ArrayList<>();
        queue.add(root);
        for (int i = 0; i < queue.size() && i < 700; i++) {
            AccessibilityNodeInfo n = queue.get(i);
            if (n == null) continue;
            CharSequence textCs = n.getText();
            CharSequence descCs = n.getContentDescription();
            String text = textCs == null ? "" : textCs.toString();
            String desc = descCs == null ? "" : descCs.toString();
            String id = n.getViewIdResourceName() == null ? "" : n.getViewIdResourceName();

            boolean hasMarker = text.contains(marker) || desc.contains(marker);
            if (hasMarker) {
                if (n.isEditable()) editableMarker = true;
                else nonEditableMarker = true;
            }

            if (exactSend == null && isExactNativeSemanticSendNode(n, text, desc, id)) {
                exactSend = n;
                exactSendSummary = "text=" + text + "; desc=" + desc + "; id=" + id +
                        "; clickable=" + n.isClickable();
            }

            int children = n.getChildCount();
            for (int c = 0; c < children && queue.size() < 700; c++) {
                AccessibilityNodeInfo child = n.getChild(c);
                if (child != null) queue.add(child);
            }
        }

        if (NativeAdapterProofStore.isAwaitingSemanticSend(this)) {
            if (!editableMarker) return;
            if (exactSend == null) {
                if (System.currentTimeMillis() - NativeAdapterProofStore.startedAt(this) > 8000L) {
                    NativeAdapterProofStore.fail(this,
                            "Injected marker is visible in the editable ChatGPT composer, but the exact semantic Send message ACTION_CLICK node was not exposed. P1b refuses coordinate/ancestor fallback.");
                    ProbeState.log(this, "NATIVE_ADAPTER_P1B FAIL-CLOSED: editable marker found but exact semantic Send message node absent.");
                }
                return;
            }

            // Durable claim before the one write-side action: never blindly replay.
            NativeAdapterProofStore.markSemanticSendDispatched(this, exactSendSummary);
            boolean clicked = exactSend.performAction(AccessibilityNodeInfo.ACTION_CLICK);
            ProbeState.log(this, "NATIVE_ADAPTER_P1B SEMANTIC SEND: " + exactSendSummary + "; ACTION_CLICK=" + clicked + ".");
            if (!clicked) {
                NativeAdapterProofStore.fail(this,
                        "Exact semantic Send message node was found, but ACTION_CLICK returned false. No fallback action was attempted.");
            }
            return;
        }

        if (NativeAdapterProofStore.isSemanticSendDispatched(this)) {
            if (!editableMarker && nonEditableMarker) {
                NativeAdapterProofStore.markSemanticSendConfirmed(this);
                ProbeState.log(this, "NATIVE_ADAPTER_P1B SEND CONFIRMED read-only: marker left editable composer and is present in a non-editable native chat node.");
            }
        }
    }

    private boolean isExactNativeSemanticSendNode(AccessibilityNodeInfo n, String text, String desc, String id) {
        if (n == null) return false;
        String t = text == null ? "" : text.trim().toLowerCase(Locale.US);
        String d = desc == null ? "" : desc.trim().toLowerCase(Locale.US);
        String v = id == null ? "" : id.trim().toLowerCase(Locale.US);
        boolean exactLabel = "send message".equals(t) || "send message".equals(d);
        boolean composerSemantic = v.contains("chatgpt.composer") && (t.contains("send") || d.contains("send"));
        if (!(exactLabel || composerSemantic)) return false;
        if (!n.isEnabled() || !n.isVisibleToUser()) return false;
        if (!n.isClickable()) return false;
        for (AccessibilityNodeInfo.AccessibilityAction a : n.getActionList()) {
            if (a != null && a.getId() == AccessibilityNodeInfo.ACTION_CLICK) return true;
        }
        return false;
    }

'''
service = service.replace(insert_anchor, semantic_methods + insert_anchor, 1)
service_path.write_text(service)

# ---- version -------------------------------------------------------------
g = gradle_path.read_text()
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 34', g, count=1)
g, n2 = re.subn(r'versionName\s+["\'][^"\']+["\']', 'versionName "0.34-native-adapter-p1b"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("Could not update P1b version metadata")
gradle_path.write_text(g)

# Build-time safety assertions.
activity = activity_path.read_text()
service = service_path.read_text()
assert 'appendQueryParameter("autosend"' not in activity
assert 'Start P1b semantic Send proof' in activity
assert 'NATIVE_ADAPTER_P1B_STRICT_SEMANTIC_SEND' in service
assert '"send message".equals' in service
assert 'ACTION_CLICK' in service
assert 'dispatchGesture' not in semantic_methods
assert 'bounds' not in semantic_methods.lower()
assert 'GLOBAL_ACTION' not in semantic_methods
assert 'versionCode 34' in g
assert 'versionName "0.34-native-adapter-p1b"' in g
