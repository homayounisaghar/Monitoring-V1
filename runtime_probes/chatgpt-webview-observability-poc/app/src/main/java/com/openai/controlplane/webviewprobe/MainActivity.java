package com.openai.controlplane.webviewprobe;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
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
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;
import org.json.JSONTokener;

public class MainActivity extends Activity {
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

        CookieManager cookieManager = CookieManager.getInstance();
        cookieManager.setAcceptCookie(true);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);

        LinearLayout actions = new LinearLayout(this);
        actions.setOrientation(LinearLayout.HORIZONTAL);

        Button home = new Button(this);
        home.setText("CHATGPT");
        home.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { webView.loadUrl("https://chatgpt.com/"); }
        });
        actions.addView(home, new LinearLayout.LayoutParams(0, dp(48), 1f));

        Button copy = new Button(this);
        copy.setText("COPY REPORT");
        copy.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { copyReport(); }
        });
        actions.addView(copy, new LinearLayout.LayoutParams(0, dp(48), 1f));

        Button reload = new Button(this);
        reload.setText("RELOAD");
        reload.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { webView.reload(); }
        });
        actions.addView(reload, new LinearLayout.LayoutParams(0, dp(48), 1f));
        root.addView(actions, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(48)));

        statusView = new TextView(this);
        statusView.setTextSize(11f);
        statusView.setTextIsSelectable(true);
        statusView.setPadding(dp(8), dp(6), dp(8), dp(6));
        statusView.setText("WebView Probe v0.2\nRead-only observability; no automated page mutation.");

        ScrollView statusScroll = new ScrollView(this);
        statusScroll.addView(statusView, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT,
                ScrollView.LayoutParams.WRAP_CONTENT));
        root.addView(statusScroll, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(150)));

        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setLoadWithOverviewMode(false);
        settings.setUseWideViewPort(false);
        cookieManager.setAcceptThirdPartyCookies(webView, true);

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override public void onPageStarted(WebView view, String url, Bitmap favicon) {
                recordRoute("PAGE_START", url);
                super.onPageStarted(view, url, favicon);
            }

            @Override public void onPageFinished(WebView view, String url) {
                recordRoute("PAGE_FINISH", url);
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
            return "DOM_PARSE_ERROR: " + e.getClass().getSimpleName() + " raw=" + safe(value);
        }
    }

    private void renderStatus(String url) {
        StringBuilder s = new StringBuilder();
        s.append("WebView Probe v0.2 — READ ONLY\n");
        s.append("URL: ").append(safe(url)).append('\n');
        s.append("CONVERSATION_ID: ").append(extractConversationId(url)).append('\n');
        s.append(latestDom).append('\n');
        s.append("ROUTE_EVENTS: ").append(countRouteEvents()).append(" (COPY REPORT for full log)");
        statusView.setText(s.toString());
    }

    private void recordRoute(String kind, String url) {
        String u = safe(url);
        String line = kind + " | " + u + " | cid=" + extractConversationId(u) + "\n";
        routeLog.append(line);
        if (routeLog.length() > 12000) routeLog.delete(0, 4000);
    }

    private int countRouteEvents() {
        int count = 0;
        for (int i = 0; i < routeLog.length(); i++) if (routeLog.charAt(i) == '\n') count++;
        return count;
    }

    private String extractConversationId(String url) {
        if (url == null) return "-";
        int marker = url.indexOf("/c/");
        if (marker < 0) return "-";
        int start = marker + 3;
        int end = url.length();
        for (char c : new char[]{'?', '#', '/'}) {
            int p = url.indexOf(c, start);
            if (p >= 0 && p < end) end = p;
        }
        if (end <= start) return "-";
        return url.substring(start, end);
    }

    private void copyReport() {
        String report = "CHATGPT_WEBVIEW_OBSERVABILITY_V02\n"
                + "CURRENT_URL=" + safe(webView == null ? null : webView.getUrl()) + "\n"
                + "CURRENT_CONVERSATION_ID=" + extractConversationId(webView == null ? null : webView.getUrl()) + "\n"
                + latestDom + "\n"
                + "--- ROUTE LOG ---\n" + routeLog;
        ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        clipboard.setPrimaryClip(ClipData.newPlainText("ChatGPT WebView Probe Report", report));
        Toast.makeText(this, "Probe report copied", Toast.LENGTH_SHORT).show();
    }

    private String safe(String s) { return s == null ? "-" : s; }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    @Override public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    @Override protected void onDestroy() {
        handler.removeCallbacks(probeRunnable);
        if (webView != null) webView.destroy();
        super.onDestroy();
    }
}
