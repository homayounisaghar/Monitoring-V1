from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
helper = Path('app/src/main/java/com/najme/perplexityprobe/SendAccessibilityService.java')
gradle_file = Path('app/build.gradle')

s = service.read_text()
h = helper.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.40 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


def replace_region(text, start_marker, end_marker, replacement, label):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f'v1.40 patch: missing start marker: {label}')
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f'v1.40 patch: missing end marker: {label}')
    return text[:start] + replacement + text[end:]


# v1.39 real-device evidence shows two concrete design mistakes:
# 1) the caret path still mutated the editor immediately and explicitly selected
#    the end of the voice-owned range, so a user tap could never remain the owner
#    of the caret;
# 2) host-Send stop depended on Accessibility exposing a semantic Send node.
#
# v1.40 changes the contract. A user caret move NEVER moves existing text and
# NEVER calls setSelection. Instead it freezes the already-visible old speech
# segment in place, creates a fresh empty projection segment at the actual current
# editor selection, and rotates only the speech transport so future audio belongs
# to the new segment. The microphone/recording session itself stays active.
#
# For host Send, the IME monitors its own ExtractedText. Once a composer that was
# non-empty becomes truly empty while the same voice run is active, the run is
# hard-stopped. This is the safety event we actually care about after Send and it
# does not require the host button to expose an accessibility label.

s = rep(s,
'''    private long voiceLastHandledTouchGeneration;\n''',
'''    private long voiceLastHandledTouchGeneration;\n    private int voiceExtractMonitorCounter;\n    private int voiceExtractMonitorToken;\n    private boolean voiceExternalClearStopArmed;\n''',
    'native editor text-monitor state')

# Request editor text monitoring as part of each new voice run. This uses the
# standard InputConnection monitor contract and does not poll or re-anchor.
s = rep(s,
'''        captureVoiceInsertionBoundary();\n''',
'''        captureVoiceInsertionBoundary();\n        armVoiceExtractedTextMonitor(ic);\n''',
    'arm extracted-text monitor at voice start')

# Replace v1.39 selection handling. The callback itself is only a hint; a single
# posted verification reads the CURRENT editor selection after callbacks settle.
# If it is still off the IME-expected cursor, that current selection is the user's
# projection target. No editor mutation occurs in this path.
selection_start = '    @Override public void onUpdateSelection('
selection_end = '    private long selectionKey('
selection_methods = r'''    @Override public void onUpdateExtractedText(int token, android.view.inputmethod.ExtractedText text) {
        super.onUpdateExtractedText(token,text);
        if(!running||token!=voiceExtractMonitorToken||text==null)return;
        if(programmaticSelectionEditDepth>0)return;
        if(text.text!=null&&text.text.length()>0){
            voiceExternalClearStopArmed=true;
            return;
        }
        stopVoiceIfExternalComposerCleared(null);
    }

    @Override public void onUpdateSelection(int oldSelStart, int oldSelEnd, int newSelStart, int newSelEnd, int candidatesStart, int candidatesEnd) {
        super.onUpdateSelection(oldSelStart, oldSelEnd, newSelStart, newSelEnd, candidatesStart, candidatesEnd);
        if(!running||newSelStart<0||newSelEnd<newSelStart)return;
        if(programmaticSelectionEditDepth>0)return;
        if(newSelStart==voiceExpectedSelectionStart&&newSelEnd==voiceExpectedSelectionEnd)return;

        final long runId=activeVoiceRunId;
        main.post(()->{
            if(!voiceRunActive(runId)||programmaticSelectionEditDepth>0)return;
            InputConnection ic=boundConnection;
            if(ic==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=ic)return;
            VoiceEditorWindow current=currentVoiceEditorWindow(ic);
            if(current==null)return;
            if(stopVoiceIfExternalComposerCleared(current))return;
            if(current.selectionStart==voiceExpectedSelectionStart&&current.selectionEnd==voiceExpectedSelectionEnd)return;
            beginVoiceCaretCutover(current.selectionStart,current.selectionEnd,runId,current);
        });
    }

'''
s = replace_region(s, selection_start, selection_end, selection_methods,
                   'user-owned caret cutover without snap-back')

