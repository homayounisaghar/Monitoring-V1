package com.homayounisaghar.chatgptwebviewprobe;

import android.content.ContentValues;
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

/**
 * Stable v0.25: bounded ready-state Dictation Start semantic census.
 *
 * This diagnostic intentionally performs NO ChatGPT control click and NO Session start.
 * It only fingerprints visible UI chrome near the composer using allowlisted metadata,
 * then exits. No composer/chat text, raw audio/speech, cookies, tokens or credentials
 * are read or uploaded.
 */
public class OrchestratorReadyStartCensusV25Activity extends OrchestratorAutonomousV24Activity {
    private static final String SCHEMA = "cp-v25-ready-start-census-v1";
    private static final String SCENARIO = "dictation-ready-start-census-v25";
    private static final long EVAL_TIMEOUT_MS = 2600L;
    private static final long READY_WAIT_MS = 9000L;
    private static final long SECOND_SNAPSHOT_DELAY_MS = 850L;
    private static final int NET_TIMEOUT_MS = 2800;

    private final Handler h25 = new Handler(Looper.getMainLooper());
    private WebView web25;
    private Button run25;
    private TextView status25;
    private boolean running25 = false;
    private String testId25 = "-";
    private int seq25 = 0;
    private long started25 = 0L;
    private JSONObject censusOne25;
    private JSONObject censusTwo25;

    private interface JsonDone25 { void done(JSONObject result); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web25 = findWeb25(getWindow().getDecorView());
        run25 = findButton25(getWindow().getDecorView(), "RUN FULL TEST");
        status25 = inheritedStatus25();
        if (run25 != null) {
            run25.setText("RUN START CENSUS");
            run25.setOnClickListener(v -> runCensus25());
        }
        setStatus25("v0.25 ready-state census ready — no control clicks");
    }

    private void runCensus25() {
        if (running25) return;
        running25 = true;
        testId25 = "cp25-" + UUID.randomUUID();
        seq25 = 0;
        started25 = System.currentTimeMillis();
        censusOne25 = null;
        censusTwo25 = null;
        if (run25 != null) { run25.setEnabled(false); run25.setText("CENSUS RUNNING..."); }
        setStatus25("Telemetry preflight...");

        JSONObject pre = new JSONObject();
        put25(pre, "no_control_clicks", true);
        put25(pre, "webview_present", web25 != null);
        uploadRequired25(payload25("TELEMETRY_PREFLIGHT", "RUNNING", pre), ok -> {
            if (!ok) {
                finish25("TELEMETRY_UNAVAILABLE", "CENSUS NOT STARTED — telemetry unavailable");
                return;
            }
            waitForReadyComposer25(System.currentTimeMillis() + READY_WAIT_MS);
        });
    }

    private void waitForReadyComposer25(long deadline) {
        if (!running25) return;
        setStatus25("Waiting for stable composer chrome...");
        eval25(READY_PROBE_JS_25, out -> {
            if (!running25) return;
            boolean ready = out.optBoolean("success", false)
                    && out.optBoolean("prompt_visible", false)
                    && out.optBoolean("root_found", false);
            if (ready) {
                JSONObject s = safeProbe25(out);
                postBestEffort25("READY_COMPOSER", "READY", s);
                captureFirst25();
                return;
            }
            if (System.currentTimeMillis() >= deadline) {
                JSONObject s = safeProbe25(out);
                postBestEffort25("READY_TIMEOUT", "PROMPT_OR_ROOT_NOT_READY", s);
                finish25("READY_TIMEOUT", "CENSUS COMPLETE — composer chrome was not ready");
                return;
            }
            h25.postDelayed(() -> waitForReadyComposer25(deadline), 350L);
        });
    }

