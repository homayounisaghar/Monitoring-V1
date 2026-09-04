from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.11 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# v1.11 changes the meaning of the v1.10 floating toggle. Instead of collapsing
# to a microphone-only island, floating mode keeps the complete keyboard visible
# and lets the user drag it around inside a transparent full-screen IME surface.
replace_once(
    '    private Button compactMic;\n',
    '''    private Button compactMic;
    private Button floatingButton;
    private float dragDownRawX;
    private float dragDownRawY;
    private int dragStartLeft;
    private int dragStartTop;
    private int floatingLeft = -1;
    private int floatingTop = -1;
    private boolean dragMoved;
''',
    'movable floating fields',
)

replace_once(
'''        Button floating = toolbarButton("▱", v -> setCollapsed(true));
        floating.setContentDescription("Floating mode");
        right.addView(floating, toolbarLp(1f));
''',
'''        floatingButton = toolbarButton("▱", v -> setCollapsed(!collapsed));
        floatingButton.setContentDescription("Floating keyboard");
        floatingButton.setOnTouchListener(this::handleFloatingHandleTouch);
        right.addView(floatingButton, toolbarLp(1f));
''',
    'floating button becomes drag handle',
)

old_window_block = '''    private void setCollapsed(boolean value) {
        collapsed = value;
        if (full != null) full.setVisibility(value ? View.GONE : View.VISIBLE);
        if (compact != null) compact.setVisibility(value ? View.VISIBLE : View.GONE);
        if (root != null) {
            root.setBackgroundColor(value ? Color.TRANSPARENT : BG);
            root.setPadding(value ? 0 : dp(3), value ? 0 : (isLandscape() ? dp(1) : dp(2)), value ? 0 : dp(3), value ? 0 : (isLandscape() ? dp(1) : dp(3)));
        }
        applyImeWindowMode(value);
    }

    private void applyImeWindowMode(boolean floating) {
        if (root != null && root.getLayoutParams() instanceof FrameLayout.LayoutParams) {
            FrameLayout.LayoutParams lp = (FrameLayout.LayoutParams) root.getLayoutParams();
            if (floating) {
                lp.width = dp(148);
                lp.height = dp(50);
                lp.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
                lp.bottomMargin = dp(24);
            } else {
                lp.width = ViewGroup.LayoutParams.MATCH_PARENT;
                lp.height = ViewGroup.LayoutParams.WRAP_CONTENT;
                lp.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
                lp.bottomMargin = 0;
            }
            root.setLayoutParams(lp);
            root.requestLayout();
        }
        try {
            android.app.Dialog dialog = getWindow();
            android.view.Window win = dialog == null ? null : dialog.getWindow();
            if (win != null) {
                win.setBackgroundDrawableResource(android.R.color.transparent);
                win.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            }
        } catch (Exception ignored) {}
        if (inputShell != null) inputShell.requestLayout();
    }

    @Override public boolean onEvaluateFullscreenMode() {
        return false;
    }

    @Override public void onConfigureWindow(android.view.Window win, boolean isFullscreen, boolean isCandidatesOnly) {
        super.onConfigureWindow(win, false, isCandidatesOnly);
        if (win != null) {
            win.setBackgroundDrawableResource(android.R.color.transparent);
            win.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        }
    }

    @Override public void onComputeInsets(Insets outInsets) {
        if (!collapsed) {
            super.onComputeInsets(outInsets);
            return;
        }

        int windowHeight = 0;
        try {
            android.app.Dialog dialog = getWindow();
            android.view.Window win = dialog == null ? null : dialog.getWindow();
            if (win != null && win.getDecorView() != null) windowHeight = win.getDecorView().getHeight();
        } catch (Exception ignored) {}
        if (windowHeight <= 0 && inputShell != null) windowHeight = inputShell.getHeight();

        // No part of the transparent IME strip should resize/pan the target app.
        outInsets.contentTopInsets = Math.max(0, windowHeight);
        outInsets.visibleTopInsets = Math.max(0, windowHeight);
        outInsets.touchableInsets = Insets.TOUCHABLE_INSETS_REGION;
        outInsets.touchableRegion.setEmpty();

        if (root != null && root.getWidth() > 0 && root.getHeight() > 0) {
            int[] loc = new int[2];
            root.getLocationInWindow(loc);
            outInsets.touchableRegion.set(loc[0], loc[1], loc[0] + root.getWidth(), loc[1] + root.getHeight());
        }
    }
'''

