#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v97_dashboard_planner_single_send.py',run_name='__main__')

old_java=PKG/'OrchestratorDashboardV97PlannerSingleSendActivity.java'
new_java=PKG/'OrchestratorDashboardV98PlannerTargetConfirmationActivity.java'
s=old_java.read_text()
for a,b in [
    ('OrchestratorDashboardV97PlannerSingleSendActivity','OrchestratorDashboardV98PlannerTargetConfirmationActivity'),
    ('cp-v97-dashboard-planner-single-send-v1','cp-v98-dashboard-planner-target-confirmation-v1'),
    ('dashboard-planner-single-send','dashboard-planner-target-confirmation'),
    ('cp903-','cp904-'),
    ('cp_v97_stateless_planner','cp_v98_stateless_planner'),
    ('cp_v97_target_execution','cp_v98_target_execution'),
    ('TelemetryConfigV97','TelemetryConfigV98'),
]:
    assert a in s,a
    s=s.replace(a,b)

old='private JSONObject pendingRecipe=null; private String pendingTargetBindingId="",pendingTargetPathHash="";'
new='private JSONObject pendingRecipe=null; private String pendingTargetBindingId="",pendingTargetPathHash="",pendingTargetAlias="",pendingTargetMessage="";'
assert s.count(old)==1,('pending target fields',s.count(old))
s=s.replace(old,new,1)

old='plannerResult=new TextView(this);plannerResult.setTextSize(11f);plannerResult.setPadding(dp(8),dp(4),dp(8),dp(4));plannerResult.setText("No Planner recipe yet.");root.addView(plannerResult,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(112)));'
new='plannerResult=new TextView(this);plannerResult.setTextSize(13f);plannerResult.setPadding(dp(10),dp(8),dp(10),dp(8));plannerResult.setText("No Planner recipe yet.");root.addView(plannerResult,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(176)));'
assert s.count(old)==1,('planner result surface',s.count(old))
s=s.replace(old,new,1)

old='pc.setOnClickListener(v->{if(!plannerRunning&&!targetExecutionRunning){plannerInput.setText("");plannerResult.setText("No Planner recipe yet.");pendingRecipe=null;executeButton.setEnabled(false);}});'
new='pc.setOnClickListener(v->{if(!plannerRunning&&!targetExecutionRunning){plannerInput.setText("");plannerResult.setText("No Planner recipe yet.");pendingRecipe=null;pendingTargetBindingId="";pendingTargetPathHash="";pendingTargetAlias="";pendingTargetMessage="";executeButton.setText("EXECUTE");executeButton.setEnabled(false);}});'
assert s.count(old)==1,('clear handler',s.count(old))
s=s.replace(old,new,1)

old='pendingRecipe=null;pendingTargetBindingId="";pendingTargetPathHash="";if(executeButton!=null)executeButton.setEnabled(false);'
new='pendingRecipe=null;pendingTargetBindingId="";pendingTargetPathHash="";pendingTargetAlias="";pendingTargetMessage="";if(executeButton!=null){executeButton.setText("EXECUTE");executeButton.setEnabled(false);}'
assert s.count(old)==1,('planner reset',s.count(old))
s=s.replace(old,new,1)

old='pendingRecipe=r;pendingTargetBindingId="";pendingTargetPathHash="";boolean executable=false;'
new='pendingRecipe=r;pendingTargetBindingId="";pendingTargetPathHash="";pendingTargetAlias="";pendingTargetMessage="";boolean executable=false;'
assert s.count(old)==1,('recipe reset',s.count(old))
s=s.replace(old,new,1)

old='if(rb!=null){pendingTargetBindingId=rb.id;pendingTargetPathHash=rb.pathHash;executable=true;}'
new='if(rb!=null){JSONObject aa=op.optJSONObject("arguments");String pm=aa==null?"":aa.optString("message_text","");pendingTargetBindingId=rb.id;pendingTargetPathHash=rb.pathHash;pendingTargetAlias=rb.alias;pendingTargetMessage=pm;executable=!pm.isEmpty();}'
assert s.count(old)==1,('resolved target freeze',s.count(old))
s=s.replace(old,new,1)

