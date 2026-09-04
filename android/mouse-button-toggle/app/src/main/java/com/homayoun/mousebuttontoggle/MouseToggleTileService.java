package com.homayoun.mousebuttontoggle;

import android.app.PendingIntent;
import android.content.Intent;
import android.graphics.drawable.Icon;
import android.os.Build;
import android.service.quicksettings.Tile;
import android.service.quicksettings.TileService;
import android.widget.Toast;

public final class MouseToggleTileService extends TileService {
    @Override
    public void onStartListening() {
        super.onStartListening();
        if (!ShizukuMouseBridge.hasPermission()) {
            showNeedsSetup();
            return;
        }
        ShizukuMouseBridge.read(this, (state, error) -> getMainExecutor().execute(() -> {
            if (error != null || state == null) {
                showError(error);
            } else {
                showState(state);
            }
        }));
    }

    @Override
    public void onClick() {
        super.onClick();
        if (!ShizukuMouseBridge.hasPermission()) {
            showNeedsSetup();
            openSetup();
            return;
        }

        Tile tile = getQsTile();
        if (tile != null) {
            tile.setLabel("Mouse: switching…");
            tile.setState(Tile.STATE_UNAVAILABLE);
            tile.updateTile();
        }

        ShizukuMouseBridge.toggle(this, (state, error) -> getMainExecutor().execute(() -> {
            if (error != null || state == null) {
                showError(error);
            } else {
                showState(state);
            }
        }));
    }

    private void showState(int swapped) {
        Tile tile = getQsTile();
        if (tile == null) return;
        boolean rightPrimary = swapped == 1;
        tile.setIcon(Icon.createWithResource(this, R.drawable.ic_mouse_toggle));
        tile.setLabel(rightPrimary ? "Mouse: Right" : "Mouse: Left");
        tile.setSubtitle(rightPrimary ? "Right click is primary" : "Left click is primary");
        tile.setState(rightPrimary ? Tile.STATE_ACTIVE : Tile.STATE_INACTIVE);
        tile.updateTile();
    }

    private void showNeedsSetup() {
        Tile tile = getQsTile();
        if (tile == null) return;
        tile.setIcon(Icon.createWithResource(this, R.drawable.ic_mouse_toggle));
        tile.setLabel("Mouse: setup");
        tile.setSubtitle("Grant Shizuku permission");
        tile.setState(Tile.STATE_UNAVAILABLE);
        tile.updateTile();
    }

    private void showError(String error) {
        Tile tile = getQsTile();
        if (tile != null) {
            tile.setLabel("Mouse: error");
            tile.setSubtitle("Open app for details");
            tile.setState(Tile.STATE_UNAVAILABLE);
            tile.updateTile();
        }
        Toast.makeText(this, "Mouse toggle failed: " + (error == null ? "unknown error" : error), Toast.LENGTH_LONG).show();
    }

    private void openSetup() {
        Intent intent = new Intent(this, MainActivity.class)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        if (Build.VERSION.SDK_INT >= 34) {
            PendingIntent pendingIntent = PendingIntent.getActivity(
                    this, 7, intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            startActivityAndCollapse(pendingIntent);
        } else {
            startActivityAndCollapse(intent);
        }
    }
}
