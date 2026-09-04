package com.homayounisaghar.chatgptwebviewprobe;

import android.content.SharedPreferences;
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
 * Stable v0.36 — guarded direct-radio paid model round-trip.
 *
 * This build never uses the invalidated v0.34 sem_model control as an opener.
 * It first proves exactly two visible header radios, exactly one LIGHT and one MEDIUM
 * in the same group, both enabled, and exactly one selected. Only then does it create
 * a durable claim BEFORE the first state-changing click. Each click is followed by a
 * selected-state receipt. Ambiguous state never triggers blind replay.
 *
 * Telemetry contains only hashes, counts, semantic classes and receipts; no raw labels,
 * chat text, HTML, cookies, tokens, credentials or URL query strings are uploaded.
 */
public class OrchestratorPaidModelDirectRadioV38Activity extends OrchestratorAuthModeV34Activity {
    private static final String SCHEMA38 = "cp-v38-paid-model-direct-radio-v1";
    private static final String SCENARIO38 = "paid-model-direct-radio-guarded-roundtrip";
    private static final long EVAL_TIMEOUT_MS38 = 2800L;
    private static final int NET_TIMEOUT_MS38 = 3200;
    private static final long RECEIPT_TIMEOUT_MS38 = 7000L;
    private static final long GLOBAL_WATCHDOG_MS38 = 28000L;

    private final Handler h38 = new Handler(Looper.getMainLooper());
    private WebView web38;
    private TextView status38;
    private Button run38;
    private SharedPreferences prefs38;
    private boolean running38 = false;
    private boolean telemetryHealthy38 = false;
    private String testId38 = "-";
    private int seq38 = 0;
    private int selectionClicks38 = 0;
    private long startedAt38 = 0L;

    private String originalHash38 = "-";
    private String targetHash38 = "-";
    private String groupHash38 = "-";
    private String originalClass38 = "UNKNOWN";
    private String targetClass38 = "UNKNOWN";
    private String claimAction38 = "NONE";
    private String claimStatus38 = "NONE";

    private interface JsonDone38 { void done(JSONObject o); }
    private interface BoolDone38 { void done(boolean ok); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs38 = getSharedPreferences("cp38_paid_model_direct_radio", MODE_PRIVATE);
        web38 = findWeb38(getWindow().getDecorView());
        installCompactUi38();
        String prior = prefs38.getString("claim_status", "NONE");
        if (isUnresolved38(prior)) {
            setStatus38("Blocked: unresolved prior claim — no replay");
            if (run38 != null) run38.setEnabled(false);
        } else {
            setStatus38("v0.36 direct-radio round-trip ready");
        }
    }

    @Override protected void onDestroy() {
        h38.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private void installCompactUi38() {
        if (web38 == null) return;
        ViewParent p = web38.getParent();
        if (!(p instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) p;
        for (int i = 0; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            if (child != web38) child.setVisibility(View.GONE);
        }
        web38.setMinimumHeight(1);
        web38.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp38(8), dp38(3), dp38(8), dp38(6));

        status38 = new TextView(this);
        status38.setTextSize(11f);
        status38.setSingleLine(true);
        status38.setEllipsize(TextUtils.TruncateAt.END);
        panel.addView(status38, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));

        run38 = new Button(this);
        run38.setText("RUN GUARDED MODEL ROUND-TRIP");
        run38.setTextSize(13f);
        run38.setAllCaps(false);
        run38.setOnClickListener(v -> runRoundTrip38());
        panel.addView(run38, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp38(46)));

