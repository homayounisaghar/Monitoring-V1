#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# Build from the exact v0.57 source, fixing only the sparse click-dispatch
# validation bug and adding a fail-closed recovery path for the known v0.57
# state where the Work click was durably claimed/observed but receipt polling
# never began. After recovery to Chat, v0.58 automatically performs one fresh
# Chat -> Work -> Chat proof with independent receipts.
runpy.run_path("ci/generate_chatgpt_webview_v59_chat_work_autonomous_roundtrip.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
old=PKG/"OrchestratorChatWorkAutonomousRoundtripV59Activity.java"
new=PKG/"OrchestratorChatWorkRecoveryRoundtripV60Activity.java"
s=old.read_text()

# Identity.
s=s.replace("public class OrchestratorChatWorkAutonomousRoundtripV59Activity",
            "public class OrchestratorChatWorkRecoveryRoundtripV60Activity")
s=s.replace('cp-v59-chat-work-autonomous-roundtrip-v1','cp-v60-chat-work-recovery-roundtrip-v1')
s=s.replace('chat-work-autonomous-roundtrip','chat-work-recovery-roundtrip')
s=s.replace('v0.57 autonomous Chat/Work roundtrip ready.','v0.58 recovery-aware Chat/Work roundtrip ready.')
s=s.replace('v0.57 ready.','v0.58 ready.')
s=s.replace('testId="cp57-"+UUID.randomUUID();','testId="cp58-"+UUID.randomUUID();')

# Persisted v0.57 claim namespace is intentionally reused so v0.58 can safely
# interpret the exact prior CLAIMED/UNCERTAIN state after an in-place update.
field_anchor='    private String claimStatus="IDLE";\n    private long startedMs=0L;\n'
assert s.count(field_anchor)==1
s=s.replace(field_anchor,
'''    private String claimStatus="IDLE";
    private int proofBaseDispatches=0;
    private boolean recoveryMode=false;
    private String priorClaimStatus="IDLE";
    private String priorChatStructHash="-";
    private String priorWorkStructHash="-";
    private long startedMs=0L;
''')

# Replace start+start resolver with recovery-aware logic. If current state is
# already Chat, run the normal proof. If current state is Work, recovery is
# allowed only when the exact v0.57 persisted UNCERTAIN_AFTER_WORK_CLAIM and
# both saved structural hashes match the live exact pair. Recovery first obtains
# two independent Work reads before any restore click.
pat=r'    private void startRoundtrip\(\)\{.*?\n    \}\n\n    private void resolveStart\(\)\{.*?\n    \}\n\n    private void claimAndClick'
m=re.search(pat,s,re.S)
assert m, "start/resolve anchor missing"
replacement=r'''    private void startRoundtrip(){
        if(running)return;
        priorClaimStatus=prefs.getString("claim_status","IDLE");
        priorChatStructHash=prefs.getString("chat_struct_hash","-");
        priorWorkStructHash=prefs.getString("work_struct_hash","-");
        running=true; telemetrySeq=0; pageUiDispatches=0; proofBaseDispatches=0; modelOptionWrites=0; effortWrites=0;
        targetReceipt=false; restoreReceipt=false; recoveryMode=false; chatStructHash="-"; workStructHash="-";
        testId="cp58-"+UUID.randomUUID(); startedMs=System.currentTimeMillis(); claimStatus="RUNNING_START_GATE";
        prefs.edit().putString("test_id",testId).putString("claim_status",claimStatus).commit();
        JSONObject st=baseState(); put(st,"prior_claim_status",priorClaimStatus);
        emit("ROUNDTRIP_STARTED","RUNNING",st);
        status.setText("Checking exact Chat/Work state; v0.57 Work recovery is allowed only from its persisted claim...");
        h.postDelayed(this::resolveStart,300L);
    }

    private void resolveStart(){
        if(!running)return;
        eval(scanJs(),o->{
            if(!running)return;
            if(exactPair(o)&&stateChat(o)){
                emitSnapshot("START_GATE","PASS_EXACT_CHAT_ACTIVE_BASELINE",o);
                chatStructHash=o.optString("chat_struct_hash","-");
                workStructHash=o.optString("work_struct_hash","-");
                if("-".equals(chatStructHash)||"-".equals(workStructHash)||chatStructHash.equals(workStructHash)){
                    finish("CHAT_WORK_STRUCTURAL_IDENTITY_INVALID_ZERO_WRITE");return;
                }
                proofBaseDispatches=pageUiDispatches;
                claimAndClick(PURPOSE_WORK); return;
            }
            boolean recoverable=exactPair(o)&&stateWork(o)
                    &&"UNCERTAIN_AFTER_WORK_CLAIM".equals(priorClaimStatus)
                    &&priorChatStructHash.equals(o.optString("chat_struct_hash",""))
                    &&priorWorkStructHash.equals(o.optString("work_struct_hash",""))
                    &&!"-".equals(priorChatStructHash)&&!"-".equals(priorWorkStructHash);
            emitSnapshot("START_GATE",recoverable?"PASS_EXACT_V057_WORK_RECOVERY_BASELINE":"CHAT_WORK_START_NOT_RECOVERABLE_ZERO_WRITE",o);
            if(!recoverable){finish("CHAT_WORK_START_NOT_RECOVERABLE_ZERO_WRITE");return;}
            recoveryMode=true; chatStructHash=priorChatStructHash; workStructHash=priorWorkStructHash;
            claimStatus="RECOVERY_VERIFYING_PRIOR_WORK_RECEIPT";
            prefs.edit().putString("claim_status",claimStatus).commit();
            status.setText("v0.57 prior Work click recovered from durable claim. Verifying stable Work receipt before restore...");
            h.postDelayed(()->pollRecoveryWork(0,0),RECEIPT_POLL_MS);
        });
    }

    private void pollRecoveryWork(final int attempt,final int stableHits){
        if(!running||!recoveryMode)return;
        eval(scanJs(),o->{
            if(!running||!recoveryMode)return;
            boolean match=sameStructs(o)&&stateWork(o);
            int hits=match?stableHits+1:0;
            if(match&&(hits==1||hits==2)) emitSnapshot("RECOVERY_WORK_RECEIPT",
                    hits>=2?"PASS_STABLE_RECOVERED_WORK_RECEIPT":"RECOVERY_RECEIPT_CANDIDATE_1_OF_2",o);
            if(hits>=2){
                targetReceipt=true; claimStatus="RECOVERY_WORK_RECEIPT_CONFIRMED";
                prefs.edit().putString("claim_status",claimStatus).commit();
                h.postDelayed(()->prepareRestore(o),350L); return;
            }
            if(attempt>=MAX_RECEIPT_POLLS){
                claimStatus="UNCERTAIN_V057_WORK_RECOVERY_NO_WRITE";
                prefs.edit().putString("claim_status",claimStatus).commit();
                finish("V057_WORK_RECOVERY_RECEIPT_UNRESOLVED_ZERO_NEW_WRITE"); return;
            }
            if(attempt==0||attempt==10||attempt==20) emitSnapshot("RECOVERY_WORK_RECEIPT_WAIT","READ_ONLY_RECOVERY_POLL_NO_REPLAY",o);
            h.postDelayed(()->pollRecoveryWork(attempt+1,hits),RECEIPT_POLL_MS);
        });
    }

    private void claimAndClick'''
s=s[:m.start()]+replacement+s[m.end():]

# Relative dispatch gates support one recovery restore click followed by a fresh
# proof. Normal fresh proof still uses base=0.
old_target='            if(pageUiDispatches!=0||targetReceipt){finish("WORK_CLICK_REPLAY_BLOCKED");return;}\n'
assert s.count(old_target)==1
s=s.replace(old_target,
            '            if(pageUiDispatches!=proofBaseDispatches||targetReceipt){finish("WORK_CLICK_REPLAY_BLOCKED");return;}\n')
old_restore='            if(!targetReceipt||pageUiDispatches!=1){finish("CHAT_RESTORE_NOT_ALLOWED_WITHOUT_WORK_RECEIPT");return;}\n'
assert s.count(old_restore)==1
s=s.replace(old_restore,
'''            boolean dispatchCountOk=recoveryMode?pageUiDispatches==0:pageUiDispatches==proofBaseDispatches+1;
            if(!targetReceipt||!dispatchCountOk){finish("CHAT_RESTORE_NOT_ALLOWED_WITHOUT_WORK_RECEIPT");return;}
''')

# Root cause fix: clickJs() returns a deliberately sparse dispatch receipt.
# Do not call sameStructs(), which requires a full scan payload. Validate the
# two structural hashes directly from the sparse receipt, then perform state
# confirmation only via the subsequent independent read-only scan polling.
old_dispatch='''            boolean dispatched=o.optBoolean("success",false)&&o.optBoolean("dispatched",false)&&o.optBoolean("click_observed",false)
                    &&o.optInt("match_count",0)==1&&sameStructs(o);'''
assert s.count(old_dispatch)==1
s=s.replace(old_dispatch,
'''            boolean dispatched=o.optBoolean("success",false)&&o.optBoolean("dispatched",false)&&o.optBoolean("click_observed",false)
                    &&o.optInt("match_count",0)==1
                    &&chatStructHash.equals(o.optString("chat_struct_hash",""))
                    &&workStructHash.equals(o.optString("work_struct_hash",""));''')

# After a recovered Chat receipt, automatically begin a fresh proof from Chat.
old_chat_complete='''                }else{
                    restoreReceipt=true; claimStatus="CHAT_RESTORE_CONFIRMED";
                    prefs.edit().putString("claim_status",claimStatus).commit();
                    boolean pass=pageUiDispatches==2&&targetReceipt&&restoreReceipt&&modelOptionWrites==0&&effortWrites==0;
                    finish(pass?"PASS_AUTONOMOUS_CHAT_WORK_CHAT_ROUNDTRIP":"CHAT_WORK_ROUNDTRIP_INCOMPLETE");
                }'''
assert s.count(old_chat_complete)==1
s=s.replace(old_chat_complete,
'''                }else{
                    restoreReceipt=true; claimStatus=recoveryMode?"RECOVERY_CHAT_RESTORE_CONFIRMED":"CHAT_RESTORE_CONFIRMED";
                    prefs.edit().putString("claim_status",claimStatus).commit();
                    if(recoveryMode){
                        emitSnapshot("RECOVERY_COMPLETE","PASS_RECOVERED_V057_WORK_TO_CHAT",o);
                        recoveryMode=false; targetReceipt=false; restoreReceipt=false;
                        proofBaseDispatches=pageUiDispatches;
                        priorClaimStatus="RECOVERY_CONSUMED";
                        claimStatus="RUNNING_START_GATE_AFTER_RECOVERY";
                        prefs.edit().putString("claim_status",claimStatus).commit();
                        status.setText("Recovered to Chat with receipt. Starting fresh autonomous Chat -> Work -> Chat proof...");
                        h.postDelayed(this::resolveStart,500L); return;
                    }
                    boolean pass=pageUiDispatches==proofBaseDispatches+2&&targetReceipt&&restoreReceipt&&modelOptionWrites==0&&effortWrites==0;
                    String passClass=proofBaseDispatches>0?"PASS_RECOVERY_PLUS_AUTONOMOUS_CHAT_WORK_CHAT_ROUNDTRIP":"PASS_AUTONOMOUS_CHAT_WORK_CHAT_ROUNDTRIP";
                    finish(pass?passClass:"CHAT_WORK_ROUNDTRIP_INCOMPLETE");
                }''')

old_prepare='        if(!targetReceipt||pageUiDispatches!=1){finish("CHAT_RESTORE_NOT_ALLOWED_WITHOUT_WORK_RECEIPT");return;}\n'
assert s.count(old_prepare)==1
s=s.replace(old_prepare,
'''        boolean dispatchCountOk=recoveryMode?pageUiDispatches==0:pageUiDispatches==proofBaseDispatches+1;
        if(!targetReceipt||!dispatchCountOk){finish("CHAT_RESTORE_NOT_ALLOWED_WITHOUT_WORK_RECEIPT");return;}
''')

# Telemetry explicitly separates recovery and fresh-proof dispatch accounting.
base_anchor='''        put(o,"page_ui_dispatches",pageUiDispatches); put(o,"page_ui_writes",pageUiDispatches);
        put(o,"model_option_writes",modelOptionWrites); put(o,"effort_writes",effortWrites); put(o,"target_receipt",targetReceipt); put(o,"restore_receipt",restoreReceipt);'''
assert s.count(base_anchor)==1
s=s.replace(base_anchor,
'''        put(o,"page_ui_dispatches",pageUiDispatches); put(o,"page_ui_writes",pageUiDispatches);
        put(o,"proof_base_dispatches",proofBaseDispatches); put(o,"recovery_mode",recoveryMode);
        put(o,"model_option_writes",modelOptionWrites); put(o,"effort_writes",effortWrites); put(o,"target_receipt",targetReceipt); put(o,"restore_receipt",restoreReceipt);''')

# Safety contracts.
assert 'sameStructs(o);' not in s[s.find('boolean dispatched='):s.find('emitSnapshot(purpose==PURPOSE_WORK?"WORK_CLICK_DISPATCH"')]
assert 'PASS_STABLE_RECOVERED_WORK_RECEIPT' in s
assert 'PASS_RECOVERED_V057_WORK_TO_CHAT' in s
assert 'PASS_RECOVERY_PLUS_AUTONOMOUS_CHAT_WORK_CHAT_ROUNDTRIP' in s
assert 'UNCERTAIN_AFTER_WORK_CLAIM' in s
assert 'pollRecoveryWork' in s
assert 't.e.click();' in s
assert 'document.evaluate' not in s
assert 'elementFromPoint' not in s
assert 'CookieManager' not in s
new.write_text(s)

# Fresh telemetry config.
cfg=(PKG/"TelemetryConfigV59.java").read_text()
(PKG/"TelemetryConfigV60.java").write_text(cfg.replace("TelemetryConfigV59","TelemetryConfigV60"))
ns=new.read_text().replace("TelemetryConfigV59","TelemetryConfigV60")
new.write_text(ns)

# In-place update identity.
g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+60\b","versionCode 61",gs)
gs=gs.replace("0.57-stable-diag-chat-work-autonomous-roundtrip",
              "0.58-stable-diag-chat-work-recovery-roundtrip")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorChatWorkAutonomousRoundtripV59Activity",
              "OrchestratorChatWorkRecoveryRoundtripV60Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
for v in (52,53,54,55,56,57,58,59,60):
    assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

print("generated v0.58 recovery-aware Chat/Work roundtrip: sparse click receipt validation fixed; prior v0.57 Work claim recovered only by exact stable read; fresh proof auto-runs after recovery")
