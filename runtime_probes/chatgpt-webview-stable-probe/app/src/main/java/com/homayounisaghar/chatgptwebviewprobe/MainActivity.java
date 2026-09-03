package com.homayounisaghar.chatgptwebviewprobe;

import android.app.Activity;
import android.content.ContentValues;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.MediaStore;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Space;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.regex.Pattern;

public class MainActivity extends Activity {
    private static final Pattern UUID_PATTERN = Pattern.compile(
            "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$");

    private WebView webView;
    private TextView statusView;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final StringBuilder routeLog = new StringBuilder();
    private String lastUrl = "";
    private String latestDom = "DOM: waiting";
    private String latestStreamState = "UNKNOWN";
    private long probeSequence = 0;

    private String verifyPhase = "IDLE";
    private String verifyStatus = "NOT_RUN";
    private String verifyExpectedCid = "-";
    private String verifyExpectedUserHash = "-";
    private int verifyExpectedUserCount = -1;
    private String verifyActualUserHash = "-";
    private int verifyActualUserCount = -1;
    private long verifyStartedAt = 0L;
    private boolean verifyProbeInFlight = false;

    private String receiptPhase = "IDLE";
    private String receiptStatus = "NOT_RUN";
    private String receiptCid = "-";
    private int receiptBaselineUserCount = -1;
    private String receiptBaselineUserHash = "-";
    private int receiptBaselineAssistantCount = -1;
    private String receiptBaselineAssistantHash = "-";
    private int receiptFinalUserCount = -1;
    private String receiptFinalUserHash = "-";
    private int receiptFinalAssistantCount = -1;
    private String receiptFinalAssistantHash = "-";
    private String receiptLastAssistantHash = "-";
    private int receiptLastAssistantCount = -1;
    private int receiptStableSamples = 0;
    private boolean receiptSawUiStreaming = false;
    private boolean receiptSawAssistantEvolution = false;
    private long receiptStartedAt = 0L;

