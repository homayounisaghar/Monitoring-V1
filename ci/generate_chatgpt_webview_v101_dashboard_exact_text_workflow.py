#!/usr/bin/env python3
from pathlib import Path
import runpy,re

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v100_dashboard_voice_manual_stop_atomic.py',run_name='__main__')
old_java=PKG/'OrchestratorDashboardV100VoiceManualStopAtomicActivity.java'
new_java=PKG/'OrchestratorDashboardV101ExactTextWorkflowActivity.java'
s=old_java.read_text()

# identity
s=s.replace('OrchestratorDashboardV100VoiceManualStopAtomicActivity','OrchestratorDashboardV101ExactTextWorkflowActivity')
s=s.replace('cp-v100-dashboard-voice-manual-stop-atomic-v1','cp-v101-dashboard-exact-text-workflow-journal-v1')
s=s.replace('dashboard-voice-manual-stop-atomic','dashboard-exact-text-workflow-journal')
s=s.replace('cp906-','cp907-')
s=s.replace('cp_v100_stateless_planner','cp_v101_stateless_planner')
s=s.replace('cp_v100_target_execution','cp_v101_target_execution')
s=s.replace('TelemetryConfigV100','TelemetryConfigV101')
s=s.replace('MIC_PERMISSION_REQUEST=906','MIC_PERMISSION_REQUEST=907')

old='private JSONObject pendingRecipe=null; private String pendingTargetBindingId="",pendingTargetPathHash="",pendingTargetAlias="",pendingTargetMessage=""; private boolean targetSendDispatchedThisAttempt=false; private String targetExecutionPhase="IDLE",targetExpectedPath="",targetExpectedBindingId="",targetExpectedMessage="",targetExpectedComposerHash="-",targetBaselineLastUserHash="-",targetAttemptId=""; private int targetBaselineTurnCount=0;'
new='private JSONObject pendingRecipe=null; private String pendingTargetBindingId="",pendingTargetPathHash="",pendingTargetAlias="",pendingTargetMessage=""; private boolean targetSendDispatchedThisAttempt=false; private String targetExecutionPhase="IDLE",targetExpectedPath="",targetExpectedBindingId="",targetExpectedMessage="",targetExpectedComposerHash="-",targetExpectedExactHash="-",targetBaselineLastUserHash="-",targetAttemptId="",activeWorkflowId="",activeWorkflowStepId="send-1"; private int targetBaselineTurnCount=0; private WorkflowJournalV1 workflowJournal;'
assert s.count(old)==1
s=s.replace(old,new,1)

old='navJournal=getSharedPreferences("cp_v91_dashboard_navigation",MODE_PRIVATE); plannerJournal=getSharedPreferences("cp_v101_stateless_planner",MODE_PRIVATE); targetJournal=getSharedPreferences("cp_v101_target_execution",MODE_PRIVATE);'
new=old+' workflowJournal=new WorkflowJournalV1(getSharedPreferences("cp_v101_workflow_journal",MODE_PRIVATE));'
assert s.count(old)==1
s=s.replace(old,new,1)

# Build/claim a one-step durable workflow only after explicit Execute.
old='targetAttemptId="target-"+UUID.randomUUID();targetExpectedPath=b.path;targetExpectedBindingId=b.id;targetExpectedMessage=text;targetExpectedComposerHash="-";targetBaselineLastUserHash="-";targetBaselineTurnCount=0;'
new='targetAttemptId="target-"+UUID.randomUUID();activeWorkflowId="wf-"+UUID.randomUUID();JSONObject wf=buildOneStepWorkflowPlan(activeWorkflowId,op,text);if(wf==null||!workflowJournal.create(wf,ExactTextV1.sha256(wf.toString()))||!workflowJournal.claimEffect(activeWorkflowId,activeWorkflowStepId,targetAttemptId)){status.setText("Execute blocked: durable workflow claim failed.");activeWorkflowId="";return;}targetExpectedPath=b.path;targetExpectedBindingId=b.id;targetExpectedMessage=ExactTextV1.canonical(text);targetExpectedComposerHash="-";targetExpectedExactHash="-";targetBaselineLastUserHash="-";targetBaselineTurnCount=0;'
assert s.count(old)==1
s=s.replace(old,new,1)

