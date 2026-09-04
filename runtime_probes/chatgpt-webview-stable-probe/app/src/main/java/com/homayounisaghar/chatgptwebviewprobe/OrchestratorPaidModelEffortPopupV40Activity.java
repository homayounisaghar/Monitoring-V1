package com.homayounisaghar.chatgptwebviewprobe;

import android.content.SharedPreferences;
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
 * Stable v0.38 — guarded composer-effort popup round-trip.
 *
 * Evidence from v0.37 proved exactly one stable composer effort selector while Medium,
 * with aria-haspopup/aria-expanded semantics. This build derives all writes from that
 * control. Every potentially state-changing click is preceded by a durable claim.
 * It opens the effort popup, requires exactly one enabled Light and one enabled Medium
 * option in one bounded popup group, selects Light, verifies the composer receipt,
 * reopens the selector, restores Medium, and verifies the final receipt.
 *
 * Any unresolved/ambiguous state fails closed. After a dispatched click, ambiguity is
 * classified UNCERTAIN_NO_REPLAY and is never blindly replayed.
 */
public class OrchestratorPaidModelEffortPopupV40Activity extends OrchestratorAuthModeV34Activity {
    private static final String SCHEMA40 = "cp-v40-paid-model-effort-popup-v1";
    private static final String SCENARIO40 = "paid-model-effort-popup-guarded-roundtrip";
    private static final long EVAL_TIMEOUT_MS40 = 3000L;
    private static final int NET_TIMEOUT_MS40 = 3200;
    private static final long POPUP_TIMEOUT_MS40 = 7000L;
    private static final long RECEIPT_TIMEOUT_MS40 = 8000L;
    private static final long GLOBAL_WATCHDOG_MS40 = 42000L;

    private final Handler h40 = new Handler(Looper.getMainLooper());
    private WebView web40;
    private TextView status40;
    private Button run40;
    private SharedPreferences prefs40;

    private boolean running40 = false;
    private boolean telemetryHealthy40 = false;
    private String testId40 = "-";
    private int seq40 = 0;
    private long startedAt40 = 0L;
    private int uiClicks40 = 0;
    private int modelClicks40 = 0;

    private String claimAction40 = "NONE";
    private String claimStatus40 = "NONE";
    private String baselineHash40 = "-";
    private String currentControlHash40 = "-";
    private String targetOptionHash40 = "-";
    private String restoreOptionHash40 = "-";
    private String popupGroupHash40 = "-";

    private interface JsonDone40 { void done(JSONObject o); }
    private interface BoolDone40 { void done(boolean ok); }
    private interface PopupDone40 { void done(JSONObject popup); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs40 = getSharedPreferences("cp40_paid_model_effort_popup", MODE_PRIVATE);
        web40 = findWeb40(getWindow().getDecorView());
        installCompactUi40();
        String prior = prefs40.getString("claim_status", "NONE");
        if (isUnresolved40(prior)) {
            setStatus40("Blocked: unresolved prior claim — no replay");
            if (run40 != null) run40.setEnabled(false);
        } else {
            setStatus40("v0.38 guarded Medium -> Light -> Medium ready");
        }
    }

    @Override protected void onDestroy() {
        h40.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private void installCompactUi40() {
        if (web40 == null) return;
        ViewParent p = web40.getParent();
        if (!(p instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) p;
        for (int i = 0; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            if (child != web40) child.setVisibility(View.GONE);
        }
        web40.setMinimumHeight(1);
        web40.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp40(8), dp40(3), dp40(8), dp40(6));

        status40 = new TextView(this);
        status40.setTextSize(11f);
        status40.setSingleLine(true);
        status40.setEllipsize(TextUtils.TruncateAt.END);
        panel.addView(status40, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));

        run40 = new Button(this);
        run40.setText("RUN GUARDED EFFORT ROUND-TRIP");
        run40.setTextSize(13f);
        run40.setAllCaps(false);
        run40.setOnClickListener(v -> runRoundTrip40());
        panel.addView(run40, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp40(46)));

        root.addView(panel, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void runRoundTrip40() {
        if (running40) return;
        String prior = prefs40.getString("claim_status", "NONE");
        if (isUnresolved40(prior)) {
            setStatus40("Blocked: unresolved prior claim — no replay");
            return;
        }
        if (web40 == null || !isChatGpt40(web40.getUrl())) {
            setStatus40("Blocked: ChatGPT page not ready");
            return;
        }

        running40 = true;
        telemetryHealthy40 = false;
        testId40 = "cp40-" + UUID.randomUUID();
        seq40 = 0;
        startedAt40 = System.currentTimeMillis();
        uiClicks40 = 0;
        modelClicks40 = 0;
        claimAction40 = "NONE";
        claimStatus40 = "NONE";
        baselineHash40 = currentControlHash40 = targetOptionHash40 = restoreOptionHash40 = popupGroupHash40 = "-";
        if (run40 != null) {
            run40.setEnabled(false);
            run40.setText("EFFORT ROUND-TRIP RUNNING...");
        }
        setStatus40("Telemetry preflight...");
        h40.postDelayed(this::watchdog40, GLOBAL_WATCHDOG_MS40);
        telemetryPreflight40();
    }

    private void telemetryPreflight40() {
        JSONObject p = payload40("TELEMETRY_PREFLIGHT", "RUNNING", baseState40());
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (!running40 || !once.compareAndSet(false, true)) return;
            finish40("TELEMETRY_PREFLIGHT_TIMEOUT");
        };
        h40.postDelayed(timeout, 8000L);
        new Thread(() -> {
            JSONObject r = upload40(p, NET_TIMEOUT_MS40 + 900);
            runOnUiThread(() -> {
                if (!running40 || !once.compareAndSet(false, true)) return;
                h40.removeCallbacks(timeout);
                if (!r.optBoolean("success", false)) {
                    finish40("TELEMETRY_UNAVAILABLE");
                    return;
                }
                telemetryHealthy40 = true;
                phase40("RUN_STARTED", "GUARDED_COMPOSER_EFFORT_POPUP", baseState40());
                resolveBaseline40();
            });
        }, "cp40-preflight").start();
    }

