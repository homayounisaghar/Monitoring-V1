#!/usr/bin/env python3
from pathlib import Path
import os, runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
runpy.run_path('ci/generate_chatgpt_webview_v102_dashboard_assistant_prototype_fixed2.py',run_name='__main__')

old_java=PKG/'OrchestratorDashboardV102ReplyReadAloudActivity.java'
new_java=PKG/'OrchestratorDashboardV103AssistantRepairActivity.java'
s=old_java.read_text()
for a,b in [
    ('OrchestratorDashboardV102ReplyReadAloudActivity','OrchestratorDashboardV103AssistantRepairActivity'),
    ('cp-v102-dashboard-correlated-reply-read-aloud-v1','cp-v103-dashboard-semantic-temp-telemetry-audio-source-v1'),
    ('dashboard-correlated-reply-read-aloud','dashboard-semantic-temp-telemetry-audio-source'),
    ('cp908-','cp909-'),
    ('cp_v102_stateless_planner','cp_v103_stateless_planner'),
    ('cp_v102_target_execution','cp_v103_target_execution'),
    ('cp_v102_workflow_journal','cp_v103_workflow_journal'),
    ('cp_v102_reply_wait','cp_v103_reply_wait'),
    ('cp_v102_disposable_planner','cp_v103_disposable_planner'),
    ('TelemetryConfigV102','TelemetryConfigV103'),
    ('MIC_PERMISSION_REQUEST=908','MIC_PERMISSION_REQUEST=909'),
]:
    assert a in s,a
    s=s.replace(a,b)

old='private boolean disposableTempEntryDispatched=false,pendingPlannerExecutable=false; private int tempReceiptStableHits=0,normalRestoreStableHits=0;'
new='private boolean disposableTempEntryDispatched=false,pendingPlannerExecutable=false; private int normalEntryStableHits=0,tempReceiptStableHits=0,normalRestoreStableHits=0;'
assert s.count(old)==1
s=s.replace(old,new,1)

old='plannerGeneration++;plannerPolls=0;plannerRunning=true;plannerPhase="WAIT_FRESH_HOME";plannerExpectedComposerHash="-";plannerBaselineAssistantHash="-";tempReceiptStableHits=0;normalRestoreStableHits=0;\n        plannerButton.setEnabled(false);plannerResult.setText("Planner: opening fresh home before disposable Temporary Chat...");\n        boolean ok=plannerJournal.edit().putString("request_id",plannerRequestId).putString("request_digest",plannerRequestDigest).putString("status","CLAIMED_BEFORE_FRESH_PLANNER_NAV").commit();'
new='plannerGeneration++;plannerPolls=0;plannerRunning=true;plannerPhase="WAIT_SEMANTIC_NORMAL";plannerExpectedComposerHash="-";plannerBaselineAssistantHash="-";normalEntryStableHits=0;tempReceiptStableHits=0;normalRestoreStableHits=0;\n        plannerButton.setEnabled(false);plannerResult.setText("Planner: opening a normal ChatGPT surface and proving semantic Temporary-entry state...");\n        boolean ok=plannerJournal.edit().putString("request_id",plannerRequestId).putString("request_digest",plannerRequestDigest).putString("status","CLAIMED_BEFORE_SEMANTIC_NORMAL_NAV").commit();'
assert s.count(old)==1
s=s.replace(old,new,1)

old='if("WAIT_FRESH_HOME".equals(plannerPhase)){\n                boolean fresh="complete".equals(o.optString("ready",""))&&"/".equals(path)&&o.optInt("turn_count",-1)==0&&o.optInt("composer_candidate_count",0)==1&&o.optInt("stop_candidate_count",0)==0;\n                if(!fresh){plannerLater(g);return;}\n                plannerResult.setText("Planner: fresh normal home observed; entering Temporary Chat...");plannerEnterTemp(g);return;\n            }'
new='if("WAIT_SEMANTIC_NORMAL".equals(plannerPhase)){\n                boolean normal="complete".equals(o.optString("ready",""))&&"NORMAL".equals(o.optString("semantic_temp_state",""))&&o.optInt("temp_candidate_count",0)==1&&o.optInt("composer_candidate_count",0)==1&&o.optInt("stop_candidate_count",0)==0;\n                normalEntryStableHits=normal?normalEntryStableHits+1:0;\n                if(normalEntryStableHits<2){plannerLater(g);return;}\n                plannerResult.setText("Planner: stable semantic NORMAL state proved; entering Temporary Chat...");emit("PLANNER_SEMANTIC_NORMAL_CONFIRMED",null,"CONFIRMED",jsonExtra("request_digest",plannerRequestDigest,"route_class",o.optString("route_class","UNKNOWN"),"turn_count_diag",o.optInt("turn_count",-1)));plannerEnterTemp(g);return;\n            }'
assert s.count(old)==1
s=s.replace(old,new,1)

