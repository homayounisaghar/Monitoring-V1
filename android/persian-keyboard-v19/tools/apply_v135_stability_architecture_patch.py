from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.35 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


def replace_region(text, start_marker, end_marker, replacement, label):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f'v1.35 patch: missing start marker: {label}')
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f'v1.35 patch: missing end marker: {label}')
    return text[:start] + replacement + text[end:]


# v1.34 real-device testing proved that the remaining instability is architectural,
# not another selection-threshold problem. Recordings share global booleans while
# WebSocket callbacks, finish-ACK timers, AudioRecord workers and credential JS
# callbacks can outlive the recording that created them. v1.35 gives each voice
# run an identity and makes every asynchronous mutation prove that identity.
#
# Editor publication is separated from speech lifetime. Same-editor selection is
# informational only: the IME never fights the user's caret and never stops healthy
# speech merely because WebView/contenteditable selection drifted. Live text owns
# and edits a proved range, temporarily selecting that range and restoring the
# user's selection afterwards.

s = rep(s,
'''    private String voiceLeftBoundary = "";\n    private String voiceRightBoundary = "";\n    private boolean voiceBoundaryCaptured;\n    private boolean voiceBoundaryOwnsWholeField;\n''',
'''    private String voiceLeftBoundary = "";\n    private String voiceRightBoundary = "";\n    private boolean voiceBoundaryCaptured;\n    private boolean voiceBoundaryOwnsWholeField;\n    private volatile long voiceRunCounter;\n    private volatile long activeVoiceRunId;\n    private volatile long credentialRequestCounter;\n    private volatile long activeCredentialRequestId;\n    private volatile int finishAckEpoch;\n    private String voicePublishedText = "";\n    private int voiceOwnedStart = -1;\n    private int voiceOwnedEnd = -1;\n    private boolean voicePublicationPaused;\n''',
    'session and range ownership state')

selection_start = '    @Override public void onUpdateSelection('
selection_end = '    private long selectionKey('
selection_method = '''    @Override public void onUpdateSelection(int oldSelStart, int oldSelEnd, int newSelStart, int newSelEnd, int candidatesStart, int candidatesEnd) {\n        super.onUpdateSelection(oldSelStart, oldSelEnd, newSelStart, newSelEnd, candidatesStart, candidatesEnd);\n        // Intentionally informational only. A real editor/focus change is handled\n        // by InputMethodService lifecycle and connection identity. A physical key\n        // still stops voice before typing, but a caret tap is never fought here.\n    }\n\n'''
s = replace_region(s, selection_start, selection_end, selection_method,
                   'replace selection causality with informational callback')

start_voice = r'''    private void startVoice(){
        if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED){setStatus("Open the app once and grant microphone permission");return;}
        if(!pageReady){setStatus("Perplexity session not ready — open the app/login once");return;}
        InputConnection ic=getCurrentInputConnection(); if(ic==null){setStatus("No active text field");return;}

        final long runId=++voiceRunCounter;
        activeVoiceRunId=runId;
        finishAckEpoch++;
        activeCredentialRequestId=0L;
        boundConnection=ic;
        activeGeneration=inputGeneration;
        captureVoiceInsertionBoundary();
        synchronized(textLock){finalTranscript.setLength(0);finalTokenIds.clear();partialTranscript="";committedFinalChars=0;hasComposingTail=false;}
        synchronized(expectedSelectionUpdates){expectedSelectionUpdates.clear();}
        resetAudio();
        running=true;stopRequested=false;completed=false;awaitingCredential=true;credentialAttempt=0;
        retryAfterPageLoad=false;lastCredentialError="";speechRecovering=false;speechRecoveryEpoch++;
        credentialWatchdogEpoch++;credentialWebViewResets=0;livePartialTail="";
        programmaticSelectionEditDepth=0;hasLastProgrammaticSelection=false;
        lastProgrammaticSelectionStart=-1;lastProgrammaticSelectionEnd=-1;
        selectionConfirmationEpoch++;selectionConfirmationPending=false;internalSelectionReanchorEpoch++;
        liveSyncRecoveryEpoch++;liveSyncFailureSince=0L;
        voiceStartedUptime=android.os.SystemClock.uptimeMillis();
        voiceStartTouchGeneration=SendAccessibilityService.userTouchGeneration();
        lastEditorToolInteractionUptime=0L;sendAfterVoiceStop=false;
        voicePublicationPaused=false;
        updateMicUi();
        setStatus(persian?"در حال ضبط — همین حالا صحبت کنید…":"Recording — speak now…");
        startAudioCapture(runId);
        armCredentialWatchdog();
        requestCredential(runId);
    }

    private void requestCredential(){requestCredential(activeVoiceRunId);}

    private void requestCredential(long runId){
        if(!voiceRunActive(runId)||!awaitingCredential||auth==null)return;
        final long requestId=++credentialRequestCounter;
        activeCredentialRequestId=requestId;
        credentialAttempt++;
        try{CookieManager.getInstance().flush();}catch(Exception ignored){}
        String js=FETCH_CREDENTIAL_JS
                .replace("__VOICE_RUN__",Long.toString(runId))
                .replace("__CRED_REQ__",Long.toString(requestId));
        auth.evaluateJavascript(js,null);
    }

'''
s = replace_region(s, '    private void startVoice(){', '    private String safeCredentialError',
                   start_voice, 'session-scoped voice start and credentials')

