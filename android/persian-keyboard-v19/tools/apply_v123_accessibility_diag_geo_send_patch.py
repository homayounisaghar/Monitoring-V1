from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
helper = Path('app/src/main/java/com/najme/perplexityprobe/SendAccessibilityService.java')
gradle_file = Path('app/build.gradle')

s = service.read_text()
g = gradle_file.read_text()

old_method = '''    private void sendFocusedField(){
        InputConnection ic=boundConnection;
        if(ic==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=ic){
            setStatus("Send cancelled — editor changed");
            return;
        }
        String targetPackage=editorInfo==null?null:editorInfo.packageName;
        if(targetPackage==null||targetPackage.isEmpty()){
            setStatus("Send unavailable — no target app");
            return;
        }
        boolean queued=SendAccessibilityService.requestSend(targetPackage);
        setStatus(queued?"Sending…":"Enable Send helper in Accessibility");
    }
'''

new_method = '''    private void sendFocusedField(){
        InputConnection ic=boundConnection;
        if(ic==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=ic){
            setStatus("SEND: editor changed");
            return;
        }
        String targetPackage=editorInfo==null?null:editorInfo.packageName;
        if(targetPackage==null||targetPackage.isEmpty()){
            setStatus("SEND: no target app");
            return;
        }
        boolean queued=SendAccessibilityService.requestSend(targetPackage);
        if(!queued){
            setStatus("SEND helper OFF — enable Accessibility");
            android.widget.Toast.makeText(this,"SEND helper OFF — enable Accessibility",android.widget.Toast.LENGTH_LONG).show();
            return;
        }
        setStatus("SEND: scanning button…");
        main.postDelayed(()->{
            String result=SendAccessibilityService.getLastResult();
            if(result!=null&&!result.isEmpty())setStatus(result);
        },1400L);
    }
'''

if old_method not in s:
    raise SystemExit('v1.23 patch: v1.22 sendFocusedField not found')
s = s.replace(old_method, new_method, 1)

