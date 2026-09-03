package com.homayounisaghar.chatgptwebviewprobe;

import android.Manifest;
import android.app.AppOpsManager;
import android.content.ContentValues;
import android.content.pm.PackageManager;
import android.hardware.SensorPrivacyManager;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.net.Uri;
import android.os.Build;
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

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.OutputStream;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * Stable v0.12 layered microphone diagnostic.
 *
 * It deliberately separates four questions that v0.11 could not distinguish:
 * 1) Android runtime/AppOps/global microphone privacy state.
 * 2) Native AudioRecord capture from this app process.
 * 3) Web Permissions API state for microphone on https://chatgpt.com.
 * 4) A real same-origin navigator.mediaDevices.getUserMedia({audio:true}) self-test.
 *
 * The JavaScript probe stores only API/result metadata. It never retains PCM,
 * speech, chat text, device identifiers, device labels, cookies, or tokens.
 */
public class AudioCaptureDiagV12Activity extends AudioModelSuiteV11FinalActivity {
    private static final int REQ_V12_AUDIO = 1201;
    private static final long DIAG_MAX_MS = 10L * 60L * 1000L;

    private final Handler diagHandler = new Handler(Looper.getMainLooper());
    private final StringBuilder diagEvents = new StringBuilder();

    private WebView diagWeb;
    private TextView diagStatusView;
    private Button diagButton;

    private boolean diagActive = false;
    private long diagStartedAt = 0L;
    private long lastEnsureProbeAt = 0L;

    private String androidPermission = "NOT_CHECKED";
    private String appOpsRecordAudio = "NOT_CHECKED";
    private String globalMicPrivacy = "NOT_CHECKED";
    private String audioManagerMicMute = "NOT_CHECKED";
    private String nativeMicSelftest = "NOT_RUN";
    private String jsProbeStatus = "NOT_RUN";
    private String permissionsApiMic = "NOT_RUN";
    private String enumerateDevicesSummary = "NOT_RUN";
    private String directGumSelftest = "NOT_RUN";
    private String lastGumError = "-";
    private int gumCalls = 0;
    private int gumResolves = 0;
    private int gumRejects = 0;
    private int trackEvents = 0;
    private int drainedJsEvents = 0;

    private final Runnable diagPoller = new Runnable() {
        @Override public void run() {
            if (!diagActive || diagWeb == null) return;
            if (System.currentTimeMillis() - diagStartedAt > DIAG_MAX_MS) {
                diagActive = false;
                localEvent("DIAG_AUTO_STOP_LEASE_EXPIRED");
                renderDiag();
                return;
            }
            long now = System.currentTimeMillis();
            if (now - lastEnsureProbeAt > 500L) {
                lastEnsureProbeAt = now;
                installProbe(false, null);
            }
            drainJsEvents();
            renderDiag();
            diagHandler.postDelayed(this, 140L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        diagWeb = findWebViewV12(getWindow().getDecorView());
        if (diagWeb == null) return;
        diagWeb.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        installDiagPanel();
        localEvent("V12_READY");
        renderDiag();
    }

    private void installDiagPanel() {
        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) content;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        int webIndex = root.indexOfChild(diagWeb);
        if (webIndex < 0) webIndex = root.getChildCount();

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);

        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        diagButton = new Button(this);
        diagButton.setText("AUDIO DIAG12");
        diagButton.setTextSize(8.6f);
        diagButton.setOnClickListener(v -> startDiagRequested());
        row.addView(diagButton, new LinearLayout.LayoutParams(0, dp12(39), 1f));

        Button report = new Button(this);
        report.setText("REPORT12");
        report.setTextSize(8.6f);
        report.setOnClickListener(v -> downloadReport12());
        row.addView(report, new LinearLayout.LayoutParams(0, dp12(39), 1f));
        panel.addView(row, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp12(39)));

