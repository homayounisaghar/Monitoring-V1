package com.homayoun.mousebuttontoggle;

import android.app.Activity;
import android.app.StatusBarManager;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.PackageManager;
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
import android.widget.TextView;

import rikka.shizuku.Shizuku;

public final class MainActivity extends Activity {
    private static final int SHIZUKU_PERMISSION_REQUEST = 100;
    private TextView status;

    private final Shizuku.OnBinderReceivedListener binderReceivedListener = this::refreshStatus;
    private final Shizuku.OnBinderDeadListener binderDeadListener = this::refreshStatus;
    private final Shizuku.OnRequestPermissionResultListener permissionResultListener = (requestCode, grantResult) -> {
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
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(p, p, p, p);
        root.setGravity(Gravity.CENTER_HORIZONTAL);

        TextView title = new TextView(this);
        title.setText("Mouse Button Toggle");
        title.setTextSize(26);
        title.setGravity(Gravity.CENTER);
        root.addView(title, matchWrap());

        TextView description = new TextView(this);
        description.setText("One Quick Settings tile switches the system primary mouse button between Left and Right.\n\nShizuku is used only to write the protected Android mouse setting.");
        description.setTextSize(16);
        description.setPadding(0, dp(18), 0, dp(18));
        root.addView(description, matchWrap());

        status = new TextView(this);
        status.setTextSize(16);
        status.setPadding(dp(16), dp(16), dp(16), dp(16));
        root.addView(status, matchWrap());

        root.addView(button("Grant Shizuku permission", v -> grantShizuku()), matchWrap());
        root.addView(button("Add Quick Settings tile", v -> requestTile()), matchWrap());
        root.addView(button("Test: switch Left / Right now", v -> testToggle()), matchWrap());
        root.addView(button("Open Shizuku", v -> openShizuku()), matchWrap());

        TextView note = new TextView(this);
        note.setText("Daily use: pull down Quick Settings and tap ‘Mouse: Left / Right’. No Accessibility service and no permanent notification are used.");
        note.setTextSize(14);
        note.setPadding(0, dp(18), 0, 0);
        root.addView(note, matchWrap());

        return root;
    }

    private void grantShizuku() {
        if (!Shizuku.pingBinder()) {
            setStatus("Shizuku is not running. Open Shizuku, start it, then return here.");
            return;
        }
        try {
            if (Shizuku.checkSelfPermission() == PackageManager.PERMISSION_GRANTED) {
                refreshStatus();
            } else if (Shizuku.shouldShowRequestPermissionRationale()) {
                setStatus("Shizuku permission was denied. Allow this app in Shizuku's Authorized applications screen.");
                openShizuku();
            } else {
                Shizuku.requestPermission(SHIZUKU_PERMISSION_REQUEST);
            }
        } catch (Throwable e) {
            setStatus("Could not request Shizuku permission: " + e);
        }
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
                    result -> setStatus("Add-tile result: " + result + ". If accepted, the tile is now in Quick Settings."));
        } else {
            setStatus("Open Quick Settings edit mode and drag ‘Mouse: Left / Right’ into the active tiles.");
        }
    }

    private void testToggle() {
        if (!ShizukuMouseBridge.hasPermission()) {
            setStatus("Grant Shizuku permission first.");
            grantShizuku();
            return;
        }
        setStatus("Switching…");
        ShizukuMouseBridge.toggle(this, (state, error) -> getMainExecutor().execute(() -> {
            if (error != null || state == null) {
                setStatus("Toggle failed: " + (error == null ? "unknown error" : error));
            } else {
                setStatus(state == 1 ? "Working. RIGHT mouse button is now primary." : "Working. LEFT mouse button is now primary.");
                TileService.requestListeningState(this, new ComponentName(this, MouseToggleTileService.class));
            }
        }));
    }

    private void refreshStatus() {
        runOnUiThread(() -> {
            if (!Shizuku.pingBinder()) {
                setStatus("1/2: Shizuku is not running. Start Shizuku first.");
                return;
            }
            if (!ShizukuMouseBridge.hasPermission()) {
                setStatus("1/2: Shizuku is running. Tap ‘Grant Shizuku permission’. ");
                return;
            }
            setStatus("2/2: Permission granted. Reading current mouse state…");
            ShizukuMouseBridge.read(this, (state, error) -> getMainExecutor().execute(() -> {
                if (error != null || state == null) {
                    setStatus("Permission granted, but reading the mouse setting failed: " + (error == null ? "unknown error" : error));
                } else {
                    setStatus(state == 1
                            ? "Ready. Current primary mouse button: RIGHT."
                            : "Ready. Current primary mouse button: LEFT.");
                    TileService.requestListeningState(this, new ComponentName(this, MouseToggleTileService.class));
                }
            }));
        });
    }

    private void openShizuku() {
        Intent launch = getPackageManager().getLaunchIntentForPackage("moe.shizuku.privileged.api");
        if (launch != null) {
            startActivity(launch);
            return;
        }
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=moe.shizuku.privileged.api")));
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
}
