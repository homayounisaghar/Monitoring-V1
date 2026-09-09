#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v99_dashboard_voice_to_text.py',run_name='__main__')

old_java=PKG/'OrchestratorDashboardV99VoiceToTextActivity.java'
new_java=PKG/'OrchestratorDashboardV100VoiceManualStopAtomicActivity.java'
s=old_java.read_text()
for a,b in [
    ('OrchestratorDashboardV99VoiceToTextActivity','OrchestratorDashboardV100VoiceManualStopAtomicActivity'),
    ('cp-v99-dashboard-voice-to-text-input-v1','cp-v100-dashboard-voice-manual-stop-atomic-v1'),
    ('dashboard-voice-to-text-input','dashboard-voice-manual-stop-atomic'),
    ('cp905-','cp906-'),
    ('cp_v99_stateless_planner','cp_v100_stateless_planner'),
    ('cp_v99_target_execution','cp_v100_target_execution'),
    ('TelemetryConfigV99','TelemetryConfigV100'),
    ('DashboardSpeechTranscriberV99','DashboardSpeechTranscriberV100'),
    ('PlatformSpeechTranscriberV99','PlatformSpeechTranscriberV100'),
    ('MIC_PERMISSION_REQUEST=905','MIC_PERMISSION_REQUEST=906'),
]:
    assert a in s,a
    s=s.replace(a,b)

old='private EditText plannerInput; private TextView plannerResult; private Button plannerButton,executeButton,voiceButton;'
new='private EditText plannerInput; private TextView plannerResult,voicePreview; private Button plannerButton,executeButton,voiceButton;'
assert s.count(old)==1,('voice preview field',s.count(old))
s=s.replace(old,new,1)

old='''speechTranscriber=new PlatformSpeechTranscriberV100(this,new DashboardSpeechTranscriberV100.Listener(){
            @Override public void onReady(){runOnUiThread(()->{if(voiceButton!=null){voiceButton.setText("■ STOP VOICE");voiceButton.setEnabled(true);}status.setText("Listening in Persian… speak now.");emit("VOICE_INPUT_READY",null,"UNKNOWN",null);});}
            @Override public void onPartial(String text){runOnUiThread(()->applyVoiceTranscript(text,false));}
            @Override public void onFinal(String text){runOnUiThread(()->{applyVoiceTranscript(text,true);setVoiceIdleUi();status.setText("Voice transcript ready. Review/edit it, then RUN PLANNER.");emit("VOICE_INPUT_FINAL",null,"CONFIRMED",jsonExtra("transcript_chars",text==null?0:text.length()));});}
            @Override public void onError(int code,String name){runOnUiThread(()->{setVoiceIdleUi();status.setText("Voice input failed: "+name+" ("+code+"). Typed commands still work.");emit("VOICE_INPUT_FAILED",null,"UNKNOWN",jsonExtra("error_code",code,"error_name",name));});}
        });'''
new='''speechTranscriber=new PlatformSpeechTranscriberV100(this,new DashboardSpeechTranscriberV100.Listener(){
            @Override public void onReady(){runOnUiThread(()->{if(voiceButton!=null){voiceButton.setText("■ STOP VOICE");voiceButton.setEnabled(true);}status.setText("Listening in Persian — stays active until you press STOP.");emit("VOICE_INPUT_READY",null,"UNKNOWN",null);});}
            @Override public void onPartial(String text){runOnUiThread(()->applyVoicePreview(text));}
            @Override public void onFinal(String text){runOnUiThread(()->{commitVoiceFinal(text);setVoiceIdleUi();status.setText("Voice transcript committed once. Review/edit it, then RUN PLANNER.");emit("VOICE_INPUT_FINAL",null,"CONFIRMED",jsonExtra("transcript_chars",text==null?0:text.length()));});}
            @Override public void onError(int code,String name){runOnUiThread(()->{if(voicePreview!=null){voicePreview.setText("");voicePreview.setVisibility(View.GONE);}setVoiceIdleUi();status.setText("Voice input failed: "+name+" ("+code+"). Command text was not changed.");emit("VOICE_INPUT_FAILED",null,"UNKNOWN",jsonExtra("error_code",code,"error_name",name));});}
        });'''
