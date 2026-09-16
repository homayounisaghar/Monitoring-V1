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
    'suite': 'conversation_history_title_binding_v17_temporal_diff_rename_reopen',
    'targetVersion': '1.2026.237',
    'targetSignerSha256': 'b24f4bfbb3cf293f938703b9d87027c1102cc36dc4fa206910e08927db40473c',
    'steps': [
        {'op': 'resume_chatgpt'},
        {'op': 'wait', 'ms': 700},
        {'op': 'history_title_baseline', 'timeoutMs': 20000, 'settleMs': 1400},
        {
            'op': 'launch_prompt',
            'prompt': 'Capability Lab temporal History title-binding proof. Reply with exactly this marker and no other text: {{marker}}'
        },
        {'op': 'capture_tree', 'label': 'pre_send_temporal_title_draft', 'timeoutMs': 8000},
        {'op': 'semantic_send', 'timeoutMs': 15000},
        {'op': 'capture_tree', 'label': 'post_send_temporal_title_receipt', 'timeoutMs': 8000},
        {'op': 'wait', 'ms': 900},
        {'op': 'history_title_binding', 'timeoutMs': 36000, 'settleMs': 1200, 'correlationWaitMs': 15000},
        {'op': 'finish', 'inconclusiveStatus': 'INCONCLUSIVE_HISTORY_TITLE_TEMPORAL_DIFF_NOT_VERIFIED'}
    ]
}

