package com.homayounisaghar.chatgptwebviewprobe;

import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
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

import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Stable v0.35 — paid-account model radio selected-state census.
 *
 * Strictly read-only. This activity performs zero DOM clicks and zero capability
 * dispatches. It observes visible role=radio controls, selected-state attributes,
 * same-group identity, and local Light/Medium semantic booleans. Raw labels/text,
 * HTML, URL query strings, credentials, cookies and tokens are never uploaded.
 */
public class OrchestratorPaidModelRadioCensusV37Activity extends OrchestratorAuthModeV34Activity {
    private static final String SCHEMA37 = "cp-v37-paid-model-radio-census-v1";
    private static final String SCENARIO37 = "paid-model-radio-selected-state-read-only-census";
    private static final int SNAPSHOT_COUNT37 = 4;
    private static final long EVAL_TIMEOUT_MS37 = 2800L;
    private static final int NET_TIMEOUT_MS37 = 3200;

    private final Handler h37 = new Handler(Looper.getMainLooper());
    private WebView web37;
    private TextView status37;
    private Button run37;
    private boolean running37 = false;
    private boolean telemetryHealthy37 = false;
    private String testId37 = "-";
    private int seq37 = 0;
    private int snapshotsOk37 = 0;
    private int snapshotsComplete37 = 0;
    private int stableRadioSetCount37 = 0;
    private int stableSelectedSetCount37 = 0;
    private int maxRadioCount37 = 0;
    private int maxSelectedCount37 = 0;
    private String firstRadioSetHash37 = "-";
    private String firstSelectedSetHash37 = "-";
    private long startedAt37 = 0L;

    private interface JsonDone37 { void done(JSONObject o); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web37 = findWeb37(getWindow().getDecorView());
        installCompactUi37();
        setStatus37("v0.35 model radio census ready — zero click");
    }

    @Override protected void onDestroy() {
        h37.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private void installCompactUi37() {
        if (web37 == null) return;
        ViewParent p = web37.getParent();
        if (!(p instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) p;
        for (int i = 0; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            if (child != web37) child.setVisibility(View.GONE);
        }
        web37.setMinimumHeight(1);
        web37.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp37(8), dp37(3), dp37(8), dp37(6));

        status37 = new TextView(this);
        status37.setTextSize(11f);
        status37.setSingleLine(true);
        status37.setEllipsize(TextUtils.TruncateAt.END);
        panel.addView(status37, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));

        run37 = new Button(this);
        run37.setText("RUN ZERO-CLICK RADIO CENSUS");
        run37.setTextSize(13f);
        run37.setAllCaps(false);
        run37.setOnClickListener(v -> runCensus37());
        panel.addView(run37, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp37(46)));

