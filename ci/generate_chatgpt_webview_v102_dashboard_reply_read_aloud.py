#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v101_dashboard_exact_text_workflow_fixed.py',run_name='__main__')
old_java=PKG/'OrchestratorDashboardV101ExactTextWorkflowActivity.java'
new_java=PKG/'OrchestratorDashboardV102ReplyReadAloudActivity.java'
s=old_java.read_text()

for a,b in [
    ('OrchestratorDashboardV101ExactTextWorkflowActivity','OrchestratorDashboardV102ReplyReadAloudActivity'),
    ('cp-v101-dashboard-exact-text-workflow-journal-v1','cp-v102-dashboard-correlated-reply-read-aloud-v1'),
    ('dashboard-exact-text-workflow-journal','dashboard-correlated-reply-read-aloud'),
    ('cp907-','cp908-'),
    ('cp_v101_stateless_planner','cp_v102_stateless_planner'),
    ('cp_v101_target_execution','cp_v102_target_execution'),
    ('cp_v101_workflow_journal','cp_v102_workflow_journal'),
    ('TelemetryConfigV101','TelemetryConfigV102'),
    ('MIC_PERMISSION_REQUEST=907','MIC_PERMISSION_REQUEST=908'),
]:
    assert a in s,a
    s=s.replace(a,b)

old='private EditText plannerInput; private TextView plannerResult,voicePreview; private Button plannerButton,executeButton,voiceButton; private SharedPreferences plannerJournal,targetJournal;'
new='private EditText plannerInput; private TextView plannerResult,voicePreview; private Button plannerButton,executeButton,voiceButton,readReplyButton,stopSpeechButton; private SharedPreferences plannerJournal,targetJournal;'
assert s.count(old)==1
s=s.replace(old,new,1)

old='private JSONObject pendingRecipe=null; private String pendingTargetBindingId="",pendingTargetPathHash="",pendingTargetAlias="",pendingTargetMessage=""; private boolean targetSendDispatchedThisAttempt=false; private String targetExecutionPhase="IDLE",targetExpectedPath="",targetExpectedBindingId="",targetExpectedMessage="",targetExpectedComposerHash="-",targetExpectedExactHash="-",targetBaselineLastUserHash="-",targetAttemptId="",activeWorkflowId="",activeWorkflowStepId="send-1"; private int targetBaselineTurnCount=0; private WorkflowJournalGuardV1 workflowJournal;'
new='private JSONObject pendingRecipe=null; private String pendingTargetBindingId="",pendingTargetPathHash="",pendingTargetAlias="",pendingTargetMessage=""; private boolean targetSendDispatchedThisAttempt=false; private String targetExecutionPhase="IDLE",targetExpectedPath="",targetExpectedBindingId="",targetExpectedMessage="",targetExpectedComposerHash="-",targetExpectedExactHash="-",targetBaselineLastUserHash="-",targetAttemptId="",activeWorkflowId="",activeWorkflowStepId="send-1"; private int targetBaselineTurnCount=0,targetBaselineUserTurnCount=0,targetBaselineAssistantTurnCount=0; private String targetBaselineAssistantExactSha=""; private WorkflowJournalGuardV1 workflowJournal; private AssistantReplyWaitJournalV1 replyWaitJournal; private CorrelatedAssistantReplyTrackerV1 replyTracker; private boolean replyTracking=false; private long replyGeneration=0L; private int replyPolls=0; private String replyWorkflowId="",replyStepId="",capturedReplyText="",capturedReplySha=""; private SpeechOutputSessionV1 activeSpeechSession;'
assert s.count(old)==1
s=s.replace(old,new,1)

old='private static final int MAX_TARGET_EXECUTION_POLLS=120;'
new='private static final int MAX_TARGET_EXECUTION_POLLS=120,MAX_REPLY_POLLS=1200; private static final long REPLY_POLL_MS=500L,REPLY_WAIT_TTL_MS=600000L;'
assert s.count(old)==1
s=s.replace(old,new,1)

old='navJournal=getSharedPreferences("cp_v91_dashboard_navigation",MODE_PRIVATE); plannerJournal=getSharedPreferences("cp_v102_stateless_planner",MODE_PRIVATE); targetJournal=getSharedPreferences("cp_v102_target_execution",MODE_PRIVATE); workflowJournal=new WorkflowJournalGuardV1(getSharedPreferences("cp_v102_workflow_journal",MODE_PRIVATE));'
new=old+' replyWaitJournal=new AssistantReplyWaitJournalV1(getSharedPreferences("cp_v102_reply_wait",MODE_PRIVATE));'
assert s.count(old)==1
s=s.replace(old,new,1)

