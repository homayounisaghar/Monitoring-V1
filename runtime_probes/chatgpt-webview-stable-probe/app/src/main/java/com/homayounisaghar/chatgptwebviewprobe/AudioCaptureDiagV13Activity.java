package com.homayounisaghar.chatgptwebviewprobe;

import android.Manifest;
import android.app.AppOpsManager;
import android.content.ContentValues;
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
import android.os.SystemClock;
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

/** Stable v0.13 audio diagnostic.
 *
 * v0.12 accidentally serialized Web Permissions API -> enumerateDevices ->
 * getUserMedia. On the real device the first promise did not settle, so the
 * direct GUM probe never actually ran. v0.13 fixes that by dispatching all
 * three probes independently, with JS-side and native watchdog timeouts.
 *
 * No raw audio, speech, chat text, device ids/labels, cookies or tokens are
 * retained. The direct GUM stream is stopped after a short success sample;
 * if a timed-out GUM resolves late, its tracks are stopped immediately.
 */
public class AudioCaptureDiagV13Activity extends AudioModelSuiteV11FinalActivity {
    private static final int REQ_AUDIO = 1301;
    private static final long LEASE_MS = 10L * 60L * 1000L;
    private static final long WEB_WATCHDOG_MS = 9000L;

    private final Handler h13 = new Handler(Looper.getMainLooper());
    private final StringBuilder events13 = new StringBuilder();

    private WebView web13;
    private TextView status13;
    private Button diag13;
    private boolean active13 = false;
    private long startedElapsed = 0L;

    private String androidPermission = "NOT_CHECKED";
    private String appOps = "NOT_CHECKED";
    private String micMute = "NOT_CHECKED";
    private String nativeMic = "NOT_RUN";
    private String bridge = "NOT_RUN";
    private String permissionsApi = "NOT_RUN";
    private String enumerate = "NOT_RUN";
    private String directGum = "NOT_RUN";
    private String gumError = "-";
    private int gumAudioTracks = -1;
    private String gumTrackState = "-";
    private String gumTrackMuted = "-";
    private int jsEvents = 0;

