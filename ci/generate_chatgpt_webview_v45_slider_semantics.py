#!/usr/bin/env python3
from pathlib import Path
import json
import re
import runpy

runpy.run_path('ci/generate_chatgpt_webview_v44_aria_controls.py', run_name='__main__')

ROOT = Path('runtime_probes/chatgpt-webview-stable-probe')
PKG = ROOT / 'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
src44 = PKG / 'OrchestratorPaidModelEffortAriaControlsCensusV44Activity.java'
src45 = PKG / 'OrchestratorPaidModelEffortSliderSemanticsV45Activity.java'
man = ROOT / 'app/src/main/AndroidManifest.xml'
gradle = ROOT / 'app/build.gradle'

s = src44.read_text()
s = s.replace('OrchestratorPaidModelEffortAriaControlsCensusV44Activity', 'OrchestratorPaidModelEffortSliderSemanticsV45Activity')
s = s.replace('TelemetryConfigV44', 'TelemetryConfigV45')
s = s.replace('44', '45')
s = s.replace('cp-v45-paid-model-effort-aria-controls-target-census-v1', 'cp-v45-paid-model-effort-slider-value-census-v1')
s = s.replace('paid-model-effort-aria-controls-target-census', 'paid-model-effort-slider-value-census')
s = s.replace('RUN ARIA-CONTROLS TARGET CENSUS', 'RUN SLIDER VALUE SEMANTICS CENSUS')
s = s.replace('ARIA TARGET CENSUS RUNNING...', 'SLIDER VALUE CENSUS RUNNING...')
s = s.replace('Relation-target snapshot ', 'Slider snapshot ')
s = s.replace('ARIA_CONTROLS_TARGET_SNAPSHOT', 'SLIDER_VALUE_SNAPSHOT')
s = s.replace('v0.42 aria-controls target census ready — zero model option clicks', 'v0.43 slider-value census ready — read-only after proven opener')

old_fields = '    private int resolvedTargetSnapshots45 = 0;\n    private int targetEffortOptionSnapshots45 = 0;\n'
new_fields = ('    private int resolvedTargetSnapshots45 = 0;\n'
              '    private int uniqueSliderSnapshots45 = 0;\n'
              '    private int stableSliderSnapshots45 = 0;\n'
              '    private String resolverStructureHash45 = "-";\n'
              '    private String resolverValueHash45 = "-";\n')
assert old_fields in s
s = s.replace(old_fields, new_fields)

old_reset = '        resolvedTargetSnapshots45 = 0;\n        targetEffortOptionSnapshots45 = 0;\n'
new_reset = ('        resolvedTargetSnapshots45 = 0;\n'
             '        uniqueSliderSnapshots45 = 0;\n'
             '        stableSliderSnapshots45 = 0;\n'
             '        resolverStructureHash45 = "-";\n'
             '        resolverValueHash45 = "-";\n')
assert old_reset in s
s = s.replace(old_reset, new_reset, 1)

old_final = '''        if (index >= SNAPSHOTS45) {
            if (popupEvidenceSnapshots45 > 0) {
                prefs45.edit().putString("claim_status", "CONFIRMED_POPUP_EVIDENCE").commit();
                claimStatus45 = "CONFIRMED_POPUP_EVIDENCE";
                if (completeSnapshots45 == SNAPSHOTS45 && resolvedTargetSnapshots45 == SNAPSHOTS45) {
                    finish45(targetEffortOptionSnapshots45 > 0
                            ? "PASS_ARIA_CONTROLS_TARGET_EXPOSES_LIGHT_HEAVY"
                            : "NEGATIVE_ARIA_CONTROLS_TARGET_RESOLVED_NO_LIGHT_HEAVY");
                } else if (resolvedTargetSnapshots45 > 0) {
                    finish45("PARTIAL_ARIA_CONTROLS_TARGET_RESOLUTION");
                } else {
                    finish45("NEGATIVE_ARIA_CONTROLS_TARGET_UNRESOLVED");
                }
            } else {
                prefs45.edit().putString("claim_status", "UNCERTAIN_NO_REPLAY").commit();
                claimStatus45 = "UNCERTAIN_NO_REPLAY";
                finish45("ARIA_CONTROLS_TARGET_UNCERTAIN_NO_REPLAY");
            }
            return;
        }'''
