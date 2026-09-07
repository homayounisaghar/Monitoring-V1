from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.29 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# v1.28 device diagnostics identified the remaining involuntary stop path as
# onUpdateSelection(): "Voice stopped — selection changed". Keep the proven
# v1.26 live-partial publisher intact and make ownership of its own selection
# callbacks explicit. Two races are covered:
# 1) an editor may call onUpdateSelection synchronously/re-entrantly from
#    deleteSurroundingText()/commitText(), before rememberProgrammaticSelection()
#    could previously record the new cursor;
# 2) an editor may emit the same final cursor callback more than once, while the
#    old one-shot expectedSelectionUpdates queue consumed only the first copy.
# A genuine user caret move still differs from the last IME-owned cursor and is
# checked against the editor's current selection before stopping voice.

replace_once(
'''    private final ArrayDeque<Long> expectedSelectionUpdates = new ArrayDeque<>();
''',
'''    private final ArrayDeque<Long> expectedSelectionUpdates = new ArrayDeque<>();
    private int programmaticSelectionEditDepth;
    private long lastProgrammaticSelectionKey;
    private boolean hasLastProgrammaticSelection;
''',
    'selection ownership state',
)

replace_once(
'''            long key=selectionKey(start,end);
            synchronized(expectedSelectionUpdates){
                while(expectedSelectionUpdates.size()>=10)expectedSelectionUpdates.removeFirst();
                expectedSelectionUpdates.addLast(key);
            }
''',
'''            long key=selectionKey(start,end);
            synchronized(expectedSelectionUpdates){
                lastProgrammaticSelectionKey=key;
                hasLastProgrammaticSelection=true;
                while(expectedSelectionUpdates.size()>=10)expectedSelectionUpdates.removeFirst();
                expectedSelectionUpdates.addLast(key);
            }
''',
    'persist latest programmatic cursor',
)

replace_once(
'''    private boolean consumeExpectedSelection(int start,int end){
        long key=selectionKey(start,end);
        synchronized(expectedSelectionUpdates){return expectedSelectionUpdates.removeFirstOccurrence(key);}
    }
''',
'''    private boolean consumeExpectedSelection(int start,int end){
        long key=selectionKey(start,end);
        synchronized(expectedSelectionUpdates){return expectedSelectionUpdates.removeFirstOccurrence(key);}
    }
    private boolean matchesLastProgrammaticSelection(int start,int end){
        long key=selectionKey(start,end);
        synchronized(expectedSelectionUpdates){return hasLastProgrammaticSelection&&lastProgrammaticSelectionKey==key;}
    }
''',
    'persistent programmatic selection matcher',
)

replace_once(
'''        if(!running)return;
        if(oldSelStart==newSelStart&&oldSelEnd==newSelEnd)return;
        // Multiple selection callbacks can be emitted for one batch edit. By the
        // time the IME main thread receives an intermediate callback, the editor
        // may already be at the final programmatic cursor. Ignore only callbacks
        // that no longer describe the editor's current selection; a real user tap
        // still matches the current editor snapshot and keeps the original stop.
        if(!selectionCallbackMatchesEditorNow(newSelStart,newSelEnd))return;
        if(consumeExpectedSelection(newSelStart,newSelEnd))return;
''',
'''        if(!running)return;
        if(oldSelStart==newSelStart&&oldSelEnd==newSelEnd)return;
        // A callback delivered while this same main-thread publication is
        // mutating the editor is necessarily IME-owned; user input cannot
        // interleave inside the current edit operation.
        if(programmaticSelectionEditDepth>0)return;
        // Some browser/contenteditable editors repeat the same final selection
        // callback. Keep the latest IME-owned cursor persistent instead of
        // consuming ownership after only one callback.
        if(matchesLastProgrammaticSelection(newSelStart,newSelEnd))return;
        // Delayed intermediate callbacks are ignored only when they no longer
        // describe the editor's current selection. A real user caret move still
        // matches the current editor snapshot and reaches the stop path below.
        if(!selectionCallbackMatchesEditorNow(newSelStart,newSelEnd))return;
        if(consumeExpectedSelection(newSelStart,newSelEnd))return;
''',
    'selection callback ownership gate',
)

replace_once(
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; livePartialTail=""; sendAfterVoiceStop=false; updateMicUi();
''',
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; livePartialTail=""; programmaticSelectionEditDepth=0; hasLastProgrammaticSelection=false; sendAfterVoiceStop=false; updateMicUi();
''',
    'reset selection ownership on voice start',
)

replace_once(
'''            boolean batch=false;
            try{
''',
'''            boolean batch=false;
            programmaticSelectionEditDepth++;
            try{
''',
    'enter programmatic selection edit',
)

replace_once(
'''            }finally{
                if(batch)try{boundConnection.endBatchEdit();}catch(Exception ignored){}
            }
            rememberProgrammaticSelection();
''',
'''            }finally{
                if(batch)try{boundConnection.endBatchEdit();}catch(Exception ignored){}
                // Record the actual final cursor before releasing the ownership
                // guard. This also runs after a partial mutation exception, so a
                // delayed callback from that mutation cannot be misread as touch.
                rememberProgrammaticSelection();
                programmaticSelectionEditDepth=Math.max(0,programmaticSelectionEditDepth-1);
            }
''',
    'release programmatic selection edit after recording final cursor',
)

if 'versionCode 38' not in g or "versionName '1.28'" not in g:
    raise SystemExit('v1.29 patch: expected v1.28 version markers missing')
g = g.replace('versionCode 38', 'versionCode 39', 1)
g = g.replace("versionName '1.28'", "versionName '1.29'", 1)

required = [
    'private int programmaticSelectionEditDepth;',
    'private long lastProgrammaticSelectionKey;',
    'private boolean hasLastProgrammaticSelection;',
    'lastProgrammaticSelectionKey=key;',
    'private boolean matchesLastProgrammaticSelection(int start,int end){',
    'if(programmaticSelectionEditDepth>0)return;',
    'if(matchesLastProgrammaticSelection(newSelStart,newSelEnd))return;',
    'programmaticSelectionEditDepth++;',
    'programmaticSelectionEditDepth=Math.max(0,programmaticSelectionEditDepth-1);',
    'programmaticSelectionEditDepth=0; hasLastProgrammaticSelection=false;',
    'Voice stopped — selection changed',
    'private String livePartialTail = "";',
    'versionCode 39',
    "versionName '1.29'",
]
text = s + '\n' + g
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.29 patch: required invariant missing: {needle}')

for forbidden in [
    'MAX_CAPTURE_MS',
    'boundConnection.setComposingText(partial,1);',
    'versionCode 38',
    "versionName '1.28'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.29 patch: forbidden old behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.29 selection callback ownership patch')
