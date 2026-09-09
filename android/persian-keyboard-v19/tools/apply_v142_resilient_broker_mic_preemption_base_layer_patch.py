from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
setup = Path('app/src/main/java/com/najme/perplexityprobe/KeyboardSetupActivity.java')
gradle_file = Path('app/build.gradle')

s = service.read_text()
a = setup.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.42 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


def replace_region(text, start_marker, end_marker, replacement, label):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f'v1.42 patch: missing start marker: {label}')
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f'v1.42 patch: missing end marker: {label}')
    return text[:start] + replacement + text[end:]


# v1.42 resilience goals:
# - Perplexity credential WebView has service lifetime, not input-view lifetime.
# - "ready" means an actual credential probe succeeded, not merely a host page load.
# - WebView renderer death is explicitly recoverable.
# - keep one unused short-lived credential warm in RAM, respecting expiry/single-use.
# - microphone capture preemption is a normal suspend/resume state.
# - starting voice from symbols/numpad always returns immediately to the base alpha layer.
# No cookies/app data/IME enablement are cleared by recovery.

s = rep(s,
'''    private volatile boolean pageReady;\n''',
'''    private volatile boolean pageReady;\n    private volatile boolean brokerPageLoaded;\n    private volatile boolean warmCredentialFetchInFlight;\n    private volatile boolean microphoneSilenced;\n    private volatile int microphoneSuspendEpoch;\n    private String warmCredential="";\n    private long warmCredentialExpiresAtMs;\n    private long warmCredentialRequestId;\n    private int warmCredentialFailureCount;\n''',
    'broker/microphone state')

# The credential WebView must not be a child of the keyboard input view.
old_auth_view = '''        auth = new WebView(this);\n        auth.setAlpha(0.01f);\n        root.addView(auth, new LinearLayout.LayoutParams(1, 1));\n        configureWebView();\n        auth.loadUrl(START_URL);\n'''
s = rep(s, old_auth_view, '''        ensureCredentialWebView();\n''',
        'decouple hidden auth WebView from input view')

# Keep a broker alive with service/process lifetime. It is intentionally unattached:
# cookies/storage are still the app's normal WebView profile, but input-view rebuilds
# can no longer destroy the JS bridge/renderer object by replacing the keyboard root.
broker_methods = r'''    private boolean warmCredentialUsable(){
        if(warmCredential==null||warmCredential.isEmpty())return false;
        return warmCredentialExpiresAtMs<=0L||warmCredentialExpiresAtMs-System.currentTimeMillis()>15000L;
    }

    private long parseCredentialExpiry(String value){
        if(value==null||value.trim().isEmpty())return 0L;
        String v=value.trim();
        try{
            long n=Long.parseLong(v);
            if(n>0L&&n<100000000000L)n*=1000L;
            return n;
        }catch(Exception ignored){}
        try{return java.time.Instant.parse(v).toEpochMilli();}catch(Exception ignored){}
        return 0L;
    }

    private void ensureCredentialWebView(){
        if(Looper.myLooper()!=Looper.getMainLooper()){
            main.post(this::ensureCredentialWebView);
            return;
        }
        if(auth!=null)return;
        brokerPageLoaded=false;
        pageReady=false;
        auth=new WebView(this);
        auth.setAlpha(0.01f);
        configureWebView();
        auth.loadUrl(START_URL);
    }

    private void clearWarmCredential(){
        warmCredential="";
        warmCredentialExpiresAtMs=0L;
    }

    private String consumeWarmCredential(){
        if(!warmCredentialUsable()){
            clearWarmCredential();
            return null;
        }
        String key=warmCredential;
        clearWarmCredential();
        return key;
    }

    private void prefetchWarmCredential(){
        if(Looper.myLooper()!=Looper.getMainLooper()){
            main.post(this::prefetchWarmCredential);
            return;
        }
        ensureCredentialWebView();
        if(auth==null||!brokerPageLoaded||warmCredentialFetchInFlight||warmCredentialUsable())return;
        warmCredentialFetchInFlight=true;
        final long requestId=++credentialRequestCounter;
        warmCredentialRequestId=requestId;
        String js=FETCH_CREDENTIAL_JS
                .replace("__VOICE_RUN__","0")
                .replace("__CRED_REQ__",Long.toString(requestId));
        try{auth.evaluateJavascript(js,null);}
        catch(Exception e){
            warmCredentialFetchInFlight=false;
            pageReady=false;
        }
        main.postDelayed(()->{
            if(!warmCredentialFetchInFlight||requestId!=warmCredentialRequestId)return;
            warmCredentialFetchInFlight=false;
            pageReady=false;
            warmCredentialFailureCount++;
            if(warmCredentialFailureCount<2)recreateCredentialWebView("warm credential timeout");
            else if(!running)setStatus(persian?"تأیید Perplexity لازم است — برنامه را باز کنید":"Perplexity verification needed — open app");
        },6500L);
    }

    public static void notifyPerplexitySessionChanged(){
        PersianKeyboardService service=activeInstance;
        if(service==null)return;
        service.main.post(service::repairCredentialBrokerAfterVisibleVerification);
    }

    private void repairCredentialBrokerAfterVisibleVerification(){
        warmCredentialFailureCount=0;
        warmCredentialFetchInFlight=false;
        clearWarmCredential();
        pageReady=false;
        try{CookieManager.getInstance().flush();}catch(Exception ignored){}
        recreateCredentialWebView("visible verification/session changed");
    }

'''
config_marker = '    @SuppressLint({"SetJavaScriptEnabled","AddJavascriptInterface"})\n    private void configureWebView(){'
if config_marker not in s:
    raise SystemExit('v1.42 patch: configureWebView marker missing')
