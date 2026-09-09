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
        raise SystemExit(f'v1.41 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


def replace_region(text, start_marker, end_marker, transform, label):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f'v1.41 patch: missing start marker: {label}')
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f'v1.41 patch: missing end marker: {label}')
    block = text[start:end]
    new_block = transform(block)
    return text[:start] + new_block + text[end:]


# v1.41 is intentionally diagnostic. It preserves v1.40 behavior and records the
# exact IME/editor/accessibility causality needed to diagnose the two remaining
# real-device gates. No message text, selected text or speech transcript is logged.

s = rep(s,
'''public class PersianKeyboardService extends InputMethodService {\n    private static volatile PersianKeyboardService activeInstance;\n''',
'''public class PersianKeyboardService extends InputMethodService {\n    private static volatile PersianKeyboardService activeInstance;\n    private static final int DIAG_MAX_CHARS=60000;\n    private final StringBuilder diagBuffer=new StringBuilder();\n    private int diagSequence;\n''',
    'diagnostic fields')

# Add a privacy-preserving persistent ring buffer and a long-press clipboard export.
diag_methods = r'''    private String diagPackage(){
        return editorInfo==null||editorInfo.packageName==null?"-":editorInfo.packageName;
    }

    private void diag(String event){
        try{
            String line=(++diagSequence)+" t="+android.os.SystemClock.uptimeMillis()+" "+event+"\n";
            synchronized(diagBuffer){
                if(diagBuffer.length()==0){
                    String saved=getSharedPreferences("v141_diag",MODE_PRIVATE).getString("log","");
                    if(saved!=null&&!saved.isEmpty())diagBuffer.append(saved);
                }
                diagBuffer.append(line);
                if(diagBuffer.length()>DIAG_MAX_CHARS){
                    int cut=diagBuffer.length()-DIAG_MAX_CHARS;
                    int nl=diagBuffer.indexOf("\n",cut);
                    diagBuffer.delete(0,nl>=0?nl+1:cut);
                }
                getSharedPreferences("v141_diag",MODE_PRIVATE).edit().putString("log",diagBuffer.toString()).apply();
            }
        }catch(Exception ignored){}
    }

    private void diagCurrentEditor(String tag){
        try{
            InputConnection ic=boundConnection!=null?boundConnection:getCurrentInputConnection();
            if(ic==null){diag(tag+" ic=null running="+running+" gen="+inputGeneration+" pkg="+diagPackage());return;}
            VoiceEditorWindow w=currentVoiceEditorWindow(ic);
            if(w==null){
                diag(tag+" ic="+System.identityHashCode(ic)+" window=null running="+running+" gen="+inputGeneration+" activeGen="+activeGeneration+" pkg="+diagPackage());
                return;
            }
            diag(tag+" ic="+System.identityHashCode(ic)+" len="+w.text.length()+" abs="+w.absoluteStart+
                    " sel="+w.selectionStart+":"+w.selectionEnd+
                    " owned="+voiceOwnedStart+":"+voiceOwnedEnd+
                    " expected="+voiceExpectedSelectionStart+":"+voiceExpectedSelectionEnd+
                    " follow="+voiceSelectionFollowsOwnedRange+
                    " prog="+programmaticSelectionEditDepth+
                    " clearArmed="+voiceExternalClearStopArmed+
                    " running="+running+" run="+activeVoiceRunId+" pkg="+diagPackage());
        }catch(Exception e){diag(tag+" editorProbeException="+e.getClass().getSimpleName());}
    }

    private void copyDiagnosticsToClipboard(){
        try{
            String out;
            synchronized(diagBuffer){
                if(diagBuffer.length()==0){
                    String saved=getSharedPreferences("v141_diag",MODE_PRIVATE).getString("log","");
                    if(saved!=null)diagBuffer.append(saved);
                }
                out="Persian Keyboard v1.41 diagnostic\n"+diagBuffer.toString();
            }
            ClipboardManager cm=(ClipboardManager)getSystemService(Context.CLIPBOARD_SERVICE);
            if(cm==null){setStatus("DIAG clipboard unavailable");return;}
            cm.setPrimaryClip(ClipData.newPlainText("Persian keyboard diagnostic",out));
            setStatus("DIAG COPIED");
        }catch(Exception e){setStatus("DIAG copy failed");}
    }

    public static void notifyAccessibilityProbe(String sourcePackage,int eventType,int contentChanges,
            String className,String viewId,boolean clickable,boolean editable,boolean focused,
            int left,int top,int right,int bottom,int semantic,long eventTime){
        PersianKeyboardService service=activeInstance;
        if(service==null)return;
        service.main.post(()->service.diag("A11Y type="+eventType+" cc="+contentChanges+
                " pkg="+(sourcePackage==null?"-":sourcePackage)+
                " class="+(className==null?"-":className)+
                " id="+(viewId==null?"-":viewId)+
                " click="+clickable+" edit="+editable+" focus="+focused+
                " bounds="+left+","+top+","+right+","+bottom+
                " semantic="+semantic+" eventT="+eventTime));
    }

'''
on_create_marker = '    @Override public void onCreate() {'
if on_create_marker not in s:
    raise SystemExit('v1.41 patch: onCreate marker missing')
