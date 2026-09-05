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
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
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

public class MainActivity extends Activity {
    private static final String TARGET_URL = "https://www.traceparts.com/fr/product/schneider-electric-interrupteurs-a-pedale-plastique-universelle-xpe-a-pedale-simple-sans-capot-de-protection-2-entrees-de-cable-pour-presseetoupe-1-iso-m20-1-iso-m16-1-cran-1-contact-o-f-noir?CatalogPath=TRACEPARTS:TP09007004&PartNumber=XPEA110&Product=10-31032006-112260";
    private static final String MODEL_PATH_ENDPOINT = "https://www.traceparts.com/fr/api/v/path?CADDetailLevelID=0&Product=10-31032006-112260&SelectionPath=1%7C1%7C1%7C1%7C&ServiceType=1";

    private static final String HOOK_SCRIPT = """
        (() => {
          if (window.__TPX_HOOKED__) return;
          window.__TPX_HOOKED__ = true;
          let seq = 0;
          const post = o => {
            try {
              if (window.TPNative && typeof window.TPNative.postMessage === 'function') {
                window.TPNative.postMessage(JSON.stringify(o));
              }
            } catch (_) {}
          };
          const armed = () => {
            try { return /(?:^|;\\s*)tp_capture=1(?:;|$)/.test(document.cookie || ''); }
            catch (_) { return false; }
          };
          const looksLikeModel = (url, ct) => {
            if (!armed()) return false;
            const u = String(url || '').toLowerCase();
            const c = String(ct || '').toLowerCase();
            if (u.includes('/api/v/path')) return true;
            if (/\\.(glb|gltf|bin|obj|stl|ply|3mf|dae|fbx|step|stp|iges|igs|scs|scz|s3d|zip)(?:[?#]|$)/i.test(u)) return true;
            if (u.includes('geometry') || u.includes('mesh') || u.includes('manifest') || u.includes('model') || u.includes('stream')) return true;
            if (c.startsWith('model/') || c.includes('gltf') || c.includes('octet-stream') || c.includes('zip') || c.includes('mesh')) return true;
            return false;
          };
          const urlLooksInteresting = url => {
            const u = String(url || '').toLowerCase();
            return u.includes('/api/v/path') ||
              /\\.(glb|gltf|bin|obj|stl|ply|3mf|dae|fbx|step|stp|iges|igs|scs|scz|s3d|zip)(?:[?#]|$)/i.test(u) ||
              u.includes('geometry') || u.includes('mesh') || u.includes('manifest') || u.includes('model') || u.includes('stream');
          };
          const b64 = bytes => {
            let out = '';
            for (let i = 0; i < bytes.length; i++) out += String.fromCharCode(bytes[i]);
            return btoa(out);
          };
          const sendBytes = (id, bytes) => {
            const N = 24576;
            for (let p = 0; p < bytes.length; p += N) {
              post({t:'chunk', id, b64:b64(bytes.subarray(p, Math.min(bytes.length, p + N)))});
            }
          };
          const captureResponse = async (response, requestUrl, source) => {
            try {
              const url = response.url || String(requestUrl || '');
              const ct = response.headers ? (response.headers.get('content-type') || '') : '';
              if (!looksLikeModel(url, ct)) return;
              const id = `${Date.now()}-${++seq}-${Math.random().toString(16).slice(2)}`;
              post({t:'begin', id, url, ct, source, status:response.status || 0});
              let total = 0;
              if (response.body && response.body.getReader) {
                const reader = response.body.getReader();
                while (true) {
                  const r = await reader.read();
                  if (r.done) break;
                  if (r.value && r.value.length) {
                    total += r.value.length;
                    sendBytes(id, r.value);
                  }
                }
              } else {
                const bytes = new Uint8Array(await response.arrayBuffer());
                total = bytes.length;
                sendBytes(id, bytes);
              }
              post({t:'end', id, total});
            } catch (e) {
              post({t:'error', where:'captureResponse', message:String(e)});
            }
          };

          const realFetch = window.fetch.bind(window);
          window.fetch = function(input, init) {
            let requestUrl = '';
            try { requestUrl = typeof input === 'string' ? input : input.url; } catch (_) {}
            if (armed() && String(requestUrl).includes('/api/v/path')) {
              post({t:'request', transport:'fetch', url:String(requestUrl)});
            }
            return realFetch(input, init).then(res => {
              try {
                const ct = res.headers ? (res.headers.get('content-type') || '') : '';
                if (looksLikeModel(res.url || requestUrl, ct)) {
                  const clone = res.clone();
                  Promise.resolve().then(() => captureResponse(clone, requestUrl, 'fetch'));
                }
              } catch (e) { post({t:'error', where:'fetchClone', message:String(e)}); }
              return res;
            });
          };

          const X = window.XMLHttpRequest;
          if (X && X.prototype) {
            const realOpen = X.prototype.open;
            const realSend = X.prototype.send;
            X.prototype.open = function(method, url) {
              this.__tpxUrl = String(url || '');
              this.__tpxMethod = String(method || 'GET');
              return realOpen.apply(this, arguments);
            };
            X.prototype.send = function() {
              if (!this.__tpxInstalled) {
                this.__tpxInstalled = true;
                this.addEventListener('loadend', () => {
                  try {
                    if (!armed()) return;
                    const url = this.responseURL || this.__tpxUrl || '';
                    const ct = this.getResponseHeader('content-type') || '';
                    if (!looksLikeModel(url, ct)) return;
                    const id = `${Date.now()}-${++seq}-xhr`;
                    post({t:'begin', id, url, ct, source:'xhr', status:this.status || 0});
                    const finish = bytesLike => {
                      try {
                        const bytes = bytesLike instanceof Uint8Array ? bytesLike : new Uint8Array(bytesLike);
                        sendBytes(id, bytes);
                        post({t:'end', id, total:bytes.length});
                      } catch (e) { post({t:'error', where:'xhrFinish', message:String(e)}); }
                    };
                    const r = this.response;
                    if (r instanceof ArrayBuffer) finish(r);
                    else if (typeof Blob !== 'undefined' && r instanceof Blob) r.arrayBuffer().then(finish);
                    else if (typeof r === 'string') finish(new TextEncoder().encode(r));
                    else if (r != null) finish(new TextEncoder().encode(JSON.stringify(r)));
                    else finish(new Uint8Array(0));
                  } catch (e) { post({t:'error', where:'xhrCapture', message:String(e)}); }
                });
              }
              if (armed() && String(this.__tpxUrl || '').includes('/api/v/path')) {
                post({t:'request', transport:'xhr', url:this.__tpxUrl || ''});
              }
              return realSend.apply(this, arguments);
            };
          }

          window.__tpxFetchUrl = async url => {
            try {
              const res = await realFetch(url, {credentials:'include', cache:'no-store'});
              await captureResponse(res, url, 'forced-fetch');
              return res.status;
            } catch (e) {
              post({t:'error', where:'forcedFetch', message:String(e), url:String(url)});
              return -1;
            }
          };
          window.__tpxRecaptureResources = () => {
            try {
              const urls = [...new Set(performance.getEntriesByType('resource').map(e => e.name).filter(urlLooksInteresting))].slice(0, 150);
              post({t:'note', message:`performance candidates=${urls.length}`});
              urls.forEach((u, i) => setTimeout(() => window.__tpxFetchUrl(u), i * 100));
              return urls.length;
            } catch (e) {
              post({t:'error', where:'performance', message:String(e)});
              return -1;
            }
          };
          post({t:'note', message:'capture hook installed', href:String(location.href)});
        })();
        """;

