from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
helper = Path('app/src/main/java/com/najme/perplexityprobe/SendAccessibilityService.java')
manifest = Path('app/src/main/AndroidManifest.xml')
accessibility_xml = Path('app/src/main/res/xml/send_accessibility_service.xml')
gradle_file = Path('app/build.gradle')

s = service.read_text()
m = manifest.read_text()
g = gradle_file.read_text()


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.22 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


old_method = '''    private void sendFocusedField(){
        InputConnection ic=boundConnection;
        if(ic==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=ic){
            setStatus("Send cancelled — editor changed");
            return;
        }
        try{
            int advertised=editorInfo==null?EditorInfo.IME_ACTION_UNSPECIFIED:(editorInfo.imeOptions&EditorInfo.IME_MASK_ACTION);
            if(advertised==EditorInfo.IME_ACTION_SEND){
                boolean handled=ic.performEditorAction(EditorInfo.IME_ACTION_SEND);
                if(handled){setStatus("Sent");return;}
            }
            boolean down=ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_DOWN,KeyEvent.KEYCODE_ENTER));
            boolean up=ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_UP,KeyEvent.KEYCODE_ENTER));
            setStatus((down||up)?"Send key sent":"Send unavailable in this field");
        }catch(Exception e){
            setStatus("Send unavailable in this field");
        }
    }
'''

# Canonical v1.21 includes comments inside this method. Accept either exact shape.
if old_method not in s:
    start = s.index('    private void sendFocusedField(){')
    end = s.index('\n    private void startVoice(){', start)
    old_method = s[start:end] + '\n'

new_method = '''    private void sendFocusedField(){
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

s = replace_once(s, old_method, new_method, 'replace v1.21 raw-Enter send path')

manifest_old = '''        <service
            android:name=".PersianKeyboardService"
            android:exported="true"
            android:label="Persian keyboard"
            android:permission="android.permission.BIND_INPUT_METHOD">
            <intent-filter>
                <action android:name="android.view.InputMethod" />
            </intent-filter>
            <meta-data
                android:name="android.view.im"
                android:resource="@xml/ime_method" />
        </service>
'''
manifest_new = manifest_old + '''
        <service
            android:name=".SendAccessibilityService"
            android:exported="true"
            android:label="Persian keyboard Send helper"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService" />
            </intent-filter>
            <meta-data
                android:name="android.accessibilityservice"
                android:resource="@xml/send_accessibility_service" />
        </service>
