#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v102_dashboard_reply_read_aloud.py',run_name='__main__')
p=PKG/'OrchestratorDashboardV102ReplyReadAloudActivity.java'
s=p.read_text()

def replace_method(src, marker, replacement):
    start=src.index(marker)
    brace=src.index('{', start)
    i=brace
    depth=0
    state='code'
    esc=False
    while i < len(src):
        c=src[i]
        n=src[i+1] if i+1 < len(src) else ''
        if state=='code':
            if c=='"': state='str'; esc=False
            elif c=="'": state='char'; esc=False
            elif c=='/' and n=='/': state='line'; i+=1
            elif c=='/' and n=='*': state='block'; i+=1
            elif c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0:
                    return src[:start]+replacement+src[i+1:]
        elif state=='str':
            if esc: esc=False
            elif c=='\\': esc=True
            elif c=='"': state='code'
        elif state=='char':
            if esc: esc=False
            elif c=='\\': esc=True
            elif c=="'": state='code'
        elif state=='line':
            if c=='\n': state='code'
        elif state=='block':
            if c=='*' and n=='/': state='code'; i+=1
        i+=1
    raise AssertionError('method close not found: '+marker)

assert 'import android.view.View;\n' in s
s=s.replace('import android.view.View;\n','import android.view.View;\nimport android.view.WindowInsets;\nimport android.view.DisplayCutout;\n',1)
assert 'import android.os.Looper;\n' in s
s=s.replace('import android.os.Looper;\n','import android.os.Looper;\nimport android.os.Build;\n',1)
old='        setContentView(root);'
new='''        if(Build.VERSION.SDK_INT>=21){
            root.setOnApplyWindowInsetsListener((v,insets)->{
                int left=insets.getSystemWindowInsetLeft(),topInset=insets.getSystemWindowInsetTop(),right=insets.getSystemWindowInsetRight(),bottom=insets.getSystemWindowInsetBottom();
                if(Build.VERSION.SDK_INT>=28){DisplayCutout cutout=insets.getDisplayCutout();if(cutout!=null){left=Math.max(left,cutout.getSafeInsetLeft());topInset=Math.max(topInset,cutout.getSafeInsetTop());right=Math.max(right,cutout.getSafeInsetRight());bottom=Math.max(bottom,cutout.getSafeInsetBottom());}}
                v.setPadding(left,topInset,right,bottom);return insets;
            });
        }
        setContentView(root);
        if(Build.VERSION.SDK_INT>=21)root.post(()->root.requestApplyInsets());'''
assert s.count(old)==1
s=s.replace(old,new,1)

anchor='private SpeechOutputSessionV1 activeSpeechSession;'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+' private TemporaryPlannerJournalV1 disposablePlannerJournal; private String disposablePlannerAttemptId=""; private boolean disposableTempEntryDispatched=false,pendingPlannerExecutable=false; private int tempReceiptStableHits=0,normalRestoreStableHits=0; private WebChatFreshnessGuardV1 replyFreshnessGuard; private boolean replyReloadDispatched=false;',1)
anchor='replyWaitJournal=new AssistantReplyWaitJournalV1(getSharedPreferences("cp_v102_reply_wait",MODE_PRIVATE));'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+' disposablePlannerJournal=new TemporaryPlannerJournalV1(getSharedPreferences("cp_v102_disposable_planner",MODE_PRIVATE));',1)

old='if(targetExecutionRunning){long g=targetExecutionGeneration;h.postDelayed(()->targetObserve(g),350L);return;} if(plannerRunning){long g=plannerGeneration;h.postDelayed(()->plannerObserve(g),350L);return;} if(pendingOpenPath!=null)h.postDelayed(()->verifyOpenReceipt(),350L);'
new='if(targetExecutionRunning){long g=targetExecutionGeneration;h.postDelayed(()->targetObserve(g),350L);return;} if(plannerRunning){long g=plannerGeneration;h.postDelayed(()->plannerObserve(g),350L);return;} if(replyTracking){long g=replyGeneration;h.postDelayed(()->replyObserve(g),500L);return;} if(pendingOpenPath!=null)h.postDelayed(()->verifyOpenReceipt(),350L);'
assert s.count(old)==1
s=s.replace(old,new,1)

