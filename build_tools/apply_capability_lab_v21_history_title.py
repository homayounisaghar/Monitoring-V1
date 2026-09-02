#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT = Path('runtime_probes/native-capability-lab')
GRADLE = ROOT / 'app/build.gradle'
PLAN = ROOT / 'plans/default.json'
LOADER = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/PlanLoader.java'
MAIN = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/MainActivity.java'
STORE = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabStore.java'
SVC = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java'

plan = {
    'schema': 1,
    'suite': 'conversation_history_title_binding_v16_rename_reopen',
    'targetVersion': '1.2026.237',
    'targetSignerSha256': 'b24f4bfbb3cf293f938703b9d87027c1102cc36dc4fa206910e08927db40473c',
    'steps': [
        {'op': 'resume_chatgpt'},
        {'op': 'wait', 'ms': 700},
        {
            'op': 'launch_prompt',
            'prompt': '{{titleSeed}} title-binding proof. Reply with exactly this marker and no other text: {{marker}}'
        },
        {'op': 'capture_tree', 'label': 'pre_send_title_binding_draft', 'timeoutMs': 8000},
        {'op': 'semantic_send', 'timeoutMs': 15000},
        {'op': 'capture_tree', 'label': 'post_send_title_binding_receipt', 'timeoutMs': 8000},
        {'op': 'wait', 'ms': 900},
        {'op': 'history_title_binding', 'timeoutMs': 36000, 'settleMs': 1200},
        {'op': 'finish', 'inconclusiveStatus': 'INCONCLUSIVE_HISTORY_TITLE_BINDING_NOT_VERIFIED'}
    ]
}

# Stable package/signing lineage, one version bump.
gradle = GRADLE.read_text()
assert 'versionCode 20' in gradle
assert '0.20-native-capability-lab-stable-history-row-disambiguation' in gradle
gradle = gradle.replace('versionCode 20', 'versionCode 21')
gradle = gradle.replace(
    '0.20-native-capability-lab-stable-history-row-disambiguation',
    '0.21-native-capability-lab-stable-history-title-binding'
)
GRADLE.write_text(gradle)

PLAN.write_text(json.dumps(plan, indent=2) + '\n')

loader = LOADER.read_text()
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

main = MAIN.read_text()
old_desc = '''    private static final String SCREEN_DESCRIPTION =\n            "Stable v0.20 continues the exact APK-derived History accessibility boundary proof with official Search removed from the critical path. "\n          + "It first foregrounds ChatGPT and records a direct pre-fresh baseline of raw chatgpt.history.item.* / chatgpt.history.actions.* view IDs, actions, and structure. "\n          + "It then creates one fresh synthetic marker chat, sends exactly once with the proven CLAIM/no-replay contract, and identifies a fresh row only by a unique new History accessibility ID relative to that baseline. "\n          + "Runtime-proven History rows titled New chat are excluded by their ACTION_LONG_CLICK row contract; the navigation control must be the unique clickable non-long-click target before switching away. No unrelated History row is clicked if that APK-derived boundary is absent or ambiguous. "\n          + "Any plausible ID candidate is independently verified through neutral state -> /c/<candidate> -> exact marker. DOWNLOAD FULL REPORT saves the authoritative report directly to Android Downloads. "\n          + "No private ChatGPT API is called, no credentials are extracted, and no coordinate writes, gestures, or global actions are used.";'''
new_desc = '''    private static final String SCREEN_DESCRIPTION =\n            "Stable v0.21 tests the final HistoryTitleBinding chain after the accessibility-ID boundary closed negative on v0.20. "\n          + "It creates one fresh synthetic marker chat, sends exactly once under the proven CLAIM/no-replay contract, then opens official History. "\n          + "The row may be touched only when it is uniquely correlated to the currently open conversation by structural current-row state, with a unique run-specific title seed as a bounded fallback. "\n          + "It long-clicks only that History row, requires a unique Rename action and one editable title field, sets a synthetic unique title, persists a separate durable RENAME_CLAIM before the single commit action, and requires the renamed title to appear exactly once as the mutation receipt. "\n          + "Finally it opens only that uniquely renamed row and requires the original synthetic chat marker to be present before declaring PASS. No unrelated History row is walked. "\n          + "No private ChatGPT API is called, no credentials are extracted, and no coordinate writes, gestures, or global actions are used.";'''
assert old_desc in main
main = main.replace(old_desc, new_desc)
main = main.replace('RUN HISTORY ACCESSIBILITY BOUNDARY PROOF', 'RUN HISTORY TITLE BINDING PROOF')
main = main.replace('HISTORY BOUNDARY PROOF RUNNING…', 'HISTORY TITLE BINDING PROOF RUNNING…')
main = main.replace('STARTING HISTORY ACCESSIBILITY BOUNDARY PROOF…', 'STARTING HISTORY TITLE BINDING PROOF…')
main = main.replace('the Lab is executing one bounded static-first History accessibility boundary proof.', 'the Lab is executing one bounded HistoryTitleBinding rename/reopen proof.')
MAIN.write_text(main)