new_window_block = '''    private void setCollapsed(boolean value) {
        collapsed = value;

        // Floating mode keeps the entire keyboard, not the old compact island.
        if (full != null) full.setVisibility(View.VISIBLE);
        if (compact != null) compact.setVisibility(View.GONE);
        if (root != null) {
            root.setBackground(round(BG, dp(value ? 14 : 0)));
            root.setPadding(dp(3), isLandscape() ? dp(1) : dp(2), dp(3), isLandscape() ? dp(1) : dp(3));
            root.setElevation(value ? dp(8) : 0f);
        }
        if (floatingButton != null) {
            floatingButton.setText(value ? "✥" : "▱");
            floatingButton.setContentDescription(value ? "Drag floating keyboard; tap to dock" : "Float keyboard");
        }
        applyImeWindowMode(value);
    }

    private int floatingKeyboardWidth() {
        int shellWidth = inputShell != null && inputShell.getWidth() > 0
                ? inputShell.getWidth() : getResources().getDisplayMetrics().widthPixels;
        float factor = isLandscape() ? 0.78f : 0.88f;
        int desired = Math.round(shellWidth * factor);
        int minWidth = dp(isLandscape() ? 420 : 300);
        int maxWidth = dp(isLandscape() ? 620 : 460);
        desired = Math.max(minWidth, Math.min(desired, maxWidth));
        return Math.max(dp(240), Math.min(desired, Math.max(dp(240), shellWidth - dp(20))));
    }

    private void applyImeWindowMode(boolean floating) {
        if (root != null && root.getLayoutParams() instanceof FrameLayout.LayoutParams) {
            FrameLayout.LayoutParams lp = (FrameLayout.LayoutParams) root.getLayoutParams();
            if (floating) {
                lp.width = floatingKeyboardWidth();
                lp.height = ViewGroup.LayoutParams.WRAP_CONTENT;
                lp.gravity = Gravity.TOP | Gravity.START;
                lp.bottomMargin = 0;
                lp.leftMargin = Math.max(0, floatingLeft);
                lp.topMargin = Math.max(0, floatingTop);
            } else {
                lp.width = ViewGroup.LayoutParams.MATCH_PARENT;
                lp.height = ViewGroup.LayoutParams.WRAP_CONTENT;
                lp.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
                lp.leftMargin = 0;
                lp.topMargin = 0;
                lp.bottomMargin = 0;
            }
            root.setLayoutParams(lp);
            root.requestLayout();
        }
        try {
            android.app.Dialog dialog = getWindow();
            android.view.Window win = dialog == null ? null : dialog.getWindow();
            if (win != null) {
                win.setBackgroundDrawableResource(android.R.color.transparent);
                win.setLayout(ViewGroup.LayoutParams.MATCH_PARENT,
                        floating ? ViewGroup.LayoutParams.MATCH_PARENT : ViewGroup.LayoutParams.WRAP_CONTENT);
            }
        } catch (Exception ignored) {}
        if (inputShell != null) {
            inputShell.requestLayout();
            if (floating) inputShell.post(this::ensureFloatingPosition);
        }
    }

    private void ensureFloatingPosition() {
        if (!collapsed || root == null || inputShell == null) return;
        if (!(root.getLayoutParams() instanceof FrameLayout.LayoutParams)) return;
        if (inputShell.getWidth() <= 0 || inputShell.getHeight() <= 0 || root.getWidth() <= 0 || root.getHeight() <= 0) {
            inputShell.postDelayed(this::ensureFloatingPosition, 40L);
            return;
        }

        FrameLayout.LayoutParams lp = (FrameLayout.LayoutParams) root.getLayoutParams();
        int pad = dp(8);
        int maxLeft = Math.max(pad, inputShell.getWidth() - root.getWidth() - pad);
        int maxTop = Math.max(pad, inputShell.getHeight() - root.getHeight() - pad);

        if (floatingLeft < 0 || floatingTop < 0) {
            floatingLeft = Math.max(pad, (inputShell.getWidth() - root.getWidth()) / 2);
            floatingTop = Math.max(pad, inputShell.getHeight() - root.getHeight() - dp(28));
        }
        floatingLeft = Math.max(pad, Math.min(floatingLeft, maxLeft));
        floatingTop = Math.max(pad, Math.min(floatingTop, maxTop));

        lp.gravity = Gravity.TOP | Gravity.START;
        lp.leftMargin = floatingLeft;
        lp.topMargin = floatingTop;
        lp.bottomMargin = 0;
        root.setLayoutParams(lp);
        root.requestLayout();
    }

    private boolean handleFloatingHandleTouch(View v, MotionEvent event) {
        int action = event.getActionMasked();
        if (action == MotionEvent.ACTION_DOWN) {
            dragDownRawX = event.getRawX();
            dragDownRawY = event.getRawY();
            dragMoved = false;
            if (root != null && root.getLayoutParams() instanceof FrameLayout.LayoutParams) {
                FrameLayout.LayoutParams lp = (FrameLayout.LayoutParams) root.getLayoutParams();
                dragStartLeft = lp.leftMargin;
                dragStartTop = lp.topMargin;
            }
            return true;
        }
        if (action == MotionEvent.ACTION_MOVE) {
            if (!collapsed) return true;
            int dx = Math.round(event.getRawX() - dragDownRawX);
            int dy = Math.round(event.getRawY() - dragDownRawY);
            if (!dragMoved && Math.abs(dx) + Math.abs(dy) >= dp(6)) dragMoved = true;
            if (dragMoved) moveFloatingKeyboard(dragStartLeft + dx, dragStartTop + dy);
            return true;
        }
        if (action == MotionEvent.ACTION_UP) {
            if (!dragMoved) v.performClick();
            return true;
        }
        if (action == MotionEvent.ACTION_CANCEL) return true;
        return true;
    }

    private void moveFloatingKeyboard(int requestedLeft, int requestedTop) {
        if (!collapsed || root == null || inputShell == null) return;
        if (!(root.getLayoutParams() instanceof FrameLayout.LayoutParams)) return;
        if (root.getWidth() <= 0 || root.getHeight() <= 0 || inputShell.getWidth() <= 0 || inputShell.getHeight() <= 0) return;

        int pad = dp(8);
        int maxLeft = Math.max(pad, inputShell.getWidth() - root.getWidth() - pad);
        int maxTop = Math.max(pad, inputShell.getHeight() - root.getHeight() - pad);
        floatingLeft = Math.max(pad, Math.min(requestedLeft, maxLeft));
        floatingTop = Math.max(pad, Math.min(requestedTop, maxTop));

        FrameLayout.LayoutParams lp = (FrameLayout.LayoutParams) root.getLayoutParams();
        lp.gravity = Gravity.TOP | Gravity.START;
        lp.leftMargin = floatingLeft;
        lp.topMargin = floatingTop;
        lp.bottomMargin = 0;
        root.setLayoutParams(lp);
        root.requestLayout();
        inputShell.requestLayout();
    }

    @Override public boolean onEvaluateFullscreenMode() {
        return false;
    }

    @Override public void onConfigureWindow(android.view.Window win, boolean isFullscreen, boolean isCandidatesOnly) {
        super.onConfigureWindow(win, false, isCandidatesOnly);
        if (win != null) {
            win.setBackgroundDrawableResource(android.R.color.transparent);
            win.setLayout(ViewGroup.LayoutParams.MATCH_PARENT,
                    collapsed ? ViewGroup.LayoutParams.MATCH_PARENT : ViewGroup.LayoutParams.WRAP_CONTENT);
        }
    }

    @Override public void onComputeInsets(Insets outInsets) {
        if (!collapsed) {
            super.onComputeInsets(outInsets);
            return;
        }

        int windowHeight = 0;
        try {
            android.app.Dialog dialog = getWindow();
            android.view.Window win = dialog == null ? null : dialog.getWindow();
            if (win != null && win.getDecorView() != null) windowHeight = win.getDecorView().getHeight();
        } catch (Exception ignored) {}
        if (windowHeight <= 0 && inputShell != null) windowHeight = inputShell.getHeight();

        // Floating keyboard overlays the app: it reserves no bottom content area.
        outInsets.contentTopInsets = Math.max(0, windowHeight);
        outInsets.visibleTopInsets = Math.max(0, windowHeight);
        outInsets.touchableInsets = Insets.TOUCHABLE_INSETS_REGION;
        outInsets.touchableRegion.setEmpty();

        // Only the keyboard itself captures touch. Everything around it passes through.
        if (root != null && root.getWidth() > 0 && root.getHeight() > 0) {
            int[] loc = new int[2];
            root.getLocationInWindow(loc);
            outInsets.touchableRegion.set(loc[0], loc[1], loc[0] + root.getWidth(), loc[1] + root.getHeight());
        }
    }
'''

