from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.44 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


def replace_region(text, start_marker, end_marker, replacement, label):
    start = text.find(start_marker)
    end = text.find(end_marker, start + len(start_marker)) if start >= 0 else -1
    if start < 0 or end < 0:
        raise SystemExit(f'v1.44 patch: missing region: {label}')
    return text[:start] + replacement + text[end:]


# v1.44 targets four concrete device-reported failure modes without changing the
# accepted v1.42 broker/microphone architecture or v1.40 user-caret contract:
#
# 1) Some host editors can settle the caret one UTF-16 code unit before the live
#    voice end immediately after an IME-owned publication. v1.40 interpreted every
#    such divergence as a deliberate user caret move and rotated the speech
#    transport. A narrow, time-bounded lease now repairs only the exact end-1
#    pattern when the voice-owned text is still proved intact and no newer touch
#    generation is visible. Every other selection divergence still uses the
#    established true-caret-cutover path.
# 2) A real user cutover to the end of non-whitespace text now carries one visual
#    word-boundary space into the new voice segment. The cutover itself still does
#    not mutate editor text; the prefix is published with the first/future speech
#    projection, preserving the v1.40 no-snap/no-move invariant.
# 3) The dedicated Enter key inserts a newline first in multiline/no-enter-action
#    text editors instead of letting an advertised editor action swallow Enter.
# 4) v1.33 removed horizontal dead margins but key views remained shorter than
#    their row. Keys now fill row height; InsetDrawable keeps the same visual gap
#    inside each clickable tile, removing the remaining vertical dead strips.
#
# Genuine caret cutover transport recovery also consumes the v1.42 warm credential
# first, avoiding an unnecessary fresh private-session probe where possible.

s = rep(
    s,
    '''    private boolean voiceExternalClearStopArmed;\n''',
    '''    private boolean voiceExternalClearStopArmed;\n    private long voiceProgrammaticCaretLeaseUntilUptime;\n    private int voiceProgrammaticCaretLeaseEnd = -1;\n    private long voiceProgrammaticCaretTouchGeneration;\n    private String voiceProjectionPrefix = "";\n''',
    'v1.44 caret lease and projection prefix state',
)

# The view now fills the fixed-height row. Visual top/bottom gutters remain inside
# the existing InsetDrawable, so appearance stays unchanged while touch tiling is
# continuous between rows.
key_lp = r'''    private LinearLayout.LayoutParams keyLp(float weight) {
        // The clickable View owns the entire weighted row tile. v1.33 already
        // moved the visible gutters into InsetDrawable; MATCH_PARENT closes the
        // remaining vertical dead strip between adjacent key rows.
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                0, ViewGroup.LayoutParams.MATCH_PARENT, weight);
        lp.setMargins(0,0,0,0);
        return lp;
    }

'''
s = replace_region(
    s,
    '    private LinearLayout.LayoutParams keyLp(float weight) {',
    '    private Button charKey(String label)',
    key_lp,
    'full-height key touch tiles',
)

# Dedicated Enter semantics: in a text editor that explicitly supports multiple
# lines (or asks IMEs not to turn Enter into an action), newline is the primary
# operation. Single-line action fields retain their advertised editor action.
enter_method = r'''    private void enter(){
        stopVoiceForManualInput();
        InputConnection ic=getCurrentInputConnection();
        if(ic==null)return;
        int inputType=editorInfo==null?0:editorInfo.inputType;
        int imeOptions=editorInfo==null?0:editorInfo.imeOptions;
        int action=imeOptions&EditorInfo.IME_MASK_ACTION;
        boolean textEditor=(inputType&InputType.TYPE_MASK_CLASS)==InputType.TYPE_CLASS_TEXT;
        boolean multiline=(inputType&InputType.TYPE_TEXT_FLAG_MULTI_LINE)!=0;
        boolean noEnterAction=(imeOptions&EditorInfo.IME_FLAG_NO_ENTER_ACTION)!=0;
        try{
            if(textEditor&&(multiline||noEnterAction)){
                if(ic.commitText("\n",1))return;
                ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_DOWN,KeyEvent.KEYCODE_ENTER));
                ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_UP,KeyEvent.KEYCODE_ENTER));
                return;
            }
            if(action!=EditorInfo.IME_ACTION_NONE
                    &&action!=EditorInfo.IME_ACTION_UNSPECIFIED
                    &&ic.performEditorAction(action))return;
            ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_DOWN,KeyEvent.KEYCODE_ENTER));
            ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_UP,KeyEvent.KEYCODE_ENTER));
        }catch(Exception ignored){}
    }

'''
s = replace_region(
    s,
    '    private void enter(){',
    '    private void pasteClipboard(){',
    enter_method,
    'multiline newline-first Enter semantics',
)

