#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.68: preserve v0.67 zero-clock/event-driven control and change only:
# 1) assistant completion receipt recognizes both current action-bar copy testids;
# 2) remote diagnostic RUNTIME_EVENT emission is control-state deduplicated so
#    token-by-token assistant mutations cannot exhaust the collector.
runpy.run_path("ci/generate_chatgpt_webview_v69_planner_event_driven_final.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorPlannerCoreV69Activity.java"
ACT=PKG/"OrchestratorPlannerCoreV70Activity.java"
s=OLD.read_text()

def replace_once(old,new,label):
    global s
    n=s.count(old)
    assert n==1,(label,n)
    s=s.replace(old,new,1)

def replace_method(name,new_body):
    global s
    pat=rf'    private void {re.escape(name)}\([^\n]*\)\{{.*?\n    \}}\n\n'
    m=re.search(pat,s,re.S)
    assert m,(name,"method not found")
    s=s[:m.start()]+new_body+s[m.end():]

# Identity.
s=s.replace("OrchestratorPlannerCoreV69Activity","OrchestratorPlannerCoreV70Activity")
s=re.sub(r'private static final String SCHEMA="[^"]+";', 'private static final String SCHEMA="cp-v70-planner-core-completion-v2-v1";', s, count=1)
s=re.sub(r'private static final String SCENARIO="[^"]+";', 'private static final String SCENARIO="same-apk-semantic-planner-core-completion-v2";', s, count=1)
s=s.replace('getSharedPreferences("cp_v69_planner_core",MODE_PRIVATE)','getSharedPreferences("cp_v70_planner_core",MODE_PRIVATE)')
s=s.replace('testId="cp67-"+UUID.randomUUID();','testId="cp68-"+UUID.randomUUID();')
s=s.replace('status.setText("v0.67 EVENT-DRIVEN Planner ready. Puzzle is unknown at build time.\\nNo fixed-delay/poll/timeout controls: DOM + page + receipt events alone advance automation.");','status.setText("v0.68 EVENT-DRIVEN Planner completion-v2 ready. Puzzle is unknown at build time.\\nNo clock control. Completion accepts current ChatGPT action-bar copy receipts; remote streaming telemetry is deduplicated.");')

# Control-state telemetry fingerprint. Full DOM fingerprint still drives local LEARN trace;
# only remote diagnostic snapshots are deduplicated independently of assistant token churn.
replace_once('    private boolean pendingManualDraftReceipt=false;\n', '    private boolean pendingManualDraftReceipt=false;\n    private String lastControlTelemetryFingerprint="-";\n', 'control telemetry field')
s=s.replace('lastStateFingerprint="-"; lastAssistantHash="-";', 'lastStateFingerprint="-"; lastControlTelemetryFingerprint="-"; lastAssistantHash="-";', 1)

old_final="const F=Array.from(root.querySelectorAll('button[data-testid=copy-turn-action-button]')).filter(e=>V(e)&&!e.hasAttribute('disabled'));finalCount=F.length;if(F.length===1)finalStruct=H([(F[0].tagName||'').toLowerCase(),N(F[0].getAttribute('data-testid')||''),N(F[0].getAttribute('aria-label')||'')].join('|'));"
new_final="const F=Array.from(root.querySelectorAll('button[data-testid=copy-turn-action-button],button[data-testid=action-bar-copy]')).filter(e=>V(e)&&!e.hasAttribute('disabled'));finalCount=F.length;if(F.length===1)finalStruct=H([(F[0].tagName||'').toLowerCase(),N(F[0].getAttribute('data-testid')||''),N(F[0].getAttribute('aria-label')||'')].join('|'));"
replace_once(old_final,new_final,'assistant completion selector v2')

old_on='''    private void onObservedState(JSONObject o,String reason){
        if(!o.optBoolean("success",false))return;int n=++sampleIndex;updateLifecycle(o);String fp=o.optString("state_fingerprint","-");boolean changed=!fp.equals(lastStateFingerprint);
        if(learning&&changed){maybeAutoAnchor(o);appendLocal(o,"EVENT:"+reason);}
        if(changed){JSONObject st=sanitizedState(o);put(st,"event_observation_index",n);put(st,"event_reason_hash",hashNorm(reason));emit("RUNTIME_EVENT","LOCAL_STATE_CHANGED_BY_EVENT",st);}lastStateFingerprint=fp;renderLocal(o);
        if(returnPending&&pageFinishedReady)verifyReturnReceiptFromState(o);
        if(pendingManualDraftReceipt&&pendingDraftHash.equals(o.optString("composer_hash",""))&&o.optInt("composer_candidate_count",0)==1){pendingManualDraftReceipt=false;prefs.edit().putString("claim_status","COMPOSER_WRITE_RECEIPT_CONFIRMED").commit();emit("COMPOSER_WRITE_RECEIPT","PASS_COMPOSER_HASH_RECEIPT",sanitizedState(o));}
        if(sendPending){boolean exact=pendingSendHash.equals(o.optString("last_user_hash",""))&&o.optInt("composer_chars",-1)==0;if(exact){sendPending=false;prefs.edit().putString("claim_status","SEND_RECEIPT_CONFIRMED").commit();emit("SEND_RECEIPT","PASS_EXACT_USER_TURN_EVENT_RECEIPT",sanitizedState(o));armResponseTransaction(o);}}
        if(plannerRunning)drivePlannerFromState(o);
    }

'''
new_on='''    private String controlTelemetryFingerprint(JSONObject o){
        String raw=o.optString("route_class","")+"|"+o.optString("local_path_hash","")+"|"+o.optBoolean("temporary_hint",false)+"|"+
                o.optString("semantic_temp_state","")+"|"+o.optInt("temp_candidate_count",-1)+"|"+o.optInt("turn_count",-1)+"|"+
                o.optString("last_user_hash","-")+"|"+o.optString("composer_hash","-")+"|"+o.optInt("composer_chars",-1)+"|"+
                o.optInt("send_candidate_count",-1)+"|"+o.optInt("assistant_completion_candidate_count",-1)+"|"+lifecycle+"|"+plannerPhase+"|"+
                responseArmed+"|"+responseStarted;
        return hashNorm(raw);
    }

    private void onObservedState(JSONObject o,String reason){
        if(!o.optBoolean("success",false))return;
        int n=++sampleIndex;
        updateLifecycle(o);
        String fp=o.optString("state_fingerprint","-");
        boolean changed=!fp.equals(lastStateFingerprint);
        String cfp=controlTelemetryFingerprint(o);
        boolean controlChanged=!cfp.equals(lastControlTelemetryFingerprint);
        if(learning&&changed){maybeAutoAnchor(o);appendLocal(o,"EVENT:"+reason);}
        if(controlChanged){
            JSONObject st=sanitizedState(o);put(st,"event_observation_index",n);put(st,"event_reason_hash",hashNorm(reason));put(st,"remote_control_state_fingerprint",cfp);
            emit("RUNTIME_EVENT","LOCAL_CONTROL_STATE_CHANGED_BY_EVENT",st);
        }
        lastStateFingerprint=fp;lastControlTelemetryFingerprint=cfp;renderLocal(o);
        if(returnPending&&pageFinishedReady)verifyReturnReceiptFromState(o);
        if(pendingManualDraftReceipt&&pendingDraftHash.equals(o.optString("composer_hash",""))&&o.optInt("composer_candidate_count",0)==1){pendingManualDraftReceipt=false;prefs.edit().putString("claim_status","COMPOSER_WRITE_RECEIPT_CONFIRMED").commit();emit("COMPOSER_WRITE_RECEIPT","PASS_COMPOSER_HASH_RECEIPT",sanitizedState(o));}
        if(sendPending){boolean exact=pendingSendHash.equals(o.optString("last_user_hash",""))&&o.optInt("composer_chars",-1)==0;if(exact){sendPending=false;prefs.edit().putString("claim_status","SEND_RECEIPT_CONFIRMED").commit();emit("SEND_RECEIPT","PASS_EXACT_USER_TURN_EVENT_RECEIPT",sanitizedState(o));armResponseTransaction(o);}}
        if(plannerRunning)drivePlannerFromState(o);
    }

'''
assert s.count(old_on)==1,('onObservedState exact block',s.count(old_on))
s=s.replace(old_on,new_on,1)

# Telemetry/config lineage.
s=s.replace("TelemetryConfigV69","TelemetryConfigV70")
ACT.write_text(s)
assert OLD.exists();OLD.unlink()
cfg=(PKG/"TelemetryConfigV69.java").read_text()
(PKG/"TelemetryConfigV70.java").write_text(cfg.replace("TelemetryConfigV69","TelemetryConfigV70"))
(PKG/"TelemetryConfigV69.java").unlink()

# Version identity.
g=ROOT/"app/build.gradle"
gs=g.read_text();gs=re.sub(r"versionCode\s+70\b","versionCode 71",gs);gs=gs.replace("0.67-stable-diag-semantic-planner-event-driven","0.68-stable-diag-semantic-planner-completion-v2");g.write_text(gs)

# Launcher only; Accessibility remains V51.
m=ROOT/"app/src/main/AndroidManifest.xml";ms=m.read_text().replace("OrchestratorPlannerCoreV69Activity","OrchestratorPlannerCoreV70Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms and "@xml/cp_accessibility_service_v51" in ms
for v in range(52,71):assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

out=ACT.read_text()
for required in [
    "PUZZLE_UNKNOWN_AT_BUILD_TIME","CONTROL_EVENT_DRIVEN_NO_FIXED_DELAY_POLL_TIMEOUT","WebMessagePort","MutationObserver",
    "copy-turn-action-button","action-bar-copy","PASS_RESPONSE_COMPLETE_BY_ASSISTANT_ACTION_RECEIPT",
    "LOCAL_CONTROL_STATE_CHANGED_BY_EVENT","controlTelemetryFingerprint","remote_control_state_fingerprint",
    "PASS_RESPONSE_CORRELATED_AUTO_SEND_EVENT_RECEIPT","PASS_FRESH_TEMP_ROOM_EVENT_RECEIPT","PASS_AUTO_COMPOSER_HASH_EVENT_RECEIPT",
    "PASS_BOUNDED_PLANNER_ACTION_PARSED","PASS_PLANNER_DONE_RETURNED_TO_MAIN","raw_chat_text_remote","safe_top_inset_px","TelemetryConfigV70"
]:assert required in out,required
for forbidden in [
    "postDelayed","Thread.sleep","setTimeout(","setInterval(","SAMPLE_MS","SEND_POLL_MS","RESPONSE_TIMEOUT_MS",
    "ScheduledExecutorService","TimerTask","pollPlannerNormalHome","pollPlannerTempReceipt","pollAutoComposerReceipt",
    "pollAutoSendReceipt","pollAutoResponse","pollPlannerNavReceipt","pollSendReceipt","confirmAutoSendReceipt",
    "elementFromPoint","document.evaluate","dispatchTouchEvent(","performClick(","ACTION_SET_PROGRESS","CookieManager",
    "getCookie(","addJavascriptInterface","setAttribute(\\\"aria-value"
]:assert forbidden not in out,forbidden
assert out.count('.click();')==2,out.count('.click();')
assert "Tehran" not in out and "تهران" not in out
print("PASS v0.68 completion-v2: dual current copy-action receipt, event-driven zero-clock control, remote streaming telemetry deduplicated")
