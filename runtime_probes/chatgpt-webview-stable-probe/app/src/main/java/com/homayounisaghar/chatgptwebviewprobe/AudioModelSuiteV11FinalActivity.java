package com.homayounisaghar.chatgptwebviewprobe;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.view.View;
import android.view.ViewGroup;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.net.URI;
import java.util.ArrayList;
import java.util.Locale;
import java.util.regex.Pattern;

/** Final v0.11 launcher wrapper: preserves the real WebView chooser while keeping
 * the audio permission gate, and turns an ACTION_DOWNLOAD listener receipt into
 * the existing v0.10 artifact broker rather than treating the callback alone as
 * a completed download. No ChatGPT cookies or raw file names are extracted. */
public class AudioModelSuiteV11FinalActivity extends AudioModelSuiteV11Activity {
    private static final int REQ_V11_FILE = 1199;
    private static final Pattern UUID_PATTERN = Pattern.compile(
            "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$");
    private final Handler finalHandler = new Handler(Looper.getMainLooper());
    private WebView finalWeb;
    private ValueCallback<Uri[]> chooserCallback;

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        finalWeb = findWebView(getWindow().getDecorView());
        if (finalWeb == null) return;
        finalWeb.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        installFinalWebChromeClient();
        installFinalDownloadListener();
        recordBase("V11_FINAL_WRAPPER_READY");
    }

    private void installFinalWebChromeClient() {
        finalWeb.setWebChromeClient(new WebChromeClient() {
            @Override public void onPermissionRequest(PermissionRequest request) {
                if (request == null) return;
                runOnUiThread(() -> invokeBasePermissionRequest(request));
            }

            @Override public void onPermissionRequestCanceled(PermissionRequest request) {
                recordBase("AUDIO_WEB_PERMISSION_CANCELED");
            }

            @Override public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> callback,
                                                       FileChooserParams params) {
                if (chooserCallback != null) chooserCallback.onReceiveValue(null);
                chooserCallback = callback;
                try {
                    Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                    i.addCategory(Intent.CATEGORY_OPENABLE);
                    i.setType("*/*");
                    i.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
                    startActivityForResult(i, REQ_V11_FILE);
                    recordBase("WEB_FILE_CHOOSER_REQUESTED");
                    return true;
                } catch (Exception e) {
                    chooserCallback = null;
                    recordBase("WEB_FILE_CHOOSER_FAILED_" + e.getClass().getSimpleName());
                    return false;
                }
            }
        });
    }

    private void installFinalDownloadListener() {
        finalWeb.setDownloadListener((url, userAgent, contentDisposition, mimetype, contentLength) -> {
            setBaseFieldQuiet("resourceCallbackMime", safeMime(mimetype));
            setBaseFieldQuiet("resourceCallbackLength", contentLength);
            setBaseFieldQuiet("resourceCallbackSafeUrl", sanitizeUrl(url));
            try {
                setParentField("passiveDownloadObserved", true);
                setParentField("passiveDownloadMime", safeMime(mimetype));
                setParentField("passiveDownloadLength", contentLength);
                setParentField("passiveDownloadSafeUrl", sanitizeUrl(url));
            } catch (Exception ignored) { }

            boolean pending = getBaseBooleanQuiet("pendingResourceDownload");
            if (!pending) {
                recordBase("PASSIVE_DOWNLOAD_LISTENER_OBSERVED");
                return;
            }

            String pendingCid = String.valueOf(getBaseFieldQuiet("pendingResourceCid", "-"));
            String pendingId = String.valueOf(getBaseFieldQuiet("pendingResourceId", "-"));
            setBaseFieldQuiet("pendingResourceDownload", false);
            if (!pendingCid.equals(canonicalCid(finalWeb.getUrl()))) {
                setBaseFieldQuiet("resourceActionStatus", "UNCERTAIN_CALLBACK_AFTER_ROUTE_CHANGE");
                setBaseClaim("UNCERTAIN");
                recordBase("RESOURCE_ACTION_CALLBACK_ROUTE_CHANGED");
                return;
            }

            try {
                invokeParentNoArg("resetDownloadReceipt");
                setParentField("pendingActionResourceId", pendingId);
                setParentField("pendingActionCid", pendingCid);
                setParentField("pendingActionListener", false);
                Object callbackResource = makeParentDownloadCallback(
                        pendingId, pendingCid, url, mimetype, contentDisposition, contentLength);
                setBaseFieldQuiet("resourceActionStatus", "CALLBACK_RECEIVED_BROKER_RUNNING");
                recordBase("RESOURCE_ACTION_DOWNLOAD_CALLBACK_BROKER_STARTED");
                invokeParentExecuteResolvedDownload(callbackResource, true);
                observeBrokerOutcome(0);
            } catch (Exception e) {
                setBaseFieldQuiet("resourceActionStatus", "FAIL_BROKER_REFLECTION_" + e.getClass().getSimpleName());
                setBaseClaim("-");
                recordBase("RESOURCE_ACTION_BROKER_FAIL_" + e.getClass().getSimpleName());
            }
        });
    }

    private void observeBrokerOutcome(int attempt) {
        finalHandler.postDelayed(() -> {
            try {
                String status = String.valueOf(getParentField("downloadStatus"));
                if ("CONFIRMED".equals(status)) {
                    setBaseFieldQuiet("resourceActionStatus", "CONFIRMED_ARTIFACT_BROKER");
                    setBaseClaim("CONFIRMED");
                    recordBase("RESOURCE_ACTION_CONFIRMED_ARTIFACT_BROKER");
                    return;
                }
                if (status.startsWith("FAIL") || status.startsWith("BLOCKED") || status.startsWith("UNCERTAIN")) {
                    setBaseFieldQuiet("resourceActionStatus", status);
                    setBaseClaim(status.startsWith("UNCERTAIN") ? "UNCERTAIN" : "-");
                    recordBase("RESOURCE_ACTION_BROKER_TERMINAL_" + safeToken(status));
                    return;
                }
                if (attempt < 120) observeBrokerOutcome(attempt + 1);
                else {
                    setBaseFieldQuiet("resourceActionStatus", "UNCERTAIN_BROKER_OUTCOME_TIMEOUT");
                    setBaseClaim("UNCERTAIN");
                    recordBase("RESOURCE_ACTION_BROKER_OUTCOME_TIMEOUT");
                }
            } catch (Exception e) {
                if (attempt < 5) observeBrokerOutcome(attempt + 1);
                else recordBase("RESOURCE_ACTION_BROKER_OBSERVE_FAIL_" + e.getClass().getSimpleName());
            }
        }, 250L);
    }

    private void invokeBasePermissionRequest(PermissionRequest request) {
        try {
            Method m = AudioModelSuiteV11Activity.class.getDeclaredMethod(
                    "handleWebPermissionRequest", PermissionRequest.class);
            m.setAccessible(true);
            m.invoke(this, request);
        } catch (Exception e) {
            try { request.deny(); } catch (Exception ignored) { }
            recordBase("AUDIO_WEB_PERMISSION_REFLECTION_FAIL_" + e.getClass().getSimpleName());
        }
    }

    private Object makeParentDownloadCallback(String id, String cid, String url, String mime,
                                              String disposition, long length) throws Exception {
        Class<?> rc = Class.forName(
                "com.homayounisaghar.chatgptwebviewprobe.ResourceSuiteV10Activity$Resource");
        Method m = rc.getDeclaredMethod("fromDownloadCallback",
                String.class, String.class, String.class, String.class, String.class, long.class);
        m.setAccessible(true);
        return m.invoke(null, id, cid, url, mime, disposition, length);
    }

    private void invokeParentExecuteResolvedDownload(Object resource, boolean fromListener) throws Exception {
        Class<?> rc = Class.forName(
                "com.homayounisaghar.chatgptwebviewprobe.ResourceSuiteV10Activity$Resource");
        Method m = ResourceSuiteV10Activity.class.getDeclaredMethod(
                "executeResolvedDownload", rc, boolean.class);
        m.setAccessible(true);
        m.invoke(this, resource, fromListener);
    }

    private void invokeParentNoArg(String name) throws Exception {
        Method m = ResourceSuiteV10Activity.class.getDeclaredMethod(name);
        m.setAccessible(true);
        m.invoke(this);
    }

    private Object getParentField(String name) throws Exception {
        Field f = ResourceSuiteV10Activity.class.getDeclaredField(name);
        f.setAccessible(true);
        return f.get(this);
    }

    private void setParentField(String name, Object value) throws Exception {
        Field f = ResourceSuiteV10Activity.class.getDeclaredField(name);
        f.setAccessible(true);
        f.set(this, value);
    }

    private Object getBaseFieldQuiet(String name, Object fallback) {
        try {
            Field f = AudioModelSuiteV11Activity.class.getDeclaredField(name);
            f.setAccessible(true);
            return f.get(this);
        } catch (Exception e) { return fallback; }
    }

    private boolean getBaseBooleanQuiet(String name) {
        Object x = getBaseFieldQuiet(name, false);
        return x instanceof Boolean && (Boolean) x;
    }

    private void setBaseFieldQuiet(String name, Object value) {
        try {
            Field f = AudioModelSuiteV11Activity.class.getDeclaredField(name);
            f.setAccessible(true);
            f.set(this, value);
        } catch (Exception ignored) { }
    }

    private void setBaseClaim(String value) {
        Object x = getBaseFieldQuiet("prefsV11", null);
        if (x instanceof SharedPreferences) {
            ((SharedPreferences) x).edit().putString("resource_claim_status", value).commit();
        }
    }

    private void recordBase(String event) {
        try {
            Method m = AudioModelSuiteV11Activity.class.getDeclaredMethod("record", String.class);
            m.setAccessible(true);
            m.invoke(this, event);
        } catch (Exception ignored) { }
    }

    private static String canonicalCid(String raw) {
        try {
            URI u = URI.create(raw == null ? "" : raw);
            String[] parts = (u.getPath() == null ? "" : u.getPath()).split("/");
            for (int i = 0; i < parts.length - 1; i++) {
                if ("c".equals(parts[i]) && UUID_PATTERN.matcher(parts[i + 1]).matches()) return parts[i + 1];
            }
        } catch (Exception ignored) { }
        return "-";
    }

    private static String sanitizeUrl(String raw) {
        try {
            URI u = URI.create(raw == null ? "" : raw);
            String scheme = u.getScheme() == null ? "" : u.getScheme();
            String host = u.getHost() == null ? "" : u.getHost();
            String path = u.getPath() == null ? "" : u.getPath();
            if (scheme.isEmpty() || host.isEmpty()) return "-";
            return scheme + "://" + host + path;
        } catch (Exception e) { return "-"; }
    }

    private static String safeMime(String mime) {
        String x = mime == null ? "" : mime.trim().toLowerCase(Locale.US);
        return x.isEmpty() ? "application/octet-stream" : x;
    }

    private static String safeToken(String s) {
        String x = s == null ? "-" : s.replaceAll("[^A-Za-z0-9_.:+/-]", "_");
        return x.length() > 100 ? x.substring(0, 100) : x;
    }

    private WebView findWebView(View view) {
        if (view instanceof WebView) return (WebView) view;
        if (!(view instanceof ViewGroup)) return null;
        ViewGroup g = (ViewGroup) view;
        for (int i = 0; i < g.getChildCount(); i++) {
            WebView found = findWebView(g.getChildAt(i));
            if (found != null) return found;
        }
        return null;
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != REQ_V11_FILE || chooserCallback == null) return;
        ValueCallback<Uri[]> cb = chooserCallback;
        chooserCallback = null;
        if (resultCode != Activity.RESULT_OK || data == null) {
            cb.onReceiveValue(null);
            return;
        }
        ArrayList<Uri> uris = new ArrayList<>();
        if (data.getClipData() != null) {
            for (int i = 0; i < data.getClipData().getItemCount(); i++) {
                Uri u = data.getClipData().getItemAt(i).getUri();
                if (u != null) uris.add(u);
            }
        } else if (data.getData() != null) {
            uris.add(data.getData());
        }
        cb.onReceiveValue(uris.isEmpty() ? null : uris.toArray(new Uri[0]));
        recordBase("WEB_FILE_CHOOSER_RETURN count=" + uris.size());
    }

    @Override protected void onDestroy() {
        finalHandler.removeCallbacksAndMessages(null);
        if (chooserCallback != null) chooserCallback.onReceiveValue(null);
        chooserCallback = null;
        super.onDestroy();
    }
}
