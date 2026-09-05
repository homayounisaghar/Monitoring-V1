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

        if (!RotationController.isEnabled(this)) {
            cancelPendingBatch(this);
            updateTile();
            return;
        }

        if (!RotationController.hasRequiredPermissions(this)) {
            cancelPendingBatch(this);
            openSetup();
            return;
        }

        final long generation;
        synchronized (TAP_LOCK) {
            RotationMode base = pendingTarget != null
                    ? pendingTarget
                    : RotationController.getLockedMode(this);
            pendingTarget = base.nextLocked();
            pendingTapCount += 1;
            pendingGeneration += 1;
            generation = pendingGeneration;
        }

        // Count every tap immediately, but wait until 400 ms after the last tap
        // before applying the final locked angle.
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
            if (generation != pendingGeneration || pendingTarget == null) return;
            target = pendingTarget;
            pendingTarget = null;
            pendingTapCount = 0;
            context = appContext;
            service = latestService.get();
        }

        if (context == null || !RotationController.isEnabled(context)) {
            requestTileRefresh(context);
            return;
        }

        if (!RotationController.hasRequiredPermissions(context)) {
            if (service != null) service.openSetup();
            requestTileRefresh(context);
            return;
        }

        RotationController.setLockedMode(context, target);
        requestTileRefresh(context);
    }

    public static void cancelPendingBatch(Context context) {
        synchronized (TAP_LOCK) {
            pendingTarget = null;
            pendingTapCount = 0;
            pendingGeneration += 1;
            if (context != null) appContext = context.getApplicationContext();
        }
        requestTileRefresh(context);
    }

    public static void requestTileRefresh(Context context) {
        if (context == null) return;
        RotationTileService service = latestService.get();
        if (service != null) {
            service.updateTile();
            return;
        }
        try {
            TileService.requestListeningState(
                    context.getApplicationContext(),
                    new ComponentName(context, RotationTileService.class));
        } catch (Throwable ignored) {
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

        boolean enabled = RotationController.isEnabled(this);
        RotationMode actual = RotationController.getLockedMode(this);
        RotationMode queued;
        int queuedTaps;
        synchronized (TAP_LOCK) {
            queued = pendingTarget;
            queuedTaps = pendingTapCount;
        }

        tile.setIcon(Icon.createWithResource(this, R.drawable.ic_rotation));
        tile.setLabel("Rotation");
        tile.setState(enabled ? Tile.STATE_ACTIVE : Tile.STATE_INACTIVE);

        String subtitle;
        if (!enabled) {
            subtitle = "Off · Auto";
        } else if (queued != null) {
            subtitle = "Queued ×" + queuedTaps + " → " + queued.label;
        } else {
            subtitle = actual.label;
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            tile.setSubtitle(subtitle);
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            tile.setContentDescription("Rotation. " + subtitle);
        }
        tile.updateTile();
    }
}
