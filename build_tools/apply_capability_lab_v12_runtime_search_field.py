from pathlib import Path
import json

root = Path('runtime_probes/native-capability-lab')
svc_path = root / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java'
svc = svc_path.read_text()

old_screen = '''    private boolean isGlobalSearchScreen(AccessibilityNodeInfo root) {
        return containsSemantic(root, "chatgpt-global-search", 0)
                || countEditableSearchFields(root, true) == 1;
    }
'''
new_screen = '''    private boolean isGlobalSearchScreen(AccessibilityNodeInfo root) {
        if (containsSemantic(root, "chatgpt-global-search", 0)
                || countEditableSearchFields(root, true) == 1) {
            return true;
        }

        // v0.11 real-device evidence reached the official Search surface, but the runtime
        // EditText intentionally exposed no semantic/hint. Identify that surface only by
        // the exact first-party heading plus exactly one visible/enabled ACTION_SET_TEXT
        // field. This remains screen-scoped and must not turn a generic EditText into a
        // Search field elsewhere in ChatGPT.
        List<AccessibilityNodeInfo> runtimeSentinels = new ArrayList<>();
        collectExactSemanticNodes(root, "Search chats, files, and projects", runtimeSentinels, 0);
        int editableSetTextFields = countEditableSearchFields(root, false);
        return runtimeSentinels.size() == 1 && editableSetTextFields == 1;
    }
'''
if 'v0.11 real-device evidence reached the official Search surface' not in svc:
    if old_screen not in svc:
        raise SystemExit('isGlobalSearchScreen anchor not found')
    svc = svc.replace(old_screen, new_screen, 1)
svc_path.write_text(svc)

gradle_path = root / 'app/build.gradle'
gradle = gradle_path.read_text()
gradle = gradle.replace('versionCode 11', 'versionCode 12', 1)
gradle = gradle.replace("versionName '0.11-native-capability-lab-stable-exact-drawer-search'",
                        "versionName '0.12-native-capability-lab-stable-runtime-search-field'", 1)
if 'versionCode 12' not in gradle or "0.12-native-capability-lab-stable-runtime-search-field" not in gradle:
    raise SystemExit('version patch failed')
gradle_path.write_text(gradle)

plan_path = root / 'plans/default.json'
plan = json.loads(plan_path.read_text())
if plan.get('suite') == 'conversation_search_binding_v6_exact_drawer_search':
    plan['suite'] = 'conversation_search_binding_v7_runtime_search_field'
elif plan.get('suite') != 'conversation_search_binding_v7_runtime_search_field':
    raise SystemExit('unexpected suite: ' + str(plan.get('suite')))
plan_path.write_text(json.dumps(plan, indent=2) + '\n')
