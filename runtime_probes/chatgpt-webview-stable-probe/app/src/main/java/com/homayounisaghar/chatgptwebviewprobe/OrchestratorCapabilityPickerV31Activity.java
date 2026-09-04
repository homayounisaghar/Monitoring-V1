package com.homayounisaghar.chatgptwebviewprobe;

import android.content.ContentValues;
import android.content.SharedPreferences;
import android.net.Uri;
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
import java.lang.reflect.Field;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Stable v0.31 — production-style capability picker census + guarded model round-trip.
 *
 * Read-only phase enumerates the current model menu plus composer add/tools surfaces.
 * Selection phase runs only when exactly one current model and at least one distinct
 * enabled alternate are semantically resolvable. It then performs exactly one target
 * selection and exactly one restore selection, each behind a durable local claim and
 * each requiring an observable selected-option receipt. Ambiguity fails closed.
 *
 * Telemetry contains counts, hashes, selected/enabled flags and receipts only. Raw
 * model/tool labels, chat/composer text, HTML, cookies, tokens and credentials are not
 * uploaded. No prompt is sent and no tool is invoked.
 */
public class OrchestratorCapabilityPickerV31Activity extends OrchestratorVoiceSupervisorV30Activity {
    private static final String PREFS31 = "stable_v31_capability_picker";
    private static final String SCHEMA31 = "cp-v31-capability-picker-v1";
    private static final String SCENARIO31 = "model-tool-enumeration-guarded-model-roundtrip";
    private static final long WATCHDOG_MS = 50000L;
    private static final long EVAL_TIMEOUT_MS = 2600L;
    private static final int NET_TIMEOUT_MS = 2800;
    private static final int EXPECTED_EVENT_BUDGET = 24;

    private final Handler h31 = new Handler(Looper.getMainLooper());
    private final Runnable watchdog31 = this::onWatchdog31;
    private SharedPreferences prefs31;
    private WebView web31;
    private Button run31;
    private TextView status31;

    private boolean running31 = false;
    private boolean telemetryHealthy31 = false;
    private String testId31 = "-";
    private int seq31 = 0;
    private long startedAt31 = 0L;
    private String finalClassification31 = "NOT_RUN";
    private String claimAction31 = "NONE";
    private String claimStatus31 = "NONE";
    private int selectionClicks31 = 0;

    private String triggerLabel31 = "";
    private String triggerHash31 = "-";
    private String originalLabel31 = "";
    private String originalHash31 = "-";
    private String targetLabel31 = "";
    private String targetHash31 = "-";
    private int modelOptionCount31 = 0;
    private int modelEnabledCount31 = 0;
    private int addItemCount31 = 0;
    private int toolsItemCount31 = 0;
    private int toolsTriggerCount31 = 0;
    private String modelSetHash31 = "-";
    private String addSetHash31 = "-";
    private String toolsSetHash31 = "-";

    private interface JsonDone31 { void done(JSONObject o); }
    private interface BoolDone31 { void done(boolean ok); }

