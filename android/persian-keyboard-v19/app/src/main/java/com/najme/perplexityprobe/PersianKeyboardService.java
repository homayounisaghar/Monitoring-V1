package com.najme.perplexityprobe;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.inputmethodservice.InputMethodService;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import android.text.InputType;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputConnection;
import android.view.inputmethod.InputMethodInfo;
import android.view.inputmethod.InputMethodManager;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.PopupWindow;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.WebSocket;
import okhttp3.WebSocketListener;
import okio.ByteString;

/**
 * Compact daily-use prototype. The speech path is the validated native AudioRecord ->
 * temporary Perplexity-session Soniox credential -> Soniox realtime path.
 */
public class PersianKeyboardService extends InputMethodService {
    private static final String START_URL = "https://www.perplexity.ai/";
    private static final String SONIOX_WS = "wss://stt-rt.soniox.com/transcribe-websocket";
    private static final String GBOARD_PACKAGE = "com.google.android.inputmethod.latin";
    private static final int SAMPLE_RATE = 16000;
    private static final int AUDIO_CHUNK = 3200;
    private static final int PREBUFFER_MAX = SAMPLE_RATE * 2 * 20;
    private static final long CREDENTIAL_TIMEOUT_MS = 18000L;
    private static final long FINISH_TIMEOUT_MS = 10000L;
    private static final long MAX_CAPTURE_MS = 60000L;

    private static final int BG = 0xFFE5E5E9;
    private static final int KEY = 0xFFF9F9FB;
    private static final int ACTION = 0xFFD8E3FA;
    private static final int TEXT = 0xFF3F4248;
    private static final int MIC_ACTIVE = 0xFF5D6A86;

    private static final String MOBILE_BROWSER_UA =
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 " +
            "(KHTML, like Gecko) SamsungBrowser/30.0 Chrome/143.0.0.0 Mobile Safari/537.36";

    private enum Layer { ALPHA, SYMBOL1, SYMBOL2, NUMPAD }

    private final Handler main = new Handler(Looper.getMainLooper());
    private final OkHttpClient http = new OkHttpClient.Builder().readTimeout(0, TimeUnit.MILLISECONDS).build();
    private final Object textLock = new Object();
    private final Object audioLock = new Object();
    private final StringBuilder finalTranscript = new StringBuilder();
    private final Set<String> finalTokenIds = new HashSet<>();
    private final ArrayDeque<byte[]> pendingAudio = new ArrayDeque<>();
    private final Map<String, String[]> longPress = new HashMap<>();

    private LinearLayout root;
    private LinearLayout full;
    private LinearLayout rows;
    private LinearLayout compact;
    private TextView status;
    private TextView compactStatus;
    private Button mic;
    private Button collapse;
    private Button compactMic;
    private WebView auth;
    private EditorInfo editorInfo;

    private boolean persian = true;
    private boolean shift;
    private boolean collapsed;
    private Layer layer = Layer.ALPHA;

    private volatile boolean pageReady;
    private volatile boolean running;
    private volatile boolean stopRequested;
    private volatile boolean awaitingCredential;
    private volatile boolean completed;
    private volatile boolean sonioxReady;
    private volatile boolean audioDone;
    private volatile boolean finishSent;

    private long inputGeneration;
    private long activeGeneration = -1;
    private InputConnection boundConnection;
    private WebSocket webSocket;
    private AudioRecord audioRecord;
    private String partialTranscript = "";
    private int pendingBytes;
    private int credentialAttempt;
    private boolean retryAfterPageLoad;
    private String lastCredentialError = "";

    @Override public void onCreate() {
        super.onCreate();
        initLongPress();
        persian = getSharedPreferences("keyboard", MODE_PRIVATE).getBoolean("persian", true);
    }

    @Override public View onCreateInputView() {
        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(3), dp(2), dp(3), dp(3));
        root.setBackgroundColor(BG);

        full = new LinearLayout(this);
        full.setOrientation(LinearLayout.VERTICAL);
        root.addView(full, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        buildToolbar();
        status = new TextView(this);
        status.setText(pageReady ? readyText() : "Loading session…");
        status.setTextColor(0xFF6D7078);
        status.setTextSize(9.5f);
        status.setGravity(Gravity.CENTER);
        full.addView(status, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(14)));

        rows = new LinearLayout(this);
        rows.setOrientation(LinearLayout.VERTICAL);
        full.addView(rows, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        buildCompact();

        auth = new WebView(this);
        auth.setAlpha(0.01f);
        root.addView(auth, new LinearLayout.LayoutParams(1, 1));
        configureWebView();
        auth.loadUrl(START_URL);

        render();
        updateMicUi();
        return root;
    }

