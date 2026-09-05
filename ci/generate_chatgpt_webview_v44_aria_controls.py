#!/usr/bin/env python3
from pathlib import Path
import json
import re
import runpy

# Reuse the already-verified v0.41 generator as the exact base, then narrow the
# next diagnostic around one falsifiable hypothesis: the open THINKING button's
# aria-controls target is the secondary effort surface.
runpy.run_path('ci/generate_chatgpt_webview_v43_nested.py', run_name='__main__')

ROOT = Path('runtime_probes/chatgpt-webview-stable-probe')
PKG = ROOT / 'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
src43 = PKG / 'OrchestratorPaidModelEffortNestedCensusV43Activity.java'
src44 = PKG / 'OrchestratorPaidModelEffortAriaControlsCensusV44Activity.java'
man = ROOT / 'app/src/main/AndroidManifest.xml'
gradle = ROOT / 'app/build.gradle'

s = src43.read_text()
s = s.replace('OrchestratorPaidModelEffortNestedCensusV43Activity', 'OrchestratorPaidModelEffortAriaControlsCensusV44Activity')
s = s.replace('TelemetryConfigV43', 'TelemetryConfigV44')
s = s.replace('43', '44')
s = s.replace('cp-v44-paid-model-effort-nested-surface-census-v1', 'cp-v44-paid-model-effort-aria-controls-target-census-v1')
s = s.replace('paid-model-effort-open-popup-nested-structure-census', 'paid-model-effort-aria-controls-target-census')
s = s.replace('RUN NESTED EFFORT SURFACE CENSUS', 'RUN ARIA-CONTROLS TARGET CENSUS')
s = s.replace('NESTED CENSUS RUNNING...', 'ARIA TARGET CENSUS RUNNING...')
s = s.replace('Nested snapshot ', 'Relation-target snapshot ')
s = s.replace('NESTED_SURFACE_SNAPSHOT', 'ARIA_CONTROLS_TARGET_SNAPSHOT')
s = s.replace('v0.40 semantic pointer popup census ready — no model option click', 'v0.42 aria-controls target census ready — zero model option clicks')
s = s.replace('PASS_NESTED_EFFORT_STRUCTURE_CENSUS_CAPTURED', 'PASS_ARIA_CONTROLS_TARGET_CENSUS_CAPTURED')
s = s.replace('PARTIAL_NESTED_EFFORT_STRUCTURE_CENSUS_CAPTURED', 'PARTIAL_ARIA_CONTROLS_TARGET_CENSUS_CAPTURED')
s = s.replace('NESTED_EFFORT_STRUCTURE_UNCERTAIN_NO_REPLAY', 'ARIA_CONTROLS_TARGET_UNCERTAIN_NO_REPLAY')

field_anchor = '    private int popupEvidenceSnapshots44 = 0;\n'
assert field_anchor in s
s = s.replace(field_anchor, field_anchor + '    private int resolvedTargetSnapshots44 = 0;\n    private int targetEffortOptionSnapshots44 = 0;\n')
reset_anchor = '        popupEvidenceSnapshots44 = 0;\n'
assert reset_anchor in s
s = s.replace(reset_anchor, reset_anchor + '        resolvedTargetSnapshots44 = 0;\n        targetEffortOptionSnapshots44 = 0;\n', 1)

old_final = '''        if (index >= SNAPSHOTS44) {
            if (popupEvidenceSnapshots44 > 0) {
                prefs44.edit().putString("claim_status", "CONFIRMED_POPUP_EVIDENCE").commit();
                claimStatus44 = "CONFIRMED_POPUP_EVIDENCE";
                finish44(completeSnapshots44 == SNAPSHOTS44
                        ? "PASS_ARIA_CONTROLS_TARGET_CENSUS_CAPTURED"
                        : "PARTIAL_ARIA_CONTROLS_TARGET_CENSUS_CAPTURED");
            } else {
                prefs44.edit().putString("claim_status", "UNCERTAIN_NO_REPLAY").commit();
                claimStatus44 = "UNCERTAIN_NO_REPLAY";
                finish44("ARIA_CONTROLS_TARGET_UNCERTAIN_NO_REPLAY");
            }
            return;
        }'''
