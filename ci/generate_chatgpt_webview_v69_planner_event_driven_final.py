#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# The first v69 rewrite intentionally asserts if any inherited clock-driven
# control remains. It writes the generated tree before that final gate. Catch
# only that gate, remove the one legacy helper left by v0.65, then re-run the
# complete zero-clock contract here.
try:
    runpy.run_path("ci/generate_chatgpt_webview_v69_planner_event_driven.py", run_name="__main__")
except AssertionError as e:
    assert "postDelayed" in str(e), ("unexpected v69 generator failure",repr(e))

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
ACT=PKG/"OrchestratorPlannerCoreV69Activity.java"
assert ACT.exists()
s=ACT.read_text()

# v0.65 introduced this helper around the old polling loop. v0.67 confirms
# Send receipts directly from DOM events, so the helper is unreachable and must
# not retain a delayed response poll.
pat=r'    private void confirmAutoSendReceipt\([^\n]*\)\{.*?\n    \}\n\n'
s,n=re.subn(pat,'',s,count=1,flags=re.S)
assert n==1,("confirmAutoSendReceipt removal",n)
ACT.write_text(s)

out=ACT.read_text()
for required in [
    "PUZZLE_UNKNOWN_AT_BUILD_TIME","WebMessagePort","MutationObserver","PASS_EVENT_BRIDGE_CHANNEL_CONNECTED",
    "control_event_driven","control_clock_driven","PASS_PAGE_FINISHED_PLUS_EXACT_NORMAL_TEMP_ENTRY_GATE",
    "PASS_FRESH_TEMP_ROOM_EVENT_RECEIPT","PASS_AUTO_COMPOSER_HASH_EVENT_RECEIPT","PASS_AUTO_EXACT_USER_TURN_EVENT_RECEIPT",
    "PASS_RESPONSE_CORRELATED_AUTO_SEND_EVENT_RECEIPT","copy-turn-action-button","PASS_RESPONSE_COMPLETE_BY_ASSISTANT_ACTION_RECEIPT",
    "PASS_PLANNER_RESPONSE_COMPLETE_BY_ACTION_RECEIPT","PASS_TARGET_RESPONSE_COMPLETE_BY_ACTION_RECEIPT",
    "PASS_PLANNER_CHAT_NAVIGATION_EVENT_RECEIPT","CLAIMED_BEFORE_PLANNER_TEMP_ENTRY_CLICK","CLAIMED_BEFORE_AUTO_SEND_CLICK",
    "raw_chat_text_remote","safe_top_inset_px","TelemetryConfigV69"
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
print("PASS v0.67 event-driven final generator: zero fixed-delay/poll/timeout control; event/page/semantic receipts only")
