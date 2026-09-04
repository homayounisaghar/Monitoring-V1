from pathlib import Path
import json

ROOT = Path('runtime_probes/native-capability-lab')
SVC = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java'
MAIN = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/MainActivity.java'
GRADLE = ROOT / 'app/build.gradle'
PLAN = ROOT / 'plans/default.json'

# ---- version -------------------------------------------------------------
g = GRADLE.read_text()
g = g.replace('versionCode 7', 'versionCode 8')
g = g.replace("versionName '0.7-native-capability-lab-stable-search-fallback'",
              "versionName '0.8-native-capability-lab-stable-window-semantics'")
GRADLE.write_text(g)

# ---- plan ----------------------------------------------------------------
p = json.loads(PLAN.read_text())
p['suite'] = 'conversation_search_binding_v3_window_semantics'
p['steps'][4]['ms'] = 8000
p['steps'][5]['timeoutMs'] = 35000
PLAN.write_text(json.dumps(p, indent=2) + '\n')

# ---- Accessibility: all-window semantic lookup + semantic census ---------
s = SVC.read_text()
if 'import android.view.accessibility.AccessibilityWindowInfo;\n' not in s:
    s = s.replace('import android.view.accessibility.AccessibilityNodeInfo;\n',
                  'import android.view.accessibility.AccessibilityNodeInfo;\nimport android.view.accessibility.AccessibilityWindowInfo;\n')

