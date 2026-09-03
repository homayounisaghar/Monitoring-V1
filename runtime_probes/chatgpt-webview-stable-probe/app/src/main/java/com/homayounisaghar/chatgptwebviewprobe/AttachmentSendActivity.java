package com.homayounisaghar.chatgptwebviewprobe;

import android.app.Activity;
import android.content.ClipData;
import android.content.ContentValues;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.MediaStore;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Space;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import java.util.regex.Pattern;

public class AttachmentSendActivity extends Activity {
    private static final int FILE_CHOOSER_REQUEST = 4343;
    private static final Pattern UUID_PATTERN = Pattern.compile(
            "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$");
    private static final String PREFS = "stable_v07_attachment_claim_journal";

    private WebView webView;
    private TextView statusView;
    private EditText draftInput;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final StringBuilder eventLog = new StringBuilder();
    private long probeSequence = 0L;
    private String lastUrl = "";
    private String latestSummary = "DOM: waiting";
    private int latestComposerAttachmentHints = -1;
    private int latestGlobalAttachmentHints = -1;

    private ValueCallback<Uri[]> pendingFileCallback;
    private String fileChooserOrigin = "-";
    private String fileChooserStatus = "NOT_RUN";
    private String fileAcceptTypes = "-";
    private boolean fileMultipleAllowed = false;
    private int fileSelectedCount = 0;
    private String fileSelectedMimeTypes = "-";

    private String attachStatus = "NOT_RUN";
    private String attachPhase = "IDLE";
    private String attachCid = "-";
    private String attachTriggerResult = "-";
    private int attachBaselineComposerHints = -1;
    private long attachStartedAt = 0L;

    private String draftStatus = "NOT_RUN";
    private String draftCid = "-";
    private String draftHash = "-";
    private int draftBaselineUserCount = -1;
    private String draftBaselineUserHash = "-";
    private int draftBaselineAssistantCount = -1;
    private String draftBaselineAssistantHash = "-";
    private int draftComposerAttachmentHints = -1;

    private String sendStatus = "IDLE";
    private String sendPhase = "IDLE";
    private String sendRunId = "-";
    private String sendCid = "-";
    private String sendDraftHash = "-";
    private int sendBaselineUserCount = -1;
    private String sendBaselineUserHash = "-";
    private int sendBaselineAssistantCount = -1;
    private String sendBaselineAssistantHash = "-";
    private int sendBaselineComposerAttachmentHints = -1;
    private int sendLastAssistantCount = -1;
    private String sendLastAssistantHash = "-";
    private int sendStableSamples = 0;
    private boolean sendSawUiStreaming = false;
    private boolean sendSawAssistantEvolution = false;
    private boolean sendSawExactUserIncrement = false;
    private boolean sendSawComposerCleared = false;
    private boolean sendSawAttachmentCleared = false;
    private long sendStartedAt = 0L;

    private SharedPreferences prefs;

    private final Runnable probeRunnable = new Runnable() {
        @Override public void run() {
            probeOnce();
            handler.postDelayed(this, 500L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        restoreJournal();

        getWindow().setStatusBarColor(Color.WHITE);
        getWindow().setNavigationBarColor(Color.WHITE);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);

        CookieManager cm = CookieManager.getInstance();
        cm.setAcceptCookie(true);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setFitsSystemWindows(true);

        Space gap = new Space(this);
        root.addView(gap, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(8)));

        LinearLayout row1 = new LinearLayout(this);
        row1.setOrientation(LinearLayout.HORIZONTAL);
        row1.addView(button("HOME", new View.OnClickListener() {
            @Override public void onClick(View v) { webView.loadUrl("https://chatgpt.com/"); }
        }), weighted());
        row1.addView(button("ATTACH FILE", new View.OnClickListener() {
            @Override public void onClick(View v) { beginNativeAttach(); }
        }), weighted());
        row1.addView(button("V06 SUITE", new View.OnClickListener() {
            @Override public void onClick(View v) {
                startActivity(new Intent(AttachmentSendActivity.this, CapabilitySuiteActivity.class));
            }
        }), weighted());
        row1.addView(button("RELOAD", new View.OnClickListener() {
            @Override public void onClick(View v) { webView.reload(); }
        }), weighted());
        root.addView(row1, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(46)));

