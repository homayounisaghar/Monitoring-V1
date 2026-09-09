package com.homayounisaghar.chatgptwebviewprobe;

import android.content.SharedPreferences;

import org.json.JSONObject;

/**
 * Durable lifecycle journal for one disposable semantic Planner conversation.
 *
 * This journal is intentionally separate from target-effect workflow state.
 * A failed Temporary Chat cleanup must never erase an already-persisted
 * semantic result and must never authorize replay of a target effect.
 */
final class TemporaryPlannerJournalV1 {
    static final String IDLE = "IDLE";
    static final String CLAIMED_BEFORE_ENTER = "CLAIMED_BEFORE_ENTER";
    static final String TEMP_CONFIRMED = "TEMP_CONFIRMED";
    static final String CLAIMED_BEFORE_SEND = "CLAIMED_BEFORE_SEND";
    static final String PLANNER_SEND_IN_FLIGHT = "PLANNER_SEND_IN_FLIGHT";
    static final String WAITING_RESULT = "WAITING_RESULT";
    static final String RESULT_PERSISTED = "RESULT_PERSISTED";
    static final String CLAIMED_BEFORE_EXIT = "CLAIMED_BEFORE_EXIT";
    static final String NORMAL_CONFIRMED = "NORMAL_CONFIRMED";
    static final String CLEANUP_UNCERTAIN = "CLEANUP_UNCERTAIN";
    static final String FAILED_PRE_SEND = "FAILED_PRE_SEND";

    static final String RECOVERY_OBSERVE_ONLY = "OBSERVE_ONLY";
    static final String RECOVERY_RESULT_ONLY = "RESULT_ONLY_NO_REPLAY";
    static final String RECOVERY_CLEANUP_ONLY = "CLEANUP_ONLY";
    static final String RECOVERY_TERMINAL = "TERMINAL";

    private static final String KEY = "current_disposable_planner_v1";
    private final SharedPreferences prefs;

    TemporaryPlannerJournalV1(SharedPreferences prefs) {
        if (prefs == null) throw new IllegalArgumentException("prefs required");
        this.prefs = prefs;
    }

    synchronized boolean begin(String attemptId, String requestId, String requestDigest) {
        if (!safe(attemptId) || !safe(requestId) || requestDigest == null || requestDigest.length() < 16)
            return false;
        JSONObject current = load();
        if (current != null && !isTerminal(current.optString("state", ""))) return false;
        try {
            JSONObject j = new JSONObject();
            j.put("protocol", "cf-disposable-planner-journal.v1");
            j.put("attempt_id", attemptId);
            j.put("request_id", requestId);
            j.put("request_digest", requestDigest);
            j.put("state", CLAIMED_BEFORE_ENTER);
            j.put("planner_dispatch_count", 0);
            j.put("result_digest", JSONObject.NULL);
            j.put("revision", 1L);
            return save(j);
        } catch (Exception e) {
            return false;
        }
    }

    synchronized JSONObject load() {
        String raw = prefs.getString(KEY, null);
        if (raw == null) return null;
        try { return new JSONObject(raw); }
        catch (Exception e) { return null; }
    }

    synchronized boolean confirmTemp(String attemptId) {
        return transition(attemptId, CLAIMED_BEFORE_ENTER, TEMP_CONFIRMED);
    }

    synchronized boolean claimPlannerSend(String attemptId) {
        return transition(attemptId, TEMP_CONFIRMED, CLAIMED_BEFORE_SEND);
    }

    /** Call immediately before the one Planner Send click boundary. */
    synchronized boolean markPlannerSendInFlight(String attemptId) {
        JSONObject j = load();
        if (!matches(j, attemptId, CLAIMED_BEFORE_SEND)) return false;
        if (j.optInt("planner_dispatch_count", 0) != 0) return false;
        try {
            j.put("state", PLANNER_SEND_IN_FLIGHT);
            j.put("planner_dispatch_count", 1);
            bump(j);
            return save(j);
        } catch (Exception e) { return false; }
    }

    synchronized boolean markWaitingResult(String attemptId) {
        return transitionWithOneDispatch(attemptId, PLANNER_SEND_IN_FLIGHT, WAITING_RESULT);
    }

    /**
     * The semantic result must already be mechanically parsed/correlated and
     * durably copied into immutable local workflow/recipe data before this call.
     */
    synchronized boolean persistResultReceipt(String attemptId, String resultDigest) {
        if (resultDigest == null || resultDigest.length() < 16) return false;
        JSONObject j = load();
        if (!matches(j, attemptId, WAITING_RESULT)) return false;
        if (j.optInt("planner_dispatch_count", 0) != 1) return false;
        try {
            j.put("result_digest", resultDigest);
            j.put("state", RESULT_PERSISTED);
            bump(j);
            return save(j);
        } catch (Exception e) { return false; }
    }

