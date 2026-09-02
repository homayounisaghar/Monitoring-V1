from pathlib import Path
import json

root = Path('runtime_probes/native-capability-lab')
svc_path = root / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java'
svc = svc_path.read_text()

old_receipt = '''                boolean exactQuery = marker.equals(actualQuery);
                LabStore.append(this, "GLOBAL_SEARCH_QUERY_RECEIPT exact=" + exactQuery
                        + " actualLen=" + actualQuery.length()
                        + " actual=" + LabStore.abbrev(actualQuery, 96));
                if (!exactQuery) {
                    failRun("GLOBAL_SEARCH_QUERY_TEXT_MISMATCH");
                    return;
                }
                LabStore.append(this, "GLOBAL_SEARCH_POST_QUERY_CONTROL_CENSUS windows="
'''
new_receipt = '''                boolean exactQuery = marker.equals(actualQuery);
                boolean queryTextUnavailable = actualQuery.isEmpty();
                LabStore.append(this, "GLOBAL_SEARCH_QUERY_RECEIPT exact=" + exactQuery
                        + " unavailable=" + queryTextUnavailable
                        + " actualLen=" + actualQuery.length()
                        + " actual=" + LabStore.abbrev(actualQuery, 96));
                // Runtime v0.14 showed ACTION_SET_TEXT=true while the re-rendered Search
                // EditText returned an empty getText() through Accessibility. Empty readback
                // is therefore treated as unavailable evidence, not contradictory evidence.
                // A non-empty mismatch still fails closed. Exactness is then established by
                // the unique marker-bearing result and exact marker receipt after reopen.
                if (!exactQuery && !queryTextUnavailable) {
                    failRun("GLOBAL_SEARCH_QUERY_TEXT_MISMATCH");
                    return;
                }
                if (queryTextUnavailable) {
                    LabStore.append(this, "GLOBAL_SEARCH_QUERY_RECEIPT_DEFERRED_TO_RESULT_EVIDENCE");
                }
                LabStore.append(this, "GLOBAL_SEARCH_POST_QUERY_CONTROL_CENSUS windows="
'''
if old_receipt not in svc:
    raise SystemExit('query receipt anchor not found')
svc = svc.replace(old_receipt, new_receipt, 1)

old_runtime_helper = '''    private boolean isRuntimeSearchRoot(AccessibilityNodeInfo root) {
        if (root == null) return false;
        List<AccessibilityNodeInfo> search = new ArrayList<>();
        List<AccessibilityNodeInfo> close = new ArrayList<>();
        collectExactSemanticNodes(root, "Search", search, 0);
        collectExactSemanticNodes(root, "Close", close, 0);
        int editableSetTextFields = countEditableSearchFields(root, false);
        return search.size() == 1 && close.size() == 1 && editableSetTextFields == 1;
    }
'''
new_runtime_helper = old_runtime_helper + '''\n    private AccessibilityNodeInfo findRuntimeSearchSurfaceRoot(List<AccessibilityNodeInfo> roots) {
        AccessibilityNodeInfo match = null;
        for (AccessibilityNodeInfo root : roots) {
            if (!isRuntimeSearchSurfaceRoot(root)) continue;
            if (match != null && !match.equals(root)) return null;
            match = root;
        }
        return match;
    }

    private boolean isRuntimeSearchSurfaceRoot(AccessibilityNodeInfo root) {
        if (root == null) return false;
        List<AccessibilityNodeInfo> close = new ArrayList<>();
        collectExactSemanticNodes(root, "Close", close, 0);
        int editableSetTextFields = countEditableSearchFields(root, false);
        return close.size() == 1 && editableSetTextFields == 1;
    }
'''
if 'findRuntimeSearchSurfaceRoot' not in svc:
    if old_runtime_helper not in svc:
        raise SystemExit('runtime search helper anchor not found')
    svc = svc.replace(old_runtime_helper, new_runtime_helper, 1)

old_result_surface = '''            if (surfaceRoot == null) {
                surfaceRoot = findRuntimeSearchRoot(roots);
                if (surfaceRoot != null) globalSurface = true;
            }
            if (surfaceRoot == null) surfaceRoot = findRootWithHistorySearchFieldEquals(roots, marker);
'''
new_result_surface = '''            if (surfaceRoot == null) {
                surfaceRoot = findRuntimeSearchRoot(roots);
                if (surfaceRoot != null) globalSurface = true;
            }
            if (surfaceRoot == null) {
                // After a query the literal Search label may disappear while the same
                // first-party surface keeps the unique editable field + Close control.
                surfaceRoot = findRuntimeSearchSurfaceRoot(roots);
                if (surfaceRoot != null) globalSurface = true;
            }
            if (surfaceRoot == null) surfaceRoot = findRootWithHistorySearchFieldEquals(roots, marker);
'''
if old_result_surface not in svc:
    raise SystemExit('result surface anchor not found')
svc = svc.replace(old_result_surface, new_result_surface, 1)

old_reopen_guard = '''        if ("WAITING_GLOBAL_SEARCH_REOPEN".equals(state)) {
            if (anyGlobalSearchScreen(roots) || anyHistoryDrawerScreen(roots)) return;
            MarkerCounts counts = countMarkerNodesAcrossRoots(roots, marker);
'''
new_reopen_guard = '''        if ("WAITING_GLOBAL_SEARCH_REOPEN".equals(state)) {
            // Do not mistake the marker text inside Search results for a reopened chat.
            // Require every known Search-surface sentinel to disappear first.
            if (anyGlobalSearchScreen(roots) || anyHistoryDrawerScreen(roots)
                    || findRuntimeSearchSurfaceRoot(roots) != null) return;
            MarkerCounts counts = countMarkerNodesAcrossRoots(roots, marker);
'''
if old_reopen_guard not in svc:
    raise SystemExit('reopen guard anchor not found')
svc = svc.replace(old_reopen_guard, new_reopen_guard, 1)
svc_path.write_text(svc)

gradle_path = root / 'app/build.gradle'
gradle = gradle_path.read_text()
gradle = gradle.replace('versionCode 14', 'versionCode 15', 1)
gradle = gradle.replace("versionName '0.14-native-capability-lab-stable-indexed-marker-reopen'",
                        "versionName '0.15-native-capability-lab-stable-result-evidence-receipt'", 1)
if 'versionCode 15' not in gradle:
    raise SystemExit('version patch failed')
gradle_path.write_text(gradle)

plan_path = root / 'plans/default.json'
plan = json.loads(plan_path.read_text())
if plan.get('suite') != 'conversation_search_binding_v9_indexed_marker_reopen':
    raise SystemExit('unexpected prior suite: ' + str(plan.get('suite')))
plan['suite'] = 'conversation_search_binding_v10_result_evidence_receipt'
plan_path.write_text(json.dumps(plan, indent=2) + '\n')

main_path = root / 'app/src/main/java/com/openai/controlplane/capabilitylab/MainActivity.java'
main = main_path.read_text()
main = main.replace('Stable v0.10 matches the real-device Menu semantic exactly (not by substring) and continues the official Search proof',
                    'Stable v0.15 verifies an indexed historical SearchBinding using result evidence when Search field readback is unavailable, while continuing the official Search proof', 1)
main_path.write_text(main)
