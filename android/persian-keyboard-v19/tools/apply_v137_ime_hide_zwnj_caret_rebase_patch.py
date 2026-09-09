from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.37 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


def replace_region(text, start_marker, end_marker, replacement, label):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f'v1.37 patch: missing start marker: {label}')
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f'v1.37 patch: missing end marker: {label}')
    return text[:start] + replacement + text[end:]


# v1.37 addresses three real-device behaviors without weakening the v1.35/v1.36
# session/range architecture:
# 1) IME visibility loss must terminate the active voice run so reopening the
#    keyboard can never expose a fake-active microphone state.
# 2) Persian bottom row gets a dedicated ZWNJ (half-space) key next to Space.
# 3) A genuine fresh touch that moves the caret rebases only the current unstable
#    live tail to the new caret. Already-final voice text stays frozen where it was;
#    future final/partial transcript deltas continue from the new caret.

s = rep(s,
'''    private boolean voiceSelectionFollowsOwnedRange;\n    private int voiceExpectedSelectionStart = -1;\n    private int voiceExpectedSelectionEnd = -1;\n''',
'''    private boolean voiceSelectionFollowsOwnedRange;\n    private int voiceExpectedSelectionStart = -1;\n    private int voiceExpectedSelectionEnd = -1;\n    private int voiceProjectionFinalBaseChars;\n    private boolean voiceCaretRebasePending;\n    private int voiceCaretRebaseStart = -1;\n    private int voiceCaretRebaseEnd = -1;\n    private long voiceCaretRebaseTouchGeneration;\n    private long voiceLastHandledTouchGeneration;\n''',
    'caret rebase state')

s = rep(s,
'''        voicePublishedText="";voiceOwnedStart=-1;voiceOwnedEnd=-1;voicePublicationPaused=false;\n        voiceSelectionFollowsOwnedRange=false;voiceExpectedSelectionStart=-1;voiceExpectedSelectionEnd=-1;\n''',
'''        voicePublishedText="";voiceOwnedStart=-1;voiceOwnedEnd=-1;voicePublicationPaused=false;\n        voiceSelectionFollowsOwnedRange=false;voiceExpectedSelectionStart=-1;voiceExpectedSelectionEnd=-1;\n        voiceProjectionFinalBaseChars=0;voiceCaretRebasePending=false;voiceCaretRebaseStart=-1;voiceCaretRebaseEnd=-1;\n        voiceCaretRebaseTouchGeneration=0L;voiceLastHandledTouchGeneration=SendAccessibilityService.userTouchGeneration();\n''',
    'reset caret rebase state')

s = rep(s,
'''    private String desiredVoiceText(){\n        synchronized(textLock){return finalTranscript.toString()+(partialTranscript==null?"":partialTranscript);}\n    }\n''',
'''    private String desiredVoiceText(){\n        synchronized(textLock){\n            String allFinal=finalTranscript.toString();\n            int base=Math.max(0,Math.min(voiceProjectionFinalBaseChars,allFinal.length()));\n            return allFinal.substring(base)+(partialTranscript==null?"":partialTranscript);\n        }\n    }\n''',
    'segment-aware desired voice text')

