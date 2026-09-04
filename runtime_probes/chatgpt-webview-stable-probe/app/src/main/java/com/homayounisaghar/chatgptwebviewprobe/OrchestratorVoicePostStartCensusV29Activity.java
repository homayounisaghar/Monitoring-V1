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
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.TextView;

import org.json.JSONArray;
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
 * Stable v0.29 — bounded post-Start Voice census.
 *
 * v0.28 proved the current ready Voice control and exactly-once Start dispatch,
 * but its strict active/unmuted receipt (End=1, Mute=1, Unmute=0) timed out.
 * This diagnostic does not guess a new production resolver. It performs exactly
 * one guarded Voice Start, observes the post-Start surface at bounded intervals,
 * then hard-recovers. It never clicks Mute/Unmute and never replays Voice Start.
 *
 * Telemetry contains only control counts, fingerprints, coarse generic keyword
 * feature bits, tag/role/state classes, media/session counters and receipts.
 * No raw chat/composer text, HTML, audio, speech, cookies or tokens are read/uploaded.
 */
public class OrchestratorVoicePostStartCensusV29Activity extends OrchestratorAutonomousV28Activity {
    private static final String PREFS29 = "stable_v29_voice_post_start_census";
    private static final String SCHEMA29 = "cp-v29-voice-post-start-census-v1";
    private static final String SCENARIO29 = "voice-post-start-bounded-census";
    private static final long GLOBAL_WATCHDOG_MS = 45000L;
    private static final long EVAL_TIMEOUT_MS = 2600L;
    private static final long LIVE_LEASE_MS = 10L * 60L * 1000L;
    private static final int NET_TIMEOUT_MS = 2800;
    private static final int EXPECTED_EVENT_BUDGET = 20;
    private static final long[] SNAPSHOT_DELAYS_MS = {400L, 1200L, 2500L, 5000L, 9000L, 14000L};

    private final Handler h29 = new Handler(Looper.getMainLooper());
    private final Runnable watchdog29 = this::onWatchdog29;
    private SharedPreferences prefs29;
    private WebView web29;
    private Button run29;
    private TextView status29;

    private boolean running29 = false;
    private boolean telemetryHealthy29 = false;
    private boolean censusComplete29 = true;
    private String testId29 = "-";
    private int seq29 = 0;
    private long startedAt29 = 0L;
    private long startDispatchedAt29 = 0L;
    private int snapshotIndex29 = 0;
    private int dispatchedSideEffects29 = 0;
    private String currentClaimAction29 = "NONE";
    private String currentClaimStatus29 = "NONE";
    private String finalClassification29 = "NOT_RUN";

    private interface JsonDone29 { void done(JSONObject result); }
    private interface Condition29 { boolean ok(); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs29 = getSharedPreferences(PREFS29, MODE_PRIVATE);
        web29 = findWeb29(getWindow().getDecorView());
        Object rb = field29("runButton23");
        Object st = field29("status23");
        if (rb instanceof Button) run29 = (Button) rb;
        if (st instanceof TextView) status29 = (TextView) st;
        if (run29 == null) run29 = findRunButton29(getWindow().getDecorView());
        if (run29 != null) {
            run29.setEnabled(true);
            run29.setText("RUN VOICE CENSUS");
            run29.setAllCaps(false);
            run29.setOnClickListener(v -> runCensus29());
        }
        setStatus29("v0.29 Voice post-Start census ready — one tap, no speech, do not touch ChatGPT controls.");
        reportInterrupted29();
    }

