from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.16 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# Replace the unused Translate toolbar action beside Paste with a practical Copy
# action. Copy selected text when there is a selection; otherwise copy the entire
# currently focused text field. Existing Paste, clear-field, floating and speech
# behavior are intentionally unchanged.
replace_once(
'''        Button translate = toolbarButton("G⇄", v -> { stopVoiceForManualInput(); setStatus("Translate: next build"); });
        translate.setContentDescription("Translate");
        left.addView(translate, toolbarLp(1f));
''',
'''        Button copy = toolbarButton("Copy", v -> copyCurrentText());
        copy.setContentDescription("Copy selected text or entire field");
        left.addView(copy, toolbarLp(1f));
''',
    'replace Translate toolbar button with Copy button',
)

replace_once(
'''    private void pasteClipboard(){
        try{ClipboardManager cm=(ClipboardManager)getSystemService(Context.CLIPBOARD_SERVICE); if(cm==null||!cm.hasPrimaryClip()){setStatus("Clipboard is empty");return;} ClipData d=cm.getPrimaryClip(); if(d==null||d.getItemCount()==0)return; CharSequence t=d.getItemAt(0).coerceToText(this); if(t!=null){commitText(t.toString());setStatus("Clipboard pasted");}}catch(Exception e){setStatus("Clipboard unavailable");}
    }
''',
'''    private void copyCurrentText(){
        stopVoiceForManualInput();
        InputConnection ic=getCurrentInputConnection();
        if(ic==null){setStatus(persian?"فیلد متنی فعالی نیست":"No active text field");return;}
        try{
            CharSequence toCopy=null;
            try{
                CharSequence selected=ic.getSelectedText(0);
                if(selected!=null&&selected.length()>0)toCopy=selected;
            }catch(Exception ignored){}
            if(toCopy==null||toCopy.length()==0){
                try{
                    android.view.inputmethod.ExtractedTextRequest req=new android.view.inputmethod.ExtractedTextRequest();
                    android.view.inputmethod.ExtractedText et=ic.getExtractedText(req,0);
                    if(et!=null&&et.text!=null)toCopy=et.text;
                }catch(Exception ignored){}
            }
            if(toCopy==null){
                CharSequence before=null,after=null;
                try{before=ic.getTextBeforeCursor(65536,0);}catch(Exception ignored){}
                try{after=ic.getTextAfterCursor(65536,0);}catch(Exception ignored){}
                StringBuilder all=new StringBuilder();
                if(before!=null)all.append(before);
                if(after!=null)all.append(after);
                toCopy=all.toString();
            }
            ClipboardManager cm=(ClipboardManager)getSystemService(Context.CLIPBOARD_SERVICE);
            if(cm==null){setStatus(persian?"کلیپ‌بورد در دسترس نیست":"Clipboard unavailable");return;}
            cm.setPrimaryClip(ClipData.newPlainText("Persian keyboard copy",toCopy==null?"":toCopy));
            setStatus(persian?"کپی شد":"Copied");
        }catch(Exception e){
            setStatus(persian?"کپی ممکن نشد":"Unable to copy");
        }
    }

    private void pasteClipboard(){
        try{ClipboardManager cm=(ClipboardManager)getSystemService(Context.CLIPBOARD_SERVICE); if(cm==null||!cm.hasPrimaryClip()){setStatus("Clipboard is empty");return;} ClipData d=cm.getPrimaryClip(); if(d==null||d.getItemCount()==0)return; CharSequence t=d.getItemAt(0).coerceToText(this); if(t!=null){commitText(t.toString());setStatus("Clipboard pasted");}}catch(Exception e){setStatus("Clipboard unavailable");}
    }
''',
    'add copy-current-text helper before existing paste helper',
)

if 'versionCode 25' not in g or "versionName '1.15'" not in g:
    raise SystemExit('v1.16 patch: expected v1.15 version markers missing')
g = g.replace('versionCode 25', 'versionCode 26', 1)
g = g.replace("versionName '1.15'", "versionName '1.16'", 1)

required = [
    'Button copy = toolbarButton("Copy", v -> copyCurrentText());',
    'copy.setContentDescription("Copy selected text or entire field");',
    'private void copyCurrentText(){',
    'CharSequence selected=ic.getSelectedText(0);',
    'android.view.inputmethod.ExtractedTextRequest',
    'getTextBeforeCursor(65536,0)',
    'getTextAfterCursor(65536,0)',
    'cm.setPrimaryClip(ClipData.newPlainText("Persian keyboard copy",toCopy==null?"":toCopy));',
    'Button clearField = toolbarButton("×", v -> clearCurrentTextField());',
    'private void clearCurrentTextField(){',
    'int desired = Math.round(v112Width * 0.70f);',
    'moveFloatingKeyboard(dragStartLeft + dx, dragStartTop + dy);',
    'hasComposingTail=false;\n        updateMicUi(); setStatus(readyText());',
    'enable_endpoint_detection",false',
    'language_hints_strict",true',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.16 patch: required invariant missing: {needle}')

for forbidden in [
    'toolbarButton("G⇄"',
    'Translate: next build',
    'setContentDescription("Translate")',
    'toolbarButton("G", v -> switchToGboard())',
    'Switch to Gboard',
    'private void switchToGboard(){',
    'setCollapsed(false); updateMicUi(); setStatus(readyText());',
    'MAX_CAPTURE_MS',
    'Floating mode: next build',
]:
    if forbidden in s:
        raise SystemExit(f'v1.16 patch: forbidden old behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.16 Copy-toolbar patch')
