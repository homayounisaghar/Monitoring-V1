package com.homayounisaghar.chatgptwebviewprobe;

import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.CookieManager;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.json.JSONObject;
import org.json.JSONTokener;

import java.lang.reflect.Field;
import java.lang.reflect.Method;

/**
 * v0.32.1 auth-readiness repair.
 *
 * The first v0.32 real-device launch proved Auth Mode was running, but its readiness
 * classifier falsely treated the anonymous ChatGPT landing page as authenticated
 * because that page now exposes a visible composer. This wrapper keeps all v0.32
 * contained-auth navigation/deep-link behavior, removes the legacy false-positive
 * poller, and requires BOTH a usable composer AND absence of a visible Login control
 * before capability mode is enabled.
 *
 * No passwords, OTPs, cookies, tokens, form values, raw URLs or HTML are read/uploaded.
 */
public class OrchestratorAuthModeV33Activity extends OrchestratorAuthModeV32Activity {
    private final Handler h33 = new Handler(Looper.getMainLooper());
    private final Runnable poll33 = new Runnable() {
        @Override public void run() {
            pollCorrectedAuth33();
            h33.postDelayed(this, 650L);
        }
    };

    private WebView web33;
    private String lastClass33 = "-";

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web33 = findWeb33(getWindow().getDecorView());
        stopLegacyPoll33();
        installCorrectedWebViewClient33();
        forceAuthUi33(true, "Login required — use ChatGPT Log in above or the in-app login button below.");
        retitleLegacyStatus33();
        h33.postDelayed(poll33, 100L);
    }

    @Override protected void onResume() {
        super.onResume();
        stopLegacyPoll33();
        h33.removeCallbacks(poll33);
        h33.postDelayed(poll33, 100L);
    }

    @Override protected void onDestroy() {
        h33.removeCallbacksAndMessages(null);
        stopLegacyPoll33();
        super.onDestroy();
    }

    private void installCorrectedWebViewClient33() {
        if (web33 == null) return;
        web33.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request == null || request.getUrl() == null ? null : request.getUrl().toString();
                return invokeMainNavigation33(view, url);
            }

            @SuppressWarnings("deprecation")
            @Override public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return invokeMainNavigation33(view, url);
            }

            @Override public void onPageStarted(WebView view, String url, Bitmap favicon) {
                invokeObserveNav33(url, false);
                super.onPageStarted(view, url, favicon);
            }

            @Override public void onPageFinished(WebView view, String url) {
                CookieManager.getInstance().flush();
                invokeObserveNav33(url, false);
                stopLegacyPoll33();
                h33.removeCallbacks(poll33);
                h33.postDelayed(poll33, 100L);
                super.onPageFinished(view, url);
            }
        });
    }

    private void pollCorrectedAuth33() {
        if (web33 == null) return;
        stopLegacyPoll33();
        String js = "(function(){try{"
                + "const vis=e=>{if(!e)return false;const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';};"
                + "const norm=x=>(x||'').replace(/\\s+/g,' ').trim().toLowerCase();"
                + "const c=document.querySelector('#prompt-textarea')||Array.from(document.querySelectorAll('textarea,[contenteditable=\\\"true\\\"]')).filter(vis).slice(-1)[0]||null;"
                + "const controls=Array.from(document.querySelectorAll('a,button,[role=\\\"button\\\"]')).filter(vis);"
                + "const login=controls.filter(e=>{const t=norm(e.getAttribute('aria-label')||e.innerText||e.textContent||'');const h=(e.getAttribute('href')||'').toLowerCase();return t==='log in'||t==='login'||h.includes('/auth/login');});"
                + "const body=((document.body&&document.body.innerText)||'').toLowerCase();"
                + "const expired=body.includes('your session has expired')||body.includes('log in again to continue');"
                + "const host=(location.hostname||'').toLowerCase();"
                + "const prod=host==='chatgpt.com'||host.endsWith('.chatgpt.com');"
                + "const anonymous=prod&&(expired||login.length>0);"
                + "const ready=prod&&vis(c)&&!expired&&login.length===0;"
                + "return JSON.stringify({ready:ready,anonymous:anonymous,login_count:login.length,expired:expired,host:host});"
                + "}catch(e){return JSON.stringify({ready:false,anonymous:false,login_count:-1,expired:false,host:''});}})();";
        web33.evaluateJavascript(js, value -> {
            try {
                String s = value == null ? "" : value;
                Object outer = new JSONTokener(s).nextValue();
                if (outer instanceof String) s = (String) outer;
                JSONObject o = new JSONObject(s);
                boolean ready = o.optBoolean("ready", false);
                boolean anonymous = o.optBoolean("anonymous", false);
                if (ready) {
                    forceAuthUi33(false, "Authenticated ChatGPT ready.");
                    emitClass33("AUTH_READY_CORRECTED", "PASS");
                    return;
                }
                if (anonymous) {
                    forceAuthUi33(true, "Login required — use ChatGPT Log in above or the in-app login button below.");
                    emitClass33("AUTH_ANONYMOUS_CONFIRMED", "AUTH_REQUIRED");
                    return;
                }
                forceAuthUi33(true, "Auth Mode active — complete the current login/MFA step in this app.");
                emitClass33("AUTH_IN_PROGRESS", "ACTIVE");
            } catch (Exception e) {
                forceAuthUi33(true, "Auth state unresolved — capability mode remains locked.");
                emitClass33("AUTH_STATE_UNRESOLVED", "FAIL_CLOSED");
            }
        });
    }

    private void forceAuthUi33(boolean active, String message) {
        try {
            setField33("authMode32", active);
            setField33("authReady32", !active);
            Object panel = getField33("authPanel32");
            if (panel instanceof View) ((View) panel).setVisibility(active ? View.VISIBLE : View.GONE);
            Object login = getField33("loginButton32");
            if (login instanceof Button) ((Button) login).setEnabled(active);
            Object model = getField33("modelButton32");
            if (model instanceof Button) ((Button) model).setEnabled(!active);
            Object status = getField33("authStatus32");
            if (status instanceof TextView) ((TextView) status).setText("AUTH MODE: " + message);
        } catch (Exception ignored) { }
    }

    private void stopLegacyPoll33() {
        try {
            Field hf = OrchestratorAuthModeV32Activity.class.getDeclaredField("h32");
            hf.setAccessible(true);
            Object h = hf.get(this);
            Field rf = OrchestratorAuthModeV32Activity.class.getDeclaredField("authPoll32");
            rf.setAccessible(true);
            Object r = rf.get(this);
            if (h instanceof Handler && r instanceof Runnable) ((Handler) h).removeCallbacks((Runnable) r);
        } catch (Exception ignored) { }
    }

    private boolean invokeMainNavigation33(WebView view, String url) {
        try {
            Method m = OrchestratorAuthModeV32Activity.class.getDeclaredMethod("handleMainNavigation32", WebView.class, String.class);
            m.setAccessible(true);
            Object r = m.invoke(this, view, url);
            return r instanceof Boolean && (Boolean) r;
        } catch (Exception e) {
            forceAuthUi33(true, "Navigation resolver failed — blocked for safety.");
            return true;
        }
    }

    private void invokeObserveNav33(String url, boolean popup) {
        try {
            Method m = OrchestratorAuthModeV32Activity.class.getDeclaredMethod("observeNavigation32", String.class, boolean.class);
            m.setAccessible(true);
            m.invoke(this, url, popup);
        } catch (Exception ignored) { }
    }

    private void emitClass33(String phase, String classification) {
        if (phase.equals(lastClass33)) return;
        lastClass33 = phase;
        try {
            Method m = OrchestratorAuthModeV32Activity.class.getDeclaredMethod("phase32", String.class, String.class, String.class);
            m.setAccessible(true);
            m.invoke(this, phase, classification, "CORRECTED_READY_GATE");
        } catch (Exception ignored) { }
    }

    private Object getField33(String name) throws Exception {
        Field f = OrchestratorAuthModeV32Activity.class.getDeclaredField(name);
        f.setAccessible(true);
        return f.get(this);
    }

    private void setField33(String name, Object value) throws Exception {
        Field f = OrchestratorAuthModeV32Activity.class.getDeclaredField(name);
        f.setAccessible(true);
        f.set(this, value);
    }

    private void retitleLegacyStatus33() {
        retitleWalk33(getWindow().getDecorView());
    }

    private void retitleWalk33(View v) {
        if (v instanceof TextView && !(v instanceof Button)) {
            TextView t = (TextView) v;
            String s = String.valueOf(t.getText());
            if (s.startsWith("v0.31 capability picker test ready")) {
                t.setText("v0.32.1 Auth/MFA readiness fix");
            }
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) retitleWalk33(g.getChildAt(i));
        }
    }

    private WebView findWeb33(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                WebView w = findWeb33(g.getChildAt(i));
                if (w != null) return w;
            }
        }
        return null;
    }
}
