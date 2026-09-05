package com.homayoun.mouseinstaller;

import android.os.Build;
import android.os.RemoteException;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

/** Runs as Shizuku's shell UID and performs the one-time legacy-target APK update. */
public final class InstallerUserService extends IInstallerService.Stub {
    private static final String TARGET_PACKAGE = "com.homayoun.mousebuttontoggle";
    private static final String PM = "/system/bin/pm";
    private static final String DUMPSYS = "/system/bin/dumpsys";

    public InstallerUserService() {
    }

    @Override
    public String probe() throws RemoteException {
        CommandResult id = run("/system/bin/id");
        return "sdk=" + Build.VERSION.SDK_INT
                + "\nrelease=" + Build.VERSION.RELEASE
                + "\nid_exit=" + id.exitCode
                + "\nid=" + id.output.trim();
    }

    @Override
    public String installApk(byte[] apkBytes) throws RemoteException {
        if (apkBytes == null || apkBytes.length < 1024) {
            throw remote("Bundled APK payload is missing or too small");
        }
        if (apkBytes[0] != 'P' || apkBytes[1] != 'K') {
            throw remote("Bundled payload is not an APK/ZIP file");
        }

        File temp = new File("/data/local/tmp/MouseButtonToggle-v1.0.8.apk");
        try {
            try (FileOutputStream output = new FileOutputStream(temp, false)) {
                output.write(apkBytes);
                output.flush();
            }
            temp.setReadable(true, false);

            CommandResult install = run(
                    PM,
                    "install",
                    "-r",
                    "--bypass-low-target-sdk-block",
                    temp.getAbsolutePath());

            StringBuilder report = new StringBuilder();
            report.append("install_exit=").append(install.exitCode)
                    .append("\ninstall_output=").append(install.output.trim());

            if (install.exitCode != 0 || !install.output.contains("Success")) {
                throw remote("Package install failed\n" + report);
            }

            CommandResult dump = run(DUMPSYS, "package", TARGET_PACKAGE);
            report.append("\nverify_exit=").append(dump.exitCode)
                    .append("\n").append(extractFacts(dump.output));

            if (dump.exitCode != 0
                    || !dump.output.contains("versionCode=9")
                    || !dump.output.contains("targetSdk=22")) {
                throw remote("Install command succeeded, but v1.0.8 verification failed\n" + report);
            }

            return report.toString();
        } catch (RemoteException e) {
            throw e;
        } catch (Throwable e) {
            RemoteException remote = remote(e.toString());
            remote.initCause(e);
            throw remote;
        } finally {
            try {
                if (temp.exists()) temp.delete();
            } catch (Throwable ignored) {
            }
        }
    }

    private static String extractFacts(String dump) {
        StringBuilder out = new StringBuilder();
        String[] lines = dump.split("\\r?\\n");
        for (String line : lines) {
            String t = line.trim();
            if (t.startsWith("versionCode=")
                    || t.startsWith("versionName=")
                    || t.startsWith("targetSdk=")) {
                if (out.length() > 0) out.append('\n');
                out.append(t);
            }
        }
        return out.length() == 0 ? "package_facts=not-found" : out.toString();
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
                    if (output.length() < 65536) output.append(line);
                }
            }
            int exit = process.waitFor();
            return new CommandResult(exit, output.toString());
        } catch (Throwable e) {
            RemoteException remote = remote(e.toString());
            remote.initCause(e);
            throw remote;
        }
    }

    private static RemoteException remote(String message) {
        return new RemoteException(message);
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
