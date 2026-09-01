package com.openai.controlplane.notificationprobe;

import android.app.Activity;
import android.app.NotificationManager;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.graphics.Typeface;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.service.notification.NotificationListenerService;
import android.text.method.ScrollingMovementMethod;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.Set;

public class MainActivity extends Activity {
    private static final String CHATGPT_PACKAGE = "com.openai.chatgpt";
    private static final String EXPECTED_VERSION = "1.2026.237";

    private final Handler handler = new Handler(Looper.getMainLooper());
    private TextView status;
    private final Runnable refresh = new Runnable() {
        @Override public void run() {
            refreshUi();
            handler.postDelayed(this, 500L);
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildUi();
    }

    @Override
    protected void onResume() {
        super.onResume();
        handler.removeCallbacks(refresh);
        handler.post(refresh);
    }

    @Override
    protected void onPause() {
        super.onPause();
        handler.removeCallbacks(refresh);
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int pad = dp(18);
        root.setPadding(pad, pad, pad, pad);

        TextView title = new TextView(this);
        title.setText("Notification Read-Side Probe P3");
        title.setTextSize(24f);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        root.addView(title, new LinearLayout.LayoutParams(-1, -2));

        TextView subtitle = new TextView(this);
        subtitle.setText("Read-only diagnostic for the remaining conversationId gap. P3 verifies that Android actually binds the NotificationListenerService and records ChatGPT notification metadata (tag, shortcut, channel/conversation metadata, ranking, locus and selected extras). It performs no ChatGPT Send, no Accessibility action and has no INTERNET permission.");
        subtitle.setTextSize(15f);
        LinearLayout.LayoutParams subLp = new LinearLayout.LayoutParams(-1, -2);
        subLp.topMargin = dp(8);
        root.addView(subtitle, subLp);

        Button access = new Button(this);
        access.setText("Open notification access settings");
        access.setOnClickListener(v -> {
            try {
                startActivity(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));
            } catch (Throwable t) {
                startActivity(new Intent("android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS"));
            }
        });
        LinearLayout.LayoutParams firstLp = new LinearLayout.LayoutParams(-1, -2);
        firstLp.topMargin = dp(16);
        root.addView(access, firstLp);

        Button rebind = new Button(this);
        rebind.setText("Request listener rebind");
        rebind.setOnClickListener(v -> requestListenerRebind());
        root.addView(rebind, new LinearLayout.LayoutParams(-1, -2));

        Button clear = new Button(this);
        clear.setText("Clear captured events");
        clear.setOnClickListener(v -> {
            ProbeStore.clearEvents(this);
            refreshUi();
        });
        root.addView(clear, new LinearLayout.LayoutParams(-1, -2));

        Button copy = new Button(this);
        copy.setText("Copy trace");
        copy.setOnClickListener(v -> copyTrace());
        root.addView(copy, new LinearLayout.LayoutParams(-1, -2));

        status = new TextView(this);
        status.setTextSize(13f);
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

    private void requestListenerRebind() {
        ProbeStore.markRebindRequested(this);
        try {
            ComponentName component = new ComponentName(this, NotificationProbeService.class);
            NotificationListenerService.requestRebind(component);
        } catch (Throwable t) {
            ProbeStore.append(this, "REBIND_CALL_ERROR " + t.getClass().getSimpleName());
        }
        refreshUi();
    }

    private boolean hasNotificationAccess() {
        try {
            Set<String> enabled = NotificationManager.getEnabledListenerPackages(this);
            return enabled != null && enabled.contains(getPackageName());
        } catch (Throwable t) {
            String flat = Settings.Secure.getString(getContentResolver(), "enabled_notification_listeners");
            return flat != null && flat.contains(getPackageName());
        }
    }

    private String chatGptVersion() {
        try {
            PackageInfo info = getPackageManager().getPackageInfo(CHATGPT_PACKAGE, 0);
            return info.versionName == null ? "<null>" : info.versionName;
        } catch (Throwable t) {
            return "NOT_INSTALLED";
        }
    }

    private boolean exactBuild() {
        return EXPECTED_VERSION.equals(chatGptVersion());
    }

    private void refreshUi() {
        if (status == null) return;
        boolean access = hasNotificationAccess();
        boolean connected = ProbeStore.listenerConnected(this);
        String version = chatGptVersion();

        StringBuilder b = new StringBuilder();
        b.append("Expected ChatGPT: ").append(EXPECTED_VERSION).append('\n');
        b.append("Detected ChatGPT: ").append(version).append(exactBuild() ? " [EXACT]" : " [MISMATCH]").append('\n');
        b.append("Notification Access grant: ").append(access ? "ENABLED" : "NOT ENABLED").append('\n');
        b.append("Listener connection callback: ").append(connected ? "CONNECTED" : "NOT CONNECTED").append('\n');
        b.append("Listener connectedAt: ").append(formatTime(ProbeStore.connectedAt(this))).append('\n');
        b.append("Listener disconnectedAt: ").append(formatTime(ProbeStore.disconnectedAt(this))).append('\n');
        b.append("Last rebind request: ").append(formatTime(ProbeStore.rebindRequestedAt(this))).append('\n');
        b.append("Captured event count: ").append(ProbeStore.eventCount(this)).append('\n');
        b.append("Last event: ").append(formatTime(ProbeStore.lastEventAt(this))).append('\n');

        if (!exactBuild()) {
            b.append("\nFAIL CLOSED: P3 evidence is accepted only for exact ChatGPT 1.2026.237.\n");
        } else if (!access) {
            b.append("\nNEXT: grant Notification Access to exactly Notification Read-Side Probe P3. No ChatGPT action is required yet.\n");
        } else if (!connected) {
            b.append("\nNEXT: tap REQUEST LISTENER REBIND. Do not create another ChatGPT test conversation yet.\n");
        } else {
            b.append("\nLISTENER READY. P3 is passively observing ChatGPT notification traffic. No ChatGPT mutation has been performed by P3.\n");
        }

        String log = ProbeStore.log(this);
        b.append("\n=== RECENT P3 EVENTS ===\n");
        b.append(tail(log, 14000));
        status.setText(b.toString());
    }

    private void copyTrace() {
        ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        if (cm != null && status != null) {
            cm.setPrimaryClip(ClipData.newPlainText("P3 notification trace", status.getText()));
        }
    }

    private static String tail(String s, int max) {
        if (s == null || s.isEmpty()) return "<none>\n";
        return s.length() <= max ? s : "...<older events truncated>...\n" + s.substring(s.length() - max);
    }

    private static String formatTime(long value) {
        if (value <= 0L) return "<never>";
        return new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date(value));
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
