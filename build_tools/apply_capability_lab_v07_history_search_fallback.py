import json
import re
from pathlib import Path

ROOT = Path("runtime_probes/native-capability-lab")
SVC = ROOT / "app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java"
MAIN = ROOT / "app/src/main/java/com/openai/controlplane/capabilitylab/MainActivity.java"
GRADLE = ROOT / "app/build.gradle"
PLAN = ROOT / "plans/default.json"
CI = Path(".github/workflows/native-capability-lab.yml")

svc = SVC.read_text()

old_entry = '''        if ("WAITING_GLOBAL_SEARCH_ENTRY".equals(state)) {
            if (isGlobalSearchScreen(root)) {
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 120L);
                return;
            }
            AccessibilityNodeInfo entry = findUniqueGlobalSearchEntry(root);
            if (entry == null) return;
            AccessibilityNodeInfo clickTarget = firstClickableAncestor(entry, 4);
            if (clickTarget == null) {
                failRun("GLOBAL_SEARCH_ENTRY_NOT_CLICKABLE");
                return;
            }
            LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
            boolean clicked = clickTarget.performAction(AccessibilityNodeInfo.ACTION_CLICK);
            LabStore.append(this, "GLOBAL_SEARCH_ENTRY ACTION_CLICK returned=" + clicked);
            if (!clicked) {
                failRun("GLOBAL_SEARCH_ENTRY_CLICK_FALSE");
                return;
            }
            handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 300L);
            return;
        }
'''
new_entry = '''        if ("WAITING_GLOBAL_SEARCH_ENTRY".equals(state)) {
            if (isGlobalSearchScreen(root)) {
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 120L);
                return;
            }
            AccessibilityNodeInfo entry = findUniqueGlobalSearchEntry(root);
            if (entry != null) {
                AccessibilityNodeInfo clickTarget = firstClickableAncestor(entry, 4);
                if (clickTarget == null) {
                    failRun("GLOBAL_SEARCH_ENTRY_NOT_CLICKABLE");
                    return;
                }
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                boolean clicked = clickTarget.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                LabStore.append(this, "GLOBAL_SEARCH_ENTRY ACTION_CLICK returned=" + clicked);
                if (!clicked) {
                    failRun("GLOBAL_SEARCH_ENTRY_CLICK_FALSE");
                    return;
                }
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 300L);
                return;
            }

            // Exact-build fallback: the same conversation module exposes the history drawer
            // (`chatgpt.history` / "Open conversation history") and a semantic Search chats
            // entry inside it. On the real-device v0.6 run the direct global-search control
            // was not present in the active conversation tree, so enter Search through the
            // official drawer instead of failing on an account/layout-specific visibility gap.
            AccessibilityNodeInfo historyEntry = findUniqueHistoryEntry(root);
            if (historyEntry == null) return;
            AccessibilityNodeInfo historyClick = firstClickableAncestor(historyEntry, 4);
            if (historyClick == null) {
                failRun("GLOBAL_SEARCH_HISTORY_ENTRY_NOT_CLICKABLE");
                return;
            }
            LabStore.setState(this, "WAITING_GLOBAL_SEARCH_DRAWER");
            boolean clickedHistory = historyClick.performAction(AccessibilityNodeInfo.ACTION_CLICK);
            LabStore.append(this, "GLOBAL_SEARCH_HISTORY_ENTRY ACTION_CLICK returned=" + clickedHistory);
            if (!clickedHistory) {
                failRun("GLOBAL_SEARCH_HISTORY_ENTRY_CLICK_FALSE");
                return;
            }
            handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 300L);
            return;
        }

        if ("WAITING_GLOBAL_SEARCH_DRAWER".equals(state)) {
            if (isGlobalSearchScreen(root)) {
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 120L);
                return;
            }
            if (!isHistoryDrawerScreen(root)) return;
            AccessibilityNodeInfo historySearch = findUniqueHistorySearchEntry(root);
            if (historySearch == null) return;
            AccessibilityNodeInfo historySearchClick = firstClickableAncestor(historySearch, 4);
            if (historySearchClick == null) {
                failRun("GLOBAL_SEARCH_HISTORY_SEARCH_NOT_CLICKABLE");
                return;
            }
            LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
            boolean clickedHistorySearch = historySearchClick.performAction(AccessibilityNodeInfo.ACTION_CLICK);
            LabStore.append(this, "GLOBAL_SEARCH_HISTORY_SEARCH ACTION_CLICK returned=" + clickedHistorySearch);
            if (!clickedHistorySearch) {
                failRun("GLOBAL_SEARCH_HISTORY_SEARCH_CLICK_FALSE");
                return;
            }
            handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 300L);
            return;
        }
'''
if old_entry not in svc:
    raise SystemExit("v0.7 entry anchor missing")
