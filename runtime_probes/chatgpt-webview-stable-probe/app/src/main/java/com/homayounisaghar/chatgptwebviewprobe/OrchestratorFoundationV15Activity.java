package com.homayounisaghar.chatgptwebviewprobe;

import android.Manifest;
import android.content.ContentValues;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.MediaStore;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
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
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;

/**
 * Stable v0.15 - Interaction Session + Orchestrator Foundation.
 *
 * Architectural boundary:
 * - Dashboard/native controls are clients, not the supervisor.
 * - This Activity hosts the first deterministic Orchestrator/Supervisor slice.
 * - PlannerAdapter is intentionally NONE_DETERMINISTIC in this gate; a future
 *   ChatGPT-Web/API/local planner can be swapped in without changing capability contracts.
 * - Capability actions are semantic DOM operations with durable claims and observable
 *   receipts. No coordinates, XPath, private ChatGPT APIs, credentials, cookies or tokens.
 * - MicArbiter owns an explicit PHONE MicLease. WebView audio permission is granted only
 *   for trusted https://chatgpt.com while that lease is valid.
 * - ActivationSource is UI_TAP in this build. WAKE_WORD, BLUETOOTH_PTT and ASSISTANT_ROLE
 *   remain replaceable future activation adapters, not dependencies of the core.
 */
public class OrchestratorFoundationV15Activity extends AudioFixVisibleActivityV14Activity {
    private static final int REQ_AUDIO_15 = 1501;
    private static final long DICT_LEASE_MS = 2L * 60L * 1000L;
    private static final long LIVE_LEASE_MS = 10L * 60L * 1000L;
    private static final String PREFS_15 = "stable_v15_orchestrator";

    private static final String ORCHESTRATOR_ROLE = "SUPERVISOR_NOT_DASHBOARD";
    private static final String PLANNER_ADAPTER = "NONE_DETERMINISTIC";
    private static final String POLICY_MODE = "LOCAL_FAIL_CLOSED";
    private static final String ACTIVATION_SOURCE = "UI_TAP";

    private final Handler h15 = new Handler(Looper.getMainLooper());
    private final StringBuilder events15 = new StringBuilder();
    private SharedPreferences prefs15;
    private WebView web15;
    private TextView status15;
    private Button sessionButton;

    private String sessionState = "IDLE";
    private String sessionId = "-";
    private long sessionStartedAt = 0L;

    private String micLeaseMode = "NONE";
    private long micLeaseUntil = 0L;
    private int webAudioPermissionRequests = 0;
    private int webAudioPermissionGrants = 0;
    private int webAudioPermissionDenials = 0;
    private String lastPermissionOrigin = "-";

    private String runState = "IDLE";
    private boolean snapshotInitialized = false;
    private int lastUserCount = 0;
    private int lastAssistantCount = 0;
    private int lastAssistantLen = 0;
    private String lastAssistantHash = "-";
    private long lastAssistantChangeAt = 0L;
    private boolean runCycleSeen = false;

    private String lastAudioState = "UNKNOWN";
    private final Set<String> lastCats = new HashSet<>();
    private int lastComposerLen = 0;
    private String lastComposerHash = "-";
    private boolean lastRunStop = false;

    private String transientStatus = "";
    private String transientStatusKind = "none";
    private int transientStatusLen = 0;
    private String transientStatusHash = "-";
    private long transientStatusUntil = 0L;

    private String lastAction = "NONE";
    private String lastActionStatus = "NOT_RUN";
    private String uncertainBlockedAction = "NONE";
    private PendingOp pending;

