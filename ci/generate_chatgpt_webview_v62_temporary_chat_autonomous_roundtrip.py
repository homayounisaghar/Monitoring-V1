#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# Build on the exact v0.59 observation lineage. v0.60 turns only the
# independently repeated manual Temporary Chat contract into a fail-closed
# reversible autonomous roundtrip. No model, effort, or Chat/Work write path.
runpy.run_path("ci/generate_chatgpt_webview_v61_temporary_chat_manual_observation.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
ACT=PKG/"OrchestratorTemporaryChatAutonomousRoundtripV62Activity.java"

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

public class OrchestratorTemporaryChatAutonomousRoundtripV62Activity extends Activity {
    private static final String SCHEMA="cp-v62-temporary-chat-autonomous-roundtrip-v1";
    private static final String SCENARIO="temporary-chat-autonomous-roundtrip";

    // Two independent real-device v0.59 observation runs produced the same
    // exact manual entry/exit signatures and semantic receipts.
    private static final String NORMAL_LABEL_HASH="1a957a52";
    private static final String NORMAL_STRUCT_HASH="b9c97d1e";
    private static final String NORMAL_SEMANTIC_SET_HASH="566ee132";
    private static final String TEMP_LABEL_HASH="ae0e16e6";
    private static final String TEMP_STRUCT_HASH="34d052a8";
    private static final String TEMP_SEMANTIC_SET_HASH="2f8aeb2c";
    private static final String EMPTY_TESTID_HASH="811c9dc5";

    private static final int PURPOSE_ENTER_TEMP=1;
    private static final int PURPOSE_EXIT_TEMP=2;
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
    private boolean targetReceipt=false;
    private boolean restoreReceipt=false;
    private String testId="-";
    private String claimStatus="IDLE";
    private long startedMs=0L;

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        prefs=getSharedPreferences("cp_v62_temp_roundtrip_claim",MODE_PRIVATE);
        LinearLayout root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);
        Button run=new Button(this); run.setText("RUN AUTONOMOUS TEMP CHAT ROUNDTRIP");
        run.setOnClickListener(v->startRoundtrip());
        root.addView(run,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(52)));
        status=new TextView(this); status.setTextSize(12f); status.setPadding(dp(8),dp(6),dp(8),dp(6));
        status.setText("v0.60 autonomous Temporary Chat roundtrip ready.\nFail-closed: exact normal baseline required; no model/effort/Chat-Work writes.");
        root.addView(status,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(100)));
        web=new WebView(this);
        WebSettings s=web.getSettings(); s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setDatabaseEnabled(true);
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient(){
            @Override public void onPageStarted(WebView v,String u,Bitmap f){super.onPageStarted(v,u,f);}
            @Override public void onPageFinished(WebView v,String u){super.onPageFinished(v,u);if(!running)status.setText("v0.60 ready.\nCurrent UI must be normal Chat on HOME before RUN.");}
        });
        root.addView(web,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,0,1f));
        setContentView(root);
        web.loadUrl("https://chatgpt.com/");
    }

    private void startRoundtrip(){
        if(running)return;
        running=true; telemetrySeq=0; pageUiDispatches=0; targetReceipt=false; restoreReceipt=false;
        testId="cp60-"+UUID.randomUUID(); startedMs=System.currentTimeMillis(); claimStatus="RUNNING_START_GATE";
        prefs.edit().putString("test_id",testId).putString("claim_status",claimStatus).commit();
        emit("ROUNDTRIP_STARTED","RUNNING",baseState());
        status.setText("Checking exact normal Temporary Chat baseline...");
        h.postDelayed(this::resolveStart,300L);
    }

    private void resolveStart(){
        if(!running)return;
        eval(scanJs(),o->{
            if(!running)return;
            boolean ok=exactNormal(o)&&pageUiDispatches==0;
            emitSnapshot("START_GATE",ok?"PASS_EXACT_NORMAL_TEMP_BASELINE":"TEMP_START_NOT_EXACT_NORMAL_ZERO_WRITE",o);
            if(!ok){finish("TEMP_START_NOT_EXACT_NORMAL_ZERO_WRITE");return;}
            claimAndClick(PURPOSE_ENTER_TEMP);
        });
    }

    private void claimAndClick(final int purpose){
        if(!running)return;
        if(purpose==PURPOSE_ENTER_TEMP){
            if(pageUiDispatches!=0||targetReceipt){finish("TEMP_ENTRY_REPLAY_BLOCKED");return;}
            claimStatus="CLAIMED_BEFORE_TEMP_ENTRY_CLICK";
        }else{
            if(!targetReceipt||pageUiDispatches!=1){finish("TEMP_EXIT_NOT_ALLOWED_WITHOUT_TARGET_RECEIPT");return;}
            claimStatus="CLAIMED_BEFORE_TEMP_EXIT_CLICK";
        }
        prefs.edit().putString("test_id",testId).putString("claim_status",claimStatus).commit();
        JSONObject claim=baseState(); put(claim,"purpose",purpose);
        emit("DURABLE_CLAIM",claimStatus,claim);
        status.setText(purpose==PURPOSE_ENTER_TEMP?"CLAIMED; entering Temporary Chat...":"Temporary receipt confirmed; CLAIMED; returning to normal Chat...");
        eval(clickJs(purpose),o->{
            if(!running)return;
            String expectedLabel=purpose==PURPOSE_ENTER_TEMP?NORMAL_LABEL_HASH:TEMP_LABEL_HASH;
            String expectedStruct=purpose==PURPOSE_ENTER_TEMP?NORMAL_STRUCT_HASH:TEMP_STRUCT_HASH;
            String expectedFrom=purpose==PURPOSE_ENTER_TEMP?"NORMAL":"TEMP";
            boolean dispatched=o.optBoolean("success",false)&&o.optBoolean("dispatched",false)&&o.optBoolean("click_observed",false)
                    &&o.optInt("match_count",0)==1
                    &&expectedLabel.equals(o.optString("label_hash",""))
                    &&expectedStruct.equals(o.optString("struct_hash",""))
                    &&expectedFrom.equals(o.optString("from_state",""));
            emitSnapshot(purpose==PURPOSE_ENTER_TEMP?"TEMP_ENTRY_CLICK_DISPATCH":"TEMP_EXIT_CLICK_DISPATCH",
                    dispatched?"PASS_EXACT_ELEMENT_CLICK_DISPATCHED":"TEMP_CLICK_DISPATCH_UNCERTAIN_NO_REPLAY",o);
            if(!dispatched){
                claimStatus=purpose==PURPOSE_ENTER_TEMP?"UNCERTAIN_AFTER_TEMP_ENTRY_CLAIM":"UNCERTAIN_TEMP_EXIT_REQUIRED";
                prefs.edit().putString("claim_status",claimStatus).commit();
                finish("TEMP_CLICK_DISPATCH_UNCERTAIN_NO_REPLAY");return;
            }
            pageUiDispatches++;
            h.postDelayed(()->pollReceipt(purpose,0,0),RECEIPT_POLL_MS);
        });
    }

    private void pollReceipt(final int purpose,final int attempt,final int stableHits){
        if(!running)return;
        eval(scanJs(),o->{
            if(!running)return;
            boolean match=purpose==PURPOSE_ENTER_TEMP?exactTemp(o):exactNormal(o);
            int hits=match?stableHits+1:0;
            if(match&&(hits==1||hits==2)){
                String cls=hits>=2?(purpose==PURPOSE_ENTER_TEMP?"PASS_STABLE_TEMP_TARGET_RECEIPT":"PASS_STABLE_NORMAL_RESTORE_RECEIPT"):"RECEIPT_CANDIDATE_1_OF_2";
                emitSnapshot(purpose==PURPOSE_ENTER_TEMP?"TEMP_TARGET_RECEIPT":"NORMAL_RESTORE_RECEIPT",cls,o);
            }
            if(hits>=2){
                if(purpose==PURPOSE_ENTER_TEMP){
                    targetReceipt=true; claimStatus="TEMP_TARGET_RECEIPT_CONFIRMED";
                    prefs.edit().putString("claim_status",claimStatus).commit();
                    h.postDelayed(this::prepareExit,350L);
                }else{
                    restoreReceipt=true; claimStatus="NORMAL_RESTORE_CONFIRMED";
                    prefs.edit().putString("claim_status",claimStatus).commit();
                    boolean pass=pageUiDispatches==2&&targetReceipt&&restoreReceipt;
                    finish(pass?"PASS_AUTONOMOUS_TEMPORARY_CHAT_ROUNDTRIP":"TEMP_ROUNDTRIP_INCOMPLETE");
                }
                return;
            }
            if(attempt>=MAX_RECEIPT_POLLS){
                claimStatus=purpose==PURPOSE_ENTER_TEMP?"UNCERTAIN_TEMP_TARGET_NO_EXIT":"UNCERTAIN_NORMAL_RESTORE_REQUIRED";
                prefs.edit().putString("claim_status",claimStatus).commit();
                finish(purpose==PURPOSE_ENTER_TEMP?"TEMP_TARGET_RECEIPT_UNRESOLVED_NO_REPLAY_NO_EXIT":"NORMAL_RESTORE_RECEIPT_UNRESOLVED_NO_REPLAY");
                return;
            }
            if(attempt==0||attempt==10||attempt==20)
                emitSnapshot(purpose==PURPOSE_ENTER_TEMP?"TEMP_TARGET_RECEIPT_WAIT":"NORMAL_RESTORE_RECEIPT_WAIT","READ_ONLY_POLL_NO_REPLAY",o);
            h.postDelayed(()->pollReceipt(purpose,attempt+1,hits),RECEIPT_POLL_MS);
        });
    }

    private void prepareExit(){
        if(!running)return;
        if(!targetReceipt||pageUiDispatches!=1){finish("TEMP_EXIT_NOT_ALLOWED_WITHOUT_TARGET_RECEIPT");return;}
        eval(scanJs(),o->{
            if(!running)return;
            boolean ok=exactTemp(o);
            emitSnapshot("EXIT_GATE",ok?"PASS_FRESH_TEMP_STATE_BEFORE_EXIT":"TEMP_EXIT_GATE_STATE_DRIFT_NO_REPLAY",o);
            if(!ok){claimStatus="UNCERTAIN_TEMP_STATE_MANUAL_RESTORE_REQUIRED";prefs.edit().putString("claim_status",claimStatus).commit();finish("TEMP_EXIT_GATE_STATE_DRIFT_NO_REPLAY");return;}
            claimAndClick(PURPOSE_EXIT_TEMP);
        });
    }

    private boolean exactBase(JSONObject o){
        return o.optBoolean("success",false)
                &&"complete".equals(o.optString("ready",""))
                &&"HOME".equals(o.optString("route_class",""))
                &&o.optInt("temp_candidate_count",0)==1
                &&"button".equals(o.optString("candidate_tag",""))
                &&"button".equals(o.optString("candidate_role",""))
                &&EMPTY_TESTID_HASH.equals(o.optString("candidate_testid_hash",""))
                &&"NONE".equals(o.optString("candidate_data_state",""))
                &&o.optInt("candidate_selected",-1)==0
                &&o.optInt("candidate_pressed",-1)==0
                &&o.optInt("candidate_expanded",-1)==0
                &&o.optInt("candidate_disabled",-1)==0
                &&"NONE".equals(o.optString("candidate_href_class",""))
                &&o.optInt("temp_active_count",-1)==0
                &&!o.optBoolean("composer_temp_hint",true);
    }

    private boolean exactNormal(JSONObject o){
        return exactBase(o)
                &&"NORMAL".equals(o.optString("semantic_temp_state",""))
                &&!o.optBoolean("url_temp_hint",true)
                &&NORMAL_LABEL_HASH.equals(o.optString("candidate_label_hash",""))
                &&NORMAL_STRUCT_HASH.equals(o.optString("candidate_struct_hash",""))
                &&NORMAL_SEMANTIC_SET_HASH.equals(o.optString("temp_semantic_set_hash",""));
    }

    private boolean exactTemp(JSONObject o){
        return exactBase(o)
                &&"TEMP".equals(o.optString("semantic_temp_state",""))
                &&o.optBoolean("url_temp_hint",false)
                &&TEMP_LABEL_HASH.equals(o.optString("candidate_label_hash",""))
                &&TEMP_STRUCT_HASH.equals(o.optString("candidate_struct_hash",""))
                &&TEMP_SEMANTIC_SET_HASH.equals(o.optString("temp_semantic_set_hash",""));
    }

    private String scanJs(){
        return "(function(){try{"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};"+
            "const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};"+
            "const DS=e=>{const v=N(e.getAttribute('data-state'));if(['active','selected','checked','on'].includes(v))return 'ACTIVE';if(['inactive','unselected','unchecked','off'].includes(v))return 'INACTIVE';if(v==='open')return 'OPEN';if(v==='closed')return 'CLOSED';return v?'OTHER':'NONE';};"+
            "const HC=e=>{const h=e.getAttribute('href')||'';if(!h)return 'NONE';try{const u=new URL(h,location.href),p=u.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';return 'OTHER';}catch(x){return 'OTHER';}};"+
            "const RC=()=>{const p=location.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';if(/^\\/g\\//.test(p))return 'GPT_ROUTE';if(/^\\/project/.test(p))return 'PROJECT_ROUTE';return 'OTHER_ROUTE';};"+
            "const SEM=(label,tid)=>{const x=N(label),t=N(tid),z=x+' '+t;if(z.includes('temporary')||x==='temp'||t.includes('temp'))return 'TEMP';return 'OTHER';};"+
            "const q=Array.from(document.querySelectorAll('button,a,[role],[aria-selected],[aria-pressed],[data-state],[data-testid]')).filter(V);let T=[];"+
            "for(const e of q){const tag=(e.tagName||'').toLowerCase(),role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none'));const actionable=tag==='button'||tag==='a'||['button','tab','menuitem','radio','switch','option'].includes(role)||e.hasAttribute('aria-selected')||e.hasAttribute('aria-pressed')||e.hasAttribute('data-state');if(!actionable)continue;const label=e.getAttribute('aria-label')||e.innerText||e.textContent||'',tid=e.getAttribute('data-testid')||'';if(SEM(label,tid)!=='TEMP')continue;const lh=H(N(label)),th=H(tid),ds=DS(e),sel=e.getAttribute('aria-selected')==='true'?1:0,prs=e.getAttribute('aria-pressed')==='true'?1:0,exp=e.getAttribute('aria-expanded')==='true'?1:0,dis=e.hasAttribute('disabled')?1:0,hc=HC(e),sh=H([tag,role,'TEMP',lh,th,hc].join('|'));T.push({tag:tag,role:role,lh:lh,th:th,ds:ds,sel:sel,prs:prs,exp:exp,dis:dis,hc:hc,sh:sh});}"+
            "const c=T.length===1?T[0]:null;const urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));let comphint=false;for(const e of Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).filter(V)){const s=N((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('placeholder')||''));if(s.includes('temporary')||s==='temp'){comphint=true;break;}}let active=0;if(c&&(c.ds==='ACTIVE'||c.sel===1||c.prs===1))active=1;let sem='UNKNOWN';if(c&&c.tag==='button'&&c.role==='button'&&c.th==='811c9dc5'&&c.ds==='NONE'&&c.sel===0&&c.prs===0&&c.exp===0&&c.dis===0&&c.hc==='NONE'&&!comphint){if(c.lh==='1a957a52'&&c.sh==='b9c97d1e'&&!urlhint)sem='NORMAL';else if(c.lh==='ae0e16e6'&&c.sh==='34d052a8'&&urlhint)sem='TEMP';}"+
            "const rows=T.map(x=>[x.tag,x.role,x.lh,x.th,x.ds,x.sel,x.prs].join('|')).sort();return JSON.stringify({success:true,ready:document.readyState,route_class:RC(),url_temp_hint:urlhint,composer_temp_hint:comphint,temp_candidate_count:T.length,temp_active_count:active,temp_semantic_set_hash:H(rows.join('~')),semantic_temp_state:sem,candidate_tag:c?c.tag:'-',candidate_role:c?c.role:'-',candidate_label_hash:c?c.lh:'-',candidate_testid_hash:c?c.th:'-',candidate_data_state:c?c.ds:'NONE',candidate_selected:c?c.sel:-1,candidate_pressed:c?c.prs:-1,candidate_expanded:c?c.exp:-1,candidate_disabled:c?c.dis:-1,candidate_href_class:c?c.hc:'-',candidate_struct_hash:c?c.sh:'-'});"+
            "}catch(e){return JSON.stringify({success:false,ready:'error',route_class:'ERROR',semantic_temp_state:'UNKNOWN',temp_candidate_count:0});}})();";
    }

    private String clickJs(int purpose){
        final String expectedLabel=purpose==PURPOSE_ENTER_TEMP?NORMAL_LABEL_HASH:TEMP_LABEL_HASH;
        final String expectedStruct=purpose==PURPOSE_ENTER_TEMP?NORMAL_STRUCT_HASH:TEMP_STRUCT_HASH;
        final String expectedFrom=purpose==PURPOSE_ENTER_TEMP?"NORMAL":"TEMP";
        final boolean expectedUrl=purpose==PURPOSE_EXIT_TEMP;
        return "(function(){try{"+
            "const EL='"+expectedLabel+"',ES='"+expectedStruct+"',FROM='"+expectedFrom+"',EU="+("+expectedUrl+"?'true':'false')+";"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};"+
            "const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const HC=e=>{const h=e.getAttribute('href')||'';if(!h)return 'NONE';try{const u=new URL(h,location.href),p=u.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';return 'OTHER';}catch(x){return 'OTHER';}};"+
            "const q=Array.from(document.querySelectorAll('button,a,[role],[aria-selected],[aria-pressed],[data-state],[data-testid]')).filter(V);let T=[];for(const e of q){const tag=(e.tagName||'').toLowerCase(),role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none')),label=e.getAttribute('aria-label')||e.innerText||e.textContent||'',tid=e.getAttribute('data-testid')||'',z=N(label)+' '+N(tid);if(!(z.includes('temporary')||N(label)==='temp'||N(tid).includes('temp')))continue;const lh=H(N(label)),th=H(tid),hc=HC(e),sh=H([tag,role,'TEMP',lh,th,hc].join('|'));T.push({e:e,tag:tag,role:role,lh:lh,th:th,hc:hc,sh:sh,sel:e.getAttribute('aria-selected')==='true'?1:0,prs:e.getAttribute('aria-pressed')==='true'?1:0,exp:e.getAttribute('aria-expanded')==='true'?1:0,dis:e.hasAttribute('disabled')?1:0,ds:N(e.getAttribute('data-state'))||'none'});}"+
            "if(T.length!==1)return JSON.stringify({success:false,reason:'TEMP_COUNT',match_count:0,dispatched:false,click_observed:false});const t=T[0],urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));const clean=t.tag==='button'&&t.role==='button'&&t.th==='811c9dc5'&&t.hc==='NONE'&&t.sel===0&&t.prs===0&&t.exp===0&&t.dis===0&&t.ds==='none';if(!clean||t.lh!==EL||t.sh!==ES||urlhint!==EU)return JSON.stringify({success:false,reason:'STATE_OR_HASH',match_count:(t.lh===EL&&t.sh===ES)?1:0,dispatched:false,click_observed:false,label_hash:t.lh,struct_hash:t.sh,from_state:FROM});let observed=false;t.e.addEventListener('click',()=>{observed=true;},{capture:true,once:true});t.e.click();return JSON.stringify({success:true,reason:'ELEMENT_CLICK',match_count:1,dispatched:true,click_observed:observed,label_hash:t.lh,struct_hash:t.sh,from_state:FROM});"+
            "}catch(e){return JSON.stringify({success:false,reason:'JS_ERROR',match_count:0,dispatched:false,click_observed:false});}})();";
    }

    private void eval(String js,final JsCallback cb){
        if(web==null){JSONObject o=new JSONObject();put(o,"success",false);cb.done(o);return;}
        web.evaluateJavascript(js,new ValueCallback<String>(){public void onReceiveValue(String value){try{Object outer=new JSONTokener(value).nextValue();String raw=outer instanceof String?(String)outer:String.valueOf(outer);cb.done(new JSONObject(raw));}catch(Exception e){JSONObject o=new JSONObject();put(o,"success",false);put(o,"parse_error_class",e.getClass().getSimpleName());cb.done(o);}}});
    }
    private interface JsCallback{void done(JSONObject o);}

    private JSONObject baseState(){
        JSONObject o=new JSONObject(); put(o,"elapsed_ms",Math.max(0,System.currentTimeMillis()-startedMs));
        put(o,"page_ui_dispatches",pageUiDispatches); put(o,"page_ui_writes",pageUiDispatches);
        put(o,"target_receipt",targetReceipt); put(o,"restore_receipt",restoreReceipt); put(o,"claim_status",claimStatus);
        put(o,"model_option_writes",0); put(o,"effort_writes",0); put(o,"chat_work_writes",0);
        put(o,"cookies_tokens_accessed",false); put(o,"raw_html_uploaded",false); put(o,"raw_text_uploaded",false); put(o,"raw_url_uploaded",false);
        put(o,"geometry_click_used",false); put(o,"pro_write_attempted",false); return o;
    }

    private void emitSnapshot(String phase,String classification,JSONObject src){
        JSONObject st=baseState(); copy(st,src,"success","ready","route_class","url_temp_hint","composer_temp_hint","temp_candidate_count","temp_active_count","temp_semantic_set_hash","semantic_temp_state","candidate_tag","candidate_role","candidate_label_hash","candidate_testid_hash","candidate_data_state","candidate_selected","candidate_pressed","candidate_expanded","candidate_disabled","candidate_href_class","candidate_struct_hash","reason","match_count","dispatched","click_observed","label_hash","struct_hash","from_state"); emit(phase,classification,st);
    }

    private void finish(String classification){
        if(!running)return; running=false; h.removeCallbacksAndMessages(null);
        if(classification.startsWith("PASS_"))claimStatus="TEMP_ROUNDTRIP_RESTORED_CONFIRMED";
        prefs.edit().putString("claim_status",claimStatus).commit();
        JSONObject st=baseState(); put(st,"final_classification",classification); emit("FINAL",classification,st);
        status.setText(classification.startsWith("PASS_")?"PASS\nTemporary Chat entered and normal Chat independently restored.":"STOPPED FAIL-CLOSED\n"+classification);
    }

    private void emit(String phase,String classification,JSONObject state){
        if(!TelemetryConfigV62.CONFIGURED)return;
        JSONObject o=new JSONObject(); put(o,"schema_version",SCHEMA); put(o,"scenario_id",SCENARIO); put(o,"test_id",testId);
        put(o,"collector_id",TelemetryConfigV62.COLLECTOR_ID); put(o,"source_ref",TelemetryConfigV62.SOURCE_REF);
        put(o,"seq",telemetrySeq++); put(o,"timestamp_epoch_ms",System.currentTimeMillis()); put(o,"phase",phase); put(o,"classification",classification);
        try{o.put("state",state);}catch(Exception ignored){}
        final byte[] bytes=o.toString().getBytes(StandardCharsets.UTF_8);
        net.execute(()->{HttpURLConnection c=null;try{c=(HttpURLConnection)new URL(TelemetryConfigV62.WEBHOOK_URL).openConnection();c.setRequestMethod("POST");c.setConnectTimeout(5000);c.setReadTimeout(5000);c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json");c.setFixedLengthStreamingMode(bytes.length);try(OutputStream os=c.getOutputStream()){os.write(bytes);}c.getResponseCode();}catch(Exception ignored){}finally{if(c!=null)c.disconnect();}});
    }

    private static void put(JSONObject o,String k,Object v){try{o.put(k,v);}catch(Exception ignored){}}
    private static void copy(JSONObject dst,JSONObject src,String... keys){for(String k:keys)if(src.has(k))try{dst.put(k,src.get(k));}catch(Exception ignored){}}
    private int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+0.5f);}
}
'''
ACT.write_text(activity)

cfg=(PKG/"TelemetryConfigV61.java").read_text()
(PKG/"TelemetryConfigV62.java").write_text(cfg.replace("TelemetryConfigV61","TelemetryConfigV62"))

g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+62\b","versionCode 63",gs)
gs=gs.replace("0.59-stable-diag-temporary-chat-manual-observation","0.60-stable-diag-temporary-chat-autonomous-roundtrip")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorTemporaryChatManualObservationV61Activity","OrchestratorTemporaryChatAutonomousRoundtripV62Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
for v in (52,53,54,55,56,57,58,59,60,61,62):
    assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)
