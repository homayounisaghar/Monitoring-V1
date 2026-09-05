#!/usr/bin/env python3
from pathlib import Path
import runpy,re,shutil

runpy.run_path("ci/generate_chatgpt_webview_v50_current_ui_roundtrip.py", run_name="__main__")
ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
RESXML=ROOT/"app/src/main/res/xml"
SRC=Path("ci/v51_model_observer")

shutil.copyfile(SRC/"OrchestratorPaidModelHumanOpenDiscoveryV51Activity.java", PKG/"OrchestratorPaidModelHumanOpenDiscoveryV51Activity.java")
shutil.copyfile(SRC/"ControlPlaneAccessibilityServiceV51.java", PKG/"ControlPlaneAccessibilityServiceV51.java")
shutil.copyfile(RESXML/"cp_accessibility_service_v50.xml", RESXML/"cp_accessibility_service_v51.xml")

cfg50=(PKG/"TelemetryConfigV50.java").read_text()
(PKG/"TelemetryConfigV51.java").write_text(cfg50.replace("TelemetryConfigV50","TelemetryConfigV51"))

g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+51\b","versionCode 52",gs)
gs=gs.replace("0.48-stable-diag-current-ui-effort-model-roundtrip","0.49-stable-diag-model-human-open-discovery")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorPaidCurrentUiControlRoundtripV50Activity","OrchestratorPaidModelHumanOpenDiscoveryV51Activity")
ms=ms.replace("ControlPlaneAccessibilityServiceV50","ControlPlaneAccessibilityServiceV51")
ms=ms.replace("@xml/cp_accessibility_service_v50","@xml/cp_accessibility_service_v51")
m.write_text(ms)
print("generated v0.49 human-assisted zero-write model trigger/menu discovery")