s = s.replace(config_marker, broker_methods + config_marker, 1)

# Existing recovery came from v1.25 and still required root!=null.
recreate = r'''    private void recreateCredentialWebView(String reason){
        if(Looper.myLooper()!=Looper.getMainLooper()){
            main.post(()->recreateCredentialWebView(reason));
            return;
        }
        brokerPageLoaded=false;
        pageReady=false;
        warmCredentialFetchInFlight=false;
        clearWarmCredential();
        credentialAttempt=0;
        try{CookieManager.getInstance().flush();}catch(Exception ignored){}

        WebView old=auth;
        auth=null;
        if(old!=null){
            try{old.stopLoading();}catch(Exception ignored){}
            try{old.removeJavascriptInterface("AndroidKeyboard");}catch(Exception ignored){}
            try{
                android.view.ViewParent parent=old.getParent();
                if(parent instanceof ViewGroup)((ViewGroup)parent).removeView(old);
            }catch(Exception ignored){}
            try{old.destroy();}catch(Exception ignored){}
        }
        ensureCredentialWebView();
        if(running&&awaitingCredential){
            retryAfterPageLoad=true;
            setStatus(persian?"در حال بازیابی نشست Perplexity…":"Recovering Perplexity session…");
        }else if(!running){
            setStatus(persian?"در حال بررسی نشست Perplexity…":"Checking Perplexity session…");
        }
    }

'''
s = replace_region(s, '    private void recreateCredentialWebView(String reason){',
                   '    private void armCredentialWatchdog(){', recreate,
                   'service-lifetime credential WebView recovery')

