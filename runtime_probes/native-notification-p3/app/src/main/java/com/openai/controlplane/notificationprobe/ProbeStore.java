package com.openai.controlplane.notificationprobe;

import android.content.Context;
import android.content.SharedPreferences;

public final class ProbeStore {
    private static final String PREFS = "notification_p3";
    private static final int MAX_LOG_CHARS = 30000;

    private ProbeStore() {}

    private static SharedPreferences p(Context c) {
        return c.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    public static void markConnected(Context c) {
        p(c).edit()
                .putBoolean("listenerConnected", true)
                .putLong("connectedAt", System.currentTimeMillis())
                .apply();
        append(c, "LISTENER_CONNECTED");
    }

    public static void markDisconnected(Context c) {
        p(c).edit()
                .putBoolean("listenerConnected", false)
                .putLong("disconnectedAt", System.currentTimeMillis())
                .apply();
        append(c, "LISTENER_DISCONNECTED");
    }

    public static void markRebindRequested(Context c) {
        p(c).edit().putLong("rebindRequestedAt", System.currentTimeMillis()).apply();
        append(c, "LISTENER_REBIND_REQUESTED");
    }

    public static boolean listenerConnected(Context c) {
        return p(c).getBoolean("listenerConnected", false);
    }

    public static long connectedAt(Context c) {
        return p(c).getLong("connectedAt", 0L);
    }

    public static long disconnectedAt(Context c) {
        return p(c).getLong("disconnectedAt", 0L);
    }

    public static long rebindRequestedAt(Context c) {
        return p(c).getLong("rebindRequestedAt", 0L);
    }

    public static long eventCount(Context c) {
        return p(c).getLong("eventCount", 0L);
    }

    public static long lastEventAt(Context c) {
        return p(c).getLong("lastEventAt", 0L);
    }

    public static String log(Context c) {
        return p(c).getString("log", "");
    }

    public static void clearEvents(Context c) {
        p(c).edit()
                .remove("log")
                .putLong("eventCount", 0L)
                .putLong("lastEventAt", 0L)
                .apply();
    }

    public static synchronized void append(Context c, String line) {
        SharedPreferences prefs = p(c);
        long seq = prefs.getLong("eventCount", 0L) + 1L;
        long now = System.currentTimeMillis();
        String old = prefs.getString("log", "");
        String entry = "#" + seq + " @" + now + " " + (line == null ? "" : line) + "\n";
        String combined = old + entry;
        if (combined.length() > MAX_LOG_CHARS) {
            combined = combined.substring(combined.length() - MAX_LOG_CHARS);
        }
        prefs.edit()
                .putString("log", combined)
                .putLong("eventCount", seq)
                .putLong("lastEventAt", now)
                .apply();
    }
}