store = STORE.read_text()
# New durable mutation/readback state.
assert '.putBoolean("writeClaimed", false)' in store
store = store.replace(
    '.putBoolean("writeClaimed", false)\n                .putBoolean("sendConfirmed", false)',
    '.putBoolean("writeClaimed", false)\n                .putBoolean("sendConfirmed", false)\n                .putBoolean("renameClaimed", false)\n                .putBoolean("renameConfirmed", false)\n                .putBoolean("historyTitleBindingVerified", false)'
)
assert 'static boolean historyBindingVerified(Context c)' in store
store = store.replace(
    '    static boolean historyBindingVerified(Context c) { return p(c).getBoolean("historyBindingVerified", false); }',
    '    static boolean historyBindingVerified(Context c) { return p(c).getBoolean("historyBindingVerified", false); }\n'
    '    static boolean renameClaimed(Context c) { return p(c).getBoolean("renameClaimed", false); }\n'
    '    static boolean renameConfirmed(Context c) { return p(c).getBoolean("renameConfirmed", false); }\n'
    '    static boolean historyTitleBindingVerified(Context c) { return p(c).getBoolean("historyTitleBindingVerified", false); }'
)
claim_anchor = '''    static synchronized void markSendConfirmed(Context c) {\n        if (sendConfirmed(c)) return;'''
assert claim_anchor in store
rename_methods = '''    static synchronized boolean claimRename(Context c) {\n        if (renameClaimed(c)) return false;\n        p(c).edit().putBoolean("renameClaimed", true).commit();\n        append(c, "RENAME_CLAIM durable=true");\n        return true;\n    }\n\n    static synchronized void markRenameConfirmed(Context c, String title) {\n        if (renameConfirmed(c)) return;\n        p(c).edit().putBoolean("renameConfirmed", true).commit();\n        append(c, "RENAME_RECEIPT exactTitleUnique=true title=" + abbrev(title == null ? "" : title, 180));\n    }\n\n    static synchronized void markHistoryTitleBindingVerified(Context c, String title) {\n        if (historyTitleBindingVerified(c)) return;\n        String safeTitle = title == null ? "" : title;\n        p(c).edit()\n                .putBoolean("historyTitleBindingVerified", true)\n                .putBoolean("historyBindingVerified", true)\n                .putString("historyVerifiedTitle", safeTitle)\n                .commit();\n        append(c, "VERIFIED_HISTORY_TITLE_BINDING marker=" + marker(c)\n                + " title=" + abbrev(safeTitle, 180));\n    }\n\n'''
store = store.replace(claim_anchor, rename_methods + claim_anchor)
# Summary evidence.
assert '+ " historyBinding=" + historyBindingVerified(c)' in store
store = store.replace(
    '+ " historyBinding=" + historyBindingVerified(c)',
    '+ " historyBinding=" + historyBindingVerified(c)\n'
    '                + " titleBinding=" + historyTitleBindingVerified(c)\n'
    '                + " renameClaimed=" + renameClaimed(c)\n'
    '                + " renameConfirmed=" + renameConfirmed(c)'
)
STORE.write_text(store)

