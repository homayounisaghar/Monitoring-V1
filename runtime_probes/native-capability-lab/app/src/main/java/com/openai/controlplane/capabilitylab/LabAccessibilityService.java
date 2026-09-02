package com.openai.controlplane.capabilitylab;

import android.accessibilityservice.AccessibilityService;
import android.content.ClipData;
import android.content.ComponentName;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.view.accessibility.AccessibilityWindowInfo;

import androidx.core.content.FileProvider;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class LabAccessibilityService extends AccessibilityService {
    private static volatile LabAccessibilityService INSTANCE;
    private static final Pattern UUID_PATTERN = Pattern.compile("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$");
    private static final Pattern HEX32_PATTERN = Pattern.compile("^[0-9a-fA-F]{32}$");
    private static final Pattern UUID_FIND = Pattern.compile("(?i)(?<![0-9a-f])[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?![0-9a-f])");
    private static final Pattern HEX32_FIND = Pattern.compile("(?i)(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])");
    private static final int MAX_VERIFY_CANDIDATES = 8;
    private static final int MAX_METADATA_NODES = 1400;
    private static final String HISTORY_ITEM_PREFIX = "chatgpt.history.item.";
    private static final String HISTORY_ACTIONS_PREFIX = "chatgpt.history.actions.";

    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Runnable runCurrentStepRunnable = new Runnable() {
        @Override public void run() { executeCurrentStep(); }
    };
    private Runnable timeoutRunnable;
    private int timeoutStep = -1;
    private String verifyingCandidate = "";
    private String neutralMarker = "";

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        INSTANCE = this;
        LabStore.markAccessibilityConnected(this, true);
        LabStore.append(this, "ACCESSIBILITY_CONNECTED");
        if ("RUNNING".equals(LabStore.status(this)) && "RUNNING".equals(LabStore.state(this))) {
            scheduleCurrentStep(250L);
        }
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (!ProfileGuard.CHATGPT_PACKAGE.equals(String.valueOf(event == null ? null : event.getPackageName()))) return;
        if (!"RUNNING".equals(LabStore.status(this))) return;
        int expectedStep = LabStore.step(this);
        String state = LabStore.state(this);
        if ("WAITING_SEMANTIC_SEND".equals(state) || "SEND_CLAIMED".equals(state)) {
            trySemanticSendOrReceipt(expectedStep);
        } else if ("WAITING_TREE_CAPTURE".equals(state)) {
            tryCaptureTreeAndAdvance(expectedStep);
        } else if ("WAITING_VERIFY_NEUTRAL".equals(state)) {
            tryVerifyNeutralThenCandidate(expectedStep);
        } else if ("WAITING_VERIFY_CANDIDATE".equals(state)) {
            tryVerifyCandidate(expectedStep);
        } else if (state.startsWith("WAITING_HISTORY_BOUNDARY_CALIBRATION_")) {
            tryHistoryBoundaryCalibration(expectedStep);
        } else if (state.startsWith("WAITING_HISTORY_RECENT_")) {
            tryHistoryRecentBinding(expectedStep);
        } else if (state.startsWith("WAITING_HISTORY_REFRESH")) {
            tryHistoryRefresh(expectedStep);
        } else if (state.startsWith("WAITING_GLOBAL_SEARCH_")) {
            tryGlobalSearchBinding(expectedStep);
        }
    }

    @Override
    public void onInterrupt() {
        LabStore.append(this, "ACCESSIBILITY_INTERRUPTED");
    }

    @Override
    public void onDestroy() {
        if (INSTANCE == this) INSTANCE = null;
        LabStore.markAccessibilityConnected(this, false);
        cancelTimeout();
        handler.removeCallbacks(runCurrentStepRunnable);
        super.onDestroy();
    }

    static boolean isLive() { return INSTANCE != null; }

    static void startCurrentPlan() {
        LabAccessibilityService s = INSTANCE;
        if (s == null) throw new IllegalStateException("Accessibility service is not connected");
        s.scheduleCurrentStep(0L);
    }

    private JSONObject planRoot() throws Exception {
        return new JSONObject(LabStore.planJson(this));
    }

    private JSONArray steps() throws Exception {
        JSONArray a = planRoot().getJSONArray("steps");
        if (a.length() > 100) throw new IllegalStateException("too many plan steps");
        return a;
    }

    private void scheduleCurrentStep(long delayMs) {
        handler.removeCallbacks(runCurrentStepRunnable);
        handler.postDelayed(runCurrentStepRunnable, Math.max(0L, delayMs));
    }

    private boolean isCurrentStep(int expectedStep) {
        return "RUNNING".equals(LabStore.status(this)) && LabStore.step(this) == expectedStep;
    }

    private void executeCurrentStep() {
        if (!"RUNNING".equals(LabStore.status(this))) return;
        if (!"RUNNING".equals(LabStore.state(this))) return;
        try {
            ProfileGuard.assertExact(this);
            JSONArray steps = steps();
            int i = LabStore.step(this);
            if (i >= steps.length()) {
                finishWithoutVerifiedId("INCONCLUSIVE_PLAN_EXHAUSTED");
                return;
            }
            JSONObject step = steps.getJSONObject(i);
            String op = step.getString("op");
            LabStore.append(this, "STEP index=" + i + " op=" + op);

            switch (op) {
                case "launch_prompt":
                    opLaunchPrompt(step);
                    completeStep(i);
                    break;
                case "semantic_send":
                    opSemanticSend(step, i);
                    break;
                case "return_lab":
                    launchLabForeground();
                    completeStep(i);
                    break;
                case "wait":
                    opWait(step, i);
                    break;
                case "notification_snapshot":
                    LabNotificationService.snapshotFromRunner("plan_step_" + i);
                    completeStep(i);
                    break;
                case "channel_snapshot":
                    LabNotificationService.tryChannelSnapshotFromRunner();
                    completeStep(i);
                    break;
                case "resume_chatgpt":
                    resumeChatGpt();
                    completeStep(i);
                    break;
                case "capture_tree":
                    opCaptureTree(step, i);
                    break;
                case "global_search_binding":
                    opGlobalSearchBinding(step, i);
                    break;
                case "history_boundary_calibration":
                    opHistoryBoundaryCalibration(step, i);
                    break;
                case "reset_after_calibration":
                    LabStore.resetAfterCalibration(this);
                    completeStep(i);
                    break;
                case "history_recent_binding":
                    opHistoryRecentBinding(step, i);
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
                case "share_files":
                    opShareFiles(step);
                    completeStep(i);
                    break;
                case "open_voice":
                    openVoice();
                    completeStep(i);
                    break;
                case "process_text":
                    processText();
                    completeStep(i);
                    break;
                case "finish":
                    if (!LabStore.verifiedConversationId(this).isEmpty()) {
                        LabStore.finish(this, "PASS_VERIFIED_CONVERSATION_ID");
                    } else if (LabStore.historyBindingVerified(this)) {
                        LabStore.finish(this, "PASS_VERIFIED_HISTORY_RECENT_BINDING");
                    } else if (LabStore.searchBindingVerified(this)) {
                        LabStore.finish(this, "PASS_VERIFIED_SEARCH_BINDING");
                    } else {
                        finishWithoutVerifiedId(step.optString("inconclusiveStatus", "INCONCLUSIVE_NO_VERIFIED_BINDING"));
                    }
                    launchLabForeground();
                    break;
                default:
                    failRun("UNSUPPORTED_PLAN_OP:" + op);
            }
        } catch (Throwable t) {
            failRun("STEP_ERROR " + t.getClass().getSimpleName() + ":" + LabStore.abbrev(String.valueOf(t.getMessage()), 300));
        }
    }

    private void opLaunchPrompt(JSONObject step) throws Exception {
        String marker = LabStore.marker(this);
        if (marker.isEmpty()) {
            marker = "LAB_CID_" + UUID.randomUUID().toString().replace("-", "").substring(0, 16).toUpperCase(Locale.US);
            LabStore.setMarker(this, marker);
        }
        String prompt = step.optString("prompt", "Capability Lab proof {{marker}}").replace("{{marker}}", marker);
        Uri uri = Uri.parse("https://chatgpt.com/c").buildUpon().appendQueryParameter("prompt", prompt).build();
        Intent i = new Intent(Intent.ACTION_VIEW, uri);
        i.setComponent(new ComponentName(ProfileGuard.CHATGPT_PACKAGE, ProfileGuard.CHATGPT_DEEPLINK));
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        LabStore.append(this, "LAUNCH_PROMPT marker=" + marker + " uriPath=/c promptLen=" + prompt.length());
        startActivity(i);
    }

    private void opSemanticSend(JSONObject step, int stepIndex) {
        if (!isCurrentStep(stepIndex)) return;
        LabStore.setState(this, "WAITING_SEMANTIC_SEND");
        armTimeout(step.optLong("timeoutMs", 15000L), "SEMANTIC_SEND_TIMEOUT", stepIndex);
        handler.postDelayed(() -> trySemanticSendOrReceipt(stepIndex), 250L);
    }

    private void trySemanticSendOrReceipt(int expectedStep) {
        if (!isCurrentStep(expectedStep)) return;
        String state = LabStore.state(this);
        if (!("WAITING_SEMANTIC_SEND".equals(state) || "SEND_CLAIMED".equals(state))) return;
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null || !isChatGptRoot(root)) return;
        String marker = LabStore.marker(this);
        if (marker.isEmpty()) return;

        MarkerCounts counts = countMarkerNodes(root, marker);
        if (LabStore.writeClaimed(this)) {
            if (counts.editable == 0 && counts.nonEditable >= 1) {
                LabStore.markSendConfirmed(this);
                completeStep(expectedStep);
            }
            return;
        }

        if (counts.editable != 1) return;
        AccessibilityNodeInfo editable = findUniqueEditableMarker(root, marker);
        if (editable == null) return;
        AccessibilityNodeInfo scope1 = editable.getParent();
        AccessibilityNodeInfo scope2 = scope1 == null ? null : scope1.getParent();
        if (scope2 == null) {
            failRun("SEMANTIC_SEND_CONTRACT_NO_UP2_SCOPE");
            return;
        }

        List<AccessibilityNodeInfo> sends = new ArrayList<>();
        collectSendLeaves(scope2, sends, 0);
        if (sends.size() != 1) return;
        AccessibilityNodeInfo leaf = sends.get(0);
        AccessibilityNodeInfo directParent = leaf.getParent();
        if (directParent == null || !directParent.isVisibleToUser() || !directParent.isEnabled()
                || !directParent.isClickable() || !hasAction(directParent, AccessibilityNodeInfo.ACTION_CLICK)) {
            failRun("SEMANTIC_SEND_CONTRACT_PARENT_INVALID");
            return;
        }

        if (!LabStore.claimWrite(this)) return;
        LabStore.setState(this, "SEND_CLAIMED");
        boolean clicked = directParent.performAction(AccessibilityNodeInfo.ACTION_CLICK);
        LabStore.append(this, "SEMANTIC_SEND ACTION_CLICK returned=" + clicked + " target=directParentOfUniqueSendMessage");
        if (!clicked) {
            failUncertain("SEMANTIC_SEND_CLAIMED_BUT_CLICK_FALSE");
            return;
        }
        handler.postDelayed(() -> trySemanticSendOrReceipt(expectedStep), 180L);
    }

    private void opWait(JSONObject step, int stepIndex) {
        if (!isCurrentStep(stepIndex)) return;
        long ms = Math.max(0L, Math.min(step.optLong("ms", 1000L), 180_000L));
        LabStore.setState(this, "WAITING_TIMER");
        LabStore.setWaitUntil(this, System.currentTimeMillis() + ms);
        cancelTimeout();
        handler.postDelayed(() -> {
            if (!isCurrentStep(stepIndex)) return;
            if (!"WAITING_TIMER".equals(LabStore.state(this))) return;
            LabStore.append(this, "WAIT_COMPLETE ms=" + ms);
            completeStep(stepIndex);
        }, ms);
    }

    private void opCaptureTree(JSONObject step, int stepIndex) {
        if (!isCurrentStep(stepIndex)) return;
        LabStore.setState(this, "WAITING_TREE_CAPTURE");
        String label = step.optString("label", "tree");
        LabStore.append(this, "TREE_CAPTURE_ARMED label=" + label);
        armTimeout(step.optLong("timeoutMs", 8000L), "TREE_CAPTURE_TIMEOUT label=" + label, stepIndex);
        handler.postDelayed(() -> tryCaptureTreeAndAdvance(stepIndex), 250L);
    }

    private void tryCaptureTreeAndAdvance(int expectedStep) {
        if (!isCurrentStep(expectedStep)) return;
        if (!"WAITING_TREE_CAPTURE".equals(LabStore.state(this))) return;
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null || !isChatGptRoot(root)) return;
        String marker = LabStore.marker(this);
        MarkerCounts counts = countMarkerNodes(root, marker);
        MetadataStats metadata = harvestAccessibilityMetadata(root);
        String snapshot = normalizedTree(root, marker, 650, 14);
        LabStore.append(this, "ACCESSIBILITY_METADATA nodes=" + metadata.nodes
                + " extras=" + metadata.extras
                + " candidateMatches=" + metadata.candidateMatches);
        LabStore.append(this, "TREE_CAPTURE markerEditable=" + counts.editable + " markerNonEditable=" + counts.nonEditable + " snapshot=" + LabStore.abbrev(snapshot, 28000));
        completeStep(expectedStep);
    }

    private void opGlobalSearchBinding(JSONObject step, int stepIndex) {
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

    private void tryGlobalSearchBinding(int expectedStep) {
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
            // An indexed-marker probe may resume ChatGPT while the first-party Search
            // surface is already open from a previous run. Accept the same strict runtime
            // Search root contract here instead of forcing a redundant Menu -> Search cycle.
            if (anyGlobalSearchScreen(roots) || findRuntimeSearchRoot(roots) != null) {
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
                    "Open conversation history", "Open sidebar", "Open navigation", "Open navigation menu", "Navigation menu", "Menu")) {
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

            // v0.8 runtime exposed the real conversation opener as a visible semantic child
            // labelled exactly "Menu" with ACTION_CLICK on its parent. Once that official
            // menu is opened, do not require the drawer root itself to expose the static
            // `chatgpt.history.drawer` identifier: look directly for first-party Search
            // controls/fields across the ChatGPT windows.
            AccessibilityNodeInfo directSearch = findUniqueGlobalSearchEntryAcrossRoots(roots);
            if (directSearch != null) {
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                if (!performBoundedNavigation(directSearch, "GLOBAL_SEARCH_DRAWER_DIRECT_SEARCH",
                        "Search chats, files, and projects", "Search ChatGPT")) {
                    failRun("GLOBAL_SEARCH_DRAWER_DIRECT_SEARCH_ACTION_FALSE");
                    return;
                }
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 300L);
                return;
            }

            AccessibilityNodeInfo alreadyVisibleField = findHistorySearchFieldAcrossRoots(roots);
            if (alreadyVisibleField != null) {
                LabStore.append(this, "GLOBAL_SEARCH_HISTORY_FIELD already_visible=true source=across_roots");
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                handler.postDelayed(() -> tryGlobalSearchBinding(expectedStep), 80L);
                return;
            }

            // v0.10 crossed the Menu gate and exposed the real first-party drawer control
            // as a child whose COMPLETE semantic is exactly "Search", with ACTION_CLICK on
            // its parent. Accept that control only in this post-Menu state and only when it
            // is unique across ChatGPT roots. Do not broaden this into a generic Search alias.
            int exactDrawerSearchCount = countExactSemanticAcrossRoots(roots, "Search");
            if (exactDrawerSearchCount > 0) {
                LabStore.append(this, "GLOBAL_SEARCH_DRAWER_SEARCH_EXACT_MATCHES=" + exactDrawerSearchCount);
            }
            if (exactDrawerSearchCount > 1) {
                failRun("GLOBAL_SEARCH_DRAWER_SEARCH_NOT_UNIQUE count=" + exactDrawerSearchCount);
                return;
            }
            if (exactDrawerSearchCount == 1) {
                AccessibilityNodeInfo exactDrawerSearch = findUniqueExactSemanticAcrossRoots(roots, "Search");
                if (exactDrawerSearch == null) {
                    failRun("GLOBAL_SEARCH_DRAWER_SEARCH_UNIQUE_RESOLUTION_FAILED");
                    return;
                }
                LabStore.setState(this, "WAITING_GLOBAL_SEARCH_FIELD");
                if (!performBoundedNavigation(exactDrawerSearch, "GLOBAL_SEARCH_DRAWER_EXACT_SEARCH", "Search")) {
                    failRun("GLOBAL_SEARCH_DRAWER_EXACT_SEARCH_ACTION_FALSE");
                    return;
                }
                handler.postDelayed(() -> {
                    if (!isCurrentStep(expectedStep)) return;
                    if (!"WAITING_GLOBAL_SEARCH_FIELD".equals(LabStore.state(this))) return;
                    List<AccessibilityNodeInfo> postSearchRoots = chatGptRoots();
                    LabStore.append(this, "GLOBAL_SEARCH_POST_SEARCH_CLICK_CONTROL_CENSUS windows="
                            + postSearchRoots.size() + " "
                            + LabStore.abbrev(controlCensus(postSearchRoots, 220), 18000));
                    tryGlobalSearchBinding(expectedStep);
                }, 300L);
                return;
            }

            AccessibilityNodeInfo historySearch = findUniqueHistorySearchEntryAcrossRoots(roots);
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
            if (globalRoot == null) {
                // v0.12 runtime contract, usable only after the already-proven Menu + Search
                // navigation has placed the runner in WAITING_GLOBAL_SEARCH_FIELD.
                globalRoot = findRuntimeSearchRoot(roots);
                if (globalRoot != null) {
                    LabStore.append(this, "GLOBAL_SEARCH_RUNTIME_FIELD_CONTRACT matched=true");
                }
            }
            if (globalRoot != null) {
                field = findGlobalSearchField(globalRoot);
                surface = "global";
            }
            if (field == null) {
                field = findHistorySearchFieldAcrossRoots(roots);
                if (field != null) surface = "history";
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
            JSONObject currentStep = currentPlanStep(expectedStep);
            if (currentStep != null && currentStep.optBoolean("probe", false)) {
                armGlobalSearchProbeResultTimeout(currentStep, expectedStep,
                        searchProbeLabel(currentStep, expectedStep));
            }
            handler.postDelayed(() -> {
                if (!isCurrentStep(expectedStep)) return;
                if (!"WAITING_GLOBAL_SEARCH_RESULT".equals(LabStore.state(this))) return;
                List<AccessibilityNodeInfo> postQueryRoots = chatGptRoots();
                AccessibilityNodeInfo receiptRoot = findGlobalSearchRoot(postQueryRoots);
                if (receiptRoot == null) receiptRoot = findRuntimeSearchRoot(postQueryRoots);
                AccessibilityNodeInfo receiptField = receiptRoot == null ? null : findGlobalSearchField(receiptRoot);
                String actualQuery = receiptField == null || receiptField.getText() == null
                        ? "" : receiptField.getText().toString();
                boolean exactQuery = marker.equals(actualQuery);
                boolean queryTextUnavailable = actualQuery.isEmpty();
                LabStore.append(this, "GLOBAL_SEARCH_QUERY_RECEIPT exact=" + exactQuery
                        + " unavailable=" + queryTextUnavailable
                        + " actualLen=" + actualQuery.length()
                        + " actual=" + LabStore.abbrev(actualQuery, 96));
                // Runtime v0.14 showed ACTION_SET_TEXT=true while the re-rendered Search
                // EditText returned an empty getText() through Accessibility. Empty readback
                // is therefore treated as unavailable evidence, not contradictory evidence.
                // A non-empty mismatch still fails closed. Exactness is then established by
                // the unique marker-bearing result and exact marker receipt after reopen.
                if (!exactQuery && !queryTextUnavailable) {
                    failRun("GLOBAL_SEARCH_QUERY_TEXT_MISMATCH");
                    return;
                }
                if (queryTextUnavailable) {
                    LabStore.append(this, "GLOBAL_SEARCH_QUERY_RECEIPT_DEFERRED_TO_RESULT_EVIDENCE");
                }
                LabStore.append(this, "GLOBAL_SEARCH_POST_QUERY_CONTROL_CENSUS windows="
                        + postQueryRoots.size() + " "
                        + LabStore.abbrev(controlCensus(postQueryRoots, 260), 20000));
                tryGlobalSearchBinding(expectedStep);
            }, 350L);
            return;
        }

        if ("WAITING_GLOBAL_SEARCH_RESULT".equals(state)) {
            AccessibilityNodeInfo surfaceRoot = findGlobalSearchRoot(roots);
            boolean globalSurface = surfaceRoot != null;
            if (surfaceRoot == null) {
                surfaceRoot = findRuntimeSearchRoot(roots);
                if (surfaceRoot != null) globalSurface = true;
            }
            if (surfaceRoot == null) {
                // After a query the literal Search label may disappear while the same
                // first-party surface keeps the unique editable field + Close control.
                surfaceRoot = findRuntimeSearchSurfaceRoot(roots);
                if (surfaceRoot != null) globalSurface = true;
            }
            if (surfaceRoot == null) surfaceRoot = findRootWithHistorySearchFieldEquals(roots, marker);
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
            // Do not mistake the marker text inside Search results for a reopened chat.
            // Require every known Search-surface sentinel to disappear first.
            if (anyGlobalSearchScreen(roots) || anyHistoryDrawerScreen(roots)
                    || findRuntimeSearchSurfaceRoot(roots) != null) return;
            MarkerCounts counts = countMarkerNodesAcrossRoots(roots, marker);
            if (counts.editable != 0 || counts.nonEditable < 1) return;
            LabStore.append(this, "GLOBAL_SEARCH_REOPEN_VERIFIED markerEditable=" + counts.editable
                    + " markerNonEditable=" + counts.nonEditable);
            JSONObject verifiedStep = currentPlanStep(expectedStep);
            if (verifiedStep != null && verifiedStep.optBoolean("probe", false)) {
                LabStore.append(this, "SEARCH_INDEX_FIRST_VERIFIED_HIT label="
                        + searchProbeLabel(verifiedStep, expectedStep));
            }
            LabStore.markSearchBindingVerified(this);
            completeStep(expectedStep);
        }
    }

    private JSONObject currentPlanStep(int expectedStep) {
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

    private void opHistoryBoundaryCalibration(JSONObject step, int stepIndex) {
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

    private void opHistoryRecentBinding(JSONObject step, int stepIndex) {
        if (!isCurrentStep(stepIndex)) return;
        LabStore.clearCandidates(this);
        LabStore.setFreshBoundaryItemId(this, "");
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
        List<AccessibilityNodeInfo> semanticLeaves = new ArrayList<>();
        List<AccessibilityNodeInfo> actionableTargets = new ArrayList<>();
        for (AccessibilityNodeInfo root : roots) {
            List<AccessibilityNodeInfo> one = new ArrayList<>();
            collectExactSemanticNodes(root, "New chat", one, 0);
            for (AccessibilityNodeInfo leaf : one) {
                addUniqueNode(semanticLeaves, leaf);
                AccessibilityNodeInfo target = firstActionClickAncestor(leaf, 8);
                if (target != null) addUniqueNode(actionableTargets, target);
            }
        }
        LabStore.append(this, "HISTORY_RECENT_NEW_CHAT_RESOLUTION semanticLeaves=" + semanticLeaves.size()
                + " actionableTargets=" + actionableTargets.size());
        if (actionableTargets.size() != 1) {
            failRun("HISTORY_RECENT_NEW_CHAT_ACTIONABLE_NOT_UNIQUE count=" + actionableTargets.size());
            return;
        }
        AccessibilityNodeInfo newChat = actionableTargets.get(0);
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

        observeFreshBoundaryCandidate("settled_after_switch_away", roots);
        String boundaryId = LabStore.freshBoundaryItemId(this);
        AccessibilityNodeInfo row = rowForHistoryBoundaryId(rows, boundaryId);
        if (boundaryId.isEmpty() || row == null) {
            cancelTimeout();
            LabStore.append(this, "HISTORY_RECENT_NO_UNIQUE_APK_DERIVED_ROW boundaryId="
                    + LabStore.abbrev(boundaryId, 220)
                    + " action=observation_only_no_unrelated_row_click");
            completeStep(expectedStep);
            return;
        }
        String title = historyRowTitle(row);
        LabStore.clearCandidates(this);
        LabStore.setHistoryCandidateTitle(this, title);
        MetadataStats stats = harvestAccessibilityMetadata(row);
        String rowTree = normalizedTree(row, LabStore.marker(this), 180, 7);
        LabStore.append(this, "HISTORY_RECENT_SELECTED_ROW source=unique_new_history_accessibility_id"
                + " boundaryId=" + LabStore.abbrev(boundaryId, 260)
                + " suffix=" + LabStore.abbrev(historyBoundarySuffix(boundaryId, HISTORY_ITEM_PREFIX), 180)
                + " title=" + LabStore.abbrev(title, 180)
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
        recordHistoryBoundaryEvidence("fresh_" + phase, roots);
        observeFreshBoundaryCandidate(phase, roots);
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
            // Runtime evidence distinguishes History conversation rows by their
            // ACTION_CLICK + ACTION_LONG_CLICK contract. A freshly finalized
            // conversation may not have a generated title yet, so title text is
            // evidence only, not a prerequisite for row recognition.
            out.add(node);
            return;
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
                    && !"Search".equals(value) && !"Close".equals(value)) return value;
        }
        for (int i = 0; i < node.getChildCount(); i++) {
            String value = historyRowTitle(node.getChild(i), depth + 1);
            if (!value.isEmpty()) return value;
        }
        return "";
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

    private void opVerifyCandidates(JSONObject step, int stepIndex) {
        if (!isCurrentStep(stepIndex)) return;
        List<String> plausible = plausibleCandidates();
        LabStore.append(this, "VERIFY_CANDIDATES plausibleCount=" + plausible.size() + " rawCount=" + LabStore.candidates(this).size());
        if (plausible.isEmpty()) {
            completeStep(stepIndex);
            return;
        }
        int index = LabStore.candidateIndex(this);
        if (index >= plausible.size() || index >= MAX_VERIFY_CANDIDATES) {
            completeStep(stepIndex);
            return;
        }
        verifyingCandidate = plausible.get(index);
        neutralMarker = "LAB_NEUTRAL_" + UUID.randomUUID().toString().replace("-", "").substring(0, 12).toUpperCase(Locale.US);
        Uri uri = Uri.parse("https://chatgpt.com/c").buildUpon().appendQueryParameter("prompt", neutralMarker).build();
        Intent neutral = new Intent(Intent.ACTION_VIEW, uri);
        neutral.setComponent(new ComponentName(ProfileGuard.CHATGPT_PACKAGE, ProfileGuard.CHATGPT_DEEPLINK));
        neutral.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        LabStore.setState(this, "WAITING_VERIFY_NEUTRAL");
        LabStore.append(this, "VERIFY_NEUTRAL launch candidateIndex=" + index + " candidate=" + verifyingCandidate + " neutralMarker=" + neutralMarker);
        startActivity(neutral);
        armTimeout(step.optLong("timeoutMs", 8000L), "VERIFY_NEUTRAL_TIMEOUT", stepIndex);
        handler.postDelayed(() -> tryVerifyNeutralThenCandidate(stepIndex), 250L);
    }

    private void tryVerifyNeutralThenCandidate(int expectedStep) {
        if (!isCurrentStep(expectedStep)) return;
        if (!"WAITING_VERIFY_NEUTRAL".equals(LabStore.state(this))) return;
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null || !isChatGptRoot(root)) return;
        if (findUniqueEditableMarker(root, neutralMarker) == null) return;
        MarkerCounts old = countMarkerNodes(root, LabStore.marker(this));
        if (old.editable > 0 || old.nonEditable > 0) return;

        cancelTimeout();
        Uri uri = Uri.parse("https://chatgpt.com/c/" + verifyingCandidate);
        Intent candidate = new Intent(Intent.ACTION_VIEW, uri);
        candidate.setComponent(new ComponentName(ProfileGuard.CHATGPT_PACKAGE, ProfileGuard.CHATGPT_DEEPLINK));
        candidate.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        LabStore.setState(this, "WAITING_VERIFY_CANDIDATE");
        LabStore.append(this, "VERIFY_CANDIDATE launch /c/<candidate> candidate=" + verifyingCandidate);
        startActivity(candidate);
        armTimeout(currentVerifyTimeout(), "VERIFY_CANDIDATE_TIMEOUT candidate=" + verifyingCandidate, expectedStep);
        handler.postDelayed(() -> tryVerifyCandidate(expectedStep), 250L);
    }

    private long currentVerifyTimeout() {
        try {
            JSONObject step = steps().getJSONObject(LabStore.step(this));
            return Math.max(2000L, Math.min(step.optLong("timeoutMs", 8000L), 30000L));
        } catch (Throwable t) {
            return 8000L;
        }
    }

    private void tryVerifyCandidate(int expectedStep) {
        if (!isCurrentStep(expectedStep)) return;
        if (!"WAITING_VERIFY_CANDIDATE".equals(LabStore.state(this))) return;
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null || !isChatGptRoot(root)) return;
        MarkerCounts counts = countMarkerNodes(root, LabStore.marker(this));
        if (counts.nonEditable >= 1) {
            cancelTimeout();
            if (LabStore.calibrationMode(this)) {
                LabStore.markCalibrationVerified(this, verifyingCandidate);
                completeStep(expectedStep);
            } else {
                LabStore.markVerified(this, verifyingCandidate);
                launchLabForeground();
            }
        }
    }

    private void onVerifyTimeout(int expectedStep, String reason) {
        if (!isCurrentStep(expectedStep)) return;
        LabStore.append(this, reason);
        LabStore.setCandidateIndex(this, LabStore.candidateIndex(this) + 1);
        LabStore.setState(this, "RUNNING");
        scheduleCurrentStep(0L);
    }

    private void opShareFiles(JSONObject step) throws Exception {
        int count = Math.max(1, Math.min(step.optInt("count", 1), 2));
        ArrayList<Uri> uris = new ArrayList<>();
        for (int i = 0; i < count; i++) uris.add(createProbeFile("share" + (i + 1)));
        Intent out = new Intent(count == 1 ? Intent.ACTION_SEND : Intent.ACTION_SEND_MULTIPLE);
        out.setComponent(new ComponentName(ProfileGuard.CHATGPT_PACKAGE, ProfileGuard.CHATGPT_MAIN));
        out.setType("text/plain");
        if (count == 1) {
            out.putExtra(Intent.EXTRA_STREAM, uris.get(0));
        } else {
            out.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris);
        }
        ClipData clip = ClipData.newRawUri("Capability Lab", uris.get(0));
        for (int i = 1; i < uris.size(); i++) clip.addItem(new ClipData.Item(uris.get(i)));
        out.setClipData(clip);
        out.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
        LabStore.append(this, "SHARE_FILES launch count=" + count);
        startActivity(out);
    }

    private Uri createProbeFile(String suffix) throws Exception {
        String marker = "LAB_FILE_" + UUID.randomUUID().toString().replace("-", "").substring(0, 12).toUpperCase(Locale.US);
        File f = new File(getCacheDir(), "capability-lab-" + suffix + "-" + marker + ".txt");
        String text = "ChatGPT Capability Lab\nmarker=" + marker + "\nSynthetic test file.\n";
        try (FileOutputStream out = new FileOutputStream(f)) {
            out.write(text.getBytes(StandardCharsets.UTF_8));
        }
        return FileProvider.getUriForFile(this, getPackageName() + ".files", f);
    }

    private void openVoice() {
        Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse("https://chatgpt.com/voice"));
        i.setComponent(new ComponentName(ProfileGuard.CHATGPT_PACKAGE, ProfileGuard.CHATGPT_DEEPLINK));
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        LabStore.append(this, "OPEN_VOICE /voice");
        startActivity(i);
    }

    private void processText() {
        String marker = "LAB_PROCESS_TEXT_" + UUID.randomUUID().toString().replace("-", "").substring(0, 12).toUpperCase(Locale.US);
        Intent i = new Intent(Intent.ACTION_PROCESS_TEXT);
        i.setComponent(new ComponentName(ProfileGuard.CHATGPT_PACKAGE, ProfileGuard.CHATGPT_PROCESS_TEXT));
        i.setType("text/plain");
        i.putExtra(Intent.EXTRA_PROCESS_TEXT, marker);
        i.putExtra(Intent.EXTRA_PROCESS_TEXT_READONLY, true);
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        LabStore.append(this, "PROCESS_TEXT marker=" + marker);
        startActivity(i);
    }

    private void resumeChatGpt() {
        Intent i = getPackageManager().getLaunchIntentForPackage(ProfileGuard.CHATGPT_PACKAGE);
        if (i == null) throw new IllegalStateException("ChatGPT launch intent missing");
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        LabStore.append(this, "RESUME_CHATGPT launchIntent");
        startActivity(i);
    }

    private void launchLabForeground() {
        Intent i = new Intent(this, MainActivity.class);
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        startActivity(i);
    }

    private void completeStep(int expectedStep) {
        if (!LabStore.advanceStepIfCurrent(this, expectedStep)) return;
        cancelTimeout();
        scheduleCurrentStep(120L);
    }

    private void armTimeout(long requestedMs, String reason, int expectedStep) {
        cancelTimeout();
        long ms = Math.max(1000L, Math.min(requestedMs, 180_000L));
        timeoutStep = expectedStep;
        timeoutRunnable = () -> {
            timeoutRunnable = null;
            int armedStep = timeoutStep;
            timeoutStep = -1;
            if (armedStep != expectedStep || !isCurrentStep(expectedStep)) return;
            String state = LabStore.state(this);
            if ("WAITING_VERIFY_NEUTRAL".equals(state) || "WAITING_VERIFY_CANDIDATE".equals(state)) {
                onVerifyTimeout(expectedStep, reason);
            } else if ("SEND_CLAIMED".equals(state) && LabStore.writeClaimed(this)) {
                failUncertain(reason + " after durable claim");
            } else {
                if (reason.startsWith("GLOBAL_SEARCH_BINDING_TIMEOUT")) {
                    List<AccessibilityNodeInfo> roots = chatGptRoots();
                    String census = controlCensus(roots, 260);
                    String snapshot = roots.isEmpty() ? "<no ChatGPT roots>"
                            : normalizedTree(roots.get(0), LabStore.marker(this), 220, 10);
                    LabStore.append(this, "GLOBAL_SEARCH_TIMEOUT_DIAGNOSTIC state=" + state
                            + " windows=" + roots.size()
                            + " controlCensus=" + LabStore.abbrev(census, 18000)
                            + " activeSnapshot=" + LabStore.abbrev(snapshot, 8000));
                }
                failRun(reason);
            }
        };
        handler.postDelayed(timeoutRunnable, ms);
    }

    private void cancelTimeout() {
        if (timeoutRunnable != null) handler.removeCallbacks(timeoutRunnable);
        timeoutRunnable = null;
        timeoutStep = -1;
    }

    private void failRun(String reason) {
        cancelTimeout();
        LabStore.append(this, "FAIL " + reason);
        LabStore.finish(this, "FAIL:" + reason);
        launchLabForeground();
    }

    private void failUncertain(String reason) {
        cancelTimeout();
        LabStore.append(this, "UNCERTAIN " + reason + " writeClaimed=true; no replay permitted");
        LabStore.finish(this, "UNCERTAIN:" + reason);
        launchLabForeground();
    }

    private void finishWithoutVerifiedId(String status) {
        LabStore.finish(this, status);
        launchLabForeground();
    }

    private List<String> plausibleCandidates() {
        List<String> out = new ArrayList<>();
        for (String raw : LabStore.candidates(this)) {
            String x = raw == null ? "" : raw.trim();
            if (UUID_PATTERN.matcher(x).matches() || HEX32_PATTERN.matcher(x).matches()) {
                if (!out.contains(x)) out.add(x);
            }
        }
        return out;
    }

    private MetadataStats harvestAccessibilityMetadata(AccessibilityNodeInfo root) {
        MetadataStats stats = new MetadataStats();
        harvestAccessibilityMetadata0(root, stats, 0);
        return stats;
    }

    private void harvestAccessibilityMetadata0(AccessibilityNodeInfo n, MetadataStats stats, int depth) {
        if (n == null || depth > 40 || stats.nodes >= MAX_METADATA_NODES) return;
        stats.nodes++;
        stats.candidateMatches += addEmbeddedCandidates("a11y.viewId", n.getViewIdResourceName());
        if (Build.VERSION.SDK_INT >= 33) {
            try { stats.candidateMatches += addEmbeddedCandidates("a11y.uniqueId", n.getUniqueId()); }
            catch (Throwable ignored) {}
        }
        try { stats.candidateMatches += addEmbeddedCandidates("a11y.paneTitle", String.valueOf(n.getPaneTitle())); }
        catch (Throwable ignored) {}
        try { stats.candidateMatches += addEmbeddedCandidates("a11y.stateDescription", String.valueOf(n.getStateDescription())); }
        catch (Throwable ignored) {}
        try { stats.candidateMatches += addEmbeddedCandidates("a11y.tooltipText", String.valueOf(n.getTooltipText())); }
        catch (Throwable ignored) {}

        try {
            Bundle extras = n.getExtras();
            if (extras != null && !extras.isEmpty()) {
                for (String key : extras.keySet()) {
                    if (key == null) continue;
                    stats.extras++;
                    stats.candidateMatches += addEmbeddedCandidates("a11y.extraKey", key);
                    Object value;
                    try { value = extras.get(key); }
                    catch (Throwable t) { value = null; }
                    if (value != null) {
                        stats.candidateMatches += addEmbeddedCandidates("a11y.extra." + key, String.valueOf(value));
                    }
                }
            }
        } catch (Throwable ignored) {}

        for (int i = 0; i < n.getChildCount(); i++) {
            harvestAccessibilityMetadata0(n.getChild(i), stats, depth + 1);
        }
    }

    private int addEmbeddedCandidates(String source, String raw) {
        if (raw == null || raw.isEmpty()) return 0;
        int count = 0;
        Matcher uuid = UUID_FIND.matcher(raw);
        while (uuid.find() && count < 16) {
            LabStore.addCandidate(this, source, uuid.group());
            count++;
        }
        Matcher hex = HEX32_FIND.matcher(raw);
        while (hex.find() && count < 16) {
            LabStore.addCandidate(this, source, hex.group());
            count++;
        }
        return count;
    }

    private boolean isChatGptRoot(AccessibilityNodeInfo root) {
        CharSequence pkg = root.getPackageName();
        return pkg != null && ProfileGuard.CHATGPT_PACKAGE.contentEquals(pkg);
    }

    private List<AccessibilityNodeInfo> chatGptRoots() {
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

    private AccessibilityNodeInfo findRuntimeSearchRoot(List<AccessibilityNodeInfo> roots) {
        AccessibilityNodeInfo match = null;
        for (AccessibilityNodeInfo root : roots) {
            if (!isRuntimeSearchRoot(root)) continue;
            if (match != null && !match.equals(root)) return null;
            match = root;
        }
        return match;
    }

    private boolean isRuntimeSearchRoot(AccessibilityNodeInfo root) {
        if (root == null) return false;
        List<AccessibilityNodeInfo> search = new ArrayList<>();
        List<AccessibilityNodeInfo> close = new ArrayList<>();
        collectExactSemanticNodes(root, "Search", search, 0);
        collectExactSemanticNodes(root, "Close", close, 0);
        int editableSetTextFields = countEditableSearchFields(root, false);
        return search.size() == 1 && close.size() == 1 && editableSetTextFields == 1;
    }

    private AccessibilityNodeInfo findRuntimeSearchSurfaceRoot(List<AccessibilityNodeInfo> roots) {
        AccessibilityNodeInfo match = null;
        for (AccessibilityNodeInfo root : roots) {
            if (!isRuntimeSearchSurfaceRoot(root)) continue;
            if (match != null && !match.equals(root)) return null;
            match = root;
        }
        return match;
    }

    private boolean isRuntimeSearchSurfaceRoot(AccessibilityNodeInfo root) {
        if (root == null) return false;
        List<AccessibilityNodeInfo> close = new ArrayList<>();
        collectExactSemanticNodes(root, "Close", close, 0);
        int editableSetTextFields = countEditableSearchFields(root, false);
        return close.size() == 1 && editableSetTextFields == 1;
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

    private AccessibilityNodeInfo findUniqueHistorySearchEntryAcrossRoots(List<AccessibilityNodeInfo> roots) {
        List<AccessibilityNodeInfo> found = new ArrayList<>();
        for (AccessibilityNodeInfo root : roots) {
            AccessibilityNodeInfo n = findUniqueHistorySearchEntry(root);
            if (n != null) addUniqueNode(found, n);
        }
        return found.size() == 1 ? found.get(0) : null;
    }

    private AccessibilityNodeInfo findHistorySearchFieldAcrossRoots(List<AccessibilityNodeInfo> roots) {
        List<AccessibilityNodeInfo> found = new ArrayList<>();
        for (AccessibilityNodeInfo root : roots) {
            AccessibilityNodeInfo n = findHistorySearchField(root);
            if (n != null) addUniqueNode(found, n);
        }
        return found.size() == 1 ? found.get(0) : null;
    }

    private AccessibilityNodeInfo findRootWithHistorySearchFieldEquals(List<AccessibilityNodeInfo> roots, String marker) {
        AccessibilityNodeInfo match = null;
        for (AccessibilityNodeInfo root : roots) {
            if (!historySearchFieldEquals(root, marker)) continue;
            if (match != null && !match.equals(root)) return null;
            match = root;
        }
        return match;
    }

    private int countExactSemanticAcrossRoots(List<AccessibilityNodeInfo> roots, String exact) {
        List<AccessibilityNodeInfo> found = new ArrayList<>();
        for (AccessibilityNodeInfo root : roots) {
            List<AccessibilityNodeInfo> one = new ArrayList<>();
            collectExactSemanticNodes(root, exact, one, 0);
            for (AccessibilityNodeInfo n : one) addUniqueNode(found, n);
        }
        return found.size();
    }

    private AccessibilityNodeInfo findUniqueExactSemanticAcrossRoots(List<AccessibilityNodeInfo> roots, String exact) {
        List<AccessibilityNodeInfo> found = new ArrayList<>();
        for (AccessibilityNodeInfo root : roots) {
            List<AccessibilityNodeInfo> one = new ArrayList<>();
            collectExactSemanticNodes(root, exact, one, 0);
            for (AccessibilityNodeInfo n : one) addUniqueNode(found, n);
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

    private boolean isHistoryDrawerScreen(AccessibilityNodeInfo root) {
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
        if (filtered.size() == 1) return filtered.get(0);
        String[] aliases = new String[]{"Open sidebar", "Open navigation", "Open navigation menu", "Navigation menu", "Menu"};
        for (String alias : aliases) {
            List<AccessibilityNodeInfo> aliasNodes = new ArrayList<>();
            // Runtime v0.9 proved that substring matching is too broad for the generic
            // label "Menu": unrelated/redacted controls can contain that token and make
            // an otherwise unique official Menu look ambiguous. Navigation aliases are
            // therefore matched against the node's complete semantic value exactly.
            collectExactSemanticNodes(root, alias, aliasNodes, 0);
            if (aliasNodes.size() == 1) return aliasNodes.get(0);
        }
        return null;
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

    private boolean isGlobalSearchScreen(AccessibilityNodeInfo root) {
        if (containsSemantic(root, "chatgpt-global-search", 0)
                || countEditableSearchFields(root, true) == 1) {
            return true;
        }

        // v0.11 real-device evidence reached the official Search surface, but the runtime
        // EditText intentionally exposed no semantic/hint. Identify that surface only by
        // the exact first-party heading plus exactly one visible/enabled ACTION_SET_TEXT
        // field. This remains screen-scoped and must not turn a generic EditText into a
        // Search field elsewhere in ChatGPT.
        List<AccessibilityNodeInfo> runtimeSentinels = new ArrayList<>();
        collectExactSemanticNodes(root, "Search chats, files, and projects", runtimeSentinels, 0);
        int editableSetTextFields = countEditableSearchFields(root, false);
        return runtimeSentinels.size() == 1 && editableSetTextFields == 1;
    }

    private AccessibilityNodeInfo findUniqueGlobalSearchEntry(AccessibilityNodeInfo root) {
        List<AccessibilityNodeInfo> exactId = new ArrayList<>();
        collectSemanticNodes(root, "chatgpt.global-search", exactId, 0);
        if (exactId.size() == 1) return exactId.get(0);

        List<AccessibilityNodeInfo> labels = new ArrayList<>();
        collectSemanticNodes(root, "Search chats, files, and projects", labels, 0);
        if (labels.size() == 1) return labels.get(0);

        labels.clear();
        collectSemanticNodes(root, "Search chats", labels, 0);
        return labels.size() == 1 ? labels.get(0) : null;
    }

    private AccessibilityNodeInfo findGlobalSearchField(AccessibilityNodeInfo root) {
        List<AccessibilityNodeInfo> preferred = new ArrayList<>();
        collectEditableSearchFields(root, true, preferred, 0);
        if (preferred.size() == 1) return preferred.get(0);
        List<AccessibilityNodeInfo> any = new ArrayList<>();
        collectEditableSearchFields(root, false, any, 0);
        return any.size() == 1 ? any.get(0) : null;
    }

    private int countEditableSearchFields(AccessibilityNodeInfo root, boolean requireSearchSemantic) {
        List<AccessibilityNodeInfo> out = new ArrayList<>();
        collectEditableSearchFields(root, requireSearchSemantic, out, 0);
        return out.size();
    }

    private void collectEditableSearchFields(AccessibilityNodeInfo n, boolean requireSearchSemantic,
                                             List<AccessibilityNodeInfo> out, int depth) {
        if (n == null || depth > 40 || out.size() > 6) return;
        if (n.isEditable() && n.isVisibleToUser() && n.isEnabled()
                && hasAction(n, AccessibilityNodeInfo.ACTION_SET_TEXT)) {
            String semantic = semanticValue(n).toLowerCase(Locale.US);
            if (!requireSearchSemantic || semantic.contains("search chatgpt") || semantic.contains("chatgpt-global-search")) {
                out.add(n);
            }
        }
        for (int i = 0; i < n.getChildCount(); i++) {
            collectEditableSearchFields(n.getChild(i), requireSearchSemantic, out, depth + 1);
        }
    }

    private boolean containsSemantic(AccessibilityNodeInfo n, String token, int depth) {
        if (n == null || depth > 40) return false;
        if (semanticValue(n).toLowerCase(Locale.US).contains(token.toLowerCase(Locale.US))) return true;
        for (int i = 0; i < n.getChildCount(); i++) {
            if (containsSemantic(n.getChild(i), token, depth + 1)) return true;
        }
        return false;
    }

    private void collectSemanticNodes(AccessibilityNodeInfo n, String token, List<AccessibilityNodeInfo> out, int depth) {
        if (n == null || depth > 40 || out.size() > 8) return;
        if (semanticValue(n).toLowerCase(Locale.US).contains(token.toLowerCase(Locale.US))
                && n.isVisibleToUser() && n.isEnabled()) {
            out.add(n);
        }
        for (int i = 0; i < n.getChildCount(); i++) {
            collectSemanticNodes(n.getChild(i), token, out, depth + 1);
        }
    }

    private void collectExactSemanticNodes(AccessibilityNodeInfo n, String exact,
                                           List<AccessibilityNodeInfo> out, int depth) {
        if (n == null || depth > 40 || out.size() > 8) return;
        String value = semanticValue(n).trim();
        if (value.equalsIgnoreCase(exact) && n.isVisibleToUser() && n.isEnabled()) {
            out.add(n);
        }
        for (int i = 0; i < n.getChildCount(); i++) {
            collectExactSemanticNodes(n.getChild(i), exact, out, depth + 1);
        }
    }

    private String semanticValue(AccessibilityNodeInfo n) {
        if (n == null) return "";
        StringBuilder b = new StringBuilder();
        appendSemanticPart(b, n.getViewIdResourceName());
        appendSemanticPart(b, n.getText());
        appendSemanticPart(b, n.getContentDescription());
        try { appendSemanticPart(b, n.getHintText()); } catch (Throwable ignored) {}
        try { appendSemanticPart(b, n.getPaneTitle()); } catch (Throwable ignored) {}
        try { appendSemanticPart(b, n.getTooltipText()); } catch (Throwable ignored) {}
        try { appendSemanticPart(b, n.getStateDescription()); } catch (Throwable ignored) {}
        try {
            List<AccessibilityNodeInfo.AccessibilityAction> actions = n.getActionList();
            if (actions != null) for (AccessibilityNodeInfo.AccessibilityAction action : actions) {
                if (action != null) appendSemanticPart(b, action.getLabel());
            }
        } catch (Throwable ignored) {}
        return b.toString();
    }

    private static void appendSemanticPart(StringBuilder b, Object value) {
        if (value == null) return;
        if (b.length() > 0) b.append(' ');
        b.append(String.valueOf(value));
    }

    private AccessibilityNodeInfo firstClickableAncestor(AccessibilityNodeInfo start, int maxUp) {
        AccessibilityNodeInfo n = start;
        for (int i = 0; n != null && i <= maxUp; i++) {
            if (n.isVisibleToUser() && n.isEnabled() && n.isClickable()
                    && hasAction(n, AccessibilityNodeInfo.ACTION_CLICK)) {
                return n;
            }
            n = n.getParent();
        }
        return null;
    }

    private void collectNonEditableMarkerNodes(AccessibilityNodeInfo n, String marker,
                                               List<AccessibilityNodeInfo> out, int depth) {
        if (n == null || depth > 40 || out.size() > 12) return;
        if (!n.isEditable() && n.isVisibleToUser() && nodeText(n).contains(marker)) out.add(n);
        for (int i = 0; i < n.getChildCount(); i++) {
            collectNonEditableMarkerNodes(n.getChild(i), marker, out, depth + 1);
        }
    }

    private static void addUniqueNode(List<AccessibilityNodeInfo> out, AccessibilityNodeInfo candidate) {
        for (AccessibilityNodeInfo existing : out) {
            if (existing.equals(candidate)) return;
        }
        out.add(candidate);
    }

    private static boolean hasAction(AccessibilityNodeInfo n, int action) {
        return n != null && (n.getActions() & action) != 0;
    }

    private AccessibilityNodeInfo findUniqueEditableMarker(AccessibilityNodeInfo root, String marker) {
        List<AccessibilityNodeInfo> found = new ArrayList<>();
        collectMarkerNodes(root, marker, true, found, 0);
        return found.size() == 1 ? found.get(0) : null;
    }

    private MarkerCounts countMarkerNodes(AccessibilityNodeInfo root, String marker) {
        MarkerCounts counts = new MarkerCounts();
        if (marker == null || marker.isEmpty()) return counts;
        countMarkerNodes0(root, marker, counts, 0);
        return counts;
    }

    private void countMarkerNodes0(AccessibilityNodeInfo n, String marker, MarkerCounts counts, int depth) {
        if (n == null || depth > 40) return;
        String text = nodeText(n);
        if (text.contains(marker)) {
            if (n.isEditable()) counts.editable++; else counts.nonEditable++;
        }
        for (int i = 0; i < n.getChildCount(); i++) countMarkerNodes0(n.getChild(i), marker, counts, depth + 1);
    }

    private void collectMarkerNodes(AccessibilityNodeInfo n, String marker, boolean editableOnly, List<AccessibilityNodeInfo> out, int depth) {
        if (n == null || depth > 40 || out.size() > 8) return;
        if ((!editableOnly || n.isEditable()) && nodeText(n).contains(marker)) out.add(n);
        for (int i = 0; i < n.getChildCount(); i++) collectMarkerNodes(n.getChild(i), marker, editableOnly, out, depth + 1);
    }

    private void collectSendLeaves(AccessibilityNodeInfo n, List<AccessibilityNodeInfo> out, int depth) {
        if (n == null || depth > 12 || out.size() > 3) return;
        String desc = n.getContentDescription() == null ? "" : n.getContentDescription().toString().trim();
        String text = n.getText() == null ? "" : n.getText().toString().trim();
        if (("Send Message".equalsIgnoreCase(desc) || "Send Message".equalsIgnoreCase(text))
                && n.isEnabled() && n.isVisibleToUser()) out.add(n);
        for (int i = 0; i < n.getChildCount(); i++) collectSendLeaves(n.getChild(i), out, depth + 1);
    }

    private String normalizedTree(AccessibilityNodeInfo root, String marker, int maxNodes, int maxDepth) {
        StringBuilder out = new StringBuilder();
        int[] count = {0};
        appendNode(root, marker == null ? "" : marker, out, count, maxNodes, maxDepth, 0);
        return out.toString();
    }

    private void appendNode(AccessibilityNodeInfo n, String marker, StringBuilder out, int[] count, int maxNodes, int maxDepth, int depth) {
        if (n == null || count[0] >= maxNodes || depth > maxDepth) return;
        count[0]++;
        String text = n.getText() == null ? "" : n.getText().toString();
        String desc = n.getContentDescription() == null ? "" : n.getContentDescription().toString();
        out.append("\n");
        for (int i = 0; i < depth; i++) out.append('>');
        out.append(" class=").append(shortClass(n.getClassName()))
                .append(" editable=").append(n.isEditable())
                .append(" clickable=").append(n.isClickable())
                .append(" enabled=").append(n.isEnabled())
                .append(" visible=").append(n.isVisibleToUser())
                .append(" text=").append(redacted(text, marker))
                .append(" desc=").append(redacted(desc, marker));
        String id = n.getViewIdResourceName();
        if (id != null && !id.isEmpty()) out.append(" viewId=").append(id);
        for (int i = 0; i < n.getChildCount(); i++) appendNode(n.getChild(i), marker, out, count, maxNodes, maxDepth, depth + 1);
    }

    private String redacted(String value, String marker) {
        if (value == null || value.isEmpty()) return "\"\"";
        String one = value.replace('\n', ' ').replace('\r', ' ');
        String lower = one.toLowerCase(Locale.US);
        if ((!marker.isEmpty() && one.contains(marker))
                || one.startsWith("LAB_")
                || lower.equals("send message")
                || lower.contains("stop generating")
                || lower.equals("retry")
                || lower.equals("regenerate")
                || lower.equals("search chatgpt")
                || lower.contains("search chats")
                || lower.contains("conversation history")
                || lower.equals("search results")
                || lower.equals("recent")
                || lower.equals("pinned")
                || lower.contains("apps and conversations")
                || lower.contains("voice")) {
            return "\"" + LabStore.abbrev(one, 180) + "\"";
        }
        return "<redacted len=" + one.length() + " sha256=" + hashPrefix(one) + ">";
    }

    private static String hashPrefix(String value) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] d = md.digest(value.getBytes(StandardCharsets.UTF_8));
            StringBuilder b = new StringBuilder();
            for (int i = 0; i < Math.min(8, d.length); i++) b.append(String.format(Locale.US, "%02x", d[i] & 0xff));
            return b.toString();
        } catch (Throwable t) {
            return "error";
        }
    }

    private static String shortClass(CharSequence c) {
        if (c == null) return "";
        String s = c.toString();
        int dot = s.lastIndexOf('.');
        return dot >= 0 ? s.substring(dot + 1) : s;
    }

    private static String nodeText(AccessibilityNodeInfo n) {
        if (n == null) return "";
        CharSequence t = n.getText();
        return t == null ? "" : t.toString();
    }

    private static final class MarkerCounts {
        int editable;
        int nonEditable;
    }

    private static final class MetadataStats {
        int nodes;
        int extras;
        int candidateMatches;
    }
}