recovery = r'''    private boolean recoverableSonioxError(JSONObject o){
        if(o==null)return false;
        int code=o.optInt("error_code",0);
        String type=o.optString("error_type","");
        return code==408 || code>=500
                || "temp_api_key_session_expired".equals(type)
                || "max_duration_reached".equals(type)
                || "service_unavailable".equals(type)
                || "request_timeout".equals(type);
    }

    private void recoverSpeechTransport(String reason){recoverSpeechTransport(reason,activeVoiceRunId);}

    private void recoverSpeechTransport(String reason,long runId){
        if(!voiceRunActive(runId)||completed||stopRequested)return;
        synchronized(audioLock){
            if(!voiceRunActive(runId)||speechRecovering)return;
            speechRecovering=true;
            sonioxReady=false;
            finishSent=false;
            finishAckEpoch++;
        }
        WebSocket old=webSocket;
        webSocket=null;
        if(old!=null)try{old.cancel();}catch(Exception ignored){}
        synchronized(textLock){
            if(partialTranscript!=null&&!partialTranscript.isEmpty()){
                finalTranscript.append(partialTranscript);
                partialTranscript="";
            }
            finalTokenIds.clear();
        }
        publish(false,runId);
        if(!voiceRunActive(runId))return;
        awaitingCredential=true;
        credentialAttempt=0;
        retryAfterPageLoad=false;
        lastCredentialError="";
        final int epoch=++speechRecoveryEpoch;
        armCredentialWatchdog();
        main.post(()->{
            if(!voiceRunActive(runId)||completed||stopRequested||epoch!=speechRecoveryEpoch)return;
            setStatus(persian?"در حال اتصال مجدد…":"Reconnecting speech…");
            requestCredential(runId);
        });
        main.postDelayed(()->{
            if(voiceRunActive(runId)&&!completed&&!stopRequested&&speechRecovering
                    &&awaitingCredential&&epoch==speechRecoveryEpoch)requestCredential(runId);
        },2500L);
    }

'''
s = replace_region(s, '    private boolean recoverableSonioxError(JSONObject o){',
                   '    private void requestStop(){', recovery,
                   'run-scoped transport recovery')

request_stop = r'''    private void requestStop(){
        final long runId=activeVoiceRunId;
        if(!voiceRunActive(runId)||stopRequested)return;
        stopRequested=true;
        speechRecoveryEpoch++;
        finishAckEpoch++;
        setStatus(persian?"در حال نهایی‌سازی…":"Finalizing…");
        AudioRecord r=audioRecord;
        if(r!=null)try{r.stop();}catch(Exception ignored){}
        if(speechRecovering||webSocket==null){
            speechRecovering=false;
            completed=true;
            publish(true,runId);
            completeSession(persian?"تمام شد":"Done",runId);
        }
    }

'''
s = replace_region(s, '    private void requestStop(){', '    private boolean sessionStillBound()',
                   request_stop, 'run-scoped stop request')

lifecycle = r'''    private boolean voiceRunCurrent(long runId){return runId>0L&&runId==activeVoiceRunId;}
    private boolean voiceRunActive(long runId){return voiceRunCurrent(runId)&&running;}
    private boolean sessionStillBound(long runId){
        return voiceRunActive(runId)&&boundConnection!=null&&activeGeneration==inputGeneration
                &&getCurrentInputConnection()==boundConnection;
    }
    private boolean sessionStillBound(){return sessionStillBound(activeVoiceRunId);}

    private void abortForEditorChange(){abortForEditorChange("editor changed");}
    private void abortForEditorChange(String reason){
        if(!running)return;
        sendAfterVoiceStop=false;
        finishAckEpoch++;
        activeCredentialRequestId=0L;
        activeVoiceRunId=0L;
        InputConnection old=boundConnection;
        running=false;stopRequested=true;awaitingCredential=false;speechRecovering=false;speechRecoveryEpoch++;
        stopAudioRecord();clearPending();
        WebSocket ws=webSocket;webSocket=null;if(ws!=null)try{ws.cancel();}catch(Exception ignored){}
        if(old!=null)try{old.finishComposingText();}catch(Exception ignored){}
        boundConnection=null;
        final String why=(reason==null||reason.isEmpty())?"editor changed":reason;
        main.post(()->{setCollapsed(false);updateMicUi();setStatus("Voice cancelled — "+why);});
    }

    private void stopVoiceForManualInput(){
        if(!running)return;
        sendAfterVoiceStop=false;
        finishAckEpoch++;
        activeCredentialRequestId=0L;
        activeVoiceRunId=0L;
        running=false;completed=true;stopRequested=true;awaitingCredential=false;retryAfterPageLoad=false;
        speechRecovering=false;speechRecoveryEpoch++;
        backspaceHeld=false;main.removeCallbacks(backspaceRepeater);
        stopAudioRecord();clearPending();
        WebSocket ws=webSocket;webSocket=null;if(ws!=null)try{ws.cancel();}catch(Exception ignored){}
        InputConnection old=boundConnection;boundConnection=null;
        if(old!=null)try{old.finishComposingText();}catch(Exception ignored){}
        synchronized(expectedSelectionUpdates){expectedSelectionUpdates.clear();}
        hasComposingTail=false;
        updateMicUi();setStatus(readyText());
    }

'''
s = replace_region(s, '    private boolean sessionStillBound()', '    private void switchToGboard(){',
                   lifecycle, 'unified lifecycle invalidation')

