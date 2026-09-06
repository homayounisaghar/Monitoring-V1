#!/usr/bin/env python3
from pathlib import Path
import runpy,re

runpy.run_path("ci/generate_chatgpt_webview_v64_conversation_runtime.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorConversationRuntimeV64Activity.java"
ACT=PKG/"OrchestratorConversationRuntimeV65Activity.java"

s=OLD.read_text()

def once(old,new,label):
    global s
    n=s.count(old)
    assert n==1,(label,n)
    s=s.replace(old,new,1)

once("OrchestratorConversationRuntimeV64Activity","OrchestratorConversationRuntimeV65Activity","activity class")
once('SCHEMA="cp-v64-conversation-runtime-v1"','SCHEMA="cp-v65-conversation-runtime-lifecycle-v2-v1"',"schema")
once('SCENARIO="conversation-runtime-read-anchor-compose-send-lifecycle"','SCENARIO="conversation-runtime-lifecycle-v2-safe-insets"',"scenario")
once('getSharedPreferences("cp_v64_conversation_runtime",MODE_PRIVATE)','getSharedPreferences("cp_v65_conversation_runtime",MODE_PRIVATE)',"prefs")
once('testId="cp62-"+UUID.randomUUID();','testId="cp63-"+UUID.randomUUID();',"test id")
once('status.setText("v0.62 Conversation Runtime ready. Raw conversation text stays local.\\nSTART LEARN records a bounded local trace; ANCHOR/RETURN, SET DRAFT and SEND are fail-closed.");','status.setText("v0.63 Conversation Runtime lifecycle-v2 ready. Raw conversation text stays local.\\nResponse start/end are transaction-correlated; top controls respect runtime safe insets.");',"ready status")

once(
'''    private static final long SEND_POLL_MS=300L;''',
'''    private static final long SEND_POLL_MS=300L;
    private static final int RESPONSE_STABLE_SAMPLES=8;
    private static final long RESPONSE_TIMEOUT_MS=240000L;''',
"lifecycle constants")

once(
'''    private String lastAssistantHash="-";
    private int assistantStableHits=0;
    private String lifecycle="IDLE";
    private long startedMs=0L;''',
'''    private String lastAssistantHash="-";
    private int assistantStableHits=0;
    private String lifecycle="IDLE";
    private boolean responseArmed=false;
    private boolean responseStarted=false;
    private boolean responseTimeoutEmitted=false;
    private String pendingResponseBaselineHash="-";
    private String responseBaselineAssistantHash="-";
    private String responseLastAssistantHash="-";
    private int responseStableHits=0;
    private long responseArmedAtMs=0L;
    private int safeTopInsetPx=0;
    private long startedMs=0L;''',
"lifecycle fields")

once(
'''        LinearLayout root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);''',
'''        LinearLayout root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);
        if(android.os.Build.VERSION.SDK_INT>=30)getWindow().setDecorFitsSystemWindows(false);
        root.setOnApplyWindowInsetsListener((v,insets)->{
            int top=0;
            if(android.os.Build.VERSION.SDK_INT>=30){
                top=insets.getInsets(android.view.WindowInsets.Type.statusBars()|android.view.WindowInsets.Type.displayCutout()).top;
            }else{
                top=insets.getSystemWindowInsetTop();
                if(android.os.Build.VERSION.SDK_INT>=28&&insets.getDisplayCutout()!=null)top=Math.max(top,insets.getDisplayCutout().getSafeInsetTop());
            }
            safeTopInsetPx=Math.max(0,top);
            v.setPadding(v.getPaddingLeft(),safeTopInsetPx,v.getPaddingRight(),v.getPaddingBottom());
            return insets;
        });
        root.requestApplyInsets();''',
"safe insets")

once(
'''        lastStateFingerprint="-"; lastAssistantHash="-"; assistantStableHits=0; lifecycle="IDLE";''',
'''        lastStateFingerprint="-"; lastAssistantHash="-"; assistantStableHits=0; lifecycle="IDLE";
        responseArmed=false; responseStarted=false; responseTimeoutEmitted=false;
        pendingResponseBaselineHash="-"; responseBaselineAssistantHash="-"; responseLastAssistantHash="-";
        responseStableHits=0; responseArmedAtMs=0L;''',
"learn reset")

once(
'''            pendingSendHash=ch;
            String claimId="send-"+UUID.randomUUID();''',
'''            pendingSendHash=ch;
            pendingResponseBaselineHash=o.optString("last_assistant_hash","-");
            String claimId="send-"+UUID.randomUUID();''',
"send baseline")

once(
'''            JSONObject claim=sanitizedState(o); put(claim,"payload_hash",pendingSendHash); put(claim,"claim_committed",committed);''',
'''            JSONObject claim=sanitizedState(o); put(claim,"payload_hash",pendingSendHash); put(claim,"response_baseline_assistant_hash",pendingResponseBaselineHash); put(claim,"claim_committed",committed);''',
"send claim baseline")

once(
'''            if(hits>=2){
                sendPending=false; prefs.edit().putString("claim_status","SEND_RECEIPT_CONFIRMED").commit();
                status.setText("Send receipt confirmed. generation="+lifecycle+". Reader will capture the assistant response locally.");
                if(learning)appendLocal(o,"SEND_RECEIPT"); renderLocal(o); return;
            }''',
'''            if(hits>=2){
                sendPending=false; prefs.edit().putString("claim_status","SEND_RECEIPT_CONFIRMED").commit();
                armResponseTransaction(o);
                status.setText("Send receipt confirmed. response="+lifecycle+". Reader will correlate new assistant output to this send.");
                if(learning)appendLocal(o,"SEND_RECEIPT"); renderLocal(o); return;
            }''',
"arm after send receipt")

old_lifecycle='''    private void updateLifecycle(JSONObject o){
        String ah=o.optString("last_assistant_hash","-");
        int stops=o.optInt("stop_candidate_count",0);
        if(stops>0){lifecycle="GENERATING";assistantStableHits=0;}
        else if(!"-".equals(ah)){
            if(ah.equals(lastAssistantHash))assistantStableHits++;else assistantStableHits=1;
            lifecycle=assistantStableHits>=2?"COMPLETE":"ASSISTANT_PRESENT_UNSTABLE";
        } else lifecycle="IDLE";
        lastAssistantHash=ah;
    }
'''
new_lifecycle='''    private void armResponseTransaction(JSONObject o){
        responseArmed=true; responseStarted=false; responseTimeoutEmitted=false;
        responseBaselineAssistantHash=pendingResponseBaselineHash==null?"-":pendingResponseBaselineHash;
        responseLastAssistantHash="-"; responseStableHits=0; responseArmedAtMs=System.currentTimeMillis();
        transitionLifecycle("SENT_AWAITING_ASSISTANT","PASS_RESPONSE_TRANSACTION_ARMED_AFTER_SEND_RECEIPT",o);
        updateLifecycle(o);
    }

    private void transitionLifecycle(String next,String classification,JSONObject o){
        if(next.equals(lifecycle))return;
        lifecycle=next;
        emit("RESPONSE_LIFECYCLE",classification,sanitizedState(o));
    }

    private void updateLifecycle(JSONObject o){
        String ah=o.optString("last_assistant_hash","-");
        long now=System.currentTimeMillis();
        if(responseArmed){
            if(now-responseArmedAtMs>RESPONSE_TIMEOUT_MS){
                if(!responseTimeoutEmitted){
                    responseTimeoutEmitted=true;
                    transitionLifecycle("RESPONSE_TIMEOUT_UNRESOLVED","RESPONSE_TIMEOUT_NO_SEND_REPLAY",o);
                }
                responseArmed=false; responseStableHits=0; lastAssistantHash=ah; return;
            }
            boolean diverged=!"-".equals(ah)&&!ah.equals(responseBaselineAssistantHash);
            if(!responseStarted){
                if(diverged){
                    responseStarted=true; responseLastAssistantHash=ah; responseStableHits=1;
                    transitionLifecycle("STREAMING","PASS_RESPONSE_STREAMING_STARTED_BY_ASSISTANT_DIVERGENCE",o);
                }else{
                    transitionLifecycle("SENT_AWAITING_ASSISTANT","RESPONSE_WAITING_FOR_NEW_ASSISTANT_OUTPUT",o);
                }
            }else{
                if("-".equals(ah)||ah.equals(responseBaselineAssistantHash)){
                    responseStableHits=0;
                }else{
                    if(ah.equals(responseLastAssistantHash))responseStableHits++;else{responseLastAssistantHash=ah;responseStableHits=1;}
                    if(responseStableHits>=RESPONSE_STABLE_SAMPLES){
                        transitionLifecycle("COMPLETE","PASS_RESPONSE_STABLE_COMPLETE",o);
                        responseArmed=false;
                    }else{
                        transitionLifecycle("STREAMING","RESPONSE_STREAMING_ACTIVE",o);
                    }
                }
            }
            lastAssistantHash=ah;
            return;
        }
        if(!"-".equals(ah)){
            if(ah.equals(lastAssistantHash))assistantStableHits++;else assistantStableHits=1;
            lifecycle=assistantStableHits>=2?"COMPLETE":"ASSISTANT_PRESENT_UNSTABLE";
        }else{
            assistantStableHits=0; lifecycle="IDLE";
        }
        lastAssistantHash=ah;
    }
'''
once(old_lifecycle,new_lifecycle,"lifecycle implementation")

once(
'''        put(st,"generation_lifecycle",lifecycle); put(st,"trace_records",traceRecords); put(st,"anchor_hash",anchorHash); put(st,"raw_text_remote",false);''',
'''        put(st,"generation_lifecycle",lifecycle); put(st,"trace_records",traceRecords); put(st,"anchor_hash",anchorHash);
        put(st,"response_armed",responseArmed); put(st,"response_started",responseStarted);
        put(st,"response_baseline_assistant_hash",responseBaselineAssistantHash); put(st,"response_last_assistant_hash",responseLastAssistantHash);
        put(st,"response_stable_hits",responseStableHits); put(st,"response_stable_required",RESPONSE_STABLE_SAMPLES);
        put(st,"response_user_hash",pendingSendHash); put(st,"safe_top_inset_px",safeTopInsetPx); put(st,"raw_text_remote",false);''',
"sanitized lifecycle state")

once(
'''        put(o,"pro_forbidden",true); put(o,"geometry_selection",false); put(o,"raw_html_remote",false); put(o,"raw_url_remote",false); put(o,"raw_chat_text_remote",false); put(o,"cookies_tokens_remote",false);''',
'''        put(o,"pro_forbidden",true); put(o,"geometry_selection",false); put(o,"raw_html_remote",false); put(o,"raw_url_remote",false); put(o,"raw_chat_text_remote",false); put(o,"cookies_tokens_remote",false); put(o,"safe_top_inset_px",safeTopInsetPx);''',
"base safe inset telemetry")

s=s.replace("TelemetryConfigV64","TelemetryConfigV65")
ACT.write_text(s)
assert OLD.exists(); OLD.unlink()

cfg=(PKG/"TelemetryConfigV64.java").read_text()
(PKG/"TelemetryConfigV65.java").write_text(cfg.replace("TelemetryConfigV64","TelemetryConfigV65"))
(PKG/"TelemetryConfigV64.java").unlink()

# Version identity.
g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+65\b","versionCode 66",gs)
gs=gs.replace("0.62-stable-diag-conversation-runtime","0.63-stable-diag-conversation-runtime-lifecycle-v2")
g.write_text(gs)

# Launcher only; Accessibility identity remains V51.
m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text().replace("OrchestratorConversationRuntimeV64Activity","OrchestratorConversationRuntimeV65Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
for v in range(52,66):
    assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

out=ACT.read_text()
for required in [
    "LOCAL READER PREVIEW","START LEARN","ANCHOR CHAT","RETURN","SET DRAFT","SEND",
    "data-message-author-role","conversation_runtime_trace.jsonl","CLAIMED_BEFORE_LOCAL_ANCHOR_NAVIGATION",
    "CLAIMED_BEFORE_COMPOSER_WRITE","CLAIMED_BEFORE_SEND_CLICK","PASS_STABLE_USER_TURN_RECEIPT",
    "PASS_RESPONSE_TRANSACTION_ARMED_AFTER_SEND_RECEIPT","PASS_RESPONSE_STREAMING_STARTED_BY_ASSISTANT_DIVERGENCE",
    "PASS_RESPONSE_STABLE_COMPLETE","RESPONSE_TIMEOUT_NO_SEND_REPLAY","SENT_AWAITING_ASSISTANT","STREAMING",
    "RESPONSE_STABLE_SAMPLES","setDecorFitsSystemWindows(false)","displayCutout()","safe_top_inset_px",
    "raw_chat_text_remote","TelemetryConfigV65"
]: assert required in out, required
assert 'lifecycle="GENERATING"' not in out
assert out.count('.click();')==1
for forbidden in ["elementFromPoint","document.evaluate","dispatchTouchEvent(","performClick(","ACTION_SET_PROGRESS","CookieManager","getCookie(","addJavascriptInterface","setAttribute(\\\"aria-value"]:
    assert forbidden not in out, forbidden
