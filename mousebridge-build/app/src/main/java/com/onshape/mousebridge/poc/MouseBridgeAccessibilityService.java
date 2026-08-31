package com.onshape.mousebridge.poc;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.graphics.Rect;
import android.os.Handler;
import android.os.Looper;
import android.view.InputDevice;
import android.view.MotionEvent;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.view.accessibility.AccessibilityWindowInfo;

import java.util.List;

public class MouseBridgeAccessibilityService extends AccessibilityService {
    private static final String ONSHAPE_PACKAGE = "com.onshape.app";

    private static final long DRAG_SEGMENT_MS = 34L;
    private static final long PINCH_MS = 78L;
    private static final long ZOOM_COALESCE_MS = 24L;
    private static final long ZOOM_NEXT_SEGMENT_MS = 9L;
    private static final long UI_SWIPE_MS = 88L;

    private static final float MIN_ZOOM_WHEEL_UNITS = 0.16f;
    private static final float MAX_ZOOM_CHUNK = 1.35f;
    private static final float MIN_SAFE_PINCH_TRAVEL_DP = 13f;
    private static final float BASE_PINCH_TRAVEL_DP = 24f;

    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private final Runnable pinchPumpRunnable = this::pumpPinch;

    private boolean mouseCaptured = false;
    private int lastButtons = 0;
    private float cursorX = 300f;
    private float cursorY = 300f;
    private int displayId = 0;
    private CharSequence lastWindowPackage;

    private DragSession leftDrag;
    private DragSession middleDrag;

    private boolean rightPressed = false;
    private boolean rightStartedInWorkspace = false;
    private float rightDownX;
    private float rightDownY;

    private float pendingScroll = 0f;
    private boolean pinchBusy = false;

    private float pendingUiScroll = 0f;
    private float pendingHorizontalScroll = 0f;
    private boolean uiSwipeBusy = false;

