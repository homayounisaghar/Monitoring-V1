#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.84: zero-effect diagnostic only.
# Preserve v0.83 admission, V64 authority, claim, and calibrated actuator setup,
# but instrument final pre-effect JS with sanitized stage markers and explicit
# exception classification. No Resource actuation is authorized in this build.
runpy.run_path("ci/generate_chatgpt_webview_v85_resource_fingerprint_drift_probe_fix2.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorResourceToolsV85Activity.java"
ACT=PKG/"OrchestratorResourceToolsV86Activity.java"
s=OLD.read_text()

# Advance generated identity while preserving behavior semantics.
s=s.replace("OrchestratorResourceToolsV85Activity","OrchestratorResourceToolsV86Activity")
s=s.replace("TelemetryConfigV85","TelemetryConfigV86")
s=s.replace("V85","V86").replace("v85","v86")
s=s.replace('SCHEMA="cp-v86-resource-fingerprint-drift-probe-v1"','SCHEMA="cp-v86-resource-final-stage-probe-v1"')
s=s.replace('SCENARIO="resource-fingerprint-component-drift-probe"','SCENARIO="resource-final-recert-stage-probe"')
s=s.replace('testId="cp83-"+UUID.randomUUID();','testId="cp84-"+UUID.randomUUID();')
s=s.replace('v0.83 Fingerprint drift diagnostic ready.','v0.84 Final re-certification stage diagnostic ready.')
s=s.replace('cp_v86_resource_fingerprint_drift_probe','cp_v86_resource_final_stage_probe')

# Replace the final JS only. Authority and Resource semantic predicate are unchanged.
pat=r'    private String assistantLocalResourceFinalV82Js\([^\n]*\)\{.*?\n    \}\n\n'
m=re.search(pat,s,re.S)
assert m,"final method not found"
final_method=r'''    private String assistantLocalResourceFinalV82Js(String expectedTurnFingerprint,boolean ignoredJsActuate){
        return "(function(){let stage='FINAL_STAGE_INIT';const SH=s=>{let h=2166136261>>>0;const q=(s||'').toString();for(let i=0;i<q.length;i++){h^=q.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};try{const expected="+jsV79(expectedTurnFingerprint)+";const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();const H=SH;const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const st=getComputedStyle(e);if(st.display==='none'||st.visibility==='hidden'||st.opacity==='0')return false;try{if(typeof e.checkVisibility==='function')return e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});}catch(_){}return true;};const SIG=e=>e?H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|'))):'-';const TXT=e=>{if(!e)return '';return (e.innerText||e.textContent||'').replace(/\\s+$/,'').trim();};const PROJ=raw=>{const q=(raw||'').toString().normalize('NFKC');let z='';for(let k=0;k<q.length;k++){const c=q.charCodeAt(k);if((c>=8203&&c<=8207)||(c>=8234&&c<=8238)||(c>=8288&&c<=8303)||c===65279)continue;z+=q[k];}return N(z);};stage='FINAL_STAGE_TURN_QUERY';const nodes=[];const seen=new Set();const add=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);nodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(add);stage='FINAL_STAGE_TURN_MAP';const turns=nodes.map(e=>{const a=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');const role=a?N(a.getAttribute('data-message-author-role')||'-'):'-';const raw=TXT(a),norm=N(raw),proj=PROJ(raw);return{el:e,author:a,role:role,content_hash:norm?H(norm):'-',norm_len:norm.length,projection_hash:proj?H(proj):'-',projection_len:proj.length};}).filter(t=>t.role==='user'||t.role==='assistant');stage='FINAL_STAGE_FINGERPRINT_BUILD';const precedingUser=i=>{for(let j=i-1;j>=0;j--)if(turns[j].role==='user')return turns[j];return null;};const FP=i=>{const t=turns[i];if(!t||t.role!=='assistant'||t.content_hash==='-')return '-';const u=precedingUser(i);return H(['assistant',t.content_hash,t.norm_len,u?u.content_hash:'-',u?u.norm_len:0].join('|'));};stage='FINAL_STAGE_MATCH_SCAN';const matches=[];let lastAssistant=-1,ao=0,lastOrdinal=-1;for(let i=0;i<turns.length;i++)if(turns[i].role==='assistant'){if(FP(i)===expected)matches.push(i);lastAssistant=i;lastOrdinal=ao++;}const assistantCount=ao,userCount=turns.filter(t=>t.role==='user').length;stage='FINAL_STAGE_DIAG_BUILD';const observed=lastAssistant>=0?turns[lastAssistant]:null,ou=lastAssistant>=0?precedingUser(lastAssistant):null;const diag={assistant_turn_count:assistantCount,user_turn_count:userCount,observed_assistant_ordinal:lastOrdinal,observed_assistant_content_hash:observed?observed.content_hash:'-',observed_assistant_norm_len:observed?observed.norm_len:-1,observed_preceding_user_hash:ou?ou.content_hash:'-',observed_preceding_user_norm_len:ou?ou.norm_len:-1,observed_assistant_projection_hash:observed?observed.projection_hash:'-',observed_assistant_projection_len:observed?observed.projection_len:-1,observed_preceding_user_projection_hash:ou?ou.projection_hash:'-',observed_preceding_user_projection_len:ou?ou.projection_len:-1,observed_last_assistant_fingerprint:lastAssistant>=0?FP(lastAssistant):'-',diagnostic_only:true,final_stage:stage,error_class:'-',failure_stage:'-',exception_name_class:'-',exception_family_hash:'-'};if(matches.length!==1)return JSON.stringify(Object.assign({success:true,same_assistant_turn:false,assistant_match_count:matches.length,semantic_candidate_count:0,ready:false,clicked:false,candidate_token:'-'},diag));const target=turns[matches[0]],author=target.author;if(!author)return JSON.stringify(Object.assign({success:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:0,ready:false,clicked:false,candidate_token:'-'},diag));stage='FINAL_STAGE_RESOURCE_SCAN';const depth=e=>{let d=0,p=e;while(p&&p!==target.el){d++;p=p.parentElement;}return d;};const good=[];for(const e of Array.from(author.querySelectorAll('a')).filter(V)){const hrefAttr=e.getAttribute('href');const noHref=hrefAttr===null||String(hrefAttr).trim()==='';const targetBlank=N(e.getAttribute('target')||'')==='_blank';const externalRel=/noopener|noreferrer|external/.test(N(e.getAttribute('rel')||''));const on=typeof e.onclick==='function'||e.hasAttribute('onclick');const st=getComputedStyle(e),ptr=N(st.cursor||'').includes('pointer'),und=N(st.textDecorationLine||st.textDecoration||'').includes('underline');const disabled=e.hasAttribute('disabled')||e.getAttribute('aria-disabled')==='true';const excluded=!!e.closest(`form,nav,aside,header,[role='navigation'],[data-testid*='composer']`);const p=e.parentElement;const parentOn=!!(p&&(typeof p.onclick==='function'||p.hasAttribute('onclick')));const parentSingle=!!(p&&p.querySelectorAll&&p.querySelectorAll('a').length===1);if(noHref&&targetBlank&&externalRel&&on&&(ptr||und)&&!disabled&&!excluded&&parentOn&&parentSingle){const token=H([SIG(e),SIG(p),depth(e),targetBlank?1:0,externalRel?1:0,on?1:0,ptr?1:0,und?1:0].join('|'));good.push({el:e,token:token});}}if(good.length!==1)return JSON.stringify(Object.assign({success:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:good.length,ready:false,clicked:false,candidate_token:'-',final_stage:stage},diag));stage='FINAL_STAGE_READY_CHECK';const e=good[0].el,r=e.getBoundingClientRect();const ready=!!(r&&r.width>0&&r.height>0);stage='FINAL_STAGE_COMPLETE';return JSON.stringify(Object.assign({success:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:1,ready:ready,clicked:false,candidate_token:good[0].token,center_x_css:ready?r.left+r.width/2:0,center_y_css:ready?r.top+r.height/2:0,viewport_w_css:window.innerWidth||document.documentElement.clientWidth||0,viewport_h_css:window.innerHeight||document.documentElement.clientHeight||0,final_stage:stage},diag));}catch(e){let en='Error';try{en=(e&&e.name)?String(e.name):'Error';}catch(_){}en=(en.replace(/[^A-Za-z]/g,'').slice(0,32)||'Error');return JSON.stringify({success:false,error_class:'ASSISTANT_LOCAL_RESOURCE_FINAL_EXCEPTION',failure_stage:stage,final_stage:stage,exception_name_class:en,exception_family_hash:SH(en),same_assistant_turn:false,assistant_match_count:0,semantic_candidate_count:0,ready:false,clicked:false,candidate_token:'-',diagnostic_only:true});}})()";
    }

'''
s=s[:m.start()]+final_method+s[m.end():]

# Propagate final-eval failure explicitly instead of collapsing it into turn-changed.
dpat=r'    private void driveResourceV82\([^\n]*\)\{.*?\n    \}\n\n'
dm=re.search(dpat,s,re.S)
assert dm,"drive method not found"
drive=dm.group(0)
needle='int n=o.optInt("semantic_candidate_count",0),assistantMatches=o.optInt("assistant_match_count",0);boolean sameAssistant=o.optBoolean("same_assistant_turn",false),ready=o.optBoolean("ready",false);'
assert drive.count(needle)==1,drive.count(needle)
drive=drive.replace(needle,needle+'boolean finalEvalSuccess=o.optBoolean("success",false);String finalErrorClass=o.optString("error_class","-"),finalFailureStage=o.optString("failure_stage","-"),finalStage=o.optString("final_stage","-"),finalExceptionNameClass=o.optString("exception_name_class","-"),finalExceptionFamilyHash=o.optString("exception_family_hash","-");',1)
marker='put(st,"raw_html_remote",false);'
idx=drive.find(marker)
assert idx>=0
insert=marker+'put(st,"final_eval_success",finalEvalSuccess);put(st,"final_error_class",finalErrorClass);put(st,"final_failure_stage",finalFailureStage);put(st,"final_stage",finalStage);put(st,"final_exception_name_class",finalExceptionNameClass);put(st,"final_exception_family_hash",finalExceptionFamilyHash);'
drive=drive[:idx]+insert+drive[idx+len(marker):]
old_if='if(!sameAssistant){resourceV82Finalized=true;String cls=assistantMatches>1?"RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_IDENTITY_AMBIGUOUS_PRE_EFFECT":"RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_CHANGED_PRE_EFFECT";'
assert drive.count(old_if)==1,drive.count(old_if)
new_if='if(!finalEvalSuccess){resourceV82Finalized=true;emit("RESOURCE_ACTION","RESOURCE_ACTION_ABORTED_FINAL_RECERTIFICATION_EXCEPTION_DIAGNOSTIC",st);status.setText("Final re-certification diagnostic captured exception stage; no action dispatched.");clearResourceV82TerminalState();return;}'+old_if
drive=drive.replace(old_if,new_if,1)
s=s[:dm.start()]+drive+s[dm.end():]

# Zero-effect guard stays before any inherited effect branch after V85->V86 rename.
assert 'if(resourceV86DiagnosticOnly())' in s
assert s.index('if(resourceV86DiagnosticOnly())') < s.index('if(js){boolean clicked=')

ACT.write_text(s)
OLD.unlink()

# Rename telemetry config class/file.
oldcfg=PKG/"TelemetryConfigV85.java"
newcfg=PKG/"TelemetryConfigV86.java"
cfg=oldcfg.read_text().replace("TelemetryConfigV85","TelemetryConfigV86")
newcfg.write_text(cfg)
oldcfg.unlink()

# Manifest/build identity advance only.
man=ROOT/"app/src/main/AndroidManifest.xml"
ms=man.read_text().replace("OrchestratorResourceToolsV85Activity","OrchestratorResourceToolsV86Activity")
man.write_text(ms)
grad=ROOT/"app/build.gradle"
gs=grad.read_text()
gs=gs.replace('versionCode 86','versionCode 87')
gs=gs.replace("versionName '0.83-stable-diag-resource-fingerprint-drift-probe'","versionName '0.84-stable-diag-resource-final-stage-probe'")
grad.write_text(gs)

# Generator-time invariants.
out=ACT.read_text()
required=[
    'SCHEMA="cp-v86-resource-final-stage-probe-v1"','SCENARIO="resource-final-recert-stage-probe"','TelemetryConfigV86',
    'FINAL_STAGE_TURN_QUERY','FINAL_STAGE_TURN_MAP','FINAL_STAGE_FINGERPRINT_BUILD','FINAL_STAGE_MATCH_SCAN','FINAL_STAGE_DIAG_BUILD','FINAL_STAGE_RESOURCE_SCAN','FINAL_STAGE_READY_CHECK','FINAL_STAGE_COMPLETE',
    'ASSISTANT_LOCAL_RESOURCE_FINAL_EXCEPTION','failure_stage','exception_name_class','exception_family_hash','final_eval_success','final_error_class','final_failure_stage','final_stage',
    'RESOURCE_ACTION_ABORTED_FINAL_RECERTIFICATION_EXCEPTION_DIAGNOSTIC','resourceV86DiagnosticOnly()','V64_NORMALIZED_FNV_CONTEXT','PASS_ASSISTANT_LOCAL_RESOURCE_UNIQUE_ADMITTED','CLAIMED_BEFORE_RESOURCE_ACTION'
]
for x in required: assert x in out,x
fm=re.search(r'    private String assistantLocalResourceFinalV82Js\([^\n]*\)\{.*?\n    \}\n\n',out,re.S);assert fm
assert '.click();' not in fm.group(0)
assert 'e.message' not in fm.group(0) and 'stack' not in fm.group(0)
for bad in ['elementFromPoint','document.evaluate','XPathResult','getCookie(','CookieManager','addJavascriptInterface','Thread.sleep','ScheduledExecutorService','TimerTask']:
    assert bad not in out,bad
assert 'versionCode 87' in grad.read_text()
assert "versionName '0.84-stable-diag-resource-final-stage-probe'" in grad.read_text()
assert 'OrchestratorResourceToolsV86Activity' in man.read_text()
print('PASS v0.84 generator: zero-effect final re-certification stage diagnostics with explicit sanitized exception telemetry')
