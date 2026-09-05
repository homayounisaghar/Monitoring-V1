package com.homayounisaghar.chatgptwebviewprobe;

import android.content.Intent;
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

import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;

/** v0.49: human-assisted, zero-write model-trigger/menu discovery. */
public class OrchestratorPaidModelHumanOpenDiscoveryV51Activity extends OrchestratorAuthModeV34Activity {
    private static final String SCHEMA="cp-v51-paid-model-human-open-discovery-v1";
    private static final String SCENARIO="paid-model-human-open-discovery";
    private static final int NET_TIMEOUT_MS=3200;
    private static final long OBSERVE_TIMEOUT_MS=15000L;
    private final Handler h=new Handler(Looper.getMainLooper());
    private WebView web; private TextView status; private Button arm;
    private boolean running=false, telemetryHealthy=false; private String testId="-"; private int seq=0; private long started=0L;
    private JSONObject baselineClosed=new JSONObject();

    @Override public void onCreate(Bundle b){
        super.onCreate(b); web=findWeb(getWindow().getDecorView()); installUi(); setStatus("v0.49 model discovery ready — zero automatic model writes");
    }
    @Override protected void onDestroy(){h.removeCallbacksAndMessages(null);ControlPlaneAccessibilityServiceV51.disarmManualModelClickObservation();super.onDestroy();}
    @Override protected void onResume(){super.onResume();h.postDelayed(()->{if(!running&&status!=null){setStatus(ControlPlaneAccessibilityServiceV51.isObserverReady()?"Ready — tap ARM, then manually tap the model name at the top":"Accessibility verifier disabled — ARM opens Settings");}},180L);}

