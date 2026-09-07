from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
helper = Path('app/src/main/java/com/najme/perplexityprobe/SendAccessibilityService.java')
accessibility_xml = Path('app/src/main/res/xml/send_accessibility_service.xml')
gradle_file = Path('app/build.gradle')

s = service.read_text()
h = helper.read_text()
a = accessibility_xml.read_text()
g = gradle_file.read_text()


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.31 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


# v1.30 proved that a browser/contenteditable editor can move its selection
# persistently away from the IME-owned voice tail without any user touch. A
# selection position therefore describes state, not causality. v1.31 changes
# attribution: selection alone can never stop speech. It must be accompanied by
# independently observed user interaction with the editor/screen. Internal
# off-tail churn is re-anchored to the last IME-owned cursor instead of stopping
# AudioRecord/WebSocket or permanently stalling live publication.

s = replace_once(
    s,
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
''',
    'user-interaction attribution state',
)

s = replace_once(
    s,
'''                lastProgrammaticSelectionKey=key;
                hasLastProgrammaticSelection=true;
                while(expectedSelectionUpdates.size()>=10)expectedSelectionUpdates.removeFirst();
''',
'''                lastProgrammaticSelectionKey=key;
                lastProgrammaticSelectionStart=start;
                lastProgrammaticSelectionEnd=end;
                hasLastProgrammaticSelection=true;
                while(expectedSelectionUpdates.size()>=10)expectedSelectionUpdates.removeFirst();
''',
    'remember absolute owned cursor coordinates',
)

s = replace_once(
    s,
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
''',
    'interaction attribution and internal re-anchor helpers',
)

s = replace_once(
    s,
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
            // Selection state is not proof of user intent. Only an independently
            // observed touch/editor click may authorize the manual-stop path.
            if(!hasRecentEditorUserInteraction()){
                selectionConfirmationPending=false;
                scheduleInternalSelectionReanchor();
                return;
            }
            selectionConfirmationPending=false;
            stopVoiceForManualInput();
            setStatus("Voice stopped — selection after user interaction");
''',
    'require independently observed user interaction before selection stop',
)

s = replace_once(
    s,
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
        // v1.30 device evidence proved that persistent off-tail selection can be
        // editor-generated. Do not even start the stop-confirmation gate unless
        // a separate user-interaction signal exists. Otherwise restore the last
        // IME-owned cursor and keep speech/live publication alive.
        if(!hasRecentEditorUserInteraction()){
            scheduleInternalSelectionReanchor();
            return;
        }
        scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);
''',
    'selection callback must have user-interaction evidence',
)

s = replace_once(
    s,
'''    @Override public void onUpdateSelection(int oldSelStart,int oldSelEnd,int newSelStart,int newSelEnd,int candidatesStart,int candidatesEnd){
''',
'''    @Override public void onUpdateEditorToolType(int toolType){
        lastEditorToolInteractionUptime=android.os.SystemClock.uptimeMillis();
    }

    @Override public void onUpdateSelection(int oldSelStart,int oldSelEnd,int newSelStart,int newSelEnd,int candidatesStart,int candidatesEnd){
''',
    'direct editor tap/click attribution callback',
)

s = replace_once(
    s,
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; livePartialTail=""; programmaticSelectionEditDepth=0; hasLastProgrammaticSelection=false; selectionConfirmationEpoch++; selectionConfirmationPending=false; sendAfterVoiceStop=false; updateMicUi();
''',
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; livePartialTail=""; programmaticSelectionEditDepth=0; hasLastProgrammaticSelection=false; lastProgrammaticSelectionStart=-1; lastProgrammaticSelectionEnd=-1; selectionConfirmationEpoch++; selectionConfirmationPending=false; internalSelectionReanchorEpoch++; voiceStartedUptime=android.os.SystemClock.uptimeMillis(); voiceStartTouchGeneration=SendAccessibilityService.userTouchGeneration(); lastEditorToolInteractionUptime=0L; sendAfterVoiceStop=false; updateMicUi();
''',
    'snapshot touch generation at voice start',
)

h = replace_once(
    h,
'''    private static volatile SendAccessibilityService instance;
    private static volatile String lastResult = "";
''',
'''    private static volatile SendAccessibilityService instance;
    private static volatile String lastResult = "";
    private static volatile long latestUserTouchUptime;
    private static volatile long userTouchGeneration;
''',
    'Accessibility user-touch state',
)

h = replace_once(
    h,
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
''',
    'Accessibility touch accessors',
)

h = replace_once(
    h,
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
        // Other accessibility events remain ignored. This service still does no
        // continuous node/text processing outside an explicit Send request.
    }
''',
    'system user-touch event attribution',
)

a = replace_once(
    a,
'''    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged|typeViewFocused"
''',
'''    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged|typeViewFocused|typeTouchInteractionStart|typeTouchInteractionEnd"
''',
    'subscribe to system touch-interaction events',
)

if 'versionCode 40' not in g or "versionName '1.30'" not in g:
    raise SystemExit('v1.31 patch: expected v1.30 version markers missing')
g = g.replace('versionCode 40', 'versionCode 41', 1)
g = g.replace("versionName '1.30'", "versionName '1.31'", 1)

required = [
    'private long voiceStartedUptime;',
    'private long voiceStartTouchGeneration;',
    'private int lastProgrammaticSelectionStart=-1;',
    'private int internalSelectionReanchorEpoch;',
    'private boolean hasRecentEditorUserInteraction(){',
    'private void scheduleInternalSelectionReanchor(){',
    'ic.setSelection(lastProgrammaticSelectionStart,lastProgrammaticSelectionEnd);',
    '@Override public void onUpdateEditorToolType(int toolType){',
    'if(!hasRecentEditorUserInteraction()){',
    'Voice stopped — selection after user interaction',
    'public static long latestUserTouchUptime()',
    'public static long userTouchGeneration()',
    'AccessibilityEvent.TYPE_TOUCH_INTERACTION_START',
    'typeTouchInteractionStart|typeTouchInteractionEnd',
    'versionCode 41',
    "versionName '1.31'",
]
text = s + '\n' + h + '\n' + a + '\n' + g
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
