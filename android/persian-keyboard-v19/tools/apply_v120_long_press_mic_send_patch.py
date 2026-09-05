from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.20 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# v1.20 adds a second stop gesture to the microphone button:
# - normal tap while recording: stop only (existing behavior)
# - long press while recording: stop, wait for final transcript commit, then submit
#   the same focused editor via its real IME action.

replace_once(
'''    private volatile boolean speechRecovering;
    private volatile int speechRecoveryEpoch;
''',
'''    private volatile boolean speechRecovering;
    private volatile int speechRecoveryEpoch;
    private boolean sendAfterVoiceStop;
''',
    'pending stop-and-send state',
)

replace_once(
'''        mic = toolbarButton("🎙", v -> toggleVoice());
        bar.addView(mic, toolbarLp(1f));
''',
'''        mic = toolbarButton("🎙", v -> toggleVoice());
        mic.setContentDescription("Microphone; long press while recording to stop and send");
        mic.setOnLongClickListener(v -> stopVoiceAndSend());
        bar.addView(mic, toolbarLp(1f));
''',
    'main microphone long press',
)

replace_once(
'''        compactMic = smallButton("🎙 " + badge(), v -> toggleVoice());
        compact.addView(compactMic, new LinearLayout.LayoutParams(dp(78), dp(42)));
''',
'''        compactMic = smallButton("🎙 " + badge(), v -> toggleVoice());
        compactMic.setContentDescription("Microphone; long press while recording to stop and send");
        compactMic.setOnLongClickListener(v -> stopVoiceAndSend());
        compact.addView(compactMic, new LinearLayout.LayoutParams(dp(78), dp(42)));
''',
    'compact microphone long press',
)

replace_once(
'''    private void toggleVoice(){if(running)requestStop();else startVoice();}

    private void startVoice(){
''',
'''    private void toggleVoice(){if(running)requestStop();else startVoice();}

    private boolean stopVoiceAndSend(){
        if(!running)return false;
        sendAfterVoiceStop=true;
        requestStop();
        return true;
    }

    private void sendFocusedField(){
        InputConnection ic=boundConnection;
        if(ic==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=ic){
            setStatus("Send cancelled — editor changed");
            return;
        }
        try{
            boolean handled=false;
            int customAction=editorInfo==null?0:editorInfo.actionId;
            int advertised=editorInfo==null?EditorInfo.IME_ACTION_UNSPECIFIED:(editorInfo.imeOptions&EditorInfo.IME_MASK_ACTION);

            if(customAction!=0)handled=ic.performEditorAction(customAction);
            if(!handled&&(advertised==EditorInfo.IME_ACTION_SEND||advertised==EditorInfo.IME_ACTION_GO||advertised==EditorInfo.IME_ACTION_DONE)){
                handled=ic.performEditorAction(advertised);
            }
            if(!handled)handled=ic.performEditorAction(EditorInfo.IME_ACTION_SEND);

            // Only fall back to an Enter key for a single-line editor. In a
            // multiline field, an Enter fallback could insert a newline instead
            // of sending, so it is safer to leave the text untouched.
            if(!handled){
                int inputType=editorInfo==null?0:editorInfo.inputType;
                boolean multiline=(inputType&InputType.TYPE_TEXT_FLAG_MULTI_LINE)!=0;
                if(!multiline){
                    boolean down=ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_DOWN,KeyEvent.KEYCODE_ENTER));
                    boolean up=ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_UP,KeyEvent.KEYCODE_ENTER));
                    handled=down||up;
                }
            }
            setStatus(handled?"Sent":"Send unavailable in this field");
        }catch(Exception e){
            setStatus("Send unavailable in this field");
        }
    }

    private void startVoice(){
''',
    'stop-and-send helper',
)

replace_once(
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; updateMicUi();
''',
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; sendAfterVoiceStop=false; updateMicUi();
''',
    'clear pending send when voice starts',
)

