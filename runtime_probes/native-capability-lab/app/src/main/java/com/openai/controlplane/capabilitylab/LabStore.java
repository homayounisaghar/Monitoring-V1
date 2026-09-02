package com.openai.controlplane.capabilitylab;

import android.content.Context;
import android.content.SharedPreferences;

import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;

final class LabStore {
    private static final String PREFS = "capability_lab";
    private static final int MAX_LOG = 180_000;
    private static final String REPORT_DIR = "reports";

    private LabStore() {}

    private static SharedPreferences p(Context c) {
        return c.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    static void markAccessibilityConnected(Context c, boolean value) {
        p(c).edit().putBoolean("accessibilityConnected", value).apply();
    }

    static boolean accessibilityConnected(Context c) {
        return p(c).getBoolean("accessibilityConnected", false);
    }

    static void markNotificationConnected(Context c, boolean value) {
        p(c).edit().putBoolean("notificationConnected", value).apply();
    }

    static boolean notificationConnected(Context c) {
        return p(c).getBoolean("notificationConnected", false);
    }

    static synchronized void beginRun(Context c, String planJson, String planSha, String suite) {
        String runId = UUID.randomUUID().toString();
        String base = "Capability Lab report\n"
                + "runId=" + runId + "\n"
                + "startedAt=" + now() + "\n"
                + "suite=" + suite + "\n"
                + "planSha256=" + planSha + "\n"
                + "targetPackage=" + ProfileGuard.CHATGPT_PACKAGE + "\n"
                + "targetVersion=" + ProfileGuard.EXPECTED_VERSION + "\n"
                + "targetSignerSha256=" + ProfileGuard.EXPECTED_SIGNER_SHA256 + "\n"
                + "deviceSdk=" + android.os.Build.VERSION.SDK_INT + "\n";
        String header = base + "--- evidence ---\n";
        String fileName = "capability-lab-report-" + runId + ".txt";
        p(c).edit()
                .putString("runId", runId)
                .putString("planJson", planJson == null ? "" : planJson)
                .putString("planSha", planSha == null ? "" : planSha)
                .putString("suite", suite == null ? "" : suite)
                .putString("state", "RUNNING")
                .putString("status", "RUNNING")
                .putInt("step", 0)
                .putString("marker", "")
                .putBoolean("writeClaimed", false)
                .putBoolean("sendConfirmed", false)
                .putLong("sendConfirmedAtMs", 0L)
                .putBoolean("searchBindingVerified", false)
                .putString("candidates", "")
                .putInt("candidateIndex", 0)
                .putString("verifiedConversationId", "")
                .putLong("waitUntil", 0L)
                .putString("reportFileName", fileName)
                .putBoolean("uiSnapshotRunning", false)
                .putBoolean("uiSnapshotFinal", false)
                .putString("report", header)
                .commit();

        String plan = planJson == null ? "" : planJson.trim();
        String fileHeader = base
                + "--- plan ---\n"
                + plan + "\n"
                + "--- evidence ---\n";
        writeReportFile(c, fileHeader, false);
    }

    static synchronized void resetRun(Context c) {
        boolean a = accessibilityConnected(c);
        boolean n = notificationConnected(c);
        p(c).edit().clear().commit();
        p(c).edit()
                .putBoolean("accessibilityConnected", a)
                .putBoolean("notificationConnected", n)
                .apply();
    }

    static String runId(Context c) { return p(c).getString("runId", ""); }
    static String planJson(Context c) { return p(c).getString("planJson", ""); }
    static String planSha(Context c) { return p(c).getString("planSha", ""); }
    static String suite(Context c) { return p(c).getString("suite", ""); }
    static String state(Context c) { return p(c).getString("state", "IDLE"); }
    static String status(Context c) { return p(c).getString("status", "IDLE"); }
    static int step(Context c) { return p(c).getInt("step", 0); }
    static String marker(Context c) { return p(c).getString("marker", ""); }
    static boolean writeClaimed(Context c) { return p(c).getBoolean("writeClaimed", false); }
    static boolean sendConfirmed(Context c) { return p(c).getBoolean("sendConfirmed", false); }
    static long sendConfirmedAtMs(Context c) { return p(c).getLong("sendConfirmedAtMs", 0L); }
    static boolean searchBindingVerified(Context c) { return p(c).getBoolean("searchBindingVerified", false); }
    static int candidateIndex(Context c) { return p(c).getInt("candidateIndex", 0); }
    static long waitUntil(Context c) { return p(c).getLong("waitUntil", 0L); }
    static String verifiedConversationId(Context c) { return p(c).getString("verifiedConversationId", ""); }
    static String reportFileName(Context c) { return p(c).getString("reportFileName", ""); }

    static long sinceSendMs(Context c) {
        long t = sendConfirmedAtMs(c);
        return t <= 0L ? -1L : Math.max(0L, System.currentTimeMillis() - t);
    }

    static void setStep(Context c, int value) { p(c).edit().putInt("step", value).apply(); }
    static void setState(Context c, String value) { p(c).edit().putString("state", value).apply(); }
    static void setStatus(Context c, String value) { p(c).edit().putString("status", value).apply(); }
    static void setMarker(Context c, String value) { p(c).edit().putString("marker", value == null ? "" : value).apply(); }
    static void setWaitUntil(Context c, long value) { p(c).edit().putLong("waitUntil", value).apply(); }
    static void setCandidateIndex(Context c, int value) { p(c).edit().putInt("candidateIndex", value).apply(); }

    static synchronized boolean advanceStepIfCurrent(Context c, int expectedStep) {
        if (!"RUNNING".equals(status(c)) || step(c) != expectedStep) return false;
        p(c).edit()
                .putString("state", "RUNNING")
                .putInt("step", expectedStep + 1)
                .apply();
        return true;
    }

    static synchronized boolean claimWrite(Context c) {
        if (writeClaimed(c)) return false;
        p(c).edit().putBoolean("writeClaimed", true).commit();
        append(c, "WRITE_CLAIM durable=true");
        return true;
    }

    static synchronized void markSendConfirmed(Context c) {
        if (sendConfirmed(c)) return;
        p(c).edit()
                .putBoolean("sendConfirmed", true)
                .putLong("sendConfirmedAtMs", System.currentTimeMillis())
                .commit();
        append(c, "SEND_RECEIPT editable_to_noneditable=true");
    }

    static synchronized void markSearchBindingVerified(Context c) {
        if (searchBindingVerified(c)) return;
        p(c).edit().putBoolean("searchBindingVerified", true).commit();
        append(c, "VERIFIED_SEARCH_BINDING marker=" + marker(c));
    }

    static synchronized void markVerified(Context c, String id) {
        if ("FINISHED".equals(state(c)) && !verifiedConversationId(c).isEmpty()) return;
        p(c).edit()
                .putString("verifiedConversationId", id == null ? "" : id)
                .putString("state", "FINISHED")
                .putString("status", "PASS_VERIFIED_CONVERSATION_ID")
                .commit();
        append(c, "VERIFIED_CONVERSATION_ID=" + id);
    }

    static synchronized void finish(Context c, String status) {
        if ("FINISHED".equals(state(c))) return;
        p(c).edit().putString("state", "FINISHED").putString("status", status).commit();
        append(c, "FINISH status=" + status + " finishedAt=" + now());
    }

    static synchronized void addCandidate(Context c, String source, String raw) {
        String value = clean(raw);
        if (value.isEmpty()) return;
        String marker = marker(c);
        if (!marker.isEmpty() && value.contains(marker)) return;
        Set<String> values = new LinkedHashSet<>(candidates(c));
        if (values.add(value)) {
            StringBuilder b = new StringBuilder();
            for (String x : values) {
                if (b.length() > 0) b.append('\n');
                b.append(x);
            }
            p(c).edit().putString("candidates", b.toString()).apply();
            append(c, "CANDIDATE source=" + source + " value=" + abbrev(value, 200));
        }
    }

    static List<String> candidates(Context c) {
        String s = p(c).getString("candidates", "");
        List<String> out = new ArrayList<>();
        if (s == null || s.trim().isEmpty()) return out;
        for (String line : s.split("\\n")) {
            String x = clean(line);
            if (!x.isEmpty() && !out.contains(x)) out.add(x);
        }
        return out;
    }

    static synchronized void append(Context c, String line) {
        String rendered = "[" + now() + "] " + cleanLine(line) + "\n";
        String old = p(c).getString("report", "");
        String next = old + rendered;
        if (next.length() > MAX_LOG) next = "...<older evidence truncated in UI copy>...\n" + next.substring(next.length() - MAX_LOG);
        p(c).edit().putString("report", next).apply();
        writeReportFile(c, rendered, true);
    }

    static synchronized void appendUiSnapshotOnce(Context c, String phase, String snapshot) {
        String normalized = phase == null ? "" : phase.trim().toUpperCase(Locale.US);
        String key;
        if ("RUNNING".equals(normalized)) key = "uiSnapshotRunning";
        else if ("FINAL".equals(normalized)) key = "uiSnapshotFinal";
        else return;
        if (p(c).getBoolean(key, false)) return;
        p(c).edit().putBoolean(key, true).commit();
        String block = "\n--- lab-ui-snapshot " + normalized + " ---\n"
                + (snapshot == null ? "" : snapshot.trim()) + "\n"
                + "--- end-lab-ui-snapshot " + normalized + " ---\n";
        writeReportFile(c, block, true);
        append(c, "LAB_UI_SNAPSHOT_CAPTURED phase=" + normalized);
    }

    static String report(Context c) {
        return p(c).getString("report", "<no run report>");
    }

    static File reportFile(Context c) {
        String name = reportFileName(c);
        if (name == null || name.trim().isEmpty()) return null;
        File dir = new File(c.getFilesDir(), REPORT_DIR);
        return new File(dir, name);
    }

    static synchronized File ensureReportFile(Context c) {
        File f = reportFile(c);
        if (f == null) return null;
        if (!f.exists() || f.length() == 0L) writeReportFile(c, report(c), false);
        return f;
    }

    static String compactSummary(Context c) {
        return "run=" + runId(c)
                + " state=" + state(c)
                + " status=" + status(c)
                + " step=" + step(c)
                + " marker=" + marker(c)
                + " candidates=" + candidates(c).size()
                + " verifiedId=" + verifiedConversationId(c)
                + " searchBinding=" + searchBindingVerified(c)
                + " sinceSendMs=" + sinceSendMs(c)
                + " reportFile=" + reportFileName(c);
    }

    private static void writeReportFile(Context c, String text, boolean append) {
        try {
            File f = reportFile(c);
            if (f == null) return;
            File parent = f.getParentFile();
            if (parent != null && !parent.exists() && !parent.mkdirs() && !parent.exists()) return;
            try (FileOutputStream out = new FileOutputStream(f, append)) {
                out.write((text == null ? "" : text).getBytes(StandardCharsets.UTF_8));
                out.flush();
            }
        } catch (Throwable ignored) {}
    }

    private static String now() {
        return new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSZ", Locale.US).format(new Date());
    }

    private static String clean(String s) { return s == null ? "" : s.trim(); }

    private static String cleanLine(String s) {
        if (s == null) return "";
        return s.replace('\n', ' ').replace('\r', ' ');
    }

    static String abbrev(String s, int max) {
        if (s == null) return "";
        String one = cleanLine(s);
        return one.length() <= max ? one : one.substring(0, max) + "...";
    }
}
