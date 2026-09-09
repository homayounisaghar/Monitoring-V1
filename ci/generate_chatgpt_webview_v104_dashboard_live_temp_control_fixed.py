#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v104_dashboard_live_temp_control.py',run_name='__main__')

# Legacy TemporaryChatDomV1 is still compiled in this app and references the
# historical signature constants. Keep those symbols for source compatibility,
# while v0.91.0's active Planner path deliberately does NOT use them for
# classification or actuation.
p=PKG/'TemporaryChatSignaturesV1.java'
s=p.read_text()
needle='final class TemporaryChatSignaturesV1 {\n    enum State { NORMAL, TEMP, UNKNOWN }'
replacement='''final class TemporaryChatSignaturesV1 {\n    // LEGACY-COMPATIBILITY-ONLY: referenced by historical TemporaryChatDomV1.\n    // The v0.91.0 live Planner adapter does not use these for runtime authority.\n    static final String NORMAL_LABEL_HASH = "1a957a52";\n    static final String NORMAL_STRUCT_HASH = "b9c97d1e";\n    static final String NORMAL_SEMANTIC_SET_HASH = "566ee132";\n    static final String TEMP_LABEL_HASH = "ae0e16e6";\n    static final String TEMP_STRUCT_HASH = "34d052a8";\n    static final String TEMP_SEMANTIC_SET_HASH = "2f8aeb2c";\n    static final String EMPTY_TESTID_HASH = "811c9dc5";\n\n    enum State { NORMAL, TEMP, UNKNOWN }'''
assert s.count(needle)==1,('legacy compatibility insertion',s.count(needle))
s=s.replace(needle,replacement,1)
p.write_text(s)

activity=(PKG/'OrchestratorDashboardV104LiveTempControlActivity.java').read_text()
for h in ['1a957a52','b9c97d1e','ae0e16e6','34d052a8','811c9dc5']:
    assert h not in activity,h
for required in ['PLANNER_ENTRY_SCAN','UNIQUE_SEMANTIC_TEMP_CONTROL_CLICK','candidate_active_hint']:
    assert required in activity,required
assert 'LEGACY-COMPATIBILITY-ONLY' in p.read_text()
print('PASS v0.91.0 fixed: legacy compile symbols restored; live Planner remains hash-independent')
