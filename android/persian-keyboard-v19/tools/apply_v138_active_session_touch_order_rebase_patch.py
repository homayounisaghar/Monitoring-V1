from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.38 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


def replace_region(text, start_marker, end_marker, replacement, label):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f'v1.38 patch: missing start marker: {label}')
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f'v1.38 patch: missing end marker: {label}')
    return text[:start] + replacement + text[end:]


# v1.37 made active-session caret rebase depend on callback ordering: the fresh
# Accessibility touch generation had to be visible already when onUpdateSelection
# ran. Android does not guarantee that cross-service Accessibility delivery wins
# that race. If selection arrived first, v1.37 discarded it and never reconsidered
# the now-changed caret when the next speech publication occurred.
#
# v1.38 removes only that ordering assumption. A divergent selection is retained
# as a short-lived candidate. It becomes mutation authority only after a fresh
# system touch-start event is correlated to the candidate. The next normal speech
# publication re-checks that correlation, so touch-before-selection and
# selection-before-touch both converge without polling, delayed selection loops,
# active re-anchor, snap-to-end, or selection-as-stop causality.

s = rep(s,
'''    private long voiceCaretRebaseTouchGeneration;\n    private long voiceLastHandledTouchGeneration;\n''',
'''    private long voiceCaretRebaseTouchGeneration;\n    private long voiceCaretRebaseSelectionUptime;\n    private long voiceLastHandledTouchGeneration;\n''',
    'selection-time correlation state')

s = rep(s,
'''        voiceCaretRebaseTouchGeneration=0L;voiceLastHandledTouchGeneration=SendAccessibilityService.userTouchGeneration();\n''',
'''        voiceCaretRebaseTouchGeneration=0L;voiceCaretRebaseSelectionUptime=0L;\n        voiceLastHandledTouchGeneration=SendAccessibilityService.userTouchGeneration();\n''',
    'reset selection-time correlation state')

selection_start = '    @Override public void onUpdateSelection('
selection_end = '    private long selectionKey('
selection_method = r'''    @Override public void onUpdateSelection(int oldSelStart, int oldSelEnd, int newSelStart, int newSelEnd, int candidatesStart, int candidatesEnd) {
        super.onUpdateSelection(oldSelStart, oldSelEnd, newSelStart, newSelEnd, candidatesStart, candidatesEnd);
        // Same-editor selection still never stops speech and never re-anchors the
        // user's caret. Keep an off-expected selection only as a candidate until
        // an independently observed fresh system touch proves user intent.
        if(!running||newSelStart<0||newSelEnd<newSelStart)return;
        if(newSelStart==voiceExpectedSelectionStart&&newSelEnd==voiceExpectedSelectionEnd)return;
        if(programmaticSelectionEditDepth>0)return;

        voiceCaretRebasePending=true;
        voiceCaretRebaseStart=newSelStart;
        voiceCaretRebaseEnd=newSelEnd;
        voiceCaretRebaseSelectionUptime=android.os.SystemClock.uptimeMillis();
        voiceCaretRebaseTouchGeneration=0L;

        final long runId=activeVoiceRunId;
        InputConnection ic=boundConnection;
        VoiceEditorWindow window=(ic!=null&&getCurrentInputConnection()==ic)?currentVoiceEditorWindow(ic):null;
        if(confirmVoiceCaretRebaseCandidate(ic,window,runId))
            main.post(()->{if(voiceRunActive(runId))publish(false,runId);});
    }

'''
s = replace_region(s, selection_start, selection_end, selection_method,
                   'order-independent active-session caret candidate capture')

# Insert the correlation helper immediately before the existing v1.37 rebase
# mutation. It never edits text. It only converts a selection candidate into a
# confirmed rebase request when the current editor selection still agrees and a
# fresh touch-start event is close to the candidate in the same uptime clock.
rebase_marker = '    private boolean rebaseVoiceProjectionIfPending(InputConnection ic,VoiceEditorWindow window,long runId){\n'
correlation_helper = r'''    private void clearVoiceCaretRebaseCandidate(){
        voiceCaretRebasePending=false;
        voiceCaretRebaseStart=-1;voiceCaretRebaseEnd=-1;
        voiceCaretRebaseTouchGeneration=0L;voiceCaretRebaseSelectionUptime=0L;
    }

    private boolean confirmVoiceCaretRebaseCandidate(InputConnection ic,VoiceEditorWindow window,long runId){
        if(!voiceCaretRebasePending||voiceCaretRebaseTouchGeneration>0L)return false;
        if(!voiceRunActive(runId)||ic==null){clearVoiceCaretRebaseCandidate();return false;}

        long now=android.os.SystemClock.uptimeMillis();
        long candidateTime=voiceCaretRebaseSelectionUptime;
        if(candidateTime<=0L||now<candidateTime||now-candidateTime>3000L){
            clearVoiceCaretRebaseCandidate();return false;
        }

        if(window==null)window=currentVoiceEditorWindow(ic);
        if(window==null)return false;
        // Publication at the old voice range may have adjusted the absolute
        // cursor position while preserving the user's logical caret. Follow the
        // editor's current off-expected selection, but never manufacture a
        // candidate if the editor has returned to the IME-expected voice end.
        if(window.selectionStart==voiceExpectedSelectionStart&&window.selectionEnd==voiceExpectedSelectionEnd){
            clearVoiceCaretRebaseCandidate();return false;
        }
        voiceCaretRebaseStart=window.selectionStart;
        voiceCaretRebaseEnd=window.selectionEnd;

        long touchGeneration=SendAccessibilityService.userTouchGeneration();
        long touchEventTime=SendAccessibilityService.latestUserTouchEventTime();
        if(touchGeneration<=voiceLastHandledTouchGeneration)return false;
        if(touchEventTime<=voiceStartedUptime+200L||now<touchEventTime||now-touchEventTime>3000L)return false;
        long correlation=Math.abs(candidateTime-touchEventTime);
        if(correlation>900L)return false;

        voiceCaretRebaseTouchGeneration=touchGeneration;
        return true;
    }

'''
if rebase_marker not in s:
    raise SystemExit('v1.38 patch: rebase method marker missing')
