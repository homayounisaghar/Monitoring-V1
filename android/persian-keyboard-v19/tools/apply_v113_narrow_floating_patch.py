from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.13 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


old_width = '''    private int floatingKeyboardWidth() {
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

new_width = '''    private int floatingKeyboardWidth() {
        android.util.DisplayMetrics dm = getResources().getDisplayMetrics();
        int shellWidth = inputShell != null && inputShell.getWidth() > 0
                ? inputShell.getWidth() : dm.widthPixels;

        // v1.13 keeps v1.12's orientation-independent portrait-width baseline,
        // then makes the floating keyboard exactly 30% narrower.
        int shortSide = Math.min(dm.widthPixels, dm.heightPixels);
        int v112Desired = Math.round(shortSide * 0.88f);
        v112Desired = Math.max(dp(300), Math.min(v112Desired, dp(460)));
        int v112Width = Math.max(dp(240), Math.min(v112Desired,
                Math.max(dp(240), shellWidth - dp(20))));
        int desired = Math.round(v112Width * 0.70f);
        return Math.max(dp(160), Math.min(desired,
                Math.max(dp(160), shellWidth - dp(20))));
    }
'''

replace_once(old_width, new_width, 'reduce v1.12 floating width by 30 percent')

if 'versionCode 22' not in g or "versionName '1.12'" not in g:
    raise SystemExit('v1.13 patch: expected v1.12 version markers missing')
g = g.replace('versionCode 22', 'versionCode 23', 1)
g = g.replace("versionName '1.12'", "versionName '1.13'", 1)

required = [
    'int v112Desired = Math.round(shortSide * 0.88f);',
    'int desired = Math.round(v112Width * 0.70f);',
    'return Math.max(dp(160), Math.min(desired,',
    'moveFloatingKeyboard(dragStartLeft + dx, dragStartTop + dy);',
    'inputShell.setMinimumHeight(floating ? screenHeight : 0);',
    'return collapsed || getResources().getConfiguration().orientation == Configuration.ORIENTATION_LANDSCAPE;',
    'enable_endpoint_detection",false',
    'language_hints_strict",true',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.13 patch: required invariant missing: {needle}')

if 'int desired = Math.round(shortSide * 0.88f);' in s:
    raise SystemExit('v1.13 patch: old full v1.12 width calculation remains')
if 'MAX_CAPTURE_MS' in s:
    raise SystemExit('v1.13 patch: one-minute limit unexpectedly returned')
if 'Floating mode: next build' in s:
    raise SystemExit('v1.13 patch: old floating placeholder returned')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.13 30-percent-narrower floating patch')