# Prefix is segment-local and persistent so subsequent partial/final replacements
# do not delete the one separator that was added at a genuine end-of-text cutover.
prefix_helper = r'''    private String withVoiceProjectionPrefix(String segment){
        if(segment==null||segment.isEmpty()||voiceProjectionPrefix.isEmpty())return segment==null?"":segment;
        if(Character.isWhitespace(segment.charAt(0)))return segment;
        return voiceProjectionPrefix+segment;
    }

'''
marker = '    private String desiredVoiceText(){'
if marker not in s:
    raise SystemExit('v1.44 patch: desiredVoiceText marker missing')
s = s.replace(marker, prefix_helper + marker, 1)

s = rep(
    s,
    'return allFinal.substring(base)+(partialTranscript==null?"":partialTranscript);',
    'return withVoiceProjectionPrefix(allFinal.substring(base)+(partialTranscript==null?"":partialTranscript));',
    'segment-aware helper prefix',
)
s = rep(
    s,
    'desired=allFinal.substring(base)+(partialTranscript==null?"":partialTranscript);',
    'desired=withVoiceProjectionPrefix(allFinal.substring(base)+(partialTranscript==null?"":partialTranscript));',
    'publisher segment prefix',
)

# Reset v1.44 state at the start of every logical voice run. v1.42 immediately
# follows this marker by forcing the alpha layer before activating the mic UI.
s = rep(
    s,
    '''        voicePublicationPaused=false;\n        layer=Layer.ALPHA;shift=false;\n''',
    '''        voicePublicationPaused=false;\n        voiceProgrammaticCaretLeaseUntilUptime=0L;\n        voiceProgrammaticCaretLeaseEnd=-1;\n        voiceProgrammaticCaretTouchGeneration=SendAccessibilityService.userTouchGeneration();\n        voiceProjectionPrefix="";\n        layer=Layer.ALPHA;shift=false;\n''',
    'reset v1.44 voice-run state',
)

# Remember a short ownership lease around the exact live-end selection that the
# publisher itself creates. Synchronous callbacks are already protected by
# programmaticSelectionEditDepth; this covers only delayed host callbacks.
s = rep(
    s,
    '''                if(followVoiceEnd){\n                    voiceExpectedSelectionStart=newOwnedEnd;\n                    voiceExpectedSelectionEnd=newOwnedEnd;\n                }\n                voicePublishedText=desired;voiceOwnedStart=region[0];voiceOwnedEnd=newOwnedEnd;\n''',
    '''                if(followVoiceEnd){\n                    voiceExpectedSelectionStart=newOwnedEnd;\n                    voiceExpectedSelectionEnd=newOwnedEnd;\n                    voiceProgrammaticCaretLeaseEnd=newOwnedEnd;\n                    voiceProgrammaticCaretLeaseUntilUptime=android.os.SystemClock.uptimeMillis()+1200L;\n                    voiceProgrammaticCaretTouchGeneration=SendAccessibilityService.userTouchGeneration();\n                }\n                voicePublishedText=desired;voiceOwnedStart=region[0];voiceOwnedEnd=newOwnedEnd;\n''',
    'lease delayed programmatic live-end callbacks',
)