selection_start = '    @Override public void onUpdateSelection('
selection_end = '    private long selectionKey('
selection_method = r'''    @Override public void onUpdateSelection(int oldSelStart, int oldSelEnd, int newSelStart, int newSelEnd, int candidatesStart, int candidatesEnd) {
        super.onUpdateSelection(oldSelStart, oldSelEnd, newSelStart, newSelEnd, candidatesStart, candidatesEnd);
        // Same-editor selection still never stops speech and never re-anchors the
        // user's caret. A fresh real touch may, however, request a publication
        // rebase so subsequent dictated text follows the caret the user chose.
        if(!running||newSelStart<0||newSelEnd<newSelStart)return;
        if(newSelStart==voiceExpectedSelectionStart&&newSelEnd==voiceExpectedSelectionEnd)return;

        long touchGeneration=SendAccessibilityService.userTouchGeneration();
        long touchEventTime=SendAccessibilityService.latestUserTouchEventTime();
        long now=android.os.SystemClock.uptimeMillis();
        if(touchGeneration<voiceLastHandledTouchGeneration)return;
        if(touchGeneration==voiceLastHandledTouchGeneration&&!voiceCaretRebasePending)return;
        if(touchEventTime<=voiceStartedUptime+200L||now<touchEventTime||now-touchEventTime>1600L)return;

        if(!voiceCaretRebasePending||touchGeneration>voiceCaretRebaseTouchGeneration){
            voiceCaretRebasePending=true;
            voiceCaretRebaseTouchGeneration=touchGeneration;
        }
        if(voiceCaretRebaseTouchGeneration!=touchGeneration)return;
        voiceCaretRebaseStart=newSelStart;
        voiceCaretRebaseEnd=newSelEnd;
        final long runId=activeVoiceRunId;
        main.post(()->{if(voiceRunActive(runId))publish(false,runId);});
    }

'''
s = replace_region(s, selection_start, selection_end, selection_method,
                   'touch-gated caret publication rebase request')

# The IME can be hidden without onFinishInput() firing (for example when the host
# composer Send button is tapped). Treat visibility loss itself as voice-session
# termination and normalize the UI before a later keyboard show.
hide_methods = r'''    private void stopVoiceForImeHidden(){
        if(running)stopVoiceForManualInput();
        voiceCaretRebasePending=false;
        voiceSelectionFollowsOwnedRange=false;
        voiceExpectedSelectionStart=-1;voiceExpectedSelectionEnd=-1;
        setCollapsed(false);
        updateMicUi();
        setStatus(readyText());
    }

    @Override public void onFinishInputView(boolean finishingInput) {
        stopVoiceForImeHidden();
        super.onFinishInputView(finishingInput);
    }

    @Override public void onWindowHidden() {
        stopVoiceForImeHidden();
        super.onWindowHidden();
    }

'''
finish_input_marker = '    @Override public void onFinishInput() {'
if finish_input_marker not in s:
    raise SystemExit('v1.37 patch: onFinishInput marker missing')
s = s.replace(finish_input_marker, hide_methods + finish_input_marker, 1)

# Dedicated Persian half-space key next to Space. The visible minus-like glyph is
# only the icon; the committed character is exactly U+200C ZERO WIDTH NON-JOINER.
s = rep(s,
'''        Button space = actionKey(persian ? "فارسی" : "English", v -> commitText(" "));\n        space.setTextSize(persian ? 15f : 14f); r.addView(space, keyLp(3.7f));\n        r.addView(charKey("."), keyLp(0.88f));\n''',
'''        Button space = actionKey(persian ? "فارسی" : "English", v -> commitText(" "));\n        space.setTextSize(persian ? 15f : 14f); r.addView(space, keyLp(persian ? 2.95f : 3.7f));\n        if(persian){\n            Button zwnj=actionKey("−", v -> commitText("\\u200C"));\n            zwnj.setContentDescription("نیم‌فاصله");\n            zwnj.setTextSize(16f);\n            r.addView(zwnj,keyLp(0.75f));\n        }\n        r.addView(charKey("."), keyLp(0.88f));\n''',
    'Persian ZWNJ key beside space')

