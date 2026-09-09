package com.homayounisaghar.chatgptwebviewprobe;

import android.content.Context;

import java.util.ArrayList;
import java.util.List;

interface SpeechOutputProviderFactoryV1 {
    SpeechOutputAdapterV1 create(SpeechOutputAdapterV1.Listener listener);
}

final class AndroidTtsSpeechOutputFactoryV1 implements SpeechOutputProviderFactoryV1 {
    private final Context context;
    AndroidTtsSpeechOutputFactoryV1(Context context) {
        if (context == null) throw new IllegalArgumentException("context required");
        this.context = context.getApplicationContext();
    }
    @Override public SpeechOutputAdapterV1 create(SpeechOutputAdapterV1.Listener listener) {
        return new AndroidTtsSpeechOutputV1(context, listener);
    }
}

/**
 * One exact-text speech-output transaction with deterministic chunking and a
 * single terminal receipt only after every provider utterance completes.
 *
 * No semantic summarization is performed. The exact source text digest binds
 * the entire speech transaction even though transport may use many chunks.
 */
final class SpeechOutputSessionV1 implements SpeechOutputAdapterV1.Listener {
    interface Listener {
        void onReady();
        void onSessionStarted(String sessionId, String sourceExactSha256, int chunkCount);
        void onSessionDone(String sessionId, String sourceExactSha256, int chunkCount);
        void onSessionFailed(String sessionId, String sourceExactSha256, String errorClass);
    }

    private final SpeechOutputAdapterV1 adapter;
    private final Listener listener;
    private final int maxChunkChars;
    private final List<String> chunks = new ArrayList<String>();

    private String sessionId = "";
    private String sourceDigest = "";
    private int nextIndex;
    private String activeUtteranceId = "";
    private boolean pendingStart;
    private boolean running;
    private boolean terminal;

    SpeechOutputSessionV1(SpeechOutputProviderFactoryV1 factory, Listener listener, int maxChunkChars) {
        if (factory == null) throw new IllegalArgumentException("factory required");
        if (maxChunkChars < 64) throw new IllegalArgumentException("chunk bound too small");
        this.listener = listener;
        this.maxChunkChars = maxChunkChars;
        this.adapter = factory.create(this);
        if (this.adapter == null) throw new IllegalStateException("provider unavailable");
    }

    synchronized boolean start(String requestedSessionId, String exactText) {
        if (running || pendingStart || terminal) return false;
        if (!safe(requestedSessionId)) return false;
        String canonical = ExactTextV1.canonical(exactText);
        if (canonical.length() == 0) return false;
        List<String> built = SpeechTextChunkerV1.chunk(canonical, maxChunkChars);
        if (built.isEmpty()) return false;

        sessionId = requestedSessionId;
        sourceDigest = ExactTextV1.sha256(canonical);
        chunks.clear();
        chunks.addAll(built);
        nextIndex = 0;
        activeUtteranceId = "";
        pendingStart = true;
        terminal = false;

        if (adapter.isReady()) beginNow();
        return true;
    }

    synchronized boolean isRunning() {
        return running || pendingStart;
    }

    synchronized void cancel() {
        if (terminal) return;
        adapter.stop();
        if (running || pendingStart) fail("USER_CANCELLED");
    }

    synchronized void destroy() {
        adapter.destroy();
        running = false;
        pendingStart = false;
        terminal = true;
    }

    @Override public synchronized void onReady() {
        if (listener != null) listener.onReady();
        if (pendingStart && !terminal) beginNow();
    }

    @Override public synchronized void onStart(String utteranceId) {
        if (!running || terminal || !activeUtteranceId.equals(utteranceId)) return;
    }

    @Override public synchronized void onDone(String utteranceId) {
        if (!running || terminal || !activeUtteranceId.equals(utteranceId)) return;
        activeUtteranceId = "";
        if (nextIndex >= chunks.size()) {
            running = false;
            terminal = true;
            if (listener != null) listener.onSessionDone(sessionId, sourceDigest, chunks.size());
            return;
        }
        dispatchNext();
    }

    @Override public synchronized void onError(String utteranceId, String errorClass) {
        if (terminal) return;
        if ("init".equals(utteranceId) && "PERSIAN_VOICE_UNAVAILABLE".equals(errorClass)) {
            // Provider may still be able to speak with its default voice; this is
            // a capability warning, not proof that the requested utterance failed.
            return;
        }
        fail(errorClass == null ? "SPEECH_PROVIDER_ERROR" : errorClass);
    }

    private void beginNow() {
        if (terminal || running || !pendingStart || !adapter.isReady()) return;
        pendingStart = false;
        running = true;
        if (listener != null) listener.onSessionStarted(sessionId, sourceDigest, chunks.size());
        dispatchNext();
    }

    private void dispatchNext() {
        if (!running || terminal) return;
        if (nextIndex >= chunks.size()) {
            running = false;
            terminal = true;
            if (listener != null) listener.onSessionDone(sessionId, sourceDigest, chunks.size());
            return;
        }
        int index = nextIndex++;
        activeUtteranceId = sessionId + ":chunk:" + index;
        boolean accepted = adapter.speak(chunks.get(index), activeUtteranceId);
        if (!accepted) fail("SPEECH_DISPATCH_REJECTED");
    }

    private void fail(String errorClass) {
        if (terminal) return;
        adapter.stop();
        running = false;
        pendingStart = false;
        terminal = true;
        if (listener != null) listener.onSessionFailed(sessionId, sourceDigest,
                errorClass == null ? "SPEECH_FAILED" : errorClass);
    }

    private static boolean safe(String s) {
        return s != null && s.length() >= 8 && s.length() <= 128 && s.matches("[A-Za-z0-9._:-]+");
    }
}
