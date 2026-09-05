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
                "Quick Settings cycle:\nOff → Portrait → 90° → 180° → 270° → Off\n\n" +
                "For stronger forcing, the app combines Android's system rotation lock with a tiny transparent orientation overlay.");
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

        Button off = new Button(this);
        off.setText("Turn forcing OFF and restore previous rotation setting");
        off.setOnClickListener(v -> {
            RotationController.setMode(this, RotationMode.OFF);
            refresh();
        });
        root.addView(off, matchWrap());

        TextView note = new TextView(this);
        note.setText(
                "Tap the tile to advance one state. Rapid taps are buffered for about 0.4 seconds after the most recent tap: every tap is counted, but only the final queued state is applied. " +
                "Long-press the tile to return here. If Android does not show the add-tile prompt, add “Rotate 90°” from Quick Settings edit mode.");
        note.setTextSize(14);
        note.setTextColor(Color.GRAY);
        note.setPadding(0, dp(18), 0, 0);
        root.addView(note, matchWrap());

        setContentView(root);
    }

    private void refresh() {
        boolean overlay = Settings.canDrawOverlays(this);
        boolean write = Settings.System.canWrite(this);
        RotationMode mode = RotationController.getMode(this);
        status.setText(
                "Overlay: " + (overlay ? "OK" : "needed") +
                "   •   Modify settings: " + (write ? "OK" : "needed") +
                "\nCurrent mode: " + mode.label);
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
                "Rotate 90°",
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
