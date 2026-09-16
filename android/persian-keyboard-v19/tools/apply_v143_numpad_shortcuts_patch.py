from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
setup = Path('app/src/main/java/com/najme/perplexityprobe/KeyboardSetupActivity.java')
gradle_file = Path('app/build.gradle')

s = service.read_text()
a = setup.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.43 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


def replace_region(text, start_marker, end_marker, replacement, label):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f'v1.43 patch: missing start marker: {label}')
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f'v1.43 patch: missing end marker: {label}')
    return text[:start] + replacement + text[end:]


# v1.43 is a UI/productivity-only layer over the v1.42 speech/session architecture.
# User-provided shortcut contents are intentionally NOT embedded in public source.
# Only editable labels have harmless defaults; contents live in app-private prefs.
s = rep(s,
'''    private enum Layer { ALPHA, SYMBOL1, SYMBOL2, NUMPAD }\n''',
'''    private enum Layer { ALPHA, SYMBOL1, SYMBOL2, NUMPAD }\n    private static final String SHORTCUT_PREFS="numpad_shortcuts";\n    private static final String SHORTCUT_LABEL_PREFIX="label_";\n    private static final String SHORTCUT_VALUE_PREFIX="value_";\n    private static final String[] SHORTCUT_DEFAULT_LABELS={"UN","PW","PN","S4"};\n''',
    'shortcut preference constants')

numpad = r'''    private String shortcutLabel(int slot){
        if(slot<0||slot>=SHORTCUT_DEFAULT_LABELS.length)return "S?";
        String value=getSharedPreferences(SHORTCUT_PREFS,MODE_PRIVATE)
                .getString(SHORTCUT_LABEL_PREFIX+slot,SHORTCUT_DEFAULT_LABELS[slot]);
        if(value==null)value="";
        value=value.trim();
        return value.isEmpty()?SHORTCUT_DEFAULT_LABELS[slot]:value;
    }

    private String shortcutValue(int slot){
        if(slot<0||slot>=SHORTCUT_DEFAULT_LABELS.length)return "";
        String value=getSharedPreferences(SHORTCUT_PREFS,MODE_PRIVATE)
                .getString(SHORTCUT_VALUE_PREFIX+slot,"");
        return value==null?"":value;
    }

    private void insertNumpadShortcut(int slot){
        stopVoiceForManualInput();
        String value=shortcutValue(slot);
        if(value.isEmpty()){
            setStatus(persian?"میانبر خالی است — برای تنظیم نگه دارید":"Shortcut empty — long press to configure");
            return;
        }
        commitText(value);
    }

    private void openNumpadShortcutSetup(int slot){
        stopVoiceForManualInput();
        try{
            android.content.Intent intent=new android.content.Intent(this,KeyboardSetupActivity.class);
            intent.addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK);
            intent.putExtra("shortcut_slot",slot);
            startActivity(intent);
        }catch(Exception e){
            setStatus(persian?"باز کردن تنظیم میانبر ممکن نشد":"Unable to open shortcut setup");
        }
    }

    private Button shortcutKey(int slot){
        Button b=actionKey(shortcutLabel(slot),v -> insertNumpadShortcut(slot));
        b.setTextSize(isLandscape()?10.5f:12.5f);
        b.setContentDescription("Numpad shortcut "+(slot+1)+"; long press to edit");
        b.setOnLongClickListener(v -> {openNumpadShortcutSetup(slot);return true;});
        return b;
    }

    private void addNumpadDigitRow(int shortcutSlot,String[] labels){
        LinearLayout r=newKeyRow();
        r.addView(shortcutKey(shortcutSlot),keyLp(1.2f));
        for(String label:labels)r.addView(charKey(label),keyLp(2f));
        spacer(r,1.2f);
        rows.addView(r);
    }

    private void numpadBackspace(){
        stopVoiceForManualInput();
        InputConnection ic=getCurrentInputConnection();
        if(ic==null)return;
        try{
            CharSequence sel=ic.getSelectedText(0);
            if(sel!=null&&sel.length()>0)ic.commitText("",1);
            else ic.deleteSurroundingText(1,0);
        }catch(Exception ignored){}
    }

    private void renderNumpad() {
        LinearLayout ops = newKeyRow();
        for (String op : new String[]{"+","−","×","*","÷","%","="}) ops.addView(charKey(op), keyLp(1f));
        rows.addView(ops);

        addNumpadDigitRow(0,new String[]{"1","2","3"});
        addNumpadDigitRow(1,new String[]{"4","5","6"});
        addNumpadDigitRow(2,new String[]{"7","8","9"});

        LinearLayout last = newKeyRow();
        last.addView(shortcutKey(3), keyLp(1.05f));
        last.addView(actionKey(alphaLabel(), v -> { layer=Layer.ALPHA; render(); }), keyLp(1.1f));
        last.addView(charKey("0"), keyLp(1.7f));
        last.addView(charKey("."), keyLp(0.85f));
        last.addView(actionKey("⌫", v -> numpadBackspace()), keyLp(1.05f));
        last.addView(actionKey("↵", v -> enter()), keyLp(1.05f));
        rows.addView(last);
    }

'''
s = replace_region(s, '    private void renderNumpad() {', '    private void addRow(String[] labels)',
                   numpad, 'editable numpad shortcuts and math operator row')