start = s.index('    private void tryGlobalSearchBinding(int expectedStep) {')
end = s.index('    private void opVerifyCandidates(JSONObject step, int stepIndex) {', start)
new_method = r'''    private void tryGlobalSearchBinding(int expectedStep) {
        if (!isCurrentStep(expectedStep)) return;
        List<AccessibilityNodeInfo> roots = chatGptRoots();
        if (roots.isEmpty()) return;
        String marker = LabStore.marker(this);
        if (marker.isEmpty()) {
            failRun("GLOBAL_SEARCH_MARKER_MISSING");
            return;
        }

        String state = LabStore.state(this);
        if ("WAITING_GLOBAL_SEARCH_ENTRY".equals(state)) {
            if (anyGlobalSearchScreen(roots)) {
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 120L);
                return;
            }

            AccessibilityNodeInfo entry = findUniqueGlobalSearchEntryAcrossRoots(roots);
            if (entry != null) {
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                if (!performBoundedNavigation(entry, "GLOBAL_SEARCH_ENTRY",
                        "Search chats, files, and projects", "Search ChatGPT")) {
                    failRun("GLOBAL_SEARCH_ENTRY_ACTION_FALSE");
                    return;
                }
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 300L);
                return;
            }

            AccessibilityNodeInfo historyEntry = findUniqueHistoryEntryAcrossRoots(roots);
            if (historyEntry == null) return;
            LabStore.setState(this, "WAITING_GLOBAL_SEARCH_DRAWER");
            if (!performBoundedNavigation(historyEntry, "GLOBAL_SEARCH_HISTORY_ENTRY",
                    "Open conversation history", "Open sidebar", "Open navigation", "Navigation menu")) {
                failRun("GLOBAL_SEARCH_HISTORY_ENTRY_ACTION_FALSE");
                return;
            }
            handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 300L);
            return;
        }

        if ("WAITING_GLOBAL_SEARCH_DRAWER".equals(state)) {
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

        if ("WAITING_GLOBAL_SEARCH_FIELD".equals(state)) {
            AccessibilityNodeInfo field = null;
            String surface = "";
            AccessibilityNodeInfo globalRoot = findGlobalSearchRoot(roots);
            if (globalRoot != null) {
                field = findGlobalSearchField(globalRoot);
                surface = "global";
            }
            if (field == null) {
                AccessibilityNodeInfo historyRoot = findHistoryDrawerRoot(roots);
                if (historyRoot != null) {
                    field = findHistorySearchField(historyRoot);
                    surface = "history";
                }
            }
            if (field == null) return;
            Bundle args = new Bundle();
            args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, marker);
            LabStore.setState(this, "WAITING_GLOBAL_SEARCH_RESULT");
            boolean set = field.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args);
            LabStore.append(this, "GLOBAL_SEARCH_QUERY ACTION_SET_TEXT returned=" + set
                    + " surface=" + surface + " marker=" + marker);
            if (!set) {
                failRun("GLOBAL_SEARCH_SET_TEXT_FALSE surface=" + surface);
                return;
            }
            handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 350L);
            return;
        }

        if ("WAITING_GLOBAL_SEARCH_RESULT".equals(state)) {
            AccessibilityNodeInfo surfaceRoot = findGlobalSearchRoot(roots);
            boolean globalSurface = surfaceRoot != null;
            if (surfaceRoot == null) surfaceRoot = findHistoryDrawerRoot(roots);
            boolean historySurface = !globalSurface && surfaceRoot != null;
            if (surfaceRoot == null) return;

            List<AccessibilityNodeInfo> markerNodes = new ArrayList<>();
            collectNonEditableMarkerNodes(surfaceRoot, marker, markerNodes, 0);
            List<AccessibilityNodeInfo> resultTargets = new ArrayList<>();
            for (AccessibilityNodeInfo markerNode : markerNodes) {
                AccessibilityNodeInfo candidate = firstActionClickAncestor(markerNode, 8);
                if (candidate != null) addUniqueNode(resultTargets, candidate);
            }

            String resultEvidence = markerNodes.isEmpty() ? "none" : "visible_marker";
            if (resultTargets.isEmpty() && historySurface && historySearchFieldEquals(surfaceRoot, marker)) {
                List<AccessibilityNodeInfo> historyItems = new ArrayList<>();
                collectSemanticNodes(surfaceRoot, "chatgpt.history.item.", historyItems, 0);
                for (AccessibilityNodeInfo item : historyItems) {
                    AccessibilityNodeInfo candidate = firstActionClickAncestor(item, 4);
                    if (candidate != null) addUniqueNode(resultTargets, candidate);
                }
                if (!resultTargets.isEmpty()) resultEvidence = "unique_history_item_after_exact_marker_query";
            }
            if (resultTargets.size() > 1) {
                failRun("GLOBAL_SEARCH_RESULT_NOT_UNIQUE count=" + resultTargets.size());
                return;
            }
            if (resultTargets.size() != 1) return;

            AccessibilityNodeInfo resultTarget = resultTargets.get(0);
            MetadataStats metadata = harvestAccessibilityMetadata(resultTarget);
            String snapshot = normalizedTree(resultTarget, marker, 220, 12);
            LabStore.append(this, "GLOBAL_SEARCH_RESULT surface=" + (globalSurface ? "global" : "history")
                    + " evidence=" + resultEvidence
                    + " markerNodes=" + markerNodes.size()
                    + " clickableResults=" + resultTargets.size()
                    + " metadataNodes=" + metadata.nodes
                    + " extras=" + metadata.extras
                    + " candidateMatches=" + metadata.candidateMatches
                    + " snapshot=" + LabStore.abbrev(snapshot, 16000));

            LabStore.setState(this, "WAITING_GLOBAL_SEARCH_REOPEN");
            if (!performBoundedNavigation(resultTarget, "GLOBAL_SEARCH_RESULT")) {
                failRun("GLOBAL_SEARCH_RESULT_ACTION_FALSE");
                return;
            }
            handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 300L);
            return;
        }

        if ("WAITING_GLOBAL_SEARCH_REOPEN".equals(state)) {
            if (anyGlobalSearchScreen(roots) || anyHistoryDrawerScreen(roots)) return;
            MarkerCounts counts = countMarkerNodesAcrossRoots(roots, marker);
            if (counts.editable != 0 || counts.nonEditable < 1) return;
            LabStore.append(this, "GLOBAL_SEARCH_REOPEN_VERIFIED markerEditable=" + counts.editable
                    + " markerNonEditable=" + counts.nonEditable);
            LabStore.markSearchBindingVerified(this);
            completeStep(expectedStep);
        }
    }

'''
s = s[:start] + new_method + s[end:]

