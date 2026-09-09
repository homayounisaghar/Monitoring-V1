#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v98_dashboard_planner_target_confirmation.py',run_name='__main__')

old_java=PKG/'OrchestratorDashboardV98PlannerTargetConfirmationActivity.java'
new_java=PKG/'OrchestratorDashboardV99VoiceToTextActivity.java'
s=old_java.read_text()
for a,b in [
    ('OrchestratorDashboardV98PlannerTargetConfirmationActivity','OrchestratorDashboardV99VoiceToTextActivity'),
    ('cp-v98-dashboard-planner-target-confirmation-v1','cp-v99-dashboard-voice-to-text-input-v1'),
    ('dashboard-planner-target-confirmation','dashboard-voice-to-text-input'),
    ('cp904-','cp905-'),
    ('cp_v98_stateless_planner','cp_v99_stateless_planner'),
    ('cp_v98_target_execution','cp_v99_target_execution'),
    ('TelemetryConfigV98','TelemetryConfigV99'),
]:
    assert a in s,a
    s=s.replace(a,b)

old='import android.app.Activity;\nimport android.content.Context;\nimport android.content.SharedPreferences;'
new='import android.Manifest;\nimport android.app.Activity;\nimport android.content.Context;\nimport android.content.SharedPreferences;\nimport android.content.pm.PackageManager;'
assert s.count(old)==1,('imports',s.count(old))
s=s.replace(old,new,1)

old='private EditText plannerInput; private TextView plannerResult; private Button plannerButton,executeButton; private SharedPreferences plannerJournal,targetJournal;'
new='private EditText plannerInput; private TextView plannerResult; private Button plannerButton,executeButton,voiceButton; private SharedPreferences plannerJournal,targetJournal;\n    private DashboardSpeechTranscriberV99 speechTranscriber; private String voiceBaseText=""; private static final int MIC_PERMISSION_REQUEST=905;'
assert s.count(old)==1,('planner fields',s.count(old))
s=s.replace(old,new,1)

old='buildUi();\n        configureWebViews();'
new='''buildUi();
        speechTranscriber=new PlatformSpeechTranscriberV99(this,new DashboardSpeechTranscriberV99.Listener(){
            @Override public void onReady(){runOnUiThread(()->{if(voiceButton!=null){voiceButton.setText("■ STOP VOICE");voiceButton.setEnabled(true);}status.setText("Listening in Persian… speak now.");emit("VOICE_INPUT_READY",null,"UNKNOWN",null);});}
            @Override public void onPartial(String text){runOnUiThread(()->applyVoiceTranscript(text,false));}
            @Override public void onFinal(String text){runOnUiThread(()->{applyVoiceTranscript(text,true);setVoiceIdleUi();status.setText("Voice transcript ready. Review/edit it, then RUN PLANNER.");emit("VOICE_INPUT_FINAL",null,"CONFIRMED",jsonExtra("transcript_chars",text==null?0:text.length()));});}
            @Override public void onError(int code,String name){runOnUiThread(()->{setVoiceIdleUi();status.setText("Voice input failed: "+name+" ("+code+"). Typed commands still work.");emit("VOICE_INPUT_FAILED",null,"UNKNOWN",jsonExtra("error_code",code,"error_name",name));});}
        });
        configureWebViews();'''
assert s.count(old)==1,('speech init',s.count(old))
s=s.replace(old,new,1)

old='plannerInput=new EditText(this);plannerInput.setHint("Command to fresh Planner chat"); root.addView(plannerInput,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(58)));\n        LinearLayout pr=new LinearLayout(this);pr.setOrientation(LinearLayout.HORIZONTAL);plannerButton=new Button(this);plannerButton.setText("RUN PLANNER");plannerButton.setOnClickListener(v->startPlannerRequest());executeButton=new Button(this);executeButton.setText("EXECUTE");executeButton.setEnabled(false);executeButton.setOnClickListener(v->startTargetExecution());Button pc=new Button(this);pc.setText("CLEAR");pc.setOnClickListener(v->{if(!plannerRunning&&!targetExecutionRunning){plannerInput.setText("");plannerResult.setText("No Planner recipe yet.");pendingRecipe=null;pendingTargetBindingId="";pendingTargetPathHash="";pendingTargetAlias="";pendingTargetMessage="";executeButton.setText("EXECUTE");executeButton.setEnabled(false);}});pr.addView(plannerButton,new LinearLayout.LayoutParams(0,dp(42),1.2f));pr.addView(executeButton,new LinearLayout.LayoutParams(0,dp(42),1f));pr.addView(pc,new LinearLayout.LayoutParams(0,dp(42),.7f));root.addView(pr,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(42)));'
new='plannerInput=new EditText(this);plannerInput.setHint("Type or dictate a command to the fresh Planner chat"); root.addView(plannerInput,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(78)));\n        LinearLayout pr=new LinearLayout(this);pr.setOrientation(LinearLayout.HORIZONTAL);voiceButton=new Button(this);voiceButton.setText("🎤 VOICE FA");voiceButton.setOnClickListener(v->toggleVoiceInput());plannerButton=new Button(this);plannerButton.setText("RUN PLANNER");plannerButton.setOnClickListener(v->startPlannerRequest());executeButton=new Button(this);executeButton.setText("EXECUTE");executeButton.setEnabled(false);executeButton.setOnClickListener(v->startTargetExecution());Button pc=new Button(this);pc.setText("CLEAR");pc.setOnClickListener(v->{if(!plannerRunning&&!targetExecutionRunning&&!isVoiceBusy()){plannerInput.setText("");plannerResult.setText("No Planner recipe yet.");pendingRecipe=null;pendingTargetBindingId="";pendingTargetPathHash="";pendingTargetAlias="";pendingTargetMessage="";executeButton.setText("EXECUTE");executeButton.setEnabled(false);}});pr.addView(voiceButton,new LinearLayout.LayoutParams(0,dp(42),1.1f));pr.addView(plannerButton,new LinearLayout.LayoutParams(0,dp(42),1.1f));pr.addView(executeButton,new LinearLayout.LayoutParams(0,dp(42),1f));pr.addView(pc,new LinearLayout.LayoutParams(0,dp(42),.7f));root.addView(pr,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(42)));'
assert s.count(old)==1,('planner controls',s.count(old))
s=s.replace(old,new,1)

