from pathlib import Path

p = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
s = p.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.9 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# v1.9 is intentionally a UI-only patch layered on top of the validated v1.8 speech path.
replace_once(
    'import android.content.Context;\n',
    'import android.content.Context;\nimport android.content.res.Configuration;\n',
    'Configuration import',
)
replace_once(
    'import android.widget.Button;\n',
    'import android.widget.Button;\nimport android.widget.FrameLayout;\n',
    'FrameLayout import',
)

replace_once(
    '        root.setPadding(dp(3), dp(2), dp(3), dp(3));\n',
    '        root.setPadding(dp(3), isLandscape() ? dp(1) : dp(2), dp(3), isLandscape() ? dp(1) : dp(3));\n',
    'orientation-aware root padding',
)

replace_once(
'''        buildToolbar();
        status = new TextView(this);
        status.setText(pageReady ? readyText() : "Loading session…");
        status.setTextColor(0xFF6D7078);
        status.setTextSize(9.5f);
        status.setGravity(Gravity.CENTER);
        full.addView(status, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(14)));

''',
'''        buildToolbar();

''',
    'remove separate status row',
)

replace_once(
'''    private void buildToolbar() {
        LinearLayout bar = new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setGravity(Gravity.CENTER_VERTICAL);
        bar.setPadding(dp(3), 0, dp(3), dp(1));

        mic = toolbarButton("🎤", v -> toggleVoice());
        bar.addView(mic, toolbarLp(1f));
        collapse = toolbarButton("⇊", v -> setCollapsed(true));
        collapse.setVisibility(View.INVISIBLE);
        bar.addView(collapse, toolbarLp(0.68f));
        bar.addView(toolbarButton("G⇄", v -> { stopVoiceForManualInput(); setStatus("Translate: next build"); }), toolbarLp(0.85f));
        Button clip = toolbarButton("▣", v -> { stopVoiceForManualInput(); pasteClipboard(); });
        clip.setContentDescription("Clipboard");
        bar.addView(clip, toolbarLp(0.72f));
        Button floating = toolbarButton("▱", v -> { stopVoiceForManualInput(); setStatus("Floating mode: next build"); });
        floating.setContentDescription("Floating mode");
        bar.addView(floating, toolbarLp(0.72f));
        Button gboard = toolbarButton("G", v -> switchToGboard());
        gboard.setContentDescription("Switch to Gboard");
        bar.addView(gboard, toolbarLp(0.72f));
        full.addView(bar, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(34)));
    }
''',
'''    private void buildToolbar() {
        boolean landscape = isLandscape();
        int barHeight = landscape ? 32 : 50;

        LinearLayout bar = new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setGravity(Gravity.CENTER_VERTICAL);
        bar.setPadding(dp(3), 0, dp(3), 0);

        LinearLayout left = new LinearLayout(this);
        left.setOrientation(LinearLayout.HORIZONTAL);
        left.setGravity(Gravity.CENTER_VERTICAL);
        Button translate = toolbarButton("G⇄", v -> { stopVoiceForManualInput(); setStatus("Translate: next build"); });
        translate.setContentDescription("Translate");
        left.addView(translate, toolbarLp(1f));
        Button clip = toolbarButton("▣", v -> { stopVoiceForManualInput(); pasteClipboard(); });
        clip.setContentDescription("Clipboard");
        left.addView(clip, toolbarLp(1f));
        bar.addView(left, new LinearLayout.LayoutParams(0, dp(barHeight), 1f));

        FrameLayout center = new FrameLayout(this);
        LinearLayout.LayoutParams centerLp = new LinearLayout.LayoutParams(dp(124), dp(barHeight));
        centerLp.setMargins(dp(3), 0, dp(3), 0);

        mic = toolbarButton("🎤", v -> toggleVoice());
        mic.setTextSize(landscape ? 18f : 22f);
        mic.setBackground(round(KEY, dp(landscape ? 12 : 16)));
        center.addView(mic, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        status = new TextView(this);
        status.setText(pageReady ? readyText() : "Loading session…");
        status.setTextColor(0xFF6D7078);
        status.setTextSize(landscape ? 7.5f : 9f);
        status.setGravity(Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        status.setPadding(dp(2), 0, dp(2), landscape ? dp(1) : dp(2));
        status.setClickable(false);
        status.setFocusable(false);
        center.addView(status, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        bar.addView(center, centerLp);

        LinearLayout right = new LinearLayout(this);
        right.setOrientation(LinearLayout.HORIZONTAL);
        right.setGravity(Gravity.CENTER_VERTICAL);
        Button floating = toolbarButton("▱", v -> setCollapsed(true));
        floating.setContentDescription("Floating mode");
        right.addView(floating, toolbarLp(1f));
        Button gboard = toolbarButton("G", v -> switchToGboard());
        gboard.setContentDescription("Switch to Gboard");
        right.addView(gboard, toolbarLp(1f));
        bar.addView(right, new LinearLayout.LayoutParams(0, dp(barHeight), 1f));

        full.addView(bar, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(barHeight)));
    }
''',
    'centered microphone toolbar',
)

