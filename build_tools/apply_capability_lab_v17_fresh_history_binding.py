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

OLD_SUITE = 'conversation_search_binding_v11_fresh_index_trigger_ladder'
NEW_SUITE = 'conversation_history_binding_v12_fresh_recent_reopen'
NEW_VERSION_NAME = '0.17-native-capability-lab-stable-fresh-history-binding'


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if old not in text:
        raise SystemExit(f'anchor missing in {path}: {old[:140]!r}')
    path.write_text(text.replace(old, new, 1))


def regex_replace_once(path: Path, pattern: str, repl: str, flags=0) -> None:
    text = path.read_text()
    new, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'regex anchor missing/ambiguous in {path}: {pattern}')
    path.write_text(new)


# ---- Store: persist a separate verified History binding and row-local candidates. ----
replace_once(
    STORE,
    '''                .putBoolean("searchBindingVerified", false)\n                .putString("candidates", "")\n''',
    '''                .putBoolean("searchBindingVerified", false)\n                .putBoolean("historyBindingVerified", false)\n                .putString("historyCandidateTitle", "")\n                .putString("historyVerifiedTitle", "")\n                .putString("candidates", "")\n''')
replace_once(
    STORE,
    '''    static boolean searchBindingVerified(Context c) { return p(c).getBoolean("searchBindingVerified", false); }\n    static int candidateIndex(Context c) { return p(c).getInt("candidateIndex", 0); }\n''',
    '''    static boolean searchBindingVerified(Context c) { return p(c).getBoolean("searchBindingVerified", false); }\n    static boolean historyBindingVerified(Context c) { return p(c).getBoolean("historyBindingVerified", false); }\n    static String historyCandidateTitle(Context c) { return p(c).getString("historyCandidateTitle", ""); }\n    static String historyVerifiedTitle(Context c) { return p(c).getString("historyVerifiedTitle", ""); }\n    static int candidateIndex(Context c) { return p(c).getInt("candidateIndex", 0); }\n''')
replace_once(
    STORE,
    '''    static void setCandidateIndex(Context c, int value) { p(c).edit().putInt("candidateIndex", value).apply(); }\n''',
    '''    static void setCandidateIndex(Context c, int value) { p(c).edit().putInt("candidateIndex", value).apply(); }\n    static void setHistoryCandidateTitle(Context c, String value) {\n        p(c).edit().putString("historyCandidateTitle", value == null ? "" : value).apply();\n    }\n''')
replace_once(
    STORE,
    '''    static synchronized void markVerified(Context c, String id) {\n''',
    '''    static synchronized void markHistoryBindingVerified(Context c, String title) {\n        if (historyBindingVerified(c)) return;\n        String safeTitle = title == null ? "" : title;\n        p(c).edit()\n                .putBoolean("historyBindingVerified", true)\n                .putString("historyVerifiedTitle", safeTitle)\n                .commit();\n        append(c, "VERIFIED_HISTORY_RECENT_BINDING marker=" + marker(c)\n                + " title=" + abbrev(safeTitle, 180));\n    }\n\n    static synchronized void clearCandidates(Context c) {\n        p(c).edit().putString("candidates", "").putInt("candidateIndex", 0).commit();\n        append(c, "CANDIDATES_CLEARED scope=history_selected_row");\n    }\n\n    static synchronized void markVerified(Context c, String id) {\n''')
replace_once(
    STORE,
    '''                + " searchBinding=" + searchBindingVerified(c)\n                + " sinceSendMs=" + sinceSendMs(c)\n''',
    '''                + " searchBinding=" + searchBindingVerified(c)\n                + " historyBinding=" + historyBindingVerified(c)\n                + " historyTitle=" + historyVerifiedTitle(c)\n                + " sinceSendMs=" + sinceSendMs(c)\n''')

# ---- Accessibility runner: new bounded fresh History recent-row binding primitive. ----
replace_once(
    SVC,
    '''        } else if (state.startsWith("WAITING_HISTORY_REFRESH")) {\n            tryHistoryRefresh(expectedStep);\n''',
    '''        } else if (state.startsWith("WAITING_HISTORY_RECENT_")) {\n            tryHistoryRecentBinding(expectedStep);\n        } else if (state.startsWith("WAITING_HISTORY_REFRESH")) {\n            tryHistoryRefresh(expectedStep);\n''')
