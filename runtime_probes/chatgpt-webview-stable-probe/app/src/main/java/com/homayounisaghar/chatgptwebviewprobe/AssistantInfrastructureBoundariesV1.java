package com.homayounisaghar.chatgptwebviewprobe;

import android.content.Context;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;

import java.util.Locale;

/** Provider boundaries for the first-usable-assistant infrastructure. */
interface SpeechOutputAdapterV1 {
    interface Listener {
        void onReady();
        void onStart(String utteranceId);
        void onDone(String utteranceId);
        void onError(String utteranceId, String errorClass);
    }

    boolean isReady();
    boolean speak(String exactText, String utteranceId);
    void stop();
    void destroy();
}

/**
 * First speech-output provider. It is deliberately replaceable: workflow and
 * Planner semantics depend only on SpeechOutputAdapterV1, never on Android TTS.
 */
final class AndroidTtsSpeechOutputV1 implements SpeechOutputAdapterV1, TextToSpeech.OnInitListener {
    private final Listener listener;
    private TextToSpeech tts;
    private boolean ready;
    private boolean destroyed;

    AndroidTtsSpeechOutputV1(Context context, Listener listener) {
        if (context == null) throw new IllegalArgumentException("context required");
        this.listener = listener;
        this.tts = new TextToSpeech(context.getApplicationContext(), this);
    }

    @Override public void onInit(int status) {
        if (destroyed || tts == null) return;
        if (status != TextToSpeech.SUCCESS) {
            if (listener != null) listener.onError("init", "TTS_INIT_FAILED");
            return;
        }
        int language = tts.setLanguage(new Locale("fa", "IR"));
        if (language == TextToSpeech.LANG_MISSING_DATA || language == TextToSpeech.LANG_NOT_SUPPORTED) {
            // Do not fail the adapter entirely: installed engine may still handle
            // mixed-language text via its default voice. Report the limitation.
            if (listener != null) listener.onError("init", "PERSIAN_VOICE_UNAVAILABLE");
        }
        tts.setOnUtteranceProgressListener(new UtteranceProgressListener() {
            @Override public void onStart(String utteranceId) {
                if (listener != null) listener.onStart(utteranceId);
            }
            @Override public void onDone(String utteranceId) {
                if (listener != null) listener.onDone(utteranceId);
            }
            @Override public void onError(String utteranceId) {
                if (listener != null) listener.onError(utteranceId, "TTS_ERROR");
            }
            @Override public void onError(String utteranceId, int errorCode) {
                if (listener != null) listener.onError(utteranceId, "TTS_ERROR_" + errorCode);
            }
        });
        ready = true;
        if (listener != null) listener.onReady();
    }

    @Override public boolean isReady() {
        return ready && !destroyed && tts != null;
    }

    @Override public boolean speak(String exactText, String utteranceId) {
        if (!isReady() || utteranceId == null || utteranceId.length() < 1) return false;
        String text = ExactTextV1.canonical(exactText);
        if (text.length() == 0) return false;
        Bundle params = new Bundle();
        int result = tts.speak(text, TextToSpeech.QUEUE_FLUSH, params, utteranceId);
        return result == TextToSpeech.SUCCESS;
    }

    @Override public void stop() {
        if (tts != null) tts.stop();
    }

    @Override public void destroy() {
        destroyed = true;
        ready = false;
        if (tts != null) {
            tts.stop();
            tts.shutdown();
            tts = null;
        }
    }
}

/**
 * Wake word is ingress only. Implementations may be local hotword engines,
 * assistant-role integrations, watches, headsets or other future sources.
 * They are not allowed to interpret user intent or dispatch capabilities.
 */
interface WakeIngressAdapterV1 {
    interface Listener {
        void onWakeDetected(String detectorEventId);
        void onWakeError(String errorClass);
    }

    boolean start();
    void stop();
    boolean isRunning();
    void destroy();
}

/** Safe placeholder until a concrete always-listening provider is selected. */
final class DisabledWakeIngressV1 implements WakeIngressAdapterV1 {
    @Override public boolean start() { return false; }
    @Override public void stop() {}
    @Override public boolean isRunning() { return false; }
    @Override public void destroy() {}
}

/**
 * Disposable semantic Planner session boundary.
 *
 * The current Dashboard still has a concrete WebView implementation path. The
 * next integration should implement this interface using the already-qualified
 * Temporary Chat entry/exit signatures rather than baking Temporary Chat logic
 * into workflow semantics.
 */
interface PlannerSessionLifecycleV1 {
    interface Listener {
        void onDisposableSessionReady(String sessionAttemptId);
        void onDisposableSessionClosed(String sessionAttemptId);
        void onSessionError(String sessionAttemptId, String errorClass);
    }

    boolean beginDisposable(String sessionAttemptId);
    boolean markSemanticResultPersisted(String sessionAttemptId, String resultDigest);
    boolean finishDisposable(String sessionAttemptId);
    boolean isDisposableSessionActive();
}
