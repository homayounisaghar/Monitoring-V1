#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v103_dashboard_assistant_repair.py',run_name='__main__')

old_java=PKG/'OrchestratorDashboardV103AssistantRepairActivity.java'
new_java=PKG/'OrchestratorDashboardV104LiveTempControlActivity.java'
s=old_java.read_text()
for a,b in [
    ('OrchestratorDashboardV103AssistantRepairActivity','OrchestratorDashboardV104LiveTempControlActivity'),
    ('cp-v103-dashboard-semantic-temp-telemetry-audio-source-v1','cp-v104-dashboard-live-temp-control-v1'),
    ('dashboard-semantic-temp-telemetry-audio-source','dashboard-live-temp-control'),
    ('cp909-','cp910-'),
    ('cp_v103_','cp_v104_'),
    ('TelemetryConfigV103','TelemetryConfigV104'),
    ('MIC_PERMISSION_REQUEST=909','MIC_PERMISSION_REQUEST=910'),
]:
    assert a in s,a
    s=s.replace(a,b)

s=s.replace('Planner: opening a normal ChatGPT surface and proving semantic Temporary-entry state...',
            'Planner: locating one live Temporary Chat control on the current normal surface...',1)

old='''            if("WAIT_SEMANTIC_NORMAL".equals(plannerPhase)){\n                boolean normal="complete".equals(o.optString("ready",""))&&"NORMAL".equals(o.optString("semantic_temp_state",""))&&o.optInt("temp_candidate_count",0)==1&&o.optInt("composer_candidate_count",0)==1&&o.optInt("stop_candidate_count",0)==0;\n                normalEntryStableHits=normal?normalEntryStableHits+1:0;\n                if(normalEntryStableHits<2){plannerLater(g);return;}\n                plannerResult.setText("Planner: stable semantic NORMAL state proved; entering Temporary Chat...");emit("PLANNER_SEMANTIC_NORMAL_CONFIRMED",null,"CONFIRMED",jsonExtra("request_digest",plannerRequestDigest,"route_class",o.optString("route_class","UNKNOWN"),"turn_count_diag",o.optInt("turn_count",-1)));plannerEnterTemp(g);return;\n            }'''
new='''            if("WAIT_SEMANTIC_NORMAL".equals(plannerPhase)){\n                boolean normal="complete".equals(o.optString("ready",""))&&"NORMAL".equals(o.optString("semantic_temp_state",""))&&o.optInt("temp_candidate_count",0)==1&&o.optInt("composer_candidate_count",0)==1&&o.optInt("stop_candidate_count",0)==0;\n                normalEntryStableHits=normal?normalEntryStableHits+1:0;\n                if(plannerPolls==1||plannerPolls%5==0)emit("PLANNER_ENTRY_SCAN",null,normal?"CONFIRMED":"UNKNOWN",jsonExtra("request_digest",plannerRequestDigest,"semantic_temp_state",o.optString("semantic_temp_state","UNKNOWN"),"temp_candidate_count",o.optInt("temp_candidate_count",-1),"composer_candidate_count",o.optInt("composer_candidate_count",-1),"stop_candidate_count",o.optInt("stop_candidate_count",-1),"route_class",o.optString("route_class","UNKNOWN"),"temporary_hint",o.optBoolean("temporary_hint",false),"state_fingerprint",o.optString("state_fingerprint","-")));\n                if(normalEntryStableHits<2){plannerLater(g);return;}\n                plannerResult.setText("Planner: stable unique Temporary control proved in NORMAL mode; entering Temporary Chat...");emit("PLANNER_SEMANTIC_NORMAL_CONFIRMED",null,"CONFIRMED",jsonExtra("request_digest",plannerRequestDigest,"route_class",o.optString("route_class","UNKNOWN"),"turn_count_diag",o.optInt("turn_count",-1),"temp_candidate_count",o.optInt("temp_candidate_count",-1)));plannerEnterTemp(g);return;\n            }'''
assert s.count(old)==1,('WAIT_SEMANTIC_NORMAL',s.count(old))
s=s.replace(old,new,1)

