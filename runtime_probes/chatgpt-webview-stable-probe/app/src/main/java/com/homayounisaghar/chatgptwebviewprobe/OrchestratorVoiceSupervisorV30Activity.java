package com.homayounisaghar.chatgptwebviewprobe;

import android.Manifest;
import android.content.ContentValues;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.MediaStore;
import android.text.TextUtils;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewParent;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.OutputStream;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Stable v0.30 — full Voice supervisor using contextual mic-toggle receipts.
 *
 * v0.29 proved that current ChatGPT Voice activates after the unique Start click:
 * by ~1.2s there is one stable Voice End control and one stable microphone-feature
 * button. The old v0.28 timeout was a false negative caused by exact Mute/Unmute
 * wording assumptions. v0.30 therefore treats the unique active mic button as a
 * contextual toggle and proves state changes by fingerprint/state transitions.
 *
 * Strong-write rules remain unchanged: durable claim before every possible click,
 * at most one click per claim, bounded receipt, no blind replay, hard Session-End
 * recovery. No coordinates/XPath/private ChatGPT APIs/cookies/tokens/raw text/audio.
 */
public class OrchestratorVoiceSupervisorV30Activity extends OrchestratorVoicePostStartCensusV29Activity {
    private static final String PREFS30 = "stable_v30_voice_supervisor_contextual";
    private static final String SCHEMA30 = "cp-v30-voice-supervisor-contextual-v1";
    private static final String SCENARIO30 = "voice-start-mic-toggle-mute-unmute-end-e2e";
    private static final long GLOBAL_WATCHDOG_MS = 70000L;
    private static final long EVAL_TIMEOUT_MS = 2600L;
    private static final long LIVE_LEASE_MS = 10L * 60L * 1000L;
    private static final int NET_TIMEOUT_MS = 2800;
    private static final int EXPECTED_EVENT_BUDGET = 32;

    private final Handler h30 = new Handler(Looper.getMainLooper());
    private final Runnable watchdog30 = this::onWatchdog30;
    private SharedPreferences prefs30;
    private WebView web30;
    private Button run30;
    private TextView status30;

    private boolean running30 = false;
    private boolean telemetryHealthy30 = false;
    private String testId30 = "-";
    private int seq30 = 0;
    private long startedAt30 = 0L;
    private String finalClassification30 = "NOT_RUN";
    private String currentClaimAction30 = "NONE";
    private String currentClaimStatus30 = "NONE";
    private int dispatchedSideEffects30 = 0;
    private String baselineMicFingerprint30 = "-";
    private String baselineMicState30 = "unknown";
    private String mutedMicFingerprint30 = "-";
    private String mutedMicState30 = "unknown";
    private String unmutedMicFingerprint30 = "-";
    private boolean unmuteReturnedBaseline30 = false;

    private interface JsonDone30 { void done(JSONObject result); }
    private interface Condition30 { boolean ok(); }
    private interface ScanPredicate30 { boolean ok(JSONObject scan); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs30 = getSharedPreferences(PREFS30, MODE_PRIVATE);
        web30 = findWeb30(getWindow().getDecorView());
        compactUi30();
        setStatus30("v0.30 Voice supervisor ready");
        reportInterrupted30();
    }

    @Override protected void onDestroy() {
        h30.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    /** Remove inherited manual diagnostic panels and let the WebView fill the main area. */
    private void compactUi30() {
        if (web30 == null) return;
        ViewParent p = web30.getParent();
        if (!(p instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) p;
        for (int i = 0; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            if (child != web30) child.setVisibility(View.GONE);
        }
        LinearLayout.LayoutParams wlp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f);
        web30.setMinimumHeight(1);
        web30.setLayoutParams(wlp);

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp30(8), dp30(3), dp30(8), dp30(6));

        status30 = new TextView(this);
        status30.setTextSize(11f);
        status30.setSingleLine(true);
        status30.setEllipsize(TextUtils.TruncateAt.END);
        status30.setPadding(dp30(4), dp30(2), dp30(4), dp30(2));
        panel.addView(status30, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));

