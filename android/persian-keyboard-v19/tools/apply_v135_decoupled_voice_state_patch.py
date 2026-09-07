from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.35 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


# v1.35 is an architectural correction, not another selection timeout tweak.
# Real-device v1.34 evidence exposed three coupled state machines:
#   1) editor projection uncertainty could terminate healthy speech;
#   2) internal selection re-anchor could fight an intentional user caret tap;
#   3) the legacy finish-ACK timeout was not scoped to a voice session, so a
#      stale callback could land on a later recording.
#
# v1.35 separates capture/transport state from editor-projection state. Losing a
# safe live-text projection can pause/retry publication, but it cannot stop audio.
# User intent is attributed by a fresh system touch START correlated with an
# off-tail selection change; onUpdateEditorToolType is no longer required. The
# old 90 ms automatic re-anchor is removed from active selection handling. Finish
# fallback callbacks are scoped to the exact voice-session epoch and WebSocket.

s = rep(s,
'''    private long liveSyncFailureSince;\n    private String voiceLeftBoundary = "";\n''',
'''    private long liveSyncFailureSince;\n    private boolean liveSyncRetryScheduled;\n    private long lastUnattributedOffTailSelectionUptime;\n    private volatile int voiceSessionEpoch;\n    private volatile int finishAckEpoch;\n    private String voiceLeftBoundary = "";\n''',
    'decoupled projection/session state')

old_interaction = r'''    private boolean hasRecentEditorUserInteraction(){
        long now=android.os.SystemClock.uptimeMillis();
        if(!running||voiceStartedUptime<=0L||now-voiceStartedUptime<300L)return false;

        long touchGeneration=SendAccessibilityService.userTouchGeneration();
        long touchEventTime=SendAccessibilityService.latestUserTouchEventTime();
        if(touchGeneration<=voiceStartTouchGeneration
                ||touchEventTime<=voiceStartedUptime+200L
                ||now<touchEventTime
                ||now-touchEventTime>1000L)return false;

        // onUpdateEditorToolType is no longer trusted on its own. It must be a
        // near-immediate consequence of the same fresh system touch-start event.
        if(lastEditorToolInteractionUptime<=voiceStartedUptime+200L
                ||now<lastEditorToolInteractionUptime
                ||now-lastEditorToolInteractionUptime>1000L)return false;
        long correlation=lastEditorToolInteractionUptime-touchEventTime;
        return correlation>=0L&&correlation<=700L;
    }
'''
new_interaction = r'''    private boolean hasRecentEditorUserInteraction(){
        long now=android.os.SystemClock.uptimeMillis();
        if(!running||voiceStartedUptime<=0L||now-voiceStartedUptime<250L)return false;
        long touchGeneration=SendAccessibilityService.userTouchGeneration();
        long touchEventTime=SendAccessibilityService.latestUserTouchEventTime();
        return touchGeneration>voiceStartTouchGeneration
                &&touchEventTime>voiceStartedUptime+150L
                &&now>=touchEventTime
                &&now-touchEventTime<=1000L;
    }

    private boolean inSelectionHoldoff(){
        long t=lastUnattributedOffTailSelectionUptime;
        if(t<=0L)return false;
        long now=android.os.SystemClock.uptimeMillis();
        return now>=t&&now-t<750L;
    }
'''
s = rep(s, old_interaction, new_interaction, 'fresh touch plus off-tail selection attribution')

s = rep(s,
'''            if(!hasRecentEditorUserInteraction()){\n                selectionConfirmationPending=false;\n                scheduleInternalSelectionReanchor();\n                return;\n            }\n''',
'''            if(!hasRecentEditorUserInteraction()){\n                selectionConfirmationPending=false;\n                lastUnattributedOffTailSelectionUptime=android.os.SystemClock.uptimeMillis();\n                return;\n            }\n''',
    'confirmed off-tail selection must not auto-reanchor')

s = rep(s,
'''        if(!hasRecentEditorUserInteraction()){\n            scheduleInternalSelectionReanchor();\n            return;\n        }\n        scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);\n''',
'''        if(!hasRecentEditorUserInteraction()){\n            // Editor/WebView selection churn is not user intent. Do not fight it\n            // by moving the caret back. A brief holdoff also gives a real user\n            // tap time to be followed by a manual key, whose existing path stops\n            // voice deterministically before committing that key.\n            lastUnattributedOffTailSelectionUptime=android.os.SystemClock.uptimeMillis();\n            return;\n        }\n        scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);\n''',
    'selection callback no active reanchor')

s = rep(s,
'''    private boolean recoverVoiceBoundaryOwnership(){\n        if(!running||hasRecentEditorUserInteraction()||!voiceBoundaryCaptured)return false;\n''',
'''    private boolean recoverVoiceBoundaryOwnership(){\n        if(!running||hasRecentEditorUserInteraction()||inSelectionHoldoff()||!voiceBoundaryCaptured)return false;\n''',
    'boundary recovery respects user-selection holdoff')

