package com.homayounisaghar.wakehandshakeprobe;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.Looper;
import android.webkit.CookieManager;
import android.webkit.WebSettings;
import android.webkit.WebStorage;
import android.webkit.WebView;

final class PerplexitySessionCompat {
    private static final String PREFS = "perplexity_session_compat";
    private static final String PREF_DEFAULT_UA_RESET_V015 = "default_ua_reset_v015";

    private PerplexitySessionCompat() {}

    static void configure(WebView webView) {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        // Deliberately keep Android WebView's default, unmodified User-Agent.
        // Cloudflare Turnstile binds challenge/clearance state to a consistent
        // browser environment; a spoofed browser UA can invalidate that state.
        CookieManager cm = CookieManager.getInstance();
        cm.setAcceptCookie(true);
        cm.setAcceptThirdPartyCookies(webView, true);
    }

    static boolean needsDefaultUaReset(Context context) {
        return !context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
                .getBoolean(PREF_DEFAULT_UA_RESET_V015, false);
    }

    static void resetLegacyProfileOnce(Context context, Runnable done) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        if (prefs.getBoolean(PREF_DEFAULT_UA_RESET_V015, false)) {
            post(done);
            return;
        }
        clearSession(context, () -> {
            prefs.edit().putBoolean(PREF_DEFAULT_UA_RESET_V015, true).apply();
            if (done != null) done.run();
        });
    }

    static void clearSession(Context context, Runnable done) {
        Handler main = new Handler(Looper.getMainLooper());
        Runnable finish = () -> {
            try { WebStorage.getInstance().deleteAllData(); } catch (Exception ignored) {}
            try { CookieManager.getInstance().flush(); } catch (Exception ignored) {}
            if (done != null) main.post(done);
        };
        try {
            CookieManager.getInstance().removeAllCookies(value -> finish.run());
        } catch (Exception e) {
            finish.run();
        }
    }

    private static void post(Runnable runnable) {
        if (runnable == null) return;
        new Handler(Looper.getMainLooper()).post(runnable);
    }
}
