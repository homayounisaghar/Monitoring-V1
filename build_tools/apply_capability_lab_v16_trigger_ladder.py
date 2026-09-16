from pathlib import Path

ROOT = Path('runtime_probes/native-capability-lab')
SVC = ROOT / 'app/src/main/java/com/openai/controlplane/capabilitylab/LabAccessibilityService.java'


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if old not in text:
        raise SystemExit(f'anchor missing in {path}: {old[:120]!r}')
    path.write_text(text.replace(old, new, 1))


# Route the new bounded history-refresh state through the existing Accessibility service.
replace_once(
    SVC,
    '''        } else if ("WAITING_VERIFY_CANDIDATE".equals(state)) {
            tryVerifyCandidate(expectedStep);
        } else if (state.startsWith("WAITING_GLOBAL_SEARCH_")) {
            tryGlobalSearchBinding(expectedStep);
        }
''',
    '''        } else if ("WAITING_VERIFY_CANDIDATE".equals(state)) {
            tryVerifyCandidate(expectedStep);
        } else if (state.startsWith("WAITING_HISTORY_REFRESH")) {
            tryHistoryRefresh(expectedStep);
        } else if (state.startsWith("WAITING_GLOBAL_SEARCH_")) {
            tryGlobalSearchBinding(expectedStep);
        }
''')

# Add plan-level primitives so future trigger hypotheses can usually be plan-only changes.
replace_once(
    SVC,
    '''                case "global_search_binding":
                    opGlobalSearchBinding(step, i);
                    break;
                case "verify_candidates":
                    opVerifyCandidates(step, i);
                    break;
''',
    '''                case "global_search_binding":
                    opGlobalSearchBinding(step, i);
                    break;
                case "history_refresh":
                    opHistoryRefresh(step, i);
                    break;
                case "finish_if_search_binding":
                    if (LabStore.searchBindingVerified(this)) {
                        LabStore.append(this, "TRIGGER_LADDER_EARLY_FINISH searchBinding=true");
                        LabStore.finish(this, "PASS_VERIFIED_SEARCH_BINDING");
                        launchLabForeground();
                    } else {
                        completeStep(i);
                    }
                    break;
                case "verify_candidates":
                    opVerifyCandidates(step, i);
                    break;
''')

# Allow the final plan step to name a more specific inconclusive classification.
replace_once(
    SVC,
    '''                    } else {
                        finishWithoutVerifiedId("INCONCLUSIVE_NO_VERIFIED_BINDING");
                    }
                    launchLabForeground();
                    break;
''',
    '''                    } else {
                        finishWithoutVerifiedId(step.optString("inconclusiveStatus", "INCONCLUSIVE_NO_VERIFIED_BINDING"));
                    }
                    launchLabForeground();
                    break;
''')

# Upgrade Global Search into a reusable non-fatal probe mode. Normal binding behavior is unchanged.
old = '''    private void opGlobalSearchBinding(JSONObject step, int stepIndex) {
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
        LabStore.append(this, "GLOBAL_SEARCH_BINDING_ARMED marker=" + LabStore.marker(this)
                + " windows=" + roots.size());
        LabStore.append(this, "GLOBAL_SEARCH_ENTRY_CONTROL_CENSUS "
                + LabStore.abbrev(controlCensus(roots, 180), 14000));
        LabStore.append(this, "GLOBAL_SEARCH_MENU_EXACT_MATCHES=" + countExactSemanticAcrossRoots(roots, "Menu"));
        armTimeout(step.optLong("timeoutMs", 35000L), "GLOBAL_SEARCH_BINDING_TIMEOUT", stepIndex);
        handler.postDelayed(() -> tryGlobalSearchBinding(stepIndex), 300L);
    }
'''
new = '''    private void opGlobalSearchBinding(JSONObject step, int stepIndex) {
        if (!isCurrentStep(stepIndex)) return;
        boolean probe = step.optBoolean("probe", false);
        String probeLabel = searchProbeLabel(step, stepIndex);
        if (probe && LabStore.searchBindingVerified(this)) {
            LabStore.append(this, "GLOBAL_SEARCH_PROBE_SKIPPED label=" + probeLabel + " reason=already_verified");
            completeStep(stepIndex);
            return;
        }
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
        LabStore.append(this, "GLOBAL_SEARCH_BINDING_ARMED mode=" + (probe ? "probe" : "binding")
                + " label=" + (probe ? probeLabel : "<none>")
                + " marker=" + LabStore.marker(this)
                + " windows=" + roots.size());
        LabStore.append(this, "GLOBAL_SEARCH_ENTRY_CONTROL_CENSUS "
                + LabStore.abbrev(controlCensus(roots, 180), 14000));
        LabStore.append(this, "GLOBAL_SEARCH_MENU_EXACT_MATCHES=" + countExactSemanticAcrossRoots(roots, "Menu"));
        if (probe) {
            armTimeout(step.optLong("navigationTimeoutMs", 8000L),
                    "GLOBAL_SEARCH_PROBE_NAV_TIMEOUT label=" + probeLabel, stepIndex);
        } else {
            armTimeout(step.optLong("timeoutMs", 35000L), "GLOBAL_SEARCH_BINDING_TIMEOUT", stepIndex);
        }
        handler.postDelayed(() -> tryGlobalSearchBinding(stepIndex), 300L);
    }
'''
replace_once(SVC, old, new)

