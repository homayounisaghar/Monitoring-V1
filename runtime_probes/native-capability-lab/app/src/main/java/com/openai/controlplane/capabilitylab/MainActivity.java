package com.openai.controlplane.capabilitylab;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.ContentValues;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.provider.MediaStore;
import android.text.method.ScrollingMovementMethod;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.OutputStream;

public class MainActivity extends Activity {
    private static final String SCREEN_DESCRIPTION =
            "Stable v0.17 tests a fresh History binding that does not depend on Global Search indexing. It creates one synthetic marker chat, sends exactly once with the proven CLAIM/no-replay Send contract, opens official History, deliberately switches away through the exact New chat control, reopens History, selects only the first semantic conversation row, harvests that row metadata, and requires the exact marker on the reopened thread.

The full report file remains authoritative and captures the relevant ChatGPT Accessibility surfaces. DOWNLOAD FULL REPORT saves it directly to Android Downloads with one tap and no share sheet. No private ChatGPT API is called, no credentials are extracted, and no coordinate writes, gestures, or global actions are used.";

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
    private Button shareButton;
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
        desc.setText(SCREEN_DESCRIPTION);
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

        runButton = button("RUN FRESH HISTORY BINDING PROOF", v -> startSuite());
        root.addView(runButton);
        resetButton = button("Reset Lab run state", v -> {
            if ("RUNNING".equals(LabStore.status(this))) return;
            LabStore.resetRun(this);
            refreshUi();
        });
        root.addView(resetButton);
        copyButton = button("COPY FINAL REPORT", v -> copyReport());
        root.addView(copyButton);
        shareButton = button("DOWNLOAD FULL REPORT", v -> downloadReportFile());
        root.addView(shareButton);

        status = new TextView(this);
        status.setTextSize(13.5f);
        status.setTypeface(Typeface.MONOSPACE);
        status.setTextIsSelectable(true);
        status.setPadding(0, dp(18), 0, dp(12));
        root.addView(status);

        TextView reportTitle = new TextView(this);
        reportTitle.setText("Report / evidence (UI tail only; file keeps the full report)");
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

