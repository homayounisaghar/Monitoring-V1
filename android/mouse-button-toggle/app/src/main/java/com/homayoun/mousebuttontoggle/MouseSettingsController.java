package com.homayoun.mousebuttontoggle;

import android.content.ContentResolver;
import android.content.Context;
import android.os.Build;
import android.provider.Settings;

public final class MouseSettingsController {
    private static final String AOSP_KEY = "mouse_swap_primary_button";
    private static final String SAMSUNG_KEY = "primary_mouse_button_option";

    private MouseSettingsController() {
    }

    public static boolean hasWritePermission(Context context) {
        return Settings.System.canWrite(context);
    }

    public static boolean isSamsungDevice() {
        return "samsung".equalsIgnoreCase(Build.MANUFACTURER)
                || "samsung".equalsIgnoreCase(Build.BRAND);
    }

    public static int readPrimaryButton(Context context) {
        ContentResolver resolver = context.getContentResolver();
        Integer samsung = readBinary(resolver, SAMSUNG_KEY);
        Integer aosp = readBinary(resolver, AOSP_KEY);
        if (isSamsungDevice() && samsung != null) return samsung;
        if (aosp != null) return aosp;
        if (samsung != null) return samsung;
        return 0;
    }

    public static int togglePrimaryButtonDirect(Context context) {
        if (isSamsungDevice()) {
            throw new IllegalStateException(
                    "Samsung primary mouse setting is private; use the Samsung Settings helper");
        }
        if (!hasWritePermission(context)) {
            throw new IllegalStateException("Modify system settings permission is not granted");
        }
        ContentResolver resolver = context.getContentResolver();
        int current = readPrimaryButton(context);
        int next = current == 1 ? 0 : 1;
        writeAndVerify(resolver, AOSP_KEY, next, "Android primary mouse setting");
        return next;
    }

    public static String diagnostics(Context context) {
        ContentResolver resolver = context.getContentResolver();
        Integer samsung = readBinary(resolver, SAMSUNG_KEY);
        Integer aosp = readBinary(resolver, AOSP_KEY);
        boolean samsungDevice = isSamsungDevice();
        return "manufacturer=" + Build.MANUFACTURER
                + "\nbrand=" + Build.BRAND
                + "\nmodel=" + Build.MODEL
                + "\ndevice=" + Build.DEVICE
                + "\nsdk=" + Build.VERSION.SDK_INT
                + "\nrelease=" + Build.VERSION.RELEASE
                + "\nselected_backend="
                + (samsungDevice ? "samsung-settings-accessibility" : "android-system")
                + "\nmodify_system_settings=" + hasWritePermission(context)
                + "\n" + SAMSUNG_KEY + "=" + valueText(samsung)
                + "\n" + AOSP_KEY + "=" + valueText(aosp)
                + "\nreported_primary=" + readPrimaryButton(context)
                + "\n" + SamsungMouseAccessibilityService.diagnostics(context);
    }

    private static void writeAndVerify(ContentResolver resolver, String key, int value, String label) {
        final boolean wrote;
        try {
            wrote = Settings.System.putInt(resolver, key, value);
        } catch (SecurityException | IllegalArgumentException e) {
            throw new IllegalStateException(label + " is blocked by this Android build", e);
        } catch (Throwable e) {
            throw new IllegalStateException(label + " write failed: " + message(e), e);
        }
        if (!wrote) throw new IllegalStateException(label + " write returned false");
        Integer verified = readBinary(resolver, key);
        if (verified == null || verified != value) {
            throw new IllegalStateException(label + " did not persist (requested="
                    + value + ", read=" + valueText(verified) + ")");
        }
    }

    private static Integer readBinary(ContentResolver resolver, String key) {
        try {
            String raw = Settings.System.getString(resolver, key);
            if ("0".equals(raw)) return 0;
            if ("1".equals(raw)) return 1;
            return null;
        } catch (Throwable ignored) {
            return null;
        }
    }

    private static String valueText(Integer value) {
        return value == null ? "not-set" : Integer.toString(value);
    }

    private static String message(Throwable throwable) {
        String message = throwable.getMessage();
        return message == null ? throwable.toString() : message;
    }
}