    private final Runnable poller13 = new Runnable() {
        @Override public void run() {
            if (!active13 || web13 == null) return;
            long age = SystemClock.elapsedRealtime() - startedElapsed;
            if (age >= LEASE_MS) {
                active13 = false;
                ev13("DIAG_AUTO_STOP_LEASE_EXPIRED");
                render13();
                return;
            }
            drain13();
            if (age >= WEB_WATCHDOG_MS) applyNativeWatchdogs();
            render13();
            h13.postDelayed(this, 140L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web13 = findWeb(getWindow().getDecorView());
        if (web13 == null) return;
        web13.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        hideParentUiAndAddPanel();
        ev13("V13_READY");
        render13();
    }

    private void hideParentUiAndAddPanel() {
        View c = findViewById(android.R.id.content);
        if (!(c instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) c;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);

        for (int i = 0; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            if (child != web13) child.setVisibility(View.GONE);
        }

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);

        diag13 = new Button(this);
        diag13.setText("AUDIO DIAG13");
        diag13.setTextSize(8.6f);
        diag13.setOnClickListener(v -> startRequested13());
        row.addView(diag13, new LinearLayout.LayoutParams(0, dp(40), 1f));

        Button report = new Button(this);
        report.setText("REPORT13");
        report.setTextSize(8.6f);
        report.setOnClickListener(v -> saveReport13());
        row.addView(report, new LinearLayout.LayoutParams(0, dp(40), 1f));
        panel.addView(row, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(40)));

        status13 = new TextView(this);
        status13.setTextSize(9.0f);
        status13.setTextIsSelectable(true);
        status13.setPadding(dp(7), dp(3), dp(7), dp(3));
        ScrollView sv = new ScrollView(this);
        sv.addView(status13, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));
        panel.addView(sv, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(82)));

        int wi = root.indexOfChild(web13);
        if (wi < 0) wi = root.getChildCount();
        root.addView(panel, wi, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private void startRequested13() {
        if (active13) {
            ev13("DIAG_START_IGNORED_ALREADY_ACTIVE");
            return;
        }
        if (web13 == null || !trusted(web13.getUrl())) {
            bridge = "FAIL_NOT_CHATGPT_HTTPS";
            render13();
            return;
        }
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            androidPermission = "WAITING_RUNTIME_PERMISSION";
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQ_AUDIO);
            render13();
            return;
        }
        begin13();
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        if (requestCode != REQ_AUDIO) return;
        if (results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED) begin13();
        else {
            androidPermission = "DENIED";
            bridge = "BLOCKED_ANDROID_PERMISSION_DENIED";
            ev13("ANDROID_RECORD_AUDIO_DENIED");
            render13();
        }
    }

    private void begin13() {
        h13.removeCallbacksAndMessages(null);
        events13.setLength(0);
        active13 = true;
        startedElapsed = SystemClock.elapsedRealtime();
        permissionsApi = "RUNNING";
        enumerate = "RUNNING";
        directGum = "RUNNING";
        gumError = "-";
        gumAudioTracks = -1;
        gumTrackState = "-";
        gumTrackMuted = "-";
        jsEvents = 0;
        snapshotAndroid13();
        armV11AudioLease();
        nativeMic = "RUNNING";
        bridge = "WAITING_NATIVE_SELFTEST";
        ev13("DIAG_STARTED");
        render13();

        new Thread(() -> {
            String r = nativeSelftest13();
            runOnUiThread(() -> {
                nativeMic = r;
                ev13("NATIVE_MIC_SELFTEST_" + tok(r));
                installBridgeAndDispatch13();
            });
        }, "v13-native-mic").start();
    }

    private void snapshotAndroid13() {
        androidPermission = checkSelfPermission(Manifest.permission.RECORD_AUDIO)
                == PackageManager.PERMISSION_GRANTED ? "GRANTED" : "DENIED";
        try {
            AppOpsManager a = (AppOpsManager) getSystemService(APP_OPS_SERVICE);
            int mode = a.unsafeCheckOpNoThrow(AppOpsManager.OPSTR_RECORD_AUDIO,
                    Process.myUid(), getPackageName());
            if (mode == AppOpsManager.MODE_ALLOWED) appOps = "ALLOWED";
            else if (mode == AppOpsManager.MODE_IGNORED) appOps = "IGNORED";
            else if (mode == AppOpsManager.MODE_ERRORED) appOps = "ERRORED";
            else if (mode == AppOpsManager.MODE_DEFAULT) appOps = "DEFAULT";
            else appOps = "MODE_" + mode;
        } catch (Exception e) {
            appOps = "ERROR_" + e.getClass().getSimpleName();
        }
        try {
            AudioManager am = (AudioManager) getSystemService(AUDIO_SERVICE);
            micMute = am != null && am.isMicrophoneMute() ? "MUTED" : "NOT_MUTED";
        } catch (Exception e) {
            micMute = "ERROR_" + e.getClass().getSimpleName();
        }
    }

    private String nativeSelftest13() {
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
            long deadline = SystemClock.elapsedRealtime() + 450L;
            while (SystemClock.elapsedRealtime() < deadline && frames < 3200) {
                int n = ar.read(buf, 0, buf.length, AudioRecord.READ_BLOCKING);
                if (n < 0) return "FAIL_READ_" + n;
                frames += n;
                for (int i = 0; i < n; i++) {
                    if (buf[i] != 0) { nonZero = true; break; }
                }
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
            ev13("V11_AUDIO_LEASE_ARMED_BY_V13");
        } catch (Exception e) {
            ev13("V11_AUDIO_LEASE_ARM_FAIL_" + e.getClass().getSimpleName());
        }
    }

    private void installBridgeAndDispatch13() {
        if (web13 == null || !trusted(web13.getUrl())) {
            bridge = "FAIL_NOT_CHATGPT_HTTPS";
            applyNativeWatchdogs();
            return;
        }
        bridge = "INSTALLING";
        web13.evaluateJavascript(INSTALL_JS, value -> {
            String x = jsString(value);
            bridge = x.isEmpty() ? "INSTALLED" : tok(x);
            ev13("JS_BRIDGE_" + bridge);
            if (!bridge.startsWith("INSTALLED")) {
                applyNativeWatchdogs();
                render13();
                return;
            }
            // Important: each probe is dispatched independently. None awaits another.
            web13.evaluateJavascript(GUM_JS, v -> ev13("DIRECT_GUM_SCRIPT_" + tok(jsString(v))));
            web13.evaluateJavascript(PERM_JS, v -> ev13("PERMISSIONS_SCRIPT_" + tok(jsString(v))));
            web13.evaluateJavascript(ENUM_JS, v -> ev13("ENUM_SCRIPT_" + tok(jsString(v))));
            h13.post(poller13);
            h13.postDelayed(this::applyNativeWatchdogs, WEB_WATCHDOG_MS);
            render13();
        });
    }

    private void drain13() {
        if (web13 == null || !trusted(web13.getUrl())) return;
        web13.evaluateJavascript(DRAIN_JS, value -> {
            try {
                String s = jsString(value);
                if (s.isEmpty()) return;
                JSONObject root = new JSONObject(s);
                JSONArray a = root.optJSONArray("events");
                if (a == null) return;
                for (int i = 0; i < a.length(); i++) {
                    JSONObject e = a.optJSONObject(i);
                    if (e != null) consume13(e);
                }
            } catch (Exception ignored) { }
        });
    }

    private void consume13(JSONObject e) {
        String type = tok(e.optString("type", "UNKNOWN"));
        JSONObject d = e.optJSONObject("data");
        if (d == null) d = new JSONObject();
        jsEvents++;
        switch (type) {
            case "PERM_OK": permissionsApi = tok(d.optString("state", "UNKNOWN")); break;
            case "PERM_FAIL": permissionsApi = "FAIL_" + tok(d.optString("name", "UNKNOWN")); break;
            case "PERM_TIMEOUT": permissionsApi = "TIMEOUT"; break;
            case "ENUM_OK":
                enumerate = "PASS_total=" + d.optInt("total", -1)
                        + "_audioIn=" + d.optInt("audioIn", -1)
                        + "_labelsPresent=" + d.optInt("labels", -1);
                break;
            case "ENUM_FAIL": enumerate = "FAIL_" + tok(d.optString("name", "UNKNOWN")); break;
            case "ENUM_TIMEOUT": enumerate = "TIMEOUT"; break;
            case "GUM_OK":
                directGum = "PASS";
                gumAudioTracks = d.optInt("audioTracks", -1);
                gumTrackState = tok(d.optString("state", "-"));
                gumTrackMuted = String.valueOf(d.optBoolean("muted", false));
                break;
            case "GUM_FAIL":
                directGum = "FAIL_" + tok(d.optString("name", "UNKNOWN"));
                gumError = tok(d.optString("name", "UNKNOWN"));
                break;
            case "GUM_TIMEOUT": directGum = "TIMEOUT"; break;
            case "GUM_LATE_OK_STOPPED":
                if ("TIMEOUT".equals(directGum) || directGum.startsWith("WATCHDOG")) {
                    directGum = "TIMEOUT_LATE_OK_STOPPED";
                    gumAudioTracks = d.optInt("audioTracks", -1);
                }
                break;
            case "GUM_LATE_FAIL":
                if ("TIMEOUT".equals(directGum) || directGum.startsWith("WATCHDOG")) {
                    gumError = tok(d.optString("name", "UNKNOWN"));
                }
                break;
            default: break;
        }
        if (events13.length() < 20000) {
            events13.append(stamp()).append(" | JS_").append(type)
                    .append(" | ").append(safeEventData(d)).append('\n');
        }
        render13();
    }

    private void applyNativeWatchdogs() {
        if ("RUNNING".equals(permissionsApi)) {
            permissionsApi = "WATCHDOG_TIMEOUT_NO_RESULT";
            ev13("PERMISSIONS_NATIVE_WATCHDOG_TIMEOUT");
        }
        if ("RUNNING".equals(enumerate)) {
            enumerate = "WATCHDOG_TIMEOUT_NO_RESULT";
            ev13("ENUM_NATIVE_WATCHDOG_TIMEOUT");
        }
        if ("RUNNING".equals(directGum)) {
            directGum = "WATCHDOG_TIMEOUT_NO_RESULT";
            ev13("GUM_NATIVE_WATCHDOG_TIMEOUT");
        }
        render13();
    }

    private void render13() {
        if (status13 == null) return;
        StringBuilder s = new StringBuilder();
        s.append("v0.13 PARALLEL AUDIO DIAG active=").append(active13).append('\n');
        s.append("Android=").append(androidPermission).append(" AppOps=").append(appOps)
                .append(" SysMute=").append(micMute).append('\n');
        s.append("NativeMic=").append(nativeMic).append(" Bridge=").append(bridge).append('\n');
        s.append("DirectGUM=").append(directGum).append(" err=").append(gumError).append('\n');
        s.append("PermissionsAPI=").append(permissionsApi).append('\n');
        s.append("Devices=").append(enumerate).append(" jsEvents=").append(jsEvents);
        status13.setText(s.toString());
        if (diag13 != null) diag13.setText(active13 ? "DIAG13 ACTIVE" : "AUDIO DIAG13");
    }

    private void saveReport13() {
        drain13();
        h13.postDelayed(() -> {
            try {
                String name = "chatgpt-webview-v13-parallel-audio-report-"
                        + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".txt";
                ContentValues cv = new ContentValues();
                cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
                cv.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
                cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
                Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
                if (u == null) throw new IllegalStateException("insert");
                try (OutputStream out = getContentResolver().openOutputStream(u)) {
                    if (out == null) throw new IllegalStateException("stream");
                    out.write(reportText13().getBytes(StandardCharsets.UTF_8));
                }
                Toast.makeText(this, "v0.13 report saved to Downloads", Toast.LENGTH_LONG).show();
            } catch (Exception e) {
                Toast.makeText(this, "REPORT13 failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
            }
        }, 280L);
    }

    private String reportText13() {
        StringBuilder r = new StringBuilder();
        r.append("CHATGPT_WEBVIEW_STABLE_V13_PARALLEL_AUDIO_DIAGNOSTIC\n");
        r.append("CURRENT_URL=").append(sanitizeUrl(web13 == null ? "" : web13.getUrl())).append('\n');
        r.append("ANDROID_RECORD_AUDIO_PERMISSION=").append(androidPermission).append('\n');
        r.append("ANDROID_RECORD_AUDIO_APPOPS=").append(appOps).append('\n');
        r.append("ANDROID_AUDIO_MANAGER_MIC_MUTE=").append(micMute).append('\n');
        r.append("NATIVE_AUDIORECORD_SELFTEST=").append(nativeMic).append('\n');
        r.append("JS_BRIDGE=").append(bridge).append('\n');
        r.append("WEB_PERMISSIONS_API_MIC_STATE=").append(permissionsApi).append('\n');
        r.append("WEB_ENUMERATE_DEVICES=").append(enumerate).append('\n');
        r.append("WEB_DIRECT_GUM_SELFTEST=").append(directGum).append('\n');
        r.append("WEB_DIRECT_GUM_LAST_ERROR=").append(gumError).append('\n');
        r.append("WEB_DIRECT_GUM_AUDIO_TRACKS=").append(gumAudioTracks).append('\n');
        r.append("WEB_DIRECT_GUM_TRACK_STATE=").append(gumTrackState).append('\n');
        r.append("WEB_DIRECT_GUM_TRACK_MUTED=").append(gumTrackMuted).append('\n');
        r.append("WEB_JS_EVENT_COUNT=").append(jsEvents).append('\n');
        r.append("V11_WEB_PERMISSION_STATUS=").append(parentString("audioPermissionStatus", "-")).append('\n');
        r.append("V11_WEB_PERMISSION_ORIGIN=").append(parentString("audioPermissionOrigin", "-")).append('\n');
        r.append("V11_WEB_PERMISSION_REQUEST_COUNT=").append(parentInt("audioPermissionRequestCount", -1)).append('\n');
        r.append("RAW_AUDIO_RETAINED=false\n");
        r.append("RAW_CHAT_TEXT_RETAINED=false\n");
        r.append("DEVICE_IDS_RETAINED=false\n");
        r.append("DEVICE_LABELS_RETAINED=false\n");
        r.append("CHATGPT_COOKIES_EXTRACTED=false\n");
        r.append("--- V13 EVENT LOG ---\n").append(events13);
        Object p = parentObject("events");
        if (p instanceof StringBuilder) r.append("--- V11 EVENT LOG ---\n").append(p.toString());
        return r.toString();
    }

    private Object parentObject(String name) {
        try {
            Field f = AudioModelSuiteV11Activity.class.getDeclaredField(name);
            f.setAccessible(true);
            return f.get(this);
        } catch (Exception e) { return null; }
    }

    private String parentString(String name, String fallback) {
        Object x = parentObject(name);
        return x == null ? fallback : tok(String.valueOf(x));
    }

    private int parentInt(String name, int fallback) {
        Object x = parentObject(name);
        return x instanceof Number ? ((Number) x).intValue() : fallback;
    }

    private String safeEventData(JSONObject d) {
        StringBuilder s = new StringBuilder();
        if (d.has("state")) s.append("state=").append(tok(d.optString("state", "-"))).append(' ');
        if (d.has("name")) s.append("name=").append(tok(d.optString("name", "-"))).append(' ');
        if (d.has("total")) s.append("total=").append(d.optInt("total", -1)).append(' ');
        if (d.has("audioIn")) s.append("audioIn=").append(d.optInt("audioIn", -1)).append(' ');
        if (d.has("labels")) s.append("labels=").append(d.optInt("labels", -1)).append(' ');
        if (d.has("audioTracks")) s.append("audioTracks=").append(d.optInt("audioTracks", -1)).append(' ');
        if (d.has("muted")) s.append("muted=").append(d.optBoolean("muted", false)).append(' ');
        return s.toString().trim();
    }

    private void ev13(String e) {
        if (events13.length() < 20000) events13.append(stamp()).append(" | ").append(tok(e)).append('\n');
    }

    private static String stamp() {
        return new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date());
    }

    private static String tok(String s) {
        String x = s == null ? "-" : s.replaceAll("[^A-Za-z0-9_.:+/=-]", "_");
        return x.length() > 140 ? x.substring(0, 140) : x;
    }

    private static String jsString(String raw) {
        if (raw == null || "null".equals(raw)) return "";
        try {
            Object o = new JSONTokener(raw).nextValue();
            return o instanceof String ? (String) o : String.valueOf(o);
        } catch (Exception e) { return raw.replace("\"", ""); }
    }

    private static boolean trusted(String raw) {
        try {
            URI u = URI.create(raw == null ? "" : raw);
            return "https".equalsIgnoreCase(u.getScheme()) && "chatgpt.com".equalsIgnoreCase(u.getHost());
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

    private int dp(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }

    private WebView findWeb(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (!(v instanceof ViewGroup)) return null;
        ViewGroup g = (ViewGroup) v;
        for (int i = 0; i < g.getChildCount(); i++) {
            WebView w = findWeb(g.getChildAt(i));
            if (w != null) return w;
        }
        return null;
    }

    @Override protected void onDestroy() {
        h13.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private static final String INSTALL_JS =
            "(function(){try{if(window.__cp13&&window.__cp13.v===13)return 'INSTALLED_REUSED';"
            + "const D={v:13,q:[]};D.p=(t,d)=>D.q.push({type:t,data:d||{},ts:performance.now()});"
            + "D.drain=()=>{const a=D.q.splice(0,D.q.length);return {events:a};};"
            + "window.__cp13=D;D.p('PROBE',{secure:!!window.isSecureContext,media:!!navigator.mediaDevices});"
            + "return 'INSTALLED';}catch(e){return 'INSTALL_FAIL_'+String(e&&e.name||'Error');}})()";

    // Immediate return: the underlying getUserMedia promise is not awaited by evaluateJavascript.
    private static final String GUM_JS =
            "(function(){const D=window.__cp13;if(!D)return 'NO_BRIDGE';"
            + "try{if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){D.p('GUM_FAIL',{name:'UNSUPPORTED'});return 'UNSUPPORTED';}"
            + "D.p('GUM_DISPATCH',{});let done=false;let p;try{p=navigator.mediaDevices.getUserMedia({audio:true,video:false});}catch(x){D.p('GUM_FAIL',{name:String(x&&x.name||'Error')});return 'SYNC_FAIL';}"
            + "setTimeout(()=>{if(!done){done=true;D.p('GUM_TIMEOUT',{});}},7000);"
            + "Promise.resolve(p).then(s=>{const a=s&&s.getAudioTracks?s.getAudioTracks():[];if(done){a.forEach(t=>{try{t.stop();}catch(_){}});D.p('GUM_LATE_OK_STOPPED',{audioTracks:a.length});return;}"
            + "done=true;D.p('GUM_OK',{audioTracks:a.length,state:a[0]?String(a[0].readyState||'-'):'-',muted:a[0]?!!a[0].muted:false});"
            + "setTimeout(()=>a.forEach(t=>{try{t.stop();}catch(_){}}),650);},x=>{const n=String(x&&x.name||'Error');if(done)D.p('GUM_LATE_FAIL',{name:n});else{done=true;D.p('GUM_FAIL',{name:n});}});"
            + "return 'DISPATCHED';}catch(e){D.p('GUM_FAIL',{name:String(e&&e.name||'Error')});return 'FAIL';}})()";

    private static final String PERM_JS =
            "(function(){const D=window.__cp13;if(!D)return 'NO_BRIDGE';"
            + "try{if(!navigator.permissions||!navigator.permissions.query){D.p('PERM_FAIL',{name:'UNSUPPORTED'});return 'UNSUPPORTED';}"
            + "let done=false;D.p('PERM_DISPATCH',{});setTimeout(()=>{if(!done){done=true;D.p('PERM_TIMEOUT',{});}},2500);"
            + "let p;try{p=navigator.permissions.query({name:'microphone'});}catch(x){D.p('PERM_FAIL',{name:String(x&&x.name||'Error')});return 'SYNC_FAIL';}"
            + "Promise.resolve(p).then(x=>{if(done)return;done=true;D.p('PERM_OK',{state:String(x&&x.state||'UNKNOWN')});},x=>{if(done)return;done=true;D.p('PERM_FAIL',{name:String(x&&x.name||'Error')});});"
            + "return 'DISPATCHED';}catch(e){D.p('PERM_FAIL',{name:String(e&&e.name||'Error')});return 'FAIL';}})()";

    private static final String ENUM_JS =
            "(function(){const D=window.__cp13;if(!D)return 'NO_BRIDGE';"
            + "try{if(!navigator.mediaDevices||!navigator.mediaDevices.enumerateDevices){D.p('ENUM_FAIL',{name:'UNSUPPORTED'});return 'UNSUPPORTED';}"
            + "let done=false;D.p('ENUM_DISPATCH',{});setTimeout(()=>{if(!done){done=true;D.p('ENUM_TIMEOUT',{});}},3000);"
            + "let p;try{p=navigator.mediaDevices.enumerateDevices();}catch(x){D.p('ENUM_FAIL',{name:String(x&&x.name||'Error')});return 'SYNC_FAIL';}"
            + "Promise.resolve(p).then(a=>{if(done)return;done=true;let ai=0,l=0;(a||[]).forEach(x=>{if(x.kind==='audioinput')ai++;if(x.label)l++;});D.p('ENUM_OK',{total:(a||[]).length,audioIn:ai,labels:l});},x=>{if(done)return;done=true;D.p('ENUM_FAIL',{name:String(x&&x.name||'Error')});});"
            + "return 'DISPATCHED';}catch(e){D.p('ENUM_FAIL',{name:String(e&&e.name||'Error')});return 'FAIL';}})()";

    private static final String DRAIN_JS =
            "(function(){try{return JSON.stringify(window.__cp13?window.__cp13.drain():{events:[]});}catch(e){return JSON.stringify({events:[]});}})()";
}
