package com.homayounisaghar.wakehandshakeprobe;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.webkit.CookieManager;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class SetupActivity extends Activity {
    private static final String START_URL = "https://www.perplexity.ai/";

    private TextView status;
    private WebView webView;

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (Build.VERSION.SDK_INT >= 30) getWindow().setDecorFitsSystemWindows(true);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(14), dp(14), dp(14), dp(14));
        root.setBackgroundColor(Color.WHITE);

        TextView title = new TextView(this);
        title.setText("Perplexity session");
        title.setTextSize(21f);
        title.setGravity(Gravity.CENTER);
        title.setPadding(0, dp(4), 0, dp(8));
        root.addView(title, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        status = new TextView(this);
        status.setText("Loading Perplexity…");
        status.setGravity(Gravity.CENTER);
        status.setTextSize(12f);
        status.setPadding(0, 0, 0, dp(8));
        root.addView(status);

        TextView hint = new TextView(this);
        hint.setText("If Perplexity asks you to sign in or complete a normal verification, do it here. This session uses the standard Android WebView browser profile.");
        hint.setTextSize(12f);
        hint.setPadding(dp(3), 0, dp(3), dp(8));
        root.addView(hint);

        Button reset = new Button(this);
        reset.setText("Reset Perplexity session");
        reset.setAllCaps(false);
        reset.setOnClickListener(v -> resetPerplexitySession());
        root.addView(reset, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        webView = new WebView(this);
        root.addView(webView, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));
        setContentView(root);

        configureWebView();
        boolean resettingLegacyProfile = PerplexitySessionCompat.needsDefaultUaReset(this);
        if (resettingLegacyProfile) {
            status.setText("Resetting the old Perplexity WebView profile…");
        }
        PerplexitySessionCompat.resetLegacyProfileOnce(this, () -> {
            if (webView == null) return;
            webView.clearCache(true);
            webView.loadUrl(START_URL);
            if (resettingLegacyProfile) {
                status.setText("Session reset. Sign in and complete normal verification once.");
            }
        });
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void configureWebView() {
        PerplexitySessionCompat.configure(webView);
        WebSettings s = webView.getSettings();
        s.setSupportZoom(true);
        s.setBuiltInZoomControls(true);
        s.setDisplayZoomControls(false);

        webView.setWebViewClient(new WebViewClient() {
            @Override public void onPageFinished(WebView view, String url) {
                String host = null;
                try { host = Uri.parse(url).getHost(); } catch (Exception ignored) {}
                boolean ok = host != null &&
                        (host.equals("perplexity.ai") || host.endsWith(".perplexity.ai"));
                if (ok) {
                    try { CookieManager.getInstance().flush(); } catch (Exception ignored) {}
                    status.setText("Perplexity session is loaded. You can go back to the probe.");
                } else {
                    status.setText("Waiting for Perplexity…");
                }
            }
        });
    }

    private void resetPerplexitySession() {
        status.setText("Clearing Perplexity session…");
        PerplexitySessionCompat.clearSession(this, () -> {
            if (webView == null) return;
            webView.stopLoading();
            webView.clearHistory();
            webView.clearCache(true);
            webView.loadUrl(START_URL);
            status.setText("Session cleared. Sign in and complete normal verification once.");
        });
    }

    @Override protected void onDestroy() {
        try { CookieManager.getInstance().flush(); } catch (Exception ignored) {}
        if (webView != null) webView.destroy();
        super.onDestroy();
    }

    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }
}
