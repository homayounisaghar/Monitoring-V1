package com.homayounisaghar.chatgptwebviewprobe;

final class DictationLifecycleAdapterV23 {
    static final String SUBMIT_LABEL = "Submit dictation";
    static final String CANCEL_LABEL = "Cancel dictation";

    private DictationLifecycleAdapterV23() {}

    static String clickSubmitJs() { return clickExactLabelJs(SUBMIT_LABEL); }
    static String clickCancelJs() { return clickExactLabelJs(CANCEL_LABEL); }

    static String clickExactLabelJs(String label) {
        String target = js(label);
        return "(function(){try{" + COMMON_JS
                + "const s=scan();if(!s.success)return JSON.stringify({success:false,matches:-1,clicked:false,reason:s.reason,scan_nodes:s.nodes,root_count:s.roots,elapsed_ms:s.elapsed});"
                + "const target=N('" + target + "').toLowerCase();const xs=[];const seen=new Set();"
                + "for(const r of s.list){let q=[];try{q=[...r.querySelectorAll('button[aria-label],[role=button][aria-label]')];}catch(_){}for(const e of q){if(seen.has(e)||!V(e))continue;seen.add(e);if(N(A(e,'aria-label')).toLowerCase()===target)xs.push(e);}}"
                + "const out={success:true,matches:xs.length,clicked:false,scan_nodes:s.nodes,root_count:s.roots,elapsed_ms:s.elapsed};if(xs.length===1){xs[0].click();out.clicked=true;}return JSON.stringify(out);"
                + "}catch(e){return JSON.stringify({success:false,matches:-1,clicked:false,reason:String(e&&e.name||'ERR')});}})();";
    }

    static String stateJs() {
        return "(function(){try{" + COMMON_JS
                + "const s=scan();if(!s.success)return JSON.stringify({success:false,reason:s.reason,scan_nodes:s.nodes,root_count:s.roots,elapsed_ms:s.elapsed,raw_chat_text_returned:false,raw_composer_text_returned:false});"
                + "let submit=0,cancel=0,ready=0;const seen=new Set();for(const r of s.list){let q=[];try{q=[...r.querySelectorAll('button,[role=button]')];}catch(_){}for(const e of q){if(seen.has(e)||!V(e))continue;seen.add(e);const a=N(A(e,'aria-label')).toLowerCase();if(a==='submit dictation')submit++;else if(a==='cancel dictation')cancel++;else{const z=(a+' '+N(A(e,'title'))+' '+N(A(e,'data-testid'))).toLowerCase();if(/microphone|dictat|voice input|record audio|record message/.test(z))ready++;}}}"
                + "let users=-1;try{users=document.querySelectorAll('[data-message-author-role=user]').length;}catch(_){}let raw='';try{const ed=[...document.querySelectorAll('#prompt-textarea,textarea,[contenteditable=true]')].filter(V);const ce=ed.length?ed[ed.length-1]:null;raw=ce?N(typeof ce.value==='string'?ce.value:(ce.innerText||ce.textContent||'')):'';}catch(_){}"
                + "return JSON.stringify({success:true,submit_count:submit,cancel_count:cancel,ready_dictation_count:ready,user_turn_count:users,composer_len:raw.length,composer_hash:raw?H(raw):'-',scan_nodes:s.nodes,root_count:s.roots,elapsed_ms:s.elapsed,raw_chat_text_returned:false,raw_composer_text_returned:false});"
                + "}catch(e){return JSON.stringify({success:false,reason:String(e&&e.name||'ERR'),raw_chat_text_returned:false,raw_composer_text_returned:false});}})();";
    }

    private static String js(String s) {
        return (s == null ? "" : s).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r");
    }

    private static final String COMMON_JS =
            "const MAX_NODES=8000,MAX_ROOTS=32,MAX_MS=180;"
            + "const N=s=>String(s==null?'':s).replace(/\\s+/g,' ').trim();"
            + "const A=(e,n)=>{try{return String(e&&e.getAttribute?e.getAttribute(n)||'':'');}catch(_){return '';}};"
            + "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};"
            + "const H=s=>{let h=2166136261>>>0;for(let i=0;i<String(s).length;i++){h^=String(s).charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return('00000000'+h.toString(16)).slice(-8);};"
            + "const NOW=()=>{try{return performance.now();}catch(_){return Date.now();}};"
            + "const scan=()=>{const t=NOW(),list=[document],known=new Set([document]);let nodes=0,truncated=false;outer:for(let i=0;i<list.length;i++){const r=list[i],doc=(r&&r.ownerDocument)||document;let w=null;try{w=doc.createTreeWalker(r,(typeof NodeFilter!=='undefined'?NodeFilter.SHOW_ELEMENT:1));}catch(_){}if(!w)continue;let e;while((e=w.nextNode())){nodes++;if(nodes>MAX_NODES||NOW()-t>MAX_MS){truncated=true;break outer;}try{if(e.shadowRoot&&!known.has(e.shadowRoot)){if(list.length>=MAX_ROOTS){truncated=true;break outer;}known.add(e.shadowRoot);list.push(e.shadowRoot);}}catch(_){}if(String(e.tagName||'').toLowerCase()==='iframe'){try{const d=e.contentDocument;if(d&&!known.has(d)){if(list.length>=MAX_ROOTS){truncated=true;break outer;}known.add(d);list.push(d);}}catch(_){}}}}const elapsed=Math.round(NOW()-t);return truncated?{success:false,reason:'SCAN_BUDGET_EXCEEDED',nodes:nodes,roots:list.length,elapsed:elapsed,list:list}:{success:true,nodes:nodes,roots:list.length,elapsed:elapsed,list:list};};";
}