# Exact composer and exact user-turn receipt fields.
old='targetExpectedComposerHash.equals(o.optString("composer_hash","-"))&&o.optInt("stop_candidate_count",0)==0'
new='targetExpectedExactHash.equals(o.optString("composer_exact_hash","-"))&&o.optInt("stop_candidate_count",0)==0'
assert s.count(old)==1
s=s.replace(old,new,1)
old='targetExpectedComposerHash.equals(o.optString("last_user_hash","-"));if(!receipt)'
new='targetExpectedExactHash.equals(o.optString("last_user_exact_hash","-"));if(!receipt)'
assert s.count(old)==1
s=s.replace(old,new,1)

# Confirm journal before declaring success.
old='ConversationBindingV91 b=registry.byId(targetExpectedBindingId);targetJournal.edit().putString("status","TARGET_SEND_RECEIPT_CONFIRMED").commit();targetExecutionRunning=false;'
new='ConversationBindingV91 b=registry.byId(targetExpectedBindingId);String exactReply=o.optString("last_user_text","");String receiptDigest=ExactTextV1.sha256(exactReply);if(!workflowJournal.confirmReceipt(activeWorkflowId,activeWorkflowStepId,targetAttemptId,receiptDigest)||!workflowJournal.markStepSucceeded(activeWorkflowId,activeWorkflowStepId)){workflowJournal.markStepUncertain(activeWorkflowId,activeWorkflowStepId,"RECEIPT_JOURNAL_COMMIT_FAILED");targetFail("TARGET_RECEIPT_JOURNAL_FAILED_NO_REPLAY");return;}targetJournal.edit().putString("status","TARGET_SEND_RECEIPT_CONFIRMED").commit();targetExecutionRunning=false;'
assert s.count(old)==1
s=s.replace(old,new,1)

# Exact writer.
old='eval(foreground,plannerSetDraftJs(targetExpectedMessage),o->{if(!targetExecutionRunning||g!=targetExecutionGeneration)return;if(!o.optBoolean("success",false)||!o.optBoolean("mutated",false)||o.optInt("composer_count",0)!=1){targetFail("TARGET_COMPOSER_WRITE_UNCERTAIN_NO_REPLAY");return;}targetExpectedComposerHash=o.optString("composer_hash","-");if("-".equals(targetExpectedComposerHash)){targetFail("TARGET_COMPOSER_HASH_MISSING");return;}targetExecutionPhase="WAIT_TARGET_COMPOSER_RECEIPT";'
new='eval(foreground,targetSetDraftExactJs(targetExpectedMessage),o->{if(!targetExecutionRunning||g!=targetExecutionGeneration)return;if(!o.optBoolean("success",false)||!o.optBoolean("mutated",false)||o.optInt("composer_count",0)!=1){targetFail("TARGET_COMPOSER_WRITE_UNCERTAIN_NO_REPLAY");return;}targetExpectedComposerHash=o.optString("composer_hash","-");targetExpectedExactHash=o.optString("composer_exact_hash","-");if("-".equals(targetExpectedExactHash)){targetFail("TARGET_COMPOSER_EXACT_HASH_MISSING");return;}targetExecutionPhase="WAIT_TARGET_COMPOSER_RECEIPT";'
assert s.count(old)==1
s=s.replace(old,new,1)

