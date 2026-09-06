#!/usr/bin/env python3
from pathlib import Path
import runpy,re

# Start from the exact v0.60 source, then narrow the resolver from
# "exactly one TEMP-like control" to "exactly one control matching the
# independently observed exact entry/exit signature". Unrelated TEMP-like
# controls remain visible/read-only and can never satisfy the write gate.
runpy.run_path("ci/generate_chatgpt_webview_v62_temporary_chat_autonomous_roundtrip_fixed.py", run_name="__main__")

ROOT=Path("runtime_probes/chatgpt-webview-stable-probe")
PKG=ROOT/"app/src/main/java/com/homayounisaghar/chatgptwebviewprobe"
OLD=PKG/"OrchestratorTemporaryChatAutonomousRoundtripV62Activity.java"
NEW=PKG/"OrchestratorTemporaryChatSignatureUniqueRoundtripV63Activity.java"
s=OLD.read_text()

# Identity/version-local replacements.
s=s.replace("OrchestratorTemporaryChatAutonomousRoundtripV62Activity","OrchestratorTemporaryChatSignatureUniqueRoundtripV63Activity")
s=s.replace("cp-v62-temporary-chat-autonomous-roundtrip-v1","cp-v63-temporary-chat-signature-unique-roundtrip-v1")
s=s.replace("temporary-chat-autonomous-roundtrip","temporary-chat-signature-unique-roundtrip")
s=s.replace("cp_v62_temp_roundtrip_claim","cp_v63_temp_signature_roundtrip_claim")
s=s.replace("TelemetryConfigV62","TelemetryConfigV63")
s=s.replace("v0.60 autonomous Temporary Chat roundtrip","v0.61 autonomous Temporary Chat exact-signature roundtrip")
s=s.replace("v0.60 ready.","v0.61 ready.")

# Scanner: keep all TEMP-like controls in T for telemetry, but define E as the
# exact signature set appropriate to the current URL state. Only E can become
# the candidate used by semantic gates. temp_candidate_count now means exact
# candidate count; temp_like_candidate_count separately reports T.length.
old_scan='''            \"const c=T.length===1?T[0]:null;const urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));let comphint=false;for(const e of Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).filter(V)){const s=N((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('placeholder')||''));if(s.includes('temporary')||s==='temp'){comphint=true;break;}}let active=0;if(c&&(c.ds==='ACTIVE'||c.sel===1||c.prs===1))active=1;let sem='UNKNOWN';if(c&&c.tag==='button'&&c.role==='button'&&c.th==='811c9dc5'&&c.ds==='NONE'&&c.sel===0&&c.prs===0&&c.exp===0&&c.dis===0&&c.hc==='NONE'&&!comphint){if(c.lh==='1a957a52'&&c.sh==='b9c97d1e'&&!urlhint)sem='NORMAL';else if(c.lh==='ae0e16e6'&&c.sh==='34d052a8'&&urlhint)sem='TEMP';}\"+\n            \"const rows=T.map(x=>[x.tag,x.role,x.lh,x.th,x.ds,x.sel,x.prs].join('|')).sort();return JSON.stringify({success:true,ready:document.readyState,route_class:RC(),url_temp_hint:urlhint,composer_temp_hint:comphint,temp_candidate_count:T.length,temp_active_count:active,temp_semantic_set_hash:H(rows.join('~')),semantic_temp_state:sem,candidate_tag:c?c.tag:'-',candidate_role:c?c.role:'-',candidate_label_hash:c?c.lh:'-',candidate_testid_hash:c?c.th:'-',candidate_data_state:c?c.ds:'NONE',candidate_selected:c?c.sel:-1,candidate_pressed:c?c.prs:-1,candidate_expanded:c?c.exp:-1,candidate_disabled:c?c.dis:-1,candidate_href_class:c?c.hc:'-',candidate_struct_hash:c?c.sh:'-'});\"+'''
new_scan='''            \"const urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));const E=T.filter(x=>urlhint?(x.lh==='ae0e16e6'&&x.sh==='34d052a8'):(x.lh==='1a957a52'&&x.sh==='b9c97d1e'));const c=E.length===1?E[0]:null;let comphint=false;for(const e of Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).filter(V)){const s=N((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('placeholder')||''));if(s.includes('temporary')||s==='temp'){comphint=true;break;}}let active=0;if(c&&(c.ds==='ACTIVE'||c.sel===1||c.prs===1))active=1;let sem='UNKNOWN';if(c&&c.tag==='button'&&c.role==='button'&&c.th==='811c9dc5'&&c.ds==='NONE'&&c.sel===0&&c.prs===0&&c.exp===0&&c.dis===0&&c.hc==='NONE'&&!comphint){if(c.lh==='1a957a52'&&c.sh==='b9c97d1e'&&!urlhint)sem='NORMAL';else if(c.lh==='ae0e16e6'&&c.sh==='34d052a8'&&urlhint)sem='TEMP';}\"+\n            \"const rows=E.map(x=>[x.tag,x.role,x.lh,x.th,x.ds,x.sel,x.prs].join('|')).sort();const allrows=T.map(x=>[x.tag,x.role,x.lh,x.th,x.ds,x.sel,x.prs].join('|')).sort();return JSON.stringify({success:true,ready:document.readyState,route_class:RC(),url_temp_hint:urlhint,composer_temp_hint:comphint,temp_candidate_count:E.length,temp_like_candidate_count:T.length,temp_active_count:active,temp_semantic_set_hash:H(rows.join('~')),temp_like_set_hash:H(allrows.join('~')),semantic_temp_state:sem,candidate_tag:c?c.tag:'-',candidate_role:c?c.role:'-',candidate_label_hash:c?c.lh:'-',candidate_testid_hash:c?c.th:'-',candidate_data_state:c?c.ds:'NONE',candidate_selected:c?c.sel:-1,candidate_pressed:c?c.prs:-1,candidate_expanded:c?c.exp:-1,candidate_disabled:c?c.dis:-1,candidate_href_class:c?c.hc:'-',candidate_struct_hash:c?c.sh:'-'});\"+'''
assert old_scan in s, "v0.60 scan block not found"
s=s.replace(old_scan,new_scan,1)

