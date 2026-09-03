package com.homayounisaghar.chatgptwebviewprobe;

/**
 * Production-facing semantic adapter for the active ChatGPT Dictation UI.
 *
 * Stable v0.20 real-device evidence identified two exact accessible controls:
 *   aria-label="Cancel dictation"
 *   aria-label="Submit dictation"
 *
 * The legacy classifier incorrectly treated generic "submit" as message SEND.
 * This adapter keeps active Dictation lifecycle semantics separate from message
 * sending and uses exact accessible labels only. No coordinates/XPath/private API.
 */
final class DictationActiveControlsV21 {
    static final String SUBMIT_LABEL = "Submit dictation";
    static final String CANCEL_LABEL = "Cancel dictation";

    private DictationActiveControlsV21() {}

    static String clickExactLabelJs(String label) {
        String target = js(label);
        return "(function(){try{" + COMMON_JS
                + "const target=N('" + target + "').toLowerCase();"
                + "const all=buttons();const xs=all.filter(e=>N(A(e,'aria-label')).toLowerCase()===target);"
                + "const out={matches:xs.length,visible_buttons:all.length,clicked:false};"
                + "if(xs.length===1){xs[0].click();out.clicked=true;}"
                + "return JSON.stringify(out);"
                + "}catch(e){return JSON.stringify({matches:-1,visible_buttons:-1,clicked:false,error:String(e&&e.name||'ERR')});}})();";
    }

    static String stateJs() {
        return "(function(){try{" + COMMON_JS
                + "const all=buttons();"
                + "const aria=e=>N(A(e,'aria-label')).toLowerCase();"
                + "const submit=all.filter(e=>aria(e)==='submit dictation').length;"
                + "const cancel=all.filter(e=>aria(e)==='cancel dictation').length;"
                + "const ready=all.filter(e=>{const a=aria(e);if(a==='submit dictation'||a==='cancel dictation')return false;const z=(a+' '+N(A(e,'title'))+' '+N(A(e,'data-testid'))).toLowerCase();return /microphone|dictat|voice input|record audio|record message/.test(z);}).length;"
                + "const users=[...document.querySelectorAll('[data-message-author-role=user]')].length;"
                + "return JSON.stringify({success:true,submit_count:submit,cancel_count:cancel,ready_dictation_count:ready,user_turn_count:users,visible_buttons:all.length});"
                + "}catch(e){return JSON.stringify({success:false,error:String(e&&e.name||'ERR')});}})();";
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
            + "const roots=[];const seen=new Set();"
            + "const walk=(root)=>{if(!root||seen.has(root))return;seen.add(root);roots.push(root);let es=[];try{es=[...root.querySelectorAll('*')];}catch(_){}for(const e of es){try{if(e.shadowRoot)walk(e.shadowRoot);}catch(_){}if((e.tagName||'').toLowerCase()==='iframe'){try{if(e.contentDocument)walk(e.contentDocument);}catch(_){}}}};"
            + "walk(document);"
            + "const buttons=()=>{const out=[];const d=new Set();for(const r of roots){let xs=[];try{xs=[...r.querySelectorAll('button,[role=button]')];}catch(_){}for(const e of xs){if(!d.has(e)&&V(e)){d.add(e);out.push(e);}}}return out;};";
}
