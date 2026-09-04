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
 * Stable v0.37 — zero-click composer effort selector census.
 *
 * The previous direct-radio hypothesis is intentionally discarded: the two header
 * role=radio controls are Chat/Work, not model effort. This diagnostic anchors on the
 * visible composer input, finds the nearest bounded composer control cluster, and
 * fingerprints visible non-radio buttons for Light/Medium/Heavy/Auto semantics.
 * No DOM click or capability dispatch is performed.
 */
public class OrchestratorPaidModelEffortCensusV39Activity extends OrchestratorAuthModeV34Activity {
    private static final String SCHEMA39 = "cp-v39-paid-model-effort-census-v1";
    private static final String SCENARIO39 = "paid-model-composer-effort-read-only-census";
    private static final long EVAL_TIMEOUT_MS39 = 2800L;
    private static final int NET_TIMEOUT_MS39 = 3200;
    private static final int SNAPSHOT_COUNT39 = 4;

    private final Handler h39 = new Handler(Looper.getMainLooper());
    private WebView web39;
    private TextView status39;
    private Button run39;
    private boolean running39 = false;
    private boolean telemetryHealthy39 = false;
    private String testId39 = "-";
    private int seq39 = 0;
    private int snapshotsOk39 = 0;
    private int snapshotsComplete39 = 0;
    private int exactEffortSnapshots39 = 0;
    private String firstEffortHash39 = "-";
    private String firstEffortSemantic39 = "-";
    private int stableEffortHashCount39 = 0;
    private int stableEffortSemanticCount39 = 0;
    private long startedAt39 = 0L;

    private interface JsonDone39 { void done(JSONObject o); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web39 = findWeb39(getWindow().getDecorView());
        installCompactUi39();
        setStatus39("v0.37 composer effort census ready — zero click");
    }

    @Override protected void onDestroy() {
        h39.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private void installCompactUi39() {
        if (web39 == null) return;
        ViewParent p = web39.getParent();
        if (!(p instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) p;
        for (int i = 0; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            if (child != web39) child.setVisibility(View.GONE);
        }
        web39.setMinimumHeight(1);
        web39.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp39(8), dp39(3), dp39(8), dp39(6));

        status39 = new TextView(this);
        status39.setTextSize(11f);
        status39.setSingleLine(true);
        status39.setEllipsize(TextUtils.TruncateAt.END);
        panel.addView(status39, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));

        run39 = new Button(this);
        run39.setText("RUN ZERO-CLICK EFFORT CENSUS");
        run39.setTextSize(13f);
        run39.setAllCaps(false);
        run39.setOnClickListener(v -> runCensus39());
        panel.addView(run39, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp39(46)));

