import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
java_dir = root / "app/src/main/java/com/pebblebridge/poc"
manifest_path = root / "app/src/main/AndroidManifest.xml"
gradle_path = root / "app/build.gradle"
service_path = java_dir / "NativeProbeAccessibilityService.java"

java_dir.mkdir(parents=True, exist_ok=True)

store_java = r'''package com.pebblebridge.poc;

import android.content.Context;
import android.content.SharedPreferences;

import java.util.Locale;
import java.util.UUID;

public final class NativeAdapterProofStore {
    private static final String PREFS = "native_adapter_p1";

    public static final String IDLE = "IDLE";
    public static final String WAITING_NOTIFICATION = "WAITING_NOTIFICATION";
    public static final String CANDIDATE_CAPTURED = "CANDIDATE_CAPTURED";
    public static final String VERIFYING = "VERIFYING";
    public static final String VERIFIED = "VERIFIED";
    public static final String FAILED = "FAILED";

    private NativeAdapterProofStore() {}

    private static SharedPreferences p(Context c) {
        return c.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    public static void reset(Context c) {
        p(c).edit().clear().putString("state", IDLE).apply();
    }

    public static String start(Context c) {
        String marker = "PB_NATIVE_P1_" + UUID.randomUUID().toString().replace("-", "").substring(0, 16).toUpperCase(Locale.US);
        p(c).edit()
                .clear()
                .putString("state", WAITING_NOTIFICATION)
                .putString("marker", marker)
                .putLong("startedAt", System.currentTimeMillis())
                .putString("candidateConversationId", "")
                .putString("lastNotificationTag", "")
                .putString("lastNotificationText", "")
                .putBoolean("candidateOpened", false)
                .putBoolean("verified", false)
                .putString("failure", "")
                .apply();
        return marker;
    }

    public static String state(Context c) { return p(c).getString("state", IDLE); }
    public static String marker(Context c) { return p(c).getString("marker", ""); }
    public static long startedAt(Context c) { return p(c).getLong("startedAt", 0L); }
    public static String candidate(Context c) { return p(c).getString("candidateConversationId", ""); }
    public static String lastNotificationTag(Context c) { return p(c).getString("lastNotificationTag", ""); }
    public static String lastNotificationText(Context c) { return p(c).getString("lastNotificationText", ""); }
    public static String failure(Context c) { return p(c).getString("failure", ""); }
    public static boolean verified(Context c) { return p(c).getBoolean("verified", false); }
    public static boolean candidateOpened(Context c) { return p(c).getBoolean("candidateOpened", false); }

    public static boolean isPending(Context c) {
        String s = state(c);
        return WAITING_NOTIFICATION.equals(s) || CANDIDATE_CAPTURED.equals(s) || VERIFYING.equals(s);
    }

    public static boolean isAwaitingNotification(Context c) {
        return WAITING_NOTIFICATION.equals(state(c));
    }

    public static boolean isAwaitingReceipt(Context c) {
        return VERIFYING.equals(state(c));
    }

    public static void recordNotification(Context c, String tag, String text) {
        p(c).edit()
                .putString("lastNotificationTag", tag == null ? "" : tag)
                .putString("lastNotificationText", text == null ? "" : text)
                .apply();
    }

    public static void captureCandidate(Context c, String conversationId) {
        p(c).edit()
                .putString("candidateConversationId", conversationId)
                .putString("state", CANDIDATE_CAPTURED)
                .apply();
    }

    public static void markVerifying(Context c) {
        p(c).edit().putBoolean("candidateOpened", true).putString("state", VERIFYING).apply();
    }

    public static void markVerified(Context c) {
        p(c).edit().putBoolean("verified", true).putString("state", VERIFIED).apply();
    }

    public static void fail(Context c, String reason) {
        p(c).edit().putString("failure", reason == null ? "" : reason).putString("state", FAILED).apply();
    }
}
'''

