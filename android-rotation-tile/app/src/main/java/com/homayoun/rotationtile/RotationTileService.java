package com.homayoun.rotationtile;

import android.app.PendingIntent;
import android.content.Intent;
import android.graphics.drawable.Icon;
import android.os.Build;
import android.service.quicksettings.Tile;
import android.service.quicksettings.TileService;

public class RotationTileService extends TileService {
    @Override
    public void onStartListening() {
        super.onStartListening();
        updateTile();
    }

    @Override
    public void onClick() {
        super.onClick();
        RotationMode current = RotationController.getMode(this);
        RotationMode next = current.next();

        if (next != RotationMode.OFF && !RotationController.hasRequiredPermissions(this)) {
            openSetup();
            return;
        }

        RotationController.setMode(this, next);
        updateTile();
    }

    private void openSetup() {
        Intent intent = new Intent(this, MainActivity.class)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        if (Build.VERSION.SDK_INT >= 34) {
            PendingIntent pendingIntent = PendingIntent.getActivity(
                    this,
                    200,
                    intent,
                    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            startActivityAndCollapse(pendingIntent);
        } else {
            startActivityAndCollapse(intent);
        }
    }

    private void updateTile() {
        Tile tile = getQsTile();
        if (tile == null) return;

        RotationMode mode = RotationController.getMode(this);
        tile.setIcon(Icon.createWithResource(this, R.drawable.ic_rotation));
        tile.setLabel("Rotate 90°");
        tile.setState(mode == RotationMode.OFF ? Tile.STATE_INACTIVE : Tile.STATE_ACTIVE);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            tile.setSubtitle(mode.label);
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            tile.setContentDescription("Rotate 90°. " + mode.label);
        }
        tile.updateTile();
    }
}
