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

import org.json.JSONArray;
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
 * Stable v0.20 - autonomous post-Dictation semantic fingerprint harness.
 *
 * v0.19 proved that Dictation Start succeeds, then the active composer changes
 * from DICTATION=1 to DICTATION=0 / STOP=0 / SEND=1 / CANCEL=2. The existing
 * Stop resolver therefore fails closed with MATCHES_0. This diagnostic does not
 * guess which of those controls means finish/accept/stop. It starts Dictation
 * exactly once, captures bounded allowlisted fingerprints of visible button-like
 * controls, uploads them, then performs unconditional Session recovery.
 *
 * This remains a TEST CLIENT above the v0.18 orchestrator. It performs no ChatGPT
 * message send, no unknown-control click, no coordinate/XPath action, no private
 * ChatGPT API call, and uploads no raw audio, speech, chat text, cookies or tokens.
 */
public class OrchestratorSemanticFingerprintV20Activity extends OrchestratorFoundationV18Activity {
    private static final String PREFS20 = "stable_v20_semantic_fingerprint";
    private static final String SCHEMA_VERSION = "cp-autonomous-runtime-v1";
    private static final String SCENARIO_ID = "dictation-active-control-fingerprint";
    private static final int SCENARIO_VERSION = 1;

    private final Handler h20 = new Handler(Looper.getMainLooper());
    private final StringBuilder localEvents20 = new StringBuilder();

    private SharedPreferences prefs20;
    private WebView web20;
    private Button runButton20;
    private TextView status20;

    private boolean running20 = false;
    private boolean telemetryHealthy20 = false;
    private String testId20 = "-";
    private int seq20 = 0;
    private long startedAt20 = 0L;
    private String finalClassification20 = "NOT_RUN";
    private int fingerprintControlCount20 = -1;

    private interface UploadCallback20 { void done(JSONObject result); }
    private interface Condition20 { boolean ok(); }
    private interface FingerprintCallback20 { void done(JSONObject result); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs20 = getSharedPreferences(PREFS20, MODE_PRIVATE);
        web20 = findWeb20(getWindow().getDecorView());
        if (web20 != null) {
            web20.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        }
        installHarnessPanel20();
        reportInterruptedRunIfNeeded20();
    }