svc = svc.replace(old_entry, new_entry, 1)

old_field = '''        if ("WAITING_GLOBAL_SEARCH_FIELD".equals(state)) {
            if (!isGlobalSearchScreen(root)) return;
            AccessibilityNodeInfo field = findGlobalSearchField(root);
            if (field == null) return;
            Bundle args = new Bundle();
            args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, marker);
            LabStore.setState(this, "WAITING_GLOBAL_SEARCH_RESULT");
            boolean set = field.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args);
            LabStore.append(this, "GLOBAL_SEARCH_QUERY ACTION_SET_TEXT returned=" + set + " marker=" + marker);
            if (!set) {
                failRun("GLOBAL_SEARCH_SET_TEXT_FALSE");
                return;
            }
            handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 350L);
            return;
        }
'''
new_field = '''        if ("WAITING_GLOBAL_SEARCH_FIELD".equals(state)) {
            AccessibilityNodeInfo field;
            String surface;
            if (isGlobalSearchScreen(root)) {
                field = findGlobalSearchField(root);
                surface = "global";
            } else if (isHistoryDrawerScreen(root)) {
                field = findHistorySearchField(root);
                surface = "history";
            } else {
                return;
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
'''
if old_field not in svc:
    raise SystemExit("v0.7 field anchor missing")
svc = svc.replace(old_field, new_field, 1)

old_result_prefix = '''        if ("WAITING_GLOBAL_SEARCH_RESULT".equals(state)) {
            if (!isGlobalSearchScreen(root)) return;
            List<AccessibilityNodeInfo> markerNodes = new ArrayList<>();
            collectNonEditableMarkerNodes(root, marker, markerNodes, 0);
            if (markerNodes.isEmpty()) return;

            List<AccessibilityNodeInfo> resultTargets = new ArrayList<>();
            for (AccessibilityNodeInfo markerNode : markerNodes) {
                AccessibilityNodeInfo candidate = firstClickableAncestor(markerNode, 8);
                if (candidate != null) addUniqueNode(resultTargets, candidate);
            }
'''
new_result_prefix = '''        if ("WAITING_GLOBAL_SEARCH_RESULT".equals(state)) {
            boolean globalSurface = isGlobalSearchScreen(root);
            boolean historySurface = isHistoryDrawerScreen(root);
            if (!globalSurface && !historySurface) return;
            List<AccessibilityNodeInfo> markerNodes = new ArrayList<>();
            collectNonEditableMarkerNodes(root, marker, markerNodes, 0);

            List<AccessibilityNodeInfo> resultTargets = new ArrayList<>();
            for (AccessibilityNodeInfo markerNode : markerNodes) {
                AccessibilityNodeInfo candidate = firstClickableAncestor(markerNode, 8);
                if (candidate != null) addUniqueNode(resultTargets, candidate);
            }

            // The drawer's local history filter can match message content while rendering only
            // the conversation title. In that case the marker is not visible in the result row.
            // Accept a result only if the Search field still contains the exact synthetic marker
            // and exactly one official history item remains after filtering.
            String resultEvidence = markerNodes.isEmpty() ? "none" : "visible_marker";
            if (resultTargets.isEmpty() && historySurface && historySearchFieldEquals(root, marker)) {
                List<AccessibilityNodeInfo> historyItems = new ArrayList<>();
                collectSemanticNodes(root, "chatgpt.history.item.", historyItems, 0);
                for (AccessibilityNodeInfo item : historyItems) {
                    AccessibilityNodeInfo candidate = firstClickableAncestor(item, 4);
                    if (candidate != null) addUniqueNode(resultTargets, candidate);
                }
                if (!resultTargets.isEmpty()) resultEvidence = "unique_history_item_after_exact_marker_query";
            }
'''
if old_result_prefix not in svc:
    raise SystemExit("v0.7 result anchor missing")
