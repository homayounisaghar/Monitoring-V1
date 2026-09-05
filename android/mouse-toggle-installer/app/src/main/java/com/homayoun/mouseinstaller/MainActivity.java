package com.homayoun.mouseinstaller;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.security.MessageDigest;
import java.util.Locale;

import rikka.shizuku.Shizuku;

public final class MainActivity extends Activity {
    private static final int SHIZUKU_PERMISSION_REQUEST = 701;
    private static final String TARGET_PACKAGE = "com.homayoun.mousebuttontoggle";
    private static final String ASSET_NAME = "MouseButtonToggle-v1.0.8.apk";
    private static final String EXPECTED_SHA256 =
            "2710c765cf21b7fea794e54a476775025cdb800205def814f905c5a7ec652402";

    private TextView status;
    private boolean installing;

    private final Shizuku.OnBinderReceivedListener binderReceivedListener = this::refreshStatus;
    private final Shizuku.OnBinderDeadListener binderDeadListener = this::refreshStatus;
    private final Shizuku.OnRequestPermissionResultListener permissionResultListener =
            (requestCode, grantResult) -> {
                if (requestCode == SHIZUKU_PERMISSION_REQUEST) refreshStatus();
            };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(makeContentView());
        Shizuku.addBinderReceivedListenerSticky(binderReceivedListener);
        Shizuku.addBinderDeadListener(binderDeadListener);
        Shizuku.addRequestPermissionResultListener(permissionResultListener);
        refreshStatus();
    }

    @Override
    protected void onDestroy() {
        Shizuku.removeBinderReceivedListener(binderReceivedListener);
        Shizuku.removeBinderDeadListener(binderDeadListener);
        Shizuku.removeRequestPermissionResultListener(permissionResultListener);
        super.onDestroy();
    }

    private View makeContentView() {
        int p = dp(24);
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(p, p, p, p);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        scroll.addView(root, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT,
                ScrollView.LayoutParams.WRAP_CONTENT));

        TextView title = new TextView(this);
        title.setText("Mouse Toggle Installer Helper");
        title.setTextSize(26);
        title.setGravity(Gravity.CENTER);
        root.addView(title, matchWrap());

        TextView description = new TextView(this);
        description.setText(
                "This one-time helper contains the verified Mouse Button Toggle v1.0.8 APK inside itself. "
                        + "It uses Shizuku only to run Android's package installer with the low-target-SDK bypass flag.\n\n"
                        + "After v1.0.8 is installed, this helper is no longer needed and can be uninstalled.");
        description.setTextSize(16);
        description.setPadding(0, dp(18), 0, dp(18));
        root.addView(description, matchWrap());

        status = new TextView(this);
        status.setTextSize(15);
        status.setTextIsSelectable(true);
        status.setPadding(dp(16), dp(16), dp(16), dp(16));
        root.addView(status, matchWrap());

        root.addView(button("Grant Shizuku permission", v -> grantShizuku()), matchWrap());
        root.addView(button("Install Mouse Button Toggle v1.0.8", v -> installTarget()), matchWrap());
        root.addView(button("Open Mouse Button Toggle", v -> openTarget()), matchWrap());
        root.addView(button("Open Shizuku", v -> openShizuku()), matchWrap());

        TextView note = new TextView(this);
        note.setText(
                "The helper preserves the existing Mouse Button Toggle app data and signature lineage by using an in-place package update (-r). "
                        + "It does not uninstall the existing app first.");
        note.setTextSize(14);
        note.setPadding(0, dp(18), 0, 0);
        root.addView(note, matchWrap());

        return scroll;
    }

    private void grantShizuku() {
        if (!Shizuku.pingBinder()) {
            setStatus("Shizuku is not running. Start Shizuku, then return here.");
            return;
        }
        try {
            if (ShizukuInstallerBridge.hasPermission()) {
                refreshStatus();
            } else if (Shizuku.shouldShowRequestPermissionRationale()) {
                setStatus("Shizuku permission was denied. Allow Mouse Toggle Installer in Shizuku's Authorized applications screen.");
                openShizuku();
            } else {
                Shizuku.requestPermission(SHIZUKU_PERMISSION_REQUEST);
            }
        } catch (Throwable e) {
            setStatus("Could not request Shizuku permission: " + message(e));
        }
    }

    private void installTarget() {
        if (installing) return;
        if (!Shizuku.pingBinder()) {
            setStatus("Shizuku is not running. Start it first.");
            return;
        }
        if (!ShizukuInstallerBridge.hasPermission()) {
            setStatus("Grant Shizuku permission first.");
            grantShizuku();
            return;
        }

        final byte[] apk;
        final String sha;
        try {
            apk = readBundledApk();
            sha = sha256(apk);
        } catch (Throwable e) {
            setStatus("Bundled v1.0.8 APK could not be read: " + message(e));
            return;
        }
        if (!EXPECTED_SHA256.equalsIgnoreCase(sha)) {
            setStatus("Safety check failed. Bundled APK SHA-256 is " + sha
                    + " but expected " + EXPECTED_SHA256 + ". Installation was not attempted.");
            return;
        }

        installing = true;
        setStatus("Installing v1.0.8 through Shizuku shell…\nPayload SHA-256 verified: " + sha);
        ShizukuInstallerBridge.install(this, apk, (report, error) -> getMainExecutor().execute(() -> {
            installing = false;
            if (error != null) {
                setStatus("Installation failed:\n" + error);
                return;
            }
            setStatus("v1.0.8 installed successfully.\n\n" + report
                    + "\n\nYou can now open Mouse Button Toggle and test the true-background switch. "
                    + "This Installer Helper can be removed afterward.");
        }));
    }

    private void refreshStatus() {
        runOnUiThread(() -> {
            if (installing) return;
            String installed = installedTargetSummary();
            String asset = bundledAssetSummary();
            if (!Shizuku.pingBinder()) {
                setStatus("Shizuku: NOT RUNNING\n" + installed + "\n" + asset
                        + "\n\nStart Shizuku first.");
                return;
            }
            if (!ShizukuInstallerBridge.hasPermission()) {
                setStatus("Shizuku: RUNNING, permission not granted\n" + installed + "\n" + asset
                        + "\n\nTap Grant Shizuku permission.");
                return;
            }
            setStatus("Shizuku: READY\n" + installed + "\n" + asset
                    + "\n\nTap Install Mouse Button Toggle v1.0.8.");
        });
    }

    private String installedTargetSummary() {
        try {
            PackageInfo info = getPackageManager().getPackageInfo(TARGET_PACKAGE, 0);
            long versionCode = info.getLongVersionCode();
            int targetSdk = info.applicationInfo == null ? -1 : info.applicationInfo.targetSdkVersion;
            return "Currently installed Mouse Button Toggle: version=" + info.versionName
                    + " (code " + versionCode + "), targetSdk=" + targetSdk;
        } catch (PackageManager.NameNotFoundException e) {
            return "Currently installed Mouse Button Toggle: not found";
        } catch (Throwable e) {
            return "Currently installed Mouse Button Toggle: could not inspect (" + message(e) + ")";
        }
    }

    private String bundledAssetSummary() {
        try {
            byte[] apk = readBundledApk();
            String sha = sha256(apk);
            return "Bundled v1.0.8 payload: " + apk.length + " bytes, SHA-256=" + sha
                    + (EXPECTED_SHA256.equalsIgnoreCase(sha) ? " [OK]" : " [MISMATCH]");
        } catch (Throwable e) {
            return "Bundled v1.0.8 payload: missing/error (" + message(e) + ")";
        }
    }

    private byte[] readBundledApk() throws Exception {
        try (InputStream input = getAssets().open(ASSET_NAME);
             ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[16384];
            int read;
            while ((read = input.read(buffer)) != -1) {
                output.write(buffer, 0, read);
            }
            return output.toByteArray();
        }
    }

    private static String sha256(byte[] bytes) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hash = digest.digest(bytes);
        StringBuilder out = new StringBuilder(hash.length * 2);
        for (byte b : hash) out.append(String.format(Locale.ROOT, "%02x", b & 0xff));
        return out.toString();
    }

    private void openTarget() {
        Intent launch = getPackageManager().getLaunchIntentForPackage(TARGET_PACKAGE);
        if (launch == null) {
            setStatus("Mouse Button Toggle is not installed or cannot be launched yet.");
            return;
        }
        startActivity(launch);
    }

    private void openShizuku() {
        Intent launch = getPackageManager().getLaunchIntentForPackage("moe.shizuku.privileged.api");
        if (launch != null) {
            startActivity(launch);
            return;
        }
        try {
            startActivity(new Intent(Intent.ACTION_VIEW,
                    Uri.parse("market://details?id=moe.shizuku.privileged.api")));
        } catch (Throwable ignored) {
            startActivity(new Intent(Settings.ACTION_APPLICATION_SETTINGS));
        }
    }

    private void setStatus(String text) {
        status.setText(text);
    }

    private Button button(String text, View.OnClickListener listener) {
        Button button = new Button(this);
        button.setText(text);
        button.setAllCaps(false);
        button.setOnClickListener(listener);
        return button;
    }

    private LinearLayout.LayoutParams matchWrap() {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0, dp(6), 0, dp(6));
        return lp;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private static String message(Throwable throwable) {
        String message = throwable.getMessage();
        return message == null ? throwable.toString() : message;
    }
}