        root.addView(panel, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void runCensus39() {
        if (running39) return;
        if (web39 == null || !isChatGpt39(web39.getUrl())) {
            setStatus39("Blocked: ChatGPT page not ready");
            return;
        }
        running39 = true;
        telemetryHealthy39 = false;
        testId39 = "cp39-" + UUID.randomUUID();
        seq39 = 0;
        snapshotsOk39 = 0;
        snapshotsComplete39 = 0;
        exactEffortSnapshots39 = 0;
        firstEffortHash39 = "-";
        firstEffortSemantic39 = "-";
        stableEffortHashCount39 = 0;
        stableEffortSemanticCount39 = 0;
        startedAt39 = System.currentTimeMillis();
        if (run39 != null) {
            run39.setEnabled(false);
            run39.setText("EFFORT CENSUS RUNNING...");
        }
        setStatus39("Telemetry preflight...");
        telemetryPreflight39();
    }

    private void telemetryPreflight39() {
        JSONObject st = baseState39();
        put39(st, "snapshot_target", SNAPSHOT_COUNT39);
        JSONObject p = payload39("TELEMETRY_PREFLIGHT", "RUNNING", st);
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!running39 || !once.compareAndSet(false, true)) return;
            finish39("TELEMETRY_PREFLIGHT_TIMEOUT");
        };
        h39.postDelayed(timeout, 8000L);
        new Thread(() -> {
            JSONObject r = upload39(p, NET_TIMEOUT_MS39 + 900);
            runOnUiThread(() -> {
                if (!running39 || !once.compareAndSet(false, true)) return;
                h39.removeCallbacks(timeout);
                if (!r.optBoolean("success", false)) {
                    finish39("TELEMETRY_UNAVAILABLE");
                    return;
                }
                telemetryHealthy39 = true;
                phase39("RUN_STARTED", "READ_ONLY_ZERO_CLICK_COMPOSER_EFFORT", baseState39());
                takeSnapshot39(0);
            });
        }, "cp39-preflight").start();
    }

    private void takeSnapshot39(int index) {
        if (!running39) return;
        if (index >= SNAPSHOT_COUNT39) {
            boolean all = snapshotsOk39 == SNAPSHOT_COUNT39 && snapshotsComplete39 == SNAPSHOT_COUNT39;
            boolean exact = exactEffortSnapshots39 == SNAPSHOT_COUNT39;
            boolean stable = stableEffortHashCount39 == SNAPSHOT_COUNT39
                    && stableEffortSemanticCount39 == SNAPSHOT_COUNT39;
            finish39(all && exact && stable
                    ? "PASS_COMPOSER_EFFORT_SELECTOR_CENSUS_STABLE"
                    : all ? "PASS_COMPOSER_EFFORT_CENSUS_CAPTURED_AMBIGUOUS"
                    : "PARTIAL_COMPOSER_EFFORT_CENSUS");
            return;
        }

        setStatus39("Composer effort snapshot " + (index + 1) + "/" + SNAPSHOT_COUNT39 + "...");
        eval39(snapshotJs39(index), o -> {
            JSONObject st = baseState39();
            boolean success = o.optBoolean("success", false);
            boolean complete = o.optBoolean("complete", false);
            int effortCount = o.optInt("effort_control_count", -1);
            String effortHash = o.optString("effort_control_hash", "-");
            String effortSemantic = o.optString("effort_semantic", "-");

            if (success) snapshotsOk39++;
            if (complete) snapshotsComplete39++;
            if (effortCount == 1 && !"-".equals(effortHash) && !"-".equals(effortSemantic)) exactEffortSnapshots39++;
            if (index == 0) {
                firstEffortHash39 = effortHash;
                firstEffortSemantic39 = effortSemantic;
            }
            if (!"-".equals(firstEffortHash39) && firstEffortHash39.equals(effortHash)) stableEffortHashCount39++;
            if (!"-".equals(firstEffortSemantic39) && firstEffortSemantic39.equals(effortSemantic)) stableEffortSemanticCount39++;

            put39(st, "snapshot_index", index);
            put39(st, "success", success);
            put39(st, "complete", complete);
            put39(st, "elapsed_ms", o.optInt("elapsed_ms", -1));
            put39(st, "visited_nodes", o.optInt("visited_nodes", -1));
            put39(st, "input_found", o.optBoolean("input_found", false));
            put39(st, "composer_root_found", o.optBoolean("composer_root_found", false));
            put39(st, "composer_control_count", o.optInt("composer_control_count", -1));
            put39(st, "effort_control_count", effortCount);
            put39(st, "light_count", o.optInt("light_count", -1));
            put39(st, "medium_count", o.optInt("medium_count", -1));
            put39(st, "heavy_count", o.optInt("heavy_count", -1));
            put39(st, "auto_count", o.optInt("auto_count", -1));
            put39(st, "thinking_count", o.optInt("thinking_count", -1));
            put39(st, "effort_control_hash", effortHash);
            put39(st, "effort_semantic", effortSemantic);
            put39(st, "candidate_set_hash", o.optString("candidate_set_hash", "-"));
            JSONArray controls = o.optJSONArray("controls");
            if (controls != null) put39(st, "controls", controls);
            phase39("COMPOSER_EFFORT_SNAPSHOT",
                    success && complete ? "CAPTURED_COMPLETE" : success ? "CAPTURED_BUDGET_LIMIT" : "UNRESOLVED",
                    st);

            long delay = index == 0 ? 650L : index == 1 ? 1100L : index == 2 ? 1700L : 0L;
            h39.postDelayed(() -> takeSnapshot39(index + 1), delay);
        });
    }

    private String snapshotJs39(int index) {
        return "(function(){try{const T0=performance.now(),MAXN=6500,MAXMS=180,MAXC=16;"
                + "const N=x=>(x||'').replace(/\\s+/g,' ').trim();const L=x=>N(x).toLowerCase();"
                + "const TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean);const HAS=(s,w)=>TOK(s).includes(w);"
                + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};"
                + "const B=n=>n<=0?0:n<=8?1:n<=16?2:n<=32?3:n<=64?4:5;"
                + "let visited=0,complete=true,input=null;"
                + "for(const e of document.querySelectorAll('textarea,[contenteditable=\"true\"],[role=\"textbox\"]')){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(V(e)){input=e;break;}}"
                + "let root=null;if(input){let p=input.parentElement;for(let d=0;p&&d<9;d++,p=p.parentElement){if(performance.now()-T0>MAXMS){complete=false;break;}const cs=[...p.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio');if(cs.length>=3&&cs.length<=12){root=p;break;}}}"
                + "const nodes=root?[...root.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio'):[];"
                + "const seen=new Set(),controls=[];let light=0,medium=0,heavy=0,auto=0,thinking=0,effort=0,effortHash='-',effortSemantic='-';"
                + "for(const e of nodes){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(seen.has(e))continue;seen.add(e);if(controls.length>=MAXC)break;"
                + "const txt=N(e.innerText||e.textContent||''),aria=N(e.getAttribute('aria-label')),title=N(e.getAttribute('title')),acc=N(aria||title||txt),mix=acc+' '+txt;"
                + "const sl=HAS(mix,'light'),sm=HAS(mix,'medium'),sh=HAS(mix,'heavy'),sa=HAS(mix,'auto'),st=HAS(mix,'thinking');const semCount=(sl?1:0)+(sm?1:0)+(sh?1:0)+(sa?1:0);"
                + "const sem=semCount===1?(sl?'LIGHT':sm?'MEDIUM':sh?'HEAVY':'AUTO'):'NONE';if(sl)light++;if(sm)medium++;if(sh)heavy++;if(sa)auto++;if(st)thinking++;if(sem!=='NONE')effort++;"
                + "const popup=N(e.getAttribute('aria-haspopup')),expanded=N(e.getAttribute('aria-expanded')),ds=N(e.getAttribute('data-state')),ap=N(e.getAttribute('aria-pressed')),ac=N(e.getAttribute('aria-current')),testid=N(e.getAttribute('data-testid'));"
                + "const parent=e.parentElement;const pt=parent?N(parent.getAttribute('data-testid')):'';const q={tag:(e.tagName||'').toLowerCase(),enabled:!(e.disabled||L(e.getAttribute('aria-disabled'))==='true'),sem_light:sl,sem_medium:sm,sem_heavy:sh,sem_auto:sa,sem_thinking:st,effort_semantic:sem,has_popup:popup!==''&&L(popup)!=='false',popup_hash:popup?H(L(popup)):'-',has_expanded:expanded!=='',expanded_true:L(expanded)==='true',has_data_state:ds!=='',data_state_hash:ds?H(L(ds)):'-',aria_pressed_true:L(ap)==='true',aria_current_true:L(ac)==='true',has_svg:!!e.querySelector('svg'),acc_hash:acc?H(L(acc)):'-',text_hash:txt?H(L(txt)):'-',testid_hash:testid?H(L(testid)):'-',parent_testid_hash:pt?H(L(pt)):'-',text_len_bucket:B(txt.length),aria_len_bucket:B(aria.length),title_len_bucket:B(title.length)};"
                + "q.fp=H([q.tag,q.enabled,q.sem_light,q.sem_medium,q.sem_heavy,q.sem_auto,q.sem_thinking,q.effort_semantic,q.has_popup,q.popup_hash,q.has_expanded,q.expanded_true,q.has_data_state,q.data_state_hash,q.aria_pressed_true,q.aria_current_true,q.has_svg,q.acc_hash,q.text_hash,q.testid_hash,q.parent_testid_hash,q.text_len_bucket,q.aria_len_bucket,q.title_len_bucket].join('|'));controls.push(q);if(sem!=='NONE'){effortHash=q.acc_hash!=='-'?q.acc_hash:q.text_hash;effortSemantic=sem;}}"
                + "controls.sort((a,b)=>a.fp.localeCompare(b.fp));const setHash=H(controls.map(x=>x.fp).join(','));if(effort!==1){effortHash='-';effortSemantic='-';}"
                + "return JSON.stringify({success:true,complete:complete,snapshot_index:" + index + ",elapsed_ms:Math.round(performance.now()-T0),visited_nodes:visited,input_found:!!input,composer_root_found:!!root,composer_control_count:controls.length,effort_control_count:effort,light_count:light,medium_count:medium,heavy_count:heavy,auto_count:auto,thinking_count:thinking,effort_control_hash:effortHash,effort_semantic:effortSemantic,candidate_set_hash:setHash,controls:controls});"
                + "}catch(e){return JSON.stringify({success:false,complete:false,error_class:'SCAN_EXCEPTION',effort_control_count:-1,composer_control_count:-1});}})();";
    }

    private void eval39(String js, JsonDone39 done) {
        if (web39 == null) { done.done(new JSONObject()); return; }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (once.compareAndSet(false, true)) {
                JSONObject o = new JSONObject();
                put39(o, "success", false);
                put39(o, "complete", false);
                put39(o, "error_class", "EVAL_TIMEOUT");
                done.done(o);
            }
        };
        h39.postDelayed(timeout, EVAL_TIMEOUT_MS39);
        web39.evaluateJavascript(js, value -> {
            if (!once.compareAndSet(false, true)) return;
            h39.removeCallbacks(timeout);
            try {
                String s = value == null ? "" : value;
                Object outer = new JSONTokener(s).nextValue();
                if (outer instanceof String) s = (String) outer;
                done.done(new JSONObject(s));
            } catch (Exception e) {
                JSONObject o = new JSONObject();
                put39(o, "success", false);
                put39(o, "complete", false);
                put39(o, "error_class", "PARSE_ERROR");
                done.done(o);
            }
        });
    }

    private void finish39(String classification) {
        if (!running39) return;
        JSONObject st = baseState39();
        put39(st, "snapshots_ok", snapshotsOk39);
        put39(st, "snapshots_complete", snapshotsComplete39);
        put39(st, "exact_effort_snapshots", exactEffortSnapshots39);
        put39(st, "stable_effort_hash_count", stableEffortHashCount39);
        put39(st, "stable_effort_semantic_count", stableEffortSemanticCount39);
        put39(st, "runtime_ms", System.currentTimeMillis() - startedAt39);
        put39(st, "dom_clicks", 0);
        put39(st, "capability_dispatches", 0);
        put39(st, "raw_text_uploaded", false);
        put39(st, "raw_html_uploaded", false);
        put39(st, "cookies_tokens_accessed", false);
        JSONObject p = payload39("FINAL", classification, st);
        if (telemetryHealthy39) new Thread(() -> upload39(p, NET_TIMEOUT_MS39), "cp39-final").start();
        running39 = false;
        setStatus39(classification);
        if (run39 != null) {
            run39.setEnabled(true);
            run39.setText("RUN ZERO-CLICK EFFORT CENSUS");
        }
    }

    private void phase39(String phase, String classification, JSONObject state) {
        if (!running39 || !telemetryHealthy39) return;
        JSONObject p = payload39(phase, classification, state);
        new Thread(() -> upload39(p, NET_TIMEOUT_MS39), "cp39-phase-" + seq39).start();
    }

    private JSONObject baseState39() {
        JSONObject st = new JSONObject();
        put39(st, "dom_clicks", 0);
        put39(st, "capability_dispatches", 0);
        put39(st, "raw_text_uploaded", false);
        put39(st, "raw_html_uploaded", false);
        put39(st, "cookies_tokens_accessed", false);
        return st;
    }

    private JSONObject payload39(String phase, String classification, JSONObject state) {
        JSONObject p = new JSONObject();
        put39(p, "schema_version", SCHEMA39);
        put39(p, "scenario_id", SCENARIO39);
        put39(p, "source_ref", TelemetryConfigV39.SOURCE_REF);
        put39(p, "collector_id", TelemetryConfigV39.COLLECTOR_ID);
        put39(p, "test_id", testId39);
        put39(p, "seq", seq39++);
        put39(p, "timestamp_epoch_ms", System.currentTimeMillis());
        put39(p, "phase", phase);
        put39(p, "classification", classification);
        put39(p, "state", state);
        return p;
    }

    private JSONObject upload39(JSONObject payload, int timeoutMs) {
        JSONObject r = new JSONObject();
        if (!TelemetryConfigV39.isConfigured()) {
            put39(r, "success", false);
            put39(r, "error", "TELEMETRY_NOT_CONFIGURED");
            return r;
        }
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(TelemetryConfigV39.WEBHOOK_URL).openConnection();
            c.setRequestMethod("POST");
            c.setConnectTimeout(timeoutMs);
            c.setReadTimeout(timeoutMs);
            c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/json");
            byte[] body = payload.toString().getBytes(StandardCharsets.UTF_8);
            c.setFixedLengthStreamingMode(body.length);
            c.getOutputStream().write(body);
            int code = c.getResponseCode();
            put39(r, "success", code >= 200 && code < 300);
            put39(r, "code", code);
        } catch (Exception e) {
            put39(r, "success", false);
            put39(r, "error", "NETWORK_ERROR");
        } finally {
            if (c != null) c.disconnect();
        }
        return r;
    }

    private WebView findWeb39(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb39(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }

    private boolean isChatGpt39(String url) {
        if (TextUtils.isEmpty(url)) return false;
        try {
            String h = Uri.parse(url).getHost();
            if (h == null) return false;
            h = h.toLowerCase();
            return h.equals("chatgpt.com") || h.endsWith(".chatgpt.com")
                    || h.equals("openai.com") || h.endsWith(".openai.com");
        } catch (Exception e) {
            return false;
        }
    }

    private int dp39(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    private void setStatus39(String s) {
        if (status39 != null) status39.setText(s);
    }

    private static void put39(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) {}
    }
}
