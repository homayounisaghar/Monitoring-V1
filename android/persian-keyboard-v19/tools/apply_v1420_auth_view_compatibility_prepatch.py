from pathlib import Path
import re

p=Path('app/src/main/java/com/najme/perplexityprobe/PersianKeyboardService.java')
s=p.read_text()
start=s.find('    @Override public View onCreateInputView()')
end=s.find('    private void buildToolbar()',start)
if start<0 or end<0:
    raise SystemExit('v1.42 prepatch: onCreateInputView region missing')
region=s[start:end]
pattern=re.compile(r'(?ms)^\s*auth\s*=\s*new WebView\(this\);.*?^\s*auth\.loadUrl\(START_URL\);\s*$')
m=pattern.search(region)
if not m:
    raise SystemExit('v1.42 prepatch: credential WebView creation block missing')
canonical='''        auth = new WebView(this);\n        auth.setAlpha(0.01f);\n        root.addView(auth, new LinearLayout.LayoutParams(1, 1));\n        configureWebView();\n        auth.loadUrl(START_URL);'''
region=region[:m.start()]+canonical+region[m.end():]
s=s[:start]+region+s[end:]
p.write_text(s)
print('Canonicalized v1.42 input-view auth block for resilient broker patch')
