package com.homayounisaghar.chatgptwebviewprobe;

import android.content.pm.PackageInfo;
import android.graphics.Typeface;
import android.media.AudioManager;
import android.media.ToneGenerator;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.TypedValue;
import android.view.HapticFeedbackConstants;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import org.json.JSONObject;

import java.io.OutputStream;
import java.lang.reflect.Field;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

/**
 * Stable v0.27: redundant user speech cue on top of the proven v0.26 ready-gated lifecycle.
 *
 * v0.26 real-device telemetry proved that SPEAK_WINDOW_STARTED was reached, while the user
 * heard no beep. The inherited v0.23 cue uses STREAM_NOTIFICATION, which may be inaudible
 * under notification/ringer/DND policy. v0.27 does not change Dictation control semantics.
 * It adds a prominent visual countdown, best-effort haptic feedback and a short STREAM_MUSIC
 * tone without changing user volume or adding permissions.
 */
public class OrchestratorAutonomousV27Activity extends OrchestratorAutonomousV26Activity {
    private static final String SCHEMA27 = "cp-v27-speech-cue-v1";
    private static final String SCENARIO27 = "dictation-redundant-speech-cue-v27";
    private static final long SPEECH_WINDOW_MS = 5000L;
    private static final int NET_TIMEOUT_MS = 2800;

    private final Handler h27 = new Handler(Looper.getMainLooper());
    private final Runnable monitor27 = new Runnable() {
        @Override public void run() {
            try { tick27(); } catch (Exception ignored) {}
            h27.postDelayed(this, 70L);
        }
    };