    private void buildToolbar() {
        LinearLayout bar = new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setGravity(Gravity.CENTER_VERTICAL);
        bar.setPadding(dp(3), 0, dp(3), dp(1));

        mic = toolbarButton("🎤", v -> toggleVoice());
        bar.addView(mic, toolbarLp(1f));
        collapse = toolbarButton("⇊", v -> setCollapsed(true));
        collapse.setVisibility(View.INVISIBLE);
        bar.addView(collapse, toolbarLp(0.68f));
        bar.addView(toolbarButton("G⇄", v -> setStatus("Translate: next build")), toolbarLp(0.85f));
        Button clip = toolbarButton("▣", v -> pasteClipboard());
        clip.setContentDescription("Clipboard");
        bar.addView(clip, toolbarLp(0.72f));
        Button floating = toolbarButton("▱", v -> setStatus("Floating mode: next build"));
        floating.setContentDescription("Floating mode");
        bar.addView(floating, toolbarLp(0.72f));
        Button gboard = toolbarButton("G", v -> switchToGboard());
        gboard.setContentDescription("Switch to Gboard");
        bar.addView(gboard, toolbarLp(0.72f));
        full.addView(bar, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(34)));
    }

    private void buildCompact() {
        compact = new LinearLayout(this);
        compact.setOrientation(LinearLayout.HORIZONTAL);
        compact.setGravity(Gravity.CENTER_VERTICAL);
        compact.setPadding(dp(7), dp(3), dp(7), dp(3));
        compact.setVisibility(View.GONE);

        compactMic = smallButton("🎙 " + badge(), v -> toggleVoice());
        compact.addView(compactMic, new LinearLayout.LayoutParams(dp(78), dp(42)));
        Button stop = smallButton("■", v -> requestStop());
        LinearLayout.LayoutParams sp = new LinearLayout.LayoutParams(dp(46), dp(42));
        sp.setMarginStart(dp(4));
        compact.addView(stop, sp);
        compactStatus = new TextView(this);
        compactStatus.setText(listeningText());
        compactStatus.setTextSize(12f);
        compactStatus.setTextColor(TEXT);
        compactStatus.setGravity(Gravity.CENTER);
        compact.addView(compactStatus, new LinearLayout.LayoutParams(0, dp(42), 1f));
        Button restore = smallButton("⌨", v -> setCollapsed(false));
        compact.addView(restore, new LinearLayout.LayoutParams(dp(52), dp(42)));
        root.addView(compact, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(48)));
    }

    private LinearLayout.LayoutParams toolbarLp(float weight) {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(32), weight);
        lp.setMargins(dp(1), 0, dp(1), 0);
        return lp;
    }

    private Button toolbarButton(String label, View.OnClickListener listener) {
        Button b = new Button(this);
        b.setText(label); b.setTextSize(16f); b.setTextColor(TEXT); b.setAllCaps(false);
        b.setPadding(0,0,0,0); b.setMinWidth(0); b.setMinimumWidth(0); b.setMinHeight(0); b.setMinimumHeight(0);
        b.setBackground(round(0x00FFFFFF, dp(15))); b.setOnClickListener(listener);
        return b;
    }

    private Button smallButton(String label, View.OnClickListener listener) {
        Button b = new Button(this);
        b.setText(label); b.setTextSize(14f); b.setTextColor(TEXT); b.setAllCaps(false);
        b.setPadding(0,0,0,0); b.setMinWidth(0); b.setMinimumWidth(0); b.setMinHeight(0); b.setMinimumHeight(0);
        b.setBackground(round(KEY, dp(18))); b.setOnClickListener(listener);
        return b;
    }

    private void setCollapsed(boolean value) {
        if (value && !running) return;
        collapsed = value;
        if (full != null) full.setVisibility(value ? View.GONE : View.VISIBLE);
        if (compact != null) compact.setVisibility(value ? View.VISIBLE : View.GONE);
        if (root != null) root.requestLayout();
    }

    @Override public void onStartInput(EditorInfo attribute, boolean restarting) {
        super.onStartInput(attribute, restarting);
        editorInfo = attribute;
        inputGeneration++;
        if (running) abortForEditorChange();
        shift = false;
        int klass = attribute == null ? InputType.TYPE_CLASS_TEXT : (attribute.inputType & InputType.TYPE_MASK_CLASS);
        layer = (klass == InputType.TYPE_CLASS_NUMBER || klass == InputType.TYPE_CLASS_PHONE) ? Layer.NUMPAD : Layer.ALPHA;
        main.post(this::render);
    }

    @Override public void onStartInputView(EditorInfo info, boolean restarting) {
        super.onStartInputView(info, restarting);
        editorInfo = info;
        main.post(this::render);
    }

    @Override public void onFinishInput() {
        inputGeneration++;
        if (running) abortForEditorChange();
        editorInfo = null;
        super.onFinishInput();
    }

    private void render() {
        if (rows == null) return;
        rows.removeAllViews();
        if (layer == Layer.NUMPAD) renderNumpad();
        else if (layer == Layer.SYMBOL1) renderSymbols1();
        else if (layer == Layer.SYMBOL2) renderSymbols2();
        else if (persian) renderPersian();
        else renderEnglish();
        updateMicUi();
    }

    private void renderPersian() {
        addRow(new String[]{"۱","۲","۳","۴","۵","۶","۷","۸","۹","۰"});
        addRow(new String[]{"ض","ص","ث","ق","ف","غ","ع","ه","خ","ح","ج"});
        addRow(new String[]{"ش","س","ی","ب","ل","ا","ت","ن","م","ک","گ"});
        LinearLayout r4 = newKeyRow();
        for (String s : new String[]{"ظ","ط","ژ","ز","ر","ذ","د","پ","و","چ"}) r4.addView(charKey(s), keyLp(1f));
        r4.addView(actionKey("⌫", v -> backspace()), keyLp(1.15f));
        rows.addView(r4);
        addBottomRow();
    }

    private void renderEnglish() {
        addRow(new String[]{"1","2","3","4","5","6","7","8","9","0"});
        addRow(cased(new String[]{"q","w","e","r","t","y","u","i","o","p"}));
        LinearLayout r3 = newKeyRow();
        spacer(r3, 0.5f);
        for (String s : cased(new String[]{"a","s","d","f","g","h","j","k","l"})) r3.addView(charKey(s), keyLp(1f));
        spacer(r3, 0.5f); rows.addView(r3);
        LinearLayout r4 = newKeyRow();
        r4.addView(actionKey(shift ? "⇧●" : "⇧", v -> { shift = !shift; render(); }), keyLp(1.35f));
        for (String s : cased(new String[]{"z","x","c","v","b","n","m"})) r4.addView(charKey(s), keyLp(1f));
        r4.addView(actionKey("⌫", v -> backspace()), keyLp(1.35f));
        rows.addView(r4);
        addBottomRow();
    }

    private String[] cased(String[] in) {
        if (!shift) return in;
        String[] out = new String[in.length];
        for (int i=0;i<in.length;i++) out[i]=in[i].toUpperCase();
        return out;
    }

    private void addBottomRow() {
        LinearLayout r = newKeyRow();
        r.addView(actionKey(layer == Layer.ALPHA ? (persian ? "؟۳۲۱" : "?123") : alphaLabel(), v -> {
            layer = layer == Layer.ALPHA ? Layer.SYMBOL1 : Layer.ALPHA; render();
        }), keyLp(1.35f));
        r.addView(charKey(persian ? "،" : ","), keyLp(0.82f));
        r.addView(actionKey("◉", v -> toggleLanguage()), keyLp(0.9f));
        Button space = actionKey(persian ? "فارسی" : "English", v -> commitText(" "));
        space.setTextSize(persian ? 15f : 14f); r.addView(space, keyLp(3.7f));
        r.addView(charKey("."), keyLp(0.88f));
        r.addView(actionKey("↵", v -> enter()), keyLp(1.35f));
        rows.addView(r);
    }

    private void renderSymbols1() {
        addRow(persian ? new String[]{"۱","۲","۳","۴","۵","۶","۷","۸","۹","۰"} : new String[]{"1","2","3","4","5","6","7","8","9","0"});
        addRow(new String[]{"@","#","﷼","-","&","_","+","(",")","/"});
        LinearLayout r3 = newKeyRow();
        r3.addView(actionKey("=\\<", v -> { layer=Layer.SYMBOL2; render(); }), keyLp(1.25f));
        for (String s : new String[]{"/","«","»",":","؛","!","؟"}) r3.addView(charKey(s), keyLp(1f));
        r3.addView(actionKey("⌫", v -> backspace()), keyLp(1.25f)); rows.addView(r3);
        addSymbolBottom();
    }

    private void renderSymbols2() {
        addRow(new String[]{"~","`","|","•","√","π","÷","×","§","Δ"});
        addRow(new String[]{"£","¥","$","¢","^","°","=","{","}","\\"});
        LinearLayout r3 = newKeyRow();
        r3.addView(actionKey(persian ? "؟۳۲۱" : "123?", v -> { layer=Layer.SYMBOL1; render(); }), keyLp(1.25f));
        for (String s : new String[]{"%","©","®","™","✓","[","]"}) r3.addView(charKey(s), keyLp(1f));
        r3.addView(actionKey("⌫", v -> backspace()), keyLp(1.25f)); rows.addView(r3);
        addSymbolBottom();
    }

    private void addSymbolBottom() {
        LinearLayout r = newKeyRow();
        r.addView(actionKey(alphaLabel(), v -> { layer=Layer.ALPHA; render(); }), keyLp(1.3f));
        r.addView(charKey(persian ? "،" : ","), keyLp(0.8f));
        r.addView(actionKey("¹²₃₄", v -> { layer=Layer.NUMPAD; render(); }), keyLp(1f));
        r.addView(actionKey(persian ? "فارسی" : "English", v -> commitText(" ")), keyLp(3.7f));
        r.addView(actionKey("↵", v -> enter()), keyLp(1.35f));
        rows.addView(r);
    }

    private void renderNumpad() {
        LinearLayout ops = newKeyRow();
        for (String s : new String[]{"+","−","×","÷","%"}) ops.addView(charKey(s), keyLp(1f));
        rows.addView(ops);
        addLargeRow(new String[]{"1","2","3"}); addLargeRow(new String[]{"4","5","6"}); addLargeRow(new String[]{"7","8","9"});
        LinearLayout last = newKeyRow();
        last.addView(actionKey(alphaLabel(), v -> { layer=Layer.ALPHA; render(); }), keyLp(1.25f));
        last.addView(charKey("0"), keyLp(2f)); last.addView(charKey("."), keyLp(1f));
        last.addView(actionKey("⌫", v -> backspace()), keyLp(1.25f)); last.addView(actionKey("↵", v -> enter()), keyLp(1.25f));
        rows.addView(last);
    }

    private void addRow(String[] labels) {
        LinearLayout r = newKeyRow(); for (String s : labels) r.addView(charKey(s), keyLp(1f)); rows.addView(r);
    }

    private void addLargeRow(String[] labels) {
        LinearLayout r = newKeyRow(); spacer(r,1.2f); for (String s:labels) r.addView(charKey(s), keyLp(2f)); spacer(r,1.2f); rows.addView(r);
    }

    private LinearLayout newKeyRow() {
        LinearLayout r = new LinearLayout(this); r.setOrientation(LinearLayout.HORIZONTAL); r.setGravity(Gravity.CENTER);
        r.setPadding(dp(1),0,dp(1),0); r.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(38)));
        return r;
    }

    private void spacer(LinearLayout r, float weight) { r.addView(new View(this), new LinearLayout.LayoutParams(0, dp(35), weight)); }
    private LinearLayout.LayoutParams keyLp(float weight) {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(35), weight); lp.setMargins(dp(2),dp(1),dp(2),dp(1)); return lp;
    }

    private Button charKey(String label) {
        Button b=baseKey(label,false); b.setOnClickListener(v -> commitText(label));
        String[] vars=longPress.get(label); if (vars!=null) b.setOnLongClickListener(v -> { showVariants(b,vars); return true; });
        return b;
    }

    private Button actionKey(String label, View.OnClickListener listener) { Button b=baseKey(label,true); b.setOnClickListener(listener); return b; }

    private Button baseKey(String label, boolean action) {
        Button b=new Button(this); b.setText(label); b.setAllCaps(false); b.setTextColor(TEXT);
        b.setTextSize(persian && containsPersian(label) ? 18f : 17f); b.setGravity(Gravity.CENTER); b.setPadding(0,0,0,0);
        b.setMinWidth(0); b.setMinimumWidth(0); b.setMinHeight(0); b.setMinimumHeight(0);
        b.setTypeface(Typeface.create("sans-serif",Typeface.NORMAL)); b.setBackground(round(action?ACTION:KEY,dp(8))); return b;
    }

    private boolean containsPersian(String s) {
        if (s==null) return false; for (int i=0;i<s.length();i++) { char c=s.charAt(i); if(c>='\u0600'&&c<='\u06FF') return true; } return false;
    }

    private void showVariants(View anchor, String[] vars) {
        LinearLayout box=new LinearLayout(this); box.setOrientation(LinearLayout.HORIZONTAL); box.setGravity(Gravity.CENTER);
        box.setPadding(dp(5),dp(3),dp(5),dp(3)); box.setBackground(round(KEY,dp(18)));
        PopupWindow popup=new PopupWindow(box,ViewGroup.LayoutParams.WRAP_CONTENT,dp(52),true); popup.setOutsideTouchable(true); popup.setElevation(dp(8));
        for(String v:vars){ Button b=baseKey(v,false); b.setBackgroundColor(Color.TRANSPARENT); b.setTextSize(18f); b.setOnClickListener(x->{commitText(v);popup.dismiss();}); box.addView(b,new LinearLayout.LayoutParams(dp(48),dp(44))); }
        popup.showAsDropDown(anchor,-dp(36),-dp(100));
    }

    private void initLongPress() {
        longPress.put("ا",new String[]{"آ","أ","إ","ٱ","ء"}); longPress.put("ی",new String[]{"ئ","ي","ى"});
        longPress.put("و",new String[]{"ؤ"}); longPress.put("ه",new String[]{"ۀ","ة"}); longPress.put("ک",new String[]{"ك"});
        longPress.put(".",new String[]{"…",":","؛","!","؟"}); longPress.put("،",new String[]{"؛",":","!","؟"});
        longPress.put("a",new String[]{"á","à","â","ä","ã","å"}); longPress.put("e",new String[]{"é","è","ê","ë"});
        longPress.put("i",new String[]{"í","ì","î","ï"}); longPress.put("o",new String[]{"ó","ò","ô","ö","õ"}); longPress.put("u",new String[]{"ú","ù","û","ü"});
    }

    private String alphaLabel(){return persian?"ابپ":"ABC";}
    private void toggleLanguage(){
        if(running){setStatus("Stop voice before changing language");return;}
        persian=!persian; shift=false; layer=Layer.ALPHA; getSharedPreferences("keyboard",MODE_PRIVATE).edit().putBoolean("persian",persian).apply(); render(); setStatus(readyText());
    }

    private void commitText(String t){
        InputConnection ic=getCurrentInputConnection(); if(ic==null)return; try{ic.commitText(t,1); if(!persian&&shift&&t.length()==1&&Character.isLetter(t.charAt(0))){shift=false;render();}}catch(Exception ignored){}
    }
    private void backspace(){
        InputConnection ic=getCurrentInputConnection(); if(ic==null)return; try{CharSequence sel=ic.getSelectedText(0); if(sel!=null&&sel.length()>0)ic.commitText("",1); else ic.deleteSurroundingText(1,0);}catch(Exception ignored){}
    }
    private void enter(){
        InputConnection ic=getCurrentInputConnection(); if(ic==null)return; int action=editorInfo==null?EditorInfo.IME_ACTION_NONE:(editorInfo.imeOptions&EditorInfo.IME_MASK_ACTION);
        try{if(action!=EditorInfo.IME_ACTION_NONE&&action!=EditorInfo.IME_ACTION_UNSPECIFIED&&ic.performEditorAction(action))return; ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_DOWN,KeyEvent.KEYCODE_ENTER)); ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_UP,KeyEvent.KEYCODE_ENTER));}catch(Exception ignored){}
    }
    private void pasteClipboard(){
        try{ClipboardManager cm=(ClipboardManager)getSystemService(Context.CLIPBOARD_SERVICE); if(cm==null||!cm.hasPrimaryClip()){setStatus("Clipboard is empty");return;} ClipData d=cm.getPrimaryClip(); if(d==null||d.getItemCount()==0)return; CharSequence t=d.getItemAt(0).coerceToText(this); if(t!=null){commitText(t.toString());setStatus("Clipboard pasted");}}catch(Exception e){setStatus("Clipboard unavailable");}
    }

    private void toggleVoice(){if(running)requestStop();else startVoice();}

    private void startVoice(){
        if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED){setStatus("Open the app once and grant microphone permission");return;}
        if(!pageReady){setStatus("Perplexity session not ready — open the app/login once");return;}
        InputConnection ic=getCurrentInputConnection(); if(ic==null){setStatus("No active text field");return;}
        boundConnection=ic; activeGeneration=inputGeneration;
        synchronized(textLock){finalTranscript.setLength(0);finalTokenIds.clear();partialTranscript="";}
        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; updateMicUi();
        setStatus(persian?"در حال ضبط — همین حالا صحبت کنید…":"Recording — speak now…"); startAudioCapture();
        main.postDelayed(()->{if(running&&awaitingCredential){awaitingCredential=false;String d=lastCredentialError.isEmpty()?"timeout":lastCredentialError;failSession("Perplexity credential failed ("+d+")");}},CREDENTIAL_TIMEOUT_MS);
        requestCredential();
    }

    private void requestCredential(){
        if(!running||!awaitingCredential||auth==null)return; credentialAttempt++; try{CookieManager.getInstance().flush();}catch(Exception ignored){} auth.evaluateJavascript(FETCH_CREDENTIAL_JS,null);
    }

    private String safeCredentialError(String e){
        if(e==null||e.trim().isEmpty())return"unknown"; String s=e.replace('\n',' ').replace('\r',' ').trim(); return s.length()>48?s.substring(0,48):s;
    }

    private void requestStop(){if(!running||stopRequested)return;stopRequested=true;setStatus(persian?"در حال نهایی‌سازی…":"Finalizing…");AudioRecord r=audioRecord;if(r!=null)try{r.stop();}catch(Exception ignored){}}

    private boolean sessionStillBound(){return running&&boundConnection!=null&&activeGeneration==inputGeneration&&getCurrentInputConnection()==boundConnection;}

    private void abortForEditorChange(){
        InputConnection old=boundConnection;running=false;stopRequested=true;awaitingCredential=false;stopAudioRecord();clearPending();WebSocket ws=webSocket;webSocket=null;if(ws!=null)ws.cancel();if(old!=null)try{old.finishComposingText();}catch(Exception ignored){} boundConnection=null;
        main.post(()->{setCollapsed(false);updateMicUi();setStatus("Voice cancelled — editor changed");});
    }

    private void switchToGboard(){
        if(running)abortForEditorChange(); InputMethodManager imm=(InputMethodManager)getSystemService(INPUT_METHOD_SERVICE); String id=null;
        if(imm!=null)try{for(InputMethodInfo i:imm.getEnabledInputMethodList())if(GBOARD_PACKAGE.equals(i.getPackageName())){id=i.getId();break;}}catch(Exception ignored){}
        if(id!=null)try{java.lang.reflect.Method m=InputMethodService.class.getMethod("switchInputMethod",String.class);m.invoke(this,id);return;}catch(Exception ignored){}
        try{if(switchToNextInputMethod(false))return;}catch(Exception ignored){} if(imm!=null)try{imm.showInputMethodPicker();}catch(Exception ignored){}
    }

    private void startSoniox(String apiKey){
        if(!sessionStillBound())return; setStatus(persian?"در حال اتصال به سرویس گفتار…":"Connecting speech service…");
        JSONObject c=new JSONObject();put(c,"api_key",apiKey);put(c,"model","stt-rt-v4");put(c,"audio_format","pcm_s16le");put(c,"sample_rate",SAMPLE_RATE);put(c,"num_channels",1);put(c,"enable_endpoint_detection",true);put(c,"max_endpoint_delay_ms",2000);JSONArray h=new JSONArray();h.put(persian?"fa":"en");put(c,"language_hints",h);
        webSocket=http.newWebSocket(new Request.Builder().url(SONIOX_WS).build(),new WebSocketListener(){
            @Override public void onOpen(WebSocket ws,Response response){if(!sessionStillBound()){ws.cancel();return;}webSocket=ws;if(!ws.send(c.toString())){finishWithText("Config send error");return;}boolean ok;synchronized(audioLock){sonioxReady=true;ok=flushLocked(ws);}if(!ok){finishWithText("Audio send error");return;}main.post(()->setStatus(stopRequested?(persian?"در حال نهایی‌سازی…":"Finalizing…"):listeningText()));maybeFinish();}
            @Override public void onMessage(WebSocket ws,String text){handleSoniox(text);}
            @Override public void onClosed(WebSocket ws,int code,String reason){if(running&&!completed)finishWithText("Connection closed");}
            @Override public void onFailure(WebSocket ws,Throwable t,Response response){if(running&&!completed)finishWithText("Connection error");}
        });
    }

    private void startAudioCapture(){
        new Thread(()->{
            try{
                int min=AudioRecord.getMinBufferSize(SAMPLE_RATE,AudioFormat.CHANNEL_IN_MONO,AudioFormat.ENCODING_PCM_16BIT);if(min<=0)throw new IllegalStateException("Invalid audio buffer");
                audioRecord=new AudioRecord(MediaRecorder.AudioSource.VOICE_RECOGNITION,SAMPLE_RATE,AudioFormat.CHANNEL_IN_MONO,AudioFormat.ENCODING_PCM_16BIT,Math.max(min,AUDIO_CHUNK));
                if(audioRecord.getState()!=AudioRecord.STATE_INITIALIZED)throw new IllegalStateException("AudioRecord not initialized");audioRecord.startRecording();byte[] buf=new byte[AUDIO_CHUNK];long deadline=System.currentTimeMillis()+MAX_CAPTURE_MS;
                while(running&&!stopRequested&&System.currentTimeMillis()<deadline){int n;try{n=audioRecord.read(buf,0,buf.length);}catch(Exception e){if(stopRequested||!running)break;throw e;}if(n>0){byte[] chunk=Arrays.copyOf(buf,n);if(!bufferOrSend(chunk))throw new IllegalStateException("Audio send rejected");}else if(n<0&&!stopRequested)throw new IllegalStateException("Audio read failed");}
                if(running&&!stopRequested&&System.currentTimeMillis()>=deadline){stopRequested=true;main.post(()->setStatus(persian?"در حال نهایی‌سازی…":"Finalizing…"));}
                stopAudioRecord();synchronized(audioLock){audioDone=true;}if(running&&!completed)maybeFinish();
            }catch(Exception e){stopAudioRecord();synchronized(audioLock){audioDone=true;}if(running)finishWithText("Audio error");}
        },"persian-keyboard-audio").start();
    }

    private boolean bufferOrSend(byte[] chunk){
        synchronized(audioLock){if(!sonioxReady||webSocket==null){pendingAudio.addLast(chunk);pendingBytes+=chunk.length;while(pendingBytes>PREBUFFER_MAX&&pendingAudio.size()>1){byte[] d=pendingAudio.removeFirst();pendingBytes-=d.length;}return true;}if(!flushLocked(webSocket))return false;return webSocket.send(ByteString.of(chunk,0,chunk.length));}
    }
    private boolean flushLocked(WebSocket ws){while(!pendingAudio.isEmpty()){byte[] c=pendingAudio.removeFirst();pendingBytes-=c.length;if(!ws.send(ByteString.of(c,0,c.length))){pendingAudio.clear();pendingBytes=0;return false;}}pendingBytes=0;return true;}
    private void maybeFinish(){
        WebSocket ws; synchronized(audioLock){if(!running||completed||finishSent||!audioDone||!sonioxReady||webSocket==null)return;if(!flushLocked(webSocket)){ws=null;}else{finishSent=true;ws=webSocket;}}
        if(ws==null){finishWithText("Audio send error");return;}if(!ws.send("")){finishWithText("Finish send error");return;}main.postDelayed(()->{if(running&&!completed)finishWithText("Done (finish ACK timeout)");},FINISH_TIMEOUT_MS);
    }
    private void resetAudio(){synchronized(audioLock){pendingAudio.clear();pendingBytes=0;sonioxReady=false;audioDone=false;finishSent=false;}}
    private void clearPending(){synchronized(audioLock){pendingAudio.clear();pendingBytes=0;sonioxReady=false;}}

    private void handleSoniox(String text){
        try{JSONObject o=new JSONObject(text);if(o.has("error_code")&&!o.isNull("error_code")){finishWithText("Soniox error");return;}JSONArray tokens=o.optJSONArray("tokens");StringBuilder partial=new StringBuilder();if(tokens!=null){synchronized(textLock){for(int i=0;i<tokens.length();i++){JSONObject t=tokens.optJSONObject(i);if(t==null)continue;String tt=t.optString("text","");if(tt.isEmpty()||isControl(tt))continue;if(t.optBoolean("is_final",false)){String id=t.optLong("start_ms",-1)+"|"+t.optLong("end_ms",-1)+"|"+tt;if(finalTokenIds.add(id))finalTranscript.append(tt);}else partial.append(tt);}partialTranscript=partial.toString();}publish(false);}if(o.optBoolean("finished",false)){completed=true;publish(true);completeSession(persian?"تمام شد":"Done");WebSocket ws=webSocket;if(ws!=null)ws.close(1000,"finished");}}catch(Exception ignored){}
    }
    private boolean isControl(String t){String s=t==null?"":t.trim();return"<end>".equalsIgnoreCase(s)||"<fin>".equalsIgnoreCase(s);}

    private void publish(boolean finish){
        final String display;synchronized(textLock){display=finalTranscript.toString()+(finish?"":partialTranscript);}main.post(()->{if(!sessionStillBound()&&!finish)return;if(boundConnection==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=boundConnection){if(running)abortForEditorChange();return;}try{boundConnection.setComposingText(display,1);if(finish)boundConnection.finishComposingText();}catch(Exception e){abortForEditorChange();}});
    }
    private void finishWithText(String m){if(!running)return;completed=true;publish(true);completeSession(m);}
    private void completeSession(String m){running=false;stopRequested=true;awaitingCredential=false;stopAudioRecord();clearPending();main.post(()->{setCollapsed(false);updateMicUi();setStatus(m);});}
    private void failSession(String m){if(!running)return;synchronized(textLock){if(finalTranscript.length()>0||partialTranscript.length()>0){finishWithText(m);return;}}running=false;stopRequested=true;awaitingCredential=false;stopAudioRecord();clearPending();WebSocket ws=webSocket;webSocket=null;if(ws!=null)ws.cancel();main.post(()->{setCollapsed(false);updateMicUi();setStatus(m);});}
    private void stopAudioRecord(){AudioRecord r=audioRecord;audioRecord=null;if(r!=null){try{if(r.getRecordingState()==AudioRecord.RECORDSTATE_RECORDING)r.stop();}catch(Exception ignored){}try{r.release();}catch(Exception ignored){}}}

    private void updateMicUi(){
        String label=running?"🎙 "+badge():"🎤";if(mic!=null){mic.setText(label);mic.setTextColor(running?Color.WHITE:TEXT);mic.setBackground(round(running?MIC_ACTIVE:0x00FFFFFF,dp(15)));}if(collapse!=null)collapse.setVisibility(running?View.VISIBLE:View.INVISIBLE);if(compactMic!=null)compactMic.setText("🎙 "+badge());if(compactStatus!=null)compactStatus.setText(listeningText());
    }
    private String badge(){return persian?"FA":"EN";}
    private String readyText(){return persian?"آماده — میکروفون فارسی":"Ready — English microphone";}
    private String listeningText(){return persian?"در حال گوش کردن…":"Listening…";}
    private void setStatus(String s){if(status!=null)status.setText(s);if(compactStatus!=null&&running)compactStatus.setText(s);}
    private int dp(int v){return Math.round(v*getResources().getDisplayMetrics().density);}
    private GradientDrawable round(int color,int radius){GradientDrawable g=new GradientDrawable();g.setColor(color);g.setCornerRadius(radius);return g;}
    private void put(JSONObject o,String k,Object v){try{o.put(k,v);}catch(Exception ignored){}}

    @SuppressLint({"SetJavaScriptEnabled","AddJavascriptInterface"})
    private void configureWebView(){
        WebSettings s=auth.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setUserAgentString(MOBILE_BROWSER_UA);CookieManager.getInstance().setAcceptCookie(true);CookieManager.getInstance().setAcceptThirdPartyCookies(auth,true);auth.addJavascriptInterface(new CredentialBridge(),"AndroidKeyboard");auth.setWebViewClient(new WebViewClient(){
            @Override public void onPageFinished(WebView view,String url){String host=null;try{host=Uri.parse(url).getHost();}catch(Exception ignored){}pageReady=host!=null&&(host.equals("perplexity.ai")||host.endsWith(".perplexity.ai"));if(running&&awaitingCredential&&retryAfterPageLoad&&pageReady){retryAfterPageLoad=false;main.postDelayed(PersianKeyboardService.this::requestCredential,350L);}else if(!running)setStatus(pageReady?readyText():"Open app/login to Perplexity once");}
        });
    }

    private final class CredentialBridge {
        @JavascriptInterface public void credential(String apiKey,String expiresAt){main.post(()->{if(!running||!awaitingCredential)return;awaitingCredential=false;retryAfterPageLoad=false;if(apiKey==null||apiKey.isEmpty()){failSession("Perplexity returned no credential");return;}startSoniox(apiKey);});}
        @JavascriptInterface public void credentialError(String error){main.post(()->{if(!running||!awaitingCredential)return;lastCredentialError=safeCredentialError(error);if(credentialAttempt<3&&auth!=null){retryAfterPageLoad=true;pageReady=false;setStatus(persian?"در حال بازیابی نشست Perplexity…":"Refreshing Perplexity session…");try{CookieManager.getInstance().flush();}catch(Exception ignored){}auth.reload();main.postDelayed(()->{if(running&&awaitingCredential&&retryAfterPageLoad){retryAfterPageLoad=false;requestCredential();}},1600L);return;}awaitingCredential=false;failSession("Perplexity credential failed ("+lastCredentialError+")");});}
    }

    @Override public void onDestroy(){running=false;stopRequested=true;stopAudioRecord();clearPending();if(webSocket!=null)webSocket.cancel();if(auth!=null){auth.removeJavascriptInterface("AndroidKeyboard");auth.destroy();}http.dispatcher().executorService().shutdown();super.onDestroy();}

    private static final String FETCH_CREDENTIAL_JS=
            "(async function(){try{"+
            "const tz=(Intl.DateTimeFormat().resolvedOptions().timeZone||'UTC');"+
            "const r=await fetch('/rest/realtime/v1/transcription/soniox-api-key',{method:'POST',credentials:'include',headers:{'Accept':'application/json','Content-Type':'application/json'},body:JSON.stringify({source:'android',timezone:tz,version:'2.97.0'})});"+
            "if(!r.ok){AndroidKeyboard.credentialError('http '+r.status);return;}"+
            "const j=await r.json();if(!j||!j.api_key){AndroidKeyboard.credentialError('no key');return;}"+
            "AndroidKeyboard.credential(String(j.api_key),String(j.expires_at||''));"+
            "}catch(e){AndroidKeyboard.credentialError(String(e&&e.name||'Error'));}})()";
}