    private WebView webView;
    private EditText address;
    private Button captureButton;
    private TextView status;
    private final StringBuilder visibleLog = new StringBuilder();
    private CaptureStore store;
    private boolean captureActive;
    private boolean documentStartSupported;
    private String runName = "";

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        store = new CaptureStore();
        makeUi();
        configureWebView();
        address.setText(TARGET_URL);
        webView.loadUrl(TARGET_URL);
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
        Button go = button("Go");
        go.setOnClickListener(v -> openAddress());
        top.addView(go, new LinearLayout.LayoutParams(dp(64), dp(44)));
        root.addView(top);

        LinearLayout controls = new LinearLayout(this);
        controls.setOrientation(LinearLayout.HORIZONTAL);
        controls.setGravity(Gravity.CENTER_VERTICAL);
        controls.setPadding(dp(5), 0, dp(5), 0);
        Button back = button("Back");
        back.setOnClickListener(v -> { if (webView.canGoBack()) webView.goBack(); });
        controls.addView(back, new LinearLayout.LayoutParams(0, dp(44), 1f));
        Button reload = button("Reload");
        reload.setOnClickListener(v -> webView.reload());
        controls.addView(reload, new LinearLayout.LayoutParams(0, dp(44), 1f));
        captureButton = button("Extract 3D");
        captureButton.setOnClickListener(v -> { if (captureActive) stopCapture(); else startCapture(); });
        controls.addView(captureButton, new LinearLayout.LayoutParams(0, dp(44), 1.35f));
        Button files = button("Files");
        files.setOnClickListener(v -> openDownloads());
        controls.addView(files, new LinearLayout.LayoutParams(0, dp(44), .8f));
        root.addView(controls);