svc = svc.replace(old_result_prefix, new_result_prefix, 1)

old_result_log = '''            LabStore.append(this, "GLOBAL_SEARCH_RESULT markerNodes=" + markerNodes.size()
                    + " clickableResults=" + resultTargets.size()
                    + " metadataNodes=" + metadata.nodes
'''
new_result_log = '''            LabStore.append(this, "GLOBAL_SEARCH_RESULT surface=" + (globalSurface ? "global" : "history")
                    + " evidence=" + resultEvidence
                    + " markerNodes=" + markerNodes.size()
                    + " clickableResults=" + resultTargets.size()
                    + " metadataNodes=" + metadata.nodes
'''
if old_result_log not in svc:
    raise SystemExit("v0.7 result log anchor missing")
svc = svc.replace(old_result_log, new_result_log, 1)

helper_anchor = '''    private boolean isGlobalSearchScreen(AccessibilityNodeInfo root) {
'''
helpers = '''    private boolean isHistoryDrawerScreen(AccessibilityNodeInfo root) {
        return containsSemantic(root, "chatgpt.history.drawer", 0)
                || containsSemantic(root, "Conversation history", 0)
                || containsSemantic(root, "chatgpt.history.content", 0);
    }

    private AccessibilityNodeInfo findUniqueHistoryEntry(AccessibilityNodeInfo root) {
        List<AccessibilityNodeInfo> labels = new ArrayList<>();
        collectSemanticNodes(root, "Open conversation history", labels, 0);
        if (labels.size() == 1) return labels.get(0);
        labels.clear();
        collectSemanticNodes(root, "chatgpt.history", labels, 0);
        List<AccessibilityNodeInfo> filtered = new ArrayList<>();
        for (AccessibilityNodeInfo n : labels) {
            String value = semanticValue(n).toLowerCase(Locale.US);
            if (!value.contains("history-search") && !value.contains("history.content")
                    && !value.contains("history.scroll") && !value.contains("history.item")) {
                filtered.add(n);
            }
        }
        return filtered.size() == 1 ? filtered.get(0) : null;
    }

    private AccessibilityNodeInfo findUniqueHistorySearchEntry(AccessibilityNodeInfo root) {
        List<AccessibilityNodeInfo> nodes = new ArrayList<>();
        collectSemanticNodes(root, "chatgpt.history-search", nodes, 0);
        if (nodes.size() == 1) return nodes.get(0);
        nodes.clear();
        collectSemanticNodes(root, "Search chats", nodes, 0);
        List<AccessibilityNodeInfo> clickable = new ArrayList<>();
        for (AccessibilityNodeInfo n : nodes) {
            if (!n.isEditable() && firstClickableAncestor(n, 4) != null) addUniqueNode(clickable, n);
        }
        return clickable.size() == 1 ? clickable.get(0) : null;
    }

    private AccessibilityNodeInfo findHistorySearchField(AccessibilityNodeInfo root) {
        List<AccessibilityNodeInfo> out = new ArrayList<>();
        collectHistorySearchFields(root, out, 0);
        return out.size() == 1 ? out.get(0) : null;
    }

    private void collectHistorySearchFields(AccessibilityNodeInfo n, List<AccessibilityNodeInfo> out, int depth) {
        if (n == null || depth > 40 || out.size() > 6) return;
        if (n.isEditable() && n.isVisibleToUser() && n.isEnabled()
                && hasAction(n, AccessibilityNodeInfo.ACTION_SET_TEXT)) {
            String semantic = semanticValue(n).toLowerCase(Locale.US);
            if (semantic.contains("search chats") || semantic.contains("chatgpt.history.search-toggle")
                    || semantic.contains("chatgpt.history-search")) {
                out.add(n);
            }
        }
        for (int i = 0; i < n.getChildCount(); i++) {
            collectHistorySearchFields(n.getChild(i), out, depth + 1);
        }
    }

    private boolean historySearchFieldEquals(AccessibilityNodeInfo root, String marker) {
        AccessibilityNodeInfo field = findHistorySearchField(root);
        if (field == null || marker == null) return false;
        CharSequence text = field.getText();
        return text != null && marker.equals(text.toString());
    }

'''
if helper_anchor not in svc:
    raise SystemExit("v0.7 helper anchor missing")
