package com.homayoun.rotationtile;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Build;
import android.provider.Settings;

public final class RotationController {
    private static final String PREFS = "rotation_tile";
    private static final String KEY_MODE = "mode";
    private static final String KEY_SNAPSHOT = "snapshot_saved";
    private static final String KEY_ACCEL = "saved_accelerometer_rotation";
    private static final String KEY_USER = "saved_user_rotation";

    private RotationController() {}

    private static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    public static RotationMode getMode(Context context) {
        return RotationMode.fromId(prefs(context).getInt(KEY_MODE, RotationMode.OFF.id));
    }

    public static boolean hasRequiredPermissions(Context context) {
        return Settings.canDrawOverlays(context) && Settings.System.canWrite(context);
    }

    public static boolean setMode(Context context, RotationMode target) {
        Context app = context.getApplicationContext();
        RotationMode previous = getMode(app);

        if (target != RotationMode.OFF && !hasRequiredPermissions(app)) {
            return false;
        }

        if (previous == RotationMode.OFF && target != RotationMode.OFF) {
            saveRotationSnapshot(app);
        }

        prefs(app).edit().putInt(KEY_MODE, target.id).apply();

        if (target == RotationMode.OFF) {
            restoreRotationSnapshot(app);
            app.stopService(new Intent(app, RotationService.class));
            return true;
        }

        enforceSystemSettings(app, target);
        startOrUpdateService(app, target);
        return true;
    }

    public static void enforceSystemSettings(Context context, RotationMode mode) {
        if (mode == RotationMode.OFF || !Settings.System.canWrite(context)) return;
        try {
            int accel = Settings.System.getInt(
                    context.getContentResolver(),
                    Settings.System.ACCELEROMETER_ROTATION,
                    1);
            int user = Settings.System.getInt(
                    context.getContentResolver(),
                    Settings.System.USER_ROTATION,
                    0);
            if (accel != 0) {
                Settings.System.putInt(
                        context.getContentResolver(),
                        Settings.System.ACCELEROMETER_ROTATION,
                        0);
            }
            if (user != mode.userRotation) {
                Settings.System.putInt(
                        context.getContentResolver(),
                        Settings.System.USER_ROTATION,
                        mode.userRotation);
            }
        } catch (Throwable ignored) {
        }
    }

    private static void saveRotationSnapshot(Context context) {
        SharedPreferences p = prefs(context);
        if (p.getBoolean(KEY_SNAPSHOT, false)) return;
        try {
            int accel = Settings.System.getInt(
                    context.getContentResolver(),
                    Settings.System.ACCELEROMETER_ROTATION,
                    1);
            int user = Settings.System.getInt(
                    context.getContentResolver(),
                    Settings.System.USER_ROTATION,
                    0);
            p.edit()
                    .putInt(KEY_ACCEL, accel)
                    .putInt(KEY_USER, user)
                    .putBoolean(KEY_SNAPSHOT, true)
                    .apply();
        } catch (Throwable ignored) {
        }
    }

    private static void restoreRotationSnapshot(Context context) {
        SharedPreferences p = prefs(context);
        if (!p.getBoolean(KEY_SNAPSHOT, false)) return;
        if (Settings.System.canWrite(context)) {
            try {
                Settings.System.putInt(
                        context.getContentResolver(),
                        Settings.System.ACCELEROMETER_ROTATION,
                        p.getInt(KEY_ACCEL, 1));
                Settings.System.putInt(
                        context.getContentResolver(),
                        Settings.System.USER_ROTATION,
                        p.getInt(KEY_USER, 0));
            } catch (Throwable ignored) {
            }
        }
        p.edit()
                .remove(KEY_ACCEL)
                .remove(KEY_USER)
                .putBoolean(KEY_SNAPSHOT, false)
                .apply();
    }

    private static void startOrUpdateService(Context context, RotationMode mode) {
        Intent intent = new Intent(context, RotationService.class)
                .setAction(RotationService.ACTION_SET_MODE)
                .putExtra(RotationService.EXTRA_MODE, mode.id);
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent);
            } else {
                context.startService(intent);
            }
        } catch (Throwable ignored) {
        }
    }

    public static Intent overlayPermissionIntent(Context context) {
        return new Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:" + context.getPackageName()));
    }

    public static Intent writeSettingsPermissionIntent(Context context) {
        return new Intent(
                Settings.ACTION_MANAGE_WRITE_SETTINGS,
                Uri.parse("package:" + context.getPackageName()));
    }
}
