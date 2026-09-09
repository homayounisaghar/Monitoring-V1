package com.homayounisaghar.chatgptwebviewprobe;

import android.content.SharedPreferences;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Durable mechanical workflow state for the first-usable-assistant line.
 *
 * This class deliberately contains no semantic intent logic. It persists one
 * accepted candidate plan, step/effect identities, receipts and exact outputs
 * so orchestration can survive Activity/process restart without replaying a
 * possibly dispatched material effect.
 */
final class WorkflowJournalV1 {
    static final String WF_PENDING = "PENDING";
    static final String WF_RUNNING = "RUNNING";
    static final String WF_WAITING = "WAITING";
    static final String WF_NEEDS_USER = "NEEDS_USER";
    static final String WF_SUCCEEDED = "SUCCEEDED";
    static final String WF_FAILED = "FAILED";
    static final String WF_UNCERTAIN = "UNCERTAIN";

    static final String STEP_BLOCKED = "BLOCKED";
    static final String STEP_ELIGIBLE = "ELIGIBLE";
    static final String STEP_CLAIMED = "CLAIMED";
    static final String STEP_DISPATCH_IN_FLIGHT = "DISPATCH_IN_FLIGHT";
    static final String STEP_WAITING_RECEIPT = "WAITING_RECEIPT";
    static final String STEP_RECEIPT_CONFIRMED = "RECEIPT_CONFIRMED";
    static final String STEP_OUTPUT_CAPTURED = "OUTPUT_CAPTURED";
    static final String STEP_SUCCEEDED = "SUCCEEDED";
    static final String STEP_FAILED = "FAILED";
    static final String STEP_UNCERTAIN = "UNCERTAIN";

    static final String RECOVERY_RECONCILE_ONLY = "RECONCILE_ONLY";
    static final String RECOVERY_PRE_DISPATCH = "PRE_DISPATCH_SAFE";
    static final String RECOVERY_TERMINAL = "TERMINAL";
    static final String RECOVERY_NORMAL = "NORMAL";

    private static final String PREFIX = "cf_workflow_v1_";
    private final SharedPreferences prefs;

    WorkflowJournalV1(SharedPreferences prefs) {
        if (prefs == null) throw new IllegalArgumentException("prefs required");
        this.prefs = prefs;
    }

    synchronized boolean create(JSONObject plan, String planDigest) {
        try {
            validatePlanShape(plan);
            String workflowId = plan.getString("workflow_id");
            String key = key(workflowId);
            if (prefs.contains(key)) return false;

            JSONObject journal = new JSONObject();
            journal.put("journal_protocol", "cf-workflow-journal.v1");
            journal.put("workflow_id", workflowId);
            journal.put("request_id", plan.getString("request_id"));
            journal.put("request_digest", plan.getString("request_digest"));
            journal.put("plan_digest", planDigest == null ? "" : planDigest);
            journal.put("workflow_state", WF_PENDING);
            journal.put("revision", 1L);
            journal.put("plan", new JSONObject(plan.toString()));
            journal.put("outputs", new JSONObject());

            JSONObject runtime = new JSONObject();
            JSONArray steps = plan.getJSONArray("steps");
            Set<String> initialEligible = rootStepIds(steps);
            for (int i = 0; i < steps.length(); i++) {
                JSONObject spec = steps.getJSONObject(i);
                String stepId = spec.getString("step_id");
                JSONObject s = new JSONObject();
                s.put("state", initialEligible.contains(stepId) ? STEP_ELIGIBLE : STEP_BLOCKED);
                s.put("effect_id", JSONObject.NULL);
                s.put("receipt_digest", JSONObject.NULL);
                s.put("dispatch_count", 0);
                s.put("last_error", JSONObject.NULL);
                runtime.put(stepId, s);
            }
            journal.put("steps", runtime);
            return persistNew(key, journal);
        } catch (Exception e) {
            return false;
        }
    }