listener_java = r'''package com.pebblebridge.poc;

import android.app.Notification;
import android.os.Bundle;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;

public class NativeAdapterNotificationListenerService extends NotificationListenerService {
    private static final String CHATGPT_PACKAGE = "com.openai.chatgpt";

    @Override public void onNotificationPosted(StatusBarNotification sbn) {
        if (sbn == null || !CHATGPT_PACKAGE.equals(sbn.getPackageName())) return;
        if (!NativeAdapterProofStore.isAwaitingNotification(this)) return;

        long startedAt = NativeAdapterProofStore.startedAt(this);
        if (startedAt <= 0 || sbn.getPostTime() + 1500L < startedAt) return;

        String tag = sbn.getTag();
        String text = notificationText(sbn.getNotification());
        NativeAdapterProofStore.recordNotification(this, tag, text);

        if (!isPlausibleConversationId(tag)) return;
        NativeAdapterProofStore.captureCandidate(this, tag);
    }

    private static String notificationText(Notification n) {
        if (n == null || n.extras == null) return "";
        Bundle e = n.extras;
        CharSequence title = e.getCharSequence(Notification.EXTRA_TITLE);
        CharSequence text = e.getCharSequence(Notification.EXTRA_TEXT);
        CharSequence big = e.getCharSequence(Notification.EXTRA_BIG_TEXT);
        StringBuilder out = new StringBuilder();
        if (title != null) out.append(title);
        if (text != null) out.append(" | ").append(text);
        if (big != null) out.append(" | ").append(big);
        return out.toString();
    }

    private static boolean isPlausibleConversationId(String s) {
        if (s == null) return false;
        String t = s.trim();
        if (t.length() < 16 || t.length() > 96) return false;
        for (int i = 0; i < t.length(); i++) {
            char c = t.charAt(i);
            boolean ok = (c >= '0' && c <= '9') ||
                    (c >= 'a' && c <= 'z') ||
                    (c >= 'A' && c <= 'Z') || c == '-' || c == '_';
            if (!ok) return false;
        }
        return true;
    }
}
'''

