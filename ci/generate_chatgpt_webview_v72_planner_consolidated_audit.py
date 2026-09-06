#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.70: one consolidated fix after an end-to-end audit of v0.69.
# Preserve the zero-clock/event-driven control plane and fix the structural
# issues together: persistent-composer resolution, semantic hydration after
# navigation, Planner-response re-entry, persistent-send receipt fallback,
# event-bridge reconnect duplication, parser/prompt robustness, and bounded
# remote diagnostic telemetry with a local sanitized ring.
runpy.run_path("ci/generate_chatgpt_webview_v71_planner_parser_v2.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorPlannerCoreV71Activity.java"
ACT=PKG/"OrchestratorPlannerCoreV72Activity.java"
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
s=s.replace("OrchestratorPlannerCoreV71Activity","OrchestratorPlannerCoreV72Activity")
s=s.replace('SCHEMA="cp-v71-planner-core-parser-v2-v1"','SCHEMA="cp-v72-planner-core-consolidated-v1"')
s=s.replace('SCENARIO="same-apk-semantic-planner-core-parser-v2"','SCENARIO="same-apk-semantic-planner-core-consolidated-audit"')
s=s.replace('getSharedPreferences("cp_v71_planner_core",MODE_PRIVATE)','getSharedPreferences("cp_v72_planner_core",MODE_PRIVATE)')
s=s.replace('testId="cp69-"+UUID.randomUUID();','testId="cp70-"+UUID.randomUUID();')
s=s.replace('status.setText("v0.69 EVENT-DRIVEN Planner parser-v2 ready. Puzzle is unknown at build time.\\nNo clock control. A single bounded JSON action may be recovered from harmless Markdown/prose wrapping; ambiguity still fails closed.");','status.setText("v0.70 EVENT-DRIVEN Planner consolidated-audit ready. Puzzle is unknown at build time.\\nNo clock control. Navigation waits for semantic hydration; composer resolution and Planner execution are guarded end-to-end.");')

# Remove timer-era dead fields so zero-clock architecture is explicit, not only unused.
for line in [
    '    private int assistantStableHits=0;\n',
    '    private boolean responseTimeoutEmitted=false;\n',
    '    private int responseStableHits=0;\n',
    '    private long responseArmedAtMs=0L;\n',
    '    private String autoSendText="";\n',
]: s=s.replace(line,'')
s=s.replace('lastStateFingerprint="-"; lastControlTelemetryFingerprint="-"; lastAssistantHash="-"; assistantStableHits=0; lifecycle="IDLE";','lastStateFingerprint="-"; lastControlTelemetryFingerprint="-"; lastAssistantHash="-"; lifecycle="IDLE";')
s=s.replace('autoSendPending=true;autoSendPurpose=purpose;autoSendText=text;autoSendExpectedHash=hashNorm(text);plannerActionInFlight=true;','autoSendPending=true;autoSendPurpose=purpose;autoSendExpectedHash=hashNorm(text);plannerActionInFlight=true;')

once('    private static final int MAX_PLANNER_SEND_CHARS=3000;\n','    private static final int MAX_PLANNER_SEND_CHARS=3000;\n    private static final int MAX_DIAG_RING=64;\n','diag ring constant')
once('    private String plannerPendingTargetText="";\n','''    private String plannerPendingTargetText="";
    private int plannerNavExpectedMinTurns=1;
    private final LinkedHashMap<String,Integer> plannerPathKnownTurns=new LinkedHashMap<>();
    private final ArrayList<String> diagnosticRing=new ArrayList<>();
    private int remoteTelemetryPosts=0;
''','planner audit fields')

# Persistent Chat currently exposes a composer shape not covered by [contenteditable=true].
# Resolve a unique preferred composer via prompt-textarea / composer-or-prompt testid;
# fall back only when exactly one editable exists. The same resolver is used by read/write/send.
old="const C=Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).filter(e=>V(e)&&!e.hasAttribute('disabled')),c=C.length===1?C[0]:null,ct=c?txt(c):'';"
new="const CA=Array.from(document.querySelectorAll('textarea,[contenteditable],[role=textbox]')).filter(e=>V(e)&&!e.hasAttribute('disabled')&&e.getAttribute('aria-disabled')!=='true'&&e.getAttribute('contenteditable')!=='false');const CP=CA.filter(e=>e.id==='prompt-textarea'||N(e.getAttribute('data-testid')||'').includes('composer')||N(e.getAttribute('data-testid')||'').includes('prompt'));const C=CP.length===1?CP:((CP.length===0&&CA.length===1)?CA:[]),c=C.length===1?C[0]:null,ct=c?txt(c):'',cm=CP.length===1?'PREFERRED':((CP.length===0&&CA.length===1)?'SOLE_FALLBACK':'AMBIGUOUS');"
once(old,new,'read composer resolver')
old="const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const C=Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).filter(e=>V(e)&&!e.hasAttribute('disabled'));if(C.length!==1)return JSON.stringify({success:false,reason:'COMPOSER_COUNT',composer_count:C.length,mutated:false});const e=C[0];"
new="const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const CA=Array.from(document.querySelectorAll('textarea,[contenteditable],[role=textbox]')).filter(e=>V(e)&&!e.hasAttribute('disabled')&&e.getAttribute('aria-disabled')!=='true'&&e.getAttribute('contenteditable')!=='false');const CP=CA.filter(e=>e.id==='prompt-textarea'||N(e.getAttribute('data-testid')||'').includes('composer')||N(e.getAttribute('data-testid')||'').includes('prompt'));const C=CP.length===1?CP:((CP.length===0&&CA.length===1)?CA:[]);if(C.length!==1)return JSON.stringify({success:false,reason:'COMPOSER_COUNT',composer_count:C.length,composer_raw_count:CA.length,composer_preferred_count:CP.length,mutated:false});const e=C[0];"
once(old,new,'write composer resolver')
old="const C=Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).filter(e=>V(e)&&!e.hasAttribute('disabled'));if(C.length!==1)return JSON.stringify({success:false,reason:'COMPOSER_COUNT',send_match_count:0,dispatched:false,click_observed:false});const ch=H(N(txt(C[0])));"
new="const CA=Array.from(document.querySelectorAll('textarea,[contenteditable],[role=textbox]')).filter(e=>V(e)&&!e.hasAttribute('disabled')&&e.getAttribute('aria-disabled')!=='true'&&e.getAttribute('contenteditable')!=='false');const CP=CA.filter(e=>e.id==='prompt-textarea'||N(e.getAttribute('data-testid')||'').includes('composer')||N(e.getAttribute('data-testid')||'').includes('prompt'));const C=CP.length===1?CP:((CP.length===0&&CA.length===1)?CA:[]);if(C.length!==1)return JSON.stringify({success:false,reason:'COMPOSER_COUNT',composer_count:C.length,composer_raw_count:CA.length,composer_preferred_count:CP.length,send_match_count:0,dispatched:false,click_observed:false});const ch=H(N(txt(C[0])));"
once(old,new,'send composer resolver')
once("composer_candidate_count:C.length,composer_text:ct,composer_hash:c?H(N(ct)):'-',composer_chars:ct.length,","composer_candidate_count:C.length,composer_raw_candidate_count:CA.length,composer_preferred_candidate_count:CP.length,composer_resolution_mode:cm,composer_text:ct,composer_hash:c?H(N(ct)):'-',composer_chars:ct.length,",'composer resolver diagnostics')
s=s.replace('"composer_candidate_count","composer_hash","composer_chars"','"composer_candidate_count","composer_raw_candidate_count","composer_preferred_candidate_count","composer_resolution_mode","composer_hash","composer_chars"')
s=s.replace('"composer_count","composer_hash","send_match_count"','"composer_count","composer_raw_count","composer_preferred_count","composer_hash","send_match_count"')

# Build a content hydration floor from the learned snapshot. Keep it monotonic across
# Planner observations so a later return cannot accept a partially rehydrated older view.
s=s.replace('plannerHistory.clear();plannerPhase="INTERPRET_START";','plannerHistory.clear();plannerPathKnownTurns.clear();plannerPhase="INTERPRET_START";',1)
old='if("CONVERSATION".equals(route)&&path.matches("^/c/[^/?#]+$")){ref=plannerRefForPath(path);JSONArray turns=r.optJSONArray("turns");if(turns!=null)latest.put(ref,compactTurns(turns,8,1200));}'
new='if("CONVERSATION".equals(route)&&path.matches("^/c/[^/?#]+$")){ref=plannerRefForPath(path);JSONArray turns=r.optJSONArray("turns");if(turns!=null){latest.put(ref,compactTurns(turns,12,1400));Integer prev=plannerPathKnownTurns.get(path);plannerPathKnownTurns.put(path,Math.max(prev==null?0:prev,turns.length()));}}'
once(old,new,'known turn floor')
s=s.replace('timeline.put(ev);','timeline.put(ev);while(timeline.length()>60)removeFirst(timeline);',1)
old='obs.put("last_user_text",clip(o.optString("last_user_text",""),1800));obs.put("last_assistant_text",clip(o.optString("last_assistant_text",""),2600));\n            addPlannerHistory(null,kind,obs);'
new='obs.put("last_user_text",clip(o.optString("last_user_text",""),1800));obs.put("last_assistant_text",clip(o.optString("last_assistant_text",""),2600));\n            String op=o.optString("local_path","");if(op.matches("^/c/[^/?#]+$")){Integer prev=plannerPathKnownTurns.get(op);plannerPathKnownTurns.put(op,Math.max(prev==null?0:prev,o.optInt("turn_count",0)));}\n            addPlannerHistory(null,kind,obs);'
once(old,new,'dynamic known turn floor')

# Planner prompt examples must be actual JSON, not JSON with literal backslashes.
method('buildPlannerPrompt',r'''    private String buildPlannerPrompt(){
        try{
            JSONObject ctx=buildPlannerContext();JSONArray hist=new JSONArray();for(String x:plannerHistory){try{hist.put(new JSONObject(x));}catch(Exception ignored){}}
            ctx.put("execution_history",hist);ctx.put("planner_iteration",plannerIteration);ctx.put("blind_build_marker",BLIND_BUILD_MARKER);
            String rules="You are the semantic control-plane Planner inside the user's existing ChatGPT session. The APK was frozen before the puzzle was known. Solve only from the supplied evidence. Return exactly one executable JSON action. No markdown, prose, explanation, or chain-of-thought. Allowed actions: {\"version\":1,\"action\":\"GO_MAIN_CHAT\"}; {\"version\":1,\"action\":\"GO_CHAT\",\"chat_ref\":\"CHAT_1\"}; {\"version\":1,\"action\":\"READ_LAST_RESPONSE\",\"chat_ref\":\"MAIN\"}; {\"version\":1,\"action\":\"SEND\",\"chat_ref\":\"MAIN\",\"text\":\"message\"}; {\"version\":1,\"action\":\"DONE\"}. Choose only one action. Never invent a chat_ref. SEND only if the semantic task requires a new message. If the demonstrated task is complete, emit DONE. Treat Temporary snapshots as evidence only; they are not navigable chat_refs. CONTEXT=";
            String p=rules+ctx.toString();return p.length()<=MAX_PLANNER_PROMPT_CHARS?p:"";
        }catch(Exception e){return "";}
    }

''','String')

# Exactly one bounded action is authoritative; unrelated JSON in presentation wrapping
# is not itself ambiguity. Multiple bounded actions still fail closed.
s=s.replace('if(jsonObjects!=1||valid!=1)return null;\n            plannerParseMode=x.equals(acceptedRaw)?"EXACT_JSON":"WRAPPED_SINGLE_JSON";','if(valid!=1)return null;\n            plannerParseMode=x.equals(acceptedRaw)?"EXACT_JSON":(jsonObjects==1?"WRAPPED_SINGLE_JSON":"WRAPPED_ONE_VALID_ACTION");')

# Navigation is two-stage: route receipt first, then semantic content hydration.
once('plannerNavRef=ref;plannerNavPath=path;plannerAfterNav=after;plannerPendingTargetText=text;','plannerNavRef=ref;plannerNavPath=path;plannerAfterNav=after;plannerPendingTargetText=text;Integer known=plannerPathKnownTurns.get(path);plannerNavExpectedMinTurns=Math.max(1,known==null?1:known);','navigation hydration floor')
s=s.replace('boolean already=path.equals(o.optString("local_path",""))&&"CONVERSATION".equals(o.optString("route_class",""));if(already){afterPlannerNavigation(o);return;}','boolean already=path.equals(o.optString("local_path",""))&&"CONVERSATION".equals(o.optString("route_class",""));if(already){plannerPhase="WAIT_PLANNER_CONTENT_READY";requestEventRead("PLANNER_ALREADY_ON_TARGET");return;}',1)

# Consume a completed response by changing phase before parsing/executing it. This
# closes the duplicate-plan re-entry window from repeated DOM events.
method('driveAutoResponseFromState','''    private void driveAutoResponseFromState(JSONObject o){
        updateLifecycle(o);
        boolean complete=!responseArmed&&responseStarted&&"COMPLETE".equals(lifecycle)&&o.optInt("assistant_completion_candidate_count",0)>=1;
        if(!complete)return;
        String purpose=autoSendPurpose;autoSendPending=false;
        if("PLANNER_PROMPT".equals(purpose)){
            plannerPhase="PLANNER_RESPONSE_READY";
            emit("AUTO_RESPONSE_RECEIPT","PASS_PLANNER_RESPONSE_COMPLETE_BY_ACTION_RECEIPT",sanitizedState(o));
            handlePlannerResponse(o);return;
        }
        if("TARGET_MESSAGE".equals(purpose)){
            plannerPhase="TARGET_RESPONSE_READY";
            emit("AUTO_RESPONSE_RECEIPT","PASS_TARGET_RESPONSE_COMPLETE_BY_ACTION_RECEIPT",sanitizedState(o));
            plannerTargetSendCount++;recordPlannerObservation(o,"TARGET_RESPONSE_COMPLETE");plannerIteration++;openFreshPlannerTemp();return;
        }
        plannerFail("AUTO_RESPONSE_UNKNOWN_PURPOSE");
    }

''')
s=s.replace('emit("PLANNER_PLAN","PASS_BOUNDED_PLANNER_ACTION_PARSED",st);\n        addPlannerHistory(action,"PLAN_ACCEPTED",null);','plannerPhase="PLAN_ACCEPTED";emit("PLANNER_PLAN","PASS_BOUNDED_PLANNER_ACTION_PARSED",st);\n        addPlannerHistory(action,"PLAN_ACCEPTED",null);',1)

method('drivePlannerFromState','''    private void drivePlannerFromState(JSONObject o){
        if(!plannerRunning||plannerActionInFlight)return;
        if("NAVIGATE_HOME_FOR_FRESH_TEMP".equals(plannerPhase)){
            boolean gate=pageFinishedReady&&"complete".equals(o.optString("ready",""))&&"HOME".equals(o.optString("route_class",""))&&"NORMAL".equals(o.optString("semantic_temp_state",""))&&o.optInt("temp_candidate_count",0)==1;
            if(gate){emit("PLANNER_TEMP_GATE","PASS_PAGE_FINISHED_PLUS_EXACT_NORMAL_TEMP_ENTRY_GATE",sanitizedState(o));plannerEnterFreshTemp(o);}return;
        }
        if("WAIT_TEMP_ENTRY_RECEIPT".equals(plannerPhase)){
            boolean temp="TEMP".equals(o.optString("semantic_temp_state",""))&&o.optInt("temp_candidate_count",0)==1&&o.optBoolean("temporary_hint",false);
            if(temp){emit("PLANNER_TEMP_RECEIPT","PASS_FRESH_TEMP_ROOM_EVENT_RECEIPT",sanitizedState(o));plannerPhase="SEND_PLANNER_PACKET";String packet=buildPlannerPrompt();if(packet==null||packet.length()==0||packet.length()>MAX_PLANNER_PROMPT_CHARS){plannerFail("PLANNER_PACKET_SIZE_INVALID");return;}autoWriteAndSend(packet,"PLANNER_PROMPT");}return;
        }
        if("WAIT_AUTO_COMPOSER_RECEIPT".equals(plannerPhase)){
            boolean receipt=o.optInt("composer_candidate_count",0)==1&&autoSendExpectedHash.equals(o.optString("composer_hash",""));
            if(receipt){emit("AUTO_COMPOSER_RECEIPT","PASS_AUTO_COMPOSER_HASH_EVENT_RECEIPT",sanitizedState(o));claimAutoSendClick(o);}return;
        }
        if("WAIT_AUTO_SEND_RECEIPT".equals(plannerPhase)){
            String observedUser=o.optString("last_user_hash","-"),observedAssistant=o.optString("last_assistant_hash","-");
            boolean cleared=o.optInt("composer_chars",-1)==0;
            boolean exact=cleared&&autoSendExpectedHash.equals(observedUser);
            boolean assistantDiverged=!"-".equals(observedAssistant)&&!observedAssistant.equals(pendingResponseBaselineHash);
            boolean userAdvanced=!"-".equals(observedUser)&&!observedUser.equals(autoSendBaselineUserHash);
            boolean freshTemp="PLANNER_PROMPT".equals(autoSendPurpose)&&"-".equals(pendingResponseBaselineHash)&&o.optBoolean("temporary_hint",false);
            boolean samePersistentTarget="TARGET_MESSAGE".equals(autoSendPurpose)&&"CONVERSATION".equals(o.optString("route_class",""))&&plannerNavPath.equals(o.optString("local_path",""));
            boolean correlated=cleared&&assistantDiverged&&(freshTemp||userAdvanced||samePersistentTarget);
            if(exact||correlated){String basis=exact?"EXACT_USER_HASH_EVENT":(freshTemp?"FRESH_TEMP_ASSISTANT_EVENT":(userAdvanced?"USER_ADVANCE_PLUS_ASSISTANT_EVENT":"TARGET_ROUTE_PLUS_ASSISTANT_EVENT"));JSONObject st=sanitizedState(o);put(st,"receipt_basis",basis);emit("AUTO_SEND_RECEIPT",exact?"PASS_AUTO_EXACT_USER_TURN_EVENT_RECEIPT":"PASS_RESPONSE_CORRELATED_AUTO_SEND_EVENT_RECEIPT",st);prefs.edit().putString("claim_status","AUTO_SEND_RECEIPT_CONFIRMED_"+basis).commit();armResponseTransaction(o);plannerPhase="PLANNER_PROMPT".equals(autoSendPurpose)?"WAIT_PLANNER_RESPONSE":"WAIT_TARGET_RESPONSE";driveAutoResponseFromState(o);}return;
        }
        if("WAIT_PLANNER_RESPONSE".equals(plannerPhase)||"WAIT_TARGET_RESPONSE".equals(plannerPhase)){driveAutoResponseFromState(o);return;}
        if("WAIT_PLANNER_NAV_RECEIPT".equals(plannerPhase)){
            boolean ok=pageFinishedReady&&plannerNavPath.equals(o.optString("local_path",""))&&"CONVERSATION".equals(o.optString("route_class",""));
            if(ok){plannerPhase="WAIT_PLANNER_CONTENT_READY";JSONObject st=sanitizedState(o);put(st,"expected_min_turns",plannerNavExpectedMinTurns);emit("PLANNER_NAV_RECEIPT","PASS_PLANNER_ROUTE_RECEIPT_AWAITING_SEMANTIC_HYDRATION",st);requestEventRead("PLANNER_ROUTE_RECEIPT");}return;
        }
        if("WAIT_PLANNER_CONTENT_READY".equals(plannerPhase)){
            boolean hydrated=pageFinishedReady&&"complete".equals(o.optString("ready",""))&&plannerNavPath.equals(o.optString("local_path",""))&&"CONVERSATION".equals(o.optString("route_class",""))&&o.optInt("composer_candidate_count",0)==1&&o.optInt("turn_count",0)>=plannerNavExpectedMinTurns;
            if(hydrated){plannerPhase="PLANNER_CONTENT_READY";JSONObject st=sanitizedState(o);put(st,"expected_min_turns",plannerNavExpectedMinTurns);emit("PLANNER_CONTENT_RECEIPT","PASS_PLANNER_SEMANTIC_CONTENT_HYDRATED",st);afterPlannerNavigation(o);}return;
        }
    }

''')

# A reconnect should replace the active WebMessagePort, not add another observer and
# another full set of DOM listeners on the same document.
method('eventBootstrapJs',r'''    private String eventBootstrapJs(){
        return "(function(){try{if(window.__cpEventBootstrapInstalled)return JSON.stringify({success:true,installed:true});window.__cpEventBootstrapInstalled=true;window.__cpEventPort=null;const fire=()=>{try{const p=window.__cpEventPort;if(p)p.postMessage('DOM');}catch(e){}};window.__cpEventFire=fire;const mo=new MutationObserver(fire);window.__cpEventObserver=mo;mo.observe(document.documentElement,{subtree:true,childList:true,attributes:true,characterData:true});document.addEventListener('input',fire,true);document.addEventListener('change',fire,true);document.addEventListener('click',fire,true);window.addEventListener('popstate',fire,true);const hp=history.pushState.bind(history),hr=history.replaceState.bind(history);history.pushState=function(){const r=hp.apply(history,arguments);fire();return r;};history.replaceState=function(){const r=hr.apply(history,arguments);fire();return r;};window.addEventListener('message',function(ev){try{if(ev.data!=='CP_CONNECT'||!ev.ports||!ev.ports[0])return;window.__cpEventPort=ev.ports[0];fire();}catch(e){}},false);return JSON.stringify({success:true,installed:true});}catch(e){return JSON.stringify({success:false,error_class:'EVENT_BOOTSTRAP_EXCEPTION'});}})();";
    }

''','String')

# Explicit observer/read failures terminate fail-closed instead of silently leaving an
# unobservable wait state. Absence of an event is never converted to success by time.
once('''    private void onObservedState(JSONObject o,String reason){
        if(!o.optBoolean("success",false))return;
''','''    private void onObservedState(JSONObject o,String reason){
        if(!o.optBoolean("success",false)){
            if(plannerRunning){JSONObject st=sanitizedState(o);put(st,"event_reason_hash",hashNorm(reason));emit("CONTROL_READ","CONTROL_READ_FAILED_FAIL_CLOSED",st);plannerFail("CONTROL_READ_FAILED");}
            return;
        }
''','control read fail closed')
s=s.replace('if(!o.optBoolean("success",false)){emit("EVENT_BRIDGE","EVENT_BRIDGE_BOOTSTRAP_FAILED",sanitizedState(o));return;}','if(!o.optBoolean("success",false)){emit("EVENT_BRIDGE","EVENT_BRIDGE_BOOTSTRAP_FAILED",sanitizedState(o));if(plannerRunning)plannerFail("EVENT_BRIDGE_BOOTSTRAP_FAILED");return;}',1)
s=s.replace('}catch(Exception e){JSONObject st=baseState();put(st,"event_bridge_connected",false);emit("EVENT_BRIDGE","EVENT_BRIDGE_CHANNEL_FAILED",st);}','}catch(Exception e){JSONObject st=baseState();put(st,"event_bridge_connected",false);emit("EVENT_BRIDGE","EVENT_BRIDGE_CHANNEL_FAILED",st);if(plannerRunning)plannerFail("EVENT_BRIDGE_CHANNEL_FAILED");}',1)

# Completion is a read-only structural receipt; duplicate matching final controls are
# not a write ambiguity and must not deadlock completion.
s=s.replace('o.optInt("assistant_completion_candidate_count",0)==1','o.optInt("assistant_completion_candidate_count",0)>=1')
s=s.replace('if(finalSignals==1){transitionLifecycle("COMPLETE"','if(finalSignals>=1){transitionLifecycle("COMPLETE"')
s=s.replace('lifecycle=finalSignals==1?"COMPLETE":"ASSISTANT_PRESENT_UNSTABLE"','lifecycle=finalSignals>=1?"COMPLETE":"ASSISTANT_PRESENT_UNSTABLE"')

# Keep every sanitized event in a local ring, but post only bounded checkpoints and
# terminal/failure packets remotely. A terminal packet carries the recent ring, so the
# 50-request collector cannot be exhausted by a normal multi-iteration loop.
insert='''    private boolean shouldRemoteEmit(String phase,String classification,JSONObject state){
        if("LEARN_FINISHED".equals(phase)||"PLANNER_STARTED".equals(phase)||"PLANNER_PLAN".equals(phase)||"PLANNER_OBSERVATION".equals(phase)||"PLANNER_FINAL".equals(phase)||"PLANNER_STOP".equals(phase))return true;
        if("DURABLE_CLAIM".equals(phase)&&"TARGET_MESSAGE".equals(state.optString("purpose","")))return true;
        String c=classification==null?"":classification;
        return c.contains("FAILED")||c.contains("UNCERTAIN")||c.contains("BLOCKED")||c.contains("INVALID");
    }

    private JSONArray diagnosticRingJson(){
        JSONArray a=new JSONArray();for(String x:diagnosticRing){try{a.put(new JSONObject(x));}catch(Exception ignored){}}return a;
    }

'''
idx=s.index('    private void emit(String phase,String classification,JSONObject state){')
s=s[:idx]+insert+s[idx:]
method('emit','''    private void emit(String phase,String classification,JSONObject state){
        if(!TelemetryConfigV71.CONFIGURED)return;
        JSONObject o=new JSONObject(); put(o,"schema_version",SCHEMA); put(o,"scenario_id",SCENARIO); put(o,"test_id",testId);
        put(o,"collector_id",TelemetryConfigV71.COLLECTOR_ID); put(o,"source_ref",TelemetryConfigV71.SOURCE_REF);
        put(o,"seq",telemetrySeq++); put(o,"timestamp_epoch_ms",System.currentTimeMillis()); put(o,"phase",phase); put(o,"classification",classification);
        try{o.put("state",state);}catch(Exception ignored){}
        diagnosticRing.add(o.toString());while(diagnosticRing.size()>MAX_DIAG_RING)diagnosticRing.remove(0);
        if(!shouldRemoteEmit(phase,classification,state))return;
        try{o.put("recent_events",diagnosticRingJson());o.put("remote_post_index",remoteTelemetryPosts++);}catch(Exception ignored){}
        final byte[] bytes=o.toString().getBytes(StandardCharsets.UTF_8);
        net.execute(()->{HttpURLConnection c=null;try{c=(HttpURLConnection)new URL(TelemetryConfigV71.WEBHOOK_URL).openConnection();c.setRequestMethod("POST");c.setConnectTimeout(5000);c.setReadTimeout(5000);c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json");c.setFixedLengthStreamingMode(bytes.length);try(OutputStream os=c.getOutputStream()){os.write(bytes);}c.getResponseCode();}catch(Exception ignored){}finally{if(c!=null)c.disconnect();}});
    }

''')
s=s.replace('put(o,"planner_running",plannerRunning); put(o,"planner_iteration",plannerIteration); put(o,"planner_phase",plannerPhase);','put(o,"planner_running",plannerRunning); put(o,"planner_iteration",plannerIteration); put(o,"planner_phase",plannerPhase); put(o,"remote_telemetry_posts",remoteTelemetryPosts);',1)

# Telemetry/config lineage.
s=s.replace("TelemetryConfigV71","TelemetryConfigV72")
ACT.write_text(s)
assert OLD.exists();OLD.unlink()
cfg=(PKG/"TelemetryConfigV71.java").read_text()
(PKG/"TelemetryConfigV72.java").write_text(cfg.replace("TelemetryConfigV71","TelemetryConfigV72"))
(PKG/"TelemetryConfigV71.java").unlink()

# Version / launcher identity; registered Accessibility remains V51.
g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+72\b","versionCode 73",gs);gs=gs.replace("0.69-stable-diag-semantic-planner-parser-v2","0.70-stable-diag-semantic-planner-consolidated-audit");g.write_text(gs)
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorPlannerCoreV71Activity","OrchestratorPlannerCoreV72Activity");assert "ControlPlaneAccessibilityServiceV51" in ms and "@xml/cp_accessibility_service_v51" in ms
for v in range(52,73):assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
mf.write_text(ms)

# Consolidated hard gates.
out=ACT.read_text()
for required in [
    "PUZZLE_UNKNOWN_AT_BUILD_TIME","CONTROL_EVENT_DRIVEN_NO_FIXED_DELAY_POLL_TIMEOUT","WebMessagePort","MutationObserver",
    "WAIT_PLANNER_CONTENT_READY","PASS_PLANNER_SEMANTIC_CONTENT_HYDRATED","composer_resolution_mode","prompt-textarea",
    "PLANNER_RESPONSE_READY","PLAN_ACCEPTED","TARGET_ROUTE_PLUS_ASSISTANT_EVENT","WRAPPED_ONE_VALID_ACTION",
    "diagnosticRing","shouldRemoteEmit","remote_telemetry_posts","CONTROL_READ_FAILED_FAIL_CLOSED",
    "PASS_RESPONSE_COMPLETE_BY_ASSISTANT_ACTION_RECEIPT","PASS_PLANNER_DONE_RETURNED_TO_MAIN","TelemetryConfigV72"
]:assert required in out,required
for forbidden in [
    "postDelayed","Thread.sleep","setTimeout(","setInterval(","SAMPLE_MS","SEND_POLL_MS","RESPONSE_TIMEOUT_MS",
    "ScheduledExecutorService","TimerTask","pollPlannerNormalHome","pollPlannerTempReceipt","pollAutoComposerReceipt",
    "pollAutoSendReceipt","pollAutoResponse","pollPlannerNavReceipt","pollSendReceipt","confirmAutoSendReceipt",
    "elementFromPoint","document.evaluate","dispatchTouchEvent(","performClick(","ACTION_SET_PROGRESS","CookieManager",
    "getCookie(","addJavascriptInterface","[contenteditable=true]","responseArmedAtMs","responseStableHits","responseTimeoutEmitted"
]:assert forbidden not in out,forbidden
assert out.count('.click();')==2,out.count('.click();')
assert "Tehran" not in out and "تهران" not in out
# Prompt source should use Java quote escapes only, not output literal backslash-quotes.
assert 'Allowed actions: {\\"version\\":1' in out
assert 'Allowed actions: {\\\\\\"version' not in out
print("PASS v0.70 consolidated audit: hydration + composer resolver + re-entry guard + receipt fallback + event bridge + parser/prompt + bounded telemetry; strict zero-clock control")
