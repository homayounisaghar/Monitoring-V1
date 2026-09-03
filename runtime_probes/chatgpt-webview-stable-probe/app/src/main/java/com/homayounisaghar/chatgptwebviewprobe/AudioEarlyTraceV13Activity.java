package com.homayounisaghar.chatgptwebviewprobe;

import android.Manifest;
import android.app.AppOpsManager;
import android.content.ContentValues;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.os.Process;
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
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Date;
import java.util.Locale;
import java.util.Set;

/**
 * Stable v0.13 early audio trace.
 *
 * v0.12 proved native AudioRecord capture works, but its page self-test serialized
 * Permissions API -> enumerateDevices -> getUserMedia. On the real device the
 * Permissions API promise remained pending, so the direct GUM call was never
 * reached. v0.13 removes that contaminating GUM self-test entirely.
 *
 * A document-start probe is installed for the exact ChatGPT origin and the page is
 * reloaded once. The probe wraps MediaDevices.prototype.getUserMedia before site
 * JavaScript executes, then only observes ChatGPT's own Dictation/Voice calls.
 * Read-only Permissions API and enumerateDevices probes run independently with
 * watchdogs and cannot block one another. No PCM, speech, chat text, device ids,
 * labels, cookies or tokens are retained.
 */
public class AudioEarlyTraceV13Activity extends AudioModelSuiteV11FinalActivity {
    private static final int REQ_AUDIO = 1301;
    private static final long LEASE_MS = 10L * 60L * 1000L;
    private static final Set<String> ORIGINS = Collections.singleton("https://chatgpt.com");

    private final Handler h = new Handler(Looper.getMainLooper());
    private final StringBuilder events13 = new StringBuilder();

    private WebView web;
    private TextView status13;
    private Button traceButton;
    private ScriptHandler documentStartHandler;

    private boolean active = false;
    private long startedAt = 0L;
    private boolean bridgeInstalled = false;
    private boolean documentStartSupported = false;
    private boolean messageListenerSupported = false;
    private boolean reloadIssued = false;

    private String androidPermission = "NOT_CHECKED";
    private String appOps = "NOT_CHECKED";
    private String sysMute = "NOT_CHECKED";
    private String nativeMic = "NOT_RUN";
    private String webViewProvider = "-";
    private String earlyTrace = "NOT_ARMED";
    private String gumWrap = "NOT_SEEN";
    private String permissionsApi = "NOT_RUN";
    private String deviceCensus = "NOT_RUN";
    private String lastGumError = "-";

    private int bridgeMessages = 0;
    private int docStarts = 0;
    private int docStartsMain = 0;
    private int docStartsSub = 0;
    private int gumCalls = 0;
    private int gumCallsMain = 0;
    private int gumCallsSub = 0;
    private int gumResolves = 0;
    private int gumRejects = 0;
    private int gumThrows = 0;
    private int trackEvents = 0;
    private int rtcAudioEvents = 0;

    private final Runnable leasePoll = new Runnable() {
        @Override public void run() {
            if (!active) return;
            if (System.currentTimeMillis() - startedAt > LEASE_MS) {
                active = false;
                earlyTrace = "LEASE_EXPIRED";
                ev("TRACE_AUTO_STOP_LEASE_EXPIRED");
                render13();
                return;
            }
            render13();
            h.postDelayed(this, 400L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web = findWeb(getWindow().getDecorView());
        if (web == null) return;
        web.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        hideParentUiAndAddPanel();
        captureWebViewProvider();
        installEarlyInfrastructure();
        ev("V13_READY");
        render13();
    }

    private void hideParentUiAndAddPanel() {
        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) content;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        for (int i = 0; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            if (child != web) child.setVisibility(View.GONE);
        }

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);

        traceButton = new Button(this);
        traceButton.setText("AUDIO TRACE13");
        traceButton.setTextSize(8.5f);
        traceButton.setOnClickListener(v -> startRequested());
        row.addView(traceButton, new LinearLayout.LayoutParams(0, dp(39), 1f));

        Button report = new Button(this);
        report.setText("REPORT13");
        report.setTextSize(8.5f);
        report.setOnClickListener(v -> saveReport());
        row.addView(report, new LinearLayout.LayoutParams(0, dp(39), 1f));
        panel.addView(row, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(39)));

