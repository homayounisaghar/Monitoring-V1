package com.homayounisaghar.chatgptwebviewprobe;

import android.app.Activity;
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
import android.util.Base64;
import android.webkit.CookieManager;
import android.webkit.DownloadListener;
import android.webkit.MimeTypeMap;
import android.webkit.WebResourceRequest;
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

import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import java.util.regex.Pattern;

public class ResourceSuiteActivity extends Activity {
    private static final Pattern UUID_PATTERN = Pattern.compile(
            "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$");
    private static final long MAX_PAGE_FETCH_BYTES = 96L * 1024L * 1024L;
    private static final long MAX_PUBLIC_DOWNLOAD_BYTES = 128L * 1024L * 1024L;
    private static final int PULL_CHUNK_BYTES = 96 * 1024;
    private static final String PREFS = "stable_v09_resource_suite";

    private WebView webView;
    private TextView statusView;
    private EditText resourceIndexInput;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final StringBuilder eventLog = new StringBuilder();
    private final List<Resource> resources = new ArrayList<>();
    private SharedPreferences prefs;

    private String lastUrl = "";
    private String scanStatus = "NOT_RUN";
    private String scanCid = "-";
    private int scanVisibleTurnCount = -1;
    private int scanRegistryCount = 0;
    private String selectedResourceId = "-";
    private int selectedResourceIndex = -1;
    private String selectedResourceClass = "-";

    private String downloadStatus = "NOT_RUN";
    private String downloadStrategy = "-";
    private String downloadMime = "-";
    private long downloadBytes = 0L;
    private String downloadSha256 = "-";
    private int downloadChunks = 0;
    private String downloadReceiptId = "-";
    private boolean downloadBusy = false;

    private String pendingActionResourceId = "-";
    private String pendingActionCid = "-";
    private boolean pendingActionListener = false;
    private long pendingActionStartedAt = 0L;

    private final Runnable routeProbe = new Runnable() {
        @Override public void run() {
            if (webView != null) {
                String u = safe(webView.getUrl());
                if (!u.equals(lastUrl)) {
                    lastUrl = u;
                    recordRoute("URL_CHANGE", u);
                    if (isTrustedChatGptUrl(u)) installRegistry();
                }
                if (pendingActionListener && pendingActionStartedAt > 0L
                        && System.currentTimeMillis() - pendingActionStartedAt > 20000L) {
                    pendingActionListener = false;
                    downloadStatus = "UNCERTAIN_ACTION_NO_DOWNLOAD_CALLBACK";
                    prefs.edit().putString("action_claim_status", "UNCERTAIN").commit();
                    recordEvent("DOWNLOAD_ACTION_UNCERTAIN_NO_CALLBACK");
                }
                renderStatus();
            }
            handler.postDelayed(this, 750L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);

        getWindow().setStatusBarColor(Color.WHITE);
        getWindow().setNavigationBarColor(Color.WHITE);
        getWindow().getDecorView().setSystemUiVisibility(android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);

        CookieManager cm = CookieManager.getInstance();
        cm.setAcceptCookie(true);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setFitsSystemWindows(true);
        Space gap = new Space(this);
        root.addView(gap, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(8)));

        LinearLayout row1 = new LinearLayout(this);
        row1.setOrientation(LinearLayout.HORIZONTAL);
        row1.addView(button("HOME", v -> webView.loadUrl("https://chatgpt.com/")), weighted());
        row1.addView(button("SCAN", v -> scanResources()), weighted());
        row1.addView(button("V08", v -> startActivity(new Intent(this, DirectAttachmentActivity.class))), weighted());
        root.addView(row1, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(46)));

