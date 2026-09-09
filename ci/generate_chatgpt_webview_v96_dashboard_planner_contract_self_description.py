#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v95_dashboard_planner_correlation_readback_repair.py',run_name='__main__')

old_java=PKG/'OrchestratorDashboardV95PlannerReceiptRepairActivity.java'
new_java=PKG/'OrchestratorDashboardV96PlannerContractRepairActivity.java'
s=old_java.read_text()
for a,b in [
    ('OrchestratorDashboardV95PlannerReceiptRepairActivity','OrchestratorDashboardV96PlannerContractRepairActivity'),
    ('cp-v95-dashboard-planner-correlation-readback-repair-v1','cp-v96-dashboard-planner-contract-self-description-v1'),
    ('dashboard-planner-correlation-readback-repair','dashboard-planner-contract-self-description'),
    ('cp901-','cp902-'),
    ('cp_v95_stateless_planner','cp_v96_stateless_planner'),
    ('TelemetryConfigV95','TelemetryConfigV96'),
]:
    assert a in s,a
    s=s.replace(a,b)

old='READY operations use {op_id,capability,target:{chat_ref},arguments}. Non-READY returns operations=[].'
new=('READY operations use {op_id,capability,target:{chat_ref},arguments}. '
     'Capability argument contracts are strict: chat.refresh_state requires arguments={}; '
     'chat.send_message requires arguments={\\"message_text\\":\\"<non-empty string>\\"}; '
     'chat.send_attachment requires arguments={\\"attachment_ref\\":\\"<non-empty ref>\\"} and may additionally include '
     '\\"message_text\\":\\"<non-empty string>\\". Do not use other argument keys. '
     'Non-READY returns operations=[].')
assert s.count(old)==1,('planner capability contract anchor',s.count(old))
s=s.replace(old,new,1)

for required in [
    'chat.send_message requires arguments={\\"message_text\\":\\"<non-empty string>\\"}',
    'chat.send_attachment requires arguments={\\"attachment_ref\\":\\"<non-empty ref>\\"}',
    'Do not use other argument keys.',
    'receipt_basis","REQUEST_ID_DIGEST"',
]:
    assert required in s,required
assert 'targetChatEffectDispatches++' not in s
assert s.count('.click()')==1
new_java.write_text(s)

cfg_old=PKG/'TelemetryConfigV95.java'
cfg_new=PKG/'TelemetryConfigV96.java'
cfg=cfg_old.read_text().replace('TelemetryConfigV95','TelemetryConfigV96')
assert 'CONFIGURED=false' in cfg
cfg_new.write_text(cfg)

gradle=ROOT/'app/build.gradle'
g=gradle.read_text()
assert g.count('versionCode 96')==1
assert g.count("versionName '0.90.1-stable-dashboard-planner-correlation-readback-repair'")==1
g=g.replace('versionCode 96','versionCode 97',1).replace(
    "versionName '0.90.1-stable-dashboard-planner-correlation-readback-repair'",
    "versionName '0.90.2-stable-dashboard-planner-contract-self-description'",1)
gradle.write_text(g)

man=ROOT/'app/src/main/AndroidManifest.xml'
m=man.read_text()
assert m.count('OrchestratorDashboardV95PlannerReceiptRepairActivity')==1
m=m.replace('OrchestratorDashboardV95PlannerReceiptRepairActivity','OrchestratorDashboardV96PlannerContractRepairActivity',1)
man.write_text(m)

print('PASS v0.90.2 generator: self-describing capability argument contracts + v0.90.1 correlation/readback repair')
