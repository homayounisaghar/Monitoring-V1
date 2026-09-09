package com.homayounisaghar.chatgptwebviewprobe;

import android.os.Handler;
import android.os.Looper;

import org.json.JSONObject;

/**
 * Reusable Temporary-Chat lifecycle controller for semantic Planner sessions.
 *
 * It owns only reversible Planner-room navigation and lifecycle receipts. The
 * caller still owns composer write/send correlation and recipe parsing. The
 * caller MUST call beforePlannerSend() immediately before the Planner Send
 * boundary, afterPlannerSendObserved() only after an observed single dispatch,
 * and persistResultAndClose() only after the response has been mechanically
 * parsed/correlated and immutably persisted locally.
 */
final class DisposablePlannerLifecycleControllerV1 {
    interface WebSurface {
        interface JsonCallback { void onResult(JSONObject result); }
        void loadHome();
        void eval(String javascript, JsonCallback callback);
    }

    interface Listener {
        void onTemporaryReady(String attemptId);
        void onResultPersisted(String attemptId, String resultDigest);
        void onCleanupComplete(String attemptId);
        void onLifecycleUncertain(String attemptId, String reason);
    }

    private static final int MAX_POLLS = 40;
    private static final long POLL_MS = 250L;
    private static final int REQUIRED_STABLE_HITS = 2;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private final WebSurface surface;
    private final TemporaryPlannerJournalV1 journal;
    private final Listener listener;

    private boolean running;
    private String attemptId = "";
    private int generation;

    DisposablePlannerLifecycleControllerV1(WebSurface surface,
                                           TemporaryPlannerJournalV1 journal,
                                           Listener listener) {
        if (surface == null || journal == null) throw new IllegalArgumentException("surface/journal required");
        this.surface = surface;
        this.journal = journal;
        this.listener = listener;
    }

    synchronized boolean begin(String newAttemptId, String requestId, String requestDigest) {
        if (running) return false;
        if (!journal.begin(newAttemptId, requestId, requestDigest)) return false;
        running = true;
        attemptId = newAttemptId;
        generation++;
        int g = generation;
        surface.loadHome();
        handler.postDelayed(() -> pollNormalForEntry(g, 0, 0), POLL_MS);
        return true;
    }

    /** Call immediately before the exactly-once Planner Send boundary. */
    synchronized boolean beforePlannerSend(String expectedAttemptId) {
        return running && attemptId.equals(expectedAttemptId)
                && journal.claimPlannerSend(attemptId)
                && journal.markPlannerSendInFlight(attemptId);
    }

    /** Call only after the page observed one Planner Send dispatch. */
    synchronized boolean afterPlannerSendObserved(String expectedAttemptId) {
        return running && attemptId.equals(expectedAttemptId)
                && journal.markWaitingResult(attemptId);
    }

    /**
     * Result digest means the accepted semantic result is already immutable in
     * local recipe/workflow state. Cleanup starts only after that fact persists.
     */
    synchronized boolean persistResultAndClose(String expectedAttemptId, String resultDigest) {
        if (!running || !attemptId.equals(expectedAttemptId)) return false;
        if (!journal.persistResultReceipt(attemptId, resultDigest)) return false;
        if (listener != null) listener.onResultPersisted(attemptId, resultDigest);
        int g = generation;
        handler.post(() -> pollTempForExit(g, 0, 0));
        return true;
    }

    synchronized void stopWithoutReplay(String reason) {
        if (!running) return;
        running = false;
        generation++;
        if (listener != null) listener.onLifecycleUncertain(attemptId,
                reason == null ? "STOPPED_NO_REPLAY" : reason);
    }

    synchronized boolean isRunning() { return running; }

    private void pollNormalForEntry(int g, int attempt, int stableHits) {
        if (!active(g)) return;
        surface.eval(TemporaryChatDomV1.scanJs(), o -> {
            if (!active(g)) return;
            TemporaryChatSignaturesV1.State state = TemporaryChatSignaturesV1.classify(o);
            int hits = state == TemporaryChatSignaturesV1.State.NORMAL ? stableHits + 1 : 0;
            if (hits >= REQUIRED_STABLE_HITS) {
                dispatchEntry(g);
                return;
            }
            if (attempt >= MAX_POLLS) {
                preSendFail("TEMP_NORMAL_ENTRY_GATE_UNRESOLVED");
                return;
            }
            handler.postDelayed(() -> pollNormalForEntry(g, attempt + 1, hits), POLL_MS);
        });
    }

