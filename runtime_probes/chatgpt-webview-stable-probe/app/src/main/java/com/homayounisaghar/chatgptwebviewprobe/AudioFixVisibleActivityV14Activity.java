package com.homayounisaghar.chatgptwebviewprobe;

import android.Manifest;
import android.content.ContentValues;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.MediaStore;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.webkit.JavaScriptReplyProxy;
import androidx.webkit.ScriptHandler;
import androidx.webkit.WebMessageCompat;
import androidx.webkit.WebViewCompat;
import androidx.webkit.WebViewFeature;

import org.json.JSONObject;

import java.io.OutputStream;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Date;
import java.util.Locale;
import java.util.Set;

/**
 * Stable v0.14: minimal audio-fix A/B + visible response-activity probe.
 *
 * Audio experiment: the APK adds android.permission.MODIFY_AUDIO_SETTINGS while
 * retaining v0.13's real ChatGPT getUserMedia trace. No routing/mode mutation is
 * introduced, so a change from NotReadableError is attributable to the manifest
 * permission rather than a second audio intervention.
 *
 * Dashboard experiment: observe only browser-visible response activity. A
 * document-start MutationObserver watches semantic assistant-turn mutations,
 * stop/streaming controls and visible status/progress nodes. Raw visible status
 * text may be displayed transiently in this Activity but is never written to the
 * report. Hidden model chain-of-thought is neither requested nor accessed.
 */
public class AudioFixVisibleActivityV14Activity extends AudioEarlyTraceV13Activity {
    private static final Set<String> ORIGINS = Collections.singleton("https://chatgpt.com");
    private final Handler h14 = new Handler(Looper.getMainLooper());
    private final StringBuilder events14 = new StringBuilder();

    private WebView web14;
    private TextView status14;
    private ScriptHandler activityScriptHandler;

