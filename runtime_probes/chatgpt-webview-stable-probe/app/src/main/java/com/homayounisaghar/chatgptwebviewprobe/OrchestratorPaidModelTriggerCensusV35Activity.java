package com.homayounisaghar.chatgptwebviewprobe;

import android.content.ContentValues;
import android.net.Uri;
import android.os.Build;
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

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Stable v0.33 — paid-account model trigger census.
 *
 * Read-only diagnostic. It performs no DOM click and dispatches no ChatGPT capability.
 * It captures bounded, privacy-safe semantic feature vectors for visible controls near
 * the header/model-selection surface across several snapshots. Raw labels/text/HTML,
 * URLs/query strings, credentials, cookies and tokens are never uploaded.
 */
public class OrchestratorPaidModelTriggerCensusV35Activity extends OrchestratorAuthModeV34Activity {
    private static final String SCHEMA35 = "cp-v35-paid-model-trigger-census-v1";
    private static final String SCENARIO35 = "paid-model-trigger-read-only-census";
    private static final long EVAL_TIMEOUT_MS35 = 2800L;
    private static final int NET_TIMEOUT_MS35 = 3200;
    private static final int SNAPSHOT_COUNT35 = 4;

    private final Handler h35 = new Handler(Looper.getMainLooper());
    private WebView web35;
    private TextView status35;
    private Button run35;
    private boolean running35 = false;
    private boolean telemetryHealthy35 = false;
    private String testId35 = "-";
    private int seq35 = 0;
    private int snapshotsOk35 = 0;
    private int snapshotsComplete35 = 0;
    private int maxCandidateCount35 = 0;
    private int maxVisibleControls35 = 0;
    private long startedAt35 = 0L;

    private interface JsonDone35 { void done(JSONObject o); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web35 = findWeb35(getWindow().getDecorView());
        installCompactUi35();
        setStatus35("v0.33 paid model trigger census ready — read only");
    }

    @Override protected void onDestroy() {
        h35.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private void installCompactUi35() {
        if (web35 == null) return;
        ViewParent p = web35.getParent();
        if (!(p instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) p;
        for (int i = 0; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            if (child != web35) child.setVisibility(View.GONE);
        }
        web35.setMinimumHeight(1);
        web35.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp35(8), dp35(3), dp35(8), dp35(6));

        status35 = new TextView(this);
        status35.setTextSize(11f);
        status35.setSingleLine(true);
        status35.setEllipsize(TextUtils.TruncateAt.END);
        panel.addView(status35, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));

        run35 = new Button(this);
        run35.setText("RUN READ-ONLY MODEL CENSUS");
        run35.setTextSize(13f);
        run35.setAllCaps(false);
        run35.setOnClickListener(v -> runCensus35());
        panel.addView(run35, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp35(46)));