        resourceIndexInput = new EditText(this);
        resourceIndexInput.setSingleLine(true);
        resourceIndexInput.setTextSize(13f);
        resourceIndexInput.setHint("Resource # from SCAN, e.g. 1");
        resourceIndexInput.setPadding(dp(8), dp(4), dp(8), dp(4));
        root.addView(resourceIndexInput,
                new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(48)));

        LinearLayout row2 = new LinearLayout(this);
        row2.setOrientation(LinearLayout.HORIZONTAL);
        row2.addView(button("DOWNLOAD", v -> downloadSelected()), weighted());
        row2.addView(button("OPEN", v -> openSelected()), weighted());
        row2.addView(button("REPORT", v -> downloadReport()), weighted());
        root.addView(row2, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(48)));

        statusView = new TextView(this);
        statusView.setTextSize(10.2f);
        statusView.setTextIsSelectable(true);
        statusView.setPadding(dp(8), dp(5), dp(8), dp(5));
        ScrollView statusScroll = new ScrollView(this);
        statusScroll.addView(statusView, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));
        root.addView(statusScroll, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(300)));

        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setJavaScriptCanOpenWindowsAutomatically(true);
        settings.setLoadWithOverviewMode(false);
        settings.setUseWideViewPort(false);
        cm.setAcceptThirdPartyCookies(webView, true);

        webView.setDownloadListener(new DownloadListener() {
            @Override public void onDownloadStart(String url, String userAgent, String contentDisposition,
                                                  String mimetype, long contentLength) {
                recordEvent("WEBVIEW_DOWNLOAD_LISTENER");
                if (!pendingActionListener) {
                    downloadStatus = "PASSIVE_DOWNLOAD_LISTENER_OBSERVED";
                    renderStatus();
                    return;
                }
                pendingActionListener = false;
                String nowCid = extractCanonicalConversationId(sanitizeUrl(webView.getUrl()));
                if (!pendingActionCid.equals(nowCid)) {
                    downloadStatus = "UNCERTAIN_ACTION_ROUTE_CHANGED";
                    prefs.edit().putString("action_claim_status", "UNCERTAIN").commit();
                    renderStatus();
                    return;
                }
                Resource callback = Resource.fromDownloadCallback(
                        pendingActionResourceId, pendingActionCid, url, mimetype, contentDisposition, contentLength);
                recordEvent("DOWNLOAD_ACTION_LISTENER_RECEIPT");
                executeResolvedDownload(callback, true);
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
                if (isTrustedChatGptUrl(url)) installRegistry();
                super.onPageFinished(view, url);
            }

            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return false;
            }
        });

        root.addView(webView, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));
        setContentView(root);
        webView.loadUrl("https://chatgpt.com/");
        handler.post(routeProbe);
        renderStatus();
    }

    private Button button(String text, android.view.View.OnClickListener listener) {
        Button b = new Button(this);
        b.setText(text);
        b.setTextSize(9.5f);
        b.setOnClickListener(listener);
        return b;
    }

    private LinearLayout.LayoutParams weighted() {
        return new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f);
    }

    private void installRegistry() {
        if (webView == null || !isTrustedChatGptUrl(webView.getUrl())) return;
        webView.evaluateJavascript(installRegistryJs(), ignored -> { });
    }

    private String installRegistryJs() {
        return "(function(){try{"
                + "if(window.__cpResourceRegistryV09){window.__cpResourceRegistryV09.scan();return 'EXISTS';}"
                + "const norm=(x)=>(x||'').replace(/\\s+/g,' ').trim();"
                + "const vis=(e)=>{try{const r=e.getBoundingClientRect();const s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
                + "const h=(s)=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return ('00000000'+x.toString(16)).slice(-8);};"
                + "const reg={items:{},visibleTurns:0};"
                + "const put=(el,kind,href,label,dl,turn,idx)=>{"
                + "const role=turn?String(turn.getAttribute('data-message-author-role')||'-'):'-';"
                + "const turnText=turn?norm(turn.innerText||turn.textContent||''):'';"
                + "let full='';try{full=href?String(new URL(href,location.href).href):'';}catch(_){full=String(href||'');}"
                + "let scheme='';let host='';let path='';let same=false;try{const u=new URL(full);scheme=u.protocol.replace(':','');host=u.host;path=u.pathname;same=u.origin===location.origin;}catch(_){scheme=full.startsWith('blob:')?'blob':(full.startsWith('data:')?'data':'');}"
                + "const key=h(role+'|'+h(turnText)+'|'+kind+'|'+full+'|'+norm(label));"
                + "reg.items[key]={id:key,kind:kind,href:full,label:norm(label),downloadAttr:norm(dl),turnRole:role,turnText:turnText,turnIndex:idx,scheme:scheme,host:host,path:path,sameOrigin:same};"
                + "try{el.setAttribute('data-cp-resource-v09',key);}catch(_){}"
                + "};"
                + "reg.scan=()=>{"
                + "const turns=Array.from(document.querySelectorAll('[data-message-author-role]'));reg.visibleTurns=turns.length;"
                + "turns.forEach((turn,idx)=>{"
                + "turn.querySelectorAll('a[href]').forEach(a=>put(a,'LINK',a.getAttribute('href')||'',a.getAttribute('aria-label')||a.innerText||a.textContent||'',a.getAttribute('download')||'',turn,idx));"
                + "turn.querySelectorAll('button,[role=\\\"button\\\"]').forEach(b=>{if(!vis(b))return;const lab=norm(b.getAttribute('aria-label')||b.innerText||b.textContent||'');const low=lab.toLowerCase();if(/download|save|open file|view file|document|attachment|file|pdf|دانلود|فایل/.test(low)){put(b,'ACTION','',lab,'',turn,idx);}});"
                + "});return Object.keys(reg.items).length;};"
                + "reg.scan();"
                + "reg.observer=new MutationObserver(()=>{try{reg.scan();}catch(_){}});"
                + "reg.observer.observe(document.documentElement||document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['href','aria-label','download']});"
                + "window.__cpResourceRegistryV09=reg;return 'INSTALLED';"
                + "}catch(e){return 'ERR:'+String(e);}})();";
    }

    private void scanResources() {
        if (webView == null || !isTrustedChatGptUrl(webView.getUrl())) {
            scanStatus = "FAIL_NOT_CHATGPT_ORIGIN";
            renderStatus();
            return;
        }
        String cid = extractCanonicalConversationId(sanitizeUrl(webView.getUrl()));
        if ("-".equals(cid)) {
            scanStatus = "FAIL_NO_CANONICAL_CHAT";
            renderStatus();
            return;
        }
        installRegistry();
        handler.postDelayed(() -> webView.evaluateJavascript(registrySnapshotJs(), value -> {
            try {
                JSONObject root = jsonObject(value);
                JSONArray arr = root.optJSONArray("items");
                resources.clear();
                if (arr != null) {
                    for (int i = 0; i < arr.length(); i++) {
                        JSONObject o = arr.optJSONObject(i);
                        if (o == null) continue;
                        Resource r = Resource.fromJson(o, cid);
                        r.resourceClass = classify(r);
                        resources.add(r);
                    }
                }
                scanCid = cid;
                scanVisibleTurnCount = root.optInt("visibleTurns", -1);
                scanRegistryCount = resources.size();
                scanStatus = "COMPLETE";
                selectedResourceId = "-";
                selectedResourceIndex = -1;
                selectedResourceClass = "-";
                recordEvent("RESOURCE_SCAN_COMPLETE count=" + resources.size());
            } catch (Exception e) {
                scanStatus = "FAIL_PARSE_" + e.getClass().getSimpleName();
            }
            renderStatus();
        }), 250L);
    }

    private String registrySnapshotJs() {
        return "(function(){try{const r=window.__cpResourceRegistryV09;if(!r)return JSON.stringify({error:'NO_REGISTRY',visibleTurns:-1,items:[]});r.scan();return JSON.stringify({visibleTurns:r.visibleTurns,items:Object.values(r.items)});}catch(e){return JSON.stringify({error:String(e),visibleTurns:-1,items:[]});}})();";
    }

    private Resource selectedResource() {
        if (!"COMPLETE".equals(scanStatus) || resources.isEmpty()) {
            Toast.makeText(this, "Run SCAN first", Toast.LENGTH_LONG).show();
            return null;
        }
        int idx;
        try { idx = Integer.parseInt(resourceIndexInput.getText().toString().trim()) - 1; }
        catch (Exception e) {
            Toast.makeText(this, "Enter a resource number from SCAN", Toast.LENGTH_LONG).show();
            return null;
        }
        if (idx < 0 || idx >= resources.size()) {
            Toast.makeText(this, "Resource number out of range", Toast.LENGTH_LONG).show();
            return null;
        }
        Resource r = resources.get(idx);
        String cid = extractCanonicalConversationId(sanitizeUrl(webView.getUrl()));
        if (!r.cid.equals(cid)) {
            downloadStatus = "BLOCKED_CONVERSATION_CHANGED";
            renderStatus();
            return null;
        }
        selectedResourceId = r.id;
        selectedResourceIndex = idx + 1;
        selectedResourceClass = r.resourceClass;
        return r;
    }

    private void downloadSelected() {
        if (downloadBusy) {
            Toast.makeText(this, "Download already running", Toast.LENGTH_LONG).show();
            return;
        }
        Resource r = selectedResource();
        if (r == null) return;
        resetDownloadReceipt();
        selectedResourceId = r.id;
        selectedResourceClass = r.resourceClass;
        executeResolvedDownload(r, false);
    }

    private void executeResolvedDownload(Resource r, boolean fromActionListener) {
        String c = r.resourceClass;
        if ("ACTION".equals(c) && !fromActionListener) {
            beginActionDownload(r);
            return;
        }
        if ("SAME_ORIGIN".equals(c) || "BLOB".equals(c) || "DATA".equals(c)) {
            startPageFetchPull(r);
            return;
        }
        if ("CROSS_ORIGIN_DIRECT".equals(c)) {
            startPublicDirectDownload(r);
            return;
        }
        if ("EXTERNAL_NAVIGATION".equals(c)) {
            downloadStatus = "NEEDS_EXTERNAL_NAVIGATION";
            downloadStrategy = "TRUST_ZONE_EXTERNAL";
            recordEvent("DOWNLOAD_BLOCKED_EXTERNAL_NAVIGATION_REQUIRED");
            renderStatus();
            return;
        }
        downloadStatus = "BLOCKED_UNSUPPORTED_RESOURCE";
        downloadStrategy = "NONE";
        renderStatus();
    }

    private void beginActionDownload(Resource r) {
        String prior = prefs.getString("action_claim_status", "-");
        if ("CLAIMED".equals(prior) || "DISPATCHED".equals(prior) || "UNCERTAIN".equals(prior)) {
            downloadStatus = "BLOCKED_UNRESOLVED_ACTION_CLAIM";
            downloadStrategy = "ACTION_CLICK";
            renderStatus();
            return;
        }
        prefs.edit()
                .putString("action_claim_status", "CLAIMED")
                .putString("action_claim_resource", sha256Quiet(r.id + "|" + r.cid))
                .commit();
        pendingActionResourceId = r.id;
        pendingActionCid = r.cid;
        pendingActionListener = true;
        pendingActionStartedAt = System.currentTimeMillis();
        downloadStatus = "ACTION_CLAIMED";
        downloadStrategy = "ACTION_CLICK_WAIT_DOWNLOAD_LISTENER";
        recordEvent("DOWNLOAD_ACTION_DURABLE_CLAIMED");
        webView.evaluateJavascript(clickTaggedResourceJs(r.id), value -> {
            String token = cleanJsScalar(value);
            if (!"CLICKED_1".equals(token)) {
                pendingActionListener = false;
                downloadStatus = "BLOCKED_ACTION_" + safeToken(token);
                prefs.edit().putString("action_claim_status", "-").commit();
                recordEvent("DOWNLOAD_ACTION_NOT_DISPATCHED " + safeToken(token));
            } else {
                prefs.edit().putString("action_claim_status", "DISPATCHED").commit();
                downloadStatus = "ACTION_DISPATCHED_WAIT_RECEIPT";
                recordEvent("DOWNLOAD_ACTION_SINGLE_CLICK_DISPATCHED");
            }
            renderStatus();
        });
    }

    private String clickTaggedResourceJs(String id) {
        return "(function(){try{const all=Array.from(document.querySelectorAll('[data-cp-resource-v09=\\\"" + js(id) + "\\\"]'));const vis=all.filter(e=>{const r=e.getBoundingClientRect();const s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';});if(vis.length!==1)return 'MATCHES_'+vis.length;const e=vis[0];if(e.disabled||e.getAttribute('aria-disabled')==='true')return 'DISABLED';e.click();return 'CLICKED_1';}catch(e){return 'ERR';}})();";
    }

    private void startPageFetchPull(Resource r) {
        if (downloadBusy) return;
        downloadBusy = true;
        downloadStatus = "PAGE_FETCH_STARTING";
        downloadStrategy = "PAGE_CONTEXT_FETCH_PULL";
        downloadReceiptId = UUID.randomUUID().toString();
        recordEvent("DOWNLOAD_PAGE_FETCH_START");
        webView.evaluateJavascript(beginPageFetchJs(r.id, r.href), value -> {
            String token = cleanJsScalar(value);
            if (!"STARTED".equals(token)) {
                finishDownloadFailure("FAIL_PAGE_FETCH_START_" + safeToken(token));
                return;
            }
            new Thread(() -> pullPreparedPageBytes(r), "cp-resource-pull").start();
        });
    }

    private String beginPageFetchJs(String id, String fallbackHref) {
        return "(function(){try{"
                + "const reg=window.__cpResourceRegistryV09;const item=reg&&reg.items?reg.items['" + js(id) + "']:null;"
                + "const href=item&&item.href?item.href:'" + js(fallbackHref) + "';if(!href)return 'NO_HREF';"
                + "window.__cpDownloadStateV09={status:'FETCHING',size:0,mime:'',error:''};window.__cpDownloadBytesV09=null;"
                + "(async()=>{try{const u=new URL(href,location.href);const opt=(u.origin===location.origin)?{credentials:'same-origin',redirect:'follow'}:{credentials:'omit',redirect:'follow'};"
                + "const res=await fetch(href,opt);const mime=(res.headers.get('content-type')||'').split(';')[0].trim();"
                + "if(!res.ok){window.__cpDownloadStateV09={status:'FAIL_HTTP',code:res.status,size:0,mime:mime,error:''};return;}"
                + "if(/^text\\/html/i.test(mime)){window.__cpDownloadStateV09={status:'HTML_NAVIGATION',size:0,mime:mime,error:''};return;}"
                + "const b=await res.blob();if(b.size>" + MAX_PAGE_FETCH_BYTES + "){window.__cpDownloadStateV09={status:'TOO_LARGE',size:b.size,mime:(mime||b.type||''),error:''};return;}"
                + "const buf=await b.arrayBuffer();window.__cpDownloadBytesV09=new Uint8Array(buf);window.__cpDownloadStateV09={status:'READY',size:buf.byteLength,mime:(mime||b.type||'application/octet-stream'),error:''};"
                + "}catch(e){window.__cpDownloadStateV09={status:'FAIL_FETCH',size:0,mime:'',error:String(e&&e.name?e.name:'Error')};}})();return 'STARTED';"
                + "}catch(e){return 'ERR';}})();";
    }

    private void pullPreparedPageBytes(Resource r) {
        try {
            JSONObject state = null;
            long deadline = System.currentTimeMillis() + 90000L;
            while (System.currentTimeMillis() < deadline) {
                state = jsonObject(evalJsBlocking("JSON.stringify(window.__cpDownloadStateV09||{status:'MISSING'})"));
                String s = state.optString("status", "MISSING");
                if (!"FETCHING".equals(s)) break;
                Thread.sleep(250L);
            }
            if (state == null) throw new IllegalStateException("NO_STATE");
            String status = state.optString("status", "MISSING");
            if ("HTML_NAVIGATION".equals(status)) {
                finishDownloadFailure("NEEDS_EXTERNAL_NAVIGATION_HTML");
                return;
            }
            if ("TOO_LARGE".equals(status)) {
                finishDownloadFailure("BLOCKED_PAGE_FILE_GT_96_MIB");
                return;
            }
            if (!"READY".equals(status)) {
                finishDownloadFailure("FAIL_PAGE_FETCH_" + safeToken(status));
                return;
            }
            long size = state.optLong("size", -1L);
            String mime = safeMime(state.optString("mime", "application/octet-stream"));
            if (size < 0L || size > MAX_PAGE_FETCH_BYTES) {
                finishDownloadFailure("FAIL_PAGE_SIZE");
                return;
            }
            MediaTarget target = createMediaTarget(mime);
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            long offset = 0L;
            int chunks = 0;
            try (OutputStream out = getContentResolver().openOutputStream(target.uri, "w")) {
                if (out == null) throw new IllegalStateException("NO_OUTPUT");
                while (offset < size) {
                    int len = (int) Math.min(PULL_CHUNK_BYTES, size - offset);
                    String encoded = cleanJsScalar(evalJsBlocking(readPageChunkJs(offset, len)));
                    if (encoded == null || encoded.isEmpty() || "-".equals(encoded)) throw new IllegalStateException("EMPTY_CHUNK");
                    byte[] bytes = Base64.decode(encoded, Base64.DEFAULT);
                    if (bytes.length == 0) throw new IllegalStateException("ZERO_CHUNK");
                    out.write(bytes);
                    md.update(bytes);
                    offset += bytes.length;
                    chunks++;
                }
            } catch (Exception e) {
                getContentResolver().delete(target.uri, null, null);
                throw e;
            }
            publishMediaTarget(target);
            evalJsBlocking("(function(){window.__cpDownloadBytesV09=null;window.__cpDownloadStateV09={status:'CLEARED'};return 'OK';})()");
            final long finalSize = offset;
            final int finalChunks = chunks;
            final String finalMime = mime;
            final String finalSha = hex(md.digest());
            runOnUiThread(() -> finishDownloadSuccess(finalSize, finalChunks, finalMime, finalSha,
                    "PAGE_CONTEXT_FETCH_PULL", r));
        } catch (Exception e) {
            try { evalJsBlocking("(function(){window.__cpDownloadBytesV09=null;return 'OK';})()"); } catch (Exception ignored) { }
            finishDownloadFailure("FAIL_PAGE_PULL_" + e.getClass().getSimpleName());
        }
    }

    private String readPageChunkJs(long offset, int len) {
        return "(function(){try{const b=window.__cpDownloadBytesV09;if(!b)return '-';const x=b.slice(" + offset + "," + (offset + len) + ");let s='';const step=0x8000;for(let i=0;i<x.length;i+=step){s+=String.fromCharCode.apply(null,x.subarray(i,Math.min(i+step,x.length)));}return btoa(s);}catch(e){return '-';}})();";
    }

    private void startPublicDirectDownload(Resource r) {
        if (downloadBusy) return;
        if (!r.href.toLowerCase(Locale.US).startsWith("https://")) {
            downloadStatus = "BLOCKED_EXTERNAL_NON_HTTPS";
            downloadStrategy = "TRUST_ZONE_EXTERNAL";
            renderStatus();
            return;
        }
        downloadBusy = true;
        downloadStatus = "PUBLIC_DIRECT_STARTING";
        downloadStrategy = "NATIVE_PUBLIC_NO_COOKIE";
        downloadReceiptId = UUID.randomUUID().toString();
        recordEvent("DOWNLOAD_PUBLIC_NO_COOKIE_START");
        new Thread(() -> {
            HttpURLConnection conn = null;
            try {
                URL url = new URL(r.href);
                conn = (HttpURLConnection) url.openConnection();
                conn.setInstanceFollowRedirects(true);
                conn.setConnectTimeout(15000);
                conn.setReadTimeout(45000);
                conn.setRequestMethod("GET");
                conn.setRequestProperty("User-Agent", webView.getSettings().getUserAgentString());
                conn.setRequestProperty("Accept", "*/*");
                int code = conn.getResponseCode();
                if (code < 200 || code >= 300) {
                    finishDownloadFailure("FAIL_PUBLIC_HTTP_" + code);
                    return;
                }
                String mime = safeMime(conn.getContentType());
                if (mime.toLowerCase(Locale.US).startsWith("text/html")) {
                    finishDownloadFailure("NEEDS_EXTERNAL_NAVIGATION_HTML");
                    return;
                }
                long declared = conn.getContentLengthLong();
                if (declared > MAX_PUBLIC_DOWNLOAD_BYTES) {
                    finishDownloadFailure("BLOCKED_PUBLIC_FILE_GT_128_MIB");
                    return;
                }
                MediaTarget target = createMediaTarget(mime);
                MessageDigest md = MessageDigest.getInstance("SHA-256");
                long total = 0L;
                int chunks = 0;
                byte[] buf = new byte[64 * 1024];
                try (InputStream in = conn.getInputStream(); OutputStream out = getContentResolver().openOutputStream(target.uri, "w")) {
                    if (out == null) throw new IllegalStateException("NO_OUTPUT");
                    int n;
                    while ((n = in.read(buf)) >= 0) {
                        if (n == 0) continue;
                        total += n;
                        if (total > MAX_PUBLIC_DOWNLOAD_BYTES) {
                            getContentResolver().delete(target.uri, null, null);
                            finishDownloadFailure("BLOCKED_PUBLIC_FILE_GT_128_MIB");
                            return;
                        }
                        out.write(buf, 0, n);
                        md.update(buf, 0, n);
                        chunks++;
                    }
                } catch (Exception e) {
                    getContentResolver().delete(target.uri, null, null);
                    throw e;
                }
                publishMediaTarget(target);
                final long finalTotal = total;
                final int finalChunks = chunks;
                final String finalMime = mime;
                final String finalSha = hex(md.digest());
                runOnUiThread(() -> finishDownloadSuccess(finalTotal, finalChunks, finalMime, finalSha,
                        "NATIVE_PUBLIC_NO_COOKIE", r));
            } catch (Exception e) {
                finishDownloadFailure("FAIL_PUBLIC_" + e.getClass().getSimpleName());
            } finally {
                if (conn != null) conn.disconnect();
            }
        }, "cp-public-download").start();
    }

    private void finishDownloadSuccess(long bytes, int chunks, String mime, String sha,
                                       String strategy, Resource r) {
        downloadBusy = false;
        downloadStatus = "CONFIRMED";
        downloadBytes = bytes;
        downloadChunks = chunks;
        downloadMime = mime;
        downloadSha256 = sha;
        downloadStrategy = strategy;
        if (pendingActionResourceId.equals(r.id)) {
            prefs.edit().putString("action_claim_status", "CONFIRMED").commit();
        }
        recordEvent("DOWNLOAD_CONFIRMED strategy=" + strategy + " bytes=" + bytes);
        Toast.makeText(this, "Download confirmed in Downloads/ChatGPTWebViewProbe", Toast.LENGTH_LONG).show();
        renderStatus();
    }

    private void finishDownloadFailure(String status) {
        runOnUiThread(() -> {
            downloadBusy = false;
            downloadStatus = status;
            if (status.startsWith("UNCERTAIN") && !"-".equals(pendingActionResourceId)) {
                prefs.edit().putString("action_claim_status", "UNCERTAIN").commit();
            }
            recordEvent("DOWNLOAD_END " + safeToken(status));
            renderStatus();
        });
    }

    private void openSelected() {
        Resource r = selectedResource();
        if (r == null) return;
        if (!(r.href.startsWith("http://") || r.href.startsWith("https://"))) {
            Toast.makeText(this, "This resource is not an external HTTP(S) navigation", Toast.LENGTH_LONG).show();
            return;
        }
        try {
            URI u = URI.create(r.href);
            String host = safe(u.getHost()).toLowerCase(Locale.US);
            if (isTrustedChatGptHost(host)) {
                webView.loadUrl(r.href);
                recordEvent("OPEN_TRUSTED_IN_WEBVIEW");
            } else {
                Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse(r.href));
                startActivity(i);
                recordEvent("OPEN_EXTERNAL_SYSTEM_BROWSER");
            }
        } catch (Exception e) {
            Toast.makeText(this, "Could not open resource", Toast.LENGTH_LONG).show();
        }
        renderStatus();
    }

    private MediaTarget createMediaTarget(String mime) throws Exception {
        String ext = MimeTypeMap.getSingleton().getExtensionFromMimeType(mime);
        if (ext == null || ext.trim().isEmpty() || ext.length() > 8) ext = "bin";
        String name = "chatgpt-resource-" + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + "." + ext;
        ContentValues values = new ContentValues();
        values.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
        values.put(MediaStore.MediaColumns.MIME_TYPE, mime);
        values.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
        values.put(MediaStore.MediaColumns.IS_PENDING, 1);
        Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
        if (uri == null) throw new IllegalStateException("MEDIASTORE_INSERT");
        return new MediaTarget(uri);
    }

    private void publishMediaTarget(MediaTarget target) {
        ContentValues done = new ContentValues();
        done.put(MediaStore.MediaColumns.IS_PENDING, 0);
        getContentResolver().update(target.uri, done, null, null);
    }

    private void resetDownloadReceipt() {
        downloadStatus = "NOT_RUN";
        downloadStrategy = "-";
        downloadMime = "-";
        downloadBytes = 0L;
        downloadSha256 = "-";
        downloadChunks = 0;
        downloadReceiptId = "-";
        pendingActionResourceId = "-";
        pendingActionCid = "-";
        pendingActionListener = false;
        pendingActionStartedAt = 0L;
    }

    private String classify(Resource r) {
        if ("ACTION".equals(r.kind)) return "ACTION";
        String scheme = safe(r.scheme).toLowerCase(Locale.US);
        if ("blob".equals(scheme)) return "BLOB";
        if ("data".equals(scheme)) return "DATA";
        if (("http".equals(scheme) || "https".equals(scheme)) && r.sameOrigin) return "SAME_ORIGIN";
        if ("https".equals(scheme) && looksDirectDownload(r)) return "CROSS_ORIGIN_DIRECT";
        if ("http".equals(scheme) || "https".equals(scheme)) return "EXTERNAL_NAVIGATION";
        return "OTHER";
    }

    private boolean looksDirectDownload(Resource r) {
        if (!safe(r.downloadAttr).isEmpty()) return true;
        String p = safe(r.path).toLowerCase(Locale.US);
        String l = safe(r.label).toLowerCase(Locale.US);
        if (p.matches(".*\\.(pdf|zip|csv|txt|json|doc|docx|xls|xlsx|ppt|pptx|png|jpg|jpeg|webp|gif|mp3|mp4|wav)(?:$|/).*")) return true;
        return l.contains("download") || l.contains("save") || l.contains("pdf") || l.contains("دانلود") || l.contains("فایل");
    }

    private void renderStatus() {
        if (statusView == null) return;
        StringBuilder s = new StringBuilder();
        s.append("STABLE v0.9 RESOURCE SUITE\n");
        s.append("URL: ").append(sanitizeUrl(webView == null ? "-" : webView.getUrl())).append('\n');
        s.append("CID: ").append(extractCanonicalConversationId(sanitizeUrl(webView == null ? "-" : webView.getUrl()))).append('\n');
        s.append("SCAN: ").append(scanStatus).append(" resources=").append(resources.size())
                .append(" visibleTurns=").append(scanVisibleTurnCount).append('\n');
        s.append("SELECTED: #").append(selectedResourceIndex).append(" class=").append(selectedResourceClass).append('\n');
        s.append("DOWNLOAD: ").append(downloadStatus).append(" strategy=").append(downloadStrategy).append('\n');
        if (!"-".equals(downloadSha256)) {
            s.append("RECEIPT: bytes=").append(downloadBytes).append(" mime=").append(downloadMime)
                    .append(" sha=").append(shortHash(downloadSha256)).append('\n');
        }
        s.append("\nRESOURCE INDEX (transient labels; URLs sanitized):\n");
        int cap = Math.min(resources.size(), 30);
        for (int i = 0; i < cap; i++) {
            Resource r = resources.get(i);
            s.append(i + 1).append(") [").append(r.resourceClass).append("] ")
                    .append(clip(r.label, 54)).append(" | ").append(safeHostPath(r)).append('\n');
        }
        if (resources.size() > cap) s.append("... +").append(resources.size() - cap).append(" more\n");
        statusView.setText(s.toString());
    }

    private void downloadReport() {
        try {
            String report = buildReport();
            String name = "chatgpt-webview-v09-resource-report-"
                    + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".txt";
            ContentValues values = new ContentValues();
            values.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            values.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
            values.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
            values.put(MediaStore.MediaColumns.IS_PENDING, 1);
            Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
            if (uri == null) throw new IllegalStateException("insert");
            try (OutputStream out = getContentResolver().openOutputStream(uri, "w")) {
                if (out == null) throw new IllegalStateException("stream");
                out.write(report.getBytes(StandardCharsets.UTF_8));
            }
            ContentValues done = new ContentValues();
            done.put(MediaStore.MediaColumns.IS_PENDING, 0);
            getContentResolver().update(uri, done, null, null);
            Toast.makeText(this, "Report saved to Downloads/ChatGPTWebViewProbe", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "Report failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
        }
    }

    private String buildReport() {
        StringBuilder r = new StringBuilder();
        String current = sanitizeUrl(webView == null ? "-" : webView.getUrl());
        r.append("CHATGPT_WEBVIEW_STABLE_V09_SEMANTIC_RESOURCE_SUITE\n");
        r.append("CURRENT_URL=").append(current).append('\n');
        r.append("CURRENT_CONVERSATION_ID=").append(extractCanonicalConversationId(current)).append('\n');
        r.append("SCAN_STATUS=").append(scanStatus).append('\n');
        r.append("SCAN_VISIBLE_TURNS=").append(scanVisibleTurnCount).append('\n');
        r.append("SCAN_REGISTRY_COUNT=").append(scanRegistryCount).append('\n');
        r.append("SELECTED_RESOURCE_INDEX=").append(selectedResourceIndex).append('\n');
        r.append("SELECTED_RESOURCE_CLASS=").append(selectedResourceClass).append('\n');
        r.append("DOWNLOAD_STATUS=").append(downloadStatus).append('\n');
        r.append("DOWNLOAD_STRATEGY=").append(downloadStrategy).append('\n');
        r.append("DOWNLOAD_MIME=").append(downloadMime).append('\n');
        r.append("DOWNLOAD_BYTES=").append(downloadBytes).append('\n');
        r.append("DOWNLOAD_CHUNKS=").append(downloadChunks).append('\n');
        r.append("DOWNLOAD_SHA256=").append(downloadSha256).append('\n');
        r.append("DOWNLOAD_RECEIPT_ID=").append(downloadReceiptId).append('\n');
        r.append("RAW_CHAT_TEXT_RETAINED=false\n");
        r.append("RAW_RESOURCE_LABEL_RETAINED_IN_REPORT=false\n");
        r.append("RAW_RESOURCE_URL_OR_QUERY_RETAINED_IN_REPORT=false\n");
        r.append("CHATGPT_COOKIES_EXTRACTED=false\n");
        r.append("EXTERNAL_DOWNLOAD_COOKIE_FORWARDING=false\n");
        r.append("--- RESOURCE INDEX (SANITIZED/HASHED) ---\n");
        for (int i = 0; i < resources.size(); i++) {
            Resource x = resources.get(i);
            r.append('#').append(i + 1)
                    .append(" class=").append(x.resourceClass)
                    .append(" kind=").append(x.kind)
                    .append(" role=").append(x.turnRole)
                    .append(" turnIndex=").append(x.turnIndex)
                    .append(" turnSha=").append(sha256Quiet(x.turnText))
                    .append(" labelSha=").append(sha256Quiet(x.label))
                    .append(" hrefSha=").append(sha256Quiet(x.href))
                    .append(" safe=").append(safeHostPath(x))
                    .append(" sameOrigin=").append(x.sameOrigin)
                    .append('\n');
        }
        r.append("--- EVENT LOG (SANITIZED; NO QUERY/FRAGMENT) ---\n");
        r.append(eventLog);
        return r.toString();
    }

    private void recordEvent(String event) {
        if (eventLog.length() > 30000) eventLog.delete(0, Math.min(8000, eventLog.length()));
        eventLog.append(new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date()))
                .append(" | ").append(event).append(" | ")
                .append(sanitizeUrl(webView == null ? "-" : webView.getUrl()))
                .append('\n');
    }

    private void recordRoute(String event, String url) {
        if (eventLog.length() > 30000) eventLog.delete(0, Math.min(8000, eventLog.length()));
        eventLog.append(new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date()))
                .append(" | ").append(event).append(" | ").append(sanitizeUrl(url)).append('\n');
    }

    private String safeHostPath(Resource r) {
        if ("blob".equals(r.scheme)) return "blob:<opaque>";
        if ("data".equals(r.scheme)) return "data:<inline>";
        String h = safe(r.host);
        String p = safe(r.path);
        if (h.isEmpty() && p.isEmpty()) return "-";
        return h + p;
    }

    private static boolean isTrustedChatGptUrl(String url) {
        try {
            URI u = URI.create(url);
            return "https".equalsIgnoreCase(u.getScheme()) && isTrustedChatGptHost(safe(u.getHost()).toLowerCase(Locale.US));
        } catch (Exception e) { return false; }
    }

    private static boolean isTrustedChatGptHost(String host) {
        return "chatgpt.com".equals(host) || host.endsWith(".chatgpt.com");
    }

    private static String sanitizeUrl(String raw) {
        try {
            if (raw == null || raw.trim().isEmpty()) return "-";
            URI u = URI.create(raw);
            String scheme = safe(u.getScheme());
            String host = safe(u.getHost());
            String path = safe(u.getRawPath());
            if (!scheme.isEmpty() && !host.isEmpty()) return scheme + "://" + host + (path.isEmpty() ? "/" : path);
            if (raw.startsWith("blob:")) return "blob:<opaque>";
            if (raw.startsWith("data:")) return "data:<inline>";
            int q = raw.indexOf('?');
            int f = raw.indexOf('#');
            int cut = raw.length();
            if (q >= 0) cut = Math.min(cut, q);
            if (f >= 0) cut = Math.min(cut, f);
            return raw.substring(0, cut);
        } catch (Exception e) { return "-"; }
    }

    private static String extractCanonicalConversationId(String safeUrl) {
        try {
            URI u = URI.create(safeUrl);
            String path = safe(u.getPath());
            String[] parts = path.split("/");
            for (int i = 0; i < parts.length - 1; i++) {
                if ("c".equals(parts[i])) {
                    String id = parts[i + 1];
                    if (UUID_PATTERN.matcher(id).matches()) return id;
                    return "-";
                }
            }
        } catch (Exception ignored) { }
        return "-";
    }

    private String evalJsBlocking(String script) throws Exception {
        CountDownLatch latch = new CountDownLatch(1);
        AtomicReference<String> value = new AtomicReference<>(null);
        AtomicReference<Throwable> error = new AtomicReference<>(null);
        runOnUiThread(() -> {
            try {
                webView.evaluateJavascript(script, v -> { value.set(v); latch.countDown(); });
            } catch (Throwable t) {
                error.set(t);
                latch.countDown();
            }
        });
        if (!latch.await(30, TimeUnit.SECONDS)) throw new IllegalStateException("JS_TIMEOUT");
        if (error.get() != null) throw new IllegalStateException("JS_ERROR", error.get());
        return value.get();
    }

    private static JSONObject jsonObject(String value) throws Exception {
        Object first = new JSONTokener(value == null ? "null" : value).nextValue();
        if (first instanceof JSONObject) return (JSONObject) first;
        if (first instanceof String) {
            Object second = new JSONTokener((String) first).nextValue();
            if (second instanceof JSONObject) return (JSONObject) second;
        }
        throw new IllegalArgumentException("NOT_OBJECT");
    }

    private static String cleanJsScalar(String value) {
        try {
            Object o = new JSONTokener(value == null ? "null" : value).nextValue();
            return o == null || o == JSONObject.NULL ? "-" : String.valueOf(o);
        } catch (Exception e) { return safe(value).replace("\"", ""); }
    }

    private static String sha256Quiet(String text) {
        try {
            MessageDigest d = MessageDigest.getInstance("SHA-256");
            return hex(d.digest(safe(text).getBytes(StandardCharsets.UTF_8)));
        } catch (Exception e) { return "-"; }
    }

    private static String hex(byte[] data) {
        StringBuilder b = new StringBuilder(data.length * 2);
        for (byte x : data) b.append(String.format(Locale.US, "%02x", x & 0xff));
        return b.toString();
    }

    private static String shortHash(String h) {
        return h == null || h.length() < 12 ? safe(h) : h.substring(0, 12);
    }

    private static String safeMime(String raw) {
        String m = safe(raw).split(";")[0].trim().toLowerCase(Locale.US);
        if (m.isEmpty() || !m.contains("/")) return "application/octet-stream";
        return m;
    }

    private static String js(String s) {
        return safe(s).replace("\\", "\\\\").replace("'", "\\'").replace("\r", " ").replace("\n", " ");
    }

    private static String clip(String s, int max) {
        String x = safe(s);
        return x.length() <= max ? x : x.substring(0, max - 1) + "…";
    }

    private static String safeToken(String s) {
        String x = safe(s).replaceAll("[^A-Za-z0-9_.-]", "_");
        return x.length() > 64 ? x.substring(0, 64) : x;
    }

    private static String safe(String s) { return s == null ? "" : s; }

    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    @Override protected void onPause() {
        CookieManager.getInstance().flush();
        super.onPause();
    }

    @Override protected void onDestroy() {
        handler.removeCallbacks(routeProbe);
        if (webView != null) webView.destroy();
        super.onDestroy();
    }

    private static final class MediaTarget {
        final Uri uri;
        MediaTarget(Uri uri) { this.uri = uri; }
    }

    private static final class Resource {
        String id = "-";
        String cid = "-";
        String kind = "-";
        String href = "";
        String label = "";
        String downloadAttr = "";
        String turnRole = "-";
        String turnText = "";
        int turnIndex = -1;
        String scheme = "";
        String host = "";
        String path = "";
        boolean sameOrigin = false;
        String resourceClass = "OTHER";

        static Resource fromJson(JSONObject o, String cid) {
            Resource r = new Resource();
            r.id = o.optString("id", "-");
            r.cid = cid;
            r.kind = o.optString("kind", "-");
            r.href = o.optString("href", "");
            r.label = o.optString("label", "");
            r.downloadAttr = o.optString("downloadAttr", "");
            r.turnRole = o.optString("turnRole", "-");
            r.turnText = o.optString("turnText", "");
            r.turnIndex = o.optInt("turnIndex", -1);
            r.scheme = o.optString("scheme", "");
            r.host = o.optString("host", "");
            r.path = o.optString("path", "");
            r.sameOrigin = o.optBoolean("sameOrigin", false);
            return r;
        }

        static Resource fromDownloadCallback(String id, String cid, String url, String mime,
                                             String disposition, long length) {
            Resource r = new Resource();
            r.id = id;
            r.cid = cid;
            r.kind = "DOWNLOAD_CALLBACK";
            r.href = safe(url);
            r.downloadAttr = safe(disposition);
            try {
                URI u = URI.create(r.href);
                r.scheme = safe(u.getScheme()).toLowerCase(Locale.US);
                r.host = safe(u.getHost());
                r.path = safe(u.getPath());
                r.sameOrigin = isTrustedChatGptHost(r.host.toLowerCase(Locale.US));
            } catch (Exception ignored) { }
            if ("blob".equals(r.scheme)) r.resourceClass = "BLOB";
            else if ("data".equals(r.scheme)) r.resourceClass = "DATA";
            else if (r.sameOrigin) r.resourceClass = "SAME_ORIGIN";
            else if (r.href.startsWith("https://")) r.resourceClass = "CROSS_ORIGIN_DIRECT";
            else r.resourceClass = "OTHER";
            return r;
        }
    }
}
