package com.homayounisaghar.chatgptwebviewprobe;

import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.os.Message;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.TextView;
import android.widget.Toast;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Locale;

/**
 * Stable v0.32.2 — controlled Google OAuth experiment.
 *
 * Keeps the corrected v0.32.1 auth-readiness gate and all no-credential/no-token
 * invariants, but permits a narrowly scoped Google OAuth web flow to remain inside
 * the app-owned WebView. No browser-session transfer, cookie extraction, token copy,
 * user-agent spoofing or provider credential inspection is performed.
 *
 * Only ChatGPT/OpenAI auth hosts plus the explicit Google OAuth host allowlist may
 * become top-level WebView navigations while Auth Mode is active. Other providers
 * remain fail-closed. Google intent:// links are converted to an allowlisted HTTPS
 * fallback when one is supplied; native Google/session handoff is not attempted.
 */
public class OrchestratorAuthModeV34Activity extends OrchestratorAuthModeV33Activity {
    private WebView web34;

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web34 = findWeb34(getWindow().getDecorView());
        installControlledGoogleClients34();
        retitle34();
        emit34("AUTH_GOOGLE_MODE_READY", "ACTIVE", "GOOGLE_WEB_CONTAINED");
    }

    private void installControlledGoogleClients34() {
        if (web34 == null) return;
        WebSettings s = web34.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setJavaScriptCanOpenWindowsAutomatically(true);
        s.setSupportMultipleWindows(true);
        CookieManager cm = CookieManager.getInstance();
        cm.setAcceptCookie(true);
        cm.setAcceptThirdPartyCookies(web34, true);

        web34.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri u = request == null ? null : request.getUrl();
                return routeMain34(view, u == null ? null : u.toString());
            }

            @SuppressWarnings("deprecation")
            @Override public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return routeMain34(view, url);
            }

            @Override public void onPageStarted(WebView view, String url, Bitmap favicon) {
                emitNavigation34(url, false);
                super.onPageStarted(view, url, favicon);
            }

            @Override public void onPageFinished(WebView view, String url) {
                CookieManager.getInstance().flush();
                emitNavigation34(url, false);
                super.onPageFinished(view, url);
            }
        });

        web34.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onCreateWindow(WebView view, boolean isDialog,
                                                    boolean isUserGesture, Message resultMsg) {
                if (resultMsg == null || !(resultMsg.obj instanceof WebView.WebViewTransport)) return false;
                final WebView popup = new WebView(OrchestratorAuthModeV34Activity.this);
                WebSettings ps = popup.getSettings();
                ps.setJavaScriptEnabled(true);
                ps.setDomStorageEnabled(true);
                ps.setDatabaseEnabled(true);
                ps.setJavaScriptCanOpenWindowsAutomatically(true);
                ps.setSupportMultipleWindows(false);
                CookieManager.getInstance().setAcceptThirdPartyCookies(popup, true);
                popup.setWebViewClient(new WebViewClient() {
                    @Override public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                        Uri u = r == null ? null : r.getUrl();
                        return routePopup34(popup, u == null ? null : u.toString());
                    }
                    @SuppressWarnings("deprecation")
                    @Override public boolean shouldOverrideUrlLoading(WebView v, String url) {
                        return routePopup34(popup, url);
                    }
                    @Override public void onPageStarted(WebView v, String url, Bitmap favicon) {
                        if (url != null && !"about:blank".equalsIgnoreCase(url)) routePopup34(popup, url);
                    }
                });
                WebView.WebViewTransport transport = (WebView.WebViewTransport) resultMsg.obj;
                transport.setWebView(popup);
                resultMsg.sendToTarget();
                emit34("AUTH_GOOGLE_POPUP_CAPTURED", "CONTAINED", "POPUP_TO_MAIN_WEBVIEW");
                return true;
            }

            @Override public void onCloseWindow(WebView window) {
                safeDestroy34(window);
            }
        });
    }

    private boolean routeMain34(WebView view, String raw) {
        if (raw == null || raw.trim().isEmpty()) return false;
        Uri u;
        try { u = Uri.parse(raw); } catch (Exception e) { return true; }
        String scheme = safe34(u.getScheme()).toLowerCase(Locale.ROOT);

        if ("http".equals(scheme) || "https".equals(scheme)) {
            String host = safe34(u.getHost()).toLowerCase(Locale.ROOT);
            if (isOpenAiAuthHost34(host)) {
                emitNavigation34(raw, false);
                return false;
            }
            if (authActive34() && isGoogleOAuthHost34(host)) {
                setAuthMessage34("Google sign-in is contained in this app. Complete it here; no browser-session transfer is used.");
                emit34("AUTH_GOOGLE_WEB_ALLOWED", "CONTAINED", googleClass34(host));
                return false;
            }
            if (authActive34()) {
                setAuthMessage34("Only OpenAI/ChatGPT and the controlled Google OAuth flow are allowed during Auth Mode.");
                emit34("AUTH_EXTERNAL_WEB_BLOCKED", "FAIL_CLOSED", providerClass34(host));
                Toast.makeText(this, "Only the controlled Google sign-in flow is allowed here", Toast.LENGTH_LONG).show();
                return true;
            }
            return invokeBaseMain34(view, raw);
        }

        if (authActive34() && "intent".equals(scheme)) {
            if (handleGoogleIntentFallback34(raw)) return true;
        }
        return invokeBaseMain34(view, raw);
    }

    private boolean routePopup34(WebView popup, String raw) {
        if (raw == null || raw.trim().isEmpty() || "about:blank".equalsIgnoreCase(raw)) return false;
        Uri u;
        try { u = Uri.parse(raw); } catch (Exception e) { safeDestroy34(popup); return true; }
        String scheme = safe34(u.getScheme()).toLowerCase(Locale.ROOT);
        String host = safe34(u.getHost()).toLowerCase(Locale.ROOT);

        if (("http".equals(scheme) || "https".equals(scheme))
                && (isOpenAiAuthHost34(host) || (authActive34() && isGoogleOAuthHost34(host)))) {
            if (web34 != null) web34.loadUrl(raw);
            emit34(isGoogleOAuthHost34(host) ? "AUTH_GOOGLE_POPUP_ROUTED" : "AUTH_OPENAI_POPUP_ROUTED",
                    "CONTAINED", isGoogleOAuthHost34(host) ? googleClass34(host) : "OPENAI_AUTH");
            safeDestroy34(popup);
            return true;
        }
        if (authActive34() && "intent".equals(scheme) && handleGoogleIntentFallback34(raw)) {
            safeDestroy34(popup);
            return true;
        }
        if (!("http".equals(scheme) || "https".equals(scheme))) {
            boolean handled = invokeBaseMain34(web34, raw);
            safeDestroy34(popup);
            return handled;
        }
        emit34("AUTH_POPUP_EXTERNAL_BLOCKED", "FAIL_CLOSED", providerClass34(host));
        safeDestroy34(popup);
        return true;
    }

    private boolean handleGoogleIntentFallback34(String raw) {
        try {
            Intent i = Intent.parseUri(raw, Intent.URI_INTENT_SCHEME);
            String fallback = i.getStringExtra("browser_fallback_url");
            if (fallback == null || fallback.trim().isEmpty()) return false;
            Uri f = Uri.parse(fallback);
            String scheme = safe34(f.getScheme()).toLowerCase(Locale.ROOT);
            String host = safe34(f.getHost()).toLowerCase(Locale.ROOT);
            if (("http".equals(scheme) || "https".equals(scheme))
                    && (isGoogleOAuthHost34(host) || isOpenAiAuthHost34(host))) {
                if (web34 != null) web34.loadUrl(fallback);
                emit34("AUTH_GOOGLE_INTENT_FALLBACK", "CONTAINED_HTTPS", isGoogleOAuthHost34(host) ? googleClass34(host) : "OPENAI_AUTH");
                return true;
            }
        } catch (Exception ignored) { }
        return false;
    }

    private boolean isOpenAiAuthHost34(String host) {
        String h = safe34(host).toLowerCase(Locale.ROOT);
        return h.equals("chatgpt.com") || h.endsWith(".chatgpt.com")
                || h.equals("openai.com") || h.endsWith(".openai.com");
    }

    private boolean isGoogleOAuthHost34(String host) {
        String h = safe34(host).toLowerCase(Locale.ROOT);
        return h.equals("accounts.google.com")
                || h.equals("accounts.googleusercontent.com")
                || h.equals("oauth2.googleapis.com");
    }

    private String googleClass34(String host) {
        String h = safe34(host).toLowerCase(Locale.ROOT);
        if (h.equals("accounts.google.com")) return "GOOGLE_ACCOUNTS";
        if (h.equals("accounts.googleusercontent.com")) return "GOOGLE_ACCOUNTS_CONTENT";
        if (h.equals("oauth2.googleapis.com")) return "GOOGLE_OAUTH2";
        return "GOOGLE_OTHER";
    }

    private String providerClass34(String host) {
        String h = safe34(host).toLowerCase(Locale.ROOT);
        if (h.contains("google")) return "GOOGLE_OTHER";
        if (h.contains("microsoft") || h.contains("live.com")) return "MICROSOFT";
        if (h.contains("apple")) return "APPLE";
        if (h.isEmpty()) return "NO_HOST";
        return "EXTERNAL_OTHER";
    }

    private boolean authActive34() {
        try {
            Field f = OrchestratorAuthModeV32Activity.class.getDeclaredField("authMode32");
            f.setAccessible(true);
            return f.getBoolean(this);
        } catch (Exception e) {
            return true;
        }
    }

    private boolean invokeBaseMain34(WebView view, String raw) {
        try {
            Method m = OrchestratorAuthModeV32Activity.class.getDeclaredMethod("handleMainNavigation32", WebView.class, String.class);
            m.setAccessible(true);
            Object r = m.invoke(this, view, raw);
            return r instanceof Boolean && (Boolean) r;
        } catch (Exception e) {
            emit34("AUTH_NAV_RESOLVER_FAILED", "FAIL_CLOSED", "REFLECTION_ERROR");
            return true;
        }
    }

    private void emitNavigation34(String raw, boolean popup) {
        try {
            Uri u = Uri.parse(raw == null ? "" : raw);
            String host = safe34(u.getHost()).toLowerCase(Locale.ROOT);
            String c = isGoogleOAuthHost34(host) ? googleClass34(host)
                    : isOpenAiAuthHost34(host) ? "OPENAI_CHATGPT_AUTH" : providerClass34(host);
            emit34("AUTH_NAV", popup ? "POPUP_CONTAINED" : "MAIN_WEBVIEW", c);
        } catch (Exception ignored) { }
    }

    private void emit34(String phase, String classification, String navClass) {
        try {
            Method m = OrchestratorAuthModeV32Activity.class.getDeclaredMethod("phase32", String.class, String.class, String.class);
            m.setAccessible(true);
            m.invoke(this, phase, classification, navClass);
        } catch (Exception ignored) { }
    }

    private void setAuthMessage34(String message) {
        try {
            Field f = OrchestratorAuthModeV32Activity.class.getDeclaredField("authStatus32");
            f.setAccessible(true);
            Object o = f.get(this);
            if (o instanceof TextView) ((TextView) o).setText("AUTH MODE: " + message);
        } catch (Exception ignored) { }
    }

    private void retitle34() {
        retitleWalk34(getWindow().getDecorView());
    }

    private void retitleWalk34(View v) {
        if (v instanceof TextView && !(v instanceof android.widget.Button)) {
            TextView t = (TextView) v;
            String s = String.valueOf(t.getText());
            if (s.startsWith("v0.32.1 Auth/MFA readiness fix")) {
                t.setText("v0.32.2 Controlled Google OAuth");
            }
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) retitleWalk34(g.getChildAt(i));
        }
    }

    private WebView findWeb34(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb34(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }

    private void safeDestroy34(WebView w) {
        try { if (w != null && w != web34) w.destroy(); } catch (Exception ignored) { }
    }

    private String safe34(String s) { return s == null ? "" : s; }
}
