from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
helper = Path('app/src/main/java/com/najme/perplexityprobe/SendAccessibilityService.java')
accessibility_xml = Path('app/src/main/res/xml/send_accessibility_service.xml')
gradle_file = Path('app/build.gradle')

s = service.read_text()
h = helper.read_text()
a = accessibility_xml.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.39 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


def replace_region(text, start_marker, end_marker, replacement, label):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f'v1.39 patch: missing start marker: {label}')
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f'v1.39 patch: missing end marker: {label}')
    return text[:start] + replacement + text[end:]


# Real-device v1.38 evidence disproved the remaining touch-correlation premise:
# while a voice run is active, the user can move the editor caret and Android
# reports the new selection, yet the voice projection still remains anchored to
# the pre-recording location. The IME already has stronger self-edit attribution:
# programmaticSelectionEditDepth plus the exact voiceExpectedSelection pair.
# v1.39 therefore treats any other valid same-editor selection as the user's new
# projection target directly. No touch event, delayed confirmation or re-anchor
# loop is required, and selection still never stops the voice transport.

selection_start = '    @Override public void onUpdateSelection('
selection_end = '    private long selectionKey('
selection_method = r'''    @Override public void onUpdateSelection(int oldSelStart, int oldSelEnd, int newSelStart, int newSelEnd, int candidatesStart, int candidatesEnd) {
        super.onUpdateSelection(oldSelStart, oldSelEnd, newSelStart, newSelEnd, candidatesStart, candidatesEnd);
        if(!running||newSelStart<0||newSelEnd<newSelStart)return;
        if(programmaticSelectionEditDepth>0)return;
        if(newSelStart==voiceExpectedSelectionStart&&newSelEnd==voiceExpectedSelectionEnd)return;

        // A selection that is not the IME's own expected post-publication caret is
        // authoritative editor state. Rebase the current unstable voice tail to it
        // immediately; do not wait for Accessibility touch delivery.
        voiceCaretRebasePending=true;
        voiceCaretRebaseStart=newSelStart;
        voiceCaretRebaseEnd=newSelEnd;
        voiceCaretRebaseSelectionUptime=android.os.SystemClock.uptimeMillis();
        voiceCaretRebaseTouchGeneration=1L;
        final long runId=activeVoiceRunId;
        main.post(()->{if(voiceRunActive(runId))publish(false,runId);});
    }

'''
s = replace_region(s, selection_start, selection_end, selection_method,
                   'direct active-session selection rebase')

