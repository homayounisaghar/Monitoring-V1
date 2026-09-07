from pathlib import Path
import re

p=Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
s=p.read_text()


def replace_method_body(text, signature, body, label):
    start=text.find(signature)
    if start<0:
        raise SystemExit(f'v1.35 selection decoupling: missing method: {label}')
    brace=text.find('{',start)
    if brace<0:
        raise SystemExit(f'v1.35 selection decoupling: missing opening brace: {label}')
    depth=0
    end=-1
    for i in range(brace,len(text)):
        c=text[i]
        if c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0:
                end=i+1
                break
    if end<0:
        raise SystemExit(f'v1.35 selection decoupling: missing closing brace: {label}')
    return text[:brace+1]+'\n'+body+'\n    }'+text[end:]


s=replace_method_body(
    s,
    'private void scheduleInternalSelectionReanchor()',
    '        // v1.35: deliberately disabled. Same-editor selection never forces the\n'
    '        // caret back to an IME-owned position.',
    'internal selection reanchor')

s=replace_method_body(
    s,
    'private void scheduleExternalSelectionConfirmation(int start,int end)',
    '        // v1.35: deliberately disabled. Selection is not a stop-causality signal.',
    'external selection confirmation')

# The main architecture patch was authored against the compact generated method
# signature. Later formatting-only patch history may leave whitespace around the
# switchToGboard signature. Normalize only that signature; do not move or rewrite
# the method body.
m=re.search(r'    private void switchToGboard\s*\(\s*\)\s*\{',s)
if not m:
    raise SystemExit('v1.35 selection decoupling: switchToGboard method missing')
s=s[:m.start()]+'    private void switchToGboard(){'+s[m.end():]

# Do not reject old call sites here: the main v1.35 architecture patch replaces
# onUpdateSelection entirely. The final workflow gate verifies that no active
# re-anchor/selection-stop call survives after the complete v1.35 patch chain.
for required in [
    'private void scheduleInternalSelectionReanchor(){',
    'private void scheduleExternalSelectionConfirmation(int start,int end){',
    'private void switchToGboard(){',
    'deliberately disabled',
]:
    if required not in s:
        raise SystemExit(f'v1.35 selection decoupling: invariant missing: {required}')

p.write_text(s)
print('Applied v1.35 selection causality decoupling prepatch')
