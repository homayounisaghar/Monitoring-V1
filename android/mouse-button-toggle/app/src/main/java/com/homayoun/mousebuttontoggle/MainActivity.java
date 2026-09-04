package com.homayoun.mousebuttontoggle;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.StatusBarManager;
import android.content.ClipData;
import android.content.ClipboardManager;
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
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

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
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(p, p, p, p);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        scroll.addView(root, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));

        TextView title = new TextView(this);
        title.setText("Mouse Button Toggle 1.0.1");
        title.setTextSize(26);
        title.setGravity(Gravity.CENTER);
        root.addView(title, matchWrap());

        TextView description = new TextView(this);
        description.setText("One Quick Settings control switches the physical mouse primary button between Left and Right.\n\nShizuku is used only for protected input/settings access.");
        description.setTextSize(16);
        description.setPadding(0, dp(18), 0, dp(18));
        root.addView(description, matchWrap());

        status = new TextView(this);
        status.setTextSize(16);
        status.setTextIsSelectable(true);
        status.setPadding(dp(16), dp(16), dp(16), dp(16));
        root.addView(status, matchWrap());

        Button grant = button("Grant Shizuku permission", v -> grantShizuku());
        root.addView(grant, matchWrap());

        Button addTile = button("Add Quick Panel control", v -> requestTile());
        root.addView(addTile, matchWrap());

        Button test = button("Test: switch Left / Right now", v -> testToggle());
        root.addView(test, matchWrap());

        Button diagnostics = button("Run Samsung mouse diagnostics", v -> runDiagnostics());
        root.addView(diagnostics, matchWrap());

        Button openShizuku = button("Open Shizuku", v -> openShizuku());
        root.addView(openShizuku, matchWrap());

        TextView note = new TextView(this);
        note.setText("One UI controls the initial location of third-party Quick Panel controls. After adding it, use the Quick Panel pencil/edit mode and drag the mouse control into the expandable/top Quick Settings area where you want it. The app cannot choose that exact slot itself.");
        note.setTextSize(14);
        note.setPadding(0, dp(18), 0, 0);
        root.addView(note, matchWrap());

        return scroll;
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
                    result -> setStatus("Add-control result: " + result
                            + ". One UI chooses the initial position. Use Quick Panel edit mode to drag it into the top/expandable Quick Settings area."));
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
        setStatus("Switching and checking Samsung input state…");
        ShizukuMouseBridge.toggle(this, (state, error) -> getMainExecutor().execute(() -> {
            if (error != null || state == null) {
                setStatus("Toggle failed: " + (error == null ? "unknown error" : error));
                if (error != null && error.contains("Samsung input state did not change")) {
                    runDiagnostics();
                }
            } else {
                setStatus(state == 1
                        ? "Working. RIGHT mouse button is now primary."
                        : "Working. LEFT mouse button is now primary.");
                TileService.requestListeningState(this, new ComponentName(this, MouseToggleTileService.class));
            }
        }));
    }

    private void runDiagnostics() {
        if (!ShizukuMouseBridge.hasPermission()) {
            setStatus("Grant Shizuku permission first, then run diagnostics.");
            grantShizuku();
            return;
        }
        setStatus("Collecting Samsung mouse diagnostics…");
        ShizukuMouseBridge.diagnostics(this, (text, error) -> getMainExecutor().execute(() -> {
            if (error != null || text == null) {
                setStatus("Diagnostics failed: " + (error == null ? "unknown error" : error));
                return;
            }
            setStatus("Diagnostics collected. A report window is open; use Copy if we need the Samsung-specific backend details.");
            showDiagnostics(text);
        }));
    }

    private void showDiagnostics(String text) {
        TextView view = new TextView(this);
        view.setText(text);
        view.setTextSize(13);
        view.setTextIsSelectable(true);
        view.setPadding(dp(16), dp(12), dp(16), dp(12));

        ScrollView scroll = new ScrollView(this);
        scroll.addView(view);

        new AlertDialog.Builder(this)
                .setTitle("Samsung mouse diagnostics")
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
        runOnUiThread(() -> {
            if (!Shizuku.pingBinder()) {
                setStatus("1/2: Shizuku is not running. Start Shizuku first.");
                return;
            }
            if (!ShizukuMouseBridge.hasPermission()) {
                setStatus("1/2: Shizuku is running. Tap ‘Grant Shizuku permission’.");
                return;
            }
            setStatus("2/2: Permission granted. Reading current Samsung/Android mouse state…");
            ShizukuMouseBridge.read(this, (state, error) -> getMainExecutor().execute(() -> {
                if (error != null || state == null) {
                    setStatus("Permission granted, but reading the mouse state failed: "
                            + (error == null ? "unknown error" : error));
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