activity_java = r'''package com.pebblebridge.poc;

import android.app.Activity;
import android.app.NotificationManager;
import android.content.ComponentName;
import android.content.Intent;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.text.method.ScrollingMovementMethod;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.Set;

public class NativeAdapterProofActivity extends Activity {
    private static final String CHATGPT_PACKAGE = "com.openai.chatgpt";
    private static final String CHATGPT_DEEPLINK_ACTIVITY = "com.openai.chatgpt.ChatGptDeeplinkActivity";
    private static final long RETURN_DELAY_MS = 1800L;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private TextView status;
    private Button startButton;
    private Button openCandidateButton;

    private final Runnable refresh = new Runnable() {
        @Override public void run() {
            refreshUi();
            maybeAdvanceProof();
            handler.postDelayed(this, 350L);
        }
    };

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildUi();
    }

    @Override protected void onResume() {
        super.onResume();
        handler.removeCallbacks(refresh);
        handler.post(refresh);
    }

    @Override protected void onPause() {
        super.onPause();
        handler.removeCallbacks(refresh);
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int pad = dp(18);
        root.setPadding(pad, pad, pad, pad);

        TextView title = new TextView(this);
        title.setText("Native Chat Adapter P1");
        title.setTextSize(24f);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        root.addView(title, new LinearLayout.LayoutParams(-1, -2));

        TextView subtitle = new TextView(this);
        subtitle.setText("APK-derived proof: deep-link autosend -> notification conversationId -> direct /c/<id> -> read-only receipt verification. No Search, coordinate tap, or write-side Accessibility is used.");
        subtitle.setTextSize(15f);
        LinearLayout.LayoutParams subtitleLp = new LinearLayout.LayoutParams(-1, -2);
        subtitleLp.topMargin = dp(8);
        root.addView(subtitle, subtitleLp);

        Button notificationAccess = new Button(this);
        notificationAccess.setText("Grant notification access");
        notificationAccess.setOnClickListener(v -> {
            try {
                startActivity(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));
            } catch (Exception e) {
                startActivity(new Intent("android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS"));
            }
        });
        LinearLayout.LayoutParams buttonLp = new LinearLayout.LayoutParams(-1, -2);
        buttonLp.topMargin = dp(16);
        root.addView(notificationAccess, buttonLp);

        Button accessibility = new Button(this);
        accessibility.setText("Open accessibility settings");
        accessibility.setOnClickListener(v -> startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));
        root.addView(accessibility, new LinearLayout.LayoutParams(-1, -2));

        startButton = new Button(this);
        startButton.setText("Start native adapter proof");
        startButton.setOnClickListener(v -> startProof());
        LinearLayout.LayoutParams startLp = new LinearLayout.LayoutParams(-1, -2);
        startLp.topMargin = dp(12);
        root.addView(startButton, startLp);

        openCandidateButton = new Button(this);
        openCandidateButton.setText("Open captured conversation");
        openCandidateButton.setOnClickListener(v -> openCandidateForVerification());
        root.addView(openCandidateButton, new LinearLayout.LayoutParams(-1, -2));

        Button reset = new Button(this);
        reset.setText("Reset proof state");
        reset.setOnClickListener(v -> {
            NativeAdapterProofStore.reset(this);
            refreshUi();
        });
        root.addView(reset, new LinearLayout.LayoutParams(-1, -2));

        status = new TextView(this);
        status.setTextSize(14f);
        status.setTypeface(Typeface.MONOSPACE);
        status.setTextIsSelectable(true);
        status.setMovementMethod(new ScrollingMovementMethod());
        LinearLayout.LayoutParams statusLp = new LinearLayout.LayoutParams(-1, -2);
        statusLp.topMargin = dp(18);
        root.addView(status, statusLp);

        ScrollView scroll = new ScrollView(this);
        scroll.addView(root);
        setContentView(scroll);
        refreshUi();
    }

    private void startProof() {
        if (!hasNotificationAccess()) {
            NativeAdapterProofStore.fail(this, "Notification access is not enabled. Grant it, return here, reset, and start again.");
            refreshUi();
            return;
        }
        if (!isAccessibilityVerifierEnabled()) {
            NativeAdapterProofStore.fail(this, "The existing Pebble Bridge Accessibility service is not enabled. It is used read-only in this proof to verify the unique assistant marker.");
            refreshUi();
            return;
        }

        String marker = NativeAdapterProofStore.start(this);
        String prompt = "Native adapter proof. Reply with exactly this marker and no other text: " + marker;
        Uri uri = new Uri.Builder()
                .scheme("https")
                .authority("chatgpt.com")
                .appendPath("c")
                .appendQueryParameter("prompt", prompt)
                .appendQueryParameter("autosend", "true")
                .build();

        if (!launchChatGpt(uri)) {
            NativeAdapterProofStore.fail(this, "Could not launch the official ChatGPT deeplink activity for new-chat autosend.");
            refreshUi();
            return;
        }

        // Move ChatGPT out of the foreground shortly after the software-addressed
        // autosend is handed off, so its normal response notification path can fire.
        handler.postDelayed(() -> {
            if (!NativeAdapterProofStore.isAwaitingNotification(this)) return;
            try {
                Intent back = new Intent(this, NativeAdapterProofActivity.class);
                back.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_SINGLE_TOP);
                startActivity(back);
            } catch (Exception ignored) {
                // If Android blocks the short background return, the user can simply
                // return to the Bridge app manually; the notification listener remains active.
            }
        }, RETURN_DELAY_MS);
    }

    private void maybeAdvanceProof() {
        if (NativeAdapterProofStore.CANDIDATE_CAPTURED.equals(NativeAdapterProofStore.state(this)) &&
                !NativeAdapterProofStore.candidateOpened(this)) {
            openCandidateForVerification();
        }
    }

    private void openCandidateForVerification() {
        String id = NativeAdapterProofStore.candidate(this);
        if (id == null || id.trim().isEmpty()) return;
        Uri uri = new Uri.Builder()
                .scheme("https")
                .authority("chatgpt.com")
                .appendPath("c")
                .appendPath(id.trim())
                .build();
        NativeAdapterProofStore.markVerifying(this);
        if (!launchChatGpt(uri)) {
            NativeAdapterProofStore.fail(this, "Captured conversationId could not be reopened through the official ChatGPT deeplink activity.");
        }
    }

    private boolean launchChatGpt(Uri uri) {
        try {
            Intent i = new Intent(Intent.ACTION_VIEW, uri);
            i.setComponent(new ComponentName(CHATGPT_PACKAGE, CHATGPT_DEEPLINK_ACTIVITY));
            i.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(i);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    private boolean hasNotificationAccess() {
        if (Build.VERSION.SDK_INT >= 27) {
            Set<String> enabled = NotificationManager.getEnabledListenerPackages(this);
            return enabled.contains(getPackageName());
        }
        String flat = Settings.Secure.getString(getContentResolver(), "enabled_notification_listeners");
        return flat != null && flat.contains(getPackageName());
    }

    private boolean isAccessibilityVerifierEnabled() {
        String flat = Settings.Secure.getString(getContentResolver(), Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
        return flat != null && flat.contains(NativeProbeAccessibilityService.class.getName());
    }

    private void refreshUi() {
        if (status == null) return;
        String state = NativeAdapterProofStore.state(this);
        String candidate = NativeAdapterProofStore.candidate(this);
        String marker = NativeAdapterProofStore.marker(this);
        long started = NativeAdapterProofStore.startedAt(this);
        long age = started <= 0 ? 0 : Math.max(0, (System.currentTimeMillis() - started) / 1000L);

        StringBuilder b = new StringBuilder();
        b.append("ChatGPT APK target: 1.2026.237\n");
        b.append("Write path: explicit ChatGptDeeplinkActivity\n");
        b.append("Notification access: ").append(hasNotificationAccess() ? "ENABLED" : "NOT ENABLED").append('\n');
        b.append("Accessibility receipt verifier: ").append(isAccessibilityVerifierEnabled() ? "ENABLED" : "NOT ENABLED").append('\n');
        b.append("\nstate = ").append(state).append('\n');
        if (!marker.isEmpty()) b.append("marker = ").append(marker).append('\n');
        if (started > 0) b.append("age = ").append(age).append(" s\n");
        if (!candidate.isEmpty()) b.append("conversationId = ").append(candidate).append('\n');
        String lastTag = NativeAdapterProofStore.lastNotificationTag(this);
        if (!lastTag.isEmpty()) b.append("last ChatGPT notification tag = ").append(lastTag).append('\n');
        String lastText = NativeAdapterProofStore.lastNotificationText(this);
        if (!lastText.isEmpty()) b.append("notification text = ").append(abbreviate(lastText, 220)).append('\n');
        String failure = NativeAdapterProofStore.failure(this);
        if (!failure.isEmpty()) b.append("\nFAILURE: ").append(failure).append('\n');
        if (NativeAdapterProofStore.verified(this)) {
            b.append("\nPASS: direct /c/<notification-tag> reopened the created conversation and the unique assistant marker was observed by the read-only verifier.\n");
        } else if (NativeAdapterProofStore.VERIFYING.equals(state)) {
            b.append("\nVerifying: the captured ID has been reopened directly. Waiting for the unique assistant marker in the native conversation tree.\n");
        } else if (NativeAdapterProofStore.WAITING_NOTIFICATION.equals(state)) {
            b.append("\nWaiting for a ChatGPT conversation notification. Search/drawer/coordinates are not used.\n");
        }

        status.setText(b.toString());
        startButton.setEnabled(!NativeAdapterProofStore.isPending(this));
        openCandidateButton.setEnabled(candidate != null && !candidate.isEmpty() && !NativeAdapterProofStore.verified(this));
    }

    private static String abbreviate(String s, int max) {
        if (s == null) return "";
        String one = s.replace('\n', ' ').replace('\r', ' ');
        return one.length() <= max ? one : one.substring(0, max) + "...";
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
'''