# Setup Activity owns repeated editing. Long-pressing a shortcut launches this
# activity directly into the selected slot; normal setup also exposes a chooser.
a = rep(a,
'''import android.app.Activity;\n''',
'''import android.app.Activity;\nimport android.app.AlertDialog;\n''',
    'AlertDialog import')
a = rep(a,
'''import android.widget.Button;\n''',
'''import android.widget.Button;\nimport android.widget.EditText;\n''',
    'EditText import')
a = rep(a,
'''    private static final int REQ_MIC = 71;\n''',
'''    private static final int REQ_MIC = 71;\n    private static final String SHORTCUT_PREFS="numpad_shortcuts";\n    private static final String SHORTCUT_LABEL_PREFIX="label_";\n    private static final String SHORTCUT_VALUE_PREFIX="value_";\n    private static final String[] SHORTCUT_DEFAULT_LABELS={"UN","PW","PN","S4"};\n''',
    'setup shortcut constants')

a = rep(a,
'''        webView.loadUrl(START_URL);\n    }\n''',
'''        webView.loadUrl(START_URL);\n        int shortcutSlot=getIntent()==null?-1:getIntent().getIntExtra("shortcut_slot",-1);\n        if(shortcutSlot>=0&&shortcutSlot<SHORTCUT_DEFAULT_LABELS.length)\n            webView.post(()->showShortcutEditor(shortcutSlot));\n    }\n''',
    'open requested shortcut editor after long press')

a = rep(a,
'''        root.addView(choose, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(56)));\n\n        status = new TextView(this);\n''',
'''        root.addView(choose, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(56)));\n\n        Button shortcuts = new Button(this);\n        shortcuts.setText("تنظیم میانبرهای صفحه اعداد");\n        shortcuts.setAllCaps(false);\n        shortcuts.setTextSize(14f);\n        shortcuts.setOnClickListener(v -> showShortcutChooser());\n        root.addView(shortcuts, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(52)));\n\n        status = new TextView(this);\n''',
    'shortcut setup entry button')

