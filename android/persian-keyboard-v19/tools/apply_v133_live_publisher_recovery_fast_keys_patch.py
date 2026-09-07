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
'''    private int lastProgrammaticSelectionStart=-1;
    private int lastProgrammaticSelectionEnd=-1;
    private int internalSelectionReanchorEpoch;
''',
'''    private int lastProgrammaticSelectionStart=-1;
    private int lastProgrammaticSelectionEnd=-1;
    private int internalSelectionReanchorEpoch;
    private int livePublishRecoveryEpoch;
    private int livePublishRecoveryAttempts;
    private boolean livePublishRecovering;
    private final StringBuilder manualCommitQueue = new StringBuilder();
    private InputConnection manualCommitConnection;
    private boolean manualCommitScheduled;
''', 'publisher recovery and manual commit state')

s = rep(s,
'''    private void scheduleInternalSelectionReanchor(){
        final int epoch=++internalSelectionReanchorEpoch;
        main.postDelayed(()->{
            if(epoch!=internalSelectionReanchorEpoch||!running)return;
            if(hasRecentEditorUserInteraction())return;
            if(!hasLastProgrammaticSelection||lastProgrammaticSelectionStart<0||lastProgrammaticSelectionEnd<0)return;
            InputConnection ic=boundConnection;
            if(ic==null||getCurrentInputConnection()!=ic)return;
            programmaticSelectionEditDepth++;
            try{
                ic.setSelection(lastProgrammaticSelectionStart,lastProgrammaticSelectionEnd);
                rememberProgrammaticSelection();
            }catch(Exception ignored){
            }finally{
                programmaticSelectionEditDepth=Math.max(0,programmaticSelectionEditDepth-1);
            }
        },90L);
    }
''',
'''    private void scheduleInternalSelectionReanchor(){
        scheduleLivePublishRecovery();
    }

    private void scheduleLivePublishRecovery(){
        if(!running)return;
        livePublishRecovering=true;
        updateMicUi();
        if(livePublishRecoveryAttempts>=8){
            setStatus(persian?"متن زنده متوقف شده — صدا هنوز در حال ضبط است":"Live text blocked — audio is still recording");
            return;
        }
        final int epoch=++livePublishRecoveryEpoch;
        final int attempt=++livePublishRecoveryAttempts;
        long delay=Math.min(220L,40L+(attempt*25L));
        main.postDelayed(()->{
            if(epoch!=livePublishRecoveryEpoch||!running)return;
            if(hasRecentEditorUserInteraction()){
                livePublishRecovering=false;
                updateMicUi();
                return;
            }
            InputConnection ic=boundConnection;
            if(ic==null||getCurrentInputConnection()!=ic){
                livePublishRecovering=false;
                updateMicUi();
                return;
            }
            if(hasLastProgrammaticSelection&&lastProgrammaticSelectionStart>=0&&lastProgrammaticSelectionEnd>=0){
                programmaticSelectionEditDepth++;
                try{
                    ic.setSelection(lastProgrammaticSelectionStart,lastProgrammaticSelectionEnd);
                    rememberProgrammaticSelection();
                }catch(Exception ignored){
                }finally{
                    programmaticSelectionEditDepth=Math.max(0,programmaticSelectionEditDepth-1);
                }
            }
            livePublishRecovering=false;
            updateMicUi();
            publish(false);
        },delay);
    }
''', 'make internal reanchor explicitly retry publisher')

s = rep(s,
'''    private Button charKey(String label) {
        Button b=baseKey(label,false);
        b.setOnClickListener(v -> { stopVoiceForManualInput(); commitText(label); });
        String[] vars=longPress.get(label);
        if (vars!=null) b.setOnLongClickListener(v -> { stopVoiceForManualInput(); showVariants(b,vars); return true; });
        return b;
    }
''',
'''    private Button charKey(String label) {
        Button b=baseKey(label,false);
        String[] vars=longPress.get(label);
        if(vars==null){
            b.setOnTouchListener((v,event)->{
                int action=event.getActionMasked();
                if(action==MotionEvent.ACTION_DOWN){
                    stopVoiceForManualInput();
                    v.setPressed(true);
                    commitText(label);
                    return true;
                }
                if(action==MotionEvent.ACTION_UP||action==MotionEvent.ACTION_CANCEL){
                    v.setPressed(false);
                    return true;
                }
                return true;
            });
        }else{
            final boolean[] variantOpened={false};
            final Runnable hold=()->{
                if(!b.isPressed())return;
                variantOpened[0]=true;
                stopVoiceForManualInput();
                showVariants(b,vars);
            };
            b.setOnTouchListener((v,event)->{
                int action=event.getActionMasked();
                if(action==MotionEvent.ACTION_DOWN){
                    stopVoiceForManualInput();
                    variantOpened[0]=false;
                    v.setPressed(true);
                    main.removeCallbacks(hold);
                    main.postDelayed(hold,android.view.ViewConfiguration.getLongPressTimeout());
                    return true;
                }
                if(action==MotionEvent.ACTION_UP){
                    main.removeCallbacks(hold);
                    v.setPressed(false);
                    if(!variantOpened[0])commitText(label);
                    return true;
                }
                if(action==MotionEvent.ACTION_CANCEL){
                    main.removeCallbacks(hold);
                    v.setPressed(false);
                    return true;
                }
                return true;
            });
        }
        b.setOnClickListener(v -> { stopVoiceForManualInput(); commitText(label); });
        return b;
    }
''', 'replace ordinary Button click character path with fast touch handling')

