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
 * Stable v0.40 — guarded semantic pointer-down popup census.
 *
 * v0.39 proved that HTMLElement.click() on the unique Medium composer selector did not
 * open the effort popup. This build never clicks a model option. It resolves the same
 * semantic Medium selector, persists a claim, dispatches exactly one synthetic pointerdown
 * (or mousedown only if PointerEvent is unavailable) directly to that semantic element,
 * and captures four broad privacy-safe popup snapshots. No coordinates/XPath are used.
 */
public class OrchestratorPaidModelEffortPointerCensusV42Activity extends OrchestratorAuthModeV34Activity {
    private static final String SCHEMA42 = "cp-v42-paid-model-effort-pointer-census-v1";
    private static final String SCENARIO42 = "paid-model-effort-semantic-pointer-popup-census";
    private static final long EVAL_TIMEOUT_MS42 = 3200L;
    private static final int NET_TIMEOUT_MS42 = 3200;
    private static final int SNAPSHOTS42 = 4;
    private static final long WATCHDOG_MS42 = 30000L;

    private final Handler h42 = new Handler(Looper.getMainLooper());
    private WebView web42;
    private TextView status42;
    private Button run42;
    private SharedPreferences prefs42;
    private boolean running42 = false;
    private boolean telemetryHealthy42 = false;
    private String testId42 = "-";
    private int seq42 = 0;
    private long startedAt42 = 0L;
    private String baselineHash42 = "-";
    private String claimStatus42 = "NONE";
    private int uiDispatches42 = 0;
    private int completeSnapshots42 = 0;
    private int popupEvidenceSnapshots42 = 0;

    private interface JsonDone42 { void done(JSONObject o); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs42 = getSharedPreferences("cp42_paid_model_effort_pointer_census", MODE_PRIVATE);
        web42 = findWeb42(getWindow().getDecorView());
        installUi42();
        String prior = prefs42.getString("claim_status", "NONE");
        if (prior.startsWith("UNCERTAIN")) {
            setStatus42("Blocked: unresolved prior pointer-open claim — no replay");
            if (run42 != null) run42.setEnabled(false);
        } else {
            setStatus42("v0.40 semantic pointer popup census ready — no model option click");
        }
    }