replace_once(
    SVC,
    '''                case "history_refresh":\n                    opHistoryRefresh(step, i);\n                    break;\n''',
    '''                case "history_recent_binding":\n                    opHistoryRecentBinding(step, i);\n                    break;\n                case "history_refresh":\n                    opHistoryRefresh(step, i);\n                    break;\n''')
replace_once(
    SVC,
    '''                    } else if (LabStore.searchBindingVerified(this)) {\n                        LabStore.finish(this, "PASS_VERIFIED_SEARCH_BINDING");\n                    } else {\n''',
    '''                    } else if (LabStore.historyBindingVerified(this)) {\n                        LabStore.finish(this, "PASS_VERIFIED_HISTORY_RECENT_BINDING");\n                    } else if (LabStore.searchBindingVerified(this)) {\n                        LabStore.finish(this, "PASS_VERIFIED_SEARCH_BINDING");\n                    } else {\n''')

anchor = '    private void opHistoryRefresh(JSONObject step, int stepIndex) {'
text = SVC.read_text()
if anchor not in text:
    raise SystemExit('opHistoryRefresh anchor missing')
helpers = r'''    private void opHistoryRecentBinding(JSONObject step, int stepIndex) {
        if (!isCurrentStep(stepIndex)) return;
        LabStore.setState(this, "WAITING_HISTORY_RECENT_OPEN_INITIAL");
        LabStore.append(this, "HISTORY_RECENT_BINDING_ARMED marker=" + LabStore.marker(this));
        armTimeout(step.optLong("timeoutMs", 20000L), "HISTORY_RECENT_BINDING_TIMEOUT", stepIndex);
        handler.postDelayed(() -> tryHistoryRecentBinding(stepIndex), 200L);
    }

    private void tryHistoryRecentBinding(int expectedStep) {
        if (!isCurrentStep(expectedStep)) return;
        String state = LabStore.state(this);
        if (!state.startsWith("WAITING_HISTORY_RECENT_")) return;
        List<AccessibilityNodeInfo> roots = chatGptRoots();
        if (roots.isEmpty()) return;

        if ("WAITING_HISTORY_RECENT_OPEN_INITIAL".equals(state)) {
            if (isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots)) {
                recordHistoryRecentDrawer("before_switch_away", roots);
                switchAwayFromFreshThread(expectedStep, roots);
                return;
            }
            AccessibilityNodeInfo historyEntry = findUniqueHistoryEntryAcrossRoots(roots);
            if (historyEntry == null) return;
            LabStore.setState(this, "WAITING_HISTORY_RECENT_WAIT_INITIAL_DRAWER");
            if (!performBoundedNavigation(historyEntry, "HISTORY_RECENT_OPEN_INITIAL",
                    "Open conversation history", "Open sidebar", "Open navigation",
                    "Open navigation menu", "Navigation menu", "Menu")) {
                failRun("HISTORY_RECENT_OPEN_INITIAL_ACTION_FALSE");
                return;
            }
            handler.postDelayed(() -> tryHistoryRecentBinding(expectedStep), 280L);
            return;
        }

        if ("WAITING_HISTORY_RECENT_WAIT_INITIAL_DRAWER".equals(state)) {
            if (!(isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots))) return;
            recordHistoryRecentDrawer("before_switch_away", roots);
            switchAwayFromFreshThread(expectedStep, roots);
            return;
        }

        if ("WAITING_HISTORY_RECENT_SWITCH_AWAY".equals(state)) {
            if (isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots)) return;
            if (findRuntimeSearchSurfaceRoot(roots) != null || anyGlobalSearchScreen(roots)) return;
            AccessibilityNodeInfo active = getRootInActiveWindow();
            String snapshot = active == null ? "<no active root>"
                    : normalizedTree(active, LabStore.marker(this), 260, 11);
            LabStore.append(this, "HISTORY_RECENT_SWITCH_AWAY_RECEIPT surface=chat_or_starter"
                    + " activeSnapshot=" + LabStore.abbrev(snapshot, 12000));
            LabStore.setState(this, "WAITING_HISTORY_RECENT_REOPEN_HISTORY");
            handler.postDelayed(() -> tryHistoryRecentBinding(expectedStep), 260L);
            return;
        }

        if ("WAITING_HISTORY_RECENT_REOPEN_HISTORY".equals(state)) {
            if (isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots)) {
                prepareHistoryRecentRows(expectedStep, roots);
                return;
            }
            AccessibilityNodeInfo historyEntry = findUniqueHistoryEntryAcrossRoots(roots);
            if (historyEntry == null) return;
            LabStore.setState(this, "WAITING_HISTORY_RECENT_WAIT_REOPENED_DRAWER");
            if (!performBoundedNavigation(historyEntry, "HISTORY_RECENT_REOPEN_HISTORY",
                    "Open conversation history", "Open sidebar", "Open navigation",
                    "Open navigation menu", "Navigation menu", "Menu")) {
                failRun("HISTORY_RECENT_REOPEN_HISTORY_ACTION_FALSE");
                return;
            }
            handler.postDelayed(() -> tryHistoryRecentBinding(expectedStep), 280L);
            return;
        }

        if ("WAITING_HISTORY_RECENT_WAIT_REOPENED_DRAWER".equals(state)) {
            if (!(isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots))) return;
            prepareHistoryRecentRows(expectedStep, roots);
            return;
        }

        if ("WAITING_HISTORY_RECENT_SETTLE".equals(state)) {
            if (!(isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots))) return;
            long remaining = LabStore.waitUntil(this) - System.currentTimeMillis();
            if (remaining > 0L) {
                handler.postDelayed(() -> tryHistoryRecentBinding(expectedStep), Math.min(remaining, 250L));
                return;
            }
            evaluateHistoryRecentRows(expectedStep, roots);
            return;
        }

        if ("WAITING_HISTORY_RECENT_VERIFY_REOPEN".equals(state)) {
            if (isRuntimeHistoryDrawer(roots) || anyHistoryDrawerScreen(roots)) return;
            AccessibilityNodeInfo active = getRootInActiveWindow();
            if (active == null || !isChatGptRoot(active)) return;
            MarkerCounts counts = countMarkerNodes(active, LabStore.marker(this));
            if (counts.editable == 0 && counts.nonEditable >= 1) {
                cancelTimeout();
                String title = LabStore.historyCandidateTitle(this);
                LabStore.append(this, "HISTORY_RECENT_REOPEN_VERIFIED markerEditable=" + counts.editable
                        + " markerNonEditable=" + counts.nonEditable
                        + " title=" + LabStore.abbrev(title, 180));
                LabStore.markHistoryBindingVerified(this, title);
                completeStep(expectedStep);
                return;
            }
            long remaining = LabStore.waitUntil(this) - System.currentTimeMillis();
            if (remaining > 0L) {
                handler.postDelayed(() -> tryHistoryRecentBinding(expectedStep), Math.min(remaining, 250L));
                return;
            }
            String snapshot = normalizedTree(active, LabStore.marker(this), 320, 12);
            LabStore.append(this, "HISTORY_RECENT_TOP_ROW_MISMATCH title="
                    + LabStore.abbrev(LabStore.historyCandidateTitle(this), 180)
                    + " markerEditable=" + counts.editable
                    + " markerNonEditable=" + counts.nonEditable
                    + " activeSnapshot=" + LabStore.abbrev(snapshot, 16000));
            LabStore.clearCandidates(this);
            cancelTimeout();
            completeStep(expectedStep);
        }
    }

    private void switchAwayFromFreshThread(int expectedStep, List<AccessibilityNodeInfo> roots) {
        int newChatCount = countExactSemanticAcrossRoots(roots, "New chat");
        LabStore.append(this, "HISTORY_RECENT_NEW_CHAT_EXACT_MATCHES=" + newChatCount);
        if (newChatCount != 1) {
            failRun("HISTORY_RECENT_NEW_CHAT_NOT_UNIQUE count=" + newChatCount);
            return;
        }
        AccessibilityNodeInfo newChat = findUniqueExactSemanticAcrossRoots(roots, "New chat");
        if (newChat == null) {
            failRun("HISTORY_RECENT_NEW_CHAT_MISSING");
            return;
        }
        LabStore.setState(this, "WAITING_HISTORY_RECENT_SWITCH_AWAY");
        if (!performBoundedNavigation(newChat, "HISTORY_RECENT_SWITCH_AWAY", "New chat")) {
            failRun("HISTORY_RECENT_SWITCH_AWAY_ACTION_FALSE");
            return;
        }
        handler.postDelayed(() -> tryHistoryRecentBinding(expectedStep), 320L);
    }

    private void prepareHistoryRecentRows(int expectedStep, List<AccessibilityNodeInfo> roots) {
        recordHistoryRecentDrawer("after_switch_away", roots);
        JSONObject step = currentPlanStep(expectedStep);
        long settleMs = step == null ? 1200L : Math.max(300L, Math.min(step.optLong("settleMs", 1200L), 5000L));
        LabStore.setWaitUntil(this, System.currentTimeMillis() + settleMs);
        LabStore.setState(this, "WAITING_HISTORY_RECENT_SETTLE");
        LabStore.append(this, "HISTORY_RECENT_SETTLE ms=" + settleMs);
        handler.postDelayed(() -> tryHistoryRecentBinding(expectedStep), Math.min(settleMs, 300L));
    }

    private void evaluateHistoryRecentRows(int expectedStep, List<AccessibilityNodeInfo> roots) {
        List<AccessibilityNodeInfo> rows = historyConversationRows(roots);
        StringBuilder titles = new StringBuilder();
        for (int i = 0; i < rows.size() && i < 16; i++) {
            if (titles.length() > 0) titles.append(" | ");
            titles.append(i).append(':').append(LabStore.abbrev(historyRowTitle(rows.get(i)), 120));
        }
        String snapshot = roots.isEmpty() ? "<no ChatGPT roots>"
                : normalizedTree(roots.get(0), LabStore.marker(this), 520, 14);
        LabStore.append(this, "HISTORY_RECENT_ROWS count=" + rows.size()
                + " titles=" + titles
                + " controlCensus=" + LabStore.abbrev(controlCensus(roots, 360), 26000)
                + " activeSnapshot=" + LabStore.abbrev(snapshot, 22000));
        if (rows.isEmpty()) {
            cancelTimeout();
            LabStore.append(this, "HISTORY_RECENT_NO_ROWS_AFTER_SWITCH_AWAY");
            completeStep(expectedStep);
            return;
        }

        AccessibilityNodeInfo row = rows.get(0);
        String title = historyRowTitle(row);
        LabStore.clearCandidates(this);
        LabStore.setHistoryCandidateTitle(this, title);
        MetadataStats stats = harvestAccessibilityMetadata(row);
        String rowTree = normalizedTree(row, LabStore.marker(this), 180, 7);
        LabStore.append(this, "HISTORY_RECENT_SELECTED_ROW index=0 title=" + LabStore.abbrev(title, 180)
                + " metadataNodes=" + stats.nodes
                + " extras=" + stats.extras
                + " candidateMatches=" + stats.candidateMatches
                + " rowTree=" + LabStore.abbrev(rowTree, 12000));

        LabStore.setState(this, "WAITING_HISTORY_RECENT_VERIFY_REOPEN");
        LabStore.setWaitUntil(this, System.currentTimeMillis() + 1800L);
        if (!performBoundedNavigation(row, "HISTORY_RECENT_ROW_OPEN")) {
            failRun("HISTORY_RECENT_ROW_OPEN_ACTION_FALSE");
            return;
        }
        handler.postDelayed(() -> tryHistoryRecentBinding(expectedStep), 300L);
    }

    private void recordHistoryRecentDrawer(String phase, List<AccessibilityNodeInfo> roots) {
        String snapshot = roots.isEmpty() ? "<no ChatGPT roots>"
                : normalizedTree(roots.get(0), LabStore.marker(this), 520, 14);
        LabStore.append(this, "HISTORY_RECENT_DRAWER phase=" + phase
                + " rows=" + historyConversationRows(roots).size()
                + " controlCensus=" + LabStore.abbrev(controlCensus(roots, 360), 26000)
                + " activeSnapshot=" + LabStore.abbrev(snapshot, 22000));
    }

    private List<AccessibilityNodeInfo> historyConversationRows(List<AccessibilityNodeInfo> roots) {
        List<AccessibilityNodeInfo> out = new ArrayList<>();
        if (roots == null) return out;
        for (AccessibilityNodeInfo root : roots) {
            collectHistoryConversationRows(root, out, 0);
            if (out.size() >= 40) break;
        }
        return out;
    }

    private void collectHistoryConversationRows(AccessibilityNodeInfo node,
                                                List<AccessibilityNodeInfo> out,
                                                int depth) {
        if (node == null || depth > 24 || out.size() >= 40) return;
        if (node.isVisibleToUser() && node.isEnabled() && node.isClickable()
                && hasAction(node, AccessibilityNodeInfo.ACTION_CLICK)
                && hasAction(node, AccessibilityNodeInfo.ACTION_LONG_CLICK)) {
            String title = historyRowTitle(node);
            if (!title.isEmpty()) {
                out.add(node);
                return;
            }
        }
        for (int i = 0; i < node.getChildCount(); i++) {
            collectHistoryConversationRows(node.getChild(i), out, depth + 1);
            if (out.size() >= 40) return;
        }
    }

    private String historyRowTitle(AccessibilityNodeInfo row) {
        return historyRowTitle(row, 0);
    }

    private String historyRowTitle(AccessibilityNodeInfo node, int depth) {
        if (node == null || depth > 6) return "";
        CharSequence text = node.getText();
        if (text != null) {
            String value = text.toString().trim();
            String cls = String.valueOf(node.getClassName());
            if (!value.isEmpty() && cls.endsWith("TextView")
                    && !"New chat".equals(value) && !"Search".equals(value)
                    && !"Close".equals(value)) return value;
        }
        for (int i = 0; i < node.getChildCount(); i++) {
            String value = historyRowTitle(node.getChild(i), depth + 1);
            if (!value.isEmpty()) return value;
        }
        return "";
    }

'''
SVC.write_text(text.replace(anchor, helpers + anchor, 1))