# Replace v1.40 selection handling with the same true user-caret cutover plus one
# very narrow repair: exact end-1, inside the lease, intact voice-owned range, and
# no newer accessibility touch generation. This is deliberately not a broad
# re-anchor/selection-confirmation mechanism.
selection_methods = r'''    private boolean healTransientVoiceEndMinusOne(
            InputConnection ic,VoiceEditorWindow current,long runId){
        if(!voiceRunActive(runId)||ic==null||current==null)return false;
        int expected=voiceProgrammaticCaretLeaseEnd;
        if(expected<=0||expected!=voiceExpectedSelectionStart||expected!=voiceExpectedSelectionEnd)return false;
        if(voiceOwnedEnd!=expected||current.selectionStart!=current.selectionEnd
                ||current.selectionStart!=expected-1)return false;
        long now=android.os.SystemClock.uptimeMillis();
        if(now>voiceProgrammaticCaretLeaseUntilUptime)return false;
        if(SendAccessibilityService.userTouchGeneration()>voiceProgrammaticCaretTouchGeneration)return false;
        int[] region=locatePublishedVoiceRegion(current);
        if(region==null||region[1]!=expected)return false;

        programmaticSelectionEditDepth++;
        try{
            if(!ic.setSelection(expected,expected))return false;
            voiceSelectionFollowsOwnedRange=true;
            voiceExpectedSelectionStart=expected;
            voiceExpectedSelectionEnd=expected;
            rememberProgrammaticSelection();
            voiceProgrammaticCaretLeaseUntilUptime=now+300L;
            return true;
        }catch(Exception ignored){
            return false;
        }finally{
            programmaticSelectionEditDepth=Math.max(0,programmaticSelectionEditDepth-1);
        }
    }

    @Override public void onUpdateSelection(int oldSelStart, int oldSelEnd, int newSelStart, int newSelEnd, int candidatesStart, int candidatesEnd) {
        super.onUpdateSelection(oldSelStart, oldSelEnd, newSelStart, newSelEnd, candidatesStart, candidatesEnd);
        if(!running||newSelStart<0||newSelEnd<newSelStart)return;
        if(programmaticSelectionEditDepth>0)return;
        if(newSelStart==voiceExpectedSelectionStart&&newSelEnd==voiceExpectedSelectionEnd)return;

        final long runId=activeVoiceRunId;
        main.post(()->{
            if(!voiceRunActive(runId)||programmaticSelectionEditDepth>0)return;
            InputConnection ic=boundConnection;
            if(ic==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=ic)return;
            VoiceEditorWindow current=currentVoiceEditorWindow(ic);
            if(current==null)return;
            if(stopVoiceIfExternalComposerCleared(current))return;
            if(current.selectionStart==voiceExpectedSelectionStart&&current.selectionEnd==voiceExpectedSelectionEnd)return;
            if(healTransientVoiceEndMinusOne(ic,current,runId))return;
            beginVoiceCaretCutover(current.selectionStart,current.selectionEnd,runId,current);
        });
    }

'''
s = replace_region(
    s,
    '    @Override public void onUpdateSelection(',
    '    private long selectionKey(',
    selection_methods,
    'narrow delayed-selection self-heal',
)

# A genuine user cutover invalidates the programmatic lease. If the new caret is a
# collapsed caret at the actual end of non-whitespace text, arm exactly one
# persistent segment prefix. No text is changed here.
s = rep(
    s,
    '''        clearVoiceCaretRebaseCandidate();\n        livePartialTail="";hasComposingTail=false;\n''',
    '''        voiceProgrammaticCaretLeaseUntilUptime=0L;\n        voiceProgrammaticCaretLeaseEnd=-1;\n        voiceProjectionPrefix="";\n        if(targetStart==targetEnd&&rs==window.text.length()&&rs>0\n                &&!Character.isWhitespace(window.text.charAt(rs-1)))\n            voiceProjectionPrefix=" ";\n        clearVoiceCaretRebaseCandidate();\n        livePartialTail="";hasComposingTail=false;\n''',
    'cutover boundary separator without editor mutation',
)

