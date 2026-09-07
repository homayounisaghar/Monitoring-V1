#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.76: repair the real-device v0.75 false-negative while preserving the v0.75
# Add/Attach exclusion and semantic re-certification. Add a bounded final-assistant
# resource corridor, same-origin wrapped-link navigation receipts, and a terminal
# telemetry classification for every TEST ACTION press.
runpy.run_path("ci/generate_chatgpt_webview_v77_resource_provenance_hardened_fix1.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorResourceToolsV77Activity.java"
ACT=PKG/"OrchestratorResourceToolsV78Activity.java"
s=OLD.read_text()

def method(name,body,rettype="void"):
    global s
    pat=rf'    private {re.escape(rettype)} {re.escape(name)}\([^\n]*\)\{{.*?\n    \}}\n\n'
    m=re.search(pat,s,re.S)
    assert m,(rettype,name,"method not found")
    s=s[:m.start()]+body+s[m.end():]

def once(old,new,label):
    global s
    n=s.count(old)
    assert n==1,(label,n)
    s=s.replace(old,new,1)

# Identity rollover.
s=s.replace("OrchestratorResourceToolsV77Activity","OrchestratorResourceToolsV78Activity")
s=s.replace("TelemetryConfigV77","TelemetryConfigV78")
s=s.replace("V77","V78")
s=s.replace("resourceResolverV3Js","resourceResolverV4Js")
s=s.replace("RESOURCE_RESOLVER_V3","RESOURCE_RESOLVER_V4")
s=s.replace('SCHEMA="cp-v77-resource-provenance-hardened-v1"','SCHEMA="cp-v78-resource-final-bounded-wrapped-v1"')
s=s.replace('SCENARIO="resource-provenance-action-recertification"','SCENARIO="resource-final-bounded-wrapped-navigation-receipt"')
s=s.replace('getSharedPreferences("cp_v77_resource_provenance",MODE_PRIVATE)','getSharedPreferences("cp_v78_resource_final_bounded",MODE_PRIVATE)')
s=s.replace('testId="cp75-"+UUID.randomUUID();','testId="cp76-"+UUID.randomUUID();')
s=s.replace('resource_v77_claim_','resource_v78_claim_')
s=s.replace('data-cp-resource-locator-v77','data-cp-resource-locator-v78')
s=s.replace('__cpResourceResolverV77','__cpResourceResolverV78')
s=s.replace('v0.75 Resource provenance hardened + Tools ready.','v0.76 Final-bounded wrapped-resource resolver + Tools ready.')

# New local-only state. Raw wrapper URL never enters telemetry.
field_anchor='    private String resourceActionPendingId="-";\n'
assert s.count(field_anchor)==1,s.count(field_anchor)
fields='''    private boolean resourceNavigationPending=false;
    private String resourceWrappedInitialHref="";
    private boolean resourceWrappedSawSameOriginNavigation=false;
'''
s=s.replace(field_anchor,field_anchor+fields,1)

# Extend the WebViewClient with receipt-driven wrapped-link handling. Same-origin
# wrapper navigation is allowed; a later observed external main-frame destination
# is intercepted and dispatched through Android ACTION_VIEW under the durable claim.
client=re.search(r'        web\.setWebViewClient\(new WebViewClient\(\)\{.*?\n        \}\);',s,re.S)
assert client,"web client"
s=s[:client.start()]+'''        web.setWebViewClient(new WebViewClient(){
            @Override public boolean shouldOverrideUrlLoading(WebView v,android.webkit.WebResourceRequest r){
                if(resourceNavigationPending&&r!=null&&handleResourceNavigationV78(r.getUrl()==null?null:r.getUrl().toString(),r.isForMainFrame()))return true;
                return super.shouldOverrideUrlLoading(v,r);
            }
            @Override public boolean shouldOverrideUrlLoading(WebView v,String u){
                if(resourceNavigationPending&&handleResourceNavigationV78(u,true))return true;
                return super.shouldOverrideUrlLoading(v,u);
            }
            @Override public void onPageStarted(WebView v,String u,Bitmap f){
                super.onPageStarted(v,u,f); documentEpoch++; pageFinishedReady=false; pageFinishedEpoch=-1L;
                if(resourceNavigationPending&&handleResourceNavigationV78(u,true)){try{v.stopLoading();}catch(Exception ignored){}}
                invalidateResourceV78OnDocumentStart(); closeEventBridge();
            }
            @Override public void onPageFinished(WebView v,String u){
                super.onPageFinished(v,u); pageFinishedReady=true; pageFinishedEpoch=documentEpoch; installEventBridge(documentEpoch);
                if(resourceNavigationPending)finishResourceNavigationV78(u);
            }
        });'''+s[client.end():]

# Download callback is also a valid receipt for a wrapped resource action.
method('installResourceDownloadListenerV78',r'''    private void installResourceDownloadListenerV78(){
        if(web==null)return;
        web.setDownloadListener(new android.webkit.DownloadListener(){
            @Override public void onDownloadStart(String url,String userAgent,String contentDisposition,String mimetype,long contentLength){
                if(!resourceDownloadPending&&!resourceNavigationPending)return;
                resourceDownloadPending=false;resourceNavigationPending=false;resourceWrappedInitialHref="";
                prefs.edit().putString("resource_v78_claim_status","CONFIRMED_DOWNLOAD_CALLBACK").commit();
                JSONObject st=baseState();
                put(st,"resource_action_id",resourceActionPendingId);put(st,"download_content_length",contentLength);
                put(st,"download_mime_hash",hashNorm(mimetype==null?"":mimetype));put(st,"raw_url_remote",false);put(st,"raw_filename_remote",false);
                emit("RESOURCE_ACTION","PASS_RESOURCE_DOWNLOAD_CALLBACK_RECEIPT",st);
                status.setText("Resource action PASS by download callback.");
                resourceActionPendingId="-";
            }
        });
    }

''')

# A wrapped-navigation action survives its own document transition long enough to
# observe the destination. Other pending download actions retain the v0.75 fail-closed behavior.
method('invalidateResourceV78OnDocumentStart',r'''    private void invalidateResourceV78OnDocumentStart(){
        if(resourceNavigationPending){
            resourceScanDocumentEpoch=-1L;resourceScanPageFinishedEpoch=-1L;resourceSelectedId="-";resourceSelectedKind="-";resourceSelectedHref="";resourceSelectedLocatorCount=0;
            return;
        }
        if(resourceDownloadPending){
            resourceDownloadPending=false;
            prefs.edit().putString("resource_v78_claim_status","UNCERTAIN_ROUTE_CHANGED_NO_DOWNLOAD_RECEIPT").commit();
            JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"uncertain_effect",true);
            emit("RESOURCE_ACTION","RESOURCE_ACTION_UNCERTAIN_ROUTE_CHANGED_NO_DOWNLOAD_RECEIPT",st);
        }
        resourceScanDocumentEpoch=-1L;resourceScanPageFinishedEpoch=-1L;resourceSelectedId="-";resourceSelectedKind="-";resourceSelectedHref="";resourceSelectedLocatorCount=0;resourceActionPendingId="-";
    }

''')

method('runResourceTest',r'''    private void runResourceTest(){
        if(learning||plannerRunning||toolsTestRunning||resourceDownloadPending||resourceNavigationPending){status.setText("RESOURCE TEST blocked while another test/action is active.");return;}
        installResourceDownloadListenerV78();
        testId="cp76-"+UUID.randomUUID();startedMs=System.currentTimeMillis();telemetrySeq=0;remoteTelemetryPosts=0;
        resourceScanDocumentEpoch=documentEpoch;resourceScanPageFinishedEpoch=pageFinishedEpoch;
        resourceSelectedId="-";resourceSelectedKind="-";resourceSelectedHref="";resourceSelectedLocatorCount=0;
        JSONObject start=baseState();put(start,"resolver_version",4);put(start,"read_only",true);put(start,"document_epoch",documentEpoch);put(start,"page_finished_epoch",pageFinishedEpoch);
        emit("RESOURCE_RESOLVER","RESOURCE_RESOLVER_V4_STARTED_READ_ONLY",start);
        eval(resourceResolverV4Js(),o->{
            JSONObject st=baseState();
            String[] ints={"global_resource_candidate_count","global_visible_links","owned_direct_count","owned_correlated_count","bounded_correlated_count","final_bounded_correlated_count","unowned_candidate_count","ambiguous_owner_count","semantic_resource_count","dom_locator_count","alias_resource_count","alias_locator_max","same_origin_resource_count","cross_origin_resource_count","same_origin_wrapped_actionable_count","direct_external_actionable_count","blob_resource_count","data_resource_count","citation_like_count","file_action_candidate_count","download_link_candidate_count","excluded_global_control_count","strong_nonhref_action_count","composer_boundary_count","actionable_unique_count","preferred_locator_count"};
            for(String k:ints)put(st,k,o.optInt(k,0));
            put(st,"resolver_version",4);put(st,"read_only",true);put(st,"resource_semantic_hash",o.optString("resource_semantic_hash","-"));
            put(st,"preferred_action_kind",o.optString("preferred_action_kind","NONE"));put(st,"preferred_semantic_class",o.optString("preferred_semantic_class","NONE"));put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);put(st,"cookies_tokens_accessed",false);
            if(!o.optBoolean("success",false)){
                emit("RESOURCE_RESOLVER","RESOURCE_RESOLVER_V4_FAILED_READ_ONLY",st);status.setText("RESOURCE TEST failed read-only. No action dispatched.");return;
            }
            if(resourceScanDocumentEpoch!=documentEpoch||resourceScanPageFinishedEpoch!=pageFinishedEpoch||pageFinishedEpoch!=documentEpoch){
                emit("RESOURCE_RESOLVER","RESOURCE_RESOLVER_V4_STALE_EPOCH_REJECTED",st);status.setText("RESOURCE TEST stale after page change. Run it again on the current chat.");return;
            }
            resourceSelectedId=o.optString("preferred_action_id","-");resourceSelectedKind=o.optString("preferred_action_kind","NONE");resourceSelectedHref=o.optString("preferred_action_href","");resourceSelectedLocatorCount=o.optInt("preferred_locator_count",0);
            put(st,"has_actionable_preferred",!"-".equals(resourceSelectedId)&&resourceSelectedLocatorCount==1);
            emit("RESOURCE_RESOLVER","PASS_RESOURCE_RESOLVER_V4_CENSUS_COMPLETE",st);
            if(o.optInt("global_resource_candidate_count",0)>0&&o.optInt("semantic_resource_count",0)==0)emit("RESOURCE_RESOLVER","RESOURCE_CANDIDATES_PRESENT_BUT_NO_OWNED_SEMANTIC_RESOURCE",st);
            status.setText("Resource resolver v4 complete. candidates="+o.optInt("global_resource_candidate_count",0)+" resources="+o.optInt("semantic_resource_count",0)+" finalBounded="+o.optInt("final_bounded_correlated_count",0)+" action="+resourceSelectedKind+". Press TEST ACTION.");
        });
    }

''')

# Every TEST ACTION press now has an admission event and a terminal or explicit
# waiting-for-receipt result. No early silent return remains.
method('runResourceActionV78',r'''    private void runResourceActionV78(){
        JSONObject attempt=baseState();put(attempt,"selected_present",!"-".equals(resourceSelectedId));put(attempt,"selected_locator_count",resourceSelectedLocatorCount);put(attempt,"selected_kind",resourceSelectedKind);put(attempt,"raw_url_remote",false);
        emit("RESOURCE_ACTION","RESOURCE_ACTION_ATTEMPTED",attempt);
        if(learning||plannerRunning||toolsTestRunning||resourceDownloadPending||resourceNavigationPending){emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_BUSY",attempt);status.setText("TEST ACTION blocked while another operation is active.");return;}
        if("-".equals(resourceSelectedId)||resourceSelectedLocatorCount!=1){emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_NO_ACTIONABLE_PREFERRED",attempt);status.setText("TEST ACTION blocked: RESOURCE TEST did not prove one actionable resource.");return;}
        if(resourceScanDocumentEpoch!=documentEpoch||resourceScanPageFinishedEpoch!=pageFinishedEpoch||pageFinishedEpoch!=documentEpoch){
            JSONObject st=baseState();put(st,"scan_document_epoch",resourceScanDocumentEpoch);put(st,"current_document_epoch",documentEpoch);emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_STALE_EPOCH",st);status.setText("TEST ACTION blocked: page changed after RESOURCE TEST.");return;
        }
        final String expectedId=resourceSelectedId;final String expectedKind=resourceSelectedKind;
        eval(resourceResolverV4Js(),o->{
            String id=o.optString("preferred_action_id","-");String kind=o.optString("preferred_action_kind","NONE");String href=o.optString("preferred_action_href","");int locators=o.optInt("preferred_locator_count",0);
            boolean epochFresh=resourceScanDocumentEpoch==documentEpoch&&resourceScanPageFinishedEpoch==pageFinishedEpoch&&pageFinishedEpoch==documentEpoch;
            boolean fresh=o.optBoolean("success",false)&&epochFresh&&locators==1&&expectedId.equals(id)&&expectedKind.equals(kind);
            JSONObject pre=baseState();put(pre,"resource_action_id",expectedId);put(pre,"resource_action_kind",kind);put(pre,"locator_count",locators);put(pre,"fresh",fresh);put(pre,"semantic_recertified",fresh);put(pre,"resolver_version",4);put(pre,"final_bounded_correlated_count",o.optInt("final_bounded_correlated_count",0));put(pre,"raw_url_remote",false);
            if(!fresh){emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_SEMANTIC_RECERTIFICATION_FAILED",pre);status.setText("TEST ACTION blocked: resource provenance/semantics no longer recertify exactly.");return;}
            boolean committed=prefs.edit().putString("resource_v78_claim_status","CLAIMED").putString("resource_v78_claim_id",expectedId).commit();
            put(pre,"claim_committed",committed);emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_RESOURCE_ACTION":"RESOURCE_ACTION_CLAIM_COMMIT_FAILED",pre);
            if(!committed){status.setText("TEST ACTION blocked: durable claim failed.");return;}
            resourceActionPendingId=expectedId;
            if("CROSS_ORIGIN_LINK".equals(kind)&&href.matches("^https?://.+")){
                try{
                    android.content.Intent intent=new android.content.Intent(android.content.Intent.ACTION_VIEW,android.net.Uri.parse(href));startActivity(intent);pageUiDispatches++;pageUiWrites++;
                    prefs.edit().putString("resource_v78_claim_status","OPEN_INTENT_DISPATCHED").commit();emit("RESOURCE_ACTION","PASS_RESOURCE_EXTERNAL_OPEN_INTENT_DISPATCHED",pre);status.setText("Resource action PASS: direct external link open dispatched.");resourceActionPendingId="-";
                }catch(Exception e){prefs.edit().putString("resource_v78_claim_status","OPEN_INTENT_FAILED_NO_REPLAY").commit();emit("RESOURCE_ACTION","RESOURCE_EXTERNAL_OPEN_INTENT_FAILED_NO_REPLAY",pre);status.setText("External open failed; no replay.");resourceActionPendingId="-";}
                return;
            }
            if("SAME_ORIGIN_WRAPPED_LINK".equals(kind)&&href.matches("^https?://.+")){
                resourceNavigationPending=true;resourceWrappedInitialHref=href;resourceWrappedSawSameOriginNavigation=false;
                eval(resourceActionClickV78Js(expectedId),a->{
                    boolean clicked=a.optBoolean("success",false)&&a.optBoolean("clicked",false)&&a.optInt("locator_count",0)==1&&a.optBoolean("semantic_guard",false);
                    JSONObject st=baseState();put(st,"resource_action_id",expectedId);put(st,"resource_action_kind",kind);put(st,"locator_count",a.optInt("locator_count",0));put(st,"semantic_guard",a.optBoolean("semantic_guard",false));put(st,"raw_url_remote",false);
                    if(clicked){pageUiDispatches++;pageUiWrites++;emit("RESOURCE_ACTION","PASS_RESOURCE_WRAPPED_EXACT_SINGLE_CLICK_DISPATCHED_WAITING_NAVIGATION_RECEIPT",st);status.setText("Wrapped resource clicked once. Waiting for navigation/download receipt; do not press TEST ACTION again.");}
                    else{resourceNavigationPending=false;resourceWrappedInitialHref="";prefs.edit().putString("resource_v78_claim_status","WRAPPED_CLICK_UNCERTAIN_NO_REPLAY").commit();emit("RESOURCE_ACTION","RESOURCE_CLICK_UNCERTAIN_NO_REPLAY",st);status.setText("Wrapped resource click uncertain; no replay.");resourceActionPendingId="-";}
                });
                return;
            }
            if("DOWNLOAD_LINK".equals(kind)||"FILE_ACTION".equals(kind)||"BLOB_RESOURCE".equals(kind)||"DATA_RESOURCE".equals(kind)){
                resourceDownloadPending=true;
                eval(resourceActionClickV78Js(expectedId),a->{
                    boolean clicked=a.optBoolean("success",false)&&a.optBoolean("clicked",false)&&a.optInt("locator_count",0)==1&&a.optBoolean("semantic_guard",false);
                    JSONObject st=baseState();put(st,"resource_action_id",expectedId);put(st,"resource_action_kind",kind);put(st,"locator_count",a.optInt("locator_count",0));put(st,"semantic_guard",a.optBoolean("semantic_guard",false));put(st,"raw_url_remote",false);
                    if(clicked){pageUiDispatches++;pageUiWrites++;emit("RESOURCE_ACTION","PASS_RESOURCE_EXACT_SINGLE_CLICK_DISPATCHED_WAITING_RECEIPT",st);status.setText("Resource click dispatched once. Waiting for explicit receipt; do not press TEST ACTION again.");}
                    else{resourceDownloadPending=false;prefs.edit().putString("resource_v78_claim_status","CLICK_UNCERTAIN_NO_REPLAY").commit();emit("RESOURCE_ACTION","RESOURCE_CLICK_UNCERTAIN_NO_REPLAY",st);status.setText("Resource click uncertain; no replay.");resourceActionPendingId="-";}
                });
                return;
            }
            prefs.edit().putString("resource_v78_claim_status","BLOCKED_UNSUPPORTED_REALIZATION").commit();emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_UNSUPPORTED_REALIZATION",pre);status.setText("TEST ACTION blocked: unsupported resource realization.");resourceActionPendingId="-";
        });
    }

''')

# Replace resolver/click/misdispatch block with v4. Semantic resource class is
# separate from URL realization. Final-tail ownership is bounded by an exact
# composer root, never the unbounded page tail.
start=s.index('    private String resourceResolverV4Js(){\n')
end=s.index('    private void runToolsTest(){\n',start)
resource_block=r'''    private String resourceResolverV4Js(){
        return "(function(){try{"+
            "const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const H=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return ('00000000'+(h>>>0).toString(16)).slice(-8);};"+
            "const V=e=>{if(!e||!e.isConnected)return false;const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true'&&r.width>0&&r.height>0;};"+
            "const D=e=>N([e.tagName||'',e.getAttribute('role')||'',e.getAttribute('aria-label')||'',e.getAttribute('title')||'',e.getAttribute('data-testid')||'',e.getAttribute('name')||'',(e.innerText||e.textContent||'').slice(0,180)].join(' '));"+
            "const A=e=>N([e.tagName||'',e.getAttribute('role')||'',e.getAttribute('aria-label')||'',e.getAttribute('title')||'',e.getAttribute('data-testid')||'',e.getAttribute('name')||'',e.getAttribute('target')||'',e.getAttribute('rel')||''].join(' '));"+
            "const before=(a,b)=>!!(a&&b&&(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING));"+
            "const canon=h=>{try{if(!h)return '';if(h.startsWith('blob:'))return 'blob:';if(h.startsWith('data:'))return 'data:';const u=new URL(h,location.href);return u.protocol+'//'+u.host+u.pathname+'|q:'+H(u.search||'')+'|f:'+H(u.hash||'');}catch(_){return 'other:'+H(String(h||''));}};"+
            "const turnNodes=[];const seen=new Set();const addTurn=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);turnNodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(addTurn);const turns=turnNodes.map((e,i)=>{const r=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');return{el:e,role:r?String(r.getAttribute('data-message-author-role')||'-'):'-',ref:String(e.getAttribute('data-turn-id')||e.getAttribute('data-testid')||('T'+i)),index:i};});"+
            "const assistants=turns.filter(t=>t.role==='assistant');const lastAssistant=assistants.length?assistants[assistants.length-1]:null;"+
            "const directAssistant=e=>{const h=turns.filter(t=>t.role==='assistant'&&t.el.contains(e));return h.length===1?h[0]:null;};"+
            "const isComposer=e=>!!(e.closest&&(e.closest('form')||e.closest(`[data-testid*='composer']`)));"+
            "const excludedRoot=e=>!!(e.closest&&(e.closest('nav,header,aside,[role=navigation]')||isComposer(e)));"+
            "const resourceWrapper=e=>e.closest&&e.closest(`[data-testid*='citation'],[data-testid*='source'],[data-testid*='resource'],[data-testid*='file'],[data-testid*='download'],[data-testid*='attachment']`);"+
            "const isComposerRoot=e=>{if(!V(e))return false;const dt=N(e.getAttribute('data-testid')||'');if(dt.includes('composer'))return true;if((e.tagName||'').toLowerCase()==='form'){return !!Array.from(e.querySelectorAll('textarea,[contenteditable=true],button,[role=button]')).find(x=>V(x)&&(/send|composer|prompt|message/.test(A(x))||x.matches('textarea,[contenteditable=true]')));}return false;};"+
            "const roots=Array.from(document.querySelectorAll(`form,[data-testid*='composer']`)).filter(isComposerRoot);let composerBoundary=null;if(lastAssistant){for(const r of roots){if(before(lastAssistant.el,r)&&(!composerBoundary||before(r,composerBoundary)))composerBoundary=r;}}"+
            "const strongNonHref=e=>{if(isComposer(e)||excludedRoot(e))return false;const a=A(e),w=resourceWrapper(e);return !!w||/download|save|file|attachment|citation|source|reference|resource/.test(a);};"+
            "const strongWrapped=e=>{if(excludedRoot(e))return false;let h=e.getAttribute('href')||'';try{if(!h&&typeof e.href==='string')h=e.href;}catch(_){}if(!h)return false;try{const u=new URL(h,location.href);if(u.origin!==location.origin)return false;}catch(_){return false;}const a=A(e),w=resourceWrapper(e),target=N(e.getAttribute('target')||''),rel=N(e.getAttribute('rel')||'');return !!w||target==='_blank'||/noopener|noreferrer|external/.test(rel)||/citation|source|reference|resource|redirect|outbound|external/.test(a);};"+
            "const owner=e=>{const direct=turns.filter(t=>t.el.contains(e));if(direct.length===1)return{mode:'DIRECT',turn:direct[0]};if(direct.length>1)return{mode:'AMBIGUOUS',turn:null};const w=resourceWrapper(e);if(w){const hits=turns.filter(t=>w.contains(t.el));const ah=hits.filter(t=>t.role==='assistant');if(hits.length===1&&ah.length===1)return{mode:'CORRELATED_WRAPPER',turn:ah[0]};if(hits.length>1)return{mode:'AMBIGUOUS',turn:null};}let prev=null,next=null;for(const t of turns){if(before(t.el,e))prev=t;else if(before(e,t.el)){next=t;break;}}if(prev&&next&&prev.role==='assistant'&&before(prev.el,e)&&before(e,next.el))return{mode:'CORRELATED_BOUNDED',turn:prev};if(lastAssistant&&prev===lastAssistant&&!next&&composerBoundary&&before(lastAssistant.el,e)&&before(e,composerBoundary)&&!excludedRoot(e))return{mode:'CORRELATED_FINAL_BOUNDED',turn:lastAssistant};return{mode:'UNOWNED',turn:null};};"+
            "const nodes=[];const add=e=>{if(V(e)&&nodes.indexOf(e)<0)nodes.push(e);};document.querySelectorAll('a[href],[role=link],[download]').forEach(add);"+
            "let excludedGlobal=0,strongNonHrefCount=0;const resourceWords=/download|save|file|attachment|citation|source|reference|resource/;Array.from(document.querySelectorAll('button,[role=button]')).filter(V).forEach(e=>{if(!resourceWords.test(D(e)))return;const da=directAssistant(e);if(!da||isComposer(e)){excludedGlobal++;return;}if(strongNonHref(e)){add(e);strongNonHrefCount++;}});"+
            "let seq=0;const locator=e=>{let x=e.getAttribute('data-cp-resource-locator-v78');if(!x){x='R'+(++seq)+'_'+H(A(e));e.setAttribute('data-cp-resource-locator-v78',x);}return x;};"+
            "const items={};let direct=0,corr=0,bounded=0,finalBounded=0,unowned=0,amb=0,same=0,cross=0,sameWrapped=0,directExternal=0,blob=0,data=0,citation=0,fileAction=0,downloadLink=0;"+
            "for(const e of nodes){const ow=owner(e);if(ow.mode==='DIRECT')direct++;else if(ow.mode==='CORRELATED_WRAPPER'||ow.mode==='CORRELATED_BOUNDED'||ow.mode==='CORRELATED_FINAL_BOUNDED'){corr++;if(ow.mode==='CORRELATED_BOUNDED')bounded++;if(ow.mode==='CORRELATED_FINAL_BOUNDED')finalBounded++;}else if(ow.mode==='UNOWNED')unowned++;else amb++;const d=D(e),a=A(e);let href=e.getAttribute('href')||'';try{if(!href&&typeof e.href==='string')href=e.href;}catch(_){}let kind='UNCLASSIFIED_CONTROL',semantic='NONE',evidence='NONE';if(href){if(href.startsWith('blob:')){kind='BLOB_RESOURCE';semantic='URL_RESOURCE';blob++;evidence='URL_BACKED';}else if(href.startsWith('data:')){kind='DATA_RESOURCE';semantic='URL_RESOURCE';data++;evidence='URL_BACKED';}else{try{const u=new URL(href,location.href);if(u.origin===location.origin){same++;if(strongWrapped(e)){kind='SAME_ORIGIN_WRAPPED_LINK';semantic='URL_RESOURCE';evidence='STRONG_WRAPPED_URL';sameWrapped++;}else{kind='SAME_ORIGIN_LINK';semantic='NONRESOURCE_NAV';evidence='URL_BACKED_SAME_ORIGIN';}}else{kind='CROSS_ORIGIN_LINK';semantic='URL_RESOURCE';evidence='DIRECT_EXTERNAL_URL';cross++;directExternal++;}}catch(_){kind='UNCLASSIFIED_LINK';}}if(e.hasAttribute('download')||/download|save/.test(a)){kind='DOWNLOAD_LINK';semantic='DOWNLOAD_RESOURCE';downloadLink++;evidence='URL_BACKED_DOWNLOAD';}}else if(/citation|source|reference/.test(a)||N(e.getAttribute('data-testid')||'').includes('citation')){kind='CITATION_CONTROL';semantic='CITATION_RESOURCE';citation++;evidence='DIRECT_STRUCTURAL';}else if(directAssistant(e)&&strongNonHref(e)){kind='FILE_ACTION';semantic='FILE_RESOURCE';fileAction++;evidence='STRONG_DIRECT_NONHREF';}if(!(ow.mode==='DIRECT'||ow.mode==='CORRELATED_WRAPPER'||ow.mode==='CORRELATED_BOUNDED'||ow.mode==='CORRELATED_FINAL_BOUNDED')||!ow.turn)continue;if(semantic==='NONE'||semantic==='NONRESOURCE_NAV'||kind==='UNCLASSIFIED_CONTROL'||kind==='UNCLASSIFIED_LINK')continue;if(kind==='FILE_ACTION'&&!(ow.mode==='DIRECT'&&ow.turn.role==='assistant'))continue;if(kind==='SAME_ORIGIN_WRAPPED_LINK'&&evidence!=='STRONG_WRAPPED_URL')continue;const w=resourceWrapper(e),wt=w?N(w.getAttribute('data-testid')||''):'';const target=href?canon(href):('struct:'+H(A(e)+'|'+wt));const key=H(H(ow.turn.ref)+'|'+semantic+'|'+target);let it=items[key];if(!it)it=items[key]={id:key,kind:kind,semanticClass:semantic,href:href,ownerMode:ow.mode,ownerRef:ow.turn.ref,role:ow.turn.role,turnIndex:ow.turn.index,target:target,evidence:evidence,locators:[],order:nodes.indexOf(e)};const loc=locator(e);if(it.locators.indexOf(loc)<0)it.locators.push(loc);items[key]=it;}"+
            "const vals=Object.values(items);let aliasCount=0,aliasMax=0,locatorCount=0;for(const x of vals){locatorCount+=x.locators.length;if(x.locators.length>1)aliasCount++;if(x.locators.length>aliasMax)aliasMax=x.locators.length;}"+
            "const actionable=vals.filter(x=>x.role==='assistant'&&x.locators.length===1&&['DOWNLOAD_LINK','CROSS_ORIGIN_LINK','SAME_ORIGIN_WRAPPED_LINK','BLOB_RESOURCE','DATA_RESOURCE','FILE_ACTION'].includes(x.kind)&&(x.kind!=='FILE_ACTION'||(x.ownerMode==='DIRECT'&&x.evidence==='STRONG_DIRECT_NONHREF'))&&(x.kind!=='SAME_ORIGIN_WRAPPED_LINK'||x.evidence==='STRONG_WRAPPED_URL'));const pri={DOWNLOAD_LINK:65,CROSS_ORIGIN_LINK:60,SAME_ORIGIN_WRAPPED_LINK:58,BLOB_RESOURCE:50,DATA_RESOURCE:49,FILE_ACTION:40};actionable.sort((a,b)=>(pri[b.kind]||0)-(pri[a.kind]||0)||a.order-b.order);const pref=actionable.length?actionable[0]:null;"+
            "window.__cpResourceResolverV78={routePath:location.pathname,items:items,preferredId:pref?pref.id:'-'};const sig=vals.map(x=>x.id+':'+x.locators.length+':'+x.ownerMode+':'+x.semanticClass).sort().join('|');"+
            "return JSON.stringify({success:true,global_resource_candidate_count:nodes.length,global_visible_links:Array.from(document.querySelectorAll('a[href]')).filter(V).length,owned_direct_count:direct,owned_correlated_count:corr,bounded_correlated_count:bounded,final_bounded_correlated_count:finalBounded,unowned_candidate_count:unowned,ambiguous_owner_count:amb,semantic_resource_count:vals.length,dom_locator_count:locatorCount,alias_resource_count:aliasCount,alias_locator_max:aliasMax,same_origin_resource_count:same,cross_origin_resource_count:cross,same_origin_wrapped_actionable_count:sameWrapped,direct_external_actionable_count:directExternal,blob_resource_count:blob,data_resource_count:data,citation_like_count:citation,file_action_candidate_count:fileAction,download_link_candidate_count:downloadLink,excluded_global_control_count:excludedGlobal,strong_nonhref_action_count:strongNonHrefCount,composer_boundary_count:composerBoundary?1:0,actionable_unique_count:actionable.length,preferred_action_id:pref?pref.id:'-',preferred_action_kind:pref?pref.kind:'NONE',preferred_semantic_class:pref?pref.semanticClass:'NONE',preferred_action_href:pref?pref.href:'',preferred_locator_count:pref?pref.locators.length:0,resource_semantic_hash:H(sig)});"+
        "}catch(e){return JSON.stringify({success:false,error_class:'RESOURCE_RESOLVER_V4_EXCEPTION'});}})()";
    }

    private String jsV78(String value){
        if(value==null)return "";
        return value.replace("\\","\\\\").replace("'","\\'").replace("\r","\\r").replace("\n","\\n");
    }

    private String resourceActionClickV78Js(String id){
        return "(function(){try{const R=window.__cpResourceResolverV78;if(!R||R.routePath!==location.pathname)return JSON.stringify({success:false,clicked:false,locator_count:0,semantic_guard:false});const x=R.items['"+jsV78(id)+"'];if(!x||x.role!=='assistant')return JSON.stringify({success:false,clicked:false,locator_count:0,semantic_guard:false});if(x.kind==='FILE_ACTION'&&(x.ownerMode!=='DIRECT'||x.evidence!=='STRONG_DIRECT_NONHREF'))return JSON.stringify({success:false,clicked:false,locator_count:0,semantic_guard:false});if(x.kind==='SAME_ORIGIN_WRAPPED_LINK'&&x.evidence!=='STRONG_WRAPPED_URL')return JSON.stringify({success:false,clicked:false,locator_count:0,semantic_guard:false});const vis=Array.from(document.querySelectorAll('[data-cp-resource-locator-v78]')).filter(e=>x.locators.indexOf(e.getAttribute('data-cp-resource-locator-v78'))>=0).filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return e.isConnected&&s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true'&&r.width>0&&r.height>0;});if(vis.length!==1)return JSON.stringify({success:false,clicked:false,locator_count:vis.length,semantic_guard:false});const e=vis[0];if(e.disabled||e.getAttribute('aria-disabled')==='true')return JSON.stringify({success:false,clicked:false,locator_count:1,semantic_guard:false});e.click();return JSON.stringify({success:true,clicked:true,locator_count:1,semantic_guard:true});}catch(e){return JSON.stringify({success:false,clicked:false,locator_count:0,semantic_guard:false});}})()";
    }

    private String originOfV78(String u){
        try{android.net.Uri x=android.net.Uri.parse(u==null?"":u);String scheme=x.getScheme(),host=x.getHost();if(scheme==null||host==null)return "";scheme=scheme.toLowerCase(java.util.Locale.ROOT);host=host.toLowerCase(java.util.Locale.ROOT);if(!"http".equals(scheme)&&!"https".equals(scheme))return "";int port=x.getPort();return scheme+"://"+host+(port>=0?":"+port:"");}catch(Exception e){return "";}
    }

    private boolean handleResourceNavigationV78(String u,boolean mainFrame){
        if(!resourceNavigationPending||!mainFrame||u==null)return false;
        String expected=originOfV78(resourceWrappedInitialHref),observed=originOfV78(u);
        if(observed.isEmpty()){
            resourceNavigationPending=false;resourceWrappedInitialHref="";prefs.edit().putString("resource_v78_claim_status","WRAPPED_UNSUPPORTED_SCHEME_NO_REPLAY").commit();JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"raw_url_remote",false);emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_UNSUPPORTED_RESOLVED_SCHEME",st);status.setText("Wrapped resource resolved to an unsupported scheme; no replay.");resourceActionPendingId="-";return true;
        }
        if(!expected.isEmpty()&&expected.equals(observed)){
            resourceWrappedSawSameOriginNavigation=true;JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"same_origin_navigation_observed",true);put(st,"raw_url_remote",false);emit("RESOURCE_ACTION","RESOURCE_WRAPPED_SAME_ORIGIN_NAVIGATION_OBSERVED",st);return false;
        }
        resourceNavigationPending=false;resourceDownloadPending=false;resourceWrappedInitialHref="";
        JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"resolved_external",true);put(st,"raw_url_remote",false);
        try{android.content.Intent intent=new android.content.Intent(android.content.Intent.ACTION_VIEW,android.net.Uri.parse(u));startActivity(intent);pageUiDispatches++;pageUiWrites++;prefs.edit().putString("resource_v78_claim_status","WRAPPED_EXTERNAL_OPEN_INTENT_DISPATCHED").commit();emit("RESOURCE_ACTION","PASS_RESOURCE_WRAPPED_EXTERNAL_RESOLVED_OPEN_INTENT_DISPATCHED",st);status.setText("Resource action PASS: wrapped link resolved externally and browser open dispatched.");}
        catch(Exception e){prefs.edit().putString("resource_v78_claim_status","WRAPPED_EXTERNAL_OPEN_INTENT_FAILED_NO_REPLAY").commit();emit("RESOURCE_ACTION","RESOURCE_WRAPPED_EXTERNAL_OPEN_INTENT_FAILED_NO_REPLAY",st);status.setText("Wrapped external open failed; no replay.");}
        resourceActionPendingId="-";return true;
    }

    private void finishResourceNavigationV78(String u){
        if(!resourceNavigationPending)return;
        if(handleResourceNavigationV78(u,true))return;
        resourceNavigationPending=false;resourceWrappedInitialHref="";prefs.edit().putString("resource_v78_claim_status","WRAPPED_SAME_ORIGIN_TERMINAL_NO_REPLAY").commit();JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"same_origin_navigation_observed",resourceWrappedSawSameOriginNavigation);put(st,"uncertain_effect",true);put(st,"raw_url_remote",false);emit("RESOURCE_ACTION","RESOURCE_ACTION_UNCERTAIN_WRAPPED_SAME_ORIGIN_TERMINAL_NO_REPLAY",st);status.setText("Wrapped resource stayed same-origin through page-finished; no external receipt, no replay.");resourceActionPendingId="-";
    }

    private void driveResourcePendingOnEventV78(String reason){
        if((!resourceDownloadPending&&!resourceNavigationPending)||"-".equals(resourceActionPendingId))return;
        eval(toolsMenuCensusV78Js(),o->{
            if((!resourceDownloadPending&&!resourceNavigationPending)||"-".equals(resourceActionPendingId))return;
            if(!o.optBoolean("success",false)||!o.optBoolean("menu_materialized",false))return;
            resourceDownloadPending=false;resourceNavigationPending=false;resourceWrappedInitialHref="";
            prefs.edit().putString("resource_v78_claim_status","MISDISPATCHED_NONRESOURCE_UI_NO_REPLAY").commit();
            JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"menu_surface_count",o.optInt("menu_surface_count",0));put(st,"option_count",o.optInt("option_count",0));put(st,"event_reason_hash",hashNorm(reason));put(st,"uncertain_effect",true);put(st,"raw_text_remote",false);
            emit("RESOURCE_ACTION","RESOURCE_ACTION_MISDISPATCHED_NONRESOURCE_UI",st);status.setText("Resource action FAILED: incompatible Add/Tools UI materialized. No replay authorized.");resourceActionPendingId="-";
        });
    }

'''
s=s[:start]+resource_block+s[end:]

# Event bridge and Tools busy gate now understand wrapped-navigation pending state.
s=s.replace('if(resourceDownloadPending)driveResourcePendingOnEventV78(reason);','if(resourceDownloadPending||resourceNavigationPending)driveResourcePendingOnEventV78(reason);')
s=s.replace('if(learning||plannerRunning||toolsTestRunning||resourceDownloadPending){status.setText("TOOLS TEST blocked while another operation is active.");return;}','if(learning||plannerRunning||toolsTestRunning||resourceDownloadPending||resourceNavigationPending){status.setText("TOOLS TEST blocked while another operation is active.");return;}')

# Write renamed activity and telemetry config.
ACT.write_text(s);OLD.unlink()
old_cfg=PKG/"TelemetryConfigV77.java";new_cfg=PKG/"TelemetryConfigV78.java"
cfg=old_cfg.read_text().replace("TelemetryConfigV77","TelemetryConfigV78")
new_cfg.write_text(cfg);old_cfg.unlink()

# Version/package/update continuity.
g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+78\b","versionCode 79",gs);gs=gs.replace("0.75-stable-diag-resource-provenance-hardened","0.76-stable-diag-resource-final-bounded-wrapped");g.write_text(gs)
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorResourceToolsV77Activity","OrchestratorResourceToolsV78Activity");mf.write_text(ms)

# Consolidated regression/safety gates.
out=ACT.read_text();resolver=out[out.index('private String resourceResolverV4Js'):out.index('private void runToolsTest')]
for required in [
    'RESOURCE_RESOLVER_V4','CORRELATED_FINAL_BOUNDED','composerBoundary','SAME_ORIGIN_WRAPPED_LINK','STRONG_WRAPPED_URL',
    'RESOURCE_ACTION_ATTEMPTED','RESOURCE_ACTION_BLOCKED_NO_ACTIONABLE_PREFERRED','PASS_RESOURCE_WRAPPED_EXACT_SINGLE_CLICK_DISPATCHED_WAITING_NAVIGATION_RECEIPT',
    'PASS_RESOURCE_WRAPPED_EXTERNAL_RESOLVED_OPEN_INTENT_DISPATCHED','RESOURCE_ACTION_UNCERTAIN_WRAPPED_SAME_ORIGIN_TERMINAL_NO_REPLAY',
    'RESOURCE_ACTION_BLOCKED_SEMANTIC_RECERTIFICATION_FAILED','RESOURCE_ACTION_MISDISPATCHED_NONRESOURCE_UI','CLAIMED_BEFORE_RESOURCE_ACTION',
    'data-cp-resource-locator-v78','TelemetryConfigV78','private String jsV78(String value)','shouldOverrideUrlLoading',
    "prev&&next&&prev.role==='assistant'","prev===lastAssistant&&!next&&composerBoundary","if(!da||isComposer(e)){excludedGlobal++;return;}",
    'SAME_ORIGIN_WRAPPED_LINK:58','CROSS_ORIGIN_LINK:60','FILE_ACTION:40'
]: assert required in out,required
assert "(!next||" not in resolver
assert "x.kind==='FILE_ACTION'&&(x.ownerMode!=='DIRECT'||x.evidence!=='STRONG_DIRECT_NONHREF')" in resolver
assert "x.kind==='SAME_ORIGIN_WRAPPED_LINK'&&x.evidence!=='STRONG_WRAPPED_URL'" in resolver
assert out.count('.click();')==5,out.count('.click();')
for forbidden in ['Thread.sleep','setTimeout(','setInterval(','ScheduledExecutorService','TimerTask','elementFromPoint','document.evaluate','dispatchTouchEvent(','performClick(','ACTION_SET_PROGRESS','CookieManager','getCookie(','addJavascriptInterface','XPathResult']:
    assert forbidden not in out,forbidden
assert "versionCode 79" in g.read_text()
assert "versionName '0.76-stable-diag-resource-final-bounded-wrapped'" in g.read_text()
assert "OrchestratorResourceToolsV78Activity" in mf.read_text()
print("PASS v0.76: final-assistant bounded corridor + wrapped navigation receipts + complete action admission telemetry")
