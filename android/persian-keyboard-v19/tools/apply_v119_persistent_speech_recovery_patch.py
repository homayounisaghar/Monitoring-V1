from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.19 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


replace_once('    private WebSocket webSocket;\n','    private volatile WebSocket webSocket;\n','WebSocket cross-thread visibility')
replace_once('''    private int credentialAttempt;
    private boolean retryAfterPageLoad;
    private String lastCredentialError = "";
''','''    private int credentialAttempt;
    private boolean retryAfterPageLoad;
    private String lastCredentialError = "";
    private volatile boolean speechRecovering;
    private volatile int speechRecoveryEpoch;
''','speech recovery state')
replace_once('    private static final int PREBUFFER_MAX = SAMPLE_RATE * 2 * 20;\n','    private static final int PREBUFFER_MAX = SAMPLE_RATE * 2 * 60;\n','extend recovery prebuffer')
replace_once('''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; updateMicUi();
''','''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; updateMicUi();
''','reset recovery state')
replace_once('''    private void requestStop(){if(!running||stopRequested)return;stopRequested=true;setStatus(persian?"در حال نهایی‌سازی…":"Finalizing…");AudioRecord r=audioRecord;if(r!=null)try{r.stop();}catch(Exception ignored){}}
''','''    private void requestStop(){
        if(!running||stopRequested)return;
        stopRequested=true;
        speechRecoveryEpoch++;
        setStatus(persian?"در حال نهایی‌سازی…":"Finalizing…");
        AudioRecord r=audioRecord;if(r!=null)try{r.stop();}catch(Exception ignored){}
        if(speechRecovering||webSocket==null){
            speechRecovering=false;
            completed=true;
            publish(true);
            completeSession(persian?"تمام شد":"Done");
        }
    }
''','manual stop during recovery')
replace_once('''    private String safeCredentialError(String e){
        if(e==null||e.trim().isEmpty())return"unknown"; String s=e.replace('\\n',' ').replace('\\r',' ').trim(); return s.length()>48?s.substring(0,48):s;
    }

''','''    private String safeCredentialError(String e){
        if(e==null||e.trim().isEmpty())return"unknown"; String s=e.replace('\\n',' ').replace('\\r',' ').trim(); return s.length()>48?s.substring(0,48):s;
    }

    private boolean recoverableSonioxError(JSONObject o){
        if(o==null)return false;
        int code=o.optInt("error_code",0);
        String type=o.optString("error_type","");
        return code==408 || code>=500
                || "temp_api_key_session_expired".equals(type)
                || "max_duration_reached".equals(type)
                || "service_unavailable".equals(type)
                || "request_timeout".equals(type);
    }

    private void recoverSpeechTransport(String reason){
        if(!running||completed||stopRequested)return;
        synchronized(audioLock){
            if(speechRecovering)return;
            speechRecovering=true;
            sonioxReady=false;
            finishSent=false;
        }
        WebSocket old=webSocket; webSocket=null;
        if(old!=null)try{old.cancel();}catch(Exception ignored){}
        synchronized(textLock){
            if(partialTranscript!=null&&!partialTranscript.isEmpty()){
                finalTranscript.append(partialTranscript);
                partialTranscript="";
            }
            finalTokenIds.clear();
        }
        publish(false);
        awaitingCredential=true;
        credentialAttempt=0;
        retryAfterPageLoad=false;
        lastCredentialError="";
        final int epoch=++speechRecoveryEpoch;
        main.post(()->{
            if(!running||completed||stopRequested||epoch!=speechRecoveryEpoch)return;
            setStatus(persian?"در حال اتصال مجدد…":"Reconnecting speech…");
            requestCredential();
        });
        main.postDelayed(()->{
            if(running&&!completed&&!stopRequested&&speechRecovering&&awaitingCredential&&epoch==speechRecoveryEpoch)requestCredential();
        },2500L);
    }

''','speech recovery helpers')
replace_once('''            @Override public void onOpen(WebSocket ws,Response response){if(!sessionStillBound()){ws.cancel();return;}webSocket=ws;if(!ws.send(c.toString())){finishWithText("Config send error");return;}boolean ok;synchronized(audioLock){sonioxReady=true;ok=flushLocked(ws);}if(!ok){finishWithText("Audio send error");return;}main.post(()->setStatus(stopRequested?(persian?"در حال نهایی‌سازی…":"Finalizing…"):listeningText()));maybeFinish();}
''','''            @Override public void onOpen(WebSocket ws,Response response){if(!sessionStillBound()){ws.cancel();return;}webSocket=ws;if(!ws.send(c.toString())){recoverSpeechTransport("Config send error");return;}boolean ok;synchronized(audioLock){sonioxReady=true;ok=flushLocked(ws);}if(!ok){recoverSpeechTransport("Audio send error");return;}speechRecovering=false;main.post(()->setStatus(stopRequested?(persian?"در حال نهایی‌سازی…":"Finalizing…"):listeningText()));maybeFinish();}
''','recover config/audio flush failures')
replace_once('''            @Override public void onClosed(WebSocket ws,int code,String reason){if(running&&!completed)finishWithText("Connection closed");}
            @Override public void onFailure(WebSocket ws,Throwable t,Response response){if(running&&!completed)finishWithText("Connection error");}
''','''            @Override public void onClosed(WebSocket ws,int code,String reason){if(running&&!completed&&!stopRequested)recoverSpeechTransport("Connection closed "+code);}
            @Override public void onFailure(WebSocket ws,Throwable t,Response response){if(running&&!completed&&!stopRequested)recoverSpeechTransport("Connection error");}
''','recover unexpected WebSocket close/failure')
replace_once('''    private boolean bufferOrSend(byte[] chunk){
        synchronized(audioLock){if(!sonioxReady||webSocket==null){pendingAudio.addLast(chunk);pendingBytes+=chunk.length;while(pendingBytes>PREBUFFER_MAX&&pendingAudio.size()>1){byte[] d=pendingAudio.removeFirst();pendingBytes-=d.length;}return true;}if(!flushLocked(webSocket))return false;return webSocket.send(ByteString.of(chunk,0,chunk.length));}
    }
    private boolean flushLocked(WebSocket ws){while(!pendingAudio.isEmpty()){byte[] c=pendingAudio.removeFirst();pendingBytes-=c.length;if(!ws.send(ByteString.of(c,0,c.length))){pendingAudio.clear();pendingBytes=0;return false;}}pendingBytes=0;return true;}
''','''    private void queuePendingLocked(byte[] chunk){
        pendingAudio.addLast(chunk); pendingBytes+=chunk.length;
        while(pendingBytes>PREBUFFER_MAX&&pendingAudio.size()>1){byte[] d=pendingAudio.removeFirst();pendingBytes-=d.length;}
    }
    private boolean bufferOrSend(byte[] chunk){
        synchronized(audioLock){
            if(!sonioxReady||webSocket==null){queuePendingLocked(chunk);return true;}
            if(!flushLocked(webSocket)){queuePendingLocked(chunk);return false;}
            if(!webSocket.send(ByteString.of(chunk,0,chunk.length))){queuePendingLocked(chunk);return false;}
            return true;
        }
    }
    private boolean flushLocked(WebSocket ws){
        while(!pendingAudio.isEmpty()){
            byte[] c=pendingAudio.peekFirst();
            if(!ws.send(ByteString.of(c,0,c.length)))return false;
            pendingAudio.removeFirst(); pendingBytes-=c.length;
        }
        pendingBytes=0; return true;
    }
''','retain buffered audio across recovery')
replace_once('''                while(running&&!stopRequested){int n;try{n=audioRecord.read(buf,0,buf.length);}catch(Exception e){if(stopRequested||!running)break;throw e;}if(n>0){byte[] chunk=Arrays.copyOf(buf,n);if(!bufferOrSend(chunk))throw new IllegalStateException("Audio send rejected");}else if(n<0&&!stopRequested)throw new IllegalStateException("Audio read failed");}
                stopAudioRecord();synchronized(audioLock){audioDone=true;}if(running&&!completed)maybeFinish();
            }catch(Exception e){stopAudioRecord();synchronized(audioLock){audioDone=true;}if(running)finishWithText("Audio error");}
''','''                while(running&&!stopRequested){int n;try{n=audioRecord.read(buf,0,buf.length);}catch(Exception e){if(stopRequested||!running)break;throw e;}if(n>0){byte[] chunk=Arrays.copyOf(buf,n);if(!bufferOrSend(chunk))recoverSpeechTransport("Audio send rejected");}else if(n<0&&!stopRequested)throw new IllegalStateException("Audio read failed");}
                stopAudioRecord();synchronized(audioLock){audioDone=true;}if(running&&!completed)maybeFinish();
            }catch(Exception e){
                stopAudioRecord();
                if(running&&!stopRequested&&!completed){
                    synchronized(audioLock){audioDone=false;}
                    main.post(()->setStatus(persian?"در حال بازیابی میکروفون…":"Recovering microphone…"));
                    main.postDelayed(()->{if(running&&!stopRequested&&!completed)startAudioCapture();},350L);
                }else{
                    synchronized(audioLock){audioDone=true;}
                    if(running&&!completed)maybeFinish();
                }
            }
''','restart AudioRecord after transient failure')
replace_once('if(o.has("error_code")&&!o.isNull("error_code")){finishWithText("Soniox error");return;}','if(o.has("error_code")&&!o.isNull("error_code")){if(recoverableSonioxError(o)){recoverSpeechTransport(o.optString("error_type","Soniox error"));return;}finishWithText("Soniox error");return;}','recover retryable Soniox errors')
replace_once('if(o.optBoolean("finished",false)){completed=true;publish(true);completeSession(persian?"تمام شد":"Done");WebSocket ws=webSocket;if(ws!=null)ws.close(1000,"finished");}','if(o.optBoolean("finished",false)){if(!stopRequested){recoverSpeechTransport("Unexpected finished");return;}completed=true;publish(true);completeSession(persian?"تمام شد":"Done");WebSocket ws=webSocket;if(ws!=null)ws.close(1000,"finished");}','recover unexpected finished')
replace_once('''        @JavascriptInterface public void credential(String apiKey,String expiresAt){main.post(()->{if(!running||!awaitingCredential)return;awaitingCredential=false;retryAfterPageLoad=false;if(apiKey==null||apiKey.isEmpty()){failSession("Perplexity returned no credential");return;}startSoniox(apiKey);});}
''','''        @JavascriptInterface public void credential(String apiKey,String expiresAt){main.post(()->{if(!running||!awaitingCredential)return;awaitingCredential=false;retryAfterPageLoad=false;if(apiKey==null||apiKey.isEmpty()){if(speechRecovering){awaitingCredential=true;main.postDelayed(PersianKeyboardService.this::requestCredential,1200L);return;}failSession("Perplexity returned no credential");return;}startSoniox(apiKey);});}
''','recovery credential handling')
replace_once('''        @JavascriptInterface public void credentialError(String error){main.post(()->{if(!running||!awaitingCredential)return;lastCredentialError=safeCredentialError(error);if(credentialAttempt<3&&auth!=null){retryAfterPageLoad=true;pageReady=false;setStatus(persian?"در حال بازیابی نشست Perplexity…":"Refreshing Perplexity session…");try{CookieManager.getInstance().flush();}catch(Exception ignored){}auth.reload();main.postDelayed(()->{if(running&&awaitingCredential&&retryAfterPageLoad){retryAfterPageLoad=false;requestCredential();}},1600L);return;}awaitingCredential=false;failSession("Perplexity credential failed ("+lastCredentialError+")");});}
''','''        @JavascriptInterface public void credentialError(String error){main.post(()->{if(!running||!awaitingCredential)return;lastCredentialError=safeCredentialError(error);if(speechRecovering){if(auth!=null){retryAfterPageLoad=true;pageReady=false;setStatus(persian?"در حال بازیابی نشست Perplexity…":"Refreshing Perplexity session…");try{CookieManager.getInstance().flush();}catch(Exception ignored){}auth.reload();main.postDelayed(()->{if(running&&awaitingCredential&&speechRecovering){retryAfterPageLoad=false;requestCredential();}},1600L);}return;}if(credentialAttempt<3&&auth!=null){retryAfterPageLoad=true;pageReady=false;setStatus(persian?"در حال بازیابی نشست Perplexity…":"Refreshing Perplexity session…");try{CookieManager.getInstance().flush();}catch(Exception ignored){}auth.reload();main.postDelayed(()->{if(running&&awaitingCredential&&retryAfterPageLoad){retryAfterPageLoad=false;requestCredential();}},1600L);return;}awaitingCredential=false;failSession("Perplexity credential failed ("+lastCredentialError+")");});}
''','keep retrying credentials during recovery')

