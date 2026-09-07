from pathlib import Path

p=Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
s=p.read_text()


def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'v1.35 socket hardening: missing pattern: {label}')
    s=s.replace(old,new,1)


def replace_region(start_marker,end_marker,replacement,label):
    global s
    start=s.find(start_marker)
    if start<0: raise SystemExit(f'v1.35 socket hardening: missing start: {label}')
    end=s.find(end_marker,start)
    if end<0: raise SystemExit(f'v1.35 socket hardening: missing end: {label}')
    s=s[:start]+replacement+s[end:]

rep('''    private volatile int finishAckEpoch;\n''','''    private volatile int finishAckEpoch;\n    private volatile int speechSocketEpoch;\n''','socket epoch field')

rep('''        activeVoiceRunId=runId;\n        finishAckEpoch++;\n''','''        activeVoiceRunId=runId;\n        finishAckEpoch++;\n        speechSocketEpoch++;\n''','invalidate previous sockets at run start')

rep('''            finishSent=false;\n            finishAckEpoch++;\n''','''            finishSent=false;\n            finishAckEpoch++;\n            speechSocketEpoch++;\n''','invalidate socket during transport recovery')

s=s.replace('''        finishAckEpoch++;\n        activeCredentialRequestId=0L;\n        activeVoiceRunId=0L;\n''','''        finishAckEpoch++;\n        speechSocketEpoch++;\n        activeCredentialRequestId=0L;\n        activeVoiceRunId=0L;\n''',2)

soniox=r'''    private void startSoniox(String apiKey){startSoniox(apiKey,activeVoiceRunId);}

    private void startSoniox(String apiKey,long runId){
        if(!sessionStillBound(runId))return;
        setStatus(persian?"در حال اتصال به سرویس گفتار…":"Connecting speech service…");
        JSONObject c=new JSONObject();
        put(c,"api_key",apiKey);put(c,"model","stt-rt-v4");put(c,"audio_format","pcm_s16le");
        put(c,"sample_rate",SAMPLE_RATE);put(c,"num_channels",1);put(c,"enable_endpoint_detection",false);
        JSONArray h=new JSONArray();h.put(persian?"fa":"en");put(c,"language_hints",h);put(c,"language_hints_strict",true);

        final int socketEpoch=++speechSocketEpoch;
        WebSocket previous=webSocket;
        webSocket=null;
        if(previous!=null)try{previous.cancel();}catch(Exception ignored){}

        WebSocket created=http.newWebSocket(new Request.Builder().url(SONIOX_WS).build(),new WebSocketListener(){
            @Override public void onOpen(WebSocket ws,Response response){
                if(!voiceRunActive(runId)||socketEpoch!=speechSocketEpoch){ws.cancel();return;}
                if(webSocket!=null&&webSocket!=ws){ws.cancel();return;}
                webSocket=ws;
                if(!ws.send(c.toString())){recoverSpeechTransport("Config send error",runId);return;}
                boolean ok;
                synchronized(audioLock){
                    if(!voiceRunActive(runId)||socketEpoch!=speechSocketEpoch||webSocket!=ws){ws.cancel();return;}
                    sonioxReady=true;ok=flushLocked(ws);
                }
                if(!ok){recoverSpeechTransport("Audio send error",runId);return;}
                speechRecovering=false;
                main.post(()->{if(voiceRunCurrent(runId)&&socketEpoch==speechSocketEpoch)
                    setStatus(stopRequested?(persian?"در حال نهایی‌سازی…":"Finalizing…"):listeningText());});
                maybeFinish(runId);
            }
            @Override public void onMessage(WebSocket ws,String text){
                if(!voiceRunCurrent(runId)||socketEpoch!=speechSocketEpoch||webSocket!=ws)return;
                handleSoniox(runId,ws,text);
            }
            @Override public void onClosed(WebSocket ws,int code,String reason){
                if(voiceRunActive(runId)&&socketEpoch==speechSocketEpoch&&webSocket==ws&&!completed&&!stopRequested)
                    recoverSpeechTransport("Connection closed "+code,runId);
            }
            @Override public void onFailure(WebSocket ws,Throwable t,Response response){
                if(voiceRunActive(runId)&&socketEpoch==speechSocketEpoch&&webSocket==ws&&!completed&&!stopRequested)
                    recoverSpeechTransport("Connection error",runId);
            }
        });
        if(!voiceRunActive(runId)||socketEpoch!=speechSocketEpoch){created.cancel();return;}
        webSocket=created;
    }

'''
replace_region('    private void startSoniox(String apiKey)','    private void startAudioCapture()',soniox,'socket-generation listener')

s=s.replace('''        finishAckEpoch++;activeCredentialRequestId=0L;\n        running=false;''','''        finishAckEpoch++;speechSocketEpoch++;activeCredentialRequestId=0L;\n        running=false;''',2)

required=[
    'private volatile int speechSocketEpoch;',
    'final int socketEpoch=++speechSocketEpoch;',
    'socketEpoch!=speechSocketEpoch',
    'socketEpoch==speechSocketEpoch&&webSocket==ws',
    'finishAckEpoch++;speechSocketEpoch++;activeCredentialRequestId=0L;',
    "versionName '1.35'",
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.35 socket hardening: invariant missing: {needle}')

if 'final WebSocket[] holder=' in s:
    raise SystemExit('v1.35 socket hardening: old holder-based listener remains')

p.write_text(s)
print('Applied v1.35 socket generation hardening')
