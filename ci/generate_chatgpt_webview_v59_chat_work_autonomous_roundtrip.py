#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# Build on the exact v0.56 observation lineage. v0.57 turns only the observed
# Chat/Work semantic contract into a fail-closed autonomous reversible roundtrip.
# No model-option or effort write path is added.
runpy.run_path("ci/generate_chatgpt_webview_v58_chat_work_manual_observation.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
ACT=PKG/"OrchestratorChatWorkAutonomousRoundtripV59Activity.java"

activity=r'''package com.homayounisaghar.chatgptwebviewprobe;

import android.app.Activity;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class OrchestratorChatWorkAutonomousRoundtripV59Activity extends Activity {
    private static final String SCHEMA="cp-v59-chat-work-autonomous-roundtrip-v1";
    private static final String SCENARIO="chat-work-autonomous-roundtrip";
    private static final String CHAT_LABEL_HASH="a24bf9ab";
    private static final String WORK_LABEL_HASH="5b98d260";
    private static final String CHAT_ACTIVE_SET_HASH="265f199e";
    private static final String WORK_ACTIVE_SET_HASH="efc8a127";
    private static final int PURPOSE_WORK=1;
    private static final int PURPOSE_CHAT_RESTORE=2;
    private static final int MAX_RECEIPT_POLLS=28;
    private static final long RECEIPT_POLL_MS=250L;

    private final Handler h=new Handler(Looper.getMainLooper());
    private final ExecutorService net=Executors.newSingleThreadExecutor();
    private WebView web;
    private TextView status;
    private SharedPreferences prefs;
    private boolean running=false;
    private int telemetrySeq=0;
    private int pageUiDispatches=0;
    private int modelOptionWrites=0;
    private int effortWrites=0;
    private boolean targetReceipt=false;
    private boolean restoreReceipt=false;
    private String testId="-";
    private String chatStructHash="-";
    private String workStructHash="-";
    private String claimStatus="IDLE";
    private long startedMs=0L;

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        prefs=getSharedPreferences("cp_v59_chat_work_claim",MODE_PRIVATE);
        LinearLayout root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);
        Button run=new Button(this); run.setText("RUN AUTONOMOUS CHAT/WORK ROUNDTRIP");
        run.setOnClickListener(v->startRoundtrip());
        root.addView(run,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(52)));
        status=new TextView(this); status.setTextSize(12f); status.setPadding(dp(8),dp(6),dp(8),dp(6));
        status.setText("v0.57 autonomous Chat/Work roundtrip ready.\nFail-closed: exact Chat start required; no model/effort writes.");
        root.addView(status,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(95)));
        web=new WebView(this);
        WebSettings s=web.getSettings(); s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setDatabaseEnabled(true);
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient(){
            @Override public void onPageStarted(WebView v,String u,Bitmap f){super.onPageStarted(v,u,f);}
            @Override public void onPageFinished(WebView v,String u){super.onPageFinished(v,u);if(!running)status.setText("v0.57 ready.\nCurrent UI must be exactly Chat-active on HOME before RUN.");}
        });
        root.addView(web,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,0,1f));
        setContentView(root);
        web.loadUrl("https://chatgpt.com/");
    }

    private void startRoundtrip(){
        if(running)return;
        running=true; telemetrySeq=0; pageUiDispatches=0; modelOptionWrites=0; effortWrites=0;
        targetReceipt=false; restoreReceipt=false; chatStructHash="-"; workStructHash="-";
        testId="cp57-"+UUID.randomUUID(); startedMs=System.currentTimeMillis(); claimStatus="RUNNING_START_GATE";
        prefs.edit().putString("test_id",testId).putString("claim_status",claimStatus).commit();
        emit("ROUNDTRIP_STARTED","RUNNING",baseState());
        status.setText("Checking exact Chat/Work start state...");
        h.postDelayed(this::resolveStart,300L);
    }

    private void resolveStart(){
        if(!running)return;
        eval(scanJs(),o->{
            if(!running)return;
            boolean ok=exactPair(o)&&stateChat(o)&&pageUiDispatches==0;
            emitSnapshot("START_GATE",ok?"PASS_EXACT_CHAT_ACTIVE_BASELINE":"CHAT_WORK_START_NOT_EXACT_CHAT_ACTIVE_ZERO_WRITE",o);
            if(!ok){finish("CHAT_WORK_START_NOT_EXACT_CHAT_ACTIVE_ZERO_WRITE");return;}
            chatStructHash=o.optString("chat_struct_hash","-");
            workStructHash=o.optString("work_struct_hash","-");
            if("-".equals(chatStructHash)||"-".equals(workStructHash)||chatStructHash.equals(workStructHash)){
                finish("CHAT_WORK_STRUCTURAL_IDENTITY_INVALID_ZERO_WRITE");return;
            }
            claimAndClick(PURPOSE_WORK);
        });
    }

    private void claimAndClick(final int purpose){
        if(!running)return;
        if(purpose==PURPOSE_WORK){
            if(pageUiDispatches!=0||targetReceipt){finish("WORK_CLICK_REPLAY_BLOCKED");return;}
            claimStatus="CLAIMED_BEFORE_WORK_CLICK";
        } else {
            if(!targetReceipt||pageUiDispatches!=1){finish("CHAT_RESTORE_NOT_ALLOWED_WITHOUT_WORK_RECEIPT");return;}
            claimStatus="CLAIMED_BEFORE_CHAT_RESTORE_CLICK";
        }
        prefs.edit().putString("test_id",testId).putString("claim_status",claimStatus)
                .putString("chat_struct_hash",chatStructHash).putString("work_struct_hash",workStructHash).commit();
        JSONObject claim=baseState(); put(claim,"purpose",purpose); put(claim,"chat_struct_hash",chatStructHash); put(claim,"work_struct_hash",workStructHash);
        emit("DURABLE_CLAIM",claimStatus,claim);
        status.setText(purpose==PURPOSE_WORK?"CLAIMED; switching Chat -> Work...":"Work receipt confirmed; CLAIMED; restoring Work -> Chat...");
        eval(clickJs(purpose),o->{
            if(!running)return;
            boolean dispatched=o.optBoolean("success",false)&&o.optBoolean("dispatched",false)&&o.optBoolean("click_observed",false)
                    &&o.optInt("match_count",0)==1&&sameStructs(o);
            emitSnapshot(purpose==PURPOSE_WORK?"WORK_CLICK_DISPATCH":"CHAT_RESTORE_CLICK_DISPATCH",
                    dispatched?"PASS_EXACT_ELEMENT_CLICK_DISPATCHED":"CLICK_DISPATCH_UNCERTAIN_NO_REPLAY",o);
            if(!dispatched){
                claimStatus=purpose==PURPOSE_WORK?"UNCERTAIN_AFTER_WORK_CLAIM":"UNCERTAIN_CHAT_RESTORE_REQUIRED";
                prefs.edit().putString("claim_status",claimStatus).commit();
                finish("CLICK_DISPATCH_UNCERTAIN_NO_REPLAY");return;
            }
            pageUiDispatches++;
            h.postDelayed(()->pollReceipt(purpose,0,0),RECEIPT_POLL_MS);
        });
    }

    private void pollReceipt(final int purpose,final int attempt,final int stableHits){
        if(!running)return;
        eval(scanJs(),o->{
            if(!running)return;
            boolean match=sameStructs(o)&&(purpose==PURPOSE_WORK?stateWork(o):stateChat(o));
            int hits=match?stableHits+1:0;
            if(match&&(hits==1||hits==2)) emitSnapshot(purpose==PURPOSE_WORK?"WORK_RECEIPT":"CHAT_RESTORE_RECEIPT",
                    hits>=2?(purpose==PURPOSE_WORK?"PASS_STABLE_WORK_RECEIPT":"PASS_STABLE_CHAT_RESTORE_RECEIPT"):"RECEIPT_CANDIDATE_1_OF_2",o);
            if(hits>=2){
                if(purpose==PURPOSE_WORK){
                    targetReceipt=true; claimStatus="WORK_RECEIPT_CONFIRMED";
                    prefs.edit().putString("claim_status",claimStatus).commit();
                    h.postDelayed(()->prepareRestore(o),350L);
                }else{
                    restoreReceipt=true; claimStatus="CHAT_RESTORE_CONFIRMED";
                    prefs.edit().putString("claim_status",claimStatus).commit();
                    boolean pass=pageUiDispatches==2&&targetReceipt&&restoreReceipt&&modelOptionWrites==0&&effortWrites==0;
                    finish(pass?"PASS_AUTONOMOUS_CHAT_WORK_CHAT_ROUNDTRIP":"CHAT_WORK_ROUNDTRIP_INCOMPLETE");
                }
                return;
            }
            if(attempt>=MAX_RECEIPT_POLLS){
                claimStatus=purpose==PURPOSE_WORK?"UNCERTAIN_WORK_RECEIPT_NO_RESTORE":"UNCERTAIN_CHAT_RESTORE_REQUIRED";
                prefs.edit().putString("claim_status",claimStatus).commit();
                finish(purpose==PURPOSE_WORK?"WORK_RECEIPT_UNRESOLVED_NO_REPLAY_NO_RESTORE":"CHAT_RESTORE_RECEIPT_UNRESOLVED_NO_REPLAY");
                return;
            }
            if(attempt==0||attempt==10||attempt==20) emitSnapshot(purpose==PURPOSE_WORK?"WORK_RECEIPT_WAIT":"CHAT_RESTORE_RECEIPT_WAIT","READ_ONLY_POLL_NO_REPLAY",o);
            h.postDelayed(()->pollReceipt(purpose,attempt+1,hits),RECEIPT_POLL_MS);
        });
    }

    private void prepareRestore(JSONObject ignored){
        if(!running)return;
        if(!targetReceipt||pageUiDispatches!=1){finish("CHAT_RESTORE_NOT_ALLOWED_WITHOUT_WORK_RECEIPT");return;}
        eval(scanJs(),o->{
            if(!running)return;
            boolean ok=sameStructs(o)&&stateWork(o);
            emitSnapshot("RESTORE_GATE",ok?"PASS_FRESH_WORK_STATE_BEFORE_CHAT_RESTORE":"RESTORE_GATE_STATE_DRIFT_NO_REPLAY",o);
            if(!ok){claimStatus="UNCERTAIN_WORK_STATE_MANUAL_CHAT_RESTORE_REQUIRED";prefs.edit().putString("claim_status",claimStatus).commit();finish("RESTORE_GATE_STATE_DRIFT_NO_REPLAY");return;}
            claimAndClick(PURPOSE_CHAT_RESTORE);
        });
    }

    private boolean exactPair(JSONObject o){
        if(!o.optBoolean("success",false)||!"complete".equals(o.optString("ready",""))||!"HOME".equals(o.optString("route_class","")))return false;
        if(o.optInt("chat_count",0)!=1||o.optInt("work_count",0)!=1)return false;
        if(o.optInt("chat_selected",-1)!=0||o.optInt("work_selected",-1)!=0||o.optInt("chat_pressed",-1)!=0||o.optInt("work_pressed",-1)!=0)return false;
        if(o.optInt("chat_disabled",1)!=0||o.optInt("work_disabled",1)!=0)return false;
        if(!CHAT_LABEL_HASH.equals(o.optString("chat_label_hash",""))||!WORK_LABEL_HASH.equals(o.optString("work_label_hash","")))return false;
        return !"-".equals(o.optString("chat_struct_hash","-"))&&!"-".equals(o.optString("work_struct_hash","-"));
    }

    private boolean stateChat(JSONObject o){
        return exactPair(o)&&"CHAT".equals(o.optString("semantic_state",""))&&"ACTIVE".equals(o.optString("chat_data_state",""))
                &&!"ACTIVE".equals(o.optString("work_data_state",""))&&CHAT_ACTIVE_SET_HASH.equals(o.optString("active_set_hash",""));
    }
    private boolean stateWork(JSONObject o){
        return exactPair(o)&&"WORK".equals(o.optString("semantic_state",""))&&"ACTIVE".equals(o.optString("work_data_state",""))
                &&!"ACTIVE".equals(o.optString("chat_data_state",""))&&WORK_ACTIVE_SET_HASH.equals(o.optString("active_set_hash",""));
    }
    private boolean sameStructs(JSONObject o){
        return exactPair(o)&&chatStructHash.equals(o.optString("chat_struct_hash",""))&&workStructHash.equals(o.optString("work_struct_hash",""));
    }

    private String scanJs(){
        return "(function(){try{"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};"+
            "const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};"+
            "const B=(e,n)=>e.getAttribute(n)==='true'?1:0;"+
            "const DS=e=>{const v=N(e.getAttribute('data-state'));if(v==='active'||v==='selected'||v==='checked'||v==='on')return 'ACTIVE';if(v==='inactive'||v==='unselected'||v==='unchecked'||v==='off')return 'INACTIVE';return v?'OTHER':'NONE';};"+
            "const RC=()=>{const p=location.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';return 'OTHER_ROUTE';};"+
            "const cand=Array.from(document.querySelectorAll('button,a,[role],[aria-selected],[aria-pressed],[data-state],[data-testid]')).filter(V);let C=[],W=[];"+
            "for(const e of cand){const tag=(e.tagName||'').toLowerCase();const role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none'));const actionable=tag==='button'||tag==='a'||['button','tab','menuitem','radio','switch','option'].includes(role)||e.hasAttribute('aria-selected')||e.hasAttribute('aria-pressed')||e.hasAttribute('data-state');if(!actionable)continue;const label=N(e.getAttribute('aria-label')||e.innerText||e.textContent||'');let sem=label==='chat'?'CHAT':(label==='work'?'WORK':'OTHER');if(sem==='OTHER')continue;const lh=H(label),th=H(e.getAttribute('data-testid')||''),hp=N(e.getAttribute('aria-haspopup'))||'none',disabled=e.hasAttribute('disabled')?1:0,sel=B(e,'aria-selected'),prs=B(e,'aria-pressed'),ds=DS(e),sh=H([tag,role,sem,lh,th,hp].join('|'));const r={sem:sem,tag:tag,role:role,label_hash:lh,testid_hash:th,haspopup:hp,disabled:disabled,selected:sel,pressed:prs,data_state:ds,struct_hash:sh};if(sem==='CHAT')C.push(r);else W.push(r);}"+
            "const c=C.length===1?C[0]:null,w=W.length===1?W[0]:null;const ca=c&&c.data_state==='ACTIVE',wa=w&&w.data_state==='ACTIVE';let ss='UNKNOWN';if(c&&w&&c.selected===0&&w.selected===0&&c.pressed===0&&w.pressed===0){if(ca&&!wa)ss='CHAT';else if(wa&&!ca)ss='WORK';}const act=[];if(ca)act.push(c.label_hash);if(wa)act.push(w.label_hash);act.sort();"+
            "return JSON.stringify({success:true,ready:document.readyState,route_class:RC(),chat_count:C.length,work_count:W.length,chat_label_hash:c?c.label_hash:'-',work_label_hash:w?w.label_hash:'-',chat_struct_hash:c?c.struct_hash:'-',work_struct_hash:w?w.struct_hash:'-',chat_tag:c?c.tag:'-',work_tag:w?w.tag:'-',chat_role:c?c.role:'-',work_role:w?w.role:'-',chat_testid_hash:c?c.testid_hash:'-',work_testid_hash:w?w.testid_hash:'-',chat_selected:c?c.selected:-1,work_selected:w?w.selected:-1,chat_pressed:c?c.pressed:-1,work_pressed:w?w.pressed:-1,chat_disabled:c?c.disabled:-1,work_disabled:w?w.disabled:-1,chat_data_state:c?c.data_state:'NONE',work_data_state:w?w.data_state:'NONE',semantic_state:ss,active_set_hash:H(act.join('|')),pair_fingerprint:H(JSON.stringify([c?c.struct_hash:'-',c?c.data_state:'-',w?w.struct_hash:'-',w?w.data_state:'-',ss]))});"+
            "}catch(e){return JSON.stringify({success:false,ready:'error',route_class:'ERROR',chat_count:0,work_count:0,semantic_state:'UNKNOWN'});}})();";
    }

    private String clickJs(int purpose){
        final String target=purpose==PURPOSE_WORK?"WORK":"CHAT";
        final String expected=purpose==PURPOSE_WORK?workStructHash:chatStructHash;
        final String expectedCurrent=purpose==PURPOSE_WORK?"CHAT":"WORK";
        return "(function(){try{"+
            "const TARGET='"+target+"',EXPECTED='"+expected+"',CURRENT='"+expectedCurrent+"';"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};"+
            "const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const DS=e=>{const v=N(e.getAttribute('data-state'));return (v==='active'||v==='selected'||v==='checked'||v==='on')?'ACTIVE':((v==='inactive'||v==='unselected'||v==='unchecked'||v==='off')?'INACTIVE':(v?'OTHER':'NONE'));};"+
            "const all=Array.from(document.querySelectorAll('button,a,[role],[aria-selected],[aria-pressed],[data-state],[data-testid]')).filter(V);let rows=[];for(const e of all){const tag=(e.tagName||'').toLowerCase();const role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none'));const actionable=tag==='button'||tag==='a'||['button','tab','menuitem','radio','switch','option'].includes(role)||e.hasAttribute('aria-selected')||e.hasAttribute('aria-pressed')||e.hasAttribute('data-state');if(!actionable)continue;const label=N(e.getAttribute('aria-label')||e.innerText||e.textContent||'');const sem=label==='chat'?'CHAT':(label==='work'?'WORK':'OTHER');if(sem==='OTHER')continue;const sh=H([tag,role,sem,H(label),H(e.getAttribute('data-testid')||''),N(e.getAttribute('aria-haspopup'))||'none'].join('|'));rows.push({e:e,sem:sem,sh:sh,ds:DS(e),sel:e.getAttribute('aria-selected')==='true'?1:0,prs:e.getAttribute('aria-pressed')==='true'?1:0,disabled:e.hasAttribute('disabled')?1:0});}"+
            "const C=rows.filter(r=>r.sem==='CHAT'),W=rows.filter(r=>r.sem==='WORK');if(C.length!==1||W.length!==1)return JSON.stringify({success:false,reason:'PAIR_COUNT',match_count:0,dispatched:false,click_observed:false});const c=C[0],w=W[0];let current=(c.ds==='ACTIVE'&&w.ds!=='ACTIVE'&&c.sel===0&&w.sel===0&&c.prs===0&&w.prs===0)?'CHAT':((w.ds==='ACTIVE'&&c.ds!=='ACTIVE'&&c.sel===0&&w.sel===0&&c.prs===0&&w.prs===0)?'WORK':'UNKNOWN');const t=TARGET==='WORK'?w:c;if(current!==CURRENT||t.sh!==EXPECTED||t.disabled!==0)return JSON.stringify({success:false,reason:'STATE_OR_HASH',match_count:t.sh===EXPECTED?1:0,dispatched:false,click_observed:false,chat_struct_hash:c.sh,work_struct_hash:w.sh,semantic_state:current});let observed=false;t.e.addEventListener('click',()=>{observed=true;},{capture:true,once:true});t.e.click();return JSON.stringify({success:true,reason:'ELEMENT_CLICK',match_count:1,dispatched:true,click_observed:observed,chat_struct_hash:c.sh,work_struct_hash:w.sh,semantic_state:current,target_semantic:TARGET});"+
            "}catch(e){return JSON.stringify({success:false,reason:'JS_ERROR',match_count:0,dispatched:false,click_observed:false});}})();";
    }

    private void eval(String js,final JsCallback cb){
        if(web==null){cb.done(new JSONObject());return;}
        web.evaluateJavascript(js,new ValueCallback<String>(){@Override public void onReceiveValue(String value){
            try{Object outer=new JSONTokener(value).nextValue();String raw=outer instanceof String?(String)outer:String.valueOf(outer);cb.done(new JSONObject(raw));}
            catch(Exception e){JSONObject o=new JSONObject();put(o,"success",false);put(o,"parse_error_class",e.getClass().getSimpleName());cb.done(o);}
        }});
    }
    private interface JsCallback{void done(JSONObject o);}

    private JSONObject baseState(){
        JSONObject o=new JSONObject(); put(o,"elapsed_ms",Math.max(0,System.currentTimeMillis()-startedMs));
        put(o,"page_ui_dispatches",pageUiDispatches); put(o,"page_ui_writes",pageUiDispatches);
        put(o,"model_option_writes",modelOptionWrites); put(o,"effort_writes",effortWrites); put(o,"target_receipt",targetReceipt); put(o,"restore_receipt",restoreReceipt);
        put(o,"claim_status",claimStatus); put(o,"cookies_tokens_accessed",false); put(o,"raw_html_uploaded",false); put(o,"raw_text_uploaded",false);
        put(o,"geometry_click_used",false); put(o,"pro_write_attempted",false); return o;
    }
    private void emitSnapshot(String phase,String classification,JSONObject src){
        JSONObject st=baseState(); copy(st,src,"success","ready","route_class","chat_count","work_count","chat_label_hash","work_label_hash","chat_struct_hash","work_struct_hash","chat_tag","work_tag","chat_role","work_role","chat_testid_hash","work_testid_hash","chat_selected","work_selected","chat_pressed","work_pressed","chat_disabled","work_disabled","chat_data_state","work_data_state","semantic_state","active_set_hash","pair_fingerprint","reason","match_count","dispatched","click_observed","target_semantic"); emit(phase,classification,st);
    }
    private void finish(String classification){
        if(!running)return; running=false; h.removeCallbacksAndMessages(null);
        if(classification.startsWith("PASS_")) claimStatus="CHAT_WORK_RESTORED_CONFIRMED";
        prefs.edit().putString("claim_status",claimStatus).commit();
        JSONObject st=baseState(); put(st,"final_classification",classification);
        emit("FINAL",classification,st);
        status.setText(classification+"\nclicks="+pageUiDispatches+" targetReceipt="+targetReceipt+" restoreReceipt="+restoreReceipt);
    }
    private void emit(String phase,String classification,JSONObject state){
        if(!TelemetryConfigV59.CONFIGURED)return;
        JSONObject o=new JSONObject(); put(o,"schema_version",SCHEMA); put(o,"scenario_id",SCENARIO); put(o,"test_id",testId); put(o,"collector_id",TelemetryConfigV59.COLLECTOR_ID); put(o,"source_ref",TelemetryConfigV59.SOURCE_REF); put(o,"seq",telemetrySeq++); put(o,"timestamp_epoch_ms",System.currentTimeMillis()); put(o,"phase",phase); put(o,"classification",classification); try{o.put("state",state);}catch(Exception ignored){}
        final byte[] bytes=o.toString().getBytes(StandardCharsets.UTF_8); net.execute(()->{HttpURLConnection c=null;try{c=(HttpURLConnection)new URL(TelemetryConfigV59.WEBHOOK_URL).openConnection();c.setRequestMethod("POST");c.setConnectTimeout(5000);c.setReadTimeout(5000);c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json");c.setFixedLengthStreamingMode(bytes.length);try(OutputStream os=c.getOutputStream()){os.write(bytes);}c.getResponseCode();}catch(Exception ignored){}finally{if(c!=null)c.disconnect();}});
    }
    private static void put(JSONObject o,String k,Object v){try{o.put(k,v);}catch(Exception ignored){}}
    private static void copy(JSONObject dst,JSONObject src,String... keys){for(String k:keys)if(src.has(k))try{dst.put(k,src.get(k));}catch(Exception ignored){}}
    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
    @Override public void onBackPressed(){if(web!=null&&web.canGoBack())web.goBack();else super.onBackPressed();}
    @Override protected void onDestroy(){running=false;h.removeCallbacksAndMessages(null);net.shutdownNow();if(web!=null)web.destroy();super.onDestroy();}
}
'''
ACT.write_text(activity)

cfg=(PKG/"TelemetryConfigV58.java").read_text()
(PKG/"TelemetryConfigV59.java").write_text(cfg.replace("TelemetryConfigV58","TelemetryConfigV59"))

g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+59\b","versionCode 60",gs)
gs=gs.replace("0.56-stable-diag-chat-work-manual-observation","0.57-stable-diag-chat-work-autonomous-roundtrip")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorChatWorkManualObservationV58Activity","OrchestratorChatWorkAutonomousRoundtripV59Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
for v in (52,53,54,55,56,57,58,59):
    assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

# Launch-activity safety and exact-contract assertions.
a=ACT.read_text()
for forbidden in ["elementFromPoint","document.evaluate","setAttribute(\"aria-value","ACTION_SET_PROGRESS","clickModelOption","captureModelMenu","startDynamicEffortProof","dispatchTouchEvent","performClick("]:
    assert forbidden not in a, forbidden
assert a.count(".click();")==1
assert "CLAIMED_BEFORE_WORK_CLICK" in a
assert "CLAIMED_BEFORE_CHAT_RESTORE_CLICK" in a
assert "CHAT_RESTORE_NOT_ALLOWED_WITHOUT_WORK_RECEIPT" in a
assert "WORK_RECEIPT_UNRESOLVED_NO_REPLAY_NO_RESTORE" in a
assert "PASS_AUTONOMOUS_CHAT_WORK_CHAT_ROUNDTRIP" in a
assert "CHAT_ACTIVE_SET_HASH=\"265f199e\"" in a
assert "WORK_ACTIVE_SET_HASH=\"efc8a127\"" in a
assert "data-state" in a
assert "pageUiDispatches++" in a
assert "modelOptionWrites=0" in a and "effortWrites=0" in a

print("generated v0.57 autonomous Chat->Work->Chat roundtrip; exact semantic data-state resolver; durable claims; no blind replay; V51 service unchanged")