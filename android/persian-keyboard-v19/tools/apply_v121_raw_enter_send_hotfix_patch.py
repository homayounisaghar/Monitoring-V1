from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.21 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


old_method = '''    private void sendFocusedField(){
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
'''

new_method = '''    private void sendFocusedField(){
        InputConnection ic=boundConnection;
        if(ic==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=ic){
            setStatus("Send cancelled — editor changed");
            return;
        }
        try{
            int advertised=editorInfo==null?EditorInfo.IME_ACTION_UNSPECIFIED:(editorInfo.imeOptions&EditorInfo.IME_MASK_ACTION);

            if(advertised==EditorInfo.IME_ACTION_SEND){
                boolean handled=ic.performEditorAction(EditorInfo.IME_ACTION_SEND);
                if(handled){setStatus("Sent");return;}
            }

            boolean down=ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_DOWN,KeyEvent.KEYCODE_ENTER));
            boolean up=ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_UP,KeyEvent.KEYCODE_ENTER));
            setStatus((down||up)?"Send key sent":"Send unavailable in this field");
        }catch(Exception e){
            setStatus("Send unavailable in this field");
        }
    }
'''

replace_once(old_method, new_method, 'replace v1.20 generic editor-action send path')

if 'versionCode 30' not in g or "versionName '1.20'" not in g:
    raise SystemExit('v1.21 patch: expected v1.20 version markers missing')
g = g.replace('versionCode 30', 'versionCode 31', 1)
g = g.replace("versionName '1.20'", "versionName '1.21'", 1)

required = [
    'if(advertised==EditorInfo.IME_ACTION_SEND){',
    'ic.performEditorAction(EditorInfo.IME_ACTION_SEND)',
    'ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_DOWN,KeyEvent.KEYCODE_ENTER))',
    'ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_UP,KeyEvent.KEYCODE_ENTER))',
    'setStatus((down||up)?"Send key sent":"Send unavailable in this field");',
    'private boolean sendAfterVoiceStop;',
    'mic.setOnLongClickListener(v -> stopVoiceAndSend());',
    'compactMic.setOnLongClickListener(v -> stopVoiceAndSend());',
    'if(shouldSend)main.postDelayed(this::sendFocusedField,40L);',
    'private void recoverSpeechTransport(String reason){',
    'String label=running?"🎙 "+badge():"🎙";',
    'private boolean capsLock;',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.21 patch: required invariant missing: {needle}')

for forbidden in [
    'if(customAction!=0)handled=ic.performEditorAction(customAction);',
    'advertised==EditorInfo.IME_ACTION_GO',
    'advertised==EditorInfo.IME_ACTION_DONE',
    'if(!handled)handled=ic.performEditorAction(EditorInfo.IME_ACTION_SEND);',
    'boolean multiline=(inputType&InputType.TYPE_TEXT_FLAG_MULTI_LINE)!=0;',
    'versionCode 30',
    "versionName '1.20'",
    'MAX_CAPTURE_MS',
]:
    if forbidden in s or forbidden in g:
        raise SystemExit(f'v1.21 patch: forbidden v1.20 behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.21 raw-Enter stop-and-send hotfix')