new_java.write_text(s)
old_java.unlink()

tp=PKG/'TemporaryChatSignaturesV1.java'
t=tp.read_text()
old='if (!"HOME".equals(o.optString("route_class", ""))) return State.UNKNOWN;'
new='String route = o.optString("route_class", "");\n        if (!("HOME".equals(route) || "CONVERSATION".equals(route))) return State.UNKNOWN;'
assert t.count(old)==1
tp.write_text(t.replace(old,new,1))

(PKG/'DashboardSpeechTranscriberV100.java').write_text('package com.homayounisaghar.chatgptwebviewprobe;\n\nimport android.app.Activity;\nimport android.content.Intent;\nimport android.media.AudioFormat;\nimport android.media.AudioRecord;\nimport android.media.MediaRecorder;\nimport android.os.Build;\nimport android.os.Bundle;\nimport android.os.Handler;\nimport android.os.Looper;\nimport android.os.ParcelFileDescriptor;\nimport android.speech.RecognitionListener;\nimport android.speech.RecognizerIntent;\nimport android.speech.SpeechRecognizer;\n\nimport java.io.OutputStream;\nimport java.util.ArrayList;\nimport java.util.concurrent.ExecutorService;\nimport java.util.concurrent.Executors;\n\ninterface DashboardSpeechTranscriberV100 {\n    interface Listener {\n        void onReady();\n        void onPartial(String text);\n        void onFinal(String text);\n        void onError(int code,String name);\n    }\n    void start(String languageTag);\n    void stop();\n    void cancel();\n    void destroy();\n    boolean isBusy();\n}\n\n/** v0.90.9: one app-owned AudioRecord session on API 33+, no automatic recognizer restart loop. */\nfinal class PlatformSpeechTranscriberV100 implements DashboardSpeechTranscriberV100 {\n    private static final int SAMPLE_RATE=16000;\n    private static final long LONG_SESSION_MS=10L*60L*1000L;\n    private final Activity host;\n    private final Listener listener;\n    private final Handler main=new Handler(Looper.getMainLooper());\n    private final ExecutorService audioExecutor=Executors.newSingleThreadExecutor();\n    private final StringBuilder committed=new StringBuilder();\n    private SpeechRecognizer recognizer;\n    private AudioRecord audioRecord;\n    private ParcelFileDescriptor audioReadFd;\n    private ParcelFileDescriptor audioWriteFd;\n    private OutputStream audioPipeOut;\n    private volatile boolean captureRunning;\n    private boolean sessionActive,stopRequested,readyDelivered,finishDelivered,audioSourceMode,fallbackUsed;\n    private String languageTag="fa-IR",latestPartial="",lastSegment="";\n    private int sessionGeneration;\n\n    PlatformSpeechTranscriberV100(Activity host,Listener listener){this.host=host;this.listener=listener;}\n    @Override public boolean isBusy(){return sessionActive;}\n\n    @Override public void start(String languageTag){\n        if(sessionActive)return;\n        if(!SpeechRecognizer.isRecognitionAvailable(host)){listener.onError(-100,"RECOGNIZER_UNAVAILABLE");return;}\n        this.languageTag=(languageTag==null||languageTag.isEmpty())?"fa-IR":languageTag;\n        committed.setLength(0);latestPartial="";lastSegment="";stopRequested=false;readyDelivered=false;finishDelivered=false;fallbackUsed=false;sessionActive=true;sessionGeneration++;\n        try{createRecognizer();if(Build.VERSION.SDK_INT>=33)startAudioSourceMode();else startLegacySingleSession();}\n        catch(Exception e){cleanupAudio();failSession(-101,"START_FAILED");}\n    }\n\n    private void createRecognizer(){\n        if(recognizer!=null){try{recognizer.destroy();}catch(Exception ignored){}}\n        recognizer=SpeechRecognizer.createSpeechRecognizer(host);\n        recognizer.setRecognitionListener(new RecognitionListener(){\n            @Override public void onReadyForSpeech(Bundle params){deliverReady();}\n            @Override public void onBeginningOfSpeech(){}\n            @Override public void onRmsChanged(float rmsdB){}\n            @Override public void onBufferReceived(byte[] buffer){}\n            @Override public void onEndOfSpeech(){}\n            @Override public void onError(int error){\n                if(!sessionActive)return;if(stopRequested){finishSession(true);return;}\n                if(audioSourceMode&&!fallbackUsed){fallbackUsed=true;fallbackFromAudioSource(error);return;}\n                failSession(error,errorName(error));\n            }\n            @Override public void onResults(Bundle results){\n                if(!sessionActive)return;appendSegment(best(results));latestPartial="";\n                if(stopRequested){finishSession(false);return;}\n                if(audioSourceMode){listener.onPartial(currentCommitted());return;}\n                finishSession(false);\n            }\n            @Override public void onPartialResults(Bundle partialResults){if(!sessionActive||stopRequested)return;latestPartial=best(partialResults);listener.onPartial(currentPreview());}\n            @Override public void onSegmentResults(Bundle segmentResults){if(!sessionActive)return;appendSegment(best(segmentResults));latestPartial="";if(!stopRequested)listener.onPartial(currentCommitted());}\n            @Override public void onEndOfSegmentedSession(){\n                if(!sessionActive)return;if(stopRequested){finishSession(true);return;}\n                if(audioSourceMode&&!fallbackUsed){fallbackUsed=true;fallbackFromAudioSource(-104);return;}\n                finishSession(true);\n            }\n            @Override public void onEvent(int eventType,Bundle params){}\n        });\n    }\n\n    private Intent baseIntent(){\n        Intent i=new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);\n        i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);\n        i.putExtra(RecognizerIntent.EXTRA_LANGUAGE,languageTag);i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE,languageTag);\n        i.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS,true);i.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS,3);return i;\n    }\n\n    private void startAudioSourceMode() throws Exception {\n        audioSourceMode=true;int min=AudioRecord.getMinBufferSize(SAMPLE_RATE,AudioFormat.CHANNEL_IN_MONO,AudioFormat.ENCODING_PCM_16BIT);if(min<2048)min=4096;\n        audioRecord=new AudioRecord(MediaRecorder.AudioSource.VOICE_RECOGNITION,SAMPLE_RATE,AudioFormat.CHANNEL_IN_MONO,AudioFormat.ENCODING_PCM_16BIT,min*2);\n        if(audioRecord.getState()!=AudioRecord.STATE_INITIALIZED)throw new IllegalStateException("AUDIO_RECORD_INIT");\n        ParcelFileDescriptor[] pipe=ParcelFileDescriptor.createPipe();audioReadFd=pipe[0];audioWriteFd=pipe[1];audioPipeOut=new ParcelFileDescriptor.AutoCloseOutputStream(audioWriteFd);\n        audioRecord.startRecording();if(audioRecord.getRecordingState()!=AudioRecord.RECORDSTATE_RECORDING)throw new IllegalStateException("AUDIO_RECORD_START");\n        captureRunning=true;final int generation=sessionGeneration;audioExecutor.execute(()->pumpAudio(generation));\n        Intent i=baseIntent();i.putExtra(RecognizerIntent.EXTRA_AUDIO_SOURCE,audioReadFd);i.putExtra(RecognizerIntent.EXTRA_AUDIO_SOURCE_CHANNEL_COUNT,1);\n        i.putExtra(RecognizerIntent.EXTRA_AUDIO_SOURCE_ENCODING,AudioFormat.ENCODING_PCM_16BIT);i.putExtra(RecognizerIntent.EXTRA_AUDIO_SOURCE_SAMPLING_RATE,SAMPLE_RATE);\n        i.putExtra(RecognizerIntent.EXTRA_SEGMENTED_SESSION,RecognizerIntent.EXTRA_AUDIO_SOURCE);recognizer.startListening(i);deliverReady();\n    }\n\n    private void pumpAudio(int generation){\n        byte[] buf=new byte[4096];\n        try{while(captureRunning&&sessionActive&&generation==sessionGeneration){AudioRecord ar=audioRecord;OutputStream out=audioPipeOut;if(ar==null||out==null)break;int n=ar.read(buf,0,buf.length);\n            if(n>0){out.write(buf,0,n);out.flush();}else if(n==AudioRecord.ERROR_DEAD_OBJECT||n==AudioRecord.ERROR_INVALID_OPERATION){final int err=n;main.post(()->{if(sessionActive&&!stopRequested)fallbackFromAudioSource(err);});break;}}}\n        catch(Exception e){main.post(()->{if(sessionActive&&!stopRequested)fallbackFromAudioSource(-105);});}finally{closePipeWriter();}\n    }\n\n    private void fallbackFromAudioSource(int reason){\n        if(!sessionActive||stopRequested)return;fallbackUsed=true;cleanupAudio();try{if(recognizer!=null)recognizer.cancel();}catch(Exception ignored){}\n        main.postDelayed(()->{if(!sessionActive||stopRequested)return;try{createRecognizer();startLegacySingleSession();}catch(Exception e){failSession(reason,"AUDIO_SOURCE_UNSUPPORTED_AND_FALLBACK_FAILED");}},180L);\n    }\n\n    private void startLegacySingleSession(){\n        audioSourceMode=false;Intent i=baseIntent();i.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS,LONG_SESSION_MS);\n        i.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS,LONG_SESSION_MS);i.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS,LONG_SESSION_MS);\n        if(Build.VERSION.SDK_INT>=33)i.putExtra(RecognizerIntent.EXTRA_SEGMENTED_SESSION,RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS);\n        recognizer.startListening(i);\n    }\n\n    @Override public void stop(){\n        if(!sessionActive)return;stopRequested=true;\n        if(audioSourceMode){captureRunning=false;AudioRecord ar=audioRecord;if(ar!=null)try{ar.stop();}catch(Exception ignored){}closePipeWriter();final int generation=sessionGeneration;main.postDelayed(()->{if(sessionActive&&stopRequested&&generation==sessionGeneration)finishSession(true);},2200L);return;}\n        try{if(recognizer!=null)recognizer.stopListening();}catch(Exception ignored){}final int generation=sessionGeneration;main.postDelayed(()->{if(sessionActive&&stopRequested&&generation==sessionGeneration)finishSession(true);},1800L);\n    }\n\n    @Override public void cancel(){sessionGeneration++;captureRunning=false;sessionActive=false;stopRequested=true;latestPartial="";cleanupAudio();if(recognizer!=null)try{recognizer.cancel();}catch(Exception ignored){}}\n    @Override public void destroy(){cancel();if(recognizer!=null){try{recognizer.destroy();}catch(Exception ignored){}recognizer=null;}audioExecutor.shutdownNow();}\n    private void deliverReady(){if(!sessionActive||readyDelivered)return;readyDelivered=true;listener.onReady();}\n    private void appendSegment(String text){String t=text==null?"":text.trim();if(t.isEmpty()||t.equals(lastSegment))return;if(committed.length()>0)committed.append(\' \');committed.append(t);lastSegment=t;}\n    private String currentCommitted(){return committed.toString().trim();}\n    private String currentPreview(){String base=currentCommitted(),p=latestPartial==null?"":latestPartial.trim();if(p.isEmpty())return base;if(base.isEmpty())return p;return base+" "+p;}\n    private void finishSession(boolean includePartialFallback){\n        if(!sessionActive||finishDelivered)return;finishDelivered=true;String out=includePartialFallback?currentPreview():currentCommitted();sessionGeneration++;captureRunning=false;sessionActive=false;stopRequested=true;cleanupAudio();if(recognizer!=null)try{recognizer.cancel();}catch(Exception ignored){}\n        if(out.isEmpty())listener.onError(SpeechRecognizer.ERROR_NO_MATCH,"NO_MATCH_AFTER_STOP");else listener.onFinal(out);\n    }\n    private void failSession(int code,String name){if(finishDelivered)return;finishDelivered=true;sessionGeneration++;captureRunning=false;sessionActive=false;stopRequested=true;cleanupAudio();if(recognizer!=null)try{recognizer.cancel();}catch(Exception ignored){}listener.onError(code,name);}\n    private void cleanupAudio(){captureRunning=false;AudioRecord ar=audioRecord;audioRecord=null;if(ar!=null){try{if(ar.getRecordingState()==AudioRecord.RECORDSTATE_RECORDING)ar.stop();}catch(Exception ignored){}try{ar.release();}catch(Exception ignored){}}closePipeWriter();if(audioReadFd!=null){try{audioReadFd.close();}catch(Exception ignored){}audioReadFd=null;}if(audioWriteFd!=null){try{audioWriteFd.close();}catch(Exception ignored){}audioWriteFd=null;}}\n    private void closePipeWriter(){OutputStream out=audioPipeOut;audioPipeOut=null;if(out!=null)try{out.close();}catch(Exception ignored){}}\n    private static String best(Bundle b){if(b==null)return"";ArrayList<String> xs=b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);if(xs==null||xs.isEmpty()||xs.get(0)==null)return"";return xs.get(0).trim();}\n    private static String errorName(int e){switch(e){case SpeechRecognizer.ERROR_AUDIO:return"AUDIO";case SpeechRecognizer.ERROR_CLIENT:return"CLIENT";case SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS:return"INSUFFICIENT_PERMISSIONS";case SpeechRecognizer.ERROR_NETWORK:return"NETWORK";case SpeechRecognizer.ERROR_NETWORK_TIMEOUT:return"NETWORK_TIMEOUT";case SpeechRecognizer.ERROR_NO_MATCH:return"NO_MATCH";case SpeechRecognizer.ERROR_RECOGNIZER_BUSY:return"RECOGNIZER_BUSY";case SpeechRecognizer.ERROR_SERVER:return"SERVER";case SpeechRecognizer.ERROR_SPEECH_TIMEOUT:return"SPEECH_TIMEOUT";default:return"ERROR_"+e;}}\n}\n')

