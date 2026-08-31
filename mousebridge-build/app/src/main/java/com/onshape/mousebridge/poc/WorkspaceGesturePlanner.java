package com.onshape.mousebridge.poc;

import android.accessibilityservice.AccessibilityService;
import android.graphics.Rect;
import android.graphics.RectF;
import android.view.accessibility.AccessibilityNodeInfo;
import android.view.accessibility.AccessibilityWindowInfo;

import java.util.ArrayList;
import java.util.List;

final class WorkspaceGesturePlanner {
    private static final int GRID = 29;

    static final class Plan {
        final boolean valid;
        final float anchorX;
        final float anchorY;
        final float dirX;
        final float dirY;
        final float innerDistance;
        final float outerDistance;
        final float workspaceCenterX;
        final float workspaceCenterY;

        Plan(boolean valid, float anchorX, float anchorY, float dirX, float dirY,
             float innerDistance, float outerDistance,
             float workspaceCenterX, float workspaceCenterY) {
            this.valid = valid;
            this.anchorX = anchorX;
            this.anchorY = anchorY;
            this.dirX = dirX;
            this.dirY = dirY;
            this.innerDistance = innerDistance;
            this.outerDistance = outerDistance;
            this.workspaceCenterX = workspaceCenterX;
            this.workspaceCenterY = workspaceCenterY;
        }

        float achievedDelta() { return Math.max(0f, outerDistance - innerDistance); }
        float secondX(float distance) { return anchorX + dirX * distance; }
        float secondY(float distance) { return anchorY + dirY * distance; }
    }

    private WorkspaceGesturePlanner() {}

    static Plan plan(AccessibilityService service, float mouseX, float mouseY,
                     float desiredDeltaPx) {
        WorkspaceMap map = WorkspaceMap.capture(service);
        float touchMargin = dp(service, 5f);
        if (!map.isSafe(mouseX, mouseY, 0f)) return invalid(mouseX, mouseY);

        Point center = map.findSafestCenter();
        float dx = center.x - mouseX;
        float dy = center.y - mouseY;
        float len = hypot(dx, dy);
        float dirX;
        float dirY;
        if (len >= dp(service, 2f)) {
            dirX = dx / len;
            dirY = dy / len;
        } else {
            Point direction = map.findBestDirection(mouseX, mouseY, touchMargin);
            dirX = direction.x;
            dirY = direction.y;
        }

        float maxRay = map.maxSafeRay(mouseX, mouseY, dirX, dirY, touchMargin);
        float preferredInner = dp(service, 18f);
        if (maxRay < preferredInner + dp(service, 8f)) {
            Point visibleCenter = map.findSafestVisibleCenter(mouseX, mouseY, touchMargin);
            dx = visibleCenter.x - mouseX;
            dy = visibleCenter.y - mouseY;
            len = hypot(dx, dy);
            if (len >= dp(service, 2f)) {
                dirX = dx / len;
                dirY = dy / len;
                center = visibleCenter;
                maxRay = map.maxSafeRay(mouseX, mouseY, dirX, dirY, touchMargin);
            }
        }

        if (maxRay < dp(service, 10f)) {
            Point direction = map.findBestDirection(mouseX, mouseY, touchMargin);
            dirX = direction.x;
            dirY = direction.y;
            maxRay = map.maxSafeRay(mouseX, mouseY, dirX, dirY, touchMargin);
        }
        if (maxRay < dp(service, 8f)) return invalid(mouseX, mouseY);

        float inner = Math.min(preferredInner, Math.max(dp(service, 7f), maxRay * 0.34f));
        float room = Math.max(0f, maxRay - inner - dp(service, 2f));
        float delta = Math.min(Math.max(dp(service, 3f), desiredDeltaPx), room);
        if (room < dp(service, 2.5f)) return invalid(mouseX, mouseY);
        delta = Math.min(delta, room);
        float outer = inner + delta;

        return new Plan(true, mouseX, mouseY, dirX, dirY, inner, outer,
                center.x, center.y);
    }

    static Plan planTwoFingerTap(AccessibilityService service, float mouseX, float mouseY,
                                 float preferredSeparationPx) {
        WorkspaceMap map = WorkspaceMap.capture(service);
        if (!map.isSafe(mouseX, mouseY, 0f)) return invalid(mouseX, mouseY);

        Point center = map.findSafestCenter();
        float dx = center.x - mouseX;
        float dy = center.y - mouseY;
        float len = hypot(dx, dy);
        float dirX;
        float dirY;
        if (len >= dp(service, 2f)) {
            dirX = dx / len;
            dirY = dy / len;
        } else {
            Point best = map.findBestDirection(mouseX, mouseY, dp(service, 4f));
            dirX = best.x;
            dirY = best.y;
        }

        float maxRay = map.maxSafeRay(mouseX, mouseY, dirX, dirY, dp(service, 4f));
        float separation = Math.min(preferredSeparationPx, maxRay - dp(service, 2f));
        if (separation < dp(service, 7f)) return invalid(mouseX, mouseY);
        return new Plan(true, mouseX, mouseY, dirX, dirY,
                separation, separation, center.x, center.y);
    }