# ---- Main UI: direct Downloads export, no Share sheet, updated run semantics. ----
main = MAIN.read_text()
main = main.replace('import android.content.Context;\n', 'import android.content.Context;\nimport android.content.ContentValues;\n')
main = main.replace('import android.os.Bundle;\n', 'import android.os.Bundle;\nimport android.os.Environment;\n')
main = main.replace('import android.provider.Settings;\n', 'import android.provider.Settings;\nimport android.provider.MediaStore;\n')
main = main.replace('import android.widget.TextView;\n', 'import android.widget.TextView;\nimport android.widget.Toast;\n')
main = main.replace('import androidx.core.content.FileProvider;\n\n', '')
main = main.replace('import java.io.File;\n', 'import java.io.File;\nimport java.io.FileInputStream;\nimport java.io.OutputStream;\n')
main = re.sub(
    r'    private static final String SCREEN_DESCRIPTION =\n.*?;\n\n    private final Handler handler',
    '''    private static final String SCREEN_DESCRIPTION =\n            "Stable v0.17 tests a fresh History binding that does not depend on Global Search indexing. It creates one synthetic marker chat, sends exactly once with the proven CLAIM/no-replay Send contract, opens official History, deliberately switches away through the exact New chat control, reopens History, selects only the first semantic conversation row, harvests that row metadata, and requires the exact marker on the reopened thread.\\n\\nThe full report file remains authoritative and captures the relevant ChatGPT Accessibility surfaces. DOWNLOAD FULL REPORT saves it directly to Android Downloads with one tap and no share sheet. No private ChatGPT API is called, no credentials are extracted, and no coordinate writes, gestures, or global actions are used.";\n\n    private final Handler handler''',
    main,
    count=1,
    flags=re.S)