replace_once(
'''    private void buildCompact() {
        compact = new LinearLayout(this);
        compact.setOrientation(LinearLayout.HORIZONTAL);
        compact.setGravity(Gravity.CENTER_VERTICAL);
        compact.setPadding(dp(7), dp(3), dp(7), dp(3));
        compact.setVisibility(View.GONE);

        compactMic = smallButton("🎙 " + badge(), v -> toggleVoice());
        compact.addView(compactMic, new LinearLayout.LayoutParams(dp(78), dp(42)));
        Button stop = smallButton("■", v -> requestStop());
        LinearLayout.LayoutParams sp = new LinearLayout.LayoutParams(dp(46), dp(42));
        sp.setMarginStart(dp(4));
        compact.addView(stop, sp);
        compactStatus = new TextView(this);
        compactStatus.setText(listeningText());
        compactStatus.setTextSize(12f);
        compactStatus.setTextColor(TEXT);
        compactStatus.setGravity(Gravity.CENTER);
        compact.addView(compactStatus, new LinearLayout.LayoutParams(0, dp(42), 1f));
        Button restore = smallButton("⌨", v -> setCollapsed(false));
        compact.addView(restore, new LinearLayout.LayoutParams(dp(52), dp(42)));
        root.addView(compact, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(48)));
    }
''',
'''    private void buildCompact() {
        compact = new LinearLayout(this);
        compact.setOrientation(LinearLayout.HORIZONTAL);
        compact.setGravity(Gravity.CENTER);
        compact.setPadding(dp(4), dp(4), dp(4), dp(4));
        compact.setBackground(round(BG, dp(25)));
        compact.setElevation(dp(3));
        compact.setVisibility(View.GONE);

        compactMic = smallButton("🎤 " + badge(), v -> toggleVoice());
        compactMic.setTextSize(16f);
        compact.addView(compactMic, new LinearLayout.LayoutParams(dp(94), dp(42)));

        Button restore = smallButton("⌨", v -> setCollapsed(false));
        restore.setContentDescription("Restore full keyboard");
        LinearLayout.LayoutParams restoreLp = new LinearLayout.LayoutParams(dp(42), dp(42));
        restoreLp.setMarginStart(dp(4));
        compact.addView(restore, restoreLp);

        LinearLayout.LayoutParams compactLp = new LinearLayout.LayoutParams(dp(148), dp(50));
        compactLp.gravity = Gravity.CENTER_HORIZONTAL;
        compactLp.setMargins(0, dp(1), 0, dp(1));
        root.addView(compact, compactLp);
    }
''',
    'fixed-size floating island',
)

replace_once(
'''    private LinearLayout.LayoutParams toolbarLp(float weight) {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(32), weight);
        lp.setMargins(dp(1), 0, dp(1), 0);
        return lp;
    }
''',
'''    private LinearLayout.LayoutParams toolbarLp(float weight) {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(isLandscape() ? 30 : 42), weight);
        lp.setMargins(dp(1), 0, dp(1), 0);
        return lp;
    }
''',
    'orientation-aware toolbar buttons',
)

replace_once(
'''    private void setCollapsed(boolean value) {
        if (value && !running) return;
        collapsed = value;
        if (full != null) full.setVisibility(value ? View.GONE : View.VISIBLE);
        if (compact != null) compact.setVisibility(value ? View.VISIBLE : View.GONE);
        if (root != null) root.requestLayout();
    }
''',
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
    'functional floating toggle',
)

replace_once(
'''    private LinearLayout newKeyRow() {
        LinearLayout r = new LinearLayout(this); r.setOrientation(LinearLayout.HORIZONTAL); r.setGravity(Gravity.CENTER);
        r.setPadding(dp(1),0,dp(1),0); r.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(38)));
        return r;
    }

    private void spacer(LinearLayout r, float weight) { r.addView(new View(this), new LinearLayout.LayoutParams(0, dp(35), weight)); }
    private LinearLayout.LayoutParams keyLp(float weight) {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(35), weight); lp.setMargins(dp(2),dp(1),dp(2),dp(1)); return lp;
    }
''',
'''    private boolean isLandscape() {
        return getResources().getConfiguration().orientation == Configuration.ORIENTATION_LANDSCAPE;
    }

    private int rowHeightPx() { return dp(isLandscape() ? 27 : 38); }
    private int keyHeightPx() { return dp(isLandscape() ? 24 : 35); }

    private LinearLayout newKeyRow() {
        LinearLayout r = new LinearLayout(this); r.setOrientation(LinearLayout.HORIZONTAL); r.setGravity(Gravity.CENTER);
        r.setPadding(dp(1),0,dp(1),0); r.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, rowHeightPx()));
        return r;
    }

    private void spacer(LinearLayout r, float weight) { r.addView(new View(this), new LinearLayout.LayoutParams(0, keyHeightPx(), weight)); }
    private LinearLayout.LayoutParams keyLp(float weight) {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, keyHeightPx(), weight); lp.setMargins(dp(2),dp(1),dp(2),dp(1)); return lp;
    }
''',
    'compact landscape row metrics',
)