(java_dir / "NativeAdapterProofStore.java").write_text(store_java)
(java_dir / "NativeAdapterNotificationListenerService.java").write_text(listener_java)
(java_dir / "NativeAdapterProofActivity.java").write_text(activity_java)

# Add a read-only proof observer to the already-enabled Accessibility service.
service = service_path.read_text()
old_watchdog = '''        @Override public void run() {\n            if (isActiveProbe()) processTargetWindow("watchdog");\n            handler.postDelayed(this, isActiveProbe() ? 300 : 900);\n        }\n'''
new_watchdog = '''        @Override public void run() {\n            if (NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this)) {\n                observeNativeAdapterProof(null);\n            }\n            if (isActiveProbe()) processTargetWindow("watchdog");\n            boolean hot = isActiveProbe() || NativeAdapterProofStore.isAwaitingReceipt(NativeProbeAccessibilityService.this);\n            handler.postDelayed(this, hot ? 300 : 900);\n        }\n'''
if old_watchdog not in service:
    raise SystemExit("watchdog block not found in accessibility service")
service = service.replace(old_watchdog, new_watchdog, 1)

old_event_head = '''    @Override public void onAccessibilityEvent(AccessibilityEvent event) {\n        if (!isActiveProbe()) return;\n'''
new_event_head = '''    @Override public void onAccessibilityEvent(AccessibilityEvent event) {\n        // NATIVE_ADAPTER_P1_READ_ONLY_RECEIPT_OBSERVER\n        observeNativeAdapterProof(event);\n        if (!isActiveProbe()) return;\n'''
if old_event_head not in service:
    raise SystemExit("onAccessibilityEvent head not found")
