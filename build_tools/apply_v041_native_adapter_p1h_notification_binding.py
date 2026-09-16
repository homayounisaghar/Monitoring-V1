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

# P1h closes the remaining conversationId binding loop by connecting the already
# proven P1g semantic Send to the NotificationListener/read-only verification
# machinery that existed in the original P1 harness but could not work while
# logged-in external autosend was rejected.
#
# Flow:
#   new-chat + injected marker draft
#   -> one P1g semantic-parent ACTION_CLICK after durable claim
#   -> editable marker becomes non-editable (Send confirmed)
#   -> state becomes WAITING_NOTIFICATION and Probe returns foreground
#   -> normal background ChatGPT response notification
#   -> StatusBarNotification.tag candidate
#   -> explicit /c/<candidate>
#   -> read-only unique marker verification
#   -> VERIFIED

# ---- store: preserve Send proof while arming the existing notification binder
store = store_path.read_text()
old_confirm = '''    public static void markSemanticParentSendConfirmed(Context c) {\n        p(c).edit().putString("state", SEMANTIC_PARENT_SEND_CONFIRMED).apply();\n    }\n'''
new_confirm = '''    public static void markSemanticParentSendConfirmed(Context c) {\n        // P1h: Send is already confirmed by the editable -> non-editable transition.\n        // Preserve that fact durably, then arm the original P1 notification binder.\n        p(c).edit()\n                .putBoolean("semanticSendConfirmed", true)\n                .putLong("notificationBindArmedAt", System.currentTimeMillis())\n                .putString("candidateConversationId", "")\n                .putString("lastNotificationTag", "")\n                .putString("lastNotificationText", "")\n                .putString("state", WAITING_NOTIFICATION)\n                .apply();\n    }\n\n    public static boolean semanticSendConfirmed(Context c) {\n        return p(c).getBoolean("semanticSendConfirmed", false);\n    }\n\n    public static long notificationBindArmedAt(Context c) {\n        return p(c).getLong("notificationBindArmedAt", 0L);\n    }\n'''
if old_confirm not in store:
    raise SystemExit("P1h semantic confirmation anchor missing")
store = store.replace(old_confirm, new_confirm, 1)
store_path.write_text(store)

# ---- activity: exact-build gate + binding-specific naming/status ---------
activity = activity_path.read_text()
if 'import android.content.pm.PackageInfo;\n' not in activity:
    activity = activity.replace(
        'import android.content.Intent;\n',
        'import android.content.Intent;\nimport android.content.pm.PackageInfo;\n',
        1,
    )

start_anchor = '    private void startProof() {\n'
if start_anchor not in activity:
    raise SystemExit("P1h startProof anchor missing")
exact_gate = r'''    private boolean hasExactChatGptBuild() {
        try {
            PackageInfo info = getPackageManager().getPackageInfo(CHATGPT_PACKAGE, 0);
            return info.versionName != null && "1.2026.237".equals(info.versionName);
        } catch (Throwable t) {
            return false;
        }
    }

'''
activity = activity.replace(start_anchor, exact_gate + start_anchor, 1)
activity = activity.replace(
    start_anchor,
    start_anchor + '''        if (!hasExactChatGptBuild()) {\n            NativeAdapterProofStore.fail(this, "Fail closed: P1h requires installed ChatGPT versionName exactly 1.2026.237.");\n            refreshUi();\n            return;\n        }\n''',
    1,
)

activity = activity.replace('title.setText("Native Chat Adapter P1g");', 'title.setText("Native Chat Adapter P1h");', 1)
activity = activity.replace(
    'subtitle.setText("Bounded semantic-parent Send proof selected from the P1f real-device trace. P1g opens the proven native draft route, finds exactly one Send Message semantic leaf inside the marker composer, requires its DIRECT parent to be enabled/visible/clickable with ACTION_CLICK, durably claims the write, clicks once, then verifies the marker became a sent native message. No coordinates, gestures, Search, retries, or fallback writes.");',
    'subtitle.setText("ConversationId binding proof. P1h uses the proven P1g semantic Send, returns this probe to foreground after confirmed submission so ChatGPT can emit its normal background response notification, captures the notification conversationId candidate, reopens /c/<id>, and verifies the unique marker read-only. Notification Access and Accessibility must both be enabled.");',
    1,
)
activity = activity.replace('startButton.setText("Start P1g semantic-parent Send proof");', 'startButton.setText("Start P1h conversationId binding proof");', 1)
activity = activity.replace(
    'String prompt = "Native adapter P1g semantic-parent Send proof. Reply with exactly this marker and no other text: " + marker;',
    'String prompt = "Native adapter P1h conversation binding proof. Reply with exactly this marker and no other text: " + marker;',
    1,
)