svc = SVC.read_text()
# Route state machine events.
old_event = '''        } else if (state.startsWith("WAITING_HISTORY_RECENT_")) {\n            tryHistoryRecentBinding(expectedStep);\n        } else if (state.startsWith("WAITING_HISTORY_REFRESH")) {'''
new_event = '''        } else if (state.startsWith("WAITING_HISTORY_RECENT_")) {\n            tryHistoryRecentBinding(expectedStep);\n        } else if (state.startsWith("WAITING_HISTORY_TITLE_")) {\n            tryHistoryTitleBinding(expectedStep);\n        } else if (state.startsWith("WAITING_HISTORY_REFRESH")) {'''
assert old_event in svc
svc = svc.replace(old_event, new_event)

# Add plan operation.
old_case = '''                case "history_recent_binding":\n                    opHistoryRecentBinding(step, i);\n                    break;\n                case "history_refresh":'''
new_case = '''                case "history_recent_binding":\n                    opHistoryRecentBinding(step, i);\n                    break;\n                case "history_title_binding":\n                    opHistoryTitleBinding(step, i);\n                    break;\n                case "history_refresh":'''
assert old_case in svc
svc = svc.replace(old_case, new_case)

# Dedicated PASS status.
old_finish = '''                    if (!LabStore.verifiedConversationId(this).isEmpty()) {\n                        LabStore.finish(this, "PASS_VERIFIED_CONVERSATION_ID");\n                    } else if (LabStore.historyBindingVerified(this)) {\n                        LabStore.finish(this, "PASS_VERIFIED_HISTORY_RECENT_BINDING");'''
new_finish = '''                    if (!LabStore.verifiedConversationId(this).isEmpty()) {\n                        LabStore.finish(this, "PASS_VERIFIED_CONVERSATION_ID");\n                    } else if (LabStore.historyTitleBindingVerified(this)) {\n                        LabStore.finish(this, "PASS_VERIFIED_HISTORY_TITLE_BINDING");\n                    } else if (LabStore.historyBindingVerified(this)) {\n                        LabStore.finish(this, "PASS_VERIFIED_HISTORY_RECENT_BINDING");'''
assert old_finish in svc
svc = svc.replace(old_finish, new_finish)

# Feed a run-specific title seed into the prompt so the History row has a safe fallback correlation signal.
old_prompt = '        String prompt = step.optString("prompt", "Capability Lab proof {{marker}}").replace("{{marker}}", marker);'
new_prompt = '        String prompt = step.optString("prompt", "Capability Lab proof {{marker}}").replace("{{marker}}", marker).replace("{{titleSeed}}", titleSeedForMarker(marker));'
assert old_prompt in svc
svc = svc.replace(old_prompt, new_prompt)

# A claimed rename with no receipt is UNCERTAIN and must never replay.
old_timeout = '''            } else if ("SEND_CLAIMED".equals(state) && LabStore.writeClaimed(this)) {\n                failUncertain(reason + " after durable claim");\n            } else {'''
new_timeout = '''            } else if ("SEND_CLAIMED".equals(state) && LabStore.writeClaimed(this)) {\n                failUncertain(reason + " after durable claim");\n            } else if (state.startsWith("WAITING_HISTORY_TITLE_")\n                    && LabStore.renameClaimed(this) && !LabStore.renameConfirmed(this)) {\n                failUncertain(reason + " after durable rename claim");\n            } else {'''
assert old_timeout in svc
svc = svc.replace(old_timeout, new_timeout)