        diagStatusView = new TextView(this);
        diagStatusView.setTextSize(8.8f);
        diagStatusView.setTextIsSelectable(true);
        diagStatusView.setPadding(dp12(7), dp12(2), dp12(7), dp12(2));
        ScrollView sv = new ScrollView(this);
        sv.addView(diagStatusView, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));
        panel.addView(sv, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp12(58)));

        root.addView(panel, webIndex, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void startDiagRequested() {
        if (diagWeb == null || !isTrusted12(diagWeb.getUrl())) {
            jsProbeStatus = "FAIL_NOT_TRUSTED_CHATGPT_ORIGIN";
            renderDiag();
            return;
        }
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            androidPermission = "WAITING_RUNTIME_PERMISSION";
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQ_V12_AUDIO);
            renderDiag();
            return;
        }
        beginDiag();
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != REQ_V12_AUDIO) return;
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            beginDiag();
        } else {
            androidPermission = "DENIED";
            jsProbeStatus = "BLOCKED_ANDROID_PERMISSION_DENIED";
            localEvent("ANDROID_RECORD_AUDIO_DENIED");
            renderDiag();
        }
    }

    private void beginDiag() {
        diagHandler.removeCallbacksAndMessages(null);
        diagEvents.setLength(0);
        diagActive = true;
        diagStartedAt = System.currentTimeMillis();
        lastEnsureProbeAt = 0L;
        nativeMicSelftest = "RUNNING";
        jsProbeStatus = "WAITING_NATIVE_SELFTEST";
        permissionsApiMic = "NOT_RUN";
        enumerateDevicesSummary = "NOT_RUN";
        directGumSelftest = "NOT_RUN";
        lastGumError = "-";
        gumCalls = gumResolves = gumRejects = trackEvents = drainedJsEvents = 0;
        snapshotAndroidMicState();
        invokeV11StartAudioWatch();
        localEvent("DIAG_STARTED");
        renderDiag();

        new Thread(() -> {
            String result = runNativeMicSelftest();
            runOnUiThread(() -> {
                nativeMicSelftest = result;
                localEvent("NATIVE_MIC_SELFTEST " + safeToken12(result));
                jsProbeStatus = "INSTALLING";
                installProbe(true, () -> {
                    jsProbeStatus = "INSTALLED_SELFTEST_RUNNING";
                    runWebBaselineAndSelftest();
                    diagHandler.post(diagPoller);
                    renderDiag();
                });
            });
        }, "v12-native-mic-selftest").start();
    }

    private void snapshotAndroidMicState() {
        androidPermission = checkSelfPermission(Manifest.permission.RECORD_AUDIO)
                == PackageManager.PERMISSION_GRANTED ? "GRANTED" : "DENIED";
        try {
            AppOpsManager a = (AppOpsManager) getSystemService(APP_OPS_SERVICE);
            int mode = a.unsafeCheckOpNoThrow(AppOpsManager.OPSTR_RECORD_AUDIO,
                    Process.myUid(), getPackageName());
            appOpsRecordAudio = appOpsMode(mode);
        } catch (Exception e) {
            appOpsRecordAudio = "ERROR_" + e.getClass().getSimpleName();
        }
        try {
            AudioManager am = (AudioManager) getSystemService(AUDIO_SERVICE);
            audioManagerMicMute = am != null && am.isMicrophoneMute() ? "MUTED" : "NOT_MUTED";
        } catch (Exception e) {
            audioManagerMicMute = "ERROR_" + e.getClass().getSimpleName();
        }
        if (Build.VERSION.SDK_INT >= 31) {
            try {
                SensorPrivacyManager spm = getSystemService(SensorPrivacyManager.class);
                if (spm == null) globalMicPrivacy = "UNAVAILABLE";
                else if (!spm.supportsSensorToggle(SensorPrivacyManager.Sensors.MICROPHONE)) {
                    globalMicPrivacy = "TOGGLE_UNSUPPORTED";
                } else {
                    globalMicPrivacy = spm.isSensorPrivacyEnabled(SensorPrivacyManager.Sensors.MICROPHONE)
                            ? "PRIVACY_ON_BLOCKING" : "PRIVACY_OFF";
                }
            } catch (Exception e) {
                globalMicPrivacy = "ERROR_" + e.getClass().getSimpleName();
            }
        } else {
            globalMicPrivacy = "API_LT_31";
        }
    }

    private String runNativeMicSelftest() {
        AudioRecord ar = null;
        try {
            int sr = 16000;
            int min = AudioRecord.getMinBufferSize(sr, AudioFormat.CHANNEL_IN_MONO,
                    AudioFormat.ENCODING_PCM_16BIT);
            if (min <= 0) return "FAIL_MIN_BUFFER_" + min;
            int size = Math.max(min * 2, 4096);
            ar = new AudioRecord(MediaRecorder.AudioSource.MIC, sr,
                    AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT, size);
            if (ar.getState() != AudioRecord.STATE_INITIALIZED) return "FAIL_NOT_INITIALIZED";
            ar.startRecording();
            short[] buf = new short[800];
            int frames = 0;
            long nonZero = 0;
            long deadline = System.currentTimeMillis() + 450L;
            while (System.currentTimeMillis() < deadline) {
                int n = ar.read(buf, 0, buf.length, AudioRecord.READ_BLOCKING);
                if (n < 0) return "FAIL_READ_" + n;
                frames += n;
                for (int i = 0; i < n; i++) if (buf[i] != 0) nonZero++;
                if (frames >= 3200) break;
            }
            return frames > 0 ? "PASS frames=" + frames + " nonzero=" + (nonZero > 0) : "FAIL_NO_FRAMES";
        } catch (SecurityException e) {
            return "FAIL_SECURITY_EXCEPTION";
        } catch (Exception e) {
            return "FAIL_" + e.getClass().getSimpleName();
        } finally {
            if (ar != null) {
                try { if (ar.getRecordingState() == AudioRecord.RECORDSTATE_RECORDING) ar.stop(); } catch (Exception ignored) { }
                try { ar.release(); } catch (Exception ignored) { }
            }
        }
    }

    private void invokeV11StartAudioWatch() {
        try {
            Method m = AudioModelSuiteV11Activity.class.getDeclaredMethod("startAudioWatch");
            m.setAccessible(true);
            m.invoke(this);
            localEvent("V11_AUDIO_WATCH_ARMED_BY_V12");
        } catch (Exception e) {
            localEvent("V11_AUDIO_WATCH_ARM_FAIL_" + e.getClass().getSimpleName());
        }
    }

    private void installProbe(boolean reportResult, Runnable after) {
        if (diagWeb == null || !isTrusted12(diagWeb.getUrl())) {
            if (reportResult) jsProbeStatus = "FAIL_NOT_TRUSTED_ORIGIN";
            if (after != null) after.run();
            return;
        }
        diagWeb.evaluateJavascript(INSTALL_JS, value -> {
            if (reportResult) {
                String x = jsString(value);
                jsProbeStatus = x.isEmpty() ? "INSTALLED" : safeToken12(x);
                localEvent("JS_PROBE_INSTALL " + safeToken12(jsProbeStatus));
            }
            if (after != null) after.run();
        });
    }

    private void runWebBaselineAndSelftest() {
        if (diagWeb == null) return;
        directGumSelftest = "RUNNING";
        diagWeb.evaluateJavascript(SELFTEST_JS, value -> {
            localEvent("WEB_SELFTEST_SCRIPT_DISPATCHED");
            renderDiag();
        });
    }

    private void drainJsEvents() {
        if (diagWeb == null || !isTrusted12(diagWeb.getUrl())) return;
        diagWeb.evaluateJavascript(DRAIN_JS, value -> {
            try {
                String raw = jsString(value);
                if (raw.isEmpty()) return;
                JSONObject root = new JSONObject(raw);
                JSONArray arr = root.optJSONArray("events");
                if (arr == null) return;
                for (int i = 0; i < arr.length(); i++) {
                    JSONObject e = arr.optJSONObject(i);
                    if (e == null) continue;
                    consumeJsEvent(e);
                }
            } catch (Exception ignored) { }
        });
    }

    private void consumeJsEvent(JSONObject e) {
        String type = safeToken12(e.optString("type", "UNKNOWN"));
        JSONObject d = e.optJSONObject("data");
        if (d == null) d = new JSONObject();
        drainedJsEvents++;
        switch (type) {
            case "PERM_QUERY_RESOLVE":
            case "PERM_BASELINE":
            case "PERM_POST_GUM":
                permissionsApiMic = safeToken12(d.optString("state", "UNKNOWN"));
                break;
            case "ENUM_RESOLVE":
            case "ENUM_BASELINE":
            case "ENUM_POST_GUM":
                enumerateDevicesSummary = "total=" + d.optInt("total", -1)
                        + " audioIn=" + d.optInt("audioinput", -1)
                        + " labels=" + d.optInt("labelsPresent", -1);
                break;
            case "GUM_CALL": gumCalls++; break;
            case "GUM_RESOLVE": gumResolves++; break;
            case "GUM_REJECT":
                gumRejects++;
                lastGumError = safeToken12(d.optString("name", "UNKNOWN")) + ":"
                        + safeToken12(d.optString("message", ""));
                break;
            case "TRACK_MUTE":
            case "TRACK_UNMUTE":
            case "TRACK_ENDED": trackEvents++; break;
            case "SELFTEST_OK": directGumSelftest = "PASS"; break;
            case "SELFTEST_FAIL":
                directGumSelftest = "FAIL_" + safeToken12(d.optString("name", "UNKNOWN"));
                lastGumError = safeToken12(d.optString("name", "UNKNOWN")) + ":"
                        + safeToken12(d.optString("message", ""));
                break;
            default: break;
        }
        if (diagEvents.length() < 24000) {
            diagEvents.append(new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date()))
                    .append(" | JS_").append(type)
                    .append(" | ").append(safeJsonSummary(d)).append('\n');
        }
    }

    private void localEvent(String s) {
        if (diagEvents.length() < 24000) {
            diagEvents.append(new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date()))
                    .append(" | ").append(safeToken12(s)).append('\n');
        }
    }

    private void renderDiag() {
        if (diagStatusView == null) return;
        StringBuilder s = new StringBuilder();
        s.append("v0.12 AUDIO CAPTURE DIAG  active=").append(diagActive).append('\n');
        s.append("Android=").append(androidPermission)
                .append(" AppOps=").append(appOpsRecordAudio)
                .append(" Privacy=").append(globalMicPrivacy)
                .append(" Mute=").append(audioManagerMicMute).append('\n');
        s.append("NativeMic=").append(nativeMicSelftest)
                .append("  DirectGUM=").append(directGumSelftest).append('\n');
        s.append("PermissionsAPI=").append(permissionsApiMic)
                .append("  Devices=").append(enumerateDevicesSummary).append('\n');
        s.append("GUM calls/resolves/rejects=").append(gumCalls).append('/')
                .append(gumResolves).append('/').append(gumRejects)
                .append(" lastErr=").append(lastGumError);
        diagStatusView.setText(s.toString());
        if (diagButton != null) diagButton.setText(diagActive ? "DIAG ACTIVE" : "AUDIO DIAG12");
    }

    private void downloadReport12() {
        drainJsEvents();
        diagHandler.postDelayed(() -> {
            try {
                String report = buildReport12();
                String stamp = new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date());
                String name = "chatgpt-webview-v12-audio-capture-report-" + stamp + ".txt";
                ContentValues cv = new ContentValues();
                cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
                cv.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
                cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
                Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
                if (u == null) throw new IllegalStateException("insert null");
                try (OutputStream out = getContentResolver().openOutputStream(u)) {
                    if (out == null) throw new IllegalStateException("stream null");
                    out.write(report.getBytes(StandardCharsets.UTF_8));
                }
                Toast.makeText(this, "v0.12 report saved to Downloads", Toast.LENGTH_LONG).show();
            } catch (Exception e) {
                Toast.makeText(this, "Report failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
            }
        }, 260L);
    }

    private String buildReport12() {
        StringBuilder r = new StringBuilder();
        r.append("CHATGPT_WEBVIEW_STABLE_V12_AUDIO_CAPTURE_DIAGNOSTIC\n");
        r.append("CURRENT_URL=").append(sanitizeUrl12(diagWeb == null ? "-" : diagWeb.getUrl())).append('\n');
        r.append("ANDROID_RECORD_AUDIO_PERMISSION=").append(androidPermission).append('\n');
        r.append("ANDROID_RECORD_AUDIO_APPOPS=").append(appOpsRecordAudio).append('\n');
        r.append("ANDROID_GLOBAL_MIC_PRIVACY=").append(globalMicPrivacy).append('\n');
        r.append("ANDROID_AUDIO_MANAGER_MIC_MUTE=").append(audioManagerMicMute).append('\n');
        r.append("NATIVE_AUDIORECORD_SELFTEST=").append(nativeMicSelftest).append('\n');
        r.append("JS_PROBE_STATUS=").append(jsProbeStatus).append('\n');
        r.append("WEB_PERMISSIONS_API_MIC_STATE=").append(permissionsApiMic).append('\n');
        r.append("WEB_ENUMERATE_DEVICES=").append(enumerateDevicesSummary).append('\n');
        r.append("WEB_DIRECT_GUM_SELFTEST=").append(directGumSelftest).append('\n');
        r.append("WEB_GUM_CALLS=").append(gumCalls).append('\n');
        r.append("WEB_GUM_RESOLVES=").append(gumResolves).append('\n');
        r.append("WEB_GUM_REJECTS=").append(gumRejects).append('\n');
        r.append("WEB_GUM_LAST_ERROR=").append(lastGumError).append('\n');
        r.append("WEB_TRACK_EVENTS=").append(trackEvents).append('\n');
        r.append("V11_WEB_PERMISSION_STATUS=").append(v11Field("audioPermissionStatus", "-")).append('\n');
        r.append("V11_WEB_PERMISSION_ORIGIN=").append(v11Field("audioPermissionOrigin", "-")).append('\n');
        r.append("V11_WEB_PERMISSION_REQUEST_COUNT=").append(v11Field("audioPermissionRequestCount", "-")).append('\n');
        r.append("V11_AUDIO_STATE=").append(v11Field("audioState", "-")).append('\n');
        r.append("RAW_AUDIO_RETAINED=false\n");
        r.append("RAW_CHAT_TEXT_RETAINED=false\n");
        r.append("DEVICE_IDS_RETAINED=false\n");
        r.append("DEVICE_LABELS_RETAINED=false\n");
        r.append("CHATGPT_COOKIES_EXTRACTED=false\n");
        r.append("--- V12 EVENT LOG ---\n").append(diagEvents);
        Object ev = v11FieldObject("events");
        if (ev instanceof StringBuilder) {
            r.append("--- V11 EVENT LOG ---\n").append(ev.toString());
        }
        return r.toString();
    }

    private Object v11FieldObject(String name) {
        try {
            Field f = AudioModelSuiteV11Activity.class.getDeclaredField(name);
            f.setAccessible(true);
            return f.get(this);
        } catch (Exception e) { return null; }
    }

    private String v11Field(String name, String fallback) {
        Object x = v11FieldObject(name);
        return x == null ? fallback : safeToken12(String.valueOf(x));
    }

    private static String appOpsMode(int mode) {
        if (mode == AppOpsManager.MODE_ALLOWED) return "ALLOWED";
        if (mode == AppOpsManager.MODE_IGNORED) return "IGNORED";
        if (mode == AppOpsManager.MODE_ERRORED) return "ERRORED";
        if (mode == AppOpsManager.MODE_DEFAULT) return "DEFAULT";
        if (Build.VERSION.SDK_INT >= 29 && mode == AppOpsManager.MODE_FOREGROUND) return "FOREGROUND";
        return "MODE_" + mode;
    }

    private static String jsString(String value) {
        if (value == null || "null".equals(value)) return "";
        try {
            Object x = new JSONTokener(value).nextValue();
            return x instanceof String ? (String) x : String.valueOf(x);
        } catch (Exception e) { return value; }
    }

    private static String safeJsonSummary(JSONObject d) {
        String x = d == null ? "{}" : d.toString();
        x = x.replaceAll("[^A-Za-z0-9_{}\\[\\]\\\":.,+/-]", "_");
        return x.length() > 420 ? x.substring(0, 420) : x;
    }

    private static String safeToken12(String s) {
        String x = s == null ? "-" : s.replaceAll("[^A-Za-z0-9_.:+/=-]", "_");
        return x.length() > 180 ? x.substring(0, 180) : x;
    }

    private static boolean isTrusted12(String raw) {
        try {
            URI u = URI.create(raw == null ? "" : raw);
            return "https".equalsIgnoreCase(u.getScheme()) && "chatgpt.com".equalsIgnoreCase(u.getHost());
        } catch (Exception e) { return false; }
    }

    private static String sanitizeUrl12(String raw) {
        try {
            URI u = URI.create(raw == null ? "" : raw);
            if (u.getScheme() == null || u.getHost() == null) return "-";
            return u.getScheme() + "://" + u.getHost() + (u.getPath() == null ? "" : u.getPath());
        } catch (Exception e) { return "-"; }
    }

    private int dp12(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    private WebView findWebViewV12(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (!(v instanceof ViewGroup)) return null;
        ViewGroup g = (ViewGroup) v;
        for (int i = 0; i < g.getChildCount(); i++) {
            WebView w = findWebViewV12(g.getChildAt(i));
            if (w != null) return w;
        }
        return null;
    }

    @Override protected void onDestroy() {
        diagActive = false;
        diagHandler.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private static final String INSTALL_JS =
            "(function(){try{"
            + "if(window.__cpAudioDiag12&&window.__cpAudioDiag12.installed)return 'ALREADY_INSTALLED';"
            + "const D={installed:true,events:[],seq:0};"
            + "D.clean=x=>String(x||'').replace(/[^A-Za-z0-9_.:+/ -]/g,'_').slice(0,140);"
            + "D.push=(type,data)=>{try{D.events.push({seq:++D.seq,t:performance.now(),type:type,data:data||{}});if(D.events.length>120)D.events.shift();}catch(_){}};"
            + "D.sumConstraints=c=>{const a=c&&c.audio;let keys=[];if(a&&typeof a==='object')keys=Object.keys(a).filter(k=>['echoCancellation','noiseSuppression','autoGainControl','sampleRate','channelCount','deviceId'].includes(k));return{audio:!!a,video:!!(c&&c.video),audioKeys:keys.join(','),deviceIdConstraint:keys.includes('deviceId')};};"
            + "D.sumDevices=arr=>{let ai=0,ao=0,vi=0,lab=0;(arr||[]).forEach(x=>{if(x.kind==='audioinput')ai++;else if(x.kind==='audiooutput')ao++;else if(x.kind==='videoinput')vi++;if(x.label)lab++;});return{total:(arr||[]).length,audioinput:ai,audiooutput:ao,videoinput:vi,labelsPresent:lab};};"
            + "D.track=t=>({kind:D.clean(t&&t.kind),readyState:D.clean(t&&t.readyState),enabled:!!(t&&t.enabled),muted:!!(t&&t.muted)});"
            + "D.push('ENV',{secure:!!window.isSecureContext,visibility:D.clean(document.visibilityState),hasMediaDevices:!!navigator.mediaDevices,hasPermissions:!!navigator.permissions});"
            + "const md=navigator.mediaDevices;"
            + "if(md&&md.getUserMedia){try{const orig=md.getUserMedia.bind(md);md.getUserMedia=function(c){D.push('GUM_CALL',D.sumConstraints(c));let p;try{p=orig(c);}catch(e){D.push('GUM_REJECT',{name:D.clean(e&&e.name),message:D.clean(e&&e.message),sync:true});throw e;}return Promise.resolve(p).then(s=>{const ts=s&&s.getAudioTracks?s.getAudioTracks():[];D.push('GUM_RESOLVE',{audioTracks:ts.length,tracks:ts.map(D.track)});ts.forEach((t,i)=>{try{t.addEventListener('mute',()=>D.push('TRACK_MUTE',{i:i,state:D.clean(t.readyState)}));t.addEventListener('unmute',()=>D.push('TRACK_UNMUTE',{i:i,state:D.clean(t.readyState)}));t.addEventListener('ended',()=>D.push('TRACK_ENDED',{i:i,state:D.clean(t.readyState)}));}catch(_){}});return s;},e=>{D.push('GUM_REJECT',{name:D.clean(e&&e.name),message:D.clean(e&&e.message),sync:false});throw e;});};}catch(e){D.push('PATCH_GUM_FAIL',{name:D.clean(e&&e.name)});}}"
            + "if(md&&md.enumerateDevices){try{const origE=md.enumerateDevices.bind(md);md.enumerateDevices=function(){D.push('ENUM_CALL',{});return Promise.resolve(origE()).then(a=>{D.push('ENUM_RESOLVE',D.sumDevices(a));return a;},e=>{D.push('ENUM_REJECT',{name:D.clean(e&&e.name),message:D.clean(e&&e.message)});throw e;});};}catch(e){D.push('PATCH_ENUM_FAIL',{name:D.clean(e&&e.name)});}}"
            + "if(navigator.permissions&&navigator.permissions.query){try{const origP=navigator.permissions.query.bind(navigator.permissions);navigator.permissions.query=function(desc){const n=desc&&desc.name?String(desc.name):'';if(n==='microphone')D.push('PERM_QUERY_CALL',{name:'microphone'});let p;try{p=origP(desc);}catch(e){if(n==='microphone')D.push('PERM_QUERY_REJECT',{name:D.clean(e&&e.name),message:D.clean(e&&e.message),sync:true});throw e;}return Promise.resolve(p).then(r=>{if(n==='microphone'){D.push('PERM_QUERY_RESOLVE',{state:D.clean(r&&r.state)});try{r.addEventListener('change',()=>D.push('PERM_QUERY_CHANGE',{state:D.clean(r.state)}));}catch(_){}}return r;},e=>{if(n==='microphone')D.push('PERM_QUERY_REJECT',{name:D.clean(e&&e.name),message:D.clean(e&&e.message),sync:false});throw e;});};}catch(e){D.push('PATCH_PERM_FAIL',{name:D.clean(e&&e.name)});}}"
            + "D.push('PROBE_INSTALLED',{});return 'INSTALLED';}catch(e){return 'INSTALL_FAIL_'+String(e&&e.name||'Error');}})()";

    private static final String SELFTEST_JS =
            "(async function(){const D=window.__cpAudioDiag12;if(!D)return 'NO_PROBE';"
            + "try{if(navigator.permissions&&navigator.permissions.query){try{const p=await navigator.permissions.query({name:'microphone'});D.push('PERM_BASELINE',{state:D.clean(p&&p.state)});}catch(e){D.push('PERM_BASELINE_FAIL',{name:D.clean(e&&e.name),message:D.clean(e&&e.message)});}}"
            + "if(navigator.mediaDevices&&navigator.mediaDevices.enumerateDevices){try{const a=await navigator.mediaDevices.enumerateDevices();D.push('ENUM_BASELINE',D.sumDevices(a));}catch(e){D.push('ENUM_BASELINE_FAIL',{name:D.clean(e&&e.name)});}}"
            + "D.push('SELFTEST_BEGIN',{});"
            + "try{const s=await navigator.mediaDevices.getUserMedia({audio:true,video:false});const ts=s.getAudioTracks();D.push('SELFTEST_OK',{audioTracks:ts.length,tracks:ts.map(D.track)});await new Promise(r=>setTimeout(r,650));ts.forEach(t=>{try{t.stop();}catch(_){}});D.push('SELFTEST_STOP',{audioTracks:ts.length});}catch(e){D.push('SELFTEST_FAIL',{name:D.clean(e&&e.name),message:D.clean(e&&e.message)});}"
            + "if(navigator.permissions&&navigator.permissions.query){try{const p2=await navigator.permissions.query({name:'microphone'});D.push('PERM_POST_GUM',{state:D.clean(p2&&p2.state)});}catch(e){D.push('PERM_POST_GUM_FAIL',{name:D.clean(e&&e.name)});}}"
            + "if(navigator.mediaDevices&&navigator.mediaDevices.enumerateDevices){try{const b=await navigator.mediaDevices.enumerateDevices();D.push('ENUM_POST_GUM',D.sumDevices(b));}catch(e){D.push('ENUM_POST_GUM_FAIL',{name:D.clean(e&&e.name)});}}"
            + "return 'DONE';}catch(e){D.push('SELFTEST_SCRIPT_FAIL',{name:D.clean(e&&e.name),message:D.clean(e&&e.message)});return 'FAIL';}})()";

    private static final String DRAIN_JS =
            "(function(){try{const D=window.__cpAudioDiag12;if(!D)return JSON.stringify({ok:false,events:[]});const a=D.events.splice(0,D.events.length);return JSON.stringify({ok:true,events:a});}catch(e){return JSON.stringify({ok:false,events:[]});}})()";
}
