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
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Stable v0.26: exact ready-state Dictation Start gate on top of the proven v0.24 lifecycle.
 *
 * v0.25 real-device census proved a stable, unique ready control:
 *   button[aria-label="Start dictation"]
 * in the composer form, with the same control-set hash across two snapshots.
 *
 * v0.24 had attempted its first D START before that control was present. v0.26 therefore:
 * 1) waits for two consecutive exact ready observations before starting the autonomous run;
 * 2) retargets D START to a bounded exact readiness gate immediately before invoking the
 *    inherited v0.16 DICTATION_START capability;
 * 3) preserves the inherited durable CLAIM / MicLease / exactly-one semantic click path;
 * 4) never directly clicks the DOM control from this compatibility layer;
 * 5) leaves active Submit/Cancel, Send receipt, language diagnostics and recovery unchanged.
 */
public class OrchestratorAutonomousV26Activity extends OrchestratorAutonomousV24Activity {
    private static final String SCHEMA26 = "cp-v26-ready-start-gate-v1";
    private static final String SCENARIO26 = "dictation-one-tap-ready-gated-v26";
    private static final long RUN_READY_TIMEOUT_MS = 9000L;
    private static final long START_READY_TIMEOUT_MS = 2500L;
    private static final long EVAL_TIMEOUT_MS = 2600L;
    private static final int NET_TIMEOUT_MS = 2800;

    private final Handler h26 = new Handler(Looper.getMainLooper());
    private WebView web26;
    private Button run26;
    private boolean runGatePending26 = false;
    private boolean startGatePending26 = false;
    private String gateId26 = "-";
    private int seq26 = 0;

    private interface JsonDone26 { void done(JSONObject o); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web26 = findWeb26(getWindow().getDecorView());
        run26 = findButton26(getWindow().getDecorView(), "RUN FULL TEST");
        retargetStart26(getWindow().getDecorView());
        if (run26 != null) run26.setOnClickListener(v -> onRunPressed26());
        setStatus26("v0.26 ready — exact Start dictation gate armed");
    }

    private void onRunPressed26() {
        if (runGatePending26 || boolField26("running23")) return;
        runGatePending26 = true;
        gateId26 = "cp26-gate-" + UUID.randomUUID();
        seq26 = 0;
        if (run26 != null) {
            run26.setEnabled(false);
            run26.setText("WAITING FOR START CONTROL...");
        }
        setStatus26("Waiting for stable exact Start dictation control...");
        post26("RUN_GATE_STARTED", "WAITING_EXACT_START", state26(null));
        waitRunReady26(System.currentTimeMillis() + RUN_READY_TIMEOUT_MS, 0);
    }

    private void waitRunReady26(long deadline, int consecutive) {
        if (!runGatePending26) return;
        readExactStart26(o -> {
            if (!runGatePending26) return;
            boolean unique = exactReady26(o);
            if (unique) {
                int next = consecutive + 1;
                if (next >= 2) {
                    runGatePending26 = false;
                    JSONObject s = state26(o);
                    put26(s, "consecutive_exact_ready", next);
                    post26("RUN_GATE_READY", "PASS_TWO_CONSECUTIVE_EXACT_READY", s);
                    setStatus26("Start control ready. Launching full lifecycle...");
                    invokeRunFull23_26();
                    return;
                }
                h26.postDelayed(() -> waitRunReady26(deadline, next), 250L);
                return;
            }
            if (System.currentTimeMillis() >= deadline) {
                runGatePending26 = false;
                JSONObject s = state26(o);
                put26(s, "consecutive_exact_ready", consecutive);
                post26("RUN_GATE_TIMEOUT", "EXACT_START_NOT_READY", s);
                if (run26 != null) {
                    run26.setEnabled(true);
                    run26.setText("RUN FULL TEST");
                }
                setStatus26("TEST NOT STARTED — exact Start dictation control not ready");
                return;
            }
            h26.postDelayed(() -> waitRunReady26(deadline, 0), 300L);
        });
    }