soniox = r'''    private void startSoniox(String apiKey){startSoniox(apiKey,activeVoiceRunId);}

    private void startSoniox(String apiKey,long runId){
        if(!sessionStillBound(runId))return;
        setStatus(persian?"در حال اتصال به سرویس گفتار…":"Connecting speech service…");
        JSONObject c=new JSONObject();
        put(c,"api_key",apiKey);put(c,"model","stt-rt-v4");put(c,"audio_format","pcm_s16le");
        put(c,"sample_rate",SAMPLE_RATE);put(c,"num_channels",1);put(c,"enable_endpoint_detection",false);
        JSONArray h=new JSONArray();h.put(persian?"fa":"en");put(c,"language_hints",h);put(c,"language_hints_strict",true);

        final WebSocket[] holder=new WebSocket[1];
        WebSocket created=http.newWebSocket(new Request.Builder().url(SONIOX_WS).build(),new WebSocketListener(){
            @Override public void onOpen(WebSocket ws,Response response){
                if(!voiceRunActive(runId)||webSocket!=ws){ws.cancel();return;}
                if(!ws.send(c.toString())){recoverSpeechTransport("Config send error",runId);return;}
                boolean ok;
                synchronized(audioLock){
                    if(!voiceRunActive(runId)||webSocket!=ws){ws.cancel();return;}
                    sonioxReady=true;ok=flushLocked(ws);
                }
                if(!ok){recoverSpeechTransport("Audio send error",runId);return;}
                speechRecovering=false;
                main.post(()->{if(voiceRunCurrent(runId))setStatus(stopRequested?(persian?"در حال نهایی‌سازی…":"Finalizing…"):listeningText());});
                maybeFinish(runId);
            }
            @Override public void onMessage(WebSocket ws,String text){
                if(!voiceRunCurrent(runId)||webSocket!=ws)return;
                handleSoniox(runId,ws,text);
            }
            @Override public void onClosed(WebSocket ws,int code,String reason){
                if(voiceRunActive(runId)&&webSocket==ws&&!completed&&!stopRequested)
                    recoverSpeechTransport("Connection closed "+code,runId);
            }
            @Override public void onFailure(WebSocket ws,Throwable t,Response response){
                if(voiceRunActive(runId)&&webSocket==ws&&!completed&&!stopRequested)
                    recoverSpeechTransport("Connection error",runId);
            }
        });
        holder[0]=created;
        if(!voiceRunActive(runId)){created.cancel();return;}
        webSocket=created;
    }

'''
s = replace_region(s, '    private void startSoniox(String apiKey)', '    private void startAudioCapture()',
                   soniox, 'run and socket scoped Soniox listener')

