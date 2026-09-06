#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.72: close the real-device v0.71 parser frontier without weakening the
# execution boundary. The observed v0.71 run completed a fresh Temporary
# Planner response but produced zero valid bounded JSON actions. Preserve the
# strict action validator and add one same-room, model-only FORMAT REPAIR turn
# before failing closed. Never infer an executable action from free-form text.
runpy.run_path("ci/generate_chatgpt_webview_v73_planner_execution_hardening_final.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorPlannerCoreV73Activity.java"
ACT=PKG/"OrchestratorPlannerCoreV74Activity.java"
s=OLD.read_text()

def method(name,body,rettype="void"):
    global s
    pat=rf'    private {re.escape(rettype)} {re.escape(name)}\([^\n]*\)\{{.*?\n    \}}\n\n'
    m=re.search(pat,s,re.S)
    assert m,(rettype,name,"method not found")
    s=s[:m.start()]+body+s[m.end():]

def once(old,new,label):
    global s
    n=s.count(old)
    assert n==1,(label,n)
    s=s.replace(old,new,1)

# Identity / update-line continuity.
s=s.replace("OrchestratorPlannerCoreV73Activity","OrchestratorPlannerCoreV74Activity")
s=s.replace('SCHEMA="cp-v73-planner-core-execution-hardened-v1"','SCHEMA="cp-v74-planner-core-format-repair-v1"')
s=s.replace('SCENARIO="same-apk-semantic-planner-core-execution-hardened"','SCENARIO="same-apk-semantic-planner-core-format-repair"')
s=s.replace('getSharedPreferences("cp_v73_planner_core",MODE_PRIVATE)','getSharedPreferences("cp_v74_planner_core",MODE_PRIVATE)')
s=s.replace('testId="cp71-"+UUID.randomUUID();','testId="cp72-"+UUID.randomUUID();')
s=s.replace('status.setText("v0.71 EVENT-DRIVEN Planner execution-hardened ready. Puzzle is unknown at build time.\\nNo clock control. Planner actions dispatch directly from proven Temporary state; document-epoch receipts reject stale reads.");','status.setText("v0.72 EVENT-DRIVEN Planner format-repair hardened ready. Puzzle is unknown at build time.\\nNo clock control. Invalid Planner formatting gets one same-room JSON-only repair turn; ambiguity still fails closed.");')

# Parser/repair diagnostics. Raw Planner response remains local.
needle='    private int plannerParseObjectCount=0;\n    private int plannerParseValidCount=0;\n    private String plannerParseMode="NONE";\n'
assert s.count(needle)==1,s.count(needle)
s=s.replace(needle,needle+'    private int plannerParseSegmentCount=0;\n    private int plannerFormatRepairAttempts=0;\n',1)
once('plannerParseObjectCount=0;plannerParseValidCount=0;plannerParseMode="NONE";',
     'plannerParseObjectCount=0;plannerParseValidCount=0;plannerParseSegmentCount=0;plannerParseMode="NONE";',
     'parser reset')
once('ArrayList<String> segments=extractTopLevelJsonObjects(x);',
     'ArrayList<String> segments=extractTopLevelJsonObjects(x);plannerParseSegmentCount=segments.size();',
     'segment count')

# Tighten the primary wire-format instruction. The executor still accepts only a
# validated bounded JSON action; no prose or relaxed grammar becomes executable.
method('buildPlannerPrompt',r'''    private String buildPlannerPrompt(){
        try{
            JSONObject ctx=buildPlannerContext();JSONArray hist=new JSONArray();for(String x:plannerHistory){try{hist.put(new JSONObject(x));}catch(Exception ignored){}}
            ctx.put("execution_history",hist);ctx.put("planner_iteration",plannerIteration);ctx.put("blind_build_marker",BLIND_BUILD_MARKER);
            String rules="You are the semantic control-plane Planner inside the user's existing ChatGPT session. The APK was frozen before the puzzle was known. Solve only from the supplied evidence. Return exactly one executable JSON object and nothing else. The first character of your response MUST be { and the last character MUST be }. Use standard ASCII JSON double quotes, not smart quotes and not backslash-escaped quotes around keys. No markdown, code fence, prose, explanation, or chain-of-thought. Allowed actions: {\"version\":1,\"action\":\"GO_MAIN_CHAT\"}; {\"version\":1,\"action\":\"GO_CHAT\",\"chat_ref\":\"CHAT_1\"}; {\"version\":1,\"action\":\"READ_LAST_RESPONSE\",\"chat_ref\":\"MAIN\"}; {\"version\":1,\"action\":\"SEND\",\"chat_ref\":\"MAIN\",\"text\":\"message\"}; {\"version\":1,\"action\":\"DONE\"}. Choose only one action. Never invent a chat_ref. SEND only if the semantic task requires a new message. If the demonstrated task is complete, emit DONE. Treat Temporary snapshots as evidence only; they are not navigable chat_refs. CONTEXT=";
            String p=rules+ctx.toString();return p.length()<=MAX_PLANNER_PROMPT_CHARS?p:"";
        }catch(Exception e){return "";}
    }

''',rettype='String')

# Same-room format recovery: one non-material model turn may rewrite the immediately
# preceding Planner answer, but may not re-plan. FORMAT_ERROR is deliberately not
# executable by validatePlannerActionObject, so uncertainty remains fail-closed.
repair=r'''    private String buildPlannerFormatRepairPrompt(){
        String p="FORMAT REPAIR ONLY. Your immediately previous assistant answer was not accepted by the local strict JSON action parser. Do NOT re-plan, reconsider, choose a different action, add new reasoning, or change the intended message text. Rewrite only that immediately previous intended action as exactly one JSON object and nothing else. The first character MUST be { and the last character MUST be }. Use standard ASCII JSON double quotes, with no markdown/code fence/prose and no backslash-escaped quotes around keys. Allowed executable forms are: {\"version\":1,\"action\":\"GO_MAIN_CHAT\"}; {\"version\":1,\"action\":\"GO_CHAT\",\"chat_ref\":\"CHAT_1\"}; {\"version\":1,\"action\":\"READ_LAST_RESPONSE\",\"chat_ref\":\"MAIN\"}; {\"version\":1,\"action\":\"SEND\",\"chat_ref\":\"MAIN\",\"text\":\"message\"}; {\"version\":1,\"action\":\"DONE\"}. Preserve any original chat_ref and SEND text exactly. If the previous answer cannot be represented as exactly one of those actions without changing its semantic intent, return exactly {\"version\":1,\"action\":\"FORMAT_ERROR\"}.";
        return p.length()<=MAX_PLANNER_PROMPT_CHARS?p:"";
    }

'''
pos=s.find('    private void handlePlannerResponse(')
assert pos>=0,'handlePlannerResponse insertion point'
s=s[:pos]+repair+s[pos:]

# One repair attempt per fresh Planner iteration. Multiple valid actions remain an
# ambiguity and are never delegated to the repair turn for choosing among them.
once('plannerPhase="SEND_PLANNER_PACKET";String packet=buildPlannerPrompt();',
     'plannerPhase="SEND_PLANNER_PACKET";plannerFormatRepairAttempts=0;String packet=buildPlannerPrompt();',
     'repair reset per planner iteration')

method('handlePlannerResponse',r'''    private void handlePlannerResponse(JSONObject o){
        if(!plannerRunning)return;
        String raw=o.optString("last_assistant_text","").trim();
        String responseHash=o.optString("last_assistant_hash","-");
        JSONObject action=parsePlannerAction(raw);
        if(action==null){
            JSONObject st=sanitizedState(o);put(st,"planner_response_hash",responseHash);put(st,"planner_parse_segments",plannerParseSegmentCount);put(st,"planner_parse_json_objects",plannerParseObjectCount);put(st,"planner_parse_valid_actions",plannerParseValidCount);put(st,"planner_parse_mode",plannerParseMode);put(st,"planner_format_repair_attempts",plannerFormatRepairAttempts);
            if(plannerParseValidCount>1){emit("PLANNER_PLAN","PLANNER_RESPONSE_AMBIGUOUS_MULTIPLE_ACTIONS",st);plannerFail("PLANNER_RESPONSE_AMBIGUOUS_MULTIPLE_ACTIONS");return;}
            if(plannerFormatRepairAttempts<1){
                plannerFormatRepairAttempts++;
                put(st,"planner_format_repair_attempts",plannerFormatRepairAttempts);emit("PLANNER_PLAN","PLANNER_RESPONSE_FORMAT_REPAIR_REQUESTED",st);
                String repair=buildPlannerFormatRepairPrompt();if(repair==null||repair.length()==0||repair.length()>MAX_PLANNER_PROMPT_CHARS){plannerFail("PLANNER_FORMAT_REPAIR_PACKET_INVALID");return;}
                autoWriteAndSend(repair,"PLANNER_PROMPT");return;
            }
            emit("PLANNER_PLAN","PLANNER_RESPONSE_INVALID_AFTER_FORMAT_REPAIR",st);plannerFail("PLANNER_RESPONSE_INVALID_AFTER_FORMAT_REPAIR");return;
        }
        String kind=action.optString("action","");String ref=action.optString("chat_ref","MAIN");String text=action.optString("text","");
        plannerActionCount++;
        JSONObject st=sanitizedState(o);put(st,"planner_response_hash",responseHash);put(st,"planner_action",kind);put(st,"planner_target_ref",ref);put(st,"planner_text_hash",text.isEmpty()?"-":hashNorm(text));put(st,"planner_text_chars",text.length());put(st,"planner_parse_segments",plannerParseSegmentCount);put(st,"planner_parse_json_objects",plannerParseObjectCount);put(st,"planner_parse_valid_actions",plannerParseValidCount);put(st,"planner_parse_mode",plannerParseMode);put(st,"planner_format_repair_attempts",plannerFormatRepairAttempts);
        plannerPhase="PLAN_ACCEPTED";emit("PLANNER_PLAN","PASS_BOUNDED_PLANNER_ACTION_PARSED",st);
        addPlannerHistory(action,"PLAN_ACCEPTED",null);
        executePlannerAction(action,o);
    }

''')

# New-run reset also clears any unresolved repair state.
once('diagnosticRing.clear(); remoteTelemetryPosts=0;',
     'diagnosticRing.clear(); remoteTelemetryPosts=0; plannerFormatRepairAttempts=0;',
     'run repair reset')

# Telemetry config lineage.
s=s.replace("TelemetryConfigV73","TelemetryConfigV74")
ACT.write_text(s)
assert OLD.exists();OLD.unlink()
cfg=(PKG/"TelemetryConfigV73.java").read_text()
(PKG/"TelemetryConfigV74.java").write_text(cfg.replace("TelemetryConfigV73","TelemetryConfigV74"))
(PKG/"TelemetryConfigV73.java").unlink()

# Version/package continuity.
g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+74\b","versionCode 75",gs);gs=gs.replace("0.71-stable-diag-semantic-planner-execution-hardened","0.72-stable-diag-semantic-planner-format-repair");g.write_text(gs)
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorPlannerCoreV73Activity","OrchestratorPlannerCoreV74Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms and "@xml/cp_accessibility_service_v51" in ms
mf.write_text(ms)

# Regression/contract gates for the evidenced parser family and inherited safety.
out=ACT.read_text()
for required in [
    'buildPlannerFormatRepairPrompt','plannerFormatRepairAttempts<1','PLANNER_RESPONSE_FORMAT_REPAIR_REQUESTED',
    'PLANNER_RESPONSE_INVALID_AFTER_FORMAT_REPAIR','PLANNER_RESPONSE_AMBIGUOUS_MULTIPLE_ACTIONS','planner_parse_segments',
    'FORMAT_ERROR','autoWriteAndSend(repair,"PLANNER_PROMPT")','executePlannerAction(action,o);',
    'pageFinishedEpoch==documentEpoch','activeReadSerial','PLANNER_ACTION_SOURCE_NOT_PROVEN_FRESH_TEMP',
    'PASS_TARGET_RESPONSE_COMPLETE_BY_ACTION_RECEIPT','PUZZLE_UNKNOWN_AT_BUILD_TIME','TelemetryConfigV74'
]: assert required in out,required
for forbidden in [
    'postDelayed','Thread.sleep','setTimeout(','setInterval(','SAMPLE_MS','SEND_POLL_MS','RESPONSE_TIMEOUT_MS',
    'ScheduledExecutorService','TimerTask','pollPlannerNormalHome','pollPlannerTempReceipt','pollAutoComposerReceipt',
    'pollAutoSendReceipt','pollAutoResponse','pollPlannerNavReceipt','pollSendReceipt','confirmAutoSendReceipt',
    'elementFromPoint','document.evaluate','dispatchTouchEvent(','performClick(','ACTION_SET_PROGRESS','CookieManager',
    'getCookie(','addJavascriptInterface'
]: assert forbidden not in out,forbidden
assert out.count('.click();')==2,out.count('.click();')
assert 'applicationId \'com.homayounisaghar.chatgptwebviewprobe.diag\'' in g.read_text()
assert 'versionCode 75' in g.read_text()
assert "versionName '0.72-stable-diag-semantic-planner-format-repair'" in g.read_text()
print('PASS v0.72 parser-family audit: strict bounded action parser + one same-room format repair; ambiguity fail-closed; zero-clock execution preserved')
