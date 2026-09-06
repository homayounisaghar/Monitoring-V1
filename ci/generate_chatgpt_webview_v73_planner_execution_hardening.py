#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.71: harden the complete post-plan execution family after the fresh-SEND
# v0.70 run reached a valid SEND plan but produced no later terminal checkpoint.
# Preserve zero-clock control. Remove the unnecessary asynchronous pre-navigation
# read, bind read callbacks to the current document epoch, eliminate silent
# transition no-ops, reset per-run diagnostics/state, and improve execution
# milestones/observation failure propagation in one consolidated change.
runpy.run_path("ci/generate_chatgpt_webview_v72_planner_consolidated_audit.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorPlannerCoreV72Activity.java"
ACT=PKG/"OrchestratorPlannerCoreV73Activity.java"
s=OLD.read_text()

def method(name,body,rettype="void"):
    global s
    pat=rf'    private {re.escape(rettype)} {re.escape(name)}\([^\n]*\)\{{.*?\n    \}}\n\n'
    m=re.search(pat,s,re.S)
    assert m,(rettype,name,"method not found")
    s=s[:m.start()]+body+s[m.end():]

def once(old,new,label):
    global s
    n=s.count(old)
    assert n==1,(label,n)
    s=s.replace(old,new,1)

# Identity.
s=s.replace("OrchestratorPlannerCoreV72Activity","OrchestratorPlannerCoreV73Activity")
s=s.replace('SCHEMA="cp-v72-planner-core-consolidated-v1"','SCHEMA="cp-v73-planner-core-execution-hardened-v1"')
s=s.replace('SCENARIO="same-apk-semantic-planner-core-consolidated-audit"','SCENARIO="same-apk-semantic-planner-core-execution-hardened"')
s=s.replace('getSharedPreferences("cp_v72_planner_core",MODE_PRIVATE)','getSharedPreferences("cp_v73_planner_core",MODE_PRIVATE)')
s=s.replace('testId="cp70-"+UUID.randomUUID();','testId="cp71-"+UUID.randomUUID();')
s=s.replace('status.setText("v0.70 EVENT-DRIVEN Planner consolidated-audit ready. Puzzle is unknown at build time.\\nNo clock control. Navigation waits for semantic hydration; composer resolution and Planner execution are guarded end-to-end.");','status.setText("v0.71 EVENT-DRIVEN Planner execution-hardened ready. Puzzle is unknown at build time.\\nNo clock control. Planner actions dispatch directly from proven Temporary state; document-epoch receipts reject stale reads.");')

# Document/read epochs prevent callbacks from a previous document from driving the
# current state machine after navigation.
once('    private int remoteTelemetryPosts=0;\n','''    private int remoteTelemetryPosts=0;
    private long documentEpoch=0L;
    private long pageFinishedEpoch=-1L;
    private long readSerial=0L;
    private long activeReadSerial=0L;
''','epoch fields')

client=re.search(r'        web\.setWebViewClient\(new WebViewClient\(\)\{.*?\n        \}\);',s,re.S)
assert client,"web client"
s=s[:client.start()]+'''        web.setWebViewClient(new WebViewClient(){
            @Override public void onPageStarted(WebView v,String u,Bitmap f){
                super.onPageStarted(v,u,f); documentEpoch++; pageFinishedReady=false; pageFinishedEpoch=-1L; closeEventBridge();
            }
            @Override public void onPageFinished(WebView v,String u){
                super.onPageFinished(v,u); pageFinishedReady=true; pageFinishedEpoch=documentEpoch; installEventBridge(documentEpoch);
            }
        });'''+s[client.end():]

method('closeEventBridge','''    private void closeEventBridge(){
        try{if(eventPort!=null)eventPort.close();}catch(Exception ignored){}eventPort=null;
        eventReadInFlight=false;eventReadDirty=false;activeReadSerial=++readSerial;
    }

''')
method('installEventBridge','''    private void installEventBridge(long epoch){
        if(web==null||epoch!=documentEpoch)return;closeEventBridge();
        eval(eventBootstrapJs(),o->{
            if(epoch!=documentEpoch)return;
            if(!o.optBoolean("success",false)){emit("EVENT_BRIDGE","EVENT_BRIDGE_BOOTSTRAP_FAILED",sanitizedState(o));if(plannerRunning)plannerFail("EVENT_BRIDGE_BOOTSTRAP_FAILED");return;}
            try{
                WebMessagePort[] ports=web.createWebMessageChannel();eventPort=ports[0];final long bridgeEpoch=epoch;
                eventPort.setWebMessageCallback(new WebMessagePort.WebMessageCallback(){
                    @Override public void onMessage(WebMessagePort port,WebMessage message){if(bridgeEpoch==documentEpoch)requestEventRead("DOM_EVENT");}
                });
                web.postWebMessage(new WebMessage("CP_CONNECT",new WebMessagePort[]{ports[1]}),Uri.parse("https://chatgpt.com"));
                JSONObject st=baseState();put(st,"event_bridge_connected",true);put(st,"document_epoch",documentEpoch);emit("EVENT_BRIDGE","PASS_EVENT_BRIDGE_CHANNEL_CONNECTED",st);
            }catch(Exception e){JSONObject st=baseState();put(st,"event_bridge_connected",false);emit("EVENT_BRIDGE","EVENT_BRIDGE_CHANNEL_FAILED",st);if(plannerRunning)plannerFail("EVENT_BRIDGE_CHANNEL_FAILED");}
        });
    }

''')
method('requestEventRead','''    private void requestEventRead(String reason){
        if(web==null)return;if(eventReadInFlight){eventReadDirty=true;return;}
        eventReadInFlight=true;final long epoch=documentEpoch;final long serial=++readSerial;activeReadSerial=serial;
        eval(readJs(),o->{
            if(serial!=activeReadSerial||epoch!=documentEpoch)return;
            eventReadInFlight=false;onObservedState(o,reason);
            if(eventReadDirty){eventReadDirty=false;requestEventRead("COALESCED_DOM_EVENT");}
        });
    }

''')

# Per-run state must not inherit diagnostic ring/history or unresolved side effects
# from an earlier test in the same process.
once('''        plannerRunning=false; autoSendPending=false; plannerIteration=0; plannerActionCount=0; plannerTargetSendCount=0;
        plannerPhase="LEARN"; plannerHistory.clear(); plannerRefToPath.clear(); plannerPathToRef.clear();''','''        plannerRunning=false; autoSendPending=false; plannerActionInFlight=false; plannerIteration=0; plannerActionCount=0; plannerTargetSendCount=0;
        plannerPhase="LEARN"; autoSendPurpose="NONE"; autoSendExpectedHash="-"; autoSendBaselineUserHash="-";
        plannerAfterNav="NONE"; plannerNavRef="MAIN"; plannerNavPath=""; plannerPendingTargetText=""; plannerNavExpectedMinTurns=1;
        returnPending=false; sendPending=false; pendingManualDraftReceipt=false; diagnosticRing.clear(); remoteTelemetryPosts=0;
        plannerHistory.clear(); plannerRefToPath.clear(); plannerPathToRef.clear(); plannerPathKnownTurns.clear();''','start run reset')

# Terminal paths clear in-flight/response authority so stale callbacks cannot revive work.
s=s.replace('plannerRunning=false; autoSendPending=false; plannerPhase="STOPPED";','plannerRunning=false; autoSendPending=false; plannerActionInFlight=false; responseArmed=false; plannerPhase="STOPPED";',1)
s=s.replace('boolean was=plannerRunning; plannerRunning=false; autoSendPending=false; plannerPhase="FAILED";','boolean was=plannerRunning; plannerRunning=false; autoSendPending=false; plannerActionInFlight=false; responseArmed=false; plannerPhase="FAILED";',1)

# Silent transition no-ops are not acceptable for one-shot execution entry points.
s=s.replace('if(!plannerRunning||plannerActionInFlight)return;plannerActionInFlight=true;plannerPhase="TEMP_ENTRY_DISPATCH_IN_FLIGHT";','if(!plannerRunning)return;if(plannerActionInFlight){plannerFail("PLANNER_TEMP_ENTRY_BUSY_UNEXPECTED");return;}plannerActionInFlight=true;plannerPhase="TEMP_ENTRY_DISPATCH_IN_FLIGHT";',1)
s=s.replace('if(!plannerRunning||autoSendPending||plannerActionInFlight)return;if(text==null||text.trim().isEmpty())','if(!plannerRunning)return;if(autoSendPending||plannerActionInFlight){plannerFail("AUTO_SEND_TRANSITION_BUSY_UNEXPECTED");return;}if(text==null||text.trim().isEmpty())',1)
s=s.replace('if(!plannerRunning||!autoSendPending||plannerActionInFlight)return;int cc=','if(!plannerRunning||!autoSendPending)return;if(plannerActionInFlight){plannerFail("AUTO_SEND_CLICK_BUSY_UNEXPECTED");return;}int cc=',1)

# Planner actions always originate from the just-proven fresh Temporary response.
# Dispatch navigation directly from that state. Do not insert another asynchronous
# read between plan acceptance and the durable navigation claim.
s=s.replace('executePlannerAction(action);','executePlannerAction(action,o);',1)
method('executePlannerAction','''    private void executePlannerAction(JSONObject a,JSONObject plannerState){
        if(!plannerRunning)return;
        if(plannerActionCount>MAX_PLANNER_ITERATIONS){plannerFail("PLANNER_ACTION_LIMIT_REACHED");return;}
        boolean sourceOk=plannerState!=null&&plannerState.optBoolean("temporary_hint",false)&&"HOME".equals(plannerState.optString("route_class",""))&&"complete".equals(plannerState.optString("ready",""))&&plannerState.optInt("assistant_completion_candidate_count",0)>=1;
        if(!sourceOk){plannerFail("PLANNER_ACTION_SOURCE_NOT_PROVEN_FRESH_TEMP");return;}
        String k=a.optString("action",""),ref=a.optString("chat_ref","MAIN"),text=a.optString("text","");
        if("DONE".equals(k)){navigatePlannerRef("MAIN","DONE","",plannerState);return;}
        if("GO_MAIN_CHAT".equals(k)){navigatePlannerRef("MAIN","OBSERVE","",plannerState);return;}
        if("GO_CHAT".equals(k)){navigatePlannerRef(ref,"OBSERVE","",plannerState);return;}
        if("READ_LAST_RESPONSE".equals(k)){navigatePlannerRef(ref,"OBSERVE","",plannerState);return;}
        if("SEND".equals(k)){navigatePlannerRef(ref,"SEND",text,plannerState);return;}
        plannerFail("PLANNER_ACTION_NOT_IMPLEMENTED");
    }

''')
method('navigatePlannerRef','''    private void navigatePlannerRef(String ref,String after,String text,JSONObject sourceState){
        if(!plannerRunning)return;if(plannerActionInFlight){plannerFail("PLANNER_ACTION_NAV_BUSY_UNEXPECTED");return;}
        buildPlannerContext();String path=plannerRefToPath.get(ref);if(path==null||!path.matches("^/c/[^/?#]+$")){plannerFail("PLANNER_CHAT_REF_NOT_AVAILABLE");return;}
        plannerNavRef=ref;plannerNavPath=path;plannerAfterNav=after;plannerPendingTargetText=text;Integer known=plannerPathKnownTurns.get(path);plannerNavExpectedMinTurns=Math.max(1,known==null?1:known);
        plannerActionInFlight=true;plannerPhase="PLANNER_NAV_DISPATCH_IN_FLIGHT";
        String claimId="planner-nav-"+UUID.randomUUID();boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","PLANNER_CHAT_NAV").putString("claim_anchor_hash",hashNorm(path)).putString("claim_status","CLAIMED_BEFORE_PLANNER_CHAT_NAV").commit();
        JSONObject st=sanitizedState(sourceState);put(st,"planner_target_ref",ref);put(st,"planner_after_nav",after);put(st,"claim_committed",committed);put(st,"expected_min_turns",plannerNavExpectedMinTurns);
        emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_PLANNER_CHAT_NAVIGATION":"CLAIM_COMMIT_FAILED_NO_NAVIGATION",st);
        emit("PLANNER_ACTION_EXECUTION",committed?"PASS_PLANNER_ACTION_NAVIGATION_CLAIMED":"PLANNER_ACTION_NAVIGATION_CLAIM_FAILED",st);
        if(!committed){plannerActionInFlight=false;plannerFail("PLANNER_CHAT_NAV_CLAIM_FAILED");return;}
        pageUiDispatches++;pageUiWrites++;pageFinishedReady=false;pageFinishedEpoch=-1L;plannerPhase="WAIT_PLANNER_NAV_RECEIPT";web.loadUrl("https://chatgpt.com"+path);plannerActionInFlight=false;
    }

''')

# Bind readiness gates to the current document's own page-finished receipt.
s=s.replace('boolean gate=pageFinishedReady&&"complete".equals','boolean gate=pageFinishedReady&&pageFinishedEpoch==documentEpoch&&"complete".equals',1)
s=s.replace('boolean ok=pageFinishedReady&&plannerNavPath.equals','boolean ok=pageFinishedReady&&pageFinishedEpoch==documentEpoch&&plannerNavPath.equals',1)
s=s.replace('boolean hydrated=pageFinishedReady&&"complete".equals','boolean hydrated=pageFinishedReady&&pageFinishedEpoch==documentEpoch&&"complete".equals',1)

# Observation is semantic input for the next Planner iteration; do not silently
# continue if recording it fails.
method('recordPlannerObservation','''    private boolean recordPlannerObservation(JSONObject o,String kind){
        try{
            JSONObject obs=new JSONObject();obs.put("kind",kind);obs.put("iteration",plannerIteration);obs.put("chat_ref",plannerRefForPath(o.optString("local_path","")));
            obs.put("route_class",o.optString("route_class",""));obs.put("temporary_hint",o.optBoolean("temporary_hint",false));obs.put("lifecycle",lifecycle);
            obs.put("last_user_text",clip(o.optString("last_user_text",""),1800));obs.put("last_assistant_text",clip(o.optString("last_assistant_text",""),2600));
            String op=o.optString("local_path","");if(op.matches("^/c/[^/?#]+$")){Integer prev=plannerPathKnownTurns.get(op);plannerPathKnownTurns.put(op,Math.max(prev==null?0:prev,o.optInt("turn_count",0)));}
            addPlannerHistory(null,kind,obs);
            JSONObject st=sanitizedState(o);put(st,"observation_kind",kind);put(st,"observation_assistant_hash",o.optString("last_assistant_hash","-"));put(st,"planner_target_ref",plannerRefForPath(o.optString("local_path","")));
            emit("PLANNER_OBSERVATION","PASS_LOCAL_OBSERVATION_CAPTURED_FOR_NEXT_ITERATION",st);return true;
        }catch(Exception e){return false;}
    }

''',rettype='boolean')
s=s.replace('plannerAfterNav="NONE"; recordPlannerObservation(o,"FINAL_MAIN_RECEIPT");\n            plannerRunning=false;','plannerAfterNav="NONE"; if(!recordPlannerObservation(o,"FINAL_MAIN_RECEIPT")){plannerFail("PLANNER_FINAL_OBSERVATION_FAILED");return;}\n            plannerRunning=false;',1)
s=s.replace('plannerAfterNav="NONE"; recordPlannerObservation(o,"ACTION_OBSERVATION"); plannerIteration++; openFreshPlannerTemp();','plannerAfterNav="NONE"; if(!recordPlannerObservation(o,"ACTION_OBSERVATION")){plannerFail("PLANNER_ACTION_OBSERVATION_FAILED");return;} plannerIteration++; openFreshPlannerTemp();',1)
s=s.replace('plannerTargetSendCount++;recordPlannerObservation(o,"TARGET_RESPONSE_COMPLETE");plannerIteration++;openFreshPlannerTemp();return;','plannerTargetSendCount++;if(!recordPlannerObservation(o,"TARGET_RESPONSE_COMPLETE")){plannerFail("PLANNER_TARGET_OBSERVATION_FAILED");return;}plannerIteration++;openFreshPlannerTemp();return;',1)

# Target response completion is a useful sparse checkpoint; diagnostics are reset
# each run and remain bounded.
s=s.replace('emit("AUTO_RESPONSE_RECEIPT","PASS_TARGET_RESPONSE_COMPLETE_BY_ACTION_RECEIPT",sanitizedState(o));','JSONObject ts=sanitizedState(o);put(ts,"purpose",purpose);emit("AUTO_RESPONSE_RECEIPT","PASS_TARGET_RESPONSE_COMPLETE_BY_ACTION_RECEIPT",ts);',1)
s=s.replace('if("LEARN_FINISHED".equals(phase)||"PLANNER_STARTED".equals(phase)||"PLANNER_PLAN".equals(phase)||"PLANNER_OBSERVATION".equals(phase)||"PLANNER_FINAL".equals(phase)||"PLANNER_STOP".equals(phase))return true;','if("LEARN_FINISHED".equals(phase)||"PLANNER_STARTED".equals(phase)||"PLANNER_PLAN".equals(phase)||"PLANNER_ACTION_EXECUTION".equals(phase)||"PLANNER_OBSERVATION".equals(phase)||"PLANNER_FINAL".equals(phase)||"PLANNER_STOP".equals(phase))return true;',1)
s=s.replace('if("DURABLE_CLAIM".equals(phase)&&"TARGET_MESSAGE".equals(state.optString("purpose","")))return true;','if("DURABLE_CLAIM".equals(phase)&&"TARGET_MESSAGE".equals(state.optString("purpose","")))return true;\n        if("AUTO_RESPONSE_RECEIPT".equals(phase)&&"TARGET_MESSAGE".equals(state.optString("purpose","")))return true;',1)

# Telemetry/config/version lineage.
s=s.replace("TelemetryConfigV72","TelemetryConfigV73")
ACT.write_text(s)
assert OLD.exists();OLD.unlink()
cfg=(PKG/"TelemetryConfigV72.java").read_text()
(PKG/"TelemetryConfigV73.java").write_text(cfg.replace("TelemetryConfigV72","TelemetryConfigV73"))
(PKG/"TelemetryConfigV72.java").unlink()

g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+73\b","versionCode 74",gs);gs=gs.replace("0.70-stable-diag-semantic-planner-consolidated-audit","0.71-stable-diag-semantic-planner-execution-hardened");g.write_text(gs)
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorPlannerCoreV72Activity","OrchestratorPlannerCoreV73Activity");assert "ControlPlaneAccessibilityServiceV51" in ms and "@xml/cp_accessibility_service_v51" in ms;mf.write_text(ms)

out=ACT.read_text()
for required in [
    "PUZZLE_UNKNOWN_AT_BUILD_TIME","CONTROL_EVENT_DRIVEN_NO_FIXED_DELAY_POLL_TIMEOUT","documentEpoch","pageFinishedEpoch","activeReadSerial",
    "PLANNER_ACTION_SOURCE_NOT_PROVEN_FRESH_TEMP","PLANNER_ACTION_EXECUTION","PASS_PLANNER_ACTION_NAVIGATION_CLAIMED",
    "PLANNER_ACTION_NAV_BUSY_UNEXPECTED","AUTO_SEND_TRANSITION_BUSY_UNEXPECTED","PLANNER_TARGET_OBSERVATION_FAILED",
    "diagnosticRing.clear()","remoteTelemetryPosts=0","PASS_TARGET_RESPONSE_COMPLETE_BY_ACTION_RECEIPT","TelemetryConfigV73"
]:assert required in out,required
for forbidden in [
    "postDelayed","Thread.sleep","setTimeout(","setInterval(","SAMPLE_MS","SEND_POLL_MS","RESPONSE_TIMEOUT_MS",
    "ScheduledExecutorService","TimerTask","pollPlannerNormalHome","pollPlannerTempReceipt","pollAutoComposerReceipt",
    "pollAutoSendReceipt","pollAutoResponse","pollPlannerNavReceipt","pollSendReceipt","confirmAutoSendReceipt",
    "elementFromPoint","document.evaluate","dispatchTouchEvent(","performClick(","ACTION_SET_PROGRESS","CookieManager",
    "getCookie(","addJavascriptInterface","setAttribute(\\\"aria-value"
]:assert forbidden not in out,forbidden
assert out.count('.click();')==2,out.count('.click();')
assert 'navigatePlannerRef(String ref,String after,String text)' not in out
assert 'eval(readJs(),o->{\n            boolean already=path.equals' not in out
print("PASS v0.71 execution hardening: direct action navigation, document-epoch state receipts, no silent transition no-ops, per-run diagnostic reset, zero-clock preserved")