audio = r'''    private void startAudioCapture(){startAudioCapture(activeVoiceRunId);}

    private void startAudioCapture(long runId){
        if(!voiceRunActive(runId))return;
        new Thread(()->{
            AudioRecord localRecorder=null;
            boolean retry=false;
            try{
                int min=AudioRecord.getMinBufferSize(SAMPLE_RATE,AudioFormat.CHANNEL_IN_MONO,AudioFormat.ENCODING_PCM_16BIT);
                if(min<=0)throw new IllegalStateException("Invalid audio buffer");
                localRecorder=new AudioRecord(MediaRecorder.AudioSource.VOICE_RECOGNITION,SAMPLE_RATE,
                        AudioFormat.CHANNEL_IN_MONO,AudioFormat.ENCODING_PCM_16BIT,Math.max(min,AUDIO_CHUNK));
                if(localRecorder.getState()!=AudioRecord.STATE_INITIALIZED)throw new IllegalStateException("AudioRecord not initialized");
                synchronized(audioLock){
                    if(!voiceRunActive(runId)){releaseRecorder(localRecorder);return;}
                    audioRecord=localRecorder;audioDone=false;
                }
                localRecorder.startRecording();
                byte[] buf=new byte[AUDIO_CHUNK];
                while(voiceRunActive(runId)&&!stopRequested){
                    int n;
                    try{n=localRecorder.read(buf,0,buf.length);}
                    catch(Exception e){if(stopRequested||!voiceRunActive(runId))break;throw e;}
                    if(!voiceRunActive(runId)||stopRequested)break;
                    if(n>0){
                        byte[] chunk=Arrays.copyOf(buf,n);
                        if(!bufferOrSend(runId,chunk)&&voiceRunActive(runId)&&!stopRequested)
                            recoverSpeechTransport("Audio send rejected",runId);
                    }else if(n<0&&!stopRequested)throw new IllegalStateException("Audio read failed");
                }
            }catch(Exception e){
                retry=voiceRunActive(runId)&&!stopRequested&&!completed;
            }finally{
                releaseOwnedRecorder(localRecorder);
            }

            if(!voiceRunCurrent(runId))return;
            if(retry){
                synchronized(audioLock){audioDone=false;}
                main.post(()->{if(voiceRunActive(runId))setStatus(persian?"در حال بازیابی میکروفون…":"Recovering microphone…");});
                main.postDelayed(()->{if(voiceRunActive(runId)&&!stopRequested&&!completed)startAudioCapture(runId);},350L);
            }else{
                synchronized(audioLock){if(voiceRunCurrent(runId))audioDone=true;}
                if(voiceRunActive(runId)&&!completed)maybeFinish(runId);
            }
        },"persian-keyboard-audio-"+runId).start();
    }

    private void releaseRecorder(AudioRecord r){
        if(r==null)return;
        try{if(r.getRecordingState()==AudioRecord.RECORDSTATE_RECORDING)r.stop();}catch(Exception ignored){}
        try{r.release();}catch(Exception ignored){}
    }

    private void releaseOwnedRecorder(AudioRecord r){
        if(r==null)return;
        synchronized(audioLock){if(audioRecord==r)audioRecord=null;}
        releaseRecorder(r);
    }

    private void queuePendingLocked(byte[] chunk){
        pendingAudio.addLast(chunk);pendingBytes+=chunk.length;
        while(pendingBytes>PREBUFFER_MAX&&pendingAudio.size()>1){byte[] d=pendingAudio.removeFirst();pendingBytes-=d.length;}
    }

    private boolean bufferOrSend(byte[] chunk){return bufferOrSend(activeVoiceRunId,chunk);}

    private boolean bufferOrSend(long runId,byte[] chunk){
        synchronized(audioLock){
            if(!voiceRunActive(runId))return true;
            WebSocket ws=webSocket;
            if(!sonioxReady||ws==null){queuePendingLocked(chunk);return true;}
            if(!flushLocked(ws)){queuePendingLocked(chunk);return false;}
            if(!ws.send(ByteString.of(chunk,0,chunk.length))){queuePendingLocked(chunk);return false;}
            return true;
        }
    }

    private boolean flushLocked(WebSocket ws){
        while(!pendingAudio.isEmpty()){
            byte[] c=pendingAudio.peekFirst();
            if(!ws.send(ByteString.of(c,0,c.length)))return false;
            pendingAudio.removeFirst();pendingBytes-=c.length;
        }
        pendingBytes=0;return true;
    }

    private void maybeFinish(){maybeFinish(activeVoiceRunId);}

    private void maybeFinish(long runId){
        WebSocket ws;
        synchronized(audioLock){
            if(!voiceRunActive(runId)||completed||finishSent||!audioDone||!sonioxReady||webSocket==null)return;
            ws=webSocket;
            if(!flushLocked(ws)){ws=null;}else{finishSent=true;}
        }
        if(ws==null){if(voiceRunActive(runId))recoverSpeechTransport("Audio send error",runId);return;}
        if(!ws.send("")){if(voiceRunActive(runId))recoverSpeechTransport("Finish send error",runId);return;}
        final WebSocket finishSocket=ws;
        final int ackEpoch=++finishAckEpoch;
        main.postDelayed(()->{
            if(!voiceRunActive(runId)||completed||ackEpoch!=finishAckEpoch||webSocket!=finishSocket)return;
            finishWithText("Done (finish ACK timeout)",runId);
        },FINISH_TIMEOUT_MS);
    }

    private void resetAudio(){
        synchronized(audioLock){pendingAudio.clear();pendingBytes=0;sonioxReady=false;audioDone=false;finishSent=false;}
    }
    private void clearPending(){
        synchronized(audioLock){pendingAudio.clear();pendingBytes=0;sonioxReady=false;finishSent=false;}
    }

'''
s = replace_region(s, '    private void startAudioCapture()', '    private void handleSoniox(String text)',
                   audio, 'run-owned audio and finish ACK')

handle = r'''    private void handleSoniox(String text){handleSoniox(activeVoiceRunId,webSocket,text);}

    private void handleSoniox(long runId,WebSocket source,String text){
        if(!voiceRunCurrent(runId)||source==null||source!=webSocket)return;
        try{
            JSONObject o=new JSONObject(text);
            if(o.has("error_code")&&!o.isNull("error_code")){
                if(recoverableSonioxError(o)){recoverSpeechTransport(o.optString("error_type","Soniox error"),runId);return;}
                finishWithText("Soniox stop "+o.optInt("error_code",0)+" / "+o.optString("error_type","unknown"),runId);
                return;
            }
            JSONArray tokens=o.optJSONArray("tokens");
            StringBuilder partial=new StringBuilder();
            if(tokens!=null){
                synchronized(textLock){
                    if(!voiceRunCurrent(runId))return;
                    for(int i=0;i<tokens.length();i++){
                        JSONObject t=tokens.optJSONObject(i);if(t==null)continue;
                        String tt=t.optString("text","");if(tt.isEmpty()||isControl(tt))continue;
                        if(t.optBoolean("is_final",false)){
                            String id=t.optLong("start_ms",-1)+"|"+t.optLong("end_ms",-1)+"|"+tt;
                            if(finalTokenIds.add(id))finalTranscript.append(tt);
                        }else partial.append(tt);
                    }
                    partialTranscript=partial.toString();
                }
                publish(false,runId);
            }
            if(o.optBoolean("finished",false)){
                if(!voiceRunCurrent(runId)||source!=webSocket)return;
                if(!stopRequested){recoverSpeechTransport("Unexpected finished",runId);return;}
                completed=true;finishAckEpoch++;
                publish(true,runId);
                completeSession(persian?"تمام شد":"Done",runId);
            }
        }catch(Exception ignored){}
    }

'''
s = replace_region(s, '    private void handleSoniox(String text)', '    private boolean isControl(String t)',
                   handle, 'run-scoped Soniox message handling')