# tempControlStateJs: stop depending on frozen label/struct hashes. Require one
# visible enabled button in the Temporary semantic family and classify active
# state from live URL/composer/ARIA/data-state/label cues.
old="T.push({e:e,tag:tag,role:role,lh:lh,th:th,ds:DS(e),sel:e.getAttribute('aria-selected')==='true'?1:0,prs:e.getAttribute('aria-pressed')==='true'?1:0,exp:e.getAttribute('aria-expanded')==='true'?1:0,dis:e.hasAttribute('disabled')?1:0,hc:hc,sh:sh});}const urlhint="
new="T.push({e:e,tag:tag,role:role,lh:lh,th:th,ds:DS(e),sel:e.getAttribute('aria-selected')==='true'?1:0,prs:e.getAttribute('aria-pressed')==='true'?1:0,exp:e.getAttribute('aria-expanded')==='true'?1:0,dis:e.hasAttribute('disabled')?1:0,hc:hc,sh:sh,ah:(/(turn off|disable|exit|leave|end|close).*temporary|temporary.*(turn off|disable|exit|leave|end|close)/.test(N(label))?1:0)});}const urlhint="
assert s.count(old)==1,('temp state push',s.count(old));s=s.replace(old,new,1)
old="const E=T.filter(x=>urlhint?(x.lh==='ae0e16e6'&&x.sh==='34d052a8'):(x.lh==='1a957a52'&&x.sh==='b9c97d1e')),c=E.length===1?E[0]:null;let comphint=false;"
new="const E=T.filter(x=>x.tag==='button'&&x.role==='button'&&x.hc==='NONE'&&x.dis===0),c=E.length===1?E[0]:null;let comphint=false;"
assert s.count(old)==1,('temp state dynamic filter',s.count(old));s=s.replace(old,new,1)
old="candidate_disabled:c?c.dis:-1,candidate_href_class:c?c.hc:'-',candidate_struct_hash:c?c.sh:'-'});"
new="candidate_disabled:c?c.dis:-1,candidate_href_class:c?c.hc:'-',candidate_struct_hash:c?c.sh:'-',candidate_active_hint:c?c.ah:0});"
assert s.count(old)==1,('temp state active hint',s.count(old));s=s.replace(old,new,1)

# plannerReadJs uses the same live semantic family and active-state cues.
old="TT.push({tag:tag,role:role,lh:lh,th:th,ds:DS(e),sel:e.getAttribute('aria-selected')==='true'?1:0,prs:e.getAttribute('aria-pressed')==='true'?1:0,exp:e.getAttribute('aria-expanded')==='true'?1:0,dis:e.hasAttribute('disabled')?1:0,hc:hc,sh:sh});}const urlhint="
new="TT.push({tag:tag,role:role,lh:lh,th:th,ds:DS(e),sel:e.getAttribute('aria-selected')==='true'?1:0,prs:e.getAttribute('aria-pressed')==='true'?1:0,exp:e.getAttribute('aria-expanded')==='true'?1:0,dis:e.hasAttribute('disabled')?1:0,hc:hc,sh:sh,ah:(/(turn off|disable|exit|leave|end|close).*temporary|temporary.*(turn off|disable|exit|leave|end|close)/.test(N(label))?1:0)});}const urlhint="
assert s.count(old)==1,('planner temp push',s.count(old));s=s.replace(old,new,1)
old="const E=TT.filter(x=>urlhint?(x.lh==='ae0e16e6'&&x.sh==='34d052a8'):(x.lh==='1a957a52'&&x.sh==='b9c97d1e')),tc=E.length===1?E[0]:null;let semState='UNKNOWN';if(tc&&tc.tag==='button'&&tc.role==='button'&&tc.th==='811c9dc5'&&tc.ds==='NONE'&&tc.sel===0&&tc.prs===0&&tc.exp===0&&tc.dis===0&&tc.hc==='NONE'){if(tc.lh==='1a957a52'&&tc.sh==='b9c97d1e'&&!urlhint)semState='NORMAL';else if(tc.lh==='ae0e16e6'&&tc.sh==='34d052a8'&&urlhint)semState='TEMP';}"
new="const E=TT.filter(x=>x.tag==='button'&&x.role==='button'&&x.hc==='NONE'&&x.dis===0),tc=E.length===1?E[0]:null;let comphint=false;for(const e of CA){const z=N((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('placeholder')||''));if(z.includes('temporary')||z==='temp'){comphint=true;break;}}const activeTemp=!!tc&&(urlhint||comphint||tc.sel===1||tc.prs===1||tc.ds==='ACTIVE'||tc.ds==='OPEN'||tc.ah===1);let semState='UNKNOWN';if(tc)semState=activeTemp?'TEMP':'NORMAL';"
assert s.count(old)==1,('planner temp dynamic classify',s.count(old));s=s.replace(old,new,1)