        run30 = new Button(this);
        run30.setText("RUN VOICE TEST");
        run30.setTextSize(13f);
        run30.setAllCaps(false);
        run30.setOnClickListener(v -> runVoiceTest30());
        panel.addView(run30, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp30(46)));

        root.addView(panel, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void runVoiceTest30() {
        if (running30) return;
        if (web30 == null || !trusted30(web30.getUrl())) {
            setStatus30("Blocked: ChatGPT WebView not ready");
            return;
        }
        running30 = true;
        telemetryHealthy30 = false;
        testId30 = "cp30-" + UUID.randomUUID();
        seq30 = 0;
        startedAt30 = System.currentTimeMillis();
        finalClassification30 = "RUNNING";
        currentClaimAction30 = "NONE";
        currentClaimStatus30 = "NONE";
        dispatchedSideEffects30 = 0;
        baselineMicFingerprint30 = "-";
        baselineMicState30 = "unknown";
        mutedMicFingerprint30 = "-";
        mutedMicState30 = "unknown";
        unmutedMicFingerprint30 = "-";
        unmuteReturnedBaseline30 = false;
        if (run30 != null) { run30.setEnabled(false); run30.setText("VOICE TEST RUNNING..."); }
        persistRun30(true, "TELEMETRY_PREFLIGHT");
        setStatus30("Telemetry preflight...");
        h30.removeCallbacks(watchdog30);
        h30.postDelayed(watchdog30, GLOBAL_WATCHDOG_MS);
        telemetryPreflight30();
    }

    private void telemetryPreflight30() {
        JSONObject s = captureState30();
        put30(s, "collector_capacity_hint", TelemetryConfigV30.COLLECTOR_CAPACITY_HINT);
        put30(s, "expected_event_budget", EXPECTED_EVENT_BUDGET);
        JSONObject p = payload30("TELEMETRY_PREFLIGHT", "RUNNING", s, 0);
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!running30 || !once.compareAndSet(false, true)) return;
            telemetryHealthy30 = false;
            finishNoSideEffect30("TELEMETRY_PREFLIGHT_TIMEOUT");
        };
        h30.postDelayed(timeout, 8000L);
        new Thread(() -> {
            JSONObject r = uploadJson30(p, NET_TIMEOUT_MS + 900);
            runOnUiThread(() -> {
                if (!running30 || !once.compareAndSet(false, true)) return;
                h30.removeCallbacks(timeout);
                if (!r.optBoolean("success", false)) {
                    telemetryHealthy30 = false;
                    finishNoSideEffect30("TELEMETRY_UNAVAILABLE");
                    return;
                }
                telemetryHealthy30 = true;
                phase30("RUN_STARTED", "RUNNING", captureState30());
                precondition30();
            });
        }, "cp30-preflight").start();
    }

    private void precondition30() {
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            finishNoSideEffect30("BLOCKED_ANDROID_RECORD_AUDIO_NOT_GRANTED");
            return;
        }
        if (!"IDLE".equals(parentString30("sessionState")) || !"NONE".equals(parentString30("micLeaseMode"))) {
            phase30("PRECONDITION", "DIRTY_SESSION_OR_MIC_LEASE", captureState30());
            recover30("DIRTY_INITIAL_STATE");
            return;
        }
        setStatus30("Checking ready Voice control...");
        scan30("NONE", false, scan -> {
            JSONObject s = withScan30(captureState30(), scan);
            if (!scanComplete30(scan)) {
                phase30("READY_VOICE_CENSUS", "FAIL_INCOMPLETE_SCAN", s);
                finishNoSideEffect30("READY_VOICE_SCAN_INCOMPLETE");
                return;
            }
            if (!readyVoice30(scan)) {
                phase30("READY_VOICE_CENSUS", "FAIL_UNIQUE_START_VOICE_NOT_READY", s);
                finishNoSideEffect30("READY_VOICE_START_NOT_UNIQUE");
                return;
            }
            phase30("READY_VOICE_CENSUS", "PASS_UNIQUE_START_VOICE_READY", s);
            startSession30();
        });
    }

    private void startSession30() {
        setStatus30("Starting InteractionSession...");
        boolean invoked = invokeAncestor30("toggleSession", new Class<?>[0], new Object[0]);
        JSONObject s = captureState30(); put30(s, "session_start_invoked", invoked);
        phase30("SESSION_START_DISPATCH", invoked ? "REQUESTED" : "REFLECTION_FAIL", s);
        if (!invoked) { recover30("SESSION_START_NOT_DISPATCHED"); return; }
        waitCondition30(() -> "ACTIVE".equals(parentString30("sessionState")), 4000L,
                () -> {
                    phase30("SESSION_ACTIVE", "PASS", captureState30());
                    h30.postDelayed(this::gateVoiceStart30, 300L);
                },
                () -> recover30("SESSION_START_NOT_CONFIRMED"));
    }

    private void gateVoiceStart30() {
        scan30("NONE", false, scan -> {
            JSONObject s = withScan30(captureState30(), scan);
            if (!scanComplete30(scan) || !readyVoice30(scan)) {
                phase30("VOICE_START_GATE", "FAIL_NOT_UNIQUE_READY", s);
                recover30("VOICE_START_GATE_FAILED");
                return;
            }
            phase30("VOICE_START_GATE", "PASS_UNIQUE_READY", s);
            setStatus30("1/4 Starting Voice...");
            dispatch30("VOICE_START", "VOICE_START", scan, dispatched -> {
                if (!dispatched) { recover30("VOICE_START_NOT_DISPATCHED"); return; }
                waitScan30(x -> activeContext30(x) && "LIVE".equals(parentString30("micLeaseMode")), 10000L,
                        receipt -> {
                            baselineMicFingerprint30 = micFingerprint30(receipt);
                            baselineMicState30 = receipt.optString("mic_toggle_state", "unknown");
                            if ("-".equals(baselineMicFingerprint30)) {
                                uncertainAndRecover30("VOICE_START", "VOICE_START_MIC_BASELINE_MISSING");
                                return;
                            }
                            confirmClaim30("VOICE_START", "VOICE_ACTIVE_CONTEXT_CONFIRMED");
                            JSONObject rs = withScan30(captureState30(), receipt);
                            put30(rs, "baseline_mic_fingerprint", baselineMicFingerprint30);
                            put30(rs, "baseline_mic_state", baselineMicState30);
                            phase30("VOICE_START_RECEIPT", "PASS_END_PLUS_UNIQUE_MIC_TOGGLE", rs);
                            mute30(receipt);
                        },
                        () -> uncertainAndRecover30("VOICE_START", "VOICE_START_RECEIPT_TIMEOUT"));
            });
        });
    }

    private void mute30(JSONObject baseline) {
        if (!activeContext30(baseline)) { recover30("VOICE_MUTE_PRECONDITION_LOST"); return; }
        setStatus30("2/4 Muting...");
        dispatch30("VOICE_MUTE", "MIC_TOGGLE", baseline, dispatched -> {
            if (!dispatched) { recover30("VOICE_MUTE_NOT_DISPATCHED"); return; }
            waitScan30(x -> activeContext30(x) && micTransition30(x, baselineMicFingerprint30, baselineMicState30), 7000L,
                    receipt -> {
                        mutedMicFingerprint30 = micFingerprint30(receipt);
                        mutedMicState30 = receipt.optString("mic_toggle_state", "unknown");
                        confirmClaim30("VOICE_MUTE", "MIC_TOGGLE_TRANSITION_CONFIRMED");
                        JSONObject rs = withScan30(captureState30(), receipt);
                        put30(rs, "baseline_mic_fingerprint", baselineMicFingerprint30);
                        put30(rs, "muted_mic_fingerprint", mutedMicFingerprint30);
                        put30(rs, "muted_mic_state", mutedMicState30);
                        phase30("VOICE_MUTE_RECEIPT", "PASS_CONTEXTUAL_MIC_TOGGLE_TRANSITION", rs);
                        unmute30(receipt);
                    },
                    () -> uncertainAndRecover30("VOICE_MUTE", "VOICE_MUTE_RECEIPT_TIMEOUT"));
        });
    }

    private void unmute30(JSONObject muted) {
        if (!activeContext30(muted)) { recover30("VOICE_UNMUTE_PRECONDITION_LOST"); return; }
        setStatus30("3/4 Unmuting...");
        dispatch30("VOICE_UNMUTE", "MIC_TOGGLE", muted, dispatched -> {
            if (!dispatched) { recover30("VOICE_UNMUTE_NOT_DISPATCHED"); return; }
            waitScan30(x -> activeContext30(x) && micTransition30(x, mutedMicFingerprint30, mutedMicState30), 7000L,
                    receipt -> {
                        unmutedMicFingerprint30 = micFingerprint30(receipt);
                        unmuteReturnedBaseline30 = baselineMicFingerprint30.equals(unmutedMicFingerprint30)
                                || (!"unknown".equals(baselineMicState30)
                                && baselineMicState30.equals(receipt.optString("mic_toggle_state", "unknown")));
                        confirmClaim30("VOICE_UNMUTE", "SECOND_MIC_TOGGLE_TRANSITION_CONFIRMED");
                        JSONObject rs = withScan30(captureState30(), receipt);
                        put30(rs, "muted_mic_fingerprint", mutedMicFingerprint30);
                        put30(rs, "unmuted_mic_fingerprint", unmutedMicFingerprint30);
                        put30(rs, "returned_to_baseline", unmuteReturnedBaseline30);
                        phase30("VOICE_UNMUTE_RECEIPT",
                                unmuteReturnedBaseline30 ? "PASS_RETURNED_TO_BASELINE" : "PASS_SECOND_CONTEXTUAL_TRANSITION", rs);
                        stableHold30();
                    },
                    () -> uncertainAndRecover30("VOICE_UNMUTE", "VOICE_UNMUTE_RECEIPT_TIMEOUT"));
        });
    }

    private void stableHold30() {
        phase30("VOICE_STABLE_HOLD_STARTED", "RUNNING", captureState30());
        setStatus30("Holding active Voice briefly...");
        h30.postDelayed(() -> scan30("NONE", false, scan -> {
            JSONObject s = withScan30(captureState30(), scan);
            String now = micFingerprint30(scan);
            boolean stable = scanComplete30(scan) && activeContext30(scan)
                    && "LIVE".equals(parentString30("micLeaseMode"))
                    && !"-".equals(unmutedMicFingerprint30)
                    && unmutedMicFingerprint30.equals(now);
            if (!stable) {
                phase30("VOICE_STABLE_HOLD_RESULT", "FAIL_ACTIVE_STATE_NOT_STABLE", s);
                recover30("VOICE_ACTIVE_HOLD_FAILED");
                return;
            }
            phase30("VOICE_STABLE_HOLD_RESULT", "PASS_ACTIVE_STABLE", s);
            endVoice30(scan);
        }), 1600L);
    }

    private void endVoice30(JSONObject baseline) {
        if (!activeContext30(baseline)) { recover30("VOICE_END_PRECONDITION_LOST"); return; }
        setStatus30("4/4 Ending Voice...");
        dispatch30("VOICE_END", "VOICE_END", baseline, dispatched -> {
            if (!dispatched) { recover30("VOICE_END_NOT_DISPATCHED"); return; }
            waitScan30(this::readyVoice30, 10000L,
                    receipt -> {
                        confirmClaim30("VOICE_END", "VOICE_READY_RETURNED");
                        invokeAncestor30("revokeLease", new Class<?>[]{String.class}, new Object[]{"V30_VOICE_END_CONFIRMED"});
                        phase30("VOICE_END_UI_RECEIPT", "PASS_READY_RETURNED", withScan30(captureState30(), receipt));
                        waitCondition30(() -> "NONE".equals(parentString30("micLeaseMode")), 2500L,
                                () -> {
                                    phase30("VOICE_END_RECEIPT", "PASS_READY_AND_LEASE_RELEASED", captureState30());
                                    endSession30();
                                },
                                () -> recover30("VOICE_END_LEASE_NOT_RELEASED"));
                    },
                    () -> uncertainAndRecover30("VOICE_END", "VOICE_END_RECEIPT_TIMEOUT"));
        });
    }

    private void endSession30() {
        setStatus30("Ending InteractionSession...");
        boolean invoked = invokeAncestor30("hardEndSession18", new Class<?>[0], new Object[0]);
        JSONObject s = captureState30(); put30(s, "hard_session_end_invoked", invoked);
        phase30("SESSION_END_DISPATCH", invoked ? "REQUESTED" : "REFLECTION_FAIL", s);
        if (!invoked) { recover30("SESSION_END_NOT_DISPATCHED"); return; }
        waitCondition30(() -> "IDLE".equals(parentString30("sessionState"))
                        && "NONE".equals(parentString30("micLeaseMode")), 4000L,
                () -> {
                    phase30("SESSION_END_RECEIPT", "PASS_IDLE_MIC_NONE", captureState30());
                    finalClassification30 = "PASS_VOICE_CONTEXTUAL_START_MUTE_UNMUTE_END_RECOVERED";
                    finish30();
                },
                () -> recover30("SESSION_END_NOT_CONFIRMED"));
    }

    private void dispatch30(String claimAction, String target, JSONObject knownScan,
                            java.util.function.Consumer<Boolean> done) {
        if (!running30) { done.accept(false); return; }
        if (!scanComplete30(knownScan) || targetCount30(knownScan, target) != 1) {
            done.accept(false); return;
        }
        if (!claim30(claimAction)) { done.accept(false); return; }
        if ("VOICE_START".equals(claimAction)) {
            if (!invokeAncestor30("acquireLease", new Class<?>[]{String.class, long.class},
                    new Object[]{"LIVE", LIVE_LEASE_MS})) {
                abortClaim30(claimAction, "LEASE_ARM_FAIL");
                done.accept(false); return;
            }
        }
        scan30(target, true, result -> {
            JSONObject s = withScan30(captureState30(), result);
            int matches = result.optInt("target_matches", -1);
            boolean clicked = result.optBoolean("clicked", false);
            if (!scanComplete30(result) || matches != 1 || !clicked) {
                abortClaim30(claimAction, !scanComplete30(result) ? "INCOMPLETE_SCAN" : "MATCHES_" + matches);
                if ("VOICE_START".equals(claimAction))
                    invokeAncestor30("revokeLease", new Class<?>[]{String.class}, new Object[]{"V30_START_NOT_DISPATCHED"});
                phase30(claimAction + "_DISPATCH", "ABORTED_NO_SIDE_EFFECT", s);
                done.accept(false); return;
            }
            dispatchedSideEffects30++;
            currentClaimStatus30 = "DISPATCHED";
            prefs30.edit().putString("claim_status", currentClaimStatus30).commit();
            phase30(claimAction + "_DISPATCH", "DISPATCHED_UNIQUE_SEMANTIC_CLICK", s);
            done.accept(true);
        });
    }

    private boolean claim30(String action) {
        String id = action + "_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0, 8);
        boolean ok = prefs30.edit().putString("claim_id", id).putString("claim_action", action)
                .putString("claim_status", "CLAIMED").commit();
        if (!ok) return false;
        currentClaimAction30 = action;
        currentClaimStatus30 = "CLAIMED";
        phase30(action + "_CLAIM", "DURABLE_CLAIMED", captureState30());
        return true;
    }

    private void confirmClaim30(String action, String receipt) {
        currentClaimAction30 = action;
        currentClaimStatus30 = "CONFIRMED";
        prefs30.edit().putString("claim_status", "CONFIRMED").putString("claim_receipt", receipt).commit();
    }

    private void abortClaim30(String action, String reason) {
        currentClaimAction30 = action;
        currentClaimStatus30 = "ABORTED_NO_SIDE_EFFECT_" + token30(reason);
        prefs30.edit().putString("claim_status", currentClaimStatus30).commit();
    }

    private void uncertainAndRecover30(String action, String reason) {
        currentClaimAction30 = action;
        currentClaimStatus30 = "UNCERTAIN_NO_REPLAY";
        prefs30.edit().putString("claim_status", currentClaimStatus30).putString("claim_receipt", reason).commit();
        phase30("ACTION_RECEIPT_UNCERTAIN", reason, captureState30());
        recover30(reason);
    }

    private void recover30(String reason) {
        if (!running30) return;
        phase30("RECOVERY_STARTED", reason, captureState30());
        setStatus30("Recovering safely...");
        boolean invoked = invokeAncestor30("hardEndSession18", new Class<?>[0], new Object[0]);
        JSONObject s = captureState30(); put30(s, "hard_session_end_invoked", invoked);
        phase30("RECOVERY_DISPATCH", invoked ? "SESSION_END_ESCAPE_REQUESTED" : "SESSION_END_REFLECTION_FAIL", s);
        if (!invoked) {
            finalClassification30 = reason + "_RECOVERY_DISPATCH_FAILED";
            finish30(); return;
        }
        waitCondition30(() -> "IDLE".equals(parentString30("sessionState"))
                        && "NONE".equals(parentString30("micLeaseMode")), 5000L,
                () -> {
                    phase30("RECOVERY_RESULT", "RECOVERED_IDLE_MIC_NONE", captureState30());
                    finalClassification30 = reason + "_RECOVERED";
                    finish30();
                },
                () -> {
                    finalClassification30 = reason + "_RECOVERY_TIMEOUT";
                    finish30();
                });
    }

    private void finishNoSideEffect30(String classification) {
        finalClassification30 = classification;
        finish30();
    }

    private void finish30() {
        if (!running30) return;
        h30.removeCallbacks(watchdog30);
        JSONObject s = captureState30();
        put30(s, "baseline_mic_fingerprint", baselineMicFingerprint30);
        put30(s, "muted_mic_fingerprint", mutedMicFingerprint30);
        put30(s, "unmuted_mic_fingerprint", unmutedMicFingerprint30);
        put30(s, "unmute_returned_baseline", unmuteReturnedBaseline30);
        phase30("FINAL", finalClassification30, s);
        persistRun30(false, "FINAL");
        saveLocal30(finalClassification30, s);
        running30 = false;
        if (run30 != null) { run30.setEnabled(true); run30.setText("RUN VOICE TEST"); }
        setStatus30("Done: " + finalClassification30);
    }

    private void onWatchdog30() {
        if (!running30) return;
        currentClaimStatus30 = currentClaimStatus30.startsWith("DISPATCHED") ? "UNCERTAIN_NO_REPLAY" : currentClaimStatus30;
        phase30("GLOBAL_WATCHDOG", "TIMEOUT", captureState30());
        recover30("GLOBAL_WATCHDOG_TIMEOUT");
    }

    private void scan30(String target, boolean click, JsonDone30 done) {
        evalJson30(voiceJs30(target, click), done);
    }

    private boolean scanComplete30(JSONObject s) {
        return s != null && s.optBoolean("success", false) && s.optBoolean("complete", false)
                && !s.optBoolean("budget_exceeded", true) && !s.optBoolean("truncated", true);
    }

    private boolean readyVoice30(JSONObject s) {
        return scanComplete30(s) && s.optInt("voice_start_count", -1) == 1
                && s.optInt("voice_end_count", -1) == 0;
    }

    private boolean activeContext30(JSONObject s) {
        return scanComplete30(s) && s.optInt("voice_start_count", -1) == 0
                && s.optInt("voice_end_count", -1) == 1
                && s.optInt("mic_toggle_count", -1) == 1;
    }

    private int targetCount30(JSONObject s, String target) {
        if ("VOICE_START".equals(target)) return s.optInt("voice_start_count", -1);
        if ("VOICE_END".equals(target)) return s.optInt("voice_end_count", -1);
        if ("MIC_TOGGLE".equals(target)) return s.optInt("mic_toggle_count", -1);
        return -1;
    }

    private String micFingerprint30(JSONObject s) {
        return s == null ? "-" : s.optString("mic_toggle_fingerprint", "-");
    }

    private boolean micTransition30(JSONObject s, String oldFingerprint, String oldState) {
        if (!activeContext30(s)) return false;
        String nf = micFingerprint30(s);
        String ns = s.optString("mic_toggle_state", "unknown");
        if (!"-".equals(oldFingerprint) && !oldFingerprint.equals(nf)) return true;
        return !"unknown".equals(oldState) && !oldState.equals(ns);
    }

    private void waitScan30(ScanPredicate30 predicate, long timeoutMs, JsonDone30 success, Runnable failure) {
        long deadline = System.currentTimeMillis() + timeoutMs;
        waitScanLoop30(predicate, deadline, success, failure);
    }

    private void waitScanLoop30(ScanPredicate30 predicate, long deadline, JsonDone30 success, Runnable failure) {
        if (!running30) return;
        scan30("NONE", false, scan -> {
            if (!running30) return;
            if (!scanComplete30(scan)) { failure.run(); return; }
            if (predicate.ok(scan)) { success.done(scan); return; }
            if (System.currentTimeMillis() >= deadline) { failure.run(); return; }
            h30.postDelayed(() -> waitScanLoop30(predicate, deadline, success, failure), 240L);
        });
    }

    private void waitCondition30(Condition30 condition, long timeoutMs, Runnable success, Runnable failure) {
        long deadline = System.currentTimeMillis() + timeoutMs;
        waitConditionLoop30(condition, deadline, success, failure);
    }

    private void waitConditionLoop30(Condition30 condition, long deadline, Runnable success, Runnable failure) {
        if (!running30) return;
        if (condition.ok()) { success.run(); return; }
        if (System.currentTimeMillis() >= deadline) { failure.run(); return; }
        h30.postDelayed(() -> waitConditionLoop30(condition, deadline, success, failure), 120L);
    }

    private String voiceJs30(String target, boolean click) {
        return "(function(){try{"
                + "const TARGET='" + js30(target) + "',DO=" + (click ? "true" : "false") + ";"
                + "const T=performance.now(),MAX_MS=180,MAX_NODES=7000,MAX_ROOTS=32;"
                + "const N=x=>String(x||'').replace(/\\s+/g,' ').trim();"
                + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "const V=e=>{try{const r=e.getBoundingClientRect(),w=e.ownerDocument&&e.ownerDocument.defaultView,s=w?w.getComputedStyle(e):getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
                + "const E=e=>{try{return !e.disabled&&String(e.getAttribute('aria-disabled')||'').toLowerCase()!=='true';}catch(_){return true;}};"
                + "const M=e=>{let z='';try{z+=' '+N(e.getAttribute('aria-label'))+' '+N(e.getAttribute('title'))+' '+N(e.getAttribute('data-testid'))+' '+N(e.getAttribute('name'))+' '+N(e.getAttribute('id'))+' '+N(e.getAttribute('data-state'))+' '+N(e.innerText||e.textContent||'');const st=e.querySelector&&e.querySelector('svg title');if(st)z+=' '+N(st.textContent||'');}catch(_){}return N(z).toLowerCase();};"
                + "const C=e=>{const a=N(e.getAttribute&&e.getAttribute('aria-label')).toLowerCase(),x=M(e);if(a==='start voice'||/voice mode|open voice|advanced voice|start voice/.test(x))return 'VOICE_START';if(/end voice|leave voice|exit voice|close voice|voice[^a-z]*close|end call|hang up|disconnect/.test(x))return 'VOICE_END';return 'OTHER';};"
                + "const roots=[document],seenR=new Set(),seenE=new Set(),controls=[];let nodes=0,budget=false,trunc=false;"
                + "for(let q=0;q<roots.length&&q<MAX_ROOTS;q++){if(performance.now()-T>MAX_MS){budget=true;break;}const r=roots[q];if(!r||seenR.has(r))continue;seenR.add(r);let all=[];try{all=[...r.querySelectorAll('*')];}catch(_){}for(const e of all){nodes++;if(nodes>MAX_NODES){trunc=true;break;}if(performance.now()-T>MAX_MS){budget=true;break;}try{if(e.shadowRoot&&roots.length<MAX_ROOTS)roots.push(e.shadowRoot);if(e.tagName==='IFRAME'&&e.contentDocument&&roots.length<MAX_ROOTS)roots.push(e.contentDocument);}catch(_){}}if(trunc||budget)break;let bs=[];try{bs=[...r.querySelectorAll('button,[role=button],[aria-label],[data-testid]')];}catch(_){}for(const e of bs){if(!seenE.has(e)&&V(e)&&E(e)){seenE.add(e);controls.push(e);}}}"
                + "const rows=controls.map(e=>{const x=M(e),c=C(e),tag=String(e.tagName||'').toUpperCase(),ds=N(e.getAttribute&&e.getAttribute('data-state')).toLowerCase(),ap=N(e.getAttribute&&e.getAttribute('aria-pressed')).toLowerCase();let state='unknown';if(/^(open|closed|on|off|active|inactive|true|false|pressed|unpressed)$/.test(ds))state=ds;else if(ap==='true'||ap==='false')state=ap==='true'?'pressed':'unpressed';const mic=/microphone|(^|[^a-z])mic([^a-z]|$)/.test(x),settings=/settings/.test(x);return {e:e,c:c,h:H(x),state:state,mic:mic&&!settings&&c==='OTHER'};});"
                + "const starts=rows.filter(x=>x.c==='VOICE_START'),ends=rows.filter(x=>x.c==='VOICE_END'),mics=rows.filter(x=>x.mic);"
                + "const complete=!budget&&!trunc;let tx=[];if(TARGET==='VOICE_START')tx=starts;else if(TARGET==='VOICE_END')tx=ends;else if(TARGET==='MIC_TOGGLE')tx=mics;let clicked=false;if(DO&&complete&&tx.length===1){tx[0].e.click();clicked=true;}"
                + "const mh=mics.length===1?mics[0].h:'-';const ms=mics.length===1?mics[0].state:'unknown';const mf=mics.length===1?H(mh+':'+ms):'-';"
                + "return JSON.stringify({success:true,complete:complete,budget_exceeded:budget,truncated:trunc,nodes:nodes,roots:seenR.size,visible_controls:controls.length,voice_start_count:starts.length,voice_end_count:ends.length,mic_toggle_count:mics.length,mic_toggle_hash:mh,mic_toggle_state:ms,mic_toggle_fingerprint:mf,semantic_set_hash:H(rows.filter(x=>x.c!=='OTHER').map(x=>x.c+':'+x.h).sort().join('|')),target_matches:tx.length,clicked:clicked});"
                + "}catch(e){return JSON.stringify({success:false,complete:false,budget_exceeded:false,truncated:false,error:String(e&&e.name||'ERR')});}})();";
    }

    private void evalJson30(String js, JsonDone30 done) {
        if (web30 == null) { done.done(errorJson30("NO_WEBVIEW")); return; }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (once.compareAndSet(false, true)) done.done(errorJson30("EVAL_TIMEOUT"));
        };
        h30.postDelayed(timeout, EVAL_TIMEOUT_MS);
        try {
            web30.evaluateJavascript(js, value -> {
                if (!once.compareAndSet(false, true)) return;
                h30.removeCallbacks(timeout);
                try { done.done(parseEval30(value)); }
                catch (Exception e) { done.done(errorJson30("EVAL_PARSE_" + e.getClass().getSimpleName())); }
            });
        } catch (Exception e) {
            if (once.compareAndSet(false, true)) {
                h30.removeCallbacks(timeout);
                done.done(errorJson30("EVAL_" + e.getClass().getSimpleName()));
            }
        }
    }

    private JSONObject parseEval30(String value) throws Exception {
        Object x = new JSONTokener(value == null ? "null" : value).nextValue();
        if (x instanceof String) x = new JSONTokener((String) x).nextValue();
        if (!(x instanceof JSONObject)) throw new IllegalStateException("not_object");
        return (JSONObject) x;
    }

    private JSONObject errorJson30(String error) {
        JSONObject x = new JSONObject(); put30(x, "success", false); put30(x, "complete", false); put30(x, "error", error); return x;
    }

    private JSONObject captureState30() {
        JSONObject s = new JSONObject();
        put30(s, "session_state", parentString30("sessionState"));
        put30(s, "mic_lease_mode", parentString30("micLeaseMode"));
        put30(s, "parent_last_action", parentString30("lastAction"));
        put30(s, "parent_last_status", parentString30("lastActionStatus"));
        put30(s, "permission_grants", parentInt30("permissionGrants"));
        put30(s, "permission_denials", parentInt30("permissionDenials"));
        put30(s, "active_audio_tracks", parentInt30("activeAudioTracks"));
        put30(s, "media_gum_calls", parentInt30("mediaGumCalls"));
        put30(s, "media_gum_resolves", parentInt30("mediaGumResolves"));
        put30(s, "media_gum_rejects", parentInt30("mediaGumRejects"));
        put30(s, "android_record_audio_granted", checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED);
        put30(s, "claim_action", currentClaimAction30);
        put30(s, "claim_status", currentClaimStatus30);
        put30(s, "dispatched_side_effects", dispatchedSideEffects30);
        put30(s, "raw_audio_uploaded", false);
        put30(s, "raw_speech_uploaded", false);
        put30(s, "raw_transcript_uploaded", false);
        put30(s, "raw_chat_text_uploaded", false);
        put30(s, "raw_html_uploaded", false);
        put30(s, "cookies_tokens_accessed", false);
        return s;
    }

    private JSONObject withScan30(JSONObject state, JSONObject scan) {
        try { state.put("scan", scan == null ? JSONObject.NULL : scan); } catch (Exception ignored) {}
        return state;
    }

    private void phase30(String phase, String classification, JSONObject state) {
        if (!running30 && !"INTERRUPTED_PREVIOUS_RUN".equals(phase)) return;
        persistRun30(running30, phase);
        JSONObject p = payload30(phase, classification, state, seq30++);
        if (telemetryHealthy30 && TelemetryConfigV30.isConfigured())
            new Thread(() -> uploadJson30(p, NET_TIMEOUT_MS), "cp30-phase").start();
    }

    private JSONObject payload30(String phase, String classification, JSONObject state, int seq) {
        JSONObject p = new JSONObject();
        put30(p, "schema_version", SCHEMA30);
        put30(p, "scenario_id", SCENARIO30);
        put30(p, "test_id", testId30);
        put30(p, "seq", seq);
        put30(p, "phase", phase);
        put30(p, "classification", classification);
        put30(p, "timestamp_epoch_ms", System.currentTimeMillis());
        put30(p, "source_ref", TelemetryConfigV30.SOURCE_REF);
        put30(p, "collector_id", TelemetryConfigV30.COLLECTOR_ID);
        try { p.put("state", state == null ? new JSONObject() : state); } catch (Exception ignored) {}
        return p;
    }

    private JSONObject uploadJson30(JSONObject body, int timeoutMs) {
        JSONObject out = new JSONObject();
        if (!TelemetryConfigV30.isConfigured()) { put30(out, "success", false); put30(out, "error", "CONFIG_NOT_INJECTED"); return out; }
        HttpURLConnection c = null;
        try {
            byte[] data = body.toString().getBytes(StandardCharsets.UTF_8);
            c = (HttpURLConnection) new URL(TelemetryConfigV30.WEBHOOK_URL).openConnection();
            c.setConnectTimeout(timeoutMs); c.setReadTimeout(timeoutMs); c.setRequestMethod("POST"); c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            c.setFixedLengthStreamingMode(data.length);
            try (OutputStream os = c.getOutputStream()) { os.write(data); }
            int code = c.getResponseCode();
            put30(out, "success", code >= 200 && code < 300); put30(out, "http", code);
        } catch (Exception e) {
            put30(out, "success", false); put30(out, "error", token30(e.getClass().getSimpleName()));
        } finally { if (c != null) c.disconnect(); }
        return out;
    }

    private void persistRun30(boolean running, String phase) {
        if (prefs30 == null) return;
        prefs30.edit().putBoolean("running", running).putString("test_id", testId30)
                .putString("phase", phase).putString("final", finalClassification30)
                .putLong("started_at", startedAt30).apply();
    }

    private void reportInterrupted30() {
        if (prefs30 == null || !prefs30.getBoolean("running", false)) return;
        String old = prefs30.getString("test_id", "-");
        String phase = prefs30.getString("phase", "-");
        prefs30.edit().putBoolean("running", false).apply();
        JSONObject s = captureState30(); put30(s, "previous_test_id", old); put30(s, "previous_phase", phase);
        String keep = testId30; testId30 = old == null ? "-" : old;
        phase30("INTERRUPTED_PREVIOUS_RUN", "RECORDED_ON_RESTART", s);
        testId30 = keep;
    }

    private void saveLocal30(String classification, JSONObject state) {
        try {
            JSONObject root = payload30("LOCAL_FINAL", classification, state, seq30);
            String name = "chatgpt-webview-v30-voice-" + testId30 + ".json";
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            cv.put(MediaStore.MediaColumns.MIME_TYPE, "application/json");
            cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (u == null) return;
            try (OutputStream out = getContentResolver().openOutputStream(u)) {
                if (out != null) out.write(root.toString(2).getBytes(StandardCharsets.UTF_8));
            }
        } catch (Exception ignored) {}
    }

    private boolean invokeAncestor30(String name, Class<?>[] types, Object[] args) {
        Class<?> c = getClass();
        while (c != null) {
            try {
                Method m = c.getDeclaredMethod(name, types); m.setAccessible(true); m.invoke(this, args); return true;
            } catch (NoSuchMethodException e) { c = c.getSuperclass(); }
            catch (Exception e) { return false; }
        }
        return false;
    }

    private Object field30(String name) {
        Class<?> c = getClass();
        while (c != null) {
            try { Field f = c.getDeclaredField(name); f.setAccessible(true); return f.get(this); }
            catch (NoSuchFieldException e) { c = c.getSuperclass(); }
            catch (Exception e) { return null; }
        }
        return null;
    }

    private String parentString30(String name) { Object x = field30(name); return x == null ? "-" : String.valueOf(x); }
    private int parentInt30(String name) { Object x = field30(name); return x instanceof Number ? ((Number)x).intValue() : -1; }

    private WebView findWeb30(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (!(v instanceof ViewGroup)) return null;
        ViewGroup g = (ViewGroup) v;
        for (int i = 0; i < g.getChildCount(); i++) { WebView w = findWeb30(g.getChildAt(i)); if (w != null) return w; }
        return null;
    }

    private boolean trusted30(String url) {
        try { Uri u = Uri.parse(url); return "https".equalsIgnoreCase(u.getScheme()) && "chatgpt.com".equalsIgnoreCase(u.getHost()); }
        catch (Exception e) { return false; }
    }

    private void setStatus30(String text) { if (status30 != null) status30.setText(text == null ? "" : text); }
    private int dp30(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }
    private static String js30(String s) { return s == null ? "" : s.replace("\\", "\\\\").replace("'", "\\'"); }
    private static String token30(String s) { String x=s==null?"-":s.replaceAll("[^A-Za-z0-9_.:+/@=-]","_"); return x.length()>160?x.substring(0,160):x; }
    private static void put30(JSONObject o, String k, Object v) { try { o.put(k, v); } catch (Exception ignored) {} }
}
