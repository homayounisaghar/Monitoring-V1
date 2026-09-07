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
        raise SystemExit(f'v1.31 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


# v1.30 device evidence proved that persistent off-tail selection is editor state,
# not proof of user intent. v1.31 requires an independently observed user touch/
# editor click before selection is allowed to stop speech. Otherwise it restores
# the last cursor position owned by the IME and keeps speech transport alive.
s = rep(s,
'''    private int selectionConfirmationEpoch;
    private boolean selectionConfirmationPending;
''',
'''    private int selectionConfirmationEpoch;
    private boolean selectionConfirmationPending;
    private long voiceStartedUptime;
    private long voiceStartTouchGeneration;
    private long lastEditorToolInteractionUptime;
    private int lastProgrammaticSelectionStart=-1;
    private int lastProgrammaticSelectionEnd=-1;
    private int internalSelectionReanchorEpoch;
''', 'user interaction attribution state')

s = rep(s,
'''                lastProgrammaticSelectionKey=key;
                hasLastProgrammaticSelection=true;
                while(expectedSelectionUpdates.size()>=10)expectedSelectionUpdates.removeFirst();
''',
'''                lastProgrammaticSelectionKey=key;
                lastProgrammaticSelectionStart=start;
                lastProgrammaticSelectionEnd=end;
                hasLastProgrammaticSelection=true;
                while(expectedSelectionUpdates.size()>=10)expectedSelectionUpdates.removeFirst();
''', 'remember absolute owned cursor')

s = rep(s,
'''    private void scheduleExternalSelectionConfirmation(int start,int end){
''',
'''    private boolean hasRecentEditorUserInteraction(){
        long now=android.os.SystemClock.uptimeMillis();
        if(!running||voiceStartedUptime<=0L||now-voiceStartedUptime<300L)return false;
        if(lastEditorToolInteractionUptime>voiceStartedUptime+200L
                &&now>=lastEditorToolInteractionUptime
                &&now-lastEditorToolInteractionUptime<=1200L)return true;
        long touchGeneration=SendAccessibilityService.userTouchGeneration();
        long touchUptime=SendAccessibilityService.latestUserTouchUptime();
        return touchGeneration>voiceStartTouchGeneration
                &&touchUptime>voiceStartedUptime+200L
                &&now>=touchUptime
                &&now-touchUptime<=1200L;
    }

    private void scheduleInternalSelectionReanchor(){
        final int epoch=++internalSelectionReanchorEpoch;
        main.postDelayed(()->{
            if(epoch!=internalSelectionReanchorEpoch||!running)return;
            if(hasRecentEditorUserInteraction())return;
            if(!hasLastProgrammaticSelection||lastProgrammaticSelectionStart<0||lastProgrammaticSelectionEnd<0)return;
            InputConnection ic=boundConnection;
            if(ic==null||getCurrentInputConnection()!=ic)return;
            programmaticSelectionEditDepth++;
            try{
                ic.setSelection(lastProgrammaticSelectionStart,lastProgrammaticSelectionEnd);
                rememberProgrammaticSelection();
            }catch(Exception ignored){
            }finally{
                programmaticSelectionEditDepth=Math.max(0,programmaticSelectionEditDepth-1);
            }
        },90L);
    }

    private void scheduleExternalSelectionConfirmation(int start,int end){
''', 'interaction attribution helpers')

s = rep(s,
'''            if(!selectionCallbackMatchesEditorNow(start,end)){
                selectionConfirmationPending=false;
                return;
            }
            if(currentSelectionAtOwnedVoiceTail(start,end)){
                selectionConfirmationPending=false;
                return;
            }
            selectionConfirmationPending=false;
            stopVoiceForManualInput();
            setStatus("Voice stopped — selection confirmed off voice tail");
''',
'''            if(!selectionCallbackMatchesEditorNow(start,end)){
                selectionConfirmationPending=false;
                return;
            }
            if(currentSelectionAtOwnedVoiceTail(start,end)){
                selectionConfirmationPending=false;
                return;
            }
            if(!hasRecentEditorUserInteraction()){
                selectionConfirmationPending=false;
                scheduleInternalSelectionReanchor();
                return;
            }
            selectionConfirmationPending=false;
            stopVoiceForManualInput();
            setStatus("Voice stopped — selection after user interaction");
''', 'require user interaction before confirmed selection stop')

s = rep(s,
'''        if(withinComposing)return;
        // Do not attribute causality from one callback. Browser/contenteditable
        // editors can transiently move selection while applying the IME's own
        // edit. A real user move persists away from the owned voice tail; an
        // internal move resolves back to the voice tail and is ignored.
        if(currentSelectionAtOwnedVoiceTail(newSelStart,newSelEnd))return;
        scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);
''',
'''        if(withinComposing)return;
        if(currentSelectionAtOwnedVoiceTail(newSelStart,newSelEnd))return;
        if(!hasRecentEditorUserInteraction()){
            scheduleInternalSelectionReanchor();
            return;
        }
        scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);
''', 'selection callback user attribution gate')

# Insert by stable method-prefix rather than a full signature: historical patches
# use different whitespace/parameter formatting for onUpdateSelection.
selection_marker = '    @Override public void onUpdateSelection('
if selection_marker not in s:
    raise SystemExit('v1.31 patch: missing onUpdateSelection method prefix')
insert_at = s.index(selection_marker)
s = s[:insert_at] + '''    @Override public void onUpdateEditorToolType(int toolType){
        lastEditorToolInteractionUptime=android.os.SystemClock.uptimeMillis();
    }

''' + s[insert_at:]

s = rep(s,
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; livePartialTail=""; programmaticSelectionEditDepth=0; hasLastProgrammaticSelection=false; selectionConfirmationEpoch++; selectionConfirmationPending=false; sendAfterVoiceStop=false; updateMicUi();
''',
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; livePartialTail=""; programmaticSelectionEditDepth=0; hasLastProgrammaticSelection=false; lastProgrammaticSelectionStart=-1; lastProgrammaticSelectionEnd=-1; selectionConfirmationEpoch++; selectionConfirmationPending=false; internalSelectionReanchorEpoch++; voiceStartedUptime=android.os.SystemClock.uptimeMillis(); voiceStartTouchGeneration=SendAccessibilityService.userTouchGeneration(); lastEditorToolInteractionUptime=0L; sendAfterVoiceStop=false; updateMicUi();
''', 'voice start interaction snapshot')

h = rep(h,
'''    private static volatile SendAccessibilityService instance;
    private static volatile String lastResult = "";
''',
'''    private static volatile SendAccessibilityService instance;
    private static volatile String lastResult = "";
    private static volatile long latestUserTouchUptime;
    private static volatile long userTouchGeneration;
''', 'accessibility touch state')

h = rep(h,
'''    public static String getLastResult() {
        return lastResult;
    }
''',
'''    public static String getLastResult() {
        return lastResult;
    }

    public static long latestUserTouchUptime() {
        return latestUserTouchUptime;
    }

    public static long userTouchGeneration() {
        return userTouchGeneration;
    }
''', 'accessibility touch accessors')

h = rep(h,
'''    @Override public void onAccessibilityEvent(AccessibilityEvent event) {
        // Deliberately idle: no continuous screen processing.
    }
''',
'''    @Override public void onAccessibilityEvent(AccessibilityEvent event) {
        if(event==null)return;
        int type=event.getEventType();
        if(type==AccessibilityEvent.TYPE_TOUCH_INTERACTION_START){
            latestUserTouchUptime=android.os.SystemClock.uptimeMillis();
            userTouchGeneration++;
        }else if(type==AccessibilityEvent.TYPE_TOUCH_INTERACTION_END){
            latestUserTouchUptime=android.os.SystemClock.uptimeMillis();
        }
        // All other accessibility events remain ignored; no continuous node/text
        // inspection is introduced by this change.
    }
''', 'system touch interaction attribution')

a = rep(a,
'''    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged|typeViewFocused"
''',
'''    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged|typeViewFocused|typeTouchInteractionStart|typeTouchInteractionEnd"
''', 'touch interaction event subscription')

if 'versionCode 40' not in g or "versionName '1.30'" not in g:
    raise SystemExit('v1.31 patch: expected v1.30 version markers missing')
g = g.replace('versionCode 40', 'versionCode 41', 1)
g = g.replace("versionName '1.30'", "versionName '1.31'", 1)

text = s + '\n' + h + '\n' + a + '\n' + g
required = [
    'private long voiceStartedUptime;',
    'private long voiceStartTouchGeneration;',
    'private int lastProgrammaticSelectionStart=-1;',
    'private int internalSelectionReanchorEpoch;',
    'private boolean hasRecentEditorUserInteraction(){',
    'private void scheduleInternalSelectionReanchor(){',
    'ic.setSelection(lastProgrammaticSelectionStart,lastProgrammaticSelectionEnd);',
    '@Override public void onUpdateEditorToolType(int toolType){',
    'Voice stopped — selection after user interaction',
    'public static long latestUserTouchUptime()',
    'public static long userTouchGeneration()',
    'AccessibilityEvent.TYPE_TOUCH_INTERACTION_START',
    'typeTouchInteractionStart|typeTouchInteractionEnd',
    'versionCode 41',
    "versionName '1.31'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.31 patch: required invariant missing: {needle}')

for forbidden in [
    'setStatus("Voice stopped — selection confirmed off voice tail");',
    'MAX_CAPTURE_MS',
    'boundConnection.setComposingText(partial,1);',
    'versionCode 40',
    "versionName '1.30'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.31 patch: forbidden old behavior remains: {forbidden}')

service.write_text(s)
helper.write_text(h)
accessibility_xml.write_text(a)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.31 user-interaction attribution patch')
