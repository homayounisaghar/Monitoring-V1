#!/usr/bin/env python3
from pathlib import Path
import runpy,re,json

# v0.86: consolidated WebMessagePort-certified Resource acceptance.
# Keep v0.85 admission/V64 authority, durable claim, calibrated actuator and receipts,
# but stop trusting evaluateJavascript return values for final Resource certification.
# The already-connected WebMessagePort carries bounded cert/effect receipts. The JS
# actuator re-certifies the exact semantic target and candidate token in the same task
# as its one click. Missing post-effect evidence is uncertain and is never replayed.
runpy.run_path("ci/generate_chatgpt_webview_v87_resource_parse_boundary_probe.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorResourceToolsV87Activity.java"
ACT=PKG/"OrchestratorResourceToolsV88Activity.java"
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

# Identity rollover. Internal V82 actuator/receipt helper names remain stable; the
# diagnostic V87 lineage becomes V88 where it was already version-scoped.
s=s.replace("OrchestratorResourceToolsV87Activity","OrchestratorResourceToolsV88Activity")
s=s.replace("TelemetryConfigV87","TelemetryConfigV88")
s=s.replace("V87","V88").replace("v87","v88")
s=s.replace('SCHEMA="cp-v88-resource-parse-boundary-probe-v1"','SCHEMA="cp-v88-resource-webmessage-bridge-acceptance-v1"')
s=s.replace('SCENARIO="resource-final-eval-parse-boundary-probe"','SCENARIO="resource-webmessage-bridge-certified-acceptance"')
s=s.replace('testId="cp85-"+UUID.randomUUID();','testId="cp86-"+UUID.randomUUID();')
s=s.replace('v0.85 Final evaluation parse-boundary diagnostic ready.','v0.86 WebMessagePort-certified Resource acceptance ready.')
s=s.replace('cp_v88_resource_parse_boundary_probe','cp_v88_resource_webmessage_bridge_acceptance')
assert 'private boolean resourceV88DiagnosticOnly(){return true;}' in s
s=s.replace('private boolean resourceV88DiagnosticOnly(){return true;}','private boolean resourceV88DiagnosticOnly(){return false;}',1)

# Bridge transaction state. Nonces are Android-generated hex only and never contain
# user/page data. A cert may be retried only from a fresh observed DOM event before
# any effect; an effect attempt itself is exactly once.
anchor='    private boolean resourceV88DiagnosticOnly(){return false;}'
assert s.count(anchor)==1
bridge_fields='''
    private String resourceV88TxNonce="-",resourceV88CertNonce="-",resourceV88EffectNonce="-",resourceV88CertCandidateToken="-";
    private boolean resourceV88BridgeCertAccepted=false,resourceV88EffectAttempted=false,resourceV88EffectBridgeResultAccepted=false;
    private long resourceV88CertSerial=0L,resourceV88EffectSerial=0L;
'''
s=s.replace(anchor,anchor+bridge_fields,1)

# Every new focused run and every terminal clear invalidates old bridge messages.
run_open='    private void runResourceActionV82(){\n'
assert s.count(run_open)==1
s=s.replace(run_open,run_open+'        ++resourceV88CertSerial;++resourceV88EffectSerial;resourceV88TxNonce="-";resourceV88CertNonce="-";resourceV88EffectNonce="-";resourceV88CertCandidateToken="-";resourceV88BridgeCertAccepted=false;resourceV88EffectAttempted=false;resourceV88EffectBridgeResultAccepted=false;\n',1)
clear_open='    private void clearResourceV82TerminalState(){\n'
assert s.count(clear_open)==1
s=s.replace(clear_open,clear_open+'        ++resourceV88CertSerial;++resourceV88EffectSerial;resourceV88TxNonce="-";resourceV88CertNonce="-";resourceV88EffectNonce="-";resourceV88CertCandidateToken="-";resourceV88BridgeCertAccepted=false;resourceV88EffectAttempted=false;resourceV88EffectBridgeResultAccepted=false;\n',1)

# All new bridge terminal outcomes are explicit terminal classifications.
tm=re.search(r'    private boolean isResourceTerminalV88\([^\n]*\)\{.*?\n    \}\n',s,re.S)
assert tm,'terminal classifier'
tblock=tm.group(0)
needle='String[] terminal={'
assert tblock.count(needle)==1
new_terms='''String[] terminal={
            "RESOURCE_ACTION_NO_FINAL_CERT_RECEIPT_NO_ACTION",
            "RESOURCE_ACTION_ABORTED_BRIDGE_CERT_INVALID_NO_ACTION",
            "RESOURCE_ACTION_ABORTED_BRIDGE_CERT_SCRIPT_ERROR_NO_ACTION",
            "RESOURCE_ACTION_BLOCKED_BRIDGE_ACCEPTANCE_REQUIRES_JS_ACTUATOR",
            "RESOURCE_ACTION_EFFECT_BLOCKED_TARGET_CHANGED_NO_ACTION",
            "RESOURCE_ACTION_UNCERTAIN_EFFECT_ATTEMPT_NO_BRIDGE_RESULT_NO_REPLAY",
            "RESOURCE_ACTION_UNCERTAIN_EFFECT_BRIDGE_INVALID_NO_REPLAY",
            "RESOURCE_ACTION_UNCERTAIN_EFFECT_SCRIPT_EXCEPTION_NO_REPLAY",'''
tblock=tblock.replace(needle,new_terms,1)
s=s[:tm.start()]+tblock+s[tm.end():]

# Existing event bridge remains the sole page->Android IPC. DOM notifications keep
# their exact old meaning; only bounded JSON Resource protocol messages are routed
# to the new handler. No addJavascriptInterface surface is introduced.
method('installEventBridge',r'''    private void installEventBridge(long epoch){
        if(web==null||epoch!=documentEpoch)return;closeEventBridge();
        eval(eventBootstrapJs(),o->{
            if(epoch!=documentEpoch)return;
            if(!o.optBoolean("success",false)){emit("EVENT_BRIDGE","EVENT_BRIDGE_BOOTSTRAP_FAILED",sanitizedState(o));if(plannerRunning)plannerFail("EVENT_BRIDGE_BOOTSTRAP_FAILED");return;}
            try{
                WebMessagePort[] ports=web.createWebMessageChannel();eventPort=ports[0];final long bridgeEpoch=epoch;
                eventPort.setWebMessageCallback(new WebMessagePort.WebMessageCallback(){
                    @Override public void onMessage(WebMessagePort port,WebMessage message){
                        if(bridgeEpoch!=documentEpoch)return;String data=null;try{data=message==null?null:message.getData();}catch(Exception ignored){}
                        if("DOM".equals(data)){requestEventRead("DOM_EVENT");return;}
                        handleResourceBridgeMessageV88(data,bridgeEpoch);
                    }
                });
                web.postWebMessage(new WebMessage("CP_CONNECT",new WebMessagePort[]{ports[1]}),Uri.parse("https://chatgpt.com"));
                JSONObject st=baseState();put(st,"event_bridge_connected",true);put(st,"document_epoch",documentEpoch);emit("EVENT_BRIDGE","PASS_EVENT_BRIDGE_CHANNEL_CONNECTED",st);
            }catch(Exception e){JSONObject st=baseState();put(st,"event_bridge_connected",false);emit("EVENT_BRIDGE","EVENT_BRIDGE_CHANNEL_FAILED",st);if(plannerRunning)plannerFail("EVENT_BRIDGE_CHANNEL_FAILED");}
        });
    }

''')

# Shared exact JS templates. Both contain only bounded hash/count/enum data in the
# WebMessagePort payload; neither returns semantic authority via evaluateJavascript.
CERT_JS_TEMPLATE=r'''(function(){let stage='CERT_INIT';const post=o=>{try{const p=window.__cpEventPort;if(p)p.postMessage(JSON.stringify(o));}catch(_){}};const base={type:'CP_RESOURCE_CERT_V88',v:1,tx:__CP_TX_JSON__,cert:__CP_CERT_JSON__,epoch:__CP_EPOCH__,expected:__CP_EXPECTED_JSON__};const send=o=>post(Object.assign({},base,o));const H=s=>{let h=2166136261>>>0;const q=(s||'').toString();for(let i=0;i<q.length;i++){h^=q.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};try{const expected=base.expected;const N=s=>(s||'').toString().replace(/\s+/g,' ').trim().toLowerCase();const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const st=getComputedStyle(e);if(st.display==='none'||st.visibility==='hidden'||st.opacity==='0')return false;try{if(typeof e.checkVisibility==='function')return e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});}catch(_){}return true;};const SIG=e=>e?H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|'))):'-';const TXT=e=>{if(!e)return '';return (e.innerText||e.textContent||'').replace(/\s+$/,'').trim();};stage='CERT_TURNS';const nodes=[];const seen=new Set();const add=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);nodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(add);const turns=nodes.map(e=>{const a=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');const role=a?N(a.getAttribute('data-message-author-role')||'-'):'-';const norm=N(TXT(a));return{el:e,author:a,role:role,content_hash:norm?H(norm):'-',norm_len:norm.length};}).filter(t=>t.role==='user'||t.role==='assistant');const precedingUser=i=>{for(let j=i-1;j>=0;j--)if(turns[j].role==='user')return turns[j];return null;};const FP=i=>{const t=turns[i];if(!t||t.role!=='assistant'||t.content_hash==='-')return '-';const u=precedingUser(i);return H(['assistant',t.content_hash,t.norm_len,u?u.content_hash:'-',u?u.norm_len:0].join('|'));};stage='CERT_MATCH';const matches=[];for(let i=0;i<turns.length;i++)if(turns[i].role==='assistant'&&FP(i)===expected)matches.push(i);if(matches.length!==1){send({ok:true,same_assistant_turn:false,assistant_match_count:matches.length,semantic_candidate_count:0,candidate_token:'-',ready:false,stage:stage});return;}const target=turns[matches[0]],author=target.author;if(!author){send({ok:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:0,candidate_token:'-',ready:false,stage:'CERT_NO_AUTHOR'});return;}stage='CERT_RESOURCE';const depth=e=>{let d=0,p=e;while(p&&p!==target.el){d++;p=p.parentElement;}return d;};const good=[];for(const e of Array.from(author.querySelectorAll('a')).filter(V)){const hrefAttr=e.getAttribute('href');const noHref=hrefAttr===null||String(hrefAttr).trim()==='';const targetBlank=N(e.getAttribute('target')||'')==='_blank';const externalRel=/noopener|noreferrer|external/.test(N(e.getAttribute('rel')||''));const on=typeof e.onclick==='function'||e.hasAttribute('onclick');const st=getComputedStyle(e),ptr=N(st.cursor||'').includes('pointer'),und=N(st.textDecorationLine||st.textDecoration||'').includes('underline');const disabled=e.hasAttribute('disabled')||e.getAttribute('aria-disabled')==='true';const excluded=!!e.closest(`form,nav,aside,header,[role='navigation'],[data-testid*='composer']`);const p=e.parentElement;const parentOn=!!(p&&(typeof p.onclick==='function'||p.hasAttribute('onclick')));const parentSingle=!!(p&&p.querySelectorAll&&p.querySelectorAll('a').length===1);if(noHref&&targetBlank&&externalRel&&on&&(ptr||und)&&!disabled&&!excluded&&parentOn&&parentSingle){const token=H([SIG(e),SIG(p),depth(e),targetBlank?1:0,externalRel?1:0,on?1:0,ptr?1:0,und?1:0].join('|'));good.push({el:e,token:token});}}if(good.length!==1){send({ok:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:good.length,candidate_token:'-',ready:false,stage:stage});return;}const e=good[0].el,r=e.getBoundingClientRect();const ready=!!(r&&r.width>0&&r.height>0);send({ok:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:1,candidate_token:good[0].token,ready:ready,stage:ready?'CERT_READY':'CERT_NOT_READY'});}catch(_){send({ok:false,same_assistant_turn:false,assistant_match_count:0,semantic_candidate_count:0,candidate_token:'-',ready:false,stage:stage});}})()'''

EFFECT_JS_TEMPLATE=r'''(function(){let stage='EFFECT_INIT';const post=o=>{try{const p=window.__cpEventPort;if(p)p.postMessage(JSON.stringify(o));}catch(_){}};const base={type:'CP_RESOURCE_EFFECT_V88',v:1,tx:__CP_TX_JSON__,effect:__CP_EFFECT_JSON__,epoch:__CP_EPOCH__,expected:__CP_EXPECTED_JSON__,cert_candidate:__CP_CANDIDATE_JSON__};const send=o=>post(Object.assign({},base,o));const H=s=>{let h=2166136261>>>0;const q=(s||'').toString();for(let i=0;i<q.length;i++){h^=q.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};try{const expected=base.expected,want=base.cert_candidate;const N=s=>(s||'').toString().replace(/\s+/g,' ').trim().toLowerCase();const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const st=getComputedStyle(e);if(st.display==='none'||st.visibility==='hidden'||st.opacity==='0')return false;try{if(typeof e.checkVisibility==='function')return e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});}catch(_){}return true;};const SIG=e=>e?H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|'))):'-';const TXT=e=>{if(!e)return '';return (e.innerText||e.textContent||'').replace(/\s+$/,'').trim();};stage='EFFECT_TURNS';const nodes=[];const seen=new Set();const add=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);nodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(add);const turns=nodes.map(e=>{const a=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');const role=a?N(a.getAttribute('data-message-author-role')||'-'):'-';const norm=N(TXT(a));return{el:e,author:a,role:role,content_hash:norm?H(norm):'-',norm_len:norm.length};}).filter(t=>t.role==='user'||t.role==='assistant');const precedingUser=i=>{for(let j=i-1;j>=0;j--)if(turns[j].role==='user')return turns[j];return null;};const FP=i=>{const t=turns[i];if(!t||t.role!=='assistant'||t.content_hash==='-')return '-';const u=precedingUser(i);return H(['assistant',t.content_hash,t.norm_len,u?u.content_hash:'-',u?u.norm_len:0].join('|'));};stage='EFFECT_MATCH';const matches=[];for(let i=0;i<turns.length;i++)if(turns[i].role==='assistant'&&FP(i)===expected)matches.push(i);if(matches.length!==1){send({outcome:'BLOCKED',reason:'TURN_MISMATCH',assistant_match_count:matches.length,semantic_candidate_count:0,candidate_token:'-',stage:stage});return;}const target=turns[matches[0]],author=target.author;if(!author){send({outcome:'BLOCKED',reason:'NO_AUTHOR',assistant_match_count:1,semantic_candidate_count:0,candidate_token:'-',stage:stage});return;}stage='EFFECT_RESOURCE';const depth=e=>{let d=0,p=e;while(p&&p!==target.el){d++;p=p.parentElement;}return d;};const good=[];for(const e of Array.from(author.querySelectorAll('a')).filter(V)){const hrefAttr=e.getAttribute('href');const noHref=hrefAttr===null||String(hrefAttr).trim()==='';const targetBlank=N(e.getAttribute('target')||'')==='_blank';const externalRel=/noopener|noreferrer|external/.test(N(e.getAttribute('rel')||''));const on=typeof e.onclick==='function'||e.hasAttribute('onclick');const st=getComputedStyle(e),ptr=N(st.cursor||'').includes('pointer'),und=N(st.textDecorationLine||st.textDecoration||'').includes('underline');const disabled=e.hasAttribute('disabled')||e.getAttribute('aria-disabled')==='true';const excluded=!!e.closest(`form,nav,aside,header,[role='navigation'],[data-testid*='composer']`);const p=e.parentElement;const parentOn=!!(p&&(typeof p.onclick==='function'||p.hasAttribute('onclick')));const parentSingle=!!(p&&p.querySelectorAll&&p.querySelectorAll('a').length===1);if(noHref&&targetBlank&&externalRel&&on&&(ptr||und)&&!disabled&&!excluded&&parentOn&&parentSingle){const token=H([SIG(e),SIG(p),depth(e),targetBlank?1:0,externalRel?1:0,on?1:0,ptr?1:0,und?1:0].join('|'));good.push({el:e,token:token});}}if(good.length!==1||good[0].token!==want){send({outcome:'BLOCKED',reason:'RESOURCE_CHANGED',assistant_match_count:1,semantic_candidate_count:good.length,candidate_token:good.length===1?good[0].token:'-',stage:stage});return;}const e=good[0].el,r=e.getBoundingClientRect();if(!(r&&r.width>0&&r.height>0)){send({outcome:'BLOCKED',reason:'NOT_READY',assistant_match_count:1,semantic_candidate_count:1,candidate_token:good[0].token,stage:'EFFECT_NOT_READY'});return;}stage='EFFECT_CLICK';e.click();stage='EFFECT_AFTER_CLICK';send({outcome:'DISPATCHED',reason:'CLICK_RETURNED',assistant_match_count:1,semantic_candidate_count:1,candidate_token:good[0].token,stage:stage});}catch(_){send({outcome:'EXCEPTION',reason:'SCRIPT_EXCEPTION',assistant_match_count:0,semantic_candidate_count:0,candidate_token:'-',stage:stage});}})()'''

certdir=Path('ci/v88-resource-webmessage-bridge-acceptance')
certdir.mkdir(parents=True,exist_ok=True)
cert_sentinel=CERT_JS_TEMPLATE.replace('__CP_TX_JSON__',json.dumps('a'*32)).replace('__CP_CERT_JSON__',json.dumps('b'*32)).replace('__CP_EPOCH__','7').replace('__CP_EXPECTED_JSON__',json.dumps('0123abcd'))
effect_sentinel=EFFECT_JS_TEMPLATE.replace('__CP_TX_JSON__',json.dumps('a'*32)).replace('__CP_EFFECT_JSON__',json.dumps('c'*32)).replace('__CP_EPOCH__','7').replace('__CP_EXPECTED_JSON__',json.dumps('0123abcd')).replace('__CP_CANDIDATE_JSON__',json.dumps('deadbeef'))
(certdir/'resource-cert-sentinel.js').write_text(cert_sentinel)
(certdir/'resource-effect-sentinel.js').write_text(effect_sentinel)
(certdir/'resource-cert-template-sha256-input.txt').write_text(CERT_JS_TEMPLATE)
(certdir/'resource-effect-template-sha256-input.txt').write_text(EFFECT_JS_TEMPLATE)

# Insert strict bridge helpers and exact templates before the existing drive method.
insert=s.index('    private void driveResourceV82(')
helpers='''    private static final String RESOURCE_CERT_JS_V88_TEMPLATE='''+json.dumps(CERT_JS_TEMPLATE,ensure_ascii=True)+''';
    private static final String RESOURCE_EFFECT_JS_V88_TEMPLATE='''+json.dumps(EFFECT_JS_TEMPLATE,ensure_ascii=True)+''';

    private boolean hex8V88(String x){return x!=null&&x.matches("^[0-9a-f]{8}$");}
    private boolean nonceV88(String x){return x!=null&&x.matches("^[0-9a-f]{32}$");}
    private String newNonceV88(){return UUID.randomUUID().toString().replace("-","").toLowerCase(java.util.Locale.ROOT);}
    private String jsonV88(String x){return JSONObject.quote(x==null?"":x);}
    private boolean bridgeStageV88(String x){return x!=null&&x.matches("^[A-Z0-9_]{1,64}$");}

    private String resourceBridgeCertV88Js(String expected,String tx,String cert,long epoch){
        if(!hex8V88(expected)||!nonceV88(tx)||!nonceV88(cert)||epoch<0)return "";
        return RESOURCE_CERT_JS_V88_TEMPLATE.replace("__CP_EXPECTED_JSON__",jsonV88(expected)).replace("__CP_TX_JSON__",jsonV88(tx)).replace("__CP_CERT_JSON__",jsonV88(cert)).replace("__CP_EPOCH__",Long.toString(epoch));
    }

    private String resourceBridgeEffectV88Js(String expected,String tx,String effect,String candidate,long epoch){
        if(!hex8V88(expected)||!nonceV88(tx)||!nonceV88(effect)||!hex8V88(candidate)||epoch<0)return "";
        return RESOURCE_EFFECT_JS_V88_TEMPLATE.replace("__CP_EXPECTED_JSON__",jsonV88(expected)).replace("__CP_TX_JSON__",jsonV88(tx)).replace("__CP_EFFECT_JSON__",jsonV88(effect)).replace("__CP_CANDIDATE_JSON__",jsonV88(candidate)).replace("__CP_EPOCH__",Long.toString(epoch));
    }

    private void bridgeNoEffectTerminalV88(String claimStatus,String classification,String message){
        if(resourceV82Finalized)return;resourceV82Finalized=true;prefs.edit().putString("resource_v88_claim_status",claimStatus).commit();JSONObject st=baseState();put(st,"actuator",resourceV82Actuator);put(st,"effect_dispatched",false);put(st,"effect_attempted",resourceV88EffectAttempted);put(st,"bridge_cert_accepted",resourceV88BridgeCertAccepted);put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);emit("RESOURCE_ACTION",classification,st);status.setText(message);clearResourceV82TerminalState();
    }

    private void handleResourceBridgeMessageV88(String data,long bridgeEpoch){
        if(data==null||data.length()<2||data.length()>2048)return;JSONObject o;try{o=new JSONObject(data);}catch(Exception e){return;}String type=o.optString("type","");if(!type.startsWith("CP_RESOURCE_"))return;
        if("CP_RESOURCE_CERT_V88".equals(type)){handleResourceCertMessageV88(o,bridgeEpoch);return;}
        if("CP_RESOURCE_EFFECT_V88".equals(type)){handleResourceEffectMessageV88(o,bridgeEpoch);}
    }

    private void handleResourceCertMessageV88(JSONObject o,long bridgeEpoch){
        if(resourceV82Finalized||resourceV88EffectAttempted||!resourceV82PreEffectPending)return;
        boolean protocol=o.optInt("v",0)==1&&bridgeEpoch==documentEpoch&&o.optLong("epoch",-1L)==documentEpoch&&resourceV88TxNonce.equals(o.optString("tx",""))&&resourceV88CertNonce.equals(o.optString("cert",""))&&resourceV88ClaimTurnFingerprint.equals(o.optString("expected",""))&&nonceV88(resourceV88TxNonce)&&nonceV88(resourceV88CertNonce)&&hex8V88(resourceV88ClaimTurnFingerprint);
        if(!protocol){bridgeNoEffectTerminalV88("BRIDGE_CERT_INVALID_NO_ACTION","RESOURCE_ACTION_ABORTED_BRIDGE_CERT_INVALID_NO_ACTION","Resource bridge certification correlation failed; no action dispatched.");return;}
        String stage=o.optString("stage","");if(!bridgeStageV88(stage)||!o.optBoolean("ok",false)){bridgeNoEffectTerminalV88("BRIDGE_CERT_SCRIPT_ERROR_NO_ACTION","RESOURCE_ACTION_ABORTED_BRIDGE_CERT_SCRIPT_ERROR_NO_ACTION","Resource bridge certification script did not produce a valid bounded receipt; no action dispatched.");return;}
        resourceV82DriveInFlight=false;++resourceV88CertSerial;int matches=o.optInt("assistant_match_count",0),n=o.optInt("semantic_candidate_count",0);boolean same=o.optBoolean("same_assistant_turn",false),ready=o.optBoolean("ready",false);String token=o.optString("candidate_token","-");JSONObject st=baseState();put(st,"actuator",resourceV82Actuator);put(st,"assistant_identity_mode","V64_NORMALIZED_FNV_CONTEXT");put(st,"assistant_match_count",matches);put(st,"same_assistant_turn",same);put(st,"semantic_candidate_count",n);put(st,"ready",ready);put(st,"bridge_stage",stage);put(st,"bridge_epoch_match",true);put(st,"bridge_nonce_match",true);put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);
        if(!same){resourceV82Finalized=true;emit("RESOURCE_ACTION",matches>1?"RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_IDENTITY_AMBIGUOUS_PRE_EFFECT":"RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_CHANGED_PRE_EFFECT",st);status.setText("Resource semantic Assistant identity changed before effect; no action dispatched.");clearResourceV82TerminalState();return;}
        if(n==0||!ready){emit("RESOURCE_ACTION","RESOURCE_TARGET_TRANSIENTLY_ABSENT_WAITING_EVENT",st);status.setText("Resource bridge cert saw no ready target; waiting for fresh UI feedback before any effect.");return;}
        if(n!=1||!hex8V88(token)){bridgeNoEffectTerminalV88("BRIDGE_CERT_AMBIGUOUS_NO_ACTION","RESOURCE_ACTION_BLOCKED_AMBIGUOUS_FRESH_TARGET","Resource bridge cert was ambiguous; no action dispatched.");return;}
        resourceV88BridgeCertAccepted=true;resourceV88CertCandidateToken=token;put(st,"bridge_cert_accepted",true);emit("RESOURCE_ACTION","PASS_RESOURCE_BRIDGE_CERT_ACCEPTED",st);dispatchResourceEffectV88();
    }

    private void dispatchResourceEffectV88(){
        if(resourceV82Finalized||resourceV88EffectAttempted||!resourceV88BridgeCertAccepted)return;
        if(!"JS_POPUP".equals(resourceV82Actuator)){bridgeNoEffectTerminalV88("BRIDGE_ACCEPTANCE_REQUIRES_JS_ACTUATOR","RESOURCE_ACTION_BLOCKED_BRIDGE_ACCEPTANCE_REQUIRES_JS_ACTUATOR","This acceptance build authorizes same-task Resource effect only for the calibrated JS actuator; no action dispatched.");return;}
        if(!hex8V88(resourceV88ClaimTurnFingerprint)||!hex8V88(resourceV88CertCandidateToken)||!nonceV88(resourceV88TxNonce)){bridgeNoEffectTerminalV88("BRIDGE_EFFECT_INPUT_INVALID_NO_ACTION","RESOURCE_ACTION_ABORTED_BRIDGE_CERT_INVALID_NO_ACTION","Resource effect inputs failed strict grammar; no action dispatched.");return;}
        resourceV88EffectAttempted=true;resourceV88EffectNonce=newNonceV88();resourceV82PreEffectPending=false;resourceV82DriveInFlight=false;resourceNavigationPending=true;++resourceV82TimeoutSerial;final long serial=++resourceV88EffectSerial;final String effectNonce=resourceV88EffectNonce;String js=resourceBridgeEffectV88Js(resourceV88ClaimTurnFingerprint,resourceV88TxNonce,effectNonce,resourceV88CertCandidateToken,documentEpoch);JSONObject armed=baseState();put(armed,"actuator",resourceV82Actuator);put(armed,"bridge_cert_accepted",true);put(armed,"effect_attempted",true);put(armed,"effect_dispatched",false);put(armed,"receipt_listening_armed_before_effect_script",true);put(armed,"raw_url_remote",false);put(armed,"raw_text_remote",false);put(armed,"raw_html_remote",false);emit("RESOURCE_ACTION","RESOURCE_EFFECT_ATTEMPT_ARMED_AFTER_BRIDGE_CERT",armed);
        if(web==null||js.isEmpty()){resourceNavigationPending=false;bridgeNoEffectTerminalV88("EFFECT_SCRIPT_NOT_DISPATCHED_NO_ACTION","RESOURCE_ACTION_EFFECT_BLOCKED_TARGET_CHANGED_NO_ACTION","Resource effect script could not be dispatched; no action occurred.");return;}
        try{web.evaluateJavascript(js,null);}catch(Exception e){resourceNavigationPending=false;bridgeNoEffectTerminalV88("EFFECT_SCRIPT_DISPATCH_EXCEPTION_NO_ACTION","RESOURCE_ACTION_EFFECT_BLOCKED_TARGET_CHANGED_NO_ACTION","Resource effect script dispatch failed synchronously; no action occurred.");return;}
        resourceV82Handler.postDelayed(()->{if(!resourceV82Finalized&&resourceV88EffectAttempted&&!resourceV88EffectBridgeResultAccepted&&!resourceV82EffectDispatched&&serial==resourceV88EffectSerial&&effectNonce.equals(resourceV88EffectNonce)){terminalResourceV82("EFFECT_ATTEMPT_NO_BRIDGE_RESULT_NO_REPLAY","RESOURCE_ACTION_UNCERTAIN_EFFECT_ATTEMPT_NO_BRIDGE_RESULT_NO_REPLAY","Resource effect script was attempted but no bounded bridge result or navigation/download receipt arrived; no replay.",true);}},2500L);
    }

    private void handleResourceEffectMessageV88(JSONObject o,long bridgeEpoch){
        if(resourceV82Finalized||!resourceV88EffectAttempted)return;boolean protocol=o.optInt("v",0)==1&&bridgeEpoch==documentEpoch&&o.optLong("epoch",-1L)==documentEpoch&&resourceV88TxNonce.equals(o.optString("tx",""))&&resourceV88EffectNonce.equals(o.optString("effect",""))&&resourceV88ClaimTurnFingerprint.equals(o.optString("expected",""))&&resourceV88CertCandidateToken.equals(o.optString("cert_candidate",""))&&nonceV88(resourceV88TxNonce)&&nonceV88(resourceV88EffectNonce)&&hex8V88(resourceV88ClaimTurnFingerprint)&&hex8V88(resourceV88CertCandidateToken);if(!protocol){terminalResourceV82("EFFECT_BRIDGE_INVALID_NO_REPLAY","RESOURCE_ACTION_UNCERTAIN_EFFECT_BRIDGE_INVALID_NO_REPLAY","Resource effect bridge correlation was invalid after an effect attempt; no replay.",true);return;}if(resourceV88EffectBridgeResultAccepted)return;resourceV88EffectBridgeResultAccepted=true;++resourceV88EffectSerial;String outcome=o.optString("outcome",""),stage=o.optString("stage",""),token=o.optString("candidate_token","-");JSONObject st=baseState();put(st,"actuator",resourceV82Actuator);put(st,"effect_attempted",true);put(st,"bridge_effect_outcome",outcome);put(st,"bridge_stage",bridgeStageV88(stage)?stage:"INVALID");put(st,"semantic_candidate_count",o.optInt("semantic_candidate_count",0));put(st,"assistant_match_count",o.optInt("assistant_match_count",0));put(st,"candidate_token_match",resourceV88CertCandidateToken.equals(token));put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);
        if("BLOCKED".equals(outcome)){resourceNavigationPending=false;resourceV82EffectDispatched=false;resourceV82Finalized=true;prefs.edit().putString("resource_v88_claim_status","EFFECT_BLOCKED_TARGET_CHANGED_NO_ACTION").commit();emit("RESOURCE_ACTION","RESOURCE_ACTION_EFFECT_BLOCKED_TARGET_CHANGED_NO_ACTION",st);status.setText("Resource changed at same-task effect re-certification; no click was dispatched.");clearResourceV82TerminalState();return;}
        if("EXCEPTION".equals(outcome)){terminalResourceV82("EFFECT_SCRIPT_EXCEPTION_NO_REPLAY","RESOURCE_ACTION_UNCERTAIN_EFFECT_SCRIPT_EXCEPTION_NO_REPLAY","Resource effect script reported an exception after the effect attempt began; no replay.",true);return;}
        if(!"DISPATCHED".equals(outcome)||!resourceV88CertCandidateToken.equals(token)){terminalResourceV82("EFFECT_BRIDGE_INVALID_NO_REPLAY","RESOURCE_ACTION_UNCERTAIN_EFFECT_BRIDGE_INVALID_NO_REPLAY","Resource effect bridge result was not an exact dispatched receipt; no replay.",true);return;}
        resourceV82EffectDispatched=true;resourceV82ClickConfirmed=true;pageUiDispatches++;pageUiWrites++;put(st,"effect_dispatched",true);emit("RESOURCE_ACTION","PASS_RESOURCE_JS_SAME_TASK_RECERT_AND_CLICK_DISPATCHED_WAITING_RECEIPT",st);armResourceReceiptDeadlineV88(resourceV82Actuator);if(!resourceV82Finalized)status.setText("Resource acted exactly once after bridge certification; waiting for navigation/download/external receipt.");
    }

'''
s=s[:insert]+helpers+s[insert:]

# Admission remains evaluateJavascript-return based because that path is already proven;
# after durable claim, all final authority is carried by WebMessagePort.
method('beginResourceAcceptanceV82',r'''    private void beginResourceAcceptanceV82(){
        if(resourceV82Finalized||"NONE".equals(resourceV82Actuator))return;resourceScanDocumentEpoch=documentEpoch;resourceScanPageFinishedEpoch=pageFinishedEpoch;
        eval(assistantLocalResourceCertifyV82Js(),o->{
            JSONObject admission=baseState();put(admission,"semantic_candidate_count",o.optInt("semantic_candidate_count",0));put(admission,"assistant_turn_count",o.optInt("assistant_turn_count",0));put(admission,"user_turn_count",o.optInt("user_turn_count",0));put(admission,"assistant_ordinal",o.optInt("assistant_ordinal",-1));put(admission,"last_assistant_exists",o.optBoolean("last_assistant_exists",false));put(admission,"author_message_exists",o.optBoolean("author_message_exists",false));put(admission,"exact_unique",o.optBoolean("exact_unique",false));put(admission,"assistant_identity_unique",o.optBoolean("assistant_identity_unique",false));put(admission,"assistant_identity_match_count",o.optInt("assistant_identity_match_count",0));put(admission,"assistant_identity_mode","V64_NORMALIZED_FNV_CONTEXT");put(admission,"assistant_content_hash",o.optString("assistant_content_hash","-"));put(admission,"assistant_norm_len",o.optInt("assistant_norm_len",-1));put(admission,"preceding_user_hash",o.optString("preceding_user_hash","-"));put(admission,"preceding_user_norm_len",o.optInt("preceding_user_norm_len",-1));put(admission,"assistant_projection_hash",o.optString("assistant_projection_hash","-"));put(admission,"preceding_user_projection_hash",o.optString("preceding_user_projection_hash","-"));put(admission,"assistant_projection_len",o.optInt("assistant_projection_len",-1));put(admission,"preceding_user_projection_len",o.optInt("preceding_user_projection_len",-1));put(admission,"projection_authority",false);put(admission,"actuator",resourceV82Actuator);put(admission,"raw_url_remote",false);put(admission,"raw_text_remote",false);put(admission,"raw_html_remote",false);
            boolean epochFresh=resourceScanDocumentEpoch==documentEpoch&&resourceScanPageFinishedEpoch==pageFinishedEpoch&&pageFinishedEpoch==documentEpoch;String candidate=o.optString("candidate_token","-"),turnFp=o.optString("assistant_fingerprint","-");boolean identityUnique=o.optBoolean("assistant_identity_unique",false);boolean admitted=o.optBoolean("success",false)&&o.optBoolean("exact_unique",false)&&o.optInt("semantic_candidate_count",0)==1&&identityUnique&&hex8V88(candidate)&&hex8V88(turnFp)&&epochFresh;
            put(admission,"epoch_fresh",epochFresh);put(admission,"admitted",admitted);emit("RESOURCE_DISCOVERY",admitted?"PASS_ASSISTANT_LOCAL_RESOURCE_UNIQUE_ADMITTED":"RESOURCE_ACTION_BLOCKED_NO_UNIQUE_ASSISTANT_LOCAL_RESOURCE",admission);if(!admitted){status.setText("TEST RESOURCE blocked: no unique strong assistant-local Resource with unique semantic turn identity was admitted.");return;}
            resourceV82AdmissionToken=candidate;resourceV82InitialCandidateToken=candidate;resourceV88ClaimTurnFingerprint=turnFp;resourceV82ClaimDocumentEpoch=documentEpoch;resourceV82ClaimPageFinishedEpoch=pageFinishedEpoch;resourceV88TxNonce=newNonceV88();
            String origin=originOfV82(web==null?null:web.getUrl());if(origin.isEmpty()||!nonceV88(resourceV88TxNonce)){emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_UNSUPPORTED_CURRENT_ORIGIN",admission);status.setText("TEST RESOURCE blocked: unsupported origin or transaction nonce failure.");return;}resourceV82ActionOrigin=origin;
            String claimId="resource-v88-"+UUID.randomUUID();boolean committed=prefs.edit().putString("resource_v88_claim_status","CLAIMED").putString("resource_v88_claim_id",claimId).putString("resource_v88_turn_fingerprint",turnFp).putString("resource_v88_tx_nonce",resourceV88TxNonce).commit();JSONObject pre=baseState();put(pre,"claim_committed",committed);put(pre,"actuator",resourceV82Actuator);put(pre,"assistant_bound",true);put(pre,"assistant_identity_mode","V64_NORMALIZED_FNV_CONTEXT");put(pre,"bridge_transaction",true);put(pre,"diagnostic_only",false);put(pre,"raw_url_remote",false);put(pre,"raw_text_remote",false);put(pre,"raw_html_remote",false);emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_RESOURCE_ACTION":"RESOURCE_ACTION_CLAIM_COMMIT_FAILED",pre);if(!committed){status.setText("TEST RESOURCE blocked: durable claim failed.");return;}
            resourceActionPendingId=claimId;resourceV82Finalized=false;resourceV82EffectDispatched=false;resourceV82PreEffectPending=true;resourceV82DriveInFlight=false;resourceV88BridgeCertAccepted=false;resourceV88EffectAttempted=false;resourceV88EffectBridgeResultAccepted=false;resourceNavigationPending=false;resourceDownloadPending=false;resourceWrappedSawSameOriginNavigation=false;installResourceDownloadListenerV82();try{web.getSettings().setJavaScriptCanOpenWindowsAutomatically("JS_POPUP".equals(resourceV82Actuator));}catch(Exception ignored){}
            final long timeout=++resourceV82TimeoutSerial;resourceV82Handler.postDelayed(()->{if(!resourceV82Finalized&&resourceV82PreEffectPending&&!resourceV88EffectAttempted&&!resourceV82EffectDispatched&&timeout==resourceV82TimeoutSerial){resourceV82Finalized=true;prefs.edit().putString("resource_v88_claim_status","PRE_EFFECT_TARGET_TIMEOUT").commit();JSONObject st=baseState();put(st,"actuator",resourceV82Actuator);put(st,"effect_dispatched",false);put(st,"assistant_identity_mode","V64_NORMALIZED_FNV_CONTEXT");put(st,"bridge_cert_accepted",resourceV88BridgeCertAccepted);put(st,"raw_url_remote",false);emit("RESOURCE_ACTION","RESOURCE_ACTION_PRE_EFFECT_TARGET_TIMEOUT_NO_ACTION",st);status.setText("Resource did not become bridge-certified before the fail-closed timeout; no action was dispatched.");clearResourceV82TerminalState();}},6000L);
            driveResourceV82("AFTER_CLAIM");
        });
    }

''')

method('driveResourceV82OnObservedState',r'''    private void driveResourceV82OnObservedState(String reason){
        if(!resourceV82PreEffectPending||resourceV88EffectAttempted||resourceV82EffectDispatched||resourceV82DriveInFlight||resourceV82Finalized)return;driveResourceV82("OBSERVED_"+hashNorm(reason));
    }

''')

# Final certification request: evaluateJavascript is dispatch-only; callback is null.
method('driveResourceV82',r'''    private void driveResourceV82(String reason){
        if(!resourceV82PreEffectPending||resourceV88EffectAttempted||resourceV82EffectDispatched||resourceV82DriveInFlight||resourceV82Finalized)return;if(resourceV82ClaimDocumentEpoch!=documentEpoch||resourceV82ClaimPageFinishedEpoch!=pageFinishedEpoch||pageFinishedEpoch!=documentEpoch){resourceV82Finalized=true;JSONObject st=baseState();put(st,"effect_dispatched",false);put(st,"raw_url_remote",false);emit("RESOURCE_ACTION","RESOURCE_ACTION_ABORTED_STALE_CLAIM_PRE_EFFECT",st);status.setText("Resource claim became stale before bridge certification.");clearResourceV82TerminalState();return;}
        if(!hex8V88(resourceV88ClaimTurnFingerprint)||!nonceV88(resourceV88TxNonce)){bridgeNoEffectTerminalV88("BRIDGE_CERT_INPUT_INVALID_NO_ACTION","RESOURCE_ACTION_ABORTED_BRIDGE_CERT_INVALID_NO_ACTION","Resource bridge cert inputs failed strict grammar; no action dispatched.");return;}
        resourceV82DriveInFlight=true;resourceV88BridgeCertAccepted=false;resourceV88CertCandidateToken="-";resourceV88CertNonce=newNonceV88();final String certNonce=resourceV88CertNonce;final long serial=++resourceV88CertSerial;String js=resourceBridgeCertV88Js(resourceV88ClaimTurnFingerprint,resourceV88TxNonce,certNonce,documentEpoch);JSONObject st=baseState();put(st,"actuator",resourceV82Actuator);put(st,"bridge_cert_requested",true);put(st,"drive_reason_hash",hashNorm(reason));put(st,"effect_attempted",false);put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);emit("RESOURCE_ACTION","RESOURCE_BRIDGE_CERT_REQUESTED",st);
        if(web==null||js.isEmpty()){resourceV82DriveInFlight=false;bridgeNoEffectTerminalV88("BRIDGE_CERT_SCRIPT_NOT_DISPATCHED","RESOURCE_ACTION_ABORTED_BRIDGE_CERT_SCRIPT_ERROR_NO_ACTION","Resource bridge certification script could not be dispatched; no action occurred.");return;}
        try{web.evaluateJavascript(js,null);}catch(Exception e){resourceV82DriveInFlight=false;bridgeNoEffectTerminalV88("BRIDGE_CERT_SCRIPT_DISPATCH_EXCEPTION","RESOURCE_ACTION_ABORTED_BRIDGE_CERT_SCRIPT_ERROR_NO_ACTION","Resource bridge certification dispatch failed; no action occurred.");return;}
        resourceV82Handler.postDelayed(()->{if(!resourceV82Finalized&&resourceV82PreEffectPending&&!resourceV88EffectAttempted&&resourceV82DriveInFlight&&serial==resourceV88CertSerial&&certNonce.equals(resourceV88CertNonce)){resourceV82DriveInFlight=false;bridgeNoEffectTerminalV88("NO_FINAL_CERT_RECEIPT_NO_ACTION","RESOURCE_ACTION_NO_FINAL_CERT_RECEIPT_NO_ACTION","No exact WebMessagePort Resource certification receipt arrived; no action dispatched.");}},2500L);
    }

''')

# Rename telemetry config file/class and advance package update identity.
ACT.write_text(s);OLD.unlink()
oldcfg=PKG/"TelemetryConfigV87.java";newcfg=PKG/"TelemetryConfigV88.java";assert oldcfg.exists();newcfg.write_text(oldcfg.read_text().replace("TelemetryConfigV87","TelemetryConfigV88"));oldcfg.unlink()

grad=ROOT/"app/build.gradle";gs=grad.read_text();gs=re.sub(r"versionCode\s+88\b","versionCode 89",gs);gs=gs.replace("0.85-stable-diag-resource-parse-boundary-probe","0.86-stable-diag-resource-webmessage-bridge-acceptance");grad.write_text(gs)
man=ROOT/"app/src/main/AndroidManifest.xml";ms=man.read_text().replace("OrchestratorResourceToolsV87Activity","OrchestratorResourceToolsV88Activity");man.write_text(ms)

# Generator-time contract gates.
out=ACT.read_text()
required=[
    'SCHEMA="cp-v88-resource-webmessage-bridge-acceptance-v1"','SCENARIO="resource-webmessage-bridge-certified-acceptance"','TelemetryConfigV88',
    'CP_RESOURCE_CERT_V88','CP_RESOURCE_EFFECT_V88','RESOURCE_CERT_JS_V88_TEMPLATE','RESOURCE_EFFECT_JS_V88_TEMPLATE',
    'handleResourceBridgeMessageV88','handleResourceCertMessageV88','handleResourceEffectMessageV88','resourceBridgeCertV88Js','resourceBridgeEffectV88Js',
    'web.evaluateJavascript(js,null)','PASS_RESOURCE_BRIDGE_CERT_ACCEPTED','RESOURCE_EFFECT_ATTEMPT_ARMED_AFTER_BRIDGE_CERT','PASS_RESOURCE_JS_SAME_TASK_RECERT_AND_CLICK_DISPATCHED_WAITING_RECEIPT',
    'RESOURCE_ACTION_NO_FINAL_CERT_RECEIPT_NO_ACTION','RESOURCE_ACTION_EFFECT_BLOCKED_TARGET_CHANGED_NO_ACTION','RESOURCE_ACTION_UNCERTAIN_EFFECT_ATTEMPT_NO_BRIDGE_RESULT_NO_REPLAY',
    'receipt_listening_armed_before_effect_script','V64_NORMALIZED_FNV_CONTEXT','PASS_ASSISTANT_LOCAL_RESOURCE_UNIQUE_ADMITTED','CLAIMED_BEFORE_RESOURCE_ACTION',
    'resourceV88DiagnosticOnly(){return false;}','raw_url_remote",false','raw_text_remote",false','raw_html_remote",false'
]
for x in required: assert x in out,x
# Final Resource authority no longer consumes evaluateJavascript return values.
dm=re.search(r'    private void driveResourceV82\([^\n]*\)\{.*?\n    \}\n\n',out,re.S);assert dm
assert 'evalResourceFinalV88' not in dm.group(0) and 'assistantLocalResourceFinalV82Js' not in dm.group(0)
assert 'web.evaluateJavascript(js,null)' in dm.group(0)
# Same-task effect template has exactly one click and no fallback geometry search.
assert EFFECT_JS_TEMPLATE.count('.click();')==1,EFFECT_JS_TEMPLATE.count('.click();')
assert 'window.__cpEventPort' in CERT_JS_TEMPLATE and 'window.__cpEventPort' in EFFECT_JS_TEMPLATE
assert 'innerText' in CERT_JS_TEMPLATE and 'innerText' in EFFECT_JS_TEMPLATE
for bad in ['elementFromPoint','document.evaluate','XPathResult','getCookie(','CookieManager','addJavascriptInterface','Thread.sleep','ScheduledExecutorService','TimerTask']:
    assert bad not in out,bad
assert out.count('dispatchTouchEvent(')==4,out.count('dispatchTouchEvent(')
assert 'versionCode 89' in grad.read_text()
assert "versionName '0.86-stable-diag-resource-webmessage-bridge-acceptance'" in grad.read_text()
assert 'OrchestratorResourceToolsV88Activity' in man.read_text()
assert 'ControlPlaneAccessibilityServiceV51' in man.read_text() and '@xml/cp_accessibility_service_v51' in man.read_text()
print('PASS v0.86 generator: WebMessagePort final certification + strict nonce/epoch correlation + same-task JS recert/click + receipt-first no-replay semantics')
