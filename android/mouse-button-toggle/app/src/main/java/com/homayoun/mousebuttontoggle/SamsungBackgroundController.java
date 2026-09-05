package com.homayoun.mousebuttontoggle;

import android.content.ComponentName;
import android.content.ContentResolver;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.ProviderInfo;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Parcel;
import android.os.SystemClock;
import android.service.quicksettings.TileService;
import android.text.TextUtils;
import android.util.Base64;

import com.samsung.android.gtscell.RemoteCallback;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

public final class SamsungBackgroundController {
    private static final String SETTINGS_PACKAGE = "com.android.settings";
    private static final String PROVIDER_CLASS =
            "com.samsung.android.settings.gts.GeneralSettingsGtsProvider";
    private static final String CATEGORY =
            "com.samsung.android.settings.gts.category.MOUSE_AND_TRACKPAD";
    private static final String ITEM_KEY = "key_primary_mouse_button";
    private static final String BACKUP_KEY = "/Settings/General/PrimaryMouseKey";

    private static final String METHOD_GET_ITEM = "get_item";
    private static final String METHOD_SET_ITEM = "set_item";
    private static final String EXTRA_TARGET_CATEGORY = "target_category";
    private static final String EXTRA_GTS_ACTION = "gts_action";
    private static final String EXTRA_GTS_ITEM_KEYS = "gts_item_keys";
    private static final String EXTRA_GTS_ITEM_CELL = "gts_item_cell";
    private static final String EXTRA_FINISH_CALLBACK = "finish_callback";
    private static final String EXTRA_TIMEOUT = "timeout";

    private static final String PREFS = "samsung_background_backend";
    private static final String KEY_LAST_STAGE = "last_stage";
    private static final String KEY_LAST_RESULT = "last_result";
    private static final String KEY_LAST_ERROR = "last_error";
    private static final String KEY_LAST_PROVIDER = "last_provider";
    private static final String KEY_LAST_TARGET = "last_target";
    private static final String KEY_LAST_DURATION = "last_duration_ms";

    private static final ExecutorService EXECUTOR = Executors.newSingleThreadExecutor();
    private static final Handler MAIN = new Handler(Looper.getMainLooper());
    private static final AtomicBoolean BUSY = new AtomicBoolean(false);

    private SamsungBackgroundController() {
    }

    public interface Callback {
        void onSuccess(int newPrimary);
        void onError(String error);
    }

    public static boolean isBusy() {
        return BUSY.get();
    }

    public static boolean isProviderPresent(Context context) {
        try {
            return discoverProvider(context) != null;
        } catch (Throwable ignored) {
            return false;
        }
    }

    public static void toggleAsync(Context context, Callback callback) {
        Context app = context.getApplicationContext();
        if (!BUSY.compareAndSet(false, true)) {
            deliverError(callback, "A mouse switch is already in progress");
            return;
        }

        EXECUTOR.execute(() -> {
            long started = SystemClock.elapsedRealtime();
            int target = -1;
            try {
                record(app, "discover-provider", null, null, null, -1L);
                ProviderInfo provider = discoverProvider(app);
                if (provider == null) {
                    throw new IllegalStateException(
                            "Samsung GeneralSettingsGtsProvider was not found on this build");
                }

                String authority = firstAuthority(provider.authority);
                if (TextUtils.isEmpty(authority)) {
                    throw new IllegalStateException("Samsung background provider has no authority");
                }
                String providerSummary = providerSummary(provider);
                prefs(app).edit().putString(KEY_LAST_PROVIDER, providerSummary).apply();

                int current = MouseSettingsController.readPrimaryButton(app);
                target = current == 1 ? 0 : 1;
                prefs(app).edit().putInt(KEY_LAST_TARGET, target).apply();

                Uri uri = Uri.parse("content://" + authority);
                ContentResolver resolver = app.getContentResolver();

                record(app, "get-item", null, null, providerSummary, -1L);
                Bundle getExtras = new Bundle();
                getExtras.putString(EXTRA_TARGET_CATEGORY, CATEGORY);
                getExtras.putInt(EXTRA_GTS_ACTION, 1);
                ArrayList<String> keys = new ArrayList<>();
                keys.add(ITEM_KEY);
                getExtras.putStringArrayList(EXTRA_GTS_ITEM_KEYS, keys);

                Bundle getResult = resolver.call(uri, METHOD_GET_ITEM, null, getExtras);
                if (getResult == null) {
                    throw new IllegalStateException("Samsung get_item returned no Bundle");
                }
                String cellJson = getResult.getString(EXTRA_GTS_ITEM_CELL);
                if (TextUtils.isEmpty(cellJson)) {
                    throw new IllegalStateException(
                            "Samsung get_item returned no gts_item_cell for " + ITEM_KEY);
                }

                record(app, "prepare-item", null, null, providerSummary, -1L);
                String modifiedCell = modifyCellForTarget(cellJson, target);

                record(app, "set-item", null, null, providerSummary, -1L);
                Bundle setExtras = new Bundle();
                RemoteCallback finishCallback = new RemoteCallback(result -> {
                });
                setExtras.putParcelable(EXTRA_FINISH_CALLBACK, finishCallback);
                setExtras.putString(EXTRA_GTS_ITEM_CELL, modifiedCell);
                setExtras.putLong(EXTRA_TIMEOUT, 4000L);
                resolver.call(uri, METHOD_SET_ITEM, null, setExtras);

                record(app, "verify", null, null, providerSummary, -1L);
                long deadline = SystemClock.elapsedRealtime() + 3000L;
                int observed = MouseSettingsController.readPrimaryButton(app);
                while (observed != target && SystemClock.elapsedRealtime() < deadline) {
                    SystemClock.sleep(100L);
                    observed = MouseSettingsController.readPrimaryButton(app);
                }
                if (observed != target) {
                    throw new IllegalStateException(
                            "Samsung provider call completed but primary_mouse_button_option stayed "
                                    + observed + " (target=" + target + ")");
                }

                long duration = SystemClock.elapsedRealtime() - started;
                String result = target == 1 ? "RIGHT" : "LEFT";
                record(app, "complete", result, null, providerSummary, duration);
                refreshTile(app);
                deliverSuccess(callback, target);
            } catch (Throwable e) {
                long duration = SystemClock.elapsedRealtime() - started;
                String error = shortMessage(e);
                record(app, "failed", null, error, null, duration);
                refreshTile(app);
                deliverError(callback, error);
            } finally {
                BUSY.set(false);
            }
        });
    }

