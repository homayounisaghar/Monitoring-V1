package com.openai.controlplane.capabilitylab;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Typeface;
import android.net.Uri;
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
    private Button accessibilityButton;
    private Button notificationButton;
    private Button shizukuOpenButton;
    private Button shizukuGrantButton;
    private Button runButton;
    private Button resetButton;
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
        title.setText("ChatGPT Capability Lab Stable");
        title.setTextSize(25f);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        root.addView(title);

        TextView desc = new TextView(this);
        desc.setText("Stable v0.10 matches the real-device Menu semantic exactly (not by substring) and continues the official Search proof across every ChatGPT accessibility window and exact semantic/custom-action labels, while keeping the Conversation History -> Search chats fallback. It also adds a privacy-redacted control census so any remaining mismatch is directly calibratable. The Lab creates one synthetic marker chat, uses the already-proven bounded semantic Send, opens ChatGPT's own Search control, enters the marker into the official Search ChatGPT field, requires a unique marker-bearing conversation result, then opens that result and verifies the exact marker thread.\n\nNo private ChatGPT API is called by the Lab, no ChatGPT credentials are extracted, and no coordinate writes are used. Shizuku remains available only as optional LAB-only diagnostics and is not required for this proof.");
        desc.setTextSize(15f);
        desc.setPadding(0, dp(10), 0, dp(12));
        root.addView(desc);

        runBanner = new TextView(this);
        runBanner.setTextSize(20f);
        runBanner.setTypeface(Typeface.DEFAULT_BOLD);
        runBanner.setPadding(dp(12), dp(14), dp(12), dp(14));
        root.addView(runBanner);

        accessibilityButton = button("Accessibility", v -> startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));
        root.addView(accessibilityButton);
        notificationButton = button("Notification Access", v -> {
            try { startActivity(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)); }
            catch (Throwable t) { startActivity(new Intent("android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS")); }
        });
        root.addView(notificationButton);
        shizukuOpenButton = button("Optional Shizuku diagnostics", v -> openShizuku());
        root.addView(shizukuOpenButton);
        shizukuGrantButton = button("Optional Shizuku permission", v -> requestShizukuPermission());
        root.addView(shizukuGrantButton);

        runButton = button("RUN SEARCH BINDING PROOF", v -> startSuite());
        root.addView(runButton);
        resetButton = button("Reset Lab run state", v -> {
            if ("RUNNING".equals(LabStore.status(this))) return;
            LabStore.resetRun(this);
            refreshUi();
        });
        root.addView(resetButton);
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

    private static final int GREEN = Color.rgb(46, 125, 50);
    private static final int BLUE = Color.rgb(21, 101, 192);
    private static final int AMBER = Color.rgb(239, 108, 0);
    private static final int RED = Color.rgb(198, 40, 40);
    private static final int GRAY = Color.rgb(84, 110, 122);

    private void styleButton(Button b, String text, int color, boolean enabled) {
        if (b == null) return;
        b.setText(text);
        b.setEnabled(enabled);
        b.setBackgroundTintList(ColorStateList.valueOf(color));
        b.setTextColor(Color.WHITE);
    }

    private void styleBanner(String text, int color) {
        if (runBanner == null) return;
        runBanner.setText(text);
        runBanner.setTextColor(Color.WHITE);
        runBanner.setBackgroundColor(color);
    }

    private void openShizuku() {
        try {
            Intent launch = getPackageManager().getLaunchIntentForPackage("moe.shizuku.privileged.api");
            if (launch != null) {
                startActivity(launch);
                return;
            }
        } catch (Throwable ignored) {}
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://shizuku.rikka.app/download/")));
        } catch (Throwable t) {
            LabStore.append(this, "SHIZUKU_OPEN_ERROR " + t.getClass().getSimpleName());
        }
    }

    private void requestShizukuPermission() {
        try {
            LabShizukuObserver.requestPermission();
            LabStore.append(this, "SHIZUKU_PERMISSION_REQUEST issued");
        } catch (Throwable t) {
            LabStore.append(this, "SHIZUKU_PERMISSION_REQUEST_ERROR " + t.getClass().getSimpleName()
                    + ":" + LabStore.abbrev(String.valueOf(t.getMessage()), 220));
        }
        refreshUi();
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
                LabStore.append(this, "SERVICES accessibilityConnected=" + LabAccessibilityService.isLive()
                        + " notificationConnected=" + LabNotificationService.isLive());
                LabStore.append(this, "OPTIONAL_LAB_OBSERVER " + LabShizukuObserver.compactStatus()
                        + " classification=LAB_ONLY_DISCOVERY");
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

        if (!exact) {
            styleBanner("BLOCKED — ChatGPT build mismatch", RED);
        } else if (!aLive || !nLive) {
            styleBanner("SETUP REQUIRED — follow the BLUE button", AMBER);
        } else if (starting) {
            styleBanner("STARTING SEARCH PROOF…", BLUE);
        } else if (running) {
            styleBanner("TEST RUNNING — step " + LabStore.step(this) + "\nDo not operate ChatGPT.", AMBER);
        } else if (finished && runStatus.startsWith("PASS")) {
            styleBanner("✓ TEST COMPLETE — PASS\nCOPY FINAL REPORT is GREEN.", GREEN);
        } else if (finished && runStatus.startsWith("INCONCLUSIVE")) {
            styleBanner("TEST COMPLETE — INCONCLUSIVE\nCOPY FINAL REPORT is GREEN.", AMBER);
        } else if (finished) {
            styleBanner("TEST COMPLETE — " + runStatus + "\nCOPY FINAL REPORT is GREEN.", RED);
        } else {
            styleBanner("READY TO RUN — press the BLUE RUN button", BLUE);
        }

        StringBuilder b = new StringBuilder();
        b.append("Expected ChatGPT: ").append(ProfileGuard.EXPECTED_VERSION).append('\n');
        b.append("Detected ChatGPT: ").append(ProfileGuard.version(this)).append(exact ? " [EXACT]" : " [MISMATCH]").append('\n');
        b.append("Signer: ").append(ProfileGuard.shortSigner(this)).append(exact ? " [PINNED]" : " [UNVERIFIED]").append('\n');
        b.append("Accessibility grant/live: ").append(aGrant).append('/').append(aLive).append('\n');
        b.append("Notification grant/live: ").append(nGrant).append('/').append(nLive).append('\n');
        b.append("Optional Shizuku: ").append(LabShizukuObserver.compactStatus()).append('\n');
        b.append("Plan URL: ").append(PlanLoader.PLAN_URL).append('\n');
        b.append("Run: ").append(LabStore.compactSummary(this)).append('\n');
        if (!exact) b.append("\nBLOCKED: exact official ChatGPT profile is required.\n");
        else if (!aLive || !nLive) b.append("\nSETUP: grant both Lab services and return here.\n");
        else if (running || starting) b.append("\nRUNNING: allow the Lab to navigate official ChatGPT Search and return itself here. No intermediate screenshots are required.\n");
        else if (finished) b.append("\nFINISHED: use the completion banner above and tap COPY FINAL REPORT. Reset only before a deliberate new run.\n");
        else b.append("\nREADY: one tap runs the production-faithful official Global Search binding proof. Do not manually operate ChatGPT while a run is active.\n");
        boolean shizukuReady = LabShizukuObserver.permissionGranted();
        boolean nextAccessibility = exact && !aLive;
        boolean nextNotification = exact && aLive && !nLive;
        boolean readyToRun = exact && aLive && nLive && idle && !starting;

        styleButton(accessibilityButton,
                aLive ? "✓ Accessibility enabled" : "Enable Accessibility",
                aLive ? GREEN : (nextAccessibility ? BLUE : GRAY), true);
        styleButton(notificationButton,
                nLive ? "✓ Notification Access enabled" : "Enable Notification Access",
                nLive ? GREEN : (nextNotification ? BLUE : GRAY), true);
        styleButton(shizukuOpenButton,
                shizukuReady ? "✓ Optional Shizuku observer ready" : "Optional: Open Shizuku diagnostics",
                shizukuReady ? GREEN : GRAY, true);
        styleButton(shizukuGrantButton,
                shizukuReady ? "✓ Optional Shizuku permission granted" : "Optional: Grant Shizuku permission",
                shizukuReady ? GREEN : GRAY, true);
        styleButton(runButton,
                running ? "TEST RUNNING…" : "RUN SEARCH BINDING PROOF",
                readyToRun ? BLUE : GRAY, readyToRun);
        styleButton(resetButton,
                finished ? "Reset completed run" : "Reset Lab run state",
                finished ? AMBER : GRAY, !running && !starting);
        styleButton(copyButton,
                finished ? "COPY FINAL REPORT" : "COPY FINAL REPORT (after test)",
                finished ? GREEN : GRAY, finished);

        status.setText(b.toString());

        String r = LabStore.report(this);
        report.setText(tail(r, 50000));
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
