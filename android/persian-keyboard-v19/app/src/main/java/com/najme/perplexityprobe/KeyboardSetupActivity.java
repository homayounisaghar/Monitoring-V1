package com.najme.perplexityprobe;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.view.inputmethod.InputMethodInfo;
import android.view.inputmethod.InputMethodManager;
import android.webkit.CookieManager;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class KeyboardSetupActivity extends Activity {
    private static final String START_URL = "https://www.perplexity.ai/";
    private static final int REQ_MIC = 71;
    private static final String MOBILE_BROWSER_UA =
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 " +
            "(KHTML, like Gecko) SamsungBrowser/30.0 Chrome/143.0.0.0 Mobile Safari/537.36";

    private TextView status;
    private WebView webView;

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildUi();
        configureWebView();
        requestMicIfNeeded();
        webView.loadUrl(START_URL);
    }

    private int dp(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(10), dp(10), dp(10), dp(8));

        TextView title = new TextView(this);
        title.setText("Persian keyboard");
        title.setTextSize(22f);
        title.setGravity(Gravity.CENTER);
        title.setPadding(0, dp(6), 0, dp(8));
        root.addView(title);

        Button choose = new Button(this);
        choose.setText("انتخاب Persian keyboard به‌عنوان کیبورد");
        choose.setAllCaps(false);
        choose.setTextSize(15f);
        choose.setOnClickListener(v -> openKeyboardChooser());
        root.addView(choose, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(56)));

        status = new TextView(this);
        status.setText("Perplexity session در حال بارگذاری است…");
        status.setTextSize(12f);
        status.setGravity(Gravity.CENTER);
        status.setPadding(dp(6), dp(5), dp(6), dp(7));
        root.addView(status);

        TextView hint = new TextView(this);
        hint.setText("این WebView فقط برای نگه‌داشتن نشست معمولی Perplexity است. اگر لازم بود همین‌جا وارد حساب شوید.");
        hint.setTextSize(12f);
        hint.setPadding(dp(4), 0, dp(4), dp(6));
        root.addView(hint);

        webView = new WebView(this);
        root.addView(webView, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));
        setContentView(root);
    }

    private void requestMicIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M &&
                checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQ_MIC);
        }
    }

    private void openKeyboardChooser() {
        InputMethodManager imm = (InputMethodManager) getSystemService(INPUT_METHOD_SERVICE);
        boolean enabled = false;
        if (imm != null) {
            try {
                for (InputMethodInfo info : imm.getEnabledInputMethodList()) {
                    if (getPackageName().equals(info.getPackageName())) {
                        enabled = true;
                        break;
                    }
                }
            } catch (Exception ignored) {}
        }

        if (enabled && imm != null) {
            try {
                imm.showInputMethodPicker();
                status.setText("Persian keyboard را از فهرست انتخاب کنید.");
                return;
            } catch (Exception ignored) {}
        }

        try {
            startActivity(new Intent(Settings.ACTION_INPUT_METHOD_SETTINGS));
            status.setText("ابتدا Persian keyboard را فعال کنید؛ سپس به این صفحه برگردید و دکمه را دوباره بزنید.");
        } catch (Exception e) {
            status.setText("باز کردن تنظیمات کیبورد ممکن نشد.");
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void configureWebView() {
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setSupportZoom(true);
        s.setBuiltInZoomControls(true);
        s.setDisplayZoomControls(false);
        s.setUserAgentString(MOBILE_BROWSER_UA);
        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, true);
        webView.setWebViewClient(new WebViewClient() {
            @Override public void onPageFinished(WebView view, String url) {
                String host = null;
                try { host = Uri.parse(url).getHost(); } catch (Exception ignored) {}
                boolean ok = host != null && (host.equals("perplexity.ai") || host.endsWith(".perplexity.ai"));
                if (ok) {
                    try { CookieManager.getInstance().flush(); } catch (Exception ignored) {}
                    status.setText("Perplexity session آماده است. در صورت نیاز وارد حساب شوید.");
                } else {
                    status.setText("در انتظار صفحه Perplexity…");
                }
            }
        });
    }
}
