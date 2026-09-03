package com.homayounisaghar.chatgptwebviewprobe;

import android.content.ContentValues;
import android.content.SharedPreferences;
import android.content.pm.PackageInfo;
import android.media.AudioManager;
import android.media.ToneGenerator;
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
 * Stable v0.22 - autonomous end-to-end Dictation lifecycle proof.
 *
 * Proven inputs:
 * - v0.21: Dictation.Stop == exact aria-label "Submit dictation" and exits
 *   active recording without sending a ChatGPT message.
 * - v0.20: Dictation.Cancel == exact aria-label "Cancel dictation".
 *
 * This build proves two production-facing flows behind the Orchestrator:
 * 1) Start -> Cancel, with no message and no draft side effect.
 * 2) Start -> user speaks during a fixed window -> Stop/Submit -> transcript
 *    becomes a non-empty composer draft -> D SEND exactly once -> user-turn
 *    receipt and composer clears.
 *
 * The harness never uploads raw audio, speech, transcript/chat text, cookies,
 * tokens or credentials. Telemetry contains only counts, lengths, hashes,
 * semantic receipts and classifications.
 */
public class OrchestratorAutonomousV22Activity extends OrchestratorFoundationV18Activity {
    private static final String PREFS22 = "stable_v22_dictation_e2e";
    private static final String SCHEMA_VERSION = "cp-autonomous-runtime-v1";
    private static final String SCENARIO_ID = "dictation-cancel-stop-transcript-send-e2e";
    private static final int SCENARIO_VERSION = 1;
    private static final long SPEAK_WINDOW_MS = 6500L;

    private final Handler h22 = new Handler(Looper.getMainLooper());
    private final StringBuilder localEvents22 = new StringBuilder();

    private SharedPreferences prefs22;
    private WebView web22;
    private Button runButton22;
    private TextView status22;

    private boolean running22 = false;
    private boolean telemetryHealthy22 = false;
    private String testId22 = "-";
    private int seq22 = 0;
    private long startedAt22 = 0L;
    private String finalClassification22 = "NOT_RUN";
    private String cancelClassification22 = "NOT_RUN";
    private String stopClassification22 = "NOT_RUN";
    private String transcriptClassification22 = "NOT_RUN";
    private String sendClassification22 = "NOT_RUN";

    // Active-Dictation adapter operation state.
    private boolean adapterPending22 = false;
    private String adapterAction22 = "NONE";
    private String adapterStatus22 = "NOT_RUN";
    private String adapterClaim22 = "-";
    private int adapterMatches22 = -1;
    private int adapterVisibleButtons22 = -1;
    private boolean adapterClicked22 = false;
    private int adapterSubmitCount22 = -1;
    private int adapterCancelCount22 = -1;
    private int adapterReadyCount22 = -1;
    private int adapterUserTurns22 = -1;

    private int cancelBaselineUsers22 = -1;
    private int cancelBaselineComposerLen22 = -1;
    private String cancelBaselineComposerHash22 = "-";

    private int spokenBaselineUsers22 = -1;
    private int sendBaselineUsers22 = -1;
    private int transcriptLen22 = -1;
    private String transcriptHash22 = "-";

    private interface UploadCallback22 { void done(JSONObject result); }
    private interface Condition22 { boolean ok(); }
    private interface JsonCallback22 { void done(JSONObject result); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs22 = getSharedPreferences(PREFS22, MODE_PRIVATE);
        web22 = findWeb22(getWindow().getDecorView());
        if (web22 != null) {
            web22.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        }
        retargetDictationButtons22(getWindow().getDecorView());
        installHarnessPanel22();
        reportInterruptedRunIfNeeded22();
    }