svc = svc.replace(helper_anchor, helpers + helper_anchor, 1)

# Add timeout-state diagnostics before a Global Search failure so the next report is actionable.
old_timeout = '''            } else {
                failRun(reason);
            }
'''
new_timeout = '''            } else {
                if (reason.startsWith("GLOBAL_SEARCH_BINDING_TIMEOUT")) {
                    AccessibilityNodeInfo root = getRootInActiveWindow();
                    if (root != null && isChatGptRoot(root)) {
                        String snapshot = normalizedTree(root, LabStore.marker(this), 500, 14);
                        LabStore.append(this, "GLOBAL_SEARCH_TIMEOUT_DIAGNOSTIC state=" + state
                                + " snapshot=" + LabStore.abbrev(snapshot, 22000));
                    } else {
                        LabStore.append(this, "GLOBAL_SEARCH_TIMEOUT_DIAGNOSTIC state=" + state + " root=unavailable");
                    }
                }
                failRun(reason);
            }
'''
if old_timeout not in svc:
    raise SystemExit("v0.7 timeout anchor missing")
svc = svc.replace(old_timeout, new_timeout, 1)

# Keep diagnostic labels visible but continue redacting unrelated user content.
old_redact = '''                || lower.equals("search chatgpt")
                || lower.contains("search chats")
                || lower.contains("voice")) {
'''
new_redact = '''                || lower.equals("search chatgpt")
                || lower.contains("search chats")
                || lower.contains("conversation history")
                || lower.equals("search results")
                || lower.equals("recent")
                || lower.equals("pinned")
                || lower.contains("apps and conversations")
                || lower.contains("voice")) {
'''
if old_redact not in svc:
    raise SystemExit("v0.7 redact anchor missing")
svc = svc.replace(old_redact, new_redact, 1)
SVC.write_text(svc)

# Stable package/signing identity is unchanged; only version metadata advances.
g = GRADLE.read_text()
g = g.replace("versionCode 6", "versionCode 7", 1)
g = g.replace("versionName '0.6-native-capability-lab-stable-global-search'",
              "versionName '0.7-native-capability-lab-stable-search-fallback'", 1)
if "versionCode 7" not in g:
    raise SystemExit("v0.7 gradle version update failed")
GRADLE.write_text(g)

