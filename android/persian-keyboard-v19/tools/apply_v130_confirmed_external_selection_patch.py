from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.30 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# v1.29 still reproduced an involuntary "selection changed" stop. Callback
# ownership/ordering alone is therefore not a sufficient source-of-truth in
# browser/contenteditable editors. v1.30 changes the decision rule rather than
# adding another queue heuristic:
# - an apparent external selection change is only actionable if it persists;
# - while it is being confirmed, live publication is frozen so voice text cannot
#   be inserted at a possibly user-moved caret;
# - the persisted caret must still be the editor's current selection AND must no
#   longer sit immediately after the voice-owned text tail;
# - IME-owned transient cursor churn that returns/remains at the voice tail is
#   ignored without stopping AudioRecord/WebSocket.

replace_once(
'''    private int programmaticSelectionEditDepth;
    private long lastProgrammaticSelectionKey;
    private boolean hasLastProgrammaticSelection;
''',
'''    private int programmaticSelectionEditDepth;
    private long lastProgrammaticSelectionKey;
    private boolean hasLastProgrammaticSelection;
    private int selectionConfirmationEpoch;
    private boolean selectionConfirmationPending;
''',
    'selection confirmation state',
)

replace_once(
'''    private boolean matchesLastProgrammaticSelection(int start,int end){
        long key=selectionKey(start,end);
        synchronized(expectedSelectionUpdates){return hasLastProgrammaticSelection&&lastProgrammaticSelectionKey==key;}
    }
''',
'''    private boolean matchesLastProgrammaticSelection(int start,int end){
        long key=selectionKey(start,end);
        synchronized(expectedSelectionUpdates){return hasLastProgrammaticSelection&&lastProgrammaticSelectionKey==key;}
    }

    private String currentVoiceTailGuard(){
        String provisional=livePartialTail;
        if(provisional!=null&&!provisional.isEmpty())return provisional;
        synchronized(textLock){
            String committed=finalTranscript.toString();
            int n=Math.min(48,committed.length());
            return n<=0?"":committed.substring(committed.length()-n);
        }
    }

    private boolean currentSelectionAtOwnedVoiceTail(int start,int end){
        if(start<0||end<0||start!=end)return false;
        InputConnection ic=boundConnection;
        if(ic==null||getCurrentInputConnection()!=ic)return false;
        if(!selectionCallbackMatchesEditorNow(start,end))return false;
        String guard=currentVoiceTailGuard();
        if(guard.isEmpty())return false;
        try{
            CharSequence before=ic.getTextBeforeCursor(guard.length(),0);
            return before!=null&&before.toString().endsWith(guard);
        }catch(Exception ignored){
            return false;
        }
    }

    private void scheduleExternalSelectionConfirmation(int start,int end){
        final int epoch=++selectionConfirmationEpoch;
        selectionConfirmationPending=true;
        main.postDelayed(()->{
            if(epoch!=selectionConfirmationEpoch)return;
            if(!running){selectionConfirmationPending=false;return;}
            if(programmaticSelectionEditDepth>0){
                selectionConfirmationPending=false;
                scheduleExternalSelectionConfirmation(start,end);
                return;
            }
            if(!selectionCallbackMatchesEditorNow(start,end)){
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
        },140L);
    }
''',
    'voice-tail based selection confirmation helpers',
)

replace_once(
'''        if(withinComposing)return;
        stopVoiceForManualInput();
        setStatus("Voice stopped — selection changed");
''',
'''        if(withinComposing)return;
        // Do not attribute causality from one callback. Browser/contenteditable
        // editors can transiently move selection while applying the IME's own
        // edit. A real user move persists away from the owned voice tail; an
        // internal move resolves back to the voice tail and is ignored.
        if(currentSelectionAtOwnedVoiceTail(newSelStart,newSelEnd))return;
        scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);
''',
    'replace immediate selection stop with persistent off-tail confirmation',
)

replace_once(
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; livePartialTail=""; programmaticSelectionEditDepth=0; hasLastProgrammaticSelection=false; sendAfterVoiceStop=false; updateMicUi();
''',
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; livePartialTail=""; programmaticSelectionEditDepth=0; hasLastProgrammaticSelection=false; selectionConfirmationEpoch++; selectionConfirmationPending=false; sendAfterVoiceStop=false; updateMicUi();
''',
    'reset selection confirmation on voice start',
)

replace_once(
'''            if(boundConnection==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=boundConnection){if(running)abortForEditorChange("connection mismatch");return;}

            String newFinal;String partial;int targetFinalChars;
''',
'''            if(boundConnection==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=boundConnection){if(running)abortForEditorChange("connection mismatch");return;}
            // A suspicious caret move is being confirmed. Do not publish any
            // transcript into a potentially user-moved location during this
            // short gate. The next Soniox update retries after the gate clears.
            if(selectionConfirmationPending)return;

            String newFinal;String partial;int targetFinalChars;
''',
    'freeze live publication during selection confirmation',
)

if 'versionCode 39' not in g or "versionName '1.29'" not in g:
    raise SystemExit('v1.30 patch: expected v1.29 version markers missing')
g = g.replace('versionCode 39', 'versionCode 40', 1)
g = g.replace("versionName '1.29'", "versionName '1.30'", 1)

required = [
    'private int selectionConfirmationEpoch;',
    'private boolean selectionConfirmationPending;',
    'private String currentVoiceTailGuard(){',
    'private boolean currentSelectionAtOwnedVoiceTail(int start,int end){',
    'private void scheduleExternalSelectionConfirmation(int start,int end){',
    'setStatus("Voice stopped — selection confirmed off voice tail");',
    'if(currentSelectionAtOwnedVoiceTail(newSelStart,newSelEnd))return;',
    'scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);',
    'if(selectionConfirmationPending)return;',
    'selectionConfirmationEpoch++; selectionConfirmationPending=false;',
    'private String livePartialTail = "";',
    'versionCode 40',
    "versionName '1.30'",
]
text = s + '\n' + g
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.30 patch: required invariant missing: {needle}')

for forbidden in [
    'stopVoiceForManualInput();\n        setStatus("Voice stopped — selection changed");',
    'MAX_CAPTURE_MS',
    'boundConnection.setComposingText(partial,1);',
    'versionCode 39',
    "versionName '1.29'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.30 patch: forbidden old behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.30 confirmed external selection patch')
