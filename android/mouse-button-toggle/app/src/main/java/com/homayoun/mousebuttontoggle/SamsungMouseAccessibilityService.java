package com.homayoun.mousebuttontoggle;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.pm.ServiceInfo;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.hardware.HardwareBuffer;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.service.quicksettings.TileService;
import android.text.TextUtils;
import android.view.Display;
import android.view.Gravity;
import android.view.WindowManager;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityManager;
import android.view.accessibility.AccessibilityNodeInfo;
import android.view.accessibility.AccessibilityWindowInfo;
import android.widget.ImageView;
import android.widget.Toast;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public final class SamsungMouseAccessibilityService extends AccessibilityService {
    private static final String SETTINGS_PACKAGE = "com.android.settings";
    private static final String SETTINGS_MOUSE_ACTIVITY =
            "com.android.settings.Settings$MouseAndTrackpadSettingsActivity";

    private static final String PREFS = "samsung_mouse_settings_automation";
    private static final String KEY_TARGET = "pending_target";
    private static final String KEY_STAGE = "pending_stage";
    private static final String KEY_STARTED_AT = "pending_started_at";
    private static final String KEY_SCROLLS = "pending_scrolls";
    private static final String KEY_LAST_RESULT = "last_result";
    private static final String KEY_LAST_ERROR = "last_error";
    private static final String KEY_LAST_COVER = "last_cover";
    private static final String KEY_LAST_RETURN = "last_return";

    private static final int STAGE_FIND_PRIMARY = 0;
    private static final int STAGE_PICK_SIDE = 1;
    private static final long TIMEOUT_MS = 10000L;

    private static volatile SamsungMouseAccessibilityService sInstance;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private WindowManager windowManager;
    private ImageView coverView;
    private Bitmap coverBitmap;
    private boolean settingsLaunched;

    public static ComponentName component(Context context) {
        return new ComponentName(context, SamsungMouseAccessibilityService.class);
    }

    public static boolean isEnabled(Context context) {
        AccessibilityManager manager =
                (AccessibilityManager) context.getSystemService(Context.ACCESSIBILITY_SERVICE);
        if (manager == null || !manager.isEnabled()) return false;
        ComponentName wanted = component(context);
        try {
            List<AccessibilityServiceInfo> enabled =
                    manager.getEnabledAccessibilityServiceList(AccessibilityServiceInfo.FEEDBACK_ALL_MASK);
            for (AccessibilityServiceInfo info : enabled) {
                if (info == null || info.getResolveInfo() == null
                        || info.getResolveInfo().serviceInfo == null) continue;
                ServiceInfo service = info.getResolveInfo().serviceInfo;
                ComponentName found = new ComponentName(service.packageName, service.name);
                if (wanted.equals(found)) return true;
            }
        } catch (Throwable ignored) {
        }
        return false;
    }

    public static boolean isConnected() {
        return sInstance != null;
    }

    public static boolean requestSeamlessToggle(Context context) {
        SamsungMouseAccessibilityService service = sInstance;
        if (service == null || !isEnabled(context)) return false;
        service.handler.post(service::beginSeamlessToggle);
        return true;
    }

    public static Intent accessibilitySettingsIntent(Context context) {
        return new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
    }

    public static void cancelPending(Context context, String error) {
        SharedPreferences.Editor editor = prefs(context).edit()
                .remove(KEY_TARGET)
                .remove(KEY_STAGE)
                .remove(KEY_STARTED_AT)
                .remove(KEY_SCROLLS);
        if (!TextUtils.isEmpty(error)) editor.putString(KEY_LAST_ERROR, error);
        editor.apply();
    }

    public static boolean isPending(Context context) {
        SharedPreferences p = prefs(context);
        if (!p.contains(KEY_TARGET)) return false;
        long started = p.getLong(KEY_STARTED_AT, 0L);
        if (started > 0 && System.currentTimeMillis() - started > TIMEOUT_MS + 2500L) {
            cancelPending(context, "Previous seamless Samsung Settings automation timed out");
            return false;
        }
        return true;
    }

    public static String diagnostics(Context context) {
        SharedPreferences p = prefs(context);
        return "samsung_settings_helper_enabled=" + isEnabled(context)
                + "\nsamsung_settings_helper_connected=" + isConnected()
                + "\nsamsung_automation_pending=" + isPending(context)
                + "\nsamsung_last_result=" + p.getString(KEY_LAST_RESULT, "none")
                + "\nsamsung_last_error=" + p.getString(KEY_LAST_ERROR, "none")
                + "\nsamsung_last_cover=" + p.getString(KEY_LAST_COVER, "none")
                + "\nsamsung_last_return=" + p.getString(KEY_LAST_RETURN, "none");
    }

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        sInstance = this;
        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
        requestTileRefresh();
    }

    @Override
    public void onDestroy() {
        if (sInstance == this) sInstance = null;
        handler.removeCallbacksAndMessages(null);
        removeCover();
        super.onDestroy();
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (!isPending(this)) return;
        CharSequence pkg = event == null ? null : event.getPackageName();
        if (pkg == null || !SETTINGS_PACKAGE.contentEquals(pkg)) return;
        if (settingsLaunched) processPending();
    }

    @Override
    public void onInterrupt() {
    }

    private void beginSeamlessToggle() {
        if (isPending(this)) return;

        int current = MouseSettingsController.readPrimaryButton(this);
        int target = current == 1 ? 0 : 1;
        settingsLaunched = false;
        prefs(this).edit()
                .putInt(KEY_TARGET, target)
                .putInt(KEY_STAGE, STAGE_FIND_PRIMARY)
                .putInt(KEY_SCROLLS, 0)
                .putLong(KEY_STARTED_AT, System.currentTimeMillis())
                .remove(KEY_LAST_ERROR)
                .putString(KEY_LAST_RETURN, "pending")
                .apply();
        requestTileRefresh();

        if (Build.VERSION.SDK_INT >= 31) {
            try {
                performGlobalAction(GLOBAL_ACTION_DISMISS_NOTIFICATION_SHADE);
            } catch (Throwable ignored) {
            }
        }

        handler.postDelayed(this::captureCoverThenLaunch, 260L);
        handler.postDelayed(watchdog, TIMEOUT_MS + 800L);
    }

    private void captureCoverThenLaunch() {
        if (!isPending(this)) return;

        if (Build.VERSION.SDK_INT >= 30) {
            try {
                takeScreenshot(
                        Display.DEFAULT_DISPLAY,
                        getMainExecutor(),
                        new TakeScreenshotCallback() {
                            @Override
                            public void onSuccess(ScreenshotResult screenshot) {
                                Bitmap software = null;
                                HardwareBuffer buffer = null;
                                Bitmap hardware = null;
                                try {
                                    buffer = screenshot.getHardwareBuffer();
                                    hardware = Bitmap.wrapHardwareBuffer(
                                            buffer, screenshot.getColorSpace());
                                    if (hardware != null) {
                                        software = hardware.copy(Bitmap.Config.ARGB_8888, false);
                                    }
                                } catch (Throwable ignored) {
                                } finally {
                                    if (hardware != null) {
                                        try { hardware.recycle(); } catch (Throwable ignored) {}
                                    }
                                    if (buffer != null) {
                                        try { buffer.close(); } catch (Throwable ignored) {}
                                    }
                                }

                                if (software != null) {
                                    prefs(SamsungMouseAccessibilityService.this).edit()
                                            .putString(KEY_LAST_COVER, "screenshot")
                                            .apply();
                                    showCover(software);
                                } else {
                                    prefs(SamsungMouseAccessibilityService.this).edit()
                                            .putString(KEY_LAST_COVER, "fallback-copy-failed")
                                            .apply();
                                    showFallbackCover();
                                }
                                launchSettingsUnderCover();
                            }

                            @Override
                            public void onFailure(int errorCode) {
                                prefs(SamsungMouseAccessibilityService.this).edit()
                                        .putString(KEY_LAST_COVER, "fallback-screenshot-error-" + errorCode)
                                        .apply();
                                showFallbackCover();
                                launchSettingsUnderCover();
                            }
                        });
                return;
            } catch (Throwable e) {
                prefs(this).edit().putString(KEY_LAST_COVER,
                        "fallback-exception-" + shortMessage(e)).apply();
            }
        }

        showFallbackCover();
        launchSettingsUnderCover();
    }

    private void showCover(Bitmap bitmap) {
        removeCover();
        coverBitmap = bitmap;
        ImageView view = new ImageView(this);
        view.setScaleType(ImageView.ScaleType.FIT_XY);
        view.setImageBitmap(bitmap);
        installCover(view, PixelFormat.OPAQUE);
    }

    private void showFallbackCover() {
        removeCover();
        ImageView view = new ImageView(this);
        view.setBackgroundColor(Color.BLACK);
        installCover(view, PixelFormat.OPAQUE);
    }

    private void installCover(ImageView view, int format) {
        if (windowManager == null) {
            windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
        }
        if (windowManager == null) return;

        WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                        | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
                        | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
                        | WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
                format);
        lp.gravity = Gravity.TOP | Gravity.START;
        lp.setTitle("Mouse Button Toggle seamless cover");
        if (Build.VERSION.SDK_INT >= 28) {
            lp.layoutInDisplayCutoutMode =
                    WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
        }
        try {
            windowManager.addView(view, lp);
            coverView = view;
        } catch (Throwable e) {
            prefs(this).edit().putString(KEY_LAST_COVER,
                    "overlay-failed-" + shortMessage(e)).apply();
            coverView = null;
        }
    }

    private void launchSettingsUnderCover() {
        if (!isPending(this)) {
            removeCover();
            return;
        }
        try {
            Intent intent = new Intent()
                    .setComponent(new ComponentName(SETTINGS_PACKAGE, SETTINGS_MOUSE_ACTIVITY))
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK
                            | Intent.FLAG_ACTIVITY_MULTIPLE_TASK
                            | Intent.FLAG_ACTIVITY_NO_HISTORY
                            | Intent.FLAG_ACTIVITY_NO_ANIMATION
                            | Intent.FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS);
            settingsLaunched = true;
            startActivity(intent);
            handler.postDelayed(this::processPending, 220L);
        } catch (Throwable e) {
            fail("Could not launch Samsung Mouse settings under cover: " + shortMessage(e));
        }
    }

    private void processPending() {
        SharedPreferences p = prefs(this);
        if (!p.contains(KEY_TARGET)) return;

        long started = p.getLong(KEY_STARTED_AT, 0L);
        if (started <= 0 || System.currentTimeMillis() - started > TIMEOUT_MS) {
            fail("Samsung Settings automation timed out");
            return;
        }

        int target = p.getInt(KEY_TARGET, -1);
        if (target != 0 && target != 1) {
            fail("Invalid pending mouse target");
            return;
        }

        int current = MouseSettingsController.readPrimaryButton(this);
        if (current == target) {
            succeed(target);
            return;
        }

        AccessibilityNodeInfo root = findSettingsRoot();
        if (root == null) {
            retrySoon();
            return;
        }

        int stage = p.getInt(KEY_STAGE, STAGE_FIND_PRIMARY);
        if (stage == STAGE_FIND_PRIMARY) {
            String title = samsungString("primary_mouse_button_title", "Primary mouse button");
            AccessibilityNodeInfo primary = findExactText(root, title);
            if (primary == null && !"Primary mouse button".equals(title)) {
                primary = findExactText(root, "Primary mouse button");
            }
            if (primary != null && clickNearestClickable(primary)) {
                p.edit().putInt(KEY_STAGE, STAGE_PICK_SIDE).apply();
                retrySoon();
                return;
            }

            int scrolls = p.getInt(KEY_SCROLLS, 0);
            if (scrolls < 6 && scrollFirstScrollable(root)) {
                p.edit().putInt(KEY_SCROLLS, scrolls + 1).apply();
                retrySoon();
                return;
            }
            retrySoon();
            return;
        }

        String targetText = target == 1
                ? samsungString("primary_mouse_button_right", "Right")
                : samsungString("primary_mouse_button_left", "Left");
        AccessibilityNodeInfo choice = findExactText(root, targetText);
        if (choice == null && target == 1 && !"Right".equals(targetText)) {
            choice = findExactText(root, "Right");
        } else if (choice == null && target == 0 && !"Left".equals(targetText)) {
            choice = findExactText(root, "Left");
        }

        if (choice != null && clickNearestClickable(choice)) {
            handler.postDelayed(() -> {
                if (!isPending(this)) return;
                if (MouseSettingsController.readPrimaryButton(this) == target) {
                    succeed(target);
                } else {
                    processPending();
                }
            }, 260L);
            return;
        }

        retrySoon();
    }

    private AccessibilityNodeInfo findSettingsRoot() {
        try {
            List<AccessibilityWindowInfo> windows = getWindows();
            if (windows != null) {
                for (AccessibilityWindowInfo window : windows) {
                    if (window == null) continue;
                    AccessibilityNodeInfo root = window.getRoot();
                    if (root == null) continue;
                    CharSequence pkg = root.getPackageName();
                    if (pkg != null && SETTINGS_PACKAGE.contentEquals(pkg)) {
                        return root;
                    }
                }
            }
        } catch (Throwable ignored) {
        }

        try {
            AccessibilityNodeInfo active = getRootInActiveWindow();
            if (active != null) {
                CharSequence pkg = active.getPackageName();
                if (pkg != null && SETTINGS_PACKAGE.contentEquals(pkg)) return active;
            }
        } catch (Throwable ignored) {
        }
        return null;
    }

    private void succeed(int target) {
        prefs(this).edit()
                .remove(KEY_TARGET)
                .remove(KEY_STAGE)
                .remove(KEY_STARTED_AT)
                .remove(KEY_SCROLLS)
                .putString(KEY_LAST_RESULT, target == 1 ? "RIGHT" : "LEFT")
                .remove(KEY_LAST_ERROR)
                .apply();
        requestTileRefresh();
        finishHiddenSettings("success");
    }

    private void fail(String error) {
        cancelPending(this, error);
        requestTileRefresh();
        Toast.makeText(this, "Mouse toggle failed: " + error, Toast.LENGTH_LONG).show();
        finishHiddenSettings("failed");
    }

    private void finishHiddenSettings(String result) {
        handler.removeCallbacks(retryRunnable);
        handler.removeCallbacks(watchdog);

        if (settingsLaunched) {
            try {
                performGlobalAction(GLOBAL_ACTION_BACK);
            } catch (Throwable ignored) {
            }
        }
        settingsLaunched = false;

        handler.postDelayed(() -> {
            prefs(this).edit().putString(KEY_LAST_RETURN, result + "-back-to-caller").apply();
            removeCover();
            requestTileRefresh();
        }, 360L);
    }

    private final Runnable watchdog = () -> {
        if (!isPending(this)) return;
        cancelPending(this, "Seamless toggle watchdog timeout");
        requestTileRefresh();
        if (settingsLaunched) {
            try { performGlobalAction(GLOBAL_ACTION_BACK); } catch (Throwable ignored) {}
        }
        settingsLaunched = false;
        handler.postDelayed(this::removeCover, 280L);
        Toast.makeText(this, "Mouse toggle timed out", Toast.LENGTH_LONG).show();
    };

    private void retrySoon() {
        handler.removeCallbacks(retryRunnable);
        handler.postDelayed(retryRunnable, 150L);
    }

    private final Runnable retryRunnable = this::processPending;

    private void removeCover() {
        ImageView view = coverView;
        coverView = null;
        if (view != null && windowManager != null) {
            try {
                windowManager.removeViewImmediate(view);
            } catch (Throwable ignored) {
            }
        }
        Bitmap bitmap = coverBitmap;
        coverBitmap = null;
        if (bitmap != null && !bitmap.isRecycled()) {
            try { bitmap.recycle(); } catch (Throwable ignored) {}
        }
    }

    private void requestTileRefresh() {
        try {
            TileService.requestListeningState(this,
                    new ComponentName(this, MouseToggleTileService.class));
        } catch (Throwable ignored) {
        }
    }

    private String samsungString(String name, String fallback) {
        try {
            Context settings = createPackageContext(SETTINGS_PACKAGE, 0);
            int id = settings.getResources().getIdentifier(name, "string", SETTINGS_PACKAGE);
            if (id != 0) {
                String value = settings.getString(id);
                if (!TextUtils.isEmpty(value)) return value;
            }
        } catch (PackageManager.NameNotFoundException ignored) {
        } catch (Throwable ignored) {
        }
        return fallback;
    }

    private static AccessibilityNodeInfo findExactText(AccessibilityNodeInfo root, String text) {
        if (root == null || TextUtils.isEmpty(text)) return null;
        List<AccessibilityNodeInfo> candidates = new ArrayList<>();
        try {
            List<AccessibilityNodeInfo> matches = root.findAccessibilityNodeInfosByText(text);
            if (matches != null) candidates.addAll(matches);
        } catch (Throwable ignored) {
        }

        String wanted = normalize(text);
        for (AccessibilityNodeInfo node : candidates) {
            if (node == null) continue;
            CharSequence nodeText = node.getText();
            CharSequence description = node.getContentDescription();
            if (wanted.equals(normalize(nodeText)) || wanted.equals(normalize(description))) {
                return node;
            }
        }
        return null;
    }

    private static boolean clickNearestClickable(AccessibilityNodeInfo start) {
        AccessibilityNodeInfo node = start;
        for (int i = 0; node != null && i < 8; i++) {
            if (node.isEnabled() && node.isClickable()) {
                try {
                    if (node.performAction(AccessibilityNodeInfo.ACTION_CLICK)) return true;
                } catch (Throwable ignored) {
                }
            }
            node = node.getParent();
        }
        return false;
    }

    private static boolean scrollFirstScrollable(AccessibilityNodeInfo root) {
        ArrayDeque<AccessibilityNodeInfo> queue = new ArrayDeque<>();
        queue.add(root);
        int visited = 0;
        while (!queue.isEmpty() && visited++ < 300) {
            AccessibilityNodeInfo node = queue.removeFirst();
            if (node == null) continue;
            if (node.isScrollable()) {
                try {
                    if (node.performAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD)) return true;
                } catch (Throwable ignored) {
                }
            }
            for (int i = 0; i < node.getChildCount(); i++) {
                AccessibilityNodeInfo child = node.getChild(i);
                if (child != null) queue.addLast(child);
            }
        }
        return false;
    }

    private static String normalize(CharSequence value) {
        if (value == null) return "";
        return value.toString().trim().replaceAll("\\s+", " ").toLowerCase(Locale.ROOT);
    }

    private static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    private static String shortMessage(Throwable throwable) {
        if (throwable == null) return "unknown";
        String message = throwable.getMessage();
        if (TextUtils.isEmpty(message)) message = throwable.getClass().getSimpleName();
        return message.replace('\n', ' ').replace('\r', ' ');
    }
}
