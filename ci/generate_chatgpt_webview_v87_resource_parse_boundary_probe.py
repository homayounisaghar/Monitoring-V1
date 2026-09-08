#!/usr/bin/env python3
from pathlib import Path
import runpy,re,json

# v0.85: zero-effect parse-boundary diagnostic only.
# Preserve v0.84 Resource admission, V64 semantic turn authority, durable claim,
# calibrated actuator setup, and no-replay policy. Refactor the final JS into one
# template used by BOTH the APK and CI syntax gate, and localize Java-side
# evaluateJavascript decode failures without uploading raw callback content.
runpy.run_path("ci/generate_chatgpt_webview_v86_resource_final_stage_probe.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorResourceToolsV86Activity.java"
ACT=PKG/"OrchestratorResourceToolsV87Activity.java"
s=OLD.read_text()

# Advance identity only. The inherited semantic/claim/actuator machinery remains.
s=s.replace("OrchestratorResourceToolsV86Activity","OrchestratorResourceToolsV87Activity")
s=s.replace("TelemetryConfigV86","TelemetryConfigV87")
s=s.replace("V86","V87").replace("v86","v87")
s=s.replace('SCHEMA="cp-v87-resource-final-stage-probe-v1"','SCHEMA="cp-v87-resource-parse-boundary-probe-v1"')
s=s.replace('SCENARIO="resource-final-recert-stage-probe"','SCENARIO="resource-final-eval-parse-boundary-probe"')
s=s.replace('testId="cp84-"+UUID.randomUUID();','testId="cp85-"+UUID.randomUUID();')
s=s.replace('v0.84 Final re-certification stage diagnostic ready.','v0.85 Final evaluation parse-boundary diagnostic ready.')
s=s.replace('cp_v87_resource_final_stage_probe','cp_v87_resource_parse_boundary_probe')

# One exact source template for runtime and CI. __CP_EXPECTED_JSON__ is replaced
# at runtime with jsV79(expectedTurnFingerprint), and in CI with a fixed JSON
# string sentinel. The template is intentionally zero-effect.
FINAL_JS_TEMPLATE=r'''(function(){let stage='FINAL_STAGE_INIT';const SH=s=>{let h=2166136261>>>0;const q=(s||'').toString();for(let i=0;i<q.length;i++){h^=q.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};try{const expected=__CP_EXPECTED_JSON__;const N=s=>(s||'').toString().replace(/\s+/g,' ').trim().toLowerCase();const H=SH;const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const st=getComputedStyle(e);if(st.display==='none'||st.visibility==='hidden'||st.opacity==='0')return false;try{if(typeof e.checkVisibility==='function')return e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});}catch(_){}return true;};const SIG=e=>e?H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|'))):'-';const TXT=e=>{if(!e)return '';return (e.innerText||e.textContent||'').replace(/\s+$/,'').trim();};const PROJ=raw=>{const q=(raw||'').toString().normalize('NFKC');let z='';for(let k=0;k<q.length;k++){const c=q.charCodeAt(k);if((c>=8203&&c<=8207)||(c>=8234&&c<=8238)||(c>=8288&&c<=8303)||c===65279)continue;z+=q[k];}return N(z);};stage='FINAL_STAGE_TURN_QUERY';const nodes=[];const seen=new Set();const add=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);nodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(add);stage='FINAL_STAGE_TURN_MAP';const turns=nodes.map(e=>{const a=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');const role=a?N(a.getAttribute('data-message-author-role')||'-'):'-';const raw=TXT(a),norm=N(raw),proj=PROJ(raw);return{el:e,author:a,role:role,content_hash:norm?H(norm):'-',norm_len:norm.length,projection_hash:proj?H(proj):'-',projection_len:proj.length};}).filter(t=>t.role==='user'||t.role==='assistant');stage='FINAL_STAGE_FINGERPRINT_BUILD';const precedingUser=i=>{for(let j=i-1;j>=0;j--)if(turns[j].role==='user')return turns[j];return null;};const FP=i=>{const t=turns[i];if(!t||t.role!=='assistant'||t.content_hash==='-')return '-';const u=precedingUser(i);return H(['assistant',t.content_hash,t.norm_len,u?u.content_hash:'-',u?u.norm_len:0].join('|'));};stage='FINAL_STAGE_MATCH_SCAN';const matches=[];let lastAssistant=-1,ao=0,lastOrdinal=-1;for(let i=0;i<turns.length;i++)if(turns[i].role==='assistant'){if(FP(i)===expected)matches.push(i);lastAssistant=i;lastOrdinal=ao++;}const assistantCount=ao,userCount=turns.filter(t=>t.role==='user').length;stage='FINAL_STAGE_DIAG_BUILD';const observed=lastAssistant>=0?turns[lastAssistant]:null,ou=lastAssistant>=0?precedingUser(lastAssistant):null;const diag={assistant_turn_count:assistantCount,user_turn_count:userCount,observed_assistant_ordinal:lastOrdinal,observed_assistant_content_hash:observed?observed.content_hash:'-',observed_assistant_norm_len:observed?observed.norm_len:-1,observed_preceding_user_hash:ou?ou.content_hash:'-',observed_preceding_user_norm_len:ou?ou.norm_len:-1,observed_assistant_projection_hash:observed?observed.projection_hash:'-',observed_assistant_projection_len:observed?observed.projection_len:-1,observed_preceding_user_projection_hash:ou?ou.projection_hash:'-',observed_preceding_user_projection_len:ou?ou.projection_len:-1,observed_last_assistant_fingerprint:lastAssistant>=0?FP(lastAssistant):'-',diagnostic_only:true,error_class:'-',failure_stage:'-',exception_name_class:'-',exception_family_hash:'-'};if(matches.length!==1)return JSON.stringify(Object.assign({},diag,{success:true,same_assistant_turn:false,assistant_match_count:matches.length,semantic_candidate_count:0,ready:false,clicked:false,candidate_token:'-',final_stage:stage}));const target=turns[matches[0]],author=target.author;if(!author)return JSON.stringify(Object.assign({},diag,{success:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:0,ready:false,clicked:false,candidate_token:'-',final_stage:stage}));stage='FINAL_STAGE_RESOURCE_SCAN';const depth=e=>{let d=0,p=e;while(p&&p!==target.el){d++;p=p.parentElement;}return d;};const good=[];for(const e of Array.from(author.querySelectorAll('a')).filter(V)){const hrefAttr=e.getAttribute('href');const noHref=hrefAttr===null||String(hrefAttr).trim()==='';const targetBlank=N(e.getAttribute('target')||'')==='_blank';const externalRel=/noopener|noreferrer|external/.test(N(e.getAttribute('rel')||''));const on=typeof e.onclick==='function'||e.hasAttribute('onclick');const st=getComputedStyle(e),ptr=N(st.cursor||'').includes('pointer'),und=N(st.textDecorationLine||st.textDecoration||'').includes('underline');const disabled=e.hasAttribute('disabled')||e.getAttribute('aria-disabled')==='true';const excluded=!!e.closest(`form,nav,aside,header,[role='navigation'],[data-testid*='composer']`);const p=e.parentElement;const parentOn=!!(p&&(typeof p.onclick==='function'||p.hasAttribute('onclick')));const parentSingle=!!(p&&p.querySelectorAll&&p.querySelectorAll('a').length===1);if(noHref&&targetBlank&&externalRel&&on&&(ptr||und)&&!disabled&&!excluded&&parentOn&&parentSingle){const token=H([SIG(e),SIG(p),depth(e),targetBlank?1:0,externalRel?1:0,on?1:0,ptr?1:0,und?1:0].join('|'));good.push({el:e,token:token});}}if(good.length!==1)return JSON.stringify(Object.assign({},diag,{success:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:good.length,ready:false,clicked:false,candidate_token:'-',final_stage:stage}));stage='FINAL_STAGE_READY_CHECK';const e=good[0].el,r=e.getBoundingClientRect();const ready=!!(r&&r.width>0&&r.height>0);stage='FINAL_STAGE_COMPLETE';return JSON.stringify(Object.assign({},diag,{success:true,same_assistant_turn:true,assistant_match_count:1,semantic_candidate_count:1,ready:ready,clicked:false,candidate_token:good[0].token,center_x_css:ready?r.left+r.width/2:0,center_y_css:ready?r.top+r.height/2:0,viewport_w_css:window.innerWidth||document.documentElement.clientWidth||0,viewport_h_css:window.innerHeight||document.documentElement.clientHeight||0,final_stage:stage}));}catch(e){let en='Error';try{en=(e&&e.name)?String(e.name):'Error';}catch(_){}en=(en.replace(/[^A-Za-z]/g,'').slice(0,32)||'Error');return JSON.stringify({success:false,error_class:'ASSISTANT_LOCAL_RESOURCE_FINAL_EXCEPTION',failure_stage:stage,final_stage:stage,exception_name_class:en,exception_family_hash:SH(en),same_assistant_turn:false,assistant_match_count:0,semantic_candidate_count:0,ready:false,clicked:false,candidate_token:'-',diagnostic_only:true});}})()'''
assert FINAL_JS_TEMPLATE.count('__CP_EXPECTED_JSON__')==1

# CI consumes the exact same template with a fixed sentinel.
diagdir=Path('ci/v87-resource-parse-boundary-probe')
diagdir.mkdir(parents=True,exist_ok=True)
sentinel=FINAL_JS_TEMPLATE.replace('__CP_EXPECTED_JSON__',json.dumps('cp-v87-sentinel-fingerprint'))
(diagdir/'final-script-sentinel.js').write_text(sentinel)
(diagdir/'final-script-template-sha256-input.txt').write_text(FINAL_JS_TEMPLATE)

# Replace v0.84 final-method construction with the shared template constant.
pat=r'    private String assistantLocalResourceFinalV82Js\([^\n]*\)\{.*?\n    \}\n\n'
m=re.search(pat,s,re.S);assert m,'final method not found'
java_literal=json.dumps(FINAL_JS_TEMPLATE,ensure_ascii=True)
final_java='''    private static final String FINAL_JS_V87_TEMPLATE='''+java_literal+''';\n\n    private String assistantLocalResourceFinalV82Js(String expectedTurnFingerprint,boolean ignoredJsActuate){\n        return FINAL_JS_V87_TEMPLATE.replace("__CP_EXPECTED_JSON__",jsV79(expectedTurnFingerprint));\n    }\n\n'''
s=s[:m.start()]+final_java+s[m.end():]

# Focused Java-side decoder. It never emits raw callback text; it only annotates
# the returned JSONObject (or a synthetic failure object) with coarse stages.
drive_at=s.index('    private void driveResourceV82(')
decode=r'''    private String finalDecodeLengthBucketV87(int n){
        if(n<0)return "NONE";if(n==0)return "ZERO";if(n<=64)return "LE64";if(n<=256)return "LE256";if(n<=1024)return "LE1024";if(n<=4096)return "LE4096";return "GT4096";
    }

    private JSONObject finalDecodeFailureV87(String stage,boolean callbackNull,String outerClass,int outerStringLen){
        JSONObject o=new JSONObject();put(o,"success",false);put(o,"error_class","FINAL_EVAL_DECODE_ERROR");put(o,"decode_stage",stage);put(o,"decode_failure_stage",stage);put(o,"callback_null",callbackNull);put(o,"outer_token_class",outerClass);put(o,"outer_string_length_bucket",finalDecodeLengthBucketV87(outerStringLen));put(o,"inner_object_parse_success",false);put(o,"raw_callback_remote",false);return o;
    }

    private void evalResourceFinalV87(String js,final JsonConsumer cb){
        if(web==null){cb.accept(finalDecodeFailureV87("WEBVIEW_NULL",true,"NONE",-1));return;}
        web.evaluateJavascript(js,new android.webkit.ValueCallback<String>(){
            @Override public void onReceiveValue(String value){
                if(value==null){cb.accept(finalDecodeFailureV87("CALLBACK_NULL",true,"NONE",-1));return;}
                Object outer;
                try{outer=new org.json.JSONTokener(value).nextValue();}
                catch(Exception e){cb.accept(finalDecodeFailureV87("OUTER_JSON_PARSE",false,"UNPARSED",-1));return;}
                if(outer==null||outer==org.json.JSONObject.NULL){cb.accept(finalDecodeFailureV87("OUTER_JSON_NULL",false,"NULL",-1));return;}
                if(outer instanceof org.json.JSONObject){JSONObject o=(JSONObject)outer;put(o,"decode_stage","OUTER_OBJECT_OK");put(o,"decode_failure_stage","-");put(o,"callback_null",false);put(o,"outer_token_class","OBJECT");put(o,"outer_string_length_bucket","NONE");put(o,"inner_object_parse_success",true);put(o,"raw_callback_remote",false);cb.accept(o);return;}
                if(!(outer instanceof String)){cb.accept(finalDecodeFailureV87("OUTER_NOT_STRING_OR_OBJECT",false,outer.getClass().getSimpleName().toUpperCase(java.util.Locale.ROOT),-1));return;}
                String raw=(String)outer;int n=raw.length();
                try{JSONObject o=new JSONObject(raw);put(o,"decode_stage","INNER_OBJECT_OK");put(o,"decode_failure_stage","-");put(o,"callback_null",false);put(o,"outer_token_class","STRING");put(o,"outer_string_length_bucket",finalDecodeLengthBucketV87(n));put(o,"inner_object_parse_success",true);put(o,"raw_callback_remote",false);cb.accept(o);}
                catch(Exception e){cb.accept(finalDecodeFailureV87("INNER_OBJECT_PARSE",false,"STRING",n));}
            }
        });
    }

'''
s=s[:drive_at]+decode+s[drive_at:]

# Route only the final Resource evaluation through the focused decoder.
old='eval(assistantLocalResourceFinalV82Js(resourceV87ClaimTurnFingerprint,js),o->{'
assert s.count(old)==1,s.count(old)
s=s.replace(old,'evalResourceFinalV87(assistantLocalResourceFinalV82Js(resourceV87ClaimTurnFingerprint,js),o->{',1)

# Propagate sanitized decode state into terminal telemetry.
needle='boolean finalEvalSuccess=o.optBoolean("success",false);String finalErrorClass=o.optString("error_class","-"),finalFailureStage=o.optString("failure_stage","-"),finalStage=o.optString("final_stage","-"),finalExceptionNameClass=o.optString("exception_name_class","-"),finalExceptionFamilyHash=o.optString("exception_family_hash","-");'
assert s.count(needle)==1,s.count(needle)
s=s.replace(needle,needle+'String finalDecodeStage=o.optString("decode_stage","-");String finalDecodeFailureStage=o.optString("decode_failure_stage","-");boolean finalCallbackNull=o.optBoolean("callback_null",false);String finalOuterTokenClass=o.optString("outer_token_class","-");String finalOuterStringLengthBucket=o.optString("outer_string_length_bucket","-");boolean finalInnerObjectParseSuccess=o.optBoolean("inner_object_parse_success",false);',1)
needle2='put(st,"final_exception_family_hash",finalExceptionFamilyHash);'
assert s.count(needle2)==1,s.count(needle2)
s=s.replace(needle2,needle2+'put(st,"final_decode_stage",finalDecodeStage);put(st,"final_decode_failure_stage",finalDecodeFailureStage);put(st,"final_callback_null",finalCallbackNull);put(st,"final_outer_token_class",finalOuterTokenClass);put(st,"final_outer_string_length_bucket",finalOuterStringLengthBucket);put(st,"final_inner_object_parse_success",finalInnerObjectParseSuccess);put(st,"raw_callback_remote",false);',1)

oldif='if(!finalEvalSuccess){resourceV82Finalized=true;emit("RESOURCE_ACTION","RESOURCE_ACTION_ABORTED_FINAL_RECERTIFICATION_EXCEPTION_DIAGNOSTIC",st);status.setText("Final re-certification diagnostic captured exception stage; no action dispatched.");clearResourceV82TerminalState();return;}'
assert s.count(oldif)==1,s.count(oldif)
newif='if(!finalEvalSuccess){resourceV82Finalized=true;String cls="FINAL_EVAL_DECODE_ERROR".equals(finalErrorClass)?"RESOURCE_ACTION_ABORTED_FINAL_EVAL_PARSE_BOUNDARY_DIAGNOSTIC":"RESOURCE_ACTION_ABORTED_FINAL_RECERTIFICATION_EXCEPTION_DIAGNOSTIC";emit("RESOURCE_ACTION",cls,st);status.setText("Final evaluation diagnostic captured a sanitized failure boundary; no action dispatched.");clearResourceV82TerminalState();return;}'
s=s.replace(oldif,newif,1)

# Fix terminal metadata for both diagnostic aborts.
term='            "RESOURCE_ACTION_ABORTED_ASSISTANT_TURN_IDENTITY_AMBIGUOUS_PRE_EFFECT",\n'
assert s.count(term)==1,s.count(term)
s=s.replace(term,term+'            "RESOURCE_ACTION_ABORTED_FINAL_RECERTIFICATION_EXCEPTION_DIAGNOSTIC",\n            "RESOURCE_ACTION_ABORTED_FINAL_EVAL_PARSE_BOUNDARY_DIAGNOSTIC",\n',1)

ACT.write_text(s);OLD.unlink()

# Rename telemetry config and build identity.
oldcfg=PKG/"TelemetryConfigV86.java";newcfg=PKG/"TelemetryConfigV87.java"
cfg=oldcfg.read_text().replace("TelemetryConfigV86","TelemetryConfigV87")
newcfg.write_text(cfg);oldcfg.unlink()
man=ROOT/"app/src/main/AndroidManifest.xml";ms=man.read_text().replace("OrchestratorResourceToolsV86Activity","OrchestratorResourceToolsV87Activity");man.write_text(ms)
grad=ROOT/"app/build.gradle";gs=grad.read_text().replace('versionCode 87','versionCode 88').replace("versionName '0.84-stable-diag-resource-final-stage-probe'","versionName '0.85-stable-diag-resource-parse-boundary-probe'");grad.write_text(gs)

# Generator-time safety and identity invariants.
out=ACT.read_text()
required=['SCHEMA="cp-v87-resource-parse-boundary-probe-v1"','SCENARIO="resource-final-eval-parse-boundary-probe"','TelemetryConfigV87','FINAL_JS_V87_TEMPLATE','__CP_EXPECTED_JSON__','evalResourceFinalV87','FINAL_EVAL_DECODE_ERROR','CALLBACK_NULL','OUTER_JSON_PARSE','OUTER_JSON_NULL','OUTER_NOT_STRING_OR_OBJECT','INNER_OBJECT_PARSE','INNER_OBJECT_OK','RESOURCE_ACTION_ABORTED_FINAL_EVAL_PARSE_BOUNDARY_DIAGNOSTIC','RESOURCE_ACTION_ABORTED_FINAL_RECERTIFICATION_EXCEPTION_DIAGNOSTIC','resourceV87DiagnosticOnly()','V64_NORMALIZED_FNV_CONTEXT','PASS_ASSISTANT_LOCAL_RESOURCE_UNIQUE_ADMITTED','CLAIMED_BEFORE_RESOURCE_ACTION','raw_callback_remote",false']
for x in required: assert x in out,x
fm=re.search(r'    private String assistantLocalResourceFinalV82Js\([^\n]*\)\{.*?\n    \}\n\n',out,re.S);assert fm
assert '.click();' not in FINAL_JS_TEMPLATE
assert 'e.message' not in FINAL_JS_TEMPLATE and '.stack' not in FINAL_JS_TEMPLATE
assert out.index('if(resourceV87DiagnosticOnly())') < out.index('if(js){boolean clicked=')
for bad in ['elementFromPoint','document.evaluate','XPathResult','getCookie(','CookieManager','addJavascriptInterface','Thread.sleep','ScheduledExecutorService','TimerTask']:
    assert bad not in out,bad
assert 'versionCode 88' in grad.read_text()
assert "versionName '0.85-stable-diag-resource-parse-boundary-probe'" in grad.read_text()
assert 'OrchestratorResourceToolsV87Activity' in man.read_text()
print('PASS v0.85 generator: shared exact final-JS template, focused sanitized evaluateJavascript decode stages, terminal metadata fixed, zero Resource effect')