# Replace the old hash-pinned actuator with a one-shot unique semantic control
# actuator. It still fails closed on 0/multiple candidates or wrong live state.
start=s.index('    private String tempClickJs(boolean enter){')
end=s.index('    private String plannerReadJs(){',start)
method=r'''    private String tempClickJs(boolean enter){
        return "(function(){try{const ENTER="+(enter?"true":"false")+";const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const DS=e=>{const v=N(e.getAttribute('data-state'));if(['active','selected','checked','on'].includes(v))return 'ACTIVE';if(v==='open')return 'OPEN';return v?'OTHER':'NONE';};const SEM=(label,tid)=>{const x=N(label),t=N(tid),z=x+' '+t;return (z.includes('temporary')||x==='temp'||t.includes('temp'))?'TEMP':'OTHER';};const Q=Array.from(document.querySelectorAll('button,[role=button],[data-testid]')).filter(V),T=[];for(const e of Q){const tag=(e.tagName||'').toLowerCase(),role=N(e.getAttribute('role'))||((tag==='button')?'button':'none'),label=e.getAttribute('aria-label')||e.innerText||e.textContent||'',tid=e.getAttribute('data-testid')||'';if(SEM(label,tid)!=='TEMP')continue;const href=e.getAttribute('href')||'';T.push({e:e,tag:tag,role:role,href:href,dis:e.hasAttribute('disabled')?1:0,sel:e.getAttribute('aria-selected')==='true'?1:0,prs:e.getAttribute('aria-pressed')==='true'?1:0,ds:DS(e),ah:(/(turn off|disable|exit|leave|end|close).*temporary|temporary.*(turn off|disable|exit|leave|end|close)/.test(N(label))?1:0)});}const M=T.filter(x=>x.tag==='button'&&x.role==='button'&&!x.href&&x.dis===0);if(M.length!==1)return JSON.stringify({success:false,reason:'SEMANTIC_TEMP_CONTROL_COUNT',match_count:M.length,dispatched:false,click_observed:false});const t=M[0];const urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));let comphint=false;for(const e of Array.from(document.querySelectorAll('textarea,[contenteditable=true],[role=textbox]')).filter(V)){const z=N((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('placeholder')||''));if(z.includes('temporary')||z==='temp'){comphint=true;break;}}const active=urlhint||comphint||t.sel===1||t.prs===1||t.ds==='ACTIVE'||t.ds==='OPEN'||t.ah===1;if(ENTER&&active)return JSON.stringify({success:false,reason:'EXPECTED_NORMAL_BUT_TEMP_ACTIVE',match_count:1,dispatched:false,click_observed:false});if(!ENTER&&!active)return JSON.stringify({success:false,reason:'EXPECTED_TEMP_BUT_NORMAL_ACTIVE',match_count:1,dispatched:false,click_observed:false});let observed=false;t.e.addEventListener('click',()=>{observed=true;},{capture:true,once:true});t.e.click();return JSON.stringify({success:true,reason:'UNIQUE_SEMANTIC_TEMP_CONTROL_CLICK',match_count:1,dispatched:true,click_observed:observed});}catch(e){return JSON.stringify({success:false,reason:'TEMP_CLICK_EXCEPTION',match_count:0,dispatched:false,click_observed:false});}})();";
    }

'''
s=s[:start]+method+s[end:]

