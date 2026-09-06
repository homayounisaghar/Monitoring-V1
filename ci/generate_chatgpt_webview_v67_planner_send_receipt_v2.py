#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# Build from the exact v0.64 Planner Core, then change only the autonomous
# Send receipt transaction. Temporary entry, planner grammar, composer write,
# semantic Send click, lifecycle-v2, navigation and privacy contracts remain.
runpy.run_path("ci/generate_chatgpt_webview_v66_planner_core.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorPlannerCoreV66Activity.java"
ACT=PKG/"OrchestratorPlannerCoreV67Activity.java"
s=OLD.read_text()

def once(old,new,label):
    global s
    n=s.count(old)
    assert n==1,(label,n)
    s=s.replace(old,new,1)

# Identity only.
once("OrchestratorPlannerCoreV66Activity","OrchestratorPlannerCoreV67Activity","activity")
once('SCHEMA="cp-v66-planner-core-v1"','SCHEMA="cp-v67-planner-core-send-receipt-v2-v1"',"schema")
once('SCENARIO="same-apk-semantic-planner-core"','SCENARIO="same-apk-semantic-planner-core-send-receipt-v2"',"scenario")
once('getSharedPreferences("cp_v66_planner_core",MODE_PRIVATE)','getSharedPreferences("cp_v67_planner_core",MODE_PRIVATE)',"prefs")
once('testId="cp64-"+UUID.randomUUID();','testId="cp65-"+UUID.randomUUID();',"test id")
once('status.setText("v0.64 Planner Core ready. Puzzle is unknown at build time.\\nFINISH automatically enters INTERPRET and runs bounded one-action Planner iterations.");','status.setText("v0.65 Planner Core receipt-v2 ready. Puzzle is unknown at build time.\\nAuto Send prefers exact user-turn receipt and can confirm via correlated response evidence without replay.");',"ready")

# Receipt-v2 constants/field.
once('    private static final int MAX_AUTO_RESPONSE_POLLS=420;\n', '    private static final int MAX_AUTO_RESPONSE_POLLS=420;\n    private static final int MAX_AUTO_SEND_RECEIPT_POLLS=140;\n', 'receipt poll constant')
once('    private String autoSendText="";\n', '    private String autoSendText="";\n    private String autoSendBaselineUserHash="-";\n', 'baseline user field')

# Capture the pre-Send user hash together with the already-existing assistant baseline.
once('''                pendingResponseBaselineHash=o.optString("last_assistant_hash","-");
                pendingSendHash=autoSendExpectedHash;
                claimAutoSendClick(o); return;''', '''                pendingResponseBaselineHash=o.optString("last_assistant_hash","-");
                autoSendBaselineUserHash=o.optString("last_user_hash","-");
                pendingSendHash=autoSendExpectedHash;
                claimAutoSendClick(o); return;''', 'capture send baselines')

old_method='''    private void pollAutoSendReceipt(int attempt,int stableHits){
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
'''
new_method='''    private void confirmAutoSendReceipt(JSONObject o,String basis){
        JSONObject st=sanitizedState(o); put(st,"receipt_basis",basis); put(st,"expected_user_hash",autoSendExpectedHash);
        put(st,"baseline_user_hash",autoSendBaselineUserHash); put(st,"baseline_assistant_hash",pendingResponseBaselineHash);
        emit("AUTO_SEND_RECEIPT","EXACT_USER_HASH".equals(basis)?"PASS_AUTO_STABLE_USER_TURN_RECEIPT":"PASS_RESPONSE_CORRELATED_AUTO_SEND_RECEIPT",st);
        prefs.edit().putString("claim_status","AUTO_SEND_RECEIPT_CONFIRMED_"+basis).commit();
        armResponseTransaction(o); plannerPhase="WAIT_"+autoSendPurpose+"_RESPONSE";
        h.postDelayed(()->pollAutoResponse(0),SAMPLE_MS);
    }

    private void pollAutoSendReceipt(int attempt,int stableHits){
        if(!plannerRunning||!autoSendPending)return;
        eval(readJs(),o->{
            updateLifecycle(o);
            String observedUser=o.optString("last_user_hash","-");
            String observedAssistant=o.optString("last_assistant_hash","-");
            int composerChars=o.optInt("composer_chars",-1);
            boolean exact=autoSendExpectedHash.equals(observedUser)&&composerChars==0;
            int hits=exact?stableHits+1:0;
            if(exact&&hits==1){
                JSONObject c=sanitizedState(o);put(c,"receipt_basis","EXACT_USER_HASH");put(c,"expected_user_hash",autoSendExpectedHash);
                emit("AUTO_SEND_RECEIPT","AUTO_USER_TURN_RECEIPT_CANDIDATE_1_OF_2",c);
            }
            if(hits>=2){confirmAutoSendReceipt(o,"EXACT_USER_HASH");return;}

            // Some fresh Temporary Planner rooms do not expose the newly submitted
            // user turn through the same data-message-author-role representation.
            // Never replay. Instead accept only transaction-correlated evidence:
            // the exact pre-click composer was dispatched, the composer is now empty,
            // and assistant output diverges from the pre-Send assistant baseline.
            boolean composerCleared=composerChars==0;
            boolean assistantDiverged=!"-".equals(observedAssistant)&&!observedAssistant.equals(pendingResponseBaselineHash);
            boolean userAdvanced=!"-".equals(observedUser)&&!observedUser.equals(autoSendBaselineUserHash);
            boolean freshPlannerTemp="PLANNER_PROMPT".equals(autoSendPurpose)&&"-".equals(pendingResponseBaselineHash)&&o.optBoolean("temporary_hint",false);
            boolean correlated=composerCleared&&assistantDiverged&&(freshPlannerTemp||userAdvanced);
            if(correlated){confirmAutoSendReceipt(o,freshPlannerTemp?"FRESH_TEMP_ASSISTANT_DIVERGENCE":"USER_ADVANCE_PLUS_ASSISTANT_DIVERGENCE");return;}

            if(attempt==0||attempt==12||attempt==36||attempt==72||attempt==108){
                JSONObject w=sanitizedState(o);put(w,"expected_user_hash",autoSendExpectedHash);put(w,"baseline_user_hash",autoSendBaselineUserHash);put(w,"baseline_assistant_hash",pendingResponseBaselineHash);put(w,"receipt_attempt",attempt);put(w,"composer_cleared",composerCleared);put(w,"assistant_diverged",assistantDiverged);put(w,"user_advanced",userAdvanced);
                emit("AUTO_SEND_RECEIPT_WAIT","READ_ONLY_CORRELATED_RECEIPT_POLL_NO_REPLAY",w);
            }
            if(attempt>=MAX_AUTO_SEND_RECEIPT_POLLS){autoSendPending=false;plannerFail("AUTO_SEND_RECEIPT_V2_UNRESOLVED_NO_REPLAY");return;}
            h.postDelayed(()->pollAutoSendReceipt(attempt+1,hits),SEND_POLL_MS);
        });
    }
'''
assert s.count(old_method)==1, s.count(old_method)
s=s.replace(old_method,new_method,1)

# Telemetry config lineage.
s=s.replace("TelemetryConfigV66","TelemetryConfigV67")
ACT.write_text(s)
assert OLD.exists();OLD.unlink()

cfg=(PKG/"TelemetryConfigV66.java").read_text()
(PKG/"TelemetryConfigV67.java").write_text(cfg.replace("TelemetryConfigV66","TelemetryConfigV67"))
(PKG/"TelemetryConfigV66.java").unlink()

# Version identity.
g=ROOT/"app/build.gradle"
gs=g.read_text();gs=re.sub(r"versionCode\s+67\b","versionCode 68",gs);gs=gs.replace("0.64-stable-diag-semantic-planner-core","0.65-stable-diag-semantic-planner-core-send-receipt-v2");g.write_text(gs)

# Launcher only; registered Accessibility identity remains V51.
m=ROOT/"app/src/main/AndroidManifest.xml";ms=m.read_text().replace("OrchestratorPlannerCoreV66Activity","OrchestratorPlannerCoreV67Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms and "@xml/cp_accessibility_service_v51" in ms
for v in range(52,68):assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

out=ACT.read_text()
for required in [
    "PUZZLE_UNKNOWN_AT_BUILD_TIME","PASS_RESPONSE_CORRELATED_AUTO_SEND_RECEIPT","FRESH_TEMP_ASSISTANT_DIVERGENCE",
    "USER_ADVANCE_PLUS_ASSISTANT_DIVERGENCE","READ_ONLY_CORRELATED_RECEIPT_POLL_NO_REPLAY","AUTO_SEND_RECEIPT_V2_UNRESOLVED_NO_REPLAY",
    "MAX_AUTO_SEND_RECEIPT_POLLS=140","PASS_STABLE_FRESH_TEMP_PLANNER_ROOM_RECEIPT","PASS_BOUNDED_PLANNER_ACTION_PARSED",
    "PASS_PLANNER_DONE_RETURNED_TO_MAIN","PASS_RESPONSE_STREAMING_STARTED_BY_ASSISTANT_DIVERGENCE","PASS_RESPONSE_STABLE_COMPLETE",
    "CLAIMED_BEFORE_AUTO_COMPOSER_WRITE","CLAIMED_BEFORE_AUTO_SEND_CLICK","raw_chat_text_remote","safe_top_inset_px","TelemetryConfigV67"
]: assert required in out,required
assert out.count('.click();')==2,out.count('.click();')
for forbidden in ["elementFromPoint","document.evaluate","dispatchTouchEvent(","performClick(","ACTION_SET_PROGRESS","CookieManager","getCookie(","addJavascriptInterface","setAttribute(\\\"aria-value"]:assert forbidden not in out,forbidden
assert "Tehran" not in out and "تهران" not in out
print("generated v0.65 Planner Core send-receipt-v2; exact user hash preferred, response-correlated fallback, no replay; Accessibility remains V51")
