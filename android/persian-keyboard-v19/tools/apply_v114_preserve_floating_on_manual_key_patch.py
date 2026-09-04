from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.14 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# v1.8 intentionally stops active voice input before a manual key action, but its
# cleanup also forced setCollapsed(false). After floating mode became a persistent
# full-keyboard mode in v1.11+, that old cleanup side effect docks the keyboard
# whenever the user presses a key while the microphone is active. Preserve the
# current floating/docked presentation while still stopping voice safely.
replace_once(
'''    private void stopVoiceForManualInput(){
        if(!running)return;
        running=false; completed=true; stopRequested=true; awaitingCredential=false; retryAfterPageLoad=false;
        backspaceHeld=false; main.removeCallbacks(backspaceRepeater);
        stopAudioRecord(); clearPending();
        WebSocket ws=webSocket; webSocket=null; if(ws!=null)ws.cancel();
        InputConnection old=boundConnection; boundConnection=null;
        if(old!=null)try{old.finishComposingText();}catch(Exception ignored){}
        synchronized(expectedSelectionUpdates){expectedSelectionUpdates.clear();}
        hasComposingTail=false;
        setCollapsed(false); updateMicUi(); setStatus(readyText());
    }
''',
'''    private void stopVoiceForManualInput(){
        if(!running)return;
        running=false; completed=true; stopRequested=true; awaitingCredential=false; retryAfterPageLoad=false;
        backspaceHeld=false; main.removeCallbacks(backspaceRepeater);
        stopAudioRecord(); clearPending();
        WebSocket ws=webSocket; webSocket=null; if(ws!=null)ws.cancel();
        InputConnection old=boundConnection; boundConnection=null;
        if(old!=null)try{old.finishComposingText();}catch(Exception ignored){}
        synchronized(expectedSelectionUpdates){expectedSelectionUpdates.clear();}
        hasComposingTail=false;
        updateMicUi(); setStatus(readyText());
    }
''',
    'manual voice stop must preserve floating mode',
)

if 'versionCode 23' not in g or "versionName '1.13'" not in g:
    raise SystemExit('v1.14 patch: expected v1.13 version markers missing')
g = g.replace('versionCode 23', 'versionCode 24', 1)
g = g.replace("versionName '1.13'", "versionName '1.14'", 1)

required = [
    'private void stopVoiceForManualInput(){',
    'hasComposingTail=false;\n        updateMicUi(); setStatus(readyText());',
    'int desired = Math.round(v112Width * 0.70f);',
    'moveFloatingKeyboard(dragStartLeft + dx, dragStartTop + dy);',
    'return collapsed || getResources().getConfiguration().orientation == Configuration.ORIENTATION_LANDSCAPE;',
    'enable_endpoint_detection",false',
    'language_hints_strict",true',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.14 patch: required invariant missing: {needle}')

if 'setCollapsed(false); updateMicUi(); setStatus(readyText());' in s:
    raise SystemExit('v1.14 patch: manual key voice stop still docks keyboard')
if 'MAX_CAPTURE_MS' in s:
    raise SystemExit('v1.14 patch: one-minute limit unexpectedly returned')
if 'Floating mode: next build' in s:
    raise SystemExit('v1.14 patch: old floating placeholder returned')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.14 preserve-floating-on-manual-key patch')