    public static String diagnostics(Context context) {
        ProviderInfo provider = null;
        String discoveryError = null;
        try {
            provider = discoverProvider(context);
        } catch (Throwable e) {
            discoveryError = shortMessage(e);
        }

        SharedPreferences p = prefs(context);
        StringBuilder out = new StringBuilder();
        out.append("samsung_background_busy=").append(isBusy());
        out.append("\nsamsung_gts_provider_found=").append(provider != null);
        if (provider != null) {
            out.append("\nsamsung_gts_provider_name=").append(nullText(provider.name));
            out.append("\nsamsung_gts_provider_authority=").append(nullText(provider.authority));
            out.append("\nsamsung_gts_provider_exported=").append(provider.exported);
            out.append("\nsamsung_gts_provider_enabled=").append(provider.enabled);
            out.append("\nsamsung_gts_provider_read_permission=")
                    .append(nullText(provider.readPermission));
            out.append("\nsamsung_gts_provider_write_permission=")
                    .append(nullText(provider.writePermission));
        }
        if (discoveryError != null) {
            out.append("\nsamsung_gts_discovery_error=").append(discoveryError);
        }
        out.append("\nsamsung_background_last_stage=")
                .append(p.getString(KEY_LAST_STAGE, "none"));
        out.append("\nsamsung_background_last_result=")
                .append(p.getString(KEY_LAST_RESULT, "none"));
        out.append("\nsamsung_background_last_error=")
                .append(p.getString(KEY_LAST_ERROR, "none"));
        out.append("\nsamsung_background_last_provider=")
                .append(p.getString(KEY_LAST_PROVIDER, "none"));
        out.append("\nsamsung_background_last_target=")
                .append(p.contains(KEY_LAST_TARGET)
                        ? Integer.toString(p.getInt(KEY_LAST_TARGET, -1))
                        : "none");
        out.append("\nsamsung_background_last_duration_ms=")
                .append(p.contains(KEY_LAST_DURATION)
                        ? Long.toString(p.getLong(KEY_LAST_DURATION, -1L))
                        : "none");
        return out.toString();
    }

    private static ProviderInfo discoverProvider(Context context) throws Exception {
        PackageManager pm = context.getPackageManager();
        PackageInfo info;
        if (Build.VERSION.SDK_INT >= 33) {
            info = pm.getPackageInfo(
                    SETTINGS_PACKAGE,
                    PackageManager.PackageInfoFlags.of(PackageManager.GET_PROVIDERS));
        } else {
            info = pm.getPackageInfo(SETTINGS_PACKAGE, PackageManager.GET_PROVIDERS);
        }
        ProviderInfo fallback = null;
        if (info.providers != null) {
            for (ProviderInfo provider : info.providers) {
                if (provider == null || TextUtils.isEmpty(provider.name)) continue;
                if (PROVIDER_CLASS.equals(provider.name)) return provider;
                if (provider.name.endsWith(".GeneralSettingsGtsProvider")) {
                    fallback = provider;
                }
            }
        }
        return fallback;
    }

