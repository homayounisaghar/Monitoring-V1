package com.homayoun.mousebuttontoggle;

import android.os.Build;
import android.os.RemoteException;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

public final class MouseSettingsUserService extends IMouseSettingsService.Stub {
    private static final String SETTINGS = "/system/bin/settings";
    private static final String TABLE = "system";
    private static final String KEY = "mouse_swap_primary_button";

    public MouseSettingsUserService() {
    }

    @Override
    public void destroy() {
        System.exit(0);
    }

    @Override
    public int getSwapState() throws RemoteException {
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

    @Override
    public int toggleSwapState() throws RemoteException {
        int next = getSwapState() == 1 ? 0 : 1;
        CommandResult write = run(SETTINGS, "put", TABLE, KEY, Integer.toString(next));
        if (write.exitCode != 0) {
            throw new RemoteException("settings put failed: " + write.output);
        }
        int verified = getSwapState();
        if (verified != next) {
            throw new RemoteException("Setting did not persist. Expected " + next + " but read " + verified);
        }
        return verified;
    }

    @Override
    public String getDiagnostics() throws RemoteException {
        CommandResult result = run(SETTINGS, "get", TABLE, KEY);
        return "manufacturer=" + Build.MANUFACTURER
                + "\nmodel=" + Build.MODEL
                + "\nsdk=" + Build.VERSION.SDK_INT
                + "\nrelease=" + Build.VERSION.RELEASE
                + "\n" + KEY + "=" + result.output.trim()
                + "\nexit=" + result.exitCode;
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