old='plannerButton.setVisibility(View.VISIBLE);executeButton.setVisibility(View.VISIBLE);plannerResult.setVisibility(View.VISIBLE);'
assert s.count(old)==3,('visible surfaces',s.count(old))
s=s.replace(old,'plannerButton.setVisibility(View.VISIBLE);voiceButton.setVisibility(View.VISIBLE);executeButton.setVisibility(View.VISIBLE);plannerResult.setVisibility(View.VISIBLE);')
old='plannerButton.setVisibility(View.GONE);executeButton.setVisibility(View.GONE);plannerResult.setVisibility(View.GONE);'
assert s.count(old)==1,('hidden surface',s.count(old))
s=s.replace(old,'plannerButton.setVisibility(View.GONE);voiceButton.setVisibility(View.GONE);executeButton.setVisibility(View.GONE);plannerResult.setVisibility(View.GONE);',1)

needle='    private void bindCurrent(){\n'
assert s.count(needle)==1
voice_methods='''    private boolean isVoiceBusy(){return speechTranscriber!=null&&speechTranscriber.isBusy();}

    private void toggleVoiceInput(){
        if(plannerRunning||targetExecutionRunning){status.setText("Finish the active transaction before voice input.");return;}
        if(speechTranscriber==null){status.setText("Voice input unavailable.");return;}
        if(speechTranscriber.isBusy()){voiceButton.setText("Finalizing…");voiceButton.setEnabled(false);speechTranscriber.stop();return;}
        if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED){requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO},MIC_PERMISSION_REQUEST);return;}
        startVoiceInput();
    }

    private void startVoiceInput(){
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

    @Override public void onRequestPermissionsResult(int requestCode,String[] permissions,int[] grantResults){
        super.onRequestPermissionsResult(requestCode,permissions,grantResults);
        if(requestCode==MIC_PERMISSION_REQUEST){
            if(grantResults.length>0&&grantResults[0]==PackageManager.PERMISSION_GRANTED)startVoiceInput();
            else status.setText("Microphone permission is required for voice input.");
        }
    }

'''
s=s.replace(needle,voice_methods+needle,1)

old='private void startPlannerRequest(){if(plannerRunning||targetExecutionRunning)return;'
new='private void startPlannerRequest(){if(isVoiceBusy()){status.setText("Finish voice input first.");return;}if(plannerRunning||targetExecutionRunning)return;'
assert s.count(old)==1,('planner voice fence',s.count(old))
s=s.replace(old,new,1)

old='@Override protected void onDestroy(){h.removeCallbacksAndMessages(null);net.shutdownNow();if(worker!=null)worker.destroy();if(foreground!=null)foreground.destroy();super.onDestroy();}'
new='@Override protected void onDestroy(){h.removeCallbacksAndMessages(null);net.shutdownNow();if(speechTranscriber!=null)speechTranscriber.destroy();if(worker!=null)worker.destroy();if(foreground!=null)foreground.destroy();super.onDestroy();}'
assert s.count(old)==1,('destroy',s.count(old))
s=s.replace(old,new,1)

for required in [
    '🎤 VOICE FA','■ STOP VOICE','speechTranscriber.start("fa-IR")','VOICE_INPUT_STARTED','VOICE_INPUT_READY','VOICE_INPUT_FINAL','VOICE_INPUT_FAILED',
    'TARGET: "+pendingTargetAlias','TARGET FROZEN: YES','TARGET_SEND_RECEIPT','EXACT_LAST_USER_HASH_AND_TURN_INCREMENT','targetChatEffectDispatches++'
]:
    assert required in s,required