# Manual local read-aloud proof controls. They do not add a Planner capability.
old='plannerResult=new TextView(this);plannerResult.setTextSize(13f);plannerResult.setPadding(dp(10),dp(8),dp(10),dp(8));plannerResult.setText("No Planner recipe yet.");root.addView(plannerResult,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(176)));'
new=old+'''\n        LinearLayout rr=new LinearLayout(this);rr.setOrientation(LinearLayout.HORIZONTAL);readReplyButton=new Button(this);readReplyButton.setText("🔊 READ LAST REPLY");readReplyButton.setEnabled(false);readReplyButton.setOnClickListener(v->speakCapturedReply());stopSpeechButton=new Button(this);stopSpeechButton.setText("■ STOP SPEECH");stopSpeechButton.setEnabled(false);stopSpeechButton.setOnClickListener(v->stopSpeechOutput());rr.addView(readReplyButton,new LinearLayout.LayoutParams(0,dp(42),1.5f));rr.addView(stopSpeechButton,new LinearLayout.LayoutParams(0,dp(42),1f));root.addView(rr,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(42)));'''
assert s.count(old)==1
s=s.replace(old,new,1)

# Show/hide local speech controls with Dashboard surfaces.
old='plannerResult.setVisibility(View.VISIBLE);bindButton.setEnabled(false);foreground.setLayoutParams'
new='plannerResult.setVisibility(View.VISIBLE);readReplyButton.setVisibility(View.VISIBLE);stopSpeechButton.setVisibility(View.VISIBLE);bindButton.setEnabled(false);foreground.setLayoutParams'
assert s.count(old)==3,('dashboard/planner/execution modes',s.count(old))
s=s.replace(old,new)
old='plannerResult.setVisibility(View.GONE);bindButton.setEnabled(true);status.setText(msg);}'
new='plannerResult.setVisibility(View.GONE);readReplyButton.setVisibility(View.GONE);stopSpeechButton.setVisibility(View.GONE);bindButton.setEnabled(true);status.setText(msg);}'
assert s.count(old)==1
s=s.replace(old,new,1)

# Any new Planner transaction supersedes a non-material background reply watch.
old='private void startPlannerRequest(){if(isVoiceBusy()){status.setText("Finish voice input first.");return;}if(plannerRunning||targetExecutionRunning)return;'
new='private void startPlannerRequest(){if(isVoiceBusy()){status.setText("Finish voice input first.");return;}if(plannerRunning||targetExecutionRunning)return;if(replyTracking)cancelReplyTracking("SUPERSEDED_BY_NEW_PLANNER");'
assert s.count(old)==1
s=s.replace(old,new,1)

# Capture exact turn-count anchors before the user Send.
old='targetBaselineTurnCount=o.optInt("turn_count",0);targetBaselineLastUserHash=o.optString("last_user_hash","-");plannerResult.setText("Execution: target route confirmed; writing message...");'
new='targetBaselineTurnCount=o.optInt("turn_count",0);targetBaselineUserTurnCount=o.optInt("user_turn_count",0);targetBaselineAssistantTurnCount=o.optInt("assistant_turn_count",0);targetBaselineAssistantExactSha=ExactTextV1.sha256(o.optString("last_assistant_text",""));targetBaselineLastUserHash=o.optString("last_user_hash","-");plannerResult.setText("Execution: target route confirmed; writing message...");'
assert s.count(old)==1
s=s.replace(old,new,1)

# After the exact send receipt succeeds, arm a read-only correlated reply watch.
old='emit("TARGET_SEND_RECEIPT",b,"CONFIRMED",jsonExtra("request_digest",plannerRequestDigest,"attempt_id",targetAttemptId,"receipt_basis","EXACT_LAST_USER_HASH_AND_TURN_INCREMENT","target_chat_effect_dispatches",targetChatEffectDispatches));plannerResult.setText("Execution CONFIRMED. One target message was sent.\\nRun Planner again for another action.");showDashboard("Target send confirmed. One bounded effect executed.");return;'
new='emit("TARGET_SEND_RECEIPT",b,"CONFIRMED",jsonExtra("request_digest",plannerRequestDigest,"attempt_id",targetAttemptId,"receipt_basis","EXACT_LAST_USER_HASH_AND_TURN_INCREMENT","target_chat_effect_dispatches",targetChatEffectDispatches));armReplyCapture(b);plannerResult.setText("Execution CONFIRMED. One target message was sent.\\nWaiting read-only for its correlated assistant reply; READ LAST REPLY enables when captured.");showDashboard("Target send confirmed. Reply observer armed without another target effect.");return;'
assert s.count(old)==1
s=s.replace(old,new,1)

# Snapshot reports separate role counts for exact reply correlation.
old='temp_candidate_count:E.length,turn_count:T.length,turns:T,last_user_text:'
new='temp_candidate_count:E.length,turn_count:T.length,user_turn_count:U.length,assistant_turn_count:A.length,turns:T,last_user_text:'
assert s.count(old)==1
s=s.replace(old,new,1)