s = rep(s,
'''    private boolean recoverOwnedVoiceCursor(){\n        if(!running||hasRecentEditorUserInteraction())return false;\n        if(recoverVoiceBoundaryOwnership())return true;\n''',
'''    private boolean recoverOwnedVoiceCursor(){\n        if(!running||hasRecentEditorUserInteraction()||inSelectionHoldoff())return false;\n        if(recoverVoiceBoundaryOwnership())return true;\n''',
    'cursor recovery respects user-selection holdoff')

old_sync = r'''    private void clearLiveSyncFailure(){
        if(liveSyncFailureSince==0L)return;
        liveSyncFailureSince=0L;
        liveSyncRecoveryEpoch++;
        if(running)setStatus(listeningText());
    }

    private void noteLiveSyncFailure(){
        if(liveSyncFailureSince!=0L)return;
        liveSyncFailureSince=android.os.SystemClock.uptimeMillis();
        final int epoch=++liveSyncRecoveryEpoch;
        setStatus(persian?"در حال بازیابی همگام‌سازی متن زنده…":"Recovering live text sync…");
        main.postDelayed(()->{
            if(epoch!=liveSyncRecoveryEpoch||!running||liveSyncFailureSince==0L)return;
            if(recoverOwnedVoiceCursor()){
                clearLiveSyncFailure();
                return;
            }
            stopVoiceForManualInput();
            setStatus("Voice stopped — live text sync lost");
        },1500L);
    }
'''
new_sync = r'''    private void clearLiveSyncFailure(){
        if(liveSyncFailureSince==0L&&!liveSyncRetryScheduled)return;
        liveSyncFailureSince=0L;
        liveSyncRetryScheduled=false;
        liveSyncRecoveryEpoch++;
        if(running)setStatus(listeningText());
    }

    private void armLiveSyncRetry(){
        if(liveSyncRetryScheduled||!running||liveSyncFailureSince==0L)return;
        liveSyncRetryScheduled=true;
        final int epoch=liveSyncRecoveryEpoch;
        long age=android.os.SystemClock.uptimeMillis()-liveSyncFailureSince;
        long delay=age<1500L?240L:650L;
        main.postDelayed(()->{
            liveSyncRetryScheduled=false;
            if(epoch!=liveSyncRecoveryEpoch||!running||liveSyncFailureSince==0L)return;
            if(recoverOwnedVoiceCursor()){
                clearLiveSyncFailure();
                publish(false);
                return;
            }
            long elapsed=android.os.SystemClock.uptimeMillis()-liveSyncFailureSince;
            if(elapsed>=1500L){
                setStatus(persian?"در حال ضبط — نمایش زنده متن با تأخیر":"Recording — live text delayed");
            }
            armLiveSyncRetry();
        },delay);
    }

    private void noteLiveSyncFailure(){
        if(liveSyncFailureSince==0L){
            liveSyncFailureSince=android.os.SystemClock.uptimeMillis();
            liveSyncRecoveryEpoch++;
            setStatus(persian?"در حال بازیابی همگام‌سازی متن زنده…":"Recovering live text sync…");
        }
        armLiveSyncRetry();
    }
'''
s = rep(s, old_sync, new_sync, 'projection failure must not terminate capture')

s = rep(s,
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; livePartialTail=""; programmaticSelectionEditDepth=0; hasLastProgrammaticSelection=false; lastProgrammaticSelectionStart=-1; lastProgrammaticSelectionEnd=-1; selectionConfirmationEpoch++; selectionConfirmationPending=false; internalSelectionReanchorEpoch++; liveSyncRecoveryEpoch++; liveSyncFailureSince=0L; voiceStartedUptime=android.os.SystemClock.uptimeMillis(); voiceStartTouchGeneration=SendAccessibilityService.userTouchGeneration(); lastEditorToolInteractionUptime=0L; sendAfterVoiceStop=false; updateMicUi();\n''',
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; livePartialTail=""; programmaticSelectionEditDepth=0; hasLastProgrammaticSelection=false; lastProgrammaticSelectionStart=-1; lastProgrammaticSelectionEnd=-1; selectionConfirmationEpoch++; selectionConfirmationPending=false; internalSelectionReanchorEpoch++; liveSyncRecoveryEpoch++; liveSyncFailureSince=0L; liveSyncRetryScheduled=false; lastUnattributedOffTailSelectionUptime=0L; voiceSessionEpoch++; finishAckEpoch++; voiceStartedUptime=android.os.SystemClock.uptimeMillis(); voiceStartTouchGeneration=SendAccessibilityService.userTouchGeneration(); lastEditorToolInteractionUptime=0L; sendAfterVoiceStop=false; updateMicUi();\n''',
    'reset decoupled voice state on start')

