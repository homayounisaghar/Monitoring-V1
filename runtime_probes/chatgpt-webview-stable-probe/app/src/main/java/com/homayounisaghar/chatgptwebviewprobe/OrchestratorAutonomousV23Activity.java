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
import java.util.concurrent.atomic.AtomicBoolean;

public class OrchestratorAutonomousV23Activity extends OrchestratorFoundationV18Activity {
    private static final String PREFS23 = "stable_v23_one_tap_watchdog";
    private static final String SCHEMA_VERSION = "cp-autonomous-runtime-v2";
    private static final String SCENARIO_ID = "dictation-one-tap-bounded-e2e";
    private static final int SCENARIO_VERSION = 1;
    private static final long GLOBAL_WATCHDOG_MS = 90000L;
    private static final long EVAL_TIMEOUT_MS = 2600L;
    private static final long SPEAK_WINDOW_MS = 5000L;
    private static final int NET_TIMEOUT_MS = 2800;

    private final Handler h23 = new Handler(Looper.getMainLooper());
    private final StringBuilder events23 = new StringBuilder();
    private final Runnable globalWatchdog23 = this::onGlobalWatchdog23;
    private SharedPreferences prefs23;
    private WebView web23;
    private Button runButton23;
    private TextView status23;
    private boolean running23 = false;
    private boolean telemetryHealthy23 = false;
    private String testId23 = "-";
    private int seq23 = 0;
    private long startedAt23 = 0L;
    private String currentPhase23 = "IDLE";
    private String finalClassification23 = "NOT_RUN";
    private String cancelClassification23 = "NOT_RUN";
    private String stopClassification23 = "NOT_RUN";
    private String transcriptClassification23 = "NOT_RUN";
    private String sendClassification23 = "NOT_RUN";
    private boolean adapterPending23 = false;
    private String adapterAction23 = "NONE";
    private String adapterStatus23 = "NOT_RUN";
    private String adapterClaim23 = "-";
    private int adapterMatches23 = -1;
    private boolean adapterClicked23 = false;
    private int adapterSubmit23 = -1;
    private int adapterCancel23 = -1;
    private int adapterReady23 = -1;
    private int adapterUsers23 = -1;
    private int cancelBaselineUsers23 = -1;
    private int cancelBaselineComposerLen23 = -1;
    private String cancelBaselineComposerHash23 = "-";
    private int spokenBaselineUsers23 = -1;
    private int sendBaselineUsers23 = -1;
    private int transcriptLen23 = -1;
    private String transcriptHash23 = "-";

    private interface JsonCallback23 { void done(JSONObject result); }
    private interface Condition23 { boolean ok(); }
    private interface AdapterDone23 { void done(boolean confirmed); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs23 = getSharedPreferences(PREFS23, MODE_PRIVATE);
        web23 = findWeb23(getWindow().getDecorView());
        if (web23 != null) web23.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        retargetManualDictationButtons23(getWindow().getDecorView());
        installPanel23();
        reportInterruptedRun23();
    }