# At arming time record a useful semantic census instead of waiting for a blind timeout.
old_arm = '''        LabStore.setState(this, "WAITING_GLOBAL_SEARCH_ENTRY");\n        LabStore.append(this, "GLOBAL_SEARCH_BINDING_ARMED marker=" + LabStore.marker(this));\n        armTimeout(step.optLong("timeoutMs", 30000L), "GLOBAL_SEARCH_BINDING_TIMEOUT", stepIndex);'''
new_arm = '''        LabStore.setState(this, "WAITING_GLOBAL_SEARCH_ENTRY");\n        List<AccessibilityNodeInfo> roots = chatGptRoots();\n        LabStore.append(this, "GLOBAL_SEARCH_BINDING_ARMED marker=" + LabStore.marker(this)\n                + " windows=" + roots.size());\n        LabStore.append(this, "GLOBAL_SEARCH_ENTRY_CONTROL_CENSUS "\n                + LabStore.abbrev(controlCensus(roots, 180), 14000));\n        armTimeout(step.optLong("timeoutMs", 35000L), "GLOBAL_SEARCH_BINDING_TIMEOUT", stepIndex);'''
if old_arm not in s:
    raise SystemExit('v0.8 arm anchor missing')
s = s.replace(old_arm, new_arm, 1)

# Replace timeout diagnostic with all-window control census + a compact active-root snapshot.
old_diag = '''                if (reason.startsWith("GLOBAL_SEARCH_BINDING_TIMEOUT")) {\n                    AccessibilityNodeInfo root = getRootInActiveWindow();\n                    if (root != null && isChatGptRoot(root)) {\n                        String snapshot = normalizedTree(root, LabStore.marker(this), 500, 14);\n                        LabStore.append(this, "GLOBAL_SEARCH_TIMEOUT_DIAGNOSTIC state=" + state\n                                + " snapshot=" + LabStore.abbrev(snapshot, 22000));\n                    } else {\n                        LabStore.append(this, "GLOBAL_SEARCH_TIMEOUT_DIAGNOSTIC state=" + state + " root=unavailable");\n                    }\n                }'''
new_diag = '''                if (reason.startsWith("GLOBAL_SEARCH_BINDING_TIMEOUT")) {\n                    List<AccessibilityNodeInfo> roots = chatGptRoots();\n                    String census = controlCensus(roots, 260);\n                    String snapshot = roots.isEmpty() ? "<no ChatGPT roots>"\n                            : normalizedTree(roots.get(0), LabStore.marker(this), 220, 10);\n                    LabStore.append(this, "GLOBAL_SEARCH_TIMEOUT_DIAGNOSTIC state=" + state\n                            + " windows=" + roots.size()\n                            + " controlCensus=" + LabStore.abbrev(census, 18000)\n                            + " activeSnapshot=" + LabStore.abbrev(snapshot, 8000));\n                }'''
if old_diag not in s:
    raise SystemExit('v0.8 timeout diagnostic anchor missing')
s = s.replace(old_diag, new_diag, 1)

# Insert all-window helpers and privacy-aware semantic census before history helpers.
anchor = '    private boolean isHistoryDrawerScreen(AccessibilityNodeInfo root) {\n'
if anchor not in s:
    raise SystemExit('v0.8 helper insertion anchor missing')
