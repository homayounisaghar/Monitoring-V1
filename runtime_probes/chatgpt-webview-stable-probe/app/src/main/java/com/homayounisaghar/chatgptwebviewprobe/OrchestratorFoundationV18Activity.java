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

/** Stable v0.18 - Audio Capability Adapter V2 + hard recovery. */
public class OrchestratorFoundationV18Activity extends OrchestratorFoundationV16Activity {
    private static final String PREFS18 = "stable_v18_audio_adapter_v2";
    private final Handler h18 = new Handler(Looper.getMainLooper());
    private final StringBuilder events18 = new StringBuilder();
    private WebView web18;
    private TextView status18;
    private SharedPreferences prefs18;
    private boolean playbackGestureBypass = false;
    private String adapterAction = "NONE";
    private String adapterStatus = "NOT_RUN";
    private int adapterMatches = -1;
    private int adapterVisible = -1;
    private String adapterStrategy = "-";
    private int forcedRecoveries = 0;
    private int reversibleDispatches = 0;

    private final Runnable tick18 = new Runnable() {
        @Override public void run() {
            render18();
            h18.postDelayed(this, 350L);
        }
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs18 = getSharedPreferences(PREFS18, MODE_PRIVATE);
        web18 = findWeb18(getWindow().getDecorView());
        if (web18 == null) return;
        web18.setMinimumHeight(Math.max(1, getResources().getDisplayMetrics().heightPixels / 2));
        applyPlaybackBypass();
        hideV16Status(getWindow().getDecorView());
        retargetButtons(getWindow().getDecorView());
        addStatusPanel();
        ev18("V18_READY_AUDIO_ADAPTER_V2_HARD_RECOVERY");
        h18.post(tick18);
        render18();
    }

