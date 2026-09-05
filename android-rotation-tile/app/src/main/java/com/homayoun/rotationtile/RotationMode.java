package com.homayoun.rotationtile;

import android.content.pm.ActivityInfo;
import android.view.Surface;

public enum RotationMode {
    OFF(0, ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED, -1, "Off"),
    PORTRAIT(1, ActivityInfo.SCREEN_ORIENTATION_PORTRAIT, Surface.ROTATION_0, "Portrait · 0°"),
    LANDSCAPE(2, ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE, Surface.ROTATION_90, "Landscape · 90°"),
    REVERSE_PORTRAIT(3, ActivityInfo.SCREEN_ORIENTATION_REVERSE_PORTRAIT, Surface.ROTATION_180, "Portrait · 180°"),
    REVERSE_LANDSCAPE(4, ActivityInfo.SCREEN_ORIENTATION_REVERSE_LANDSCAPE, Surface.ROTATION_270, "Landscape · 270°");

    public final int id;
    public final int requestedOrientation;
    public final int userRotation;
    public final String label;

    RotationMode(int id, int requestedOrientation, int userRotation, String label) {
        this.id = id;
        this.requestedOrientation = requestedOrientation;
        this.userRotation = userRotation;
        this.label = label;
    }

    public boolean isLockedMode() {
        return this != OFF;
    }

    public RotationMode nextLocked() {
        switch (this) {
            case PORTRAIT: return LANDSCAPE;
            case LANDSCAPE: return REVERSE_PORTRAIT;
            case REVERSE_PORTRAIT: return REVERSE_LANDSCAPE;
            case REVERSE_LANDSCAPE: return PORTRAIT;
            default: return PORTRAIT;
        }
    }

    public static RotationMode fromId(int id) {
        for (RotationMode mode : values()) {
            if (mode.id == id) return mode;
        }
        return OFF;
    }

    public static RotationMode fromSurfaceRotation(int rotation) {
        switch (rotation) {
            case Surface.ROTATION_90: return LANDSCAPE;
            case Surface.ROTATION_180: return REVERSE_PORTRAIT;
            case Surface.ROTATION_270: return REVERSE_LANDSCAPE;
            case Surface.ROTATION_0:
            default: return PORTRAIT;
        }
    }
}