insert_anchor = '    private void opHistoryRecentBinding(JSONObject step, int stepIndex) {'
assert insert_anchor in svc
history_title_code = r'''    private String titleSeedForMarker(String marker) {
        String x = marker == null ? "" : marker.replace("LAB_CID_", "").trim();
        if (x.length() > 10) x = x.substring(0, 10);
        return "LABSEED_" + x;
    }

    private String renameTitleForMarker(String marker) {
        String x = marker == null ? "" : marker.replace("LAB_CID_", "").trim();
        if (x.length() > 12) x = x.substring(0, 12);
        return "LABTITLE_" + x;
    }

    private void opHistoryTitleBinding(JSONObject step, int stepIndex) {
        if (!isCurrentStep(stepIndex)) return;
        LabStore.setState(this, "WAITING_HISTORY_TITLE_OPEN");
        LabStore.append(this, "HISTORY_TITLE_BINDING_ARMED marker=" + LabStore.marker(this)
                + " titleSeed=" + titleSeedForMarker(LabStore.marker(this))
                + " renameTitle=" + renameTitleForMarker(LabStore.marker(this)));
        armTimeout(step.optLong("timeoutMs", 36000L), "HISTORY_TITLE_BINDING_TIMEOUT", stepIndex);
        handler.postDelayed(() -> tryHistoryTitleBinding(stepIndex), 200L);
    }

    private void tryHistoryTitleBinding(int expectedStep) {
        if (!isCurrentStep(expectedStep)) return;
        String state = LabStore.state(this);
        if (!state.startsWith("WAITING_HISTORY_TITLE_")) return;
        List<AccessibilityNodeInfo> roots = chatGptRoots();
        if (roots.isEmpty()) return;

        if ("WAITING_HISTORY_TITLE_OPEN".equals(state)) {
            if (isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots)) {
                armHistoryTitleSettle(expectedStep);
                return;
            }
            AccessibilityNodeInfo historyEntry = findUniqueHistoryEntryAcrossRoots(roots);
            if (historyEntry == null) return;
            LabStore.setState(this, "WAITING_HISTORY_TITLE_DRAWER");
            if (!performBoundedNavigation(historyEntry, "HISTORY_TITLE_OPEN",
                    "Open conversation history", "Open sidebar", "Open navigation",
                    "Open navigation menu", "Navigation menu", "Menu")) {
                failRun("HISTORY_TITLE_OPEN_ACTION_FALSE");
                return;
            }
            handler.postDelayed(() -> tryHistoryTitleBinding(expectedStep), 280L);
            return;
        }

        if ("WAITING_HISTORY_TITLE_DRAWER".equals(state)) {
            if (!(isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots))) return;
            armHistoryTitleSettle(expectedStep);
            return;
        }

        if ("WAITING_HISTORY_TITLE_SETTLE".equals(state)) {
            if (!(isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots))) return;
            long remaining = LabStore.waitUntil(this) - System.currentTimeMillis();
            if (remaining > 0L) {
                handler.postDelayed(() -> tryHistoryTitleBinding(expectedStep), Math.min(remaining, 250L));
                return;
            }
            List<AccessibilityNodeInfo> rows = historyConversationRows(roots);
            LabStore.append(this, "HISTORY_TITLE_ROW_STATE_CENSUS count=" + rows.size()
                    + " rows=" + LabStore.abbrev(historyTitleRowStateCensus(rows), 18000));
            AccessibilityNodeInfo row = uniqueFreshRowForRename(rows);
            if (row == null) {
                LabStore.append(this, "HISTORY_TITLE_NO_SAFE_FRESH_ROW currentRows="
                        + countStructurallyCurrentHistoryRows(rows)
                        + " seed=" + titleSeedForMarker(LabStore.marker(this))
                        + " action=observation_only_no_row_mutation");
                cancelTimeout();
                completeStep(expectedStep);
                return;
            }
            if (!hasAction(row, AccessibilityNodeInfo.ACTION_LONG_CLICK)) {
                failRun("HISTORY_TITLE_CORRELATED_ROW_NO_LONG_CLICK");
                return;
            }
            LabStore.append(this, "HISTORY_TITLE_CORRELATED_ROW title="
                    + LabStore.abbrev(historyRowTitle(row), 180)
                    + " selected=" + row.isSelected()
                    + " focused=" + row.isFocused()
                    + " a11yFocused=" + row.isAccessibilityFocused()
                    + " checked=" + row.isChecked()
                    + " actions=" + safeActionLabels(row));
            LabStore.setState(this, "WAITING_HISTORY_TITLE_ACTIONS");
            boolean ok = row.performAction(AccessibilityNodeInfo.ACTION_LONG_CLICK);
            LabStore.append(this, "HISTORY_TITLE_ROW_LONG_CLICK returned=" + ok);
            if (!ok) {
                failRun("HISTORY_TITLE_ROW_LONG_CLICK_FALSE");
                return;
            }
            handler.postDelayed(() -> tryHistoryTitleBinding(expectedStep), 260L);
            return;
        }

        if ("WAITING_HISTORY_TITLE_ACTIONS".equals(state)) {
            AccessibilityNodeInfo rename = uniqueActionableExactAcrossRoots(roots, "Rename");
            if (rename == null) return;
            LabStore.setState(this, "WAITING_HISTORY_TITLE_EDITOR");
            if (!performBoundedNavigation(rename, "HISTORY_TITLE_RENAME_ENTRY", "Rename")) {
                failRun("HISTORY_TITLE_RENAME_ENTRY_ACTION_FALSE");
                return;
            }
            handler.postDelayed(() -> tryHistoryTitleBinding(expectedStep), 250L);
            return;
        }

        if ("WAITING_HISTORY_TITLE_EDITOR".equals(state)) {
            List<AccessibilityNodeInfo> editables = visibleEditableAcrossRoots(roots);
            if (editables.size() != 1) return;
            AccessibilityNodeInfo editor = editables.get(0);
            String desired = renameTitleForMarker(LabStore.marker(this));
            Bundle args = new Bundle();
            args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, desired);
            LabStore.setState(this, "WAITING_HISTORY_TITLE_COMMIT");
            boolean set = editor.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args);
            LabStore.append(this, "HISTORY_TITLE_RENAME_DRAFT_SET returned=" + set
                    + " desired=" + desired + " editableCount=" + editables.size());
            if (!set) {
                failRun("HISTORY_TITLE_RENAME_SET_TEXT_FALSE");
                return;
            }
            handler.postDelayed(() -> tryHistoryTitleBinding(expectedStep), 220L);
            return;
        }

        if ("WAITING_HISTORY_TITLE_COMMIT".equals(state)) {
            AccessibilityNodeInfo commit = uniqueActionableExactAcrossRoots(roots, "Save", "Rename", "Done");
            if (commit == null) return;
            if (!LabStore.claimRename(this)) {
                failUncertain("HISTORY_TITLE_RENAME_CLAIM_ALREADY_SET");
                return;
            }
            LabStore.setState(this, "WAITING_HISTORY_TITLE_RENAME_CLAIMED");
            boolean ok = performBoundedNavigation(commit, "HISTORY_TITLE_RENAME_COMMIT", "Save", "Rename", "Done");
            if (!ok) {
                failUncertain("HISTORY_TITLE_RENAME_COMMIT_ACTION_FALSE");
                return;
            }
            handler.postDelayed(() -> tryHistoryTitleBinding(expectedStep), 320L);
            return;
        }

        if ("WAITING_HISTORY_TITLE_RENAME_CLAIMED".equals(state)) {
            if (isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots)) {
                confirmRenameReceiptAndOpen(expectedStep, roots);
                return;
            }
            if (!visibleEditableAcrossRoots(roots).isEmpty()) return;
            AccessibilityNodeInfo historyEntry = findUniqueHistoryEntryAcrossRoots(roots);
            if (historyEntry == null) return;
            LabStore.setState(this, "WAITING_HISTORY_TITLE_RECEIPT_DRAWER");
            if (!performBoundedNavigation(historyEntry, "HISTORY_TITLE_RECEIPT_OPEN_HISTORY",
                    "Open conversation history", "Open sidebar", "Open navigation",
                    "Open navigation menu", "Navigation menu", "Menu")) {
                failUncertain("HISTORY_TITLE_RECEIPT_OPEN_HISTORY_FALSE");
                return;
            }
            handler.postDelayed(() -> tryHistoryTitleBinding(expectedStep), 280L);
            return;
        }

        if ("WAITING_HISTORY_TITLE_RECEIPT_DRAWER".equals(state)) {
            if (!(isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots))) return;
            confirmRenameReceiptAndOpen(expectedStep, roots);
            return;
        }

        if ("WAITING_HISTORY_TITLE_VERIFY_REOPEN".equals(state)) {
            if (isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots)) return;
            AccessibilityNodeInfo active = getRootInActiveWindow();
            if (active == null || !isChatGptRoot(active)) return;
            MarkerCounts counts = countMarkerNodes(active, LabStore.marker(this));
            if (counts.editable == 0 && counts.nonEditable >= 1) {
                cancelTimeout();
                String title = renameTitleForMarker(LabStore.marker(this));
                LabStore.append(this, "HISTORY_TITLE_REOPEN_VERIFIED markerEditable=" + counts.editable
                        + " markerNonEditable=" + counts.nonEditable
                        + " title=" + title);
                LabStore.markHistoryTitleBindingVerified(this, title);
                completeStep(expectedStep);
                return;
            }
            long remaining = LabStore.waitUntil(this) - System.currentTimeMillis();
            if (remaining > 0L) {
                handler.postDelayed(() -> tryHistoryTitleBinding(expectedStep), Math.min(remaining, 250L));
                return;
            }
            LabStore.append(this, "HISTORY_TITLE_REOPEN_MARKER_MISMATCH markerEditable=" + counts.editable
                    + " markerNonEditable=" + counts.nonEditable
                    + " snapshot=" + LabStore.abbrev(normalizedTree(active, LabStore.marker(this), 320, 12), 16000));
            failRun("HISTORY_TITLE_REOPEN_MARKER_MISMATCH");
        }
    }

    private void armHistoryTitleSettle(int expectedStep) {
        JSONObject step = currentPlanStep(expectedStep);
        long settle = step == null ? 1200L : Math.max(400L, Math.min(step.optLong("settleMs", 1200L), 5000L));
        LabStore.setWaitUntil(this, System.currentTimeMillis() + settle);
        LabStore.setState(this, "WAITING_HISTORY_TITLE_SETTLE");
        LabStore.append(this, "HISTORY_TITLE_SETTLE ms=" + settle);
        handler.postDelayed(() -> tryHistoryTitleBinding(expectedStep), Math.min(settle, 300L));
    }

    private AccessibilityNodeInfo uniqueFreshRowForRename(List<AccessibilityNodeInfo> rows) {
        AccessibilityNodeInfo current = uniqueStructurallyCurrentHistoryRow(rows);
        if (current != null) {
            LabStore.append(this, "HISTORY_TITLE_ROW_CORRELATION source=unique_structurally_current");
            return current;
        }
        String seed = titleSeedForMarker(LabStore.marker(this)).toLowerCase(Locale.US);
        AccessibilityNodeInfo found = null;
        int count = 0;
        for (AccessibilityNodeInfo row : rows) {
            String title = historyRowTitle(row).toLowerCase(Locale.US);
            if (!title.contains(seed)) continue;
            count++;
            if (found == null) found = row;
        }
        LabStore.append(this, "HISTORY_TITLE_ROW_CORRELATION source=title_seed seed=" + seed
                + " matches=" + count);
        return count == 1 ? found : null;
    }

    private String historyTitleRowStateCensus(List<AccessibilityNodeInfo> rows) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < rows.size() && i < 20; i++) {
            AccessibilityNodeInfo row = rows.get(i);
            if (out.length() > 0) out.append(" | ");
            out.append(i).append(':').append(LabStore.abbrev(historyRowTitle(row), 100))
                    .append(" sel=").append(row.isSelected())
                    .append(" foc=").append(row.isFocused())
                    .append(" a11y=").append(row.isAccessibilityFocused())
                    .append(" chk=").append(row.isChecked())
                    .append(" click=").append(row.isClickable())
                    .append(" long=").append(hasAction(row, AccessibilityNodeInfo.ACTION_LONG_CLICK));
        }
        return out.toString();
    }

    private AccessibilityNodeInfo uniqueActionableExactAcrossRoots(List<AccessibilityNodeInfo> roots,
                                                                    String... labels) {
        List<AccessibilityNodeInfo> targets = new ArrayList<>();
        for (String label : labels) {
            for (AccessibilityNodeInfo root : roots) {
                List<AccessibilityNodeInfo> nodes = new ArrayList<>();
                collectExactSemanticNodes(root, label, nodes, 0);
                for (AccessibilityNodeInfo node : nodes) {
                    AccessibilityNodeInfo target = firstActionClickAncestor(node, 8);
                    if (target != null) addUniqueNode(targets, target);
                }
            }
        }
        return targets.size() == 1 ? targets.get(0) : null;
    }

    private List<AccessibilityNodeInfo> visibleEditableAcrossRoots(List<AccessibilityNodeInfo> roots) {
        List<AccessibilityNodeInfo> out = new ArrayList<>();
        for (AccessibilityNodeInfo root : roots) collectVisibleEditables(root, out, 0);
        return out;
    }

    private void collectVisibleEditables(AccessibilityNodeInfo node, List<AccessibilityNodeInfo> out, int depth) {
        if (node == null || depth > 32 || out.size() >= 20) return;
        if (node.isVisibleToUser() && node.isEnabled() && node.isEditable()) addUniqueNode(out, node);
        for (int i = 0; i < node.getChildCount(); i++) collectVisibleEditables(node.getChild(i), out, depth + 1);
    }

    private void confirmRenameReceiptAndOpen(int expectedStep, List<AccessibilityNodeInfo> roots) {
        String desired = renameTitleForMarker(LabStore.marker(this));
        List<AccessibilityNodeInfo> rows = historyConversationRows(roots);
        List<AccessibilityNodeInfo> matches = new ArrayList<>();
        for (AccessibilityNodeInfo row : rows) {
            if (desired.equals(historyRowTitle(row))) addUniqueNode(matches, row);
        }
        LabStore.append(this, "HISTORY_TITLE_RENAME_RECEIPT_SCAN desired=" + desired
                + " exactMatches=" + matches.size()
                + " rows=" + LabStore.abbrev(historyTitleRowStateCensus(rows), 18000));
        if (matches.size() != 1) return;
        LabStore.markRenameConfirmed(this, desired);
        LabStore.setHistoryCandidateTitle(this, desired);
        LabStore.setState(this, "WAITING_HISTORY_TITLE_VERIFY_REOPEN");
        LabStore.setWaitUntil(this, System.currentTimeMillis() + 2500L);
        if (!performBoundedNavigation(matches.get(0), "HISTORY_TITLE_OPEN_RENAMED_ROW")) {
            failRun("HISTORY_TITLE_OPEN_RENAMED_ROW_ACTION_FALSE");
            return;
        }
        handler.postDelayed(() -> tryHistoryTitleBinding(expectedStep), 300L);
    }

'''
svc = svc.replace(insert_anchor, history_title_code + insert_anchor)
SVC.write_text(svc)

