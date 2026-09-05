package com.capabilityfabric.tracepartsgrabber;

import android.app.Activity;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
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

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

public class MainActivity extends Activity {
    private static final String APP_VERSION = "1.2.0";
    private static final long CAPTURE_WINDOW_MS = 10_000L;
    private static final long FINAL_WAIT_MS = 8_000L;
    private static final long MAX_SINGLE_RESOURCE = 150L * 1024L * 1024L;
    private static final int MAX_NATIVE_CANDIDATES = 120;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private final ExecutorService networkExecutor = Executors.newFixedThreadPool(4);
    private final StringBuilder visibleLog = new StringBuilder();
    private final List<ViewerCandidate> viewers = Collections.synchronizedList(new ArrayList<>());
    private final List<FrameBox> frames = Collections.synchronizedList(new ArrayList<>());
    private final Set<String> nativeDownloadSeen = Collections.synchronizedSet(new HashSet<>());
    private final AtomicInteger pendingDownloads = new AtomicInteger(0);

    private WebView webView;
    private EditText address;
    private Button captureButton;
    private TextView status;
    private String hookScript = "";
    private String currentPageUrl = "";
    private String selectedFrameHref = "";
    private String selectedDescription = "";
    private boolean extracting = false;
    private boolean documentStartSupported = false;
    private long finalizeDeadline = 0L;
    private CaptureStore store;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        hookScript = readAssetText("viewer_hook.js");
        makeUi();
        configureWebView();
        String last = getPreferences(MODE_PRIVATE).getString("last_url", "");
        address.setText(last);
        logUi("Paste a page URL, press GO, scroll until the desired 3D viewer is visible, then press EXTRACT ZIP.");
    }

    @Override
    protected void onDestroy() {
        networkExecutor.shutdownNow();
        if (webView != null) webView.destroy();
        super.onDestroy();
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
        address.setHint("https://example.com/page-with-3d-viewer");
        address.setTextSize(11f);
        top.addView(address, new LinearLayout.LayoutParams(0, dp(44), 1f));
        Button go = button("GO");
        go.setOnClickListener(v -> openAddress());
        top.addView(go, new LinearLayout.LayoutParams(dp(64), dp(44)));
        root.addView(top);

        LinearLayout controls = new LinearLayout(this);
        controls.setOrientation(LinearLayout.HORIZONTAL);
        controls.setGravity(Gravity.CENTER_VERTICAL);
        controls.setPadding(dp(5), 0, dp(5), 0);

        Button back = button("BACK");
        back.setOnClickListener(v -> { if (webView.canGoBack()) webView.goBack(); });
        controls.addView(back, new LinearLayout.LayoutParams(0, dp(44), .8f));

        Button reload = button("RELOAD");
        reload.setOnClickListener(v -> webView.reload());
        controls.addView(reload, new LinearLayout.LayoutParams(0, dp(44), .9f));

        captureButton = button("EXTRACT ZIP");
        captureButton.setOnClickListener(v -> { if (extracting) finishNow(); else startExtraction(); });
        controls.addView(captureButton, new LinearLayout.LayoutParams(0, dp(44), 1.35f));

        Button files = button("FILES");
        files.setOnClickListener(v -> openDownloads());
        controls.addView(files, new LinearLayout.LayoutParams(0, dp(44), .75f));
        root.addView(controls);

        webView = new WebView(this);
        root.addView(webView, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        ScrollView sv = new ScrollView(this);
        status = new TextView(this);
        status.setTextSize(10.5f);
        status.setTextColor(Color.DKGRAY);
        status.setPadding(dp(7), dp(4), dp(7), dp(5));
        sv.addView(status);
        root.addView(sv, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(118)));
        setContentView(root);
    }

    private Button button(String text) {
        Button b = new Button(this);
        b.setText(text);
        b.setAllCaps(false);
        return b;
    }

    private void configureWebView() {
        WebView.setWebContentsDebuggingEnabled(false);
        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null);

        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setUseWideViewPort(true);
        s.setBuiltInZoomControls(true);
        s.setDisplayZoomControls(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setJavaScriptCanOpenWindowsAutomatically(true);
        s.setSupportMultipleWindows(false);

        CookieManager cm = CookieManager.getInstance();
        cm.setAcceptCookie(true);
        cm.setAcceptThirdPartyCookies(webView, true);

        Set<String> origins = new HashSet<>();
        origins.add("*");

        if (WebViewFeature.isFeatureSupported(WebViewFeature.WEB_MESSAGE_LISTENER)) {
            WebViewCompat.addWebMessageListener(webView, "ViewerNative", origins,
                    (view, message, sourceOrigin, isMainFrame, replyProxy) -> {
                        String data = message.getData();
                        if (data != null) receive(data);
                    });
        } else {
            logUi("ERROR: Android System WebView is too old for the capture bridge. Update Android System WebView.");
        }

        if (WebViewFeature.isFeatureSupported(WebViewFeature.DOCUMENT_START_SCRIPT)) {
            WebViewCompat.addDocumentStartJavaScript(webView, hookScript, origins);
            documentStartSupported = true;
        } else {
            logUi("WARNING: document-start injection is unavailable; extraction may miss viewers that initialize very early.");
        }

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                String scheme = req.getUrl().getScheme();
                if ("https".equalsIgnoreCase(scheme) || "http".equalsIgnoreCase(scheme)) return false;
                try { startActivity(new Intent(Intent.ACTION_VIEW, req.getUrl())); } catch (Exception ignored) {}
                return true;
            }

            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap icon) {
                currentPageUrl = url == null ? "" : url;
                address.setText(currentPageUrl);
                if (!documentStartSupported && !hookScript.isEmpty()) view.evaluateJavascript(hookScript, null);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                currentPageUrl = url == null ? "" : url;
                address.setText(currentPageUrl);
                if (!documentStartSupported && !hookScript.isEmpty()) view.evaluateJavascript(hookScript, null);
                logUi("Loaded: " + shortUrl(currentPageUrl));
            }
        });
    }

    private void openAddress() {
        String u = address.getText().toString().trim();
        if (u.isEmpty()) return;
        if (!u.startsWith("https://") && !u.startsWith("http://")) u = "https://" + u;
        getPreferences(MODE_PRIVATE).edit().putString("last_url", u).apply();
        webView.loadUrl(u);
    }

    private void startExtraction() {
        if (currentPageUrl.isEmpty() || "about:blank".equals(currentPageUrl)) {
            logUi("Open a page first.");
            return;
        }
        extracting = true;
        selectedFrameHref = "";
        selectedDescription = "";
        viewers.clear();
        frames.clear();
        nativeDownloadSeen.clear();
        pendingDownloads.set(0);
        store = new CaptureStore(currentPageUrl);
        captureButton.setText("FINISH NOW");
        logUi("Scanning the visible page for the topmost 3D viewer...");
        webView.evaluateJavascript("window.__VEX_SCAN_ALL && window.__VEX_SCAN_ALL();", null);
        handler.postDelayed(this::selectViewerAndCapture, 1100L);
    }

    private void selectViewerAndCapture() {
        if (!extracting) return;
        ViewerCandidate best = null;
        double bestY = Double.POSITIVE_INFINITY;

        synchronized (viewers) {
            for (ViewerCandidate c : viewers) {
                double y;
                if (c.main) {
                    y = c.y;
                } else {
                    FrameBox box = matchFrame(c.href);
                    if (box == null) continue;
                    y = box.y + Math.max(0.0, c.y);
                }
                if (y < bestY || (Math.abs(y - bestY) < 2.0 && c.knownWebgl && best != null && !best.knownWebgl)) {
                    best = c;
                    bestY = y;
                }
            }
        }

        if (best != null) {
            selectedFrameHref = best.href;
            selectedDescription = best.kind + (best.knownWebgl ? " WebGL" : " canvas") + (best.lib.isEmpty() ? "" : " / " + best.lib);
            logUi("Selected topmost visible viewer: " + selectedDescription + " @ " + shortUrl(selectedFrameHref));
        } else {
            ViewerCandidate unmatched = firstUnmatchedChildViewer();
            if (unmatched != null) {
                selectedFrameHref = unmatched.href;
                selectedDescription = unmatched.kind + (unmatched.knownWebgl ? " WebGL" : " canvas") + " / iframe fallback";
                logUi("Selected visible viewer iframe by fallback: " + shortUrl(selectedFrameHref));
            } else {
                selectedFrameHref = currentPageUrl;
                selectedDescription = "fallback current page";
                logUi("No WebGL canvas was positively identified; capturing model-like resources from the current page.");
            }
        }

        String js = "window.__VEX_CAPTURE_ALL && window.__VEX_CAPTURE_ALL(" + JSONObject.quote(selectedFrameHref) + ");";
        webView.evaluateJavascript(js, null);
        finalizeDeadline = System.currentTimeMillis() + CAPTURE_WINDOW_MS + FINAL_WAIT_MS;
        handler.postDelayed(this::finishNow, CAPTURE_WINDOW_MS);
    }

    private ViewerCandidate firstUnmatchedChildViewer() {
        ViewerCandidate best = null;
        synchronized (viewers) {
            for (ViewerCandidate c : viewers) {
                if (c.main) continue;
                if (best == null || (c.knownWebgl && !best.knownWebgl) || c.y < best.y) best = c;
            }
        }
        return best;
    }

    private FrameBox matchFrame(String href) {
        String host = hostOf(href);
        FrameBox best = null;
        synchronized (frames) {
            for (FrameBox f : frames) {
                if (f.src.isEmpty()) continue;
                boolean exact = stripFragment(f.src).equals(stripFragment(href));
                boolean hostMatch = !host.isEmpty() && host.equalsIgnoreCase(hostOf(f.src));
                if (!exact && !hostMatch) continue;
                if (best == null || f.y < best.y) best = f;
            }
        }
        return best;
    }

    private void finishNow() {
        if (!extracting || store == null) return;
        webView.evaluateJavascript("window.__VEX_STOP_ALL && window.__VEX_STOP_ALL();", null);
        store.closeOpenStreams();
        waitForDownloadsOrPackage();
    }

    private void waitForDownloadsOrPackage() {
        if (!extracting || store == null) return;
        if (pendingDownloads.get() > 0 && System.currentTimeMillis() < finalizeDeadline) {
            logUi("Finishing downloads... pending=" + pendingDownloads.get());
            handler.postDelayed(this::waitForDownloadsOrPackage, 450L);
            return;
        }

        extracting = false;
        captureButton.setText("EXTRACT ZIP");
        final CaptureStore completedStore = store;
        final String pageUrl = currentPageUrl;
        final String viewerHref = selectedFrameHref;
        final String viewerDesc = selectedDescription;

        networkExecutor.submit(() -> {
            try {
                CaptureStore.ZipResult result = completedStore.createZip(pageUrl, viewerHref, viewerDesc);
                runOnUiThread(() -> {
                    if (result.resourceCount > 0) {
                        logUi("Saved one ZIP: Downloads/" + result.name + " — " + result.resourceCount + " unique resources, " + humanBytes(result.bytes));
                    } else {
                        logUi("ZIP created, but no model-like resource body was captured. Send me the ZIP/log if you want me to inspect why.");
                    }
                });
            } catch (Exception e) {
                runOnUiThread(() -> logUi("ZIP ERROR: " + e.getClass().getSimpleName() + ": " + e.getMessage()));
            }
        });
    }

    private void receive(String raw) {
        try {
            JSONObject o = new JSONObject(raw);
            String t = o.optString("t", "");

            if ("viewer".equals(t) && extracting && selectedFrameHref.isEmpty()) {
                viewers.add(new ViewerCandidate(
                        o.optString("href", ""), o.optBoolean("isMain", false), o.optString("kind", "canvas"),
                        o.optBoolean("knownWebgl", false), o.optDouble("y", 0), o.optString("lib", "")));
                return;
            }
            if ("framebox".equals(t) && extracting && selectedFrameHref.isEmpty()) {
                frames.add(new FrameBox(o.optString("src", ""), o.optDouble("y", 0)));
                return;
            }
            if (!extracting || store == null) return;

            if ("begin".equals(t)) {
                store.begin(o.optString("id"), o.optString("url"), o.optString("ct"), o.optString("source"), o.optInt("status"), o.optString("href"));
            } else if ("chunk".equals(t)) {
                store.chunk(o.optString("id"), o.optString("b64"));
            } else if ("end".equals(t)) {
                store.end(o.optString("id"));
            } else if ("candidate".equals(t)) {
                String href = o.optString("href", "");
                if (stripFragment(href).equals(stripFragment(selectedFrameHref))) {
                    downloadCandidate(o.optString("url", ""), href, o.optString("initiator", ""), o.optInt("priority", 0));
                }
            } else if ("note".equals(t)) {
                String msg = o.optString("message", "");
                store.log("JS " + msg + " href=" + shortUrl(o.optString("href", "")));
                if (msg.contains("resource candidates")) logUi(msg);
            } else if ("error".equals(t)) {
                store.log("JS ERROR " + o.optString("where") + ": " + o.optString("message") + " url=" + o.optString("url"));
            }
        } catch (Exception e) {
            if (store != null) store.log("Bridge parse error: " + e);
        }
    }

    private void downloadCandidate(String url, String referer, String initiator, int priority) {
        if (url == null || url.isEmpty() || nativeDownloadSeen.size() >= MAX_NATIVE_CANDIDATES) return;
        if (!isSafeRemoteUrl(url)) {
            store.log("Skipped unsafe/non-remote candidate: " + shortUrl(url));
            return;
        }
        if (!nativeDownloadSeen.add(url)) return;

        String cookie = CookieManager.getInstance().getCookie(url);
        String ua = webView.getSettings().getUserAgentString();
        pendingDownloads.incrementAndGet();
        networkExecutor.submit(() -> {
            HttpURLConnection conn = null;
            File tmp = null;
            try {
                conn = (HttpURLConnection) new URL(url).openConnection();
                conn.setInstanceFollowRedirects(true);
                conn.setConnectTimeout(15_000);
                conn.setReadTimeout(35_000);
                conn.setRequestProperty("User-Agent", ua == null ? "Mozilla/5.0" : ua);
                conn.setRequestProperty("Accept", "*/*");
                if (cookie != null && !cookie.isEmpty()) conn.setRequestProperty("Cookie", cookie);
                if (referer != null && referer.startsWith("http")) conn.setRequestProperty("Referer", referer);

                int statusCode = conn.getResponseCode();
                if (statusCode < 200 || statusCode >= 300) {
                    store.log("Native candidate HTTP " + statusCode + " " + shortUrl(url));
                    return;
                }
                long declared = conn.getContentLengthLong();
                if (declared > MAX_SINGLE_RESOURCE) {
                    store.log("Skipped resource >150MB: " + shortUrl(url));
                    return;
                }
                String ct = conn.getContentType();
                tmp = store.newTempFile(url, ct);
                long total = 0;
                try (InputStream in = new BufferedInputStream(conn.getInputStream());
                     OutputStream out = new BufferedOutputStream(new FileOutputStream(tmp))) {
                    byte[] buf = new byte[64 * 1024];
                    int n;
                    while ((n = in.read(buf)) != -1) {
                        total += n;
                        if (total > MAX_SINGLE_RESOURCE) throw new IOException("resource exceeded 150MB limit");
                        out.write(buf, 0, n);
                    }
                }
                if (total > 0) {
                    store.registerFile(url, ct, "native-download:" + initiator + ":p" + priority, statusCode, referer, tmp, total);
                } else if (tmp.exists()) {
                    tmp.delete();
                }
            } catch (Exception e) {
                if (tmp != null && tmp.exists()) tmp.delete();
                store.log("Native candidate failed: " + e.getClass().getSimpleName() + " " + shortUrl(url));
            } finally {
                if (conn != null) conn.disconnect();
                pendingDownloads.decrementAndGet();
            }
        });
    }

    private boolean isSafeRemoteUrl(String value) {
        try {
            Uri u = Uri.parse(value);
            String scheme = u.getScheme();
            String host = u.getHost();
            if (!("https".equalsIgnoreCase(scheme) || "http".equalsIgnoreCase(scheme)) || host == null) return false;
            String h = host.toLowerCase(Locale.ROOT);
            if (h.equals("localhost") || h.equals("::1") || h.endsWith(".local") || h.startsWith("127.") || h.startsWith("10.") || h.startsWith("192.168.") || h.startsWith("169.254.")) return false;
            if (h.startsWith("172.")) {
                String[] parts = h.split("\\.");
                if (parts.length > 1) {
                    int second = Integer.parseInt(parts[1]);
                    if (second >= 16 && second <= 31) return false;
                }
            }
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    private void openDownloads() {
        Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("application/zip");
        try { startActivity(i); } catch (Exception e) { logUi("Could not open the file picker."); }
    }

    private String readAssetText(String name) {
        try (InputStream in = getAssets().open(name); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] buf = new byte[16 * 1024];
            int n;
            while ((n = in.read(buf)) != -1) out.write(buf, 0, n);
            return out.toString(StandardCharsets.UTF_8.name());
        } catch (Exception e) {
            return "";
        }
    }

    private void logUi(String line) {
        runOnUiThread(() -> {
            String stamp = new SimpleDateFormat("HH:mm:ss", Locale.US).format(new Date());
            visibleLog.append(stamp).append("  ").append(line).append('\n');
            if (visibleLog.length() > 7000) visibleLog.delete(0, visibleLog.length() - 6000);
            status.setText(visibleLog.toString());
        });
    }

    private int dp(int n) {
        return Math.round(n * getResources().getDisplayMetrics().density);
    }

    private static String stripFragment(String u) {
        if (u == null) return "";
        int i = u.indexOf('#');
        return i >= 0 ? u.substring(0, i) : u;
    }

    private static String hostOf(String u) {
        try {
            String h = Uri.parse(u).getHost();
            return h == null ? "" : h;
        } catch (Exception e) {
            return "";
        }
    }

    private static String shortUrl(String u) {
        if (u == null) return "";
        return u.length() <= 110 ? u : u.substring(0, 107) + "...";
    }

    private static String humanBytes(long n) {
        if (n < 1024) return n + " B";
        if (n < 1024L * 1024L) return String.format(Locale.US, "%.1f KB", n / 1024.0);
        return String.format(Locale.US, "%.1f MB", n / (1024.0 * 1024.0));
    }

    private static final class ViewerCandidate {
        final String href;
        final boolean main;
        final String kind;
        final boolean knownWebgl;
        final double y;
        final String lib;

        ViewerCandidate(String href, boolean main, String kind, boolean knownWebgl, double y, String lib) {
            this.href = href;
            this.main = main;
            this.kind = kind;
            this.knownWebgl = knownWebgl;
            this.y = y;
            this.lib = lib;
        }
    }

    private static final class FrameBox {
        final String src;
        final double y;

        FrameBox(String src, double y) {
            this.src = src;
            this.y = y;
        }
    }

    private final class CaptureStore {
        private final File dir;
        private final Map<String, OpenCapture> open = new HashMap<>();
        private final List<ResourceRecord> records = new ArrayList<>();
        private final StringBuilder log = new StringBuilder();
        private final AtomicInteger seq = new AtomicInteger(0);

        CaptureStore(String pageUrl) {
            dir = new File(getCacheDir(), "viewer-capture-" + UUID.randomUUID());
            if (!dir.mkdirs() && !dir.isDirectory()) throw new IllegalStateException("Cannot create capture temp directory");
            log("3D Viewer Extractor v" + APP_VERSION);
            log("Page: " + pageUrl);
        }

        synchronized void log(String s) {
            String stamp = new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date());
            log.append(stamp).append(' ').append(s).append('\n');
        }

        synchronized File newTempFile(String url, String ct) throws IOException {
            String name = String.format(Locale.US, "%03d_%s", seq.incrementAndGet(), safeBaseName(url, ct));
            return new File(dir, name);
        }

        synchronized void begin(String id, String url, String ct, String source, int statusCode, String href) {
            if (id == null || id.isEmpty() || open.containsKey(id)) return;
            try {
                File f = newTempFile(url, ct);
                OpenCapture oc = new OpenCapture(url, ct, source, statusCode, href, f, new BufferedOutputStream(new FileOutputStream(f)));
                open.put(id, oc);
                log("BEGIN " + source + " " + statusCode + " " + shortUrl(url));
            } catch (Exception e) {
                log("BEGIN failed: " + e);
            }
        }

        synchronized void chunk(String id, String b64) {
            OpenCapture oc = open.get(id);
            if (oc == null || b64 == null || b64.isEmpty()) return;
            try {
                byte[] bytes = Base64.decode(b64, Base64.DEFAULT);
                oc.out.write(bytes);
                oc.total += bytes.length;
                if (oc.total > MAX_SINGLE_RESOURCE) throw new IOException("resource exceeded 150MB limit");
            } catch (Exception e) {
                log("CHUNK failed: " + e.getMessage());
                closeOne(id, false);
            }
        }

        synchronized void end(String id) {
            closeOne(id, true);
        }

        private void closeOne(String id, boolean keep) {
            OpenCapture oc = open.remove(id);
            if (oc == null) return;
            try { oc.out.close(); } catch (Exception ignored) {}
            if (keep && oc.total > 0) {
                records.add(new ResourceRecord(oc.url, oc.ct, oc.source, oc.statusCode, oc.href, oc.file, oc.total));
                log("SAVED " + oc.file.getName() + " bytes=" + oc.total + " " + shortUrl(oc.url));
            } else {
                oc.file.delete();
            }
        }

        synchronized void closeOpenStreams() {
            for (String id : new ArrayList<>(open.keySet())) closeOne(id, true);
        }

        synchronized void registerFile(String url, String ct, String source, int statusCode, String href, File file, long total) {
            if (file == null || !file.exists() || total <= 0) return;
            records.add(new ResourceRecord(url, ct, source, statusCode, href, file, total));
            log("SAVED " + file.getName() + " bytes=" + total + " " + shortUrl(url));
        }

        ZipResult createZip(String pageUrl, String viewerHref, String viewerDesc) throws Exception {
            closeOpenStreams();
            List<ResourceRecord> snapshot;
            String logText;
            synchronized (this) {
                snapshot = new ArrayList<>(records);
                logText = log.toString();
            }

            Map<String, ResourceRecord> unique = new LinkedHashMap<>();
            for (ResourceRecord r : snapshot) {
                if (!r.file.exists() || r.file.length() == 0) continue;
                r.sha256 = sha256(r.file);
                String key = r.sha256 + ":" + r.file.length();
                if (!unique.containsKey(key)) unique.put(key, r);
            }

            String ts = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(new Date());
            String host = hostOf(pageUrl).replaceAll("[^A-Za-z0-9._-]", "_");
            if (host.isEmpty()) host = "page";
            String zipName = "Viewer3DCapture_" + host + "_" + ts + ".zip";
            File tempZip = new File(dir, zipName);

            JSONArray resources = new JSONArray();
            for (ResourceRecord r : unique.values()) {
                JSONObject j = new JSONObject();
                j.put("file", r.file.getName());
                j.put("url", r.url);
                j.put("mime_type", r.ct);
                j.put("source", r.source);
                j.put("status", r.statusCode);
                j.put("frame", r.href);
                j.put("bytes", r.file.length());
                j.put("sha256", r.sha256);
                resources.put(j);
            }

            JSONObject manifest = new JSONObject();
            manifest.put("schema", "viewer3d-capture.v1");
            manifest.put("app_version", APP_VERSION);
            manifest.put("page_url", pageUrl == null ? "" : pageUrl);
            manifest.put("selected_viewer_frame", viewerHref == null ? "" : viewerHref);
            manifest.put("selected_viewer", viewerDesc == null ? "" : viewerDesc);
            manifest.put("captured_at", new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssZ", Locale.US).format(new Date()));
            manifest.put("resource_count", unique.size());
            manifest.put("resources", resources);
            manifest.put("note", "The app targets the topmost visible 3D viewer when detectable. Multiple inline viewers in one document can share page-level network resources.");

            try (ZipOutputStream zos = new ZipOutputStream(new BufferedOutputStream(new FileOutputStream(tempZip)))) {
                putText(zos, "manifest.json", manifest.toString(2));
                putText(zos, "capture_log.txt", logText);
                Set<String> names = new HashSet<>();
                for (ResourceRecord r : unique.values()) {
                    String entryName = r.file.getName();
                    if (!names.add(entryName)) entryName = UUID.randomUUID().toString().substring(0, 8) + "_" + entryName;
                    zos.putNextEntry(new ZipEntry(entryName));
                    try (InputStream in = new BufferedInputStream(new FileInputStream(r.file))) {
                        byte[] buf = new byte[64 * 1024];
                        int n;
                        while ((n = in.read(buf)) != -1) zos.write(buf, 0, n);
                    }
                    zos.closeEntry();
                }
            }

            long bytes = tempZip.length();
            saveToDownloads(tempZip, zipName);
            return new ZipResult(zipName, bytes, unique.size());
        }

        private void putText(ZipOutputStream zos, String name, String text) throws IOException {
            zos.putNextEntry(new ZipEntry(name));
            zos.write(text.getBytes(StandardCharsets.UTF_8));
            zos.closeEntry();
        }

        private void saveToDownloads(File src, String name) throws IOException {
            ContentResolver resolver = getContentResolver();
            ContentValues values = new ContentValues();
            values.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            values.put(MediaStore.MediaColumns.MIME_TYPE, "application/zip");
            values.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
            values.put(MediaStore.MediaColumns.IS_PENDING, 1);
            Uri uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
            if (uri == null) throw new IOException("Could not create Downloads entry");

            boolean ok = false;
            try (InputStream in = new BufferedInputStream(new FileInputStream(src)); OutputStream out = resolver.openOutputStream(uri)) {
                if (out == null) throw new IOException("Could not open Downloads output stream");
                byte[] buf = new byte[64 * 1024];
                int n;
                while ((n = in.read(buf)) != -1) out.write(buf, 0, n);
                ok = true;
            } finally {
                if (ok) {
                    ContentValues done = new ContentValues();
                    done.put(MediaStore.MediaColumns.IS_PENDING, 0);
                    resolver.update(uri, done, null, null);
                } else {
                    resolver.delete(uri, null, null);
                }
            }
        }

        private String safeBaseName(String url, String ct) {
            String base = "resource.bin";
            try {
                Uri u = Uri.parse(url == null ? "" : url);
                String seg = u.getLastPathSegment();
                if (seg != null && !seg.isEmpty()) base = seg;
            } catch (Exception ignored) {}
            int q = base.indexOf('?');
            if (q >= 0) base = base.substring(0, q);
            base = base.replaceAll("[^A-Za-z0-9._-]", "_");
            if (base.length() > 90) base = base.substring(base.length() - 90);
            if (!base.contains(".")) base += extensionFor(ct);
            return base;
        }

        private String extensionFor(String ct) {
            String c = ct == null ? "" : ct.toLowerCase(Locale.ROOT);
            if (c.contains("zip")) return ".zip";
            if (c.contains("json")) return ".json";
            if (c.contains("gltf-binary")) return ".glb";
            if (c.contains("gltf")) return ".gltf";
            if (c.startsWith("model/stl")) return ".stl";
            if (c.startsWith("model/obj")) return ".obj";
            return ".bin";
        }

        private String sha256(File f) throws Exception {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            try (InputStream in = new BufferedInputStream(new FileInputStream(f))) {
                byte[] buf = new byte[64 * 1024];
                int n;
                while ((n = in.read(buf)) != -1) md.update(buf, 0, n);
            }
            StringBuilder out = new StringBuilder();
            for (byte b : md.digest()) out.append(String.format(Locale.US, "%02x", b & 0xff));
            return out.toString();
        }

        final class ZipResult {
            final String name;
            final long bytes;
            final int resourceCount;
            ZipResult(String name, long bytes, int resourceCount) {
                this.name = name;
                this.bytes = bytes;
                this.resourceCount = resourceCount;
            }
        }
    }

    private static final class OpenCapture {
        final String url;
        final String ct;
        final String source;
        final int statusCode;
        final String href;
        final File file;
        final OutputStream out;
        long total = 0;

        OpenCapture(String url, String ct, String source, int statusCode, String href, File file, OutputStream out) {
            this.url = url;
            this.ct = ct;
            this.source = source;
            this.statusCode = statusCode;
            this.href = href;
            this.file = file;
            this.out = out;
        }
    }

    private static final class ResourceRecord {
        final String url;
        final String ct;
        final String source;
        final int statusCode;
        final String href;
        final File file;
        final long total;
        String sha256 = "";

        ResourceRecord(String url, String ct, String source, int statusCode, String href, File file, long total) {
            this.url = url == null ? "" : url;
            this.ct = ct == null ? "" : ct;
            this.source = source == null ? "" : source;
            this.statusCode = statusCode;
            this.href = href == null ? "" : href;
            this.file = file;
            this.total = total;
        }
    }
}
