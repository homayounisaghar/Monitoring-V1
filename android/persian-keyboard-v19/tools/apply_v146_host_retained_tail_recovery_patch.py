from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.46 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


# Device v1.45 diagnostic evidence:
#   len=29 sel=26:26 owned=0:26 expected=26:26 follow=true
# followed repeatedly by V145 PUB_PAUSE region-null.
#
# That is not an end-minus-one selection callback. The caret is exactly where the
# IME expects it, but the host retains a short stale suffix to the RIGHT of the
# caret after a live partial rewrite. Strict locatePublishedVoiceRegion() then
# cannot prove ownership and pauses publication forever.
#
# v1.46 repairs only this programmatic-follow state. It requires:
# - live run;
# - collapsed selection exactly at the expected voice end;
# - follow mode still true;
# - same short publication lease;
# - no newer accessibility touch generation;
# - a boundary-proved voice segment beginning at the same owned start;
# - a small right-side excess (<= 32 UTF-16 units).
#
# First choice is minimal: if text before the cursor ends with the current desired
# voice suffix, delete only the retained after-cursor tail. If the host also
# normalized/revised the owned segment, a bounded similarity proof permits
# canonicalizing ONLY the boundary-owned voice segment. No unrelated editor text
# or user-moved selection is touched.

helpers = r'''    private boolean voiceDesiredSuffixMatchesBeforeCursor(
            InputConnection ic,String desired,int ownedStart,int expectedEnd){
        if(ic==null||desired==null||desired.isEmpty())return false;
        if(expectedEnd-ownedStart!=desired.length())return false;
        int guardLen=Math.min(128,desired.length());
        String guard=desired.substring(desired.length()-guardLen);
        try{
            CharSequence beforeCs=ic.getTextBeforeCursor(guardLen,0);
            if(beforeCs==null)return false;
            String before=beforeCs.toString();
            if(before.endsWith(guard))return true;
            String ng=normalizeVoiceOwnedText(guard);
            return !ng.isEmpty()&&normalizeVoiceOwnedText(before).endsWith(ng);
        }catch(Exception ignored){
            return false;
        }
    }

    private boolean voiceRegionLooksLikeHostRewrite(String actual,String expected){
        if(actual==null||expected==null||expected.isEmpty())return false;
        String a=normalizeVoiceOwnedText(actual);
        String e=normalizeVoiceOwnedText(expected);
        if(a.equals(e))return true;
        int delta=Math.abs(a.length()-e.length());
        if(delta>32)return false;
        int shorter=Math.min(a.length(),e.length());
        if(shorter<8)return false;
        int prefix=commonPrefixChars(a,e);
        int suffix=0;
        while(suffix<shorter-prefix
                &&a.charAt(a.length()-1-suffix)==e.charAt(e.length()-1-suffix))suffix++;
        return prefix+suffix>=Math.max(8,(shorter*3)/4);
    }

    private boolean recoverHostRetainedVoiceTail(
            InputConnection ic,VoiceEditorWindow window,String desired,String partial,
            int finalChars,boolean finish,long runId){
        if(!voiceRunActive(runId)||ic==null||window==null||desired==null)return false;
        if(!voiceSelectionFollowsOwnedRange)return false;
        if(window.selectionStart!=window.selectionEnd)return false;
        int expected=voiceExpectedSelectionEnd;
        if(expected<0||voiceExpectedSelectionStart!=expected||voiceOwnedEnd!=expected)return false;
        if(window.selectionStart!=expected)return false;
        long now=android.os.SystemClock.uptimeMillis();
        if(now>voiceProgrammaticCaretLeaseUntilUptime)return false;
        if(SendAccessibilityService.userTouchGeneration()>voiceProgrammaticCaretTouchGeneration)return false;

        int[] boundary=locateVoiceOwnedRegion(window);
        if(boundary==null||boundary[0]!=voiceOwnedStart)return false;
        if(boundary[1]<=expected)return false;
        int retained=boundary[1]-expected;
        if(retained<=0||retained>32)return false;
        if(expected-boundary[0]!=desired.length())return false;

        boolean batch=false;boolean ok=false;
        programmaticSelectionEditDepth++;
        try{
            batch=ic.beginBatchEdit();
            if(voiceDesiredSuffixMatchesBeforeCursor(ic,desired,boundary[0],expected)){
                // Chrome/WebView can report commit success while retaining a few
                // chars from the prior partial to the right of the cursor.
                if(!ic.deleteSurroundingText(0,retained))return false;
                if(!ic.setSelection(expected,expected))return false;
                diag("V146 STALE_TAIL_DELETE retained="+retained+" expected="+expected+
                        " run="+runId+" pkg="+diagPackage());
            }else{
                String actual=window.text.substring(boundary[2],boundary[3]);
                if(!voiceRegionLooksLikeHostRewrite(actual,desired))return false;
                if(!ic.setSelection(boundary[0],boundary[1]))return false;
                if(!ic.commitText(desired,1))return false;
                int newEnd=boundary[0]+desired.length();
                if(!ic.setSelection(newEnd,newEnd))return false;
                expected=newEnd;
                diag("V146 OWNED_SEGMENT_CANONICALIZE excess="+retained+
                        " newEnd="+newEnd+" run="+runId+" pkg="+diagPackage());
            }

            voicePublishedText=desired;
            voiceOwnedStart=boundary[0];
            voiceOwnedEnd=expected;
            voiceSelectionFollowsOwnedRange=true;
            voiceExpectedSelectionStart=expected;
            voiceExpectedSelectionEnd=expected;
            voiceProgrammaticCaretLeaseEnd=expected;
            voiceProgrammaticCaretLeaseUntilUptime=now+1500L;
            voiceProgrammaticCaretTouchGeneration=SendAccessibilityService.userTouchGeneration();
            committedFinalChars=finalChars;
            livePartialTail=finish?"":partial;
            hasComposingTail=false;
            voiceExternalClearStopArmed=(window.text.length()-(boundary[3]-boundary[2])+desired.length())>0;
            rememberProgrammaticSelection();
            ok=true;
            return true;
        }catch(Exception ignored){
            return false;
        }finally{
            if(batch)try{ic.endBatchEdit();}catch(Exception ignored){}
            programmaticSelectionEditDepth=Math.max(0,programmaticSelectionEditDepth-1);
            if(ok)clearVoicePublicationPaused(runId);
        }
    }

'''