new_final = '''        if (index >= SNAPSHOTS44) {
            if (popupEvidenceSnapshots44 > 0) {
                prefs44.edit().putString("claim_status", "CONFIRMED_POPUP_EVIDENCE").commit();
                claimStatus44 = "CONFIRMED_POPUP_EVIDENCE";
                if (completeSnapshots44 == SNAPSHOTS44 && resolvedTargetSnapshots44 == SNAPSHOTS44) {
                    finish44(targetEffortOptionSnapshots44 > 0
                            ? "PASS_ARIA_CONTROLS_TARGET_EXPOSES_LIGHT_HEAVY"
                            : "NEGATIVE_ARIA_CONTROLS_TARGET_RESOLVED_NO_LIGHT_HEAVY");
                } else if (resolvedTargetSnapshots44 > 0) {
                    finish44("PARTIAL_ARIA_CONTROLS_TARGET_RESOLUTION");
                } else {
                    finish44("NEGATIVE_ARIA_CONTROLS_TARGET_UNRESOLVED");
                }
            } else {
                prefs44.edit().putString("claim_status", "UNCERTAIN_NO_REPLAY").commit();
                claimStatus44 = "UNCERTAIN_NO_REPLAY";
                finish44("ARIA_CONTROLS_TARGET_UNCERTAIN_NO_REPLAY");
            }
            return;
        }'''
assert old_final in s
s = s.replace(old_final, new_final)

counter_anchor = '            if (evidence) popupEvidenceSnapshots44++;\n'
assert counter_anchor in s
s = s.replace(counter_anchor, counter_anchor + '''            boolean targetResolved = o.optInt("resolved_target_count", 0) == 1;
            boolean targetHasEffortOption = o.optInt("target_light_count", 0) > 0 || o.optInt("target_heavy_count", 0) > 0;
            if (targetResolved) resolvedTargetSnapshots44++;
            if (targetHasEffortOption) targetEffortOptionSnapshots44++;
''', 1)

old_copy = 'copy44(st, o, "success","complete","snapshot_index","visited_nodes","semantic_candidate_count","light_count","medium_count","heavy_count","auto_count","thinking_count","instant_count","selected_count","hidden_semantic_count","relation_ref_node_count","trigger_found","trigger_expanded_true","trigger_data_state_open","popup_role_candidate_count","portalish_candidate_count","popup_evidence","candidate_set_hash","ancestor_set_hash");'
new_copy = 'copy44(st, o, "success","complete","snapshot_index","owner_count","owner_controls_hash","controls_ref_count","resolved_target_count","target_root_role","target_root_visible","target_root_open","target_descendant_count","target_interactive_count","target_semantic_count","target_visible_semantic_count","target_hidden_semantic_count","target_light_count","target_medium_count","target_heavy_count","target_auto_count","target_thinking_count","target_instant_count","target_selected_count","target_menu_count","target_listbox_count","target_group_count","target_menuitem_count","target_menuitemradio_count","target_option_count","target_radio_count","target_button_count","target_presentation_count","target_has_light_heavy","popup_evidence","target_candidate_set_hash");'
assert old_copy in s
s = s.replace(old_copy, new_copy)

phase_old = 'phase44("ARIA_CONTROLS_TARGET_SNAPSHOT", complete ? "CAPTURED_COMPLETE" : "CAPTURED_BUDGET_LIMIT", st);'
phase_new = 'phase44("ARIA_CONTROLS_TARGET_SNAPSHOT", complete ? (targetResolved ? "CAPTURED_TARGET_RESOLVED" : "CAPTURED_TARGET_UNRESOLVED") : "CAPTURED_BUDGET_LIMIT", st);'
assert phase_old in s
s = s.replace(phase_old, phase_new)

finish_anchor = '        put44(st,"popup_evidence_snapshots",popupEvidenceSnapshots44);\n'
assert finish_anchor in s
s = s.replace(finish_anchor, finish_anchor + '        put44(st,"resolved_target_snapshots",resolvedTargetSnapshots44);\n        put44(st,"target_effort_option_snapshots",targetEffortOptionSnapshots44);\n', 1)

