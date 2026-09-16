from pathlib import Path
import json

root = Path('runtime_probes/native-capability-lab')
svc_path = root / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java'
svc = svc_path.read_text()

# Add a state-bound runtime Search-surface resolver. v0.12 proved the actual
# post-navigation surface exposes exactly one ACTION_SET_TEXT EditText plus exact
# visible Search and Close semantics, but not the long static heading.
anchor = '''    private AccessibilityNodeInfo findGlobalSearchRoot(List<AccessibilityNodeInfo> roots) {
        for (AccessibilityNodeInfo root : roots) if (isGlobalSearchScreen(root)) return root;
        return null;
    }
'''
helper = anchor + '''\n    private AccessibilityNodeInfo findRuntimeSearchRoot(List<AccessibilityNodeInfo> roots) {
        AccessibilityNodeInfo match = null;
        for (AccessibilityNodeInfo root : roots) {
            if (!isRuntimeSearchRoot(root)) continue;
            if (match != null && !match.equals(root)) return null;
            match = root;
        }
        return match;
    }

    private boolean isRuntimeSearchRoot(AccessibilityNodeInfo root) {
        if (root == null) return false;
        List<AccessibilityNodeInfo> search = new ArrayList<>();
        List<AccessibilityNodeInfo> close = new ArrayList<>();
        collectExactSemanticNodes(root, "Search", search, 0);
        collectExactSemanticNodes(root, "Close", close, 0);
        int editableSetTextFields = countEditableSearchFields(root, false);
        return search.size() == 1 && close.size() == 1 && editableSetTextFields == 1;
    }
'''
if 'findRuntimeSearchRoot(List<AccessibilityNodeInfo> roots)' not in svc:
    if anchor not in svc:
        raise SystemExit('findGlobalSearchRoot anchor not found')
    svc = svc.replace(anchor, helper, 1)

old_field = '''        if ("WAITING_GLOBAL_SEARCH_FIELD".equals(state)) {
            AccessibilityNodeInfo field = null;
            String surface = "";
            AccessibilityNodeInfo globalRoot = findGlobalSearchRoot(roots);
            if (globalRoot != null) {
                field = findGlobalSearchField(globalRoot);
                surface = "global";
            }
'''
new_field = '''        if ("WAITING_GLOBAL_SEARCH_FIELD".equals(state)) {
            AccessibilityNodeInfo field = null;
            String surface = "";
            AccessibilityNodeInfo globalRoot = findGlobalSearchRoot(roots);
            if (globalRoot == null) {
                // v0.12 runtime contract, usable only after the already-proven Menu + Search
                // navigation has placed the runner in WAITING_GLOBAL_SEARCH_FIELD.
                globalRoot = findRuntimeSearchRoot(roots);
                if (globalRoot != null) {
                    LabStore.append(this, "GLOBAL_SEARCH_RUNTIME_FIELD_CONTRACT matched=true");
                }
            }
            if (globalRoot != null) {
                field = findGlobalSearchField(globalRoot);
                surface = "global";
            }
'''
if 'GLOBAL_SEARCH_RUNTIME_FIELD_CONTRACT matched=true' not in svc:
    if old_field not in svc:
        raise SystemExit('WAITING_GLOBAL_SEARCH_FIELD anchor not found')
    svc = svc.replace(old_field, new_field, 1)

old_result = '''        if ("WAITING_GLOBAL_SEARCH_RESULT".equals(state)) {
            AccessibilityNodeInfo surfaceRoot = findGlobalSearchRoot(roots);
            boolean globalSurface = surfaceRoot != null;
            if (surfaceRoot == null) surfaceRoot = findRootWithHistorySearchFieldEquals(roots, marker);
'''
new_result = '''        if ("WAITING_GLOBAL_SEARCH_RESULT".equals(state)) {
            AccessibilityNodeInfo surfaceRoot = findGlobalSearchRoot(roots);
            boolean globalSurface = surfaceRoot != null;
            if (surfaceRoot == null) {
                surfaceRoot = findRuntimeSearchRoot(roots);
                if (surfaceRoot != null) globalSurface = true;
            }
            if (surfaceRoot == null) surfaceRoot = findRootWithHistorySearchFieldEquals(roots, marker);
'''
if old_result in svc:
    svc = svc.replace(old_result, new_result, 1)
elif 'surfaceRoot = findRuntimeSearchRoot(roots);' not in svc:
    raise SystemExit('WAITING_GLOBAL_SEARCH_RESULT anchor not found')

old_post_query = '''            if (!set) {
                failRun("GLOBAL_SEARCH_SET_TEXT_FALSE surface=" + surface);
                return;
            }
            handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 350L);
            return;
'''
new_post_query = '''            if (!set) {
                failRun("GLOBAL_SEARCH_SET_TEXT_FALSE surface=" + surface);
                return;
            }
            handler.postDelayed(() -> {
                if (!isCurrentStep(expectedStep)) return;
                if (!"WAITING_GLOBAL_SEARCH_RESULT".equals(LabStore.state(this))) return;
                List<AccessibilityNodeInfo> postQueryRoots = chatGptRoots();
                LabStore.append(this, "GLOBAL_SEARCH_POST_QUERY_CONTROL_CENSUS windows="
                        + postQueryRoots.size() + " "
                        + LabStore.abbrev(controlCensus(postQueryRoots, 260), 20000));
                tryGlobalSearchBinding(expectedStep);
            }, 350L);
            return;
'''
if 'GLOBAL_SEARCH_POST_QUERY_CONTROL_CENSUS' not in svc:
    if old_post_query not in svc:
        raise SystemExit('post-query scheduling anchor not found')
    svc = svc.replace(old_post_query, new_post_query, 1)

svc_path.write_text(svc)

gradle_path = root / 'app/build.gradle'
gradle = gradle_path.read_text()
gradle = gradle.replace('versionCode 12', 'versionCode 13', 1)
gradle = gradle.replace("versionName '0.12-native-capability-lab-stable-runtime-search-field'",
                        "versionName '0.13-native-capability-lab-stable-state-bound-search-field'", 1)
if 'versionCode 13' not in gradle or "0.13-native-capability-lab-stable-state-bound-search-field" not in gradle:
    raise SystemExit('version patch failed')
gradle_path.write_text(gradle)

plan_path = root / 'plans/default.json'
plan = json.loads(plan_path.read_text())
if plan.get('suite') == 'conversation_search_binding_v7_runtime_search_field':
    plan['suite'] = 'conversation_search_binding_v8_state_bound_search_field'
elif plan.get('suite') != 'conversation_search_binding_v8_state_bound_search_field':
    raise SystemExit('unexpected suite: ' + str(plan.get('suite')))
plan_path.write_text(json.dumps(plan, indent=2) + '\n')