# Add rebase helpers after the existing selection-adjustment helper. Rebase moves
# only the currently unstable live partial tail. Finalized text already published
# in the previous segment is deliberately left untouched.
adjust_block = '''    private int adjustSelectionAfterReplace(int pos,int editStart,int editEnd,int replacementLength){\n        if(pos<=editStart)return pos;\n        int delta=replacementLength-(editEnd-editStart);\n        if(pos>=editEnd)return pos+delta;\n        return editStart+Math.min(Math.max(0,pos-editStart),replacementLength);\n    }\n'''
helpers = r'''

    private void refreshVoiceBoundariesForOwnedRegion(InputConnection ic){
        VoiceEditorWindow current=currentVoiceEditorWindow(ic);
        if(current==null)return;
        int rs=voiceOwnedStart-current.absoluteStart;
        int re=voiceOwnedEnd-current.absoluteStart;
        if(rs<0||re<rs||re>current.text.length())return;
        int leftStart=Math.max(0,rs-48);
        int rightEnd=Math.min(current.text.length(),re+48);
        voiceLeftBoundary=current.text.substring(leftStart,rs);
        voiceRightBoundary=current.text.substring(re,rightEnd);
        voiceBoundaryOwnsWholeField=voiceLeftBoundary.isEmpty()&&voiceRightBoundary.isEmpty();
        voiceBoundaryCaptured=true;
    }

    private boolean rebaseVoiceProjectionIfPending(InputConnection ic,VoiceEditorWindow window,long runId){
        if(!voiceCaretRebasePending)return true;
        final int rawTargetStart=voiceCaretRebaseStart;
        final int rawTargetEnd=voiceCaretRebaseEnd;
        final long touchGeneration=voiceCaretRebaseTouchGeneration;

        // Consume the user-touch intent before our own setSelection calls so
        // synchronous/asynchronous programmatic callbacks cannot overwrite it.
        voiceCaretRebasePending=false;
        voiceCaretRebaseStart=-1;voiceCaretRebaseEnd=-1;voiceCaretRebaseTouchGeneration=0L;
        voiceLastHandledTouchGeneration=Math.max(voiceLastHandledTouchGeneration,touchGeneration);

        if(!voiceRunActive(runId)||ic==null||window==null)return false;
        if(rawTargetStart<window.absoluteStart||rawTargetEnd<rawTargetStart
                ||rawTargetEnd>window.absoluteStart+window.text.length())return false;

        int[] oldRegion=locatePublishedVoiceRegion(window);
        if(oldRegion==null)return false;
        String oldTail=livePartialTail==null?"":livePartialTail;
        if(!oldTail.isEmpty()&&!voicePublishedText.endsWith(oldTail))return false;
        int tailStart=oldRegion[1]-oldTail.length();
        if(tailStart<oldRegion[0])return false;

        int targetStart=adjustSelectionAfterReplace(rawTargetStart,tailStart,oldRegion[1],0);
        int targetEnd=adjustSelectionAfterReplace(rawTargetEnd,tailStart,oldRegion[1],0);
        boolean batch=false;boolean ok=false;
        programmaticSelectionEditDepth++;
        try{
            batch=ic.beginBatchEdit();
            if(!oldTail.isEmpty()){
                if(!ic.setSelection(tailStart,oldRegion[1]))return false;
                if(!ic.commitText("",1))return false;
            }
            if(!ic.setSelection(targetStart,targetEnd))return false;
            if(!oldTail.isEmpty()&&!ic.commitText(oldTail,1))return false;
            int newOwnedEnd=targetStart+oldTail.length();
            if(!ic.setSelection(newOwnedEnd,newOwnedEnd))return false;

            // Everything that was final at the last successful publication is now
            // frozen in the old segment. Current/future live speech begins here.
            voiceProjectionFinalBaseChars=Math.max(0,committedFinalChars);
            voicePublishedText=oldTail;
            voiceOwnedStart=targetStart;voiceOwnedEnd=newOwnedEnd;
            voiceSelectionFollowsOwnedRange=true;
            voiceExpectedSelectionStart=newOwnedEnd;voiceExpectedSelectionEnd=newOwnedEnd;
            voicePublicationPaused=false;
            refreshVoiceBoundariesForOwnedRegion(ic);
            ok=true;
        }catch(Exception ignored){
        }finally{
            if(batch)try{ic.endBatchEdit();}catch(Exception ignored){}
            if(ok)rememberProgrammaticSelection();
            programmaticSelectionEditDepth=Math.max(0,programmaticSelectionEditDepth-1);
        }
        return ok;
    }
'''
if adjust_block not in s:
    raise SystemExit('v1.37 patch: selection adjustment helper block missing')