helpers = r'''    private List<AccessibilityNodeInfo> chatGptRoots() {
        List<AccessibilityNodeInfo> roots = new ArrayList<>();
        AccessibilityNodeInfo active = getRootInActiveWindow();
        addChatGptRoot(roots, active);
        try {
            List<AccessibilityWindowInfo> windows = getWindows();
            if (windows != null) {
                for (AccessibilityWindowInfo window : windows) {
                    if (window == null) continue;
                    AccessibilityNodeInfo root = null;
                    try { root = window.getRoot(); } catch (Throwable ignored) {}
                    addChatGptRoot(roots, root);
                }
            }
        } catch (Throwable t) {
            LabStore.append(this, "ACCESSIBILITY_WINDOWS_ERROR " + t.getClass().getSimpleName());
        }
        return roots;
    }

    private void addChatGptRoot(List<AccessibilityNodeInfo> roots, AccessibilityNodeInfo root) {
        if (root == null || !isChatGptRoot(root)) return;
        for (AccessibilityNodeInfo existing : roots) {
            if (existing.equals(root)) return;
        }
        roots.add(root);
    }

    private boolean anyGlobalSearchScreen(List<AccessibilityNodeInfo> roots) {
        return findGlobalSearchRoot(roots) != null;
    }

    private AccessibilityNodeInfo findGlobalSearchRoot(List<AccessibilityNodeInfo> roots) {
        for (AccessibilityNodeInfo root : roots) if (isGlobalSearchScreen(root)) return root;
        return null;
    }

    private boolean anyHistoryDrawerScreen(List<AccessibilityNodeInfo> roots) {
        return findHistoryDrawerRoot(roots) != null;
    }

    private AccessibilityNodeInfo findHistoryDrawerRoot(List<AccessibilityNodeInfo> roots) {
        for (AccessibilityNodeInfo root : roots) if (isHistoryDrawerScreen(root)) return root;
        return null;
    }

    private AccessibilityNodeInfo findUniqueGlobalSearchEntryAcrossRoots(List<AccessibilityNodeInfo> roots) {
        List<AccessibilityNodeInfo> found = new ArrayList<>();
        for (AccessibilityNodeInfo root : roots) {
            AccessibilityNodeInfo n = findUniqueGlobalSearchEntry(root);
            if (n != null) addUniqueNode(found, n);
        }
        return found.size() == 1 ? found.get(0) : null;
    }

    private AccessibilityNodeInfo findUniqueHistoryEntryAcrossRoots(List<AccessibilityNodeInfo> roots) {
        List<AccessibilityNodeInfo> found = new ArrayList<>();
        for (AccessibilityNodeInfo root : roots) {
            AccessibilityNodeInfo n = findUniqueHistoryEntry(root);
            if (n != null) addUniqueNode(found, n);
        }
        return found.size() == 1 ? found.get(0) : null;
    }

    private MarkerCounts countMarkerNodesAcrossRoots(List<AccessibilityNodeInfo> roots, String marker) {
        MarkerCounts total = new MarkerCounts();
        for (AccessibilityNodeInfo root : roots) {
            MarkerCounts one = countMarkerNodes(root, marker);
            total.editable += one.editable;
            total.nonEditable += one.nonEditable;
        }
        return total;
    }

    private AccessibilityNodeInfo firstActionClickAncestor(AccessibilityNodeInfo start, int maxUp) {
        AccessibilityNodeInfo n = start;
        for (int i = 0; n != null && i <= maxUp; i++) {
            if (n.isVisibleToUser() && n.isEnabled()
                    && hasAction(n, AccessibilityNodeInfo.ACTION_CLICK)) return n;
            n = n.getParent();
        }
        return null;
    }

    private boolean performBoundedNavigation(AccessibilityNodeInfo semanticNode, String logPrefix,
                                             String... allowedCustomLabels) {
        AccessibilityNodeInfo target = firstActionClickAncestor(semanticNode, 8);
        if (target != null) {
            boolean clicked = target.performAction(AccessibilityNodeInfo.ACTION_CLICK);
            LabStore.append(this, logPrefix + " ACTION_CLICK returned=" + clicked
                    + " targetClickable=" + target.isClickable());
            return clicked;
        }
        AccessibilityNodeInfo n = semanticNode;
        for (int up = 0; n != null && up <= 8; up++) {
            try {
                List<AccessibilityNodeInfo.AccessibilityAction> actions = n.getActionList();
                if (actions != null) {
                    for (AccessibilityNodeInfo.AccessibilityAction action : actions) {
                        CharSequence labelCs = action == null ? null : action.getLabel();
                        String label = labelCs == null ? "" : labelCs.toString().trim();
                        for (String allowed : allowedCustomLabels) {
                            if (!allowed.isEmpty() && allowed.equalsIgnoreCase(label)) {
                                boolean ok = n.performAction(action.getId());
                                LabStore.append(this, logPrefix + " CUSTOM_ACTION label=" + label
                                        + " id=" + action.getId() + " returned=" + ok);
                                return ok;
                            }
                        }
                    }
                }
            } catch (Throwable ignored) {}
            n = n.getParent();
        }
        LabStore.append(this, logPrefix + " NO_BOUNDED_ACTION semantic="
                + LabStore.abbrev(safeControlSemantic(semanticNode), 300));
        return false;
    }

    private String controlCensus(List<AccessibilityNodeInfo> roots, int maxNodes) {
        StringBuilder out = new StringBuilder();
        int[] count = {0};
        for (int i = 0; i < roots.size() && count[0] < maxNodes; i++) {
            out.append(" [window=").append(i).append(']');
            appendControlCensus(roots.get(i), out, count, maxNodes, 0);
        }
        return out.toString();
    }

    private void appendControlCensus(AccessibilityNodeInfo n, StringBuilder out, int[] count,
                                     int maxNodes, int depth) {
        if (n == null || count[0] >= maxNodes || depth > 40) return;
        count[0]++;
        String semantic = safeControlSemantic(n);
        boolean hasCustomActionLabel = hasNonEmptyActionLabel(n);
        if (n.isVisibleToUser() && n.isEnabled()
                && (hasAction(n, AccessibilityNodeInfo.ACTION_CLICK) || n.isClickable()
                || n.isEditable() || !semantic.isEmpty() || hasCustomActionLabel)) {
            out.append(" {d=").append(depth)
                    .append(" class=").append(shortClass(n.getClassName()))
                    .append(" click=").append(n.isClickable())
                    .append(" edit=").append(n.isEditable())
                    .append(" semantic=").append(semantic.isEmpty() ? "<none>" : semantic)
                    .append(" actions=").append(safeActionLabels(n))
                    .append('}');
        }
        for (int i = 0; i < n.getChildCount(); i++) {
            appendControlCensus(n.getChild(i), out, count, maxNodes, depth + 1);
        }
    }

    private boolean hasNonEmptyActionLabel(AccessibilityNodeInfo n) {
        try {
            List<AccessibilityNodeInfo.AccessibilityAction> actions = n.getActionList();
            if (actions != null) for (AccessibilityNodeInfo.AccessibilityAction a : actions) {
                if (a != null && a.getLabel() != null && a.getLabel().length() > 0) return true;
            }
        } catch (Throwable ignored) {}
        return false;
    }

    private String safeActionLabels(AccessibilityNodeInfo n) {
        StringBuilder b = new StringBuilder("[");
        try {
            List<AccessibilityNodeInfo.AccessibilityAction> actions = n.getActionList();
            if (actions != null) {
                for (AccessibilityNodeInfo.AccessibilityAction a : actions) {
                    if (a == null) continue;
                    if (b.length() > 1) b.append(',');
                    String label = a.getLabel() == null ? "" : a.getLabel().toString();
                    b.append(a.getId());
                    if (!label.isEmpty()) b.append(':').append(safeControlPart(label));
                }
            }
        } catch (Throwable ignored) {}
        return b.append(']').toString();
    }

    private String safeControlSemantic(AccessibilityNodeInfo n) {
        if (n == null) return "";
        StringBuilder b = new StringBuilder();
        appendSafeControlPart(b, n.getViewIdResourceName(), true);
        appendSafeControlPart(b, n.getContentDescription(), false);
        try { appendSafeControlPart(b, n.getHintText(), false); } catch (Throwable ignored) {}
        try { appendSafeControlPart(b, n.getPaneTitle(), false); } catch (Throwable ignored) {}
        try { appendSafeControlPart(b, n.getStateDescription(), false); } catch (Throwable ignored) {}
        String text = n.getText() == null ? "" : n.getText().toString();
        if (isControlLike(text)) appendSafeControlPart(b, text, false);
        try {
            List<AccessibilityNodeInfo.AccessibilityAction> actions = n.getActionList();
            if (actions != null) for (AccessibilityNodeInfo.AccessibilityAction a : actions) {
                if (a != null && a.getLabel() != null) appendSafeControlPart(b, a.getLabel(), false);
            }
        } catch (Throwable ignored) {}
        return b.toString();
    }

    private void appendSafeControlPart(StringBuilder b, Object value, boolean alwaysReveal) {
        if (value == null) return;
        String s = String.valueOf(value).replace('\n', ' ').replace('\r', ' ').trim();
        if (s.isEmpty()) return;
        String safe = alwaysReveal || isControlLike(s) ? LabStore.abbrev(s, 160) : "<redacted>";
        if (b.length() > 0) b.append('|');
        b.append(safe);
    }

    private String safeControlPart(String value) {
        if (value == null || value.isEmpty()) return "";
        return isControlLike(value) ? LabStore.abbrev(value, 120) : "<redacted>";
    }

    private boolean isControlLike(String value) {
        if (value == null) return false;
        String x = value.toLowerCase(Locale.US).trim();
        return x.contains("search") || x.contains("history") || x.contains("sidebar")
                || x.contains("navigation") || x.equals("menu") || x.equals("back")
                || x.equals("close") || x.equals("settings") || x.equals("more")
                || x.contains("new chat") || x.contains("model") || x.contains("voice")
                || x.contains("drawer") || x.contains("panel");
    }

'''
s = s.replace(anchor, helpers + anchor, 1)