helper.parent.mkdir(parents=True, exist_ok=True)
helper.write_text(r'''package com.najme.perplexityprobe;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.graphics.Rect;
import android.os.Handler;
import android.os.Looper;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.view.accessibility.AccessibilityWindowInfo;
import android.widget.Toast;

import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * One-shot Send helper. It is idle until the user explicitly long-presses the
 * recording microphone. Diagnostics contain only structural counts/status and
 * never accessibility text.
 */
public final class SendAccessibilityService extends AccessibilityService {
    private static volatile SendAccessibilityService instance;
    private static volatile String lastResult = "";

    private final Handler main = new Handler(Looper.getMainLooper());
    private String pendingPackage;
    private int pendingAttempt;
    private ScanStats lastStats;

    private static final int MAX_ATTEMPTS = 6;
    private static final long RETRY_MS = 180L;
    private static final int MAX_NODES = 3500;

    private static final class Candidate {
        final AccessibilityNodeInfo node;
        final int score;
        final Rect bounds;
        final String kind;
        Candidate(AccessibilityNodeInfo node, int score, Rect bounds, String kind) {
            this.node = node;
            this.score = score;
            this.bounds = bounds;
            this.kind = kind;
        }
    }

    private static final class ScanStats {
        int windows;
        int matchingWindows;
        int nodes;
        int focusFound;
        int clickable;
        int labeled;
        int nearby;
        String compact() {
            return "w="+matchingWindows+"/"+windows+
                    " n="+nodes+
                    " f="+focusFound+
                    " c="+clickable+
                    " l="+labeled+
                    " g="+nearby;
        }
    }

    public static boolean requestSend(String targetPackage) {
        SendAccessibilityService service = instance;
        if (service == null || targetPackage == null || targetPackage.isEmpty()) return false;
        lastResult = "SEND: scanning";
        service.main.post(() -> {
            service.pendingPackage = targetPackage;
            service.pendingAttempt = 0;
            service.lastStats = null;
            service.tryPendingSend();
        });
        return true;
    }

    public static String getLastResult() {
        return lastResult;
    }

    @Override protected void onServiceConnected() {
        super.onServiceConnected();
        instance = this;
        lastResult = "SEND helper ON";
    }

    @Override public void onDestroy() {
        if (instance == this) instance = null;
        main.removeCallbacksAndMessages(null);
        super.onDestroy();
    }

    @Override public void onAccessibilityEvent(AccessibilityEvent event) {
        // Deliberately idle: no continuous screen processing.
    }

    @Override public void onInterrupt() {}

    private void setResult(String value, boolean toast) {
        lastResult = value;
        if (toast) Toast.makeText(this, value, Toast.LENGTH_LONG).show();
    }

    private void tryPendingSend() {
        String targetPackage = pendingPackage;
        if (targetPackage == null) return;

        ScanStats stats = new ScanStats();
        Candidate candidate = findBestCandidate(targetPackage, stats);
        lastStats = stats;

        if (candidate != null && clickCandidate(candidate)) {
            pendingPackage = null;
            pendingAttempt = 0;
            setResult("SEND: "+candidate.kind+" button tapped", true);
            return;
        }

        pendingAttempt++;
        if (pendingAttempt < MAX_ATTEMPTS) {
            main.postDelayed(this::tryPendingSend, RETRY_MS);
        } else {
            pendingPackage = null;
            pendingAttempt = 0;
            String diag = lastStats == null ? "SEND diag: no scan" : "SEND diag: "+lastStats.compact();
            setResult(diag, true);
        }
    }

    private Candidate findBestCandidate(String targetPackage, ScanStats stats) {
        Candidate bestLabeled = null;
        Candidate bestNearby = null;
        List<AccessibilityWindowInfo> windows = getWindows();
        if (windows == null) return null;
        stats.windows = windows.size();

        for (AccessibilityWindowInfo window : windows) {
            AccessibilityNodeInfo root = window == null ? null : window.getRoot();
            if (root == null) continue;
            CharSequence rootPackage = root.getPackageName();
            if (rootPackage == null || !targetPackage.contentEquals(rootPackage)) continue;
            stats.matchingWindows++;

            Rect focusBounds = null;
            AccessibilityNodeInfo focus = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
            if (focus != null) {
                Rect r = new Rect();
                focus.getBoundsInScreen(r);
                if (!r.isEmpty()) {
                    focusBounds = r;
                    stats.focusFound++;
                }
            }

            ArrayDeque<AccessibilityNodeInfo> queue = new ArrayDeque<>();
            Set<String> seenBounds = new HashSet<>();
            queue.add(root);
            int visited = 0;

            while (!queue.isEmpty() && visited++ < MAX_NODES) {
                AccessibilityNodeInfo node = queue.removeFirst();
                stats.nodes++;

                if (node.isVisibleToUser() && node.isEnabled()) {
                    AccessibilityNodeInfo clickNode = clickableNode(node);
                    if (clickNode != null && !clickNode.isEditable()) {
                        Rect bounds = new Rect();
                        clickNode.getBoundsInScreen(bounds);
                        if (!bounds.isEmpty()) {
                            String key = bounds.flattenToString();
                            if (seenBounds.add(key)) {
                                stats.clickable++;

                                int semantic = semanticScore(node);
                                if (semantic > 0) {
                                    stats.labeled++;
                                    int score = semantic + proximityScore(bounds, focusBounds);
                                    if (bestLabeled == null || score > bestLabeled.score) {
                                        bestLabeled = new Candidate(clickNode, score, bounds, "labeled");
                                    }
                                } else {
                                    int geo = geometryScore(clickNode, bounds, focusBounds);
                                    if (geo > 0) {
                                        stats.nearby++;
                                        if (bestNearby == null || geo > bestNearby.score) {
                                            bestNearby = new Candidate(clickNode, geo, bounds, "nearby");
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                for (int i = 0; i < node.getChildCount(); i++) {
                    AccessibilityNodeInfo child = node.getChild(i);
                    if (child != null) queue.addLast(child);
                }
            }
        }

        return bestLabeled != null ? bestLabeled : bestNearby;
    }

    private int semanticScore(AccessibilityNodeInfo node) {
        String text = value(node.getText());
        String description = value(node.getContentDescription());
        String id = value(node.getViewIdResourceName());
        String label = (text + " " + description).trim().toLowerCase(Locale.ROOT);
        String idLower = id.toLowerCase(Locale.ROOT);

        if (label.contains("feedback") || label.contains("report") || label.contains("invite") ||
                label.contains("share") || label.contains("بازخورد") || label.contains("گزارش")) {
            return 0;
        }

        int score = 0;
        if (label.equals("send") || label.equals("send message") || label.equals("send prompt") ||
                label.equals("send query") || label.equals("submit") || label.equals("submit message") ||
                label.equals("submit prompt") || label.equals("ارسال") || label.equals("ارسال پیام") ||
                label.equals("فرستادن") || label.equals("بفرست")) {
            score = 280;
        } else if (label.startsWith("send ") || label.contains("send message") ||
                label.contains("send prompt") || label.contains("send query") ||
                label.startsWith("submit ") || label.contains("ارسال پیام") || label.startsWith("ارسال ")) {
            score = 230;
        }

        if (idLower.contains("send") || idLower.contains("submit")) score = Math.max(score, 210);
        if (score == 0) return 0;

        String className = value(node.getClassName()).toLowerCase(Locale.ROOT);
        if (className.contains("button")) score += 30;
        if (node.isClickable()) score += 25;
        return score;
    }

    private int geometryScore(AccessibilityNodeInfo node, Rect b, Rect focus) {
        if (focus == null || focus.isEmpty()) return 0;
        if (b.contains(focus) || (b.width() >= focus.width()*3/4 && b.height() >= focus.height()*3/4)) return 0;

        int fh = Math.max(1, focus.height());
        int cx = b.centerX();
        int cy = b.centerY();
        int dx = Math.abs(cx - focus.right);
        int dy = Math.abs(cy - focus.centerY());

        boolean verticalNear = cy >= focus.top - fh/2 && cy <= focus.bottom + fh/2;
        boolean rightSide = cx >= focus.centerX() && cx <= focus.right + fh*2;
        boolean compact = b.width() <= Math.max(fh*2, 260) && b.height() <= Math.max(fh*2, 260);
        if (!verticalNear || !rightSide || !compact) return 0;

        int score = 180;
        score -= Math.min(80, (dx * 80) / Math.max(fh*2, 1));
        score -= Math.min(55, (dy * 55) / Math.max(fh, 1));

        String className = value(node.getClassName()).toLowerCase(Locale.ROOT);
        if (className.contains("button")) score += 45;
        if (node.isClickable()) score += 25;
        if (cx >= focus.right - fh && cx <= focus.right + fh) score += 35;
        return Math.max(score, 0);
    }

    private AccessibilityNodeInfo clickableNode(AccessibilityNodeInfo start) {
        AccessibilityNodeInfo node = start;
        for (int depth = 0; node != null && depth < 5; depth++) {
            if (node.isClickable() || hasClickAction(node)) return node;
            node = node.getParent();
        }
        return null;
    }

    private boolean hasClickAction(AccessibilityNodeInfo node) {
        List<AccessibilityNodeInfo.AccessibilityAction> actions = node.getActionList();
        if (actions == null) return false;
        for (AccessibilityNodeInfo.AccessibilityAction action : actions) {
            if (action != null && action.getId() == AccessibilityNodeInfo.ACTION_CLICK) return true;
        }
        return false;
    }

    private int proximityScore(Rect candidate, Rect focus) {
        if (focus == null) return 0;
        int dx = Math.abs(candidate.centerX() - focus.right);
        int dy = Math.abs(candidate.centerY() - focus.centerY());
        int penalty = Math.min(100, dx / 20 + dy / 8);
        return 100 - penalty;
    }

    private boolean clickCandidate(Candidate candidate) {
        try {
            if (candidate.node.performAction(AccessibilityNodeInfo.ACTION_CLICK)) return true;
        } catch (Exception ignored) {}

        try {
            float x = candidate.bounds.exactCenterX();
            float y = candidate.bounds.exactCenterY();
            Path path = new Path();
            path.moveTo(x, y);
            GestureDescription gesture = new GestureDescription.Builder()
                    .addStroke(new GestureDescription.StrokeDescription(path, 0, 70))
                    .build();
            return dispatchGesture(gesture, new GestureResultCallback() {
                @Override public void onCancelled(GestureDescription gestureDescription) {
                    setResult("SEND: tap cancelled", true);
                }
            }, null);
        } catch (Exception ignored) {
            return false;
        }
    }

    private static String value(CharSequence value) {
        return value == null ? "" : value.toString();
    }
}
''')