old='executeButton.setEnabled(executable);emit("PLANNER_RECIPE_ACCEPTED",null,st,jsonExtra("request_digest",plannerRequestDigest,"recipe_status",st,"operation_count",n,"execution_available",executable,"target_chat_effect_dispatches",targetChatEffectDispatches));try{plannerResult.setText("Recipe "+st+(executable?" · ready for explicit EXECUTE":" · not executable in this build")+"\\n"+r.toString(2));}catch(Exception e){plannerResult.setText("Recipe "+st+" accepted.");}showDashboard(executable?"Planner recipe ready. Press EXECUTE for one bounded target send.":"Planner recipe received; this build executes only one send_message operation.");'
new='executeButton.setText(executable?"EXECUTE → "+pendingTargetAlias:"EXECUTE");executeButton.setEnabled(executable);emit("PLANNER_RECIPE_ACCEPTED",null,st,jsonExtra("request_digest",plannerRequestDigest,"recipe_status",st,"operation_count",n,"execution_available",executable,"target_chat_effect_dispatches",targetChatEffectDispatches));try{String preview=pendingTargetMessage.length()>240?pendingTargetMessage.substring(0,240)+"…":pendingTargetMessage;plannerResult.setText(executable?"TARGET: "+pendingTargetAlias+"\\nACTION: Send message\\nMESSAGE: "+preview+"\\nTARGET FROZEN: YES\\n\\nRecipe "+st+"\\n"+r.toString(2):"Recipe "+st+" · not executable in this build\\n"+r.toString(2));}catch(Exception e){plannerResult.setText("Recipe "+st+" accepted.");}showDashboard(executable?"Target frozen: "+pendingTargetAlias+". Review target/message, then press EXECUTE.":"Planner recipe received; this build executes only one send_message operation.");'
assert s.count(old)==1,('confirmation summary',s.count(old))
s=s.replace(old,new,1)

old='executeButton.setEnabled(false);emit("TARGET_SEND_RECEIPT",b,"CONFIRMED",jsonExtra('
new='executeButton.setText("EXECUTE");executeButton.setEnabled(false);emit("TARGET_SEND_RECEIPT",b,"CONFIRMED",jsonExtra('
assert s.count(old)==1,('confirmed reset button',s.count(old))
s=s.replace(old,new,1)

old='if(executeButton!=null)executeButton.setEnabled(false);emit("TARGET_EXECUTION_FAILED",b,"UNKNOWN",jsonExtra('
new='if(executeButton!=null){executeButton.setText("EXECUTE");executeButton.setEnabled(false);}emit("TARGET_EXECUTION_FAILED",b,"UNKNOWN",jsonExtra('
assert s.count(old)==1,('failed reset button',s.count(old))
s=s.replace(old,new,1)

for required in [
    'TARGET: "+pendingTargetAlias',
    'ACTION: Send message',
    'MESSAGE: "+preview',
    'TARGET FROZEN: YES',
    'EXECUTE → "+pendingTargetAlias',
    'Target frozen: "+pendingTargetAlias',
    'TARGET_SEND_RECEIPT',
    'EXACT_LAST_USER_HASH_AND_TURN_INCREMENT',
    'targetChatEffectDispatches++',
]:
    assert required in s,required
assert s.count('targetChatEffectDispatches++')==1
assert s.count('.click()')==1
new_java.write_text(s)

cfg_old=PKG/'TelemetryConfigV97.java'
cfg_new=PKG/'TelemetryConfigV98.java'
cfg=cfg_old.read_text().replace('TelemetryConfigV97','TelemetryConfigV98')
assert 'CONFIGURED=false' in cfg
cfg_new.write_text(cfg)

gradle=ROOT/'app/build.gradle'
g=gradle.read_text()
assert g.count('versionCode 98')==1
assert g.count("versionName '0.90.3-stable-dashboard-planner-single-send'")==1
g=g.replace('versionCode 98','versionCode 99',1).replace(
    "versionName '0.90.3-stable-dashboard-planner-single-send'",
    "versionName '0.90.4-stable-dashboard-planner-target-confirmation'",1)
gradle.write_text(g)

man=ROOT/'app/src/main/AndroidManifest.xml'
m=man.read_text()
assert m.count('OrchestratorDashboardV97PlannerSingleSendActivity')==1
m=m.replace('OrchestratorDashboardV97PlannerSingleSendActivity','OrchestratorDashboardV98PlannerTargetConfirmationActivity',1)
man.write_text(m)

print('PASS v0.90.4 generator: conspicuous frozen target/action/message confirmation + unchanged one-shot send/receipt semantics')