# Broaden history opener only to explicit navigation semantics; never generic content rows.
old_hist_tail = '''        return filtered.size() == 1 ? filtered.get(0) : null;\n    }\n\n    private AccessibilityNodeInfo findUniqueHistorySearchEntry'''
new_hist_tail = '''        if (filtered.size() == 1) return filtered.get(0);\n        String[] aliases = new String[]{"Open sidebar", "Open navigation", "Open navigation menu", "Navigation menu"};\n        for (String alias : aliases) {\n            List<AccessibilityNodeInfo> aliasNodes = new ArrayList<>();\n            collectSemanticNodes(root, alias, aliasNodes, 0);\n            if (aliasNodes.size() == 1) return aliasNodes.get(0);\n        }\n        return null;\n    }\n\n    private AccessibilityNodeInfo findUniqueHistorySearchEntry'''
if old_hist_tail not in s:
    raise SystemExit('v0.8 history alias anchor missing')
s = s.replace(old_hist_tail, new_hist_tail, 1)

# Include custom action labels and extra control metadata in semantic matching.
old_sem = '''        appendSemanticPart(b, n.getContentDescription());\n        try { appendSemanticPart(b, n.getHintText()); } catch (Throwable ignored) {}\n        try { appendSemanticPart(b, n.getPaneTitle()); } catch (Throwable ignored) {}\n        return b.toString();'''
new_sem = '''        appendSemanticPart(b, n.getContentDescription());\n        try { appendSemanticPart(b, n.getHintText()); } catch (Throwable ignored) {}\n        try { appendSemanticPart(b, n.getPaneTitle()); } catch (Throwable ignored) {}\n        try { appendSemanticPart(b, n.getTooltipText()); } catch (Throwable ignored) {}\n        try { appendSemanticPart(b, n.getStateDescription()); } catch (Throwable ignored) {}\n        try {\n            List<AccessibilityNodeInfo.AccessibilityAction> actions = n.getActionList();\n            if (actions != null) for (AccessibilityNodeInfo.AccessibilityAction action : actions) {\n                if (action != null) appendSemanticPart(b, action.getLabel());\n            }\n        } catch (Throwable ignored) {}\n        return b.toString();'''
if old_sem not in s:
    raise SystemExit('v0.8 semanticValue anchor missing')
