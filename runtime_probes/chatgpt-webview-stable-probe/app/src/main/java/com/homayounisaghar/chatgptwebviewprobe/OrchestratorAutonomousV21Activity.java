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
import org.json.JSONTokener;

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
 * Stable v0.21 - production-facing active-Dictation semantic adapter plus
 * one-tap autonomous proof.
 *
 * v0.20 identified exact active controls:
 *   aria-label="Cancel dictation"
 *   aria-label="Submit dictation"
 * and proved that the old generic /submit/ -> SEND classifier was the reason
 * Dictation.Stop could never resolve after Start.
 *
 * This version retargets D STOP to exactly one visible "Submit dictation" and
 * D CANCEL to exactly one visible "Cancel dictation". The autonomous scenario
 * starts a silent Dictation, invokes D STOP exactly once, confirms an observable
 * exit from active recording, verifies that no ChatGPT user turn was created,
 * then performs unconditional Session recovery.
 */
public class OrchestratorAutonomousV21Activity extends OrchestratorFoundationV18Activity {
    private static final String PREFS21 = "stable_v21_dictation_submit";
    private static final String SCHEMA_VERSION = "cp-autonomous-runtime-v1";
    private static final String SCENARIO_ID = "dictation-submit-stop-proof";
    private static final int SCENARIO_VERSION = 1;

    private final Handler h21 = new Handler(Looper.getMainLooper());
    private final StringBuilder localEvents21 = new StringBuilder();

    private SharedPreferences prefs21;
    private WebView web21;
    private Button runButton21;
    private TextView status21;

    private boolean running21 = false;
    private boolean telemetryHealthy21 = false;
    private String testId21 = "-";
    private int seq21 = 0;
    private long startedAt21 = 0L;
    private String finalClassification21 = "NOT_RUN";
    private String stopClassification21 = "NOT_RUN";
    private int baselineUserTurns21 = -1;

    // Production-facing adapter state.
    private boolean actionPending21 = false;
    private String action21 = "NONE";
    private String actionStatus21 = "NOT_RUN";
    private String claimId21 = "-";
    private int resolverMatches21 = -1;
    private int resolverVisibleButtons21 = -1;
    private boolean submitClicked21 = false;
    private int receiptSubmitCount21 = -1;
    private int receiptCancelCount21 = -1;
    private int receiptReadyCount21 = -1;
    private int receiptUserTurns21 = -1;

    private interface UploadCallback21 { void done(JSONObject result); }
    private interface Condition21 { boolean ok(); }
    private interface JsonCallback21 { void done(JSONObject result); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs21 = getSharedPreferences(PREFS21, MODE_PRIVATE);
        web21 = findWeb21(getWindow().getDecorView());
        if (web21 != null) web21.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        retargetDictationButtons21(getWindow().getDecorView());
        installHarnessPanel21();
        reportInterruptedRunIfNeeded21();
    }