        webView = new WebView(this);
        root.addView(webView, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        ScrollView sv = new ScrollView(this);
        status = new TextView(this);
        status.setTextSize(10.5f);
        status.setTextColor(Color.DKGRAY);
        status.setPadding(dp(7), dp(4), dp(7), dp(5));
        sv.addView(status);
        root.addView(sv, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(112)));
        setContentView(root);
        logUi("Ready. Open Preview if needed, then press Extract 3D.");
    }

    private Button button(String text) {
        Button b = new Button(this);
        b.setText(text);
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
        s.setBuiltInZoomControls(true);
        s.setDisplayZoomControls(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setMediaPlaybackRequiresUserGesture(false);
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
            logUi("ERROR: Android System WebView is too old for the capture bridge.");
        }

        if (WebViewFeature.isFeatureSupported(WebViewFeature.DOCUMENT_START_SCRIPT)) {
            WebViewCompat.addDocumentStartJavaScript(webView, HOOK_SCRIPT, origins);
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
                if (!documentStartSupported && url != null && url.contains("traceparts.com")) {
                    view.evaluateJavascript(HOOK_SCRIPT, null);
                }
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                address.setText(url);
                logUi("Loaded: " + shortUrl(url));
                if (captureActive && url != null && url.contains("traceparts.com")) {
                    view.postDelayed(() -> probe(), 1200);
                    view.postDelayed(() -> recapture(), 4200);
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

    private void startCapture() {
        String u = webView.getUrl();
        if (u == null || !u.contains("traceparts.com")) {
            logUi("Open the TraceParts page first.");
            return;
        }
        captureActive = true;
        runName = "XPEA110_" + new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(new Date());
        store.start(runName);
        captureButton.setText("Stop");
        logUi("Capture armed. Reloading so initial model traffic is captured.");
        webView.evaluateJavascript("document.cookie='tp_capture=1; path=/; domain=.traceparts.com; SameSite=Lax'; true;", ignored -> webView.reload());
    }

    private void stopCapture() {
        captureActive = false;
        captureButton.setText("Extract 3D");
        webView.evaluateJavascript("document.cookie='tp_capture=; Max-Age=0; path=/; domain=.traceparts.com; SameSite=Lax'; true;", null);
        store.finish();
        logUi("Stopped. Files: Downloads/TracePartsExtractor/" + runName);
    }

    private void probe() {
        if (!captureActive) return;
        String ep = JSONObject.quote(MODEL_PATH_ENDPOINT);
        String js = "(() => {try {const es=[...document.querySelectorAll('button,a,[role=tab],[role=button]')];" +
                "const h=es.find(e=>/(preview|aperçu|3d)/i.test((e.innerText||e.textContent||e.getAttribute('aria-label')||'').trim()));" +
                "if(h){try{h.scrollIntoView({block:'center'})}catch(_){};try{h.click()}catch(_){}}" +
                "if(window.__tpxFetchUrl)setTimeout(()=>window.__tpxFetchUrl(" + ep + "),500);" +
                "return h?'preview-clicked':'preview-not-found';}catch(e){return 'probe-error:'+e}})();";
        webView.evaluateJavascript(js, value -> logUi("Probe: " + value));
    }

    private void recapture() {
        if (!captureActive) return;
        webView.evaluateJavascript("window.__tpxRecaptureResources ? window.__tpxRecaptureResources() : -1;",
                value -> logUi("Resource candidates: " + value));
    }

    private void receive(String data) {
        try {
            JSONObject o = new JSONObject(data);
            String t = o.optString("t", "");
            if ("begin".equals(t)) {
                store.begin(o.optString("id"), o.optString("url"), o.optString("ct"), o.optString("source"), o.optInt("status"));
            } else if ("chunk".equals(t)) {
                store.chunk(o.optString("id"), o.optString("b64"));
            } else if ("end".equals(t)) {
                store.end(o.optString("id"), o.optLong("total", -1));
            } else if ("request".equals(t)) {
                store.log("REQUEST " + o.optString("transport") + " " + o.optString("url") + "\n");
                logUi("Observed /api/v/path request");
            } else if ("note".equals(t)) {
                String m = o.optString("message");
                store.log("NOTE " + m + "\n");
                logUi(m);
            } else if ("error".equals(t)) {
                String m = "JS ERROR " + o.optString("where") + ": " + o.optString("message");
                store.log(m + "\n");
                logUi(m);
            }
        } catch (Exception e) {
            logUi("Bridge parse error: " + e.getMessage());
        }
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

    private int dp(int n) { return Math.round(n * getResources().getDisplayMetrics().density); }

    private String shortUrl(String u) {
        if (u == null) return "";
        return u.length() <= 105 ? u : u.substring(0, 102) + "...";
    }

    private void logUi(String line) {
        runOnUiThread(() -> {
            if (visibleLog.length() > 12000) visibleLog.delete(0, Math.min(5000, visibleLog.length()));
            visibleLog.append(new SimpleDateFormat("HH:mm:ss", Locale.US).format(new Date()))
                    .append("  ").append(line).append('\n');
            status.setText(visibleLog.toString());
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
                        write("TraceParts Preview Extractor v1.0.0\nTarget=" + TARGET_URL + "\nKnownEndpoint=" + MODEL_PATH_ENDPOINT + "\n\n");
                    }
                } catch (Exception e) { logUi("Log create failed: " + e.getMessage()); }
            });
        }

        void begin(String id, String url, String ct, String source, int httpStatus) {
            if (id == null || id.length() == 0) return;
            io.execute(() -> {
                try {
                    File d = new File(getCacheDir(), "tpx");
                    if (!d.exists() && !d.mkdirs()) throw new IOException("cache mkdir failed");
                    File f = new File(d, safe(id) + ".part");
                    Item item = new Item(id, url, ct, source, httpStatus, f, new FileOutputStream(f));
                    items.put(id, item);
                    write("BEGIN status=" + httpStatus + " source=" + source + " ct=" + ct + " url=" + url + "\n");
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
            this.id = id; this.url = url; this.ct = ct; this.source = source; this.status = status; this.temp = temp; this.out = out;
        }
    }
}
