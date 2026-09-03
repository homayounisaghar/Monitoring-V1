package com.homayounisaghar.chatgptwebviewprobe;

import android.content.pm.PackageInfo;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
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
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Stable v0.24 compatibility/diagnostic layer on top of the real-device-proven v0.23 harness.
 *
 * Goals:
 * 1) close the v0.23 Send-receipt false negative without replaying Send;
 * 2) classify transcript and first assistant response locally into coarse script/language hints;
 * 3) never upload raw transcript, assistant text, audio, cookies, tokens, credentials, or device IDs.
 */
public class OrchestratorAutonomousV24Activity extends OrchestratorAutonomousV23Activity {
    private static final String DIAG_SCHEMA = "cp-v24-script-diagnostic-v1";
    private static final String DIAG_SCENARIO = "dictation-send-script-diagnostic-v24";
    private static final long EVAL_TIMEOUT_MS = 2600L;
    private static final long ASSISTANT_WAIT_MS = 30000L;
    private static final int NET_TIMEOUT_MS = 2800;

    private final Handler h24 = new Handler(Looper.getMainLooper());
    private WebView web24;
    private String activeTest24 = "-";
    private int diagSeq24 = 0;
    private boolean sendInterceptPending24 = false;
    private boolean transcriptPosted24 = false;
    private boolean receiptPosted24 = false;
    private boolean assistantPending24 = false;
    private boolean assistantPosted24 = false;
    private boolean finalStatusSet24 = false;
    private int assistantBaselineCount24 = -1;
    private int assistantBaselineLen24 = -1;
    private long assistantDeadline24 = 0L;
    private long lastAssistantPoll24 = 0L;
    private String transcriptScript24 = "NOT_OBSERVED";
    private String transcriptLanguageHint24 = "NOT_OBSERVED";
    private String assistantScript24 = "NOT_OBSERVED";
    private String assistantLanguageHint24 = "NOT_OBSERVED";

    private interface JsonCallback24 { void done(JSONObject result); }