    private void resolveBaseline40() {
        setStatus40("Resolving Medium selector...");
        eval40(scanComposerJs40(), o -> {
            JSONObject st = composerState40(o);
            boolean ok = o.optBoolean("success", false) && o.optBoolean("complete", false)
                    && o.optInt("effort_control_count", -1) == 1
                    && "MEDIUM".equals(o.optString("effort_semantic", ""))
                    && o.optBoolean("effort_has_popup", false)
                    && !"-".equals(o.optString("effort_control_hash", "-"));
            if (!ok) {
                phase40("BASELINE_COMPOSER_EFFORT", "FAIL_CLOSED_UNRESOLVED", st);
                finish40("BASELINE_MEDIUM_SELECTOR_UNRESOLVED_ZERO_CLICK");
                return;
            }
            baselineHash40 = o.optString("effort_control_hash", "-");
            currentControlHash40 = baselineHash40;
            phase40("BASELINE_COMPOSER_EFFORT", "PASS_UNIQUE_MEDIUM_SELECTOR", st);
            openTargetMenu40();
        });
    }

    private void openTargetMenu40() {
        setStatus40("Claim -> open Medium selector...");
        if (!durableClaim40("EFFORT_MENU_OPEN_TARGET", currentControlHash40, "MEDIUM")) {
            finish40("OPEN_TARGET_MENU_CLAIM_FAILED_ZERO_CLICK");
            return;
        }
        eval40(clickComposerEffortJs40(currentControlHash40, "MEDIUM"), r -> {
            int matches = r.optInt("matches", -1);
            boolean clicked = r.optBoolean("clicked", false);
            if (!r.optBoolean("success", false) || matches != 1 || !clicked) {
                abortNoSideEffect40("OPEN_TARGET_MATCHES_" + matches);
                phase40("EFFORT_MENU_OPEN_TARGET_DISPATCH", "ABORTED_NO_SIDE_EFFECT", baseState40());
                finish40("OPEN_TARGET_MENU_NOT_DISPATCHED");
                return;
            }
            uiClicks40++;
            markDispatched40();
            phase40("EFFORT_MENU_OPEN_TARGET_DISPATCH", "DISPATCHED_UNIQUE_COMPOSER_SELECTOR", baseState40());
            waitForPopup40("MEDIUM", System.currentTimeMillis() + POPUP_TIMEOUT_MS40, popup -> {
                if (popup == null) {
                    uncertain40("EFFORT_MENU_OPEN_TARGET");
                    finish40("TARGET_POPUP_RECEIPT_TIMEOUT_UNCERTAIN_NO_REPLAY");
                    return;
                }
                confirmClaim40("TARGET_POPUP_OPEN_CONFIRMED");
                popupGroupHash40 = popup.optString("group_hash", "-");
                targetOptionHash40 = optionHash40(popup.optJSONArray("options"), "LIGHT");
                restoreOptionHash40 = optionHash40(popup.optJSONArray("options"), "MEDIUM");
                JSONObject st = popupState40(popup);
                phase40("EFFORT_TARGET_POPUP_CENSUS", "PASS_UNIQUE_LIGHT_MEDIUM_POPUP", st);
                if ("-".equals(targetOptionHash40) || "-".equals(restoreOptionHash40)
                        || targetOptionHash40.equals(restoreOptionHash40)) {
                    finish40("TARGET_POPUP_OPTION_MAPPING_UNRESOLVED");
                    return;
                }
                selectLight40();
            });
        });
    }

