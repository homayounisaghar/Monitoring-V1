package com.homayounisaghar.chatgptwebviewprobe;

final class TelemetryConfigV30 {
    static final String WEBHOOK_URL = "https://webhook.site/__V30_UNCONFIGURED__";
    static final String SOURCE_REF = "__SOURCE_REF__";
    static final String COLLECTOR_ID = "__COLLECTOR_ID__";
    static final int COLLECTOR_CAPACITY_HINT = 50;
    static final boolean CONFIGURED = false;

    private TelemetryConfigV30() {}

    static boolean isConfigured() {
        return CONFIGURED && WEBHOOK_URL.startsWith("https://webhook.site/")
                && !WEBHOOK_URL.contains("__V30_UNCONFIGURED__");
    }
}