publisher = r'''    private String desiredVoiceText(){
        synchronized(textLock){return finalTranscript.toString()+(partialTranscript==null?"":partialTranscript);}
    }

    private void captureVoiceInsertionBoundary(){
        voiceLeftBoundary="";voiceRightBoundary="";voiceBoundaryCaptured=false;voiceBoundaryOwnsWholeField=false;
        voicePublishedText="";voiceOwnedStart=-1;voiceOwnedEnd=-1;voicePublicationPaused=false;
        InputConnection ic=boundConnection;if(ic==null)return;
        try{
            CharSequence beforeCs=ic.getTextBeforeCursor(65536,0);
            CharSequence selectedCs=ic.getSelectedText(0);
            CharSequence afterCs=ic.getTextAfterCursor(65536,0);
            String before=beforeCs==null?"":beforeCs.toString();
            String selected=selectedCs==null?"":selectedCs.toString();
            String after=afterCs==null?"":afterCs.toString();
            int leftKeep=Math.min(48,before.length());int rightKeep=Math.min(48,after.length());
            voiceLeftBoundary=before.substring(before.length()-leftKeep);
            voiceRightBoundary=after.substring(0,rightKeep);

            android.view.inputmethod.ExtractedTextRequest req=new android.view.inputmethod.ExtractedTextRequest();
            android.view.inputmethod.ExtractedText et=ic.getExtractedText(req,0);
            if(et!=null&&et.selectionStart>=0&&et.selectionEnd>=et.selectionStart){
                voiceOwnedStart=et.startOffset+et.selectionStart;
                voiceOwnedEnd=et.startOffset+et.selectionEnd;
                if(selected.isEmpty()&&voiceOwnedEnd>voiceOwnedStart&&et.text!=null
                        &&et.selectionStart<=et.text.length()&&et.selectionEnd<=et.text.length())
                    selected=et.text.subSequence(et.selectionStart,et.selectionEnd).toString();
                if(et.text!=null&&before.isEmpty()&&after.isEmpty()){
                    int selectedLen=voiceOwnedEnd-voiceOwnedStart;
                    voiceBoundaryOwnsWholeField=et.text.length()==0||selectedLen==et.text.length();
                }
            }
            voicePublishedText=selected;
            voiceBoundaryCaptured=true;
        }catch(Exception ignored){
            voiceBoundaryCaptured=true;
        }
    }

    private static final class VoiceEditorWindow{
        final String text;final int absoluteStart;final int selectionStart;final int selectionEnd;
        VoiceEditorWindow(String text,int absoluteStart,int selectionStart,int selectionEnd){
            this.text=text;this.absoluteStart=absoluteStart;this.selectionStart=selectionStart;this.selectionEnd=selectionEnd;
        }
    }

    private VoiceEditorWindow currentVoiceEditorWindow(InputConnection ic){
        if(ic==null)return null;
        try{
            android.view.inputmethod.ExtractedTextRequest req=new android.view.inputmethod.ExtractedTextRequest();
            android.view.inputmethod.ExtractedText et=ic.getExtractedText(req,0);
            if(et==null||et.selectionStart<0||et.selectionEnd<et.selectionStart)return null;
            int absSelStart=et.startOffset+et.selectionStart;int absSelEnd=et.startOffset+et.selectionEnd;
            CharSequence beforeCs=ic.getTextBeforeCursor(65536,0);
            CharSequence selectedCs=ic.getSelectedText(0);
            CharSequence afterCs=ic.getTextAfterCursor(65536,0);
            String before=beforeCs==null?"":beforeCs.toString();
            String selected=selectedCs==null?"":selectedCs.toString();
            String after=afterCs==null?"":afterCs.toString();
            if(selected.isEmpty()&&absSelEnd>absSelStart&&et.text!=null
                    &&et.selectionStart<=et.text.length()&&et.selectionEnd<=et.text.length())
                selected=et.text.subSequence(et.selectionStart,et.selectionEnd).toString();
            return new VoiceEditorWindow(before+selected+after,absSelStart-before.length(),absSelStart,absSelEnd);
        }catch(Exception ignored){return null;}
    }

    private int uniqueBoundaryIndex(String text,String anchor){
        if(text==null||anchor==null||anchor.isEmpty())return -1;
        int first=text.indexOf(anchor);return first>=0&&first==text.lastIndexOf(anchor)?first:-1;
    }

    private int[] locateVoiceOwnedRegion(VoiceEditorWindow window){
        if(!voiceBoundaryCaptured||window==null)return null;
        int startRel;int endRel;
        if(!voiceLeftBoundary.isEmpty()){
            int left=uniqueBoundaryIndex(window.text,voiceLeftBoundary);if(left<0)return null;
            startRel=left+voiceLeftBoundary.length();
        }else if(voiceBoundaryOwnsWholeField||!voiceRightBoundary.isEmpty())startRel=0;
        else return null;
        if(!voiceRightBoundary.isEmpty()){
            int right=uniqueBoundaryIndex(window.text,voiceRightBoundary);if(right<0)return null;endRel=right;
        }else if(voiceBoundaryOwnsWholeField||!voiceLeftBoundary.isEmpty())endRel=window.text.length();
        else return null;
        if(startRel<0||endRel<startRel||endRel>window.text.length())return null;
        return new int[]{window.absoluteStart+startRel,window.absoluteStart+endRel,startRel,endRel};
    }

    private String normalizeVoiceOwnedText(String in){
        if(in==null||in.isEmpty())return "";
        StringBuilder out=new StringBuilder(in.length());boolean pendingSpace=false;
        for(int i=0;i<in.length();i++){
            char c=in.charAt(i);
            if(c=='\u200E'||c=='\u200F'||c=='\u202A'||c=='\u202B'||c=='\u202C'||c=='\u2066'||c=='\u2067'||c=='\u2069')continue;
            if(Character.isWhitespace(c)||c=='\u00A0'){pendingSpace=out.length()>0;continue;}
            if(pendingSpace){out.append(' ');pendingSpace=false;}out.append(c);
        }
        return out.toString().trim();
    }

    private boolean exactOwnedText(String actual,String expected){
        if(actual==null||expected==null)return false;
        return actual.equals(expected)||normalizeVoiceOwnedText(actual).equals(normalizeVoiceOwnedText(expected));
    }

    private int[] locatePublishedVoiceRegion(VoiceEditorWindow window){
        if(window==null)return null;
        if(voiceOwnedStart>=window.absoluteStart&&voiceOwnedEnd>=voiceOwnedStart){
            int rs=voiceOwnedStart-window.absoluteStart;int re=voiceOwnedEnd-window.absoluteStart;
            if(rs>=0&&re>=rs&&re<=window.text.length()){
                String actual=window.text.substring(rs,re);
                if(exactOwnedText(actual,voicePublishedText))return new int[]{voiceOwnedStart,voiceOwnedEnd,rs,re};
            }
        }
        int[] byBoundary=locateVoiceOwnedRegion(window);
        if(byBoundary==null)return null;
        String actual=window.text.substring(byBoundary[2],byBoundary[3]);
        return exactOwnedText(actual,voicePublishedText)?byBoundary:null;
    }

    private int adjustSelectionAfterReplace(int pos,int editStart,int editEnd,int replacementLength){
        if(pos<=editStart)return pos;
        int delta=replacementLength-(editEnd-editStart);
        if(pos>=editEnd)return pos+delta;
        return editStart+Math.min(Math.max(0,pos-editStart),replacementLength);
    }

    private void noteVoicePublicationPaused(long runId){
        if(!voiceRunCurrent(runId))return;
        if(!voicePublicationPaused){
            voicePublicationPaused=true;
            if(running&&!stopRequested)setStatus(persian?"ضبط ادامه دارد — همگام‌سازی متن موقتاً متوقف است":"Recording — live text sync paused");
        }
    }

    private void clearVoicePublicationPaused(long runId){
        if(!voiceRunCurrent(runId)||!voicePublicationPaused)return;
        voicePublicationPaused=false;
        if(running&&!stopRequested)setStatus(listeningText());
    }

    private void publish(boolean finish){publish(finish,activeVoiceRunId);}

    private void publish(boolean finish,long runId){
        main.post(()->{
            if(!voiceRunCurrent(runId))return;
            if(!finish&&!running)return;
            InputConnection ic=boundConnection;
            if(ic==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=ic){
                if(running&&voiceRunCurrent(runId))abortForEditorChange("connection mismatch");
                return;
            }

            String desired;String partial;int finalChars;
            synchronized(textLock){
                desired=finalTranscript.toString()+(partialTranscript==null?"":partialTranscript);
                partial=partialTranscript==null?"":partialTranscript;
                finalChars=finalTranscript.length();
            }

            VoiceEditorWindow window=currentVoiceEditorWindow(ic);
            int[] region=locatePublishedVoiceRegion(window);
            if(window==null||region==null){noteVoicePublicationPaused(runId);return;}
            String actual=window.text.substring(region[2],region[3]);
            if(actual.equals(desired)){
                voicePublishedText=desired;voiceOwnedStart=region[0];voiceOwnedEnd=region[0]+desired.length();
                committedFinalChars=finalChars;livePartialTail=finish?"":partial;hasComposingTail=false;
                clearVoicePublicationPaused(runId);return;
            }

            int keep=actual.equals(voicePublishedText)?commonPrefixChars(actual,desired):0;
            int editStart=region[0]+keep;int editEnd=region[1];String replacement=desired.substring(keep);
            int oldSelStart=window.selectionStart;int oldSelEnd=window.selectionEnd;
            int restoreStart=adjustSelectionAfterReplace(oldSelStart,editStart,editEnd,replacement.length());
            int restoreEnd=adjustSelectionAfterReplace(oldSelEnd,editStart,editEnd,replacement.length());
            boolean batch=false;boolean ok=false;
            programmaticSelectionEditDepth++;
            try{
                batch=ic.beginBatchEdit();
                if(!ic.setSelection(editStart,editEnd)){noteVoicePublicationPaused(runId);return;}
                if(!ic.commitText(replacement,1)){noteVoicePublicationPaused(runId);return;}
                int newOwnedEnd=region[0]+desired.length();
                restoreStart=Math.max(0,restoreStart);restoreEnd=Math.max(restoreStart,restoreEnd);
                ic.setSelection(restoreStart,restoreEnd);
                voicePublishedText=desired;voiceOwnedStart=region[0];voiceOwnedEnd=newOwnedEnd;
                committedFinalChars=finalChars;livePartialTail=finish?"":partial;hasComposingTail=false;
                ok=true;
            }catch(Exception ignored){
            }finally{
                if(batch)try{ic.endBatchEdit();}catch(Exception ignored){}
                if(ok)rememberProgrammaticSelection();
                programmaticSelectionEditDepth=Math.max(0,programmaticSelectionEditDepth-1);
            }
            if(ok)clearVoicePublicationPaused(runId);else noteVoicePublicationPaused(runId);
        });
    }

'''
s = replace_region(s, '    private String ownedVoiceVisibleText(){', '    private void finishWithText(String m)',
                   publisher, 'range-owned caret-independent publisher')