s = s.replace(old_sem, new_sem, 1)
SVC.write_text(s)

# ---- MainActivity: make state/actions visually obvious --------------------
m = MAIN.read_text()
if 'import android.content.res.ColorStateList;\n' not in m:
    m = m.replace('import android.content.Intent;\n', 'import android.content.Intent;\nimport android.content.res.ColorStateList;\n')
if 'import android.graphics.Color;\n' not in m:
    m = m.replace('import android.graphics.Typeface;\n', 'import android.graphics.Color;\nimport android.graphics.Typeface;\n')

m = m.replace('''    private Button runButton;\n    private Button copyButton;''', '''    private Button accessibilityButton;\n    private Button notificationButton;\n    private Button shizukuOpenButton;\n    private Button shizukuGrantButton;\n    private Button runButton;\n    private Button resetButton;\n    private Button copyButton;''')

old_desc_start = 'Stable v0.7 tests a production-faithful binding path through official ChatGPT Search, with an exact-build Conversation History -> Search chats fallback when the direct Global Search control is not exposed in the active layout.'
m = m.replace(old_desc_start,
              'Stable v0.8 expands the official Search proof across every ChatGPT accessibility window and exact semantic/custom-action labels, while keeping the Conversation History -> Search chats fallback. It also adds a privacy-redacted control census so any remaining mismatch is directly calibratable.')

