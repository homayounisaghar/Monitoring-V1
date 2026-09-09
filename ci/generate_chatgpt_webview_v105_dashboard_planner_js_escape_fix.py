#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v104_dashboard_live_temp_control_fixed.py',run_name='__main__')

old_java=PKG/'OrchestratorDashboardV104LiveTempControlActivity.java'
new_java=PKG/'OrchestratorDashboardV105PlannerJsEscapeFixActivity.java'
s=old_java.read_text()

# Root cause from v0.91.0 device telemetry: Planner request starts, but the
# plannerReadJs evaluate callback never yields a valid JSONObject. The Stage-A
# source inspection shows exactly one Java-string escaping defect in the
# line-aware composer extractor: Java source contained \n escapes that became
# literal newlines inside a JavaScript regex/string at runtime, making the JS
# syntactically invalid before its try/catch could execute.
bad=r"replace(/\n$/,'');}).join('\n');return X(e.innerText||e.textContent||'');};const DS=e=>"
good=r"replace(/\\n$/,'');}).join('\\n');return X(e.innerText||e.textContent||'');};const DS=e=>"
assert s.count(bad)==1,('plannerReadJs bad newline escape',s.count(bad))
s=s.replace(bad,good,1)

for a,b in [
    ('OrchestratorDashboardV104LiveTempControlActivity','OrchestratorDashboardV105PlannerJsEscapeFixActivity'),
    ('cp-v104-dashboard-live-temp-control-v1','cp-v105-dashboard-planner-js-escape-fix-v1'),
    ('dashboard-live-temp-control','dashboard-planner-js-escape-fix'),
    ('cp910-','cp911-'),
    ('cp_v104_','cp_v105_'),
    ('TelemetryConfigV104','TelemetryConfigV105'),
    ('MIC_PERMISSION_REQUEST=910','MIC_PERMISSION_REQUEST=911'),
]:
    assert a in s,a
    s=s.replace(a,b)

new_java.write_text(s)
old_java.unlink()

old_cfg=PKG/'TelemetryConfigV104.java'
new_cfg=PKG/'TelemetryConfigV105.java'
c=old_cfg.read_text().replace('TelemetryConfigV104','TelemetryConfigV105')
new_cfg.write_text(c)
old_cfg.unlink()

gradle=ROOT/'app/build.gradle'
g=gradle.read_text()
assert g.count('versionCode 105')==1
assert g.count("versionName '0.91.0-stable-dashboard-live-temp-control'")==1
g=g.replace('versionCode 105','versionCode 106',1).replace("versionName '0.91.0-stable-dashboard-live-temp-control'","versionName '0.91.1-stable-dashboard-planner-js-escape-fix'",1)
gradle.write_text(g)

man=ROOT/'app/src/main/AndroidManifest.xml'
m=man.read_text()
assert m.count('OrchestratorDashboardV104LiveTempControlActivity')==1
m=m.replace('OrchestratorDashboardV104LiveTempControlActivity','OrchestratorDashboardV105PlannerJsEscapeFixActivity',1)
man.write_text(m)

assert bad not in s
assert good in s
assert 'PLANNER_ENTRY_SCAN' in s
assert s.count('targetChatEffectDispatches++')==1
print('PASS v0.91.1 plannerReadJs Java-to-JS newline escape repair')
