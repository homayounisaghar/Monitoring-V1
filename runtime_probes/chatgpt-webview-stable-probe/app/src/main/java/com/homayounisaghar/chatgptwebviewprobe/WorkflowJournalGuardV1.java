package com.homayounisaghar.chatgptwebviewprobe;

import android.content.SharedPreferences;

import org.json.JSONObject;

/**
 * Safety facade over the first workflow journal implementation.
 *
 * The underlying journal intentionally exposes low-level transition helpers for
 * infrastructure work. Material execution uses this facade so an uncertain or
 * post-dispatch step cannot later be downgraded to ordinary FAILED, and an
 * effectful step cannot be declared SUCCEEDED from CLAIMED without a receipt.
 */
final class WorkflowJournalGuardV1 {
    private final WorkflowJournalV1 journal;

    WorkflowJournalGuardV1(SharedPreferences prefs) {
        journal = new WorkflowJournalV1(prefs);
    }

    boolean create(JSONObject plan, String planDigest) {
        return journal.create(plan, planDigest);
    }

    JSONObject load(String workflowId) {
        return journal.load(workflowId);
    }

    boolean claimEffect(String workflowId, String stepId, String effectId) {
        return journal.claimEffect(workflowId, stepId, effectId);
    }

    boolean markDispatchInFlight(String workflowId, String stepId, String effectId) {
        return journal.markDispatchInFlight(workflowId, stepId, effectId);
    }

    boolean markWaitingReceipt(String workflowId, String stepId, String effectId) {
        return journal.markWaitingReceipt(workflowId, stepId, effectId);
    }

    boolean confirmReceipt(String workflowId, String stepId, String effectId, String receiptDigest) {
        return journal.confirmReceipt(workflowId, stepId, effectId, receiptDigest);
    }

    boolean captureExactTextOutput(String workflowId, String stepId, String outputName, String exactText) {
        return journal.captureExactTextOutput(workflowId, stepId, outputName, exactText);
    }

    String exactTextOutput(String workflowId, String stepId, String outputName) {
        return journal.exactTextOutput(workflowId, stepId, outputName);
    }

    boolean markStepSucceeded(String workflowId, String stepId) {
        String state = stepState(workflowId, stepId);
        if (!WorkflowJournalV1.STEP_RECEIPT_CONFIRMED.equals(state)
                && !WorkflowJournalV1.STEP_OUTPUT_CAPTURED.equals(state)) return false;
        return journal.markStepSucceeded(workflowId, stepId);
    }

    boolean markStepFailed(String workflowId, String stepId, String errorClass) {
        String state = stepState(workflowId, stepId);
        if (WorkflowJournalV1.STEP_DISPATCH_IN_FLIGHT.equals(state)
                || WorkflowJournalV1.STEP_WAITING_RECEIPT.equals(state)
                || WorkflowJournalV1.STEP_RECEIPT_CONFIRMED.equals(state)
                || WorkflowJournalV1.STEP_OUTPUT_CAPTURED.equals(state)
                || WorkflowJournalV1.STEP_UNCERTAIN.equals(state)
                || WorkflowJournalV1.STEP_SUCCEEDED.equals(state)) return false;
        return journal.markStepFailed(workflowId, stepId, errorClass);
    }

    boolean markStepUncertain(String workflowId, String stepId, String reason) {
        String state = stepState(workflowId, stepId);
        if (WorkflowJournalV1.STEP_SUCCEEDED.equals(state)
                || WorkflowJournalV1.STEP_FAILED.equals(state)) return false;
        return journal.markStepUncertain(workflowId, stepId, reason);
    }

    String recoveryMode(String workflowId, String stepId) {
        String state = stepState(workflowId, stepId);
        if (WorkflowJournalV1.STEP_UNCERTAIN.equals(state))
            return WorkflowJournalV1.RECOVERY_RECONCILE_ONLY;
        return journal.recoveryMode(workflowId, stepId);
    }

    private String stepState(String workflowId, String stepId) {
        try {
            JSONObject j = journal.load(workflowId);
            if (j == null) return "";
            return j.getJSONObject("steps").getJSONObject(stepId).optString("state", "");
        } catch (Exception e) {
            return "";
        }
    }
}