main = main.replace('RUN FRESH INDEX TRIGGER LADDER', 'RUN FRESH HISTORY BINDING PROOF')
main = main.replace('SHARE FULL REPORT FILE', 'DOWNLOAD FULL REPORT')
main = main.replace('shareReportFile()', 'downloadReportFile()')
main = main.replace('STARTING INDEX TRIGGER LADDER…', 'STARTING FRESH HISTORY BINDING PROOF…')
main = main.replace('the Lab is executing several bounded official-UI indexing probes in one run.',
                    'the Lab is executing one bounded official-UI fresh History binding proof.')
main = main.replace('one tap creates one synthetic chat and runs the full trigger ladder.',
                    'one tap creates one synthetic chat, switches away, reopens History, and verifies the newest semantic row.')
main = re.sub(
    r'    private void downloadReportFile\(\) \{.*?\n    \}\n\n    private void refreshUi\(\) \{',
    '''    private void downloadReportFile() {\n        Uri outUri = null;\n        try {\n            File f = LabStore.ensureReportFile(this);\n            if (f == null || !f.exists()) {\n                LabStore.append(this, "REPORT_FILE_DOWNLOAD_ERROR missing_report_file");\n                refreshUi();\n                return;\n            }\n            LabStore.append(this, "REPORT_FILE_DOWNLOAD_STARTED name=" + f.getName());\n            ContentValues values = new ContentValues();\n            values.put(MediaStore.MediaColumns.DISPLAY_NAME, f.getName());\n            values.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");\n            values.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);\n            values.put(MediaStore.MediaColumns.IS_PENDING, 1);\n            outUri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);\n            if (outUri == null) throw new IllegalStateException("Downloads insert returned null");\n            try (FileInputStream in = new FileInputStream(f);\n                 OutputStream out = getContentResolver().openOutputStream(outUri, "w")) {\n                if (out == null) throw new IllegalStateException("Downloads output stream null");\n                byte[] buf = new byte[8192];\n                int n;\n                while ((n = in.read(buf)) >= 0) out.write(buf, 0, n);\n                out.flush();\n            }\n            ContentValues done = new ContentValues();\n            done.put(MediaStore.MediaColumns.IS_PENDING, 0);\n            getContentResolver().update(outUri, done, null, null);\n            LabStore.append(this, "REPORT_FILE_DOWNLOAD_SUCCESS name=" + f.getName());\n            Toast.makeText(this, "Saved to Downloads: " + f.getName(), Toast.LENGTH_LONG).show();\n        } catch (Throwable t) {\n            if (outUri != null) {\n                try { getContentResolver().delete(outUri, null, null); } catch (Throwable ignored) {}\n            }\n            LabStore.append(this, "REPORT_FILE_DOWNLOAD_ERROR " + t.getClass().getSimpleName()\n                    + ":" + LabStore.abbrev(String.valueOf(t.getMessage()), 220));\n            Toast.makeText(this, "Could not save report", Toast.LENGTH_LONG).show();\n            refreshUi();\n        }\n    }\n\n    private void refreshUi() {''',
    main,
    count=1,
    flags=re.S)