# Real caret cutovers rotate only the speech transport. Prefer the broker's
# already-warm single-use credential, mirroring the proven v1.42 microphone-return
# path; otherwise fall back to the normal broker probe/watchdog.
restart = r'''    private void restartSpeechTransportForCaretCutover(long runId){
        if(!voiceRunActive(runId)||completed||stopRequested)return;
        WebSocket old;
        synchronized(audioLock){
            if(!voiceRunActive(runId))return;
            speechRecovering=true;
            sonioxReady=false;
            finishSent=false;
            finishAckEpoch++;
            pendingAudio.clear();pendingBytes=0;
            old=webSocket;
            webSocket=null;
        }
        if(old!=null)try{old.cancel();}catch(Exception ignored){}
        awaitingCredential=true;
        credentialAttempt=0;
        retryAfterPageLoad=false;
        lastCredentialError="";
        activeCredentialRequestId=0L;
        final int epoch=++speechRecoveryEpoch;

        String warm=consumeWarmCredential();
        if(warm!=null){
            awaitingCredential=false;
            pageReady=true;
            startSoniox(warm,runId);
            main.postDelayed(PersianKeyboardService.this::prefetchWarmCredential,500L);
            return;
        }

        armCredentialWatchdog();
        ensureCredentialWebView();
        if(brokerPageLoaded)requestCredential(runId);
        else retryAfterPageLoad=true;
        main.postDelayed(()->{
            if(!voiceRunActive(runId)||completed||stopRequested
                    ||epoch!=speechRecoveryEpoch||!speechRecovering||!awaitingCredential)return;
            ensureCredentialWebView();
            if(brokerPageLoaded){
                retryAfterPageLoad=false;
                requestCredential(runId);
            }else{
                retryAfterPageLoad=true;
            }
        },2500L);
    }

'''
s = replace_region(
    s,
    '    private void restartSpeechTransportForCaretCutover(long runId){',
    '    private void noteVoicePublicationPaused(long runId){',
    restart,
    'warm-credential true-caret transport restart',
)

if 'versionCode 53' not in g or "versionName '1.43'" not in g:
    raise SystemExit('v1.44 patch: expected v1.43 Gradle version markers missing')
g = g.replace('versionCode 53','versionCode 54',1)
g = g.replace("versionName '1.43'","versionName '1.44'",1)

text = s + '\n' + g
required = [
    'private long voiceProgrammaticCaretLeaseUntilUptime;',
    'private int voiceProgrammaticCaretLeaseEnd = -1;',
    'private String voiceProjectionPrefix = "";',
    'ViewGroup.LayoutParams.MATCH_PARENT, weight',
    'b.setBackground(keyStateBackground(action));',
    'boolean multiline=(inputType&InputType.TYPE_TEXT_FLAG_MULTI_LINE)!=0;',
    'if(ic.commitText("\\n",1))return;',
    'private String withVoiceProjectionPrefix(String segment){',
    'desired=withVoiceProjectionPrefix(',
    'private boolean healTransientVoiceEndMinusOne(',
    'current.selectionStart!=expected-1',
    'SendAccessibilityService.userTouchGeneration()>voiceProgrammaticCaretTouchGeneration',
    'if(healTransientVoiceEndMinusOne(ic,current,runId))return;',
    'voiceProgrammaticCaretLeaseUntilUptime=android.os.SystemClock.uptimeMillis()+1200L;',
    'voiceProjectionPrefix=" ";',
    'String warm=consumeWarmCredential();',
    'ensureCredentialWebView();',
    'layer=Layer.ALPHA;shift=false;',
    'versionCode 54',
    "versionName '1.44'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.44 patch: required invariant missing: {needle}')

for forbidden in [
    'new LinearLayout.LayoutParams(0, keyHeightPx(), weight);',
    'lp.setMargins(dp(2),dp(1),dp(2),dp(1));',
    'versionCode 53',
    "versionName '1.43'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.44 patch: forbidden old invariant remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.44 cursor/newline/touch hardening patch')