s = s.replace(on_create_marker, diag_methods + on_create_marker, 1)

s = rep(s,
'''        activeInstance=this;\n''',
'''        activeInstance=this;\n        diag("SERVICE_CREATE");\n''',
    'service create trace')

# Normal Copy stays unchanged. Long-press exports only structural diagnostics.
s = rep(s,
'''        Button copy = toolbarButton("Copy", v -> copyCurrentText());\n        copy.setContentDescription("Copy selected text or entire field");\n        left.addView(copy, toolbarLp(1f));\n''',
'''        Button copy = toolbarButton("Copy", v -> copyCurrentText());\n        copy.setContentDescription("Copy selected text or entire field; long press copies diagnostics");\n        copy.setOnLongClickListener(v -> {copyDiagnosticsToClipboard();return true;});\n        left.addView(copy, toolbarLp(1f));\n''',
    'long press Copy diagnostics export')

# Lifecycle traces. These are the callbacks Android documents as the IME/editor
# lifecycle and selection/extracted-text notification surface.
s = rep(s,
'''    @Override public void onStartInput(EditorInfo attribute, boolean restarting) {\n''',
'''    @Override public void onStartInput(EditorInfo attribute, boolean restarting) {\n        diag("LIFE onStartInput restarting="+restarting+" incomingPkg="+(attribute==null||attribute.packageName==null?"-":attribute.packageName)+" running="+running+" gen="+inputGeneration);\n''',
    'onStartInput trace')

s = rep(s,
'''    @Override public void onStartInputView(EditorInfo info, boolean restarting) {\n''',
'''    @Override public void onStartInputView(EditorInfo info, boolean restarting) {\n        diag("LIFE onStartInputView restarting="+restarting+" incomingPkg="+(info==null||info.packageName==null?"-":info.packageName)+" running="+running+" gen="+inputGeneration);\n''',
    'onStartInputView trace')

s = rep(s,
'''    @Override public void onFinishInput() {\n''',
'''    @Override public void onFinishInput() {\n        diag("LIFE onFinishInput running="+running+" gen="+inputGeneration+" pkg="+diagPackage());\n        diagCurrentEditor("LIFE onFinishInput state");\n''',
    'onFinishInput trace')

s = rep(s,
'''    @Override public void onFinishInputView(boolean finishingInput) {\n''',
'''    @Override public void onFinishInputView(boolean finishingInput) {\n        diag("LIFE onFinishInputView finishing="+finishingInput+" running="+running+" pkg="+diagPackage());\n        diagCurrentEditor("LIFE onFinishInputView state");\n''',
    'onFinishInputView trace')

s = rep(s,
'''    @Override public void onWindowHidden() {\n''',
'''    @Override public void onWindowHidden() {\n        diag("LIFE onWindowHidden running="+running+" pkg="+diagPackage());\n        diagCurrentEditor("LIFE onWindowHidden state");\n''',
    'onWindowHidden trace')

