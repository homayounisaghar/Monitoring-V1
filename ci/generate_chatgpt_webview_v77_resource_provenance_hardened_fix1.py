#!/usr/bin/env python3
from pathlib import Path
import runpy

# Mechanical compile repair for v0.75. The approved provenance/ownership/action
# architecture is unchanged. The v0.75 generator replaces the whole resolver/action
# block, which also removed the inherited Java string-literal escaping helper.
runpy.run_path("ci/generate_chatgpt_webview_v77_resource_provenance_hardened.py", run_name="__main__")

ACT=Path("runtime_probes/chatgpt-webview-stable-probe/app/src/main/java/com/homayounisaghar/chatgptwebviewprobe/OrchestratorResourceToolsV77Activity.java")
s=ACT.read_text()
needle="    private String resourceActionClickV77Js(String id){\n"
assert s.count(needle)==1, s.count(needle)
assert "private String jsV77(String value)" not in s
helper='''    private String jsV77(String value){
        if(value==null)return "";
        return value.replace("\\\\","\\\\\\\\").replace("'","\\\\'").replace("\\r","\\\\r").replace("\\n","\\\\n");
    }

'''
s=s.replace(needle,helper+needle,1)
ACT.write_text(s)

out=ACT.read_text()
assert "private String jsV77(String value)" in out
assert out.count("jsV77(id)")==1, out.count("jsV77(id)")
assert 'RESOURCE_ACTION_BLOCKED_SEMANTIC_RECERTIFICATION_FAILED' in out
assert 'RESOURCE_ACTION_MISDISPATCHED_NONRESOURCE_UI' in out
assert "prev&&next&&prev.role==='assistant'" in out
assert "if(!da||isComposer(e)){excludedGlobal++;return;}" in out
assert out.count('.click();')==5, out.count('.click();')
for forbidden in [
    'Thread.sleep','setTimeout(','setInterval(','ScheduledExecutorService','TimerTask',
    'elementFromPoint','document.evaluate','dispatchTouchEvent(','performClick(',
    'ACTION_SET_PROGRESS','CookieManager','getCookie(','addJavascriptInterface','XPathResult'
]:
    assert forbidden not in out, forbidden
print("PASS v0.75 fix1: Java literal escaper restored; approved provenance/action semantics unchanged")