    private void captureFirst25() {
        setStatus25("Capturing bounded ready-state census 1/2...");
        eval25(CENSUS_JS_25, out -> {
            if (!running25) return;
            censusOne25 = sanitizeCensus25(out);
            postBestEffort25("READY_CENSUS_1", classifyCensus25(censusOne25), censusOne25);
            if (!censusOne25.optBoolean("success", false)) {
                finish25("CENSUS_1_FAILED", "CENSUS COMPLETE — first bounded scan failed safely");
                return;
            }
            h25.postDelayed(this::captureSecond25, SECOND_SNAPSHOT_DELAY_MS);
        });
    }

    private void captureSecond25() {
        if (!running25) return;
        setStatus25("Capturing bounded ready-state census 2/2...");
        eval25(CENSUS_JS_25, out -> {
            if (!running25) return;
            censusTwo25 = sanitizeCensus25(out);
            JSONObject state = new JSONObject();
            put25(state, "first", censusOne25 == null ? new JSONObject() : censusOne25);
            put25(state, "second", censusTwo25);
            String h1 = censusOne25 == null ? "-" : censusOne25.optString("set_hash", "-");
            String h2 = censusTwo25.optString("set_hash", "-");
            put25(state, "set_stable", !"-".equals(h1) && h1.equals(h2));
            put25(state, "no_control_clicks", true);
            postBestEffort25("READY_CENSUS_2", classifyCensus25(censusTwo25), state);
            String finalClass = censusTwo25.optBoolean("success", false)
                    ? "PASS_READY_START_CENSUS_CAPTURED_NO_CLICK"
                    : "CENSUS_2_FAILED";
            finish25(finalClass, "CENSUS COMPLETE — no controls clicked. Tell ChatGPT: test finished");
        });
    }

    private String classifyCensus25(JSONObject o) {
        if (!o.optBoolean("success", false)) return o.optBoolean("budget_exceeded", false)
                ? "SCAN_BUDGET_EXCEEDED" : "CENSUS_FAILED";
        int old = o.optInt("old_resolver_matches", -1);
        int audio = o.optInt("audio_like_count", -1);
        if (old == 1) return "OLD_RESOLVER_UNIQUE";
        if (old > 1) return "OLD_RESOLVER_AMBIGUOUS";
        if (audio == 1) return "ONE_EXTENDED_AUDIO_LIKE";
        if (audio > 1) return "MULTIPLE_EXTENDED_AUDIO_LIKE";
        return "NO_AUDIO_LIKE_MATCH";
    }

    private JSONObject safeProbe25(JSONObject src) {
        JSONObject o = new JSONObject();
        put25(o, "success", src.optBoolean("success", false));
        put25(o, "prompt_visible", src.optBoolean("prompt_visible", false));
        put25(o, "root_found", src.optBoolean("root_found", false));
        put25(o, "root_tag", src.optString("root_tag", "-"));
        put25(o, "root_role", src.optString("root_role", "-"));
        put25(o, "root_test_id", src.optString("root_test_id", "-"));
        put25(o, "visible_control_count", src.optInt("visible_control_count", -1));
        put25(o, "reason", src.optString("reason", "-"));
        put25(o, "composer_text_read", false);
        put25(o, "chat_text_read", false);
        return o;
    }

    private JSONObject sanitizeCensus25(JSONObject src) {
        JSONObject o = new JSONObject();
        put25(o, "success", src.optBoolean("success", false));
        put25(o, "reason", src.optString("reason", "-"));
        put25(o, "root_tag", src.optString("root_tag", "-"));
        put25(o, "root_role", src.optString("root_role", "-"));
        put25(o, "root_test_id", src.optString("root_test_id", "-"));
        put25(o, "root_control_count", src.optInt("root_control_count", -1));
        put25(o, "control_count", src.optInt("control_count", -1));
        put25(o, "old_resolver_matches", src.optInt("old_resolver_matches", -1));
        put25(o, "audio_like_count", src.optInt("audio_like_count", -1));
        put25(o, "truncated", src.optBoolean("truncated", false));
        put25(o, "budget_exceeded", src.optBoolean("budget_exceeded", false));
        put25(o, "scan_elapsed_ms", src.optLong("scan_elapsed_ms", -1));
        put25(o, "set_hash", src.optString("set_hash", "-"));
        if (src.has("controls")) put25(o, "controls", src.optJSONArray("controls"));
        put25(o, "max_controls", 32);
        put25(o, "max_scan_ms", 180);
        put25(o, "no_control_clicks", true);
        put25(o, "composer_text_read", false);
        put25(o, "chat_text_read", false);
        put25(o, "raw_html_returned", false);
        return o;
    }

