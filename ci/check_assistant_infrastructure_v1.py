#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path('runtime_probes/chatgpt-webview-stable-probe')
PKG = ROOT / 'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'

exact = (PKG / 'ExactTextV1.java').read_text()
journal = (PKG / 'WorkflowJournalV1.java').read_text()
bounds = (PKG / 'AssistantInfrastructureBoundariesV1.java').read_text()

for token in [
    'replace("\\r\\n", "\\n")',
    "replace('\\r', '\\n')",
    'MessageDigest.getInstance("SHA-256")',
    'static boolean same(String a, String b)',
]:
    assert token in exact, token
assert 'replaceAll("\\s+' not in exact

for token in [
    'STEP_DISPATCH_IN_FLIGHT',
    'STEP_WAITING_RECEIPT',
    'RECOVERY_RECONCILE_ONLY',
    'dispatch_count',
    'captureExactTextOutput',
    'ExactTextV1.sha256',
    'dependency cycle',
    'output ref not dependency',
    'immutable once captured',
]:
    assert token in journal, token
assert journal.count('s.put("dispatch_count", 1)') == 1
assert 'if (s.optInt("dispatch_count", 0) != 0) return false;' in journal
assert 'STEP_DISPATCH_IN_FLIGHT.equals(state) || STEP_WAITING_RECEIPT.equals(state)' in journal

for token in [
    'interface SpeechOutputAdapterV1',
    'class AndroidTtsSpeechOutputV1',
    'interface WakeIngressAdapterV1',
    'class DisabledWakeIngressV1',
    'interface PlannerSessionLifecycleV1',
    'beginDisposable',
    'markSemanticResultPersisted',
    'finishDisposable',
]:
    assert token in bounds, token

# Optional local schema copy, when present in a future implementation bundle.
local_schema = Path('contracts/cf-workflow-plan.v1.schema.json')
if local_schema.exists():
    schema = json.loads(local_schema.read_text())
    assert schema['$id'] == 'cf-workflow-plan.v1'
    assert schema['properties']['status']['enum'] == [
        'READY', 'NEEDS_CLARIFICATION', 'NO_ACTION', 'UNSUPPORTED'
    ]
    assert 'capabilityStep' in schema['$defs']
    assert 'semanticStep' in schema['$defs']

print('PASS assistant infrastructure v1 static invariants')
