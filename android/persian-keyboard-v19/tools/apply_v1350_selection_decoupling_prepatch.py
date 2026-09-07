from pathlib import Path

p=Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
s=p.read_text()

start=s.find('    private void scheduleInternalSelectionReanchor(){')
end=s.find('    @Override public void onUpdateEditorToolType',start)
if start<0 or end<0:
    raise SystemExit('v1.35 selection decoupling: legacy helper region not found')

replacement='''    private void scheduleInternalSelectionReanchor(){\n        // v1.35: deliberately disabled. Same-editor selection never forces the\n        // caret back to an IME-owned position.\n    }\n\n    private void scheduleExternalSelectionConfirmation(int start,int end){\n        // v1.35: deliberately disabled. Selection is not a stop-causality signal.\n    }\n\n'''
s=s[:start]+replacement+s[end:]

for forbidden in [
    'scheduleInternalSelectionReanchor();',
    'stopVoiceForManualInput();\n            setStatus("Voice stopped — selection',
]:
    if forbidden in s:
        raise SystemExit(f'v1.35 selection decoupling: legacy causality remains: {forbidden}')

for required in [
    'private void scheduleInternalSelectionReanchor(){',
    'private void scheduleExternalSelectionConfirmation(int start,int end){',
    'deliberately disabled',
]:
    if required not in s:
        raise SystemExit(f'v1.35 selection decoupling: invariant missing: {required}')

p.write_text(s)
print('Applied v1.35 selection causality decoupling prepatch')
