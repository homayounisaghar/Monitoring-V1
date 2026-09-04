package com.homayounisaghar.chatgptwebviewprobe;

import android.Manifest;
import android.content.ContentValues;
import android.content.SharedPreferences;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
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
 * Stable v0.28: autonomous Voice supervisor lifecycle.
 *
 * One user tap exercises the already-established app-owned WebView/session stack:
 * READY -> Session ACTIVE -> Voice Start -> active/unmuted -> Mute -> muted ->
 * Unmute -> active/unmuted -> stable hold -> Voice End -> READY -> Session IDLE.
 *
 * Every Voice write is guarded by a durable local claim and a bounded semantic DOM
 * scan. The scan traverses only same-origin/open roots with node/root/time budgets.
 * Unknown, ambiguous or incomplete UI fails closed. A dispatched action with an
 * ambiguous receipt is never replayed; SESSION END remains the hard recovery bound.
 * No coordinates/XPath/private ChatGPT APIs/cookies/tokens/raw speech/chat text.
 */
public class OrchestratorAutonomousV28Activity extends OrchestratorAutonomousV27Activity {
    private static final String PREFS28 = "stable_v28_voice_supervisor";
    private static final String SCHEMA28 = "cp-v28-voice-supervisor-v1";
    private static final String SCENARIO28 = "voice-start-mute-unmute-end-e2e";
    private static final long GLOBAL_WATCHDOG_MS = 60000L;
    private static final long EVAL_TIMEOUT_MS = 2600L;
    private static final long LIVE_LEASE_MS = 10L * 60L * 1000L;
    private static final int NET_TIMEOUT_MS = 2800;
    private static final int EXPECTED_EVENT_BUDGET = 24;

    private final Handler h28 = new Handler(Looper.getMainLooper());
    private final Runnable watchdog28 = this::onWatchdog28;
    private SharedPreferences prefs28;
    private WebView web28;
    private Button run28;
    private TextView status28;

    private boolean running28 = false;
    private boolean telemetryHealthy28 = false;
    private String testId28 = "-";
    private int seq28 = 0;
    private long startedAt28 = 0L;
    private String finalClassification28 = "NOT_RUN";
    private String currentClaimAction28 = "NONE";
    private String currentClaimStatus28 = "NONE";
    private int dispatchedSideEffects28 = 0;

    private interface JsonDone28 { void done(JSONObject result); }
    private interface Condition28 { boolean ok(); }
    private interface ScanPredicate28 { boolean ok(JSONObject scan); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs28 = getSharedPreferences(PREFS28, MODE_PRIVATE);
        web28 = findWeb28(getWindow().getDecorView());
        Object rb = objectField28("runButton23");
        Object st = objectField28("status23");
        if (rb instanceof Button) run28 = (Button) rb;
        if (st instanceof TextView) status28 = (TextView) st;
        try { if (web28 != null) web28.getSettings().setMediaPlaybackRequiresUserGesture(false); }
        catch (Exception ignored) {}
        if (run28 != null) {
            run28.setEnabled(true);
            run28.setText("RUN VOICE TEST");
            run28.setOnClickListener(v -> runVoiceTest28());
        }
        setStatus28("v0.28 Voice supervisor ready — one tap, then do not touch ChatGPT controls.");
        reportInterrupted28();
    }

