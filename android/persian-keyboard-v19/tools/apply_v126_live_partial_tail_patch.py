from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.26 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# Restore low-latency live dictation without relying on composing spans.
# Browser/contenteditable editors (notably Samsung Browser) can lose Android
# composing state and strand stale partial text. v1.26 owns the provisional tail
# explicitly: immutable Soniox-final text is committed once, while only the
# changed suffix of the current partial is deleted/reinserted.
replace_once(
'''    private volatile int credentialWatchdogEpoch;
    private int credentialWebViewResets;
    private boolean sendAfterVoiceStop;
''',
'''    private volatile int credentialWatchdogEpoch;
    private int credentialWebViewResets;
    private String livePartialTail = "";
    private boolean sendAfterVoiceStop;
''',
    'live partial tail state',
)

replace_once(
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; sendAfterVoiceStop=false; updateMicUi();
''',
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; livePartialTail=""; sendAfterVoiceStop=false; updateMicUi();
''',
    'reset live partial tail when voice starts',
)

start = s.index('    private void publish(boolean finish){')
end = s.index('    private void finishWithText(String m){', start)
new_publish = r'''    private int commonPrefixChars(String a,String b){
        int n=Math.min(a.length(),b.length());
        int i=0;
        while(i<n&&a.charAt(i)==b.charAt(i))i++;
        if(i>0&&i<a.length()&&Character.isLowSurrogate(a.charAt(i))&&Character.isHighSurrogate(a.charAt(i-1)))i--;
        return i;
    }

    private boolean editorEndsWithLiveTail(){
        if(livePartialTail.isEmpty())return true;
        try{
            CharSequence before=boundConnection.getTextBeforeCursor(livePartialTail.length(),0);
            return before!=null&&before.toString().endsWith(livePartialTail);
        }catch(Exception e){
            return false;
        }
    }

    private void publish(boolean finish){
        main.post(()->{
            if(!sessionStillBound()&&!finish)return;
            if(boundConnection==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=boundConnection){if(running)abortForEditorChange();return;}

            String newFinal;String partial;int targetFinalChars;
            synchronized(textLock){
                String allFinal=finalTranscript.toString();
                int from=Math.min(committedFinalChars,allFinal.length());
                newFinal=allFinal.substring(from);
                partial=partialTranscript;
                targetFinalChars=allFinal.length();
            }

            // No transcript change: do not churn the browser editor.
            if(!finish&&newFinal.isEmpty()&&partial.equals(livePartialTail))return;

            if(!editorEndsWithLiveTail()){
                // The caret/editor no longer contains the provisional text that
                // this IME owns. Continuing would risk duplicates or deletion of
                // user text, so fail closed rather than guessing.
                setStatus(persian?"همگام‌سازی متن زنده از دست رفت":"Live text resync lost");
                abortForEditorChange();
                return;
            }

            boolean batch=false;
            try{
                batch=boundConnection.beginBatchEdit();

                if(!newFinal.isEmpty()){
                    // A portion of the previous provisional tail may just have
                    // become immutable final text. Remove the old tail completely,
                    // commit the newly-final text exactly once, then render the
                    // current provisional tail.
                    if(!livePartialTail.isEmpty()){
                        boundConnection.deleteSurroundingText(livePartialTail.length(),0);
                        livePartialTail="";
                    }
                    boundConnection.commitText(newFinal,1);
                    synchronized(textLock){if(committedFinalChars<targetFinalChars)committedFinalChars=targetFinalChars;}

                    if(finish){
                        if(!partial.isEmpty())boundConnection.commitText(partial,1);
                        livePartialTail="";
                    }else{
                        if(!partial.isEmpty())boundConnection.commitText(partial,1);
                        livePartialTail=partial;
                    }
                }else if(finish){
                    // If Soniox still has a non-final terminal tail, the visible
                    // live text is usually already identical. Only patch the
                    // differing suffix, then simply mark it permanent.
                    int keep=commonPrefixChars(livePartialTail,partial);
                    int remove=livePartialTail.length()-keep;
                    if(remove>0)boundConnection.deleteSurroundingText(remove,0);
                    String add=partial.substring(keep);
                    if(!add.isEmpty())boundConnection.commitText(add,1);
                    livePartialTail="";
                }else{
                    // Pure partial update: preserve the common prefix and replace
                    // only the changed suffix. This keeps live typing fast and
                    // avoids the unstable Android composing-span path entirely.
                    int keep=commonPrefixChars(livePartialTail,partial);
                    int remove=livePartialTail.length()-keep;
                    if(remove>0)boundConnection.deleteSurroundingText(remove,0);
                    String add=partial.substring(keep);
                    if(!add.isEmpty())boundConnection.commitText(add,1);
                    livePartialTail=partial;
                }

                hasComposingTail=false;
            }catch(Exception e){
                abortForEditorChange();
                return;
            }finally{
                if(batch)try{boundConnection.endBatchEdit();}catch(Exception ignored){}
            }
            rememberProgrammaticSelection();
        });
    }
'''
s = s[:start] + new_publish + s[end:]

if 'versionCode 35' not in g or "versionName '1.25'" not in g:
    raise SystemExit('v1.26 patch: expected v1.25 version markers missing')
g = g.replace('versionCode 35', 'versionCode 36', 1)
g = g.replace("versionName '1.25'", "versionName '1.26'", 1)

required = [
    'private String livePartialTail = "";',
    'private int commonPrefixChars(String a,String b){',
    'private boolean editorEndsWithLiveTail(){',
    'Pure partial update: preserve the common prefix',
    'boundConnection.deleteSurroundingText(remove,0);',
    'livePartialTail=partial;',
    'versionCode 36',
    "versionName '1.26'",
]
text = s + '\n' + g
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.26 patch: required invariant missing: {needle}')

for forbidden in [
    'boundConnection.setComposingText(partial,1);',
    'Never stream partial text into the editor',
    'versionCode 35',
    "versionName '1.25'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.26 patch: forbidden v1.25 behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.26 live partial tail replacement patch')
