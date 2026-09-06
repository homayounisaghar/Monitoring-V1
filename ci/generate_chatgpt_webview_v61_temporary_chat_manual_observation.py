#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# Preserve the exact tested v0.58 package/storage/signing lineage and registered
# Accessibility service. v0.59 changes only the launch activity to a strictly
# observation-only manual Temporary Chat observer.
runpy.run_path("ci/generate_chatgpt_webview_v60_chat_work_recovery_roundtrip.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
ACT=PKG/"OrchestratorTemporaryChatManualObservationV61Activity.java"

activity=r'''package com.homayounisaghar.chatgptwebviewprobe;

import android.app.Activity;
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

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class OrchestratorTemporaryChatManualObservationV61Activity extends Activity {
    private static final String SCHEMA="cp-v61-temporary-chat-manual-observation-v1";
    private static final String SCENARIO="temporary-chat-manual-observation";
    private static final long SAMPLE_MS=300L;
    private static final int MAX_SAMPLES=240;

    private final Handler h=new Handler(Looper.getMainLooper());
    private final ExecutorService net=Executors.newSingleThreadExecutor();
    private WebView web;
    private TextView status;
    private boolean observing=false;
    private int sampleIndex=0;
    private int telemetrySeq=0;
    private int manualClickCount=0;
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
        Button start=new Button(this); start.setText("START TEMP OBSERVATION");
        start.setOnClickListener(v->startObservation());
        Button stop=new Button(this); stop.setText("STOP");
        stop.setOnClickListener(v->stopObservation("USER_STOP"));
        bar.addView(start,new LinearLayout.LayoutParams(0,dp(48),2f));
        bar.addView(stop,new LinearLayout.LayoutParams(0,dp(48),1f));
        root.addView(bar,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(48)));

        status=new TextView(this); status.setTextSize(12f); status.setPadding(dp(8),dp(6),dp(8),dp(6));
        status.setText("v0.59 READ-ONLY Temporary Chat observer\nPress START, then manually enter Temporary Chat and return to normal Chat.\nNo page click/write is performed by this observer.");
        root.addView(status,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(110)));

        web=new WebView(this);
        WebSettings s=web.getSettings();
        s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setDatabaseEnabled(true);
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient(){
            @Override public void onPageStarted(WebView v,String u,Bitmap f){super.onPageStarted(v,u,f);}
            @Override public void onPageFinished(WebView v,String u){
                super.onPageFinished(v,u);
                if(observing) installObserverAndSample();
                else status.setText("v0.59 ready.\nPress START, manually enter Temporary Chat, pause, then return to normal Chat.\nDo not change model/effort/Chat-Work during this test.");
            }
        });
        root.addView(web,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,0,1f));
        setContentView(root);
        web.loadUrl("https://chatgpt.com/");
    }

    private void startObservation(){
        if(observing)return;
        observing=true; sampleIndex=0; telemetrySeq=0; manualClickCount=0; lastFingerprint="-";
        testId="cp59-"+UUID.randomUUID(); startedMs=System.currentTimeMillis();
        JSONObject st=baseState(); put(st,"observation_only",true); put(st,"page_ui_dispatches",0); put(st,"page_ui_writes",0);
        emit("OBSERVATION_STARTED","RUNNING",st);
        status.setText("OBSERVING...\nNow manually enter Temporary Chat, pause ~1-2 s, then return to normal Chat.\nDo not change model/effort/Chat-Work.");
        installObserverAndSample();
    }

    private void installObserverAndSample(){
        if(!observing||web==null)return;
        web.evaluateJavascript(installJs(),new ValueCallback<String>(){
            @Override public void onReceiveValue(String value){
                if(!observing)return;
                try{
                    Object outer=new JSONTokener(value).nextValue();
                    String raw=outer instanceof String?(String)outer:String.valueOf(outer);
                    JSONObject o=new JSONObject(raw);
                    JSONObject st=baseState(); put(st,"installed",o.optBoolean("installed",false)); put(st,"reused",o.optBoolean("reused",false));
                    emit("LISTENER_INSTALL",o.optBoolean("installed",false)?"PASS_MANUAL_CLICK_LISTENER_READY":"LISTENER_INSTALL_FAILED",st);
                }catch(Exception e){
                    JSONObject st=baseState(); put(st,"parse_error_class",e.getClass().getSimpleName()); emit("LISTENER_INSTALL","SANITIZED_PARSE_ERROR",st);
                }
                h.removeCallbacks(sampler); h.post(sampler);
            }
        });
    }

    private void stopObservation(String why){
        if(!observing)return;
        observing=false; h.removeCallbacks(sampler);
        JSONObject st=baseState(); put(st,"stop_reason",why); put(st,"samples",sampleIndex); put(st,"manual_click_count",manualClickCount);
        put(st,"page_ui_dispatches",0); put(st,"page_ui_writes",0); put(st,"observation_only",true);
        emit("FINAL","OBSERVATION_COMPLETE_NO_PAGE_WRITES",st);
        status.setText("OBSERVATION COMPLETE\nTell ChatGPT: انجام شد\nNo page click/write was performed by this observer.");
    }

    private void sampleOnce(){
        if(web==null||!observing)return;
        final int n=++sampleIndex;
        web.evaluateJavascript(snapshotJs(),new ValueCallback<String>(){
            @Override public void onReceiveValue(String value){
                if(!observing)return;
                try{
                    Object outer=new JSONTokener(value).nextValue();
                    String raw=outer instanceof String?(String)outer:String.valueOf(outer);
                    JSONObject o=new JSONObject(raw);
                    JSONArray clicks=o.optJSONArray("manual_clicks");
                    if(clicks!=null){
                        for(int i=0;i<clicks.length();i++){
                            JSONObject c=clicks.optJSONObject(i); if(c==null)continue;
                            manualClickCount++;
                            JSONObject st=baseState();
                            copy(st,c,"click_seq","tag","role","semantic_class","label_hash","testid_hash","data_state","selected","pressed","expanded","disabled","href_class","struct_hash","ancestor_depth");
                            put(st,"manual_click_count",manualClickCount); put(st,"sample_index",n); put(st,"observation_only",true); put(st,"page_ui_dispatches",0); put(st,"page_ui_writes",0);
                            emit("MANUAL_CLICK_OBSERVED","USER_MANUAL_CLICK_SANITIZED",st);
                        }
                    }
                    String fp=o.optString("state_fingerprint","-");
                    boolean changed=!fp.equals(lastFingerprint);
                    boolean heartbeat=(n==1||n%12==0);
                    if(changed||heartbeat){
                        JSONObject st=baseState();
                        copy(st,o,"success","ready","route_class","url_temp_hint","composer_temp_hint","temp_candidate_count","temp_active_count","temp_selected_count","temp_pressed_count","new_chat_candidate_count","back_candidate_count","close_exit_candidate_count","temp_semantic_set_hash","temp_active_set_hash","safe_ui_state_hash","state_fingerprint","semantic_temp_state");
                        put(st,"sample_index",n); put(st,"changed",changed); put(st,"manual_click_count",manualClickCount); put(st,"observation_only",true);
                        put(st,"page_ui_dispatches",0); put(st,"page_ui_writes",0);
                        emit("MANUAL_UI_SNAPSHOT",changed?"STATE_CHANGED":"HEARTBEAT",st);
                        lastFingerprint=fp;
                    }
                    status.setText("OBSERVING sample "+n+"/"+MAX_SAMPLES+" clicks="+manualClickCount+"\nEnter Temporary Chat, pause, then return to normal Chat.\nstate="+o.optString("semantic_temp_state","UNKNOWN"));
                }catch(Exception e){
                    JSONObject st=baseState(); put(st,"sample_index",n); put(st,"parse_error_class",e.getClass().getSimpleName()); emit("MANUAL_UI_SNAPSHOT","SANITIZED_PARSE_ERROR",st);
                }
            }
        });
    }

    private String installJs(){
        return "(function(){try{"+
            "if(window.__cpTempObserverV61&&window.__cpTempObserverV61.installed)return JSON.stringify({installed:true,reused:true});"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};"+
            "const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const DS=e=>{const v=N(e.getAttribute('data-state'));if(['active','selected','checked','on'].includes(v))return 'ACTIVE';if(['inactive','unselected','unchecked','off'].includes(v))return 'INACTIVE';if(v==='open')return 'OPEN';if(v==='closed')return 'CLOSED';return v?'OTHER':'NONE';};"+
            "const HC=e=>{if(!e||!e.getAttribute)return 'NONE';const h=e.getAttribute('href')||'';if(!h)return 'NONE';try{const u=new URL(h,location.href);const p=u.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';return 'OTHER';}catch(x){return 'OTHER';}};"+
            "const SEM=(label,tid)=>{const x=N(label),t=N(tid),z=x+' '+t;if(z.includes('temporary')||x==='temp'||t.includes('temp'))return 'TEMP';if(x.includes('new chat')||t.includes('new-chat')||t.includes('new_chat'))return 'NEW_CHAT';if(x==='back'||x.startsWith('back ')||t.includes('back'))return 'BACK';if(x.includes('exit')||x.includes('close')||x.includes('done')||t.includes('close')||t.includes('exit'))return 'CLOSE_EXIT';return 'OTHER';};"+
            "const actionable=e=>{if(!e||!e.tagName)return false;const tag=e.tagName.toLowerCase(),role=N(e.getAttribute('role'));return tag==='button'||tag==='a'||['button','tab','menuitem','radio','switch','option'].includes(role)||e.hasAttribute('aria-selected')||e.hasAttribute('aria-pressed')||e.hasAttribute('data-state');};"+
            "const O={installed:true,seq:0,events:[]};window.__cpTempObserverV61=O;"+
            "document.addEventListener('click',function(ev){try{let e=ev.target,d=0;while(e&&d<8&&!actionable(e)){e=e.parentElement;d++;}if(!e||!actionable(e))return;const tag=(e.tagName||'').toLowerCase(),role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none'));const label=e.getAttribute('aria-label')||e.innerText||e.textContent||'',tid=e.getAttribute('data-testid')||'',sem=SEM(label,tid);const lh=H(N(label)),th=H(tid),ds=DS(e),sel=e.getAttribute('aria-selected')==='true'?1:0,prs=e.getAttribute('aria-pressed')==='true'?1:0,exp=e.getAttribute('aria-expanded')==='true'?1:0,dis=e.hasAttribute('disabled')?1:0,hc=HC(e),sh=H([tag,role,sem,lh,th,hc].join('|'));O.events.push({click_seq:++O.seq,tag:tag,role:role,semantic_class:sem,label_hash:lh,testid_hash:th,data_state:ds,selected:sel,pressed:prs,expanded:exp,disabled:dis,href_class:hc,struct_hash:sh,ancestor_depth:d});if(O.events.length>24)O.events.shift();}catch(x){}},true);"+
            "return JSON.stringify({installed:true,reused:false});"+
            "}catch(e){return JSON.stringify({installed:false,reused:false});}})();";
    }

    private String snapshotJs(){
        return "(function(){try{"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};"+
            "const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};"+
            "const DS=e=>{const v=N(e.getAttribute('data-state'));if(['active','selected','checked','on'].includes(v))return 'ACTIVE';if(['inactive','unselected','unchecked','off'].includes(v))return 'INACTIVE';if(v==='open')return 'OPEN';if(v==='closed')return 'CLOSED';return v?'OTHER':'NONE';};"+
            "const RC=()=>{const p=location.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';if(/^\\/g\\//.test(p))return 'GPT_ROUTE';if(/^\\/project/.test(p))return 'PROJECT_ROUTE';return 'OTHER_ROUTE';};"+
            "const SEM=(label,tid)=>{const x=N(label),t=N(tid),z=x+' '+t;if(z.includes('temporary')||x==='temp'||t.includes('temp'))return 'TEMP';if(x.includes('new chat')||t.includes('new-chat')||t.includes('new_chat'))return 'NEW_CHAT';if(x==='back'||x.startsWith('back ')||t.includes('back'))return 'BACK';if(x.includes('exit')||x.includes('close')||x.includes('done')||t.includes('close')||t.includes('exit'))return 'CLOSE_EXIT';return 'OTHER';};"+
            "const q=Array.from(document.querySelectorAll('button,a,[role],[aria-selected],[aria-pressed],[data-state],[data-testid]')).filter(V);let temp=[],safe=[],tc=0,ta=0,ts=0,tp=0,nc=0,bc=0,ec=0;"+
            "for(const e of q){const tag=(e.tagName||'').toLowerCase(),role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none'));const actionable=tag==='button'||tag==='a'||['button','tab','menuitem','radio','switch','option'].includes(role)||e.hasAttribute('aria-selected')||e.hasAttribute('aria-pressed')||e.hasAttribute('data-state');if(!actionable)continue;const label=e.getAttribute('aria-label')||e.innerText||e.textContent||'',tid=e.getAttribute('data-testid')||'',sem=SEM(label,tid),ds=DS(e),sel=e.getAttribute('aria-selected')==='true'?1:0,prs=e.getAttribute('aria-pressed')==='true'?1:0,th=H(tid);safe.push([tag,role,th,ds,sel,prs,e.hasAttribute('disabled')?1:0].join('|'));if(sem==='TEMP'){tc++;if(ds==='ACTIVE'||sel===1||prs===1)ta++;if(sel===1)ts++;if(prs===1)tp++;temp.push([tag,role,H(N(label)),th,ds,sel,prs].join('|'));}else if(sem==='NEW_CHAT')nc++;else if(sem==='BACK')bc++;else if(sem==='CLOSE_EXIT')ec++;if(safe.length>=120)break;}"+
            "safe.sort();temp.sort();const act=temp.filter(x=>x.includes('|ACTIVE|')||/\\|1\\|/.test(x)).sort();const urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));let comphint=false;for(const e of Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).filter(V)){const s=N((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('placeholder')||''));if(s.includes('temporary')||s==='temp'){comphint=true;break;}}let semstate=(urlhint||comphint||ta>0)?'TEMP_HINT_ACTIVE':(tc>0?'TEMP_CONTROL_VISIBLE_NO_ACTIVE_HINT':'NO_TEMP_CONTROL_HINT');const O=window.__cpTempObserverV61;const clicks=O&&Array.isArray(O.events)?O.events.splice(0,O.events.length):[];const r=RC(),tsh=H(temp.join('~')),ash=H(act.join('~')),ush=H(safe.join('~'));return JSON.stringify({success:true,ready:document.readyState,route_class:r,url_temp_hint:urlhint,composer_temp_hint:comphint,temp_candidate_count:tc,temp_active_count:ta,temp_selected_count:ts,temp_pressed_count:tp,new_chat_candidate_count:nc,back_candidate_count:bc,close_exit_candidate_count:ec,temp_semantic_set_hash:tsh,temp_active_set_hash:ash,safe_ui_state_hash:ush,semantic_temp_state:semstate,state_fingerprint:H([r,urlhint?1:0,comphint?1:0,tc,ta,tsh,ash,ush].join('#')),manual_clicks:clicks});"+
            "}catch(e){return JSON.stringify({success:false,ready:'error',route_class:'ERROR',semantic_temp_state:'UNKNOWN',manual_clicks:[]});}})();";
    }

    private JSONObject baseState(){
        JSONObject o=new JSONObject(); put(o,"elapsed_ms",Math.max(0,System.currentTimeMillis()-startedMs));
        put(o,"cookies_tokens_accessed",false); put(o,"raw_html_uploaded",false); put(o,"raw_text_uploaded",false); put(o,"raw_url_uploaded",false);
        put(o,"geometry_click_used",false); put(o,"model_option_writes",0); put(o,"effort_writes",0); put(o,"chat_work_writes",0); put(o,"pro_write_attempted",false);
        return o;
    }

    private void emit(String phase,String classification,JSONObject state){
        if(!TelemetryConfigV61.CONFIGURED)return;
        JSONObject o=new JSONObject(); put(o,"schema_version",SCHEMA); put(o,"scenario_id",SCENARIO); put(o,"test_id",testId);
        put(o,"collector_id",TelemetryConfigV61.COLLECTOR_ID); put(o,"source_ref",TelemetryConfigV61.SOURCE_REF);
        put(o,"seq",telemetrySeq++); put(o,"timestamp_epoch_ms",System.currentTimeMillis()); put(o,"phase",phase); put(o,"classification",classification);
        try{o.put("state",state);}catch(Exception ignored){}
        final byte[] bytes=o.toString().getBytes(StandardCharsets.UTF_8);
        net.execute(()->{HttpURLConnection c=null;try{c=(HttpURLConnection)new URL(TelemetryConfigV61.WEBHOOK_URL).openConnection();c.setRequestMethod("POST");c.setConnectTimeout(5000);c.setReadTimeout(5000);c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json");c.setFixedLengthStreamingMode(bytes.length);try(OutputStream os=c.getOutputStream()){os.write(bytes);}c.getResponseCode();}catch(Exception ignored){}finally{if(c!=null)c.disconnect();}});
    }

    private void eval(String js,ValueCallback<String> cb){if(web!=null)web.evaluateJavascript(js,cb);}
    private static void put(JSONObject o,String k,Object v){try{o.put(k,v);}catch(Exception ignored){}}
    private static void copy(JSONObject dst,JSONObject src,String... keys){for(String k:keys)if(src.has(k))try{dst.put(k,src.get(k));}catch(Exception ignored){}}
    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}

    @Override public void onBackPressed(){if(web!=null&&web.canGoBack())web.goBack();else super.onBackPressed();}
    @Override protected void onDestroy(){observing=false;h.removeCallbacks(sampler);net.shutdownNow();if(web!=null)web.destroy();super.onDestroy();}
}
'''
ACT.write_text(activity)

cfg=(PKG/"TelemetryConfigV60.java").read_text()
(PKG/"TelemetryConfigV61.java").write_text(cfg.replace("TelemetryConfigV60","TelemetryConfigV61"))

g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+61\b","versionCode 62",gs)
gs=gs.replace("0.58-stable-diag-chat-work-recovery-roundtrip","0.59-stable-diag-temporary-chat-manual-observation")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorChatWorkRecoveryRoundtripV60Activity","OrchestratorTemporaryChatManualObservationV61Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
for v in (52,53,54,55,56,57,58,59,60,61):
    assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

# Observation-only launch activity: no page-side click/write API is allowed.
a=ACT.read_text()
for forbidden in [".click();","performClick(","dispatchTouchEvent(","elementFromPoint","document.evaluate","ACTION_SET_PROGRESS","setAttribute(\"aria-value","clickModelOption","captureModelMenu","CookieManager","addJavascriptInterface"]:
    assert forbidden not in a, forbidden
assert "addEventListener('click'" in a
assert "preventDefault" not in a
assert "stopPropagation" not in a
assert 'page_ui_dispatches\",0' in a
assert 'page_ui_writes\",0' in a
assert 'model_option_writes\",0' in a
assert 'effort_writes\",0' in a
assert 'chat_work_writes\",0' in a
assert 'raw_text_uploaded\",false' in a
assert 'raw_html_uploaded\",false' in a
assert 'raw_url_uploaded\",false' in a

print(ACT)
