package com.homayounisaghar.chatgptwebviewprobe;

final class TelemetryConfigV25 {
    static final String WEBHOOK_URL = "https://webhook.site/__V25_UNCONFIGURED__";
    static final String SOURCE_REF = "__SOURCE_REF__";
    static final String COLLECTOR_ID = "__COLLECTOR_ID__";
    static final boolean CONFIGURED = false;

    private TelemetryConfigV25() {}

    static boolean isConfigured() {
        return CONFIGURED && WEBHOOK_URL.startsWith("https://webhook.site/")
                && !WEBHOOK_URL.contains("__V25_UNCONFIGURED__");
    }
}
