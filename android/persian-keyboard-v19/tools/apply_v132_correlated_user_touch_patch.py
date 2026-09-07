from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
helper = Path('app/src/main/java/com/najme/perplexityprobe/SendAccessibilityService.java')
accessibility_xml = Path('app/src/main/res/xml/send_accessibility_service.xml')
gradle_file = Path('app/build.gradle')

s = service.read_text()
h = helper.read_text()
a = accessibility_xml.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.32 patch: missing pattern: {label}')
    return text.replace(old, new, 1)


# v1.31 still produced "selection after user interaction" while the user had not
# touched the screen at all. The v1.31 attribution gate accepted either an
# onUpdateEditorToolType callback OR a system touch event by itself, and it also
# timestamped Accessibility delivery time rather than the original event time.
# That makes replayed/stale editor-tool callbacks and delayed delivery of the
# touch that started voice capable of authorizing a false stop.
#
# v1.32 requires correlation instead of OR:
# - only TYPE_TOUCH_INTERACTION_START participates;
# - store AccessibilityEvent.getEventTime(), not callback-delivery uptime;
# - the touch generation and event time must both be newer than this voice run;
# - onUpdateEditorToolType must occur after that same touch and within 700 ms;
# - neither signal alone may authorize a selection stop.

s = rep(s,
'''    private boolean hasRecentEditorUserInteraction(){
        long now=android.os.SystemClock.uptimeMillis();
        if(!running||voiceStartedUptime<=0L||now-voiceStartedUptime<300L)return false;
        if(lastEditorToolInteractionUptime>voiceStartedUptime+200L
                &&now>=lastEditorToolInteractionUptime
                &&now-lastEditorToolInteractionUptime<=1200L)return true;
        long touchGeneration=SendAccessibilityService.userTouchGeneration();
        long touchUptime=SendAccessibilityService.latestUserTouchUptime();
        return touchGeneration>voiceStartTouchGeneration
                &&touchUptime>voiceStartedUptime+200L
                &&now>=touchUptime
                &&now-touchUptime<=1200L;
    }
''',
'''    private boolean hasRecentEditorUserInteraction(){
        long now=android.os.SystemClock.uptimeMillis();
        if(!running||voiceStartedUptime<=0L||now-voiceStartedUptime<300L)return false;

        long touchGeneration=SendAccessibilityService.userTouchGeneration();
        long touchEventTime=SendAccessibilityService.latestUserTouchEventTime();
        if(touchGeneration<=voiceStartTouchGeneration
                ||touchEventTime<=voiceStartedUptime+200L
                ||now<touchEventTime
                ||now-touchEventTime>1000L)return false;

        // onUpdateEditorToolType is no longer trusted on its own. It must be a
        // near-immediate consequence of the same fresh system touch-start event.
        if(lastEditorToolInteractionUptime<=voiceStartedUptime+200L
                ||now<lastEditorToolInteractionUptime
                ||now-lastEditorToolInteractionUptime>1000L)return false;
        long correlation=lastEditorToolInteractionUptime-touchEventTime;
        return correlation>=0L&&correlation<=700L;
    }
''', 'replace OR attribution with correlated fresh touch plus editor click')

s = rep(s,
'''            setStatus("Voice stopped — selection after user interaction");
''',
'''            setStatus("Voice stopped — selection after fresh touch+editor click");
''', 'make correlated stop diagnostic explicit')

h = rep(h,
'''    private static volatile long latestUserTouchUptime;
    private static volatile long userTouchGeneration;
''',
'''    private static volatile long latestUserTouchEventTime;
    private static volatile long userTouchGeneration;
''', 'store original touch event time')

h = rep(h,
'''    public static long latestUserTouchUptime() {
        return latestUserTouchUptime;
    }
''',
'''    public static long latestUserTouchEventTime() {
        return latestUserTouchEventTime;
    }
''', 'rename touch time accessor')

h = rep(h,
'''        if(type==AccessibilityEvent.TYPE_TOUCH_INTERACTION_START){
            latestUserTouchUptime=android.os.SystemClock.uptimeMillis();
            userTouchGeneration++;
        }else if(type==AccessibilityEvent.TYPE_TOUCH_INTERACTION_END){
            latestUserTouchUptime=android.os.SystemClock.uptimeMillis();
        }
''',
'''        if(type==AccessibilityEvent.TYPE_TOUCH_INTERACTION_START){
            // Use the time the system says the touch happened, not when this
            // AccessibilityService happened to receive the event. A delayed
            // callback for the mic-start tap must never look like a new touch.
            latestUserTouchEventTime=event.getEventTime();
            userTouchGeneration++;
        }
''', 'use source event time and ignore touch end')

a = rep(a,
'''    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged|typeViewFocused|typeTouchInteractionStart|typeTouchInteractionEnd"
''',
'''    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged|typeViewFocused|typeTouchInteractionStart"
''', 'subscribe only to touch start for attribution')

if 'versionCode 41' not in g or "versionName '1.31'" not in g:
    raise SystemExit('v1.32 patch: expected v1.31 version markers missing')
g = g.replace('versionCode 41', 'versionCode 42', 1)
g = g.replace("versionName '1.31'", "versionName '1.32'", 1)

text = s + '\n' + h + '\n' + a + '\n' + g
required = [
    'private boolean hasRecentEditorUserInteraction(){',
    'long touchEventTime=SendAccessibilityService.latestUserTouchEventTime();',
    'touchGeneration<=voiceStartTouchGeneration',
    'touchEventTime<=voiceStartedUptime+200L',
    'long correlation=lastEditorToolInteractionUptime-touchEventTime;',
    'correlation>=0L&&correlation<=700L',
    'Voice stopped — selection after fresh touch+editor click',
    'private static volatile long latestUserTouchEventTime;',
    'public static long latestUserTouchEventTime()',
    'latestUserTouchEventTime=event.getEventTime();',
    'typeWindowStateChanged|typeWindowContentChanged|typeViewFocused|typeTouchInteractionStart',
    'versionCode 42',
    "versionName '1.32'",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'v1.32 patch: required invariant missing: {needle}')

for forbidden in [
    'SendAccessibilityService.latestUserTouchUptime()',
    'private static volatile long latestUserTouchUptime;',
    'TYPE_TOUCH_INTERACTION_END',
    'typeTouchInteractionEnd',
    'setStatus("Voice stopped — selection after user interaction");',
    'MAX_CAPTURE_MS',
    'boundConnection.setComposingText(partial,1);',
    'versionCode 41',
    "versionName '1.31'",
]:
    if forbidden in text:
        raise SystemExit(f'v1.32 patch: forbidden old behavior remains: {needle}')

service.write_text(s)
helper.write_text(h)
accessibility_xml.write_text(a)
gradle_file.write_text(g)
print('Applied Persian keyboard v1.32 correlated user-touch attribution patch')