marker = '    private boolean voicePrefixProvesTransientEndMinusOne('
if marker not in s:
    raise SystemExit('v1.46 patch: v1.45 helper marker missing')
s = s.replace(marker, helpers + marker, 1)

old_region = r'''            int[] region=locatePublishedVoiceRegion(window);
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
new_region = r'''            int[] region=locatePublishedVoiceRegion(window);
            if(region==null){
                if(stopVoiceIfExternalComposerCleared(window))return;
                if(recoverHostRetainedVoiceTail(
                        ic,window,desired,partial,finalChars,finish,runId))return;
                // If the host snapshot is still stale immediately after the
                // repaired selection, give it one main-loop turn instead of
                // entering the persistent paused state.
                if(repairedEndMinusOne){
                    final boolean retryFinish=finish;
                    main.postDelayed(()->publish(retryFinish,runId),35L);
                    return;
                }
                diagCurrentEditor("V146 PUB_PAUSE region-null");
                noteVoicePublicationPaused(runId);return;
            }
'''
s = rep(s, old_region, new_region, 'recover retained tail before publication pause')

if 'versionCode 55' not in g or "versionName '1.45'" not in g:
    raise SystemExit('v1.46 patch: expected v1.45 Gradle markers missing')
g = g.replace('versionCode 55','versionCode 56',1)
g = g.replace("versionName '1.45'","versionName '1.46'",1)

text=s+'\n'+g
required=[
    'private boolean recoverHostRetainedVoiceTail(',
    'private boolean voiceDesiredSuffixMatchesBeforeCursor(',
    'private boolean voiceRegionLooksLikeHostRewrite(',
    'ic.deleteSurroundingText(0,retained)',
    'boundary[1]-expected',
    'retained>32',
    'SendAccessibilityService.userTouchGeneration()>voiceProgrammaticCaretTouchGeneration',
    'if(recoverHostRetainedVoiceTail(',
    'diag("V146 STALE_TAIL_DELETE retained="',
    'diag("V146 OWNED_SEGMENT_CANONICALIZE excess="',
    'diagCurrentEditor("V146 PUB_PAUSE region-null");',
    'versionCode 56',
    "versionName '1.46'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.46 patch: required invariant missing: {needle}')

for forbidden in [
    'diagCurrentEditor("V145 PUB_PAUSE region-null");',
    'versionCode 55',
    "versionName '1.45'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.46 patch: forbidden v1.45 frontier remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.46 host-retained stale-tail recovery patch')
