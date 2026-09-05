package com.homayoun.rotationtile;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.hardware.display.DisplayManager;
import android.net.Uri;
import android.os.Build;
import android.provider.Settings;
import android.view.Display;

public final class RotationController {
    private static final String PREFS = "rotation_tile";
    private static final String KEY_ENABLED = "override_enabled";
    private static final String KEY_LOCKED_MODE = "locked_mode";

    // v1.0.0/v1.0.1 compatibility keys.
    private static final String LEGACY_KEY_MODE = "mode";
    private static final String LEGACY_KEY_SNAPSHOT = "snapshot_saved";
    private static final String LEGACY_KEY_ACCEL = "saved_accelerometer_rotation";
    private static final String LEGACY_KEY_USER = "saved_user_rotation";

    private RotationController() {}

    private static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    private static void ensureMigrated(Context context) {
        SharedPreferences p = prefs(context);
        if (p.contains(KEY_ENABLED) && p.contains(KEY_LOCKED_MODE)) return;

        RotationMode legacy = RotationMode.fromId(p.getInt(LEGACY_KEY_MODE, RotationMode.OFF.id));
        boolean enabled = legacy.isLockedMode();
        RotationMode locked = enabled ? legacy : getCurrentDisplayMode(context);

        p.edit()
                .putBoolean(KEY_ENABLED, enabled)
                .putInt(KEY_LOCKED_MODE, locked.id)
                .remove(LEGACY_KEY_SNAPSHOT)
                .remove(LEGACY_KEY_ACCEL)
                .remove(LEGACY_KEY_USER)
                .apply();

        // In v1.0.2, Off explicitly means follow the device sensors. Migrate
        // legacy Off into that behavior as soon as the new state model is read.
        if (!enabled && Settings.System.canWrite(context)) {
            try {
                Settings.System.putInt(
                        context.getContentResolver(),
                        Settings.System.ACCELEROMETER_ROTATION,
                        1);
            } catch (Throwable ignored) {
            }
        }
    }

    public static boolean isEnabled(Context context) {
        ensureMigrated(context);
        return prefs(context).getBoolean(KEY_ENABLED, false);
    }

    public static RotationMode getLockedMode(Context context) {
        ensureMigrated(context);
        RotationMode mode = RotationMode.fromId(
                prefs(context).getInt(KEY_LOCKED_MODE, RotationMode.PORTRAIT.id));
        return mode.isLockedMode() ? mode : getCurrentDisplayMode(context);
    }

    public static RotationMode getCurrentDisplayMode(Context context) {
        try {
            DisplayManager manager = (DisplayManager) context.getSystemService(Context.DISPLAY_SERVICE);
            Display display = manager != null ? manager.getDisplay(Display.DEFAULT_DISPLAY) : null;
            if (display != null) {
                return RotationMode.fromSurfaceRotation(display.getRotation());
            }
        } catch (Throwable ignored) {
        }

        try {
            int userRotation = Settings.System.getInt(
                    context.getContentResolver(),
                    Settings.System.USER_ROTATION,
                    0);
            return RotationMode.fromSurfaceRotation(userRotation);
        } catch (Throwable ignored) {
            return RotationMode.PORTRAIT;
        }
    }

    public static boolean hasRequiredPermissions(Context context) {
        return Settings.canDrawOverlays(context) && Settings.System.canWrite(context);
    }

    public static boolean toggleOverride(Context context) {
        return isEnabled(context) ? disableOverride(context) : enableFromCurrentOrientation(context);
    }

    public static boolean enableFromCurrentOrientation(Context context) {
        Context app = context.getApplicationContext();
        if (!hasRequiredPermissions(app)) return false;

        RotationMode current = getCurrentDisplayMode(context);
        prefs(app).edit()
                .putInt(KEY_LOCKED_MODE, current.id)
                .putBoolean(KEY_ENABLED, true)
                .remove(LEGACY_KEY_MODE)
                .apply();

        // Preserve the exact visible angle while enabling: write the current
        // rotation first, then disable sensor rotation. This avoids a transient
        // jump to an older USER_ROTATION value during the long-press toggle.
        try {
            Settings.System.putInt(
                    app.getContentResolver(),
                    Settings.System.USER_ROTATION,
                    current.userRotation);
            Settings.System.putInt(
                    app.getContentResolver(),
                    Settings.System.ACCELEROMETER_ROTATION,
                    0);
        } catch (Throwable ignored) {
        }

        startOrUpdateService(app, current);
        return true;
    }

    public static boolean disableOverride(Context context) {
        Context app = context.getApplicationContext();
        RotationMode current = getCurrentDisplayMode(context);

        prefs(app).edit()
                .putInt(KEY_LOCKED_MODE, current.id)
                .putBoolean(KEY_ENABLED, false)
                .remove(LEGACY_KEY_MODE)
                .apply();

        // Release the lock without choosing a different angle. Auto-rotation may
        // immediately move the display if the device posture calls for it.
        if (Settings.System.canWrite(app)) {
            try {
                Settings.System.putInt(
                        app.getContentResolver(),
                        Settings.System.ACCELEROMETER_ROTATION,
                        1);
            } catch (Throwable ignored) {
            }
        }

        app.stopService(new Intent(app, RotationService.class));
        return true;
    }

    public static boolean setLockedMode(Context context, RotationMode target) {
        Context app = context.getApplicationContext();
        if (!target.isLockedMode() || !isEnabled(app) || !hasRequiredPermissions(app)) {
            return false;
        }

        prefs(app).edit().putInt(KEY_LOCKED_MODE, target.id).apply();
        enforceSystemSettings(app, target);
        startOrUpdateService(app, target);
        return true;
    }

    public static void enforceSystemSettings(Context context, RotationMode mode) {
        if (!mode.isLockedMode() || !Settings.System.canWrite(context)) return;
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