    private void eval25(String js, JsonDone25 cb) {
        if (web25 == null) {
            JSONObject o = new JSONObject(); put25(o, "success", false); put25(o, "reason", "WebViewMissing"); cb.done(o); return;
        }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!once.compareAndSet(false, true)) return;
            JSONObject o = new JSONObject(); put25(o, "success", false); put25(o, "reason", "EVAL_CALLBACK_TIMEOUT"); cb.done(o);
        };
        h25.postDelayed(timeout, EVAL_TIMEOUT_MS);
        try {
            web25.evaluateJavascript(js, value -> {
                if (!once.compareAndSet(false, true)) return;
                h25.removeCallbacks(timeout);
                cb.done(decode25(value));
            });
        } catch (Exception e) {
            if (once.compareAndSet(false, true)) {
                h25.removeCallbacks(timeout);
                JSONObject o = new JSONObject(); put25(o, "success", false); put25(o, "reason", "EVAL_THROW_" + e.getClass().getSimpleName()); cb.done(o);
            }
        }
    }

    private interface BoolDone25 { void done(boolean ok); }

    private void uploadRequired25(JSONObject payload, BoolDone25 done) {
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> { if (once.compareAndSet(false, true)) done.done(false); };
        h25.postDelayed(timeout, 7500L);
        new Thread(() -> {
            boolean ok = uploadJson25(payload, NET_TIMEOUT_MS + 900);
            runOnUiThread(() -> {
                if (!once.compareAndSet(false, true)) return;
                h25.removeCallbacks(timeout);
                done.done(ok);
            });
        }, "cp25-preflight").start();
    }

    private void postBestEffort25(String phase, String classification, JSONObject state) {
        int seq = ++seq25;
        JSONObject p = payload25(phase, classification, state);
        put25(p, "seq", seq);
        new Thread(() -> uploadJson25(p, NET_TIMEOUT_MS), "cp25-telemetry-" + seq).start();
    }

    private JSONObject payload25(String phase, String classification, JSONObject state) {
        JSONObject p = new JSONObject();
        put25(p, "kind", "TEST_PHASE");
        put25(p, "schema_version", SCHEMA);
        put25(p, "scenario_id", SCENARIO);
        put25(p, "scenario_version", 1);
        put25(p, "test_id", testId25);
        put25(p, "seq", seq25);
        put25(p, "phase", phase);
        put25(p, "classification", classification);
        put25(p, "app_version", appVersion25());
        put25(p, "source_ref", TelemetryConfigV25.SOURCE_REF);
        put25(p, "collector_id", TelemetryConfigV25.COLLECTOR_ID);
        put25(p, "elapsed_ms", started25 == 0L ? 0L : System.currentTimeMillis() - started25);
        put25(p, "timestamp_epoch_ms", System.currentTimeMillis());
        put25(p, "privacy", "composer_chrome_allowlist_no_chat_or_composer_text_no_clicks");
        put25(p, "state", state == null ? new JSONObject() : state);
        return p;
    }

    private boolean uploadJson25(JSONObject payload, int timeoutMs) {
        if (!TelemetryConfigV25.isConfigured()) return false;
        HttpURLConnection conn = null;
        try {
            URL url = new URL(TelemetryConfigV25.WEBHOOK_URL);
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setConnectTimeout(timeoutMs);
            conn.setReadTimeout(timeoutMs);
            conn.setDoOutput(true);
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            conn.setRequestProperty("Accept", "text/plain, application/json");
            conn.setRequestProperty("X-Probe-Schema", SCHEMA);
            byte[] body = payload.toString().getBytes(StandardCharsets.UTF_8);
            conn.setFixedLengthStreamingMode(body.length);
            try (OutputStream os = conn.getOutputStream()) { os.write(body); }
            int code = conn.getResponseCode();
            return code >= 200 && code < 300;
        } catch (Exception ignored) {
            return false;
        } finally {
            if (conn != null) conn.disconnect();
        }
    }

    private void finish25(String classification, String message) {
        if (!running25) return;
        JSONObject state = new JSONObject();
        put25(state, "final_classification", classification);
        put25(state, "no_control_clicks", true);
        put25(state, "first_set_hash", censusOne25 == null ? "-" : censusOne25.optString("set_hash", "-"));
        put25(state, "second_set_hash", censusTwo25 == null ? "-" : censusTwo25.optString("set_hash", "-"));
        postBestEffort25("FINAL", classification, state);
        saveLocal25(classification);
        running25 = false;
        if (run25 != null) { run25.setEnabled(true); run25.setText("RUN START CENSUS AGAIN"); }
        setStatus25(message);
    }

    private void saveLocal25(String classification) {
        try {
            JSONObject o = new JSONObject();
            put25(o, "schema_version", SCHEMA);
            put25(o, "scenario_id", SCENARIO);
            put25(o, "test_id", testId25);
            put25(o, "classification", classification);
            put25(o, "source_ref", TelemetryConfigV25.SOURCE_REF);
            put25(o, "first", censusOne25 == null ? new JSONObject() : censusOne25);
            put25(o, "second", censusTwo25 == null ? new JSONObject() : censusTwo25);
            put25(o, "no_control_clicks", true);
            put25(o, "composer_text_read", false);
            put25(o, "chat_text_read", false);
            String name = "chatgpt-webview-v25-ready-census-" + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".json";
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            cv.put(MediaStore.MediaColumns.MIME_TYPE, "application/json");
            cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
            Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (uri == null) return;
            try (OutputStream os = getContentResolver().openOutputStream(uri)) {
                if (os != null) os.write(o.toString(2).getBytes(StandardCharsets.UTF_8));
            }
        } catch (Exception ignored) {}
    }

    private TextView inheritedStatus25() {
        try {
            Field f = findField25("status23");
            Object v = f == null ? null : f.get(this);
            return v instanceof TextView ? (TextView) v : null;
        } catch (Exception e) { return null; }
    }

    private Field findField25(String name) {
        Class<?> c = getClass();
        while (c != null) {
            try { Field f = c.getDeclaredField(name); f.setAccessible(true); return f; }
            catch (Exception ignored) { c = c.getSuperclass(); }
        }
        return null;
    }

    private void setStatus25(String s) {
        if (status25 != null) status25.setText(s);
    }

    private WebView findWeb25(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb25(g.getChildAt(i)); if (w != null) return w;
            }
        }
        return null;
    }

    private Button findButton25(View v, String exact) {
        if (v instanceof Button && exact.equals(String.valueOf(((Button) v).getText()))) return (Button) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                Button b = findButton25(g.getChildAt(i), exact); if (b != null) return b;
            }
        }
        return null;
    }

    private JSONObject decode25(String value) {
        try {
            Object d = new JSONTokener(value == null ? "null" : value).nextValue();
            String text = d instanceof String ? (String) d : String.valueOf(d);
            return new JSONObject(text);
        } catch (Exception e) {
            JSONObject o = new JSONObject(); put25(o, "success", false); put25(o, "reason", "JSON_DECODE_" + e.getClass().getSimpleName()); return o;
        }
    }

    private String appVersion25() {
        try {
            PackageInfo pi = getPackageManager().getPackageInfo(getPackageName(), 0);
            return pi.versionName + "(" + pi.getLongVersionCode() + ")";
        } catch (Exception e) { return "unknown"; }
    }

    private void put25(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) {}
    }

    @Override protected void onDestroy() {
        h25.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private static final String READY_PROBE_JS_25 =
            "(function(){try{" +
            "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};" +
            "const A=(e,n)=>String(e&&e.getAttribute?e.getAttribute(n)||'':'').slice(0,96);" +
            "const p=[...document.querySelectorAll('#prompt-textarea,textarea,[contenteditable=true]')].filter(V).pop()||null;" +
            "if(!p)return JSON.stringify({success:true,prompt_visible:false,root_found:false,reason:'PROMPT_NOT_VISIBLE'});" +
            "let root=p.closest('form');if(!root){let x=p.parentElement;for(let i=0;i<6&&x;i++,x=x.parentElement){const n=x.querySelectorAll('button,[role=button],[aria-label],[data-testid]').length;if(n>=2&&n<=48){root=x;break;}}}" +
            "if(!root)return JSON.stringify({success:true,prompt_visible:true,root_found:false,reason:'COMPOSER_ROOT_NOT_FOUND'});" +
            "const n=[...root.querySelectorAll('button,[role=button],[aria-label],[data-testid]')].filter(V).length;" +
            "return JSON.stringify({success:true,prompt_visible:true,root_found:true,root_tag:String(root.tagName||'').toLowerCase(),root_role:A(root,'role'),root_test_id:A(root,'data-testid'),visible_control_count:n,reason:'READY'});" +
            "}catch(e){return JSON.stringify({success:false,prompt_visible:false,root_found:false,reason:String(e&&e.name||'ERR')});}})();";

    /**
     * Bounded synchronous census. It never calls click(), never reads prompt value/innerText,
     * and never reads message/chat content. Only allowlisted composer-chrome metadata is returned.
     */
    private static final String CENSUS_JS_25 =
            "(function(){try{" +
            "const T0=performance.now(),MAXMS=180,MAXC=32;" +
            "const N=s=>String(s==null?'':s).replace(/\\s+/g,' ').trim();const T=(s,n)=>N(s).slice(0,n);" +
            "const A=(e,n,m=96)=>T(e&&e.getAttribute?e.getAttribute(n):'',m);" +
            "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};" +
            "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};" +
            "const p=[...document.querySelectorAll('#prompt-textarea,textarea,[contenteditable=true]')].filter(V).pop()||null;if(!p)return JSON.stringify({success:false,reason:'PROMPT_NOT_VISIBLE',budget_exceeded:false});" +
            "let root=p.closest('form');if(!root){let x=p.parentElement;for(let i=0;i<6&&x;i++,x=x.parentElement){const n=x.querySelectorAll('button,[role=button],[aria-label],[data-testid]').length;if(n>=2&&n<=48){root=x;break;}}}if(!root)return JSON.stringify({success:false,reason:'COMPOSER_ROOT_NOT_FOUND',budget_exceeded:false});" +
            "const all=[...root.querySelectorAll('button,[role=button],[aria-label],[data-testid]')].filter(e=>V(e)&&e!==p&&!e.contains(p)&&!p.contains(e));const out=[];let old=0,audio=0,budget=false;" +
            "for(let i=0;i<all.length;i++){if(performance.now()-T0>MAXMS){budget=true;break;}const e=all[i];if(out.length>=MAXC)break;" +
            "const aria=A(e,'aria-label'),title=A(e,'title'),tid=A(e,'data-testid'),name=A(e,'name'),type=A(e,'type'),role=A(e,'role'),state=A(e,'data-state'),slot=A(e,'data-slot'),pressed=A(e,'aria-pressed'),expanded=A(e,'aria-expanded'),shortcut=A(e,'aria-keyshortcuts',64);" +
            "let own='';for(const n of e.childNodes){if(n&&n.nodeType===3)own+=String(n.nodeValue||'')+' ';}own=T(own,48);" +
            "const svg=e.querySelector('svg');const svgTitle=svg?T((svg.querySelector('title')||{}).textContent||'',48):'';const svgAria=svg?A(svg,'aria-label',64):'';const svgIcon=svg?A(svg,'data-icon',64):'';const vb=svg?A(svg,'viewBox',64):'';" +
            "let pathCount=0,pathSig='';if(svg){const ps=[...svg.querySelectorAll('path')].slice(0,12);pathCount=ps.length;for(const q of ps)pathSig+=A(q,'d',512)+'|';}" +
            "const parent=e.parentElement;const par={tag:parent?String(parent.tagName||'').toLowerCase():'',role:A(parent,'role'),test_id:A(parent,'data-testid'),slot:A(parent,'data-slot')};" +
            "const sib=parent?[...parent.children].filter(x=>V(x)&&(x.matches&&x.matches('button,[role=button],[aria-label],[data-testid]'))):[];const sibIndex=sib.indexOf(e);" +
            "const words=(aria+' '+title+' '+tid+' '+name+' '+own+' '+svgTitle+' '+svgAria+' '+svgIcon).toLowerCase();" +
            "const oldLike=/microphone|dictat|voice input|record audio|record message/.test(words);if(oldLike)old++;" +
            "const extAudio=oldLike||/voice typing|speech to text|speech input|talk to type|audio input|recording|mic\\b/.test(words);if(extAudio)audio++;" +
            "let hint='UNKNOWN';if(oldLike)hint='OLD_DICTATION_LIKE';else if(extAudio)hint='EXTENDED_AUDIO_LIKE';else if(/voice mode|advanced voice|start voice|open voice/.test(words))hint='VOICE_MODE_LIKE';else if(/send|submit/.test(words))hint='SEND_LIKE';else if(/attach|upload|add file|add photos|plus/.test(words))hint='ATTACHMENT_LIKE';else if(/tool|search|browse|reason/.test(words))hint='TOOLS_LIKE';" +
            "const sig=[aria,title,tid,name,type,role,state,slot,pressed,expanded,shortcut,own,svgTitle,svgAria,svgIcon,vb,String(pathCount),H(pathSig),par.tag,par.role,par.test_id,par.slot,String(sibIndex),String(sib.length)].join('|');" +
            "out.push({index:out.length,tag:String(e.tagName||'').toLowerCase(),role:role,aria_label:aria,title:title,test_id:tid,name:name,type:type,data_state:state,data_slot:slot,aria_pressed:pressed,aria_expanded:expanded,aria_keyshortcuts:shortcut,disabled:!!e.disabled,own_text_hint:own,svg_title:svgTitle,svg_aria_label:svgAria,svg_data_icon:svgIcon,svg_viewbox:vb,svg_path_count:pathCount,svg_path_hash:H(pathSig),semantic_hint:hint,parent:par,sibling_control_index:sibIndex,sibling_control_count:sib.length,fingerprint_hash:H(sig)});}" +
            "const setHash=H(out.map(x=>x.fingerprint_hash).join('|'));const elapsed=Math.round(performance.now()-T0);" +
            "return JSON.stringify({success:!budget,reason:budget?'SCAN_BUDGET_EXCEEDED':'OK',root_tag:String(root.tagName||'').toLowerCase(),root_role:A(root,'role'),root_test_id:A(root,'data-testid'),root_control_count:all.length,control_count:out.length,old_resolver_matches:old,audio_like_count:audio,controls:out,truncated:all.length>MAXC,budget_exceeded:budget,scan_elapsed_ms:elapsed,set_hash:setHash,no_control_clicks:true,composer_text_read:false,chat_text_read:false,raw_html_returned:false});" +
            "}catch(e){return JSON.stringify({success:false,reason:String(e&&e.name||'ERR'),budget_exceeded:false,no_control_clicks:true,composer_text_read:false,chat_text_read:false,raw_html_returned:false});}})();";
}
