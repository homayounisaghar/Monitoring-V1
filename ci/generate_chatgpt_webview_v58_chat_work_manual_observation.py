#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# Preserve the exact tested v0.55 app lineage, registered Accessibility service,
# WebView package/storage identity, and all proven prior code. v0.56 only changes
# the launch activity to a read-only manual Chat/Work observer.
runpy.run_path("ci/generate_chatgpt_webview_v57_model_postwrite_receipt.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
ACT=PKG/"OrchestratorChatWorkManualObservationV58Activity.java"

activity=r'''package com.homayounisaghar.chatgptwebviewprobe;

import android.app.Activity;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
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

public class OrchestratorChatWorkManualObservationV58Activity extends Activity {
    private static final String SCHEMA="cp-v58-chat-work-manual-observation-v1";
    private static final String SCENARIO="chat-work-manual-observation";
    private static final long SAMPLE_MS=400L;
    private static final int MAX_SAMPLES=180;

    private final Handler h=new Handler(Looper.getMainLooper());
    private final ExecutorService net=Executors.newSingleThreadExecutor();
    private WebView web;
    private TextView status;
    private boolean observing=false;
    private int sampleIndex=0;
    private int telemetrySeq=0;
    private String testId="-";
    private String lastFingerprint="-";
    private long startedMs=0L;

    private final Runnable sampler=new Runnable(){
        @Override public void run(){
            if(!observing)return;
            if(sampleIndex>=MAX_SAMPLES){stopObservation("AUTO_TIMEOUT");return;}
            sampleOnce();
            h.postDelayed(this,SAMPLE_MS);
        }
    };

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        LinearLayout root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);
        LinearLayout bar=new LinearLayout(this); bar.setOrientation(LinearLayout.HORIZONTAL);
        Button start=new Button(this); start.setText("START OBSERVATION");
        start.setOnClickListener(v->startObservation());
        Button stop=new Button(this); stop.setText("STOP");
        stop.setOnClickListener(v->stopObservation("USER_STOP"));
        bar.addView(start,new LinearLayout.LayoutParams(0,dp(48),2f));
        bar.addView(stop,new LinearLayout.LayoutParams(0,dp(48),1f));
        root.addView(bar,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(48)));

        status=new TextView(this); status.setTextSize(12f); status.setPadding(dp(8),dp(6),dp(8),dp(6));
        status.setText("v0.56 READ-ONLY manual Chat/Work observer\nPress START, then manually switch Chat -> Work -> Chat.\nNo page click/write is performed by this observer.");
        root.addView(status,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(105)));

        web=new WebView(this);
        WebSettings s=web.getSettings();
        s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setDatabaseEnabled(true);
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient(){
            @Override public void onPageStarted(WebView v,String u,Bitmap f){super.onPageStarted(v,u,f);}
            @Override public void onPageFinished(WebView v,String u){
                super.onPageFinished(v,u);
                if(!observing)status.setText("v0.56 READ-ONLY observer ready.\nPress START, then manually Chat -> Work -> Chat.\nDo not change model or effort during this test.");
            }
        });
        root.addView(web,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,0,1f));
        setContentView(root);
        web.loadUrl("https://chatgpt.com/");
    }

    private void startObservation(){
        if(observing)return;
        observing=true; sampleIndex=0; telemetrySeq=0; lastFingerprint="-";
        testId="cp56-"+UUID.randomUUID(); startedMs=System.currentTimeMillis();
        JSONObject st=baseState(); put(st,"observation_only",true); put(st,"page_ui_dispatches",0); put(st,"page_ui_writes",0);
        emit("OBSERVATION_STARTED","RUNNING",st);
        status.setText("OBSERVING...\nNow manually switch Chat -> Work -> Chat once.\nPause about 1-2 seconds in each state; do not change model/effort.");
        h.removeCallbacks(sampler); h.post(sampler);
    }

    private void stopObservation(String why){
        if(!observing)return;
        observing=false; h.removeCallbacks(sampler);
        JSONObject st=baseState(); put(st,"stop_reason",why); put(st,"samples",sampleIndex);
        put(st,"page_ui_dispatches",0); put(st,"page_ui_writes",0); put(st,"observation_only",true);
        emit("FINAL","OBSERVATION_COMPLETE_NO_PAGE_WRITES",st);
        status.setText("OBSERVATION COMPLETE\nYou can tell ChatGPT: انجام شد\nNo page click/write was performed by this observer.");
    }

    private void sampleOnce(){
        if(web==null||!observing)return;
        final int n=++sampleIndex;
        web.evaluateJavascript(scanJs(),new ValueCallback<String>(){
            @Override public void onReceiveValue(String value){
                if(!observing)return;
                try{
                    Object outer=new JSONTokener(value).nextValue();
                    String raw=outer instanceof String?(String)outer:String.valueOf(outer);
                    JSONObject o=new JSONObject(raw);
                    String fp=o.optString("state_fingerprint","-");
                    boolean changed=!fp.equals(lastFingerprint);
                    boolean heartbeat=(n==1||n%15==0);
                    if(changed||heartbeat){
                        JSONObject st=baseState();
                        copy(st,o,"success","ready","route_class","candidate_count","candidate_set_hash","state_fingerprint","chat_candidate_count","work_candidate_count","chat_selected_count","work_selected_count","chat_pressed_count","work_pressed_count","chat_active_count","work_active_count","semantic_state","role_set_hash","testid_set_hash","selected_set_hash","pressed_set_hash","active_set_hash");
                        put(st,"sample_index",n); put(st,"changed",changed); put(st,"observation_only",true);
                        put(st,"page_ui_dispatches",0); put(st,"page_ui_writes",0);
                        emit("MANUAL_UI_SNAPSHOT",changed?"STATE_CHANGED":"HEARTBEAT",st);
                        lastFingerprint=fp;
                    }
                    status.setText("OBSERVING sample "+n+"/"+MAX_SAMPLES+"\nManual Chat -> Work -> Chat. Pause 1-2 seconds in each state.\nsemantic="+o.optString("semantic_state","UNKNOWN")+" candidates="+o.optInt("candidate_count",-1));
                }catch(Exception e){
                    JSONObject st=baseState(); put(st,"sample_index",n); put(st,"parse_error_class",e.getClass().getSimpleName());
                    emit("MANUAL_UI_SNAPSHOT","SANITIZED_PARSE_ERROR",st);
                }
            }
        });
    }

    private String scanJs(){
        return "(function(){try{"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};"+
            "const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const B=(e,n)=>{const v=e.getAttribute(n);return v==='true'?1:(v==='false'?0:-1);};"+
            "const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};"+
            "const sem=t=>{const x=N(t);if(x==='chat')return 'CHAT';if(x==='work')return 'WORK';return 'OTHER';};"+
            "const ds=v=>{v=N(v);if(v==='active'||v==='selected'||v==='checked'||v==='on')return 'ACTIVE';if(v==='inactive'||v==='unselected'||v==='unchecked'||v==='off')return 'INACTIVE';if(v==='open')return 'OPEN';if(v==='closed')return 'CLOSED';return v?'OTHER':'NONE';};"+
            "const rc=()=>{const p=location.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';if(/^\\/g\\//.test(p))return 'GPT_ROUTE';if(/^\\/project/.test(p))return 'PROJECT_ROUTE';return 'OTHER_ROUTE';};"+
            "const q=Array.from(document.querySelectorAll('button,a,[role],[aria-selected],[aria-pressed],[data-state],[data-testid]')).filter(V);"+
            "let rows=[];let cc=0,wc=0,cs=0,ws=0,cp=0,wp=0,ca=0,wa=0;"+
            "for(const e of q){const tag=(e.tagName||'').toLowerCase();const role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none'));const actionable=tag==='button'||tag==='a'||['button','tab','menuitem','radio','switch','option'].includes(role)||e.hasAttribute('aria-selected')||e.hasAttribute('aria-pressed')||e.hasAttribute('data-state');if(!actionable)continue;"+
            "const label=(e.getAttribute('aria-label')||e.innerText||e.textContent||'').trim().replace(/\\s+/g,' ').slice(0,160);const sm=sem(label);const sel=B(e,'aria-selected'),prs=B(e,'aria-pressed'),exp=B(e,'aria-expanded');const state=ds(e.getAttribute('data-state'));const active=(sel===1||prs===1||state==='ACTIVE')?1:0;"+
            "if(sm==='CHAT'){cc++;if(sel===1)cs++;if(prs===1)cp++;if(active)ca++;}if(sm==='WORK'){wc++;if(sel===1)ws++;if(prs===1)wp++;if(active)wa++;}"+
            "const tid=e.getAttribute('data-testid')||'';rows.push([tag,role,sm,H(N(label)),H(tid),sel,prs,exp,state,e.hasAttribute('disabled')?1:0,N(e.getAttribute('aria-haspopup'))||'none']);if(rows.length>=80)break;}"+
            "rows.sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)));const packed=rows.map(r=>r.join('|'));const roles=rows.map(r=>r[1]).sort();const tids=rows.map(r=>r[4]).sort();const sels=rows.filter(r=>r[5]===1).map(r=>r[3]).sort();const presses=rows.filter(r=>r[6]===1).map(r=>r[3]).sort();const act=rows.filter(r=>r[8]==='ACTIVE'||r[5]===1||r[6]===1).map(r=>r[3]).sort();"+
            "let ss='UNKNOWN';if((cs+cp+ca)>0&&(ws+wp+wa)===0)ss='CHAT';else if((ws+wp+wa)>0&&(cs+cp+ca)===0)ss='WORK';else if(cc===1&&wc===0)ss='CHAT_CANDIDATE_ONLY';else if(wc===1&&cc===0)ss='WORK_CANDIDATE_ONLY';"+
            "return JSON.stringify({success:true,ready:document.readyState,route_class:rc(),candidate_count:rows.length,candidate_set_hash:H(packed.join('~')),state_fingerprint:H(rc()+'#'+packed.join('~')),chat_candidate_count:cc,work_candidate_count:wc,chat_selected_count:cs,work_selected_count:ws,chat_pressed_count:cp,work_pressed_count:wp,chat_active_count:ca,work_active_count:wa,semantic_state:ss,role_set_hash:H(roles.join('|')),testid_set_hash:H(tids.join('|')),selected_set_hash:H(sels.join('|')),pressed_set_hash:H(presses.join('|')),active_set_hash:H(act.join('|'))});"+
            "}catch(e){return JSON.stringify({success:false,ready:'error',route_class:'ERROR',candidate_count:-1,candidate_set_hash:'-',state_fingerprint:'-',chat_candidate_count:0,work_candidate_count:0,semantic_state:'UNKNOWN'});}})();";
    }

    private JSONObject baseState(){
        JSONObject o=new JSONObject(); put(o,"elapsed_ms",Math.max(0,System.currentTimeMillis()-startedMs));
        put(o,"cookies_tokens_accessed",false); put(o,"raw_html_uploaded",false); put(o,"raw_text_uploaded",false);
        put(o,"geometry_click_used",false); put(o,"model_option_writes",0); put(o,"effort_writes",0); put(o,"pro_write_attempted",false);
        return o;
    }

    private void emit(String phase,String classification,JSONObject state){
        if(!TelemetryConfigV58.CONFIGURED)return;
        JSONObject o=new JSONObject(); put(o,"schema_version",SCHEMA); put(o,"scenario_id",SCENARIO); put(o,"test_id",testId);
        put(o,"collector_id",TelemetryConfigV58.COLLECTOR_ID); put(o,"source_ref",TelemetryConfigV58.SOURCE_REF);
        put(o,"seq",telemetrySeq++); put(o,"timestamp_epoch_ms",System.currentTimeMillis()); put(o,"phase",phase); put(o,"classification",classification);
        try{o.put("state",state);}catch(Exception ignored){}
        final byte[] bytes=o.toString().getBytes(StandardCharsets.UTF_8);
        net.execute(()->{HttpURLConnection c=null;try{c=(HttpURLConnection)new URL(TelemetryConfigV58.WEBHOOK_URL).openConnection();c.setRequestMethod("POST");c.setConnectTimeout(5000);c.setReadTimeout(5000);c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json");c.setFixedLengthStreamingMode(bytes.length);try(OutputStream os=c.getOutputStream()){os.write(bytes);}c.getResponseCode();}catch(Exception ignored){}finally{if(c!=null)c.disconnect();}});
    }

    private static void put(JSONObject o,String k,Object v){try{o.put(k,v);}catch(Exception ignored){}}
    private static void copy(JSONObject dst,JSONObject src,String... keys){for(String k:keys)if(src.has(k))try{dst.put(k,src.get(k));}catch(Exception ignored){}}
    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}

    @Override public void onBackPressed(){if(web!=null&&web.canGoBack())web.goBack();else super.onBackPressed();}
    @Override protected void onDestroy(){observing=false;h.removeCallbacks(sampler);net.shutdownNow();if(web!=null)web.destroy();super.onDestroy();}
}
'''
ACT.write_text(activity)

# Fresh telemetry config cloned only for transport constants.
cfg=(PKG/"TelemetryConfigV57.java").read_text()
(PKG/"TelemetryConfigV58.java").write_text(cfg.replace("TelemetryConfigV57","TelemetryConfigV58"))

# In-place upgrade identity over tested v0.55.
g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+58\b","versionCode 59",gs)
gs=gs.replace("0.55-stable-diag-model-postwrite-receipt","0.56-stable-diag-chat-work-manual-observation")
g.write_text(gs)

# Only launch activity changes. Keep the proven V51 Accessibility registration exactly unchanged.
m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorPaidCurrentUiModelPostwriteReceiptV57Activity","OrchestratorChatWorkManualObservationV58Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
for v in (52,53,54,55,56,57,58):
    assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

# Build-time safety assertions for the launch activity itself.
a=ACT.read_text()
for forbidden in ["performClick(","dispatchTouchEvent(","elementFromPoint","document.evaluate","setAttribute(\"aria-","clickModelOption","startDynamicEffortProof","ACTION_CLICK","ACTION_SET_PROGRESS","CookieManager","getCookie(","addJavascriptInterface"]:
    assert forbidden not in a, forbidden
assert 'evaluateJavascript(scanJs()' in a
assert 'page_ui_dispatches",0' in a
assert 'page_ui_writes",0' in a
assert 'raw_text_uploaded",false' in a
assert 'raw_html_uploaded",false' in a
print("generated v0.56 manual Chat/Work observation; launch activity is read-only; V51 accessibility registration preserved")
