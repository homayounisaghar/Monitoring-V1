#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# Build from v0.65 exactly, then change only the pre-Temporary entry readiness
# gate. v0.65 real-device evidence showed two Planner attempts reaching HOME
# while document.readyState was only interactive; one click was unobserved and
# one observed click did not transition to Temporary. Never replay. Require a
# complete + stable exact NORMAL signature before the single authorized click.
runpy.run_path("ci/generate_chatgpt_webview_v67_planner_send_receipt_v2.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorPlannerCoreV67Activity.java"
ACT=PKG/"OrchestratorPlannerCoreV68Activity.java"
s=OLD.read_text()

def once(old,new,label):
    global s
    n=s.count(old)
    assert n==1,(label,n)
    s=s.replace(old,new,1)

# Identity.
once("OrchestratorPlannerCoreV67Activity","OrchestratorPlannerCoreV68Activity","activity")
once('SCHEMA="cp-v67-planner-core-send-receipt-v2-v1"','SCHEMA="cp-v68-planner-core-temp-entry-readiness-v1"',"schema")
once('SCENARIO="same-apk-semantic-planner-core-send-receipt-v2"','SCENARIO="same-apk-semantic-planner-core-temp-entry-readiness"',"scenario")
once('getSharedPreferences("cp_v67_planner_core",MODE_PRIVATE)','getSharedPreferences("cp_v68_planner_core",MODE_PRIVATE)',"prefs")
once('testId="cp65-"+UUID.randomUUID();','testId="cp66-"+UUID.randomUUID();',"test id")
once('status.setText("v0.65 Planner Core receipt-v2 ready. Puzzle is unknown at build time.\\nAuto Send prefers exact user-turn receipt and can confirm via correlated response evidence without replay.");','status.setText("v0.66 Planner Core readiness gate ready. Puzzle is unknown at build time.\\nTemporary entry requires two stable exact NORMAL samples after document readyState is complete; no early click or replay.");',"ready")

# The HOME poll now carries a stability counter.
once('h.postDelayed(()->pollPlannerNormalHome(0),700L);','h.postDelayed(()->pollPlannerNormalHome(0,0),700L);','initial home poll')

old='''    private void pollPlannerNormalHome(int attempt){
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
'''
new='''    private void pollPlannerNormalHome(int attempt,int stableHits){
        if(!plannerRunning)return;
        eval(tempStateJs(),o->{
            boolean exact=o.optBoolean("success",false)&&"HOME".equals(o.optString("route_class",""))
                    &&"complete".equals(o.optString("ready",""))
                    &&"NORMAL".equals(o.optString("semantic_temp_state",""))&&o.optInt("temp_candidate_count",0)==1;
            int hits=exact?stableHits+1:0;
            if(exact&&(hits==1||hits==2)){
                JSONObject st=sanitizedTempState(o);put(st,"readiness_stable_hits",hits);put(st,"readiness_required",2);
                emit("PLANNER_TEMP_GATE",hits>=2?"PASS_STABLE_COMPLETE_NORMAL_TEMP_ENTRY_GATE":"COMPLETE_NORMAL_TEMP_ENTRY_CANDIDATE_1_OF_2",st);
            }
            if(hits>=2){plannerEnterFreshTemp(o);return;}
            if(attempt>=MAX_TEMP_POLLS){plannerFail("PLANNER_COMPLETE_NORMAL_TEMP_ENTRY_GATE_UNRESOLVED_ZERO_CLICK");return;}
            if(attempt==0||attempt==10||attempt==20){
                JSONObject st=sanitizedTempState(o);put(st,"readiness_stable_hits",hits);put(st,"readiness_required",2);
                emit("PLANNER_TEMP_GATE","WAIT_READ_ONLY_FOR_COMPLETE_STABLE_NORMAL_TEMP_ENTRY",st);
            }
            h.postDelayed(()->pollPlannerNormalHome(attempt+1,hits),250L);
        });
    }
'''
assert s.count(old)==1,s.count(old)
s=s.replace(old,new,1)

# Telemetry config lineage.
s=s.replace("TelemetryConfigV67","TelemetryConfigV68")
ACT.write_text(s)
assert OLD.exists();OLD.unlink()

cfg=(PKG/"TelemetryConfigV67.java").read_text()
(PKG/"TelemetryConfigV68.java").write_text(cfg.replace("TelemetryConfigV67","TelemetryConfigV68"))
(PKG/"TelemetryConfigV67.java").unlink()

# Version identity.
g=ROOT/"app/build.gradle"
gs=g.read_text();gs=re.sub(r"versionCode\s+68\b","versionCode 69",gs);gs=gs.replace("0.65-stable-diag-semantic-planner-core-send-receipt-v2","0.66-stable-diag-semantic-planner-core-temp-entry-readiness");g.write_text(gs)

# Launcher only; registered Accessibility identity remains V51.
m=ROOT/"app/src/main/AndroidManifest.xml";ms=m.read_text().replace("OrchestratorPlannerCoreV67Activity","OrchestratorPlannerCoreV68Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms and "@xml/cp_accessibility_service_v51" in ms
for v in range(52,69):assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

out=ACT.read_text()
for required in [
    "PUZZLE_UNKNOWN_AT_BUILD_TIME","PASS_STABLE_COMPLETE_NORMAL_TEMP_ENTRY_GATE","COMPLETE_NORMAL_TEMP_ENTRY_CANDIDATE_1_OF_2",
    "WAIT_READ_ONLY_FOR_COMPLETE_STABLE_NORMAL_TEMP_ENTRY","PLANNER_COMPLETE_NORMAL_TEMP_ENTRY_GATE_UNRESOLVED_ZERO_CLICK",
    "PASS_RESPONSE_CORRELATED_AUTO_SEND_RECEIPT","PASS_STABLE_FRESH_TEMP_PLANNER_ROOM_RECEIPT","PASS_BOUNDED_PLANNER_ACTION_PARSED",
    "PASS_PLANNER_DONE_RETURNED_TO_MAIN","PASS_RESPONSE_STREAMING_STARTED_BY_ASSISTANT_DIVERGENCE","PASS_RESPONSE_STABLE_COMPLETE",
    "CLAIMED_BEFORE_PLANNER_TEMP_ENTRY_CLICK","CLAIMED_BEFORE_AUTO_COMPOSER_WRITE","CLAIMED_BEFORE_AUTO_SEND_CLICK",
    "raw_chat_text_remote","safe_top_inset_px","TelemetryConfigV68"
]:assert required in out,required
assert '"complete".equals(o.optString("ready",""))' in out
assert out.count('.click();')==2,out.count('.click();')
for forbidden in ["elementFromPoint","document.evaluate","dispatchTouchEvent(","performClick(","ACTION_SET_PROGRESS","CookieManager","getCookie(","addJavascriptInterface","setAttribute(\\\"aria-value"]:assert forbidden not in out,forbidden
assert "Tehran" not in out and "تهران" not in out
print("generated v0.66 Planner Core Temporary-entry readiness gate; two complete stable exact NORMAL samples required before one click; no early click/replay; Accessibility remains V51")
