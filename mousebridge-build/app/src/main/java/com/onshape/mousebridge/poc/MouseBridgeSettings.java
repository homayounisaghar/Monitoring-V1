package com.onshape.mousebridge.poc;

import android.content.Context;
import android.content.SharedPreferences;

public final class MouseBridgeSettings {
    private static final String PREFS = "mousebridge_settings";
    private static final String KEY_ZOOM_SENSITIVITY = "zoom_sensitivity";
    private static final String KEY_UI_SCROLL_SENSITIVITY = "ui_scroll_sensitivity";

    public static final float MIN_SENSITIVITY = 0.25f;
    public static final float MAX_SENSITIVITY = 4.0f;
    public static final float DEFAULT_ZOOM_SENSITIVITY = 2.0f;
    public static final float DEFAULT_UI_SCROLL_SENSITIVITY = 0.50f;

    private MouseBridgeSettings() {}

    public static float getZoomSensitivity(Context context) {
        return clamp(preferences(context).getFloat(
                KEY_ZOOM_SENSITIVITY, DEFAULT_ZOOM_SENSITIVITY));
    }

    public static void setZoomSensitivity(Context context, float value) {
        preferences(context).edit().putFloat(KEY_ZOOM_SENSITIVITY, clamp(value)).apply();
    }

    public static float getUiScrollSensitivity(Context context) {
        return clamp(preferences(context).getFloat(
                KEY_UI_SCROLL_SENSITIVITY, DEFAULT_UI_SCROLL_SENSITIVITY));
    }

    public static void setUiScrollSensitivity(Context context, float value) {
        preferences(context).edit().putFloat(KEY_UI_SCROLL_SENSITIVITY, clamp(value)).apply();
    }

    public static void reset(Context context) {
        preferences(context).edit()
                .remove(KEY_ZOOM_SENSITIVITY)
                .remove(KEY_UI_SCROLL_SENSITIVITY)
                .apply();
    }

    private static SharedPreferences preferences(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    private static float clamp(float value) {
        return Math.max(MIN_SENSITIVITY, Math.min(MAX_SENSITIVITY, value));
    }
}