s = rep(s,
'''        activeGeneration=inputGeneration;\n        captureVoiceInsertionBoundary();\n''',
'''        activeGeneration=inputGeneration;\n        diag("VOICE_START run="+runId+" ic="+System.identityHashCode(ic)+" gen="+inputGeneration+" pkg="+diagPackage());\n        diagCurrentEditor("VOICE_START beforeCapture");\n        captureVoiceInsertionBoundary();\n''',
    'voice start trace')

s = rep(s,
'''    private void stopVoiceForManualInput(){\n        if(!running)return;\n''',
'''    private void stopVoiceForManualInput(){\n        diag("VOICE_STOP manual-entry running="+running+" run="+activeVoiceRunId+" pkg="+diagPackage());\n        diagCurrentEditor("VOICE_STOP manual-entry state");\n        if(!running)return;\n''',
    'manual stop trace')

s = rep(s,
'''    private void stopVoiceForImeHidden(){\n        if(running)stopVoiceForManualInput();\n''',
'''    private void stopVoiceForImeHidden(){\n        diag("VOICE_STOP ime-hidden running="+running+" run="+activeVoiceRunId+" pkg="+diagPackage());\n        diagCurrentEditor("VOICE_STOP ime-hidden state");\n        if(running)stopVoiceForManualInput();\n''',
    'IME hide stop trace')

# Instrument v1.40 selection callback without changing any branch or mutation.
def instrument_selection(block):
    old = '        super.onUpdateSelection(oldSelStart, oldSelEnd, newSelStart, newSelEnd, candidatesStart, candidatesEnd);\n'
    new = old + '        diag("SEL callback old="+oldSelStart+":"+oldSelEnd+" new="+newSelStart+":"+newSelEnd+" cand="+candidatesStart+":"+candidatesEnd+" expected="+voiceExpectedSelectionStart+":"+voiceExpectedSelectionEnd+" prog="+programmaticSelectionEditDepth+" running="+running+" run="+activeVoiceRunId);\n'
    if old not in block:
        raise SystemExit('v1.41 patch: selection super marker missing')
    block = block.replace(old,new,1)
    old2 = '            VoiceEditorWindow current=currentVoiceEditorWindow(ic);\n'
    new2 = old2 + '            if(current==null)diag("SEL settle window=null"); else diag("SEL settle current="+current.selectionStart+":"+current.selectionEnd+" len="+current.text.length()+" expected="+voiceExpectedSelectionStart+":"+voiceExpectedSelectionEnd+" owned="+voiceOwnedStart+":"+voiceOwnedEnd);\n'
    if old2 not in block:
        raise SystemExit('v1.41 patch: selection settle marker missing')
    return block.replace(old2,new2,1)

s = replace_region(s, '    @Override public void onUpdateSelection(', '    private long selectionKey(',
                   instrument_selection, 'selection trace')

# Instrument extracted-text monitor; lengths/selection only, never text content.
def instrument_extracted(block):
    old = '        super.onUpdateExtractedText(token,text);\n'
    new = old + '        diag("EXTRACT token="+token+" expectedToken="+voiceExtractMonitorToken+" null="+(text==null)+" len="+(text==null||text.text==null?-1:text.text.length())+" start="+(text==null?-1:text.startOffset)+" sel="+(text==null?-1:text.selectionStart)+":"+(text==null?-1:text.selectionEnd)+" partial="+(text==null?-1:text.partialStartOffset)+":"+(text==null?-1:text.partialEndOffset)+" running="+running+" clearArmed="+voiceExternalClearStopArmed+" prog="+programmaticSelectionEditDepth);\n'
    if old not in block:
        raise SystemExit('v1.41 patch: extracted-text super marker missing')
    return block.replace(old,new,1)

s = replace_region(s, '    @Override public void onUpdateExtractedText(', '    @Override public void onUpdateSelection(',
                   instrument_extracted, 'extracted-text trace')

