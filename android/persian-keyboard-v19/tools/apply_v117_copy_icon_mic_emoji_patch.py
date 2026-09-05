from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.17 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# Keep the v1.16 Copy behavior, but present it as an icon like the neighboring
# clipboard/Paste control rather than spelling out "Copy" in the toolbar.
replace_once(
    '        Button copy = toolbarButton("Copy", v -> copyCurrentText());\n',
    '        Button copy = toolbarButton("⧉", v -> copyCurrentText());\n',
    'Copy text label -> Copy icon',
)

# Use the same microphone emoji in idle and active states. Active state still
# changes color/background and appends the FA/EN badge, so only the emoji itself
# stays visually stable as requested.
replace_once(
    '        mic = toolbarButton("🎤", v -> toggleVoice());\n',
    '        mic = toolbarButton("🎙", v -> toggleVoice());\n',
    'main microphone initial emoji',
)
replace_once(
    '        compactMic = smallButton("🎤 " + badge(), v -> toggleVoice());\n',
    '        compactMic = smallButton("🎙 " + badge(), v -> toggleVoice());\n',
    'compact microphone initial emoji',
)
replace_once(
    '        String label=running?"🎙 "+badge():"🎤";\n',
    '        String label=running?"🎙 "+badge():"🎙";\n',
    'main microphone stable emoji',
)
replace_once(
    '            compactMic.setText((running?"🎙 ":"🎤 ")+badge());\n',
    '            compactMic.setText("🎙 "+badge());\n',
    'compact microphone stable emoji',
)

if 'versionCode 26' not in g or "versionName '1.16'" not in g:
    raise SystemExit('v1.17 patch: expected v1.16 version markers missing')
g = g.replace('versionCode 26', 'versionCode 27', 1)
g = g.replace("versionName '1.16'", "versionName '1.17'", 1)

required = [
    'Button copy = toolbarButton("⧉", v -> copyCurrentText());',
    'copy.setContentDescription("Copy selected text or entire field");',
    'private void copyCurrentText(){',
    'mic = toolbarButton("🎙", v -> toggleVoice());',
    'compactMic = smallButton("🎙 " + badge(), v -> toggleVoice());',
    'String label=running?"🎙 "+badge():"🎙";',
    'compactMic.setText("🎙 "+badge());',
    'Button clearField = toolbarButton("×", v -> clearCurrentTextField());',
    'private void clearCurrentTextField(){',
    'int desired = Math.round(v112Width * 0.70f);',
    'moveFloatingKeyboard(dragStartLeft + dx, dragStartTop + dy);',
    'hasComposingTail=false;\n        updateMicUi(); setStatus(readyText());',
    'enable_endpoint_detection",false',
    'language_hints_strict",true',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.17 patch: required invariant missing: {needle}')

for forbidden in [
    'Button copy = toolbarButton("Copy", v -> copyCurrentText());',
    'mic = toolbarButton("🎤", v -> toggleVoice());',
    'compactMic = smallButton("🎤 " + badge(), v -> toggleVoice());',
    'String label=running?"🎙 "+badge():"🎤";',
    'compactMic.setText((running?"🎙 ":"🎤 ")+badge());',
    'toolbarButton("G⇄"',
    'Translate: next build',
    'toolbarButton("G", v -> switchToGboard())',
    'private void switchToGboard(){',
    'setCollapsed(false); updateMicUi(); setStatus(readyText());',
    'MAX_CAPTURE_MS',
    'Floating mode: next build',
]:
    if forbidden in s:
        raise SystemExit(f'v1.17 patch: forbidden old behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.17 Copy-icon and stable-mic-emoji patch')