    private int gestureEpoch = 0;

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        setMouseCapture(false);
        scheduleForegroundRefresh(0);
        scheduleForegroundRefresh(250);
        scheduleForegroundRefresh(800);
        scheduleForegroundRefresh(1500);
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event == null) return;
        int type = event.getEventType();
        CharSequence pkg = event.getPackageName();

        boolean fromOnshape = pkg != null && ONSHAPE_PACKAGE.contentEquals(pkg);
        if (fromOnshape && (type == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED
                || type == AccessibilityEvent.TYPE_WINDOWS_CHANGED
                || type == AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED
                || type == AccessibilityEvent.TYPE_VIEW_CLICKED
                || type == AccessibilityEvent.TYPE_VIEW_SELECTED)) {
            WorkspaceGesturePlanner.invalidate();
        }

        if (type != AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED
                && type != AccessibilityEvent.TYPE_WINDOWS_CHANGED) {
            return;
        }

        if (pkg != null) lastWindowPackage = pkg;
        scheduleForegroundRefresh(0);
        scheduleForegroundRefresh(60);
    }

    private void scheduleForegroundRefresh(long delayMs) {
        mainHandler.postDelayed(this::refreshForegroundState, delayMs);
    }

    private void refreshForegroundState() {
        CharSequence pkg = null;
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root != null) {
            pkg = root.getPackageName();
            root.recycle();
        }
        if (pkg == null) pkg = lastWindowPackage;
        boolean onshape = pkg != null && ONSHAPE_PACKAGE.contentEquals(pkg);
        setMouseCapture(onshape);
    }

    @Override
    public void onInterrupt() {
        cancelState();
    }

    @Override
    public void onDestroy() {
        setMouseCapture(false);
        WorkspaceGesturePlanner.clearCache();
        super.onDestroy();
    }

    private void setMouseCapture(boolean enabled) {
        if (mouseCaptured == enabled) return;
        AccessibilityServiceInfo info = getServiceInfo();
        if (info == null) return;
        info.setMotionEventSources(enabled ? InputDevice.SOURCE_MOUSE : 0);
        setServiceInfo(info);
        mouseCaptured = enabled;
        cancelState();
        if (enabled) {
            WorkspaceGesturePlanner.invalidate();
        } else {
            WorkspaceGesturePlanner.clearCache();
        }
    }

    @Override
    public void onMotionEvent(MotionEvent event) {
        if (!mouseCaptured || event == null) return;
        if ((event.getSource() & InputDevice.SOURCE_MOUSE) != InputDevice.SOURCE_MOUSE) return;

        cursorX = event.getRawX();
        cursorY = event.getRawY();

        int buttons = event.getButtonState();
        int changedDown = buttons & ~lastButtons;
        int changedUp = lastButtons & ~buttons;

        if ((changedDown & MotionEvent.BUTTON_PRIMARY) != 0) {
            leftDrag = new DragSession(1, cursorX, cursorY, displayId);
        }
        if ((changedDown & MotionEvent.BUTTON_TERTIARY) != 0) {
            if (isWorkspaceAt(cursorX, cursorY)) {
                middleDrag = new DragSession(2, cursorX, cursorY, displayId);
            }
        }
        if ((changedDown & MotionEvent.BUTTON_SECONDARY) != 0) {
            rightPressed = true;
            rightDownX = cursorX;
            rightDownY = cursorY;
            rightStartedInWorkspace = isWorkspaceAt(cursorX, cursorY);
        }

        if (event.getActionMasked() == MotionEvent.ACTION_MOVE
                || event.getActionMasked() == MotionEvent.ACTION_HOVER_MOVE) {
            if (leftDrag != null) leftDrag.onMove(cursorX, cursorY);
            if (middleDrag != null) middleDrag.onMove(cursorX, cursorY);
        }

        if ((changedUp & MotionEvent.BUTTON_PRIMARY) != 0 && leftDrag != null) {
            DragSession session = leftDrag;
            leftDrag = null;
            session.onRelease(cursorX, cursorY, true);
        }
        if ((changedUp & MotionEvent.BUTTON_TERTIARY) != 0 && middleDrag != null) {
            DragSession session = middleDrag;
            middleDrag = null;
            session.onRelease(cursorX, cursorY, false);
        }
        if ((changedUp & MotionEvent.BUTTON_SECONDARY) != 0 && rightPressed) {
            rightPressed = false;
            if (rightStartedInWorkspace
                    && distance(rightDownX, rightDownY, cursorX, cursorY) < dp(10)
                    && isWorkspaceAt(cursorX, cursorY)) {
                dispatchTwoFingerTap(cursorX, cursorY, displayId);
            }
            rightStartedInWorkspace = false;
        }

        if (event.getActionMasked() == MotionEvent.ACTION_SCROLL
                && leftDrag == null && middleDrag == null) {
            float vertical = event.getAxisValue(MotionEvent.AXIS_VSCROLL);
            if (vertical != 0f) handleWheel(vertical);
        }

        lastButtons = buttons;
    }

    private void handleWheel(float vertical) {
        PointContext context = inspectPoint(cursorX, cursorY);

        if (context.horizontalBottomStrip) {
            cancelPendingZoom();
            pendingUiScroll = 0f;
            pendingHorizontalScroll = clamp(pendingHorizontalScroll + vertical, -8f, 8f);
            pumpHorizontalUiSwipe(context.horizontalBounds);
            return;
        }

        if (context.isUi()) {
            cancelPendingZoom();
            pendingHorizontalScroll = 0f;
            if (context.scrollable || context.secondaryWindow) {
                pendingUiScroll = clamp(pendingUiScroll + vertical, -8f, 8f);
                pumpVerticalUiSwipe();
            }
            return;
        }

        pendingUiScroll = 0f;
        pendingHorizontalScroll = 0f;
        pendingScroll = clamp(pendingScroll + vertical, -8f, 8f);
        schedulePinchPump();
    }

    private void schedulePinchPump() {
        if (pinchBusy) return;
        mainHandler.removeCallbacks(pinchPumpRunnable);
        mainHandler.postDelayed(pinchPumpRunnable, ZOOM_COALESCE_MS);
    }

    private void cancelPendingZoom() {
        pendingScroll = 0f;
        mainHandler.removeCallbacks(pinchPumpRunnable);
    }

    private boolean isWorkspaceAt(float x, float y) {
        return !inspectPoint(x, y).isUi();
    }

    private PointContext inspectPoint(float x, float y) {
        PointContext context = new PointContext();
        context.secondaryWindow = isInSecondaryWindow(x, y);

        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root != null) {
            scanNode(root, x, y, context, 0);
            root.recycle();
        }

        int height = getResources().getDisplayMetrics().heightPixels;
        if (y < dp(110) || y > height - dp(82)) context.uiEvidence = true;
        return context;
    }

    private void scanNode(AccessibilityNodeInfo node, float x, float y,
                          PointContext context, int depth) {
        if (node == null || depth > 20) return;

        Rect bounds = new Rect();
        node.getBoundsInScreen(bounds);
        if (!bounds.contains(Math.round(x), Math.round(y))) return;

        int childCount = Math.min(node.getChildCount(), 64);
        for (int i = childCount - 1; i >= 0; i--) {
            AccessibilityNodeInfo child = node.getChild(i);
            if (child != null) {
                scanNode(child, x, y, context, depth + 1);
                child.recycle();
            }
        }

        String className = node.getClassName() == null ? "" : node.getClassName().toString();
        if (className.contains("SurfaceView")
                || className.contains("TextureView")
                || className.contains("GLSurfaceView")) {
            context.surfaceEvidence = true;
        }

        int actions = node.getActions();
        boolean scrollable = node.isScrollable()
                || (actions & AccessibilityNodeInfo.ACTION_SCROLL_FORWARD) != 0
                || (actions & AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD) != 0;
        if (scrollable) {
            context.scrollable = true;
            context.uiEvidence = true;
        }

        int screenWidth = getResources().getDisplayMetrics().widthPixels;
        int screenHeight = getResources().getDisplayMetrics().heightPixels;
        boolean wideShallow = bounds.width() > Math.max(dp(120), bounds.height() * 2.2f)
                && bounds.width() > screenWidth * 0.34f
                && bounds.height() < screenHeight * 0.22f
                && bounds.bottom > screenHeight * 0.68f;

        AccessibilityNodeInfo.CollectionInfo collection = node.getCollectionInfo();
        boolean horizontalCollection = collection != null
                && collection.getRowCount() <= 1
                && collection.getColumnCount() > 1;
        boolean horizontalClass = className.contains("HorizontalScrollView")
                || className.contains("TabLayout")
                || className.contains("ViewPager");
        boolean horizontalRecycler = className.contains("RecyclerView") && wideShallow;
        boolean horizontalTab = className.contains("Tab") && wideShallow;

        if ((horizontalClass || horizontalCollection || horizontalRecycler
                || horizontalTab || (scrollable && wideShallow))
                && bounds.bottom > screenHeight - dp(190)) {
            context.horizontalBottomStrip = true;
            context.uiEvidence = true;
            if (context.horizontalBounds.isEmpty()
                    || area(bounds) < area(context.horizontalBounds)) {
                context.horizontalBounds.set(bounds);
            }
        }

        boolean hasText = hasValue(node.getText()) || hasValue(node.getContentDescription());
        boolean interactive = node.isClickable() || node.isLongClickable() || node.isCheckable()
                || node.isEditable() || node.isFocusable();
        boolean uiClass = className.contains("Button")
                || className.contains("EditText")
                || className.contains("RecyclerView")
                || className.contains("ListView")
                || className.contains("ScrollView")
                || className.contains("Toolbar")
                || className.contains("Menu")
                || className.contains("Tab");

        long nodeArea = (long) Math.max(0, bounds.width()) * Math.max(0, bounds.height());
        long screenArea = (long) screenWidth * screenHeight;
        boolean reasonablySized = screenArea <= 0 || nodeArea < (long) (screenArea * 0.86f);

        if (reasonablySized && (hasText || interactive || uiClass)) {
            context.uiEvidence = true;
        }
    }

    private boolean isInSecondaryWindow(float x, float y) {
        List<AccessibilityWindowInfo> windows = getWindows();
        if (windows == null || windows.isEmpty()) return false;

        long screenArea = (long) getResources().getDisplayMetrics().widthPixels
                * getResources().getDisplayMetrics().heightPixels;
        int px = Math.round(x);
        int py = Math.round(y);

        for (AccessibilityWindowInfo window : windows) {
            if (window == null) continue;
            Rect bounds = new Rect();
            window.getBoundsInScreen(bounds);
            if (!bounds.contains(px, py)) continue;

            long area = (long) Math.max(0, bounds.width()) * Math.max(0, bounds.height());
            if (window.getType() != AccessibilityWindowInfo.TYPE_APPLICATION) return true;
            if (screenArea > 0 && area < (long) (screenArea * 0.82f)) return true;
        }
        return false;
    }

    private static boolean hasValue(CharSequence value) {
        return value != null && value.length() > 0;
    }

    private void dispatchSingleTap(float x, float y, int display) {
        if (pinchBusy || uiSwipeBusy) return;
        Path path = new Path();
        path.moveTo(x, y);
        GestureDescription.StrokeDescription stroke =
                new GestureDescription.StrokeDescription(path, 0, 45);
        GestureDescription.Builder builder = new GestureDescription.Builder();
        builder.setDisplayId(display);
        builder.addStroke(stroke);
        dispatchGesture(builder.build(), null, null);
    }

    private void dispatchTwoFingerTap(float x, float y, int display) {
        if (pinchBusy || uiSwipeBusy || hasActiveSyntheticDrag()) return;

        WorkspaceGesturePlanner.Plan plan = WorkspaceGesturePlanner.planTwoFingerTap(
                this, x, y, dp(24));
        if (!plan.valid) return;

        Path p1 = new Path();
        Path p2 = new Path();
        p1.moveTo(plan.anchorX, plan.anchorY);
        p2.moveTo(plan.secondX(plan.innerDistance), plan.secondY(plan.innerDistance));

        GestureDescription.Builder builder = new GestureDescription.Builder();
        builder.setDisplayId(display);
        builder.addStroke(new GestureDescription.StrokeDescription(p1, 0, 62));
        builder.addStroke(new GestureDescription.StrokeDescription(p2, 0, 62));
        dispatchGesture(builder.build(), null, null);
    }

    private void pumpPinch() {
        mainHandler.removeCallbacks(pinchPumpRunnable);
        if (pinchBusy || uiSwipeBusy || hasActiveSyntheticDrag()) return;

        if (Math.abs(pendingScroll) < MIN_ZOOM_WHEEL_UNITS) {
            pendingScroll = 0f;
            return;
        }

        float chunk = clamp(pendingScroll, -MAX_ZOOM_CHUNK, MAX_ZOOM_CHUNK);
        boolean zoomIn = chunk > 0f;
        float zoomSensitivity = MouseBridgeSettings.getZoomSensitivity(this);
        float magnitude = Math.abs(chunk);
        float requestedDelta = dp(BASE_PINCH_TRAVEL_DP) * zoomSensitivity * magnitude;
        requestedDelta = Math.max(dp(MIN_SAFE_PINCH_TRAVEL_DP), requestedDelta);

        WorkspaceGesturePlanner.Plan plan = WorkspaceGesturePlanner.plan(
                this, cursorX, cursorY, requestedDelta);
        if (!plan.valid || plan.achievedDelta() < dp(MIN_SAFE_PINCH_TRAVEL_DP)) {
            pendingScroll -= chunk;
            if (Math.abs(pendingScroll) < MIN_ZOOM_WHEEL_UNITS) pendingScroll = 0f;
            if (Math.abs(pendingScroll) >= MIN_ZOOM_WHEEL_UNITS) {
                mainHandler.postDelayed(pinchPumpRunnable, ZOOM_NEXT_SEGMENT_MS);
            }
            return;
        }

        float consumedFraction = clamp(
                plan.achievedDelta() / Math.max(1f, requestedDelta), 0.05f, 1f);
        float consumedChunk = chunk * consumedFraction;
        pendingScroll -= consumedChunk;
        if (Math.signum(pendingScroll) != Math.signum(chunk)
                || Math.abs(pendingScroll) < MIN_ZOOM_WHEEL_UNITS) {
            pendingScroll = 0f;
        }

        pinchBusy = true;
        final int epoch = gestureEpoch;

        float secondStart = zoomIn ? plan.innerDistance : plan.outerDistance;
        float secondEnd = zoomIn ? plan.outerDistance : plan.innerDistance;

        Path p1 = new Path();
        p1.moveTo(plan.anchorX, plan.anchorY);

        Path p2 = new Path();
        p2.moveTo(plan.secondX(secondStart), plan.secondY(secondStart));
        p2.lineTo(plan.secondX(secondEnd), plan.secondY(secondEnd));

        GestureDescription.Builder builder = new GestureDescription.Builder();
        builder.setDisplayId(displayId);
        builder.addStroke(new GestureDescription.StrokeDescription(p1, 0, PINCH_MS));
        builder.addStroke(new GestureDescription.StrokeDescription(p2, 0, PINCH_MS));

        boolean accepted = dispatchGesture(builder.build(), new GestureResultCallback() {
            @Override
            public void onCompleted(GestureDescription gestureDescription) {
                if (epoch != gestureEpoch) return;
                pinchBusy = false;
                if (Math.abs(pendingScroll) >= MIN_ZOOM_WHEEL_UNITS) {
                    mainHandler.postDelayed(pinchPumpRunnable, ZOOM_NEXT_SEGMENT_MS);
                } else {
                    pendingScroll = 0f;
                }
            }

            @Override
            public void onCancelled(GestureDescription gestureDescription) {
                if (epoch != gestureEpoch) return;
                pinchBusy = false;
                pendingScroll = 0f;
            }
        }, null);

        if (!accepted) {
            pinchBusy = false;
            pendingScroll = 0f;
        }
    }

    private void pumpVerticalUiSwipe() {
        if (uiSwipeBusy || pinchBusy || Math.abs(pendingUiScroll) < 0.01f
                || hasActiveSyntheticDrag()) return;

        float chunk = clamp(pendingUiScroll, -2.0f, 2.0f);
        pendingUiScroll -= chunk;
        uiSwipeBusy = true;
        final int epoch = gestureEpoch;

        int width = getResources().getDisplayMetrics().widthPixels;
        int height = getResources().getDisplayMetrics().heightPixels;
        float uiSensitivity = MouseBridgeSettings.getUiScrollSensitivity(this);
        float magnitude = Math.max(0.45f, Math.min(2.0f, Math.abs(chunk)));
        float distance = dp(40) * uiSensitivity * magnitude;
        distance = clamp(distance, dp(7), dp(190));
        float x = clamp(cursorX, dp(16), width - dp(16));
        float startY = clamp(cursorY, dp(32), height - dp(32));
        float endY = chunk > 0f ? startY + distance : startY - distance;
        endY = clamp(endY, dp(20), height - dp(20));

        Path path = new Path();
        path.moveTo(x, startY);
        path.lineTo(x, endY);

        GestureDescription.Builder builder = new GestureDescription.Builder();
        builder.setDisplayId(displayId);
        builder.addStroke(new GestureDescription.StrokeDescription(path, 0, UI_SWIPE_MS));

        boolean accepted = dispatchGesture(builder.build(), new GestureResultCallback() {
            @Override
            public void onCompleted(GestureDescription gestureDescription) {
                if (epoch != gestureEpoch) return;
                uiSwipeBusy = false;
                pumpVerticalUiSwipe();
            }

            @Override
            public void onCancelled(GestureDescription gestureDescription) {
                if (epoch != gestureEpoch) return;
                uiSwipeBusy = false;
                pendingUiScroll = 0f;
            }
        }, null);

        if (!accepted) {
            uiSwipeBusy = false;
            pendingUiScroll = 0f;
        }
    }

    private void pumpHorizontalUiSwipe(Rect preferredBounds) {
        if (uiSwipeBusy || pinchBusy || Math.abs(pendingHorizontalScroll) < 0.01f
                || hasActiveSyntheticDrag()) return;

        float chunk = clamp(pendingHorizontalScroll, -2.0f, 2.0f);
        pendingHorizontalScroll -= chunk;
        uiSwipeBusy = true;
        final int epoch = gestureEpoch;

        int width = getResources().getDisplayMetrics().widthPixels;
        int height = getResources().getDisplayMetrics().heightPixels;
        float uiSensitivity = MouseBridgeSettings.getUiScrollSensitivity(this);
        float magnitude = Math.max(0.45f, Math.min(2.0f, Math.abs(chunk)));
        float distance = dp(48) * uiSensitivity * magnitude;
        distance = clamp(distance, dp(9), dp(210));

        float left = preferredBounds != null && !preferredBounds.isEmpty()
                ? preferredBounds.left + dp(10) : dp(18);
        float right = preferredBounds != null && !preferredBounds.isEmpty()
                ? preferredBounds.right - dp(10) : width - dp(18);
        float top = preferredBounds != null && !preferredBounds.isEmpty()
                ? preferredBounds.top + dp(4) : height - dp(150);
        float bottom = preferredBounds != null && !preferredBounds.isEmpty()
                ? preferredBounds.bottom - dp(4) : height - dp(48);

        float startX = clamp(cursorX, left, right);
        float y = clamp(cursorY, top, bottom);
        float endX = chunk > 0f ? startX + distance : startX - distance;
        endX = clamp(endX, left, right);

        if (Math.abs(endX - startX) < dp(4)) {
            uiSwipeBusy = false;
            pendingHorizontalScroll = 0f;
            return;
        }

        Path path = new Path();
        path.moveTo(startX, y);
        path.lineTo(endX, y);

        GestureDescription.Builder builder = new GestureDescription.Builder();
        builder.setDisplayId(displayId);
        builder.addStroke(new GestureDescription.StrokeDescription(path, 0, UI_SWIPE_MS));

        boolean accepted = dispatchGesture(builder.build(), new GestureResultCallback() {
            @Override
            public void onCompleted(GestureDescription gestureDescription) {
                if (epoch != gestureEpoch) return;
                uiSwipeBusy = false;
                if (Math.abs(pendingHorizontalScroll) > 0.01f) {
                    PointContext next = inspectPoint(cursorX, cursorY);
                    if (next.horizontalBottomStrip) {
                        pumpHorizontalUiSwipe(next.horizontalBounds);
                    } else {
                        pendingHorizontalScroll = 0f;
                    }
                }
            }

            @Override
            public void onCancelled(GestureDescription gestureDescription) {
                if (epoch != gestureEpoch) return;
                uiSwipeBusy = false;
                pendingHorizontalScroll = 0f;
            }
        }, null);

        if (!accepted) {
            uiSwipeBusy = false;
            pendingHorizontalScroll = 0f;
        }
    }

    private boolean hasActiveSyntheticDrag() {
        return (leftDrag != null && leftDrag.started) || (middleDrag != null && middleDrag.started);
    }

    private void cancelState() {
        gestureEpoch++;
        mainHandler.removeCallbacks(pinchPumpRunnable);
        lastButtons = 0;
        rightPressed = false;
        rightStartedInWorkspace = false;
        pendingScroll = 0f;
        pinchBusy = false;
        pendingUiScroll = 0f;
        pendingHorizontalScroll = 0f;
        uiSwipeBusy = false;
        if (leftDrag != null) leftDrag.cancelled = true;
        if (middleDrag != null) middleDrag.cancelled = true;
        leftDrag = null;
        middleDrag = null;
    }

    private class DragSession {
        final int pointerCount;
        final float downX;
        final float downY;
        final int targetDisplay;

        float desiredMouseX;
        float desiredMouseY;
        float dispatchedMouseX;
        float dispatchedMouseY;

        float f1x;
        float f1y;
        float f2x;
        float f2y;

        GestureDescription.StrokeDescription stroke1;
        GestureDescription.StrokeDescription stroke2;

        boolean started = false;
        boolean dispatching = false;
        boolean ended = false;
        boolean cancelled = false;

        DragSession(int pointerCount, float x, float y, int targetDisplay) {
            this.pointerCount = pointerCount;
            this.downX = x;
            this.downY = y;
            this.targetDisplay = targetDisplay;
            this.desiredMouseX = x;
            this.desiredMouseY = y;
            this.dispatchedMouseX = x;
            this.dispatchedMouseY = y;
        }

        void onMove(float x, float y) {
            if (cancelled || ended) return;
            desiredMouseX = x;
            desiredMouseY = y;
            if (!started && distance(downX, downY, x, y) >= dp(6)) {
                startDrag();
            } else if (started) {
                pump();
            }
        }

        void onRelease(float x, float y, boolean tapIfNotStarted) {
            if (cancelled) return;
            desiredMouseX = x;
            desiredMouseY = y;
            ended = true;
            if (!started) {
                if (tapIfNotStarted) dispatchSingleTap(x, y, targetDisplay);
                return;
            }
            pump();
        }

        void startDrag() {
            if (pinchBusy || uiSwipeBusy) {
                cancelled = true;
                return;
            }
            started = true;
            float dx = desiredMouseX - downX;
            float dy = desiredMouseY - downY;
            float halfSep = pointerCount == 2 ? dp(22) : 0f;

            float s1x = downX - halfSep;
            float s1y = downY;
            float e1x = s1x + dx;
            float e1y = s1y + dy;
            float s2x = downX + halfSep;
            float s2y = downY;
            float e2x = s2x + dx;
            float e2y = s2y + dy;

            Path p1 = new Path();
            p1.moveTo(s1x, s1y);
            p1.lineTo(e1x, e1y);
            stroke1 = new GestureDescription.StrokeDescription(p1, 0, DRAG_SEGMENT_MS, true);

            GestureDescription.Builder builder = new GestureDescription.Builder();
            builder.setDisplayId(targetDisplay);
            builder.addStroke(stroke1);

            if (pointerCount == 2) {
                Path p2 = new Path();
                p2.moveTo(s2x, s2y);
                p2.lineTo(e2x, e2y);
                stroke2 = new GestureDescription.StrokeDescription(p2, 0, DRAG_SEGMENT_MS, true);
                builder.addStroke(stroke2);
            }

            f1x = e1x;
            f1y = e1y;
            f2x = e2x;
            f2y = e2y;
            dispatchedMouseX = desiredMouseX;
            dispatchedMouseY = desiredMouseY;
            dispatching = true;

            boolean accepted = dispatchGesture(builder.build(), callback, null);
            if (!accepted) {
                dispatching = false;
                cancelled = true;
            }
        }

        void pump() {
            if (cancelled || !started || dispatching) return;

            float dx = desiredMouseX - dispatchedMouseX;
            float dy = desiredMouseY - dispatchedMouseY;
            boolean hasMovement = Math.abs(dx) >= 0.25f || Math.abs(dy) >= 0.25f;
            boolean finalSegment = ended;
            if (!hasMovement && !finalSegment) return;

            float n1x = f1x + dx;
            float n1y = f1y + dy;
            float n2x = f2x + dx;
            float n2y = f2y + dy;

            if (!hasMovement) {
                n1x += 0.01f;
                if (pointerCount == 2) n2x += 0.01f;
            }

            Path p1 = new Path();
            p1.moveTo(f1x, f1y);
            p1.lineTo(n1x, n1y);
            GestureDescription.StrokeDescription next1 = stroke1.continueStroke(
                    p1, 0, DRAG_SEGMENT_MS, !finalSegment);

            GestureDescription.Builder builder = new GestureDescription.Builder();
            builder.setDisplayId(targetDisplay);
            builder.addStroke(next1);

            GestureDescription.StrokeDescription next2 = null;
            if (pointerCount == 2) {
                Path p2 = new Path();
                p2.moveTo(f2x, f2y);
                p2.lineTo(n2x, n2y);
                next2 = stroke2.continueStroke(p2, 0, DRAG_SEGMENT_MS, !finalSegment);
                builder.addStroke(next2);
            }

            stroke1 = next1;
            stroke2 = next2;
            f1x = n1x;
            f1y = n1y;
            f2x = n2x;
            f2y = n2y;
            dispatchedMouseX = desiredMouseX;
            dispatchedMouseY = desiredMouseY;
            dispatching = true;

            boolean accepted = dispatchGesture(builder.build(), callback, null);
            if (!accepted) {
                dispatching = false;
                cancelled = true;
            }
        }

        final GestureResultCallback callback = new GestureResultCallback() {
            @Override
            public void onCompleted(GestureDescription gestureDescription) {
                dispatching = false;
                if (!ended) pump();
            }

            @Override
            public void onCancelled(GestureDescription gestureDescription) {
                dispatching = false;
                cancelled = true;
            }
        };
    }

    private static class PointContext {
        boolean uiEvidence;
        boolean scrollable;
        boolean surfaceEvidence;
        boolean secondaryWindow;
        boolean horizontalBottomStrip;
        final Rect horizontalBounds = new Rect();

        boolean isUi() {
            return scrollable || secondaryWindow || uiEvidence || horizontalBottomStrip;
        }
    }

    private int dp(float value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private static float distance(float x1, float y1, float x2, float y2) {
        float dx = x2 - x1;
        float dy = y2 - y1;
        return (float) Math.sqrt(dx * dx + dy * dy);
    }

    private static long area(Rect r) {
        if (r == null) return Long.MAX_VALUE;
        return (long) Math.max(0, r.width()) * Math.max(0, r.height());
    }

    private static float clamp(float value, float min, float max) {
        if (max < min) return min;
        return Math.max(min, Math.min(max, value));
    }
}