    private void retargetDictationButtons22(View v) {
        if (v instanceof Button) {
            Button b = (Button) v;
            String t = String.valueOf(b.getText());
            if ("D STOP".equals(t)) b.setOnClickListener(x -> dispatchActiveDictation22("DICTATION_STOP"));
            if ("D CANCEL".equals(t)) b.setOnClickListener(x -> dispatchActiveDictation22("DICTATION_CANCEL"));
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) retargetDictationButtons22(g.getChildAt(i));
        }
    }

    private void installHarnessPanel22() {
        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) content;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        int wi = web22 == null ? 0 : root.indexOfChild(web22);
        if (wi < 0) wi = 0;

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp22(6), dp22(3), dp22(6), dp22(3));

        runButton22 = new Button(this);
        runButton22.setText("RUN FULL TEST");
        runButton22.setTextSize(14f);
        runButton22.setAllCaps(false);
        runButton22.setOnClickListener(v -> runFullTest22());
        panel.addView(runButton22, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp22(52)));

        status22 = new TextView(this);
        status22.setTextSize(12f);
        status22.setText("v0.22 Dictation lifecycle E2E ready");
        status22.setPadding(dp22(6), dp22(4), dp22(6), dp22(5));
        panel.addView(status22, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));

        root.addView(panel, wi, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    // ---------------------------------------------------------------------
    // Production-facing active Dictation adapter
    // ---------------------------------------------------------------------

    private void dispatchActiveDictation22(String requestedAction) {
        if (!"ACTIVE".equals(stringField22("sessionState"))) {
            adapterBlock22(requestedAction, "SESSION_NOT_ACTIVE");
            return;
        }
        if (!"DICTATION".equals(stringField22("micLeaseMode"))) {
            adapterBlock22(requestedAction, "NO_DICTATION_LEASE");
            return;
        }
        if (adapterPending22) {
            adapterBlock22(requestedAction, "ACTION_PENDING_" + adapterAction22);
            return;
        }
        if (web22 == null) {
            adapterBlock22(requestedAction, "WEBVIEW_MISSING");
            return;
        }

        final String js;
        if ("DICTATION_STOP".equals(requestedAction)) js = DictationLifecycleAdapterV22.clickSubmitJs();
        else if ("DICTATION_CANCEL".equals(requestedAction)) js = DictationLifecycleAdapterV22.clickCancelJs();
        else {
            adapterBlock22(requestedAction, "UNSUPPORTED");
            return;
        }

        adapterClaim22 = requestedAction + "_" + System.currentTimeMillis() + "_"
                + UUID.randomUUID().toString().substring(0, 8);
        boolean durable = prefs22.edit()
                .putString("claim_id", adapterClaim22)
                .putString("claim_action", requestedAction)
                .putString("claim_status", "CLAIMED")
                .commit();
        if (!durable) {
            adapterBlock22(requestedAction, "DURABLE_CLAIM_WRITE_FAIL");
            return;
        }

        adapterPending22 = true;
        adapterAction22 = requestedAction;
        adapterStatus22 = "DURABLE_CLAIMED";
        adapterMatches22 = -1;
        adapterVisibleButtons22 = -1;
        adapterClicked22 = false;
        adapterSubmitCount22 = -1;
        adapterCancelCount22 = -1;
        adapterReadyCount22 = -1;
        adapterUserTurns22 = -1;
        final int baselineUsers = intField22("userCount");
        log22(requestedAction + " DURABLE_CLAIMED");

        web22.evaluateJavascript(js, value -> {
            JSONObject out = decodeJson22(value);
            adapterMatches22 = out.optInt("matches", -1);
            adapterVisibleButtons22 = out.optInt("visible_buttons", -1);
            adapterClicked22 = out.optBoolean("clicked", false);
            if (adapterMatches22 != 1 || !adapterClicked22) {
                adapterPending22 = false;
                adapterStatus22 = "ABORTED_NO_SIDE_EFFECT_MATCHES_" + adapterMatches22;
                prefs22.edit().putString("claim_status", "ABORTED_NO_SIDE_EFFECT").commit();
                log22(requestedAction + " " + adapterStatus22);
                return;
            }
            adapterStatus22 = "DISPATCHED_WAITING_RECEIPT";
            prefs22.edit().putString("claim_status", "DISPATCHED").commit();
            log22(requestedAction + " SINGLE_EXACT_ARIA_CLICK");
            pollActiveExitReceipt22(requestedAction, baselineUsers, System.currentTimeMillis() + 12000L);
        });
    }

    private void pollActiveExitReceipt22(String requestedAction, int baselineUsers, long deadline) {
        if (!adapterPending22 || !requestedAction.equals(adapterAction22) || web22 == null) return;
        readLifecycleState22(s -> {
            if (!s.optBoolean("success", false)) {
                if (System.currentTimeMillis() >= deadline) adapterUncertain22("STATE_READ_TIMEOUT");
                else h22.postDelayed(() -> pollActiveExitReceipt22(requestedAction, baselineUsers, deadline), 300L);
                return;
            }
            adapterSubmitCount22 = s.optInt("submit_count", -1);
            adapterCancelCount22 = s.optInt("cancel_count", -1);
            adapterReadyCount22 = s.optInt("ready_dictation_count", -1);
            adapterUserTurns22 = s.optInt("user_turn_count", -1);

            if (baselineUsers >= 0 && adapterUserTurns22 > baselineUsers) {
                adapterPending22 = false;
                adapterStatus22 = "UNEXPECTED_USER_TURN_AFTER_" + requestedAction;
                prefs22.edit().putString("claim_status", "UNEXPECTED_SIDE_EFFECT").commit();
                log22(adapterStatus22);
                return;
            }

            boolean activeGone = adapterSubmitCount22 == 0 && adapterCancelCount22 == 0;
            boolean readyReturned = adapterReadyCount22 >= 1 || intField22("dictationCount") >= 1;
            if (activeGone && readyReturned) {
                adapterConfirm22(requestedAction, "ACTIVE_DICTATION_EXIT_READY_RETURNED");
                return;
            }
            if (System.currentTimeMillis() >= deadline) {
                adapterUncertain22("EXIT_RECEIPT_TIMEOUT");
                return;
            }
            h22.postDelayed(() -> pollActiveExitReceipt22(requestedAction, baselineUsers, deadline), 300L);
        });
    }

    private void adapterConfirm22(String action, String receipt) {
        adapterPending22 = false;
        adapterAction22 = action;
        adapterStatus22 = "CONFIRMED_" + receipt;
        prefs22.edit().putString("claim_status", "CONFIRMED").putString("claim_receipt", receipt).commit();
        setField22("micLeaseMode", "NONE");
        setField22("micLeaseUntil", 0L);
        setField22("lastAction", action);
        setField22("lastActionStatus", "CONFIRMED_V22_" + receipt);
        setField22("last18Action", action);
        setField22("last18Status", "CONFIRMED_V22_" + receipt);
        log22(action + " CONFIRMED " + receipt);
    }

    private void adapterUncertain22(String reason) {
        adapterPending22 = false;
        adapterStatus22 = "UNCERTAIN_" + reason;
        prefs22.edit().putString("claim_status", "UNCERTAIN").putString("claim_receipt", reason).commit();
        log22(adapterAction22 + " UNCERTAIN " + reason);
    }

    private void adapterBlock22(String action, String reason) {
        adapterAction22 = action;
        adapterStatus22 = "BLOCKED_" + reason;
        log22(action + " BLOCKED " + reason);
    }

    // ---------------------------------------------------------------------
    // Autonomous end-to-end harness
    // ---------------------------------------------------------------------

    private void runFullTest22() {
        if (running22) return;
        running22 = true;
        telemetryHealthy22 = false;
        testId22 = "cp22-" + UUID.randomUUID();
        seq22 = 0;
        startedAt22 = System.currentTimeMillis();
        finalClassification22 = "RUNNING";
        cancelClassification22 = "NOT_RUN";
        stopClassification22 = "NOT_RUN";
        transcriptClassification22 = "NOT_RUN";
        sendClassification22 = "NOT_RUN";
        localEvents22.setLength(0);
        if (runButton22 != null) {
            runButton22.setEnabled(false);
            runButton22.setText("RUNNING...");
        }
        persistRun22(true, "STARTING");
        setStatus22("Telemetry preflight...");

        JSONObject pre = captureState22();
        put22(pre, "preflight", true);
        postPhase22("TELEMETRY_PREFLIGHT", "RUNNING", pre, result -> {
            if (!result.optBoolean("success", false)) {
                telemetryHealthy22 = false;
                finalClassification22 = "TELEMETRY_UNAVAILABLE";
                finishLocally22(false);
                return;
            }
            telemetryHealthy22 = true;
            postRequiredPhase22("RUN_STARTED", "RUNNING", captureState22(), this::waitForBaseline22);
        });
    }

    private void waitForBaseline22() {
        setStatus22("Waiting for stable snapshot...");
        waitUntil22(() -> boolField22("snapOk"), 4500L,
                this::checkSafePreconditions22,
                () -> {
                    finalClassification22 = "SNAPSHOT_NOT_READY";
                    postPhase22("BASELINE_TIMEOUT", "FAIL", captureState22(), r -> recoverSession22());
                });
    }

    private void checkSafePreconditions22() {
        int composer = intField22("composerLen");
        JSONObject state = captureState22();
        put22(state, "requires_empty_composer", true);
        if (composer > 0) {
            finalClassification22 = "BLOCKED_EXISTING_DRAFT";
            postPhase22("PRECONDITION", "BLOCKED_EXISTING_DRAFT", state, r -> recoverSession22());
            return;
        }
        postRequiredPhase22("BASELINE_READY", "RUNNING", state, this::startSession22);
    }

    private void startSession22() {
        setStatus22("Starting InteractionSession...");
        JSONObject click = clickButton22("SESSION START");
        JSONObject state = captureState22();
        put22(state, "click", click);
        postRequiredPhase22("SESSION_START_DISPATCH", "RUNNING", state, () ->
                waitUntil22(() -> "ACTIVE".equals(stringField22("sessionState")), 4000L,
                        () -> postRequiredPhase22("SESSION_ACTIVE", "RUNNING", captureState22(), this::startCancelSubtest22),
                        () -> {
                            finalClassification22 = "SESSION_START_FAILED";
                            postPhase22("SESSION_START_TIMEOUT", "FAIL", captureState22(), r -> recoverSession22());
                        }));
    }

    // ----- Subtest A: Start -> Cancel -----

    private void startCancelSubtest22() {
        setStatus22("Subtest 1/2: starting silent Dictation for Cancel...");
        cancelBaselineUsers22 = intField22("userCount");
        cancelBaselineComposerLen22 = intField22("composerLen");
        cancelBaselineComposerHash22 = stringField22("composerHash");
        postRequiredPhase22("CANCEL_BEFORE_START", "RUNNING", captureState22(), () -> {
            JSONObject click = clickButton22("D START");
            JSONObject state = captureState22();
            put22(state, "click", click);
            postRequiredPhase22("CANCEL_START_DISPATCH", "RUNNING", state, () ->
                    waitUntil22(this::dictationStartObserved22, 6000L,
                            () -> h22.postDelayed(this::verifyCancelActive22, 800L),
                            () -> failAndRecover22("CANCEL_DICTATION_START_FAILED")));
        });
    }

    private void verifyCancelActive22() {
        readLifecycleState22(s -> {
            JSONObject state = captureState22();
            put22(state, "lifecycle", s);
            if (!s.optBoolean("success", false)
                    || s.optInt("submit_count", -1) != 1
                    || s.optInt("cancel_count", -1) != 1) {
                failAndRecover22("CANCEL_ACTIVE_SEMANTICS_NOT_UNIQUE");
                return;
            }
            postRequiredPhase22("CANCEL_ACTIVE_READY", "UNIQUE_SUBMIT_AND_CANCEL", state, this::dispatchCancel22);
        });
    }

    private void dispatchCancel22() {
        setStatus22("Subtest 1/2: Cancel dictation...");
        JSONObject click = clickButton22("D CANCEL");
        JSONObject state = captureState22();
        put22(state, "native_click", click);
        postRequiredPhase22("CANCEL_DISPATCH", "RUNNING", state, () ->
                waitUntil22(this::adapterTerminal22, 13000L,
                        () -> finishCancelSubtest22(false),
                        () -> finishCancelSubtest22(true)));
    }

    private void finishCancelSubtest22(boolean timedOut) {
        readLifecycleState22(s -> {
            int users = s.optInt("user_turn_count", intField22("userCount"));
            int composerLen = s.optInt("composer_len", intField22("composerLen"));
            String composerHash = s.optString("composer_hash", stringField22("composerHash"));
            boolean noMessage = cancelBaselineUsers22 < 0 || users <= cancelBaselineUsers22;
            boolean draftSame = composerLen == cancelBaselineComposerLen22
                    && composerHash.equals(cancelBaselineComposerHash22);
            boolean pass = !timedOut
                    && adapterStatus22.startsWith("CONFIRMED")
                    && noMessage && draftSame;
            cancelClassification22 = pass ? "PASS_CANCEL_NO_MESSAGE_NO_DRAFT"
                    : timedOut ? "CANCEL_TIMEOUT"
                    : !noMessage ? "CANCEL_UNEXPECTED_MESSAGE"
                    : !draftSame ? "CANCEL_DRAFT_CHANGED"
                    : "CANCEL_NOT_CONFIRMED";
            JSONObject state = captureState22();
            put22(state, "lifecycle_after_cancel", s);
            put22(state, "cancel_classification", cancelClassification22);
            put22(state, "no_message_side_effect", noMessage);
            put22(state, "draft_unchanged", draftSame);
            postPhase22("CANCEL_RESULT", cancelClassification22, state, r -> {
                if (!pass) {
                    if ("RUNNING".equals(finalClassification22)) finalClassification22 = cancelClassification22;
                    recoverSession22();
                } else {
                    h22.postDelayed(this::startSpokenSubtest22, 700L);
                }
            });
        });
    }

    // ----- Subtest B: Start -> speech -> Stop/Submit -> transcript -> Send -----

    private void startSpokenSubtest22() {
        setStatus22("Subtest 2/2: preparing spoken Dictation...");
        spokenBaselineUsers22 = intField22("userCount");
        postRequiredPhase22("SPOKEN_BEFORE_START", "RUNNING", captureState22(), () -> {
            JSONObject click = clickButton22("D START");
            JSONObject state = captureState22();
            put22(state, "click", click);
            postRequiredPhase22("SPOKEN_START_DISPATCH", "RUNNING", state, () ->
                    waitUntil22(this::dictationStartObserved22, 6000L,
                            () -> h22.postDelayed(this::verifySpokenActive22, 800L),
                            () -> failAndRecover22("SPOKEN_DICTATION_START_FAILED")));
        });
    }

    private void verifySpokenActive22() {
        readLifecycleState22(s -> {
            JSONObject state = captureState22();
            put22(state, "lifecycle", s);
            if (!s.optBoolean("success", false)
                    || s.optInt("submit_count", -1) != 1
                    || s.optInt("cancel_count", -1) != 1) {
                failAndRecover22("SPOKEN_ACTIVE_SEMANTICS_NOT_UNIQUE");
                return;
            }
            postRequiredPhase22("SPOKEN_ACTIVE_READY", "UNIQUE_SUBMIT_AND_CANCEL", state, this::beginSpeakWindow22);
        });
    }

    private void beginSpeakWindow22() {
        setStatus22("SPEAK NOW - یک جمله کوتاه بگو (حدود 6 ثانیه)");
        beep22();
        JSONObject state = captureState22();
        put22(state, "speak_window_ms", SPEAK_WINDOW_MS);
        postRequiredPhase22("SPEAK_WINDOW_STARTED", "AWAITING_USER_SPEECH", state,
                () -> h22.postDelayed(this::endSpeakWindow22, SPEAK_WINDOW_MS));
    }

    private void endSpeakWindow22() {
        beep22();
        setStatus22("Stopping Dictation and waiting for transcript...");
        postRequiredPhase22("BEFORE_DICTATION_STOP", "RUNNING", captureState22(), this::dispatchSpokenStop22);
    }

    private void dispatchSpokenStop22() {
        JSONObject click = clickButton22("D STOP");
        JSONObject state = captureState22();
        put22(state, "native_click", click);
        postRequiredPhase22("DICTATION_STOP_DISPATCH", "RUNNING", state, () ->
                waitUntil22(this::adapterTerminal22, 13000L,
                        () -> finishSpokenStop22(false),
                        () -> finishSpokenStop22(true)));
    }

    private void finishSpokenStop22(boolean timedOut) {
        readLifecycleState22(s -> {
            int users = s.optInt("user_turn_count", intField22("userCount"));
            boolean noMessage = spokenBaselineUsers22 < 0 || users <= spokenBaselineUsers22;
            boolean confirmed = !timedOut && adapterStatus22.startsWith("CONFIRMED") && noMessage;
            stopClassification22 = confirmed ? "PASS_STOP_CONFIRMED_NO_MESSAGE"
                    : timedOut ? "STOP_TIMEOUT"
                    : !noMessage ? "STOP_UNEXPECTED_MESSAGE"
                    : "STOP_NOT_CONFIRMED";
            JSONObject state = captureState22();
            put22(state, "lifecycle_after_stop", s);
            put22(state, "stop_classification", stopClassification22);
            put22(state, "no_message_side_effect", noMessage);
            postPhase22("DICTATION_STOP_RESULT", stopClassification22, state, r -> {
                if (!confirmed) {
                    if ("RUNNING".equals(finalClassification22)) finalClassification22 = stopClassification22;
                    recoverSession22();
                } else {
                    waitForTranscript22();
                }
            });
        });
    }

    private void waitForTranscript22() {
        setStatus22("Waiting for transcript draft...");
        waitUntil22(() -> intField22("composerLen") > 0, 11000L,
                this::transcriptObserved22,
                () -> {
                    transcriptClassification22 = "TRANSCRIPT_NOT_OBSERVED";
                    if ("RUNNING".equals(finalClassification22)) finalClassification22 = transcriptClassification22;
                    postPhase22("TRANSCRIPT_RESULT", transcriptClassification22, captureState22(), r -> recoverSession22());
                });
    }

    private void transcriptObserved22() {
        transcriptLen22 = intField22("composerLen");
        transcriptHash22 = stringField22("composerHash");
        transcriptClassification22 = transcriptLen22 > 0 ? "PASS_TRANSCRIPT_DRAFT_OBSERVED" : "TRANSCRIPT_EMPTY";
        JSONObject state = captureState22();
        put22(state, "transcript_len", transcriptLen22);
        put22(state, "transcript_hash", transcriptHash22);
        put22(state, "raw_transcript_uploaded", false);
        postRequiredPhase22("TRANSCRIPT_RESULT", transcriptClassification22, state, this::dispatchSend22);
    }

    private void dispatchSend22() {
        setStatus22("Transcript ready; sending once...");
        sendBaselineUsers22 = intField22("userCount");
        JSONObject click = clickButton22("D SEND");
        JSONObject state = captureState22();
        put22(state, "native_click", click);
        postRequiredPhase22("DICTATION_SEND_DISPATCH", "RUNNING", state, () ->
                waitUntil22(this::sendReceiptObserved22, 13000L,
                        () -> finishSend22(false),
                        () -> finishSend22(true)));
    }

    private boolean sendReceiptObserved22() {
        boolean userAdvanced = sendBaselineUsers22 >= 0 && intField22("userCount") > sendBaselineUsers22;
        boolean composerCleared = intField22("composerLen") == 0;
        String action = stringField22("lastAction");
        String status = stringField22("lastActionStatus");
        boolean parentConfirmed = "DICTATION_SEND".equals(action) && status.startsWith("CONFIRMED");
        return userAdvanced && composerCleared && parentConfirmed;
    }

    private void finishSend22(boolean timedOut) {
        boolean userAdvanced = sendBaselineUsers22 >= 0 && intField22("userCount") > sendBaselineUsers22;
        boolean composerCleared = intField22("composerLen") == 0;
        String action = stringField22("lastAction");
        String status = stringField22("lastActionStatus");
        boolean parentConfirmed = "DICTATION_SEND".equals(action) && status.startsWith("CONFIRMED");
        boolean pass = !timedOut && userAdvanced && composerCleared && parentConfirmed;
        sendClassification22 = pass ? "PASS_SEND_CONFIRMED_USER_TURN_RECEIPT"
                : timedOut ? "SEND_TIMEOUT"
                : !userAdvanced ? "SEND_USER_TURN_NOT_OBSERVED"
                : !composerCleared ? "SEND_COMPOSER_NOT_CLEARED"
                : "SEND_NOT_CONFIRMED";
        JSONObject state = captureState22();
        put22(state, "send_classification", sendClassification22);
        put22(state, "user_turn_advanced", userAdvanced);
        put22(state, "composer_cleared", composerCleared);
        put22(state, "parent_send_confirmed", parentConfirmed);
        postPhase22("DICTATION_SEND_RESULT", sendClassification22, state, r -> {
            if (!pass && "RUNNING".equals(finalClassification22)) finalClassification22 = sendClassification22;
            recoverSession22();
        });
    }

    private boolean dictationStartObserved22() {
        String lease = stringField22("micLeaseMode");
        String parentStatus = stringField22("lastActionStatus");
        String wrapperStatus = stringField22("lastWrapperStatus");
        return "DICTATION".equals(lease)
                && (parentStatus.contains("CONFIRMED")
                || parentStatus.contains("ACCEPTED_REVERSIBLE_START")
                || wrapperStatus.contains("CONFIRMED")
                || wrapperStatus.contains("ACCEPTED_REVERSIBLE_START"));
    }

    private boolean adapterTerminal22() {
        return adapterStatus22.startsWith("CONFIRMED")
                || adapterStatus22.startsWith("ABORTED")
                || adapterStatus22.startsWith("BLOCKED")
                || adapterStatus22.startsWith("UNCERTAIN")
                || adapterStatus22.startsWith("UNEXPECTED");
    }

    private void failAndRecover22(String classification) {
        if ("RUNNING".equals(finalClassification22)) finalClassification22 = classification;
        postPhase22("SUBTEST_FAILURE", classification, captureState22(), r -> recoverSession22());
    }

    // ---------------------------------------------------------------------
    // Recovery
    // ---------------------------------------------------------------------

    private void recoverSession22() {
        setStatus22("Recovering session...");
        JSONObject before = captureState22();
        postPhase22("BEFORE_RECOVERY", "RUNNING", before, r -> {
            JSONObject click;
            if ("ACTIVE".equals(stringField22("sessionState"))) click = clickButton22("SESSION END");
            else click = clickResult22("SESSION END", false, false, "already_not_active");
            JSONObject after = captureState22();
            put22(after, "click", click);
            postPhase22("RECOVERY_DISPATCH", "RUNNING", after, x ->
                    waitUntil22(this::recoveryComplete22, 5500L,
                            () -> finishAfterRecovery22(true),
                            () -> finishAfterRecovery22(false)));
        });
    }

    private boolean recoveryComplete22() {
        return "IDLE".equals(stringField22("sessionState"))
                && "NONE".equals(stringField22("micLeaseMode"));
    }

    private void finishAfterRecovery22(boolean recovered) {
        if ("RUNNING".equals(finalClassification22)) {
            boolean allPass = cancelClassification22.startsWith("PASS_")
                    && stopClassification22.startsWith("PASS_")
                    && transcriptClassification22.startsWith("PASS_")
                    && sendClassification22.startsWith("PASS_");
            finalClassification22 = allPass && recovered
                    ? "PASS_DICTATION_CANCEL_STOP_TRANSCRIPT_SEND_RECOVERED"
                    : allPass ? "DICTATION_E2E_RECOVERY_FAILED"
                    : "DICTATION_E2E_INCOMPLETE" + (recovered ? "_RECOVERED" : "_RECOVERY_FAILED");
        } else {
            finalClassification22 = finalClassification22 + (recovered ? "_RECOVERED" : "_RECOVERY_FAILED");
        }
        JSONObject state = captureState22();
        put22(state, "recovered", recovered);
        put22(state, "cancel_classification", cancelClassification22);
        put22(state, "stop_classification", stopClassification22);
        put22(state, "transcript_classification", transcriptClassification22);
        put22(state, "send_classification", sendClassification22);
        put22(state, "final_classification", finalClassification22);
        postPhase22("RECOVERY_RESULT", recovered ? "RECOVERED" : "RECOVERY_FAILED", state, r ->
                postPhase22("FINAL", finalClassification22, captureState22(), finalUpload ->
                        finishLocally22(finalUpload.optBoolean("success", false))));
    }

    // ---------------------------------------------------------------------
    // Telemetry and helpers
    // ---------------------------------------------------------------------

    private void readLifecycleState22(JsonCallback22 callback) {
        if (web22 == null) {
            JSONObject o = new JSONObject();
            put22(o, "success", false);
            put22(o, "error", "WebViewMissing");
            callback.done(o);
            return;
        }
        web22.evaluateJavascript(DictationLifecycleAdapterV22.stateJs(), value -> callback.done(decodeJson22(value)));
    }

    private void postRequiredPhase22(String phase, String classification, JSONObject state, Runnable next) {
        postPhase22(phase, classification, state, result -> {
            if (!result.optBoolean("success", false)) {
                telemetryHealthy22 = false;
                if ("RUNNING".equals(finalClassification22)) finalClassification22 = "TELEMETRY_LOST_AT_" + phase;
                recoverSession22();
                return;
            }
            next.run();
        });
    }

    private void postPhase22(String phase, String classification, JSONObject state, UploadCallback22 callback) {
        int seq = ++seq22;
        persistRun22(true, phase);
        JSONObject payload = new JSONObject();
        put22(payload, "kind", "TEST_PHASE");
        put22(payload, "schema_version", SCHEMA_VERSION);
        put22(payload, "scenario_id", SCENARIO_ID);
        put22(payload, "scenario_version", SCENARIO_VERSION);
        put22(payload, "test_id", testId22);
        put22(payload, "seq", seq);
        put22(payload, "phase", phase);
        put22(payload, "classification", classification);
        put22(payload, "app_version", appVersion22());
        put22(payload, "source_ref", TelemetryConfigV22.SOURCE_REF);
        put22(payload, "collector_id", TelemetryConfigV22.COLLECTOR_ID);
        put22(payload, "elapsed_ms", startedAt22 == 0L ? 0L : System.currentTimeMillis() - startedAt22);
        put22(payload, "timestamp_epoch_ms", System.currentTimeMillis());
        put22(payload, "privacy", "counts_lengths_hashes_receipts_no_raw_audio_speech_transcript_chat_or_credentials");
        put22(payload, "state", state == null ? new JSONObject() : state);
        log22("PHASE " + seq + " " + phase + " " + classification);

        new Thread(() -> {
            JSONObject result = uploadJson22(payload, 2);
            runOnUiThread(() -> callback.done(result));
        }, "cp22-telemetry-" + seq).start();
    }

    private JSONObject uploadJson22(JSONObject payload, int attempts) {
        JSONObject result = new JSONObject();
        put22(result, "configured", TelemetryConfigV22.isConfigured());
        if (!TelemetryConfigV22.isConfigured()) {
            put22(result, "success", false);
            put22(result, "error", "TelemetryNotConfigured");
            return result;
        }
        for (int attempt = 1; attempt <= attempts; attempt++) {
            HttpURLConnection conn = null;
            try {
                URL url = new URL(TelemetryConfigV22.WEBHOOK_URL);
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
                put22(result, "http_status", code);
                put22(result, "attempts", attempt);
                if (code >= 200 && code < 300) {
                    put22(result, "success", true);
                    return result;
                }
            } catch (Exception e) {
                put22(result, "error", e.getClass().getSimpleName());
                put22(result, "attempts", attempt);
            } finally {
                if (conn != null) conn.disconnect();
            }
            try { Thread.sleep(900L); }
            catch (InterruptedException e) { Thread.currentThread().interrupt(); break; }
        }
        put22(result, "success", false);
        return result;
    }

    private JSONObject captureState22() {
        JSONObject o = new JSONObject();
        put22(o, "session_state", stringField22("sessionState"));
        put22(o, "mic_lease_mode", stringField22("micLeaseMode"));
        put22(o, "snapshot_ok", boolField22("snapOk"));
        put22(o, "dictation_count", intField22("dictationCount"));
        put22(o, "stop_count", intField22("stopCount"));
        put22(o, "send_count_legacy", intField22("sendCount"));
        put22(o, "cancel_count_legacy", intField22("cancelCount"));
        put22(o, "composer_len", intField22("composerLen"));
        put22(o, "composer_hash", stringField22("composerHash"));
        put22(o, "user_turn_count", intField22("userCount"));
        put22(o, "parent_last_action", stringField22("lastAction"));
        put22(o, "parent_last_status", stringField22("lastActionStatus"));
        put22(o, "wrapper_last_status", stringField22("lastWrapperStatus"));
        put22(o, "v18_last_action", stringField22("last18Action"));
        put22(o, "v18_last_status", stringField22("last18Status"));
        put22(o, "forced_session_end_count", intField22("forcedSessionEnds"));
        put22(o, "run_state", stringField22("runState18"));
        put22(o, "adapter_action", adapterAction22);
        put22(o, "adapter_status", adapterStatus22);
        put22(o, "adapter_pending", adapterPending22);
        put22(o, "adapter_matches", adapterMatches22);
        put22(o, "adapter_visible_buttons", adapterVisibleButtons22);
        put22(o, "adapter_clicked", adapterClicked22);
        put22(o, "adapter_submit_count", adapterSubmitCount22);
        put22(o, "adapter_cancel_count", adapterCancelCount22);
        put22(o, "adapter_ready_count", adapterReadyCount22);
        put22(o, "adapter_user_turns", adapterUserTurns22);
        put22(o, "webview_present", web22 != null);
        put22(o, "telemetry_healthy", telemetryHealthy22);
        put22(o, "raw_audio_uploaded", false);
        put22(o, "raw_speech_uploaded", false);
        put22(o, "raw_transcript_uploaded", false);
        put22(o, "raw_chat_text_uploaded", false);
        return o;
    }

    private JSONObject clickButton22(String exactText) {
        JSONObject out = new JSONObject();
        Button b = findButton22(getWindow().getDecorView(), exactText);
        put22(out, "requested", exactText);
        put22(out, "found", b != null);
        if (b == null) {
            put22(out, "clicked", false);
            put22(out, "reason", "button_not_found");
            return out;
        }
        boolean enabled = b.isEnabled();
        boolean visible = b.getVisibility() == View.VISIBLE;
        put22(out, "enabled", enabled);
        put22(out, "visible", visible);
        boolean clicked = false;
        if (enabled && visible) {
            try { clicked = b.performClick(); }
            catch (Exception ignored) { }
        }
        put22(out, "clicked", clicked);
        return out;
    }

    private JSONObject clickResult22(String requested, boolean found, boolean clicked, String reason) {
        JSONObject out = new JSONObject();
        put22(out, "requested", requested);
        put22(out, "found", found);
        put22(out, "clicked", clicked);
        put22(out, "reason", reason);
        return out;
    }

    private Button findButton22(View v, String exactText) {
        if (v instanceof Button) {
            Button b = (Button) v;
            if (exactText.equals(String.valueOf(b.getText()))) return b;
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                Button b = findButton22(g.getChildAt(i), exactText);
                if (b != null) return b;
            }
        }
        return null;
    }

    private void waitUntil22(Condition22 condition, long timeoutMs, Runnable success, Runnable timeout) {
        final long start = System.currentTimeMillis();
        final Runnable[] poll = new Runnable[1];
        poll[0] = () -> {
            if (!running22) return;
            boolean ok = false;
            try { ok = condition.ok(); } catch (Exception ignored) { }
            if (ok) { success.run(); return; }
            if (System.currentTimeMillis() - start >= timeoutMs) { timeout.run(); return; }
            h22.postDelayed(poll[0], 250L);
        };
        h22.post(poll[0]);
    }

    private void reportInterruptedRunIfNeeded22() {
        if (!prefs22.getBoolean("run_active", false)) return;
        String oldId = prefs22.getString("test_id", "cp22-interrupted-unknown");
        int oldSeq = prefs22.getInt("seq", 0);
        long oldStart = prefs22.getLong("started_at", System.currentTimeMillis());
        String oldPhase = prefs22.getString("phase", "UNKNOWN");
        testId22 = oldId;
        seq22 = oldSeq;
        startedAt22 = oldStart;
        JSONObject state = captureState22();
        put22(state, "interrupted_after_phase", oldPhase);
        postPhase22("RUN_INTERRUPTED_APP_RESTART", "FAIL", state, r -> {
            prefs22.edit().putBoolean("run_active", false).apply();
            setStatus22("Previous run interruption reported. Ready for a new test.");
        });
    }

    private void persistRun22(boolean active, String phase) {
        prefs22.edit()
                .putBoolean("run_active", active)
                .putString("test_id", testId22)
                .putInt("seq", seq22)
                .putLong("started_at", startedAt22)
                .putString("phase", phase)
                .apply();
    }

    private void finishLocally22(boolean finalUploadOk) {
        running22 = false;
        persistRun22(false, "FINISHED");
        if (runButton22 != null) {
            runButton22.setEnabled(true);
            runButton22.setText("RUN AGAIN");
        }
        if (finalUploadOk) {
            setStatus22("TEST COMPLETE - report uploaded. Tell ChatGPT: test finished");
        } else {
            saveFallback22();
            setStatus22("TEST COMPLETE - telemetry unavailable; local fallback saved");
        }
    }

    private void saveFallback22() {
        try {
            JSONObject o = captureState22();
            put22(o, "test_id", testId22);
            put22(o, "final_classification", finalClassification22);
            put22(o, "events", localEvents22.toString());
            String name = "chatgpt-webview-v22-fallback-"
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
            Toast.makeText(this, "v0.22 fallback saved to Downloads", Toast.LENGTH_LONG).show();
        } catch (Exception ignored) { }
    }

    private void beep22() {
        try {
            ToneGenerator tg = new ToneGenerator(AudioManager.STREAM_NOTIFICATION, 70);
            tg.startTone(ToneGenerator.TONE_PROP_BEEP, 180);
            h22.postDelayed(tg::release, 350L);
        } catch (Exception ignored) { }
    }

    private String appVersion22() {
        try {
            PackageInfo pi = getPackageManager().getPackageInfo(getPackageName(), 0);
            return pi.versionName + "(" + pi.getLongVersionCode() + ")";
        } catch (Exception e) {
            return "unknown";
        }
    }

    private JSONObject decodeJson22(String value) {
        try {
            Object x = new JSONTokener(value == null ? "null" : value).nextValue();
            if (x instanceof String) x = new JSONTokener((String) x).nextValue();
            if (x instanceof JSONObject) return (JSONObject) x;
        } catch (Exception ignored) { }
        JSONObject o = new JSONObject();
        put22(o, "success", false);
        put22(o, "error", "DecodeFailed");
        return o;
    }

    private WebView findWeb22(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb22(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }

    private Field field22(String name) {
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

    private String stringField22(String name) {
        try {
            Field f = field22(name);
            if (f == null) return "UNKNOWN";
            Object v = f.get(this);
            return v == null ? "NONE" : String.valueOf(v);
        } catch (Exception e) { return "ERROR"; }
    }

    private int intField22(String name) {
        try {
            Field f = field22(name);
            return f == null ? -1 : f.getInt(this);
        } catch (Exception e) { return -1; }
    }

    private boolean boolField22(String name) {
        try {
            Field f = field22(name);
            return f != null && f.getBoolean(this);
        } catch (Exception e) { return false; }
    }

    private void setField22(String name, Object value) {
        try {
            Field f = field22(name);
            if (f == null) return;
            if (f.getType() == long.class && value instanceof Number) f.setLong(this, ((Number) value).longValue());
            else f.set(this, value);
        } catch (Exception ignored) { }
    }

    private int dp22(int x) {
        return Math.round(x * getResources().getDisplayMetrics().density);
    }

    private void setStatus22(String s) {
        runOnUiThread(() -> { if (status22 != null) status22.setText(s); });
        log22("STATUS " + s);
    }

    private void log22(String s) {
        String safe = s == null ? "" : s.replace('\n', ' ');
        if (safe.length() > 700) safe = safe.substring(0, 700);
        localEvents22.append(System.currentTimeMillis()).append(" | ").append(safe).append('\n');
    }

    private void put22(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) { }
    }

    @Override protected void onDestroy() {
        h22.removeCallbacksAndMessages(null);
        super.onDestroy();
    }
}