start_planner=r'''    private void startPlannerRequest(){
        if(isVoiceBusy()){status.setText("Finish voice input first.");return;}
        if(plannerRunning||targetExecutionRunning)return;
        if(replyTracking)cancelReplyTracking("SUPERSEDED_BY_NEW_PLANNER");
        pendingRecipe=null;pendingTargetBindingId="";pendingTargetPathHash="";pendingTargetAlias="";pendingTargetMessage="";pendingPlannerExecutable=false;
        if(executeButton!=null){executeButton.setText("EXECUTE");executeButton.setEnabled(false);}
        if(scheduler!=null&&scheduler.scanning){status.setText("Finish Refresh all first.");return;}
        String c=plannerInput.getText().toString().trim();if(c.isEmpty()||c.length()>MAX_PLANNER_COMMAND_CHARS){status.setText("Enter a bounded Planner command.");return;}
        plannerRequestId="req-"+UUID.randomUUID();plannerRequestDigest=sha256(c);plannerPacket=buildPlannerPacket(c);disposablePlannerAttemptId="dplan-"+UUID.randomUUID();disposableTempEntryDispatched=false;
        plannerGeneration++;plannerPolls=0;plannerRunning=true;plannerPhase="WAIT_FRESH_HOME";plannerExpectedComposerHash="-";plannerBaselineAssistantHash="-";tempReceiptStableHits=0;normalRestoreStableHits=0;
        plannerButton.setEnabled(false);plannerResult.setText("Planner: opening fresh home before disposable Temporary Chat...");
        boolean ok=plannerJournal.edit().putString("request_id",plannerRequestId).putString("request_digest",plannerRequestDigest).putString("status","CLAIMED_BEFORE_FRESH_PLANNER_NAV").commit();
        if(!ok||disposablePlannerJournal==null||!disposablePlannerJournal.begin(disposablePlannerAttemptId,plannerRequestId,plannerRequestDigest)){plannerFail("DISPOSABLE_PLANNER_JOURNAL_BEGIN_FAILED");return;}
        emit("PLANNER_REQUEST_STARTED",null,"UNKNOWN",jsonExtra("request_digest",plannerRequestDigest,"planner_phase",plannerPhase));showPlannerSurface("Planner transaction active in disposable-session mode. Target execution still requires explicit EXECUTE.");foreground.loadUrl("https://chatgpt.com/");
    }'''
s=replace_method(s,'    private void startPlannerRequest(){',start_planner)

planner_observe=r'''    private void plannerObserve(long g){
        if(!plannerRunning||g!=plannerGeneration)return;
        if(++plannerPolls>MAX_PLANNER_POLLS){plannerFail("PLANNER_OBSERVATION_BUDGET_EXHAUSTED");return;}
        if("WAIT_TEMP_RECEIPT".equals(plannerPhase)){plannerObserveTempReceipt(g);return;}
        if("WAIT_NORMAL_RESTORE".equals(plannerPhase)){plannerObserveNormalRestore(g);return;}
        eval(foreground,plannerReadJs(),o->{
            if(!plannerRunning||g!=plannerGeneration)return;
            if(!o.optBoolean("success",false)){plannerLater(g);return;}
            String path=o.optString("local_path","");
            if("WAIT_FRESH_HOME".equals(plannerPhase)){
                boolean fresh="complete".equals(o.optString("ready",""))&&"/".equals(path)&&o.optInt("turn_count",-1)==0&&o.optInt("composer_candidate_count",0)==1&&o.optInt("stop_candidate_count",0)==0;
                if(!fresh){plannerLater(g);return;}
                plannerResult.setText("Planner: fresh normal home observed; entering Temporary Chat...");plannerEnterTemp(g);return;
            }
            if("WAIT_COMPOSER_RECEIPT".equals(plannerPhase)){
                boolean temp="TEMP".equals(o.optString("semantic_temp_state",""));
                if(!temp||o.optInt("composer_candidate_count",0)!=1||o.optInt("send_candidate_count",0)!=1||!plannerExpectedComposerHash.equals(o.optString("composer_hash","-"))){plannerLater(g);return;}
                plannerSend(g);return;
            }
            if("WAIT_SEND_RECEIPT".equals(plannerPhase)){
                String lut=o.optString("last_user_text","");boolean userCorr=lut.contains(plannerRequestId)&&lut.contains(plannerRequestDigest);boolean temp="TEMP".equals(o.optString("semantic_temp_state",""));
                if(!userCorr||!temp||o.optInt("turn_count",0)<1){plannerLater(g);return;}
                plannerJournal.edit().putString("status","PLANNER_SEND_RECEIPT_CONFIRMED").commit();plannerPhase="WAIT_RESPONSE";plannerResult.setText("Planner: Temporary Chat send confirmed; waiting for correlated recipe...");emit("PLANNER_SEND_RECEIPT",null,"UNKNOWN",jsonExtra("request_digest",plannerRequestDigest,"planner_route_hash",sha256(path),"receipt_basis","REQUEST_ID_DIGEST_TEMP_SESSION"));plannerLater(g);return;
            }
            if("WAIT_RESPONSE".equals(plannerPhase)){
                String lut2=o.optString("last_user_text",""),lat=o.optString("last_assistant_text","");boolean userCorr2=lut2.contains(plannerRequestId)&&lut2.contains(plannerRequestDigest);String trimmed=lat.trim();boolean assistantCorr=lat.contains(plannerRequestId)&&lat.contains(plannerRequestDigest);boolean temp="TEMP".equals(o.optString("semantic_temp_state",""));
                boolean ready=temp&&userCorr2&&assistantCorr&&trimmed.startsWith("{")&&trimmed.endsWith("}")&&!"-".equals(o.optString("last_assistant_hash","-"))&&o.optInt("stop_candidate_count",0)==0&&o.optInt("assistant_completion_candidate_count",0)>=1;
                if(!ready){plannerLater(g);return;}
                plannerResult.setText("Planner: correlated Temporary Chat recipe received; persisting before cleanup...");plannerRecipe(lat);return;
            }
            plannerFail("PLANNER_UNKNOWN_PHASE");
        });
    }'''