s = rep(s,
'''    private void commitText(String t){
        InputConnection ic=getCurrentInputConnection(); if(ic==null)return; try{ic.commitText(t,1); if(!persian&&shift&&!capsLock&&t.length()==1&&Character.isLetter(t.charAt(0))){shift=false;render();}}catch(Exception ignored){}
    }
''',
'''    private void commitText(String t){
        if(t==null||t.isEmpty())return;
        InputConnection ic=getCurrentInputConnection();
        if(ic==null)return;
        if(manualCommitConnection!=null&&manualCommitConnection!=ic)flushManualCommitQueue();
        manualCommitConnection=ic;
        manualCommitQueue.append(t);
        if(!manualCommitScheduled){
            manualCommitScheduled=true;
            main.postDelayed(this::flushManualCommitQueue,6L);
        }
        if(!persian&&shift&&!capsLock&&t.length()==1&&Character.isLetter(t.charAt(0))){shift=false;render();}
    }

    private void flushManualCommitQueue(){
        if(android.os.Looper.myLooper()!=android.os.Looper.getMainLooper()){
            main.post(this::flushManualCommitQueue);
            return;
        }
        manualCommitScheduled=false;
        if(manualCommitQueue.length()==0){manualCommitConnection=null;return;}
        String text=manualCommitQueue.toString();
        manualCommitQueue.setLength(0);
        InputConnection ic=manualCommitConnection;
        manualCommitConnection=null;
        if(ic==null)return;
        try{ic.commitText(text,1);}catch(Exception ignored){}
    }
''', 'tiny ordered manual commit queue')

s = rep(s,
'''    private void backspaceOnce(){
        InputConnection ic=getCurrentInputConnection(); if(ic==null)return;
''',
'''    private void backspaceOnce(){
        flushManualCommitQueue();
        InputConnection ic=getCurrentInputConnection(); if(ic==null)return;
''', 'flush queued letters before backspace')

s = rep(s,
'''            // No transcript change: do not churn the browser editor.
            if(!finish&&newFinal.isEmpty()&&partial.equals(livePartialTail))return;

            if(!editorEndsWithLiveTail()){
                // Do not mutate text if ownership cannot be proven. This remains
                // fail-closed for duplicate/deletion safety, but it must not stop
                // an otherwise healthy recording session. A later transcript
                // update can retry once the editor snapshot is coherent again.
                return;
            }

            boolean batch=false;
''',
'''            if(!editorEndsWithLiveTail()){
                scheduleLivePublishRecovery();
                return;
            }

            if(!finish&&newFinal.isEmpty()&&partial.equals(livePartialTail)){
                livePublishRecoveryEpoch++;
                livePublishRecoveryAttempts=0;
                if(livePublishRecovering){livePublishRecovering=false;updateMicUi();}
                return;
            }

            boolean batch=false;
''', 'self-heal live-tail mismatch instead of silent publisher stall')

s = rep(s,
'''                hasComposingTail=false;
            }catch(Exception e){
''',
'''                hasComposingTail=false;
                livePublishRecoveryEpoch++;
                livePublishRecoveryAttempts=0;
                if(livePublishRecovering){livePublishRecovering=false;updateMicUi();}
            }catch(Exception e){
''', 'clear publisher recovery after successful mutation')

s = rep(s,
'''internalSelectionReanchorEpoch++; voiceStartedUptime=android.os.SystemClock.uptimeMillis(); voiceStartTouchGeneration=SendAccessibilityService.userTouchGeneration(); lastEditorToolInteractionUptime=0L; sendAfterVoiceStop=false; updateMicUi();''',
'''internalSelectionReanchorEpoch++; livePublishRecoveryEpoch++; livePublishRecoveryAttempts=0; livePublishRecovering=false; voiceStartedUptime=android.os.SystemClock.uptimeMillis(); voiceStartTouchGeneration=SendAccessibilityService.userTouchGeneration(); lastEditorToolInteractionUptime=0L; sendAfterVoiceStop=false; updateMicUi();''', 'reset live publisher recovery on voice start')

s = rep(s,
'''String label=running?"🎙 "+badge():"🎙";''',
'''String label=running?(livePublishRecovering?"🎙↻ "+badge():"🎙 "+badge()):"🎙";''', 'mic label exposes live publisher recovery')
s = rep(s,
'''running?MIC_ACTIVE:0x00FFFFFF''',
'''running?(livePublishRecovering?0xFFB7791F:MIC_ACTIVE):0x00FFFFFF''', 'mic background exposes recovery state')

if 'versionCode 42' not in g or "versionName '1.32'" not in g:
    raise SystemExit('v1.33 patch: expected v1.32 version markers missing')
g = g.replace('versionCode 42', 'versionCode 43', 1)
g = g.replace("versionName '1.32'", "versionName '1.33'", 1)

text=s+'\n'+g
required=[
    'private int livePublishRecoveryEpoch;',
    'private boolean livePublishRecovering;',
    'private final StringBuilder manualCommitQueue = new StringBuilder();',
    'private void scheduleLivePublishRecovery(){',
    'Live text blocked — audio is still recording',
    'main.postDelayed(hold,android.view.ViewConfiguration.getLongPressTimeout());',
    'main.postDelayed(this::flushManualCommitQueue,6L);',
    'private void flushManualCommitQueue(){',
    'scheduleLivePublishRecovery();\n                return;',
    'livePublishRecovering?"🎙↻ "+badge()',
    'livePublishRecovering?0xFFB7791F:MIC_ACTIVE',
    'versionCode 43',
    "versionName '1.33'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.33 patch: required invariant missing: {needle}')
for forbidden in ['MAX_CAPTURE_MS','boundConnection.setComposingText(partial,1);','versionCode 42',"versionName '1.32'"]:
    if forbidden in text:
        raise SystemExit(f'v1.33 patch: forbidden old behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.33 live publisher recovery + fast key patch')
