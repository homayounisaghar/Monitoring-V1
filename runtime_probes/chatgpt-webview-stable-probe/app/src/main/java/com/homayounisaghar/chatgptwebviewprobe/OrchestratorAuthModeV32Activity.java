package com.homayounisaghar.chatgptwebviewprobe;

import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewParent;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;

import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Locale;
import java.util.UUID;

/**
 * Stable v0.32 — contained Auth/MFA mode for the app-owned ChatGPT WebView.
 *
 * Authentication is a separate trust mode from production capability execution.
 * While Auth Mode is active, normal capability execution stays disabled. OpenAI
 * authentication navigation is kept in the app-owned WebView, including target=_blank
 * / window.open flows. Authenticator deep-links may temporarily open the authenticator
 * app while preserving the WebView login page for the user's return and code entry.
 *
 * The app never reads, copies, serializes or uploads passwords, OTPs, cookies,
 * session/bearer tokens, form values, raw URLs, query strings or page HTML.
 * Social-provider OAuth is not forced into an embedded WebView; unsupported external
 * provider navigation fails closed instead of pretending a browser session can be
 * transferred into this WebView.
 */
public class OrchestratorAuthModeV32Activity extends OrchestratorCapabilityPickerV31Activity {
    private static final String SCHEMA32 = "cp-v32-auth-mode-v1";
    private static final String SCENARIO32 = "contained-openai-auth-mfa-webview";
    private static final String LOGIN_URL32 = "https://chatgpt.com/auth/login";
    private static final int NET_TIMEOUT_MS32 = 2800;

    private final Handler h32 = new Handler(Looper.getMainLooper());
    private WebView web32;
    private Button modelButton32;
    private Button loginButton32;
    private TextView authStatus32;
    private LinearLayout authPanel32;

