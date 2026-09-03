package com.homayounisaghar.chatgptwebviewprobe;

import android.content.ContentValues;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.MediaStore;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.OutputStream;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.UUID;

/**
 * Stable v0.18 - Orchestrator snapshot + dictation-stop repair.
 *
 * Real-device REPORT17 proved:
 * - Dictation Start itself was confirmed after a trusted WebAudio grant.
 * - Dictation Stop then reached the resolver and aborted with MATCHES_0.
 * - v0.16 snapshot polling never produced a usable snapshot.
 *
 * Source review found a deterministic JavaScript bug in v0.16 snapshotJs():
 * SHARED_JS declares `const C` as the semantic classifier and snapshotJs declares
 * a second `const C` as a count helper in the same function scope. That is a
 * JavaScript SyntaxError, so evaluateJavascript returns no JSON object and the
 * parent logs SNAPSHOT_PARSE_FAIL_IllegalStateException forever.
 *
 * v0.18 does not rely on that broken parent snapshot. It adds a clean observer,
 * resolves Dictation.Stop against the active STOP control first with a bounded
 * fallback to the dictation toggle, makes Dictation.Send use the fresh composer
 * snapshot, and makes Session End an unconditional supervisor escape hatch.
 * No coordinates, XPath, private ChatGPT APIs, credentials, cookies or tokens.
 */
public class OrchestratorFoundationV18Activity extends OrchestratorFoundationV17Activity {
    private static final String PREFS18 = "stable_v18_orchestrator_repair";
    private static final String PREFS16 = "stable_v16_orchestrator";

    private final Handler h18 = new Handler(Looper.getMainLooper());
    private final StringBuilder events18 = new StringBuilder();
    private WebView web18;
    private TextView status18;
    private SharedPreferences prefs18;
    private SharedPreferences prefs16;

    private boolean snapOk = false;
    private int snapOkCount = 0;
    private int snapFailCount = 0;
    private int dictationCount = 0;
    private int stopCount = 0;
    private int sendCount = 0;
    private int cancelCount = 0;
    private int voiceStartCount = 0;
    private int voiceEndCount = 0;
    private int muteCount = 0;
    private int unmuteCount = 0;
    private int composerLen = 0;
    private String composerHash = "-";
    private int userCount = 0;
    private int assistantCount = 0;
    private int assistantLen = 0;
    private String assistantHash = "-";
    private boolean runStop = false;
    private String runState18 = "IDLE";
    private long assistantChangedAt = 0L;
    private boolean runCycleSeen = false;

    private Pending18 pending18;
    private String last18Action = "NONE";
    private String last18Status = "NOT_RUN";
    private int lastResolverMatches = -1;
    private int lastResolverVisibleButtons = -1;
    private String lastResolverKinds = "-";
    private int forcedSessionEnds = 0;
    private boolean lastSessionEndReloaded = false;