    @Override protected void onDestroy() {
        h42.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private void installUi42() {
        if (web42 == null) return;
        ViewParent p = web42.getParent();
        if (!(p instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) p;
        for (int i = 0; i < root.getChildCount(); i++) {
            View c = root.getChildAt(i);
            if (c != web42) c.setVisibility(View.GONE);
        }
        web42.setMinimumHeight(1);
        web42.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));
        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp42(8), dp42(3), dp42(8), dp42(6));
        status42 = new TextView(this);
        status42.setTextSize(11f);
        status42.setSingleLine(true);
        status42.setEllipsize(TextUtils.TruncateAt.END);
        panel.addView(status42, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        run42 = new Button(this);
        run42.setText("RUN SEMANTIC POINTER POPUP CENSUS");
        run42.setTextSize(13f);
        run42.setAllCaps(false);
        run42.setOnClickListener(v -> run42());
        panel.addView(run42, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp42(46)));
        root.addView(panel, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void run42() {
        if (running42) return;
        if (web42 == null || !isChatGpt42(web42.getUrl())) {
            setStatus42("Blocked: ChatGPT page not ready");
            return;
        }
        String prior = prefs42.getString("claim_status", "NONE");
        if (prior.startsWith("UNCERTAIN")) {
            setStatus42("Blocked: unresolved prior pointer-open claim — no replay");
            return;
        }
        running42 = true;
        telemetryHealthy42 = false;
        testId42 = "cp42-" + UUID.randomUUID();
        seq42 = 0;
        startedAt42 = System.currentTimeMillis();
        baselineHash42 = "-";
        claimStatus42 = "NONE";
        uiDispatches42 = 0;
        completeSnapshots42 = 0;
        popupEvidenceSnapshots42 = 0;
        if (run42 != null) { run42.setEnabled(false); run42.setText("POINTER CENSUS RUNNING..."); }
        setStatus42("Telemetry preflight...");
        h42.postDelayed(this::watchdog42, WATCHDOG_MS42);
        telemetryPreflight42();
    }

    private void telemetryPreflight42() {
        JSONObject p = payload42("TELEMETRY_PREFLIGHT", "RUNNING", baseState42());
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> { if (running42 && once.compareAndSet(false, true)) finish42("TELEMETRY_PREFLIGHT_TIMEOUT"); };
        h42.postDelayed(timeout, 8000L);
        new Thread(() -> {
            JSONObject r = upload42(p, NET_TIMEOUT_MS42 + 900);
            runOnUiThread(() -> {
                if (!running42 || !once.compareAndSet(false, true)) return;
                h42.removeCallbacks(timeout);
                if (!r.optBoolean("success", false)) { finish42("TELEMETRY_UNAVAILABLE"); return; }
                telemetryHealthy42 = true;
                phase42("RUN_STARTED", "GUARDED_SEMANTIC_POINTER_POPUP_CENSUS", baseState42());
                resolveBaseline42();
            });
        }, "cp42-preflight").start();
    }

    private void resolveBaseline42() {
        setStatus42("Resolving closed Medium selector...");
        eval42(scanClosedComposerJs42(), o -> {
            JSONObject st = baseState42();
            copy42(st, o, "success","complete","effort_control_count","effort_semantic","effort_control_hash","effort_has_popup","effort_expanded_true","composer_control_count","candidate_set_hash");
            boolean ok = o.optBoolean("success", false) && o.optBoolean("complete", false)
                    && o.optInt("effort_control_count", -1) == 1
                    && "MEDIUM".equals(o.optString("effort_semantic", ""))
                    && o.optBoolean("effort_has_popup", false)
                    && !o.optBoolean("effort_expanded_true", false)
                    && !"-".equals(o.optString("effort_control_hash", "-"));
            if (!ok) {
                phase42("BASELINE_COMPOSER", "FAIL_CLOSED_MEDIUM_SELECTOR_UNRESOLVED", st);
                finish42("BASELINE_MEDIUM_SELECTOR_UNRESOLVED_ZERO_DISPATCH");
                return;
            }
            baselineHash42 = o.optString("effort_control_hash", "-");
            phase42("BASELINE_COMPOSER", "PASS_UNIQUE_CLOSED_MEDIUM_SELECTOR", st);
            dispatchPointer42();
        });
    }

    private void dispatchPointer42() {
        setStatus42("Claim -> semantic pointerdown...");
        String claimId = "POINTER_OPEN_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0,8);
        boolean committed = prefs42.edit()
                .putString("claim_id", claimId)
                .putString("claim_status", "CLAIMED")
                .putString("claim_action", "EFFORT_POPUP_SEMANTIC_POINTERDOWN")
                .putString("baseline_hash", baselineHash42)
                .commit();
        if (!committed) { finish42("POINTER_OPEN_CLAIM_FAILED_ZERO_DISPATCH"); return; }
        claimStatus42 = "CLAIMED";
        phase42("DURABLE_CLAIM", "CLAIMED_BEFORE_SEMANTIC_POINTERDOWN", baseState42());
        eval42(pointerDownEffortJs42(baselineHash42), r -> {
            JSONObject st = baseState42();
            copy42(st, r, "success","matches","dispatched","event_class","default_prevented");
            if (!r.optBoolean("success", false) || r.optInt("matches", -1) != 1 || !r.optBoolean("dispatched", false)) {
                prefs42.edit().putString("claim_status", "ABORTED_NO_SIDE_EFFECT").commit();
                claimStatus42 = "ABORTED_NO_SIDE_EFFECT";
                phase42("POINTER_OPEN_DISPATCH", "ABORTED_NO_SIDE_EFFECT", st);
                finish42("POINTER_OPEN_NOT_DISPATCHED");
                return;
            }
            uiDispatches42 = 1;
            prefs42.edit().putString("claim_status", "DISPATCHED").commit();
            claimStatus42 = "DISPATCHED";
            phase42("POINTER_OPEN_DISPATCH", "DISPATCHED_UNIQUE_MEDIUM_SELECTOR", st);
            h42.postDelayed(() -> snapshot42(0), 180L);
        });
    }

    private void snapshot42(int index) {
        if (!running42) return;
        if (index >= SNAPSHOTS42) {
            if (popupEvidenceSnapshots42 > 0) {
                prefs42.edit().putString("claim_status", "CONFIRMED_POPUP_EVIDENCE").commit();
                claimStatus42 = "CONFIRMED_POPUP_EVIDENCE";
                finish42(completeSnapshots42 == SNAPSHOTS42
                        ? "PASS_SEMANTIC_POINTER_POPUP_CENSUS_CAPTURED"
                        : "PARTIAL_SEMANTIC_POINTER_POPUP_CENSUS_CAPTURED");
            } else {
                prefs42.edit().putString("claim_status", "UNCERTAIN_NO_REPLAY").commit();
                claimStatus42 = "UNCERTAIN_NO_REPLAY";
                finish42("SEMANTIC_POINTER_POPUP_UNCERTAIN_NO_REPLAY");
            }
            return;
        }
        setStatus42("Popup snapshot " + (index + 1) + "/" + SNAPSHOTS42 + "...");
        eval42(scanOpenSurfaceJs42(index, baselineHash42), o -> {
            boolean complete = o.optBoolean("complete", false);
            boolean evidence = o.optBoolean("popup_evidence", false);
            if (complete) completeSnapshots42++;
            if (evidence) popupEvidenceSnapshots42++;
            JSONObject st = baseState42();
            copy42(st, o, "success","complete","snapshot_index","visited_nodes","semantic_candidate_count","light_count","medium_count","heavy_count","auto_count","thinking_count","instant_count","selected_count","trigger_found","trigger_expanded_true","trigger_data_state_open","popup_role_candidate_count","portalish_candidate_count","popup_evidence","candidate_set_hash","ancestor_set_hash");
            JSONArray a = o.optJSONArray("candidates");
            if (a != null) put42(st, "candidates", a);
            phase42("POPUP_SURFACE_SNAPSHOT", complete ? "CAPTURED_COMPLETE" : "CAPTURED_BUDGET_LIMIT", st);
            long delay = index == 0 ? 500L : index == 1 ? 850L : index == 2 ? 1300L : 0L;
            h42.postDelayed(() -> snapshot42(index + 1), delay);
        });
    }

    private String scanClosedComposerJs42() {
        return "(function(){try{const T0=performance.now(),MAXN=6500,MAXMS=180;const N=x=>(x||'').replace(/\\s+/g,' ').trim(),L=x=>N(x).toLowerCase(),TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean),HAS=(s,w)=>TOK(s).includes(w),H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);},V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};let visited=0,complete=true,input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=\"true\"],[role=\"textbox\"]')){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(V(e)){input=e;break;}}let root=null;if(input){let p=input.parentElement;for(let d=0;p&&d<9;d++,p=p.parentElement){const cs=[...p.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio');if(cs.length>=3&&cs.length<=12){root=p;break;}}}const nodes=root?[...root.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio'):[];let effort=0,eh='-',es='-',hp=false,ex=false;const fps=[];for(const e of nodes){const txt=N(e.innerText||e.textContent||''),aria=N(e.getAttribute('aria-label')),title=N(e.getAttribute('title')),acc=N(aria||title||txt),mix=acc+' '+txt;const sl=HAS(mix,'light'),sm=HAS(mix,'medium'),sh=HAS(mix,'heavy'),sa=HAS(mix,'auto');const n=(sl?1:0)+(sm?1:0)+(sh?1:0)+(sa?1:0);const sem=n===1?(sl?'LIGHT':sm?'MEDIUM':sh?'HEAVY':'AUTO'):'NONE';const ah=acc?H(L(acc)):'-',popup=N(e.getAttribute('aria-haspopup')),expanded=L(e.getAttribute('aria-expanded'));const fp=H([ah,sem,popup,expanded,(e.tagName||'').toLowerCase()].join('|'));fps.push(fp);if(sem!=='NONE'){effort++;eh=ah;es=sem;hp=popup!==''&&L(popup)!=='false';ex=expanded==='true';}}fps.sort();if(effort!==1){eh='-';es='-';hp=false;ex=false;}return JSON.stringify({success:true,complete:complete,effort_control_count:effort,effort_semantic:es,effort_control_hash:eh,effort_has_popup:hp,effort_expanded_true:ex,composer_control_count:nodes.length,candidate_set_hash:H(fps.join(','))});}catch(e){return JSON.stringify({success:false,complete:false,effort_control_count:-1});}})();";
    }

    private String pointerDownEffortJs42(String hash) {
        return "(function(){try{const EH='" + js42(hash) + "';const N=x=>(x||'').replace(/\\s+/g,' ').trim(),L=x=>N(x).toLowerCase(),TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean),HAS=(s,w)=>TOK(s).includes(w),H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);},V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};let input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=\"true\"],[role=\"textbox\"]'))if(V(e)){input=e;break;}let root=null;if(input){let p=input.parentElement;for(let d=0;p&&d<9;d++,p=p.parentElement){const cs=[...p.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio');if(cs.length>=3&&cs.length<=12){root=p;break;}}}const m=[];if(root)for(const e of root.querySelectorAll('button,[role=\"button\"]')){if(!V(e)||L(e.getAttribute('role'))==='radio')continue;const txt=N(e.innerText||e.textContent||''),aria=N(e.getAttribute('aria-label')),title=N(e.getAttribute('title')),acc=N(aria||title||txt),mix=acc+' '+txt;const sm=HAS(mix,'medium'),sl=HAS(mix,'light'),sh=HAS(mix,'heavy'),sa=HAS(mix,'auto');const n=(sm?1:0)+(sl?1:0)+(sh?1:0)+(sa?1:0),ah=acc?H(L(acc)):'-',popup=N(e.getAttribute('aria-haspopup'));if(n===1&&sm&&ah===EH&&popup!==''&&L(popup)!=='false'&&!(e.disabled||L(e.getAttribute('aria-disabled'))==='true'))m.push(e);}if(m.length!==1)return JSON.stringify({success:true,matches:m.length,dispatched:false,event_class:'NONE',default_prevented:false});const e=m[0];try{e.focus({preventScroll:true});}catch(_){}let ev,kind;if(typeof PointerEvent==='function'){ev=new PointerEvent('pointerdown',{bubbles:true,cancelable:true,composed:true,pointerId:1,pointerType:'mouse',isPrimary:true,button:0,buttons:1,ctrlKey:false});kind='POINTERDOWN';}else{ev=new MouseEvent('mousedown',{bubbles:true,cancelable:true,composed:true,view:window,button:0,buttons:1,ctrlKey:false});kind='MOUSEDOWN_FALLBACK';}const accepted=e.dispatchEvent(ev);return JSON.stringify({success:true,matches:1,dispatched:true,event_class:kind,default_prevented:!accepted});}catch(e){return JSON.stringify({success:false,matches:-1,dispatched:false,event_class:'EXCEPTION',default_prevented:false});}})();";
    }

    private String scanOpenSurfaceJs42(int index, String baselineHash) {
        return "(function(){try{const IDX=" + index + ",BH='" + js42(baselineHash) + "',T0=performance.now(),MAXN=12000,MAXMS=260,MAXC=48;const N=x=>(x||'').replace(/\\s+/g,' ').trim(),L=x=>N(x).toLowerCase(),TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean),HAS=(s,w)=>TOK(s).includes(w),H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);},V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};let input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=\"true\"],[role=\"textbox\"]'))if(V(e)){input=e;break;}let composer=null;if(input){let p=input.parentElement;for(let d=0;p&&d<10;d++,p=p.parentElement){if(p.querySelectorAll('button,[role=\"button\"]').length>=3){composer=p;break;}}}const sel='button,[role=\"button\"],[role=\"menuitem\"],[role=\"menuitemradio\"],[role=\"option\"],[role=\"radio\"],[data-radix-collection-item],[aria-checked],[aria-selected]';let visited=0,complete=true,lc=0,mc=0,hc=0,ac=0,tc=0,ic=0,sc=0,triggerFound=false,triggerExpanded=false,triggerOpen=false,popupRoles=0,portalish=0;const out=[],fps=[],afps=[];for(const e of document.querySelectorAll(sel)){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(!V(e))continue;const txt=N(e.innerText||e.textContent||''),aria=N(e.getAttribute('aria-label')),title=N(e.getAttribute('title')),acc=N(aria||title||txt),mix=acc+' '+txt;const sl=HAS(mix,'light'),sm=HAS(mix,'medium'),sh=HAS(mix,'heavy'),sa=HAS(mix,'auto'),st=HAS(mix,'thinking'),si=HAS(mix,'instant');const n=(sl?1:0)+(sm?1:0)+(sh?1:0)+(sa?1:0)+(st?1:0)+(si?1:0);if(n!==1)continue;const sem=sl?'LIGHT':sm?'MEDIUM':sh?'HEAVY':sa?'AUTO':st?'THINKING':'INSTANT';if(sl)lc++;if(sm)mc++;if(sh)hc++;if(sa)ac++;if(st)tc++;if(si)ic++;const ah=acc?H(L(acc)):'-',role=L(e.getAttribute('role'))||((e.tagName||'').toLowerCase()),ds=L(e.getAttribute('data-state')),expanded=L(e.getAttribute('aria-expanded')),selected=L(e.getAttribute('aria-checked'))==='true'||L(e.getAttribute('aria-selected'))==='true'||['checked','selected','on','active'].includes(ds);if(selected)sc++;const trig=ah===BH;if(trig){triggerFound=true;if(expanded==='true')triggerExpanded=true;if(['open','expanded'].includes(ds))triggerOpen=true;}let p=e.parentElement,chain=[],menuAnc=false,portalAnc=false;for(let d=0;p&&d<6;d++,p=p.parentElement){const pr=L(p.getAttribute('role')),slot=L(p.getAttribute('data-slot')),tid=L(p.getAttribute('data-testid')),rad=L(p.getAttribute('data-radix-popper-content-wrapper'));if(['menu','listbox','radiogroup'].includes(pr))menuAnc=true;if(slot.includes('menu')||slot.includes('popover')||slot.includes('dropdown')||rad!=='')portalAnc=true;chain.push(H([pr,slot,tid,rad,(p.tagName||'').toLowerCase()].join('|')));}if(menuAnc)popupRoles++;if(portalAnc)portalish++;const afp=H(chain.join('>')),q={semantic:sem,acc_hash:ah,role:role,enabled:!(e.disabled||L(e.getAttribute('aria-disabled'))==='true'),selected:selected,is_trigger:trig,in_composer:!!(composer&&composer.contains(e)),has_popup:N(e.getAttribute('aria-haspopup'))!=='',expanded_true:expanded==='true',data_state_open:['open','expanded'].includes(ds),has_menu_ancestor:menuAnc,has_portalish_ancestor:portalAnc,ancestor_fp:afp,testid_hash:N(e.getAttribute('data-testid'))?H(L(e.getAttribute('data-testid'))):'-',slot_hash:N(e.getAttribute('data-slot'))?H(L(e.getAttribute('data-slot'))):'-'};q.fp=H([q.semantic,q.acc_hash,q.role,q.enabled,q.selected,q.is_trigger,q.in_composer,q.has_popup,q.expanded_true,q.data_state_open,q.has_menu_ancestor,q.has_portalish_ancestor,q.ancestor_fp,q.testid_hash,q.slot_hash].join('|'));if(out.length<MAXC)out.push(q);fps.push(q.fp);afps.push(afp);}out.sort((a,b)=>(a.semantic+'|'+a.acc_hash+'|'+a.ancestor_fp).localeCompare(b.semantic+'|'+b.acc_hash+'|'+b.ancestor_fp));fps.sort();afps.sort();const semanticCount=lc+mc+hc+ac+tc+ic;const popupEvidence=triggerExpanded||triggerOpen||popupRoles>0||portalish>0||semanticCount>=2;return JSON.stringify({success:true,complete:complete,snapshot_index:IDX,visited_nodes:visited,semantic_candidate_count:semanticCount,light_count:lc,medium_count:mc,heavy_count:hc,auto_count:ac,thinking_count:tc,instant_count:ic,selected_count:sc,trigger_found:triggerFound,trigger_expanded_true:triggerExpanded,trigger_data_state_open:triggerOpen,popup_role_candidate_count:popupRoles,portalish_candidate_count:portalish,popup_evidence:popupEvidence,candidate_set_hash:H(fps.join(',')),ancestor_set_hash:H(afps.join(',')),candidates:out});}catch(e){return JSON.stringify({success:false,complete:false,error_class:'OPEN_SURFACE_SCAN_EXCEPTION'});}})();";
    }

    private void eval42(String js, JsonDone42 done) {
        if (web42 == null) { done.done(new JSONObject()); return; }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> {
            if (once.compareAndSet(false, true)) {
                JSONObject o = new JSONObject(); put42(o,"success",false); put42(o,"complete",false); put42(o,"error_class","EVAL_TIMEOUT"); done.done(o);
            }
        };
        h42.postDelayed(timeout, EVAL_TIMEOUT_MS42);
        web42.evaluateJavascript(js, value -> {
            if (!once.compareAndSet(false, true)) return;
            h42.removeCallbacks(timeout);
            try {
                String s = value == null ? "" : value;
                Object outer = new JSONTokener(s).nextValue();
                if (outer instanceof String) s = (String) outer;
                done.done(new JSONObject(s));
            } catch (Exception e) {
                JSONObject o = new JSONObject(); put42(o,"success",false); put42(o,"complete",false); put42(o,"error_class","PARSE_ERROR"); done.done(o);
            }
        });
    }

    private void watchdog42() {
        if (!running42) return;
        if (claimStatus42.equals("DISPATCHED")) {
            prefs42.edit().putString("claim_status", "UNCERTAIN_NO_REPLAY").commit();
            claimStatus42 = "UNCERTAIN_NO_REPLAY";
        }
        finish42("GLOBAL_WATCHDOG");
    }

    private void finish42(String classification) {
        if (!running42) return;
        JSONObject st = baseState42();
        put42(st,"complete_snapshots",completeSnapshots42);
        put42(st,"popup_evidence_snapshots",popupEvidenceSnapshots42);
        put42(st,"runtime_ms",System.currentTimeMillis()-startedAt42);
        JSONObject p = payload42("FINAL", classification, st);
        if (telemetryHealthy42) new Thread(() -> upload42(p, NET_TIMEOUT_MS42), "cp42-final").start();
        running42 = false;
        setStatus42(classification);
        if (run42 != null) {
            boolean blocked = claimStatus42.startsWith("UNCERTAIN");
            run42.setEnabled(!blocked);
            run42.setText("RUN SEMANTIC POINTER POPUP CENSUS");
        }
    }

    private JSONObject baseState42() {
        JSONObject st = new JSONObject();
        put42(st,"baseline_hash",baselineHash42);
        put42(st,"claim_status",claimStatus42);
        put42(st,"ui_dispatches",uiDispatches42);
        put42(st,"model_option_clicks",0);
        put42(st,"raw_text_uploaded",false);
        put42(st,"raw_html_uploaded",false);
        put42(st,"cookies_tokens_accessed",false);
        put42(st,"geometry_click_used",false);
        return st;
    }

    private void phase42(String phase, String classification, JSONObject st) {
        if (!running42 || !telemetryHealthy42) return;
        JSONObject p = payload42(phase, classification, st);
        new Thread(() -> upload42(p, NET_TIMEOUT_MS42), "cp42-phase-" + seq42).start();
    }

    private JSONObject payload42(String phase, String classification, JSONObject state) {
        JSONObject p = new JSONObject();
        put42(p,"schema_version",SCHEMA42);
        put42(p,"scenario_id",SCENARIO42);
        put42(p,"source_ref",TelemetryConfigV42.SOURCE_REF);
        put42(p,"collector_id",TelemetryConfigV42.COLLECTOR_ID);
        put42(p,"test_id",testId42);
        put42(p,"seq",seq42++);
        put42(p,"timestamp_epoch_ms",System.currentTimeMillis());
        put42(p,"phase",phase);
        put42(p,"classification",classification);
        put42(p,"state",state);
        return p;
    }

    private JSONObject upload42(JSONObject payload, int timeoutMs) {
        JSONObject r = new JSONObject();
        if (!TelemetryConfigV42.isConfigured()) { put42(r,"success",false); put42(r,"error","TELEMETRY_NOT_CONFIGURED"); return r; }
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(TelemetryConfigV42.WEBHOOK_URL).openConnection();
            c.setRequestMethod("POST"); c.setConnectTimeout(timeoutMs); c.setReadTimeout(timeoutMs); c.setDoOutput(true);
            c.setRequestProperty("Content-Type","application/json");
            byte[] body = payload.toString().getBytes(StandardCharsets.UTF_8);
            c.setFixedLengthStreamingMode(body.length); c.getOutputStream().write(body);
            int code = c.getResponseCode(); put42(r,"success",code>=200&&code<300); put42(r,"code",code);
        } catch (Exception e) { put42(r,"success",false); put42(r,"error","NETWORK_ERROR"); }
        finally { if (c != null) c.disconnect(); }
        return r;
    }

    private WebView findWeb42(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i=0;i<g.getChildCount();i++) { WebView w=findWeb42(g.getChildAt(i)); if (w!=null) return w; }
        }
        return null;
    }

    private boolean isChatGpt42(String url) {
        if (TextUtils.isEmpty(url)) return false;
        try {
            String h= Uri.parse(url).getHost(); if (h==null) return false; h=h.toLowerCase();
            return h.equals("chatgpt.com")||h.endsWith(".chatgpt.com")||h.equals("openai.com")||h.endsWith(".openai.com");
        } catch (Exception e) { return false; }
    }

    private int dp42(int v) { return Math.round(v*getResources().getDisplayMetrics().density); }
    private void setStatus42(String s) { if (status42!=null) status42.setText(s); }
    private static String js42(String s) { return s==null?"":s.replace("\\","\\\\").replace("'","\\'").replace("\n"," ").replace("\r"," "); }
    private static void copy42(JSONObject dst, JSONObject src, String... keys) { for(String k:keys) if(src.has(k)) put42(dst,k,src.opt(k)); }
    private static void put42(JSONObject o,String k,Object v){ try{o.put(k,v);}catch(Exception ignored){} }
}
