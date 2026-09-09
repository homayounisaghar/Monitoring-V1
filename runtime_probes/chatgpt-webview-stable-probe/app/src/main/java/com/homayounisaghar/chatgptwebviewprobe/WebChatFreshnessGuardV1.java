package com.homayounisaghar.chatgptwebviewprobe;

/**
 * Pure mechanical guard against a dynamic Web UI rendering an older
 * conversation state after a newer external hint/notification has already
 * arrived. The guard performs no DOM access and dispatches no reload itself.
 * It only classifies sanitized snapshots and tells the caller when a single
 * controlled reload escalation is justified.
 */
final class WebChatFreshnessGuardV1 {
    enum State {
        WAIT_ROUTE,
        WAIT_HYDRATION,
        WAIT_CONVERGENCE,
        WAIT_ADVANCE,
        RELOAD_RECOMMENDED,
        FRESH,
        FRESHNESS_UNPROVEN,
        UNCERTAIN
    }

    static final class Watermark {
        final String pathHash;
        final int userTurnCount;
        final int assistantTurnCount;
        final String turnSequenceDigest;
        final String lastUserExactHash;
        final String lastAssistantExactHash;

        Watermark(String pathHash,
                  int userTurnCount,
                  int assistantTurnCount,
                  String turnSequenceDigest,
                  String lastUserExactHash,
                  String lastAssistantExactHash) {
            this.pathHash = nz(pathHash);
            this.userTurnCount = Math.max(0, userTurnCount);
            this.assistantTurnCount = Math.max(0, assistantTurnCount);
            this.turnSequenceDigest = nz(turnSequenceDigest);
            this.lastUserExactHash = nz(lastUserExactHash);
            this.lastAssistantExactHash = nz(lastAssistantExactHash);
        }
    }

    static final class Snapshot {
        final boolean documentReadyComplete;
        final String pathHash;
        final int userTurnCount;
        final int assistantTurnCount;
        final String turnSequenceDigest;
        final String lastUserExactHash;
        final String lastAssistantExactHash;
        final int stopCandidateCount;
        final boolean generationActive;

        Snapshot(boolean documentReadyComplete,
                 String pathHash,
                 int userTurnCount,
                 int assistantTurnCount,
                 String turnSequenceDigest,
                 String lastUserExactHash,
                 String lastAssistantExactHash,
                 int stopCandidateCount,
                 boolean generationActive) {
            this.documentReadyComplete = documentReadyComplete;
            this.pathHash = nz(pathHash);
            this.userTurnCount = Math.max(0, userTurnCount);
            this.assistantTurnCount = Math.max(0, assistantTurnCount);
            this.turnSequenceDigest = nz(turnSequenceDigest);
            this.lastUserExactHash = nz(lastUserExactHash);
            this.lastAssistantExactHash = nz(lastAssistantExactHash);
            this.stopCandidateCount = Math.max(0, stopCandidateCount);
            this.generationActive = generationActive;
        }
    }

    static final class Observation {
        final State state;
        final boolean authoritativeReadAllowed;
        final boolean reloadRecommended;
        final boolean advancementProved;
        final String reason;

        Observation(State state,
                    boolean authoritativeReadAllowed,
                    boolean reloadRecommended,
                    boolean advancementProved,
                    String reason) {
            this.state = state;
            this.authoritativeReadAllowed = authoritativeReadAllowed;
            this.reloadRecommended = reloadRecommended;
            this.advancementProved = advancementProved;
            this.reason = reason;
        }
    }

    private final String expectedPathHash;
    private final Watermark baseline;
    private final boolean mustAdvance;
    private final int passiveBudget;

    private State state = State.WAIT_ROUTE;
    private String stableDigest = "";
    private int stableUserCount = -1;
    private int stableAssistantCount = -1;
    private int stableHits = 0;
    private int passiveSamples = 0;
    private boolean reloadConsumed = false;

    /**
     * @param expectedPathHash exact frozen conversation path hash
     * @param baseline prior durable watermark, or null when none exists
     * @param mustAdvance true for notification/expected-new-reply reads; stable
     *                    old DOM is not sufficient authority
     * @param passiveBudget number of converged/passive samples before one reload
     *                      escalation becomes eligible
     */
    WebChatFreshnessGuardV1(String expectedPathHash,
                            Watermark baseline,
                            boolean mustAdvance,
                            int passiveBudget) {
        if (empty(expectedPathHash)) throw new IllegalArgumentException("expected path hash required");
        if (mustAdvance && baseline == null)
            throw new IllegalArgumentException("mustAdvance requires a prior watermark");
        this.expectedPathHash = expectedPathHash;
        this.baseline = baseline;
        this.mustAdvance = mustAdvance;
        this.passiveBudget = Math.max(2, passiveBudget);
    }

