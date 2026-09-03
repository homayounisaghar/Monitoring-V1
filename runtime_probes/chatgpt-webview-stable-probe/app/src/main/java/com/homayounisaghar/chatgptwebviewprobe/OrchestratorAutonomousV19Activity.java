package com.homayounisaghar.chatgptwebviewprobe;

import android.content.ContentValues;
import android.content.SharedPreferences;
import android.content.pm.PackageInfo;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.MediaStore;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.OutputStream;
import java.lang.reflect.Field;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.UUID;

/**
 * Stable v0.19 - one-tap autonomous runtime harness.
 *
 * This is a TEST CLIENT layered above the existing v0.18 orchestrator/capability
 * implementation. It does not become production orchestration logic.
 *
 * The first scenario is intentionally narrow and side-effect-light:
 *   telemetry preflight -> baseline -> Session Start -> Dictation Start ->
 *   semantic checkpoint -> Dictation Stop -> bounded receipt observation ->
 *   unconditional Session recovery -> final classification.
 *
 * No ChatGPT message is sent. No raw audio, speech or chat text is uploaded.
 * Telemetry contains only coarse state, semantic counts and action receipts.
 */
public class OrchestratorAutonomousV19Activity extends OrchestratorFoundationV18Activity {
    private static final String PREFS19 = "stable_v19_autonomous_harness";
    private static final String SCENARIO_ID = "dictation-stop-recovery";
    private static final int SCENARIO_VERSION = 1;
    private static final String SCHEMA_VERSION = "cp-autonomous-runtime-v1";

    private final Handler h19 = new Handler(Looper.getMainLooper());
    private final StringBuilder localEvents = new StringBuilder();

    private SharedPreferences prefs19;
    private Button runFullButton;
    private TextView autoStatus;
    private WebView web19;

    private boolean testRunning19 = false;
    private String testId19 = "-";
    private int seq19 = 0;
    private long startedAt19 = 0L;
    private String stopClassification19 = "NOT_RUN";
    private String finalClassification19 = "NOT_RUN";
    private boolean telemetryHealthy19 = false;

    private interface UploadCallback {
        void done(JSONObject result);
    }