        draftInput = new EditText(this);
        draftInput.setSingleLine(false);
        draftInput.setMaxLines(3);
        draftInput.setTextSize(13f);
        draftInput.setHint("After ATTACH FILE is ATTACHED, type a normal prompt here.");
        draftInput.setPadding(dp(8), dp(4), dp(8), dp(4));
        root.addView(draftInput, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(62)));

        LinearLayout row2 = new LinearLayout(this);
        row2.setOrientation(LinearLayout.HORIZONTAL);
        row2.addView(button("DRAFT", new View.OnClickListener() {
            @Override public void onClick(View v) { beginDraftSet(); }
        }), weighted());
        row2.addView(button("SEND ATTACH ONCE", new View.OnClickListener() {
            @Override public void onClick(View v) { beginGuardedAttachmentSend(); }
        }), weighted());
        row2.addView(button("DOWNLOAD", new View.OnClickListener() {
            @Override public void onClick(View v) { downloadReport(); }
        }), weighted());
        root.addView(row2, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(48)));

        statusView = new TextView(this);
        statusView.setTextSize(10.5f);
        statusView.setTextIsSelectable(true);
        statusView.setPadding(dp(8), dp(5), dp(8), dp(5));
        ScrollView statusScroll = new ScrollView(this);
        statusScroll.addView(statusView, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT,
                ScrollView.LayoutParams.WRAP_CONTENT));
        root.addView(statusScroll, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(235)));

        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setJavaScriptCanOpenWindowsAutomatically(true);
        settings.setLoadWithOverviewMode(false);
        settings.setUseWideViewPort(false);
        cm.setAcceptThirdPartyCookies(webView, true);

        webView.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onShowFileChooser(WebView view,
                                                       ValueCallback<Uri[]> filePathCallback,
                                                       FileChooserParams params) {
                if (pendingFileCallback != null) pendingFileCallback.onReceiveValue(null);
                pendingFileCallback = filePathCallback;
                fileChooserStatus = "REQUESTED";
                fileChooserOrigin = ("WAIT_CHOOSER".equals(attachPhase)
                        || "TRIGGERING".equals(attachPhase)) ? "NATIVE_ATTACH_BUTTON" : "WEB_UI";
                fileSelectedCount = 0;
                fileSelectedMimeTypes = "-";
                fileMultipleAllowed = params != null
                        && params.getMode() == FileChooserParams.MODE_OPEN_MULTIPLE;
                fileAcceptTypes = sanitizeAcceptTypes(params == null ? null : params.getAcceptTypes());
                if ("NATIVE_ATTACH_BUTTON".equals(fileChooserOrigin)) {
                    attachPhase = "CHOOSER";
                    attachStatus = "CHOOSER_OPEN";
                }
                recordEvent("FILE_CHOOSER_REQUESTED_" + fileChooserOrigin);
                renderStatus(webView == null ? "-" : webView.getUrl());
                try {
                    Intent intent = params == null ? fallbackFileIntent() : params.createIntent();
                    startActivityForResult(intent, FILE_CHOOSER_REQUEST);
                    return true;
                } catch (Exception first) {
                    try {
                        startActivityForResult(fallbackFileIntent(), FILE_CHOOSER_REQUEST);
                        return true;
                    } catch (Exception second) {
                        fileChooserStatus = "FAIL_LAUNCH";
                        if (pendingFileCallback != null) pendingFileCallback.onReceiveValue(null);
                        pendingFileCallback = null;
                        if ("NATIVE_ATTACH_BUTTON".equals(fileChooserOrigin)) {
                            attachStatus = "FAIL_CHOOSER_LAUNCH";
                            attachPhase = "IDLE";
                        }
                        recordEvent("FILE_CHOOSER_FAIL_LAUNCH");
                        return true;
                    }
                }
            }
        });

        webView.setWebViewClient(new WebViewClient() {
            @Override public void onPageStarted(WebView view, String url, Bitmap favicon) {
                recordRoute("PAGE_START", url);
                super.onPageStarted(view, url, favicon);
            }
            @Override public void onPageFinished(WebView view, String url) {
                recordRoute("PAGE_FINISH", url);
                CookieManager.getInstance().flush();
                super.onPageFinished(view, url);
            }
        });

        root.addView(webView, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));
        setContentView(root);
        webView.loadUrl("https://chatgpt.com/");
        handler.post(probeRunnable);
        renderStatus("-");
    }

    private Button button(String text, View.OnClickListener listener) {
        Button b = new Button(this);
        b.setText(text);
        b.setTextSize(9.5f);
        b.setOnClickListener(listener);
        return b;
    }

    private LinearLayout.LayoutParams weighted() {
        return new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f);
    }

    private void probeOnce() {
        if (webView == null) return;
        final String url = safe(webView.getUrl());
        if (!url.equals(lastUrl)) {
            lastUrl = url;
            recordRoute("URL_CHANGE", url);
        }
        long now = System.currentTimeMillis();
        if (("WAIT_CHOOSER".equals(attachPhase) || "TRIGGERING".equals(attachPhase))
                && attachStartedAt > 0L && now - attachStartedAt > 5000L) {
            checkAttachTriggerResult();
        }
        if ("WAIT_DOM".equals(attachPhase) && attachStartedAt > 0L
                && now - attachStartedAt > 20000L) {
            attachStatus = "FAIL_NO_DOM_ATTACHMENT";
            attachPhase = "IDLE";
            recordEvent("NATIVE_ATTACH_FAIL_NO_DOM_ATTACHMENT");
        }
        if (!"IDLE".equals(sendPhase) && sendStartedAt > 0L
                && now - sendStartedAt > 300000L) {
            markSendUncertain("UNCERTAIN_TIMEOUT");
        }

        final long seq = ++probeSequence;
        webView.evaluateJavascript(snapshotJs(), new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                if (seq < probeSequence - 3) return;
                try {
                    Snapshot s = parseSnapshot(value);
                    latestSummary = s.summary;
                    latestComposerAttachmentHints = s.composerAttachmentHints;
                    latestGlobalAttachmentHints = s.globalAttachmentHints;
                    driveNativeAttach(s, url);
                    driveSendReceipt(s, url);
                } catch (Exception e) {
                    latestSummary = "DOM_PARSE_ERROR: " + e.getClass().getSimpleName();
                }
                renderStatus(url);
            }
        });
    }

    private String snapshotJs() {
        return "(function(){try{"
                + "const qa=(s)=>Array.from(document.querySelectorAll(s));"
                + "const vis=(e)=>{const r=e.getBoundingClientRect();const st=getComputedStyle(e);return r.width>0&&r.height>0&&st.visibility!=='hidden'&&st.display!=='none';};"
                + "const norm=(x)=>(x||'').replace(/\\s+/g,' ').trim();"
                + "const label=(e)=>norm(e.getAttribute('aria-label')||e.innerText||e.textContent||'');"
                + "const users=qa('[data-message-author-role=\\\"user\\\"]').map(e=>norm(e.innerText||e.textContent)).filter(Boolean);"
                + "const assistants=qa('[data-message-author-role=\\\"assistant\\\"]').map(e=>norm(e.innerText||e.textContent)).filter(Boolean);"
                + "const controls=qa('button,[role=\\\"button\\\"]').filter(vis);"
                + "const stop=controls.filter(e=>{const x=(label(e)+' '+(e.getAttribute('data-testid')||'')).toLowerCase();return x.includes('stop generating')||x.includes('stop response')||x.includes('stop-generating')||x==='stop';}).length;"
                + "const busy=qa('[aria-busy=\\\"true\\\"]').filter(vis).length;"
                + "const responseActions=qa('[aria-label=\\\"Response actions\\\" i]').filter(vis).length;"
                + "const composer=document.querySelector('#prompt-textarea')||qa('textarea,[contenteditable=\\\"true\\\"]').filter(vis).slice(-1)[0]||null;"
                + "const composerText=composer?norm(('value' in composer?composer.value:(composer.innerText||composer.textContent))):'';"
                + "const attachmentSel='[data-testid*=\\\"attachment\\\" i],[aria-label*=\\\"remove file\\\" i],[aria-label*=\\\"remove attachment\\\" i],[data-testid*=\\\"file-pill\\\" i]';"
                + "const globalAttachmentHints=qa(attachmentSel).filter(vis).length;"
                + "const composerRoot=composer?(composer.closest('form')||composer.parentElement):null;"
                + "const composerAttachmentHints=composerRoot?Array.from(composerRoot.querySelectorAll(attachmentSel)).filter(vis).length:-1;"
                + "const sendButtons=controls.filter(e=>{const x=(label(e)+' '+(e.getAttribute('data-testid')||'')).toLowerCase();const en=!e.disabled&&e.getAttribute('aria-disabled')!=='true';return en&&(x.includes('send')||x.includes('submit'))&&!x.includes('share');});"
                + "return JSON.stringify({href:location.href,title:document.title,ready:document.readyState,users:users,assistants:assistants,stop:stop,busy:busy,responseActions:responseActions,composerText:composerText,globalAttachmentHints:globalAttachmentHints,composerAttachmentHints:composerAttachmentHints,sendButtons:sendButtons.length});"
                + "}catch(e){return JSON.stringify({error:String(e),href:String(location.href),users:[],assistants:[],composerText:''});}})();";
    }

    private Snapshot parseSnapshot(String value) throws Exception {
        JSONObject o = jsonObject(value);
        Fingerprint users = fingerprintArray(o.optJSONArray("users"));
        Fingerprint assistants = fingerprintArray(o.optJSONArray("assistants"));
        String composerText = normalize(o.optString("composerText", ""));
        String composerHash = composerText.isEmpty() ? "-" : sha256(composerText);
        int stop = o.optInt("stop", -1);
        int busy = o.optInt("busy", -1);
        int responseActions = o.optInt("responseActions", -1);
        int globalHints = o.optInt("globalAttachmentHints", -1);
        int composerHints = o.optInt("composerAttachmentHints", -1);
        int sendButtons = o.optInt("sendButtons", -1);
        StringBuilder summary = new StringBuilder();
        summary.append("TITLE: ").append(o.optString("title", "-")).append('\n');
        summary.append("READY: ").append(o.optString("ready", "-")).append('\n');
        summary.append("MESSAGES: user=").append(users.count).append(" assistant=").append(assistants.count).append('\n');
        summary.append("STREAM: stop=").append(stop).append(" busy=").append(busy)
                .append(" responseActions=").append(responseActions).append('\n');
        summary.append("COMPOSER: hash=").append(shortHash(composerHash))
                .append(" sendButtons=").append(sendButtons).append('\n');
        summary.append("ATTACHMENTS: composer=").append(composerHints)
                .append(" global=").append(globalHints);
        if (o.has("error")) summary.append("\nJS_ERROR: ").append(o.optString("error"));
        return new Snapshot(users, assistants, composerHash, stop, busy, responseActions,
                globalHints, composerHints, sendButtons, summary.toString());
    }

    private void beginNativeAttach() {
        if (webView == null) return;
        if (!"IDLE".equals(sendPhase)) {
            Toast.makeText(this, "Finish the current Send first", Toast.LENGTH_LONG).show();
            return;
        }
        final String cid = extractCanonicalConversationId(sanitizeUrl(webView.getUrl()));
        if ("-".equals(cid)) {
            attachStatus = "FAIL_NO_CANONICAL_CHAT";
            renderStatus(webView.getUrl());
            return;
        }
        attachStatus = "CAPTURING_BASELINE";
        attachPhase = "TRIGGERING";
        attachCid = cid;
        attachTriggerResult = "-";
        fileChooserOrigin = "-";
        fileChooserStatus = "NOT_RUN";
        fileSelectedCount = 0;
        fileSelectedMimeTypes = "-";
        draftStatus = "NOT_RUN";
        draftHash = "-";
        sendStatus = journalBlocksNewSend() ? sendStatus : "IDLE";
        attachStartedAt = System.currentTimeMillis();

        webView.evaluateJavascript(snapshotJs(), new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                try {
                    Snapshot s = parseSnapshot(value);
                    attachBaselineComposerHints = s.composerAttachmentHints;
                    attachPhase = "WAIT_CHOOSER";
                    attachStatus = "TRIGGERING_CHATGPT_FILES";
                    recordEvent("NATIVE_ATTACH_TRIGGER_START");
                    webView.evaluateJavascript(nativeAttachTriggerJs(), new ValueCallback<String>() {
                        @Override public void onReceiveValue(String result) {
                            attachTriggerResult = cleanJsScalar(result);
                            recordEvent("NATIVE_ATTACH_TRIGGER_" + safeEventToken(attachTriggerResult));
                            handler.postDelayed(new Runnable() {
                                @Override public void run() { checkAttachTriggerResult(); }
                            }, 2500L);
                        }
                    });
                } catch (Exception e) {
                    attachStatus = "FAIL_BASELINE_PARSE";
                    attachPhase = "IDLE";
                }
                renderStatus(webView.getUrl());
            }
        });
    }

    private String nativeAttachTriggerJs() {
        return "(function(){try{"
                + "const norm=(x)=>(x||'').replace(/\\s+/g,' ').trim();"
                + "const vis=(e)=>{const r=e.getBoundingClientRect();const st=getComputedStyle(e);return r.width>0&&r.height>0&&st.visibility!=='hidden'&&st.display!=='none';};"
                + "const label=(e)=>norm(e.getAttribute('aria-label')||e.innerText||e.textContent||'');"
                + "const controls=()=>Array.from(document.querySelectorAll('button,[role=\\\"button\\\"],[role=\\\"menuitem\\\"]')).filter(vis);"
                + "window.__cpNativeAttachResult='START';"
                + "const clickFiles=()=>{const f=controls().filter(e=>label(e).toLowerCase()==='files');if(f.length===1){f[0].click();window.__cpNativeAttachResult='FILES_CLICKED';return true;}window.__cpNativeAttachResult='FILES_COUNT_'+f.length;return false;};"
                + "if(clickFiles())return window.__cpNativeAttachResult;"
                + "const adds=controls().filter(e=>{const x=label(e).toLowerCase();return x==='add files and more'||x.includes('add files and more');});"
                + "if(adds.length!==1){window.__cpNativeAttachResult='ADD_COUNT_'+adds.length;return window.__cpNativeAttachResult;}"
                + "adds[0].click();window.__cpNativeAttachResult='ADD_CLICKED';setTimeout(clickFiles,220);return window.__cpNativeAttachResult;"
                + "}catch(e){window.__cpNativeAttachResult='ERROR';return 'ERROR';}})();";
    }

    private void checkAttachTriggerResult() {
        if (webView == null || !"WAIT_CHOOSER".equals(attachPhase)) return;
        webView.evaluateJavascript("String(window.__cpNativeAttachResult||'-')", new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                if (!"WAIT_CHOOSER".equals(attachPhase)) return;
                attachTriggerResult = cleanJsScalar(value);
                attachStatus = "BLOCKED_CHOOSER_NOT_REQUESTED";
                attachPhase = "IDLE";
                recordEvent("NATIVE_ATTACH_BLOCKED_" + safeEventToken(attachTriggerResult));
                renderStatus(webView.getUrl());
            }
        });
    }

    private void driveNativeAttach(Snapshot s, String rawUrl) {
        if (!"WAIT_DOM".equals(attachPhase)) return;
        String cid = extractCanonicalConversationId(sanitizeUrl(rawUrl));
        if (!attachCid.equals(cid)) {
            attachStatus = "FAIL_ROUTE_CHANGED";
            attachPhase = "IDLE";
            recordEvent("NATIVE_ATTACH_FAIL_ROUTE_CHANGED");
            return;
        }
        boolean grew = s.composerAttachmentHints > attachBaselineComposerHints
                && s.composerAttachmentHints > 0;
        if (fileSelectedCount > 0 && grew) {
            attachStatus = "ATTACHED";
            attachPhase = "IDLE";
            recordEvent("NATIVE_ATTACH_DOM_CONFIRMED");
        }
    }

    private void beginDraftSet() {
        if (webView == null) return;
        if (!"ATTACHED".equals(attachStatus)) {
            draftStatus = "BLOCKED_NO_CONFIRMED_ATTACHMENT";
            renderStatus(webView.getUrl());
            return;
        }
        final String text = normalize(draftInput.getText() == null ? "" : draftInput.getText().toString());
        if (text.isEmpty()) {
            draftStatus = "BLOCKED_EMPTY_DRAFT";
            renderStatus(webView.getUrl());
            return;
        }
        final String cid = extractCanonicalConversationId(sanitizeUrl(webView.getUrl()));
        if (!attachCid.equals(cid)) {
            draftStatus = "BLOCKED_ROUTE_MISMATCH";
            renderStatus(webView.getUrl());
            return;
        }
        try { draftHash = sha256(text); }
        catch (Exception e) { draftStatus = "FAIL_HASH"; return; }
        draftCid = cid;
        draftStatus = "SETTING";
        String js = setComposerJs(text);
        webView.evaluateJavascript(js, new ValueCallback<String>() {
            @Override public void onReceiveValue(String ignored) {
                handler.postDelayed(new Runnable() {
                    @Override public void run() { verifyDraftReadback(); }
                }, 350L);
            }
        });
    }

    private String setComposerJs(String text) {
        String q = JSONObject.quote(text);
        return "(function(){try{const txt=" + q + ";"
                + "const vis=(e)=>{const r=e.getBoundingClientRect();const st=getComputedStyle(e);return r.width>0&&r.height>0&&st.visibility!=='hidden'&&st.display!=='none';};"
                + "const c=document.querySelector('#prompt-textarea')||Array.from(document.querySelectorAll('textarea,[contenteditable=\\\"true\\\"]')).filter(vis).slice(-1)[0]||null;"
                + "if(!c)return 'NO_COMPOSER';c.focus();"
                + "if('value' in c){const p=Object.getPrototypeOf(c);const d=Object.getOwnPropertyDescriptor(p,'value')||Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value');if(d&&d.set)d.set.call(c,txt);else c.value=txt;}"
                + "else{c.textContent=txt;}"
                + "c.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText',data:txt}));"
                + "c.dispatchEvent(new Event('change',{bubbles:true}));return 'SET';"
                + "}catch(e){return 'ERROR';}})();";
    }

    private void verifyDraftReadback() {
        if (webView == null) return;
        webView.evaluateJavascript(snapshotJs(), new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                try {
                    Snapshot s = parseSnapshot(value);
                    String cid = extractCanonicalConversationId(sanitizeUrl(webView.getUrl()));
                    if (!draftCid.equals(cid)) draftStatus = "FAIL_ROUTE_MISMATCH";
                    else if (!draftHash.equals(s.composerHash)) draftStatus = "FAIL_COMPOSER_HASH_MISMATCH";
                    else if (s.composerAttachmentHints <= 0) draftStatus = "FAIL_ATTACHMENT_DISAPPEARED";
                    else {
                        draftStatus = "VERIFIED";
                        draftBaselineUserCount = s.users.count;
                        draftBaselineUserHash = s.users.hash;
                        draftBaselineAssistantCount = s.assistants.count;
                        draftBaselineAssistantHash = s.assistants.hash;
                        draftComposerAttachmentHints = s.composerAttachmentHints;
                        recordEvent("ATTACH_DRAFT_VERIFIED");
                    }
                } catch (Exception e) { draftStatus = "FAIL_READBACK_PARSE"; }
                renderStatus(webView.getUrl());
            }
        });
    }

    private void beginGuardedAttachmentSend() {
        if (webView == null) return;
        if (journalBlocksNewSend()) {
            sendStatus = "BLOCKED_UNRESOLVED_JOURNAL";
            renderStatus(webView.getUrl());
            return;
        }
        if (!"VERIFIED".equals(draftStatus) || !"ATTACHED".equals(attachStatus)) {
            sendStatus = "BLOCKED_NEEDS_ATTACHMENT_AND_VERIFIED_DRAFT";
            renderStatus(webView.getUrl());
            return;
        }
        if (!"IDLE".equals(sendPhase)) return;
        webView.evaluateJavascript(snapshotJs(), new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                try {
                    Snapshot s = parseSnapshot(value);
                    String cid = extractCanonicalConversationId(sanitizeUrl(webView.getUrl()));
                    if (!draftCid.equals(cid)) { sendStatus = "BLOCKED_ROUTE_MISMATCH"; return; }
                    if (!draftHash.equals(s.composerHash)) { sendStatus = "BLOCKED_DRAFT_CHANGED"; return; }
                    if (s.users.count != draftBaselineUserCount || !safeEq(s.users.hash, draftBaselineUserHash)
                            || s.assistants.count != draftBaselineAssistantCount
                            || !safeEq(s.assistants.hash, draftBaselineAssistantHash)) {
                        sendStatus = "BLOCKED_BASELINE_CHANGED"; return;
                    }
                    if (s.composerAttachmentHints <= 0
                            || s.composerAttachmentHints < draftComposerAttachmentHints) {
                        sendStatus = "BLOCKED_ATTACHMENT_MISSING"; return;
                    }
                    if (s.sendButtons != 1) { sendStatus = "BLOCKED_SEND_CANDIDATES_" + s.sendButtons; return; }

                    sendRunId = UUID.randomUUID().toString();
                    sendCid = cid;
                    sendDraftHash = draftHash;
                    sendBaselineUserCount = s.users.count;
                    sendBaselineUserHash = s.users.hash;
                    sendBaselineAssistantCount = s.assistants.count;
                    sendBaselineAssistantHash = s.assistants.hash;
                    sendBaselineComposerAttachmentHints = s.composerAttachmentHints;
                    sendLastAssistantCount = -1;
                    sendLastAssistantHash = "-";
                    sendStableSamples = 0;
                    sendSawUiStreaming = false;
                    sendSawAssistantEvolution = false;
                    sendSawExactUserIncrement = false;
                    sendSawComposerCleared = false;
                    sendSawAttachmentCleared = false;
                    sendStartedAt = System.currentTimeMillis();

                    if (!persistClaim("CLAIMED")) {
                        sendStatus = "BLOCKED_CLAIM_PERSIST_FAIL";
                        return;
                    }
                    sendStatus = "CLAIMED";
                    sendPhase = "DISPATCHING";
                    recordEvent("ATTACH_SEND_DURABLE_CLAIMED");
                    dispatchSingleSendClick();
                } catch (Exception e) { sendStatus = "BLOCKED_PRECHECK_PARSE"; }
                renderStatus(webView.getUrl());
            }
        });
    }

    private void dispatchSingleSendClick() {
        webView.evaluateJavascript(clickSendJs(), new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                try {
                    JSONObject o = jsonObject(value);
                    int count = o.optInt("count", -1);
                    boolean clicked = o.optBoolean("clicked", false);
                    if (!clicked || count != 1) {
                        markSendUncertain("UNCERTAIN_SEND_CANDIDATES_" + count);
                        return;
                    }
                    prefs.edit().putString("state", "DISPATCHED").commit();
                    sendPhase = "WAIT_USER";
                    sendStatus = "DISPATCHED_WAIT_USER_RECEIPT";
                    recordEvent("ATTACH_SEND_SINGLE_CLICK_DISPATCHED");
                } catch (Exception e) {
                    markSendUncertain("UNCERTAIN_CLICK_RESULT_PARSE");
                }
                renderStatus(webView.getUrl());
            }
        });
    }

    private String clickSendJs() {
        return "(function(){try{const norm=(x)=>(x||'').replace(/\\s+/g,' ').trim();"
                + "const vis=(e)=>{const r=e.getBoundingClientRect();const st=getComputedStyle(e);return r.width>0&&r.height>0&&st.visibility!=='hidden'&&st.display!=='none';};"
                + "const label=(e)=>norm(e.getAttribute('aria-label')||e.innerText||e.textContent||'').toLowerCase();"
                + "const bs=Array.from(document.querySelectorAll('button,[role=\\\"button\\\"]')).filter(vis).filter(e=>{const x=label(e)+' '+(e.getAttribute('data-testid')||'').toLowerCase();return !e.disabled&&e.getAttribute('aria-disabled')!=='true'&&(x.includes('send')||x.includes('submit'))&&!x.includes('share');});"
                + "if(bs.length!==1)return JSON.stringify({clicked:false,count:bs.length});bs[0].click();return JSON.stringify({clicked:true,count:1});"
                + "}catch(e){return JSON.stringify({clicked:false,count:-1});}})();";
    }

    private void driveSendReceipt(Snapshot s, String rawUrl) {
        if ("IDLE".equals(sendPhase) || "DISPATCHING".equals(sendPhase)) return;
        String cid = extractCanonicalConversationId(sanitizeUrl(rawUrl));
        if (!sendCid.equals(cid)) { markSendUncertain("UNCERTAIN_ROUTE_CHANGED"); return; }
        boolean uiStreaming = s.stop > 0 || s.busy > 0;
        if (uiStreaming) sendSawUiStreaming = true;

        if ("WAIT_USER".equals(sendPhase)) {
            if (s.users.count > sendBaselineUserCount + 1) {
                markSendUncertain("UNCERTAIN_MULTIPLE_USER_TURNS");
                return;
            }
            if (s.users.count == sendBaselineUserCount + 1) {
                sendSawExactUserIncrement = true;
                sendSawComposerCleared = "-".equals(s.composerHash);
                sendSawAttachmentCleared = s.composerAttachmentHints == 0;
                if (sendSawComposerCleared && sendSawAttachmentCleared) {
                    sendPhase = "WAIT_ASSISTANT";
                    sendStatus = "USER_RECEIPT_CONFIRMED_WAIT_ASSISTANT";
                    recordEvent("ATTACH_SEND_USER_RECEIPT_CONFIRMED");
                } else {
                    sendStatus = "USER_INCREMENT_WAIT_COMPOSER_ATTACHMENT_CLEAR";
                }
            }
            return;
        }

        if ("WAIT_ASSISTANT".equals(sendPhase)) {
            boolean changed = s.assistants.count > sendBaselineAssistantCount
                    || !safeEq(s.assistants.hash, sendBaselineAssistantHash);
            if (changed && s.assistants.count > 0 && !"-".equals(s.assistants.hash)) {
                sendPhase = "OBSERVING";
                sendStatus = uiStreaming ? "STREAMING_ACTIVE" : "ASSISTANT_CHANGE_SEEN";
                sendLastAssistantCount = s.assistants.count;
                sendLastAssistantHash = s.assistants.hash;
                sendStableSamples = 0;
                recordEvent("ATTACH_SEND_ASSISTANT_CHANGE_SEEN");
            }
            return;
        }

        if (!"OBSERVING".equals(sendPhase)) return;
        boolean changedAgain = s.assistants.count != sendLastAssistantCount
                || !safeEq(s.assistants.hash, sendLastAssistantHash);
        if (changedAgain) {
            if (!"-".equals(sendLastAssistantHash)) sendSawAssistantEvolution = true;
            sendLastAssistantCount = s.assistants.count;
            sendLastAssistantHash = s.assistants.hash;
            sendStableSamples = 0;
            sendStatus = uiStreaming ? "STREAMING_ACTIVE" : "ASSISTANT_EVOLVING";
            return;
        }
        if (uiStreaming) {
            sendStableSamples = 0;
            sendStatus = "STREAMING_ACTIVE";
            return;
        }
        boolean newAssistant = s.assistants.count > sendBaselineAssistantCount
                && !safeEq(s.assistants.hash, sendBaselineAssistantHash)
                && !"-".equals(s.assistants.hash);
        if (newAssistant && s.responseActions > 0) {
            sendStableSamples++;
            sendStatus = "STABILIZING_" + sendStableSamples;
            if (sendStableSamples >= 4) {
                if (!(sendSawExactUserIncrement && sendSawComposerCleared && sendSawAttachmentCleared)) {
                    markSendUncertain("UNCERTAIN_RECEIPT_INVARIANT");
                    return;
                }
                sendStatus = "CONFIRMED";
                sendPhase = "IDLE";
                draftStatus = "CONSUMED_BY_CONFIRMED_ATTACHMENT_SEND";
                prefs.edit().putString("state", "CONFIRMED").commit();
                recordEvent("ATTACH_SEND_CONFIRMED");
            }
        } else {
            sendStableSamples = 0;
            sendStatus = "WAITING_COMPLETE_EVIDENCE";
        }
    }

    private boolean persistClaim(String state) {
        return prefs.edit()
                .putString("state", state)
                .putString("run_id", sendRunId)
                .putString("cid", sendCid)
                .putString("draft_hash", sendDraftHash)
                .putInt("baseline_user_count", sendBaselineUserCount)
                .putString("baseline_user_hash", sendBaselineUserHash)
                .putInt("baseline_assistant_count", sendBaselineAssistantCount)
                .putString("baseline_assistant_hash", sendBaselineAssistantHash)
                .putInt("baseline_composer_attachment_hints", sendBaselineComposerAttachmentHints)
                .commit();
    }

    private boolean journalBlocksNewSend() {
        String s = prefs.getString("state", "NONE");
        return "CLAIMED".equals(s) || "DISPATCHED".equals(s) || (s != null && s.startsWith("UNCERTAIN"));
    }

    private void restoreJournal() {
        String s = prefs.getString("state", "NONE");
        if ("CLAIMED".equals(s) || "DISPATCHED".equals(s) || (s != null && s.startsWith("UNCERTAIN"))) {
            sendRunId = prefs.getString("run_id", "-");
            sendCid = prefs.getString("cid", "-");
            sendStatus = "UNCERTAIN_RECOVERED_" + s;
            sendPhase = "IDLE";
        }
    }

    private void markSendUncertain(String reason) {
        sendStatus = reason;
        sendPhase = "IDLE";
        prefs.edit().putString("state", reason).commit();
        recordEvent("ATTACH_SEND_" + safeEventToken(reason));
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode != FILE_CHOOSER_REQUEST) {
            super.onActivityResult(requestCode, resultCode, data);
            return;
        }
        List<Uri> uris = new ArrayList<>();
        if (resultCode == RESULT_OK && data != null) {
            ClipData clip = data.getClipData();
            if (clip != null) {
                for (int i = 0; i < clip.getItemCount(); i++) {
                    Uri u = clip.getItemAt(i).getUri();
                    if (u != null) uris.add(u);
                }
            } else if (data.getData() != null) {
                uris.add(data.getData());
            }
        }
        Uri[] result = uris.isEmpty() ? null : uris.toArray(new Uri[0]);
        if (pendingFileCallback != null) pendingFileCallback.onReceiveValue(result);
        pendingFileCallback = null;

        if (result == null) {
            fileChooserStatus = "CANCELLED";
            if ("NATIVE_ATTACH_BUTTON".equals(fileChooserOrigin)) {
                attachStatus = "CANCELLED";
                attachPhase = "IDLE";
                recordEvent("NATIVE_ATTACH_CANCELLED");
            }
        } else {
            fileChooserStatus = "SELECTED";
            fileSelectedCount = result.length;
            fileSelectedMimeTypes = mimeSummary(result);
            if ("NATIVE_ATTACH_BUTTON".equals(fileChooserOrigin)) {
                attachStatus = "SELECTED_WAIT_DOM";
                attachPhase = "WAIT_DOM";
                attachStartedAt = System.currentTimeMillis();
                recordEvent("NATIVE_ATTACH_FILE_SELECTED");
            }
        }
        renderStatus(webView == null ? "-" : webView.getUrl());
    }

    private Intent fallbackFileIntent() {
        Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("*/*");
        i.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, fileMultipleAllowed);
        return i;
    }

    private String sanitizeAcceptTypes(String[] types) {
        if (types == null || types.length == 0) return "-";
        List<String> clean = new ArrayList<>();
        for (String t : types) if (t != null && !t.trim().isEmpty()) clean.add(t.trim());
        return clean.isEmpty() ? "-" : clean.toString();
    }

    private String mimeSummary(Uri[] uris) {
        List<String> types = new ArrayList<>();
        for (Uri u : uris) {
            String t = null;
            try { t = getContentResolver().getType(u); } catch (Exception ignored) { }
            if (t == null || t.trim().isEmpty()) t = "unknown";
            if (!types.contains(t)) types.add(t);
        }
        return types.toString();
    }

    private void renderStatus(String rawUrl) {
        String safeUrl = sanitizeUrl(rawUrl);
        String cid = extractCanonicalConversationId(safeUrl);
        StringBuilder s = new StringBuilder();
        s.append("Stable v0.7 — NATIVE ATTACH + GUARDED ATTACHMENT SEND\n");
        s.append("CID: ").append(cid).append('\n');
        s.append("ATTACH: ").append(attachStatus).append(" trigger=").append(attachTriggerResult).append('\n');
        s.append("FILE: ").append(fileChooserStatus).append(" origin=").append(fileChooserOrigin)
                .append(" count=").append(fileSelectedCount).append(" mime=").append(fileSelectedMimeTypes).append('\n');
        s.append("DRAFT: ").append(draftStatus).append('\n');
        s.append("SEND ATTACH: ").append(sendStatus).append('\n');
        s.append(latestSummary);
        statusView.setText(s.toString());
    }

    private String buildReport() {
        String current = sanitizeUrl(webView == null ? null : webView.getUrl());
        String cid = extractCanonicalConversationId(current);
        return "CHATGPT_WEBVIEW_STABLE_V07_NATIVE_ATTACHMENT_SEND\n"
                + "CURRENT_URL=" + current + "\n"
                + "CURRENT_CONVERSATION_ID=" + cid + "\n"
                + "NATIVE_ATTACH_STATUS=" + attachStatus + "\n"
                + "NATIVE_ATTACH_TRIGGER_RESULT=" + attachTriggerResult + "\n"
                + "NATIVE_ATTACH_BASELINE_COMPOSER_HINTS=" + attachBaselineComposerHints + "\n"
                + "CURRENT_COMPOSER_ATTACHMENT_HINTS=" + latestComposerAttachmentHints + "\n"
                + "CURRENT_GLOBAL_ATTACHMENT_HINTS=" + latestGlobalAttachmentHints + "\n"
                + "FILE_CHOOSER_ORIGIN=" + fileChooserOrigin + "\n"
                + "FILE_CHOOSER_STATUS=" + fileChooserStatus + "\n"
                + "FILE_ACCEPT_TYPES=" + fileAcceptTypes + "\n"
                + "FILE_MULTIPLE_ALLOWED=" + fileMultipleAllowed + "\n"
                + "FILE_SELECTED_COUNT=" + fileSelectedCount + "\n"
                + "FILE_SELECTED_MIME_TYPES=" + fileSelectedMimeTypes + "\n"
                + "DRAFT_STATUS=" + draftStatus + "\n"
                + "DRAFT_SHA256=" + draftHash + "\n"
                + "DRAFT_BASELINE_USER_COUNT=" + draftBaselineUserCount + "\n"
                + "DRAFT_BASELINE_ASSISTANT_COUNT=" + draftBaselineAssistantCount + "\n"
                + "DRAFT_COMPOSER_ATTACHMENT_HINTS=" + draftComposerAttachmentHints + "\n"
                + "SEND_ATTACH_STATUS=" + sendStatus + "\n"
                + "SEND_RUN_ID=" + sendRunId + "\n"
                + "SEND_DRAFT_SHA256=" + sendDraftHash + "\n"
                + "SEND_BASELINE_USER_COUNT=" + sendBaselineUserCount + "\n"
                + "SEND_BASELINE_ASSISTANT_COUNT=" + sendBaselineAssistantCount + "\n"
                + "SEND_BASELINE_COMPOSER_ATTACHMENT_HINTS=" + sendBaselineComposerAttachmentHints + "\n"
                + "SEND_SAW_EXACT_USER_INCREMENT=" + sendSawExactUserIncrement + "\n"
                + "SEND_SAW_COMPOSER_CLEARED=" + sendSawComposerCleared + "\n"
                + "SEND_SAW_ATTACHMENT_CLEARED=" + sendSawAttachmentCleared + "\n"
                + "SEND_SAW_UI_STREAMING=" + sendSawUiStreaming + "\n"
                + "SEND_SAW_ASSISTANT_EVOLUTION=" + sendSawAssistantEvolution + "\n"
                + "SEND_STABLE_SAMPLES=" + sendStableSamples + "\n"
                + "RAW_DRAFT_OR_MESSAGE_TEXT_RETAINED=false\n"
                + "FILE_NAMES_OR_URIS_RETAINED=false\n"
                + latestSummary + "\n"
                + "--- EVENT LOG (SANITIZED; NO QUERY/FRAGMENT) ---\n"
                + eventLog;
    }

    private void downloadReport() {
        String ts = new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date());
        String fileName = "chatgpt-webview-v07-report-" + ts + ".txt";
        ContentValues v = new ContentValues();
        v.put(MediaStore.MediaColumns.DISPLAY_NAME, fileName);
        v.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
        v.put(MediaStore.MediaColumns.RELATIVE_PATH,
                Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
        v.put(MediaStore.MediaColumns.IS_PENDING, 1);
        Uri item = null;
        try {
            item = getContentResolver().insert(
                    MediaStore.Downloads.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY), v);
            if (item == null) throw new IllegalStateException();
            try (OutputStream out = getContentResolver().openOutputStream(item, "w")) {
                if (out == null) throw new IllegalStateException();
                out.write(buildReport().getBytes(StandardCharsets.UTF_8));
            }
            ContentValues done = new ContentValues();
            done.put(MediaStore.MediaColumns.IS_PENDING, 0);
            getContentResolver().update(item, done, null, null);
            Toast.makeText(this, "Downloaded: Downloads/ChatGPTWebViewProbe/" + fileName,
                    Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            if (item != null) getContentResolver().delete(item, null, null);
            Toast.makeText(this, "Download failed", Toast.LENGTH_LONG).show();
        }
    }

    private void recordEvent(String kind) {
        recordRoute(kind, webView == null ? "-" : webView.getUrl());
    }

    private void recordRoute(String kind, String rawUrl) {
        String u = sanitizeUrl(rawUrl);
        String cid = extractCanonicalConversationId(u);
        eventLog.append(kind).append(" | ").append(u).append(" | cid=").append(cid).append('\n');
        if (eventLog.length() > 18000) eventLog.delete(0, 6000);
    }

    private String sanitizeUrl(String raw) {
        if (raw == null || raw.trim().isEmpty()) return "-";
        try {
            Uri u = Uri.parse(raw);
            String scheme = u.getScheme();
            String host = u.getHost();
            String path = u.getEncodedPath();
            if (scheme == null || host == null) return "-";
            return scheme + "://" + host + (path == null || path.isEmpty() ? "/" : path);
        } catch (Exception e) { return "-"; }
    }

    private String extractCanonicalConversationId(String url) {
        if (url == null) return "-";
        int i = url.indexOf("/c/");
        if (i < 0) return "-";
        int start = i + 3;
        int slash = url.indexOf('/', start);
        String seg = slash < 0 ? url.substring(start) : url.substring(start, slash);
        return UUID_PATTERN.matcher(seg).matches() ? seg : "-";
    }

    private JSONObject jsonObject(String value) throws Exception {
        Object outer = new JSONTokener(value).nextValue();
        String json = outer instanceof String ? (String) outer : String.valueOf(outer);
        return new JSONObject(json);
    }

    private Fingerprint fingerprintArray(JSONArray array) throws Exception {
        if (array == null || array.length() == 0) return new Fingerprint(0, "-");
        StringBuilder b = new StringBuilder();
        int count = 0;
        for (int i = 0; i < array.length(); i++) {
            String t = normalize(array.optString(i, ""));
            if (t.isEmpty()) continue;
            if (count > 0) b.append('\u001e');
            b.append(t);
            count++;
        }
        return count == 0 ? new Fingerprint(0, "-") : new Fingerprint(count, sha256(b.toString()));
    }

    private String sha256(String s) throws Exception {
        byte[] bytes = MessageDigest.getInstance("SHA-256")
                .digest(s.getBytes(StandardCharsets.UTF_8));
        StringBuilder b = new StringBuilder();
        for (byte x : bytes) b.append(String.format(Locale.US, "%02x", x & 0xff));
        return b.toString();
    }

    private String normalize(String s) {
        return s == null ? "" : s.replaceAll("\\s+", " ").trim();
    }

    private String cleanJsScalar(String s) {
        if (s == null) return "-";
        String x = s.trim();
        if (x.startsWith("\"") && x.endsWith("\"") && x.length() >= 2) {
            x = x.substring(1, x.length() - 1);
        }
        return x.replace("\\\"", "\"");
    }

    private String safeEventToken(String s) {
        if (s == null) return "NONE";
        return s.replaceAll("[^A-Za-z0-9_-]", "_");
    }

    private String shortHash(String s) {
        return s == null || s.length() < 10 ? safe(s) : s.substring(0, 10);
    }

    private boolean safeEq(String a, String b) {
        return a == null ? b == null : a.equals(b);
    }

    private String safe(String s) { return s == null ? "-" : s; }

    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    @Override protected void onPause() {
        CookieManager.getInstance().flush();
        super.onPause();
    }

    @Override protected void onDestroy() {
        handler.removeCallbacks(probeRunnable);
        if (pendingFileCallback != null) pendingFileCallback.onReceiveValue(null);
        pendingFileCallback = null;
        if (webView != null) webView.destroy();
        super.onDestroy();
    }

    private static final class Fingerprint {
        final int count;
        final String hash;
        Fingerprint(int count, String hash) { this.count = count; this.hash = hash; }
    }

    private static final class Snapshot {
        final Fingerprint users;
        final Fingerprint assistants;
        final String composerHash;
        final int stop;
        final int busy;
        final int responseActions;
        final int globalAttachmentHints;
        final int composerAttachmentHints;
        final int sendButtons;
        final String summary;
        Snapshot(Fingerprint users, Fingerprint assistants, String composerHash,
                 int stop, int busy, int responseActions, int globalAttachmentHints,
                 int composerAttachmentHints, int sendButtons, String summary) {
            this.users = users;
            this.assistants = assistants;
            this.composerHash = composerHash;
            this.stop = stop;
            this.busy = busy;
            this.responseActions = responseActions;
            this.globalAttachmentHints = globalAttachmentHints;
            this.composerAttachmentHints = composerAttachmentHints;
            this.sendButtons = sendButtons;
            this.summary = summary;
        }
    }
}
