from pathlib import Path
import json

root = Path('runtime_probes/native-capability-lab')
svc_path = root / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java'
svc = svc_path.read_text()

old_helper = '''    private int countExactSemanticAcrossRoots(List<AccessibilityNodeInfo> roots, String exact) {
        List<AccessibilityNodeInfo> found = new ArrayList<>();
        for (AccessibilityNodeInfo root : roots) {
            List<AccessibilityNodeInfo> one = new ArrayList<>();
            collectExactSemanticNodes(root, exact, one, 0);
            for (AccessibilityNodeInfo n : one) addUniqueNode(found, n);
        }
        return found.size();
    }
'''
new_helper = old_helper + '''\n    private AccessibilityNodeInfo findUniqueExactSemanticAcrossRoots(List<AccessibilityNodeInfo> roots, String exact) {
        List<AccessibilityNodeInfo> found = new ArrayList<>();
        for (AccessibilityNodeInfo root : roots) {
            List<AccessibilityNodeInfo> one = new ArrayList<>();
            collectExactSemanticNodes(root, exact, one, 0);
            for (AccessibilityNodeInfo n : one) addUniqueNode(found, n);
        }
        return found.size() == 1 ? found.get(0) : null;
    }
'''
if 'findUniqueExactSemanticAcrossRoots' not in svc:
    if old_helper not in svc:
        raise SystemExit('countExactSemanticAcrossRoots helper anchor not found')
    svc = svc.replace(old_helper, new_helper, 1)

old_drawer = '''            AccessibilityNodeInfo historySearch = findUniqueHistorySearchEntryAcrossRoots(roots);
            if (historySearch == null) return;
            LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
            if (!performBoundedNavigation(historySearch, "GLOBAL_SEARCH_HISTORY_SEARCH",
                    "Search chats", "Search conversations")) {
                failRun("GLOBAL_SEARCH_HISTORY_SEARCH_ACTION_FALSE");
                return;
            }
            handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 300L);
            return;
'''
new_drawer = '''            // v0.10 crossed the Menu gate and exposed the real first-party drawer control
            // as a child whose COMPLETE semantic is exactly "Search", with ACTION_CLICK on
            // its parent. Accept that control only in this post-Menu state and only when it
            // is unique across ChatGPT roots. Do not broaden this into a generic Search alias.
            int exactDrawerSearchCount = countExactSemanticAcrossRoots(roots, "Search");
            if (exactDrawerSearchCount > 0) {
                LabStore.append(this, "GLOBAL_SEARCH_DRAWER_SEARCH_EXACT_MATCHES=" + exactDrawerSearchCount);
            }
            if (exactDrawerSearchCount > 1) {
                failRun("GLOBAL_SEARCH_DRAWER_SEARCH_NOT_UNIQUE count=" + exactDrawerSearchCount);
                return;
            }
            if (exactDrawerSearchCount == 1) {
                AccessibilityNodeInfo exactDrawerSearch = findUniqueExactSemanticAcrossRoots(roots, "Search");
                if (exactDrawerSearch == null) {
                    failRun("GLOBAL_SEARCH_DRAWER_SEARCH_UNIQUE_RESOLUTION_FAILED");
                    return;
                }
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                if (!performBoundedNavigation(exactDrawerSearch, "GLOBAL_SEARCH_DRAWER_EXACT_SEARCH", "Search")) {
                    failRun("GLOBAL_SEARCH_DRAWER_EXACT_SEARCH_ACTION_FALSE");
                    return;
                }
                handler.postDelayed(() -> {
                    if (!isCurrentStep(expectedStep)) return;
                    if (!"WAITING_GLOBAL_SEARCH_FIELD".equals(LabStore.state(this))) return;
                    List<AccessibilityNodeInfo> postSearchRoots = chatGptRoots();
                    LabStore.append(this, "GLOBAL_SEARCH_POST_SEARCH_CLICK_CONTROL_CENSUS windows="
                            + postSearchRoots.size() + " "
                            + LabStore.abbrev(controlCensus(postSearchRoots, 220), 18000));
                    tryGlobalSearchBinding(expectedStep);
                }, 300L);
                return;
            }

            AccessibilityNodeInfo historySearch = findUniqueHistorySearchEntryAcrossRoots(roots);
            if (historySearch == null) return;
            LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
            if (!performBoundedNavigation(historySearch, "GLOBAL_SEARCH_HISTORY_SEARCH",
                    "Search chats", "Search conversations")) {
                failRun("GLOBAL_SEARCH_HISTORY_SEARCH_ACTION_FALSE");
                return;
            }
            handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 300L);
            return;
'''
if 'GLOBAL_SEARCH_DRAWER_SEARCH_EXACT_MATCHES' not in svc:
    if old_drawer not in svc:
        raise SystemExit('post-Menu historySearch anchor not found')
    svc = svc.replace(old_drawer, new_drawer, 1)