# Contract checks.
data = json.loads(PLAN.read_text())
ops = [x['op'] for x in data['steps']]
assert data['suite'] == 'conversation_history_title_binding_v16_rename_reopen'
assert ops == ['resume_chatgpt', 'wait', 'launch_prompt', 'capture_tree', 'semantic_send', 'capture_tree', 'wait', 'history_title_binding', 'finish']
assert 'global_search_binding' not in ops
assert 'history_recent_binding' not in ops
assert '{{titleSeed}}' in data['steps'][2]['prompt']

s = SVC.read_text()
assert 'case "history_title_binding"' in s
assert 'HISTORY_TITLE_ROW_LONG_CLICK' in s
assert 'RENAME_CLAIM' not in s  # claim logging is centralized in LabStore
assert s.count('performAction(AccessibilityNodeInfo.ACTION_LONG_CLICK)') == 1
assert s.count('performAction(AccessibilityNodeInfo.ACTION_SET_TEXT') == 2
assert s.count('performAction(AccessibilityNodeInfo.ACTION_CLICK)') == 2
assert 'dispatchGesture' not in s
assert 'getBoundsInScreen' not in s
assert 'GLOBAL_ACTION_' not in s

st = STORE.read_text()
assert 'RENAME_CLAIM durable=true' in st
assert 'RENAME_RECEIPT exactTitleUnique=true' in st
assert 'VERIFIED_HISTORY_TITLE_BINDING' in st
print('Capability Lab v0.21 HistoryTitleBinding patch applied')
