from pathlib import Path
import json
import re

ROOT = Path('runtime_probes/native-capability-lab')
SVC = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java'
STORE = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabStore.java'
MAIN = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/MainActivity.java'
PLAN_LOADER = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/PlanLoader.java'
PLAN = ROOT / 'plans/default.json'
BUILD = ROOT / 'app/build.gradle'
CI = Path('.github/workflows/native-capability-lab.yml')

OLD_SUITE = 'conversation_history_binding_v12_fresh_recent_reopen'
NEW_SUITE = 'conversation_history_accessibility_binding_v13_static_first'
NEW_VERSION_NAME = '0.18-native-capability-lab-stable-history-a11y-boundary'
KNOWN_CALIBRATION_MARKER = 'LAB_CID_9FC96C5A35E04E5B'


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if old not in text:
        raise SystemExit(f'anchor missing in {path}: {old[:160]!r}')
    path.write_text(text.replace(old, new, 1))


def regex_replace_once(path: Path, pattern: str, repl: str, flags=0) -> None:
    text = path.read_text()
    new, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'regex anchor missing/ambiguous in {path}: {pattern}')
    path.write_text(new)


# ---------- LabStore: calibration state + pre-fresh History baseline ----------
replace_once(
    STORE,
    '''                .putBoolean("historyBindingVerified", false)\n                .putString("historyCandidateTitle", "")\n                .putString("historyVerifiedTitle", "")\n                .putString("candidates", "")\n''',
    '''                .putBoolean("historyBindingVerified", false)\n                .putString("historyCandidateTitle", "")\n                .putString("historyVerifiedTitle", "")\n                .putBoolean("calibrationMode", false)\n                .putString("calibrationVerifiedId", "")\n                .putString("historyBaselineItemIds", "")\n                .putString("freshBoundaryItemId", "")\n                .putString("candidates", "")\n''')
replace_once(
    STORE,
    '''    static String historyVerifiedTitle(Context c) { return p(c).getString("historyVerifiedTitle", ""); }\n    static int candidateIndex(Context c) { return p(c).getInt("candidateIndex", 0); }\n''',
    '''    static String historyVerifiedTitle(Context c) { return p(c).getString("historyVerifiedTitle", ""); }\n    static boolean calibrationMode(Context c) { return p(c).getBoolean("calibrationMode", false); }\n    static String calibrationVerifiedId(Context c) { return p(c).getString("calibrationVerifiedId", ""); }\n    static String historyBaselineItemIds(Context c) { return p(c).getString("historyBaselineItemIds", ""); }\n    static String freshBoundaryItemId(Context c) { return p(c).getString("freshBoundaryItemId", ""); }\n    static int candidateIndex(Context c) { return p(c).getInt("candidateIndex", 0); }\n''')
replace_once(
    STORE,
    '''    static void setHistoryCandidateTitle(Context c, String value) {\n        p(c).edit().putString("historyCandidateTitle", value == null ? "" : value).apply();\n    }\n''',
    '''    static void setHistoryCandidateTitle(Context c, String value) {\n        p(c).edit().putString("historyCandidateTitle", value == null ? "" : value).apply();\n    }\n    static void setCalibrationMode(Context c, boolean value) { p(c).edit().putBoolean("calibrationMode", value).apply(); }\n    static void setHistoryBaselineItemIds(Context c, String value) {\n        p(c).edit().putString("historyBaselineItemIds", value == null ? "" : value).apply();\n    }\n    static void setFreshBoundaryItemId(Context c, String value) {\n        p(c).edit().putString("freshBoundaryItemId", value == null ? "" : value).apply();\n    }\n''')
replace_once(
    STORE,
    '''    static synchronized void clearCandidates(Context c) {\n        p(c).edit().putString("candidates", "").putInt("candidateIndex", 0).commit();\n        append(c, "CANDIDATES_CLEARED scope=history_selected_row");\n    }\n\n    static synchronized void markVerified(Context c, String id) {\n''',
    '''    static synchronized void clearCandidates(Context c) {\n        p(c).edit().putString("candidates", "").putInt("candidateIndex", 0).commit();\n        append(c, "CANDIDATES_CLEARED scope=history_selected_row");\n    }\n\n    static synchronized void markCalibrationVerified(Context c, String id) {\n        String safe = id == null ? "" : id.trim();\n        p(c).edit().putString("calibrationVerifiedId", safe).commit();\n        append(c, "CALIBRATION_VERIFIED_CONVERSATION_ID=" + safe);\n    }\n\n    static synchronized void resetAfterCalibration(Context c) {\n        String baseline = historyBaselineItemIds(c);\n        String calibrated = calibrationVerifiedId(c);\n        append(c, "CALIBRATION_PHASE_COMPLETE verifiedId=" + abbrev(calibrated, 96)\n                + " baselineItemIds=" + (baseline.isEmpty() ? 0 : baseline.split("\\\\n").length));\n        p(c).edit()\n                .putString("marker", "")\n                .putBoolean("writeClaimed", false)\n                .putBoolean("sendConfirmed", false)\n                .putLong("sendConfirmedAtMs", 0L)\n                .putBoolean("searchBindingVerified", false)\n                .putBoolean("historyBindingVerified", false)\n                .putString("historyCandidateTitle", "")\n                .putString("historyVerifiedTitle", "")\n                .putBoolean("calibrationMode", false)\n                .putString("freshBoundaryItemId", "")\n                .putString("candidates", "")\n                .putInt("candidateIndex", 0)\n                .putString("verifiedConversationId", "")\n                .commit();\n        append(c, "FRESH_PHASE_RESET preservedHistoryBaseline=true");\n    }\n\n    static synchronized void markVerified(Context c, String id) {\n''')
