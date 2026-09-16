from pathlib import Path
import json

root = Path('runtime_probes/native-capability-lab')
svc_path = root / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java'
svc = svc_path.read_text()

old = '''    private void opGlobalSearchBinding(JSONObject step, int stepIndex) {
        if (!isCurrentStep(stepIndex)) return;
        LabStore.setState(this, "WAITING_GLOBAL_SEARCH_ENTRY");
        List<AccessibilityNodeInfo> roots = chatGptRoots();
'''
new = '''    private void opGlobalSearchBinding(JSONObject step, int stepIndex) {
        if (!isCurrentStep(stepIndex)) return;
        String requestedMarker = step.optString("marker", "").trim();
        if (!requestedMarker.isEmpty()) {
            if (!requestedMarker.matches("LAB_CID_[0-9A-F]{16}")) {
                failRun("GLOBAL_SEARCH_PLAN_MARKER_INVALID");
                return;
            }
            LabStore.setMarker(this, requestedMarker);
            LabStore.append(this, "GLOBAL_SEARCH_MARKER_OVERRIDE source=plan marker=" + requestedMarker);
        }
        LabStore.setState(this, "WAITING_GLOBAL_SEARCH_ENTRY");
        List<AccessibilityNodeInfo> roots = chatGptRoots();
'''
if old not in svc:
    raise SystemExit('opGlobalSearchBinding anchor not found')
svc = svc.replace(old, new, 1)

old = '''        if ("WAITING_GLOBAL_SEARCH_ENTRY".equals(state)) {
            if (anyGlobalSearchScreen(roots)) {
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 120L);
                return;
            }
'''
new = '''        if ("WAITING_GLOBAL_SEARCH_ENTRY".equals(state)) {
            // An indexed-marker probe may resume ChatGPT while the first-party Search
            // surface is already open from a previous run. Accept the same strict runtime
            // Search root contract here instead of forcing a redundant Menu -> Search cycle.
            if (anyGlobalSearchScreen(roots) || findRuntimeSearchRoot(roots) != null) {
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 120L);
                return;
            }
'''
if old not in svc:
    raise SystemExit('WAITING_GLOBAL_SEARCH_ENTRY anchor not found')
svc = svc.replace(old, new, 1)

old = '''            handler.postDelayed(() -> {
                if (!isCurrentStep(expectedStep)) return;
                if (!"WAITING_GLOBAL_SEARCH_RESULT".equals(LabStore.state(this))) return;
                List<AccessibilityNodeInfo> postQueryRoots = chatGptRoots();
                LabStore.append(this, "GLOBAL_SEARCH_POST_QUERY_CONTROL_CENSUS windows="
                        + postQueryRoots.size() + " "
                        + LabStore.abbrev(controlCensus(postQueryRoots, 260), 20000));
                tryGlobalSearchBinding(expectedStep);
            }, 350L);
'''
new = '''            handler.postDelayed(() -> {
                if (!isCurrentStep(expectedStep)) return;
                if (!"WAITING_GLOBAL_SEARCH_RESULT".equals(LabStore.state(this))) return;
                List<AccessibilityNodeInfo> postQueryRoots = chatGptRoots();
                AccessibilityNodeInfo receiptRoot = findGlobalSearchRoot(postQueryRoots);
                if (receiptRoot == null) receiptRoot = findRuntimeSearchRoot(postQueryRoots);
                AccessibilityNodeInfo receiptField = receiptRoot == null ? null : findGlobalSearchField(receiptRoot);
                String actualQuery = receiptField == null || receiptField.getText() == null
                        ? "" : receiptField.getText().toString();
                boolean exactQuery = marker.equals(actualQuery);
                LabStore.append(this, "GLOBAL_SEARCH_QUERY_RECEIPT exact=" + exactQuery
                        + " actualLen=" + actualQuery.length()
                        + " actual=" + LabStore.abbrev(actualQuery, 96));
                if (!exactQuery) {
                    failRun("GLOBAL_SEARCH_QUERY_TEXT_MISMATCH");
                    return;
                }
                LabStore.append(this, "GLOBAL_SEARCH_POST_QUERY_CONTROL_CENSUS windows="
                        + postQueryRoots.size() + " "
                        + LabStore.abbrev(controlCensus(postQueryRoots, 260), 20000));
                tryGlobalSearchBinding(expectedStep);
            }, 350L);
'''
if old not in svc:
    raise SystemExit('post-query census anchor not found')
svc = svc.replace(old, new, 1)
svc_path.write_text(svc)

gradle_path = root / 'app/build.gradle'
gradle = gradle_path.read_text()
gradle = gradle.replace('versionCode 13', 'versionCode 14', 1)
gradle = gradle.replace("versionName '0.13-native-capability-lab-stable-state-bound-search-field'",
                        "versionName '0.14-native-capability-lab-stable-indexed-marker-reopen'", 1)
if 'versionCode 14' not in gradle or '0.14-native-capability-lab-stable-indexed-marker-reopen' not in gradle:
    raise SystemExit('version patch failed')
gradle_path.write_text(gradle)

plan_path = root / 'plans/default.json'
plan = {
    'schema': 1,
    'suite': 'conversation_search_binding_v9_indexed_marker_reopen',
    'targetVersion': '1.2026.237',
    'targetSignerSha256': 'b24f4bfbb3cf293f938703b9d87027c1102cc36dc4fa206910e08927db40473c',
    'steps': [
        {'op': 'resume_chatgpt'},
        {'op': 'wait', 'ms': 500},
        {
            'op': 'global_search_binding',
            'marker': 'LAB_CID_9FC96C5A35E04E5B',
            'timeoutMs': 35000,
        },
        {'op': 'return_lab'},
        {'op': 'verify_candidates', 'timeoutMs': 10000},
        {'op': 'finish'},
    ],
}
plan_path.write_text(json.dumps(plan, indent=2) + '\n')

main_path = root / 'app/src/main/java/com/openai/controlplane/capabilitylab/MainActivity.java'
main = main_path.read_text()
old_intro = 'Stable v0.10 matches the real-device Menu semantic exactly (not by substring) and continues the official Search proof across every ChatGPT accessibility window and exact semantic/custom-action labels, while keeping the Conversation History -> Search chats fallback. It also adds a privacy-redacted control census so any remaining mismatch is directly calibratable. The Lab creates one synthetic marker chat, uses the already-proven bounded semantic Send, opens ChatGPT\'s own Search control, enters the marker into the official Search ChatGPT field, requires a unique marker-bearing conversation result, then opens that result and verifies the exact marker thread.'
new_intro = 'Stable v0.14 runs a read-only indexed-marker SearchBinding proof. It does not create a new chat in this run. Instead it searches a previously created synthetic marker that is already visibly indexed in ChatGPT Search, then opens the unique official result and verifies the exact marker thread. This isolates SearchBinding correctness from fresh-conversation indexing latency.'
if old_intro in main:
    main = main.replace(old_intro, new_intro, 1)
else:
    # Keep the patch robust if prior version text drifted; only replace the first desc sentence block.
    marker = 'desc.setText("'
    start = main.find(marker)
    if start < 0:
        raise SystemExit('MainActivity desc anchor not found')
    content_start = start + len(marker)
    para_end = main.find('\\n\\nNo private ChatGPT API', content_start)
    if para_end < 0:
        raise SystemExit('MainActivity desc paragraph end not found')
    main = main[:content_start] + new_intro + main[para_end:]
main_path.write_text(main)
