from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.45 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


def replace_region(text, start_marker, end_marker, replacement, label):
    start = text.find(start_marker)
    end = text.find(end_marker, start + len(start_marker)) if start >= 0 else -1
    if start < 0 or end < 0:
        raise SystemExit(f'v1.45 patch: missing region: {label}')
    return text[:start] + replacement + text[end:]


# Device evidence from v1.44:
# the user still sees the caret settle one UTF-16 unit before the live voice end,
# followed by "Recording — live text sync paused". v1.44's recovery still called
# locatePublishedVoiceRegion() before moving the caret. Some host InputConnections
# do not expose the one character after the cursor in their immediate snapshot,
# so the proof function failed for exactly the state it was meant to repair.
#
# v1.45 proves the same narrow end-1 case from the *before-cursor* prefix only.
# It never reads/logs user text, never broadens to arbitrary selection rebasing,
# and still requires the short IME-owned publication lease plus no newer touch.
# The publisher also runs this repair before deciding viewport-follow ownership,
# so a transient host drift cannot permanently disable follow mode.

heal = r'''    private boolean voicePrefixProvesTransientEndMinusOne(
            InputConnection ic,VoiceEditorWindow current){
        if(ic==null||current==null)return false;
        int expected=voiceProgrammaticCaretLeaseEnd;
        if(expected<=0||expected!=voiceExpectedSelectionStart||expected!=voiceExpectedSelectionEnd)return false;
        if(voiceOwnedEnd!=expected||current.selectionStart!=current.selectionEnd
                ||current.selectionStart!=expected-1)return false;
        long now=android.os.SystemClock.uptimeMillis();
        if(now>voiceProgrammaticCaretLeaseUntilUptime)return false;
        if(SendAccessibilityService.userTouchGeneration()>voiceProgrammaticCaretTouchGeneration)return false;

        String published=voicePublishedText==null?"":voicePublishedText;
        int missing=expected-current.selectionStart;
        int prefixLen=published.length()-missing;
        if(missing!=1||prefixLen<=0)return false;
        int guardLen=Math.min(96,prefixLen);
        String guard=published.substring(prefixLen-guardLen,prefixLen);
        try{
            CharSequence beforeCs=ic.getTextBeforeCursor(guardLen,0);
            if(beforeCs==null)return false;
            String before=beforeCs.toString();
            if(before.endsWith(guard))return true;
            String normalizedGuard=normalizeVoiceOwnedText(guard);
            if(normalizedGuard.isEmpty())return false;
            return normalizeVoiceOwnedText(before).endsWith(normalizedGuard);
        }catch(Exception ignored){
            return false;
        }
    }

    private boolean healTransientVoiceEndMinusOne(
            InputConnection ic,VoiceEditorWindow current,long runId){
        if(!voiceRunActive(runId))return false;
        if(!voicePrefixProvesTransientEndMinusOne(ic,current))return false;
        int expected=voiceProgrammaticCaretLeaseEnd;
        long now=android.os.SystemClock.uptimeMillis();

        programmaticSelectionEditDepth++;
        try{
            if(!ic.setSelection(expected,expected))return false;
            voiceSelectionFollowsOwnedRange=true;
            voiceExpectedSelectionStart=expected;
            voiceExpectedSelectionEnd=expected;
            rememberProgrammaticSelection();
            voiceProgrammaticCaretLeaseUntilUptime=now+350L;
            diag("V145 END_MINUS_ONE_HEAL expected="+expected+" run="+runId+
                    " pkg="+diagPackage());
            return true;
        }catch(Exception ignored){
            return false;
        }finally{
            programmaticSelectionEditDepth=Math.max(0,programmaticSelectionEditDepth-1);
        }
    }

'''
s = replace_region(
    s,
    '    private boolean healTransientVoiceEndMinusOne(',
    '    @Override public void onUpdateSelection(',
    heal,
    'prefix-proved end-minus-one repair',
)

# Refresh the lease slightly longer than v1.44; it is still short and still gated
# by the exact end-1 shape and no newer user touch.
s = rep(
    s,
    'voiceProgrammaticCaretLeaseUntilUptime=android.os.SystemClock.uptimeMillis()+1200L;',
    'voiceProgrammaticCaretLeaseUntilUptime=android.os.SystemClock.uptimeMillis()+1500L;',
    'extend narrow publication lease',
)

old_window = r'''            VoiceEditorWindow window=currentVoiceEditorWindow(ic);
            if(window==null){noteVoicePublicationPaused(runId);return;}
            int[] region=locatePublishedVoiceRegion(window);
            if(region==null){
                if(stopVoiceIfExternalComposerCleared(window))return;
                noteVoicePublicationPaused(runId);return;
            }
'''
new_window = r'''            VoiceEditorWindow window=currentVoiceEditorWindow(ic);
            if(window==null){noteVoicePublicationPaused(runId);return;}

            // Repair the exact host end-1 drift before it can make v1.36 drop
            // voiceSelectionFollowsOwnedRange. This proof intentionally does not
            // require after-cursor visibility.
            boolean repairedEndMinusOne=healTransientVoiceEndMinusOne(ic,window,runId);
            if(repairedEndMinusOne){
                window=currentVoiceEditorWindow(ic);
                if(window==null){
                    final boolean retryFinish=finish;
                    main.postDelayed(()->publish(retryFinish,runId),35L);
                    return;
                }
            }

            int[] region=locatePublishedVoiceRegion(window);
            if(region==null){
                if(stopVoiceIfExternalComposerCleared(window))return;
                // If the host snapshot is still stale immediately after the
                // repaired selection, give it one main-loop turn instead of
                // entering the persistent paused state.
                if(repairedEndMinusOne){
                    final boolean retryFinish=finish;
                    main.postDelayed(()->publish(retryFinish,runId),35L);
                    return;
                }
                diagCurrentEditor("V145 PUB_PAUSE region-null");
                noteVoicePublicationPaused(runId);return;
            }
'''
s = rep(s, old_window, new_window, 'publisher-side end-minus-one repair before follow decision')

if 'versionCode 54' not in g or "versionName '1.44'" not in g:
    raise SystemExit('v1.45 patch: expected v1.44 Gradle markers missing')
g = g.replace('versionCode 54','versionCode 55',1)
g = g.replace("versionName '1.44'","versionName '1.45'",1)

text=s+'\n'+g
required=[
    'private boolean voicePrefixProvesTransientEndMinusOne(',
    'current.selectionStart!=expected-1',
    'ic.getTextBeforeCursor(guardLen,0)',
    'normalizeVoiceOwnedText(before).endsWith(normalizedGuard)',
    'diag("V145 END_MINUS_ONE_HEAL expected="',
    'boolean repairedEndMinusOne=healTransientVoiceEndMinusOne(ic,window,runId);',
    'main.postDelayed(()->publish(retryFinish,runId),35L);',
    'diagCurrentEditor("V145 PUB_PAUSE region-null");',
    'voiceProgrammaticCaretLeaseUntilUptime=android.os.SystemClock.uptimeMillis()+1500L;',
    'versionCode 55',
    "versionName '1.45'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.45 patch: required invariant missing: {needle}')

for forbidden in [
    'int[] region=locatePublishedVoiceRegion(current);\n        if(region==null||region[1]!=expected)return false;',
    'versionCode 54',
    "versionName '1.44'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.45 patch: forbidden v1.44 recovery remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.45 prefix-proved publisher end-minus-one recovery patch')