# Trace cutover and clear-stop decisions while preserving v1.40 behavior.
s = rep(s,
'''    private boolean stopVoiceIfExternalComposerCleared(VoiceEditorWindow supplied){\n        if(!running||!voiceExternalClearStopArmed)return false;\n''',
'''    private boolean stopVoiceIfExternalComposerCleared(VoiceEditorWindow supplied){\n        diag("CLEAR_CHECK enter supplied="+(supplied!=null)+" running="+running+" armed="+voiceExternalClearStopArmed+" run="+activeVoiceRunId);\n        if(!running||!voiceExternalClearStopArmed)return false;\n''',
    'clear-stop entry trace')

s = rep(s,
'''        if(current==null)return false;\n        if(!current.text.isEmpty()){\n''',
'''        if(current==null){diag("CLEAR_CHECK window=null");return false;}\n        diag("CLEAR_CHECK state len="+current.text.length()+" sel="+current.selectionStart+":"+current.selectionEnd+" owned="+voiceOwnedStart+":"+voiceOwnedEnd);\n        if(!current.text.isEmpty()){\n''',
    'clear-stop editor-state trace')

s = rep(s,
'''        stopVoiceForManualInput();\n        clearVoiceCaretRebaseCandidate();\n''',
'''        diag("CLEAR_CHECK STOP composer-empty");\n        stopVoiceForManualInput();\n        clearVoiceCaretRebaseCandidate();\n''',
    'clear-stop success trace')

s = rep(s,
'''    private void beginVoiceCaretCutover(int targetStart,int targetEnd,long runId,VoiceEditorWindow window){\n        if(!voiceRunActive(runId)||window==null)return;\n''',
'''    private void beginVoiceCaretCutover(int targetStart,int targetEnd,long runId,VoiceEditorWindow window){\n        diag("CUTOVER enter target="+targetStart+":"+targetEnd+" windowSel="+(window==null?"null":window.selectionStart+":"+window.selectionEnd)+" owned="+voiceOwnedStart+":"+voiceOwnedEnd+" expected="+voiceExpectedSelectionStart+":"+voiceExpectedSelectionEnd+" run="+runId);\n        if(!voiceRunActive(runId)||window==null)return;\n''',
    'caret cutover trace')

s = rep(s,
'''        restartSpeechTransportForCaretCutover(runId);\n    }\n''',
'''        diagCurrentEditor("CUTOVER beforeTransportRestart");\n        restartSpeechTransportForCaretCutover(runId);\n    }\n''',
    'caret cutover settled trace')

s = rep(s,
'''    private void handleHostSendFromAccessibility(String sourcePackage,long eventTime){\n        if(!running||!hostPackageMatchesCurrentEditor(sourcePackage))return;\n''',
'''    private void handleHostSendFromAccessibility(String sourcePackage,long eventTime){\n        diag("HOST_SEND callback pkg="+sourcePackage+" eventT="+eventTime+" currentPkg="+diagPackage()+" running="+running);\n        diagCurrentEditor("HOST_SEND state");\n        if(!running||!hostPackageMatchesCurrentEditor(sourcePackage))return;\n''',
    'host Send callback trace')

s = rep(s,
'''    private void handleHostContentChangedFromAccessibility(String sourcePackage,long eventTime){\n        if(!running||!hostPackageMatchesCurrentEditor(sourcePackage))return;\n        stopVoiceIfExternalComposerCleared(null);\n''',
'''    private void handleHostContentChangedFromAccessibility(String sourcePackage,long eventTime){\n        diag("HOST_CONTENT callback pkg="+sourcePackage+" eventT="+eventTime+" currentPkg="+diagPackage()+" running="+running);\n        diagCurrentEditor("HOST_CONTENT state");\n        if(!running||!hostPackageMatchesCurrentEditor(sourcePackage))return;\n        stopVoiceIfExternalComposerCleared(null);\n''',
    'host content callback trace')

