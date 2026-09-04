from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.12 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# Floating mode must use the most compact metrics regardless of phone orientation:
# portrait floating width + landscape toolbar/row/key heights.
replace_once(
'''    private boolean isLandscape() {
        return getResources().getConfiguration().orientation == Configuration.ORIENTATION_LANDSCAPE;
    }
''',
'''    private boolean isLandscape() {
        // In floating mode always use the compact landscape metrics, even in portrait.
        return collapsed || getResources().getConfiguration().orientation == Configuration.ORIENTATION_LANDSCAPE;
    }
''',
    'floating uses compact landscape metrics',
)

old_set_collapsed = '''    private void setCollapsed(boolean value) {
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
'''

new_set_collapsed = '''    private void setCollapsed(boolean value) {
        boolean modeChanged = collapsed != value;
        collapsed = value;

        // Toolbar/rows are created with orientation-dependent dimensions. Rebuild them
        // whenever floating changes so portrait floating also receives landscape heights.
        if (modeChanged && full != null) rebuildKeyboardSurface();

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

    private void rebuildKeyboardSurface() {
        if (full == null) return;
        full.removeAllViews();
        buildToolbar();
        rows = new LinearLayout(this);
        rows.setOrientation(LinearLayout.VERTICAL);
        full.addView(rows, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));
        render();
    }
'''

replace_once(old_set_collapsed, new_set_collapsed, 'rebuild keyboard when floating metric mode changes')

old_width = '''    private int floatingKeyboardWidth() {
        int shellWidth = inputShell != null && inputShell.getWidth() > 0
                ? inputShell.getWidth() : getResources().getDisplayMetrics().widthPixels;
        float factor = isLandscape() ? 0.78f : 0.88f;
        int desired = Math.round(shellWidth * factor);
        int minWidth = dp(isLandscape() ? 420 : 300);
        int maxWidth = dp(isLandscape() ? 620 : 460);
        desired = Math.max(minWidth, Math.min(desired, maxWidth));
        return Math.max(dp(240), Math.min(desired, Math.max(dp(240), shellWidth - dp(20))));
    }
'''

new_width = '''    private int floatingKeyboardWidth() {
        android.util.DisplayMetrics dm = getResources().getDisplayMetrics();
        int shellWidth = inputShell != null && inputShell.getWidth() > 0
                ? inputShell.getWidth() : dm.widthPixels;

        // Use the portrait floating width in both orientations: 88% of the display's
        // short side, with the same portrait clamps used by v1.11.
        int shortSide = Math.min(dm.widthPixels, dm.heightPixels);
        int desired = Math.round(shortSide * 0.88f);
        desired = Math.max(dp(300), Math.min(desired, dp(460)));
        return Math.max(dp(240), Math.min(desired, Math.max(dp(240), shellWidth - dp(20))));
    }
'''

replace_once(old_width, new_width, 'orientation-independent portrait floating width')

old_window = '''        try {
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
'''

new_window = '''        int screenHeight = getResources().getDisplayMetrics().heightPixels;
        if (inputShell != null) {
            // Samsung/One UI can keep the IME input frame at keyboard height even when
            // the outer Window requests MATCH_PARENT. Give the returned input view an
            // explicit screen-height layout so there is real Y travel space.
            inputShell.setMinimumHeight(floating ? screenHeight : 0);
            ViewGroup.LayoutParams shellLp = inputShell.getLayoutParams();
            if (shellLp != null) {
                shellLp.height = floating ? screenHeight : ViewGroup.LayoutParams.WRAP_CONTENT;
                inputShell.setLayoutParams(shellLp);
            }
        }
        try {
            android.app.Dialog dialog = getWindow();
            android.view.Window win = dialog == null ? null : dialog.getWindow();
            if (win != null) {
                win.setBackgroundDrawableResource(android.R.color.transparent);
                android.view.WindowManager.LayoutParams attrs = win.getAttributes();
                attrs.width = ViewGroup.LayoutParams.MATCH_PARENT;
                attrs.height = floating ? ViewGroup.LayoutParams.MATCH_PARENT : ViewGroup.LayoutParams.WRAP_CONTENT;
                attrs.gravity = floating ? (Gravity.TOP | Gravity.START) : Gravity.BOTTOM;
                win.setAttributes(attrs);
                win.setLayout(ViewGroup.LayoutParams.MATCH_PARENT,
                        floating ? ViewGroup.LayoutParams.MATCH_PARENT : ViewGroup.LayoutParams.WRAP_CONTENT);
                if (win.getDecorView() != null) win.getDecorView().requestLayout();
            }
        } catch (Exception ignored) {}
        if (inputShell != null) {
            inputShell.requestLayout();
            if (floating) inputShell.post(this::ensureFloatingPosition);
        }
'''

