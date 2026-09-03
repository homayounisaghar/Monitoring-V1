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

/**
 * Stable v0.17 - Orchestrator start-lock + WebView media-playback repair.
 *
 * Real-device v0.16 evidence showed two independent adapter problems:
 * 1) a successful native Dictation/Voice Start could remain globally pending when
 *    the late media tracker did not observe a fresh track/permission receipt, so
 *    safe inverse controls were blocked by OTHER_ACTION_PENDING_*;
 * 2) native Voice Start entered ChatGPT Voice UI but WebView showed
 *    "Audio playback was blocked. Tap or click to resume", which is consistent
 *    with media playback still requiring a browser gesture after native -> JS click.
 *
 * v0.17 keeps the v0.16 deterministic supervisor and adds a thin compatibility
 * adapter: unique semantic Start dispatch is allowed to enter an explicit
 * ACCEPTED_REVERSIBLE_START state after a bounded delay (not falsely called a
 * confirmed media receipt), paired safe inverse actions can supersede that start,
 * and WebView media playback no longer requires a user gesture. Voice mute/end
 * also get a bounded semantic fallback that traverses open shadow roots and
 * same-origin frames; ambiguity still fails closed and no coordinates are used.
 */
public class OrchestratorFoundationV17Activity extends OrchestratorFoundationV16Activity {
    private static final String PREFS16 = "stable_v16_orchestrator";
    private static final String PREFS17 = "stable_v17_orchestrator_wrapper";

    private final Handler h17 = new Handler(Looper.getMainLooper());
    private final StringBuilder events17 = new StringBuilder();
    private WebView web17;
    private TextView status17;
    private SharedPreferences prefs16;
    private SharedPreferences prefs17;

    private boolean mediaPlaybackGestureBypass = false;
    private int acceptedReversibleStarts = 0;
    private int inverseUnlocks = 0;
    private String lastWrapperAction = "NONE";
    private String lastWrapperStatus = "NOT_RUN";
    private String lastRobustVoiceAction = "NONE";
    private String lastRobustVoiceStatus = "NOT_RUN";
    private int lastRobustVoiceMatches = -1;
    private int lastRobustVoiceVisibleButtons = -1;