    synchronized boolean claimExit(String attemptId) {
        return transition(attemptId, RESULT_PERSISTED, CLAIMED_BEFORE_EXIT);
    }

    synchronized boolean confirmNormal(String attemptId) {
        return transition(attemptId, CLAIMED_BEFORE_EXIT, NORMAL_CONFIRMED);
    }

    synchronized boolean markCleanupUncertain(String attemptId, String reason) {
        JSONObject j = load();
        if (j == null || !attemptId.equals(j.optString("attempt_id", ""))) return false;
        String state = j.optString("state", "");
        if (!RESULT_PERSISTED.equals(state) && !CLAIMED_BEFORE_EXIT.equals(state)
                && !CLEANUP_UNCERTAIN.equals(state)) return false;
        try {
            j.put("state", CLEANUP_UNCERTAIN);
            j.put("cleanup_error", reason == null ? "UNKNOWN" : reason);
            bump(j);
            return save(j);
        } catch (Exception e) { return false; }
    }

    synchronized boolean failPreSend(String attemptId, String reason) {
        JSONObject j = load();
        if (j == null || !attemptId.equals(j.optString("attempt_id", ""))) return false;
        String state = j.optString("state", "");
        if (j.optInt("planner_dispatch_count", 0) != 0) return false;
        if (!CLAIMED_BEFORE_ENTER.equals(state) && !TEMP_CONFIRMED.equals(state)
                && !CLAIMED_BEFORE_SEND.equals(state)) return false;
        try {
            j.put("state", FAILED_PRE_SEND);
            j.put("error", reason == null ? "UNKNOWN" : reason);
            bump(j);
            return save(j);
        } catch (Exception e) { return false; }
    }

    synchronized String recoveryMode() {
        JSONObject j = load();
        if (j == null) return RECOVERY_TERMINAL;
        String state = j.optString("state", "");
        if (PLANNER_SEND_IN_FLIGHT.equals(state) || WAITING_RESULT.equals(state))
            return RECOVERY_RESULT_ONLY;
        if (RESULT_PERSISTED.equals(state) || CLAIMED_BEFORE_EXIT.equals(state)
                || CLEANUP_UNCERTAIN.equals(state)) return RECOVERY_CLEANUP_ONLY;
        if (CLAIMED_BEFORE_ENTER.equals(state) || TEMP_CONFIRMED.equals(state)
                || CLAIMED_BEFORE_SEND.equals(state)) return RECOVERY_OBSERVE_ONLY;
        return RECOVERY_TERMINAL;
    }

    synchronized boolean hasPersistedResult() {
        JSONObject j = load();
        if (j == null) return false;
        String state = j.optString("state", "");
        return RESULT_PERSISTED.equals(state) || CLAIMED_BEFORE_EXIT.equals(state)
                || NORMAL_CONFIRMED.equals(state) || CLEANUP_UNCERTAIN.equals(state);
    }

    private boolean transition(String attemptId, String expected, String next) {
        JSONObject j = load();
        if (!matches(j, attemptId, expected)) return false;
        try { j.put("state", next); bump(j); return save(j); }
        catch (Exception e) { return false; }
    }

    private boolean transitionWithOneDispatch(String attemptId, String expected, String next) {
        JSONObject j = load();
        if (!matches(j, attemptId, expected) || j.optInt("planner_dispatch_count", 0) != 1) return false;
        try { j.put("state", next); bump(j); return save(j); }
        catch (Exception e) { return false; }
    }

    private static boolean matches(JSONObject j, String attemptId, String state) {
        return j != null && attemptId != null && attemptId.equals(j.optString("attempt_id", ""))
                && state.equals(j.optString("state", ""));
    }

    private static boolean isTerminal(String state) {
        return NORMAL_CONFIRMED.equals(state) || FAILED_PRE_SEND.equals(state);
    }

    private static boolean safe(String s) {
        return s != null && s.length() >= 8 && s.length() <= 128 && s.matches("[A-Za-z0-9._:-]+");
    }

    private static void bump(JSONObject j) throws Exception {
        j.put("revision", j.optLong("revision", 0L) + 1L);
    }

    private boolean save(JSONObject j) {
        return prefs.edit().putString(KEY, j.toString()).commit();
    }
}
