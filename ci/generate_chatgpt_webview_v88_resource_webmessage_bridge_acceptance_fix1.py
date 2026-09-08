#!/usr/bin/env python3
from pathlib import Path
import runpy

# Mechanical audit repair only. v0.86 authorizes Resource effect only through the
# same-task JS path. The generated Activity therefore retains exactly one benign
# native calibration tap (ACTION_DOWN + ACTION_UP) and no native Resource tap.
p=Path('ci/generate_chatgpt_webview_v88_resource_webmessage_bridge_acceptance.py')
s=p.read_text()
old="assert out.count('dispatchTouchEvent(')==4,out.count('dispatchTouchEvent(')"
new="assert out.count('dispatchTouchEvent(')==2,out.count('dispatchTouchEvent(')"
assert s.count(old)==1,s.count(old)
fixed=s.replace(old,new,1)
tmp=Path('/tmp/generate_chatgpt_webview_v88_resource_webmessage_bridge_acceptance_fix1_runtime.py')
tmp.write_text(fixed)
runpy.run_path(str(tmp),run_name='__main__')
print('PASS v0.86 fix1: native dispatch static count matches JS-only Resource effect architecture; behavior unchanged')