'''
m = replace_once(m, manifest_old, manifest_new, 'AccessibilityService manifest registration')

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
import java.util.List;
import java.util.Locale;

public final class SendAccessibilityService extends AccessibilityService {
    private static volatile SendAccessibilityService instance;
    private final Handler main = new Handler(Looper.getMainLooper());
    private String pendingPackage;
    private int pendingAttempt;
    private static final int MAX_ATTEMPTS = 5;
    private static final long RETRY_MS = 160L;
    private static final int MAX_NODES = 3000;

    private static final class Candidate {
        final AccessibilityNodeInfo node;
        final int score;
        final Rect bounds;
        Candidate(AccessibilityNodeInfo node, int score, Rect bounds) {
            this.node = node; this.score = score; this.bounds = bounds;
        }
    }

    public static boolean requestSend(String targetPackage) {
        SendAccessibilityService service = instance;
        if (service == null || targetPackage == null || targetPackage.isEmpty()) return false;
        service.main.post(() -> {
            service.pendingPackage = targetPackage;
            service.pendingAttempt = 0;
            service.tryPendingSend();
        });
        return true;
    }

    @Override protected void onServiceConnected() { super.onServiceConnected(); instance = this; }
    @Override public void onDestroy() { if (instance == this) instance = null; main.removeCallbacksAndMessages(null); super.onDestroy(); }
    @Override public void onAccessibilityEvent(AccessibilityEvent event) {}
    @Override public void onInterrupt() {}

    private void tryPendingSend() {
        String targetPackage = pendingPackage;
        if (targetPackage == null) return;
        Candidate candidate = findBestCandidate(targetPackage);
        if (candidate != null && clickCandidate(candidate)) {
            pendingPackage = null; pendingAttempt = 0; return;
        }
        pendingAttempt++;
        if (pendingAttempt < MAX_ATTEMPTS) main.postDelayed(this::tryPendingSend, RETRY_MS);
        else {
            pendingPackage = null; pendingAttempt = 0;
            Toast.makeText(this, "Send button not found", Toast.LENGTH_SHORT).show();
        }
    }

    private Candidate findBestCandidate(String targetPackage) {
        Candidate best = null;
        List<AccessibilityWindowInfo> windows = getWindows();
        if (windows == null) return null;
        for (AccessibilityWindowInfo window : windows) {
            AccessibilityNodeInfo root = window == null ? null : window.getRoot();
            if (root == null) continue;
            CharSequence rootPackage = root.getPackageName();
            if (rootPackage == null || !targetPackage.contentEquals(rootPackage)) continue;
            Rect focusBounds = null;
            AccessibilityNodeInfo focus = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
            if (focus != null) {
                Rect r = new Rect(); focus.getBoundsInScreen(r); if (!r.isEmpty()) focusBounds = r;
            }
            ArrayDeque<AccessibilityNodeInfo> queue = new ArrayDeque<>();
            queue.add(root);
            int visited = 0;
            while (!queue.isEmpty() && visited++ < MAX_NODES) {
                AccessibilityNodeInfo node = queue.removeFirst();
                int semantic = semanticScore(node);
                if (semantic > 0 && node.isVisibleToUser() && node.isEnabled()) {
                    AccessibilityNodeInfo clickNode = clickableNode(node);
                    if (clickNode != null) {
                        Rect bounds = new Rect(); clickNode.getBoundsInScreen(bounds);
                        if (!bounds.isEmpty()) {
                            int score = semantic + proximityScore(bounds, focusBounds);
                            if (best == null || score > best.score) best = new Candidate(clickNode, score, bounds);
                        }
                    }
                }
                for (int i = 0; i < node.getChildCount(); i++) {
                    AccessibilityNodeInfo child = node.getChild(i); if (child != null) queue.addLast(child);
                }
            }
        }
        return best;
    }

    private int semanticScore(AccessibilityNodeInfo node) {
        String text = value(node.getText());
        String description = value(node.getContentDescription());
        String id = value(node.getViewIdResourceName());
        String label = (text + " " + description).trim().toLowerCase(Locale.ROOT);
        String idLower = id.toLowerCase(Locale.ROOT);
        if (label.contains("feedback") || label.contains("report") || label.contains("invite") ||
                label.contains("share") || label.contains("بازخورد") || label.contains("گزارش")) return 0;
        int score = 0;
        if (label.equals("send") || label.equals("send message") || label.equals("send prompt") ||
                label.equals("send query") || label.equals("submit") || label.equals("submit message") ||
                label.equals("submit prompt") || label.equals("ارسال") || label.equals("ارسال پیام") ||
                label.equals("فرستادن") || label.equals("بفرست")) score = 260;
        else if (label.startsWith("send ") || label.contains("send message") ||
                label.contains("send prompt") || label.contains("send query") ||
                label.startsWith("submit ") || label.contains("ارسال پیام") || label.startsWith("ارسال ")) score = 220;
        if (idLower.contains("send") || idLower.contains("submit")) score = Math.max(score, 190);
        if (score == 0) return 0;
        String className = value(node.getClassName()).toLowerCase(Locale.ROOT);
        if (className.contains("button")) score += 25;
        if (node.isClickable()) score += 25;
        return score;
    }

    private AccessibilityNodeInfo clickableNode(AccessibilityNodeInfo start) {
        AccessibilityNodeInfo node = start;
        for (int depth = 0; node != null && depth < 5; depth++) {
            if (node.isClickable() || hasClickAction(node)) return node;
            node = node.getParent();
        }
        return start;
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
        int dx = Math.abs(candidate.centerX() - focus.centerX());
        int dy = Math.abs(candidate.centerY() - focus.centerY());
        int penalty = Math.min(100, dx / 24 + dy / 8);
        return 100 - penalty;
    }

    private boolean clickCandidate(Candidate candidate) {
        try { if (candidate.node.performAction(AccessibilityNodeInfo.ACTION_CLICK)) return true; } catch (Exception ignored) {}
        try {
            Path path = new Path(); path.moveTo(candidate.bounds.exactCenterX(), candidate.bounds.exactCenterY());
            GestureDescription gesture = new GestureDescription.Builder()
                    .addStroke(new GestureDescription.StrokeDescription(path, 0, 60)).build();
            return dispatchGesture(gesture, null, null);
        } catch (Exception ignored) { return false; }
    }

    private static String value(CharSequence value) { return value == null ? "" : value.toString(); }
}
''')

accessibility_xml.parent.mkdir(parents=True, exist_ok=True)
accessibility_xml.write_text('''<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged|typeViewFocused"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:notificationTimeout="50"
    android:canRetrieveWindowContent="true"
    android:canPerformGestures="true"
    android:accessibilityFlags="flagReportViewIds|flagRetrieveInteractiveWindows" />
''')

if 'versionCode 31' not in g or "versionName '1.21'" not in g:
    raise SystemExit('v1.22 patch: expected v1.21 version markers missing')
g = g.replace('versionCode 31', 'versionCode 32', 1)
g = g.replace("versionName '1.21'", "versionName '1.22'", 1)

required = [
    'SendAccessibilityService.requestSend(targetPackage)',
    'setStatus(queued?"Sending…":"Enable Send helper in Accessibility");',
    'class SendAccessibilityService extends AccessibilityService',
    'public static boolean requestSend(String targetPackage)',
    'getWindows()',
    'dispatchGesture(gesture, null, null)',
    'android:name=".SendAccessibilityService"',
    'android.permission.BIND_ACCESSIBILITY_SERVICE',
    'android:canRetrieveWindowContent="true"',
    'android:canPerformGestures="true"',
]
combined = s + '\n' + helper.read_text() + '\n' + m + '\n' + accessibility_xml.read_text()
for needle in required:
    if needle not in combined:
        raise SystemExit(f'v1.22 patch: missing invariant: {needle}')

forbidden = [
    'if(advertised==EditorInfo.IME_ACTION_SEND){',
    'setStatus((down||up)?"Send key sent":"Send unavailable in this field");',
    'versionCode 31',
    "versionName '1.21'",
    'MAX_CAPTURE_MS',
]
for needle in forbidden:
    if needle in s or needle in g:
        raise SystemExit(f'v1.22 patch: forbidden old Send behavior remains: {needle}')

service.write_text(s)
manifest.write_text(m)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.22 accessibility Send-button patch')
