from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.15 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# Replace the right-most Gboard switch with a clear-current-field action. Keep the
# existing floating handle immediately to its left and leave speech/floating logic unchanged.
replace_once(
'''        Button gboard = toolbarButton("G", v -> switchToGboard());
        gboard.setContentDescription("Switch to Gboard");
        right.addView(gboard, toolbarLp(1f));
''',
'''        Button clearField = toolbarButton("×", v -> clearCurrentTextField());
        clearField.setContentDescription("Clear text field");
        right.addView(clearField, toolbarLp(1f));
''',
    'replace Gboard toolbar button with clear-field button',
)

# The old switch implementation is no longer exposed or needed. The replacement
# clears the complete active editor using the editor-native Select All action first,
# then falls back to extracted text / surrounding text for less-complete editors.
replace_once(
'''    private void switchToGboard(){
        stopVoiceForManualInput(); InputMethodManager imm=(InputMethodManager)getSystemService(INPUT_METHOD_SERVICE); String id=null;
        if(imm!=null)try{for(InputMethodInfo i:imm.getEnabledInputMethodList())if(GBOARD_PACKAGE.equals(i.getPackageName())){id=i.getId();break;}}catch(Exception ignored){}
        if(id!=null)try{java.lang.reflect.Method m=InputMethodService.class.getMethod("switchInputMethod",String.class);m.invoke(this,id);return;}catch(Exception ignored){}
        try{if(switchToNextInputMethod(false))return;}catch(Exception ignored){} if(imm!=null)try{imm.showInputMethodPicker();}catch(Exception ignored){}
    }
''',
'''    private void clearCurrentTextField(){
        stopVoiceForManualInput();
        InputConnection ic=getCurrentInputConnection();
        if(ic==null){setStatus(persian?"فیلد متنی فعالی نیست":"No active text field");return;}
        try{
            ic.beginBatchEdit();

            // Preferred path: let the target editor select its complete contents.
            boolean selectedAll=false;
            try{selectedAll=ic.performContextMenuAction(android.R.id.selectAll);}catch(Exception ignored){}
            if(selectedAll){
                CharSequence selected=null;
                try{selected=ic.getSelectedText(0);}catch(Exception ignored){}
                if(selected!=null&&selected.length()>0){
                    ic.commitText("",1);
                    ic.finishComposingText();
                    setStatus(persian?"متن پاک شد":"Text cleared");
                    return;
                }
            }

            // Fallback for editors that do not implement Select All correctly.
            try{
                android.view.inputmethod.ExtractedTextRequest req=new android.view.inputmethod.ExtractedTextRequest();
                android.view.inputmethod.ExtractedText et=ic.getExtractedText(req,0);
                if(et!=null&&et.text!=null&&et.text.length()>0){
                    int start=Math.max(0,et.startOffset);
                    int end=start+et.text.length();
                    if(ic.setSelection(start,end)){
                        ic.commitText("",1);
                        ic.finishComposingText();
                        setStatus(persian?"متن پاک شد":"Text cleared");
                        return;
                    }
                }
            }catch(Exception ignored){}

            // Last-resort cursor-relative deletion for minimal InputConnection implementations.
            CharSequence selected=null;
            try{selected=ic.getSelectedText(0);}catch(Exception ignored){}
            if(selected!=null&&selected.length()>0)ic.commitText("",1);
            CharSequence before=null,after=null;
            try{before=ic.getTextBeforeCursor(65536,0);}catch(Exception ignored){}
            try{after=ic.getTextAfterCursor(65536,0);}catch(Exception ignored){}
            int beforeCount=before==null?0:before.length();
            int afterCount=after==null?0:after.length();
            if(beforeCount>0||afterCount>0)ic.deleteSurroundingText(beforeCount,afterCount);
            ic.finishComposingText();
            setStatus(persian?"متن پاک شد":"Text cleared");
        }catch(Exception e){
            setStatus(persian?"پاک کردن متن ممکن نشد":"Unable to clear text");
        }finally{
            try{ic.endBatchEdit();}catch(Exception ignored){}
        }
    }
''',
    'replace Gboard switch implementation with clear-current-field action',
)

# Remove imports/constants that were only needed by the deleted keyboard-switch path.
replace_once('import android.view.inputmethod.InputMethodInfo;\n', '', 'remove InputMethodInfo import')
replace_once('import android.view.inputmethod.InputMethodManager;\n', '', 'remove InputMethodManager import')
replace_once('    private static final String GBOARD_PACKAGE = "com.google.android.inputmethod.latin";\n', '', 'remove Gboard package constant')

if 'versionCode 24' not in g or "versionName '1.14'" not in g:
    raise SystemExit('v1.15 patch: expected v1.14 version markers missing')
g = g.replace('versionCode 24', 'versionCode 25', 1)
g = g.replace("versionName '1.14'", "versionName '1.15'", 1)

required = [
    'Button clearField = toolbarButton("×", v -> clearCurrentTextField());',
    'clearField.setContentDescription("Clear text field");',
    'private void clearCurrentTextField(){',
    'performContextMenuAction(android.R.id.selectAll)',
    'android.view.inputmethod.ExtractedTextRequest',
    'getTextBeforeCursor(65536,0)',
    'getTextAfterCursor(65536,0)',
    'hasComposingTail=false;\n        updateMicUi(); setStatus(readyText());',
    'int desired = Math.round(v112Width * 0.70f);',
    'moveFloatingKeyboard(dragStartLeft + dx, dragStartTop + dy);',
    'return collapsed || getResources().getConfiguration().orientation == Configuration.ORIENTATION_LANDSCAPE;',
    'enable_endpoint_detection",false',
    'language_hints_strict",true',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.15 patch: required invariant missing: {needle}')

for forbidden in [
    'toolbarButton("G", v -> switchToGboard())',
    'Switch to Gboard',
    'private void switchToGboard(){',
    'GBOARD_PACKAGE',
    'InputMethodInfo',
    'InputMethodManager',
    'setCollapsed(false); updateMicUi(); setStatus(readyText());',
    'MAX_CAPTURE_MS',
    'Floating mode: next build',
]:
    if forbidden in s:
        raise SystemExit(f'v1.15 patch: forbidden old behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.15 clear-current-field toolbar patch')