js = r'''(function(){try{const IDX=__IDX__,BH='__BH__',T0=performance.now(),MAXN=12000,MAXMS=300,MAXC=64;const N=x=>(x||'').replace(/\s+/g,' ').trim(),L=x=>N(x).toLowerCase(),TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean),H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);},V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}},SEM=s=>{const t=TOK(s),w=[['LIGHT','light'],['MEDIUM','medium'],['HEAVY','heavy'],['AUTO','auto'],['THINKING','thinking'],['INSTANT','instant']],m=w.filter(x=>t.includes(x[1]));return m.length===1?m[0][0]:'NONE';},ROLE=e=>L(e.getAttribute('role'))||((e.tagName||'').toLowerCase()),OPEN=e=>{const ds=L(e.getAttribute('data-state')),ex=L(e.getAttribute('aria-expanded'));return ex==='true'||ds==='open'||ds==='expanded';};let input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=true],[role=textbox]'))if(V(e)){input=e;break;}let composer=null;if(input){let p=input.parentElement;for(let d=0;p&&d<10;d++,p=p.parentElement){if(p.querySelectorAll('button,[role=button]').length>=3){composer=p;break;}}}const owners=[];if(composer)for(const e of composer.querySelectorAll('button,[role=button]')){if(!V(e))continue;const acc=N(e.getAttribute('aria-label')||e.getAttribute('title')||e.innerText||e.textContent||''),sem=SEM(acc),popup=N(e.getAttribute('aria-haspopup')),expanded=L(e.getAttribute('aria-expanded')),controls=N(e.getAttribute('aria-controls'));if(sem==='THINKING'&&expanded==='true'&&popup!==''&&L(popup)!=='false'&&controls!=='')owners.push(e);}let controls='',refs=[],targets=[];if(owners.length===1){controls=N(owners[0].getAttribute('aria-controls'));refs=controls.split(/\s+/).filter(Boolean).slice(0,8);for(const id of refs){let t=null;try{t=document.getElementById(id);}catch(_){}if(t&&t.isConnected&&!targets.includes(t))targets.push(t);}}let complete=true,visited=0,desc=0,interactive=0,semCount=0,visibleSem=0,hiddenSem=0,lc=0,mc=0,hc=0,ac=0,tc=0,ic=0,selected=0,menu=0,listbox=0,group=0,menuitem=0,menuitemradio=0,option=0,radio=0,button=0,presentation=0,targetRole='-',targetVisible=false,targetOpen=false;const out=[],fps=[];if(targets.length===1){const root=targets[0];targetRole=ROLE(root);targetVisible=V(root);targetOpen=OPEN(root);const nodes=[root,...root.querySelectorAll('*')];for(const e of nodes){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}desc++;const role=ROLE(e),vis=V(e),acc=N(e.getAttribute('aria-label')||e.getAttribute('title')||e.innerText||e.textContent||''),sem=SEM(acc),ds=L(e.getAttribute('data-state')),sel=L(e.getAttribute('aria-selected'))==='true'||L(e.getAttribute('aria-checked'))==='true'||['selected','checked','active','on'].includes(ds),enabled=!(e.disabled||L(e.getAttribute('aria-disabled'))==='true'),popup=N(e.getAttribute('aria-haspopup'))!==''&&L(e.getAttribute('aria-haspopup'))!=='false',expanded=L(e.getAttribute('aria-expanded'))==='true';if(['button','menuitem','menuitemradio','option','radio'].includes(role)||e.tagName==='BUTTON')interactive++;if(role==='menu')menu++;if(role==='listbox')listbox++;if(role==='group')group++;if(role==='menuitem')menuitem++;if(role==='menuitemradio')menuitemradio++;if(role==='option')option++;if(role==='radio')radio++;if(role==='button'||e.tagName==='BUTTON')button++;if(role==='presentation')presentation++;if(sel)selected++;if(sem!=='NONE'){semCount++;if(vis)visibleSem++;else hiddenSem++;if(sem==='LIGHT')lc++;if(sem==='MEDIUM')mc++;if(sem==='HEAVY')hc++;if(sem==='AUTO')ac++;if(sem==='THINKING')tc++;if(sem==='INSTANT')ic++;const ah=acc?H(L(acc)):'-',q={semantic:sem,acc_hash:ah,role:role,visible:vis,enabled:enabled,selected:sel,has_popup:popup,expanded_true:expanded,data_state_open:['open','expanded'].includes(ds)};q.fp=H([q.semantic,q.acc_hash,q.role,q.visible,q.enabled,q.selected,q.has_popup,q.expanded_true,q.data_state_open].join('|'));if(out.length<MAXC)out.push(q);fps.push(q.fp);}}}out.sort((a,b)=>(a.semantic+'|'+a.acc_hash+'|'+a.role).localeCompare(b.semantic+'|'+b.acc_hash+'|'+b.role));fps.sort();const popupEvidence=owners.length===1&&targets.length===1;return JSON.stringify({success:true,complete:complete,snapshot_index:IDX,owner_count:owners.length,owner_controls_hash:controls?H(controls):'-',controls_ref_count:refs.length,resolved_target_count:targets.length,target_root_role:targetRole,target_root_visible:targetVisible,target_root_open:targetOpen,target_descendant_count:desc,target_interactive_count:interactive,target_semantic_count:semCount,target_visible_semantic_count:visibleSem,target_hidden_semantic_count:hiddenSem,target_light_count:lc,target_medium_count:mc,target_heavy_count:hc,target_auto_count:ac,target_thinking_count:tc,target_instant_count:ic,target_selected_count:selected,target_menu_count:menu,target_listbox_count:listbox,target_group_count:group,target_menuitem_count:menuitem,target_menuitemradio_count:menuitemradio,target_option_count:option,target_radio_count:radio,target_button_count:button,target_presentation_count:presentation,target_has_light_heavy:(lc+hc)>0,popup_evidence:popupEvidence,target_candidate_set_hash:H(fps.join(',')),candidates:out});}catch(e){return JSON.stringify({success:false,complete:false,error_class:'ARIA_CONTROLS_TARGET_SCAN_EXCEPTION'});}})();'''
parts = js.split('__IDX__')
assert len(parts) == 2
parts2 = parts[1].split('__BH__')
assert len(parts2) == 2
java_method = '''    private String scanOpenSurfaceJs44(int index, String baselineHash) {\n        return ''' + json.dumps(parts[0]) + ' + index + ' + json.dumps(parts2[0]) + ' + js44(baselineHash) + ' + json.dumps(parts2[1]) + ''';\n    }\n\n    private void eval44'''