assert s.count('targetChatEffectDispatches++')==1
assert s.count('.click()')==1
assert s.count('worker.loadUrl(')==1
new_java.write_text(s)

adapter=PKG/'DashboardSpeechTranscriberV99.java'
adapter.write_text(r'''package com.homayounisaghar.chatgptwebviewprobe;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;

import java.util.ArrayList;

interface DashboardSpeechTranscriberV99 {
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

final class PlatformSpeechTranscriberV99 implements DashboardSpeechTranscriberV99 {
    private final Activity host;
    private final Listener listener;
    private SpeechRecognizer recognizer;
    private boolean busy;
    private boolean finalizing;

    PlatformSpeechTranscriberV99(Activity host,Listener listener){this.host=host;this.listener=listener;}
    @Override public boolean isBusy(){return busy;}

    @Override public void start(String languageTag){
        if(busy)return;
        if(!SpeechRecognizer.isRecognitionAvailable(host)){listener.onError(-100,"RECOGNIZER_UNAVAILABLE");return;}
        try{
            if(recognizer==null){
                recognizer=SpeechRecognizer.createSpeechRecognizer(host);
                recognizer.setRecognitionListener(new RecognitionListener(){
                    @Override public void onReadyForSpeech(Bundle params){listener.onReady();}
                    @Override public void onBeginningOfSpeech(){}
                    @Override public void onRmsChanged(float rmsdB){}
                    @Override public void onBufferReceived(byte[] buffer){}
                    @Override public void onEndOfSpeech(){finalizing=true;}
                    @Override public void onError(int error){busy=false;finalizing=false;listener.onError(error,errorName(error));}
                    @Override public void onResults(Bundle results){String best=best(results);busy=false;finalizing=false;if(best.isEmpty())listener.onError(SpeechRecognizer.ERROR_NO_MATCH,"NO_MATCH");else listener.onFinal(best);}
                    @Override public void onPartialResults(Bundle partialResults){String best=best(partialResults);if(!best.isEmpty())listener.onPartial(best);}
                    @Override public void onEvent(int eventType,Bundle params){}
                });
            }
            String lang=languageTag==null||languageTag.isEmpty()?"fa-IR":languageTag;
            Intent i=new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
            i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
            i.putExtra(RecognizerIntent.EXTRA_LANGUAGE,lang);
            i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE,lang);
            i.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS,true);
            i.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS,3);
            busy=true;finalizing=false;recognizer.startListening(i);
        }catch(Exception e){busy=false;finalizing=false;listener.onError(-101,"START_FAILED");}
    }

    @Override public void stop(){if(!busy||recognizer==null)return;if(finalizing)return;finalizing=true;try{recognizer.stopListening();}catch(Exception e){busy=false;finalizing=false;listener.onError(-102,"STOP_FAILED");}}
    @Override public void cancel(){busy=false;finalizing=false;if(recognizer!=null)try{recognizer.cancel();}catch(Exception ignored){}}
    @Override public void destroy(){cancel();if(recognizer!=null){try{recognizer.destroy();}catch(Exception ignored){}recognizer=null;}}

    private static String best(Bundle b){if(b==null)return"";ArrayList<String> xs=b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);if(xs==null||xs.isEmpty()||xs.get(0)==null)return"";return xs.get(0).trim();}
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

cfg_old=PKG/'TelemetryConfigV98.java'
cfg_new=PKG/'TelemetryConfigV99.java'
cfg=cfg_old.read_text().replace('TelemetryConfigV98','TelemetryConfigV99')
assert 'CONFIGURED=false' in cfg
cfg_new.write_text(cfg)

gradle=ROOT/'app/build.gradle'
g=gradle.read_text()
assert g.count('versionCode 99')==1
assert g.count("versionName '0.90.4-stable-dashboard-planner-target-confirmation'")==1
g=g.replace('versionCode 99','versionCode 100',1).replace(
    "versionName '0.90.4-stable-dashboard-planner-target-confirmation'",
    "versionName '0.90.5-stable-dashboard-voice-to-text-input'",1)
gradle.write_text(g)

man=ROOT/'app/src/main/AndroidManifest.xml'
m=man.read_text()
assert m.count('OrchestratorDashboardV98PlannerTargetConfirmationActivity')==1
m=m.replace('OrchestratorDashboardV98PlannerTargetConfirmationActivity','OrchestratorDashboardV99VoiceToTextActivity',1)
query='''    <queries>\n        <intent>\n            <action android:name="android.speech.RecognitionService" />\n        </intent>\n    </queries>\n'''
assert '<queries>' not in m
assert m.count('    <application ')==1
m=m.replace('    <application ',query+'    <application ',1)
man.write_text(m)

print('PASS v0.90.5 generator: local Persian voice-to-text input adapter + unchanged Planner/explicit target-send path')