    private void installHarnessPanel20() {
        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) content;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        int wi = web20 == null ? 0 : root.indexOfChild(web20);
        if (wi < 0) wi = 0;

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp20(6), dp20(3), dp20(6), dp20(3));

        runButton20 = new Button(this);
        runButton20.setText("RUN FULL TEST");
        runButton20.setTextSize(14f);
        runButton20.setAllCaps(false);
        runButton20.setOnClickListener(v -> runFullTest20());
        panel.addView(runButton20, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp20(52)));

        status20 = new TextView(this);
        status20.setTextSize(10f);
        status20.setText("v0.20 semantic fingerprint harness ready");
        status20.setPadding(dp20(6), dp20(3), dp20(6), dp20(3));
        panel.addView(status20, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));

        root.addView(panel, wi, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void runFullTest20() {
        if (running20) return;
        running20 = true;
        telemetryHealthy20 = false;
        testId20 = "cp20-" + UUID.randomUUID();
        seq20 = 0;
        startedAt20 = System.currentTimeMillis();
        finalClassification20 = "RUNNING";
        fingerprintControlCount20 = -1;
        localEvents20.setLength(0);
        if (runButton20 != null) {
            runButton20.setEnabled(false);
            runButton20.setText("RUNNING...");
        }
        persistRun20(true, "STARTING");
        setStatus20("Telemetry preflight...");

        JSONObject pre = captureState20();
        put20(pre, "preflight", true);
        postPhase20("TELEMETRY_PREFLIGHT", "RUNNING", pre, result -> {
            if (!result.optBoolean("success", false)) {
                telemetryHealthy20 = false;
                finalClassification20 = "TELEMETRY_UNAVAILABLE";
                log20("TELEMETRY_PREFLIGHT_FAIL");
                finishLocally20(false);
                return;
            }
            telemetryHealthy20 = true;
            postRequiredPhase20("RUN_STARTED", "RUNNING", captureState20(), this::waitForBaseline20);
        });
    }

    private void waitForBaseline20() {
        setStatus20("Waiting for stable semantic snapshot...");
        waitUntil20(() -> boolField20("snapOk"), 4000L,
                () -> postRequiredPhase20("BASELINE_READY", "RUNNING", captureState20(), this::startSession20),
                () -> {
                    finalClassification20 = "SNAPSHOT_NOT_READY";
                    postPhase20("BASELINE_TIMEOUT", "FAIL", captureState20(), r -> recoverSession20());
                });
    }

    private void startSession20() {
        setStatus20("Starting InteractionSession...");
        JSONObject click = clickButton20("SESSION START");
        JSONObject state = captureState20();
        put20(state, "click", click);
        postRequiredPhase20("SESSION_START_DISPATCH", "RUNNING", state, () ->
                waitUntil20(() -> "ACTIVE".equals(stringField20("sessionState")), 4000L,
                        () -> postRequiredPhase20("SESSION_ACTIVE", "RUNNING", captureState20(), this::startDictation20),
                        () -> {
                            finalClassification20 = "SESSION_START_FAILED";
                            postPhase20("SESSION_START_TIMEOUT", "FAIL", captureState20(), r -> recoverSession20());
                        }));
    }

    private void startDictation20() {
        setStatus20("Starting Dictation once...");
        postRequiredPhase20("BEFORE_DICTATION_START", "RUNNING", captureState20(), () -> {
            JSONObject click = clickButton20("D START");
            JSONObject state = captureState20();
            put20(state, "click", click);
            postRequiredPhase20("DICTATION_START_DISPATCH", "RUNNING", state, () ->
                    waitUntil20(this::dictationStartObserved20, 5500L,
                            () -> h20.postDelayed(this::postStartCheckpoint20, 1000L),
                            () -> {
                                finalClassification20 = "DICTATION_START_FAILED";
                                postPhase20("DICTATION_START_TIMEOUT", "FAIL", captureState20(), r -> recoverSession20());
                            }));
        });
    }

    private boolean dictationStartObserved20() {
        String lease = stringField20("micLeaseMode");
        String parentStatus = stringField20("lastActionStatus");
        String wrapperStatus = stringField20("lastWrapperStatus");
        return "DICTATION".equals(lease)
                && (parentStatus.contains("CONFIRMED")
                || parentStatus.contains("ACCEPTED_REVERSIBLE_START")
                || wrapperStatus.contains("CONFIRMED")
                || wrapperStatus.contains("ACCEPTED_REVERSIBLE_START"));
    }

    private void postStartCheckpoint20() {
        setStatus20("Capturing post-Start state...");
        postRequiredPhase20("POST_DICTATION_START", "RUNNING", captureState20(), () ->
                h20.postDelayed(this::captureFingerprintsFirst20, 700L));
    }

    private void captureFingerprintsFirst20() {
        setStatus20("Reading active composer controls...");
        captureControlFingerprints20(fp -> {
            JSONObject state = captureState20();
            put20(state, "fingerprint", fp);
            fingerprintControlCount20 = fp.optInt("control_count", -1);
            String cls = fp.optBoolean("success", false) ? "FINGERPRINT_CAPTURED" : "FINGERPRINT_FAILED";
            postRequiredPhase20("ACTIVE_CONTROL_FINGERPRINT_1", cls, state, () ->
                    h20.postDelayed(this::captureFingerprintsSecond20, 900L));
        });
    }

    private void captureFingerprintsSecond20() {
        captureControlFingerprints20(fp -> {
            JSONObject state = captureState20();
            put20(state, "fingerprint", fp);
            int secondCount = fp.optInt("control_count", -1);
            boolean ok = fp.optBoolean("success", false);
            put20(state, "first_control_count", fingerprintControlCount20);
            put20(state, "second_control_count", secondCount);
            put20(state, "count_stable", fingerprintControlCount20 >= 0 && fingerprintControlCount20 == secondCount);
            if (!ok && "RUNNING".equals(finalClassification20)) finalClassification20 = "FINGERPRINT_CAPTURE_FAILED";
            postPhase20("ACTIVE_CONTROL_FINGERPRINT_2", ok ? "FINGERPRINT_CAPTURED" : "FINGERPRINT_FAILED", state,
                    r -> recoverSession20());
        });
    }

    private void recoverSession20() {
        setStatus20("Recovering session...");
        JSONObject before = captureState20();
        put20(before, "unknown_control_clicked", false);
        postPhase20("BEFORE_RECOVERY", "RUNNING", before, r -> {
            JSONObject click;
            if ("ACTIVE".equals(stringField20("sessionState"))) {
                click = clickButton20("SESSION END");
            } else {
                click = clickResult20("SESSION END", false, false, "already_not_active");
            }
            JSONObject after = captureState20();
            put20(after, "click", click);
            postPhase20("RECOVERY_DISPATCH", "RUNNING", after, x ->
                    waitUntil20(this::recoveryComplete20, 5000L,
                            () -> finishAfterRecovery20(true),
                            () -> finishAfterRecovery20(false)));
        });
    }

    private boolean recoveryComplete20() {
        return "IDLE".equals(stringField20("sessionState"))
                && "NONE".equals(stringField20("micLeaseMode"));
    }

    private void finishAfterRecovery20(boolean recovered) {
        if ("RUNNING".equals(finalClassification20)) {
            finalClassification20 = recovered
                    ? "PASS_FINGERPRINT_CAPTURED_RECOVERED"
                    : "FINGERPRINT_CAPTURED_RECOVERY_FAILED";
        } else {
            finalClassification20 = finalClassification20 + (recovered ? "_RECOVERED" : "_RECOVERY_FAILED");
        }
        JSONObject state = captureState20();
        put20(state, "recovered", recovered);
        put20(state, "unknown_control_clicked", false);
        put20(state, "final_classification", finalClassification20);
        postPhase20("RECOVERY_RESULT", recovered ? "RECOVERED" : "RECOVERY_FAILED", state, r ->
                postPhase20("FINAL", finalClassification20, captureState20(), finalUpload ->
                        finishLocally20(finalUpload.optBoolean("success", false))));
    }

    private void captureControlFingerprints20(FingerprintCallback20 callback) {
        if (web20 == null) {
            JSONObject o = new JSONObject();
            put20(o, "success", false);
            put20(o, "error", "WebViewMissing");
            callback.done(o);
            return;
        }
        web20.evaluateJavascript(FINGERPRINT_JS_20, value -> {
            JSONObject out;
            try {
                Object decoded = new JSONTokener(value == null ? "null" : value).nextValue();
                String text = decoded instanceof String ? (String) decoded : String.valueOf(decoded);
                out = new JSONObject(text);
            } catch (Exception e) {
                out = new JSONObject();
                put20(out, "success", false);
                put20(out, "error", "FingerprintParse_" + e.getClass().getSimpleName());
            }
            callback.done(out);
        });
    }

    private void postRequiredPhase20(String phase, String classification, JSONObject state, Runnable next) {
        postPhase20(phase, classification, state, result -> {
            if (!result.optBoolean("success", false)) {
                telemetryHealthy20 = false;
                if ("RUNNING".equals(finalClassification20)) finalClassification20 = "TELEMETRY_LOST_AT_" + phase;
                log20("REQUIRED_UPLOAD_FAIL_" + phase);
                recoverSession20();
                return;
            }
            next.run();
        });
    }

    private void postPhase20(String phase, String classification, JSONObject state, UploadCallback20 callback) {
        int seq = ++seq20;
        persistRun20(true, phase);
        JSONObject payload = new JSONObject();
        put20(payload, "kind", "TEST_PHASE");
        put20(payload, "schema_version", SCHEMA_VERSION);
        put20(payload, "scenario_id", SCENARIO_ID);
        put20(payload, "scenario_version", SCENARIO_VERSION);
        put20(payload, "test_id", testId20);
        put20(payload, "seq", seq);
        put20(payload, "phase", phase);
        put20(payload, "classification", classification);
        put20(payload, "app_version", appVersion20());
        put20(payload, "source_ref", TelemetryConfigV20.SOURCE_REF);
        put20(payload, "collector_id", TelemetryConfigV20.COLLECTOR_ID);
        put20(payload, "elapsed_ms", startedAt20 == 0L ? 0L : System.currentTimeMillis() - startedAt20);
        put20(payload, "timestamp_epoch_ms", System.currentTimeMillis());
        put20(payload, "privacy", "allowlisted_control_metadata_no_raw_audio_speech_chat_or_credentials");
        put20(payload, "state", state == null ? new JSONObject() : state);
        log20("PHASE " + seq + " " + phase + " " + classification);

        new Thread(() -> {
            JSONObject result = uploadJson20(payload, 2);
            runOnUiThread(() -> callback.done(result));
        }, "cp20-telemetry-" + seq).start();
    }

    private JSONObject uploadJson20(JSONObject payload, int attempts) {
        JSONObject result = new JSONObject();
        put20(result, "configured", TelemetryConfigV20.isConfigured());
        if (!TelemetryConfigV20.isConfigured()) {
            put20(result, "success", false);
            put20(result, "error", "TelemetryNotConfigured");
            return result;
        }
        for (int attempt = 1; attempt <= attempts; attempt++) {
            HttpURLConnection conn = null;
            try {
                URL url = new URL(TelemetryConfigV20.WEBHOOK_URL);
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
                put20(result, "http_status", code);
                put20(result, "attempts", attempt);
                if (code >= 200 && code < 300) {
                    put20(result, "success", true);
                    return result;
                }
            } catch (Exception e) {
                put20(result, "error", e.getClass().getSimpleName());
                put20(result, "attempts", attempt);
            } finally {
                if (conn != null) conn.disconnect();
            }
            try { Thread.sleep(900L); }
            catch (InterruptedException e) { Thread.currentThread().interrupt(); break; }
        }
        put20(result, "success", false);
        return result;
    }

    private JSONObject captureState20() {
        JSONObject o = new JSONObject();
        put20(o, "session_state", stringField20("sessionState"));
        put20(o, "mic_lease_mode", stringField20("micLeaseMode"));
        put20(o, "snapshot_ok", boolField20("snapOk"));
        put20(o, "dictation_count", intField20("dictationCount"));
        put20(o, "stop_count", intField20("stopCount"));
        put20(o, "send_count", intField20("sendCount"));
        put20(o, "cancel_count", intField20("cancelCount"));
        put20(o, "voice_start_count", intField20("voiceStartCount"));
        put20(o, "voice_end_count", intField20("voiceEndCount"));
        put20(o, "parent_last_action", stringField20("lastAction"));
        put20(o, "parent_last_status", stringField20("lastActionStatus"));
        put20(o, "wrapper_last_status", stringField20("lastWrapperStatus"));
        put20(o, "v18_last_action", stringField20("last18Action"));
        put20(o, "v18_last_status", stringField20("last18Status"));
        put20(o, "forced_session_end_count", intField20("forcedSessionEnds"));
        put20(o, "run_state", stringField20("runState18"));
        put20(o, "webview_present", web20 != null);
        put20(o, "telemetry_healthy", telemetryHealthy20);
        put20(o, "unknown_control_clicked", false);
        return o;
    }

    private JSONObject clickButton20(String exactText) {
        JSONObject out = new JSONObject();
        Button b = findButton20(getWindow().getDecorView(), exactText);
        put20(out, "requested", exactText);
        put20(out, "found", b != null);
        if (b == null) {
            put20(out, "clicked", false);
            put20(out, "reason", "button_not_found");
            return out;
        }
        boolean enabled = b.isEnabled();
        boolean visible = b.getVisibility() == View.VISIBLE;
        put20(out, "enabled", enabled);
        put20(out, "visible", visible);
        boolean clicked = false;
        if (enabled && visible) {
            try { clicked = b.performClick(); }
            catch (Exception ignored) { }
        }
        put20(out, "clicked", clicked);
        return out;
    }

    private JSONObject clickResult20(String requested, boolean found, boolean clicked, String reason) {
        JSONObject out = new JSONObject();
        put20(out, "requested", requested);
        put20(out, "found", found);
        put20(out, "clicked", clicked);
        put20(out, "reason", reason);
        return out;
    }

    private Button findButton20(View v, String exactText) {
        if (v instanceof Button) {
            Button b = (Button) v;
            if (exactText.equals(String.valueOf(b.getText()))) return b;
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                Button b = findButton20(g.getChildAt(i), exactText);
                if (b != null) return b;
            }
        }
        return null;
    }

    private void waitUntil20(Condition20 condition, long timeoutMs, Runnable success, Runnable timeout) {
        final long start = System.currentTimeMillis();
        final Runnable[] poll = new Runnable[1];
        poll[0] = () -> {
            if (!running20) return;
            boolean ok = false;
            try { ok = condition.ok(); } catch (Exception ignored) { }
            if (ok) { success.run(); return; }
            if (System.currentTimeMillis() - start >= timeoutMs) { timeout.run(); return; }
            h20.postDelayed(poll[0], 250L);
        };
        h20.post(poll[0]);
    }

    private void reportInterruptedRunIfNeeded20() {
        if (!prefs20.getBoolean("run_active", false)) return;
        String oldId = prefs20.getString("test_id", "cp20-interrupted-unknown");
        int oldSeq = prefs20.getInt("seq", 0);
        long oldStart = prefs20.getLong("started_at", System.currentTimeMillis());
        String oldPhase = prefs20.getString("phase", "UNKNOWN");
        testId20 = oldId;
        seq20 = oldSeq;
        startedAt20 = oldStart;
        JSONObject state = captureState20();
        put20(state, "interrupted_after_phase", oldPhase);
        postPhase20("RUN_INTERRUPTED_APP_RESTART", "FAIL", state, r -> {
            prefs20.edit().putBoolean("run_active", false).apply();
            setStatus20("Previous run interruption reported. Ready for a new test.");
        });
    }

    private void persistRun20(boolean active, String phase) {
        prefs20.edit()
                .putBoolean("run_active", active)
                .putString("test_id", testId20)
                .putInt("seq", seq20)
                .putLong("started_at", startedAt20)
                .putString("phase", phase)
                .apply();
    }

    private void finishLocally20(boolean finalUploadOk) {
        running20 = false;
        persistRun20(false, "FINISHED");
        if (runButton20 != null) {
            runButton20.setEnabled(true);
            runButton20.setText("RUN AGAIN");
        }
        if (finalUploadOk) {
            setStatus20("TEST COMPLETE - report uploaded. Tell ChatGPT: test finished");
        } else {
            saveFallback20();
            setStatus20("TEST COMPLETE - telemetry unavailable; local fallback saved");
        }
    }

    private void saveFallback20() {
        try {
            JSONObject o = captureState20();
            put20(o, "test_id", testId20);
            put20(o, "final_classification", finalClassification20);
            put20(o, "events", localEvents20.toString());
            String name = "chatgpt-webview-v20-fallback-"
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
            Toast.makeText(this, "v0.20 fallback saved to Downloads", Toast.LENGTH_LONG).show();
        } catch (Exception ignored) { }
    }

    private String appVersion20() {
        try {
            PackageInfo pi = getPackageManager().getPackageInfo(getPackageName(), 0);
            return pi.versionName + "(" + pi.getLongVersionCode() + ")";
        } catch (Exception e) {
            return "unknown";
        }
    }

    private WebView findWeb20(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb20(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }

    private Field field20(String name) {
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

    private String stringField20(String name) {
        try {
            Field f = field20(name);
            if (f == null) return "UNKNOWN";
            Object v = f.get(this);
            return v == null ? "NONE" : String.valueOf(v);
        } catch (Exception e) { return "ERROR"; }
    }

    private int intField20(String name) {
        try {
            Field f = field20(name);
            return f == null ? -1 : f.getInt(this);
        } catch (Exception e) { return -1; }
    }

    private boolean boolField20(String name) {
        try {
            Field f = field20(name);
            return f != null && f.getBoolean(this);
        } catch (Exception e) { return false; }
    }

    private int dp20(int x) {
        return Math.round(x * getResources().getDisplayMetrics().density);
    }

    private void setStatus20(String s) {
        runOnUiThread(() -> { if (status20 != null) status20.setText(s); });
        log20("STATUS " + s);
    }

    private void log20(String s) {
        String safe = s == null ? "" : s.replace('\n', ' ');
        if (safe.length() > 700) safe = safe.substring(0, 700);
        localEvents20.append(System.currentTimeMillis()).append(" | ").append(safe).append('\n');
    }

    private void put20(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) { }
    }

    @Override protected void onDestroy() {
        h20.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    /**
     * Synchronous DOM fingerprinting only. Async browser operations are not
     * completed through evaluateJavascript callbacks in this harness.
     * Values are allowlisted and truncated; chat/composer/message text is never read.
     */
    private static final String FINGERPRINT_JS_20 =
            "(function(){try{" +
            "const N=s=>String(s==null?'':s).replace(/\\s+/g,' ').trim();" +
            "const T=(s,n)=>N(s).slice(0,n);" +
            "const A=(e,n)=>T(e&&e.getAttribute?e.getAttribute(n):'',96);" +
            "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(x){return false;}};" +
            "const H=s=>{let h=2166136261>>>0;for(const c of String(s)){h^=c.charCodeAt(0);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};" +
            "const isB=e=>e&&((e.tagName||'').toLowerCase()==='button'||A(e,'role').toLowerCase()==='button');" +
            "const roots=[];const seen=new Set();" +
            "function walkRoot(root,scope){if(!root||seen.has(root))return;seen.add(root);roots.push({root,scope});let es=[];try{es=[...root.querySelectorAll('*')];}catch(x){}for(const e of es){try{if(e.shadowRoot)walkRoot(e.shadowRoot,scope+'/shadow');}catch(x){}if((e.tagName||'').toLowerCase()==='iframe'){try{const d=e.contentDocument;if(d)walkRoot(d,scope+'/frame');}catch(x){}}}}" +
            "walkRoot(document,'main');" +
            "const out=[];const dedup=new Set();" +
            "for(const rr of roots){let xs=[];try{xs=[...rr.root.querySelectorAll('button,[role=button]')];}catch(x){}for(const e of xs){if(!isB(e)||!V(e)||dedup.has(e))continue;dedup.add(e);" +
            "const aria=A(e,'aria-label'),title=A(e,'title'),tid=A(e,'data-testid'),name=A(e,'name'),type=A(e,'type'),role=A(e,'role')||'button',state=A(e,'data-state'),slot=A(e,'data-slot'),pressed=A(e,'aria-pressed');" +
            "const text=T(e.innerText||e.textContent||'',72);" +
            "const svgTitle=(()=>{try{const q=e.querySelector('svg title');return q?T(q.textContent,72):'';}catch(x){return '';}})();" +
            "let p=e.parentElement;const parent={tag:p?String(p.tagName||'').toLowerCase():'',role:A(p,'role'),test_id:A(p,'data-testid'),slot:A(p,'data-slot')};" +
            "let form=null;try{form=e.closest('form');}catch(x){}" +
            "let nearPrompt=false,formButtons=-1,formTid='';if(form){formTid=A(form,'data-testid');try{nearPrompt=!!form.querySelector('#prompt-textarea,textarea,[contenteditable=true]');formButtons=[...form.querySelectorAll('button,[role=button]')].filter(V).length;}catch(x){}}" +
            "let sibIndex=-1,sibCount=-1;if(p){try{const bs=[...p.children].filter(x=>isB(x)&&V(x));sibCount=bs.length;sibIndex=bs.indexOf(e);}catch(x){}}" +
            "const words=(aria+' '+title+' '+tid+' '+name+' '+text+' '+svgTitle).toLowerCase();let hint='UNKNOWN';" +
            "if(/cancel|discard|close/.test(words))hint='CANCEL_LIKE';else if(/send|submit/.test(words))hint='SEND_LIKE';else if(/stop|finish|done|complete|accept|confirm/.test(words))hint='FINISH_LIKE';else if(/microphone|dictat|record|voice/.test(words))hint='AUDIO_LIKE';" +
            "const sig=[rr.scope,aria,title,tid,name,type,role,state,slot,pressed,text,svgTitle,parent.tag,parent.role,parent.test_id,parent.slot,String(nearPrompt),String(sibIndex),String(sibCount)].join('|');" +
            "out.push({index:out.length,scope:rr.scope,tag:String(e.tagName||'').toLowerCase(),role:role,aria_label:aria,title:title,test_id:tid,name:name,type:type,data_state:state,data_slot:slot,aria_pressed:pressed,disabled:!!e.disabled,text_hint:text,svg_title:svgTitle,semantic_hint:hint,parent:parent,in_form:!!form,form_test_id:formTid,near_prompt:nearPrompt,form_visible_button_count:formButtons,sibling_button_index:sibIndex,sibling_button_count:sibCount,fingerprint_hash:H(sig)});" +
            "}}" +
            "return JSON.stringify({success:true,control_count:out.length,controls:out.slice(0,32),truncated:out.length>32,raw_chat_text_read:false,composer_text_read:false});" +
            "}catch(e){return JSON.stringify({success:false,error:String(e&&e.name||'ERR'),raw_chat_text_read:false,composer_text_read:false});}})();";
}