completion = r'''    private void finishWithText(String m){finishWithText(m,activeVoiceRunId);}
    private void finishWithText(String m,long runId){
        if(!voiceRunActive(runId))return;
        completed=true;finishAckEpoch++;
        publish(true,runId);
        completeSession(m,runId);
    }

    private void completeSession(String m){completeSession(m,activeVoiceRunId);}
    private void completeSession(String m,long runId){
        if(!voiceRunCurrent(runId))return;
        boolean shouldSend=sendAfterVoiceStop;sendAfterVoiceStop=false;
        finishAckEpoch++;activeCredentialRequestId=0L;
        running=false;stopRequested=true;awaitingCredential=false;speechRecovering=false;speechRecoveryEpoch++;
        stopAudioRecord();clearPending();
        WebSocket ws=webSocket;webSocket=null;
        if(ws!=null){try{ws.close(1000,"finished");}catch(Exception ignored){try{ws.cancel();}catch(Exception ignored2){}}}
        main.post(()->{
            if(!voiceRunCurrent(runId))return;
            updateMicUi();setStatus(m);
            if(shouldSend)main.postDelayed(()->{
                if(voiceRunCurrent(runId)&&!running)sendFocusedField();
            },40L);
        });
    }

    private void failSession(String m){failSession(m,activeVoiceRunId);}
    private void failSession(String m,long runId){
        if(!voiceRunActive(runId))return;
        synchronized(textLock){
            if(finalTranscript.length()>0||partialTranscript.length()>0){finishWithText(m,runId);return;}
        }
        finishAckEpoch++;activeCredentialRequestId=0L;
        running=false;stopRequested=true;awaitingCredential=false;speechRecovering=false;speechRecoveryEpoch++;
        stopAudioRecord();clearPending();
        WebSocket ws=webSocket;webSocket=null;if(ws!=null)try{ws.cancel();}catch(Exception ignored){}
        main.post(()->{if(voiceRunCurrent(runId)){updateMicUi();setStatus(m);}});
    }

    private void stopAudioRecord(){
        AudioRecord r;
        synchronized(audioLock){r=audioRecord;audioRecord=null;}
        releaseRecorder(r);
    }

'''
s = replace_region(s, '    private void finishWithText(String m)', '    private void updateMicUi(){',
                   completion, 'idempotent session completion')