# Add read-only reply tracking and local speech methods before plannerReadJs.
marker='    private String plannerReadJs(){\n'
assert s.count(marker)==1
methods=r'''    private void armReplyCapture(ConversationBindingV91 b){
        if(b==null||replyWaitJournal==null)return;
        if(replyTracking)cancelReplyTracking("SUPERSEDED_BY_NEW_SEND");
        replyWorkflowId=activeWorkflowId;replyStepId=activeWorkflowStepId;capturedReplyText="";capturedReplySha="";replyPolls=0;replyGeneration++;long g=replyGeneration;
        String expectedUserSha=ExactTextV1.sha256(targetExpectedMessage);long expiry=System.currentTimeMillis()+REPLY_WAIT_TTL_MS;
        boolean armed=replyWaitJournal.arm(replyWorkflowId,replyStepId,b.pathHash,expectedUserSha,targetBaselineUserTurnCount,targetBaselineAssistantTurnCount,targetBaselineAssistantExactSha,expiry);
        if(!armed){emit("TARGET_REPLY_WATCH_FAILED",b,"UNKNOWN",jsonExtra("reason","REPLY_WAIT_JOURNAL_ARM_FAILED"));return;}
        replyTracker=new CorrelatedAssistantReplyTrackerV1(b.pathHash,expectedUserSha,targetBaselineUserTurnCount,targetBaselineAssistantTurnCount,targetBaselineAssistantExactSha);replyTracking=true;
        if(readReplyButton!=null)readReplyButton.setEnabled(false);
        emit("TARGET_REPLY_WATCH_STARTED",b,"UNKNOWN",jsonExtra("workflow_id_digest",sha256(replyWorkflowId),"step_id",replyStepId));
        h.postDelayed(()->replyObserve(g),REPLY_POLL_MS);
    }

    private void replyObserve(long g){
        if(!replyTracking||g!=replyGeneration||replyTracker==null)return;
        if(++replyPolls>MAX_REPLY_POLLS){cancelReplyTracking("REPLY_OBSERVATION_BUDGET_EXHAUSTED");return;}
        eval(foreground,plannerReadJs(),o->{
            if(!replyTracking||g!=replyGeneration)return;
            if(!o.optBoolean("success",false)){h.postDelayed(()->replyObserve(g),REPLY_POLL_MS);return;}
            String path=o.optString("local_path","");String lu=o.optString("last_user_text","");String la=o.optString("last_assistant_text","");
            CorrelatedAssistantReplyTrackerV1.Snapshot snap=new CorrelatedAssistantReplyTrackerV1.Snapshot(
                sha256(path),o.optInt("user_turn_count",0),o.optInt("assistant_turn_count",0),ExactTextV1.sha256(lu),ExactTextV1.sha256(la),la,o.optInt("stop_candidate_count",0),o.optInt("assistant_completion_candidate_count",0));
            CorrelatedAssistantReplyTrackerV1.Observation obs=replyTracker.observe(snap);replyWaitJournal.applyObservation(replyWorkflowId,replyStepId,obs);
            if(obs.captured){capturedReplyText=obs.exactReplyText;capturedReplySha=obs.exactReplySha256;replyTracking=false;if(readReplyButton!=null)readReplyButton.setEnabled(true);ConversationBindingV91 b=registry==null?null:registry.byId(targetExpectedBindingId);emit("TARGET_ASSISTANT_REPLY_CAPTURED",b,"CONFIRMED",jsonExtra("reply_digest",capturedReplySha,"reply_chars",capturedReplyText.length(),"receipt_basis","EXACT_CORRELATED_USER_PLUS_STABLE_COMPLETION"));status.setText("Correlated assistant reply captured. READ LAST REPLY is ready.");return;}
            if(obs.state==CorrelatedAssistantReplyTrackerV1.State.UNCERTAIN){replyTracking=false;ConversationBindingV91 b=registry==null?null:registry.byId(targetExpectedBindingId);emit("TARGET_REPLY_WATCH_FAILED",b,"UNKNOWN",jsonExtra("reason",obs.reason));return;}
            h.postDelayed(()->replyObserve(g),REPLY_POLL_MS);
        });
    }

    private void cancelReplyTracking(String reason){
        if(!replyTracking)return;replyTracking=false;replyGeneration++;if(replyWaitJournal!=null&&!replyWorkflowId.isEmpty())replyWaitJournal.markUncertain(replyWorkflowId,replyStepId,reason);ConversationBindingV91 b=registry==null?null:registry.byId(targetExpectedBindingId);emit("TARGET_REPLY_WATCH_FAILED",b,"UNKNOWN",jsonExtra("reason",reason));
    }

    private void speakCapturedReply(){
        if(capturedReplyText==null||capturedReplyText.isEmpty()){status.setText("No correlated reply has been captured yet.");return;}
        if(activeSpeechSession!=null&&activeSpeechSession.isRunning())return;
        final String sid="speech-"+UUID.randomUUID();
        activeSpeechSession=new SpeechOutputSessionV1(new AndroidTtsSpeechOutputFactoryV1(this),new SpeechOutputSessionV1.Listener(){
            @Override public void onReady(){}
            @Override public void onSessionStarted(String sessionId,String sourceExactSha256,int chunkCount){runOnUiThread(()->{if(stopSpeechButton!=null)stopSpeechButton.setEnabled(true);status.setText("Reading captured reply aloud…");emit("SPEECH_OUTPUT_STARTED",null,"UNKNOWN",jsonExtra("speech_id_digest",sha256(sessionId),"source_digest",sourceExactSha256,"chunk_count",chunkCount));});}
            @Override public void onSessionDone(String sessionId,String sourceExactSha256,int chunkCount){runOnUiThread(()->{if(stopSpeechButton!=null)stopSpeechButton.setEnabled(false);if(readReplyButton!=null)readReplyButton.setEnabled(true);status.setText("Read aloud complete.");emit("SPEECH_OUTPUT_RECEIPT",null,"CONFIRMED",jsonExtra("speech_id_digest",sha256(sessionId),"source_digest",sourceExactSha256,"chunk_count",chunkCount));});}
            @Override public void onSessionFailed(String sessionId,String sourceExactSha256,String errorClass){runOnUiThread(()->{if(stopSpeechButton!=null)stopSpeechButton.setEnabled(false);status.setText("Read aloud stopped: "+errorClass);emit("SPEECH_OUTPUT_FAILED",null,"UNKNOWN",jsonExtra("speech_id_digest",sha256(sessionId),"source_digest",sourceExactSha256,"reason",errorClass));});}
        },1800);
        if(readReplyButton!=null)readReplyButton.setEnabled(false);
        if(!activeSpeechSession.start(sid,capturedReplyText)){if(readReplyButton!=null)readReplyButton.setEnabled(true);status.setText("Read aloud could not start.");}
    }

    private void stopSpeechOutput(){if(activeSpeechSession!=null&&activeSpeechSession.isRunning())activeSpeechSession.cancel();}

'''
s=s.replace(marker,methods+marker,1)