configure = r'''    @SuppressLint({"SetJavaScriptEnabled","AddJavascriptInterface"})
    private void configureWebView(){
        final WebView target=auth;
        if(target==null)return;
        WebSettings settings=target.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setUserAgentString(MOBILE_BROWSER_UA);
        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(target,true);
        target.addJavascriptInterface(new CredentialBridge(),"AndroidKeyboard");
        target.setWebViewClient(new WebViewClient(){
            @Override public void onPageFinished(WebView view,String url){
                if(view!=auth)return;
                String host=null;try{host=Uri.parse(url).getHost();}catch(Exception ignored){}
                brokerPageLoaded=host!=null&&(host.equals("perplexity.ai")||host.endsWith(".perplexity.ai"));
                if(!brokerPageLoaded){
                    pageReady=false;
                    if(!running)setStatus("Open app/login to Perplexity once");
                    return;
                }
                try{CookieManager.getInstance().flush();}catch(Exception ignored){}
                if(running&&awaitingCredential&&retryAfterPageLoad){
                    retryAfterPageLoad=false;
                    main.postDelayed(()->requestCredential(activeVoiceRunId),250L);
                }
                if(!warmCredentialUsable()&&!warmCredentialFetchInFlight)
                    main.postDelayed(PersianKeyboardService.this::prefetchWarmCredential,300L);
                if(!running)setStatus(pageReady?readyText():(persian?"در حال بررسی نشست Perplexity…":"Checking Perplexity session…"));
            }

            @Override public boolean onRenderProcessGone(WebView view,android.webkit.RenderProcessGoneDetail detail){
                if(view==auth){
                    auth=null;
                    brokerPageLoaded=false;
                    pageReady=false;
                    warmCredentialFetchInFlight=false;
                    clearWarmCredential();
                    main.post(()->{
                        try{view.removeJavascriptInterface("AndroidKeyboard");}catch(Exception ignored){}
                        try{view.destroy();}catch(Exception ignored){}
                        ensureCredentialWebView();
                    });
                }
                return true;
            }
        });
    }

'''
s = replace_region(s, config_marker, '    private final class CredentialBridge {',
                   configure, 'credential broker WebView client')