old_buttons = '''        root.addView(button("Open Accessibility settings", v -> startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))));\n        root.addView(button("Open Notification Access settings", v -> {\n            try { startActivity(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)); }\n            catch (Throwable t) { startActivity(new Intent("android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS")); }\n        }));\n        root.addView(button("Open Shizuku (optional LAB diagnostics)", v -> openShizuku()));\n        root.addView(button("Grant Shizuku observer permission (optional)", v -> requestShizukuPermission()));\n\n        runButton = button("RUN OFFICIAL SEARCH BINDING PROOF", v -> startSuite());\n        root.addView(runButton);\n        root.addView(button("Reset Lab run state", v -> {\n            if ("RUNNING".equals(LabStore.status(this))) return;\n            LabStore.resetRun(this);\n            refreshUi();\n        }));\n        copyButton = button("COPY FINAL REPORT", v -> copyReport());\n        root.addView(copyButton);'''
new_buttons = '''        accessibilityButton = button("Accessibility", v -> startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));\n        root.addView(accessibilityButton);\n        notificationButton = button("Notification Access", v -> {\n            try { startActivity(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)); }\n            catch (Throwable t) { startActivity(new Intent("android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS")); }\n        });\n        root.addView(notificationButton);\n        shizukuOpenButton = button("Optional Shizuku diagnostics", v -> openShizuku());\n        root.addView(shizukuOpenButton);\n        shizukuGrantButton = button("Optional Shizuku permission", v -> requestShizukuPermission());\n        root.addView(shizukuGrantButton);\n\n        runButton = button("RUN SEARCH BINDING PROOF", v -> startSuite());\n        root.addView(runButton);\n        resetButton = button("Reset Lab run state", v -> {\n            if ("RUNNING".equals(LabStore.status(this))) return;\n            LabStore.resetRun(this);\n            refreshUi();\n        });\n        root.addView(resetButton);\n        copyButton = button("COPY FINAL REPORT", v -> copyReport());\n        root.addView(copyButton);'''
if old_buttons not in m:
    raise SystemExit('v0.8 MainActivity buttons anchor missing')
m = m.replace(old_buttons, new_buttons, 1)

# Add button/banner styling helpers before openShizuku.
style_anchor = '    private void openShizuku() {\n'
styles = r'''    private static final int GREEN = Color.rgb(46, 125, 50);
    private static final int BLUE = Color.rgb(21, 101, 192);
    private static final int AMBER = Color.rgb(239, 108, 0);
    private static final int RED = Color.rgb(198, 40, 40);
    private static final int GRAY = Color.rgb(84, 110, 122);

    private void styleButton(Button b, String text, int color, boolean enabled) {
        if (b == null) return;
        b.setText(text);
        b.setEnabled(enabled);
        b.setBackgroundTintList(ColorStateList.valueOf(color));
        b.setTextColor(Color.WHITE);
    }

    private void styleBanner(String text, int color) {
        if (runBanner == null) return;
        runBanner.setText(text);
        runBanner.setTextColor(Color.WHITE);
        runBanner.setBackgroundColor(color);
    }

'''
if style_anchor not in m:
    raise SystemExit('v0.8 MainActivity style insertion anchor missing')
m = m.replace(style_anchor, styles + style_anchor, 1)

