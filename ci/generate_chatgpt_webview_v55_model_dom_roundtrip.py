#!/usr/bin/env python3
from pathlib import Path
import base64,lzma,runpy,re

runpy.run_path("ci/generate_chatgpt_webview_v54_autonomous_effort_model_roundtrip.py", run_name="__main__")
ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
B=Path("ci/v55_model_dom_bridge")

act="".join((B/f"act_{i:02d}.b64").read_text().strip() for i in range(1,3))
(PKG/"OrchestratorPaidCurrentUiModelDomRoundtripV55Activity.java").write_text(
    lzma.decompress(base64.b64decode(act)).decode("utf-8"))

cfg54=(PKG/"TelemetryConfigV54.java").read_text()
(PKG/"TelemetryConfigV55.java").write_text(cfg54.replace("TelemetryConfigV54","TelemetryConfigV55"))

g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+55\b","versionCode 56",gs)
gs=gs.replace("0.52-stable-diag-autonomous-effort-model-roundtrip",
              "0.53-stable-diag-model-dom-roundtrip")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorPaidCurrentUiEffortModelBridgeRoundtripV54Activity",
              "OrchestratorPaidCurrentUiModelDomRoundtripV55Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
assert "ControlPlaneAccessibilityServiceV52" not in ms
assert "ControlPlaneAccessibilityServiceV53" not in ms
assert "ControlPlaneAccessibilityServiceV54" not in ms
assert "ControlPlaneAccessibilityServiceV55" not in ms
m.write_text(ms)
print("generated v0.53 autonomous model DOM bridge roundtrip; effort remains Medium-only guard; accessibility component remains V51")
