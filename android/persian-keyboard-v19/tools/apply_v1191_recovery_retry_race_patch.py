from pathlib import Path

p = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
s = p.read_text()


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.19.1 patch: missing pattern: {label}')
    s = s.replace(old, new, 1)

replace_once(
'''        main.postDelayed(()->{if(running&&awaitingCredential){awaitingCredential=false;String d=lastCredentialError.isEmpty()?"timeout":lastCredentialError;failSession("Perplexity credential failed ("+d+")");}},CREDENTIAL_TIMEOUT_MS);
''',
'''        main.postDelayed(()->{if(running&&awaitingCredential&&!speechRecovering){awaitingCredential=false;String d=lastCredentialError.isEmpty()?"timeout":lastCredentialError;failSession("Perplexity credential failed ("+d+")");}},CREDENTIAL_TIMEOUT_MS);
''',
    'startup credential timeout must not kill active recovery',
)

replace_once(
'''        @JavascriptInterface public void credential(String apiKey,String expiresAt){main.post(()->{if(!running||!awaitingCredential)return;awaitingCredential=false;retryAfterPageLoad=false;if(apiKey==null||apiKey.isEmpty()){if(speechRecovering){awaitingCredential=true;main.postDelayed(PersianKeyboardService.this::requestCredential,1200L);return;}failSession("Perplexity returned no credential");return;}startSoniox(apiKey);});}
''',
'''        @JavascriptInterface public void credential(String apiKey,String expiresAt){main.post(()->{if(!running||!awaitingCredential)return;awaitingCredential=false;retryAfterPageLoad=false;if(apiKey==null||apiKey.isEmpty()){if(speechRecovering){awaitingCredential=true;main.postDelayed(PersianKeyboardService.this::requestCredential,1200L);return;}failSession("Perplexity returned no credential");return;}speechRecovering=false;startSoniox(apiKey);});}
''',
    'allow repeated replacement-WebSocket recovery',
)

for needle in [
    'if(running&&awaitingCredential&&!speechRecovering)',
    'speechRecovering=false;startSoniox(apiKey);',
    'private void recoverSpeechTransport(String reason){',
    'recoverSpeechTransport("Connection error")',
]:
    if needle not in s:
        raise SystemExit(f'v1.19.1 patch: required invariant missing: {needle}')

p.write_text(s)
print('Applied v1.19 recovery retry-race hardening patch')