shortcut_setup_methods = r'''    private String shortcutLabel(int slot) {
        String value=getSharedPreferences(SHORTCUT_PREFS,MODE_PRIVATE)
                .getString(SHORTCUT_LABEL_PREFIX+slot,SHORTCUT_DEFAULT_LABELS[slot]);
        if(value==null)value="";
        value=value.trim();
        return value.isEmpty()?SHORTCUT_DEFAULT_LABELS[slot]:value;
    }

    private void showShortcutChooser() {
        String[] labels=new String[SHORTCUT_DEFAULT_LABELS.length];
        for(int i=0;i<labels.length;i++)labels[i]=(i+1)+" — "+shortcutLabel(i);
        new AlertDialog.Builder(this)
                .setTitle("میانبرهای صفحه اعداد")
                .setItems(labels,(dialog,which)->showShortcutEditor(which))
                .setNegativeButton("بستن",null)
                .show();
    }

    private void showShortcutEditor(int slot) {
        if(slot<0||slot>=SHORTCUT_DEFAULT_LABELS.length)return;
        LinearLayout box=new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(20),dp(8),dp(20),0);

        TextView labelHint=new TextView(this);
        labelHint.setText("نام دکمه");
        box.addView(labelHint);

        EditText label=new EditText(this);
        label.setSingleLine(true);
        label.setText(shortcutLabel(slot));
        label.setSelectAllOnFocus(true);
        box.addView(label,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT));

        TextView valueHint=new TextView(this);
        valueHint.setText("متنی که با لمس کوتاه درج می‌شود");
        valueHint.setPadding(0,dp(8),0,0);
        box.addView(valueHint);

        EditText value=new EditText(this);
        value.setSingleLine(false);
        value.setMinLines(1);
        value.setMaxLines(4);
        String current=getSharedPreferences(SHORTCUT_PREFS,MODE_PRIVATE)
                .getString(SHORTCUT_VALUE_PREFIX+slot,"");
        value.setText(current==null?"":current);
        value.setSelectAllOnFocus(true);
        box.addView(value,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT));

        AlertDialog dialog=new AlertDialog.Builder(this)
                .setTitle("Shortcut "+(slot+1))
                .setView(box)
                .setPositiveButton("ذخیره",(d,which)->{
                    String newLabel=label.getText()==null?"":label.getText().toString().trim();
                    if(newLabel.isEmpty())newLabel=SHORTCUT_DEFAULT_LABELS[slot];
                    String newValue=value.getText()==null?"":value.getText().toString();
                    getSharedPreferences(SHORTCUT_PREFS,MODE_PRIVATE).edit()
                            .putString(SHORTCUT_LABEL_PREFIX+slot,newLabel)
                            .putString(SHORTCUT_VALUE_PREFIX+slot,newValue)
                            .apply();
                    status.setText("میانبر "+newLabel+" ذخیره شد.");
                })
                .setNegativeButton("لغو",null)
                .create();
        dialog.setOnShowListener(ignored->value.requestFocus());
        dialog.show();
    }

'''
request_marker = '    private void requestMicIfNeeded() {'
if request_marker not in a:
    raise SystemExit('v1.43 patch: requestMicIfNeeded marker missing')
a = a.replace(request_marker, shortcut_setup_methods + request_marker, 1)

if 'versionCode 52' not in g or "versionName '1.42'" not in g:
    raise SystemExit('v1.43 patch: expected v1.42 Gradle markers missing')
g = g.replace('versionCode 52','versionCode 53',1)
g = g.replace("versionName '1.42'","versionName '1.43'",1)

text=s+'\n'+a+'\n'+g
required=[
    'private static final String SHORTCUT_PREFS="numpad_shortcuts";',
    'private static final String[] SHORTCUT_DEFAULT_LABELS={"UN","PW","PN","S4"};',
    'private Button shortcutKey(int slot){',
    'b.setOnLongClickListener(v -> {openNumpadShortcutSetup(slot);return true;});',
    'intent.putExtra("shortcut_slot",slot);',
    'new String[]{"+","−","×","*","÷","%","="}',
    'addNumpadDigitRow(0,new String[]{"1","2","3"});',
    'addNumpadDigitRow(1,new String[]{"4","5","6"});',
    'addNumpadDigitRow(2,new String[]{"7","8","9"});',
    'last.addView(shortcutKey(3)',
    'private void numpadBackspace(){',
    'stopVoiceForManualInput();',
    'else ic.deleteSurroundingText(1,0);',
    'private void showShortcutChooser()',
    'private void showShortcutEditor(int slot)',
    '.putString(SHORTCUT_LABEL_PREFIX+slot,newLabel)',
    '.putString(SHORTCUT_VALUE_PREFIX+slot,newValue)',
    'versionCode 53',
    "versionName '1.43'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.43 patch: required invariant missing: {needle}')

# Shortcut contents must remain device-local, never source defaults.
if 'SHORTCUT_DEFAULT_VALUES' in text:
    raise SystemExit('v1.43 patch: shortcut content defaults must not be embedded')

service.write_text(s)
setup.write_text(a)
gradle_file.write_text(g)
print('Applied v1.43 editable numpad shortcuts + math operator row patch')
