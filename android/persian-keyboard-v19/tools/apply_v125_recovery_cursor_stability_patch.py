from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.25 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)


# v1.25 addresses two device-reported failures:
# 1) a recovery can remain stuck forever if the IME's hidden Perplexity WebView
#    stops delivering credential callbacks; v1.19.1 intentionally excluded
#    speech recovery from the startup timeout but had no recovery watchdog.
# 2) live composing text is unreliable in browser/contenteditable editors and can
#    leave stale partial text around the caret. Commit only Soniox-final text
#    during dictation and use the last partial only as a one-time finish fallback.

replace_once(
'''    private volatile int speechRecoveryEpoch;
    private boolean sendAfterVoiceStop;
''',
'''    private volatile int speechRecoveryEpoch;
    private volatile int credentialWatchdogEpoch;
    private int credentialWebViewResets;
    private boolean sendAfterVoiceStop;
''',
    'credential watchdog state',
)

replace_once(
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; sendAfterVoiceStop=false; updateMicUi();
''',
'''        resetAudio(); running=true; stopRequested=false; completed=false; awaitingCredential=true; credentialAttempt=0; retryAfterPageLoad=false; lastCredentialError=""; speechRecovering=false; speechRecoveryEpoch++; credentialWatchdogEpoch++; credentialWebViewResets=0; sendAfterVoiceStop=false; updateMicUi();
''',
    'reset credential watchdog when voice starts',
)

# Replace the v1.8 live-composition publisher. Samsung Browser/contenteditable
# may not preserve Android composing spans consistently; repeatedly replacing a
# partial therefore can strand stale fragments after the caret. Final tokens are
# immutable and safe to append exactly once.
start = s.index('    private void publish(boolean finish){')
end = s.index('    private void finishWithText(String m){', start)
new_publish = r'''    private void publish(boolean finish){
        main.post(()->{
            if(!sessionStillBound()&&!finish)return;
            if(boundConnection==null||activeGeneration!=inputGeneration||getCurrentInputConnection()!=boundConnection){if(running)abortForEditorChange();return;}
            String newFinal;String finishTail;int targetFinalChars;
            synchronized(textLock){
                String allFinal=finalTranscript.toString();
                int from=Math.min(committedFinalChars,allFinal.length());
                newFinal=allFinal.substring(from);
                finishTail=finish?partialTranscript:"";
                targetFinalChars=allFinal.length();
            }
            try{
                // Never stream partial text into the editor. Browser-backed and
                // contenteditable fields can lose/reposition the composing span,
                // which leaves duplicate/junk text after the visible caret.
                if(hasComposingTail){
                    boundConnection.finishComposingText();
                    hasComposingTail=false;
                }
                if(!newFinal.isEmpty()){
                    boundConnection.commitText(newFinal,1);
                    rememberProgrammaticSelection();
                    synchronized(textLock){if(committedFinalChars<targetFinalChars)committedFinalChars=targetFinalChars;}
                }
                // Normally Soniox finalizes the tail before finished=true. Keep a
                // one-time fallback so the last spoken fragment is not lost if a
                // terminal response still contains a non-final tail.
                if(finish&&!finishTail.isEmpty()){
                    boundConnection.commitText(finishTail,1);
                    rememberProgrammaticSelection();
                    synchronized(textLock){partialTranscript="";}
                }
                if(finish){
                    boundConnection.finishComposingText();
                    hasComposingTail=false;
                    rememberProgrammaticSelection();
                }
            }catch(Exception e){abortForEditorChange();}
        });
    }
'''
s = s[:start] + new_publish + s[end:]

# A hidden WebView can look nominally loaded (same perplexity.ai host) while its
# renderer/JS bridge no longer produces a credential callback. Rebuild only that
# hidden WebView, preserving the shared CookieManager/session. This is not a
# challenge bypass: if Perplexity requires interactive verification, status tells
# the user to open the app and complete it normally.
bridge_marker = '    private final class CredentialBridge {'
if bridge_marker not in s:
    raise SystemExit('v1.25 patch: CredentialBridge marker missing')
helpers = r'''    private void recreateCredentialWebView(String reason){
        if(Looper.myLooper()!=Looper.getMainLooper()){
            main.post(()->recreateCredentialWebView(reason));
            return;
        }
        if(!running||completed||stopRequested)return;
        setStatus(persian?"در حال بازیابی نشست Perplexity…":"Recovering Perplexity session…");
        retryAfterPageLoad=true;
        pageReady=false;
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
        if(root==null)return;
        auth=new WebView(this);
        auth.setAlpha(0.01f);
        root.addView(auth,new LinearLayout.LayoutParams(1,1));
        configureWebView();
        auth.loadUrl(START_URL);
    }

    private void armCredentialWatchdog(){
        final int watchdog=++credentialWatchdogEpoch;
        main.postDelayed(()->{
            if(watchdog!=credentialWatchdogEpoch||!running||completed||stopRequested||!awaitingCredential)return;
            credentialWebViewResets++;
            if(credentialWebViewResets>=3){
                // Do not attempt to bypass Perplexity/Cloudflare verification.
                // Keep the speech session alive and make the required user action
                // explicit while periodically rebuilding the stuck hidden renderer.
                setStatus(persian?"تأیید Perplexity لازم است — برنامه را باز کنید":"Perplexity verification needed — open app");
                credentialWebViewResets=0;
            }
            recreateCredentialWebView("credential callback timeout");
            armCredentialWatchdog();
        },6500L);
    }

'''
s = s.replace(bridge_marker, helpers + bridge_marker, 1)

# Every transport recovery now has an independent credential watchdog. This
# closes the v1.19.1 hole where the startup timeout was suppressed during
# recovery and the IME could remain in speechRecovering forever.
replace_once(
'''        final int epoch=++speechRecoveryEpoch;
        main.post(()->{
''',
'''        final int epoch=++speechRecoveryEpoch;
        armCredentialWatchdog();
        main.post(()->{
''',
    'arm watchdog during speech transport recovery',
)

# Startup is protected too: if evaluateJavascript never calls the bridge, rebuild
# the hidden WebView instead of immediately ending the user's session.
replace_once(
'''        main.postDelayed(()->{if(running&&awaitingCredential&&!speechRecovering){awaitingCredential=false;String d=lastCredentialError.isEmpty()?"timeout":lastCredentialError;failSession("Perplexity credential failed ("+d+")");}},CREDENTIAL_TIMEOUT_MS);
''',
'''        armCredentialWatchdog();
''',
    'replace one-shot startup credential timeout with watchdog',
)

# Replace the generated bridge methods as one block so HTTP/challenge failures
# cannot reload the same broken renderer forever.
bridge_start = s.index('    private final class CredentialBridge {')
bridge_end = s.index('\n    @Override public void onDestroy()', bridge_start)
new_bridge = r'''    private final class CredentialBridge {
        @JavascriptInterface public void credential(String apiKey,String expiresAt){main.post(()->{
            if(!running||!awaitingCredential)return;
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
            speechRecovering=false;
            startSoniox(apiKey);
        });}

        @JavascriptInterface public void credentialError(String error){main.post(()->{
            if(!running||!awaitingCredential)return;
            lastCredentialError=safeCredentialError(error);
            // Two ordinary reloads are cheap. A third failure rebuilds the actual
            // hidden WebView/JS bridge rather than repeatedly trusting pageReady.
            if(credentialAttempt<3&&auth!=null){
                retryAfterPageLoad=true;
                pageReady=false;
                setStatus(persian?"در حال بازیابی نشست Perplexity…":"Refreshing Perplexity session…");
                try{CookieManager.getInstance().flush();}catch(Exception ignored){}
                auth.reload();
                main.postDelayed(()->{if(running&&awaitingCredential&&retryAfterPageLoad){retryAfterPageLoad=false;requestCredential();}},1600L);
                return;
            }
            credentialWebViewResets++;
            if(credentialWebViewResets>=3){
                setStatus(persian?"تأیید Perplexity لازم است — برنامه را باز کنید":"Perplexity verification needed — open app");
                credentialWebViewResets=0;
            }
            recreateCredentialWebView("credential error "+lastCredentialError);
            armCredentialWatchdog();
        });}
    }
'''
s = s[:bridge_start] + new_bridge + s[bridge_end:]

# Do not leak a previous hidden WebView if Android asks the IME to recreate its
# input view while the service process itself remains alive.
replace_once(
'''        auth = new WebView(this);
        auth.setAlpha(0.01f);
        root.addView(auth, new LinearLayout.LayoutParams(1, 1));
''',
'''        if(auth!=null){
            try{auth.stopLoading();}catch(Exception ignored){}
            try{auth.removeJavascriptInterface("AndroidKeyboard");}catch(Exception ignored){}
            try{auth.destroy();}catch(Exception ignored){}
            auth=null;
        }
        auth = new WebView(this);
        auth.setAlpha(0.01f);
        root.addView(auth, new LinearLayout.LayoutParams(1, 1));
''',
    'destroy stale hidden WebView when input view is recreated',
)

if 'versionCode 34' not in g or "versionName '1.24'" not in g:
    raise SystemExit('v1.25 patch: expected v1.24 version markers missing')
g = g.replace('versionCode 34', 'versionCode 35', 1)
g = g.replace("versionName '1.24'", "versionName '1.25'", 1)

required = [
    'private volatile int credentialWatchdogEpoch;',
    'private void recreateCredentialWebView(String reason){',
    'private void armCredentialWatchdog(){',
    'credential callback timeout',
    'Perplexity verification needed',
    'Never stream partial text into the editor',
    'finishTail=finish?partialTranscript:"";',
    'versionCode 35',
    "versionName '1.25'",
]
text = s + '\n' + g
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.25 patch: required invariant missing: {needle}')

for forbidden in [
    'boundConnection.setComposingText(partial,1);',
    'versionCode 34',
    "versionName '1.24'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.25 patch: forbidden v1.24 behavior remains: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.25 recovery/cursor stability patch')