s=replace_method(s,'    private void plannerObserve(long g){',planner_observe)

planner_send=r'''    private void plannerSend(long g){
        if(disposablePlannerJournal==null||!disposablePlannerJournal.claimPlannerSend(disposablePlannerAttemptId)){plannerFail("DISPOSABLE_PLANNER_SEND_CLAIM_FAILED");return;}
        if(!plannerJournal.edit().putString("status","CLAIMED_BEFORE_PLANNER_SEND").putString("composer_hash",plannerExpectedComposerHash).commit()){plannerFail("PLANNER_SEND_CLAIM_FAILED");return;}
        if(!disposablePlannerJournal.markPlannerSendInFlight(disposablePlannerAttemptId)){plannerFail("DISPOSABLE_PLANNER_SEND_IN_FLIGHT_JOURNAL_FAILED");return;}
        eval(foreground,plannerSendJs(plannerExpectedComposerHash),o->{
            if(!plannerRunning||g!=plannerGeneration)return;
            boolean ok=o.optBoolean("success",false)&&o.optBoolean("dispatched",false)&&o.optBoolean("click_observed",false)&&o.optInt("send_match_count",0)==1&&plannerExpectedComposerHash.equals(o.optString("composer_hash","-"));
            if(!ok){plannerFail("PLANNER_SEND_UNCERTAIN_NO_REPLAY");return;}
            plannerChatEffectDispatches++;
            if(!disposablePlannerJournal.markWaitingResult(disposablePlannerAttemptId)){plannerFail("DISPOSABLE_PLANNER_WAIT_RESULT_JOURNAL_FAILED");return;}
            plannerPhase="WAIT_SEND_RECEIPT";plannerResult.setText("Planner: sent once inside Temporary Chat; confirming receipt...");plannerJournal.edit().putString("status","PLANNER_SEND_DISPATCHED_AWAITING_RECEIPT").commit();emit("PLANNER_SEND_DISPATCH",null,"UNKNOWN",jsonExtra("request_digest",plannerRequestDigest,"planner_chat_effect_dispatches",plannerChatEffectDispatches,"target_chat_effect_dispatches",targetChatEffectDispatches,"temporary_session",true));plannerLater(g);
        });
    }'''
s=replace_method(s,'    private void plannerSend(long g){',planner_send)

planner_recipe=r'''    private void plannerRecipe(String raw){
        JSONObject r=parsePlannerRecipe(raw);if(r==null){plannerResult.setText("Planner reply rejected mechanically: "+plannerParseError);plannerFail("PLANNER_RECIPE_PARSE_REJECTED");return;}
        String st=r.optString("status","");JSONArray ops=r.optJSONArray("operations");int n=ops.length();pendingRecipe=r;pendingTargetBindingId="";pendingTargetPathHash="";pendingTargetAlias="";pendingTargetMessage="";pendingPlannerExecutable=false;
        if("READY".equals(st)&&n==1){JSONObject op=ops.optJSONObject(0);if(op!=null&&"chat.send_message".equals(op.optString("capability",""))){JSONObject tar=op.optJSONObject("target");ConversationBindingV91 rb=resolveChatRef(tar==null?"":tar.optString("chat_ref",""));if(rb!=null){JSONObject aa=op.optJSONObject("arguments");String pm=aa==null?"":aa.optString("message_text","");pendingTargetBindingId=rb.id;pendingTargetPathHash=rb.pathHash;pendingTargetAlias=rb.alias;pendingTargetMessage=pm;pendingPlannerExecutable=!pm.isEmpty();}}}
        String resultDigest=ExactTextV1.sha256(raw==null?"":raw);
        if(disposablePlannerJournal==null||!disposablePlannerJournal.persistResultReceipt(disposablePlannerAttemptId,resultDigest)){plannerFail("DISPOSABLE_PLANNER_RESULT_PERSIST_FAILED");return;}
        plannerJournal.edit().putString("status","RECIPE_ACCEPTED_LOCAL_AWAITING_TEMP_CLEANUP").putString("recipe_digest",resultDigest).commit();plannerResult.setText("Planner result persisted locally. Closing Temporary Chat...");plannerBeginTempCleanup(plannerGeneration);
    }'''
