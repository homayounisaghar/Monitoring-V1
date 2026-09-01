package com.openai.controlplane.capabilitylab;

import android.accessibilityservice.AccessibilityService;
import android.content.ClipData;
import android.content.ComponentName;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

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
import java.util.regex.Pattern;

public class LabAccessibilityService extends AccessibilityService {
    private static volatile LabAccessibilityService INSTANCE;
    private static final Pattern UUID_PATTERN = Pattern.compile("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$");
    private static final Pattern HEX32_PATTERN = Pattern.compile("^[0-9a-fA-F]{32}$");
    private static final int MAX_VERIFY_CANDIDATES = 8;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private Runnable timeoutRunnable;
    private String verifyingCandidate = "";
    private String neutralMarker = "";

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        INSTANCE = this;
        LabStore.markAccessibilityConnected(this, true);
        LabStore.append(this, "ACCESSIBILITY_CONNECTED");
        if ("RUNNING".equals(LabStore.status(this))) {
            handler.postDelayed(this::executeCurrentStep, 250L);
        }
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (!ProfileGuard.CHATGPT_PACKAGE.equals(String.valueOf(event == null ? null : event.getPackageName()))) return;
        if (!"RUNNING".equals(LabStore.status(this))) return;
        String state = LabStore.state(this);
        if ("WAITING_SEMANTIC_SEND".equals(state) || "SEND_CLAIMED".equals(state)) {
            trySemanticSendOrReceipt();
        } else if ("WAITING_TREE_CAPTURE".equals(state)) {
            tryCaptureTreeAndAdvance();
        } else if ("WAITING_VERIFY_NEUTRAL".equals(state)) {
            tryVerifyNeutralThenCandidate();
        } else if ("WAITING_VERIFY_CANDIDATE".equals(state)) {
            tryVerifyCandidate();
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
        super.onDestroy();
    }

    static boolean isLive() { return INSTANCE != null; }

    static void startCurrentPlan() {
        LabAccessibilityService s = INSTANCE;
        if (s == null) throw new IllegalStateException("Accessibility service is not connected");
        s.handler.post(s::executeCurrentStep);
    }

    private JSONObject planRoot() throws Exception {
        return new JSONObject(LabStore.planJson(this));
    }

    private JSONArray steps() throws Exception {
        JSONArray a = planRoot().getJSONArray("steps");
        if (a.length() > 100) throw new IllegalStateException("too many plan steps");
        return a;
    }

