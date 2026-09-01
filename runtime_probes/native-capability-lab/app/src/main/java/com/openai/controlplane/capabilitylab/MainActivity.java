package com.openai.controlplane.capabilitylab;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.graphics.Typeface;
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

import org.json.JSONObject;

public class MainActivity extends Activity {
    private final Handler handler = new Handler(Looper.getMainLooper());
    private TextView runBanner;
    private TextView status;
    private TextView report;
    private Button runButton;
    private Button copyButton;
    private volatile boolean starting;

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
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int p = dp(18);
        root.setPadding(p, p, p, p);
        scroll.addView(root);

        TextView title = new TextView(this);
        title.setText("ChatGPT Capability Lab");
        title.setTextSize(25f);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        root.addView(title);

        TextView desc = new TextView(this);
        desc.setText("Unified on-device capability test harness. It replaces the old one-hypothesis/one-APK loop. The Lab fails closed on the exact official ChatGPT build, downloads only an allowlisted test plan from the project repo, executes bounded Android/Accessibility/Notification primitives, branches locally, and emits one final report.\n\nThe current default suite creates and sends ONE synthetic disposable ChatGPT test message while proving the remaining conversationId read side. No ChatGPT credentials/private APIs and no coordinate writes are used.");
        desc.setTextSize(15f);
        desc.setPadding(0, dp(10), 0, dp(12));
        root.addView(desc);

        runBanner = new TextView(this);
        runBanner.setTextSize(20f);
        runBanner.setTypeface(Typeface.DEFAULT_BOLD);
        runBanner.setPadding(dp(12), dp(14), dp(12), dp(14));
        root.addView(runBanner);