svc_path.write_text(svc)

gradle_path = root / 'app/build.gradle'
gradle = gradle_path.read_text()
gradle = gradle.replace('versionCode 10', 'versionCode 11', 1)
gradle = gradle.replace("versionName '0.10-native-capability-lab-stable-exact-menu'",
                        "versionName '0.11-native-capability-lab-stable-exact-drawer-search'", 1)
if 'versionCode 11' not in gradle or "0.11-native-capability-lab-stable-exact-drawer-search" not in gradle:
    raise SystemExit('version patch failed')
gradle_path.write_text(gradle)

plan_path = root / 'plans/default.json'
plan = json.loads(plan_path.read_text())
if plan.get('suite') == 'conversation_search_binding_v5_exact_menu':
    plan['suite'] = 'conversation_search_binding_v6_exact_drawer_search'
elif plan.get('suite') != 'conversation_search_binding_v6_exact_drawer_search':
    raise SystemExit('unexpected suite: ' + str(plan.get('suite')))
plan_path.write_text(json.dumps(plan, indent=2) + '\n')

ci_path = Path('.github/workflows/native-capability-lab.yml')
ci = ci_path.read_text()
if 'GLOBAL_SEARCH_DRAWER_SEARCH_EXACT_MATCHES' not in ci:
    anchor = "          grep -Fq 'GLOBAL_SEARCH_MENU_EXACT_MATCHES' \"$SVC\"\n"
    insert = anchor + "          grep -Fq 'GLOBAL_SEARCH_DRAWER_SEARCH_EXACT_MATCHES' \"$SVC\"\n          grep -Fq 'GLOBAL_SEARCH_POST_SEARCH_CLICK_CONTROL_CENSUS' \"$SVC\"\n          grep -Fq 'findUniqueExactSemanticAcrossRoots' \"$SVC\"\n"
    if anchor not in ci:
        raise SystemExit('CI grep anchor not found')
    ci = ci.replace(anchor, insert, 1)
ci = ci.replace("grep -Fq 'conversation_search_binding_v5_exact_menu' \"$PLAN\"",
                "grep -Fq 'conversation_search_binding_v6_exact_drawer_search' \"$PLAN\"", 1)
ci = ci.replace('Capability Lab v0.10 must contain exactly two ACTION_CLICK code sites',
                'Capability Lab v0.11 must contain exactly two ACTION_CLICK code sites', 1)
ci = ci.replace('Capability Lab v0.10 must contain exactly one Search ACTION_SET_TEXT site',
                'Capability Lab v0.11 must contain exactly one Search ACTION_SET_TEXT site', 1)
ci = ci.replace("assert 'versionCode 10' in gradle", "assert 'versionCode 11' in gradle", 1)
ci = ci.replace("assert \"versionName '0.10-native-capability-lab-stable-exact-menu'\" in gradle",
                "assert \"versionName '0.11-native-capability-lab-stable-exact-drawer-search'\" in gradle", 1)
ci = ci.replace("assert data['suite'] == 'conversation_search_binding_v5_exact_menu'",
                "assert data['suite'] == 'conversation_search_binding_v6_exact_drawer_search'", 1)
ci = ci.replace("versionCode='10' versionName='0.10-native-capability-lab-stable-exact-menu'",
                "versionCode='11' versionName='0.11-native-capability-lab-stable-exact-drawer-search'", 1)
for token in [
    'GLOBAL_SEARCH_DRAWER_SEARCH_EXACT_MATCHES',
    'GLOBAL_SEARCH_POST_SEARCH_CLICK_CONTROL_CENSUS',
    'findUniqueExactSemanticAcrossRoots',
    'conversation_search_binding_v6_exact_drawer_search',
    'versionCode 11',
    "0.11-native-capability-lab-stable-exact-drawer-search",
]:
    if token not in ci:
        raise SystemExit('CI patch missing ' + token)
ci_path.write_text(ci)
