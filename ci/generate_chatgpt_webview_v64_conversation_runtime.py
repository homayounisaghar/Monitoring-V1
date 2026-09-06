#!/usr/bin/env python3
from pathlib import Path
import runpy,re

runpy.run_path("ci/generate_chatgpt_webview_v63_temporary_chat_signature_unique_roundtrip.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorTemporaryChatSignatureUniqueRoundtripV63Activity.java"
ACT=PKG/"OrchestratorConversationRuntimeV64Activity.java"

activity=r'''package com.homayounisaghar.chatgptwebviewprobe;

import android.app.Activity;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class OrchestratorConversationRuntimeV64Activity extends Activity {
    private static final String SCHEMA="cp-v64-conversation-runtime-v1";
    private static final String SCENARIO="conversation-runtime-read-anchor-compose-send-lifecycle";
    private static final long SAMPLE_MS=650L;
    private static final int MAX_TRACE_RECORDS=220;
    private static final int MAX_SEND_POLLS=36;
    private static final long SEND_POLL_MS=300L;

    private final Handler h=new Handler(Looper.getMainLooper());
    private final ExecutorService net=Executors.newSingleThreadExecutor();
    private WebView web;
    private TextView status;
    private TextView localPreview;
    private EditText draftInput;
    private SharedPreferences prefs;

    private boolean learning=false;
    private boolean sendPending=false;
    private boolean returnPending=false;
    private int telemetrySeq=0;
    private int sampleIndex=0;
    private int traceRecords=0;
    private int pageUiDispatches=0;
    private int pageUiWrites=0;
    private String testId="-";
    private String anchorPath="";
    private String anchorHash="-";
    private String pendingDraftHash="-";
    private String pendingSendHash="-";
    private String lastStateFingerprint="-";
    private String lastAssistantHash="-";
    private int assistantStableHits=0;
    private String lifecycle="IDLE";
    private long startedMs=0L;

    private final Runnable sampler=new Runnable(){
        @Override public void run(){
            if(!learning)return;
            sample(false);
            h.postDelayed(this,SAMPLE_MS);
        }
    };

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        prefs=getSharedPreferences("cp_v64_conversation_runtime",MODE_PRIVATE);
        anchorPath=prefs.getString("anchor_path","");
        anchorHash=prefs.getString("anchor_hash","-");

        LinearLayout root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);
        LinearLayout row1=new LinearLayout(this); row1.setOrientation(LinearLayout.HORIZONTAL);
        Button learn=new Button(this); learn.setText("START LEARN"); learn.setOnClickListener(v->startLearn());
        Button finish=new Button(this); finish.setText("FINISH"); finish.setOnClickListener(v->finishLearn());
        Button anchor=new Button(this); anchor.setText("ANCHOR CHAT"); anchor.setOnClickListener(v->anchorCurrent());
        Button back=new Button(this); back.setText("RETURN"); back.setOnClickListener(v->returnToAnchor());
        row1.addView(learn,new LinearLayout.LayoutParams(0,dp(46),1f));
        row1.addView(finish,new LinearLayout.LayoutParams(0,dp(46),1f));
        row1.addView(anchor,new LinearLayout.LayoutParams(0,dp(46),1f));
        row1.addView(back,new LinearLayout.LayoutParams(0,dp(46),1f));
        root.addView(row1,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(46)));

        LinearLayout row2=new LinearLayout(this); row2.setOrientation(LinearLayout.HORIZONTAL);
        Button snap=new Button(this); snap.setText("SNAPSHOT"); snap.setOnClickListener(v->sample(true));
        Button setDraft=new Button(this); setDraft.setText("SET DRAFT"); setDraft.setOnClickListener(v->setDraft());
        Button send=new Button(this); send.setText("SEND"); send.setOnClickListener(v->sendCurrentDraft());
        Button clear=new Button(this); clear.setText("CLEAR LOCAL"); clear.setOnClickListener(v->clearLocal());
        row2.addView(snap,new LinearLayout.LayoutParams(0,dp(46),1f));
        row2.addView(setDraft,new LinearLayout.LayoutParams(0,dp(46),1f));
        row2.addView(send,new LinearLayout.LayoutParams(0,dp(46),1f));
        row2.addView(clear,new LinearLayout.LayoutParams(0,dp(46),1f));
        root.addView(row2,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(46)));

        draftInput=new EditText(this); draftInput.setSingleLine(false); draftInput.setHint("Local draft text (never uploaded to diagnostic telemetry)");
        root.addView(draftInput,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(64)));

        status=new TextView(this); status.setTextSize(11f); status.setPadding(dp(8),dp(4),dp(8),dp(4));
        status.setText("v0.62 Conversation Runtime ready. Raw conversation text stays local.\nSTART LEARN records a bounded local trace; ANCHOR/RETURN, SET DRAFT and SEND are fail-closed.");
        root.addView(status,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(82)));

        localPreview=new TextView(this); localPreview.setTextSize(11f); localPreview.setPadding(dp(8),dp(4),dp(8),dp(4));
        localPreview.setText("LOCAL READER PREVIEW\nNo snapshot yet.");
        root.addView(localPreview,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(138)));

        web=new WebView(this);
        WebSettings s=web.getSettings();
        s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setDatabaseEnabled(true);
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient(){
            @Override public void onPageStarted(WebView v,String u,Bitmap f){super.onPageStarted(v,u,f);}
            @Override public void onPageFinished(WebView v,String u){
                super.onPageFinished(v,u);
                if(returnPending)verifyReturnReceipt();
                if(learning){h.removeCallbacks(sampler);h.postDelayed(sampler,250L);} else sample(false);
            }
        });
        root.addView(web,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,0,1f));
        setContentView(root);
        web.loadUrl("https://chatgpt.com/");
    }

    private void startLearn(){
        if(learning)return;
        clearTraceFile();
        learning=true; sampleIndex=0; traceRecords=0; telemetrySeq=0; pageUiDispatches=0; pageUiWrites=0;
        lastStateFingerprint="-"; lastAssistantHash="-"; assistantStableHits=0; lifecycle="IDLE";
        testId="cp62-"+UUID.randomUUID(); startedMs=System.currentTimeMillis();
        JSONObject st=baseState(); put(st,"local_trace_cleared",true); put(st,"raw_text_remote",false);
        emit("LEARN_STARTED","RUNNING_LOCAL_READ_PLANE",st);
        status.setText("LEARN active. Conversation turns, route transitions and composer/generation state are being captured locally.\nRaw text is not sent to telemetry.");
        h.removeCallbacks(sampler); h.post(sampler);
    }

    private void finishLearn(){
        if(!learning){sample(true);return;}
        learning=false; h.removeCallbacks(sampler);
        eval(readJs(),o->{
            updateLifecycle(o);
            appendLocal(o,"FINISH");
            JSONObject st=sanitizedState(o); put(st,"trace_records",traceRecords); put(st,"samples",sampleIndex);
            emit("LEARN_FINISHED","LOCAL_TRACE_READY_FOR_INTERPRET",st);
            status.setText("LEARN finished. Local trace is ready. traceRecords="+traceRecords+"\nReader/anchor/composer/send/lifecycle capabilities remain available in this same APK.");
            renderLocal(o);
        });
    }

    private void sample(boolean explicit){
        if(web==null)return;
        final int n=++sampleIndex;
        eval(readJs(),o->{
            updateLifecycle(o);
            String fp=o.optString("state_fingerprint","-");
            boolean changed=!fp.equals(lastStateFingerprint);
            if(learning&&(changed||explicit||n==1||n%10==0))appendLocal(o,explicit?"EXPLICIT_SNAPSHOT":"SAMPLE");
            if(changed||explicit||n==1||n%12==0){
                JSONObject st=sanitizedState(o); put(st,"sample_index",n); put(st,"changed",changed); put(st,"explicit",explicit);
                emit("RUNTIME_SNAPSHOT",explicit?"LOCAL_EXPLICIT_SNAPSHOT":(changed?"LOCAL_STATE_CHANGED":"LOCAL_HEARTBEAT"),st);
            }
            lastStateFingerprint=fp;
            renderLocal(o);
        });
    }

    private void anchorCurrent(){
        eval(readJs(),o->{
            String route=o.optString("route_class",""),path=o.optString("local_path","");
            String ph=o.optString("local_path_hash","-");
            if(!"CONVERSATION".equals(route)||!path.matches("^/c/[^/?#]+$")){
                status.setText("ANCHOR blocked: current route is not one exact /c/<id> conversation route. No write.");
                emit("ANCHOR","ANCHOR_BLOCKED_NOT_CONVERSATION",sanitizedState(o)); return;
            }
            anchorPath=path; anchorHash=ph;
            boolean committed=prefs.edit().putString("anchor_path",anchorPath).putString("anchor_hash",anchorHash).commit();
            JSONObject st=sanitizedState(o); put(st,"anchor_hash",anchorHash); put(st,"anchor_committed",committed);
            emit("ANCHOR",committed?"LOCAL_CONVERSATION_ANCHOR_COMMITTED":"LOCAL_ANCHOR_COMMIT_FAILED",st);
            status.setText(committed?"Anchored current chat locally. anchorHash="+anchorHash:"Anchor commit failed.");
        });
    }

    private void returnToAnchor(){
        if(returnPending||anchorPath==null||!anchorPath.matches("^/c/[^/?#]+$")){
            status.setText("RETURN blocked: no valid local conversation anchor or return already pending."); return;
        }
        String claimId="return-"+UUID.randomUUID();
        boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","RETURN_TO_ANCHOR")
                .putString("claim_anchor_hash",anchorHash).putString("claim_status","CLAIMED_BEFORE_NAVIGATION").commit();
        JSONObject st=baseState(); put(st,"anchor_hash",anchorHash); put(st,"claim_committed",committed);
        emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_LOCAL_ANCHOR_NAVIGATION":"CLAIM_COMMIT_FAILED_NO_NAVIGATION",st);
        if(!committed)return;
        returnPending=true; pageUiDispatches++; pageUiWrites++;
        status.setText("CLAIMED; navigating once to local anchored chat. No replay on ambiguity.");
        web.loadUrl("https://chatgpt.com"+anchorPath);
    }

    private void verifyReturnReceipt(){
        h.postDelayed(()->eval(readJs(),o->{
            if(!returnPending)return;
            boolean ok=anchorPath.equals(o.optString("local_path",""))&&"CONVERSATION".equals(o.optString("route_class",""));
            JSONObject st=sanitizedState(o); put(st,"anchor_hash",anchorHash);
            emit("RETURN_RECEIPT",ok?"PASS_LOCAL_ANCHOR_RETURN_RECEIPT":"RETURN_RECEIPT_UNRESOLVED_NO_REPLAY",st);
            prefs.edit().putString("claim_status",ok?"RETURN_RECEIPT_CONFIRMED":"RETURN_UNCERTAIN_NO_REPLAY").commit();
            returnPending=false;
            status.setText(ok?"Returned to anchored chat; independent receipt confirmed.":"Return receipt unresolved. No replay performed.");
        }),450L);
    }

    private void setDraft(){
        if(sendPending)return;
        final String text=draftInput.getText().toString();
        if(text.trim().isEmpty()){status.setText("SET DRAFT blocked: local draft is empty.");return;}
        final String expectedHash=hashNorm(text);
        String claimId="draft-"+UUID.randomUUID();
        boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","SET_DRAFT")
                .putString("claim_payload_hash",expectedHash).putString("claim_status","CLAIMED_BEFORE_COMPOSER_WRITE").commit();
        JSONObject claim=baseState(); put(claim,"draft_hash",expectedHash); put(claim,"claim_committed",committed);
        emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_COMPOSER_WRITE":"CLAIM_COMMIT_FAILED_NO_WRITE",claim);
        if(!committed)return;
        eval(setDraftJs(text),o->{
            boolean dispatched=o.optBoolean("success",false)&&o.optBoolean("mutated",false)&&o.optInt("composer_count",0)==1
                    &&expectedHash.equals(o.optString("composer_hash",""));
            if(dispatched){pageUiDispatches++;pageUiWrites++;pendingDraftHash=expectedHash;}
            JSONObject st=sanitizedAction(o); put(st,"expected_hash",expectedHash);
            emit("COMPOSER_WRITE_DISPATCH",dispatched?"PASS_SINGLE_COMPOSER_WRITE_DISPATCHED":"COMPOSER_WRITE_UNCERTAIN_NO_REPLAY",st);
            if(!dispatched){prefs.edit().putString("claim_status","COMPOSER_WRITE_UNCERTAIN_NO_REPLAY").commit();status.setText("Composer write uncertain. No replay.");return;}
            h.postDelayed(()->eval(readJs(),r->{
                boolean receipt=r.optInt("composer_candidate_count",0)==1&&expectedHash.equals(r.optString("composer_hash",""));
                emit("COMPOSER_WRITE_RECEIPT",receipt?"PASS_COMPOSER_HASH_RECEIPT":"COMPOSER_RECEIPT_UNRESOLVED_NO_REPLAY",sanitizedState(r));
                prefs.edit().putString("claim_status",receipt?"COMPOSER_WRITE_RECEIPT_CONFIRMED":"COMPOSER_WRITE_UNCERTAIN_NO_REPLAY").commit();
                status.setText(receipt?"Draft placed in composer; receipt confirmed.":"Draft write receipt unresolved. No replay.");
                renderLocal(r);
            }),250L);
        });
    }

    private void sendCurrentDraft(){
        if(sendPending)return;
        eval(readJs(),o->{
            int cc=o.optInt("composer_candidate_count",0),chars=o.optInt("composer_chars",0),sc=o.optInt("send_candidate_count",0);
            String ch=o.optString("composer_hash","-");
            if(cc!=1||chars<=0||sc!=1||"-".equals(ch)){
                status.setText("SEND blocked: requires exactly one non-empty composer and exactly one enabled semantic Send control. No click.");
                emit("SEND_GATE","SEND_GATE_NOT_EXACT_ZERO_WRITE",sanitizedState(o));return;
            }
            pendingSendHash=ch;
            String claimId="send-"+UUID.randomUUID();
            boolean committed=prefs.edit().putString("claim_id",claimId).putString("claim_type","SEND")
                    .putString("claim_payload_hash",pendingSendHash).putString("claim_status","CLAIMED_BEFORE_SEND_CLICK").commit();
            JSONObject claim=sanitizedState(o); put(claim,"payload_hash",pendingSendHash); put(claim,"claim_committed",committed);
            emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_SEND_CLICK":"CLAIM_COMMIT_FAILED_NO_CLICK",claim);
            if(!committed)return;
            sendPending=true;
            eval(sendJs(pendingSendHash),a->{
                boolean dispatched=a.optBoolean("success",false)&&a.optBoolean("dispatched",false)&&a.optBoolean("click_observed",false)
                        &&a.optInt("send_match_count",0)==1&&pendingSendHash.equals(a.optString("composer_hash",""));
                if(dispatched){pageUiDispatches++;pageUiWrites++;}
                emit("SEND_CLICK_DISPATCH",dispatched?"PASS_EXACT_SEND_CLICK_DISPATCHED":"SEND_CLICK_UNCERTAIN_NO_REPLAY",sanitizedAction(a));
                if(!dispatched){sendPending=false;prefs.edit().putString("claim_status","SEND_CLICK_UNCERTAIN_NO_REPLAY").commit();status.setText("Send dispatch uncertain. No replay.");return;}
                status.setText("Send dispatched once. Waiting for independent user-turn receipt; no replay.");
                h.postDelayed(()->pollSendReceipt(0,0),SEND_POLL_MS);
            });
        });
    }

    private void pollSendReceipt(int attempt,int stableHits){
        if(!sendPending)return;
        eval(readJs(),o->{
            updateLifecycle(o);
            boolean match=pendingSendHash.equals(o.optString("last_user_hash",""))&&o.optInt("composer_chars",-1)==0;
            int hits=match?stableHits+1:0;
            if(match&&(hits==1||hits==2))emit("SEND_RECEIPT",hits>=2?"PASS_STABLE_USER_TURN_RECEIPT":"USER_TURN_RECEIPT_CANDIDATE_1_OF_2",sanitizedState(o));
            if(hits>=2){
                sendPending=false; prefs.edit().putString("claim_status","SEND_RECEIPT_CONFIRMED").commit();
                status.setText("Send receipt confirmed. generation="+lifecycle+". Reader will capture the assistant response locally.");
                if(learning)appendLocal(o,"SEND_RECEIPT"); renderLocal(o); return;
            }
            if(attempt>=MAX_SEND_POLLS){
                sendPending=false; prefs.edit().putString("claim_status","SEND_UNCERTAIN_NO_REPLAY").commit();
                emit("SEND_RECEIPT","SEND_RECEIPT_UNRESOLVED_NO_REPLAY",sanitizedState(o));
                status.setText("Send receipt unresolved. No replay. Current content remains readable locally."); return;
            }
            if(attempt==0||attempt==12||attempt==24)emit("SEND_RECEIPT_WAIT","READ_ONLY_POLL_NO_REPLAY",sanitizedState(o));
            h.postDelayed(()->pollSendReceipt(attempt+1,hits),SEND_POLL_MS);
        });
    }

    private void clearLocal(){
        clearTraceFile(); traceRecords=0; pendingDraftHash="-"; pendingSendHash="-";
        localPreview.setText("LOCAL READER PREVIEW\nLocal trace cleared. Conversation itself was not modified.");
        JSONObject st=baseState(); put(st,"trace_records",0); emit("LOCAL_TRACE","LOCAL_TRACE_CLEARED",st);
    }

    private void updateLifecycle(JSONObject o){
        String ah=o.optString("last_assistant_hash","-");
        int stops=o.optInt("stop_candidate_count",0);
        if(stops>0){lifecycle="GENERATING";assistantStableHits=0;}
        else if(!"-".equals(ah)){
            if(ah.equals(lastAssistantHash))assistantStableHits++;else assistantStableHits=1;
            lifecycle=assistantStableHits>=2?"COMPLETE":"ASSISTANT_PRESENT_UNSTABLE";
        } else lifecycle="IDLE";
        lastAssistantHash=ah;
    }

    private void renderLocal(JSONObject o){
        String user=clip(o.optString("last_user_text",""),180);
        String assistant=clip(o.optString("last_assistant_text",""),260);
        String composer=clip(o.optString("composer_text",""),120);
        localPreview.setText("LOCAL READER PREVIEW (never remote)\nroute="+o.optString("route_class","?")+" turns="+o.optInt("turn_count",0)+" lifecycle="+lifecycle+"\nUSER: "+user+"\nASSISTANT: "+assistant+"\nCOMPOSER: "+composer);
    }

    private void appendLocal(JSONObject o,String reason){
        if(traceRecords>=MAX_TRACE_RECORDS)return;
        try{
            JSONObject rec=new JSONObject(); rec.put("reason",reason); rec.put("timestamp_epoch_ms",System.currentTimeMillis());
            rec.put("route_class",o.optString("route_class","")); rec.put("local_path",o.optString("local_path",""));
            rec.put("generation_state",lifecycle); rec.put("turns",o.optJSONArray("turns")); rec.put("composer_text",o.optString("composer_text",""));
            rec.put("composer_hash",o.optString("composer_hash","-")); rec.put("state_fingerprint",o.optString("state_fingerprint","-"));
            byte[] b=(rec.toString()+"\n").getBytes(StandardCharsets.UTF_8);
            try(FileOutputStream fos=new FileOutputStream(traceFile(),true)){fos.write(b);fos.flush();}
            traceRecords++;
        }catch(Exception ignored){}
    }

    private File traceFile(){return new File(getFilesDir(),"conversation_runtime_trace.jsonl");}
    private void clearTraceFile(){try{File f=traceFile();if(f.exists())f.delete();}catch(Exception ignored){}}

    private String readJs(){
        return "(function(){try{"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};"+
            "const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const V=e=>{if(!e)return false;const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};"+
            "const RC=()=>{const p=location.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';if(/^\\/g\\//.test(p))return 'GPT_ROUTE';if(/^\\/project/.test(p))return 'PROJECT_ROUTE';return 'OTHER_ROUTE';};"+
            "const txt=e=>{if(!e)return '';if('value' in e&&typeof e.value==='string')return e.value;return e.innerText||e.textContent||'';};"+
            "const C=Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).filter(e=>V(e)&&!e.hasAttribute('disabled'));"+
            "const c=C.length===1?C[0]:null,ct=c?txt(c):'';"+
            "const B=Array.from(document.querySelectorAll('button,[role=button]')).filter(V);let S=[],P=[];"+
            "for(const e of B){const z=N((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('title')||'')+' '+(e.getAttribute('data-testid')||'')+' '+(e.textContent||''));if(!e.hasAttribute('disabled')&&(z==='send'||z.includes('send message')||z.includes('composer-submit')||z.includes('send-button')||z.includes('submit prompt')))S.push(e);if(z.includes('stop generating')||z.includes('stop streaming')||z==='stop')P.push(e);}"+
            "let T=[];for(const e of Array.from(document.querySelectorAll('[data-message-author-role]'))){const role=N(e.getAttribute('data-message-author-role'));if(role!=='user'&&role!=='assistant')continue;const text=(e.innerText||e.textContent||'').replace(/\\s+$/,'').trim();if(!text)continue;T.push({role:role,text:text,hash:H(N(text)),chars:text.length});}"+
            "const U=T.filter(x=>x.role==='user'),A=T.filter(x=>x.role==='assistant'),lu=U.length?U[U.length-1]:null,la=A.length?A[A.length-1]:null;"+
            "const path=location.pathname||'/';const sh=S.length===1?H([S[0].tagName.toLowerCase(),N(S[0].getAttribute('role')||'button'),N(S[0].getAttribute('data-testid')||''),N(S[0].getAttribute('aria-label')||'')].join('|')):'-';"+
            "const rows=T.map(x=>x.role+'|'+x.hash).join('~');const fp=H([RC(),H(path),H(N(ct)),S.length,P.length,rows].join('|'));"+
            "return JSON.stringify({success:true,ready:document.readyState,route_class:RC(),local_path:path,local_path_hash:H(path),turn_count:T.length,turns:T,last_user_text:lu?lu.text:'',last_user_hash:lu?lu.hash:'-',last_assistant_text:la?la.text:'',last_assistant_hash:la?la.hash:'-',composer_candidate_count:C.length,composer_text:ct,composer_hash:c?H(N(ct)):'-',composer_chars:ct.length,send_candidate_count:S.length,send_struct_hash:sh,stop_candidate_count:P.length,state_fingerprint:fp});"+
            "}catch(e){return JSON.stringify({success:false,error_class:'READ_EXCEPTION'});}})();";
    }

    private String setDraftJs(String text){
        String q=JSONObject.quote(text);
        return "(function(){try{const T="+q+";"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const C=Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).filter(e=>V(e)&&!e.hasAttribute('disabled'));if(C.length!==1)return JSON.stringify({success:false,reason:'COMPOSER_COUNT',composer_count:C.length,mutated:false});const e=C[0];"+
            "if(e.tagName==='TEXTAREA'){const d=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value');if(!d||!d.set)return JSON.stringify({success:false,reason:'NO_NATIVE_SETTER',composer_count:1,mutated:false});e.focus();d.set.call(e,T);}else{e.focus();e.textContent=T;}"+
            "e.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText',data:null}));return JSON.stringify({success:true,reason:'NATIVE_INPUT',composer_count:1,mutated:true,composer_hash:H(N(T))});"+
            "}catch(e){return JSON.stringify({success:false,reason:'WRITE_EXCEPTION',composer_count:0,mutated:false});}})();";
    }

    private String sendJs(String expectedHash){
        return "(function(){try{const EH='"+expectedHash+"';"+
            "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};const txt=e=>('value' in e&&typeof e.value==='string')?e.value:(e.innerText||e.textContent||'');"+
            "const C=Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).filter(e=>V(e)&&!e.hasAttribute('disabled'));if(C.length!==1)return JSON.stringify({success:false,reason:'COMPOSER_COUNT',send_match_count:0,dispatched:false,click_observed:false});const ch=H(N(txt(C[0])));if(ch!==EH)return JSON.stringify({success:false,reason:'COMPOSER_HASH_DRIFT',composer_hash:ch,send_match_count:0,dispatched:false,click_observed:false});"+
            "const B=Array.from(document.querySelectorAll('button,[role=button]')).filter(V),S=[];for(const e of B){const z=N((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('title')||'')+' '+(e.getAttribute('data-testid')||'')+' '+(e.textContent||''));if(!e.hasAttribute('disabled')&&(z==='send'||z.includes('send message')||z.includes('composer-submit')||z.includes('send-button')||z.includes('submit prompt')))S.push(e);}if(S.length!==1)return JSON.stringify({success:false,reason:'SEND_COUNT',composer_hash:ch,send_match_count:S.length,dispatched:false,click_observed:false});let observed=false;S[0].addEventListener('click',()=>{observed=true;},{capture:true,once:true});S[0].click();return JSON.stringify({success:true,reason:'ELEMENT_CLICK',composer_hash:ch,send_match_count:1,dispatched:true,click_observed:observed});"+
            "}catch(e){return JSON.stringify({success:false,reason:'SEND_EXCEPTION',send_match_count:0,dispatched:false,click_observed:false});}})();";
    }

    private void eval(String js,final JsonConsumer cb){
        if(web==null)return;
        web.evaluateJavascript(js,new ValueCallback<String>(){
            @Override public void onReceiveValue(String value){
                try{Object outer=new JSONTokener(value).nextValue();String raw=outer instanceof String?(String)outer:String.valueOf(outer);cb.accept(new JSONObject(raw));}
                catch(Exception e){JSONObject o=new JSONObject();put(o,"success",false);put(o,"error_class","SANITIZED_PARSE_ERROR");cb.accept(o);}
            }
        });
    }

    private JSONObject sanitizedState(JSONObject o){
        JSONObject st=baseState();
        copy(st,o,"success","ready","route_class","local_path_hash","turn_count","last_user_hash","last_assistant_hash","composer_candidate_count","composer_hash","composer_chars","send_candidate_count","send_struct_hash","stop_candidate_count","state_fingerprint");
        put(st,"generation_lifecycle",lifecycle); put(st,"trace_records",traceRecords); put(st,"anchor_hash",anchorHash); put(st,"raw_text_remote",false);
        return st;
    }

    private JSONObject sanitizedAction(JSONObject o){
        JSONObject st=baseState(); copy(st,o,"success","reason","composer_count","composer_hash","send_match_count","mutated","dispatched","click_observed"); put(st,"raw_text_remote",false); return st;
    }

    private JSONObject baseState(){
        JSONObject o=new JSONObject(); put(o,"runtime_ms",startedMs==0?0:System.currentTimeMillis()-startedMs); put(o,"learning",learning);
        put(o,"page_ui_dispatches",pageUiDispatches); put(o,"page_ui_writes",pageUiWrites); put(o,"model_option_writes",0); put(o,"effort_writes",0); put(o,"chat_work_writes",0);
        put(o,"pro_forbidden",true); put(o,"geometry_selection",false); put(o,"raw_html_remote",false); put(o,"raw_url_remote",false); put(o,"raw_chat_text_remote",false); put(o,"cookies_tokens_remote",false);
        return o;
    }

    private void emit(String phase,String classification,JSONObject state){
        if(!TelemetryConfigV64.CONFIGURED)return;
        JSONObject o=new JSONObject(); put(o,"schema_version",SCHEMA); put(o,"scenario_id",SCENARIO); put(o,"test_id",testId);
        put(o,"collector_id",TelemetryConfigV64.COLLECTOR_ID); put(o,"source_ref",TelemetryConfigV64.SOURCE_REF);
        put(o,"seq",telemetrySeq++); put(o,"timestamp_epoch_ms",System.currentTimeMillis()); put(o,"phase",phase); put(o,"classification",classification);
        try{o.put("state",state);}catch(Exception ignored){}
        final byte[] bytes=o.toString().getBytes(StandardCharsets.UTF_8);
        net.execute(()->{HttpURLConnection c=null;try{c=(HttpURLConnection)new URL(TelemetryConfigV64.WEBHOOK_URL).openConnection();c.setRequestMethod("POST");c.setConnectTimeout(5000);c.setReadTimeout(5000);c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json");c.setFixedLengthStreamingMode(bytes.length);try(OutputStream os=c.getOutputStream()){os.write(bytes);}c.getResponseCode();}catch(Exception ignored){}finally{if(c!=null)c.disconnect();}});
    }

    private static String hashNorm(String s){String n=(s==null?"":s).replaceAll("\\s+"," ").trim().toLowerCase();long h=2166136261L;for(int i=0;i<n.length();i++){h^=n.charAt(i);h=(h*16777619L)&0xffffffffL;}return String.format("%08x",h);}
    private static String clip(String s,int n){if(s==null)return "";s=s.replace('\n',' ').replace('\r',' ');return s.length()<=n?s:s.substring(0,n)+"...";}
    private static void put(JSONObject o,String k,Object v){try{o.put(k,v);}catch(Exception ignored){}}
    private static void copy(JSONObject dst,JSONObject src,String... keys){for(String k:keys)if(src.has(k))try{dst.put(k,src.get(k));}catch(Exception ignored){}}
    private int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+0.5f);}
    private interface JsonConsumer{void accept(JSONObject o);}
}
'''
ACT.write_text(activity)
if OLD.exists(): OLD.unlink()

cfg=(PKG/"TelemetryConfigV63.java").read_text()
(PKG/"TelemetryConfigV64.java").write_text(cfg.replace("TelemetryConfigV63","TelemetryConfigV64"))

# Version identity.
g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+64\b","versionCode 65",gs)
gs=gs.replace("0.61-stable-diag-temporary-chat-signature-unique-roundtrip","0.62-stable-diag-conversation-runtime")
g.write_text(gs)

# Launcher only; Accessibility identity remains V51.
m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text().replace("OrchestratorTemporaryChatSignatureUniqueRoundtripV63Activity","OrchestratorConversationRuntimeV64Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
for v in range(52,65):
    assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

out=ACT.read_text()
for required in [
    "LOCAL READER PREVIEW","START LEARN","ANCHOR CHAT","RETURN","SET DRAFT","SEND",
    "data-message-author-role","conversation_runtime_trace.jsonl","CLAIMED_BEFORE_LOCAL_ANCHOR_NAVIGATION",
    "CLAIMED_BEFORE_COMPOSER_WRITE","CLAIMED_BEFORE_SEND_CLICK","PASS_STABLE_USER_TURN_RECEIPT",
    "SEND_RECEIPT_UNRESOLVED_NO_REPLAY","raw_chat_text_remote", "TelemetryConfigV64"
]: assert required in out, required
assert out.count('.click();')==1
for forbidden in ["elementFromPoint","document.evaluate","dispatchTouchEvent(","performClick(","ACTION_SET_PROGRESS","CookieManager","getCookie(","addJavascriptInterface","setAttribute(\\\"aria-value"]:
    assert forbidden not in out, forbidden
