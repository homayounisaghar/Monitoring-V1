from pathlib import Path

svc = Path('runtime_probes/native-capability-lab/app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java')
text = svc.read_text()
old = '''            AccessibilityNodeInfo close = findUniqueExactSemanticAcrossRoots(roots, "Close");
            if (close == null || !performBoundedNavigation(close, "GLOBAL_SEARCH_PROBE_CLOSE", "Close")) {
                failRun("GLOBAL_SEARCH_PROBE_CLOSE_ACTION_FALSE label=" + label);
                return;
            }
            handler.postDelayed(() -> finishGlobalSearchProbeMiss(expectedStep, label), 320L);
'''
new = '''            AccessibilityNodeInfo close = findUniqueExactSemanticAcrossRoots(roots, "Close");
            // Freeze result evaluation before closing Search. Otherwise the accessibility
            // event caused by Close could re-enter WAITING_GLOBAL_SEARCH_RESULT and count a
            // marker that appears only after the close/history transition as a hit for the
            // earlier probe stage, corrupting trigger attribution.
            LabStore.setState(this, "WAITING_GLOBAL_SEARCH_PROBE_CLOSE");
            if (close == null || !performBoundedNavigation(close, "GLOBAL_SEARCH_PROBE_CLOSE", "Close")) {
                failRun("GLOBAL_SEARCH_PROBE_CLOSE_ACTION_FALSE label=" + label);
                return;
            }
            handler.postDelayed(() -> finishGlobalSearchProbeMiss(expectedStep, label), 320L);
'''
if old not in text:
    raise SystemExit('probe-close anchor missing')
text = text.replace(old, new, 1)
svc.write_text(text)

s = svc.read_text()
assert 'WAITING_GLOBAL_SEARCH_PROBE_CLOSE' in s
assert s.count('performAction(AccessibilityNodeInfo.ACTION_CLICK)') == 2
assert s.count('performAction(AccessibilityNodeInfo.ACTION_SET_TEXT') == 1
assert 'dispatchGesture' not in s
assert 'getBoundsInScreen' not in s
assert 'GLOBAL_ACTION_' not in s
