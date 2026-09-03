package com.homayounisaghar.chatgptwebviewprobe;

/**
 * Build-time generated values for Stable v0.19 autonomous diagnostics.
 * The release workflow rewrites only these explicit fields. Runtime validation
 * never compares against a placeholder string, avoiding the self-mutating
 * placeholder bug found in the first Perplexity autonomous probe.
 */
final class TelemetryConfigV19 {
    static final String WEBHOOK_URL = "";
    static final String SOURCE_REF = "";
    static final String COLLECTOR_ID = "";

    private TelemetryConfigV19() {}

    static boolean isConfigured() {
        return WEBHOOK_URL.startsWith("https://webhook.site/") && WEBHOOK_URL.length() > 30;
    }
}
