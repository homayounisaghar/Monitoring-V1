from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.34 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


# v1.33 real-device evidence showed that cursor/tail recovery is still not a
# durable ownership model: the bounded retry can end in "live text sync lost"
# even when the user has not touched the editor. v1.34 therefore captures the
# immutable text boundaries immediately surrounding the insertion point when
# voice starts. Recovery can then identify and canonicalize only the region
# between those boundaries, independent from the editor's transient caret.
#
# The v1.33 fast-key path is retained. This patch only adds visual pressed-state
# feedback by darkening the key while it is physically pressed; hit targets and
# ACTION_DOWN dispatch are unchanged.

s = rep(s,
'''import android.graphics.drawable.InsetDrawable;\n''',
'''import android.graphics.drawable.InsetDrawable;\nimport android.graphics.drawable.StateListDrawable;\n''',
    'StateListDrawable import')

s = rep(s,
'''    private int liveSyncRecoveryEpoch;\n    private long liveSyncFailureSince;\n''',
'''    private int liveSyncRecoveryEpoch;\n    private long liveSyncFailureSince;\n    private String voiceLeftBoundary = "";\n    private String voiceRightBoundary = "";\n    private boolean voiceBoundaryCaptured;\n    private boolean voiceBoundaryOwnsWholeField;\n''',
    'voice insertion-boundary state')

s = rep(s,
'''        b.setBackground(new InsetDrawable(round(action?ACTION:KEY,dp(8)),dp(2),dp(1),dp(2),dp(1)));\n        return b;\n    }\n\n    private boolean containsPersian(String s) {\n''',
'''        b.setBackground(keyStateBackground(action));\n        return b;\n    }\n\n    private StateListDrawable keyStateBackground(boolean action){\n        StateListDrawable states=new StateListDrawable();\n        int pressed=action?0xFFC5CAD4:0xFFD0D0D5;\n        states.addState(new int[]{android.R.attr.state_pressed},\n                new InsetDrawable(round(pressed,dp(8)),dp(2),dp(1),dp(2),dp(1)));\n        states.addState(new int[]{},\n                new InsetDrawable(round(action?ACTION:KEY,dp(8)),dp(2),dp(1),dp(2),dp(1)));\n        return states;\n    }\n\n    private boolean containsPersian(String s) {\n''',
    'pressed-state key feedback')

s = rep(s,
'''        boundConnection=ic; activeGeneration=inputGeneration;\n        synchronized(textLock){finalTranscript.setLength(0);finalTokenIds.clear();partialTranscript="";}\n''',
'''        boundConnection=ic; activeGeneration=inputGeneration;\n        captureVoiceInsertionBoundary();\n        synchronized(textLock){finalTranscript.setLength(0);finalTokenIds.clear();partialTranscript="";}\n''',
    'capture insertion boundary at voice start')

old_guard = r'''    private String ownedVoiceRecoveryGuard(){
        synchronized(textLock){
            String allFinal=finalTranscript.toString();
            int committed=Math.max(0,Math.min(committedFinalChars,allFinal.length()));
            String visible=allFinal.substring(0,committed)+(livePartialTail==null?"":livePartialTail);
            int n=Math.min(80,visible.length());
            return n<=0?"":visible.substring(visible.length()-n);
        }
    }

'''