    private boolean authMode32 = true;
    private boolean authReady32 = false;
    private String authAttempt32 = "cp32-auth-" + UUID.randomUUID();
    private int seq32 = 0;
    private int navEvents32 = 0;
    private int popupCaptures32 = 0;
    private int externalBlocks32 = 0;
    private int authenticatorLaunches32 = 0;
    private String lastNavClass32 = "-";
    private String lastAuthStatus32 = "STARTING";

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web32 = findWeb32(getWindow().getDecorView());
        modelButton32 = findButton32(getWindow().getDecorView(), "RUN MODEL / TOOLS TEST");
        installAuthPanel32();
        configureContainedAuth32();
        setAuthMode32(true, "Checking ChatGPT session...");
        phase32("AUTH_MODE_READY", "ACTIVE", "STARTUP");
        h32.postDelayed(authPoll32, 150L);
    }

    @Override protected void onResume() {
        super.onResume();
        h32.postDelayed(authPoll32, 120L);
    }

    @Override protected void onDestroy() {
        h32.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private void installAuthPanel32() {
        if (web32 == null) return;
        ViewParent p = web32.getParent();
        if (!(p instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) p;

        authPanel32 = new LinearLayout(this);
        authPanel32.setOrientation(LinearLayout.VERTICAL);
        authPanel32.setPadding(dp32(8), dp32(4), dp32(8), dp32(2));

        authStatus32 = new TextView(this);
        authStatus32.setTextSize(10.5f);
        authStatus32.setSingleLine(false);
        authStatus32.setMaxLines(2);
        authPanel32.addView(authStatus32, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));

        loginButton32 = new Button(this);
        loginButton32.setText("LOGIN / RETRY IN THIS APP");
        loginButton32.setTextSize(12f);
        loginButton32.setAllCaps(false);
        loginButton32.setOnClickListener(v -> startContainedLogin32());
        authPanel32.addView(loginButton32, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp32(44)));

        int wi = root.indexOfChild(web32);
        if (wi < 0) wi = 0;
        root.addView(authPanel32, wi + 1, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void configureContainedAuth32() {
        if (web32 == null) return;
        WebSettings s = web32.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setJavaScriptCanOpenWindowsAutomatically(true);
        s.setSupportMultipleWindows(true);
        CookieManager cm = CookieManager.getInstance();
        cm.setAcceptCookie(true);
        cm.setAcceptThirdPartyCookies(web32, true);

        web32.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri u = request == null ? null : request.getUrl();
                return handleMainNavigation32(view, u == null ? null : u.toString());
            }

            @SuppressWarnings("deprecation")
            @Override public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return handleMainNavigation32(view, url);
            }

            @Override public void onPageStarted(WebView view, String url, Bitmap favicon) {
                observeNavigation32(url, false);
                super.onPageStarted(view, url, favicon);
            }

            @Override public void onPageFinished(WebView view, String url) {
                CookieManager.getInstance().flush();
                observeNavigation32(url, false);
                h32.postDelayed(authPoll32, 120L);
                super.onPageFinished(view, url);
            }
        });

        web32.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onCreateWindow(WebView view, boolean isDialog,
                                                    boolean isUserGesture, Message resultMsg) {
                if (resultMsg == null || !(resultMsg.obj instanceof WebView.WebViewTransport)) return false;
                final WebView popup = new WebView(OrchestratorAuthModeV32Activity.this);
                WebSettings ps = popup.getSettings();
                ps.setJavaScriptEnabled(true);
                ps.setDomStorageEnabled(true);
                ps.setJavaScriptCanOpenWindowsAutomatically(true);
                ps.setSupportMultipleWindows(false);
                CookieManager.getInstance().setAcceptThirdPartyCookies(popup, true);
                popup.setWebViewClient(new WebViewClient() {
                    @Override public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                        Uri u = r == null ? null : r.getUrl();
                        return routePopup32(popup, u == null ? null : u.toString());
                    }
                    @SuppressWarnings("deprecation")
                    @Override public boolean shouldOverrideUrlLoading(WebView v, String url) {
                        return routePopup32(popup, url);
                    }
                    @Override public void onPageStarted(WebView v, String url, Bitmap favicon) {
                        if (url != null && !"about:blank".equalsIgnoreCase(url)) routePopup32(popup, url);
                    }
                });
                WebView.WebViewTransport transport = (WebView.WebViewTransport) resultMsg.obj;
                transport.setWebView(popup);
                resultMsg.sendToTarget();
                popupCaptures32++;
                phase32("AUTH_POPUP_CAPTURED", "CONTAINED", "POPUP_TO_MAIN_WEBVIEW");
                return true;
            }

            @Override public void onCloseWindow(WebView window) {
                try { if (window != null && window != web32) window.destroy(); } catch (Exception ignored) { }
            }
        });
    }

    private void startContainedLogin32() {
        if (web32 == null) return;
        authAttempt32 = "cp32-auth-" + UUID.randomUUID();
        seq32 = 0;
        authReady32 = false;
        setAuthMode32(true, "Login stays in this app. Use email/password + MFA if available.");
        phase32("AUTH_LOGIN_START", "USER_REQUESTED", "DIRECT_CHATGPT_AUTH_LOGIN");
        web32.loadUrl(LOGIN_URL32);
    }

    private boolean handleMainNavigation32(WebView view, String raw) {
        if (raw == null || raw.trim().isEmpty()) return false;
        Uri u;
        try { u = Uri.parse(raw); } catch (Exception e) { return true; }
        String scheme = safe32(u.getScheme()).toLowerCase(Locale.ROOT);

        if ("http".equals(scheme) || "https".equals(scheme)) {
            if (isAuthWebHost32(u.getHost())) {
                observeNavigation32(raw, false);
                return false;
            }
            if (authMode32) {
                externalBlocks32++;
                String c = providerClass32(u.getHost());
                lastAuthStatus32 = "BLOCKED_EXTERNAL_PROVIDER_" + c;
                setAuthText32("External sign-in provider blocked here; this WebView session cannot inherit browser cookies.");
                phase32("AUTH_EXTERNAL_WEB_BLOCKED", "FAIL_CLOSED", c);
                Toast.makeText(this, "External social login cannot bind this WebView session", Toast.LENGTH_LONG).show();
                return true;
            }
            launchExternal32(u);
            return true;
        }

        if (authMode32) return handleAuthDeepLink32(raw, u);
        launchExternal32(u);
        return true;
    }

    private boolean routePopup32(WebView popup, String raw) {
        if (raw == null || raw.trim().isEmpty() || "about:blank".equalsIgnoreCase(raw)) return false;
        Uri u;
        try { u = Uri.parse(raw); } catch (Exception e) { safeDestroy32(popup); return true; }
        String scheme = safe32(u.getScheme()).toLowerCase(Locale.ROOT);
        if (("http".equals(scheme) || "https".equals(scheme)) && isAuthWebHost32(u.getHost())) {
            if (web32 != null) web32.loadUrl(raw);
            observeNavigation32(raw, true);
            safeDestroy32(popup);
            return true;
        }
        if (!("http".equals(scheme) || "https".equals(scheme)) && authMode32) {
            handleAuthDeepLink32(raw, u);
            safeDestroy32(popup);
            return true;
        }
        externalBlocks32++;
        phase32("AUTH_POPUP_EXTERNAL_BLOCKED", "FAIL_CLOSED", providerClass32(u.getHost()));
        safeDestroy32(popup);
        return true;
    }

    private boolean handleAuthDeepLink32(String raw, Uri u) {
        String scheme = safe32(u.getScheme()).toLowerCase(Locale.ROOT);
        if (scheme.startsWith("otpauth")) {
            boolean ok = launchAuthenticator32(new Intent(Intent.ACTION_VIEW, u));
            phase32("AUTH_AUTHENTICATOR_DEEPLINK", ok ? "LAUNCHED" : "NO_HANDLER", "OTPAUTH");
            return true;
        }

        if ("intent".equals(scheme)) {
            try {
                Intent i = Intent.parseUri(raw, Intent.URI_INTENT_SCHEME);
                String fallback = i.getStringExtra("browser_fallback_url");
                if (fallback != null) {
                    Uri f = Uri.parse(fallback);
                    if (isAuthWebHost32(f.getHost())) {
                        if (web32 != null) web32.loadUrl(fallback);
                        phase32("AUTH_INTENT_FALLBACK", "CONTAINED", hostClass32(f.getHost()));
                        return true;
                    }
                }
                String pkg = safe32(i.getPackage()).toLowerCase(Locale.ROOT);
                if (isKnownAuthenticatorPackage32(pkg)) {
                    boolean ok = launchAuthenticator32(i);
                    phase32("AUTH_AUTHENTICATOR_INTENT", ok ? "LAUNCHED" : "NO_HANDLER", "KNOWN_AUTHENTICATOR");
                    return true;
                }
                externalBlocks32++;
                setAuthText32("Unknown external auth intent blocked; login page preserved in app.");
                phase32("AUTH_UNKNOWN_INTENT_BLOCKED", "FAIL_CLOSED", pkg.isEmpty() ? "NO_PACKAGE" : "OTHER_PACKAGE");
                return true;
            } catch (Exception e) {
                externalBlocks32++;
                phase32("AUTH_INTENT_PARSE_BLOCKED", "FAIL_CLOSED", "PARSE_ERROR");
                return true;
            }
        }

        externalBlocks32++;
        phase32("AUTH_EXTERNAL_SCHEME_BLOCKED", "FAIL_CLOSED", token32(scheme));
        return true;
    }

    private boolean launchAuthenticator32(Intent i) {
        try {
            startActivity(i);
            authenticatorLaunches32++;
            setAuthText32("Authenticator opened. Return here; the login page is preserved.");
            return true;
        } catch (Exception e) {
            setAuthText32("No compatible Authenticator handler found; keep this page and enter the code manually.");
            return false;
        }
    }

    private void launchExternal32(Uri u) {
        try { startActivity(new Intent(Intent.ACTION_VIEW, u)); }
        catch (Exception ignored) { }
    }

    private final Runnable authPoll32 = new Runnable() {
        @Override public void run() {
            pollAuthReady32();
            h32.postDelayed(this, 700L);
        }
    };

    private void pollAuthReady32() {
        if (web32 == null) return;
        String js = "(function(){try{"
                + "const vis=e=>{if(!e)return false;const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';};"
                + "const c=document.querySelector('#prompt-textarea')||Array.from(document.querySelectorAll('textarea,[contenteditable=\\\"true\\\"]')).filter(vis).slice(-1)[0]||null;"
                + "const body=((document.body&&document.body.innerText)||'').toLowerCase();"
                + "const expired=body.includes('your session has expired')||body.includes('log in again to continue');"
                + "const host=location.hostname||'';"
                + "const ready=(host==='chatgpt.com'||host.endsWith('.chatgpt.com'))&&vis(c)&&!expired;"
                + "return JSON.stringify({ready:ready,expired:expired,host:host});"
                + "}catch(e){return JSON.stringify({ready:false,expired:false,host:''});}})();";
        web32.evaluateJavascript(js, value -> {
            try {
                String s = value == null ? "" : value;
                if (s.startsWith("\"") && s.endsWith("\"")) {
                    s = new org.json.JSONTokener(s).nextValue().toString();
                }
                JSONObject o = new JSONObject(s);
                boolean ready = o.optBoolean("ready", false);
                boolean expired = o.optBoolean("expired", false);
                if (ready && !authReady32) {
                    authReady32 = true;
                    setAuthMode32(false, "Authenticated ChatGPT ready.");
                    phase32("AUTH_READY_CONFIRMED", "PASS", hostClass32(o.optString("host", "")));
                    return;
                }
                if (!ready && (expired || !isProductionHost32(o.optString("host", "")))) {
                    if (!authMode32) setAuthMode32(true, "Authentication required.");
                }
            } catch (Exception ignored) { }
        });
    }

    private void setAuthMode32(boolean active, String message) {
        authMode32 = active;
        if (modelButton32 != null) modelButton32.setEnabled(!active);
        if (authPanel32 != null) authPanel32.setVisibility(active ? View.VISIBLE : View.GONE);
        if (loginButton32 != null) loginButton32.setEnabled(active);
        setAuthText32(message);
    }

    private void observeNavigation32(String raw, boolean popup) {
        Uri u;
        try { u = Uri.parse(raw == null ? "" : raw); } catch (Exception e) { return; }
        String c = hostClass32(u.getHost());
        if (c.equals(lastNavClass32) && !popup) return;
        lastNavClass32 = c;
        navEvents32++;
        phase32("AUTH_NAV", popup ? "POPUP_CONTAINED" : "MAIN_WEBVIEW", c);
    }

    private boolean isAuthWebHost32(String host) {
        String h = safe32(host).toLowerCase(Locale.ROOT);
        return isProductionHost32(h) || h.equals("openai.com") || h.endsWith(".openai.com");
    }

    private boolean isProductionHost32(String host) {
        String h = safe32(host).toLowerCase(Locale.ROOT);
        return h.equals("chatgpt.com") || h.endsWith(".chatgpt.com");
    }

    private String hostClass32(String host) {
        String h = safe32(host).toLowerCase(Locale.ROOT);
        if (h.equals("chatgpt.com") || h.endsWith(".chatgpt.com")) return "CHATGPT";
        if (h.equals("auth.openai.com")) return "OPENAI_AUTH";
        if (h.equals("openai.com") || h.endsWith(".openai.com")) return "OPENAI_OTHER";
        return providerClass32(h);
    }

    private String providerClass32(String host) {
        String h = safe32(host).toLowerCase(Locale.ROOT);
        if (h.contains("google")) return "GOOGLE";
        if (h.contains("microsoft") || h.contains("live.com")) return "MICROSOFT";
        if (h.contains("apple")) return "APPLE";
        if (h.isEmpty()) return "NO_HOST";
        return "EXTERNAL_OTHER";
    }

    private boolean isKnownAuthenticatorPackage32(String pkg) {
        if (pkg == null || pkg.isEmpty()) return false;
        return pkg.equals("com.google.android.apps.authenticator2")
                || pkg.equals("com.azure.authenticator")
                || pkg.equals("com.authy.authy")
                || pkg.equals("com.twofasapp")
                || pkg.equals("com.bitwarden.authenticator")
                || pkg.equals("com.bitwarden")
                || pkg.equals("com.onepassword.android")
                || pkg.equals("com.lastpass.authenticator")
                || pkg.equals("com.duosecurity.duomobile");
    }

    private void phase32(String phase, String classification, String navClass) {
        if (!TelemetryConfigV32.isConfigured()) return;
        JSONObject p = new JSONObject();
        try {
            p.put("schema_version", SCHEMA32);
            p.put("scenario_id", SCENARIO32);
            p.put("source_ref", TelemetryConfigV32.SOURCE_REF);
            p.put("test_id", authAttempt32);
            p.put("seq", seq32++);
            p.put("phase", phase);
            p.put("classification", classification);
            p.put("timestamp_epoch_ms", System.currentTimeMillis());
            JSONObject st = new JSONObject();
            st.put("auth_mode", authMode32);
            st.put("auth_ready", authReady32);
            st.put("nav_class", safe32(navClass));
            st.put("nav_events", navEvents32);
            st.put("popup_captures", popupCaptures32);
            st.put("external_blocks", externalBlocks32);
            st.put("authenticator_launches", authenticatorLaunches32);
            st.put("raw_url_uploaded", false);
            st.put("url_path_query_uploaded", false);
            st.put("password_otp_form_values_read", false);
            st.put("cookies_tokens_accessed", false);
            st.put("raw_html_uploaded", false);
            p.put("state", st);
        } catch (Exception ignored) { return; }
        new Thread(() -> upload32(p), "cp32-auth-telemetry").start();
    }

    private void upload32(JSONObject p) {
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(TelemetryConfigV32.WEBHOOK_URL).openConnection();
            c.setConnectTimeout(NET_TIMEOUT_MS32);
            c.setReadTimeout(NET_TIMEOUT_MS32);
            c.setRequestMethod("POST");
            c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/json");
            byte[] b = p.toString().getBytes(StandardCharsets.UTF_8);
            c.getOutputStream().write(b);
            c.getOutputStream().flush();
            c.getResponseCode();
        } catch (Exception ignored) {
        } finally {
            if (c != null) c.disconnect();
        }
    }

    private void setAuthText32(String s) {
        lastAuthStatus32 = safe32(s);
        if (authStatus32 != null) authStatus32.setText("AUTH MODE: " + lastAuthStatus32);
    }

    private WebView findWeb32(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb32(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }

    private Button findButton32(View v, String text) {
        if (v instanceof Button && text.equals(String.valueOf(((Button) v).getText()))) return (Button) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                Button b = findButton32(g.getChildAt(i), text);
                if (b != null) return b;
            }
        }
        return null;
    }

    private void safeDestroy32(WebView w) {
        try { if (w != null && w != web32) w.destroy(); } catch (Exception ignored) { }
    }

    private String token32(String s) {
        String x = safe32(s).replaceAll("[^A-Za-z0-9_.-]", "_");
        return x.length() > 40 ? x.substring(0, 40) : x;
    }

    private String safe32(String s) { return s == null ? "" : s; }

    private int dp32(int x) {
        return Math.max(1, Math.round(x * getResources().getDisplayMetrics().density));
    }
}
