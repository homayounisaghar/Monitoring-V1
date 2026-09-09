#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v94_dashboard_stateless_planner_recipe_only_fixed.py',run_name='__main__')

old_java=PKG/'OrchestratorDashboardV94PlannerIngressActivity.java'
new_java=PKG/'OrchestratorDashboardV95PlannerReceiptRepairActivity.java'
s=old_java.read_text()
for a,b in [
    ('OrchestratorDashboardV94PlannerIngressActivity','OrchestratorDashboardV95PlannerReceiptRepairActivity'),
    ('cp-v94-dashboard-stateless-planner-recipe-only-v1','cp-v95-dashboard-planner-correlation-readback-repair-v1'),
    ('dashboard-stateless-planner-recipe-only','dashboard-planner-correlation-readback-repair'),
    ('cp900-','cp901-'),
    ('cp_v94_stateless_planner','cp_v95_stateless_planner'),
    ('TelemetryConfigV94','TelemetryConfigV95'),
]:
    assert a in s,a
    s=s.replace(a,b)

old='if(!plannerExpectedComposerHash.equals(o.optString("last_user_hash","-"))||!path.matches("^/c/[^/?#]+$")){plannerLater(g);return;}'
new='String lut=o.optString("last_user_text","");boolean userCorr=lut.contains(plannerRequestId)&&lut.contains(plannerRequestDigest);if(!userCorr||!path.matches("^/c/[^/?#]+$")){plannerLater(g);return;}'
assert s.count(old)==1,('send receipt condition',s.count(old))
s=s.replace(old,new,1)

old='boolean ready=plannerExpectedComposerHash.equals(o.optString("last_user_hash","-"))&&!"-".equals(o.optString("last_assistant_hash","-"))&&!o.optString("last_assistant_hash","-").equals(plannerBaselineAssistantHash)&&o.optInt("stop_candidate_count",0)==0&&o.optInt("assistant_completion_candidate_count",0)>=1;'
new='String lut2=o.optString("last_user_text",""),lat=o.optString("last_assistant_text","");boolean userCorr2=lut2.contains(plannerRequestId)&&lut2.contains(plannerRequestDigest);String trimmed=lat.trim();boolean assistantCorr=lat.contains(plannerRequestId)&&lat.contains(plannerRequestDigest);boolean ready=userCorr2&&assistantCorr&&trimmed.startsWith("{")&&trimmed.endsWith("}")&&!"-".equals(o.optString("last_assistant_hash","-"))&&!o.optString("last_assistant_hash","-").equals(plannerBaselineAssistantHash)&&o.optInt("stop_candidate_count",0)==0;'
assert s.count(old)==1,('response condition',s.count(old))
s=s.replace(old,new,1)

for old,new in [
    ('plannerBaselineAssistantHash=o.optString("last_assistant_hash","-");plannerWrite(g);return;',
     'plannerBaselineAssistantHash=o.optString("last_assistant_hash","-");plannerResult.setText("Planner: fresh chat ready; writing request...");plannerWrite(g);return;'),
    ('plannerPhase="WAIT_COMPOSER_RECEIPT";emit("PLANNER_COMPOSER_WRITE"',
     'plannerPhase="WAIT_COMPOSER_RECEIPT";plannerResult.setText("Planner: request written; verifying composer...");emit("PLANNER_COMPOSER_WRITE"'),
    ('plannerChatEffectDispatches++;plannerPhase="WAIT_SEND_RECEIPT";emit("PLANNER_SEND_DISPATCH"',
     'plannerChatEffectDispatches++;plannerPhase="WAIT_SEND_RECEIPT";plannerResult.setText("Planner: sent; confirming correlated request...");emit("PLANNER_SEND_DISPATCH"'),
    ('plannerJournal.edit().putString("status","PLANNER_SEND_RECEIPT_CONFIRMED").commit();plannerPhase="WAIT_RESPONSE";emit("PLANNER_SEND_RECEIPT",null,"UNKNOWN",jsonExtra("request_digest",plannerRequestDigest,"planner_route_hash",sha256(path)));',
     'plannerJournal.edit().putString("status","PLANNER_SEND_RECEIPT_CONFIRMED").commit();plannerPhase="WAIT_RESPONSE";plannerResult.setText("Planner: send confirmed; waiting for correlated recipe...");emit("PLANNER_SEND_RECEIPT",null,"UNKNOWN",jsonExtra("request_digest",plannerRequestDigest,"planner_route_hash",sha256(path),"receipt_basis","REQUEST_ID_DIGEST"));'),
    ('if(!ready){plannerLater(g);return;}plannerRecipe(o.optString("last_assistant_text",""));return;',
     'if(!ready){plannerLater(g);return;}plannerResult.setText("Planner: correlated recipe received; parsing...");plannerRecipe(lat);return;'),
]:
    assert s.count(old)==1,(old[:70],s.count(old))
    s=s.replace(old,new,1)

assert 'plannerExpectedComposerHash.equals(o.optString("last_user_hash"' not in s
assert 'assistant_completion_candidate_count",0)>=1' not in s
assert 'receipt_basis","REQUEST_ID_DIGEST"' in s
assert 'targetChatEffectDispatches++' not in s
assert s.count('.click()')==1
new_java.write_text(s)

cfg_old=PKG/'TelemetryConfigV94.java'
cfg_new=PKG/'TelemetryConfigV95.java'
cfg=cfg_old.read_text().replace('TelemetryConfigV94','TelemetryConfigV95')
assert 'CONFIGURED=false' in cfg
cfg_new.write_text(cfg)

gradle=ROOT/'app/build.gradle'
g=gradle.read_text()
assert g.count('versionCode 95')==1
assert g.count("versionName '0.90.0-stable-dashboard-stateless-planner-recipe-only'")==1
g=g.replace('versionCode 95','versionCode 96',1).replace("versionName '0.90.0-stable-dashboard-stateless-planner-recipe-only'","versionName '0.90.1-stable-dashboard-planner-correlation-readback-repair'",1)
gradle.write_text(g)

man=ROOT/'app/src/main/AndroidManifest.xml'
m=man.read_text()
assert m.count('OrchestratorDashboardV94PlannerIngressActivity')==1
m=m.replace('OrchestratorDashboardV94PlannerIngressActivity','OrchestratorDashboardV95PlannerReceiptRepairActivity',1)
man.write_text(m)

print('PASS v0.90.1 generator: request-id/digest send receipt + correlated JSON readback + live phase UI')
