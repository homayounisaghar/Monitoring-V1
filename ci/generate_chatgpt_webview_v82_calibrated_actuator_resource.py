#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.80: calibrated-actuator + TOCTOU-safe assistant-local Resource acceptance.
# The semantic resolver decides WHAT. A benign internal WebView calibrates HOW.
# If the certified Resource is transiently absent before any effect, event-driven
# re-observation is allowed; after an effect is dispatched, no blind replay exists.
runpy.run_path("ci/generate_chatgpt_webview_v81_assistant_local_resource_acceptance.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorResourceToolsV81Activity.java"
ACT=PKG/"OrchestratorResourceToolsV82Activity.java"
s=OLD.read_text()

def method(name,body,rettype="void"):
    global s
    pat=rf'    private {re.escape(rettype)} {re.escape(name)}\([^\n]*\)\{{.*?\n    \}}\n\n'
    m=re.search(pat,s,re.S)
    assert m,(rettype,name,"method not found")
    s=s[:m.start()]+body+s[m.end():]

s=s.replace("OrchestratorResourceToolsV81Activity","OrchestratorResourceToolsV82Activity")
s=s.replace("TelemetryConfigV81","TelemetryConfigV82")
s=s.replace("V81","V82")
s=s.replace('SCHEMA="cp-v81-assistant-local-resource-acceptance-v1"','SCHEMA="cp-v82-calibrated-actuator-resource-v1"')
s=s.replace('SCENARIO="assistant-local-nohref-resource-closed-loop"','SCENARIO="calibrated-actuator-toctou-safe-resource"')
s=s.replace('getSharedPreferences("cp_v81_assistant_local_resource",MODE_PRIVATE)','getSharedPreferences("cp_v82_calibrated_actuator_resource",MODE_PRIVATE)')
s=s.replace('testId="cp79-"+UUID.randomUUID();','testId="cp80-"+UUID.randomUUID();')
s=s.replace('resource_v81_','resource_v82_')
s=s.replace('v0.79 Assistant-local Resource acceptance ready.','v0.80 Calibrated actuator Resource acceptance ready.')

field_anchor='    private boolean resourceV82ClickConfirmed=false;\n'
assert s.count(field_anchor)==1,s.count(field_anchor)
fields='''    private boolean resourceV82PreEffectPending=false;
    private boolean resourceV82DriveInFlight=false;
    private boolean resourceV82EffectDispatched=false;
    private long resourceV82ClaimDocumentEpoch=-1L;
    private long resourceV82ClaimPageFinishedEpoch=-1L;
    private String resourceV82ClaimAssistantToken="-";
    private String resourceV82InitialCandidateToken="-";
    private String resourceV82Actuator="NONE";
    private long resourceV82TimeoutSerial=0L;
    private final android.os.Handler resourceV82Handler=new android.os.Handler(android.os.Looper.getMainLooper());
    private android.webkit.WebView resourceV82CalibrationWeb=null;
    private android.webkit.WebView resourceV82CalibrationChild=null;
    private String resourceV82CalibrationPhase="IDLE";
    private boolean resourceV82CalibrationDone=false;
    private boolean resourceV82CalibrationPopupSeen=false;
    private boolean resourceV82CalibrationIsUserGesture=false;
    private long resourceV82CalibrationSerial=0L;
'''
s=s.replace(field_anchor,field_anchor+fields,1)

obs='    private void onObservedState(JSONObject o,String reason){\n'
assert s.count(obs)==1,s.count(obs)
s=s.replace(obs,obs+'        if(resourceV82PreEffectPending&&!resourceV82EffectDispatched)driveResourceV82OnObservedState(reason);\n',1)

method('clearResourceV82TerminalState',r'''    private void clearResourceV82TerminalState(){
        resourceV82PreEffectPending=false;resourceV82DriveInFlight=false;resourceV82EffectDispatched=false;
        resourceV82ClaimDocumentEpoch=-1L;resourceV82ClaimPageFinishedEpoch=-1L;resourceV82ClaimAssistantToken="-";resourceV82InitialCandidateToken="-";resourceV82Actuator="NONE";
        resourceNavigationPending=false;resourceDownloadPending=false;resourceWrappedInitialHref="";resourceV82AdmissionToken="-";resourceV82ActionOrigin="";resourceV82NewWindowObserved=false;
        try{if(web!=null)web.getSettings().setJavaScriptCanOpenWindowsAutomatically(false);}catch(Exception ignored){}
        destroyResourceChildWindowV82();resourceActionPendingId="-";
    }

''')

method('invalidateResourceV82OnDocumentStart',r'''    private void invalidateResourceV82OnDocumentStart(){
        resourceScanDocumentEpoch=-1L;resourceScanPageFinishedEpoch=-1L;resourceSelectedId="-";resourceSelectedKind="-";resourceSelectedHref="";resourceSelectedLocatorCount=0;
        if(resourceV82PreEffectPending&&!resourceV82EffectDispatched&&!resourceV82Finalized){
            resourceV82Finalized=true;prefs.edit().putString("resource_v82_claim_status","DOCUMENT_CHANGED_PRE_EFFECT_ABORTED").commit();
            JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"pre_effect",true);put(st,"effect_dispatched",false);put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);
            emit("RESOURCE_ACTION","RESOURCE_ACTION_ABORTED_DOCUMENT_CHANGED_PRE_EFFECT",st);status.setText("Resource transaction aborted: page changed before actuation.");clearResourceV82TerminalState();return;
        }
        if(!resourceNavigationPending&&!resourceDownloadPending&&!resourceV82Finalized)resourceActionPendingId="-";
    }

''')

method('runResourceActionV82',r'''    private void runResourceActionV82(){
        testId="cp80-"+UUID.randomUUID();startedMs=System.currentTimeMillis();telemetrySeq=0;remoteTelemetryPosts=0;
        JSONObject attempt=baseState();put(attempt,"calibration_required",true);put(attempt,"semantic_family","ASSISTANT_LOCAL_NOHREF_OUTBOUND_ANCHOR");put(attempt,"raw_url_remote",false);put(attempt,"raw_text_remote",false);put(attempt,"raw_html_remote",false);
        emit("RESOURCE_ACTION","RESOURCE_ACTION_ATTEMPTED",attempt);
        if(learning||plannerRunning||toolsTestRunning||resourceDownloadPending||resourceNavigationPending||resourceV82PreEffectPending){emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_BUSY",attempt);status.setText("TEST RESOURCE blocked while another operation is active.");return;}
        resourceV82Finalized=false;resourceV82ClickConfirmed=false;resourceV82NewWindowObserved=false;resourceV82EffectDispatched=false;resourceV82PreEffectPending=false;resourceV82DriveInFlight=false;
        resourceV82AdmissionToken="-";resourceV82ClaimAssistantToken="-";resourceV82InitialCandidateToken="-";resourceV82Actuator="NONE";resourceActionPendingId="-";
        startResourceActuatorCalibrationV82();
    }

''')

insert=s.index('    private String assistantLocalResourceCertifyV82Js(){\n')
helpers=r'''    private String resourceCalibrationHtmlV82(){
        return "<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>html,body{margin:0;width:100%;height:100%;overflow:hidden}#cpcal{display:flex;width:100%;height:100%;align-items:center;justify-content:center;font-size:12px}</style></head><body><a id='cpcal' href='#' role='link'>CP_ACTUATION_CALIBRATION</a><script>window.__cpTrusted=false;window.__cpActive=false;window.__cpOpenResult=false;document.getElementById('cpcal').addEventListener('click',function(e){window.__cpTrusted=!!e.isTrusted;window.__cpActive=!!(navigator.userActivation&&navigator.userActivation.isActive);e.preventDefault();try{window.__cpOpenResult=!!window.open('https://cp-target.invalid/receipt','_blank');}catch(x){window.__cpOpenResult=false;}});</script></body></html>";
    }

    private void destroyResourceCalibrationV82(){
        android.webkit.WebView c=resourceV82CalibrationChild;resourceV82CalibrationChild=null;if(c!=null){try{c.stopLoading();}catch(Exception ignored){}try{c.destroy();}catch(Exception ignored){}}
        android.webkit.WebView w=resourceV82CalibrationWeb;resourceV82CalibrationWeb=null;if(w!=null){try{android.view.ViewParent p=w.getParent();if(p instanceof android.view.ViewGroup)((android.view.ViewGroup)p).removeView(w);}catch(Exception ignored){}try{w.stopLoading();}catch(Exception ignored){}try{w.destroy();}catch(Exception ignored){}}
    }

    private void emitCalibrationV82(String classification,String actuator,boolean pass,boolean popup,boolean userGesture,boolean eventTrusted,boolean userActive){
        JSONObject st=baseState();put(st,"actuator",actuator);put(st,"pass",pass);put(st,"popup_observed",popup);put(st,"oncreatewindow_user_gesture",userGesture);put(st,"event_trusted",eventTrusted);put(st,"user_activation_active",userActive);put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);
        emit("ACTUATOR_CALIBRATION",classification,st);
    }

    private void startResourceActuatorCalibrationV82(){
        destroyResourceCalibrationV82();resourceV82CalibrationDone=false;resourceV82CalibrationPopupSeen=false;resourceV82CalibrationIsUserGesture=false;resourceV82CalibrationPhase="JS";final long serial=++resourceV82CalibrationSerial;
        JSONObject st=baseState();put(st,"calibration_surface","BENIGN_INTERNAL_WEBVIEW");put(st,"actuator_order","JS_POPUP|ACCESSIBILITY_CLICK|NATIVE_TOUCH");put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);emit("ACTUATOR_CALIBRATION","ACTUATOR_CALIBRATION_STARTED",st);
        try{
            final android.webkit.WebView cal=new android.webkit.WebView(this);resourceV82CalibrationWeb=cal;cal.getSettings().setJavaScriptEnabled(true);cal.getSettings().setSupportMultipleWindows(true);cal.getSettings().setJavaScriptCanOpenWindowsAutomatically(true);cal.setBackgroundColor(android.graphics.Color.WHITE);
            cal.setWebChromeClient(new android.webkit.WebChromeClient(){
                @Override public boolean onCreateWindow(android.webkit.WebView view,boolean isDialog,boolean isUserGesture,android.os.Message resultMsg){
                    if(resourceV82CalibrationDone||serial!=resourceV82CalibrationSerial)return false;
                    resourceV82CalibrationPopupSeen=true;resourceV82CalibrationIsUserGesture=isUserGesture;
                    try{
                        final android.webkit.WebView child=new android.webkit.WebView(OrchestratorResourceToolsV82Activity.this);resourceV82CalibrationChild=child;child.getSettings().setJavaScriptEnabled(false);
                        child.setWebViewClient(new android.webkit.WebViewClient(){
                            @Override public boolean shouldOverrideUrlLoading(android.webkit.WebView v,android.webkit.WebResourceRequest r){try{v.stopLoading();}catch(Exception ignored){}return true;}
                            @Override public boolean shouldOverrideUrlLoading(android.webkit.WebView v,String u){try{v.stopLoading();}catch(Exception ignored){}return true;}
                            @Override public void onPageStarted(android.webkit.WebView v,String u,android.graphics.Bitmap f){super.onPageStarted(v,u,f);try{v.stopLoading();}catch(Exception ignored){}}
                        });
                        android.webkit.WebView.WebViewTransport transport=(android.webkit.WebView.WebViewTransport)resultMsg.obj;transport.setWebView(child);resultMsg.sendToTarget();
                    }catch(Exception e){return false;}
                    captureCalibrationDomStateV82(serial,true,isUserGesture);
                    return true;
                }
            });
            cal.setWebViewClient(new android.webkit.WebViewClient(){
                @Override public void onPageFinished(android.webkit.WebView v,String u){super.onPageFinished(v,u);if(serial!=resourceV82CalibrationSerial||resourceV82CalibrationDone)return;runCurrentCalibrationPhaseV82(serial);}
            });
            android.view.ViewParent parent=web==null?null:web.getParent();if(!(parent instanceof android.view.ViewGroup))throw new IllegalStateException("NO_PARENT");
            android.view.ViewGroup vg=(android.view.ViewGroup)parent;int index=vg.indexOfChild(web);android.widget.LinearLayout.LayoutParams lp=new android.widget.LinearLayout.LayoutParams(android.view.ViewGroup.LayoutParams.MATCH_PARENT,dp(64));vg.addView(cal,Math.max(0,index),lp);
            cal.loadDataWithBaseURL("https://cp-calibration.invalid/",resourceCalibrationHtmlV82(),"text/html","UTF-8",null);
        }catch(Exception e){destroyResourceCalibrationV82();emitCalibrationV82("ACTUATOR_CALIBRATION_SETUP_FAILED","NONE",false,false,false,false,false);status.setText("Actuator calibration failed before touching ChatGPT.");}
    }

    private void runCurrentCalibrationPhaseV82(final long serial){
        if(serial!=resourceV82CalibrationSerial||resourceV82CalibrationDone||resourceV82CalibrationWeb==null)return;final android.webkit.WebView cal=resourceV82CalibrationWeb;resourceV82CalibrationPopupSeen=false;resourceV82CalibrationIsUserGesture=false;
        if("JS".equals(resourceV82CalibrationPhase)){
            try{cal.getSettings().setJavaScriptCanOpenWindowsAutomatically(true);}catch(Exception ignored){}
            cal.evaluateJavascript("(function(){window.__cpTrusted=false;window.__cpActive=false;window.__cpOpenResult=false;var a=document.getElementById('cpcal');if(!a)return JSON.stringify({ok:false});a.click();return JSON.stringify({ok:true,open:!!window.__cpOpenResult,trusted:!!window.__cpTrusted,active:!!window.__cpActive});})()",v->{
                if(serial!=resourceV82CalibrationSerial||resourceV82CalibrationDone)return;boolean open=v!=null&&v.contains("\\\"open\\\":true");boolean trusted=v!=null&&v.contains("\\\"trusted\\\":true");boolean active=v!=null&&v.contains("\\\"active\\\":true");
                if(!open&&!resourceV82CalibrationPopupSeen){emitCalibrationV82("ACTUATOR_JS_POPUP_CALIBRATION_FAILED","JS_POPUP",false,false,false,trusted,active);advanceCalibrationV82(serial,"ACCESSIBILITY");return;}
                final long t=++resourceV82TimeoutSerial;resourceV82Handler.postDelayed(()->{if(serial==resourceV82CalibrationSerial&&!resourceV82CalibrationDone&&"JS".equals(resourceV82CalibrationPhase)&&t==resourceV82TimeoutSerial&&!resourceV82CalibrationPopupSeen){emitCalibrationV82("ACTUATOR_JS_POPUP_CALIBRATION_TIMEOUT","JS_POPUP",false,false,false,trusted,active);advanceCalibrationV82(serial,"ACCESSIBILITY");}},1800L);
            });return;
        }
        if("ACCESSIBILITY".equals(resourceV82CalibrationPhase)){
            try{cal.getSettings().setJavaScriptCanOpenWindowsAutomatically(false);}catch(Exception ignored){}
            cal.post(()->{if(serial!=resourceV82CalibrationSerial||resourceV82CalibrationDone)return;JSONObject r=ControlPlaneAccessibilityServiceV51.performV82CalibrationClick("CP_ACTUATION_CALIBRATION");boolean performed=r.optBoolean("performed",false);int matches=r.optInt("exact_label_matches",0);JSONObject st=baseState();put(st,"actuator","ACCESSIBILITY_CLICK");put(st,"accessibility_ready",r.optBoolean("service_ready",false));put(st,"exact_label_matches",matches);put(st,"action_performed",performed);put(st,"raw_text_remote",false);emit("ACTUATOR_CALIBRATION","ACTUATOR_ACCESSIBILITY_DISPATCH_RESULT",st);if(!performed){emitCalibrationV82("ACTUATOR_ACCESSIBILITY_CALIBRATION_FAILED","ACCESSIBILITY_CLICK",false,false,false,false,false);advanceCalibrationV82(serial,"NATIVE");return;}final long t=++resourceV82TimeoutSerial;resourceV82Handler.postDelayed(()->{if(serial==resourceV82CalibrationSerial&&!resourceV82CalibrationDone&&"ACCESSIBILITY".equals(resourceV82CalibrationPhase)&&t==resourceV82TimeoutSerial&&!resourceV82CalibrationPopupSeen){emitCalibrationV82("ACTUATOR_ACCESSIBILITY_CALIBRATION_TIMEOUT","ACCESSIBILITY_CLICK",false,false,false,false,false);advanceCalibrationV82(serial,"NATIVE");}},1800L);});return;
        }
        if("NATIVE".equals(resourceV82CalibrationPhase)){
            try{cal.getSettings().setJavaScriptCanOpenWindowsAutomatically(false);}catch(Exception ignored){}
            cal.post(()->{if(serial!=resourceV82CalibrationSerial||resourceV82CalibrationDone)return;float x=Math.max(1f,cal.getWidth()/2f),y=Math.max(1f,cal.getHeight()/2f);long now=android.os.SystemClock.uptimeMillis();android.view.MotionEvent d=android.view.MotionEvent.obtain(now,now,android.view.MotionEvent.ACTION_DOWN,x,y,0);android.view.MotionEvent u=android.view.MotionEvent.obtain(now,now+16L,android.view.MotionEvent.ACTION_UP,x,y,0);boolean down=false,up=false;try{down=cal.dispatchTouchEvent(d);up=cal.dispatchTouchEvent(u);}finally{d.recycle();u.recycle();}JSONObject st=baseState();put(st,"actuator","NATIVE_TOUCH");put(st,"down_dispatched",down);put(st,"up_dispatched",up);put(st,"geometry_role","ACTUATION_TRANSPORT_ONLY");put(st,"raw_text_remote",false);emit("ACTUATOR_CALIBRATION","ACTUATOR_NATIVE_TOUCH_DISPATCH_RESULT",st);if(!down||!up){emitCalibrationV82("ACTUATOR_NATIVE_TOUCH_CALIBRATION_FAILED","NATIVE_TOUCH",false,false,false,false,false);failAllCalibrationV82();return;}final long t=++resourceV82TimeoutSerial;resourceV82Handler.postDelayed(()->{if(serial==resourceV82CalibrationSerial&&!resourceV82CalibrationDone&&"NATIVE".equals(resourceV82CalibrationPhase)&&t==resourceV82TimeoutSerial&&!resourceV82CalibrationPopupSeen){emitCalibrationV82("ACTUATOR_NATIVE_TOUCH_CALIBRATION_TIMEOUT","NATIVE_TOUCH",false,false,false,false,false);failAllCalibrationV82();}},1800L);});
        }
    }

    private void captureCalibrationDomStateV82(final long serial,final boolean popup,final boolean userGesture){
        final android.webkit.WebView cal=resourceV82CalibrationWeb;if(cal==null||serial!=resourceV82CalibrationSerial||resourceV82CalibrationDone)return;
        cal.evaluateJavascript("JSON.stringify({trusted:!!window.__cpTrusted,active:!!window.__cpActive,open:!!window.__cpOpenResult})",v->{if(serial!=resourceV82CalibrationSerial||resourceV82CalibrationDone)return;boolean trusted=v!=null&&v.contains("\\\"trusted\\\":true");boolean active=v!=null&&v.contains("\\\"active\\\":true");String phase=resourceV82CalibrationPhase;boolean pass=false;if("JS".equals(phase))pass=popup;else pass=popup&&(userGesture||trusted||active);if(pass){String actuator="JS".equals(phase)?"JS_POPUP":("ACCESSIBILITY".equals(phase)?"ACCESSIBILITY_CLICK":"NATIVE_TOUCH");completeCalibrationV82(actuator,popup,userGesture,trusted,active);}else if("JS".equals(phase)){emitCalibrationV82("ACTUATOR_JS_POPUP_CALIBRATION_SEMANTICS_FAILED","JS_POPUP",false,popup,userGesture,trusted,active);advanceCalibrationV82(serial,"ACCESSIBILITY");}else if("ACCESSIBILITY".equals(phase)){emitCalibrationV82("ACTUATOR_ACCESSIBILITY_CALIBRATION_SEMANTICS_FAILED","ACCESSIBILITY_CLICK",false,popup,userGesture,trusted,active);advanceCalibrationV82(serial,"NATIVE");}else{emitCalibrationV82("ACTUATOR_NATIVE_TOUCH_CALIBRATION_SEMANTICS_FAILED","NATIVE_TOUCH",false,popup,userGesture,trusted,active);failAllCalibrationV82();}});
    }

    private void advanceCalibrationV82(final long serial,String next){
        if(serial!=resourceV82CalibrationSerial||resourceV82CalibrationDone)return;resourceV82CalibrationPhase=next;resourceV82CalibrationPopupSeen=false;resourceV82CalibrationIsUserGesture=false;final android.webkit.WebView cal=resourceV82CalibrationWeb;if(cal==null){failAllCalibrationV82();return;}try{android.webkit.WebView c=resourceV82CalibrationChild;resourceV82CalibrationChild=null;if(c!=null)c.destroy();}catch(Exception ignored){}cal.loadDataWithBaseURL("https://cp-calibration.invalid/",resourceCalibrationHtmlV82(),"text/html","UTF-8",null);
    }

    private void completeCalibrationV82(String actuator,boolean popup,boolean userGesture,boolean trusted,boolean active){
        if(resourceV82CalibrationDone)return;resourceV82CalibrationDone=true;resourceV82Actuator=actuator;++resourceV82TimeoutSerial;emitCalibrationV82("PASS_ACTUATOR_CALIBRATION_SELECTED",actuator,true,popup,userGesture,trusted,active);destroyResourceCalibrationV82();status.setText("Actuator calibrated: "+actuator+". Certifying Resource...");beginResourceAcceptanceV82();
    }

    private void failAllCalibrationV82(){
        if(resourceV82CalibrationDone)return;resourceV82CalibrationDone=true;++resourceV82TimeoutSerial;emitCalibrationV82("ACTUATOR_CALIBRATION_FAILED_ALL_PUBLIC_PATHS","NONE",false,false,false,false,false);destroyResourceCalibrationV82();status.setText("No actuator passed calibration; ChatGPT Resource was not touched.");
    }

    private void beginResourceAcceptanceV82(){
        if(resourceV82Finalized||"NONE".equals(resourceV82Actuator))return;resourceScanDocumentEpoch=documentEpoch;resourceScanPageFinishedEpoch=pageFinishedEpoch;
        eval(assistantLocalResourceCertifyV82Js(),o->{
            JSONObject admission=baseState();put(admission,"semantic_candidate_count",o.optInt("semantic_candidate_count",0));put(admission,"assistant_turn_count",o.optInt("assistant_turn_count",0));put(admission,"last_assistant_exists",o.optBoolean("last_assistant_exists",false));put(admission,"author_message_exists",o.optBoolean("author_message_exists",false));put(admission,"exact_unique",o.optBoolean("exact_unique",false));put(admission,"actuator",resourceV82Actuator);put(admission,"raw_url_remote",false);put(admission,"raw_text_remote",false);put(admission,"raw_html_remote",false);
            boolean epochFresh=resourceScanDocumentEpoch==documentEpoch&&resourceScanPageFinishedEpoch==pageFinishedEpoch&&pageFinishedEpoch==documentEpoch;String candidate=o.optString("candidate_token","-"),assistant=o.optString("assistant_token","-");boolean admitted=o.optBoolean("success",false)&&o.optBoolean("exact_unique",false)&&o.optInt("semantic_candidate_count",0)==1&&!"-".equals(candidate)&&!"-".equals(assistant)&&epochFresh;
            put(admission,"epoch_fresh",epochFresh);put(admission,"admitted",admitted);emit("RESOURCE_DISCOVERY",admitted?"PASS_ASSISTANT_LOCAL_RESOURCE_UNIQUE_ADMITTED":"RESOURCE_ACTION_BLOCKED_NO_UNIQUE_ASSISTANT_LOCAL_RESOURCE",admission);if(!admitted){status.setText("TEST RESOURCE blocked: no unique strong assistant-local Resource was admitted.");return;}
            resourceV82AdmissionToken=candidate;resourceV82InitialCandidateToken=candidate;resourceV82ClaimAssistantToken=assistant;resourceV82ClaimDocumentEpoch=documentEpoch;resourceV82ClaimPageFinishedEpoch=pageFinishedEpoch;
            String origin=originOfV82(web==null?null:web.getUrl());if(origin.isEmpty()){emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_UNSUPPORTED_CURRENT_ORIGIN",admission);status.setText("TEST RESOURCE blocked: unsupported page origin.");return;}resourceV82ActionOrigin=origin;
            String claimId="resource-v82-"+UUID.randomUUID();boolean committed=prefs.edit().putString("resource_v82_claim_status","CLAIMED").putString("resource_v82_claim_id",claimId).putString("resource_v82_assistant_token",assistant).commit();JSONObject pre=baseState();put(pre,"claim_committed",committed);put(pre,"actuator",resourceV82Actuator);put(pre,"assistant_bound",true);put(pre,"raw_url_remote",false);emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_RESOURCE_ACTION":"RESOURCE_ACTION_CLAIM_COMMIT_FAILED",pre);if(!committed){status.setText("TEST RESOURCE blocked: durable claim failed.");return;}
            resourceActionPendingId=claimId;resourceV82Finalized=false;resourceV82EffectDispatched=false;resourceV82PreEffectPending=true;resourceNavigationPending=false;resourceDownloadPending=false;resourceWrappedSawSameOriginNavigation=false;installResourceDownloadListenerV82();try{web.getSettings().setJavaScriptCanOpenWindowsAutomatically("JS_POPUP".equals(resourceV82Actuator));}catch(Exception ignored){}
            final long timeout=++resourceV82TimeoutSerial;resourceV82Handler.postDelayed(()->{if(!resourceV82Finalized&&resourceV82PreEffectPending&&!resourceV82EffectDispatched&&timeout==resourceV82TimeoutSerial){resourceV82Finalized=true;prefs.edit().putString("resource_v82_claim_status","PRE_EFFECT_TARGET_TIMEOUT").commit();JSONObject st=baseState();put(st,"actuator",resourceV82Actuator);put(st,"effect_dispatched",false);put(st,"raw_url_remote",false);emit("RESOURCE_ACTION","RESOURCE_ACTION_PRE_EFFECT_TARGET_TIMEOUT_NO_ACTION",st);status.setText("Resource target did not reappear before fail-closed timeout; no action was dispatched.");clearResourceV82TerminalState();}},6000L);
            driveResourceV82("AFTER_CLAIM");
        });
    }

    private void driveResourceV82OnObservedState(String reason){
        if(!resourceV82PreEffectPending||resourceV82EffectDispatched||resourceV82DriveInFlight||resourceV82Finalized)return;driveResourceV82("OBSERVED_"+hashNorm(reason));
    }

    private void driveResourceV82(String reason){
        if(!resourceV82PreEffectPending||resourceV82EffectDispatched||resourceV82DriveInFlight||resourceV82Finalized)return;if(resourceV82ClaimDocumentEpoch!=documentEpoch||resourceV82ClaimPageFinishedEpoch!=pageFinishedEpoch||pageFinishedEpoch!=documentEpoch){resourceV82Finalized=true;JSONObject st=baseState();put(st,"effect_dispatched",false);put(st,"raw_url_remote",false);emit("RESOURCE_ACTION","RESOURCE_ACTION_ABORTED_STALE_CLAIM_PRE_EFFECT",st);status.setText("Resource claim became stale before actuation.");clearResourceV82TerminalState();return;}
        resourceV82DriveInFlight=true;final String actuator=resourceV82Actuator;final boolean js="JS_POPUP".equals(actuator);eval(assistantLocalResourceFinalV82Js(resourceV82ClaimAssistantToken,js),o->{resourceV82DriveInFlight=false;if(resourceV82Finalized||resourceV82EffectDispatched||!resourceV82PreEffectPending)return;int n=o.optInt("semantic_candidate_count",0);boolean sameAssistant=o.optBoolean("same_assistant_turn",false),ready=o.optBoolean("ready",false);JSONObject st=baseState();put(st,"actuator",actuator);put(st,"semantic_candidate_count",n);put(st,"same_assistant_turn",sameAssistant);put(st,"candidate_remounted",!resourceV82InitialCandidateToken.equals(o.optString("candidate_token","-")));put(st,"drive_reason_hash",hashNorm(reason));put(st,"geometry_role",js?"NONE":"ACTUATION_TRANSPORT_ONLY");put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);
            if(!sameAssistant){resourceV82Finalized=true;emit("RESOURCE_ACTION","RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_CHANGED_PRE_EFFECT",st);status.setText("Resource transaction aborted: assistant turn changed before actuation.");clearResourceV82TerminalState();return;}
            if(n==0||!ready){emit("RESOURCE_ACTION","RESOURCE_TARGET_TRANSIENTLY_ABSENT_WAITING_EVENT",st);status.setText("Resource temporarily absent; waiting for UI feedback before any action.");return;}
            if(n!=1){resourceV82Finalized=true;emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_AMBIGUOUS_FRESH_TARGET",st);status.setText("Resource became ambiguous before actuation; no action dispatched.");clearResourceV82TerminalState();return;}
            if(js){boolean clicked=o.optBoolean("clicked",false);if(!clicked){emit("RESOURCE_ACTION","RESOURCE_TARGET_TRANSIENTLY_ABSENT_WAITING_EVENT",st);return;}resourceV82EffectDispatched=true;resourceV82PreEffectPending=false;resourceV82ClickConfirmed=true;resourceNavigationPending=true;++resourceV82TimeoutSerial;pageUiDispatches++;pageUiWrites++;emit("RESOURCE_ACTION","PASS_RESOURCE_JS_CERTIFY_AND_CLICK_SAME_TASK_WAITING_RECEIPT",st);if(!resourceV82Finalized)status.setText("Resource acted once with calibrated JS actuator; waiting for receipt.");return;}
            double cx=o.optDouble("center_x_css",Double.NaN),cy=o.optDouble("center_y_css",Double.NaN),vw=o.optDouble("viewport_w_css",Double.NaN),vh=o.optDouble("viewport_h_css",Double.NaN);if(Double.isNaN(cx)||Double.isNaN(cy)||Double.isNaN(vw)||Double.isNaN(vh)||vw<=0||vh<=0||web==null||web.getWidth()<=0||web.getHeight()<=0){resourceV82Finalized=true;emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_INVALID_CERTIFIED_GEOMETRY",st);status.setText("Certified Resource geometry unavailable; no action dispatched.");clearResourceV82TerminalState();return;}float lx=(float)(cx*web.getWidth()/vw),ly=(float)(cy*web.getHeight()/vh);
            if("ACCESSIBILITY_CLICK".equals(actuator)){int[] loc=new int[2];web.getLocationOnScreen(loc);String nonce=UUID.randomUUID().toString();JSONObject arm=ControlPlaneAccessibilityServiceV51.armV82ResourceActuation(nonce);JSONObject r=ControlPlaneAccessibilityServiceV51.performV82ResourceClickAtScreenPoint(Math.round(loc[0]+lx),Math.round(loc[1]+ly),nonce);boolean performed=arm.optBoolean("armed",false)&&r.optBoolean("performed",false);put(st,"accessibility_performed",performed);put(st,"accessibility_point_candidates",r.optInt("point_click_candidates",0));resourceV82EffectDispatched=performed;resourceV82PreEffectPending=!performed;if(!performed){emit("RESOURCE_ACTION","RESOURCE_ACTUATOR_ACCESSIBILITY_NO_EFFECT_DISPATCHED_WAITING_EVENT",st);return;}resourceNavigationPending=true;++resourceV82TimeoutSerial;pageUiDispatches++;pageUiWrites++;emit("RESOURCE_ACTION","PASS_RESOURCE_ACCESSIBILITY_ACTION_DISPATCHED_WAITING_RECEIPT",st);status.setText("Resource acted once with calibrated accessibility actuator; waiting for receipt.");return;}
            if("NATIVE_TOUCH".equals(actuator)){long now=android.os.SystemClock.uptimeMillis();android.view.MotionEvent d=android.view.MotionEvent.obtain(now,now,android.view.MotionEvent.ACTION_DOWN,lx,ly,0);android.view.MotionEvent u=android.view.MotionEvent.obtain(now,now+16L,android.view.MotionEvent.ACTION_UP,lx,ly,0);boolean down=false,up=false;try{down=web.dispatchTouchEvent(d);up=web.dispatchTouchEvent(u);}finally{d.recycle();u.recycle();}resourceV82EffectDispatched=true;resourceV82PreEffectPending=false;resourceNavigationPending=true;++resourceV82TimeoutSerial;pageUiDispatches++;pageUiWrites++;put(st,"down_dispatched",down);put(st,"up_dispatched",up);emit("RESOURCE_ACTION",down&&up?"PASS_RESOURCE_NATIVE_TOUCH_DISPATCHED_WAITING_RECEIPT":"RESOURCE_NATIVE_TOUCH_DISPATCH_UNCERTAIN_NO_REPLAY",st);if(!down||!up){resourceV82Finalized=true;prefs.edit().putString("resource_v82_claim_status","NATIVE_TOUCH_DISPATCH_UNCERTAIN_NO_REPLAY").commit();status.setText("Native touch dispatch uncertain; no replay.");clearResourceV82TerminalState();}else status.setText("Resource acted once with calibrated native-touch actuator; waiting for receipt.");return;}
            resourceV82Finalized=true;emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_NO_CALIBRATED_ACTUATOR",st);clearResourceV82TerminalState();
        });
    }

'''
s=s[:insert]+helpers+s[insert:]

start=s.index('    private String assistantLocalResourceCertifyV82Js(){\n')
end=s.index('    private String assistantLocalResourceClickV82Js(',start)
cert=r'''    private String assistantLocalResourceCertifyV82Js(){
        return "(function(){try{"+
            "const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();const H=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return ('00000000'+(h>>>0).toString(16)).slice(-8);};const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const st=getComputedStyle(e);if(st.display==='none'||st.visibility==='hidden'||st.opacity==='0')return false;try{if(typeof e.checkVisibility==='function')return e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});}catch(_){}return true;};const SIG=e=>e?H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|'))):'-';"+
            "const turnNodes=[];const seen=new Set();const addTurn=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);turnNodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(addTurn);const turns=turnNodes.map((e,i)=>{const r=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');return{el:e,role:r?String(r.getAttribute('data-message-author-role')||'-'):'-',index:i};});const assistants=turns.filter(t=>t.role==='assistant');const last=assistants.length?assistants[assistants.length-1]:null;if(!last)return JSON.stringify({success:true,last_assistant_exists:false,author_message_exists:false,assistant_turn_count:0,semantic_candidate_count:0,exact_unique:false,candidate_token:'-',assistant_token:'-'});const author=(last.el.matches&&last.el.matches('[data-message-author-role=assistant]'))?last.el:last.el.querySelector('[data-message-author-role=assistant]');if(!author)return JSON.stringify({success:true,last_assistant_exists:true,author_message_exists:false,assistant_turn_count:assistants.length,semantic_candidate_count:0,exact_unique:false,candidate_token:'-',assistant_token:'-'});const turnKey=String(last.el.getAttribute('data-turn-id')||last.el.getAttribute('data-testid')||('assistant-'+last.index));const assistantToken=H('assistant|'+turnKey+'|'+last.index);const depth=e=>{let d=0,p=e;while(p&&p!==last.el){d++;p=p.parentElement;}return d;};const good=[];for(const e of Array.from(author.querySelectorAll('a')).filter(V)){const hrefAttr=e.getAttribute('href');const noHref=hrefAttr===null||String(hrefAttr).trim()==='';const targetBlank=N(e.getAttribute('target')||'')==='_blank';const externalRel=/noopener|noreferrer|external/.test(N(e.getAttribute('rel')||''));const on=typeof e.onclick==='function'||e.hasAttribute('onclick');const st=getComputedStyle(e),ptr=N(st.cursor||'').includes('pointer'),und=N(st.textDecorationLine||st.textDecoration||'').includes('underline');const disabled=e.hasAttribute('disabled')||e.getAttribute('aria-disabled')==='true';const excluded=!!e.closest(`form,nav,aside,header,[role='navigation'],[data-testid*='composer']`);const p=e.parentElement;const parentOn=!!(p&&(typeof p.onclick==='function'||p.hasAttribute('onclick')));const parentSingle=!!(p&&p.querySelectorAll&&p.querySelectorAll('a').length===1);if(noHref&&targetBlank&&externalRel&&on&&(ptr||und)&&!disabled&&!excluded&&parentOn&&parentSingle){const token=H([SIG(e),SIG(p),depth(e),targetBlank?1:0,externalRel?1:0,on?1:0,ptr?1:0,und?1:0].join('|'));good.push({token:token});}}const unique=good.length===1;return JSON.stringify({success:true,last_assistant_exists:true,author_message_exists:true,assistant_turn_count:assistants.length,semantic_candidate_count:good.length,exact_unique:unique,candidate_token:unique?good[0].token:'-',assistant_token:assistantToken});"+
        "}catch(e){return JSON.stringify({success:false,error_class:'ASSISTANT_LOCAL_RESOURCE_CERTIFY_EXCEPTION',semantic_candidate_count:0,exact_unique:false,candidate_token:'-',assistant_token:'-'});}})()";
    }

'''
s=s[:start]+cert+s[end:]

insert=s.index('    private String assistantLocalResourceClickV82Js(')
finaljs=r'''    private String assistantLocalResourceFinalV82Js(String expectedAssistantToken,boolean jsActuate){
        return "(function(){try{const expected="+jsV79(expectedAssistantToken)+",doClick="+(jsActuate?"true":"false")+";const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();const H=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return ('00000000'+(h>>>0).toString(16)).slice(-8);};const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const st=getComputedStyle(e);if(st.display==='none'||st.visibility==='hidden'||st.opacity==='0')return false;try{if(typeof e.checkVisibility==='function')return e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});}catch(_){}return true;};const SIG=e=>e?H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|'))):'-';const nodes=[];const seen=new Set();const add=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);nodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(add);const turns=nodes.map((e,i)=>{const r=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');return{el:e,role:r?String(r.getAttribute('data-message-author-role')||'-'):'-',index:i};});const assistants=turns.filter(t=>t.role==='assistant');let target=null;for(const a of assistants){const key=String(a.el.getAttribute('data-turn-id')||a.el.getAttribute('data-testid')||('assistant-'+a.index));if(H('assistant|'+key+'|'+a.index)===expected){if(target)return JSON.stringify({success:true,same_assistant_turn:false,semantic_candidate_count:0,ready:false,clicked:false});target=a;}}if(!target)return JSON.stringify({success:true,same_assistant_turn:false,semantic_candidate_count:0,ready:false,clicked:false});const author=(target.el.matches&&target.el.matches('[data-message-author-role=assistant]'))?target.el:target.el.querySelector('[data-message-author-role=assistant]');if(!author)return JSON.stringify({success:true,same_assistant_turn:true,semantic_candidate_count:0,ready:false,clicked:false});const depth=e=>{let d=0,p=e;while(p&&p!==target.el){d++;p=p.parentElement;}return d;};const good=[];for(const e of Array.from(author.querySelectorAll('a')).filter(V)){const hrefAttr=e.getAttribute('href');const noHref=hrefAttr===null||String(hrefAttr).trim()==='';const targetBlank=N(e.getAttribute('target')||'')==='_blank';const externalRel=/noopener|noreferrer|external/.test(N(e.getAttribute('rel')||''));const on=typeof e.onclick==='function'||e.hasAttribute('onclick');const st=getComputedStyle(e),ptr=N(st.cursor||'').includes('pointer'),und=N(st.textDecorationLine||st.textDecoration||'').includes('underline');const disabled=e.hasAttribute('disabled')||e.getAttribute('aria-disabled')==='true';const excluded=!!e.closest(`form,nav,aside,header,[role='navigation'],[data-testid*='composer']`);const p=e.parentElement;const parentOn=!!(p&&(typeof p.onclick==='function'||p.hasAttribute('onclick')));const parentSingle=!!(p&&p.querySelectorAll&&p.querySelectorAll('a').length===1);if(noHref&&targetBlank&&externalRel&&on&&(ptr||und)&&!disabled&&!excluded&&parentOn&&parentSingle){const token=H([SIG(e),SIG(p),depth(e),targetBlank?1:0,externalRel?1:0,on?1:0,ptr?1:0,und?1:0].join('|'));good.push({el:e,token:token});}}if(good.length!==1)return JSON.stringify({success:true,same_assistant_turn:true,semantic_candidate_count:good.length,ready:false,clicked:false,candidate_token:'-'});const e=good[0].el,r=e.getBoundingClientRect();const ready=!!(r&&r.width>0&&r.height>0);if(!ready)return JSON.stringify({success:true,same_assistant_turn:true,semantic_candidate_count:1,ready:false,clicked:false,candidate_token:good[0].token});if(doClick){e.click();return JSON.stringify({success:true,same_assistant_turn:true,semantic_candidate_count:1,ready:true,clicked:true,candidate_token:good[0].token});}return JSON.stringify({success:true,same_assistant_turn:true,semantic_candidate_count:1,ready:true,clicked:false,candidate_token:good[0].token,center_x_css:r.left+r.width/2,center_y_css:r.top+r.height/2,viewport_w_css:window.innerWidth||document.documentElement.clientWidth||0,viewport_h_css:window.innerHeight||document.documentElement.clientHeight||0});}catch(e){return JSON.stringify({success:false,error_class:'ASSISTANT_LOCAL_RESOURCE_FINAL_EXCEPTION',same_assistant_turn:false,semantic_candidate_count:0,ready:false,clicked:false});}})()";
    }

'''
s=s[:insert]+finaljs+s[insert:]

svc=PKG/"ControlPlaneAccessibilityServiceV51.java"
ss=svc.read_text();end=ss.rfind('\n}')
assert end>0
service_add=r'''
    private static volatile String V82_RESOURCE_NONCE="-";
    private static void v82Walk(android.view.accessibility.AccessibilityNodeInfo n,int x,int y,java.util.List<android.view.accessibility.AccessibilityNodeInfo> out){if(n==null)return;try{android.graphics.Rect r=new android.graphics.Rect();n.getBoundsInScreen(r);boolean has=false;for(android.view.accessibility.AccessibilityNodeInfo.AccessibilityAction a:n.getActionList())if(a!=null&&a.getId()==android.view.accessibility.AccessibilityNodeInfo.ACTION_CLICK){has=true;break;}if((n.isClickable()||has)&&r.contains(x,y))out.add(n);}catch(Exception ignored){}for(int i=0;i<n.getChildCount();i++){android.view.accessibility.AccessibilityNodeInfo c=null;try{c=n.getChild(i);}catch(Exception ignored){}if(c!=null)v82Walk(c,x,y,out);}}
    private static boolean v82ExactLabel(android.view.accessibility.AccessibilityNodeInfo n,String label){if(n==null)return false;String t=n.getText()==null?"":n.getText().toString(),d=n.getContentDescription()==null?"":n.getContentDescription().toString();return label.equals(t)||label.equals(d);}
    private static void v82FindLabel(android.view.accessibility.AccessibilityNodeInfo n,String label,java.util.List<android.view.accessibility.AccessibilityNodeInfo> out){if(n==null)return;if(v82ExactLabel(n,label))out.add(n);for(int i=0;i<n.getChildCount();i++){android.view.accessibility.AccessibilityNodeInfo c=null;try{c=n.getChild(i);}catch(Exception ignored){}if(c!=null)v82FindLabel(c,label,out);}}
    public static synchronized org.json.JSONObject performV82CalibrationClick(String exactBenignLabel){org.json.JSONObject o=new org.json.JSONObject();put(o,"service_ready",INSTANCE51!=null);if(INSTANCE51==null){put(o,"performed",false);return o;}android.view.accessibility.AccessibilityNodeInfo root=null;try{root=INSTANCE51.getRootInActiveWindow();}catch(Exception ignored){}java.util.List<android.view.accessibility.AccessibilityNodeInfo> xs=new java.util.ArrayList<>();v82FindLabel(root,exactBenignLabel,xs);put(o,"exact_label_matches",xs.size());boolean performed=false;if(xs.size()==1){android.view.accessibility.AccessibilityNodeInfo n=xs.get(0);try{performed=n.performAction(android.view.accessibility.AccessibilityNodeInfo.ACTION_CLICK);if(!performed){android.view.accessibility.AccessibilityNodeInfo p=n.getParent();if(p!=null&&p.isClickable())performed=p.performAction(android.view.accessibility.AccessibilityNodeInfo.ACTION_CLICK);}}catch(Exception ignored){}}put(o,"performed",performed);return o;}
    public static synchronized org.json.JSONObject armV82ResourceActuation(String nonce){org.json.JSONObject o=new org.json.JSONObject();boolean ok=INSTANCE51!=null&&nonce!=null&&!nonce.isEmpty();V82_RESOURCE_NONCE=ok?nonce:"-";put(o,"service_ready",INSTANCE51!=null);put(o,"armed",ok);return o;}
    public static synchronized org.json.JSONObject performV82ResourceClickAtScreenPoint(int x,int y,String nonce){org.json.JSONObject o=new org.json.JSONObject();boolean armed=INSTANCE51!=null&&nonce!=null&&nonce.equals(V82_RESOURCE_NONCE)&&!"-".equals(V82_RESOURCE_NONCE);V82_RESOURCE_NONCE="-";put(o,"service_ready",INSTANCE51!=null);put(o,"armed",armed);if(!armed){put(o,"performed",false);return o;}android.view.accessibility.AccessibilityNodeInfo root=null;try{root=INSTANCE51.getRootInActiveWindow();}catch(Exception ignored){}java.util.List<android.view.accessibility.AccessibilityNodeInfo> xs=new java.util.ArrayList<>();v82Walk(root,x,y,xs);put(o,"point_click_candidates",xs.size());android.view.accessibility.AccessibilityNodeInfo best=null;long bestArea=Long.MAX_VALUE;int ties=0;for(android.view.accessibility.AccessibilityNodeInfo n:xs){android.graphics.Rect r=new android.graphics.Rect();try{n.getBoundsInScreen(r);}catch(Exception ignored){}long a=Math.max(0,r.width())*(long)Math.max(0,r.height());if(a<bestArea){bestArea=a;best=n;ties=1;}else if(a==bestArea)ties++;}put(o,"min_area_ties",ties);boolean performed=false;if(best!=null&&ties==1)try{performed=best.performAction(android.view.accessibility.AccessibilityNodeInfo.ACTION_CLICK);}catch(Exception ignored){}put(o,"performed",performed);return o;}
'''
ss=ss[:end]+service_add+ss[end:]
svc.write_text(ss)

ACT.write_text(s);OLD.unlink()
old_cfg=PKG/"TelemetryConfigV81.java";new_cfg=PKG/"TelemetryConfigV82.java";assert old_cfg.exists();new_cfg.write_text(old_cfg.read_text().replace("TelemetryConfigV81","TelemetryConfigV82"));old_cfg.unlink()
g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+82\b","versionCode 83",gs);gs=gs.replace("0.79-stable-diag-assistant-local-resource-acceptance","0.80-stable-diag-calibrated-actuator-resource");g.write_text(gs)
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorResourceToolsV81Activity","OrchestratorResourceToolsV82Activity");mf.write_text(ms)

out=ACT.read_text();sv=svc.read_text()
for required in ['ACTUATOR_CALIBRATION_STARTED','PASS_ACTUATOR_CALIBRATION_SELECTED','JS_POPUP','ACCESSIBILITY_CLICK','NATIVE_TOUCH','RESOURCE_TARGET_TRANSIENTLY_ABSENT_WAITING_EVENT','assistantLocalResourceFinalV82Js','resourceV82ClaimAssistantToken','PASS_RESOURCE_JS_CERTIFY_AND_CLICK_SAME_TASK_WAITING_RECEIPT','PASS_RESOURCE_ACCESSIBILITY_ACTION_DISPATCHED_WAITING_RECEIPT','PASS_RESOURCE_NATIVE_TOUCH_DISPATCHED_WAITING_RECEIPT','geometry_role','ACTUATION_TRANSPORT_ONLY','RESOURCE_ACTION_PRE_EFFECT_TARGET_TIMEOUT_NO_ACTION','CLAIMED_BEFORE_RESOURCE_ACTION','RESOURCE_NEW_WINDOW_REQUEST_OBSERVED','setJavaScriptCanOpenWindowsAutomatically','onCreateWindow','ControlPlaneAccessibilityServiceV51.performV82ResourceClickAtScreenPoint','TelemetryConfigV82']:
    assert required in out,required
for required in ['performV82CalibrationClick','armV82ResourceActuation','performV82ResourceClickAtScreenPoint','V82_RESOURCE_NONCE']:
    assert required in sv,required
for bad in ['elementFromPoint','document.evaluate','XPathResult','findElementsBy','getCookie(','CookieManager','addJavascriptInterface','Thread.sleep','ScheduledExecutorService','TimerTask']:
    assert bad not in out,bad
assert 'getBoundingClientRect' in out
assert out.count('dispatchTouchEvent(')==2,out.count('dispatchTouchEvent(')
assert out.count('.click();')>=3,out.count('.click();')
assert 'versionCode 83' in g.read_text()
assert "versionName '0.80-stable-diag-calibrated-actuator-resource'" in g.read_text()
assert 'OrchestratorResourceToolsV82Activity' in mf.read_text()
assert 'ControlPlaneAccessibilityServiceV51' in mf.read_text() and '@xml/cp_accessibility_service_v51' in mf.read_text()
print('PASS v0.80 calibrated actuator audit: benign per-device calibration, turn-bound semantic claim, event-driven pre-effect recovery, geometry transport only after exact certification')
