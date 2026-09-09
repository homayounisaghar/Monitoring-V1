#!/usr/bin/env python3
from pathlib import Path
import runpy,re

runpy.run_path('ci/generate_chatgpt_webview_v92_dashboard_observer_readiness_repair.py',run_name='__main__')
ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
old=PKG/'OrchestratorDashboardV92Activity.java'
new=PKG/'OrchestratorDashboardV93Activity.java'
s=old.read_text()

s=s.replace('public class OrchestratorDashboardV92Activity extends Activity {','public class OrchestratorDashboardV93Activity extends Activity {',1)
s=s.replace('private static final String SCHEMA="cp-v92-dashboard-observer-readiness-repair-v1";','private static final String SCHEMA="cp-v93-dashboard-telemetry-budget-repair-v1";',1)
s=s.replace('private static final String SCENARIO="dashboard-multichat-read-plane-readiness-repair";','private static final String SCENARIO="dashboard-multichat-read-plane-telemetry-budget-repair";',1)
s=s.replace('private final String testId="cp891-"+UUID.randomUUID();','private final String testId="cp892-"+UUID.randomUUID();',1)
s=s.replace('TelemetryConfigV92','TelemetryConfigV93')

old_retry='''                if((!exact||hydrationPending)&&retry<MAX_READY_RETRIES){\n                    retry++;ConversationBindingV91 rb=registry.byId(id);\n                    emit("OBSERVE_RETRY",rb,"UNKNOWN",jsonExtra("scan_generation",g,"retry",retry,"route_receipt",exact,"turn_count",observedTurns,"reason",!exact?"ROUTE_OR_READY_PENDING":"TURN_DOM_NOT_HYDRATED"));\n                    h.postDelayed(()->observe(g,id,path),READY_RETRY_MS);return;\n                }'''
new_retry='''                if((!exact||hydrationPending)&&retry<MAX_READY_RETRIES){\n                    retry++;ConversationBindingV91 rb=registry.byId(id);\n                    if(retry==1)emit("OBSERVE_WAIT_STARTED",rb,"UNKNOWN",jsonExtra("scan_generation",g,"retry_budget",MAX_READY_RETRIES,"route_receipt",exact,"turn_count",observedTurns,"reason",!exact?"ROUTE_OR_READY_PENDING":"TURN_DOM_NOT_HYDRATED"));\n                    h.postDelayed(()->observe(g,id,path),READY_RETRY_MS);return;\n                }'''
assert old_retry in s
s=s.replace(old_retry,new_retry,1)
new.write_text(s)

cfg92=PKG/'TelemetryConfigV92.java'
cfg93=PKG/'TelemetryConfigV93.java'
cs=cfg92.read_text(); assert 'class TelemetryConfigV92' in cs
cs=cs.replace('class TelemetryConfigV92','class TelemetryConfigV93',1)
cs=cs.replace('TelemetryConfigV92()','TelemetryConfigV93()',1)
cfg93.write_text(cs)

man=ROOT/'app/src/main/AndroidManifest.xml'; ms=man.read_text(); assert ms.count('OrchestratorDashboardV92Activity')==1
man.write_text(ms.replace('OrchestratorDashboardV92Activity','OrchestratorDashboardV93Activity',1))
grad=ROOT/'app/build.gradle'; gs=grad.read_text(); assert re.search(r'versionCode\s+93\b',gs); assert '0.89.1-stable-dashboard-observer-readiness-repair' in gs
gs=re.sub(r'versionCode\s+93\b','versionCode 94',gs,1).replace('0.89.1-stable-dashboard-observer-readiness-repair','0.89.2-stable-dashboard-telemetry-budget-repair',1); grad.write_text(gs)

out=new.read_text()
for x in ['OrchestratorDashboardV93Activity','MAX_READY_RETRIES=12','TURN_DOM_NOT_HYDRATED','STALE_FINISH_ROUTE_MISMATCH','OBSERVE_WAIT_STARTED','TelemetryConfigV93','cp-v93-dashboard-telemetry-budget-repair-v1','dashboard_registry_v91.json']:
    assert x in out,x
assert 'emit("OBSERVE_RETRY"' not in out
for bad in ['elementFromPoint','document.evaluate','XPathResult','addJavascriptInterface','CookieManager.getCookie','setDraft','sendCurrentDraft']:
    assert bad not in out,bad
assert '.click()' not in out
assert out.count('worker.loadUrl(')==1
print('Generated v0.89.2 Dashboard telemetry budget repair')