p1g_status = '''        if (NativeAdapterProofStore.WAITING_SEMANTIC_PARENT_SEND.equals(state)) {\n            b.append("\\nP1g ARMED: waiting for the editable marker and exactly one P1f-proven Send Message -> direct clickable-parent target. No fallback exists.\\n");\n        } else if (NativeAdapterProofStore.SEMANTIC_PARENT_SEND_CLAIMED.equals(state)) {\n            b.append("\\nP1g CLAIMED: the one allowed ACTION_CLICK was attempted. P1g will NOT retry; waiting only for read-only sent-message verification.\\n");\n        } else if (NativeAdapterProofStore.SEMANTIC_PARENT_SEND_CONFIRMED.equals(state)) {\n            b.append("\\nPASS: P1g semantic-parent ACTION_CLICK sent the marker and the editable -> non-editable transition was verified.\\n");\n        }\n'''
p1h_status = '''        if (NativeAdapterProofStore.WAITING_SEMANTIC_PARENT_SEND.equals(state)) {\n            b.append("\\nP1h SEND ARMED: waiting for the exact P1g semantic-parent target. No fallback exists.\\n");\n        } else if (NativeAdapterProofStore.SEMANTIC_PARENT_SEND_CLAIMED.equals(state)) {\n            b.append("\\nP1h SEND CLAIMED: the sole allowed ACTION_CLICK was attempted. It will not be replayed.\\n");\n        } else if (NativeAdapterProofStore.WAITING_NOTIFICATION.equals(state) && NativeAdapterProofStore.semanticSendConfirmed(this)) {\n            b.append("\\nP1h SEND CONFIRMED. ChatGPT is backgrounded; waiting for its normal response notification to expose a conversationId candidate.\\n");\n        } else if (NativeAdapterProofStore.CANDIDATE_CAPTURED.equals(state)) {\n            b.append("\\nP1h CANDIDATE CAPTURED. Reopening /c/<candidate> for marker verification.\\n");\n        } else if (NativeAdapterProofStore.VERIFYING.equals(state)) {\n            b.append("\\nP1h VERIFYING: candidate thread reopened; waiting only for read-side marker verification.\\n");\n        } else if (NativeAdapterProofStore.VERIFIED.equals(state)) {\n            b.append("\\nPASS: deterministic conversationId binding verified by direct /c/<id> reopen plus unique marker observation.\\n");\n        }\n'''
if p1g_status not in activity:
    raise SystemExit("P1h P1g status block missing")
activity = activity.replace(p1g_status, p1h_status, 1)

activity = activity.replace('Native Chat Adapter P1g - semantic-parent Send proof export', 'Native Chat Adapter P1h - conversationId binding proof export')
activity = activity.replace('adapterVersion: 0.40-native-adapter-p1g-semantic-parent-send', 'adapterVersion: 0.41-native-adapter-p1h-notification-binding')
activity = activity.replace('native-chat-adapter-p1g-', 'native-chat-adapter-p1h-')
activity_path.write_text(activity)

# ---- service: keep the exact P1g write primitive, update audit wording ---
service = service_path.read_text()
service = service.replace('NATIVE_ADAPTER_P1G_BOUNDED_SEMANTIC_PARENT_SEND', 'NATIVE_ADAPTER_P1H_BINDING_SEND', 1)
service = service.replace(
    'ProbeState.log(this, "NATIVE_ADAPTER_P1G SEND CONFIRMED read-only after one claimed ACTION_CLICK.");',
    'ProbeState.log(this, "NATIVE_ADAPTER_P1H SEND CONFIRMED; notification conversationId binding is now armed.");',
    1,
)
service_path.write_text(service)

# ---- listener: retain original capture path, but document the P1h gate ---
listener = listener_path.read_text()
listener = listener.replace(
    'public class NativeAdapterNotificationListenerService extends NotificationListenerService {',
    'public class NativeAdapterNotificationListenerService extends NotificationListenerService {\n    // P1h consumes this only after P1g Send confirmation transitions state to WAITING_NOTIFICATION.',
    1,
)
listener_path.write_text(listener)

# ---- visible naming ------------------------------------------------------
ANDROID_NS = 'http://schemas.android.com/apk/res/android'
ET.register_namespace('android', ANDROID_NS)
tree = ET.parse(manifest_path)
manifest = tree.getroot()
app = manifest.find('application')
if app is None:
    raise SystemExit("P1h manifest application missing")
label_key = '{%s}label' % ANDROID_NS
name_key = '{%s}name' % ANDROID_NS
app.set(label_key, 'Native Chat Adapter P1h')
for node in list(app):
    name = node.get(name_key, '')
    if name.endswith('NativeAdapterProofActivity') or name.endswith('NativeProbeAccessibilityService') or name.endswith('NativeAdapterNotificationListenerService'):
        node.set(label_key, 'Native Chat Adapter P1h')
tree.write(manifest_path, encoding='utf-8', xml_declaration=True)

# ---- version -------------------------------------------------------------
g = gradle_path.read_text()
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 41', g, count=1)
g, n2 = re.subn(r'versionName\s+["\'][^"\']+["\']', 'versionName "0.41-native-adapter-p1h-notification-binding"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("Could not update P1h version metadata")
gradle_path.write_text(g)

# ---- build-time invariants ----------------------------------------------
activity = activity_path.read_text()
store = store_path.read_text()
service = service_path.read_text()
listener = listener_path.read_text()

assert 'hasExactChatGptBuild' in activity
assert '1.2026.237' in activity
assert 'Start P1h conversationId binding proof' in activity
assert 'semanticSendConfirmed' in store
assert '.putString("state", WAITING_NOTIFICATION)' in store
assert 'getTag()' in listener
assert 'captureCandidate' in listener
assert 'NATIVE_ADAPTER_P1H_BINDING_SEND' in service
assert 'Native Chat Adapter P1h' in manifest_path.read_text()
assert 'versionCode 41' in g
assert 'versionName "0.41-native-adapter-p1h-notification-binding"' in g

# The P1h Send primitive must remain exactly the proven P1g bounded write:
a = service.index('    private void observeNativeAdapterP1gSemanticParentSend')
b = service.index('    private void observeNativeAdapterP1eManualSendTrace', a)
proof = service[a:b]
if proof.count('performAction(AccessibilityNodeInfo.ACTION_CLICK)') != 1:
    raise SystemExit('P1h must retain exactly one allowed semantic-parent ACTION_CLICK')
for forbidden in ('dispatchGesture', 'performGlobalAction', 'GLOBAL_ACTION_', 'getBoundsInScreen'):
    if forbidden in proof:
        raise SystemExit('P1h contains forbidden fallback primitive: ' + forbidden)
