#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.81: observability/termination repair only.
# Preserve v0.80 semantic selection, calibrated actuator order, assistant-bound
# claim, event-driven pre-effect recovery, geometry-as-transport-only rule,
# exactly-once effect semantics, and no-replay guarantees.
runpy.run_path("ci/generate_chatgpt_webview_v82_calibrated_actuator_resource_fix1.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorResourceToolsV82Activity.java"
ACT=PKG/"OrchestratorResourceToolsV83Activity.java"
s=OLD.read_text()

def replace_once(old,new,label):
    global s
    n=s.count(old)
    assert n==1,(label,n)
    s=s.replace(old,new,1)

def replace_method_bool(name,body):
    global s
    pat=rf'    private boolean {re.escape(name)}\([^\n]*\)\{{.*?\n    \}}\n'
    m=re.search(pat,s,re.S)
    assert m,(name,"not found")
    s=s[:m.start()]+body+s[m.end():]

# Identity only; internal v0.80 method/state names remain unchanged to minimize
# behavioral scope. Accessibility V82 public methods are intentionally reused.
s=s.replace("OrchestratorResourceToolsV82Activity","OrchestratorResourceToolsV83Activity")
s=s.replace("TelemetryConfigV82","TelemetryConfigV83")
s=s.replace('SCHEMA="cp-v82-calibrated-actuator-resource-v1"','SCHEMA="cp-v83-resource-observable-terminal-v1"')
s=s.replace('SCENARIO="calibrated-actuator-toctou-safe-resource"','SCENARIO="resource-observable-terminal-calibrated-actuator"')
s=s.replace('getSharedPreferences("cp_v82_calibrated_actuator_resource",MODE_PRIVATE)','getSharedPreferences("cp_v83_resource_observable_terminal",MODE_PRIVATE)')
s=s.replace('testId="cp80-"+UUID.randomUUID();','testId="cp81-"+UUID.randomUUID();')
s=s.replace('"resource_v82_','"resource_v83_')
s=s.replace('"resource-v82-','"resource-v83-')
s=s.replace('v0.80 Calibrated actuator Resource acceptance ready.','v0.81 Observable terminal Resource acceptance ready.')

# Explicit lifecycle routing: focused Resource/Calibration transactions are
# remotely emitted by phase, not by English error substrings.
old_should=re.search(r'    private boolean shouldRemoteEmit\(String phase,String classification,JSONObject state\)\{.*?\n    \}\n',s,re.S)
assert old_should,"shouldRemoteEmit"
new_should=r'''    private boolean isResourceLifecycleV83(String phase){
        return "RESOURCE_ACTION".equals(phase)||"ACTUATOR_CALIBRATION".equals(phase)||"RESOURCE_DISCOVERY".equals(phase)||"DURABLE_CLAIM".equals(phase);
    }

    private boolean isResourceTerminalV83(String phase,String classification){
        String c=classification==null?"":classification;
        if("ACTUATOR_CALIBRATION".equals(phase))return "ACTUATOR_CALIBRATION_SETUP_FAILED".equals(c)||"ACTUATOR_CALIBRATION_FAILED_ALL_PUBLIC_PATHS".equals(c);
        if("RESOURCE_DISCOVERY".equals(phase))return "RESOURCE_ACTION_BLOCKED_NO_UNIQUE_ASSISTANT_LOCAL_RESOURCE".equals(c);
        if("DURABLE_CLAIM".equals(phase))return "RESOURCE_ACTION_CLAIM_COMMIT_FAILED".equals(c);
        if(!"RESOURCE_ACTION".equals(phase))return false;
        String[] terminal={
            "RESOURCE_ACTION_BLOCKED_BUSY",
            "RESOURCE_ACTION_BLOCKED_UNSUPPORTED_CURRENT_ORIGIN",
            "RESOURCE_ACTION_PRE_EFFECT_TARGET_TIMEOUT_NO_ACTION",
            "RESOURCE_ACTION_ABORTED_STALE_CLAIM_PRE_EFFECT",
            "RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_CHANGED_PRE_EFFECT",
            "RESOURCE_ACTION_ABORTED_DOCUMENT_CHANGED_PRE_EFFECT",
            "RESOURCE_ACTION_BLOCKED_AMBIGUOUS_FRESH_TARGET",
            "RESOURCE_ACTION_BLOCKED_INVALID_CERTIFIED_GEOMETRY",
            "RESOURCE_ACTION_BLOCKED_NO_CALIBRATED_ACTUATOR",
            "RESOURCE_NATIVE_TOUCH_DISPATCH_UNCERTAIN_NO_REPLAY",
            "RESOURCE_ACTION_MISDISPATCHED_NONRESOURCE_UI",
            "RESOURCE_ACTION_UNCERTAIN_NEW_WINDOW_SETUP_FAILED_NO_REPLAY",
            "RESOURCE_ACTION_UNCERTAIN_NEW_WINDOW_CLOSED_NO_EXTERNAL_RECEIPT",
            "RESOURCE_ACTION_UNCERTAIN_UNSUPPORTED_RESOLVED_SCHEME_NO_REPLAY",
            "RESOURCE_ACTION_UNCERTAIN_SAME_ORIGIN_TERMINAL_NO_EXTERNAL_RECEIPT",
            "RESOURCE_EXTERNAL_URL_RECEIPT_OPEN_INTENT_FAILED_NO_REPLAY",
            "PASS_RESOURCE_EXTERNAL_URL_RECEIPT_OPEN_INTENT_DISPATCHED",
            "PASS_RESOURCE_DOWNLOAD_CALLBACK_RECEIPT",
            "RESOURCE_ACTION_UNCERTAIN_EFFECT_DISPATCHED_NO_RECEIPT_NO_REPLAY",
            "RESOURCE_ACTION_UNCERTAIN_NEW_WINDOW_BOOTSTRAP_NO_DESTINATION_NO_REPLAY"
        };
        for(String x:terminal)if(x.equals(c))return true;
        return false;
    }

    private boolean shouldRemoteEmit(String phase,String classification,JSONObject state){
        if(isResourceLifecycleV83(phase))return true;
        if("LEARN_FINISHED".equals(phase)||"PLANNER_STARTED".equals(phase)||"PLANNER_PLAN".equals(phase)||"PLANNER_ACTION_EXECUTION".equals(phase)||"PLANNER_OBSERVATION".equals(phase)||"PLANNER_FINAL".equals(phase)||"PLANNER_STOP".equals(phase))return true;
        if("AUTO_RESPONSE_RECEIPT".equals(phase)&&"TARGET_MESSAGE".equals(state.optString("purpose","")))return true;
        String c=classification==null?"":classification;
        return c.contains("FAILED")||c.contains("UNCERTAIN")||c.contains("BLOCKED")||c.contains("INVALID");
    }
'''
s=s[:old_should.start()]+new_should+s[old_should.end():]

# Mark lifecycle/terminal explicitly in each telemetry envelope.
old='put(o,"seq",telemetrySeq++); put(o,"timestamp_epoch_ms",System.currentTimeMillis()); put(o,"phase",phase); put(o,"classification",classification);'
new='put(o,"seq",telemetrySeq++); put(o,"timestamp_epoch_ms",System.currentTimeMillis()); put(o,"phase",phase); put(o,"classification",classification); put(o,"resource_lifecycle",isResourceLifecycleV83(phase)); put(o,"terminal",isResourceTerminalV83(phase,classification));'
replace_once(old,new,"emit envelope")

# Make terminal evidence include actuator/effect state before clear/reset.
old='JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"uncertain_effect",uncertain);put(st,"new_window_observed",resourceV82NewWindowObserved);put(st,"click_confirmed",resourceV82ClickConfirmed);put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);'
new='JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"actuator",resourceV82Actuator);put(st,"effect_dispatched",resourceV82EffectDispatched);put(st,"uncertain_effect",uncertain);put(st,"new_window_observed",resourceV82NewWindowObserved);put(st,"click_confirmed",resourceV82ClickConfirmed);put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);'
replace_once(old,new,"terminal evidence")

# Clearing a terminal invalidates any pending fail-closed deadline.
old='resourceV82PreEffectPending=false;resourceV82DriveInFlight=false;resourceV82EffectDispatched=false;'
new='++resourceV82TimeoutSerial;resourceV82PreEffectPending=false;resourceV82DriveInFlight=false;resourceV82EffectDispatched=false;'
replace_once(old,new,"terminal timer invalidation")

# Add a fail-closed post-effect receipt deadline. It is never readiness/success
# authority: it only converts indefinite waiting into an uncertain no-replay terminal.
insert=s.index('    private void driveResourceV82OnObservedState(String reason){\n')
helper=r'''    private void armResourceReceiptDeadlineV83(String actuator){
        final long deadline=++resourceV82TimeoutSerial;
        JSONObject armed=baseState();put(armed,"actuator",actuator);put(armed,"effect_dispatched",true);put(armed,"deadline_role","FAIL_CLOSED_TERMINATION_ONLY");put(armed,"raw_url_remote",false);put(armed,"raw_text_remote",false);put(armed,"raw_html_remote",false);
        emit("RESOURCE_ACTION","RESOURCE_POST_EFFECT_RECEIPT_DEADLINE_ARMED",armed);
        resourceV82Handler.postDelayed(()->{
            if(resourceV82Finalized||!resourceV82EffectDispatched||!resourceNavigationPending||deadline!=resourceV82TimeoutSerial)return;
            if(resourceV82NewWindowObserved){
                terminalResourceV82("NEW_WINDOW_BOOTSTRAP_NO_DESTINATION_NO_REPLAY","RESOURCE_ACTION_UNCERTAIN_NEW_WINDOW_BOOTSTRAP_NO_DESTINATION_NO_REPLAY","Resource opened a new-window/bootstrap path but no destination receipt arrived; no replay.",true);
            }else{
                terminalResourceV82("EFFECT_DISPATCHED_NO_RECEIPT_NO_REPLAY","RESOURCE_ACTION_UNCERTAIN_EFFECT_DISPATCHED_NO_RECEIPT_NO_REPLAY","Resource effect was dispatched but no acceptable receipt arrived; no replay.",true);
            }
        },6000L);
    }

'''
s=s[:insert]+helper+s[insert:]

# After each successful effect dispatch, arm the new receipt deadline. Existing
# effect and receipt semantics are otherwise unchanged.
old='resourceNavigationPending=true;++resourceV82TimeoutSerial;pageUiDispatches++;pageUiWrites++;emit("RESOURCE_ACTION","PASS_RESOURCE_JS_CERTIFY_AND_CLICK_SAME_TASK_WAITING_RECEIPT",st);if(!resourceV82Finalized)status.setText("Resource acted once with calibrated JS actuator; waiting for receipt.");return;'
new='resourceNavigationPending=true;pageUiDispatches++;pageUiWrites++;emit("RESOURCE_ACTION","PASS_RESOURCE_JS_CERTIFY_AND_CLICK_SAME_TASK_WAITING_RECEIPT",st);armResourceReceiptDeadlineV83(actuator);if(!resourceV82Finalized)status.setText("Resource acted once with calibrated JS actuator; waiting for receipt.");return;'
replace_once(old,new,"JS receipt deadline")

old='resourceNavigationPending=true;++resourceV82TimeoutSerial;pageUiDispatches++;pageUiWrites++;emit("RESOURCE_ACTION","PASS_RESOURCE_ACCESSIBILITY_ACTION_DISPATCHED_WAITING_RECEIPT",st);status.setText("Resource acted once with calibrated accessibility actuator; waiting for receipt.");return;'
new='resourceNavigationPending=true;pageUiDispatches++;pageUiWrites++;emit("RESOURCE_ACTION","PASS_RESOURCE_ACCESSIBILITY_ACTION_DISPATCHED_WAITING_RECEIPT",st);armResourceReceiptDeadlineV83(actuator);status.setText("Resource acted once with calibrated accessibility actuator; waiting for receipt.");return;'
replace_once(old,new,"Accessibility receipt deadline")

old='resourceNavigationPending=true;++resourceV82TimeoutSerial;pageUiDispatches++;pageUiWrites++;put(st,"down_dispatched",down);put(st,"up_dispatched",up);emit("RESOURCE_ACTION",down&&up?"PASS_RESOURCE_NATIVE_TOUCH_DISPATCHED_WAITING_RECEIPT":"RESOURCE_NATIVE_TOUCH_DISPATCH_UNCERTAIN_NO_REPLAY",st);if(!down||!up){resourceV82Finalized=true;prefs.edit().putString("resource_v83_claim_status","NATIVE_TOUCH_DISPATCH_UNCERTAIN_NO_REPLAY").commit();status.setText("Native touch dispatch uncertain; no replay.");clearResourceV82TerminalState();}else status.setText("Resource acted once with calibrated native-touch actuator; waiting for receipt.");return;'
new='resourceNavigationPending=true;pageUiDispatches++;pageUiWrites++;put(st,"down_dispatched",down);put(st,"up_dispatched",up);emit("RESOURCE_ACTION",down&&up?"PASS_RESOURCE_NATIVE_TOUCH_DISPATCHED_WAITING_RECEIPT":"RESOURCE_NATIVE_TOUCH_DISPATCH_UNCERTAIN_NO_REPLAY",st);if(!down||!up){resourceV82Finalized=true;prefs.edit().putString("resource_v83_claim_status","NATIVE_TOUCH_DISPATCH_UNCERTAIN_NO_REPLAY").commit();status.setText("Native touch dispatch uncertain; no replay.");clearResourceV82TerminalState();}else{armResourceReceiptDeadlineV83(actuator);status.setText("Resource acted once with calibrated native-touch actuator; waiting for receipt.");}return;'
replace_once(old,new,"Native receipt deadline")

ACT.write_text(s);OLD.unlink()
old_cfg=PKG/"TelemetryConfigV82.java";new_cfg=PKG/"TelemetryConfigV83.java";assert old_cfg.exists();new_cfg.write_text(old_cfg.read_text().replace("TelemetryConfigV82","TelemetryConfigV83"));old_cfg.unlink()

g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+83\b","versionCode 84",gs);gs=gs.replace("0.80-stable-diag-calibrated-actuator-resource","0.81-stable-diag-resource-observable-terminal");g.write_text(gs)
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorResourceToolsV82Activity","OrchestratorResourceToolsV83Activity");mf.write_text(ms)

out=ACT.read_text()
required=[
    'SCHEMA="cp-v83-resource-observable-terminal-v1"',
    'SCENARIO="resource-observable-terminal-calibrated-actuator"',
    'isResourceLifecycleV83','isResourceTerminalV83','resource_lifecycle','terminal',
    'RESOURCE_ACTION_ATTEMPTED','ACTUATOR_CALIBRATION_STARTED','PASS_ACTUATOR_CALIBRATION_SELECTED',
    'PASS_ASSISTANT_LOCAL_RESOURCE_UNIQUE_ADMITTED','CLAIMED_BEFORE_RESOURCE_ACTION',
    'RESOURCE_TARGET_TRANSIENTLY_ABSENT_WAITING_EVENT','RESOURCE_ACTION_PRE_EFFECT_TARGET_TIMEOUT_NO_ACTION',
    'RESOURCE_ACTION_ABORTED_STALE_CLAIM_PRE_EFFECT','RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_CHANGED_PRE_EFFECT',
    'PASS_RESOURCE_JS_CERTIFY_AND_CLICK_SAME_TASK_WAITING_RECEIPT',
    'PASS_RESOURCE_ACCESSIBILITY_ACTION_DISPATCHED_WAITING_RECEIPT',
    'PASS_RESOURCE_NATIVE_TOUCH_DISPATCHED_WAITING_RECEIPT',
    'RESOURCE_POST_EFFECT_RECEIPT_DEADLINE_ARMED',
    'RESOURCE_ACTION_UNCERTAIN_EFFECT_DISPATCHED_NO_RECEIPT_NO_REPLAY',
    'RESOURCE_ACTION_UNCERTAIN_NEW_WINDOW_BOOTSTRAP_NO_DESTINATION_NO_REPLAY',
    'FAIL_CLOSED_TERMINATION_ONLY','armResourceReceiptDeadlineV83',
    'geometry_role','ACTUATION_TRANSPORT_ONLY','TelemetryConfigV83'
]
for x in required: assert x in out,x
for bad in ['elementFromPoint','document.evaluate','XPathResult','findElementsBy','getCookie(','CookieManager','addJavascriptInterface','Thread.sleep','ScheduledExecutorService','TimerTask']:
    assert bad not in out,bad
assert 'if(isResourceLifecycleV83(phase))return true;' in out
assert out.count('armResourceReceiptDeadlineV83(actuator)')==3,out.count('armResourceReceiptDeadlineV83(actuator)')
assert out.count('dispatchTouchEvent(')==4,out.count('dispatchTouchEvent(')
assert 'versionCode 84' in g.read_text()
assert "versionName '0.81-stable-diag-resource-observable-terminal'" in g.read_text()
assert 'OrchestratorResourceToolsV83Activity' in mf.read_text()
assert 'ControlPlaneAccessibilityServiceV51' in mf.read_text() and '@xml/cp_accessibility_service_v51' in mf.read_text()
print('PASS v0.81 observable-terminal audit: full sanitized Resource lifecycle remote, explicit terminal metadata, post-effect no-receipt fail-closed deadline, v0.80 semantic/actuator guards preserved')
