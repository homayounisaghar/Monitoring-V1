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
    private static final String AOSP_KEY = "mouse_swap_primary_button";
    private static final String SAMSUNG_KEY = "primary_mouse_button_option";
    private static final Pattern PRIMARY_LOCATION_PATTERN = Pattern.compile(
            "(?im)^\\s*Primary Mouse Button Location:\\s*(-?\\d+)\\s*$");

    public MouseSettingsUserService() {
    }

    @Override
    public void destroy() {
        System.exit(0);
    }

    @Override
    public int getSwapState() throws RemoteException {
        Integer live = readLivePrimaryLocation();
        if (live != null) {
            return live;
        }
        Integer samsung = readBinarySystemSetting(SAMSUNG_KEY);
        if (samsung != null && isSamsungDevice()) {
            return samsung;
        }
        return readAospSwapState();
    }

    @Override
    public int toggleSwapState() throws RemoteException {
        int current = getSwapState();
        int next = current == 1 ? 0 : 1;
        Integer liveBefore = readLivePrimaryLocation();
        Integer samsungSettingBefore = readBinarySystemSetting(SAMSUNG_KEY);
        boolean useSamsungBackend = isSamsungDevice() || samsungSettingBefore != null;

        if (useSamsungBackend) {
            writeSystemSetting(SAMSUNG_KEY, next);
        }
        writeSystemSetting(AOSP_KEY, next);

        int aospVerified = readAospSwapState();
        if (aospVerified != next) {
            throw new RemoteException("Android setting did not persist. Expected " + next
                    + " but read " + aospVerified);
        }

        if (useSamsungBackend) {
            Integer samsungVerified = readBinarySystemSetting(SAMSUNG_KEY);
            if (samsungVerified == null || samsungVerified != next) {
                throw new RemoteException("Samsung setting did not persist. Expected " + next
                        + " but read " + samsungVerified);
            }
        }

        if (liveBefore != null) {
            Integer liveAfter = liveBefore;
            for (int i = 0; i < 15; i++) {
                sleep(120L);
                liveAfter = readLivePrimaryLocation();
                if (liveAfter != null && liveAfter == next) {
                    return next;
                }
            }
            throw new RemoteException(
                    "InputManager primary button did not change (before=" + liveBefore
                            + ", after=" + liveAfter + ", requested=" + next + ").");
        }

        return useSamsungBackend ? next : aospVerified;
    }

    @Override
    public String getDiagnostics() throws RemoteException {
        CommandResult aosp = run(SETTINGS, "get", TABLE, AOSP_KEY);
        CommandResult samsungSetting = run(SETTINGS, "get", TABLE, SAMSUNG_KEY);
        CommandResult input = run(DUMPSYS, "input");
        Integer live = parsePrimaryLocation(input.output);

        StringBuilder report = new StringBuilder();
        report.append("manufacturer=").append(Build.MANUFACTURER)
                .append("\nbrand=").append(Build.BRAND)
                .append("\nmodel=").append(Build.MODEL)
                .append("\ndevice=").append(Build.DEVICE)
                .append("\nsdk=").append(Build.VERSION.SDK_INT)
                .append("\nrelease=").append(Build.VERSION.RELEASE)
                .append("\n").append(AOSP_KEY).append("=").append(aosp.output.trim())
                .append("\n").append(SAMSUNG_KEY).append("=").append(samsungSetting.output.trim())
                .append("\naosp_exit=").append(aosp.exitCode)
                .append("\nsamsung_setting_exit=").append(samsungSetting.exitCode)
                .append("\ninput_primary_location=")
                .append(live == null ? "not-found" : live)
                .append("\nselected_backend=")
                .append((isSamsungDevice() || parseBinaryValue(samsungSetting.output) != null)
                        ? "samsung+android" : "android")
                .append("\n\nRelevant dumpsys input lines:\n")
                .append(filterRelevantInputLines(input.output))
                .append("\n\nRelevant settings entries:\n")
                .append(settingsCandidates("system"))
                .append(settingsCandidates("global"))
                .append(settingsCandidates("secure"));
        return report.toString();
    }

    private static boolean isSamsungDevice() {
        return "samsung".equalsIgnoreCase(Build.MANUFACTURER)
                || "samsung".equalsIgnoreCase(Build.BRAND);
    }

    private static int readAospSwapState() throws RemoteException {
        CommandResult result = run(SETTINGS, "get", TABLE, AOSP_KEY);
        if (result.exitCode != 0) {
            throw new RemoteException("settings get failed for " + AOSP_KEY + ": " + result.output);
        }
        Integer value = parseBinaryValue(result.output);
        if (value != null) return value;
        String raw = result.output.trim();
        if (raw.isEmpty() || "null".equalsIgnoreCase(raw)
                || "false".equalsIgnoreCase(raw) || "off".equalsIgnoreCase(raw)
                || "left".equalsIgnoreCase(raw)) return 0;
        if ("true".equalsIgnoreCase(raw) || "on".equalsIgnoreCase(raw)
                || "right".equalsIgnoreCase(raw)) return 1;
        throw new RemoteException("Unexpected " + AOSP_KEY + " value: " + raw);
    }

    private static Integer readBinarySystemSetting(String key) throws RemoteException {
        CommandResult result = run(SETTINGS, "get", TABLE, key);
        if (result.exitCode != 0) return null;
        return parseBinaryValue(result.output);
    }

    private static Integer parseBinaryValue(String raw) {
        if (raw == null) return null;
        String value = raw.trim();
        if ("0".equals(value)) return 0;
        if ("1".equals(value)) return 1;
        return null;
    }

    private static void writeSystemSetting(String key, int value) throws RemoteException {
        CommandResult result = run(SETTINGS, "put", TABLE, key, Integer.toString(value));
        if (result.exitCode != 0) {
            throw new RemoteException("settings put failed for " + key + ": " + result.output);
        }
    }

    private static Integer readLivePrimaryLocation() throws RemoteException {
        CommandResult result = run(DUMPSYS, "input");
        if (result.exitCode != 0) return null;
        return parsePrimaryLocation(result.output);
    }

    private static Integer parsePrimaryLocation(String text) {
        Matcher matcher = PRIMARY_LOCATION_PATTERN.matcher(text == null ? "" : text);
        if (!matcher.find()) return null;
        try {
            int value = Integer.parseInt(matcher.group(1));
            return value == 0 || value == 1 ? value : null;
        } catch (NumberFormatException ignored) {
            return null;
        }
    }

    private static void sleep(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    private static String filterRelevantInputLines(String output) {
        if (output == null || output.isEmpty()) return "(none)\n";
        StringBuilder result = new StringBuilder();
        for (String line : output.split("\\R")) {
            String lower = line.toLowerCase(Locale.ROOT);
            if (lower.contains("primary mouse") || lower.contains("mouse button behavior")
                    || lower.contains("mouse acceleration") || lower.contains("scroll speed")) {
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
        if (filtered.length() == 0) filtered.append(table).append(":(no mouse/pointer entries found)\n");
        return filtered.toString();
    }

    private static CommandResult run(String... command) throws RemoteException {
        try {
            Process process = new ProcessBuilder(command).redirectErrorStream(true).start();
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
