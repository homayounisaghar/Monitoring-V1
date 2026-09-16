#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT = Path('runtime_probes/native-capability-lab')
GRADLE = ROOT / 'app/build.gradle'
PLAN = ROOT / 'plans/default.json'
LOADER = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/PlanLoader.java'
MAIN = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/MainActivity.java'

plan = {
    'schema': 1,
    'suite': 'conversation_history_accessibility_binding_v14_history_only',
    'targetVersion': '1.2026.237',
    'targetSignerSha256': 'b24f4bfbb3cf293f938703b9d87027c1102cc36dc4fa206910e08927db40473c',
    'steps': [
        {'op': 'resume_chatgpt'},
        {'op': 'wait', 'ms': 900},
        {'op': 'history_boundary_calibration', 'timeoutMs': 15000},
        {'op': 'reset_after_calibration'},
        {
            'op': 'launch_prompt',
            'prompt': 'Capability Lab History accessibility proof. Reply with exactly this marker and no other text: {{marker}}'
        },
        {'op': 'capture_tree', 'label': 'pre_send_draft_baseline', 'timeoutMs': 8000},
        {'op': 'semantic_send', 'timeoutMs': 15000},
        {'op': 'capture_tree', 'label': 'post_send_receipt', 'timeoutMs': 8000},
        {'op': 'wait', 'ms': 700},
        {'op': 'history_recent_binding', 'timeoutMs': 26000, 'settleMs': 1100},
        {'op': 'verify_candidates', 'timeoutMs': 8000},
        {'op': 'finish', 'inconclusiveStatus': 'INCONCLUSIVE_HISTORY_ACCESSIBILITY_BOUNDARY_NOT_VERIFIED'}
    ]
}

# Version bump keeps the persistent package/signer update path intact.
gradle = GRADLE.read_text()
assert 'versionCode 18' in gradle
assert '0.18-native-capability-lab-stable-history-a11y-boundary' in gradle
gradle = gradle.replace('versionCode 18', 'versionCode 19')
gradle = gradle.replace(
    '0.18-native-capability-lab-stable-history-a11y-boundary',
    '0.19-native-capability-lab-stable-history-only-boundary'
)
GRADLE.write_text(gradle)

PLAN.write_text(json.dumps(plan, indent=2) + '\n')

loader = LOADER.read_text()
assert 'conversation_history_accessibility_binding_v13_static_first' in loader
compact = json.dumps(plan, separators=(',', ':'))
java_literal = compact.replace('\\', '\\\\').replace('"', '\\"')
loader, n = re.subn(
    r'    static final String FALLBACK = ".*";',
    '    static final String FALLBACK = "' + java_literal + '";',
    loader,
    count=1
)
assert n == 1
LOADER.write_text(loader)

main = MAIN.read_text()
assert 'Stable v0.18 validates the exact APK-derived History accessibility boundary before using a History row.' in main
main = main.replace(
    'Stable v0.18 validates the exact APK-derived History accessibility boundary before using a History row. ',
    'Stable v0.19 tests the exact APK-derived History accessibility boundary with official Search removed from the critical path. '
)
main = main.replace(
    'It first performs a best-effort calibration against an already indexed synthetic marker and records a pre-fresh baseline of raw chatgpt.history.item.* / chatgpt.history.actions.* view IDs, actions, and structure. ',
    'It first foregrounds ChatGPT and records a direct pre-fresh baseline of raw chatgpt.history.item.* / chatgpt.history.actions.* view IDs, actions, and structure. '
)
main = main.replace('INDEX TRIGGER LADDER RUNNING…', 'HISTORY BOUNDARY PROOF RUNNING…')
main = main.replace('RUN FRESH HISTORY BINDING PROOF', 'RUN HISTORY ACCESSIBILITY BOUNDARY PROOF')
MAIN.write_text(main)

# Contract assertions: Search is no longer a prerequisite for this proof.
data = json.loads(PLAN.read_text())
ops = [x['op'] for x in data['steps']]
assert data['suite'] == 'conversation_history_accessibility_binding_v14_history_only'
assert ops[:4] == ['resume_chatgpt', 'wait', 'history_boundary_calibration', 'reset_after_calibration']
assert 'global_search_binding' not in ops
assert ops.count('semantic_send') == 1
assert ops.count('history_recent_binding') == 1
assert ops.count('verify_candidates') == 1
assert 'chatgpt.history.item.' in (ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java').read_text()
print('Capability Lab v0.19 History-only boundary patch applied')
