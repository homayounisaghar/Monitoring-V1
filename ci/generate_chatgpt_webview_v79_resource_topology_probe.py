#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.77 is diagnostic-only. It does not change Resource ownership and does not
# authorize any Resource side effect. It exposes sanitized DOM-topology evidence
# for the URL-backed candidates that v0.76 discovered but could not own.
runpy.run_path("ci/generate_chatgpt_webview_v78_resource_final_bounded_wrapped.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorResourceToolsV78Activity.java"
ACT=PKG/"OrchestratorResourceToolsV79Activity.java"
s=OLD.read_text()

# Identity rollover. Existing v0.76 action machinery remains present only as
# dormant compatibility code; runResourceActionV79 is replaced below and cannot
# enter any material Resource action path in this diagnostic build.
s=s.replace("OrchestratorResourceToolsV78Activity","OrchestratorResourceToolsV79Activity")
s=s.replace("TelemetryConfigV78","TelemetryConfigV79")
s=s.replace("V78","V79")
s=s.replace('SCHEMA="cp-v78-resource-final-bounded-wrapped-v1"','SCHEMA="cp-v79-resource-topology-probe-v1"')
s=s.replace('SCENARIO="resource-final-bounded-wrapped-navigation-receipt"','SCENARIO="resource-topology-read-only"')
s=s.replace('getSharedPreferences("cp_v78_resource_final_bounded",MODE_PRIVATE)','getSharedPreferences("cp_v79_resource_topology_probe",MODE_PRIVATE)')
s=s.replace('testId="cp76-"+UUID.randomUUID();','testId="cp77-"+UUID.randomUUID();')
s=s.replace('resource_v78_claim_','resource_v79_claim_')
s=s.replace('data-cp-resource-locator-v78','data-cp-resource-locator-v79')
s=s.replace('__cpResourceResolverV78','__cpResourceResolverV79')
s=s.replace('v0.76 Final-bounded wrapped-resource resolver + Tools ready.','v0.77 Read-only Resource topology probe + Tools ready.')
s=s.replace('"RESOURCE TEST"','"TOPOLOGY PROBE"')
s=s.replace('"TEST ACTION"','"ACTION DISABLED"')

# Replace RESOURCE TEST with the approved read-only topology probe. Every emitted
# candidate field is a boolean, enum, count, or hash. No raw URL/text/HTML is
# returned from JavaScript or admitted to telemetry.
start=s.index('    private void runResourceTest(){\n')
end=s.index('    private void runResourceActionV79(){\n',start)
run_probe=r'''    private void runResourceTest(){
        if(learning||plannerRunning||toolsTestRunning||resourceDownloadPending||resourceNavigationPending){status.setText("TOPOLOGY PROBE blocked while another operation is active.");return;}
        testId="cp77-"+UUID.randomUUID();startedMs=System.currentTimeMillis();telemetrySeq=0;remoteTelemetryPosts=0;
        resourceScanDocumentEpoch=documentEpoch;resourceScanPageFinishedEpoch=pageFinishedEpoch;
        resourceSelectedId="-";resourceSelectedKind="-";resourceSelectedHref="";resourceSelectedLocatorCount=0;
        JSONObject start=baseState();put(start,"probe_version",1);put(start,"read_only",true);put(start,"zero_click",true);put(start,"document_epoch",documentEpoch);put(start,"page_finished_epoch",pageFinishedEpoch);put(start,"raw_url_remote",false);put(start,"raw_text_remote",false);put(start,"raw_html_remote",false);
        emit("RESOURCE_TOPOLOGY","RESOURCE_TOPOLOGY_PROBE_STARTED_READ_ONLY",start);
        eval(resourceTopologyProbeV79Js(),o->{
            JSONObject summary=baseState();
            String[] ints={"candidate_count","turn_count","assistant_turn_count","composer_boundary_count","resource_wrapper_candidate_count","excluded_root_candidate_count","same_origin_count","direct_external_count","prev_is_last_assistant_count","next_turn_absent_count"};
            for(String k:ints)put(summary,k,o.optInt(k,0));
            put(summary,"probe_version",1);put(summary,"read_only",true);put(summary,"zero_click",true);put(summary,"last_assistant_exists",o.optBoolean("last_assistant_exists",false));put(summary,"raw_url_remote",false);put(summary,"raw_text_remote",false);put(summary,"raw_html_remote",false);put(summary,"cookies_tokens_accessed",false);
            if(!o.optBoolean("success",false)){
                emit("PLANNER_FINAL","RESOURCE_TOPOLOGY_PROBE_FAILED_READ_ONLY",summary);status.setText("TOPOLOGY PROBE failed read-only. No action was dispatched.");return;
            }
            if(resourceScanDocumentEpoch!=documentEpoch||resourceScanPageFinishedEpoch!=pageFinishedEpoch||pageFinishedEpoch!=documentEpoch){
                emit("PLANNER_FINAL","RESOURCE_TOPOLOGY_PROBE_STALE_EPOCH_REJECTED",summary);status.setText("TOPOLOGY PROBE stale after page change. Run it again on the current chat.");return;
            }
            org.json.JSONArray arr=o.optJSONArray("candidates");int emitted=0;
            if(arr!=null){for(int i=0;i<arr.length();i++){
                JSONObject c=arr.optJSONObject(i);if(c==null)continue;JSONObject st=baseState();
                String[] cints={"candidate_index","direct_turn_count","direct_assistant_count","prev_turn_index","next_turn_index"};for(String k:cints)put(st,k,c.optInt(k,-1));
                String[] cstr={"relation_last_assistant","relation_composer","prev_role","next_role","href_class","node_sig_hash","tag_sig_hash","role_sig_hash","testid_sig_hash","wrapper_sig_hash","nearest_landmark_sig_hash","lca_last_assistant_sig_hash","lca_composer_sig_hash"};for(String k:cstr)put(st,k,c.optString(k,"-"));
                String[] cbool={"prev_is_last_assistant","has_next_turn","in_nav","in_header","in_aside","in_role_navigation","in_composer","in_form","resource_wrapper_present","same_origin","direct_external","target_blank","external_rel","strong_wrapped_evidence"};for(String k:cbool)put(st,k,c.optBoolean(k,false));
                put(st,"read_only",true);put(st,"zero_click",true);put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);put(st,"cookies_tokens_accessed",false);
                emit("RESOURCE_TOPOLOGY","RESOURCE_TOPOLOGY_CANDIDATE",st);emitted++;
            }}
            put(summary,"candidate_events_emitted",emitted);
            emit("PLANNER_FINAL","PASS_RESOURCE_TOPOLOGY_PROBE_COMPLETE",summary);
            status.setText("TOPOLOGY PROBE complete. candidates="+o.optInt("candidate_count",0)+". No Resource action was dispatched.");
        });
    }

'''
s=s[:start]+run_probe+s[end:]

# Disable Resource action admission entirely in the diagnostic build. This is an
# explicit terminal classification, not a no-op that could be mistaken for success.
start=s.index('    private void runResourceActionV79(){\n')
end=s.index('    private String resourceResolverV4Js(){\n',start)
run_disabled=r'''    private void runResourceActionV79(){
        JSONObject st=baseState();put(st,"diagnostic_only",true);put(st,"resource_action_authorized",false);put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);
        emit("PLANNER_FINAL","RESOURCE_ACTION_DISABLED_DIAGNOSTIC_BUILD",st);
        status.setText("ACTION DISABLED in v0.77 diagnostic build. Run TOPOLOGY PROBE only.");
    }

'''
s=s[:start]+run_disabled+s[end:]

# Insert a dedicated zero-click topology reader immediately before the existing
# v0.76 resolver. It deliberately does not use geometry, coordinates, XPath,
# elementFromPoint, innerText/textContent, or raw href output.
insert=s.index('    private String resourceResolverV4Js(){\n')
topology=r'''    private String resourceTopologyProbeV79Js(){
        return "(function(){try{"+
            "const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const H=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return ('00000000'+(h>>>0).toString(16)).slice(-8);};"+
            "const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const s=getComputedStyle(e);if(s.display==='none'||s.visibility==='hidden')return false;try{if(typeof e.checkVisibility==='function')return e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});}catch(_){}return true;};"+
            "const before=(a,b)=>!!(a&&b&&(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING));"+
            "const S=e=>e?H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||'')].join('|'))):'-';"+
            "const AH=e=>N([e&&e.getAttribute?e.getAttribute('role')||'':'',e&&e.getAttribute?e.getAttribute('aria-label')||'':'',e&&e.getAttribute?e.getAttribute('title')||'':'',e&&e.getAttribute?e.getAttribute('data-testid')||'':'',e&&e.getAttribute?e.getAttribute('name')||'':'',e&&e.getAttribute?e.getAttribute('target')||'':'',e&&e.getAttribute?e.getAttribute('rel')||'':''].join(' '));"+
            "const turnNodes=[];const seen=new Set();const addTurn=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);turnNodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(addTurn);const turns=turnNodes.map((e,i)=>{const r=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');return{el:e,role:r?String(r.getAttribute('data-message-author-role')||'-'):'-',index:i};});"+
            "const assistants=turns.filter(t=>t.role==='assistant');const lastAssistant=assistants.length?assistants[assistants.length-1]:null;"+
            "const isComposerRoot=e=>{if(!V(e))return false;const dt=N(e.getAttribute('data-testid')||'');if(dt.includes('composer'))return true;if((e.tagName||'').toLowerCase()==='form')return !!e.querySelector('textarea,[contenteditable=true]');return false;};"+
            "const roots=Array.from(document.querySelectorAll(`form,[data-testid*='composer']`)).filter(isComposerRoot);let composerBoundary=null;if(lastAssistant){for(const r of roots){if(before(lastAssistant.el,r)&&(!composerBoundary||before(r,composerBoundary)))composerBoundary=r;}}if(!composerBoundary&&roots.length===1)composerBoundary=roots[0];"+
            "const wrapper=e=>e.closest&&e.closest(`[data-testid*='citation'],[data-testid*='source'],[data-testid*='resource'],[data-testid*='file'],[data-testid*='download'],[data-testid*='attachment']`);"+
            "const landmark=e=>{for(let p=e&&e.parentElement;p;p=p.parentElement){const tag=N(p.tagName||''),role=N(p.getAttribute('role')||''),dt=N(p.getAttribute('data-testid')||'');if(['main','section','article','nav','aside','header','footer','form'].includes(tag)||role||dt)return S(p);}return '-';};"+
            "const lca=(a,b)=>{if(!a||!b)return '-';const set=new Set();for(let p=a;p;p=p.parentElement)set.add(p);for(let q=b;q;q=q.parentElement)if(set.has(q))return S(q);return '-';};"+
            "const relLast=e=>{if(!lastAssistant)return 'NO_LAST_ASSISTANT';if(lastAssistant.el.contains(e))return 'INSIDE_LAST_ASSISTANT';if(e.contains(lastAssistant.el))return 'CONTAINS_LAST_ASSISTANT';if(before(lastAssistant.el,e))return 'AFTER_LAST_ASSISTANT';if(before(e,lastAssistant.el))return 'BEFORE_LAST_ASSISTANT';return 'NEITHER_OR_DISCONNECTED';};"+
            "const relComposer=e=>{if(!composerBoundary)return 'NO_COMPOSER_BOUNDARY';if(composerBoundary.contains(e))return 'INSIDE_COMPOSER';if(e.contains(composerBoundary))return 'CONTAINS_COMPOSER';if(before(e,composerBoundary))return 'BEFORE_COMPOSER';if(before(composerBoundary,e))return 'AFTER_COMPOSER';return 'NEITHER_OR_DISCONNECTED';};"+
            "const nodes=[];document.querySelectorAll('a[href],[role=link],[download]').forEach(e=>{if(V(e)&&nodes.indexOf(e)<0)nodes.push(e);});"+
            "const out=[];let wrapperCount=0,excludedCount=0,sameCount=0,externalCount=0,prevLastCount=0,nextAbsentCount=0;"+
            "for(let i=0;i<nodes.length;i++){const e=nodes[i];const direct=turns.filter(t=>t.el.contains(e));let prev=null,next=null;for(const t of turns){if(t.el.contains(e))continue;if(before(t.el,e))prev=t;else if(!next&&before(e,t.el))next=t;}const w=wrapper(e);if(w)wrapperCount++;const inNav=!!(e.closest&&e.closest('nav')),inHeader=!!(e.closest&&e.closest('header')),inAside=!!(e.closest&&e.closest('aside')),inRoleNav=!!(e.closest&&e.closest('[role=navigation]')),inForm=!!(e.closest&&e.closest('form')),inComposer=!!(e.closest&&e.closest(`[data-testid*='composer']`));if(inNav||inHeader||inAside||inRoleNav||inForm||inComposer)excludedCount++;const prevIsLast=!!(prev&&lastAssistant&&prev.el===lastAssistant.el);if(prevIsLast)prevLastCount++;if(!next)nextAbsentCount++;let href=e.getAttribute('href')||'';try{if(!href&&typeof e.href==='string')href=e.href;}catch(_){}let hrefClass='NONE',same=false,external=false;try{if(href.startsWith('blob:'))hrefClass='BLOB';else if(href.startsWith('data:'))hrefClass='DATA';else{const u=new URL(href,location.href);if(u.protocol==='http:'||u.protocol==='https:'){same=u.origin===location.origin;external=!same;hrefClass=same?'HTTP_SAME_ORIGIN':'HTTP_EXTERNAL';}else hrefClass='OTHER_SCHEME';}}catch(_){hrefClass='UNPARSEABLE';}if(same)sameCount++;if(external)externalCount++;const targetBlank=N(e.getAttribute('target')||'')==='_blank';const externalRel=/noopener|noreferrer|external/.test(N(e.getAttribute('rel')||''));const semanticAttr=/citation|source|reference|resource|redirect|outbound|external/.test(AH(e));const strongWrapped=!!w||targetBlank||externalRel||semanticAttr;out.push({candidate_index:i,direct_turn_count:direct.length,direct_assistant_count:direct.filter(t=>t.role==='assistant').length,prev_turn_index:prev?prev.index:-1,next_turn_index:next?next.index:-1,relation_last_assistant:relLast(e),relation_composer:relComposer(e),prev_role:prev?prev.role:'NONE',next_role:next?next.role:'NONE',prev_is_last_assistant:prevIsLast,has_next_turn:!!next,in_nav:inNav,in_header:inHeader,in_aside:inAside,in_role_navigation:inRoleNav,in_composer:inComposer,in_form:inForm,resource_wrapper_present:!!w,same_origin:same,direct_external:external,target_blank:targetBlank,external_rel:externalRel,strong_wrapped_evidence:strongWrapped,href_class:hrefClass,node_sig_hash:S(e),tag_sig_hash:H(N(e.tagName||'')),role_sig_hash:H(N(e.getAttribute('role')||'')),testid_sig_hash:H(N(e.getAttribute('data-testid')||'')),wrapper_sig_hash:w?S(w):'-',nearest_landmark_sig_hash:landmark(e),lca_last_assistant_sig_hash:lastAssistant?lca(e,lastAssistant.el):'-',lca_composer_sig_hash:composerBoundary?lca(e,composerBoundary):'-'});}"+
            "return JSON.stringify({success:true,candidate_count:out.length,turn_count:turns.length,assistant_turn_count:assistants.length,composer_boundary_count:composerBoundary?1:0,last_assistant_exists:!!lastAssistant,resource_wrapper_candidate_count:wrapperCount,excluded_root_candidate_count:excludedCount,same_origin_count:sameCount,direct_external_count:externalCount,prev_is_last_assistant_count:prevLastCount,next_turn_absent_count:nextAbsentCount,candidates:out});"+
        "}catch(e){return JSON.stringify({success:false,error_class:'RESOURCE_TOPOLOGY_PROBE_EXCEPTION'});}})()";
    }

'''
s=s[:insert]+topology+s[insert:]

# Write renamed activity and telemetry config.
ACT.write_text(s);OLD.unlink()
old_cfg=PKG/"TelemetryConfigV78.java";new_cfg=PKG/"TelemetryConfigV79.java"
cfg=old_cfg.read_text().replace("TelemetryConfigV78","TelemetryConfigV79")
new_cfg.write_text(cfg);old_cfg.unlink()

# Version/package/update continuity.
g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+79\b","versionCode 80",gs);gs=gs.replace("0.76-stable-diag-resource-final-bounded-wrapped","0.77-stable-diag-resource-topology-probe");g.write_text(gs)
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorResourceToolsV78Activity","OrchestratorResourceToolsV79Activity");mf.write_text(ms)

# Diagnostic-only safety and regression gates.
out=ACT.read_text()
for required in [
    'TOPOLOGY PROBE','ACTION DISABLED','RESOURCE_TOPOLOGY_PROBE_STARTED_READ_ONLY','RESOURCE_TOPOLOGY_CANDIDATE',
    'PASS_RESOURCE_TOPOLOGY_PROBE_COMPLETE','RESOURCE_ACTION_DISABLED_DIAGNOSTIC_BUILD','resourceTopologyProbeV79Js',
    'relation_last_assistant','relation_composer','prev_is_last_assistant','resource_wrapper_present','nearest_landmark_sig_hash',
    'lca_last_assistant_sig_hash','lca_composer_sig_hash','strong_wrapped_evidence','TelemetryConfigV79',
    'PASS_TOOLS_HIDDEN_MENU_CENSUS_COMPLETE'
]: assert required in out,required
probe=out[out.index('private String resourceTopologyProbeV79Js'):out.index('private String resourceResolverV4Js')]
action=out[out.index('private void runResourceActionV79'):out.index('private String resourceResolverV4Js')]
for forbidden in ['getBoundingClientRect','elementFromPoint','document.evaluate','XPathResult','innerText','textContent','setTimeout(','setInterval(']: assert forbidden not in probe,forbidden
for forbidden in ['startActivity(','.click();','resourceNavigationPending=true','resourceDownloadPending=true']:
    assert forbidden not in action,forbidden
assert 'raw_url_remote",false' in out and 'raw_text_remote",false' in out and 'raw_html_remote",false' in out
assert "versionCode 80" in g.read_text()
assert "versionName '0.77-stable-diag-resource-topology-probe'" in g.read_text()
assert "OrchestratorResourceToolsV79Activity" in mf.read_text()
print("PASS v0.77: zero-click sanitized Resource topology probe; Resource action disabled")
