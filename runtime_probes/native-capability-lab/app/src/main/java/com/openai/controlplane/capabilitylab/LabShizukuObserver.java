package com.openai.controlplane.capabilitylab;

import android.content.Context;
import android.content.pm.PackageManager;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import rikka.shizuku.Shizuku;

/**
 * LAB-ONLY observer. This class is deliberately excluded from production capability claims.
 * It uses a user-started Shizuku shell identity only to discover where ChatGPT exposes its
 * conversation identifier in Android system state. Raw dumpsys output is never persisted;
 * only bounded summaries, hashes, and candidate identifiers are recorded.
 */
final class LabShizukuObserver {
    static final int PERMISSION_REQUEST_CODE = 4204;

    private static final int MAX_OUTPUT_BYTES = 1_000_000;
    private static final Pattern UUID_FIND = Pattern.compile("(?i)(?<![0-9a-f])[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?![0-9a-f])");
    private static final Pattern HEX32_FIND = Pattern.compile("(?i)(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])");
    private static final Pattern CHAT_URI_FIND = Pattern.compile("(?i)https?://(?:www\\.)?chatgpt\\.com/c/([0-9a-f-]{32,36})");

    private static final CommandSpec[] COMMANDS = new CommandSpec[]{
            new CommandSpec("notification",
                    "dumpsys notification --noredact | grep -i -B 12 -A 220 'com.openai.chatgpt' | head -n 4000"),
            new CommandSpec("shortcut",
                    "dumpsys shortcut | grep -i -B 12 -A 320 'com.openai.chatgpt' | head -n 5000"),
            new CommandSpec("activity",
                    "dumpsys activity activities | grep -i -B 12 -A 100 'com.openai.chatgpt' | head -n 3000"),
            new CommandSpec("recents",
                    "dumpsys activity recents | grep -i -B 12 -A 100 'com.openai.chatgpt' | head -n 3000")
    };

    private LabShizukuObserver() {}

    static boolean binderAlive() {
        try {
            return Shizuku.pingBinder();
        } catch (Throwable t) {
            return false;
        }
    }

    static boolean permissionGranted() {
        try {
            return binderAlive() && Shizuku.checkSelfPermission() == PackageManager.PERMISSION_GRANTED;
        } catch (Throwable t) {
            return false;
        }
    }

    static String compactStatus() {
        if (!binderAlive()) return "binder=OFF permission=NO";
        try {
            int permission = Shizuku.checkSelfPermission();
            int version = Shizuku.getVersion();
            int uid = Shizuku.getUid();
            return "binder=ON permission=" + (permission == PackageManager.PERMISSION_GRANTED ? "YES" : "NO")
                    + " serverVersion=" + version + " serverUid=" + uid;
        } catch (Throwable t) {
            return "binder=ON statusError=" + t.getClass().getSimpleName();
        }
    }

    static void requestPermission() {
        if (!binderAlive()) throw new IllegalStateException("Shizuku binder is not running");
        if (permissionGranted()) return;
        Shizuku.requestPermission(PERMISSION_REQUEST_CODE);
    }

    static CaptureSummary capture(Context context, String label) throws Exception {
        ProfileGuard.assertExact(context);
        if (!binderAlive()) throw new IllegalStateException("Shizuku binder is not running");
        if (!permissionGranted()) throw new SecurityException("Shizuku permission not granted");

        int before = LabStore.candidates(context).size();
        int totalBytes = 0;
        int totalMatches = 0;
        int commandsSucceeded = 0;

        LabStore.append(context, "SHELL_OBSERVER_BEGIN label=" + clean(label)
                + " " + compactStatus()
                + " classification=LAB_ONLY_DISCOVERY");

        for (CommandSpec spec : COMMANDS) {
            CommandResult result = runShell(spec.command);
            totalBytes += result.output.length();
            int matches = harvestCandidates(context, "shell." + spec.name, result.output);
            totalMatches += matches;
            if (result.exitCode == 0) commandsSucceeded++;
            LabStore.append(context, "SHELL_OBSERVER_COMMAND name=" + spec.name
                    + " exit=" + result.exitCode
                    + " bytes=" + result.output.length()
                    + " sha256=" + hashPrefix(result.output)
                    + " candidateMatches=" + matches);
        }

        int after = LabStore.candidates(context).size();
        CaptureSummary summary = new CaptureSummary(COMMANDS.length, commandsSucceeded, totalBytes,
                totalMatches, Math.max(0, after - before));
        LabStore.append(context, "SHELL_OBSERVER_END label=" + clean(label)
                + " commands=" + summary.commands
                + " succeeded=" + summary.succeeded
                + " bytes=" + summary.bytes
                + " candidateMatches=" + summary.candidateMatches
                + " newUniqueCandidates=" + summary.newUniqueCandidates);
        return summary;
    }