    private void installPanel23() {
        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) content;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        int wi = web23 == null ? 0 : root.indexOfChild(web23);
        if (wi < 0) wi = 0;
        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp23(6), dp23(3), dp23(6), dp23(5));
        runButton23 = new Button(this);
        runButton23.setText("RUN FULL TEST");
        runButton23.setTextSize(14f);
        runButton23.setAllCaps(false);
        runButton23.setOnClickListener(v -> runFullTest23());
        panel.addView(runButton23, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp23(52)));
        status23 = new TextView(this);
        status23.setTextSize(12f);
        status23.setText("v0.23 one-tap bounded Dictation test ready");
        status23.setPadding(dp23(6), dp23(4), dp23(6), dp23(6));
        panel.addView(status23, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        root.addView(panel, wi, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void retargetManualDictationButtons23(View v) {
        if (v instanceof Button) {
            Button b = (Button) v;
            String t = String.valueOf(b.getText());
            if ("D STOP".equals(t)) b.setOnClickListener(x -> dispatchActive23("DICTATION_STOP", ok -> {}));
            if ("D CANCEL".equals(t)) b.setOnClickListener(x -> dispatchActive23("DICTATION_CANCEL", ok -> {}));
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) retargetManualDictationButtons23(g.getChildAt(i));
        }
    }

    private void runFullTest23() {
        if (running23) return;
        running23 = true;
        telemetryHealthy23 = false;
        testId23 = "cp23-" + UUID.randomUUID();
        seq23 = 0;
        startedAt23 = System.currentTimeMillis();
        currentPhase23 = "STARTING";
        finalClassification23 = "RUNNING";
        cancelClassification23 = "NOT_RUN";
        stopClassification23 = "NOT_RUN";
        transcriptClassification23 = "NOT_RUN";
        sendClassification23 = "NOT_RUN";
        adapterPending23 = false;
        adapterAction23 = "NONE";
        adapterStatus23 = "NOT_RUN";
        events23.setLength(0);
        if (runButton23 != null) { runButton23.setEnabled(false); runButton23.setText("RUNNING..."); }
        persistRun23(true, currentPhase23);
        setStatus23("Telemetry preflight...");
        h23.removeCallbacks(globalWatchdog23);
        h23.postDelayed(globalWatchdog23, GLOBAL_WATCHDOG_MS);
        telemetryPreflight23();
    }

    private void telemetryPreflight23() {
        JSONObject state = captureState23();
        put23(state, "preflight", true);
        JSONObject payload = payload23("TELEMETRY_PREFLIGHT", "RUNNING", state, 0);
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!running23 || !once.compareAndSet(false, true)) return;
            telemetryHealthy23 = false;
            finalClassification23 = "TELEMETRY_PREFLIGHT_TIMEOUT";
            finishLocally23("TEST NOT STARTED - telemetry preflight timed out");
        };
        h23.postDelayed(timeout, 8000L);
        new Thread(() -> {
            JSONObject r = uploadJson23(payload, NET_TIMEOUT_MS + 900);
            runOnUiThread(() -> {
                if (!running23 || !once.compareAndSet(false, true)) return;
                h23.removeCallbacks(timeout);
                if (!r.optBoolean("success", false)) {
                    telemetryHealthy23 = false;
                    finalClassification23 = "TELEMETRY_UNAVAILABLE";
                    finishLocally23("TEST NOT STARTED - telemetry unavailable");
                    return;
                }
                telemetryHealthy23 = true;
                phase23("RUN_STARTED", "RUNNING", captureState23());
                waitForBaseline23();
            });
        }, "cp23-preflight").start();
    }

    private void waitForBaseline23() {
        setStatus23("Waiting for stable ChatGPT state...");
        waitUntil23(() -> boolField23("snapOk"), 4500L, this::checkPreconditions23, () -> failAndRecover23("SNAPSHOT_NOT_READY"));
    }

    private void checkPreconditions23() {
        int composer = intField23("composerLen");
        JSONObject s = captureState23();
        put23(s, "requires_empty_composer", true);
        if (composer > 0) {
            finalClassification23 = "BLOCKED_EXISTING_DRAFT";
            phase23("PRECONDITION", finalClassification23, s);
            recoverSession23();
            return;
        }
        phase23("BASELINE_READY", "RUNNING", s);
        startSession23();
    }

    private void startSession23() {
        setStatus23("Starting InteractionSession...");
        JSONObject click = clickButton23("SESSION START");
        JSONObject s = captureState23(); put23(s, "click", click);
        phase23("SESSION_START_DISPATCH", "RUNNING", s);
        if (!click.optBoolean("clicked", false)) { failAndRecover23("SESSION_START_NOT_DISPATCHED"); return; }
        waitUntil23(() -> "ACTIVE".equals(stringField23("sessionState")), 4000L,
                () -> { phase23("SESSION_ACTIVE", "RUNNING", captureState23()); startCancelSubtest23(); },
                () -> failAndRecover23("SESSION_START_FAILED"));
    }

    private void startCancelSubtest23() {
        setStatus23("1/2: starting Dictation for Cancel test...");
        cancelBaselineUsers23 = intField23("userCount");
        cancelBaselineComposerLen23 = intField23("composerLen");
        cancelBaselineComposerHash23 = stringField23("composerHash");
        phase23("CANCEL_BEFORE_START", "RUNNING", captureState23());
        JSONObject click = clickButton23("D START");
        JSONObject s = captureState23(); put23(s, "click", click);
        phase23("CANCEL_START_DISPATCH", "RUNNING", s);
        if (!click.optBoolean("clicked", false)) { failAndRecover23("CANCEL_DICTATION_START_NOT_DISPATCHED"); return; }
        waitUntil23(this::dictationStartObserved23, 6000L, () -> h23.postDelayed(this::verifyCancelActive23, 650L), () -> failAndRecover23("CANCEL_DICTATION_START_FAILED"));
    }

    private void verifyCancelActive23() {
        readLifecycle23(s -> {
            if (!running23) return;
            JSONObject state = captureState23(); put23(state, "lifecycle", s);
            boolean unique = s.optBoolean("success", false) && s.optInt("submit_count", -1) == 1 && s.optInt("cancel_count", -1) == 1;
            if (!unique) { phase23("CANCEL_ACTIVE_CHECK", "ACTIVE_SEMANTICS_NOT_UNIQUE", state); failAndRecover23("CANCEL_ACTIVE_SEMANTICS_NOT_UNIQUE"); return; }
            phase23("CANCEL_ACTIVE_READY", "UNIQUE_SUBMIT_AND_CANCEL", state);
            setStatus23("1/2: cancelling Dictation...");
            dispatchActive23("DICTATION_CANCEL", this::finishCancelSubtest23);
        });
    }

    private void finishCancelSubtest23(boolean confirmed) {
        if (!running23) return;
        h23.postDelayed(() -> readLifecycle23(s -> {
            if (!running23) return;
            int users = intField23("userCount");
            int composerLen = intField23("composerLen");
            String composerHash = stringField23("composerHash");
            boolean noMessage = cancelBaselineUsers23 < 0 || users <= cancelBaselineUsers23;
            boolean draftSame = composerLen == cancelBaselineComposerLen23 && composerHash.equals(cancelBaselineComposerHash23);
            boolean pass = confirmed && noMessage && draftSame;
            cancelClassification23 = pass ? "PASS_CANCEL_NO_MESSAGE_NO_DRAFT" : !confirmed ? "CANCEL_NOT_CONFIRMED" : !noMessage ? "CANCEL_UNEXPECTED_MESSAGE" : "CANCEL_DRAFT_CHANGED";
            JSONObject state = captureState23(); put23(state, "lifecycle_after_cancel", s); put23(state, "cancel_classification", cancelClassification23); put23(state, "no_message_side_effect", noMessage); put23(state, "draft_unchanged", draftSame);
            phase23("CANCEL_RESULT", cancelClassification23, state);
            if (!pass) { if ("RUNNING".equals(finalClassification23)) finalClassification23 = cancelClassification23; recoverSession23(); }
            else h23.postDelayed(this::startSpokenSubtest23, 650L);
        }), 450L);
    }

    private void startSpokenSubtest23() {
        if (!running23) return;
        setStatus23("2/2: starting Dictation for transcript/send test...");
        spokenBaselineUsers23 = intField23("userCount");
        phase23("SPOKEN_BEFORE_START", "RUNNING", captureState23());
        JSONObject click = clickButton23("D START");
        JSONObject s = captureState23(); put23(s, "click", click);
        phase23("SPOKEN_START_DISPATCH", "RUNNING", s);
        if (!click.optBoolean("clicked", false)) { failAndRecover23("SPOKEN_DICTATION_START_NOT_DISPATCHED"); return; }
        waitUntil23(this::dictationStartObserved23, 6000L, () -> h23.postDelayed(this::verifySpokenActive23, 650L), () -> failAndRecover23("SPOKEN_DICTATION_START_FAILED"));
    }

    private void verifySpokenActive23() {
        readLifecycle23(s -> {
            if (!running23) return;
            JSONObject state = captureState23(); put23(state, "lifecycle", s);
            boolean unique = s.optBoolean("success", false) && s.optInt("submit_count", -1) == 1 && s.optInt("cancel_count", -1) == 1;
            if (!unique) { phase23("SPOKEN_ACTIVE_CHECK", "ACTIVE_SEMANTICS_NOT_UNIQUE", state); failAndRecover23("SPOKEN_ACTIVE_SEMANTICS_NOT_UNIQUE"); return; }
            phase23("SPOKEN_ACTIVE_READY", "UNIQUE_SUBMIT_AND_CANCEL", state);
            beginSpeakWindow23();
        });
    }

    private void beginSpeakWindow23() {
        setStatus23("SPEAK NOW - یک جمله کوتاه آزمایشی بگو");
        beep23();
        JSONObject s = captureState23(); put23(s, "speak_window_ms", SPEAK_WINDOW_MS);
        phase23("SPEAK_WINDOW_STARTED", "AWAITING_USER_SPEECH", s);
        h23.postDelayed(this::endSpeakWindow23, SPEAK_WINDOW_MS);
    }

    private void endSpeakWindow23() {
        if (!running23) return;
        beep23();
        setStatus23("Stopping Dictation; waiting for transcript...");
        phase23("BEFORE_DICTATION_STOP", "RUNNING", captureState23());
        dispatchActive23("DICTATION_STOP", this::finishStopSubtest23);
    }

    private void finishStopSubtest23(boolean confirmed) {
        if (!running23) return;
        h23.postDelayed(() -> readLifecycle23(s -> {
            if (!running23) return;
            int users = intField23("userCount");
            boolean noMessage = spokenBaselineUsers23 < 0 || users <= spokenBaselineUsers23;
            boolean pass = confirmed && noMessage;
            stopClassification23 = pass ? "PASS_STOP_CONFIRMED_NO_MESSAGE" : !confirmed ? "STOP_NOT_CONFIRMED" : "STOP_UNEXPECTED_MESSAGE";
            JSONObject state = captureState23(); put23(state, "lifecycle_after_stop", s); put23(state, "stop_classification", stopClassification23); put23(state, "no_message_side_effect", noMessage);
            phase23("DICTATION_STOP_RESULT", stopClassification23, state);
            if (!pass) { if ("RUNNING".equals(finalClassification23)) finalClassification23 = stopClassification23; recoverSession23(); return; }
            waitForTranscript23();
        }), 450L);
    }

    private void waitForTranscript23() {
        setStatus23("Waiting for transcript draft...");
        waitUntil23(() -> intField23("composerLen") > 0, 11000L, this::transcriptObserved23, () -> {
            transcriptClassification23 = "TRANSCRIPT_NOT_OBSERVED";
            if ("RUNNING".equals(finalClassification23)) finalClassification23 = transcriptClassification23;
            phase23("TRANSCRIPT_RESULT", transcriptClassification23, captureState23());
            recoverSession23();
        });
    }

    private void transcriptObserved23() {
        transcriptLen23 = intField23("composerLen");
        transcriptHash23 = stringField23("composerHash");
        transcriptClassification23 = transcriptLen23 > 0 ? "PASS_TRANSCRIPT_DRAFT_OBSERVED" : "TRANSCRIPT_EMPTY";
        JSONObject state = captureState23(); put23(state, "transcript_len", transcriptLen23); put23(state, "transcript_hash", transcriptHash23); put23(state, "raw_transcript_uploaded", false);
        phase23("TRANSCRIPT_RESULT", transcriptClassification23, state);
        if (!transcriptClassification23.startsWith("PASS_")) { if ("RUNNING".equals(finalClassification23)) finalClassification23 = transcriptClassification23; recoverSession23(); return; }
        dispatchSend23();
    }

    private void dispatchSend23() {
        setStatus23("Transcript ready; sending exactly once...");
        sendBaselineUsers23 = intField23("userCount");
        JSONObject click = clickButton23("D SEND");
        JSONObject state = captureState23(); put23(state, "native_click", click);
        phase23("DICTATION_SEND_DISPATCH", "RUNNING", state);
        if (!click.optBoolean("clicked", false)) { sendClassification23 = "SEND_NOT_DISPATCHED"; if ("RUNNING".equals(finalClassification23)) finalClassification23 = sendClassification23; recoverSession23(); return; }
        waitUntil23(this::sendReceiptObserved23, 11000L, () -> finishSend23(false), () -> finishSend23(true));
    }

    private boolean sendReceiptObserved23() {
        boolean userAdvanced = sendBaselineUsers23 >= 0 && intField23("userCount") > sendBaselineUsers23;
        boolean composerCleared = intField23("composerLen") == 0;
        String action = stringField23("lastAction");
        String status = stringField23("lastActionStatus");
        return userAdvanced && composerCleared && "DICTATION_SEND".equals(action) && status.startsWith("CONFIRMED");
    }

    private void finishSend23(boolean timedOut) {
        boolean userAdvanced = sendBaselineUsers23 >= 0 && intField23("userCount") > sendBaselineUsers23;
        boolean composerCleared = intField23("composerLen") == 0;
        String action = stringField23("lastAction");
        String status = stringField23("lastActionStatus");
        boolean parentConfirmed = "DICTATION_SEND".equals(action) && status.startsWith("CONFIRMED");
        boolean pass = !timedOut && userAdvanced && composerCleared && parentConfirmed;
        sendClassification23 = pass ? "PASS_SEND_CONFIRMED_USER_TURN_RECEIPT" : timedOut ? "SEND_TIMEOUT" : !userAdvanced ? "SEND_USER_TURN_NOT_OBSERVED" : !composerCleared ? "SEND_COMPOSER_NOT_CLEARED" : "SEND_NOT_CONFIRMED";
        JSONObject state = captureState23(); put23(state, "send_classification", sendClassification23); put23(state, "user_turn_advanced", userAdvanced); put23(state, "composer_cleared", composerCleared); put23(state, "parent_send_confirmed", parentConfirmed);
        phase23("DICTATION_SEND_RESULT", sendClassification23, state);
        if (!pass && "RUNNING".equals(finalClassification23)) finalClassification23 = sendClassification23;
        recoverSession23();
    }

    private void dispatchActive23(String action, AdapterDone23 done) {
        if (!"ACTIVE".equals(stringField23("sessionState"))) { adapterStatus23 = "BLOCKED_SESSION_NOT_ACTIVE"; adapterEvent23(action + "_BLOCK", adapterStatus23, captureState23()); done.done(false); return; }
        if (!"DICTATION".equals(stringField23("micLeaseMode"))) { adapterStatus23 = "BLOCKED_NO_DICTATION_LEASE"; adapterEvent23(action + "_BLOCK", adapterStatus23, captureState23()); done.done(false); return; }
        if (adapterPending23 || web23 == null) { adapterStatus23 = adapterPending23 ? "BLOCKED_ACTION_PENDING" : "BLOCKED_WEBVIEW_MISSING"; adapterEvent23(action + "_BLOCK", adapterStatus23, captureState23()); done.done(false); return; }
        final String js = "DICTATION_STOP".equals(action) ? DictationLifecycleAdapterV23.clickSubmitJs() : "DICTATION_CANCEL".equals(action) ? DictationLifecycleAdapterV23.clickCancelJs() : null;
        if (js == null) { adapterStatus23 = "BLOCKED_UNSUPPORTED"; done.done(false); return; }
        adapterClaim23 = action + "_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0, 8);
        boolean durable = prefs23.edit().putString("claim_id", adapterClaim23).putString("claim_action", action).putString("claim_status", "CLAIMED").commit();
        if (!durable) { adapterStatus23 = "BLOCKED_DURABLE_CLAIM_WRITE_FAIL"; done.done(false); return; }
        adapterPending23 = true; adapterAction23 = action; adapterStatus23 = "DURABLE_CLAIMED"; adapterMatches23 = -1; adapterClicked23 = false;
        final int baselineUsers = intField23("userCount");
        adapterEvent23(action + "_CLAIM", "DURABLE_CLAIMED", captureState23());
        evalJson23(js, EVAL_TIMEOUT_MS, out -> {
            if (!adapterPending23) return;
            if (out.optBoolean("eval_timeout", false)) { adapterPending23 = false; adapterStatus23 = "UNCERTAIN_EVAL_CALLBACK_TIMEOUT"; prefs23.edit().putString("claim_status", "UNCERTAIN").putString("claim_receipt", "EVAL_CALLBACK_TIMEOUT").commit(); adapterEvent23(action + "_DISPATCH", adapterStatus23, captureState23()); done.done(false); return; }
            adapterMatches23 = out.optInt("matches", -1); adapterClicked23 = out.optBoolean("clicked", false);
            if (!out.optBoolean("success", false) || adapterMatches23 != 1 || !adapterClicked23) {
                adapterPending23 = false;
                if (adapterClicked23) { adapterStatus23 = "UNCERTAIN_POST_CLICK_RESULT_INVALID"; prefs23.edit().putString("claim_status", "UNCERTAIN").commit(); }
                else { adapterStatus23 = "ABORTED_NO_SIDE_EFFECT_MATCHES_" + adapterMatches23; prefs23.edit().putString("claim_status", "ABORTED_NO_SIDE_EFFECT").commit(); }
                JSONObject s = captureState23(); put23(s, "adapter_result", out); adapterEvent23(action + "_DISPATCH", adapterStatus23, s); done.done(false); return;
            }
            adapterStatus23 = "DISPATCHED_WAITING_RECEIPT"; prefs23.edit().putString("claim_status", "DISPATCHED").commit();
            JSONObject s = captureState23(); put23(s, "adapter_result", out); adapterEvent23(action + "_DISPATCH", "SINGLE_EXACT_ARIA_CLICK", s);
            pollActiveExit23(action, baselineUsers, System.currentTimeMillis() + 10500L, done);
        });
    }

    private void pollActiveExit23(String action, int baselineUsers, long deadline, AdapterDone23 done) {
        if (!adapterPending23) return;
        readLifecycle23(s -> {
            if (!adapterPending23) return;
            if (s.optBoolean("success", false)) {
                adapterSubmit23 = s.optInt("submit_count", -1); adapterCancel23 = s.optInt("cancel_count", -1); adapterReady23 = s.optInt("ready_dictation_count", -1); adapterUsers23 = s.optInt("user_turn_count", -1);
                if (baselineUsers >= 0 && adapterUsers23 > baselineUsers) { adapterPending23 = false; adapterStatus23 = "UNEXPECTED_USER_TURN_AFTER_" + action; prefs23.edit().putString("claim_status", "UNEXPECTED_SIDE_EFFECT").commit(); adapterEvent23(action + "_RECEIPT", adapterStatus23, captureState23()); done.done(false); return; }
                boolean activeGone = adapterSubmit23 == 0 && adapterCancel23 == 0;
                boolean readyReturned = adapterReady23 >= 1 || intField23("dictationCount") >= 1;
                if (activeGone && readyReturned) {
                    adapterPending23 = false; adapterStatus23 = "CONFIRMED_ACTIVE_DICTATION_EXIT_READY_RETURNED";
                    prefs23.edit().putString("claim_status", "CONFIRMED").putString("claim_receipt", "ACTIVE_DICTATION_EXIT_READY_RETURNED").commit();
                    setField23("micLeaseMode", "NONE"); setField23("micLeaseUntil", 0L); setField23("lastAction", action); setField23("lastActionStatus", "CONFIRMED_V23_ACTIVE_DICTATION_EXIT_READY_RETURNED"); setField23("last18Action", action); setField23("last18Status", "CONFIRMED_V23_ACTIVE_DICTATION_EXIT_READY_RETURNED");
                    adapterEvent23(action + "_RECEIPT", adapterStatus23, captureState23()); done.done(true); return;
                }
            }
            if (System.currentTimeMillis() >= deadline) { adapterPending23 = false; adapterStatus23 = "UNCERTAIN_EXIT_RECEIPT_TIMEOUT"; prefs23.edit().putString("claim_status", "UNCERTAIN").putString("claim_receipt", "EXIT_RECEIPT_TIMEOUT").commit(); JSONObject state = captureState23(); put23(state, "last_lifecycle", s); adapterEvent23(action + "_RECEIPT", adapterStatus23, state); done.done(false); return; }
            h23.postDelayed(() -> pollActiveExit23(action, baselineUsers, deadline, done), 300L);
        });
    }

    private void adapterEvent23(String phase, String classification, JSONObject state) { if (running23) phase23(phase, classification, state); else log23("MANUAL " + phase + " " + classification); }
    private void failAndRecover23(String classification) { if (!running23) return; if ("RUNNING".equals(finalClassification23)) finalClassification23 = classification; phase23("FAILURE", classification, captureState23()); recoverSession23(); }

    private void recoverSession23() {
        if (!running23) return;
        setStatus23("Recovering session...");
        phase23("BEFORE_RECOVERY", "RUNNING", captureState23());
        JSONObject click = "ACTIVE".equals(stringField23("sessionState")) ? clickButton23("SESSION END") : clickResult23("SESSION END", false, false, "already_not_active");
        JSONObject s = captureState23(); put23(s, "click", click); phase23("RECOVERY_DISPATCH", "RUNNING", s);
        waitUntil23(this::recoveryComplete23, 5500L, () -> finishAfterRecovery23(true), () -> finishAfterRecovery23(false));
    }

    private boolean recoveryComplete23() { return "IDLE".equals(stringField23("sessionState")) && "NONE".equals(stringField23("micLeaseMode")); }

    private void finishAfterRecovery23(boolean recovered) {
        if (!running23) return;
        if ("RUNNING".equals(finalClassification23)) {
            boolean allPass = cancelClassification23.startsWith("PASS_") && stopClassification23.startsWith("PASS_") && transcriptClassification23.startsWith("PASS_") && sendClassification23.startsWith("PASS_");
            finalClassification23 = allPass && recovered ? "PASS_DICTATION_ONE_TAP_E2E_RECOVERED" : allPass ? "DICTATION_E2E_RECOVERY_FAILED" : "DICTATION_E2E_INCOMPLETE" + (recovered ? "_RECOVERED" : "_RECOVERY_FAILED");
        } else finalClassification23 = finalClassification23 + (recovered ? "_RECOVERED" : "_RECOVERY_FAILED");
        JSONObject s = captureState23(); put23(s, "recovered", recovered); put23(s, "final_classification", finalClassification23); phase23("RECOVERY_RESULT", recovered ? "RECOVERED" : "RECOVERY_FAILED", s);
        h23.removeCallbacks(globalWatchdog23); finalizeReport23();
    }

    private void onGlobalWatchdog23() {
        if (!running23) return;
        finalClassification23 = "GLOBAL_TIMEOUT_AT_" + currentPhase23;
        JSONObject s = captureState23(); put23(s, "watchdog_ms", GLOBAL_WATCHDOG_MS); phase23("GLOBAL_WATCHDOG", finalClassification23, s);
        running23 = false; adapterPending23 = false;
        try { if ("ACTIVE".equals(stringField23("sessionState"))) clickButton23("SESSION END"); } catch (Exception ignored) {}
        h23.postDelayed(() -> { saveLocalReport23(); persistRun23(false, "WATCHDOG_FINISHED"); if (runButton23 != null) { runButton23.setEnabled(true); runButton23.setText("RUN AGAIN"); } setStatus23("TEST STOPPED SAFELY - watchdog timeout; local report saved"); postPhaseBestEffort23("WATCHDOG_FINAL", finalClassification23, captureState23()); }, 5600L);
    }

    private void readLifecycle23(JsonCallback23 cb) { evalJson23(DictationLifecycleAdapterV23.stateJs(), EVAL_TIMEOUT_MS, cb); }

    private void evalJson23(String js, long timeoutMs, JsonCallback23 cb) {
        if (web23 == null) { JSONObject o = new JSONObject(); put23(o, "success", false); put23(o, "reason", "WebViewMissing"); cb.done(o); return; }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> { if (!once.compareAndSet(false, true)) return; JSONObject o = new JSONObject(); put23(o, "success", false); put23(o, "eval_timeout", true); put23(o, "reason", "EVAL_CALLBACK_TIMEOUT"); cb.done(o); };
        h23.postDelayed(timeout, timeoutMs);
        try {
            web23.evaluateJavascript(js, value -> { if (!once.compareAndSet(false, true)) return; h23.removeCallbacks(timeout); cb.done(decodeJson23(value)); });
        } catch (Exception e) {
            if (once.compareAndSet(false, true)) { h23.removeCallbacks(timeout); JSONObject o = new JSONObject(); put23(o, "success", false); put23(o, "reason", "EVAL_THROW_" + e.getClass().getSimpleName()); cb.done(o); }
        }
    }

    private void phase23(String phase, String classification, JSONObject state) { currentPhase23 = phase; int seq = ++seq23; persistRun23(true, phase); log23("PHASE " + seq + " " + phase + " " + classification); postPayloadBestEffort23(payload23(phase, classification, state, seq), seq); }
    private void postPhaseBestEffort23(String phase, String classification, JSONObject state) { int seq = ++seq23; log23("PHASE " + seq + " " + phase + " " + classification); postPayloadBestEffort23(payload23(phase, classification, state, seq), seq); }
    private void postPayloadBestEffort23(JSONObject payload, int seq) { if (!TelemetryConfigV23.isConfigured()) return; new Thread(() -> uploadJson23(payload, NET_TIMEOUT_MS), "cp23-telemetry-" + seq).start(); }

    private void finalizeReport23() {
        saveLocalReport23();
        setStatus23("Finalizing report...");
        int seq = ++seq23;
        JSONObject payload = payload23("FINAL", finalClassification23, captureState23(), seq);
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> { if (!once.compareAndSet(false, true)) return; finishLocally23("TEST COMPLETE - local report saved; remote final timed out"); };
        h23.postDelayed(timeout, 6000L);
        new Thread(() -> {
            JSONObject r = uploadJson23(payload, NET_TIMEOUT_MS);
            runOnUiThread(() -> { if (!once.compareAndSet(false, true)) return; h23.removeCallbacks(timeout); finishLocally23(r.optBoolean("success", false) ? "TEST COMPLETE - report uploaded + local copy saved. Tell ChatGPT: test finished" : "TEST COMPLETE - local report saved; remote final unavailable"); });
        }, "cp23-final").start();
    }

    private JSONObject payload23(String phase, String classification, JSONObject state, int seq) {
        JSONObject p = new JSONObject();
        put23(p, "kind", "TEST_PHASE"); put23(p, "schema_version", SCHEMA_VERSION); put23(p, "scenario_id", SCENARIO_ID); put23(p, "scenario_version", SCENARIO_VERSION); put23(p, "test_id", testId23); put23(p, "seq", seq); put23(p, "phase", phase); put23(p, "classification", classification); put23(p, "app_version", appVersion23()); put23(p, "source_ref", TelemetryConfigV23.SOURCE_REF); put23(p, "collector_id", TelemetryConfigV23.COLLECTOR_ID); put23(p, "elapsed_ms", startedAt23 == 0L ? 0L : System.currentTimeMillis() - startedAt23); put23(p, "timestamp_epoch_ms", System.currentTimeMillis()); put23(p, "privacy", "counts_lengths_hashes_receipts_no_raw_audio_speech_transcript_chat_or_credentials"); put23(p, "state", state == null ? new JSONObject() : state);
        return p;
    }

    private JSONObject uploadJson23(JSONObject payload, int timeoutMs) {
        JSONObject result = new JSONObject(); put23(result, "configured", TelemetryConfigV23.isConfigured());
        if (!TelemetryConfigV23.isConfigured()) { put23(result, "success", false); put23(result, "error", "TelemetryNotConfigured"); return result; }
        HttpURLConnection conn = null;
        try {
            URL url = new URL(TelemetryConfigV23.WEBHOOK_URL); conn = (HttpURLConnection) url.openConnection(); conn.setRequestMethod("POST"); conn.setConnectTimeout(timeoutMs); conn.setReadTimeout(timeoutMs); conn.setDoOutput(true); conn.setRequestProperty("Content-Type", "application/json; charset=utf-8"); conn.setRequestProperty("Accept", "text/plain, application/json"); conn.setRequestProperty("X-Probe-Schema", SCHEMA_VERSION);
            byte[] body = payload.toString().getBytes(StandardCharsets.UTF_8); conn.setFixedLengthStreamingMode(body.length); try (OutputStream os = conn.getOutputStream()) { os.write(body); }
            int code = conn.getResponseCode(); put23(result, "http_status", code); put23(result, "success", code >= 200 && code < 300);
        } catch (Exception e) { put23(result, "success", false); put23(result, "error", e.getClass().getSimpleName()); }
        finally { if (conn != null) conn.disconnect(); }
        return result;
    }

    private JSONObject captureState23() {
        JSONObject o = new JSONObject();
        put23(o, "phase", currentPhase23); put23(o, "session_state", stringField23("sessionState")); put23(o, "mic_lease_mode", stringField23("micLeaseMode")); put23(o, "snapshot_ok", boolField23("snapOk")); put23(o, "dictation_count", intField23("dictationCount")); put23(o, "composer_len", intField23("composerLen")); put23(o, "composer_hash", stringField23("composerHash")); put23(o, "user_turn_count", intField23("userCount")); put23(o, "parent_last_action", stringField23("lastAction")); put23(o, "parent_last_status", stringField23("lastActionStatus")); put23(o, "wrapper_last_status", stringField23("lastWrapperStatus")); put23(o, "forced_session_end_count", intField23("forcedSessionEnds")); put23(o, "adapter_action", adapterAction23); put23(o, "adapter_status", adapterStatus23); put23(o, "adapter_pending", adapterPending23); put23(o, "adapter_matches", adapterMatches23); put23(o, "adapter_clicked", adapterClicked23); put23(o, "adapter_submit_count", adapterSubmit23); put23(o, "adapter_cancel_count", adapterCancel23); put23(o, "adapter_ready_count", adapterReady23); put23(o, "adapter_user_turns", adapterUsers23); put23(o, "cancel_classification", cancelClassification23); put23(o, "stop_classification", stopClassification23); put23(o, "transcript_classification", transcriptClassification23); put23(o, "send_classification", sendClassification23); put23(o, "final_classification", finalClassification23); put23(o, "webview_present", web23 != null); put23(o, "telemetry_preflight_ok", telemetryHealthy23); put23(o, "raw_audio_uploaded", false); put23(o, "raw_speech_uploaded", false); put23(o, "raw_transcript_uploaded", false); put23(o, "raw_chat_text_uploaded", false);
        return o;
    }

    private void saveLocalReport23() {
        try {
            JSONObject o = captureState23(); put23(o, "test_id", testId23); put23(o, "schema_version", SCHEMA_VERSION); put23(o, "scenario_id", SCENARIO_ID); put23(o, "events", events23.toString());
            String name = "chatgpt-webview-v23-report-" + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".json";
            ContentValues cv = new ContentValues(); cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name); cv.put(MediaStore.MediaColumns.MIME_TYPE, "application/json"); cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv); if (u == null) return;
            try (OutputStream os = getContentResolver().openOutputStream(u)) { if (os != null) os.write(o.toString(2).getBytes(StandardCharsets.UTF_8)); }
        } catch (Exception ignored) {}
    }

    private void finishLocally23(String message) { h23.removeCallbacks(globalWatchdog23); h23.removeCallbacksAndMessages(null); running23 = false; persistRun23(false, "FINISHED"); saveLocalReport23(); if (runButton23 != null) { runButton23.setEnabled(true); runButton23.setText("RUN AGAIN"); } if (status23 != null) status23.setText(message); log23("STATUS " + message); }
    private void reportInterruptedRun23() { if (!prefs23.getBoolean("run_active", false)) return; testId23 = prefs23.getString("test_id", "cp23-interrupted-unknown"); currentPhase23 = prefs23.getString("phase", "UNKNOWN"); finalClassification23 = "RUN_INTERRUPTED_APP_RESTART"; prefs23.edit().putBoolean("run_active", false).apply(); postPhaseBestEffort23("RUN_INTERRUPTED_APP_RESTART", "FAIL", captureState23()); setStatus23("Previous interrupted run reported. Ready for a new one-tap test."); }
    private boolean dictationStartObserved23() { String lease = stringField23("micLeaseMode"), parent = stringField23("lastActionStatus"), wrapper = stringField23("lastWrapperStatus"); return "DICTATION".equals(lease) && (parent.contains("CONFIRMED") || parent.contains("ACCEPTED_REVERSIBLE_START") || wrapper.contains("CONFIRMED") || wrapper.contains("ACCEPTED_REVERSIBLE_START")); }

    private void waitUntil23(Condition23 condition, long timeoutMs, Runnable success, Runnable timeout) {
        long start = System.currentTimeMillis(); Runnable[] poll = new Runnable[1];
        poll[0] = () -> { if (!running23) return; boolean ok = false; try { ok = condition.ok(); } catch (Exception ignored) {} if (ok) { success.run(); return; } if (System.currentTimeMillis() - start >= timeoutMs) { timeout.run(); return; } h23.postDelayed(poll[0], 250L); };
        h23.post(poll[0]);
    }

    private JSONObject clickButton23(String exactText) { Button b = findButton23(getWindow().getDecorView(), exactText); JSONObject o = new JSONObject(); put23(o, "requested", exactText); put23(o, "found", b != null); if (b == null) { put23(o, "clicked", false); return o; } boolean enabled = b.isEnabled(), visible = b.getVisibility() == View.VISIBLE; put23(o, "enabled", enabled); put23(o, "visible", visible); boolean clicked = false; if (enabled && visible) try { clicked = b.performClick(); } catch (Exception ignored) {} put23(o, "clicked", clicked); return o; }
    private JSONObject clickResult23(String requested, boolean found, boolean clicked, String reason) { JSONObject o = new JSONObject(); put23(o, "requested", requested); put23(o, "found", found); put23(o, "clicked", clicked); put23(o, "reason", reason); return o; }
    private Button findButton23(View v, String exactText) { if (v instanceof Button) { Button b = (Button) v; if (exactText.equals(String.valueOf(b.getText()))) return b; } if (v instanceof ViewGroup) { ViewGroup g = (ViewGroup) v; for (int i = 0; i < g.getChildCount(); i++) { Button b = findButton23(g.getChildAt(i), exactText); if (b != null) return b; } } return null; }
    private JSONObject decodeJson23(String value) { try { Object decoded = new JSONTokener(value == null ? "null" : value).nextValue(); String text = decoded instanceof String ? (String) decoded : String.valueOf(decoded); return new JSONObject(text); } catch (Exception e) { JSONObject o = new JSONObject(); put23(o, "success", false); put23(o, "reason", "JSON_DECODE_" + e.getClass().getSimpleName()); return o; } }
    private Field field23(String name) { Class<?> c = getClass(); while (c != null) { try { Field f = c.getDeclaredField(name); f.setAccessible(true); return f; } catch (Exception ignored) { c = c.getSuperclass(); } } return null; }
    private String stringField23(String name) { try { Field f = field23(name); if (f == null) return "UNKNOWN"; Object v = f.get(this); return v == null ? "NONE" : String.valueOf(v); } catch (Exception e) { return "ERROR"; } }
    private int intField23(String name) { try { Field f = field23(name); return f == null ? -1 : f.getInt(this); } catch (Exception e) { return -1; } }
    private boolean boolField23(String name) { try { Field f = field23(name); return f != null && f.getBoolean(this); } catch (Exception e) { return false; } }
    private void setField23(String name, Object value) { try { Field f = field23(name); if (f == null) return; if (value instanceof Long) f.setLong(this, (Long) value); else if (value instanceof Integer) f.setInt(this, (Integer) value); else if (value instanceof Boolean) f.setBoolean(this, (Boolean) value); else f.set(this, value); } catch (Exception ignored) {} }
    private WebView findWeb23(View v) { if (v instanceof WebView) return (WebView) v; if (v instanceof ViewGroup) { ViewGroup g = (ViewGroup) v; for (int i = 0; i < g.getChildCount(); i++) { WebView w = findWeb23(g.getChildAt(i)); if (w != null) return w; } } return null; }
    private void beep23() { try { ToneGenerator t = new ToneGenerator(AudioManager.STREAM_NOTIFICATION, 70); t.startTone(ToneGenerator.TONE_PROP_BEEP, 160); h23.postDelayed(t::release, 280L); } catch (Exception ignored) {} }
    private String appVersion23() { try { PackageInfo pi = getPackageManager().getPackageInfo(getPackageName(), 0); return pi.versionName + "(" + pi.getLongVersionCode() + ")"; } catch (Exception e) { return "unknown"; } }
    private int dp23(int x) { return Math.round(x * getResources().getDisplayMetrics().density); }
    private void setStatus23(String s) { if (status23 != null) status23.setText(s); log23("STATUS " + s); }
    private void log23(String s) { String safe = s == null ? "" : s.replace('\n', ' '); if (safe.length() > 700) safe = safe.substring(0, 700); events23.append(System.currentTimeMillis()).append(" | ").append(safe).append('\n'); }
    private void persistRun23(boolean active, String phase) { if (prefs23 == null) return; prefs23.edit().putBoolean("run_active", active).putString("test_id", testId23).putInt("seq", seq23).putLong("started_at", startedAt23).putString("phase", phase).apply(); }
    private void put23(JSONObject o, String k, Object v) { try { o.put(k, v); } catch (Exception ignored) {} }
    @Override protected void onDestroy() { h23.removeCallbacksAndMessages(null); super.onDestroy(); }
}