# Once the exact Search field accepts the query, a probe gets its own short result-evidence window.
replace_once(
    SVC,
    '''            if (!set) {
                failRun("GLOBAL_SEARCH_SET_TEXT_FALSE surface=" + surface);
                return;
            }
            handler.postDelayed(() -> {
''',
    '''            if (!set) {
                failRun("GLOBAL_SEARCH_SET_TEXT_FALSE surface=" + surface);
                return;
            }
            JSONObject currentStep = currentPlanStep(expectedStep);
            if (currentStep != null && currentStep.optBoolean("probe", false)) {
                armGlobalSearchProbeResultTimeout(currentStep, expectedStep,
                        searchProbeLabel(currentStep, expectedStep));
            }
            handler.postDelayed(() -> {
''')

# Record which trigger stage first produced a fully verified fresh SearchBinding.
replace_once(
    SVC,
    '''            LabStore.append(this, "GLOBAL_SEARCH_REOPEN_VERIFIED markerEditable=" + counts.editable
                    + " markerNonEditable=" + counts.nonEditable);
            LabStore.markSearchBindingVerified(this);
            completeStep(expectedStep);
''',
    '''            LabStore.append(this, "GLOBAL_SEARCH_REOPEN_VERIFIED markerEditable=" + counts.editable
                    + " markerNonEditable=" + counts.nonEditable);
            JSONObject verifiedStep = currentPlanStep(expectedStep);
            if (verifiedStep != null && verifiedStep.optBoolean("probe", false)) {
                LabStore.append(this, "SEARCH_INDEX_FIRST_VERIFIED_HIT label="
                        + searchProbeLabel(verifiedStep, expectedStep));
            }
            LabStore.markSearchBindingVerified(this);
            completeStep(expectedStep);
''')

# Insert reusable probe-timeout and explicit history-refresh helpers before candidate verification.
anchor = '    private void opVerifyCandidates(JSONObject step, int stepIndex) {'
text = SVC.read_text()
if anchor not in text:
    raise SystemExit('opVerifyCandidates anchor missing')
