#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.82: remount-stable semantic Assistant-turn identity repair only.
# Reuse the proven conversation-runtime normalization/hash primitive:
# N = whitespace collapse + trim + lowercase; H = FNV-1a 32-bit.
# Resource semantics, calibrated actuator order, exactly-once/no-replay behavior,
# geometry policy, complete lifecycle telemetry, and receipt deadlines stay intact.
runpy.run_path("ci/generate_chatgpt_webview_v83_resource_observable_terminal.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorResourceToolsV83Activity.java"
ACT=PKG/"OrchestratorResourceToolsV84Activity.java"
s=OLD.read_text()

def method(name,body,rettype="void"):
    global s
    pat=rf'    private {re.escape(rettype)} {re.escape(name)}\([^\n]*\)\{{.*?\n    \}}\n\n'
    m=re.search(pat,s,re.S)
    assert m,(rettype,name,"method not found")
    s=s[:m.start()]+body+s[m.end():]

def replace_once(old,new,label):
    global s
    n=s.count(old)
    assert n==1,(label,n)
    s=s.replace(old,new,1)

# Version/class identity. Internal V82 actuator/accessibility method names are
# intentionally preserved; V83 observability helpers become V84.
s=s.replace("OrchestratorResourceToolsV83Activity","OrchestratorResourceToolsV84Activity")
s=s.replace("TelemetryConfigV83","TelemetryConfigV84")
s=s.replace("isResourceLifecycleV83","isResourceLifecycleV84")
s=s.replace("isResourceTerminalV83","isResourceTerminalV84")
s=s.replace("armResourceReceiptDeadlineV83","armResourceReceiptDeadlineV84")
s=s.replace('SCHEMA="cp-v83-resource-observable-terminal-v1"','SCHEMA="cp-v84-resource-semantic-turn-identity-v1"')
s=s.replace('SCENARIO="resource-observable-terminal-calibrated-actuator"','SCENARIO="resource-semantic-turn-identity-calibrated-actuator"')
s=s.replace('getSharedPreferences("cp_v83_resource_observable_terminal",MODE_PRIVATE)','getSharedPreferences("cp_v84_resource_semantic_turn_identity",MODE_PRIVATE)')
s=s.replace('testId="cp81-"+UUID.randomUUID();','testId="cp82-"+UUID.randomUUID();')
s=s.replace('"resource_v83_','"resource_v84_')
s=s.replace('"resource-v83-','"resource-v84-')
s=s.replace('v0.81 Observable terminal Resource acceptance ready.','v0.82 Semantic turn identity Resource acceptance ready.')

# Durable claim authority is now a semantic fingerprint, not DOM turn identity.
s=s.replace('resourceV82ClaimAssistantToken','resourceV84ClaimTurnFingerprint')

# Explicit terminal classification for a non-unique semantic turn fingerprint.
replace_once(
    '            "RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_CHANGED_PRE_EFFECT",\n',
    '            "RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_CHANGED_PRE_EFFECT",\n            "RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_IDENTITY_AMBIGUOUS_PRE_EFFECT",\n',
    'semantic identity ambiguous terminal')

# Admission/claim: store the same semantic fingerprint returned by the resolver.
method('beginResourceAcceptanceV82',r'''    private void beginResourceAcceptanceV82(){
        if(resourceV82Finalized||"NONE".equals(resourceV82Actuator))return;resourceScanDocumentEpoch=documentEpoch;resourceScanPageFinishedEpoch=pageFinishedEpoch;
        eval(assistantLocalResourceCertifyV82Js(),o->{
            JSONObject admission=baseState();put(admission,"semantic_candidate_count",o.optInt("semantic_candidate_count",0));put(admission,"assistant_turn_count",o.optInt("assistant_turn_count",0));put(admission,"last_assistant_exists",o.optBoolean("last_assistant_exists",false));put(admission,"author_message_exists",o.optBoolean("author_message_exists",false));put(admission,"exact_unique",o.optBoolean("exact_unique",false));put(admission,"assistant_identity_unique",o.optBoolean("assistant_identity_unique",false));put(admission,"assistant_identity_match_count",o.optInt("assistant_identity_match_count",0));put(admission,"assistant_identity_mode","V64_NORMALIZED_FNV_CONTEXT");put(admission,"assistant_content_hash",o.optString("assistant_content_hash","-"));put(admission,"preceding_user_hash",o.optString("preceding_user_hash","-"));put(admission,"actuator",resourceV82Actuator);put(admission,"raw_url_remote",false);put(admission,"raw_text_remote",false);put(admission,"raw_html_remote",false);
            boolean epochFresh=resourceScanDocumentEpoch==documentEpoch&&resourceScanPageFinishedEpoch==pageFinishedEpoch&&pageFinishedEpoch==documentEpoch;String candidate=o.optString("candidate_token","-"),turnFp=o.optString("assistant_fingerprint","-");boolean identityUnique=o.optBoolean("assistant_identity_unique",false);boolean admitted=o.optBoolean("success",false)&&o.optBoolean("exact_unique",false)&&o.optInt("semantic_candidate_count",0)==1&&identityUnique&&!"-".equals(candidate)&&!"-".equals(turnFp)&&epochFresh;
            put(admission,"epoch_fresh",epochFresh);put(admission,"admitted",admitted);emit("RESOURCE_DISCOVERY",admitted?"PASS_ASSISTANT_LOCAL_RESOURCE_UNIQUE_ADMITTED":"RESOURCE_ACTION_BLOCKED_NO_UNIQUE_ASSISTANT_LOCAL_RESOURCE",admission);if(!admitted){status.setText("TEST RESOURCE blocked: no unique strong assistant-local Resource with unique semantic turn identity was admitted.");return;}
            resourceV82AdmissionToken=candidate;resourceV82InitialCandidateToken=candidate;resourceV84ClaimTurnFingerprint=turnFp;resourceV82ClaimDocumentEpoch=documentEpoch;resourceV82ClaimPageFinishedEpoch=pageFinishedEpoch;
            String origin=originOfV82(web==null?null:web.getUrl());if(origin.isEmpty()){emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_UNSUPPORTED_CURRENT_ORIGIN",admission);status.setText("TEST RESOURCE blocked: unsupported page origin.");return;}resourceV82ActionOrigin=origin;
            String claimId="resource-v84-"+UUID.randomUUID();boolean committed=prefs.edit().putString("resource_v84_claim_status","CLAIMED").putString("resource_v84_claim_id",claimId).putString("resource_v84_turn_fingerprint",turnFp).commit();JSONObject pre=baseState();put(pre,"claim_committed",committed);put(pre,"actuator",resourceV82Actuator);put(pre,"assistant_bound",true);put(pre,"assistant_identity_mode","V64_NORMALIZED_FNV_CONTEXT");put(pre,"raw_url_remote",false);emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_RESOURCE_ACTION":"RESOURCE_ACTION_CLAIM_COMMIT_FAILED",pre);if(!committed){status.setText("TEST RESOURCE blocked: durable claim failed.");return;}
            resourceActionPendingId=claimId;resourceV82Finalized=false;resourceV82EffectDispatched=false;resourceV82PreEffectPending=true;resourceNavigationPending=false;resourceDownloadPending=false;resourceWrappedSawSameOriginNavigation=false;installResourceDownloadListenerV82();try{web.getSettings().setJavaScriptCanOpenWindowsAutomatically("JS_POPUP".equals(resourceV82Actuator));}catch(Exception ignored){}
            final long timeout=++resourceV82TimeoutSerial;resourceV82Handler.postDelayed(()->{if(!resourceV82Finalized&&resourceV82PreEffectPending&&!resourceV82EffectDispatched&&timeout==resourceV82TimeoutSerial){resourceV82Finalized=true;prefs.edit().putString("resource_v84_claim_status","PRE_EFFECT_TARGET_TIMEOUT").commit();JSONObject st=baseState();put(st,"actuator",resourceV82Actuator);put(st,"effect_dispatched",false);put(st,"assistant_identity_mode","V64_NORMALIZED_FNV_CONTEXT");put(st,"raw_url_remote",false);emit("RESOURCE_ACTION","RESOURCE_ACTION_PRE_EFFECT_TARGET_TIMEOUT_NO_ACTION",st);status.setText("Resource target did not reappear before fail-closed timeout; no action was dispatched.");clearResourceV82TerminalState();}},6000L);
            driveResourceV82("AFTER_CLAIM");
        });
    }

''')

# Same candidate predicate as v0.81. Only Assistant-turn identity changes.
start=s.index('    private String assistantLocalResourceCertifyV82Js(){\n')
end=s.index('    private String assistantLocalResourceFinalV82Js(',start)
cert=r'''    private String assistantLocalResourceCertifyV82Js(){
        return "(function(){try{"+
            "const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const st=getComputedStyle(e);if(st.display==='none'||st.visibility==='hidden'||st.opacity==='0')return false;try{if(typeof e.checkVisibility==='function')return e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});}catch(_){}return true;};const SIG=e=>e?H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|'))):'-';const TXT=e=>{if(!e)return '';return (e.innerText||e.textContent||'').replace(/\\s+$/,'').trim();};"+
            "const turnNodes=[];const seen=new Set();const addTurn=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);turnNodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(addTurn);const turns=turnNodes.map(e=>{const a=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');const role=a?N(a.getAttribute('data-message-author-role')||'-'):'-';const norm=N(TXT(a));return{el:e,author:a,role:role,content_hash:norm?H(norm):'-',norm_len:norm.length};}).filter(t=>t.role==='user'||t.role==='assistant');const precedingUser=i=>{for(let j=i-1;j>=0;j--)if(turns[j].role==='user')return turns[j];return null;};const FP=i=>{const t=turns[i];if(!t||t.role!=='assistant'||t.content_hash==='-')return '-';const u=precedingUser(i);return H(['assistant',t.content_hash,t.norm_len,u?u.content_hash:'-',u?u.norm_len:0].join('|'));};let li=-1;for(let i=0;i<turns.length;i++)if(turns[i].role==='assistant')li=i;if(li<0)return JSON.stringify({success:true,last_assistant_exists:false,author_message_exists:false,assistant_turn_count:0,semantic_candidate_count:0,exact_unique:false,candidate_token:'-',assistant_fingerprint:'-',assistant_identity_unique:false,assistant_identity_match_count:0});const last=turns[li],author=last.author;if(!author)return JSON.stringify({success:true,last_assistant_exists:true,author_message_exists:false,assistant_turn_count:turns.filter(t=>t.role==='assistant').length,semantic_candidate_count:0,exact_unique:false,candidate_token:'-',assistant_fingerprint:'-',assistant_identity_unique:false,assistant_identity_match_count:0});const assistantFp=FP(li),u=precedingUser(li);let identityMatches=0;for(let i=0;i<turns.length;i++)if(turns[i].role==='assistant'&&FP(i)===assistantFp)identityMatches++;const depth=e=>{let d=0,p=e;while(p&&p!==last.el){d++;p=p.parentElement;}return d;};const good=[];for(const e of Array.from(author.querySelectorAll('a')).filter(V)){const hrefAttr=e.getAttribute('href');const noHref=hrefAttr===null||String(hrefAttr).trim()==='';const targetBlank=N(e.getAttribute('target')||'')==='_blank';const externalRel=/noopener|noreferrer|external/.test(N(e.getAttribute('rel')||''));const on=typeof e.onclick==='function'||e.hasAttribute('onclick');const st=getComputedStyle(e),ptr=N(st.cursor||'').includes('pointer'),und=N(st.textDecorationLine||st.textDecoration||'').includes('underline');const disabled=e.hasAttribute('disabled')||e.getAttribute('aria-disabled')==='true';const excluded=!!e.closest(`form,nav,aside,header,[role='navigation'],[data-testid*='composer']`);const p=e.parentElement;const parentOn=!!(p&&(typeof p.onclick==='function'||p.hasAttribute('onclick')));const parentSingle=!!(p&&p.querySelectorAll&&p.querySelectorAll('a').length===1);if(noHref&&targetBlank&&externalRel&&on&&(ptr||und)&&!disabled&&!excluded&&parentOn&&parentSingle){const token=H([SIG(e),SIG(p),depth(e),targetBlank?1:0,externalRel?1:0,on?1:0,ptr?1:0,und?1:0].join('|'));good.push({token:token});}}const unique=good.length===1,identityUnique=assistantFp!=='-'&&identityMatches===1;return JSON.stringify({success:true,last_assistant_exists:true,author_message_exists:true,assistant_turn_count:turns.filter(t=>t.role==='assistant').length,semantic_candidate_count:good.length,exact_unique:unique,candidate_token:unique?good[0].token:'-',assistant_fingerprint:assistantFp,assistant_identity_unique:identityUnique,assistant_identity_match_count:identityMatches,assistant_content_hash:last.content_hash,preceding_user_hash:u?u.content_hash:'-'});"+
        "}catch(e){return JSON.stringify({success:false,error_class:'ASSISTANT_LOCAL_RESOURCE_CERTIFY_EXCEPTION',semantic_candidate_count:0,exact_unique:false,candidate_token:'-',assistant_fingerprint:'-',assistant_identity_unique:false,assistant_identity_match_count:0});}})()";
    }

'''
s=s[:start]+cert+s[end:]

start=s.index('    private String assistantLocalResourceFinalV82Js(')
end=s.index('    private String assistantLocalResourceClickV82Js(',start)
finaljs=r'''    private String assistantLocalResourceFinalV82Js(String expectedTurnFingerprint,boolean jsActuate){
        return "(function(){try{const expected="+jsV79(expectedTurnFingerprint)+",doClick="+(jsActuate?"true":"false")+";const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const st=getComputedStyle(e);if(st.display==='none'||st.visibility==='hidden'||st.opacity==='0')return false;try{if(typeof e.checkVisibility==='function')return e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});}catch(_){}return true;};const SIG=e=>e?H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|'))):'-';const TXT=e=>{if(!e)return '';return (e.innerText||e.textContent||'').replace(/\\s+$/,'').trim();};const nodes=[];const seen=new Set();const add=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);nodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(add);const turns=nodes.map(e=>{const a=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');const role=a?N(a.getAttribute('data-message-author-role')||'-'):'-';const norm=N(TXT(a));return{el:e,author:a,role:role,content_hash:norm?H(norm):'-',norm_len:norm.length};}).filter(t=>t.role==='user'||t.role==='assistant');const precedingUser=i=>{for(let j=i-1;j>=0;j--)if(turns[j].role==='user')return turns[j];return null;};const FP=i=>{const t=turns[i];if(!t||t.role!=='assistant'||t.content_hash==='-')return '-';const u=precedingUser(i);return H(['assistant',t.content_hash,t.norm_len,u?u.content_hash:'-',u?u.norm_len:0].join('|'));};const matches=[];for(let i=0;i<turns.length;i++)if(turns[i].role==='assistant'&&FP(i)===expected)matches.push(i);if(matches.length!==1)return JSON.stringify({success:true,same_assistant_turn:false,assistant_match_count:matches.length,semantic_candidate_count:0,ready:false,clicked:false,candidate_token:'-'});const target=turns[matches[0]],author=target.author;if(!author)return JSON.stringify({success:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:0,ready:false,clicked:false,candidate_token:'-'});const depth=e=>{let d=0,p=e;while(p&&p!==target.el){d++;p=p.parentElement;}return d;};const good=[];for(const e of Array.from(author.querySelectorAll('a')).filter(V)){const hrefAttr=e.getAttribute('href');const noHref=hrefAttr===null||String(hrefAttr).trim()==='';const targetBlank=N(e.getAttribute('target')||'')==='_blank';const externalRel=/noopener|noreferrer|external/.test(N(e.getAttribute('rel')||''));const on=typeof e.onclick==='function'||e.hasAttribute('onclick');const st=getComputedStyle(e),ptr=N(st.cursor||'').includes('pointer'),und=N(st.textDecorationLine||st.textDecoration||'').includes('underline');const disabled=e.hasAttribute('disabled')||e.getAttribute('aria-disabled')==='true';const excluded=!!e.closest(`form,nav,aside,header,[role='navigation'],[data-testid*='composer']`);const p=e.parentElement;const parentOn=!!(p&&(typeof p.onclick==='function'||p.hasAttribute('onclick')));const parentSingle=!!(p&&p.querySelectorAll&&p.querySelectorAll('a').length===1);if(noHref&&targetBlank&&externalRel&&on&&(ptr||und)&&!disabled&&!excluded&&parentOn&&parentSingle){const token=H([SIG(e),SIG(p),depth(e),targetBlank?1:0,externalRel?1:0,on?1:0,ptr?1:0,und?1:0].join('|'));good.push({el:e,token:token});}}if(good.length!==1)return JSON.stringify({success:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:good.length,ready:false,clicked:false,candidate_token:'-'});const e=good[0].el,r=e.getBoundingClientRect();const ready=!!(r&&r.width>0&&r.height>0);if(!ready)return JSON.stringify({success:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:1,ready:false,clicked:false,candidate_token:good[0].token});if(doClick){e.click();return JSON.stringify({success:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:1,ready:true,clicked:true,candidate_token:good[0].token});}return JSON.stringify({success:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:1,ready:true,clicked:false,candidate_token:good[0].token,center_x_css:r.left+r.width/2,center_y_css:r.top+r.height/2,viewport_w_css:window.innerWidth||document.documentElement.clientWidth||0,viewport_h_css:window.innerHeight||document.documentElement.clientHeight||0});}catch(e){return JSON.stringify({success:false,error_class:'ASSISTANT_LOCAL_RESOURCE_FINAL_EXCEPTION',same_assistant_turn:false,assistant_match_count:0,semantic_candidate_count:0,ready:false,clicked:false,candidate_token:'-'});}})()";
    }

'''
s=s[:start]+finaljs+s[end:]

# Pre-effect drive now interprets unique semantic-fingerprint matches. Resource
# candidate semantics and all actuation/receipt code remain unchanged.
old='int n=o.optInt("semantic_candidate_count",0);boolean sameAssistant=o.optBoolean("same_assistant_turn",false),ready=o.optBoolean("ready",false);JSONObject st=baseState();put(st,"actuator",actuator);put(st,"semantic_candidate_count",n);put(st,"same_assistant_turn",sameAssistant);put(st,"candidate_remounted",!resourceV82InitialCandidateToken.equals(o.optString("candidate_token","-")));put(st,"drive_reason_hash",hashNorm(reason));put(st,"geometry_role",js?"NONE":"ACTUATION_TRANSPORT_ONLY");put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);'
new='int n=o.optInt("semantic_candidate_count",0),assistantMatches=o.optInt("assistant_match_count",0);boolean sameAssistant=o.optBoolean("same_assistant_turn",false),ready=o.optBoolean("ready",false);JSONObject st=baseState();put(st,"actuator",actuator);put(st,"semantic_candidate_count",n);put(st,"same_assistant_turn",sameAssistant);put(st,"assistant_match_count",assistantMatches);put(st,"assistant_identity_mode","V64_NORMALIZED_FNV_CONTEXT");put(st,"candidate_remounted",!resourceV82InitialCandidateToken.equals(o.optString("candidate_token","-")));put(st,"drive_reason_hash",hashNorm(reason));put(st,"geometry_role",js?"NONE":"ACTUATION_TRANSPORT_ONLY");put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);'
replace_once(old,new,'drive semantic identity telemetry')
old='if(!sameAssistant){resourceV82Finalized=true;emit("RESOURCE_ACTION","RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_CHANGED_PRE_EFFECT",st);status.setText("Resource transaction aborted: assistant turn changed before actuation.");clearResourceV82TerminalState();return;}'
new='if(!sameAssistant){resourceV82Finalized=true;String cls=assistantMatches>1?"RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_IDENTITY_AMBIGUOUS_PRE_EFFECT":"RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_CHANGED_PRE_EFFECT";emit("RESOURCE_ACTION",cls,st);status.setText(assistantMatches>1?"Resource transaction aborted: semantic Assistant identity became ambiguous before actuation.":"Resource transaction aborted: semantic Assistant turn changed before actuation.");clearResourceV82TerminalState();return;}'
replace_once(old,new,'drive semantic identity guard')

ACT.write_text(s);OLD.unlink()
old_cfg=PKG/"TelemetryConfigV83.java";new_cfg=PKG/"TelemetryConfigV84.java";assert old_cfg.exists();new_cfg.write_text(old_cfg.read_text().replace("TelemetryConfigV83","TelemetryConfigV84"));old_cfg.unlink()

g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+84\b","versionCode 85",gs);gs=gs.replace("0.81-stable-diag-resource-observable-terminal","0.82-stable-diag-resource-semantic-turn-identity");g.write_text(gs)
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorResourceToolsV83Activity","OrchestratorResourceToolsV84Activity");mf.write_text(ms)

out=ACT.read_text()
required=[
    'SCHEMA="cp-v84-resource-semantic-turn-identity-v1"',
    'SCENARIO="resource-semantic-turn-identity-calibrated-actuator"',
    'V64_NORMALIZED_FNV_CONTEXT','assistant_fingerprint','assistant_identity_unique','assistant_identity_match_count','assistant_match_count',
    'resourceV84ClaimTurnFingerprint','resource_v84_turn_fingerprint',
    "H(['assistant',t.content_hash,t.norm_len,u?u.content_hash:'-',u?u.norm_len:0].join('|'))",
    'RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_IDENTITY_AMBIGUOUS_PRE_EFFECT',
    'RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_CHANGED_PRE_EFFECT',
    'PASS_ASSISTANT_LOCAL_RESOURCE_UNIQUE_ADMITTED','CLAIMED_BEFORE_RESOURCE_ACTION',
    'PASS_ACTUATOR_CALIBRATION_SELECTED','JS_POPUP','ACCESSIBILITY_CLICK','NATIVE_TOUCH',
    'RESOURCE_POST_EFFECT_RECEIPT_DEADLINE_ARMED','RESOURCE_ACTION_UNCERTAIN_EFFECT_DISPATCHED_NO_RECEIPT_NO_REPLAY',
    'ACTUATION_TRANSPORT_ONLY','TelemetryConfigV84'
]
for x in required: assert x in out,x
for bad in ["H('assistant|'+turnKey+'|'+last.index)","getAttribute('data-turn-id')||last.el.getAttribute('data-testid')",'resourceV82ClaimAssistantToken','assistant_token']:
    assert bad not in out,bad
for bad in ['elementFromPoint','document.evaluate','XPathResult','findElementsBy','getCookie(','CookieManager','addJavascriptInterface','Thread.sleep','ScheduledExecutorService','TimerTask']:
    assert bad not in out,bad
assert out.count('armResourceReceiptDeadlineV84(actuator)')==3,out.count('armResourceReceiptDeadlineV84(actuator)')
assert out.count('dispatchTouchEvent(')==4,out.count('dispatchTouchEvent(')
assert 'versionCode 85' in g.read_text()
assert "versionName '0.82-stable-diag-resource-semantic-turn-identity'" in g.read_text()
assert 'OrchestratorResourceToolsV84Activity' in mf.read_text()
assert 'ControlPlaneAccessibilityServiceV51' in mf.read_text() and '@xml/cp_accessibility_service_v51' in mf.read_text()
print('PASS v0.82 semantic-turn-identity audit: v64 normalization/FNV context fingerprint reused, DOM turn-id/index authority removed, exact Resource semantics and v0.81 actuation/receipt invariants preserved')