    private void selectLight40() {
        setStatus40("Claim -> select Light...");
        if (!durableClaim40("MODEL_EFFORT_SELECT_LIGHT", targetOptionHash40, "LIGHT")) {
            finish40("LIGHT_CLAIM_FAILED");
            return;
        }
        eval40(clickPopupOptionJs40(targetOptionHash40, "LIGHT"), r -> {
            int matches = r.optInt("matches", -1);
            boolean clicked = r.optBoolean("clicked", false);
            if (!r.optBoolean("success", false) || matches != 1 || !clicked) {
                abortNoSideEffect40("LIGHT_MATCHES_" + matches);
                phase40("MODEL_EFFORT_LIGHT_DISPATCH", "ABORTED_NO_SIDE_EFFECT", baseState40());
                finish40("LIGHT_NOT_DISPATCHED");
                return;
            }
            uiClicks40++;
            modelClicks40++;
            markDispatched40();
            phase40("MODEL_EFFORT_LIGHT_DISPATCH", "DISPATCHED_UNIQUE_LIGHT_OPTION", baseState40());
            verifyComposerSemantic40("LIGHT", System.currentTimeMillis() + RECEIPT_TIMEOUT_MS40, ok -> {
                if (!ok) {
                    uncertain40("MODEL_EFFORT_SELECT_LIGHT");
                    finish40("LIGHT_RECEIPT_TIMEOUT_UNCERTAIN_NO_REPLAY");
                    return;
                }
                confirmClaim40("LIGHT_SELECTED_CONFIRMED");
                phase40("MODEL_EFFORT_LIGHT_RECEIPT", "PASS_LIGHT_SELECTED", baseState40());
                reopenForRestore40();
            });
        });
    }

    private void reopenForRestore40() {
        setStatus40("Resolving Light selector for restore...");
        eval40(scanComposerJs40(), o -> {
            boolean ok = o.optBoolean("success", false) && o.optBoolean("complete", false)
                    && o.optInt("effort_control_count", -1) == 1
                    && "LIGHT".equals(o.optString("effort_semantic", ""))
                    && o.optBoolean("effort_has_popup", false)
                    && !"-".equals(o.optString("effort_control_hash", "-"));
            if (!ok) {
                phase40("RESTORE_COMPOSER_EFFORT", "FAIL_LIGHT_SELECTOR_UNRESOLVED", composerState40(o));
                finish40("RESTORE_LIGHT_SELECTOR_UNRESOLVED");
                return;
            }
            currentControlHash40 = o.optString("effort_control_hash", "-");
            if (!durableClaim40("EFFORT_MENU_OPEN_RESTORE", currentControlHash40, "LIGHT")) {
                finish40("OPEN_RESTORE_MENU_CLAIM_FAILED");
                return;
            }
            eval40(clickComposerEffortJs40(currentControlHash40, "LIGHT"), r -> {
                int matches = r.optInt("matches", -1);
                boolean clicked = r.optBoolean("clicked", false);
                if (!r.optBoolean("success", false) || matches != 1 || !clicked) {
                    abortNoSideEffect40("OPEN_RESTORE_MATCHES_" + matches);
                    phase40("EFFORT_MENU_OPEN_RESTORE_DISPATCH", "ABORTED_NO_SIDE_EFFECT", baseState40());
                    finish40("OPEN_RESTORE_MENU_NOT_DISPATCHED");
                    return;
                }
                uiClicks40++;
                markDispatched40();
                phase40("EFFORT_MENU_OPEN_RESTORE_DISPATCH", "DISPATCHED_UNIQUE_COMPOSER_SELECTOR", baseState40());
                waitForPopup40("LIGHT", System.currentTimeMillis() + POPUP_TIMEOUT_MS40, popup -> {
                    if (popup == null) {
                        uncertain40("EFFORT_MENU_OPEN_RESTORE");
                        finish40("RESTORE_POPUP_RECEIPT_TIMEOUT_UNCERTAIN_NO_REPLAY");
                        return;
                    }
                    confirmClaim40("RESTORE_POPUP_OPEN_CONFIRMED");
                    popupGroupHash40 = popup.optString("group_hash", "-");
                    String mediumHash = optionHash40(popup.optJSONArray("options"), "MEDIUM");
                    if ("-".equals(mediumHash)) {
                        phase40("EFFORT_RESTORE_POPUP_CENSUS", "FAIL_MEDIUM_OPTION_UNRESOLVED", popupState40(popup));
                        finish40("RESTORE_MEDIUM_OPTION_UNRESOLVED");
                        return;
                    }
                    restoreOptionHash40 = mediumHash;
                    phase40("EFFORT_RESTORE_POPUP_CENSUS", "PASS_UNIQUE_MEDIUM_OPTION", popupState40(popup));
                    restoreMedium40();
                });
            });
        });
    }

