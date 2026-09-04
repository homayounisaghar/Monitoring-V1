#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT = Path('runtime_probes/native-capability-lab')
GRADLE = ROOT / 'app/build.gradle'
PLAN = ROOT / 'plans/default.json'
LOADER = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/PlanLoader.java'
MAIN = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/MainActivity.java'
SVC = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java'

OLD_SUITE = 'conversation_history_accessibility_binding_v14_history_only'
NEW_SUITE = 'conversation_history_accessibility_binding_v15_row_disambiguated'
NEW_VERSION_NAME = '0.20-native-capability-lab-stable-history-row-disambiguation'

# Preserve the v0.19 History-only plan; only advance suite identity.
plan = json.loads(PLAN.read_text())
assert plan['suite'] == OLD_SUITE
ops = [x['op'] for x in plan['steps']]
assert ops[:4] == ['resume_chatgpt', 'wait', 'history_boundary_calibration', 'reset_after_calibration']
assert 'global_search_binding' not in ops
assert ops.count('semantic_send') == 1
assert ops.count('history_recent_binding') == 1
plan['suite'] = NEW_SUITE
PLAN.write_text(json.dumps(plan, indent=2) + '\n')

# Persistent package/signer lineage, monotonic versionCode.
gradle = GRADLE.read_text()
assert 'versionCode 19' in gradle
assert '0.19-native-capability-lab-stable-history-only-boundary' in gradle
gradle = gradle.replace('versionCode 19', 'versionCode 20')
gradle = gradle.replace('0.19-native-capability-lab-stable-history-only-boundary', NEW_VERSION_NAME)
GRADLE.write_text(gradle)

# Embedded fallback must match the remote plan contract.
loader = LOADER.read_text()
assert OLD_SUITE in loader
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

