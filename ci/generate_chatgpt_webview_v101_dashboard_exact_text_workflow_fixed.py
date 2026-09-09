#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v101_dashboard_exact_text_workflow.py',run_name='__main__')
p=PKG/'OrchestratorDashboardV101ExactTextWorkflowActivity.java'
s=p.read_text()

# Use the guarded facade for material execution so post-dispatch uncertainty
# cannot be downgraded to ordinary failure and CLAIMED cannot become success.
old='private int targetBaselineTurnCount=0; private WorkflowJournalV1 workflowJournal;'
new='private int targetBaselineTurnCount=0; private WorkflowJournalGuardV1 workflowJournal;'
assert s.count(old)==1,('journal guard field',s.count(old))
s=s.replace(old,new,1)
old='workflowJournal=new WorkflowJournalV1(getSharedPreferences("cp_v101_workflow_journal",MODE_PRIVATE));'
new='workflowJournal=new WorkflowJournalGuardV1(getSharedPreferences("cp_v101_workflow_journal",MODE_PRIVATE));'
assert s.count(old)==1,('journal guard init',s.count(old))
s=s.replace(old,new,1)

# Use the same line-aware contenteditable extractor for the post-write observer
# as the exact writer/send gate. Raw Python strings intentionally preserve the
# two backslashes required inside generated JavaScript string literals.
old="const txt=e=>{if(!e)return '';if('value' in e&&typeof e.value==='string')return e.value;return e.innerText||e.textContent||'';};const DS=e=>"
new=r"const txt=e=>{if(!e)return '';if('value' in e&&typeof e.value==='string')return e.value;return e.innerText||e.textContent||'';};const XT=e=>{if(!e)return '';if('value' in e&&typeof e.value==='string')return X(e.value);const kids=Array.from(e.children||[]);if(kids.length&&kids.every(k=>k.tagName==='P'))return kids.map(k=>{if(k.children.length===1&&k.children[0].tagName==='BR'&&!k.textContent)return '';return X(k.innerText||k.textContent||'').replace(/\n$/,'');}).join('\n');return X(e.innerText||e.textContent||'');};const DS=e=>"
assert s.count(old)==1,('planner exact extractor insertion',s.count(old))
s=s.replace(old,new,1)

old="composer_hash:c?H(N(ct)):'-',composer_exact_hash:c?H(X(ct)):'-',composer_chars:ct.length,"
new="composer_hash:c?H(N(ct)):'-',composer_exact_hash:c?H(XT(c)):'-',composer_chars:ct.length,"
assert s.count(old)==1,('planner exact composer hash',s.count(old))
s=s.replace(old,new,1)

# Do not trim material turn text before the exact receipt hash. Avoid matching
# the regex literal itself so this transform is insensitive to Python escaping.
prefix="const text=(e.innerText||e.textContent||'').replace("
suffix="if(role==='assistant')assistantEls.push(e);"
start=s.find(prefix)
assert start>=0,'exact turn prefix missing'
end=s.find(suffix,start)
assert end>start,'exact turn suffix missing'
segment=s[start:end]
assert "T.push({role:role,text:text,hash:H(N(text)),exact_hash:H(X(text)),chars:text.length});" in segment
replacement="const raw=X(e.innerText||e.textContent||'');if(!N(raw))continue;T.push({role:role,text:raw,hash:H(N(raw)),exact_hash:H(raw),chars:raw.length});"
s=s[:start]+replacement+s[end:]

# Once DISPATCH_IN_FLIGHT is durably committed, a crash/JS uncertainty must be
# classified as possible external effect even before the click callback returns.
old='if(!targetJournal.edit().putString("status","CLAIMED_BEFORE_TARGET_SEND").putString("composer_hash",targetExpectedExactHash).commit()||!workflowJournal.markDispatchInFlight(activeWorkflowId,activeWorkflowStepId,targetAttemptId)){targetFail("TARGET_SEND_CLAIM_FAILED");return;}eval(foreground,targetSendExactJs(targetExpectedExactHash),o->{'
new='if(!targetJournal.edit().putString("status","CLAIMED_BEFORE_TARGET_SEND").putString("composer_hash",targetExpectedExactHash).commit()||!workflowJournal.markDispatchInFlight(activeWorkflowId,activeWorkflowStepId,targetAttemptId)){targetFail("TARGET_SEND_CLAIM_FAILED");return;}targetSendDispatchedThisAttempt=true;eval(foreground,targetSendExactJs(targetExpectedExactHash),o->{'
assert s.count(old)==1,('dispatch-in-flight uncertainty fence',s.count(old))
s=s.replace(old,new,1)

old='targetChatEffectDispatches++;targetSendDispatchedThisAttempt=true;if(!workflowJournal.markWaitingReceipt(activeWorkflowId,activeWorkflowStepId,targetAttemptId))'
new='targetChatEffectDispatches++;if(!workflowJournal.markWaitingReceipt(activeWorkflowId,activeWorkflowStepId,targetAttemptId))'
assert s.count(old)==1,('remove late uncertainty assignment',s.count(old))
s=s.replace(old,new,1)

for required in [
    'WorkflowJournalGuardV1 workflowJournal',
    "composer_exact_hash:c?H(XT(c))",
    "const raw=X(e.innerText||e.textContent||'');if(!N(raw))continue",
    'targetSendDispatchedThisAttempt=true;eval(foreground,targetSendExactJs',
    'TARGET_SEND_RECEIPT',
]:
    assert required in s,required
assert (PKG/'WorkflowJournalGuardV1.java').exists()
assert s.count('targetChatEffectDispatches++')==1
assert s.count('.click()')==2
p.write_text(s)
print('PASS v0.90.7 fixed generator: exact line-aware observation + guarded conservative dispatch uncertainty')