    private final Runnable probeRunnable = new Runnable() {
        @Override public void run() {
            probeOnce();
            handler.postDelayed(this, 500L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getWindow().setStatusBarColor(Color.WHITE);
        getWindow().setNavigationBarColor(Color.WHITE);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);

        CookieManager cookieManager = CookieManager.getInstance();
        cookieManager.setAcceptCookie(true);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setFitsSystemWindows(true);

        Space topGap = new Space(this);
        root.addView(topGap, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(8)));

        LinearLayout actions1 = new LinearLayout(this);
        actions1.setOrientation(LinearLayout.HORIZONTAL);

        Button home = new Button(this);
        home.setText("CHATGPT");
        home.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                webView.loadUrl("https://chatgpt.com/");
            }
        });
        actions1.addView(home, new LinearLayout.LayoutParams(0, dp(46), 1f));

        Button verify = new Button(this);
        verify.setText("VERIFY");
        verify.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                beginReopenVerification();
            }
        });
        actions1.addView(verify, new LinearLayout.LayoutParams(0, dp(46), 1f));

        Button watch = new Button(this);
        watch.setText("WATCH");
        watch.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                beginResponseReceiptWatch();
            }
        });
        actions1.addView(watch, new LinearLayout.LayoutParams(0, dp(46), 1f));
        root.addView(actions1, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(46)));

        LinearLayout actions2 = new LinearLayout(this);
        actions2.setOrientation(LinearLayout.HORIZONTAL);

        Button download = new Button(this);
        download.setText("DOWNLOAD");
        download.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                downloadReport();
            }
        });
        actions2.addView(download, new LinearLayout.LayoutParams(0, dp(46), 1f));

        Button reload = new Button(this);
        reload.setText("RELOAD");
        reload.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                webView.reload();
            }
        });
        actions2.addView(reload, new LinearLayout.LayoutParams(0, dp(46), 1f));
        root.addView(actions2, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(46)));

        statusView = new TextView(this);
        statusView.setTextSize(11f);
        statusView.setTextIsSelectable(true);
        statusView.setPadding(dp(8), dp(6), dp(8), dp(6));
        statusView.setText("WebView Probe Stable v0.5\nWATCH observes a manual normal turn and produces a hash-only response receipt. No automated Send.");

        ScrollView statusScroll = new ScrollView(this);
        statusScroll.addView(statusView, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT,
                ScrollView.LayoutParams.WRAP_CONTENT));
        root.addView(statusScroll, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(205)));

        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setLoadWithOverviewMode(false);
        settings.setUseWideViewPort(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(true);
        cookieManager.setAcceptThirdPartyCookies(webView, true);

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override public void onPageStarted(WebView view, String url, Bitmap favicon) {
                recordRoute("PAGE_START", url);
                super.onPageStarted(view, url, favicon);
            }

            @Override public void onPageFinished(WebView view, String url) {
                recordRoute("PAGE_FINISH", url);
                CookieManager.getInstance().flush();
                driveVerification(url);
                super.onPageFinished(view, url);
            }
        });

        root.addView(webView, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));
        setContentView(root);

        webView.loadUrl("https://chatgpt.com/");
        handler.post(probeRunnable);
    }

    private void probeOnce() {
        if (webView == null) return;
        final String nativeUrl = safe(webView.getUrl());
        if (!nativeUrl.equals(lastUrl)) {
            lastUrl = nativeUrl;
            recordRoute("URL_CHANGE", nativeUrl);
        }

        if (!"IDLE".equals(verifyPhase) && verifyStartedAt > 0L
                && System.currentTimeMillis() - verifyStartedAt > 20000L) {
            failVerification("FAIL_TIMEOUT");
        }

        if (!"IDLE".equals(receiptPhase) && receiptStartedAt > 0L
                && System.currentTimeMillis() - receiptStartedAt > 300000L) {
            failReceipt("FAIL_TIMEOUT");
        }

        driveVerification(nativeUrl);

        final long seq = ++probeSequence;
        webView.evaluateJavascript(snapshotJs(), new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                if (seq < probeSequence - 3) return;
                try {
                    DomSnapshot snapshot = parseSnapshot(value);
                    latestDom = snapshot.summary;
                    latestStreamState = snapshot.streamState;
                    driveResponseReceipt(snapshot, nativeUrl);
                } catch (Exception e) {
                    latestDom = "DOM_PARSE_ERROR: " + e.getClass().getSimpleName();
                    latestStreamState = "UNKNOWN";
                }
                renderStatus(nativeUrl);
            }
        });
    }

    private String snapshotJs() {
        return "(function(){try{"
                + "const qa=(s)=>Array.from(document.querySelectorAll(s));"
                + "const vis=(e)=>{const r=e.getBoundingClientRect();const st=getComputedStyle(e);return r.width>0&&r.height>0&&st.visibility!=='hidden'&&st.display!=='none';};"
                + "const norm=(x)=>(x||'').replace(/\\s+/g,' ').trim();"
                + "const label=(e)=>norm(e.getAttribute('aria-label')||e.innerText||e.textContent||'');"
                + "const labels=qa('button,[role=\\\"button\\\"],[aria-label]').filter(vis).map(label).filter(Boolean).slice(0,24);"
                + "const controls=qa('button,[role=\\\"button\\\"]').filter(vis);"
                + "const stopControls=controls.filter(e=>{const x=(label(e)+' '+(e.getAttribute('data-testid')||'')).toLowerCase();return x.includes('stop generating')||x.includes('stop response')||x.includes('stop-generating')||x==='stop';}).length;"
                + "const busyNodes=qa('[aria-busy=\\\"true\\\"]').filter(vis).length;"
                + "const responseActions=qa('[aria-label=\\\"Response actions\\\" i]').filter(vis).length;"
                + "const users=qa('[data-message-author-role=\\\"user\\\"]').map(e=>norm(e.innerText||e.textContent)).filter(Boolean);"
                + "const assistants=qa('[data-message-author-role=\\\"assistant\\\"]').map(e=>norm(e.innerText||e.textContent)).filter(Boolean);"
                + "const o={href:location.href,title:document.title,ready:document.readyState,"
                + "editables:qa('textarea,[contenteditable=\\\"true\\\"]').filter(vis).length,"
                + "buttons:qa('button').filter(vis).length,roleButtons:qa('[role=\\\"button\\\"]').filter(vis).length,"
                + "links:qa('a').filter(vis).length,articles:qa('article').length,mains:qa('main').length,"
                + "conversationTurns:qa('[data-testid*=\\\"conversation-turn\\\"]').length,composerHints:qa('[data-testid*=\\\"composer\\\"],[aria-label*=\\\"Message\\\" i],[placeholder*=\\\"Message\\\" i]').length,"
                + "stopControls:stopControls,busyNodes:busyNodes,responseActions:responseActions,users:users,assistants:assistants,labels:labels};"
                + "return JSON.stringify(o);}catch(e){return JSON.stringify({error:String(e),href:String(location.href),users:[],assistants:[]});}})();";
    }

    private DomSnapshot parseSnapshot(String value) throws Exception {
        Object outer = new JSONTokener(value).nextValue();
        String json = outer instanceof String ? (String) outer : String.valueOf(outer);
        JSONObject o = new JSONObject(json);

        Fingerprint users = fingerprintArray(o.optJSONArray("users"));
        Fingerprint assistants = fingerprintArray(o.optJSONArray("assistants"));
        int stopControls = o.optInt("stopControls", -1);
        int busyNodes = o.optInt("busyNodes", -1);
        int responseActions = o.optInt("responseActions", -1);
        String streamState = (stopControls > 0 || busyNodes > 0)
                ? "STREAMING_HINT" : (assistants.count > 0 ? "COMPLETE_CANDIDATE" : "NONE");

        StringBuilder s = new StringBuilder();
        s.append("TITLE: ").append(o.optString("title", "-")).append('\n');
        s.append("READY: ").append(o.optString("ready", "-")).append('\n');
        s.append("DOM: editables=").append(o.optInt("editables", -1));
        s.append(" buttons=").append(o.optInt("buttons", -1));
        s.append(" roleButtons=").append(o.optInt("roleButtons", -1));
        s.append(" links=").append(o.optInt("links", -1));
        s.append(" articles=").append(o.optInt("articles", -1));
        s.append(" main=").append(o.optInt("mains", -1)).append('\n');
        s.append("CHAT_HINTS: user=").append(users.count);
        s.append(" assistant=").append(assistants.count);
        s.append(" turns=").append(o.optInt("conversationTurns", -1));
        s.append(" composer=").append(o.optInt("composerHints", -1)).append('\n');
        s.append("STREAM_HINTS: stopControls=").append(stopControls);
        s.append(" busyNodes=").append(busyNodes);
        s.append(" responseActions=").append(responseActions);
        s.append(" state=").append(streamState).append('\n');
        if (o.has("labels")) s.append("VISIBLE_LABELS: ").append(o.optJSONArray("labels")).append('\n');
        if (o.has("error")) s.append("JS_ERROR: ").append(o.optString("error"));

        return new DomSnapshot(users, assistants, stopControls, busyNodes,
                responseActions, streamState, s.toString().trim());
    }

    private Fingerprint fingerprintArray(JSONArray array) throws Exception {
        if (array == null || array.length() == 0) return new Fingerprint(0, "-");
        StringBuilder joined = new StringBuilder();
        int count = 0;
        for (int i = 0; i < array.length(); i++) {
            String text = normalize(array.optString(i, ""));
            if (text.isEmpty()) continue;
            if (count > 0) joined.append('\u001e');
            joined.append(text);
            count++;
        }
        if (count == 0) return new Fingerprint(0, "-");
        return new Fingerprint(count, sha256(joined.toString()));
    }

    private String fingerprintJs() {
        return "(function(){try{"
                + "const norm=(x)=>(x||'').replace(/\\s+/g,' ').trim();"
                + "const users=Array.from(document.querySelectorAll('[data-message-author-role=\\\"user\\\"]')).map(e=>norm(e.innerText||e.textContent)).filter(Boolean);"
                + "return JSON.stringify({href:location.href,users:users});"
                + "}catch(e){return JSON.stringify({error:String(e),href:String(location.href),users:[]});}})();";
    }

    private Fingerprint parseUserFingerprint(String value) throws Exception {
        Object outer = new JSONTokener(value).nextValue();
        String json = outer instanceof String ? (String) outer : String.valueOf(outer);
        JSONObject o = new JSONObject(json);
        return fingerprintArray(o.optJSONArray("users"));
    }

    private void beginReopenVerification() {
        if (webView == null) return;
        if (!"IDLE".equals(verifyPhase)) {
            Toast.makeText(this, "Verification already running", Toast.LENGTH_SHORT).show();
            return;
        }
        if (!"IDLE".equals(receiptPhase)) {
            Toast.makeText(this, "Finish WATCH before VERIFY", Toast.LENGTH_SHORT).show();
            return;
        }

        final String current = sanitizeUrl(webView.getUrl());
        final String canonical = extractCanonicalConversationId(current);
        if ("-".equals(canonical)) {
            verifyStatus = "FAIL_NO_CANONICAL_CHAT";
            renderStatus(webView.getUrl());
            Toast.makeText(this, "Open a normal saved conversation first", Toast.LENGTH_LONG).show();
            return;
        }

        verifyStatus = "CAPTURING";
        verifyPhase = "CAPTURING";
        verifyStartedAt = System.currentTimeMillis();
        verifyExpectedCid = canonical;
        verifyExpectedUserHash = "-";
        verifyExpectedUserCount = -1;
        verifyActualUserHash = "-";
        verifyActualUserCount = -1;

        webView.evaluateJavascript(fingerprintJs(), new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                try {
                    Fingerprint fp = parseUserFingerprint(value);
                    if (fp.count <= 0 || "-".equals(fp.hash)) {
                        failVerification("FAIL_NO_USER_MESSAGE");
                        return;
                    }
                    verifyExpectedUserHash = fp.hash;
                    verifyExpectedUserCount = fp.count;
                    verifyStatus = "CAPTURED_NAVIGATING_HOME";
                    verifyPhase = "WAIT_HOME";
                    recordRoute("VERIFY_CAPTURE", current);
                    webView.loadUrl("https://chatgpt.com/");
                } catch (Exception e) {
                    failVerification("FAIL_CAPTURE_PARSE");
                }
            }
        });
    }

    private void driveVerification(String rawUrl) {
        if (webView == null || "IDLE".equals(verifyPhase)) return;
        String sanitized = sanitizeUrl(rawUrl);
        String canonical = extractCanonicalConversationId(sanitized);

        if ("WAIT_HOME".equals(verifyPhase) && isHomeUrl(sanitized)) {
            verifyPhase = "REOPENING";
            verifyStatus = "REOPENING";
            final String target = "https://chatgpt.com/c/" + verifyExpectedCid;
            handler.postDelayed(new Runnable() {
                @Override public void run() {
                    if ("REOPENING".equals(verifyPhase) && webView != null) webView.loadUrl(target);
                }
            }, 250L);
            return;
        }

        if (("REOPENING".equals(verifyPhase) || "VERIFYING".equals(verifyPhase))
                && verifyExpectedCid.equals(canonical) && !verifyProbeInFlight) {
            verifyPhase = "VERIFYING";
            verifyStatus = "VERIFYING_REOPENED_DOM";
            scheduleReopenFingerprintAttempt(500L);
        }
    }

    private void scheduleReopenFingerprintAttempt(long delayMs) {
        if (verifyProbeInFlight || "IDLE".equals(verifyPhase)) return;
        verifyProbeInFlight = true;
        handler.postDelayed(new Runnable() {
            @Override public void run() {
                attemptReopenedFingerprint();
            }
        }, delayMs);
    }

    private void attemptReopenedFingerprint() {
        if (webView == null || "IDLE".equals(verifyPhase)) {
            verifyProbeInFlight = false;
            return;
        }
        final String canonicalNow = extractCanonicalConversationId(sanitizeUrl(webView.getUrl()));
        webView.evaluateJavascript(fingerprintJs(), new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                verifyProbeInFlight = false;
                try {
                    Fingerprint fp = parseUserFingerprint(value);
                    verifyActualUserCount = fp.count;
                    verifyActualUserHash = fp.hash;
                    if (!verifyExpectedCid.equals(canonicalNow)) {
                        failVerification("FAIL_CANONICAL_ID_MISMATCH");
                        return;
                    }
                    if (verifyExpectedUserCount == fp.count && verifyExpectedUserHash.equals(fp.hash)) {
                        verifyStatus = "PASS";
                        verifyPhase = "IDLE";
                        recordRoute("VERIFY_PASS", webView.getUrl());
                        Toast.makeText(MainActivity.this, "Reopen guard PASS", Toast.LENGTH_LONG).show();
                    } else if (System.currentTimeMillis() - verifyStartedAt < 18000L) {
                        verifyStatus = "WAITING_REOPENED_DOM";
                        scheduleReopenFingerprintAttempt(600L);
                    } else {
                        failVerification("FAIL_FINGERPRINT_MISMATCH");
                    }
                } catch (Exception e) {
                    if (System.currentTimeMillis() - verifyStartedAt < 18000L) {
                        scheduleReopenFingerprintAttempt(600L);
                    } else {
                        failVerification("FAIL_REOPEN_PARSE");
                    }
                }
                renderStatus(webView == null ? "-" : webView.getUrl());
            }
        });
    }

    private void failVerification(String status) {
        verifyStatus = status;
        verifyPhase = "IDLE";
        verifyProbeInFlight = false;
        recordRoute("VERIFY_FAIL_" + status, webView == null ? "-" : webView.getUrl());
        renderStatus(webView == null ? "-" : webView.getUrl());
    }

    private void beginResponseReceiptWatch() {
        if (webView == null) return;
        if (!"IDLE".equals(receiptPhase)) {
            Toast.makeText(this, "WATCH already running", Toast.LENGTH_SHORT).show();
            return;
        }
        if (!"IDLE".equals(verifyPhase)) {
            Toast.makeText(this, "Finish VERIFY before WATCH", Toast.LENGTH_SHORT).show();
            return;
        }

        final String canonical = extractCanonicalConversationId(sanitizeUrl(webView.getUrl()));
        if ("-".equals(canonical)) {
            receiptStatus = "FAIL_NO_CANONICAL_CHAT";
            renderStatus(webView.getUrl());
            Toast.makeText(this, "Open a normal saved conversation first", Toast.LENGTH_LONG).show();
            return;
        }

        receiptStatus = "CAPTURING_BASELINE";
        receiptPhase = "CAPTURING";
        receiptCid = canonical;
        receiptStartedAt = System.currentTimeMillis();
        receiptStableSamples = 0;
        receiptSawUiStreaming = false;
        receiptSawAssistantEvolution = false;
        receiptFinalUserCount = -1;
        receiptFinalUserHash = "-";
        receiptFinalAssistantCount = -1;
        receiptFinalAssistantHash = "-";
        receiptLastAssistantCount = -1;
        receiptLastAssistantHash = "-";

        webView.evaluateJavascript(snapshotJs(), new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                try {
                    DomSnapshot s = parseSnapshot(value);
                    receiptBaselineUserCount = s.users.count;
                    receiptBaselineUserHash = s.users.hash;
                    receiptBaselineAssistantCount = s.assistants.count;
                    receiptBaselineAssistantHash = s.assistants.hash;
                    receiptPhase = "WAIT_USER_CHANGE";
                    receiptStatus = "ARMED_WAIT_USER_CHANGE";
                    recordRoute("RECEIPT_ARMED", webView.getUrl());
                    Toast.makeText(MainActivity.this,
                            "WATCH armed. Send one normal message manually.", Toast.LENGTH_LONG).show();
                } catch (Exception e) {
                    failReceipt("FAIL_BASELINE_PARSE");
                }
                renderStatus(webView == null ? "-" : webView.getUrl());
            }
        });
    }

    private void driveResponseReceipt(DomSnapshot s, String rawUrl) {
        if ("IDLE".equals(receiptPhase) || "CAPTURING".equals(receiptPhase)) return;
        String canonical = extractCanonicalConversationId(sanitizeUrl(rawUrl));
        if (!receiptCid.equals(canonical)) {
            failReceipt("FAIL_ROUTE_CHANGED");
            return;
        }

        boolean uiStreaming = s.stopControls > 0 || s.busyNodes > 0;
        if (uiStreaming) receiptSawUiStreaming = true;

        if ("WAIT_USER_CHANGE".equals(receiptPhase)) {
            boolean userChanged = s.users.count > receiptBaselineUserCount
                    || !safeEq(s.users.hash, receiptBaselineUserHash);
            if (userChanged) {
                receiptPhase = "WAIT_ASSISTANT_CHANGE";
                receiptStatus = "USER_CHANGE_SEEN";
                receiptFinalUserCount = s.users.count;
                receiptFinalUserHash = s.users.hash;
                recordRoute("RECEIPT_USER_CHANGE", rawUrl);
            }
            return;
        }

        if ("WAIT_ASSISTANT_CHANGE".equals(receiptPhase)) {
            boolean assistantChanged = s.assistants.count > receiptBaselineAssistantCount
                    || !safeEq(s.assistants.hash, receiptBaselineAssistantHash);
            if (assistantChanged && s.assistants.count > 0 && !"-".equals(s.assistants.hash)) {
                receiptPhase = "OBSERVING";
                receiptStatus = uiStreaming ? "STREAMING_ACTIVE" : "ASSISTANT_CHANGE_SEEN";
                receiptLastAssistantCount = s.assistants.count;
                receiptLastAssistantHash = s.assistants.hash;
                receiptFinalAssistantCount = s.assistants.count;
                receiptFinalAssistantHash = s.assistants.hash;
                receiptStableSamples = 0;
                recordRoute("RECEIPT_ASSISTANT_CHANGE", rawUrl);
            }
            return;
        }

        if (!"OBSERVING".equals(receiptPhase)) return;

        boolean assistantChangedAgain = s.assistants.count != receiptLastAssistantCount
                || !safeEq(s.assistants.hash, receiptLastAssistantHash);
        if (assistantChangedAgain) {
            if (!"-".equals(receiptLastAssistantHash)) receiptSawAssistantEvolution = true;
            receiptLastAssistantCount = s.assistants.count;
            receiptLastAssistantHash = s.assistants.hash;
            receiptFinalAssistantCount = s.assistants.count;
            receiptFinalAssistantHash = s.assistants.hash;
            receiptStableSamples = 0;
            receiptStatus = uiStreaming ? "STREAMING_ACTIVE" : "ASSISTANT_EVOLVING";
            return;
        }

        if (uiStreaming) {
            receiptStableSamples = 0;
            receiptStatus = "STREAMING_ACTIVE";
            return;
        }

        boolean hasNewAssistant = s.assistants.count > receiptBaselineAssistantCount
                && !safeEq(s.assistants.hash, receiptBaselineAssistantHash)
                && !"-".equals(s.assistants.hash);
        if (hasNewAssistant && s.responseActions > 0) {
            receiptStableSamples++;
            receiptFinalAssistantCount = s.assistants.count;
            receiptFinalAssistantHash = s.assistants.hash;
            receiptFinalUserCount = s.users.count;
            receiptFinalUserHash = s.users.hash;
            receiptStatus = "STABILIZING_" + receiptStableSamples;
            if (receiptStableSamples >= 4) {
                boolean streamingObserved = receiptSawUiStreaming || receiptSawAssistantEvolution;
                receiptStatus = streamingObserved ? "COMPLETE" : "COMPLETE_NO_STREAMING_OBSERVED";
                receiptPhase = "IDLE";
                recordRoute(streamingObserved ? "RECEIPT_COMPLETE" : "RECEIPT_COMPLETE_NO_STREAM",
                        rawUrl);
                Toast.makeText(this, "Response receipt: " + receiptStatus, Toast.LENGTH_LONG).show();
            }
        } else {
            receiptStableSamples = 0;
            receiptStatus = "WAITING_COMPLETE_EVIDENCE";
        }
    }

    private void failReceipt(String status) {
        receiptStatus = status;
        receiptPhase = "IDLE";
        recordRoute("RECEIPT_FAIL_" + status, webView == null ? "-" : webView.getUrl());
        renderStatus(webView == null ? "-" : webView.getUrl());
    }

    private void renderStatus(String rawUrl) {
        String sanitized = sanitizeUrl(rawUrl);
        String canonical = extractCanonicalConversationId(sanitized);
        String routeSegment = extractRouteSegment(sanitized);
        String bindingState = !"-".equals(canonical) ? "CANONICAL_UUID"
                : (routeSegment.startsWith("WEB:") ? "TRANSIENT_WEB_ID" : "NONE");

        StringBuilder s = new StringBuilder();
        s.append("WebView Probe Stable v0.5 — READ SIDE ONLY\n");
        s.append("URL: ").append(sanitized).append('\n');
        s.append("BINDING_STATE: ").append(bindingState).append('\n');
        s.append("CONVERSATION_ID: ").append(canonical).append('\n');
        s.append("REOPEN_GUARD: ").append(verifyStatus).append('\n');
        s.append("RESPONSE_RECEIPT: ").append(receiptStatus).append('\n');
        s.append("STREAM_STATE: ").append(latestStreamState).append('\n');
        s.append(latestDom).append('\n');
        s.append("ROUTE_EVENTS: ").append(countRouteEvents()).append(" (DOWNLOAD for sanitized report)");
        statusView.setText(s.toString());
    }

    private void recordRoute(String kind, String rawUrl) {
        String u = sanitizeUrl(rawUrl);
        String canonical = extractCanonicalConversationId(u);
        String segment = extractRouteSegment(u);
        String cid = !"-".equals(canonical) ? canonical : (segment.startsWith("WEB:") ? "TRANSIENT" : "-");
        routeLog.append(kind).append(" | ").append(u).append(" | cid=").append(cid).append('\n');
        if (routeLog.length() > 16000) routeLog.delete(0, 5000);
    }

    private String sanitizeUrl(String rawUrl) {
        if (rawUrl == null || rawUrl.trim().isEmpty()) return "-";
        try {
            Uri uri = Uri.parse(rawUrl);
            String scheme = uri.getScheme();
            String host = uri.getHost();
            String path = uri.getEncodedPath();
            if (scheme == null || host == null) {
                int q = rawUrl.indexOf('?');
                int h = rawUrl.indexOf('#');
                int end = rawUrl.length();
                if (q >= 0) end = Math.min(end, q);
                if (h >= 0) end = Math.min(end, h);
                return rawUrl.substring(0, end);
            }
            return scheme + "://" + host + (path == null || path.isEmpty() ? "/" : path);
        } catch (Exception e) {
            return "-";
        }
    }

    private String extractRouteSegment(String url) {
        if (url == null) return "-";
        int marker = url.indexOf("/c/");
        if (marker < 0) return "-";
        int start = marker + 3;
        int end = url.length();
        int slash = url.indexOf('/', start);
        if (slash >= 0) end = slash;
        if (end <= start) return "-";
        return url.substring(start, end);
    }

    private String extractCanonicalConversationId(String url) {
        String segment = extractRouteSegment(url);
        return UUID_PATTERN.matcher(segment).matches() ? segment : "-";
    }

    private boolean isHomeUrl(String url) {
        if (url == null) return false;
        try {
            Uri uri = Uri.parse(url);
            return "chatgpt.com".equalsIgnoreCase(uri.getHost())
                    && (uri.getPath() == null || "/".equals(uri.getPath()) || uri.getPath().isEmpty());
        } catch (Exception e) {
            return false;
        }
    }

    private int countRouteEvents() {
        int count = 0;
        for (int i = 0; i < routeLog.length(); i++) {
            if (routeLog.charAt(i) == '\n') count++;
        }
        return count;
    }

    private String buildReport() {
        String current = sanitizeUrl(webView == null ? null : webView.getUrl());
        String canonical = extractCanonicalConversationId(current);
        return "CHATGPT_WEBVIEW_OBSERVABILITY_STABLE_V05\n"
                + "CURRENT_URL=" + current + "\n"
                + "CURRENT_CONVERSATION_ID=" + canonical + "\n"
                + "REOPEN_GUARD_STATUS=" + verifyStatus + "\n"
                + "REOPEN_EXPECTED_USER_COUNT=" + verifyExpectedUserCount + "\n"
                + "REOPEN_ACTUAL_USER_COUNT=" + verifyActualUserCount + "\n"
                + "REOPEN_EXPECTED_USER_SHA256=" + verifyExpectedUserHash + "\n"
                + "REOPEN_ACTUAL_USER_SHA256=" + verifyActualUserHash + "\n"
                + "RESPONSE_RECEIPT_STATUS=" + receiptStatus + "\n"
                + "RECEIPT_BASELINE_USER_COUNT=" + receiptBaselineUserCount + "\n"
                + "RECEIPT_BASELINE_USER_SHA256=" + receiptBaselineUserHash + "\n"
                + "RECEIPT_BASELINE_ASSISTANT_COUNT=" + receiptBaselineAssistantCount + "\n"
                + "RECEIPT_BASELINE_ASSISTANT_SHA256=" + receiptBaselineAssistantHash + "\n"
                + "RECEIPT_FINAL_USER_COUNT=" + receiptFinalUserCount + "\n"
                + "RECEIPT_FINAL_USER_SHA256=" + receiptFinalUserHash + "\n"
                + "RECEIPT_FINAL_ASSISTANT_COUNT=" + receiptFinalAssistantCount + "\n"
                + "RECEIPT_FINAL_ASSISTANT_SHA256=" + receiptFinalAssistantHash + "\n"
                + "RECEIPT_SAW_UI_STREAMING=" + receiptSawUiStreaming + "\n"
                + "RECEIPT_SAW_ASSISTANT_EVOLUTION=" + receiptSawAssistantEvolution + "\n"
                + "RECEIPT_STABLE_SAMPLES=" + receiptStableSamples + "\n"
                + "RAW_MESSAGE_TEXT_RETAINED=false\n"
                + "STREAM_STATE=" + latestStreamState + "\n"
                + latestDom + "\n"
                + "--- ROUTE LOG (SANITIZED; NO QUERY/FRAGMENT) ---\n"
                + routeLog;
    }

    private void downloadReport() {
        String timestamp = new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date());
        String fileName = "chatgpt-webview-report-" + timestamp + ".txt";
        ContentValues values = new ContentValues();
        values.put(MediaStore.MediaColumns.DISPLAY_NAME, fileName);
        values.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
        values.put(MediaStore.MediaColumns.RELATIVE_PATH,
                Environment.DIRECTORY_DOWNLOADS + "/ChatGPTWebViewProbe");
        values.put(MediaStore.MediaColumns.IS_PENDING, 1);

        Uri collection = MediaStore.Downloads.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY);
        Uri item = null;
        try {
            item = getContentResolver().insert(collection, values);
            if (item == null) throw new IllegalStateException("MediaStore insert returned null");
            try (OutputStream out = getContentResolver().openOutputStream(item, "w")) {
                if (out == null) throw new IllegalStateException("Output stream unavailable");
                out.write(buildReport().getBytes(StandardCharsets.UTF_8));
                out.flush();
            }
            ContentValues done = new ContentValues();
            done.put(MediaStore.MediaColumns.IS_PENDING, 0);
            getContentResolver().update(item, done, null, null);
            Toast.makeText(this,
                    "Downloaded: Downloads/ChatGPTWebViewProbe/" + fileName,
                    Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            if (item != null) getContentResolver().delete(item, null, null);
            Toast.makeText(this,
                    "Download failed: " + e.getClass().getSimpleName(),
                    Toast.LENGTH_LONG).show();
        }
    }

    private String normalize(String s) {
        return s == null ? "" : s.replaceAll("\\s+", " ").trim();
    }

    private String sha256(String value) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] bytes = digest.digest(value.getBytes(StandardCharsets.UTF_8));
        StringBuilder hex = new StringBuilder();
        for (byte b : bytes) hex.append(String.format(Locale.US, "%02x", b & 0xff));
        return hex.toString();
    }

    private boolean safeEq(String a, String b) {
        return a == null ? b == null : a.equals(b);
    }

    private String safe(String s) {
        return s == null ? "-" : s;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    @Override public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    @Override protected void onPause() {
        CookieManager.getInstance().flush();
        super.onPause();
    }

    @Override protected void onDestroy() {
        handler.removeCallbacks(probeRunnable);
        if (webView != null) webView.destroy();
        super.onDestroy();
    }

    private static final class Fingerprint {
        final int count;
        final String hash;
        Fingerprint(int count, String hash) {
            this.count = count;
            this.hash = hash;
        }
    }

    private static final class DomSnapshot {
        final Fingerprint users;
        final Fingerprint assistants;
        final int stopControls;
        final int busyNodes;
        final int responseActions;
        final String streamState;
        final String summary;

        DomSnapshot(Fingerprint users, Fingerprint assistants,
                    int stopControls, int busyNodes, int responseActions,
                    String streamState, String summary) {
            this.users = users;
            this.assistants = assistants;
            this.stopControls = stopControls;
            this.busyNodes = busyNodes;
            this.responseActions = responseActions;
            this.streamState = streamState;
            this.summary = summary;
        }
    }
}
