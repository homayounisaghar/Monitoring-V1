#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.75: consolidated repair for the real-device v0.74 resource-action misdispatch.
# The repair hardens resource provenance/ownership and re-certifies semantics at action time,
# while preserving the proven Planner, breadth, and dedicated Tools paths.
runpy.run_path("ci/generate_chatgpt_webview_v76_resource_tools_consolidated_fix1.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorResourceToolsV76Activity.java"
ACT=PKG/"OrchestratorResourceToolsV77Activity.java"
s=OLD.read_text()

# Identity rollover first so the replacement blocks use the v0.75 names consistently.
s=s.replace("OrchestratorResourceToolsV76Activity","OrchestratorResourceToolsV77Activity")
s=s.replace("V76","V77")
s=s.replace("resourceResolverV2Js","resourceResolverV3Js")
s=s.replace("RESOURCE_RESOLVER_V2","RESOURCE_RESOLVER_V3")
s=s.replace('SCHEMA="cp-v76-resource-tools-consolidated-v1"','SCHEMA="cp-v77-resource-provenance-hardened-v1"')
s=s.replace('SCENARIO="resource-resolver-tools-consolidated"','SCENARIO="resource-provenance-action-recertification"')
s=s.replace('getSharedPreferences("cp_v76_resource_tools",MODE_PRIVATE)','getSharedPreferences("cp_v77_resource_provenance",MODE_PRIVATE)')
s=s.replace('testId="cp74-"+UUID.randomUUID();','testId="cp75-"+UUID.randomUUID();')
s=s.replace('put(start,"resolver_version",2)','put(start,"resolver_version",3)')
s=s.replace('put(st,"resolver_version",2)','put(st,"resolver_version",3)')
s=s.replace('v0.74 Resource Resolver + Tools consolidated ready.','v0.75 Resource provenance hardened + Tools ready.')

# Add the new sanitized provenance counters to RESOURCE TEST telemetry.
old_ints='"actionable_unique_count","preferred_locator_count"};'
new_ints='"actionable_unique_count","preferred_locator_count","excluded_global_control_count","strong_nonhref_action_count","bounded_correlated_count"};'
assert s.count(old_ints)==1,s.count(old_ints)
s=s.replace(old_ints,new_ints,1)

# The event bridge now also observes an incompatible Add/Attach-menu materialization while
# a resource click is awaiting a download receipt. This is failure evidence, never success/replay authority.
hook='        if(toolsTestRunning)driveToolsTestOnEvent(reason);\n'
assert s.count(hook)==1,s.count(hook)
s=s.replace(hook,hook+'        if(resourceDownloadPending)driveResourcePendingOnEventV77(reason);\n',1)

# Replace the complete material-action admission method. A fresh Resolver-v3 recertification
# must reproduce the exact selected semantic id/class before durable claim or side effect.
start=s.index('    private void runResourceActionV77(){\n')
end=s.index('    private String resourceResolverV3Js(){\n',start)
run_action=r'''    private void runResourceActionV77(){
        if(learning||plannerRunning||toolsTestRunning||resourceDownloadPending){status.setText("TEST ACTION blocked while another operation is active.");return;}
        if("-".equals(resourceSelectedId)||resourceSelectedLocatorCount!=1){status.setText("TEST ACTION blocked: RESOURCE TEST did not prove one actionable resource.");return;}
        if(resourceScanDocumentEpoch!=documentEpoch||resourceScanPageFinishedEpoch!=pageFinishedEpoch||pageFinishedEpoch!=documentEpoch){
            JSONObject st=baseState();put(st,"scan_document_epoch",resourceScanDocumentEpoch);put(st,"current_document_epoch",documentEpoch);emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_STALE_EPOCH",st);status.setText("TEST ACTION blocked: page changed after RESOURCE TEST.");return;
        }
        final String expectedId=resourceSelectedId;
        final String expectedKind=resourceSelectedKind;
        eval(resourceResolverV3Js(),o->{
            String id=o.optString("preferred_action_id","-");
            String kind=o.optString("preferred_action_kind","NONE");
            String href=o.optString("preferred_action_href","");
            int locators=o.optInt("preferred_locator_count",0);
            boolean epochFresh=resourceScanDocumentEpoch==documentEpoch&&resourceScanPageFinishedEpoch==pageFinishedEpoch&&pageFinishedEpoch==documentEpoch;
            boolean fresh=o.optBoolean("success",false)&&epochFresh&&locators==1&&expectedId.equals(id)&&expectedKind.equals(kind);
            JSONObject pre=baseState();put(pre,"resource_action_id",expectedId);put(pre,"resource_action_kind",kind);put(pre,"locator_count",locators);put(pre,"fresh",fresh);put(pre,"semantic_recertified",fresh);put(pre,"resolver_version",3);put(pre,"excluded_global_control_count",o.optInt("excluded_global_control_count",0));put(pre,"raw_url_remote",false);
            if(!fresh){emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_SEMANTIC_RECERTIFICATION_FAILED",pre);status.setText("TEST ACTION blocked: resource provenance/semantics no longer recertify exactly.");return;}
            boolean committed=prefs.edit().putString("resource_v77_claim_status","CLAIMED").putString("resource_v77_claim_id",expectedId).commit();
            put(pre,"claim_committed",committed);emit("DURABLE_CLAIM",committed?"CLAIMED_BEFORE_RESOURCE_ACTION":"RESOURCE_ACTION_CLAIM_COMMIT_FAILED",pre);
            if(!committed){status.setText("TEST ACTION blocked: durable claim failed.");return;}
            resourceActionPendingId=expectedId;
            if("CROSS_ORIGIN_LINK".equals(kind)&&href.matches("^https?://.+")){
                try{
                    android.content.Intent intent=new android.content.Intent(android.content.Intent.ACTION_VIEW,android.net.Uri.parse(href));
                    startActivity(intent);pageUiDispatches++;pageUiWrites++;
                    prefs.edit().putString("resource_v77_claim_status","OPEN_INTENT_DISPATCHED").commit();
                    emit("RESOURCE_ACTION","PASS_RESOURCE_EXTERNAL_OPEN_INTENT_DISPATCHED",pre);
                    status.setText("Resource action PASS: external link open was dispatched. Return here and run TOOLS TEST.");
                    resourceActionPendingId="-";
                }catch(Exception e){
                    prefs.edit().putString("resource_v77_claim_status","OPEN_INTENT_FAILED_NO_REPLAY").commit();
                    emit("RESOURCE_ACTION","RESOURCE_EXTERNAL_OPEN_INTENT_FAILED_NO_REPLAY",pre);status.setText("External open failed; no replay.");resourceActionPendingId="-";
                }
                return;
            }
            if("DOWNLOAD_LINK".equals(kind)||"FILE_ACTION".equals(kind)||"BLOB_RESOURCE".equals(kind)||"DATA_RESOURCE".equals(kind)){
                resourceDownloadPending=true;
                eval(resourceActionClickV77Js(expectedId),a->{
                    boolean clicked=a.optBoolean("success",false)&&a.optBoolean("clicked",false)&&a.optInt("locator_count",0)==1&&a.optBoolean("semantic_guard",false);
                    JSONObject st=baseState();put(st,"resource_action_id",expectedId);put(st,"resource_action_kind",kind);put(st,"locator_count",a.optInt("locator_count",0));put(st,"semantic_guard",a.optBoolean("semantic_guard",false));put(st,"raw_url_remote",false);
                    if(clicked){pageUiDispatches++;pageUiWrites++;emit("RESOURCE_ACTION","PASS_RESOURCE_EXACT_SINGLE_CLICK_DISPATCHED_WAITING_RECEIPT",st);status.setText("Resource click dispatched once. Waiting for an explicit download/effect receipt; do not press TEST ACTION again.");}
                    else{resourceDownloadPending=false;prefs.edit().putString("resource_v77_claim_status","CLICK_UNCERTAIN_NO_REPLAY").commit();emit("RESOURCE_ACTION","RESOURCE_CLICK_UNCERTAIN_NO_REPLAY",st);status.setText("Resource click uncertain; no replay.");resourceActionPendingId="-";}
                });
                return;
            }
            prefs.edit().putString("resource_v77_claim_status","BLOCKED_UNSUPPORTED_REALIZATION").commit();
            emit("RESOURCE_ACTION","RESOURCE_ACTION_BLOCKED_UNSUPPORTED_REALIZATION",pre);status.setText("TEST ACTION blocked: this resource class has no authorized test realization.");resourceActionPendingId="-";
        });
    }

'''
s=s[:start]+run_action+s[end:]

# Replace the full resolver/prepare/click family up to the dedicated Tools test.
start=s.index('    private String resourceResolverV3Js(){\n')
end=s.index('    private void runToolsTest(){\n',start)
resource_block=r'''    private String resourceResolverV3Js(){
        return "(function(){try{"+
            "const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const H=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return ('00000000'+(h>>>0).toString(16)).slice(-8);};"+
            "const V=e=>{if(!e||!e.isConnected)return false;const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true'&&r.width>0&&r.height>0;};"+
            "const D=e=>N([e.tagName||'',e.getAttribute('role')||'',e.getAttribute('aria-label')||'',e.getAttribute('title')||'',e.getAttribute('data-testid')||'',e.getAttribute('name')||'',(e.innerText||e.textContent||'').slice(0,180)].join(' '));"+
            "const A=e=>N([e.tagName||'',e.getAttribute('role')||'',e.getAttribute('aria-label')||'',e.getAttribute('title')||'',e.getAttribute('data-testid')||'',e.getAttribute('name')||''].join(' '));"+
            "const before=(a,b)=>!!(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING);"+
            "const canon=h=>{try{if(!h)return '';if(h.startsWith('blob:'))return 'blob:';if(h.startsWith('data:'))return 'data:';const u=new URL(h,location.href);return u.protocol+'//'+u.host+u.pathname;}catch(_){return 'other:'+H(String(h||''));}};"+
            "const turnNodes=[];const seen=new Set();const addTurn=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);turnNodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(addTurn);const turns=turnNodes.map((e,i)=>{const r=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');return{el:e,role:r?String(r.getAttribute('data-message-author-role')||'-'):'-',ref:String(e.getAttribute('data-turn-id')||e.getAttribute('data-testid')||('T'+i)),index:i};});"+
            "const directAssistant=e=>{const h=turns.filter(t=>t.role==='assistant'&&t.el.contains(e));return h.length===1?h[0]:null;};"+
            "const isComposer=e=>!!(e.closest&&(e.closest('form')||e.closest(`[data-testid*='composer']`)));"+
            "const resourceWrapper=e=>e.closest&&e.closest(`[data-testid*='citation'],[data-testid*='source'],[data-testid*='resource'],[data-testid*='file'],[data-testid*='download'],[data-testid*='attachment']`);"+
            "const strongNonHref=e=>{if(isComposer(e))return false;const a=A(e),w=resourceWrapper(e);return !!w||/download|save|file|attachment|citation|source|reference|resource/.test(a);};"+
            "const owner=e=>{const direct=turns.filter(t=>t.el.contains(e));if(direct.length===1)return{mode:'DIRECT',turn:direct[0]};if(direct.length>1)return{mode:'AMBIGUOUS',turn:null};const w=resourceWrapper(e);if(w){const hits=turns.filter(t=>w.contains(t.el));const ah=hits.filter(t=>t.role==='assistant');if(hits.length===1&&ah.length===1)return{mode:'CORRELATED_WRAPPER',turn:ah[0]};if(hits.length>1)return{mode:'AMBIGUOUS',turn:null};}let prev=null,next=null;for(const t of turns){if(before(t.el,e))prev=t;else if(before(e,t.el)){next=t;break;}}if(prev&&next&&prev.role==='assistant'&&before(prev.el,e)&&before(e,next.el))return{mode:'CORRELATED_BOUNDED',turn:prev};return{mode:'UNOWNED',turn:null};};"+
            "const nodes=[];const add=e=>{if(V(e)&&nodes.indexOf(e)<0)nodes.push(e);};document.querySelectorAll('a[href],[role=link],[download]').forEach(add);"+
            "let excludedGlobal=0,strongNonHrefCount=0;const resourceWords=/download|save|file|attachment|citation|source|reference|resource/;Array.from(document.querySelectorAll('button,[role=button]')).filter(V).forEach(e=>{if(!resourceWords.test(D(e)))return;const da=directAssistant(e);if(!da||isComposer(e)){excludedGlobal++;return;}if(strongNonHref(e)){add(e);strongNonHrefCount++;}});"+
            "let seq=0;const locator=e=>{let x=e.getAttribute('data-cp-resource-locator-v77');if(!x){x='R'+(++seq)+'_'+H(A(e));e.setAttribute('data-cp-resource-locator-v77',x);}return x;};"+
            "const items={};let direct=0,corr=0,bounded=0,unowned=0,amb=0,same=0,cross=0,blob=0,data=0,citation=0,fileAction=0,downloadLink=0;"+
            "for(const e of nodes){const ow=owner(e);if(ow.mode==='DIRECT')direct++;else if(ow.mode==='CORRELATED_WRAPPER'||ow.mode==='CORRELATED_BOUNDED'){corr++;if(ow.mode==='CORRELATED_BOUNDED')bounded++;}else if(ow.mode==='UNOWNED')unowned++;else amb++;const d=D(e),a=A(e);let href=e.getAttribute('href')||'';try{if(!href&&typeof e.href==='string')href=e.href;}catch(_){}let kind='UNCLASSIFIED_CONTROL',evidence='NONE';if(href){if(href.startsWith('blob:')){kind='BLOB_RESOURCE';blob++;evidence='URL_BACKED';}else if(href.startsWith('data:')){kind='DATA_RESOURCE';data++;evidence='URL_BACKED';}else{try{const u=new URL(href,location.href);if(u.origin===location.origin){kind='SAME_ORIGIN_LINK';same++;}else{kind='CROSS_ORIGIN_LINK';cross++;}evidence='URL_BACKED';}catch(_){kind='UNCLASSIFIED_LINK';}}if(e.hasAttribute('download')||/download|save/.test(a)){kind='DOWNLOAD_LINK';downloadLink++;evidence='URL_BACKED_DOWNLOAD';}}else if(/citation|source|reference/.test(a)||N(e.getAttribute('data-testid')||'').includes('citation')){kind='CITATION_CONTROL';citation++;evidence='DIRECT_STRUCTURAL';}else if(directAssistant(e)&&strongNonHref(e)){kind='FILE_ACTION';fileAction++;evidence='STRONG_DIRECT_NONHREF';}if(!(ow.mode==='DIRECT'||ow.mode==='CORRELATED_WRAPPER'||ow.mode==='CORRELATED_BOUNDED')||!ow.turn)continue;if(kind==='FILE_ACTION'&&!(ow.mode==='DIRECT'&&ow.turn.role==='assistant'))continue;if(kind==='UNCLASSIFIED_CONTROL'||kind==='UNCLASSIFIED_LINK')continue;const w=resourceWrapper(e),wt=w?N(w.getAttribute('data-testid')||''):'';const target=href?canon(href):('struct:'+H(A(e)+'|'+wt));const key=H(H(ow.turn.ref)+'|'+kind+'|'+target);let it=items[key];if(!it)it=items[key]={id:key,kind:kind,href:href,ownerMode:ow.mode,ownerRef:ow.turn.ref,role:ow.turn.role,turnIndex:ow.turn.index,target:target,evidence:evidence,locators:[],order:nodes.indexOf(e)};const loc=locator(e);if(it.locators.indexOf(loc)<0)it.locators.push(loc);items[key]=it;}"+
            "const vals=Object.values(items);let aliasCount=0,aliasMax=0,locatorCount=0;for(const x of vals){locatorCount+=x.locators.length;if(x.locators.length>1)aliasCount++;if(x.locators.length>aliasMax)aliasMax=x.locators.length;}"+
            "const actionable=vals.filter(x=>x.role==='assistant'&&x.locators.length===1&&['DOWNLOAD_LINK','CROSS_ORIGIN_LINK','BLOB_RESOURCE','DATA_RESOURCE','FILE_ACTION'].includes(x.kind)&&(x.kind!=='FILE_ACTION'||(x.ownerMode==='DIRECT'&&x.evidence==='STRONG_DIRECT_NONHREF')));const pri={DOWNLOAD_LINK:60,CROSS_ORIGIN_LINK:55,BLOB_RESOURCE:50,DATA_RESOURCE:49,FILE_ACTION:40};actionable.sort((a,b)=>(pri[b.kind]||0)-(pri[a.kind]||0)||a.order-b.order);const pref=actionable.length?actionable[0]:null;"+
            "window.__cpResourceResolverV77={routePath:location.pathname,items:items,preferredId:pref?pref.id:'-'};const sig=vals.map(x=>x.id+':'+x.locators.length+':'+x.ownerMode).sort().join('|');"+
            "return JSON.stringify({success:true,global_resource_candidate_count:nodes.length,global_visible_links:Array.from(document.querySelectorAll('a[href]')).filter(V).length,owned_direct_count:direct,owned_correlated_count:corr,bounded_correlated_count:bounded,unowned_candidate_count:unowned,ambiguous_owner_count:amb,semantic_resource_count:vals.length,dom_locator_count:locatorCount,alias_resource_count:aliasCount,alias_locator_max:aliasMax,same_origin_resource_count:same,cross_origin_resource_count:cross,blob_resource_count:blob,data_resource_count:data,citation_like_count:citation,file_action_candidate_count:fileAction,download_link_candidate_count:downloadLink,excluded_global_control_count:excludedGlobal,strong_nonhref_action_count:strongNonHrefCount,actionable_unique_count:actionable.length,preferred_action_id:pref?pref.id:'-',preferred_action_kind:pref?pref.kind:'NONE',preferred_action_href:pref?pref.href:'',preferred_locator_count:pref?pref.locators.length:0,resource_semantic_hash:H(sig)});"+
        "}catch(e){return JSON.stringify({success:false,error_class:'RESOURCE_RESOLVER_V3_EXCEPTION'});}})()";
    }

    private String resourceActionClickV77Js(String id){
        return "(function(){try{const R=window.__cpResourceResolverV77;if(!R||R.routePath!==location.pathname)return JSON.stringify({success:false,clicked:false,locator_count:0,semantic_guard:false});const x=R.items['"+jsV77(id)+"'];if(!x||x.role!=='assistant')return JSON.stringify({success:false,clicked:false,locator_count:0,semantic_guard:false});if(x.kind==='FILE_ACTION'&&(x.ownerMode!=='DIRECT'||x.evidence!=='STRONG_DIRECT_NONHREF'))return JSON.stringify({success:false,clicked:false,locator_count:0,semantic_guard:false});const vis=Array.from(document.querySelectorAll('[data-cp-resource-locator-v77]')).filter(e=>x.locators.indexOf(e.getAttribute('data-cp-resource-locator-v77'))>=0).filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return e.isConnected&&s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true'&&r.width>0&&r.height>0;});if(vis.length!==1)return JSON.stringify({success:false,clicked:false,locator_count:vis.length,semantic_guard:false});const e=vis[0];if(e.disabled||e.getAttribute('aria-disabled')==='true')return JSON.stringify({success:false,clicked:false,locator_count:1,semantic_guard:false});e.click();return JSON.stringify({success:true,clicked:true,locator_count:1,semantic_guard:true});}catch(e){return JSON.stringify({success:false,clicked:false,locator_count:0,semantic_guard:false});}})()";
    }

    private void driveResourcePendingOnEventV77(String reason){
        if(!resourceDownloadPending||"-".equals(resourceActionPendingId))return;
        eval(toolsMenuCensusV77Js(),o->{
            if(!resourceDownloadPending||"-".equals(resourceActionPendingId))return;
            if(!o.optBoolean("success",false)||!o.optBoolean("menu_materialized",false))return;
            resourceDownloadPending=false;
            prefs.edit().putString("resource_v77_claim_status","MISDISPATCHED_NONRESOURCE_UI_NO_REPLAY").commit();
            JSONObject st=baseState();put(st,"resource_action_id",resourceActionPendingId);put(st,"menu_surface_count",o.optInt("menu_surface_count",0));put(st,"option_count",o.optInt("option_count",0));put(st,"event_reason_hash",hashNorm(reason));put(st,"uncertain_effect",true);put(st,"raw_text_remote",false);
            emit("RESOURCE_ACTION","RESOURCE_ACTION_MISDISPATCHED_NONRESOURCE_UI",st);
            status.setText("Resource action FAILED: incompatible Add/Tools UI materialized. No replay authorized.");
            resourceActionPendingId="-";
        });
    }

'''
s=s[:start]+resource_block+s[end:]

# Durable claim field names and user-facing status now refer to v0.75.
s=s.replace('resource_v76_claim_status','resource_v77_claim_status')
s=s.replace('resource_v76_claim_id','resource_v77_claim_id')
s=s.replace('v0.74','v0.75')

# Write the renamed Activity and remove the generated v0.74 class.
ACT.write_text(s)
OLD.unlink()

# Telemetry class rollover.
old_cfg=PKG/"TelemetryConfigV76.java"
new_cfg=PKG/"TelemetryConfigV77.java"
cfg=old_cfg.read_text().replace("TelemetryConfigV76","TelemetryConfigV77")
new_cfg.write_text(cfg)
old_cfg.unlink()

# Version/package/update continuity.
g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+77\b","versionCode 78",gs);gs=gs.replace("0.74-stable-diag-resource-tools-consolidated","0.75-stable-diag-resource-provenance-hardened");g.write_text(gs)
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorResourceToolsV76Activity","OrchestratorResourceToolsV77Activity");mf.write_text(ms)

# Consolidated regression/safety gates for the observed defect family.
out=ACT.read_text()
resolver=out[out.index('private String resourceResolverV3Js'):out.index('private void runToolsTest')]
assert "prev&&next&&prev.role==='assistant'" in resolver
assert "(!next||" not in resolver
assert "directAssistant(e)&&strongNonHref(e)" in resolver
assert "if(!da||isComposer(e)){excludedGlobal++;return;}" in resolver
assert "FILE_ACTION:40" in resolver and "CROSS_ORIGIN_LINK:55" in resolver
assert resolver.index("CROSS_ORIGIN_LINK:55") < resolver.index("FILE_ACTION:40")
assert "x.kind==='FILE_ACTION'&&(x.ownerMode!=='DIRECT'||x.evidence!=='STRONG_DIRECT_NONHREF')" in resolver
assert 'eval(resourceResolverV3Js(),o->{' in out
assert 'RESOURCE_ACTION_BLOCKED_SEMANTIC_RECERTIFICATION_FAILED' in out
assert 'RESOURCE_ACTION_MISDISPATCHED_NONRESOURCE_UI' in out
assert 'driveResourcePendingOnEventV77(reason)' in out
assert "data-cp-resource-locator-v77" in out
assert "TelemetryConfigV77" in out
assert out.count('.click();')==5,out.count('.click();')
for forbidden in [
    'Thread.sleep','setTimeout(','setInterval(','ScheduledExecutorService','TimerTask',
    'elementFromPoint','document.evaluate','dispatchTouchEvent(','performClick(',
    'ACTION_SET_PROGRESS','CookieManager','getCookie(','addJavascriptInterface','XPathResult'
]:
    assert forbidden not in out,forbidden
assert "versionCode 78" in g.read_text()
assert "versionName '0.75-stable-diag-resource-provenance-hardened'" in g.read_text()
assert "OrchestratorResourceToolsV77Activity" in mf.read_text()
print("PASS v0.75: provenance-bounded resolver + semantic action recertification + incompatible-UI receipt")
