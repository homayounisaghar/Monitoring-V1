from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.33 patch: missing pattern: {label}')
    return text.replace(old, new, 1)

s = rep(s,
'''import android.graphics.drawable.GradientDrawable;\n''',
'''import android.graphics.drawable.GradientDrawable;\nimport android.graphics.drawable.InsetDrawable;\n''',
    'InsetDrawable import')

s = rep(s,
'''    private int internalSelectionReanchorEpoch;\n''',
'''    private int internalSelectionReanchorEpoch;\n    private int liveSyncRecoveryEpoch;\n    private long liveSyncFailureSince;\n''',
    'live sync recovery state')

s = rep(s,
'''    private LinearLayout.LayoutParams keyLp(float weight) {\n        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(35), weight); lp.setMargins(dp(2),dp(1),dp(2),dp(1)); return lp;\n    }\n\n    private Button charKey(String label) {\n        Button b=baseKey(label,false);\n        b.setOnClickListener(v -> { stopVoiceForManualInput(); commitText(label); });\n        String[] vars=longPress.get(label);\n        if (vars!=null) b.setOnLongClickListener(v -> { stopVoiceForManualInput(); showVariants(b,vars); return true; });\n        return b;\n    }\n''',
'''    private LinearLayout.LayoutParams keyLp(float weight) {\n        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(38), weight);\n        lp.setMargins(0,0,0,0);\n        return lp;\n    }\n\n    private Button charKey(String label) {\n        Button b=baseKey(label,false);\n        final boolean[] downCommitted=new boolean[]{false};\n        b.setOnTouchListener((v,event) -> {\n            int action=event.getActionMasked();\n            if(action==MotionEvent.ACTION_DOWN){\n                downCommitted[0]=true;\n                stopVoiceForManualInput();\n                commitText(label);\n            }else if(action==MotionEvent.ACTION_CANCEL){\n                downCommitted[0]=false;\n            }\n            return false;\n        });\n        b.setOnClickListener(v -> {\n            if(downCommitted[0]){downCommitted[0]=false;return;}\n            stopVoiceForManualInput();\n            commitText(label);\n        });\n        String[] vars=longPress.get(label);\n        if(vars!=null) b.setOnLongClickListener(v -> {\n            backspaceOnce();\n            showVariants(b,vars);\n            return true;\n        });\n        return b;\n    }\n''',
    'full-slot touch targets and ACTION_DOWN character dispatch')

s = rep(s,
'''        b.setTypeface(Typeface.create("sans-serif",Typeface.NORMAL)); b.setBackground(round(action?ACTION:KEY,dp(8))); return b;\n''',
'''        b.setTypeface(Typeface.create("sans-serif",Typeface.NORMAL));\n        b.setBackground(new InsetDrawable(round(action?ACTION:KEY,dp(8)),dp(2),dp(1),dp(2),dp(1)));\n        return b;\n''',
    'visual inset without dead touch margins')

old_manual = '''    private void stopVoiceForManualInput(){\n        if(!running)return;\n        sendAfterVoiceStop=false;\n        running=false; completed=true; stopRequested=true; awaitingCredential=false; retryAfterPageLoad=false;\n        backspaceHeld=false; main.removeCallbacks(backspaceRepeater);\n        stopAudioRecord(); clearPending();\n        WebSocket ws=webSocket; webSocket=null; if(ws!=null)ws.cancel();\n        InputConnection old=boundConnection; boundConnection=null;\n        if(old!=null)try{old.finishComposingText();}catch(Exception ignored){}\n        synchronized(expectedSelectionUpdates){expectedSelectionUpdates.clear();}\n        hasComposingTail=false;\n        updateMicUi(); setStatus(readyText());\n    }\n'''
new_manual = '''    private void stopVoiceForManualInput(){\n        if(!running)return;\n        sendAfterVoiceStop=false;\n        running=false; completed=true; stopRequested=true; awaitingCredential=false; retryAfterPageLoad=false;\n        selectionConfirmationEpoch++; selectionConfirmationPending=false;\n        internalSelectionReanchorEpoch++; liveSyncRecoveryEpoch++; liveSyncFailureSince=0L;\n        backspaceHeld=false; main.removeCallbacks(backspaceRepeater);\n\n        AudioRecord detachedAudio=audioRecord; audioRecord=null;\n        WebSocket detachedSocket=webSocket; webSocket=null;\n        boundConnection=null;\n        clearPending();\n        synchronized(expectedSelectionUpdates){expectedSelectionUpdates.clear();}\n        hasComposingTail=false; livePartialTail="";\n        updateMicUi(); setStatus(readyText());\n\n        if(detachedAudio!=null||detachedSocket!=null){\n            new Thread(()->{\n                if(detachedAudio!=null){\n                    try{if(detachedAudio.getRecordingState()==AudioRecord.RECORDSTATE_RECORDING)detachedAudio.stop();}catch(Exception ignored){}\n                    try{detachedAudio.release();}catch(Exception ignored){}\n                }\n                if(detachedSocket!=null)try{detachedSocket.cancel();}catch(Exception ignored){}\n            },"persian-keyboard-manual-stop").start();\n        }\n    }\n'''
s = rep(s, old_manual, new_manual, 'non-blocking manual voice interruption')