    private static Plan invalid(float x, float y) {
        return new Plan(false, x, y, 1f, 0f, 0f, 0f, x, y);
    }

    private static final class Point {
        final float x;
        final float y;
        Point(float x, float y) { this.x = x; this.y = y; }
    }

    private static final class WorkspaceMap {
        final AccessibilityService service;
        final RectF base;
        final ArrayList<RectF> obstacles;
        final float screenArea;

        WorkspaceMap(AccessibilityService service, RectF base, ArrayList<RectF> obstacles,
                     float screenArea) {
            this.service = service;
            this.base = base;
            this.obstacles = obstacles;
            this.screenArea = screenArea;
        }

        static WorkspaceMap capture(AccessibilityService service) {
            int width = service.getResources().getDisplayMetrics().widthPixels;
            int height = service.getResources().getDisplayMetrics().heightPixels;
            float screenArea = Math.max(1f, (float) width * height);
            RectF conservativeScreen = new RectF(
                    0f, dp(service, 92f), width,
                    Math.max(dp(service, 120f), height - dp(service, 72f)));

            Collector collector = new Collector(service, screenArea);
            AccessibilityNodeInfo root = service.getRootInActiveWindow();
            if (root != null) {
                collector.collect(root, 0);
                root.recycle();
            }

            RectF base = conservativeScreen;
            if (collector.largestSurface != null) {
                RectF candidate = new RectF(collector.largestSurface);
                if (candidate.intersect(conservativeScreen)
                        && area(candidate) > screenArea * 0.12f) base = candidate;
            }

            List<AccessibilityWindowInfo> windows = service.getWindows();
            if (windows != null) {
                for (AccessibilityWindowInfo window : windows) {
                    if (window == null) continue;
                    Rect r = new Rect();
                    window.getBoundsInScreen(r);
                    if (r.isEmpty()) continue;
                    RectF rf = new RectF(r);
                    float fraction = area(rf) / screenArea;
                    if (window.getType() != AccessibilityWindowInfo.TYPE_APPLICATION
                            || fraction < 0.82f) collector.addObstacle(rf);
                }
            }
            return new WorkspaceMap(service, base, collector.obstacles, screenArea);
        }

        boolean isSafe(float x, float y, float margin) {
            if (x < base.left + margin || x > base.right - margin
                    || y < base.top + margin || y > base.bottom - margin) return false;
            for (RectF obstacle : obstacles) {
                if (x >= obstacle.left - margin && x <= obstacle.right + margin
                        && y >= obstacle.top - margin && y <= obstacle.bottom + margin) return false;
            }
            return true;
        }

        Point findSafestCenter() {
            Point best = new Point(base.centerX(), base.centerY());
            float bestScore = -1f;
            float margin = dp(service, 4f);
            for (int gy = 0; gy < GRID; gy++) {
                float y = base.top + (gy + 0.5f) * base.height() / GRID;
                for (int gx = 0; gx < GRID; gx++) {
                    float x = base.left + (gx + 0.5f) * base.width() / GRID;
                    float score = clearance(x, y, margin);
                    if (score > bestScore) { bestScore = score; best = new Point(x, y); }
                }
            }
            return best;
        }

        Point findSafestVisibleCenter(float fromX, float fromY, float margin) {
            Point best = new Point(fromX, fromY);
            float bestScore = -1f;
            for (int gy = 0; gy < GRID; gy++) {
                float y = base.top + (gy + 0.5f) * base.height() / GRID;
                for (int gx = 0; gx < GRID; gx++) {
                    float x = base.left + (gx + 0.5f) * base.width() / GRID;
                    float score = clearance(x, y, margin);
                    if (score <= bestScore) continue;
                    if (!segmentSafe(fromX, fromY, x, y, margin)) continue;
                    bestScore = score;
                    best = new Point(x, y);
                }
            }
            return best;
        }

        Point findBestDirection(float x, float y, float margin) {
            float bestDistance = -1f;
            float bestX = 1f;
            float bestY = 0f;
            for (int i = 0; i < 24; i++) {
                double a = 2.0 * Math.PI * i / 24;
                float ux = (float) Math.cos(a);
                float uy = (float) Math.sin(a);
                float ray = maxSafeRay(x, y, ux, uy, margin);
                if (ray > bestDistance) {
                    bestDistance = ray;
                    bestX = ux;
                    bestY = uy;
                }
            }
            return new Point(bestX, bestY);
        }

