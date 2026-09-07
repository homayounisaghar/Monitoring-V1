from pathlib import Path

service = Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
gradle_file = Path('app/build.gradle')
s = service.read_text()
g = gradle_file.read_text()


def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'v1.36 viewport patch: missing pattern: {label}')
    return text.replace(old, new, 1)


s = rep(s,
'''    private boolean voicePublicationPaused;\n''',
'''    private boolean voicePublicationPaused;\n    private boolean voiceSelectionFollowsOwnedRange;\n    private int voiceExpectedSelectionStart = -1;\n    private int voiceExpectedSelectionEnd = -1;\n''',
    'voice viewport-follow state')

s = rep(s,
'''        voicePublishedText="";voiceOwnedStart=-1;voiceOwnedEnd=-1;voicePublicationPaused=false;\n''',
'''        voicePublishedText="";voiceOwnedStart=-1;voiceOwnedEnd=-1;voicePublicationPaused=false;\n        voiceSelectionFollowsOwnedRange=false;voiceExpectedSelectionStart=-1;voiceExpectedSelectionEnd=-1;\n''',
    'reset viewport-follow state')

s = rep(s,
'''            voicePublishedText=selected;\n            voiceBoundaryCaptured=true;\n''',
'''            voicePublishedText=selected;\n            voiceSelectionFollowsOwnedRange=voiceOwnedStart>=0&&voiceOwnedEnd>=voiceOwnedStart;\n            voiceExpectedSelectionStart=voiceOwnedStart;\n            voiceExpectedSelectionEnd=voiceOwnedEnd;\n            voiceBoundaryCaptured=true;\n''',
    'capture expected initial selection')

s = rep(s,
'''            int oldSelStart=window.selectionStart;int oldSelEnd=window.selectionEnd;\n            int restoreStart=adjustSelectionAfterReplace(oldSelStart,editStart,editEnd,replacement.length());\n            int restoreEnd=adjustSelectionAfterReplace(oldSelEnd,editStart,editEnd,replacement.length());\n            boolean batch=false;boolean ok=false;\n''',
'''            int oldSelStart=window.selectionStart;int oldSelEnd=window.selectionEnd;\n            boolean followVoiceEnd=voiceSelectionFollowsOwnedRange\n                    &&oldSelStart==voiceExpectedSelectionStart&&oldSelEnd==voiceExpectedSelectionEnd;\n            if(voiceSelectionFollowsOwnedRange&&!followVoiceEnd)voiceSelectionFollowsOwnedRange=false;\n            int restoreStart=followVoiceEnd?-1:adjustSelectionAfterReplace(oldSelStart,editStart,editEnd,replacement.length());\n            int restoreEnd=followVoiceEnd?-1:adjustSelectionAfterReplace(oldSelEnd,editStart,editEnd,replacement.length());\n            boolean batch=false;boolean ok=false;\n''',
    'decide whether viewport should follow live voice end')

s = rep(s,
'''                int newOwnedEnd=region[0]+desired.length();\n                restoreStart=Math.max(0,restoreStart);restoreEnd=Math.max(restoreStart,restoreEnd);\n                ic.setSelection(restoreStart,restoreEnd);\n                voicePublishedText=desired;voiceOwnedStart=region[0];voiceOwnedEnd=newOwnedEnd;\n''',
'''                int newOwnedEnd=region[0]+desired.length();\n                if(followVoiceEnd){\n                    restoreStart=newOwnedEnd;restoreEnd=newOwnedEnd;\n                }else{\n                    restoreStart=Math.max(0,restoreStart);restoreEnd=Math.max(restoreStart,restoreEnd);\n                }\n                ic.setSelection(restoreStart,restoreEnd);\n                if(followVoiceEnd){\n                    voiceExpectedSelectionStart=newOwnedEnd;\n                    voiceExpectedSelectionEnd=newOwnedEnd;\n                }\n                voicePublishedText=desired;voiceOwnedStart=region[0];voiceOwnedEnd=newOwnedEnd;\n''',
    'restore live caret at voice end unless user/editor selection diverged')

if 'versionCode 45' not in g or "versionName '1.35'" not in g:
    raise SystemExit('v1.36 viewport patch: v1.35 Gradle version markers missing')
g = g.replace('versionCode 45', 'versionCode 46', 1)
g = g.replace("versionName '1.35'", "versionName '1.36'", 1)

required = [
    'private boolean voiceSelectionFollowsOwnedRange;',
    'private int voiceExpectedSelectionStart = -1;',
    'private int voiceExpectedSelectionEnd = -1;',
    'boolean followVoiceEnd=voiceSelectionFollowsOwnedRange',
    'restoreStart=newOwnedEnd;restoreEnd=newOwnedEnd;',
    'voiceExpectedSelectionStart=newOwnedEnd;',
    'voiceExpectedSelectionEnd=newOwnedEnd;',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'v1.36 viewport patch: invariant missing: {needle}')

for forbidden in [
    'scheduleInternalSelectionReanchor();',
    'scheduleExternalSelectionConfirmation(newSelStart,newSelEnd);',
    'Voice stopped — live text sync lost',
]:
    if forbidden in s:
        raise SystemExit(f'v1.36 viewport patch: forbidden legacy behavior present: {forbidden}')

service.write_text(s)
gradle_file.write_text(g)
print('Applied v1.36 follow-live-voice viewport patch')