    @Override protected void onDestroy() {
        h28.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private void runVoiceTest28() {
        if (running28) return;
        if (web28 == null || !trusted28(web28.getUrl())) {
            setStatus28("Voice test blocked: trusted ChatGPT WebView is not ready.");
            return;
        }
        running28 = true;
        telemetryHealthy28 = false;
        testId28 = "cp28-" + UUID.randomUUID();
        seq28 = 0;
        startedAt28 = System.currentTimeMillis();
        finalClassification28 = "RUNNING";
        currentClaimAction28 = "NONE";
        currentClaimStatus28 = "NONE";
        dispatchedSideEffects28 = 0;
        if (run28 != null) { run28.setEnabled(false); run28.setText("VOICE TEST RUNNING..."); }
        persistRun28(true, "TELEMETRY_PREFLIGHT");
        setStatus28("Voice test: telemetry preflight...");
        h28.removeCallbacks(watchdog28);
        h28.postDelayed(watchdog28, GLOBAL_WATCHDOG_MS);
        telemetryPreflight28();
    }

    private void telemetryPreflight28() {
        JSONObject s = captureState28();
        put28(s, "collector_capacity_hint", TelemetryConfigV28.COLLECTOR_CAPACITY_HINT);
        put28(s, "expected_event_budget", EXPECTED_EVENT_BUDGET);
        JSONObject p = payload28("TELEMETRY_PREFLIGHT", "RUNNING", s, 0);
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!running28 || !once.compareAndSet(false, true)) return;
            telemetryHealthy28 = false;
            finishNoSideEffect28("TELEMETRY_PREFLIGHT_TIMEOUT");
        };
        h28.postDelayed(timeout, 8000L);
        new Thread(() -> {
            JSONObject r = uploadJson28(p, NET_TIMEOUT_MS + 900);
            runOnUiThread(() -> {
                if (!running28 || !once.compareAndSet(false, true)) return;
                h28.removeCallbacks(timeout);
                if (!r.optBoolean("success", false)) {
                    telemetryHealthy28 = false;
                    finishNoSideEffect28("TELEMETRY_UNAVAILABLE");
                    return;
                }
                telemetryHealthy28 = true;
                phase28("RUN_STARTED", "RUNNING", captureState28());
                precondition28();
            });
        }, "cp28-preflight").start();
    }

    private void precondition28() {
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            finishNoSideEffect28("BLOCKED_ANDROID_RECORD_AUDIO_NOT_GRANTED");
            return;
        }
        if (!"IDLE".equals(parentString28("sessionState")) || !"NONE".equals(parentString28("micLeaseMode"))) {
            phase28("PRECONDITION", "DIRTY_SESSION_OR_MIC_LEASE", captureState28());
            recover28("DIRTY_INITIAL_STATE");
            return;
        }
        setStatus28("Voice test: checking the current Start Voice control...");
        scanVoice28(scan -> {
            JSONObject s = withScan28(captureState28(), scan);
            if (!scanComplete28(scan)) {
                phase28("READY_VOICE_CENSUS", "FAIL_INCOMPLETE_SCAN", s);
                finishNoSideEffect28("READY_VOICE_SCAN_INCOMPLETE");
                return;
            }
            if (!readyVoice28(scan)) {
                phase28("READY_VOICE_CENSUS", "FAIL_UNIQUE_START_VOICE_NOT_READY", s);
                finishNoSideEffect28("READY_VOICE_START_NOT_UNIQUE");
                return;
            }
            phase28("READY_VOICE_CENSUS", "PASS_UNIQUE_START_VOICE_READY", s);
            startSession28();
        });
    }

    private void startSession28() {
        setStatus28("Voice test: starting InteractionSession...");
        boolean invoked = invokeV16Void28("toggleSession", new Class<?>[0], new Object[0]);
        JSONObject s = captureState28(); put28(s, "session_start_invoked", invoked);
        phase28("SESSION_START_DISPATCH", invoked ? "REQUESTED" : "REFLECTION_FAIL", s);
        if (!invoked) { recover28("SESSION_START_NOT_DISPATCHED"); return; }
        waitCondition28(() -> "ACTIVE".equals(parentString28("sessionState")), 4000L,
                () -> {
                    phase28("SESSION_ACTIVE", "PASS", captureState28());
                    h28.postDelayed(this::gateVoiceStart28, 300L);
                },
                () -> recover28("SESSION_START_NOT_CONFIRMED"));
    }

    private void gateVoiceStart28() {
        scanVoice28(scan -> {
            JSONObject s = withScan28(captureState28(), scan);
            if (!scanComplete28(scan) || !readyVoice28(scan)) {
                phase28("VOICE_START_GATE", "FAIL_NOT_UNIQUE_READY", s);
                recover28("VOICE_START_GATE_FAILED");
                return;
            }
            phase28("VOICE_START_GATE", "PASS_UNIQUE_READY", s);
            setStatus28("Voice test 1/4: starting Voice...");
            dispatchVoice28("VOICE_START", scan, dispatched -> {
                if (!dispatched) { recover28("VOICE_START_NOT_DISPATCHED"); return; }
                waitScan28(x -> activeUnmuted28(x) && "LIVE".equals(parentString28("micLeaseMode")), 12000L,
                        receipt -> {
                            confirmClaim28("VOICE_START", "VOICE_ACTIVE_UNMUTED");
                            phase28("VOICE_START_RECEIPT", "PASS_ACTIVE_UNMUTED", withScan28(captureState28(), receipt));
                            mute28(receipt);
                        },
                        () -> uncertainAndRecover28("VOICE_START", "VOICE_START_RECEIPT_TIMEOUT"));
            });
        });
    }

    private void mute28(JSONObject baseline) {
        if (!activeUnmuted28(baseline)) { recover28("VOICE_MUTE_PRECONDITION_LOST"); return; }
        setStatus28("Voice test 2/4: muting...");
        dispatchVoice28("VOICE_MUTE", baseline, dispatched -> {
            if (!dispatched) { recover28("VOICE_MUTE_NOT_DISPATCHED"); return; }
            waitScan28(this::activeMuted28, 7000L,
                    receipt -> {
                        confirmClaim28("VOICE_MUTE", "VOICE_MUTED");
                        phase28("VOICE_MUTE_RECEIPT", "PASS_MUTED", withScan28(captureState28(), receipt));
                        unmute28(receipt);
                    },
                    () -> uncertainAndRecover28("VOICE_MUTE", "VOICE_MUTE_RECEIPT_TIMEOUT"));
        });
    }

    private void unmute28(JSONObject baseline) {
        if (!activeMuted28(baseline)) { recover28("VOICE_UNMUTE_PRECONDITION_LOST"); return; }
        setStatus28("Voice test 3/4: unmuting...");
        dispatchVoice28("VOICE_UNMUTE", baseline, dispatched -> {
            if (!dispatched) { recover28("VOICE_UNMUTE_NOT_DISPATCHED"); return; }
            waitScan28(this::activeUnmuted28, 7000L,
                    receipt -> {
                        confirmClaim28("VOICE_UNMUTE", "VOICE_UNMUTED");
                        phase28("VOICE_UNMUTE_RECEIPT", "PASS_UNMUTED", withScan28(captureState28(), receipt));
                        stableHold28();
                    },
                    () -> uncertainAndRecover28("VOICE_UNMUTE", "VOICE_UNMUTE_RECEIPT_TIMEOUT"));
        });
    }

    private void stableHold28() {
        phase28("VOICE_STABLE_HOLD_STARTED", "RUNNING", captureState28());
        setStatus28("Voice test: holding active state briefly...");
        h28.postDelayed(() -> scanVoice28(scan -> {
            JSONObject s = withScan28(captureState28(), scan);
            if (!scanComplete28(scan) || !activeUnmuted28(scan) || !"LIVE".equals(parentString28("micLeaseMode"))) {
                phase28("VOICE_STABLE_HOLD_RESULT", "FAIL_ACTIVE_STATE_NOT_STABLE", s);
                recover28("VOICE_ACTIVE_HOLD_FAILED");
                return;
            }
            phase28("VOICE_STABLE_HOLD_RESULT", "PASS_ACTIVE_STABLE", s);
            endVoice28(scan);
        }), 1600L);
    }

    private void endVoice28(JSONObject baseline) {
        if (!activeUnmuted28(baseline)) { recover28("VOICE_END_PRECONDITION_LOST"); return; }
        setStatus28("Voice test 4/4: ending Voice...");
        dispatchVoice28("VOICE_END", baseline, dispatched -> {
            if (!dispatched) { recover28("VOICE_END_NOT_DISPATCHED"); return; }
            waitScan28(this::readyVoice28, 10000L,
                    receipt -> {
                        confirmClaim28("VOICE_END", "VOICE_READY_RETURNED");
                        invokeV16Void28("revokeLease", new Class<?>[]{String.class}, new Object[]{"V28_VOICE_END_CONFIRMED"});
                        JSONObject s = withScan28(captureState28(), receipt);
                        phase28("VOICE_END_UI_RECEIPT", "PASS_READY_RETURNED", s);
                        waitCondition28(() -> "NONE".equals(parentString28("micLeaseMode")), 2500L,
                                () -> {
                                    phase28("VOICE_END_RECEIPT", "PASS_READY_AND_LEASE_RELEASED", captureState28());
                                    endSession28();
                                },
                                () -> recover28("VOICE_END_LEASE_NOT_RELEASED"));
                    },
                    () -> uncertainAndRecover28("VOICE_END", "VOICE_END_RECEIPT_TIMEOUT"));
        });
    }

    private void endSession28() {
        setStatus28("Voice test: ending InteractionSession...");
        boolean invoked = invokeV18Void28("hardEndSession18");
        JSONObject s = captureState28(); put28(s, "hard_session_end_invoked", invoked);
        phase28("SESSION_END_DISPATCH", invoked ? "REQUESTED" : "REFLECTION_FAIL", s);
        if (!invoked) { recover28("SESSION_END_NOT_DISPATCHED"); return; }
        waitCondition28(() -> "IDLE".equals(parentString28("sessionState"))
                        && "NONE".equals(parentString28("micLeaseMode")),
                4000L,
                () -> {
                    phase28("SESSION_END_RECEIPT", "PASS_IDLE_MIC_NONE", captureState28());
                    finalClassification28 = "PASS_VOICE_START_MUTE_UNMUTE_END_RECOVERED";
                    finish28();
                },
                () -> recover28("SESSION_END_NOT_CONFIRMED"));
    }

    private void dispatchVoice28(String action, JSONObject knownScan, java.util.function.Consumer<Boolean> done) {
        if (!running28) { done.accept(false); return; }
        String category = action;
        if (!scanComplete28(knownScan) || count28(knownScan, keyFor28(category)) != 1) {
            done.accept(false);
            return;
        }
        if (!claim28(action)) { done.accept(false); return; }
        if ("VOICE_START".equals(action)) {
            if (!invokeV16Void28("acquireLease", new Class<?>[]{String.class, long.class}, new Object[]{"LIVE", LIVE_LEASE_MS})) {
                abortClaim28(action, "LEASE_ARM_FAIL");
                done.accept(false);
                return;
            }
        }
        evalJson28(voiceJs28(category, true), result -> {
            JSONObject s = withScan28(captureState28(), result);
            int matches = result.optInt("target_matches", -1);
            boolean clicked = result.optBoolean("clicked", false);
            boolean complete = result.optBoolean("success", false);
            if (!complete || matches != 1 || !clicked) {
                abortClaim28(action, !complete ? "INCOMPLETE_SCAN" : "MATCHES_" + matches);
                if ("VOICE_START".equals(action))
                    invokeV16Void28("revokeLease", new Class<?>[]{String.class}, new Object[]{"V28_START_NOT_DISPATCHED"});
                phase28(action + "_DISPATCH", "ABORTED_NO_SIDE_EFFECT", s);
                done.accept(false);
                return;
            }
            dispatchedSideEffects28++;
            currentClaimStatus28 = "DISPATCHED";
            prefs28.edit().putString("claim_status", "DISPATCHED").commit();
            phase28(action + "_DISPATCH", "DISPATCHED_UNIQUE_SEMANTIC_CLICK", s);
            done.accept(true);
        });
    }

    private boolean claim28(String action) {
        String id = action + "_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0, 8);
        boolean ok = prefs28.edit()
                .putString("claim_id", id)
                .putString("claim_action", action)
                .putString("claim_status", "CLAIMED")
                .commit();
        if (!ok) return false;
        currentClaimAction28 = action;
        currentClaimStatus28 = "CLAIMED";
        return true;
    }

    private void confirmClaim28(String action, String receipt) {
        if (!action.equals(currentClaimAction28)) return;
        currentClaimStatus28 = "CONFIRMED";
        prefs28.edit().putString("claim_status", "CONFIRMED").putString("claim_receipt", receipt).commit();
    }

    private void abortClaim28(String action, String reason) {
        if (!action.equals(currentClaimAction28)) return;
        currentClaimStatus28 = "ABORTED_NO_SIDE_EFFECT";
        prefs28.edit().putString("claim_status", "ABORTED_NO_SIDE_EFFECT")
                .putString("claim_receipt", reason).commit();
    }

    private void uncertainAndRecover28(String action, String reason) {
        if (action.equals(currentClaimAction28)) {
            currentClaimStatus28 = "UNCERTAIN_NO_REPLAY";
            prefs28.edit().putString("claim_status", "UNCERTAIN_NO_REPLAY")
                    .putString("claim_receipt", reason).commit();
        }
        phase28("ACTION_RECEIPT_UNCERTAIN", reason, captureState28());
        recover28(reason);
    }

    private void recover28(String reason) {
        if (!running28) return;
        if ("RUNNING".equals(finalClassification28)) finalClassification28 = reason;
        setStatus28("Voice test: recovery boundary...");
        phase28("RECOVERY_STARTED", reason, captureState28());
        boolean invoked = invokeV18Void28("hardEndSession18");
        JSONObject s = captureState28(); put28(s, "hard_session_end_invoked", invoked);
        phase28("RECOVERY_DISPATCH", invoked ? "SESSION_END_ESCAPE_REQUESTED" : "SESSION_END_ESCAPE_REFLECTION_FAIL", s);
        waitCondition28(() -> "IDLE".equals(parentString28("sessionState"))
                        && "NONE".equals(parentString28("micLeaseMode")),
                5000L,
                () -> {
                    finalClassification28 = finalClassification28 + "_RECOVERED";
                    phase28("RECOVERY_RESULT", "RECOVERED_IDLE_MIC_NONE", captureState28());
                    finish28();
                },
                () -> {
                    finalClassification28 = finalClassification28 + "_RECOVERY_UNCONFIRMED";
                    phase28("RECOVERY_RESULT", "RECOVERY_UNCONFIRMED", captureState28());
                    finish28();
                });
    }

    private void finishNoSideEffect28(String classification) {
        finalClassification28 = classification;
        phase28("FINAL", classification, captureState28());
        saveLocal28();
        persistRun28(false, "FINAL");
        h28.removeCallbacks(watchdog28);
        running28 = false;
        if (run28 != null) { run28.setEnabled(true); run28.setText("RUN VOICE TEST"); }
        setStatus28("Voice test did not start: " + classification);
    }

    private void finish28() {
        phase28("FINAL", finalClassification28, captureState28());
        saveLocal28();
        persistRun28(false, "FINAL");
        h28.removeCallbacks(watchdog28);
        running28 = false;
        if (run28 != null) { run28.setEnabled(true); run28.setText("RUN VOICE TEST"); }
        if (finalClassification28.startsWith("PASS_"))
            setStatus28("VOICE TEST PASS — Start / Mute / Unmute / End / recovery confirmed.");
        else setStatus28("VOICE TEST finished: " + finalClassification28);
    }

    private void onWatchdog28() {
        if (!running28) return;
        if ("DISPATCHED".equals(currentClaimStatus28)) {
            currentClaimStatus28 = "UNCERTAIN_NO_REPLAY";
            prefs28.edit().putString("claim_status", "UNCERTAIN_NO_REPLAY")
                    .putString("claim_receipt", "GLOBAL_WATCHDOG").commit();
        }
        phase28("GLOBAL_WATCHDOG", "GLOBAL_TIMEOUT", captureState28());
        recover28("GLOBAL_TIMEOUT");
    }

    private void scanVoice28(JsonDone28 done) {
        evalJson28(voiceJs28("NONE", false), done);
    }

    private void waitScan28(ScanPredicate28 predicate, long timeoutMs, JsonDone28 success, Runnable failure) {
        long deadline = System.currentTimeMillis() + timeoutMs;
        waitScanLoop28(predicate, deadline, success, failure);
    }

    private void waitScanLoop28(ScanPredicate28 predicate, long deadline, JsonDone28 success, Runnable failure) {
        if (!running28) return;
        scanVoice28(scan -> {
            if (!running28) return;
            if (!scanComplete28(scan)) { failure.run(); return; }
            if (predicate.ok(scan)) { success.done(scan); return; }
            if (System.currentTimeMillis() >= deadline) { failure.run(); return; }
            h28.postDelayed(() -> waitScanLoop28(predicate, deadline, success, failure), 240L);
        });
    }

    private void waitCondition28(Condition28 condition, long timeoutMs, Runnable success, Runnable failure) {
        long deadline = System.currentTimeMillis() + timeoutMs;
        waitConditionLoop28(condition, deadline, success, failure);
    }

    private void waitConditionLoop28(Condition28 condition, long deadline, Runnable success, Runnable failure) {
        if (!running28) return;
        boolean ok = false;
        try { ok = condition.ok(); } catch (Exception ignored) {}
        if (ok) { success.run(); return; }
        if (System.currentTimeMillis() >= deadline) { failure.run(); return; }
        h28.postDelayed(() -> waitConditionLoop28(condition, deadline, success, failure), 120L);
    }

    private boolean scanComplete28(JSONObject s) {
        return s != null && s.optBoolean("success", false)
                && !s.optBoolean("budget_exceeded", true)
                && !s.optBoolean("truncated", true)
                && !s.optBoolean("eval_timeout", false);
    }

    private boolean readyVoice28(JSONObject s) {
        return scanComplete28(s)
                && s.optInt("voice_start_count", -1) == 1
                && s.optInt("voice_end_count", -1) == 0
                && s.optInt("mute_count", -1) == 0
                && s.optInt("unmute_count", -1) == 0;
    }

    private boolean activeUnmuted28(JSONObject s) {
        return scanComplete28(s)
                && s.optInt("voice_end_count", -1) == 1
                && s.optInt("mute_count", -1) == 1
                && s.optInt("unmute_count", -1) == 0;
    }

    private boolean activeMuted28(JSONObject s) {
        return scanComplete28(s)
                && s.optInt("voice_end_count", -1) == 1
                && s.optInt("mute_count", -1) == 0
                && s.optInt("unmute_count", -1) == 1;
    }

    private static String keyFor28(String category) {
        switch (category) {
            case "VOICE_START": return "voice_start_count";
            case "VOICE_MUTE": return "mute_count";
            case "VOICE_UNMUTE": return "unmute_count";
            case "VOICE_END": return "voice_end_count";
            default: return "unknown_count";
        }
    }

    private static int count28(JSONObject o, String k) { return o == null ? -1 : o.optInt(k, -1); }

    private void evalJson28(String js, JsonDone28 done) {
        if (web28 == null) {
            JSONObject o = new JSONObject(); put28(o, "success", false); put28(o, "web_missing", true); done.done(o); return;
        }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!once.compareAndSet(false, true)) return;
            JSONObject o = new JSONObject(); put28(o, "success", false); put28(o, "eval_timeout", true); done.done(o);
        };
        h28.postDelayed(timeout, EVAL_TIMEOUT_MS);
        try {
            web28.evaluateJavascript(js, value -> {
                if (!once.compareAndSet(false, true)) return;
                h28.removeCallbacks(timeout);
                try { done.done(jsonObject28(value)); }
                catch (Exception e) {
                    JSONObject o = new JSONObject(); put28(o, "success", false); put28(o, "parse_error", e.getClass().getSimpleName()); done.done(o);
                }
            });
        } catch (Exception e) {
            if (!once.compareAndSet(false, true)) return;
            h28.removeCallbacks(timeout);
            JSONObject o = new JSONObject(); put28(o, "success", false); put28(o, "eval_error", e.getClass().getSimpleName()); done.done(o);
        }
    }

    private static JSONObject jsonObject28(String raw) throws Exception {
        Object x = new JSONTokener(raw == null ? "null" : raw).nextValue();
        if (x instanceof String) x = new JSONTokener((String) x).nextValue();
        if (!(x instanceof JSONObject)) throw new IllegalStateException("not_object");
        return (JSONObject) x;
    }

    private String voiceJs28(String target, boolean click) {
        return "(function(){try{"
                + "const TARGET='" + js28(target) + "',DO=" + (click ? "true" : "false") + ";"
                + "const T=performance.now(),MAX_MS=180,MAX_NODES=7000,MAX_ROOTS=32;"
                + "const N=x=>String(x||'').replace(/\\s+/g,' ').trim();"
                + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "const V=e=>{try{const r=e.getBoundingClientRect(),w=e.ownerDocument&&e.ownerDocument.defaultView,s=w?w.getComputedStyle(e):getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
                + "const E=e=>{try{return !e.disabled&&String(e.getAttribute('aria-disabled')||'').toLowerCase()!=='true';}catch(_){return true;}};"
                + "const M=e=>{let z='';try{z+=' '+N(e.getAttribute('aria-label'))+' '+N(e.getAttribute('title'))+' '+N(e.getAttribute('data-testid'))+' '+N(e.getAttribute('name'))+' '+N(e.getAttribute('id'))+' '+N(e.getAttribute('data-state'))+' '+N(e.innerText||e.textContent||'');const st=e.querySelector&&e.querySelector('svg title');if(st)z+=' '+N(st.textContent||'');}catch(_){}return N(z).toLowerCase();};"
                + "const C=e=>{const a=N(e.getAttribute&&e.getAttribute('aria-label')).toLowerCase(),x=M(e);if(a==='start voice'||/voice mode|open voice|advanced voice|start voice/.test(x))return 'VOICE_START';if(/unmute|turn[^ ]* microphone on|turn microphone on|mic on|microphone on/.test(x))return 'VOICE_UNMUTE';if(/(^|[^a-z])mute([^a-z]|$)|turn microphone off|mic off|microphone off/.test(x))return 'VOICE_MUTE';if(/end voice|leave voice|exit voice|close voice|voice[^a-z]*close|end call|hang up|disconnect/.test(x))return 'VOICE_END';return 'OTHER';};"
                + "const roots=[document],seenR=new Set(),seenE=new Set(),controls=[];let nodes=0,budget=false,trunc=false;"
                + "for(let q=0;q<roots.length&&q<MAX_ROOTS;q++){if(performance.now()-T>MAX_MS){budget=true;break;}const r=roots[q];if(!r||seenR.has(r))continue;seenR.add(r);let all=[];try{all=[...r.querySelectorAll('*')];}catch(_){}for(const e of all){nodes++;if(nodes>MAX_NODES){trunc=true;break;}if(performance.now()-T>MAX_MS){budget=true;break;}try{if(e.shadowRoot&&roots.length<MAX_ROOTS)roots.push(e.shadowRoot);if(e.tagName==='IFRAME'&&e.contentDocument&&roots.length<MAX_ROOTS)roots.push(e.contentDocument);}catch(_){}}if(trunc||budget)break;let bs=[];try{bs=[...r.querySelectorAll('button,[role=button],[aria-label],[data-testid]')];}catch(_){}for(const e of bs){if(!seenE.has(e)&&V(e)&&E(e)){seenE.add(e);controls.push(e);}}}"
                + "const xs=controls.map(e=>({e:e,c:C(e),h:H(M(e)),a:N(e.getAttribute&&e.getAttribute('aria-label')).toLowerCase()})).filter(x=>x.c!=='OTHER');"
                + "const cnt=k=>xs.filter(x=>x.c===k).length;const complete=!budget&&!trunc;const tx=xs.filter(x=>x.c===TARGET);let clicked=false;if(DO&&complete&&tx.length===1){tx[0].e.click();clicked=true;}"
                + "const sig=H(xs.map(x=>x.c+':'+x.h).sort().join('|'));"
                + "return JSON.stringify({success:complete,budget_exceeded:budget,truncated:trunc,scan_ms:Math.round(performance.now()-T),roots:seenR.size,nodes:nodes,visible_controls:controls.length,voice_start_count:cnt('VOICE_START'),voice_start_exact_aria_count:xs.filter(x=>x.c==='VOICE_START'&&x.a==='start voice').length,voice_end_count:cnt('VOICE_END'),mute_count:cnt('VOICE_MUTE'),unmute_count:cnt('VOICE_UNMUTE'),set_hash:sig,target_matches:TARGET==='NONE'?0:tx.length,clicked:clicked});"
                + "}catch(e){return JSON.stringify({success:false,budget_exceeded:false,truncated:false,target_matches:-1,clicked:false,error:String(e&&e.name||'ERR')});}})();";
    }

    private JSONObject captureState28() {
        JSONObject s = new JSONObject();
        put28(s, "session_state", parentString28("sessionState"));
        put28(s, "mic_lease_mode", parentString28("micLeaseMode"));
        put28(s, "parent_last_action", parentString28("lastAction"));
        put28(s, "parent_last_status", parentString28("lastActionStatus"));
        put28(s, "v17_wrapper_status", parentString28("lastWrapperStatus"));
        put28(s, "v17_robust_status", parentString28("lastRobustVoiceStatus"));
        put28(s, "android_record_audio_granted", checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED);
        boolean requiresGesture = true;
        try { if (web28 != null) requiresGesture = web28.getSettings().getMediaPlaybackRequiresUserGesture(); } catch (Exception ignored) {}
        put28(s, "media_playback_requires_user_gesture", requiresGesture);
        put28(s, "claim_action", currentClaimAction28);
        put28(s, "claim_status", currentClaimStatus28);
        put28(s, "dispatched_side_effects", dispatchedSideEffects28);
        put28(s, "raw_audio_uploaded", false);
        put28(s, "raw_speech_uploaded", false);
        put28(s, "raw_transcript_uploaded", false);
        put28(s, "raw_chat_text_uploaded", false);
        put28(s, "cookies_tokens_accessed", false);
        return s;
    }

    private JSONObject withScan28(JSONObject s, JSONObject scan) {
        if (s == null) s = new JSONObject();
        if (scan == null) return s;
        String[] keys = {"success","budget_exceeded","truncated","eval_timeout","scan_ms","roots","nodes","visible_controls","voice_start_count","voice_start_exact_aria_count","voice_end_count","mute_count","unmute_count","set_hash","target_matches","clicked"};
        for (String k : keys) if (scan.has(k)) put28(s, k, scan.opt(k));
        return s;
    }

    private void phase28(String phase, String classification, JSONObject state) {
        if (!running28 && !"FINAL".equals(phase)) return;
        persistRun28(true, phase);
        JSONObject p = payload28(phase, classification, state, ++seq28);
        if (telemetryHealthy28 && TelemetryConfigV28.isConfigured())
            new Thread(() -> uploadJson28(p, NET_TIMEOUT_MS), "cp28-t-" + seq28).start();
    }

    private JSONObject payload28(String phase, String classification, JSONObject state, int seq) {
        JSONObject p = new JSONObject();
        put28(p, "kind", "TEST_PHASE");
        put28(p, "schema_version", SCHEMA28);
        put28(p, "scenario_id", SCENARIO28);
        put28(p, "test_id", testId28);
        put28(p, "seq", seq);
        put28(p, "phase", phase);
        put28(p, "classification", classification);
        put28(p, "app_version", appVersion28());
        put28(p, "source_ref", TelemetryConfigV28.SOURCE_REF);
        put28(p, "collector_id", TelemetryConfigV28.COLLECTOR_ID);
        put28(p, "timestamp_epoch_ms", System.currentTimeMillis());
        put28(p, "elapsed_ms", startedAt28 == 0L ? 0L : Math.max(0L, System.currentTimeMillis() - startedAt28));
        put28(p, "privacy", "receipts_and_control_counts_only_no_raw_audio_speech_transcript_chat_text_credentials_or_tokens");
        put28(p, "state", state == null ? new JSONObject() : state);
        return p;
    }

    private JSONObject uploadJson28(JSONObject p, int timeoutMs) {
        JSONObject r = new JSONObject(); HttpURLConnection c = null;
        try {
            if (!TelemetryConfigV28.isConfigured()) { put28(r, "success", false); put28(r, "reason", "UNCONFIGURED"); return r; }
            c = (HttpURLConnection) new URL(TelemetryConfigV28.WEBHOOK_URL).openConnection();
            c.setRequestMethod("POST"); c.setConnectTimeout(timeoutMs); c.setReadTimeout(timeoutMs); c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            byte[] b = p.toString().getBytes(StandardCharsets.UTF_8); c.setFixedLengthStreamingMode(b.length);
            try (OutputStream os = c.getOutputStream()) { os.write(b); }
            int code = c.getResponseCode(); put28(r, "success", code >= 200 && code < 300); put28(r, "http_status", code);
        } catch (Exception e) { put28(r, "success", false); put28(r, "reason", e.getClass().getSimpleName()); }
        finally { if (c != null) c.disconnect(); }
        return r;
    }

    private void saveLocal28() {
        try {
            JSONObject o = new JSONObject();
            put28(o, "schema_version", SCHEMA28); put28(o, "scenario_id", SCENARIO28); put28(o, "test_id", testId28);
            put28(o, "final_classification", finalClassification28); put28(o, "app_version", appVersion28());
            put28(o, "source_ref", TelemetryConfigV28.SOURCE_REF); put28(o, "collector_id", TelemetryConfigV28.COLLECTOR_ID);
            put28(o, "state", captureState28());
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.MediaColumns.DISPLAY_NAME, "chatgpt-webview-v28-voice-" + testId28 + ".json");
            cv.put(MediaStore.MediaColumns.MIME_TYPE, "application/json");
            cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (u != null) try (OutputStream os = getContentResolver().openOutputStream(u)) {
                if (os != null) os.write(o.toString().getBytes(StandardCharsets.UTF_8));
            }
        } catch (Exception ignored) {}
    }

    private void persistRun28(boolean running, String phase) {
        try { prefs28.edit().putBoolean("run_in_progress", running).putString("test_id", testId28).putString("phase", phase).putString("final", finalClassification28).commit(); }
        catch (Exception ignored) {}
    }

    private void reportInterrupted28() {
        try {
            if (!prefs28.getBoolean("run_in_progress", false)) return;
            String old = prefs28.getString("test_id", "-");
            String phase = prefs28.getString("phase", "-");
            prefs28.edit().putBoolean("run_in_progress", false).commit();
            setStatus28("Previous v0.28 run was interrupted at " + phase + " (" + old + "). Ready for a fresh run.");
        } catch (Exception ignored) {}
    }

    private String parentString28(String name) {
        Object o = objectField28(name); return o == null ? "-" : String.valueOf(o);
    }

    private Object objectField28(String name) {
        Class<?> c = getClass();
        while (c != null) {
            try { Field f = c.getDeclaredField(name); f.setAccessible(true); return f.get(this); }
            catch (Exception ignored) { c = c.getSuperclass(); }
        }
        return null;
    }

    private boolean invokeV16Void28(String name, Class<?>[] types, Object[] args) {
        try { Method m = OrchestratorFoundationV16Activity.class.getDeclaredMethod(name, types); m.setAccessible(true); m.invoke(this, args); return true; }
        catch (Exception e) { return false; }
    }

    private boolean invokeV18Void28(String name) {
        try { Method m = OrchestratorFoundationV18Activity.class.getDeclaredMethod(name); m.setAccessible(true); m.invoke(this); return true; }
        catch (Exception e) { return false; }
    }

    private WebView findWeb28(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (!(v instanceof ViewGroup)) return null;
        ViewGroup g = (ViewGroup) v;
        for (int i = 0; i < g.getChildCount(); i++) { WebView w = findWeb28(g.getChildAt(i)); if (w != null) return w; }
        return null;
    }

    private boolean trusted28(String raw) {
        try { Uri u = Uri.parse(raw == null ? "" : raw); return "https".equalsIgnoreCase(u.getScheme()) && "chatgpt.com".equalsIgnoreCase(u.getHost()); }
        catch (Exception e) { return false; }
    }

    private void setStatus28(String s) { if (status28 != null) status28.setText(s); }

    private String appVersion28() {
        try { PackageInfo p = getPackageManager().getPackageInfo(getPackageName(), 0); long code = android.os.Build.VERSION.SDK_INT >= 28 ? p.getLongVersionCode() : p.versionCode; return p.versionName + "(" + code + ")"; }
        catch (Exception e) { return "unknown"; }
    }

    private static String js28(String s) { return (s == null ? "" : s).replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ").replace("\r", " "); }
    private static void put28(JSONObject o, String k, Object v) { try { o.put(k, v); } catch (Exception ignored) {} }
}