if 'private void downloadReportFile()' not in main:
    raise SystemExit('downloadReportFile replacement failed')
MAIN.write_text(main)

# ---- Version and plan. ----
replace_once(BUILD, 'versionCode 16', 'versionCode 17')
replace_once(BUILD,
             'versionName "0.16-native-capability-lab-stable-index-trigger-ladder"',
             f'versionName "{NEW_VERSION_NAME}"')

plan = {
    'schema': 1,
    'suite': NEW_SUITE,
    'targetVersion': '1.2026.237',
    'targetSignerSha256': 'b24f4bfbb3cf293f938703b9d87027c1102cc36dc4fa206910e08927db40473c',
    'steps': [
        {'op': 'launch_prompt', 'prompt': 'Capability Lab fresh History binding proof. Reply with exactly this marker and no other text: {{marker}}'},
        {'op': 'capture_tree', 'label': 'pre_send_draft_baseline', 'timeoutMs': 8000},
        {'op': 'semantic_send', 'timeoutMs': 15000},
        {'op': 'capture_tree', 'label': 'post_send_receipt', 'timeoutMs': 8000},
        {'op': 'wait', 'ms': 800},
        {'op': 'history_recent_binding', 'timeoutMs': 20000, 'settleMs': 1200},
        {'op': 'verify_candidates'},
        {'op': 'finish', 'inconclusiveStatus': 'INCONCLUSIVE_FRESH_HISTORY_RECENT_BINDING_NOT_FOUND'},
    ],
}
PLAN.write_text(json.dumps(plan, indent=2) + '\n')
fallback = json.dumps(plan, separators=(',', ':'))
escaped = fallback.replace('\\', '\\\\').replace('"', '\\"')
loader = PLAN_LOADER.read_text()
loader, n = re.subn(
    r'    static final String FALLBACK = .*?;\n\n    private PlanLoader\(\) \{\}',
    f'    static final String FALLBACK = "{escaped}";\\n\\n    private PlanLoader() {{}}',
    loader,
    count=1,
    flags=re.S)
