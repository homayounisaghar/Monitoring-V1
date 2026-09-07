from pathlib import Path

p=Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
s=p.read_text()

if 'private void clearCurrentTextField(){' in s:
    print('v1.35 clear-field helper already present')
    raise SystemExit(0)

marker='    private void startSoniox(String apiKey)'
pos=s.find(marker)
if pos<0:
    raise SystemExit('v1.35 clear-field preservation: startSoniox marker missing')

method=r'''    private void clearCurrentTextField(){
        stopVoiceForManualInput();
        InputConnection ic=getCurrentInputConnection();
        if(ic==null){setStatus(persian?"فیلد متنی فعالی نیست":"No active text field");return;}
        try{
            ic.beginBatchEdit();

            boolean selectedAll=false;
            try{selectedAll=ic.performContextMenuAction(android.R.id.selectAll);}catch(Exception ignored){}
            if(selectedAll){
                CharSequence selected=null;
                try{selected=ic.getSelectedText(0);}catch(Exception ignored){}
                if(selected!=null&&selected.length()>0){
                    ic.commitText("",1);
                    ic.finishComposingText();
                    setStatus(persian?"متن پاک شد":"Text cleared");
                    return;
                }
            }

            try{
                android.view.inputmethod.ExtractedTextRequest req=new android.view.inputmethod.ExtractedTextRequest();
                android.view.inputmethod.ExtractedText et=ic.getExtractedText(req,0);
                if(et!=null&&et.text!=null&&et.text.length()>0){
                    int start=Math.max(0,et.startOffset);
                    int end=start+et.text.length();
                    if(ic.setSelection(start,end)){
                        ic.commitText("",1);
                        ic.finishComposingText();
                        setStatus(persian?"متن پاک شد":"Text cleared");
                        return;
                    }
                }
            }catch(Exception ignored){}

            CharSequence selected=null;
            try{selected=ic.getSelectedText(0);}catch(Exception ignored){}
            if(selected!=null&&selected.length()>0)ic.commitText("",1);
            CharSequence before=null,after=null;
            try{before=ic.getTextBeforeCursor(65536,0);}catch(Exception ignored){}
            try{after=ic.getTextAfterCursor(65536,0);}catch(Exception ignored){}
            int beforeCount=before==null?0:before.length();
            int afterCount=after==null?0:after.length();
            if(beforeCount>0||afterCount>0)ic.deleteSurroundingText(beforeCount,afterCount);
            ic.finishComposingText();
            setStatus(persian?"متن پاک شد":"Text cleared");
        }catch(Exception e){
            setStatus(persian?"پاک کردن متن ممکن نشد":"Unable to clear text");
        }finally{
            try{ic.endBatchEdit();}catch(Exception ignored){}
        }
    }

'''

s=s[:pos]+method+s[pos:]

for needle in [
    'private void clearCurrentTextField(){',
    'performContextMenuAction(android.R.id.selectAll)',
    'getTextBeforeCursor(65536,0)',
    'getTextAfterCursor(65536,0)',
    'stopVoiceForManualInput();',
]:
    if needle not in s:
        raise SystemExit(f'v1.35 clear-field preservation: invariant missing: {needle}')

p.write_text(s)
print('Restored v1.15 clear-field helper after v1.35 lifecycle rewrite')