    synchronized Observation observe(Snapshot s) {
        if (state == State.FRESH) return result(State.FRESH, true, false, advanced(s), "ALREADY_FRESH");
        if (state == State.UNCERTAIN || state == State.FRESHNESS_UNPROVEN)
            return result(state, false, false, false, "TERMINAL_NON_AUTHORITATIVE");
        if (s == null) return result(state, false, false, false, "NO_SNAPSHOT");

        passiveSamples++;

        if (!expectedPathHash.equals(s.pathHash)) {
            clearStability();
            state = State.WAIT_ROUTE;
            return result(state, false, false, false, "WAIT_EXACT_ROUTE");
        }
        if (!s.documentReadyComplete) {
            clearStability();
            state = State.WAIT_HYDRATION;
            return result(state, false, false, false, "DOCUMENT_NOT_COMPLETE");
        }
        if (s.generationActive || s.stopCandidateCount > 0) {
            clearStability();
            state = State.WAIT_HYDRATION;
            return result(state, false, false, false, "CONVERSATION_STILL_CHANGING");
        }
        if (empty(s.turnSequenceDigest)) {
            clearStability();
            state = State.WAIT_HYDRATION;
            return result(state, false, false, false, "TURN_SEQUENCE_NOT_MATERIALIZED");
        }

        if (sameStableCandidate(s)) stableHits++;
        else {
            stableDigest = s.turnSequenceDigest;
            stableUserCount = s.userTurnCount;
            stableAssistantCount = s.assistantTurnCount;
            stableHits = 1;
        }

        if (stableHits < 2) {
            state = State.WAIT_CONVERGENCE;
            return result(state, false, false, advanced(s), "STABLE_SAMPLE_1_OF_2");
        }

        boolean advanced = advanced(s);
        if (!mustAdvance || advanced) {
            state = State.FRESH;
            return result(state, true, false, advanced, mustAdvance ? "PASS_STABLE_ADVANCED_STATE" : "PASS_STABLE_OBSERVED_STATE");
        }

        state = State.WAIT_ADVANCE;
        if (!reloadConsumed && passiveSamples >= passiveBudget) {
            state = State.RELOAD_RECOMMENDED;
            return result(state, false, true, false, "STABLE_BUT_NOT_ADVANCED_RELOAD_ONCE");
        }
        if (reloadConsumed && passiveSamples >= passiveBudget * 2) {
            state = State.FRESHNESS_UNPROVEN;
            return result(state, false, false, false, "POST_RELOAD_ADVANCE_NOT_PROVED");
        }
        return result(state, false, false, false, "WAIT_POST_WATERMARK_ADVANCE");
    }

    /** Caller invokes this only after it has durably claimed and dispatched one
     * exact same-route reload/navigation. It does not mean the content is fresh;
     * subsequent observations must still converge and, when required, advance.
     */
    synchronized boolean markControlledReloadDispatched() {
        if (reloadConsumed || state != State.RELOAD_RECOMMENDED) return false;
        reloadConsumed = true;
        passiveSamples = 0;
        clearStability();
        state = State.WAIT_ROUTE;
        return true;
    }

    synchronized Observation markUncertain(String reason) {
        if (state != State.FRESH) state = State.UNCERTAIN;
        return result(state, state == State.FRESH, false, false,
                reason == null ? "UNCERTAIN" : reason);
    }

    synchronized State state() { return state; }

    private boolean advanced(Snapshot s) {
        if (baseline == null || s == null) return false;
        if (!expectedPathHash.equals(baseline.pathHash)) return false;
        if (s.userTurnCount > baseline.userTurnCount) return true;
        if (s.assistantTurnCount > baseline.assistantTurnCount) return true;
        if (!empty(baseline.turnSequenceDigest)
                && !baseline.turnSequenceDigest.equals(s.turnSequenceDigest)) return true;
        if (!empty(baseline.lastUserExactHash)
                && !baseline.lastUserExactHash.equals(s.lastUserExactHash)) return true;
        return !empty(baseline.lastAssistantExactHash)
                && !baseline.lastAssistantExactHash.equals(s.lastAssistantExactHash);
    }

    private boolean sameStableCandidate(Snapshot s) {
        return stableDigest.equals(s.turnSequenceDigest)
                && stableUserCount == s.userTurnCount
                && stableAssistantCount == s.assistantTurnCount;
    }

    private void clearStability() {
        stableDigest = "";
        stableUserCount = -1;
        stableAssistantCount = -1;
        stableHits = 0;
    }

    private static Observation result(State state,
                                      boolean allowed,
                                      boolean reload,
                                      boolean advanced,
                                      String reason) {
        return new Observation(state, allowed, reload, advanced, reason);
    }

    private static String nz(String s) { return s == null ? "" : s; }
    private static boolean empty(String s) { return s == null || s.length() == 0 || "-".equals(s); }
}
