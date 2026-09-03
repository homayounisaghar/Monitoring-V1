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
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;

/**
 * Stable v0.16 - Orchestrator Foundation dictation-toggle repair.
 *
 * v0.15 proved that native -> semantic DICTATION_START works, but it modeled
 * dictation stop as a distinct STOP control. The tested ChatGPT mobile Web UI
 * actually uses the same semantic microphone/dictation control as a start/stop
 * toggle. v0.16 therefore maps both Dictation.Start and Dictation.Stop to the
 * unique visible dictation toggle, while keeping different preconditions and
 * receipts for the two capability operations.
 *
 * The dashboard remains a client. The deterministic supervisor owns session,
 * MicLease, claims, side effects and receipts. No coordinates, XPath, private
 * ChatGPT APIs, credentials, cookies or tokens are used.
 */
public class OrchestratorFoundationV16Activity extends AudioFixVisibleActivityV14Activity {
    private static final int REQ_AUDIO = 1601;
    private static final long DICT_LEASE_MS = 2L * 60L * 1000L;
    private static final long LIVE_LEASE_MS = 10L * 60L * 1000L;
    private static final String PREFS = "stable_v16_orchestrator";
    private static final String PLANNER_ADAPTER = "NONE_DETERMINISTIC";
    private static final String ACTIVATION_SOURCE = "UI_TAP";

    private final Handler h = new Handler(Looper.getMainLooper());
    private final StringBuilder events = new StringBuilder();
    private SharedPreferences prefs;
    private WebView web;
    private TextView status;
    private Button sessionButton;

    private String sessionState = "IDLE";
    private String sessionId = "-";
    private long sessionStartedAt = 0L;

    private String micLeaseMode = "NONE";
    private long micLeaseUntil = 0L;
    private int permissionRequests = 0;
    private int permissionGrants = 0;
    private int permissionDenials = 0;

    private boolean mediaTrackerInstalled = false;
    private int activeAudioTracks = 0;
    private int mediaGumCalls = 0;
    private int mediaGumResolves = 0;
    private int mediaGumRejects = 0;

    private boolean initialized = false;
    private String audioState = "UNKNOWN";
    private final Set<String> cats = new HashSet<>();
    private int dictationCount = 0;
    private int voiceStartCount = 0;
    private int voiceEndCount = 0;
    private int muteCount = 0;
    private int unmuteCount = 0;
    private int sendCount = 0;
    private int cancelCount = 0;
    private int confirmCount = 0;
    private int composerLen = 0;
    private String composerHash = "-";
    private int userCount = 0;
    private int assistantCount = 0;
    private int assistantLen = 0;
    private String assistantHash = "-";
    private long assistantChangedAt = 0L;
    private boolean runStop = false;
    private boolean runCycleSeen = false;
    private String runState = "IDLE";

    private String lastAction = "NONE";
    private String lastActionStatus = "NOT_RUN";
    private String uncertainBlockedAction = "NONE";
    private Pending pending;

