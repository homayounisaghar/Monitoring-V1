#!/usr/bin/env python3
from pathlib import Path
import runpy,re,json

# v0.87: post-effect Resource repair.
# Preserve v0.86 WebMessagePort-certified original Resource effect and exactly-once/no-replay
# invariants. Repair only post-effect classification and the external-link interstitial path.
runpy.run_path("ci/generate_chatgpt_webview_v88_resource_webmessage_bridge_acceptance_fix1.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorResourceToolsV88Activity.java"
ACT=PKG/"OrchestratorResourceToolsV89Activity.java"
s=OLD.read_text()

# Public identity only. Keep the proven V88 bridge protocol/method names intact so the
# original Resource transaction remains byte-semantically the same except for the repair below.
s=s.replace("OrchestratorResourceToolsV88Activity","OrchestratorResourceToolsV89Activity")
s=s.replace("TelemetryConfigV88","TelemetryConfigV89")
s=s.replace('SCHEMA="cp-v88-resource-webmessage-bridge-acceptance-v1"','SCHEMA="cp-v89-resource-posteffect-repair-v1"')
s=s.replace('SCENARIO="resource-webmessage-bridge-certified-acceptance"','SCENARIO="resource-posteffect-provenance-continuation"')
s=s.replace('testId="cp86-"+UUID.randomUUID();','testId="cp87-"+UUID.randomUUID();')
s=s.replace('v0.86 WebMessagePort-certified Resource acceptance ready.','v0.87 Resource post-effect repair ready.')
s=s.replace('resource_v88_','resource_v89_').replace('resource-v88-','resource-v89-')

# Reset v0.87 continuation state at each transaction boundary.
reset='        resourceV89ContinuationCertInFlight=false;resourceV89ContinuationEffectAttempted=false;resourceV89ContinuationCandidateToken="-";resourceV89ContinuationClaimId="-";\n'
for opening in ['    private void runResourceActionV82(){\n','    private void clearResourceV82TerminalState(){\n']:
    assert s.count(opening)==1,(opening,s.count(opening))
    s=s.replace(opening,opening+reset,1)

TOOLS_GUARD_JS=r'''(function(){try{const N=s=>(s||'').toString().replace(/\s+/g,' ').trim().toLowerCase();const H=s=>{let h=2166136261>>>0;const q=(s||'').toString();for(let i=0;i<q.length;i++){h^=q.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const st=getComputedStyle(e);return st.display!=='none'&&st.visibility!=='hidden'&&st.opacity!=='0';};const L=e=>N([(e.innerText||e.textContent||''),(e.getAttribute('aria-label')||''),(e.getAttribute('title')||''),(e.getAttribute('data-testid')||''),(e.getAttribute('name')||'')].join(' '));const S=e=>H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|')));const triggers=[];for(const e of Array.from(document.querySelectorAll('button,[role=button]')).filter(V)){const l=L(e);if(!/(^|\s)(add|tools|tool)(\s|$)|composer[^ ]*(add|tool)|(add|tool)[^ ]*composer/.test(l))continue;if(N(e.getAttribute('aria-expanded')||'')!=='true')continue;const refs=N([(e.getAttribute('aria-controls')||''),(e.getAttribute('aria-owns')||'')].join(' ')).split(/\s+/).filter(Boolean);const owned=[];for(const id of refs){const x=document.getElementById(id);if(x&&V(x)&&/^(menu|listbox|dialog)$/.test(N(x.getAttribute('role')||'')))owned.push(x);}if(owned.length===1)triggers.push({e:e,surface:owned[0]});}const unique=triggers.length===1;return JSON.stringify({success:true,trigger_certified:unique,trigger_expanded:unique,surface_owned:unique,trigger_count:triggers.length,menu_surface_count:unique?1:0,option_count:unique?triggers[0].surface.querySelectorAll('[role=menuitem],[role=option],button').length:0,trigger_sig:unique?S(triggers[0].e):'-',surface_sig:unique?S(triggers[0].surface):'-'});}catch(_){return JSON.stringify({success:false,trigger_certified:false,trigger_expanded:false,surface_owned:false,trigger_count:0,menu_surface_count:0,option_count:0,trigger_sig:'-',surface_sig:'-'});}})()'''

CONT_CERT_JS=r'''(function(){try{const N=s=>(s||'').toString().replace(/\s+/g,' ').trim().toLowerCase();const H=s=>{let h=2166136261>>>0;const q=(s||'').toString();for(let i=0;i<q.length;i++){h^=q.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const st=getComputedStyle(e);return st.display!=='none'&&st.visibility!=='hidden'&&st.opacity!=='0';};const L=e=>N([(e.innerText||e.textContent||''),(e.getAttribute('aria-label')||''),(e.getAttribute('title')||''),(e.getAttribute('data-testid')||'')].join(' '));const S=e=>H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|')));const dialogs=Array.from(document.querySelectorAll('[role=dialog],[role=alertdialog],[aria-modal=true]')).filter(V);const good=[];for(const d of dialogs){for(const e of Array.from(d.querySelectorAll('button,[role=button],a,[role=link]')).filter(V)){const l=L(e);if(/^(open link|open external link|open in browser|continue to link|visit site)$/.test(l)||/\bopen link\b/.test(l))good.push({d:d,e:e,token:H([S(d),S(e),'OPEN_LINK'].join('|'))});}}const unique=dialogs.length===1&&good.length===1;return JSON.stringify({success:true,dialog_count:dialogs.length,continuation_candidate_count:good.length,semantic_class:unique?'OPEN_LINK':'NONE',candidate_token:unique?good[0].token:'-',ready:unique});}catch(_){return JSON.stringify({success:false,dialog_count:0,continuation_candidate_count:0,semantic_class:'NONE',candidate_token:'-',ready:false});}})()'''

CONT_EFFECT_JS=r'''(function(){try{const want=__CP_CONT_TOKEN_JSON__;const N=s=>(s||'').toString().replace(/\s+/g,' ').trim().toLowerCase();const H=s=>{let h=2166136261>>>0;const q=(s||'').toString();for(let i=0;i<q.length;i++){h^=q.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const st=getComputedStyle(e);return st.display!=='none'&&st.visibility!=='hidden'&&st.opacity!=='0';};const L=e=>N([(e.innerText||e.textContent||''),(e.getAttribute('aria-label')||''),(e.getAttribute('title')||''),(e.getAttribute('data-testid')||'')].join(' '));const S=e=>H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|')));const dialogs=Array.from(document.querySelectorAll('[role=dialog],[role=alertdialog],[aria-modal=true]')).filter(V);const good=[];for(const d of dialogs){for(const e of Array.from(d.querySelectorAll('button,[role=button],a,[role=link]')).filter(V)){const l=L(e);if(/^(open link|open external link|open in browser|continue to link|visit site)$/.test(l)||/\bopen link\b/.test(l)){const token=H([S(d),S(e),'OPEN_LINK'].join('|'));good.push({e:e,token:token});}}}if(dialogs.length!==1||good.length!==1||good[0].token!==want)return JSON.stringify({success:true,clicked:false,reason:'TARGET_CHANGED',dialog_count:dialogs.length,continuation_candidate_count:good.length,candidate_token:good.length===1?good[0].token:'-'});good[0].e.click();return JSON.stringify({success:true,clicked:true,reason:'DISPATCHED',dialog_count:1,continuation_candidate_count:1,candidate_token:good[0].token});}catch(_){return JSON.stringify({success:false,clicked:false,reason:'SCRIPT_EXCEPTION',dialog_count:0,continuation_candidate_count:0,candidate_token:'-'});}})()'''
assert CONT_EFFECT_JS.count('.click();')==1

insert=s.index('    private void driveResourcePendingOnEventV79(')
helpers='''    private boolean resourceV89ContinuationCertInFlight=false;\n    private boolean resourceV89ContinuationEffectAttempted=false;\n    private String resourceV89ContinuationCandidateToken="-",resourceV89ContinuationClaimId="-";\n    private static final String RESOURCE_TOOLS_MISDISPATCH_GUARD_V89_JS='''+json.dumps(TOOLS_GUARD_JS,ensure_ascii=True)+''';\n    private static final String RESOURCE_CONTINUATION_CERT_V89_JS='''+json.dumps(CONT_CERT_JS,ensure_ascii=True)+''';\n    private static final String RESOURCE_CONTINUATION_EFFECT_V89_TEMPLATE='''+json.dumps(CONT_EFFECT_JS,ensure_ascii=True)+''';\n\n    private String resourceToolsMisdispatchGuardV89Js(){return RESOURCE_TOOLS_MISDISPATCH_GUARD_V89_JS;}\n    private String resourceContinuationCertV89Js(){return RESOURCE_CONTINUATION_CERT_V89_JS;}\n    private String resourceContinuationEffectV89Js(String token){if(!hex8V88(token))return "";return RESOURCE_CONTINUATION_EFFECT_V89_TEMPLATE.replace("__CP_CONT_TOKEN_JSON__",jsonV88(token));}\n\n    private void maybeContinueResourceInterstitialV89(String reason){\n        if(resourceV82Finalized||!resourceNavigationPending||!resourceV82EffectDispatched||resourceV89ContinuationEffectAttempted||resourceV89ContinuationCertInFlight)return;\n        if(resourceV82ClaimDocumentEpoch!=documentEpoch)return;\n        resourceV89ContinuationCertInFlight=true;\n        eval(resourceContinuationCertV89Js(),o->{\n            resourceV89ContinuationCertInFlight=false;\n            if(resourceV82Finalized||!resourceNavigationPending||!resourceV82EffectDispatched||resourceV89ContinuationEffectAttempted)return;\n            String token=o.optString("candidate_token","-");boolean certified=o.optBoolean("success",false)&&o.optBoolean("ready",false)&&o.optInt("dialog_count",0)==1&&o.optInt("continuation_candidate_count",0)==1&&"OPEN_LINK".equals(o.optString("semantic_class",""))&&hex8V88(token);\n            JSONObject seen=baseState();put(seen,"continuation_certified",certified);put(seen,"dialog_count",o.optInt("dialog_count",0));put(seen,"continuation_candidate_count",o.optInt("continuation_candidate_count",0));put(seen,"semantic_class",o.optString("semantic_class","NONE"));put(seen,"event_reason_hash",hashNorm(reason));put(seen,"raw_text_remote",false);put(seen,"raw_url_remote",false);\n            emit("RESOURCE_ACTION",certified?"RESOURCE_INTERSTITIAL_OPEN_LINK_CERTIFIED":"RESOURCE_POST_EFFECT_INTERMEDIATE_STATE_NO_CERTIFIED_CONTINUATION",seen);\n            if(!certified)return;\n            String subId="resource-v89-cont-"+UUID.randomUUID();boolean claimed=prefs.edit().putString("resource_v89_continuation_claim_status","CLAIMED").putString("resource_v89_continuation_claim_id",subId).putString("resource_v89_continuation_candidate_token",token).commit();\n            JSONObject claim=baseState();put(claim,"continuation_subclaim",true);put(claim,"claim_committed",claimed);put(claim,"semantic_class","OPEN_LINK");put(claim,"raw_text_remote",false);put(claim,"raw_url_remote",false);emit("DURABLE_CLAIM",claimed?"RESOURCE_CONTINUATION_SUBCLAIM_COMMITTED":"RESOURCE_CONTINUATION_SUBCLAIM_COMMIT_FAILED",claim);\n            if(!claimed){terminalResourceV82("CONTINUATION_SUBCLAIM_COMMIT_FAILED_NO_REPLAY","RESOURCE_ACTION_UNCERTAIN_CONTINUATION_SUBCLAIM_COMMIT_FAILED_NO_REPLAY","Open-link continuation was certified but its durable sub-claim failed; original Resource is not replayed.",true);return;}\n            resourceV89ContinuationClaimId=subId;resourceV89ContinuationCandidateToken=token;boolean armed=prefs.edit().putString("resource_v89_continuation_claim_status","EFFECT_ATTEMPTED_NO_REPLAY").commit();\n            if(!armed){terminalResourceV82("CONTINUATION_ATTEMPT_MARKER_FAILED_NO_REPLAY","RESOURCE_ACTION_UNCERTAIN_CONTINUATION_ATTEMPT_MARKER_FAILED_NO_REPLAY","Continuation attempt marker failed before dispatch; original Resource is not replayed.",true);return;}\n            resourceV89ContinuationEffectAttempted=true;String js=resourceContinuationEffectV89Js(token);if(js.isEmpty()){terminalResourceV82("CONTINUATION_SCRIPT_INVALID_NO_REPLAY","RESOURCE_ACTION_UNCERTAIN_CONTINUATION_SCRIPT_INVALID_NO_REPLAY","Continuation script could not be prepared; no replay.",true);return;}\n            eval(js,r->{\n                if(resourceV82Finalized||!resourceNavigationPending)return;boolean clicked=r.optBoolean("success",false)&&r.optBoolean("clicked",false)&&token.equals(r.optString("candidate_token",""))&&r.optInt("dialog_count",0)==1&&r.optInt("continuation_candidate_count",0)==1;JSONObject st=baseState();put(st,"continuation_subclaim",true);put(st,"continuation_effect_attempted",true);put(st,"continuation_clicked",clicked);put(st,"raw_text_remote",false);put(st,"raw_url_remote",false);\n                if(!clicked){emit("RESOURCE_ACTION","RESOURCE_INTERSTITIAL_CONTINUATION_NOT_DISPATCHED_TARGET_CHANGED_NO_REPLAY",st);status.setText("Open-link continuation was not re-certified in the effect task; no replay.");return;}\n                prefs.edit().putString("resource_v89_continuation_claim_status","DISPATCHED_WAITING_INDEPENDENT_RECEIPT").commit();pageUiDispatches++;pageUiWrites++;emit("RESOURCE_ACTION","RESOURCE_INTERSTITIAL_CONTINUATION_DISPATCHED_WAITING_INDEPENDENT_RECEIPT",st);armResourceReceiptDeadlineV88(resourceV82Actuator);status.setText("Open-link continuation dispatched exactly once; waiting for independent destination/download receipt.");\n            });\n        });\n    }\n\n'''
s=s[:insert]+helpers+s[insert:]

# Replace the old broad post-effect menu census. A generic menu/option/dialog is never
# terminal authority. Tools misdispatch requires a fresh expanded Add/Tools trigger and
# a visible surface owned by that same trigger through aria-controls/aria-owns.
pat=r'    private void driveResourcePendingOnEventV79\([^\n]*\)\{.*?\n    \}\n\n'
m=re.search(pat,s,re.S);assert m,'driveResourcePendingOnEventV79 not found'
replacement=r'''    private void driveResourcePendingOnEventV79(String reason){
        if(!resourceNavigationPending||resourceV82Finalized||"-".equals(resourceActionPendingId))return;
        eval(resourceToolsMisdispatchGuardV89Js(),o->{
            if(!resourceNavigationPending||resourceV82Finalized||"-".equals(resourceActionPendingId))return;
            boolean proven=o.optBoolean("success",false)&&o.optBoolean("trigger_certified",false)&&o.optBoolean("trigger_expanded",false)&&o.optBoolean("surface_owned",false)&&o.optInt("trigger_count",0)==1&&o.optInt("menu_surface_count",0)==1;
            JSONObject st=baseState();put(st,"tools_misdispatch_proven",proven);put(st,"trigger_certified",o.optBoolean("trigger_certified",false));put(st,"trigger_expanded",o.optBoolean("trigger_expanded",false));put(st,"surface_owned",o.optBoolean("surface_owned",false));put(st,"trigger_count",o.optInt("trigger_count",0));put(st,"menu_surface_count",o.optInt("menu_surface_count",0));put(st,"option_count",o.optInt("option_count",0));put(st,"event_reason_hash",hashNorm(reason));put(st,"raw_text_remote",false);put(st,"raw_url_remote",false);
            emit("RESOURCE_ACTION",proven?"RESOURCE_POST_EFFECT_PROVEN_TOOLS_MISDISPATCH":"RESOURCE_POST_EFFECT_GENERIC_UI_NOT_TOOLS_AUTHORITY",st);
            if(proven){terminalResourceV82("MISDISPATCHED_NONRESOURCE_UI_NO_REPLAY","RESOURCE_ACTION_MISDISPATCHED_NONRESOURCE_UI","Resource effect provably expanded its own Add/Tools surface; no replay authorized.",true);return;}
            maybeContinueResourceInterstitialV89(reason);
        });
    }

'''
s=s[:m.start()]+replacement+s[m.end():]

# Emit new file/config identity.
ACT.write_text(s);OLD.unlink()
oldcfg=PKG/"TelemetryConfigV88.java";newcfg=PKG/"TelemetryConfigV89.java";assert oldcfg.exists();newcfg.write_text(oldcfg.read_text().replace("TelemetryConfigV88","TelemetryConfigV89"));oldcfg.unlink()

grad=ROOT/"app/build.gradle";gs=grad.read_text();gs=re.sub(r"versionCode\s+89\b","versionCode 90",gs);gs=gs.replace("0.86-stable-diag-resource-webmessage-bridge-acceptance","0.87-stable-diag-resource-posteffect-repair");grad.write_text(gs)
man=ROOT/"app/src/main/AndroidManifest.xml";ms=man.read_text().replace("OrchestratorResourceToolsV88Activity","OrchestratorResourceToolsV89Activity");man.write_text(ms)

# Generator-time invariants.
out=ACT.read_text()
required=[
    'SCHEMA="cp-v89-resource-posteffect-repair-v1"','SCENARIO="resource-posteffect-provenance-continuation"','TelemetryConfigV89',
    'CP_RESOURCE_CERT_V88','CP_RESOURCE_EFFECT_V88','createWebMessageChannel','window.__cpEventPort',
    'RESOURCE_TOOLS_MISDISPATCH_GUARD_V89_JS','trigger_certified','trigger_expanded','surface_owned','RESOURCE_POST_EFFECT_GENERIC_UI_NOT_TOOLS_AUTHORITY',
    'RESOURCE_CONTINUATION_CERT_V89_JS','RESOURCE_CONTINUATION_EFFECT_V89_TEMPLATE','RESOURCE_CONTINUATION_SUBCLAIM_COMMITTED','EFFECT_ATTEMPTED_NO_REPLAY',
    'RESOURCE_INTERSTITIAL_CONTINUATION_DISPATCHED_WAITING_INDEPENDENT_RECEIPT','android.content.Intent.ACTION_VIEW','PASS_RESOURCE_DOWNLOAD_CALLBACK_RECEIPT',
    'RESOURCE_ACTION_MISDISPATCHED_NONRESOURCE_UI','armResourceReceiptDeadlineV88(resourceV82Actuator)','raw_text_remote",false','raw_url_remote",false'
]
for x in required: assert x in out,x
mm=re.search(pat,out,re.S);assert mm
assert 'toolsMenuCensusV79Js()' not in mm.group(0)
assert 'resourceToolsMisdispatchGuardV89Js()' in mm.group(0)
assert 'trigger_certified' in mm.group(0) and 'trigger_expanded' in mm.group(0) and 'surface_owned' in mm.group(0)
assert CONT_EFFECT_JS.count('.click();')==1
assert out.count('resourceV89ContinuationEffectAttempted=true;')==1,out.count('resourceV89ContinuationEffectAttempted=true;')
for bad in ['elementFromPoint','document.evaluate','XPathResult','getCookie(','CookieManager','addJavascriptInterface','Thread.sleep','ScheduledExecutorService','TimerTask']:
    assert bad not in out,bad
assert out.count('dispatchTouchEvent(')==2,out.count('dispatchTouchEvent(')
assert 'versionCode 90' in grad.read_text()
assert "versionName '0.87-stable-diag-resource-posteffect-repair'" in grad.read_text()
assert 'OrchestratorResourceToolsV89Activity' in man.read_text()
assert 'ControlPlaneAccessibilityServiceV51' in man.read_text()
print('PASS v0.87 generator: provenance-safe Tools guard + exactly-once Open-link continuation subclaim + independent receipt-only success')