replace_once(
'''    private Button baseKey(String label, boolean action) {
        Button b=new Button(this); b.setText(label); b.setAllCaps(false); b.setTextColor(TEXT);
        b.setTextSize(persian && containsPersian(label) ? 18f : 17f); b.setGravity(Gravity.CENTER); b.setPadding(0,0,0,0);
        b.setMinWidth(0); b.setMinimumWidth(0); b.setMinHeight(0); b.setMinimumHeight(0);
        b.setTypeface(Typeface.create("sans-serif",Typeface.NORMAL)); b.setBackground(round(action?ACTION:KEY,dp(8))); return b;
    }
''',
'''    private Button baseKey(String label, boolean action) {
        Button b=new Button(this); b.setText(label); b.setAllCaps(false); b.setTextColor(TEXT);
        float keyTextSize = persian && containsPersian(label) ? (isLandscape() ? 15f : 18f) : (isLandscape() ? 14f : 17f);
        b.setTextSize(keyTextSize); b.setGravity(Gravity.CENTER); b.setPadding(0,0,0,0);
        b.setMinWidth(0); b.setMinimumWidth(0); b.setMinHeight(0); b.setMinimumHeight(0);
        b.setTypeface(Typeface.create("sans-serif",Typeface.NORMAL)); b.setBackground(round(action?ACTION:KEY,dp(8))); return b;
    }
''',
    'compact landscape key text',
)

# Floating mode is a persistent UI mode. Speech completion/recovery must not expand it automatically.
s = s.replace('main.post(()->{setCollapsed(false);updateMicUi();setStatus("Voice cancelled — editor changed");});',
              'main.post(()->{updateMicUi();setStatus("Voice cancelled — editor changed");});')
s = s.replace('main.post(()->{setCollapsed(false);updateMicUi();setStatus(m);});',
              'main.post(()->{updateMicUi();setStatus(m);});')
if 'main.post(()->{setCollapsed(false);updateMicUi();setStatus(m);});' in s:
    raise SystemExit('v1.9 patch: speech completion still forces full keyboard')

replace_once(
'''    private void updateMicUi(){
        String label=running?"🎙 "+badge():"🎤";if(mic!=null){mic.setText(label);mic.setTextColor(running?Color.WHITE:TEXT);mic.setBackground(round(running?MIC_ACTIVE:0x00FFFFFF,dp(15)));}if(collapse!=null)collapse.setVisibility(running?View.VISIBLE:View.INVISIBLE);if(compactMic!=null)compactMic.setText("🎙 "+badge());if(compactStatus!=null)compactStatus.setText(listeningText());
    }
''',
'''    private void updateMicUi(){
        String label=running?"🎙 "+badge():"🎤";
        if(mic!=null){
            mic.setText(label);
            mic.setTextColor(running?Color.WHITE:TEXT);
            mic.setBackground(round(running?MIC_ACTIVE:KEY,dp(isLandscape()?12:16)));
        }
        if(status!=null)status.setTextColor(running?0xFFE9EDF5:0xFF6D7078);
        if(compactMic!=null){
            compactMic.setText((running?"🎙 ":"🎤 ")+badge());
            compactMic.setTextColor(running?Color.WHITE:TEXT);
            compactMic.setBackground(round(running?MIC_ACTIVE:KEY,dp(18)));
        }
        if(compactStatus!=null)compactStatus.setText(listeningText());
    }
''',
    'microphone state styling',
)

# Guardrails: v1.9 must not alter the validated realtime speech transport/configuration.
if 'Floating mode: next build' in s:
    raise SystemExit('v1.9 patch: floating placeholder still present')
if 'enable_endpoint_detection",false' not in s:
    raise SystemExit('v1.9 patch: v1.8 manual endpointing missing')
if 'language_hints_strict",true' not in s:
    raise SystemExit('v1.9 patch: strict language hint missing')
if 'MAX_CAPTURE_MS' in s:
    raise SystemExit('v1.9 patch: one-minute limit unexpectedly returned')
if 'new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(14))' in s:
    raise SystemExit('v1.9 patch: old separate status row still present')

p.write_text(s)
print('Applied Persian keyboard v1.9 centered-mic / compact-landscape / floating-island patch')
