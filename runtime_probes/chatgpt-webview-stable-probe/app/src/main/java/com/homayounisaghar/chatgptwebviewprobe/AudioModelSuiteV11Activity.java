package com.homayounisaghar.chatgptwebviewprobe;

import android.Manifest;
import android.content.ContentValues;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.provider.MediaStore;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.DownloadListener;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.OutputStream;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Pattern;

/**
 * Stable v0.11 diagnostic suite.
 *
 * Goals:
 * 1. Fix v0.10's FILE_ACTION alias problem by separating one semantic resource
 *    identity from one-or-more concrete DOM locators and clicking only a unique locator.
 * 2. Observe the full Dictation / Voice control state machine, including secondary
 *    controls that appear after activation, without retaining chat text or raw audio.
 * 3. Measure browser-event -> DOM-state transition timing so future watch routing can
 *    be compared against the direct-phone baseline.
 * 4. Census the live model selector and exercise one guarded model selection.
 */
public class AudioModelSuiteV11Activity extends ResourceSuiteV10FinalActivity {
    private static final int REQ_RECORD_AUDIO = 1101;
    private static final Pattern UUID_PATTERN = Pattern.compile(
            "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$");
    private static final String PREFS = "stable_v11_audio_model_suite";

    private final Handler handlerV11 = new Handler(Looper.getMainLooper());
    private final StringBuilder events = new StringBuilder();
    private final List<ResourceV11> resources = new ArrayList<>();
    private final List<String> modelOptions = new ArrayList<>();

    private WebView web;
    private TextView status;
    private EditText indexInput;
    private Button audioWatchButton;
    private SharedPreferences prefsV11;

    private String lastUrlV11 = "";
    private String currentCid = "-";

    private String resourceStatus = "NOT_RUN";
    private String resourceScanCid = "-";
    private String resourceActionStatus = "NOT_RUN";
    private String resourceCallbackMime = "-";
    private long resourceCallbackLength = -1L;
    private String resourceCallbackSafeUrl = "-";
    private String pendingResourceId = "-";
    private String pendingResourceLocator = "-";
    private String pendingResourceCid = "-";
    private long pendingResourceStartedAt = 0L;
    private boolean pendingResourceDownload = false;

    private boolean audioWatch = false;
    private long audioLeaseUntil = 0L;
    private String audioPermissionStatus = "NOT_REQUESTED";
    private String audioPermissionOrigin = "-";
    private int audioPermissionRequestCount = 0;
    private String audioState = "NOT_WATCHING";
    private String audioControlSignature = "-";
    private int audioLastEventSeq = -1;
    private String audioLastEventCategory = "-";
    private double audioLastEventToSnapshotMs = -1d;
    private int audioStateTransitions = 0;

    private String modelStatus = "NOT_RUN";
    private String modelScanCid = "-";
    private String modelTriggerBefore = "-";
    private String modelSelected = "-";
    private long modelClaimStartedAt = 0L;