    private static CommandResult runShell(String command) throws Exception {
        // Shizuku 13.1.5 keeps newProcess as an internal transition API. The Lab pins that
        // client version and accesses it reflectively only in this observer-only diagnostic.
        Method newProcess = Shizuku.class.getDeclaredMethod("newProcess", String[].class, String[].class, String.class);
        newProcess.setAccessible(true);
        String[] argv = new String[]{"/system/bin/sh", "-c", command + " 2>&1"};
        Object process = newProcess.invoke(null, new Object[]{argv, null, null});
        if (process == null) throw new IllegalStateException("Shizuku process unavailable");

        Method getInputStream = process.getClass().getMethod("getInputStream");
        Method waitFor = process.getClass().getMethod("waitFor");
        Method destroy = process.getClass().getMethod("destroy");

        String output;
        int exit;
        try {
            InputStream in = (InputStream) getInputStream.invoke(process);
            output = readBounded(in, MAX_OUTPUT_BYTES);
            Object code = waitFor.invoke(process);
            exit = code instanceof Integer ? (Integer) code : -1;
        } finally {
            try { destroy.invoke(process); } catch (Throwable ignored) {}
        }
        return new CommandResult(exit, output == null ? "" : output);
    }

    private static String readBounded(InputStream in, int maxBytes) throws Exception {
        if (in == null) return "";
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buffer = new byte[8192];
        int total = 0;
        while (true) {
            int n = in.read(buffer);
            if (n < 0) break;
            int remaining = maxBytes - total;
            if (remaining <= 0) break;
            int write = Math.min(n, remaining);
            out.write(buffer, 0, write);
            total += write;
            if (total >= maxBytes) break;
        }
        return out.toString(StandardCharsets.UTF_8.name());
    }

    private static int harvestCandidates(Context context, String source, String raw) {
        if (raw == null || raw.isEmpty()) return 0;
        int matches = 0;

        Matcher uri = CHAT_URI_FIND.matcher(raw);
        while (uri.find() && matches < 128) {
            LabStore.addCandidate(context, source + ".chatUri", uri.group(1));
            matches++;
        }

        Matcher uuid = UUID_FIND.matcher(raw);
        while (uuid.find() && matches < 128) {
            LabStore.addCandidate(context, source + ".uuid", uuid.group());
            matches++;
        }

        Matcher hex = HEX32_FIND.matcher(raw);
        while (hex.find() && matches < 128) {
            LabStore.addCandidate(context, source + ".hex32", hex.group());
            matches++;
        }
        return matches;
    }

    private static String hashPrefix(String value) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] d = md.digest((value == null ? "" : value).getBytes(StandardCharsets.UTF_8));
            StringBuilder b = new StringBuilder();
            for (int i = 0; i < Math.min(12, d.length); i++) {
                b.append(String.format(Locale.US, "%02x", d[i] & 0xff));
            }
            return b.toString();
        } catch (Throwable t) {
            return "error";
        }
    }

    private static String clean(String value) {
        if (value == null) return "";
        return value.replace('\n', ' ').replace('\r', ' ').trim();
    }

    static final class CaptureSummary {
        final int commands;
        final int succeeded;
        final int bytes;
        final int candidateMatches;
        final int newUniqueCandidates;

        CaptureSummary(int commands, int succeeded, int bytes, int candidateMatches, int newUniqueCandidates) {
            this.commands = commands;
            this.succeeded = succeeded;
            this.bytes = bytes;
            this.candidateMatches = candidateMatches;
            this.newUniqueCandidates = newUniqueCandidates;
        }
    }

    private static final class CommandSpec {
        final String name;
        final String command;
        CommandSpec(String name, String command) {
            this.name = name;
            this.command = command;
        }
    }

    private static final class CommandResult {
        final int exitCode;
        final String output;
        CommandResult(int exitCode, String output) {
            this.exitCode = exitCode;
            this.output = output;
        }
    }
}