# Mark effect in-flight before the click, then waiting-receipt immediately after observed dispatch.
old='private void targetSend(long g){ConversationBindingV91 b=registry.byId(targetExpectedBindingId);if(!targetJournal.edit().putString("status","CLAIMED_BEFORE_TARGET_SEND").putString("composer_hash",targetExpectedComposerHash).commit()){targetFail("TARGET_SEND_CLAIM_FAILED");return;}eval(foreground,plannerSendJs(targetExpectedComposerHash),o->{'
new='private void targetSend(long g){ConversationBindingV91 b=registry.byId(targetExpectedBindingId);if(!targetJournal.edit().putString("status","CLAIMED_BEFORE_TARGET_SEND").putString("composer_hash",targetExpectedExactHash).commit()||!workflowJournal.markDispatchInFlight(activeWorkflowId,activeWorkflowStepId,targetAttemptId)){targetFail("TARGET_SEND_CLAIM_FAILED");return;}eval(foreground,targetSendExactJs(targetExpectedExactHash),o->{'
assert s.count(old)==1
s=s.replace(old,new,1)
old='targetExpectedComposerHash.equals(o.optString("composer_hash","-"));if(!ok){targetFail("TARGET_SEND_UNCERTAIN_NO_REPLAY");return;}targetChatEffectDispatches++;targetSendDispatchedThisAttempt=true;targetExecutionPhase="WAIT_TARGET_SEND_RECEIPT";targetJournal.edit().putString("status","TARGET_SEND_DISPATCHED_AWAITING_RECEIPT").commit();'
new='targetExpectedExactHash.equals(o.optString("composer_exact_hash","-"));if(!ok){workflowJournal.markStepUncertain(activeWorkflowId,activeWorkflowStepId,"TARGET_SEND_DISPATCH_UNCERTAIN");targetFail("TARGET_SEND_UNCERTAIN_NO_REPLAY");return;}targetChatEffectDispatches++;targetSendDispatchedThisAttempt=true;if(!workflowJournal.markWaitingReceipt(activeWorkflowId,activeWorkflowStepId,targetAttemptId)){workflowJournal.markStepUncertain(activeWorkflowId,activeWorkflowStepId,"WAITING_RECEIPT_JOURNAL_FAILED");targetFail("TARGET_SEND_JOURNAL_UNCERTAIN_NO_REPLAY");return;}targetExecutionPhase="WAIT_TARGET_SEND_RECEIPT";targetJournal.edit().putString("status","TARGET_SEND_DISPATCHED_AWAITING_RECEIPT").commit();'
assert s.count(old)==1
s=s.replace(old,new,1)

# Failure state mirrors whether the effect may have crossed the boundary.
old='boolean effectPossiblyDispatched=targetSendDispatchedThisAttempt;targetExecutionRunning=false;'
new='boolean effectPossiblyDispatched=targetSendDispatchedThisAttempt;if(workflowJournal!=null&&!activeWorkflowId.isEmpty()){if(effectPossiblyDispatched)workflowJournal.markStepUncertain(activeWorkflowId,activeWorkflowStepId,why);else workflowJournal.markStepFailed(activeWorkflowId,activeWorkflowStepId,why);}targetExecutionRunning=false;'
assert s.count(old)==1
s=s.replace(old,new,1)

# Add exact hashes to read snapshot while retaining normalized hashes for Planner correlation.
old=r"const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();"
new=r"const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const X=s=>(s||'').replace(/\\r\\n/g,'\\n').replace(/\\r/g,'\\n');const N=s=>X(s).replace(/\\s+/g,' ').trim().toLowerCase();"
assert s.count(old)>=3
# Only plannerReadJs first occurrence is modified here.
s=s.replace(old,new,1)
old="T.push({role:role,text:text,hash:H(N(text)),chars:text.length});"
new="T.push({role:role,text:text,hash:H(N(text)),exact_hash:H(X(text)),chars:text.length});"
assert s.count(old)==1
s=s.replace(old,new,1)
old="last_user_text:lu?lu.text:'',last_user_hash:lu?lu.hash:'-',last_assistant_text:la?la.text:'',last_assistant_hash:la?la.hash:'-',"
new="last_user_text:lu?lu.text:'',last_user_hash:lu?lu.hash:'-',last_user_exact_hash:lu?lu.exact_hash:'-',last_assistant_text:la?la.text:'',last_assistant_hash:la?la.hash:'-',last_assistant_exact_hash:la?la.exact_hash:'-',"
assert s.count(old)==1
s=s.replace(old,new,1)
old="composer_hash:c?H(N(ct)):'-',composer_chars:ct.length,"
new="composer_hash:c?H(N(ct)):'-',composer_exact_hash:c?H(X(ct)):'-',composer_chars:ct.length,"
assert s.count(old)==1
s=s.replace(old,new,1)