replace_once(old_window, new_window, 'force full-height floating IME shell for vertical drag')

old_configure = '''    @Override public void onConfigureWindow(android.view.Window win, boolean isFullscreen, boolean isCandidatesOnly) {
        super.onConfigureWindow(win, false, isCandidatesOnly);
        if (win != null) {
            win.setBackgroundDrawableResource(android.R.color.transparent);
            win.setLayout(ViewGroup.LayoutParams.MATCH_PARENT,
                    collapsed ? ViewGroup.LayoutParams.MATCH_PARENT : ViewGroup.LayoutParams.WRAP_CONTENT);
        }
    }
'''

new_configure = '''    @Override public void onConfigureWindow(android.view.Window win, boolean isFullscreen, boolean isCandidatesOnly) {
        super.onConfigureWindow(win, false, isCandidatesOnly);
        if (win != null) {
            win.setBackgroundDrawableResource(android.R.color.transparent);
            android.view.WindowManager.LayoutParams attrs = win.getAttributes();
            attrs.width = ViewGroup.LayoutParams.MATCH_PARENT;
            attrs.height = collapsed ? ViewGroup.LayoutParams.MATCH_PARENT : ViewGroup.LayoutParams.WRAP_CONTENT;
            attrs.gravity = collapsed ? (Gravity.TOP | Gravity.START) : Gravity.BOTTOM;
            win.setAttributes(attrs);
            win.setLayout(ViewGroup.LayoutParams.MATCH_PARENT,
                    collapsed ? ViewGroup.LayoutParams.MATCH_PARENT : ViewGroup.LayoutParams.WRAP_CONTENT);
        }
    }
'''

replace_once(old_configure, new_configure, 'configure floating window top/full-height')

if 'versionCode 21' not in g or "versionName '1.11'" not in g:
    raise SystemExit('v1.12 patch: expected v1.11 version markers missing')
g = g.replace('versionCode 21', 'versionCode 22', 1)
g = g.replace("versionName '1.11'", "versionName '1.12'", 1)

required = [
    'return collapsed || getResources().getConfiguration().orientation == Configuration.ORIENTATION_LANDSCAPE;',
    'rebuildKeyboardSurface();',
    'int shortSide = Math.min(dm.widthPixels, dm.heightPixels);',
    'int desired = Math.round(shortSide * 0.88f);',
    'inputShell.setMinimumHeight(floating ? screenHeight : 0);',
    'shellLp.height = floating ? screenHeight : ViewGroup.LayoutParams.WRAP_CONTENT;',
    'attrs.gravity = floating ? (Gravity.TOP | Gravity.START) : Gravity.BOTTOM;',
    'moveFloatingKeyboard(dragStartLeft + dx, dragStartTop + dy);',
    'outInsets.touchableInsets = Insets.TOUCHABLE_INSETS_REGION;',
    'enable_endpoint_detection",false',
    'language_hints_strict",true',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.12 patch: required invariant missing: {needle}')

for forbidden in [
    'float factor = isLandscape() ? 0.78f : 0.88f;',
    'int minWidth = dp(isLandscape() ? 420 : 300);',
    'int maxWidth = dp(isLandscape() ? 620 : 460);',
]:
    if forbidden in s:
        raise SystemExit(f'v1.12 patch: orientation-dependent floating size remains: {forbidden}')

if 'MAX_CAPTURE_MS' in s:
    raise SystemExit('v1.12 patch: one-minute limit unexpectedly returned')
if 'Floating mode: next build' in s:
    raise SystemExit('v1.12 patch: old floating placeholder returned')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.12 vertical-drag / compact-orientation-independent floating patch')
