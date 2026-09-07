#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.74: one consolidated build after the v0.73 resource-discovery defect audit.
# Preserve the proven v0.72 Planner and v0.73 breadth paths while adding:
# - Resource Resolver v2: global candidate discovery + semantic ownership + alias separation
# - one guarded TEST ACTION path with durable claim and explicit receipt semantics
# - one controlled reversible Add/Tools hidden-menu census driven by DOM events
runpy.run_path("ci/generate_chatgpt_webview_v75_unified_breadth_frontier.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorUnifiedBreadthV75Activity.java"
ACT=PKG/"OrchestratorResourceToolsV76Activity.java"
s=OLD.read_text()

def once(old,new,label):
    global s
    n=s.count(old)
    assert n==1,(label,n)
    s=s.replace(old,new,1)

# Identity / update continuity.
s=s.replace("OrchestratorUnifiedBreadthV75Activity","OrchestratorResourceToolsV76Activity")
s=s.replace('SCHEMA="cp-v75-unified-breadth-frontier-v1"','SCHEMA="cp-v76-resource-tools-consolidated-v1"')
s=s.replace('SCENARIO="unified-current-ui-resource-tool-breadth-frontier"','SCENARIO="resource-resolver-tools-consolidated"')
s=s.replace('getSharedPreferences("cp_v75_unified_breadth",MODE_PRIVATE)','getSharedPreferences("cp_v76_resource_tools",MODE_PRIVATE)')
s=s.replace('testId="cp73-"+UUID.randomUUID();','testId="cp74-"+UUID.randomUUID();')
s=s.replace('v0.73 Unified Breadth + proven Planner ready.','v0.74 Resource Resolver + Tools consolidated ready.')

# State for the new consolidated tests. Raw href is local-only and never placed in telemetry.
field_anchor='    private long activeReadSerial=0L;\n'
assert field_anchor in s
fields='''    private long resourceScanDocumentEpoch=-1L;
    private long resourceScanPageFinishedEpoch=-1L;
    private String resourceSelectedId="-";
    private String resourceSelectedKind="-";
    private String resourceSelectedHref="";
    private int resourceSelectedLocatorCount=0;
    private boolean resourceDownloadPending=false;
    private String resourceActionPendingId="-";
    private boolean toolsTestRunning=false;
    private boolean toolsEvalInFlight=false;
    private String toolsTestPhase="IDLE";
'''
s=s.replace(field_anchor,field_anchor+fields,1)

# Add exactly the three user-facing controls approved for the next test cycle.
ui_anchor='''        root.addView(row4,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(42)));

        draftInput=new EditText(this);'''
ui_insert='''        root.addView(row4,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(42)));

        LinearLayout row5=new LinearLayout(this); row5.setOrientation(LinearLayout.HORIZONTAL);
        Button resourceTest=new Button(this); resourceTest.setText("RESOURCE TEST"); resourceTest.setOnClickListener(v->runResourceTest());
        Button testAction=new Button(this); testAction.setText("TEST ACTION"); testAction.setOnClickListener(v->runResourceActionV76());
        Button toolsTest=new Button(this); toolsTest.setText("TOOLS TEST"); toolsTest.setOnClickListener(v->runToolsTest());
        row5.addView(resourceTest,new LinearLayout.LayoutParams(0,dp(42),1f));
        row5.addView(testAction,new LinearLayout.LayoutParams(0,dp(42),1f));
        row5.addView(toolsTest,new LinearLayout.LayoutParams(0,dp(42),1f));
        root.addView(row5,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(42)));

        draftInput=new EditText(this);'''
once(ui_anchor,ui_insert,"v76 user controls")

# Any new document invalidates scan/action locators immediately. If a click was
# pending a download and navigation starts instead, classify UNCERTAIN and never replay.
once('super.onPageStarted(v,u,f); documentEpoch++; pageFinishedReady=false; pageFinishedEpoch=-1L; closeEventBridge();',
     'super.onPageStarted(v,u,f); documentEpoch++; pageFinishedReady=false; pageFinishedEpoch=-1L; invalidateResourceV76OnDocumentStart(); closeEventBridge();',
     'resource invalidation on document start')

# Reuse the existing event bridge. Tools menu transitions are advanced only from
# observed DOM/input/click/mutation events; no timer/poll delay becomes authority.
once('    private void onObservedState(JSONObject o,String reason){\n',
     '    private void onObservedState(JSONObject o,String reason){\n        if(toolsTestRunning)driveToolsTestOnEvent(reason);\n',
     'tools event hook')

methods=r'''    private void installResourceDownloadListenerV76(){
        if(web==null)return;
        web.setDownloadListener(new android.webkit.DownloadListener(){
            @Override public void onDownloadStart(String url,String userAgent,String contentDisposition,String mimetype,long contentLength){
                if(!resourceDownloadPending)return;
                resourceDownloadPending=false;
                prefs.edit().putString("resource_v76_claim_status","CONFIRMED_DOWNLOAD_CALLBACK").commit();
                JSONObject st=baseState();
                put(st,"resource_action_id",resourceActionPendingId);put(st,"download_content_length",contentLength);
                put(st,"download_mime_hash",hashNorm(mimetype==null?"":mimetype));put(st,"raw_url_remote",false);put(st,"raw_filename_remote",false);
                emit("RESOURCE_ACTION","PASS_RESOURCE_DOWNLOAD_CALLBACK_RECEIPT",st);
                status.setText("Resource action PASS by download callback. Run TOOLS TEST when ready.");
                resourceActionPendingId="-";
            }
        });
    }

    private void invalidateResourceV76OnDocumentStart(){
        if(resourceDownloadPending){
            resourceDownloadPending=false;
            prefs.edit().putString("resource_v76_claim_status","UNCERTAIN_ROUTE_CHANGED_NO_DOWNLOAD_RECEIPT").commit();
            JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"uncertain_effect",true);
            emit("RESOURCE_ACTION","RESOURCE_ACTION_UNCERTAIN_ROUTE_CHANGED_NO_DOWNLOAD_RECEIPT",st);
        }
        resourceScanDocumentEpoch=-1L;resourceScanPageFinishedEpoch=-1L;resourceSelectedId="-";resourceSelectedKind="-";resourceSelectedHref="";resourceSelectedLocatorCount=0;resourceActionPendingId="-";
    }

    private void runResourceTest(){
        if(learning||plannerRunning||toolsTestRunning||resourceDownloadPending){status.setText("RESOURCE TEST blocked while another test/action is active.");return;}
        installResourceDownloadListenerV76();
        testId="cp74-"+UUID.randomUUID();startedMs=System.currentTimeMillis();telemetrySeq=0;remoteTelemetryPosts=0;
        resourceScanDocumentEpoch=documentEpoch;resourceScanPageFinishedEpoch=pageFinishedEpoch;
        resourceSelectedId="-";resourceSelectedKind="-";resourceSelectedHref="";resourceSelectedLocatorCount=0;
        JSONObject start=baseState();put(start,"resolver_version",2);put(start,"read_only",true);put(start,"document_epoch",documentEpoch);put(start,"page_finished_epoch",pageFinishedEpoch);
        emit("RESOURCE_RESOLVER","RESOURCE_RESOLVER_V2_STARTED_READ_ONLY",start);
        eval(resourceResolverV2Js(),o->{
            JSONObject st=baseState();
            String[] ints={"global_resource_candidate_count","global_visible_links","owned_direct_count","owned_correlated_count","unowned_candidate_count","ambiguous_owner_count","semantic_resource_count","dom_locator_count","alias_resource_count","alias_locator_max","same_origin_resource_count","cross_origin_resource_count","blob_resource_count","data_resource_count","citation_like_count","file_action_candidate_count","download_link_candidate_count","actionable_unique_count","preferred_locator_count"};
            for(String k:ints)put(st,k,o.optInt(k,0));
            put(st,"resolver_version",2);put(st,"read_only",true);put(st,"resource_semantic_hash",o.optString("resource_semantic_hash","-"));
            put(st,"preferred_action_kind",o.optString("preferred_action_kind","NONE"));put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);put(st,"cookies_tokens_accessed",false);
            if(!o.optBoolean("success",false)){
                emit("RESOURCE_RESOLVER","RESOURCE_RESOLVER_V2_FAILED_READ_ONLY",st);status.setText("RESOURCE TEST failed read-only. No action dispatched.");return;
            }
            if(resourceScanDocumentEpoch!=documentEpoch||resourceScanPageFinishedEpoch!=pageFinishedEpoch||pageFinishedEpoch!=documentEpoch){
                emit("RESOURCE_RESOLVER","RESOURCE_RESOLVER_V2_STALE_EPOCH_REJECTED",st);status.setText("RESOURCE TEST stale after page change. Run it again on the current chat.");return;
            }
            resourceSelectedId=o.optString("preferred_action_id","-");resourceSelectedKind=o.optString("preferred_action_kind","NONE");resourceSelectedHref=o.optString("preferred_action_href","");resourceSelectedLocatorCount=o.optInt("preferred_locator_count",0);
            put(st,"has_actionable_preferred",!"-".equals(resourceSelectedId)&&resourceSelectedLocatorCount==1);
            emit("RESOURCE_RESOLVER","PASS_RESOURCE_RESOLVER_V2_CENSUS_COMPLETE",st);
            if(o.optInt("global_resource_candidate_count",0)>0&&o.optInt("semantic_resource_count",0)==0){
                emit("RESOURCE_RESOLVER","RESOURCE_CANDIDATES_PRESENT_BUT_NO_OWNED_SEMANTIC_RESOURCE",st);
            }
            status.setText("Resource resolver complete. candidates="+o.optInt("global_resource_candidate_count",0)+" resources="+o.optInt("semantic_resource_count",0)+" unowned="+o.optInt("unowned_candidate_count",0)+" action="+resourceSelectedKind+". Press TEST ACTION.");
        });
    }

    private void runResourceActionV76(){
        if(learning||plannerRunning||toolsTestRunning||resourceDownloadPending){status.setText("TEST ACTION blocked while another operation is active.");return;}
        if("-".equals(resourceSelectedId)||resourceSelectedLocatorCount!=1){status.setText("TEST ACTION blocked: RESOURCE TEST did not prove one actionable resource.");return;}
        if(resourceScanDocumentEpoch!=documentEpoch||resourceScanPageFinishedEpoch!=pageFinishedEpoch||pageFinishedEpoch!=documentEpoch){
            JSONObject st=baseState();put(st,"scan_document_epoch",resourceScanDocumentEpoch);put(st,"current_document_epoch",documentEpoch);emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_STALE_EPOCH",st);status.setText("TEST ACTION blocked: page changed after RESOURCE TEST.");return;
        }
        final String expectedId=resourceSelectedId;
        eval(resourceActionPrepareV76Js(expectedId),o->{
            boolean fresh=o.optBoolean("success",false)&&o.optBoolean("fresh",false)&&o.optInt("locator_count",0)==1&&expectedId.equals(o.optString("id","-"));
            String kind=o.optString("kind","NONE");String href=o.optString("href","");
            JSONObject pre=baseState();put(pre,"resource_action_id",expectedId);put(pre,"resource_action_kind",kind);put(pre,"locator_count",o.optInt("locator_count",0));put(pre,"fresh",fresh);put(pre,"raw_url_remote",false);
            if(!fresh){emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_NOT_FRESH_UNIQUE",pre);status.setText("TEST ACTION blocked: resource is no longer fresh and unique.");return;}
            boolean committed=prefs.edit().putString("resource_v76_claim_status","CLAIMED").putString("resource_v76_claim_id",expectedId).commit();
            put(pre,"claim_committed",committed);emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_RESOURCE_ACTION":"RESOURCE_ACTION_CLAIM_COMMIT_FAILED",pre);
            if(!committed){status.setText("TEST ACTION blocked: durable claim failed.");return;}
            resourceActionPendingId=expectedId;
            if("CROSS_ORIGIN_LINK".equals(kind)&&href.matches("^https?://.+")){
                try{
                    android.content.Intent intent=new android.content.Intent(android.content.Intent.ACTION_VIEW,android.net.Uri.parse(href));
                    startActivity(intent);pageUiDispatches++;pageUiWrites++;
                    prefs.edit().putString("resource_v76_claim_status","OPEN_INTENT_DISPATCHED").commit();
                    emit("RESOURCE_ACTION","PASS_RESOURCE_EXTERNAL_OPEN_INTENT_DISPATCHED",pre);
                    status.setText("Resource action PASS: external link open was dispatched. Return here and run TOOLS TEST.");
                    resourceActionPendingId="-";
                }catch(Exception e){
                    prefs.edit().putString("resource_v76_claim_status","OPEN_INTENT_FAILED_NO_REPLAY").commit();
                    emit("RESOURCE_ACTION","RESOURCE_EXTERNAL_OPEN_INTENT_FAILED_NO_REPLAY",pre);status.setText("External open failed; no replay.");resourceActionPendingId="-";
                }
                return;
            }
            if("DOWNLOAD_LINK".equals(kind)||"FILE_ACTION".equals(kind)||"BLOB_RESOURCE".equals(kind)||"DATA_RESOURCE".equals(kind)){
                resourceDownloadPending=true;
                eval(resourceActionClickV76Js(expectedId),a->{
                    boolean clicked=a.optBoolean("success",false)&&a.optBoolean("clicked",false)&&a.optInt("locator_count",0)==1;
                    JSONObject st=baseState();put(st,"resource_action_id",expectedId);put(st,"resource_action_kind",kind);put(st,"locator_count",a.optInt("locator_count",0));put(st,"raw_url_remote",false);
                    if(clicked){pageUiDispatches++;pageUiWrites++;emit("RESOURCE_ACTION","PASS_RESOURCE_EXACT_SINGLE_CLICK_DISPATCHED_WAITING_RECEIPT",st);status.setText("Resource click dispatched once. Waiting for the browser download receipt; do not press TEST ACTION again.");}
                    else{resourceDownloadPending=false;prefs.edit().putString("resource_v76_claim_status","CLICK_UNCERTAIN_NO_REPLAY").commit();emit("RESOURCE_ACTION","RESOURCE_CLICK_UNCERTAIN_NO_REPLAY",st);status.setText("Resource click uncertain; no replay.");resourceActionPendingId="-";}
                });
                return;
            }
            prefs.edit().putString("resource_v76_claim_status","BLOCKED_UNSUPPORTED_REALIZATION").commit();
            emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_UNSUPPORTED_REALIZATION",pre);status.setText("TEST ACTION blocked: this resource class has no authorized test realization.");resourceActionPendingId="-";
        });
    }

    private String resourceResolverV2Js(){
        return "(function(){try{"+
            "const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const H=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return ('00000000'+(h>>>0).toString(16)).slice(-8);};"+
            "const V=e=>{if(!e||!e.isConnected)return false;const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true'&&r.width>0&&r.height>0;};"+
            "const D=e=>N([e.tagName||'',e.getAttribute('role')||'',e.getAttribute('aria-label')||'',e.getAttribute('title')||'',e.getAttribute('data-testid')||'',e.getAttribute('name')||'',(e.innerText||e.textContent||'').slice(0,180)].join(' '));"+
            "const before=(a,b)=>!!(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING);"+
            "const canon=h=>{try{if(!h)return '';if(h.startsWith('blob:'))return 'blob:';if(h.startsWith('data:'))return 'data:';const u=new URL(h,location.href);return u.protocol+'//'+u.host+u.pathname;}catch(_){return 'other:'+H(String(h||''));}};"+
            "const turnNodes=[];const seen=new Set();const addTurn=e=>{const t=(e.closest&&e.closest('article[data-testid^=\\\"conversation-turn-\\\"]'))||e;if(t&&!seen.has(t)){seen.add(t);turnNodes.push(t);}};document.querySelectorAll('article[data-testid^=\\\"conversation-turn-\\\"],[data-testid^=\\\"conversation-turn-\\\"],[data-message-author-role]').forEach(addTurn);const turns=turnNodes.map((e,i)=>{const r=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');return{el:e,role:r?String(r.getAttribute('data-message-author-role')||'-'):'-',ref:String(e.getAttribute('data-turn-id')||e.getAttribute('data-testid')||('T'+i)),index:i};});"+
            "const owner=e=>{const direct=turns.filter(t=>t.el.contains(e));if(direct.length===1)return{mode:'DIRECT',turn:direct[0]};if(direct.length>1)return{mode:'AMBIGUOUS',turn:null};let cur=e.parentElement;for(let n=0;n<8&&cur;n++,cur=cur.parentElement){const hits=turns.filter(t=>cur.contains(t.el));const ah=hits.filter(t=>t.role==='assistant');if(ah.length===1)return{mode:'CORRELATED',turn:ah[0]};if(hits.length>1)return{mode:'AMBIGUOUS',turn:null};}let prev=null,next=null;for(const t of turns){if(before(t.el,e))prev=t;else if(before(e,t.el)){next=t;break;}}if(prev&&prev.role==='assistant'&&(!next||before(e,next.el)))return{mode:'CORRELATED',turn:prev};return{mode:'UNOWNED',turn:null};};"+
            "const nodes=[];const add=e=>{if(V(e)&&nodes.indexOf(e)<0)nodes.push(e);};document.querySelectorAll('a[href],[role=link],[download]').forEach(add);document.querySelectorAll('button,[role=button]').forEach(e=>{const d=D(e);if(/download|save|file|attachment|citation|source|reference|resource/.test(d))add(e);});"+
            "let seq=0;const locator=e=>{let x=e.getAttribute('data-cp-resource-locator-v76');if(!x){x='R'+(++seq)+'_'+H(D(e));e.setAttribute('data-cp-resource-locator-v76',x);}return x;};"+
            "const items={};let direct=0,corr=0,unowned=0,amb=0,same=0,cross=0,blob=0,data=0,citation=0,fileAction=0,downloadLink=0;"+
            "for(const e of nodes){const ow=owner(e);if(ow.mode==='DIRECT')direct++;else if(ow.mode==='CORRELATED')corr++;else if(ow.mode==='UNOWNED')unowned++;else amb++;const d=D(e);let href=e.getAttribute('href')||'';try{if(!href&&typeof e.href==='string')href=e.href;}catch(_){}let kind='FILE_ACTION';if(href){if(href.startsWith('blob:')){kind='BLOB_RESOURCE';blob++;}else if(href.startsWith('data:')){kind='DATA_RESOURCE';data++;}else{try{const u=new URL(href,location.href);if(u.origin===location.origin){kind='SAME_ORIGIN_LINK';same++;}else{kind='CROSS_ORIGIN_LINK';cross++;}}catch(_){kind='UNCLASSIFIED_LINK';}}if(e.hasAttribute('download')||/download|save/.test(d)){kind='DOWNLOAD_LINK';downloadLink++;}}else if(/citation|source|reference/.test(d)||N(e.getAttribute('data-testid')||'').includes('citation')){kind='CITATION_CONTROL';citation++;}else fileAction++;if(!(ow.mode==='DIRECT'||ow.mode==='CORRELATED')||!ow.turn)continue;const target=href?canon(href):('labelhash:'+H(d));const key=H(H(ow.turn.ref)+'|'+kind+'|'+target);let it=items[key];if(!it)it=items[key]={id:key,kind:kind,href:href,ownerMode:ow.mode,role:ow.turn.role,turnIndex:ow.turn.index,locators:[],order:nodes.indexOf(e)};const loc=locator(e);if(it.locators.indexOf(loc)<0)it.locators.push(loc);items[key]=it;}"+
            "const vals=Object.values(items);let aliasCount=0,aliasMax=0,locatorCount=0;for(const x of vals){locatorCount+=x.locators.length;if(x.locators.length>1)aliasCount++;if(x.locators.length>aliasMax)aliasMax=x.locators.length;}"+
            "const actionable=vals.filter(x=>x.role==='assistant'&&x.locators.length===1&&['DOWNLOAD_LINK','FILE_ACTION','CROSS_ORIGIN_LINK','BLOB_RESOURCE','DATA_RESOURCE'].includes(x.kind));const pri={DOWNLOAD_LINK:50,FILE_ACTION:40,BLOB_RESOURCE:35,DATA_RESOURCE:34,CROSS_ORIGIN_LINK:30};actionable.sort((a,b)=>(pri[b.kind]||0)-(pri[a.kind]||0)||a.order-b.order);const pref=actionable.length?actionable[0]:null;"+
            "window.__cpResourceResolverV76={routePath:location.pathname,items:items,preferredId:pref?pref.id:'-'};const sig=vals.map(x=>x.id+':'+x.locators.length).sort().join('|');"+
            "return JSON.stringify({success:true,global_resource_candidate_count:nodes.length,global_visible_links:Array.from(document.querySelectorAll('a[href]')).filter(V).length,owned_direct_count:direct,owned_correlated_count:corr,unowned_candidate_count:unowned,ambiguous_owner_count:amb,semantic_resource_count:vals.length,dom_locator_count:locatorCount,alias_resource_count:aliasCount,alias_locator_max:aliasMax,same_origin_resource_count:same,cross_origin_resource_count:cross,blob_resource_count:blob,data_resource_count:data,citation_like_count:citation,file_action_candidate_count:fileAction,download_link_candidate_count:downloadLink,actionable_unique_count:actionable.length,preferred_action_id:pref?pref.id:'-',preferred_action_kind:pref?pref.kind:'NONE',preferred_action_href:pref?pref.href:'',preferred_locator_count:pref?pref.locators.length:0,resource_semantic_hash:H(sig)});"+
        "}catch(e){return JSON.stringify({success:false,error_class:'RESOURCE_RESOLVER_V2_EXCEPTION'});}})()";
    }

    private String resourceActionPrepareV76Js(String id){
        return "(function(){try{const R=window.__cpResourceResolverV76;if(!R||R.routePath!==location.pathname)return JSON.stringify({success:false,fresh:false,reason:'STALE_ROUTE'});const x=R.items['"+js(id)+"'];if(!x)return JSON.stringify({success:false,fresh:false,reason:'MISSING_RESOURCE'});const all=Array.from(document.querySelectorAll('[data-cp-resource-locator-v76]')).filter(e=>x.locators.indexOf(e.getAttribute('data-cp-resource-locator-v76'))>=0);const vis=all.filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return e.isConnected&&s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true'&&r.width>0&&r.height>0;});return JSON.stringify({success:true,fresh:vis.length===1,id:x.id,kind:x.kind,href:x.href||'',locator_count:vis.length});}catch(e){return JSON.stringify({success:false,fresh:false,reason:'PREPARE_EXCEPTION'});}})()";
    }

    private String resourceActionClickV76Js(String id){
        return "(function(){try{const R=window.__cpResourceResolverV76;if(!R||R.routePath!==location.pathname)return JSON.stringify({success:false,clicked:false,locator_count:0});const x=R.items['"+js(id)+"'];if(!x)return JSON.stringify({success:false,clicked:false,locator_count:0});const vis=Array.from(document.querySelectorAll('[data-cp-resource-locator-v76]')).filter(e=>x.locators.indexOf(e.getAttribute('data-cp-resource-locator-v76'))>=0).filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return e.isConnected&&s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true'&&r.width>0&&r.height>0;});if(vis.length!==1)return JSON.stringify({success:false,clicked:false,locator_count:vis.length});const e=vis[0];if(e.disabled||e.getAttribute('aria-disabled')==='true')return JSON.stringify({success:false,clicked:false,locator_count:1});e.click();return JSON.stringify({success:true,clicked:true,locator_count:1});}catch(e){return JSON.stringify({success:false,clicked:false,locator_count:0});}})()";
    }

    private void runToolsTest(){
        if(learning||plannerRunning||toolsTestRunning||resourceDownloadPending){status.setText("TOOLS TEST blocked while another operation is active.");return;}
        testId="cp74-"+UUID.randomUUID();startedMs=System.currentTimeMillis();telemetrySeq=0;remoteTelemetryPosts=0;
        toolsTestRunning=true;toolsEvalInFlight=false;toolsTestPhase="OPEN_DISPATCH_IN_FLIGHT";
        JSONObject start=baseState();put(start,"reversible",true);put(start,"event_driven",true);emit("TOOLS_TEST","TOOLS_HIDDEN_MENU_TEST_STARTED",start);
        eval(toolsOpenV76Js(),o->{
            boolean clicked=o.optBoolean("success",false)&&o.optBoolean("clicked",false)&&o.optInt("trigger_count",0)==1;
            JSONObject st=baseState();put(st,"trigger_count",o.optInt("trigger_count",0));put(st,"trigger_semantic_hash",o.optString("trigger_semantic_hash","-"));put(st,"clicked",clicked);
            if(!clicked){toolsTestRunning=false;toolsTestPhase="FAILED";emit("TOOLS_TEST","TOOLS_TRIGGER_NOT_EXACTLY_ONE_NO_CLICK",st);status.setText("TOOLS TEST blocked: exact Add trigger was not uniquely resolved.");return;}
            pageUiDispatches++;pageUiWrites++;toolsTestPhase="WAIT_MENU_RECEIPT";emit("TOOLS_TEST","PASS_TOOLS_TRIGGER_SINGLE_CLICK_DISPATCHED",st);
            status.setText("TOOLS TEST opened Add. Waiting for event-driven menu receipt...");requestEventRead("TOOLS_TRIGGER_CLICK");
        });
    }

    private void driveToolsTestOnEvent(String reason){
        if(!toolsTestRunning||toolsEvalInFlight)return;
        if("WAIT_MENU_RECEIPT".equals(toolsTestPhase)){
            toolsEvalInFlight=true;
            eval(toolsMenuCensusV76Js(),o->{
                toolsEvalInFlight=false;if(!toolsTestRunning||!"WAIT_MENU_RECEIPT".equals(toolsTestPhase))return;
                if(!o.optBoolean("success",false)||!o.optBoolean("menu_materialized",false))return;
                JSONObject st=baseState();String[] ints={"menu_surface_count","option_count","search_count","deep_research_count","file_count","photo_image_count","apps_plugins_count","project_count","other_tool_count"};for(String k:ints)put(st,k,o.optInt(k,0));put(st,"tool_semantic_hash",o.optString("tool_semantic_hash","-"));put(st,"event_reason_hash",hashNorm(reason));put(st,"raw_text_remote",false);
                emit("TOOLS_TEST","PASS_TOOLS_HIDDEN_MENU_MATERIALIZED_AND_ENUMERATED",st);
                toolsTestPhase="CLOSE_DISPATCH_IN_FLIGHT";toolsEvalInFlight=true;
                eval(toolsCloseV76Js(),c->{
                    toolsEvalInFlight=false;if(!toolsTestRunning)return;boolean clicked=c.optBoolean("success",false)&&c.optBoolean("clicked",false)&&c.optInt("trigger_count",0)==1;
                    JSONObject cs=baseState();put(cs,"trigger_count",c.optInt("trigger_count",0));put(cs,"clicked",clicked);
                    if(!clicked){toolsTestRunning=false;toolsTestPhase="FAILED";emit("TOOLS_TEST","TOOLS_CLOSE_TRIGGER_FAILED_NO_REPLAY",cs);status.setText("TOOLS TEST enumerated the menu but could not prove the reversible close click.");return;}
                    pageUiDispatches++;pageUiWrites++;toolsTestPhase="WAIT_CLOSE_RECEIPT";emit("TOOLS_TEST","PASS_TOOLS_CLOSE_SINGLE_CLICK_DISPATCHED",cs);requestEventRead("TOOLS_CLOSE_CLICK");
                });
            });return;
        }
        if("WAIT_CLOSE_RECEIPT".equals(toolsTestPhase)){
            toolsEvalInFlight=true;
            eval(toolsMenuCensusV76Js(),o->{
                toolsEvalInFlight=false;if(!toolsTestRunning||!"WAIT_CLOSE_RECEIPT".equals(toolsTestPhase))return;
                if(!o.optBoolean("success",false)||o.optBoolean("menu_materialized",true))return;
                JSONObject st=baseState();put(st,"menu_closed",true);put(st,"event_reason_hash",hashNorm(reason));
                emit("TOOLS_TEST","PASS_TOOLS_MENU_RESTORED_CLOSED",st);emit("PLANNER_FINAL","PASS_TOOLS_HIDDEN_MENU_CENSUS_COMPLETE",st);
                toolsTestRunning=false;toolsTestPhase="DONE";status.setText("TOOLS TEST PASS. Menu was enumerated and restored closed. Tell ChatGPT the test finished.");
            });
        }
    }

    private String toolsOpenV76Js(){
        return "(function(){try{const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();const V=e=>{if(!e||!e.isConnected)return false;const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true'&&r.width>0&&r.height>0;};const H=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return('00000000'+(h>>>0).toString(16)).slice(-8);};const D=e=>N([e.getAttribute('aria-label')||'',e.getAttribute('title')||'',e.getAttribute('data-testid')||'',e.getAttribute('name')||'',e.innerText||e.textContent||''].join(' '));const C=Array.from(document.querySelectorAll('button,[role=button]')).filter(V).filter(e=>!e.closest('[data-message-author-role]')).filter(e=>/\\b(add|attach|attachment|upload|file|photo|image)\\b/.test(D(e)));if(C.length!==1)return JSON.stringify({success:false,clicked:false,trigger_count:C.length,trigger_semantic_hash:H(C.map(D).sort().join('|'))});const e=C[0];if(e.disabled||e.getAttribute('aria-disabled')==='true')return JSON.stringify({success:false,clicked:false,trigger_count:1,trigger_semantic_hash:H(D(e))});e.setAttribute('data-cp-tools-trigger-v76','1');e.click();return JSON.stringify({success:true,clicked:true,trigger_count:1,trigger_semantic_hash:H(D(e))});}catch(e){return JSON.stringify({success:false,clicked:false,trigger_count:0});}})()";
    }

    private String toolsCloseV76Js(){
        return "(function(){try{const V=e=>{if(!e||!e.isConnected)return false;const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true'&&r.width>0&&r.height>0;};const C=Array.from(document.querySelectorAll('[data-cp-tools-trigger-v76=\\\"1\\\"]')).filter(V);if(C.length!==1)return JSON.stringify({success:false,clicked:false,trigger_count:C.length});const e=C[0];if(e.disabled||e.getAttribute('aria-disabled')==='true')return JSON.stringify({success:false,clicked:false,trigger_count:1});e.click();return JSON.stringify({success:true,clicked:true,trigger_count:1});}catch(e){return JSON.stringify({success:false,clicked:false,trigger_count:0});}})()";
    }

    private String toolsMenuCensusV76Js(){
        return "(function(){try{const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();const V=e=>{if(!e||!e.isConnected)return false;const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true'&&r.width>0&&r.height>0;};const H=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return('00000000'+(h>>>0).toString(16)).slice(-8);};const D=e=>N([e.getAttribute('role')||'',e.getAttribute('aria-label')||'',e.getAttribute('title')||'',e.getAttribute('data-testid')||'',e.innerText||e.textContent||''].join(' '));const trig=Array.from(document.querySelectorAll('[data-cp-tools-trigger-v76=\\\"1\\\"]')).filter(V);const expanded=trig.length===1&&trig[0].getAttribute('aria-expanded')==='true';const surfaces=Array.from(document.querySelectorAll('[role=menu],[role=listbox],[role=dialog],[data-radix-menu-content]')).filter(V);const controls=Array.from(document.querySelectorAll('button,[role=button],[role=menuitem],[role=option],[role=radio],[role=checkbox]')).filter(V).filter(e=>!e.closest('[data-message-author-role]')&&!e.hasAttribute('data-cp-tools-trigger-v76'));const toolRe=/search|research|file|upload|photo|image|camera|project|apps?|plugins?|connectors?|canvas|code|study|learn/;const opts=controls.filter(e=>toolRe.test(D(e)));const count=re=>opts.reduce((n,e)=>n+(re.test(D(e))?1:0),0);const search=count(/\\bsearch\\b/),deep=count(/deep research|\\bresearch\\b/),file=count(/file|upload/),photo=count(/photo|image|camera/),apps=count(/apps?|plugins?|connectors?/),project=count(/projects?/);const known=new Set();opts.forEach(e=>{const d=D(e);if(/\\bsearch\\b/.test(d)||/deep research|\\bresearch\\b/.test(d)||/file|upload/.test(d)||/photo|image|camera/.test(d)||/apps?|plugins?|connectors?/.test(d)||/projects?/.test(d))known.add(e);});const sig=opts.map(e=>H(D(e))).sort().join('|');const materialized=expanded||opts.length>0||surfaces.length>0;return JSON.stringify({success:true,menu_materialized:materialized,menu_surface_count:surfaces.length,option_count:opts.length,search_count:search,deep_research_count:deep,file_count:file,photo_image_count:photo,apps_plugins_count:apps,project_count:project,other_tool_count:Math.max(0,opts.length-known.size),tool_semantic_hash:H(sig)});}catch(e){return JSON.stringify({success:false,menu_materialized:false});}})()";
    }

'''
needle='    private void clearLocal(){'
pos=s.find(needle)
assert pos>=0,"clearLocal insertion point"
s=s[:pos]+methods+s[pos:]

# Telemetry lineage.
s=s.replace("TelemetryConfigV75","TelemetryConfigV76")
ACT.write_text(s)
assert OLD.exists();OLD.unlink()
cfg=(PKG/"TelemetryConfigV75.java").read_text()
(PKG/"TelemetryConfigV76.java").write_text(cfg.replace("TelemetryConfigV75","TelemetryConfigV76"))
(PKG/"TelemetryConfigV75.java").unlink()

# Version/package/update continuity.
g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+76\b","versionCode 77",gs);gs=gs.replace("0.73-stable-diag-unified-breadth-frontier","0.74-stable-diag-resource-tools-consolidated");g.write_text(gs)
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorUnifiedBreadthV75Activity","OrchestratorResourceToolsV76Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms and "@xml/cp_accessibility_service_v51" in ms
mf.write_text(ms)

# Regression and safety gates. Exactly five JS click sites are authorized:
# two inherited Planner clicks + resource exact click + tools open + tools close.
out=ACT.read_text()
for required in [
    'RESOURCE TEST','TEST ACTION','TOOLS TEST','runResourceTest','runResourceActionV76','runToolsTest',
    'PASS_RESOURCE_RESOLVER_V2_CENSUS_COMPLETE','owned_direct_count','owned_correlated_count','unowned_candidate_count','ambiguous_owner_count',
    'alias_resource_count','alias_locator_max','data-cp-resource-locator-v76','RESOURCE_ACTION_BLOCKED_STALE_EPOCH',
    'CLAIMED_BEFORE_RESOURCE_ACTION','PASS_RESOURCE_DOWNLOAD_CALLBACK_RECEIPT','PASS_RESOURCE_EXTERNAL_OPEN_INTENT_DISPATCHED',
    'PASS_TOOLS_HIDDEN_MENU_MATERIALIZED_AND_ENUMERATED','PASS_TOOLS_MENU_RESTORED_CLOSED','PASS_TOOLS_HIDDEN_MENU_CENSUS_COMPLETE',
    'WAIT_MENU_RECEIPT','WAIT_CLOSE_RECEIPT','requestEventRead("TOOLS_TRIGGER_CLICK")','requestEventRead("TOOLS_CLOSE_CLICK")',
    'plannerFormatRepairAttempts<1','PLANNER_RESPONSE_FORMAT_REPAIR_REQUESTED','executePlannerAction(action,o);',
    'pageFinishedEpoch==documentEpoch','PLANNER_ACTION_SOURCE_NOT_PROVEN_FRESH_TEMP','TelemetryConfigV76'
]: assert required in out,required
for forbidden in [
    'Thread.sleep','setTimeout(','setInterval(','ScheduledExecutorService','TimerTask','elementFromPoint','document.evaluate',
    'dispatchTouchEvent(','performClick(','ACTION_SET_PROGRESS','CookieManager','getCookie(','addJavascriptInterface','XPathResult'
]: assert forbidden not in out,forbidden
assert out.count('.click();')==5,out.count('.click();')
assert 'applicationId \'com.homayounisaghar.chatgptwebviewprobe.diag\'' in g.read_text()
assert 'versionCode 77' in g.read_text()
assert "versionName '0.74-stable-diag-resource-tools-consolidated'" in g.read_text()
print('PASS v0.74 consolidated audit: global resource resolver + guarded action + event-driven reversible tools census; proven Planner/breadth preserved')
