from pathlib import Path

svc = Path('runtime_probes/native-capability-lab/app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java')
text = svc.read_text()
old = '''            if (anyGlobalSearchScreen(roots) || findRuntimeSearchRoot(roots) != null) {
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 120L);
                return;
            }

            AccessibilityNodeInfo entry = findUniqueGlobalSearchEntryAcrossRoots(roots);
'''
new = '''            if (anyGlobalSearchScreen(roots) || findRuntimeSearchRoot(roots) != null) {
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 120L);
                return;
            }
            // Trigger-ladder probes may deliberately begin while the official History
            // drawer is already open. Re-enter the existing post-Menu drawer state rather
            // than requiring a second Menu opener that is no longer present on that UI.
            if (anyHistoryDrawerScreen(roots) || isRuntimeHistoryDrawer(roots)) {
                LabStore.append(this, "GLOBAL_SEARCH_ENTRY already_history_drawer=true");
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_DRAWER");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 100L);
                return;
            }

            AccessibilityNodeInfo entry = findUniqueGlobalSearchEntryAcrossRoots(roots);
'''
if old not in text:
    raise SystemExit('history-resume anchor missing')
text = text.replace(old, new, 1)
svc.write_text(text)

s = svc.read_text()
assert 'GLOBAL_SEARCH_ENTRY already_history_drawer=true' in s
assert s.count('performAction(AccessibilityNodeInfo.ACTION_CLICK)') == 2
assert s.count('performAction(AccessibilityNodeInfo.ACTION_SET_TEXT') == 1
assert 'dispatchGesture' not in s
assert 'getBoundsInScreen' not in s
assert 'GLOBAL_ACTION_' not in s