    private void restoreMedium40() {
        setStatus40("Claim -> restore Medium...");
        if (!durableClaim40("MODEL_EFFORT_RESTORE_MEDIUM", restoreOptionHash40, "MEDIUM")) {
            finish40("MEDIUM_RESTORE_CLAIM_FAILED");
            return;
        }
        eval40(clickPopupOptionJs40(restoreOptionHash40, "MEDIUM"), r -> {
            int matches = r.optInt("matches", -1);
            boolean clicked = r.optBoolean("clicked", false);
            if (!r.optBoolean("success", false) || matches != 1 || !clicked) {
                abortNoSideEffect40("MEDIUM_RESTORE_MATCHES_" + matches);
                phase40("MODEL_EFFORT_MEDIUM_RESTORE_DISPATCH", "ABORTED_NO_SIDE_EFFECT", baseState40());
                finish40("MEDIUM_RESTORE_NOT_DISPATCHED");
                return;
            }
            uiClicks40++;
            modelClicks40++;
            markDispatched40();
            phase40("MODEL_EFFORT_MEDIUM_RESTORE_DISPATCH", "DISPATCHED_UNIQUE_MEDIUM_OPTION", baseState40());
            verifyComposerSemantic40("MEDIUM", System.currentTimeMillis() + RECEIPT_TIMEOUT_MS40, ok -> {
                if (!ok) {
                    uncertain40("MODEL_EFFORT_RESTORE_MEDIUM");
                    finish40("MEDIUM_RESTORE_RECEIPT_TIMEOUT_UNCERTAIN_NO_REPLAY");
                    return;
                }
                confirmClaim40("MEDIUM_RESTORED_CONFIRMED");
                phase40("MODEL_EFFORT_MEDIUM_RESTORE_RECEIPT", "PASS_MEDIUM_RESTORED", baseState40());
                finish40(modelClicks40 == 2
                        ? "PASS_EFFORT_POPUP_MODEL_ROUNDTRIP_RESTORED"
                        : "FAIL_UNEXPECTED_MODEL_CLICK_COUNT");
            });
        });
    }

    private void waitForPopup40(String expectedComposerSemantic, long deadline, PopupDone40 done) {
        if (!running40) { done.done(null); return; }
        eval40(scanComposerJs40(), c -> {
            String sem = c.optString("effort_semantic", "-");
            boolean composerOk = c.optBoolean("success", false) && c.optBoolean("complete", false)
                    && c.optInt("effort_control_count", -1) == 1;
            if (!composerOk) {
                if (System.currentTimeMillis() >= deadline) { done.done(null); return; }
                h40.postDelayed(() -> waitForPopup40(expectedComposerSemantic, deadline, done), 260L);
                return;
            }
            if (!expectedComposerSemantic.equals(sem)) {
                phase40("EFFORT_MENU_OPEN_GUARD", "UNEXPECTED_COMPOSER_SEMANTIC_CHANGE", composerState40(c));
                done.done(null);
                return;
            }
            eval40(scanPopupJs40(), p -> {
                boolean ok = p.optBoolean("success", false) && p.optBoolean("complete", false)
                        && p.optBoolean("group_ok", false)
                        && p.optInt("light_count", -1) == 1
                        && p.optInt("medium_count", -1) == 1
                        && p.optInt("enabled_count", -1) >= 2
                        && !"-".equals(p.optString("group_hash", "-"));
                if (ok) { done.done(p); return; }
                if (System.currentTimeMillis() >= deadline) { done.done(null); return; }
                h40.postDelayed(() -> waitForPopup40(expectedComposerSemantic, deadline, done), 280L);
            });
        });
    }

    private void verifyComposerSemantic40(String expected, long deadline, BoolDone40 done) {
        if (!running40) { done.done(false); return; }
        eval40(scanComposerJs40(), o -> {
            boolean shape = o.optBoolean("success", false) && o.optBoolean("complete", false)
                    && o.optInt("effort_control_count", -1) == 1
                    && o.optBoolean("effort_has_popup", false);
            if (shape && expected.equals(o.optString("effort_semantic", ""))) {
                done.done(true);
                return;
            }
            if (System.currentTimeMillis() >= deadline) {
                done.done(false);
                return;
            }
            h40.postDelayed(() -> verifyComposerSemantic40(expected, deadline, done), 320L);
        });
    }

    private String optionHash40(JSONArray a, String semantic) {
        if (a == null) return "-";
        String found = "-";
        int count = 0;
        for (int i = 0; i < a.length(); i++) {
            JSONObject x = a.optJSONObject(i);
            if (x == null || !semantic.equals(x.optString("semantic", "")) || !x.optBoolean("enabled", false)) continue;
            String h = x.optString("acc_hash", "-");
            if ("-".equals(h)) continue;
            found = h;
            count++;
        }
        return count == 1 ? found : "-";
    }

    private boolean durableClaim40(String action, String targetHash, String targetSemantic) {
        String id = action + "_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0, 8);
        boolean ok = prefs40.edit()
                .putString("claim_id", id)
                .putString("claim_action", action)
                .putString("claim_status", "CLAIMED")
                .putString("claim_target_hash", targetHash)
                .putString("claim_target_semantic", targetSemantic)
                .commit();
        if (!ok) return false;
        claimAction40 = action;
        claimStatus40 = "CLAIMED";
        phase40("DURABLE_CLAIM", "CLAIMED_BEFORE_SIDE_EFFECT", baseState40());
        return true;
    }

    private void markDispatched40() {
        prefs40.edit().putString("claim_status", "DISPATCHED").commit();
        claimStatus40 = "DISPATCHED";
    }

    private void confirmClaim40(String receipt) {
        prefs40.edit().putString("claim_status", "CONFIRMED").putString("claim_receipt", receipt).commit();
        claimStatus40 = "CONFIRMED";
    }

