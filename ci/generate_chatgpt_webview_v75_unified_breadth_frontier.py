#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.73 minimizes remaining APK/test round-trips by preserving the proven v0.72
# Planner Core unchanged while adding one dense, read-only current-account/UI
# breadth census. The census targets the two largest open capability families:
# resources/downloads and tools/modes, while also inventorying current visible
# ChatGPT surfaces. It intentionally performs zero additional page clicks/writes.
runpy.run_path("ci/generate_chatgpt_webview_v74_planner_format_repair.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorPlannerCoreV74Activity.java"
ACT=PKG/"OrchestratorUnifiedBreadthV75Activity.java"
s=OLD.read_text()

def once(old,new,label):
    global s
    n=s.count(old)
    assert n==1,(label,n)
    s=s.replace(old,new,1)

# Identity / update continuity.
s=s.replace("OrchestratorPlannerCoreV74Activity","OrchestratorUnifiedBreadthV75Activity")
s=s.replace('SCHEMA="cp-v74-planner-core-format-repair-v1"','SCHEMA="cp-v75-unified-breadth-frontier-v1"')
s=s.replace('SCENARIO="same-apk-semantic-planner-core-format-repair"','SCENARIO="unified-current-ui-resource-tool-breadth-frontier"')
s=s.replace('getSharedPreferences("cp_v74_planner_core",MODE_PRIVATE)','getSharedPreferences("cp_v75_unified_breadth",MODE_PRIVATE)')
s=s.replace('testId="cp72-"+UUID.randomUUID();','testId="cp73-"+UUID.randomUUID();')
s=s.replace('v0.72 EVENT-DRIVEN Planner format-repair hardened ready.','v0.73 Unified Breadth + proven Planner ready.')

# Add one dedicated one-tap read-only frontier control without disturbing the
# existing Planner/STOP controls or the manual diagnostics retained below them.
anchor='''        root.addView(row3,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(42)));

        draftInput=new EditText(this);'''
insert='''        root.addView(row3,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(42)));

        LinearLayout row4=new LinearLayout(this); row4.setOrientation(LinearLayout.HORIZONTAL);
        Button breadth=new Button(this); breadth.setText("RUN FULL BREADTH"); breadth.setOnClickListener(v->runFullBreadth());
        row4.addView(breadth,new LinearLayout.LayoutParams(0,dp(42),1f));
        root.addView(row4,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(42)));

        draftInput=new EditText(this);'''
once(anchor,insert,"breadth control")

# Read-only breadth inventory. Raw chat text, raw labels, URLs/query strings,
# filenames and HTML never leave the page. Only counts/booleans and aggregate
# semantic fingerprints are returned to Android/telemetry.
methods=r'''    private void runFullBreadth(){
        if(learning||plannerRunning){status.setText("Breadth census blocked while LEARN/Planner is active.");return;}
        testId="cp73-"+UUID.randomUUID();startedMs=System.currentTimeMillis();telemetrySeq=0;remoteTelemetryPosts=0;
        JSONObject start=baseState();put(start,"breadth_version",1);put(start,"read_only",true);put(start,"planner_regression_preserved",true);
        emit("PLANNER_OBSERVATION","BREADTH_CENSUS_STARTED_READ_ONLY",start);
        status.setText("Breadth census running read-only on the currently materialized ChatGPT UI...");
        eval(breadthCensusJs(),o->{
            JSONObject st=baseState();
            put(st,"breadth_version",1);put(st,"read_only",true);put(st,"success",o.optBoolean("success",false));
            String[] ints={"materialized_turns","global_visible_controls","global_visible_links","composer_count","send_count","model_trigger_count","add_trigger_count","tools_trigger_count","voice_trigger_count","dictation_trigger_count","temporary_trigger_count","work_trigger_count","search_trigger_count","deep_research_trigger_count","project_trigger_count","apps_plugins_trigger_count","settings_trigger_count","resource_anchor_count","same_origin_resource_count","cross_origin_resource_count","blob_resource_count","data_resource_count","citation_like_count","file_action_candidate_count","download_action_candidate_count","resource_alias_group_count","resource_alias_max_occurrence","resource_unique_semantic_count"};
            for(String k:ints)put(st,k,o.optInt(k,0));
            put(st,"control_semantic_hash",o.optString("control_semantic_hash","-"));
            put(st,"resource_semantic_hash",o.optString("resource_semantic_hash","-"));
            put(st,"has_resource_frontier",o.optInt("resource_anchor_count",0)>0||o.optInt("file_action_candidate_count",0)>0);
            put(st,"has_tools_frontier",o.optInt("tools_trigger_count",0)>0||o.optInt("add_trigger_count",0)>0||o.optInt("search_trigger_count",0)>0||o.optInt("deep_research_trigger_count",0)>0);
            put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);put(st,"raw_url_remote",false);put(st,"cookies_tokens_accessed",false);put(st,"page_ui_writes_delta",0);
            if(!o.optBoolean("success",false)){
                emit("PLANNER_FINAL","BREADTH_CENSUS_FAILED_READ_ONLY",st);
                status.setText("Breadth census failed read-only. No page action was dispatched.");return;
            }
            emit("PLANNER_OBSERVATION","PASS_READ_ONLY_CURRENT_UI_RESOURCE_TOOL_CENSUS",st);
            emit("PLANNER_FINAL","PASS_UNIFIED_BREADTH_FRONTIER_CENSUS_COMPLETE",st);
            status.setText("Breadth PASS. turns="+o.optInt("materialized_turns",0)+" resources="+o.optInt("resource_unique_semantic_count",0)+" aliases="+o.optInt("resource_alias_group_count",0)+" tools/add="+(o.optInt("tools_trigger_count",0)+o.optInt("add_trigger_count",0))+". Tell ChatGPT the test finished.");
        });
    }

    private String breadthCensusJs(){
        return "(function(){try{"+
            "const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const H=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return ('00000000'+(h>>>0).toString(16)).slice(-8);};"+
            "const V=e=>{if(!e||!e.isConnected)return false;const s=getComputedStyle(e);const r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true'&&r.width>0&&r.height>0;};"+
            "const D=e=>N([e.tagName||'',e.getAttribute('role')||'',e.getAttribute('aria-label')||'',e.getAttribute('title')||'',e.getAttribute('data-testid')||'',e.getAttribute('name')||'',(e.innerText||e.textContent||'').slice(0,180)].join(' '));"+
            "const turns=Array.from(document.querySelectorAll('[data-message-author-role]'));"+
            "const allControls=Array.from(document.querySelectorAll('button,[role=button],[role=menuitem],[role=option],input[type=file],textarea,[contenteditable],[role=textbox]')).filter(V);"+
            "const chromeControls=allControls.filter(e=>!e.closest('[data-message-author-role]'));"+
            "const links=Array.from(document.querySelectorAll('a[href]')).filter(V);"+
            "const cls={model:/\\b(model|gpt|latest|sol|luna)\\b/,add:/\\b(add|attach|attachment|upload|file|photo|image)\\b/,tools:/\\btools?\\b/,voice:/\\bvoice\\b/,dictation:/\\b(dictat|microphone|mic)\\b/,temporary:/\\btemporary\\b/,work:/\\bwork\\b/,search:/\\bsearch\\b/,deep:/deep research|\\bresearch\\b/,project:/\\bprojects?\\b/,apps:/\\b(apps?|plugins?|connectors?)\\b/,settings:/\\bsettings?\\b/};"+
            "const count=k=>chromeControls.reduce((n,e)=>n+(cls[k].test(D(e))?1:0),0);"+
            "const composers=allControls.filter(e=>{const d=D(e);return e.id==='prompt-textarea'||d.includes('composer')||d.includes('message chatgpt')||((e.tagName==='TEXTAREA'||e.getAttribute('contenteditable')==='true'||e.getAttribute('role')==='textbox')&&!e.closest('[data-message-author-role]'));});"+
            "const sends=chromeControls.filter(e=>{const d=D(e);return /\\b(send|submit)\\b/.test(d)&&!e.hasAttribute('disabled')&&e.getAttribute('aria-disabled')!=='true';});"+
            "let same=0,cross=0,blob=0,data=0,citation=0,fileAction=0,downloadAction=0;const keys=[];const occ=new Map();"+
            "const safeHref=h=>{try{if(h.startsWith('blob:'))return 'blob:';if(h.startsWith('data:'))return 'data:';const u=new URL(h,location.href);return u.protocol+'//'+u.host+u.pathname;}catch(_){return 'other:';}};"+
            "turns.forEach((t,ti)=>{const acts=Array.from(t.querySelectorAll('a[href],button,[role=button]')).filter(V);acts.forEach(e=>{const d=D(e);const raw=e.getAttribute('href')||'';const sh=raw?safeHref(raw):'';let kind='ACTION';if(raw){if(raw.startsWith('blob:')){blob++;kind='BLOB';}else if(raw.startsWith('data:')){data++;kind='DATA';}else{try{const u=new URL(raw,location.href);if(u.origin===location.origin){same++;kind='SAME';}else{cross++;kind='CROSS';}}catch(_){kind='OTHER';}}}if(/citation|source|reference/.test(d)||N(e.getAttribute('data-testid')||'').includes('citation'))citation++;if(/file|attachment|download/.test(d)){fileAction++;kind+='|FILE';}if(/download|save/.test(d))downloadAction++;if(raw||/file|attachment|download|citation|source|reference/.test(d)){const key=ti+'|'+kind+'|'+sh+'|'+H(d);keys.push(key);occ.set(key,(occ.get(key)||0)+1);}});});"+
            "let aliasGroups=0,aliasMax=0;for(const n of occ.values()){if(n>1)aliasGroups++;if(n>aliasMax)aliasMax=n;}"+
            "const controlSig=chromeControls.map(e=>H(D(e))).sort().join('|');const resourceSig=Array.from(new Set(keys)).sort().join('|');"+
            "return JSON.stringify({success:true,materialized_turns:turns.length,global_visible_controls:allControls.length,global_visible_links:links.length,composer_count:composers.length,send_count:sends.length,model_trigger_count:count('model'),add_trigger_count:count('add'),tools_trigger_count:count('tools'),voice_trigger_count:count('voice'),dictation_trigger_count:count('dictation'),temporary_trigger_count:count('temporary'),work_trigger_count:count('work'),search_trigger_count:count('search'),deep_research_trigger_count:count('deep'),project_trigger_count:count('project'),apps_plugins_trigger_count:count('apps'),settings_trigger_count:count('settings'),resource_anchor_count:keys.length,same_origin_resource_count:same,cross_origin_resource_count:cross,blob_resource_count:blob,data_resource_count:data,citation_like_count:citation,file_action_candidate_count:fileAction,download_action_candidate_count:downloadAction,resource_alias_group_count:aliasGroups,resource_alias_max_occurrence:aliasMax,resource_unique_semantic_count:new Set(keys).size,control_semantic_hash:H(controlSig),resource_semantic_hash:H(resourceSig)});"+
        "}catch(e){return JSON.stringify({success:false,error_class:'BREADTH_JS_EXCEPTION'});}})()";
    }

'''
needle='    private void clearLocal(){'
pos=s.find(needle)
assert pos>=0,"clearLocal insertion point"
s=s[:pos]+methods+s[pos:]

# Telemetry config lineage.
s=s.replace("TelemetryConfigV74","TelemetryConfigV75")
ACT.write_text(s)
assert OLD.exists();OLD.unlink()
cfg=(PKG/"TelemetryConfigV74.java").read_text()
(PKG/"TelemetryConfigV75.java").write_text(cfg.replace("TelemetryConfigV74","TelemetryConfigV75"))
(PKG/"TelemetryConfigV74.java").unlink()

# Version/package/update continuity.
g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+75\b","versionCode 76",gs);gs=gs.replace("0.72-stable-diag-semantic-planner-format-repair","0.73-stable-diag-unified-breadth-frontier");g.write_text(gs)
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorPlannerCoreV74Activity","OrchestratorUnifiedBreadthV75Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms and "@xml/cp_accessibility_service_v51" in ms
mf.write_text(ms)

# Regression gates: breadth is strictly read-only and inherited v0.72 execution
# semantics remain byte-generated from the same chain. No extra click primitive,
# coordinate action, cookie/token access, timers or private API path is introduced.
out=ACT.read_text()
for required in [
    'RUN FULL BREADTH','runFullBreadth','breadthCensusJs','PASS_READ_ONLY_CURRENT_UI_RESOURCE_TOOL_CENSUS',
    'PASS_UNIFIED_BREADTH_FRONTIER_CENSUS_COMPLETE','resource_alias_group_count','resource_alias_max_occurrence',
    'model_trigger_count','tools_trigger_count','deep_research_trigger_count','apps_plugins_trigger_count',
    'plannerFormatRepairAttempts<1','PLANNER_RESPONSE_FORMAT_REPAIR_REQUESTED','executePlannerAction(action,o);',
    'pageFinishedEpoch==documentEpoch','PLANNER_ACTION_SOURCE_NOT_PROVEN_FRESH_TEMP','TelemetryConfigV75'
]: assert required in out,required
for forbidden in [
    'Thread.sleep','setTimeout(','setInterval(','ScheduledExecutorService','TimerTask','elementFromPoint','document.evaluate',
    'dispatchTouchEvent(','performClick(','ACTION_SET_PROGRESS','CookieManager','getCookie(','addJavascriptInterface'
]: assert forbidden not in out,forbidden
assert out.count('.click();')==2,out.count('.click();')
assert 'applicationId \'com.homayounisaghar.chatgptwebviewprobe.diag\'' in g.read_text()
assert 'versionCode 76' in g.read_text()
assert "versionName '0.73-stable-diag-unified-breadth-frontier'" in g.read_text()
print('PASS v0.73 unified breadth audit: current-account/resource/tool census is read-only; v0.72 Planner execution preserved; update identity advanced')