replace_once(
    STORE,
    '''                + " historyBinding=" + historyBindingVerified(c)\n                + " historyTitle=" + historyVerifiedTitle(c)\n                + " sinceSendMs=" + sinceSendMs(c)\n''',
    '''                + " historyBinding=" + historyBindingVerified(c)\n                + " historyTitle=" + historyVerifiedTitle(c)\n                + " calibrationId=" + calibrationVerifiedId(c)\n                + " freshBoundaryItem=" + abbrev(freshBoundaryItemId(c), 80)\n                + " sinceSendMs=" + sinceSendMs(c)\n''')


# ---------- Service: explicit APK-derived History accessibility boundary ----------
replace_once(
    SVC,
    '''    private static final int MAX_VERIFY_CANDIDATES = 8;\n    private static final int MAX_METADATA_NODES = 1400;\n''',
    '''    private static final int MAX_VERIFY_CANDIDATES = 8;\n    private static final int MAX_METADATA_NODES = 1400;\n    private static final String HISTORY_ITEM_PREFIX = "chatgpt.history.item.";\n    private static final String HISTORY_ACTIONS_PREFIX = "chatgpt.history.actions.";\n''')
replace_once(
    SVC,
    '''        } else if ("WAITING_VERIFY_CANDIDATE".equals(state)) {\n            tryVerifyCandidate(expectedStep);\n        } else if (state.startsWith("WAITING_HISTORY_RECENT_")) {\n''',
    '''        } else if ("WAITING_VERIFY_CANDIDATE".equals(state)) {\n            tryVerifyCandidate(expectedStep);\n        } else if (state.startsWith("WAITING_HISTORY_BOUNDARY_CALIBRATION_")) {\n            tryHistoryBoundaryCalibration(expectedStep);\n        } else if (state.startsWith("WAITING_HISTORY_RECENT_")) {\n''')
replace_once(
    SVC,
    '''                case "history_recent_binding":\n                    opHistoryRecentBinding(step, i);\n                    break;\n''',
    '''                case "history_boundary_calibration":\n                    opHistoryBoundaryCalibration(step, i);\n                    break;\n                case "reset_after_calibration":\n                    LabStore.resetAfterCalibration(this);\n                    completeStep(i);\n                    break;\n                case "history_recent_binding":\n                    opHistoryRecentBinding(step, i);\n                    break;\n''')

