#!/usr/bin/env python3
from pathlib import Path
import base64,lzma,runpy,re

runpy.run_path("ci/generate_chatgpt_webview_v53_model_human_path.py", run_name="__main__")
ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
B=Path("ci/v54_combined")

act="".join((B/f"act_{i:02d}.b64").read_text().strip() for i in range(1,6))
svc="".join((B/f"svc_{i:02d}.b64").read_text().strip() for i in range(1,3))
(PKG/"OrchestratorPaidCurrentUiEffortModelBridgeRoundtripV54Activity.java").write_text(
    lzma.decompress(base64.b64decode(act)).decode("utf-8"))
# V51 is the stable registered component and extends this base implementation.
# Replace only the base implementation; never rename the registered V51 component.
(PKG/"ControlPlaneAccessibilityServiceV50.java").write_text(
    lzma.decompress(base64.b64decode(svc)).decode("utf-8"))

cfg53=(PKG/"TelemetryConfigV53.java").read_text()
(PKG/"TelemetryConfigV54.java").write_text(cfg53.replace("TelemetryConfigV53","TelemetryConfigV54"))

g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+54\b","versionCode 55",gs)
gs=gs.replace("0.51-stable-diag-effort-popup-human-model-path",
              "0.52-stable-diag-autonomous-effort-model-roundtrip")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorPaidEffortPopupHumanModelPathV53Activity",
              "OrchestratorPaidCurrentUiEffortModelBridgeRoundtripV54Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
assert "ControlPlaneAccessibilityServiceV52" not in ms
assert "ControlPlaneAccessibilityServiceV53" not in ms
assert "ControlPlaneAccessibilityServiceV54" not in ms
m.write_text(ms)
print("generated v0.52 autonomous effort+model roundtrip; accessibility component remains V51")
