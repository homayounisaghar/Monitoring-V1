package com.homayoun.mousebuttontoggle;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.pm.ServiceInfo;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.service.quicksettings.TileService;
import android.text.TextUtils;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityManager;
import android.view.accessibility.AccessibilityNodeInfo;
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

    private static final int STAGE_FIND_PRIMARY = 0;
    private static final int STAGE_PICK_SIDE = 1;
    private static final long TIMEOUT_MS = 9000L;

    private final Handler handler = new Handler(Looper.getMainLooper());

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

    public static Intent accessibilitySettingsIntent(Context context) {
        ComponentName component = component(context);
        Intent details = new Intent("android.settings.ACCESSIBILITY_DETAILS_SETTINGS")
                .putExtra(Intent.EXTRA_COMPONENT_NAME, component);
        try {
            if (details.resolveActivity(context.getPackageManager()) != null) {
                return details;
            }
        } catch (Throwable ignored) {
        }
        return new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
    }

    public static PreparedToggle prepareToggle(Context context) {
        if (!isEnabled(context)) {
            throw new IllegalStateException("Enable the Samsung Settings helper first");
        }
        int current = MouseSettingsController.readPrimaryButton(context);
        int target = current == 1 ? 0 : 1;
        prefs(context).edit()
                .putInt(KEY_TARGET, target)
                .putInt(KEY_STAGE, STAGE_FIND_PRIMARY)
                .putInt(KEY_SCROLLS, 0)
                .putLong(KEY_STARTED_AT, System.currentTimeMillis())
                .remove(KEY_LAST_ERROR)
                .apply();

        Intent intent = new Intent()
                .setComponent(new ComponentName(SETTINGS_PACKAGE, SETTINGS_MOUSE_ACTIVITY))
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK
                        | Intent.FLAG_ACTIVITY_CLEAR_TOP
                        | Intent.FLAG_ACTIVITY_NO_ANIMATION
                        | Intent.FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS);
        return new PreparedToggle(target, intent);
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
        if (started > 0 && System.currentTimeMillis() - started > TIMEOUT_MS + 2000L) {
            cancelPending(context, "Previous Samsung Settings automation timed out");
            return false;
        }
        return true;
    }

    public static String diagnostics(Context context) {
        SharedPreferences p = prefs(context);
        return "samsung_settings_helper_enabled=" + isEnabled(context)
                + "\nsamsung_automation_pending=" + isPending(context)
                + "\nsamsung_last_result=" + p.getString(KEY_LAST_RESULT, "none")
                + "\nsamsung_last_error=" + p.getString(KEY_LAST_ERROR, "none");
    }

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        requestTileRefresh();
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (!isPending(this)) return;
        CharSequence pkg = event == null ? null : event.getPackageName();
        if (pkg == null || !SETTINGS_PACKAGE.contentEquals(pkg)) return;
        processPending();
    }

    @Override
    public void onInterrupt() {
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

        AccessibilityNodeInfo root = getRootInActiveWindow();
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
            }, 300L);
            return;
        }

        retrySoon();
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
        Toast.makeText(this,
                target == 1 ? "Right mouse button is primary" : "Left mouse button is primary",
                Toast.LENGTH_SHORT).show();
        handler.postDelayed(() -> performGlobalAction(GLOBAL_ACTION_BACK), 180L);
    }

    private void fail(String error) {
        cancelPending(this, error);
        requestTileRefresh();
        Toast.makeText(this, "Mouse toggle failed: " + error, Toast.LENGTH_LONG).show();
        handler.postDelayed(() -> performGlobalAction(GLOBAL_ACTION_BACK), 180L);
    }

    private void retrySoon() {
        handler.removeCallbacks(retryRunnable);
        handler.postDelayed(retryRunnable, 180L);
    }

    private final Runnable retryRunnable = this::processPending;

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

    public static final class PreparedToggle {
        public final int target;
        public final Intent settingsIntent;

        PreparedToggle(int target, Intent settingsIntent) {
            this.target = target;
            this.settingsIntent = settingsIntent;
        }
    }
}