calibration_methods = r'''    private void opHistoryBoundaryCalibration(JSONObject step, int stepIndex) {
        if (!isCurrentStep(stepIndex)) return;
        LabStore.clearCandidates(this);
        LabStore.setCalibrationMode(this, true);
        LabStore.setState(this, "WAITING_HISTORY_BOUNDARY_CALIBRATION_OPEN");
        LabStore.append(this, "HISTORY_BOUNDARY_CALIBRATION_ARMED knownMarkerVerified="
                + LabStore.searchBindingVerified(this) + " marker=" + LabStore.marker(this));
        armTimeout(step.optLong("timeoutMs", 12000L), "HISTORY_BOUNDARY_CALIBRATION_TIMEOUT", stepIndex);
        handler.postDelayed(() -> tryHistoryBoundaryCalibration(stepIndex), 200L);
    }

    private void tryHistoryBoundaryCalibration(int expectedStep) {
        if (!isCurrentStep(expectedStep)) return;
        String state = LabStore.state(this);
        if (!state.startsWith("WAITING_HISTORY_BOUNDARY_CALIBRATION_")) return;
        List<AccessibilityNodeInfo> roots = chatGptRoots();
        if (roots.isEmpty()) return;

        if (!(isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots))) {
            if ("WAITING_HISTORY_BOUNDARY_CALIBRATION_WAIT_DRAWER".equals(state)) return;
            AccessibilityNodeInfo historyEntry = findUniqueHistoryEntryAcrossRoots(roots);
            if (historyEntry == null) return;
            LabStore.setState(this, "WAITING_HISTORY_BOUNDARY_CALIBRATION_WAIT_DRAWER");
            if (!performBoundedNavigation(historyEntry, "HISTORY_BOUNDARY_CALIBRATION_OPEN",
                    "Open conversation history", "Open sidebar", "Open navigation",
                    "Open navigation menu", "Navigation menu", "Menu")) {
                failRun("HISTORY_BOUNDARY_CALIBRATION_OPEN_ACTION_FALSE");
                return;
            }
            handler.postDelayed(() -> tryHistoryBoundaryCalibration(expectedStep), 280L);
            return;
        }

        List<String> baselineIds = historyBoundaryItemIds(roots);
        LabStore.setHistoryBaselineItemIds(this, joinLines(baselineIds));
        recordHistoryBoundaryEvidence("known_baseline", roots);

        List<AccessibilityNodeInfo> rows = historyConversationRows(roots);
        AccessibilityNodeInfo currentRow = uniqueStructurallyCurrentHistoryRow(rows);
        if (LabStore.searchBindingVerified(this) && currentRow != null) {
            MetadataStats stats = harvestAccessibilityMetadata(currentRow);
            String rowTree = normalizedTree(currentRow, LabStore.marker(this), 180, 8);
            LabStore.append(this, "HISTORY_BOUNDARY_CALIBRATION_ROW correlatedBy=unique_selected_or_focused"
                    + " viewId=" + LabStore.abbrev(firstHistoryItemViewId(currentRow), 220)
                    + " metadataNodes=" + stats.nodes
                    + " extras=" + stats.extras
                    + " candidateMatches=" + stats.candidateMatches
                    + " rowTree=" + LabStore.abbrev(rowTree, 12000));
        } else {
            LabStore.append(this, "HISTORY_BOUNDARY_CALIBRATION_NO_CORRELATED_ROW knownMarkerVerified="
                    + LabStore.searchBindingVerified(this)
                    + " structurallyCurrentRows=" + countStructurallyCurrentHistoryRows(rows)
                    + " action=no_row_candidate_verification");
        }
        cancelTimeout();
        completeStep(expectedStep);
    }

    private int countStructurallyCurrentHistoryRows(List<AccessibilityNodeInfo> rows) {
        int count = 0;
        for (AccessibilityNodeInfo row : rows) if (isStructurallyCurrentHistoryRow(row)) count++;
        return count;
    }

    private AccessibilityNodeInfo uniqueStructurallyCurrentHistoryRow(List<AccessibilityNodeInfo> rows) {
        AccessibilityNodeInfo found = null;
        for (AccessibilityNodeInfo row : rows) {
            if (!isStructurallyCurrentHistoryRow(row)) continue;
            if (found != null && !found.equals(row)) return null;
            found = row;
        }
        return found;
    }

    private boolean isStructurallyCurrentHistoryRow(AccessibilityNodeInfo row) {
        if (row == null) return false;
        return row.isSelected() || row.isFocused() || row.isAccessibilityFocused() || row.isChecked();
    }

    private void recordHistoryBoundaryEvidence(String phase, List<AccessibilityNodeInfo> roots) {
        List<String> ids = historyBoundaryItemIds(roots);
        String dump = historyBoundaryDump(roots, 96);
        LabStore.append(this, "HISTORY_A11Y_BOUNDARY phase=" + phase
                + " itemCount=" + ids.size()
                + " itemIds=" + LabStore.abbrev(joinForReport(ids), 12000)
                + " nodes=" + LabStore.abbrev(dump, 26000));
    }

    private List<String> historyBoundaryItemIds(List<AccessibilityNodeInfo> roots) {
        List<String> out = new ArrayList<>();
        if (roots == null) return out;
        for (AccessibilityNodeInfo root : roots) collectHistoryBoundaryItemIds(root, out, 0);
        return out;
    }

    private void collectHistoryBoundaryItemIds(AccessibilityNodeInfo node, List<String> out, int depth) {
        if (node == null || depth > 32 || out.size() >= 120) return;
        String id = node.getViewIdResourceName();
        if (id != null && id.contains(HISTORY_ITEM_PREFIX) && !out.contains(id)) out.add(id);
        for (int i = 0; i < node.getChildCount(); i++) {
            collectHistoryBoundaryItemIds(node.getChild(i), out, depth + 1);
            if (out.size() >= 120) return;
        }
    }

    private String historyBoundaryDump(List<AccessibilityNodeInfo> roots, int maxNodes) {
        StringBuilder out = new StringBuilder();
        int[] count = {0};
        if (roots != null) {
            for (AccessibilityNodeInfo root : roots) {
                appendHistoryBoundaryDump(root, out, count, maxNodes, 0);
                if (count[0] >= maxNodes) break;
            }
        }
        return out.toString();
    }

    private void appendHistoryBoundaryDump(AccessibilityNodeInfo node, StringBuilder out,
                                           int[] count, int maxNodes, int depth) {
        if (node == null || depth > 32 || count[0] >= maxNodes) return;
        String id = node.getViewIdResourceName();
        if (id != null && (id.contains(HISTORY_ITEM_PREFIX) || id.contains(HISTORY_ACTIONS_PREFIX))) {
            count[0]++;
            if (out.length() > 0) out.append(" || ");
            String prefix = id.contains(HISTORY_ITEM_PREFIX) ? HISTORY_ITEM_PREFIX : HISTORY_ACTIONS_PREFIX;
            out.append("kind=").append(prefix == HISTORY_ITEM_PREFIX ? "item" : "actions")
                    .append(" viewId=").append(id)
                    .append(" suffix=").append(historyBoundarySuffix(id, prefix))
                    .append(" class=").append(String.valueOf(node.getClassName()))
                    .append(" click=").append(node.isClickable())
                    .append(" long=").append(node.isLongClickable())
                    .append(" selected=").append(node.isSelected())
                    .append(" focused=").append(node.isFocused())
                    .append(" a11yFocused=").append(node.isAccessibilityFocused())
                    .append(" checked=").append(node.isChecked())
                    .append(" actions=").append(accessibilityActionSet(node))
                    .append(" parentChain=").append(parentViewIdChain(node, 4))
                    .append(" children=").append(directChildViewIds(node));
        }
        for (int i = 0; i < node.getChildCount(); i++) {
            appendHistoryBoundaryDump(node.getChild(i), out, count, maxNodes, depth + 1);
            if (count[0] >= maxNodes) return;
        }
    }

    private String accessibilityActionSet(AccessibilityNodeInfo node) {
        StringBuilder out = new StringBuilder();
        try {
            List<AccessibilityNodeInfo.AccessibilityAction> actions = node.getActionList();
            if (actions != null) {
                for (AccessibilityNodeInfo.AccessibilityAction action : actions) {
                    if (out.length() > 0) out.append(',');
                    out.append(action.getId());
                    CharSequence label = action.getLabel();
                    if (label != null && label.length() > 0) out.append(':').append(label);
                }
            }
        } catch (Throwable ignored) {}
        return out.toString();
    }

    private String parentViewIdChain(AccessibilityNodeInfo node, int maxUp) {
        StringBuilder out = new StringBuilder();
        AccessibilityNodeInfo p = node == null ? null : node.getParent();
        for (int i = 0; p != null && i < maxUp; i++) {
            if (out.length() > 0) out.append(" <- ");
            String id = p.getViewIdResourceName();
            out.append(id == null || id.isEmpty() ? String.valueOf(p.getClassName()) : id);
            p = p.getParent();
        }
        return out.toString();
    }

    private String directChildViewIds(AccessibilityNodeInfo node) {
        StringBuilder out = new StringBuilder();
        if (node == null) return "";
        for (int i = 0; i < node.getChildCount() && i < 16; i++) {
            AccessibilityNodeInfo child = node.getChild(i);
            if (child == null) continue;
            if (out.length() > 0) out.append(',');
            String id = child.getViewIdResourceName();
            out.append(id == null || id.isEmpty() ? String.valueOf(child.getClassName()) : id);
        }
        return out.toString();
    }

    private String historyBoundarySuffix(String raw, String prefix) {
        if (raw == null || prefix == null) return "";
        int at = raw.indexOf(prefix);
        if (at < 0) return "";
        return raw.substring(at + prefix.length()).trim();
    }

    private String firstHistoryItemViewId(AccessibilityNodeInfo node) {
        if (node == null) return "";
        String id = node.getViewIdResourceName();
        if (id != null && id.contains(HISTORY_ITEM_PREFIX)) return id;
        for (int i = 0; i < node.getChildCount(); i++) {
            String found = firstHistoryItemViewId(node.getChild(i));
            if (!found.isEmpty()) return found;
        }
        return "";
    }

    private String joinLines(List<String> values) {
        StringBuilder out = new StringBuilder();
        for (String value : values) {
            if (value == null || value.trim().isEmpty()) continue;
            if (out.length() > 0) out.append('\n');
            out.append(value.trim());
        }
        return out.toString();
    }

    private String joinForReport(List<String> values) {
        StringBuilder out = new StringBuilder();
        for (String value : values) {
            if (value == null || value.trim().isEmpty()) continue;
            if (out.length() > 0) out.append(" | ");
            out.append(value.trim());
        }
        return out.toString();
    }

    private List<String> baselineHistoryItemIds() {
        List<String> out = new ArrayList<>();
        String raw = LabStore.historyBaselineItemIds(this);
        if (raw == null || raw.trim().isEmpty()) return out;
        for (String line : raw.split("\\n")) {
            String value = line.trim();
            if (!value.isEmpty() && !out.contains(value)) out.add(value);
        }
        return out;
    }

    private List<String> newHistoryBoundaryItemIds(List<AccessibilityNodeInfo> roots) {
        List<String> baseline = baselineHistoryItemIds();
        List<String> current = historyBoundaryItemIds(roots);
        List<String> out = new ArrayList<>();
        for (String value : current) if (!baseline.contains(value) && !out.contains(value)) out.add(value);
        return out;
    }

    private void observeFreshBoundaryCandidate(String phase, List<AccessibilityNodeInfo> roots) {
        List<String> baseline = baselineHistoryItemIds();
        List<String> current = historyBoundaryItemIds(roots);
        List<String> added = newHistoryBoundaryItemIds(roots);
        LabStore.append(this, "HISTORY_A11Y_DIFF phase=" + phase
                + " baseline=" + baseline.size()
                + " current=" + current.size()
                + " added=" + added.size()
                + " addedIds=" + LabStore.abbrev(joinForReport(added), 8000));
        String existing = LabStore.freshBoundaryItemId(this);
        if (added.size() == 1) {
            String candidate = added.get(0);
            if (existing.isEmpty() || existing.equals(candidate)) {
                LabStore.setFreshBoundaryItemId(this, candidate);
                LabStore.append(this, "HISTORY_A11Y_FRESH_ITEM_UNIQUE phase=" + phase
                        + " viewId=" + candidate
                        + " suffix=" + historyBoundarySuffix(candidate, HISTORY_ITEM_PREFIX));
            } else {
                LabStore.append(this, "HISTORY_A11Y_FRESH_ITEM_CONFLICT existing=" + existing
                        + " observed=" + candidate);
                LabStore.setFreshBoundaryItemId(this, "");
            }
        }
    }

    private AccessibilityNodeInfo rowForHistoryBoundaryId(List<AccessibilityNodeInfo> rows, String id) {
        if (id == null || id.isEmpty()) return null;
        AccessibilityNodeInfo found = null;
        for (AccessibilityNodeInfo row : rows) {
            if (!historyRowContainsBoundaryId(row, id)) continue;
            if (found != null && !found.equals(row)) return null;
            found = row;
        }
        return found;
    }

    private boolean historyRowContainsBoundaryId(AccessibilityNodeInfo node, String id) {
        if (node == null) return false;
        if (id.equals(node.getViewIdResourceName())) return true;
        for (int i = 0; i < node.getChildCount(); i++) {
            if (historyRowContainsBoundaryId(node.getChild(i), id)) return true;
        }
        return false;
    }

'''
text = SVC.read_text()
anchor = '    private void opHistoryRecentBinding(JSONObject step, int stepIndex) {'
if anchor not in text:
    raise SystemExit('history recent anchor missing')