    private final Runnable poller18 = new Runnable() {
        @Override public void run() {
            pollSnapshot18();
            render18();
            h18.postDelayed(this, 300L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs18 = getSharedPreferences(PREFS18, MODE_PRIVATE);
        prefs16 = getSharedPreferences(PREFS16, MODE_PRIVATE);
        web18 = findWeb18(getWindow().getDecorView());
        if (web18 == null) return;
        web18.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        try { web18.getSettings().setMediaPlaybackRequiresUserGesture(false); } catch (Exception ignored) { }
        installV18PanelAndRetarget();
        ev18("V18_READY_SNAPSHOT_AND_DICTATION_STOP_REPAIR");
        h18.post(poller18);
        render18();
    }

    private void installV18PanelAndRetarget() {
        hideOldStatus(getWindow().getDecorView());
        retarget(getWindow().getDecorView());

        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) content;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        int wi = root.indexOfChild(web18);
        if (wi < 0) wi = 0;

        status18 = new TextView(this);
        status18.setTextSize(8.2f);
        status18.setTextIsSelectable(true);
        status18.setPadding(dp18(7), dp18(2), dp18(7), dp18(2));
        ScrollView sv = new ScrollView(this);
        sv.addView(status18, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));
        root.addView(sv, wi, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp18(112)));
    }

    private void hideOldStatus(View v) {
        if (v instanceof TextView && !(v instanceof Button)) {
            String t = String.valueOf(((TextView) v).getText());
            if (t.startsWith("v0.16 ORCHESTRATOR") || t.startsWith("v0.17 ORCHESTRATOR")) {
                v.setVisibility(View.GONE);
            }
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) hideOldStatus(g.getChildAt(i));
        }
    }

    private void retarget(View v) {
        if (v instanceof Button) {
            Button b = (Button) v;
            String t = String.valueOf(b.getText());
            switch (t) {
                case "SESSION START":
                case "SESSION END":
                    b.setOnClickListener(x -> sessionToggle18());
                    break;
                case "D STOP":
                    b.setOnClickListener(x -> dictationStop18());
                    break;
                case "D SEND":
                    b.setOnClickListener(x -> dictationSend18());
                    break;
                case "D CANCEL":
                    b.setOnClickListener(x -> dictationCancel18());
                    break;
                case "STATE":
                    b.setOnClickListener(x -> pollSnapshot18());
                    break;
                case "REPORT17":
                    b.setText("REPORT18");
                    b.setOnClickListener(x -> saveReport18());
                    break;
                default:
                    break;
            }
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) retarget(g.getChildAt(i));
        }
    }

    private void sessionToggle18() {
        String state = parentString("sessionState");
        if (!"ACTIVE".equals(state)) {
            try {
                invokeV16("toggleSession", new Class<?>[0], new Object[0]);
                last18Action = "SESSION_START";
                last18Status = "PARENT_START_REQUESTED";
                ev18("SESSION_START_PARENT_REQUESTED");
            } catch (Exception e) {
                last18Action = "SESSION_START";
                last18Status = "START_REFLECTION_FAIL_" + e.getClass().getSimpleName();
                ev18(last18Status);
            }
            render18();
            return;
        }
        hardEndSession18();
    }

    private void hardEndSession18() {
        boolean hadLease = !"NONE".equals(parentString("micLeaseMode"));
        boolean hadPending = parentPendingAction() != null;
        try {
            setV16Field("pending", null);
            setV16Field("uncertainBlockedAction", "NONE");
            setV16Field("micLeaseMode", "NONE");
            setV16Field("micLeaseUntil", 0L);
            setV16Field("sessionState", "IDLE");
            setV16Field("sessionId", "-");
            setV16Field("runState", "IDLE");
            setV16Field("runCycleSeen", false);
            setV16Field("lastAction", "SESSION_END");
            setV16Field("lastActionStatus", "CONFIRMED_ESCAPE_HATCH_V18");
            prefs16.edit().putString("claim_status", "ABANDONED_BY_SESSION_END").commit();
            if (pending18 != null) {
                prefs18.edit().putString("claim_status", "ABANDONED_BY_SESSION_END").commit();
                pending18 = null;
            }
            forcedSessionEnds++;
            last18Action = "SESSION_END";
            last18Status = "CONFIRMED_ESCAPE_HATCH";
            lastSessionEndReloaded = hadLease || hadPending;
            ev18("SESSION_END_ESCAPE hadLease=" + hadLease + " hadPending=" + hadPending
                    + " reload=" + lastSessionEndReloaded);
            if (lastSessionEndReloaded && web18 != null) web18.reload();
        } catch (Exception e) {
            last18Action = "SESSION_END";
            last18Status = "ESCAPE_FAIL_" + e.getClass().getSimpleName();
            ev18(last18Status);
        }
        render18();
    }

    private void dictationStop18() {
        if (!"ACTIVE".equals(parentString("sessionState"))) {
            block18("DICTATION_STOP", "SESSION_NOT_ACTIVE");
            return;
        }
        if (!"DICTATION".equals(parentString("micLeaseMode"))) {
            block18("DICTATION_STOP", "NO_DICTATION_LEASE");
            return;
        }
        if (pending18 != null) {
            block18("DICTATION_STOP", "V18_ACTION_PENDING_" + pending18.action);
            return;
        }
        releaseParentStartIfPresent("DICTATION_START");
        Pending18 op = claim18("DICTATION_STOP");
        if (op == null) return;
        op.baselineComposerLen = composerLen;
        op.baselineComposerHash = composerHash;
        op.baselineUserCount = userCount;
        op.deadlineAt = System.currentTimeMillis() + 12000L;

        web18.evaluateJavascript(resolveClickJs18("DICTATION_STOP"), value -> {
            try {
                JSONObject o = jsonObject18(value);
                lastResolverMatches = o.optInt("matches", -1);
                lastResolverVisibleButtons = o.optInt("visibleButtons", -1);
                lastResolverKinds = safe18(o.optString("kinds", "-"));
                boolean clicked = o.optBoolean("clicked", false);
                if (lastResolverMatches != 1 || !clicked) {
                    abort18(op, "MATCHES_" + lastResolverMatches + "_KINDS_" + lastResolverKinds);
                    return;
                }
                op.dispatched = true;
                op.dispatchedAt = System.currentTimeMillis();
                last18Status = "DISPATCHED_WAITING_RECEIPT";
                prefs18.edit().putString("claim_status", "DISPATCHED").commit();
                ev18("DICTATION_STOP SINGLE_SEMANTIC_CLICK kinds=" + lastResolverKinds);
                render18();
            } catch (Exception e) {
                abort18(op, "PARSE_" + e.getClass().getSimpleName());
            }
        });
    }

    private void dictationSend18() {
        if (!"ACTIVE".equals(parentString("sessionState"))) {
            block18("DICTATION_SEND", "SESSION_NOT_ACTIVE");
            return;
        }
        if (pending18 != null) {
            block18("DICTATION_SEND", "V18_ACTION_PENDING_" + pending18.action);
            return;
        }
        pollSnapshotThen(() -> {
            if (composerLen <= 0) {
                block18("DICTATION_SEND", "COMPOSER_EMPTY");
                return;
            }
            Pending18 op = claim18("DICTATION_SEND");
            if (op == null) return;
            op.baselineComposerLen = composerLen;
            op.baselineComposerHash = composerHash;
            op.baselineUserCount = userCount;
            op.deadlineAt = System.currentTimeMillis() + 10000L;
            web18.evaluateJavascript(resolveClickJs18("DICTATION_SEND"), value -> {
                try {
                    JSONObject o = jsonObject18(value);
                    lastResolverMatches = o.optInt("matches", -1);
                    lastResolverVisibleButtons = o.optInt("visibleButtons", -1);
                    lastResolverKinds = safe18(o.optString("kinds", "-"));
                    boolean clicked = o.optBoolean("clicked", false);
                    if (lastResolverMatches != 1 || !clicked) {
                        abort18(op, "MATCHES_" + lastResolverMatches + "_KINDS_" + lastResolverKinds);
                        return;
                    }
                    op.dispatched = true;
                    op.dispatchedAt = System.currentTimeMillis();
                    last18Status = "DISPATCHED_WAITING_RECEIPT";
                    prefs18.edit().putString("claim_status", "DISPATCHED").commit();
                    ev18("DICTATION_SEND SINGLE_SEMANTIC_CLICK");
                    render18();
                } catch (Exception e) {
                    abort18(op, "PARSE_" + e.getClass().getSimpleName());
                }
            });
        });
    }

    private void dictationCancel18() {
        if (!"ACTIVE".equals(parentString("sessionState"))) {
            block18("DICTATION_CANCEL", "SESSION_NOT_ACTIVE");
            return;
        }
        releaseParentStartIfPresent("DICTATION_START");
        Pending18 op = claim18("DICTATION_CANCEL");
        if (op == null) return;
        op.deadlineAt = System.currentTimeMillis() + 7000L;
        web18.evaluateJavascript(resolveClickJs18("DICTATION_CANCEL"), value -> {
            try {
                JSONObject o = jsonObject18(value);
                lastResolverMatches = o.optInt("matches", -1);
                lastResolverVisibleButtons = o.optInt("visibleButtons", -1);
                lastResolverKinds = safe18(o.optString("kinds", "-"));
                boolean clicked = o.optBoolean("clicked", false);
                if (lastResolverMatches != 1 || !clicked) {
                    abort18(op, "MATCHES_" + lastResolverMatches + "_KINDS_" + lastResolverKinds);
                    return;
                }
                op.dispatched = true;
                op.dispatchedAt = System.currentTimeMillis();
                last18Status = "DISPATCHED_WAITING_RECEIPT";
                prefs18.edit().putString("claim_status", "DISPATCHED").commit();
                ev18("DICTATION_CANCEL SINGLE_SEMANTIC_CLICK");
                render18();
            } catch (Exception e) {
                abort18(op, "PARSE_" + e.getClass().getSimpleName());
            }
        });
    }

    private Pending18 claim18(String action) {
        Pending18 op = new Pending18();
        op.action = action;
        op.claimId = action + "_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0, 8);
        boolean ok = prefs18.edit()
                .putString("claim_id", op.claimId)
                .putString("claim_action", action)
                .putString("claim_status", "CLAIMED")
                .commit();
        if (!ok) {
            block18(action, "DURABLE_CLAIM_WRITE_FAIL");
            return null;
        }
        pending18 = op;
        last18Action = action;
        last18Status = "DURABLE_CLAIMED";
        ev18(action + " DURABLE_CLAIMED");
        return op;
    }

    private void abort18(Pending18 op, String reason) {
        if (pending18 != op) return;
        pending18 = null;
        last18Action = op.action;
        last18Status = "ABORTED_NO_SIDE_EFFECT_" + safe18(reason);
        prefs18.edit().putString("claim_status", "ABORTED_NO_SIDE_EFFECT").commit();
        ev18(op.action + " ABORTED_NO_SIDE_EFFECT " + safe18(reason));
        render18();
    }

    private void confirm18(String receipt) {
        if (pending18 == null) return;
        String action = pending18.action;
        pending18 = null;
        last18Action = action;
        last18Status = "CONFIRMED_" + safe18(receipt);
        prefs18.edit().putString("claim_status", "CONFIRMED")
                .putString("claim_receipt", safe18(receipt)).commit();
        if ("DICTATION_STOP".equals(action) || "DICTATION_CANCEL".equals(action)) {
            try { invokeV16("revokeLease", new Class<?>[]{String.class}, new Object[]{"V18_" + action}); }
            catch (Exception e) {
                try { setV16Field("micLeaseMode", "NONE"); setV16Field("micLeaseUntil", 0L); }
                catch (Exception ignored) { }
            }
        }
        ev18(action + " CONFIRMED " + safe18(receipt));
        render18();
    }

    private void uncertain18(String reason) {
        if (pending18 == null) return;
        String action = pending18.action;
        pending18 = null;
        last18Action = action;
        last18Status = "UNCERTAIN_" + safe18(reason);
        prefs18.edit().putString("claim_status", "UNCERTAIN")
                .putString("claim_receipt", safe18(reason)).commit();
        ev18(action + " UNCERTAIN_NO_REPLAY " + safe18(reason));
        render18();
    }

    private void block18(String action, String reason) {
        last18Action = action;
        last18Status = "BLOCKED_" + safe18(reason);
        ev18(action + " BLOCKED " + safe18(reason));
        render18();
    }

    private void pollSnapshotThen(Runnable next) {
        if (web18 == null) return;
        web18.evaluateJavascript(snapshotJs18(), value -> {
            consumeSnapshot18(value);
            if (next != null) next.run();
        });
    }

    private void pollSnapshot18() {
        if (web18 == null) return;
        String url = web18.getUrl();
        if (url == null || !url.startsWith("https://chatgpt.com")) return;
        web18.evaluateJavascript(snapshotJs18(), this::consumeSnapshot18);
    }

    private void consumeSnapshot18(String value) {
        try {
            JSONObject o = jsonObject18(value);
            if (o.has("error")) throw new IllegalStateException(o.optString("error"));
            snapOk = true;
            snapOkCount++;

            int oldUser = userCount;
            int oldAssistantCount = assistantCount;
            int oldAssistantLen = assistantLen;
            String oldAssistantHash = assistantHash;

            dictationCount = o.optInt("dictationCount", 0);
            stopCount = o.optInt("stopCount", 0);
            sendCount = o.optInt("sendCount", 0);
            cancelCount = o.optInt("cancelCount", 0);
            voiceStartCount = o.optInt("voiceStartCount", 0);
            voiceEndCount = o.optInt("voiceEndCount", 0);
            muteCount = o.optInt("muteCount", 0);
            unmuteCount = o.optInt("unmuteCount", 0);
            composerLen = o.optInt("composerLen", 0);
            composerHash = safe18(o.optString("composerHash", "-"));
            userCount = o.optInt("userCount", 0);
            assistantCount = o.optInt("assistantCount", 0);
            assistantLen = o.optInt("assistantLen", 0);
            assistantHash = safe18(o.optString("assistantHash", "-"));
            runStop = o.optBoolean("runStop", false);

            long now = System.currentTimeMillis();
            if (userCount > oldUser) {
                runCycleSeen = true;
                runState18 = "ACTIVE";
                ev18("RUN_USER_TURN count=" + userCount);
            }
            boolean assistantChanged = assistantCount != oldAssistantCount
                    || assistantLen != oldAssistantLen || !assistantHash.equals(oldAssistantHash);
            if (assistantChanged) {
                assistantChangedAt = now;
                if (runCycleSeen || runStop) runState18 = "STREAMING";
            }
            if (runStop) {
                runCycleSeen = true;
                runState18 = assistantChanged || (assistantChangedAt > 0 && now - assistantChangedAt < 2500L)
                        ? "STREAMING" : "ACTIVE";
            } else if (runCycleSeen && assistantChangedAt > 0 && now - assistantChangedAt > 2800L) {
                runState18 = "COMPLETE";
                runCycleSeen = false;
            }

            checkPending18(now);
        } catch (Exception e) {
            snapOk = false;
            snapFailCount++;
            if (snapFailCount <= 6 || snapFailCount % 20 == 0) {
                ev18("SNAPSHOT18_FAIL_" + e.getClass().getSimpleName());
            }
        }
        render18();
    }

    private void checkPending18(long now) {
        if (pending18 == null || !pending18.dispatched) return;
        Pending18 op = pending18;
        long age = now - op.dispatchedAt;
        if ("DICTATION_STOP".equals(op.action)) {
            if (composerLen > 0 && (composerLen != op.baselineComposerLen
                    || !composerHash.equals(op.baselineComposerHash))) {
                confirm18("TRANSCRIPT_IN_COMPOSER");
                return;
            }
            if (age > 450L && stopCount == 0 && dictationCount == 1) {
                confirm18("STOP_CONTROL_GONE_READY_DICTATION_RETURNED");
                return;
            }
        } else if ("DICTATION_SEND".equals(op.action)) {
            if (userCount > op.baselineUserCount && composerLen == 0) {
                confirm18("USER_TURN_RECEIPT");
                return;
            }
        } else if ("DICTATION_CANCEL".equals(op.action)) {
            if (age > 450L && cancelCount == 0 && stopCount == 0) {
                confirm18("CANCEL_CONTROL_GONE");
                return;
            }
        }
        if (now > op.deadlineAt) uncertain18("RECEIPT_TIMEOUT");
    }

    private String resolveClickJs18(String action) {
        return "(function(){try{"
                + rootsJs18()
                + "const A='" + js18(action) + "';"
                + "const C=e=>{const x=M(e);"
                + "if(/unmute|turn microphone on|mic on|microphone on/.test(x))return 'UNMUTE';"
                + "if(/(^|[^a-z])mute([^a-z]|$)|turn microphone off|mic off|microphone off/.test(x))return 'MUTE';"
                + "if(/end voice|leave voice|exit voice|close voice|end call|hang up|disconnect/.test(x))return 'VOICE_END';"
                + "if(/voice mode|start voice|open voice|advanced voice/.test(x))return 'VOICE_START';"
                + "if(/cancel|discard/.test(x))return 'CANCEL';"
                + "if(/stop recording|finish recording|end recording|stop dictation|stop listening|(^|[^a-z])stop([^a-z]|$)/.test(x)&&!/stop generating|stop response/.test(x))return 'STOP';"
                + "if(/send prompt|send message|submit|(^|[^a-z])send([^a-z]|$)/.test(x))return 'SEND';"
                + "if(/microphone|dictat|voice input|record audio|record message/.test(x))return 'DICTATION_MIC';"
                + "return 'OTHER';};"
                + "const tagged=els.map(e=>({e:e,c:C(e)}));let xs=[];"
                + "if(A==='DICTATION_STOP'){const p=tagged.filter(x=>x.c==='STOP');xs=p.length?p:tagged.filter(x=>x.c==='DICTATION_MIC');}"
                + "else if(A==='DICTATION_SEND')xs=tagged.filter(x=>x.c==='SEND');"
                + "else if(A==='DICTATION_CANCEL')xs=tagged.filter(x=>x.c==='CANCEL');"
                + "const ks=['DICTATION_MIC','STOP','SEND','CANCEL','VOICE_START','VOICE_END','MUTE','UNMUTE'].map(k=>k+':'+tagged.filter(x=>x.c===k).length).join(',');"
                + "let did=false;if(xs.length===1){xs[0].e.click();did=true;}"
                + "return JSON.stringify({matches:xs.length,clicked:did,visibleButtons:els.length,kinds:ks});"
                + "}catch(e){return JSON.stringify({matches:-1,clicked:false,visibleButtons:-1,kinds:'ERR',error:String(e&&e.name||'ERR')});}})();";
    }

    private String snapshotJs18() {
        return "(function(){try{"
                + rootsJs18()
                + "const C=e=>{const x=M(e);"
                + "if(/unmute|turn microphone on|mic on|microphone on/.test(x))return 'UNMUTE';"
                + "if(/(^|[^a-z])mute([^a-z]|$)|turn microphone off|mic off|microphone off/.test(x))return 'MUTE';"
                + "if(/end voice|leave voice|exit voice|close voice|end call|hang up|disconnect/.test(x))return 'VOICE_END';"
                + "if(/voice mode|start voice|open voice|advanced voice/.test(x))return 'VOICE_START';"
                + "if(/cancel|discard/.test(x))return 'CANCEL';"
                + "if(/stop recording|finish recording|end recording|stop dictation|stop listening|(^|[^a-z])stop([^a-z]|$)/.test(x)&&!/stop generating|stop response/.test(x))return 'STOP';"
                + "if(/send prompt|send message|submit|(^|[^a-z])send([^a-z]|$)/.test(x))return 'SEND';"
                + "if(/microphone|dictat|voice input|record audio|record message/.test(x))return 'DICTATION_MIC';return 'OTHER';};"
                + "const cs=els.map(e=>C(e));const CNT=k=>cs.filter(x=>x===k).length;"
                + "const ed=[...document.querySelectorAll('#prompt-textarea,textarea,[contenteditable=true]')].filter(V);const ce=ed.length?ed[ed.length-1]:null;"
                + "const ct=ce?N(typeof ce.value==='string'?ce.value:(ce.innerText||ce.textContent||'')):'';"
                + "const us=[...document.querySelectorAll('[data-message-author-role=user]')];const as=[...document.querySelectorAll('[data-message-author-role=assistant]')];"
                + "let al=0,ah='-';if(as.length){const t=N(as[as.length-1].innerText||as[as.length-1].textContent||'');al=t.length;ah=H(t);}"
                + "const rs=els.some(e=>/stop generating|stop response|stop-button|stop_response/.test(M(e)));"
                + "return JSON.stringify({dictationCount:CNT('DICTATION_MIC'),stopCount:CNT('STOP'),sendCount:CNT('SEND'),cancelCount:CNT('CANCEL'),voiceStartCount:CNT('VOICE_START'),voiceEndCount:CNT('VOICE_END'),muteCount:CNT('MUTE'),unmuteCount:CNT('UNMUTE'),composerLen:ct.length,composerHash:ct?H(ct):'-',userCount:us.length,assistantCount:as.length,assistantLen:al,assistantHash:ah,runStop:rs});"
                + "}catch(e){return JSON.stringify({error:String(e&&e.name||'ERR')});}})();";
    }

    private String rootsJs18() {
        return "const N=x=>String(x||'').replace(/\\s+/g,' ').trim();"
                + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "const V=e=>{try{const r=e.getBoundingClientRect();const w=e.ownerDocument&&e.ownerDocument.defaultView;const s=w?w.getComputedStyle(e):getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
                + "const M=e=>{let z='';try{z+=' '+N(e.getAttribute('aria-label'))+' '+N(e.getAttribute('title'))+' '+N(e.getAttribute('data-testid'))+' '+N(e.getAttribute('name'))+' '+N(e.getAttribute('id'))+' '+N(e.getAttribute('data-state'))+' '+N(e.innerText||e.textContent||'');const st=e.querySelector&&e.querySelector('svg title');if(st)z+=' '+N(st.textContent||'');}catch(_){}return N(z).toLowerCase();};"
                + "const roots=[document],seenRoots=new Set(),seenEls=new Set(),els=[];for(let q=0;q<roots.length&&q<64;q++){const r=roots[q];if(!r||seenRoots.has(r))continue;seenRoots.add(r);let all=[];try{all=[...r.querySelectorAll('*')];}catch(_){}for(const e of all){try{if(e.shadowRoot)roots.push(e.shadowRoot);if(e.tagName==='IFRAME'&&e.contentDocument)roots.push(e.contentDocument);}catch(_){}}let bs=[];try{bs=[...r.querySelectorAll('button,[role=button],[aria-label],[data-testid]')];}catch(_){}for(const e of bs){if(!seenEls.has(e)&&V(e)){seenEls.add(e);els.push(e);}}}";
    }

    private void releaseParentStartIfPresent(String action) {
        try {
            Object p = getV16Field("pending");
            if (p == null) return;
            Field af = p.getClass().getDeclaredField("action");
            af.setAccessible(true);
            String pa = String.valueOf(af.get(p));
            if (!action.equals(pa)) return;
            Field df = p.getClass().getDeclaredField("dispatched");
            df.setAccessible(true);
            boolean dispatched = df.getBoolean(p);
            if (!dispatched) return;
            setV16Field("pending", null);
            setV16Field("lastAction", action);
            setV16Field("lastActionStatus", "ACCEPTED_REVERSIBLE_START_FOR_V18_INVERSE");
            prefs16.edit().putString("claim_status", "ACCEPTED_REVERSIBLE_START").commit();
            ev18(action + " RELEASED_FOR_SAFE_INVERSE");
        } catch (Exception e) {
            ev18("RELEASE_PARENT_START_FAIL_" + e.getClass().getSimpleName());
        }
    }

    private String parentPendingAction() {
        try {
            Object p = getV16Field("pending");
            if (p == null) return null;
            Field f = p.getClass().getDeclaredField("action");
            f.setAccessible(true);
            return String.valueOf(f.get(p));
        } catch (Exception e) { return "ERR"; }
    }

    private Object invokeV16(String name, Class<?>[] sig, Object[] args) throws Exception {
        Method m = OrchestratorFoundationV16Activity.class.getDeclaredMethod(name, sig);
        m.setAccessible(true);
        return m.invoke(this, args);
    }

    private Object getV16Field(String name) throws Exception {
        Field f = OrchestratorFoundationV16Activity.class.getDeclaredField(name);
        f.setAccessible(true);
        return f.get(this);
    }

    private void setV16Field(String name, Object value) throws Exception {
        Field f = OrchestratorFoundationV16Activity.class.getDeclaredField(name);
        f.setAccessible(true);
        f.set(this, value);
    }

    private String parentString(String name) {
        try { return String.valueOf(getV16Field(name)); }
        catch (Exception e) { return "ERR"; }
    }

    private void render18() {
        if (status18 == null) return;
        status18.setText("v0.18 ORCHESTRATOR - SNAPSHOT + DICTATION STOP REPAIR\n"
                + "Session=" + parentString("sessionState") + " MicLease=PHONE/" + parentString("micLeaseMode")
                + " Snapshot=" + (snapOk ? "OK" : "FAIL") + " ok/fail=" + snapOkCount + "/" + snapFailCount + "\n"
                + "Controls D=" + dictationCount + " Stop=" + stopCount + " Send=" + sendCount + " Cancel=" + cancelCount
                + " Vstart=" + voiceStartCount + " Vend=" + voiceEndCount + " M=" + muteCount + " U=" + unmuteCount + "\n"
                + "ComposerLen=" + composerLen + " RunState=" + runState18 + " ParentPending="
                + (parentPendingAction() == null ? "NONE" : parentPendingAction()) + "\n"
                + "Action=" + last18Action + " status=" + last18Status
                + " resolverMatches=" + lastResolverMatches + " visibleBtns=" + lastResolverVisibleButtons);
    }

    private void saveReport18() {
        try {
            String name = "chatgpt-webview-v18-orchestrator-repair-"
                    + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".txt";
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            cv.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
            cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (u == null) throw new IllegalStateException("insert");
            try (OutputStream out = getContentResolver().openOutputStream(u)) {
                if (out == null) throw new IllegalStateException("stream");
                out.write(reportText18().getBytes(StandardCharsets.UTF_8));
            }
            Toast.makeText(this, "v0.18 report saved to Downloads", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "REPORT18 failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
        }
    }

    private String reportText18() {
        StringBuilder r = new StringBuilder();
        r.append("CHATGPT_WEBVIEW_STABLE_V18_ORCHESTRATOR_SNAPSHOT_DICTATION_REPAIR\n");
        r.append("REPORT17_FACT_D_START_CONFIRMED=true\n");
        r.append("REPORT17_FACT_D_STOP_MATCHES_0=true\n");
        r.append("REPORT17_FACT_PARENT_SNAPSHOT_PARSE_FAIL_REPEATED=true\n");
        r.append("V16_SNAPSHOT_SOURCE_BUG=DUPLICATE_CONST_C_IN_SAME_FUNCTION_SCOPE\n");
        r.append("V18_USES_INDEPENDENT_FIXED_SNAPSHOT=true\n");
        r.append("V18_DICTATION_STOP_RESOLVER=STOP_FIRST_THEN_DICTATION_TOGGLE_FALLBACK\n");
        r.append("SESSION_END_ESCAPE_HATCH=true\n");
        r.append("SESSION_STATE=").append(parentString("sessionState")).append('\n');
        r.append("MIC_LEASE_MODE=").append(parentString("micLeaseMode")).append('\n');
        r.append("SNAPSHOT_OK=").append(snapOk).append('\n');
        r.append("SNAPSHOT_OK_COUNT=").append(snapOkCount).append('\n');
        r.append("SNAPSHOT_FAIL_COUNT=").append(snapFailCount).append('\n');
        r.append("CONTROL_DICTATION_COUNT=").append(dictationCount).append('\n');
        r.append("CONTROL_STOP_COUNT=").append(stopCount).append('\n');
        r.append("CONTROL_SEND_COUNT=").append(sendCount).append('\n');
        r.append("CONTROL_CANCEL_COUNT=").append(cancelCount).append('\n');
        r.append("CONTROL_VOICE_START_COUNT=").append(voiceStartCount).append('\n');
        r.append("CONTROL_VOICE_END_COUNT=").append(voiceEndCount).append('\n');
        r.append("CONTROL_MUTE_COUNT=").append(muteCount).append('\n');
        r.append("CONTROL_UNMUTE_COUNT=").append(unmuteCount).append('\n');
        r.append("COMPOSER_LENGTH=").append(composerLen).append('\n');
        r.append("COMPOSER_HASH=").append(composerHash).append('\n');
        r.append("USER_TURN_COUNT=").append(userCount).append('\n');
        r.append("ASSISTANT_TURN_COUNT=").append(assistantCount).append('\n');
        r.append("LAST_ASSISTANT_LENGTH=").append(assistantLen).append('\n');
        r.append("LAST_ASSISTANT_HASH=").append(assistantHash).append('\n');
        r.append("RUN_STATE=").append(runState18).append('\n');
        r.append("RUN_STOP_PRESENT=").append(runStop).append('\n');
        r.append("V18_PENDING_ACTION=").append(pending18 == null ? "NONE" : safe18(pending18.action)).append('\n');
        r.append("PARENT_PENDING_ACTION=").append(parentPendingAction() == null ? "NONE" : safe18(parentPendingAction())).append('\n');
        r.append("LAST_ACTION=").append(safe18(last18Action)).append('\n');
        r.append("LAST_ACTION_STATUS=").append(safe18(last18Status)).append('\n');
        r.append("LAST_RESOLVER_MATCHES=").append(lastResolverMatches).append('\n');
        r.append("LAST_RESOLVER_VISIBLE_BUTTONS=").append(lastResolverVisibleButtons).append('\n');
        r.append("LAST_RESOLVER_KINDS=").append(safe18(lastResolverKinds)).append('\n');
        r.append("FORCED_SESSION_END_COUNT=").append(forcedSessionEnds).append('\n');
        r.append("LAST_SESSION_END_RELOADED=").append(lastSessionEndReloaded).append('\n');
        r.append("SEMANTIC_SHADOW_AND_SAME_ORIGIN_FRAME_FALLBACK=true\n");
        r.append("COORDINATE_ACTIONS_USED=false\n");
        r.append("PRIVATE_CHATGPT_API_USED=false\n");
        r.append("RAW_AUDIO_RETAINED=false\n");
        r.append("RAW_SPEECH_RETAINED=false\n");
        r.append("RAW_CHAT_TEXT_RETAINED=false\n");
        r.append("--- V18 EVENT LOG ---\n").append(events18);
        return r.toString();
    }

    private static JSONObject jsonObject18(String value) throws Exception {
        Object x = new JSONTokener(value == null ? "null" : value).nextValue();
        if (x instanceof String) x = new JSONTokener((String) x).nextValue();
        if (!(x instanceof JSONObject)) throw new IllegalStateException("not_object");
        return (JSONObject) x;
    }

    private WebView findWeb18(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (!(v instanceof ViewGroup)) return null;
        ViewGroup g = (ViewGroup) v;
        for (int i = 0; i < g.getChildCount(); i++) {
            WebView w = findWeb18(g.getChildAt(i));
            if (w != null) return w;
        }
        return null;
    }

    private void ev18(String s) {
        if (events18.length() < 30000) {
            events18.append(new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date()))
                    .append(" | ").append(safe18(s)).append('\n');
        }
    }

    private static String safe18(String s) {
        String x = s == null ? "-" : s.replaceAll("[^A-Za-z0-9_.:+/@=, -]", "_");
        return x.length() > 260 ? x.substring(0, 260) : x;
    }

    private static String js18(String s) {
        return (s == null ? "" : s).replace("\\", "\\\\").replace("'", "\\'")
                .replace("\n", "\\n").replace("\r", "\\r");
    }

    private int dp18(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }

    @Override protected void onDestroy() {
        h18.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    private static final class Pending18 {
        String action;
        String claimId;
        boolean dispatched;
        long dispatchedAt;
        long deadlineAt;
        int baselineComposerLen;
        String baselineComposerHash = "-";
        int baselineUserCount;
    }
}