    private void dispatchEntry(int g) {
        if (!active(g)) return;
        surface.eval(TemporaryChatDomV1.enterJs(), action -> {
            if (!active(g)) return;
            boolean dispatched = action != null
                    && action.optBoolean("success", false)
                    && action.optBoolean("dispatched", false)
                    && action.optBoolean("click_observed", false)
                    && action.optInt("match_count", 0) == 1;
            if (!dispatched) {
                lifecycleUncertain("TEMP_ENTRY_DISPATCH_UNCERTAIN_NO_REPLAY");
                return;
            }
            handler.postDelayed(() -> pollTempReceipt(g, 0, 0), POLL_MS);
        });
    }

    private void pollTempReceipt(int g, int attempt, int stableHits) {
        if (!active(g)) return;
        surface.eval(TemporaryChatDomV1.scanJs(), o -> {
            if (!active(g)) return;
            TemporaryChatSignaturesV1.State state = TemporaryChatSignaturesV1.classify(o);
            int hits = state == TemporaryChatSignaturesV1.State.TEMP ? stableHits + 1 : 0;
            if (hits >= REQUIRED_STABLE_HITS) {
                if (!journal.confirmTemp(attemptId)) {
                    lifecycleUncertain("TEMP_RECEIPT_JOURNAL_FAILED");
                    return;
                }
                if (listener != null) listener.onTemporaryReady(attemptId);
                return;
            }
            if (attempt >= MAX_POLLS) {
                lifecycleUncertain("TEMP_ENTRY_RECEIPT_UNRESOLVED_NO_REPLAY");
                return;
            }
            handler.postDelayed(() -> pollTempReceipt(g, attempt + 1, hits), POLL_MS);
        });
    }

    private void pollTempForExit(int g, int attempt, int stableHits) {
        if (!active(g)) return;
        surface.eval(TemporaryChatDomV1.scanJs(), o -> {
            if (!active(g)) return;
            TemporaryChatSignaturesV1.State state = TemporaryChatSignaturesV1.classify(o);
            int hits = state == TemporaryChatSignaturesV1.State.TEMP ? stableHits + 1 : 0;
            if (hits >= REQUIRED_STABLE_HITS) {
                if (!journal.claimExit(attemptId)) {
                    cleanupUncertain("TEMP_EXIT_CLAIM_FAILED");
                    return;
                }
                dispatchExit(g);
                return;
            }
            if (attempt >= MAX_POLLS) {
                cleanupUncertain("TEMP_EXIT_GATE_UNRESOLVED");
                return;
            }
            handler.postDelayed(() -> pollTempForExit(g, attempt + 1, hits), POLL_MS);
        });
    }

    private void dispatchExit(int g) {
        if (!active(g)) return;
        surface.eval(TemporaryChatDomV1.exitJs(), action -> {
            if (!active(g)) return;
            boolean dispatched = action != null
                    && action.optBoolean("success", false)
                    && action.optBoolean("dispatched", false)
                    && action.optBoolean("click_observed", false)
                    && action.optInt("match_count", 0) == 1;
            if (!dispatched) {
                cleanupUncertain("TEMP_EXIT_DISPATCH_UNCERTAIN_NO_REPLAY");
                return;
            }
            handler.postDelayed(() -> pollNormalRestore(g, 0, 0), POLL_MS);
        });
    }

    private void pollNormalRestore(int g, int attempt, int stableHits) {
        if (!active(g)) return;
        surface.eval(TemporaryChatDomV1.scanJs(), o -> {
            if (!active(g)) return;
            TemporaryChatSignaturesV1.State state = TemporaryChatSignaturesV1.classify(o);
            int hits = state == TemporaryChatSignaturesV1.State.NORMAL ? stableHits + 1 : 0;
            if (hits >= REQUIRED_STABLE_HITS) {
                if (!journal.confirmNormal(attemptId)) {
                    cleanupUncertain("NORMAL_RESTORE_JOURNAL_FAILED");
                    return;
                }
                running = false;
                if (listener != null) listener.onCleanupComplete(attemptId);
                return;
            }
            if (attempt >= MAX_POLLS) {
                cleanupUncertain("NORMAL_RESTORE_RECEIPT_UNRESOLVED_NO_REPLAY");
                return;
            }
            handler.postDelayed(() -> pollNormalRestore(g, attempt + 1, hits), POLL_MS);
        });
    }

    private void preSendFail(String reason) {
        journal.failPreSend(attemptId, reason);
        running = false;
        generation++;
        if (listener != null) listener.onLifecycleUncertain(attemptId, reason);
    }

    private void lifecycleUncertain(String reason) {
        running = false;
        generation++;
        if (listener != null) listener.onLifecycleUncertain(attemptId, reason);
    }

    private void cleanupUncertain(String reason) {
        journal.markCleanupUncertain(attemptId, reason);
        running = false;
        generation++;
        if (listener != null) listener.onLifecycleUncertain(attemptId, reason);
    }

    private synchronized boolean active(int g) {
        return running && generation == g;
    }
}