SVC.write_text(text.replace(anchor, calibration_methods + anchor, 1))

replace_once(
    SVC,
    '''    private void opHistoryRecentBinding(JSONObject step, int stepIndex) {\n        if (!isCurrentStep(stepIndex)) return;\n        LabStore.setState(this, "WAITING_HISTORY_RECENT_OPEN_INITIAL");\n''',
    '''    private void opHistoryRecentBinding(JSONObject step, int stepIndex) {\n        if (!isCurrentStep(stepIndex)) return;\n        LabStore.clearCandidates(this);\n        LabStore.setFreshBoundaryItemId(this, "");\n        LabStore.setState(this, "WAITING_HISTORY_RECENT_OPEN_INITIAL");\n''')

old_switch = '''    private void switchAwayFromFreshThread(int expectedStep, List<AccessibilityNodeInfo> roots) {\n        int newChatCount = countExactSemanticAcrossRoots(roots, "New chat");\n        LabStore.append(this, "HISTORY_RECENT_NEW_CHAT_EXACT_MATCHES=" + newChatCount);\n        if (newChatCount != 1) {\n            failRun("HISTORY_RECENT_NEW_CHAT_NOT_UNIQUE count=" + newChatCount);\n            return;\n        }\n        AccessibilityNodeInfo newChat = findUniqueExactSemanticAcrossRoots(roots, "New chat");\n        if (newChat == null) {\n            failRun("HISTORY_RECENT_NEW_CHAT_MISSING");\n            return;\n        }\n        LabStore.setState(this, "WAITING_HISTORY_RECENT_SWITCH_AWAY");\n        if (!performBoundedNavigation(newChat, "HISTORY_RECENT_SWITCH_AWAY", "New chat")) {\n            failRun("HISTORY_RECENT_SWITCH_AWAY_ACTION_FALSE");\n            return;\n        }\n        handler.postDelayed(() -> tryHistoryRecentBinding(expectedStep), 320L);\n    }\n'''
new_switch = '''    private void switchAwayFromFreshThread(int expectedStep, List<AccessibilityNodeInfo> roots) {\n        List<AccessibilityNodeInfo> semanticLeaves = new ArrayList<>();\n        List<AccessibilityNodeInfo> actionableTargets = new ArrayList<>();\n        for (AccessibilityNodeInfo root : roots) {\n            List<AccessibilityNodeInfo> one = new ArrayList<>();\n            collectExactSemanticNodes(root, "New chat", one, 0);\n            for (AccessibilityNodeInfo leaf : one) {\n                addUniqueNode(semanticLeaves, leaf);\n                AccessibilityNodeInfo target = firstActionClickAncestor(leaf, 8);\n                if (target != null) addUniqueNode(actionableTargets, target);\n            }\n        }\n        LabStore.append(this, "HISTORY_RECENT_NEW_CHAT_RESOLUTION semanticLeaves=" + semanticLeaves.size()\n                + " actionableTargets=" + actionableTargets.size());\n        if (actionableTargets.size() != 1) {\n            failRun("HISTORY_RECENT_NEW_CHAT_ACTIONABLE_NOT_UNIQUE count=" + actionableTargets.size());\n            return;\n        }\n        AccessibilityNodeInfo newChat = actionableTargets.get(0);\n        LabStore.setState(this, "WAITING_HISTORY_RECENT_SWITCH_AWAY");\n        if (!performBoundedNavigation(newChat, "HISTORY_RECENT_SWITCH_AWAY", "New chat")) {\n            failRun("HISTORY_RECENT_SWITCH_AWAY_ACTION_FALSE");\n            return;\n        }\n        handler.postDelayed(() -> tryHistoryRecentBinding(expectedStep), 320L);\n    }\n'''
replace_once(SVC, old_switch, new_switch)