        root.addView(panel, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void runCensus35() {
        if (running35) return;
        if (web35 == null || !isChatGpt35(web35.getUrl())) {
            setStatus35("Blocked: authenticated ChatGPT page not ready");
            return;
        }
        running35 = true;
        telemetryHealthy35 = false;
        testId35 = "cp35-" + UUID.randomUUID();
        seq35 = 0;
        snapshotsOk35 = 0;
        snapshotsComplete35 = 0;
        maxCandidateCount35 = 0;
        maxVisibleControls35 = 0;
        startedAt35 = System.currentTimeMillis();
        if (run35 != null) {
            run35.setEnabled(false);
            run35.setText("CENSUS RUNNING...");
        }
        setStatus35("Telemetry preflight...");
        telemetryPreflight35();
    }

    private void telemetryPreflight35() {
        JSONObject st = baseState35();
        put35(st, "snapshot_target", SNAPSHOT_COUNT35);
        put35(st, "collector_capacity_hint", TelemetryConfigV35.COLLECTOR_CAPACITY_HINT);
        JSONObject p = payload35("TELEMETRY_PREFLIGHT", "RUNNING", st);
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!running35 || !once.compareAndSet(false, true)) return;
            finish35("TELEMETRY_PREFLIGHT_TIMEOUT");
        };
        h35.postDelayed(timeout, 8000L);
        new Thread(() -> {
            JSONObject r = upload35(p, NET_TIMEOUT_MS35 + 900);
            runOnUiThread(() -> {
                if (!running35 || !once.compareAndSet(false, true)) return;
                h35.removeCallbacks(timeout);
                if (!r.optBoolean("success", false)) {
                    finish35("TELEMETRY_UNAVAILABLE");
                    return;
                }
                telemetryHealthy35 = true;
                phase35("RUN_STARTED", "READ_ONLY_ZERO_CLICK", baseState35());
                takeSnapshot35(0);
            });
        }, "cp35-preflight").start();
    }

    private void takeSnapshot35(int index) {
        if (!running35) return;
        if (index >= SNAPSHOT_COUNT35) {
            finish35(snapshotsOk35 == SNAPSHOT_COUNT35
                    ? "PASS_PAID_MODEL_TRIGGER_CENSUS_CAPTURED"
                    : "PARTIAL_PAID_MODEL_TRIGGER_CENSUS_CAPTURED");
            return;
        }
        setStatus35("Read-only snapshot " + (index + 1) + "/" + SNAPSHOT_COUNT35 + "...");
        eval35(snapshotJs35(index), o -> {
            JSONObject st = baseState35();
            boolean success = o.optBoolean("success", false);
            boolean complete = o.optBoolean("complete", false);
            int visible = o.optInt("visible_control_count", -1);
            int candidates = o.optInt("candidate_count", -1);
            if (success) snapshotsOk35++;
            if (complete) snapshotsComplete35++;
            if (visible > maxVisibleControls35) maxVisibleControls35 = visible;
            if (candidates > maxCandidateCount35) maxCandidateCount35 = candidates;

            put35(st, "snapshot_index", index);
            put35(st, "success", success);
            put35(st, "complete", complete);
            put35(st, "elapsed_ms", o.optInt("elapsed_ms", -1));
            put35(st, "visited_nodes", o.optInt("visited_nodes", -1));
            put35(st, "visible_control_count", visible);
            put35(st, "candidate_count", candidates);
            put35(st, "top_band_control_count", o.optInt("top_band_control_count", -1));
            put35(st, "popup_control_count", o.optInt("popup_control_count", -1));
            put35(st, "semantic_modelish_count", o.optInt("semantic_modelish_count", -1));
            put35(st, "candidate_set_hash", o.optString("candidate_set_hash", "-"));
            JSONArray c = o.optJSONArray("candidates");
            if (c != null) put35(st, "candidates", c);
            phase35("MODEL_TRIGGER_SNAPSHOT",
                    success && complete ? "CAPTURED_COMPLETE" : success ? "CAPTURED_BUDGET_LIMIT" : "UNRESOLVED",
                    st);

            long delay = index == 0 ? 650L : index == 1 ? 1150L : index == 2 ? 1800L : 0L;
            h35.postDelayed(() -> takeSnapshot35(index + 1), delay);
        });
    }

    private String snapshotJs35(int index) {
        return "(function(){try{const T0=performance.now(),MAXN=6500,MAXMS=170,MAXC=36;"
                + "const N=x=>(x||'').replace(/\\s+/g,' ').trim();const L=x=>N(x).toLowerCase();"
                + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};"
                + "const B=n=>n<=0?0:n<=8?1:n<=16?2:n<=32?3:n<=64?4:5;"
                + "let visited=0,complete=true;const all=[];"
                + "const roots=[document];for(const e of document.querySelectorAll('*')){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(e.shadowRoot)roots.push(e.shadowRoot);if(roots.length>=24)break;}"
                + "for(const root of roots){if(performance.now()-T0>MAXMS){complete=false;break;}for(const e of root.querySelectorAll('button,[role=button],a')){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(V(e))all.push(e);}}"
                + "const seen=new Set(),uniq=[];for(const e of all){if(!seen.has(e)){seen.add(e);uniq.push(e);}}"
                + "let topCount=0,popupCount=0,modelishCount=0;const cand=[];"
                + "for(const e of uniq){const r=e.getBoundingClientRect();const aria=N(e.getAttribute('aria-label'));const txt=N(e.innerText||e.textContent||'');const title=N(e.getAttribute('title'));const acc=N(aria||title||txt);const la=L(acc);"
                + "const popup=N(e.getAttribute('aria-haspopup'));const expanded=N(e.getAttribute('aria-expanded'));const ds=N(e.getAttribute('data-state'));const testid=N(e.getAttribute('data-testid'));"
                + "const top=r.top<Math.max(210,innerHeight*0.30);const hasPopup=popup!==''&&popup!=='false';const model=/(model|gpt|chatgpt|thinking|instant|auto|pro|^o[0-9])/i.test(la);"
                + "if(top)topCount++;if(hasPopup)popupCount++;if(model)modelishCount++;"
                + "const keep=top||hasPopup||model||expanded!==''||ds!=='';if(!keep)continue;"
                + "const q={tag:(e.tagName||'').toLowerCase(),role:L(e.getAttribute('role')),top_band:top,headerish:!!e.closest('header,nav'),has_popup:hasPopup,popup_hash:popup?H(L(popup)):'-',has_expanded:expanded!=='',expanded_true:L(expanded)==='true',has_controls:!!e.getAttribute('aria-controls'),has_data_state:ds!=='',data_state_open:L(ds)==='open',disabled:!!(e.disabled||e.getAttribute('aria-disabled')==='true'),has_svg:!!e.querySelector('svg'),text_len_bucket:B(txt.length),aria_len_bucket:B(aria.length),title_len_bucket:B(title.length),sem_model:la.includes('model'),sem_gpt:la.includes('gpt'),sem_chatgpt:la.includes('chatgpt'),sem_auto:/(^|\\s)auto($|\\s)/.test(la),sem_instant:la.includes('instant'),sem_thinking:la.includes('thinking'),sem_pro:/(^|\\s)pro($|\\s)/.test(la),sem_o_series:/^o[0-9]/.test(la),acc_hash:acc?H(L(acc)):'-',testid_hash:testid?H(testid):'-',x_bucket:Math.max(0,Math.min(4,Math.floor((r.left+r.width/2)/Math.max(1,innerWidth)*5))),y_bucket:Math.max(0,Math.min(4,Math.floor((r.top+r.height/2)/Math.max(1,innerHeight)*5))),w_bucket:B(Math.round(r.width/8)),h_bucket:B(Math.round(r.height/8))};"
                + "const fp=[q.tag,q.role,q.top_band,q.headerish,q.has_popup,q.popup_hash,q.has_expanded,q.expanded_true,q.has_controls,q.has_data_state,q.data_state_open,q.disabled,q.has_svg,q.text_len_bucket,q.aria_len_bucket,q.title_len_bucket,q.sem_model,q.sem_gpt,q.sem_chatgpt,q.sem_auto,q.sem_instant,q.sem_thinking,q.sem_pro,q.sem_o_series,q.acc_hash,q.testid_hash,q.x_bucket,q.y_bucket,q.w_bucket,q.h_bucket].join('|');q.fp=H(fp);cand.push(q);if(cand.length>=MAXC)break;}"
                + "cand.sort((a,b)=>a.y_bucket-b.y_bucket||a.x_bucket-b.x_bucket||a.fp.localeCompare(b.fp));const setHash=H(cand.map(x=>x.fp).join(','));"
                + "return JSON.stringify({success:true,complete:complete,snapshot_index:" + index + ",elapsed_ms:Math.round(performance.now()-T0),visited_nodes:visited,visible_control_count:uniq.length,candidate_count:cand.length,top_band_control_count:topCount,popup_control_count:popupCount,semantic_modelish_count:modelishCount,candidate_set_hash:setHash,candidates:cand});"
                + "}catch(e){return JSON.stringify({success:false,complete:false,error_class:'SCAN_EXCEPTION',candidate_count:-1,visible_control_count:-1});}})();";
    }

    private void eval35(String js, JsonDone35 done) {
        if (web35 == null) { done.done(new JSONObject()); return; }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (once.compareAndSet(false, true)) {
                JSONObject o = new JSONObject(); put35(o, "success", false); put35(o, "complete", false); put35(o, "error_class", "EVAL_TIMEOUT"); done.done(o);
            }
        };
        h35.postDelayed(timeout, EVAL_TIMEOUT_MS35);
        web35.evaluateJavascript(js, value -> {
            if (!once.compareAndSet(false, true)) return;
            h35.removeCallbacks(timeout);
            try {
                String s = value == null ? "" : value;
                Object outer = new JSONTokener(s).nextValue();
                if (outer instanceof String) s = (String) outer;
                done.done(new JSONObject(s));
            } catch (Exception e) {
                JSONObject o = new JSONObject(); put35(o, "success", false); put35(o, "complete", false); put35(o, "error_class", "PARSE_ERROR"); done.done(o);
            }
        });
    }

    private void finish35(String classification) {
        if (!running35) return;
        JSONObject st = baseState35();
        put35(st, "snapshots_ok", snapshotsOk35);
        put35(st, "snapshots_complete", snapshotsComplete35);
        put35(st, "max_candidate_count", maxCandidateCount35);
        put35(st, "max_visible_control_count", maxVisibleControls35);
        put35(st, "runtime_ms", System.currentTimeMillis() - startedAt35);
        put35(st, "dom_clicks", 0);
        put35(st, "capability_dispatches", 0);
        put35(st, "raw_text_uploaded", false);
        put35(st, "raw_html_uploaded", false);
        put35(st, "cookies_tokens_accessed", false);
        JSONObject finalPayload = payload35("FINAL", classification, st);
        saveLocal35(finalPayload);
        if (telemetryHealthy35) {
            new Thread(() -> upload35(finalPayload, NET_TIMEOUT_MS35), "cp35-final").start();
        }
        running35 = false;
        setStatus35(classification);
        if (run35 != null) {
            run35.setEnabled(true);
            run35.setText("RUN READ-ONLY MODEL CENSUS");
        }
    }

    private void phase35(String phase, String classification, JSONObject state) {
        if (!telemetryHealthy35 && !"RUN_STARTED".equals(phase)) return;
        JSONObject p = payload35(phase, classification, state);
        new Thread(() -> upload35(p, NET_TIMEOUT_MS35), "cp35-phase").start();
    }

    private JSONObject payload35(String phase, String classification, JSONObject state) {
        JSONObject p = new JSONObject();
        put35(p, "schema_version", SCHEMA35);
        put35(p, "scenario_id", SCENARIO35);
        put35(p, "source_ref", TelemetryConfigV35.SOURCE_REF);
        put35(p, "test_id", testId35);
        put35(p, "seq", seq35++);
        put35(p, "phase", phase);
        put35(p, "classification", classification);
        put35(p, "timestamp_epoch_ms", System.currentTimeMillis());
        put35(p, "state", state == null ? new JSONObject() : state);
        return p;
    }

    private JSONObject baseState35() {
        JSONObject st = new JSONObject();
        put35(st, "read_only", true);
        put35(st, "dom_clicks", 0);
        put35(st, "capability_dispatches", 0);
        put35(st, "raw_text_uploaded", false);
        put35(st, "raw_html_uploaded", false);
        put35(st, "raw_url_query_uploaded", false);
        put35(st, "cookies_tokens_accessed", false);
        return st;
    }

    private JSONObject upload35(JSONObject p, int timeoutMs) {
        JSONObject r = new JSONObject();
        if (!TelemetryConfigV35.isConfigured()) { put35(r, "success", false); return r; }
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(TelemetryConfigV35.WEBHOOK_URL).openConnection();
            c.setConnectTimeout(timeoutMs);
            c.setReadTimeout(timeoutMs);
            c.setRequestMethod("POST");
            c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/json");
            byte[] b = p.toString().getBytes(StandardCharsets.UTF_8);
            try (OutputStream os = c.getOutputStream()) { os.write(b); os.flush(); }
            int code = c.getResponseCode();
            put35(r, "success", code >= 200 && code < 300);
            put35(r, "code", code);
        } catch (Exception e) {
            put35(r, "success", false);
        } finally {
            if (c != null) c.disconnect();
        }
        return r;
    }

    private void saveLocal35(JSONObject p) {
        if (Build.VERSION.SDK_INT < 29) return;
        try {
            ContentValues v = new ContentValues();
            v.put(MediaStore.Downloads.DISPLAY_NAME, "cp35-" + testId35 + ".json");
            v.put(MediaStore.Downloads.MIME_TYPE, "application/json");
            v.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v);
            if (u != null) {
                try (OutputStream os = getContentResolver().openOutputStream(u)) {
                    if (os != null) os.write(p.toString(2).getBytes(StandardCharsets.UTF_8));
                }
            }
        } catch (Exception ignored) { }
    }

    private boolean isChatGpt35(String raw) {
        try {
            Uri u = Uri.parse(raw == null ? "" : raw);
            String h = u.getHost() == null ? "" : u.getHost().toLowerCase();
            return h.equals("chatgpt.com") || h.endsWith(".chatgpt.com");
        } catch (Exception e) { return false; }
    }

    private void setStatus35(String s) {
        if (status35 != null) status35.setText(s == null ? "" : s);
    }

    private WebView findWeb35(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb35(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }

    private static void put35(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) { }
    }

    private int dp35(int x) {
        return Math.max(1, Math.round(x * getResources().getDisplayMetrics().density));
    }
}
