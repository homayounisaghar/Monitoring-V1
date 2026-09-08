#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.88: instrumentation-only successor to v0.87.
# Preserve the proven v0.87 Resource post-effect behavior exactly; advance app identity
# and telemetry config class so the build workflow can inject a fresh collector.
runpy.run_path("ci/generate_chatgpt_webview_v89_resource_posteffect_repair.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorResourceToolsV89Activity.java"
ACT=PKG/"OrchestratorResourceToolsV90Activity.java"
s=OLD.read_text()

# Identity/instrumentation rollover only. Keep all V88/V89 Resource protocol helpers,
# exact-one effects, semantic guards, continuation semantics and receipts unchanged.
s=s.replace("OrchestratorResourceToolsV89Activity","OrchestratorResourceToolsV90Activity")
s=s.replace("TelemetryConfigV89","TelemetryConfigV90")
s=s.replace('SCHEMA="cp-v89-resource-posteffect-repair-v1"','SCHEMA="cp-v90-resource-posteffect-telemetry-repair-v1"')
s=s.replace('SCENARIO="resource-posteffect-provenance-continuation"','SCENARIO="resource-posteffect-provenance-continuation-telemetry-repair"')
s=s.replace('testId="cp87-"+UUID.randomUUID();','testId="cp88-"+UUID.randomUUID();')
s=s.replace('v0.87 Resource post-effect repair ready.','v0.88 Resource post-effect telemetry repair ready.')
# Namespace only the persisted continuation sub-claim markers so the new acceptance run
# cannot inherit a v0.87 continuation-attempt marker. Runtime behavior remains identical.
s=s.replace('resource_v89_continuation_','resource_v90_continuation_')
s=s.replace('resource-v89-cont-','resource-v90-cont-')

ACT.write_text(s);OLD.unlink()
oldcfg=PKG/"TelemetryConfigV89.java";newcfg=PKG/"TelemetryConfigV90.java"
assert oldcfg.exists()
cfg=oldcfg.read_text().replace("TelemetryConfigV89","TelemetryConfigV90")
newcfg.write_text(cfg);oldcfg.unlink()

man=ROOT/"app/src/main/AndroidManifest.xml"
ms=man.read_text();assert ms.count("OrchestratorResourceToolsV89Activity")==1
man.write_text(ms.replace("OrchestratorResourceToolsV89Activity","OrchestratorResourceToolsV90Activity",1))

grad=ROOT/"app/build.gradle"
gs=grad.read_text();assert re.search(r"versionCode\s+90\b",gs)
gs=re.sub(r"versionCode\s+90\b","versionCode 91",gs,1)
assert "0.87-stable-diag-resource-posteffect-repair" in gs
gs=gs.replace("0.87-stable-diag-resource-posteffect-repair","0.88-stable-diag-resource-posteffect-telemetry-repair",1)
grad.write_text(gs)

# Generator-time invariants: this version must be behaviorally identical to v0.87
# except identity, telemetry configuration and fresh continuation preference namespace.
out=ACT.read_text()
required=[
    'SCHEMA="cp-v90-resource-posteffect-telemetry-repair-v1"',
    'SCENARIO="resource-posteffect-provenance-continuation-telemetry-repair"',
    'TelemetryConfigV90',
    'CP_RESOURCE_CERT_V88','CP_RESOURCE_EFFECT_V88','createWebMessageChannel','window.__cpEventPort',
    'RESOURCE_TOOLS_MISDISPATCH_GUARD_V89_JS','trigger_certified','trigger_expanded','surface_owned',
    'RESOURCE_POST_EFFECT_GENERIC_UI_NOT_TOOLS_AUTHORITY','RESOURCE_ACTION_MISDISPATCHED_NONRESOURCE_UI',
    'RESOURCE_CONTINUATION_CERT_V89_JS','RESOURCE_CONTINUATION_EFFECT_V89_TEMPLATE',
    'RESOURCE_CONTINUATION_SUBCLAIM_COMMITTED','EFFECT_ATTEMPTED_NO_REPLAY',
    'RESOURCE_INTERSTITIAL_CONTINUATION_DISPATCHED_WAITING_INDEPENDENT_RECEIPT',
    'android.content.Intent.ACTION_VIEW','PASS_RESOURCE_DOWNLOAD_CALLBACK_RECEIPT',
    'armResourceReceiptDeadlineV88(resourceV82Actuator)',
    'raw_text_remote",false','raw_url_remote",false'
]
for x in required: assert x in out,x
m=re.search(r'    private void driveResourcePendingOnEventV79\([^\n]*\)\{.*?\n    \}\n\n',out,re.S);assert m
assert 'toolsMenuCensusV79Js()' not in m.group(0)
assert 'resourceToolsMisdispatchGuardV89Js()' in m.group(0)
assert all(x in m.group(0) for x in ['trigger_certified','trigger_expanded','surface_owned'])
em=re.search(r'private static final String RESOURCE_CONTINUATION_EFFECT_V89_TEMPLATE=.*?;\n',out,re.S)
assert em and em.group(0).count('.click();')==1
assert out.count('resourceV89ContinuationEffectAttempted=true;')==1
assert out.count('dispatchTouchEvent(')==2,out.count('dispatchTouchEvent(')
for bad in ['elementFromPoint','document.evaluate','XPathResult','getCookie(','CookieManager','addJavascriptInterface','Thread.sleep','ScheduledExecutorService','TimerTask']:
    assert bad not in out,bad
assert newcfg.exists() and 'CONFIGURED=false' in newcfg.read_text()
print('Generated v0.88 Resource post-effect telemetry repair')