s = s.replace(adjust_block, adjust_block + helpers, 1)

# Make the publication target segment-aware and apply a pending caret rebase before
# computing the desired current-segment text. No-touch v1.36 behavior is retained.
publisher_old = '''            String desired;String partial;int finalChars;\n            synchronized(textLock){\n                desired=finalTranscript.toString()+(partialTranscript==null?"":partialTranscript);\n                partial=partialTranscript==null?"":partialTranscript;\n                finalChars=finalTranscript.length();\n            }\n\n            VoiceEditorWindow window=currentVoiceEditorWindow(ic);\n            int[] region=locatePublishedVoiceRegion(window);\n            if(window==null||region==null){noteVoicePublicationPaused(runId);return;}\n'''
publisher_new = '''            VoiceEditorWindow window=currentVoiceEditorWindow(ic);\n            if(window==null){noteVoicePublicationPaused(runId);return;}\n            if(voiceCaretRebasePending){\n                if(!rebaseVoiceProjectionIfPending(ic,window,runId)){\n                    // Rebase is opportunistic but fail-closed: never mutate an\n                    // unproved region and never stop healthy speech because of it.\n                    voiceSelectionFollowsOwnedRange=false;\n                }\n                window=currentVoiceEditorWindow(ic);\n                if(window==null){noteVoicePublicationPaused(runId);return;}\n            }\n\n            String desired;String partial;int finalChars;\n            synchronized(textLock){\n                String allFinal=finalTranscript.toString();\n                int base=Math.max(0,Math.min(voiceProjectionFinalBaseChars,allFinal.length()));\n                desired=allFinal.substring(base)+(partialTranscript==null?"":partialTranscript);\n                partial=partialTranscript==null?"":partialTranscript;\n                finalChars=allFinal.length();\n            }\n\n            int[] region=locatePublishedVoiceRegion(window);\n            if(region==null){noteVoicePublicationPaused(runId);return;}\n'''
s = rep(s, publisher_old, publisher_new, 'segment-aware publisher with caret rebase')

if 'versionCode 46' not in g or "versionName '1.36'" not in g:
    raise SystemExit('v1.37 patch: v1.36 Gradle version markers missing')
g = g.replace('versionCode 46', 'versionCode 47', 1)
g = g.replace("versionName '1.36'", "versionName '1.37'", 1)

text = s + '\n' + g
required = [
    'private int voiceProjectionFinalBaseChars;',
    'private boolean voiceCaretRebasePending;',
    'private long voiceLastHandledTouchGeneration;',
    'touchGeneration==voiceLastHandledTouchGeneration&&!voiceCaretRebasePending',
    'main.post(()->{if(voiceRunActive(runId))publish(false,runId);});',
    'private void stopVoiceForImeHidden(){',
    '@Override public void onFinishInputView(boolean finishingInput)',
    '@Override public void onWindowHidden()',
    'Button zwnj=actionKey("−", v -> commitText("\\u200C"));',
    'zwnj.setContentDescription("نیم‌فاصله")',
    'private boolean rebaseVoiceProjectionIfPending(',
    'voiceProjectionFinalBaseChars=Math.max(0,committedFinalChars);',
    'desired=allFinal.substring(base)+(partialTranscript==null?"":partialTranscript);',
    'voiceSelectionFollowsOwnedRange=true;',
    'versionCode 47',
    "versionName '1.37'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.37 patch: required invariant missing: {needle}')

for forbidden in [
    'Voice stopped — live text sync lost',
    'scheduleInternalSelectionReanchor();',
    'scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);',
    'MAX_CAPTURE_MS',
    'boundConnection.setComposingText(partial,1);',
    'versionCode 46',
    "versionName '1.36'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.37 patch: forbidden unstable behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.37 IME-hide, ZWNJ, and caret-rebase patch')