    private interface Condition {
        boolean ok();
    }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs19 = getSharedPreferences(PREFS19, MODE_PRIVATE);
        web19 = findWeb19(getWindow().getDecorView());
        installHarnessPanel19();
        reportInterruptedRunIfNeeded19();
    }

    private void installHarnessPanel19() {
        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) content;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        int wi = web19 == null ? 0 : root.indexOfChild(web19);
        if (wi < 0) wi = 0;

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp19(6), dp19(3), dp19(6), dp19(3));

        runFullButton = new Button(this);
        runFullButton.setText("RUN FULL TEST");
        runFullButton.setTextSize(14f);
        runFullButton.setAllCaps(false);
        runFullButton.setOnClickListener(v -> runFullTest19());
        panel.addView(runFullButton, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp19(52)));

        autoStatus = new TextView(this);
        autoStatus.setTextSize(10f);
        autoStatus.setText("v0.19 autonomous harness ready");
        autoStatus.setPadding(dp19(6), dp19(3), dp19(6), dp19(3));
        panel.addView(autoStatus, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));

        root.addView(panel, wi, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void runFullTest19() {
        if (testRunning19) return;
        testRunning19 = true;
        telemetryHealthy19 = false;
        testId19 = "cp19-" + UUID.randomUUID();
        seq19 = 0;
        startedAt19 = System.currentTimeMillis();
        stopClassification19 = "NOT_RUN";
        finalClassification19 = "RUNNING";
        localEvents.setLength(0);
        if (runFullButton != null) {
            runFullButton.setEnabled(false);
            runFullButton.setText("RUNNING...");
        }
        persistRun19(true, "STARTING");
        setAutoStatus19("Telemetry preflight...");

        JSONObject pre = captureState19();
        put19(pre, "preflight", true);
        postPhase19("TELEMETRY_PREFLIGHT", "RUNNING", pre, result -> {
            if (!result.optBoolean("success", false)) {
                telemetryHealthy19 = false;
                finalClassification19 = "TELEMETRY_UNAVAILABLE";
                log19("TELEMETRY_PREFLIGHT_FAIL");
                finishLocally19(false);
                return;
            }
            telemetryHealthy19 = true;
            postRequiredPhase19("RUN_STARTED", "RUNNING", captureState19(), this::waitForBaseline19);
        });
    }

    private void waitForBaseline19() {
        setAutoStatus19("Waiting for stable semantic snapshot...");
        waitUntil19(() -> boolField19("snapOk"), 3500L,
                () -> postRequiredPhase19("BASELINE_READY", "RUNNING", captureState19(), this::startSession19),
                () -> {
                    finalClassification19 = "SNAPSHOT_NOT_READY";
                    postPhase19("BASELINE_TIMEOUT", "FAIL", captureState19(), r -> recoverSession19());
                });
    }

    private void startSession19() {
        setAutoStatus19("Starting InteractionSession...");
        JSONObject click = clickButton19("SESSION START");
        JSONObject state = captureState19();
        put19(state, "click", click);
        postRequiredPhase19("SESSION_START_DISPATCH", "RUNNING", state, () ->
                waitUntil19(() -> "ACTIVE".equals(stringField19("sessionState")), 3500L,
                        () -> postRequiredPhase19("SESSION_ACTIVE", "RUNNING", captureState19(), this::startDictation19),
                        () -> {
                            finalClassification19 = "SESSION_START_FAILED";
                            postPhase19("SESSION_START_TIMEOUT", "FAIL", captureState19(), r -> recoverSession19());
                        }));
    }

    private void startDictation19() {
        setAutoStatus19("Starting Dictation...");
        postRequiredPhase19("BEFORE_DICTATION_START", "RUNNING", captureState19(), () -> {
            JSONObject click = clickButton19("D START");
            JSONObject state = captureState19();
            put19(state, "click", click);
            postRequiredPhase19("DICTATION_START_DISPATCH", "RUNNING", state, () ->
                    waitUntil19(this::dictationStartObserved19, 5000L,
                            () -> h19.postDelayed(this::postStartCheckpoint19, 900L),
                            () -> {
                                finalClassification19 = "DICTATION_START_FAILED";
                                postPhase19("DICTATION_START_TIMEOUT", "FAIL", captureState19(), r -> recoverSession19());
                            }));
        });
    }

    private boolean dictationStartObserved19() {
        String lease = stringField19("micLeaseMode");
        String last = stringField19("lastAction");
        String status = stringField19("lastActionStatus");
        return "DICTATION".equals(lease)
                && ("DICTATION_START".equals(last)
                || status.contains("CONFIRMED")
                || status.contains("ACCEPTED_REVERSIBLE_START"));
    }

    private void postStartCheckpoint19() {
        setAutoStatus19("Capturing post-Start semantic state...");
        postRequiredPhase19("POST_DICTATION_START", "RUNNING", captureState19(), () ->
                h19.postDelayed(this::beforeStop19, 900L));
    }

    private void beforeStop19() {
        setAutoStatus19("Checkpointing before Dictation Stop...");
        postRequiredPhase19("BEFORE_DICTATION_STOP", "RUNNING", captureState19(), this::dispatchStop19);
    }

    private void dispatchStop19() {
        setAutoStatus19("Attempting Dictation Stop once...");
        JSONObject click = clickButton19("D STOP");
        JSONObject immediate = captureState19();
        put19(immediate, "click", click);
        postRequiredPhase19("DICTATION_STOP_DISPATCH", "RUNNING", immediate, () ->
                h19.postDelayed(this::checkpointStop900ms19, 900L));
    }

    private void checkpointStop900ms19() {
        JSONObject state = captureState19();
        String v18Action = stringField19("last18Action");
        String cls = "DICTATION_STOP".equals(v18Action) ? "HANDLER_OBSERVED" : "HANDLER_NOT_OBSERVED";
        postRequiredPhase19("DICTATION_STOP_AFTER_900MS", cls, state, () ->
                waitUntil19(this::stopReachedTerminal19, 12500L,
                        () -> finishStopObservation19(false),
                        () -> finishStopObservation19(true)));
    }

    private boolean stopReachedTerminal19() {
        if (!"DICTATION_STOP".equals(stringField19("last18Action"))) return false;
        String s = stringField19("last18Status");
        return s.startsWith("CONFIRMED")
                || s.startsWith("ABORTED")
                || s.startsWith("BLOCKED")
                || s.startsWith("UNCERTAIN")
                || s.startsWith("PARSE_");
    }

    private void finishStopObservation19(boolean timedOut) {
        String action = stringField19("last18Action");
        String status = stringField19("last18Status");
        if (!"DICTATION_STOP".equals(action)) {
            stopClassification19 = "STOP_HANDLER_NOT_OBSERVED";
        } else if (status.startsWith("CONFIRMED")) {
            stopClassification19 = "STOP_CONFIRMED";
        } else if (status.startsWith("ABORTED")) {
            stopClassification19 = "STOP_ABORTED";
        } else if (status.startsWith("BLOCKED")) {
            stopClassification19 = "STOP_BLOCKED";
        } else if (status.startsWith("UNCERTAIN")) {
            stopClassification19 = "STOP_UNCERTAIN";
        } else if (timedOut) {
            stopClassification19 = "STOP_TIMEOUT";
        } else {
            stopClassification19 = "STOP_OTHER_TERMINAL";
        }
        JSONObject out = captureState19();
        put19(out, "timed_out", timedOut);
        put19(out, "stop_classification", stopClassification19);
        postPhase19("DICTATION_STOP_RESULT", stopClassification19, out, r -> recoverSession19());
    }

    private void recoverSession19() {
        setAutoStatus19("Recovering/ending session...");
        JSONObject before = captureState19();
        put19(before, "recovery_attempted", true);
        postPhase19("BEFORE_RECOVERY", "RUNNING", before, r -> {
            JSONObject click;
            if ("ACTIVE".equals(stringField19("sessionState"))) click = clickButton19("SESSION END");
            else click = clickResult19("SESSION END", false, false, false, "already_not_active");
            JSONObject afterClick = captureState19();
            put19(afterClick, "click", click);
            postPhase19("RECOVERY_DISPATCH", "RUNNING", afterClick, x ->
                    waitUntil19(this::recoveryComplete19, 4500L,
                            () -> finalAfterRecovery19(true),
                            () -> finalAfterRecovery19(false)));
        });
    }

    private boolean recoveryComplete19() {
        return "IDLE".equals(stringField19("sessionState"))
                && "NONE".equals(stringField19("micLeaseMode"));
    }

    private void finalAfterRecovery19(boolean recovered) {
        if ("RUNNING".equals(finalClassification19)) {
            if ("STOP_CONFIRMED".equals(stopClassification19) && recovered) {
                finalClassification19 = "PASS_STOP_CONFIRMED_RECOVERED";
            } else if (recovered) {
                finalClassification19 = stopClassification19 + "_RECOVERED";
            } else {
                finalClassification19 = stopClassification19 + "_RECOVERY_FAILED";
            }
        } else if (recovered) {
            finalClassification19 = finalClassification19 + "_RECOVERED";
        } else {
            finalClassification19 = finalClassification19 + "_RECOVERY_FAILED";
        }

        JSONObject state = captureState19();
        put19(state, "recovered", recovered);
        put19(state, "stop_classification", stopClassification19);
        put19(state, "final_classification", finalClassification19);
        postPhase19("RECOVERY_RESULT", recovered ? "RECOVERED" : "RECOVERY_FAILED", state, r ->
                postPhase19("FINAL", finalClassification19, captureState19(), finalUpload ->
                        finishLocally19(finalUpload.optBoolean("success", false))));
    }

    private void postRequiredPhase19(String phase, String classification, JSONObject state, Runnable next) {
        postPhase19(phase, classification, state, result -> {
            if (!result.optBoolean("success", false)) {
                telemetryHealthy19 = false;
                if ("RUNNING".equals(finalClassification19)) finalClassification19 = "TELEMETRY_LOST_AT_" + phase;
                log19("REQUIRED_UPLOAD_FAIL_" + phase);
                recoverSession19();
                return;
            }
            next.run();
        });
    }

    private void postPhase19(String phase, String classification, JSONObject state, UploadCallback callback) {
        int seq = ++seq19;
        persistRun19(true, phase);
        JSONObject payload = new JSONObject();
        put19(payload, "kind", "TEST_PHASE");
        put19(payload, "schema_version", SCHEMA_VERSION);
        put19(payload, "scenario_id", SCENARIO_ID);
        put19(payload, "scenario_version", SCENARIO_VERSION);
        put19(payload, "test_id", testId19);
        put19(payload, "seq", seq);
        put19(payload, "phase", phase);
        put19(payload, "classification", classification);
        put19(payload, "app_version", appVersion19());
        put19(payload, "source_ref", TelemetryConfigV19.SOURCE_REF);
        put19(payload, "collector_id", TelemetryConfigV19.COLLECTOR_ID);
        put19(payload, "elapsed_ms", startedAt19 == 0L ? 0L : System.currentTimeMillis() - startedAt19);
        put19(payload, "timestamp_epoch_ms", System.currentTimeMillis());
        put19(payload, "privacy", "no_raw_audio_speech_chat_or_credentials");
        put19(payload, "state", state == null ? new JSONObject() : state);
        log19("PHASE " + seq + " " + phase + " " + classification);

        new Thread(() -> {
            JSONObject result = uploadJson19(payload, 2);
            runOnUiThread(() -> callback.done(result));
        }, "cp19-telemetry-" + seq).start();
    }

    private JSONObject uploadJson19(JSONObject payload, int attempts) {
        JSONObject result = new JSONObject();
        put19(result, "configured", TelemetryConfigV19.isConfigured());
        if (!TelemetryConfigV19.isConfigured()) {
            put19(result, "success", false);
            put19(result, "error", "TelemetryNotConfigured");
            return result;
        }
        for (int attempt = 1; attempt <= attempts; attempt++) {
            HttpURLConnection conn = null;
            try {
                URL url = new URL(TelemetryConfigV19.WEBHOOK_URL);
                conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setConnectTimeout(9000);
                conn.setReadTimeout(9000);
                conn.setDoOutput(true);
                conn.setRequestProperty("Content-Type", "application/json; charset=utf-8");
                conn.setRequestProperty("Accept", "text/plain, application/json");
                conn.setRequestProperty("X-Probe-Schema", SCHEMA_VERSION);
                byte[] body = payload.toString().getBytes(StandardCharsets.UTF_8);
                conn.setFixedLengthStreamingMode(body.length);
                try (OutputStream os = conn.getOutputStream()) {
                    os.write(body);
                }
                int code = conn.getResponseCode();
                put19(result, "http_status", code);
                put19(result, "attempts", attempt);
                if (code >= 200 && code < 300) {
                    put19(result, "success", true);
                    return result;
                }
            } catch (Exception e) {
                put19(result, "error", e.getClass().getSimpleName());
                put19(result, "attempts", attempt);
            } finally {
                if (conn != null) conn.disconnect();
            }
            try { Thread.sleep(700L); }
            catch (InterruptedException e) { Thread.currentThread().interrupt(); break; }
        }
        put19(result, "success", false);
        return result;
    }

    private void waitUntil19(Condition condition, long timeoutMs, Runnable yes, Runnable timeout) {
        final long deadline = System.currentTimeMillis() + timeoutMs;
        Runnable checker = new Runnable() {
            @Override public void run() {
                if (!testRunning19) return;
                boolean ok = false;
                try { ok = condition.ok(); } catch (Exception ignored) {}
                if (ok) {
                    yes.run();
                    return;
                }
                if (System.currentTimeMillis() >= deadline) {
                    timeout.run();
                    return;
                }
                h19.postDelayed(this, 250L);
            }
        };
        h19.post(checker);
    }

    private JSONObject captureState19() {
        JSONObject o = new JSONObject();
        put19(o, "session_state", stringField19("sessionState"));
        put19(o, "mic_lease_mode", stringField19("micLeaseMode"));
        put19(o, "parent_last_action", stringField19("lastAction"));
        put19(o, "parent_last_action_status", stringField19("lastActionStatus"));
        put19(o, "parent_pending_present", field19("pending") != null);
        put19(o, "web_audio_permission_grants", intField19("permissionGrants"));
        put19(o, "web_audio_permission_denials", intField19("permissionDenials"));
        put19(o, "active_audio_tracks", intField19("activeAudioTracks"));
        put19(o, "media_gum_calls", intField19("mediaGumCalls"));
        put19(o, "media_gum_resolves", intField19("mediaGumResolves"));
        put19(o, "media_gum_rejects", intField19("mediaGumRejects"));

        put19(o, "snapshot_ok", boolField19("snapOk"));
        put19(o, "snapshot_ok_count", intField19("snapOkCount"));
        put19(o, "snapshot_fail_count", intField19("snapFailCount"));
        put19(o, "control_dictation_count", intField19("dictationCount"));
        put19(o, "control_stop_count", intField19("stopCount"));
        put19(o, "control_send_count", intField19("sendCount"));
        put19(o, "control_cancel_count", intField19("cancelCount"));
        put19(o, "composer_length", intField19("composerLen"));
        put19(o, "user_turn_count", intField19("userCount"));
        put19(o, "assistant_turn_count", intField19("assistantCount"));
        put19(o, "run_state", stringField19("runState18"));
        put19(o, "v18_pending_present", field19("pending18") != null);
        put19(o, "v18_last_action", stringField19("last18Action"));
        put19(o, "v18_last_status", stringField19("last18Status"));
        put19(o, "resolver_matches", intField19("lastResolverMatches"));
        put19(o, "resolver_visible_buttons", intField19("lastResolverVisibleButtons"));
        put19(o, "resolver_kinds", safeToken19(stringField19("lastResolverKinds")));
        put19(o, "forced_session_end_count", intField19("forcedSessionEnds"));
        put19(o, "session_end_reloaded", boolField19("lastSessionEndReloaded"));

        try {
            PackageInfo p = WebView.getCurrentWebViewPackage();
            if (p != null) {
                put19(o, "webview_package", p.packageName);
                put19(o, "webview_version", p.versionName);
            }
        } catch (Exception e) {
            put19(o, "webview_env_error", e.getClass().getSimpleName());
        }
        put19(o, "android_sdk", android.os.Build.VERSION.SDK_INT);
        put19(o, "android_release", android.os.Build.VERSION.RELEASE);
        return o;
    }

    private JSONObject clickButton19(String label) {
        Button b = findButton19(getWindow().getDecorView(), label);
        if (b == null) return clickResult19(label, false, false, false, "not_found");
        boolean enabled = b.isEnabled();
        boolean shown = b.isShown();
        boolean clicked = false;
        String error = "";
        try { clicked = b.performClick(); }
        catch (Exception e) { error = e.getClass().getSimpleName(); }
        return clickResult19(label, true, enabled, clicked, shown ? error : "not_shown" + (error.isEmpty() ? "" : "_" + error));
    }

    private JSONObject clickResult19(String label, boolean found, boolean enabled, boolean clicked, String note) {
        JSONObject o = new JSONObject();
        put19(o, "label", label);
        put19(o, "found", found);
        put19(o, "enabled", enabled);
        put19(o, "clicked", clicked);
        put19(o, "note", safeToken19(note));
        return o;
    }

    private Button findButton19(View v, String label) {
        if (v instanceof Button) {
            Button b = (Button) v;
            if (label.equals(String.valueOf(b.getText()))) return b;
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                Button found = findButton19(g.getChildAt(i), label);
                if (found != null) return found;
            }
        }
        return null;
    }

    private Object field19(String name) {
        Class<?> c = getClass();
        while (c != null) {
            try {
                Field f = c.getDeclaredField(name);
                f.setAccessible(true);
                return f.get(this);
            } catch (Exception ignored) {
                c = c.getSuperclass();
            }
        }
        return null;
    }

    private String stringField19(String name) {
        Object v = field19(name);
        return v == null ? "-" : String.valueOf(v);
    }

    private int intField19(String name) {
        Object v = field19(name);
        return v instanceof Number ? ((Number) v).intValue() : -1;
    }

    private boolean boolField19(String name) {
        Object v = field19(name);
        return v instanceof Boolean && (Boolean) v;
    }

    private WebView findWeb19(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb19(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }

    private void reportInterruptedRunIfNeeded19() {
        if (!prefs19.getBoolean("running", false)) return;
        String oldId = prefs19.getString("test_id", "-");
        int oldSeq = prefs19.getInt("seq", 0);
        String oldPhase = prefs19.getString("phase", "UNKNOWN");
        if ("-".equals(oldId) || !TelemetryConfigV19.isConfigured()) {
            prefs19.edit().putBoolean("running", false).apply();
            return;
        }
        JSONObject payload = new JSONObject();
        put19(payload, "kind", "TEST_PHASE");
        put19(payload, "schema_version", SCHEMA_VERSION);
        put19(payload, "scenario_id", SCENARIO_ID);
        put19(payload, "scenario_version", SCENARIO_VERSION);
        put19(payload, "test_id", oldId);
        put19(payload, "seq", oldSeq + 1);
        put19(payload, "phase", "RUN_INTERRUPTED_APP_RESTART");
        put19(payload, "classification", "INTERRUPTED");
        put19(payload, "previous_phase", safeToken19(oldPhase));
        put19(payload, "app_version", appVersion19());
        put19(payload, "source_ref", TelemetryConfigV19.SOURCE_REF);
        put19(payload, "state", captureState19());
        new Thread(() -> {
            uploadJson19(payload, 2);
            prefs19.edit().putBoolean("running", false).apply();
        }, "cp19-interruption").start();
        setAutoStatus19("Previous autonomous run was interrupted; interruption checkpoint sent. Run again when ready.");
    }

    private void persistRun19(boolean running, String phase) {
        prefs19.edit()
                .putBoolean("running", running)
                .putString("test_id", testId19)
                .putInt("seq", seq19)
                .putString("phase", phase)
                .putLong("started_at", startedAt19)
                .apply();
    }

    private void finishLocally19(boolean finalUploadSuccess) {
        testRunning19 = false;
        persistRun19(false, "COMPLETE");
        saveLocalReport19(finalUploadSuccess);
        if (runFullButton != null) {
            runFullButton.setEnabled(true);
            runFullButton.setText("RUN FULL TEST");
        }
        if (finalUploadSuccess) {
            setAutoStatus19("TEST COMPLETE - report uploaded. Tell ChatGPT: test finished");
        } else {
            setAutoStatus19("TEST COMPLETE - telemetry unavailable; local fallback report saved");
        }
    }

    private void saveLocalReport19(boolean uploadOk) {
        try {
            String name = "chatgpt-webview-v19-autonomous-"
                    + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".json";
            JSONObject out = new JSONObject();
            put19(out, "schema_version", SCHEMA_VERSION);
            put19(out, "scenario_id", SCENARIO_ID);
            put19(out, "scenario_version", SCENARIO_VERSION);
            put19(out, "test_id", testId19);
            put19(out, "final_classification", finalClassification19);
            put19(out, "stop_classification", stopClassification19);
            put19(out, "telemetry_preflight_passed", telemetryHealthy19);
            put19(out, "final_upload_success", uploadOk);
            put19(out, "source_ref", TelemetryConfigV19.SOURCE_REF);
            put19(out, "state", captureState19());
            put19(out, "event_tokens", localEvents.toString());

            ContentValues cv = new ContentValues();
            cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            cv.put(MediaStore.MediaColumns.MIME_TYPE, "application/json");
            cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (u == null) return;
            try (OutputStream os = getContentResolver().openOutputStream(u)) {
                if (os != null) os.write(out.toString(2).getBytes(StandardCharsets.UTF_8));
            }
        } catch (Exception ignored) {}
    }

    private void setAutoStatus19(String text) {
        if (autoStatus != null) autoStatus.setText(text);
        log19(safeToken19(text));
    }

    private void log19(String token) {
        if (localEvents.length() > 8000) localEvents.delete(0, Math.min(3000, localEvents.length()));
        localEvents.append(System.currentTimeMillis()).append('|').append(safeToken19(token)).append('\n');
    }

    private String safeToken19(String s) {
        if (s == null) return "-";
        String x = s.replaceAll("[^A-Za-z0-9_.,:=+/-]", "_");
        return x.length() > 180 ? x.substring(0, 180) : x;
    }

    private String appVersion19() {
        try {
            return getPackageManager().getPackageInfo(getPackageName(), 0).versionName;
        } catch (Exception e) {
            return "0.19";
        }
    }

    private int dp19(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    private void put19(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) {}
    }
}