# Insert workflow plan builder and dedicated exact target composer primitives.
marker='    private String plannerSetDraftJs(String text){\n'
assert s.count(marker)==1
insert=r'''    private JSONObject buildOneStepWorkflowPlan(String workflowId,JSONObject op,String messageText){
        try{
            JSONObject plan=new JSONObject();plan.put("protocol","cf-workflow-plan.v1");plan.put("request_id",plannerRequestId);plan.put("request_digest",plannerRequestDigest);plan.put("workflow_id",workflowId);plan.put("status","READY");plan.put("ambiguities",new JSONArray());
            JSONObject step=new JSONObject();step.put("step_id",activeWorkflowStepId);step.put("kind","CAPABILITY");step.put("depends_on",new JSONArray());step.put("capability","chat.send_message");
            JSONObject tar=op.optJSONObject("target");JSONObject target=new JSONObject();target.put("chat_ref",tar==null?pendingTargetBindingId:tar.optString("chat_ref",pendingTargetBindingId));step.put("target",target);
            JSONObject args=new JSONObject();JSONObject mv=new JSONObject();mv.put("kind","LITERAL");mv.put("value",ExactTextV1.canonical(messageText));args.put("message_text",mv);step.put("arguments",args);
            JSONObject wait=new JSONObject();wait.put("type","SEND_RECEIPT");wait.put("timeout_ms",60000);wait.put("on_timeout","NEEDS_USER");step.put("wait_for",wait);step.put("outputs",new JSONArray());
            JSONArray steps=new JSONArray();steps.put(step);plan.put("steps",steps);return plan;
        }catch(Exception e){return null;}
    }

    private String targetSetDraftExactJs(String text){
        String q=JSONObject.quote(ExactTextV1.canonical(text));
        return "(function(){try{const T="+q+";"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const X=s=>(s||'').replace(/\\r\\n/g,'\\n').replace(/\\r/g,'\\n');const N=s=>X(s).replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const XT=e=>{if('value' in e&&typeof e.value==='string')return X(e.value);const kids=Array.from(e.children||[]);if(kids.length&&kids.every(k=>k.tagName==='P'))return kids.map(k=>{if(k.children.length===1&&k.children[0].tagName==='BR'&&!k.textContent)return '';return X(k.innerText||k.textContent||'').replace(/\\n$/,'');}).join('\\n');return X(e.innerText||e.textContent||'');};"+
            "const CA=Array.from(document.querySelectorAll('textarea,[contenteditable],[role=textbox]')).filter(e=>V(e)&&!e.hasAttribute('disabled')&&e.getAttribute('aria-disabled')!=='true'&&e.getAttribute('contenteditable')!=='false');const CP=CA.filter(e=>e.id==='prompt-textarea'||N(e.getAttribute('data-testid')||'').includes('composer')||N(e.getAttribute('data-testid')||'').includes('prompt'));const C=CP.length===1?CP:((CP.length===0&&CA.length===1)?CA:[]);if(C.length!==1)return JSON.stringify({success:false,reason:'COMPOSER_COUNT',composer_count:C.length,mutated:false});const e=C[0];"+
            "if(e.tagName==='TEXTAREA'){const d=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value');if(!d||!d.set)return JSON.stringify({success:false,reason:'NO_NATIVE_SETTER',composer_count:1,mutated:false});e.focus();d.set.call(e,T);}else{e.focus();while(e.firstChild)e.removeChild(e.firstChild);const L=T.split('\\n');for(let i=0;i<L.length;i++){const p=document.createElement('p');if(L[i].length)p.appendChild(document.createTextNode(L[i]));else p.appendChild(document.createElement('br'));e.appendChild(p);}}"+
            "e.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText',data:null}));const A=XT(e);return JSON.stringify({success:true,reason:'EXACT_NATIVE_INPUT',composer_count:1,mutated:true,composer_hash:H(N(A)),composer_exact_hash:H(X(A)),composer_exact_chars:A.length});"+
            "}catch(e){return JSON.stringify({success:false,reason:'WRITE_EXCEPTION',composer_count:0,mutated:false});}})();";
    }

    private String targetSendExactJs(String expectedExactHash){
        return "(function(){try{const EH='"+expectedExactHash+"';"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const X=s=>(s||'').replace(/\\r\\n/g,'\\n').replace(/\\r/g,'\\n');const N=s=>X(s).replace(/\\s+/g,' ').trim().toLowerCase();const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const XT=e=>{if('value' in e&&typeof e.value==='string')return X(e.value);const kids=Array.from(e.children||[]);if(kids.length&&kids.every(k=>k.tagName==='P'))return kids.map(k=>{if(k.children.length===1&&k.children[0].tagName==='BR'&&!k.textContent)return '';return X(k.innerText||k.textContent||'').replace(/\\n$/,'');}).join('\\n');return X(e.innerText||e.textContent||'');};"+
            "const CA=Array.from(document.querySelectorAll('textarea,[contenteditable],[role=textbox]')).filter(e=>V(e)&&!e.hasAttribute('disabled')&&e.getAttribute('aria-disabled')!=='true'&&e.getAttribute('contenteditable')!=='false');const CP=CA.filter(e=>e.id==='prompt-textarea'||N(e.getAttribute('data-testid')||'').includes('composer')||N(e.getAttribute('data-testid')||'').includes('prompt'));const C=CP.length===1?CP:((CP.length===0&&CA.length===1)?CA:[]);if(C.length!==1)return JSON.stringify({success:false,reason:'COMPOSER_COUNT',composer_count:C.length,send_match_count:0,dispatched:false,click_observed:false});const ch=H(X(XT(C[0])));if(ch!==EH)return JSON.stringify({success:false,reason:'COMPOSER_EXACT_HASH_DRIFT',composer_exact_hash:ch,send_match_count:0,dispatched:false,click_observed:false});"+
            "const B=Array.from(document.querySelectorAll('button,[role=button]')).filter(V),S=[];for(const e of B){const z=N((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('title')||'')+' '+(e.getAttribute('data-testid')||'')+' '+(e.textContent||''));if(!e.hasAttribute('disabled')&&(z==='send'||z.includes('send message')||z.includes('composer-submit')||z.includes('send-button')||z.includes('submit prompt')))S.push(e);}if(S.length!==1)return JSON.stringify({success:false,reason:'SEND_COUNT',composer_exact_hash:ch,send_match_count:S.length,dispatched:false,click_observed:false});let observed=false;S[0].addEventListener('click',()=>{observed=true;},{capture:true,once:true});S[0].click();return JSON.stringify({success:true,reason:'EXACT_ELEMENT_CLICK',composer_exact_hash:ch,send_match_count:1,dispatched:true,click_observed:observed});"+
            "}catch(e){return JSON.stringify({success:false,reason:'SEND_EXCEPTION',send_match_count:0,dispatched:false,click_observed:false});}})();";
    }

'''
s=s.replace(marker,insert+marker,1)