# Replace the v1.39 physical-tail rebase helpers. The new cutover freezes the old
# visible segment in place. The current partial is promoted locally only to define
# a clean transcript boundary, then the speech socket is rotated while AudioRecord
# continues. Audio arriving after the cutover is buffered for the fresh socket.
helpers_start = '    private void clearVoiceCaretRebaseCandidate(){'
helpers_end = '    private void noteVoicePublicationPaused(long runId){'
helpers = r'''    private void clearVoiceCaretRebaseCandidate(){
        voiceCaretRebasePending=false;
        voiceCaretRebaseStart=-1;voiceCaretRebaseEnd=-1;
        voiceCaretRebaseTouchGeneration=0L;voiceCaretRebaseSelectionUptime=0L;
    }

    private void armVoiceExtractedTextMonitor(InputConnection ic){
        voiceExtractMonitorToken=++voiceExtractMonitorCounter;
        voiceExternalClearStopArmed=false;
        if(ic==null)return;
        try{
            android.view.inputmethod.ExtractedTextRequest req=new android.view.inputmethod.ExtractedTextRequest();
            req.token=voiceExtractMonitorToken;
            android.view.inputmethod.ExtractedText et=ic.getExtractedText(req,InputConnection.GET_EXTRACTED_TEXT_MONITOR);
            if(et!=null&&et.text!=null&&et.text.length()>0)voiceExternalClearStopArmed=true;
        }catch(Exception ignored){}
    }

    private boolean stopVoiceIfExternalComposerCleared(VoiceEditorWindow supplied){
        if(!running||!voiceExternalClearStopArmed)return false;
        InputConnection ic=boundConnection;
        if(ic==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=ic)return false;
        VoiceEditorWindow current=supplied==null?currentVoiceEditorWindow(ic):supplied;
        if(current==null)return false;
        if(!current.text.isEmpty()){
            voiceExternalClearStopArmed=true;
            return false;
        }
        stopVoiceForManualInput();
        clearVoiceCaretRebaseCandidate();
        voiceSelectionFollowsOwnedRange=false;
        voiceExpectedSelectionStart=-1;voiceExpectedSelectionEnd=-1;
        setCollapsed(false);
        updateMicUi();
        setStatus(readyText());
        return true;
    }

    private void beginVoiceCaretCutover(int targetStart,int targetEnd,long runId,VoiceEditorWindow window){
        if(!voiceRunActive(runId)||window==null)return;
        InputConnection ic=boundConnection;
        if(ic==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=ic)return;
        if(targetStart<window.absoluteStart||targetEnd<targetStart
                ||targetEnd>window.absoluteStart+window.text.length())return;

        int rs=targetStart-window.absoluteStart;
        int re=targetEnd-window.absoluteStart;
        if(rs<0||re<rs||re>window.text.length())return;
        String selected=window.text.substring(rs,re);

        // Freeze exactly what is already visible at the old voice segment. The
        // current partial becomes a local final boundary so it can never be moved
        // or rewritten at the newly selected caret.
        synchronized(textLock){
            if(partialTranscript!=null&&!partialTranscript.isEmpty()){
                finalTranscript.append(partialTranscript);
                partialTranscript="";
            }
            finalTokenIds.clear();
            voiceProjectionFinalBaseChars=finalTranscript.length();
            committedFinalChars=finalTranscript.length();
        }

        clearVoiceCaretRebaseCandidate();
        livePartialTail="";hasComposingTail=false;
        voicePublishedText=selected;
        voiceOwnedStart=targetStart;voiceOwnedEnd=targetEnd;
        voiceSelectionFollowsOwnedRange=true;
        voiceExpectedSelectionStart=targetStart;voiceExpectedSelectionEnd=targetEnd;
        voicePublicationPaused=false;
        if(!window.text.isEmpty())voiceExternalClearStopArmed=true;
        refreshVoiceBoundariesForOwnedRegion(ic);

        // Crucially: no commitText, deleteSurroundingText or setSelection here.
        // The user's caret stays exactly where the host editor put it.
        restartSpeechTransportForCaretCutover(runId);
    }

    private void restartSpeechTransportForCaretCutover(long runId){
        if(!voiceRunActive(runId)||completed||stopRequested)return;
        WebSocket old;
        synchronized(audioLock){
            if(!voiceRunActive(runId))return;
            speechRecovering=true;
            sonioxReady=false;
            finishSent=false;
            finishAckEpoch++;
            pendingAudio.clear();pendingBytes=0;
            old=webSocket;
            webSocket=null;
        }
        if(old!=null)try{old.cancel();}catch(Exception ignored){}
        awaitingCredential=true;
        credentialAttempt=0;
        retryAfterPageLoad=false;
        lastCredentialError="";
        activeCredentialRequestId=0L;
        final int epoch=++speechRecoveryEpoch;
        armCredentialWatchdog();
        requestCredential(runId);
        main.postDelayed(()->{
            if(voiceRunActive(runId)&&!completed&&!stopRequested&&speechRecovering
                    &&awaitingCredential&&epoch==speechRecoveryEpoch)requestCredential(runId);
        },2500L);
    }

'''
s = replace_region(s, helpers_start, helpers_end, helpers,
                   'freeze old segment and rotate speech transport at user caret')