new_guard = r'''    private String ownedVoiceVisibleText(){
        synchronized(textLock){
            String allFinal=finalTranscript.toString();
            int committed=Math.max(0,Math.min(committedFinalChars,allFinal.length()));
            return allFinal.substring(0,committed)+(livePartialTail==null?"":livePartialTail);
        }
    }

    private String ownedVoiceRecoveryGuard(){
        String visible=ownedVoiceVisibleText();
        int n=Math.min(80,visible.length());
        return n<=0?"":visible.substring(visible.length()-n);
    }

    private void captureVoiceInsertionBoundary(){
        voiceLeftBoundary="";
        voiceRightBoundary="";
        voiceBoundaryCaptured=false;
        voiceBoundaryOwnsWholeField=false;
        InputConnection ic=boundConnection;
        if(ic==null)return;
        try{
            CharSequence beforeCs=ic.getTextBeforeCursor(96,0);
            CharSequence selectedCs=ic.getSelectedText(0);
            CharSequence afterCs=ic.getTextAfterCursor(96,0);
            String before=beforeCs==null?"":beforeCs.toString();
            String selected=selectedCs==null?"":selectedCs.toString();
            String after=afterCs==null?"":afterCs.toString();
            int leftKeep=Math.min(48,before.length());
            int rightKeep=Math.min(48,after.length());
            voiceLeftBoundary=before.substring(before.length()-leftKeep);
            voiceRightBoundary=after.substring(0,rightKeep);

            // Empty editor and genuine select-all are the only cases where no
            // external left/right boundary is required to prove whole-field
            // ownership. Cross-check with ExtractedText so unsupported surrounding
            // text APIs do not accidentally grant whole-field ownership.
            if(before.isEmpty()&&after.isEmpty()){
                try{
                    android.view.inputmethod.ExtractedTextRequest req=new android.view.inputmethod.ExtractedTextRequest();
                    android.view.inputmethod.ExtractedText et=ic.getExtractedText(req,0);
                    if(et!=null&&et.text!=null){
                        int selectedLen=(et.selectionStart>=0&&et.selectionEnd>=et.selectionStart)
                                ?et.selectionEnd-et.selectionStart:selected.length();
                        voiceBoundaryOwnsWholeField=et.text.length()==0||selectedLen==et.text.length();
                    }
                }catch(Exception ignored){}
            }
            voiceBoundaryCaptured=true;
        }catch(Exception ignored){}
    }

    private static final class VoiceEditorWindow{
        final String text;
        final int absoluteStart;
        VoiceEditorWindow(String text,int absoluteStart){this.text=text;this.absoluteStart=absoluteStart;}
    }

    private VoiceEditorWindow currentVoiceEditorWindow(InputConnection ic){
        if(ic==null)return null;
        try{
            android.view.inputmethod.ExtractedTextRequest req=new android.view.inputmethod.ExtractedTextRequest();
            android.view.inputmethod.ExtractedText et=ic.getExtractedText(req,0);
            if(et==null||et.selectionStart<0||et.selectionEnd<et.selectionStart)return null;
            int absStart=et.startOffset+et.selectionStart;
            int absEnd=et.startOffset+et.selectionEnd;
            CharSequence beforeCs=ic.getTextBeforeCursor(65536,0);
            CharSequence selectedCs=ic.getSelectedText(0);
            CharSequence afterCs=ic.getTextAfterCursor(65536,0);
            String before=beforeCs==null?"":beforeCs.toString();
            String selected=selectedCs==null?"":selectedCs.toString();
            String after=afterCs==null?"":afterCs.toString();
            if(selected.isEmpty()&&absEnd>absStart&&et.text!=null
                    &&et.selectionStart<=et.text.length()&&et.selectionEnd<=et.text.length()){
                selected=et.text.subSequence(et.selectionStart,et.selectionEnd).toString();
            }
            return new VoiceEditorWindow(before+selected+after,absStart-before.length());
        }catch(Exception ignored){
            return null;
        }
    }

    private int uniqueBoundaryIndex(String text,String anchor){
        if(text==null||anchor==null||anchor.isEmpty())return -1;
        int first=text.indexOf(anchor);
        return first>=0&&first==text.lastIndexOf(anchor)?first:-1;
    }

    private int[] locateVoiceOwnedRegion(VoiceEditorWindow window){
        if(!voiceBoundaryCaptured||window==null)return null;
        int startRel;
        int endRel;
        if(!voiceLeftBoundary.isEmpty()){
            int left=uniqueBoundaryIndex(window.text,voiceLeftBoundary);
            if(left<0)return null;
            startRel=left+voiceLeftBoundary.length();
        }else if(voiceBoundaryOwnsWholeField||!voiceRightBoundary.isEmpty()){
            startRel=0;
        }else return null;

        if(!voiceRightBoundary.isEmpty()){
            int right=uniqueBoundaryIndex(window.text,voiceRightBoundary);
            if(right<0)return null;
            endRel=right;
        }else if(voiceBoundaryOwnsWholeField||!voiceLeftBoundary.isEmpty()){
            endRel=window.text.length();
        }else return null;

        if(startRel<0||endRel<startRel||endRel>window.text.length())return null;
        return new int[]{window.absoluteStart+startRel,window.absoluteStart+endRel,startRel,endRel};
    }

    private String normalizeVoiceOwnedText(String in){
        if(in==null||in.isEmpty())return "";
        StringBuilder out=new StringBuilder(in.length());
        boolean pendingSpace=false;
        for(int i=0;i<in.length();i++){
            char c=in.charAt(i);
            if(c=='\u200E'||c=='\u200F'||c=='\u202A'||c=='\u202B'||c=='\u202C'||c=='\u2066'||c=='\u2067'||c=='\u2069')continue;
            if(Character.isWhitespace(c)||c=='\u00A0'){
                pendingSpace=out.length()>0;
                continue;
            }
            if(pendingSpace){out.append(' ');pendingSpace=false;}
            out.append(c);
        }
        return out.toString().trim();
    }

    private boolean regionLooksVoiceOwned(String actual,String expected){
        if(actual==null||expected==null)return false;
        if(actual.equals(expected))return true;
        String a=normalizeVoiceOwnedText(actual);
        String e=normalizeVoiceOwnedText(expected);
        if(a.equals(e))return true;
        int shorter=Math.min(a.length(),e.length());
        if(shorter<8)return false;
        int prefix=commonPrefixChars(a,e);
        int suffix=0;
        while(suffix<shorter-prefix
                &&a.charAt(a.length()-1-suffix)==e.charAt(e.length()-1-suffix))suffix++;
        return prefix+suffix>=Math.max(8,(shorter*2)/3);
    }

'''