assert s.count(old)==1,('speech listener',s.count(old))
s=s.replace(old,new,1)

old='plannerInput=new EditText(this);plannerInput.setHint("Type or dictate a command to the fresh Planner chat"); root.addView(plannerInput,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(78)));'
new=old+'''
        voicePreview=new TextView(this);voicePreview.setTextSize(12f);voicePreview.setPadding(dp(10),dp(4),dp(10),dp(4));voicePreview.setVisibility(View.GONE);root.addView(voicePreview,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(56)));'''
assert s.count(old)==1,('voice preview ui',s.count(old))
s=s.replace(old,new,1)

old='''    private void startVoiceInput(){
        if(speechTranscriber==null||speechTranscriber.isBusy())return;
        voiceBaseText=plannerInput.getText().toString().trim();
        voiceButton.setText("Starting…");voiceButton.setEnabled(false);plannerButton.setEnabled(false);
        status.setText("Starting Persian voice input…");
        emit("VOICE_INPUT_STARTED",null,"UNKNOWN",null);
        speechTranscriber.start("fa-IR");
    }

    private void applyVoiceTranscript(String transcript,boolean isFinal){
        String t=transcript==null?"":transcript.trim();if(t.isEmpty())return;
        String combined=voiceBaseText.isEmpty()?t:(voiceBaseText+" "+t);
        plannerInput.setText(combined);plannerInput.setSelection(combined.length());
        if(!isFinal)status.setText("Listening… transcript is editable after Stop.");
    }

    private void setVoiceIdleUi(){
        if(voiceButton!=null){voiceButton.setText("🎤 VOICE FA");voiceButton.setEnabled(true);}
        if(plannerButton!=null)plannerButton.setEnabled(!plannerRunning&&!targetExecutionRunning);
    }

'''
new='''    private void startVoiceInput(){
        if(speechTranscriber==null||speechTranscriber.isBusy())return;
        voiceBaseText=plannerInput.getText().toString().trim();
        if(voicePreview!=null){voicePreview.setText("Voice preview (not committed yet)…");voicePreview.setVisibility(View.VISIBLE);}
        voiceButton.setText("Starting…");voiceButton.setEnabled(false);plannerButton.setEnabled(false);plannerInput.setEnabled(false);
        status.setText("Starting Persian voice input… it will stay active until STOP.");
        emit("VOICE_INPUT_STARTED",null,"UNKNOWN",null);
        speechTranscriber.start("fa-IR");
    }

    private void applyVoicePreview(String transcript){
        String t=transcript==null?"":transcript.trim();
        if(voicePreview==null)return;
        voicePreview.setVisibility(View.VISIBLE);
        voicePreview.setText(t.isEmpty()?"Voice preview (not committed yet)…":"PREVIEW — NOT COMMITTED:\\n"+t);
        status.setText("Listening… partials stay in preview; press STOP to commit once.");
    }

    private void commitVoiceFinal(String transcript){
        String t=transcript==null?"":transcript.trim();
        if(t.isEmpty())return;
        String combined=voiceBaseText.isEmpty()?t:(voiceBaseText+" "+t);
        plannerInput.setText(combined);plannerInput.setSelection(combined.length());
        if(voicePreview!=null){voicePreview.setText("");voicePreview.setVisibility(View.GONE);}
    }

    private void setVoiceIdleUi(){
        if(voiceButton!=null){voiceButton.setText("🎤 VOICE FA");voiceButton.setEnabled(true);}
        if(plannerButton!=null)plannerButton.setEnabled(!plannerRunning&&!targetExecutionRunning);
        if(plannerInput!=null)plannerInput.setEnabled(true);
    }

'''
assert s.count(old)==1,('voice methods',s.count(old))
s=s.replace(old,new,1)

