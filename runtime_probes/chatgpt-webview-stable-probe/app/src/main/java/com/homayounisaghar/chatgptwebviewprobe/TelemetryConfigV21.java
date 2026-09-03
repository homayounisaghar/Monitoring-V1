package com.homayounisaghar.chatgptwebviewprobe;

/** Build-time injected transport config for Stable v0.21 diagnostics. */
final class TelemetryConfigV21 {
    static final String WEBHOOK_URL = "https://invalid.local/unconfigured";
    static final String SOURCE_REF = "UNCONFIGURED_SOURCE";
    static final String COLLECTOR_ID = "UNCONFIGURED_COLLECTOR";
    static final boolean CONFIGURED = false;

    private TelemetryConfigV21() {}

    static boolean isConfigured() {
        return CONFIGURED && WEBHOOK_URL.startsWith("https://webhook.site/");
    }
}