endpoint=os.environ.get('CP_TELEMETRY_ENDPOINT','').strip()
collector=os.environ.get('CP_TELEMETRY_COLLECTOR_ID','').strip()
source=os.environ.get('CP_TELEMETRY_SOURCE_REF','').strip()
assert endpoint.startswith('https://webhook.site/'), endpoint
assert collector and endpoint.endswith(collector), (endpoint,collector)
assert source, source
cfg=PKG/'TelemetryConfigV103.java'
cfg.write_text('package com.homayounisaghar.chatgptwebviewprobe;\n\nfinal class TelemetryConfigV103 {\n'
               '    static final String ENDPOINT = '+repr(endpoint)+';\n'
               '    static final String SOURCE_REF = '+repr(source)+';\n'
               '    static final String COLLECTOR_ID = '+repr(collector)+';\n'
               '    static final boolean CONFIGURED = true;\n'
               '    private TelemetryConfigV103() {}\n}\n')
cfg.write_text(cfg.read_text().replace("'",'"'))
old_cfg=PKG/'TelemetryConfigV102.java'
if old_cfg.exists(): old_cfg.unlink()

gradle=ROOT/'app/build.gradle'
g=gradle.read_text()
assert g.count('versionCode 103')==1
assert g.count("versionName '0.90.8-stable-dashboard-correlated-reply-read-aloud'")==1
g=g.replace('versionCode 103','versionCode 104',1).replace("versionName '0.90.8-stable-dashboard-correlated-reply-read-aloud'","versionName '0.90.9-stable-dashboard-semantic-temp-telemetry-audio-source'",1)
gradle.write_text(g)