new_final = '''        if (index >= SNAPSHOTS45) {
            if (popupEvidenceSnapshots45 > 0) {
                prefs45.edit().putString("claim_status", "CONFIRMED_POPUP_EVIDENCE").commit();
                claimStatus45 = "CONFIRMED_POPUP_EVIDENCE";
                if (completeSnapshots45 == SNAPSHOTS45 && resolvedTargetSnapshots45 == SNAPSHOTS45) {
                    if (uniqueSliderSnapshots45 == SNAPSHOTS45 && stableSliderSnapshots45 == SNAPSHOTS45) {
                        finish45("PASS_UNIQUE_STABLE_SLIDER_VALUE_SEMANTICS");
                    } else if (uniqueSliderSnapshots45 > 0) {
                        finish45("PARTIAL_SLIDER_VALUE_SEMANTICS");
                    } else {
                        finish45("NEGATIVE_SLIDER_VALUE_SEMANTICS_ABSENT");
                    }
                } else if (resolvedTargetSnapshots45 > 0) {
                    finish45("PARTIAL_SLIDER_TARGET_RESOLUTION");
                } else {
                    finish45("NEGATIVE_SLIDER_TARGET_UNRESOLVED");
                }
            } else {
                prefs45.edit().putString("claim_status", "UNCERTAIN_NO_REPLAY").commit();
                claimStatus45 = "UNCERTAIN_NO_REPLAY";
                finish45("SLIDER_VALUE_SEMANTICS_UNCERTAIN_NO_REPLAY");
            }
            return;
        }'''
assert old_final in s
s = s.replace(old_final, new_final)

old_counter = '''            boolean targetResolved = o.optInt("resolved_target_count", 0) == 1;
            boolean targetHasEffortOption = o.optInt("target_light_count", 0) > 0 || o.optInt("target_heavy_count", 0) > 0;
            if (targetResolved) resolvedTargetSnapshots45++;
            if (targetHasEffortOption) targetEffortOptionSnapshots45++;
'''
new_counter = '''            boolean targetResolved = o.optInt("resolved_target_count", 0) == 1;
            boolean uniqueSlider = o.optInt("logical_slider_count", 0) == 1;
            String structureHash = o.optString("resolver_structure_hash", "-");
            String valueHash = o.optString("resolver_value_hash", "-");
            if (targetResolved) resolvedTargetSnapshots45++;
            if (uniqueSlider) {
                uniqueSliderSnapshots45++;
                if ("-".equals(resolverStructureHash45)) {
                    resolverStructureHash45 = structureHash;
                    resolverValueHash45 = valueHash;
                }
                if (resolverStructureHash45.equals(structureHash) && resolverValueHash45.equals(valueHash)) stableSliderSnapshots45++;
            }
'''
assert old_counter in s
s = s.replace(old_counter, new_counter, 1)

old_copy = 'copy45(st, o, "success","complete","snapshot_index","owner_count","owner_controls_hash","controls_ref_count","resolved_target_count","target_root_role","target_root_visible","target_root_open","target_descendant_count","target_interactive_count","target_semantic_count","target_visible_semantic_count","target_hidden_semantic_count","target_light_count","target_medium_count","target_heavy_count","target_auto_count","target_thinking_count","target_instant_count","target_selected_count","target_menu_count","target_listbox_count","target_group_count","target_menuitem_count","target_menuitemradio_count","target_option_count","target_radio_count","target_button_count","target_presentation_count","target_has_light_heavy","popup_evidence","target_candidate_set_hash");'
new_copy = 'copy45(st, o, "success","complete","snapshot_index","owner_count","owner_controls_hash","controls_ref_count","resolved_target_count","target_root_role","target_root_visible","target_root_open","sliderish_count","visible_sliderish_count","role_slider_count","visible_role_slider_count","range_input_count","visible_range_input_count","aria_value_node_count","logical_slider_count","resolver_role","resolver_tag","resolver_visible","resolver_enabled","resolver_orientation","resolver_has_aria_now","resolver_aria_now","resolver_has_aria_min","resolver_aria_min","resolver_has_aria_max","resolver_aria_max","resolver_has_aria_text","resolver_value_text_semantic","resolver_value_text_hash","resolver_has_native_value","resolver_native_value","resolver_native_min","resolver_native_max","resolver_native_step","resolver_structure_hash","resolver_value_hash","popup_evidence","slider_candidate_set_hash");'
assert old_copy in s
s = s.replace(old_copy, new_copy)