        status13 = new TextView(this);
        status13.setTextSize(8.8f);
        status13.setTextIsSelectable(true);
        status13.setPadding(dp(7), dp(2), dp(7), dp(2));
        ScrollView sv = new ScrollView(this);
        sv.addView(status13, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));
        panel.addView(sv, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(82)));

        int wi = root.indexOfChild(web);
        if (wi < 0) wi = root.getChildCount();
        root.addView(panel, wi, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void installEarlyInfrastructure() {
        messageListenerSupported = WebViewFeature.isFeatureSupported(WebViewFeature.WEB_MESSAGE_LISTENER);
        documentStartSupported = WebViewFeature.isFeatureSupported(WebViewFeature.DOCUMENT_START_SCRIPT);

        if (messageListenerSupported) {
            try {
                WebViewCompat.addWebMessageListener(web, "cp13bridge", ORIGINS,
                        new WebViewCompat.WebMessageListener() {
                            @Override public void onPostMessage(WebView view, WebMessageCompat message,
                                                                Uri sourceOrigin, boolean isMainFrame,
                                                                JavaScriptReplyProxy replyProxy) {
                                if (!trustedOrigin(sourceOrigin)) return;
                                if (message.getType() != WebMessageCompat.TYPE_STRING) return;
                                String data = message.getData();
                                if (data == null || data.length() > 4096) return;
                                consumeBridge(data, isMainFrame);
                            }
                        });
                bridgeInstalled = true;
                ev("WEB_MESSAGE_LISTENER_INSTALLED");
            } catch (Exception e) {
                bridgeInstalled = false;
                ev("WEB_MESSAGE_LISTENER_FAIL_" + e.getClass().getSimpleName());
            }
        } else ev("WEB_MESSAGE_LISTENER_UNSUPPORTED");

        if (documentStartSupported && bridgeInstalled) {
            try {
                documentStartHandler = WebViewCompat.addDocumentStartJavaScript(web, EARLY_JS, ORIGINS);
                earlyTrace = "INSTALLED_RELOAD_REQUIRED";
                ev("DOCUMENT_START_SCRIPT_INSTALLED");
            } catch (Exception e) {
                earlyTrace = "DOC_START_INSTALL_FAIL_" + e.getClass().getSimpleName();
                ev("DOCUMENT_START_SCRIPT_FAIL_" + e.getClass().getSimpleName());
            }
        } else if (!documentStartSupported) earlyTrace = "DOCUMENT_START_UNSUPPORTED";
        else earlyTrace = "BRIDGE_UNAVAILABLE";
    }

    private void startRequested() {
        if (web == null || !trustedUrl(web.getUrl())) {
            earlyTrace = "FAIL_NOT_CHATGPT_HTTPS";
            render13();
            return;
        }
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            androidPermission = "WAITING_RUNTIME_PERMISSION";
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQ_AUDIO);
            render13();
            return;
        }
        beginTrace();
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        if (requestCode != REQ_AUDIO) return;
        if (results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED) beginTrace();
        else {
            androidPermission = "DENIED";
            earlyTrace = "BLOCKED_ANDROID_PERMISSION_DENIED";
            ev("ANDROID_RECORD_AUDIO_DENIED");
            render13();
        }
    }

    private void beginTrace() {
        if (active) return;
        active = true;
        startedAt = System.currentTimeMillis();
        resetRunCounters();
        snapshotAndroid();
        armV11AudioLease();
        nativeMic = "RUNNING";
        ev("TRACE_STARTED_NO_DIRECT_GUM_SELFTEST");
        render13();

        new Thread(() -> {
            String result = nativeSelftest();
            runOnUiThread(() -> {
                nativeMic = result;
                ev("NATIVE_MIC_SELFTEST_" + tok(result));
                if (documentStartSupported && bridgeInstalled && documentStartHandler != null) {
                    earlyTrace = "RELOADING_FOR_DOCUMENT_START";
                    reloadIssued = true;
                    ev("TRACE_RELOAD_ISSUED");
                    web.reload();
                    h.postDelayed(this::runReadOnlyProbes, 2600L);
                } else {
                    earlyTrace = "LATE_FALLBACK_ACTIVE";
                    web.evaluateJavascript(EARLY_JS_FALLBACK, value -> {
                        ev("LATE_FALLBACK_INJECTED");
                        runReadOnlyProbes();
                    });
                }
                h.removeCallbacks(leasePoll);
                h.post(leasePoll);
                render13();
            });
        }, "v13-native-mic").start();
    }

    private void resetRunCounters() {
        bridgeMessages = docStarts = docStartsMain = docStartsSub = 0;
        gumCalls = gumCallsMain = gumCallsSub = 0;
        gumResolves = gumRejects = gumThrows = 0;
        trackEvents = rtcAudioEvents = 0;
        permissionsApi = "NOT_RUN";
        deviceCensus = "NOT_RUN";
        lastGumError = "-";
        gumWrap = "NOT_SEEN";
        reloadIssued = false;
    }

    private void runReadOnlyProbes() {
        if (!active || web == null || !trustedUrl(web.getUrl())) return;
        web.evaluateJavascript(READ_ONLY_JS, value -> ev("READ_ONLY_PROBES_DISPATCHED"));
    }

    private void consumeBridge(String data, boolean isMainFrame) {
        try {
            JSONObject root = new JSONObject(data);
            String type = tok(root.optString("t", "UNKNOWN"));
            JSONObject d = root.optJSONObject("d");
            if (d == null) d = new JSONObject();
            bridgeMessages++;
            switch (type) {
                case "DOC_START":
                    docStarts++;
                    if (isMainFrame) docStartsMain++; else docStartsSub++;
                    if (isMainFrame) earlyTrace = "ACTIVE_DOCUMENT_START";
                    break;
                case "GUM_WRAP": gumWrap = d.optBoolean("ok", false) ? "PASS" : "FAIL"; break;
                case "GUM_WRAP_FAIL": gumWrap = "FAIL_" + tok(d.optString("name", "UNKNOWN")); break;
                case "GUM_CALL":
                    gumCalls++;
                    if (isMainFrame) gumCallsMain++; else gumCallsSub++;
                    break;
                case "GUM_OK": gumResolves++; break;
                case "GUM_FAIL":
                    gumRejects++;
                    lastGumError = tok(d.optString("name", "UNKNOWN"));
                    break;
                case "GUM_THROW":
                    gumThrows++;
                    lastGumError = tok(d.optString("name", "UNKNOWN"));
                    break;
                case "TRACK_MUTE":
                case "TRACK_UNMUTE":
                case "TRACK_ENDED": trackEvents++; break;
                case "RTC_AUDIO": rtcAudioEvents++; break;
                case "PERM": permissionsApi = tok(d.optString("state", "UNKNOWN")); break;
                case "PERM_TIMEOUT": permissionsApi = "TIMEOUT"; break;
                case "PERM_ERROR": permissionsApi = "ERROR_" + tok(d.optString("name", "UNKNOWN")); break;
                case "ENUM":
                    deviceCensus = "total=" + d.optInt("total", -1)
                            + "_audioIn=" + d.optInt("audioIn", -1)
                            + "_labelsPresent=" + d.optInt("labels", -1);
                    break;
                case "ENUM_TIMEOUT": deviceCensus = "TIMEOUT"; break;
                case "ENUM_ERROR": deviceCensus = "ERROR_" + tok(d.optString("name", "UNKNOWN")); break;
                default: break;
            }
            if (events13.length() < 26000) {
                events13.append(stamp()).append(" | JS_").append(type)
                        .append(" frame=").append(isMainFrame ? "MAIN" : "SUB")
                        .append(" | ").append(safeEventData(d)).append('\n');
            }
            render13();
        } catch (Exception e) {
            ev("BRIDGE_PARSE_FAIL_" + e.getClass().getSimpleName());
        }
    }

    private void snapshotAndroid() {
        androidPermission = checkSelfPermission(Manifest.permission.RECORD_AUDIO)
                == PackageManager.PERMISSION_GRANTED ? "GRANTED" : "DENIED";
        try {
            AppOpsManager a = (AppOpsManager) getSystemService(APP_OPS_SERVICE);
            int mode = a.unsafeCheckOpNoThrow(AppOpsManager.OPSTR_RECORD_AUDIO,
                    Process.myUid(), getPackageName());
            appOps = appOpsMode(mode);
        } catch (Exception e) { appOps = "ERROR_" + e.getClass().getSimpleName(); }
        try {
            AudioManager am = (AudioManager) getSystemService(AUDIO_SERVICE);
            sysMute = am != null && am.isMicrophoneMute() ? "MUTED" : "NOT_MUTED";
        } catch (Exception e) { sysMute = "ERROR_" + e.getClass().getSimpleName(); }
    }

    private void captureWebViewProvider() {
        try {
            PackageInfo p = WebView.getCurrentWebViewPackage();
            webViewProvider = p == null ? "UNKNOWN" : tok(p.packageName) + "@" + tok(p.versionName);
        } catch (Exception e) { webViewProvider = "ERROR_" + e.getClass().getSimpleName(); }
    }

    private String nativeSelftest() {
        AudioRecord ar = null;
        try {
            int sr = 16000;
            int min = AudioRecord.getMinBufferSize(sr, AudioFormat.CHANNEL_IN_MONO,
                    AudioFormat.ENCODING_PCM_16BIT);
            if (min <= 0) return "FAIL_MIN_BUFFER_" + min;
            ar = new AudioRecord(MediaRecorder.AudioSource.MIC, sr,
                    AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT,
                    Math.max(min * 2, 4096));
            if (ar.getState() != AudioRecord.STATE_INITIALIZED) return "FAIL_NOT_INITIALIZED";
            ar.startRecording();
            short[] buf = new short[800];
            int frames = 0;
            boolean nonZero = false;
            long deadline = System.currentTimeMillis() + 450L;
            while (System.currentTimeMillis() < deadline && frames < 3200) {
                int n = ar.read(buf, 0, buf.length, AudioRecord.READ_BLOCKING);
                if (n < 0) return "FAIL_READ_" + n;
                frames += n;
                for (int i = 0; i < n; i++) {
                    if (buf[i] != 0) { nonZero = true; break; }
                }
            }
            return frames > 0 ? "PASS_frames=" + frames + "_nonzero=" + nonZero : "FAIL_NO_FRAMES";
        } catch (SecurityException e) { return "FAIL_SECURITY_EXCEPTION";
        } catch (Exception e) { return "FAIL_" + e.getClass().getSimpleName();
        } finally {
            if (ar != null) {
                try { if (ar.getRecordingState() == AudioRecord.RECORDSTATE_RECORDING) ar.stop(); } catch (Exception ignored) { }
                try { ar.release(); } catch (Exception ignored) { }
            }
        }
    }

    private void armV11AudioLease() {
        try {
            Method m = AudioModelSuiteV11Activity.class.getDeclaredMethod("startAudioWatch");
            m.setAccessible(true);
            m.invoke(this);
            ev("V11_AUDIO_LEASE_ARMED_BY_V13");
        } catch (Exception e) { ev("V11_AUDIO_LEASE_ARM_FAIL_" + e.getClass().getSimpleName()); }
    }

    private void render13() {
        if (status13 == null) return;
        StringBuilder s = new StringBuilder();
        s.append("v0.13 EARLY AUDIO TRACE active=").append(active).append('\n');
        s.append("Android=").append(androidPermission).append(" AppOps=").append(appOps)
                .append(" SysMute=").append(sysMute).append('\n');
        s.append("NativeMic=").append(nativeMic).append(" Early=").append(earlyTrace)
                .append(" Wrap=").append(gumWrap).append('\n');
        s.append("DocStart=").append(docStarts).append(" msg=").append(bridgeMessages)
                .append(" GUM=").append(gumCalls).append('/').append(gumResolves)
                .append('/').append(gumRejects).append('/').append(gumThrows)
                .append(" err=").append(lastGumError).append('\n');
        s.append("PermAPI=").append(permissionsApi).append(" Devices=").append(deviceCensus);
        status13.setText(s.toString());
        if (traceButton != null) traceButton.setText(active ? "TRACE ACTIVE" : "AUDIO TRACE13");
    }

    private void saveReport() {
        try {
            String name = "chatgpt-webview-v13-early-audio-trace-"
                    + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".txt";
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            cv.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
            cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (u == null) throw new IllegalStateException("insert");
            try (OutputStream out = getContentResolver().openOutputStream(u)) {
                if (out == null) throw new IllegalStateException("stream");
                out.write(reportText().getBytes(StandardCharsets.UTF_8));
            }
            Toast.makeText(this, "v0.13 report saved to Downloads", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "REPORT13 failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
        }
    }

    private String reportText() {
        StringBuilder r = new StringBuilder();
        r.append("CHATGPT_WEBVIEW_STABLE_V13_EARLY_AUDIO_TRACE\n");
        r.append("CURRENT_URL=").append(sanitizeUrl(web == null ? "" : web.getUrl())).append('\n');
        r.append("ANDROID_RECORD_AUDIO_PERMISSION=").append(androidPermission).append('\n');
        r.append("ANDROID_RECORD_AUDIO_APPOPS=").append(appOps).append('\n');
        r.append("ANDROID_AUDIO_MANAGER_MIC_MUTE=").append(sysMute).append('\n');
        r.append("NATIVE_AUDIORECORD_SELFTEST=").append(nativeMic).append('\n');
        r.append("WEBVIEW_PROVIDER=").append(webViewProvider).append('\n');
        r.append("WEB_MESSAGE_LISTENER_SUPPORTED=").append(messageListenerSupported).append('\n');
        r.append("WEB_MESSAGE_LISTENER_INSTALLED=").append(bridgeInstalled).append('\n');
        r.append("DOCUMENT_START_SCRIPT_SUPPORTED=").append(documentStartSupported).append('\n');
        r.append("RELOAD_ISSUED=").append(reloadIssued).append('\n');
        r.append("EARLY_TRACE_STATUS=").append(earlyTrace).append('\n');
        r.append("GUM_WRAP_STATUS=").append(gumWrap).append('\n');
        r.append("DOC_START_MESSAGES=").append(docStarts).append('\n');
        r.append("DOC_START_MAIN=").append(docStartsMain).append('\n');
        r.append("DOC_START_SUB=").append(docStartsSub).append('\n');
        r.append("BRIDGE_MESSAGES=").append(bridgeMessages).append('\n');
        r.append("CHATGPT_GUM_CALLS=").append(gumCalls).append('\n');
        r.append("CHATGPT_GUM_CALLS_MAIN=").append(gumCallsMain).append('\n');
        r.append("CHATGPT_GUM_CALLS_SUB=").append(gumCallsSub).append('\n');
        r.append("CHATGPT_GUM_RESOLVES=").append(gumResolves).append('\n');
        r.append("CHATGPT_GUM_REJECTS=").append(gumRejects).append('\n');
        r.append("CHATGPT_GUM_THROWS=").append(gumThrows).append('\n');
        r.append("CHATGPT_GUM_LAST_ERROR=").append(lastGumError).append('\n');
        r.append("TRACK_EVENTS=").append(trackEvents).append('\n');
        r.append("RTC_AUDIO_EVENTS=").append(rtcAudioEvents).append('\n');
        r.append("WEB_PERMISSIONS_API_MIC_STATE=").append(permissionsApi).append('\n');
        r.append("WEB_ENUMERATE_DEVICES=").append(deviceCensus).append('\n');
        r.append("V11_WEB_PERMISSION_STATUS=").append(parentString("audioPermissionStatus")).append('\n');
        r.append("V11_WEB_PERMISSION_ORIGIN=").append(parentString("audioPermissionOrigin")).append('\n');
        r.append("V11_WEB_PERMISSION_REQUEST_COUNT=").append(parentString("audioPermissionRequestCount")).append('\n');
        r.append("DIRECT_GUM_SELFTEST_USED=false\n");
        r.append("RAW_AUDIO_RETAINED=false\n");
        r.append("RAW_CHAT_TEXT_RETAINED=false\n");
        r.append("DEVICE_IDS_RETAINED=false\n");
        r.append("DEVICE_LABELS_RETAINED=false\n");
        r.append("CHATGPT_COOKIES_EXTRACTED=false\n");
        r.append("--- V13 EVENT LOG ---\n").append(events13);
        Object x = parentObject("events");
        if (x instanceof StringBuilder) r.append("--- V11 EVENT LOG ---\n").append(x.toString());
        return r.toString();
    }

    private Object parentObject(String name) {
        try {
            Field f = AudioModelSuiteV11Activity.class.getDeclaredField(name);
            f.setAccessible(true);
            return f.get(this);
        } catch (Exception e) { return null; }
    }

    private String parentString(String name) {
        Object x = parentObject(name);
        return x == null ? "-" : tok(String.valueOf(x));
    }

    private String appOpsMode(int mode) {
        if (mode == AppOpsManager.MODE_ALLOWED) return "ALLOWED";
        if (mode == AppOpsManager.MODE_IGNORED) return "IGNORED";
        if (mode == AppOpsManager.MODE_ERRORED) return "ERRORED";
        if (mode == AppOpsManager.MODE_DEFAULT) return "DEFAULT";
        if (mode == AppOpsManager.MODE_FOREGROUND) return "FOREGROUND";
        return "MODE_" + mode;
    }

    private boolean trustedOrigin(Uri u) {
        return u != null && "https".equalsIgnoreCase(u.getScheme())
                && "chatgpt.com".equalsIgnoreCase(u.getHost());
    }

    private boolean trustedUrl(String raw) {
        try {
            URI u = URI.create(raw == null ? "" : raw);
            return "https".equalsIgnoreCase(u.getScheme())
                    && "chatgpt.com".equalsIgnoreCase(u.getHost());
        } catch (Exception e) { return false; }
    }

    private static String sanitizeUrl(String raw) {
        try {
            URI u = URI.create(raw == null ? "" : raw);
            String scheme = u.getScheme() == null ? "" : u.getScheme();
            String host = u.getHost() == null ? "" : u.getHost();
            String path = u.getPath() == null ? "" : u.getPath();
            if (scheme.isEmpty() || host.isEmpty()) return "-";
            return scheme + "://" + host + path;
        } catch (Exception e) { return "-"; }
    }

    private void ev(String s) {
        if (events13.length() < 26000) events13.append(stamp()).append(" | ").append(tok(s)).append('\n');
    }

    private static String stamp() {
        return new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date());
    }

    private static String tok(String s) {
        String x = s == null ? "-" : s.replaceAll("[^A-Za-z0-9_.:+/@=-]", "_");
        return x.length() > 180 ? x.substring(0, 180) : x;
    }

    private static String safeEventData(JSONObject d) {
        if (d == null) return "-";
        StringBuilder s = new StringBuilder();
        String[] keys = {"secure","media","ok","audio","video","audioTracks","state","muted","name","total","audioIn","labels","kind"};
        for (String k : keys) {
            if (!d.has(k)) continue;
            if (s.length() > 0) s.append(' ');
            s.append(k).append('=').append(tok(String.valueOf(d.opt(k))));
        }
        return s.length() == 0 ? "-" : s.toString();
    }

    private int dp(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }

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
        h.removeCallbacksAndMessages(null);
        try { if (documentStartHandler != null) documentStartHandler.remove(); } catch (Exception ignored) { }
        super.onDestroy();
    }

    private static final String EARLY_JS =
            "(function(){try{if(window.__cp13Installed)return;window.__cp13Installed=true;"
            + "const C=x=>String(x||'').replace(/[^A-Za-z0-9_.:+/-]/g,'_').slice(0,80);"
            + "const S=(t,d)=>{try{cp13bridge.postMessage(JSON.stringify({t:t,d:d||{}}));}catch(_){}};"
            + "S('DOC_START',{secure:!!window.isSecureContext,media:!!navigator.mediaDevices});"
            + "try{const P=(typeof MediaDevices!=='undefined')?MediaDevices.prototype:null;const O=P&&P.getUserMedia;"
            + "if(O&&!O.__cp13){const W=function(c){S('GUM_CALL',{audio:!!(c&&c.audio),video:!!(c&&c.video)});let q;"
            + "try{q=Reflect.apply(O,this,[c]);}catch(x){S('GUM_THROW',{name:C(x&&x.name)});throw x;}"
            + "return Promise.resolve(q).then(s=>{const a=s&&s.getAudioTracks?s.getAudioTracks():[];"
            + "S('GUM_OK',{audioTracks:a.length,state:a[0]?C(a[0].readyState):'-',muted:a[0]?!!a[0].muted:false});"
            + "a.forEach(t=>{try{t.addEventListener('mute',()=>S('TRACK_MUTE',{state:C(t.readyState)}));"
            + "t.addEventListener('unmute',()=>S('TRACK_UNMUTE',{state:C(t.readyState)}));"
            + "t.addEventListener('ended',()=>S('TRACK_ENDED',{state:C(t.readyState)}));}catch(_){}});return s;},"
            + "x=>{S('GUM_FAIL',{name:C(x&&x.name)});throw x;});};"
            + "try{Object.defineProperty(W,'__cp13',{value:true});}catch(_){};try{P.getUserMedia=W;}catch(_){};"
            + "S('GUM_WRAP',{ok:P.getUserMedia===W});}else S('GUM_WRAP',{ok:false});}catch(x){S('GUM_WRAP_FAIL',{name:C(x&&x.name)});}"
            + "try{const R=(typeof RTCPeerConnection!=='undefined')?RTCPeerConnection.prototype:null;"
            + "if(R&&R.addTrack&&!R.addTrack.__cp13){const A=R.addTrack;const W=function(t){if(t&&t.kind==='audio')S('RTC_AUDIO',{kind:'addTrack'});return Reflect.apply(A,this,arguments);};"
            + "try{Object.defineProperty(W,'__cp13',{value:true});}catch(_){};R.addTrack=W;}"
            + "if(R&&R.addTransceiver&&!R.addTransceiver.__cp13){const A=R.addTransceiver;const W=function(x){if((x&&x.kind==='audio')||x==='audio')S('RTC_AUDIO',{kind:'addTransceiver'});return Reflect.apply(A,this,arguments);};"
            + "try{Object.defineProperty(W,'__cp13',{value:true});}catch(_){};R.addTransceiver=W;}}catch(_){}"
            + "}catch(_){} })();";

    private static final String EARLY_JS_FALLBACK = EARLY_JS;

    private static final String READ_ONLY_JS =
            "(function(){const C=x=>String(x||'').replace(/[^A-Za-z0-9_.:+/-]/g,'_').slice(0,80);"
            + "const S=(t,d)=>{try{cp13bridge.postMessage(JSON.stringify({t:t,d:d||{}}));}catch(_){}};"
            + "const T=(p,ms)=>Promise.race([p,new Promise((_,j)=>setTimeout(()=>j({__timeout:true}),ms))]);"
            + "if(navigator.permissions&&navigator.permissions.query){T(navigator.permissions.query({name:'microphone'}),1800).then(p=>S('PERM',{state:C(p&&p.state)}),x=>{if(x&&x.__timeout)S('PERM_TIMEOUT',{});else S('PERM_ERROR',{name:C(x&&x.name)});});}else S('PERM_ERROR',{name:'UNSUPPORTED'});"
            + "if(navigator.mediaDevices&&navigator.mediaDevices.enumerateDevices){T(navigator.mediaDevices.enumerateDevices(),1800).then(a=>{let ai=0,l=0;(a||[]).forEach(x=>{if(x.kind==='audioinput')ai++;if(x.label)l++;});S('ENUM',{total:(a||[]).length,audioIn:ai,labels:l});},x=>{if(x&&x.__timeout)S('ENUM_TIMEOUT',{});else S('ENUM_ERROR',{name:C(x&&x.name)});});}else S('ENUM_ERROR',{name:'UNSUPPORTED'});"
            + "return 'DISPATCHED';})();";
}
