#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# Build from the exact v0.54 source, then change only the post-model-write
# receipt/restore state machine. The proven DOM semantic resolver and
# HTMLElement.click() activation path remain unchanged.
runpy.run_path("ci/generate_chatgpt_webview_v56_model_dom_click_roundtrip.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
old=PKG/"OrchestratorPaidCurrentUiModelDomClickRoundtripV56Activity.java"
new=PKG/"OrchestratorPaidCurrentUiModelPostwriteReceiptV57Activity.java"
s=old.read_text()

# Identity only.
s=s.replace("public class OrchestratorPaidCurrentUiModelDomClickRoundtripV56Activity",
            "public class OrchestratorPaidCurrentUiModelPostwriteReceiptV57Activity")
s=s.replace("cp-v56-paid-current-ui-model-dom-click-roundtrip-v1",
            "cp-v57-paid-current-ui-model-postwrite-receipt-v1")
s=s.replace("paid-current-ui-model-dom-click-roundtrip",
            "paid-current-ui-model-postwrite-receipt")
s=s.replace("TelemetryConfigV56","TelemetryConfigV57")
s=s.replace('testId47 = "cp54-" + UUID.randomUUID();',
            'testId47 = "cp55-" + UUID.randomUUID();')
s=s.replace("AUTONOMOUS_CURRENT_UI_MODEL_DOM_ROUNDTRIP",
            "AUTONOMOUS_CURRENT_UI_MODEL_POSTWRITE_RECEIPT")
s=s.replace("RUN AUTONOMOUS MODEL CLICK ROUNDTRIP",
            "RUN AUTONOMOUS MODEL POSTWRITE RECEIPT")
s=s.replace("v0.53 autonomous model DOM-bridge roundtrip ready",
            "v0.55 autonomous model post-write receipt roundtrip ready")

# After a model option write, never assume the closed Medium composer has already
# returned. Poll the live state and independently reacquire the model menu.
old_target_delay='h47.postDelayed(()->prepareModelBridge55(MODEL_PURPOSE_RESTORE54),700L);'
old_restore_delay='h47.postDelayed(()->prepareModelBridge55(MODEL_PURPOSE_VERIFY54),700L);'
assert s.count(old_target_delay)==1
assert s.count(old_restore_delay)==1
s=s.replace(old_target_delay,
            'h47.postDelayed(()->preparePostWriteModelReceipt57(MODEL_PURPOSE_RESTORE54,0),700L);')
s=s.replace(old_restore_delay,
            'h47.postDelayed(()->preparePostWriteModelReceipt57(MODEL_PURPOSE_VERIFY54,0),700L);')

# Replace only the exact-menu decision method and prepend the new bounded
# post-write reacquisition helper. No model option is replayed by this helper.
pat=r'    private void onExactModelMenu54\(int purpose,JSONObject o\) \{.*?\n    \}\n\n    private void claimSelectTargetModel54\(\) \{'
m=re.search(pat,s,re.S)
assert m, "onExactModelMenu54 anchor missing"
replacement=r'''    private void preparePostWriteModelReceipt57(final int purpose,final int attempt) {
        if(!running47)return;
        if(purpose!=MODEL_PURPOSE_RESTORE54&&purpose!=MODEL_PURPOSE_VERIFY54){
            failModelBridge54(purpose,"MODEL_POSTWRITE_RECEIPT_BAD_PURPOSE"); return;
        }
        JSONObject menu=ControlPlaneAccessibilityServiceV50.captureModelMenu("-");
        if(exactModelMenu54(menu)){onExactModelMenu54(purpose,menu);return;}
        setStatus47(purpose==MODEL_PURPOSE_RESTORE54
                ? "Waiting for independent GPT-5.6 SOL receipt before restore..."
                : "Waiting for independent Latest restore receipt...");
        eval47(scanDomModelBridgeJs55("-"),bridge->{
            if(!running47)return;
            JSONObject bst=baseState47();
            copy47(bst,bridge,"success","complete","owner_count","controlled_root_count","overlay_root_count","root_count","candidate_total","bridge_candidate_count","bridge_candidate_hash","bridge_candidate_class","bridge_candidate_surface","bridge_candidate_role","bridge_candidate_label_hash","candidate_set_hash");
            put47(bst,"postwrite_attempt",attempt); put47(bst,"postwrite_purpose",purpose);
            boolean bridgeReady=bridge.optBoolean("success",false)&&bridge.optBoolean("complete",false)
                    &&bridge.optInt("bridge_candidate_count",0)==1&&!"-".equals(bridge.optString("bridge_candidate_hash","-"))
                    &&("MODEL_NAV".equals(bridge.optString("bridge_candidate_class",""))||"MODEL_TRIGGER".equals(bridge.optString("bridge_candidate_class","")));
            if(bridgeReady){
                phase47("MODEL_POSTWRITE_SURFACE","PASS_DIRECT_LIVE_DOM_MODEL_BRIDGE",bst);
                claimDispatchDomModelBridge55(purpose,0,bridge.optString("bridge_candidate_hash","-"),bridge.optString("bridge_candidate_class","NONE"),"-");
                return;
            }
            eval47(scanClosedComposerJs47(),closed->{
                if(!running47)return;
                JSONObject cst=baseState47();
                copy47(cst,closed,"success","complete","effort_control_count","effort_semantic","effort_control_hash","effort_has_popup","effort_expanded_true","composer_control_count","candidate_set_hash");
                put47(cst,"postwrite_attempt",attempt); put47(cst,"postwrite_purpose",purpose);
                boolean mediumReady=closed.optBoolean("success",false)&&closed.optBoolean("complete",false)
                        &&closed.optInt("effort_control_count",-1)==1&&"MEDIUM".equals(closed.optString("effort_semantic",""))
                        &&closed.optBoolean("effort_has_popup",false)&&!closed.optBoolean("effort_expanded_true",true)
                        &&!"-".equals(closed.optString("effort_control_hash","-"));
                if(mediumReady){
                    phase47("MODEL_POSTWRITE_SURFACE","PASS_CLOSED_MEDIUM_FALLBACK_MODEL_BRIDGE",cst);
                    prepareModelBridge55(purpose); return;
                }
                if(attempt<20){
                    if(attempt==0||attempt==8||attempt==16)
                        phase47("MODEL_POSTWRITE_SURFACE","WAIT_READ_ONLY_FOR_STABLE_MODEL_RECEIPT_SURFACE",cst);
                    h47.postDelayed(()->preparePostWriteModelReceipt57(purpose,attempt+1),250L);
                    return;
                }
                phase47("MODEL_POSTWRITE_SURFACE","MODEL_POSTWRITE_RECEIPT_SURFACE_UNRESOLVED_NO_REPLAY",cst);
                failModelBridge54(purpose,"MODEL_POSTWRITE_RECEIPT_SURFACE_UNRESOLVED_NO_REPLAY");
            });
        });
    }

    private void onExactModelMenu54(int purpose,JSONObject o) {
        JSONObject st=baseState47(); copy47(st,o,"success","complete","visited_count","web_node_count","group_count","option_count","selected_count","group_hash","current_option_hash","target_option_hash","current_semantic","target_semantic","exact_expected_set","selection_basis","option_set_hash");
        if(!exactModelMenu54(o)){failModelBridge54(purpose,"EXACT_MODEL_MENU_CONTRACT_MISMATCH");return;}
        if(purpose==MODEL_PURPOSE_TARGET54){
            modelGroupHash49=o.optString("group_hash","-"); modelOriginalOptionHash49=o.optString("current_option_hash","-"); modelTargetOptionHash49=o.optString("target_option_hash","-");
            modelOriginalSemantic50=o.optString("current_semantic","NONE"); modelTargetSemantic50=o.optString("target_semantic","NONE");
            boolean startSafe="LATEST".equals(modelOriginalSemantic50)&&"GPT56_SOL".equals(modelTargetSemantic50)&&modelOptionClicks49==0;
            phase47("MODEL_START_STATE_GATE",startSafe?"PASS_START_LATEST_TARGET_GPT56_SOL":"MODEL_START_NOT_CONFIRMED_LATEST_ZERO_OPTION_WRITE",st);
            if(!startSafe){
                claimStatus47="UNCERTAIN_MODEL_START_NOT_LATEST";
                prefs47.edit().putString("claim_status",claimStatus47).commit();
                finish47("MODEL_START_NOT_CONFIRMED_LATEST_ZERO_OPTION_WRITE"); return;
            }
            boolean plan=!"-".equals(modelTargetOptionHash49)&&!"NONE".equals(modelOriginalSemantic50)&&!"NONE".equals(modelTargetSemantic50)
                    &&!modelOriginalOptionHash49.equals(modelTargetOptionHash49);
            phase47("MODEL_MENU_PLAN",plan?"PASS_EXACT_THREE_MODEL_TARGET_PLAN":"MODEL_TARGET_PLAN_INVALID_ZERO_OPTION_WRITE",st);
            if(!plan){failModelBridge54(purpose,"MODEL_TARGET_PLAN_INVALID_ZERO_OPTION_WRITE");return;}
            claimSelectTargetModel54(); return;
        }
        boolean groupOk=modelGroupHash49.equals(o.optString("group_hash",""));
        String current=o.optString("current_option_hash","-"); String sem=o.optString("current_semantic","NONE");
        if(purpose==MODEL_PURPOSE_RESTORE54){
            modelTargetReceipt49=groupOk&&modelTargetOptionHash49.equals(current)&&modelTargetSemantic50.equals(sem);
            phase47("MODEL_TARGET_SELECTED_RECEIPT",modelTargetReceipt49?"PASS_MODEL_TARGET_SELECTED_ACCESSIBILITY":"MODEL_TARGET_SELECTION_RECEIPT_INCOMPLETE_NO_RESTORE_DISPATCH",st);
            if(!groupOk){failModelBridge54(purpose,"MODEL_RESTORE_GROUP_DRIFT_MANUAL_MODEL_RESTORE_REQUIRED");return;}
            if(!modelTargetReceipt49||modelOptionClicks49!=1){
                failModelBridge54(purpose,"MODEL_TARGET_SELECTION_RECEIPT_INCOMPLETE_NO_RESTORE_DISPATCH");return;
            }
            claimRestoreOriginalModel54(); return;
        }
        modelRestoreReceipt49=groupOk&&modelOriginalOptionHash49.equals(current)&&modelOriginalSemantic50.equals(sem);
        modelGatePass49=modelTargetReceipt49&&modelRestoreReceipt49&&modelOptionClicks49==2;
        phase47("MODEL_ORIGINAL_SELECTED_RECEIPT",modelRestoreReceipt49?"PASS_MODEL_ORIGINAL_RESTORED_ACCESSIBILITY":"MODEL_ORIGINAL_RESTORE_RECEIPT_INCOMPLETE",st);
        if(!modelRestoreReceipt49){claimStatus47="UNCERTAIN_MODEL_RESTORE_REQUIRED";prefs47.edit().putString("claim_status",claimStatus47).commit();finish47("MODEL_ORIGINAL_RESTORE_RECEIPT_INCOMPLETE_MANUAL_MODEL_CHECK_REQUIRED");return;}
        claimStatus47="MODEL_RESTORED_CONFIRMED"; prefs47.edit().putString("claim_status",claimStatus47).commit();
        finish47(modelGatePass49&&effortGatePass49?"PASS_AUTONOMOUS_MODEL_POSTWRITE_RECEIPT_ROUNDTRIP_RESTORED_MEDIUM_UNCHANGED":"PARTIAL_MODEL_POSTWRITE_RECEIPT_INCOMPLETE_MEDIUM_UNCHANGED");
    }

    private void claimSelectTargetModel54() {'''
s=s[:m.start()]+replacement+s[m.end():]

# Defense in depth: neither option write method may be entered in the wrong
# transaction state.
needle='    private void claimSelectTargetModel54() {\n'
assert s.count(needle)==1
s=s.replace(needle,needle+'        if(modelOptionClicks49!=0){failModelBridge54(MODEL_PURPOSE_TARGET54,"MODEL_TARGET_REPLAY_BLOCKED");return;}\n')
needle='    private void claimRestoreOriginalModel54() {\n'
assert s.count(needle)==1
s=s.replace(needle,needle+'        if(!modelTargetReceipt49||modelOptionClicks49!=1){failModelBridge54(MODEL_PURPOSE_RESTORE54,"MODEL_RESTORE_NOT_ALLOWED_WITHOUT_TARGET_RECEIPT");return;}\n')

# Safety/lineage contracts.
assert "clickDomModelBridgeJs56" in s
assert "ELEMENT_CLICK" in s
assert "scanDomModelBridgeJs55" in s
assert "preparePostWriteModelReceipt57" in s
assert "MODEL_START_NOT_CONFIRMED_LATEST_ZERO_OPTION_WRITE" in s
assert "MODEL_TARGET_SELECTION_RECEIPT_INCOMPLETE_NO_RESTORE_DISPATCH" in s
assert "MODEL_RESTORE_NOT_ALLOWED_WITHOUT_TARGET_RECEIPT" in s
assert old_target_delay not in s
assert old_restore_delay not in s
assert "startDynamicEffortProof50();" not in s
new.write_text(s)

# Fresh telemetry config.
cfg56=(PKG/"TelemetryConfigV56.java").read_text()
(PKG/"TelemetryConfigV57.java").write_text(cfg56.replace("TelemetryConfigV56","TelemetryConfigV57"))

# In-place upgrade identity.
g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+57\b","versionCode 58",gs)
gs=gs.replace("0.54-stable-diag-model-dom-click-roundtrip",
              "0.55-stable-diag-model-postwrite-receipt")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorPaidCurrentUiModelDomClickRoundtripV56Activity",
              "OrchestratorPaidCurrentUiModelPostwriteReceiptV57Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
for v in (52,53,54,55,56,57):
    assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

print("generated v0.55 model post-write receipt roundtrip; proven DOM click bridge unchanged; target receipt hard-gates restore; accessibility component V51")