# Stable package/signing lineage, one version bump.
gradle = GRADLE.read_text()
assert 'versionCode 21' in gradle
assert '0.21-native-capability-lab-stable-history-title-binding' in gradle
gradle = gradle.replace('versionCode 21', 'versionCode 22')
gradle = gradle.replace(
    '0.21-native-capability-lab-stable-history-title-binding',
    '0.22-native-capability-lab-stable-history-title-temporal-diff'
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
assert 'Stable v0.21' in main
main = main.replace('Stable v0.21', 'Stable v0.22')
main = main.replace(
    'tests the final HistoryTitleBinding chain after the accessibility-ID boundary closed negative on v0.20.',
    'tests a temporal History-title set-difference before the existing bounded rename/reopen chain.'
)
main = main.replace(
    'The row may be touched only when it is uniquely correlated to the currently open conversation by structural current-row state, with a unique run-specific title seed as a bounded fallback.',
    'Before creating the fresh chat it records a read-only History title baseline. After Send, a row may be touched only when History has exactly one additional row and exactly one current title is absent from that baseline; structurally-current row state remains an independent stronger signal when present.'
)
main = main.replace('RUN HISTORY TITLE BINDING PROOF', 'RUN HISTORY TITLE DIFF BINDING PROOF')
main = main.replace('HISTORY TITLE BINDING PROOF RUNNING…', 'HISTORY TITLE DIFF BINDING PROOF RUNNING…')
main = main.replace('STARTING HISTORY TITLE BINDING PROOF…', 'STARTING HISTORY TITLE DIFF BINDING PROOF…')
main = main.replace(
    'the Lab is executing one bounded HistoryTitleBinding rename/reopen proof.',
    'the Lab is executing one bounded temporal History-title diff plus rename/reopen proof.'
)
MAIN.write_text(main)

store = STORE.read_text()
assert '.putString("historyVerifiedTitle", "")' in store
store = store.replace(
    '.putString("historyVerifiedTitle", "")\n                .putBoolean("calibrationMode", false)',
    '.putString("historyVerifiedTitle", "")\n                .putString("historyTitleBaseline", "")\n                .putBoolean("calibrationMode", false)',
    1
)
assert 'static String historyVerifiedTitle(Context c)' in store
store = store.replace(
    '    static String historyVerifiedTitle(Context c) { return p(c).getString("historyVerifiedTitle", ""); }',
    '    static String historyVerifiedTitle(Context c) { return p(c).getString("historyVerifiedTitle", ""); }\n'
    '    static String historyTitleBaseline(Context c) { return p(c).getString("historyTitleBaseline", ""); }',
    1
)
anchor = '''    static void setHistoryCandidateTitle(Context c, String value) {\n        p(c).edit().putString("historyCandidateTitle", value == null ? "" : value).apply();\n    }'''
assert anchor in store
store = store.replace(
    anchor,
    anchor + '''\n    static void setHistoryTitleBaseline(Context c, String value) {\n        p(c).edit().putString("historyTitleBaseline", value == null ? "" : value).commit();\n    }''',
    1
)
STORE.write_text(store)

svc = SVC.read_text()
# Route the new read-only baseline state before the mutation state.
old_event = '''        } else if (state.startsWith("WAITING_HISTORY_RECENT_")) {\n            tryHistoryRecentBinding(expectedStep);\n        } else if (state.startsWith("WAITING_HISTORY_TITLE_")) {\n            tryHistoryTitleBinding(expectedStep);'''
new_event = '''        } else if (state.startsWith("WAITING_HISTORY_RECENT_")) {\n            tryHistoryRecentBinding(expectedStep);\n        } else if (state.startsWith("WAITING_HISTORY_TITLE_BASELINE_")) {\n            tryHistoryTitleBaseline(expectedStep);\n        } else if (state.startsWith("WAITING_HISTORY_TITLE_")) {\n            tryHistoryTitleBinding(expectedStep);'''
assert old_event in svc
svc = svc.replace(old_event, new_event, 1)

old_case = '''                case "history_recent_binding":\n                    opHistoryRecentBinding(step, i);\n                    break;\n                case "history_title_binding":'''
new_case = '''                case "history_recent_binding":\n                    opHistoryRecentBinding(step, i);\n                    break;\n                case "history_title_baseline":\n                    opHistoryTitleBaseline(step, i);\n                    break;\n                case "history_title_binding":'''
assert old_case in svc
svc = svc.replace(old_case, new_case, 1)

# The old prompt title-seed hypothesis was disproven by the v0.21 device run.
old_prompt = '        String prompt = step.optString("prompt", "Capability Lab proof {{marker}}").replace("{{marker}}", marker).replace("{{titleSeed}}", titleSeedForMarker(marker));'
assert old_prompt in svc
svc = svc.replace(
    old_prompt,
    '        String prompt = step.optString("prompt", "Capability Lab proof {{marker}}").replace("{{marker}}", marker);',
    1
)

baseline_code = r'''    private void opHistoryTitleBaseline(JSONObject step, int stepIndex) {
        if (!isCurrentStep(stepIndex)) return;
        LabStore.setState(this, "WAITING_HISTORY_TITLE_BASELINE_OPEN");
        LabStore.append(this, "HISTORY_TITLE_BASELINE_ARMED");
        armTimeout(step.optLong("timeoutMs", 20000L), "HISTORY_TITLE_BASELINE_TIMEOUT", stepIndex);
        handler.postDelayed(() -> tryHistoryTitleBaseline(stepIndex), 200L);
    }

    private void tryHistoryTitleBaseline(int expectedStep) {
        if (!isCurrentStep(expectedStep)) return;
        String state = LabStore.state(this);
        if (!state.startsWith("WAITING_HISTORY_TITLE_BASELINE_")) return;
        List<AccessibilityNodeInfo> roots = chatGptRoots();
        if (roots.isEmpty()) return;

        if ("WAITING_HISTORY_TITLE_BASELINE_OPEN".equals(state)) {
            if (isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots)) {
                armHistoryTitleBaselineSettle(expectedStep);
                return;
            }
            AccessibilityNodeInfo historyEntry = findUniqueHistoryEntryAcrossRoots(roots);
            if (historyEntry == null) return;
            LabStore.setState(this, "WAITING_HISTORY_TITLE_BASELINE_DRAWER");
            if (!performBoundedNavigation(historyEntry, "HISTORY_TITLE_BASELINE_OPEN",
                    "Open conversation history", "Open sidebar", "Open navigation",
                    "Open navigation menu", "Navigation menu", "Menu")) {
                failRun("HISTORY_TITLE_BASELINE_OPEN_ACTION_FALSE");
                return;
            }
            handler.postDelayed(() -> tryHistoryTitleBaseline(expectedStep), 280L);
            return;
        }

        if ("WAITING_HISTORY_TITLE_BASELINE_DRAWER".equals(state)) {
            if (!(isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots))) return;
            armHistoryTitleBaselineSettle(expectedStep);
            return;
        }

        if ("WAITING_HISTORY_TITLE_BASELINE_SETTLE".equals(state)) {
            if (!(isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots))) return;
            long remaining = LabStore.waitUntil(this) - System.currentTimeMillis();
            if (remaining > 0L) {
                handler.postDelayed(() -> tryHistoryTitleBaseline(expectedStep), Math.min(remaining, 250L));
                return;
            }
            List<AccessibilityNodeInfo> rows = historyConversationRows(roots);
            String baseline = serializeHistoryTitleBaseline(rows);
            LabStore.setHistoryTitleBaseline(this, baseline);
            LabStore.append(this, "HISTORY_TITLE_BASELINE_CAPTURED rowCount=" + rows.size()
                    + " titledCount=" + countSerializedBaselineTitles(baseline)
                    + " baseline=" + LabStore.abbrev(baseline.replace('\n', '|'), 12000));
            cancelTimeout();
            completeStep(expectedStep);
        }
    }

    private void armHistoryTitleBaselineSettle(int expectedStep) {
        long settle = 1400L;
        try {
            JSONObject step = steps().getJSONObject(expectedStep);
            settle = Math.max(300L, Math.min(step.optLong("settleMs", 1400L), 5000L));
        } catch (Throwable ignored) {}
        LabStore.setWaitUntil(this, System.currentTimeMillis() + settle);
        LabStore.setState(this, "WAITING_HISTORY_TITLE_BASELINE_SETTLE");
        LabStore.append(this, "HISTORY_TITLE_BASELINE_SETTLE ms=" + settle);
        handler.postDelayed(() -> tryHistoryTitleBaseline(expectedStep), Math.min(settle, 300L));
    }

    private String normalizeHistoryTitle(String raw) {
        if (raw == null) return "";
        return raw.trim().toLowerCase(Locale.US).replaceAll("\\s+", " ");
    }

    private String serializeHistoryTitleBaseline(List<AccessibilityNodeInfo> rows) {
        StringBuilder b = new StringBuilder();
        int count = rows == null ? 0 : rows.size();
        b.append("#rows=").append(count);
        if (rows != null) {
            for (AccessibilityNodeInfo row : rows) {
                String title = normalizeHistoryTitle(historyRowTitle(row));
                if (!title.isEmpty()) b.append('\n').append(title);
            }
        }
        return b.toString();
    }

    private int baselineHistoryRowCount(String baseline) {
        if (baseline == null) return -1;
        String[] lines = baseline.split("\\n");
        if (lines.length == 0 || !lines[0].startsWith("#rows=")) return -1;
        try { return Integer.parseInt(lines[0].substring(6)); }
        catch (Throwable ignored) { return -1; }
    }

    private int countSerializedBaselineTitles(String baseline) {
        if (baseline == null || baseline.isEmpty()) return 0;
        int count = 0;
        for (String line : baseline.split("\\n")) {
            if (!line.isEmpty() && !line.startsWith("#rows=")) count++;
        }
        return count;
    }

    private int countBaselineTitle(String baseline, String normalizedTitle) {
        if (baseline == null || normalizedTitle == null || normalizedTitle.isEmpty()) return 0;
        int count = 0;
        for (String line : baseline.split("\\n")) {
            if (normalizedTitle.equals(line)) count++;
        }
        return count;
    }

    private int countCurrentNormalizedTitle(List<AccessibilityNodeInfo> rows, String normalizedTitle) {
        if (rows == null || normalizedTitle == null || normalizedTitle.isEmpty()) return 0;
        int count = 0;
        for (AccessibilityNodeInfo row : rows) {
            if (normalizedTitle.equals(normalizeHistoryTitle(historyRowTitle(row)))) count++;
        }
        return count;
    }

'''
insert_anchor = '    private String titleSeedForMarker(String marker) {'
assert insert_anchor in svc
svc = svc.replace(insert_anchor, baseline_code + insert_anchor, 1)

# Replace v0.21 row correlation with baseline -> fresh temporal set-difference.
pattern = r'    private AccessibilityNodeInfo uniqueFreshRowForRename\(List<AccessibilityNodeInfo> rows\) \{.*?(?=    private String historyTitleRowStateCensus\(List<AccessibilityNodeInfo> rows\))'
new_method = r'''    private AccessibilityNodeInfo uniqueFreshRowForRename(List<AccessibilityNodeInfo> rows) {
        AccessibilityNodeInfo current = uniqueStructurallyCurrentHistoryRow(rows);
        if (current != null) {
            LabStore.append(this, "HISTORY_TITLE_ROW_CORRELATION source=unique_structurally_current");
            return current;
        }

        String baseline = LabStore.historyTitleBaseline(this);
        int baselineRows = baselineHistoryRowCount(baseline);
        if (baselineRows < 0) {
            LabStore.append(this, "HISTORY_TITLE_ROW_CORRELATION source=temporal_title_diff baseline=missing");
            return null;
        }
        boolean rowDeltaOne = rows != null && rows.size() == baselineRows + 1;
        AccessibilityNodeInfo found = null;
        int candidateCount = 0;
        StringBuilder added = new StringBuilder();
        if (rows != null) {
            for (AccessibilityNodeInfo row : rows) {
                String title = normalizeHistoryTitle(historyRowTitle(row));
                if (title.isEmpty()) continue;
                int before = countBaselineTitle(baseline, title);
                int now = countCurrentNormalizedTitle(rows, title);
                if (before != 0 || now != 1) continue;
                candidateCount++;
                found = row;
                if (added.length() > 0) added.append(" || ");
                added.append(title);
            }
        }
        LabStore.append(this, "HISTORY_TITLE_ROW_CORRELATION source=temporal_title_diff"
                + " baselineRows=" + baselineRows
                + " currentRows=" + (rows == null ? 0 : rows.size())
                + " rowDeltaOne=" + rowDeltaOne
                + " candidates=" + candidateCount
                + " addedTitles=" + LabStore.abbrev(added.toString(), 1200));
        return rowDeltaOne && candidateCount == 1 ? found : null;
    }

'''
svc, n = re.subn(pattern, lambda m: new_method, svc, count=1, flags=re.S)
assert n == 1

# v0.22 waits for asynchronous title generation instead of immediately giving up.
old_no_row = '''            if (row == null) {\n                LabStore.append(this, "HISTORY_TITLE_NO_SAFE_FRESH_ROW currentRows="\n                        + countStructurallyCurrentHistoryRows(rows)\n                        + " seed=" + titleSeedForMarker(LabStore.marker(this))\n                        + " action=observation_only_no_row_mutation");\n                cancelTimeout();\n                completeStep(expectedStep);\n                return;\n            }'''
assert old_no_row in svc
new_no_row = '''            if (row == null) {\n                long waitMax = 15000L;\n                try {\n                    JSONObject step = steps().getJSONObject(expectedStep);\n                    waitMax = Math.max(1500L, Math.min(step.optLong("correlationWaitMs", 15000L), 25000L));\n                } catch (Throwable ignored) {}\n                long sinceSend = LabStore.sinceSendMs(this);\n                if (sinceSend >= 0L && sinceSend < waitMax) {\n                    LabStore.append(this, "HISTORY_TITLE_CORRELATION_WAIT sinceSendMs=" + sinceSend\n                            + " maxMs=" + waitMax\n                            + " action=read_only_retry_no_row_mutation");\n                    handler.postDelayed(() -> tryHistoryTitleBinding(expectedStep), 750L);\n                    return;\n                }\n                LabStore.append(this, "HISTORY_TITLE_NO_SAFE_FRESH_ROW currentRows="\n                        + countStructurallyCurrentHistoryRows(rows)\n                        + " baselineRows=" + baselineHistoryRowCount(LabStore.historyTitleBaseline(this))\n                        + " action=observation_only_no_row_mutation");\n                cancelTimeout();\n                completeStep(expectedStep);\n                return;\n            }'''
svc = svc.replace(old_no_row, new_no_row, 1)

# Update armed evidence so the report makes the actual hypothesis explicit.
old_armed = '''        LabStore.append(this, "HISTORY_TITLE_BINDING_ARMED marker=" + LabStore.marker(this)\n                + " titleSeed=" + titleSeedForMarker(LabStore.marker(this))\n                + " renameTitle=" + renameTitleForMarker(LabStore.marker(this)));'''
assert old_armed in svc
new_armed = '''        LabStore.append(this, "HISTORY_TITLE_BINDING_ARMED marker=" + LabStore.marker(this)\n                + " baselineRows=" + baselineHistoryRowCount(LabStore.historyTitleBaseline(this))\n                + " renameTitle=" + renameTitleForMarker(LabStore.marker(this)));'''
svc = svc.replace(old_armed, new_armed, 1)

SVC.write_text(svc)

# Patcher self-checks.
assert 'versionCode 22' in GRADLE.read_text()
assert 'history_title_baseline' in PLAN.read_text()
assert 'conversation_history_title_binding_v17_temporal_diff_rename_reopen' in PLAN.read_text()
s = SVC.read_text()
assert 'case "history_title_baseline"' in s
assert 'HISTORY_TITLE_BASELINE_CAPTURED' in s
assert 'source=temporal_title_diff' in s
assert 'rowDeltaOne' in s
assert 'HISTORY_TITLE_CORRELATION_WAIT' in s
assert 'RENAME_CLAIM' not in s
print('Applied Capability Lab v0.22 temporal History title diff patch')