    private final Runnable monitor24 = new Runnable() {
        @Override public void run() {
            try { tick24(); } catch (Exception ignored) {}
            h24.postDelayed(this, 220L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web24 = findWeb24(getWindow().getDecorView());
        retargetSendButton24(getWindow().getDecorView());
        h24.postDelayed(monitor24, 250L);
    }

    private void retargetSendButton24(View v) {
        if (v instanceof Button) {
            Button b = (Button) v;
            if ("D SEND".equals(String.valueOf(b.getText()))) b.setOnClickListener(x -> onSendButton24());
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) retargetSendButton24(g.getChildAt(i));
        }
    }

    private void onSendButton24() {
        if (sendInterceptPending24) return;
        boolean harnessRunning = boolField24("running23");
        if (!harnessRunning) {
            invokeV18Send24();
            return;
        }
        sendInterceptPending24 = true;
        readScriptSnapshot24(out -> {
            if (out.optBoolean("success", false)) {
                JSONObject composer = out.optJSONObject("composer");
                JSONObject assistant = out.optJSONObject("assistant");
                assistantBaselineCount24 = out.optInt("assistant_count", -1);
                assistantBaselineLen24 = out.optInt("assistant_len", -1);
                assistantDeadline24 = System.currentTimeMillis() + ASSISTANT_WAIT_MS;
                if (composer != null) {
                    transcriptScript24 = composer.optString("script_class", "UNAVAILABLE");
                    transcriptLanguageHint24 = composer.optString("language_hint", "UNAVAILABLE");
                }
                if (!transcriptPosted24) {
                    transcriptPosted24 = true;
                    JSONObject state = safeClassState24(composer);
                    put24(state, "assistant_baseline_count", assistantBaselineCount24);
                    put24(state, "assistant_baseline_len", assistantBaselineLen24);
                    put24(state, "assistant_baseline_script_class", assistant == null ? "UNAVAILABLE" : assistant.optString("script_class", "UNAVAILABLE"));
                    postDiag24("TRANSCRIPT_SCRIPT_CLASS", transcriptScript24, state);
                }
            } else if (!transcriptPosted24) {
                transcriptPosted24 = true;
                transcriptScript24 = "UNAVAILABLE";
                transcriptLanguageHint24 = "UNAVAILABLE";
                JSONObject state = new JSONObject();
                put24(state, "reason", out.optString("reason", "SCRIPT_SNAPSHOT_FAILED"));
                put24(state, "raw_text_uploaded", false);
                postDiag24("TRANSCRIPT_SCRIPT_CLASS", "UNAVAILABLE", state);
            }
            sendInterceptPending24 = false;
            invokeV18Send24();
        });
    }

    private void tick24() {
        String testId = stringField24("testId23");
        if (testId != null && testId.startsWith("cp23-") && !testId.equals(activeTest24)) resetForTest24(testId);
        if ("-".equals(activeTest24)) return;

        boolean running = boolField24("running23");
        String phase = stringField24("currentPhase23");
        if (running && "DICTATION_SEND_DISPATCH".equals(phase)) bridgeSendReceipt24();

        if (assistantBaselineCount24 >= 0 && !assistantPosted24 && assistantDeadline24 > 0L) {
            long now = System.currentTimeMillis();
            if (now >= assistantDeadline24) {
                assistantPosted24 = true;
                assistantScript24 = "NO_RESPONSE_OBSERVED";
                assistantLanguageHint24 = "NO_RESPONSE_OBSERVED";
                JSONObject state = new JSONObject();
                put24(state, "assistant_baseline_count", assistantBaselineCount24);
                put24(state, "assistant_baseline_len", assistantBaselineLen24);
                put24(state, "raw_text_uploaded", false);
                postDiag24("ASSISTANT_SCRIPT_CLASS", "NO_RESPONSE_OBSERVED", state);
            } else if (!assistantPending24 && now - lastAssistantPoll24 >= 650L) {
                lastAssistantPoll24 = now;
                assistantPending24 = true;
                readScriptSnapshot24(out -> {
                    assistantPending24 = false;
                    if (!out.optBoolean("success", false) || assistantPosted24) return;
                    int count = out.optInt("assistant_count", -1);
                    int len = out.optInt("assistant_len", -1);
                    boolean changed = count > assistantBaselineCount24 || (count == assistantBaselineCount24 && len > assistantBaselineLen24 + 8);
                    if (!changed || len < 8) return;
                    JSONObject a = out.optJSONObject("assistant");
                    if (a == null) return;
                    assistantPosted24 = true;
                    assistantScript24 = a.optString("script_class", "UNAVAILABLE");
                    assistantLanguageHint24 = a.optString("language_hint", "UNAVAILABLE");
                    JSONObject state = safeClassState24(a);
                    put24(state, "assistant_count", count);
                    put24(state, "assistant_len", len);
                    put24(state, "baseline_count", assistantBaselineCount24);
                    put24(state, "baseline_len", assistantBaselineLen24);
                    postDiag24("ASSISTANT_SCRIPT_CLASS", assistantScript24, state);
                });
            }
        }

        if (!running && assistantPosted24 && !finalStatusSet24) setFinalStatus24();
    }

    private void bridgeSendReceipt24() {
        int baseline = intField24("sendBaselineUsers23");
        int users = intField24("userCount");
        int composer = intField24("composerLen");
        boolean externalReceipt = baseline >= 0 && users > baseline && composer == 0;
        if (!externalReceipt) return;

        String a18 = stringField24("last18Action");
        String s18 = stringField24("last18Status");
        boolean v18Confirmed = "DICTATION_SEND".equals(a18) && s18.startsWith("CONFIRMED");

        // Compatibility bridge only: no click/replay occurs here. It exposes the already-observed
        // external receipt to the v0.23 terminal classifier via its inherited receipt fields.
        setField24("lastAction", "DICTATION_SEND");
        setField24("lastActionStatus", v18Confirmed ? "CONFIRMED_V24_EXTERNAL_PLUS_V18_RECEIPT" : "CONFIRMED_V24_EXTERNAL_USER_TURN_COMPOSER_CLEAR");

        if (!receiptPosted24) {
            receiptPosted24 = true;
            JSONObject state = new JSONObject();
            put24(state, "user_turn_advanced", true);
            put24(state, "composer_cleared", true);
            put24(state, "v18_receipt_confirmed", v18Confirmed);
            put24(state, "v18_status_class", classifyStatus24(s18));
            put24(state, "send_replayed", false);
            put24(state, "receipt_basis", "USER_TURN_ADVANCED_AND_COMPOSER_CLEARED");
            postDiag24("SEND_RECEIPT_V24", "PASS_EXTERNAL_USER_TURN_COMPOSER_CLEAR", state);
        }
    }

    private void resetForTest24(String testId) {
        activeTest24 = testId;
        diagSeq24 = 0;
        sendInterceptPending24 = false;
        transcriptPosted24 = false;
        receiptPosted24 = false;
        assistantPending24 = false;
        assistantPosted24 = false;
        finalStatusSet24 = false;
        assistantBaselineCount24 = -1;
        assistantBaselineLen24 = -1;
        assistantDeadline24 = 0L;
        lastAssistantPoll24 = 0L;
        transcriptScript24 = "NOT_OBSERVED";
        transcriptLanguageHint24 = "NOT_OBSERVED";
        assistantScript24 = "NOT_OBSERVED";
        assistantLanguageHint24 = "NOT_OBSERVED";
        JSONObject state = new JSONObject();
        put24(state, "send_receipt_fix", "external_receipt_plus_v18_compatibility_bridge");
        put24(state, "script_diagnostic", "coarse_counts_only_no_text");
        postDiag24("V24_MONITOR_ATTACHED", "READY", state);
    }

    private void setFinalStatus24() {
        finalStatusSet24 = true;
        try {
            Object o = objectField24("status23");
            if (o instanceof TextView) {
                ((TextView) o).setText("TEST COMPLETE v0.24 - transcript=" + transcriptScript24 + "/" + transcriptLanguageHint24
                        + " ; assistant=" + assistantScript24 + "/" + assistantLanguageHint24
                        + ". Tell ChatGPT: test finished");
            }
        } catch (Exception ignored) {}
    }

    private void invokeV18Send24() {
        try {
            Method m = OrchestratorFoundationV18Activity.class.getDeclaredMethod("dictationSend18");
            m.setAccessible(true);
            m.invoke(this);
        } catch (Exception e) {
            JSONObject state = new JSONObject();
            put24(state, "reason", "V18_SEND_INVOKE_" + e.getClass().getSimpleName());
            postDiag24("SEND_INTERCEPT_FAILURE", "FAILED_NO_EXTRA_CLICK", state);
        }
    }

    private void readScriptSnapshot24(JsonCallback24 cb) {
        if (web24 == null) {
            JSONObject o = new JSONObject();
            put24(o, "success", false);
            put24(o, "reason", "WebViewMissing");
            cb.done(o);
            return;
        }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!once.compareAndSet(false, true)) return;
            JSONObject o = new JSONObject();
            put24(o, "success", false);
            put24(o, "reason", "EVAL_CALLBACK_TIMEOUT");
            cb.done(o);
        };
        h24.postDelayed(timeout, EVAL_TIMEOUT_MS);
        try {
            web24.evaluateJavascript(scriptSnapshotJs24(), value -> {
                if (!once.compareAndSet(false, true)) return;
                h24.removeCallbacks(timeout);
                cb.done(decodeJson24(value));
            });
        } catch (Exception e) {
            if (once.compareAndSet(false, true)) {
                h24.removeCallbacks(timeout);
                JSONObject o = new JSONObject();
                put24(o, "success", false);
                put24(o, "reason", "EVAL_THROW_" + e.getClass().getSimpleName());
                cb.done(o);
            }
        }
    }

    private String scriptSnapshotJs24() {
        return "(function(){try{"
                + "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
                + "const N=x=>String(x||'').replace(/\\s+/g,' ').trim();"
                + "const C=t=>{t=N(t);let ar=0,la=0,pm=0,am=0,letters=0;for(const ch of Array.from(t)){const c=ch.codePointAt(0);const isAr=(c>=0x0600&&c<=0x06ff)||(c>=0x0750&&c<=0x077f)||(c>=0x08a0&&c<=0x08ff);const isLa=(c>=0x0041&&c<=0x005a)||(c>=0x0061&&c<=0x007a)||(c>=0x00c0&&c<=0x024f);if(isAr){ar++;letters++;if(c===0x067e||c===0x0686||c===0x0698||c===0x06af||c===0x06a9||c===0x06cc)pm++;if(c===0x0629||c===0x0649||c===0x0623||c===0x0625||c===0x0622)am++;}else if(isLa){la++;letters++;}}let sc='NO_LETTERS';if(letters>0){if(ar/letters>=0.70)sc='ARABIC_PERSIAN_SCRIPT_DOMINANT';else if(la/letters>=0.70)sc='LATIN_SCRIPT_DOMINANT';else if(ar>0&&la>0)sc='MIXED_ARABIC_LATIN';else sc='OTHER_SCRIPT_DOMINANT';}let lh='UNRESOLVED';if(sc==='LATIN_SCRIPT_DOMINANT')lh='LATIN_LANGUAGE_FAMILY';else if(sc==='MIXED_ARABIC_LATIN')lh='MIXED';else if(sc==='ARABIC_PERSIAN_SCRIPT_DOMINANT'){if(pm>=1&&pm>=am)lh='PERSIAN_LIKELY';else if(am>=2&&pm===0)lh='ARABIC_LIKELY';else lh='ARABIC_PERSIAN_UNRESOLVED';}return {script_class:sc,language_hint:lh,arabic_persian_letters:ar,latin_letters:la,persian_markers:pm,arabic_markers:am,total_letters:letters,text_length:t.length,raw_text_returned:false};};"
                + "let ce=null;const canonical=[...document.querySelectorAll('#prompt-textarea')].filter(V);if(canonical.length)ce=canonical[canonical.length-1];if(!ce){const fallback=[...document.querySelectorAll('textarea,[contenteditable=true]')].filter(V);if(fallback.length)ce=fallback[fallback.length-1];}"
                + "const ct=ce?N(typeof ce.value==='string'?ce.value:(ce.innerText||ce.textContent||'')):'';"
                + "const as=[...document.querySelectorAll('[data-message-author-role=assistant]')];const at=as.length?N(as[as.length-1].innerText||as[as.length-1].textContent||''):'';"
                + "return JSON.stringify({success:true,composer:C(ct),assistant:C(at),assistant_count:as.length,assistant_len:at.length,raw_transcript_returned:false,raw_assistant_text_returned:false});"
                + "}catch(e){return JSON.stringify({success:false,reason:String(e&&e.name||'ERR'),raw_transcript_returned:false,raw_assistant_text_returned:false});}})();";
    }

    private JSONObject safeClassState24(JSONObject src) {
        JSONObject o = new JSONObject();
        if (src == null) {
            put24(o, "script_class", "UNAVAILABLE");
            put24(o, "language_hint", "UNAVAILABLE");
            put24(o, "raw_text_uploaded", false);
            return o;
        }
        put24(o, "script_class", src.optString("script_class", "UNAVAILABLE"));
        put24(o, "language_hint", src.optString("language_hint", "UNAVAILABLE"));
        put24(o, "arabic_persian_letters", src.optInt("arabic_persian_letters", 0));
        put24(o, "latin_letters", src.optInt("latin_letters", 0));
        put24(o, "persian_markers", src.optInt("persian_markers", 0));
        put24(o, "arabic_markers", src.optInt("arabic_markers", 0));
        put24(o, "total_letters", src.optInt("total_letters", 0));
        put24(o, "text_length", src.optInt("text_length", 0));
        put24(o, "raw_text_uploaded", false);
        return o;
    }

    private void postDiag24(String phase, String classification, JSONObject state) {
        if (!TelemetryConfigV24.isConfigured()) return;
        final JSONObject payload = new JSONObject();
        put24(payload, "kind", "DIAGNOSTIC_PHASE");
        put24(payload, "schema_version", DIAG_SCHEMA);
        put24(payload, "scenario_id", DIAG_SCENARIO);
        put24(payload, "test_id", activeTest24);
        put24(payload, "seq", ++diagSeq24);
        put24(payload, "phase", phase);
        put24(payload, "classification", classification);
        put24(payload, "app_version", appVersion24());
        put24(payload, "source_ref", TelemetryConfigV24.SOURCE_REF);
        put24(payload, "collector_id", TelemetryConfigV24.COLLECTOR_ID);
        put24(payload, "privacy", "coarse_script_counts_and_receipts_only_no_raw_audio_speech_transcript_assistant_chat_or_credentials");
        put24(payload, "timestamp_epoch_ms", System.currentTimeMillis());
        put24(payload, "state", state == null ? new JSONObject() : state);
        new Thread(() -> upload24(payload), "cp24-diag-" + diagSeq24).start();
    }

    private void upload24(JSONObject payload) {
        HttpURLConnection conn = null;
        try {
            URL url = new URL(TelemetryConfigV24.WEBHOOK_URL);
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setConnectTimeout(NET_TIMEOUT_MS);
            conn.setReadTimeout(NET_TIMEOUT_MS);
            conn.setDoOutput(true);
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            conn.setRequestProperty("X-Probe-Schema", DIAG_SCHEMA);
            byte[] body = payload.toString().getBytes(StandardCharsets.UTF_8);
            conn.setFixedLengthStreamingMode(body.length);
            try (OutputStream os = conn.getOutputStream()) { os.write(body); }
            conn.getResponseCode();
        } catch (Exception ignored) {
        } finally {
            if (conn != null) conn.disconnect();
        }
    }

    private JSONObject decodeJson24(String value) {
        try {
            Object decoded = new JSONTokener(value == null ? "null" : value).nextValue();
            String text = decoded instanceof String ? (String) decoded : String.valueOf(decoded);
            return new JSONObject(text);
        } catch (Exception e) {
            JSONObject o = new JSONObject();
            put24(o, "success", false);
            put24(o, "reason", "JSON_DECODE_" + e.getClass().getSimpleName());
            return o;
        }
    }

    private String classifyStatus24(String s) {
        if (s == null) return "NONE";
        if (s.startsWith("CONFIRMED")) return "CONFIRMED";
        if (s.startsWith("UNCERTAIN")) return "UNCERTAIN";
        if (s.startsWith("ABORTED") || s.startsWith("BLOCKED")) return "NO_SIDE_EFFECT_OR_BLOCKED";
        return "OTHER";
    }

    private Field field24(String name) {
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

    private Object objectField24(String name) {
        try {
            Field f = field24(name);
            return f == null ? null : f.get(this);
        } catch (Exception e) { return null; }
    }

    private String stringField24(String name) {
        Object v = objectField24(name);
        return v == null ? "UNKNOWN" : String.valueOf(v);
    }

    private int intField24(String name) {
        try {
            Field f = field24(name);
            return f == null ? -1 : f.getInt(this);
        } catch (Exception e) { return -1; }
    }

    private boolean boolField24(String name) {
        try {
            Field f = field24(name);
            return f != null && f.getBoolean(this);
        } catch (Exception e) { return false; }
    }

    private void setField24(String name, Object value) {
        try {
            Field f = field24(name);
            if (f == null) return;
            if (value instanceof Long) f.setLong(this, (Long) value);
            else if (value instanceof Integer) f.setInt(this, (Integer) value);
            else if (value instanceof Boolean) f.setBoolean(this, (Boolean) value);
            else f.set(this, value);
        } catch (Exception ignored) {}
    }

    private WebView findWeb24(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb24(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }

    private String appVersion24() {
        try {
            PackageInfo pi = getPackageManager().getPackageInfo(getPackageName(), 0);
            return pi.versionName + "(" + pi.getLongVersionCode() + ")";
        } catch (Exception e) { return "unknown"; }
    }

    private void put24(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) {}
    }

    @Override protected void onDestroy() {
        h24.removeCallbacksAndMessages(null);
        super.onDestroy();
    }
}
