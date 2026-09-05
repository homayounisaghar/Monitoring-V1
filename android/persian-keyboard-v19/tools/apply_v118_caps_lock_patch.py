from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.18 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# Keep one-shot Shift behavior, and add a distinct Caps Lock state activated by
# long-pressing Shift. A normal tap while Caps Lock is active turns it off.
replace_once(
    '    private boolean shift;\n',
    '    private boolean shift;\n    private boolean capsLock;\n',
    'capsLock state',
)

replace_once(
'''        shift = false;
        int klass = attribute == null ? InputType.TYPE_CLASS_TEXT : (attribute.inputType & InputType.TYPE_MASK_CLASS);
''',
'''        shift = false;
        capsLock = false;
        int klass = attribute == null ? InputType.TYPE_CLASS_TEXT : (attribute.inputType & InputType.TYPE_MASK_CLASS);
''',
    'reset Caps Lock for a new editor',
)

replace_once(
'''        LinearLayout r4 = newKeyRow();
        r4.addView(actionKey(shift ? "⇧●" : "⇧", v -> { shift = !shift; render(); }), keyLp(1.35f));
        for (String s : cased(new String[]{"z","x","c","v","b","n","m"})) r4.addView(charKey(s), keyLp(1f));
''',
'''        LinearLayout r4 = newKeyRow();
        Button shiftKey = actionKey(capsLock ? "⇪" : (shift ? "⇧●" : "⇧"), v -> {
            if(capsLock){capsLock=false; shift=false;}
            else shift=!shift;
            render();
        });
        shiftKey.setContentDescription(capsLock ? "Caps Lock on" : "Shift; long press for Caps Lock");
        shiftKey.setOnLongClickListener(v -> {
            stopVoiceForManualInput();
            capsLock=true;
            shift=true;
            render();
            return true;
        });
        r4.addView(shiftKey, keyLp(1.35f));
        for (String s : cased(new String[]{"z","x","c","v","b","n","m"})) r4.addView(charKey(s), keyLp(1f));
''',
    'long-press Shift Caps Lock behavior',
)

replace_once(
'''        persian=!persian; shift=false; layer=Layer.ALPHA; getSharedPreferences("keyboard",MODE_PRIVATE).edit().putBoolean("persian",persian).apply(); render(); setStatus(readyText());
''',
'''        persian=!persian; shift=false; capsLock=false; layer=Layer.ALPHA; getSharedPreferences("keyboard",MODE_PRIVATE).edit().putBoolean("persian",persian).apply(); render(); setStatus(readyText());
''',
    'clear Caps Lock on language switch',
)

replace_once(
'''        InputConnection ic=getCurrentInputConnection(); if(ic==null)return; try{ic.commitText(t,1); if(!persian&&shift&&t.length()==1&&Character.isLetter(t.charAt(0))){shift=false;render();}}catch(Exception ignored){}
''',
'''        InputConnection ic=getCurrentInputConnection(); if(ic==null)return; try{ic.commitText(t,1); if(!persian&&shift&&!capsLock&&t.length()==1&&Character.isLetter(t.charAt(0))){shift=false;render();}}catch(Exception ignored){}
''',
    'preserve Shift while Caps Lock is active',
)

if 'versionCode 27' not in g or "versionName '1.17'" not in g:
    raise SystemExit('v1.18 patch: expected v1.17 version markers missing')
g = g.replace('versionCode 27', 'versionCode 28', 1)
g = g.replace("versionName '1.17'", "versionName '1.18'", 1)

required = [
    'private boolean capsLock;',
    'Button shiftKey = actionKey(capsLock ? "⇪" : (shift ? "⇧●" : "⇧")',
    'shiftKey.setOnLongClickListener(v -> {',
    'capsLock=true;',
    'if(capsLock){capsLock=false; shift=false;}',
    'if(!persian&&shift&&!capsLock&&t.length()==1&&Character.isLetter(t.charAt(0)))',
    'persian=!persian; shift=false; capsLock=false; layer=Layer.ALPHA;',
    'Button copy = toolbarButton("⧉", v -> copyCurrentText());',
    'String label=running?"🎙 "+badge():"🎙";',
    'compactMic.setText("🎙 "+badge());',
    'Button clearField = toolbarButton("×", v -> clearCurrentTextField());',
    'int desired = Math.round(v112Width * 0.70f);',
    'moveFloatingKeyboard(dragStartLeft + dx, dragStartTop + dy);',
    'enable_endpoint_detection",false',
    'language_hints_strict",true',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.18 patch: required invariant missing: {needle}')

for forbidden in [
    'r4.addView(actionKey(shift ? "⇧●" : "⇧", v -> { shift = !shift; render(); })',
    'if(!persian&&shift&&t.length()==1&&Character.isLetter(t.charAt(0)))',
    'Button copy = toolbarButton("Copy", v -> copyCurrentText());',
    'mic = toolbarButton("🎤", v -> toggleVoice());',
    'compactMic = smallButton("🎤 " + badge(), v -> toggleVoice());',
    'String label=running?"🎙 "+badge():"🎤";',
    'toolbarButton("G⇄"',
    'Translate: next build',
    'toolbarButton("G", v -> switchToGboard())',
    'private void switchToGboard(){',
    'setCollapsed(false); updateMicUi(); setStatus(readyText());',
    'MAX_CAPTURE_MS',
    'Floating mode: next build',
]:
    if forbidden in s:
        raise SystemExit(f'v1.18 patch: forbidden old behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.18 long-press Shift Caps Lock patch')
