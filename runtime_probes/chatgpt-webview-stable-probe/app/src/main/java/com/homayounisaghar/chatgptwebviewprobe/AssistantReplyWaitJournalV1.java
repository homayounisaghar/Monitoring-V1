package com.homayounisaghar.chatgptwebviewprobe;

import android.content.SharedPreferences;

import org.json.JSONObject;

/**
 * Durable metadata for waiting on the assistant reply correlated to one exact
 * previously-dispatched user turn. This journal performs no DOM access; it
 * persists only the frozen correlation anchors needed to reconstruct
 * CorrelatedAssistantReplyTrackerV1 after process restart.
 */
final class AssistantReplyWaitJournalV1 {
    static final String ARMED = "ARMED";
    static final String USER_RECEIPT_CONFIRMED = "USER_RECEIPT_CONFIRMED";
    static final String ASSISTANT_STARTED = "ASSISTANT_STARTED";
    static final String WAITING_STABLE = "WAITING_STABLE";
    static final String REPLY_CAPTURED = "REPLY_CAPTURED";
    static final String UNCERTAIN = "UNCERTAIN";
    static final String EXPIRED = "EXPIRED";

    private static final String PREFIX = "cf_reply_wait_v1_";
    private final SharedPreferences prefs;

    AssistantReplyWaitJournalV1(SharedPreferences prefs) {
        if (prefs == null) throw new IllegalArgumentException("prefs required");
        this.prefs = prefs;
    }

    synchronized boolean arm(String workflowId,
                             String stepId,
                             String targetPathHash,
                             String expectedUserExactHash,
                             int baselineUserTurnCount,
                             int baselineAssistantTurnCount,
                             String baselineAssistantExactHash,
                             long expiresAtEpochMs) {
        if (!safe(workflowId) || !safe(stepId) || empty(targetPathHash)
                || empty(expectedUserExactHash) || expiresAtEpochMs <= System.currentTimeMillis()) return false;
        String key = key(workflowId, stepId);
        if (prefs.contains(key)) return false;
        try {
            JSONObject j = new JSONObject();
            j.put("protocol", "cf-assistant-reply-wait.v1");
            j.put("workflow_id", workflowId);
            j.put("step_id", stepId);
            j.put("target_path_hash", targetPathHash);
            j.put("expected_user_exact_hash", expectedUserExactHash);
            j.put("baseline_user_turn_count", baselineUserTurnCount);
            j.put("baseline_assistant_turn_count", baselineAssistantTurnCount);
            j.put("baseline_assistant_exact_hash", nz(baselineAssistantExactHash));
            j.put("expires_at_epoch_ms", expiresAtEpochMs);
            j.put("state", ARMED);
            j.put("reply_exact_sha256", JSONObject.NULL);
            j.put("reply_exact_text", JSONObject.NULL);
            j.put("revision", 1L);
            return prefs.edit().putString(key, j.toString()).commit();
        } catch (Exception e) { return false; }
    }

    synchronized JSONObject load(String workflowId, String stepId) {
        String raw = prefs.getString(key(workflowId, stepId), null);
        if (raw == null) return null;
        try { return new JSONObject(raw); }
        catch (Exception e) { return null; }
    }

    synchronized CorrelatedAssistantReplyTrackerV1 restoreTracker(String workflowId, String stepId) {
        JSONObject j = load(workflowId, stepId);
        if (j == null || terminal(j.optString("state", ""))) return null;
        if (expired(j)) {
            markExpired(workflowId, stepId);
            return null;
        }
        try {
            return new CorrelatedAssistantReplyTrackerV1(
                    j.getString("target_path_hash"),
                    j.getString("expected_user_exact_hash"),
                    j.getInt("baseline_user_turn_count"),
                    j.getInt("baseline_assistant_turn_count"),
                    j.optString("baseline_assistant_exact_hash", ""));
        } catch (Exception e) { return null; }
    }

    synchronized boolean applyObservation(String workflowId, String stepId,
                                          CorrelatedAssistantReplyTrackerV1.Observation o) {
        if (o == null) return false;
        JSONObject j = load(workflowId, stepId);
        if (j == null || terminal(j.optString("state", ""))) return false;
        if (expired(j)) return markExpired(workflowId, stepId);
        try {
            if (o.state == CorrelatedAssistantReplyTrackerV1.State.UNCERTAIN) {
                j.put("state", UNCERTAIN);
                j.put("last_reason", o.reason);
            } else if (o.captured) {
                String exact = ExactTextV1.canonical(o.exactReplyText);
                String digest = ExactTextV1.sha256(exact);
                if (!digest.equals(o.exactReplySha256)) return false;
                j.put("reply_exact_text", exact);
                j.put("reply_exact_sha256", digest);
                j.put("state", REPLY_CAPTURED);
                j.put("last_reason", o.reason);
            } else if (o.assistantStarted) {
                j.put("state", WAITING_STABLE);
                j.put("last_reason", o.reason);
            } else if (o.userReceiptConfirmed) {
                j.put("state", USER_RECEIPT_CONFIRMED);
                j.put("last_reason", o.reason);
            } else {
                j.put("state", ARMED);
                j.put("last_reason", o.reason);
            }
            bump(j);
            return save(workflowId, stepId, j);
        } catch (Exception e) { return false; }
    }

    synchronized String capturedReply(String workflowId, String stepId) {
        JSONObject j = load(workflowId, stepId);
        if (j == null || !REPLY_CAPTURED.equals(j.optString("state", ""))) return null;
        try {
            String text = j.getString("reply_exact_text");
            String digest = j.getString("reply_exact_sha256");
            return ExactTextV1.sha256(text).equals(digest) ? text : null;
        } catch (Exception e) { return null; }
    }

    synchronized boolean markUncertain(String workflowId, String stepId, String reason) {
        JSONObject j = load(workflowId, stepId);
        if (j == null || REPLY_CAPTURED.equals(j.optString("state", ""))) return false;
        try {
            j.put("state", UNCERTAIN);
            j.put("last_reason", reason == null ? "UNCERTAIN" : reason);
            bump(j);
            return save(workflowId, stepId, j);
        } catch (Exception e) { return false; }
    }

    synchronized boolean markExpired(String workflowId, String stepId) {
        JSONObject j = load(workflowId, stepId);
        if (j == null || terminal(j.optString("state", ""))) return false;
        try {
            j.put("state", EXPIRED);
            j.put("last_reason", "WAIT_EXPIRED");
            bump(j);
            return save(workflowId, stepId, j);
        } catch (Exception e) { return false; }
    }

    private static boolean expired(JSONObject j) {
        return System.currentTimeMillis() >= j.optLong("expires_at_epoch_ms", Long.MAX_VALUE);
    }

    private static boolean terminal(String state) {
        return REPLY_CAPTURED.equals(state) || UNCERTAIN.equals(state) || EXPIRED.equals(state);
    }

    private boolean save(String workflowId, String stepId, JSONObject j) {
        return prefs.edit().putString(key(workflowId, stepId), j.toString()).commit();
    }

    private static String key(String workflowId, String stepId) {
        return PREFIX + workflowId + "__" + stepId;
    }

    private static void bump(JSONObject j) throws Exception {
        j.put("revision", j.optLong("revision", 0L) + 1L);
    }

    private static boolean safe(String s) {
        return s != null && s.length() >= 1 && s.length() <= 128 && s.matches("[A-Za-z0-9._:-]+");
    }
    private static boolean empty(String s) { return s == null || s.length() == 0 || "-".equals(s); }
    private static String nz(String s) { return s == null ? "" : s; }
}
