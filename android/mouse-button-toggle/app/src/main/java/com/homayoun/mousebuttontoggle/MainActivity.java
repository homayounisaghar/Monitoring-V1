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
        title.setText("Mouse Button Toggle 1.0.8");
        title.setTextSize(26);
        title.setGravity(Gravity.CENTER);
        root.addView(title, matchWrap());

        TextView description = new TextView(this);
        description.setText("Experimental true-background build. It opens no Samsung Settings page, uses no Accessibility helper, overlay, or Shizuku.\n\nOn Samsung this APK deliberately targets Android 5.1 / API 22 so Android's legacy private-System-setting compatibility path can be tested for primary_mouse_button_option. The physical device remains Android 16; only this app's declared target SDK is old.");
        description.setTextSize(16);
        description.setPadding(0, dp(18), 0, dp(18));
        root.addView(description, matchWrap());

        status = new TextView(this);
        status.setTextSize(16);
        status.setTextIsSelectable(true);
        status.setPadding(dp(16), dp(16), dp(16), dp(16));
        root.addView(status, matchWrap());

        root.addView(button("Grant Modify system settings", v -> grantWriteSettings()), matchWrap());
        root.addView(button("Add Quick Panel control", v -> requestTile()), matchWrap());
        root.addView(button("Test direct background Left / Right switch", v -> testToggle()), matchWrap());
        root.addView(button("Show local mouse diagnostics", v -> showDiagnostics()), matchWrap());

        TextView note = new TextView(this);
        note.setText("Android 16 normally blocks installation of very old-target apps. Install/update this test build with ADB using --bypass-low-target-sdk-block. If One UI still blocks the private setting write after that, this experiment is finished and the project should return to v1.0.6.");
        note.setTextSize(14);
        note.setPadding(0, dp(18), 0, 0);
        root.addView(note, matchWrap());
        return scroll;
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
        if (!MouseSettingsController.hasWritePermission(this)) {
            setStatus("Grant Modify system settings first.");
            grantWriteSettings();
            return;
        }
        try {
            int state = MouseSettingsController.togglePrimaryButtonDirect(this);
            setStatus(state == 1
                    ? "Success. RIGHT mouse button is now primary. No page was opened."
                    : "Success. LEFT mouse button is now primary. No page was opened.");
            TileService.requestListeningState(this, new ComponentName(this, MouseToggleTileService.class));
        } catch (Throwable e) {
            setStatus("Legacy direct switch failed: " + message(e)
                    + "\nIf diagnostics confirm targetSdk=22, this route is blocked on this One UI build and we should return to v1.0.6.");
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
        int state = MouseSettingsController.readPrimaryButton(this);
        String permission = MouseSettingsController.hasWritePermission(this) ? "granted" : "not granted";
        setStatus((state == 1
                        ? "Current primary mouse button: RIGHT."
                        : "Current primary mouse button: LEFT.")
                + "\nModify system settings: " + permission
                + "\nApp target SDK reported by Android: " + MouseSettingsController.appTargetSdk(this)
                + "\nBackend: "
                + (MouseSettingsController.isSamsungDevice()
                        ? "Samsung legacy direct"
                        : "Android direct"));
        TileService.requestListeningState(this, new ComponentName(this, MouseToggleTileService.class));
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