replace_once(
'''    private void stopVoiceForManualInput(){
        if(!running)return;
        running=false; completed=true; stopRequested=true; awaitingCredential=false; retryAfterPageLoad=false;
''',
'''    private void stopVoiceForManualInput(){
        if(!running)return;
        sendAfterVoiceStop=false;
        running=false; completed=true; stopRequested=true; awaitingCredential=false; retryAfterPageLoad=false;
''',
    'manual key cancels pending send',
)

replace_once(
'''    private void abortForEditorChange(){
        InputConnection old=boundConnection;running=false;stopRequested=true;awaitingCredential=false;stopAudioRecord();clearPending();WebSocket ws=webSocket;webSocket=null;if(ws!=null)ws.cancel();if(old!=null)try{old.finishComposingText();}catch(Exception ignored){} boundConnection=null;
''',
'''    private void abortForEditorChange(){
        sendAfterVoiceStop=false;
        InputConnection old=boundConnection;running=false;stopRequested=true;awaitingCredential=false;stopAudioRecord();clearPending();WebSocket ws=webSocket;webSocket=null;if(ws!=null)ws.cancel();if(old!=null)try{old.finishComposingText();}catch(Exception ignored){} boundConnection=null;
''',
    'editor change cancels pending send',
)

replace_once(
'''    private void completeSession(String m){running=false;stopRequested=true;awaitingCredential=false;stopAudioRecord();clearPending();main.post(()->{setCollapsed(false);updateMicUi();setStatus(m);});}
''',
'''    private void completeSession(String m){
        boolean shouldSend=sendAfterVoiceStop;
        sendAfterVoiceStop=false;
        running=false;stopRequested=true;awaitingCredential=false;stopAudioRecord();clearPending();
        main.post(()->{
            setCollapsed(false);updateMicUi();setStatus(m);
            // publish(true) is queued before completeSession(), so this follow-up
            // executes only after the final transcript has been committed.
            if(shouldSend)main.postDelayed(this::sendFocusedField,40L);
        });
    }
''',
    'send only after final transcript commit',
)

if 'versionCode 29' not in g or "versionName '1.19'" not in g:
    raise SystemExit('v1.20 patch: expected v1.19 version markers missing')
g = g.replace('versionCode 29', 'versionCode 30', 1)
g = g.replace("versionName '1.19'", "versionName '1.20'", 1)

required = [
    'private boolean sendAfterVoiceStop;',
    'mic.setOnLongClickListener(v -> stopVoiceAndSend());',
    'compactMic.setOnLongClickListener(v -> stopVoiceAndSend());',
    'private boolean stopVoiceAndSend(){',
    'sendAfterVoiceStop=true;',
    'private void sendFocusedField(){',
    'ic.performEditorAction(EditorInfo.IME_ACTION_SEND)',
    'editorInfo.imeOptions&EditorInfo.IME_MASK_ACTION',
    'InputType.TYPE_TEXT_FLAG_MULTI_LINE',
    'if(shouldSend)main.postDelayed(this::sendFocusedField,40L);',
    'sendAfterVoiceStop=false; updateMicUi();',
    'private volatile boolean speechRecovering;',
    'private void recoverSpeechTransport(String reason){',
    'Button copy = toolbarButton("⧉", v -> copyCurrentText());',
    'String label=running?"🎙 "+badge():"🎙";',
    'private boolean capsLock;',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.20 patch: required invariant missing: {needle}')

for forbidden in [
    'versionCode 29',
    "versionName '1.19'",
    'MAX_CAPTURE_MS',
    '@Override public void onClosed(WebSocket ws,int code,String reason){if(running&&!completed)finishWithText("Connection closed");}',
    'String label=running?"🎙 "+badge():"🎤";',
]:
    if forbidden in s or forbidden in g:
        raise SystemExit(f'v1.20 patch: forbidden old behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.20 long-press microphone stop-and-send patch')
