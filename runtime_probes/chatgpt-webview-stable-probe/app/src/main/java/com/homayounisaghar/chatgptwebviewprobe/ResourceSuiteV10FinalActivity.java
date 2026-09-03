package com.homayounisaghar.chatgptwebviewprobe;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;

import java.lang.reflect.Field;
import java.net.URI;
import java.util.regex.Pattern;

public class ResourceSuiteV10FinalActivity extends ResourceSuiteV10Activity {
    private static final Pattern UUID_PATTERN = Pattern.compile(
            "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$");
    private final Handler finalGuardHandler = new Handler(Looper.getMainLooper());
    private WebView guardedWebView;
    private String lastCanonicalCid = "-";

    private final Runnable finalGuard = new Runnable() {
        @Override public void run() {
            if (guardedWebView != null) {
                String nowCid = canonicalCid(guardedWebView.getUrl());
                if (!"-".equals(lastCanonicalCid) && !lastCanonicalCid.equals(nowCid)) {
                    clearPriorChatReceiptsIfIdle();
                }
                lastCanonicalCid = nowCid;
            }
            finalGuardHandler.postDelayed(this, 500L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        guardedWebView = findWebView(getWindow().getDecorView());
        if (guardedWebView != null) {
            int screenHeight = getResources().getDisplayMetrics().heightPixels;
            guardedWebView.setMinimumHeight(Math.max(1, screenHeight / 2));
            lastCanonicalCid = canonicalCid(guardedWebView.getUrl());
        }
        finalGuardHandler.post(finalGuard);
    }

    private void clearPriorChatReceiptsIfIdle() {
        try {
            boolean busy = getBooleanField("downloadBusy");
            boolean pending = getBooleanField("pendingActionListener");
            if (busy || pending) return;
            setField("downloadStatus", "NOT_RUN");
            setField("downloadStrategy", "-");
            setField("downloadMime", "-");
            setField("downloadBytes", 0L);
            setField("downloadSha256", "-");
            setField("downloadChunks", 0);
            setField("downloadReceiptId", "-");
            setField("passiveDownloadObserved", false);
            setField("passiveDownloadMime", "-");
            setField("passiveDownloadLength", -1L);
            setField("passiveDownloadSafeUrl", "-");
        } catch (Exception ignored) { }
    }

    private boolean getBooleanField(String name) throws Exception {
        Field f = ResourceSuiteV10Activity.class.getDeclaredField(name);
        f.setAccessible(true);
        return f.getBoolean(this);
    }

    private void setField(String name, Object value) throws Exception {
        Field f = ResourceSuiteV10Activity.class.getDeclaredField(name);
        f.setAccessible(true);
        f.set(this, value);
    }

    private static String canonicalCid(String raw) {
        try {
            if (raw == null) return "-";
            URI u = URI.create(raw);
            String[] parts = (u.getPath() == null ? "" : u.getPath()).split("/");
            for (int i = 0; i < parts.length - 1; i++) {
                if ("c".equals(parts[i]) && UUID_PATTERN.matcher(parts[i + 1]).matches()) return parts[i + 1];
            }
        } catch (Exception ignored) { }
        return "-";
    }

    private WebView findWebView(View view) {
        if (view instanceof WebView) return (WebView) view;
        if (!(view instanceof ViewGroup)) return null;
        ViewGroup group = (ViewGroup) view;
        for (int i = 0; i < group.getChildCount(); i++) {
            WebView found = findWebView(group.getChildAt(i));
            if (found != null) return found;
        }
        return null;
    }

    @Override protected void onDestroy() {
        finalGuardHandler.removeCallbacks(finalGuard);
        super.onDestroy();
    }
}
