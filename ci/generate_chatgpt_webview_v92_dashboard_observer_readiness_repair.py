#!/usr/bin/env python3
from pathlib import Path
import runpy,re

runpy.run_path('ci/generate_chatgpt_webview_v91_dashboard_observer_registry.py',run_name='__main__')
ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
old=PKG/'OrchestratorDashboardV91Activity.java'
new=PKG/'OrchestratorDashboardV92Activity.java'
s=old.read_text()
s=s.replace('import android.os.Looper;','import android.os.Looper;\nimport android.net.Uri;',1)
s=s.replace('public class OrchestratorDashboardV91Activity extends Activity {','public class OrchestratorDashboardV92Activity extends Activity {',1)
s=s.replace('private static final String SCHEMA="cp-v91-dashboard-observer-registry-v1";','private static final String SCHEMA="cp-v92-dashboard-observer-readiness-repair-v1";',1)
s=s.replace('private static final String SCENARIO="dashboard-multichat-read-plane";','private static final String SCENARIO="dashboard-multichat-read-plane-readiness-repair";',1)
s=s.replace('private static final int MAX_READY_RETRIES=4;','private static final int MAX_READY_RETRIES=12;',1)
s=s.replace('private static final long READY_RETRY_MS=450L;','private static final long READY_RETRY_MS=500L;',1)
s=s.replace('private final String testId="cp89-"+UUID.randomUUID();','private final String testId="cp891-"+UUID.randomUUID();',1)
s=s.replace('TelemetryConfigV91','TelemetryConfigV92')
old_finish='''            @Override public void onPageFinished(WebView v,String u){\n                super.onPageFinished(v,u);\n                if(scheduler!=null)scheduler.onWorkerPageFinished();\n            }'''
new_finish='''            @Override public void onPageFinished(WebView v,String u){\n                super.onPageFinished(v,u);\n                if(scheduler!=null)scheduler.onWorkerPageFinished(u);\n            }'''
assert old_finish in s
s=s.replace(old_finish,new_finish,1)
old_method='''        void onWorkerPageFinished(){\n            final long g=scanGeneration;final String id=activeId;final String path=activePath;\n            if(!scanning||id==null||path==null)return;\n            h.postDelayed(()->observe(g,id,path),320L);\n        }'''
new_method='''        void onWorkerPageFinished(String finishedUrl){\n            final long g=scanGeneration;final String id=activeId;final String path=activePath;\n            if(!scanning||id==null||path==null)return;\n            String finishedPath="";try{finishedPath=Uri.parse(finishedUrl==null?"":finishedUrl).getPath();}catch(Exception ignored){}\n            if(!path.equals(finishedPath)){emit("WORKER_FINISH_IGNORED",registry.byId(id),"UNKNOWN",jsonExtra("scan_generation",g,"reason","STALE_FINISH_ROUTE_MISMATCH"));return;}\n            h.postDelayed(()->observe(g,id,path),500L);\n        }'''
assert old_method in s
s=s.replace(old_method,new_method,1)
old_obs='''                String ready=o.optString("ready","");String got=o.optString("path","");\n                boolean exact="complete".equals(ready)&&path.equals(got);\n                if(!exact&&retry<MAX_READY_RETRIES){retry++;h.postDelayed(()->observe(g,id,path),READY_RETRY_MS);return;}\n                ConversationBindingV91 b=registry.byId(id);if(b==null){index++;advance();return;}\n                ObservationSnapshotV91 snap=new ObservationSnapshotV91();'''
new_obs='''                String ready=o.optString("ready","");String got=o.optString("path","");\n                boolean exact="complete".equals(ready)&&path.equals(got);\n                int observedTurns=Math.max(0,o.optInt("turn_count",0));\n                boolean generationSeen=o.optBoolean("generation_active",false);\n                boolean hydrationPending=exact&&observedTurns==0&&!generationSeen;\n                if((!exact||hydrationPending)&&retry<MAX_READY_RETRIES){\n                    retry++;ConversationBindingV91 rb=registry.byId(id);\n                    emit("OBSERVE_RETRY",rb,"UNKNOWN",jsonExtra("scan_generation",g,"retry",retry,"route_receipt",exact,"turn_count",observedTurns,"reason",!exact?"ROUTE_OR_READY_PENDING":"TURN_DOM_NOT_HYDRATED"));\n                    h.postDelayed(()->observe(g,id,path),READY_RETRY_MS);return;\n                }\n                ConversationBindingV91 b=registry.byId(id);if(b==null){index++;advance();return;}\n                ObservationSnapshotV91 snap=new ObservationSnapshotV91();'''
assert old_obs in s
s=s.replace(old_obs,new_obs,1)
s=s.replace('snap.routeReceipt=exact;snap.readyState=ready;snap.turnCount=Math.max(0,o.optInt("turn_count",0));','snap.routeReceipt=exact;snap.readyState=ready;snap.turnCount=observedTurns;',1)
new.write_text(s)

cfg91=PKG/'TelemetryConfigV91.java'
cfg92=PKG/'TelemetryConfigV92.java'
cs=cfg91.read_text(); assert 'class TelemetryConfigV91' in cs
cfg92.write_text(cs.replace('class TelemetryConfigV91','class TelemetryConfigV92',1))

man=ROOT/'app/src/main/AndroidManifest.xml'; ms=man.read_text(); assert ms.count('OrchestratorDashboardV91Activity')==1
man.write_text(ms.replace('OrchestratorDashboardV91Activity','OrchestratorDashboardV92Activity',1))
grad=ROOT/'app/build.gradle'; gs=grad.read_text(); assert re.search(r'versionCode\s+92\b',gs); assert '0.89-stable-dashboard-observer-registry' in gs
gs=re.sub(r'versionCode\s+92\b','versionCode 93',gs,1).replace('0.89-stable-dashboard-observer-registry','0.89.1-stable-dashboard-observer-readiness-repair',1); grad.write_text(gs)

out=new.read_text()
for x in ['OrchestratorDashboardV92Activity','MAX_READY_RETRIES=12','TURN_DOM_NOT_HYDRATED','STALE_FINISH_ROUTE_MISMATCH','OBSERVE_RETRY','TelemetryConfigV92','cp-v92-dashboard-observer-readiness-repair-v1','dashboard_registry_v91.json']:
    assert x in out,x
for bad in ['elementFromPoint','document.evaluate','XPathResult','addJavascriptInterface','CookieManager.getCookie','setDraft','sendCurrentDraft']:
    assert bad not in out,bad
assert '.click()' not in out
assert out.count('worker.loadUrl(')==1
print('Generated v0.89.1 Dashboard observer readiness repair')
