from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.27 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# v1.27 fixes false voice cancellation caused by IME-generated selection callbacks.
# ExtractedText.selectionStart/End are relative to ExtractedText.startOffset, while
# onUpdateSelection reports editor-global positions. Once an editor returns a
# windowed ExtractedText for longer content, v1.26 could mistake its own commit/
# delete cursor movement for an external user tap and call stopVoiceForManualInput().
replace_once(
'''    private void rememberProgrammaticSelection(){
        InputConnection ic=boundConnection;if(ic==null)return;
        try{
            android.view.inputmethod.ExtractedTextRequest req=new android.view.inputmethod.ExtractedTextRequest();
            android.view.inputmethod.ExtractedText et=ic.getExtractedText(req,0);
            if(et==null)return;
            long key=selectionKey(et.selectionStart,et.selectionEnd);
            synchronized(expectedSelectionUpdates){
                while(expectedSelectionUpdates.size()>=10)expectedSelectionUpdates.removeFirst();
                expectedSelectionUpdates.addLast(key);
            }
        }catch(Exception ignored){}
    }
''',
'''    private void rememberProgrammaticSelection(){
        InputConnection ic=boundConnection;if(ic==null)return;
        try{
            android.view.inputmethod.ExtractedTextRequest req=new android.view.inputmethod.ExtractedTextRequest();
            android.view.inputmethod.ExtractedText et=ic.getExtractedText(req,0);
            if(et==null)return;
            int start=et.selectionStart;
            int end=et.selectionEnd;
            if(start>=0)start+=et.startOffset;
            if(end>=0)end+=et.startOffset;
            long key=selectionKey(start,end);
            synchronized(expectedSelectionUpdates){
                while(expectedSelectionUpdates.size()>=10)expectedSelectionUpdates.removeFirst();
                expectedSelectionUpdates.addLast(key);
            }
        }catch(Exception ignored){}
    }

    private boolean selectionCallbackMatchesEditorNow(int start,int end){
        InputConnection ic=boundConnection;
        if(ic==null||getCurrentInputConnection()!=ic)return false;
        try{
            android.view.inputmethod.ExtractedTextRequest req=new android.view.inputmethod.ExtractedTextRequest();
            android.view.inputmethod.ExtractedText et=ic.getExtractedText(req,0);
            if(et==null)return true;
            int actualStart=et.selectionStart;
            int actualEnd=et.selectionEnd;
            if(actualStart>=0)actualStart+=et.startOffset;
            if(actualEnd>=0)actualEnd+=et.startOffset;
            return actualStart==start&&actualEnd==end;
        }catch(Exception ignored){
            // Fall back to the existing stop semantics if the editor cannot
            // provide a snapshot; never suppress a real user movement blindly.
            return true;
        }
    }
''',
    'absolute programmatic selection coordinates',
)

replace_once(
'''        if(!running)return;
        if(oldSelStart==newSelStart&&oldSelEnd==newSelEnd)return;
        if(consumeExpectedSelection(newSelStart,newSelEnd))return;
        boolean withinComposing=candidatesStart>=0&&candidatesEnd>=candidatesStart
''',
'''        if(!running)return;
        if(oldSelStart==newSelStart&&oldSelEnd==newSelEnd)return;
        // Multiple selection callbacks can be emitted for one batch edit. By the
        // time the IME main thread receives an intermediate callback, the editor
        // may already be at the final programmatic cursor. Ignore only callbacks
        // that no longer describe the editor's current selection; a real user tap
        // still matches the current editor snapshot and keeps the original stop.
        if(!selectionCallbackMatchesEditorNow(newSelStart,newSelEnd))return;
        if(consumeExpectedSelection(newSelStart,newSelEnd))return;
        boolean withinComposing=candidatesStart>=0&&candidatesEnd>=candidatesStart
''',
    'ignore stale programmatic selection callbacks',
)

# A transient inability to prove ownership of the live provisional tail is a
# text-publication safety event, not proof that the user requested audio stop.
# Keep fail-closed editor mutation semantics (do not delete/append anything), but
# leave AudioRecord/WebSocket alive. Real editor/focus changes are still handled
# by onStartInput/onFinishInput, bound-connection checks and onUpdateSelection.
replace_once(
'''            if(!editorEndsWithLiveTail()){
                // The caret/editor no longer contains the provisional text that
                // this IME owns. Continuing would risk duplicates or deletion of
                // user text, so fail closed rather than guessing.
                setStatus(persian?"همگام‌سازی متن زنده از دست رفت":"Live text resync lost");
                abortForEditorChange();
                return;
            }
''',
'''            if(!editorEndsWithLiveTail()){
                // Do not mutate text if ownership cannot be proven. This remains
                // fail-closed for duplicate/deletion safety, but it must not stop
                // an otherwise healthy recording session. A later transcript
                // update can retry once the editor snapshot is coherent again.
                return;
            }
''',
    'live-tail mismatch must not stop audio',
)

replace_once(
'''            }catch(Exception e){
                abortForEditorChange();
                return;
            }finally{
''',
'''            }catch(Exception e){
                // A transient InputConnection mutation failure is not evidence of
                // an explicit user stop. Leave speech transport alive and skip
                // only this unsafe publication attempt.
                return;
            }finally{
''',
    'publication exception must not stop audio',
)

if 'versionCode 36' not in g or "versionName '1.26'" not in g:
    raise SystemExit('v1.27 patch: expected v1.26 version markers missing')
g = g.replace('versionCode 36', 'versionCode 37', 1)
g = g.replace("versionName '1.26'", "versionName '1.27'", 1)

required = [
    'if(start>=0)start+=et.startOffset;',
    'private boolean selectionCallbackMatchesEditorNow(int start,int end){',
    'if(!selectionCallbackMatchesEditorNow(newSelStart,newSelEnd))return;',
    'it must not stop',
    'versionCode 37',
    "versionName '1.27'",
]
text = s + '\n' + g
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.27 patch: required invariant missing: {needle}')

for forbidden in [
    'long key=selectionKey(et.selectionStart,et.selectionEnd);',
    'MAX_CAPTURE_MS',
    'boundConnection.setComposingText(partial,1);',
    'versionCode 36',
    "versionName '1.26'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.27 patch: forbidden old behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.27 manual-stop semantics patch')
