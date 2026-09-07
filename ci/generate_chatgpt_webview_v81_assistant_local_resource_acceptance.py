#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.79: guarded assistant-local Resource acceptance for the real-device
# no-href/onclick external-link family identified by v0.78. The entire action is
# closed-loop: semantic admission -> re-certification -> durable claim -> one
# exact click -> main-frame/download/new-window receipt -> verify/reclassify.
runpy.run_path("ci/generate_chatgpt_webview_v80_assistant_local_interaction_probe.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorResourceToolsV80Activity.java"
ACT=PKG/"OrchestratorResourceToolsV81Activity.java"
s=OLD.read_text()

def method(name,body,rettype="void"):
    global s
    pat=rf'    private {re.escape(rettype)} {re.escape(name)}\([^\n]*\)\{{.*?\n    \}}\n\n'
    m=re.search(pat,s,re.S)
    assert m,(rettype,name,"method not found")
    s=s[:m.start()]+body+s[m.end():]

# Identity / update continuity.
s=s.replace("OrchestratorResourceToolsV80Activity","OrchestratorResourceToolsV81Activity")
s=s.replace("TelemetryConfigV80","TelemetryConfigV81")
s=s.replace("runResourceActionV80","runResourceActionV81")
s=s.replace("assistantLocalInteractionProbeV80Js","assistantLocalInteractionProbeV81Js")
s=s.replace("resourceTopologyProbeV80Js","resourceTopologyProbeV81Js")
s=s.replace('SCHEMA="cp-v80-assistant-local-interaction-probe-v1"','SCHEMA="cp-v81-assistant-local-resource-acceptance-v1"')
s=s.replace('SCENARIO="assistant-local-interaction-surface-read-only"','SCENARIO="assistant-local-nohref-resource-closed-loop"')
s=s.replace('getSharedPreferences("cp_v80_assistant_local_probe",MODE_PRIVATE)','getSharedPreferences("cp_v81_assistant_local_resource",MODE_PRIVATE)')
s=s.replace('testId="cp78-"+UUID.randomUUID();','testId="cp79-"+UUID.randomUUID();')
s=s.replace('v0.78 Assistant-local interaction probe ready.','v0.79 Assistant-local Resource acceptance ready.')
s=s.replace('ACTION DISABLED in v0.78 diagnostic build.','Assistant-local Resource action is closed-loop and receipt-driven.')

# Minimal chrome: one focused action control only.
pat=r'        LinearLayout row5=new LinearLayout\(this\);.*?        root\.addView\(row5,new LinearLayout\.LayoutParams\(LinearLayout\.LayoutParams\.MATCH_PARENT,dp\(42\)\)\);\n'
m=re.search(pat,s,re.S);assert m,"row5 block"
mini='''        LinearLayout row5=new LinearLayout(this); row5.setOrientation(LinearLayout.HORIZONTAL);
        Button resourceAcceptance=new Button(this); resourceAcceptance.setText("TEST RESOURCE"); resourceAcceptance.setOnClickListener(v->runResourceActionV81());
        row5.addView(resourceAcceptance,new LinearLayout.LayoutParams(0,dp(42),1f));
        root.addView(row5,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(42)));
'''
s=s[:m.start()]+mini+s[m.end():]

# Local-only action state. Raw URL stays in process memory and never enters telemetry.
field_anchor='    private boolean resourceWrappedSawSameOriginNavigation=false;\n'
assert s.count(field_anchor)==1,s.count(field_anchor)
fields='''    private String resourceV81AdmissionToken="-";
    private String resourceV81ActionOrigin="";
    private android.webkit.WebView resourceV81ChildWindow=null;
    private boolean resourceV81NewWindowObserved=false;
    private boolean resourceV81Finalized=false;
    private boolean resourceV81ClickConfirmed=false;
'''
s=s.replace(field_anchor,field_anchor+fields,1)

# Parent WebView receipts plus target-blank/script-open capture.
client=re.search(r'        web\.setWebViewClient\(new WebViewClient\(\)\{.*?\n        \}\);',s,re.S)
assert client,"web client"
client_block='''        web.setWebViewClient(new WebViewClient(){
            @Override public boolean shouldOverrideUrlLoading(WebView v,android.webkit.WebResourceRequest r){
                if(resourceNavigationPending&&r!=null&&handleResourceObservedUrlV81(r.getUrl()==null?null:r.getUrl().toString(),r.isForMainFrame(),false))return true;
                return super.shouldOverrideUrlLoading(v,r);
            }
            @Override public boolean shouldOverrideUrlLoading(WebView v,String u){
                if(resourceNavigationPending&&handleResourceObservedUrlV81(u,true,false))return true;
                return super.shouldOverrideUrlLoading(v,u);
            }
            @Override public void onPageStarted(WebView v,String u,Bitmap f){
                super.onPageStarted(v,u,f); documentEpoch++; pageFinishedReady=false; pageFinishedEpoch=-1L;
                if(resourceNavigationPending&&handleResourceObservedUrlV81(u,true,false)){try{v.stopLoading();}catch(Exception ignored){}}
                invalidateResourceV81OnDocumentStart(); closeEventBridge();
            }
            @Override public void onPageFinished(WebView v,String u){
                super.onPageFinished(v,u); pageFinishedReady=true; pageFinishedEpoch=documentEpoch; installEventBridge(documentEpoch);
                if(resourceNavigationPending)finishResourceObservedUrlV81(u,false);
            }
        });
        web.getSettings().setSupportMultipleWindows(true);
        web.getSettings().setJavaScriptCanOpenWindowsAutomatically(false);
        web.setWebChromeClient(new android.webkit.WebChromeClient(){
            @Override public boolean onCreateWindow(WebView view,boolean isDialog,boolean isUserGesture,android.os.Message resultMsg){
                if(!resourceNavigationPending||resourceV81Finalized)return super.onCreateWindow(view,isDialog,isUserGesture,resultMsg);
                resourceV81NewWindowObserved=true;
                JSONObject seen=baseState();put(seen,"resource_action_id",resourceActionPendingId);put(seen,"new_window",true);put(seen,"is_user_gesture",isUserGesture);put(seen,"is_dialog",isDialog);put(seen,"raw_url_remote",false);
                emit("RESOURCE_ACTION","RESOURCE_NEW_WINDOW_REQUEST_OBSERVED",seen);
                try{
                    destroyResourceChildWindowV81();
                    final android.webkit.WebView child=new android.webkit.WebView(OrchestratorResourceToolsV81Activity.this);resourceV81ChildWindow=child;
                    child.getSettings().setJavaScriptEnabled(true);child.getSettings().setDomStorageEnabled(true);
                    child.setWebViewClient(new WebViewClient(){
                        @Override public boolean shouldOverrideUrlLoading(WebView v,android.webkit.WebResourceRequest r){return resourceNavigationPending&&r!=null&&handleResourceObservedUrlV81(r.getUrl()==null?null:r.getUrl().toString(),r.isForMainFrame(),true);}
                        @Override public boolean shouldOverrideUrlLoading(WebView v,String u){return resourceNavigationPending&&handleResourceObservedUrlV81(u,true,true);}
                        @Override public void onPageStarted(WebView v,String u,Bitmap f){super.onPageStarted(v,u,f);if(resourceNavigationPending&&handleResourceObservedUrlV81(u,true,true)){try{v.stopLoading();}catch(Exception ignored){}}}
                        @Override public void onPageFinished(WebView v,String u){super.onPageFinished(v,u);if(resourceNavigationPending)finishResourceObservedUrlV81(u,true);}
                    });
                    android.webkit.WebView.WebViewTransport transport=(android.webkit.WebView.WebViewTransport)resultMsg.obj;transport.setWebView(child);resultMsg.sendToTarget();
                    JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"new_window_transport_attached",true);put(st,"raw_url_remote",false);
                    emit("RESOURCE_ACTION","PASS_RESOURCE_NEW_WINDOW_TRANSPORT_ATTACHED_WAITING_URL_RECEIPT",st);
                    return true;
                }catch(Exception e){
                    terminalResourceV81("NEW_WINDOW_SETUP_FAILED_NO_REPLAY","RESOURCE_ACTION_UNCERTAIN_NEW_WINDOW_SETUP_FAILED_NO_REPLAY","New-window Resource receipt setup failed; no replay.",true);
                    return false;
                }
            }
            @Override public void onCloseWindow(WebView window){
                if(resourceNavigationPending&&!resourceV81Finalized&&window!=null&&window==resourceV81ChildWindow){terminalResourceV81("NEW_WINDOW_CLOSED_WITHOUT_EXTERNAL_RECEIPT","RESOURCE_ACTION_UNCERTAIN_NEW_WINDOW_CLOSED_NO_EXTERNAL_RECEIPT","Resource new window closed without a proven external receipt; no replay.",true);}
                super.onCloseWindow(window);
            }
        });'''
s=s[:client.start()]+client_block+s[client.end():]

insert=s.index('    private void runResourceActionV81(){\n')
helpers=r'''    private String originOfV81(String u){
        try{android.net.Uri x=android.net.Uri.parse(u==null?"":u);String scheme=x.getScheme(),host=x.getHost();if(scheme==null||host==null)return "";scheme=scheme.toLowerCase(java.util.Locale.ROOT);host=host.toLowerCase(java.util.Locale.ROOT);if(!"http".equals(scheme)&&!"https".equals(scheme))return "";int port=x.getPort();return scheme+"://"+host+(port>=0?":"+port:"");}catch(Exception e){return "";}
    }

    private boolean isResourceBootstrapUrlV81(String u){
        if(u==null)return true;String x=u.trim().toLowerCase(java.util.Locale.ROOT);return x.isEmpty()||"about:blank".equals(x)||"about:srcdoc".equals(x);
    }

    private void destroyResourceChildWindowV81(){
        android.webkit.WebView c=resourceV81ChildWindow;resourceV81ChildWindow=null;if(c!=null){try{c.stopLoading();}catch(Exception ignored){}try{c.destroy();}catch(Exception ignored){}}
    }

    private void clearResourceV81TerminalState(){
        resourceNavigationPending=false;resourceDownloadPending=false;resourceWrappedInitialHref="";resourceV81AdmissionToken="-";resourceV81ActionOrigin="";resourceV81NewWindowObserved=false;
        try{if(web!=null)web.getSettings().setJavaScriptCanOpenWindowsAutomatically(false);}catch(Exception ignored){}
        destroyResourceChildWindowV81();resourceActionPendingId="-";
    }

    private void terminalResourceV81(String claimStatus,String classification,String message,boolean uncertain){
        if(resourceV81Finalized)return;resourceV81Finalized=true;
        prefs.edit().putString("resource_v81_claim_status",claimStatus).commit();
        JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"uncertain_effect",uncertain);put(st,"new_window_observed",resourceV81NewWindowObserved);put(st,"click_confirmed",resourceV81ClickConfirmed);put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);
        emit("RESOURCE_ACTION",classification,st);status.setText(message);clearResourceV81TerminalState();
    }

    private void installResourceDownloadListenerV81(){
        if(web==null)return;
        web.setDownloadListener(new android.webkit.DownloadListener(){
            @Override public void onDownloadStart(String url,String userAgent,String contentDisposition,String mimetype,long contentLength){
                if(!resourceNavigationPending||resourceV81Finalized)return;resourceV81Finalized=true;
                prefs.edit().putString("resource_v81_claim_status","CONFIRMED_DOWNLOAD_CALLBACK").commit();
                JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"download_content_length",contentLength);put(st,"download_mime_hash",hashNorm(mimetype==null?"":mimetype));put(st,"new_window_observed",resourceV81NewWindowObserved);put(st,"raw_url_remote",false);put(st,"raw_filename_remote",false);
                emit("RESOURCE_ACTION","PASS_RESOURCE_DOWNLOAD_CALLBACK_RECEIPT",st);status.setText("Resource action PASS by download callback.");clearResourceV81TerminalState();
            }
        });
    }

    private void invalidateResourceV81OnDocumentStart(){
        resourceScanDocumentEpoch=-1L;resourceScanPageFinishedEpoch=-1L;resourceSelectedId="-";resourceSelectedKind="-";resourceSelectedHref="";resourceSelectedLocatorCount=0;
        if(!resourceNavigationPending&&!resourceDownloadPending&&!resourceV81Finalized)resourceActionPendingId="-";
    }

    private boolean handleResourceObservedUrlV81(String u,boolean mainFrame,boolean childWindow){
        if(!resourceNavigationPending||resourceV81Finalized||!mainFrame||u==null)return false;
        if(isResourceBootstrapUrlV81(u)){JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"child_window",childWindow);put(st,"raw_url_remote",false);emit("RESOURCE_ACTION","RESOURCE_WINDOW_BOOTSTRAP_URL_OBSERVED_WAITING_REAL_URL",st);return false;}
        String observed=originOfV81(u);
        if(observed.isEmpty()){terminalResourceV81("UNSUPPORTED_RESOLVED_SCHEME_NO_REPLAY","RESOURCE_ACTION_UNCERTAIN_UNSUPPORTED_RESOLVED_SCHEME_NO_REPLAY","Resource resolved to an unsupported scheme; no replay.",true);return true;}
        if(observed.equals(resourceV81ActionOrigin)){
            resourceWrappedSawSameOriginNavigation=true;JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"same_origin_navigation_observed",true);put(st,"child_window",childWindow);put(st,"raw_url_remote",false);emit("RESOURCE_ACTION","RESOURCE_SAME_ORIGIN_NAVIGATION_OBSERVED_WAITING_TERMINAL_RECEIPT",st);return false;
        }
        resourceV81Finalized=true;JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"resolved_external",true);put(st,"child_window",childWindow);put(st,"new_window_observed",resourceV81NewWindowObserved);put(st,"raw_url_remote",false);
        try{android.content.Intent intent=new android.content.Intent(android.content.Intent.ACTION_VIEW,android.net.Uri.parse(u));startActivity(intent);pageUiDispatches++;pageUiWrites++;prefs.edit().putString("resource_v81_claim_status","EXTERNAL_URL_RECEIPT_OPEN_INTENT_DISPATCHED").commit();emit("RESOURCE_ACTION","PASS_RESOURCE_EXTERNAL_URL_RECEIPT_OPEN_INTENT_DISPATCHED",st);status.setText("Resource action PASS: observed external destination opened in browser.");}
        catch(Exception e){prefs.edit().putString("resource_v81_claim_status","EXTERNAL_URL_RECEIPT_OPEN_INTENT_FAILED_NO_REPLAY").commit();emit("RESOURCE_ACTION","RESOURCE_EXTERNAL_URL_RECEIPT_OPEN_INTENT_FAILED_NO_REPLAY",st);status.setText("Observed external destination could not be opened; no replay.");}
        clearResourceV81TerminalState();return true;
    }

    private void finishResourceObservedUrlV81(String u,boolean childWindow){
        if(!resourceNavigationPending||resourceV81Finalized||isResourceBootstrapUrlV81(u))return;
        if(handleResourceObservedUrlV81(u,true,childWindow))return;
        terminalResourceV81("SAME_ORIGIN_TERMINAL_NO_EXTERNAL_RECEIPT","RESOURCE_ACTION_UNCERTAIN_SAME_ORIGIN_TERMINAL_NO_EXTERNAL_RECEIPT","Resource stayed same-origin through page-finished; no external receipt, no replay.",true);
    }

'''
s=s[:insert]+helpers+s[insert:]

method('driveResourcePendingOnEventV79',r'''    private void driveResourcePendingOnEventV79(String reason){
        if(!resourceNavigationPending||resourceV81Finalized||"-".equals(resourceActionPendingId))return;
        eval(toolsMenuCensusV79Js(),o->{
            if(!resourceNavigationPending||resourceV81Finalized||"-".equals(resourceActionPendingId))return;
            if(!o.optBoolean("success",false)||!o.optBoolean("menu_materialized",false))return;
            resourceV81Finalized=true;prefs.edit().putString("resource_v81_claim_status","MISDISPATCHED_NONRESOURCE_UI_NO_REPLAY").commit();
            JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"menu_surface_count",o.optInt("menu_surface_count",0));put(st,"option_count",o.optInt("option_count",0));put(st,"event_reason_hash",hashNorm(reason));put(st,"uncertain_effect",true);put(st,"raw_text_remote",false);put(st,"raw_url_remote",false);
            emit("RESOURCE_ACTION","RESOURCE_ACTION_MISDISPATCHED_NONRESOURCE_UI",st);status.setText("Resource action FAILED: incompatible Add/Tools UI materialized. No replay authorized.");clearResourceV81TerminalState();
        });
    }

''')

method('runResourceActionV81',r'''    private void runResourceActionV81(){
        testId="cp79-"+UUID.randomUUID();startedMs=System.currentTimeMillis();telemetrySeq=0;remoteTelemetryPosts=0;
        JSONObject attempt=baseState();put(attempt,"semantic_family","ASSISTANT_LOCAL_NOHREF_OUTBOUND_ANCHOR");put(attempt,"raw_url_remote",false);put(attempt,"raw_text_remote",false);put(attempt,"raw_html_remote",false);emit("RESOURCE_ACTION","RESOURCE_ACTION_ATTEMPTED",attempt);
        if(learning||plannerRunning||toolsTestRunning||resourceDownloadPending||resourceNavigationPending){emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_BUSY",attempt);status.setText("TEST RESOURCE blocked while another operation is active.");return;}
        resourceScanDocumentEpoch=documentEpoch;resourceScanPageFinishedEpoch=pageFinishedEpoch;resourceV81Finalized=false;resourceV81ClickConfirmed=false;resourceV81NewWindowObserved=false;resourceV81AdmissionToken="-";resourceV81ActionOrigin="";resourceActionPendingId="-";
        eval(assistantLocalResourceCertifyV81Js(),o->{
            JSONObject admission=baseState();put(admission,"semantic_candidate_count",o.optInt("semantic_candidate_count",0));put(admission,"assistant_turn_count",o.optInt("assistant_turn_count",0));put(admission,"last_assistant_exists",o.optBoolean("last_assistant_exists",false));put(admission,"author_message_exists",o.optBoolean("author_message_exists",false));put(admission,"exact_unique",o.optBoolean("exact_unique",false));put(admission,"raw_url_remote",false);put(admission,"raw_text_remote",false);put(admission,"raw_html_remote",false);
            boolean epochFresh=resourceScanDocumentEpoch==documentEpoch&&resourceScanPageFinishedEpoch==pageFinishedEpoch&&pageFinishedEpoch==documentEpoch;
            String token=o.optString("candidate_token","-");boolean admitted=o.optBoolean("success",false)&&o.optBoolean("exact_unique",false)&&o.optInt("semantic_candidate_count",0)==1&&!"-".equals(token)&&epochFresh;
            put(admission,"epoch_fresh",epochFresh);put(admission,"admitted",admitted);emit("RESOURCE_DISCOVERY",admitted?"PASS_ASSISTANT_LOCAL_RESOURCE_UNIQUE_ADMITTED":"RESOURCE_ACTION_BLOCKED_NO_UNIQUE_ASSISTANT_LOCAL_RESOURCE",admission);
            if(!admitted){status.setText("TEST RESOURCE blocked: no unique strong assistant-local Resource was admitted.");return;}
            resourceV81AdmissionToken=token;
            eval(assistantLocalResourceCertifyV81Js(),r->{
                String rt=r.optString("candidate_token","-");boolean fresh=resourceScanDocumentEpoch==documentEpoch&&resourceScanPageFinishedEpoch==pageFinishedEpoch&&pageFinishedEpoch==documentEpoch&&r.optBoolean("success",false)&&r.optBoolean("exact_unique",false)&&r.optInt("semantic_candidate_count",0)==1&&token.equals(rt);
                JSONObject pre=baseState();put(pre,"semantic_candidate_count",r.optInt("semantic_candidate_count",0));put(pre,"semantic_recertified",fresh);put(pre,"same_runtime_token",token.equals(rt));put(pre,"raw_url_remote",false);put(pre,"raw_text_remote",false);put(pre,"raw_html_remote",false);
                if(!fresh){emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_SEMANTIC_RECERTIFICATION_FAILED",pre);status.setText("TEST RESOURCE blocked: semantic re-certification failed.");return;}
                String origin=originOfV81(web==null?null:web.getUrl());if(origin.isEmpty()){emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_UNSUPPORTED_CURRENT_ORIGIN",pre);status.setText("TEST RESOURCE blocked: current page origin is not a supported http(s) origin.");return;}
                String claimId="resource-v81-"+UUID.randomUUID();boolean committed=prefs.edit().putString("resource_v81_claim_status","CLAIMED").putString("resource_v81_claim_id",claimId).putString("resource_v81_candidate_token",token).commit();
                put(pre,"claim_committed",committed);emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_RESOURCE_ACTION":"RESOURCE_ACTION_CLAIM_COMMIT_FAILED",pre);
                if(!committed){status.setText("TEST RESOURCE blocked: durable claim failed.");return;}
                resourceActionPendingId=claimId;resourceV81ActionOrigin=origin;resourceWrappedSawSameOriginNavigation=false;resourceNavigationPending=true;resourceDownloadPending=false;installResourceDownloadListenerV81();
                try{web.getSettings().setJavaScriptCanOpenWindowsAutomatically(true);}catch(Exception ignored){}
                eval(assistantLocalResourceClickV81Js(token),a->{
                    boolean clicked=a.optBoolean("success",false)&&a.optBoolean("clicked",false)&&a.optBoolean("semantic_guard",false)&&a.optInt("semantic_candidate_count",0)==1&&token.equals(a.optString("candidate_token","-"));
                    JSONObject click=baseState();put(click,"semantic_guard",a.optBoolean("semantic_guard",false));put(click,"semantic_candidate_count",a.optInt("semantic_candidate_count",0));put(click,"clicked",clicked);put(click,"raw_url_remote",false);put(click,"raw_text_remote",false);put(click,"raw_html_remote",false);
                    if(clicked){resourceV81ClickConfirmed=true;pageUiDispatches++;pageUiWrites++;if(resourceV81Finalized||!resourceNavigationPending){emit("RESOURCE_ACTION","PASS_RESOURCE_EXACT_SINGLE_CLICK_CONFIRMED_AFTER_EFFECT_RECEIPT",click);}else{emit("RESOURCE_ACTION","PASS_RESOURCE_EXACT_SINGLE_CLICK_DISPATCHED_WAITING_EFFECT_RECEIPT",click);status.setText("Resource clicked once. Waiting for navigation/download/new-window receipt; do not press again.");}return;}
                    if(!resourceV81Finalized){resourceV81Finalized=true;prefs.edit().putString("resource_v81_claim_status","CLICK_UNCERTAIN_NO_REPLAY").commit();emit("RESOURCE_ACTION","RESOURCE_CLICK_UNCERTAIN_NO_REPLAY",click);status.setText("Resource click could not be proven; no replay.");clearResourceV81TerminalState();}
                });
            });
        });
    }

''')

insert=s.index('    private String assistantLocalInteractionProbeV81Js(){\n')
js_methods=r'''    private String assistantLocalResourceCertifyV81Js(){
        return "(function(){try{"+
            "const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const H=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return ('00000000'+(h>>>0).toString(16)).slice(-8);};"+
            "const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const st=getComputedStyle(e);if(st.display==='none'||st.visibility==='hidden'||st.opacity==='0')return false;try{if(typeof e.checkVisibility==='function')return e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});}catch(_){}return true;};"+
            "const SIG=e=>e?H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|'))):'-';"+
            "const turnNodes=[];const seen=new Set();const addTurn=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);turnNodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(addTurn);const turns=turnNodes.map((e,i)=>{const r=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');return{el:e,role:r?String(r.getAttribute('data-message-author-role')||'-'):'-',index:i};});const assistants=turns.filter(t=>t.role==='assistant');const last=assistants.length?assistants[assistants.length-1]:null;if(!last)return JSON.stringify({success:true,last_assistant_exists:false,author_message_exists:false,assistant_turn_count:assistants.length,semantic_candidate_count:0,exact_unique:false,candidate_token:'-'});const author=(last.el.matches&&last.el.matches('[data-message-author-role=assistant]'))?last.el:last.el.querySelector('[data-message-author-role=assistant]');if(!author)return JSON.stringify({success:true,last_assistant_exists:true,author_message_exists:false,assistant_turn_count:assistants.length,semantic_candidate_count:0,exact_unique:false,candidate_token:'-'});"+
            "const depth=e=>{let d=0,p=e;while(p&&p!==last.el){d++;p=p.parentElement;}return d;};"+
            "const anchors=Array.from(author.querySelectorAll('a')).filter(V);const good=[];for(const e of anchors){const hrefAttr=e.getAttribute('href');const noHref=hrefAttr===null||String(hrefAttr).trim()==='';const targetBlank=N(e.getAttribute('target')||'')==='_blank';const externalRel=/noopener|noreferrer|external/.test(N(e.getAttribute('rel')||''));const on=typeof e.onclick==='function'||e.hasAttribute('onclick');const st=getComputedStyle(e),ptr=N(st.cursor||'').includes('pointer'),und=N(st.textDecorationLine||st.textDecoration||'').includes('underline');const disabled=e.hasAttribute('disabled')||e.getAttribute('aria-disabled')==='true';const excluded=!!e.closest(`form,nav,aside,header,[role='navigation'],[data-testid*='composer']`);const p=e.parentElement;const parentOn=!!(p&&(typeof p.onclick==='function'||p.hasAttribute('onclick')));const parentSingle=!!(p&&p.querySelectorAll&&p.querySelectorAll('a').length===1);if(noHref&&targetBlank&&externalRel&&on&&(ptr||und)&&!disabled&&!excluded&&parentOn&&parentSingle){const token=H([SIG(e),SIG(p),depth(e),targetBlank?1:0,externalRel?1:0,on?1:0,ptr?1:0,und?1:0].join('|'));good.push({token:token});}}const unique=good.length===1;return JSON.stringify({success:true,last_assistant_exists:true,author_message_exists:true,assistant_turn_count:assistants.length,semantic_candidate_count:good.length,exact_unique:unique,candidate_token:unique?good[0].token:'-'});"+
        "}catch(e){return JSON.stringify({success:false,error_class:'ASSISTANT_LOCAL_RESOURCE_CERTIFY_EXCEPTION',semantic_candidate_count:0,exact_unique:false,candidate_token:'-'});}})()";
    }

    private String assistantLocalResourceClickV81Js(String expectedToken){
        return "(function(){try{"+
            "const expected="+jsV79(expectedToken)+";const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();const H=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return ('00000000'+(h>>>0).toString(16)).slice(-8);};const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const st=getComputedStyle(e);if(st.display==='none'||st.visibility==='hidden'||st.opacity==='0')return false;try{if(typeof e.checkVisibility==='function')return e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});}catch(_){}return true;};const SIG=e=>e?H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|'))):'-';const turnNodes=[];const seen=new Set();const addTurn=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);turnNodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(addTurn);const turns=turnNodes.map((e,i)=>{const r=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');return{el:e,role:r?String(r.getAttribute('data-message-author-role')||'-'):'-',index:i};});const assistants=turns.filter(t=>t.role==='assistant');const last=assistants.length?assistants[assistants.length-1]:null;if(!last)return JSON.stringify({success:true,clicked:false,semantic_guard:false,semantic_candidate_count:0,candidate_token:'-'});const author=(last.el.matches&&last.el.matches('[data-message-author-role=assistant]'))?last.el:last.el.querySelector('[data-message-author-role=assistant]');if(!author)return JSON.stringify({success:true,clicked:false,semantic_guard:false,semantic_candidate_count:0,candidate_token:'-'});const depth=e=>{let d=0,p=e;while(p&&p!==last.el){d++;p=p.parentElement;}return d;};const good=[];for(const e of Array.from(author.querySelectorAll('a')).filter(V)){const hrefAttr=e.getAttribute('href');const noHref=hrefAttr===null||String(hrefAttr).trim()==='';const targetBlank=N(e.getAttribute('target')||'')==='_blank';const externalRel=/noopener|noreferrer|external/.test(N(e.getAttribute('rel')||''));const on=typeof e.onclick==='function'||e.hasAttribute('onclick');const st=getComputedStyle(e),ptr=N(st.cursor||'').includes('pointer'),und=N(st.textDecorationLine||st.textDecoration||'').includes('underline');const disabled=e.hasAttribute('disabled')||e.getAttribute('aria-disabled')==='true';const excluded=!!e.closest(`form,nav,aside,header,[role='navigation'],[data-testid*='composer']`);const p=e.parentElement;const parentOn=!!(p&&(typeof p.onclick==='function'||p.hasAttribute('onclick')));const parentSingle=!!(p&&p.querySelectorAll&&p.querySelectorAll('a').length===1);if(noHref&&targetBlank&&externalRel&&on&&(ptr||und)&&!disabled&&!excluded&&parentOn&&parentSingle){const token=H([SIG(e),SIG(p),depth(e),targetBlank?1:0,externalRel?1:0,on?1:0,ptr?1:0,und?1:0].join('|'));good.push({el:e,token:token});}}if(good.length!==1||good[0].token!==expected)return JSON.stringify({success:true,clicked:false,semantic_guard:false,semantic_candidate_count:good.length,candidate_token:good.length===1?good[0].token:'-'});good[0].el.click();return JSON.stringify({success:true,clicked:true,semantic_guard:true,semantic_candidate_count:1,candidate_token:good[0].token});"+
        "}catch(e){return JSON.stringify({success:false,clicked:false,semantic_guard:false,error_class:'ASSISTANT_LOCAL_RESOURCE_CLICK_EXCEPTION',semantic_candidate_count:0,candidate_token:'-'});}})()";
    }

'''
s=s[:insert]+js_methods+s[insert:]

ACT.write_text(s);OLD.unlink()
old_cfg=PKG/"TelemetryConfigV80.java";new_cfg=PKG/"TelemetryConfigV81.java";assert old_cfg.exists();new_cfg.write_text(old_cfg.read_text().replace("TelemetryConfigV80","TelemetryConfigV81"));old_cfg.unlink()
g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+81\b","versionCode 82",gs);gs=gs.replace("0.78-stable-diag-assistant-local-interaction-probe","0.79-stable-diag-assistant-local-resource-acceptance");g.write_text(gs)
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorResourceToolsV80Activity","OrchestratorResourceToolsV81Activity");mf.write_text(ms)

out=ACT.read_text()
for required in ['TEST RESOURCE','runResourceActionV81','assistantLocalResourceCertifyV81Js','assistantLocalResourceClickV81Js','PASS_ASSISTANT_LOCAL_RESOURCE_UNIQUE_ADMITTED','RESOURCE_ACTION_BLOCKED_SEMANTIC_RECERTIFICATION_FAILED','CLAIMED_BEFORE_RESOURCE_ACTION','PASS_RESOURCE_EXACT_SINGLE_CLICK_DISPATCHED_WAITING_EFFECT_RECEIPT','RESOURCE_NEW_WINDOW_REQUEST_OBSERVED','PASS_RESOURCE_NEW_WINDOW_TRANSPORT_ATTACHED_WAITING_URL_RECEIPT','PASS_RESOURCE_EXTERNAL_URL_RECEIPT_OPEN_INTENT_DISPATCHED','PASS_RESOURCE_DOWNLOAD_CALLBACK_RECEIPT','RESOURCE_ACTION_MISDISPATCHED_NONRESOURCE_UI','setSupportMultipleWindows(true)','setJavaScriptCanOpenWindowsAutomatically(true)','targetBlank&&externalRel&&on&&(ptr||und)','parentOn&&parentSingle','TelemetryConfigV81']:
    assert required in out,required
cert=out[out.index('private String assistantLocalResourceCertifyV81Js'):out.index('private String assistantLocalInteractionProbeV81Js')]
for forbidden in ['getBoundingClientRect','elementFromPoint','document.evaluate','XPathResult','innerText','textContent','setTimeout(','setInterval(']: assert forbidden not in cert,forbidden
assert cert.count('.click();')==1,cert.count('.click();')
assert out.index('CLAIMED_BEFORE_RESOURCE_ACTION') < out.index('assistantLocalResourceClickV81Js(token)')
assert "versionCode 82" in g.read_text()
assert "versionName '0.79-stable-diag-assistant-local-resource-acceptance'" in g.read_text()
assert "OrchestratorResourceToolsV81Activity" in mf.read_text()
print('PASS v0.79 assistant-local no-href Resource closed-loop generator audit')