        root.addView(panel, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void runCensus37() {
        if (running37) return;
        if (web37 == null || !isChatGpt37(web37.getUrl())) {
            setStatus37("Blocked: ChatGPT page not ready");
            return;
        }
        running37 = true;
        telemetryHealthy37 = false;
        testId37 = "cp37-" + UUID.randomUUID();
        seq37 = 0;
        snapshotsOk37 = 0;
        snapshotsComplete37 = 0;
        stableRadioSetCount37 = 0;
        stableSelectedSetCount37 = 0;
        maxRadioCount37 = 0;
        maxSelectedCount37 = 0;
        firstRadioSetHash37 = "-";
        firstSelectedSetHash37 = "-";
        startedAt37 = System.currentTimeMillis();
        if (run37 != null) {
            run37.setEnabled(false);
            run37.setText("RADIO CENSUS RUNNING...");
        }
        setStatus37("Telemetry preflight...");
        telemetryPreflight37();
    }

    private void telemetryPreflight37() {
        JSONObject st = baseState37();
        put37(st, "snapshot_target", SNAPSHOT_COUNT37);
        put37(st, "collector_capacity_hint", TelemetryConfigV37.COLLECTOR_CAPACITY_HINT);
        JSONObject p = payload37("TELEMETRY_PREFLIGHT", "RUNNING", st);
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!running37 || !once.compareAndSet(false, true)) return;
            finish37("TELEMETRY_PREFLIGHT_TIMEOUT");
        };
        h37.postDelayed(timeout, 8000L);
        new Thread(() -> {
            JSONObject r = upload37(p, NET_TIMEOUT_MS37 + 900);
            runOnUiThread(() -> {
                if (!running37 || !once.compareAndSet(false, true)) return;
                h37.removeCallbacks(timeout);
                if (!r.optBoolean("success", false)) {
                    finish37("TELEMETRY_UNAVAILABLE");
                    return;
                }
                telemetryHealthy37 = true;
                phase37("RUN_STARTED", "READ_ONLY_ZERO_CLICK", baseState37());
                takeSnapshot37(0);
            });
        }, "cp37-preflight").start();
    }

    private void takeSnapshot37(int index) {
        if (!running37) return;
        if (index >= SNAPSHOT_COUNT37) {
            boolean all = snapshotsOk37 == SNAPSHOT_COUNT37 && snapshotsComplete37 == SNAPSHOT_COUNT37;
            boolean radioStable = stableRadioSetCount37 == SNAPSHOT_COUNT37;
            boolean selectedStable = stableSelectedSetCount37 == SNAPSHOT_COUNT37;
            String cls = all && radioStable && selectedStable
                    ? "PASS_RADIO_SELECTED_STATE_CENSUS_STABLE"
                    : all ? "PASS_RADIO_CENSUS_CAPTURED_STATE_VARIATION"
                    : "PARTIAL_RADIO_SELECTED_STATE_CENSUS";
            finish37(cls);
            return;
        }
        setStatus37("Read-only radio snapshot " + (index + 1) + "/" + SNAPSHOT_COUNT37 + "...");
        eval37(snapshotJs37(index), o -> {
            JSONObject st = baseState37();
            boolean success = o.optBoolean("success", false);
            boolean complete = o.optBoolean("complete", false);
            int radios = o.optInt("radio_count", -1);
            int selected = o.optInt("selected_count", -1);
            String radioHash = o.optString("radio_set_hash", "-");
            String selectedHash = o.optString("selected_set_hash", "-");

            if (success) snapshotsOk37++;
            if (complete) snapshotsComplete37++;
            maxRadioCount37 = Math.max(maxRadioCount37, Math.max(0, radios));
            maxSelectedCount37 = Math.max(maxSelectedCount37, Math.max(0, selected));

            if (index == 0) {
                firstRadioSetHash37 = radioHash;
                firstSelectedSetHash37 = selectedHash;
            }
            if (!"-".equals(firstRadioSetHash37) && firstRadioSetHash37.equals(radioHash)) stableRadioSetCount37++;
            if (!"-".equals(firstSelectedSetHash37) && firstSelectedSetHash37.equals(selectedHash)) stableSelectedSetCount37++;

            put37(st, "snapshot_index", index);
            put37(st, "success", success);
            put37(st, "complete", complete);
            put37(st, "elapsed_ms", o.optInt("elapsed_ms", -1));
            put37(st, "visited_nodes", o.optInt("visited_nodes", -1));
            put37(st, "radio_count", radios);
            put37(st, "selected_count", selected);
            put37(st, "enabled_count", o.optInt("enabled_count", -1));
            put37(st, "header_radio_count", o.optInt("header_radio_count", -1));
            put37(st, "light_count", o.optInt("light_count", -1));
            put37(st, "medium_count", o.optInt("medium_count", -1));
            put37(st, "light_selected_count", o.optInt("light_selected_count", -1));
            put37(st, "medium_selected_count", o.optInt("medium_selected_count", -1));
            put37(st, "same_group_light_medium", o.optBoolean("same_group_light_medium", false));
            put37(st, "radio_set_hash", radioHash);
            put37(st, "selected_set_hash", selectedHash);
            JSONArray radiosArr = o.optJSONArray("radios");
            if (radiosArr != null) put37(st, "radios", radiosArr);

            phase37("MODEL_RADIO_SNAPSHOT",
                    success && complete ? "CAPTURED_COMPLETE" : success ? "CAPTURED_BUDGET_LIMIT" : "UNRESOLVED",
                    st);

            long delay = index == 0 ? 650L : index == 1 ? 1100L : index == 2 ? 1700L : 0L;
            h37.postDelayed(() -> takeSnapshot37(index + 1), delay);
        });
    }

    private String snapshotJs37(int index) {
        return "(function(){try{const T0=performance.now(),MAXN=6500,MAXMS=170,MAXC=16;"
                + "const N=x=>(x||'').replace(/\\s+/g,' ').trim();const L=x=>N(x).toLowerCase();"
                + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};"
                + "const B=n=>n<=0?0:n<=8?1:n<=16?2:n<=32?3:n<=64?4:5;"
                + "let visited=0,complete=true;const roots=[document];"
                + "for(const e of document.querySelectorAll('*')){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(e.shadowRoot)roots.push(e.shadowRoot);if(roots.length>=24)break;}"
                + "const raw=[];for(const root of roots){if(performance.now()-T0>MAXMS){complete=false;break;}for(const e of root.querySelectorAll('[role=radio]')){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(V(e))raw.push(e);}}"
                + "const seen=new Set(),nodes=[];for(const e of raw){if(!seen.has(e)){seen.add(e);nodes.push(e);}}"
                + "const out=[];let selectedCount=0,enabledCount=0,headerCount=0,lightCount=0,mediumCount=0,lightSel=0,mediumSel=0;const groups={};"
                + "for(const e of nodes){if(out.length>=MAXC)break;const txt=N(e.innerText||e.textContent||'');const aria=N(e.getAttribute('aria-label'));const title=N(e.getAttribute('title'));const acc=N(aria||title||txt);const la=L(acc);"
                + "const ds=L(e.getAttribute('data-state')),ac=L(e.getAttribute('aria-checked')),as=L(e.getAttribute('aria-selected')),ap=L(e.getAttribute('aria-pressed')),cur=L(e.getAttribute('aria-current'));"
                + "const selected=ac==='true'||as==='true'||ap==='true'||cur==='true'||ds==='checked'||ds==='selected'||ds==='active'||ds==='on';"
                + "const enabled=!e.disabled&&L(e.getAttribute('aria-disabled'))!=='true';const headerish=!!e.closest('header,nav');"
                + "const semLight=/(^|\\b)light(\\b|$)/i.test(la);const semMedium=/(^|\\b)medium(\\b|$)/i.test(la);"
                + "const g=e.closest('[role=radiogroup]')||e.parentElement;const ga=g?L(g.getAttribute('aria-label')):'';const gt=g?L(g.getAttribute('data-testid')):'';const gr=g?L(g.getAttribute('role')):'';const gc=g&&g.children?g.children.length:0;const groupHash=H((g&&g.tagName||'-')+'|'+gr+'|'+H(ga)+'|'+H(gt)+'|'+B(gc));"
                + "if(!groups[groupHash])groups[groupHash]={light:0,medium:0};if(semLight)groups[groupHash].light++;if(semMedium)groups[groupHash].medium++;"
                + "if(selected)selectedCount++;if(enabled)enabledCount++;if(headerish)headerCount++;if(semLight){lightCount++;if(selected)lightSel++;}if(semMedium){mediumCount++;if(selected)mediumSel++;}"
                + "const q={tag:(e.tagName||'').toLowerCase(),headerish:headerish,group_hash:groupHash,enabled:enabled,selected:selected,has_data_state:ds!=='',data_state_hash:ds?H(ds):'-',data_state_checked:ds==='checked',data_state_selected:ds==='selected',data_state_active:ds==='active',data_state_on:ds==='on',aria_checked_true:ac==='true',aria_selected_true:as==='true',aria_pressed_true:ap==='true',aria_current_true:cur==='true',sem_light:semLight,sem_medium:semMedium,sem_auto:/(^|\\b)auto(\\b|$)/i.test(la),sem_thinking:la.includes('thinking'),acc_hash:acc?H(la):'-',text_len_bucket:B(txt.length),aria_len_bucket:B(aria.length),title_len_bucket:B(title.length)};"
                + "q.fp=H([q.tag,q.headerish,q.group_hash,q.enabled,q.selected,q.has_data_state,q.data_state_hash,q.aria_checked_true,q.aria_selected_true,q.aria_pressed_true,q.aria_current_true,q.sem_light,q.sem_medium,q.sem_auto,q.sem_thinking,q.acc_hash,q.text_len_bucket,q.aria_len_bucket,q.title_len_bucket].join('|'));out.push(q);}" 
                + "out.sort((a,b)=>a.group_hash.localeCompare(b.group_hash)||a.acc_hash.localeCompare(b.acc_hash)||a.fp.localeCompare(b.fp));let sameGroup=false;for(const k of Object.keys(groups)){if(groups[k].light===1&&groups[k].medium===1){sameGroup=true;break;}}"
                + "const radioSetHash=H(out.map(x=>x.fp.replace('|true|','|*|').replace('|false|','|*|')).join(','));const selectedSetHash=H(out.filter(x=>x.selected).map(x=>x.group_hash+':'+x.acc_hash).join(','));"
                + "return JSON.stringify({success:true,complete:complete,snapshot_index:" + index + ",elapsed_ms:Math.round(performance.now()-T0),visited_nodes:visited,radio_count:out.length,selected_count:selectedCount,enabled_count:enabledCount,header_radio_count:headerCount,light_count:lightCount,medium_count:mediumCount,light_selected_count:lightSel,medium_selected_count:mediumSel,same_group_light_medium:sameGroup,radio_set_hash:radioSetHash,selected_set_hash:selectedSetHash,radios:out});"
                + "}catch(e){return JSON.stringify({success:false,complete:false,error_class:'SCAN_EXCEPTION',radio_count:-1,selected_count:-1});}})();";
    }

    private void eval37(String js, JsonDone37 done) {
        if (web37 == null) { done.done(new JSONObject()); return; }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (once.compareAndSet(false, true)) {
                JSONObject o = new JSONObject();
                put37(o, "success", false);
                put37(o, "complete", false);
                put37(o, "error_class", "EVAL_TIMEOUT");
                done.done(o);
            }
        };
        h37.postDelayed(timeout, EVAL_TIMEOUT_MS37);
        web37.evaluateJavascript(js, value -> {
            if (!once.compareAndSet(false, true)) return;
            h37.removeCallbacks(timeout);
            try {
                String s = value == null ? "" : value;
                Object outer = new JSONTokener(s).nextValue();
                if (outer instanceof String) s = (String) outer;
                done.done(new JSONObject(s));
            } catch (Exception e) {
                JSONObject o = new JSONObject();
                put37(o, "success", false);
                put37(o, "complete", false);
                put37(o, "error_class", "PARSE_ERROR");
                done.done(o);
            }
        });
    }

    private void finish37(String classification) {
        if (!running37) return;
        JSONObject st = baseState37();
        put37(st, "snapshots_ok", snapshotsOk37);
        put37(st, "snapshots_complete", snapshotsComplete37);
        put37(st, "stable_radio_set_count", stableRadioSetCount37);
        put37(st, "stable_selected_set_count", stableSelectedSetCount37);
        put37(st, "max_radio_count", maxRadioCount37);
        put37(st, "max_selected_count", maxSelectedCount37);
        put37(st, "runtime_ms", System.currentTimeMillis() - startedAt37);
        put37(st, "dom_clicks", 0);
        put37(st, "capability_dispatches", 0);
        put37(st, "raw_text_uploaded", false);
        put37(st, "raw_html_uploaded", false);
        put37(st, "cookies_tokens_accessed", false);
        JSONObject p = payload37("FINAL", classification, st);
        if (telemetryHealthy37) new Thread(() -> upload37(p, NET_TIMEOUT_MS37), "cp37-final").start();
        running37 = false;
        setStatus37(classification);
        if (run37 != null) {
            run37.setEnabled(true);
            run37.setText("RUN ZERO-CLICK RADIO CENSUS");
        }
    }

    private void phase37(String phase, String classification, JSONObject state) {
        if (!telemetryHealthy37) return;
        JSONObject p = payload37(phase, classification, state);
        new Thread(() -> upload37(p, NET_TIMEOUT_MS37), "cp37-phase").start();
    }

    private JSONObject payload37(String phase, String classification, JSONObject state) {
        JSONObject p = new JSONObject();
        put37(p, "schema_version", SCHEMA37);
        put37(p, "scenario_id", SCENARIO37);
        put37(p, "source_ref", TelemetryConfigV37.SOURCE_REF);
        put37(p, "collector_id", TelemetryConfigV37.COLLECTOR_ID);
        put37(p, "test_id", testId37);
        put37(p, "seq", seq37++);
        put37(p, "phase", phase);
        put37(p, "classification", classification);
        put37(p, "timestamp_epoch_ms", System.currentTimeMillis());
        put37(p, "state", state == null ? new JSONObject() : state);
        return p;
    }

    private JSONObject baseState37() {
        JSONObject s = new JSONObject();
        put37(s, "dom_clicks", 0);
        put37(s, "capability_dispatches", 0);
        return s;
    }

    private JSONObject upload37(JSONObject payload, int timeoutMs) {
        JSONObject out = new JSONObject();
        HttpURLConnection c = null;
        try {
            if (!TelemetryConfigV37.isConfigured()) {
                put37(out, "success", false);
                put37(out, "error", "UNCONFIGURED");
                return out;
            }
            byte[] body = payload.toString().getBytes(StandardCharsets.UTF_8);
            c = (HttpURLConnection) new URL(TelemetryConfigV37.WEBHOOK_URL).openConnection();
            c.setRequestMethod("POST");
            c.setConnectTimeout(timeoutMs);
            c.setReadTimeout(timeoutMs);
            c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/json");
            c.getOutputStream().write(body);
            int code = c.getResponseCode();
            put37(out, "success", code >= 200 && code < 300);
            put37(out, "status", code);
        } catch (Exception e) {
            put37(out, "success", false);
            put37(out, "error", e.getClass().getSimpleName());
        } finally {
            if (c != null) c.disconnect();
        }
        return out;
    }

    private WebView findWeb37(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb37(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }

    private boolean isChatGpt37(String u) {
        try {
            Uri x = Uri.parse(u == null ? "" : u);
            String h = x.getHost();
            return h != null && ("chatgpt.com".equalsIgnoreCase(h) || h.toLowerCase().endsWith(".chatgpt.com"));
        } catch (Exception e) {
            return false;
        }
    }

    private int dp37(int x) {
        return Math.round(x * getResources().getDisplayMetrics().density);
    }

    private void setStatus37(String s) {
        if (status37 != null) status37.setText(s);
    }

    private static void put37(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) {}
    }
}