man=ROOT/'app/src/main/AndroidManifest.xml'
m=man.read_text()
assert m.count('OrchestratorDashboardV102ReplyReadAloudActivity')==1
m=m.replace('OrchestratorDashboardV102ReplyReadAloudActivity','OrchestratorDashboardV103AssistantRepairActivity',1)
man.write_text(m)

for required in [
    'WAIT_SEMANTIC_NORMAL','PLANNER_SEMANTIC_NORMAL_CONFIRMED','normalEntryStableHits<2',
    'TemporaryChatSignaturesV1.exactEntryGate','TARGET_SEND_RECEIPT','TARGET_ASSISTANT_REPLY_CAPTURED',
    'TARGET_REPLY_FRESHNESS_RELOAD','SPEECH_OUTPUT_RECEIPT','setOnApplyWindowInsetsListener','DisplayCutout',
    'PREVIEW — NOT COMMITTED','WorkflowJournalGuardV1','TelemetryConfigV103.CONFIGURED'
]:
    assert required in s,required
assert '"/".equals(path)&&o.optInt("turn_count",-1)==0' not in s
assert 'WAIT_FRESH_HOME' not in s
assert s.count('targetChatEffectDispatches++')==1
voice=(PKG/'DashboardSpeechTranscriberV100.java').read_text()
for required in ['AudioRecord','EXTRA_AUDIO_SOURCE','EXTRA_SEGMENTED_SESSION','onSegmentResults','startLegacySingleSession']:
    assert required in voice,required
assert 'scheduleRestart' not in voice
assert voice.count('recognizer.startListening(i)')==2
assert 'CONFIGURED = true' in cfg.read_text()
print('PASS v0.90.9 generator: semantic Temporary entry + active telemetry + no restart-loop voice provider')
