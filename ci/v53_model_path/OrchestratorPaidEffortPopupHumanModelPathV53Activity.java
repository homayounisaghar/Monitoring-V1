package com.homayounisaghar.chatgptwebviewprobe;

import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.text.TextUtils;
import android.view.View;
import android.view.ViewParent;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.json.JSONObject;
import org.json.JSONTokener;

import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * v0.51: open the already-proven Medium effort popup, then observe the operator's
 * multi-tap path until the exact three-model menu is visible. No effort value
 * write and no automatic model option click occurs in this build.
 */
public class OrchestratorPaidEffortPopupHumanModelPathV53Activity extends OrchestratorAuthModeV34Activity {
    private static final String SCHEMA="cp-v53-paid-effort-popup-human-model-path-v1";
    private static final String SCENARIO="paid-effort-popup-human-model-path";
    private static final int NET_TIMEOUT_MS=3200;
    private static final long OBSERVE_TIMEOUT_MS=30000L;
    private static final int EVAL_TIMEOUT_MS=2600;

    private final Handler h=new Handler(Looper.getMainLooper());
    private WebView web; private TextView status; private Button arm;
    private SharedPreferences prefs;
    private boolean running=false, telemetryHealthy=false;
    private String testId="-", baselineHash="-"; private int seq=0; private long started=0L;
    private int lastObservedClickCount=0;

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        web=findWeb(getWindow().getDecorView());
        prefs=getSharedPreferences("cp_diag_paid_model_effort",MODE_PRIVATE);
        installUi();
        setStatus("v0.51 ready — opens effort popup, then observes your multi-tap path to the 3-model list");
    }

    @Override protected void onDestroy(){
        h.removeCallbacksAndMessages(null);
        ControlPlaneAccessibilityServiceV51.disarmManualModelClickObservation();
        super.onDestroy();
    }

    @Override protected void onResume(){
        super.onResume();
        h.postDelayed(()->{if(!running&&status!=null){
            setStatus(ControlPlaneAccessibilityServiceV51.isObserverReady()
                    ? "Ready — Medium required; ARM opens effort popup, then follow model navigation"
                    : "Accessibility verifier disabled — ARM opens Settings");
        }},180L);
    }

    private void installUi(){
        if(web==null)return;
        ViewParent p=web.getParent(); if(!(p instanceof LinearLayout))return;
        LinearLayout root=(LinearLayout)p;
        for(int i=0;i<root.getChildCount();i++){View c=root.getChildAt(i);if(c!=web)c.setVisibility(View.GONE);}
        web.setMinimumHeight(1); web.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,0,1f));
        LinearLayout panel=new LinearLayout(this); panel.setOrientation(LinearLayout.VERTICAL); panel.setPadding(dp(8),dp(3),dp(8),dp(6));
        status=new TextView(this); status.setTextSize(11f); status.setSingleLine(true); status.setEllipsize(TextUtils.TruncateAt.END);
        panel.addView(status,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT));
        arm=new Button(this); arm.setText("ARM EFFORT POPUP -> OBSERVE MODEL PATH"); arm.setTextSize(13f); arm.setAllCaps(false); arm.setOnClickListener(v->armRun());
        panel.addView(arm,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(47)));
        root.addView(panel,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void armRun(){
        if(running)return;
        if(web==null||!isChatGpt(web.getUrl())){setStatus("Blocked: ChatGPT page not ready");return;}
        if(!ControlPlaneAccessibilityServiceV51.isObserverReady()){
            setStatus("Enable CP WebView semantic verifier, return, then ARM again");
            try{startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));}catch(Exception ignored){}
            return;
        }
        running=true; telemetryHealthy=false; testId="cp53-"+UUID.randomUUID(); seq=0; started=System.currentTimeMillis();
        arm.setEnabled(false); arm.setText("PREPARING EFFORT POPUP..."); setStatus("Telemetry preflight...");
        telemetryPreflight();
    }

    private void telemetryPreflight(){
        JSONObject p=payload("TELEMETRY_PREFLIGHT","RUNNING",baseState()); AtomicBoolean once=new AtomicBoolean(false);
        Runnable timeout=()->{if(running&&once.compareAndSet(false,true))finish("TELEMETRY_PREFLIGHT_TIMEOUT");}; h.postDelayed(timeout,8000L);
        new Thread(()->{JSONObject r=upload(p,NET_TIMEOUT_MS+900); runOnUiThread(()->{
            if(!running||!once.compareAndSet(false,true))return; h.removeCallbacks(timeout);
            if(!r.optBoolean("success",false)){finish("TELEMETRY_UNAVAILABLE");return;}
            telemetryHealthy=true; phase("RUN_STARTED","EFFORT_POPUP_MULTI_TAP_MODEL_PATH_ZERO_MODEL_WRITE",baseState());
            resolveClosedMediumAndOpen();
        });},"cp53-preflight").start();
    }

    private void resolveClosedMediumAndOpen(){
        setStatus("Resolving closed Medium effort control...");
        eval(scanClosedMediumJs(),o->{
            JSONObject st=baseState(); copy(st,o,"success","complete","effort_control_count","effort_semantic","effort_control_hash","effort_has_popup","effort_expanded_true","composer_control_count","candidate_set_hash");
            boolean ok=o.optBoolean("success",false)&&o.optBoolean("complete",false)
                    &&o.optInt("effort_control_count",-1)==1
                    &&"MEDIUM".equals(o.optString("effort_semantic",""))
                    &&o.optBoolean("effort_has_popup",false)
                    &&!o.optBoolean("effort_expanded_true",false)
                    &&!"-".equals(o.optString("effort_control_hash","-"));
            phase("CLOSED_MEDIUM_BASELINE",ok?"PASS_UNIQUE_CLOSED_MEDIUM":"FAIL_CLOSED_MEDIUM_REQUIRED_ZERO_DISPATCH",st);
            if(!ok){finish("SET_EFFORT_TO_MEDIUM_AND_CLOSE_POPUP_THEN_RETRY");return;}
            baselineHash=o.optString("effort_control_hash","-");
            claimAndOpenEffortPopup();
        });
    }

    private void claimAndOpenEffortPopup(){
        String claimId="POPUP_OPEN_"+System.currentTimeMillis()+"_"+UUID.randomUUID().toString().substring(0,8);
        boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_status","CLAIMED")
                .putString("claim_action","EFFORT_POPUP_OPEN_FOR_HUMAN_MODEL_PATH").putString("baseline_hash",baselineHash).commit();
        if(!committed){finish("EFFORT_POPUP_OPEN_CLAIM_FAILED_ZERO_DISPATCH");return;}
        phase("DURABLE_CLAIM","CLAIMED_BEFORE_PROVEN_EFFORT_POPUP_POINTERDOWN",baseState());
        eval(pointerDownMediumJs(baselineHash),o->{
            JSONObject st=baseState(); copy(st,o,"success","matches","dispatched","event_class","default_prevented","matched_semantic","matched_expanded");
            boolean sent=o.optBoolean("success",false)&&o.optInt("matches",-1)==1&&o.optBoolean("dispatched",false);
            phase("EFFORT_POPUP_OPEN_DISPATCH",sent?"DISPATCHED_PROVEN_MEDIUM_SELECTOR":"ABORTED_NO_SIDE_EFFECT",st);
            if(!sent){prefs.edit().putString("claim_status","ABORTED_NO_SIDE_EFFECT").commit();finish("EFFORT_POPUP_OPEN_NOT_DISPATCHED");return;}
            prefs.edit().putString("claim_status","DISPATCHED").commit();
            h.postDelayed(this::verifyPopupAndArmObserver,260L);
        });
    }

    private void verifyPopupAndArmObserver(){
        eval(scanOpenEffortPopupJs(),o->{
            JSONObject st=baseState(); copy(st,o,"success","complete","visible_slider_count","slider_current","slider_min","slider_max","role_slider_count","menu_count","structure_hash");
            boolean ready=o.optBoolean("success",false)&&o.optBoolean("complete",false)
                    &&o.optInt("visible_slider_count",0)==1
                    &&Math.abs(o.optDouble("slider_current",-99)-1.0)<0.001
                    &&Math.abs(o.optDouble("slider_min",-99)-0.0)<0.001
                    &&Math.abs(o.optDouble("slider_max",-99)-4.0)<0.001;
            phase("EFFORT_POPUP_DOM_READY",ready?"PASS_PROVEN_MEDIUM_SLIDER_VISIBLE":"EFFORT_POPUP_DOM_NOT_VERIFIED_ZERO_MODEL_WRITE",st);
            if(!ready){finish("EFFORT_POPUP_DOM_NOT_VERIFIED_ZERO_MODEL_WRITE");return;}
            JSONObject armed=ControlPlaneAccessibilityServiceV51.armManualModelClickObservation();
            if(!armed.optBoolean("success",false)){finish("OBSERVER_ARM_FAILED_ZERO_MODEL_WRITE");return;}
            lastObservedClickCount=0;
            arm.setText("OBSERVING YOUR MODEL NAVIGATION TAPS...");
            setStatus("ARMED — tap upper effort control; continue until 3-model list appears, then STOP");
            h.postDelayed(()->pollHumanModelPath(0),120L);
            h.postDelayed(()->{if(running)finish("HUMAN_MODEL_PATH_TIMEOUT_EXACT_MENU_NOT_CAPTURED");},OBSERVE_TIMEOUT_MS);
        });
    }

    private void pollHumanModelPath(int n){
        if(!running)return;
        JSONObject ev=ControlPlaneAccessibilityServiceV51.captureManualClickEvidence();
        int clicks=ev.optInt("clicked_event_count",0);
        String fallback=ev.optString("nearest_model_hash","-"); if("-".equals(fallback))fallback=ev.optString("source_label_hash","-");
        JSONObject menu=ControlPlaneAccessibilityServiceV50.captureModelMenu(fallback);
        boolean exact=menu.optBoolean("success",false)&&menu.optBoolean("complete",false)
                &&menu.optBoolean("exact_expected_set",false)&&menu.optInt("group_count",0)==1&&menu.optInt("option_count",0)==3;

        if(clicks>lastObservedClickCount){
            lastObservedClickCount=clicks;
            JSONObject st=baseState(); put(st,"human_click_index",clicks);
            copy(st,ev,"observed_event_count","clicked_event_count","human_click_seen","last_event_type","source_label_hash","source_semantic","nearest_model_hash","nearest_model_semantic","source_class_hash","action_set_hash","ancestry_hash","source_clickable","source_selected");
            copy(st,menu,"visited_count","web_node_count","group_count","option_count","selected_count","group_hash","current_option_hash","target_option_hash","current_semantic","target_semantic","exact_expected_set","selection_basis","option_set_hash");
            phase("HUMAN_MODEL_NAV_CLICK_"+clicks,exact?"EXACT_MODEL_MENU_VISIBLE_AFTER_CLICK":"NAV_CLICK_CAPTURED_WAITING_FOR_EXACT_MODEL_MENU",st);
        }

        if(exact){
            JSONObject st=baseState(); put(st,"human_click_count",clicks);
            copy(st,ev,"observed_event_count","clicked_event_count","human_click_seen","source_label_hash","source_semantic","nearest_model_hash","nearest_model_semantic","source_class_hash","action_set_hash","ancestry_hash");
            copy(st,menu,"visited_count","web_node_count","group_count","option_count","selected_count","group_hash","current_option_hash","target_option_hash","current_semantic","target_semantic","exact_expected_set","selection_basis","option_set_hash");
            phase("EXACT_MODEL_MENU_CAPTURE","PASS_MULTI_TAP_HUMAN_PATH_TO_EXACT_THREE_MODEL_MENU",st);
            finish("PASS_MULTI_TAP_HUMAN_PATH_TO_EXACT_MODEL_MENU_ZERO_MODEL_WRITE");
            return;
        }
        h.postDelayed(()->pollHumanModelPath(n+1),120L);
    }

    private JSONObject baseState(){JSONObject o=new JSONObject();put(o,"effort_popup_open_dispatches_by_app",0);put(o,"effort_value_writes_by_app",0);put(o,"model_trigger_clicks_by_app",0);put(o,"model_option_clicks_by_app",0);put(o,"pro_write_attempted",false);put(o,"raw_text_uploaded",false);put(o,"raw_html_uploaded",false);put(o,"cookies_tokens_accessed",false);put(o,"geometry_click_used",false);return o;}

    private void finish(String c){
        if(!running)return;
        JSONObject st=baseState(); JSONObject ev=ControlPlaneAccessibilityServiceV51.captureManualClickEvidence();
        copy(st,ev,"observed_event_count","clicked_event_count","human_click_seen","source_label_hash","source_semantic","nearest_model_hash","nearest_model_semantic","source_class_hash","action_set_hash","ancestry_hash","source_clickable","source_selected");
        put(st,"runtime_ms",System.currentTimeMillis()-started);
        if(telemetryHealthy)new Thread(()->upload(payload("FINAL",c,st),NET_TIMEOUT_MS),"cp53-final").start();
        ControlPlaneAccessibilityServiceV51.disarmManualModelClickObservation();
        running=false; setStatus(c); arm.setEnabled(true); arm.setText("ARM EFFORT POPUP -> OBSERVE MODEL PATH");
    }

    private void phase(String ph,String cl,JSONObject st){if(!running||!telemetryHealthy)return;JSONObject p=payload(ph,cl,st);new Thread(()->upload(p,NET_TIMEOUT_MS),"cp53-phase-"+seq).start();}
    private JSONObject payload(String ph,String cl,JSONObject st){JSONObject p=new JSONObject();put(p,"schema_version",SCHEMA);put(p,"scenario_id",SCENARIO);put(p,"source_ref",TelemetryConfigV53.SOURCE_REF);put(p,"collector_id",TelemetryConfigV53.COLLECTOR_ID);put(p,"test_id",testId);put(p,"seq",seq++);put(p,"timestamp_epoch_ms",System.currentTimeMillis());put(p,"phase",ph);put(p,"classification",cl);put(p,"state",st);return p;}

    private JSONObject upload(JSONObject payload,int timeoutMs){JSONObject r=new JSONObject();HttpURLConnection c=null;try{if(!TelemetryConfigV53.CONFIGURED){put(r,"success",false);return r;}URL u=new URL(TelemetryConfigV53.WEBHOOK_URL);c=(HttpURLConnection)u.openConnection();c.setRequestMethod("POST");c.setConnectTimeout(timeoutMs);c.setReadTimeout(timeoutMs);c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json");byte[] body=payload.toString().getBytes(StandardCharsets.UTF_8);c.getOutputStream().write(body);int code=c.getResponseCode();put(r,"success",code>=200&&code<300);put(r,"http_code",code);return r;}catch(Exception e){put(r,"success",false);put(r,"error_class",e.getClass().getSimpleName());return r;}finally{if(c!=null)c.disconnect();}}

    private void eval(String js, JsonDone done){
        if(web==null){done.done(new JSONObject());return;}
        AtomicBoolean once=new AtomicBoolean(false);
        Runnable timeout=()->{if(once.compareAndSet(false,true)){JSONObject o=new JSONObject();put(o,"success",false);put(o,"complete",false);put(o,"error_class","EVAL_TIMEOUT");done.done(o);}};
        h.postDelayed(timeout,EVAL_TIMEOUT_MS);
        web.evaluateJavascript(js,value->{if(!once.compareAndSet(false,true))return;h.removeCallbacks(timeout);try{String s=value==null?"":value;Object outer=new JSONTokener(s).nextValue();if(outer instanceof String)s=(String)outer;done.done(new JSONObject(s));}catch(Exception e){JSONObject o=new JSONObject();put(o,"success",false);put(o,"complete",false);put(o,"error_class","PARSE_ERROR");done.done(o);}});
    }

    private String scanClosedMediumJs(){
        return "(function(){try{const T0=performance.now(),MAXN=6500,MAXMS=180;const N=x=>(x||'').replace(/\\s+/g,' ').trim(),L=x=>N(x).toLowerCase(),TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean),HAS=(s,w)=>TOK(s).includes(w),H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);},V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};let visited=0,complete=true,input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=\"true\"],[role=\"textbox\"]')){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}if(V(e)){input=e;break;}}let root=null;if(input){let p=input.parentElement;for(let d=0;p&&d<9;d++,p=p.parentElement){const cs=[...p.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio');if(cs.length>=3&&cs.length<=12){root=p;break;}}}const nodes=root?[...root.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio'):[];let effort=0,eh='-',es='-',hp=false,ex=false;const fps=[];for(const e of nodes){const txt=N(e.innerText||e.textContent||''),aria=N(e.getAttribute('aria-label')),title=N(e.getAttribute('title')),acc=N(aria||title||txt),mix=acc+' '+txt;const sm=HAS(mix,'medium');const sem=sm?'MEDIUM':'NONE';const ah=acc?H(L(acc)):'-',popup=N(e.getAttribute('aria-haspopup')),expanded=L(e.getAttribute('aria-expanded'));const fp=H([ah,sem,popup,expanded,(e.tagName||'').toLowerCase()].join('|'));fps.push(fp);if(sem==='MEDIUM'){effort++;eh=ah;es=sem;hp=popup!==''&&L(popup)!=='false';ex=expanded==='true';}}fps.sort();if(effort!==1){eh='-';es='-';hp=false;ex=false;}return JSON.stringify({success:true,complete:complete,effort_control_count:effort,effort_semantic:es,effort_control_hash:eh,effort_has_popup:hp,effort_expanded_true:ex,composer_control_count:nodes.length,candidate_set_hash:H(fps.join(','))});}catch(e){return JSON.stringify({success:false,complete:false,effort_control_count:-1});}})();";
    }

    private String scanOpenEffortPopupJs(){
        return "(function(){try{const N=x=>(x||'').replace(/\\s+/g,' ').trim(),L=x=>N(x).toLowerCase(),V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}},H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};const all=[...document.querySelectorAll('[role=\"slider\"]')],vis=all.filter(V),exact=vis.filter(e=>Number(e.getAttribute('aria-valuemin'))===0&&Number(e.getAttribute('aria-valuemax'))===4&&Number(e.getAttribute('aria-valuenow'))===1);const s=exact.length===1?exact[0]:null;const fp=s?H([(s.tagName||'').toLowerCase(),L(s.getAttribute('role')),s.getAttribute('aria-valuemin'),s.getAttribute('aria-valuemax'),L(s.getAttribute('aria-orientation'))].join('|')):'-';const menus=[...document.querySelectorAll('[role=\"menu\"]')].filter(V);return JSON.stringify({success:true,complete:true,role_slider_count:all.length,visible_slider_count:exact.length,slider_current:s?Number(s.getAttribute('aria-valuenow')):-99,slider_min:s?Number(s.getAttribute('aria-valuemin')):-99,slider_max:s?Number(s.getAttribute('aria-valuemax')):-99,menu_count:menus.length,structure_hash:fp});}catch(e){return JSON.stringify({success:false,complete:false,visible_slider_count:-1});}})();";
    }

    private String pointerDownMediumJs(String hash){
        return "(function(){try{const EH='"+js(hash)+"';const N=x=>(x||'').replace(/\\s+/g,' ').trim(),L=x=>N(x).toLowerCase(),TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean),HAS=(s,w)=>TOK(s).includes(w),H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);},V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};let input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=\"true\"],[role=\"textbox\"]'))if(V(e)){input=e;break;}let root=null;if(input){let p=input.parentElement;for(let d=0;p&&d<9;d++,p=p.parentElement){const cs=[...p.querySelectorAll('button,[role=\"button\"]')].filter(V).filter(e=>L(e.getAttribute('role'))!=='radio');if(cs.length>=3&&cs.length<=12){root=p;break;}}}const m=[];if(root)for(const e of root.querySelectorAll('button,[role=\"button\"]')){if(!V(e)||L(e.getAttribute('role'))==='radio')continue;const txt=N(e.innerText||e.textContent||''),aria=N(e.getAttribute('aria-label')),title=N(e.getAttribute('title')),acc=N(aria||title||txt),mix=acc+' '+txt,ah=acc?H(L(acc)):'-',popup=N(e.getAttribute('aria-haspopup')),expanded=L(e.getAttribute('aria-expanded'));if(HAS(mix,'medium')&&ah===EH&&popup!==''&&L(popup)!=='false'&&expanded!=='true'&&!(e.disabled||L(e.getAttribute('aria-disabled'))==='true'))m.push(e);}if(m.length!==1)return JSON.stringify({success:true,matches:m.length,dispatched:false,event_class:'NONE',default_prevented:false,matched_semantic:'NONE',matched_expanded:'-'});const e=m[0];try{e.focus({preventScroll:true});}catch(_){}let ev,kind;if(typeof PointerEvent==='function'){ev=new PointerEvent('pointerdown',{bubbles:true,cancelable:true,composed:true,pointerId:1,pointerType:'mouse',isPrimary:true,button:0,buttons:1,ctrlKey:false});kind='POINTERDOWN';}else{ev=new MouseEvent('mousedown',{bubbles:true,cancelable:true,composed:true,view:window,button:0,buttons:1,ctrlKey:false});kind='MOUSEDOWN_FALLBACK';}const accepted=e.dispatchEvent(ev);return JSON.stringify({success:true,matches:1,dispatched:true,event_class:kind,default_prevented:!accepted,matched_semantic:'MEDIUM',matched_expanded:L(e.getAttribute('aria-expanded'))});}catch(e){return JSON.stringify({success:false,matches:-1,dispatched:false,event_class:'EXCEPTION',default_prevented:false});}})();";
    }

    private WebView findWeb(View v){if(v instanceof WebView)return(WebView)v;if(v instanceof android.view.ViewGroup){android.view.ViewGroup g=(android.view.ViewGroup)v;for(int i=0;i<g.getChildCount();i++){WebView w=findWeb(g.getChildAt(i));if(w!=null)return w;}}return null;}
    private boolean isChatGpt(String u){if(u==null)return false;try{Uri x=Uri.parse(u);String hh=x.getHost();return hh!=null&&(hh.equals("chatgpt.com")||hh.endsWith(".chatgpt.com"));}catch(Exception e){return false;}}
    private String js(String s){return s==null?"":s.replace("\\","\\\\").replace("'","\\'").replace("\r"," ").replace("\n"," ");}
    private int dp(int x){return(int)(x*getResources().getDisplayMetrics().density+0.5f);}
    private void setStatus(String s){if(status!=null)status.setText(s);}
    private interface JsonDone{void done(JSONObject o);}
    private static void put(JSONObject o,String k,Object v){try{o.put(k,v);}catch(Exception ignored){}}
    private static void copy(JSONObject d,JSONObject s,String...ks){for(String k:ks)if(s.has(k))try{d.put(k,s.get(k));}catch(Exception ignored){}}
}