    private void installUi(){
        if(web==null)return; ViewParent p=web.getParent(); if(!(p instanceof LinearLayout))return; LinearLayout root=(LinearLayout)p;
        for(int i=0;i<root.getChildCount();i++){View c=root.getChildAt(i);if(c!=web)c.setVisibility(View.GONE);} web.setMinimumHeight(1);web.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,0,1f));
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);panel.setPadding(dp(8),dp(3),dp(8),dp(6));
        status=new TextView(this);status.setTextSize(11f);status.setSingleLine(true);status.setEllipsize(TextUtils.TruncateAt.END);panel.addView(status,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT));
        arm=new Button(this);arm.setText("ARM MODEL MENU OBSERVER");arm.setTextSize(13f);arm.setAllCaps(false);arm.setOnClickListener(v->armRun());panel.addView(arm,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(47)));
        root.addView(panel,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void armRun(){
        if(running)return; if(web==null||!isChatGpt(web.getUrl())){setStatus("Blocked: ChatGPT page not ready");return;}
        if(!ControlPlaneAccessibilityServiceV51.isObserverReady()){
            setStatus("Enable CP WebView semantic verifier, return, then ARM again"); try{startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));}catch(Exception ignored){} return;
        }
        JSONObject ready=ControlPlaneAccessibilityServiceV50.captureReadiness(); if(!ready.optBoolean("success",false)||ready.optInt("web_node_count",0)<5){setStatus("Accessibility tree not ready; zero writes");return;}
        running=true; telemetryHealthy=false; testId="cp51-"+UUID.randomUUID();seq=0;started=System.currentTimeMillis();arm.setEnabled(false);arm.setText("WAITING FOR YOUR MANUAL MODEL CLICK...");setStatus("Telemetry preflight...");
        telemetryPreflight();
    }

    private void telemetryPreflight(){
        JSONObject p=payload("TELEMETRY_PREFLIGHT","RUNNING",baseState()); AtomicBoolean once=new AtomicBoolean(false);
        Runnable timeout=()->{if(running&&once.compareAndSet(false,true))finish("TELEMETRY_PREFLIGHT_TIMEOUT");};h.postDelayed(timeout,8000L);
        new Thread(()->{JSONObject r=upload(p,NET_TIMEOUT_MS+900);runOnUiThread(()->{if(!running||!once.compareAndSet(false,true))return;h.removeCallbacks(timeout);if(!r.optBoolean("success",false)){finish("TELEMETRY_UNAVAILABLE");return;}telemetryHealthy=true;phase("RUN_STARTED","MODEL_HUMAN_OPEN_ZERO_WRITE_DISCOVERY",baseState());armObserver();});},"cp51-preflight").start();
    }

    private void armObserver(){
        baselineClosed=ControlPlaneAccessibilityServiceV50.captureClosedModelSurface(); JSONObject st=baseState();copy(st,baselineClosed,"success","complete","visited_count","web_node_count","model_trigger_count","model_trigger_hash","model_trigger_semantic","model_trigger_set_hash");
        phase("CLOSED_BASELINE_CENSUS","CAPTURED_BEFORE_HUMAN_MODEL_CLICK",st);
        JSONObject armed=ControlPlaneAccessibilityServiceV51.armManualModelClickObservation(); if(!armed.optBoolean("success",false)){finish("OBSERVER_ARM_FAILED_ZERO_WRITE");return;}
        setStatus("ARMED — now tap the model name at the TOP of the WebView once");
        h.postDelayed(()->pollOpenMenu(0),180L); h.postDelayed(()->{if(running)finish("HUMAN_MODEL_OPEN_NOT_OBSERVED_TIMEOUT_ZERO_WRITE");},OBSERVE_TIMEOUT_MS);
    }

    private void pollOpenMenu(int n){
        if(!running)return; JSONObject ev=ControlPlaneAccessibilityServiceV51.captureManualClickEvidence(); String fallback=ev.optString("nearest_model_hash","-"); if("-".equals(fallback))fallback=ev.optString("source_label_hash","-");
        JSONObject menu=ControlPlaneAccessibilityServiceV50.captureModelMenu(fallback); boolean human=ev.optBoolean("human_click_seen",false); boolean exact=menu.optBoolean("success",false)&&menu.optBoolean("complete",false)&&menu.optBoolean("exact_expected_set",false)&&menu.optInt("group_count",0)==1&&menu.optInt("option_count",0)==3;
        String es=ev.optString("nearest_model_semantic","NONE"); boolean semOk="LATEST".equals(es)||"GPT56_SOL".equals(es)||"GPT55".equals(es);
        if(human&&exact){
            JSONObject st=baseState(); copy(st,ev,"observed_event_count","clicked_event_count","human_click_seen","last_event_type","source_label_hash","source_semantic","nearest_model_hash","nearest_model_semantic","source_class_hash","action_set_hash","ancestry_hash","source_clickable","source_selected");
            copy(st,menu,"visited_count","web_node_count","group_count","option_count","selected_count","group_hash","current_option_hash","target_option_hash","current_semantic","target_semantic","exact_expected_set","selection_basis","option_set_hash");
            phase("OPEN_MODEL_MENU_CAPTURE",semOk?"PASS_HUMAN_MODEL_TRIGGER_AND_EXACT_MENU_DISCOVERED":"PASS_EXACT_MODEL_MENU_DISCOVERED_TRIGGER_EVENT_SEMANTIC_INCOMPLETE",st);
            finish(semOk?"PASS_HUMAN_MODEL_TRIGGER_AND_EXACT_MENU_DISCOVERED_ZERO_WRITE":"PARTIAL_EXACT_MODEL_MENU_DISCOVERED_TRIGGER_SEMANTIC_INCOMPLETE_ZERO_WRITE"); return;
        }
        if(human && n%5==0){JSONObject st=baseState();copy(st,ev,"observed_event_count","clicked_event_count","human_click_seen","source_label_hash","source_semantic","nearest_model_hash","nearest_model_semantic","ancestry_hash");copy(st,menu,"group_count","option_count","exact_expected_set","option_set_hash");phase("MODEL_OPEN_POLL","HUMAN_CLICK_SEEN_WAITING_FOR_EXACT_MODEL_MENU",st);}
        h.postDelayed(()->pollOpenMenu(n+1),180L);
    }

    private JSONObject baseState(){JSONObject o=new JSONObject();put(o,"model_trigger_clicks_by_app",0);put(o,"model_option_clicks_by_app",0);put(o,"effort_writes_by_app",0);put(o,"pro_write_attempted",false);put(o,"raw_text_uploaded",false);put(o,"raw_html_uploaded",false);put(o,"cookies_tokens_accessed",false);put(o,"geometry_click_used",false);return o;}
    private void finish(String c){if(!running)return;JSONObject st=baseState();JSONObject ev=ControlPlaneAccessibilityServiceV51.captureManualClickEvidence();copy(st,ev,"observed_event_count","clicked_event_count","human_click_seen","source_label_hash","source_semantic","nearest_model_hash","nearest_model_semantic","source_class_hash","action_set_hash","ancestry_hash","source_clickable","source_selected");put(st,"runtime_ms",System.currentTimeMillis()-started);if(telemetryHealthy)new Thread(()->upload(payload("FINAL",c,st),NET_TIMEOUT_MS),"cp51-final").start();ControlPlaneAccessibilityServiceV51.disarmManualModelClickObservation();running=false;setStatus(c);arm.setEnabled(true);arm.setText("ARM MODEL MENU OBSERVER");}
    private void phase(String ph,String cl,JSONObject st){if(!running||!telemetryHealthy)return;JSONObject p=payload(ph,cl,st);new Thread(()->upload(p,NET_TIMEOUT_MS),"cp51-phase-"+seq).start();}
    private JSONObject payload(String ph,String cl,JSONObject st){JSONObject p=new JSONObject();put(p,"schema_version",SCHEMA);put(p,"scenario_id",SCENARIO);put(p,"source_ref",TelemetryConfigV51.SOURCE_REF);put(p,"collector_id",TelemetryConfigV51.COLLECTOR_ID);put(p,"test_id",testId);put(p,"seq",seq++);put(p,"timestamp_epoch_ms",System.currentTimeMillis());put(p,"phase",ph);put(p,"classification",cl);put(p,"state",st);return p;}
    private JSONObject upload(JSONObject payload,int timeoutMs){JSONObject r=new JSONObject();HttpURLConnection c=null;try{if(!TelemetryConfigV51.CONFIGURED){put(r,"success",false);return r;}URL u=new URL(TelemetryConfigV51.WEBHOOK_URL);c=(HttpURLConnection)u.openConnection();c.setRequestMethod("POST");c.setConnectTimeout(timeoutMs);c.setReadTimeout(timeoutMs);c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json");byte[] body=payload.toString().getBytes(StandardCharsets.UTF_8);c.getOutputStream().write(body);int code=c.getResponseCode();put(r,"success",code>=200&&code<300);put(r,"http_code",code);return r;}catch(Exception e){put(r,"success",false);put(r,"error_class",e.getClass().getSimpleName());return r;}finally{if(c!=null)c.disconnect();}}
    private WebView findWeb(View v){if(v instanceof WebView)return(WebView)v;if(v instanceof android.view.ViewGroup){android.view.ViewGroup g=(android.view.ViewGroup)v;for(int i=0;i<g.getChildCount();i++){WebView w=findWeb(g.getChildAt(i));if(w!=null)return w;}}return null;}
    private boolean isChatGpt(String u){if(u==null)return false;try{Uri x=Uri.parse(u);String h=x.getHost();return h!=null&&(h.equals("chatgpt.com")||h.endsWith(".chatgpt.com"));}catch(Exception e){return false;}}
    private int dp(int x){return(int)(x*getResources().getDisplayMetrics().density+0.5f);} private void setStatus(String s){if(status!=null)status.setText(s);} private static void put(JSONObject o,String k,Object v){try{o.put(k,v);}catch(Exception ignored){}}
    private static void copy(JSONObject d,JSONObject s,String...ks){for(String k:ks)if(s.has(k))try{d.put(k,s.get(k));}catch(Exception ignored){}}
}
