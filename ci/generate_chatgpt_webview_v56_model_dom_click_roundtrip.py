#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# Reuse the exact v0.53b semantic resolver and closed effort-write path.
runpy.run_path("ci/generate_chatgpt_webview_v55_model_dom_roundtrip.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
old=PKG/"OrchestratorPaidCurrentUiModelDomRoundtripV55Activity.java"
new=PKG/"OrchestratorPaidCurrentUiModelDomClickRoundtripV56Activity.java"
s=old.read_text()

# Identity / telemetry version.
s=s.replace("public class OrchestratorPaidCurrentUiModelDomRoundtripV55Activity",
            "public class OrchestratorPaidCurrentUiModelDomClickRoundtripV56Activity")
s=s.replace("cp-v55-paid-current-ui-model-dom-roundtrip-v1",
            "cp-v56-paid-current-ui-model-dom-click-roundtrip-v1")
s=s.replace("paid-current-ui-model-dom-roundtrip",
            "paid-current-ui-model-dom-click-roundtrip")
s=s.replace("TelemetryConfigV55","TelemetryConfigV56")
s=s.replace("RUN AUTONOMOUS MODEL ROUNDTRIP","RUN AUTONOMOUS MODEL CLICK ROUNDTRIP")

# v0.53b proved the exact semantic MODEL_NAV menuitem but pointerdown-only did not activate it.
# Keep the resolver unchanged and change only the activation event class.
s=s.replace("pointerDownDomModelBridgeJs55","clickDomModelBridgeJs56")
s=s.replace("DOM_POINTERDOWN_UNIQUE_MODEL_BRIDGE","DOM_CLICK_UNIQUE_MODEL_BRIDGE")
s=s.replace("CLAIMED_BEFORE_UNIQUE_DOM_MODEL_BRIDGE_POINTERDOWN",
            "CLAIMED_BEFORE_UNIQUE_DOM_MODEL_BRIDGE_CLICK")

old_copy='copy47(st,r,"success","candidate_count","matches","dispatched","event_class","default_prevented","matched_hash","matched_class","matched_surface","matched_role")'
new_copy='copy47(st,r,"success","candidate_count","matches","dispatched","click_observed","event_class","matched_hash","matched_class","matched_surface","matched_role")'
assert s.count(old_copy)==1
s=s.replace(old_copy,new_copy)

old_sent='boolean sent=r.optBoolean("success",false)&&r.optInt("candidate_count",0)==1&&r.optInt("matches",0)==1&&r.optBoolean("dispatched",false);'
new_sent='boolean sent=r.optBoolean("success",false)&&r.optInt("candidate_count",0)==1&&r.optInt("matches",0)==1&&r.optBoolean("dispatched",false)&&r.optBoolean("click_observed",false);'
assert s.count(old_sent)==1
s=s.replace(old_sent,new_sent)
s=s.replace('DISPATCHED_UNIQUE_DOM_MODEL_BRIDGE','DISPATCHED_UNIQUE_DOM_MODEL_BRIDGE_CLICK')
s=s.replace('MODEL_DOM_BRIDGE_NOT_DISPATCHED','MODEL_DOM_BRIDGE_CLICK_NOT_DISPATCHED')

old_tail="try{e.focus({preventScroll:true});}catch(_){}let ev,kind;if(typeof PointerEvent==='function'){ev=new PointerEvent('pointerdown',{bubbles:true,cancelable:true,composed:true,pointerId:1,pointerType:'mouse',isPrimary:true,button:0,buttons:1});kind='POINTERDOWN';}else{ev=new MouseEvent('mousedown',{bubbles:true,cancelable:true,composed:true,view:window,button:0,buttons:1});kind='MOUSEDOWN_FALLBACK';}const accepted=e.dispatchEvent(ev);return JSON.stringify({success:true,candidate_count:1,matches:1,dispatched:true,event_class:kind,default_prevented:!accepted,matched_hash:x.h,matched_class:x.k,matched_surface:x.s,matched_role:x.role});"
new_tail="try{e.focus({preventScroll:true});}catch(_){}let observed=0;const watch=()=>{observed++;};try{e.addEventListener('click',watch,{capture:true,once:true});}catch(_){}let method='NONE',ok=false;try{if(typeof e.click==='function'){e.click();method='ELEMENT_CLICK';ok=true;}else{const ev=new MouseEvent('click',{bubbles:true,cancelable:true,composed:true,view:window,button:0,buttons:0});e.dispatchEvent(ev);method='MOUSE_CLICK_FALLBACK';ok=true;}}catch(_){ok=false;}return JSON.stringify({success:true,candidate_count:1,matches:1,dispatched:ok,click_observed:observed===1,event_class:method,matched_hash:x.h,matched_class:x.k,matched_surface:x.s,matched_role:x.role});"
assert s.count(old_tail)==1
s=s.replace(old_tail,new_tail)

# Ensure the prior failed activation is absent from the model-bridge method.
assert "DOM_POINTERDOWN_UNIQUE_MODEL_BRIDGE" not in s
assert "CLAIMED_BEFORE_UNIQUE_DOM_MODEL_BRIDGE_POINTERDOWN" not in s
assert "clickDomModelBridgeJs56" in s
assert "ELEMENT_CLICK" in s
assert "click_observed" in s
assert "startDynamicEffortProof50();" not in s
new.write_text(s)

# Fresh telemetry config derived from v0.53b config.
cfg55=(PKG/"TelemetryConfigV55.java").read_text()
(PKG/"TelemetryConfigV56.java").write_text(cfg55.replace("TelemetryConfigV55","TelemetryConfigV56"))

# In-place update identity.
g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+56\b","versionCode 57",gs)
gs=gs.replace("0.53-stable-diag-model-dom-roundtrip",
              "0.54-stable-diag-model-dom-click-roundtrip")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorPaidCurrentUiModelDomRoundtripV55Activity",
              "OrchestratorPaidCurrentUiModelDomClickRoundtripV56Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
for v in (52,53,54,55,56):
    assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

print("generated v0.54 model DOM click roundtrip; semantic bridge resolver unchanged; effort Medium-only guard; accessibility component V51")