plan = {
    "schema": 1,
    "suite": "conversation_search_binding_v2_history_fallback",
    "targetVersion": "1.2026.237",
    "targetSignerSha256": "b24f4bfbb3cf293f938703b9d87027c1102cc36dc4fa206910e08927db40473c",
    "steps": [
        {"op": "launch_prompt", "prompt": "Capability Lab official search binding proof. Reply with exactly this marker and no other text: {{marker}}"},
        {"op": "capture_tree", "label": "pre_send_draft_baseline", "timeoutMs": 8000},
        {"op": "semantic_send", "timeoutMs": 15000},
        {"op": "capture_tree", "label": "post_send_receipt", "timeoutMs": 8000},
        {"op": "wait", "ms": 8000},
        {"op": "global_search_binding", "timeoutMs": 45000},
        {"op": "return_lab"},
        {"op": "verify_candidates", "timeoutMs": 10000},
        {"op": "finish"},
    ],
}
PLAN.write_text(json.dumps(plan, indent=2) + "\n")

main = MAIN.read_text()
main = main.replace(
    "Stable v0.6 tests a production-faithful binding path through the official ChatGPT Global Search UI.",
    "Stable v0.7 tests a production-faithful binding path through official ChatGPT Search, with an exact-build Conversation History -> Search chats fallback when the direct Global Search control is not exposed in the active layout.",
    1,
)
main = main.replace("RUN OFFICIAL GLOBAL SEARCH BINDING PROOF", "RUN OFFICIAL SEARCH BINDING PROOF", 1)
main = main.replace("READY TO RUN — OFFICIAL GLOBAL SEARCH PROOF", "READY TO RUN — OFFICIAL SEARCH + HISTORY FALLBACK", 1)
MAIN.write_text(main)

ci = CI.read_text()
ci = ci.replace("conversation_search_binding_v1_official_ui", "conversation_search_binding_v2_history_fallback")
ci = ci.replace("versionCode 6", "versionCode 7")
ci = ci.replace("0.6-native-capability-lab-stable-global-search", "0.7-native-capability-lab-stable-search-fallback")
ci = ci.replace("Capability Lab v0.6 must contain exactly three bounded ACTION_CLICK sites",
                "Capability Lab v0.7 must contain exactly five bounded ACTION_CLICK sites")
ci = ci.replace("!= 3", "!= 5", 1)
ci = ci.replace("Capability Lab v0.6 must contain exactly one Global Search ACTION_SET_TEXT site",
                "Capability Lab v0.7 must contain exactly one Search ACTION_SET_TEXT site")
ci = ci.replace("assert data['steps'][4]['ms'] == 5000", "assert data['steps'][4]['ms'] == 8000")
ci = ci.replace("assert data['steps'][5]['timeoutMs'] == 30000", "assert data['steps'][5]['timeoutMs'] == 45000")
ci = ci.replace("grep -Fq 'GLOBAL_SEARCH_ENTRY ACTION_CLICK' \"$SVC\"",
                "grep -Fq 'GLOBAL_SEARCH_ENTRY ACTION_CLICK' \"$SVC\"\n          grep -Fq 'GLOBAL_SEARCH_HISTORY_ENTRY ACTION_CLICK' \"$SVC\"\n          grep -Fq 'GLOBAL_SEARCH_HISTORY_SEARCH ACTION_CLICK' \"$SVC\"\n          grep -Fq 'GLOBAL_SEARCH_TIMEOUT_DIAGNOSTIC' \"$SVC\"")
CI.write_text(ci)

# Final invariants.
svc = SVC.read_text()
assert 'WAITING_GLOBAL_SEARCH_DRAWER' in svc
assert 'Open conversation history' in svc
assert 'chatgpt.history-search' in svc
assert 'unique_history_item_after_exact_marker_query' in svc
assert 'GLOBAL_SEARCH_TIMEOUT_DIAGNOSTIC' in svc
assert svc.count('performAction(AccessibilityNodeInfo.ACTION_CLICK)') == 5
assert svc.count('performAction(AccessibilityNodeInfo.ACTION_SET_TEXT') == 1
assert 'dispatchGesture' not in svc
assert 'getBoundsInScreen' not in svc
assert 'GLOBAL_ACTION_' not in svc