    private void abortNoSideEffect40(String receipt) {
        prefs40.edit().putString("claim_status", "ABORTED_NO_SIDE_EFFECT").putString("claim_receipt", receipt).commit();
        claimStatus40 = "ABORTED_NO_SIDE_EFFECT";
    }

    private void uncertain40(String action) {
        prefs40.edit().putString("claim_status", "UNCERTAIN_NO_REPLAY").putString("claim_action", action).commit();
        claimAction40 = action;
        claimStatus40 = "UNCERTAIN_NO_REPLAY";
        phase40("CLAIM_UNCERTAIN", "UNCERTAIN_NO_REPLAY", baseState40());
    }

    private boolean isUnresolved40(String s) {
        return "CLAIMED".equals(s) || "DISPATCHED".equals(s) || "UNCERTAIN_NO_REPLAY".equals(s);
    }

    private void watchdog40() {
        if (!running40) return;
        String s = prefs40.getString("claim_status", "NONE");
        if ("CLAIMED".equals(s) || "DISPATCHED".equals(s)) uncertain40(prefs40.getString("claim_action", "WATCHDOG"));
        finish40("GLOBAL_WATCHDOG_STOPPED_NO_REPLAY");
    }

    private JSONObject composerState40(JSONObject o) {
        JSONObject st = baseState40();
        put40(st, "success", o.optBoolean("success", false));
        put40(st, "complete", o.optBoolean("complete", false));
        put40(st, "composer_control_count", o.optInt("composer_control_count", -1));
        put40(st, "effort_control_count", o.optInt("effort_control_count", -1));
        put40(st, "effort_semantic", o.optString("effort_semantic", "-"));
        put40(st, "effort_control_hash", o.optString("effort_control_hash", "-"));
        put40(st, "effort_has_popup", o.optBoolean("effort_has_popup", false));
        put40(st, "effort_expanded", o.optBoolean("effort_expanded", false));
        put40(st, "candidate_set_hash", o.optString("candidate_set_hash", "-"));
        return st;
    }

    private JSONObject popupState40(JSONObject o) {
        JSONObject st = baseState40();
        put40(st, "success", o.optBoolean("success", false));
        put40(st, "complete", o.optBoolean("complete", false));
        put40(st, "group_ok", o.optBoolean("group_ok", false));
        put40(st, "valid_group_count", o.optInt("valid_group_count", -1));
        put40(st, "option_count", o.optInt("option_count", -1));
        put40(st, "light_count", o.optInt("light_count", -1));
        put40(st, "medium_count", o.optInt("medium_count", -1));
        put40(st, "heavy_count", o.optInt("heavy_count", -1));
        put40(st, "auto_count", o.optInt("auto_count", -1));
        put40(st, "enabled_count", o.optInt("enabled_count", -1));
        put40(st, "selected_count", o.optInt("selected_count", -1));
        put40(st, "group_hash", o.optString("group_hash", "-"));
        put40(st, "option_set_hash", o.optString("option_set_hash", "-"));
        JSONArray a = o.optJSONArray("options");
        if (a != null) put40(st, "options", a);
        return st;
    }

    private JSONObject baseState40() {
        JSONObject st = new JSONObject();
        put40(st, "claim_action", claimAction40);
        put40(st, "claim_status", claimStatus40);
        put40(st, "baseline_hash", baselineHash40);
        put40(st, "current_control_hash", currentControlHash40);
        put40(st, "target_option_hash", targetOptionHash40);
        put40(st, "restore_option_hash", restoreOptionHash40);
        put40(st, "popup_group_hash", popupGroupHash40);
        put40(st, "ui_clicks", uiClicks40);
        put40(st, "model_clicks", modelClicks40);
        put40(st, "raw_text_uploaded", false);
        put40(st, "raw_html_uploaded", false);
        put40(st, "cookies_tokens_accessed", false);
        return st;
    }