if 'versionCode 28' not in g or "versionName '1.18'" not in g:
    raise SystemExit('v1.19 patch: expected v1.18 version markers missing')
g = g.replace('versionCode 28', 'versionCode 29', 1)
g = g.replace("versionName '1.18'", "versionName '1.19'", 1)

required = [
    'private volatile boolean speechRecovering;',
    'private void recoverSpeechTransport(String reason){',
    'code==408 || code>=500',
    '"temp_api_key_session_expired".equals(type)',
    '"max_duration_reached".equals(type)',
    'recoverSpeechTransport("Connection closed "+code)',
    'recoverSpeechTransport("Connection error")',
    'if(!stopRequested){recoverSpeechTransport("Unexpected finished");return;}',
    'private void queuePendingLocked(byte[] chunk){',
    'pendingAudio.peekFirst()',
    'Recovering microphone',
    'private static final int PREBUFFER_MAX = SAMPLE_RATE * 2 * 60;',
    'Button copy = toolbarButton("⧉", v -> copyCurrentText());',
    'String label=running?"🎙 "+badge():"🎙";',
    'private boolean capsLock;',
    'Button clearField = toolbarButton("×", v -> clearCurrentTextField());',
    'enable_endpoint_detection",false',
    'language_hints_strict",true',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.19 patch: required invariant missing: {needle}')
for forbidden in [
    '@Override public void onClosed(WebSocket ws,int code,String reason){if(running&&!completed)finishWithText("Connection closed");}',
    '@Override public void onFailure(WebSocket ws,Throwable t,Response response){if(running&&!completed)finishWithText("Connection error");}',
    'if(!bufferOrSend(chunk))throw new IllegalStateException("Audio send rejected")',
    'if(running)finishWithText("Audio error")',
    'if(o.has("error_code")&&!o.isNull("error_code")){finishWithText("Soniox error");return;}',
    'if(o.optBoolean("finished",false)){completed=true;',
    'MAX_CAPTURE_MS',
    'toolbarButton("G⇄"',
    'private void switchToGboard(){',
    'Button copy = toolbarButton("Copy", v -> copyCurrentText());',
    'String label=running?"🎙 "+badge():"🎤";',
]:
    if forbidden in s:
        raise SystemExit(f'v1.19 patch: forbidden old stop path remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.19 persistent speech recovery patch')