    private static final class ModelOpt31 {
        final String label;
        final String hash;
        final boolean selected;
        final boolean enabled;
        ModelOpt31(String label, String hash, boolean selected, boolean enabled) {
            this.label = label; this.hash = hash; this.selected = selected; this.enabled = enabled;
        }
    }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs31 = getSharedPreferences(PREFS31, MODE_PRIVATE);
        web31 = findWeb31(getWindow().getDecorView());
        compactUi31();
        setStatus31("v0.31 capability picker test ready");
        reportInterrupted31();
    }

    @Override protected void onDestroy() {
        h31.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private void compactUi31() {
        if (web31 == null) return;
        ViewParent p = web31.getParent();
        if (!(p instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) p;
        for (int i = 0; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            if (child != web31) child.setVisibility(View.GONE);
        }
        web31.setMinimumHeight(1);
        web31.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp31(8), dp31(3), dp31(8), dp31(6));
        status31 = new TextView(this);
        status31.setTextSize(11f);
        status31.setSingleLine(true);
        status31.setEllipsize(TextUtils.TruncateAt.END);
        panel.addView(status31, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        run31 = new Button(this);
        run31.setText("RUN MODEL / TOOLS TEST");
        run31.setTextSize(13f);
        run31.setAllCaps(false);
        run31.setOnClickListener(v -> run31());
        panel.addView(run31, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp31(46)));
        root.addView(panel, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void run31() {
        if (running31) return;
        if (web31 == null || !trusted31(web31.getUrl())) {
            setStatus31("Blocked: ChatGPT WebView not ready");
            return;
        }
        if (!"IDLE".equals(parentString31("sessionState")) || !"NONE".equals(parentString31("micLeaseMode"))) {
            setStatus31("Blocked: finish active audio/session first");
            return;
        }
        running31 = true;
        telemetryHealthy31 = false;
        testId31 = "cp31-" + UUID.randomUUID();
        seq31 = 0;
        startedAt31 = System.currentTimeMillis();
        finalClassification31 = "RUNNING";
        claimAction31 = "NONE";
        claimStatus31 = "NONE";
        selectionClicks31 = 0;
        triggerLabel31 = originalLabel31 = targetLabel31 = "";
        triggerHash31 = originalHash31 = targetHash31 = "-";
        modelOptionCount31 = modelEnabledCount31 = addItemCount31 = toolsItemCount31 = toolsTriggerCount31 = 0;
        modelSetHash31 = addSetHash31 = toolsSetHash31 = "-";
        prefs31.edit().putBoolean("running", true).putString("phase", "TELEMETRY_PREFLIGHT").commit();
        if (run31 != null) { run31.setEnabled(false); run31.setText("TEST RUNNING..."); }
        h31.removeCallbacks(watchdog31);
        h31.postDelayed(watchdog31, WATCHDOG_MS);
        telemetryPreflight31();
    }

    private void telemetryPreflight31() {
        JSONObject s = baseState31();
        put31(s, "collector_capacity_hint", TelemetryConfigV31.COLLECTOR_CAPACITY_HINT);
        put31(s, "expected_event_budget", EXPECTED_EVENT_BUDGET);
        JSONObject p = payload31("TELEMETRY_PREFLIGHT", "RUNNING", s, 0);
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!running31 || !once.compareAndSet(false, true)) return;
            finish31("TELEMETRY_PREFLIGHT_TIMEOUT");
        };
        h31.postDelayed(timeout, 8000L);
        new Thread(() -> {
            JSONObject r = upload31(p, NET_TIMEOUT_MS + 900);
            runOnUiThread(() -> {
                if (!running31 || !once.compareAndSet(false, true)) return;
                h31.removeCallbacks(timeout);
                if (!r.optBoolean("success", false)) { finish31("TELEMETRY_UNAVAILABLE"); return; }
                telemetryHealthy31 = true;
                phase31("RUN_STARTED", "RUNNING", baseState31());
                censusModelTrigger31();
            });
        }, "cp31-preflight").start();
    }

    private void censusModelTrigger31() {
        setStatus31("Enumerating model selector...");
        eval31(modelTriggerJs31(false), o -> {
            JSONObject s = baseState31();
            int count = o.optInt("count", -1);
            triggerLabel31 = o.optString("label", "");
            triggerHash31 = o.optString("hash", "-");
            put31(s, "model_trigger_count", count);
            put31(s, "model_trigger_hash", triggerHash31);
            if (!o.optBoolean("success", false) || count != 1) {
                phase31("MODEL_TRIGGER_CENSUS", "FAIL_NOT_UNIQUE", s);
                finish31("MODEL_TRIGGER_NOT_UNIQUE");
                return;
            }
            phase31("MODEL_TRIGGER_CENSUS", "PASS_UNIQUE_MODEL_TRIGGER", s);
            openModelMenu31(open -> {
                if (!open) { finish31("MODEL_MENU_OPEN_FAILED"); return; }
                h31.postDelayed(this::readModelOptions31, 350L);
            });
        });
    }

    private void readModelOptions31() {
        eval31(modelMenuJs31(), o -> {
            List<ModelOpt31> opts = parseModelOpts31(o.optJSONArray("items"));
            modelOptionCount31 = opts.size();
            modelEnabledCount31 = 0;
            int selectedCount = 0;
            ModelOpt31 selected = null;
            ModelOpt31 fallbackMatch = null;
            for (ModelOpt31 x : opts) {
                if (x.enabled) modelEnabledCount31++;
                if (x.selected) { selectedCount++; selected = x; }
                if (triggerMatches31(triggerLabel31, x.label)) fallbackMatch = x;
            }
            modelSetHash31 = o.optString("set_hash", "-");
            if (selectedCount == 0 && fallbackMatch != null) { selectedCount = 1; selected = fallbackMatch; }

            JSONObject s = baseState31();
            put31(s, "model_option_count", modelOptionCount31);
            put31(s, "model_enabled_count", modelEnabledCount31);
            put31(s, "model_selected_count", selectedCount);
            put31(s, "model_set_hash", modelSetHash31);
            put31(s, "menu_complete", o.optBoolean("complete", false));
            if (!o.optBoolean("success", false) || !o.optBoolean("complete", false) || modelOptionCount31 < 1) {
                phase31("MODEL_OPTIONS_CENSUS", "FAIL_MODEL_OPTIONS_UNRESOLVED", s);
                closeModelMenu31(() -> finish31("MODEL_OPTIONS_UNRESOLVED"));
                return;
            }
            phase31("MODEL_OPTIONS_CENSUS", "PASS_MODEL_OPTIONS_ENUMERATED", s);

            ModelOpt31 target = null;
            if (selectedCount == 1 && selected != null && selected.enabled) {
                for (ModelOpt31 x : opts) {
                    if (x.enabled && !x.hash.equals(selected.hash) && safeModelCandidate31(x.label)) { target = x; break; }
                }
            }
            if (selectedCount == 1 && selected != null) {
                originalLabel31 = selected.label;
                originalHash31 = selected.hash;
            }
            if (target != null) {
                targetLabel31 = target.label;
                targetHash31 = target.hash;
            }
            JSONObject plan = baseState31();
            put31(plan, "selection_applicable", target != null && !originalHash31.equals("-"));
            put31(plan, "original_model_hash", originalHash31);
            put31(plan, "target_model_hash", targetHash31);
            phase31("MODEL_SELECTION_PLAN",
                    target != null && !originalHash31.equals("-") ? "PASS_UNIQUE_BASELINE_AND_ALTERNATE" : "ENUMERATION_ONLY_NO_SAFE_ROUNDTRIP", plan);
            closeModelMenu31(() -> h31.postDelayed(this::censusAddSurface31, 250L));
        });
    }

    private void censusAddSurface31() {
        setStatus31("Enumerating add/tools surfaces...");
        eval31(surfaceTriggerJs31("add", false), tr -> {
            int count = tr.optInt("count", 0);
            JSONObject s = baseState31(); put31(s, "add_trigger_count", count);
            if (count != 1) {
                phase31("ADD_TRIGGER_CENSUS", count == 0 ? "ABSENT" : "AMBIGUOUS_FAIL_CLOSED", s);
                censusToolsSurface31();
                return;
            }
            eval31(surfaceTriggerJs31("add", true), clicked -> {
                if (!clicked.optBoolean("clicked", false)) { censusToolsSurface31(); return; }
                h31.postDelayed(() -> eval31(surfaceMenuJs31(), menu -> {
                    addItemCount31 = menu.optInt("item_count", 0);
                    addSetHash31 = menu.optString("set_hash", "-");
                    JSONObject x = baseState31();
                    put31(x, "add_item_count", addItemCount31);
                    put31(x, "add_set_hash", addSetHash31);
                    phase31("ADD_SURFACE_CENSUS", menu.optBoolean("success", false) ? "CAPTURED" : "UNRESOLVED", x);
                    eval31(surfaceTriggerJs31("add", true), ignored -> h31.postDelayed(this::censusToolsSurface31, 220L));
                }), 320L);
            });
        });
    }

    private void censusToolsSurface31() {
        eval31(surfaceTriggerJs31("tools", false), tr -> {
            toolsTriggerCount31 = tr.optInt("count", 0);
            JSONObject s = baseState31(); put31(s, "tools_trigger_count", toolsTriggerCount31);
            if (toolsTriggerCount31 != 1) {
                phase31("TOOLS_TRIGGER_CENSUS", toolsTriggerCount31 == 0 ? "ABSENT_ADD_SURFACE_IS_PRIMARY" : "AMBIGUOUS_FAIL_CLOSED", s);
                afterEnumeration31();
                return;
            }
            phase31("TOOLS_TRIGGER_CENSUS", "PASS_UNIQUE_TOOLS_TRIGGER", s);
            eval31(surfaceTriggerJs31("tools", true), clicked -> {
                if (!clicked.optBoolean("clicked", false)) { afterEnumeration31(); return; }
                h31.postDelayed(() -> eval31(surfaceMenuJs31(), menu -> {
                    toolsItemCount31 = menu.optInt("item_count", 0);
                    toolsSetHash31 = menu.optString("set_hash", "-");
                    JSONObject x = baseState31();
                    put31(x, "tools_item_count", toolsItemCount31);
                    put31(x, "tools_set_hash", toolsSetHash31);
                    phase31("TOOLS_SURFACE_CENSUS", menu.optBoolean("success", false) ? "CAPTURED" : "UNRESOLVED", x);
                    eval31(surfaceTriggerJs31("tools", true), ignored -> h31.postDelayed(this::afterEnumeration31, 220L));
                }), 320L);
            });
        });
    }

    private void afterEnumeration31() {
        JSONObject s = baseState31();
        put31(s, "tool_surface_item_total", addItemCount31 + toolsItemCount31);
        phase31("ENUMERATION_COMPLETE", "PASS_MODEL_AND_TOOL_SURFACES_CENSUSED", s);
        if (originalHash31.equals("-") || targetHash31.equals("-")) {
            finish31("PASS_ENUMERATION_MODEL_ROUNDTRIP_NOT_APPLICABLE");
            return;
        }
        selectTarget31();
    }

    private void selectTarget31() {
        setStatus31("Guarded model switch 1/2...");
        if (!durableClaim31("MODEL_SELECT_TARGET", targetHash31)) { finish31("MODEL_TARGET_CLAIM_FAILED"); return; }
        ensureModelMenuOpen31(open -> {
            if (!open) { abortNoSideEffect31("TARGET_MENU_OPEN_FAIL"); finish31("MODEL_TARGET_NOT_DISPATCHED"); return; }
            eval31(clickModelOptionJs31(targetLabel31), r -> {
                if (!r.optBoolean("success", false) || r.optInt("matches", -1) != 1 || !r.optBoolean("clicked", false)) {
                    abortNoSideEffect31("TARGET_MATCHES_" + r.optInt("matches", -1));
                    closeModelMenu31(() -> finish31("MODEL_TARGET_NOT_DISPATCHED"));
                    return;
                }
                selectionClicks31++;
                claimStatus31 = "DISPATCHED";
                prefs31.edit().putString("claim_status", claimStatus31).commit();
                phase31("MODEL_TARGET_DISPATCH", "DISPATCHED_UNIQUE_OPTION_CLICK", baseState31());
                verifySelected31(targetHash31, 7000L, ok -> {
                    if (!ok) { uncertain31("MODEL_SELECT_TARGET"); finish31("MODEL_TARGET_RECEIPT_TIMEOUT_UNCERTAIN_NO_REPLAY"); return; }
                    confirmClaim31("TARGET_SELECTED_CONFIRMED");
                    phase31("MODEL_TARGET_RECEIPT", "PASS_TARGET_SELECTED", baseState31());
                    restoreOriginal31();
                });
            });
        });
    }

    private void restoreOriginal31() {
        setStatus31("Guarded model restore 2/2...");
        if (!durableClaim31("MODEL_RESTORE_ORIGINAL", originalHash31)) { finish31("MODEL_RESTORE_CLAIM_FAILED"); return; }
        ensureModelMenuOpen31(open -> {
            if (!open) { abortNoSideEffect31("RESTORE_MENU_OPEN_FAIL"); finish31("MODEL_RESTORE_NOT_DISPATCHED"); return; }
            eval31(clickModelOptionJs31(originalLabel31), r -> {
                if (!r.optBoolean("success", false) || r.optInt("matches", -1) != 1 || !r.optBoolean("clicked", false)) {
                    abortNoSideEffect31("RESTORE_MATCHES_" + r.optInt("matches", -1));
                    closeModelMenu31(() -> finish31("MODEL_RESTORE_NOT_DISPATCHED"));
                    return;
                }
                selectionClicks31++;
                claimStatus31 = "DISPATCHED";
                prefs31.edit().putString("claim_status", claimStatus31).commit();
                phase31("MODEL_RESTORE_DISPATCH", "DISPATCHED_UNIQUE_OPTION_CLICK", baseState31());
                verifySelected31(originalHash31, 7000L, ok -> {
                    if (!ok) { uncertain31("MODEL_RESTORE_ORIGINAL"); finish31("MODEL_RESTORE_RECEIPT_TIMEOUT_UNCERTAIN_NO_REPLAY"); return; }
                    confirmClaim31("ORIGINAL_RESTORED_CONFIRMED");
                    phase31("MODEL_RESTORE_RECEIPT", "PASS_ORIGINAL_RESTORED", baseState31());
                    finish31(selectionClicks31 == 2
                            ? "PASS_MODEL_TOOL_ENUMERATION_AND_GUARDED_MODEL_ROUNDTRIP"
                            : "FAIL_UNEXPECTED_SELECTION_CLICK_COUNT");
                });
            });
        });
    }

    private void verifySelected31(String expectedHash, long timeoutMs, BoolDone31 done) {
        long deadline = System.currentTimeMillis() + timeoutMs;
        verifySelectedLoop31(expectedHash, deadline, done);
    }

    private void verifySelectedLoop31(String expectedHash, long deadline, BoolDone31 done) {
        if (!running31) { done.done(false); return; }
        ensureModelMenuOpen31(open -> {
            if (!open) {
                if (System.currentTimeMillis() >= deadline) done.done(false);
                else h31.postDelayed(() -> verifySelectedLoop31(expectedHash, deadline, done), 300L);
                return;
            }
            eval31(modelMenuJs31(), menu -> {
                JSONArray a = menu.optJSONArray("items");
                int sel = 0; String sh = "-";
                if (a != null) for (int i = 0; i < a.length(); i++) {
                    JSONObject x = a.optJSONObject(i);
                    if (x != null && x.optBoolean("selected", false)) { sel++; sh = x.optString("hash", "-"); }
                }
                boolean ok = menu.optBoolean("success", false) && menu.optBoolean("complete", false)
                        && sel == 1 && expectedHash.equals(sh);
                closeModelMenu31(() -> {
                    if (ok) done.done(true);
                    else if (System.currentTimeMillis() >= deadline) done.done(false);
                    else h31.postDelayed(() -> verifySelectedLoop31(expectedHash, deadline, done), 350L);
                });
            });
        });
    }

    private void openModelMenu31(BoolDone31 done) {
        eval31(modelTriggerJs31(true), o -> done.done(o.optBoolean("success", false)
                && o.optInt("count", -1) == 1 && o.optBoolean("clicked", false)));
    }

    private void ensureModelMenuOpen31(BoolDone31 done) {
        eval31(modelMenuJs31(), o -> {
            if (o.optBoolean("success", false) && o.optInt("item_count", 0) > 0) { done.done(true); return; }
            openModelMenu31(ok -> {
                if (!ok) { done.done(false); return; }
                h31.postDelayed(() -> eval31(modelMenuJs31(), m -> done.done(m.optBoolean("success", false)
                        && m.optInt("item_count", 0) > 0)), 320L);
            });
        });
    }

    private void closeModelMenu31(Runnable done) {
        eval31(modelMenuJs31(), menu -> {
            if (!menu.optBoolean("success", false) || menu.optInt("item_count", 0) == 0) { done.run(); return; }
            eval31(modelTriggerJs31(true), ignored -> h31.postDelayed(done, 180L));
        });
    }

    private boolean durableClaim31(String action, String targetHash) {
        String id = action + "_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0, 8);
        boolean ok = prefs31.edit().putString("claim_id", id).putString("claim_action", action)
                .putString("claim_status", "CLAIMED").putString("claim_target_hash", targetHash).commit();
        if (!ok) return false;
        claimAction31 = action; claimStatus31 = "CLAIMED";
        phase31(action + "_CLAIM", "DURABLE_CLAIMED", baseState31());
        return true;
    }

    private void confirmClaim31(String receipt) {
        claimStatus31 = "CONFIRMED";
        prefs31.edit().putString("claim_status", claimStatus31).putString("claim_receipt", receipt).commit();
    }

    private void abortNoSideEffect31(String why) {
        claimStatus31 = "ABORTED_NO_SIDE_EFFECT_" + token31(why);
        prefs31.edit().putString("claim_status", claimStatus31).commit();
    }

    private void uncertain31(String action) {
        claimAction31 = action; claimStatus31 = "UNCERTAIN_NO_REPLAY";
        prefs31.edit().putString("claim_status", claimStatus31).commit();
        phase31("UNCERTAIN_BOUNDARY", "UNCERTAIN_NO_REPLAY", baseState31());
    }

    private List<ModelOpt31> parseModelOpts31(JSONArray a) {
        List<ModelOpt31> out = new ArrayList<>();
        if (a == null) return out;
        for (int i = 0; i < a.length(); i++) {
            JSONObject o = a.optJSONObject(i); if (o == null) continue;
            String label = o.optString("label", "");
            if (label.isEmpty()) continue;
            out.add(new ModelOpt31(label, o.optString("hash", "-"),
                    o.optBoolean("selected", false), o.optBoolean("enabled", false)));
        }
        return out;
    }

    private boolean safeModelCandidate31(String label) {
        String x = norm31(label).toLowerCase(Locale.US);
        if (x.length() < 1 || x.length() > 80) return false;
        return !(x.contains("upgrade") || x.contains("learn more") || x.contains("settings")
                || x.contains("manage") || x.contains("temporary chat") || x.contains("more models"));
    }

    private boolean triggerMatches31(String trigger, String option) {
        String a = norm31(trigger).toLowerCase(Locale.US), b = norm31(option).toLowerCase(Locale.US);
        return !a.isEmpty() && !b.isEmpty() && (a.equals(b) || a.contains(b) || b.contains(a));
    }

    private String modelTriggerJs31(boolean click) {
        return "(function(){try{const DO=" + (click ? "true" : "false") + ";"
                + "const N=x=>(x||'').replace(/\\s+/g,' ').trim();const L=x=>N(x).toLowerCase();"
                + "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
                + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "let all=[...document.querySelectorAll('button,[role=button]')].filter(V);let c=all.filter(e=>{const a=L(e.getAttribute('aria-label')),t=N(e.innerText||e.textContent||''),tl=L(t),hp=!!(e.getAttribute('aria-haspopup')||e.getAttribute('data-state'));return a.includes('model selector')||a==='switch model'||a.includes('model picker')||(hp&&/^(chatgpt|gpt[ -]?|o[0-9])/i.test(t)&&t.length<80);});"
                + "let label=c.length===1?N(c[0].innerText||c[0].textContent||c[0].getAttribute('aria-label')||''):'';let clicked=false;if(DO&&c.length===1){c[0].click();clicked=true;}return JSON.stringify({success:true,count:c.length,clicked:clicked,label:label,hash:label?H(L(label)):'-'});}catch(e){return JSON.stringify({success:false,count:0,clicked:false,error:String(e&&e.name||'ERR')});}})();";
    }

    private String modelMenuJs31() {
        return "(function(){try{const N=x=>(x||'').replace(/\\s+/g,' ').trim();const L=x=>N(x).toLowerCase();"
                + "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
                + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "let scopes=[...document.querySelectorAll('[role=menu],[role=listbox],[data-radix-menu-content],[data-radix-popper-content-wrapper]')].filter(V);let nodes=[];for(const s of scopes){for(const e of s.querySelectorAll('button,[role=menuitem],[role=menuitemradio],[role=option]'))if(V(e)&&!nodes.includes(e))nodes.push(e);}"
                + "const items=[];for(const e of nodes){const label=N(e.innerText||e.textContent||e.getAttribute('aria-label')||'');if(!label||label.length>120)continue;const lo=L(label);if(/^(close|cancel|more)$/.test(lo))continue;if(lo.includes('temporary chat')||lo.includes('upgrade')||lo.includes('learn more')||lo.includes('settings'))continue;const ds=L(e.getAttribute('data-state')),ac=L(e.getAttribute('aria-checked')),as=L(e.getAttribute('aria-selected')),ap=L(e.getAttribute('aria-pressed')),cur=L(e.getAttribute('aria-current'));const mark=!!e.querySelector('[data-state=checked],[aria-checked=true],[aria-selected=true],[data-selected=true],[data-testid*=check i]');const selected=ac==='true'||as==='true'||ap==='true'||cur==='true'||ds==='checked'||ds==='selected'||mark;const enabled=!e.disabled&&L(e.getAttribute('aria-disabled'))!=='true';items.push({label:label,hash:H(lo),selected:selected,enabled:enabled});}"
                + "items.sort((a,b)=>a.hash.localeCompare(b.hash));return JSON.stringify({success:true,complete:true,item_count:items.length,set_hash:H(items.map(x=>x.hash+':'+(x.enabled?'1':'0')).join('|')),items:items});}catch(e){return JSON.stringify({success:false,complete:false,item_count:0,error:String(e&&e.name||'ERR'),items:[]});}})();";
    }

    private String clickModelOptionJs31(String label) {
        String q = JSONObject.quote(norm31(label));
        return "(function(){try{const T=" + q + ";const N=x=>(x||'').replace(/\\s+/g,' ').trim();const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};let scopes=[...document.querySelectorAll('[role=menu],[role=listbox],[data-radix-menu-content],[data-radix-popper-content-wrapper]')].filter(V);let c=[];for(const s of scopes){for(const e of s.querySelectorAll('button,[role=menuitem],[role=menuitemradio],[role=option]'))if(V(e)&&N(e.innerText||e.textContent||e.getAttribute('aria-label')||'')===T&&!c.includes(e))c.push(e);}let clicked=false;if(c.length===1&&!c[0].disabled&&String(c[0].getAttribute('aria-disabled')||'').toLowerCase()!=='true'){c[0].click();clicked=true;}return JSON.stringify({success:true,matches:c.length,clicked:clicked});}catch(e){return JSON.stringify({success:false,matches:0,clicked:false,error:String(e&&e.name||'ERR')});}})();";
    }

    private String surfaceTriggerJs31(String kind, boolean click) {
        String k = JSONObject.quote(kind);
        return "(function(){try{const K=" + k + ",DO=" + (click ? "true" : "false") + ";const N=x=>(x||'').replace(/\\s+/g,' ').trim().toLowerCase();const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};let all=[...document.querySelectorAll('button,[role=button]')].filter(V);let c=all.filter(e=>{const a=N(e.getAttribute('aria-label')),t=N(e.innerText||e.textContent),d=N(e.getAttribute('data-testid'));if(K==='tools')return a==='tools'||a.includes('tools')||t==='tools';return a.includes('add files')||a.includes('attach file')||a.includes('attachments')||d.includes('composer-menu')||d.includes('attach');});let clicked=false;if(DO&&c.length===1){c[0].click();clicked=true;}return JSON.stringify({success:true,count:c.length,clicked:clicked});}catch(e){return JSON.stringify({success:false,count:0,clicked:false,error:String(e&&e.name||'ERR')});}})();";
    }

    private String surfaceMenuJs31() {
        return "(function(){try{const N=x=>(x||'').replace(/\\s+/g,' ').trim();const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};let scopes=[...document.querySelectorAll('[role=menu],[role=listbox],[data-radix-menu-content],[data-radix-popper-content-wrapper]')].filter(V);let hs=[];for(const s of scopes){for(const e of s.querySelectorAll('button,[role=menuitem],[role=option]')){if(!V(e))continue;const t=N(e.innerText||e.textContent||e.getAttribute('aria-label')||'');if(t&&t.length<=160){const h=H(t.toLowerCase());if(!hs.includes(h))hs.push(h);}}}hs.sort();return JSON.stringify({success:true,item_count:hs.length,set_hash:H(hs.join('|'))});}catch(e){return JSON.stringify({success:false,item_count:0,set_hash:'-',error:String(e&&e.name||'ERR')});}})();";
    }

    private void eval31(String js, JsonDone31 done) {
        if (web31 == null) { done.done(new JSONObject()); return; }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> { if (once.compareAndSet(false, true)) done.done(new JSONObject()); };
        h31.postDelayed(timeout, EVAL_TIMEOUT_MS);
        web31.evaluateJavascript(js, value -> {
            if (!once.compareAndSet(false, true)) return;
            h31.removeCallbacks(timeout);
            try { done.done(json31(value)); } catch (Exception e) { done.done(new JSONObject()); }
        });
    }

    private JSONObject json31(String value) throws Exception {
        Object x = new JSONTokener(value == null ? "null" : value).nextValue();
        if (x instanceof String) x = new JSONTokener((String) x).nextValue();
        if (!(x instanceof JSONObject)) throw new IllegalStateException("not_object");
        return (JSONObject) x;
    }

    private JSONObject baseState31() {
        JSONObject s = new JSONObject();
        put31(s, "session_state", parentString31("sessionState"));
        put31(s, "mic_lease_mode", parentString31("micLeaseMode"));
        put31(s, "claim_action", claimAction31);
        put31(s, "claim_status", claimStatus31);
        put31(s, "selection_clicks", selectionClicks31);
        put31(s, "model_trigger_hash", triggerHash31);
        put31(s, "original_model_hash", originalHash31);
        put31(s, "target_model_hash", targetHash31);
        put31(s, "model_option_count", modelOptionCount31);
        put31(s, "model_enabled_count", modelEnabledCount31);
        put31(s, "model_set_hash", modelSetHash31);
        put31(s, "add_item_count", addItemCount31);
        put31(s, "add_set_hash", addSetHash31);
        put31(s, "tools_trigger_count", toolsTriggerCount31);
        put31(s, "tools_item_count", toolsItemCount31);
        put31(s, "tools_set_hash", toolsSetHash31);
        put31(s, "raw_model_labels_uploaded", false);
        put31(s, "raw_tool_labels_uploaded", false);
        put31(s, "raw_chat_text_uploaded", false);
        put31(s, "raw_html_uploaded", false);
        put31(s, "cookies_tokens_accessed", false);
        return s;
    }

    private void phase31(String phase, String classification, JSONObject state) {
        if (!running31) return;
        prefs31.edit().putString("phase", phase).commit();
        JSONObject p = payload31(phase, classification, state, seq31++);
        if (telemetryHealthy31 && TelemetryConfigV31.isConfigured()) {
            new Thread(() -> upload31(p, NET_TIMEOUT_MS), "cp31-phase").start();
        }
    }

    private JSONObject payload31(String phase, String classification, JSONObject state, int seq) {
        JSONObject p = new JSONObject();
        put31(p, "schema_version", SCHEMA31);
        put31(p, "scenario_id", SCENARIO31);
        put31(p, "source_ref", TelemetryConfigV31.SOURCE_REF);
        put31(p, "collector_id", TelemetryConfigV31.COLLECTOR_ID);
        put31(p, "test_id", testId31);
        put31(p, "seq", seq);
        put31(p, "timestamp_epoch_ms", System.currentTimeMillis());
        put31(p, "phase", phase);
        put31(p, "classification", classification);
        try { p.put("state", state == null ? new JSONObject() : state); } catch (Exception ignored) {}
        return p;
    }

    private JSONObject upload31(JSONObject body, int timeoutMs) {
        JSONObject out = new JSONObject();
        if (!TelemetryConfigV31.isConfigured()) { put31(out, "success", false); return out; }
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(TelemetryConfigV31.WEBHOOK_URL).openConnection();
            c.setConnectTimeout(timeoutMs); c.setReadTimeout(timeoutMs); c.setRequestMethod("POST"); c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/json");
            byte[] b = body.toString().getBytes(StandardCharsets.UTF_8);
            try (OutputStream os = c.getOutputStream()) { os.write(b); }
            int code = c.getResponseCode(); put31(out, "success", code >= 200 && code < 300); put31(out, "code", code);
        } catch (Exception e) { put31(out, "success", false); put31(out, "error", e.getClass().getSimpleName()); }
        finally { if (c != null) c.disconnect(); }
        return out;
    }

    private void finish31(String classification) {
        if (!running31) return;
        finalClassification31 = classification;
        phase31("FINAL", classification, baseState31());
        writeLocal31(classification);
        running31 = false;
        prefs31.edit().putBoolean("running", false).putString("phase", "FINAL").putString("final", classification).commit();
        h31.removeCallbacks(watchdog31);
        setStatus31("v0.31 finished: " + classification);
        if (run31 != null) { run31.setEnabled(true); run31.setText("RUN MODEL / TOOLS TEST"); }
    }

    private void onWatchdog31() {
        if (!running31) return;
        if ("DISPATCHED".equals(claimStatus31)) uncertain31(claimAction31);
        finish31("GLOBAL_WATCHDOG_RECOVERED_NO_REPLAY");
    }

    private void reportInterrupted31() {
        if (prefs31 == null || !prefs31.getBoolean("running", false)) return;
        prefs31.edit().putBoolean("running", false).putString("phase", "INTERRUPTED_RESTART_NO_REPLAY").commit();
        setStatus31("Previous v0.31 run interrupted; no action replayed.");
    }

    private void writeLocal31(String classification) {
        try {
            JSONObject o = baseState31(); put31(o, "test_id", testId31); put31(o, "final", classification);
            put31(o, "source_ref", TelemetryConfigV31.SOURCE_REF);
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.Downloads.DISPLAY_NAME, "chatgpt-webview-v31-" + testId31 + ".json");
            cv.put(MediaStore.Downloads.MIME_TYPE, "application/json");
            cv.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (u != null) try (OutputStream os = getContentResolver().openOutputStream(u)) {
                if (os != null) os.write(o.toString(2).getBytes(StandardCharsets.UTF_8));
            }
        } catch (Exception ignored) {}
    }

    private String parentString31(String name) {
        try { Object x = field31(name); return x == null ? "-" : String.valueOf(x); }
        catch (Exception e) { return "-"; }
    }

    private Object field31(String name) throws Exception {
        Class<?> c = getClass();
        while (c != null) {
            try { Field f = c.getDeclaredField(name); f.setAccessible(true); return f.get(this); }
            catch (NoSuchFieldException e) { c = c.getSuperclass(); }
        }
        throw new NoSuchFieldException(name);
    }

    private WebView findWeb31(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (!(v instanceof ViewGroup)) return null;
        ViewGroup g = (ViewGroup) v;
        for (int i = 0; i < g.getChildCount(); i++) { WebView w = findWeb31(g.getChildAt(i)); if (w != null) return w; }
        return null;
    }

    private boolean trusted31(String raw) {
        try { Uri u = Uri.parse(raw == null ? "" : raw); String h = u.getHost(); return "https".equalsIgnoreCase(u.getScheme()) && h != null && (h.equals("chatgpt.com") || h.endsWith(".chatgpt.com")); }
        catch (Exception e) { return false; }
    }

    private void setStatus31(String s) { if (status31 != null) status31.setText(s); }
    private int dp31(int x) { return Math.max(1, Math.round(x * getResources().getDisplayMetrics().density)); }
    private String norm31(String s) { return s == null ? "" : s.replaceAll("\\s+", " ").trim(); }
    private String token31(String s) { String x = s == null ? "-" : s.replaceAll("[^A-Za-z0-9_.:+/-]", "_"); return x.length() > 90 ? x.substring(0, 90) : x; }
    private void put31(JSONObject o, String k, Object v) { try { o.put(k, v); } catch (Exception ignored) {} }
}