watchdog = r'''    private void armCredentialWatchdog(){
        final long runId=activeVoiceRunId;
        final int watchdog=++credentialWatchdogEpoch;
        main.postDelayed(()->{
            if(watchdog!=credentialWatchdogEpoch||!voiceRunActive(runId)||completed||stopRequested||!awaitingCredential)return;
            credentialWebViewResets++;
            if(credentialWebViewResets>=3){
                setStatus(persian?"تأیید Perplexity لازم است — برنامه را باز کنید":"Perplexity verification needed — open app");
                credentialWebViewResets=0;
            }
            recreateCredentialWebView("credential callback timeout");
            if(voiceRunActive(runId))armCredentialWatchdog();
        },6500L);
    }

    private long bridgeLong(String value){try{return Long.parseLong(value);}catch(Exception ignored){return -1L;}}

'''
s = replace_region(s, '    private void armCredentialWatchdog(){', '    private final class CredentialBridge {',
                   watchdog, 'run-scoped credential watchdog')

bridge = r'''    private final class CredentialBridge {
        @JavascriptInterface public void credential(String apiKey,String expiresAt,String runValue,String requestValue){
            final long runId=bridgeLong(runValue);final long requestId=bridgeLong(requestValue);
            main.post(()->{
                if(!voiceRunActive(runId)||!awaitingCredential||requestId!=activeCredentialRequestId)return;
                credentialWatchdogEpoch++;credentialWebViewResets=0;awaitingCredential=false;retryAfterPageLoad=false;
                if(apiKey==null||apiKey.isEmpty()){
                    awaitingCredential=true;recreateCredentialWebView("empty credential");armCredentialWatchdog();return;
                }
                speechRecovering=false;startSoniox(apiKey,runId);
            });
        }

        @JavascriptInterface public void credentialError(String error,String runValue,String requestValue){
            final long runId=bridgeLong(runValue);final long requestId=bridgeLong(requestValue);
            main.post(()->{
                if(!voiceRunActive(runId)||!awaitingCredential||requestId!=activeCredentialRequestId)return;
                lastCredentialError=safeCredentialError(error);
                if(credentialAttempt<3&&auth!=null){
                    retryAfterPageLoad=true;pageReady=false;
                    setStatus(persian?"در حال بازیابی نشست Perplexity…":"Refreshing Perplexity session…");
                    try{CookieManager.getInstance().flush();}catch(Exception ignored){}
                    auth.reload();
                    main.postDelayed(()->{
                        if(voiceRunActive(runId)&&awaitingCredential&&retryAfterPageLoad){retryAfterPageLoad=false;requestCredential(runId);}
                    },1600L);
                    return;
                }
                credentialWebViewResets++;
                if(credentialWebViewResets>=3){
                    setStatus(persian?"تأیید Perplexity لازم است — برنامه را باز کنید":"Perplexity verification needed — open app");
                    credentialWebViewResets=0;
                }
                recreateCredentialWebView("credential error "+lastCredentialError);
                if(voiceRunActive(runId))armCredentialWatchdog();
            });
        }
    }

'''
s = replace_region(s, '    private final class CredentialBridge {', '    @Override public void onDestroy()',
                   bridge, 'credential response run/request identity')

