package com.homayounisaghar.chatgptwebviewprobe;

import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

/**
 * v0.49 model-trigger observer. This service performs no UI actions.
 * It records only bounded, privacy-safe fingerprints from a human click event.
 */
public class ControlPlaneAccessibilityServiceV51 extends ControlPlaneAccessibilityServiceV50 {
    private static volatile ControlPlaneAccessibilityServiceV51 INSTANCE51;
    private static volatile boolean ARMED = false;
    private static volatile int observedEvents = 0;
    private static volatile int clickedEvents = 0;
    private static volatile long armedAt = 0L;
    private static volatile long lastClickAt = 0L;
    private static volatile String lastSourceHash = "-";
    private static volatile String lastSourceSemantic = "NONE";
    private static volatile String lastNearestModelHash = "-";
    private static volatile String lastNearestModelSemantic = "NONE";
    private static volatile String lastSourceClassHash = "-";
    private static volatile String lastActionSetHash = "-";
    private static volatile String lastAncestryHash = "-";
    private static volatile boolean lastSourceClickable = false;
    private static volatile boolean lastSourceSelected = false;
    private static volatile int lastEventType = -1;

    @Override protected void onServiceConnected() {
        super.onServiceConnected();
        INSTANCE51 = this;
    }

    @Override public void onDestroy() {
        if (INSTANCE51 == this) INSTANCE51 = null;
        super.onDestroy();
    }

    private static String cs(CharSequence x) { return x == null ? "" : x.toString(); }
    private static String norm(String x) {
        if (x == null) return "";
        return x.replace('\u00a0',' ').replaceAll("\\s+"," ").trim().toLowerCase(Locale.ROOT);
    }
    private static String join(String... xs) {
        StringBuilder b = new StringBuilder();
        for (String x : xs) { String n=x==null?"":x.trim(); if(n.isEmpty())continue; if(b.length()>0)b.append(' '); b.append(n); }
        return b.toString();
    }
    private static String fnv(String s) {
        long h=0x811c9dc5L; for(int i=0;i<s.length();i++){h^=s.charAt(i);h=(h*0x01000193L)&0xffffffffL;}
        return String.format(Locale.ROOT,"%08x",h);
    }
    private static String sem(String raw) {
        String s=norm(raw);
        if(s.equals("latest")||s.startsWith("latest ")||s.endsWith(" latest")) return "LATEST";
        if(s.contains("gpt-5.6 sol")||s.contains("gpt 5.6 sol")) return "GPT56_SOL";
        if(s.contains("gpt-5.5")||s.contains("gpt 5.5")) return "GPT55";
        return "NONE";
    }
    private static String label(AccessibilityNodeInfo n) {
        if(n==null)return "";
        return norm(join(cs(n.getText()),cs(n.getContentDescription()),cs(n.getHintText()),cs(n.getStateDescription())));
    }
    private static String actionHash(AccessibilityNodeInfo n) {
        List<String> ids=new ArrayList<>();
        try { for(AccessibilityNodeInfo.AccessibilityAction a:n.getActionList()) if(a!=null) ids.add(String.valueOf(a.getId())); } catch(Exception ignored){}
        Collections.sort(ids); return fnv(joinList(ids));
    }
    private static String joinList(List<String> xs){StringBuilder b=new StringBuilder();for(String x:xs){if(b.length()>0)b.append(',');b.append(x);}return b.toString();}

    public static boolean isObserverReady(){ return INSTANCE51 != null; }

    public static synchronized JSONObject armManualModelClickObservation() {
        ARMED=true; observedEvents=0; clickedEvents=0; armedAt=System.currentTimeMillis(); lastClickAt=0L;
        lastSourceHash="-"; lastSourceSemantic="NONE"; lastNearestModelHash="-"; lastNearestModelSemantic="NONE";
        lastSourceClassHash="-"; lastActionSetHash="-"; lastAncestryHash="-"; lastSourceClickable=false; lastSourceSelected=false; lastEventType=-1;
        JSONObject o=new JSONObject(); put(o,"success",INSTANCE51!=null); put(o,"armed",ARMED); return o;
    }
    public static synchronized void disarmManualModelClickObservation(){ ARMED=false; }

    @Override public void onAccessibilityEvent(AccessibilityEvent event) {
        super.onAccessibilityEvent(event);
        if(!ARMED || event==null) return;
        int type=event.getEventType();
        if(type!=AccessibilityEvent.TYPE_VIEW_CLICKED && type!=AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED && type!=AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) return;
        observedEvents++;
        if(type!=AccessibilityEvent.TYPE_VIEW_CLICKED) return;
        AccessibilityNodeInfo src=null;
        try{src=event.getSource();}catch(Exception ignored){}
        if(src==null)return;
        clickedEvents++; lastClickAt=System.currentTimeMillis(); lastEventType=type;
        String sl=label(src); lastSourceHash=sl.isEmpty()?"-":fnv(sl); lastSourceSemantic=sem(sl);
        lastSourceClassHash=fnv(norm(cs(src.getClassName()))); lastActionSetHash=actionHash(src);
        try{lastSourceClickable=src.isClickable();lastSourceSelected=src.isSelected()||src.isChecked();}catch(Exception ignored){}
        String nearestSem=lastSourceSemantic, nearestHash=lastSourceHash;
        List<String> ancestry=new ArrayList<>(); AccessibilityNodeInfo cur=src;
        for(int i=0;i<5 && cur!=null;i++){
            String l=label(cur), s=sem(l), cls=norm(cs(cur.getClassName())); boolean click=false;
            try{click=cur.isClickable();}catch(Exception ignored){}
            String lh=l.isEmpty()?"-":fnv(l); ancestry.add(i+"|"+fnv(cls)+"|"+lh+"|"+(click?1:0)+"|"+actionHash(cur));
            if("NONE".equals(nearestSem) && !"NONE".equals(s)){nearestSem=s;nearestHash=lh;}
            try{cur=cur.getParent();}catch(Exception e){cur=null;}
        }
        lastNearestModelSemantic=nearestSem; lastNearestModelHash=nearestHash; lastAncestryHash=fnv(joinList(ancestry));
    }

    public static synchronized JSONObject captureManualClickEvidence() {
        JSONObject o=new JSONObject();
        put(o,"success",INSTANCE51!=null); put(o,"armed",ARMED); put(o,"observed_event_count",observedEvents); put(o,"clicked_event_count",clickedEvents);
        put(o,"human_click_seen",clickedEvents>0 && lastClickAt>=armedAt); put(o,"last_event_type",lastEventType);
        put(o,"source_label_hash",lastSourceHash); put(o,"source_semantic",lastSourceSemantic); put(o,"nearest_model_hash",lastNearestModelHash); put(o,"nearest_model_semantic",lastNearestModelSemantic);
        put(o,"source_class_hash",lastSourceClassHash); put(o,"action_set_hash",lastActionSetHash); put(o,"ancestry_hash",lastAncestryHash);
        put(o,"source_clickable",lastSourceClickable); put(o,"source_selected",lastSourceSelected); put(o,"elapsed_since_arm_ms",armedAt==0?0:System.currentTimeMillis()-armedAt);
        return o;
    }
    private static void put(JSONObject o,String k,Object v){try{o.put(k,v);}catch(Exception ignored){}}
}