m = re.search(r'    private String scanOpenSurfaceJs44\(.*?\n    }\n\n    private void eval44', s, re.S)
assert m, 'scanOpenSurfaceJs44 not found'
s = s[:m.start()] + java_method + s[m.end():]
src44.write_text(s)

cfg = PKG / 'TelemetryConfigV44.java'
cfg.write_text('''package com.homayounisaghar.chatgptwebviewprobe;\nfinal class TelemetryConfigV44 {\n    static final String WEBHOOK_URL="https://webhook.site/__V44_UNCONFIGURED__";\n    static final String SOURCE_REF="__SOURCE_REF__";\n    static final String COLLECTOR_ID="__COLLECTOR_ID__";\n    static final boolean CONFIGURED=false;\n    private TelemetryConfigV44(){}\n    static boolean isConfigured(){return CONFIGURED&&WEBHOOK_URL.startsWith("https://webhook.site/")&&!WEBHOOK_URL.contains("__V44_UNCONFIGURED__");}\n}\n''')

x = man.read_text()
old = '''        <activity android:name=".OrchestratorPaidModelEffortNestedCensusV43Activity" android:exported="true">\n            <intent-filter>\n                <action android:name="android.intent.action.MAIN" />\n                <category android:name="android.intent.category.LAUNCHER" />\n            </intent-filter>\n        </activity>'''
new = '''        <activity android:name=".OrchestratorPaidModelEffortNestedCensusV43Activity" android:exported="false" />\n        <activity android:name=".OrchestratorPaidModelEffortAriaControlsCensusV44Activity" android:exported="true">\n            <intent-filter>\n                <action android:name="android.intent.action.MAIN" />\n                <category android:name="android.intent.category.LAUNCHER" />\n            </intent-filter>\n        </activity>'''
assert old in x
man.write_text(x.replace(old, new))

g = gradle.read_text()
g = g.replace("applicationId 'com.homayounisaghar.chatgptwebviewprobe.v43diag'", "applicationId 'com.homayounisaghar.chatgptwebviewprobe.v44diag'")
g = re.sub(r'versionCode\s+\d+', 'versionCode 45', g)
g = re.sub(r"versionName\s+'[^']+'", "versionName '0.42-sidecar-paid-model-effort-aria-controls-target-census'", g)
gradle.write_text(g)

print('V44_GENERATED sidecar=com.homayounisaghar.chatgptwebviewprobe.v44diag versionCode=45 hypothesis=aria-controls-target')