marker = '    private void publish(boolean finish){\n'
if marker not in s:
    raise SystemExit('v1.33 patch: missing publish marker')
insert_at = s.index(marker)
helpers = r'''    private String ownedVoiceRecoveryGuard(){
        synchronized(textLock){
            String allFinal=finalTranscript.toString();
            int committed=Math.max(0,Math.min(committedFinalChars,allFinal.length()));
            String visible=allFinal.substring(0,committed)+(livePartialTail==null?"":livePartialTail);
            int n=Math.min(80,visible.length());
            return n<=0?"":visible.substring(visible.length()-n);
        }
    }

    private boolean cursorEndsWithGuard(InputConnection ic,String guard){
        if(ic==null||guard==null||guard.isEmpty())return false;
        try{
            CharSequence before=ic.getTextBeforeCursor(guard.length(),0);
            return before!=null&&before.toString().endsWith(guard);
        }catch(Exception ignored){
            return false;
        }
    }

    private boolean setRecoverySelection(InputConnection ic,int start,int end){
        if(ic==null||start<0||end<0)return false;
        programmaticSelectionEditDepth++;
        try{
            if(!ic.setSelection(start,end))return false;
            rememberProgrammaticSelection();
            return true;
        }catch(Exception ignored){
            return false;
        }finally{
            programmaticSelectionEditDepth=Math.max(0,programmaticSelectionEditDepth-1);
        }
    }

    private boolean recoverOwnedVoiceCursor(){
        if(!running||hasRecentEditorUserInteraction())return false;
        InputConnection ic=boundConnection;
        if(ic==null||getCurrentInputConnection()!=ic)return false;
        String guard=ownedVoiceRecoveryGuard();
        if(hasLastProgrammaticSelection&&lastProgrammaticSelectionStart>=0&&lastProgrammaticSelectionEnd>=0){
            if(setRecoverySelection(ic,lastProgrammaticSelectionStart,lastProgrammaticSelectionEnd)){
                if(livePartialTail.isEmpty()||editorEndsWithLiveTail()){
                    if(guard.isEmpty()||cursorEndsWithGuard(ic,guard))return true;
                }
            }
        }
        if(guard.length()<8)return false;
        try{
            android.view.inputmethod.ExtractedTextRequest req=new android.view.inputmethod.ExtractedTextRequest();
            android.view.inputmethod.ExtractedText et=ic.getExtractedText(req,0);
            if(et==null||et.text==null)return false;
            String snapshot=et.text.toString();
            int first=snapshot.indexOf(guard);
            if(first<0||first!=snapshot.lastIndexOf(guard))return false;
            int target=et.startOffset+first+guard.length();
            if(!setRecoverySelection(ic,target,target))return false;
            return cursorEndsWithGuard(ic,guard)
                    &&(livePartialTail.isEmpty()||editorEndsWithLiveTail());
        }catch(Exception ignored){
            return false;
        }
    }

    private void clearLiveSyncFailure(){
        if(liveSyncFailureSince==0L)return;
        liveSyncFailureSince=0L;
        liveSyncRecoveryEpoch++;
        if(running)setStatus(listeningText());
    }

    private void noteLiveSyncFailure(){
        if(liveSyncFailureSince!=0L)return;
        liveSyncFailureSince=android.os.SystemClock.uptimeMillis();
        final int epoch=++liveSyncRecoveryEpoch;
        setStatus(persian?"در حال بازیابی همگام‌سازی متن زنده…":"Recovering live text sync…");
        main.postDelayed(()->{
            if(epoch!=liveSyncRecoveryEpoch||!running||liveSyncFailureSince==0L)return;
            if(recoverOwnedVoiceCursor()){
                clearLiveSyncFailure();
                return;
            }
            stopVoiceForManualInput();
            setStatus("Voice stopped — live text sync lost");
        },1500L);
    }

'''
s = s[:insert_at] + helpers + s[insert_at:]