s = rep(s, old_guard, new_guard, 'replace tail-only guard with boundary ownership helpers')

old_recover = r'''    private boolean recoverOwnedVoiceCursor(){
        if(!running||hasRecentEditorUserInteraction())return false;
        InputConnection ic=boundConnection;
'''
new_recover = r'''    private boolean recoverOwnedVoiceCursor(){
        if(!running||hasRecentEditorUserInteraction())return false;
        if(recoverVoiceBoundaryOwnership())return true;
        InputConnection ic=boundConnection;
'''
s = rep(s, old_recover, new_recover, 'boundary recovery precedes cursor recovery')

marker = r'''    private boolean recoverOwnedVoiceCursor(){
'''
if marker not in s:
    raise SystemExit('v1.34 patch: missing recoverOwnedVoiceCursor marker')
insert_at=s.index(marker)
boundary_recover = r'''    private boolean recoverVoiceBoundaryOwnership(){
        if(!running||hasRecentEditorUserInteraction()||!voiceBoundaryCaptured)return false;
        InputConnection ic=boundConnection;
        if(ic==null||getCurrentInputConnection()!=ic)return false;
        String expected=ownedVoiceVisibleText();
        if(expected.isEmpty())return false;
        VoiceEditorWindow window=currentVoiceEditorWindow(ic);
        int[] region=locateVoiceOwnedRegion(window);
        if(window==null||region==null)return false;
        int start=region[0];
        int end=region[1];
        String actual=window.text.substring(region[2],region[3]);

        // First try the cheapest repair: move only the selection to the proven
        // end of the owned insertion region. This fixes pure caret drift without
        // rewriting any text.
        if(setRecoverySelection(ic,end,end)){
            String guard=ownedVoiceRecoveryGuard();
            if(editorEndsWithLiveTail()&&(guard.isEmpty()||cursorEndsWithGuard(ic,guard)))return true;
        }

        // If WebView normalized the owned text itself, boundary proof lets us
        // repair only that insertion region. Require substantial agreement with
        // the IME's own text before canonicalizing; never overwrite an unrelated
        // region merely because selection moved.
        if(!regionLooksVoiceOwned(actual,expected))return false;
        boolean batch=false;
        programmaticSelectionEditDepth++;
        try{
            batch=ic.beginBatchEdit();
            if(!ic.setSelection(start,end))return false;
            if(!ic.commitText(expected,1))return false;
        }catch(Exception ignored){
            return false;
        }finally{
            if(batch)try{ic.endBatchEdit();}catch(Exception ignored){}
            rememberProgrammaticSelection();
            programmaticSelectionEditDepth=Math.max(0,programmaticSelectionEditDepth-1);
        }
        String guard=ownedVoiceRecoveryGuard();
        return editorEndsWithLiveTail()&&(guard.isEmpty()||cursorEndsWithGuard(ic,guard));
    }

'''
s=s[:insert_at]+boundary_recover+s[insert_at:]

if 'versionCode 43' not in g or "versionName '1.33'" not in g:
    raise SystemExit('v1.34 patch: expected v1.33 version markers missing')
g=g.replace('versionCode 43','versionCode 44',1)
g=g.replace("versionName '1.33'","versionName '1.34'",1)

text=s+'\n'+g
required=[
    'import android.graphics.drawable.StateListDrawable;',
    'private String voiceLeftBoundary = "";',
    'private String voiceRightBoundary = "";',
    'private boolean voiceBoundaryCaptured;',
    'private boolean voiceBoundaryOwnsWholeField;',
    'private StateListDrawable keyStateBackground(boolean action){',
    'android.R.attr.state_pressed',
    'captureVoiceInsertionBoundary();',
    'private String ownedVoiceVisibleText(){',
    'private static final class VoiceEditorWindow{',
    'getTextBeforeCursor(65536,0)',
    'private int[] locateVoiceOwnedRegion(VoiceEditorWindow window){',
    'private boolean regionLooksVoiceOwned(String actual,String expected){',
    'private boolean recoverVoiceBoundaryOwnership(){',
    'if(recoverVoiceBoundaryOwnership())return true;',
    'if(!ic.commitText(expected,1))return false;',
    'if(!editorEndsWithLiveTail()&&!recoverOwnedVoiceCursor())',
    'Voice stopped — live text sync lost',
    'versionCode 44',
    "versionName '1.34'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.34 patch: required invariant missing: {needle}')

for forbidden in [
    'b.setBackground(new InsetDrawable(round(action?ACTION:KEY,dp(8)),dp(2),dp(1),dp(2),dp(1)));',
    'MAX_CAPTURE_MS',
    'boundConnection.setComposingText(partial,1);',
    'versionCode 43',
    "versionName '1.33'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.34 patch: forbidden old behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.34 boundary-owned voice recovery and key feedback patch')