    private String activeTest27 = "-";
    private boolean cueActive27 = false;
    private boolean cuePosted27 = false;
    private long cueStarted27 = 0L;
    private int seq27 = 0;
    private TextView status27;
    private Button run27;

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Object s = objectField27("status23");
        if (s instanceof TextView) status27 = (TextView) s;
        Object b = objectField27("runButton23");
        if (b instanceof Button) run27 = (Button) b;
        h27.postDelayed(monitor27, 120L);
    }

    @Override protected void onDestroy() {
        h27.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private void tick27() {
        String testId = stringField27("testId23");
        if (testId != null && testId.startsWith("cp23-") && !testId.equals(activeTest27)) {
            activeTest27 = testId;
            cueActive27 = false;
            cuePosted27 = false;
            cueStarted27 = 0L;
            seq27 = 0;
        }
        if ("-".equals(activeTest27)) return;

        String phase = stringField27("currentPhase23");
        if ("SPEAK_WINDOW_STARTED".equals(phase)) {
            if (!cueActive27) beginCue27();
            updateVisual27();
        } else if (cueActive27) {
            endCue27(phase);
        }
    }

    private void beginCue27() {
        cueActive27 = true;
        cueStarted27 = System.currentTimeMillis();

        boolean haptic = false;
        try {
            View target = status27 != null ? status27 : run27;
            if (target != null) haptic = target.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS);
        } catch (Exception ignored) {}

        boolean accessibilityAnnounced = false;
        try {
            View target = status27 != null ? status27 : run27;
            if (target != null) {
                target.announceForAccessibility("Speak now. Say one short Persian sentence.");
                accessibilityAnnounced = true;
            }
        } catch (Exception ignored) {}

        boolean mediaToneAttempted = false;
        try {
            ToneGenerator t = new ToneGenerator(AudioManager.STREAM_MUSIC, 100);
            mediaToneAttempted = t.startTone(ToneGenerator.TONE_PROP_BEEP, 140);
            h27.postDelayed(t::release, 260L);
        } catch (Exception ignored) {}

        JSONObject s = new JSONObject();
        put27(s, "visual_status_banner", status27 != null);
        put27(s, "visual_button_banner", run27 != null);
        put27(s, "haptic_result", haptic);
        put27(s, "accessibility_announce_attempted", accessibilityAnnounced);
        put27(s, "media_tone_attempted", mediaToneAttempted);
        put27(s, "media_stream", "STREAM_MUSIC");
        put27(s, "notification_stream_dependency_removed", true);
        put27(s, "user_volume_changed", false);
        put27(s, "speech_window_ms", SPEECH_WINDOW_MS);
        put27(s, "raw_audio_uploaded", false);
        put27(s, "raw_speech_uploaded", false);
        post27("SPEECH_CUE_EMITTED", "REDUNDANT_VISUAL_HAPTIC_MEDIA_CUE", s);
        cuePosted27 = true;
    }

    private void updateVisual27() {
        long elapsed = Math.max(0L, System.currentTimeMillis() - cueStarted27);
        long remain = Math.max(0L, SPEECH_WINDOW_MS - elapsed);
        int sec = Math.max(1, (int) Math.ceil(remain / 1000.0));
        if (status27 != null) {
            status27.setTextSize(TypedValue.COMPLEX_UNIT_SP, 28f);
            status27.setTypeface(Typeface.DEFAULT_BOLD);
            status27.setText("SPEAK NOW — " + sec + "\nیک جمله کوتاه فارسی بگو");
        }
        if (run27 != null) run27.setText("SPEAK NOW — " + sec);
    }

    private void endCue27(String nextPhase) {
        cueActive27 = false;
        long duration = cueStarted27 == 0L ? -1L : System.currentTimeMillis() - cueStarted27;
        if (status27 != null) {
            status27.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12f);
            status27.setTypeface(Typeface.DEFAULT);
        }
        if (run27 != null && !run27.isEnabled()) run27.setText("RUNNING...");
        if (cuePosted27) {
            JSONObject s = new JSONObject();
            put27(s, "cue_visible_ms", duration);
            put27(s, "next_parent_phase", nextPhase == null ? "-" : nextPhase);
            put27(s, "user_volume_changed", false);
            post27("SPEECH_CUE_EXIT", "CUE_WINDOW_ENDED", s);
        }
    }

    private void post27(String phase, String classification, JSONObject state) {
        if (!TelemetryConfigV27.isConfigured()) return;
        JSONObject p = new JSONObject();
        put27(p, "kind", "DIAGNOSTIC_PHASE");
        put27(p, "schema_version", SCHEMA27);
        put27(p, "scenario_id", SCENARIO27);
        put27(p, "test_id", activeTest27);
        put27(p, "seq", ++seq27);
        put27(p, "phase", phase);
        put27(p, "classification", classification);
        put27(p, "app_version", appVersion27());
        put27(p, "source_ref", TelemetryConfigV27.SOURCE_REF);
        put27(p, "collector_id", TelemetryConfigV27.COLLECTOR_ID);
        put27(p, "privacy", "cue_receipts_only_no_raw_audio_speech_transcript_or_chat_text");
        put27(p, "state", state == null ? new JSONObject() : state);
        int n = seq27;
        new Thread(() -> upload27(p), "cp27-telemetry-" + n).start();
    }

    private void upload27(JSONObject payload) {
        HttpURLConnection c = null;
        try {
            URL u = new URL(TelemetryConfigV27.WEBHOOK_URL);
            c = (HttpURLConnection) u.openConnection();
            c.setRequestMethod("POST");
            c.setConnectTimeout(NET_TIMEOUT_MS);
            c.setReadTimeout(NET_TIMEOUT_MS);
            c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            byte[] b = payload.toString().getBytes(StandardCharsets.UTF_8);
            c.setFixedLengthStreamingMode(b.length);
            try (OutputStream os = c.getOutputStream()) { os.write(b); }
            c.getResponseCode();
        } catch (Exception ignored) {
        } finally {
            if (c != null) c.disconnect();
        }
    }

    private String appVersion27() {
        try {
            PackageInfo p = getPackageManager().getPackageInfo(getPackageName(), 0);
            long code = android.os.Build.VERSION.SDK_INT >= 28 ? p.getLongVersionCode() : p.versionCode;
            return p.versionName + "(" + code + ")";
        } catch (Exception e) {
            return "unknown";
        }
    }

    private Object objectField27(String name) {
        Class<?> c = getClass();
        while (c != null) {
            try {
                Field f = c.getDeclaredField(name);
                f.setAccessible(true);
                return f.get(this);
            } catch (Exception ignored) {
                c = c.getSuperclass();
            }
        }
        return null;
    }

    private String stringField27(String name) {
        Object o = objectField27(name);
        return o == null ? "-" : String.valueOf(o);
    }

    private void put27(JSONObject o, String k, Object v) {
        try { o.put(k, v); } catch (Exception ignored) {}
    }
}