    private final Runnable poller = new Runnable() {
        @Override public void run() {
            if (web != null && trustedUrl(web.getUrl())) pollSnapshot();
            if (!"NONE".equals(micLeaseMode) && System.currentTimeMillis() >= micLeaseUntil) {
                ev("MIC_LEASE_EXPIRED mode=" + micLeaseMode);
                micLeaseMode = "NONE";
                micLeaseUntil = 0L;
            }
            render();
            h.postDelayed(this, 300L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        web = findWeb(getWindow().getDecorView());
        if (web == null) return;
        web.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        hideParentUiAndInstallPanel();
        installLeaseAwareChromeClient();
        installMediaTracker();
        ev("V16_READY_DICTATION_TOGGLE_REPAIR");
        h.post(poller);
        render();
    }

    private void hideParentUiAndInstallPanel() {
        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) content;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        for (int i = 0; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            if (child != web) child.setVisibility(View.GONE);
        }

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);

        LinearLayout r1 = row();
        sessionButton = button("SESSION START", v -> toggleSession());
        r1.addView(sessionButton, weight());
        r1.addView(button("D START", v -> dispatch("DICTATION_START")), weight());
        r1.addView(button("D STOP", v -> dispatch("DICTATION_STOP")), weight());
        r1.addView(button("D SEND", v -> dispatch("DICTATION_SEND")), weight());
        panel.addView(r1, rowParams());

        LinearLayout r2 = row();
        r2.addView(button("D CANCEL", v -> dispatch("DICTATION_CANCEL")), weight());
        r2.addView(button("V START", v -> dispatch("VOICE_START")), weight());
        r2.addView(button("V MUTE", v -> dispatch("VOICE_MUTE")), weight());
        r2.addView(button("V UNMUTE", v -> dispatch("VOICE_UNMUTE")), weight());
        panel.addView(r2, rowParams());

        LinearLayout r3 = row();
        r3.addView(button("V END", v -> dispatch("VOICE_END")), weight());
        r3.addView(button("STATE", v -> pollSnapshot()), weight());
        r3.addView(button("REPORT16", v -> saveReport()), weight());
        panel.addView(r3, rowParams());

        status = new TextView(this);
        status.setTextSize(8.1f);
        status.setTextIsSelectable(true);
        status.setPadding(dp(7), dp(2), dp(7), dp(2));
        ScrollView sv = new ScrollView(this);
        sv.addView(status, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));
        panel.addView(sv, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(103)));

        int wi = root.indexOfChild(web);
        if (wi < 0) wi = root.getChildCount();
        root.addView(panel, wi, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    private LinearLayout row() {
        LinearLayout x = new LinearLayout(this);
        x.setOrientation(LinearLayout.HORIZONTAL);
        return x;
    }

    private LinearLayout.LayoutParams rowParams() {
        return new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(35));
    }

    private LinearLayout.LayoutParams weight() {
        return new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f);
    }

    private Button button(String text, View.OnClickListener l) {
        Button b = new Button(this);
        b.setText(text);
        b.setTextSize(7.7f);
        b.setOnClickListener(l);
        return b;
    }

    private void installLeaseAwareChromeClient() {
        web.setWebChromeClient(new WebChromeClient() {
            @Override public void onPermissionRequest(PermissionRequest request) {
                runOnUiThread(() -> handlePermission(request));
            }
        });
    }

    private void handlePermission(PermissionRequest request) {
        permissionRequests++;
        if (request == null) return;
        Uri origin = request.getOrigin();
        boolean audio = false;
        boolean other = false;
        String[] rs = request.getResources();
        if (rs != null) {
            for (String r : rs) {
                if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(r)) audio = true;
                else other = true;
            }
        }
        boolean allow = audio && !other && trustedOrigin(origin)
                && "ACTIVE".equals(sessionState) && micLeaseValid();
        if (allow) {
            request.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
            permissionGrants++;
            ev("WEB_AUDIO_GRANTED mode=" + micLeaseMode);
        } else {
            request.deny();
            permissionDenials++;
            ev("WEB_AUDIO_DENIED session=" + sessionState + " lease=" + micLeaseMode);
        }
    }

    private void toggleSession() {
        if ("IDLE".equals(sessionState)) {
            if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQ_AUDIO);
                lastAction = "SESSION_START";
                lastActionStatus = "WAITING_ANDROID_AUDIO_PERMISSION";
                render();
                return;
            }
            startSession();
            return;
        }
        if (!"NONE".equals(micLeaseMode)) {
            lastAction = "SESSION_END";
            lastActionStatus = "BLOCKED_MIC_LEASE_" + micLeaseMode;
            render();
            return;
        }
        sessionState = "IDLE";
        sessionId = "-";
        pending = null;
        uncertainBlockedAction = "NONE";
        runState = "IDLE";
        lastAction = "SESSION_END";
        lastActionStatus = "CONFIRMED";
        ev("SESSION_ENDED");
        render();
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        if (requestCode != REQ_AUDIO) return;
        if (results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED) startSession();
        else {
            lastAction = "SESSION_START";
            lastActionStatus = "BLOCKED_ANDROID_AUDIO_PERMISSION";
            render();
        }
    }

    private void startSession() {
        sessionState = "ACTIVE";
        sessionId = UUID.randomUUID().toString();
        sessionStartedAt = System.currentTimeMillis();
        pending = null;
        uncertainBlockedAction = "NONE";
        micLeaseMode = "NONE";
        micLeaseUntil = 0L;
        initialized = false;
        runState = "IDLE";
        runCycleSeen = false;
        lastAction = "SESSION_START";
        lastActionStatus = "CONFIRMED";
        installMediaTracker();
        pollSnapshot();
        ev("SESSION_STARTED planner=" + PLANNER_ADAPTER + " activation=" + ACTIVATION_SOURCE);
        render();
    }

    private void dispatch(String action) {
        if (!"ACTIVE".equals(sessionState)) {
            block(action, "SESSION_NOT_ACTIVE");
            return;
        }
        if (!trustedUrl(web.getUrl())) {
            block(action, "UNTRUSTED_ORIGIN");
            return;
        }
        if (pending != null) {
            block(action, "OTHER_ACTION_PENDING_" + pending.action);
            return;
        }
        if (action.equals(uncertainBlockedAction)) {
            block(action, "PRIOR_UNCERTAIN_NO_REPLAY");
            return;
        }

        if ("DICTATION_START".equals(action) && !"NONE".equals(micLeaseMode)) {
            block(action, "MIC_ALREADY_LEASED_" + micLeaseMode);
            return;
        }
        if ("DICTATION_STOP".equals(action) && !"DICTATION".equals(micLeaseMode)) {
            block(action, "NO_DICTATION_LEASE");
            return;
        }
        if ("VOICE_START".equals(action) && !"NONE".equals(micLeaseMode)) {
            block(action, "MIC_ALREADY_LEASED_" + micLeaseMode);
            return;
        }
        if (("VOICE_END".equals(action) || "VOICE_MUTE".equals(action) || "VOICE_UNMUTE".equals(action))
                && !"LIVE".equals(micLeaseMode)) {
            block(action, "NO_LIVE_LEASE");
            return;
        }
        if ("DICTATION_SEND".equals(action) && composerLen <= 0) {
            block(action, "COMPOSER_EMPTY_WAIT_FOR_TRANSCRIPT");
            return;
        }

        String category = categoryFor(action);
        if (category == null) {
            block(action, "UNSUPPORTED");
            return;
        }

        if ("DICTATION_START".equals(action)) acquireLease("DICTATION", DICT_LEASE_MS);
        if ("VOICE_START".equals(action)) acquireLease("LIVE", LIVE_LEASE_MS);

        Pending op = claim(action, category);
        if (op == null) return;
        op.baselineUserCount = userCount;
        op.baselineComposerLen = composerLen;
        op.baselineComposerHash = composerHash;
        op.baselinePermissionGrants = permissionGrants;
        op.baselineActiveTracks = activeAudioTracks;
        op.deadlineAt = System.currentTimeMillis() + timeoutFor(action);

        web.evaluateJavascript(actionJs(category), value -> {
            try {
                JSONObject o = jsonObject(value);
                int matches = o.optInt("matches", -1);
                boolean clicked = o.optBoolean("clicked", false);
                if (matches != 1 || !clicked) {
                    abortNoSideEffect(op, "MATCHES_" + matches);
                    if ("DICTATION_START".equals(action) || "VOICE_START".equals(action)) revokeLease("START_NOT_DISPATCHED");
                    return;
                }
                op.dispatched = true;
                op.dispatchedAt = System.currentTimeMillis();
                lastActionStatus = "DISPATCHED_WAITING_RECEIPT";
                prefs.edit().putString("claim_status", "DISPATCHED").commit();
                ev(action + " SINGLE_SEMANTIC_CLICK category=" + category);
                render();
            } catch (Exception e) {
                abortNoSideEffect(op, "PARSE_" + e.getClass().getSimpleName());
                if ("DICTATION_START".equals(action) || "VOICE_START".equals(action)) revokeLease("START_PARSE_FAIL");
            }
        });
    }

    private Pending claim(String action, String category) {
        Pending op = new Pending();
        op.action = action;
        op.category = category;
        op.claimId = action + "_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0, 8);
        boolean ok = prefs.edit()
                .putString("claim_id", op.claimId)
                .putString("claim_action", action)
                .putString("claim_status", "CLAIMED")
                .commit();
        if (!ok) {
            block(action, "DURABLE_CLAIM_WRITE_FAIL");
            return null;
        }
        pending = op;
        lastAction = action;
        lastActionStatus = "DURABLE_CLAIMED";
        ev(action + " DURABLE_CLAIMED");
        return op;
    }

    private void abortNoSideEffect(Pending op, String reason) {
        if (pending != op) return;
        pending = null;
        lastAction = op.action;
        lastActionStatus = "ABORTED_NO_SIDE_EFFECT_" + token(reason);
        prefs.edit().putString("claim_status", "ABORTED_NO_SIDE_EFFECT").commit();
        ev(op.action + " ABORTED_NO_SIDE_EFFECT " + token(reason));
        render();
    }

    private void confirm(String receipt) {
        if (pending == null) return;
        String action = pending.action;
        pending = null;
        lastAction = action;
        lastActionStatus = "CONFIRMED_" + token(receipt);
        prefs.edit().putString("claim_status", "CONFIRMED").putString("claim_receipt", token(receipt)).commit();
        if ("DICTATION_STOP".equals(action) || "DICTATION_CANCEL".equals(action)) revokeLease("DICTATION_FINISHED");
        if ("VOICE_END".equals(action)) revokeLease("VOICE_ENDED");
        ev(action + " CONFIRMED " + token(receipt));
        render();
    }

    private void uncertain(String reason) {
        if (pending == null) return;
        String action = pending.action;
        pending = null;
        lastAction = action;
        lastActionStatus = "UNCERTAIN_" + token(reason);
        uncertainBlockedAction = action;
        prefs.edit().putString("claim_status", "UNCERTAIN").putString("claim_receipt", token(reason)).commit();
        ev(action + " UNCERTAIN_NO_REPLAY " + token(reason));
        render();
    }

    private void block(String action, String reason) {
        lastAction = action;
        lastActionStatus = "BLOCKED_" + token(reason);
        ev(action + " BLOCKED " + token(reason));
        render();
    }

    private void acquireLease(String mode, long ms) {
        micLeaseMode = mode;
        micLeaseUntil = System.currentTimeMillis() + ms;
        ev("MIC_LEASE_ARMED source=PHONE mode=" + mode);
    }

    private void revokeLease(String reason) {
        if (!"NONE".equals(micLeaseMode)) ev("MIC_LEASE_REVOKED mode=" + micLeaseMode + " reason=" + token(reason));
        micLeaseMode = "NONE";
        micLeaseUntil = 0L;
    }

    private boolean micLeaseValid() {
        return !"NONE".equals(micLeaseMode) && System.currentTimeMillis() < micLeaseUntil;
    }

    private void installMediaTracker() {
        if (web == null || !trustedUrl(web.getUrl())) return;
        web.evaluateJavascript(MEDIA_TRACKER_JS, value -> {
            mediaTrackerInstalled = true;
            ev("MEDIA_TRACKER_INSTALL " + token(String.valueOf(value)));
        });
    }

    private void pollSnapshot() {
        if (web == null || !trustedUrl(web.getUrl())) return;
        web.evaluateJavascript(snapshotJs(), value -> {
            try {
                Snapshot s = Snapshot.from(jsonObject(value));
                applySnapshot(s);
            } catch (Exception e) {
                ev("SNAPSHOT_PARSE_FAIL_" + e.getClass().getSimpleName());
            }
        });
    }

    private void applySnapshot(Snapshot s) {
        long now = System.currentTimeMillis();
        String oldAssistantHash = assistantHash;
        int oldAssistantCount = assistantCount;
        int oldAssistantLen = assistantLen;
        int oldUserCount = userCount;

        audioState = token(s.audioState);
        cats.clear();
        cats.addAll(s.cats);
        dictationCount = s.dictationCount;
        voiceStartCount = s.voiceStartCount;
        voiceEndCount = s.voiceEndCount;
        muteCount = s.muteCount;
        unmuteCount = s.unmuteCount;
        sendCount = s.sendCount;
        cancelCount = s.cancelCount;
        confirmCount = s.confirmCount;
        composerLen = s.composerLen;
        composerHash = token(s.composerHash);
        userCount = s.userCount;
        assistantCount = s.assistantCount;
        assistantLen = s.assistantLen;
        assistantHash = token(s.assistantHash);
        runStop = s.runStop;
        activeAudioTracks = s.activeAudioTracks;
        mediaGumCalls = s.gumCalls;
        mediaGumResolves = s.gumResolves;
        mediaGumRejects = s.gumRejects;

        if (!initialized) {
            initialized = true;
            render();
            return;
        }

        if (userCount > oldUserCount) {
            runCycleSeen = true;
            runState = "ACTIVE";
            ev("RUN_USER_TURN count=" + userCount);
        }
        boolean assistantChanged = assistantCount != oldAssistantCount || assistantLen != oldAssistantLen
                || !assistantHash.equals(oldAssistantHash);
        if (assistantChanged) {
            assistantChangedAt = now;
            if (runCycleSeen || runStop) runState = "STREAMING";
            ev("RUN_ASSISTANT_CHANGE count=" + assistantCount + " len=" + assistantLen);
        }
        if (runStop) {
            runCycleSeen = true;
            runState = assistantChanged || (assistantChangedAt > 0 && now - assistantChangedAt < 2500L)
                    ? "STREAMING" : "ACTIVE";
        } else if (runCycleSeen && assistantChangedAt > 0 && now - assistantChangedAt > 2800L) {
            runState = "COMPLETE";
            runCycleSeen = false;
            ev("RUN_COMPLETE");
        }

        checkReceipt(s, now);
        render();
    }

    private void checkReceipt(Snapshot s, long now) {
        if (pending == null || !pending.dispatched) return;
        Pending op = pending;
        long age = now - op.dispatchedAt;
        switch (op.action) {
            case "DICTATION_START":
                if (s.activeAudioTracks > op.baselineActiveTracks || permissionGrants > op.baselinePermissionGrants) {
                    confirm("DICTATION_AUDIO_ACTIVE");
                    return;
                }
                break;
            case "DICTATION_STOP":
                if (s.activeAudioTracks < op.baselineActiveTracks) {
                    confirm("DICTATION_AUDIO_TRACK_ENDED");
                    return;
                }
                if (s.composerLen > 0 && (!s.composerHash.equals(op.baselineComposerHash)
                        || s.composerLen != op.baselineComposerLen)) {
                    confirm("DICTATION_TRANSCRIPT_IN_COMPOSER");
                    return;
                }
                break;
            case "DICTATION_CANCEL":
                if (age > 450L && s.activeAudioTracks == 0 && s.cancelCount == 0) {
                    confirm("DICTATION_CANCELED");
                    return;
                }
                break;
            case "DICTATION_SEND":
                if (s.userCount > op.baselineUserCount && s.composerLen == 0) {
                    confirm("USER_TURN_RECEIPT");
                    return;
                }
                break;
            case "VOICE_START":
                if ("VOICE_ACTIVE".equals(s.audioState) || s.activeAudioTracks > op.baselineActiveTracks) {
                    confirm("VOICE_ACTIVE");
                    return;
                }
                break;
            case "VOICE_MUTE":
                if (s.unmuteCount == 1 && s.muteCount == 0) {
                    confirm("VOICE_MUTED");
                    return;
                }
                break;
            case "VOICE_UNMUTE":
                if (s.muteCount == 1 && s.unmuteCount == 0) {
                    confirm("VOICE_UNMUTED");
                    return;
                }
                break;
            case "VOICE_END":
                if (age > 400L && s.activeAudioTracks == 0 && !"VOICE_ACTIVE".equals(s.audioState)) {
                    confirm("VOICE_ENDED");
                    return;
                }
                break;
            default:
                break;
        }
        if (now > op.deadlineAt) uncertain("RECEIPT_TIMEOUT");
    }

    private String categoryFor(String action) {
        switch (action) {
            case "DICTATION_START":
            case "DICTATION_STOP": return "DICTATION_MIC";
            case "DICTATION_CANCEL": return "CANCEL";
            case "DICTATION_SEND": return "SEND";
            case "VOICE_START": return "VOICE_START";
            case "VOICE_END": return "VOICE_END";
            case "VOICE_MUTE": return "MUTE";
            case "VOICE_UNMUTE": return "UNMUTE";
            default: return null;
        }
    }

    private long timeoutFor(String action) {
        if ("DICTATION_STOP".equals(action)) return 12000L;
        if ("DICTATION_SEND".equals(action)) return 10000L;
        if ("VOICE_START".equals(action) || "VOICE_END".equals(action)) return 10000L;
        return 7000L;
    }

    private String actionJs(String category) {
        return "(function(){try{" + SHARED_JS
                + "const want='" + js(category) + "';const xs=I().filter(x=>x.c===want);"
                + "const out={matches:xs.length,clicked:false};if(xs.length===1){xs[0].e.click();out.clicked=true;}"
                + "return JSON.stringify(out);}catch(e){return JSON.stringify({matches:-1,clicked:false,error:String(e&&e.name||'ERR')});}})();";
    }

    private String snapshotJs() {
        return "(function(){try{" + SHARED_JS
                + "const xs=I(),cs=xs.map(x=>x.c),S=new Set(cs);"
                + "let ast='NO_AUDIO_CONTROLS';if(S.has('VOICE_END')||S.has('MUTE')||S.has('UNMUTE'))ast='VOICE_ACTIVE';"
                + "else if(S.has('DICTATION_MIC')&&S.has('VOICE_START'))ast='READY_DICTATION_AND_VOICE';"
                + "else if(S.has('DICTATION_MIC'))ast='READY_DICTATION';else if(S.has('VOICE_START'))ast='READY_VOICE';"
                + "const ed=[...document.querySelectorAll('#prompt-textarea,textarea,[contenteditable=true]')].filter(V);const ce=ed.length?ed[ed.length-1]:null;"
                + "const ct=ce?N(typeof ce.value==='string'?ce.value:(ce.innerText||ce.textContent||'')):'';"
                + "const us=[...document.querySelectorAll('[data-message-author-role=user]')];const as=[...document.querySelectorAll('[data-message-author-role=assistant]')];"
                + "let al=0,ah='-';if(as.length){const t=N(as[as.length-1].innerText||as[as.length-1].textContent||'');al=t.length;ah=H(t);}"
                + "const rs=[...document.querySelectorAll('button,[role=button]')].filter(V).some(e=>{const z=M(e).toLowerCase();return /stop generating|stop response|stop-button|stop_response/.test(z)&&!/record|dictat|microphone/.test(z);});"
                + "const mt=window.__cp16Media||null;const ms=mt&&mt.snap?mt.snap():{active:0,calls:0,ok:0,fail:0};"
                + "const C=k=>cs.filter(x=>x===k).length;return JSON.stringify({audioState:ast,cats:cs,dictationCount:C('DICTATION_MIC'),voiceStartCount:C('VOICE_START'),voiceEndCount:C('VOICE_END'),muteCount:C('MUTE'),unmuteCount:C('UNMUTE'),sendCount:C('SEND'),cancelCount:C('CANCEL'),confirmCount:C('CONFIRM'),composerLen:ct.length,composerHash:ct?H(ct):'-',userCount:us.length,assistantCount:as.length,assistantLen:al,assistantHash:ah,runStop:rs,activeAudioTracks:ms.active||0,gumCalls:ms.calls||0,gumResolves:ms.ok||0,gumRejects:ms.fail||0});"
                + "}catch(e){return JSON.stringify({error:String(e&&e.name||'ERR')});}})();";
    }

    private void render() {
        if (status == null) return;
        long now = System.currentTimeMillis();
        long lease = micLeaseUntil == 0L ? 0L : Math.max(0L, micLeaseUntil - now);
        status.setText("v0.16 ORCHESTRATOR - DICTATION TOGGLE REPAIR\n"
                + "Session=" + sessionState + " Planner=" + PLANNER_ADAPTER + "\n"
                + "MicLease=PHONE/" + micLeaseMode + " remainMs=" + lease
                + " WebAudio grants=" + permissionGrants + " denies=" + permissionDenials + " tracks=" + activeAudioTracks + "\n"
                + "Controls D=" + dictationCount + " Vstart=" + voiceStartCount + " Vend=" + voiceEndCount
                + " M=" + muteCount + " U=" + unmuteCount + " Send=" + sendCount + " Cancel=" + cancelCount + "\n"
                + "RunState=" + runState + " AudioState=" + audioState + " ComposerLen=" + composerLen + "\n"
                + "Action=" + lastAction + " status=" + lastActionStatus);
        if (sessionButton != null) sessionButton.setText("ACTIVE".equals(sessionState) ? "SESSION END" : "SESSION START");
    }

    private void saveReport() {
        try {
            String name = "chatgpt-webview-v16-orchestrator-"
                    + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".txt";
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            cv.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
            cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (u == null) throw new IllegalStateException("insert");
            try (OutputStream out = getContentResolver().openOutputStream(u)) {
                if (out == null) throw new IllegalStateException("stream");
                out.write(reportText().getBytes(StandardCharsets.UTF_8));
            }
            Toast.makeText(this, "v0.16 report saved to Downloads", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "REPORT16 failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
        }
    }

    private String reportText() {
        StringBuilder r = new StringBuilder();
        r.append("CHATGPT_WEBVIEW_STABLE_V16_ORCHESTRATOR_TOGGLE_REPAIR\n");
        r.append("V15_FINDING=DICTATION_START_WORKED_OTHER_CONTROLS_FAILED\n");
        r.append("V16_REPAIR=DICTATION_START_AND_STOP_SHARE_DICTATION_MIC_TOGGLE\n");
        r.append("ORCHESTRATOR_ROLE=SUPERVISOR_NOT_DASHBOARD\n");
        r.append("PLANNER_ADAPTER=").append(PLANNER_ADAPTER).append('\n');
        r.append("ACTIVATION_SOURCE=").append(ACTIVATION_SOURCE).append('\n');
        r.append("SESSION_STATE=").append(sessionState).append('\n');
        r.append("SESSION_ID_PRESENT=").append(!"-".equals(sessionId)).append('\n');
        r.append("MIC_SOURCE=PHONE\n");
        r.append("MIC_LEASE_MODE=").append(micLeaseMode).append('\n');
        r.append("WEB_AUDIO_PERMISSION_REQUESTS=").append(permissionRequests).append('\n');
        r.append("WEB_AUDIO_PERMISSION_GRANTS=").append(permissionGrants).append('\n');
        r.append("WEB_AUDIO_PERMISSION_DENIALS=").append(permissionDenials).append('\n');
        r.append("MEDIA_TRACKER_INSTALLED=").append(mediaTrackerInstalled).append('\n');
        r.append("ACTIVE_AUDIO_TRACKS=").append(activeAudioTracks).append('\n');
        r.append("MEDIA_GUM_CALLS=").append(mediaGumCalls).append('\n');
        r.append("MEDIA_GUM_RESOLVES=").append(mediaGumResolves).append('\n');
        r.append("MEDIA_GUM_REJECTS=").append(mediaGumRejects).append('\n');
        r.append("CONTROL_DICTATION_COUNT=").append(dictationCount).append('\n');
        r.append("CONTROL_VOICE_START_COUNT=").append(voiceStartCount).append('\n');
        r.append("CONTROL_VOICE_END_COUNT=").append(voiceEndCount).append('\n');
        r.append("CONTROL_MUTE_COUNT=").append(muteCount).append('\n');
        r.append("CONTROL_UNMUTE_COUNT=").append(unmuteCount).append('\n');
        r.append("CONTROL_SEND_COUNT=").append(sendCount).append('\n');
        r.append("CONTROL_CANCEL_COUNT=").append(cancelCount).append('\n');
        r.append("RUN_STATE=").append(runState).append('\n');
        r.append("AUDIO_STATE=").append(audioState).append('\n');
        r.append("COMPOSER_LENGTH=").append(composerLen).append('\n');
        r.append("USER_TURN_COUNT=").append(userCount).append('\n');
        r.append("ASSISTANT_TURN_COUNT=").append(assistantCount).append('\n');
        r.append("LAST_ACTION=").append(token(lastAction)).append('\n');
        r.append("LAST_ACTION_STATUS=").append(token(lastActionStatus)).append('\n');
        r.append("UNCERTAIN_BLOCKED_ACTION=").append(token(uncertainBlockedAction)).append('\n');
        r.append("PENDING_ACTION=").append(pending == null ? "NONE" : token(pending.action)).append('\n');
        r.append("SEMANTIC_COORDINATES_USED=false\n");
        r.append("PRIVATE_CHATGPT_API_USED=false\n");
        r.append("RAW_AUDIO_RETAINED=false\n");
        r.append("RAW_SPEECH_RETAINED=false\n");
        r.append("RAW_CHAT_TEXT_RETAINED=false\n");
        r.append("--- V16 EVENT LOG ---\n").append(events);
        return r.toString();
    }

    private static JSONObject jsonObject(String value) throws Exception {
        Object x = new JSONTokener(value == null ? "null" : value).nextValue();
        if (x instanceof String) x = new JSONTokener((String) x).nextValue();
        if (!(x instanceof JSONObject)) throw new IllegalStateException("not_object");
        return (JSONObject) x;
    }

    private boolean trustedUrl(String s) {
        try {
            Uri u = Uri.parse(s == null ? "" : s);
            return "https".equalsIgnoreCase(u.getScheme()) && "chatgpt.com".equalsIgnoreCase(u.getHost());
        } catch (Exception e) { return false; }
    }

    private boolean trustedOrigin(Uri u) {
        return u != null && "https".equalsIgnoreCase(u.getScheme()) && "chatgpt.com".equalsIgnoreCase(u.getHost());
    }

    private WebView findWeb(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (!(v instanceof ViewGroup)) return null;
        ViewGroup g = (ViewGroup) v;
        for (int i = 0; i < g.getChildCount(); i++) {
            WebView w = findWeb(g.getChildAt(i));
            if (w != null) return w;
        }
        return null;
    }

    private void ev(String s) {
        if (events.length() < 30000) {
            events.append(new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date()))
                    .append(" | ").append(token(s)).append('\n');
        }
    }

    private static String token(String s) {
        String x = s == null ? "-" : s.replaceAll("[^A-Za-z0-9_.:+/@= -]", "_");
        return x.length() > 220 ? x.substring(0, 220) : x;
    }

    private static String js(String s) {
        return (s == null ? "" : s).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r");
    }

    private int dp(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }

    @Override protected void onDestroy() {
        h.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private static final class Pending {
        String action;
        String category;
        String claimId;
        boolean dispatched;
        long dispatchedAt;
        long deadlineAt;
        int baselineUserCount;
        int baselineComposerLen;
        String baselineComposerHash;
        int baselinePermissionGrants;
        int baselineActiveTracks;
    }

    private static final class Snapshot {
        String audioState = "UNKNOWN";
        Set<String> cats = new HashSet<>();
        int dictationCount;
        int voiceStartCount;
        int voiceEndCount;
        int muteCount;
        int unmuteCount;
        int sendCount;
        int cancelCount;
        int confirmCount;
        int composerLen;
        String composerHash = "-";
        int userCount;
        int assistantCount;
        int assistantLen;
        String assistantHash = "-";
        boolean runStop;
        int activeAudioTracks;
        int gumCalls;
        int gumResolves;
        int gumRejects;

        static Snapshot from(JSONObject o) {
            Snapshot s = new Snapshot();
            s.audioState = o.optString("audioState", "UNKNOWN");
            JSONArray a = o.optJSONArray("cats");
            if (a != null) for (int i = 0; i < a.length(); i++) s.cats.add(a.optString(i, ""));
            s.dictationCount = o.optInt("dictationCount", 0);
            s.voiceStartCount = o.optInt("voiceStartCount", 0);
            s.voiceEndCount = o.optInt("voiceEndCount", 0);
            s.muteCount = o.optInt("muteCount", 0);
            s.unmuteCount = o.optInt("unmuteCount", 0);
            s.sendCount = o.optInt("sendCount", 0);
            s.cancelCount = o.optInt("cancelCount", 0);
            s.confirmCount = o.optInt("confirmCount", 0);
            s.composerLen = o.optInt("composerLen", 0);
            s.composerHash = o.optString("composerHash", "-");
            s.userCount = o.optInt("userCount", 0);
            s.assistantCount = o.optInt("assistantCount", 0);
            s.assistantLen = o.optInt("assistantLen", 0);
            s.assistantHash = o.optString("assistantHash", "-");
            s.runStop = o.optBoolean("runStop", false);
            s.activeAudioTracks = o.optInt("activeAudioTracks", 0);
            s.gumCalls = o.optInt("gumCalls", 0);
            s.gumResolves = o.optInt("gumResolves", 0);
            s.gumRejects = o.optInt("gumRejects", 0);
            return s;
        }
    }

    private static final String SHARED_JS =
            "const N=x=>String(x||'').replace(/\\s+/g,' ').trim();"
            + "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
            + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
            + "const M=e=>N((e.getAttribute&&e.getAttribute('aria-label'))||'')+' '+N((e.getAttribute&&e.getAttribute('title'))||'')+' '+N((e.getAttribute&&e.getAttribute('data-testid'))||'')+' '+N(e.innerText||e.textContent||'');"
            + "const C=e=>{const x=M(e).toLowerCase();if(/unmute|turn microphone on|mic on/.test(x))return 'UNMUTE';if(/mute|turn microphone off|mic off/.test(x))return 'MUTE';if(/end voice|leave voice|exit voice|end call/.test(x))return 'VOICE_END';if(/voice mode|start voice|open voice|advanced voice/.test(x))return 'VOICE_START';if(/cancel|discard/.test(x))return 'CANCEL';if(/^send$|send message|submit/.test(x))return 'SEND';if(/confirm|done|accept|use recording/.test(x))return 'CONFIRM';if(/microphone|dictat|voice input|record audio|record message/.test(x))return 'DICTATION_MIC';if(/stop|finish recording|stop recording/.test(x))return 'STOP';return 'OTHER';};"
            + "const I=()=>[...document.querySelectorAll('button,[role=button],[aria-label]')].filter(V).map(e=>({e:e,c:C(e)})).filter(x=>x.c!=='OTHER');";

    private static final String MEDIA_TRACKER_JS =
            "(function(){try{if(window.__cp16Media)return 'EXISTS';const md=navigator.mediaDevices;if(!md||!md.getUserMedia)return 'NO_GUM';const orig=md.getUserMedia;const o={calls:0,ok:0,fail:0,tracks:new Set()};md.getUserMedia=function(c){o.calls++;let p;try{p=Reflect.apply(orig,this,[c]);}catch(e){o.fail++;throw e;}return Promise.resolve(p).then(s=>{o.ok++;try{for(const t of s.getAudioTracks()){o.tracks.add(t);t.addEventListener('ended',()=>o.tracks.delete(t),{once:true});}}catch(_){}return s;},e=>{o.fail++;throw e;});};o.snap=()=>{let n=0;for(const t of [...o.tracks]){if(t.readyState==='live')n++;else o.tracks.delete(t);}return {active:n,calls:o.calls,ok:o.ok,fail:o.fail};};window.__cp16Media=o;return 'INSTALLED';}catch(e){return 'ERR';}})();";
}