phase_old = 'phase45("SLIDER_VALUE_SNAPSHOT", complete ? (targetResolved ? "CAPTURED_TARGET_RESOLVED" : "CAPTURED_TARGET_UNRESOLVED") : "CAPTURED_BUDGET_LIMIT", st);'
phase_new = 'phase45("SLIDER_VALUE_SNAPSHOT", complete ? (uniqueSlider ? "CAPTURED_UNIQUE_SLIDER" : (targetResolved ? "CAPTURED_TARGET_NO_UNIQUE_SLIDER" : "CAPTURED_TARGET_UNRESOLVED")) : "CAPTURED_BUDGET_LIMIT", st);'
assert phase_old in s
s = s.replace(phase_old, phase_new)

old_finish = '        put45(st,"resolved_target_snapshots",resolvedTargetSnapshots45);\n        put45(st,"target_effort_option_snapshots",targetEffortOptionSnapshots45);\n'
new_finish = ('        put45(st,"resolved_target_snapshots",resolvedTargetSnapshots45);\n'
              '        put45(st,"unique_slider_snapshots",uniqueSliderSnapshots45);\n'
              '        put45(st,"stable_slider_snapshots",stableSliderSnapshots45);\n'
              '        put45(st,"resolver_structure_hash",resolverStructureHash45);\n'
              '        put45(st,"resolver_value_hash",resolverValueHash45);\n')
assert old_finish in s
s = s.replace(old_finish, new_finish, 1)