old_finish = r'''    private void maybeFinish(){
        WebSocket ws; synchronized(audioLock){if(!running||completed||finishSent||!audioDone||!sonioxReady||webSocket==null)return;if(!flushLocked(webSocket)){ws=null;}else{finishSent=true;ws=webSocket;}}
        if(ws==null){finishWithText("Audio send error");return;}if(!ws.send("")){finishWithText("Finish send error");return;}main.postDelayed(()->{if(running&&!completed)finishWithText("Done (finish ACK timeout)");},FINISH_TIMEOUT_MS);
    }
'''
new_finish = r'''    private void maybeFinish(){
        final int session=voiceSessionEpoch;
        final int ack;
        final WebSocket ws;
        synchronized(audioLock){
            if(!running||completed||finishSent||!audioDone||!sonioxReady||webSocket==null)return;
            if(!flushLocked(webSocket)){
                ws=null;
                ack=finishAckEpoch;
            }else{
                finishSent=true;
                ws=webSocket;
                ack=++finishAckEpoch;
            }
        }
        // Once stop was requested, transport-finalization errors are best-effort
        // completion conditions, not reasons to destabilize or revive recording.
        if(ws==null){finishWithText("Done");return;}
        if(!ws.send("")){finishWithText("Done");return;}
        main.postDelayed(()->{
            if(session!=voiceSessionEpoch||ack!=finishAckEpoch)return;
            if(!running||completed||!stopRequested||webSocket!=ws)return;
            finishWithText("Done");
        },FINISH_TIMEOUT_MS);
    }
'''
s = rep(s, old_finish, new_finish, 'session-scoped finish ACK fallback')

old_complete = r'''    private void completeSession(String m){
        boolean shouldSend=sendAfterVoiceStop;
        sendAfterVoiceStop=false;
        running=false;stopRequested=true;awaitingCredential=false;stopAudioRecord();clearPending();
        main.post(()->{
            updateMicUi();setStatus(m);
            // publish(true) is queued before completeSession(), so this follow-up
            // executes only after the final transcript has been committed.
            if(shouldSend)main.postDelayed(this::sendFocusedField,40L);
        });
    }
'''
new_complete = r'''    private void completeSession(String m){
        boolean shouldSend=sendAfterVoiceStop;
        sendAfterVoiceStop=false;
        final int endedSession=++voiceSessionEpoch;
        finishAckEpoch++;
        liveSyncRecoveryEpoch++;
        liveSyncRetryScheduled=false;
        running=false;stopRequested=true;awaitingCredential=false;stopAudioRecord();clearPending();
        WebSocket ws=webSocket;webSocket=null;
        if(ws!=null)try{ws.close(1000,"complete");}catch(Exception ignored){try{ws.cancel();}catch(Exception ignoredToo){}}
        main.post(()->{
            if(voiceSessionEpoch!=endedSession||running)return;
            updateMicUi();setStatus(m);
            // publish(true) is queued before completeSession(), so this follow-up
            // executes only after the final transcript has been committed.
            if(shouldSend)main.postDelayed(()->{
                if(voiceSessionEpoch==endedSession&&!running)sendFocusedField();
            },40L);
        });
    }
'''
s = rep(s, old_complete, new_complete, 'session-scoped completion cleanup')

if 'versionCode 44' not in g or "versionName '1.34'" not in g:
    raise SystemExit('v1.35 patch: expected v1.34 version markers missing')
g=g.replace('versionCode 44','versionCode 45',1)
g=g.replace("versionName '1.34'","versionName '1.35'",1)

text=s+'\n'+g
required=[
    'private boolean liveSyncRetryScheduled;',
    'private long lastUnattributedOffTailSelectionUptime;',
    'private volatile int voiceSessionEpoch;',
    'private volatile int finishAckEpoch;',
    'private boolean inSelectionHoldoff(){',
    'touchGeneration>voiceStartTouchGeneration',
    'lastUnattributedOffTailSelectionUptime=android.os.SystemClock.uptimeMillis();',
    'private void armLiveSyncRetry(){',
    'Recording — live text delayed',
    'if(!running||hasRecentEditorUserInteraction()||inSelectionHoldoff())return false;',
    'if(!running||hasRecentEditorUserInteraction()||inSelectionHoldoff()||!voiceBoundaryCaptured)return false;',
    'final int session=voiceSessionEpoch;',
    'ack=++finishAckEpoch;',
    'if(session!=voiceSessionEpoch||ack!=finishAckEpoch)return;',
    'if(voiceSessionEpoch!=endedSession||running)return;',
    'ws.close(1000,"complete")',
    'versionCode 45',
    "versionName '1.35'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.35 patch: required invariant missing: {needle}')

for forbidden in [
    'stopVoiceForManualInput();\n            setStatus("Voice stopped — live text sync lost");',
    'long correlation=lastEditorToolInteractionUptime-touchEventTime;',
    'scheduleInternalSelectionReanchor();\n            return;',
    'Done (finish ACK timeout)',
    'MAX_CAPTURE_MS',
    'boundConnection.setComposingText(partial,1);',
    'versionCode 44',
    "versionName '1.34'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.35 patch: forbidden coupled behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.35 decoupled capture/projection/intent state patch')