# Click resolver: total TEMP-like count no longer gates dispatch. Resolve the
# exact expected label+struct signature and require exactly one exact match.
old_click='''            \"if(T.length!==1)return JSON.stringify({success:false,reason:'TEMP_COUNT',match_count:0,dispatched:false,click_observed:false});const t=T[0],urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));const clean=t.tag==='button'&&t.role==='button'&&t.th==='811c9dc5'&&t.hc==='NONE'&&t.sel===0&&t.prs===0&&t.exp===0&&t.dis===0&&t.ds==='none';if(!clean||t.lh!==EL||t.sh!==ES||urlhint!==EU)return JSON.stringify({success:false,reason:'STATE_OR_HASH',match_count:(t.lh===EL&&t.sh===ES)?1:0,dispatched:false,click_observed:false,label_hash:t.lh,struct_hash:t.sh,from_state:FROM});let observed=false;t.e.addEventListener('click',()=>{observed=true;},{capture:true,once:true});t.e.click();return JSON.stringify({success:true,reason:'ELEMENT_CLICK',match_count:1,dispatched:true,click_observed:observed,label_hash:t.lh,struct_hash:t.sh,from_state:FROM});\"+'''
new_click='''            \"const M=T.filter(x=>x.lh===EL&&x.sh===ES);if(M.length!==1)return JSON.stringify({success:false,reason:'EXACT_SIGNATURE_COUNT',match_count:M.length,temp_like_count:T.length,dispatched:false,click_observed:false});const t=M[0],urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));const clean=t.tag==='button'&&t.role==='button'&&t.th==='811c9dc5'&&t.hc==='NONE'&&t.sel===0&&t.prs===0&&t.exp===0&&t.dis===0&&t.ds==='none';if(!clean||urlhint!==EU)return JSON.stringify({success:false,reason:'STATE_OR_HASH',match_count:1,temp_like_count:T.length,dispatched:false,click_observed:false,label_hash:t.lh,struct_hash:t.sh,from_state:FROM});let observed=false;t.e.addEventListener('click',()=>{observed=true;},{capture:true,once:true});t.e.click();return JSON.stringify({success:true,reason:'ELEMENT_CLICK',match_count:1,temp_like_count:T.length,dispatched:true,click_observed:observed,label_hash:t.lh,struct_hash:t.sh,from_state:FROM});\"+'''
assert old_click in s, "v0.60 click resolver block not found"
s=s.replace(old_click,new_click,1)

# Include the new diagnostic fields in emitted full-state snapshots.
s=s.replace('"temp_candidate_count","temp_active_count","temp_semantic_set_hash"', '"temp_candidate_count","temp_like_candidate_count","temp_active_count","temp_semantic_set_hash","temp_like_set_hash"')

NEW.write_text(s)
OLD.unlink()

# Fresh telemetry config for v0.61.
cfg=(PKG/"TelemetryConfigV62.java").read_text()
(PKG/"TelemetryConfigV63.java").write_text(cfg.replace("TelemetryConfigV62","TelemetryConfigV63"))

# Version identity.
g=ROOT/"app/build.gradle"
gs=g.read_text()
gs=re.sub(r"versionCode\s+63\b","versionCode 64",gs)
gs=gs.replace("0.60-stable-diag-temporary-chat-autonomous-roundtrip","0.61-stable-diag-temporary-chat-signature-unique-roundtrip")
g.write_text(gs)

# Launcher only; registered Accessibility service remains V51.
m=ROOT/"app/src/main/AndroidManifest.xml"
ms=m.read_text().replace("OrchestratorTemporaryChatAutonomousRoundtripV62Activity","OrchestratorTemporaryChatSignatureUniqueRoundtripV63Activity")
assert "ControlPlaneAccessibilityServiceV51" in ms
assert "@xml/cp_accessibility_service_v51" in ms
for v in range(52,64):
    assert f"ControlPlaneAccessibilityServiceV{v}" not in ms
m.write_text(ms)

# Build-time contract assertions.
out=NEW.read_text()
assert 'temp_like_candidate_count' in out
assert "const M=T.filter(x=>x.lh===EL&&x.sh===ES)" in out
assert "reason:'EXACT_SIGNATURE_COUNT'" in out
assert "temp_candidate_count:E.length" in out
assert "pageUiDispatches==2&&targetReceipt&&restoreReceipt" in out
assert "CLAIMED_BEFORE_TEMP_ENTRY_CLICK" in out
assert "CLAIMED_BEFORE_TEMP_EXIT_CLICK" in out
assert "PASS_STABLE_TEMP_TARGET_RECEIPT" in out
assert "PASS_STABLE_NORMAL_RESTORE_RECEIPT" in out
assert "PASS_AUTONOMOUS_TEMPORARY_CHAT_ROUNDTRIP" in out
for forbidden in ["elementFromPoint","document.evaluate","dispatchTouchEvent(","performClick(","ACTION_SET_PROGRESS","CookieManager","getCookie(","addJavascriptInterface"]:
    assert forbidden not in out