new_java.write_text(s)
old_java.unlink()

cfg_old=PKG/'TelemetryConfigV100.java'
cfg_new=PKG/'TelemetryConfigV101.java'
cfg=cfg_old.read_text().replace('TelemetryConfigV100','TelemetryConfigV101')
assert 'CONFIGURED=false' in cfg
cfg_new.write_text(cfg)

gradle=ROOT/'app/build.gradle'
g=gradle.read_text()
assert g.count('versionCode 101')==1
assert g.count("versionName '0.90.6-stable-dashboard-voice-manual-stop-atomic'")==1
g=g.replace('versionCode 101','versionCode 102',1).replace(
    "versionName '0.90.6-stable-dashboard-voice-manual-stop-atomic'",
    "versionName '0.90.7-stable-dashboard-exact-text-workflow-journal'",1)
gradle.write_text(g)

man=ROOT/'app/src/main/AndroidManifest.xml'
m=man.read_text()
assert m.count('OrchestratorDashboardV100VoiceManualStopAtomicActivity')==1
m=m.replace('OrchestratorDashboardV100VoiceManualStopAtomicActivity','OrchestratorDashboardV101ExactTextWorkflowActivity',1)
man.write_text(m)

out=new_java.read_text()
for required in [
    'targetSetDraftExactJs',
    'targetSendExactJs',
    'composer_exact_hash',
    'last_user_exact_hash',
    'WorkflowJournalV1',
    'buildOneStepWorkflowPlan',
    'markDispatchInFlight',
    'markWaitingReceipt',
    'confirmReceipt',
    'ExactTextV1.canonical',
    'ExactTextV1.sha256',
    'TARGET_SEND_RECEIPT',
    'TARGET FROZEN: YES',
    'PREVIEW — NOT COMMITTED',
]:
    assert required in out,required
assert out.count('targetChatEffectDispatches++')==1
assert out.count('.click()')==2
assert (PKG/'ExactTextV1.java').exists()
assert (PKG/'WorkflowJournalV1.java').exists()
assert (PKG/'AssistantInfrastructureBoundariesV1.java').exists()
print('PASS v0.90.7 generator: exact multiline target identity + one-step durable workflow journal + preserved explicit execution')