old_selection = '''        AccessibilityNodeInfo row = rows.get(0);\n        String title = historyRowTitle(row);\n        LabStore.clearCandidates(this);\n        LabStore.setHistoryCandidateTitle(this, title);\n        MetadataStats stats = harvestAccessibilityMetadata(row);\n        String rowTree = normalizedTree(row, LabStore.marker(this), 180, 7);\n        LabStore.append(this, "HISTORY_RECENT_SELECTED_ROW index=0 title=" + LabStore.abbrev(title, 180)\n                + " metadataNodes=" + stats.nodes\n                + " extras=" + stats.extras\n                + " candidateMatches=" + stats.candidateMatches\n                + " rowTree=" + LabStore.abbrev(rowTree, 12000));\n'''
new_selection = '''        observeFreshBoundaryCandidate("settled_after_switch_away", roots);\n        String boundaryId = LabStore.freshBoundaryItemId(this);\n        AccessibilityNodeInfo row = rowForHistoryBoundaryId(rows, boundaryId);\n        if (boundaryId.isEmpty() || row == null) {\n            cancelTimeout();\n            LabStore.append(this, "HISTORY_RECENT_NO_UNIQUE_APK_DERIVED_ROW boundaryId="\n                    + LabStore.abbrev(boundaryId, 220)\n                    + " action=observation_only_no_unrelated_row_click");\n            completeStep(expectedStep);\n            return;\n        }\n        String title = historyRowTitle(row);\n        LabStore.clearCandidates(this);\n        LabStore.setHistoryCandidateTitle(this, title);\n        MetadataStats stats = harvestAccessibilityMetadata(row);\n        String rowTree = normalizedTree(row, LabStore.marker(this), 180, 7);\n        LabStore.append(this, "HISTORY_RECENT_SELECTED_ROW source=unique_new_history_accessibility_id"\n                + " boundaryId=" + LabStore.abbrev(boundaryId, 260)\n                + " suffix=" + LabStore.abbrev(historyBoundarySuffix(boundaryId, HISTORY_ITEM_PREFIX), 180)\n                + " title=" + LabStore.abbrev(title, 180)\n                + " metadataNodes=" + stats.nodes\n                + " extras=" + stats.extras\n                + " candidateMatches=" + stats.candidateMatches\n                + " rowTree=" + LabStore.abbrev(rowTree, 12000));\n'''
replace_once(SVC, old_selection, new_selection)