        root.addView(button("Open Accessibility settings", v -> startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))));
        root.addView(button("Open Notification Access settings", v -> {
            try { startActivity(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)); }
            catch (Throwable t) { startActivity(new Intent("android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS")); }
        }));

        runButton = button("RUN CURRENT SUITE (1 synthetic test message)", v -> startSuite());
        root.addView(runButton);
        root.addView(button("Reset Lab run state", v -> {
            if ("RUNNING".equals(LabStore.status(this))) return;
            LabStore.resetRun(this);
            refreshUi();
        }));
        copyButton = button("COPY FINAL REPORT", v -> copyReport());
        root.addView(copyButton);

        status = new TextView(this);
        status.setTextSize(13.5f);
        status.setTypeface(Typeface.MONOSPACE);
        status.setTextIsSelectable(true);
        status.setPadding(0, dp(18), 0, dp(12));
        root.addView(status);

        TextView reportTitle = new TextView(this);
        reportTitle.setText("Report / evidence");
        reportTitle.setTextSize(18f);
        reportTitle.setTypeface(Typeface.DEFAULT_BOLD);
        root.addView(reportTitle);

        report = new TextView(this);
        report.setTextSize(11.5f);
        report.setTypeface(Typeface.MONOSPACE);
        report.setTextIsSelectable(true);
        report.setMovementMethod(new ScrollingMovementMethod());
        root.addView(report);

        setContentView(scroll);
        refreshUi();
    }

    private Button button(String label, View.OnClickListener listener) {
        Button b = new Button(this);
        b.setText(label);
        b.setAllCaps(false);
        b.setOnClickListener(listener);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2);
        lp.setMargins(0, dp(4), 0, dp(4));
        b.setLayoutParams(lp);
        return b;
    }

    private void startSuite() {
        if (starting || "RUNNING".equals(LabStore.status(this))) return;
        if (!"IDLE".equals(LabStore.status(this))) {
            LabStore.append(this, "PRECONDITION_FAIL reset finished run before starting a new run");
            refreshUi();
            return;
        }
        if (!ProfileGuard.isExact(this)) {
            LabStore.append(this, "PRECONDITION_FAIL exact ChatGPT profile mismatch");
            refreshUi();
            return;
        }
        if (!LabAccessibilityService.isLive() || !LabStore.accessibilityConnected(this)) {
            LabStore.append(this, "PRECONDITION_FAIL Accessibility service not connected");
            refreshUi();
            return;
        }
        if (!LabNotificationService.isLive() || !LabStore.notificationConnected(this)) {
            LabStore.append(this, "PRECONDITION_FAIL Notification listener not connected");
            refreshUi();
            return;
        }

        starting = true;
        refreshUi();
        new Thread(() -> {
            try {
                PlanLoader.PlanData data = PlanLoader.fetchOrFallback();
                PlanLoader.validate(data.json);
                JSONObject root = new JSONObject(data.json);
                String suite = root.getString("suite");
                LabStore.beginRun(this, data.json, data.sha256, suite);
                LabStore.append(this, "PLAN_SOURCE=" + data.source);
                LabStore.append(this, "PROFILE version=" + ProfileGuard.version(this) + " signer=" + ProfileGuard.signerSha256(this));
                LabStore.append(this, "SERVICES accessibilityConnected=" + LabAccessibilityService.isLive() + " notificationConnected=" + LabNotificationService.isLive());
                runOnUiThread(() -> {
                    starting = false;
                    refreshUi();
                    try {
                        LabAccessibilityService.startCurrentPlan();
                    } catch (Throwable t) {
                        LabStore.finish(this, "FAIL:RUNNER_START:" + t.getClass().getSimpleName());
                        LabStore.append(this, "RUNNER_START_ERROR " + String.valueOf(t.getMessage()));
                    }
                });
            } catch (Throwable t) {
                runOnUiThread(() -> {
                    starting = false;
                    LabStore.append(this, "PLAN_START_ERROR " + t.getClass().getSimpleName() + ":" + LabStore.abbrev(String.valueOf(t.getMessage()), 300));
                    refreshUi();
                });
            }
        }, "capability-lab-plan-loader").start();
    }

    private void copyReport() {
        ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        if (cm != null) cm.setPrimaryClip(ClipData.newPlainText("ChatGPT Capability Lab report", LabStore.report(this)));
    }

    private void refreshUi() {
        if (status == null) return;
        boolean exact = ProfileGuard.isExact(this);
        boolean aGrant = settingContains(Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES, getPackageName());
        boolean nGrant = settingContains("enabled_notification_listeners", getPackageName());
        boolean aLive = LabAccessibilityService.isLive() && LabStore.accessibilityConnected(this);
        boolean nLive = LabNotificationService.isLive() && LabStore.notificationConnected(this);
        String runState = LabStore.state(this);
        String runStatus = LabStore.status(this);
        boolean running = "RUNNING".equals(runStatus);
        boolean finished = "FINISHED".equals(runState);
        boolean idle = "IDLE".equals(runStatus);

        if (runBanner != null) {
            if (!exact) {
                runBanner.setText("BLOCKED — ChatGPT build mismatch");
            } else if (!aLive || !nLive) {
                runBanner.setText("SETUP REQUIRED — enable both Lab services");
            } else if (starting) {
                runBanner.setText("STARTING TEST…");
            } else if (running) {
                runBanner.setText("TEST RUNNING — step " + LabStore.step(this) + "\nDo not operate ChatGPT until this changes.");
            } else if (finished && runStatus.startsWith("PASS")) {
                runBanner.setText("✓ TEST COMPLETE — PASS\nTap COPY FINAL REPORT.");
            } else if (finished && runStatus.startsWith("INCONCLUSIVE")) {
                runBanner.setText("TEST COMPLETE — INCONCLUSIVE\nTap COPY FINAL REPORT.");
            } else if (finished) {
                runBanner.setText("TEST COMPLETE — " + runStatus + "\nTap COPY FINAL REPORT.");
            } else {
                runBanner.setText("READY TO RUN");
            }
        }

        StringBuilder b = new StringBuilder();
        b.append("Expected ChatGPT: ").append(ProfileGuard.EXPECTED_VERSION).append('\n');
        b.append("Detected ChatGPT: ").append(ProfileGuard.version(this)).append(exact ? " [EXACT]" : " [MISMATCH]").append('\n');
        b.append("Signer: ").append(ProfileGuard.shortSigner(this)).append(exact ? " [PINNED]" : " [UNVERIFIED]").append('\n');
        b.append("Accessibility grant/live: ").append(aGrant).append('/').append(aLive).append('\n');
        b.append("Notification grant/live: ").append(nGrant).append('/').append(nLive).append('\n');
        b.append("Plan URL: ").append(PlanLoader.PLAN_URL).append('\n');
        b.append("Run: ").append(LabStore.compactSummary(this)).append('\n');
        if (!exact) b.append("\nBLOCKED: exact official ChatGPT profile is required.\n");
        else if (!aLive || !nLive) b.append("\nSETUP: grant both services and return here. The RUN button stays fail-closed until both callbacks are live.\n");
        else if (running || starting) b.append("\nRUNNING: allow the Lab to navigate ChatGPT and return itself here. No intermediate screenshots are required.\n");
        else if (finished) b.append("\nFINISHED: use the large completion banner above and tap COPY FINAL REPORT. Reset only before a deliberate new run.\n");
        else b.append("\nREADY: one tap runs the current suite autonomously. Do not manually operate ChatGPT while a run is active.\n");
        status.setText(b.toString());

        String r = LabStore.report(this);
        report.setText(tail(r, 50000));
        if (runButton != null) runButton.setEnabled(exact && aLive && nLive && idle && !starting);
        if (copyButton != null) copyButton.setEnabled(finished);
    }

    private boolean settingContains(String key, String token) {
        try {
            String value = Settings.Secure.getString(getContentResolver(), key);
            return value != null && value.contains(token);
        } catch (Throwable t) {
            return false;
        }
    }

    private static String tail(String s, int max) {
        if (s == null || s.isEmpty()) return "<none>";
        return s.length() <= max ? s : "...<older evidence truncated in UI>...\n" + s.substring(s.length() - max);
    }

    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }
}
