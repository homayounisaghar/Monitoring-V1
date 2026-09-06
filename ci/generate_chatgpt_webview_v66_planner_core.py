#!/usr/bin/env python3
from pathlib import Path
import runpy,re

runpy.run_path("ci/generate_chatgpt_webview_v65_conversation_runtime_lifecycle_v2.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorConversationRuntimeV65Activity.java"
ACT=PKG/"OrchestratorPlannerCoreV66Activity.java"
s=OLD.read_text()

def once(old,new,label):
    global s
    n=s.count(old)
    assert n==1,(label,n)
    s=s.replace(old,new,1)

def method(name,new_body):
    global s
    pat=rf'    private void {re.escape(name)}\([^\n]*\)\{{.*?\n    \}}\n\n'
    m=re.search(pat,s,re.S)
    assert m,(name,"method not found")
    s=s[:m.start()]+new_body+s[m.end():]

# Identity.
once("OrchestratorConversationRuntimeV65Activity","OrchestratorPlannerCoreV66Activity","activity")
once('SCHEMA="cp-v65-conversation-runtime-lifecycle-v2-v1"','SCHEMA="cp-v66-planner-core-v1"',"schema")
once('SCENARIO="conversation-runtime-lifecycle-v2-safe-insets"','SCENARIO="same-apk-semantic-planner-core"',"scenario")
once('getSharedPreferences("cp_v65_conversation_runtime",MODE_PRIVATE)','getSharedPreferences("cp_v66_planner_core",MODE_PRIVATE)',"prefs")
once('testId="cp63-"+UUID.randomUUID();','testId="cp64-"+UUID.randomUUID();',"test id")
once('status.setText("v0.63 Conversation Runtime lifecycle-v2 ready. Raw conversation text stays local.\\nResponse start/end are transaction-correlated; top controls respect runtime safe insets.");','status.setText("v0.64 Planner Core ready. Puzzle is unknown at build time.\\nFINISH automatically enters INTERPRET and runs bounded one-action Planner iterations.");',"ready")

# Imports.
once('import java.io.FileOutputStream;\n','import java.io.FileOutputStream;\nimport java.io.FileInputStream;\nimport java.io.InputStreamReader;\nimport java.io.BufferedReader;\n',"io imports")
once('import java.util.UUID;\n','import java.util.UUID;\nimport java.util.ArrayList;\nimport java.util.LinkedHashMap;\nimport java.util.Map;\n',"util imports")

# Planner constants.
once('    private static final long RESPONSE_TIMEOUT_MS=240000L;\n', '''    private static final long RESPONSE_TIMEOUT_MS=240000L;
    private static final int MAX_PLANNER_ITERATIONS=10;
    private static final int MAX_PLANNER_HISTORY=16;
    private static final int MAX_AUTO_RESPONSE_POLLS=420;
    private static final int MAX_TEMP_POLLS=28;
    private static final int MAX_NAV_POLLS=28;
    private static final int MAX_PLANNER_PROMPT_CHARS=48000;
    private static final int MAX_PLANNER_SEND_CHARS=3000;
    private static final String BLIND_BUILD_MARKER="PUZZLE_UNKNOWN_AT_BUILD_TIME";
''',"planner constants")

# Planner fields.
once('    private int safeTopInsetPx=0;\n    private long startedMs=0L;', '''    private int safeTopInsetPx=0;
    private boolean plannerRunning=false;
    private boolean autoSendPending=false;
    private int plannerIteration=0;
    private int plannerActionCount=0;
    private int plannerTargetSendCount=0;
    private String plannerPhase="IDLE";
    private String autoSendPurpose="NONE";
    private String autoSendExpectedHash="-";
    private String autoSendText="";
    private String plannerAfterNav="NONE";
    private String plannerNavRef="MAIN";
    private String plannerNavPath="";
    private String plannerPendingTargetText="";
    private final ArrayList<String> plannerHistory=new ArrayList<>();
    private final LinkedHashMap<String,String> plannerRefToPath=new LinkedHashMap<>();
    private final LinkedHashMap<String,String> plannerPathToRef=new LinkedHashMap<>();
    private long startedMs=0L;''',"planner fields")

# Add emergency/fallback controls below existing row 2.
anchor='''        root.addView(row2,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(46)));

        draftInput=new EditText(this);'''
insert='''        root.addView(row2,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(46)));

        LinearLayout row3=new LinearLayout(this); row3.setOrientation(LinearLayout.HORIZONTAL);
        Button runPlanner=new Button(this); runPlanner.setText("RUN PLANNER"); runPlanner.setOnClickListener(v->beginPlanner());
        Button stopAuto=new Button(this); stopAuto.setText("STOP AUTO"); stopAuto.setOnClickListener(v->stopPlanner("USER_STOPPED_AUTOMATION"));
        row3.addView(runPlanner,new LinearLayout.LayoutParams(0,dp(42),1f));
        row3.addView(stopAuto,new LinearLayout.LayoutParams(0,dp(42),1f));
        root.addView(row3,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(42)));

        draftInput=new EditText(this);'''
once(anchor,insert,"planner controls")

# START LEARN now captures a run-local MAIN anchor automatically when possible.
method("startLearn", '''    private void startLearn(){
        if(learning||plannerRunning)return;
        clearTraceFile();
        learning=true; sampleIndex=0; traceRecords=0; telemetrySeq=0; pageUiDispatches=0; pageUiWrites=0;
        lastStateFingerprint="-"; lastAssistantHash="-"; assistantStableHits=0; lifecycle="IDLE";
        responseArmed=false; responseStarted=false; responseTimeoutEmitted=false;
        pendingResponseBaselineHash="-"; responseBaselineAssistantHash="-"; responseLastAssistantHash="-";
        responseStableHits=0; responseArmedAtMs=0L;
        plannerRunning=false; autoSendPending=false; plannerIteration=0; plannerActionCount=0; plannerTargetSendCount=0;
        plannerPhase="LEARN"; plannerHistory.clear(); plannerRefToPath.clear(); plannerPathToRef.clear();
        anchorPath=""; anchorHash="-"; prefs.edit().remove("anchor_path").remove("anchor_hash").commit();
        testId="cp64-"+UUID.randomUUID(); startedMs=System.currentTimeMillis();
        eval(readJs(),o->{
            maybeAutoAnchor(o);
            appendLocal(o,"START");
            JSONObject st=sanitizedState(o); put(st,"local_trace_cleared",true); put(st,"blind_build_marker",BLIND_BUILD_MARKER); put(st,"raw_text_remote",false);
            emit("LEARN_STARTED","RUNNING_LOCAL_READ_PLANE_BLIND_BUILD",st);
            status.setText("LEARN active. MAIN chat auto-anchors on the first exact persistent conversation.\\nFINISH will automatically start INTERPRET; raw conversation text stays out of diagnostic telemetry.");
            renderLocal(o);
            h.removeCallbacks(sampler); h.post(sampler);
        });
    }

''')

# FINISH automatically enters INTERPRET.
method("finishLearn", '''    private void finishLearn(){
        if(!learning){if(!plannerRunning)beginPlanner();return;}
        learning=false; h.removeCallbacks(sampler);
        eval(readJs(),o->{
            updateLifecycle(o);
            maybeAutoAnchor(o);
            appendLocal(o,"FINISH");
            JSONObject st=sanitizedState(o); put(st,"trace_records",traceRecords); put(st,"samples",sampleIndex); put(st,"blind_build_marker",BLIND_BUILD_MARKER);
            emit("LEARN_FINISHED","LOCAL_TRACE_READY_FOR_INTERPRET",st);
            status.setText("LEARN finished. Entering INTERPRET automatically. No user copy/paste is required.");
            renderLocal(o);
            h.postDelayed(()->beginPlanner(),250L);
        });
    }

''')

# Make manual/local trace records aware of temporary state and auto-anchor first persistent chat.
once('''    private void appendLocal(JSONObject o,String reason){
        if(traceRecords>=MAX_TRACE_RECORDS)return;
        try{
            JSONObject rec=new JSONObject(); rec.put("reason",reason); rec.put("timestamp_epoch_ms",System.currentTimeMillis());
            rec.put("route_class",o.optString("route_class","")); rec.put("local_path",o.optString("local_path",""));
            rec.put("generation_state",lifecycle);''', '''    private void appendLocal(JSONObject o,String reason){
        if(traceRecords>=MAX_TRACE_RECORDS)return;
        maybeAutoAnchor(o);
        try{
            JSONObject rec=new JSONObject(); rec.put("reason",reason); rec.put("timestamp_epoch_ms",System.currentTimeMillis());
            rec.put("route_class",o.optString("route_class","")); rec.put("local_path",o.optString("local_path","")); rec.put("temporary_hint",o.optBoolean("temporary_hint",false));
            rec.put("generation_state",lifecycle);''',"append local temp")

# Add Temporary hint to read plane. This is local raw state; only the boolean is eligible for telemetry.
once('''            "const path=location.pathname||'/';const sh=S.length===1?H([S[0].tagName.toLowerCase(),N(S[0].getAttribute('role')||'button'),N(S[0].getAttribute('data-testid')||''),N(S[0].getAttribute('aria-label')||'')].join('|')):'-';"+
            "const rows=T.map(x=>x.role+'|'+x.hash).join('~');const fp=H([RC(),H(path),H(N(ct)),S.length,P.length,rows].join('|'));"+
            "return JSON.stringify({success:true,ready:document.readyState,route_class:RC(),local_path:path,local_path_hash:H(path),turn_count:T.length,turns:T,last_user_text:lu?lu.text:'',last_user_hash:lu?lu.hash:'-',last_assistant_text:la?la.text:'',last_assistant_hash:la?la.hash:'-',composer_candidate_count:C.length,composer_text:ct,composer_hash:c?H(N(ct)):'-',composer_chars:ct.length,send_candidate_count:S.length,send_struct_hash:sh,stop_candidate_count:P.length,state_fingerprint:fp});"+''', '''            "const path=location.pathname||'/';const sh=S.length===1?H([S[0].tagName.toLowerCase(),N(S[0].getAttribute('role')||'button'),N(S[0].getAttribute('data-testid')||''),N(S[0].getAttribute('aria-label')||'')].join('|')):'-';"+
            "const urltemp=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));let comptemp=false;for(const e of C){const q=N((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('placeholder')||''));if(q.includes('temporary')||q==='temp'){comptemp=true;break;}}const temphint=urltemp||comptemp;"+
            "const rows=T.map(x=>x.role+'|'+x.hash).join('~');const fp=H([RC(),H(path),H(N(ct)),S.length,P.length,temphint?1:0,rows].join('|'));"+
            "return JSON.stringify({success:true,ready:document.readyState,route_class:RC(),local_path:path,local_path_hash:H(path),temporary_hint:temphint,turn_count:T.length,turns:T,last_user_text:lu?lu.text:'',last_user_hash:lu?lu.hash:'-',last_assistant_text:la?la.text:'',last_assistant_hash:la?la.hash:'-',composer_candidate_count:C.length,composer_text:ct,composer_hash:c?H(N(ct)):'-',composer_chars:ct.length,send_candidate_count:S.length,send_struct_hash:sh,stop_candidate_count:P.length,state_fingerprint:fp});"+''',"read temp hint")

# Sanitized telemetry can include only the boolean Temporary hint, never raw paths/text.
s=s.replace('"success","ready","route_class","local_path_hash","turn_count"','"success","ready","route_class","local_path_hash","temporary_hint","turn_count"')
once('''        put(st,"response_user_hash",pendingSendHash); put(st,"safe_top_inset_px",safeTopInsetPx); put(st,"raw_text_remote",false);''', '''        put(st,"response_user_hash",pendingSendHash); put(st,"safe_top_inset_px",safeTopInsetPx);
        put(st,"planner_running",plannerRunning); put(st,"planner_iteration",plannerIteration); put(st,"planner_action_count",plannerActionCount); put(st,"planner_target_send_count",plannerTargetSendCount); put(st,"planner_phase",plannerPhase); put(st,"raw_text_remote",false);''',"planner sanitized state")

# Insert Planner implementation before clearLocal().
planner_methods=r'''    private void maybeAutoAnchor(JSONObject o){
        if(anchorPath!=null&&anchorPath.matches("^/c/[^/?#]+$"))return;
        String route=o.optString("route_class",""),path=o.optString("local_path",""),ph=o.optString("local_path_hash","-");
        if(!"CONVERSATION".equals(route)||!path.matches("^/c/[^/?#]+$"))return;
        anchorPath=path; anchorHash=ph;
        boolean committed=prefs.edit().putString("anchor_path",anchorPath).putString("anchor_hash",anchorHash).commit();
        JSONObject st=sanitizedState(o); put(st,"anchor_hash",anchorHash); put(st,"anchor_committed",committed);
        emit("ANCHOR",committed?"PASS_AUTO_MAIN_CHAT_ANCHOR_COMMITTED":"AUTO_MAIN_CHAT_ANCHOR_COMMIT_FAILED",st);
    }

    private void beginPlanner(){
        if(learning||plannerRunning)return;
        if(anchorPath==null||!anchorPath.matches("^/c/[^/?#]+$")){
            plannerFail("PLANNER_BLOCKED_NO_PERSISTENT_MAIN_ANCHOR"); return;
        }
        plannerRunning=true; autoSendPending=false; plannerIteration=0; plannerActionCount=0; plannerTargetSendCount=0;
        plannerHistory.clear(); plannerPhase="INTERPRET_START";
        JSONObject st=baseState(); put(st,"anchor_hash",anchorHash); put(st,"blind_build_marker",BLIND_BUILD_MARKER);
        emit("PLANNER_STARTED","INTERPRET_STARTED_BLIND_GENERIC_PLANNER",st);
        status.setText("INTERPRET active. Opening a fresh Temporary Planner room. No user action required.");
        h.postDelayed(()->openFreshPlannerTemp(),200L);
    }

    private void stopPlanner(String why){
        if(!plannerRunning)return;
        plannerRunning=false; autoSendPending=false; plannerPhase="STOPPED";
        JSONObject st=baseState(); put(st,"planner_iteration",plannerIteration); put(st,"planner_action_count",plannerActionCount);
        emit("PLANNER_STOP",why,st); status.setText("Automation stopped: "+why+". No pending action is replayed.");
    }

    private void plannerFail(String why){
        boolean was=plannerRunning; plannerRunning=false; autoSendPending=false; plannerPhase="FAILED";
        JSONObject st=baseState(); put(st,"planner_iteration",plannerIteration); put(st,"planner_action_count",plannerActionCount); put(st,"planner_target_send_count",plannerTargetSendCount); put(st,"blind_build_marker",BLIND_BUILD_MARKER);
        emit("PLANNER_FINAL",why,st); status.setText("Planner stopped fail-closed: "+why+". No ambiguous action is replayed.");
    }

    private void openFreshPlannerTemp(){
        if(!plannerRunning)return;
        if(plannerIteration>=MAX_PLANNER_ITERATIONS){plannerFail("PLANNER_MAX_ITERATIONS_REACHED");return;}
        plannerPhase="NAVIGATE_HOME_FOR_FRESH_TEMP";
        String claimId="planner-home-"+UUID.randomUUID();
        boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","PLANNER_HOME_NAV")
                .putString("claim_status","CLAIMED_BEFORE_PLANNER_HOME_NAV").commit();
        JSONObject st=baseState(); put(st,"claim_committed",committed); put(st,"planner_iteration",plannerIteration);
        emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_PLANNER_HOME_NAVIGATION":"CLAIM_COMMIT_FAILED_NO_NAVIGATION",st);
        if(!committed){plannerFail("PLANNER_HOME_CLAIM_COMMIT_FAILED");return;}
        pageUiDispatches++; pageUiWrites++;
        web.loadUrl("https://chatgpt.com/");
        h.postDelayed(()->pollPlannerNormalHome(0),700L);
    }

    private void pollPlannerNormalHome(int attempt){
        if(!plannerRunning)return;
        eval(tempStateJs(),o->{
            boolean ok=o.optBoolean("success",false)&&"HOME".equals(o.optString("route_class",""))
                    &&"NORMAL".equals(o.optString("semantic_temp_state",""))&&o.optInt("temp_candidate_count",0)==1;
            if(ok){plannerEnterFreshTemp(o);return;}
            if(attempt>=MAX_TEMP_POLLS){plannerFail("PLANNER_NORMAL_TEMP_ENTRY_GATE_UNRESOLVED");return;}
            if(attempt==0||attempt==10||attempt==20)emit("PLANNER_TEMP_GATE","WAIT_READ_ONLY_FOR_EXACT_NORMAL_TEMP_ENTRY",sanitizedTempState(o));
            h.postDelayed(()->pollPlannerNormalHome(attempt+1),250L);
        });
    }

    private void plannerEnterFreshTemp(JSONObject gate){
        if(!plannerRunning)return;
        plannerPhase="ENTER_FRESH_TEMP";
        String claimId="planner-temp-"+UUID.randomUUID();
        boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","PLANNER_TEMP_ENTRY")
                .putString("claim_status","CLAIMED_BEFORE_PLANNER_TEMP_ENTRY").commit();
        JSONObject st=sanitizedTempState(gate); put(st,"claim_committed",committed); put(st,"planner_iteration",plannerIteration);
        emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_PLANNER_TEMP_ENTRY_CLICK":"CLAIM_COMMIT_FAILED_NO_CLICK",st);
        if(!committed){plannerFail("PLANNER_TEMP_ENTRY_CLAIM_FAILED");return;}
        eval(tempClickJs("NORMAL"),a->{
            boolean sent=a.optBoolean("success",false)&&a.optBoolean("dispatched",false)&&a.optBoolean("click_observed",false)&&a.optInt("match_count",0)==1;
            if(sent){pageUiDispatches++;pageUiWrites++;}
            emit("PLANNER_TEMP_ENTRY_DISPATCH",sent?"PASS_EXACT_PLANNER_TEMP_ENTRY_CLICK_DISPATCHED":"PLANNER_TEMP_ENTRY_UNCERTAIN_NO_REPLAY",sanitizedTempAction(a));
            if(!sent){plannerFail("PLANNER_TEMP_ENTRY_UNCERTAIN_NO_REPLAY");return;}
            h.postDelayed(()->pollPlannerTempReceipt(0,0),300L);
        });
    }

    private void pollPlannerTempReceipt(int attempt,int stableHits){
        if(!plannerRunning)return;
        eval(tempStateJs(),o->{
            boolean match=o.optBoolean("success",false)&&"TEMP".equals(o.optString("semantic_temp_state",""))&&o.optInt("temp_candidate_count",0)==1;
            int hits=match?stableHits+1:0;
            if(hits>=2){
                emit("PLANNER_TEMP_RECEIPT","PASS_STABLE_FRESH_TEMP_PLANNER_ROOM_RECEIPT",sanitizedTempState(o));
                plannerPhase="SEND_PLANNER_PACKET";
                String packet=buildPlannerPrompt();
                if(packet==null||packet.length()==0||packet.length()>MAX_PLANNER_PROMPT_CHARS){plannerFail("PLANNER_PACKET_SIZE_INVALID");return;}
                autoWriteAndSend(packet,"PLANNER_PROMPT"); return;
            }
            if(attempt>=MAX_TEMP_POLLS){plannerFail("PLANNER_TEMP_RECEIPT_UNRESOLVED_NO_REPLAY");return;}
            h.postDelayed(()->pollPlannerTempReceipt(attempt+1,hits),250L);
        });
    }

    private void autoWriteAndSend(String text,String purpose){
        if(!plannerRunning||autoSendPending)return;
        if(text==null||text.trim().isEmpty()){plannerFail("AUTO_SEND_EMPTY_TEXT_BLOCKED");return;}
        if("TARGET_MESSAGE".equals(purpose)&&text.length()>MAX_PLANNER_SEND_CHARS){plannerFail("PLANNER_TARGET_SEND_TOO_LONG");return;}
        autoSendPending=true; autoSendPurpose=purpose; autoSendText=text; autoSendExpectedHash=hashNorm(text);
        String claimId="auto-draft-"+UUID.randomUUID();
        boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","AUTO_SET_DRAFT_"+purpose)
                .putString("claim_payload_hash",autoSendExpectedHash).putString("claim_status","CLAIMED_BEFORE_AUTO_COMPOSER_WRITE").commit();
        JSONObject claim=baseState(); put(claim,"purpose",purpose); put(claim,"payload_hash",autoSendExpectedHash); put(claim,"payload_chars",text.length()); put(claim,"claim_committed",committed);
        emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_AUTO_COMPOSER_WRITE":"CLAIM_COMMIT_FAILED_NO_WRITE",claim);
        if(!committed){autoSendPending=false;plannerFail("AUTO_COMPOSER_CLAIM_FAILED");return;}
        eval(setDraftJs(text),o->{
            boolean dispatched=o.optBoolean("success",false)&&o.optBoolean("mutated",false)&&o.optInt("composer_count",0)==1&&autoSendExpectedHash.equals(o.optString("composer_hash",""));
            if(dispatched){pageUiDispatches++;pageUiWrites++;}
            JSONObject st=sanitizedAction(o); put(st,"purpose",purpose); put(st,"expected_hash",autoSendExpectedHash);
            emit("AUTO_COMPOSER_WRITE",dispatched?"PASS_AUTO_SINGLE_COMPOSER_WRITE_DISPATCHED":"AUTO_COMPOSER_WRITE_UNCERTAIN_NO_REPLAY",st);
            if(!dispatched){autoSendPending=false;plannerFail("AUTO_COMPOSER_WRITE_UNCERTAIN_NO_REPLAY");return;}
            h.postDelayed(()->pollAutoComposerReceipt(0),250L);
        });
    }

    private void pollAutoComposerReceipt(int attempt){
        if(!plannerRunning||!autoSendPending)return;
        eval(readJs(),o->{
            boolean receipt=o.optInt("composer_candidate_count",0)==1&&autoSendExpectedHash.equals(o.optString("composer_hash",""));
            if(receipt){
                emit("AUTO_COMPOSER_RECEIPT","PASS_AUTO_COMPOSER_HASH_RECEIPT",sanitizedState(o));
                pendingResponseBaselineHash=o.optString("last_assistant_hash","-");
                pendingSendHash=autoSendExpectedHash;
                claimAutoSendClick(o); return;
            }
            if(attempt>=12){autoSendPending=false;plannerFail("AUTO_COMPOSER_RECEIPT_UNRESOLVED_NO_REPLAY");return;}
            h.postDelayed(()->pollAutoComposerReceipt(attempt+1),250L);
        });
    }

    private void claimAutoSendClick(JSONObject o){
        int cc=o.optInt("composer_candidate_count",0),chars=o.optInt("composer_chars",0),sc=o.optInt("send_candidate_count",0);
        if(cc!=1||chars<=0||sc!=1||!autoSendExpectedHash.equals(o.optString("composer_hash",""))){autoSendPending=false;plannerFail("AUTO_SEND_GATE_NOT_EXACT_ZERO_CLICK");return;}
        String claimId="auto-send-"+UUID.randomUUID();
        boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","AUTO_SEND_"+autoSendPurpose)
                .putString("claim_payload_hash",autoSendExpectedHash).putString("claim_status","CLAIMED_BEFORE_AUTO_SEND_CLICK").commit();
        JSONObject claim=sanitizedState(o); put(claim,"purpose",autoSendPurpose); put(claim,"payload_hash",autoSendExpectedHash); put(claim,"claim_committed",committed);
        emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_AUTO_SEND_CLICK":"CLAIM_COMMIT_FAILED_NO_CLICK",claim);
        if(!committed){autoSendPending=false;plannerFail("AUTO_SEND_CLAIM_FAILED");return;}
        eval(sendJs(autoSendExpectedHash),a->{
            boolean dispatched=a.optBoolean("success",false)&&a.optBoolean("dispatched",false)&&a.optBoolean("click_observed",false)&&a.optInt("send_match_count",0)==1&&autoSendExpectedHash.equals(a.optString("composer_hash",""));
            if(dispatched){pageUiDispatches++;pageUiWrites++;}
            JSONObject st=sanitizedAction(a); put(st,"purpose",autoSendPurpose); put(st,"payload_hash",autoSendExpectedHash);
            emit("AUTO_SEND_DISPATCH",dispatched?"PASS_AUTO_EXACT_SEND_CLICK_DISPATCHED":"AUTO_SEND_CLICK_UNCERTAIN_NO_REPLAY",st);
            if(!dispatched){autoSendPending=false;plannerFail("AUTO_SEND_CLICK_UNCERTAIN_NO_REPLAY");return;}
            h.postDelayed(()->pollAutoSendReceipt(0,0),SEND_POLL_MS);
        });
    }

    private void pollAutoSendReceipt(int attempt,int stableHits){
        if(!plannerRunning||!autoSendPending)return;
        eval(readJs(),o->{
            updateLifecycle(o);
            boolean match=autoSendExpectedHash.equals(o.optString("last_user_hash",""))&&o.optInt("composer_chars",-1)==0;
            int hits=match?stableHits+1:0;
            if(match&&(hits==1||hits==2))emit("AUTO_SEND_RECEIPT",hits>=2?"PASS_AUTO_STABLE_USER_TURN_RECEIPT":"AUTO_USER_TURN_RECEIPT_CANDIDATE_1_OF_2",sanitizedState(o));
            if(hits>=2){
                prefs.edit().putString("claim_status","AUTO_SEND_RECEIPT_CONFIRMED").commit();
                armResponseTransaction(o); plannerPhase="WAIT_"+autoSendPurpose+"_RESPONSE";
                h.postDelayed(()->pollAutoResponse(0),SAMPLE_MS); return;
            }
            if(attempt>=MAX_SEND_POLLS){autoSendPending=false;plannerFail("AUTO_SEND_RECEIPT_UNRESOLVED_NO_REPLAY");return;}
            h.postDelayed(()->pollAutoSendReceipt(attempt+1,hits),SEND_POLL_MS);
        });
    }

    private void pollAutoResponse(int attempt){
        if(!plannerRunning||!autoSendPending)return;
        eval(readJs(),o->{
            updateLifecycle(o);
            boolean complete=!responseArmed&&responseStarted&&"COMPLETE".equals(lifecycle)&&!"-".equals(o.optString("last_assistant_hash","-"));
            if(complete){
                String purpose=autoSendPurpose; autoSendPending=false;
                emit("AUTO_RESPONSE_RECEIPT","PLANNER_PROMPT".equals(purpose)?"PASS_PLANNER_RESPONSE_COMPLETE":"PASS_TARGET_RESPONSE_COMPLETE",sanitizedState(o));
                if("PLANNER_PROMPT".equals(purpose)){handlePlannerResponse(o);return;}
                if("TARGET_MESSAGE".equals(purpose)){plannerTargetSendCount++;recordPlannerObservation(o,"TARGET_RESPONSE_COMPLETE");plannerIteration++;openFreshPlannerTemp();return;}
                plannerFail("AUTO_RESPONSE_UNKNOWN_PURPOSE"); return;
            }
            if(attempt>=MAX_AUTO_RESPONSE_POLLS){autoSendPending=false;plannerFail("AUTO_RESPONSE_TIMEOUT_NO_REPLAY");return;}
            h.postDelayed(()->pollAutoResponse(attempt+1),SAMPLE_MS);
        });
    }

    private void handlePlannerResponse(JSONObject o){
        if(!plannerRunning)return;
        String raw=o.optString("last_assistant_text","").trim();
        String responseHash=o.optString("last_assistant_hash","-");
        JSONObject action=parsePlannerAction(raw);
        if(action==null){JSONObject st=sanitizedState(o);put(st,"planner_response_hash",responseHash);emit("PLANNER_PLAN","PLANNER_RESPONSE_INVALID_JSON_OR_ACTION",st);plannerFail("PLANNER_RESPONSE_INVALID_JSON_OR_ACTION");return;}
        String kind=action.optString("action",""); String ref=action.optString("chat_ref","MAIN"); String text=action.optString("text","");
        plannerActionCount++;
        JSONObject st=sanitizedState(o); put(st,"planner_response_hash",responseHash); put(st,"planner_action",kind); put(st,"planner_target_ref",ref); put(st,"planner_text_hash",text.isEmpty()?"-":hashNorm(text)); put(st,"planner_text_chars",text.length());
        emit("PLANNER_PLAN","PASS_BOUNDED_PLANNER_ACTION_PARSED",st);
        addPlannerHistory(action,"PLAN_ACCEPTED",null);
        executePlannerAction(action);
    }

    private JSONObject parsePlannerAction(String raw){
        try{
            if(raw==null)return null; String x=raw.trim();
            if(x.startsWith("```")){
                int nl=x.indexOf('\n'),end=x.lastIndexOf("```"); if(nl<0||end<=nl)return null; x=x.substring(nl+1,end).trim();
            }
            if(!x.startsWith("{")||!x.endsWith("}"))return null;
            JSONObject a=new JSONObject(x); if(a.optInt("version",-1)!=1)return null;
            String k=a.optString("action","");
            if("GO_MAIN_CHAT".equals(k))return a;
            if("GO_CHAT".equals(k)){String r=a.optString("chat_ref","");return r.matches("^CHAT_[0-9]+$")?a:null;}
            if("READ_LAST_RESPONSE".equals(k)){String r=a.optString("chat_ref","MAIN");return ("MAIN".equals(r)||r.matches("^CHAT_[0-9]+$"))?a:null;}
            if("SEND".equals(k)){String r=a.optString("chat_ref","MAIN"),t=a.optString("text","");return (("MAIN".equals(r)||r.matches("^CHAT_[0-9]+$"))&&!t.trim().isEmpty()&&t.length()<=MAX_PLANNER_SEND_CHARS)?a:null;}
            if("DONE".equals(k))return a;
        }catch(Exception ignored){}
        return null;
    }

    private void executePlannerAction(JSONObject a){
        if(!plannerRunning)return;
        if(plannerActionCount>MAX_PLANNER_ITERATIONS){plannerFail("PLANNER_ACTION_LIMIT_REACHED");return;}
        buildPlannerContext();
        String k=a.optString("action",""),ref=a.optString("chat_ref","MAIN"),text=a.optString("text","");
        if("DONE".equals(k)){navigatePlannerRef("MAIN","DONE","");return;}
        if("GO_MAIN_CHAT".equals(k)){navigatePlannerRef("MAIN","OBSERVE","");return;}
        if("GO_CHAT".equals(k)){navigatePlannerRef(ref,"OBSERVE","");return;}
        if("READ_LAST_RESPONSE".equals(k)){navigatePlannerRef(ref,"OBSERVE","");return;}
        if("SEND".equals(k)){navigatePlannerRef(ref,"SEND",text);return;}
        plannerFail("PLANNER_ACTION_NOT_IMPLEMENTED");
    }

    private void navigatePlannerRef(String ref,String after,String text){
        if(!plannerRunning)return;
        buildPlannerContext();
        String path=plannerRefToPath.get(ref);
        if(path==null||!path.matches("^/c/[^/?#]+$")){plannerFail("PLANNER_CHAT_REF_NOT_AVAILABLE");return;}
        plannerNavRef=ref; plannerNavPath=path; plannerAfterNav=after; plannerPendingTargetText=text;
        eval(readJs(),o->{
            boolean already=path.equals(o.optString("local_path",""))&&"CONVERSATION".equals(o.optString("route_class",""));
            if(already){afterPlannerNavigation(o);return;}
            String claimId="planner-nav-"+UUID.randomUUID();
            boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","PLANNER_CHAT_NAV")
                    .putString("claim_anchor_hash",hashNorm(path)).putString("claim_status","CLAIMED_BEFORE_PLANNER_CHAT_NAV").commit();
            JSONObject st=sanitizedState(o);put(st,"planner_target_ref",ref);put(st,"claim_committed",committed);
            emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_PLANNER_CHAT_NAVIGATION":"CLAIM_COMMIT_FAILED_NO_NAVIGATION",st);
            if(!committed){plannerFail("PLANNER_CHAT_NAV_CLAIM_FAILED");return;}
            pageUiDispatches++;pageUiWrites++;plannerPhase="NAVIGATE_"+ref;
            web.loadUrl("https://chatgpt.com"+path);
            h.postDelayed(()->pollPlannerNavReceipt(0),700L);
        });
    }

    private void pollPlannerNavReceipt(int attempt){
        if(!plannerRunning)return;
        eval(readJs(),o->{
            boolean ok=plannerNavPath.equals(o.optString("local_path",""))&&"CONVERSATION".equals(o.optString("route_class",""));
            if(ok){emit("PLANNER_NAV_RECEIPT","PASS_PLANNER_CHAT_NAVIGATION_RECEIPT",sanitizedState(o));afterPlannerNavigation(o);return;}
            if(attempt>=MAX_NAV_POLLS){plannerFail("PLANNER_CHAT_NAVIGATION_RECEIPT_UNRESOLVED_NO_REPLAY");return;}
            h.postDelayed(()->pollPlannerNavReceipt(attempt+1),250L);
        });
    }

    private void afterPlannerNavigation(JSONObject o){
        if(!plannerRunning)return;
        if("SEND".equals(plannerAfterNav)){
            plannerPhase="EXECUTE_SEND_"+plannerNavRef;
            String t=plannerPendingTargetText; plannerAfterNav="NONE"; plannerPendingTargetText="";
            autoWriteAndSend(t,"TARGET_MESSAGE"); return;
        }
        if("DONE".equals(plannerAfterNav)){
            plannerAfterNav="NONE"; recordPlannerObservation(o,"FINAL_MAIN_RECEIPT");
            plannerRunning=false; plannerPhase="DONE";
            JSONObject st=sanitizedState(o);put(st,"planner_iteration",plannerIteration);put(st,"planner_action_count",plannerActionCount);put(st,"planner_target_send_count",plannerTargetSendCount);put(st,"final_anchor_hash",anchorHash);put(st,"blind_build_marker",BLIND_BUILD_MARKER);
            emit("PLANNER_FINAL","PASS_PLANNER_DONE_RETURNED_TO_MAIN",st);
            status.setText("PLANNER DONE. Returned to MAIN with independent route receipt. You can now return to ChatGPT and ask for telemetry validation."); return;
        }
        plannerAfterNav="NONE"; recordPlannerObservation(o,"ACTION_OBSERVATION"); plannerIteration++; openFreshPlannerTemp();
    }

    private void recordPlannerObservation(JSONObject o,String kind){
        try{
            JSONObject obs=new JSONObject();obs.put("kind",kind);obs.put("iteration",plannerIteration);obs.put("chat_ref",plannerRefForPath(o.optString("local_path","")));
            obs.put("route_class",o.optString("route_class",""));obs.put("temporary_hint",o.optBoolean("temporary_hint",false));obs.put("lifecycle",lifecycle);
            obs.put("last_user_text",clip(o.optString("last_user_text",""),1800));obs.put("last_assistant_text",clip(o.optString("last_assistant_text",""),2600));
            addPlannerHistory(null,kind,obs);
            JSONObject st=sanitizedState(o);put(st,"observation_kind",kind);put(st,"observation_assistant_hash",o.optString("last_assistant_hash","-"));put(st,"planner_target_ref",plannerRefForPath(o.optString("local_path","")));
            emit("PLANNER_OBSERVATION","PASS_LOCAL_OBSERVATION_CAPTURED_FOR_NEXT_ITERATION",st);
        }catch(Exception ignored){}
    }

    private void addPlannerHistory(JSONObject action,String result,JSONObject observation){
        try{
            JSONObject hst=new JSONObject();hst.put("iteration",plannerIteration);hst.put("result",result);
            if(action!=null){hst.put("action",action.optString("action",""));hst.put("chat_ref",action.optString("chat_ref","MAIN"));if(action.has("text"))hst.put("text",clip(action.optString("text",""),MAX_PLANNER_SEND_CHARS));}
            if(observation!=null)hst.put("observation",observation);
            plannerHistory.add(hst.toString());while(plannerHistory.size()>MAX_PLANNER_HISTORY)plannerHistory.remove(0);
        }catch(Exception ignored){}
    }

    private String buildPlannerPrompt(){
        try{
            JSONObject ctx=buildPlannerContext();JSONArray hist=new JSONArray();for(String x:plannerHistory){try{hist.put(new JSONObject(x));}catch(Exception ignored){}}
            ctx.put("execution_history",hist);ctx.put("planner_iteration",plannerIteration);ctx.put("blind_build_marker",BLIND_BUILD_MARKER);
            String rules="You are the semantic control-plane Planner inside the user's existing ChatGPT session. The APK was frozen before the puzzle was known. Solve only from the supplied evidence. Return EXACTLY ONE JSON object and nothing else (no markdown, no prose, no chain-of-thought). Allowed actions: {\\\"version\\\":1,\\\"action\\\":\\\"GO_MAIN_CHAT\\\"}; {\\\"version\\\":1,\\\"action\\\":\\\"GO_CHAT\\\",\\\"chat_ref\\\":\\\"CHAT_1\\\"}; {\\\"version\\\":1,\\\"action\\\":\\\"READ_LAST_RESPONSE\\\",\\\"chat_ref\\\":\\\"MAIN\\\"}; {\\\"version\\\":1,\\\"action\\\":\\\"SEND\\\",\\\"chat_ref\\\":\\\"MAIN\\\",\\\"text\\\":\\\"message\\\"}; {\\\"version\\\":1,\\\"action\\\":\\\"DONE\\\"}. Choose only one action. Never invent a chat_ref. SEND only if the semantic task requires a new message. If the demonstrated task is complete, emit DONE. Treat Temporary snapshots as evidence only; they are not navigable chat_refs. CONTEXT=";
            String p=rules+ctx.toString();return p.length()<=MAX_PLANNER_PROMPT_CHARS?p:"";
        }catch(Exception e){return "";}
    }

    private JSONObject buildPlannerContext(){
        JSONObject ctx=new JSONObject();plannerRefToPath.clear();plannerPathToRef.clear();
        try{
            plannerRefToPath.put("MAIN",anchorPath);plannerPathToRef.put(anchorPath,"MAIN");
            LinkedHashMap<String,JSONArray> latest=new LinkedHashMap<>();JSONArray timeline=new JSONArray();JSONArray temp=new JSONArray();
            File f=traceFile();if(f.exists()){
                try(BufferedReader br=new BufferedReader(new InputStreamReader(new FileInputStream(f),StandardCharsets.UTF_8))){
                    String line;int idx=0;while((line=br.readLine())!=null){if(line.trim().isEmpty())continue;JSONObject r=new JSONObject(line);String path=r.optString("local_path",""),route=r.optString("route_class","");String ref="-";
                        if("CONVERSATION".equals(route)&&path.matches("^/c/[^/?#]+$")){ref=plannerRefForPath(path);JSONArray turns=r.optJSONArray("turns");if(turns!=null)latest.put(ref,compactTurns(turns,8,1200));}
                        JSONObject ev=new JSONObject();ev.put("i",idx++);ev.put("reason",r.optString("reason",""));ev.put("chat_ref",ref);ev.put("temporary_hint",r.optBoolean("temporary_hint",false));ev.put("generation_state",r.optString("generation_state",""));timeline.put(ev);
                        if(r.optBoolean("temporary_hint",false)&&r.optJSONArray("turns")!=null){JSONObject ts=new JSONObject();ts.put("reason",r.optString("reason",""));ts.put("turns",compactTurns(r.optJSONArray("turns"),8,1200));temp.put(ts);while(temp.length()>3)removeFirst(temp);}
                    }
                }
            }
            JSONObject chats=new JSONObject();for(Map.Entry<String,JSONArray> e:latest.entrySet()){JSONObject c=new JSONObject();c.put("turns",e.getValue());chats.put(e.getKey(),c);}ctx.put("main_chat_ref","MAIN");ctx.put("known_chats",chats);ctx.put("timeline",timeline);ctx.put("temporary_snapshots",temp);
        }catch(Exception ignored){}
        return ctx;
    }

    private String plannerRefForPath(String path){
        if(path!=null&&path.equals(anchorPath))return "MAIN";
        String r=plannerPathToRef.get(path);if(r!=null)return r;
        if(path==null||!path.matches("^/c/[^/?#]+$"))return "-";
        int n=1;while(plannerRefToPath.containsKey("CHAT_"+n))n++;r="CHAT_"+n;plannerPathToRef.put(path,r);plannerRefToPath.put(r,path);return r;
    }

    private JSONArray compactTurns(JSONArray a,int max,int clipChars){
        JSONArray out=new JSONArray();if(a==null)return out;int start=Math.max(0,a.length()-max);for(int i=start;i<a.length();i++){JSONObject x=a.optJSONObject(i);if(x==null)continue;JSONObject y=new JSONObject();put(y,"role",x.optString("role",""));put(y,"text",clip(x.optString("text",""),clipChars));out.put(y);}return out;
    }

    private void removeFirst(JSONArray a){
        if(a==null||a.length()==0)return;JSONArray b=new JSONArray();for(int i=1;i<a.length();i++)b.put(a.opt(i));while(a.length()>0)a.remove(a.length()-1);for(int i=0;i<b.length();i++)a.put(b.opt(i));
    }

    private JSONObject sanitizedTempState(JSONObject o){
        JSONObject st=baseState();copy(st,o,"success","ready","route_class","url_temp_hint","temp_candidate_count","temp_like_candidate_count","semantic_temp_state","candidate_label_hash","candidate_struct_hash");put(st,"planner_iteration",plannerIteration);return st;
    }

    private JSONObject sanitizedTempAction(JSONObject o){
        JSONObject st=baseState();copy(st,o,"success","reason","match_count","temp_like_count","dispatched","click_observed","label_hash","struct_hash","from_state");put(st,"planner_iteration",plannerIteration);return st;
    }

    private String tempStateJs(){
        return "(function(){try{"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const DS=e=>{const v=N(e.getAttribute('data-state'));if(['active','selected','checked','on'].includes(v))return 'ACTIVE';if(['inactive','unselected','unchecked','off'].includes(v))return 'INACTIVE';if(v==='open')return 'OPEN';if(v==='closed')return 'CLOSED';return v?'OTHER':'NONE';};const RC=()=>{const p=location.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';return 'OTHER_ROUTE';};const SEM=(label,tid)=>{const x=N(label),t=N(tid),z=x+' '+t;if(z.includes('temporary')||x==='temp'||t.includes('temp'))return 'TEMP';return 'OTHER';};"+
            "const q=Array.from(document.querySelectorAll('button,a,[role],[aria-selected],[aria-pressed],[data-state],[data-testid]')).filter(V),T=[];for(const e of q){const tag=(e.tagName||'').toLowerCase(),role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none')),label=e.getAttribute('aria-label')||e.innerText||e.textContent||'',tid=e.getAttribute('data-testid')||'',sem=SEM(label,tid);if(sem!=='TEMP')continue;const lh=H(N(label)),th=H(tid),hc=(e.getAttribute('href')||'')?'OTHER':'NONE',sh=H([tag,role,sem,lh,th,hc].join('|'));T.push({e:e,tag:tag,role:role,lh:lh,th:th,ds:DS(e),sel:e.getAttribute('aria-selected')==='true'?1:0,prs:e.getAttribute('aria-pressed')==='true'?1:0,exp:e.getAttribute('aria-expanded')==='true'?1:0,dis:e.hasAttribute('disabled')?1:0,hc:hc,sh:sh});}"+
            "const urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));const E=T.filter(x=>urlhint?(x.lh==='ae0e16e6'&&x.sh==='34d052a8'):(x.lh==='1a957a52'&&x.sh==='b9c97d1e'));const c=E.length===1?E[0]:null;let sem='UNKNOWN';if(c&&c.tag==='button'&&c.role==='button'&&c.th==='811c9dc5'&&c.ds==='NONE'&&c.sel===0&&c.prs===0&&c.exp===0&&c.dis===0&&c.hc==='NONE'){if(c.lh==='1a957a52'&&c.sh==='b9c97d1e'&&!urlhint)sem='NORMAL';else if(c.lh==='ae0e16e6'&&c.sh==='34d052a8'&&urlhint)sem='TEMP';}return JSON.stringify({success:true,ready:document.readyState,route_class:RC(),url_temp_hint:urlhint,temp_candidate_count:E.length,temp_like_candidate_count:T.length,semantic_temp_state:sem,candidate_label_hash:c?c.lh:'-',candidate_struct_hash:c?c.sh:'-'});"+
            "}catch(e){return JSON.stringify({success:false,semantic_temp_state:'UNKNOWN',temp_candidate_count:0,temp_like_candidate_count:0});}})();";
    }

    private String tempClickJs(String from){
        String label="NORMAL".equals(from)?"1a957a52":"ae0e16e6",struct="NORMAL".equals(from)?"b9c97d1e":"34d052a8";boolean expectUrl="TEMP".equals(from);
        return "(function(){try{const EL='"+label+"',ES='"+struct+"',EU="+(expectUrl?"true":"false")+",FROM='"+from+"';"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const SEM=(label,tid)=>{const x=N(label),t=N(tid),z=x+' '+t;if(z.includes('temporary')||x==='temp'||t.includes('temp'))return 'TEMP';return 'OTHER';};const q=Array.from(document.querySelectorAll('button,a,[role],[aria-selected],[aria-pressed],[data-state],[data-testid]')).filter(V),T=[];for(const e of q){const tag=(e.tagName||'').toLowerCase(),role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none')),label=e.getAttribute('aria-label')||e.innerText||e.textContent||'',tid=e.getAttribute('data-testid')||'',sem=SEM(label,tid);if(sem!=='TEMP')continue;const lh=H(N(label)),th=H(tid),hc=(e.getAttribute('href')||'')?'OTHER':'NONE',sh=H([tag,role,sem,lh,th,hc].join('|'));T.push({e:e,tag:tag,role:role,lh:lh,th:th,ds:N(e.getAttribute('data-state'))||'none',sel:e.getAttribute('aria-selected')==='true'?1:0,prs:e.getAttribute('aria-pressed')==='true'?1:0,exp:e.getAttribute('aria-expanded')==='true'?1:0,dis:e.hasAttribute('disabled')?1:0,hc:hc,sh:sh});}const M=T.filter(x=>x.lh===EL&&x.sh===ES);if(M.length!==1)return JSON.stringify({success:false,reason:'EXACT_SIGNATURE_COUNT',match_count:M.length,temp_like_count:T.length,dispatched:false,click_observed:false});const t=M[0],urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));const clean=t.tag==='button'&&t.role==='button'&&t.th==='811c9dc5'&&t.hc==='NONE'&&t.sel===0&&t.prs===0&&t.exp===0&&t.dis===0&&t.ds==='none';if(!clean||urlhint!==EU)return JSON.stringify({success:false,reason:'STATE_OR_HASH',match_count:1,temp_like_count:T.length,dispatched:false,click_observed:false,label_hash:t.lh,struct_hash:t.sh,from_state:FROM});let observed=false;t.e.addEventListener('click',()=>{observed=true;},{capture:true,once:true});t.e.click();return JSON.stringify({success:true,reason:'ELEMENT_CLICK',match_count:1,temp_like_count:T.length,dispatched:true,click_observed:observed,label_hash:t.lh,struct_hash:t.sh,from_state:FROM});"+
            "}catch(e){return JSON.stringify({success:false,reason:'CLICK_EXCEPTION',match_count:0,dispatched:false,click_observed:false});}})();";
    }

'''
marker='    private void clearLocal(){\n'
assert s.count(marker)==1
s=s.replace(marker,planner_methods+marker,1)

# Planner state is also surfaced in base diagnostics, but never raw packet/response text.
once('''        put(o,"pro_forbidden",true); put(o,"geometry_selection",false); put(o,"raw_html_remote",false); put(o,"raw_url_remote",false); put(o,"raw_chat_text_remote",false); put(o,"cookies_tokens_remote",false); put(o,"safe_top_inset_px",safeTopInsetPx);''', '''        put(o,"pro_forbidden",true); put(o,"geometry_selection",false); put(o,"raw_html_remote",false); put(o,"raw_url_remote",false); put(o,"raw_chat_text_remote",false); put(o,"cookies_tokens_remote",false); put(o,"safe_top_inset_px",safeTopInsetPx);
        put(o,"planner_running",plannerRunning); put(o,"planner_iteration",plannerIteration); put(o,"planner_phase",plannerPhase); put(o,"blind_build_marker",BLIND_BUILD_MARKER);''',"base planner")

# Telemetry config lineage.
s=s.replace("TelemetryConfigV65","TelemetryConfigV66")
ACT.write_text(s)
assert OLD.exists(); OLD.unlink()

cfg=(PKG/"TelemetryConfigV65.java").read_text()
(PKG/"TelemetryConfigV66.java").write_text(cfg.replace("TelemetryConfigV65","TelemetryConfigV66"))
(PKG/"TelemetryConfigV65.java").unlink()

# Version identity.
g=ROOT/"app/build.gradle"
gs=g.read_text();gs=re.sub(r"versionCode\s+66\b","versionCode 67",gs);gs=gs.replace("0.63-stable-diag-conversation-runtime-lifecycle-v2","0.64-stable-diag-semantic-planner-core");g.write_text(gs)

# Launcher only; registered Accessibility identity remains V51.
m=ROOT/"app/src/main/AndroidManifest.xml";ms=m.read_text().replace("OrchestratorConversationRuntimeV65Activity","OrchestratorPlannerCoreV66Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms and "@xml/cp_accessibility_service_v51" in ms
for v in range(52,67):assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

# Build-time safety / blind-generic contracts.
out=ACT.read_text()
for required in [
    "PUZZLE_UNKNOWN_AT_BUILD_TIME","INTERPRET_STARTED_BLIND_GENERIC_PLANNER","PASS_STABLE_FRESH_TEMP_PLANNER_ROOM_RECEIPT",
    "PASS_BOUNDED_PLANNER_ACTION_PARSED","GO_MAIN_CHAT","GO_CHAT","READ_LAST_RESPONSE","TARGET_MESSAGE","PASS_PLANNER_DONE_RETURNED_TO_MAIN",
    "PASS_RESPONSE_TRANSACTION_ARMED_AFTER_SEND_RECEIPT","PASS_RESPONSE_STREAMING_STARTED_BY_ASSISTANT_DIVERGENCE","PASS_RESPONSE_STABLE_COMPLETE",
    "CLAIMED_BEFORE_PLANNER_HOME_NAVIGATION","CLAIMED_BEFORE_PLANNER_TEMP_ENTRY_CLICK","CLAIMED_BEFORE_PLANNER_CHAT_NAVIGATION",
    "CLAIMED_BEFORE_AUTO_COMPOSER_WRITE","CLAIMED_BEFORE_AUTO_SEND_CLICK","raw_chat_text_remote","safe_top_inset_px","TelemetryConfigV66"
]:assert required in out,required
assert out.count('.click();')==2, out.count('.click();')
for forbidden in ["elementFromPoint","document.evaluate","dispatchTouchEvent(","performClick(","ACTION_SET_PROGRESS","CookieManager","getCookie(","addJavascriptInterface","setAttribute(\\\"aria-value"]:assert forbidden not in out,forbidden
assert "Tehran" not in out and "تهران" not in out
print("generated v0.64 same-APK blind semantic Planner core; Temporary planner is stateless across iterations; bounded actions only; Accessibility remains V51")
