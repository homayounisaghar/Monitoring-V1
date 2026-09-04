package com.homayounisaghar.chatgptwebviewprobe;

final class TelemetryConfigV27 {
    static final String WEBHOOK_URL = "https://webhook.site/__V27_UNCONFIGURED__";
    static final String SOURCE_REF = "__SOURCE_REF__";
    static final String COLLECTOR_ID = "__COLLECTOR_ID__";
    static final boolean CONFIGURED = false;

    private TelemetryConfigV27() {}

    static boolean isConfigured() {
        return CONFIGURED && WEBHOOK_URL.startsWith("https://webhook.site/")
                && !WEBHOOK_URL.contains("__V27_UNCONFIGURED__");
    }
}