js = r'''(function(){try{const IDX=__IDX__,T0=performance.now(),MAXN=12000,MAXMS=300,MAXC=16;const N=x=>(x||'').replace(/\s+/g,' ').trim(),L=x=>N(x).toLowerCase(),TOK=s=>L(s).split(/[^a-z0-9.]+/).filter(Boolean),H=s=>{let x=2166136261>>>0;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return('00000000'+x.toString(16)).slice(-8);},V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}},SEM=s=>{const t=TOK(s),w=[['LIGHT','light'],['MEDIUM','medium'],['HEAVY','heavy'],['AUTO','auto'],['THINKING','thinking'],['INSTANT','instant']],m=w.filter(x=>t.includes(x[1]));return m.length===1?m[0][0]:'NONE';},ROLE=e=>L(e.getAttribute('role'))||((e.tagName||'').toLowerCase()),OPEN=e=>{const ds=L(e.getAttribute('data-state')),ex=L(e.getAttribute('aria-expanded'));return ex==='true'||ds==='open'||ds==='expanded';},NUM=x=>{const s=N(x);if(!/^-?\d+(?:\.\d+)?$/.test(s))return '-';const n=Number(s);return Number.isFinite(n)?String(n):'-';};let input=null;for(const e of document.querySelectorAll('textarea,[contenteditable=true],[role=textbox]'))if(V(e)){input=e;break;}let composer=null;if(input){let p=input.parentElement;for(let d=0;p&&d<10;d++,p=p.parentElement){if(p.querySelectorAll('button,[role=button]').length>=3){composer=p;break;}}}const owners=[];if(composer)for(const e of composer.querySelectorAll('button,[role=button]')){if(!V(e))continue;const acc=N(e.getAttribute('aria-label')||e.getAttribute('title')||e.innerText||e.textContent||''),sem=SEM(acc),popup=N(e.getAttribute('aria-haspopup')),expanded=L(e.getAttribute('aria-expanded')),controls=N(e.getAttribute('aria-controls'));if(sem==='THINKING'&&expanded==='true'&&popup!==''&&L(popup)!=='false'&&controls!=='')owners.push(e);}let controls='',refs=[],targets=[];if(owners.length===1){controls=N(owners[0].getAttribute('aria-controls'));refs=controls.split(/\s+/).filter(Boolean).slice(0,8);for(const id of refs){let t=null;try{t=document.getElementById(id);}catch(_){}if(t&&t.isConnected&&!targets.includes(t))targets.push(t);}}let complete=true,visited=0,sliderish=0,visibleSliderish=0,roleSlider=0,visibleRoleSlider=0,rangeInput=0,visibleRangeInput=0,ariaValue=0,targetRole='-',targetVisible=false,targetOpen=false;const candidates=[],fps=[];let primary=[];if(targets.length===1){const root=targets[0];targetRole=ROLE(root);targetVisible=V(root);targetOpen=OPEN(root);const nodes=[root,...root.querySelectorAll('*')];for(const e of nodes){if(++visited>MAXN||performance.now()-T0>MAXMS){complete=false;break;}const role=ROLE(e),tag=(e.tagName||'').toLowerCase(),type=L(e.getAttribute('type')),vis=V(e),isRole=role==='slider',isRange=tag==='input'&&type==='range',hasNow=N(e.getAttribute('aria-valuenow'))!=='',hasMin=N(e.getAttribute('aria-valuemin'))!=='',hasMax=N(e.getAttribute('aria-valuemax'))!=='',hasText=N(e.getAttribute('aria-valuetext'))!=='';if(!(isRole||isRange||hasNow||hasMin||hasMax||hasText))continue;sliderish++;if(vis)visibleSliderish++;if(isRole){roleSlider++;if(vis)visibleRoleSlider++;}if(isRange){rangeInput++;if(vis)visibleRangeInput++;}if(hasNow||hasMin||hasMax||hasText)ariaValue++;const enabled=!(e.disabled||L(e.getAttribute('aria-disabled'))==='true'),orientation=(L(e.getAttribute('aria-orientation'))==='vertical'?'VERTICAL':L(e.getAttribute('aria-orientation'))==='horizontal'?'HORIZONTAL':'NONE'),acc=N(e.getAttribute('aria-label')||e.getAttribute('title')||''),vtext=N(e.getAttribute('aria-valuetext')),now=NUM(e.getAttribute('aria-valuenow')),amin=NUM(e.getAttribute('aria-valuemin')),amax=NUM(e.getAttribute('aria-valuemax')),nvalue=isRange?NUM(e.value):'-',nmin=isRange?NUM(e.min):'-',nmax=isRange?NUM(e.max):'-',nstep=isRange?NUM(e.step):'-',struct=H([role,tag,isRange,hasNow,hasMin,hasMax,hasText,orientation,acc?H(L(acc)):'-'].join('|')),val=H([now,amin,amax,vtext?H(L(vtext)):'-',SEM(vtext),nvalue,nmin,nmax,nstep].join('|')),q={role:role,tag:tag,visible:vis,enabled:enabled,is_role_slider:isRole,is_range_input:isRange,has_aria_now:hasNow,aria_now:now,has_aria_min:hasMin,aria_min:amin,has_aria_max:hasMax,aria_max:amax,has_aria_text:hasText,value_text_semantic:SEM(vtext),value_text_hash:vtext?H(L(vtext)):'-',has_native_value:isRange,native_value:nvalue,native_min:nmin,native_max:nmax,native_step:nstep,orientation:orientation,acc_hash:acc?H(L(acc)):'-',structure_hash:struct,value_hash:val};q.fp=H([struct,val,vis,enabled].join('|'));if(candidates.length<MAXC)candidates.push(q);fps.push(q.fp);if(vis&&isRole)primary.push(q);}if(primary.length===0)for(const q of candidates)if(q.visible&&q.is_range_input)primary.push(q);}candidates.sort((a,b)=>(a.role+'|'+a.tag+'|'+a.structure_hash).localeCompare(b.role+'|'+b.tag+'|'+b.structure_hash));fps.sort();const logical=primary.length===1?1:0,r=logical?primary[0]:null,popupEvidence=owners.length===1&&targets.length===1;return JSON.stringify({success:true,complete:complete,snapshot_index:IDX,owner_count:owners.length,owner_controls_hash:controls?H(controls):'-',controls_ref_count:refs.length,resolved_target_count:targets.length,target_root_role:targetRole,target_root_visible:targetVisible,target_root_open:targetOpen,sliderish_count:sliderish,visible_sliderish_count:visibleSliderish,role_slider_count:roleSlider,visible_role_slider_count:visibleRoleSlider,range_input_count:rangeInput,visible_range_input_count:visibleRangeInput,aria_value_node_count:ariaValue,logical_slider_count:logical,resolver_role:r?r.role:'-',resolver_tag:r?r.tag:'-',resolver_visible:r?!!r.visible:false,resolver_enabled:r?!!r.enabled:false,resolver_orientation:r?r.orientation:'NONE',resolver_has_aria_now:r?!!r.has_aria_now:false,resolver_aria_now:r?r.aria_now:'-',resolver_has_aria_min:r?!!r.has_aria_min:false,resolver_aria_min:r?r.aria_min:'-',resolver_has_aria_max:r?!!r.has_aria_max:false,resolver_aria_max:r?r.aria_max:'-',resolver_has_aria_text:r?!!r.has_aria_text:false,resolver_value_text_semantic:r?r.value_text_semantic:'NONE',resolver_value_text_hash:r?r.value_text_hash:'-',resolver_has_native_value:r?!!r.has_native_value:false,resolver_native_value:r?r.native_value:'-',resolver_native_min:r?r.native_min:'-',resolver_native_max:r?r.native_max:'-',resolver_native_step:r?r.native_step:'-',resolver_structure_hash:r?r.structure_hash:'-',resolver_value_hash:r?r.value_hash:'-',popup_evidence:popupEvidence,slider_candidate_set_hash:H(fps.join(',')),candidates:candidates});}catch(e){return JSON.stringify({success:false,complete:false,error_class:'SLIDER_VALUE_SCAN_EXCEPTION'});}})();'''
parts = js.split('__IDX__')
assert len(parts) == 2
java_method = '''    private String scanOpenSurfaceJs45(int index, String baselineHash) {\n        return ''' + json.dumps(parts[0]) + ' + index + ' + json.dumps(parts[1]) + ''';\n    }\n\n    private void eval45'''
m = re.search(r'    private String scanOpenSurfaceJs45\(.*?\n    }\n\n    private void eval45', s, re.S)
assert m, 'scanOpenSurfaceJs45 not found'
s = s[:m.start()] + java_method + s[m.end():]
src45.write_text(s)