# v1.39 publish performed the pending physical rebase before every transcript
# update. Remove that machinery entirely. The new segment has already been
# established without mutating the editor in beginVoiceCaretCutover().
publisher_old = '''            VoiceEditorWindow window=currentVoiceEditorWindow(ic);\n            if(window==null){noteVoicePublicationPaused(runId);return;}\n            if(voiceCaretRebasePending){\n                if(!rebaseVoiceProjectionIfPending(ic,window,runId)){\n                    // Rebase is opportunistic but fail-closed: never mutate an\n                    // unproved region and never stop healthy speech because of it.\n                    voiceSelectionFollowsOwnedRange=false;\n                }\n                window=currentVoiceEditorWindow(ic);\n                if(window==null){noteVoicePublicationPaused(runId);return;}\n            }\n'''
publisher_new = '''            VoiceEditorWindow window=currentVoiceEditorWindow(ic);\n            if(window==null){noteVoicePublicationPaused(runId);return;}\n'''
s = rep(s, publisher_old, publisher_new,
        'remove physical rebase from publisher')

# If the host cleared the composer (Telegram Send is the concrete case), a missing
# old voice-owned range is not a live-sync pause: it is session termination. Keep
# the old fail-closed pause for every non-empty/ambiguous editor state.
s = rep(s,
'''            int[] region=locatePublishedVoiceRegion(window);\n            if(region==null){noteVoicePublicationPaused(runId);return;}\n''',
'''            int[] region=locatePublishedVoiceRegion(window);\n            if(region==null){\n                if(stopVoiceIfExternalComposerCleared(window))return;\n                noteVoicePublicationPaused(runId);return;\n            }\n''',
    'empty composer is stop causality, not sync pause')

# Mark the composer non-empty directly from successful voice publication too, so
# external-clear detection does not depend on the host honoring ExtractedText
# monitoring callbacks.
s = rep(s,
'''            if(actual.equals(desired)){\n                voicePublishedText=desired;voiceOwnedStart=region[0];voiceOwnedEnd=region[0]+desired.length();\n''',
'''            if(actual.equals(desired)){\n                voicePublishedText=desired;voiceOwnedStart=region[0];voiceOwnedEnd=region[0]+desired.length();\n                voiceExternalClearStopArmed=!window.text.isEmpty();\n''',
    'remember non-empty composer on no-op voice publication')

s = rep(s,
'''                voicePublishedText=desired;voiceOwnedStart=region[0];voiceOwnedEnd=newOwnedEnd;\n                committedFinalChars=finalChars;livePartialTail=finish?"":partial;hasComposingTail=false;\n''',
'''                voicePublishedText=desired;voiceOwnedStart=region[0];voiceOwnedEnd=newOwnedEnd;\n                voiceExternalClearStopArmed=(window.text.length()-(region[3]-region[2])+desired.length())>0;\n                committedFinalChars=finalChars;livePartialTail=finish?"":partial;hasComposingTail=false;\n''',
    'remember non-empty composer after voice edit')

# Preserve the v1.39 semantic Send fast path, but add an independent content-change
# fallback. Accessibility never passes editor text; it only wakes the IME to check
# its own bound InputConnection after host content changes.
host_callbacks_start = '    public static void notifyHostSendFromAccessibility('
host_callbacks_end = '    @Override public void onCreate() {'
host_callbacks = r'''    public static void notifyHostSendFromAccessibility(String sourcePackage,long eventTime){
        PersianKeyboardService service=activeInstance;
        if(service==null)return;
        service.main.post(()->service.handleHostSendFromAccessibility(sourcePackage,eventTime));
    }

    public static void notifyHostContentChangedFromAccessibility(String sourcePackage,long eventTime){
        PersianKeyboardService service=activeInstance;
        if(service==null)return;
        service.main.post(()->service.handleHostContentChangedFromAccessibility(sourcePackage,eventTime));
    }

    private boolean hostPackageMatchesCurrentEditor(String sourcePackage){
        String currentPackage=editorInfo==null?null:editorInfo.packageName;
        return sourcePackage!=null&&currentPackage!=null&&currentPackage.equals(sourcePackage);
    }

    private void handleHostSendFromAccessibility(String sourcePackage,long eventTime){
        if(!running||!hostPackageMatchesCurrentEditor(sourcePackage))return;
        stopVoiceForManualInput();
        clearVoiceCaretRebaseCandidate();
        voiceSelectionFollowsOwnedRange=false;
        voiceExpectedSelectionStart=-1;voiceExpectedSelectionEnd=-1;
        setCollapsed(false);
        updateMicUi();
        setStatus(readyText());
    }

    private void handleHostContentChangedFromAccessibility(String sourcePackage,long eventTime){
        if(!running||!hostPackageMatchesCurrentEditor(sourcePackage))return;
        stopVoiceIfExternalComposerCleared(null);
    }

'''
s = replace_region(s, host_callbacks_start, host_callbacks_end, host_callbacks,
                   'host Send plus composer-clear accessibility fallback')