# Destroy local speech provider but leave reply wait journal durable for later recovery versions.
old='if(speechTranscriber!=null)speechTranscriber.destroy();if(worker!=null)worker.destroy();'
new='if(speechTranscriber!=null)speechTranscriber.destroy();if(activeSpeechSession!=null)activeSpeechSession.destroy();if(worker!=null)worker.destroy();'
assert s.count(old)==1
s=s.replace(old,new,1)

# Identity advance.
cfg_old=PKG/'TelemetryConfigV101.java';cfg_new=PKG/'TelemetryConfigV102.java';cfg=cfg_old.read_text().replace('TelemetryConfigV101','TelemetryConfigV102');assert 'CONFIGURED=false' in cfg;cfg_new.write_text(cfg)
gradle=ROOT/'app/build.gradle';g=gradle.read_text();assert g.count('versionCode 102')==1;assert g.count("versionName '0.90.7-stable-dashboard-exact-text-workflow-journal'")==1;g=g.replace('versionCode 102','versionCode 103',1).replace("versionName '0.90.7-stable-dashboard-exact-text-workflow-journal'","versionName '0.90.8-stable-dashboard-correlated-reply-read-aloud'",1);gradle.write_text(g)
man=ROOT/'app/src/main/AndroidManifest.xml';m=man.read_text();assert m.count('OrchestratorDashboardV101ExactTextWorkflowActivity')==1;m=m.replace('OrchestratorDashboardV101ExactTextWorkflowActivity','OrchestratorDashboardV102ReplyReadAloudActivity',1);man.write_text(m)

out=new_java.write_text(s)
for required in [
    'TARGET_ASSISTANT_REPLY_CAPTURED','SPEECH_OUTPUT_RECEIPT','READ LAST REPLY','CorrelatedAssistantReplyTrackerV1','AssistantReplyWaitJournalV1','SpeechOutputSessionV1','user_turn_count:U.length','assistant_turn_count:A.length','EXACT_CORRELATED_USER_PLUS_STABLE_COMPLETION','TARGET_SEND_RECEIPT','PREVIEW — NOT COMMITTED','WorkflowJournalGuardV1']:
    assert required in s,required
assert s.count('targetChatEffectDispatches++')==1
assert s.count('.click()')==2
print('PASS v0.90.8 generator: correlated exact assistant-reply capture + manual local read aloud + unchanged explicit one-shot target authority')
