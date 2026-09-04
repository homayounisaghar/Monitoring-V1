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
 * Stable v0.39 — guarded popup-open census for the paid composer effort selector.
 *
 * v0.38 proved the closed Medium selector, claimed and clicked it once, but its popup
 * resolver timed out before any model option click. This build does not select a model.
 * It proves the closed Medium selector, durably claims the single popup-open click,
 * then takes four broad, privacy-safe snapshots of visible semantic controls across
 * portal/composer DOM. Raw labels/text/HTML are never uploaded.
 */
public class OrchestratorPaidModelEffortPopupCensusV41Activity extends OrchestratorAuthModeV34Activity {
    private static final String SCHEMA41 = "cp-v41-paid-model-effort-popup-census-v1";
    private static final String SCENARIO41 = "paid-model-effort-popup-open-read-only-census";
    private static final long EVAL_TIMEOUT_MS41 = 3200L;
    private static final int NET_TIMEOUT_MS41 = 3200;
    private static final int SNAPSHOTS41 = 4;
    private static final long WATCHDOG_MS41 = 30000L;

    private final Handler h41 = new Handler(Looper.getMainLooper());
    private WebView web41;
    private TextView status41;
    private Button run41;
    private SharedPreferences prefs41;
    private boolean running41 = false;
    private boolean telemetryHealthy41 = false;
    private String testId41 = "-";
    private int seq41 = 0;
    private long startedAt41 = 0L;
    private String baselineHash41 = "-";
    private String claimStatus41 = "NONE";
    private int uiClicks41 = 0;
    private int completeSnapshots41 = 0;
    private int popupEvidenceSnapshots41 = 0;