replace_once(old_window_block, new_window_block, 'replace compact island with movable full keyboard')

if 'versionCode 20' not in g or "versionName '1.10'" not in g:
    raise SystemExit('v1.11 patch: expected v1.10 version markers missing')
g = g.replace('versionCode 20', 'versionCode 21', 1)
g = g.replace("versionName '1.10'", "versionName '1.11'", 1)

required = [
    'if (full != null) full.setVisibility(View.VISIBLE);',
    'if (compact != null) compact.setVisibility(View.GONE);',
    'floatingButton.setOnTouchListener(this::handleFloatingHandleTouch);',
    'floating ? ViewGroup.LayoutParams.MATCH_PARENT : ViewGroup.LayoutParams.WRAP_CONTENT',
    'moveFloatingKeyboard(dragStartLeft + dx, dragStartTop + dy);',
    'outInsets.touchableInsets = Insets.TOUCHABLE_INSETS_REGION;',
    'root.getLocationInWindow(loc);',
    'enable_endpoint_detection",false',
    'language_hints_strict",true',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.11 patch: required invariant missing: {needle}')

for forbidden in [
    'lp.width = dp(148);',
    'lp.height = dp(50);',
    'if (full != null) full.setVisibility(value ? View.GONE : View.VISIBLE);',
]:
    if forbidden in s:
        raise SystemExit(f'v1.11 patch: old compact floating behavior remains: {forbidden}')

if 'MAX_CAPTURE_MS' in s:
    raise SystemExit('v1.11 patch: one-minute limit unexpectedly returned')
if 'Floating mode: next build' in s:
    raise SystemExit('v1.11 patch: old floating placeholder returned')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.11 movable full-keyboard floating patch')
