from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.10 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# v1.10 fixes the architectural defect in v1.9 floating mode: v1.9 only shrank
# a child view inside a normal IME window. v1.10 makes the collapsed island an
# overlay-like IME surface: it does not resize/pan the target app and only the
# island itself is touchable; transparent space passes touches through.
replace_once(
    '    private LinearLayout root;\n',
    '    private FrameLayout inputShell;\n    private LinearLayout root;\n',
    'input shell field',
)

replace_once(
'''    @Override public View onCreateInputView() {
        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(3), isLandscape() ? dp(1) : dp(2), dp(3), isLandscape() ? dp(1) : dp(3));
        root.setBackgroundColor(BG);
''',
'''    @Override public View onCreateInputView() {
        inputShell = new FrameLayout(this);
        inputShell.setBackgroundColor(Color.TRANSPARENT);
        inputShell.setClipChildren(false);
        inputShell.setClipToPadding(false);

        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(3), isLandscape() ? dp(1) : dp(2), dp(3), isLandscape() ? dp(1) : dp(3));
        root.setBackgroundColor(BG);
        FrameLayout.LayoutParams rootLp = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT,
                Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        inputShell.addView(root, rootLp);
''',
    'wrap IME contents in transparent shell',
)

replace_once(
'''        auth = new WebView(this);
        auth.setAlpha(0.01f);
        root.addView(auth, new LinearLayout.LayoutParams(1, 1));
        configureWebView();
        auth.loadUrl(START_URL);

        render();
        updateMicUi();
        return root;
    }
''',
'''        auth = new WebView(this);
        auth.setAlpha(0.01f);
        FrameLayout.LayoutParams authLp = new FrameLayout.LayoutParams(1, 1, Gravity.TOP | Gravity.START);
        inputShell.addView(auth, authLp);
        configureWebView();
        auth.loadUrl(START_URL);

        render();
        updateMicUi();
        main.post(() -> applyImeWindowMode(collapsed));
        return inputShell;
    }
''',
    'return transparent shell and keep auth outside island',
)

replace_once(
'''    private void setCollapsed(boolean value) {
        collapsed = value;
        if (full != null) full.setVisibility(value ? View.GONE : View.VISIBLE);
        if (compact != null) compact.setVisibility(value ? View.VISIBLE : View.GONE);
        if (root != null) {
            root.setBackgroundColor(value ? Color.TRANSPARENT : BG);
            root.setPadding(value ? 0 : dp(3), value ? 0 : (isLandscape() ? dp(1) : dp(2)), value ? 0 : dp(3), value ? 0 : (isLandscape() ? dp(1) : dp(3)));
            root.requestLayout();
        }
    }
''',
'''    private void setCollapsed(boolean value) {
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
''',
    'true floating window/insets behavior',
)

# Version bump is part of the patch so the canonical baseline remains reproducible.
if 'versionCode 19' not in g or "versionName '1.9'" not in g:
    raise SystemExit('v1.10 patch: expected v1.9 version markers missing')
g = g.replace('versionCode 19', 'versionCode 20', 1)
g = g.replace("versionName '1.9'", "versionName '1.10'", 1)

# Guardrails: the validated speech transport stays untouched and floating mode
# must now be implemented at the IME insets/window layer, not just as a small child.
required = [
    'enable_endpoint_detection",false',
    'language_hints_strict",true',
    'TOUCHABLE_INSETS_REGION',
    'outInsets.contentTopInsets = Math.max(0, windowHeight);',
    'root.getLocationInWindow(loc);',
    'lp.bottomMargin = dp(24);',
    'return false;',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.10 patch: required invariant missing: {needle}')
if 'MAX_CAPTURE_MS' in s:
    raise SystemExit('v1.10 patch: one-minute limit unexpectedly returned')
if 'Floating mode: next build' in s:
    raise SystemExit('v1.10 patch: old floating placeholder returned')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.10 true floating IME overlay patch')