    private final Runnable poller = new Runnable() {
        @Override public void run() {
            if (web != null) {
                String raw = safe(web.getUrl());
                String cid = canonicalCid(raw);
                if (!raw.equals(lastUrlV11)) {
                    lastUrlV11 = raw;
                    record("URL_CHANGE " + sanitizeUrl(raw));
                }
                if (!cid.equals(currentCid)) {
                    String old = currentCid;
                    currentCid = cid;
                    invalidateConversationBoundState(old, cid);
                }
                if (pendingResourceDownload && pendingResourceStartedAt > 0L
                        && System.currentTimeMillis() - pendingResourceStartedAt > 20000L) {
                    pendingResourceDownload = false;
                    resourceActionStatus = "UNCERTAIN_NO_DOWNLOAD_CALLBACK";
                    prefsV11.edit().putString("resource_claim_status", "UNCERTAIN").commit();
                    record("RESOURCE_ACTION_UNCERTAIN_NO_CALLBACK");
                }
                if (audioWatch) pollAudioSnapshot();
                render();
            }
            handlerV11.postDelayed(this, 350L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefsV11 = getSharedPreferences(PREFS, MODE_PRIVATE);
        web = findWebView(getWindow().getDecorView());
        if (web == null) return;

        hideParentNativeUiAndInstallV11Panel();
        web.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));

        web.setDownloadListener(new DownloadListener() {
            @Override public void onDownloadStart(String url, String userAgent, String contentDisposition,
                                                  String mimetype, long contentLength) {
                resourceCallbackMime = safeMime(mimetype);
                resourceCallbackLength = contentLength;
                resourceCallbackSafeUrl = sanitizeUrl(url);
                record("WEBVIEW_DOWNLOAD_LISTENER mime=" + safeToken(resourceCallbackMime)
                        + " len=" + contentLength + " safe=" + safeToken(resourceCallbackSafeUrl));
                if (!pendingResourceDownload) {
                    record("PASSIVE_DOWNLOAD_LISTENER_OBSERVED");
                    render();
                    return;
                }
                pendingResourceDownload = false;
                String nowCid = canonicalCid(web.getUrl());
                if (!pendingResourceCid.equals(nowCid)) {
                    resourceActionStatus = "UNCERTAIN_CALLBACK_AFTER_ROUTE_CHANGE";
                    prefsV11.edit().putString("resource_claim_status", "UNCERTAIN").commit();
                } else {
                    resourceActionStatus = "CONFIRMED_SINGLE_CLICK_DOWNLOAD_CALLBACK";
                    prefsV11.edit().putString("resource_claim_status", "CONFIRMED").commit();
                    record("RESOURCE_ACTION_CONFIRMED_DOWNLOAD_CALLBACK");
                }
                render();
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            @Override public void onPermissionRequest(PermissionRequest request) {
                runOnUiThread(() -> handleWebPermissionRequest(request));
            }

            @Override public void onPermissionRequestCanceled(PermissionRequest request) {
                audioPermissionStatus = "WEB_PERMISSION_CANCELED";
                record("AUDIO_WEB_PERMISSION_CANCELED");
                render();
            }
        });

        web.setWebViewClient(new WebViewClient() {
            @Override public void onPageStarted(WebView view, String url, Bitmap favicon) {
                record("PAGE_START " + sanitizeUrl(url));
                super.onPageStarted(view, url, favicon);
            }

            @Override public void onPageFinished(WebView view, String url) {
                record("PAGE_FINISH " + sanitizeUrl(url));
                if (audioWatch && isTrusted(url)) installAudioProbe();
                super.onPageFinished(view, url);
            }

            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                if (request == null || !request.isForMainFrame() || request.getUrl() == null) return false;
                String target = request.getUrl().toString();
                if (isTrusted(target)) return false;
                if (target.startsWith("https://") || target.startsWith("http://")) {
                    try {
                        startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(target)));
                        record("MANUAL_EXTERNAL_NAVIGATION_SYSTEM_BROWSER");
                        return true;
                    } catch (Exception ignored) { }
                }
                return false;
            }
        });

        currentCid = canonicalCid(web.getUrl());
        lastUrlV11 = safe(web.getUrl());
        handlerV11.post(poller);
        render();
    }

    private void hideParentNativeUiAndInstallV11Panel() {
        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup contentGroup = (ViewGroup) content;
        if (contentGroup.getChildCount() == 0 || !(contentGroup.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) contentGroup.getChildAt(0);

        for (int i = 0; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            if (child != web) child.setVisibility(View.GONE);
        }

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);

        LinearLayout row1 = new LinearLayout(this);
        row1.setOrientation(LinearLayout.HORIZONTAL);
        row1.addView(button("HOME", v -> web.loadUrl("https://chatgpt.com/")), weighted());
        row1.addView(button("RES SCAN", v -> scanResourcesV11()), weighted());
        audioWatchButton = button("AUDIO WATCH", v -> toggleAudioWatch());
        row1.addView(audioWatchButton, weighted());
        row1.addView(button("MODEL SCAN", v -> scanModelMenu()), weighted());
        panel.addView(row1, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(39)));

        LinearLayout row2 = new LinearLayout(this);
        row2.setOrientation(LinearLayout.HORIZONTAL);
        indexInput = new EditText(this);
        indexInput.setSingleLine(true);
        indexInput.setTextSize(12f);
        indexInput.setHint("# resource/model");
        indexInput.setPadding(dp(6), 0, dp(6), 0);
        row2.addView(indexInput, new LinearLayout.LayoutParams(0, dp(39), 1.25f));
        row2.addView(button("RES DL", v -> runResourceAction()), weighted());
        row2.addView(button("MODEL SET", v -> setSelectedModel()), weighted());
        row2.addView(button("REPORT", v -> downloadReportV11()), weighted());
        panel.addView(row2, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(39)));

        status = new TextView(this);
        status.setTextSize(9.2f);
        status.setTextIsSelectable(true);
        status.setPadding(dp(7), dp(3), dp(7), dp(3));
        ScrollView scroll = new ScrollView(this);
        scroll.addView(status, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));
        panel.addView(scroll, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(92)));

        int webIndex = root.indexOfChild(web);
        if (webIndex < 0) webIndex = root.getChildCount();
        root.addView(panel, webIndex, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private Button button(String text, View.OnClickListener listener) {
        Button b = new Button(this);
        b.setText(text);
        b.setTextSize(8.6f);
        b.setOnClickListener(listener);
        return b;
    }

    private LinearLayout.LayoutParams weighted() {
        return new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f);
    }

    private void invalidateConversationBoundState(String oldCid, String newCid) {
        if (!"-".equals(resourceScanCid) && !resourceScanCid.equals(newCid)) {
            resources.clear();
            resourceStatus = "STALE_CONVERSATION_CHANGED";
            resourceScanCid = "-";
            resourceActionStatus = "NOT_RUN";
            if (indexInput != null) indexInput.setText("");
        }
        if (!"-".equals(modelScanCid) && !modelScanCid.equals(newCid)) {
            modelOptions.clear();
            modelStatus = "STALE_CONVERSATION_CHANGED";
            modelScanCid = "-";
        }
        if (!safe(oldCid).equals(safe(newCid))) {
            record("CONVERSATION_CHANGED old=" + safeToken(oldCid) + " new=" + safeToken(newCid));
        }
    }

    // ---------------------------------------------------------------------
    // Resource locator v3: semantic identity != concrete action locator.
    // ---------------------------------------------------------------------

    private void scanResourcesV11() {
        String cid = canonicalCid(web.getUrl());
        if ("-".equals(cid) || !isTrusted(web.getUrl())) {
            resourceStatus = "FAIL_NO_CANONICAL_CHAT";
            render();
            return;
        }
        web.evaluateJavascript(resourceScanJs(cid), value -> {
            try {
                JSONObject root = jsonObject(value);
                String nowCid = canonicalCid(web.getUrl());
                if (!cid.equals(nowCid) || !cid.equals(root.optString("cid", "-"))) {
                    resourceStatus = "FAIL_CID_CHANGED";
                    resources.clear();
                    render();
                    return;
                }
                resources.clear();
                JSONArray arr = root.optJSONArray("items");
                if (arr != null) {
                    for (int i = 0; i < arr.length(); i++) {
                        JSONObject o = arr.optJSONObject(i);
                        if (o == null) continue;
                        ResourceV11 r = ResourceV11.from(o, cid);
                        resources.add(r);
                    }
                }
                resourceScanCid = cid;
                resourceStatus = "COMPLETE";
                resourceActionStatus = "NOT_RUN";
                if (indexInput != null) indexInput.setText("");
                record("RESOURCE_V11_SCAN_COMPLETE unique=" + resources.size());
            } catch (Exception e) {
                resourceStatus = "FAIL_PARSE_" + e.getClass().getSimpleName();
            }
            render();
        });
    }

    private String resourceScanJs(String cid) {
        return "(function(){try{"
                + "const CID='" + js(cid) + "';const norm=x=>(x||'').replace(/\\s+/g,' ').trim();"
                + "const vis=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
                + "const hash=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "const meta=e=>norm((e.getAttribute&&e.getAttribute('aria-label'))||'')+' '+norm((e.getAttribute&&e.getAttribute('title'))||'')+' '+norm((e.getAttribute&&e.getAttribute('data-testid'))||'')+' '+norm(e.innerText||e.textContent||'');"
                + "const fileRe=/[^\\s\\/\\\\]{1,120}\\.(pdf|zip|csv|txt|json|doc|docx|xls|xlsx|ppt|pptx|png|jpg|jpeg|webp|gif|mp3|mp4|wav)\\b/i;"
                + "let locSeq=0;const locator=e=>{let x=e.getAttribute('data-cp-locator-v11');if(!x){x='L'+(++locSeq)+'_'+hash(meta(e));e.setAttribute('data-cp-locator-v11',x);}return x;};"
                + "const items={};const put=(key,kind,label,href,role,idx,loc,score)=>{let x=items[key];if(!x)x=items[key]={id:key,kind:kind,label:label,href:href||'',role:role,turnIndex:idx,locators:[],locatorScores:[],occurrences:0};x.occurrences++;if(loc&&x.locators.indexOf(loc)<0){x.locators.push(loc);x.locatorScores.push(score||0);}items[key]=x;};"
                + "const turns=[];const seen=new Set();document.querySelectorAll('article[data-testid^=\\\"conversation-turn-\\\"],[data-message-author-role]').forEach(e=>{const t=e.closest('article')||e;if(!seen.has(t)){seen.add(t);turns.push(t);}});"
                + "turns.forEach((turn,idx)=>{const roleEl=turn.matches('[data-message-author-role]')?turn:turn.querySelector('[data-message-author-role]');const role=roleEl?String(roleEl.getAttribute('data-message-author-role')||'-'):'-';"
                + "const controls=Array.from(turn.querySelectorAll('button,[role=\\\"button\\\"],a[href]')).filter(vis);"
                + "controls.forEach(c=>{let card=c,cur=c;let file='';for(let n=0;n<6&&cur&&turn.contains(cur);n++,cur=cur.parentElement){const tx=norm(cur.innerText||cur.textContent||'');const m=tx.match(fileRe);if(m&&tx.length<650){card=cur;file=m[0];break;}}const m=meta(c);const low=m.toLowerCase();const explicit=/download|save|دانلود/.test(low);if(file&&explicit){const loc=locator(c);let score=explicit?10:0;if(c.tagName==='BUTTON')score+=3;if((c.getAttribute('aria-label')||'').length)score+=2;const key=hash(role+'|'+idx+'|FILE_ACTION|'+file.toLowerCase());put(key,'FILE_ACTION',file,'',role,idx,loc,score);}});"
                + "turn.querySelectorAll('a[href]').forEach(a=>{if(!vis(a))return;const href=a.href||a.getAttribute('href')||'';let u=null;try{u=new URL(href,location.href);}catch(_){}const label=norm(a.getAttribute('aria-label')||a.innerText||a.textContent||'link');const key=hash(role+'|'+idx+'|LINK|'+(u?u.origin+u.pathname:href)+'|'+label);put(key,'LINK',label,href,role,idx,locator(a),1);});"
                + "});"
                + "Object.values(items).forEach(x=>{if(x.kind==='FILE_ACTION'){let best=-999,bi=-1,tie=false;for(let i=0;i<x.locators.length;i++){const s=x.locatorScores[i]||0;if(s>best){best=s;bi=i;tie=false;}else if(s===best){tie=true;}}x.primaryLocator=(!tie&&bi>=0)?x.locators[bi]:'';}else{x.primaryLocator=x.locators.length===1?x.locators[0]:'';}});"
                + "return JSON.stringify({cid:CID,items:Object.values(items)});"
                + "}catch(e){return JSON.stringify({cid:'-',error:String(e),items:[]});}})();";
    }

    private void runResourceAction() {
        if (!"COMPLETE".equals(resourceStatus) || !resourceScanCid.equals(canonicalCid(web.getUrl()))) {
            Toast.makeText(this, "Run RES SCAN on the current chat first", Toast.LENGTH_LONG).show();
            return;
        }
        int idx = selectedIndex();
        if (idx < 0 || idx >= resources.size()) {
            Toast.makeText(this, "Enter a resource number", Toast.LENGTH_LONG).show();
            return;
        }
        ResourceV11 r = resources.get(idx);
        if (!"FILE_ACTION".equals(r.kind)) {
            resourceActionStatus = "BLOCKED_NOT_FILE_ACTION";
            render();
            return;
        }
        if (r.primaryLocator.isEmpty()) {
            resourceActionStatus = "BLOCKED_NO_UNIQUE_PRIMARY_LOCATOR count=" + r.locators.size();
            render();
            return;
        }
        String prior = prefsV11.getString("resource_claim_status", "-");
        if ("CLAIMED".equals(prior) || "DISPATCHED".equals(prior) || "UNCERTAIN".equals(prior)) {
            resourceActionStatus = "BLOCKED_UNRESOLVED_PRIOR_CLAIM";
            render();
            return;
        }
        prefsV11.edit().putString("resource_claim_status", "CLAIMED")
                .putString("resource_claim_hash", sha256Quiet(r.id + "|" + r.cid)).commit();
        pendingResourceId = r.id;
        pendingResourceLocator = r.primaryLocator;
        pendingResourceCid = r.cid;
        pendingResourceStartedAt = System.currentTimeMillis();
        pendingResourceDownload = true;
        resourceActionStatus = "CLAIMED";
        record("RESOURCE_ACTION_DURABLE_CLAIMED locators=" + r.locators.size());
        web.evaluateJavascript(clickLocatorJs(r.primaryLocator), value -> {
            String token = cleanScalar(value);
            if (!"CLICKED_1".equals(token)) {
                pendingResourceDownload = false;
                resourceActionStatus = "BLOCKED_" + safeToken(token);
                prefsV11.edit().putString("resource_claim_status", "-").commit();
                record("RESOURCE_ACTION_NOT_DISPATCHED " + safeToken(token));
            } else {
                prefsV11.edit().putString("resource_claim_status", "DISPATCHED").commit();
                resourceActionStatus = "DISPATCHED_WAIT_DOWNLOAD_CALLBACK";
                record("RESOURCE_ACTION_SINGLE_CLICK_DISPATCHED");
            }
            render();
        });
    }

    private String clickLocatorJs(String locator) {
        return "(function(){try{const q='[data-cp-locator-v11=\\\"" + js(locator) + "\\\"]';const all=Array.from(document.querySelectorAll(q));const vis=all.filter(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';});if(vis.length!==1)return 'MATCHES_'+vis.length;const e=vis[0];if(e.disabled||e.getAttribute('aria-disabled')==='true')return 'DISABLED';e.click();return 'CLICKED_1';}catch(_){return 'ERR';}})();";
    }

    // ---------------------------------------------------------------------
    // Audio capability watcher.
    // ---------------------------------------------------------------------

    private void toggleAudioWatch() {
        if (audioWatch) {
            audioWatch = false;
            audioLeaseUntil = 0L;
            audioState = "WATCH_STOPPED";
            if (audioWatchButton != null) audioWatchButton.setText("AUDIO WATCH");
            record("AUDIO_WATCH_STOPPED");
            render();
            return;
        }
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            audioPermissionStatus = "WAITING_ANDROID_RUNTIME_PERMISSION";
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQ_RECORD_AUDIO);
            render();
            return;
        }
        startAudioWatch();
    }

    private void startAudioWatch() {
        audioWatch = true;
        audioLeaseUntil = System.currentTimeMillis() + 10L * 60L * 1000L;
        audioState = "ARMED_WAITING_FOR_WEB_INTERACTION";
        audioPermissionStatus = "ANDROID_PERMISSION_GRANTED_WEB_NOT_YET_REQUESTED";
        audioLastEventSeq = -1;
        audioStateTransitions = 0;
        if (audioWatchButton != null) audioWatchButton.setText("AUDIO STOP");
        installAudioProbe();
        record("AUDIO_WATCH_ARMED leaseMs=600000");
        Toast.makeText(this, "Now use Dictation and Voice controls inside ChatGPT, including their secondary buttons", Toast.LENGTH_LONG).show();
        render();
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != REQ_RECORD_AUDIO) return;
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            audioPermissionStatus = "ANDROID_PERMISSION_GRANTED";
            startAudioWatch();
        } else {
            audioPermissionStatus = "ANDROID_PERMISSION_DENIED";
            audioState = "BLOCKED_ANDROID_PERMISSION_DENIED";
            record("AUDIO_ANDROID_PERMISSION_DENIED");
            render();
        }
    }

    private void handleWebPermissionRequest(PermissionRequest request) {
        if (request == null) return;
        audioPermissionRequestCount++;
        Uri origin = request.getOrigin();
        audioPermissionOrigin = origin == null ? "-" : safe(origin.getScheme()) + "://" + safe(origin.getHost());
        boolean wantsAudio = false;
        for (String r : request.getResources()) {
            if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(r)) wantsAudio = true;
        }
        record("WEB_PERMISSION_REQUEST audio=" + wantsAudio + " origin=" + safeToken(audioPermissionOrigin));
        boolean allowed = wantsAudio
                && origin != null
                && "https".equalsIgnoreCase(origin.getScheme())
                && isTrustedHost(safe(origin.getHost()))
                && audioWatch
                && System.currentTimeMillis() < audioLeaseUntil
                && checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED;
        if (allowed) {
            request.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
            audioPermissionStatus = "WEB_AUDIO_CAPTURE_GRANTED_EXPLICITLY";
            record("WEB_AUDIO_CAPTURE_GRANTED");
        } else {
            request.deny();
            audioPermissionStatus = "WEB_PERMISSION_DENIED_FAIL_CLOSED";
            record("WEB_AUDIO_CAPTURE_DENIED_FAIL_CLOSED");
        }
        render();
    }

    private void installAudioProbe() {
        if (web == null || !isTrusted(web.getUrl())) return;
        web.evaluateJavascript(audioInstallJs(), ignored -> { });
    }

    private String audioInstallJs() {
        return "(function(){try{if(window.__cpAudioV11)return 'EXISTS';"
                + "const norm=x=>(x||'').replace(/\\s+/g,' ').trim();const vis=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
                + "const h=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "const label=e=>norm((e.getAttribute&&e.getAttribute('aria-label'))||e.innerText||e.textContent||(e.getAttribute&&e.getAttribute('title'))||'');"
                + "const cat=e=>{const x=(label(e)+' '+((e.getAttribute&&e.getAttribute('data-testid'))||'')+' '+((e.getAttribute&&e.getAttribute('title'))||'')).toLowerCase();if(/unmute/.test(x))return 'UNMUTE';if(/mute/.test(x))return 'MUTE';if(/end voice|leave voice|exit voice|end call/.test(x))return 'VOICE_END';if(/voice mode|start voice|open voice|advanced voice/.test(x))return 'VOICE_START';if(/microphone|dictat|voice input|record audio|record message/.test(x))return 'DICTATION_MIC';if(/cancel|discard/.test(x))return 'CANCEL';if(/stop|finish recording|stop recording/.test(x))return 'STOP';if(/confirm|done|accept|use recording/.test(x))return 'CONFIRM';if(/^send$|send message|submit/.test(x))return 'SEND';return 'OTHER';};"
                + "const interesting=()=>Array.from(document.querySelectorAll('button,[role=\\\"button\\\"],[aria-label]')).filter(vis).map(e=>({e:e,c:cat(e),l:label(e)})).filter(x=>x.c!=='OTHER');"
                + "const state=xs=>{const s=new Set(xs.map(x=>x.c));if(s.has('VOICE_END')||s.has('MUTE')||s.has('UNMUTE'))return 'VOICE_ACTIVE';if(s.has('CANCEL')&&(s.has('STOP')||s.has('CONFIRM')))return 'DICTATION_ACTIVE';if(s.has('DICTATION_MIC')&&s.has('VOICE_START'))return 'READY_DICTATION_AND_VOICE';if(s.has('DICTATION_MIC'))return 'READY_DICTATION';if(s.has('VOICE_START'))return 'READY_VOICE';return 'NO_AUDIO_CONTROLS';};"
                + "const o={seq:0,last:null};document.addEventListener('pointerdown',ev=>{const e=ev.target&&ev.target.closest?ev.target.closest('button,[role=\\\"button\\\"],[aria-label]'):null;if(!e)return;const c=cat(e);if(c==='OTHER')return;o.seq++;o.last={seq:o.seq,cat:c,t:performance.now(),labelHash:h(label(e))};},true);"
                + "o.snap=()=>{const xs=interesting(),cats=xs.map(x=>x.c),hashes=xs.map(x=>x.c+':'+h(x.l));return {state:state(xs),cats:cats,controlSig:h(hashes.sort().join('|')),last:o.last,now:performance.now()};};window.__cpAudioV11=o;return 'INSTALLED';}catch(e){return 'ERR';}})();";
    }

    private void pollAudioSnapshot() {
        if (web == null || !isTrusted(web.getUrl())) return;
        web.evaluateJavascript("(function(){try{return JSON.stringify(window.__cpAudioV11?window.__cpAudioV11.snap():{state:'PROBE_MISSING'});}catch(e){return JSON.stringify({state:'ERR'});}})();", value -> {
            try {
                JSONObject o = jsonObject(value);
                String newState = o.optString("state", "UNKNOWN");
                String newSig = o.optString("controlSig", "-");
                JSONObject last = o.optJSONObject("last");
                int seq = last == null ? -1 : last.optInt("seq", -1);
                String cat = last == null ? "-" : last.optString("cat", "-");
                double eventT = last == null ? -1d : last.optDouble("t", -1d);
                double now = o.optDouble("now", -1d);
                double since = eventT >= 0d && now >= eventT ? now - eventT : -1d;
                boolean changed = !newState.equals(audioState) || !newSig.equals(audioControlSignature) || seq != audioLastEventSeq;
                if (changed) {
                    if (!newState.equals(audioState)) audioStateTransitions++;
                    audioState = newState;
                    audioControlSignature = newSig;
                    audioLastEventSeq = seq;
                    audioLastEventCategory = cat;
                    audioLastEventToSnapshotMs = since;
                    record("AUDIO_STATE state=" + safeToken(newState)
                            + " event=" + safeToken(cat)
                            + " eventSeq=" + seq
                            + " eventToSnapshotMs=" + formatMs(since)
                            + " controlSig=" + safeToken(newSig));
                }
            } catch (Exception e) {
                audioState = "SNAPSHOT_PARSE_FAIL";
            }
        });
    }

    // ---------------------------------------------------------------------
    // Model controller diagnostic.
    // ---------------------------------------------------------------------

    private void scanModelMenu() {
        String cid = canonicalCid(web.getUrl());
        if ("-".equals(cid) || !isTrusted(web.getUrl())) {
            modelStatus = "FAIL_NO_CANONICAL_CHAT";
            render();
            return;
        }
        web.evaluateJavascript(modelTriggerClickJs(), value -> {
            String token = cleanScalar(value);
            if (!token.startsWith("CLICKED_1|")) {
                modelStatus = "FAIL_TRIGGER_" + safeToken(token);
                render();
                return;
            }
            modelTriggerBefore = token.substring("CLICKED_1|".length());
            handlerV11.postDelayed(() -> web.evaluateJavascript(modelOptionsJs(), optionsValue -> {
                try {
                    JSONObject o = jsonObject(optionsValue);
                    String nowCid = canonicalCid(web.getUrl());
                    if (!cid.equals(nowCid)) {
                        modelStatus = "FAIL_CID_CHANGED";
                        modelOptions.clear();
                        render();
                        return;
                    }
                    modelOptions.clear();
                    JSONArray a = o.optJSONArray("items");
                    if (a != null) {
                        Set<String> dedup = new LinkedHashSet<>();
                        for (int i = 0; i < a.length(); i++) {
                            String x = normalize(a.optString(i, ""));
                            if (!x.isEmpty()) dedup.add(x);
                        }
                        modelOptions.addAll(dedup);
                    }
                    modelScanCid = cid;
                    modelStatus = modelOptions.isEmpty() ? "COMPLETE_EMPTY" : "COMPLETE";
                    record("MODEL_SCAN_COMPLETE count=" + modelOptions.size()
                            + " triggerHash=" + sha256Quiet(modelTriggerBefore));
                } catch (Exception e) {
                    modelStatus = "FAIL_PARSE_" + e.getClass().getSimpleName();
                }
                render();
            }), 450L);
        });
    }

    private String modelTriggerClickJs() {
        return "(function(){try{const norm=x=>(x||'').replace(/\\s+/g,' ').trim();const vis=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';};const all=Array.from(document.querySelectorAll('button,[role=\\\"button\\\"]')).filter(vis);const cand=all.filter(e=>{const a=norm(e.getAttribute('aria-label')||'').toLowerCase(),t=norm(e.innerText||e.textContent||'');return a.includes('model selector')||a==='switch model'||(/^(gpt|o[134]|chatgpt)/i.test(t)&&t.length<80&&e.getAttribute('aria-haspopup'));});if(cand.length!==1)return 'MATCHES_'+cand.length;const e=cand[0];const txt=norm(e.innerText||e.textContent||e.getAttribute('aria-label')||'model');e.click();return 'CLICKED_1|'+txt;}catch(e){return 'ERR';}})();";
    }

    private String modelOptionsJs() {
        return "(function(){try{const norm=x=>(x||'').replace(/\\s+/g,' ').trim();const vis=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';};let scopes=Array.from(document.querySelectorAll('[role=\\\"menu\\\"],[role=\\\"listbox\\\"],[data-radix-menu-content],[data-radix-popper-content-wrapper]')).filter(vis);let nodes=[];if(scopes.length){scopes.forEach(s=>nodes.push(...Array.from(s.querySelectorAll('button,[role=\\\"menuitem\\\"],[role=\\\"option\\\"]')).filter(vis)));}else{nodes=Array.from(document.querySelectorAll('[role=\\\"menuitem\\\"],[role=\\\"option\\\"]')).filter(vis);}const out=[];nodes.forEach(e=>{const t=norm(e.innerText||e.textContent||e.getAttribute('aria-label')||'');if(t.length>=2&&t.length<=180&&!/^(close|cancel|more)$/i.test(t))out.push(t);});return JSON.stringify({items:out});}catch(e){return JSON.stringify({items:[],error:String(e)});}})();";
    }

    private void setSelectedModel() {
        if (!"COMPLETE".equals(modelStatus) || !modelScanCid.equals(canonicalCid(web.getUrl()))) {
            Toast.makeText(this, "Run MODEL SCAN on the current chat first", Toast.LENGTH_LONG).show();
            return;
        }
        int idx = selectedIndex();
        if (idx < 0 || idx >= modelOptions.size()) {
            Toast.makeText(this, "Enter a model number", Toast.LENGTH_LONG).show();
            return;
        }
        String target = modelOptions.get(idx);
        String prior = prefsV11.getString("model_claim_status", "-");
        if ("CLAIMED".equals(prior) || "DISPATCHED".equals(prior) || "UNCERTAIN".equals(prior)) {
            modelStatus = "BLOCKED_UNRESOLVED_PRIOR_MODEL_CLAIM";
            render();
            return;
        }
        prefsV11.edit().putString("model_claim_status", "CLAIMED")
                .putString("model_claim_target_hash", sha256Quiet(target)).commit();
        modelClaimStartedAt = System.currentTimeMillis();
        modelStatus = "CLAIMED_OPENING_MENU";
        record("MODEL_SET_DURABLE_CLAIMED targetHash=" + sha256Quiet(target));
        web.evaluateJavascript(modelTriggerClickJs(), triggerValue -> {
            String triggerToken = cleanScalar(triggerValue);
            if (!triggerToken.startsWith("CLICKED_1|")) {
                prefsV11.edit().putString("model_claim_status", "-").commit();
                modelStatus = "BLOCKED_TRIGGER_" + safeToken(triggerToken);
                record("MODEL_SET_NOT_DISPATCHED_TRIGGER");
                render();
                return;
            }
            handlerV11.postDelayed(() -> web.evaluateJavascript(modelClickOptionJs(target), clickValue -> {
                String clickToken = cleanScalar(clickValue);
                if (!"CLICKED_1".equals(clickToken)) {
                    prefsV11.edit().putString("model_claim_status", "-").commit();
                    modelStatus = "BLOCKED_OPTION_" + safeToken(clickToken);
                    record("MODEL_SET_NOT_DISPATCHED " + safeToken(clickToken));
                    render();
                    return;
                }
                prefsV11.edit().putString("model_claim_status", "DISPATCHED").commit();
                modelStatus = "DISPATCHED_VERIFYING";
                modelSelected = target;
                record("MODEL_SET_SINGLE_CLICK_DISPATCHED");
                handlerV11.postDelayed(() -> verifyModelSelection(target), 800L);
                render();
            }), 350L);
        });
    }

    private String modelClickOptionJs(String target) {
        return "(function(){try{const T='" + js(normalize(target)) + "';const norm=x=>(x||'').replace(/\\s+/g,' ').trim();const vis=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';};const all=Array.from(document.querySelectorAll('button,[role=\\\"menuitem\\\"],[role=\\\"option\\\"]')).filter(vis).filter(e=>norm(e.innerText||e.textContent||e.getAttribute('aria-label')||'')===T);if(all.length!==1)return 'MATCHES_'+all.length;all[0].click();return 'CLICKED_1';}catch(e){return 'ERR';}})();";
    }

    private void verifyModelSelection(String target) {
        web.evaluateJavascript("(function(){try{const norm=x=>(x||'').replace(/\\s+/g,' ').trim();const vis=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';};const all=Array.from(document.querySelectorAll('button,[role=\\\"button\\\"]')).filter(vis).filter(e=>{const a=norm(e.getAttribute('aria-label')||'').toLowerCase(),t=norm(e.innerText||e.textContent||'');return a.includes('model selector')||a==='switch model'||(/^(gpt|o[134]|chatgpt)/i.test(t)&&t.length<80&&e.getAttribute('aria-haspopup'));});return all.length===1?norm(all[0].innerText||all[0].textContent||all[0].getAttribute('aria-label')||''):'MATCHES_'+all.length;}catch(e){return 'ERR';}})();", value -> {
            String observed = cleanScalar(value);
            String nt = normalize(target).toLowerCase(Locale.US);
            String no = normalize(observed).toLowerCase(Locale.US);
            boolean strong = !no.startsWith("matches_") && !"err".equals(no)
                    && (no.equals(nt) || no.contains(nt) || nt.contains(no));
            if (strong) {
                modelStatus = "CONFIRMED";
                prefsV11.edit().putString("model_claim_status", "CONFIRMED").commit();
                record("MODEL_SET_CONFIRMED observedHash=" + sha256Quiet(observed)
                        + " elapsedMs=" + (System.currentTimeMillis() - modelClaimStartedAt));
            } else {
                modelStatus = "UNCERTAIN_DISPATCHED_NOT_STRONGLY_VERIFIED";
                prefsV11.edit().putString("model_claim_status", "UNCERTAIN").commit();
                record("MODEL_SET_UNCERTAIN observedHash=" + sha256Quiet(observed));
            }
            render();
        });
    }

    // ---------------------------------------------------------------------
    // Status and report.
    // ---------------------------------------------------------------------

    private void render() {
        if (status == null) return;
        StringBuilder s = new StringBuilder();
        s.append("Stable v0.11 AUDIO + MODEL + RESOURCE LOCATOR V3\n");
        s.append("CID: ").append(currentCid).append("  WebView>=50%: true\n");
        s.append("RES: ").append(resourceStatus).append(" n=").append(resources.size())
                .append(" action=").append(resourceActionStatus).append('\n');
        s.append("AUDIO: ").append(audioState).append(" permission=").append(audioPermissionStatus)
                .append(" transitions=").append(audioStateTransitions).append('\n');
        s.append("AUDIO_LAST: ").append(audioLastEventCategory)
                .append(" ->snapshot=").append(formatMs(audioLastEventToSnapshotMs)).append("ms\n");
        s.append("MODEL: ").append(modelStatus).append(" n=").append(modelOptions.size()).append('\n');

        int cap = Math.min(resources.size(), 5);
        for (int i = 0; i < cap; i++) {
            ResourceV11 r = resources.get(i);
            s.append("R").append(i + 1).append(" [").append(r.kind).append("] ")
                    .append(clip(r.label, 26)).append(" loc=").append(r.locators.size())
                    .append(r.primaryLocator.isEmpty() ? " !" : " *").append('\n');
        }
        int mcap = Math.min(modelOptions.size(), 5);
        for (int i = 0; i < mcap; i++) {
            s.append("M").append(i + 1).append(" ").append(clip(modelOptions.get(i), 42)).append('\n');
        }
        status.setText(s.toString().trim());
    }

    private void downloadReportV11() {
        StringBuilder r = new StringBuilder();
        r.append("CHATGPT_WEBVIEW_STABLE_V11_AUDIO_MODEL_RESOURCE_SUITE\n");
        r.append("CURRENT_URL=").append(sanitizeUrl(web == null ? "-" : web.getUrl())).append('\n');
        r.append("CURRENT_CONVERSATION_ID=").append(currentCid).append('\n');
        r.append("WEBVIEW_MIN_HALF_SCREEN_POLICY=true\n");
        r.append("RECORD_AUDIO_PERMISSION_DECLARED=true\n");
        r.append("RESOURCE_STATUS=").append(resourceStatus).append('\n');
        r.append("RESOURCE_SCAN_CID=").append(resourceScanCid).append('\n');
        r.append("RESOURCE_ACTION_STATUS=").append(resourceActionStatus).append('\n');
        r.append("RESOURCE_DOWNLOAD_CALLBACK_MIME=").append(resourceCallbackMime).append('\n');
        r.append("RESOURCE_DOWNLOAD_CALLBACK_LENGTH=").append(resourceCallbackLength).append('\n');
        r.append("RESOURCE_DOWNLOAD_CALLBACK_SAFE_URL=").append(resourceCallbackSafeUrl).append('\n');
        r.append("AUDIO_WATCH_ACTIVE=").append(audioWatch).append('\n');
        r.append("AUDIO_PERMISSION_STATUS=").append(audioPermissionStatus).append('\n');
        r.append("AUDIO_PERMISSION_ORIGIN=").append(audioPermissionOrigin).append('\n');
        r.append("AUDIO_PERMISSION_REQUEST_COUNT=").append(audioPermissionRequestCount).append('\n');
        r.append("AUDIO_STATE=").append(audioState).append('\n');
        r.append("AUDIO_CONTROL_SIGNATURE=").append(audioControlSignature).append('\n');
        r.append("AUDIO_LAST_EVENT_CATEGORY=").append(audioLastEventCategory).append('\n');
        r.append("AUDIO_LAST_EVENT_TO_SNAPSHOT_MS=").append(formatMs(audioLastEventToSnapshotMs)).append('\n');
        r.append("AUDIO_STATE_TRANSITIONS=").append(audioStateTransitions).append('\n');
        r.append("MODEL_STATUS=").append(modelStatus).append('\n');
        r.append("MODEL_SCAN_CID=").append(modelScanCid).append('\n');
        r.append("MODEL_TRIGGER_BEFORE_SHA256=").append(sha256Quiet(modelTriggerBefore)).append('\n');
        r.append("MODEL_SELECTED_SHA256=").append(sha256Quiet(modelSelected)).append('\n');
        r.append("MODEL_OPTION_COUNT=").append(modelOptions.size()).append('\n');
        for (int i = 0; i < modelOptions.size(); i++) {
            r.append("MODEL_OPTION_").append(i + 1).append('=').append(modelOptions.get(i)).append('\n');
        }
        r.append("RAW_CHAT_TEXT_RETAINED=false\n");
        r.append("RAW_AUDIO_RETAINED=false\n");
        r.append("CHATGPT_COOKIES_EXTRACTED=false\n");
        r.append("RAW_RESOURCE_LABEL_RETAINED_IN_REPORT=false\n");
        r.append("RAW_RESOURCE_QUERY_URL_RETAINED_IN_REPORT=false\n");
        r.append("--- RESOURCE INDEX (HASHED) ---\n");
        for (int i = 0; i < resources.size(); i++) {
            ResourceV11 x = resources.get(i);
            r.append('#').append(i + 1)
                    .append(" kind=").append(x.kind)
                    .append(" role=").append(x.role)
                    .append(" turnIndex=").append(x.turnIndex)
                    .append(" occurrences=").append(x.occurrences)
                    .append(" locatorCount=").append(x.locators.size())
                    .append(" hasUniquePrimary=").append(!x.primaryLocator.isEmpty())
                    .append(" labelSha=").append(sha256Quiet(x.label))
                    .append(" hrefSha=").append(sha256Quiet(x.href))
                    .append(" safe=").append(safeHostPath(x.href))
                    .append('\n');
        }
        r.append("--- EVENT LOG ---\n").append(events);
        saveTextReport(r.toString());
    }

    private void saveTextReport(String text) {
        try {
            String name = "chatgpt-webview-v11-audio-model-report-"
                    + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".txt";
            ContentValues v = new ContentValues();
            v.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            v.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
            v.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
            v.put(MediaStore.MediaColumns.IS_PENDING, 1);
            Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v);
            if (uri == null) throw new IllegalStateException("insert failed");
            try (OutputStream os = getContentResolver().openOutputStream(uri)) {
                if (os == null) throw new IllegalStateException("stream failed");
                os.write(text.getBytes(StandardCharsets.UTF_8));
            }
            ContentValues done = new ContentValues();
            done.put(MediaStore.MediaColumns.IS_PENDING, 0);
            getContentResolver().update(uri, done, null, null);
            Toast.makeText(this, "v0.11 report saved to Downloads/ChatGPTWebViewProbe", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "Report failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
        }
    }

    private void record(String event) {
        String ts = new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date());
        if (events.length() > 28000) events.delete(0, Math.min(7000, events.length()));
        events.append(ts).append(" | ").append(event).append(" | cid=").append(currentCid).append('\n');
    }

    private int selectedIndex() {
        try { return Integer.parseInt(indexInput.getText().toString().trim()) - 1; }
        catch (Exception e) { return -1; }
    }

    private JSONObject jsonObject(String value) throws Exception {
        Object outer = new JSONTokener(value).nextValue();
        String json = outer instanceof String ? (String) outer : String.valueOf(outer);
        return new JSONObject(json);
    }

    private String cleanScalar(String value) {
        try {
            Object outer = new JSONTokener(value).nextValue();
            return outer == null ? "" : String.valueOf(outer);
        } catch (Exception e) {
            if (value == null) return "";
            return value.replace("\"", "");
        }
    }

    private static String canonicalCid(String raw) {
        try {
            URI u = URI.create(safe(raw));
            String[] p = safe(u.getPath()).split("/");
            for (int i = 0; i < p.length - 1; i++) {
                if ("c".equals(p[i]) && UUID_PATTERN.matcher(p[i + 1]).matches()) return p[i + 1];
            }
        } catch (Exception ignored) { }
        return "-";
    }

    private static boolean isTrusted(String raw) {
        try {
            URI u = URI.create(safe(raw));
            return "https".equalsIgnoreCase(safe(u.getScheme())) && isTrustedHost(safe(u.getHost()));
        } catch (Exception e) { return false; }
    }

    private static boolean isTrustedHost(String host) {
        String h = safe(host).toLowerCase(Locale.US);
        return "chatgpt.com".equals(h) || h.endsWith(".chatgpt.com");
    }

    private static String sanitizeUrl(String raw) {
        try {
            URI u = URI.create(safe(raw));
            if (u.getScheme() == null || u.getHost() == null) return "-";
            return u.getScheme() + "://" + u.getHost() + (u.getPort() > 0 ? ":" + u.getPort() : "") + safe(u.getPath());
        } catch (Exception e) { return "-"; }
    }

    private static String safeHostPath(String raw) {
        try {
            URI u = URI.create(safe(raw));
            return safe(u.getHost()) + safe(u.getPath());
        } catch (Exception e) { return "-"; }
    }

    private static String js(String s) {
        return safe(s).replace("\\", "\\\\").replace("'", "\\'")
                .replace("\r", " ").replace("\n", " ");
    }

    private static String safe(String s) { return s == null ? "" : s; }

    private static String normalize(String s) {
        return safe(s).replaceAll("\\s+", " ").trim();
    }

    private static String safeToken(String s) {
        String x = safe(s).replaceAll("[^A-Za-z0-9_./:=+-]", "_");
        return x.length() > 180 ? x.substring(0, 180) : x;
    }

    private static String safeMime(String s) {
        String x = safe(s).split(";", 2)[0].trim().toLowerCase(Locale.US);
        return x.isEmpty() ? "application/octet-stream" : x;
    }

    private static String clip(String s, int max) {
        String x = normalize(s);
        return x.length() <= max ? x : x.substring(0, Math.max(0, max - 3)) + "...";
    }

    private static String formatMs(double ms) {
        if (ms < 0d || Double.isNaN(ms) || Double.isInfinite(ms)) return "-1";
        return String.format(Locale.US, "%.1f", ms);
    }

    private static String sha256Quiet(String text) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] out = md.digest(safe(text).getBytes(StandardCharsets.UTF_8));
            StringBuilder b = new StringBuilder();
            for (byte x : out) b.append(String.format(Locale.US, "%02x", x & 0xff));
            return b.toString();
        } catch (Exception e) { return "-"; }
    }

    private int dp(int n) {
        return Math.round(n * getResources().getDisplayMetrics().density);
    }

    private WebView findWebView(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (!(v instanceof ViewGroup)) return null;
        ViewGroup g = (ViewGroup) v;
        for (int i = 0; i < g.getChildCount(); i++) {
            WebView w = findWebView(g.getChildAt(i));
            if (w != null) return w;
        }
        return null;
    }

    @Override protected void onDestroy() {
        handlerV11.removeCallbacks(poller);
        audioWatch = false;
        super.onDestroy();
    }

    private static final class ResourceV11 {
        String id = "-";
        String cid = "-";
        String kind = "OTHER";
        String label = "";
        String href = "";
        String role = "-";
        int turnIndex = -1;
        int occurrences = 0;
        String primaryLocator = "";
        final List<String> locators = new ArrayList<>();

        static ResourceV11 from(JSONObject o, String cid) {
            ResourceV11 r = new ResourceV11();
            r.id = o.optString("id", "-");
            r.cid = cid;
            r.kind = o.optString("kind", "OTHER");
            r.label = o.optString("label", "");
            r.href = o.optString("href", "");
            r.role = o.optString("role", "-");
            r.turnIndex = o.optInt("turnIndex", -1);
            r.occurrences = o.optInt("occurrences", 0);
            r.primaryLocator = o.optString("primaryLocator", "");
            JSONArray a = o.optJSONArray("locators");
            if (a != null) for (int i = 0; i < a.length(); i++) {
                String x = a.optString(i, "");
                if (!x.isEmpty()) r.locators.add(x);
            }
            return r;
        }
    }
}
