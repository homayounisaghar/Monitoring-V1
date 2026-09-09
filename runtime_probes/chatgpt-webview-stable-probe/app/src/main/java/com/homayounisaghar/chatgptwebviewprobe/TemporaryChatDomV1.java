package com.homayounisaghar.chatgptwebviewprobe;

/**
 * Current qualified Temporary Chat DOM compatibility adapter.
 *
 * Every action script re-scans the live DOM, resolves exactly one control that
 * matches the previously qualified semantic signature, verifies the expected
 * current NORMAL/TEMP route state, and then dispatches one element click.
 * Unknown/drifted/multiple matches return without a click.
 */
final class TemporaryChatDomV1 {
    private TemporaryChatDomV1() {}

    static String scanJs() {
        return "(function(){try{"+
                commonJs()+
                "const q=Array.from(document.querySelectorAll('button,a,[role],[aria-selected],[aria-pressed],[data-state],[data-testid]')).filter(V);let T=[];"+
                "for(const e of q){const tag=(e.tagName||'').toLowerCase(),role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none'));const actionable=tag==='button'||tag==='a'||['button','tab','menuitem','radio','switch','option'].includes(role)||e.hasAttribute('aria-selected')||e.hasAttribute('aria-pressed')||e.hasAttribute('data-state');if(!actionable)continue;const label=e.getAttribute('aria-label')||e.innerText||e.textContent||'',tid=e.getAttribute('data-testid')||'';if(SEM(label,tid)!=='TEMP')continue;const lh=H(N(label)),th=H(tid),ds=DS(e),sel=e.getAttribute('aria-selected')==='true'?1:0,prs=e.getAttribute('aria-pressed')==='true'?1:0,exp=e.getAttribute('aria-expanded')==='true'?1:0,dis=e.hasAttribute('disabled')?1:0,hc=HC(e),sh=H([tag,role,'TEMP',lh,th,hc].join('|'));T.push({tag:tag,role:role,lh:lh,th:th,ds:ds,sel:sel,prs:prs,exp:exp,dis:dis,hc:hc,sh:sh});}"+
                "const urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));"+
                "const E=T.filter(x=>urlhint?(x.lh==='"+TemporaryChatSignaturesV1.TEMP_LABEL_HASH+"'&&x.sh==='"+TemporaryChatSignaturesV1.TEMP_STRUCT_HASH+"'):(x.lh==='"+TemporaryChatSignaturesV1.NORMAL_LABEL_HASH+"'&&x.sh==='"+TemporaryChatSignaturesV1.NORMAL_STRUCT_HASH+"'));const c=E.length===1?E[0]:null;"+
                "let comphint=false;for(const e of Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).filter(V)){const z=N((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('placeholder')||''));if(z.includes('temporary')||z==='temp'){comphint=true;break;}}"+
                "let active=0;if(c&&(c.ds==='ACTIVE'||c.sel===1||c.prs===1))active=1;let sem='UNKNOWN';if(c&&c.tag==='button'&&c.role==='button'&&c.th==='"+TemporaryChatSignaturesV1.EMPTY_TESTID_HASH+"'&&c.ds==='NONE'&&c.sel===0&&c.prs===0&&c.exp===0&&c.dis===0&&c.hc==='NONE'&&!comphint){if(c.lh==='"+TemporaryChatSignaturesV1.NORMAL_LABEL_HASH+"'&&c.sh==='"+TemporaryChatSignaturesV1.NORMAL_STRUCT_HASH+"'&&!urlhint)sem='NORMAL';else if(c.lh==='"+TemporaryChatSignaturesV1.TEMP_LABEL_HASH+"'&&c.sh==='"+TemporaryChatSignaturesV1.TEMP_STRUCT_HASH+"'&&urlhint)sem='TEMP';}"+
                "const rows=E.map(x=>[x.tag,x.role,x.lh,x.th,x.ds,x.sel,x.prs].join('|')).sort();const allrows=T.map(x=>[x.tag,x.role,x.lh,x.th,x.ds,x.sel,x.prs].join('|')).sort();return JSON.stringify({success:true,ready:document.readyState,route_class:RC(),url_temp_hint:urlhint,composer_temp_hint:comphint,temp_candidate_count:E.length,temp_like_candidate_count:T.length,temp_active_count:active,temp_semantic_set_hash:H(rows.join('~')),temp_like_set_hash:H(allrows.join('~')),semantic_temp_state:sem,candidate_tag:c?c.tag:'-',candidate_role:c?c.role:'-',candidate_label_hash:c?c.lh:'-',candidate_testid_hash:c?c.th:'-',candidate_data_state:c?c.ds:'NONE',candidate_selected:c?c.sel:-1,candidate_pressed:c?c.prs:-1,candidate_expanded:c?c.exp:-1,candidate_disabled:c?c.dis:-1,candidate_href_class:c?c.hc:'-',candidate_struct_hash:c?c.sh:'-'});"+
                "}catch(e){return JSON.stringify({success:false,reason:'TEMP_SCAN_EXCEPTION'});}})();";
    }

    static String enterJs() { return actionJs(true); }
    static String exitJs() { return actionJs(false); }