for h in ['1a957a52','b9c97d1e','ae0e16e6','34d052a8','811c9dc5']:
    assert h not in s,h
assert 'PLANNER_ENTRY_SCAN' in s
assert 'UNIQUE_SEMANTIC_TEMP_CONTROL_CLICK' in s
assert s.count('targetChatEffectDispatches++')==1
new_java.write_text(s);old_java.unlink()

# Dynamic semantic gate used for entry/receipt/exit/restore.
(PKG/'TemporaryChatSignaturesV1.java').write_text('''package com.homayounisaghar.chatgptwebviewprobe;\n\nimport org.json.JSONObject;\n\nfinal class TemporaryChatSignaturesV1 {\n    enum State { NORMAL, TEMP, UNKNOWN }\n    private TemporaryChatSignaturesV1() {}\n    static State classify(JSONObject o) {\n        if (o == null || !o.optBoolean("success", false)) return State.UNKNOWN;\n        if (!"complete".equals(o.optString("ready", ""))) return State.UNKNOWN;\n        if (o.optInt("temp_candidate_count", 0) != 1) return State.UNKNOWN;\n        if (!"button".equals(o.optString("candidate_tag", ""))) return State.UNKNOWN;\n        if (!"button".equals(o.optString("candidate_role", ""))) return State.UNKNOWN;\n        if (!"NONE".equals(o.optString("candidate_href_class", ""))) return State.UNKNOWN;\n        if (o.optInt("candidate_disabled", 1) != 0) return State.UNKNOWN;\n        boolean active = o.optBoolean("url_temp_hint", false)\n                || o.optBoolean("composer_temp_hint", false)\n                || o.optInt("candidate_selected", 0) == 1\n                || o.optInt("candidate_pressed", 0) == 1\n                || "ACTIVE".equals(o.optString("candidate_data_state", ""))\n                || "OPEN".equals(o.optString("candidate_data_state", ""))\n                || o.optInt("candidate_active_hint", 0) == 1;\n        return active ? State.TEMP : State.NORMAL;\n    }\n    static boolean exactEntryGate(JSONObject o) { return classify(o) == State.NORMAL; }\n    static boolean exactExitGate(JSONObject o) { return classify(o) == State.TEMP; }\n}\n''')

# Promote telemetry config identity without changing the injected endpoint.
old_cfg=PKG/'TelemetryConfigV103.java';new_cfg=PKG/'TelemetryConfigV104.java'
c=old_cfg.read_text().replace('TelemetryConfigV103','TelemetryConfigV104')
new_cfg.write_text(c);old_cfg.unlink()

gradle=ROOT/'app/build.gradle';g=gradle.read_text()
assert g.count('versionCode 104')==1
assert g.count("versionName '0.90.9-stable-dashboard-semantic-temp-telemetry-audio-source'")==1
g=g.replace('versionCode 104','versionCode 105',1).replace("versionName '0.90.9-stable-dashboard-semantic-temp-telemetry-audio-source'","versionName '0.91.0-stable-dashboard-live-temp-control'",1)
gradle.write_text(g)

man=ROOT/'app/src/main/AndroidManifest.xml';m=man.read_text()
assert m.count('OrchestratorDashboardV103AssistantRepairActivity')==1
m=m.replace('OrchestratorDashboardV103AssistantRepairActivity','OrchestratorDashboardV104LiveTempControlActivity',1)
man.write_text(m)

print('PASS v0.91.0 live semantic Temporary control + scan telemetry generator')
