from pathlib import Path

root = Path('runtime_probes/native-capability-lab')
svc_path = root / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java'
gradle_path = root / 'app/build.gradle'
plan_path = root / 'plans/default.json'
main_path = root / 'app/src/main/java/com/openai/controlplane/capabilitylab/MainActivity.java'
ci_path = Path('.github/workflows/native-capability-lab.yml')

s = svc_path.read_text()

old = '''            if (!performBoundedNavigation(historyEntry, "GLOBAL_SEARCH_HISTORY_ENTRY",
                    "Open conversation history", "Open sidebar", "Open navigation", "Navigation menu")) {'''
new = '''            if (!performBoundedNavigation(historyEntry, "GLOBAL_SEARCH_HISTORY_ENTRY",
                    "Open conversation history", "Open sidebar", "Open navigation", "Open navigation menu", "Navigation menu", "Menu")) {'''
assert old in s
s = s.replace(old, new, 1)

old = '''        String[] aliases = new String[]{"Open sidebar", "Open navigation", "Open navigation menu", "Navigation menu"};'''
new = '''        String[] aliases = new String[]{"Open sidebar", "Open navigation", "Open navigation menu", "Navigation menu", "Menu"};'''
assert old in s
s = s.replace(old, new, 1)

old = '''        if ("WAITING_GLOBAL_SEARCH_DRAWER".equals(state)) {
            if (anyGlobalSearchScreen(roots)) {
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 120L);
                return;
            }
            AccessibilityNodeInfo historyRoot = findHistoryDrawerRoot(roots);
            if (historyRoot == null) return;

            // Some exact-build layouts expose the editable Search chats field immediately
            // when the drawer opens; do not require a redundant Search toggle in that case.
            AccessibilityNodeInfo alreadyVisibleField = findHistorySearchField(historyRoot);
            if (alreadyVisibleField != null) {
                LabStore.append(this, "GLOBAL_SEARCH_HISTORY_FIELD already_visible=true");
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 80L);
                return;
            }

            AccessibilityNodeInfo historySearch = findUniqueHistorySearchEntry(historyRoot);
            if (historySearch == null) return;
            LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
            if (!performBoundedNavigation(historySearch, "GLOBAL_SEARCH_HISTORY_SEARCH",
                    "Search chats", "Search conversations")) {
                failRun("GLOBAL_SEARCH_HISTORY_SEARCH_ACTION_FALSE");
                return;
            }
            handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 300L);
            return;
        }
'''
new = '''        if ("WAITING_GLOBAL_SEARCH_DRAWER".equals(state)) {
            if (anyGlobalSearchScreen(roots)) {
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 120L);
                return;
            }

            // v0.8 runtime exposed the real conversation opener as a visible semantic child
            // labelled exactly "Menu" with ACTION_CLICK on its parent. Once that official
            // menu is opened, do not require the drawer root itself to expose the static
            // `chatgpt.history.drawer` identifier: look directly for first-party Search
            // controls/fields across the ChatGPT windows.
            AccessibilityNodeInfo directSearch = findUniqueGlobalSearchEntryAcrossRoots(roots);
            if (directSearch != null) {
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                if (!performBoundedNavigation(directSearch, "GLOBAL_SEARCH_DRAWER_DIRECT_SEARCH",
                        "Search chats, files, and projects", "Search ChatGPT")) {
                    failRun("GLOBAL_SEARCH_DRAWER_DIRECT_SEARCH_ACTION_FALSE");
                    return;
                }
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 300L);
                return;
            }

            AccessibilityNodeInfo alreadyVisibleField = findHistorySearchFieldAcrossRoots(roots);
            if (alreadyVisibleField != null) {
                LabStore.append(this, "GLOBAL_SEARCH_HISTORY_FIELD already_visible=true source=across_roots");
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 80L);
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
        }
'''
assert old in s
s = s.replace(old, new, 1)

old = '''            if (field == null) {
                AccessibilityNodeInfo historyRoot = findHistoryDrawerRoot(roots);
                if (historyRoot != null) {
                    field = findHistorySearchField(historyRoot);
                    surface = "history";
                }
            }
'''
new = '''            if (field == null) {
                field = findHistorySearchFieldAcrossRoots(roots);
                if (field != null) surface = "history";
            }
'''
assert old in s
s = s.replace(old, new, 1)

