package com.homayoun.mousebuttontoggle;

import android.content.ComponentName;
import android.content.Context;
import android.content.ServiceConnection;
import android.content.pm.PackageManager;
import android.os.IBinder;

import rikka.shizuku.Shizuku;

public final class ShizukuMouseBridge {
    public interface Callback {
        void onResult(Integer state, String error);
    }

    private ShizukuMouseBridge() {
    }

    public static boolean hasPermission() {
        try {
            return Shizuku.checkSelfPermission() == PackageManager.PERMISSION_GRANTED;
        } catch (Throwable ignored) {
            return false;
        }
    }

    public static void read(Context context, Callback callback) {
        execute(context, false, callback);
    }

    public static void toggle(Context context, Callback callback) {
        execute(context, true, callback);
    }

    private static void execute(Context context, boolean toggle, Callback callback) {
        if (!hasPermission()) {
            callback.onResult(null, "Shizuku permission is not granted");
            return;
        }

        ComponentName component = new ComponentName(
                context.getPackageName(), MouseSettingsUserService.class.getName());
        Shizuku.UserServiceArgs args = new Shizuku.UserServiceArgs(component)
                .daemon(false)
                .processNameSuffix("mouse_settings")
                .debuggable(false)
                .version(1);

        final ServiceConnection[] holder = new ServiceConnection[1];
        holder[0] = new ServiceConnection() {
            @Override
            public void onServiceConnected(ComponentName name, IBinder binder) {
                if (binder == null || !binder.pingBinder()) {
                    callback.onResult(null, "Shizuku returned an invalid service binder");
                    safeUnbind(args, holder[0]);
                    return;
                }
                new Thread(() -> {
                    try {
                        IMouseSettingsService service = IMouseSettingsService.Stub.asInterface(binder);
                        int state = toggle ? service.toggleSwapState() : service.getSwapState();
                        callback.onResult(state, null);
                    } catch (Throwable e) {
                        callback.onResult(null, e.getMessage() == null ? e.toString() : e.getMessage());
                    } finally {
                        safeUnbind(args, holder[0]);
                    }
                }, "mouse-toggle-operation").start();
            }

            @Override
            public void onServiceDisconnected(ComponentName name) {
            }
        };

        try {
            Shizuku.bindUserService(args, holder[0]);
        } catch (Throwable e) {
            callback.onResult(null, e.getMessage() == null ? e.toString() : e.getMessage());
        }
    }

    private static void safeUnbind(Shizuku.UserServiceArgs args, ServiceConnection connection) {
        try {
            Shizuku.unbindUserService(args, connection, true);
        } catch (Throwable ignored) {
        }
    }
}