cfg = PKG / 'TelemetryConfigV45.java'
cfg.write_text('''package com.homayounisaghar.chatgptwebviewprobe;\nfinal class TelemetryConfigV45 {\n    static final String WEBHOOK_URL="https://webhook.site/__V45_UNCONFIGURED__";\n    static final String SOURCE_REF="__SOURCE_REF__";\n    static final String COLLECTOR_ID="__COLLECTOR_ID__";\n    static final boolean CONFIGURED=false;\n    private TelemetryConfigV45(){}\n    static boolean isConfigured(){return CONFIGURED&&WEBHOOK_URL.startsWith("https://webhook.site/")&&!WEBHOOK_URL.contains("__V45_UNCONFIGURED__");}\n}\n''')

x = man.read_text()
old = '''        <activity android:name=".OrchestratorPaidModelEffortAriaControlsCensusV44Activity" android:exported="true">\n            <intent-filter>\n                <action android:name="android.intent.action.MAIN" />\n                <category android:name="android.intent.category.LAUNCHER" />\n            </intent-filter>\n        </activity>'''
new = '''        <activity android:name=".OrchestratorPaidModelEffortAriaControlsCensusV44Activity" android:exported="false" />\n        <activity android:name=".OrchestratorPaidModelEffortSliderSemanticsV45Activity" android:exported="true">\n            <intent-filter>\n                <action android:name="android.intent.action.MAIN" />\n                <category android:name="android.intent.category.LAUNCHER" />\n            </intent-filter>\n        </activity>'''
assert old in x
man.write_text(x.replace(old, new))

g = gradle.read_text()
g = g.replace("applicationId 'com.homayounisaghar.chatgptwebviewprobe.v44diag'", "applicationId 'com.homayounisaghar.chatgptwebviewprobe.diag'")
g = re.sub(r'versionCode\s+\d+', 'versionCode 46', g)
g = re.sub(r"versionName\s+'[^']+'", "versionName '0.43-stable-diag-paid-model-effort-slider-value-census'", g)
gradle.write_text(g)

print('V45_GENERATED package=com.homayounisaghar.chatgptwebviewprobe.diag versionCode=46 hypothesis=slider-value-semantics')