    private boolean activityBridgeInstalled = false;
    private boolean activityDocStartSupported = false;
    private boolean activityDocStartSeen = false;
    private boolean assistantActive = false;
    private boolean stopControlPresent = false;
    private int activityBridgeMessages = 0;
    private int assistantChangeEvents = 0;
    private int visibleStatusChanges = 0;
    private int visibleStatusNodeCount = 0;
    private int lastAssistantLen = 0;
    private long lastAssistantChangeAt = 0L;
    private String lastAssistantSig = "-";
    private String lastVisibleStatusHash = "-";
    private int lastVisibleStatusLen = 0;
    private String lastVisibleStatusKind = "-";
    private String transientVisibleStatus = "";

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web14 = findWeb(getWindow().getDecorView());
        if (web14 == null) return;
        web14.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        retitleParentControls(getWindow().getDecorView());
        addV14StatusPanel();
        installVisibleActivityInfrastructure();
        ev14("V14_READY_MODIFY_AUDIO_SETTINGS_EXPERIMENT");
        render14();
    }

    private void retitleParentControls(View v) {
        if (v instanceof Button) {
            Button b = (Button) v;
            String t = String.valueOf(b.getText());
            if ("AUDIO TRACE13".equals(t)) b.setText("AUDIO FIX14");
            if ("REPORT13".equals(t)) {
                b.setText("REPORT14");
                b.setOnClickListener(x -> saveReport14());
            }
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) retitleParentControls(g.getChildAt(i));
        }
    }

    private void addV14StatusPanel() {
        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) content;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        int wi = root.indexOfChild(web14);
        if (wi < 0) wi = 0;

        status14 = new TextView(this);
        status14.setTextSize(8.5f);
        status14.setTextIsSelectable(true);
        status14.setPadding(dp14(7), dp14(2), dp14(7), dp14(2));
        ScrollView sv = new ScrollView(this);
        sv.addView(status14, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));
        root.addView(sv, wi, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp14(70)));
    }

    private void installVisibleActivityInfrastructure() {
        activityDocStartSupported = WebViewFeature.isFeatureSupported(WebViewFeature.DOCUMENT_START_SCRIPT);
        boolean listenerSupported = WebViewFeature.isFeatureSupported(WebViewFeature.WEB_MESSAGE_LISTENER);
        if (!listenerSupported) {
            ev14("ACTIVITY_WEB_MESSAGE_LISTENER_UNSUPPORTED");
            return;
        }
        try {
            WebViewCompat.addWebMessageListener(web14, "cp14activity", ORIGINS,
                    new WebViewCompat.WebMessageListener() {
                        @Override public void onPostMessage(WebView view, WebMessageCompat message,
                                                            Uri sourceOrigin, boolean isMainFrame,
                                                            JavaScriptReplyProxy replyProxy) {
                            if (!trustedOrigin14(sourceOrigin) || !isMainFrame) return;
                            if (message.getType() != WebMessageCompat.TYPE_STRING) return;
                            String data = message.getData();
                            if (data == null || data.length() > 4096) return;
                            consumeActivityBridge(data);
                        }
                    });
            activityBridgeInstalled = true;
            ev14("ACTIVITY_WEB_MESSAGE_LISTENER_INSTALLED");
        } catch (Exception e) {
            ev14("ACTIVITY_WEB_MESSAGE_LISTENER_FAIL_" + e.getClass().getSimpleName());
            return;
        }

        if (activityDocStartSupported) {
            try {
                activityScriptHandler = WebViewCompat.addDocumentStartJavaScript(web14, ACTIVITY_JS, ORIGINS);
                ev14("ACTIVITY_DOCUMENT_START_SCRIPT_INSTALLED");
            } catch (Exception e) {
                ev14("ACTIVITY_DOCUMENT_START_FAIL_" + e.getClass().getSimpleName());
            }
        } else ev14("ACTIVITY_DOCUMENT_START_UNSUPPORTED");

        // Observe the already-loaded document too. The next AUDIO FIX14 reload will
        // install the same observer at document start before ChatGPT site scripts.
        h14.postDelayed(() -> {
            if (web14 != null) web14.evaluateJavascript(ACTIVITY_JS, value -> ev14("ACTIVITY_LATE_FALLBACK_DISPATCHED"));
        }, 300L);
    }

    private void consumeActivityBridge(String data) {
        try {
            JSONObject root = new JSONObject(data);
            String type = tok14(root.optString("t", "UNKNOWN"));
            JSONObject d = root.optJSONObject("d");
            if (d == null) d = new JSONObject();
            activityBridgeMessages++;
            switch (type) {
                case "DOC_START":
                    activityDocStartSeen = true;
                    break;
                case "ASSISTANT_CHANGE":
                    assistantChangeEvents++;
                    lastAssistantLen = d.optInt("len", 0);
                    lastAssistantSig = tok14(d.optString("sig", "-"));
                    lastAssistantChangeAt = System.currentTimeMillis();
                    break;
                case "VISIBLE_STATUS":
                    visibleStatusChanges++;
                    visibleStatusNodeCount = d.optInt("nodes", 0);
                    lastVisibleStatusKind = tok14(d.optString("kind", "-"));
                    String raw = d.optString("text", "");
                    if (raw.length() > 220) raw = raw.substring(0, 220);
                    transientVisibleStatus = raw;
                    lastVisibleStatusLen = raw.length();
                    lastVisibleStatusHash = raw.isEmpty() ? "-" : sha256Hex(raw);
                    break;
                case "ACTIVITY_STATE":
                    assistantActive = d.optBoolean("active", false);
                    stopControlPresent = d.optBoolean("stop", false);
                    visibleStatusNodeCount = d.optInt("statusNodes", visibleStatusNodeCount);
                    break;
                default:
                    break;
            }
            if (events14.length() < 22000) {
                events14.append(stamp14()).append(" | ").append(type)
                        .append(" active=").append(d.optBoolean("active", false))
                        .append(" stop=").append(d.optBoolean("stop", false))
                        .append(" nodes=").append(d.optInt("statusNodes", d.optInt("nodes", -1)))
                        .append(" len=").append(d.optInt("len", -1))
                        .append(" kind=").append(tok14(d.optString("kind", "-")))
                        .append('\n');
            }
            render14();
        } catch (Exception e) {
            ev14("ACTIVITY_BRIDGE_PARSE_FAIL_" + e.getClass().getSimpleName());
        }
    }

    private void render14() {
        if (status14 == null) return;
        long age = lastAssistantChangeAt == 0L ? -1L : Math.max(0L, System.currentTimeMillis() - lastAssistantChangeAt);
        String visible = transientVisibleStatus.isEmpty() ? "(none)" : transientVisibleStatus;
        StringBuilder s = new StringBuilder();
        s.append("v0.14 AUDIO FIX + VISIBLE ACTIVITY\n");
        s.append("MODIFY_AUDIO_SETTINGS=")
                .append(checkSelfPermission(Manifest.permission.MODIFY_AUDIO_SETTINGS) == PackageManager.PERMISSION_GRANTED ? "GRANTED" : "DENIED")
                .append(" DocStart=").append(activityDocStartSeen)
                .append(" Active=").append(assistantActive)
                .append(" Stop=").append(stopControlPresent).append('\n');
        s.append("AssistantChanges=").append(assistantChangeEvents)
                .append(" lastAgeMs=").append(age)
                .append(" statusNodes=").append(visibleStatusNodeCount)
                .append(" statusChanges=").append(visibleStatusChanges).append('\n');
        s.append("VisibleStatus: ").append(visible);
        status14.setText(s.toString());
        h14.removeCallbacks(renderTick);
        h14.postDelayed(renderTick, 600L);
    }

    private final Runnable renderTick = new Runnable() {
        @Override public void run() { render14(); }
    };

    private void saveReport14() {
        try {
            String name = "chatgpt-webview-v14-audio-fix-visible-activity-"
                    + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".txt";
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            cv.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
            cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (u == null) throw new IllegalStateException("insert");
            try (OutputStream out = getContentResolver().openOutputStream(u)) {
                if (out == null) throw new IllegalStateException("stream");
                out.write(reportText14().getBytes(StandardCharsets.UTF_8));
            }
            Toast.makeText(this, "v0.14 report saved to Downloads", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "REPORT14 failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
        }
    }

    private String reportText14() {
        StringBuilder r = new StringBuilder();
        r.append("CHATGPT_WEBVIEW_STABLE_V14_AUDIO_FIX_VISIBLE_ACTIVITY\n");
        r.append("MODIFY_AUDIO_SETTINGS_PERMISSION=")
                .append(checkSelfPermission(Manifest.permission.MODIFY_AUDIO_SETTINGS) == PackageManager.PERMISSION_GRANTED ? "GRANTED" : "DENIED").append('\n');
        r.append("AUDIO_FIX_INTERVENTION=MANIFEST_PERMISSION_ONLY\n");
        r.append("ACTIVITY_WEB_MESSAGE_LISTENER_INSTALLED=").append(activityBridgeInstalled).append('\n');
        r.append("ACTIVITY_DOCUMENT_START_SUPPORTED=").append(activityDocStartSupported).append('\n');
        r.append("ACTIVITY_DOCUMENT_START_SEEN=").append(activityDocStartSeen).append('\n');
        r.append("ACTIVITY_BRIDGE_MESSAGES=").append(activityBridgeMessages).append('\n');
        r.append("ASSISTANT_ACTIVITY_ACTIVE=").append(assistantActive).append('\n');
        r.append("STOP_CONTROL_PRESENT=").append(stopControlPresent).append('\n');
        r.append("ASSISTANT_CHANGE_EVENTS=").append(assistantChangeEvents).append('\n');
        r.append("LAST_ASSISTANT_LENGTH=").append(lastAssistantLen).append('\n');
        r.append("LAST_ASSISTANT_SIGNATURE=").append(lastAssistantSig).append('\n');
        r.append("VISIBLE_STATUS_NODE_COUNT=").append(visibleStatusNodeCount).append('\n');
        r.append("VISIBLE_STATUS_CHANGES=").append(visibleStatusChanges).append('\n');
        r.append("LAST_VISIBLE_STATUS_KIND=").append(lastVisibleStatusKind).append('\n');
        r.append("LAST_VISIBLE_STATUS_LENGTH=").append(lastVisibleStatusLen).append('\n');
        r.append("LAST_VISIBLE_STATUS_SHA256=").append(lastVisibleStatusHash).append('\n');
        r.append("VISIBLE_STATUS_RAW_PERSISTED=false\n");
        r.append("VISIBLE_STATUS_TRANSIENT_DISPLAY=true\n");
        r.append("HIDDEN_CHAIN_OF_THOUGHT_ACCESSED=false\n");
        r.append("--- V14 ACTIVITY EVENT LOG ---\n").append(events14);
        r.append("--- V13 AUDIO TRACE BASE ---\n").append(parentV13Report());
        return r.toString();
    }

    private String parentV13Report() {
        try {
            Method m = AudioEarlyTraceV13Activity.class.getDeclaredMethod("reportText");
            m.setAccessible(true);
            Object x = m.invoke(this);
            return x == null ? "V13_REPORT_UNAVAILABLE\n" : String.valueOf(x);
        } catch (Exception e) {
            return "V13_REPORT_REFLECTION_FAIL=" + e.getClass().getSimpleName() + "\n";
        }
    }

    private boolean trustedOrigin14(Uri u) {
        return u != null && "https".equalsIgnoreCase(u.getScheme())
                && "chatgpt.com".equalsIgnoreCase(u.getHost());
    }

    private static String sha256Hex(String s) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] b = md.digest(s.getBytes(StandardCharsets.UTF_8));
            StringBuilder out = new StringBuilder();
            for (byte x : b) out.append(String.format(Locale.US, "%02x", x & 0xff));
            return out.toString();
        } catch (Exception e) { return "HASH_ERROR"; }
    }

    private void ev14(String s) {
        if (events14.length() < 22000) events14.append(stamp14()).append(" | ").append(tok14(s)).append('\n');
    }

    private static String stamp14() {
        return new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date());
    }

    private static String tok14(String s) {
        String x = s == null ? "-" : s.replaceAll("[^A-Za-z0-9_.:+/@=-]", "_");
        return x.length() > 180 ? x.substring(0, 180) : x;
    }

    private int dp14(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }

    private WebView findWeb(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (!(v instanceof ViewGroup)) return null;
        ViewGroup g = (ViewGroup) v;
        for (int i = 0; i < g.getChildCount(); i++) {
            WebView z = findWeb(g.getChildAt(i));
            if (z != null) return z;
        }
        return null;
    }

    @Override protected void onDestroy() {
        h14.removeCallbacksAndMessages(null);
        try { if (activityScriptHandler != null) activityScriptHandler.remove(); } catch (Exception ignored) { }
        super.onDestroy();
    }

    private static final String ACTIVITY_JS =
            "(function(){try{if(window.__cp14ActivityInstalled)return;window.__cp14ActivityInstalled=true;"
            + "const S=(t,d)=>{try{cp14activity.postMessage(JSON.stringify({t:t,d:d||{}}));}catch(_){}};"
            + "const N=x=>String(x||'').replace(/\\s+/g,' ').trim();"
            + "const V=e=>{try{if(!e||!e.getBoundingClientRect)return false;const r=e.getBoundingClientRect();const s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none';}catch(_){return false;}};"
            + "const H=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0).toString(16);};"
            + "let lastAssistantSig='-',lastAssistantLen=-1,lastStatus='__init__',lastState='',lastChange=0,timer=0;"
            + "const latestAssistant=()=>{const a=[...document.querySelectorAll('[data-message-author-role=\\"assistant\\"]')].filter(V);if(!a.length)return null;const x=a[a.length-1];return x.closest('article[data-testid^=\\"conversation-turn-\\"]')||x;};"
            + "const stopPresent=()=>[...document.querySelectorAll('button,[role=\\"button\\"]')].some(e=>{if(!V(e))return false;const z=(N(e.getAttribute('aria-label'))+' '+N(e.getAttribute('data-testid'))+' '+N(e.textContent)).toLowerCase();return z.includes('stop generating')||z==='stop'||z.includes('stop-button')||z.includes('stop_response');});"
            + "const statusCandidate=()=>{let best=null;const all=[...document.querySelectorAll('[role=\\"status\\"],[aria-live],summary,[data-testid]')];for(const e of all){if(!V(e))continue;const txt=N(e.innerText||e.textContent);if(!txt||txt.length>220)continue;const role=(e.getAttribute('role')||'').toLowerCase();const live=(e.getAttribute('aria-live')||'').toLowerCase();const test=(e.getAttribute('data-testid')||'').toLowerCase();const semantic=role==='status'||e.tagName==='SUMMARY'||/reason|think|progress|status|research|browse|search/.test(test)||(live&&txt.length<=160);if(!semantic)continue;let score=0;if(role==='status')score+=5;if(/reason|think|progress|research/.test(test))score+=6;if(e.tagName==='SUMMARY')score+=4;if(live)score+=2;const k=role==='status'?'role_status':(e.tagName==='SUMMARY'?'summary':(/reason|think/.test(test)?'reasoning_testid':(/progress|status|research|browse|search/.test(test)?'progress_testid':'aria_live')));if(!best||score>best.score)best={text:txt,kind:k,score:score};}return best;};"
            + "const scan=()=>{try{const a=latestAssistant();let len=0,sig='-';if(a){const t=N(a.innerText||a.textContent);len=t.length;sig=H(t);}if(a&&(len!==lastAssistantLen||sig!==lastAssistantSig)){lastAssistantLen=len;lastAssistantSig=sig;lastChange=Date.now();S('ASSISTANT_CHANGE',{len:len,sig:sig});}"
            + "const c=statusCandidate();const st=c?c.text:'';if(st!==lastStatus){lastStatus=st;S('VISIBLE_STATUS',{text:st,len:st.length,kind:c?c.kind:'none',nodes:c?1:0});}"
            + "const stop=stopPresent();const active=stop||(Date.now()-lastChange<2500);const state=(active?'1':'0')+'|'+(stop?'1':'0')+'|'+(c?'1':'0');if(state!==lastState){lastState=state;S('ACTIVITY_STATE',{active:active,stop:stop,statusNodes:c?1:0});}}catch(_){}};"
            + "const boot=()=>{if(!document.documentElement)return;S('DOC_START',{ready:document.readyState});const o=new MutationObserver(()=>{clearTimeout(timer);timer=setTimeout(scan,90);});o.observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['aria-busy','aria-live','aria-label','data-testid']});scan();setInterval(scan,750);};"
            + "if(document.documentElement)boot();else document.addEventListener('DOMContentLoaded',boot,{once:true});"
            + "}catch(_){} })();";
}