    private void retargetDictationButtons21(View v) {
        if (v instanceof Button) {
            Button b = (Button) v;
            String t = String.valueOf(b.getText());
            if ("D STOP".equals(t)) b.setOnClickListener(x -> dispatchActiveDictation21("DICTATION_STOP"));
            if ("D CANCEL".equals(t)) b.setOnClickListener(x -> dispatchActiveDictation21("DICTATION_CANCEL"));
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) retargetDictationButtons21(g.getChildAt(i));
        }
    }

    private void installHarnessPanel21() {
        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) content;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        int wi = web21 == null ? 0 : root.indexOfChild(web21);
        if (wi < 0) wi = 0;

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp21(6), dp21(3), dp21(6), dp21(3));

        runButton21 = new Button(this);
        runButton21.setText("RUN FULL TEST");
        runButton21.setTextSize(14f);
        runButton21.setAllCaps(false);
        runButton21.setOnClickListener(v -> runFullTest21());
        panel.addView(runButton21, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp21(52)));

        status21 = new TextView(this);
        status21.setTextSize(10f);
        status21.setText("v0.21 Dictation Submit semantic proof ready");
        status21.setPadding(dp21(6), dp21(3), dp21(6), dp21(3));
        panel.addView(status21, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));

        root.addView(panel, wi, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    // ---------------------------------------------------------------------
    // Production-facing active Dictation adapter
    // ---------------------------------------------------------------------

    private void dispatchActiveDictation21(String requestedAction) {
        if (!"ACTIVE".equals(stringField21("sessionState"))) {
            adapterBlock21(requestedAction, "SESSION_NOT_ACTIVE");
            return;
        }
        if (!"DICTATION".equals(stringField21("micLeaseMode"))) {
            adapterBlock21(requestedAction, "NO_DICTATION_LEASE");
            return;
        }
        if (actionPending21) {
            adapterBlock21(requestedAction, "ACTION_PENDING_" + action21);
            return;
        }
        if (web21 == null) {
            adapterBlock21(requestedAction, "WEBVIEW_MISSING");
            return;
        }

        final String label;
        if ("DICTATION_STOP".equals(requestedAction)) label = DictationActiveControlsV21.SUBMIT_LABEL;
        else if ("DICTATION_CANCEL".equals(requestedAction)) label = DictationActiveControlsV21.CANCEL_LABEL;
        else {
            adapterBlock21(requestedAction, "UNSUPPORTED");
            return;
        }

        claimId21 = requestedAction + "_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0, 8);
        boolean durable = prefs21.edit()
                .putString("claim_id", claimId21)
                .putString("claim_action", requestedAction)
                .putString("claim_status", "CLAIMED")
                .commit();
        if (!durable) {
            adapterBlock21(requestedAction, "DURABLE_CLAIM_WRITE_FAIL");
            return;
        }

        actionPending21 = true;
        action21 = requestedAction;
        actionStatus21 = "DURABLE_CLAIMED";
        resolverMatches21 = -1;
        resolverVisibleButtons21 = -1;
        submitClicked21 = false;
        receiptSubmitCount21 = -1;
        receiptCancelCount21 = -1;
        receiptReadyCount21 = -1;
        receiptUserTurns21 = -1;
        int baseline = intField21("userCount");
        log21(requestedAction + " DURABLE_CLAIMED label=" + label);

        web21.evaluateJavascript(DictationActiveControlsV21.clickExactLabelJs(label), value -> {
            JSONObject out = decodeJson21(value);
            resolverMatches21 = out.optInt("matches", -1);
            resolverVisibleButtons21 = out.optInt("visible_buttons", -1);
            boolean clicked = out.optBoolean("clicked", false);
            submitClicked21 = clicked;
            if (resolverMatches21 != 1 || !clicked) {
                actionPending21 = false;
                actionStatus21 = "ABORTED_NO_SIDE_EFFECT_MATCHES_" + resolverMatches21;
                prefs21.edit().putString("claim_status", "ABORTED_NO_SIDE_EFFECT").commit();
                log21(requestedAction + " " + actionStatus21);
                return;
            }
            actionStatus21 = "DISPATCHED_WAITING_RECEIPT";
            prefs21.edit().putString("claim_status", "DISPATCHED").commit();
            log21(requestedAction + " SINGLE_EXACT_ARIA_CLICK");
            pollActiveExitReceipt21(requestedAction, baseline, System.currentTimeMillis() + 12000L);
        });
    }

    private void pollActiveExitReceipt21(String requestedAction, int baselineUserTurns, long deadline) {
        if (!actionPending21 || !requestedAction.equals(action21) || web21 == null) return;
        web21.evaluateJavascript(DictationActiveControlsV21.stateJs(), value -> {
            JSONObject s = decodeJson21(value);
            if (!s.optBoolean("success", false)) {
                if (System.currentTimeMillis() >= deadline) adapterUncertain21("STATE_READ_TIMEOUT");
                else h21.postDelayed(() -> pollActiveExitReceipt21(requestedAction, baselineUserTurns, deadline), 300L);
                return;
            }
            receiptSubmitCount21 = s.optInt("submit_count", -1);
            receiptCancelCount21 = s.optInt("cancel_count", -1);
            receiptReadyCount21 = s.optInt("ready_dictation_count", -1);
            receiptUserTurns21 = s.optInt("user_turn_count", -1);

            if (baselineUserTurns >= 0 && receiptUserTurns21 > baselineUserTurns) {
                actionPending21 = false;
                actionStatus21 = "UNEXPECTED_USER_TURN_AFTER_" + requestedAction;
                prefs21.edit().putString("claim_status", "UNEXPECTED_SIDE_EFFECT").commit();
                log21(actionStatus21);
                return;
            }

            boolean activeGone = receiptSubmitCount21 == 0 && receiptCancelCount21 == 0;
            boolean readyReturned = receiptReadyCount21 >= 1 || intField21("dictationCount") >= 1;
            if (activeGone && readyReturned) {
                adapterConfirm21(requestedAction, "ACTIVE_DICTATION_EXIT_READY_RETURNED");
                return;
            }
            if (System.currentTimeMillis() >= deadline) {
                adapterUncertain21("EXIT_RECEIPT_TIMEOUT");
                return;
            }
            h21.postDelayed(() -> pollActiveExitReceipt21(requestedAction, baselineUserTurns, deadline), 300L);
        });
    }

    private void adapterConfirm21(String requestedAction, String receipt) {
        actionPending21 = false;
        action21 = requestedAction;
        actionStatus21 = "CONFIRMED_" + receipt;
        prefs21.edit().putString("claim_status", "CONFIRMED").putString("claim_receipt", receipt).commit();
        setField21("micLeaseMode", "NONE");
        setField21("micLeaseUntil", 0L);
        setField21("lastAction", requestedAction);
        setField21("lastActionStatus", "CONFIRMED_V21_" + receipt);
        setField21("last18Action", requestedAction);
        setField21("last18Status", "CONFIRMED_V21_" + receipt);
        log21(requestedAction + " CONFIRMED " + receipt);
    }

    private void adapterUncertain21(String reason) {
        actionPending21 = false;
        actionStatus21 = "UNCERTAIN_" + reason;
        prefs21.edit().putString("claim_status", "UNCERTAIN").putString("claim_receipt", reason).commit();
        log21(action21 + " UNCERTAIN " + reason);
    }

    private void adapterBlock21(String requestedAction, String reason) {
        action21 = requestedAction;
        actionStatus21 = "BLOCKED_" + reason;
        log21(requestedAction + " BLOCKED " + reason);
    }

    // ---------------------------------------------------------------------
    // Autonomous proof harness
    // ---------------------------------------------------------------------

    private void runFullTest21() {
        if (running21) return;
        running21 = true;
        telemetryHealthy21 = false;
        testId21 = "cp21-" + UUID.randomUUID();
        seq21 = 0;
        startedAt21 = System.currentTimeMillis();
        finalClassification21 = "RUNNING";
        stopClassification21 = "NOT_RUN";
        baselineUserTurns21 = -1;
        localEvents21.setLength(0);
        if (runButton21 != null) {
            runButton21.setEnabled(false);
            runButton21.setText("RUNNING...");
        }
        persistRun21(true, "STARTING");
        setStatus21("Telemetry preflight...");

        JSONObject pre = captureState21();
        put21(pre, "preflight", true);
        postPhase21("TELEMETRY_PREFLIGHT", "RUNNING", pre, result -> {
            if (!result.optBoolean("success", false)) {
                telemetryHealthy21 = false;
                finalClassification21 = "TELEMETRY_UNAVAILABLE";
                finishLocally21(false);
                return;
            }
            telemetryHealthy21 = true;
            postRequiredPhase21("RUN_STARTED", "RUNNING", captureState21(), this::waitForBaseline21);
        });
    }

    private void waitForBaseline21() {
        setStatus21("Waiting for stable snapshot...");
        waitUntil21(() -> boolField21("snapOk"), 4000L,
                () -> postRequiredPhase21("BASELINE_READY", "RUNNING", captureState21(), this::startSession21),
                () -> {
                    finalClassification21 = "SNAPSHOT_NOT_READY";
                    postPhase21("BASELINE_TIMEOUT", "FAIL", captureState21(), r -> recoverSession21());
                });
    }

    private void startSession21() {
        setStatus21("Starting InteractionSession...");
        JSONObject click = clickButton21("SESSION START");
        JSONObject state = captureState21();
        put21(state, "click", click);
        postRequiredPhase21("SESSION_START_DISPATCH", "RUNNING", state, () ->
                waitUntil21(() -> "ACTIVE".equals(stringField21("sessionState")), 4000L,
                        () -> postRequiredPhase21("SESSION_ACTIVE", "RUNNING", captureState21(), this::startDictation21),
                        () -> {
                            finalClassification21 = "SESSION_START_FAILED";
                            postPhase21("SESSION_START_TIMEOUT", "FAIL", captureState21(), r -> recoverSession21());
                        }));
    }

    private void startDictation21() {
        setStatus21("Starting silent Dictation once...");
        postRequiredPhase21("BEFORE_DICTATION_START", "RUNNING", captureState21(), () -> {
            JSONObject click = clickButton21("D START");
            JSONObject state = captureState21();
            put21(state, "click", click);
            postRequiredPhase21("DICTATION_START_DISPATCH", "RUNNING", state, () ->
                    waitUntil21(this::dictationStartObserved21, 5500L,
                            () -> h21.postDelayed(this::verifyActiveControls21, 1000L),
                            () -> {
                                finalClassification21 = "DICTATION_START_FAILED";
                                postPhase21("DICTATION_START_TIMEOUT", "FAIL", captureState21(), r -> recoverSession21());
                            }));
        });
    }

    private boolean dictationStartObserved21() {
        String lease = stringField21("micLeaseMode");
        String parentStatus = stringField21("lastActionStatus");
        String wrapperStatus = stringField21("lastWrapperStatus");
        return "DICTATION".equals(lease)
                && (parentStatus.contains("CONFIRMED")
                || parentStatus.contains("ACCEPTED_REVERSIBLE_START")
                || wrapperStatus.contains("CONFIRMED")
                || wrapperStatus.contains("ACCEPTED_REVERSIBLE_START"));
    }

    private void verifyActiveControls21() {
        setStatus21("Verifying exact active Dictation controls...");
        readActiveState21(active -> {
            JSONObject state = captureState21();
            put21(state, "active_semantics", active);
            int submit = active.optInt("submit_count", -1);
            int cancel = active.optInt("cancel_count", -1);
            baselineUserTurns21 = active.optInt("user_turn_count", intField21("userCount"));
            if (!active.optBoolean("success", false) || submit != 1 || cancel != 1) {
                finalClassification21 = "ACTIVE_SEMANTICS_NOT_UNIQUE";
                postPhase21("ACTIVE_SEMANTIC_CHECK", "FAIL", state, r -> recoverSession21());
                return;
            }
            postRequiredPhase21("ACTIVE_SEMANTIC_CHECK", "UNIQUE_SUBMIT_AND_CANCEL", state, this::beforeStop21);
        });
    }

    private void beforeStop21() {
        setStatus21("Checkpointing before Dictation Stop...");
        readActiveState21(active -> {
            JSONObject state = captureState21();
            put21(state, "active_semantics", active);
            postRequiredPhase21("BEFORE_DICTATION_STOP", "RUNNING", state, this::dispatchStop21);
        });
    }

    private void dispatchStop21() {
        setStatus21("Stopping Dictation via exact Submit dictation semantic...");
        JSONObject click = clickButton21("D STOP");
        JSONObject state = captureState21();
        put21(state, "native_click", click);
        postRequiredPhase21("DICTATION_STOP_DISPATCH", "RUNNING", state, () ->
                waitUntil21(this::stopTerminal21, 13000L,
                        () -> finishStopResult21(false),
                        () -> finishStopResult21(true)));
    }

    private boolean stopTerminal21() {
        if (!"DICTATION_STOP".equals(action21)) return false;
        return actionStatus21.startsWith("CONFIRMED")
                || actionStatus21.startsWith("ABORTED")
                || actionStatus21.startsWith("BLOCKED")
                || actionStatus21.startsWith("UNCERTAIN")
                || actionStatus21.startsWith("UNEXPECTED");
    }

    private void finishStopResult21(boolean timedOut) {
        readActiveState21(active -> {
            int userTurns = active.optInt("user_turn_count", intField21("userCount"));
            boolean noMessage = baselineUserTurns21 < 0 || userTurns <= baselineUserTurns21;
            if (actionStatus21.startsWith("CONFIRMED") && noMessage) {
                stopClassification21 = "STOP_CONFIRMED_NO_MESSAGE";
            } else if (!noMessage || actionStatus21.startsWith("UNEXPECTED")) {
                stopClassification21 = "UNEXPECTED_MESSAGE_SIDE_EFFECT";
            } else if (timedOut) {
                stopClassification21 = "STOP_TIMEOUT";
            } else if (actionStatus21.startsWith("ABORTED")) {
                stopClassification21 = "STOP_ABORTED";
            } else if (actionStatus21.startsWith("BLOCKED")) {
                stopClassification21 = "STOP_BLOCKED";
            } else if (actionStatus21.startsWith("UNCERTAIN")) {
                stopClassification21 = "STOP_UNCERTAIN";
            } else {
                stopClassification21 = "STOP_OTHER";
            }
            JSONObject state = captureState21();
            put21(state, "active_semantics_after_stop", active);
            put21(state, "baseline_user_turns", baselineUserTurns21);
            put21(state, "no_message_side_effect", noMessage);
            put21(state, "timed_out", timedOut);
            put21(state, "stop_classification", stopClassification21);
            postPhase21("DICTATION_STOP_RESULT", stopClassification21, state, r -> recoverSession21());
        });
    }

    private void recoverSession21() {
        setStatus21("Recovering session...");
        JSONObject before = captureState21();
        postPhase21("BEFORE_RECOVERY", "RUNNING", before, r -> {
            JSONObject click;
            if ("ACTIVE".equals(stringField21("sessionState"))) click = clickButton21("SESSION END");
            else click = clickResult21("SESSION END", false, false, "already_not_active");
            JSONObject after = captureState21();
            put21(after, "click", click);
            postPhase21("RECOVERY_DISPATCH", "RUNNING", after, x ->
                    waitUntil21(this::recoveryComplete21, 5000L,
                            () -> finishAfterRecovery21(true),
                            () -> finishAfterRecovery21(false)));
        });
    }

    private boolean recoveryComplete21() {
        return "IDLE".equals(stringField21("sessionState"))
                && "NONE".equals(stringField21("micLeaseMode"));
    }

    private void finishAfterRecovery21(boolean recovered) {
        if ("RUNNING".equals(finalClassification21)) {
            if ("STOP_CONFIRMED_NO_MESSAGE".equals(stopClassification21) && recovered) {
                finalClassification21 = "PASS_DICTATION_STOP_SUBMIT_SEMANTIC_RECOVERED";
            } else {
                finalClassification21 = stopClassification21 + (recovered ? "_RECOVERED" : "_RECOVERY_FAILED");
            }
        } else {
            finalClassification21 = finalClassification21 + (recovered ? "_RECOVERED" : "_RECOVERY_FAILED");
        }
        JSONObject state = captureState21();
        put21(state, "recovered", recovered);
        put21(state, "stop_classification", stopClassification21);
        put21(state, "final_classification", finalClassification21);
        postPhase21("RECOVERY_RESULT", recovered ? "RECOVERED" : "RECOVERY_FAILED", state, r ->
                postPhase21("FINAL", finalClassification21, captureState21(), finalUpload ->
                        finishLocally21(finalUpload.optBoolean("success", false))));
    }

    // ---------------------------------------------------------------------
    // Telemetry, state, persistence and helpers
    // ---------------------------------------------------------------------

    private void readActiveState21(JsonCallback21 callback) {
        if (web21 == null) {
            JSONObject o = new JSONObject();
            put21(o, "success", false);
            put21(o, "error", "WebViewMissing");
            callback.done(o);
            return;
        }
        web21.evaluateJavascript(DictationActiveControlsV21.stateJs(), value -> callback.done(decodeJson21(value)));
    }

    private void postRequiredPhase21(String phase, String classification, JSONObject state, Runnable next) {
        postPhase21(phase, classification, state, result -> {
            if (!result.optBoolean("success", false)) {
                telemetryHealthy21 = false;
                if ("RUNNING".equals(finalClassification21)) finalClassification21 = "TELEMETRY_LOST_AT_" + phase;
                recoverSession21();
                return;
            }
            next.run();
        });
    }

    private void postPhase21(String phase, String classification, JSONObject state, UploadCallback21 callback) {
        int seq = ++seq21;
        persistRun21(true, phase);
        JSONObject payload = new JSONObject();
        put21(payload, "kind", "TEST_PHASE");
        put21(payload, "schema_version", SCHEMA_VERSION);
        put21(payload, "scenario_id", SCENARIO_ID);
        put21(payload, "scenario_version", SCENARIO_VERSION);
        put21(payload, "test_id", testId21);
        put21(payload, "seq", seq);
        put21(payload, "phase", phase);
        put21(payload, "classification", classification);
        put21(payload, "app_version", appVersion21());
        put21(payload, "source_ref", TelemetryConfigV21.SOURCE_REF);
        put21(payload, "collector_id", TelemetryConfigV21.COLLECTOR_ID);
        put21(payload, "elapsed_ms", startedAt21 == 0L ? 0L : System.currentTimeMillis() - startedAt21);
        put21(payload, "timestamp_epoch_ms", System.currentTimeMillis());
        put21(payload, "privacy", "semantic_counts_receipts_no_raw_audio_speech_chat_or_credentials");
        put21(payload, "state", state == null ? new JSONObject() : state);
        log21("PHASE " + seq + " " + phase + " " + classification);

        new Thread(() -> {
            JSONObject result = uploadJson21(payload, 2);
            runOnUiThread(() -> callback.done(result));
        }, "cp21-telemetry-" + seq).start();
    }

    private JSONObject uploadJson21(JSONObject payload, int attempts) {
        JSONObject result = new JSONObject();
        put21(result, "configured", TelemetryConfigV21.isConfigured());
        if (!TelemetryConfigV21.isConfigured()) {
            put21(result, "success", false);
            put21(result, "error", "TelemetryNotConfigured");
            return result;
        }
        for (int attempt = 1; attempt <= attempts; attempt++) {
            HttpURLConnection conn = null;
            try {
                URL url = new URL(TelemetryConfigV21.WEBHOOK_URL);
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
                try (OutputStream os = conn.getOutputStream()) { os.write(body); }
                int code = conn.getResponseCode();
                put21(result, "http_status", code);
                put21(result, "attempts", attempt);
                if (code >= 200 && code < 300) {
                    put21(result, "success", true);
                    return result;
                }
            } catch (Exception e) {
                put21(result, "error", e.getClass().getSimpleName());
                put21(result, "attempts", attempt);
            } finally {
                if (conn != null) conn.disconnect();
            }
            try { Thread.sleep(900L); }
            catch (InterruptedException e) { Thread.currentThread().interrupt(); break; }
        }
        put21(result, "success", false);
        return result;
    }

    private JSONObject captureState21() {
        JSONObject o = new JSONObject();
        put21(o, "session_state", stringField21("sessionState"));
        put21(o, "mic_lease_mode", stringField21("micLeaseMode"));
        put21(o, "snapshot_ok", boolField21("snapOk"));
        put21(o, "dictation_count", intField21("dictationCount"));
        put21(o, "stop_count", intField21("stopCount"));
        put21(o, "send_count_legacy", intField21("sendCount"));
        put21(o, "cancel_count_legacy", intField21("cancelCount"));
        put21(o, "user_turn_count", intField21("userCount"));
        put21(o, "parent_last_action", stringField21("lastAction"));
        put21(o, "parent_last_status", stringField21("lastActionStatus"));
        put21(o, "wrapper_last_status", stringField21("lastWrapperStatus"));
        put21(o, "v18_last_action", stringField21("last18Action"));
        put21(o, "v18_last_status", stringField21("last18Status"));
        put21(o, "forced_session_end_count", intField21("forcedSessionEnds"));
        put21(o, "adapter_action", action21);
        put21(o, "adapter_status", actionStatus21);
        put21(o, "adapter_pending", actionPending21);
        put21(o, "adapter_claim_present", !"-".equals(claimId21));
        put21(o, "resolver_matches", resolverMatches21);
        put21(o, "resolver_visible_buttons", resolverVisibleButtons21);
        put21(o, "semantic_click_dispatched", submitClicked21);
        put21(o, "receipt_submit_count", receiptSubmitCount21);
        put21(o, "receipt_cancel_count", receiptCancelCount21);
        put21(o, "receipt_ready_count", receiptReadyCount21);
        put21(o, "receipt_user_turns", receiptUserTurns21);
        put21(o, "telemetry_healthy", telemetryHealthy21);
        put21(o, "raw_audio_retained", false);
        put21(o, "raw_speech_retained", false);
        put21(o, "raw_chat_text_retained", false);
        put21(o, "private_chatgpt_api_used", false);
        put21(o, "coordinate_action_used", false);
        return o;
    }

    private JSONObject clickButton21(String exactText) {
        JSONObject out = new JSONObject();
        Button b = findButton21(getWindow().getDecorView(), exactText);
        put21(out, "requested", exactText);
        put21(out, "found", b != null);
        if (b == null) {
            put21(out, "clicked", false);
            put21(out, "reason", "button_not_found");
            return out;
        }
        boolean enabled = b.isEnabled();
        boolean visible = b.getVisibility() == View.VISIBLE;
        put21(out, "enabled", enabled);
        put21(out, "visible", visible);
        boolean clicked = false;
        if (enabled && visible) {
            try { clicked = b.performClick(); }
            catch (Exception ignored) { }
        }
        put21(out, "clicked", clicked);
        return out;
    }

    private JSONObject clickResult21(String requested, boolean found, boolean clicked, String reason) {
        JSONObject out = new JSONObject();
        put21(out, "requested", requested);
        put21(out, "found", found);
        put21(out, "clicked", clicked);
        put21(out, "reason", reason);
        return out;
    }

    private Button findButton21(View v, String exactText) {
        if (v instanceof Button) {
            Button b = (Button) v;
            if (exactText.equals(String.valueOf(b.getText()))) return b;
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                Button b = findButton21(g.getChildAt(i), exactText);
                if (b != null) return b;
            }
        }
        return null;
    }

    private void waitUntil21(Condition21 condition, long timeoutMs, Runnable success, Runnable timeout) {
        final long start = System.currentTimeMillis();
        final Runnable[] poll = new Runnable[1];
        poll[0] = () -> {
            if (!running21) return;
            boolean ok = false;
            try { ok = condition.ok(); } catch (Exception ignored) { }
            if (ok) { success.run(); return; }
            if (System.currentTimeMillis() - start >= timeoutMs) { timeout.run(); return; }
            h21.postDelayed(poll[0], 250L);
        };
        h21.post(poll[0]);
    }

    private void reportInterruptedRunIfNeeded21() {
        if (!prefs21.getBoolean("run_active", false)) return;
        String oldId = prefs21.getString("test_id", "cp21-interrupted-unknown");
        int oldSeq = prefs21.getInt("seq", 0);
        long oldStart = prefs21.getLong("started_at", System.currentTimeMillis());
        String oldPhase = prefs21.getString("phase", "UNKNOWN");
        testId21 = oldId;
        seq21 = oldSeq;
        startedAt21 = oldStart;
        JSONObject state = captureState21();
        put21(state, "interrupted_after_phase", oldPhase);
        postPhase21("RUN_INTERRUPTED_APP_RESTART", "FAIL", state, r -> {
            prefs21.edit().putBoolean("run_active", false).apply();
            setStatus21("Previous run interruption reported. Ready for a new test.");
        });
    }

    private void persistRun21(boolean active, String phase) {
        prefs21.edit()
                .putBoolean("run_active", active)
                .putString("test_id", testId21)
                .putInt("seq", seq21)
                .putLong("started_at", startedAt21)
                .putString("phase", phase)
                .apply();
    }

    private void finishLocally21(boolean finalUploadOk) {
        running21 = false;
        persistRun21(false, "FINISHED");
        if (runButton21 != null) {
            runButton21.setEnabled(true);
            runButton21.setText("RUN AGAIN");
        }
        if (finalUploadOk) setStatus21("TEST COMPLETE - report uploaded. Tell ChatGPT: test finished");
        else {
            saveFallback21();
            setStatus21("TEST COMPLETE - telemetry unavailable; local fallback saved");
        }
    }

    private void saveFallback21() {
        try {
            JSONObject o = captureState21();
            put21(o, "test_id", testId21);
            put21(o, "final_classification", finalClassification21);
            put21(o, "events", localEvents21.toString());
            String name = "chatgpt-webview-v21-fallback-"
                    + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".json";
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            cv.put(MediaStore.MediaColumns.MIME_TYPE, "application/json");
            cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (u == null) return;
            try (OutputStream os = getContentResolver().openOutputStream(u)) {
                if (os != null) os.write(o.toString(2).getBytes(StandardCharsets.UTF_8));
            }
            Toast.makeText(this, "v0.21 fallback saved to Downloads", Toast.LENGTH_LONG).show();
        } catch (Exception ignored) { }
    }

    private String appVersion21() {
        try {
            PackageInfo pi = getPackageManager().getPackageInfo(getPackageName(), 0);
            return pi.versionName + "(" + pi.getLongVersionCode() + ")";
        } catch (Exception e) { return "unknown"; }
    }

    private WebView findWeb21(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb21(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }

    private Field field21(String name) {
        Class<?> c = getClass();
        while (c != null) {
            try {
                Field f = c.getDeclaredField(name);
                f.setAccessible(true);
                return f;
            } catch (Exception ignored) { c = c.getSuperclass(); }
        }
        return null;
    }

    private String stringField21(String name) {
        try {
            Field f = field21(name);
            if (f == null) return "UNKNOWN";
            Object v = f.get(this);
            return v == null ? "NONE" : String.valueOf(v);
        } catch (Exception e) { return "ERROR"; }
    }

    private int intField21(String name) {
        try {
            Field f = field21(name);
            return f == null ? -1 : f.getInt(this);
        } catch (Exception e) { return -1; }
    }

    private boolean boolField21(String name) {
        try {
            Field f = field21(name);
            return f != null && f.getBoolean(this);
        } catch (Exception e) { return false; }
    }

    private void setField21(String name, Object value) {
        try {
            Field f = field21(name);
            if (f != null) f.set(this, value);
        } catch (Exception ignored) { }
    }

    private JSONObject decodeJson21(String value) {
        try {
            Object x = new JSONTokener(value == null ? "null" : value).nextValue();
            if (x instanceof String) x = new JSONTokener((String) x).nextValue();
            if (x instanceof JSONObject) return (JSONObject) x;
        } catch (Exception ignored) { }
        JSONObject o = new JSONObject();
        put21(o, "success", false);
        put21(o, "error", "DecodeFailed");
        return o;
    }

    private int dp21(int x) { return Math.round(x * getResources().getDisplayMetrics().density); }

    private void setStatus21(String s) {
        runOnUiThread(() -> { if (status21 != null) status21.setText(s); });
        log21("STATUS " + s);
    }

    private void log21(String s) {
        String safe = s == null ? "" : s.replace('\n', ' ');
        if (safe.length() > 700) safe = safe.substring(0, 700);
        if (localEvents21.length() < 24000) localEvents21.append(System.currentTimeMillis()).append(" | ").append(safe).append('\n');
    }

    private void put21(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) { }
    }

    @Override protected void onDestroy() {
        h21.removeCallbacksAndMessages(null);
        super.onDestroy();
    }
}
