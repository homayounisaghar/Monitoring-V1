#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v104_dashboard_live_temp_control_fixed.py',run_name='__main__')

old_java=PKG/'OrchestratorDashboardV104LiveTempControlActivity.java'
new_java=PKG/'OrchestratorDashboardV105PlannerObserveSeedActivity.java'
s=old_java.read_text()
for a,b in [
    ('OrchestratorDashboardV104LiveTempControlActivity','OrchestratorDashboardV105PlannerObserveSeedActivity'),
    ('cp-v104-dashboard-live-temp-control-v1','cp-v105-dashboard-planner-observe-seed-v1'),
    ('dashboard-live-temp-control','dashboard-planner-observe-seed'),
    ('cp910-','cp911-'),
    ('cp_v104_','cp_v105_'),
    ('TelemetryConfigV104','TelemetryConfigV105'),
    ('MIC_PERMISSION_REQUEST=910','MIC_PERMISSION_REQUEST=911'),
]:
    assert a in s,a
    s=s.replace(a,b)

# v0.91.0 device telemetry proved PLANNER_REQUEST_STARTED but no first
# PLANNER_ENTRY_SCAN. The initial observer was only seeded from onPageFinished,
# which is not guaranteed when loadUrl(home) resolves to the already-current
# surface. Give Planner its own generation-deduped observation scheduler.
old='private boolean plannerRunning=false,targetExecutionRunning=false; private long plannerGeneration=0L,targetExecutionGeneration=0L; private int plannerPolls=0,targetExecutionPolls=0,plannerChatEffectDispatches=0,targetChatEffectDispatches=0;'
new='private boolean plannerRunning=false,targetExecutionRunning=false; private long plannerGeneration=0L,targetExecutionGeneration=0L,plannerObserveScheduledGeneration=-1L; private int plannerPolls=0,targetExecutionPolls=0,plannerChatEffectDispatches=0,targetChatEffectDispatches=0;'
assert s.count(old)==1,('planner fields',s.count(old))
s=s.replace(old,new,1)

old='plannerGeneration++;plannerPolls=0;plannerRunning=true;plannerPhase="WAIT_SEMANTIC_NORMAL";plannerExpectedComposerHash="-";plannerBaselineAssistantHash="-";normalEntryStableHits=0;tempReceiptStableHits=0;normalRestoreStableHits=0;'
new='plannerGeneration++;plannerPolls=0;plannerRunning=true;plannerObserveScheduledGeneration=-1L;plannerPhase="WAIT_SEMANTIC_NORMAL";plannerExpectedComposerHash="-";plannerBaselineAssistantHash="-";normalEntryStableHits=0;tempReceiptStableHits=0;normalRestoreStableHits=0;'
assert s.count(old)==1,('planner start reset',s.count(old))
s=s.replace(old,new,1)

old='emit("PLANNER_REQUEST_STARTED",null,"UNKNOWN",jsonExtra("request_digest",plannerRequestDigest,"planner_phase",plannerPhase));showPlannerSurface("Planner transaction active in disposable-session mode. Target execution still requires explicit EXECUTE.");foreground.loadUrl("https://chatgpt.com/");'
new='emit("PLANNER_REQUEST_STARTED",null,"UNKNOWN",jsonExtra("request_digest",plannerRequestDigest,"planner_phase",plannerPhase));showPlannerSurface("Planner transaction active in disposable-session mode. Target execution still requires explicit EXECUTE.");foreground.loadUrl("https://chatgpt.com/");plannerScheduleObserve(plannerGeneration,450L);emit("PLANNER_OBSERVE_SEEDED",null,"UNKNOWN",jsonExtra("request_digest",plannerRequestDigest,"planner_phase",plannerPhase));'
assert s.count(old)==1,('planner initial seed',s.count(old))
s=s.replace(old,new,1)

old='if(targetExecutionRunning){long g=targetExecutionGeneration;h.postDelayed(()->targetObserve(g),350L);return;} if(plannerRunning){long g=plannerGeneration;h.postDelayed(()->plannerObserve(g),350L);return;} if(replyTracking){long g=replyGeneration;h.postDelayed(()->replyObserve(g),500L);return;} if(pendingOpenPath!=null)h.postDelayed(()->verifyOpenReceipt(),350L);'
new='if(targetExecutionRunning){long g=targetExecutionGeneration;h.postDelayed(()->targetObserve(g),350L);return;} if(plannerRunning){long g=plannerGeneration;plannerScheduleObserve(g,350L);return;} if(replyTracking){long g=replyGeneration;h.postDelayed(()->replyObserve(g),500L);return;} if(pendingOpenPath!=null)h.postDelayed(()->verifyOpenReceipt(),350L);'
assert s.count(old)==1,('page-finished planner scheduler',s.count(old))
s=s.replace(old,new,1)

old='    private void plannerLater(long g){if(plannerRunning&&g==plannerGeneration)h.postDelayed(()->plannerObserve(g),PLANNER_POLL_MS);}'
new='''    private void plannerScheduleObserve(long g,long delayMs){
        if(!plannerRunning||g!=plannerGeneration||plannerObserveScheduledGeneration==g)return;
        plannerObserveScheduledGeneration=g;
        h.postDelayed(()->{
            if(plannerObserveScheduledGeneration==g)plannerObserveScheduledGeneration=-1L;
            if(!plannerRunning||g!=plannerGeneration)return;
            plannerObserve(g);
        },delayMs);
    }
    private void plannerLater(long g){plannerScheduleObserve(g,PLANNER_POLL_MS);}'''
assert s.count(old)==1,('plannerLater',s.count(old))
s=s.replace(old,new,1)

# Scheduler is control-flow only: semantic admission and all one-shot effect
# claims remain unchanged.
for required in [
    'PLANNER_OBSERVE_SEEDED','plannerScheduleObserve','plannerObserveScheduledGeneration',
    'PLANNER_ENTRY_SCAN','UNIQUE_SEMANTIC_TEMP_CONTROL_CLICK','WAIT_TEMP_RECEIPT',
    'WAIT_NORMAL_RESTORE','targetChatEffectDispatches++','No target action executed or replayed'
]:
    assert required in s,required
assert s.count('targetChatEffectDispatches++')==1
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
g=g.replace('versionCode 105','versionCode 106',1).replace("versionName '0.91.0-stable-dashboard-live-temp-control'","versionName '0.91.1-stable-dashboard-planner-observe-seed'",1)
gradle.write_text(g)

man=ROOT/'app/src/main/AndroidManifest.xml'
m=man.read_text()
assert m.count('OrchestratorDashboardV104LiveTempControlActivity')==1
m=m.replace('OrchestratorDashboardV104LiveTempControlActivity','OrchestratorDashboardV105PlannerObserveSeedActivity',1)
man.write_text(m)

print('PASS v0.91.1 Planner observation seed + generation dedupe; semantic/effect gates unchanged')
