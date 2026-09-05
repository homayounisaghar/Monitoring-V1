#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path('runtime_probes/chatgpt-webview-stable-probe')
PKG = ROOT / 'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
src42 = PKG / 'OrchestratorPaidModelEffortPointerCensusV42Activity.java'
src43 = PKG / 'OrchestratorPaidModelEffortNestedCensusV43Activity.java'
man = ROOT / 'app/src/main/AndroidManifest.xml'
gradle = ROOT / 'app/build.gradle'

s = src42.read_text()
s = s.replace('OrchestratorPaidModelEffortPointerCensusV42Activity', 'OrchestratorPaidModelEffortNestedCensusV43Activity')
s = s.replace('TelemetryConfigV42', 'TelemetryConfigV43')
s = re.sub(r'42', '43', s)
s = s.replace('cp-v43-paid-model-effort-pointer-census-v1', 'cp-v43-paid-model-effort-nested-surface-census-v1')
s = s.replace('paid-model-effort-semantic-pointer-popup-census', 'paid-model-effort-open-popup-nested-structure-census')
s = s.replace('RUN SEMANTIC POINTER POPUP CENSUS', 'RUN NESTED EFFORT SURFACE CENSUS')
s = s.replace('POINTER CENSUS RUNNING...', 'NESTED CENSUS RUNNING...')
s = s.replace('Popup snapshot ', 'Nested snapshot ')
s = s.replace('POPUP_SURFACE_SNAPSHOT', 'NESTED_SURFACE_SNAPSHOT')
s = s.replace('PASS_SEMANTIC_POINTER_POPUP_CENSUS_CAPTURED', 'PASS_NESTED_EFFORT_STRUCTURE_CENSUS_CAPTURED')
s = s.replace('PARTIAL_SEMANTIC_POINTER_POPUP_CENSUS_CAPTURED', 'PARTIAL_NESTED_EFFORT_STRUCTURE_CENSUS_CAPTURED')
s = s.replace('SEMANTIC_POINTER_POPUP_UNCERTAIN_NO_REPLAY', 'NESTED_EFFORT_STRUCTURE_UNCERTAIN_NO_REPLAY')

m = re.search(r'    private String scanOpenSurfaceJs43\(.*?\n    }\n\n    private void eval43', s, re.S)
assert m, 'scanOpenSurfaceJs43 not found'
b = m.group(0)
b = b.replace('MAXN=12000,MAXMS=260,MAXC=48', 'MAXN=20000,MAXMS=320,MAXC=64')
b = b.replace(
    "const sel='button,[role=\\\"button\\\"],[role=\\\"menuitem\\\"],[role=\\\"menuitemradio\\\"],[role=\\\"option\\\"],[role=\\\"radio\\\"],[data-radix-collection-item],[aria-checked],[aria-selected]';",
    "const sel='button,[role],[aria-haspopup],[aria-expanded],[aria-controls],[aria-owns],[data-state],[data-slot],[data-radix-collection-item],[aria-checked],[aria-selected]';"
)
b = b.replace('portalish=0;const out=[]', 'portalish=0,hiddenSem=0,relationRefs=0;const out=[]')
b = b.replace('if(!V(e))continue;const txt=', 'const vis=V(e);const txt=')
b = b.replace(
    "const sem=sl?'LIGHT':sm?'MEDIUM':sh?'HEAVY':sa?'AUTO':st?'THINKING':'INSTANT';",
    "const sem=sl?'LIGHT':sm?'MEDIUM':sh?'HEAVY':sa?'AUTO':st?'THINKING':'INSTANT';if(!vis)hiddenSem++;"
)
b = b.replace(
    "const afp=H(chain.join('>')),q={semantic:sem,",
    "const controls=N(e.getAttribute('aria-controls')),owns=N(e.getAttribute('aria-owns'));if(controls!==''||owns!=='')relationRefs++;const afp=H(chain.join('>')),q={semantic:sem,visible:vis,has_controls:controls!=='',has_owns:owns!=='',controls_hash:controls?H(controls):'-',owns_hash:owns?H(owns):'-',"
)
b = b.replace('selected_count:sc,trigger_found:', 'selected_count:sc,hidden_semantic_count:hiddenSem,relation_ref_node_count:relationRefs,trigger_found:')
s = s[:m.start()] + b + s[m.end():]

old = 'copy43(st, o, "success","complete","snapshot_index","visited_nodes","semantic_candidate_count","light_count","medium_count","heavy_count","auto_count","thinking_count","instant_count","selected_count","trigger_found","trigger_expanded_true","trigger_data_state_open","popup_role_candidate_count","portalish_candidate_count","popup_evidence","candidate_set_hash","ancestor_set_hash");'
new = 'copy43(st, o, "success","complete","snapshot_index","visited_nodes","semantic_candidate_count","light_count","medium_count","heavy_count","auto_count","thinking_count","instant_count","selected_count","hidden_semantic_count","relation_ref_node_count","trigger_found","trigger_expanded_true","trigger_data_state_open","popup_role_candidate_count","portalish_candidate_count","popup_evidence","candidate_set_hash","ancestor_set_hash");'
assert old in s
s = s.replace(old, new)
s = s.replace('put43(st,"ui_dispatches",uiDispatches43);', 'put43(st,"ui_dispatches",uiDispatches43);\n        put43(st,"secondary_ui_dispatches",0);')
src43.write_text(s)

cfg = PKG / 'TelemetryConfigV43.java'
cfg.write_text('''package com.homayounisaghar.chatgptwebviewprobe;\nfinal class TelemetryConfigV43 {\n    static final String WEBHOOK_URL="https://webhook.site/__V43_UNCONFIGURED__";\n    static final String SOURCE_REF="__SOURCE_REF__";\n    static final String COLLECTOR_ID="__COLLECTOR_ID__";\n    static final boolean CONFIGURED=false;\n    private TelemetryConfigV43(){}\n    static boolean isConfigured(){return CONFIGURED&&WEBHOOK_URL.startsWith("https://webhook.site/")&&!WEBHOOK_URL.contains("__V43_UNCONFIGURED__");}\n}\n''')

x = man.read_text()
old_activity = '''        <activity android:name=".OrchestratorPaidModelEffortPointerCensusV42Activity" android:exported="true">\n            <intent-filter>\n                <action android:name="android.intent.action.MAIN" />\n                <category android:name="android.intent.category.LAUNCHER" />\n            </intent-filter>\n        </activity>'''
new_activity = '''        <activity android:name=".OrchestratorPaidModelEffortPointerCensusV42Activity" android:exported="false" />\n        <activity android:name=".OrchestratorPaidModelEffortNestedCensusV43Activity" android:exported="true">\n            <intent-filter>\n                <action android:name="android.intent.action.MAIN" />\n                <category android:name="android.intent.category.LAUNCHER" />\n            </intent-filter>\n        </activity>'''
assert old_activity in x
man.write_text(x.replace(old_activity, new_activity))

g = gradle.read_text()
g = g.replace("applicationId 'com.homayounisaghar.chatgptwebviewprobe'", "applicationId 'com.homayounisaghar.chatgptwebviewprobe.v43diag'")
g = re.sub(r'versionCode\s+\d+', 'versionCode 44', g)
g = re.sub(r"versionName\s+'[^']+'", "versionName '0.41-sidecar-paid-model-effort-nested-surface-census'", g)
gradle.write_text(g)

print('V43_GENERATED sidecar=com.homayounisaghar.chatgptwebviewprobe.v43diag versionCode=44')
