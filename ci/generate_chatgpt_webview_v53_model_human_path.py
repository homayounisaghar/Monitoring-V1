#!/usr/bin/env python3
from pathlib import Path
import runpy,re,shutil

runpy.run_path("ci/generate_chatgpt_webview_v52_effort_popup_human_model_bridge.py", run_name="__main__")
ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
SRC=Path("ci/v53_model_path")

shutil.copyfile(SRC/"OrchestratorPaidEffortPopupHumanModelPathV53Activity.java", PKG/"OrchestratorPaidEffortPopupHumanModelPathV53Activity.java")

cfg52=(PKG/"TelemetryConfigV52.java").read_text()
(PKG/"TelemetryConfigV53.java").write_text(cfg52.replace("TelemetryConfigV52","TelemetryConfigV53"))

g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+53\b","versionCode 54",gs)
gs=gs.replace("0.50-stable-diag-effort-popup-human-model-bridge","0.51-stable-diag-effort-popup-human-model-path")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorPaidEffortPopupHumanModelBridgeV52Activity","OrchestratorPaidEffortPopupHumanModelPathV53Activity")
# Preserve the already-authorized Accessibility service component identity.
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
assert "ControlPlaneAccessibilityServiceV52" not in ms
assert "ControlPlaneAccessibilityServiceV53" not in ms
m.write_text(ms)
print("generated v0.51 multi-tap human model path observer; accessibility component remains V51")
