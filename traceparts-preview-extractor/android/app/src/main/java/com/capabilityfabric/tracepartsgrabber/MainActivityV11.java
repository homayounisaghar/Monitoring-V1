package com.capabilityfabric.tracepartsgrabber;

import android.app.Activity;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import androidx.webkit.WebViewCompat;
import androidx.webkit.WebViewFeature;

import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

public class MainActivityV11 extends Activity {
    private static final String TARGET_URL = "https://www.traceparts.com/fr/product/schneider-electric-interrupteurs-a-pedale-plastique-universelle-xpe-a-pedale-simple-sans-capot-de-protection-2-entrees-de-cable-pour-presseetoupe-1-iso-m20-1-iso-m16-1-cran-1-contact-o-f-noir?CatalogPath=TRACEPARTS:TP09007004&PartNumber=XPEA110&Product=10-31032006-112260";
    private static final String MODEL_PATH_ENDPOINT = "https://www.traceparts.com/fr/api/v/path?CADDetailLevelID=0&Product=10-31032006-112260&SelectionPath=1%7C1%7C1%7C1%7C&ServiceType=1";
    private static final String VERSION = "1.1.0";

    private WebView webView;
    private EditText address;
    private Button captureButton;
    private TextView status;
    private String hookScript = "";
    private final StringBuilder visibleLog = new StringBuilder();
    private CaptureStore store;
    private boolean captureActive;
    private boolean documentStartSupported;
    private String runName = "";

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        store = new CaptureStore();
        hookScript = readAsset("tpx_hook.js");
        makeUi();
        configureWebView();
        address.setText(TARGET_URL);
        beginCapture(false, true);
    }

    private void makeUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.WHITE);

        LinearLayout top = new LinearLayout(this);
        top.setOrientation(LinearLayout.HORIZONTAL);
        top.setPadding(dp(5), dp(3), dp(5), 0);
        address = new EditText(this);
        address.setSingleLine(true);
        address.setTextSize(11f);
        top.addView(address, new LinearLayout.LayoutParams(0, dp(44), 1f));
        Button go = button("GO");
        go.setOnClickListener(v -> openAddress());
        top.addView(go, new LinearLayout.LayoutParams(dp(60), dp(44)));
        root.addView(top);

        LinearLayout controls = new LinearLayout(this);
        controls.setOrientation(LinearLayout.HORIZONTAL);
        controls.setGravity(Gravity.CENTER_VERTICAL);
        controls.setPadding(dp(4), 0, dp(4), 0);

        Button back = button("BACK");
        back.setOnClickListener(v -> { if (webView.canGoBack()) webView.goBack(); });
        controls.addView(back, new LinearLayout.LayoutParams(0, dp(44), 1f));

        Button reload = button("RELOAD");
        reload.setOnClickListener(v -> webView.reload());
        controls.addView(reload, new LinearLayout.LayoutParams(0, dp(44), 1f));

        Button preview = button("PREVIEW");
        preview.setOnClickListener(v -> {
            if (!captureActive) beginCapture(false, false);
            webView.postDelayed(() -> findPreview(true), 250);
        });
        controls.addView(preview, new LinearLayout.LayoutParams(0, dp(44), 1f));

        captureButton = button("STOP");
        captureButton.setOnClickListener(v -> { if (captureActive) stopCapture(); else beginCapture(false, false); });
        controls.addView(captureButton, new LinearLayout.LayoutParams(0, dp(44), .9f));

        Button files = button("FILES");
        files.setOnClickListener(v -> openDownloads());
        controls.addView(files, new LinearLayout.LayoutParams(0, dp(44), .9f));
        root.addView(controls);

        webView = new WebView(this);
        root.addView(webView, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        ScrollView sv = new ScrollView(this);
        status = new TextView(this);
        status.setTextSize(10.3f);
        status.setTextColor(Color.DKGRAY);
        status.setPadding(dp(7), dp(4), dp(7), dp(5));
        sv.addView(status);
        root.addView(sv, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(126)));
        setContentView(root);
        logUi("v1.1 ready. Capture starts automatically; browse normally until Preview is visible.");
    }

    private Button button(String text) {
        Button b = new Button(this);
        b.setText(text);
        b.setTextSize(11f);
        b.setAllCaps(false);
        return b;
    }

    private void configureWebView() {
        WebView.setWebContentsDebuggingEnabled(true);
        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null);
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setUseWideViewPort(true);
        s.setLoadWithOverviewMode(false);
        s.setBuiltInZoomControls(true);
        s.setDisplayZoomControls(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setSupportMultipleWindows(false);

        String ua = s.getUserAgentString();
        if (ua != null) {
            ua = ua.replace("; wv", "").replace(" Version/4.0", "");
            s.setUserAgentString(ua);
        }

        CookieManager cm = CookieManager.getInstance();
        cm.setAcceptCookie(true);
        cm.setAcceptThirdPartyCookies(webView, true);

        Set<String> origins = new HashSet<>();
        origins.add("https://traceparts.com");
        origins.add("https://*.traceparts.com");

        if (WebViewFeature.isFeatureSupported(WebViewFeature.WEB_MESSAGE_LISTENER)) {
            WebViewCompat.addWebMessageListener(webView, "TPNative", origins,
                    (view, message, sourceOrigin, isMainFrame, replyProxy) -> {
                        if (!trusted(sourceOrigin)) return;
                        String data = message.getData();
                        if (data != null) receive(data);
                    });
        } else {
            logUi("ERROR: Android System WebView is too old for the capture bridge. Update Android System WebView/Chrome.");
        }

        if (!hookScript.isEmpty() && WebViewFeature.isFeatureSupported(WebViewFeature.DOCUMENT_START_SCRIPT)) {
            WebViewCompat.addDocumentStartJavaScript(webView, hookScript, origins);
            documentStartSupported = true;
        } else {
            logUi("WARNING: document-start hook unavailable; fallback injection will be used.");
        }

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                String scheme = req.getUrl().getScheme();
                return !("https".equalsIgnoreCase(scheme) || "http".equalsIgnoreCase(scheme));
            }

            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap icon) {
                address.setText(url);
                if (!documentStartSupported && url != null && url.contains("traceparts.com") && !hookScript.isEmpty()) {
                    view.evaluateJavascript(hookScript, null);
                }
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                address.setText(url);
                logUi("Loaded: " + shortUrl(url));
                if (captureActive && url != null && url.contains("traceparts.com")) {
                    view.postDelayed(() -> findPreview(false), 1400);
                    view.postDelayed(() -> findPreview(false), 3900);
                    view.postDelayed(() -> dumpResources(), 6200);
                    view.postDelayed(() -> replayLastPath(), 7600);
                }
            }
        });
    }

    private boolean trusted(Uri origin) {
        if (origin == null || !"https".equalsIgnoreCase(origin.getScheme())) return false;
        String host = origin.getHost();
        return host != null && ("traceparts.com".equals(host) || host.endsWith(".traceparts.com"));
    }

    private void openAddress() {
        String u = address.getText().toString().trim();
        if (u.length() == 0) return;
        if (!u.startsWith("https://") && !u.startsWith("http://")) u = "https://" + u;
        webView.loadUrl(u);
    }

    private void beginCapture(boolean reload, boolean initialLoad) {
        if (captureActive) {
            if (reload) webView.reload();
            return;
        }
        captureActive = true;
        runName = "XPEA110_" + new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(new Date());
        store.start(runName);
        captureButton.setText("STOP");
        logUi(initialLoad
                ? "Capture ON before first page load. Navigate normally; all later Preview traffic stays armed."
                : "Capture ON. Open/tap Preview now; use RELOAD only if you want to replay the whole page.");

        CookieManager cm = CookieManager.getInstance();
        cm.setCookie("https://www.traceparts.com", "tp_capture=1; Path=/; Domain=.traceparts.com; SameSite=Lax", ok -> {
            cm.flush();
            runOnUiThread(() -> {
                if (initialLoad) webView.loadUrl(TARGET_URL);
                else if (reload) webView.reload();
            });
        });
    }

    private void stopCapture() {
        captureActive = false;
        captureButton.setText("START");
        CookieManager cm = CookieManager.getInstance();
        cm.setCookie("https://www.traceparts.com", "tp_capture=; Max-Age=0; Path=/; Domain=.traceparts.com; SameSite=Lax", ok -> cm.flush());
        store.finish();
        logUi("Stopped. Files: Downloads/TracePartsExtractor/" + runName);
    }

    private void findPreview(boolean userRequested) {
        if (!captureActive) return;
        String js = "window.__tpxFindPreview ? window.__tpxFindPreview() : 'hook-not-ready';";
        webView.evaluateJavascript(js, value -> {
            if (userRequested || (value != null && !value.contains("not-found"))) logUi("Preview helper: " + value);
            webView.postDelayed(this::dumpResources, 2200);
            webView.postDelayed(this::replayLastPath, 3300);
        });
    }

    private void dumpResources() {
        if (!captureActive) return;
        webView.evaluateJavascript("window.__tpxDumpResources ? window.__tpxDumpResources() : -1;",
                value -> logUi("Resource candidates: " + value));
    }

    private void replayLastPath() {
        if (!captureActive) return;
        webView.evaluateJavascript("window.__tpxReplayLastPath ? window.__tpxReplayLastPath() : -2;",
                value -> {
                    if (value != null && !"-3".equals(value) && !"-2".equals(value)) logUi("Exact path replay: " + value);
                });
    }

    private void receive(String data) {
        try {
            JSONObject o = new JSONObject(data);
            String t = o.optString("t", "");
            if ("begin".equals(t)) {
                store.begin(o.optString("id"), o.optString("url"), o.optString("ct"), o.optString("source"),
                        o.optInt("status"), o.optString("headers"));
            } else if ("chunk".equals(t)) {
                store.chunk(o.optString("id"), o.optString("b64"));
            } else if ("end".equals(t)) {
                store.end(o.optString("id"), o.optLong("total", -1));
            } else if ("meta".equals(t)) {
                store.log("META transport=" + o.optString("transport") + " status=" + o.optInt("status") +
                        " ct=" + o.optString("ct") + " type=" + o.optString("type") + " url=" + o.optString("url") +
                        "\nHEADERS\n" + trim(o.optString("headers"), 5000) + "\nEND_HEADERS\n");
            } else if ("net".equals(t)) {
                String line = "NET " + o.optString("phase") + " " + o.optString("transport") + " " +
                        o.optString("method") + " " + o.optString("url") + " headers=[" + o.optString("headerNames") + "]";
                store.log(line + "\n");
                if (o.optString("url").contains("/api/v/path")) logUi("Observed real /api/v/path traffic");
            } else if ("note".equals(t)) {
                String m = o.optString("message");
                store.log("NOTE " + m + "\n");
                logUi(m);
            } else if ("error".equals(t)) {
                String m = "JS ERROR " + o.optString("where") + ": " + o.optString("message");
                store.log(m + " url=" + o.optString("url") + "\n");
                logUi(m);
            }
        } catch (Exception e) {
            logUi("Bridge parse error: " + e.getMessage());
        }
    }

    private String trim(String s, int max) {
        if (s == null) return "";
        return s.length() <= max ? s : s.substring(0, max) + "...";
    }

    private void openDownloads() {
        try {
            Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse("content://com.android.providers.downloads.documents/root/downloads"));
            startActivity(i);
        } catch (Exception e) {
            Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
            i.setType("*/*");
            i.addCategory(Intent.CATEGORY_OPENABLE);
            try { startActivity(i); } catch (Exception ignored) { logUi("Could not open Downloads."); }
        }
    }

    private String readAsset(String name) {
        try (InputStream in = getAssets().open(name); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] b = new byte[16384];
            int n;
            while ((n = in.read(b)) != -1) out.write(b, 0, n);
            return out.toString(StandardCharsets.UTF_8.name());
        } catch (Exception e) {
            logUi("ERROR loading capture hook: " + e.getMessage());
            return "";
        }
    }

    private int dp(int n) { return Math.round(n * getResources().getDisplayMetrics().density); }

    private String shortUrl(String u) {
        if (u == null) return "";
        return u.length() <= 105 ? u : u.substring(0, 102) + "...";
    }

    private void logUi(String line) {
        runOnUiThread(() -> {
            if (visibleLog.length() > 14000) visibleLog.delete(0, Math.min(6000, visibleLog.length()));
            visibleLog.append(new SimpleDateFormat("HH:mm:ss", Locale.US).format(new Date()))
                    .append("  ").append(line).append('\n');
            if (status != null) status.setText(visibleLog.toString());
        });
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack(); else super.onBackPressed();
    }

    @Override
    protected void onDestroy() {
        if (captureActive) store.finish();
        store.shutdown();
        if (webView != null) { webView.stopLoading(); webView.destroy(); }
        super.onDestroy();
    }

    private final class CaptureStore {
        private final ExecutorService io = Executors.newSingleThreadExecutor();
        private final Map<String, Item> items = new HashMap<>();
        private final AtomicInteger index = new AtomicInteger();
        private String folder = "unsorted";
        private Writer logWriter;
        private Uri logUri;
        private int saved;

        void start(String name) {
            folder = name;
            saved = 0;
            index.set(0);
            io.execute(() -> {
                closeLog();
                try {
                    logUri = pending("capture_log.txt", "text/plain", folder);
                    OutputStream out = getContentResolver().openOutputStream(logUri, "w");
                    if (out != null) {
                        logWriter = new OutputStreamWriter(out, StandardCharsets.UTF_8);
                        write("TraceParts Preview Extractor v" + VERSION + "\nTarget=" + TARGET_URL +
                                "\nKnownEndpoint=" + MODEL_PATH_ENDPOINT + "\nMode=auto-armed-before-first-load\n\n");
                    }
                } catch (Exception e) { logUi("Log create failed: " + e.getMessage()); }
            });
        }

        void begin(String id, String url, String ct, String source, int httpStatus, String headers) {
            if (id == null || id.length() == 0) return;
            io.execute(() -> {
                try {
                    File d = new File(getCacheDir(), "tpx");
                    if (!d.exists() && !d.mkdirs()) throw new IOException("cache mkdir failed");
                    File f = new File(d, safe(id) + ".part");
                    Item item = new Item(id, url, ct, source, httpStatus, f, new FileOutputStream(f));
                    items.put(id, item);
                    write("BEGIN status=" + httpStatus + " source=" + source + " ct=" + ct + " url=" + url +
                            "\nHEADERS\n" + trim(headers, 5000) + "\nEND_HEADERS\n");
                    logUi("Capturing: " + shortUrl(url));
                } catch (Exception e) { logUi("Capture begin failed: " + e.getMessage()); }
            });
        }

        void chunk(String id, String encoded) {
            if (id == null || encoded == null || encoded.length() == 0) return;
            io.execute(() -> {
                Item item = items.get(id);
                if (item == null) return;
                try {
                    byte[] bytes = Base64.decode(encoded, Base64.DEFAULT);
                    item.out.write(bytes);
                    item.bytes += bytes.length;
                } catch (Exception e) { write("CHUNK_ERROR " + id + " " + e + "\n"); }
            });
        }

        void end(String id, long reported) {
            if (id == null) return;
            io.execute(() -> {
                Item item = items.remove(id);
                if (item == null) return;
                try {
                    item.out.flush();
                    item.out.close();
                    if (item.bytes <= 0) {
                        write("EMPTY source=" + item.source + " status=" + item.status + " reported=" + reported +
                                " ct=" + item.ct + " url=" + item.url + "\n");
                        logUi("Empty response recorded (metadata kept): " + shortUrl(item.url));
                        return;
                    }
                    String name = outputName(item, index.incrementAndGet());
                    Uri uri = publish(item.temp, name, mime(item.ct, name), folder);
                    if (uri != null) {
                        saved++;
                        write("SAVED " + name + " bytes=" + item.bytes + " reported=" + reported + " ct=" + item.ct + " url=" + item.url + "\n");
                        logUi("Saved " + name + " (" + item.bytes + " bytes)");
                    }
                } catch (Exception e) {
                    write("END_ERROR " + id + " " + e + "\n");
                    logUi("Save failed: " + e.getMessage());
                } finally {
                    if (item.temp.exists()) item.temp.delete();
                }
            });
        }

        void log(String line) { io.execute(() -> write(line)); }

        void finish() {
            io.execute(() -> {
                write("\nFinished. Saved=" + saved + "\n");
                closeLog();
            });
        }

        void shutdown() { io.shutdown(); }

        private Uri pending(String displayName, String mime, String subfolder) {
            ContentValues v = new ContentValues();
            v.put(MediaStore.MediaColumns.DISPLAY_NAME, displayName);
            v.put(MediaStore.MediaColumns.MIME_TYPE, mime);
            v.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/TracePartsExtractor/" + subfolder);
            v.put(MediaStore.MediaColumns.IS_PENDING, 1);
            return getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v);
        }

        private Uri publish(File temp, String name, String mime, String subfolder) throws IOException {
            ContentResolver r = getContentResolver();
            Uri uri = pending(name, mime, subfolder);
            if (uri == null) throw new IOException("MediaStore insert failed");
            boolean ok = false;
            try (BufferedInputStream in = new BufferedInputStream(new FileInputStream(temp)); OutputStream out = r.openOutputStream(uri, "w")) {
                if (out == null) throw new IOException("MediaStore output failed");
                byte[] buf = new byte[65536];
                int n;
                while ((n = in.read(buf)) != -1) out.write(buf, 0, n);
                out.flush();
                ok = true;
            } finally {
                ContentValues done = new ContentValues();
                done.put(MediaStore.MediaColumns.IS_PENDING, 0);
                r.update(uri, done, null, null);
                if (!ok) try { r.delete(uri, null, null); } catch (Exception ignored) {}
            }
            return ok ? uri : null;
        }

        private void write(String s) {
            try { if (logWriter != null) { logWriter.write(s); logWriter.flush(); } } catch (Exception ignored) {}
        }

        private void closeLog() {
            try { if (logWriter != null) logWriter.close(); } catch (Exception ignored) {}
            logWriter = null;
            if (logUri != null) {
                try {
                    ContentValues v = new ContentValues();
                    v.put(MediaStore.MediaColumns.IS_PENDING, 0);
                    getContentResolver().update(logUri, v, null, null);
                } catch (Exception ignored) {}
            }
            logUri = null;
        }

        private String outputName(Item item, int number) {
            String raw = "asset";
            try {
                String s = Uri.parse(item.url).getLastPathSegment();
                if (s != null && s.length() > 0 && s.length() < 100) raw = s;
            } catch (Exception ignored) {}
            raw = safe(raw);
            String ext = knownExt(raw);
            if (ext.length() == 0) ext = sniff(item.temp, item.ct);
            if (ext.length() > 0 && !raw.toLowerCase(Locale.US).endsWith(ext)) raw += ext;
            return String.format(Locale.US, "%03d_%s", number, raw);
        }

        private String knownExt(String name) {
            String n = name.toLowerCase(Locale.US);
            String[] es = {".glb", ".gltf", ".bin", ".obj", ".stl", ".ply", ".3mf", ".dae", ".fbx", ".step", ".stp", ".iges", ".igs", ".scs", ".scz", ".s3d", ".zip", ".json", ".txt"};
            for (String e : es) if (n.endsWith(e)) return e;
            return "";
        }

        private String sniff(File f, String ct) {
            try (FileInputStream in = new FileInputStream(f)) {
                byte[] h = new byte[16];
                int n = in.read(h);
                if (n >= 4 && h[0] == 'g' && h[1] == 'l' && h[2] == 'T' && h[3] == 'F') return ".glb";
                if (n >= 4 && h[0] == 'P' && h[1] == 'K' && h[2] == 3 && h[3] == 4) return ".zip";
                int p = 0;
                while (p < n && Character.isWhitespace((char) h[p])) p++;
                if (p < n && (h[p] == '{' || h[p] == '[')) return ".json";
            } catch (Exception ignored) {}
            String c = ct == null ? "" : ct.toLowerCase(Locale.US);
            if (c.contains("gltf-binary")) return ".glb";
            if (c.contains("gltf+json")) return ".gltf";
            if (c.contains("json")) return ".json";
            if (c.contains("zip")) return ".zip";
            if (c.startsWith("text/")) return ".txt";
            return ".bin";
        }

        private String mime(String ct, String name) {
            if (ct != null && ct.trim().length() > 0) {
                int semicolon = ct.indexOf(';');
                return semicolon >= 0 ? ct.substring(0, semicolon).trim() : ct.trim();
            }
            String n = name.toLowerCase(Locale.US);
            if (n.endsWith(".json") || n.endsWith(".gltf")) return "application/json";
            if (n.endsWith(".txt")) return "text/plain";
            if (n.endsWith(".zip")) return "application/zip";
            return "application/octet-stream";
        }

        private String safe(String s) {
            if (s == null || s.length() == 0) return "asset";
            String out = s.replaceAll("[^A-Za-z0-9._-]+", "_").replaceAll("_+", "_");
            if (out.length() == 0) out = "asset";
            return out.length() > 110 ? out.substring(0, 110) : out;
        }
    }

    private static final class Item {
        final String id, url, ct, source;
        final int status;
        final File temp;
        final FileOutputStream out;
        long bytes;

        Item(String id, String url, String ct, String source, int status, File temp, FileOutputStream out) {
            this.id = id;
            this.url = url;
            this.ct = ct;
            this.source = source;
            this.status = status;
            this.temp = temp;
            this.out = out;
        }
    }
}
