package com.homayounisaghar.chatgptwebviewprobe;

import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Mechanical runtime binding of a validated workflow step.
 *
 * It resolves only explicit LITERAL and OUTPUT_REF bindings. It never resolves
 * pronouns, target names, fuzzy descriptions, or semantic conditions. Those
 * must already have been compiled by the Planner into exact refs.
 */
final class WorkflowValueResolverV1 {
    static final class Result {
        final boolean success;
        final JSONObject values;
        final String errorClass;
        Result(boolean success, JSONObject values, String errorClass) {
            this.success = success;
            this.values = values;
            this.errorClass = errorClass;
        }
    }

    private WorkflowValueResolverV1() {}

    static Result resolveCapabilityArguments(WorkflowJournalGuardV1 journal,
                                             String workflowId,
                                             JSONObject step) {
        if (step == null || !"CAPABILITY".equals(step.optString("kind", "")))
            return fail("NOT_CAPABILITY_STEP");
        return resolveBindings(journal, workflowId, step.optJSONObject("arguments"));
    }

    static Result resolveSemanticInputs(WorkflowJournalGuardV1 journal,
                                        String workflowId,
                                        JSONObject step) {
        if (step == null || !"SEMANTIC".equals(step.optString("kind", "")))
            return fail("NOT_SEMANTIC_STEP");
        return resolveBindings(journal, workflowId, step.optJSONObject("inputs"));
    }

    private static Result resolveBindings(WorkflowJournalGuardV1 journal,
                                          String workflowId,
                                          JSONObject bindings) {
        if (journal == null || workflowId == null || bindings == null)
            return fail("BINDING_INPUT_MISSING");
        try {
            JSONObject out = new JSONObject();
            JSONArray names = bindings.names();
            if (names == null) return new Result(true, out, "");
            for (int i = 0; i < names.length(); i++) {
                String name = names.getString(i);
                JSONObject binding = bindings.getJSONObject(name);
                String kind = binding.optString("kind", "");
                if ("LITERAL".equals(kind)) {
                    Object value = binding.opt("value");
                    if (value instanceof String) value = ExactTextV1.canonical((String)value);
                    out.put(name, deepCopy(value));
                } else if ("OUTPUT_REF".equals(kind)) {
                    String sourceStep = binding.optString("step_id", "");
                    String outputName = binding.optString("output_name", "");
                    String exact = journal.exactTextOutput(workflowId, sourceStep, outputName);
                    if (exact == null) return fail("OUTPUT_REF_UNAVAILABLE");
                    out.put(name, exact);
                } else {
                    return fail("UNKNOWN_BINDING_KIND");
                }
            }
            return new Result(true, out, "");
        } catch (Exception e) {
            return fail("BINDING_RESOLUTION_EXCEPTION");
        }
    }

    private static Object deepCopy(Object value) throws Exception {
        if (value == null || value == JSONObject.NULL) return JSONObject.NULL;
        if (value instanceof JSONObject) return new JSONObject(value.toString());
        if (value instanceof JSONArray) return new JSONArray(value.toString());
        return value;
    }

    private static Result fail(String errorClass) {
        return new Result(false, new JSONObject(), errorClass);
    }
}