service = service.replace(old_event_head, new_event_head, 1)

insert_marker = '''    @Override public void onInterrupt() {\n'''
observer_methods = r'''    private void observeNativeAdapterProof(AccessibilityEvent event) {
        if (!NativeAdapterProofStore.isAwaitingReceipt(this)) return;
        if (event != null) {
            CharSequence pkg = event.getPackageName();
            if (pkg != null && !ProbeState.TARGET.equals(pkg.toString())) return;
        }
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (!ProbeState.TARGET.equals(packageOf(root))) return;
        String marker = NativeAdapterProofStore.marker(this);
        if (marker == null || marker.isEmpty()) return;
        if (!nativeAdapterProofTreeContains(root, marker, 700)) return;

        NativeAdapterProofStore.markVerified(this);
        ProbeState.log(this, "NATIVE_ADAPTER_P1 VERIFIED: captured notification tag reopened the exact conversation and the expected unique assistant marker was observed read-only. conversationId=" + NativeAdapterProofStore.candidate(this) + ".");
        try {
            Intent back = new Intent(this, NativeAdapterProofActivity.class);
            back.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(back);
        } catch (Exception e) {
            ProbeState.log(this, "NATIVE_ADAPTER_P1 verification succeeded; automatic return to proof UI was blocked: " + e.getClass().getSimpleName());
        }
    }

    private boolean nativeAdapterProofTreeContains(AccessibilityNodeInfo root, String needle, int limit) {
        if (root == null || needle == null || needle.isEmpty()) return false;
        ArrayList<AccessibilityNodeInfo> queue = new ArrayList<>();
        queue.add(root);
        for (int i = 0; i < queue.size() && i < limit; i++) {
            AccessibilityNodeInfo n = queue.get(i);
            if (n == null) continue;
            CharSequence text = n.getText();
            CharSequence desc = n.getContentDescription();
            if ((text != null && text.toString().contains(needle)) ||
                    (desc != null && desc.toString().contains(needle))) return true;
            int children = n.getChildCount();
            for (int c = 0; c < children && queue.size() < limit; c++) {
                AccessibilityNodeInfo child = n.getChild(c);
                if (child != null) queue.add(child);
            }
        }
        return false;
    }

'''
if insert_marker not in service:
    raise SystemExit("onInterrupt insertion marker not found")
