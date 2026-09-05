package com.homayoun.rotationtile;

import android.app.PendingIntent;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.graphics.drawable.Icon;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.service.quicksettings.Tile;
import android.service.quicksettings.TileService;

import java.lang.ref.WeakReference;

public class RotationTileService extends TileService {
    private static final long MULTI_TAP_SETTLE_MS = 400L;
    private static final Object TAP_LOCK = new Object();
    private static final Handler TAP_HANDLER = new Handler(Looper.getMainLooper());

    private static RotationMode pendingTarget;
    private static int pendingTapCount;
    private static long pendingGeneration;
    private static Context appContext;
    private static WeakReference<RotationTileService> latestService = new WeakReference<>(null);

    @Override
    public void onStartListening() {
        super.onStartListening();
        rememberService();
        updateTile();
    }

    @Override
    public void onClick() {
        super.onClick();
        rememberService();

        RotationMode actual = RotationController.getMode(this);
        if (actual == RotationMode.OFF && !RotationController.hasRequiredPermissions(this)) {
            cancelPendingBatch();
            openSetup();
            return;
        }

        final long generation;
        synchronized (TAP_LOCK) {
            RotationMode base = pendingTarget != null ? pendingTarget : actual;
            pendingTarget = base.next();
            pendingTapCount += 1;
            pendingGeneration += 1;
            generation = pendingGeneration;
        }

        // Give the user immediate visual confirmation that this tap was counted,
        // but do not rotate yet. The 400 ms timer restarts after every tap.
        updateTile();
        TAP_HANDLER.postDelayed(() -> commitPendingBatch(generation), MULTI_TAP_SETTLE_MS);
    }

    private void rememberService() {
        synchronized (TAP_LOCK) {
            appContext = getApplicationContext();
            latestService = new WeakReference<>(this);
        }
    }

    private static void commitPendingBatch(long generation) {
        final RotationMode target;
        final Context context;
        final RotationTileService service;

        synchronized (TAP_LOCK) {
            if (generation != pendingGeneration || pendingTarget == null) {
                return;
            }
            target = pendingTarget;
            pendingTarget = null;
            pendingTapCount = 0;
            context = appContext;
            service = latestService.get();
        }

        if (context == null) return;

        if (target != RotationMode.OFF && !RotationController.hasRequiredPermissions(context)) {
            if (service != null) {
                service.openSetup();
                service.updateTile();
            }
            return;
        }

        RotationController.setMode(context, target);

        if (service != null) {
            service.updateTile();
        } else {
            try {
                TileService.requestListeningState(
                        context,
                        new ComponentName(context, RotationTileService.class));
            } catch (Throwable ignored) {
            }
        }
    }

    private static void cancelPendingBatch() {
        synchronized (TAP_LOCK) {
            pendingTarget = null;
            pendingTapCount = 0;
            pendingGeneration += 1;
        }
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

        RotationMode actual = RotationController.getMode(this);
        RotationMode queued;
        int queuedTaps;
        synchronized (TAP_LOCK) {
            queued = pendingTarget;
            queuedTaps = pendingTapCount;
        }

        RotationMode shown = queued != null ? queued : actual;
        tile.setIcon(Icon.createWithResource(this, R.drawable.ic_rotation));
        tile.setLabel("Rotate 90°");
        tile.setState(shown == RotationMode.OFF ? Tile.STATE_INACTIVE : Tile.STATE_ACTIVE);

        String subtitle = queued != null
                ? "Queued ×" + queuedTaps + " → " + queued.label
                : actual.label;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            tile.setSubtitle(subtitle);
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            tile.setContentDescription("Rotate 90°. " + subtitle);
        }
        tile.updateTile();
    }
}
