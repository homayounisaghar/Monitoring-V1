#!/usr/bin/env python3
from pathlib import Path
import base64,lzma,runpy,re

runpy.run_path("ci/generate_chatgpt_webview_v54_autonomous_effort_model_roundtrip.py", run_name="__main__")
ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
B=Path("ci/v55_dom_selfupdate")

act="".join((B/f"act_{i:02d}.b64").read_text().strip() for i in range(1,7))
(PKG/"OrchestratorPaidModelDomBridgeSelfUpdateV55Activity.java").write_text(
    lzma.decompress(base64.b64decode(act)).decode("utf-8"))
(PKG/"SelfUpdateStatusReceiverV55.java").write_text(
    lzma.decompress(base64.b64decode((B/"receiver.b64").read_text().strip())).decode("utf-8"))

cfg54=(PKG/"TelemetryConfigV54.java").read_text()
(PKG/"TelemetryConfigV55.java").write_text(cfg54.replace("TelemetryConfigV54","TelemetryConfigV55"))

g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+55\b","versionCode 56",gs)
gs=gs.replace("0.52-stable-diag-autonomous-effort-model-roundtrip",
              "0.53-stable-diag-dom-model-self-update")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text()
ms=ms.replace("OrchestratorPaidCurrentUiEffortModelBridgeRoundtripV54Activity",
              "OrchestratorPaidModelDomBridgeSelfUpdateV55Activity")
anchor='    <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />'
if 'android.permission.REQUEST_INSTALL_PACKAGES' not in ms:
    ms=ms.replace(anchor,anchor+'\n    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />\n    <uses-permission android:name="android.permission.UPDATE_PACKAGES_WITHOUT_USER_ACTION" />')
if 'SelfUpdateStatusReceiverV55' not in ms:
    ms=ms.replace('    </application>','        <receiver android:name=".SelfUpdateStatusReceiverV55" android:exported="false" />\n    </application>')
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
assert "ControlPlaneAccessibilityServiceV52" not in ms
assert "ControlPlaneAccessibilityServiceV53" not in ms
assert "ControlPlaneAccessibilityServiceV54" not in ms
assert "ControlPlaneAccessibilityServiceV55" not in ms
m.write_text(ms)
print("generated v0.53 DOM model bridge + self updater; accessibility component remains V51")