js_replacements = [
    ("AndroidKeyboard.credentialError('http '+r.status)",
     "AndroidKeyboard.credentialError('http '+r.status,'__VOICE_RUN__','__CRED_REQ__')"),
    ("AndroidKeyboard.credentialError('no key')",
     "AndroidKeyboard.credentialError('no key','__VOICE_RUN__','__CRED_REQ__')"),
    ("AndroidKeyboard.credential(String(j.api_key),String(j.expires_at||''))",
     "AndroidKeyboard.credential(String(j.api_key),String(j.expires_at||''),'__VOICE_RUN__','__CRED_REQ__')"),
    ("AndroidKeyboard.credentialError(String(e&&e.name||'Error'))",
     "AndroidKeyboard.credentialError(String(e&&e.name||'Error'),'__VOICE_RUN__','__CRED_REQ__')"),
]
for old,new in js_replacements:
    s=rep(s,old,new,'credential JS identity propagation')

if 'versionCode 44' not in g or "versionName '1.34'" not in g:
    raise SystemExit('v1.35 patch: expected v1.34 version markers missing')
g=g.replace('versionCode 44','versionCode 45',1)
g=g.replace("versionName '1.34'","versionName '1.35'",1)

text=s+'\n'+g
required=[
    'private volatile long activeVoiceRunId;',
    'private volatile long activeCredentialRequestId;',
    'private volatile int finishAckEpoch;',
    'private String voicePublishedText = "";',
    'private boolean voiceRunCurrent(long runId){',
    'private boolean sessionStillBound(long runId){',
    'startAudioCapture(runId);',
    'requestCredential(runId);',
    'requestId!=activeCredentialRequestId',
    "'__VOICE_RUN__','__CRED_REQ__'",
    'if(!voiceRunCurrent(runId)||webSocket!=ws)return;',
    'if(voiceRunActive(runId)&&webSocket==ws&&!completed&&!stopRequested)',
    'final int ackEpoch=++finishAckEpoch;',
    'ackEpoch!=finishAckEpoch||webSocket!=finishSocket',
    'private void releaseOwnedRecorder(AudioRecord r){',
    'private int[] locatePublishedVoiceRegion(VoiceEditorWindow window){',
    'private int adjustSelectionAfterReplace(',
    'Recording — live text sync paused',
    'private void publish(boolean finish,long runId){',
    'ic.setSelection(restoreStart,restoreEnd);',
    'Intentionally informational only',
    'versionCode 45',
    "versionName '1.35'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.35 patch: required invariant missing: {needle}')

for forbidden in [
    'Voice stopped — live text sync lost',
    'scheduleInternalSelectionReanchor();',
    'scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);',
    'stopVoiceForManualInput();\n            setStatus("Voice stopped — selection',
    'MAX_CAPTURE_MS',
    'boundConnection.setComposingText(partial,1);',
    'versionCode 44',
    "versionName '1.34'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.35 patch: forbidden unstable behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.35 session-scoped stability architecture patch')
