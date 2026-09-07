from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.28 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# v1.27 ruled out one false-stop source (selection-coordinate mismatch) but
# real-device testing still reproduced an involuntary microphone stop while all
# v1.26 live-text behavior remained healthy. Android explicitly reports
# onStartInput(..., restarting=true) when input is restarting in the SAME editor,
# for example after the application changes editor text. The old code aborted any
# running voice session on every onStartInput call, so a benign same-editor
# restart was indistinguishable from a genuine editor/focus change.
replace_once(
'''    @Override public void onStartInput(EditorInfo attribute, boolean restarting) {
        super.onStartInput(attribute, restarting);
        editorInfo = attribute;
        inputGeneration++;
        if (running) abortForEditorChange();
        shift = false;
        int klass = attribute == null ? InputType.TYPE_CLASS_TEXT : (attribute.inputType & InputType.TYPE_MASK_CLASS);
        layer = (klass == InputType.TYPE_CLASS_NUMBER || klass == InputType.TYPE_CLASS_PHONE) ? Layer.NUMPAD : Layer.ALPHA;
        main.post(this::render);
    }
''',
'''    @Override public void onStartInput(EditorInfo attribute, boolean restarting) {
        super.onStartInput(attribute, restarting);
        editorInfo = attribute;

        // Android guarantees restarting=true means input is restarting in the
        // same editor. Preserve the active speech session and only rebind the
        // InputConnection; do not bump inputGeneration or tear down transport.
        if(running&&restarting){
            InputConnection current=getCurrentInputConnection();
            if(current!=null){
                boundConnection=current;
                activeGeneration=inputGeneration;
                synchronized(expectedSelectionUpdates){expectedSelectionUpdates.clear();}
                setStatus(listeningText());
            }else{
                final long generation=inputGeneration;
                main.post(()->{
                    if(!running||generation!=inputGeneration)return;
                    InputConnection rebound=getCurrentInputConnection();
                    if(rebound==null){abortForEditorChange("restart rebind failed");return;}
                    boundConnection=rebound;
                    activeGeneration=inputGeneration;
                    synchronized(expectedSelectionUpdates){expectedSelectionUpdates.clear();}
                    setStatus(listeningText());
                });
            }
            main.post(this::render);
            return;
        }

        inputGeneration++;
        if (running) abortForEditorChange("new input");
        shift = false;
        int klass = attribute == null ? InputType.TYPE_CLASS_TEXT : (attribute.inputType & InputType.TYPE_MASK_CLASS);
        layer = (klass == InputType.TYPE_CLASS_NUMBER || klass == InputType.TYPE_CLASS_PHONE) ? Layer.NUMPAD : Layer.ALPHA;
        main.post(this::render);
    }
''',
    'same-editor restart must not cancel voice',
)

replace_once(
'''    @Override public void onFinishInput() {
        inputGeneration++;
        if (running) abortForEditorChange();
        editorInfo = null;
        super.onFinishInput();
    }
''',
'''    @Override public void onFinishInput() {
        inputGeneration++;
        if (running) abortForEditorChange("finish input");
        editorInfo = null;
        super.onFinishInput();
    }
''',
    'diagnose true finish-input cancellation',
)

# Keep the old no-argument helper for existing call sites, but make automatic
# cancellations self-identifying on the keyboard status line. If v1.28 still
# stops on-device, the next reproduction will distinguish lifecycle, connection,
# selection, and Soniox causes instead of forcing another guess.
replace_once(
'''    private void abortForEditorChange(){
        sendAfterVoiceStop=false;
        InputConnection old=boundConnection;running=false;stopRequested=true;awaitingCredential=false;stopAudioRecord();clearPending();WebSocket ws=webSocket;webSocket=null;if(ws!=null)ws.cancel();if(old!=null)try{old.finishComposingText();}catch(Exception ignored){} boundConnection=null;
        main.post(()->{setCollapsed(false);updateMicUi();setStatus("Voice cancelled — editor changed");});
    }
''',
'''    private void abortForEditorChange(){abortForEditorChange("editor changed");}
    private void abortForEditorChange(String reason){
        sendAfterVoiceStop=false;
        InputConnection old=boundConnection;running=false;stopRequested=true;awaitingCredential=false;stopAudioRecord();clearPending();WebSocket ws=webSocket;webSocket=null;if(ws!=null)ws.cancel();if(old!=null)try{old.finishComposingText();}catch(Exception ignored){} boundConnection=null;
        final String why=(reason==null||reason.isEmpty())?"editor changed":reason;
        main.post(()->{setCollapsed(false);updateMicUi();setStatus("Voice cancelled — "+why);});
    }
''',
    'reasoned automatic cancellation diagnostics',
)

replace_once(
'''            if(boundConnection==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=boundConnection){if(running)abortForEditorChange();return;}
''',
'''            if(boundConnection==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=boundConnection){if(running)abortForEditorChange("connection mismatch");return;}
''',
    'diagnose publish connection mismatch',
)

replace_once(
'''        if(withinComposing)return;
        stopVoiceForManualInput();
    }
''',
'''        if(withinComposing)return;
        stopVoiceForManualInput();
        setStatus("Voice stopped — selection changed");
    }
''',
    'diagnose selection-triggered stop',
)

replace_once(
'''if(o.has("error_code")&&!o.isNull("error_code")){if(recoverableSonioxError(o)){recoverSpeechTransport(o.optString("error_type","Soniox error"));return;}finishWithText("Soniox error");return;}''',
'''if(o.has("error_code")&&!o.isNull("error_code")){if(recoverableSonioxError(o)){recoverSpeechTransport(o.optString("error_type","Soniox error"));return;}finishWithText("Soniox stop "+o.optInt("error_code",0)+" / "+o.optString("error_type","unknown"));return;}''',
    'diagnose unrecoverable Soniox stop',
)

if 'versionCode 37' not in g or "versionName '1.27'" not in g:
    raise SystemExit('v1.28 patch: expected v1.27 version markers missing')
g = g.replace('versionCode 37', 'versionCode 38', 1)
g = g.replace("versionName '1.27'", "versionName '1.28'", 1)

required = [
    'if(running&&restarting){',
    'boundConnection=current;',
    'activeGeneration=inputGeneration;',
    'abortForEditorChange("restart rebind failed")',
    'abortForEditorChange("new input")',
    'abortForEditorChange("finish input")',
    'private void abortForEditorChange(String reason){',
    'Voice cancelled — "+why',
    'abortForEditorChange("connection mismatch")',
    'Voice stopped — selection changed',
    'Soniox stop "+o.optInt("error_code",0)',
    'private String livePartialTail = "";',
    'if(!selectionCallbackMatchesEditorNow(newSelStart,newSelEnd))return;',
    'versionCode 38',
    "versionName '1.28'",
]
text = s + '\n' + g
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.28 patch: required invariant missing: {needle}')

for forbidden in [
    'if (running) abortForEditorChange();',
    'finishWithText("Soniox error")',
    'MAX_CAPTURE_MS',
    'boundConnection.setComposingText(partial,1);',
    'versionCode 37',
    "versionName '1.27'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.28 patch: forbidden old behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.28 restart-tolerant lifecycle patch')