# Accessibility probe: log only structure, IDs and event metadata. Never event text.
def instrument_accessibility(block):
    marker = '        int type=event.getEventType();\n'
    addition = r'''        String probePackage=value(event.getPackageName());
        AccessibilityNodeInfo probeSource=event.getSource();
        String probeClass=probeSource==null?value(event.getClassName()):value(probeSource.getClassName());
        String probeId=probeSource==null?"":value(probeSource.getViewIdResourceName());
        boolean probeClickable=probeSource!=null&&probeSource.isClickable();
        boolean probeEditable=probeSource!=null&&probeSource.isEditable();
        boolean probeFocused=probeSource!=null&&probeSource.isFocused();
        Rect probeBounds=new Rect();
        if(probeSource!=null)probeSource.getBoundsInScreen(probeBounds);
        int probeSemantic=probeSource==null?0:semanticScore(probeSource);
        PersianKeyboardService.notifyAccessibilityProbe(probePackage,type,event.getContentChangeTypes(),probeClass,probeId,
                probeClickable,probeEditable,probeFocused,probeBounds.left,probeBounds.top,probeBounds.right,probeBounds.bottom,
                probeSemantic,event.getEventTime());
'''
    if marker not in block:
        raise SystemExit('v1.41 patch: accessibility type marker missing')
    return block.replace(marker, marker + addition, 1)

h = replace_region(h, '    @Override public void onAccessibilityEvent(AccessibilityEvent event) {',
                   '    @Override public void onInterrupt() {}', instrument_accessibility,
                   'accessibility structural trace')

# Subscribe to the two text-related event families for diagnosis only. Existing
# v1.40 content-changed/click behavior remains untouched.
if 'typeViewClicked' not in a:
    raise SystemExit('v1.41 patch: expected v1.40 accessibility subscription missing')
if 'typeViewTextChanged' not in a:
    a = a.replace('typeViewClicked', 'typeViewClicked|typeViewTextChanged|typeViewTextSelectionChanged', 1)

if 'versionCode 50' not in g or "versionName '1.40'" not in g:
    raise SystemExit('v1.41 patch: v1.40 Gradle version markers missing')
g = g.replace('versionCode 50', 'versionCode 51', 1)
g = g.replace("versionName '1.40'", "versionName '1.41'", 1)

text = s + '\n' + h + '\n' + a + '\n' + g
required = [
    'DIAG_MAX_CHARS=60000',
    'private void diag(String event)',
    'private void diagCurrentEditor(String tag)',
    'private void copyDiagnosticsToClipboard()',
    'copy.setOnLongClickListener',
    'public static void notifyAccessibilityProbe(',
    'SEL callback old=',
    'SEL settle current=',
    'EXTRACT token=',
    'CLEAR_CHECK enter',
    'CUTOVER enter target=',
    'HOST_SEND callback',
    'HOST_CONTENT callback',
    'A11Y type=',
    'typeViewTextChanged',
    'typeViewTextSelectionChanged',
    'versionCode 51',
    "versionName '1.41'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.41 patch: required invariant missing: {needle}')

# Diagnostic build must not reintroduce the known harmful paths or change v1.40's
# user-caret contract.
for forbidden in [
    'rebaseVoiceProjectionIfPending(',
    'scheduleInternalSelectionReanchor();',
    'scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);',
    'Voice stopped — live text sync lost',
    'versionCode 50',
    "versionName '1.40'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.41 patch: forbidden old behavior remains: {forbidden}')

sel_start=s.index('    @Override public void onUpdateSelection(')
sel_end=s.index('    private long selectionKey(',sel_start)
selection_block=s[sel_start:sel_end]
assert 'setSelection(' not in selection_block
cut_start=s.index('    private void beginVoiceCaretCutover(')
cut_end=s.index('    private void restartSpeechTransportForCaretCutover(',cut_start)
cutover_block=s[cut_start:cut_end]
for forbidden in ['setSelection(','commitText(','deleteSurroundingText(']:
    assert forbidden not in cutover_block, forbidden

service.write_text(s)
helper.write_text(h)
accessibility_xml.write_text(a)
gradle_file.write_text(g)
print('Applied v1.41 diagnostic IME/editor/accessibility event trace patch')
