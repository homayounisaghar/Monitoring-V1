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
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;
import java.util.regex.Pattern;

public class CapabilitySuiteActivity extends Activity {
    private static final int FILE_CHOOSER_REQUEST = 4242;
    private static final Pattern UUID_PATTERN = Pattern.compile(
            "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$");
    private static final String PREFS = "stable_v06_claim_journal";

    private WebView webView;
    private TextView statusView;
    private EditText draftInput;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final StringBuilder eventLog = new StringBuilder();
    private String lastUrl = "";
    private String latestSummary = "DOM: waiting";
    private long probeSequence = 0L;

    private String scanStatus = "NOT_RUN";
    private final List<String> modelItems = new ArrayList<>();
    private final List<String> addItems = new ArrayList<>();
    private final List<String> toolItems = new ArrayList<>();

    private ValueCallback<Uri[]> pendingFileCallback;
    private String fileChooserStatus = "NOT_RUN";
    private String fileAcceptTypes = "-";
    private boolean fileMultipleAllowed = false;
    private int fileSelectedCount = 0;
    private String fileSelectedMimeTypes = "-";
    private int latestAttachmentHints = -1;

    private String draftStatus = "NOT_RUN";
    private String draftCid = "-";
    private String draftHash = "-";
    private int draftBaselineUserCount = -1;
    private String draftBaselineUserHash = "-";
    private int draftBaselineAssistantCount = -1;
    private String draftBaselineAssistantHash = "-";

    private String sendStatus = "IDLE";
    private String sendPhase = "IDLE";
    private String sendRunId = "-";
    private String sendCid = "-";
    private String sendDraftHash = "-";
    private int sendBaselineUserCount = -1;
    private String sendBaselineUserHash = "-";
    private int sendBaselineAssistantCount = -1;
    private String sendBaselineAssistantHash = "-";
    private String sendLastAssistantHash = "-";
    private int sendLastAssistantCount = -1;
    private int sendStableSamples = 0;
    private boolean sendSawUiStreaming = false;
    private boolean sendSawAssistantEvolution = false;
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
        restoreClaimJournal();

