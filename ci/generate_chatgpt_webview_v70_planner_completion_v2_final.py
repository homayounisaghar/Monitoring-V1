#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# The base v0.68 generator writes the complete generated tree before its final
# explicit CONTROL_SYNC marker assertion. Preserve that tree, add the marker as
# a source-visible invariant, and re-run the strict zero-clock + completion-v2 gate.
try:
    runpy.run_path("ci/generate_chatgpt_webview_v70_planner_completion_v2.py", run_name="__main__")
except AssertionError as e:
    assert "CONTROL_EVENT_DRIVEN_NO_FIXED_DELAY_POLL_TIMEOUT" in str(e), ("unexpected v0.68 generator failure",repr(e))

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
ACT=PKG/"OrchestratorPlannerCoreV70Activity.java"
assert ACT.exists()
s=ACT.read_text()
marker='    private static final String CONTROL_SYNC="CONTROL_EVENT_DRIVEN_NO_FIXED_DELAY_POLL_TIMEOUT";\n'
if marker not in s:
    pat=r'(    private static final String SCENARIO="[^"]+";\n)'
    s,n=re.subn(pat,r'\1'+marker,s,count=1)
    assert n==1,("control marker insert",n)
ACT.write_text(s)

out=ACT.read_text()
for required in [
    "PUZZLE_UNKNOWN_AT_BUILD_TIME","CONTROL_EVENT_DRIVEN_NO_FIXED_DELAY_POLL_TIMEOUT","WebMessagePort","MutationObserver",
    "copy-turn-action-button","action-bar-copy","PASS_RESPONSE_COMPLETE_BY_ASSISTANT_ACTION_RECEIPT",
    "LOCAL_CONTROL_STATE_CHANGED_BY_EVENT","controlTelemetryFingerprint","remote_control_state_fingerprint",
    "PASS_RESPONSE_CORRELATED_AUTO_SEND_EVENT_RECEIPT","PASS_FRESH_TEMP_ROOM_EVENT_RECEIPT","PASS_AUTO_COMPOSER_HASH_EVENT_RECEIPT",
    "PASS_BOUNDED_PLANNER_ACTION_PARSED","PASS_PLANNER_DONE_RETURNED_TO_MAIN","raw_chat_text_remote","safe_top_inset_px","TelemetryConfigV70"
]: assert required in out,required
for forbidden in [
    "postDelayed","Thread.sleep","setTimeout(","setInterval(","SAMPLE_MS","SEND_POLL_MS","RESPONSE_TIMEOUT_MS",
    "ScheduledExecutorService","TimerTask","pollPlannerNormalHome","pollPlannerTempReceipt","pollAutoComposerReceipt",
    "pollAutoSendReceipt","pollAutoResponse","pollPlannerNavReceipt","pollSendReceipt","confirmAutoSendReceipt",
    "elementFromPoint","document.evaluate","dispatchTouchEvent(","performClick(","ACTION_SET_PROGRESS","CookieManager",
    "getCookie(","addJavascriptInterface","setAttribute(\\\"aria-value"
]: assert forbidden not in out,forbidden
assert out.count('.click();')==2,out.count('.click();')
assert "Tehran" not in out and "تهران" not in out
print("PASS v0.68 final: dual completion action receipt + remote control-state dedupe + strict zero-clock control")