    private void retargetStart26(View v) {
        if (v instanceof Button) {
            Button b = (Button) v;
            if ("D START".equals(String.valueOf(b.getText()))) {
                b.setOnClickListener(x -> onStartButton26());
            }
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) retargetStart26(g.getChildAt(i));
        }
    }

    private void onStartButton26() {
        if (startGatePending26) return;
        startGatePending26 = true;
        post26("START_GATE_REQUEST", "WAITING_EXACT_START", state26(null));
        waitStartReady26(System.currentTimeMillis() + START_READY_TIMEOUT_MS);
    }

    private void waitStartReady26(long deadline) {
        if (!startGatePending26) return;
        readExactStart26(o -> {
            if (!startGatePending26) return;
            if (exactReady26(o)) {
                startGatePending26 = false;
                JSONObject s = state26(o);
                put26(s, "dom_clicked_by_v26", false);
                put26(s, "dispatch_basis", "UNIQUE_VISIBLE_BUTTON_ARIA_LABEL_START_DICTATION_IN_COMPOSER_FORM");
                post26("START_GATE_READY", "PASS_EXACT_START_READY_DISPATCH_PARENT", s);
                invokeParentStart26();
                return;
            }
            if (System.currentTimeMillis() >= deadline) {
                startGatePending26 = false;
                JSONObject s = state26(o);
                put26(s, "dom_clicked_by_v26", false);
                post26("START_GATE_TIMEOUT", "ABORTED_NO_SIDE_EFFECT_EXACT_START_NOT_READY", s);
                setInheritedField26("lastAction", "DICTATION_START");
                setInheritedField26("lastActionStatus", "ABORTED_V26_EXACT_START_NOT_READY");
                return;
            }
            h26.postDelayed(() -> waitStartReady26(deadline), 180L);
        });
    }

    private boolean exactReady26(JSONObject o) {
        return o != null
                && o.optBoolean("success", false)
                && o.optBoolean("prompt_visible", false)
                && o.optBoolean("root_found", false)
                && o.optInt("matches", -1) == 1
                && o.optBoolean("enabled", false)
                && "Start dictation".equals(o.optString("aria_label", ""));
    }

    private void readExactStart26(JsonDone26 done) {
        if (web26 == null) {
            JSONObject o = new JSONObject();
            put26(o, "success", false);
            put26(o, "reason", "WebViewMissing");
            done.done(o);
            return;
        }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!once.compareAndSet(false, true)) return;
            JSONObject o = new JSONObject();
            put26(o, "success", false);
            put26(o, "reason", "EVAL_CALLBACK_TIMEOUT");
            done.done(o);
        };
        h26.postDelayed(timeout, EVAL_TIMEOUT_MS);
        try {
            web26.evaluateJavascript(EXACT_READY_JS_26, value -> {
                if (!once.compareAndSet(false, true)) return;
                h26.removeCallbacks(timeout);
                done.done(decode26(value));
            });
        } catch (Exception e) {
            if (once.compareAndSet(false, true)) {
                h26.removeCallbacks(timeout);
                JSONObject o = new JSONObject();
                put26(o, "success", false);
                put26(o, "reason", "EVAL_THROW_" + e.getClass().getSimpleName());
                done.done(o);
            }
        }
    }

    private void invokeRunFull23_26() {
        try {
            Method m = OrchestratorAutonomousV23Activity.class.getDeclaredMethod("runFullTest23");
            m.setAccessible(true);
            m.invoke(this);
        } catch (Exception e) {
            if (run26 != null) {
                run26.setEnabled(true);
                run26.setText("RUN FULL TEST");
            }
            JSONObject s = state26(null);
            put26(s, "reason", "RUN_INVOKE_" + e.getClass().getSimpleName());
            post26("RUN_GATE_INVOKE_FAILED", "FAILED_NO_SIDE_EFFECT", s);
            setStatus26("TEST NOT STARTED — v0.23 harness invocation failed");
        }
    }

    private void invokeParentStart26() {
        try {
            Method m = OrchestratorFoundationV16Activity.class.getDeclaredMethod("dispatch", String.class);
            m.setAccessible(true);
            m.invoke(this, "DICTATION_START");
        } catch (Exception e) {
            JSONObject s = state26(null);
            put26(s, "reason", "PARENT_START_INVOKE_" + e.getClass().getSimpleName());
            put26(s, "dom_clicked_by_v26", false);
            post26("START_PARENT_INVOKE_FAILED", "FAILED_NO_SIDE_EFFECT", s);
            setInheritedField26("lastAction", "DICTATION_START");
            setInheritedField26("lastActionStatus", "ABORTED_V26_PARENT_INVOKE_FAILED");
        }
    }

    private JSONObject state26(JSONObject ready) {
        JSONObject s = new JSONObject();
        put26(s, "exact_contract", "button[aria-label=Start dictation] within composer form");
        put26(s, "v25_fingerprint", "ccd4005b");
        put26(s, "v25_set_hash", "5170cd41");
        put26(s, "no_direct_dom_click", true);
        put26(s, "parent_claim_click_path_preserved", true);
        put26(s, "test_id_parent", stringField26("testId23"));
        if (ready != null) {
            put26(s, "probe_success", ready.optBoolean("success", false));
            put26(s, "prompt_visible", ready.optBoolean("prompt_visible", false));
            put26(s, "root_found", ready.optBoolean("root_found", false));
            put26(s, "matches", ready.optInt("matches", -1));
            put26(s, "enabled", ready.optBoolean("enabled", false));
            put26(s, "aria_label", ready.optString("aria_label", "-"));
            put26(s, "root_tag", ready.optString("root_tag", "-"));
            put26(s, "reason", ready.optString("reason", "-"));
        }
        return s;
    }

    private void post26(String phase, String classification, JSONObject state) {
        if (!TelemetryConfigV26.isConfigured()) return;
        JSONObject p = new JSONObject();
        put26(p, "kind", "TEST_PHASE");
        put26(p, "schema_version", SCHEMA26);
        put26(p, "scenario_id", SCENARIO26);
        put26(p, "test_id", parentOrGateTestId26());
        put26(p, "seq", ++seq26);
        put26(p, "phase", phase);
        put26(p, "classification", classification);
        put26(p, "app_version", appVersion26());
        put26(p, "source_ref", TelemetryConfigV26.SOURCE_REF);
        put26(p, "collector_id", TelemetryConfigV26.COLLECTOR_ID);
        put26(p, "privacy", "exact_ready_control_metadata_and_receipts_only_no_chat_or_composer_text");
        put26(p, "state", state == null ? new JSONObject() : state);
        new Thread(() -> upload26(p), "cp26-telemetry-" + seq26).start();
    }

    private String parentOrGateTestId26() {
        String parent = stringField26("testId23");
        if (parent != null && parent.startsWith("cp23-")) return parent;
        return gateId26 == null ? "-" : gateId26;
    }

    private void upload26(JSONObject payload) {
        HttpURLConnection c = null;
        try {
            URL u = new URL(TelemetryConfigV26.WEBHOOK_URL);
            c = (HttpURLConnection) u.openConnection();
            c.setRequestMethod("POST");
            c.setConnectTimeout(NET_TIMEOUT_MS);
            c.setReadTimeout(NET_TIMEOUT_MS);
            c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            byte[] b = payload.toString().getBytes(StandardCharsets.UTF_8);
            c.setFixedLengthStreamingMode(b.length);
            try (OutputStream os = c.getOutputStream()) { os.write(b); }
            c.getResponseCode();
        } catch (Exception ignored) {
        } finally {
            if (c != null) c.disconnect();
        }
    }

    private String appVersion26() {
        try {
            PackageInfo p = getPackageManager().getPackageInfo(getPackageName(), 0);
            long code = android.os.Build.VERSION.SDK_INT >= 28 ? p.getLongVersionCode() : p.versionCode;
            return p.versionName + "(" + code + ")";
        } catch (Exception e) {
            return "unknown";
        }
    }

    private JSONObject decode26(String value) {
        try {
            Object decoded = new JSONTokener(value == null ? "null" : value).nextValue();
            String text = decoded instanceof String ? (String) decoded : String.valueOf(decoded);
            return new JSONObject(text);
        } catch (Exception e) {
            JSONObject o = new JSONObject();
            put26(o, "success", false);
            put26(o, "reason", "PARSE_" + e.getClass().getSimpleName());
            return o;
        }
    }

    private WebView findWeb26(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb26(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }

    private Button findButton26(View v, String text) {
        if (v instanceof Button && text.equals(String.valueOf(((Button) v).getText()))) return (Button) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                Button b = findButton26(g.getChildAt(i), text);
                if (b != null) return b;
            }
        }
        return null;
    }

    private void setStatus26(String text) {
        try {
            Object o = objectField26("status23");
            if (o instanceof TextView) ((TextView) o).setText(text);
        } catch (Exception ignored) {}
    }

    private boolean boolField26(String name) {
        Object o = objectField26(name);
        return o instanceof Boolean && (Boolean) o;
    }

    private String stringField26(String name) {
        Object o = objectField26(name);
        return o == null ? "-" : String.valueOf(o);
    }

    private Object objectField26(String name) {
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

    private void setInheritedField26(String name, Object value) {
        Class<?> c = getClass();
        while (c != null) {
            try {
                Field f = c.getDeclaredField(name);
                f.setAccessible(true);
                f.set(this, value);
                return;
            } catch (Exception ignored) {
                c = c.getSuperclass();
            }
        }
    }

    private void put26(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) {}
    }

    private static final String EXACT_READY_JS_26 =
            "(function(){try{"
            + "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};"
            + "const ps=[...document.querySelectorAll('#prompt-textarea')].filter(V);const p=ps.length?ps[ps.length-1]:null;"
            + "if(!p)return JSON.stringify({success:true,prompt_visible:false,root_found:false,matches:0,enabled:false,aria_label:'',root_tag:'',reason:'PROMPT_NOT_VISIBLE'});"
            + "let r=p.closest('form');if(!r){let n=p;for(let i=0;i<6&&n;i++,n=n.parentElement){if(n.querySelector&&n.querySelector('button[aria-label=\\\"Start dictation\\\"]')){r=n;break;}}}"
            + "if(!r)return JSON.stringify({success:true,prompt_visible:true,root_found:false,matches:0,enabled:false,aria_label:'',root_tag:'',reason:'COMPOSER_ROOT_NOT_FOUND'});"
            + "const xs=[...r.querySelectorAll('button[aria-label=\\\"Start dictation\\\"]')].filter(V);const e=xs.length===1?xs[0]:null;"
            + "return JSON.stringify({success:true,prompt_visible:true,root_found:true,matches:xs.length,enabled:!!(e&&!e.disabled&&e.getAttribute('aria-disabled')!=='true'),aria_label:e?String(e.getAttribute('aria-label')||''):'',root_tag:String(r.tagName||'').toLowerCase(),reason:xs.length===1?'EXACT_READY':'EXACT_MATCHES_'+xs.length});"
            + "}catch(e){return JSON.stringify({success:false,prompt_visible:false,root_found:false,matches:-1,enabled:false,aria_label:'',root_tag:'',reason:String(e&&e.name||'ERR')});}})();";
}
