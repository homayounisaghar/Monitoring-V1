from pathlib import Path

p=Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
s=p.read_text()

marker='    private final class CredentialBridge {'
if marker not in s:
    raise SystemExit('v1.42.1 patch: CredentialBridge marker missing')

for missing in [
    '    private void recreateCredentialWebView(String reason){',
    '    private void armCredentialWatchdog(){',
    '    private long bridgeLong(String value){',
]:
    if missing in s:
        raise SystemExit(f'v1.42.1 patch: helper unexpectedly already present: {missing}')

helpers=r'''    private void recreateCredentialWebView(String reason){
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

    private void armCredentialWatchdog(){
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

    private long bridgeLong(String value){
        try{return Long.parseLong(value);}catch(Exception ignored){return -1L;}
    }

'''

s=s.replace(marker,helpers+marker,1)

for needle in [
    'private void recreateCredentialWebView(String reason){',
    'private void armCredentialWatchdog(){',
    'private long bridgeLong(String value){',
    'recreateCredentialWebView("credential callback timeout")',
    'ensureCredentialWebView();',
]:
    if needle not in s:
        raise SystemExit(f'v1.42.1 patch: invariant missing: {needle}')

p.write_text(s)
print('Restored v1.42 broker recovery/watchdog bridge helpers')
