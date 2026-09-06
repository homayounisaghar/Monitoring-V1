#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.69: preserve v0.68 completion-v2 + zero-clock event-driven control.
# Change only Planner response parsing: accept exactly one syntactically valid,
# bounded action JSON object even when ChatGPT wraps it in prose/Markdown.
# Multiple valid JSON objects remain ambiguous and fail closed.
runpy.run_path("ci/generate_chatgpt_webview_v70_planner_completion_v2_final.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorPlannerCoreV70Activity.java"
ACT=PKG/"OrchestratorPlannerCoreV71Activity.java"
s=OLD.read_text()

# Identity.
s=s.replace("OrchestratorPlannerCoreV70Activity","OrchestratorPlannerCoreV71Activity")
s=re.sub(r'private static final String SCHEMA="[^"]+";', 'private static final String SCHEMA="cp-v71-planner-core-parser-v2-v1";', s, count=1)
s=re.sub(r'private static final String SCENARIO="[^"]+";', 'private static final String SCENARIO="same-apk-semantic-planner-core-parser-v2";', s, count=1)
s=s.replace('getSharedPreferences("cp_v70_planner_core",MODE_PRIVATE)','getSharedPreferences("cp_v71_planner_core",MODE_PRIVATE)')
s=s.replace('testId="cp68-"+UUID.randomUUID();','testId="cp69-"+UUID.randomUUID();')
s=s.replace('status.setText("v0.68 EVENT-DRIVEN Planner completion-v2 ready. Puzzle is unknown at build time.\\nNo clock control. Completion accepts current ChatGPT action-bar copy receipts; remote streaming telemetry is deduplicated.");','status.setText("v0.69 EVENT-DRIVEN Planner parser-v2 ready. Puzzle is unknown at build time.\\nNo clock control. A single bounded JSON action may be recovered from harmless Markdown/prose wrapping; ambiguity still fails closed.");')

# Parser diagnostics are hashes/counts/classes only; raw Planner response remains local.
needle='    private String lastControlTelemetryFingerprint="-";\n'
assert s.count(needle)==1
s=s.replace(needle,needle+'    private int plannerParseObjectCount=0;\n    private int plannerParseValidCount=0;\n    private String plannerParseMode="NONE";\n',1)

# Replace strict wrapper-sensitive parser with a brace/string-aware extractor.
pat=r'    private JSONObject parsePlannerAction\(String raw\)\{.*?\n    \}\n\n    private void executePlannerAction'
m=re.search(pat,s,re.S)
assert m,"parsePlannerAction block not found"
parser=r'''    private JSONObject validatePlannerActionObject(JSONObject a){
        if(a==null||a.optInt("version",-1)!=1)return null;
        String k=a.optString("action","");
        if("GO_MAIN_CHAT".equals(k))return a;
        if("GO_CHAT".equals(k)){String r=a.optString("chat_ref","");return r.matches("^CHAT_[0-9]+$")?a:null;}
        if("READ_LAST_RESPONSE".equals(k)){String r=a.optString("chat_ref","MAIN");return ("MAIN".equals(r)||r.matches("^CHAT_[0-9]+$"))?a:null;}
        if("SEND".equals(k)){String r=a.optString("chat_ref","MAIN"),t=a.optString("text","");return (("MAIN".equals(r)||r.matches("^CHAT_[0-9]+$"))&&!t.trim().isEmpty()&&t.length()<=MAX_PLANNER_SEND_CHARS)?a:null;}
        if("DONE".equals(k))return a;
        return null;
    }

    private ArrayList<String> extractTopLevelJsonObjects(String raw){
        ArrayList<String> out=new ArrayList<>();
        if(raw==null)return out;
        int depth=0,start=-1;boolean inString=false,escape=false;
        for(int i=0;i<raw.length();i++){
            char c=raw.charAt(i);
            if(inString){
                if(escape){escape=false;continue;}
                if(c=='\\'){escape=true;continue;}
                if(c=='\"'){inString=false;}
                continue;
            }
            if(c=='\"'){inString=true;continue;}
            if(c=='{'){if(depth==0)start=i;depth++;continue;}
            if(c=='}'&&depth>0){depth--;if(depth==0&&start>=0){out.add(raw.substring(start,i+1));start=-1;}}
        }
        return out;
    }

    private JSONObject parsePlannerAction(String raw){
        plannerParseObjectCount=0;plannerParseValidCount=0;plannerParseMode="NONE";
        try{
            if(raw==null)return null;
            String x=raw.trim();
            ArrayList<String> segments=extractTopLevelJsonObjects(x);
            int jsonObjects=0,valid=0;JSONObject accepted=null;String acceptedRaw="";
            for(String seg:segments){
                try{
                    JSONObject candidate=new JSONObject(seg);jsonObjects++;
                    JSONObject bounded=validatePlannerActionObject(candidate);
                    if(bounded!=null){valid++;accepted=bounded;acceptedRaw=seg;}
                }catch(Exception ignored){}
            }
            plannerParseObjectCount=jsonObjects;plannerParseValidCount=valid;
            if(jsonObjects!=1||valid!=1)return null;
            plannerParseMode=x.equals(acceptedRaw)?"EXACT_JSON":"WRAPPED_SINGLE_JSON";
            return accepted;
        }catch(Exception ignored){return null;}
    }

    private void executePlannerAction'''
s=s[:m.start()]+parser+s[m.end():]

# Add sanitized parser evidence to both reject and accept Planner-plan events.
old='if(action==null){JSONObject st=sanitizedState(o);put(st,"planner_response_hash",responseHash);emit("PLANNER_PLAN","PLANNER_RESPONSE_INVALID_JSON_OR_ACTION",st);plannerFail("PLANNER_RESPONSE_INVALID_JSON_OR_ACTION");return;}'
new='if(action==null){JSONObject st=sanitizedState(o);put(st,"planner_response_hash",responseHash);put(st,"planner_parse_json_objects",plannerParseObjectCount);put(st,"planner_parse_valid_actions",plannerParseValidCount);put(st,"planner_parse_mode",plannerParseMode);emit("PLANNER_PLAN","PLANNER_RESPONSE_INVALID_JSON_OR_ACTION",st);plannerFail("PLANNER_RESPONSE_INVALID_JSON_OR_ACTION");return;}'
assert s.count(old)==1,("invalid plan branch",s.count(old))
s=s.replace(old,new,1)
old2='JSONObject st=sanitizedState(o); put(st,"planner_response_hash",responseHash); put(st,"planner_action",kind); put(st,"planner_target_ref",ref); put(st,"planner_text_hash",text.isEmpty()?"-":hashNorm(text)); put(st,"planner_text_chars",text.length());'
new2='JSONObject st=sanitizedState(o); put(st,"planner_response_hash",responseHash); put(st,"planner_action",kind); put(st,"planner_target_ref",ref); put(st,"planner_text_hash",text.isEmpty()?"-":hashNorm(text)); put(st,"planner_text_chars",text.length()); put(st,"planner_parse_json_objects",plannerParseObjectCount); put(st,"planner_parse_valid_actions",plannerParseValidCount); put(st,"planner_parse_mode",plannerParseMode);'
assert s.count(old2)==1,("accepted plan telemetry",s.count(old2))
s=s.replace(old2,new2,1)

# Telemetry config lineage.
s=s.replace("TelemetryConfigV70","TelemetryConfigV71")
ACT.write_text(s)
assert OLD.exists();OLD.unlink()
cfg=(PKG/"TelemetryConfigV70.java").read_text()
(PKG/"TelemetryConfigV71.java").write_text(cfg.replace("TelemetryConfigV70","TelemetryConfigV71"))
(PKG/"TelemetryConfigV70.java").unlink()

# Version identity.
g=ROOT/"app/build.gradle"
gs=g.read_text();gs=re.sub(r"versionCode\s+71\b","versionCode 72",gs);gs=gs.replace("0.68-stable-diag-semantic-planner-completion-v2","0.69-stable-diag-semantic-planner-parser-v2");g.write_text(gs)

# Launcher only; Accessibility identity remains V51.
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorPlannerCoreV70Activity","OrchestratorPlannerCoreV71Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms and "@xml/cp_accessibility_service_v51" in ms
for v in range(52,72):assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
mf.write_text(ms)

out=ACT.read_text()
for required in [
    "PUZZLE_UNKNOWN_AT_BUILD_TIME","CONTROL_EVENT_DRIVEN_NO_FIXED_DELAY_POLL_TIMEOUT","WebMessagePort","MutationObserver",
    "copy-turn-action-button","action-bar-copy","PASS_RESPONSE_COMPLETE_BY_ASSISTANT_ACTION_RECEIPT",
    "extractTopLevelJsonObjects","validatePlannerActionObject","WRAPPED_SINGLE_JSON","planner_parse_json_objects","planner_parse_valid_actions",
    "PASS_BOUNDED_PLANNER_ACTION_PARSED","PASS_PLANNER_DONE_RETURNED_TO_MAIN","raw_chat_text_remote","safe_top_inset_px","TelemetryConfigV71"
]:assert required in out,required
for forbidden in [
    "postDelayed","Thread.sleep","setTimeout(","setInterval(","SAMPLE_MS","SEND_POLL_MS","RESPONSE_TIMEOUT_MS",
    "ScheduledExecutorService","TimerTask","pollPlannerNormalHome","pollPlannerTempReceipt","pollAutoComposerReceipt",
    "pollAutoSendReceipt","pollAutoResponse","pollPlannerNavReceipt","pollSendReceipt","confirmAutoSendReceipt",
    "elementFromPoint","document.evaluate","dispatchTouchEvent(","performClick(","ACTION_SET_PROGRESS","CookieManager",
    "getCookie(","addJavascriptInterface","setAttribute(\\\"aria-value"
]:assert forbidden not in out,forbidden
assert out.count('.click();')==2,out.count('.click();')
assert "Tehran" not in out and "تهران" not in out
print("PASS v0.69 parser-v2: exactly one bounded JSON action may be recovered from wrapping; ambiguity fails closed; zero-clock control preserved")