replace_once(
    SVC,
    '''    private void recordHistoryRecentDrawer(String phase, List<AccessibilityNodeInfo> roots) {\n        String snapshot = roots.isEmpty() ? "<no ChatGPT roots>"\n                : normalizedTree(roots.get(0), LabStore.marker(this), 520, 14);\n        LabStore.append(this, "HISTORY_RECENT_DRAWER phase=" + phase\n                + " rows=" + historyConversationRows(roots).size()\n                + " controlCensus=" + LabStore.abbrev(controlCensus(roots, 360), 26000)\n                + " activeSnapshot=" + LabStore.abbrev(snapshot, 22000));\n    }\n''',
    '''    private void recordHistoryRecentDrawer(String phase, List<AccessibilityNodeInfo> roots) {\n        String snapshot = roots.isEmpty() ? "<no ChatGPT roots>"\n                : normalizedTree(roots.get(0), LabStore.marker(this), 520, 14);\n        recordHistoryBoundaryEvidence("fresh_" + phase, roots);\n        observeFreshBoundaryCandidate(phase, roots);\n        LabStore.append(this, "HISTORY_RECENT_DRAWER phase=" + phase\n                + " rows=" + historyConversationRows(roots).size()\n                + " controlCensus=" + LabStore.abbrev(controlCensus(roots, 360), 26000)\n                + " activeSnapshot=" + LabStore.abbrev(snapshot, 22000));\n    }\n''')

replace_once(
    SVC,
    '''        if (counts.nonEditable >= 1) {\n            cancelTimeout();\n            LabStore.markVerified(this, verifyingCandidate);\n            launchLabForeground();\n        }\n''',
    '''        if (counts.nonEditable >= 1) {\n            cancelTimeout();\n            if (LabStore.calibrationMode(this)) {\n                LabStore.markCalibrationVerified(this, verifyingCandidate);\n                completeStep(expectedStep);\n            } else {\n                LabStore.markVerified(this, verifyingCandidate);\n                launchLabForeground();\n            }\n        }\n''')


# ---------- Plan: known indexed calibration (non-fatal probe) -> baseline -> fresh proof ----------
plan = {
    'schema': 1,
    'suite': NEW_SUITE,
    'targetVersion': '1.2026.237',
    'targetSignerSha256': 'b24f4bfbb3cf293f938703b9d87027c1102cc36dc4fa206910e08927db40473c',
    'steps': [
        {
            'op': 'global_search_binding',
            'marker': KNOWN_CALIBRATION_MARKER,
            'probe': True,
            'label': 'known_indexed_row_calibration',
            'navigationTimeoutMs': 8000,
            'resultWaitMs': 5000,
        },
        {'op': 'history_boundary_calibration', 'timeoutMs': 12000},
        {'op': 'verify_candidates', 'timeoutMs': 7000},
        {'op': 'reset_after_calibration'},
        {
            'op': 'launch_prompt',
            'prompt': 'Capability Lab static-first History accessibility proof. Reply with exactly this marker and no other text: {{marker}}',
        },
        {'op': 'capture_tree', 'label': 'pre_send_draft_baseline', 'timeoutMs': 8000},
        {'op': 'semantic_send', 'timeoutMs': 15000},
        {'op': 'capture_tree', 'label': 'post_send_receipt', 'timeoutMs': 8000},
        {'op': 'wait', 'ms': 700},
        {'op': 'history_recent_binding', 'timeoutMs': 22000, 'settleMs': 1100},
        {'op': 'verify_candidates', 'timeoutMs': 8000},
        {'op': 'finish', 'inconclusiveStatus': 'INCONCLUSIVE_HISTORY_ACCESSIBILITY_BOUNDARY_NOT_VERIFIED'},
    ],
}
PLAN.write_text(json.dumps(plan, indent=2) + '\n')
compact = json.dumps(plan, separators=(',', ':'))
java_literal = json.dumps(compact)
regex_replace_once(
    PLAN_LOADER,
    r'    static final String FALLBACK = ".*";\n',
    '    static final String FALLBACK = ' + java_literal + ';\n')