    synchronized JSONObject load(String workflowId) {
        String raw = prefs.getString(key(workflowId), null);
        if (raw == null) return null;
        try {
            return new JSONObject(raw);
        } catch (Exception e) {
            return null;
        }
    }

    synchronized boolean setWorkflowState(String workflowId, String expected, String next) {
        JSONObject j = load(workflowId);
        if (j == null || !expected.equals(j.optString("workflow_state", ""))) return false;
        try {
            j.put("workflow_state", next);
            bump(j);
            return persistExisting(key(workflowId), j);
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Persist CLAIMED before any material target navigation/write/send boundary.
     * The immutable effectId must be reused for all later recovery of this step.
     */
    synchronized boolean claimEffect(String workflowId, String stepId, String effectId) {
        if (effectId == null || effectId.length() < 8) return false;
        JSONObject j = load(workflowId);
        if (j == null) return false;
        try {
            JSONObject s = stepRuntime(j, stepId);
            if (!STEP_ELIGIBLE.equals(s.getString("state"))) return false;
            Object previous = s.opt("effect_id");
            if (previous != null && previous != JSONObject.NULL && !effectId.equals(String.valueOf(previous))) return false;
            s.put("effect_id", effectId);
            s.put("state", STEP_CLAIMED);
            j.put("workflow_state", WF_RUNNING);
            bump(j);
            return persistExisting(key(workflowId), j);
        } catch (Exception e) {
            return false;
        }
    }

    synchronized boolean markDispatchInFlight(String workflowId, String stepId, String effectId) {
        JSONObject j = load(workflowId);
        if (j == null) return false;
        try {
            JSONObject s = stepRuntime(j, stepId);
            if (!STEP_CLAIMED.equals(s.getString("state"))) return false;
            if (!effectId.equals(s.optString("effect_id", ""))) return false;
            if (s.optInt("dispatch_count", 0) != 0) return false;
            s.put("state", STEP_DISPATCH_IN_FLIGHT);
            s.put("dispatch_count", 1);
            bump(j);
            return persistExisting(key(workflowId), j);
        } catch (Exception e) {
            return false;
        }
    }

    synchronized boolean markWaitingReceipt(String workflowId, String stepId, String effectId) {
        return transitionEffectState(workflowId, stepId, effectId,
                STEP_DISPATCH_IN_FLIGHT, STEP_WAITING_RECEIPT, null);
    }

    synchronized boolean confirmReceipt(String workflowId, String stepId, String effectId, String receiptDigest) {
        if (receiptDigest == null || receiptDigest.length() < 8) return false;
        return transitionEffectState(workflowId, stepId, effectId,
                STEP_WAITING_RECEIPT, STEP_RECEIPT_CONFIRMED, receiptDigest);
    }

    synchronized boolean captureExactTextOutput(String workflowId, String stepId, String outputName, String exactText) {
        if (!safeId(outputName)) return false;
        JSONObject j = load(workflowId);
        if (j == null) return false;
        try {
            JSONObject s = stepRuntime(j, stepId);
            String state = s.getString("state");
            if (!STEP_RECEIPT_CONFIRMED.equals(state) && !STEP_OUTPUT_CAPTURED.equals(state)) return false;

            JSONObject outputs = j.getJSONObject("outputs");
            JSONObject perStep = outputs.optJSONObject(stepId);
            if (perStep == null) {
                perStep = new JSONObject();
                outputs.put(stepId, perStep);
            }
            if (perStep.has(outputName)) return false; // immutable once captured

            String canonical = ExactTextV1.canonical(exactText);
            JSONObject item = new JSONObject();
            item.put("kind", "EXACT_TEXT");
            item.put("value", canonical);
            item.put("sha256", ExactTextV1.sha256(canonical));
            perStep.put(outputName, item);
            s.put("state", STEP_OUTPUT_CAPTURED);
            bump(j);
            return persistExisting(key(workflowId), j);
        } catch (Exception e) {
            return false;
        }
    }

    synchronized String exactTextOutput(String workflowId, String stepId, String outputName) {
        JSONObject j = load(workflowId);
        if (j == null) return null;
        try {
            JSONObject item = j.getJSONObject("outputs").getJSONObject(stepId).getJSONObject(outputName);
            if (!"EXACT_TEXT".equals(item.getString("kind"))) return null;
            String value = item.getString("value");
            if (!ExactTextV1.sha256(value).equals(item.getString("sha256"))) return null;
            return value;
        } catch (Exception e) {
            return null;
        }
    }

    synchronized boolean markStepSucceeded(String workflowId, String stepId) {
        JSONObject j = load(workflowId);
        if (j == null) return false;
        try {
            JSONObject s = stepRuntime(j, stepId);
            String state = s.getString("state");
            if (!STEP_RECEIPT_CONFIRMED.equals(state) && !STEP_OUTPUT_CAPTURED.equals(state)
                    && !STEP_CLAIMED.equals(state)) return false;
            s.put("state", STEP_SUCCEEDED);
            recomputeEligibility(j);
            if (allStepsSucceeded(j)) j.put("workflow_state", WF_SUCCEEDED);
            else j.put("workflow_state", hasWaitingWork(j) ? WF_WAITING : WF_RUNNING);
            bump(j);
            return persistExisting(key(workflowId), j);
        } catch (Exception e) {
            return false;
        }
    }

    synchronized boolean markStepFailed(String workflowId, String stepId, String errorClass) {
        JSONObject j = load(workflowId);
        if (j == null) return false;
        try {
            JSONObject s = stepRuntime(j, stepId);
            String state = s.optString("state", "");
            if (STEP_SUCCEEDED.equals(state) || STEP_FAILED.equals(state)) return false;
            s.put("state", STEP_FAILED);
            s.put("last_error", errorClass == null ? "UNKNOWN" : errorClass);
            j.put("workflow_state", WF_FAILED);
            bump(j);
            return persistExisting(key(workflowId), j);
        } catch (Exception e) {
            return false;
        }
    }

    synchronized boolean markStepUncertain(String workflowId, String stepId, String reason) {
        JSONObject j = load(workflowId);
        if (j == null) return false;
        try {
            JSONObject s = stepRuntime(j, stepId);
            String state = s.optString("state", "");
            if (STEP_SUCCEEDED.equals(state) || STEP_FAILED.equals(state)) return false;
            s.put("state", STEP_UNCERTAIN);
            s.put("last_error", reason == null ? "UNCERTAIN" : reason);
            j.put("workflow_state", WF_UNCERTAIN);
            bump(j);
            return persistExisting(key(workflowId), j);
        } catch (Exception e) {
            return false;
        }
    }

    synchronized List<String> eligibleStepIds(String workflowId) {
        List<String> out = new ArrayList<String>();
        JSONObject j = load(workflowId);
        if (j == null) return out;
        try {
            recomputeEligibility(j);
            JSONObject runtime = j.getJSONObject("steps");
            JSONArray names = runtime.names();
            if (names != null) {
                for (int i = 0; i < names.length(); i++) {
                    String id = names.getString(i);
                    if (STEP_ELIGIBLE.equals(runtime.getJSONObject(id).optString("state", ""))) out.add(id);
                }
            }
            bump(j);
            persistExisting(key(workflowId), j);
        } catch (Exception ignored) {}
        return out;
    }

    synchronized String recoveryMode(String workflowId, String stepId) {
        JSONObject j = load(workflowId);
        if (j == null) return RECOVERY_NORMAL;
        try {
            String state = stepRuntime(j, stepId).getString("state");
            if (STEP_DISPATCH_IN_FLIGHT.equals(state) || STEP_WAITING_RECEIPT.equals(state))
                return RECOVERY_RECONCILE_ONLY;
            if (STEP_CLAIMED.equals(state)) return RECOVERY_PRE_DISPATCH;
            if (STEP_SUCCEEDED.equals(state) || STEP_FAILED.equals(state)) return RECOVERY_TERMINAL;
            return RECOVERY_NORMAL;
        } catch (Exception e) {
            return RECOVERY_NORMAL;
        }
    }

    private boolean transitionEffectState(String workflowId, String stepId, String effectId,
                                          String expected, String next, String receiptDigest) {
        JSONObject j = load(workflowId);
        if (j == null) return false;
        try {
            JSONObject s = stepRuntime(j, stepId);
            if (!expected.equals(s.getString("state"))) return false;
            if (!effectId.equals(s.optString("effect_id", ""))) return false;
            if (s.optInt("dispatch_count", 0) != 1) return false;
            s.put("state", next);
            if (receiptDigest != null) s.put("receipt_digest", receiptDigest);
            j.put("workflow_state", STEP_WAITING_RECEIPT.equals(next) ? WF_WAITING : WF_RUNNING);
            bump(j);
            return persistExisting(key(workflowId), j);
        } catch (Exception e) {
            return false;
        }
    }

    private static JSONObject stepRuntime(JSONObject journal, String stepId) throws JSONException {
        return journal.getJSONObject("steps").getJSONObject(stepId);
    }

    private static void recomputeEligibility(JSONObject journal) throws JSONException {
        JSONObject plan = journal.getJSONObject("plan");
        JSONArray specs = plan.getJSONArray("steps");
        JSONObject runtime = journal.getJSONObject("steps");
        for (int i = 0; i < specs.length(); i++) {
            JSONObject spec = specs.getJSONObject(i);
            String id = spec.getString("step_id");
            JSONObject r = runtime.getJSONObject(id);
            if (!STEP_BLOCKED.equals(r.optString("state", ""))) continue;
            JSONArray deps = spec.getJSONArray("depends_on");
            boolean ready = true;
            for (int d = 0; d < deps.length(); d++) {
                String dep = deps.getString(d);
                if (!STEP_SUCCEEDED.equals(runtime.getJSONObject(dep).optString("state", ""))) {
                    ready = false;
                    break;
                }
            }
            if (ready) r.put("state", STEP_ELIGIBLE);
        }
    }

    private static boolean allStepsSucceeded(JSONObject journal) throws JSONException {
        JSONObject runtime = journal.getJSONObject("steps");
        JSONArray names = runtime.names();
        if (names == null || names.length() == 0) return false;
        for (int i = 0; i < names.length(); i++) {
            if (!STEP_SUCCEEDED.equals(runtime.getJSONObject(names.getString(i)).optString("state", ""))) return false;
        }
        return true;
    }

    private static boolean hasWaitingWork(JSONObject journal) throws JSONException {
        JSONObject runtime = journal.getJSONObject("steps");
        JSONArray names = runtime.names();
        if (names == null) return false;
        for (int i = 0; i < names.length(); i++) {
            String s = runtime.getJSONObject(names.getString(i)).optString("state", "");
            if (STEP_WAITING_RECEIPT.equals(s) || STEP_BLOCKED.equals(s)) return true;
        }
        return false;
    }

    /** Mechanical structural checks only; full JSON Schema/capability checks stay outside. */
    static void validatePlanShape(JSONObject plan) throws JSONException {
        if (plan == null || !"cf-workflow-plan.v1".equals(plan.getString("protocol")))
            throw new JSONException("protocol");
        if (!"READY".equals(plan.getString("status"))) throw new JSONException("not READY");
        String workflowId = plan.getString("workflow_id");
        if (!safeId(workflowId)) throw new JSONException("workflow_id");
        JSONArray steps = plan.getJSONArray("steps");
        if (steps.length() < 1 || steps.length() > 32) throw new JSONException("steps");

        Map<String, JSONObject> byId = new HashMap<String, JSONObject>();
        for (int i = 0; i < steps.length(); i++) {
            JSONObject s = steps.getJSONObject(i);
            String id = s.getString("step_id");
            if (!safeId(id) || byId.containsKey(id)) throw new JSONException("duplicate/invalid step_id");
            byId.put(id, s);
        }
        for (JSONObject s : byId.values()) {
            JSONArray deps = s.getJSONArray("depends_on");
            Set<String> seen = new HashSet<String>();
            for (int i = 0; i < deps.length(); i++) {
                String dep = deps.getString(i);
                if (!byId.containsKey(dep) || dep.equals(s.getString("step_id")) || !seen.add(dep))
                    throw new JSONException("bad dependency");
            }
        }
        detectCycles(byId);
        validateOutputRefs(byId);
    }

    private static void detectCycles(Map<String, JSONObject> byId) throws JSONException {
        Set<String> done = new HashSet<String>();
        Set<String> active = new HashSet<String>();
        for (String id : byId.keySet()) visit(id, byId, done, active);
    }

    private static void visit(String id, Map<String, JSONObject> byId, Set<String> done, Set<String> active)
            throws JSONException {
        if (done.contains(id)) return;
        if (!active.add(id)) throw new JSONException("dependency cycle");
        JSONArray deps = byId.get(id).getJSONArray("depends_on");
        for (int i = 0; i < deps.length(); i++) visit(deps.getString(i), byId, done, active);
        active.remove(id);
        done.add(id);
    }

    private static void validateOutputRefs(Map<String, JSONObject> byId) throws JSONException {
        for (JSONObject step : byId.values()) {
            String current = step.getString("step_id");
            JSONObject args = "CAPABILITY".equals(step.getString("kind"))
                    ? step.getJSONObject("arguments") : step.getJSONObject("inputs");
            JSONArray names = args.names();
            if (names == null) continue;
            Set<String> dependencies = transitiveDependencies(current, byId, new HashSet<String>());
            for (int i = 0; i < names.length(); i++) {
                JSONObject value = args.getJSONObject(names.getString(i));
                if (!"OUTPUT_REF".equals(value.optString("kind", ""))) continue;
                String source = value.getString("step_id");
                String outputName = value.getString("output_name");
                if (!dependencies.contains(source)) throw new JSONException("output ref not dependency");
                if (!declaresOutput(byId.get(source), outputName)) throw new JSONException("unknown output ref");
            }
        }
    }

    private static Set<String> transitiveDependencies(String id, Map<String, JSONObject> byId, Set<String> out)
            throws JSONException {
        JSONArray deps = byId.get(id).getJSONArray("depends_on");
        for (int i = 0; i < deps.length(); i++) {
            String dep = deps.getString(i);
            if (out.add(dep)) transitiveDependencies(dep, byId, out);
        }
        return out;
    }

    private static boolean declaresOutput(JSONObject step, String outputName) throws JSONException {
        JSONArray outputs = step.getJSONArray("outputs");
        for (int i = 0; i < outputs.length(); i++) {
            if (outputName.equals(outputs.getJSONObject(i).getString("name"))) return true;
        }
        return false;
    }

    private static Set<String> rootStepIds(JSONArray steps) throws JSONException {
        Set<String> out = new HashSet<String>();
        for (int i = 0; i < steps.length(); i++) {
            JSONObject s = steps.getJSONObject(i);
            if (s.getJSONArray("depends_on").length() == 0) out.add(s.getString("step_id"));
        }
        return out;
    }

    private static boolean safeId(String s) {
        return s != null && s.length() >= 1 && s.length() <= 128 && s.matches("[A-Za-z0-9._:-]+");
    }

    private static String key(String workflowId) {
        return PREFIX + workflowId;
    }

    private static void bump(JSONObject j) throws JSONException {
        j.put("revision", j.optLong("revision", 0L) + 1L);
    }

    private boolean persistNew(String key, JSONObject j) {
        if (prefs.contains(key)) return false;
        return prefs.edit().putString(key, j.toString()).commit();
    }

    private boolean persistExisting(String key, JSONObject j) {
        if (!prefs.contains(key)) return false;
        return prefs.edit().putString(key, j.toString()).commit();
    }
}