s=replace_method(s,'    private void plannerRecipe(String raw){',planner_recipe)

arm_reply=r'''    private void armReplyCapture(ConversationBindingV91 b,JSONObject postSend){
        if(b==null||replyWaitJournal==null)return;
        if(replyTracking)cancelReplyTracking("SUPERSEDED_BY_NEW_SEND");
        replyWorkflowId=activeWorkflowId;replyStepId=activeWorkflowStepId;capturedReplyText="";capturedReplySha="";replyPolls=0;replyGeneration++;long g=replyGeneration;replyReloadDispatched=false;
        String expectedUserSha=ExactTextV1.sha256(targetExpectedMessage);long expiry=System.currentTimeMillis()+REPLY_WAIT_TTL_MS;
        boolean armed=replyWaitJournal.arm(replyWorkflowId,replyStepId,b.pathHash,expectedUserSha,targetBaselineUserTurnCount,targetBaselineAssistantTurnCount,targetBaselineAssistantExactSha,expiry);
        if(!armed){emit("TARGET_REPLY_WATCH_FAILED",b,"UNKNOWN",jsonExtra("reason","REPLY_WAIT_JOURNAL_ARM_FAILED"));return;}
        replyTracker=new CorrelatedAssistantReplyTrackerV1(b.pathHash,expectedUserSha,targetBaselineUserTurnCount,targetBaselineAssistantTurnCount,targetBaselineAssistantExactSha);
        int pu=postSend==null?targetBaselineUserTurnCount+1:postSend.optInt("user_turn_count",targetBaselineUserTurnCount+1);int pa=postSend==null?targetBaselineAssistantTurnCount:postSend.optInt("assistant_turn_count",targetBaselineAssistantTurnCount);String seq=postSend==null?"-":postSend.optString("turn_sequence_digest","-");String lu=postSend==null?targetExpectedMessage:postSend.optString("last_user_text",targetExpectedMessage);String la=postSend==null?"":postSend.optString("last_assistant_text","");
        WebChatFreshnessGuardV1.Watermark wm=new WebChatFreshnessGuardV1.Watermark(b.pathHash,pu,pa,seq,ExactTextV1.sha256(lu),ExactTextV1.sha256(la));replyFreshnessGuard=new WebChatFreshnessGuardV1(b.pathHash,wm,true,12);replyTracking=true;
        if(readReplyButton!=null)readReplyButton.setEnabled(false);
        emit("TARGET_REPLY_WATCH_STARTED",b,"UNKNOWN",jsonExtra("workflow_id_digest",sha256(replyWorkflowId),"step_id",replyStepId,"freshness_must_advance",true));h.postDelayed(()->replyObserve(g),REPLY_POLL_MS);
    }'''
s=replace_method(s,'    private void armReplyCapture(ConversationBindingV91 b){',arm_reply)