# ---------- Identity/UI ----------
replace_once(BUILD, '        versionCode 17\n', '        versionCode 18\n')
replace_once(BUILD,
             '        versionName "0.17-native-capability-lab-stable-fresh-history-binding"\n',
             f'        versionName "{NEW_VERSION_NAME}"\n')

main_text = MAIN.read_text()
start = main_text.index('    private static final String SCREEN_DESCRIPTION =')
end = main_text.index('\n\n    private final Handler handler', start)
new_desc = '''    private static final String SCREEN_DESCRIPTION =\n            "Stable v0.18 validates the exact APK-derived History accessibility boundary before using a History row. "\n          + "It first performs a best-effort calibration against an already indexed synthetic marker and records a pre-fresh baseline of raw chatgpt.history.item.* / chatgpt.history.actions.* view IDs, actions, and structure. "\n          + "It then creates one fresh synthetic marker chat, sends exactly once with the proven CLAIM/no-replay contract, and identifies a fresh row only by a unique new History accessibility ID relative to that baseline. "\n          + "New chat label/container aliases are deduplicated to one actionable target before navigation. No unrelated History row is clicked if that APK-derived boundary is absent or ambiguous. "\n          + "Any plausible ID candidate is independently verified through neutral state -> /c/<candidate> -> exact marker. DOWNLOAD FULL REPORT saves the authoritative report directly to Android Downloads. "\n          + "No private ChatGPT API is called, no credentials are extracted, and no coordinate writes, gestures, or global actions are used.";'''
MAIN.write_text(main_text[:start] + new_desc + main_text[end:])
replace_once(MAIN,
             '        runButton = button("RUN FRESH HISTORY BINDING PROOF", v -> startSuite());\n',
             '        runButton = button("RUN HISTORY ACCESSIBILITY BOUNDARY PROOF", v -> startSuite());\n')
replace_once(MAIN,
             '            styleBanner("STARTING FRESH HISTORY BINDING PROOF…", BLUE);\n',
             '            styleBanner("STARTING HISTORY ACCESSIBILITY BOUNDARY PROOF…", BLUE);\n')
replace_once(MAIN,
             '        else if (running || starting) b.append("\\nRUNNING: the Lab is executing one bounded official-UI fresh History binding proof. No screenshots are expected; the report file captures the evidence.\\n");\n',
             '        else if (running || starting) b.append("\\nRUNNING: the Lab is executing one bounded static-first History accessibility boundary proof. No screenshots are expected; the report file captures the evidence.\\n");\n')

