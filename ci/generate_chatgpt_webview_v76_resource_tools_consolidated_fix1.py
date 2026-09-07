#!/usr/bin/env python3
from pathlib import Path
import runpy

# Mechanical compile repair for v0.74. The approved architecture remains unchanged.
# Generate the consolidated source first, then add the Java string-literal escaper
# required by the two resource-action registry lookups.
runpy.run_path("ci/generate_chatgpt_webview_v76_resource_tools_consolidated.py", run_name="__main__")

ACT=Path("runtime_probes/chatgpt-webview-stable-probe/app/src/main/java/com/homayounisaghar/chatgptwebviewprobe/OrchestratorResourceToolsV76Activity.java")
s=ACT.read_text()
assert s.count("js(id)")==2, s.count("js(id)")
s=s.replace("js(id)","jsV76(id)")
needle="    private String resourceActionPrepareV76Js(String id){\n"
assert s.count(needle)==1
helper='''    private String jsV76(String value){
        if(value==null)return "";
        return value.replace("\\\\","\\\\\\\\").replace("'","\\\\'").replace("\\r","\\\\r").replace("\\n","\\\\n");
    }

'''
s=s.replace(needle,helper+needle,1)
ACT.write_text(s)

out=ACT.read_text()
assert "js(id)" not in out
assert out.count("jsV76(id)")==2
assert "private String jsV76(String value)" in out
assert out.count('.click();')==5
for forbidden in [
    'Thread.sleep','setTimeout(','setInterval(','ScheduledExecutorService','TimerTask',
    'elementFromPoint','document.evaluate','dispatchTouchEvent(','performClick(',
    'ACTION_SET_PROGRESS','CookieManager','getCookie(','addJavascriptInterface','XPathResult'
]:
    assert forbidden not in out, forbidden
print("PASS v0.74 fix1: Java resource-action literal escaping patched; architecture unchanged")
