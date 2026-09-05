from pathlib import Path

helper = Path('app/src/main/java/com/najme/perplexityprobe/SendAccessibilityService.java')
gradle_file = Path('app/build.gradle')
h = helper.read_text()
g = gradle_file.read_text()

# v1.23 device evidence: with Accessibility enabled, the geometric fallback
# clicked Samsung Browser's Refresh control instead of ChatGPT's Send button.
# The browser chrome and web content share the same package, so package matching
# alone is insufficient. v1.24 scopes geometric candidates to the actual focused
# (or best visible editable) composer bounds and refuses geometry entirely if no
# editor can be identified.

h = h.replace(
'''        int focusFound;
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
''',
'''        int focusFound;
        int editors;
        int clickable;
        int labeled;
        int nearby;
        String compact() {
            return "w="+matchingWindows+"/"+windows+
                    " n="+nodes+
                    " f="+focusFound+
                    " e="+editors+
                    " c="+clickable+
                    " l="+labeled+
                    " g="+nearby;
        }
''', 1)

start = h.index('    private Candidate findBestCandidate(String targetPackage, ScanStats stats) {')
end = h.index('    private int semanticScore(AccessibilityNodeInfo node) {', start)
new_block = r'''    private static final class EditorTarget {
        final AccessibilityNodeInfo node;
        final Rect bounds;
        final boolean directFocus;
        EditorTarget(AccessibilityNodeInfo node, Rect bounds, boolean directFocus) {
            this.node = node;
            this.bounds = bounds;
            this.directFocus = directFocus;
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

            EditorTarget editor = findEditor(root, stats);
            Rect editorBounds = editor == null ? null : editor.bounds;

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
                                if (semantic > 0 && (editorBounds == null || nearComposer(bounds, editorBounds, true))) {
                                    stats.labeled++;
                                    int score = semantic + proximityScore(bounds, editorBounds);
                                    if (bestLabeled == null || score > bestLabeled.score) {
                                        bestLabeled = new Candidate(clickNode, score, bounds, "labeled-near");
                                    }
                                } else if (editorBounds != null) {
                                    int geo = geometryScore(clickNode, bounds, editorBounds);
                                    if (geo > 0) {
                                        stats.nearby++;
                                        if (bestNearby == null || geo > bestNearby.score) {
                                            bestNearby = new Candidate(clickNode, geo, bounds, "composer-nearby");
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

    private EditorTarget findEditor(AccessibilityNodeInfo root, ScanStats stats) {
        AccessibilityNodeInfo focus = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
        if (focus != null) {
            Rect r = new Rect();
            focus.getBoundsInScreen(r);
            if (!r.isEmpty() && focus.isVisibleToUser()) {
                stats.focusFound++;
                if (focus.isEditable() || isEditLike(focus)) {
                    stats.editors++;
                    return new EditorTarget(focus, r, true);
                }
            }
        }

        AccessibilityNodeInfo best = null;
        Rect bestBounds = null;
        long bestScore = Long.MIN_VALUE;
        ArrayDeque<AccessibilityNodeInfo> queue = new ArrayDeque<>();
        queue.add(root);
        int visited = 0;
        while (!queue.isEmpty() && visited++ < MAX_NODES) {
            AccessibilityNodeInfo node = queue.removeFirst();
            if (node.isVisibleToUser() && node.isEnabled() && (node.isEditable() || isEditLike(node))) {
                Rect b = new Rect();
                node.getBoundsInScreen(b);
                if (!b.isEmpty() && b.width() >= 80 && b.height() >= 32) {
                    stats.editors++;
                    long score = b.bottom * 4L + Math.min(b.width(), 1400);
                    if (node.isFocused()) score += 100000L;
                    if (node.isEditable()) score += 10000L;
                    if (isEditLike(node)) score += 3000L;
                    if (score > bestScore) {
                        bestScore = score;
                        best = node;
                        bestBounds = b;
                    }
                }
            }
            for (int i = 0; i < node.getChildCount(); i++) {
                AccessibilityNodeInfo child = node.getChild(i);
                if (child != null) queue.addLast(child);
            }
        }
        return best == null ? null : new EditorTarget(best, bestBounds, false);
    }

    private boolean isEditLike(AccessibilityNodeInfo node) {
        String className = value(node.getClassName()).toLowerCase(Locale.ROOT);
        return className.contains("edittext") || className.contains("textarea") ||
                className.contains("textfield") || className.contains("textbox");
    }

    private boolean nearComposer(Rect b, Rect editor, boolean labeled) {
        if (editor == null || editor.isEmpty()) return labeled;
        int eh = Math.max(1, editor.height());
        int allowance = Math.max(eh / 2, 80);
        int cy = b.centerY();
        int cx = b.centerX();

        if (cy < editor.top - allowance || cy > editor.bottom + allowance) return false;
        if (cx < editor.centerX() - Math.max(eh / 2, 60)) return false;
        if (cx > editor.right + Math.max(eh * 2, 240)) return false;

        int maxSide = Math.max(eh * 2, 260);
        if (!labeled && (b.width() > maxSide || b.height() > maxSide)) return false;
        return true;
    }

'''
h = h[:start] + new_block + h[end:]

old_geo = r'''    private int geometryScore(AccessibilityNodeInfo node, Rect b, Rect focus) {
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
'''
new_geo = r'''    private int geometryScore(AccessibilityNodeInfo node, Rect b, Rect editor) {
        if (editor == null || editor.isEmpty()) return 0;
        if (!nearComposer(b, editor, false)) return 0;
        if (b.contains(editor) || (b.width() >= editor.width()*3/4 && b.height() >= editor.height()*3/4)) return 0;

        int eh = Math.max(1, editor.height());
        int cx = b.centerX();
        int cy = b.centerY();
        int dx = Math.abs(cx - editor.right);
        int dy = Math.abs(cy - editor.centerY());

        int score = 220;
        score -= Math.min(90, (dx * 90) / Math.max(eh*2, 1));
        score -= Math.min(70, (dy * 70) / Math.max(eh, 1));

        String className = value(node.getClassName()).toLowerCase(Locale.ROOT);
        if (className.contains("button")) score += 50;
        if (node.isClickable()) score += 25;
        if (cx >= editor.right - eh && cx <= editor.right + eh) score += 45;
        if (b.left >= editor.centerX()) score += 20;
        return Math.max(score, 0);
    }
'''
if old_geo not in h:
    raise SystemExit('v1.24 patch: v1.23 geometryScore not found')
h = h.replace(old_geo, new_geo, 1)

if 'versionCode 33' not in g or "versionName '1.23'" not in g:
    raise SystemExit('v1.24 patch: expected v1.23 version markers missing')
g = g.replace('versionCode 33', 'versionCode 34', 1)
g = g.replace("versionName '1.23'", "versionName '1.24'", 1)

required = [
    'private EditorTarget findEditor(',
    'private boolean nearComposer(',
    'if (editorBounds != null)',
    '"composer-nearby"',
    'cy < editor.top - allowance',
    'stats.editors++',
    'e="+editors',
    'private int geometryScore(AccessibilityNodeInfo node, Rect b, Rect editor)',
]
for needle in required:
    if needle not in h:
        raise SystemExit(f'v1.24 patch: required invariant missing: {needle}')

for forbidden in [
    'private int geometryScore(AccessibilityNodeInfo node, Rect b, Rect focus)',
    'versionCode 33',
    "versionName '1.23'",
]:
    if forbidden in h or forbidden in g:
        raise SystemExit(f'v1.24 patch: forbidden v1.23 behavior remains: {forbidden}')

helper.write_text(h)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.24 composer-scoped accessibility Send patch')