if 'versionCode 32' not in g or "versionName '1.22'" not in g:
    raise SystemExit('v1.23 patch: expected v1.22 version markers missing')
g = g.replace('versionCode 32', 'versionCode 33', 1)
g = g.replace("versionName '1.22'", "versionName '1.23'", 1)

required_service = [
    'SEND helper OFF — enable Accessibility',
    'SendAccessibilityService.getLastResult()',
    'SEND: scanning button…',
    'SendAccessibilityService.requestSend(targetPackage)',
    'private boolean sendAfterVoiceStop;',
    'if(shouldSend)main.postDelayed(this::sendFocusedField,40L);',
    'private void recoverSpeechTransport(String reason){',
]
for needle in required_service:
    if needle not in s:
        raise SystemExit(f'v1.23 patch: required IME invariant missing: {needle}')

helper_text = helper.read_text()
for needle in [
    'class SendAccessibilityService extends AccessibilityService',
    'public static String getLastResult()',
    'private int geometryScore(',
    'String compact()',
    'SEND diag:',
    'candidate.kind',
    'stats.nearby++',
    'getWindows()',
    'AccessibilityNodeInfo.ACTION_CLICK',
    'dispatchGesture(gesture, new GestureResultCallback()',
]:
    if needle not in helper_text:
        raise SystemExit(f'v1.23 patch: helper invariant missing: {needle}')

for forbidden in [
    'setStatus(queued?"Sending…":"Enable Send helper in Accessibility");',
    'versionCode 32',
    "versionName '1.22'",
    'MAX_CAPTURE_MS',
]:
    if forbidden in s or forbidden in g:
        raise SystemExit(f'v1.23 patch: forbidden v1.22 behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.23 accessibility diagnostics + geometric Send fallback patch')