bridge = r'''    private final class CredentialBridge {
        @JavascriptInterface public void credential(String apiKey,String expiresAt,String runValue,String requestValue){
            final long runId=bridgeLong(runValue);final long requestId=bridgeLong(requestValue);
            main.post(()->{
                if(runId==0L){
                    if(requestId!=warmCredentialRequestId)return;
                    warmCredentialFetchInFlight=false;
                    if(apiKey==null||apiKey.isEmpty()){
                        pageReady=false;
                        warmCredentialFailureCount++;
                        clearWarmCredential();
                        return;
                    }
                    warmCredential=apiKey;
                    warmCredentialExpiresAtMs=parseCredentialExpiry(expiresAt);
                    if(warmCredentialExpiresAtMs<=0L)warmCredentialExpiresAtMs=System.currentTimeMillis()+45000L;
                    warmCredentialFailureCount=0;
                    pageReady=true;
                    if(!running)setStatus(readyText());
                    return;
                }
                if(!voiceRunActive(runId)||!awaitingCredential||requestId!=activeCredentialRequestId)return;
                credentialWatchdogEpoch++;
                credentialWebViewResets=0;
                awaitingCredential=false;
                retryAfterPageLoad=false;
                if(apiKey==null||apiKey.isEmpty()){
                    awaitingCredential=true;
                    recreateCredentialWebView("empty credential");
                    armCredentialWatchdog();
                    return;
                }
                pageReady=true;
                warmCredentialFailureCount=0;
                speechRecovering=false;
                startSoniox(apiKey,runId);
                main.postDelayed(PersianKeyboardService.this::prefetchWarmCredential,500L);
            });
        }

        @JavascriptInterface public void credentialError(String error,String runValue,String requestValue){
            final long runId=bridgeLong(runValue);final long requestId=bridgeLong(requestValue);
            main.post(()->{
                if(runId==0L){
                    if(requestId!=warmCredentialRequestId)return;
                    warmCredentialFetchInFlight=false;
                    pageReady=false;
                    clearWarmCredential();
                    lastCredentialError=safeCredentialError(error);
                    warmCredentialFailureCount++;
                    if(warmCredentialFailureCount<2){
                        main.postDelayed(()->recreateCredentialWebView("warm credential error "+lastCredentialError),800L);
                    }else if(!running){
                        setStatus(persian?"تأیید Perplexity لازم است — برنامه را باز کنید":"Perplexity verification needed — open app");
                    }
                    return;
                }
                if(!voiceRunActive(runId)||!awaitingCredential||requestId!=activeCredentialRequestId)return;
                pageReady=false;
                lastCredentialError=safeCredentialError(error);
                if(credentialAttempt<3&&auth!=null){
                    retryAfterPageLoad=true;
                    brokerPageLoaded=false;
                    setStatus(persian?"در حال بازیابی نشست Perplexity…":"Refreshing Perplexity session…");
                    try{CookieManager.getInstance().flush();}catch(Exception ignored){}
                    auth.reload();
                    main.postDelayed(()->{
                        if(voiceRunActive(runId)&&awaitingCredential&&retryAfterPageLoad){
                            retryAfterPageLoad=false;
                            requestCredential(runId);
                        }
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
s = replace_region(s, '    private final class CredentialBridge {',
                   '    @Override public void onDestroy()', bridge,
                   'warm/voice credential bridge')

start = s.find('    private void startVoice(){')
end = s.find('    private String safeCredentialError', start)
if start < 0 or end < 0:
    raise SystemExit('v1.42 patch: startVoice region missing')
start_voice = s[start:end]
old_gate = '        if(!pageReady){setStatus("Perplexity session not ready — open the app/login once");return;}\n'
if old_gate not in start_voice:
    raise SystemExit('v1.42 patch: old pageReady start gate missing')
start_voice = start_voice.replace(old_gate, '        ensureCredentialWebView();\n', 1)
old_layout = '''        voicePublicationPaused=false;\n        updateMicUi();\n'''
if old_layout not in start_voice:
    raise SystemExit('v1.42 patch: voice-start UI marker missing')
start_voice = start_voice.replace(old_layout,
'''        voicePublicationPaused=false;\n        layer=Layer.ALPHA;shift=false;\n        render();\n        updateMicUi();\n''', 1)
old_request = '''        startAudioCapture(runId);\n        armCredentialWatchdog();\n        requestCredential(runId);\n'''
if old_request not in start_voice:
    raise SystemExit('v1.42 patch: voice credential start marker missing')
start_voice = start_voice.replace(old_request,
'''        startAudioCapture(runId);\n        String warm=consumeWarmCredential();\n        if(warm!=null){\n            awaitingCredential=false;\n            credentialWatchdogEpoch++;\n            pageReady=true;\n            startSoniox(warm,runId);\n            main.postDelayed(PersianKeyboardService.this::prefetchWarmCredential,500L);\n        }else{\n            awaitingCredential=true;\n            armCredentialWatchdog();\n            if(brokerPageLoaded)requestCredential(runId);else retryAfterPageLoad=true;\n        }\n''', 1)
s = s[:start] + start_voice + s[end:]

mic_methods = r'''    private void checkMicrophoneRecovery(long runId,int epoch){
        if(android.os.Build.VERSION.SDK_INT<29||epoch!=microphoneSuspendEpoch
                ||!microphoneSilenced||!voiceRunActive(runId))return;
        AudioRecord recorder=audioRecord;
        if(recorder!=null){
            try{
                android.media.AudioRecordingConfiguration config=recorder.getActiveRecordingConfiguration();
                if(config!=null&&!config.isClientSilenced()){
                    handleMicrophoneSilenced(false);
                    return;
                }
            }catch(Exception ignored){}
        }
        main.postDelayed(()->checkMicrophoneRecovery(runId,epoch),750L);
    }

    private void handleMicrophoneSilenced(boolean silenced){
        if(microphoneSilenced==silenced)return;
        microphoneSilenced=silenced;
        final int suspendEpoch=++microphoneSuspendEpoch;
        final long runId=activeVoiceRunId;
        diag("MIC silenced="+silenced+" running="+running+" run="+runId);
        if(!voiceRunActive(runId))return;
        if(silenced){
            WebSocket old;
            synchronized(audioLock){
                sonioxReady=false;
                finishSent=false;
                speechRecovering=true;
                pendingAudio.clear();
                pendingBytes=0;
                old=webSocket;
                webSocket=null;
            }
            if(old!=null)try{old.cancel();}catch(Exception ignored){}
            awaitingCredential=false;
            activeCredentialRequestId=0L;
            credentialWatchdogEpoch++;
            setStatus(persian?"میکروفون موقتاً در اختیار برنامهٔ دیگری است…":"Microphone temporarily in use…");
            main.postDelayed(()->checkMicrophoneRecovery(runId,suspendEpoch),750L);
            return;
        }

        if(!voiceRunActive(runId)||completed||stopRequested)return;
        setStatus(persian?"میکروفون برگشت — اتصال مجدد…":"Microphone restored — reconnecting…");
        speechRecovering=true;
        awaitingCredential=true;
        credentialAttempt=0;
        retryAfterPageLoad=false;
        lastCredentialError="";
        String warm=consumeWarmCredential();
        if(warm!=null){
            awaitingCredential=false;
            pageReady=true;
            startSoniox(warm,runId);
            main.postDelayed(PersianKeyboardService.this::prefetchWarmCredential,500L);
        }else{
            armCredentialWatchdog();
            ensureCredentialWebView();
            if(brokerPageLoaded)requestCredential(runId);else retryAfterPageLoad=true;
        }
    }

    private final android.media.AudioManager.AudioRecordingCallback audioRecordingCallback=
            new android.media.AudioManager.AudioRecordingCallback(){
        @Override public void onRecordingConfigChanged(java.util.List<android.media.AudioRecordingConfiguration> configs){
            if(android.os.Build.VERSION.SDK_INT<29)return;
            AudioRecord recorder=audioRecord;
            if(recorder==null)return;
            int sessionId;
            try{sessionId=recorder.getAudioSessionId();}catch(Exception e){return;}
            for(android.media.AudioRecordingConfiguration config:configs){
                if(config==null)continue;
                try{
                    if(config.getClientAudioSessionId()==sessionId){
                        handleMicrophoneSilenced(config.isClientSilenced());
                        return;
                    }
                }catch(Exception ignored){}
            }
        }
    };

