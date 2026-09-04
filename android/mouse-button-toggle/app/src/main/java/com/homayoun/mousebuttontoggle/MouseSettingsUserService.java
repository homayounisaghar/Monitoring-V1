package com.homayoun.mousebuttontoggle;

import android.os.Build;
import android.os.RemoteException;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class MouseSettingsUserService extends IMouseSettingsService.Stub {
    private static final String SETTINGS = "/system/bin/settings";
    private static final String DUMPSYS = "/system/bin/dumpsys";
    private static final String TABLE = "system";
    private static final String KEY = "mouse_swap_primary_button";
    private static final Pattern SAMSUNG_PRIMARY_PATTERN = Pattern.compile(
            "(?im)^\\s*Primary Mouse Button Location:\\s*(-?\\d+)\\s*$");

    public MouseSettingsUserService() {
    }

    @Override
    public void destroy() {
        System.exit(0);
    }

    @Override
    public int getSwapState() throws RemoteException {
        Integer samsung = readSamsungPrimaryLocation();
        if (samsung != null) {
            return samsung;
        }
        return readAospSwapState();
    }

    @Override
    public int toggleSwapState() throws RemoteException {
        int current = getSwapState();
        int next = current == 1 ? 0 : 1;
        Integer samsungBefore = readSamsungPrimaryLocation();

        CommandResult write = run(SETTINGS, "put", TABLE, KEY, Integer.toString(next));
        if (write.exitCode != 0) {
            throw new RemoteException("settings put failed: " + write.output);
        }

        int aospVerified = readAospSwapState();
        if (aospVerified != next) {
            throw new RemoteException("Android setting did not persist. Expected " + next
                    + " but read " + aospVerified);
        }

        if (samsungBefore != null) {
            Integer samsungAfter = samsungBefore;
            for (int i = 0; i < 6; i++) {
                try {
                    Thread.sleep(150L);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
                samsungAfter = readSamsungPrimaryLocation();
                if (samsungAfter != null && samsungAfter == next) {
                    return next;
                }
            }
            throw new RemoteException(
                    "Samsung input state did not change (before=" + samsungBefore
                            + ", after=" + samsungAfter
                            + ") although Android setting changed to " + next
                            + ". Open the app and run Diagnostics.");
        }

        return next;
    }

    @Override
    public String getDiagnostics() throws RemoteException {
        CommandResult aosp = run(SETTINGS, "get", TABLE, KEY);
        CommandResult input = run(DUMPSYS, "input");
        Integer samsung = parseSamsungPrimaryLocation(input.output);

        StringBuilder report = new StringBuilder();
        report.append("manufacturer=").append(Build.MANUFACTURER)
                .append("\nbrand=").append(Build.BRAND)
                .append("\nmodel=").append(Build.MODEL)
                .append("\ndevice=").append(Build.DEVICE)
                .append("\nsdk=").append(Build.VERSION.SDK_INT)
                .append("\nrelease=").append(Build.VERSION.RELEASE)
                .append("\n").append(KEY).append("=").append(aosp.output.trim())
                .append("\naosp_exit=").append(aosp.exitCode)
                .append("\nsamsung_primary_location=")
                .append(samsung == null ? "not-found" : samsung)
                .append("\n\nRelevant dumpsys input lines:\n")
                .append(filterRelevantInputLines(input.output))
                .append("\n\nRelevant settings entries:\n")
                .append(settingsCandidates("system"))
                .append(settingsCandidates("global"))
                .append(settingsCandidates("secure"));
        return report.toString();
    }

    private static int readAospSwapState() throws RemoteException {
        CommandResult result = run(SETTINGS, "get", TABLE, KEY);
        if (result.exitCode != 0) {
            throw new RemoteException("settings get failed: " + result.output);
        }
        String raw = result.output.trim();
        if (raw.isEmpty() || "null".equalsIgnoreCase(raw) || "0".equals(raw)
                || "false".equalsIgnoreCase(raw) || "off".equalsIgnoreCase(raw)
                || "left".equalsIgnoreCase(raw)) {
            return 0;
        }
        if ("1".equals(raw) || "true".equalsIgnoreCase(raw) || "on".equalsIgnoreCase(raw)
                || "right".equalsIgnoreCase(raw)) {
            return 1;
        }
        throw new RemoteException("Unexpected " + KEY + " value: " + raw);
    }

    private static Integer readSamsungPrimaryLocation() throws RemoteException {
        CommandResult result = run(DUMPSYS, "input");
        if (result.exitCode != 0) {
            return null;
        }
        return parseSamsungPrimaryLocation(result.output);
    }

    private static Integer parseSamsungPrimaryLocation(String text) {
        Matcher matcher = SAMSUNG_PRIMARY_PATTERN.matcher(text == null ? "" : text);
        if (!matcher.find()) {
            return null;
        }
        try {
            int value = Integer.parseInt(matcher.group(1));
            return value == 0 || value == 1 ? value : null;
        } catch (NumberFormatException ignored) {
            return null;
        }
    }

    private static String filterRelevantInputLines(String output) {
        if (output == null || output.isEmpty()) {
            return "(none)\n";
        }
        StringBuilder result = new StringBuilder();
        for (String line : output.split("\\R")) {
            String lower = line.toLowerCase(Locale.ROOT);
            if (lower.contains("primary mouse")
                    || lower.contains("mouse button behavior")
                    || lower.contains("mouse acceleration")
                    || lower.contains("scroll speed")) {
                result.append(line.trim()).append('\n');
            }
        }
        return result.length() == 0 ? "(none)\n" : result.toString();
    }

    private static String settingsCandidates(String table) throws RemoteException {
        CommandResult result = run(SETTINGS, "list", table);
        StringBuilder filtered = new StringBuilder();
        if (result.exitCode == 0) {
            for (String line : result.output.split("\\R")) {
                String lower = line.toLowerCase(Locale.ROOT);
                if (lower.contains("mouse") || lower.contains("pointer")) {
                    filtered.append(table).append(':').append(line.trim()).append('\n');
                }
            }
        }
        if (filtered.length() == 0) {
            filtered.append(table).append(":(no mouse/pointer entries found)\n");
        }
        return filtered.toString();
    }

    private static CommandResult run(String... command) throws RemoteException {
        try {
            Process process = new ProcessBuilder(command)
                    .redirectErrorStream(true)
                    .start();
            StringBuilder output = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    if (output.length() > 0) output.append('\n');
                    output.append(line);
                }
            }
            int exit = process.waitFor();
            return new CommandResult(exit, output.toString());
        } catch (Exception e) {
            RemoteException remote = new RemoteException(e.toString());
            remote.initCause(e);
            throw remote;
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