helpers = r'''    private JSONObject currentPlanStep(int expectedStep) {
        try {
            if (!isCurrentStep(expectedStep)) return null;
            return steps().getJSONObject(expectedStep);
        } catch (Throwable t) {
            return null;
        }
    }

    private String searchProbeLabel(JSONObject step, int stepIndex) {
        String label = step == null ? "" : step.optString("label", "").trim();
        if (!label.matches("[A-Za-z0-9_.-]{1,64}")) label = "probe_" + stepIndex;
        return label;
    }

    private void armGlobalSearchProbeResultTimeout(JSONObject step, int expectedStep, String label) {
        cancelTimeout();
        long ms = Math.max(600L, Math.min(step.optLong("resultWaitMs", 1800L), 15000L));
        timeoutStep = expectedStep;
        timeoutRunnable = () -> {
            timeoutRunnable = null;
            int armedStep = timeoutStep;
            timeoutStep = -1;
            if (armedStep != expectedStep || !isCurrentStep(expectedStep)) return;
            String state = LabStore.state(this);
            if (!"WAITING_GLOBAL_SEARCH_RESULT".equals(state)) {
                if ("WAITING_GLOBAL_SEARCH_REOPEN".equals(state)) {
                    failRun("GLOBAL_SEARCH_PROBE_REOPEN_TIMEOUT label=" + label);
                } else {
                    failRun("GLOBAL_SEARCH_PROBE_STATE_TIMEOUT label=" + label + " state=" + state);
                }
                return;
            }

            List<AccessibilityNodeInfo> roots = chatGptRoots();
            String census = controlCensus(roots, 280);
            String snapshot = roots.isEmpty() ? "<no ChatGPT roots>"
                    : normalizedTree(roots.get(0), LabStore.marker(this), 260, 11);
            LabStore.append(this, "GLOBAL_SEARCH_PROBE_MISS label=" + label
                    + " resultWaitMs=" + ms
                    + " windows=" + roots.size()
                    + " controlCensus=" + LabStore.abbrev(census, 22000)
                    + " activeSnapshot=" + LabStore.abbrev(snapshot, 12000));

            AccessibilityNodeInfo searchSurface = findRuntimeSearchSurfaceRoot(roots);
            if (searchSurface == null) searchSurface = findGlobalSearchRoot(roots);
            int closeCount = countExactSemanticAcrossRoots(roots, "Close");
            if (searchSurface == null || closeCount != 1) {
                failRun("GLOBAL_SEARCH_PROBE_MISS_SURFACE_INVALID label=" + label
                        + " closeCount=" + closeCount);
                return;
            }
            AccessibilityNodeInfo close = findUniqueExactSemanticAcrossRoots(roots, "Close");
            if (close == null || !performBoundedNavigation(close, "GLOBAL_SEARCH_PROBE_CLOSE", "Close")) {
                failRun("GLOBAL_SEARCH_PROBE_CLOSE_ACTION_FALSE label=" + label);
                return;
            }
            handler.postDelayed(() -> finishGlobalSearchProbeMiss(expectedStep, label), 320L);
        };
        handler.postDelayed(timeoutRunnable, ms);
    }

    private void finishGlobalSearchProbeMiss(int expectedStep, String label) {
        if (!isCurrentStep(expectedStep)) return;
        List<AccessibilityNodeInfo> roots = chatGptRoots();
        boolean searchStillOpen = findRuntimeSearchSurfaceRoot(roots) != null || anyGlobalSearchScreen(roots);
        boolean history = anyHistoryDrawerScreen(roots) || isRuntimeHistoryDrawer(roots);
        String postSurface = searchStillOpen ? "search" : (history ? "history_drawer" : "chat_or_other");
        String snapshot = roots.isEmpty() ? "<no ChatGPT roots>"
                : normalizedTree(roots.get(0), LabStore.marker(this), 220, 10);
        LabStore.append(this, "GLOBAL_SEARCH_PROBE_POST_CLOSE label=" + label
                + " surface=" + postSurface
                + " windows=" + roots.size()
                + " controlCensus=" + LabStore.abbrev(controlCensus(roots, 220), 18000)
                + " activeSnapshot=" + LabStore.abbrev(snapshot, 9000));
        if (searchStillOpen) {
            failRun("GLOBAL_SEARCH_PROBE_CLOSE_NOT_EFFECTIVE label=" + label);
            return;
        }
        LabStore.setState(this, "RUNNING");
        completeStep(expectedStep);
    }

    private void opHistoryRefresh(JSONObject step, int stepIndex) {
        if (!isCurrentStep(stepIndex)) return;
        if (LabStore.searchBindingVerified(this)) {
            LabStore.append(this, "HISTORY_REFRESH_SKIPPED reason=already_verified");
            completeStep(stepIndex);
            return;
        }
        LabStore.setState(this, "WAITING_HISTORY_REFRESH");
        LabStore.append(this, "HISTORY_REFRESH_ARMED label="
                + searchProbeLabel(step, stepIndex));
        armTimeout(step.optLong("timeoutMs", 6000L),
                "HISTORY_REFRESH_TIMEOUT label=" + searchProbeLabel(step, stepIndex), stepIndex);
        handler.postDelayed(() -> tryHistoryRefresh(stepIndex), 200L);
    }

    private void tryHistoryRefresh(int expectedStep) {
        if (!isCurrentStep(expectedStep)) return;
        String state = LabStore.state(this);
        if (!state.startsWith("WAITING_HISTORY_REFRESH")) return;
        List<AccessibilityNodeInfo> roots = chatGptRoots();
        if (roots.isEmpty()) return;

        if (anyHistoryDrawerScreen(roots) || isRuntimeHistoryDrawer(roots)) {
            String snapshot = normalizedTree(roots.get(0), LabStore.marker(this), 260, 11);
            LabStore.append(this, "HISTORY_REFRESH_READY windows=" + roots.size()
                    + " controlCensus=" + LabStore.abbrev(controlCensus(roots, 260), 22000)
                    + " activeSnapshot=" + LabStore.abbrev(snapshot, 12000));
            completeStep(expectedStep);
            return;
        }

        if ("WAITING_HISTORY_REFRESH_AFTER_OPEN".equals(state)) return;
        if ("WAITING_HISTORY_REFRESH_AFTER_CLOSE".equals(state)) {
            if (findRuntimeSearchSurfaceRoot(roots) != null || anyGlobalSearchScreen(roots)) return;
            LabStore.setState(this, "WAITING_HISTORY_REFRESH");
            handler.postDelayed(() -> tryHistoryRefresh(expectedStep), 100L);
            return;
        }

        AccessibilityNodeInfo searchSurface = findRuntimeSearchSurfaceRoot(roots);
        if (searchSurface != null || anyGlobalSearchScreen(roots)) {
            if (countExactSemanticAcrossRoots(roots, "Close") != 1) {
                failRun("HISTORY_REFRESH_SEARCH_CLOSE_NOT_UNIQUE");
                return;
            }
            AccessibilityNodeInfo close = findUniqueExactSemanticAcrossRoots(roots, "Close");
            LabStore.setState(this, "WAITING_HISTORY_REFRESH_AFTER_CLOSE");
            if (close == null || !performBoundedNavigation(close, "HISTORY_REFRESH_CLOSE_SEARCH", "Close")) {
                failRun("HISTORY_REFRESH_CLOSE_SEARCH_ACTION_FALSE");
                return;
            }
            handler.postDelayed(() -> tryHistoryRefresh(expectedStep), 300L);
            return;
        }

        AccessibilityNodeInfo historyEntry = findUniqueHistoryEntryAcrossRoots(roots);
        if (historyEntry == null) return;
        LabStore.setState(this, "WAITING_HISTORY_REFRESH_AFTER_OPEN");
        if (!performBoundedNavigation(historyEntry, "HISTORY_REFRESH_OPEN",
                "Open conversation history", "Open sidebar", "Open navigation",
                "Open navigation menu", "Navigation menu", "Menu")) {
            failRun("HISTORY_REFRESH_OPEN_ACTION_FALSE");
            return;
        }
        handler.postDelayed(() -> tryHistoryRefresh(expectedStep), 300L);
    }

    private boolean isRuntimeHistoryDrawer(List<AccessibilityNodeInfo> roots) {
        if (roots == null || roots.isEmpty()) return false;
        if (findRuntimeSearchSurfaceRoot(roots) != null || anyGlobalSearchScreen(roots)) return false;
        return countExactSemanticAcrossRoots(roots, "Search") == 1
                && countExactSemanticAcrossRoots(roots, "Close") == 1
                && countExactSemanticAcrossRoots(roots, "New chat") >= 1;
    }

'''
SVC.write_text(text.replace(anchor, helpers + anchor, 1))

# Static invariants: no coordinate/gesture/global-action path was introduced and the
# existing direct ACTION_CLICK/ACTION_SET_TEXT code-site counts remain unchanged.
s = SVC.read_text()
assert s.count('performAction(AccessibilityNodeInfo.ACTION_CLICK)') == 2
assert s.count('performAction(AccessibilityNodeInfo.ACTION_SET_TEXT') == 1
assert 'dispatchGesture' not in s
assert 'getBoundsInScreen' not in s
assert 'GLOBAL_ACTION_' not in s
assert 'GLOBAL_SEARCH_PROBE_MISS' in s
assert 'HISTORY_REFRESH_READY' in s
assert 'finish_if_search_binding' in s