reply_observe=r'''    private void replyObserve(long g){
        if(!replyTracking||g!=replyGeneration||replyTracker==null)return;
        if(++replyPolls>MAX_REPLY_POLLS){cancelReplyTracking("REPLY_OBSERVATION_BUDGET_EXHAUSTED");return;}
        eval(foreground,plannerReadJs(),o->{
            if(!replyTracking||g!=replyGeneration)return;
            if(!o.optBoolean("success",false)){h.postDelayed(()->replyObserve(g),REPLY_POLL_MS);return;}
            String path=o.optString("local_path",""),lu=o.optString("last_user_text",""),la=o.optString("last_assistant_text","");
            CorrelatedAssistantReplyTrackerV1.Snapshot snap=new CorrelatedAssistantReplyTrackerV1.Snapshot(sha256(path),o.optInt("user_turn_count",0),o.optInt("assistant_turn_count",0),ExactTextV1.sha256(lu),ExactTextV1.sha256(la),la,o.optInt("stop_candidate_count",0),o.optInt("assistant_completion_candidate_count",0));
            CorrelatedAssistantReplyTrackerV1.Observation obs=replyTracker.observe(snap);replyWaitJournal.applyObservation(replyWorkflowId,replyStepId,obs);
            if(obs.captured){capturedReplyText=obs.exactReplyText;capturedReplySha=obs.exactReplySha256;replyTracking=false;if(readReplyButton!=null)readReplyButton.setEnabled(true);ConversationBindingV91 b=registry==null?null:registry.byId(targetExpectedBindingId);emit("TARGET_ASSISTANT_REPLY_CAPTURED",b,"CONFIRMED",jsonExtra("reply_digest",capturedReplySha,"reply_chars",capturedReplyText.length(),"receipt_basis","EXACT_CORRELATED_USER_PLUS_STABLE_COMPLETION","freshness_basis","CORRELATED_ADVANCED"));status.setText("Correlated assistant reply captured. Reading it aloud...");speakCapturedReply();return;}
            if(obs.state==CorrelatedAssistantReplyTrackerV1.State.UNCERTAIN){replyTracking=false;ConversationBindingV91 b=registry==null?null:registry.byId(targetExpectedBindingId);emit("TARGET_REPLY_WATCH_FAILED",b,"UNKNOWN",jsonExtra("reason",obs.reason));return;}
            if(replyFreshnessGuard!=null){WebChatFreshnessGuardV1.Snapshot fs=new WebChatFreshnessGuardV1.Snapshot("complete".equals(o.optString("ready","")),sha256(path),o.optInt("user_turn_count",0),o.optInt("assistant_turn_count",0),o.optString("turn_sequence_digest","-"),ExactTextV1.sha256(lu),ExactTextV1.sha256(la),o.optInt("stop_candidate_count",0),o.optInt("stop_candidate_count",0)>0);WebChatFreshnessGuardV1.Observation fo=replyFreshnessGuard.observe(fs);if(fo.reloadRecommended&&!replyReloadDispatched){boolean claimed=targetJournal.edit().putString("status","CLAIMED_BEFORE_REPLY_FRESHNESS_RELOAD").putBoolean("reply_freshness_reload_consumed",true).commit();if(!claimed||!replyFreshnessGuard.markControlledReloadDispatched()){cancelReplyTracking("REPLY_FRESHNESS_RELOAD_CLAIM_FAILED");return;}replyReloadDispatched=true;ConversationBindingV91 b=registry==null?null:registry.byId(targetExpectedBindingId);emit("TARGET_REPLY_FRESHNESS_RELOAD",b,"UNKNOWN",jsonExtra("reason",fo.reason,"reload_count",1));foreground.loadUrl("https://chatgpt.com"+targetExpectedPath);return;}if(fo.state==WebChatFreshnessGuardV1.State.FRESHNESS_UNPROVEN){cancelReplyTracking("FRESHNESS_UNPROVEN");return;}}
            h.postDelayed(()->replyObserve(g),REPLY_POLL_MS);
        });
    }'''
s=replace_method(s,'    private void replyObserve(long g){',reply_observe)

old='armReplyCapture(b);plannerResult.setText('
new='armReplyCapture(b,o);plannerResult.setText('
assert s.count(old)==1
s=s.replace(old,new,1)
s=s.replace('status.setText("Read aloud stopped: "+errorClass);emit("SPEECH_OUTPUT_FAILED"','if(readReplyButton!=null)readReplyButton.setEnabled(true);status.setText("Read aloud stopped: "+errorClass);emit("SPEECH_OUTPUT_FAILED"',1)

old='temp_candidate_count:E.length,turn_count:T.length,user_turn_count:U.length,assistant_turn_count:A.length,turns:T,last_user_text:'
new='temp_candidate_count:E.length,turn_count:T.length,user_turn_count:U.length,assistant_turn_count:A.length,turn_sequence_digest:H(T.map(x=>x.role+\'|\'+x.exact_hash).join(\'~\')),turns:T,last_user_text:'
assert s.count(old)==1
s=s.replace(old,new,1)

planner_fail=r'''    private void plannerFail(String why){
        if(plannerJournal!=null)plannerJournal.edit().putString("status",why).commit();
        if(disposablePlannerJournal!=null&&!disposablePlannerAttemptId.isEmpty()){JSONObject dj=disposablePlannerJournal.load();String ds=dj==null?"":dj.optString("state","");if(TemporaryPlannerJournalV1.RESULT_PERSISTED.equals(ds)||TemporaryPlannerJournalV1.CLAIMED_BEFORE_EXIT.equals(ds)||TemporaryPlannerJournalV1.CLEANUP_UNCERTAIN.equals(ds))disposablePlannerJournal.markCleanupUncertain(disposablePlannerAttemptId,why);else if(!disposableTempEntryDispatched&&(TemporaryPlannerJournalV1.CLAIMED_BEFORE_ENTER.equals(ds)||TemporaryPlannerJournalV1.TEMP_CONFIRMED.equals(ds)||TemporaryPlannerJournalV1.CLAIMED_BEFORE_SEND.equals(ds)))disposablePlannerJournal.failPreSend(disposablePlannerAttemptId,why);}
        plannerRunning=false;plannerPhase="FAILED";if(plannerButton!=null)plannerButton.setEnabled(true);if(executeButton!=null)executeButton.setEnabled(false);emit("PLANNER_FAILED",null,"UNKNOWN",jsonExtra("request_digest",plannerRequestDigest,"reason",why,"planner_chat_effect_dispatches",plannerChatEffectDispatches,"target_chat_effect_dispatches",targetChatEffectDispatches));showDashboard("Planner stopped safely: "+why+". No target action executed or replayed.");
    }'''