# Remove v1.38's touch-correlation helper entirely. The rebase itself remains
# range-owned and fail-closed, but now verifies the known unstable partial tail
# directly at the absolute voice-owned range rather than requiring a touch-gated
# candidate. This also avoids making the user's new cursor the only window from
# which the old tail must be rediscovered.
correlation_start = '    private void clearVoiceCaretRebaseCandidate(){'
correlation_end = '    private void noteVoicePublicationPaused(long runId){'
rebase_helpers = r'''    private void clearVoiceCaretRebaseCandidate(){
        voiceCaretRebasePending=false;
        voiceCaretRebaseStart=-1;voiceCaretRebaseEnd=-1;
        voiceCaretRebaseTouchGeneration=0L;voiceCaretRebaseSelectionUptime=0L;
    }

    private boolean rebaseVoiceProjectionIfPending(InputConnection ic,VoiceEditorWindow window,long runId){
        if(!voiceCaretRebasePending)return true;
        final int rawTargetStart=voiceCaretRebaseStart;
        final int rawTargetEnd=voiceCaretRebaseEnd;
        clearVoiceCaretRebaseCandidate();

        if(!voiceRunActive(runId)||ic==null)return false;
        if(rawTargetStart<0||rawTargetEnd<rawTargetStart)return false;
        if(voiceOwnedStart<0||voiceOwnedEnd<voiceOwnedStart)return false;

        String oldTail=livePartialTail==null?"":livePartialTail;
        if(!oldTail.isEmpty()&&!voicePublishedText.endsWith(oldTail))return false;
        int tailStart=voiceOwnedEnd-oldTail.length();
        if(tailStart<voiceOwnedStart)return false;

        int targetStart=adjustSelectionAfterReplace(rawTargetStart,tailStart,voiceOwnedEnd,0);
        int targetEnd=adjustSelectionAfterReplace(rawTargetEnd,tailStart,voiceOwnedEnd,0);
        if(targetStart<0||targetEnd<targetStart)return false;

        boolean batch=false;boolean ok=false;
        programmaticSelectionEditDepth++;
        try{
            batch=ic.beginBatchEdit();
            if(!oldTail.isEmpty()){
                if(!ic.setSelection(tailStart,voiceOwnedEnd))return false;
                CharSequence selectedCs=ic.getSelectedText(0);
                String selected=selectedCs==null?"":selectedCs.toString();
                if(!exactOwnedText(selected,oldTail)){
                    try{ic.setSelection(rawTargetStart,rawTargetEnd);}catch(Exception ignored){}
                    return false;
                }
                if(!ic.commitText("",1))return false;
            }
            if(!ic.setSelection(targetStart,targetEnd))return false;
            if(!oldTail.isEmpty()&&!ic.commitText(oldTail,1))return false;
            int newOwnedEnd=targetStart+oldTail.length();
            if(!ic.setSelection(newOwnedEnd,newOwnedEnd))return false;

            // Everything already final stays frozen at the old segment. Only the
            // unstable live tail and all future transcript deltas belong here.
            voiceProjectionFinalBaseChars=Math.max(0,committedFinalChars);
            voicePublishedText=oldTail;
            voiceOwnedStart=targetStart;voiceOwnedEnd=newOwnedEnd;
            voiceSelectionFollowsOwnedRange=true;
            voiceExpectedSelectionStart=newOwnedEnd;voiceExpectedSelectionEnd=newOwnedEnd;
            voicePublicationPaused=false;
            refreshVoiceBoundariesForOwnedRegion(ic);
            ok=true;
        }catch(Exception ignored){
        }finally{
            if(batch)try{ic.endBatchEdit();}catch(Exception ignored){}
            if(ok)rememberProgrammaticSelection();
            programmaticSelectionEditDepth=Math.max(0,programmaticSelectionEditDepth-1);
        }
        return ok;
    }

'''
s = replace_region(s, correlation_start, correlation_end, rebase_helpers,
                   'remove touch correlation and keep ownership-safe direct rebase')

publisher_old = '''            VoiceEditorWindow window=currentVoiceEditorWindow(ic);\n            if(window==null){noteVoicePublicationPaused(runId);return;}\n            if(voiceCaretRebasePending&&voiceCaretRebaseTouchGeneration<=0L)\n                confirmVoiceCaretRebaseCandidate(ic,window,runId);\n            if(voiceCaretRebasePending&&voiceCaretRebaseTouchGeneration>0L){\n                if(!rebaseVoiceProjectionIfPending(ic,window,runId)){\n                    // Rebase is opportunistic but fail-closed: never mutate an\n                    // unproved region and never stop healthy speech because of it.\n                    voiceSelectionFollowsOwnedRange=false;\n                }\n                window=currentVoiceEditorWindow(ic);\n                if(window==null){noteVoicePublicationPaused(runId);return;}\n            }\n'''
publisher_new = '''            VoiceEditorWindow window=currentVoiceEditorWindow(ic);\n            if(window==null){noteVoicePublicationPaused(runId);return;}\n            if(voiceCaretRebasePending){\n                if(!rebaseVoiceProjectionIfPending(ic,window,runId)){\n                    // Rebase is opportunistic but fail-closed: never mutate an\n                    // unproved region and never stop healthy speech because of it.\n                    voiceSelectionFollowsOwnedRange=false;\n                }\n                window=currentVoiceEditorWindow(ic);\n                if(window==null){noteVoicePublicationPaused(runId);return;}\n            }\n'''
s = rep(s, publisher_old, publisher_new,
        'publish directly consumes selection rebase without touch confirmation')

# Host Send must terminate recording even when the IME remains visible (Telegram
# is the concrete device case). Accessibility already belongs to this APK and can
# identify semantically labeled Send/Submit clicks. Keep a live IME instance only
# in-process; no persisted state or exported broadcast is introduced.
s = rep(s,
'''public class PersianKeyboardService extends InputMethodService {\n''',
'''public class PersianKeyboardService extends InputMethodService {\n    private static volatile PersianKeyboardService activeInstance;\n''',
    'active IME instance for host Send callback')

s = rep(s,
'''    @Override public void onCreate() {\n        super.onCreate();\n''',
'''    @Override public void onCreate() {\n        super.onCreate();\n        activeInstance=this;\n''',
    'register active IME instance')