access_event_start = '    @Override public void onAccessibilityEvent(AccessibilityEvent event) {'
access_event_end = '    @Override public void onInterrupt() {}'
access_event_method = r'''    @Override public void onAccessibilityEvent(AccessibilityEvent event) {
        if(event==null)return;
        int type=event.getEventType();
        if(type==AccessibilityEvent.TYPE_TOUCH_INTERACTION_START){
            latestUserTouchEventTime=event.getEventTime();
            userTouchGeneration++;
            return;
        }
        if(type==AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED){
            String sourcePackage=value(event.getPackageName());
            if(!sourcePackage.isEmpty())
                PersianKeyboardService.notifyHostContentChangedFromAccessibility(sourcePackage,event.getEventTime());
            return;
        }
        if(type!=AccessibilityEvent.TYPE_VIEW_CLICKED)return;

        AccessibilityNodeInfo source=event.getSource();
        if(source==null)return;
        AccessibilityNodeInfo clickNode=clickableNode(source);
        int semantic=semanticScore(source);
        if(clickNode!=null&&clickNode!=source)semantic=Math.max(semantic,semanticScore(clickNode));
        if(semantic<=0)return;
        String sourcePackage=value(event.getPackageName());
        if(sourcePackage.isEmpty())return;
        PersianKeyboardService.notifyHostSendFromAccessibility(sourcePackage,event.getEventTime());
    }

'''
h = replace_region(h, access_event_start, access_event_end,
                   access_event_method, 'wake IME on host content clear as Send fallback')

if 'versionCode 49' not in g or "versionName '1.39'" not in g:
    raise SystemExit('v1.40 patch: v1.39 Gradle version markers missing')
g = g.replace('versionCode 49', 'versionCode 50', 1)
g = g.replace("versionName '1.39'", "versionName '1.40'", 1)

text = s + '\n' + h + '\n' + g
required = [
    'private int voiceExtractMonitorToken;',
    'private boolean voiceExternalClearStopArmed;',
    'InputConnection.GET_EXTRACTED_TEXT_MONITOR',
    '@Override public void onUpdateExtractedText(',
    'beginVoiceCaretCutover(current.selectionStart,current.selectionEnd,runId,current);',
    'private void beginVoiceCaretCutover(',
    'voiceProjectionFinalBaseChars=finalTranscript.length();',
    'restartSpeechTransportForCaretCutover(runId);',
    'pendingAudio.clear();pendingBytes=0;',
    'private boolean stopVoiceIfExternalComposerCleared(',
    'notifyHostContentChangedFromAccessibility(',
    'AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED',
    'if(stopVoiceIfExternalComposerCleared(window))return;',
    'private void stopVoiceForImeHidden(){',
    'Button zwnj=actionKey("−", v -> commitText("\\u200C"));',
    'versionCode 50',
    "versionName '1.40'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.40 patch: required invariant missing: {needle}')

for forbidden in [
    'rebaseVoiceProjectionIfPending(',
    'voiceCaretRebaseTouchGeneration=1L;',
    'int tailStart=voiceOwnedEnd-oldTail.length();',
    'if(!exactOwnedText(selected,oldTail))',
    'if(!oldTail.isEmpty()&&!ic.commitText(oldTail,1))return false;',
    'if(!ic.setSelection(newOwnedEnd,newOwnedEnd))return false;',
    'scheduleInternalSelectionReanchor();',
    'scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);',
    'Voice stopped — live text sync lost',
    'versionCode 49',
    "versionName '1.39'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.40 patch: forbidden snap-back/legacy behavior remains: {forbidden}')

service.write_text(s)
helper.write_text(h)
gradle_file.write_text(g)
print('Applied v1.40 true caret cutover + composer-clear voice-stop patch')
