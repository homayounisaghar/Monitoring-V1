#!/usr/bin/env python3
from pathlib import Path
import base64,lzma,runpy,re

runpy.run_path("ci/generate_chatgpt_webview_v51_model_human_open_discovery.py", run_name="__main__")
ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
B=Path("ci/v52_model_bridge")
blob=(B/"act_01.b64").read_text().strip()+(B/"act_02.b64").read_text().strip()
(PKG/"OrchestratorPaidEffortPopupHumanModelBridgeV52Activity.java").write_text(lzma.decompress(base64.b64decode(blob)).decode("utf-8"))

cfg51=(PKG/"TelemetryConfigV51.java").read_text()
(PKG/"TelemetryConfigV52.java").write_text(cfg51.replace("TelemetryConfigV51","TelemetryConfigV52"))

g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+52\b","versionCode 53",gs)
gs=gs.replace("0.49-stable-diag-model-human-open-discovery","0.50-stable-diag-effort-popup-human-model-bridge")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorPaidModelHumanOpenDiscoveryV51Activity","OrchestratorPaidEffortPopupHumanModelBridgeV52Activity")
# IMPORTANT: preserve the already-authorized accessibility component identity.
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
assert "ControlPlaneAccessibilityServiceV52" not in ms
m.write_text(ms)
print("generated v0.50 effort-popup human model bridge; accessibility component remains V51")
# build trigger after workflow registration