    private final Runnable poller15 = new Runnable() {
        @Override public void run() {
            if (web15 != null && isTrustedUrl15(web15.getUrl())) pollSnapshot15();
            expireMicLeaseIfNeeded();
            render15();
            h15.postDelayed(this, 350L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs15 = getSharedPreferences(PREFS_15, MODE_PRIVATE);
        web15 = findWeb15(getWindow().getDecorView());
        if (web15 == null) return;
        web15.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        hideParentUiAndInstallV15();
        installLeaseAwareWebChromeClient();
        ev15("V15_READY_ORCHESTRATOR_FOUNDATION");
        h15.post(poller15);
        render15();
    }

    private void hideParentUiAndInstallV15() {
        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) content;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        for (int i = 0; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            if (child != web15) child.setVisibility(View.GONE);
        }

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);

        LinearLayout row1 = row15();
        sessionButton = button15("SESSION START", v -> toggleSession15());
        row1.addView(sessionButton, weight15());
        row1.addView(button15("D START", v -> dispatchCapability15("DICTATION_START")), weight15());
        row1.addView(button15("D STOP", v -> dispatchCapability15("DICTATION_STOP")), weight15());
        row1.addView(button15("D COMMIT", v -> dispatchCapability15("DICTATION_COMMIT")), weight15());
        panel.addView(row1, rowParams15());

        LinearLayout row2 = row15();
        row2.addView(button15("D CANCEL", v -> dispatchCapability15("DICTATION_CANCEL")), weight15());
        row2.addView(button15("D SEND", v -> dispatchCapability15("DICTATION_SEND")), weight15());
        row2.addView(button15("V START", v -> dispatchCapability15("VOICE_START")), weight15());
        row2.addView(button15("V END", v -> dispatchCapability15("VOICE_END")), weight15());
        panel.addView(row2, rowParams15());

        LinearLayout row3 = row15();
        row3.addView(button15("V MUTE", v -> dispatchCapability15("VOICE_MUTE")), weight15());
        row3.addView(button15("V UNMUTE", v -> dispatchCapability15("VOICE_UNMUTE")), weight15());
        row3.addView(button15("STATE", v -> pollSnapshot15()), weight15());
        row3.addView(button15("REPORT15", v -> saveReport15()), weight15());
        panel.addView(row3, rowParams15());

        status15 = new TextView(this);
        status15.setTextSize(8.2f);
        status15.setTextIsSelectable(true);
        status15.setPadding(dp15(7), dp15(2), dp15(7), dp15(2));
        ScrollView sv = new ScrollView(this);
        sv.addView(status15, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));
        panel.addView(sv, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp15(94)));

        int wi = root.indexOfChild(web15);
        if (wi < 0) wi = root.getChildCount();
        root.addView(panel, wi, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private LinearLayout row15() {
        LinearLayout r = new LinearLayout(this);
        r.setOrientation(LinearLayout.HORIZONTAL);
        return r;
    }

    private LinearLayout.LayoutParams rowParams15() {
        return new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp15(35));
    }

    private LinearLayout.LayoutParams weight15() {
        return new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f);
    }

    private Button button15(String text, View.OnClickListener l) {
        Button b = new Button(this);
        b.setText(text);
        b.setTextSize(7.8f);
        b.setOnClickListener(l);
        return b;
    }

    private void installLeaseAwareWebChromeClient() {
        web15.setWebChromeClient(new WebChromeClient() {
            @Override public void onPermissionRequest(PermissionRequest request) {
                runOnUiThread(() -> handlePermission15(request));
            }

            @Override public void onPermissionRequestCanceled(PermissionRequest request) {
                ev15("WEB_PERMISSION_CANCELED");
            }
        });
    }

    private void handlePermission15(PermissionRequest request) {
        webAudioPermissionRequests++;
        if (request == null) return;
        Uri origin = request.getOrigin();
        lastPermissionOrigin = safeOrigin15(origin);
        String[] resources = request.getResources();
        boolean audio = false;
        boolean other = false;
        if (resources != null) {
            for (String r : resources) {
                if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(r)) audio = true;
                else other = true;
            }
        }
        boolean allowed = audio && !other && trustedOrigin15(origin)
                && "ACTIVE".equals(sessionState) && micLeaseValid15();
        if (allowed) {
            request.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
            webAudioPermissionGrants++;
            ev15("WEB_AUDIO_CAPTURE_GRANTED mode=" + micLeaseMode);
        } else {
            request.deny();
            webAudioPermissionDenials++;
            ev15("WEB_AUDIO_CAPTURE_DENIED session=" + sessionState + " lease=" + micLeaseMode
                    + " audio=" + audio + " other=" + other);
        }
        render15();
    }

    private void toggleSession15() {
        if ("IDLE".equals(sessionState)) {
            if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQ_AUDIO_15);
                lastActionStatus = "WAITING_ANDROID_AUDIO_PERMISSION";
                render15();
                return;
            }
            startSession15();
            return;
        }
        if (!"NONE".equals(micLeaseMode)) {
            lastActionStatus = "SESSION_END_BLOCKED_MIC_LEASE_" + micLeaseMode;
            ev15(lastActionStatus);
            render15();
            return;
        }
        sessionState = "IDLE";
        sessionId = "-";
        sessionStartedAt = 0L;
        pending = null;
        runState = "IDLE";
        runCycleSeen = false;
        uncertainBlockedAction = "NONE";
        lastAction = "SESSION_END";
        lastActionStatus = "CONFIRMED";
        ev15("SESSION_ENDED");
        render15();
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        if (requestCode != REQ_AUDIO_15) return;
        if (results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED) startSession15();
        else {
            lastAction = "SESSION_START";
            lastActionStatus = "BLOCKED_ANDROID_AUDIO_PERMISSION_DENIED";
            ev15(lastActionStatus);
            render15();
        }
    }

    private void startSession15() {
        sessionState = "ACTIVE";
        sessionId = UUID.randomUUID().toString();
        sessionStartedAt = System.currentTimeMillis();
        micLeaseMode = "NONE";
        micLeaseUntil = 0L;
        pending = null;
        uncertainBlockedAction = "NONE";
        lastAction = "SESSION_START";
        lastActionStatus = "CONFIRMED";
        snapshotInitialized = false;
        runState = "IDLE";
        runCycleSeen = false;
        ev15("SESSION_STARTED activation=" + ACTIVATION_SOURCE + " planner=" + PLANNER_ADAPTER);
        pollSnapshot15();
        render15();
    }

    private void dispatchCapability15(String action) {
        if (!"ACTIVE".equals(sessionState)) {
            lastAction = action;
            lastActionStatus = "BLOCKED_SESSION_NOT_ACTIVE";
            ev15(action + " BLOCKED_SESSION_NOT_ACTIVE");
            render15();
            return;
        }
        if (!isTrustedUrl15(web15.getUrl())) {
            lastAction = action;
            lastActionStatus = "BLOCKED_UNTRUSTED_ORIGIN";
            ev15(action + " BLOCKED_UNTRUSTED_ORIGIN");
            render15();
            return;
        }
        if (pending != null) {
            lastAction = action;
            lastActionStatus = "BLOCKED_OTHER_ACTION_PENDING_" + pending.action;
            render15();
            return;
        }
        if (action.equals(uncertainBlockedAction)) {
            lastAction = action;
            lastActionStatus = "BLOCKED_PRIOR_UNCERTAIN_NO_REPLAY";
            ev15(action + " BLOCKED_PRIOR_UNCERTAIN_NO_REPLAY");
            render15();
            return;
        }

        if ("DICTATION_COMMIT".equals(action) && lastComposerLen > 0
                && !lastCats.contains("CONFIRM") && !lastCats.contains("STOP") && !lastCats.contains("CANCEL")) {
            lastAction = action;
            lastActionStatus = "CONFIRMED_NOOP_ALREADY_COMMITTED";
            ev15(action + " CONFIRMED_NOOP_ALREADY_COMMITTED");
            render15();
            return;
        }

        String category = categoryForAction15(action);
        if (category == null) {
            lastAction = action;
            lastActionStatus = "BLOCKED_UNSUPPORTED_ACTION";
            render15();
            return;
        }

        if ("DICTATION_START".equals(action)) acquireMicLease15("DICTATION", DICT_LEASE_MS);
        if ("VOICE_START".equals(action)) acquireMicLease15("LIVE", LIVE_LEASE_MS);

        PendingOp op = beginClaim15(action);
        if (op == null) return;
        op.baselineUserCount = lastUserCount;
        op.baselineComposerLen = lastComposerLen;
        op.baselineComposerHash = lastComposerHash;
        op.baselinePermissionGrants = webAudioPermissionGrants;
        op.baselineAudioState = lastAudioState;
        op.category = category;
        op.deadlineAt = System.currentTimeMillis() + timeoutFor15(action);

        web15.evaluateJavascript(actionJs15(category), value -> {
            try {
                JSONObject o = jsonObject15(value);
                int matches = o.optInt("matches", -1);
                boolean clicked = o.optBoolean("clicked", false);
                op.userActivationActive = o.optBoolean("uaActive", false);
                op.userActivationBeen = o.optBoolean("uaBeen", false);
                if (matches != 1 || !clicked) {
                    abortNoSideEffect15(op, "NOT_DISPATCHED_MATCHES_" + matches);
                    if ("DICTATION_START".equals(action) || "VOICE_START".equals(action)) revokeMicLease15("START_NOT_DISPATCHED");
                    return;
                }
                op.dispatched = true;
                op.dispatchedAt = System.currentTimeMillis();
                lastActionStatus = "DISPATCHED_WAITING_RECEIPT";
                prefs15.edit().putString("claim_status", "DISPATCHED").commit();
                ev15(action + " SINGLE_SEMANTIC_CLICK_DISPATCHED uaActive=" + op.userActivationActive
                        + " uaBeen=" + op.userActivationBeen);
                render15();
            } catch (Exception e) {
                abortNoSideEffect15(op, "NOT_DISPATCHED_PARSE_" + e.getClass().getSimpleName());
                if ("DICTATION_START".equals(action) || "VOICE_START".equals(action)) revokeMicLease15("START_PARSE_FAIL");
            }
        });
    }

    private PendingOp beginClaim15(String action) {
        PendingOp op = new PendingOp();
        op.action = action;
        op.claimId = action + "_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0, 8);
        op.claimedAt = System.currentTimeMillis();
        boolean ok = prefs15.edit()
                .putString("claim_id", op.claimId)
                .putString("claim_action", action)
                .putString("claim_status", "CLAIMED")
                .putLong("claim_at", op.claimedAt)
                .commit();
        if (!ok) {
            lastAction = action;
            lastActionStatus = "BLOCKED_DURABLE_CLAIM_WRITE_FAIL";
            ev15(action + " DURABLE_CLAIM_WRITE_FAIL");
            render15();
            return null;
        }
        pending = op;
        lastAction = action;
        lastActionStatus = "DURABLE_CLAIMED";
        ev15(action + " DURABLE_CLAIMED id=" + token15(op.claimId));
        return op;
    }

    private void abortNoSideEffect15(PendingOp op, String reason) {
        if (pending != op) return;
        pending = null;
        lastAction = op.action;
        lastActionStatus = "ABORTED_" + token15(reason);
        prefs15.edit().putString("claim_status", "ABORTED_NO_SIDE_EFFECT").commit();
        ev15(op.action + " ABORTED_NO_SIDE_EFFECT " + token15(reason));
        render15();
    }

    private void confirmPending15(String receipt) {
        if (pending == null) return;
        PendingOp op = pending;
        pending = null;
        lastAction = op.action;
        lastActionStatus = "CONFIRMED_" + token15(receipt);
        prefs15.edit()
                .putString("claim_status", "CONFIRMED")
                .putString("claim_receipt", token15(receipt))
                .commit();
        ev15(op.action + " CONFIRMED receipt=" + token15(receipt));
        if ("DICTATION_STOP".equals(op.action) || "DICTATION_CANCEL".equals(op.action)
                || "DICTATION_COMMIT".equals(op.action)) revokeMicLease15("DICTATION_FINISHED");
        if ("VOICE_END".equals(op.action)) revokeMicLease15("VOICE_ENDED");
        render15();
    }

    private void uncertainPending15(String reason) {
        if (pending == null) return;
        PendingOp op = pending;
        pending = null;
        lastAction = op.action;
        lastActionStatus = "UNCERTAIN_" + token15(reason);
        uncertainBlockedAction = op.action;
        prefs15.edit()
                .putString("claim_status", "UNCERTAIN")
                .putString("claim_receipt", token15(reason))
                .commit();
        ev15(op.action + " UNCERTAIN_NO_REPLAY " + token15(reason));
        render15();
    }

    private void pollSnapshot15() {
        if (web15 == null || !isTrustedUrl15(web15.getUrl())) return;
        web15.evaluateJavascript(snapshotJs15(), value -> {
            try {
                JSONObject o = jsonObject15(value);
                Snapshot15 s = Snapshot15.from(o);
                applySnapshot15(s);
            } catch (Exception e) {
                ev15("SNAPSHOT_PARSE_FAIL_" + e.getClass().getSimpleName());
            }
        });
    }

    private void applySnapshot15(Snapshot15 s) {
        long now = System.currentTimeMillis();
        lastAudioState = token15(s.audioState);
        lastCats.clear();
        lastCats.addAll(s.cats);
        lastComposerLen = s.composerLen;
        lastComposerHash = token15(s.composerHash);
        lastRunStop = s.runStop;

        if (!s.visibleStatus.isEmpty()) {
            transientStatus = s.visibleStatus.length() > 180 ? s.visibleStatus.substring(0, 180) : s.visibleStatus;
            transientStatusKind = token15(s.visibleStatusKind);
            transientStatusLen = s.visibleStatus.length();
            transientStatusHash = sha256Hex15(s.visibleStatus);
            transientStatusUntil = now + 8000L;
        } else if (now > transientStatusUntil) {
            transientStatus = "";
        }

        if (!snapshotInitialized) {
            snapshotInitialized = true;
            lastUserCount = s.userCount;
            lastAssistantCount = s.assistantCount;
            lastAssistantLen = s.assistantLen;
            lastAssistantHash = token15(s.assistantHash);
            render15();
            return;
        }

        if (s.userCount > lastUserCount) {
            runCycleSeen = true;
            runState = "ACTIVE";
            ev15("RUN_USER_TURN_SEEN count=" + s.userCount);
        }

        boolean assistantChanged = s.assistantCount != lastAssistantCount
                || s.assistantLen != lastAssistantLen
                || !token15(s.assistantHash).equals(lastAssistantHash);
        if (assistantChanged) {
            lastAssistantChangeAt = now;
            if (runCycleSeen || s.runStop) runState = "STREAMING";
            ev15("RUN_ASSISTANT_CHANGE count=" + s.assistantCount + " len=" + s.assistantLen);
        }

        if (s.runStop) {
            if (assistantChanged || (lastAssistantChangeAt > 0 && now - lastAssistantChangeAt < 2500L)) runState = "STREAMING";
            else runState = "ACTIVE";
            runCycleSeen = true;
        } else if (runCycleSeen && lastAssistantChangeAt > 0 && now - lastAssistantChangeAt > 2800L) {
            if (!"COMPLETE".equals(runState)) ev15("RUN_COMPLETE");
            runState = "COMPLETE";
            runCycleSeen = false;
        }

        lastUserCount = s.userCount;
        lastAssistantCount = s.assistantCount;
        lastAssistantLen = s.assistantLen;
        lastAssistantHash = token15(s.assistantHash);

        checkPendingReceipt15(s, now);
        render15();
    }

    private void checkPendingReceipt15(Snapshot15 s, long now) {
        if (pending == null || !pending.dispatched) return;
        PendingOp op = pending;
        long age = now - op.dispatchedAt;
        switch (op.action) {
            case "DICTATION_START":
                if (webAudioPermissionGrants > op.baselinePermissionGrants) {
                    confirmPending15("WEB_AUDIO_PERMISSION_AFTER_START");
                    return;
                }
                break;
            case "DICTATION_STOP":
                if ((s.composerLen > 0 && (!s.composerHash.equals(op.baselineComposerHash)
                        || s.composerLen != op.baselineComposerLen))
                        || (age > 850L && !s.cats.contains("STOP") && !s.cats.contains("CANCEL"))) {
                    confirmPending15("DICTATION_STOPPED_COMPOSER_OR_CONTROLS");
                    return;
                }
                break;
            case "DICTATION_COMMIT":
                if (!s.cats.contains("CONFIRM") && (s.composerLen > 0
                        || !s.composerHash.equals(op.baselineComposerHash))) {
                    confirmPending15("DICTATION_COMMITTED");
                    return;
                }
                break;
            case "DICTATION_CANCEL":
                if (age > 450L && !s.cats.contains("CANCEL") && !s.cats.contains("STOP")) {
                    confirmPending15("DICTATION_CANCELED");
                    return;
                }
                break;
            case "DICTATION_SEND":
                if (s.userCount > op.baselineUserCount && s.composerLen == 0) {
                    confirmPending15("USER_TURN_RECEIPT_AND_COMPOSER_CLEARED");
                    return;
                }
                break;
            case "VOICE_START":
                if ("VOICE_ACTIVE".equals(s.audioState)) {
                    confirmPending15("VOICE_ACTIVE");
                    return;
                }
                break;
            case "VOICE_END":
                if (age > 450L && !"VOICE_ACTIVE".equals(s.audioState)
                        && (s.cats.contains("VOICE_START") || s.cats.contains("DICTATION_MIC"))) {
                    confirmPending15("VOICE_ENDED_READY_CONTROLS");
                    return;
                }
                break;
            case "VOICE_MUTE":
                if (s.cats.contains("UNMUTE") && !s.cats.contains("MUTE")) {
                    confirmPending15("VOICE_MUTED");
                    return;
                }
                break;
            case "VOICE_UNMUTE":
                if (s.cats.contains("MUTE") && !s.cats.contains("UNMUTE")) {
                    confirmPending15("VOICE_UNMUTED");
                    return;
                }
                break;
            default:
                break;
        }
        if (now > op.deadlineAt) uncertainPending15("RECEIPT_TIMEOUT");
    }

    private void acquireMicLease15(String mode, long duration) {
        micLeaseMode = mode;
        micLeaseUntil = System.currentTimeMillis() + duration;
        ev15("MIC_LEASE_ARMED source=PHONE mode=" + mode + " ms=" + duration);
    }

    private void revokeMicLease15(String reason) {
        if (!"NONE".equals(micLeaseMode)) ev15("MIC_LEASE_REVOKED mode=" + micLeaseMode + " reason=" + token15(reason));
        micLeaseMode = "NONE";
        micLeaseUntil = 0L;
    }

    private boolean micLeaseValid15() {
        return !"NONE".equals(micLeaseMode) && System.currentTimeMillis() < micLeaseUntil;
    }

    private void expireMicLeaseIfNeeded() {
        if (!"NONE".equals(micLeaseMode) && System.currentTimeMillis() >= micLeaseUntil) {
            ev15("MIC_LEASE_EXPIRED mode=" + micLeaseMode);
            micLeaseMode = "NONE";
            micLeaseUntil = 0L;
        }
    }

    private String categoryForAction15(String action) {
        switch (action) {
            case "DICTATION_START": return "DICTATION_MIC";
            case "DICTATION_STOP": return "STOP";
            case "DICTATION_COMMIT": return "CONFIRM";
            case "DICTATION_CANCEL": return "CANCEL";
            case "DICTATION_SEND": return "SEND";
            case "VOICE_START": return "VOICE_START";
            case "VOICE_END": return "VOICE_END";
            case "VOICE_MUTE": return "MUTE";
            case "VOICE_UNMUTE": return "UNMUTE";
            default: return null;
        }
    }

    private long timeoutFor15(String action) {
        if ("VOICE_START".equals(action)) return 9000L;
        if ("VOICE_END".equals(action)) return 7000L;
        if ("DICTATION_SEND".equals(action)) return 9000L;
        return 6000L;
    }

    private String actionJs15(String category) {
        return "(function(){try{"
                + sharedJs15()
                + "const want='" + js15(category) + "';const xs=interesting().filter(x=>x.c===want);"
                + "const ua=navigator.userActivation||null;const out={matches:xs.length,clicked:false,uaActive:!!(ua&&ua.isActive),uaBeen:!!(ua&&ua.hasBeenActive)};"
                + "if(xs.length===1){xs[0].e.click();out.clicked=true;}return JSON.stringify(out);"
                + "}catch(e){return JSON.stringify({matches:-1,clicked:false,error:String(e&&e.name||'ERR')});}})();";
    }

    private String snapshotJs15() {
        return "(function(){try{"
                + sharedJs15()
                + "const xs=interesting(),cats=xs.map(x=>x.c),aset=new Set(cats);"
                + "let audioState='NO_AUDIO_CONTROLS';if(aset.has('VOICE_END')||aset.has('MUTE')||aset.has('UNMUTE'))audioState='VOICE_ACTIVE';"
                + "else if(aset.has('CANCEL')&&(aset.has('STOP')||aset.has('CONFIRM')))audioState='DICTATION_ACTIVE';"
                + "else if(aset.has('DICTATION_MIC')&&aset.has('VOICE_START'))audioState='READY_DICTATION_AND_VOICE';"
                + "else if(aset.has('DICTATION_MIC'))audioState='READY_DICTATION';else if(aset.has('VOICE_START'))audioState='READY_VOICE';"
                + "const ed=[...document.querySelectorAll('textarea,[contenteditable=true]')].filter(V);const ce=ed.length?ed[ed.length-1]:null;"
                + "const ct=ce?N(typeof ce.value==='string'?ce.value:(ce.innerText||ce.textContent||'')):'';"
                + "const us=[...document.querySelectorAll('[data-message-author-role=user]')];const as=[...document.querySelectorAll('[data-message-author-role=assistant]')];"
                + "let al=0,ah='-';if(as.length){const x=as[as.length-1],t=N(x.innerText||x.textContent||'');al=t.length;ah=H(t);}"
                + "const runStop=[...document.querySelectorAll('button,[role=button]')].filter(V).some(e=>{const z=M(e).toLowerCase();return /stop generating|stop response|stop-button|stop_response/.test(z)&&!/record|dictat|microphone/.test(z);});"
                + "let best=null;for(const e of [...document.querySelectorAll('[role=status],[aria-live],summary,[data-testid]')]){if(!V(e))continue;const t=N(e.innerText||e.textContent||'');if(!t||t.length>220)continue;const role=(e.getAttribute('role')||'').toLowerCase();const live=(e.getAttribute('aria-live')||'').toLowerCase();const test=(e.getAttribute('data-testid')||'').toLowerCase();const sem=role==='status'||e.tagName==='SUMMARY'||/reason|think|progress|status|research|browse|search/.test(test)||(live&&t.length<=160);if(!sem)continue;let sc=0;if(role==='status')sc+=5;if(/reason|think|progress|research/.test(test))sc+=6;if(e.tagName==='SUMMARY')sc+=4;if(live)sc+=2;let k=role==='status'?'role_status':(e.tagName==='SUMMARY'?'summary':(/reason|think/.test(test)?'reasoning_testid':(/progress|status|research|browse|search/.test(test)?'progress_testid':'aria_live')));if(!best||sc>best.sc)best={text:t,kind:k,sc:sc};}"
                + "return JSON.stringify({audioState:audioState,cats:cats,composerLen:ct.length,composerHash:ct?H(ct):'-',userCount:us.length,assistantCount:as.length,assistantLen:al,assistantHash:ah,runStop:runStop,visibleStatus:best?best.text:'',visibleStatusKind:best?best.kind:'none'});"
                + "}catch(e){return JSON.stringify({error:String(e&&e.name||'ERR')});}})();";
    }

    private String sharedJs15() {
        return "const N=x=>String(x||'').replace(/\\s+/g,' ').trim();"
                + "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
                + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "const M=e=>N((e.getAttribute&&e.getAttribute('aria-label'))||'')+' '+N((e.getAttribute&&e.getAttribute('title'))||'')+' '+N((e.getAttribute&&e.getAttribute('data-testid'))||'')+' '+N(e.innerText||e.textContent||'');"
                + "const cat=e=>{const x=M(e).toLowerCase();if(/unmute/.test(x))return 'UNMUTE';if(/mute/.test(x))return 'MUTE';if(/end voice|leave voice|exit voice|end call/.test(x))return 'VOICE_END';if(/voice mode|start voice|open voice|advanced voice/.test(x))return 'VOICE_START';if(/microphone|dictat|voice input|record audio|record message/.test(x))return 'DICTATION_MIC';if(/cancel|discard/.test(x))return 'CANCEL';if(/stop|finish recording|stop recording/.test(x))return 'STOP';if(/confirm|done|accept|use recording/.test(x))return 'CONFIRM';if(/^send$|send message|submit/.test(x))return 'SEND';return 'OTHER';};"
                + "const interesting=()=>[...document.querySelectorAll('button,[role=button],[aria-label]')].filter(V).map(e=>({e:e,c:cat(e)})).filter(x=>x.c!=='OTHER');";
    }

    private void render15() {
        if (status15 == null) return;
        long now = System.currentTimeMillis();
        long sessionAge = sessionStartedAt == 0L ? -1L : Math.max(0L, now - sessionStartedAt);
        long leaseRemain = micLeaseUntil == 0L ? 0L : Math.max(0L, micLeaseUntil - now);
        String vis = transientStatus.isEmpty() ? "(none)" : transientStatus;
        status15.setText("v0.15 ORCHESTRATOR FOUNDATION\n"
                + "Session=" + sessionState + " ageMs=" + sessionAge + " Activation=" + ACTIVATION_SOURCE
                + " Planner=" + PLANNER_ADAPTER + "\n"
                + "MicLease=PHONE/" + micLeaseMode + " remainMs=" + leaseRemain
                + " WebAudio grants=" + webAudioPermissionGrants + " denies=" + webAudioPermissionDenials + "\n"
                + "RunState=" + runState + " AudioState=" + lastAudioState + " Stop=" + lastRunStop
                + " ComposerLen=" + lastComposerLen + "\n"
                + "Action=" + lastAction + " status=" + lastActionStatus + "\n"
                + "VisibleStatus(last<=8s): " + vis);
        if (sessionButton != null) sessionButton.setText("ACTIVE".equals(sessionState) ? "SESSION END" : "SESSION START");
    }

    private void saveReport15() {
        try {
            String name = "chatgpt-webview-v15-orchestrator-"
                    + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".txt";
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            cv.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
            cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (u == null) throw new IllegalStateException("insert");
            try (OutputStream out = getContentResolver().openOutputStream(u)) {
                if (out == null) throw new IllegalStateException("stream");
                out.write(reportText15().getBytes(StandardCharsets.UTF_8));
            }
            Toast.makeText(this, "v0.15 report saved to Downloads", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "REPORT15 failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
        }
    }

    private String reportText15() {
        long now = System.currentTimeMillis();
        StringBuilder r = new StringBuilder();
        r.append("CHATGPT_WEBVIEW_STABLE_V15_ORCHESTRATOR_FOUNDATION\n");
        r.append("ORCHESTRATOR_ROLE=").append(ORCHESTRATOR_ROLE).append('\n');
        r.append("DASHBOARD_ROLE=UI_CLIENT_ONLY\n");
        r.append("PLANNER_ADAPTER=").append(PLANNER_ADAPTER).append('\n');
        r.append("POLICY_MODE=").append(POLICY_MODE).append('\n');
        r.append("ACTIVATION_SOURCE=").append(ACTIVATION_SOURCE).append('\n');
        r.append("FUTURE_ACTIVATION_ADAPTERS=WAKE_WORD|BLUETOOTH_PTT|ASSISTANT_ROLE\n");
        r.append("SESSION_STATE=").append(sessionState).append('\n');
        r.append("SESSION_ID_PRESENT=").append(!"-".equals(sessionId)).append('\n');
        r.append("MIC_SOURCE=PHONE\n");
        r.append("MIC_LEASE_MODE=").append(micLeaseMode).append('\n');
        r.append("MIC_LEASE_VALID=").append(micLeaseValid15()).append('\n');
        r.append("MIC_LEASE_REMAIN_MS=").append(micLeaseUntil == 0L ? 0L : Math.max(0L, micLeaseUntil - now)).append('\n');
        r.append("WEB_AUDIO_PERMISSION_REQUESTS=").append(webAudioPermissionRequests).append('\n');
        r.append("WEB_AUDIO_PERMISSION_GRANTS=").append(webAudioPermissionGrants).append('\n');
        r.append("WEB_AUDIO_PERMISSION_DENIALS=").append(webAudioPermissionDenials).append('\n');
        r.append("LAST_PERMISSION_ORIGIN=").append(token15(lastPermissionOrigin)).append('\n');
        r.append("RUN_STATE=").append(runState).append('\n');
        r.append("AUDIO_STATE=").append(lastAudioState).append('\n');
        r.append("RUN_STOP_PRESENT=").append(lastRunStop).append('\n');
        r.append("USER_TURN_COUNT=").append(lastUserCount).append('\n');
        r.append("ASSISTANT_TURN_COUNT=").append(lastAssistantCount).append('\n');
        r.append("LAST_ASSISTANT_LENGTH=").append(lastAssistantLen).append('\n');
        r.append("LAST_ASSISTANT_HASH=").append(lastAssistantHash).append('\n');
        r.append("COMPOSER_LENGTH=").append(lastComposerLen).append('\n');
        r.append("COMPOSER_HASH=").append(lastComposerHash).append('\n');
        r.append("LAST_VISIBLE_STATUS_KIND=").append(transientStatusKind).append('\n');
        r.append("LAST_VISIBLE_STATUS_LENGTH=").append(transientStatusLen).append('\n');
        r.append("LAST_VISIBLE_STATUS_SHA256=").append(transientStatusHash).append('\n');
        r.append("VISIBLE_STATUS_RAW_PERSISTED=false\n");
        r.append("LAST_ACTION=").append(token15(lastAction)).append('\n');
        r.append("LAST_ACTION_STATUS=").append(token15(lastActionStatus)).append('\n');
        r.append("UNCERTAIN_BLOCKED_ACTION=").append(token15(uncertainBlockedAction)).append('\n');
        r.append("PENDING_ACTION=").append(pending == null ? "NONE" : token15(pending.action)).append('\n');
        r.append("SEMANTIC_COORDINATES_USED=false\n");
        r.append("PRIVATE_CHATGPT_API_USED=false\n");
        r.append("CHATGPT_CREDENTIALS_EXTRACTED=false\n");
        r.append("RAW_AUDIO_RETAINED=false\n");
        r.append("RAW_SPEECH_RETAINED=false\n");
        r.append("RAW_CHAT_TEXT_RETAINED=false\n");
        r.append("HIDDEN_CHAIN_OF_THOUGHT_ACCESSED=false\n");
        r.append("--- V15 EVENT LOG ---\n").append(events15);
        return r.toString();
    }

    private boolean isTrustedUrl15(String url) {
        try {
            Uri u = Uri.parse(url == null ? "" : url);
            return "https".equalsIgnoreCase(u.getScheme()) && "chatgpt.com".equalsIgnoreCase(u.getHost());
        } catch (Exception e) { return false; }
    }

    private boolean trustedOrigin15(Uri u) {
        return u != null && "https".equalsIgnoreCase(u.getScheme()) && "chatgpt.com".equalsIgnoreCase(u.getHost());
    }

    private String safeOrigin15(Uri u) {
        if (u == null) return "-";
        String s = u.getScheme() == null ? "-" : u.getScheme();
        String h = u.getHost() == null ? "-" : u.getHost();
        return s + "://" + h;
    }

    private JSONObject jsonObject15(String value) throws Exception {
        Object outer = new JSONTokener(value == null ? "null" : value).nextValue();
        if (outer instanceof JSONObject) return (JSONObject) outer;
        if (outer instanceof String) return new JSONObject((String) outer);
        return new JSONObject();
    }

    private static String sha256Hex15(String s) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] b = md.digest(s.getBytes(StandardCharsets.UTF_8));
            StringBuilder out = new StringBuilder();
            for (byte x : b) out.append(String.format(Locale.US, "%02x", x & 0xff));
            return out.toString();
        } catch (Exception e) { return "HASH_ERROR"; }
    }

    private void ev15(String s) {
        if (events15.length() < 30000) {
            events15.append(new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date()))
                    .append(" | ").append(token15(s)).append('\n');
        }
    }

    private static String token15(String s) {
        String x = s == null ? "-" : s.replaceAll("[^A-Za-z0-9_.:+/@=|-]", "_");
        return x.length() > 220 ? x.substring(0, 220) : x;
    }

    private static String js15(String s) {
        return s == null ? "" : s.replace("\\", "\\\\").replace("'", "\\'");
    }

    private int dp15(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }

    private WebView findWeb15(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (!(v instanceof ViewGroup)) return null;
        ViewGroup g = (ViewGroup) v;
        for (int i = 0; i < g.getChildCount(); i++) {
            WebView w = findWeb15(g.getChildAt(i));
            if (w != null) return w;
        }
        return null;
    }

    @Override protected void onDestroy() {
        h15.removeCallbacksAndMessages(null);
        revokeMicLease15("ACTIVITY_DESTROY");
        super.onDestroy();
    }

    private static final class PendingOp {
        String action;
        String category;
        String claimId;
        long claimedAt;
        long dispatchedAt;
        long deadlineAt;
        boolean dispatched;
        boolean userActivationActive;
        boolean userActivationBeen;
        int baselineUserCount;
        int baselineComposerLen;
        String baselineComposerHash;
        int baselinePermissionGrants;
        String baselineAudioState;
    }

    private static final class Snapshot15 {
        String audioState = "UNKNOWN";
        final Set<String> cats = new HashSet<>();
        int composerLen = 0;
        String composerHash = "-";
        int userCount = 0;
        int assistantCount = 0;
        int assistantLen = 0;
        String assistantHash = "-";
        boolean runStop = false;
        String visibleStatus = "";
        String visibleStatusKind = "none";

        static Snapshot15 from(JSONObject o) {
            Snapshot15 s = new Snapshot15();
            s.audioState = o.optString("audioState", "UNKNOWN");
            JSONArray a = o.optJSONArray("cats");
            if (a != null) for (int i = 0; i < a.length(); i++) s.cats.add(a.optString(i, ""));
            s.composerLen = o.optInt("composerLen", 0);
            s.composerHash = o.optString("composerHash", "-");
            s.userCount = o.optInt("userCount", 0);
            s.assistantCount = o.optInt("assistantCount", 0);
            s.assistantLen = o.optInt("assistantLen", 0);
            s.assistantHash = o.optString("assistantHash", "-");
            s.runStop = o.optBoolean("runStop", false);
            s.visibleStatus = o.optString("visibleStatus", "");
            s.visibleStatusKind = o.optString("visibleStatusKind", "none");
            return s;
        }
    }
}