    private interface JsonDone41 { void done(JSONObject o); }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs41 = getSharedPreferences("cp41_paid_model_effort_popup_census", MODE_PRIVATE);
        web41 = findWeb41(getWindow().getDecorView());
        installUi41();
        String prior = prefs41.getString("claim_status", "NONE");
        if (prior.startsWith("UNCERTAIN")) {
            setStatus41("Blocked: unresolved prior popup-open claim — no replay");
            if (run41 != null) run41.setEnabled(false);
        } else {
            setStatus41("v0.39 popup census ready — no model-option click");
        }
    }

    @Override protected void onDestroy() {
        h41.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private void installUi41() {
        if (web41 == null) return;
        ViewParent p = web41.getParent();
        if (!(p instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) p;
        for (int i = 0; i < root.getChildCount(); i++) {
            View c = root.getChildAt(i);
            if (c != web41) c.setVisibility(View.GONE);
        }
        web41.setMinimumHeight(1);
        web41.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));
        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp41(8), dp41(3), dp41(8), dp41(6));
        status41 = new TextView(this);
        status41.setTextSize(11f);
        status41.setSingleLine(true);
        status41.setEllipsize(TextUtils.TruncateAt.END);
        panel.addView(status41, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        run41 = new Button(this);
        run41.setText("RUN GUARDED POPUP CENSUS");
        run41.setTextSize(13f);
        run41.setAllCaps(false);
        run41.setOnClickListener(v -> run41());
        panel.addView(run41, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp41(46)));
        root.addView(panel, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void run41() {
        if (running41) return;
        if (web41 == null || !isChatGpt41(web41.getUrl())) {
            setStatus41("Blocked: ChatGPT page not ready");
            return;
        }
        String prior = prefs41.getString("claim_status", "NONE");
        if (prior.startsWith("UNCERTAIN")) {
            setStatus41("Blocked: unresolved prior popup-open claim — no replay");
            return;
        }
        running41 = true;
        telemetryHealthy41 = false;
        testId41 = "cp41-" + UUID.randomUUID();
        seq41 = 0;
        startedAt41 = System.currentTimeMillis();
        baselineHash41 = "-";
        claimStatus41 = "NONE";
        uiClicks41 = 0;
        completeSnapshots41 = 0;
        popupEvidenceSnapshots41 = 0;
        if (run41 != null) { run41.setEnabled(false); run41.setText("POPUP CENSUS RUNNING..."); }
        setStatus41("Telemetry preflight...");
        h41.postDelayed(this::watchdog41, WATCHDOG_MS41);
        telemetryPreflight41();
    }

    private void telemetryPreflight41() {
        JSONObject p = payload41("TELEMETRY_PREFLIGHT", "RUNNING", baseState41());
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> { if (running41 && once.compareAndSet(false, true)) finish41("TELEMETRY_PREFLIGHT_TIMEOUT"); };
        h41.postDelayed(timeout, 8000L);
        new Thread(() -> {
            JSONObject r = upload41(p, NET_TIMEOUT_MS41 + 900);
            runOnUiThread(() -> {
                if (!running41 || !once.compareAndSet(false, true)) return;
                h41.removeCallbacks(timeout);
                if (!r.optBoolean("success", false)) { finish41("TELEMETRY_UNAVAILABLE"); return; }
                telemetryHealthy41 = true;
                phase41("RUN_STARTED", "GUARDED_POPUP_OPEN_CENSUS", baseState41());
                resolveBaseline41();
            });
        }, "cp41-preflight").start();
    }

    private void resolveBaseline41() {
        setStatus41("Resolving closed Medium selector...");
        eval41(scanClosedComposerJs41(), o -> {
            JSONObject st = baseState41();
            copy41(st, o, "success","complete","effort_control_count","effort_semantic","effort_control_hash","effort_has_popup","effort_expanded_true","composer_control_count","candidate_set_hash");
            boolean ok = o.optBoolean("success", false) && o.optBoolean("complete", false)
                    && o.optInt("effort_control_count", -1) == 1
                    && "MEDIUM".equals(o.optString("effort_semantic", ""))
                    && o.optBoolean("effort_has_popup", false)
                    && !o.optBoolean("effort_expanded_true", false)
                    && !"-".equals(o.optString("effort_control_hash", "-"));
            if (!ok) {
                phase41("BASELINE_COMPOSER", "FAIL_CLOSED_MEDIUM_SELECTOR_UNRESOLVED", st);
                finish41("BASELINE_MEDIUM_SELECTOR_UNRESOLVED_ZERO_CLICK");
                return;
            }
            baselineHash41 = o.optString("effort_control_hash", "-");
            phase41("BASELINE_COMPOSER", "PASS_UNIQUE_CLOSED_MEDIUM_SELECTOR", st);
            openPopup41();
        });
    }

    private void openPopup41() {
        setStatus41("Claim -> open selector once...");
        String claimId = "POPUP_OPEN_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0,8);
        boolean committed = prefs41.edit()
                .putString("claim_id", claimId)
                .putString("claim_status", "CLAIMED")
                .putString("claim_action", "EFFORT_POPUP_OPEN_CENSUS")
                .putString("baseline_hash", baselineHash41)
                .commit();
        if (!committed) { finish41("POPUP_OPEN_CLAIM_FAILED_ZERO_CLICK"); return; }
        claimStatus41 = "CLAIMED";
        phase41("DURABLE_CLAIM", "CLAIMED_BEFORE_POPUP_OPEN", baseState41());
        eval41(clickClosedEffortJs41(baselineHash41), r -> {
            JSONObject st = baseState41();
            copy41(st, r, "success","matches","clicked");
            if (!r.optBoolean("success", false) || r.optInt("matches", -1) != 1 || !r.optBoolean("clicked", false)) {
                prefs41.edit().putString("claim_status", "ABORTED_NO_SIDE_EFFECT").commit();
                claimStatus41 = "ABORTED_NO_SIDE_EFFECT";
                phase41("POPUP_OPEN_DISPATCH", "ABORTED_NO_SIDE_EFFECT", st);
                finish41("POPUP_OPEN_NOT_DISPATCHED");
                return;
            }
            uiClicks41 = 1;
            prefs41.edit().putString("claim_status", "DISPATCHED").commit();
            claimStatus41 = "DISPATCHED";
            phase41("POPUP_OPEN_DISPATCH", "DISPATCHED_UNIQUE_MEDIUM_SELECTOR", st);
            h41.postDelayed(() -> snapshot41(0), 180L);
        });
    }

    private void snapshot41(int index) {
        if (!running41) return;
        if (index >= SNAPSHOTS41) {
            if (popupEvidenceSnapshots41 > 0) {
                prefs41.edit().putString("claim_status", "CONFIRMED_POPUP_EVIDENCE").commit();
                claimStatus41 = "CONFIRMED_POPUP_EVIDENCE";
                finish41(completeSnapshots41 == SNAPSHOTS41
                        ? "PASS_POPUP_OPEN_CENSUS_CAPTURED"
                        : "PARTIAL_POPUP_OPEN_CENSUS_CAPTURED");
            } else {
                prefs41.edit().putString("claim_status", "UNCERTAIN_NO_REPLAY").commit();
                claimStatus41 = "UNCERTAIN_NO_REPLAY";
                finish41("POPUP_OPEN_UNCERTAIN_NO_REPLAY");
            }
            return;
        }
        setStatus41("Popup snapshot " + (index + 1) + "/" + SNAPSHOTS41 + "...");
        eval41(scanOpenSurfaceJs41(index, baselineHash41), o -> {
            boolean complete = o.optBoolean("complete", false);
            boolean evidence = o.optBoolean("popup_evidence", false);
            if (complete) completeSnapshots41++;
            if (evidence) popupEvidenceSnapshots41++;
            JSONObject st = baseState41();
            copy41(st, o, "success","complete","snapshot_index","visited_nodes","semantic_candidate_count","light_count","medium_count","heavy_count","auto_count","thinking_count","instant_count","selected_count","trigger_found","trigger_expanded_true","trigger_data_state_open","popup_role_candidate_count","portalish_candidate_count","popup_evidence","candidate_set_hash","ancestor_set_hash");
            JSONArray a = o.optJSONArray("candidates");
            if (a != null) put41(st, "candidates", a);
            phase41("POPUP_SURFACE_SNAPSHOT", complete ? "CAPTURED_COMPLETE" : "CAPTURED_BUDGET_LIMIT", st);
            long delay = index == 0 ? 500L : index == 1 ? 850L : index == 2 ? 1300L : 0L;
            h41.postDelayed(() -> snapshot41(index + 1), delay);
        });
    }

    private String scanClosedComposerJs41() {
        return "(function(){try{const T0=performance.now(),MAXN=6500,MAXMS=180;const N=x=>(x||'').replace(/\\s+/g,' ').trim(),L=x=>N(x).toLowerCase(),TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean),HAS=(s,w)=>TOK(s).includes(w),H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);},V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};let visited=0,complete=true,input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=\"true\"],[role=\"textbox\"]')){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(V(e)){input=e;break;}}let root=null;if(input){let p=input.parentElement;for(let d=0;p&&d<9;d++,p=p.parentElement){const cs=[...p.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio');if(cs.length>=3&&cs.length<=12){root=p;break;}}}const nodes=root?[...root.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio'):[];let effort=0,eh='-',es='-',hp=false,ex=false;const fps=[];for(const e of nodes){const txt=N(e.innerText||e.textContent||''),aria=N(e.getAttribute('aria-label')),title=N(e.getAttribute('title')),acc=N(aria||title||txt),mix=acc+' '+txt;const sl=HAS(mix,'light'),sm=HAS(mix,'medium'),sh=HAS(mix,'heavy'),sa=HAS(mix,'auto');const n=(sl?1:0)+(sm?1:0)+(sh?1:0)+(sa?1:0);const sem=n===1?(sl?'LIGHT':sm?'MEDIUM':sh?'HEAVY':'AUTO'):'NONE';const ah=acc?H(L(acc)):'-',popup=N(e.getAttribute('aria-haspopup')),expanded=L(e.getAttribute('aria-expanded'));const fp=H([ah,sem,popup,expanded,(e.tagName||'').toLowerCase()].join('|'));fps.push(fp);if(sem!=='NONE'){effort++;eh=ah;es=sem;hp=popup!==''&&L(popup)!=='false';ex=expanded==='true';}}fps.sort();if(effort!==1){eh='-';es='-';hp=false;ex=false;}return JSON.stringify({success:true,complete:complete,effort_control_count:effort,effort_semantic:es,effort_control_hash:eh,effort_has_popup:hp,effort_expanded_true:ex,composer_control_count:nodes.length,candidate_set_hash:H(fps.join(','))});}catch(e){return JSON.stringify({success:false,complete:false,effort_control_count:-1});}})();";
    }

    private String clickClosedEffortJs41(String hash) {
        return "(function(){try{const EH='" + js41(hash) + "';const N=x=>(x||'').replace(/\\s+/g,' ').trim(),L=x=>N(x).toLowerCase(),TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean),HAS=(s,w)=>TOK(s).includes(w),H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);},V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};let input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=\"true\"],[role=\"textbox\"]'))if(V(e)){input=e;break;}let root=null;if(input){let p=input.parentElement;for(let d=0;p&&d<9;d++,p=p.parentElement){const cs=[...p.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio');if(cs.length>=3&&cs.length<=12){root=p;break;}}}const m=[];if(root)for(const e of root.querySelectorAll('button,[role=\"button\"]')){if(!V(e)||L(e.getAttribute('role'))==='radio')continue;const txt=N(e.innerText||e.textContent||''),aria=N(e.getAttribute('aria-label')),title=N(e.getAttribute('title')),acc=N(aria||title||txt),mix=acc+' '+txt;const sm=HAS(mix,'medium'),sl=HAS(mix,'light'),sh=HAS(mix,'heavy'),sa=HAS(mix,'auto');const n=(sm?1:0)+(sl?1:0)+(sh?1:0)+(sa?1:0),ah=acc?H(L(acc)):'-',popup=N(e.getAttribute('aria-haspopup'));if(n===1&&sm&&ah===EH&&popup!==''&&L(popup)!=='false'&&!(e.disabled||L(e.getAttribute('aria-disabled'))==='true'))m.push(e);}if(m.length===1){m[0].click();return JSON.stringify({success:true,matches:1,clicked:true});}return JSON.stringify({success:true,matches:m.length,clicked:false});}catch(e){return JSON.stringify({success:false,matches:-1,clicked:false});}})();";
    }

    private String scanOpenSurfaceJs41(int index, String baselineHash) {
        return "(function(){try{const IDX=" + index + ",BH='" + js41(baselineHash) + "',T0=performance.now(),MAXN=12000,MAXMS=260,MAXC=48;const N=x=>(x||'').replace(/\\s+/g,' ').trim(),L=x=>N(x).toLowerCase(),TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean),HAS=(s,w)=>TOK(s).includes(w),H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);},V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};let input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=\"true\"],[role=\"textbox\"]'))if(V(e)){input=e;break;}let composer=null;if(input){let p=input.parentElement;for(let d=0;p&&d<10;d++,p=p.parentElement){if(p.querySelectorAll('button,[role=\"button\"]').length>=3){composer=p;break;}}}const sel='button,[role=\"button\"],[role=\"menuitem\"],[role=\"menuitemradio\"],[role=\"option\"],[role=\"radio\"],[data-radix-collection-item],[aria-checked],[aria-selected]';let visited=0,complete=true,lc=0,mc=0,hc=0,ac=0,tc=0,ic=0,sc=0,triggerFound=false,triggerExpanded=false,triggerOpen=false,popupRoles=0,portalish=0;const out=[],fps=[],afps=[];for(const e of document.querySelectorAll(sel)){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(!V(e))continue;const txt=N(e.innerText||e.textContent||''),aria=N(e.getAttribute('aria-label')),title=N(e.getAttribute('title')),acc=N(aria||title||txt),mix=acc+' '+txt;const sl=HAS(mix,'light'),sm=HAS(mix,'medium'),sh=HAS(mix,'heavy'),sa=HAS(mix,'auto'),st=HAS(mix,'thinking'),si=HAS(mix,'instant');const n=(sl?1:0)+(sm?1:0)+(sh?1:0)+(sa?1:0)+(st?1:0)+(si?1:0);if(n!==1)continue;const sem=sl?'LIGHT':sm?'MEDIUM':sh?'HEAVY':sa?'AUTO':st?'THINKING':'INSTANT';if(sl)lc++;if(sm)mc++;if(sh)hc++;if(sa)ac++;if(st)tc++;if(si)ic++;const ah=acc?H(L(acc)):'-',role=L(e.getAttribute('role'))||((e.tagName||'').toLowerCase()),ds=L(e.getAttribute('data-state')),expanded=L(e.getAttribute('aria-expanded')),selected=L(e.getAttribute('aria-checked'))==='true'||L(e.getAttribute('aria-selected'))==='true'||['checked','selected','on','active'].includes(ds);if(selected)sc++;const trig=ah===BH;if(trig){triggerFound=true;if(expanded==='true')triggerExpanded=true;if(['open','expanded'].includes(ds))triggerOpen=true;}let p=e.parentElement,chain=[],menuAnc=false,portalAnc=false;for(let d=0;p&&d<6;d++,p=p.parentElement){const pr=L(p.getAttribute('role')),slot=L(p.getAttribute('data-slot')),tid=L(p.getAttribute('data-testid')),rad=L(p.getAttribute('data-radix-popper-content-wrapper'));if(['menu','listbox','radiogroup'].includes(pr))menuAnc=true;if(slot.includes('menu')||slot.includes('popover')||slot.includes('dropdown')||rad!=='')portalAnc=true;chain.push(H([pr,slot,tid,rad,(p.tagName||'').toLowerCase()].join('|')));}if(menuAnc)popupRoles++;if(portalAnc)portalish++;const afp=H(chain.join('>')),q={semantic:sem,acc_hash:ah,role:role,enabled:!(e.disabled||L(e.getAttribute('aria-disabled'))==='true'),selected:selected,is_trigger:trig,in_composer:!!(composer&&composer.contains(e)),has_popup:N(e.getAttribute('aria-haspopup'))!=='',expanded_true:expanded==='true',data_state_open:['open','expanded'].includes(ds),has_menu_ancestor:menuAnc,has_portalish_ancestor:portalAnc,ancestor_fp:afp,testid_hash:N(e.getAttribute('data-testid'))?H(L(e.getAttribute('data-testid'))):'-',slot_hash:N(e.getAttribute('data-slot'))?H(L(e.getAttribute('data-slot'))):'-'};q.fp=H([q.semantic,q.acc_hash,q.role,q.enabled,q.selected,q.is_trigger,q.in_composer,q.has_popup,q.expanded_true,q.data_state_open,q.has_menu_ancestor,q.has_portalish_ancestor,q.ancestor_fp,q.testid_hash,q.slot_hash].join('|'));if(out.length<MAXC)out.push(q);fps.push(q.fp);afps.push(afp);}out.sort((a,b)=>(a.semantic+'|'+a.acc_hash+'|'+a.ancestor_fp).localeCompare(b.semantic+'|'+b.acc_hash+'|'+b.ancestor_fp));fps.sort();afps.sort();const semanticCount=lc+mc+hc+ac+tc+ic;const popupEvidence=triggerExpanded||triggerOpen||popupRoles>0||portalish>0||semanticCount>=2;return JSON.stringify({success:true,complete:complete,snapshot_index:IDX,visited_nodes:visited,semantic_candidate_count:semanticCount,light_count:lc,medium_count:mc,heavy_count:hc,auto_count:ac,thinking_count:tc,instant_count:ic,selected_count:sc,trigger_found:triggerFound,trigger_expanded_true:triggerExpanded,trigger_data_state_open:triggerOpen,popup_role_candidate_count:popupRoles,portalish_candidate_count:portalish,popup_evidence:popupEvidence,candidate_set_hash:H(fps.join(',')),ancestor_set_hash:H(afps.join(',')),candidates:out});}catch(e){return JSON.stringify({success:false,complete:false,error_class:'OPEN_SURFACE_SCAN_EXCEPTION'});}})();";
    }

    private void eval41(String js, JsonDone41 done) {
        if (web41 == null) { done.done(new JSONObject()); return; }
        AtomicBoolean once = new AtomicBoolean(false);
        Runnable timeout = () -> { if (once.compareAndSet(false, true)) { JSONObject o=new JSONObject();put41(o,"success",false);put41(o,"complete",false);put41(o,"error_class","EVAL_TIMEOUT");done.done(o);} };
        h41.postDelayed(timeout, EVAL_TIMEOUT_MS41);
        web41.evaluateJavascript(js, value -> {
            if (!once.compareAndSet(false, true)) return;
            h41.removeCallbacks(timeout);
            try {
                String s=value==null?"":value;Object outer=new JSONTokener(s).nextValue();if(outer instanceof String)s=(String)outer;done.done(new JSONObject(s));
            } catch (Exception e) { JSONObject o=new JSONObject();put41(o,"success",false);put41(o,"complete",false);put41(o,"error_class","PARSE_ERROR");done.done(o); }
        });
    }

    private void watchdog41() {
        if (!running41) return;
        if (claimStatus41.equals("DISPATCHED")) {
            prefs41.edit().putString("claim_status", "UNCERTAIN_NO_REPLAY").commit();
            claimStatus41 = "UNCERTAIN_NO_REPLAY";
        }
        finish41("GLOBAL_WATCHDOG");
    }

    private void finish41(String classification) {
        if (!running41) return;
        h41.removeCallbacksAndMessages(null);
        JSONObject st=baseState41();put41(st,"complete_snapshots",completeSnapshots41);put41(st,"popup_evidence_snapshots",popupEvidenceSnapshots41);put41(st,"runtime_ms",System.currentTimeMillis()-startedAt41);put41(st,"raw_text_uploaded",false);put41(st,"raw_html_uploaded",false);put41(st,"cookies_tokens_accessed",false);put41(st,"model_option_clicks",0);
        JSONObject p=payload41("FINAL",classification,st);if(telemetryHealthy41)new Thread(()->upload41(p,NET_TIMEOUT_MS41),"cp41-final").start();
        running41=false;setStatus41(classification);if(run41!=null){run41.setEnabled(!claimStatus41.startsWith("UNCERTAIN"));run41.setText("RUN GUARDED POPUP CENSUS");}
    }

    private void phase41(String phase,String classification,JSONObject state) { if(!running41||!telemetryHealthy41)return;JSONObject p=payload41(phase,classification,state);new Thread(()->upload41(p,NET_TIMEOUT_MS41),"cp41-phase").start(); }
    private JSONObject baseState41(){JSONObject s=new JSONObject();put41(s,"baseline_hash",baselineHash41);put41(s,"claim_status",claimStatus41);put41(s,"ui_clicks",uiClicks41);put41(s,"model_option_clicks",0);put41(s,"raw_text_uploaded",false);put41(s,"raw_html_uploaded",false);put41(s,"cookies_tokens_accessed",false);return s;}
    private JSONObject payload41(String phase,String cls,JSONObject state){JSONObject p=new JSONObject();put41(p,"schema_version",SCHEMA41);put41(p,"scenario_id",SCENARIO41);put41(p,"source_ref",TelemetryConfigV41.SOURCE_REF);put41(p,"collector_id",TelemetryConfigV41.COLLECTOR_ID);put41(p,"test_id",testId41);put41(p,"seq",seq41++);put41(p,"timestamp_epoch_ms",System.currentTimeMillis());put41(p,"phase",phase);put41(p,"classification",cls);put41(p,"state",state);return p;}
    private JSONObject upload41(JSONObject payload,int timeoutMs){JSONObject r=new JSONObject();if(!TelemetryConfigV41.isConfigured()){put41(r,"success",false);return r;}HttpURLConnection c=null;try{c=(HttpURLConnection)new URL(TelemetryConfigV41.WEBHOOK_URL).openConnection();c.setRequestMethod("POST");c.setConnectTimeout(timeoutMs);c.setReadTimeout(timeoutMs);c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json");byte[] b=payload.toString().getBytes(StandardCharsets.UTF_8);c.setFixedLengthStreamingMode(b.length);c.getOutputStream().write(b);int code=c.getResponseCode();put41(r,"success",code>=200&&code<300);}catch(Exception e){put41(r,"success",false);}finally{if(c!=null)c.disconnect();}return r;}
    private WebView findWeb41(View v){if(v instanceof WebView)return(WebView)v;if(v instanceof ViewGroup){ViewGroup g=(ViewGroup)v;for(int i=0;i<g.getChildCount();i++){WebView w=findWeb41(g.getChildAt(i));if(w!=null)return w;}}return null;}
    private boolean isChatGpt41(String url){if(TextUtils.isEmpty(url))return false;try{String h=Uri.parse(url).getHost();if(h==null)return false;h=h.toLowerCase();return h.equals("chatgpt.com")||h.endsWith(".chatgpt.com")||h.equals("openai.com")||h.endsWith(".openai.com");}catch(Exception e){return false;}}
    private int dp41(int v){return Math.round(v*getResources().getDisplayMetrics().density);}
    private void setStatus41(String s){if(status41!=null)status41.setText(s);}
    private static void put41(JSONObject o,String k,Object v){try{o.put(k,v);}catch(Exception ignored){}}
    private static void copy41(JSONObject dst,JSONObject src,String...ks){for(String k:ks)if(src.has(k))put41(dst,k,src.opt(k));}
    private static String js41(String s){return (s==null?"":s).replace("\\","\\\\").replace("'","\\'").replace("\n"," ").replace("\r"," ");}
}