old='dash.setText("DASHBOARD");dash.setOnClickListener(v->{if(!plannerRunning&&!targetExecutionRunning)showDashboard("Dashboard");});'
new='dash.setText("DASHBOARD");dash.setOnClickListener(v->{if(!plannerRunning&&!targetExecutionRunning&&!isVoiceBusy())showDashboard("Dashboard");else if(isVoiceBusy())status.setText("Stop voice input before changing surfaces.");});'
assert s.count(old)==1,('dashboard voice fence',s.count(old))
s=s.replace(old,new,1)

old='Button chat=new Button(this);chat.setText("CHAT");chat.setOnClickListener(v->{if(plannerRunning||targetExecutionRunning){status.setText("Transaction active; navigation fenced.");return;}showChat("Chat");});'
new='Button chat=new Button(this);chat.setText("CHAT");chat.setOnClickListener(v->{if(plannerRunning||targetExecutionRunning||isVoiceBusy()){status.setText("Transaction or voice input active; navigation fenced.");return;}showChat("Chat");});'
assert s.count(old)==1,('chat voice fence',s.count(old))
s=s.replace(old,new,1)

old='Button refresh=new Button(this);refresh.setText("REFRESH ALL");refresh.setOnClickListener(v->{if(plannerRunning||targetExecutionRunning){status.setText("Transaction active; refresh fenced.");return;}if(scheduler!=null)scheduler.refreshAll();});'
new='Button refresh=new Button(this);refresh.setText("REFRESH ALL");refresh.setOnClickListener(v->{if(plannerRunning||targetExecutionRunning||isVoiceBusy()){status.setText("Transaction or voice input active; refresh fenced.");return;}if(scheduler!=null)scheduler.refreshAll();});'
assert s.count(old)==1,('refresh voice fence',s.count(old))
s=s.replace(old,new,1)

old='private void showChat(String msg){if(plannerRunning||targetExecutionRunning){status.setText("Transaction active; Chat mode fenced.");return;}'
new='private void showChat(String msg){if(plannerRunning||targetExecutionRunning||isVoiceBusy()){status.setText("Transaction or voice input active; Chat mode fenced.");return;}'
assert s.count(old)==1,('show chat voice fence',s.count(old))
s=s.replace(old,new,1)

for required in [
    'PREVIEW — NOT COMMITTED',
    'commitVoiceFinal(text)',
    'plannerInput.setEnabled(false)',
    'stays active until you press STOP',
    'TARGET: "+pendingTargetAlias',
    'TARGET FROZEN: YES',
    'TARGET_SEND_RECEIPT',
    'EXACT_LAST_USER_HASH_AND_TURN_INCREMENT',
    'targetChatEffectDispatches++',
]:
    assert required in s,required
assert 'applyVoiceTranscript' not in s
assert s.count('targetChatEffectDispatches++')==1
assert s.count('.click()')==1
assert s.count('worker.loadUrl(')==1
new_java.write_text(s)