# ---------- Public CI: freeze v0.18 contract and safety boundaries ----------
CI.write_text(r'''name: Unified ChatGPT Capability Lab CI

on:
  push:
    branches:
      - build/pebble-chat-bridge-v019
    paths:
      - '.github/workflows/native-capability-lab.yml'
      - 'runtime_probes/native-capability-lab/**'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Capability Lab v0.18 safety prechecks
        shell: bash
        run: |
          set -euo pipefail
          ROOT=runtime_probes/native-capability-lab
          SVC="$ROOT/app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java"
          STORE="$ROOT/app/src/main/java/com/openai/controlplane/capabilitylab/LabStore.java"
          MAIN="$ROOT/app/src/main/java/com/openai/controlplane/capabilitylab/MainActivity.java"
          LOADER="$ROOT/app/src/main/java/com/openai/controlplane/capabilitylab/PlanLoader.java"
          MAN="$ROOT/app/src/main/AndroidManifest.xml"
          PLAN="$ROOT/plans/default.json"

          grep -Fq 'com.openai.chatgpt' "$ROOT/app/src/main/java/com/openai/controlplane/capabilitylab/ProfileGuard.java"
          grep -Fq 'WRITE_CLAIM' "$STORE"
          grep -Fq 'calibrationMode' "$STORE"
          grep -Fq 'historyBaselineItemIds' "$STORE"
          grep -Fq 'freshBoundaryItemId' "$STORE"
          grep -Fq 'case "history_boundary_calibration"' "$SVC"
          grep -Fq 'case "reset_after_calibration"' "$SVC"
          grep -Fq 'HISTORY_ITEM_PREFIX = "chatgpt.history.item."' "$SVC"
          grep -Fq 'HISTORY_ACTIONS_PREFIX = "chatgpt.history.actions."' "$SVC"
          grep -Fq 'HISTORY_A11Y_BOUNDARY' "$SVC"
          grep -Fq 'HISTORY_A11Y_DIFF' "$SVC"
          grep -Fq 'HISTORY_A11Y_FRESH_ITEM_UNIQUE' "$SVC"
          grep -Fq 'HISTORY_RECENT_NEW_CHAT_RESOLUTION' "$SVC"
          grep -Fq 'source=unique_new_history_accessibility_id' "$SVC"
          grep -Fq 'action=observation_only_no_unrelated_row_click' "$SVC"
          grep -Fq 'harvestAccessibilityMetadata(row)' "$SVC"
          grep -Fq 'DOWNLOAD FULL REPORT' "$MAIN"
          grep -Fq 'RUN HISTORY ACCESSIBILITY BOUNDARY PROOF' "$MAIN"
          grep -Fq 'MediaStore.Downloads.EXTERNAL_CONTENT_URI' "$MAIN"
          grep -Fq 'conversation_history_accessibility_binding_v13_static_first' "$LOADER"
          grep -Fq 'conversation_history_accessibility_binding_v13_static_first' "$PLAN"
          grep -Fq 'android.permission.INTERNET' "$MAN"

          ! grep -R -n -E 'api\.openai\.com|Authorization: Bearer|access_token|refresh_token' "$ROOT"
          ! grep -Fq 'dispatchGesture' "$SVC"
          ! grep -Fq 'getBoundsInScreen' "$SVC"
          ! grep -Fq 'GLOBAL_ACTION_' "$SVC"
          ! grep -Fq 'Intent.createChooser' "$MAIN"
          ! grep -Fq 'FileProvider.getUriForFile' "$MAIN"

          python3 - <<'PY'
          from pathlib import Path
          import json
          root = Path('runtime_probes/native-capability-lab')
          s = (root / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java').read_text()
          if s.count('performAction(AccessibilityNodeInfo.ACTION_CLICK)') != 2:
              raise SystemExit('v0.18 must retain exactly two ACTION_CLICK code sites')
          if s.count('performAction(AccessibilityNodeInfo.ACTION_SET_TEXT') != 1:
              raise SystemExit('v0.18 must retain exactly one Search ACTION_SET_TEXT site')
          if 'completeStep();' in s:
              raise SystemExit('unguarded bare completeStep() found')

          gradle = (root / 'app/build.gradle').read_text()
          assert "applicationId 'com.openai.controlplane.capabilitylab.stable'" in gradle
          assert 'versionCode 18' in gradle
          assert '0.18-native-capability-lab-stable-history-a11y-boundary' in gradle

          data = json.loads((root / 'plans/default.json').read_text())
          assert data['schema'] == 1
          assert data['targetVersion'] == '1.2026.237'
          assert data['suite'] == 'conversation_history_accessibility_binding_v13_static_first'
          steps = data['steps']
          ops = [x['op'] for x in steps]
          assert ops.count('launch_prompt') == 1
          assert ops.count('semantic_send') == 1
          assert ops.count('history_boundary_calibration') == 1
          assert ops.count('reset_after_calibration') == 1
          assert ops.count('history_recent_binding') == 1
          assert ops.count('verify_candidates') == 2
          assert ops.count('global_search_binding') == 1
          calibration = next(x for x in steps if x['op'] == 'global_search_binding')
          assert calibration['probe'] is True
          assert calibration['marker'] == 'LAB_CID_9FC96C5A35E04E5B'
          assert calibration['label'] == 'known_indexed_row_calibration'
          assert steps[-1]['op'] == 'finish'
          assert steps[-1]['inconclusiveStatus'] == 'INCONCLUSIVE_HISTORY_ACCESSIBILITY_BOUNDARY_NOT_VERIFIED'
          PY

      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - name: Set up Android SDK
        uses: android-actions/setup-android@v3

      - name: Install Android SDK
        shell: bash
        run: |
          set -euo pipefail
          sdkmanager "platforms;android-35" "build-tools;35.0.0"
          echo "sdk.dir=$ANDROID_SDK_ROOT" > runtime_probes/native-capability-lab/local.properties

      - name: Build verification APK
        shell: bash
        run: |
          set -euo pipefail
          curl -fsSL https://services.gradle.org/distributions/gradle-8.10.2-bin.zip -o /tmp/gradle.zip
          unzip -q /tmp/gradle.zip -d /tmp
          cd runtime_probes/native-capability-lab
          /tmp/gradle-8.10.2/bin/gradle --no-daemon :app:assembleDebug --stacktrace
          mkdir -p ../../ci/out
          cp app/build/outputs/apk/debug/app-debug.apk ../../ci/out/chatgpt-capability-lab-ci-only.apk

      - name: Verify package metadata
        shell: bash
        run: |
          set -euo pipefail
          APKSIGNER=$(find "$ANDROID_SDK_ROOT/build-tools" -type f -name apksigner | sort | tail -n 1)
          AAPT=$(find "$ANDROID_SDK_ROOT/build-tools" -type f -name aapt | sort | tail -n 1)
          "$APKSIGNER" verify --verbose --print-certs ci/out/chatgpt-capability-lab-ci-only.apk | tee ci/out/apksigner.txt
          "$AAPT" dump badging ci/out/chatgpt-capability-lab-ci-only.apk | tee ci/out/badging.txt
          grep -Fq "package: name='com.openai.controlplane.capabilitylab.stable' versionCode='18' versionName='0.18-native-capability-lab-stable-history-a11y-boundary'" ci/out/badging.txt
          sha256sum ci/out/chatgpt-capability-lab-ci-only.apk | tee ci/out/SHA256.txt

      - name: Upload CI-only artifact
        uses: actions/upload-artifact@v4
        with:
          name: chatgpt-capability-lab-ci-only
          path: |
            ci/out/chatgpt-capability-lab-ci-only.apk
            ci/out/SHA256.txt
            ci/out/apksigner.txt
            ci/out/badging.txt
''')

print('Capability Lab v0.18 static-first History accessibility boundary patch applied')
