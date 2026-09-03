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

/** Stable v0.12 layered microphone diagnostic.
 *
 * Separates Android process capture from Web getUserMedia. No PCM, speech,
 * chat text, device ids/labels, cookies or tokens are retained.
 */
public class AudioCaptureDiagV12Activity extends AudioModelSuiteV11FinalActivity {
    private static final int REQ_V12_AUDIO = 1201;
    private static final long LEASE_MS = 10L * 60L * 1000L;

    private final Handler h = new Handler(Looper.getMainLooper());
    private final StringBuilder events12 = new StringBuilder();
    private WebView w;
    private TextView status12;
    private Button diagButton;
    private boolean active = false;
    private long startedAt = 0L;
    private long lastEnsure = 0L;

    private String androidPermission = "NOT_CHECKED";
    private String appOps = "NOT_CHECKED";
    private String audioManagerMute = "NOT_CHECKED";
    private String micToggleSupport = "NOT_CHECKED";
    private String nativeMic = "NOT_RUN";
    private String probeInstall = "NOT_RUN";
    private String permissionApi = "NOT_RUN";
    private String deviceCensus = "NOT_RUN";
    private String directGum = "NOT_RUN";
    private String lastGumError = "-";
    private int gumCalls = 0;
    private int gumResolves = 0;
    private int gumRejects = 0;
    private int trackEvents = 0;