service = service.replace(insert_marker, observer_methods + insert_marker, 1)
service_path.write_text(service)

# Replace the launcher with the native-adapter proof UI and add the listener service.
ANDROID = "http://schemas.android.com/apk/res/android"
A = "{" + ANDROID + "}"
ET.register_namespace("android", ANDROID)
tree = ET.parse(manifest_path)
manifest = tree.getroot()
app = manifest.find("application")
if app is None:
    raise SystemExit("manifest application element missing")

# Ensure package visibility for the explicit ChatGPT component on modern Android.
queries = manifest.find("queries")
if queries is None:
    queries = ET.Element("queries")
    manifest.insert(0, queries)
if not any(p.get(A + "name") == "com.openai.chatgpt" for p in queries.findall("package")):
    ET.SubElement(queries, "package", {A + "name": "com.openai.chatgpt"})

# Remove launcher filters from legacy activities but keep their components available.
for tag in ("activity", "activity-alias"):
    for comp in app.findall(tag):
        for filt in list(comp.findall("intent-filter")):
            actions = {x.get(A + "name") for x in filt.findall("action")}
            categories = {x.get(A + "name") for x in filt.findall("category")}
            if "android.intent.action.MAIN" in actions and "android.intent.category.LAUNCHER" in categories:
                comp.remove(filt)

for existing in list(app.findall("activity")):
    if existing.get(A + "name") == "com.pebblebridge.poc.NativeAdapterProofActivity":
        app.remove(existing)
proof_activity = ET.SubElement(app, "activity", {
    A + "name": "com.pebblebridge.poc.NativeAdapterProofActivity",
    A + "exported": "true",
    A + "label": "Native Adapter P1",
    A + "launchMode": "singleTop",
})
intent_filter = ET.SubElement(proof_activity, "intent-filter")
ET.SubElement(intent_filter, "action", {A + "name": "android.intent.action.MAIN"})
ET.SubElement(intent_filter, "category", {A + "name": "android.intent.category.LAUNCHER"})

for existing in list(app.findall("service")):
    if existing.get(A + "name") == "com.pebblebridge.poc.NativeAdapterNotificationListenerService":
        app.remove(existing)
listener = ET.SubElement(app, "service", {
    A + "name": "com.pebblebridge.poc.NativeAdapterNotificationListenerService",
    A + "label": "Native Adapter conversation binding",
    A + "permission": "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE",
    A + "exported": "true",
})
listener_filter = ET.SubElement(listener, "intent-filter")
ET.SubElement(listener_filter, "action", {A + "name": "android.service.notification.NotificationListenerService"})

tree.write(manifest_path, encoding="utf-8", xml_declaration=True)

# Version bump only; preserve applicationId/signing continuity.
gradle = gradle_path.read_text()
gradle, n = re.subn(r"versionCode\s+31\b", "versionCode 32", gradle, count=1)
if n != 1:
    raise SystemExit("versionCode 31 replacement failed")
if "0.31-centered-overlay-free-search-gesture" not in gradle:
    raise SystemExit("v0.31 versionName not found")
gradle = gradle.replace("0.31-centered-overlay-free-search-gesture", "0.32-native-adapter-p1", 1)
gradle_path.write_text(gradle)

# Build-time assertions: no write-side Accessibility is part of the new proof UI.
assert "ChatGptDeeplinkActivity" in activity_java
assert "autosend" in activity_java
assert "StatusBarNotification" in listener_java
assert "getTag()" in listener_java
assert "NATIVE_ADAPTER_P1_READ_ONLY_RECEIPT_OBSERVER" in service_path.read_text()