    private void applyPlaybackBypass() {
        try {
            web18.getSettings().setMediaPlaybackRequiresUserGesture(false);
            playbackGestureBypass = !web18.getSettings().getMediaPlaybackRequiresUserGesture();
        } catch (Exception e) {
            playbackGestureBypass = false;
            ev18("PLAYBACK_BYPASS_FAIL_" + e.getClass().getSimpleName());
        }
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
                case "SESSION START":
                case "SESSION END":
                    b.setOnClickListener(x -> sessionToggle18());
                    break;
                case "D START": b.setOnClickListener(x -> audioAction18("DICTATION_START")); break;
                case "D STOP": b.setOnClickListener(x -> audioAction18("DICTATION_STOP")); break;
                case "D CANCEL": b.setOnClickListener(x -> audioAction18("DICTATION_CANCEL")); break;
                case "V START": b.setOnClickListener(x -> audioAction18("VOICE_START")); break;
                case "V MUTE": b.setOnClickListener(x -> audioAction18("VOICE_MUTE")); break;
                case "V UNMUTE": b.setOnClickListener(x -> audioAction18("VOICE_UNMUTE")); break;
                case "V END": b.setOnClickListener(x -> audioAction18("VOICE_END")); break;
                case "STATE":
                    b.setOnClickListener(x -> { invokeParentNoArg("pollSnapshot"); render18(); });
                    break;
                case "REPORT16":
                    b.setText("REPORT18");
                    b.setOnClickListener(x -> saveReport18());
                    break;
                default: break;
            }
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) retargetButtons(g.getChildAt(i));
        }
    }

    private void addStatusPanel() {
        View content = findViewById(android.R.id.content);
        if (!(content instanceof ViewGroup)) return;
        ViewGroup cg = (ViewGroup) content;
        if (cg.getChildCount() == 0 || !(cg.getChildAt(0) instanceof LinearLayout)) return;
        LinearLayout root = (LinearLayout) cg.getChildAt(0);
        int wi = root.indexOfChild(web18);
        if (wi < 0) wi = 0;
        status18 = new TextView(this);
        status18.setTextSize(8.3f);
        status18.setTextIsSelectable(true);
        status18.setPadding(dp18(7), dp18(2), dp18(7), dp18(2));
        ScrollView sv = new ScrollView(this);
        sv.addView(status18, new ScrollView.LayoutParams(ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT));
        root.addView(sv, wi, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp18(102)));
    }

    private void sessionToggle18() {
        String state = strParent("sessionState");
        if (!"ACTIVE".equals(state)) {
            adapterAction = "SESSION_START";
            adapterStatus = "PARENT_START_REQUESTED";
            invokeParentNoArg("toggleSession");
            render18();
            return;
        }
        adapterAction = "SESSION_END";
        adapterStatus = "FORCE_RECOVERY_STARTED";
        forcedRecoveries++;
        ev18("SESSION_END_FORCE_RECOVERY lease=" + strParent("micLeaseMode") + " pending=" + pendingAction18());
        if ("DICTATION".equals(strParent("micLeaseMode"))) bestEffortTeardown18("DICTATION_STOP");
        else if ("LIVE".equals(strParent("micLeaseMode"))) bestEffortTeardown18("VOICE_END");
        else stopTrackedAudio18();
        clearParentPending18("SESSION_END_FORCE_RECOVERY");
        invokeParentPrivateQuiet("revokeLease", new Class<?>[]{String.class}, new Object[]{"V18_FORCE_SESSION_END"});
        setParentQuiet("uncertainBlockedAction", "NONE");
        invokeParentNoArg("toggleSession");
        adapterStatus = "FORCE_RECOVERY_SESSION_END_REQUESTED";
        render18();
    }

    private void audioAction18(String action) {
        if (!"ACTIVE".equals(strParent("sessionState"))) { blocked18(action, "SESSION_NOT_ACTIVE"); return; }
        if (!trustedUrl18(web18.getUrl())) { blocked18(action, "UNTRUSTED_ORIGIN"); return; }
        String lease = strParent("micLeaseMode");
        if (("DICTATION_START".equals(action) || "VOICE_START".equals(action)) && !"NONE".equals(lease)) {
            blocked18(action, "MIC_ALREADY_LEASED_" + lease); return;
        }
        if (("DICTATION_STOP".equals(action) || "DICTATION_CANCEL".equals(action)) && !"DICTATION".equals(lease)) {
            blocked18(action, "NO_DICTATION_LEASE"); return;
        }
        if (("VOICE_MUTE".equals(action) || "VOICE_UNMUTE".equals(action) || "VOICE_END".equals(action)) && !"LIVE".equals(lease)) {
            blocked18(action, "NO_LIVE_LEASE"); return;
        }
        clearStaleAudioStartPending18(action);
        if ("DICTATION_START".equals(action)) {
            invokeParentPrivateQuiet("acquireLease", new Class<?>[]{String.class, long.class}, new Object[]{"DICTATION", 2L * 60L * 1000L});
        } else if ("VOICE_START".equals(action)) {
            applyPlaybackBypass();
            invokeParentPrivateQuiet("acquireLease", new Class<?>[]{String.class, long.class}, new Object[]{"LIVE", 10L * 60L * 1000L});
        }
        String claimId = action + "_" + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0, 8);
        boolean durable = prefs18.edit().putString("claim_id", claimId).putString("claim_action", action).putString("claim_status", "CLAIMED").commit();
        if (!durable) {
            if (action.endsWith("START")) invokeParentPrivateQuiet("revokeLease", new Class<?>[]{String.class}, new Object[]{"V18_CLAIM_FAIL"});
            blocked18(action, "CLAIM_WRITE_FAIL"); return;
        }
        adapterAction = action;
        adapterStatus = "RESOLVING_CURRENT_SEMANTIC_CONTROL";
        adapterMatches = -1; adapterVisible = -1; adapterStrategy = "-";
        render18();
        web18.evaluateJavascript(audioResolverJs18(action, true), value -> {
            try {
                JSONObject o = jsonObject18(value);
                int matches = o.optInt("matches", -1);
                int visible = o.optInt("visible", -1);
                boolean clicked = o.optBoolean("clicked", false);
                String strategy = tok18(o.optString("strategy", "-"));
                adapterMatches = matches; adapterVisible = visible; adapterStrategy = strategy;
                if (matches == 1 && clicked) {
                    reversibleDispatches++;
                    prefs18.edit().putString("claim_status", "DISPATCHED_REVERSIBLE").commit();
                    adapterStatus = "DISPATCHED_REVERSIBLE_NO_GLOBAL_LOCK";
                    ev18(action + " DISPATCHED strategy=" + strategy + " visible=" + visible);
                    if ("DICTATION_STOP".equals(action) || "DICTATION_CANCEL".equals(action)) {
                        h18.postDelayed(() -> {
                            invokeParentPrivateQuiet("revokeLease", new Class<?>[]{String.class}, new Object[]{"V18_DICTATION_FINISHED"});
                            adapterStatus = "DISPATCHED_STOP_LEASE_RELEASED";
                            invokeParentNoArg("pollSnapshot");
                            render18();
                        }, 450L);
                    } else if ("VOICE_END".equals(action)) {
                        h18.postDelayed(() -> {
                            invokeParentPrivateQuiet("revokeLease", new Class<?>[]{String.class}, new Object[]{"V18_VOICE_ENDED"});
                            adapterStatus = "DISPATCHED_END_LEASE_RELEASED";
                            render18();
                        }, 450L);
                    }
                    render18(); return;
                }
                prefs18.edit().putString("claim_status", "ABORTED_NO_SIDE_EFFECT").commit();
                adapterStatus = matches == 0 ? "ABORTED_NO_MATCH" : "ABORTED_AMBIGUOUS_MATCHES_" + matches;
                ev18(action + " " + adapterStatus + " strategy=" + strategy + " visible=" + visible);
                if (action.endsWith("START")) invokeParentPrivateQuiet("revokeLease", new Class<?>[]{String.class}, new Object[]{"V18_START_NOT_DISPATCHED"});
                render18();
            } catch (Exception e) {
                prefs18.edit().putString("claim_status", "ABORTED_PARSE_NO_SIDE_EFFECT").commit();
                adapterStatus = "ABORTED_PARSE_" + e.getClass().getSimpleName();
                if (action.endsWith("START")) invokeParentPrivateQuiet("revokeLease", new Class<?>[]{String.class}, new Object[]{"V18_PARSE_FAIL"});
                render18();
            }
        });
    }

    private void clearStaleAudioStartPending18(String nextAction) {
        try {
            Object p = getParentField18("pending");
            if (p == null) return;
            String a = String.valueOf(getObjectField18(p, "action"));
            if (!"DICTATION_START".equals(a) && !"VOICE_START".equals(a)) return;
            setParentField18("pending", null);
            setParentField18("lastAction", a);
            setParentField18("lastActionStatus", "ACCEPTED_REVERSIBLE_START_SUPERSEDED_V18");
            ev18("CLEARED_STALE_AUDIO_START pending=" + a + " next=" + nextAction);
        } catch (Exception e) { ev18("CLEAR_STALE_AUDIO_START_FAIL_" + e.getClass().getSimpleName()); }
    }

    private void clearParentPending18(String reason) {
        try {
            Object p = getParentField18("pending");
            if (p != null) {
                String a = String.valueOf(getObjectField18(p, "action"));
                setParentField18("pending", null);
                ev18("PARENT_PENDING_CLEARED action=" + a + " reason=" + reason);
            }
        } catch (Exception e) { ev18("PARENT_PENDING_CLEAR_FAIL_" + e.getClass().getSimpleName()); }
    }

    private void bestEffortTeardown18(String action) {
        try {
            web18.evaluateJavascript(audioResolverJs18(action, true), value -> {
                ev18("FORCE_TEARDOWN_CLICK_RESULT action=" + action + " value=" + tok18(String.valueOf(value)));
                stopTrackedAudio18();
            });
        } catch (Exception e) {
            ev18("FORCE_TEARDOWN_CLICK_FAIL_" + e.getClass().getSimpleName());
            stopTrackedAudio18();
        }
    }

    private void stopTrackedAudio18() {
        if (web18 == null) return;
        web18.evaluateJavascript("(function(){try{let n=0;const o=window.__cp16Media;if(o&&o.tracks){for(const t of [...o.tracks]){try{if(t&&t.readyState==='live'){t.stop();n++;}}catch(_){}}}return String(n);}catch(e){return 'ERR';}})();", value -> ev18("FORCE_TRACK_STOP_RESULT=" + tok18(String.valueOf(value))));
    }

    private String audioResolverJs18(String action, boolean click) {
        return "(function(){try{"
                + "const A='" + js18(action) + "',DO=" + (click ? "true" : "false") + ";"
                + "const N=x=>String(x||'').replace(/\\s+/g,' ').trim();"
                + "const V=e=>{try{const r=e.getBoundingClientRect();const w=e.ownerDocument&&e.ownerDocument.defaultView;const s=w?w.getComputedStyle(e):getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}catch(_){return false;}};"
                + "const M=e=>{let z='';try{for(const k of ['aria-label','title','data-testid','name','id','data-state'])z+=' '+N(e.getAttribute&&e.getAttribute(k));z+=' '+N(e.innerText||e.textContent||'');const st=e.querySelector&&e.querySelector('svg title');if(st)z+=' '+N(st.textContent||'');}catch(_){}return N(z).toLowerCase();};"
                + "const roots=[document],sr=new Set(),se=new Set(),els=[];for(let q=0;q<roots.length&&q<80;q++){const r=roots[q];if(!r||sr.has(r))continue;sr.add(r);let all=[];try{all=[...r.querySelectorAll('*')];}catch(_){}for(const e of all){try{if(e.shadowRoot)roots.push(e.shadowRoot);if(e.tagName==='IFRAME'&&e.contentDocument)roots.push(e.contentDocument);}catch(_){}}let bs=[];try{bs=[...r.querySelectorAll('button,[role=button],[aria-label],[data-testid]')];}catch(_){}for(const e of bs){if(!se.has(e)&&V(e)){se.add(e);els.push(e);}}}"
                + "const isStopResponse=x=>/stop generating|stop response|stop-button|stop_response/.test(x);"
                + "const startDict=x=>/dictat|voice input|record audio|record message|start recording|microphone/.test(x)&&!/mute|unmute|voice mode|advanced voice|end voice|leave voice/.test(x);"
                + "const stopDict=x=>!isStopResponse(x)&&(/stop recording|finish recording|end recording|recording stop|stop dictat|stop voice input|finish dictat/.test(x)||(/^stop$/.test(x)));"
                + "const cancelDict=x=>/cancel recording|discard recording|cancel dictat|discard dictat|cancel voice input/.test(x)||(/^cancel$/.test(x));"
                + "const voiceStart=x=>/voice mode|start voice|open voice|advanced voice/.test(x);"
                + "const voiceMute=x=>/(^|[^a-z])mute([^a-z]|$)|turn microphone off|mic off|microphone off/.test(x)&&!/unmute/.test(x);"
                + "const voiceUnmute=x=>/unmute|turn microphone on|mic on|microphone on/.test(x);"
                + "const voiceEnd=x=>/end voice|leave voice|exit voice|close voice|end call|hang up|disconnect/.test(x)||(/^close$/.test(x));"
                + "let primary=[],fallback=[],strategy='primary';for(const e of els){const x=M(e);if(A==='DICTATION_START'&&startDict(x))primary.push(e);else if(A==='DICTATION_STOP'){if(stopDict(x))primary.push(e);else if(startDict(x))fallback.push(e);}else if(A==='DICTATION_CANCEL'&&cancelDict(x))primary.push(e);else if(A==='VOICE_START'&&voiceStart(x))primary.push(e);else if(A==='VOICE_MUTE'&&voiceMute(x))primary.push(e);else if(A==='VOICE_UNMUTE'&&voiceUnmute(x))primary.push(e);else if(A==='VOICE_END'&&voiceEnd(x))primary.push(e);}"
                + "let xs=primary;if(A==='DICTATION_STOP'&&primary.length===0&&fallback.length===1){xs=fallback;strategy='dictation_toggle_fallback';}"
                + "let did=false;if(DO&&xs.length===1){xs[0].click();did=true;}return JSON.stringify({matches:xs.length,clicked:did,visible:els.length,strategy:strategy,primary:primary.length,fallback:fallback.length});"
                + "}catch(e){return JSON.stringify({matches:-1,clicked:false,visible:-1,strategy:'error',error:String(e&&e.name||'ERR')});}})();";
    }

    private void blocked18(String action, String reason) {
        adapterAction = action;
        adapterStatus = "BLOCKED_" + tok18(reason);
        ev18(action + " " + adapterStatus);
        render18();
    }

    private void render18() {
        if (status18 == null) return;
        status18.setText("v0.18 ORCHESTRATOR - AUDIO ADAPTER V2 + HARD RECOVERY\n"
                + "Session=" + strParent("sessionState") + " MicLease=PHONE/" + strParent("micLeaseMode") + " PlaybackGestureRequired=" + !playbackGestureBypass + "\n"
                + "ParentPending=" + pendingAction18() + " ParentAction=" + strParent("lastAction") + " ParentStatus=" + strParent("lastActionStatus") + "\n"
                + "AudioAdapter=" + adapterAction + " status=" + adapterStatus + "\n"
                + "matches=" + adapterMatches + " strategy=" + adapterStrategy + " visible=" + adapterVisible + " reversibleDispatches=" + reversibleDispatches + " recoveries=" + forcedRecoveries);
    }

    private void saveReport18() {
        try {
            String name = "chatgpt-webview-v18-audio-adapter-" + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date()) + ".txt";
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
        } catch (Exception e) { Toast.makeText(this, "REPORT18 failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show(); }
    }

    private String reportText18() {
        StringBuilder r = new StringBuilder();
        r.append("CHATGPT_WEBVIEW_STABLE_V18_AUDIO_ADAPTER_V2_HARD_RECOVERY\n");
        r.append("V17_DEVICE_FINDING=D_START_STILL_LEFT_UI_EFFECTIVELY_LOCKED_AND_SESSION_END_BLOCKED\n");
        r.append("AUDIO_LIFECYCLE_GLOBAL_PENDING_LOCK=false\n");
        r.append("SESSION_END_HARD_RECOVERY=true\n");
        r.append("MEDIA_PLAYBACK_REQUIRES_USER_GESTURE=").append(!playbackGestureBypass).append('\n');
        r.append("SESSION_STATE=").append(tok18(strParent("sessionState"))).append('\n');
        r.append("MIC_LEASE_MODE=").append(tok18(strParent("micLeaseMode"))).append('\n');
        r.append("PARENT_PENDING_ACTION=").append(tok18(pendingAction18())).append('\n');
        r.append("LAST_AUDIO_ADAPTER_ACTION=").append(tok18(adapterAction)).append('\n');
        r.append("LAST_AUDIO_ADAPTER_STATUS=").append(tok18(adapterStatus)).append('\n');
        r.append("LAST_AUDIO_ADAPTER_MATCHES=").append(adapterMatches).append('\n');
        r.append("LAST_AUDIO_ADAPTER_STRATEGY=").append(tok18(adapterStrategy)).append('\n');
        r.append("LAST_AUDIO_ADAPTER_VISIBLE_COUNT=").append(adapterVisible).append('\n');
        r.append("REVERSIBLE_AUDIO_DISPATCH_COUNT=").append(reversibleDispatches).append('\n');
        r.append("FORCED_SESSION_RECOVERY_COUNT=").append(forcedRecoveries).append('\n');
        r.append("SHADOW_AND_SAME_ORIGIN_FRAME_TRAVERSAL=true\n");
        r.append("SEMANTIC_COORDINATES_USED=false\nPRIVATE_CHATGPT_API_USED=false\n");
        r.append("RAW_AUDIO_RETAINED=false\nRAW_SPEECH_RETAINED=false\nRAW_CHAT_TEXT_RETAINED=false\n");
        r.append("--- V18 EVENT LOG ---\n").append(events18);
        return r.toString();
    }

    private String pendingAction18() {
        try { Object p = getParentField18("pending"); return p == null ? "NONE" : String.valueOf(getObjectField18(p, "action")); }
        catch (Exception e) { return "ERR"; }
    }

    private Object invokeParentPrivate18(String method, Class<?>[] sig, Object[] args) throws Exception {
        Method m = OrchestratorFoundationV16Activity.class.getDeclaredMethod(method, sig);
        m.setAccessible(true);
        return m.invoke(this, args);
    }
    private void invokeParentPrivateQuiet(String method, Class<?>[] sig, Object[] args) {
        try { invokeParentPrivate18(method, sig, args); } catch (Exception e) { ev18(method + "_REFLECTION_FAIL_" + e.getClass().getSimpleName()); }
    }
    private void invokeParentNoArg(String method) { invokeParentPrivateQuiet(method, new Class<?>[0], new Object[0]); }
    private Object getParentField18(String name) throws Exception { Field f = OrchestratorFoundationV16Activity.class.getDeclaredField(name); f.setAccessible(true); return f.get(this); }
    private void setParentField18(String name, Object value) throws Exception { Field f = OrchestratorFoundationV16Activity.class.getDeclaredField(name); f.setAccessible(true); f.set(this, value); }
    private void setParentQuiet(String name, Object value) { try { setParentField18(name, value); } catch (Exception e) { ev18("SET_PARENT_" + name + "_FAIL_" + e.getClass().getSimpleName()); } }
    private static Object getObjectField18(Object obj, String name) throws Exception { Field f = obj.getClass().getDeclaredField(name); f.setAccessible(true); return f.get(obj); }
    private String strParent(String name) { try { return String.valueOf(getParentField18(name)); } catch (Exception e) { return "-"; } }
    private boolean trustedUrl18(String s) { try { Uri u = Uri.parse(s == null ? "" : s); return "https".equalsIgnoreCase(u.getScheme()) && "chatgpt.com".equalsIgnoreCase(u.getHost()); } catch (Exception e) { return false; } }
    private WebView findWeb18(View v) { if (v instanceof WebView) return (WebView) v; if (!(v instanceof ViewGroup)) return null; ViewGroup g = (ViewGroup) v; for (int i=0;i<g.getChildCount();i++){ WebView w=findWeb18(g.getChildAt(i)); if(w!=null)return w;} return null; }
    private static JSONObject jsonObject18(String value) throws Exception { Object x = new JSONTokener(value == null ? "null" : value).nextValue(); if (x instanceof String) x = new JSONTokener((String)x).nextValue(); if (!(x instanceof JSONObject)) throw new IllegalStateException("not_object"); return (JSONObject)x; }
    private void ev18(String s) { if (events18.length() < 30000) events18.append(new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date())).append(" | ").append(tok18(s)).append('\n'); }
    private static String tok18(String s) { String x=s==null?"-":s.replaceAll("[^A-Za-z0-9_.:+/@= -]","_"); return x.length()>240?x.substring(0,240):x; }
    private static String js18(String s) { return (s==null?"":s).replace("\\","\\\\").replace("'","\\'").replace("\n","\\n").replace("\r","\\r"); }
    private int dp18(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }
    @Override protected void onDestroy() { h18.removeCallbacksAndMessages(null); super.onDestroy(); }
}