    private final Runnable poller = new Runnable() {
        @Override public void run() {
            if (!active || w == null) return;
            if (System.currentTimeMillis() - startedAt > LEASE_MS) {
                active = false;
                ev("DIAG_AUTO_STOP_LEASE_EXPIRED");
                render12();
                return;
            }
            long now = System.currentTimeMillis();
            if (now - lastEnsure > 500L && trusted(w.getUrl())) {
                lastEnsure = now;
                installProbe(false, null);
            }
            drain();
            render12();
            h.postDelayed(this, 140L);
        }
    };

    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        w = findWeb(getWindow().getDecorView());
        if (w == null) return;
        w.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        addPanel();
        ev("V12_READY");
        render12();
    }

    private void addPanel() {
        View c = findViewById(android.R.id.content);
        if (!(c instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) c;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        int wi = root.indexOfChild(w);
        if (wi < 0) wi = root.getChildCount();

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);

        diagButton = new Button(this);
        diagButton.setText("AUDIO DIAG12");
        diagButton.setTextSize(8.5f);
        diagButton.setOnClickListener(v -> startRequested());
        row.addView(diagButton, new LinearLayout.LayoutParams(0, dp(39), 1f));

        Button report = new Button(this);
        report.setText("REPORT12");
        report.setTextSize(8.5f);
        report.setOnClickListener(v -> saveReport());
        row.addView(report, new LinearLayout.LayoutParams(0, dp(39), 1f));
        panel.addView(row, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(39)));

        status12 = new TextView(this);
        status12.setTextSize(8.8f);
        status12.setTextIsSelectable(true);
        status12.setPadding(dp(7), dp(2), dp(7), dp(2));
        ScrollView sv = new ScrollView(this);
        sv.addView(status12, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));
        panel.addView(sv, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(60)));
        root.addView(panel, wi, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void startRequested() {
        if (w == null || !trusted(w.getUrl())) {
            probeInstall = "FAIL_NOT_CHATGPT_HTTPS";
            render12();
            return;
        }
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            androidPermission = "WAITING_RUNTIME_PERMISSION";
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQ_V12_AUDIO);
            render12();
            return;
        }
        begin();
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        if (requestCode != REQ_V12_AUDIO) return;
        if (results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED) begin();
        else {
            androidPermission = "DENIED";
            probeInstall = "BLOCKED_ANDROID_PERMISSION_DENIED";
            ev("ANDROID_RECORD_AUDIO_DENIED");
            render12();
        }
    }

    private void begin() {
        h.removeCallbacksAndMessages(null);
        events12.setLength(0);
        active = true;
        startedAt = System.currentTimeMillis();
        lastEnsure = 0L;
        permissionApi = "NOT_RUN";
        deviceCensus = "NOT_RUN";
        directGum = "NOT_RUN";
        lastGumError = "-";
        gumCalls = gumResolves = gumRejects = trackEvents = 0;
        snapshotAndroid();
        armV11AudioLease();
        nativeMic = "RUNNING";
        probeInstall = "WAITING_NATIVE_SELFTEST";
        ev("DIAG_STARTED");
        render12();

        new Thread(() -> {
            String r = nativeSelftest();
            runOnUiThread(() -> {
                nativeMic = r;
                ev("NATIVE_MIC_SELFTEST_" + tok(r));
                probeInstall = "INSTALLING";
                installProbe(true, () -> {
                    directGum = "RUNNING";
                    runSelftestJs();
                    h.post(poller);
                    render12();
                });
            });
        }, "v12-native-mic").start();
    }

    private void snapshotAndroid() {
        androidPermission = checkSelfPermission(Manifest.permission.RECORD_AUDIO)
                == PackageManager.PERMISSION_GRANTED ? "GRANTED" : "DENIED";
        try {
            AppOpsManager a = (AppOpsManager) getSystemService(APP_OPS_SERVICE);
            int mode = a.unsafeCheckOpNoThrow(AppOpsManager.OPSTR_RECORD_AUDIO,
                    Process.myUid(), getPackageName());
            appOps = appOpsMode(mode);
        } catch (Exception e) {
            appOps = "ERROR_" + e.getClass().getSimpleName();
        }
        try {
            AudioManager am = (AudioManager) getSystemService(AUDIO_SERVICE);
            audioManagerMute = am != null && am.isMicrophoneMute() ? "MUTED" : "NOT_MUTED";
        } catch (Exception e) {
            audioManagerMute = "ERROR_" + e.getClass().getSimpleName();
        }
        if (Build.VERSION.SDK_INT >= 31) {
            try {
                SensorPrivacyManager spm = getSystemService(SensorPrivacyManager.class);
                if (spm == null) micToggleSupport = "UNAVAILABLE";
                else micToggleSupport = spm.supportsSensorToggle(SensorPrivacyManager.Sensors.MICROPHONE)
                        ? "SUPPORTED_STATE_NOT_EXPOSED_BY_PUBLIC_API" : "UNSUPPORTED";
            } catch (Exception e) {
                micToggleSupport = "ERROR_" + e.getClass().getSimpleName();
            }
        } else micToggleSupport = "API_LT_31";
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
                for (int i = 0; i < n; i++) if (buf[i] != 0) { nonZero = true; break; }
            }
            return frames > 0 ? "PASS_frames=" + frames + "_nonzero=" + nonZero : "FAIL_NO_FRAMES";
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

    private void armV11AudioLease() {
        try {
            Method m = AudioModelSuiteV11Activity.class.getDeclaredMethod("startAudioWatch");
            m.setAccessible(true);
            m.invoke(this);
            ev("V11_AUDIO_LEASE_ARMED_BY_V12");
        } catch (Exception e) {
            ev("V11_AUDIO_LEASE_ARM_FAIL_" + e.getClass().getSimpleName());
        }
    }

    private void installProbe(boolean report, Runnable done) {
        if (w == null || !trusted(w.getUrl())) {
            if (report) probeInstall = "FAIL_NOT_CHATGPT_HTTPS";
            if (done != null) done.run();
            return;
        }
        w.evaluateJavascript(INSTALL_JS, value -> {
            if (report) {
                String x = jsString(value);
                probeInstall = x.isEmpty() ? "INSTALLED" : tok(x);
                ev("JS_PROBE_" + probeInstall);
            }
            if (done != null) done.run();
        });
    }

    private void runSelftestJs() {
        w.evaluateJavascript(SELFTEST_JS, value -> {
            ev("WEB_SELFTEST_DISPATCHED");
            render12();
        });
    }

    private void drain() {
        if (w == null || !trusted(w.getUrl())) return;
        w.evaluateJavascript(DRAIN_JS, value -> {
            try {
                String s = jsString(value);
                if (s.isEmpty()) return;
                JSONObject root = new JSONObject(s);
                JSONArray a = root.optJSONArray("events");
                if (a == null) return;
                for (int i = 0; i < a.length(); i++) {
                    JSONObject e = a.optJSONObject(i);
                    if (e != null) consume(e);
                }
            } catch (Exception ignored) { }
        });
    }

    private void consume(JSONObject e) {
        String type = tok(e.optString("type", "UNKNOWN"));
        JSONObject d = e.optJSONObject("data");
        if (d == null) d = new JSONObject();
        switch (type) {
            case "PERM": permissionApi = tok(d.optString("state", "UNKNOWN")); break;
            case "ENUM":
                deviceCensus = "total=" + d.optInt("total", -1)
                        + "_audioIn=" + d.optInt("audioIn", -1)
                        + "_labelsPresent=" + d.optInt("labels", -1);
                break;
            case "GUM_CALL": gumCalls++; break;
            case "GUM_OK": gumResolves++; break;
            case "GUM_FAIL":
                gumRejects++;
                lastGumError = tok(d.optString("name", "UNKNOWN"));
                break;
            case "TRACK_MUTE":
            case "TRACK_UNMUTE":
            case "TRACK_ENDED": trackEvents++; break;
            case "SELFTEST_OK": directGum = "PASS"; break;
            case "SELFTEST_FAIL":
                directGum = "FAIL_" + tok(d.optString("name", "UNKNOWN"));
                lastGumError = tok(d.optString("name", "UNKNOWN"));
                break;
            default: break;
        }
        if (events12.length() < 22000) {
            events12.append(stamp()).append(" | JS_").append(type)
                    .append(" | ").append(safeEventData(d)).append('\n');
        }
    }

    private void render12() {
        if (status12 == null) return;
        StringBuilder s = new StringBuilder();
        s.append("v0.12 AUDIO CAPTURE DIAG active=").append(active).append('\n');
        s.append("Android=").append(androidPermission)
                .append(" AppOps=").append(appOps)
                .append(" SysMute=").append(audioManagerMute).append('\n');
        s.append("NativeMic=").append(nativeMic)
                .append(" DirectGUM=").append(directGum).append('\n');
        s.append("PermissionsAPI=").append(permissionApi)
                .append(" Devices=").append(deviceCensus).append('\n');
        s.append("GUM ").append(gumCalls).append('/').append(gumResolves).append('/')
                .append(gumRejects).append(" lastErr=").append(lastGumError);
        status12.setText(s.toString());
        if (diagButton != null) diagButton.setText(active ? "DIAG ACTIVE" : "AUDIO DIAG12");
    }

    private void saveReport() {
        drain();
        h.postDelayed(() -> {
            try {
                String name = "chatgpt-webview-v12-audio-capture-report-"
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
                Toast.makeText(this, "v0.12 report saved to Downloads", Toast.LENGTH_LONG).show();
            } catch (Exception e) {
                Toast.makeText(this, "REPORT12 failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
            }
        }, 260L);
    }

    private String reportText() {
        StringBuilder r = new StringBuilder();
        r.append("CHATGPT_WEBVIEW_STABLE_V12_AUDIO_CAPTURE_DIAGNOSTIC\n");
        r.append("CURRENT_URL=").append(sanitize(w == null ? "-" : w.getUrl())).append('\n');
        r.append("ANDROID_RECORD_AUDIO_PERMISSION=").append(androidPermission).append('\n');
        r.append("ANDROID_RECORD_AUDIO_APPOPS=").append(appOps).append('\n');
        r.append("ANDROID_AUDIO_MANAGER_MIC_MUTE=").append(audioManagerMute).append('\n');
        r.append("ANDROID_MIC_TOGGLE_SUPPORT=").append(micToggleSupport).append('\n');
        r.append("NATIVE_AUDIORECORD_SELFTEST=").append(nativeMic).append('\n');
        r.append("JS_PROBE_INSTALL=").append(probeInstall).append('\n');
        r.append("WEB_PERMISSIONS_API_MIC_STATE=").append(permissionApi).append('\n');
        r.append("WEB_ENUMERATE_DEVICES=").append(deviceCensus).append('\n');
        r.append("WEB_DIRECT_GUM_SELFTEST=").append(directGum).append('\n');
        r.append("WEB_GUM_CALLS=").append(gumCalls).append('\n');
        r.append("WEB_GUM_RESOLVES=").append(gumResolves).append('\n');
        r.append("WEB_GUM_REJECTS=").append(gumRejects).append('\n');
        r.append("WEB_GUM_LAST_ERROR=").append(lastGumError).append('\n');
        r.append("WEB_TRACK_EVENTS=").append(trackEvents).append('\n');
        r.append("V11_WEB_PERMISSION_STATUS=").append(parentField("audioPermissionStatus")).append('\n');
        r.append("V11_WEB_PERMISSION_ORIGIN=").append(parentField("audioPermissionOrigin")).append('\n');
        r.append("V11_WEB_PERMISSION_REQUEST_COUNT=").append(parentField("audioPermissionRequestCount")).append('\n');
        r.append("RAW_AUDIO_RETAINED=false\nRAW_CHAT_TEXT_RETAINED=false\n");
        r.append("DEVICE_IDS_RETAINED=false\nDEVICE_LABELS_RETAINED=false\n");
        r.append("CHATGPT_COOKIES_EXTRACTED=false\n");
        r.append("--- V12 EVENT LOG ---\n").append(events12);
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

    private String parentField(String name) {
        Object x = parentObject(name);
        return x == null ? "-" : tok(String.valueOf(x));
    }

    private void ev(String s) {
        if (events12.length() < 22000) events12.append(stamp()).append(" | ").append(tok(s)).append('\n');
    }

    private static String stamp() {
        return new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date());
    }

    private static String appOpsMode(int mode) {
        if (mode == AppOpsManager.MODE_ALLOWED) return "ALLOWED";
        if (mode == AppOpsManager.MODE_IGNORED) return "IGNORED";
        if (mode == AppOpsManager.MODE_ERRORED) return "ERRORED";
        if (mode == AppOpsManager.MODE_DEFAULT) return "DEFAULT";
        if (Build.VERSION.SDK_INT >= 29 && mode == AppOpsManager.MODE_FOREGROUND) return "FOREGROUND";
        return "MODE_" + mode;
    }

    private static String jsString(String v) {
        if (v == null || "null".equals(v)) return "";
        try {
            Object x = new JSONTokener(v).nextValue();
            return x instanceof String ? (String) x : String.valueOf(x);
        } catch (Exception e) { return v; }
    }

    private static String tok(String s) {
        String x = s == null ? "-" : s.replaceAll("[^A-Za-z0-9_.:+/=-]", "_");
        return x.length() > 180 ? x.substring(0, 180) : x;
    }

    private static String safeEventData(JSONObject d) {
        String x = d == null ? "{}" : d.toString();
        x = x.replaceAll("[^A-Za-z0-9_{}\\[\\]\\\":.,+/-]", "_");
        return x.length() > 300 ? x.substring(0, 300) : x;
    }

    private static boolean trusted(String raw) {
        try {
            URI u = URI.create(raw == null ? "" : raw);
            return "https".equalsIgnoreCase(u.getScheme()) && "chatgpt.com".equalsIgnoreCase(u.getHost());
        } catch (Exception e) { return false; }
    }

    private static String sanitize(String raw) {
        try {
            URI u = URI.create(raw == null ? "" : raw);
            if (u.getScheme() == null || u.getHost() == null) return "-";
            return u.getScheme() + "://" + u.getHost() + (u.getPath() == null ? "" : u.getPath());
        } catch (Exception e) { return "-"; }
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
        active = false;
        h.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private static final String INSTALL_JS =
            "(function(){try{if(window.__cp12&&window.__cp12.installed)return 'ALREADY_INSTALLED';"
            + "const D={installed:true,e:[]};D.p=(t,d)=>{D.e.push({type:t,data:d||{}});if(D.e.length>100)D.e.shift();};"
            + "D.clean=x=>String(x||'').replace(/[^A-Za-z0-9_.:+/-]/g,'_').slice(0,80);"
            + "const md=navigator.mediaDevices;"
            + "if(md&&md.getUserMedia){const o=md.getUserMedia.bind(md);md.getUserMedia=function(c){D.p('GUM_CALL',{audio:!!(c&&c.audio),video:!!(c&&c.video)});let q;try{q=o(c);}catch(x){D.p('GUM_FAIL',{name:D.clean(x&&x.name)});throw x;}return Promise.resolve(q).then(s=>{const a=s&&s.getAudioTracks?s.getAudioTracks():[];D.p('GUM_OK',{audioTracks:a.length,state:a[0]?D.clean(a[0].readyState):'-',muted:a[0]?!!a[0].muted:false});a.forEach(t=>{try{t.addEventListener('mute',()=>D.p('TRACK_MUTE',{state:D.clean(t.readyState)}));t.addEventListener('unmute',()=>D.p('TRACK_UNMUTE',{state:D.clean(t.readyState)}));t.addEventListener('ended',()=>D.p('TRACK_ENDED',{state:D.clean(t.readyState)}));}catch(_){}});return s;},x=>{D.p('GUM_FAIL',{name:D.clean(x&&x.name)});throw x;});};}"
            + "D.p('PROBE_INSTALLED',{secure:!!window.isSecureContext,media:!!navigator.mediaDevices});return 'INSTALLED';}catch(e){return 'INSTALL_FAIL_'+String(e&&e.name||'Error');}})()";

    private static final String SELFTEST_JS =
            "(async function(){const D=window.__cp12;if(!D)return 'NO_PROBE';"
            + "try{if(navigator.permissions&&navigator.permissions.query){try{const p=await navigator.permissions.query({name:'microphone'});D.p('PERM',{state:D.clean(p&&p.state)});}catch(x){D.p('PERM',{state:'ERROR_'+D.clean(x&&x.name)});}}else D.p('PERM',{state:'UNSUPPORTED'});"
            + "if(navigator.mediaDevices&&navigator.mediaDevices.enumerateDevices){try{const a=await navigator.mediaDevices.enumerateDevices();let ai=0,l=0;a.forEach(x=>{if(x.kind==='audioinput')ai++;if(x.label)l++;});D.p('ENUM',{total:a.length,audioIn:ai,labels:l});}catch(x){D.p('ENUM',{total:-1,audioIn:-1,labels:-1});}}"
            + "try{const s=await navigator.mediaDevices.getUserMedia({audio:true,video:false});const a=s.getAudioTracks();D.p('SELFTEST_OK',{audioTracks:a.length,state:a[0]?D.clean(a[0].readyState):'-',muted:a[0]?!!a[0].muted:false});await new Promise(r=>setTimeout(r,650));a.forEach(t=>{try{t.stop();}catch(_){}});}catch(x){D.p('SELFTEST_FAIL',{name:D.clean(x&&x.name)});}return 'DONE';}catch(x){D.p('SELFTEST_FAIL',{name:D.clean(x&&x.name)});return 'FAIL';}})()";

    private static final String DRAIN_JS =
            "(function(){try{const D=window.__cp12;if(!D)return JSON.stringify({events:[]});const a=D.e.splice(0,D.e.length);return JSON.stringify({events:a});}catch(e){return JSON.stringify({events:[]});}})()";
}