    private void downloadReportFile() {
        Uri outUri = null;
        try {
            File f = LabStore.ensureReportFile(this);
            if (f == null || !f.exists()) {
                LabStore.append(this, "REPORT_FILE_DOWNLOAD_ERROR missing_report_file");
                refreshUi();
                return;
            }
            LabStore.append(this, "REPORT_FILE_DOWNLOAD_STARTED name=" + f.getName());
            ContentValues values = new ContentValues();
            values.put(MediaStore.MediaColumns.DISPLAY_NAME, f.getName());
            values.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
            values.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
            values.put(MediaStore.MediaColumns.IS_PENDING, 1);
            outUri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
            if (outUri == null) throw new IllegalStateException("Downloads insert returned null");
            try (FileInputStream in = new FileInputStream(f);
                 OutputStream out = getContentResolver().openOutputStream(outUri, "w")) {
                if (out == null) throw new IllegalStateException("Downloads output stream null");
                byte[] buf = new byte[8192];
                int n;
                while ((n = in.read(buf)) >= 0) out.write(buf, 0, n);
                out.flush();
            }
            ContentValues done = new ContentValues();
            done.put(MediaStore.MediaColumns.IS_PENDING, 0);
            getContentResolver().update(outUri, done, null, null);
            LabStore.append(this, "REPORT_FILE_DOWNLOAD_SUCCESS name=" + f.getName());
            Toast.makeText(this, "Saved to Downloads: " + f.getName(), Toast.LENGTH_LONG).show();
        } catch (Throwable t) {
            if (outUri != null) {
                try { getContentResolver().delete(outUri, null, null); } catch (Throwable ignored) {}
            }
            LabStore.append(this, "REPORT_FILE_DOWNLOAD_ERROR " + t.getClass().getSimpleName()
                    + ":" + LabStore.abbrev(String.valueOf(t.getMessage()), 220));
            Toast.makeText(this, "Could not save report", Toast.LENGTH_LONG).show();
            refreshUi();
        }
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
            styleBanner("STARTING FRESH HISTORY BINDING PROOF…", BLUE);
        } else if (running) {
            styleBanner("TEST RUNNING — step " + LabStore.step(this) + "\nDo not operate ChatGPT.", AMBER);
        } else if (finished && runStatus.startsWith("PASS")) {
            styleBanner("✓ TEST COMPLETE — PASS\nDOWNLOAD FULL REPORT is GREEN.", GREEN);
        } else if (finished && runStatus.startsWith("INCONCLUSIVE")) {
            styleBanner("TEST COMPLETE — INCONCLUSIVE\nDOWNLOAD FULL REPORT is GREEN.", AMBER);
        } else if (finished) {
            styleBanner("TEST COMPLETE — " + runStatus + "\nDOWNLOAD FULL REPORT is GREEN.", RED);
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
        b.append("Full report file: ").append(LabStore.reportFileName(this).isEmpty() ? "<created when run starts>" : LabStore.reportFileName(this)).append('\n');
        if (!exact) b.append("\nBLOCKED: exact official ChatGPT profile is required.\n");
        else if (!aLive || !nLive) b.append("\nSETUP: grant both Lab services and return here.\n");
        else if (running || starting) b.append("\nRUNNING: the Lab is executing one bounded official-UI fresh History binding proof. No screenshots are expected; the report file captures the evidence.\n");
        else if (finished) b.append("\nFINISHED: tap DOWNLOAD FULL REPORT and send the .txt file. COPY FINAL REPORT remains a fallback. Reset only before a deliberate new run.\n");
        else b.append("\nREADY: one tap creates one synthetic chat, switches away, reopens History, and verifies the newest semantic row. Do not manually operate ChatGPT while the run is active.\n");

        boolean shizukuReady = LabShizukuObserver.permissionGranted();
        boolean nextAccessibility = exact && !aLive;
        boolean nextNotification = exact && aLive && !nLive;
        boolean readyToRun = exact && aLive && nLive && idle && !starting;
        boolean reportFileReady = finished && LabStore.reportFile(this) != null;

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
                running ? "INDEX TRIGGER LADDER RUNNING…" : "RUN FRESH HISTORY BINDING PROOF",
                readyToRun ? BLUE : GRAY, readyToRun);
        styleButton(resetButton,
                finished ? "Reset completed run" : "Reset Lab run state",
                finished ? AMBER : GRAY, !running && !starting);
        styleButton(copyButton,
                finished ? "COPY FINAL REPORT (fallback)" : "COPY FINAL REPORT (after test)",
                finished ? GREEN : GRAY, finished);
        styleButton(shareButton,
                reportFileReady ? "DOWNLOAD FULL REPORT" : "DOWNLOAD FULL REPORT (after test)",
                reportFileReady ? GREEN : GRAY, reportFileReady);

        String statusText = b.toString();
        status.setText(statusText);

        if (running) {
            LabStore.appendUiSnapshotOnce(this, "RUNNING", buildUiSnapshot(statusText));
        } else if (finished) {
            LabStore.appendUiSnapshotOnce(this, "FINAL", buildUiSnapshot(statusText));
            LabStore.ensureReportFile(this);
        }

        String r = LabStore.report(this);
        report.setText(tail(r, 50000));
    }

    private String buildUiSnapshot(String statusText) {
        StringBuilder b = new StringBuilder();
        b.append("screenTitle=ChatGPT Capability Lab Stable\n");
        b.append("description=").append(SCREEN_DESCRIPTION.replace('\n', ' ')).append('\n');
        b.append("banner=").append(textOf(runBanner)).append('\n');
        b.append("statusText:\n").append(statusText == null ? "" : statusText).append('\n');
        appendButtonSnapshot(b, "accessibility", accessibilityButton);
        appendButtonSnapshot(b, "notification", notificationButton);
        appendButtonSnapshot(b, "shizukuOpen", shizukuOpenButton);
        appendButtonSnapshot(b, "shizukuGrant", shizukuGrantButton);
        appendButtonSnapshot(b, "run", runButton);
        appendButtonSnapshot(b, "reset", resetButton);
        appendButtonSnapshot(b, "copy", copyButton);
        appendButtonSnapshot(b, "shareFile", shareButton);
        b.append("reportUiNote=Report / evidence (UI tail only; file keeps the full report)\n");
        return b.toString();
    }

    private static void appendButtonSnapshot(StringBuilder b, String name, Button button) {
        if (button == null) return;
        b.append("button.").append(name)
                .append(" text=").append(button.getText())
                .append(" enabled=").append(button.isEnabled())
                .append('\n');
    }

    private static String textOf(TextView v) {
        return v == null || v.getText() == null ? "" : v.getText().toString().replace('\n', ' ');
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