    private void executeCurrentStep() {
        if (!"RUNNING".equals(LabStore.status(this))) return;
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
                    completeStep();
                    break;
                case "semantic_send":
                    opSemanticSend(step);
                    break;
                case "return_lab":
                    launchLabForeground();
                    completeStep();
                    break;
                case "wait":
                    opWait(step);
                    break;
                case "notification_snapshot":
                    LabNotificationService.snapshotFromRunner("plan_step_" + i);
                    completeStep();
                    break;
                case "channel_snapshot":
                    LabNotificationService.tryChannelSnapshotFromRunner();
                    completeStep();
                    break;
                case "resume_chatgpt":
                    resumeChatGpt();
                    completeStep();
                    break;
                case "capture_tree":
                    opCaptureTree(step);
                    break;
                case "verify_candidates":
                    opVerifyCandidates(step);
                    break;
                case "share_files":
                    opShareFiles(step);
                    completeStep();
                    break;
                case "open_voice":
                    openVoice();
                    completeStep();
                    break;
                case "process_text":
                    processText();
                    completeStep();
                    break;
                case "finish":
                    if (!LabStore.verifiedConversationId(this).isEmpty()) {
                        LabStore.finish(this, "PASS_VERIFIED_CONVERSATION_ID");
                    } else {
                        finishWithoutVerifiedId("INCONCLUSIVE_NO_VERIFIED_CONVERSATION_ID");
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

    private void opSemanticSend(JSONObject step) {
        LabStore.setState(this, "WAITING_SEMANTIC_SEND");
        armTimeout(step.optLong("timeoutMs", 15000L), "SEMANTIC_SEND_TIMEOUT");
        handler.postDelayed(this::trySemanticSendOrReceipt, 250L);
    }

    private void trySemanticSendOrReceipt() {
        if (!"RUNNING".equals(LabStore.status(this))) return;
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null || !isChatGptRoot(root)) return;
        String marker = LabStore.marker(this);
        if (marker.isEmpty()) return;

        MarkerCounts counts = countMarkerNodes(root, marker);
        if (LabStore.writeClaimed(this)) {
            if (counts.editable == 0 && counts.nonEditable >= 1) {
                cancelTimeout();
                LabStore.markSendConfirmed(this);
                LabStore.setState(this, "RUNNING");
                completeStep();
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
        handler.postDelayed(this::trySemanticSendOrReceipt, 180L);
    }

    private void opWait(JSONObject step) {
        long ms = Math.max(0L, Math.min(step.optLong("ms", 1000L), 180_000L));
        LabStore.setState(this, "WAITING_TIMER");
        LabStore.setWaitUntil(this, System.currentTimeMillis() + ms);
        cancelTimeout();
        handler.postDelayed(() -> {
            if (!"RUNNING".equals(LabStore.status(this))) return;
            LabStore.append(this, "WAIT_COMPLETE ms=" + ms);
            LabStore.setState(this, "RUNNING");
            completeStep();
        }, ms);
    }

    private void opCaptureTree(JSONObject step) {
        LabStore.setState(this, "WAITING_TREE_CAPTURE");
        String label = step.optString("label", "tree");
        LabStore.append(this, "TREE_CAPTURE_ARMED label=" + label);
        armTimeout(step.optLong("timeoutMs", 8000L), "TREE_CAPTURE_TIMEOUT label=" + label);
        handler.postDelayed(this::tryCaptureTreeAndAdvance, 250L);
    }

    private void tryCaptureTreeAndAdvance() {
        if (!"WAITING_TREE_CAPTURE".equals(LabStore.state(this))) return;
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null || !isChatGptRoot(root)) return;
        String marker = LabStore.marker(this);
        MarkerCounts counts = countMarkerNodes(root, marker);
        String snapshot = normalizedTree(root, marker, 300, 7);
        LabStore.append(this, "TREE_CAPTURE markerEditable=" + counts.editable + " markerNonEditable=" + counts.nonEditable + " snapshot=" + LabStore.abbrev(snapshot, 28000));
        cancelTimeout();
        LabStore.setState(this, "RUNNING");
        completeStep();
    }

    private void opVerifyCandidates(JSONObject step) {
        List<String> plausible = plausibleCandidates();
        LabStore.append(this, "VERIFY_CANDIDATES plausibleCount=" + plausible.size() + " rawCount=" + LabStore.candidates(this).size());
        if (plausible.isEmpty()) {
            completeStep();
            return;
        }
        int index = LabStore.candidateIndex(this);
        if (index >= plausible.size() || index >= MAX_VERIFY_CANDIDATES) {
            completeStep();
            return;
        }
        verifyingCandidate = plausible.get(index);
        neutralMarker = "LAB_NEUTRAL_" + UUID.randomUUID().toString().replace("-", "").substring(0, 12).toUpperCase(Locale.US);
        String prompt = neutralMarker;
        Uri uri = Uri.parse("https://chatgpt.com/c").buildUpon().appendQueryParameter("prompt", prompt).build();
        Intent neutral = new Intent(Intent.ACTION_VIEW, uri);
        neutral.setComponent(new ComponentName(ProfileGuard.CHATGPT_PACKAGE, ProfileGuard.CHATGPT_DEEPLINK));
        neutral.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        LabStore.setState(this, "WAITING_VERIFY_NEUTRAL");
        LabStore.append(this, "VERIFY_NEUTRAL launch candidateIndex=" + index + " candidate=" + verifyingCandidate + " neutralMarker=" + neutralMarker);
        startActivity(neutral);
        armTimeout(step.optLong("timeoutMs", 8000L), "VERIFY_NEUTRAL_TIMEOUT");
        handler.postDelayed(this::tryVerifyNeutralThenCandidate, 250L);
    }

    private void tryVerifyNeutralThenCandidate() {
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
        armTimeout(currentVerifyTimeout(), "VERIFY_CANDIDATE_TIMEOUT candidate=" + verifyingCandidate);
        handler.postDelayed(this::tryVerifyCandidate, 250L);
    }

    private long currentVerifyTimeout() {
        try {
            JSONObject step = steps().getJSONObject(LabStore.step(this));
            return Math.max(2000L, Math.min(step.optLong("timeoutMs", 8000L), 30000L));
        } catch (Throwable t) {
            return 8000L;
        }
    }

    private void tryVerifyCandidate() {
        if (!"WAITING_VERIFY_CANDIDATE".equals(LabStore.state(this))) return;
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null || !isChatGptRoot(root)) return;
        MarkerCounts counts = countMarkerNodes(root, LabStore.marker(this));
        if (counts.nonEditable >= 1) {
            cancelTimeout();
            LabStore.markVerified(this, verifyingCandidate);
            launchLabForeground();
        }
    }

    private void onVerifyTimeout(String reason) {
        if (!"RUNNING".equals(LabStore.status(this))) return;
        LabStore.append(this, reason);
        LabStore.setCandidateIndex(this, LabStore.candidateIndex(this) + 1);
        LabStore.setState(this, "RUNNING");
        handler.post(this::executeCurrentStep);
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

    private void completeStep() {
        cancelTimeout();
        LabStore.setState(this, "RUNNING");
        LabStore.setStep(this, LabStore.step(this) + 1);
        handler.postDelayed(this::executeCurrentStep, 120L);
    }

    private void armTimeout(long requestedMs, String reason) {
        cancelTimeout();
        long ms = Math.max(1000L, Math.min(requestedMs, 180_000L));
        timeoutRunnable = () -> {
            timeoutRunnable = null;
            String state = LabStore.state(this);
            if ("WAITING_VERIFY_NEUTRAL".equals(state) || "WAITING_VERIFY_CANDIDATE".equals(state)) {
                onVerifyTimeout(reason);
            } else if ("SEND_CLAIMED".equals(state) && LabStore.writeClaimed(this)) {
                failUncertain(reason + " after durable claim");
            } else {
                failRun(reason);
            }
        };
        handler.postDelayed(timeoutRunnable, ms);
    }

    private void cancelTimeout() {
        if (timeoutRunnable != null) handler.removeCallbacks(timeoutRunnable);
        timeoutRunnable = null;
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

    private boolean isChatGptRoot(AccessibilityNodeInfo root) {
        CharSequence pkg = root.getPackageName();
        return pkg != null && ProfileGuard.CHATGPT_PACKAGE.contentEquals(pkg);
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
}