s=replace_method(s,'    private void plannerFail(String why){',planner_fail)

marker='    private String plannerReadJs(){\n'
assert s.count(marker)==1
extra=r'''    private void plannerEnterTemp(long g){
        eval(foreground,tempControlStateJs(),o->{if(!plannerRunning||g!=plannerGeneration)return;if(!TemporaryChatSignaturesV1.exactEntryGate(o)){plannerFail("TEMP_ENTRY_GATE_NOT_EXACT_NORMAL");return;}eval(foreground,tempClickJs(true),c->{if(!plannerRunning||g!=plannerGeneration)return;boolean ok=c.optBoolean("success",false)&&c.optBoolean("dispatched",false)&&c.optBoolean("click_observed",false)&&c.optInt("match_count",0)==1;if(!ok){plannerFail("TEMP_ENTRY_DISPATCH_UNCERTAIN_NO_REPLAY");return;}disposableTempEntryDispatched=true;plannerPhase="WAIT_TEMP_RECEIPT";tempReceiptStableHits=0;emit("DISPOSABLE_PLANNER_TEMP_ENTRY_DISPATCH",null,"UNKNOWN",jsonExtra("request_digest",plannerRequestDigest));plannerLater(g);});});
    }

    private void plannerObserveTempReceipt(long g){
        eval(foreground,tempControlStateJs(),o->{if(!plannerRunning||g!=plannerGeneration)return;boolean match=TemporaryChatSignaturesV1.exactExitGate(o);tempReceiptStableHits=match?tempReceiptStableHits+1:0;if(tempReceiptStableHits>=2){if(!disposablePlannerJournal.confirmTemp(disposablePlannerAttemptId)){plannerFail("TEMP_RECEIPT_JOURNAL_FAILED");return;}plannerBaselineAssistantHash="-";plannerResult.setText("Temporary Chat confirmed; writing Planner packet...");plannerWrite(g);return;}plannerLater(g);});
    }

    private void plannerBeginTempCleanup(long g){
        eval(foreground,tempControlStateJs(),o->{if(!plannerRunning||g!=plannerGeneration)return;if(!TemporaryChatSignaturesV1.exactExitGate(o)){if(disposablePlannerJournal!=null)disposablePlannerJournal.markCleanupUncertain(disposablePlannerAttemptId,"TEMP_EXIT_GATE_DRIFT");plannerFail("TEMP_EXIT_GATE_DRIFT");return;}if(!disposablePlannerJournal.claimExit(disposablePlannerAttemptId)){plannerFail("TEMP_EXIT_CLAIM_FAILED");return;}eval(foreground,tempClickJs(false),c->{if(!plannerRunning||g!=plannerGeneration)return;boolean ok=c.optBoolean("success",false)&&c.optBoolean("dispatched",false)&&c.optBoolean("click_observed",false)&&c.optInt("match_count",0)==1;if(!ok){disposablePlannerJournal.markCleanupUncertain(disposablePlannerAttemptId,"TEMP_EXIT_DISPATCH_UNCERTAIN");plannerFail("TEMP_EXIT_DISPATCH_UNCERTAIN");return;}plannerPhase="WAIT_NORMAL_RESTORE";normalRestoreStableHits=0;emit("DISPOSABLE_PLANNER_TEMP_EXIT_DISPATCH",null,"UNKNOWN",jsonExtra("request_digest",plannerRequestDigest));plannerLater(g);});});
    }

    private void plannerObserveNormalRestore(long g){
        eval(foreground,tempControlStateJs(),o->{if(!plannerRunning||g!=plannerGeneration)return;boolean match=TemporaryChatSignaturesV1.exactEntryGate(o);normalRestoreStableHits=match?normalRestoreStableHits+1:0;if(normalRestoreStableHits>=2){if(!disposablePlannerJournal.confirmNormal(disposablePlannerAttemptId)){plannerFail("NORMAL_RESTORE_JOURNAL_FAILED");return;}plannerCompleteRecipeAfterCleanup();return;}plannerLater(g);});
    }

    private void plannerCompleteRecipeAfterCleanup(){
        JSONObject r=pendingRecipe;if(r==null){plannerFail("PERSISTED_RECIPE_MISSING_AFTER_CLEANUP");return;}String st=r.optString("status","");JSONArray ops=r.optJSONArray("operations");int n=ops==null?0:ops.length();plannerRunning=false;plannerPhase="RECIPE_READY";plannerButton.setEnabled(true);executeButton.setText(pendingPlannerExecutable?"EXECUTE → "+pendingTargetAlias:"EXECUTE");executeButton.setEnabled(pendingPlannerExecutable);plannerJournal.edit().putString("status","RECIPE_ACCEPTED_TEMP_CLEANUP_CONFIRMED").commit();emit("PLANNER_RECIPE_ACCEPTED",null,st,jsonExtra("request_digest",plannerRequestDigest,"recipe_status",st,"operation_count",n,"execution_available",pendingPlannerExecutable,"temporary_cleanup_confirmed",true,"target_chat_effect_dispatches",targetChatEffectDispatches));try{String preview=pendingTargetMessage.length()>240?pendingTargetMessage.substring(0,240)+"…":pendingTargetMessage;plannerResult.setText(pendingPlannerExecutable?"TARGET: "+pendingTargetAlias+"\nACTION: Send message → wait for exact correlated reply → auto read aloud\nMESSAGE: "+preview+"\nTARGET FROZEN: YES\nTEMP PLANNER CLEANUP: CONFIRMED\n\nRecipe "+st+"\n"+r.toString(2):"Recipe "+st+" · not executable in this prototype\nTEMP PLANNER CLEANUP: CONFIRMED\n"+r.toString(2));}catch(Exception e){plannerResult.setText("Recipe "+st+" accepted after Temporary Chat cleanup.");}showDashboard(pendingPlannerExecutable?"Target frozen: "+pendingTargetAlias+". EXECUTE sends once, waits for the correlated reply, refreshes once if stale, then reads it aloud.":"Planner recipe received; no executable single-send action.");
    }

    private String tempControlStateJs(){
        return "(function(){try{"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const DS=e=>{const v=N(e.getAttribute('data-state'));if(['active','selected','checked','on'].includes(v))return 'ACTIVE';if(['inactive','unselected','unchecked','off'].includes(v))return 'INACTIVE';if(v==='open')return 'OPEN';if(v==='closed')return 'CLOSED';return v?'OTHER':'NONE';};const HC=e=>{const h=e.getAttribute('href')||'';if(!h)return 'NONE';try{const u=new URL(h,location.href),p=u.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';return 'OTHER';}catch(x){return 'OTHER';}};const RC=()=>{const p=location.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';return 'OTHER_ROUTE';};const SEM=(label,tid)=>{const x=N(label),t=N(tid),z=x+' '+t;if(z.includes('temporary')||x==='temp'||t.includes('temp'))return 'TEMP';return 'OTHER';};"+
            "const q=Array.from(document.querySelectorAll('button,a,[role],[aria-selected],[aria-pressed],[data-state],[data-testid]')).filter(V),T=[];for(const e of q){const tag=(e.tagName||'').toLowerCase(),role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none')),actionable=tag==='button'||tag==='a'||['button','tab','menuitem','radio','switch','option'].includes(role)||e.hasAttribute('aria-selected')||e.hasAttribute('aria-pressed')||e.hasAttribute('data-state');if(!actionable)continue;const label=e.getAttribute('aria-label')||e.innerText||e.textContent||'',tid=e.getAttribute('data-testid')||'';if(SEM(label,tid)!=='TEMP')continue;const lh=H(N(label)),th=H(tid),hc=HC(e),sh=H([tag,role,'TEMP',lh,th,hc].join('|'));T.push({e:e,tag:tag,role:role,lh:lh,th:th,ds:DS(e),sel:e.getAttribute('aria-selected')==='true'?1:0,prs:e.getAttribute('aria-pressed')==='true'?1:0,exp:e.getAttribute('aria-expanded')==='true'?1:0,dis:e.hasAttribute('disabled')?1:0,hc:hc,sh:sh});}const urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));const E=T.filter(x=>urlhint?(x.lh==='ae0e16e6'&&x.sh==='34d052a8'):(x.lh==='1a957a52'&&x.sh==='b9c97d1e')),c=E.length===1?E[0]:null;let comphint=false;for(const e of Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).filter(V)){const z=N((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('placeholder')||''));if(z.includes('temporary')||z==='temp'){comphint=true;break;}}const rows=E.map(x=>[x.tag,x.role,x.lh,x.th,x.ds,x.sel,x.prs].join('|')).sort();return JSON.stringify({success:true,ready:document.readyState,route_class:RC(),url_temp_hint:urlhint,composer_temp_hint:comphint,temp_candidate_count:E.length,temp_semantic_set_hash:H(rows.join('~')),candidate_tag:c?c.tag:'-',candidate_role:c?c.role:'-',candidate_label_hash:c?c.lh:'-',candidate_testid_hash:c?c.th:'-',candidate_data_state:c?c.ds:'NONE',candidate_selected:c?c.sel:-1,candidate_pressed:c?c.prs:-1,candidate_expanded:c?c.exp:-1,candidate_disabled:c?c.dis:-1,candidate_href_class:c?c.hc:'-',candidate_struct_hash:c?c.sh:'-'});"+
            "}catch(e){return JSON.stringify({success:false,error_class:'TEMP_SCAN_EXCEPTION'});}})();";
    }

    private String tempClickJs(boolean enter){
        final String el=enter?TemporaryChatSignaturesV1.NORMAL_LABEL_HASH:TemporaryChatSignaturesV1.TEMP_LABEL_HASH,es=enter?TemporaryChatSignaturesV1.NORMAL_STRUCT_HASH:TemporaryChatSignaturesV1.TEMP_STRUCT_HASH;final boolean expectedUrl=!enter;
        return "(function(){try{const EL='"+el+"',ES='"+es+"',EU="+(expectedUrl?"true":"false")+";const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const HC=e=>{const h=e.getAttribute('href')||'';if(!h)return 'NONE';try{const u=new URL(h,location.href),p=u.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';return 'OTHER';}catch(x){return 'OTHER';}};const q=Array.from(document.querySelectorAll('button,a,[role],[aria-selected],[aria-pressed],[data-state],[data-testid]')).filter(V),T=[];for(const e of q){const tag=(e.tagName||'').toLowerCase(),role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none')),label=e.getAttribute('aria-label')||e.innerText||e.textContent||'',tid=e.getAttribute('data-testid')||'',z=N(label)+' '+N(tid);if(!(z.includes('temporary')||N(label)==='temp'||N(tid).includes('temp')))continue;const lh=H(N(label)),th=H(tid),hc=HC(e),sh=H([tag,role,'TEMP',lh,th,hc].join('|'));T.push({e:e,tag:tag,role:role,lh:lh,th:th,hc:hc,sh:sh,dis:e.hasAttribute('disabled')?1:0,sel:e.getAttribute('aria-selected')==='true'?1:0,prs:e.getAttribute('aria-pressed')==='true'?1:0,exp:e.getAttribute('aria-expanded')==='true'?1:0});}const M=T.filter(x=>x.lh===EL&&x.sh===ES),urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));if(M.length!==1)return JSON.stringify({success:false,reason:'EXACT_SIGNATURE_COUNT',match_count:M.length,dispatched:false,click_observed:false});const t=M[0];if(urlhint!==EU||t.tag!=='button'||t.role!=='button'||t.hc!=='NONE'||t.dis!==0||t.sel!==0||t.prs!==0||t.exp!==0)return JSON.stringify({success:false,reason:'STATE_OR_HASH',match_count:1,dispatched:false,click_observed:false});let observed=false;t.e.addEventListener('click',()=>{observed=true;},{capture:true,once:true});t.e.click();return JSON.stringify({success:true,reason:'EXACT_TEMP_ELEMENT_CLICK',match_count:1,dispatched:true,click_observed:observed});}catch(e){return JSON.stringify({success:false,reason:'TEMP_CLICK_EXCEPTION',match_count:0,dispatched:false,click_observed:false});}})();";
    }

'''
s=s.replace(marker,extra+marker,1)

for required in [
    'TemporaryPlannerJournalV1','TemporaryChatSignaturesV1','WAIT_TEMP_RECEIPT','WAIT_NORMAL_RESTORE','TEMP PLANNER CLEANUP: CONFIRMED',
    'WebChatFreshnessGuardV1','markControlledReloadDispatched','FRESHNESS_UNPROVEN','TARGET_REPLY_FRESHNESS_RELOAD',
    'TARGET_ASSISTANT_REPLY_CAPTURED','speakCapturedReply();','SPEECH_OUTPUT_RECEIPT','turn_sequence_digest',
    'setOnApplyWindowInsetsListener','DisplayCutout','getSafeInsetTop','TARGET_SEND_RECEIPT','PREVIEW — NOT COMMITTED','WorkflowJournalGuardV1'
]:
    assert required in s,required
assert s.count('targetChatEffectDispatches++')==1
assert s.count('.click()')==4, s.count('.click()')
assert s.count('foreground.loadUrl("https://chatgpt.com"+targetExpectedPath)')==1
p.write_text(s)
print('PASS v0.90.8 fixed prototype: disposable Planner + exact send + correlated freshness-safe reply + auto read aloud + cutout/status safe interactive insets')
