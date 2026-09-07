#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# v0.78: evidence-first assistant-local interaction-surface diagnostic.
# No Resource action is authorized. Start from the final assistant turn and
# inventory plausible interactive descendants using sanitized structural/style
# signals only. Also collapse the test chrome to one attached button row.
runpy.run_path("ci/generate_chatgpt_webview_v79_resource_topology_probe.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorResourceToolsV79Activity.java"
ACT=PKG/"OrchestratorResourceToolsV80Activity.java"
s=OLD.read_text()

s=s.replace("OrchestratorResourceToolsV79Activity","OrchestratorResourceToolsV80Activity")
s=s.replace("TelemetryConfigV79","TelemetryConfigV80")
s=s.replace("runResourceActionV79","runResourceActionV80")
s=s.replace("resourceTopologyProbeV79Js","resourceTopologyProbeV80Js")
s=s.replace('SCHEMA="cp-v79-resource-topology-probe-v1"','SCHEMA="cp-v80-assistant-local-interaction-probe-v1"')
s=s.replace('SCENARIO="resource-topology-read-only"','SCENARIO="assistant-local-interaction-surface-read-only"')
s=s.replace('getSharedPreferences("cp_v79_resource_topology_probe",MODE_PRIVATE)','getSharedPreferences("cp_v80_assistant_local_probe",MODE_PRIVATE)')
s=s.replace('data-cp-resource-locator-v79','data-cp-resource-locator-v80')
s=s.replace('__cpResourceResolverV79','__cpResourceResolverV80')
s=s.replace('resource_v79_claim_','resource_v80_claim_')
s=s.replace('v0.77 Read-only Resource topology probe + Tools ready.','v0.78 Assistant-local interaction probe ready.')
s=s.replace('ACTION DISABLED in v0.77 diagnostic build. Run TOPOLOGY PROBE only.','ACTION DISABLED in v0.78 diagnostic build.')

# Minimal diagnostic chrome: detach historical rows 1-4 and replace row5 with
# exactly one attached full-width SCAN ASSISTANT control.
for n in range(1,5):
    s,c=re.subn(rf'^\s*root\.addView\(row{n},.*?\);\s*$', '', s, count=1, flags=re.M)
    assert c==1,("detach row",n,c)
pat=r'        LinearLayout row5=new LinearLayout\(this\);.*?        root\.addView\(row5,new LinearLayout\.LayoutParams\(LinearLayout\.LayoutParams\.MATCH_PARENT,dp\(42\)\)\);\n'
m=re.search(pat,s,re.S); assert m,"row5 block"
mini='''        LinearLayout row5=new LinearLayout(this); row5.setOrientation(LinearLayout.HORIZONTAL);
        Button assistantProbe=new Button(this); assistantProbe.setText("SCAN ASSISTANT"); assistantProbe.setOnClickListener(v->runResourceTest());
        row5.addView(assistantProbe,new LinearLayout.LayoutParams(0,dp(42),1f));
        root.addView(row5,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(42)));
'''
s=s[:m.start()]+mini+s[m.end():]

# Replace the v0.77 topology test with the approved assistant-local probe.
start=s.index('    private void runResourceTest(){\n')
end=s.index('    private void runResourceActionV80(){\n',start)
run_probe=r'''    private void runResourceTest(){
        if(learning||plannerRunning||toolsTestRunning||resourceDownloadPending||resourceNavigationPending){status.setText("SCAN ASSISTANT blocked while another operation is active.");return;}
        testId="cp78-"+UUID.randomUUID();startedMs=System.currentTimeMillis();telemetrySeq=0;remoteTelemetryPosts=0;
        resourceScanDocumentEpoch=documentEpoch;resourceScanPageFinishedEpoch=pageFinishedEpoch;
        resourceSelectedId="-";resourceSelectedKind="-";resourceSelectedHref="";resourceSelectedLocatorCount=0;
        JSONObject st0=baseState();put(st0,"probe_version",1);put(st0,"read_only",true);put(st0,"zero_click",true);put(st0,"raw_url_remote",false);put(st0,"raw_text_remote",false);put(st0,"raw_html_remote",false);
        emit("RESOURCE_DISCOVERY","ASSISTANT_LOCAL_PROBE_STARTED_READ_ONLY",st0);
        eval(assistantLocalInteractionProbeV80Js(),o->{
            JSONObject summary=baseState();
            String[] ints={"turn_count","assistant_turn_count","assistant_descendant_count","plausible_candidate_count","emitted_candidate_count","truncated_candidate_count","inside_author_message_count","href_present_count","pointer_count","underline_count","onclick_count","tabindex_count","semantic_role_count","semantic_metadata_count","resource_wrapper_count","ancestor_interactive_count"};
            for(String k:ints)put(summary,k,o.optInt(k,0));
            put(summary,"probe_version",1);put(summary,"read_only",true);put(summary,"zero_click",true);put(summary,"last_assistant_exists",o.optBoolean("last_assistant_exists",false));put(summary,"author_message_exists",o.optBoolean("author_message_exists",false));put(summary,"raw_url_remote",false);put(summary,"raw_text_remote",false);put(summary,"raw_html_remote",false);put(summary,"cookies_tokens_accessed",false);
            if(!o.optBoolean("success",false)){emit("PLANNER_FINAL","ASSISTANT_LOCAL_PROBE_FAILED_READ_ONLY",summary);status.setText("SCAN ASSISTANT failed read-only. No action dispatched.");return;}
            if(resourceScanDocumentEpoch!=documentEpoch||resourceScanPageFinishedEpoch!=pageFinishedEpoch||pageFinishedEpoch!=documentEpoch){emit("PLANNER_FINAL","ASSISTANT_LOCAL_PROBE_STALE_EPOCH_REJECTED",summary);status.setText("SCAN ASSISTANT stale after page change. Run it again.");return;}
            org.json.JSONArray arr=o.optJSONArray("candidates");int emitted=0;
            if(arr!=null){for(int i=0;i<arr.length();i++){
                JSONObject c=arr.optJSONObject(i);if(c==null)continue;JSONObject st=baseState();
                String[] cints={"candidate_rank","candidate_doc_index","score","depth_from_turn","descendant_anchor_count","descendant_button_count"};for(String k:cints)put(st,k,c.optInt(k,-1));
                String[] cstr={"surface_kind","href_class","node_sig_hash","tag_sig_hash","role_sig_hash","testid_sig_hash","class_sig_hash","parent_sig_hash","nearest_interactive_ancestor_sig_hash","wrapper_sig_hash"};for(String k:cstr)put(st,k,c.optString(k,"-"));
                String[] cbool={"inside_author_message","direct_child_of_author_message","tag_anchor","tag_button","semantic_role","href_present","same_origin","direct_external","tabindex_present","tabindex_nonnegative","disabled","target_blank","external_rel","onclick_property","onclick_attribute","cursor_pointer","underline_present","semantic_metadata","aria_label_present","aria_controls_present","aria_owns_present","aria_describedby_present","title_present","name_present","testid_present","resource_wrapper_present","ancestor_interactive_present"};for(String k:cbool)put(st,k,c.optBoolean(k,false));
                put(st,"read_only",true);put(st,"zero_click",true);put(st,"raw_url_remote",false);put(st,"raw_text_remote",false);put(st,"raw_html_remote",false);put(st,"cookies_tokens_accessed",false);
                emit("RESOURCE_DISCOVERY","ASSISTANT_LOCAL_INTERACTION_CANDIDATE",st);emitted++;
            }}
            put(summary,"candidate_events_emitted",emitted);
            emit("PLANNER_FINAL","PASS_ASSISTANT_LOCAL_INTERACTION_PROBE_COMPLETE",summary);
            status.setText("SCAN ASSISTANT complete. plausible="+o.optInt("plausible_candidate_count",0)+" emitted="+emitted+". No action dispatched.");
        });
    }

'''
s=s[:start]+run_probe+s[end:]

# Insert the new probe before the dormant v0.77 topology reader.
insert=s.index('    private String resourceTopologyProbeV80Js(){\n')
probe=r'''    private String assistantLocalInteractionProbeV80Js(){
        return "(function(){try{"+
            "const N=s=>(s||'').toString().replace(/\\s+/g,' ').trim().toLowerCase();"+
            "const H=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return ('00000000'+(h>>>0).toString(16)).slice(-8);};"+
            "const V=e=>{if(!e||!e.isConnected||e.getAttribute('aria-hidden')==='true')return false;const s=getComputedStyle(e);if(s.display==='none'||s.visibility==='hidden'||s.opacity==='0')return false;try{if(typeof e.checkVisibility==='function')return e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});}catch(_){}return true;};"+
            "const SIG=e=>e?H(N([(e.tagName||''),(e.getAttribute('role')||''),(e.getAttribute('data-testid')||''),String(e.className||'')].join('|'))):'-';"+
            "const turnNodes=[];const seen=new Set();const addTurn=e=>{const t=(e.closest&&e.closest(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-']`))||e;if(t&&!seen.has(t)){seen.add(t);turnNodes.push(t);}};document.querySelectorAll(`article[data-testid^='conversation-turn-'],[data-testid^='conversation-turn-'],[data-message-author-role]`).forEach(addTurn);const turns=turnNodes.map((e,i)=>{const r=(e.matches&&e.matches('[data-message-author-role]'))?e:e.querySelector('[data-message-author-role]');return{el:e,role:r?String(r.getAttribute('data-message-author-role')||'-'):'-',index:i};});"+
            "const assistants=turns.filter(t=>t.role==='assistant');const last=assistants.length?assistants[assistants.length-1]:null;if(!last)return JSON.stringify({success:true,last_assistant_exists:false,author_message_exists:false,turn_count:turns.length,assistant_turn_count:assistants.length,assistant_descendant_count:0,plausible_candidate_count:0,emitted_candidate_count:0,truncated_candidate_count:0,candidates:[]});"+
            "const author=(last.el.matches&&last.el.matches('[data-message-author-role=assistant]'))?last.el:last.el.querySelector('[data-message-author-role=assistant]');const root=last.el;const all=Array.from(root.querySelectorAll('*'));"+
            "const wrap=e=>e.closest&&e.closest(`[data-testid*='citation'],[data-testid*='source'],[data-testid*='resource'],[data-testid*='reference'],[data-testid*='file'],[data-testid*='download'],[data-testid*='attachment']`);"+
            "const hrefInfo=e=>{let h='';try{h=e.getAttribute('href')||((typeof e.href==='string')?e.href:'');}catch(_){}if(!h)return{present:false,cls:'NONE',same:false,external:false};try{if(h.startsWith('blob:'))return{present:true,cls:'BLOB',same:false,external:false};if(h.startsWith('data:'))return{present:true,cls:'DATA',same:false,external:false};const u=new URL(h,location.href);if(u.protocol==='http:'||u.protocol==='https:'){const same=u.origin===location.origin;return{present:true,cls:same?'HTTP_SAME_ORIGIN':'HTTP_EXTERNAL',same:same,external:!same};}return{present:true,cls:'OTHER_SCHEME',same:false,external:false};}catch(_){return{present:true,cls:'UNPARSEABLE',same:false,external:false};}};"+
            "const isInt=e=>{if(!e)return false;const tag=N(e.tagName||''),role=N(e.getAttribute('role')||''),dt=N(e.getAttribute('data-testid')||''),aria=N(e.getAttribute('aria-label')||''),title=N(e.getAttribute('title')||''),name=N(e.getAttribute('name')||'');const st=getComputedStyle(e);const semRole=/^(link|button|menuitem|option|tab|checkbox|switch)$/.test(role);const semMeta=/link|button|citation|source|resource|reference|external|open|url|action|copy|share|feedback|retry/.test([dt,aria,title,name].join(' '));const tab=e.hasAttribute('tabindex');const on=typeof e.onclick==='function'||e.hasAttribute('onclick');const ptr=N(st.cursor||'').includes('pointer');const und=N(st.textDecorationLine||st.textDecoration||'').includes('underline');return tag==='a'||tag==='button'||semRole||tab||on||ptr||und||semMeta;};"+
            "const nearestIntAncestor=e=>{for(let p=e.parentElement;p&&p!==root;p=p.parentElement)if(isInt(p))return p;return null;};"+
            "const depth=e=>{let d=0,p=e;while(p&&p!==root){d++;p=p.parentElement;}return d;};"+
            "const rows=[];let hrefCount=0,pointerCount=0,underlineCount=0,onclickCount=0,tabCount=0,roleCount=0,metaCount=0,wrapperCount=0,insideAuthorCount=0,ancestorCount=0;"+
            "all.forEach((e,di)=>{if(!V(e)||!isInt(e))return;const tag=N(e.tagName||''),role=N(e.getAttribute('role')||''),dt=N(e.getAttribute('data-testid')||''),aria=N(e.getAttribute('aria-label')||''),title=N(e.getAttribute('title')||''),name=N(e.getAttribute('name')||'');const st=getComputedStyle(e),hi=hrefInfo(e),semRole=/^(link|button|menuitem|option|tab|checkbox|switch)$/.test(role),semMeta=/link|button|citation|source|resource|reference|external|open|url|action|copy|share|feedback|retry/.test([dt,aria,title,name].join(' ')),tab=e.hasAttribute('tabindex'),tabN=tab&&!Number.isNaN(parseInt(e.getAttribute('tabindex')||'',10))&&parseInt(e.getAttribute('tabindex')||'',10)>=0,onProp=typeof e.onclick==='function',onAttr=e.hasAttribute('onclick'),ptr=N(st.cursor||'').includes('pointer'),und=N(st.textDecorationLine||st.textDecoration||'').includes('underline'),w=wrap(e),inside=!!(author&&author.contains(e)),nia=nearestIntAncestor(e);if(hi.present)hrefCount++;if(ptr)pointerCount++;if(und)underlineCount++;if(onProp||onAttr)onclickCount++;if(tab)tabCount++;if(semRole)roleCount++;if(semMeta)metaCount++;if(w)wrapperCount++;if(inside)insideAuthorCount++;if(nia)ancestorCount++;let score=(inside?8:0)+(hi.present?8:0)+(tag==='a'?6:0)+(tag==='button'?5:0)+(role==='link'?6:(semRole?4:0))+(ptr?4:0)+(und?4:0)+((onProp||onAttr)?4:0)+(tabN?3:0)+(semMeta?3:0)+(w?5:0)+(nia?2:0);let kind='METADATA';if(tag==='a'||hi.present)kind='ANCHOR_OR_HREF';else if(tag==='button')kind='BUTTON';else if(role==='link')kind='ROLE_LINK';else if(semRole)kind='SEMANTIC_ROLE';else if(onProp||onAttr)kind='ONCLICK';else if(ptr&&und)kind='POINTER_UNDERLINE';else if(ptr)kind='POINTER';else if(und)kind='UNDERLINE';else if(tab)kind='TABINDEX';rows.push({candidate_doc_index:di,score:score,surface_kind:kind,depth_from_turn:depth(e),inside_author_message:inside,direct_child_of_author_message:!!(author&&e.parentElement===author),tag_anchor:tag==='a',tag_button:tag==='button',semantic_role:semRole,href_present:hi.present,href_class:hi.cls,same_origin:hi.same,direct_external:hi.external,tabindex_present:tab,tabindex_nonnegative:tabN,disabled:e.hasAttribute('disabled')||e.getAttribute('aria-disabled')==='true',target_blank:N(e.getAttribute('target')||'')==='_blank',external_rel:/noopener|noreferrer|external/.test(N(e.getAttribute('rel')||'')),onclick_property:onProp,onclick_attribute:onAttr,cursor_pointer:ptr,underline_present:und,semantic_metadata:semMeta,aria_label_present:e.hasAttribute('aria-label'),aria_controls_present:e.hasAttribute('aria-controls'),aria_owns_present:e.hasAttribute('aria-owns'),aria_describedby_present:e.hasAttribute('aria-describedby'),title_present:e.hasAttribute('title'),name_present:e.hasAttribute('name'),testid_present:e.hasAttribute('data-testid'),resource_wrapper_present:!!w,ancestor_interactive_present:!!nia,descendant_anchor_count:e.querySelectorAll?e.querySelectorAll('a').length:0,descendant_button_count:e.querySelectorAll?e.querySelectorAll('button').length:0,node_sig_hash:SIG(e),tag_sig_hash:H(tag),role_sig_hash:H(role),testid_sig_hash:H(dt),class_sig_hash:H(N(String(e.className||''))),parent_sig_hash:SIG(e.parentElement),nearest_interactive_ancestor_sig_hash:nia?SIG(nia):'-',wrapper_sig_hash:w?SIG(w):'-'});});"+
            "rows.sort((a,b)=>b.score-a.score||a.candidate_doc_index-b.candidate_doc_index);const total=rows.length,limit=24,emit=rows.slice(0,limit);emit.forEach((x,i)=>x.candidate_rank=i);return JSON.stringify({success:true,last_assistant_exists:true,author_message_exists:!!author,turn_count:turns.length,assistant_turn_count:assistants.length,assistant_descendant_count:all.length,plausible_candidate_count:total,emitted_candidate_count:emit.length,truncated_candidate_count:Math.max(0,total-emit.length),inside_author_message_count:insideAuthorCount,href_present_count:hrefCount,pointer_count:pointerCount,underline_count:underlineCount,onclick_count:onclickCount,tabindex_count:tabCount,semantic_role_count:roleCount,semantic_metadata_count:metaCount,resource_wrapper_count:wrapperCount,ancestor_interactive_count:ancestorCount,candidates:emit});"+
        "}catch(e){return JSON.stringify({success:false,error_class:'ASSISTANT_LOCAL_PROBE_EXCEPTION'});}})()";
    }

'''
s=s[:insert]+probe+s[insert:]

ACT.write_text(s);OLD.unlink()
old_cfg=PKG/"TelemetryConfigV79.java";new_cfg=PKG/"TelemetryConfigV80.java"
cfg=old_cfg.read_text().replace("TelemetryConfigV79","TelemetryConfigV80")
new_cfg.write_text(cfg);old_cfg.unlink()

g=ROOT/"app/build.gradle";gs=g.read_text();gs=re.sub(r"versionCode\s+80\b","versionCode 81",gs);gs=gs.replace("0.77-stable-diag-resource-topology-probe","0.78-stable-diag-assistant-local-interaction-probe");g.write_text(gs)
mf=ROOT/"app/src/main/AndroidManifest.xml";ms=mf.read_text().replace("OrchestratorResourceToolsV79Activity","OrchestratorResourceToolsV80Activity");mf.write_text(ms)

out=ACT.read_text()
for required in ['SCAN ASSISTANT','ASSISTANT_LOCAL_PROBE_STARTED_READ_ONLY','ASSISTANT_LOCAL_INTERACTION_CANDIDATE','PASS_ASSISTANT_LOCAL_INTERACTION_PROBE_COMPLETE','assistantLocalInteractionProbeV80Js','inside_author_message','cursor_pointer','underline_present','ancestor_interactive_present','TelemetryConfigV80','RESOURCE_ACTION_DISABLED_DIAGNOSTIC_BUILD']:
    assert required in out,required
for n in range(1,5): assert f'root.addView(row{n}' not in out,n
assert out.count('root.addView(row5')==1,out.count('root.addView(row5')
assert 'setOnClickListener(v->runResourceActionV80())' not in out
p=out[out.index('private String assistantLocalInteractionProbeV80Js'):out.index('private String resourceTopologyProbeV80Js')]
for bad in ['getBoundingClientRect','elementFromPoint','document.evaluate','XPathResult','innerText','textContent','setTimeout(','setInterval(']: assert bad not in p,bad
a=out[out.index('private void runResourceActionV80'):out.index('private String assistantLocalInteractionProbeV80Js')]
for bad in ['startActivity(','.click();','resourceNavigationPending=true','resourceDownloadPending=true']: assert bad not in a,bad
assert 'raw_url_remote",false' in out and 'raw_text_remote",false' in out and 'raw_html_remote",false' in out
assert "versionCode 81" in g.read_text()
assert "versionName '0.78-stable-diag-assistant-local-interaction-probe'" in g.read_text()
assert "OrchestratorResourceToolsV80Activity" in mf.read_text()
print("PASS v0.78: minimal one-button zero-click assistant-local interaction probe")