    private static String modifyCellForTarget(String cellJson, int target) throws Exception {
        JSONObject cell = new JSONObject(cellJson);
        JSONArray items = cell.optJSONArray("items");
        if (items == null) {
            throw new IllegalStateException("Samsung gts_item_cell has no items array");
        }

        for (int i = 0; i < items.length(); i++) {
            JSONObject item = items.optJSONObject(i);
            if (item == null || !ITEM_KEY.equals(item.optString("item_key"))) continue;

            String itemValue = item.optString("item_value", null);
            if (TextUtils.isEmpty(itemValue)) {
                throw new IllegalStateException(ITEM_KEY + " has no item_value");
            }

            JSONObject wrapper = new JSONObject(itemValue);
            String encodedBundle = wrapper.optString("bundle", null);
            if (TextUtils.isEmpty(encodedBundle)) {
                throw new IllegalStateException(ITEM_KEY + " control wrapper has no bundle");
            }

            Bundle controlBundle = decodeBundle(encodedBundle);
            Bundle sceneBundle = controlBundle.getBundle(BACKUP_KEY);
            if (sceneBundle == null) {
                throw new IllegalStateException(
                        "PrimaryMouseKey scene is missing; control bundle keys="
                                + controlBundle.keySet());
            }
            sceneBundle.putString("value", Integer.toString(target));
            controlBundle.putBundle(BACKUP_KEY, sceneBundle);

            wrapper.put("bundle", encodeBundle(controlBundle));
            wrapper.put("forceChange", "true");
            item.put("item_value", wrapper.toString());
            return cell.toString();
        }

        throw new IllegalStateException(
                "Samsung get_item did not include " + ITEM_KEY);
    }

    private static Bundle decodeBundle(String encoded) {
        byte[] data = Base64.decode(encoded, Base64.DEFAULT);
        Parcel parcel = Parcel.obtain();
        try {
            parcel.unmarshall(data, 0, data.length);
            parcel.setDataPosition(0);
            Bundle bundle = Bundle.CREATOR.createFromParcel(parcel);
            bundle.setClassLoader(SamsungBackgroundController.class.getClassLoader());
            return bundle;
        } finally {
            parcel.recycle();
        }
    }

    private static String encodeBundle(Bundle bundle) {
        Parcel parcel = Parcel.obtain();
        try {
            bundle.writeToParcel(parcel, 0);
            return Base64.encodeToString(parcel.marshall(), Base64.NO_WRAP);
        } finally {
            parcel.recycle();
        }
    }

    private static String firstAuthority(String authority) {
        if (authority == null) return null;
        int semicolon = authority.indexOf(';');
        return semicolon >= 0 ? authority.substring(0, semicolon) : authority;
    }

    private static String providerSummary(ProviderInfo provider) {
        return nullText(provider.name)
                + "|authority=" + nullText(provider.authority)
                + "|exported=" + provider.exported
                + "|read=" + nullText(provider.readPermission)
                + "|write=" + nullText(provider.writePermission);
    }

    private static void record(
            Context context,
            String stage,
            String result,
            String error,
            String provider,
            long duration) {
        SharedPreferences.Editor e = prefs(context).edit().putString(KEY_LAST_STAGE, stage);
        if (result != null) e.putString(KEY_LAST_RESULT, result);
        if (error != null) e.putString(KEY_LAST_ERROR, error);
        else if (!"failed".equals(stage)) e.remove(KEY_LAST_ERROR);
        if (provider != null) e.putString(KEY_LAST_PROVIDER, provider);
        if (duration >= 0) e.putLong(KEY_LAST_DURATION, duration);
        e.apply();
    }

    private static void refreshTile(Context context) {
        try {
            TileService.requestListeningState(
                    context,
                    new ComponentName(context, MouseToggleTileService.class));
        } catch (Throwable ignored) {
        }
    }

    private static void deliverSuccess(Callback callback, int state) {
        if (callback == null) return;
        MAIN.post(() -> callback.onSuccess(state));
    }

    private static void deliverError(Callback callback, String error) {
        if (callback == null) return;
        MAIN.post(() -> callback.onError(error));
    }

    private static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    private static String nullText(String value) {
        return TextUtils.isEmpty(value) ? "none" : value;
    }

    private static String shortMessage(Throwable throwable) {
        if (throwable == null) return "unknown error";
        String message = throwable.getMessage();
        if (TextUtils.isEmpty(message)) message = throwable.toString();
        String type = throwable.getClass().getSimpleName();
        if (message.startsWith(type + ":")) return message;
        return type + ": " + message;
    }
}