# v0.19 runtime evidence proved the duplicate semantic New chat nodes are NOT aliases:
# one is a History conversation title whose actionable ancestor has ACTION_LONG_CLICK;
# the other is the actual navigation control, clickable without ACTION_LONG_CLICK.
svc = SVC.read_text()
old = '''    private void switchAwayFromFreshThread(int expectedStep, List<AccessibilityNodeInfo> roots) {\n        List<AccessibilityNodeInfo> semanticLeaves = new ArrayList<>();\n        List<AccessibilityNodeInfo> actionableTargets = new ArrayList<>();\n        for (AccessibilityNodeInfo root : roots) {\n            List<AccessibilityNodeInfo> one = new ArrayList<>();\n            collectExactSemanticNodes(root, "New chat", one, 0);\n            for (AccessibilityNodeInfo leaf : one) {\n                addUniqueNode(semanticLeaves, leaf);\n                AccessibilityNodeInfo target = firstActionClickAncestor(leaf, 8);\n                if (target != null) addUniqueNode(actionableTargets, target);\n            }\n        }\n        LabStore.append(this, "HISTORY_RECENT_NEW_CHAT_RESOLUTION semanticLeaves=" + semanticLeaves.size()\n                + " actionableTargets=" + actionableTargets.size());\n        if (actionableTargets.size() != 1) {\n            failRun("HISTORY_RECENT_NEW_CHAT_ACTIONABLE_NOT_UNIQUE count=" + actionableTargets.size());\n            return;\n        }\n        AccessibilityNodeInfo newChat = actionableTargets.get(0);\n        LabStore.setState(this, "WAITING_HISTORY_RECENT_SWITCH_AWAY");\n        if (!performBoundedNavigation(newChat, "HISTORY_RECENT_SWITCH_AWAY", "New chat")) {\n            failRun("HISTORY_RECENT_SWITCH_AWAY_ACTION_FALSE");\n            return;\n        }\n        handler.postDelayed(() -> tryHistoryRecentBinding(expectedStep), 320L);\n    }\n'''
new = '''    private void switchAwayFromFreshThread(int expectedStep, List<AccessibilityNodeInfo> roots) {\n        List<AccessibilityNodeInfo> semanticLeaves = new ArrayList<>();\n        List<AccessibilityNodeInfo> navigationTargets = new ArrayList<>();\n        List<AccessibilityNodeInfo> excludedHistoryRows = new ArrayList<>();\n        StringBuilder signatures = new StringBuilder();\n        for (AccessibilityNodeInfo root : roots) {\n            List<AccessibilityNodeInfo> one = new ArrayList<>();\n            collectExactSemanticNodes(root, "New chat", one, 0);\n            for (AccessibilityNodeInfo leaf : one) {\n                addUniqueNode(semanticLeaves, leaf);\n                AccessibilityNodeInfo target = firstActionClickAncestor(leaf, 8);\n                if (target == null) continue;\n                boolean historyRowContract = hasAction(target, AccessibilityNodeInfo.ACTION_LONG_CLICK);\n                if (signatures.length() > 0) signatures.append(" || ");\n                signatures.append("leafClass=").append(shortClass(leaf.getClassName()))\n                        .append(" leafClickable=").append(leaf.isClickable())\n                        .append(" targetClass=").append(shortClass(target.getClassName()))\n                        .append(" targetClickable=").append(target.isClickable())\n                        .append(" targetLongClick=").append(historyRowContract)\n                        .append(" targetSemantic=").append(LabStore.abbrev(safeControlSemantic(target), 180))\n                        .append(" actions=").append(safeActionLabels(target));\n                if (historyRowContract) {\n                    addUniqueNode(excludedHistoryRows, target);\n                } else if (target.isVisibleToUser() && target.isEnabled()\n                        && hasAction(target, AccessibilityNodeInfo.ACTION_CLICK)) {\n                    addUniqueNode(navigationTargets, target);\n                }\n            }\n        }\n        LabStore.append(this, "HISTORY_RECENT_NEW_CHAT_RESOLUTION semanticLeaves=" + semanticLeaves.size()\n                + " navigationTargets=" + navigationTargets.size()\n                + " excludedLongClickHistoryRows=" + excludedHistoryRows.size()\n                + " signatures=" + LabStore.abbrev(signatures.toString(), 8000));\n        if (navigationTargets.size() != 1) {\n            failRun("HISTORY_RECENT_NEW_CHAT_NAVIGATION_NOT_UNIQUE count=" + navigationTargets.size()\n                    + " excludedHistoryRows=" + excludedHistoryRows.size());\n            return;\n        }\n        AccessibilityNodeInfo newChat = navigationTargets.get(0);\n        LabStore.setState(this, "WAITING_HISTORY_RECENT_SWITCH_AWAY");\n        if (!performBoundedNavigation(newChat, "HISTORY_RECENT_SWITCH_AWAY", "New chat")) {\n            failRun("HISTORY_RECENT_SWITCH_AWAY_ACTION_FALSE");\n            return;\n        }\n        handler.postDelayed(() -> tryHistoryRecentBinding(expectedStep), 320L);\n    }\n'''
assert old in svc
svc = svc.replace(old, new, 1)
SVC.write_text(svc)

# Explain the evidence-driven selector change in the Lab UI.
main = MAIN.read_text()
assert 'Stable v0.19 tests the exact APK-derived History accessibility boundary with official Search removed from the critical path.' in main
main = main.replace(
    'Stable v0.19 tests the exact APK-derived History accessibility boundary with official Search removed from the critical path.',
    'Stable v0.20 continues the exact APK-derived History accessibility boundary proof with official Search removed from the critical path.'
)
main = main.replace(
    'New chat label/container aliases are deduplicated to one actionable target before navigation.',
    'Runtime-proven History rows titled New chat are excluded by their ACTION_LONG_CLICK row contract; the navigation control must be the unique clickable non-long-click target before switching away.'
)
MAIN.write_text(main)

# Strong postconditions.
data = json.loads(PLAN.read_text())
ops = [x['op'] for x in data['steps']]
assert data['suite'] == NEW_SUITE
assert 'global_search_binding' not in ops
assert ops.count('semantic_send') == 1
assert ops.count('history_recent_binding') == 1
svc = SVC.read_text()
assert 'excludedLongClickHistoryRows=' in svc
assert 'HISTORY_RECENT_NEW_CHAT_NAVIGATION_NOT_UNIQUE' in svc
assert 'hasAction(target, AccessibilityNodeInfo.ACTION_LONG_CLICK)' in svc
assert 'chatgpt.history.item.' in svc
print('Capability Lab v0.20 History row disambiguation patch applied')
