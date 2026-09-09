package com.homayounisaghar.chatgptwebviewprobe;

import org.json.JSONObject;

/**
 * Frozen semantic signatures from the previously qualified Temporary Chat
 * manual-observation / exact-signature roundtrip lineage.
 *
 * These values are a compatibility adapter for the current ChatGPT UI, not a
 * timeless product API. A concrete disposable Planner adapter must fresh-scan,
 * require exactly one matching control, obtain post-click receipts, and fail
 * closed if the UI no longer matches. It must never click from these hashes
 * alone without fresh semantic observation.
 */
final class TemporaryChatSignaturesV1 {
    static final String NORMAL_LABEL_HASH = "1a957a52";
    static final String NORMAL_STRUCT_HASH = "b9c97d1e";
    static final String NORMAL_SEMANTIC_SET_HASH = "566ee132";
    static final String TEMP_LABEL_HASH = "ae0e16e6";
    static final String TEMP_STRUCT_HASH = "34d052a8";
    static final String TEMP_SEMANTIC_SET_HASH = "2f8aeb2c";
    static final String EMPTY_TESTID_HASH = "811c9dc5";

    enum State { NORMAL, TEMP, UNKNOWN }

    private TemporaryChatSignaturesV1() {}

    static State classify(JSONObject o) {
        if (o == null || !o.optBoolean("success", false)) return State.UNKNOWN;
        if (!"complete".equals(o.optString("ready", ""))) return State.UNKNOWN;
        if (!"HOME".equals(o.optString("route_class", ""))) return State.UNKNOWN;
        if (o.optInt("temp_candidate_count", 0) != 1) return State.UNKNOWN;
        if (!"button".equals(o.optString("candidate_tag", ""))) return State.UNKNOWN;
        if (!"button".equals(o.optString("candidate_role", ""))) return State.UNKNOWN;
        if (!EMPTY_TESTID_HASH.equals(o.optString("candidate_testid_hash", ""))) return State.UNKNOWN;
        if (!"NONE".equals(o.optString("candidate_data_state", ""))) return State.UNKNOWN;
        if (o.optInt("candidate_selected", -1) != 0
                || o.optInt("candidate_pressed", -1) != 0
                || o.optInt("candidate_expanded", -1) != 0
                || o.optInt("candidate_disabled", -1) != 0) return State.UNKNOWN;
        if (!"NONE".equals(o.optString("candidate_href_class", ""))) return State.UNKNOWN;
        if (o.optBoolean("composer_temp_hint", true)) return State.UNKNOWN;

        boolean urlTemp = o.optBoolean("url_temp_hint", false);
        String label = o.optString("candidate_label_hash", "");
        String struct = o.optString("candidate_struct_hash", "");
        String set = o.optString("temp_semantic_set_hash", "");

        if (!urlTemp
                && NORMAL_LABEL_HASH.equals(label)
                && NORMAL_STRUCT_HASH.equals(struct)
                && NORMAL_SEMANTIC_SET_HASH.equals(set)) return State.NORMAL;
        if (urlTemp
                && TEMP_LABEL_HASH.equals(label)
                && TEMP_STRUCT_HASH.equals(struct)
                && TEMP_SEMANTIC_SET_HASH.equals(set)) return State.TEMP;
        return State.UNKNOWN;
    }

    static boolean exactEntryGate(JSONObject o) {
        return classify(o) == State.NORMAL;
    }

    static boolean exactExitGate(JSONObject o) {
        return classify(o) == State.TEMP;
    }
}