old = '''            AccessibilityNodeInfo surfaceRoot = findGlobalSearchRoot(roots);
            boolean globalSurface = surfaceRoot != null;
            if (surfaceRoot == null) surfaceRoot = findHistoryDrawerRoot(roots);
            boolean historySurface = !globalSurface && surfaceRoot != null;
            if (surfaceRoot == null) return;
'''
new = '''            AccessibilityNodeInfo surfaceRoot = findGlobalSearchRoot(roots);
            boolean globalSurface = surfaceRoot != null;
            if (surfaceRoot == null) surfaceRoot = findRootWithHistorySearchFieldEquals(roots, marker);
            if (surfaceRoot == null) surfaceRoot = findHistoryDrawerRoot(roots);
            boolean historySurface = !globalSurface && surfaceRoot != null;
            if (surfaceRoot == null) return;
'''
assert old in s
s = s.replace(old, new, 1)

anchor = '''    private MarkerCounts countMarkerNodesAcrossRoots(List<AccessibilityNodeInfo> roots, String marker) {'''
helper = '''    private AccessibilityNodeInfo findUniqueHistorySearchEntryAcrossRoots(List<AccessibilityNodeInfo> roots) {
        List<AccessibilityNodeInfo> found = new ArrayList<>();
        for (AccessibilityNodeInfo root : roots) {
            AccessibilityNodeInfo n = findUniqueHistorySearchEntry(root);
            if (n != null) addUniqueNode(found, n);
        }
        return found.size() == 1 ? found.get(0) : null;
    }

    private AccessibilityNodeInfo findHistorySearchFieldAcrossRoots(List<AccessibilityNodeInfo> roots) {
        List<AccessibilityNodeInfo> found = new ArrayList<>();
        for (AccessibilityNodeInfo root : roots) {
            AccessibilityNodeInfo n = findHistorySearchField(root);
            if (n != null) addUniqueNode(found, n);
        }
        return found.size() == 1 ? found.get(0) : null;
    }

    private AccessibilityNodeInfo findRootWithHistorySearchFieldEquals(List<AccessibilityNodeInfo> roots, String marker) {
        AccessibilityNodeInfo match = null;
        for (AccessibilityNodeInfo root : roots) {
            if (!historySearchFieldEquals(root, marker)) continue;
            if (match != null && !match.equals(root)) return null;
            match = root;
        }
        return match;
    }

'''
assert anchor in s
s = s.replace(anchor, helper + anchor, 1)
svc_path.write_text(s)

g = gradle_path.read_text()
assert 'versionCode 8' in g
assert "versionName '0.8-native-capability-lab-stable-window-semantics'" in g
g = g.replace('versionCode 8', 'versionCode 9', 1)
g = g.replace("versionName '0.8-native-capability-lab-stable-window-semantics'",
              "versionName '0.9-native-capability-lab-stable-menu-calibration'", 1)
gradle_path.write_text(g)

p = plan_path.read_text()
assert 'conversation_search_binding_v3_window_semantics' in p
p = p.replace('conversation_search_binding_v3_window_semantics',
              'conversation_search_binding_v4_menu_calibration', 1)
plan_path.write_text(p)

m = main_path.read_text()
assert 'Stable v0.8 expands the official Search proof' in m
m = m.replace('Stable v0.8 expands the official Search proof',
              'Stable v0.9 uses the real-device Menu semantic discovered by v0.8 and expands the official Search proof', 1)
main_path.write_text(m)

c = ci_path.read_text()
needle = "          grep -Fq 'Open sidebar' \"$SVC\"\n"
assert needle in c
c = c.replace(needle, needle +
              "          grep -Fq '\"Menu\"' \"$SVC\"\n" +
              "          grep -Fq 'findHistorySearchFieldAcrossRoots' \"$SVC\"\n" +
              "          grep -Fq 'findUniqueHistorySearchEntryAcrossRoots' \"$SVC\"\n", 1)
c = c.replace('conversation_search_binding_v3_window_semantics', 'conversation_search_binding_v4_menu_calibration')
c = c.replace('Capability Lab v0.8 must contain exactly two ACTION_CLICK code sites',
              'Capability Lab v0.9 must contain exactly two ACTION_CLICK code sites')
c = c.replace('Capability Lab v0.8 must contain exactly one Search ACTION_SET_TEXT site',
              'Capability Lab v0.9 must contain exactly one Search ACTION_SET_TEXT site')
c = c.replace("assert 'versionCode 8' in gradle", "assert 'versionCode 9' in gradle")
c = c.replace("assert \"versionName '0.8-native-capability-lab-stable-window-semantics'\" in gradle",
              "assert \"versionName '0.9-native-capability-lab-stable-menu-calibration'\" in gradle")
c = c.replace("versionCode='8' versionName='0.8-native-capability-lab-stable-window-semantics'",
              "versionCode='9' versionName='0.9-native-capability-lab-stable-menu-calibration'")
ci_path.write_text(c)