s = s.replace(rebase_marker, correlation_helper + rebase_marker, 1)

# A candidate without a confirmed touch is not a rebase mutation request. Leave it
# pending for a later normal speech publish to correlate. Once confirmed, consume
# it exactly once and preserve v1.37 fail-closed range ownership.
s = rep(s,
'''        if(!voiceCaretRebasePending)return true;\n        final int rawTargetStart=voiceCaretRebaseStart;\n''',
'''        if(!voiceCaretRebasePending)return true;\n        if(voiceCaretRebaseTouchGeneration<=0L)return true;\n        final int rawTargetStart=voiceCaretRebaseStart;\n''',
    'do not mutate from unconfirmed selection candidate')

s = rep(s,
'''        voiceCaretRebasePending=false;\n        voiceCaretRebaseStart=-1;voiceCaretRebaseEnd=-1;voiceCaretRebaseTouchGeneration=0L;\n        voiceLastHandledTouchGeneration=Math.max(voiceLastHandledTouchGeneration,touchGeneration);\n''',
'''        clearVoiceCaretRebaseCandidate();\n        voiceLastHandledTouchGeneration=Math.max(voiceLastHandledTouchGeneration,touchGeneration);\n''',
    'consume confirmed candidate once')

publisher_old = '''            VoiceEditorWindow window=currentVoiceEditorWindow(ic);\n            if(window==null){noteVoicePublicationPaused(runId);return;}\n            if(voiceCaretRebasePending){\n                if(!rebaseVoiceProjectionIfPending(ic,window,runId)){\n                    // Rebase is opportunistic but fail-closed: never mutate an\n                    // unproved region and never stop healthy speech because of it.\n                    voiceSelectionFollowsOwnedRange=false;\n                }\n                window=currentVoiceEditorWindow(ic);\n                if(window==null){noteVoicePublicationPaused(runId);return;}\n            }\n'''
publisher_new = '''            VoiceEditorWindow window=currentVoiceEditorWindow(ic);\n            if(window==null){noteVoicePublicationPaused(runId);return;}\n            if(voiceCaretRebasePending&&voiceCaretRebaseTouchGeneration<=0L)\n                confirmVoiceCaretRebaseCandidate(ic,window,runId);\n            if(voiceCaretRebasePending&&voiceCaretRebaseTouchGeneration>0L){\n                if(!rebaseVoiceProjectionIfPending(ic,window,runId)){\n                    // Rebase is opportunistic but fail-closed: never mutate an\n                    // unproved region and never stop healthy speech because of it.\n                    voiceSelectionFollowsOwnedRange=false;\n                }\n                window=currentVoiceEditorWindow(ic);\n                if(window==null){noteVoicePublicationPaused(runId);return;}\n            }\n'''
s = rep(s, publisher_old, publisher_new,
        're-check late touch correlation on the next speech publication')

# IME-hide reset must discard any candidate as well as any confirmed rebase request.
s = rep(s,
'''        voiceCaretRebasePending=false;\n        voiceSelectionFollowsOwnedRange=false;\n''',
'''        clearVoiceCaretRebaseCandidate();\n        voiceSelectionFollowsOwnedRange=false;\n''',
    'hide clears unconfirmed/confirmed caret candidate')

if 'versionCode 47' not in g or "versionName '1.37'" not in g:
    raise SystemExit('v1.38 patch: v1.37 Gradle version markers missing')
g = g.replace('versionCode 47', 'versionCode 48', 1)
g = g.replace("versionName '1.37'", "versionName '1.38'", 1)

text = s + '\n' + g
required = [
    'private long voiceCaretRebaseSelectionUptime;',
    'voiceCaretRebaseSelectionUptime=android.os.SystemClock.uptimeMillis();',
    'private boolean confirmVoiceCaretRebaseCandidate(',
    'long correlation=Math.abs(candidateTime-touchEventTime);',
    'if(correlation>900L)return false;',
    'if(voiceCaretRebaseTouchGeneration<=0L)return true;',
    'if(voiceCaretRebasePending&&voiceCaretRebaseTouchGeneration<=0L)',
    'confirmVoiceCaretRebaseCandidate(ic,window,runId);',
    'if(voiceCaretRebasePending&&voiceCaretRebaseTouchGeneration>0L)',
    'clearVoiceCaretRebaseCandidate();',
    'private void stopVoiceForImeHidden(){',
    'Button zwnj=actionKey("−", v -> commitText("\\u200C"));',
    'voiceProjectionFinalBaseChars=Math.max(0,committedFinalChars);',
    'versionCode 48',
    "versionName '1.38'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.38 patch: required invariant missing: {needle}')

for forbidden in [
    'Voice stopped — live text sync lost',
    'scheduleInternalSelectionReanchor();',
    'scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);',
    'MAX_CAPTURE_MS',
    'boundConnection.setComposingText(partial,1);',
    'touchGeneration==voiceLastHandledTouchGeneration&&!voiceCaretRebasePending',
    'versionCode 47',
    "versionName '1.37'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.38 patch: forbidden unstable/old behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied v1.38 order-independent active-session caret rebase patch')