        float maxSafeRay(float x, float y, float ux, float uy, float margin) {
            float step = Math.max(2f, dp(service, 3f));
            float max = (float) Math.hypot(base.width(), base.height());
            float last = 0f;
            for (float d = step; d <= max; d += step) {
                if (!isSafe(x + ux * d, y + uy * d, margin)) break;
                last = d;
            }
            return last;
        }

        boolean segmentSafe(float x1, float y1, float x2, float y2, float margin) {
            float length = hypot(x2 - x1, y2 - y1);
            if (length < 1f) return isSafe(x1, y1, margin);
            float step = Math.max(3f, dp(service, 5f));
            int count = Math.max(1, (int) Math.ceil(length / step));
            for (int i = 0; i <= count; i++) {
                float t = i / (float) count;
                if (!isSafe(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, margin)) return false;
            }
            return true;
        }

        float clearance(float x, float y, float margin) {
            if (!isSafe(x, y, margin)) return -1f;
            float best = Math.min(Math.min(x - base.left, base.right - x),
                    Math.min(y - base.top, base.bottom - y));
            for (RectF r : obstacles) {
                float dx = Math.max(Math.max(r.left - x, 0f), x - r.right);
                float dy = Math.max(Math.max(r.top - y, 0f), y - r.bottom);
                float d = (dx == 0f) ? dy : (dy == 0f ? dx : hypot(dx, dy));
                best = Math.min(best, d);
            }
            return best;
        }
    }

    private static final class Collector {
        final AccessibilityService service;
        final float screenArea;
        final ArrayList<RectF> obstacles = new ArrayList<>();
        RectF largestSurface;

        Collector(AccessibilityService service, float screenArea) {
            this.service = service;
            this.screenArea = screenArea;
        }

        int collect(AccessibilityNodeInfo node, int depth) {
            if (node == null || depth > 24) return 0;
            Rect r = new Rect();
            node.getBoundsInScreen(r);
            RectF bounds = new RectF(r);
            float fraction = area(bounds) / screenArea;
            String cls = node.getClassName() == null ? "" : node.getClassName().toString();

            boolean surface = cls.contains("SurfaceView") || cls.contains("TextureView")
                    || cls.contains("GLSurfaceView");
            if (surface && !r.isEmpty()) {
                if (largestSurface == null || area(bounds) > area(largestSurface))
                    largestSurface = new RectF(bounds);
                return 0;
            }

            int childEvidence = 0;
            int childCount = Math.min(node.getChildCount(), 80);
            for (int i = 0; i < childCount; i++) {
                AccessibilityNodeInfo child = node.getChild(i);
                if (child != null) {
                    childEvidence += Math.min(4, collect(child, depth + 1));
                    child.recycle();
                }
            }

            int actions = node.getActions();
            boolean scrollable = node.isScrollable()
                    || (actions & AccessibilityNodeInfo.ACTION_SCROLL_FORWARD) != 0
                    || (actions & AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD) != 0;
            boolean knownUiClass = cls.contains("Button") || cls.contains("EditText")
                    || cls.contains("RecyclerView") || cls.contains("ListView")
                    || cls.contains("ScrollView") || cls.contains("Toolbar")
                    || cls.contains("Menu") || cls.contains("Popup")
                    || cls.contains("Dialog") || cls.contains("Spinner") || cls.contains("Tab");
            boolean hasText = hasValue(node.getText()) || hasValue(node.getContentDescription());
            boolean interactive = node.isClickable() || node.isLongClickable()
                    || node.isCheckable() || node.isEditable();
            boolean ownEvidence = scrollable || knownUiClass || hasText || interactive;
            boolean add = !r.isEmpty() && fraction < 0.90f && (scrollable || knownUiClass
                    || (hasText && fraction < 0.28f)
                    || (interactive && fraction < 0.14f)
                    || (childEvidence >= 3 && fraction < 0.55f));
            if (add) addObstacle(bounds);
            return (ownEvidence ? 1 : 0) + Math.min(8, childEvidence);
        }

        void addObstacle(RectF candidate) {
            if (candidate == null || candidate.isEmpty()) return;
            if (candidate.width() < dp(service, 3f) || candidate.height() < dp(service, 3f)) return;
            obstacles.add(new RectF(candidate));
        }
    }

    private static boolean hasValue(CharSequence value) {
        return value != null && value.length() > 0;
    }
    private static float area(RectF r) {
        if (r == null) return 0f;
        return Math.max(0f, r.width()) * Math.max(0f, r.height());
    }
    private static float hypot(float x, float y) { return (float) Math.hypot(x, y); }
    private static float dp(AccessibilityService service, float value) {
        return value * service.getResources().getDisplayMetrics().density;
    }
}