adapter=PKG/'DashboardSpeechTranscriberV100.java'
adapter.write_text(r'''package com.homayounisaghar.chatgptwebviewprobe;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;

import java.util.ArrayList;

interface DashboardSpeechTranscriberV100 {
    interface Listener {
        void onReady();
        void onPartial(String text);
        void onFinal(String text);
        void onError(int code,String name);
    }
    void start(String languageTag);
    void stop();
    void cancel();
    void destroy();
    boolean isBusy();
}

final class PlatformSpeechTranscriberV100 implements DashboardSpeechTranscriberV100 {
    private final Activity host;
    private final Listener listener;
    private final Handler main=new Handler(Looper.getMainLooper());
    private final StringBuilder committed=new StringBuilder();

    private SpeechRecognizer recognizer;
    private boolean sessionActive;
    private boolean cycleActive;
    private boolean stopRequested;
    private boolean readyDelivered;
    private boolean finishDelivered;
    private String languageTag="fa-IR";
    private String latestPartial="";
    private String lastSegment="";
    private int restartGeneration;

    PlatformSpeechTranscriberV100(Activity host,Listener listener){
        this.host=host;
        this.listener=listener;
    }

    @Override public boolean isBusy(){return sessionActive;}

    @Override public void start(String languageTag){
        if(sessionActive)return;
        if(!SpeechRecognizer.isRecognitionAvailable(host)){
            listener.onError(-100,"RECOGNIZER_UNAVAILABLE");
            return;
        }
        this.languageTag=(languageTag==null||languageTag.isEmpty())?"fa-IR":languageTag;
        committed.setLength(0);
        latestPartial="";
        lastSegment="";
        stopRequested=false;
        readyDelivered=false;
        finishDelivered=false;
        sessionActive=true;
        cycleActive=false;
        restartGeneration++;
        try{
            ensureRecognizer();
            startCycle();
        }catch(Exception e){
            failSession(-101,"START_FAILED");
        }
    }

    private void ensureRecognizer(){
        if(recognizer!=null)return;
        recognizer=SpeechRecognizer.createSpeechRecognizer(host);
        recognizer.setRecognitionListener(new RecognitionListener(){
            @Override public void onReadyForSpeech(Bundle params){
                if(!sessionActive)return;
                if(!readyDelivered){
                    readyDelivered=true;
                    listener.onReady();
                }
            }
            @Override public void onBeginningOfSpeech(){}
            @Override public void onRmsChanged(float rmsdB){}
            @Override public void onBufferReceived(byte[] buffer){}
            @Override public void onEndOfSpeech(){}

            @Override public void onError(int error){
                if(!sessionActive)return;
                cycleActive=false;
                if(stopRequested){
                    finishSession(true);
                    return;
                }
                if(error==SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS||error==SpeechRecognizer.ERROR_AUDIO){
                    failSession(error,errorName(error));
                    return;
                }
                scheduleRestart(error==SpeechRecognizer.ERROR_RECOGNIZER_BUSY?350L:140L);
            }

            @Override public void onResults(Bundle results){
                if(!sessionActive)return;
                cycleActive=false;
                String best=best(results);
                latestPartial="";
                appendSegment(best);
                if(stopRequested){
                    finishSession(false);
                    return;
                }
                listener.onPartial(currentCommitted());
                scheduleRestart(120L);
            }

            @Override public void onPartialResults(Bundle partialResults){
                if(!sessionActive||stopRequested)return;
                latestPartial=best(partialResults);
                listener.onPartial(currentPreview());
            }

            @Override public void onEvent(int eventType,Bundle params){}
        });
    }

    private void startCycle(){
        if(!sessionActive||stopRequested)return;
        try{
            ensureRecognizer();
            Intent i=new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
            i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
            i.putExtra(RecognizerIntent.EXTRA_LANGUAGE,languageTag);
            i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE,languageTag);
            i.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS,true);
            i.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS,3);
            latestPartial="";
            cycleActive=true;
            recognizer.startListening(i);
        }catch(Exception e){
            cycleActive=false;
            if(sessionActive&&!stopRequested)scheduleRestart(350L);
        }
    }

    private void scheduleRestart(long delayMs){
        if(!sessionActive||stopRequested)return;
        final int generation=++restartGeneration;
        main.postDelayed(()->{
            if(!sessionActive||stopRequested||generation!=restartGeneration)return;
            startCycle();
        },delayMs);
    }

    @Override public void stop(){
        if(!sessionActive)return;
        stopRequested=true;
        restartGeneration++;
        if(cycleActive&&recognizer!=null){
            try{
                recognizer.stopListening();
                main.postDelayed(()->{
                    if(sessionActive&&stopRequested)finishSession(true);
                },1800L);
                return;
            }catch(Exception ignored){}
        }
        finishSession(true);
    }

    @Override public void cancel(){
        restartGeneration++;
        sessionActive=false;
        cycleActive=false;
        stopRequested=true;
        latestPartial="";
        if(recognizer!=null)try{recognizer.cancel();}catch(Exception ignored){}
    }

    @Override public void destroy(){
        cancel();
        if(recognizer!=null){
            try{recognizer.destroy();}catch(Exception ignored){}
            recognizer=null;
        }
    }

    private void appendSegment(String text){
        String t=text==null?"":text.trim();
        if(t.isEmpty())return;
        if(t.equals(lastSegment))return;
        if(committed.length()>0)committed.append(' ');
        committed.append(t);
        lastSegment=t;
    }

    private String currentCommitted(){
        return committed.toString().trim();
    }

    private String currentPreview(){
        String base=currentCommitted();
        String p=latestPartial==null?"":latestPartial.trim();
        if(p.isEmpty())return base;
        if(base.isEmpty())return p;
        return base+" "+p;
    }

    private void finishSession(boolean includePartialFallback){
        if(!sessionActive||finishDelivered)return;
        finishDelivered=true;
        String out=includePartialFallback?currentPreview():currentCommitted();
        sessionActive=false;
        cycleActive=false;
        stopRequested=true;
        restartGeneration++;
        if(recognizer!=null)try{recognizer.cancel();}catch(Exception ignored){}
        if(out.isEmpty())listener.onError(SpeechRecognizer.ERROR_NO_MATCH,"NO_MATCH_AFTER_STOP");
        else listener.onFinal(out);
    }

    private void failSession(int code,String name){
        if(!sessionActive&&finishDelivered)return;
        restartGeneration++;
        sessionActive=false;
        cycleActive=false;
        stopRequested=true;
        finishDelivered=true;
        if(recognizer!=null)try{recognizer.cancel();}catch(Exception ignored){}
        listener.onError(code,name);
    }

    private static String best(Bundle b){
        if(b==null)return"";
        ArrayList<String> xs=b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
        if(xs==null||xs.isEmpty()||xs.get(0)==null)return"";
        return xs.get(0).trim();
    }

    private static String errorName(int e){
        switch(e){
            case SpeechRecognizer.ERROR_AUDIO:return"AUDIO";
            case SpeechRecognizer.ERROR_CLIENT:return"CLIENT";
            case SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS:return"INSUFFICIENT_PERMISSIONS";
            case SpeechRecognizer.ERROR_NETWORK:return"NETWORK";
            case SpeechRecognizer.ERROR_NETWORK_TIMEOUT:return"NETWORK_TIMEOUT";
            case SpeechRecognizer.ERROR_NO_MATCH:return"NO_MATCH";
            case SpeechRecognizer.ERROR_RECOGNIZER_BUSY:return"RECOGNIZER_BUSY";
            case SpeechRecognizer.ERROR_SERVER:return"SERVER";
            case SpeechRecognizer.ERROR_SPEECH_TIMEOUT:return"SPEECH_TIMEOUT";
            default:return"ERROR_"+e;
        }
    }
}
''')

cfg_old=PKG/'TelemetryConfigV99.java'
cfg_new=PKG/'TelemetryConfigV100.java'
cfg=cfg_old.read_text().replace('TelemetryConfigV99','TelemetryConfigV100')
assert 'CONFIGURED=false' in cfg
cfg_new.write_text(cfg)

gradle=ROOT/'app/build.gradle'
g=gradle.read_text()
assert g.count('versionCode 100')==1
assert g.count("versionName '0.90.5-stable-dashboard-voice-to-text-input'")==1
g=g.replace('versionCode 100','versionCode 101',1).replace(
    "versionName '0.90.5-stable-dashboard-voice-to-text-input'",
    "versionName '0.90.6-stable-dashboard-voice-manual-stop-atomic'",1)
gradle.write_text(g)

man=ROOT/'app/src/main/AndroidManifest.xml'
m=man.read_text()
assert m.count('OrchestratorDashboardV99VoiceToTextActivity')==1
m=m.replace('OrchestratorDashboardV99VoiceToTextActivity','OrchestratorDashboardV100VoiceManualStopAtomicActivity',1)
man.write_text(m)

print('PASS v0.90.6 generator: preview-only partials + atomic manual-stop commit + automatic recognizer restart + unchanged Planner/execute path')
