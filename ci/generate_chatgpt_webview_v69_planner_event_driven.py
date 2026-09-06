#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.67: replace every timer/poll-driven control transition with an event/state
# driven control plane.  Build from v0.66 to preserve the proven bounded action
# grammar, Temporary exact signatures, privacy, safe insets and signer lineage.
runpy.run_path("ci/generate_chatgpt_webview_v68_planner_temp_entry_readiness.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorPlannerCoreV68Activity.java"
ACT=PKG/"OrchestratorPlannerCoreV69Activity.java"
s=OLD.read_text()

def once(old,new,label):
    global s
    n=s.count(old)
    assert n==1,(label,n)
    s=s.replace(old,new,1)

def void_method(name,new_body):
    global s
    pat=rf'    private void {re.escape(name)}\([^\n]*\)\{{.*?\n    \}}\n\n'
    m=re.search(pat,s,re.S)
    assert m,(name,"void method not found")
    s=s[:m.start()]+new_body+s[m.end():]

def string_method(name,new_body):
    global s
    pat=rf'    private String {re.escape(name)}\([^\n]*\)\{{.*?\n    \}}\n\n'
    m=re.search(pat,s,re.S)
    assert m,(name,"String method not found")
    s=s[:m.start()]+new_body+s[m.end():]

def remove_void(name):
    global s
    pat=rf'    private void {re.escape(name)}\([^\n]*\)\{{.*?\n    \}}\n\n'
    s,n=re.subn(pat,'',s,count=1,flags=re.S)
    assert n==1,(name,"remove method not found")

# Identity.
once("OrchestratorPlannerCoreV68Activity","OrchestratorPlannerCoreV69Activity","activity")
once('SCHEMA="cp-v68-planner-core-temp-entry-readiness-v1"','SCHEMA="cp-v69-planner-core-event-driven-v1"',"schema")
once('SCENARIO="same-apk-semantic-planner-core-temp-entry-readiness"','SCENARIO="same-apk-semantic-planner-core-event-driven"',"scenario")
once('getSharedPreferences("cp_v68_planner_core",MODE_PRIVATE)','getSharedPreferences("cp_v69_planner_core",MODE_PRIVATE)',"prefs")
once('testId="cp66-"+UUID.randomUUID();','testId="cp67-"+UUID.randomUUID();',"test id")
once('status.setText("v0.66 Planner Core readiness gate ready. Puzzle is unknown at build time.\\nTemporary entry requires two stable exact NORMAL samples after document readyState is complete; no early click or replay.");','status.setText("v0.67 EVENT-DRIVEN Planner ready. Puzzle is unknown at build time.\\nNo fixed-delay/poll/timeout controls: DOM + page + receipt events alone advance automation.");',"ready")

# Imports for event bridge. Handler/Looper are removed because no timer orchestration remains.
s=s.replace('import android.os.Handler;\n','').replace('import android.os.Looper;\n','')
once('import android.graphics.Bitmap;\n','import android.graphics.Bitmap;\nimport android.net.Uri;\n',"uri import")
once('import android.webkit.WebViewClient;\n','import android.webkit.WebViewClient;\nimport android.webkit.WebMessage;\nimport android.webkit.WebMessagePort;\n',"webmessage imports")

# Remove timer/poll constants inherited from older runtime. Timestamps remain diagnostic only.
for pat in [
    r'    private static final long SAMPLE_MS=.*?;\n',
    r'    private static final int MAX_SEND_POLLS=.*?;\n',
    r'    private static final long SEND_POLL_MS=.*?;\n',
    r'    private static final int RESPONSE_STABLE_SAMPLES=.*?;\n',
    r'    private static final long RESPONSE_TIMEOUT_MS=.*?;\n',
    r'    private static final int MAX_AUTO_RESPONSE_POLLS=.*?;\n',
    r'    private static final int MAX_TEMP_POLLS=.*?;\n',
    r'    private static final int MAX_NAV_POLLS=.*?;\n',
    r'    private static final int MAX_AUTO_SEND_RECEIPT_POLLS=.*?;\n',
]:
    s=re.sub(pat,'',s)

# Remove legacy Handler and sampler loop entirely.
s=s.replace('    private final Handler h=new Handler(Looper.getMainLooper());\n','')
s=re.sub(r'    private final Runnable sampler=new Runnable\(\)\{.*?\n    \};\n\n','',s,count=1,flags=re.S)

# Event-driven fields.
once('    private WebView web;\n', '''    private WebView web;
    private WebMessagePort eventPort;
    private boolean pageFinishedReady=false;
    private boolean eventReadInFlight=false;
    private boolean eventReadDirty=false;
    private boolean plannerActionInFlight=false;
    private boolean pendingManualDraftReceipt=false;
''',"event fields")

# Replace WebViewClient with page lifecycle + WebMessagePort DOM event bridge. No delays.
old_client=re.search(r'        web\.setWebViewClient\(new WebViewClient\(\)\{.*?\n        \}\);',s,re.S)
assert old_client,"web client block"
new_client='''        web.setWebViewClient(new WebViewClient(){
            @Override public void onPageStarted(WebView v,String u,Bitmap f){
                super.onPageStarted(v,u,f); pageFinishedReady=false; closeEventBridge();
            }
            @Override public void onPageFinished(WebView v,String u){
                super.onPageFinished(v,u); pageFinishedReady=true; installEventBridge();
            }
        });'''
s=s[:old_client.start()]+new_client+s[old_client.end():]

# LEARN is now mutation/input/navigation driven. Manual SNAPSHOT remains immediate on demand.
void_method("startLearn",'''    private void startLearn(){
        if(learning||plannerRunning)return;
        clearTraceFile();
        learning=true; sampleIndex=0; traceRecords=0; telemetrySeq=0; pageUiDispatches=0; pageUiWrites=0;
        lastStateFingerprint="-"; lastAssistantHash="-"; assistantStableHits=0; lifecycle="IDLE";
        responseArmed=false; responseStarted=false;
        pendingResponseBaselineHash="-"; responseBaselineAssistantHash="-"; responseLastAssistantHash="-";
        plannerRunning=false; autoSendPending=false; plannerIteration=0; plannerActionCount=0; plannerTargetSendCount=0;
        plannerPhase="LEARN"; plannerHistory.clear(); plannerRefToPath.clear(); plannerPathToRef.clear();
        anchorPath=""; anchorHash="-"; prefs.edit().remove("anchor_path").remove("anchor_hash").commit();
        testId="cp67-"+UUID.randomUUID(); startedMs=System.currentTimeMillis();
        eval(readJs(),o->{
            maybeAutoAnchor(o); appendLocal(o,"START");
            JSONObject st=sanitizedState(o); put(st,"local_trace_cleared",true); put(st,"event_driven",true); put(st,"raw_text_remote",false);
            emit("LEARN_STARTED","RUNNING_EVENT_DRIVEN_LOCAL_READ_PLANE",st);
            status.setText("LEARN active: DOM/input/navigation events drive observation. No timer sampling. Raw text stays local.");
            renderLocal(o); lastStateFingerprint=o.optString("state_fingerprint","-");
        });
    }

''')

void_method("finishLearn",'''    private void finishLearn(){
        if(!learning){if(!plannerRunning)beginPlanner();return;}
        learning=false;
        eval(readJs(),o->{
            updateLifecycle(o); maybeAutoAnchor(o); appendLocal(o,"FINISH");
            JSONObject st=sanitizedState(o); put(st,"trace_records",traceRecords); put(st,"event_observations",sampleIndex); put(st,"blind_build_marker",BLIND_BUILD_MARKER);
            emit("LEARN_FINISHED","LOCAL_EVENT_TRACE_READY_FOR_INTERPRET",st);
            status.setText("LEARN finished. Entering INTERPRET immediately from this state receipt; no clock delay.");
            renderLocal(o); beginPlanner();
        });
    }

''')

void_method("sample",'''    private void sample(boolean explicit){
        if(web==null)return;
        eval(readJs(),o->{
            updateLifecycle(o); int n=++sampleIndex;
            if(learning)appendLocal(o,explicit?"EXPLICIT_SNAPSHOT":"MANUAL_SAMPLE");
            JSONObject st=sanitizedState(o); put(st,"event_observation_index",n); put(st,"explicit",explicit);
            emit("RUNTIME_SNAPSHOT",explicit?"LOCAL_EXPLICIT_SNAPSHOT":"LOCAL_MANUAL_SNAPSHOT",st);
            lastStateFingerprint=o.optString("state_fingerprint","-"); renderLocal(o);
        });
    }

''')

# Return receipt is checked from an actual page/DOM event, never after a delay.
void_method("verifyReturnReceipt",'''    private void verifyReturnReceipt(){
        if(!returnPending)return;
        eval(readJs(),o->{
            if(!returnPending)return;
            boolean ok=pageFinishedReady&&anchorPath.equals(o.optString("local_path",""))&&"CONVERSATION".equals(o.optString("route_class",""));
            if(!ok)return;
            JSONObject st=sanitizedState(o); put(st,"anchor_hash",anchorHash);
            emit("RETURN_RECEIPT","PASS_LOCAL_ANCHOR_RETURN_RECEIPT",st);
            prefs.edit().putString("claim_status","RETURN_RECEIPT_CONFIRMED").commit(); returnPending=false;
            status.setText("Returned to anchored chat; event-driven route receipt confirmed.");
        });
    }

''')

# Manual composer write: dispatch then await the DOM/input event state. No delayed re-read.
void_method("setDraft",'''    private void setDraft(){
        if(sendPending||pendingManualDraftReceipt)return;
        final String text=draftInput.getText().toString();
        if(text.trim().isEmpty()){status.setText("SET DRAFT blocked: local draft is empty.");return;}
        final String expectedHash=hashNorm(text);
        String claimId="draft-"+UUID.randomUUID();
        boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","SET_DRAFT")
                .putString("claim_payload_hash",expectedHash).putString("claim_status","CLAIMED_BEFORE_COMPOSER_WRITE").commit();
        JSONObject claim=baseState(); put(claim,"draft_hash",expectedHash); put(claim,"claim_committed",committed);
        emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_COMPOSER_WRITE":"CLAIM_COMMIT_FAILED_NO_WRITE",claim);
        if(!committed)return;
        eval(setDraftJs(text),o->{
            boolean dispatched=o.optBoolean("success",false)&&o.optBoolean("mutated",false)&&o.optInt("composer_count",0)==1&&expectedHash.equals(o.optString("composer_hash",""));
            if(dispatched){pageUiDispatches++;pageUiWrites++;pendingDraftHash=expectedHash;pendingManualDraftReceipt=true;}
            JSONObject st=sanitizedAction(o);put(st,"expected_hash",expectedHash);
            emit("COMPOSER_WRITE_DISPATCH",dispatched?"PASS_SINGLE_COMPOSER_WRITE_DISPATCHED":"COMPOSER_WRITE_UNCERTAIN_NO_REPLAY",st);
            if(!dispatched){prefs.edit().putString("claim_status","COMPOSER_WRITE_UNCERTAIN_NO_REPLAY").commit();status.setText("Composer write uncertain. No replay.");return;}
            status.setText("Draft dispatched. Waiting for DOM/input receipt event; no timer and no replay.");
            requestEventRead("MANUAL_DRAFT_DISPATCH");
        });
    }

''')

# Manual Send: click once, then state events prove user-turn receipt.
void_method("sendCurrentDraft",'''    private void sendCurrentDraft(){
        if(sendPending)return;
        eval(readJs(),o->{
            int cc=o.optInt("composer_candidate_count",0),chars=o.optInt("composer_chars",0),sc=o.optInt("send_candidate_count",0);String ch=o.optString("composer_hash","-");
            if(cc!=1||chars<=0||sc!=1||"-".equals(ch)){emit("SEND_GATE","SEND_GATE_NOT_EXACT_ZERO_WRITE",sanitizedState(o));status.setText("SEND blocked: exact semantic gate not met.");return;}
            pendingSendHash=ch; pendingResponseBaselineHash=o.optString("last_assistant_hash","-");
            String claimId="send-"+UUID.randomUUID();
            boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","SEND").putString("claim_payload_hash",pendingSendHash).putString("claim_status","CLAIMED_BEFORE_SEND_CLICK").commit();
            JSONObject claim=sanitizedState(o);put(claim,"payload_hash",pendingSendHash);put(claim,"claim_committed",committed);emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_SEND_CLICK":"CLAIM_COMMIT_FAILED_NO_CLICK",claim);
            if(!committed)return;sendPending=true;
            eval(sendJs(pendingSendHash),a->{
                boolean dispatched=a.optBoolean("success",false)&&a.optBoolean("dispatched",false)&&a.optBoolean("click_observed",false)&&a.optInt("send_match_count",0)==1&&pendingSendHash.equals(a.optString("composer_hash",""));
                if(dispatched){pageUiDispatches++;pageUiWrites++;}
                emit("SEND_CLICK_DISPATCH",dispatched?"PASS_EXACT_SEND_CLICK_DISPATCHED":"SEND_CLICK_UNCERTAIN_NO_REPLAY",sanitizedAction(a));
                if(!dispatched){sendPending=false;prefs.edit().putString("claim_status","SEND_CLICK_UNCERTAIN_NO_REPLAY").commit();return;}
                status.setText("Send dispatched once. Waiting for event-driven user-turn receipt; no replay.");requestEventRead("MANUAL_SEND_DISPATCH");
            });
        });
    }

''')
remove_void("pollSendReceipt")

# Lifecycle completion is structural/event driven: the completion action on the
# latest assistant turn is the final receipt. No hash-stability clock.
void_method("updateLifecycle",'''    private void updateLifecycle(JSONObject o){
        String ah=o.optString("last_assistant_hash","-");int finalSignals=o.optInt("assistant_completion_candidate_count",0);
        if(responseArmed){
            boolean diverged=!"-".equals(ah)&&!ah.equals(responseBaselineAssistantHash);
            if(!responseStarted){
                if(diverged){responseStarted=true;responseLastAssistantHash=ah;transitionLifecycle("STREAMING","PASS_RESPONSE_STREAMING_STARTED_BY_ASSISTANT_DIVERGENCE",o);}
                else transitionLifecycle("SENT_AWAITING_ASSISTANT","RESPONSE_WAITING_FOR_NEW_ASSISTANT_OUTPUT",o);
            }
            if(responseStarted&&diverged){
                responseLastAssistantHash=ah;
                if(finalSignals==1){transitionLifecycle("COMPLETE","PASS_RESPONSE_COMPLETE_BY_ASSISTANT_ACTION_RECEIPT",o);responseArmed=false;}
                else transitionLifecycle("STREAMING","RESPONSE_STREAMING_ACTIVE_BY_DOM_EVENTS",o);
            }
            lastAssistantHash=ah;return;
        }
        if(!"-".equals(ah))lifecycle=finalSignals==1?"COMPLETE":"ASSISTANT_PRESENT_UNSTABLE";else lifecycle="IDLE";
        lastAssistantHash=ah;
    }

''')

# Arm without a timeout clock.
void_method("armResponseTransaction",'''    private void armResponseTransaction(JSONObject o){
        responseArmed=true;responseStarted=false;responseBaselineAssistantHash=pendingResponseBaselineHash==null?"-":pendingResponseBaselineHash;responseLastAssistantHash="-";
        transitionLifecycle("SENT_AWAITING_ASSISTANT","PASS_RESPONSE_TRANSACTION_ARMED_AFTER_SEND_RECEIPT",o);updateLifecycle(o);
    }

''')

# Planner starts immediately from FINISH receipt.
void_method("beginPlanner",'''    private void beginPlanner(){
        if(learning||plannerRunning)return;
        if(anchorPath==null||!anchorPath.matches("^/c/[^/?#]+$")){plannerFail("PLANNER_BLOCKED_NO_PERSISTENT_MAIN_ANCHOR");return;}
        plannerRunning=true;autoSendPending=false;plannerActionInFlight=false;plannerIteration=0;plannerActionCount=0;plannerTargetSendCount=0;plannerHistory.clear();plannerPhase="INTERPRET_START";
        JSONObject st=baseState();put(st,"anchor_hash",anchorHash);put(st,"blind_build_marker",BLIND_BUILD_MARKER);put(st,"event_driven",true);emit("PLANNER_STARTED","INTERPRET_STARTED_EVENT_DRIVEN_BLIND_GENERIC_PLANNER",st);
        status.setText("INTERPRET active. Event/state receipts alone drive the Planner.");openFreshPlannerTemp();
    }

''')

void_method("openFreshPlannerTemp",'''    private void openFreshPlannerTemp(){
        if(!plannerRunning)return;if(plannerIteration>=MAX_PLANNER_ITERATIONS){plannerFail("PLANNER_MAX_ITERATIONS_REACHED");return;}
        plannerPhase="NAVIGATE_HOME_FOR_FRESH_TEMP";plannerActionInFlight=true;
        String claimId="planner-home-"+UUID.randomUUID();boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","PLANNER_HOME_NAV").putString("claim_status","CLAIMED_BEFORE_PLANNER_HOME_NAV").commit();
        JSONObject st=baseState();put(st,"claim_committed",committed);put(st,"planner_iteration",plannerIteration);emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_PLANNER_HOME_NAVIGATION":"CLAIM_COMMIT_FAILED_NO_NAVIGATION",st);
        if(!committed){plannerActionInFlight=false;plannerFail("PLANNER_HOME_CLAIM_COMMIT_FAILED");return;}
        pageUiDispatches++;pageUiWrites++;pageFinishedReady=false;web.loadUrl("https://chatgpt.com/");
        plannerActionInFlight=false;
    }

''')
remove_void("pollPlannerNormalHome")
remove_void("pollPlannerTempReceipt")

# Temporary click stays exactly-once; transition receipt comes from subsequent DOM event.
void_method("plannerEnterFreshTemp",'''    private void plannerEnterFreshTemp(JSONObject gate){
        if(!plannerRunning||plannerActionInFlight)return;plannerActionInFlight=true;plannerPhase="TEMP_ENTRY_DISPATCH_IN_FLIGHT";
        String claimId="planner-temp-"+UUID.randomUUID();boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","PLANNER_TEMP_ENTRY").putString("claim_status","CLAIMED_BEFORE_PLANNER_TEMP_ENTRY").commit();
        JSONObject st=sanitizedState(gate);put(st,"claim_committed",committed);emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_PLANNER_TEMP_ENTRY_CLICK":"CLAIM_COMMIT_FAILED_NO_CLICK",st);
        if(!committed){plannerActionInFlight=false;plannerFail("PLANNER_TEMP_ENTRY_CLAIM_FAILED");return;}
        eval(tempClickJs("NORMAL"),a->{
            boolean sent=a.optBoolean("success",false)&&a.optBoolean("dispatched",false)&&a.optBoolean("click_observed",false)&&a.optInt("match_count",0)==1;
            if(sent){pageUiDispatches++;pageUiWrites++;}emit("PLANNER_TEMP_ENTRY_DISPATCH",sent?"PASS_EXACT_PLANNER_TEMP_ENTRY_CLICK_DISPATCHED":"PLANNER_TEMP_ENTRY_UNCERTAIN_NO_REPLAY",sanitizedTempAction(a));
            plannerActionInFlight=false;if(!sent){plannerFail("PLANNER_TEMP_ENTRY_UNCERTAIN_NO_REPLAY");return;}plannerPhase="WAIT_TEMP_ENTRY_RECEIPT";requestEventRead("TEMP_ENTRY_DISPATCH");
        });
    }

''')

# Auto composer/send dispatch; every receipt is later driven by an event snapshot.
void_method("autoWriteAndSend",'''    private void autoWriteAndSend(String text,String purpose){
        if(!plannerRunning||autoSendPending||plannerActionInFlight)return;if(text==null||text.trim().isEmpty()){plannerFail("AUTO_SEND_EMPTY_TEXT_BLOCKED");return;}if("TARGET_MESSAGE".equals(purpose)&&text.length()>MAX_PLANNER_SEND_CHARS){plannerFail("PLANNER_TARGET_SEND_TOO_LONG");return;}
        autoSendPending=true;autoSendPurpose=purpose;autoSendText=text;autoSendExpectedHash=hashNorm(text);plannerActionInFlight=true;
        String claimId="auto-draft-"+UUID.randomUUID();boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","AUTO_SET_DRAFT_"+purpose).putString("claim_payload_hash",autoSendExpectedHash).putString("claim_status","CLAIMED_BEFORE_AUTO_COMPOSER_WRITE").commit();
        JSONObject claim=baseState();put(claim,"purpose",purpose);put(claim,"payload_hash",autoSendExpectedHash);put(claim,"payload_chars",text.length());put(claim,"claim_committed",committed);emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_AUTO_COMPOSER_WRITE":"CLAIM_COMMIT_FAILED_NO_WRITE",claim);
        if(!committed){plannerActionInFlight=false;autoSendPending=false;plannerFail("AUTO_COMPOSER_CLAIM_FAILED");return;}
        eval(setDraftJs(text),o->{
            boolean dispatched=o.optBoolean("success",false)&&o.optBoolean("mutated",false)&&o.optInt("composer_count",0)==1&&autoSendExpectedHash.equals(o.optString("composer_hash",""));if(dispatched){pageUiDispatches++;pageUiWrites++;}
            JSONObject st=sanitizedAction(o);put(st,"purpose",purpose);put(st,"expected_hash",autoSendExpectedHash);emit("AUTO_COMPOSER_WRITE",dispatched?"PASS_AUTO_SINGLE_COMPOSER_WRITE_DISPATCHED":"AUTO_COMPOSER_WRITE_UNCERTAIN_NO_REPLAY",st);
            plannerActionInFlight=false;if(!dispatched){autoSendPending=false;plannerFail("AUTO_COMPOSER_WRITE_UNCERTAIN_NO_REPLAY");return;}pendingResponseBaselineHash=o.optString("last_assistant_hash",pendingResponseBaselineHash);plannerPhase="WAIT_AUTO_COMPOSER_RECEIPT";requestEventRead("AUTO_COMPOSER_DISPATCH");
        });
    }

''')
remove_void("pollAutoComposerReceipt")

void_method("claimAutoSendClick",'''    private void claimAutoSendClick(JSONObject o){
        if(!plannerRunning||!autoSendPending||plannerActionInFlight)return;int cc=o.optInt("composer_candidate_count",0),chars=o.optInt("composer_chars",0),sc=o.optInt("send_candidate_count",0);
        if(cc!=1||chars<=0||sc!=1||!autoSendExpectedHash.equals(o.optString("composer_hash",""))){autoSendPending=false;plannerFail("AUTO_SEND_GATE_NOT_EXACT_ZERO_CLICK");return;}
        pendingResponseBaselineHash=o.optString("last_assistant_hash","-");autoSendBaselineUserHash=o.optString("last_user_hash","-");pendingSendHash=autoSendExpectedHash;plannerActionInFlight=true;
        String claimId="auto-send-"+UUID.randomUUID();boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","AUTO_SEND_"+autoSendPurpose).putString("claim_payload_hash",autoSendExpectedHash).putString("claim_status","CLAIMED_BEFORE_AUTO_SEND_CLICK").commit();
        JSONObject claim=sanitizedState(o);put(claim,"purpose",autoSendPurpose);put(claim,"payload_hash",autoSendExpectedHash);put(claim,"claim_committed",committed);emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_AUTO_SEND_CLICK":"CLAIM_COMMIT_FAILED_NO_CLICK",claim);
        if(!committed){plannerActionInFlight=false;autoSendPending=false;plannerFail("AUTO_SEND_CLAIM_FAILED");return;}
        eval(sendJs(autoSendExpectedHash),a->{
            boolean dispatched=a.optBoolean("success",false)&&a.optBoolean("dispatched",false)&&a.optBoolean("click_observed",false)&&a.optInt("send_match_count",0)==1&&autoSendExpectedHash.equals(a.optString("composer_hash",""));if(dispatched){pageUiDispatches++;pageUiWrites++;}
            JSONObject st=sanitizedAction(a);put(st,"purpose",autoSendPurpose);put(st,"payload_hash",autoSendExpectedHash);emit("AUTO_SEND_DISPATCH",dispatched?"PASS_AUTO_EXACT_SEND_CLICK_DISPATCHED":"AUTO_SEND_CLICK_UNCERTAIN_NO_REPLAY",st);
            plannerActionInFlight=false;if(!dispatched){autoSendPending=false;plannerFail("AUTO_SEND_CLICK_UNCERTAIN_NO_REPLAY");return;}plannerPhase="WAIT_AUTO_SEND_RECEIPT";requestEventRead("AUTO_SEND_DISPATCH");
        });
    }

''')
remove_void("pollAutoSendReceipt")
remove_void("pollAutoResponse")

# Navigation receipt is onPageFinished + exact DOM route, not a delayed poll.
void_method("navigatePlannerRef",'''    private void navigatePlannerRef(String ref,String after,String text){
        if(!plannerRunning||plannerActionInFlight)return;buildPlannerContext();String path=plannerRefToPath.get(ref);if(path==null||!path.matches("^/c/[^/?#]+$")){plannerFail("PLANNER_CHAT_REF_NOT_AVAILABLE");return;}
        plannerNavRef=ref;plannerNavPath=path;plannerAfterNav=after;plannerPendingTargetText=text;
        eval(readJs(),o->{
            boolean already=path.equals(o.optString("local_path",""))&&"CONVERSATION".equals(o.optString("route_class",""));if(already){afterPlannerNavigation(o);return;}
            String claimId="planner-nav-"+UUID.randomUUID();boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","PLANNER_CHAT_NAV").putString("claim_anchor_hash",hashNorm(path)).putString("claim_status","CLAIMED_BEFORE_PLANNER_CHAT_NAV").commit();JSONObject st=sanitizedState(o);put(st,"planner_target_ref",ref);put(st,"claim_committed",committed);emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_PLANNER_CHAT_NAVIGATION":"CLAIM_COMMIT_FAILED_NO_NAVIGATION",st);if(!committed){plannerFail("PLANNER_CHAT_NAV_CLAIM_FAILED");return;}
            pageUiDispatches++;pageUiWrites++;plannerPhase="WAIT_PLANNER_NAV_RECEIPT";pageFinishedReady=false;web.loadUrl("https://chatgpt.com"+path);
        });
    }

''')
remove_void("pollPlannerNavReceipt")

# New event/state driver methods inserted before clearLocal().
insert=r'''    private void closeEventBridge(){
        try{if(eventPort!=null)eventPort.close();}catch(Exception ignored){}eventPort=null;eventReadInFlight=false;eventReadDirty=false;
    }

    private void installEventBridge(){
        if(web==null)return;closeEventBridge();
        eval(eventBootstrapJs(),o->{
            if(!o.optBoolean("success",false)){emit("EVENT_BRIDGE","EVENT_BRIDGE_BOOTSTRAP_FAILED",sanitizedState(o));return;}
            try{
                WebMessagePort[] ports=web.createWebMessageChannel();eventPort=ports[0];
                eventPort.setWebMessageCallback(new WebMessagePort.WebMessageCallback(){
                    @Override public void onMessage(WebMessagePort port,WebMessage message){requestEventRead("DOM_EVENT");}
                });
                web.postWebMessage(new WebMessage("CP_CONNECT",new WebMessagePort[]{ports[1]}),Uri.parse("https://chatgpt.com"));
                JSONObject st=baseState();put(st,"event_bridge_connected",true);emit("EVENT_BRIDGE","PASS_EVENT_BRIDGE_CHANNEL_CONNECTED",st);
            }catch(Exception e){JSONObject st=baseState();put(st,"event_bridge_connected",false);emit("EVENT_BRIDGE","EVENT_BRIDGE_CHANNEL_FAILED",st);}
        });
    }

    private void requestEventRead(String reason){
        if(web==null)return;if(eventReadInFlight){eventReadDirty=true;return;}eventReadInFlight=true;
        eval(readJs(),o->{
            eventReadInFlight=false;onObservedState(o,reason);
            if(eventReadDirty){eventReadDirty=false;requestEventRead("COALESCED_DOM_EVENT");}
        });
    }

    private void onObservedState(JSONObject o,String reason){
        if(!o.optBoolean("success",false))return;int n=++sampleIndex;updateLifecycle(o);String fp=o.optString("state_fingerprint","-");boolean changed=!fp.equals(lastStateFingerprint);
        if(learning&&changed){maybeAutoAnchor(o);appendLocal(o,"EVENT:"+reason);}
        if(changed){JSONObject st=sanitizedState(o);put(st,"event_observation_index",n);put(st,"event_reason_hash",hashNorm(reason));emit("RUNTIME_EVENT","LOCAL_STATE_CHANGED_BY_EVENT",st);}lastStateFingerprint=fp;renderLocal(o);
        if(returnPending&&pageFinishedReady)verifyReturnReceiptFromState(o);
        if(pendingManualDraftReceipt&&pendingDraftHash.equals(o.optString("composer_hash",""))&&o.optInt("composer_candidate_count",0)==1){pendingManualDraftReceipt=false;prefs.edit().putString("claim_status","COMPOSER_WRITE_RECEIPT_CONFIRMED").commit();emit("COMPOSER_WRITE_RECEIPT","PASS_COMPOSER_HASH_RECEIPT",sanitizedState(o));}
        if(sendPending){boolean exact=pendingSendHash.equals(o.optString("last_user_hash",""))&&o.optInt("composer_chars",-1)==0;if(exact){sendPending=false;prefs.edit().putString("claim_status","SEND_RECEIPT_CONFIRMED").commit();emit("SEND_RECEIPT","PASS_EXACT_USER_TURN_EVENT_RECEIPT",sanitizedState(o));armResponseTransaction(o);}}
        if(plannerRunning)drivePlannerFromState(o);
    }

    private void verifyReturnReceiptFromState(JSONObject o){
        boolean ok=anchorPath.equals(o.optString("local_path",""))&&"CONVERSATION".equals(o.optString("route_class",""));if(!ok)return;JSONObject st=sanitizedState(o);put(st,"anchor_hash",anchorHash);emit("RETURN_RECEIPT","PASS_LOCAL_ANCHOR_RETURN_RECEIPT",st);prefs.edit().putString("claim_status","RETURN_RECEIPT_CONFIRMED").commit();returnPending=false;
    }

    private void drivePlannerFromState(JSONObject o){
        if(!plannerRunning||plannerActionInFlight)return;
        if("NAVIGATE_HOME_FOR_FRESH_TEMP".equals(plannerPhase)){
            boolean gate=pageFinishedReady&&"complete".equals(o.optString("ready",""))&&"HOME".equals(o.optString("route_class",""))&&"NORMAL".equals(o.optString("semantic_temp_state",""))&&o.optInt("temp_candidate_count",0)==1;
            if(gate){emit("PLANNER_TEMP_GATE","PASS_PAGE_FINISHED_PLUS_EXACT_NORMAL_TEMP_ENTRY_GATE",sanitizedState(o));plannerEnterFreshTemp(o);}return;
        }
        if("WAIT_TEMP_ENTRY_RECEIPT".equals(plannerPhase)){
            boolean temp="TEMP".equals(o.optString("semantic_temp_state",""))&&o.optInt("temp_candidate_count",0)==1&&o.optBoolean("temporary_hint",false);if(temp){emit("PLANNER_TEMP_RECEIPT","PASS_FRESH_TEMP_ROOM_EVENT_RECEIPT",sanitizedState(o));plannerPhase="SEND_PLANNER_PACKET";String packet=buildPlannerPrompt();if(packet==null||packet.length()==0||packet.length()>MAX_PLANNER_PROMPT_CHARS){plannerFail("PLANNER_PACKET_SIZE_INVALID");return;}autoWriteAndSend(packet,"PLANNER_PROMPT");}return;
        }
        if("WAIT_AUTO_COMPOSER_RECEIPT".equals(plannerPhase)){
            boolean receipt=o.optInt("composer_candidate_count",0)==1&&autoSendExpectedHash.equals(o.optString("composer_hash",""));if(receipt){emit("AUTO_COMPOSER_RECEIPT","PASS_AUTO_COMPOSER_HASH_EVENT_RECEIPT",sanitizedState(o));claimAutoSendClick(o);}return;
        }
        if("WAIT_AUTO_SEND_RECEIPT".equals(plannerPhase)){
            String observedUser=o.optString("last_user_hash","-"),observedAssistant=o.optString("last_assistant_hash","-");boolean cleared=o.optInt("composer_chars",-1)==0;boolean exact=cleared&&autoSendExpectedHash.equals(observedUser);boolean assistantDiverged=!"-".equals(observedAssistant)&&!observedAssistant.equals(pendingResponseBaselineHash);boolean userAdvanced=!"-".equals(observedUser)&&!observedUser.equals(autoSendBaselineUserHash);boolean freshTemp="PLANNER_PROMPT".equals(autoSendPurpose)&&"-".equals(pendingResponseBaselineHash)&&o.optBoolean("temporary_hint",false);boolean correlated=cleared&&assistantDiverged&&(freshTemp||userAdvanced);
            if(exact||correlated){String basis=exact?"EXACT_USER_HASH_EVENT":(freshTemp?"FRESH_TEMP_ASSISTANT_EVENT":"USER_ADVANCE_PLUS_ASSISTANT_EVENT");JSONObject st=sanitizedState(o);put(st,"receipt_basis",basis);emit("AUTO_SEND_RECEIPT",exact?"PASS_AUTO_EXACT_USER_TURN_EVENT_RECEIPT":"PASS_RESPONSE_CORRELATED_AUTO_SEND_EVENT_RECEIPT",st);prefs.edit().putString("claim_status","AUTO_SEND_RECEIPT_CONFIRMED_"+basis).commit();armResponseTransaction(o);plannerPhase="PLANNER_PROMPT".equals(autoSendPurpose)?"WAIT_PLANNER_RESPONSE":"WAIT_TARGET_RESPONSE";driveAutoResponseFromState(o);}return;
        }
        if("WAIT_PLANNER_RESPONSE".equals(plannerPhase)||"WAIT_TARGET_RESPONSE".equals(plannerPhase)){driveAutoResponseFromState(o);return;}
        if("WAIT_PLANNER_NAV_RECEIPT".equals(plannerPhase)){
            boolean ok=pageFinishedReady&&plannerNavPath.equals(o.optString("local_path",""))&&"CONVERSATION".equals(o.optString("route_class",""));if(ok){emit("PLANNER_NAV_RECEIPT","PASS_PLANNER_CHAT_NAVIGATION_EVENT_RECEIPT",sanitizedState(o));afterPlannerNavigation(o);}return;
        }
    }

    private void driveAutoResponseFromState(JSONObject o){
        updateLifecycle(o);boolean complete=!responseArmed&&responseStarted&&"COMPLETE".equals(lifecycle)&&o.optInt("assistant_completion_candidate_count",0)==1;if(!complete)return;String purpose=autoSendPurpose;autoSendPending=false;emit("AUTO_RESPONSE_RECEIPT","PLANNER_PROMPT".equals(purpose)?"PASS_PLANNER_RESPONSE_COMPLETE_BY_ACTION_RECEIPT":"PASS_TARGET_RESPONSE_COMPLETE_BY_ACTION_RECEIPT",sanitizedState(o));if("PLANNER_PROMPT".equals(purpose)){handlePlannerResponse(o);return;}if("TARGET_MESSAGE".equals(purpose)){plannerTargetSendCount++;recordPlannerObservation(o,"TARGET_RESPONSE_COMPLETE");plannerIteration++;openFreshPlannerTemp();return;}plannerFail("AUTO_RESPONSE_UNKNOWN_PURPOSE");
    }

'''
marker='    private void clearLocal(){\n'
assert s.count(marker)==1
s=s.replace(marker,insert+marker,1)

# readJs now includes exact Temporary semantic state and a structural completion
# receipt scoped to the latest assistant turn.
string_method("readJs",r'''    private String readJs(){
        return "(function(){try{"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();const V=e=>{if(!e)return false;const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const RC=()=>{const p=location.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';if(/^\\/g\\//.test(p))return 'GPT_ROUTE';if(/^\\/project/.test(p))return 'PROJECT_ROUTE';return 'OTHER_ROUTE';};const txt=e=>{if(!e)return '';if('value' in e&&typeof e.value==='string')return e.value;return e.innerText||e.textContent||'';};const DS=e=>{const v=N(e.getAttribute('data-state'));if(['active','selected','checked','on'].includes(v))return 'ACTIVE';if(['inactive','unselected','unchecked','off'].includes(v))return 'INACTIVE';if(v==='open')return 'OPEN';if(v==='closed')return 'CLOSED';return v?'OTHER':'NONE';};"+
            "const C=Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).filter(e=>V(e)&&!e.hasAttribute('disabled')),c=C.length===1?C[0]:null,ct=c?txt(c):'';const B=Array.from(document.querySelectorAll('button,[role=button]')).filter(V);let S=[],P=[];for(const e of B){const z=N((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('title')||'')+' '+(e.getAttribute('data-testid')||'')+' '+(e.textContent||''));if(!e.hasAttribute('disabled')&&(z==='send'||z.includes('send message')||z.includes('composer-submit')||z.includes('send-button')||z.includes('submit prompt')))S.push(e);if(z.includes('stop generating')||z.includes('stop streaming')||z==='stop')P.push(e);}"+
            "let T=[],assistantEls=[];for(const e of Array.from(document.querySelectorAll('[data-message-author-role]'))){const role=N(e.getAttribute('data-message-author-role'));if(role!=='user'&&role!=='assistant')continue;const text=(e.innerText||e.textContent||'').replace(/\\s+$/,'').trim();if(!text)continue;T.push({role:role,text:text,hash:H(N(text)),chars:text.length});if(role==='assistant')assistantEls.push(e);}const U=T.filter(x=>x.role==='user'),A=T.filter(x=>x.role==='assistant'),lu=U.length?U[U.length-1]:null,la=A.length?A[A.length-1]:null;"+
            "let finalCount=0,finalStruct='-';if(assistantEls.length){const ae=assistantEls[assistantEls.length-1],root=ae.closest('article[data-turn],article[data-testid^=conversation-turn],article[id^=conversation-turn],[data-testid^=conversation-turn]')||ae;const F=Array.from(root.querySelectorAll('button[data-testid=copy-turn-action-button]')).filter(e=>V(e)&&!e.hasAttribute('disabled'));finalCount=F.length;if(F.length===1)finalStruct=H([(F[0].tagName||'').toLowerCase(),N(F[0].getAttribute('data-testid')||''),N(F[0].getAttribute('aria-label')||'')].join('|'));}"+
            "const SEM=(label,tid)=>{const x=N(label),t=N(tid),z=x+' '+t;if(z.includes('temporary')||x==='temp'||t.includes('temp'))return 'TEMP';return 'OTHER';};const q=Array.from(document.querySelectorAll('button,a,[role],[aria-selected],[aria-pressed],[data-state],[data-testid]')).filter(V),TT=[];for(const e of q){const tag=(e.tagName||'').toLowerCase(),role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none')),label=e.getAttribute('aria-label')||e.innerText||e.textContent||'',tid=e.getAttribute('data-testid')||'',sem=SEM(label,tid);if(sem!=='TEMP')continue;const lh=H(N(label)),th=H(tid),hc=(e.getAttribute('href')||'')?'OTHER':'NONE',sh=H([tag,role,sem,lh,th,hc].join('|'));TT.push({tag:tag,role:role,lh:lh,th:th,ds:DS(e),sel:e.getAttribute('aria-selected')==='true'?1:0,prs:e.getAttribute('aria-pressed')==='true'?1:0,exp:e.getAttribute('aria-expanded')==='true'?1:0,dis:e.hasAttribute('disabled')?1:0,hc:hc,sh:sh});}const urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));const E=TT.filter(x=>urlhint?(x.lh==='ae0e16e6'&&x.sh==='34d052a8'):(x.lh==='1a957a52'&&x.sh==='b9c97d1e')),tc=E.length===1?E[0]:null;let semState='UNKNOWN';if(tc&&tc.tag==='button'&&tc.role==='button'&&tc.th==='811c9dc5'&&tc.ds==='NONE'&&tc.sel===0&&tc.prs===0&&tc.exp===0&&tc.dis===0&&tc.hc==='NONE'){if(tc.lh==='1a957a52'&&tc.sh==='b9c97d1e'&&!urlhint)semState='NORMAL';else if(tc.lh==='ae0e16e6'&&tc.sh==='34d052a8'&&urlhint)semState='TEMP';}"+
            "const path=location.pathname||'/',sh=S.length===1?H([S[0].tagName.toLowerCase(),N(S[0].getAttribute('role')||'button'),N(S[0].getAttribute('data-testid')||''),N(S[0].getAttribute('aria-label')||'')].join('|')):'-',rows=T.map(x=>x.role+'|'+x.hash).join('~'),fp=H([RC(),H(path),H(N(ct)),S.length,P.length,finalCount,semState,rows].join('|'));return JSON.stringify({success:true,ready:document.readyState,route_class:RC(),local_path:path,local_path_hash:H(path),temporary_hint:urlhint,semantic_temp_state:semState,temp_candidate_count:E.length,turn_count:T.length,turns:T,last_user_text:lu?lu.text:'',last_user_hash:lu?lu.hash:'-',last_assistant_text:la?la.text:'',last_assistant_hash:la?la.hash:'-',assistant_completion_candidate_count:finalCount,assistant_completion_struct_hash:finalStruct,composer_candidate_count:C.length,composer_text:ct,composer_hash:c?H(N(ct)):'-',composer_chars:ct.length,send_candidate_count:S.length,send_struct_hash:sh,stop_candidate_count:P.length,state_fingerprint:fp});"+
            "}catch(e){return JSON.stringify({success:false,error_class:'READ_EXCEPTION'});}})();";
    }

''')

# Bootstrap contains no timers. Mutation/input/history events notify Android; Android
# then performs a fresh semantic read and coalesces concurrent event notifications.
new_event_method=r'''    private String eventBootstrapJs(){
        return "(function(){try{if(window.__cpEventBootstrapInstalled)return JSON.stringify({success:true,installed:true});window.__cpEventBootstrapInstalled=true;window.addEventListener('message',function(ev){try{if(ev.data!=='CP_CONNECT'||!ev.ports||!ev.ports[0])return;const p=ev.ports[0];window.__cpEventPort=p;const fire=()=>{try{p.postMessage('DOM');}catch(e){}};const mo=new MutationObserver(fire);mo.observe(document.documentElement,{subtree:true,childList:true,attributes:true,characterData:true});document.addEventListener('input',fire,true);document.addEventListener('change',fire,true);document.addEventListener('click',fire,true);window.addEventListener('popstate',fire,true);const hp=history.pushState.bind(history),hr=history.replaceState.bind(history);history.pushState=function(){const r=hp.apply(history,arguments);fire();return r;};history.replaceState=function(){const r=hr.apply(history,arguments);fire();return r;};fire();}catch(e){}},false);return JSON.stringify({success:true,installed:true});}catch(e){return JSON.stringify({success:false,error_class:'EVENT_BOOTSTRAP_EXCEPTION'});}})();";
    }

'''
marker='    private String tempStateJs(){\n'
assert s.count(marker)==1
s=s.replace(marker,new_event_method+marker,1)

# Sanitized state exposes structural completion/temp fields only; raw text remains local.
s=s.replace('"success","ready","route_class","local_path_hash","temporary_hint","turn_count"','"success","ready","route_class","local_path_hash","temporary_hint","semantic_temp_state","temp_candidate_count","turn_count"')
s=s.replace('"last_user_hash","last_assistant_hash","composer_candidate_count"','"last_user_hash","last_assistant_hash","assistant_completion_candidate_count","assistant_completion_struct_hash","composer_candidate_count"')

# Remove stale timer fields/references from diagnostics/reset code where possible.
for token in ['responseTimeoutEmitted','responseStableHits','responseArmedAtMs','assistantStableHits']:
    # keep declaration only if other passive code still needs it; assignments are harmless but remove direct reset chains later by compilation cleanup.
    pass
# Stale sanitized fields referencing removed semantics are still compilable; normalize their values to structural receipt.
s=s.replace('put(st,"response_stable_hits",responseStableHits); put(st,"response_stable_required",RESPONSE_STABLE_SAMPLES);','put(st,"response_completion_signal_count",o.optInt("assistant_completion_candidate_count",0));')

# Base diagnostics state: explicit non-clock-driven control invariant.
once('put(o,"pro_forbidden",true); put(o,"geometry_selection",false); put(o,"raw_html_remote",false); put(o,"raw_url_remote",false); put(o,"raw_chat_text_remote",false); put(o,"cookies_tokens_remote",false); put(o,"safe_top_inset_px",safeTopInsetPx);', 'put(o,"pro_forbidden",true); put(o,"geometry_selection",false); put(o,"raw_html_remote",false); put(o,"raw_url_remote",false); put(o,"raw_chat_text_remote",false); put(o,"cookies_tokens_remote",false); put(o,"safe_top_inset_px",safeTopInsetPx); put(o,"control_event_driven",true); put(o,"control_clock_driven",false);', 'event diagnostic invariant')

# Remove obsolete reset references that depended on timing fields/constants.
s=s.replace('responseArmed=false; responseStarted=false; responseTimeoutEmitted=false;','responseArmed=false; responseStarted=false;')
s=s.replace('responseStableHits=0; responseArmedAtMs=0L;','')

# Telemetry config lineage.
s=s.replace("TelemetryConfigV68","TelemetryConfigV69")
ACT.write_text(s)
assert OLD.exists();OLD.unlink()
cfg=(PKG/"TelemetryConfigV68.java").read_text();(PKG/"TelemetryConfigV69.java").write_text(cfg.replace("TelemetryConfigV68","TelemetryConfigV69"));(PKG/"TelemetryConfigV68.java").unlink()

# Version identity.
g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+69\b","versionCode 70",gs);gs=gs.replace("0.66-stable-diag-semantic-planner-core-temp-entry-readiness","0.67-stable-diag-semantic-planner-event-driven");g.write_text(gs)

# Launcher only; Accessibility identity remains V51.
m=ROOT/"app/src/main/AndroidManifest.xml";ms=m.read_text().replace("OrchestratorPlannerCoreV68Activity","OrchestratorPlannerCoreV69Activity");assert "ControlPlaneAccessibilityServiceV51" in ms and "@xml/cp_accessibility_service_v51" in ms
for v in range(52,70):assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

out=ACT.read_text()
for required in [
    "PUZZLE_UNKNOWN_AT_BUILD_TIME","WebMessagePort","MutationObserver","PASS_EVENT_BRIDGE_CHANNEL_CONNECTED",
    "control_event_driven","control_clock_driven","PASS_PAGE_FINISHED_PLUS_EXACT_NORMAL_TEMP_ENTRY_GATE",
    "PASS_FRESH_TEMP_ROOM_EVENT_RECEIPT","PASS_AUTO_COMPOSER_HASH_EVENT_RECEIPT","PASS_AUTO_EXACT_USER_TURN_EVENT_RECEIPT",
    "PASS_RESPONSE_CORRELATED_AUTO_SEND_EVENT_RECEIPT","copy-turn-action-button","PASS_RESPONSE_COMPLETE_BY_ASSISTANT_ACTION_RECEIPT",
    "PASS_PLANNER_RESPONSE_COMPLETE_BY_ACTION_RECEIPT","PASS_TARGET_RESPONSE_COMPLETE_BY_ACTION_RECEIPT",
    "PASS_PLANNER_CHAT_NAVIGATION_EVENT_RECEIPT","CLAIMED_BEFORE_PLANNER_TEMP_ENTRY_CLICK","CLAIMED_BEFORE_AUTO_SEND_CLICK",
    "raw_chat_text_remote","safe_top_inset_px","TelemetryConfigV69"
]:assert required in out,required
for forbidden in ["postDelayed","Thread.sleep","setTimeout(","setInterval(","SAMPLE_MS","SEND_POLL_MS","RESPONSE_TIMEOUT_MS","ScheduledExecutorService","TimerTask","elementFromPoint","document.evaluate","dispatchTouchEvent(","performClick(","ACTION_SET_PROGRESS","CookieManager","getCookie(","addJavascriptInterface","setAttribute(\\\"aria-value"]:
    assert forbidden not in out,forbidden
assert out.count('.click();')==2,out.count('.click();')
assert "Tehran" not in out and "تهران" not in out
print("generated v0.67 event-driven Planner: WebMessagePort+MutationObserver+onPageFinished+semantic receipts; zero fixed-delay/poll/timeout control; Accessibility remains V51")
