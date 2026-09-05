#!/usr/bin/env python3
from pathlib import Path
import base64,lzma,runpy,re,shutil

runpy.run_path("ci/generate_chatgpt_webview_v49_accessibility_model_roundtrip.py", run_name="__main__")
ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
RESXML=ROOT/"app/src/main/res/xml"
B=Path("ci/v50_current_ui_blobs")
act="".join((B/f"act_{i:02d}.b64").read_text().strip() for i in range(1,6))
svc="".join((B/f"svc_{i:02d}.b64").read_text().strip() for i in range(1,3))
(PKG/"OrchestratorPaidCurrentUiControlRoundtripV50Activity.java").write_text(lzma.decompress(base64.b64decode(act)).decode("utf-8"))
svc_path=PKG/"ControlPlaneAccessibilityServiceV50.java"
svc_path.write_text(lzma.decompress(base64.b64decode(svc)).decode("utf-8"))
# Keep source compatible with the project's Java 8 compile target. The blob's
# regex line contained source-level \s escapes; normalized accessibility text
# already collapses whitespace, so a literal phrase check is equivalent here.
svc_source=svc_path.read_text()
svc_source,n=re.subn(r'^\s*boolean extra = s\.matches\(.*\);$', '        boolean extra = s.contains("extra high");', svc_source, count=1, flags=re.M)
assert n == 1, "expected Extra High semantic line not found"
svc_path.write_text(svc_source)
shutil.copyfile(RESXML/"cp_accessibility_service_v49.xml", RESXML/"cp_accessibility_service_v50.xml")

cfg49=(PKG/"TelemetryConfigV49.java").read_text()
(PKG/"TelemetryConfigV50.java").write_text(cfg49.replace("TelemetryConfigV49","TelemetryConfigV50"))

g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+50\b","versionCode 51",gs)
gs=gs.replace("0.47-stable-diag-accessibility-light-model-roundtrip","0.48-stable-diag-current-ui-effort-model-roundtrip")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorPaidEffortAccessibilityModelRoundtripV49Activity","OrchestratorPaidCurrentUiControlRoundtripV50Activity")
ms=ms.replace("ControlPlaneAccessibilityServiceV49","ControlPlaneAccessibilityServiceV50")
ms=ms.replace("@xml/cp_accessibility_service_v49","@xml/cp_accessibility_service_v50")
m.write_text(ms)
print("generated v0.48 dynamic current-UI effort/model roundtrip")
