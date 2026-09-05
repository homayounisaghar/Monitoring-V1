#!/usr/bin/env python3
from pathlib import Path
import base64,lzma,runpy,re

runpy.run_path("ci/generate_chatgpt_webview_v48_transactional_receipt_fixed.py", run_name="__main__")
ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
RESXML=ROOT/"app/src/main/res/xml"
RESXML.mkdir(parents=True,exist_ok=True)
B=Path("ci/v49_accessibility_blobs")
act="".join((B/f"act_{i:02d}.b64").read_text().strip() for i in range(1,4))
svc=(B/"service.b64").read_text().strip()
xml=(B/"service_xml.b64").read_text().strip()
(PKG/"OrchestratorPaidEffortAccessibilityModelRoundtripV49Activity.java").write_text(lzma.decompress(base64.b64decode(act)).decode("utf-8"))
(PKG/"ControlPlaneAccessibilityServiceV49.java").write_text(lzma.decompress(base64.b64decode(svc)).decode("utf-8"))
(RESXML/"cp_accessibility_service_v49.xml").write_text(lzma.decompress(base64.b64decode(xml)).decode("utf-8"))

cfg48=(PKG/"TelemetryConfigV48.java").read_text()
(PKG/"TelemetryConfigV49.java").write_text(cfg48.replace("TelemetryConfigV48","TelemetryConfigV49"))

g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+49\b","versionCode 50",gs)
gs=gs.replace("0.46-stable-diag-transactional-light-receipt","0.47-stable-diag-accessibility-light-model-roundtrip")
g.write_text(gs)

m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text().replace("OrchestratorPaidModelEffortTransactionalReceiptV48Activity","OrchestratorPaidEffortAccessibilityModelRoundtripV49Activity")
service='''        <service android:name=".ControlPlaneAccessibilityServiceV49"\n            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE"\n            android:exported="true"\n            android:label="CP WebView semantic verifier">\n            <intent-filter>\n                <action android:name="android.accessibilityservice.AccessibilityService" />\n            </intent-filter>\n            <meta-data android:name="android.accessibilityservice" android:resource="@xml/cp_accessibility_service_v49" />\n        </service>\n'''
assert service not in ms
ms=ms.replace("    </application>",service+"    </application>")
m.write_text(ms)
print("generated v0.47 accessibility Light proof + guarded model roundtrip")