    private final Runnable tick17 = new Runnable() {
        @Override public void run() {
            autoAcceptStartIfNeeded("DICTATION_START", 850L);
            autoAcceptStartIfNeeded("VOICE_START", 1100L);
            render17();
            h17.postDelayed(this, 300L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs16 = getSharedPreferences(PREFS16, MODE_PRIVATE);
        prefs17 = getSharedPreferences(PREFS17, MODE_PRIVATE);
        web17 = findWeb17(getWindow().getDecorView());
        if (web17 == null) return;
        web17.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        try {
            web17.getSettings().setMediaPlaybackRequiresUserGesture(false);
            mediaPlaybackGestureBypass = !web17.getSettings().getMediaPlaybackRequiresUserGesture();
        } catch (Exception e) {
            mediaPlaybackGestureBypass = false;
            ev17("MEDIA_PLAYBACK_GESTURE_SETTING_FAIL_" + e.getClass().getSimpleName());
        }
        installV17PanelAndRetargetButtons();
        ev17("V17_READY_START_LOCK_AND_MEDIA_PLAYBACK_REPAIR bypass=" + mediaPlaybackGestureBypass);
        h17.post(tick17);
        render17();
    }

    private void installV17PanelAndRetargetButtons() {
        hideV16Status(getWindow().getDecorView());
        retargetButtons(getWindow().getDecorView());

        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) content;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        int wi = root.indexOfChild(web17);
        if (wi < 0) wi = 0;

        status17 = new TextView(this);
        status17.setTextSize(8.3f);
        status17.setTextIsSelectable(true);
        status17.setPadding(dp17(7), dp17(2), dp17(7), dp17(2));
        ScrollView sv = new ScrollView(this);
        sv.addView(status17, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));
        root.addView(sv, wi, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp17(96)));
    }

    private void hideV16Status(View v) {
        if (v instanceof TextView && !(v instanceof Button)) {
            String t = String.valueOf(((TextView) v).getText());
            if (t.startsWith("v0.16 ORCHESTRATOR")) v.setVisibility(View.GONE);
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) hideV16Status(g.getChildAt(i));
        }
    }

    private void retargetButtons(View v) {
        if (v instanceof Button) {
            Button b = (Button) v;
            String t = String.valueOf(b.getText());
            switch (t) {
                case "D START":
                    b.setOnClickListener(x -> {
                        lastWrapperAction = "DICTATION_START";
                        lastWrapperStatus = "DISPATCH_REQUESTED";
                        invokeParentDispatch("DICTATION_START");
                        h17.postDelayed(() -> autoAcceptStartIfNeeded("DICTATION_START", 0L), 900L);
                    });
                    break;
                case "D STOP":
                    b.setOnClickListener(x -> {
                        releaseStartForSafeInverse("DICTATION_START", "DICTATION_STOP");
                        lastWrapperAction = "DICTATION_STOP";
                        lastWrapperStatus = "DISPATCH_REQUESTED";
                        invokeParentDispatch("DICTATION_STOP");
                    });
                    break;
                case "D CANCEL":
                    b.setOnClickListener(x -> {
                        releaseStartForSafeInverse("DICTATION_START", "DICTATION_CANCEL");
                        lastWrapperAction = "DICTATION_CANCEL";
                        lastWrapperStatus = "DISPATCH_REQUESTED";
                        invokeParentDispatch("DICTATION_CANCEL");
                    });
                    break;
                case "D SEND":
                    b.setOnClickListener(x -> {
                        lastWrapperAction = "DICTATION_SEND";
                        lastWrapperStatus = "DISPATCH_REQUESTED";
                        invokeParentDispatch("DICTATION_SEND");
                    });
                    break;
                case "V START":
                    b.setOnClickListener(x -> {
                        ensureMediaPlaybackBypass();
                        lastWrapperAction = "VOICE_START";
                        lastWrapperStatus = "DISPATCH_REQUESTED";
                        invokeParentDispatch("VOICE_START");
                        h17.postDelayed(() -> autoAcceptStartIfNeeded("VOICE_START", 0L), 1150L);
                    });
                    break;
                case "V MUTE":
                    b.setOnClickListener(x -> {
                        releaseStartForSafeInverse("VOICE_START", "VOICE_MUTE");
                        robustVoiceAction("VOICE_MUTE");
                    });
                    break;
                case "V UNMUTE":
                    b.setOnClickListener(x -> {
                        releaseStartForSafeInverse("VOICE_START", "VOICE_UNMUTE");
                        robustVoiceAction("VOICE_UNMUTE");
                    });
                    break;
                case "V END":
                    b.setOnClickListener(x -> {
                        releaseStartForSafeInverse("VOICE_START", "VOICE_END");
                        robustVoiceAction("VOICE_END");
                    });
                    break;
                case "STATE":
                    b.setOnClickListener(x -> {
                        invokeParentNoArg("pollSnapshot");
                        render17();
                    });
                    break;
                case "REPORT16":
                    b.setText("REPORT17");
                    b.setOnClickListener(x -> saveReport17());
                    break;
                default:
                    break;
            }
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) retargetButtons(g.getChildAt(i));
        }
    }

    private void ensureMediaPlaybackBypass() {
        try {
            web17.getSettings().setMediaPlaybackRequiresUserGesture(false);
            mediaPlaybackGestureBypass = !web17.getSettings().getMediaPlaybackRequiresUserGesture();
            ev17("MEDIA_PLAYBACK_REQUIRES_GESTURE=" + !mediaPlaybackGestureBypass);
        } catch (Exception e) {
            mediaPlaybackGestureBypass = false;
            ev17("MEDIA_PLAYBACK_GESTURE_REAPPLY_FAIL_" + e.getClass().getSimpleName());
        }
    }

    private void autoAcceptStartIfNeeded(String action, long minAgeMs) {
        try {
            Object p = getParentField("pending");
            if (p == null) return;
            String pa = String.valueOf(getObjectField(p, "action"));
            if (!action.equals(pa)) return;
            boolean dispatched = getBooleanField(p, "dispatched");
            if (!dispatched) return;
            long dispatchedAt = getLongField(p, "dispatchedAt");
            long age = Math.max(0L, System.currentTimeMillis() - dispatchedAt);
            if (age < minAgeMs) return;

            int baseGrants = getIntField(p, "baselinePermissionGrants");
            int baseTracks = getIntField(p, "baselineActiveTracks");
            int grants = intParent("permissionGrants");
            int tracks = intParent("activeAudioTracks");
            if (grants > baseGrants || tracks > baseTracks) {
                invokeParentConfirm("V17_OBSERVED_START_RECEIPT");
                lastWrapperAction = action;
                lastWrapperStatus = "CONFIRMED_OBSERVED_START_RECEIPT";
                ev17(action + " CONFIRMED_OBSERVED_START_RECEIPT");
                return;
            }

            setParentField("pending", null);
            setParentField("lastAction", action);
            setParentField("lastActionStatus", "ACCEPTED_REVERSIBLE_START_V17");
            prefs16.edit().putString("claim_status", "ACCEPTED_REVERSIBLE_START").commit();
            acceptedReversibleStarts++;
            lastWrapperAction = action;
            lastWrapperStatus = "ACCEPTED_REVERSIBLE_START";
            ev17(action + " ACCEPTED_REVERSIBLE_START unique_dispatch=true ageMs=" + age);
        } catch (Exception e) {
            ev17("AUTO_ACCEPT_FAIL_" + action + "_" + e.getClass().getSimpleName());
        }
    }

    private void releaseStartForSafeInverse(String startAction, String inverseAction) {
        try {
            Object p = getParentField("pending");
            if (p == null) return;
            String pa = String.valueOf(getObjectField(p, "action"));
            if (!startAction.equals(pa)) return;
            boolean dispatched = getBooleanField(p, "dispatched");
            if (!dispatched) return;
            setParentField("pending", null);
            setParentField("lastAction", startAction);
            setParentField("lastActionStatus", "ACCEPTED_REVERSIBLE_START_FOR_SAFE_INVERSE_V17");
            prefs16.edit().putString("claim_status", "ACCEPTED_REVERSIBLE_START").commit();
            acceptedReversibleStarts++;
            inverseUnlocks++;
            ev17(startAction + " ACCEPTED_FOR_SAFE_INVERSE next=" + inverseAction);
        } catch (Exception e) {
            ev17("SAFE_INVERSE_UNLOCK_FAIL_" + e.getClass().getSimpleName());
        }
    }

    private void robustVoiceAction(String action) {
        lastWrapperAction = action;
        lastWrapperStatus = "ROBUST_VOICE_RESOLVING";
        lastRobustVoiceAction = action;
        lastRobustVoiceStatus = "RESOLVING";
        if (!"LIVE".equals(strParent("micLeaseMode"))) {
            lastRobustVoiceStatus = "BLOCKED_NO_LIVE_LEASE";
            lastWrapperStatus = lastRobustVoiceStatus;
            ev17(action + " BLOCKED_NO_LIVE_LEASE");
            render17();
            return;
        }

        String claimId = action + "_" + System.currentTimeMillis();
        boolean durable = prefs17.edit()
                .putString("voice_claim_id", claimId)
                .putString("voice_claim_action", action)
                .putString("voice_claim_status", "CLAIMED")
                .commit();
        if (!durable) {
            lastRobustVoiceStatus = "BLOCKED_CLAIM_WRITE_FAIL";
            lastWrapperStatus = lastRobustVoiceStatus;
            render17();
            return;
        }

        web17.evaluateJavascript(robustVoiceJs(action, true), value -> {
            try {
                JSONObject o = jsonObject17(value);
                int matches = o.optInt("matches", -1);
                int visibleButtons = o.optInt("visibleButtons", -1);
                boolean clicked = o.optBoolean("clicked", false);
                lastRobustVoiceMatches = matches;
                lastRobustVoiceVisibleButtons = visibleButtons;
                if (matches == 1 && clicked) {
                    prefs17.edit().putString("voice_claim_status", "DISPATCHED").commit();
                    lastRobustVoiceStatus = "DISPATCHED_WAITING_SEMANTIC_RECEIPT";
                    lastWrapperStatus = lastRobustVoiceStatus;
                    ev17(action + " ROBUST_SINGLE_CLICK_DISPATCHED visibleButtons=" + visibleButtons);
                    h17.postDelayed(() -> verifyRobustVoiceAction(action), 650L);
                    render17();
                    return;
                }
                if (matches == 0) {
                    prefs17.edit().putString("voice_claim_status", "ABORTED_NO_SIDE_EFFECT").commit();
                    lastRobustVoiceStatus = "ROBUST_MATCHES_0_FALLBACK_PARENT";
                    lastWrapperStatus = lastRobustVoiceStatus;
                    ev17(action + " ROBUST_MATCHES_0_FALLBACK_PARENT visibleButtons=" + visibleButtons);
                    invokeParentDispatch(action);
                    render17();
                    return;
                }
                prefs17.edit().putString("voice_claim_status", "ABORTED_AMBIGUOUS_NO_SIDE_EFFECT").commit();
                lastRobustVoiceStatus = "ABORTED_AMBIGUOUS_MATCHES_" + matches;
                lastWrapperStatus = lastRobustVoiceStatus;
                ev17(action + " ABORTED_AMBIGUOUS matches=" + matches + " visibleButtons=" + visibleButtons);
                render17();
            } catch (Exception e) {
                prefs17.edit().putString("voice_claim_status", "ABORTED_PARSE_NO_SIDE_EFFECT").commit();
                lastRobustVoiceStatus = "ABORTED_PARSE_" + e.getClass().getSimpleName();
                lastWrapperStatus = lastRobustVoiceStatus;
                render17();
            }
        });
    }

    private void verifyRobustVoiceAction(String action) {
        String opposite;
        if ("VOICE_MUTE".equals(action)) opposite = "VOICE_UNMUTE";
        else if ("VOICE_UNMUTE".equals(action)) opposite = "VOICE_MUTE";
        else opposite = "VOICE_END";

        web17.evaluateJavascript(robustVoiceJs(opposite, false), value -> {
            try {
                JSONObject o = jsonObject17(value);
                int matches = o.optInt("matches", -1);
                if ("VOICE_END".equals(action)) {
                    if (matches == 0) {
                        prefs17.edit().putString("voice_claim_status", "CONFIRMED").commit();
                        lastRobustVoiceStatus = "CONFIRMED_VOICE_END_CONTROL_GONE";
                        lastWrapperStatus = lastRobustVoiceStatus;
                        invokeParentPrivate("revokeLease", new Class<?>[]{String.class}, new Object[]{"V17_ROBUST_VOICE_END"});
                        ev17("VOICE_END CONFIRMED_CONTROL_GONE");
                    } else {
                        prefs17.edit().putString("voice_claim_status", "ACCEPTED_REVERSIBLE").commit();
                        lastRobustVoiceStatus = "ACCEPTED_END_CLICK_RECEIPT_NOT_YET_SEEN";
                        lastWrapperStatus = lastRobustVoiceStatus;
                    }
                } else if (matches == 1) {
                    prefs17.edit().putString("voice_claim_status", "CONFIRMED").commit();
                    lastRobustVoiceStatus = "CONFIRMED_OPPOSITE_CONTROL_VISIBLE";
                    lastWrapperStatus = lastRobustVoiceStatus;
                    ev17(action + " CONFIRMED_OPPOSITE_CONTROL_VISIBLE");
                } else {
                    prefs17.edit().putString("voice_claim_status", "ACCEPTED_REVERSIBLE").commit();
                    lastRobustVoiceStatus = "ACCEPTED_CLICK_RECEIPT_NOT_SEEN";
                    lastWrapperStatus = lastRobustVoiceStatus;
                }
                render17();
            } catch (Exception e) {
                lastRobustVoiceStatus = "VERIFY_PARSE_FAIL_" + e.getClass().getSimpleName();
                lastWrapperStatus = lastRobustVoiceStatus;
                render17();
            }
        });
    }

    private String robustVoiceJs(String action, boolean click) {
        return "(function(){try{"
                + "const A='" + js17(action) + "',DO=" + (click ? "true" : "false") + ";"
                + "const N=x=>String(x||'').replace(/\\s+/g,' ').trim();"
                + "const H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);};"
                + "const V=e=>{try{const r=e.getBoundingClientRect();const w=e.ownerDocument&&e.ownerDocument.defaultView;const s=w?w.getComputedStyle(e):getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
                + "const M=e=>{let z='';try{z+=' '+N(e.getAttribute('aria-label'))+' '+N(e.getAttribute('title'))+' '+N(e.getAttribute('data-testid'))+' '+N(e.getAttribute('name'))+' '+N(e.getAttribute('id'))+' '+N(e.getAttribute('data-state'))+' '+N(e.innerText||e.textContent||'');const st=e.querySelector&&e.querySelector('svg title');if(st)z+=' '+N(st.textContent||'');}catch(_){}return N(z).toLowerCase();};"
                + "const C=e=>{const x=M(e);if(/unmute|turn[^ ]* microphone on|turn microphone on|mic on|microphone on/.test(x))return 'VOICE_UNMUTE';if(/(^|[^a-z])mute([^a-z]|$)|turn microphone off|mic off|microphone off/.test(x))return 'VOICE_MUTE';if(/end voice|leave voice|exit voice|close voice|voice[^a-z]*close|end call|hang up|disconnect/.test(x))return 'VOICE_END';return 'OTHER';};"
                + "const roots=[document],seenRoots=new Set(),seenEls=new Set(),els=[];for(let q=0;q<roots.length&&q<64;q++){const r=roots[q];if(!r||seenRoots.has(r))continue;seenRoots.add(r);let all=[];try{all=[...r.querySelectorAll('*')];}catch(_){}for(const e of all){try{if(e.shadowRoot)roots.push(e.shadowRoot);if(e.tagName==='IFRAME'&&e.contentDocument)roots.push(e.contentDocument);}catch(_){}}let bs=[];try{bs=[...r.querySelectorAll('button,[role=button],[aria-label],[data-testid]')];}catch(_){}for(const e of bs){if(!seenEls.has(e)&&V(e)){seenEls.add(e);els.push(e);}}}"
                + "const xs=els.filter(e=>C(e)===A);const hs=xs.slice(0,4).map(e=>H(M(e)));let did=false;if(DO&&xs.length===1){xs[0].click();did=true;}return JSON.stringify({matches:xs.length,clicked:did,visibleButtons:els.length,candidateHashes:hs});"
                + "}catch(e){return JSON.stringify({matches:-1,clicked:false,visibleButtons:-1,error:String(e&&e.name||'ERR')});}})();";
    }

    private void invokeParentDispatch(String action) {
        try {
            invokeParentPrivate("dispatch", new Class<?>[]{String.class}, new Object[]{action});
        } catch (Exception e) {
            lastWrapperAction = action;
            lastWrapperStatus = "PARENT_DISPATCH_REFLECTION_FAIL_" + e.getClass().getSimpleName();
            ev17(lastWrapperStatus);
        }
        render17();
    }

    private void invokeParentConfirm(String receipt) throws Exception {
        invokeParentPrivate("confirm", new Class<?>[]{String.class}, new Object[]{receipt});
    }

    private void invokeParentNoArg(String method) {
        try { invokeParentPrivate(method, new Class<?>[0], new Object[0]); }
        catch (Exception e) { ev17(method + "_REFLECTION_FAIL_" + e.getClass().getSimpleName()); }
    }

    private Object invokeParentPrivate(String method, Class<?>[] sig, Object[] args) throws Exception {
        Method m = OrchestratorFoundationV16Activity.class.getDeclaredMethod(method, sig);
        m.setAccessible(true);
        return m.invoke(this, args);
    }

    private Object getParentField(String name) throws Exception {
        Field f = OrchestratorFoundationV16Activity.class.getDeclaredField(name);
        f.setAccessible(true);
        return f.get(this);
    }

    private void setParentField(String name, Object value) throws Exception {
        Field f = OrchestratorFoundationV16Activity.class.getDeclaredField(name);
        f.setAccessible(true);
        f.set(this, value);
    }

    private static Object getObjectField(Object obj, String name) throws Exception {
        Field f = obj.getClass().getDeclaredField(name);
        f.setAccessible(true);
        return f.get(obj);
    }

    private static boolean getBooleanField(Object obj, String name) throws Exception {
        Object x = getObjectField(obj, name);
        return x instanceof Boolean && (Boolean) x;
    }

    private static long getLongField(Object obj, String name) throws Exception {
        Object x = getObjectField(obj, name);
        return x instanceof Number ? ((Number) x).longValue() : 0L;
    }

    private static int getIntField(Object obj, String name) throws Exception {
        Object x = getObjectField(obj, name);
        return x instanceof Number ? ((Number) x).intValue() : 0;
    }

    private int intParent(String name) {
        try {
            Object x = getParentField(name);
            return x instanceof Number ? ((Number) x).intValue() : 0;
        } catch (Exception e) { return 0; }
    }

    private String strParent(String name) {
        try { return String.valueOf(getParentField(name)); }
        catch (Exception e) { return "-"; }
    }

    private String pendingAction() {
        try {
            Object p = getParentField("pending");
            return p == null ? "NONE" : String.valueOf(getObjectField(p, "action"));
        } catch (Exception e) { return "ERR"; }
    }

    private void render17() {
        if (status17 == null) return;
        status17.setText("v0.17 ORCHESTRATOR - START LOCK + MEDIA PLAYBACK REPAIR\n"
                + "Session=" + strParent("sessionState") + " MicLease=PHONE/" + strParent("micLeaseMode")
                + " PlaybackGestureRequired=" + !mediaPlaybackGestureBypass + "\n"
                + "Pending=" + pendingAction() + " ParentAction=" + strParent("lastAction")
                + " ParentStatus=" + strParent("lastActionStatus") + "\n"
                + "WrapperAction=" + lastWrapperAction + " status=" + lastWrapperStatus + "\n"
                + "AcceptedStarts=" + acceptedReversibleStarts + " inverseUnlocks=" + inverseUnlocks
                + " VoiceRobust=" + lastRobustVoiceAction + "/" + lastRobustVoiceStatus
                + " matches=" + lastRobustVoiceMatches + " visibleBtns=" + lastRobustVoiceVisibleButtons);
    }

    private void saveReport17() {
        try {
            String name = "chatgpt-webview-v17-orchestrator-repair-"
                    + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".txt";
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            cv.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
            cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
            Uri u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
            if (u == null) throw new IllegalStateException("insert");
            try (OutputStream out = getContentResolver().openOutputStream(u)) {
                if (out == null) throw new IllegalStateException("stream");
                out.write(reportText17().getBytes(StandardCharsets.UTF_8));
            }
            Toast.makeText(this, "v0.17 report saved to Downloads", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "REPORT17 failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
        }
    }

    private String reportText17() {
        StringBuilder r = new StringBuilder();
        r.append("CHATGPT_WEBVIEW_STABLE_V17_ORCHESTRATOR_START_LOCK_MEDIA_REPAIR\n");
        r.append("V16_DEVICE_FINDING=D_START_OR_V_START_COULD_REMAIN_PENDING_AND_BLOCK_SAFE_FOLLOWUPS\n");
        r.append("V16_VOICE_FINDING=AUDIO_PLAYBACK_WAS_BLOCKED_TAP_OR_CLICK_TO_RESUME\n");
        r.append("MEDIA_PLAYBACK_REQUIRES_USER_GESTURE=").append(!mediaPlaybackGestureBypass).append('\n');
        r.append("START_STATE_MODEL=CONFIRMED_OR_ACCEPTED_REVERSIBLE_START\n");
        r.append("ACCEPTED_REVERSIBLE_START_COUNT=").append(acceptedReversibleStarts).append('\n');
        r.append("SAFE_INVERSE_UNLOCK_COUNT=").append(inverseUnlocks).append('\n');
        r.append("LAST_WRAPPER_ACTION=").append(tok17(lastWrapperAction)).append('\n');
        r.append("LAST_WRAPPER_STATUS=").append(tok17(lastWrapperStatus)).append('\n');
        r.append("LAST_ROBUST_VOICE_ACTION=").append(tok17(lastRobustVoiceAction)).append('\n');
        r.append("LAST_ROBUST_VOICE_STATUS=").append(tok17(lastRobustVoiceStatus)).append('\n');
        r.append("LAST_ROBUST_VOICE_MATCHES=").append(lastRobustVoiceMatches).append('\n');
        r.append("LAST_ROBUST_VOICE_VISIBLE_BUTTONS=").append(lastRobustVoiceVisibleButtons).append('\n');
        r.append("SEMANTIC_SHADOW_AND_SAME_ORIGIN_FRAME_FALLBACK=true\n");
        r.append("COORDINATE_ACTIONS_USED=false\n");
        r.append("RAW_AUDIO_RETAINED=false\nRAW_SPEECH_RETAINED=false\nRAW_CHAT_TEXT_RETAINED=false\n");
        r.append("--- V17 EVENT LOG ---\n").append(events17);
        r.append("--- V16 PARENT REPORT ---\n").append(parentReport16());
        return r.toString();
    }

    private String parentReport16() {
        try {
            Method m = OrchestratorFoundationV16Activity.class.getDeclaredMethod("reportText");
            m.setAccessible(true);
            Object x = m.invoke(this);
            return x == null ? "V16_REPORT_UNAVAILABLE\n" : String.valueOf(x);
        } catch (Exception e) {
            return "V16_REPORT_REFLECTION_FAIL=" + e.getClass().getSimpleName() + "\n";
        }
    }

    private static JSONObject jsonObject17(String value) throws Exception {
        Object x = new JSONTokener(value == null ? "null" : value).nextValue();
        if (x instanceof String) x = new JSONTokener((String) x).nextValue();
        if (!(x instanceof JSONObject)) throw new IllegalStateException("not_object");
        return (JSONObject) x;
    }

    private WebView findWeb17(View v) {
        if (v instanceof WebView) return (WebView) v;
        if (!(v instanceof ViewGroup)) return null;
        ViewGroup g = (ViewGroup) v;
        for (int i = 0; i < g.getChildCount(); i++) {
            WebView w = findWeb17(g.getChildAt(i));
            if (w != null) return w;
        }
        return null;
    }

    private void ev17(String s) {
        if (events17.length() < 26000) {
            events17.append(new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date()))
                    .append(" | ").append(tok17(s)).append('\n');
        }
    }

    private static String tok17(String s) {
        String x = s == null ? "-" : s.replaceAll("[^A-Za-z0-9_.:+/@= -]", "_");
        return x.length() > 220 ? x.substring(0, 220) : x;
    }

    private static String js17(String s) {
        return (s == null ? "" : s).replace("\\", "\\\\").replace("'", "\\'")
                .replace("\n", "\\n").replace("\r", "\\r");
    }

    private int dp17(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    @Override protected void onDestroy() {
        h17.removeCallbacksAndMessages(null);
        super.onDestroy();
    }
}
