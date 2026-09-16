from pathlib import Path

root = Path('runtime_probes/native-capability-lab')
svc_path = root / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java'
gradle_path = root / 'app/build.gradle'
plan_path = root / 'plans/default.json'
main_path = root / 'app/src/main/java/com/openai/controlplane/capabilitylab/MainActivity.java'

s = svc_path.read_text()

old = '''        String[] aliases = new String[]{"Open sidebar", "Open navigation", "Open navigation menu", "Navigation menu", "Menu"};
        for (String alias : aliases) {
            List<AccessibilityNodeInfo> aliasNodes = new ArrayList<>();
            collectSemanticNodes(root, alias, aliasNodes, 0);
            if (aliasNodes.size() == 1) return aliasNodes.get(0);
        }
        return null;
    }
'''
new = '''        String[] aliases = new String[]{"Open sidebar", "Open navigation", "Open navigation menu", "Navigation menu", "Menu"};
        for (String alias : aliases) {
            List<AccessibilityNodeInfo> aliasNodes = new ArrayList<>();
            // Runtime v0.9 proved that substring matching is too broad for the generic
            // label "Menu": unrelated/redacted controls can contain that token and make
            // an otherwise unique official Menu look ambiguous. Navigation aliases are
            // therefore matched against the node's complete semantic value exactly.
            collectExactSemanticNodes(root, alias, aliasNodes, 0);
            if (aliasNodes.size() == 1) return aliasNodes.get(0);
        }
        return null;
    }
'''
assert old in s
s = s.replace(old, new, 1)

anchor = '''    private void collectSemanticNodes(AccessibilityNodeInfo n, String token, List<AccessibilityNodeInfo> out, int depth) {
        if (n == null || depth > 40 || out.size() > 8) return;
        if (semanticValue(n).toLowerCase(Locale.US).contains(token.toLowerCase(Locale.US))
                && n.isVisibleToUser() && n.isEnabled()) {
            out.add(n);
        }
        for (int i = 0; i < n.getChildCount(); i++) {
            collectSemanticNodes(n.getChild(i), token, out, depth + 1);
        }
    }
'''
helper = anchor + '''
    private void collectExactSemanticNodes(AccessibilityNodeInfo n, String exact,
                                           List<AccessibilityNodeInfo> out, int depth) {
        if (n == null || depth > 40 || out.size() > 8) return;
        String value = semanticValue(n).trim();
        if (value.equalsIgnoreCase(exact) && n.isVisibleToUser() && n.isEnabled()) {
            out.add(n);
        }
        for (int i = 0; i < n.getChildCount(); i++) {
            collectExactSemanticNodes(n.getChild(i), exact, out, depth + 1);
        }
    }
'''
assert anchor in s
s = s.replace(anchor, helper, 1)

# Add a bounded diagnostic at Search arm time so any future ambiguity is explicit.
old = '''        LabStore.append(this, "GLOBAL_SEARCH_ENTRY_CONTROL_CENSUS "
                + LabStore.abbrev(controlCensus(roots, 180), 14000));
'''
new = '''        LabStore.append(this, "GLOBAL_SEARCH_ENTRY_CONTROL_CENSUS "
                + LabStore.abbrev(controlCensus(roots, 180), 14000));
        LabStore.append(this, "GLOBAL_SEARCH_MENU_EXACT_MATCHES=" + countExactSemanticAcrossRoots(roots, "Menu"));
'''
assert old in s
s = s.replace(old, new, 1)

anchor2 = '''    private MarkerCounts countMarkerNodesAcrossRoots(List<AccessibilityNodeInfo> roots, String marker) {'''
helper2 = '''    private int countExactSemanticAcrossRoots(List<AccessibilityNodeInfo> roots, String exact) {
        List<AccessibilityNodeInfo> found = new ArrayList<>();
        for (AccessibilityNodeInfo root : roots) {
            List<AccessibilityNodeInfo> one = new ArrayList<>();
            collectExactSemanticNodes(root, exact, one, 0);
            for (AccessibilityNodeInfo n : one) addUniqueNode(found, n);
        }
        return found.size();
    }

'''
assert anchor2 in s
s = s.replace(anchor2, helper2 + anchor2, 1)

svc_path.write_text(s)

g = gradle_path.read_text()
assert 'versionCode 9' in g
assert "versionName '0.9-native-capability-lab-stable-menu-calibration'" in g
g = g.replace('versionCode 9', 'versionCode 10', 1)
g = g.replace("versionName '0.9-native-capability-lab-stable-menu-calibration'",
              "versionName '0.10-native-capability-lab-stable-exact-menu'", 1)
gradle_path.write_text(g)

p = plan_path.read_text()
assert 'conversation_search_binding_v4_menu_calibration' in p
p = p.replace('conversation_search_binding_v4_menu_calibration',
              'conversation_search_binding_v5_exact_menu', 1)
plan_path.write_text(p)

m = main_path.read_text()
assert 'Stable v0.9 uses the real-device Menu semantic discovered by v0.8 and expands the official Search proof' in m
m = m.replace('Stable v0.9 uses the real-device Menu semantic discovered by v0.8 and expands the official Search proof',
              'Stable v0.10 matches the real-device Menu semantic exactly (not by substring) and continues the official Search proof', 1)
main_path.write_text(m)
