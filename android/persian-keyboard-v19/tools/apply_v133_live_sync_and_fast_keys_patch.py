from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.33 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


# v1.32 device evidence changed the diagnosis: the microphone UI can remain in
# the active/navy state while live transcript publication has stopped. Since
# v1.27, loss of livePartialTail ownership deliberately returns from publish()
# without stopping transport. That protects text from unsafe mutation, but can
# leave running=true while the user sees no new text.
#
# v1.33 adds a fail-safe recovery path. It first re-anchors to the last cursor
# position proven to be IME-owned. If editor offsets shifted, it searches for a
# bounded, sufficiently long UNIQUE suffix of the text already owned by the voice
# session in ExtractedText. Text is mutated only after ownership is verified. If
# recovery remains impossible, the session/UI is explicitly stopped instead of
# pretending to keep recording.
#
# Fast manual typing is fixed independently: key views now fill their entire
# weighted slots (visual spacing moves inside the drawable), and ordinary
# character keys commit on ACTION_DOWN. Keys with long-press variants retain the
# old click/long-click semantics so variants are not regressed.

s = rep(s,
'''import android.graphics.drawable.GradientDrawable;\n''',
'''import android.graphics.drawable.GradientDrawable;\nimport android.graphics.drawable.InsetDrawable;\n''',
    'InsetDrawable import')

s = rep(s,
'''    private int internalSelectionReanchorEpoch;\n''',
'''    private int internalSelectionReanchorEpoch;\n    private int liveSyncRecoveryEpoch;\n    private long liveSyncFailureSince;\n''',
    'live sync recovery state')

s = rep(s,
'''    private LinearLayout.LayoutParams keyLp(float weight) {\n        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, keyHeightPx(), weight); lp.setMargins(dp(2),dp(1),dp(2),dp(1)); return lp;\n    }\n''',
'''    private LinearLayout.LayoutParams keyLp(float weight) {\n        // The View owns the whole weighted slot. Visual separation is drawn by\n        // InsetDrawable in baseKey(), so fast taps cannot land in a dead margin.\n        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, keyHeightPx(), weight);\n        lp.setMargins(0,0,0,0);\n        return lp;\n    }\n''',
    'full-slot key touch targets')

s = rep(s,
'''    private Button charKey(String label) {\n        Button b=baseKey(label,false);\n        b.setOnClickListener(v -> { stopVoiceForManualInput(); commitText(label); });\n        String[] vars=longPress.get(label);\n        if (vars!=null) b.setOnLongClickListener(v -> { stopVoiceForManualInput(); showVariants(b,vars); return true; });\n        return b;\n    }\n''',
'''    private Button charKey(String label) {\n        Button b=baseKey(label,false);\n        String[] vars=longPress.get(label);\n        if(vars==null){\n            // Low-latency physical-key path. Consume the gesture so ACTION_UP does\n            // not generate a second click; the OnClick listener remains available\n            // to accessibility/programmatic activation.\n            b.setOnTouchListener((v,event) -> {\n                int action=event.getActionMasked();\n                if(action==MotionEvent.ACTION_DOWN){\n                    v.setPressed(true);\n                    stopVoiceForManualInput();\n                    commitText(label);\n                    return true;\n                }\n                if(action==MotionEvent.ACTION_UP||action==MotionEvent.ACTION_CANCEL){\n                    v.setPressed(false);\n                    return true;\n                }\n                return true;\n            });\n            b.setOnClickListener(v -> { stopVoiceForManualInput(); commitText(label); });\n        }else{\n            // Preserve the established long-press popup behavior exactly for the\n            // small set of keys that expose character variants.\n            b.setOnClickListener(v -> { stopVoiceForManualInput(); commitText(label); });\n            b.setOnLongClickListener(v -> { stopVoiceForManualInput(); showVariants(b,vars); return true; });\n        }\n        return b;\n    }\n''',
    'ACTION_DOWN ordinary character dispatch')

s = rep(s,
'''        b.setTypeface(Typeface.create("sans-serif",Typeface.NORMAL)); b.setBackground(round(action?ACTION:KEY,dp(8))); return b;\n''',
'''        b.setTypeface(Typeface.create("sans-serif",Typeface.NORMAL));\n        // Preserve the old visual gutters but keep them inside the clickable view.\n        b.setBackground(new InsetDrawable(round(action?ACTION:KEY,dp(8)),dp(2),dp(1),dp(2),dp(1)));\n        return b;\n''',
    'visual inset without dead touch margins')

# Insert publisher-side recovery immediately before the existing publish method.
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

        // Fast path: editor text is intact and only its reported selection drifted.
        if(hasLastProgrammaticSelection&&lastProgrammaticSelectionStart>=0&&lastProgrammaticSelectionEnd>=0){
            if(setRecoverySelection(ic,lastProgrammaticSelectionStart,lastProgrammaticSelectionEnd)){
                if(livePartialTail.isEmpty()||editorEndsWithLiveTail()){
                    if(guard.isEmpty()||cursorEndsWithGuard(ic,guard))return true;
                }
            }
        }

        // Offset-shift fallback. Never guess from a short/repeated suffix.
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
'''            if(!editorEndsWithLiveTail()&&!recoverOwnedVoiceCursor()){\n                // Stay fail-closed for text mutation, but actively recover the\n                // owned cursor instead of silently leaving running=true forever.\n                noteLiveSyncFailure();\n                return;\n            }\n            clearLiveSyncFailure();\n\n            boolean batch=false;\n''',
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
    'new LinearLayout.LayoutParams(0, keyHeightPx(), weight)',
    'lp.setMargins(0,0,0,0);',
    'if(vars==null){',
    'if(action==MotionEvent.ACTION_DOWN)',
    'v.setPressed(true);',
    'b.setBackground(new InsetDrawable(',
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
