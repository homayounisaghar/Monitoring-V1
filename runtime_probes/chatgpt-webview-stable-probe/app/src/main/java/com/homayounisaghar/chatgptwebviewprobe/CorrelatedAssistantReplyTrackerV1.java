package com.homayounisaghar.chatgptwebviewprobe;

/**
 * Pure mechanical correlation for an assistant reply that follows one exact
 * user turn in one frozen target conversation.
 *
 * This tracker never chooses a chat and never interprets reply meaning. It only
 * proves sequence/identity/completion from already-sanitized local DOM
 * observations and returns exact reply text for immutable workflow capture.
 */
final class CorrelatedAssistantReplyTrackerV1 {
    enum State {
        WAIT_USER_RECEIPT,
        WAIT_ASSISTANT_START,
        WAIT_ASSISTANT_STABLE,
        CAPTURED,
        UNCERTAIN
    }

    static final class Snapshot {
        final String pathHash;
        final int userTurnCount;
        final int assistantTurnCount;
        final String lastUserExactHash;
        final String lastAssistantExactHash;
        final String lastAssistantExactText;
        final int stopCandidateCount;
        final int completionCandidateCount;

        Snapshot(String pathHash,
                 int userTurnCount,
                 int assistantTurnCount,
                 String lastUserExactHash,
                 String lastAssistantExactHash,
                 String lastAssistantExactText,
                 int stopCandidateCount,
                 int completionCandidateCount) {
            this.pathHash = nz(pathHash);
            this.userTurnCount = userTurnCount;
            this.assistantTurnCount = assistantTurnCount;
            this.lastUserExactHash = nz(lastUserExactHash);
            this.lastAssistantExactHash = nz(lastAssistantExactHash);
            this.lastAssistantExactText = ExactTextV1.canonical(lastAssistantExactText);
            this.stopCandidateCount = stopCandidateCount;
            this.completionCandidateCount = completionCandidateCount;
        }
    }

    static final class Observation {
        final State state;
        final boolean userReceiptConfirmed;
        final boolean assistantStarted;
        final boolean captured;
        final String exactReplyText;
        final String exactReplySha256;
        final String reason;

        Observation(State state, boolean userReceiptConfirmed, boolean assistantStarted,
                    boolean captured, String exactReplyText, String exactReplySha256, String reason) {
            this.state = state;
            this.userReceiptConfirmed = userReceiptConfirmed;
            this.assistantStarted = assistantStarted;
            this.captured = captured;
            this.exactReplyText = exactReplyText;
            this.exactReplySha256 = exactReplySha256;
            this.reason = reason;
        }
    }

    private final String targetPathHash;
    private final String expectedUserExactHash;
    private final int baselineUserTurnCount;
    private final int baselineAssistantTurnCount;
    private final String baselineAssistantExactHash;

    private State state = State.WAIT_USER_RECEIPT;
    private boolean userReceipt;
    private boolean assistantStarted;
    private String stableAssistantExactHash = "";
    private String stableAssistantExactText = "";
    private int stableHits;

    CorrelatedAssistantReplyTrackerV1(String targetPathHash,
                                      String expectedUserExactHash,
                                      int baselineUserTurnCount,
                                      int baselineAssistantTurnCount,
                                      String baselineAssistantExactHash) {
        if (empty(targetPathHash) || empty(expectedUserExactHash))
            throw new IllegalArgumentException("target and exact user hash required");
        this.targetPathHash = targetPathHash;
        this.expectedUserExactHash = expectedUserExactHash;
        this.baselineUserTurnCount = baselineUserTurnCount;
        this.baselineAssistantTurnCount = baselineAssistantTurnCount;
        this.baselineAssistantExactHash = nz(baselineAssistantExactHash);
    }

    synchronized Observation observe(Snapshot s) {
        if (state == State.CAPTURED) return captured("ALREADY_CAPTURED");
        if (state == State.UNCERTAIN) return current(false, "ALREADY_UNCERTAIN");
        if (s == null) return current(false, "NO_SNAPSHOT");

        if (!targetPathHash.equals(s.pathHash)) {
            state = State.UNCERTAIN;
            return current(false, "TARGET_PATH_HASH_DRIFT");
        }

        if (!userReceipt) {
            boolean exactUser = expectedUserExactHash.equals(s.lastUserExactHash)
                    && s.userTurnCount >= baselineUserTurnCount + 1;
            if (!exactUser) return current(false, "WAIT_EXACT_USER_RECEIPT");
            userReceipt = true;
            state = State.WAIT_ASSISTANT_START;
        }

        // Once correlated user receipt exists, it must remain the last user turn
        // while we capture its assistant answer. A later user message makes the
        // relation ambiguous instead of silently rebinding the tracker.
        if (!expectedUserExactHash.equals(s.lastUserExactHash)) {
            state = State.UNCERTAIN;
            return current(false, "CORRELATED_USER_NO_LONGER_LAST_USER");
        }

        boolean newAssistant = s.assistantTurnCount >= baselineAssistantTurnCount + 1
                && !empty(s.lastAssistantExactHash)
                && !s.lastAssistantExactHash.equals(baselineAssistantExactHash);
        if (!assistantStarted) {
            if (!newAssistant) return current(false, "WAIT_ASSISTANT_START");
            assistantStarted = true;
            state = State.WAIT_ASSISTANT_STABLE;
            stableAssistantExactHash = "";
            stableAssistantExactText = "";
            stableHits = 0;
        }

        if (s.stopCandidateCount > 0) {
            stableAssistantExactHash = "";
            stableAssistantExactText = "";
            stableHits = 0;
            return current(false, "ASSISTANT_STILL_GENERATING");
        }

        // Completion control is an independent DOM receipt that the final turn
        // action bar exists. Require it as well as two identical exact samples.
        if (s.completionCandidateCount < 1 || empty(s.lastAssistantExactHash)
                || s.lastAssistantExactText.length() == 0) {
            stableHits = 0;
            return current(false, "WAIT_COMPLETION_RECEIPT");
        }

        String localDigest = ExactTextV1.sha256(s.lastAssistantExactText);
        if (!s.lastAssistantExactHash.equals(localDigest)) {
            state = State.UNCERTAIN;
            return current(false, "ASSISTANT_TEXT_HASH_MISMATCH");
        }

        if (s.lastAssistantExactHash.equals(stableAssistantExactHash)
                && s.lastAssistantExactText.equals(stableAssistantExactText)) {
            stableHits++;
        } else {
            stableAssistantExactHash = s.lastAssistantExactHash;
            stableAssistantExactText = s.lastAssistantExactText;
            stableHits = 1;
        }

        if (stableHits < 2) return current(false, "FINAL_CANDIDATE_1_OF_2");
        state = State.CAPTURED;
        return captured("PASS_CORRELATED_STABLE_ASSISTANT_REPLY");
    }

    synchronized State state() { return state; }

    synchronized Observation markUncertain(String reason) {
        if (state != State.CAPTURED) state = State.UNCERTAIN;
        return current(false, reason == null ? "UNCERTAIN" : reason);
    }

    private Observation captured(String reason) {
        return new Observation(State.CAPTURED, true, true, true,
                stableAssistantExactText, ExactTextV1.sha256(stableAssistantExactText), reason);
    }

    private Observation current(boolean captured, String reason) {
        return new Observation(state, userReceipt, assistantStarted, captured,
                captured ? stableAssistantExactText : "",
                captured ? ExactTextV1.sha256(stableAssistantExactText) : "", reason);
    }

    private static String nz(String s) { return s == null ? "" : s; }
    private static boolean empty(String s) { return s == null || s.length() == 0 || "-".equals(s); }
}
