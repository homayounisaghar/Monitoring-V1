package com.openai.controlplane.capabilitylab;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

final class PlanLoader {
    static final String PLAN_URL = "https://raw.githubusercontent.com/homayounisaghar/Monitoring-V1/build/pebble-chat-bridge-v019/runtime_probes/native-capability-lab/plans/default.json";

    static final String FALLBACK = "{\"schema\":1,\"suite\":\"conversation_history_accessibility_binding_v13_static_first\",\"targetVersion\":\"1.2026.237\",\"targetSignerSha256\":\"b24f4bfbb3cf293f938703b9d87027c1102cc36dc4fa206910e08927db40473c\",\"steps\":[{\"op\":\"global_search_binding\",\"marker\":\"LAB_CID_9FC96C5A35E04E5B\",\"probe\":true,\"label\":\"known_indexed_row_calibration\",\"navigationTimeoutMs\":8000,\"resultWaitMs\":5000},{\"op\":\"history_boundary_calibration\",\"timeoutMs\":12000},{\"op\":\"verify_candidates\",\"timeoutMs\":7000},{\"op\":\"reset_after_calibration\"},{\"op\":\"launch_prompt\",\"prompt\":\"Capability Lab static-first History accessibility proof. Reply with exactly this marker and no other text: {{marker}}\"},{\"op\":\"capture_tree\",\"label\":\"pre_send_draft_baseline\",\"timeoutMs\":8000},{\"op\":\"semantic_send\",\"timeoutMs\":15000},{\"op\":\"capture_tree\",\"label\":\"post_send_receipt\",\"timeoutMs\":8000},{\"op\":\"wait\",\"ms\":700},{\"op\":\"history_recent_binding\",\"timeoutMs\":22000,\"settleMs\":1100},{\"op\":\"verify_candidates\",\"timeoutMs\":8000},{\"op\":\"finish\",\"inconclusiveStatus\":\"INCONCLUSIVE_HISTORY_ACCESSIBILITY_BOUNDARY_NOT_VERIFIED\"}]}";

    private PlanLoader() {}

    static final class PlanData {
        final String json;
        final String sha256;
        final String source;
        PlanData(String json, String sha256, String source) {
            this.json = json;
            this.sha256 = sha256;
            this.source = source;
        }
    }

    static PlanData fetchOrFallback() throws Exception {
        try {
            HttpURLConnection c = (HttpURLConnection) new URL(PLAN_URL).openConnection();
            c.setConnectTimeout(8000);
            c.setReadTimeout(8000);
            c.setUseCaches(false);
            c.setRequestProperty("Accept", "application/json");
            int code = c.getResponseCode();
            if (code < 200 || code >= 300) throw new IllegalStateException("HTTP " + code);
            byte[] bytes;
            try (InputStream in = c.getInputStream()) {
                bytes = readAll(in, 200_000);
            } finally {
                c.disconnect();
            }
            String json = new String(bytes, StandardCharsets.UTF_8);
            validate(json);
            return new PlanData(json, ProfileGuard.sha256(bytes), PLAN_URL);
        } catch (Throwable remote) {
            byte[] bytes = FALLBACK.getBytes(StandardCharsets.UTF_8);
            validate(FALLBACK);
            return new PlanData(FALLBACK, ProfileGuard.sha256(bytes), "embedded-fallback:" + remote.getClass().getSimpleName());
        }
    }

    static void validate(String json) throws Exception {
        JSONObject root = new JSONObject(json);
        if (root.optInt("schema", -1) != 1) throw new IllegalArgumentException("unsupported plan schema");
        if (!ProfileGuard.EXPECTED_VERSION.equals(root.optString("targetVersion"))) {
            throw new IllegalArgumentException("plan targetVersion mismatch");
        }
        if (!ProfileGuard.EXPECTED_SIGNER_SHA256.equalsIgnoreCase(root.optString("targetSignerSha256"))) {
            throw new IllegalArgumentException("plan signer mismatch");
        }
        String suite = root.optString("suite", "");
        if (suite.isEmpty()) throw new IllegalArgumentException("plan suite missing");
        JSONArray steps = root.optJSONArray("steps");
        if (steps == null || steps.length() == 0 || steps.length() > 100) throw new IllegalArgumentException("plan steps invalid");
        for (int i = 0; i < steps.length(); i++) {
            JSONObject step = steps.optJSONObject(i);
            if (step == null || step.optString("op", "").isEmpty()) throw new IllegalArgumentException("step " + i + " invalid");
        }
    }

    private static byte[] readAll(InputStream in, int max) throws Exception {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int total = 0;
        int n;
        while ((n = in.read(buf)) >= 0) {
            total += n;
            if (total > max) throw new IllegalStateException("plan too large");
            out.write(buf, 0, n);
        }
        return out.toByteArray();
    }
}