        root.addView(panel, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void runRoundTrip38() {
        if (running38) return;
        String prior = prefs38.getString("claim_status", "NONE");
        if (isUnresolved38(prior)) {
            setStatus38("Blocked: unresolved prior claim — no replay");
            return;
        }
        if (web38 == null || !isChatGpt38(web38.getUrl())) {
            setStatus38("Blocked: ChatGPT page not ready");
            return;
        }

        running38 = true;
        telemetryHealthy38 = false;
        testId38 = "cp38-" + UUID.randomUUID();
        seq38 = 0;
        selectionClicks38 = 0;
        startedAt38 = System.currentTimeMillis();
        originalHash38 = targetHash38 = groupHash38 = "-";
        originalClass38 = targetClass38 = "UNKNOWN";
        claimAction38 = "NONE";
        claimStatus38 = "NONE";
        if (run38 != null) {
            run38.setEnabled(false);
            run38.setText("ROUND-TRIP RUNNING...");
        }
        setStatus38("Telemetry preflight...");
        h38.postDelayed(this::watchdog38, GLOBAL_WATCHDOG_MS38);
        telemetryPreflight38();
    }

    private void telemetryPreflight38() {
        JSONObject p = payload38("TELEMETRY_PREFLIGHT", "RUNNING", baseState38());
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!running38 || !once.compareAndSet(false, true)) return;
            finish38("TELEMETRY_PREFLIGHT_TIMEOUT");
        };
        h38.postDelayed(timeout, 8000L);
        new Thread(() -> {
            JSONObject r = upload38(p, NET_TIMEOUT_MS38 + 900);
            runOnUiThread(() -> {
                if (!running38 || !once.compareAndSet(false, true)) return;
                h38.removeCallbacks(timeout);
                if (!r.optBoolean("success", false)) {
                    finish38("TELEMETRY_UNAVAILABLE");
                    return;
                }
                telemetryHealthy38 = true;
                phase38("RUN_STARTED", "GUARDED_DIRECT_RADIO", baseState38());
                resolveBaseline38();
            });
        }, "cp38-preflight").start();
    }

    private void resolveBaseline38() {
        setStatus38("Resolving Light/Medium radios...");
        eval38(scanRadiosJs38(), o -> {
            JSONArray a = o.optJSONArray("radios");
            int radioCount = o.optInt("radio_count", -1);
            int headerCount = o.optInt("header_radio_count", -1);
            int selectedCount = o.optInt("selected_count", -1);
            int enabledCount = o.optInt("enabled_count", -1);
            int lightCount = o.optInt("light_count", -1);
            int mediumCount = o.optInt("medium_count", -1);
            boolean sameGroup = o.optBoolean("same_group_light_medium", false);

            JSONObject st = baseState38();
            put38(st, "radio_count", radioCount);
            put38(st, "header_radio_count", headerCount);
            put38(st, "selected_count", selectedCount);
            put38(st, "enabled_count", enabledCount);
            put38(st, "light_count", lightCount);
            put38(st, "medium_count", mediumCount);
            put38(st, "same_group_light_medium", sameGroup);
            put38(st, "radio_set_hash", o.optString("radio_set_hash", "-"));
            put38(st, "selected_set_hash", o.optString("selected_set_hash", "-"));

            boolean shape = o.optBoolean("success", false) && o.optBoolean("complete", false)
                    && radioCount == 2 && headerCount == 2 && selectedCount == 1
                    && enabledCount == 2 && lightCount == 1 && mediumCount == 1 && sameGroup;
            if (!shape || a == null || a.length() != 2) {
                phase38("BASELINE_RADIO_CENSUS", "FAIL_CLOSED_UNRESOLVED", st);
                finish38("BASELINE_RADIO_MAPPING_UNRESOLVED_ZERO_CLICK");
                return;
            }

            JSONObject selected = null, alternate = null;
            for (int i = 0; i < a.length(); i++) {
                JSONObject x = a.optJSONObject(i);
                if (x == null) continue;
                if (x.optBoolean("selected", false)) selected = x;
                else alternate = x;
            }
            if (selected == null || alternate == null) {
                phase38("BASELINE_RADIO_CENSUS", "FAIL_CLOSED_SELECTED_AMBIGUOUS", st);
                finish38("BASELINE_SELECTED_AMBIGUOUS_ZERO_CLICK");
                return;
            }

            String sg = selected.optString("group_hash", "-");
            String ag = alternate.optString("group_hash", "-");
            if ("-".equals(sg) || !sg.equals(ag)) {
                phase38("BASELINE_RADIO_CENSUS", "FAIL_CLOSED_GROUP_MISMATCH", st);
                finish38("BASELINE_GROUP_MISMATCH_ZERO_CLICK");
                return;
            }

            originalHash38 = selected.optString("acc_hash", "-");
            targetHash38 = alternate.optString("acc_hash", "-");
            groupHash38 = sg;
            originalClass38 = classOf38(selected);
            targetClass38 = classOf38(alternate);
            boolean classPair = (("LIGHT".equals(originalClass38) && "MEDIUM".equals(targetClass38))
                    || ("MEDIUM".equals(originalClass38) && "LIGHT".equals(targetClass38)));
            if ("-".equals(originalHash38) || "-".equals(targetHash38)
                    || originalHash38.equals(targetHash38) || !classPair) {
                phase38("BASELINE_RADIO_CENSUS", "FAIL_CLOSED_SEMANTIC_PAIR", baseState38());
                finish38("BASELINE_SEMANTIC_PAIR_UNRESOLVED_ZERO_CLICK");
                return;
            }

            phase38("BASELINE_RADIO_CENSUS", "PASS_UNIQUE_LIGHT_MEDIUM_PAIR", baseState38());
            selectTarget38();
        });
    }

    private void selectTarget38() {
        setStatus38("Claim -> switch to alternate...");
        if (!durableClaim38("MODEL_RADIO_SELECT_TARGET", targetHash38)) {
            finish38("TARGET_CLAIM_FAILED_ZERO_CLICK");
            return;
        }
        eval38(clickRadioJs38(targetHash38, groupHash38), r -> {
            int matches = r.optInt("matches", -1);
            boolean clicked = r.optBoolean("clicked", false);
            if (!r.optBoolean("success", false) || matches != 1 || !clicked) {
                abortNoSideEffect38("TARGET_MATCHES_" + matches);
                phase38("MODEL_TARGET_DISPATCH", "ABORTED_NO_SIDE_EFFECT", baseState38());
                finish38("TARGET_NOT_DISPATCHED");
                return;
            }
            selectionClicks38++;
            markDispatched38();
            phase38("MODEL_TARGET_DISPATCH", "DISPATCHED_UNIQUE_RADIO", baseState38());
            verifySelected38(targetHash38, System.currentTimeMillis() + RECEIPT_TIMEOUT_MS38, ok -> {
                if (!ok) {
                    uncertain38("MODEL_RADIO_SELECT_TARGET");
                    finish38("TARGET_RECEIPT_TIMEOUT_UNCERTAIN_NO_REPLAY");
                    return;
                }
                confirmClaim38("TARGET_SELECTED_CONFIRMED");
                phase38("MODEL_TARGET_RECEIPT", "PASS_TARGET_SELECTED", baseState38());
                restoreOriginal38();
            });
        });
    }

    private void restoreOriginal38() {
        setStatus38("Claim -> restore original...");
        if (!durableClaim38("MODEL_RADIO_RESTORE_ORIGINAL", originalHash38)) {
            finish38("RESTORE_CLAIM_FAILED");
            return;
        }
        eval38(clickRadioJs38(originalHash38, groupHash38), r -> {
            int matches = r.optInt("matches", -1);
            boolean clicked = r.optBoolean("clicked", false);
            if (!r.optBoolean("success", false) || matches != 1 || !clicked) {
                abortNoSideEffect38("RESTORE_MATCHES_" + matches);
                phase38("MODEL_RESTORE_DISPATCH", "ABORTED_NO_SIDE_EFFECT", baseState38());
                finish38("RESTORE_NOT_DISPATCHED");
                return;
            }
            selectionClicks38++;
            markDispatched38();
            phase38("MODEL_RESTORE_DISPATCH", "DISPATCHED_UNIQUE_RADIO", baseState38());
            verifySelected38(originalHash38, System.currentTimeMillis() + RECEIPT_TIMEOUT_MS38, ok -> {
                if (!ok) {
                    uncertain38("MODEL_RADIO_RESTORE_ORIGINAL");
                    finish38("RESTORE_RECEIPT_TIMEOUT_UNCERTAIN_NO_REPLAY");
                    return;
                }
                confirmClaim38("ORIGINAL_RESTORED_CONFIRMED");
                phase38("MODEL_RESTORE_RECEIPT", "PASS_ORIGINAL_RESTORED", baseState38());
                finish38(selectionClicks38 == 2
                        ? "PASS_DIRECT_RADIO_MODEL_ROUNDTRIP_RESTORED"
                        : "FAIL_UNEXPECTED_SELECTION_CLICK_COUNT");
            });
        });
    }

    private void verifySelected38(String expectedHash, long deadline, BoolDone38 done) {
        if (!running38) { done.done(false); return; }
        eval38(scanRadiosJs38(), o -> {
            JSONArray a = o.optJSONArray("radios");
            boolean ok = o.optBoolean("success", false) && o.optBoolean("complete", false)
                    && o.optInt("radio_count", -1) == 2
                    && o.optInt("selected_count", -1) == 1
                    && o.optInt("enabled_count", -1) == 2
                    && o.optInt("light_count", -1) == 1
                    && o.optInt("medium_count", -1) == 1
                    && o.optBoolean("same_group_light_medium", false)
                    && selectedHashEquals38(a, expectedHash, groupHash38);
            if (ok) { done.done(true); return; }
            if (System.currentTimeMillis() >= deadline) { done.done(false); return; }
            h38.postDelayed(() -> verifySelected38(expectedHash, deadline, done), 320L);
        });
    }

    private boolean selectedHashEquals38(JSONArray a, String expectedHash, String expectedGroup) {
        if (a == null) return false;
        int selected = 0;
        String hash = "-", group = "-";
        for (int i = 0; i < a.length(); i++) {
            JSONObject x = a.optJSONObject(i);
            if (x != null && x.optBoolean("selected", false)) {
                selected++;
                hash = x.optString("acc_hash", "-");
                group = x.optString("group_hash", "-");
            }
        }
        return selected == 1 && expectedHash.equals(hash) && expectedGroup.equals(group);
    }

    private boolean durableClaim38(String action, String targetHash) {
        String id = action + "_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0, 8);
        boolean ok = prefs38.edit()
                .putString("claim_id", id)
                .putString("claim_action", action)
                .putString("claim_status", "CLAIMED")
                .putString("claim_target_hash", targetHash)
                .putString("claim_original_hash", originalHash38)
                .putString("claim_group_hash", groupHash38)
                .commit();
        if (!ok) return false;
        claimAction38 = action;
        claimStatus38 = "CLAIMED";
        phase38(action + "_CLAIM", "DURABLE_CLAIMED", baseState38());
        return true;
    }

    private void markDispatched38() {
        claimStatus38 = "DISPATCHED";
        prefs38.edit().putString("claim_status", claimStatus38).commit();
    }

    private void confirmClaim38(String receipt) {
        claimStatus38 = "CONFIRMED";
        prefs38.edit().putString("claim_status", claimStatus38)
                .putString("claim_receipt", receipt).commit();
    }

    private void abortNoSideEffect38(String why) {
        claimStatus38 = "ABORTED_NO_SIDE_EFFECT";
        prefs38.edit().putString("claim_status", claimStatus38)
                .putString("claim_abort_reason", token38(why)).commit();
    }

    private void uncertain38(String action) {
        claimAction38 = action;
        claimStatus38 = "UNCERTAIN_NO_REPLAY";
        prefs38.edit().putString("claim_action", action)
                .putString("claim_status", claimStatus38).commit();
        phase38("UNCERTAIN_BOUNDARY", "UNCERTAIN_NO_REPLAY", baseState38());
    }

    private boolean isUnresolved38(String s) {
        return "CLAIMED".equals(s) || "DISPATCHED".equals(s) || "UNCERTAIN_NO_REPLAY".equals(s);
    }

    private void watchdog38() {
        if (!running38) return;
        if ("DISPATCHED".equals(claimStatus38)) {
            uncertain38(claimAction38);
            finish38("GLOBAL_WATCHDOG_UNCERTAIN_NO_REPLAY");
        } else {
            finish38("GLOBAL_WATCHDOG_FAIL_CLOSED");
        }
    }

    private String classOf38(JSONObject x) {
        if (x == null) return "UNKNOWN";
        if (x.optBoolean("sem_light", false) && !x.optBoolean("sem_medium", false)) return "LIGHT";
        if (x.optBoolean("sem_medium", false) && !x.optBoolean("sem_light", false)) return "MEDIUM";
        return "UNKNOWN";
    }

    private String scanRadiosJs38() {
        return "(function(){try{const T0=performance.now(),MAXN=6500,MAXMS=170,MAXC=8;"
                + "const N=x=>(x||'').replace(/\\s+/g,' ').trim();const L=x=>N(x).toLowerCase();"
                + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};"
                + "let visited=0,complete=true;const roots=[document];for(const e of document.querySelectorAll('*')){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(e.shadowRoot)roots.push(e.shadowRoot);if(roots.length>=24)break;}"
                + "const raw=[];for(const root of roots){if(performance.now()-T0>MAXMS){complete=false;break;}for(const e of root.querySelectorAll('[role=radio]')){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(V(e))raw.push(e);}}"
                + "const seen=new Set(),nodes=[];for(const e of raw){if(!seen.has(e)){seen.add(e);nodes.push(e);}}"
                + "const out=[];let sel=0,en=0,head=0,lc=0,mc=0;const groups={};"
                + "for(const e of nodes){if(out.length>=MAXC)break;const txt=N(e.innerText||e.textContent||'');const aria=N(e.getAttribute('aria-label'));const title=N(e.getAttribute('title'));const acc=N(aria||title||txt);const la=L(acc);"
                + "const ds=L(e.getAttribute('data-state')),ac=L(e.getAttribute('aria-checked')),as=L(e.getAttribute('aria-selected')),ap=L(e.getAttribute('aria-pressed')),cur=L(e.getAttribute('aria-current'));const selected=ac==='true'||as==='true'||ap==='true'||cur==='true'||ds==='checked'||ds==='selected'||ds==='active'||ds==='on';const enabled=!e.disabled&&L(e.getAttribute('aria-disabled'))!=='true';const headerish=!!e.closest('header,nav');"
                + "const semLight=la.includes('light');const semMedium=la.includes('medium');const g=e.closest('[role=radiogroup]')||e.parentElement;const ga=g?L(g.getAttribute('aria-label')):'';const gt=g?L(g.getAttribute('data-testid')):'';const gr=g?L(g.getAttribute('role')):'';const gc=g&&g.children?g.children.length:0;const gh=H((g&&g.tagName||'-')+'|'+gr+'|'+H(ga)+'|'+H(gt)+'|'+gc);"
                + "if(!groups[gh])groups[gh]={light:0,medium:0};if(semLight){groups[gh].light++;lc++;}if(semMedium){groups[gh].medium++;mc++;}if(selected)sel++;if(enabled)en++;if(headerish)head++;"
                + "out.push({acc_hash:acc?H(la):'-',group_hash:gh,selected:selected,enabled:enabled,headerish:headerish,sem_light:semLight,sem_medium:semMedium,aria_checked_true:ac==='true',data_state_on:ds==='on',data_state_hash:ds?H(ds):'-'});}" 
                + "out.sort((a,b)=>a.group_hash.localeCompare(b.group_hash)||a.acc_hash.localeCompare(b.acc_hash));let same=false;for(const k of Object.keys(groups)){if(groups[k].light===1&&groups[k].medium===1){same=true;break;}}const rs=H(out.map(x=>x.group_hash+':'+x.acc_hash+':'+(x.enabled?'1':'0')).join(','));const ss=H(out.filter(x=>x.selected).map(x=>x.group_hash+':'+x.acc_hash).join(','));"
                + "return JSON.stringify({success:true,complete:complete,visited_nodes:visited,radio_count:out.length,header_radio_count:head,selected_count:sel,enabled_count:en,light_count:lc,medium_count:mc,same_group_light_medium:same,radio_set_hash:rs,selected_set_hash:ss,radios:out});"
                + "}catch(e){return JSON.stringify({success:false,complete:false,error_class:'SCAN_EXCEPTION',radio_count:-1});}})();";
    }

    private String clickRadioJs38(String targetHash, String groupHash) {
        String th = token38(targetHash), gh = token38(groupHash);
        return "(function(){try{const TH='" + th + "',GH='" + gh + "';const N=x=>(x||'').replace(/\\s+/g,' ').trim();const L=x=>N(x).toLowerCase();const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};let c=[];for(const e of document.querySelectorAll('[role=radio]')){if(!V(e))continue;const acc=N(e.getAttribute('aria-label')||e.getAttribute('title')||e.innerText||e.textContent||'');const la=L(acc);const g=e.closest('[role=radiogroup]')||e.parentElement;const ga=g?L(g.getAttribute('aria-label')):'';const gt=g?L(g.getAttribute('data-testid')):'';const gr=g?L(g.getAttribute('role')):'';const gc=g&&g.children?g.children.length:0;const h=H((g&&g.tagName||'-')+'|'+gr+'|'+H(ga)+'|'+H(gt)+'|'+gc);if(H(la)===TH&&h===GH)c.push(e);}let clicked=false;if(c.length===1&&!c[0].disabled&&L(c[0].getAttribute('aria-disabled'))!=='true'){c[0].click();clicked=true;}return JSON.stringify({success:true,matches:c.length,clicked:clicked});}catch(e){return JSON.stringify({success:false,matches:0,clicked:false,error_class:'CLICK_EXCEPTION'});}})();";
    }

    private void eval38(String js, JsonDone38 done) {
        if (web38 == null) { done.done(new JSONObject()); return; }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (once.compareAndSet(false, true)) {
                JSONObject o = new JSONObject();
                put38(o, "success", false);
                put38(o, "complete", false);
                put38(o, "error_class", "EVAL_TIMEOUT");
                done.done(o);
            }
        };
        h38.postDelayed(timeout, EVAL_TIMEOUT_MS38);
        web38.evaluateJavascript(js, value -> {
            if (!once.compareAndSet(false, true)) return;
            h38.removeCallbacks(timeout);
            try {
                Object outer = new JSONTokener(value == null ? "null" : value).nextValue();
                if (outer instanceof String) outer = new JSONTokener((String) outer).nextValue();
                done.done(outer instanceof JSONObject ? (JSONObject) outer : new JSONObject());
            } catch (Exception e) {
                done.done(new JSONObject());
            }
        });
    }

    private JSONObject baseState38() {
        JSONObject s = new JSONObject();
        put38(s, "claim_action", claimAction38);
        put38(s, "claim_status", claimStatus38);
        put38(s, "selection_clicks", selectionClicks38);
        put38(s, "original_hash", originalHash38);
        put38(s, "target_hash", targetHash38);
        put38(s, "group_hash", groupHash38);
        put38(s, "original_class", originalClass38);
        put38(s, "target_class", targetClass38);
        put38(s, "raw_text_uploaded", false);
        put38(s, "raw_html_uploaded", false);
        put38(s, "cookies_tokens_accessed", false);
        return s;
    }

    private void phase38(String phase, String classification, JSONObject state) {
        if (!telemetryHealthy38) return;
        JSONObject p = payload38(phase, classification, state);
        new Thread(() -> upload38(p, NET_TIMEOUT_MS38), "cp38-" + token38(phase)).start();
    }

    private JSONObject payload38(String phase, String classification, JSONObject state) {
        JSONObject p = new JSONObject();
        put38(p, "schema_version", SCHEMA38);
        put38(p, "scenario_id", SCENARIO38);
        put38(p, "test_id", testId38);
        put38(p, "seq", seq38++);
        put38(p, "phase", phase);
        put38(p, "classification", classification);
        put38(p, "source_ref", TelemetryConfigV38.SOURCE_REF);
        put38(p, "collector_id", TelemetryConfigV38.COLLECTOR_ID);
        put38(p, "timestamp_epoch_ms", System.currentTimeMillis());
        try { p.put("state", state == null ? new JSONObject() : state); } catch (Exception ignored) {}
        return p;
    }

    private JSONObject upload38(JSONObject p, int timeoutMs) {
        JSONObject r = new JSONObject();
        if (!TelemetryConfigV38.isConfigured()) return r;
        HttpURLConnection c = null;
        try {
            byte[] b = p.toString().getBytes(StandardCharsets.UTF_8);
            c = (HttpURLConnection) new URL(TelemetryConfigV38.WEBHOOK_URL).openConnection();
            c.setConnectTimeout(timeoutMs);
            c.setReadTimeout(timeoutMs);
            c.setRequestMethod("POST");
            c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/json");
            c.getOutputStream().write(b);
            int code = c.getResponseCode();
            put38(r, "success", code >= 200 && code < 300);
        } catch (Exception ignored) {
            put38(r, "success", false);
        } finally {
            if (c != null) c.disconnect();
        }
        return r;
    }

    private void finish38(String classification) {
        if (!running38) return;
        JSONObject st = baseState38();
        put38(st, "runtime_ms", System.currentTimeMillis() - startedAt38);
        put38(st, "final_claim_persisted_status", prefs38.getString("claim_status", "NONE"));
        JSONObject p = payload38("FINAL", classification, st);
        if (telemetryHealthy38) new Thread(() -> upload38(p, NET_TIMEOUT_MS38), "cp38-final").start();
        running38 = false;
        h38.removeCallbacksAndMessages(null);
        setStatus38(classification);
        if (run38 != null) {
            run38.setText("RUN GUARDED MODEL ROUND-TRIP");
            run38.setEnabled(!isUnresolved38(prefs38.getString("claim_status", "NONE")));
        }
    }

    private WebView findWeb38(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb38(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }

    private boolean isChatGpt38(String u) {
        if (u == null) return false;
        try {
            String h = android.net.Uri.parse(u).getHost();
            return h != null && (h.equals("chatgpt.com") || h.endsWith(".chatgpt.com"));
        } catch (Exception e) { return false; }
    }

    private void setStatus38(String s) {
        if (status38 != null) status38.setText(s);
    }

    private int dp38(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    private String token38(String s) {
        if (s == null) return "-";
        return s.replaceAll("[^A-Za-z0-9_.-]", "_");
    }

    private void put38(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) {}
    }
}
