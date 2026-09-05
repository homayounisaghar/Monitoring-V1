package com.homayoun.mousebuttontoggle;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.StatusBarManager;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.ComponentName;
import android.content.Intent;
import android.graphics.drawable.Icon;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.service.quicksettings.TileService;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

public final class MainActivity extends Activity {
    private TextView status;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(makeContentView());
    }

    @Override
    protected void onResume() {
        super.onResume();
        refreshStatus();
    }

    private View makeContentView() {
        int p = dp(24);
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(p, p, p, p);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        scroll.addView(root, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));

        TextView title = new TextView(this);
        title.setText("Mouse Button Toggle 1.0.6");
        title.setTextSize(26);
        title.setGravity(Gravity.CENTER);
        root.addView(title, matchWrap());

        TextView description = new TextView(this);
        if (MouseSettingsController.isSamsungDevice()) {
            description.setText("One Quick Settings control switches the physical mouse primary button between Left and Right.\n\nSamsung protects this setting from ordinary app writes. v1.0.6 keeps Shizuku out of the daily path and hides the Samsung Settings transition behind a short in-memory screen cover, then returns to the exact app you were using.");
        } else {
            description.setText("One Quick Settings control switches the physical mouse primary button between Left and Right.\n\nThis version does not use Shizuku. Grant Android's Modify system settings permission once, then the tile works independently.");
        }
        description.setTextSize(16);
        description.setPadding(0, dp(18), 0, dp(18));
        root.addView(description, matchWrap());

        status = new TextView(this);
        status.setTextSize(16);
        status.setTextIsSelectable(true);
        status.setPadding(dp(16), dp(16), dp(16), dp(16));
        root.addView(status, matchWrap());

        if (MouseSettingsController.isSamsungDevice()) {
            root.addView(button("Open Accessibility settings", v -> openAccessibilitySetup()), matchWrap());
        } else {
            root.addView(button("Grant Modify system settings", v -> grantWriteSettings()), matchWrap());
        }
        root.addView(button("Add Quick Panel control", v -> requestTile()), matchWrap());
        root.addView(button("Test seamless Left / Right switch", v -> testToggle()), matchWrap());
        root.addView(button("Show local mouse diagnostics", v -> showDiagnostics()), matchWrap());

        TextView note = new TextView(this);
        String placement = "One UI controls the initial location of third-party Quick Panel controls. After adding it, use the Quick Panel pencil/edit mode and drag the mouse control into the expandable/top Quick Settings area where you want it.";
        if (MouseSettingsController.isSamsungDevice()) {
            placement += "\n\nThe Accessibility helper is restricted to Android Settings. For the seamless cover, Android also grants it screenshot capability; the captured frame is kept only in RAM for the fraction of a second needed to hide Samsung Settings and is never saved or transmitted. If a secure app blocks screenshots, the fallback is a brief black cover instead of exposing Settings.";
        }
        note.setText(placement);
        note.setTextSize(14);
        note.setPadding(0, dp(18), 0, 0);
        root.addView(note, matchWrap());

        return scroll;
    }

    private void openAccessibilitySetup() {
        try {
            startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
            setStatus("Accessibility opened. Go to Installed apps -> Mouse Button Toggle and enable it.");
        } catch (Throwable e) {
            setStatus("Could not open Accessibility settings: " + message(e));
        }
    }

    private void grantWriteSettings() {
        if (MouseSettingsController.hasWritePermission(this)) {
            refreshStatus();
            return;
        }
        Intent intent = new Intent(
                Settings.ACTION_MANAGE_WRITE_SETTINGS,
                Uri.parse("package:" + getPackageName()));
        startActivity(intent);
    }

    private void requestTile() {
        if (Build.VERSION.SDK_INT >= 33) {
            StatusBarManager manager = getSystemService(StatusBarManager.class);
            if (manager == null) {
                setStatus("Quick Settings service is unavailable on this device.");
                return;
            }
            ComponentName component = new ComponentName(this, MouseToggleTileService.class);
            manager.requestAddTileService(
                    component,
                    "Mouse: Left / Right",
                    Icon.createWithResource(this, R.drawable.ic_mouse_toggle),
                    getMainExecutor(),
                    result -> setStatus("Add-control result: " + result
                            + ". One UI chooses the initial position; use Quick Panel edit mode to move it."));
        } else {
            setStatus("Open Quick Settings edit mode and drag 'Mouse: Left / Right' into the active tiles.");
        }
    }

    private void testToggle() {
        if (MouseSettingsController.isSamsungDevice()) {
            if (!SamsungMouseAccessibilityService.isEnabled(this)) {
                setStatus("Enable Mouse Button Toggle under Accessibility -> Installed apps first. Shizuku is not required.");
                openAccessibilitySetup();
                return;
            }
            if (!SamsungMouseAccessibilityService.requestSeamlessToggle(this)) {
                setStatus("Accessibility is enabled but its helper is not connected yet. Turn Mouse Button Toggle off/on once in Accessibility, then retry.");
                return;
            }
            setStatus("Seamless switch started. This app should stay visually in place while Samsung Settings is handled underneath.");
            return;
        }

        if (!MouseSettingsController.hasWritePermission(this)) {
            setStatus("Grant Modify system settings first.");
            grantWriteSettings();
            return;
        }
        try {
            int state = MouseSettingsController.togglePrimaryButtonDirect(this);
            setStatus(state == 1
                    ? "RIGHT mouse button is now primary. Test the physical mouse to confirm."
                    : "LEFT mouse button is now primary. Test the physical mouse to confirm.");
            TileService.requestListeningState(this, new ComponentName(this, MouseToggleTileService.class));
        } catch (Throwable e) {
            setStatus("Toggle failed: " + message(e));
            showDiagnostics();
        }
    }

    private void showDiagnostics() {
        String text = MouseSettingsController.diagnostics(this);

        TextView view = new TextView(this);
        view.setText(text);
        view.setTextSize(13);
        view.setTextIsSelectable(true);
        view.setPadding(dp(16), dp(12), dp(16), dp(12));

        ScrollView scroll = new ScrollView(this);
        scroll.addView(view);

        new AlertDialog.Builder(this)
                .setTitle("Mouse diagnostics")
                .setView(scroll)
                .setPositiveButton("Copy", (dialog, which) -> {
                    ClipboardManager clipboard = getSystemService(ClipboardManager.class);
                    if (clipboard != null) {
                        clipboard.setPrimaryClip(ClipData.newPlainText("Mouse diagnostics", text));
                        Toast.makeText(this, "Diagnostics copied", Toast.LENGTH_SHORT).show();
                    }
                })
                .setNegativeButton("Close", null)
                .show();
    }

    private void refreshStatus() {
        if (MouseSettingsController.isSamsungDevice()) {
            if (!SamsungMouseAccessibilityService.isEnabled(this)) {
                setStatus("Setup required: Accessibility -> Installed apps -> Mouse Button Toggle -> On. Shizuku is not required.");
                return;
            }
            if (!SamsungMouseAccessibilityService.isConnected()) {
                setStatus("Accessibility is enabled; waiting for its helper service to reconnect. If this persists, turn it off/on once.");
                return;
            }
            if (SamsungMouseAccessibilityService.isPending(this)) {
                setStatus("Seamless Samsung switch is in progress...");
                return;
            }
            int state = MouseSettingsController.readPrimaryButton(this);
            setStatus(state == 1
                    ? "Ready. Current primary mouse button: RIGHT. Seamless mode active; Shizuku is not required."
                    : "Ready. Current primary mouse button: LEFT. Seamless mode active; Shizuku is not required.");
            TileService.requestListeningState(this, new ComponentName(this, MouseToggleTileService.class));
            return;
        }

        if (!MouseSettingsController.hasWritePermission(this)) {
            setStatus("Setup required: grant Modify system settings once. Shizuku is not required.");
            return;
        }
        try {
            int state = MouseSettingsController.readPrimaryButton(this);
            setStatus(state == 1
                    ? "Ready. Current primary mouse button: RIGHT. Shizuku is not required."
                    : "Ready. Current primary mouse button: LEFT. Shizuku is not required.");
            TileService.requestListeningState(this, new ComponentName(this, MouseToggleTileService.class));
        } catch (Throwable e) {
            setStatus("Permission granted, but reading mouse state failed: " + message(e));
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