'''
audio_marker = '    private void startAudioCapture(){startAudioCapture(activeVoiceRunId);}'
if audio_marker not in s:
    raise SystemExit('v1.42 patch: audio capture marker missing')
s = s.replace(audio_marker, mic_methods + audio_marker, 1)

audio_start_old = '''                localRecorder=new AudioRecord(MediaRecorder.AudioSource.VOICE_RECOGNITION,SAMPLE_RATE,\n                        AudioFormat.CHANNEL_IN_MONO,AudioFormat.ENCODING_PCM_16BIT,Math.max(min,AUDIO_CHUNK));\n                if(localRecorder.getState()!=AudioRecord.STATE_INITIALIZED)throw new IllegalStateException("AudioRecord not initialized");\n'''
audio_start_new = '''                localRecorder=new AudioRecord(MediaRecorder.AudioSource.VOICE_RECOGNITION,SAMPLE_RATE,\n                        AudioFormat.CHANNEL_IN_MONO,AudioFormat.ENCODING_PCM_16BIT,Math.max(min,AUDIO_CHUNK));\n                if(localRecorder.getState()!=AudioRecord.STATE_INITIALIZED)throw new IllegalStateException("AudioRecord not initialized");\n                if(android.os.Build.VERSION.SDK_INT>=29){\n                    try{localRecorder.registerAudioRecordingCallback(getMainExecutor(),audioRecordingCallback);}catch(Exception ignored){}\n                }\n'''
s = rep(s, audio_start_old, audio_start_new, 'register audio recording callback')

buffer_marker = '''    private boolean bufferOrSend(long runId,byte[] chunk){\n        synchronized(audioLock){\n            if(!voiceRunActive(runId))return true;\n'''
s = rep(s, buffer_marker,
'''    private boolean bufferOrSend(long runId,byte[] chunk){\n        synchronized(audioLock){\n            if(!voiceRunActive(runId))return true;\n            if(microphoneSilenced)return true;\n''', 'drop silenced PCM')

release_marker = '''    private void releaseRecorder(AudioRecord r){\n        if(r==null)return;\n        try{if(r.getRecordingState()==AudioRecord.RECORDSTATE_RECORDING)r.stop();}catch(Exception ignored){}\n        try{r.release();}catch(Exception ignored){}\n    }\n'''
s = rep(s, release_marker,
'''    private void releaseRecorder(AudioRecord r){\n        if(r==null)return;\n        if(android.os.Build.VERSION.SDK_INT>=29){\n            try{r.unregisterAudioRecordingCallback(audioRecordingCallback);}catch(Exception ignored){}\n        }\n        try{if(r.getRecordingState()==AudioRecord.RECORDSTATE_RECORDING)r.stop();}catch(Exception ignored){}\n        try{r.release();}catch(Exception ignored){}\n    }\n''', 'unregister audio recording callback')

s = rep(s,
'''        resetAudio();\n        running=true;stopRequested=false;completed=false;awaitingCredential=true;credentialAttempt=0;\n''',
'''        resetAudio();\n        microphoneSilenced=false;\n        running=true;stopRequested=false;completed=false;awaitingCredential=true;credentialAttempt=0;\n''', 'reset mic suspension on voice start')

setup_config_start = '    @SuppressLint("SetJavaScriptEnabled")\n    private void configureWebView() {'
setup_config_end = '\n    }\n}'
sa_start = a.find(setup_config_start)
sa_end = a.find(setup_config_end, sa_start)
if sa_start < 0 or sa_end < 0:
    raise SystemExit('v1.42 patch: setup configureWebView region missing')
setup_config = r'''    @SuppressLint("SetJavaScriptEnabled")
    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setSupportZoom(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setUserAgentString(MOBILE_BROWSER_UA);
        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, true);
        webView.setWebViewClient(new WebViewClient() {
            @Override public void onPageFinished(WebView view, String url) {
                String host = null;
                try { host = Uri.parse(url).getHost(); } catch (Exception ignored) {}
                boolean ok = host != null && (host.equals("perplexity.ai") || host.endsWith(".perplexity.ai"));
                if (ok) {
                    try { CookieManager.getInstance().flush(); } catch (Exception ignored) {}
                    status.setText("Perplexity page loaded — checking keyboard credential path…");
                    PersianKeyboardService.notifyPerplexitySessionChanged();
                } else {
                    status.setText("در انتظار صفحه Perplexity…");
                }
            }

            @Override public boolean onRenderProcessGone(WebView view, android.webkit.RenderProcessGoneDetail detail) {
                if (view != webView) return true;
                try { view.destroy(); } catch (Exception ignored) {}
                webView = null;
                recreate();
                return true;
            }
        });
    }
'''
a = a[:sa_start] + setup_config + a[sa_end+len('\n    }'):]

if 'versionCode 51' not in g or "versionName '1.41'" not in g:
    raise SystemExit('v1.42 patch: expected v1.41 Gradle markers missing')
g = g.replace('versionCode 51','versionCode 52',1)
g = g.replace("versionName '1.41'","versionName '1.42'",1)

text = s + '\n' + a + '\n' + g
required = [
    'private void ensureCredentialWebView(){',
    'private void prefetchWarmCredential(){',
    'runId==0L',
    'parseCredentialExpiry(expiresAt)',
    'onRenderProcessGone(WebView view,android.webkit.RenderProcessGoneDetail detail)',
    'public static void notifyPerplexitySessionChanged(){',
    'private void handleMicrophoneSilenced(boolean silenced){',
    'private void checkMicrophoneRecovery(long runId,int epoch){',
    'getActiveRecordingConfiguration()',
    'registerAudioRecordingCallback(getMainExecutor(),audioRecordingCallback)',
    'config.isClientSilenced()',
    'if(microphoneSilenced)return true;',
    'layer=Layer.ALPHA;shift=false;',
    'String warm=consumeWarmCredential();',
    'PersianKeyboardService.notifyPerplexitySessionChanged();',
    'versionCode 52',
    "versionName '1.42'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.42 patch: required invariant missing: {needle}')

for forbidden in [
    'root.addView(auth,new LinearLayout.LayoutParams(1,1));',
    'root.addView(auth, new LinearLayout.LayoutParams(1, 1));',
    'if(!pageReady){setStatus("Perplexity session not ready',
    'versionCode 51',
    "versionName '1.41'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.42 patch: forbidden old behavior remains: {forbidden}')

service.write_text(s)
setup.write_text(a)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.42 resilient broker/mic/base-layer patch')