    private static String actionJs(boolean enter) {
        String expectedLabel = enter ? TemporaryChatSignaturesV1.NORMAL_LABEL_HASH : TemporaryChatSignaturesV1.TEMP_LABEL_HASH;
        String expectedStruct = enter ? TemporaryChatSignaturesV1.NORMAL_STRUCT_HASH : TemporaryChatSignaturesV1.TEMP_STRUCT_HASH;
        String from = enter ? "NORMAL" : "TEMP";
        String expectedUrlTemp = enter ? "false" : "true";
        return "(function(){try{const EL='"+expectedLabel+"',ES='"+expectedStruct+"',FROM='"+from+"',EU="+expectedUrlTemp+";"+
                commonJs()+
                "const q=Array.from(document.querySelectorAll('button,a,[role],[aria-selected],[aria-pressed],[data-state],[data-testid]')).filter(V);let T=[];"+
                "for(const e of q){const tag=(e.tagName||'').toLowerCase(),role=N(e.getAttribute('role'))||((tag==='button')?'button':(tag==='a'?'link':'none'));const actionable=tag==='button'||tag==='a'||['button','tab','menuitem','radio','switch','option'].includes(role)||e.hasAttribute('aria-selected')||e.hasAttribute('aria-pressed')||e.hasAttribute('data-state');if(!actionable)continue;const label=e.getAttribute('aria-label')||e.innerText||e.textContent||'',tid=e.getAttribute('data-testid')||'';if(SEM(label,tid)!=='TEMP')continue;const lh=H(N(label)),th=H(tid),ds=N(e.getAttribute('data-state')||''),sel=e.getAttribute('aria-selected')==='true'?1:0,prs=e.getAttribute('aria-pressed')==='true'?1:0,exp=e.getAttribute('aria-expanded')==='true'?1:0,dis=e.hasAttribute('disabled')?1:0,hc=HC(e),sh=H([tag,role,'TEMP',lh,th,hc].join('|'));T.push({e:e,tag:tag,role:role,lh:lh,th:th,ds:ds,sel:sel,prs:prs,exp:exp,dis:dis,hc:hc,sh:sh});}"+
                "const M=T.filter(x=>x.lh===EL&&x.sh===ES);if(M.length!==1)return JSON.stringify({success:false,reason:'EXACT_SIGNATURE_COUNT',match_count:M.length,temp_like_count:T.length,dispatched:false,click_observed:false});const t=M[0],urlhint=/temporary|(?:^|[?&=_-])temp(?:[?&=_-]|$)/i.test((location.pathname||'')+(location.search||''));const clean=t.tag==='button'&&t.role==='button'&&t.th==='"+TemporaryChatSignaturesV1.EMPTY_TESTID_HASH+"'&&t.hc==='NONE'&&t.sel===0&&t.prs===0&&t.exp===0&&t.dis===0&&t.ds==='';if(!clean||urlhint!==EU)return JSON.stringify({success:false,reason:'STATE_OR_HASH',match_count:1,temp_like_count:T.length,dispatched:false,click_observed:false,label_hash:t.lh,struct_hash:t.sh,from_state:FROM});let observed=false;t.e.addEventListener('click',()=>{observed=true;},{capture:true,once:true});t.e.click();return JSON.stringify({success:true,reason:'ELEMENT_CLICK',match_count:1,temp_like_count:T.length,dispatched:true,click_observed:observed,label_hash:t.lh,struct_hash:t.sh,from_state:FROM});"+
                "}catch(e){return JSON.stringify({success:false,reason:'TEMP_ACTION_EXCEPTION',match_count:0,dispatched:false,click_observed:false});}})();";
    }

    private static String commonJs() {
        return "const H=s=>{let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return ('00000000'+h.toString(16)).slice(-8);};"+
                "const N=s=>(s||'').replace(/\\s+/g,' ').trim().toLowerCase();"+
                "const V=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getAttribute('aria-hidden')!=='true';};"+
                "const DS=e=>{const v=N(e.getAttribute('data-state'));if(['active','selected','checked','on'].includes(v))return 'ACTIVE';if(['inactive','unselected','unchecked','off'].includes(v))return 'INACTIVE';if(v==='open')return 'OPEN';if(v==='closed')return 'CLOSED';return v?'OTHER':'NONE';};"+
                "const HC=e=>{const h=e.getAttribute('href')||'';if(!h)return 'NONE';try{const u=new URL(h,location.href),p=u.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';return 'OTHER';}catch(x){return 'OTHER';}};"+
                "const RC=()=>{const p=location.pathname||'/';if(p==='/')return 'HOME';if(/^\\/c\\/[^/]+/.test(p))return 'CONVERSATION';if(/^\\/g\\//.test(p))return 'GPT_ROUTE';if(/^\\/project/.test(p))return 'PROJECT_ROUTE';return 'OTHER_ROUTE';};"+
                "const SEM=(label,tid)=>{const x=N(label),t=N(tid),z=x+' '+t;if(z.includes('temporary')||x==='temp'||t.includes('temp'))return 'TEMP';return 'OTHER';};";
    }
}