s = rep(s,
'''            if(!editorEndsWithLiveTail()){\n                // Do not mutate text if ownership cannot be proven. This remains\n                // fail-closed for duplicate/deletion safety, but it must not stop\n                // an otherwise healthy recording session. A later transcript\n                // update can retry once the editor snapshot is coherent again.\n                return;\n            }\n\n            boolean batch=false;\n''',
'''            if(!editorEndsWithLiveTail()&&!recoverOwnedVoiceCursor()){\n                noteLiveSyncFailure();\n                return;\n            }\n            clearLiveSyncFailure();\n\n            boolean batch=false;\n''',
    'recover instead of silently stalling live publisher')

s = rep(s,
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; livePartialTail=""; programmaticSelectionEditDepth=0; hasLastProgrammaticSelection=false; lastProgrammaticSelectionStart=-1; lastProgrammaticSelectionEnd=-1; selectionConfirmationEpoch++; selectionConfirmationPending=false; internalSelectionReanchorEpoch++; voiceStartedUptime=android.os.SystemClock.uptimeMillis(); voiceStartTouchGeneration=SendAccessibilityService.userTouchGeneration(); lastEditorToolInteractionUptime=0L; sendAfterVoiceStop=false; updateMicUi();\n''',
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; livePartialTail=""; programmaticSelectionEditDepth=0; hasLastProgrammaticSelection=false; lastProgrammaticSelectionStart=-1; lastProgrammaticSelectionEnd=-1; selectionConfirmationEpoch++; selectionConfirmationPending=false; internalSelectionReanchorEpoch++; liveSyncRecoveryEpoch++; liveSyncFailureSince=0L; voiceStartedUptime=android.os.SystemClock.uptimeMillis(); voiceStartTouchGeneration=SendAccessibilityService.userTouchGeneration(); lastEditorToolInteractionUptime=0L; sendAfterVoiceStop=false; updateMicUi();\n''',
    'reset live sync recovery on voice start')

if 'versionCode 42' not in g or "versionName '1.32'" not in g:
    raise SystemExit('v1.33 patch: expected v1.32 version markers missing')
g = g.replace('versionCode 42', 'versionCode 43', 1)
g = g.replace("versionName '1.32'", "versionName '1.33'", 1)

text=s+'\n'+g
required=[
    'import android.graphics.drawable.InsetDrawable;',
    'private int liveSyncRecoveryEpoch;',
    'private long liveSyncFailureSince;',
    'new LinearLayout.LayoutParams(0, dp(38), weight)',
    'lp.setMargins(0,0,0,0);',
    'if(action==MotionEvent.ACTION_DOWN)',
    'b.setBackground(new InsetDrawable(',
    'AudioRecord detachedAudio=audioRecord; audioRecord=null;',
    'persian-keyboard-manual-stop',
    'private String ownedVoiceRecoveryGuard(){',
    'private boolean recoverOwnedVoiceCursor(){',
    'snapshot.lastIndexOf(guard)',
    'private void noteLiveSyncFailure(){',
    'Voice stopped — live text sync lost',
    'if(!editorEndsWithLiveTail()&&!recoverOwnedVoiceCursor())',
    'versionCode 43',
    "versionName '1.33'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.33 patch: required invariant missing: {needle}')
for forbidden in [
    'lp.setMargins(dp(2),dp(1),dp(2),dp(1));',
    'b.setOnClickListener(v -> { stopVoiceForManualInput(); commitText(label); });',
    'MAX_CAPTURE_MS',
    'boundConnection.setComposingText(partial,1);',
    'versionCode 42',
    "versionName '1.32'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.33 patch: forbidden old behavior remains: {needle}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.33 live-sync recovery and fast-key patch')
