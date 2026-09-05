package com.homayoun.mouseinstaller;

import android.content.ComponentName;
import android.content.Context;
import android.content.ServiceConnection;
import android.content.pm.PackageManager;
import android.os.IBinder;

import rikka.shizuku.Shizuku;

public final class ShizukuInstallerBridge {
    public interface Callback {
        void onResult(String report, String error);
    }

    private ShizukuInstallerBridge() {
    }

    public static boolean hasPermission() {
        try {
            return Shizuku.checkSelfPermission() == PackageManager.PERMISSION_GRANTED;
        } catch (Throwable ignored) {
            return false;
        }
    }

    public static void install(Context context, byte[] apkBytes, Callback callback) {
        execute(context, apkBytes, false, callback);
    }

    public static void probe(Context context, Callback callback) {
        execute(context, null, true, callback);
    }

    private static void execute(
            Context context,
            byte[] apkBytes,
            boolean probe,
            Callback callback) {
        if (!hasPermission()) {
            callback.onResult(null, "Shizuku permission is not granted");
            return;
        }

        ComponentName component = new ComponentName(
                context.getPackageName(), InstallerUserService.class.getName());
        Shizuku.UserServiceArgs args = new Shizuku.UserServiceArgs(component)
                .daemon(false)
                .processNameSuffix("installer")
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
                        IInstallerService service = IInstallerService.Stub.asInterface(binder);
                        String report = probe ? service.probe() : service.installApk(apkBytes);
                        callback.onResult(report, null);
                    } catch (Throwable e) {
                        callback.onResult(null, message(e));
                    } finally {
                        safeUnbind(args, holder[0]);
                    }
                }, "mouse-toggle-installer-operation").start();
            }

            @Override
            public void onServiceDisconnected(ComponentName name) {
            }
        };

        try {
            Shizuku.bindUserService(args, holder[0]);
        } catch (Throwable e) {
            callback.onResult(null, message(e));
        }
    }

    private static void safeUnbind(Shizuku.UserServiceArgs args, ServiceConnection connection) {
        try {
            Shizuku.unbindUserService(args, connection, true);
        } catch (Throwable ignored) {
        }
    }

    private static String message(Throwable throwable) {
        String message = throwable.getMessage();
        return message == null ? throwable.toString() : message;
    }
}