        getWindow().setStatusBarColor(Color.WHITE);
        getWindow().setNavigationBarColor(Color.WHITE);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);

        CookieManager cookieManager = CookieManager.getInstance();
        cookieManager.setAcceptCookie(true);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setFitsSystemWindows(true);

        Space topGap = new Space(this);
        root.addView(topGap, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(8)));

        LinearLayout row1 = new LinearLayout(this);
        row1.setOrientation(LinearLayout.HORIZONTAL);
        row1.addView(button("HOME", new View.OnClickListener() {
            @Override public void onClick(View v) { webView.loadUrl("https://chatgpt.com/"); }
        }), weighted());
        row1.addView(button("SCAN", new View.OnClickListener() {
            @Override public void onClick(View v) { beginMenuScan(); }
        }), weighted());
        row1.addView(button("READ TESTS", new View.OnClickListener() {
            @Override public void onClick(View v) {
                startActivity(new Intent(CapabilitySuiteActivity.this, MainActivity.class));
            }
        }), weighted());
        row1.addView(button("RELOAD", new View.OnClickListener() {
            @Override public void onClick(View v) { webView.reload(); }
        }), weighted());
        root.addView(row1, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(44)));

        draftInput = new EditText(this);
        draftInput.setSingleLine(false);
        draftInput.setMaxLines(3);
        draftInput.setTextSize(13f);
        draftInput.setHint("Type a normal draft here. DRAFT sets it; SEND ONCE never runs before verification.");
        draftInput.setPadding(dp(8), dp(4), dp(8), dp(4));
        root.addView(draftInput, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(62)));

        LinearLayout row2 = new LinearLayout(this);
        row2.setOrientation(LinearLayout.HORIZONTAL);
        row2.addView(button("DRAFT", new View.OnClickListener() {
            @Override public void onClick(View v) { beginDraftSet(); }
        }), weighted());
        row2.addView(button("SEND ONCE", new View.OnClickListener() {
            @Override public void onClick(View v) { beginGuardedSend(); }
        }), weighted());
        row2.addView(button("DOWNLOAD", new View.OnClickListener() {
            @Override public void onClick(View v) { downloadReport(); }
        }), weighted());
        root.addView(row2, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(46)));

        statusView = new TextView(this);
        statusView.setTextSize(10.5f);
        statusView.setTextIsSelectable(true);
        statusView.setPadding(dp(8), dp(5), dp(8), dp(5));
        ScrollView statusScroll = new ScrollView(this);
        statusScroll.addView(statusView, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT,
                ScrollView.LayoutParams.WRAP_CONTENT));
        root.addView(statusScroll, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(225)));

        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setLoadWithOverviewMode(false);
        settings.setUseWideViewPort(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(true);
        cookieManager.setAcceptThirdPartyCookies(webView, true);

        webView.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onShowFileChooser(WebView view,
                                                       ValueCallback<Uri[]> filePathCallback,
                                                       FileChooserParams fileChooserParams) {
                if (pendingFileCallback != null) pendingFileCallback.onReceiveValue(null);
                pendingFileCallback = filePathCallback;
                fileChooserStatus = "REQUESTED";
                fileSelectedCount = 0;
                fileSelectedMimeTypes = "-";
                fileMultipleAllowed = fileChooserParams != null
                        && fileChooserParams.getMode() == FileChooserParams.MODE_OPEN_MULTIPLE;
                String[] types = fileChooserParams == null ? null : fileChooserParams.getAcceptTypes();
                fileAcceptTypes = sanitizeAcceptTypes(types);
                recordEvent("FILE_CHOOSER_REQUESTED");
                renderStatus(webView == null ? "-" : webView.getUrl());
                try {
                    Intent intent = fileChooserParams == null
                            ? fallbackFileIntent() : fileChooserParams.createIntent();
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
        b.setTextSize(10f);
        b.setOnClickListener(listener);
        return b;
    }

    private LinearLayout.LayoutParams weighted() {
        return new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f);
    }

    private void probeOnce() {
        if (webView == null) return;
        final String nativeUrl = safe(webView.getUrl());
        if (!nativeUrl.equals(lastUrl)) {
            lastUrl = nativeUrl;
            recordRoute("URL_CHANGE", nativeUrl);
        }
        if (!"IDLE".equals(sendPhase) && sendStartedAt > 0L
                && System.currentTimeMillis() - sendStartedAt > 300000L) {
            markSendUncertain("UNCERTAIN_TIMEOUT");
        }
        final long seq = ++probeSequence;
        webView.evaluateJavascript(snapshotJs(), new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                if (seq < probeSequence - 3) return;
                try {
                    Snapshot s = parseSnapshot(value);
                    latestSummary = s.summary;
                    latestAttachmentHints = s.attachmentHints;
                    driveSendReceipt(s, nativeUrl);
                    reconcileRecoveredClaim(s, nativeUrl);
                } catch (Exception e) {
                    latestSummary = "DOM_PARSE_ERROR: " + e.getClass().getSimpleName();
                }
                renderStatus(nativeUrl);
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
                + "const stopControls=controls.filter(e=>{const x=(label(e)+' '+(e.getAttribute('data-testid')||'')).toLowerCase();return x.includes('stop generating')||x.includes('stop response')||x.includes('stop-generating')||x==='stop';}).length;"
                + "const busyNodes=qa('[aria-busy=\\\"true\\\"]').filter(vis).length;"
                + "const responseActions=qa('[aria-label=\\\"Response actions\\\" i]').filter(vis).length;"
                + "const composer=document.querySelector('#prompt-textarea')||qa('textarea,[contenteditable=\\\"true\\\"]').filter(vis).slice(-1)[0]||null;"
                + "const composerText=composer?norm(('value' in composer?composer.value:(composer.innerText||composer.textContent))):'';"
                + "const attachmentHints=qa('[data-testid*=\\\"attachment\\\" i],[aria-label*=\\\"remove file\\\" i],[aria-label*=\\\"remove attachment\\\" i],[data-testid*=\\\"file-pill\\\" i]').filter(vis).length;"
                + "const sendButtons=controls.filter(e=>{const x=(label(e)+' '+(e.getAttribute('data-testid')||'')).toLowerCase();return (x.includes('send')||x.includes('submit'))&&!x.includes('share');});"
                + "return JSON.stringify({href:location.href,title:document.title,ready:document.readyState,users:users,assistants:assistants,stopControls:stopControls,busyNodes:busyNodes,responseActions:responseActions,composerText:composerText,attachmentHints:attachmentHints,sendButtons:sendButtons.length});"
                + "}catch(e){return JSON.stringify({error:String(e),href:String(location.href),users:[],assistants:[],composerText:''});}})();";
    }

    private Snapshot parseSnapshot(String value) throws Exception {
        JSONObject o = jsonObject(value);
        Fingerprint users = fingerprintArray(o.optJSONArray("users"));
        Fingerprint assistants = fingerprintArray(o.optJSONArray("assistants"));
        String composerText = normalize(o.optString("composerText", ""));
        String composerHash = composerText.isEmpty() ? "-" : sha256(composerText);
        int stop = o.optInt("stopControls", -1);
        int busy = o.optInt("busyNodes", -1);
        int responseActions = o.optInt("responseActions", -1);
        int attachments = o.optInt("attachmentHints", -1);
        int sendButtons = o.optInt("sendButtons", -1);
        StringBuilder summary = new StringBuilder();
        summary.append("TITLE: ").append(o.optString("title", "-")).append('\n');
        summary.append("READY: ").append(o.optString("ready", "-")).append('\n');
        summary.append("MESSAGES: user=").append(users.count)
                .append(" assistant=").append(assistants.count).append('\n');
        summary.append("STREAM: stop=").append(stop).append(" busy=").append(busy)
                .append(" responseActions=").append(responseActions).append('\n');
        summary.append("COMPOSER: hash=").append(shortHash(composerHash))
                .append(" sendButtons=").append(sendButtons).append('\n');
        summary.append("ATTACHMENT_HINTS: ").append(attachments);
        if (o.has("error")) summary.append("\nJS_ERROR: ").append(o.optString("error"));
        return new Snapshot(users, assistants, composerHash, stop, busy,
                responseActions, attachments, sendButtons, summary.toString());
    }

    private void beginMenuScan() {
        if (webView == null) return;
        scanStatus = "SCANNING_MODEL";
        modelItems.clear();
        addItems.clear();
        toolItems.clear();
        openSemanticMenu("model", new Runnable() {
            @Override public void run() {
                collectVisibleMenuItems(modelItems, new Runnable() {
                    @Override public void run() {
                        closeSemanticMenu("model");
                        handler.postDelayed(new Runnable() {
                            @Override public void run() { scanAddMenu(); }
                        }, 180L);
                    }
                });
            }
        });
    }

    private void scanAddMenu() {
        scanStatus = "SCANNING_ADD";
        openSemanticMenu("add", new Runnable() {
            @Override public void run() {
                collectVisibleMenuItems(addItems, new Runnable() {
                    @Override public void run() {
                        closeSemanticMenu("add");
                        handler.postDelayed(new Runnable() {
                            @Override public void run() { scanToolMenu(); }
                        }, 180L);
                    }
                });
            }
        });
    }

    private void scanToolMenu() {
        scanStatus = "SCANNING_TOOLS";
        openSemanticMenu("tools", new Runnable() {
            @Override public void run() {
                collectVisibleMenuItems(toolItems, new Runnable() {
                    @Override public void run() {
                        closeSemanticMenu("tools");
                        scanStatus = "COMPLETE";
                        recordEvent("MENU_SCAN_COMPLETE");
                        renderStatus(webView == null ? "-" : webView.getUrl());
                        Toast.makeText(CapabilitySuiteActivity.this,
                                "Menu scan complete", Toast.LENGTH_SHORT).show();
                    }
                });
            }
        });
    }

    private void openSemanticMenu(final String kind, final Runnable afterOpen) {
        String js = semanticButtonClickJs(kind);
        webView.evaluateJavascript(js, new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                try {
                    JSONObject o = jsonObject(value);
                    int count = o.optInt("count", 0);
                    boolean clicked = o.optBoolean("clicked", false);
                    recordEvent("MENU_OPEN_" + kind.toUpperCase(Locale.US)
                            + "_COUNT_" + count + "_CLICKED_" + clicked);
                    if (!clicked) {
                        if ("tools".equals(kind)) {
                            scanStatus = "TOOLS_CONTROL_NOT_VISIBLE";
                            toolItems.clear();
                            handler.postDelayed(afterOpen, 50L);
                        } else {
                            scanStatus = "PARTIAL_" + kind.toUpperCase(Locale.US) + "_NOT_FOUND";
                            handler.postDelayed(afterOpen, 50L);
                        }
                        return;
                    }
                    handler.postDelayed(afterOpen, 350L);
                } catch (Exception e) {
                    scanStatus = "FAIL_" + kind.toUpperCase(Locale.US) + "_PARSE";
                    handler.postDelayed(afterOpen, 50L);
                }
                renderStatus(webView == null ? "-" : webView.getUrl());
            }
        });
    }

    private String semanticButtonClickJs(String kind) {
        String mode = JSONObject.quote(kind);
        return "(function(){try{"
                + "const kind=" + mode + ";"
                + "const vis=(e)=>{const r=e.getBoundingClientRect();const s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';};"
                + "const norm=(x)=>(x||'').replace(/\\s+/g,' ').trim().toLowerCase();"
                + "const label=(e)=>norm(e.getAttribute('aria-label')||e.innerText||e.textContent||'');"
                + "let c=Array.from(document.querySelectorAll('button,[role=\\\"button\\\"]')).filter(vis);"
                + "if(kind==='model')c=c.filter(e=>label(e)==='model selector'||label(e).includes('model selector'));"
                + "else if(kind==='add')c=c.filter(e=>label(e)==='add files and more'||label(e).includes('add files'));"
                + "else c=c.filter(e=>label(e)==='tools'||label(e).includes('tools'));"
                + "if(c.length===1){c[0].click();return JSON.stringify({count:1,clicked:true});}"
                + "return JSON.stringify({count:c.length,clicked:false});"
                + "}catch(e){return JSON.stringify({count:0,clicked:false,error:String(e)});}})();";
    }

    private void collectVisibleMenuItems(final List<String> target, final Runnable done) {
        String js = "(function(){try{"
                + "const vis=(e)=>{const r=e.getBoundingClientRect();const s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';};"
                + "const norm=(x)=>(x||'').replace(/\\s+/g,' ').trim();"
                + "const nodes=Array.from(document.querySelectorAll('[role=\\\"menuitem\\\"],[role=\\\"menuitemradio\\\"],[role=\\\"option\\\"],[data-radix-collection-item]')).filter(vis);"
                + "const items=[];for(const e of nodes){const x=norm(e.getAttribute('aria-label')||e.innerText||e.textContent||'');if(x&&x.length<=120&&!x.includes('@')&&!items.includes(x))items.push(x);if(items.length>=40)break;}"
                + "return JSON.stringify({items:items});"
                + "}catch(e){return JSON.stringify({items:[],error:String(e)});}})();";
        webView.evaluateJavascript(js, new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                target.clear();
                try {
                    JSONArray arr = jsonObject(value).optJSONArray("items");
                    if (arr != null) {
                        Set<String> unique = new LinkedHashSet<>();
                        for (int i = 0; i < arr.length(); i++) {
                            String item = normalize(arr.optString(i, ""));
                            if (!item.isEmpty()) unique.add(item);
                        }
                        target.addAll(unique);
                    }
                } catch (Exception ignored) { }
                done.run();
            }
        });
    }

    private void closeSemanticMenu(String kind) {
        if (webView == null) return;
        webView.evaluateJavascript(semanticButtonClickJs(kind), null);
    }

    private void beginDraftSet() {
        if (webView == null) return;
        if (isUnresolvedClaim()) {
            Toast.makeText(this, "A previous Send claim is unresolved; no new mutation is allowed.",
                    Toast.LENGTH_LONG).show();
            return;
        }
        final String raw = draftInput.getText() == null ? "" : draftInput.getText().toString();
        final String normalized = normalize(raw);
        if (normalized.isEmpty()) {
            draftStatus = "FAIL_EMPTY_INPUT";
            renderStatus(webView.getUrl());
            return;
        }
        final String cid = extractCanonicalConversationId(sanitizeUrl(webView.getUrl()));
        if ("-".equals(cid)) {
            draftStatus = "FAIL_NO_CANONICAL_CHAT";
            renderStatus(webView.getUrl());
            return;
        }
        draftStatus = "SETTING";
        try {
            draftHash = sha256(normalized);
        } catch (Exception e) {
            draftStatus = "FAIL_HASH";
            return;
        }
        draftCid = cid;
        final String quoted = JSONObject.quote(raw);
        String js = "(function(){try{"
                + "const text=" + quoted + ";"
                + "const vis=(e)=>{const r=e.getBoundingClientRect();const s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';};"
                + "const c=document.querySelector('#prompt-textarea')||Array.from(document.querySelectorAll('textarea,[contenteditable=\\\"true\\\"]')).filter(vis).slice(-1)[0];"
                + "if(!c)return JSON.stringify({ok:false,reason:'NO_COMPOSER'});"
                + "c.focus();"
                + "if(c instanceof HTMLTextAreaElement||c instanceof HTMLInputElement){const p=Object.getPrototypeOf(c);const d=Object.getOwnPropertyDescriptor(p,'value');if(d&&d.set)d.set.call(c,text);else c.value=text;}"
                + "else{try{document.execCommand('selectAll',false,null);document.execCommand('insertText',false,text);}catch(x){c.textContent=text;}}"
                + "c.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText',data:text}));"
                + "c.dispatchEvent(new Event('change',{bubbles:true}));"
                + "return JSON.stringify({ok:true});"
                + "}catch(e){return JSON.stringify({ok:false,reason:String(e)});}})();";
        webView.evaluateJavascript(js, new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                boolean ok = false;
                try { ok = jsonObject(value).optBoolean("ok", false); } catch (Exception ignored) { }
                if (!ok) {
                    draftStatus = "FAIL_SET";
                    recordEvent("DRAFT_SET_FAIL");
                    renderStatus(webView.getUrl());
                    return;
                }
                handler.postDelayed(new Runnable() {
                    @Override public void run() { verifyDraftReceipt(); }
                }, 450L);
            }
        });
    }

    private void verifyDraftReceipt() {
        if (webView == null) return;
        final String currentCid = extractCanonicalConversationId(sanitizeUrl(webView.getUrl()));
        webView.evaluateJavascript(snapshotJs(), new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                try {
                    Snapshot s = parseSnapshot(value);
                    if (!draftCid.equals(currentCid)) {
                        draftStatus = "FAIL_ROUTE_CHANGED";
                    } else if (!draftHash.equals(s.composerHash)) {
                        draftStatus = "FAIL_COMPOSER_HASH_MISMATCH";
                    } else {
                        draftBaselineUserCount = s.users.count;
                        draftBaselineUserHash = s.users.hash;
                        draftBaselineAssistantCount = s.assistants.count;
                        draftBaselineAssistantHash = s.assistants.hash;
                        draftStatus = "VERIFIED";
                        recordEvent("DRAFT_VERIFIED");
                        Toast.makeText(CapabilitySuiteActivity.this,
                                "Draft verified. SEND ONCE is now eligible.", Toast.LENGTH_LONG).show();
                    }
                } catch (Exception e) {
                    draftStatus = "FAIL_VERIFY_PARSE";
                }
                renderStatus(webView == null ? "-" : webView.getUrl());
            }
        });
    }

    private void beginGuardedSend() {
        if (webView == null) return;
        if (isUnresolvedClaim()) {
            Toast.makeText(this, "Previous durable claim unresolved; no replay allowed.",
                    Toast.LENGTH_LONG).show();
            return;
        }
        if (!"VERIFIED".equals(draftStatus)) {
            sendStatus = "BLOCKED_DRAFT_NOT_VERIFIED";
            renderStatus(webView.getUrl());
            return;
        }
        final String cid = extractCanonicalConversationId(sanitizeUrl(webView.getUrl()));
        if (!draftCid.equals(cid)) {
            sendStatus = "BLOCKED_ROUTE_MISMATCH";
            return;
        }
        webView.evaluateJavascript(snapshotJs(), new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                try {
                    Snapshot s = parseSnapshot(value);
                    boolean guard = draftHash.equals(s.composerHash)
                            && s.users.count == draftBaselineUserCount
                            && safeEq(s.users.hash, draftBaselineUserHash)
                            && s.assistants.count == draftBaselineAssistantCount
                            && safeEq(s.assistants.hash, draftBaselineAssistantHash);
                    if (!guard) {
                        sendStatus = "BLOCKED_PRE_SEND_GUARD_MISMATCH";
                        renderStatus(webView.getUrl());
                        return;
                    }
                    persistClaim(cid, s);
                    clickSendExactlyOnce();
                } catch (Exception e) {
                    sendStatus = "BLOCKED_PRE_SEND_PARSE";
                    renderStatus(webView.getUrl());
                }
            }
        });
    }

    private void persistClaim(String cid, Snapshot s) {
        sendRunId = UUID.randomUUID().toString();
        sendCid = cid;
        sendDraftHash = draftHash;
        sendBaselineUserCount = s.users.count;
        sendBaselineUserHash = s.users.hash;
        sendBaselineAssistantCount = s.assistants.count;
        sendBaselineAssistantHash = s.assistants.hash;
        sendStatus = "CLAIMED";
        sendPhase = "CLAIMED";
        sendStartedAt = System.currentTimeMillis();
        boolean committed = prefs.edit()
                .putString("state", "CLAIMED")
                .putString("run_id", sendRunId)
                .putString("cid", sendCid)
                .putString("draft_hash", sendDraftHash)
                .putInt("baseline_user_count", sendBaselineUserCount)
                .putString("baseline_user_hash", sendBaselineUserHash)
                .putInt("baseline_assistant_count", sendBaselineAssistantCount)
                .putString("baseline_assistant_hash", sendBaselineAssistantHash)
                .putLong("started_at", sendStartedAt)
                .commit();
        recordEvent(committed ? "SEND_DURABLE_CLAIMED" : "SEND_CLAIM_COMMIT_FAIL");
        if (!committed) {
            sendStatus = "BLOCKED_CLAIM_PERSIST_FAIL";
            sendPhase = "IDLE";
        }
    }

    private void clickSendExactlyOnce() {
        if (!"CLAIMED".equals(sendPhase)) return;
        String js = "(function(){try{"
                + "const vis=(e)=>{const r=e.getBoundingClientRect();const s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';};"
                + "const norm=(x)=>(x||'').replace(/\\s+/g,' ').trim().toLowerCase();"
                + "const label=(e)=>norm(e.getAttribute('aria-label')||e.getAttribute('title')||e.innerText||e.textContent||'');"
                + "let c=Array.from(document.querySelectorAll('button')).filter(vis).filter(e=>{const x=label(e)+' '+norm(e.getAttribute('data-testid'));return (x.includes('send')||x.includes('submit'))&&!x.includes('share')&&!e.disabled;});"
                + "if(c.length!==1)return JSON.stringify({count:c.length,clicked:false});"
                + "c[0].click();return JSON.stringify({count:1,clicked:true});"
                + "}catch(e){return JSON.stringify({count:0,clicked:false,error:String(e)});}})();";
        webView.evaluateJavascript(js, new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                try {
                    JSONObject o = jsonObject(value);
                    int count = o.optInt("count", 0);
                    boolean clicked = o.optBoolean("clicked", false);
                    if (count == 1 && clicked) {
                        sendStatus = "AWAITING_USER_RECEIPT";
                        sendPhase = "WAIT_USER";
                        sendStableSamples = 0;
                        sendSawUiStreaming = false;
                        sendSawAssistantEvolution = false;
                        sendLastAssistantHash = "-";
                        sendLastAssistantCount = -1;
                        prefs.edit().putString("state", "AWAITING_RECEIPT").commit();
                        recordEvent("SEND_SINGLE_CLICK_DISPATCHED");
                    } else {
                        markSendUncertain("UNCERTAIN_SEND_BUTTON_COUNT_" + count);
                    }
                } catch (Exception e) {
                    markSendUncertain("UNCERTAIN_CLICK_RESULT_PARSE");
                }
                renderStatus(webView == null ? "-" : webView.getUrl());
            }
        });
    }

    private void driveSendReceipt(Snapshot s, String rawUrl) {
        if ("IDLE".equals(sendPhase) || "CLAIMED".equals(sendPhase)) return;
        if (!sendCid.equals(extractCanonicalConversationId(sanitizeUrl(rawUrl)))) {
            markSendUncertain("UNCERTAIN_ROUTE_CHANGED");
            return;
        }
        boolean uiStreaming = s.stopControls > 0 || s.busyNodes > 0;
        if (uiStreaming) sendSawUiStreaming = true;

        if ("WAIT_USER".equals(sendPhase)) {
            if (s.users.count == sendBaselineUserCount + 1
                    && sendDraftHash.equals(s.users.lastHash)) {
                sendPhase = "WAIT_ASSISTANT";
                sendStatus = "USER_RECEIPT_CONFIRMED";
                recordEvent("SEND_USER_RECEIPT_CONFIRMED");
            } else if (s.users.count > sendBaselineUserCount + 1
                    || (s.users.count == sendBaselineUserCount + 1
                    && !sendDraftHash.equals(s.users.lastHash))) {
                markSendUncertain("UNCERTAIN_USER_RECEIPT_MISMATCH");
            }
            return;
        }

        if ("WAIT_ASSISTANT".equals(sendPhase)) {
            boolean assistantChanged = s.assistants.count > sendBaselineAssistantCount
                    || !safeEq(s.assistants.hash, sendBaselineAssistantHash);
            if (assistantChanged && s.assistants.count > 0) {
                sendPhase = "OBSERVING";
                sendStatus = uiStreaming ? "ASSISTANT_STREAMING" : "ASSISTANT_CHANGE_SEEN";
                sendLastAssistantCount = s.assistants.count;
                sendLastAssistantHash = s.assistants.hash;
                sendStableSamples = 0;
                recordEvent("SEND_ASSISTANT_CHANGE_SEEN");
            }
            return;
        }

        if (!"OBSERVING".equals(sendPhase)) return;
        boolean assistantChangedAgain = s.assistants.count != sendLastAssistantCount
                || !safeEq(s.assistants.hash, sendLastAssistantHash);
        if (assistantChangedAgain) {
            if (!"-".equals(sendLastAssistantHash)) sendSawAssistantEvolution = true;
            sendLastAssistantCount = s.assistants.count;
            sendLastAssistantHash = s.assistants.hash;
            sendStableSamples = 0;
            sendStatus = uiStreaming ? "ASSISTANT_STREAMING" : "ASSISTANT_EVOLVING";
            return;
        }
        if (uiStreaming) {
            sendStableSamples = 0;
            sendStatus = "ASSISTANT_STREAMING";
            return;
        }
        boolean assistantReceipt = s.assistants.count > sendBaselineAssistantCount
                && !safeEq(s.assistants.hash, sendBaselineAssistantHash)
                && s.responseActions > 0;
        if (assistantReceipt) {
            sendStableSamples++;
            sendStatus = "STABILIZING_" + sendStableSamples;
            if (sendStableSamples >= 4) confirmSend();
        } else {
            sendStableSamples = 0;
            sendStatus = "WAITING_ASSISTANT_COMPLETE_EVIDENCE";
        }
    }

    private void confirmSend() {
        sendStatus = "CONFIRMED";
        sendPhase = "IDLE";
        prefs.edit().putString("state", "CONFIRMED").commit();
        recordEvent("SEND_CONFIRMED");
        draftStatus = "CONSUMED_BY_CONFIRMED_SEND";
        Toast.makeText(this, "Guarded Send CONFIRMED", Toast.LENGTH_LONG).show();
    }

    private void markSendUncertain(String status) {
        if (status == null) status = "UNCERTAIN";
        sendStatus = status;
        sendPhase = "IDLE";
        prefs.edit().putString("state", "UNCERTAIN").putString("uncertain_status", status).commit();
        recordEvent(status);
        renderStatus(webView == null ? "-" : webView.getUrl());
    }

    private void restoreClaimJournal() {
        String state = prefs.getString("state", "IDLE");
        if ("CLAIMED".equals(state) || "AWAITING_RECEIPT".equals(state)) {
            sendStatus = "RECOVERING_PREVIOUS_" + state;
            sendPhase = "RECOVERING";
            sendRunId = prefs.getString("run_id", "-");
            sendCid = prefs.getString("cid", "-");
            sendDraftHash = prefs.getString("draft_hash", "-");
            sendBaselineUserCount = prefs.getInt("baseline_user_count", -1);
            sendBaselineUserHash = prefs.getString("baseline_user_hash", "-");
            sendBaselineAssistantCount = prefs.getInt("baseline_assistant_count", -1);
            sendBaselineAssistantHash = prefs.getString("baseline_assistant_hash", "-");
            sendStartedAt = prefs.getLong("started_at", 0L);
        } else if ("UNCERTAIN".equals(state)) {
            sendStatus = prefs.getString("uncertain_status", "UNCERTAIN_PREVIOUS_CLAIM");
            sendPhase = "IDLE";
        } else if ("CONFIRMED".equals(state)) {
            sendStatus = "PREVIOUS_RUN_CONFIRMED";
            sendPhase = "IDLE";
        }
    }

    private void reconcileRecoveredClaim(Snapshot s, String rawUrl) {
        if (!"RECOVERING".equals(sendPhase)) return;
        String cid = extractCanonicalConversationId(sanitizeUrl(rawUrl));
        if (!sendCid.equals(cid)) return;
        boolean exactUserReceipt = s.users.count == sendBaselineUserCount + 1
                && sendDraftHash.equals(s.users.lastHash);
        boolean assistantReceipt = s.assistants.count > sendBaselineAssistantCount
                && !safeEq(s.assistants.hash, sendBaselineAssistantHash)
                && s.stopControls == 0 && s.busyNodes == 0 && s.responseActions > 0;
        if (exactUserReceipt && assistantReceipt) {
            sendStatus = "CONFIRMED_RECOVERED_READ_ONLY";
            sendPhase = "IDLE";
            prefs.edit().putString("state", "CONFIRMED").commit();
            recordEvent("SEND_CONFIRMED_RECOVERED_READ_ONLY");
        } else if (System.currentTimeMillis() - sendStartedAt > 30000L) {
            markSendUncertain("UNCERTAIN_PREVIOUS_CLAIM_NO_REPLAY");
        }
    }

    private boolean isUnresolvedClaim() {
        String state = prefs.getString("state", "IDLE");
        return "CLAIMED".equals(state) || "AWAITING_RECEIPT".equals(state)
                || "UNCERTAIN".equals(state) || "RECOVERING".equals(sendPhase);
    }

    private Intent fallbackFileIntent() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
        return intent;
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != FILE_CHOOSER_REQUEST) return;
        Uri[] results = extractUris(resultCode, data);
        fileSelectedCount = results == null ? 0 : results.length;
        fileSelectedMimeTypes = mimeTypesFor(results);
        fileChooserStatus = fileSelectedCount > 0 ? "SELECTED" : "CANCELED";
        recordEvent(fileSelectedCount > 0 ? "FILE_CHOOSER_SELECTED" : "FILE_CHOOSER_CANCELED");
        if (pendingFileCallback != null) pendingFileCallback.onReceiveValue(results);
        pendingFileCallback = null;
        renderStatus(webView == null ? "-" : webView.getUrl());
    }

    private Uri[] extractUris(int resultCode, Intent data) {
        if (resultCode != RESULT_OK || data == null) return null;
        List<Uri> uris = new ArrayList<>();
        ClipData clip = data.getClipData();
        if (clip != null) {
            for (int i = 0; i < clip.getItemCount(); i++) {
                Uri u = clip.getItemAt(i).getUri();
                if (u != null) uris.add(u);
            }
        } else if (data.getData() != null) {
            uris.add(data.getData());
        }
        return uris.isEmpty() ? null : uris.toArray(new Uri[0]);
    }

    private String mimeTypesFor(Uri[] uris) {
        if (uris == null || uris.length == 0) return "-";
        Set<String> types = new LinkedHashSet<>();
        for (Uri uri : uris) {
            String type = null;
            try { type = getContentResolver().getType(uri); } catch (Exception ignored) { }
            if (type != null && !type.trim().isEmpty()) types.add(type.trim());
        }
        return types.isEmpty() ? "unknown" : join(types, ",");
    }

    private String sanitizeAcceptTypes(String[] types) {
        if (types == null || types.length == 0) return "-";
        Set<String> clean = new LinkedHashSet<>();
        for (String t : types) {
            if (t == null) continue;
            String x = t.trim();
            if (!x.isEmpty() && x.length() <= 80) clean.add(x);
        }
        return clean.isEmpty() ? "-" : join(clean, ",");
    }

    private void renderStatus(String rawUrl) {
        String sanitized = sanitizeUrl(rawUrl);
        String cid = extractCanonicalConversationId(sanitized);
        StringBuilder s = new StringBuilder();
        s.append("Stable v0.6 Capability Suite\n");
        s.append("CID: ").append(cid).append('\n');
        s.append("SCAN: ").append(scanStatus)
                .append(" model=").append(modelItems.size())
                .append(" add=").append(addItems.size())
                .append(" tools=").append(toolItems.size()).append('\n');
        s.append("FILE: ").append(fileChooserStatus)
                .append(" selected=").append(fileSelectedCount)
                .append(" domHints=").append(latestAttachmentHints).append('\n');
        s.append("DRAFT: ").append(draftStatus)
                .append(" hash=").append(shortHash(draftHash)).append('\n');
        s.append("SEND: ").append(sendStatus)
                .append(" stable=").append(sendStableSamples).append('\n');
        s.append(latestSummary).append('\n');
        s.append("EVENTS: ").append(countEvents()).append(" (DOWNLOAD for full sanitized report)");
        statusView.setText(s.toString());
    }

    private String buildReport() {
        String current = sanitizeUrl(webView == null ? null : webView.getUrl());
        String cid = extractCanonicalConversationId(current);
        return "CHATGPT_WEBVIEW_STABLE_V06_CAPABILITY_SUITE\n"
                + "CURRENT_URL=" + current + "\n"
                + "CURRENT_CONVERSATION_ID=" + cid + "\n"
                + "MENU_SCAN_STATUS=" + scanStatus + "\n"
                + "MODEL_MENU_ITEMS=" + safeList(modelItems) + "\n"
                + "ADD_MENU_ITEMS=" + safeList(addItems) + "\n"
                + "TOOLS_MENU_ITEMS=" + safeList(toolItems) + "\n"
                + "FILE_CHOOSER_STATUS=" + fileChooserStatus + "\n"
                + "FILE_ACCEPT_TYPES=" + fileAcceptTypes + "\n"
                + "FILE_MULTIPLE_ALLOWED=" + fileMultipleAllowed + "\n"
                + "FILE_SELECTED_COUNT=" + fileSelectedCount + "\n"
                + "FILE_SELECTED_MIME_TYPES=" + fileSelectedMimeTypes + "\n"
                + "DOM_ATTACHMENT_HINTS=" + latestAttachmentHints + "\n"
                + "DRAFT_STATUS=" + draftStatus + "\n"
                + "DRAFT_SHA256=" + draftHash + "\n"
                + "DRAFT_BASELINE_USER_COUNT=" + draftBaselineUserCount + "\n"
                + "DRAFT_BASELINE_USER_SHA256=" + draftBaselineUserHash + "\n"
                + "DRAFT_BASELINE_ASSISTANT_COUNT=" + draftBaselineAssistantCount + "\n"
                + "DRAFT_BASELINE_ASSISTANT_SHA256=" + draftBaselineAssistantHash + "\n"
                + "SEND_STATUS=" + sendStatus + "\n"
                + "SEND_RUN_ID=" + sendRunId + "\n"
                + "SEND_DRAFT_SHA256=" + sendDraftHash + "\n"
                + "SEND_BASELINE_USER_COUNT=" + sendBaselineUserCount + "\n"
                + "SEND_BASELINE_ASSISTANT_COUNT=" + sendBaselineAssistantCount + "\n"
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
        String timestamp = new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date());
        String fileName = "chatgpt-webview-v06-report-" + timestamp + ".txt";
        ContentValues values = new ContentValues();
        values.put(MediaStore.MediaColumns.DISPLAY_NAME, fileName);
        values.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
        values.put(MediaStore.MediaColumns.RELATIVE_PATH,
                Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
        values.put(MediaStore.MediaColumns.IS_PENDING, 1);
        Uri collection = MediaStore.Downloads.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY);
        Uri item = null;
        try {
            item = getContentResolver().insert(collection, values);
            if (item == null) throw new IllegalStateException("MediaStore insert returned null");
            try (OutputStream out = getContentResolver().openOutputStream(item, "w")) {
                if (out == null) throw new IllegalStateException("Output stream unavailable");
                out.write(buildReport().getBytes(StandardCharsets.UTF_8));
                out.flush();
            }
            ContentValues done = new ContentValues();
            done.put(MediaStore.MediaColumns.IS_PENDING, 0);
            getContentResolver().update(item, done, null, null);
            Toast.makeText(this, "Downloaded: Downloads/ChatGPTWebViewProbe/" + fileName,
                    Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            if (item != null) getContentResolver().delete(item, null, null);
            Toast.makeText(this, "Download failed: " + e.getClass().getSimpleName(),
                    Toast.LENGTH_LONG).show();
        }
    }

    private JSONObject jsonObject(String value) throws Exception {
        Object outer = new JSONTokener(value).nextValue();
        String json = outer instanceof String ? (String) outer : String.valueOf(outer);
        return new JSONObject(json);
    }

    private Fingerprint fingerprintArray(JSONArray array) throws Exception {
        if (array == null || array.length() == 0) return new Fingerprint(0, "-", "-");
        StringBuilder joined = new StringBuilder();
        int count = 0;
        String last = "";
        for (int i = 0; i < array.length(); i++) {
            String text = normalize(array.optString(i, ""));
            if (text.isEmpty()) continue;
            if (count > 0) joined.append('\u001e');
            joined.append(text);
            last = text;
            count++;
        }
        if (count == 0) return new Fingerprint(0, "-", "-");
        return new Fingerprint(count, sha256(joined.toString()), sha256(last));
    }

    private void recordEvent(String kind) {
        recordRoute(kind, webView == null ? "-" : webView.getUrl());
    }

    private void recordRoute(String kind, String rawUrl) {
        String u = sanitizeUrl(rawUrl);
        String cid = extractCanonicalConversationId(u);
        String segment = extractRouteSegment(u);
        String reported = !"-".equals(cid) ? cid : (segment.startsWith("WEB:") ? "TRANSIENT" : "-");
        eventLog.append(kind).append(" | ").append(u).append(" | cid=").append(reported).append('\n');
        if (eventLog.length() > 24000) eventLog.delete(0, 7000);
    }

    private String sanitizeUrl(String rawUrl) {
        if (rawUrl == null || rawUrl.trim().isEmpty()) return "-";
        try {
            Uri uri = Uri.parse(rawUrl);
            String scheme = uri.getScheme();
            String host = uri.getHost();
            String path = uri.getEncodedPath();
            if (scheme == null || host == null) {
                int q = rawUrl.indexOf('?');
                int h = rawUrl.indexOf('#');
                int end = rawUrl.length();
                if (q >= 0) end = Math.min(end, q);
                if (h >= 0) end = Math.min(end, h);
                return rawUrl.substring(0, end);
            }
            return scheme + "://" + host + (path == null || path.isEmpty() ? "/" : path);
        } catch (Exception e) {
            return "-";
        }
    }

    private String extractRouteSegment(String url) {
        if (url == null) return "-";
        int marker = url.indexOf("/c/");
        if (marker < 0) return "-";
        int start = marker + 3;
        int end = url.length();
        int slash = url.indexOf('/', start);
        if (slash >= 0) end = slash;
        return end > start ? url.substring(start, end) : "-";
    }

    private String extractCanonicalConversationId(String url) {
        String segment = extractRouteSegment(url);
        return UUID_PATTERN.matcher(segment).matches() ? segment : "-";
    }

    private int countEvents() {
        int count = 0;
        for (int i = 0; i < eventLog.length(); i++) if (eventLog.charAt(i) == '\n') count++;
        return count;
    }

    private String normalize(String s) {
        return s == null ? "" : s.replaceAll("\\s+", " ").trim();
    }

    private String sha256(String value) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] bytes = digest.digest(value.getBytes(StandardCharsets.UTF_8));
        StringBuilder hex = new StringBuilder();
        for (byte b : bytes) hex.append(String.format(Locale.US, "%02x", b & 0xff));
        return hex.toString();
    }

    private String shortHash(String hash) {
        if (hash == null || "-".equals(hash)) return "-";
        return hash.length() <= 12 ? hash : hash.substring(0, 12);
    }

    private boolean safeEq(String a, String b) {
        return a == null ? b == null : a.equals(b);
    }

    private String safe(String s) { return s == null ? "-" : s; }

    private String safeList(List<String> items) {
        JSONArray arr = new JSONArray();
        for (String item : items) arr.put(item);
        return arr.toString();
    }

    private String join(Iterable<String> values, String separator) {
        StringBuilder b = new StringBuilder();
        for (String value : values) {
            if (b.length() > 0) b.append(separator);
            b.append(value);
        }
        return b.toString();
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    @Override public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
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
        final String lastHash;
        Fingerprint(int count, String hash, String lastHash) {
            this.count = count;
            this.hash = hash;
            this.lastHash = lastHash;
        }
    }

    private static final class Snapshot {
        final Fingerprint users;
        final Fingerprint assistants;
        final String composerHash;
        final int stopControls;
        final int busyNodes;
        final int responseActions;
        final int attachmentHints;
        final int sendButtons;
        final String summary;
        Snapshot(Fingerprint users, Fingerprint assistants, String composerHash,
                 int stopControls, int busyNodes, int responseActions,
                 int attachmentHints, int sendButtons, String summary) {
            this.users = users;
            this.assistants = assistants;
            this.composerHash = composerHash;
            this.stopControls = stopControls;
            this.busyNodes = busyNodes;
            this.responseActions = responseActions;
            this.attachmentHints = attachmentHints;
            this.sendButtons = sendButtons;
            this.summary = summary;
        }
    }
}