if n != 1:
    raise SystemExit('PlanLoader FALLBACK replacement failed')
PLAN_LOADER.write_text(loader)

# ---- Public CI: replace with a compact v0.17 source/build gate. ----
CI.write_text(r'''name: Native Capability Lab

on:
  push:
    branches: [build/pebble-chat-bridge-v019]
    paths:
      - 'runtime_probes/native-capability-lab/**'
      - '.github/workflows/native-capability-lab.yml'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build-and-verify:
    runs-on: ubuntu-latest
    timeout-minutes: 25
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
      - uses: android-actions/setup-android@v3
      - name: Source and safety prechecks
        run: |
          python3 - <<'PY'
          import json
          from pathlib import Path
          root=Path('runtime_probes/native-capability-lab')
          svc=(root/'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java').read_text()
          store=(root/'app/src/main/java/com/openai/controlplane/capabilitylab/LabStore.java').read_text()
          main=(root/'app/src/main/java/com/openai/controlplane/capabilitylab/MainActivity.java').read_text()
          build=(root/'app/build.gradle').read_text()
          plan=json.loads((root/'plans/default.json').read_text())
          assert 'versionCode 17' in build
          assert '0.17-native-capability-lab-stable-fresh-history-binding' in build
          assert plan['suite']=='conversation_history_binding_v12_fresh_recent_reopen'
          ops=[x['op'] for x in plan['steps']]
          assert ops.count('launch_prompt')==1
          assert ops.count('semantic_send')==1
          assert ops.count('history_recent_binding')==1
          assert ops.count('verify_candidates')==1
          assert ops.count('global_search_binding')==0
          assert 'case "history_recent_binding"' in svc
          assert 'HISTORY_RECENT_SWITCH_AWAY' in svc
          assert 'HISTORY_RECENT_ROWS' in svc
          assert 'HISTORY_RECENT_REOPEN_VERIFIED' in svc
          assert 'harvestAccessibilityMetadata(row)' in svc
          assert 'markHistoryBindingVerified' in store
          assert 'CANDIDATES_CLEARED scope=history_selected_row' in store
          assert svc.count('performAction(AccessibilityNodeInfo.ACTION_CLICK)') == 2
          assert svc.count('performAction(AccessibilityNodeInfo.ACTION_SET_TEXT') == 1
          for forbidden in ('getBoundsInScreen','dispatchGesture','GLOBAL_ACTION_'):
              assert forbidden not in svc
          assert 'DOWNLOAD FULL REPORT' in main
          assert 'MediaStore.Downloads.EXTERNAL_CONTENT_URI' in main
          assert 'Intent.createChooser' not in main
          assert 'FileProvider.getUriForFile' not in main
          print('v0.17 safety prechecks OK')
          PY
          git diff --check
      - name: Build debug APK
        working-directory: runtime_probes/native-capability-lab
        run: |
          chmod +x gradlew
          ./gradlew --no-daemon :app:assembleDebug
      - name: Verify APK exists
        run: |
          test -s runtime_probes/native-capability-lab/app/build/outputs/apk/debug/app-debug.apk
          sha256sum runtime_probes/native-capability-lab/app/build/outputs/apk/debug/app-debug.apk
      - uses: actions/upload-artifact@v4
        with:
          name: native-capability-lab-v017-debug
          path: runtime_probes/native-capability-lab/app/build/outputs/apk/debug/app-debug.apk
          if-no-files-found: error
''')

# Final static invariants before the patch commit is allowed.
svc = SVC.read_text()
main = MAIN.read_text()
assert svc.count('performAction(AccessibilityNodeInfo.ACTION_CLICK)') == 2
assert svc.count('performAction(AccessibilityNodeInfo.ACTION_SET_TEXT') == 1
assert 'getBoundsInScreen' not in svc
assert 'dispatchGesture' not in svc
assert 'GLOBAL_ACTION_' not in svc
assert 'HISTORY_RECENT_REOPEN_VERIFIED' in svc
assert 'MediaStore.Downloads.EXTERNAL_CONTENT_URI' in main
assert 'Intent.createChooser' not in main
print('Applied Stable Capability Lab v0.17 fresh History binding proof')
