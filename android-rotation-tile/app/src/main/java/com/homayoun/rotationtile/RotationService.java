package com.homayoun.rotationtile;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.ContentResolver;
import android.content.Intent;
import android.content.res.Configuration;
import android.database.ContentObserver;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;

public class RotationService extends Service {
    public static final String ACTION_SET_MODE = "com.homayoun.rotationtile.SET_MODE";
    public static final String EXTRA_MODE = "mode";

    private static final int NOTIFICATION_ID = 77;
    private static final String CHANNEL_ID = "rotation_lock";

    private WindowManager windowManager;
    private View overlayView;
    private RotationMode activeMode = RotationMode.OFF;
    private Handler handler;
    private ContentObserver settingsObserver;

    @Override
    public void onCreate() {
        super.onCreate();
        handler = new Handler(Looper.getMainLooper());
        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
        createNotificationChannel();
        registerSettingsObserver();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        int modeId = intent != null
                ? intent.getIntExtra(EXTRA_MODE, RotationController.getLockedMode(this).id)
                : RotationController.getLockedMode(this).id;
        activeMode = RotationMode.fromId(modeId);

        if (!RotationController.isEnabled(this)
                || !activeMode.isLockedMode()
                || !RotationController.hasRequiredPermissions(this)) {
            removeOverlay();
            stopForeground(true);
            stopSelf();
            return START_NOT_STICKY;
        }

        startForeground(NOTIFICATION_ID, buildNotification(activeMode));
        RotationController.enforceSystemSettings(this, activeMode);
        applyOverlay(activeMode);
        return START_STICKY;
    }

    private void applyOverlay(RotationMode mode) {
        if (!mode.isLockedMode() || !Settings.canDrawOverlays(this) || windowManager == null) return;
        removeOverlay();

        overlayView = new View(this);
        overlayView.setBackgroundColor(Color.TRANSPARENT);

        int type = Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                : WindowManager.LayoutParams.TYPE_SYSTEM_ALERT;

        WindowManager.LayoutParams params = new WindowManager.LayoutParams(
                1,
                1,
                type,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                        | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
                        | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
                        | WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
                PixelFormat.TRANSLUCENT);
        params.gravity = Gravity.TOP | Gravity.START;
        params.alpha = 0.01f;
        params.screenOrientation = mode.requestedOrientation;
        params.setTitle("RotationTileOrientationLock");

        try {
            windowManager.addView(overlayView, params);
        } catch (Throwable ignored) {
            overlayView = null;
        }
    }

    private void removeOverlay() {
        if (overlayView != null && windowManager != null) {
            try {
                windowManager.removeViewImmediate(overlayView);
            } catch (Throwable ignored) {
            }
        }
        overlayView = null;
    }

    private void registerSettingsObserver() {
        settingsObserver = new ContentObserver(handler) {
            @Override
            public void onChange(boolean selfChange) {
                scheduleReassert(120);
            }
        };
        ContentResolver resolver = getContentResolver();
        resolver.registerContentObserver(
                Settings.System.getUriFor(Settings.System.ACCELEROMETER_ROTATION),
                false,
                settingsObserver);
        resolver.registerContentObserver(
                Settings.System.getUriFor(Settings.System.USER_ROTATION),
                false,
                settingsObserver);
    }

    private void scheduleReassert(long delayMs) {
        if (!RotationController.isEnabled(this) || handler == null) return;
        handler.removeCallbacks(reassertRunnable);
        handler.postDelayed(reassertRunnable, delayMs);
    }

    private final Runnable reassertRunnable = new Runnable() {
        @Override
        public void run() {
            if (!RotationController.isEnabled(RotationService.this)) return;
            activeMode = RotationController.getLockedMode(RotationService.this);
            RotationController.enforceSystemSettings(RotationService.this, activeMode);
            applyOverlay(activeMode);
        }
    };

    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        scheduleReassert(80);
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID,
                    "Rotation lock service",
                    NotificationManager.IMPORTANCE_MIN);
            channel.setDescription("Keeps the selected display orientation active.");
            channel.setShowBadge(false);
            NotificationManager manager = getSystemService(NotificationManager.class);
            if (manager != null) manager.createNotificationChannel(channel);
        }
    }

    private Notification buildNotification(RotationMode mode) {
        Intent open = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(
                this,
                0,
                open,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        Notification.Builder builder = Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                ? new Notification.Builder(this, CHANNEL_ID)
                : new Notification.Builder(this);

        return builder
                .setSmallIcon(R.drawable.ic_rotation)
                .setContentTitle("Rotation override on")
                .setContentText(mode.label)
                .setOngoing(true)
                .setCategory(Notification.CATEGORY_SERVICE)
                .setContentIntent(pendingIntent)
                .build();
    }

    @Override
    public void onDestroy() {
        if (settingsObserver != null) {
            try {
                getContentResolver().unregisterContentObserver(settingsObserver);
            } catch (Throwable ignored) {
            }
        }
        if (handler != null) handler.removeCallbacksAndMessages(null);
        removeOverlay();
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
