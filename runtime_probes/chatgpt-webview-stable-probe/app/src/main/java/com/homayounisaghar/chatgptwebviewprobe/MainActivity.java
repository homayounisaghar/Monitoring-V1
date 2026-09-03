package com.homayounisaghar.chatgptwebviewprobe;

import android.app.Activity;
import android.content.ContentValues;
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
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Space;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.regex.Pattern;

public class MainActivity extends Activity {
    private static final Pattern UUID_PATTERN = Pattern.compile(
            "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$");

    private WebView webView;
    private TextView statusView;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final StringBuilder routeLog = new StringBuilder();
    private String lastUrl = "";
    private String latestDom = "DOM: waiting";
    private long probeSequence = 0;

    private final Runnable probeRunnable = new Runnable() {
        @Override public void run() {
            probeOnce();
            handler.postDelayed(this, 1000L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

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

        LinearLayout actions = new LinearLayout(this);
        actions.setOrientation(LinearLayout.HORIZONTAL);

        Button home = new Button(this);
        home.setText("CHATGPT");
        home.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                webView.loadUrl("https://chatgpt.com/");
            }
        });
        actions.addView(home, new LinearLayout.LayoutParams(0, dp(48), 1f));

        Button download = new Button(this);
        download.setText("DOWNLOAD");
        download.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                downloadReport();
            }
        });
        actions.addView(download, new LinearLayout.LayoutParams(0, dp(48), 1f));

        Button reload = new Button(this);
        reload.setText("RELOAD");
        reload.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                webView.reload();
            }
        });
        actions.addView(reload, new LinearLayout.LayoutParams(0, dp(48), 1f));
        root.addView(actions, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(48)));

        statusView = new TextView(this);
        statusView.setTextSize(11f);
        statusView.setTextIsSelectable(true);
        statusView.setPadding(dp(8), dp(6), dp(8), dp(6));
        statusView.setText("WebView Probe Stable v0.3\nRead-only observability; DOWNLOAD writes a sanitized text report.");

        ScrollView statusScroll = new ScrollView(this);
        statusScroll.addView(statusView, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT,
                ScrollView.LayoutParams.WRAP_CONTENT));
        root.addView(statusScroll, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(160)));

        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setLoadWithOverviewMode(false);
        settings.setUseWideViewPort(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(true);
        cookieManager.setAcceptThirdPartyCookies(webView, true);

        webView.setWebChromeClient(new WebChromeClient());
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
    }

    private void probeOnce() {
        if (webView == null) return;
        final String nativeUrl = safe(webView.getUrl());
        if (!nativeUrl.equals(lastUrl)) {
            lastUrl = nativeUrl;
            recordRoute("URL_CHANGE", nativeUrl);
        }

        final long seq = ++probeSequence;
        String js = "(function(){try{"
                + "const qa=(s)=>Array.from(document.querySelectorAll(s));"
                + "const vis=(e)=>{const r=e.getBoundingClientRect();const st=getComputedStyle(e);return r.width>0&&r.height>0&&st.visibility!=='hidden'&&st.display!=='none';};"
                + "const labels=qa('button,[role=\\\"button\\\"],[aria-label]').filter(vis).map(e=>(e.getAttribute('aria-label')||e.innerText||e.textContent||'').trim().replace(/\\s+/g,' ')).filter(Boolean).slice(0,24);"
                + "const o={href:location.href,title:document.title,ready:document.readyState,"
                + "editables:qa('textarea,[contenteditable=\\\"true\\\"]').filter(vis).length,"
                + "buttons:qa('button').filter(vis).length,roleButtons:qa('[role=\\\"button\\\"]').filter(vis).length,"
                + "links:qa('a').filter(vis).length,articles:qa('article').length,mains:qa('main').length,"
                + "userRoleNodes:qa('[data-message-author-role=\\\"user\\\"]').length,assistantRoleNodes:qa('[data-message-author-role=\\\"assistant\\\"]').length,"
                + "conversationTurns:qa('[data-testid*=\\\"conversation-turn\\\"]').length,composerHints:qa('[data-testid*=\\\"composer\\\"],[aria-label*=\\\"Message\\\" i],[placeholder*=\\\"Message\\\" i]').length,"
                + "labels:labels};return JSON.stringify(o);}catch(e){return JSON.stringify({error:String(e),href:String(location.href)});}})();";

        webView.evaluateJavascript(js, new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                if (seq < probeSequence - 2) return;
                latestDom = parseDomResult(value);
                renderStatus(nativeUrl);
            }
        });
    }

    private String parseDomResult(String value) {
        try {
            Object outer = new JSONTokener(value).nextValue();
            String json = outer instanceof String ? (String) outer : String.valueOf(outer);
            JSONObject o = new JSONObject(json);
            StringBuilder s = new StringBuilder();
            s.append("TITLE: ").append(o.optString("title", "-")).append('\n');
            s.append("READY: ").append(o.optString("ready", "-")).append('\n');
            s.append("DOM: editables=").append(o.optInt("editables", -1));
            s.append(" buttons=").append(o.optInt("buttons", -1));
            s.append(" roleButtons=").append(o.optInt("roleButtons", -1));
            s.append(" links=").append(o.optInt("links", -1));
            s.append(" articles=").append(o.optInt("articles", -1));
            s.append(" main=").append(o.optInt("mains", -1)).append('\n');
            s.append("CHAT_HINTS: user=").append(o.optInt("userRoleNodes", -1));
            s.append(" assistant=").append(o.optInt("assistantRoleNodes", -1));
            s.append(" turns=").append(o.optInt("conversationTurns", -1));
            s.append(" composer=").append(o.optInt("composerHints", -1)).append('\n');
            if (o.has("labels")) s.append("VISIBLE_LABELS: ").append(o.optJSONArray("labels")).append('\n');
            if (o.has("error")) s.append("JS_ERROR: ").append(o.optString("error"));
            return s.toString().trim();
        } catch (Exception e) {
            return "DOM_PARSE_ERROR: " + e.getClass().getSimpleName();
        }
    }

    private void renderStatus(String rawUrl) {
        String sanitized = sanitizeUrl(rawUrl);
        String canonical = extractCanonicalConversationId(sanitized);
        String routeSegment = extractRouteSegment(sanitized);
        String bindingState = !"-".equals(canonical) ? "CANONICAL_UUID"
                : (routeSegment.startsWith("WEB:") ? "TRANSIENT_WEB_ID" : "NONE");

        StringBuilder s = new StringBuilder();
        s.append("WebView Probe Stable v0.3 — READ ONLY\n");
        s.append("URL: ").append(sanitized).append('\n');
        s.append("BINDING_STATE: ").append(bindingState).append('\n');
        s.append("CONVERSATION_ID: ").append(canonical).append('\n');
        s.append(latestDom).append('\n');
        s.append("ROUTE_EVENTS: ").append(countRouteEvents()).append(" (DOWNLOAD for full sanitized log)");
        statusView.setText(s.toString());
    }

    private void recordRoute(String kind, String rawUrl) {
        String u = sanitizeUrl(rawUrl);
        String canonical = extractCanonicalConversationId(u);
        String segment = extractRouteSegment(u);
        String cid = !"-".equals(canonical) ? canonical : (segment.startsWith("WEB:") ? "TRANSIENT" : "-");
        routeLog.append(kind).append(" | ").append(u).append(" | cid=").append(cid).append('\n');
        if (routeLog.length() > 12000) routeLog.delete(0, 4000);
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
        if (end <= start) return "-";
        return url.substring(start, end);
    }

    private String extractCanonicalConversationId(String url) {
        String segment = extractRouteSegment(url);
        return UUID_PATTERN.matcher(segment).matches() ? segment : "-";
    }

    private int countRouteEvents() {
        int count = 0;
        for (int i = 0; i < routeLog.length(); i++) {
            if (routeLog.charAt(i) == '\n') count++;
        }
        return count;
    }

    private String buildReport() {
        String current = sanitizeUrl(webView == null ? null : webView.getUrl());
        String canonical = extractCanonicalConversationId(current);
        return "CHATGPT_WEBVIEW_OBSERVABILITY_STABLE_V03\n"
                + "CURRENT_URL=" + current + "\n"
                + "CURRENT_CONVERSATION_ID=" + canonical + "\n"
                + latestDom + "\n"
                + "--- ROUTE LOG (SANITIZED; NO QUERY/FRAGMENT) ---\n"
                + routeLog;
    }

    private void downloadReport() {
        String timestamp = new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date());
        String fileName = "chatgpt-webview-report-" + timestamp + ".txt";
        ContentValues values = new ContentValues();
        values.put(MediaStore.MediaColumns.DISPLAY_NAME, fileName);
        values.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
        values.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
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
            Toast.makeText(this, "Downloaded: Downloads/ChatGPTWebViewProbe/" + fileName, Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            if (item != null) getContentResolver().delete(item, null, null);
            Toast.makeText(this, "Download failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
        }
    }

    private String safe(String s) {
        return s == null ? "-" : s;
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
        if (webView != null) webView.destroy();
        super.onDestroy();
    }
}