    @Override protected void onDestroy() {
        h29.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private void runCensus29() {
        if (running29) return;
        if (web29 == null || !trusted29(web29.getUrl())) {
            setStatus29("Voice census blocked: trusted ChatGPT WebView is not ready.");
            return;
        }
        running29 = true;
        telemetryHealthy29 = false;
        censusComplete29 = true;
        testId29 = "cp29-" + UUID.randomUUID();
        seq29 = 0;
        startedAt29 = System.currentTimeMillis();
        startDispatchedAt29 = 0L;
        snapshotIndex29 = 0;
        dispatchedSideEffects29 = 0;
        currentClaimAction29 = "NONE";
        currentClaimStatus29 = "NONE";
        finalClassification29 = "RUNNING";
        if (run29 != null) { run29.setEnabled(false); run29.setText("VOICE CENSUS RUNNING..."); }
        persistRun29(true, "TELEMETRY_PREFLIGHT");
        h29.removeCallbacks(watchdog29);
        h29.postDelayed(watchdog29, GLOBAL_WATCHDOG_MS);
        telemetryPreflight29();
    }

    private void telemetryPreflight29() {
        JSONObject s = captureState29();
        put29(s, "collector_capacity_hint", TelemetryConfigV29.COLLECTOR_CAPACITY_HINT);
        put29(s, "expected_event_budget", EXPECTED_EVENT_BUDGET);
        JSONObject p = payload29("TELEMETRY_PREFLIGHT", "RUNNING", s, 0);
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!running29 || !once.compareAndSet(false, true)) return;
            finalClassification29 = "TELEMETRY_PREFLIGHT_TIMEOUT";
            finishNoSideEffect29();
        };
        h29.postDelayed(timeout, 8000L);
        new Thread(() -> {
            JSONObject r = uploadJson29(p, NET_TIMEOUT_MS + 900);
            runOnUiThread(() -> {
                if (!running29 || !once.compareAndSet(false, true)) return;
                h29.removeCallbacks(timeout);
                if (!r.optBoolean("success", false)) {
                    finalClassification29 = "TELEMETRY_UNAVAILABLE";
                    finishNoSideEffect29();
                    return;
                }
                telemetryHealthy29 = true;
                phase29("RUN_STARTED", "RUNNING", captureState29());
                precondition29();
            });
        }, "cp29-preflight").start();
    }

    private void precondition29() {
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            finalClassification29 = "BLOCKED_ANDROID_RECORD_AUDIO_NOT_GRANTED";
            finishNoSideEffect29();
            return;
        }
        if (!"IDLE".equals(parentString29("sessionState")) || !"NONE".equals(parentString29("micLeaseMode"))) {
            phase29("PRECONDITION", "DIRTY_SESSION_OR_MIC_LEASE", captureState29());
            recover29("DIRTY_INITIAL_STATE");
            return;
        }
        setStatus29("Voice census: checking unique ready Voice control...");
        scan29("NONE", false, scan -> {
            JSONObject s = withScan29(captureState29(), scan);
            if (!scanComplete29(scan)) {
                phase29("READY_VOICE_CENSUS", "FAIL_INCOMPLETE_SCAN", s);
                finalClassification29 = "READY_SCAN_INCOMPLETE";
                finishNoSideEffect29();
                return;
            }
            if (!readyVoice29(scan)) {
                phase29("READY_VOICE_CENSUS", "FAIL_UNIQUE_READY_NOT_PRESENT", s);
                finalClassification29 = "READY_VOICE_NOT_UNIQUE";
                finishNoSideEffect29();
                return;
            }
            phase29("READY_VOICE_CENSUS", "PASS_UNIQUE_START_VOICE_READY", s);
            startSession29();
        });
    }

    private void startSession29() {
        setStatus29("Voice census: starting InteractionSession...");
        boolean invoked = invokeAncestor29("toggleSession", new Class<?>[0], new Object[0]);
        JSONObject s = captureState29(); put29(s, "session_start_invoked", invoked);
        phase29("SESSION_START_DISPATCH", invoked ? "REQUESTED" : "REFLECTION_FAIL", s);
        if (!invoked) { recover29("SESSION_START_NOT_DISPATCHED"); return; }
        waitCondition29(() -> "ACTIVE".equals(parentString29("sessionState")), 4000L,
                () -> {
                    phase29("SESSION_ACTIVE", "PASS", captureState29());
                    h29.postDelayed(this::gateAndStartVoice29, 300L);
                },
                () -> recover29("SESSION_START_NOT_CONFIRMED"));
    }

    private void gateAndStartVoice29() {
        scan29("NONE", false, baseline -> {
            JSONObject s = withScan29(captureState29(), baseline);
            if (!scanComplete29(baseline) || !readyVoice29(baseline)) {
                phase29("VOICE_START_GATE", "FAIL_NOT_UNIQUE_READY", s);
                recover29("VOICE_START_GATE_FAILED");
                return;
            }
            phase29("VOICE_START_GATE", "PASS_UNIQUE_READY", s);
            if (!claim29("VOICE_START")) { recover29("VOICE_START_CLAIM_FAILED"); return; }
            if (!invokeAncestor29("acquireLease", new Class<?>[]{String.class, long.class}, new Object[]{"LIVE", LIVE_LEASE_MS})) {
                abortClaim29("LEASE_ARM_FAIL");
                recover29("VOICE_START_LEASE_ARM_FAILED");
                return;
            }
            setStatus29("Voice census: dispatching exactly one Voice Start...");
            scan29("VOICE_START", true, click -> {
                JSONObject cs = withScan29(captureState29(), click);
                int matches = click.optInt("target_matches", -1);
                boolean clicked = click.optBoolean("clicked", false);
                if (!scanComplete29(click) || matches != 1 || !clicked) {
                    abortClaim29(!scanComplete29(click) ? "INCOMPLETE_SCAN" : "MATCHES_" + matches);
                    invokeAncestor29("revokeLease", new Class<?>[]{String.class}, new Object[]{"V29_START_NOT_DISPATCHED"});
                    phase29("VOICE_START_DISPATCH", "ABORTED_NO_SIDE_EFFECT", cs);
                    recover29("VOICE_START_NOT_DISPATCHED");
                    return;
                }
                dispatchedSideEffects29 = 1;
                startDispatchedAt29 = System.currentTimeMillis();
                currentClaimStatus29 = "DISPATCHED_CENSUS_PENDING";
                prefs29.edit().putString("claim_status", currentClaimStatus29).commit();
                phase29("VOICE_START_DISPATCH", "DISPATCHED_UNIQUE_SEMANTIC_CLICK", cs);
                snapshotIndex29 = 0;
                scheduleNextSnapshot29();
            });
        });
    }

    private void scheduleNextSnapshot29() {
        if (!running29) return;
        if (snapshotIndex29 >= SNAPSHOT_DELAYS_MS.length) {
            currentClaimStatus29 = "OBSERVED_POST_START_CENSUS_NO_REPLAY";
            prefs29.edit().putString("claim_status", currentClaimStatus29).commit();
            phase29("POST_START_CENSUS_COMPLETE", "CAPTURED_NO_REPLAY", captureState29());
            recover29("CENSUS_COMPLETE");
            return;
        }
        long targetDelay = SNAPSHOT_DELAYS_MS[snapshotIndex29];
        long elapsed = Math.max(0L, System.currentTimeMillis() - startDispatchedAt29);
        long wait = Math.max(0L, targetDelay - elapsed);
        h29.postDelayed(this::captureSnapshot29, wait);
    }

    private void captureSnapshot29() {
        if (!running29) return;
        final int idx = snapshotIndex29;
        final long target = SNAPSHOT_DELAYS_MS[idx];
        scan29("NONE", false, scan -> {
            if (!running29) return;
            long actual = startDispatchedAt29 == 0L ? -1L : Math.max(0L, System.currentTimeMillis() - startDispatchedAt29);
            JSONObject s = withScan29(captureState29(), scan);
            put29(s, "snapshot_index", idx);
            put29(s, "target_delay_ms", target);
            put29(s, "actual_delay_ms", actual);
            String classification;
            if (!scanComplete29(scan)) {
                censusComplete29 = false;
                classification = "INCOMPLETE_SCAN_FAIL_CLOSED";
            } else if (activeUnmutedOld29(scan)) classification = "OLD_ACTIVE_UNMUTED_MATCH";
            else if (activeMutedOld29(scan)) classification = "OLD_ACTIVE_MUTED_MATCH";
            else if (readyVoice29(scan)) classification = "READY_VOICE_PRESENT";
            else classification = "POST_START_SURFACE_UNRESOLVED";
            phase29(String.format(java.util.Locale.US, "POST_START_CENSUS_%05dMS", target), classification, s);
            if (!scanComplete29(scan)) {
                recover29("CENSUS_SCAN_INCOMPLETE");
                return;
            }
            snapshotIndex29++;
            scheduleNextSnapshot29();
        });
    }

    private void recover29(String reason) {
        if (!running29) return;
        phase29("RECOVERY_STARTED", reason, captureState29());
        setStatus29("Voice census: recovering session...");
        boolean invoked = invokeAncestor29("hardEndSession18", new Class<?>[0], new Object[0]);
        JSONObject s = captureState29(); put29(s, "hard_session_end_invoked", invoked);
        phase29("RECOVERY_DISPATCH", invoked ? "SESSION_END_ESCAPE_REQUESTED" : "SESSION_END_REFLECTION_FAIL", s);
        if (!invoked) {
            finalClassification29 = reason + "_RECOVERY_DISPATCH_FAILED";
            finish29();
            return;
        }
        waitCondition29(() -> "IDLE".equals(parentString29("sessionState"))
                        && "NONE".equals(parentString29("micLeaseMode")),
                4500L,
                () -> {
                    phase29("RECOVERY_RESULT", "RECOVERED_IDLE_MIC_NONE", captureState29());
                    if ("CENSUS_COMPLETE".equals(reason) && censusComplete29) {
                        finalClassification29 = "PASS_POST_START_CENSUS_CAPTURED_RECOVERED";
                    } else if ("CENSUS_SCAN_INCOMPLETE".equals(reason)) {
                        finalClassification29 = "POST_START_CENSUS_INCOMPLETE_RECOVERED";
                    } else {
                        finalClassification29 = reason + "_RECOVERED";
                    }
                    finish29();
                },
                () -> {
                    finalClassification29 = reason + "_RECOVERY_TIMEOUT";
                    finish29();
                });
    }

    private boolean claim29(String action) {
        String id = action + "_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0, 8);
        boolean ok = prefs29.edit()
                .putString("claim_id", id)
                .putString("claim_action", action)
                .putString("claim_status", "CLAIMED")
                .commit();
        if (!ok) return false;
        currentClaimAction29 = action;
        currentClaimStatus29 = "CLAIMED";
        phase29("VOICE_START_CLAIM", "DURABLE_CLAIMED", captureState29());
        return true;
    }

    private void abortClaim29(String reason) {
        currentClaimStatus29 = "ABORTED_NO_SIDE_EFFECT_" + token29(reason);
        prefs29.edit().putString("claim_status", currentClaimStatus29).commit();
    }

    private void scan29(String target, boolean click, JsonDone29 done) {
        evalJson29(voiceCensusJs29(target, click), done);
    }

    private boolean scanComplete29(JSONObject s) {
        return s != null && s.optBoolean("success", false)
                && s.optBoolean("complete", false)
                && !s.optBoolean("budget_exceeded", true)
                && !s.optBoolean("truncated", true);
    }

    private boolean readyVoice29(JSONObject s) {
        return scanComplete29(s)
                && s.optInt("voice_start_count", -1) == 1
                && s.optInt("voice_end_count", -1) == 0
                && s.optInt("mute_count", -1) == 0
                && s.optInt("unmute_count", -1) == 0;
    }

    private boolean activeUnmutedOld29(JSONObject s) {
        return scanComplete29(s)
                && s.optInt("voice_end_count", -1) == 1
                && s.optInt("mute_count", -1) == 1
                && s.optInt("unmute_count", -1) == 0;
    }

    private boolean activeMutedOld29(JSONObject s) {
        return scanComplete29(s)
                && s.optInt("voice_end_count", -1) == 1
                && s.optInt("mute_count", -1) == 0
                && s.optInt("unmute_count", -1) == 1;
    }

    private void waitCondition29(Condition29 condition, long timeoutMs, Runnable success, Runnable failure) {
        long deadline = System.currentTimeMillis() + timeoutMs;
        waitConditionLoop29(condition, deadline, success, failure);
    }

    private void waitConditionLoop29(Condition29 condition, long deadline, Runnable success, Runnable failure) {
        if (!running29) return;
        if (condition.ok()) { success.run(); return; }
        if (System.currentTimeMillis() >= deadline) { failure.run(); return; }
        h29.postDelayed(() -> waitConditionLoop29(condition, deadline, success, failure), 120L);
    }

    private void evalJson29(String js, JsonDone29 done) {
        if (web29 == null || !trusted29(web29.getUrl())) {
            JSONObject o = new JSONObject(); put29(o, "success", false); put29(o, "error", "UNTRUSTED_WEBVIEW"); done.done(o); return;
        }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!once.compareAndSet(false, true)) return;
            JSONObject o = new JSONObject();
            put29(o, "success", false); put29(o, "error", "EVAL_TIMEOUT"); put29(o, "complete", false);
            done.done(o);
        };
        h29.postDelayed(timeout, EVAL_TIMEOUT_MS);
        try {
            web29.evaluateJavascript(js, value -> {
                if (!once.compareAndSet(false, true)) return;
                h29.removeCallbacks(timeout);
                try { done.done(jsonObject29(value)); }
                catch (Exception e) {
                    JSONObject o = new JSONObject();
                    put29(o, "success", false); put29(o, "complete", false); put29(o, "error", "PARSE_" + e.getClass().getSimpleName());
                    done.done(o);
                }
            });
        } catch (Exception e) {
            if (!once.compareAndSet(false, true)) return;
            h29.removeCallbacks(timeout);
            JSONObject o = new JSONObject();
            put29(o, "success", false); put29(o, "complete", false); put29(o, "error", "EVAL_" + e.getClass().getSimpleName());
            done.done(o);
        }
    }

    private JSONObject jsonObject29(String value) throws Exception {
        Object x = new JSONTokener(value == null ? "null" : value).nextValue();
        if (x instanceof String) x = new JSONTokener((String) x).nextValue();
        if (!(x instanceof JSONObject)) throw new IllegalStateException("not_object");
        return (JSONObject) x;
    }

    private JSONObject captureState29() {
        JSONObject s = new JSONObject();
        put29(s, "session_state", parentString29("sessionState"));
        put29(s, "mic_lease_mode", parentString29("micLeaseMode"));
        put29(s, "parent_last_action", parentString29("lastAction"));
        put29(s, "parent_last_status", parentString29("lastActionStatus"));
        put29(s, "permission_grants", parentInt29("permissionGrants"));
        put29(s, "permission_denials", parentInt29("permissionDenials"));
        put29(s, "active_audio_tracks", parentInt29("activeAudioTracks"));
        put29(s, "media_gum_calls", parentInt29("mediaGumCalls"));
        put29(s, "media_gum_resolves", parentInt29("mediaGumResolves"));
        put29(s, "media_gum_rejects", parentInt29("mediaGumRejects"));
        put29(s, "android_record_audio_granted", checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED);
        try { put29(s, "media_playback_requires_user_gesture", web29 != null && web29.getSettings().getMediaPlaybackRequiresUserGesture()); }
        catch (Exception ignored) {}
        put29(s, "claim_action", currentClaimAction29);
        put29(s, "claim_status", currentClaimStatus29);
        put29(s, "dispatched_side_effects", dispatchedSideEffects29);
        put29(s, "raw_audio_uploaded", false);
        put29(s, "raw_speech_uploaded", false);
        put29(s, "raw_transcript_uploaded", false);
        put29(s, "raw_chat_text_uploaded", false);
        put29(s, "raw_html_uploaded", false);
        put29(s, "cookies_tokens_accessed", false);
        return s;
    }

    private JSONObject withScan29(JSONObject state, JSONObject scan) {
        try { state.put("scan", scan == null ? JSONObject.NULL : scan); }
        catch (Exception ignored) {}
        return state;
    }

    private void phase29(String phase, String classification, JSONObject state) {
        if (!running29 && !"INTERRUPTED_PREVIOUS_RUN".equals(phase)) return;
        persistRun29(running29, phase);
        JSONObject p = payload29(phase, classification, state, seq29++);
        if (telemetryHealthy29 && TelemetryConfigV29.isConfigured()) {
            new Thread(() -> uploadJson29(p, NET_TIMEOUT_MS), "cp29-phase").start();
        }
    }

    private JSONObject payload29(String phase, String classification, JSONObject state, int seq) {
        JSONObject p = new JSONObject();
        put29(p, "schema_version", SCHEMA29);
        put29(p, "scenario_id", SCENARIO29);
        put29(p, "test_id", testId29);
        put29(p, "seq", seq);
        put29(p, "phase", phase);
        put29(p, "classification", classification);
        put29(p, "timestamp_epoch_ms", System.currentTimeMillis());
        put29(p, "source_ref", TelemetryConfigV29.SOURCE_REF);
        put29(p, "collector_id", TelemetryConfigV29.COLLECTOR_ID);
        try { p.put("state", state == null ? new JSONObject() : state); } catch (Exception ignored) {}
        return p;
    }

    private JSONObject uploadJson29(JSONObject body, int timeoutMs) {
        JSONObject out = new JSONObject();
        if (!TelemetryConfigV29.isConfigured()) { put29(out, "success", false); put29(out, "error", "CONFIG_NOT_INJECTED"); return out; }
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(TelemetryConfigV29.WEBHOOK_URL).openConnection();
            c.setConnectTimeout(timeoutMs);
            c.setReadTimeout(timeoutMs);
            c.setRequestMethod("POST");
            c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/json");
            byte[] b = body.toString().getBytes(StandardCharsets.UTF_8);
            c.setFixedLengthStreamingMode(b.length);
            try (OutputStream os = c.getOutputStream()) { os.write(b); }
            int code = c.getResponseCode();
            put29(out, "success", code >= 200 && code < 300);
            put29(out, "http_code", code);
        } catch (Exception e) {
            put29(out, "success", false);
            put29(out, "error", e.getClass().getSimpleName());
        } finally { if (c != null) c.disconnect(); }
        return out;
    }

    private void finishNoSideEffect29() {
        if (!running29) return;
        phase29("FINAL", finalClassification29, captureState29());
        finishUi29();
    }

    private void finish29() {
        if (!running29) return;
        phase29("FINAL", finalClassification29, captureState29());
        finishUi29();
    }

    private void finishUi29() {
        JSONObject local = payload29("LOCAL_FINAL", finalClassification29, captureState29(), seq29);
        saveLocal29(local);
        running29 = false;
        persistRun29(false, "FINAL");
        h29.removeCallbacks(watchdog29);
        setStatus29("v0.29 Voice census finished: " + finalClassification29);
        if (run29 != null) { run29.setEnabled(true); run29.setText("RUN VOICE CENSUS"); }
    }

    private void onWatchdog29() {
        if (!running29) return;
        phase29("WATCHDOG", "GLOBAL_TIMEOUT", captureState29());
        recover29("GLOBAL_TIMEOUT");
    }

    private void persistRun29(boolean active, String phase) {
        if (prefs29 == null) return;
        prefs29.edit().putBoolean("run_active", active).putString("test_id", testId29)
                .putString("phase", phase).putLong("updated_at", System.currentTimeMillis()).commit();
    }

    private void reportInterrupted29() {
        if (prefs29 == null || !prefs29.getBoolean("run_active", false)) return;
        String oldId = prefs29.getString("test_id", "cp29-interrupted");
        String oldPhase = prefs29.getString("phase", "UNKNOWN");
        prefs29.edit().putBoolean("run_active", false).commit();
        if (!TelemetryConfigV29.isConfigured()) return;
        JSONObject p = new JSONObject();
        put29(p, "schema_version", SCHEMA29); put29(p, "scenario_id", SCENARIO29);
        put29(p, "test_id", oldId); put29(p, "seq", -1); put29(p, "phase", "INTERRUPTED_PREVIOUS_RUN");
        put29(p, "classification", "INTERRUPTED_AT_" + token29(oldPhase));
        put29(p, "timestamp_epoch_ms", System.currentTimeMillis()); put29(p, "source_ref", TelemetryConfigV29.SOURCE_REF);
        new Thread(() -> uploadJson29(p, NET_TIMEOUT_MS), "cp29-interrupted").start();
    }

    private void saveLocal29(JSONObject o) {
        try {
            String name = "chatgpt-webview-v29-voice-census-" + testId29 + ".json";
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            cv.put(MediaStore.MediaColumns.MIME_TYPE, "application/json");
            cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (u == null) return;
            try (OutputStream os = getContentResolver().openOutputStream(u)) {
                if (os != null) os.write(o.toString(2).getBytes(StandardCharsets.UTF_8));
            }
        } catch (Exception ignored) {}
    }

    private String voiceCensusJs29(String target, boolean click) {
        return "(function(){try{"
                + "const TARGET='" + js29(target) + "',DO=" + (click ? "true" : "false") + ";"
                + "const T=performance.now(),MAX_MS=180,MAX_NODES=7000,MAX_ROOTS=32,MAX_CAND=16;"
                + "const N=x=>String(x||'').replace(/\\s+/g,' ').trim();"
                + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "const V=e=>{try{const r=e.getBoundingClientRect(),w=e.ownerDocument&&e.ownerDocument.defaultView,s=w?w.getComputedStyle(e):getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
                + "const E=e=>{try{return !e.disabled&&String(e.getAttribute('aria-disabled')||'').toLowerCase()!=='true';}catch(_){return true;}};"
                + "const M=e=>{let z='';try{z+=' '+N(e.getAttribute('aria-label'))+' '+N(e.getAttribute('title'))+' '+N(e.getAttribute('data-testid'))+' '+N(e.getAttribute('name'))+' '+N(e.getAttribute('id'))+' '+N(e.getAttribute('data-state'))+' '+N(e.getAttribute('aria-pressed'))+' '+N(e.innerText||e.textContent||'');const st=e.querySelector&&e.querySelector('svg title');if(st)z+=' '+N(st.textContent||'');}catch(_){}return N(z).toLowerCase();};"
                + "const C=e=>{const a=N(e.getAttribute&&e.getAttribute('aria-label')).toLowerCase(),x=M(e);if(a==='start voice'||/voice mode|open voice|advanced voice|start voice/.test(x))return 'VOICE_START';if(/unmute|turn[^ ]* microphone on|turn microphone on|mic on|microphone on/.test(x))return 'VOICE_UNMUTE';if(/(^|[^a-z])mute([^a-z]|$)|turn microphone off|mic off|microphone off/.test(x))return 'VOICE_MUTE';if(/end voice|leave voice|exit voice|close voice|voice[^a-z]*close|end call|hang up|disconnect/.test(x))return 'VOICE_END';return 'OTHER';};"
                + "const roots=[document],seenR=new Set(),seenE=new Set(),controls=[];let nodes=0,budget=false,trunc=false;"
                + "for(let q=0;q<roots.length&&q<MAX_ROOTS;q++){if(performance.now()-T>MAX_MS){budget=true;break;}const r=roots[q];if(!r||seenR.has(r))continue;seenR.add(r);let all=[];try{all=[...r.querySelectorAll('*')];}catch(_){}for(const e of all){nodes++;if(nodes>MAX_NODES){trunc=true;break;}if(performance.now()-T>MAX_MS){budget=true;break;}try{if(e.shadowRoot&&roots.length<MAX_ROOTS)roots.push(e.shadowRoot);if(e.tagName==='IFRAME'&&e.contentDocument&&roots.length<MAX_ROOTS)roots.push(e.contentDocument);}catch(_){}}if(trunc||budget)break;let bs=[];try{bs=[...r.querySelectorAll('button,[role=button],[aria-label],[data-testid]')];}catch(_){}for(const e of bs){if(!seenE.has(e)&&V(e)&&E(e)){seenE.add(e);controls.push(e);}}}"
                + "const rows=controls.map(e=>{const x=M(e),c=C(e),tag=String(e.tagName||'').toUpperCase(),role=N(e.getAttribute&&e.getAttribute('role')).toLowerCase(),ds=N(e.getAttribute&&e.getAttribute('data-state')).toLowerCase(),ap=N(e.getAttribute&&e.getAttribute('aria-pressed')).toLowerCase(),aria=N(e.getAttribute&&e.getAttribute('aria-label'));const f={voice:/voice/.test(x),mic:/microphone|(^|[^a-z])mic([^a-z]|$)/.test(x),mute:/mute/.test(x),unmute:/unmute/.test(x),audio:/audio|speaker|headphone/.test(x),call:/call|hang/.test(x),end:/end/.test(x),close:/close/.test(x),leave:/leave/.test(x),exit:/exit/.test(x),disconnect:/disconnect/.test(x),stop:/stop/.test(x),settings:/settings/.test(x),camera:/camera/.test(x),video:/video/.test(x)};const rel=Object.values(f).some(Boolean)||c!=='OTHER';let state='unknown';if(/^(open|closed|on|off|active|inactive|true|false|pressed|unpressed)$/.test(ds))state=ds;else if(ap==='true'||ap==='false')state=ap==='true'?'pressed':'unpressed';return {c:c,h:H(x),tag:tag,is_button:tag==='BUTTON',role_button:role==='button',state:state,meta_len:x.length,aria_len:aria.length,aria_present:aria.length>0,features:f,relevant:rel};});"
                + "const semantic=rows.filter(x=>x.c!=='OTHER'),relevant=rows.filter(x=>x.relevant);const cnt=k=>semantic.filter(x=>x.c===k).length;const complete=!budget&&!trunc;const tx=semantic.filter(x=>x.c===TARGET);let clicked=false;if(DO&&complete&&tx.length===1){tx[0].__unused=true;const original=controls.find(e=>C(e)===TARGET);if(original){original.click();clicked=true;}}"
                + "const cand=relevant.slice(0,MAX_CAND).map(x=>({c:x.c,h:x.h,tag:x.tag,is_button:x.is_button,role_button:x.role_button,state:x.state,meta_len:x.meta_len,aria_len:x.aria_len,aria_present:x.aria_present,features:x.features}));"
                + "const dialogs=controls.filter(e=>{try{return e.closest&&e.closest('[role=dialog]');}catch(_){return false;}}).length;"
                + "return JSON.stringify({success:true,complete:complete,budget_exceeded:budget,truncated:trunc,nodes:nodes,roots:seenR.size,visible_controls:controls.length,dialog_control_count:dialogs,voice_start_count:cnt('VOICE_START'),voice_end_count:cnt('VOICE_END'),mute_count:cnt('VOICE_MUTE'),unmute_count:cnt('VOICE_UNMUTE'),semantic_set_hash:H(semantic.map(x=>x.c+':'+x.h).sort().join('|')),relevant_count:relevant.length,candidate_overflow:relevant.length>MAX_CAND,candidate_set_hash:H(relevant.map(x=>x.h).sort().join('|')),candidates:cand,target_matches:tx.length,clicked:clicked});"
                + "}catch(e){return JSON.stringify({success:false,complete:false,budget_exceeded:false,truncated:false,error:String(e&&e.name||'ERR')});}})();";
    }

    private boolean invokeAncestor29(String name, Class<?>[] types, Object[] args) {
        Class<?> c = getClass();
        while (c != null) {
            try {
                Method m = c.getDeclaredMethod(name, types);
                m.setAccessible(true);
                m.invoke(this, args);
                return true;
            } catch (NoSuchMethodException e) { c = c.getSuperclass(); }
            catch (Exception e) { return false; }
        }
        return false;
    }

    private Object field29(String name) {
        Class<?> c = getClass();
        while (c != null) {
            try { Field f = c.getDeclaredField(name); f.setAccessible(true); return f.get(this); }
            catch (NoSuchFieldException e) { c = c.getSuperclass(); }
            catch (Exception e) { return null; }
        }
        return null;
    }

    private String parentString29(String name) {
        Object x = field29(name); return x == null ? "-" : String.valueOf(x);
    }

    private int parentInt29(String name) {
        Object x = field29(name); return x instanceof Number ? ((Number) x).intValue() : -1;
    }

    private WebView findWeb29(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (!(v instanceof ViewGroup)) return null;
        ViewGroup g = (ViewGroup) v;
        for (int i = 0; i < g.getChildCount(); i++) { WebView w = findWeb29(g.getChildAt(i)); if (w != null) return w; }
        return null;
    }

    private Button findRunButton29(View v) {
        if (v instanceof Button) {
            Button b = (Button) v;
            String t = String.valueOf(b.getText());
            if (t.contains("VOICE TEST") || t.contains("VOICE CENSUS")) return b;
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) { Button b = findRunButton29(g.getChildAt(i)); if (b != null) return b; }
        }
        return null;
    }

    private boolean trusted29(String url) {
        if (url == null) return false;
        try { Uri u = Uri.parse(url); return "https".equalsIgnoreCase(u.getScheme()) && "chatgpt.com".equalsIgnoreCase(u.getHost()); }
        catch (Exception e) { return false; }
    }

    private void setStatus29(String s) {
        if (status29 != null) status29.setText(s);
    }

    private static void put29(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) {}
    }

    private static String token29(String s) {
        String x = s == null ? "-" : s.replaceAll("[^A-Za-z0-9_.:+/@=-]", "_");
        return x.length() > 180 ? x.substring(0, 180) : x;
    }

    private static String js29(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r");
    }
}