host_send_methods = r'''    public static void notifyHostSendFromAccessibility(String sourcePackage,long eventTime){
        PersianKeyboardService service=activeInstance;
        if(service==null)return;
        service.main.post(()->service.handleHostSendFromAccessibility(sourcePackage,eventTime));
    }

    private void handleHostSendFromAccessibility(String sourcePackage,long eventTime){
        if(!running)return;
        String currentPackage=editorInfo==null?null:editorInfo.packageName;
        if(sourcePackage==null||currentPackage==null||!currentPackage.equals(sourcePackage))return;
        // The host has already accepted Send. Finalizing speech into the now-cleared
        // composer would risk leaking the tail into a new message, so invalidate the
        // voice run immediately instead of waiting for IME visibility lifecycle.
        stopVoiceForManualInput();
        setCollapsed(false);
        updateMicUi();
        setStatus(readyText());
    }

'''
on_create_marker = '    @Override public void onCreate() {'
if on_create_marker not in s:
    raise SystemExit('v1.39 patch: onCreate marker missing')
s = s.replace(on_create_marker, host_send_methods + on_create_marker, 1)

s = rep(s,
'''    @Override public void onDestroy(){''',
'''    @Override public void onDestroy(){if(activeInstance==this)activeInstance=null;''',
    'clear active IME instance on destroy')

# Convert the accessibility helper from touch-only observation to touch + exact
# host Send observation. Only TYPE_VIEW_CLICKED is inspected, and only nodes whose
# own/nearest clickable semantic label or resource id scores as Send/Submit cause
# a voice stop. Other clicks remain ignored.
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
                   access_event_method, 'observe semantic host Send clicks')

if 'typeWindowStateChanged|typeWindowContentChanged|typeViewFocused|typeTouchInteractionStart' not in a:
    raise SystemExit('v1.39 patch: accessibility event subscription marker missing')
a = a.replace(
    'typeWindowStateChanged|typeWindowContentChanged|typeViewFocused|typeTouchInteractionStart',
    'typeWindowStateChanged|typeWindowContentChanged|typeViewFocused|typeTouchInteractionStart|typeViewClicked',
    1)

if 'versionCode 48' not in g or "versionName '1.38'" not in g:
    raise SystemExit('v1.39 patch: v1.38 Gradle version markers missing')
g = g.replace('versionCode 48', 'versionCode 49', 1)
g = g.replace("versionName '1.38'", "versionName '1.39'", 1)

text = s + '\n' + h + '\n' + a + '\n' + g
required = [
    'private static volatile PersianKeyboardService activeInstance;',
    'public static void notifyHostSendFromAccessibility(',
    'private void handleHostSendFromAccessibility(',
    'stopVoiceForManualInput();',
    'if(programmaticSelectionEditDepth>0)return;',
    'voiceCaretRebaseStart=newSelStart;',
    'voiceCaretRebaseTouchGeneration=1L;',
    'if(voiceCaretRebasePending){',
    'int tailStart=voiceOwnedEnd-oldTail.length();',
    'if(!exactOwnedText(selected,oldTail))',
    'voiceProjectionFinalBaseChars=Math.max(0,committedFinalChars);',
    'AccessibilityEvent.TYPE_VIEW_CLICKED',
    'semanticScore(source)',
    'PersianKeyboardService.notifyHostSendFromAccessibility(sourcePackage,event.getEventTime());',
    'typeTouchInteractionStart|typeViewClicked',
    'private void stopVoiceForImeHidden(){',
    'Button zwnj=actionKey("−", v -> commitText("\\u200C"));',
    'versionCode 49',
    "versionName '1.39'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.39 patch: required invariant missing: {needle}')

for forbidden in [
    'confirmVoiceCaretRebaseCandidate(',
    'long correlation=Math.abs(candidateTime-touchEventTime);',
    'if(voiceCaretRebaseTouchGeneration<=0L)return true;',
    'scheduleInternalSelectionReanchor();',
    'scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);',
    'Voice stopped — live text sync lost',
    'versionCode 48',
    "versionName '1.38'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.39 patch: forbidden v1.38/legacy behavior remains: {forbidden}')

service.write_text(s)
helper.write_text(h)
accessibility_xml.write_text(a)
gradle_file.write_text(g)
print('Applied v1.39 direct-selection caret rebase + host Send stop patch')
