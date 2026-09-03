package com.homayounisaghar.chatgptwebviewprobe;

/**
 * Stable v0.22 production-facing DOM adapter for ChatGPT Dictation lifecycle.
 *
 * Proven real-device semantics from v0.20/v0.21:
 *   active cancel = aria-label="Cancel dictation"
 *   active finish = aria-label="Submit dictation"
 *
 * This adapter intentionally keeps active Dictation "Submit" separate from
 * generic ChatGPT message Send. It uses semantic/accessible metadata only,
 * traverses the main document, open shadow roots and accessible same-origin
 * frames, and never uses coordinates, XPath, private ChatGPT APIs or cookies.
 */
final class DictationLifecycleAdapterV22 {
    static final String SUBMIT_LABEL = "Submit dictation";
    static final String CANCEL_LABEL = "Cancel dictation";

    private DictationLifecycleAdapterV22() {}

    static String clickSubmitJs() { return clickExactLabelJs(SUBMIT_LABEL); }
    static String clickCancelJs() { return clickExactLabelJs(CANCEL_LABEL); }

    static String clickExactLabelJs(String label) {
        String target = js(label);
        return "(function(){try{" + COMMON_JS
                + "const target=N('" + target + "').toLowerCase();"
                + "const all=buttons();const xs=all.filter(e=>N(A(e,'aria-label')).toLowerCase()===target);"
                + "const out={success:true,matches:xs.length,visible_buttons:all.length,clicked:false};"
                + "if(xs.length===1){xs[0].click();out.clicked=true;}"
                + "return JSON.stringify(out);"
                + "}catch(e){return JSON.stringify({success:false,matches:-1,visible_buttons:-1,clicked:false,error:String(e&&e.name||'ERR')});}})();";
    }

    /** Privacy-bounded state: raw composer/chat text is not returned. */
    static String stateJs() {
        return "(function(){try{" + COMMON_JS
                + "const all=buttons();"
                + "const aria=e=>N(A(e,'aria-label')).toLowerCase();"
                + "const submit=all.filter(e=>aria(e)==='submit dictation').length;"
                + "const cancel=all.filter(e=>aria(e)==='cancel dictation').length;"
                + "const ready=all.filter(e=>{const a=aria(e);if(a==='submit dictation'||a==='cancel dictation')return false;const z=(a+' '+N(A(e,'title'))+' '+N(A(e,'data-testid'))).toLowerCase();return /microphone|dictat|voice input|record audio|record message/.test(z);}).length;"
                + "const users=[...document.querySelectorAll('[data-message-author-role=user]')].length;"
                + "const ed=[...document.querySelectorAll('#prompt-textarea,textarea,[contenteditable=true]')].filter(V);"
                + "const ce=ed.length?ed[ed.length-1]:null;"
                + "const raw=ce?N(typeof ce.value==='string'?ce.value:(ce.innerText||ce.textContent||'')):'';"
                + "let send=0;for(const e of all){const a=aria(e),t=N(A(e,'title')).toLowerCase(),id=N(A(e,'data-testid')).toLowerCase();if(a==='submit dictation'||a==='cancel dictation')continue;const z=a+' '+t+' '+id;if(/(^| )send( message)?($| )|send-button|composer-submit/.test(z))send++;}"
                + "return JSON.stringify({success:true,submit_count:submit,cancel_count:cancel,ready_dictation_count:ready,user_turn_count:users,composer_len:raw.length,composer_hash:raw?H(raw):'-',message_send_count:send,visible_buttons:all.length,raw_chat_text_returned:false,raw_composer_text_returned:false});"
                + "}catch(e){return JSON.stringify({success:false,error:String(e&&e.name||'ERR'),raw_chat_text_returned:false,raw_composer_text_returned:false});}})();";
    }

    private static String js(String s) {
        return (s == null ? "" : s)
                .replace("\\", "\\\\")
                .replace("'", "\\'")
                .replace("\n", "\\n")
                .replace("\r", "\\r");
    }

    private static final String COMMON_JS =
            "const N=s=>String(s==null?'':s).replace(/\\s+/g,' ').trim();"
            + "const A=(e,n)=>{try{return String(e&&e.getAttribute?e.getAttribute(n)||'':'');}catch(_){return '';}};"
            + "const V=e=>{try{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}catch(_){return false;}};"
            + "const H=s=>{let h=2166136261>>>0;for(let i=0;i<String(s).length;i++){h^=String(s).charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return('00000000'+h.toString(16)).slice(-8);};"
            + "const roots=[];const seen=new Set();"
            + "const walk=root=>{if(!root||seen.has(root))return;seen.add(root);roots.push(root);let es=[];try{es=[...root.querySelectorAll('*')];}catch(_){}for(const e of es){try{if(e.shadowRoot)walk(e.shadowRoot);}catch(_){}if((e.tagName||'').toLowerCase()==='iframe'){try{if(e.contentDocument)walk(e.contentDocument);}catch(_){}}}};"
            + "walk(document);"
            + "const buttons=()=>{const out=[];const d=new Set();for(const r of roots){let xs=[];try{xs=[...r.querySelectorAll('button,[role=button]')];}catch(_){}for(const e of xs){if(!d.has(e)&&V(e)){d.add(e);out.push(e);}}}return out;};";
}