# Replace banner block with colored states.
banner_start = m.index('        if (runBanner != null) {')
banner_end = m.index('\n\n        StringBuilder b = new StringBuilder();', banner_start)
new_banner = r'''        if (!exact) {
            styleBanner("BLOCKED — ChatGPT build mismatch", RED);
        } else if (!aLive || !nLive) {
            styleBanner("SETUP REQUIRED — follow the BLUE button", AMBER);
        } else if (starting) {
            styleBanner("STARTING SEARCH PROOF…", BLUE);
        } else if (running) {
            styleBanner("TEST RUNNING — step " + LabStore.step(this) + "\nDo not operate ChatGPT.", AMBER);
        } else if (finished && runStatus.startsWith("PASS")) {
            styleBanner("✓ TEST COMPLETE — PASS\nCOPY FINAL REPORT is GREEN.", GREEN);
        } else if (finished && runStatus.startsWith("INCONCLUSIVE")) {
            styleBanner("TEST COMPLETE — INCONCLUSIVE\nCOPY FINAL REPORT is GREEN.", AMBER);
        } else if (finished) {
            styleBanner("TEST COMPLETE — " + runStatus + "\nCOPY FINAL REPORT is GREEN.", RED);
        } else {
            styleBanner("READY TO RUN — press the BLUE RUN button", BLUE);
        }'''
m = m[:banner_start] + new_banner + m[banner_end:]

# Insert state-driven button colors immediately before status.setText.
status_anchor = '        status.setText(b.toString());\n\n        String r = LabStore.report(this);'
button_styles = r'''        boolean shizukuReady = LabShizukuObserver.permissionGranted();
        boolean nextAccessibility = exact && !aLive;
        boolean nextNotification = exact && aLive && !nLive;
        boolean readyToRun = exact && aLive && nLive && idle && !starting;

        styleButton(accessibilityButton,
                aLive ? "✓ Accessibility enabled" : "Enable Accessibility",
                aLive ? GREEN : (nextAccessibility ? BLUE : GRAY), true);
        styleButton(notificationButton,
                nLive ? "✓ Notification Access enabled" : "Enable Notification Access",
                nLive ? GREEN : (nextNotification ? BLUE : GRAY), true);
        styleButton(shizukuOpenButton,
                shizukuReady ? "✓ Optional Shizuku observer ready" : "Optional: Open Shizuku diagnostics",
                shizukuReady ? GREEN : GRAY, true);
        styleButton(shizukuGrantButton,
                shizukuReady ? "✓ Optional Shizuku permission granted" : "Optional: Grant Shizuku permission",
                shizukuReady ? GREEN : GRAY, true);
        styleButton(runButton,
                running ? "TEST RUNNING…" : "RUN SEARCH BINDING PROOF",
                readyToRun ? BLUE : GRAY, readyToRun);
        styleButton(resetButton,
                finished ? "Reset completed run" : "Reset Lab run state",
                finished ? AMBER : GRAY, !running && !starting);
        styleButton(copyButton,
                finished ? "COPY FINAL REPORT" : "COPY FINAL REPORT (after test)",
                finished ? GREEN : GRAY, finished);

        status.setText(b.toString());

        String r = LabStore.report(this);'''
if status_anchor not in m:
    raise SystemExit('v0.8 MainActivity status anchor missing')
m = m.replace(status_anchor, button_styles, 1)

# Remove old enable toggles; styleButton now owns enable state.
m = m.replace('        if (runButton != null) runButton.setEnabled(exact && aLive && nLive && idle && !starting);\n        if (copyButton != null) copyButton.setEnabled(finished);\n', '')
MAIN.write_text(m)

# ---- invariants ----------------------------------------------------------
s = SVC.read_text()
m = MAIN.read_text()
g = GRADLE.read_text()
p = PLAN.read_text()
assert 'versionCode 8' in g
assert "0.8-native-capability-lab-stable-window-semantics" in g
assert 'conversation_search_binding_v3_window_semantics' in p
assert 'chatGptRoots()' in s
assert 'GLOBAL_SEARCH_ENTRY_CONTROL_CENSUS' in s
assert 'Open sidebar' in s
assert 'getActionList()' in s
assert 'performBoundedNavigation' in s
assert 'styleButton(accessibilityButton' in m
assert 'READY TO RUN — press the BLUE RUN button' in m
assert 'ColorStateList' in m
