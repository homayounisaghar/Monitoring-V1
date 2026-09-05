package com.homayoun.rotationtile;

import android.app.Activity;
import android.app.StatusBarManager;
import android.content.ComponentName;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.Icon;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.util.concurrent.Executor;

public class MainActivity extends Activity {
    private TextView status;
    private Button overrideButton;
    private boolean tileRequestAttemptedThisLaunch;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildUi();
    }

    @Override
    protected void onResume() {
        super.onResume();
        refresh();

        boolean autoTileRequestDone = getSharedPreferences("rotation_tile_ui", MODE_PRIVATE)
                .getBoolean("auto_tile_request_done", false);
        if (RotationController.hasRequiredPermissions(this)
                && !autoTileRequestDone
                && !tileRequestAttemptedThisLaunch) {
            tileRequestAttemptedThisLaunch = true;
            getSharedPreferences("rotation_tile_ui", MODE_PRIVATE)
                    .edit()
                    .putBoolean("auto_tile_request_done", true)
                    .apply();
            requestTileIfSupported();
        }
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(24), dp(28), dp(24), dp(24));
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setBackgroundColor(Color.rgb(250, 250, 250));

        TextView title = new TextView(this);
        title.setText("Rotation Tile");
        title.setTextSize(28);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        title.setTextColor(Color.BLACK);
        root.addView(title, matchWrap());

        TextView description = new TextView(this);
        description.setText(
                "Long-press the Quick Settings tile to toggle the rotation override. " +
                "Turning it on locks the exact angle the display already has; turning it off releases the lock without choosing another angle.\n\n" +
                "While override is ON, short taps rotate through 0° / 90° / 180° / 270°. " +
                "Rapid taps are grouped for about 0.4 seconds after the last tap.");
        description.setTextSize(16);
        description.setTextColor(Color.DKGRAY);
        description.setPadding(0, dp(18), 0, dp(20));
        root.addView(description, matchWrap());

        status = new TextView(this);
        status.setTextSize(16);
        status.setTypeface(Typeface.DEFAULT_BOLD);
        status.setTextColor(Color.BLACK);
        status.setPadding(0, 0, 0, dp(14));
        root.addView(status, matchWrap());

        Button overlay = new Button(this);
        overlay.setText("1. Allow display over other apps");
        overlay.setOnClickListener(v -> startActivity(RotationController.overlayPermissionIntent(this)));
        root.addView(overlay, matchWrap());

        Button writeSettings = new Button(this);
        writeSettings.setText("2. Allow modify system settings");
        writeSettings.setOnClickListener(v -> startActivity(RotationController.writeSettingsPermissionIntent(this)));
        root.addView(writeSettings, matchWrap());

        Button addTile = new Button(this);
        addTile.setText("3. Add Quick Settings tile");
        addTile.setOnClickListener(v -> requestTileIfSupported());
        root.addView(addTile, matchWrap());

        overrideButton = new Button(this);
        overrideButton.setOnClickListener(v -> {
            RotationTileService.cancelPendingBatch(this);
            if (!RotationController.isEnabled(this)
                    && !RotationController.hasRequiredPermissions(this)) {
                refresh();
                return;
            }
            RotationController.toggleOverride(this);
            RotationTileService.requestTileRefresh(this);
            refresh();
        });
        root.addView(overrideButton, matchWrap());

        TextView note = new TextView(this);
        note.setText(
                "Normal taps do nothing while override is OFF. Long-press toggles override. " +
                "When override is released, Android auto-rotation is enabled, so the screen may rotate immediately if the device posture calls for it.");
        note.setTextSize(14);
        note.setTextColor(Color.GRAY);
        note.setPadding(0, dp(18), 0, 0);
        root.addView(note, matchWrap());

        setContentView(root);
    }

    private void refresh() {
        boolean overlay = Settings.canDrawOverlays(this);
        boolean write = Settings.System.canWrite(this);
        boolean enabled = RotationController.isEnabled(this);
        RotationMode locked = RotationController.getLockedMode(this);
        RotationMode current = RotationController.getCurrentDisplayMode(this);

        status.setText(
                "Overlay: " + (overlay ? "OK" : "needed") +
                "   •   Modify settings: " + (write ? "OK" : "needed") +
                "\nOverride: " + (enabled ? "ON" : "OFF") +
                (enabled ? "   •   Locked: " + locked.label : "   •   Display now: " + current.label));

        if (overrideButton != null) {
            overrideButton.setText(enabled
                    ? "Turn override OFF and follow device auto-rotation"
                    : "Lock the current display angle now");
        }
    }

    private void requestTileIfSupported() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return;
        StatusBarManager manager = getSystemService(StatusBarManager.class);
        if (manager == null) return;

        ComponentName component = new ComponentName(this, RotationTileService.class);
        Icon icon = Icon.createWithResource(this, R.drawable.ic_rotation);
        Executor executor = getMainExecutor();
        manager.requestAddTileService(
                component,
                "Rotation",
                icon,
                executor,
                result -> refresh());
    }

    private LinearLayout.LayoutParams matchWrap() {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        p.setMargins(0, dp(5), 0, dp(5));
        return p;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
