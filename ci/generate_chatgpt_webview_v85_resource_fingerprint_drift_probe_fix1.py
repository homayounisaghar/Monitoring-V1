#!/usr/bin/env python3
from pathlib import Path
import runpy

# Mechanical compile repair only. The v0.83 diagnostic semantics are generated
# by the base script unchanged; this wrapper repairs one malformed class-scope
# declaration produced when runtime-reset text also matched the field initializer.
runpy.run_path("ci/generate_chatgpt_webview_v85_resource_fingerprint_drift_probe.py", run_name="__main__")

p=Path("runtime_probes/chatgpt-webview-stable-probe/app/src/main/java/com/homayounisaghar/chatgptwebviewprobe/OrchestratorResourceToolsV85Activity.java")
s=p.read_text()
bad='private String resourceV85ClaimTurnFingerprint="-";resourceV85ClaimAssistantHash="-";resourceV85ClaimUserHash="-";resourceV85ClaimAssistantProjectionHash="-";resourceV85ClaimUserProjectionHash="-";resourceV85ClaimAssistantLen=-1;resourceV85ClaimUserLen=-1;resourceV85ClaimAssistantProjectionLen=-1;resourceV85ClaimUserProjectionLen=-1;resourceV85ClaimAssistantOrdinal=-1;resourceV85ClaimAssistantTurnCount=-1;resourceV85ClaimUserTurnCount=-1;'
assert s.count(bad)==1,s.count(bad)
s=s.replace(bad,'private String resourceV85ClaimTurnFingerprint="-";',1)
p.write_text(s)

# Prove the intended separately declared diagnostic fields remain, and runtime
# resets still clear them outside the field declaration.
out=p.read_text()
assert 'private String resourceV85ClaimAssistantHash="-",resourceV85ClaimUserHash="-";' in out
assert 'private String resourceV85ClaimAssistantProjectionHash="-",resourceV85ClaimUserProjectionHash="-";' in out
assert 'private int resourceV85ClaimAssistantLen=-1,resourceV85ClaimUserLen=-1;' in out
assert 'private int resourceV85ClaimAssistantProjectionLen=-1,resourceV85ClaimUserProjectionLen=-1;' in out
assert 'private int resourceV85ClaimAssistantOrdinal=-1,resourceV85ClaimAssistantTurnCount=-1,resourceV85ClaimUserTurnCount=-1;' in out
assert out.count('resourceV85ClaimAssistantHash="-";')>=1
assert out.count('resourceV85ClaimAssistantLen=-1;')>=1
assert bad not in out
print('PASS v0.83 fix1: mechanical class-field declaration repair; diagnostic semantics unchanged')
