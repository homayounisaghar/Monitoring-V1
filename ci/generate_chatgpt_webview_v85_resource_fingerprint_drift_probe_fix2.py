#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# Mechanical compile repair only. Run the approved v0.83 diagnostic generator,
# then repair the generated field declaration that was broadened by the global
# reset replacement. Diagnostic semantics and zero-effect behavior are unchanged.
runpy.run_path("ci/generate_chatgpt_webview_v85_resource_fingerprint_drift_probe.py", run_name="__main__")

p=Path("runtime_probes/chatgpt-webview-stable-probe/app/src/main/java/com/homayounisaghar/chatgptwebviewprobe/OrchestratorResourceToolsV85Activity.java")
s=p.read_text()
pat=r'(?m)^    private String resourceV85ClaimTurnFingerprint="-";resourceV85ClaimAssistantHash="-";resourceV85ClaimUserHash="-";resourceV85ClaimAssistantProjectionHash="-";resourceV85ClaimUserProjectionHash="-";resourceV85ClaimAssistantLen=-1;resourceV85ClaimUserLen=-1;resourceV85ClaimAssistantProjectionLen=-1;resourceV85ClaimUserProjectionLen=-1;resourceV85ClaimAssistantOrdinal=-1;resourceV85ClaimAssistantTurnCount=-1;resourceV85ClaimUserTurnCount=-1;$'
m=re.findall(pat,s)
assert len(m)==1, len(m)
s=re.sub(pat,'    private String resourceV85ClaimTurnFingerprint="-";',s,count=1)
# The correctly typed diagnostic fields inserted immediately after the claim
# fingerprint must remain exactly once.
for needle in [
    'private String resourceV85ClaimAssistantHash="-",resourceV85ClaimUserHash="-";',
    'private String resourceV85ClaimAssistantProjectionHash="-",resourceV85ClaimUserProjectionHash="-";',
    'private int resourceV85ClaimAssistantLen=-1,resourceV85ClaimUserLen=-1;',
    'private int resourceV85ClaimAssistantProjectionLen=-1,resourceV85ClaimUserProjectionLen=-1;',
    'private int resourceV85ClaimAssistantOrdinal=-1,resourceV85ClaimAssistantTurnCount=-1,resourceV85ClaimUserTurnCount=-1;'
]:
    assert s.count(needle)==1,(needle,s.count(needle))
p.write_text(s)
print('PASS v0.83 fix2: generated Java field declarations mechanically repaired; diagnostic semantics unchanged')