    private String scanComposerJs40() {
        return "(function(){try{const T0=performance.now(),MAXN=6500,MAXMS=180,MAXC=16;"
                + "const N=x=>(x||'').replace(/\\s+/g,' ').trim();const L=x=>N(x).toLowerCase();"
                + "const TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean);const HAS=(s,w)=>TOK(s).includes(w);"
                + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};"
                + "let visited=0,complete=true,input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=\"true\"],[role=\"textbox\"]')){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(V(e)){input=e;break;}}"
                + "let root=null;if(input){let p=input.parentElement;for(let d=0;p&&d<9;d++,p=p.parentElement){if(performance.now()-T0>MAXMS){complete=false;break;}const cs=[...p.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio');if(cs.length>=3&&cs.length<=12){root=p;break;}}}"
                + "const nodes=root?[...root.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio'):[];let effort=0,effortHash='-',effortSemantic='-',effortPopup=false,effortExpanded=false;const fps=[];"
                + "for(const e of nodes){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(fps.length>=MAXC)break;const txt=N(e.innerText||e.textContent||''),aria=N(e.getAttribute('aria-label')),title=N(e.getAttribute('title')),acc=N(aria||title||txt),mix=acc+' '+txt;const sl=HAS(mix,'light'),sm=HAS(mix,'medium'),sh=HAS(mix,'heavy'),sa=HAS(mix,'auto');const n=(sl?1:0)+(sm?1:0)+(sh?1:0)+(sa?1:0);const sem=n===1?(sl?'LIGHT':sm?'MEDIUM':sh?'HEAVY':'AUTO'):'NONE';const pop=N(e.getAttribute('aria-haspopup')),exp=N(e.getAttribute('aria-expanded'));const ah=acc?H(L(acc)):'-';const fp=H([(e.tagName||'').toLowerCase(),sem,pop?H(L(pop)):'-',exp!==''?1:0,ah].join('|'));fps.push(fp);if(sem!=='NONE'){effort++;effortHash=ah;effortSemantic=sem;effortPopup=pop!==''&&L(pop)!=='false';effortExpanded=L(exp)==='true';}}"
                + "fps.sort();if(effort!==1){effortHash='-';effortSemantic='-';effortPopup=false;effortExpanded=false;}return JSON.stringify({success:true,complete:complete,input_found:!!input,composer_root_found:!!root,composer_control_count:nodes.length,effort_control_count:effort,effort_control_hash:effortHash,effort_semantic:effortSemantic,effort_has_popup:effortPopup,effort_expanded:effortExpanded,candidate_set_hash:H(fps.join(','))});}catch(e){return JSON.stringify({success:false,complete:false,error_class:'SCAN_EXCEPTION'});}})();";
    }

    private String clickComposerEffortJs40(String expectedHash, String expectedSemantic) {
        return "(function(){try{const EH='" + js40(expectedHash) + "',ES='" + js40(expectedSemantic) + "';"
                + "const N=x=>(x||'').replace(/\\s+/g,' ').trim();const L=x=>N(x).toLowerCase();const TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean);const HAS=(s,w)=>TOK(s).includes(w);const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};"
                + "let input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=\"true\"],[role=\"textbox\"]'))if(V(e)){input=e;break;}let root=null;if(input){let p=input.parentElement;for(let d=0;p&&d<9;d++,p=p.parentElement){const cs=[...p.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio');if(cs.length>=3&&cs.length<=12){root=p;break;}}}let matches=[];if(root){for(const e of root.querySelectorAll('button,[role=\"button\"]')){if(!V(e)||L(e.getAttribute('role'))==='radio')continue;const txt=N(e.innerText||e.textContent||''),aria=N(e.getAttribute('aria-label')),title=N(e.getAttribute('title')),acc=N(aria||title||txt),mix=acc+' '+txt;const sl=HAS(mix,'light'),sm=HAS(mix,'medium'),sh=HAS(mix,'heavy'),sa=HAS(mix,'auto');const n=(sl?1:0)+(sm?1:0)+(sh?1:0)+(sa?1:0);const sem=n===1?(sl?'LIGHT':sm?'MEDIUM':sh?'HEAVY':'AUTO'):'NONE';const ah=acc?H(L(acc)):'-';const pop=N(e.getAttribute('aria-haspopup'));if(sem===ES&&ah===EH&&pop!==''&&L(pop)!=='false'&&!(e.disabled||L(e.getAttribute('aria-disabled'))==='true'))matches.push(e);}}if(matches.length===1){matches[0].click();return JSON.stringify({success:true,matches:1,clicked:true});}return JSON.stringify({success:true,matches:matches.length,clicked:false});}catch(e){return JSON.stringify({success:false,matches:-1,clicked:false});}})();";
    }

    private String scanPopupJs40() {
        return "(function(){try{const T0=performance.now(),MAXN=9000,MAXMS=220;const N=x=>(x||'').replace(/\\s+/g,' ').trim();const L=x=>N(x).toLowerCase();const TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean);const HAS=(s,w)=>TOK(s).includes(w);const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};"
                + "let visited=0,complete=true,input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=\"true\"],[role=\"textbox\"]')){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(V(e)){input=e;break;}}let composer=null;if(input){let p=input.parentElement;for(let d=0;p&&d<9;d++,p=p.parentElement){const cs=[...p.querySelectorAll('button,[role=\"button\"]')].filter(V);if(cs.length>=3&&cs.length<=12){composer=p;break;}}}"
                + "const sel='button,[role=\"menuitem\"],[role=\"menuitemradio\"],[role=\"option\"],[role=\"radio\"]';const raw=[];for(const e of document.querySelectorAll(sel)){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(!V(e)||(composer&&composer.contains(e)))continue;const txt=N(e.innerText||e.textContent||''),aria=N(e.getAttribute('aria-label')),title=N(e.getAttribute('title')),acc=N(aria||title||txt),mix=acc+' '+txt;const sl=HAS(mix,'light'),sm=HAS(mix,'medium'),sh=HAS(mix,'heavy'),sa=HAS(mix,'auto');const n=(sl?1:0)+(sm?1:0)+(sh?1:0)+(sa?1:0);if(n!==1)continue;const sem=sl?'LIGHT':sm?'MEDIUM':sh?'HEAVY':'AUTO';raw.push({e:e,sem:sem,acc:acc,hash:acc?H(L(acc)):'-',enabled:!(e.disabled||L(e.getAttribute('aria-disabled'))==='true')});}"
                + "const uniq=raw.filter((c,i)=>!raw.some((d,j)=>j!==i&&d.e.contains(c.e)&&d.sem===c.sem));const groups=new Map();for(const c of uniq){let g=null,p=c.e.parentElement;for(let d=0;p&&d<9;d++,p=p.parentElement){const m=uniq.filter(x=>p.contains(x.e));if(m.length>=2&&m.length<=6){g=p;break;}}if(!g)continue;if(!groups.has(g))groups.set(g,[]);groups.get(g).push(c);}"
                + "const valid=[];for(const [g,m0] of groups.entries()){const seen=new Set(),m=[];for(const c of m0){const k=c.sem+'|'+c.hash;if(!seen.has(k)){seen.add(k);m.push(c);}}const lc=m.filter(x=>x.sem==='LIGHT').length,mc=m.filter(x=>x.sem==='MEDIUM').length;if(lc===1&&mc===1&&m.length>=2&&m.length<=5&&m.every(x=>x.enabled))valid.push({g:g,m:m});}"
                + "if(valid.length!==1)return JSON.stringify({success:true,complete:complete,group_ok:false,valid_group_count:valid.length,option_count:0,light_count:0,medium_count:0,heavy_count:0,auto_count:0,enabled_count:0,selected_count:0,group_hash:'-',option_set_hash:'-',options:[]});const m=valid[0].m;let lc=0,mc=0,hc=0,ac=0,en=0,sc=0;const opts=[];for(const c of m){if(c.sem==='LIGHT')lc++;if(c.sem==='MEDIUM')mc++;if(c.sem==='HEAVY')hc++;if(c.sem==='AUTO')ac++;if(c.enabled)en++;const e=c.e,selc=L(e.getAttribute('aria-checked'))==='true'||L(e.getAttribute('aria-selected'))==='true'||['checked','selected','on','active'].includes(L(e.getAttribute('data-state')));if(selc)sc++;opts.push({semantic:c.sem,acc_hash:c.hash,enabled:c.enabled,selected:selc,role:L(e.getAttribute('role'))||((e.tagName||'').toLowerCase())});}opts.sort((a,b)=>(a.semantic+'|'+a.acc_hash).localeCompare(b.semantic+'|'+b.acc_hash));const setHash=H(opts.map(x=>x.semantic+'|'+x.acc_hash+'|'+x.enabled).join(','));return JSON.stringify({success:true,complete:complete,group_ok:true,valid_group_count:1,option_count:opts.length,light_count:lc,medium_count:mc,heavy_count:hc,auto_count:ac,enabled_count:en,selected_count:sc,group_hash:setHash,option_set_hash:setHash,options:opts});}catch(e){return JSON.stringify({success:false,complete:false,group_ok:false,error_class:'POPUP_SCAN_EXCEPTION'});}})();";
    }

    private String clickPopupOptionJs40(String expectedHash, String expectedSemantic) {
        return "(function(){try{const EH='" + js40(expectedHash) + "',ES='" + js40(expectedSemantic) + "';const N=x=>(x||'').replace(/\\s+/g,' ').trim();const L=x=>N(x).toLowerCase();const TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean);const HAS=(s,w)=>TOK(s).includes(w);const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};"
                + "let input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=\"true\"],[role=\"textbox\"]'))if(V(e)){input=e;break;}let composer=null;if(input){let p=input.parentElement;for(let d=0;p&&d<9;d++,p=p.parentElement){const cs=[...p.querySelectorAll('button,[role=\"button\"]')].filter(V);if(cs.length>=3&&cs.length<=12){composer=p;break;}}}const sel='button,[role=\"menuitem\"],[role=\"menuitemradio\"],[role=\"option\"],[role=\"radio\"]';const raw=[];for(const e of document.querySelectorAll(sel)){if(!V(e)||(composer&&composer.contains(e)))continue;const txt=N(e.innerText||e.textContent||''),aria=N(e.getAttribute('aria-label')),title=N(e.getAttribute('title')),acc=N(aria||title||txt),mix=acc+' '+txt;const sl=HAS(mix,'light'),sm=HAS(mix,'medium'),sh=HAS(mix,'heavy'),sa=HAS(mix,'auto');const n=(sl?1:0)+(sm?1:0)+(sh?1:0)+(sa?1:0);if(n!==1)continue;raw.push({e:e,sem:sl?'LIGHT':sm?'MEDIUM':sh?'HEAVY':'AUTO',hash:acc?H(L(acc)):'-',enabled:!(e.disabled||L(e.getAttribute('aria-disabled'))==='true')});}const uniq=raw.filter((c,i)=>!raw.some((d,j)=>j!==i&&d.e.contains(c.e)&&d.sem===c.sem));const groups=new Map();for(const c of uniq){let g=null,p=c.e.parentElement;for(let d=0;p&&d<9;d++,p=p.parentElement){const m=uniq.filter(x=>p.contains(x.e));if(m.length>=2&&m.length<=6){g=p;break;}}if(!g)continue;if(!groups.has(g))groups.set(g,[]);groups.get(g).push(c);}const valid=[];for(const [g,m0] of groups.entries()){const seen=new Set(),m=[];for(const c of m0){const k=c.sem+'|'+c.hash;if(!seen.has(k)){seen.add(k);m.push(c);}}if(m.filter(x=>x.sem==='LIGHT').length===1&&m.filter(x=>x.sem==='MEDIUM').length===1&&m.length>=2&&m.length<=5&&m.every(x=>x.enabled))valid.push(m);}if(valid.length!==1)return JSON.stringify({success:true,matches:0,clicked:false,valid_group_count:valid.length});const matches=valid[0].filter(x=>x.sem===ES&&x.hash===EH&&x.enabled);if(matches.length===1){matches[0].e.click();return JSON.stringify({success:true,matches:1,clicked:true,valid_group_count:1});}return JSON.stringify({success:true,matches:matches.length,clicked:false,valid_group_count:1});}catch(e){return JSON.stringify({success:false,matches:-1,clicked:false});}})();";
    }

    private void eval40(String js, JsonDone40 done) {
        if (web40 == null) { done.done(new JSONObject()); return; }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (once.compareAndSet(false, true)) {
                JSONObject o = new JSONObject();
                put40(o, "success", false);
                put40(o, "complete", false);
                put40(o, "error_class", "EVAL_TIMEOUT");
                done.done(o);
            }
        };
        h40.postDelayed(timeout, EVAL_TIMEOUT_MS40);
        web40.evaluateJavascript(js, value -> {
            if (!once.compareAndSet(false, true)) return;
            h40.removeCallbacks(timeout);
            try {
                String s = value == null ? "" : value;
                Object outer = new JSONTokener(s).nextValue();
                if (outer instanceof String) s = (String) outer;
                done.done(new JSONObject(s));
            } catch (Exception e) {
                JSONObject o = new JSONObject();
                put40(o, "success", false);
                put40(o, "complete", false);
                put40(o, "error_class", "PARSE_ERROR");
                done.done(o);
            }
        });
    }

    private void finish40(String classification) {
        if (!running40) return;
        h40.removeCallbacks(this::watchdog40);
        JSONObject st = baseState40();
        put40(st, "runtime_ms", System.currentTimeMillis() - startedAt40);
        JSONObject p = payload40("FINAL", classification, st);
        if (telemetryHealthy40) new Thread(() -> upload40(p, NET_TIMEOUT_MS40), "cp40-final").start();
        running40 = false;
        setStatus40(classification);
        if (run40 != null) {
            boolean blocked = isUnresolved40(prefs40.getString("claim_status", "NONE"));
            run40.setEnabled(!blocked);
            run40.setText("RUN GUARDED EFFORT ROUND-TRIP");
        }
    }

    private void phase40(String phase, String classification, JSONObject state) {
        if (!running40 || !telemetryHealthy40) return;
        JSONObject p = payload40(phase, classification, state);
        new Thread(() -> upload40(p, NET_TIMEOUT_MS40), "cp40-phase-" + seq40).start();
    }

    private JSONObject payload40(String phase, String classification, JSONObject state) {
        JSONObject p = new JSONObject();
        put40(p, "schema_version", SCHEMA40);
        put40(p, "scenario_id", SCENARIO40);
        put40(p, "source_ref", TelemetryConfigV40.SOURCE_REF);
        put40(p, "collector_id", TelemetryConfigV40.COLLECTOR_ID);
        put40(p, "test_id", testId40);
        put40(p, "seq", seq40++);
        put40(p, "timestamp_epoch_ms", System.currentTimeMillis());
        put40(p, "phase", phase);
        put40(p, "classification", classification);
        put40(p, "state", state);
        return p;
    }

    private JSONObject upload40(JSONObject payload, int timeoutMs) {
        JSONObject r = new JSONObject();
        if (!TelemetryConfigV40.isConfigured()) {
            put40(r, "success", false);
            put40(r, "error", "TELEMETRY_NOT_CONFIGURED");
            return r;
        }
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(TelemetryConfigV40.WEBHOOK_URL).openConnection();
            c.setRequestMethod("POST");
            c.setConnectTimeout(timeoutMs);
            c.setReadTimeout(timeoutMs);
            c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/json");
            byte[] body = payload.toString().getBytes(StandardCharsets.UTF_8);
            c.setFixedLengthStreamingMode(body.length);
            c.getOutputStream().write(body);
            int code = c.getResponseCode();
            put40(r, "success", code >= 200 && code < 300);
            put40(r, "code", code);
        } catch (Exception e) {
            put40(r, "success", false);
            put40(r, "error", "NETWORK_ERROR");
        } finally {
            if (c != null) c.disconnect();
        }
        return r;
    }

    private WebView findWeb40(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb40(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }

    private boolean isChatGpt40(String url) {
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

    private int dp40(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    private void setStatus40(String s) {
        if (status40 != null) status40.setText(s);
    }

    private static String js40(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "");
    }

    private static void put40(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) {}
    }
}
