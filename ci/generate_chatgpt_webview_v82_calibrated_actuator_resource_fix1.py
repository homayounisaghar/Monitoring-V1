#!/usr/bin/env python3
from pathlib import Path

# Mechanical audit repair only: each native tap contains ACTION_DOWN + ACTION_UP.
# v0.80 has one benign calibration tap and one certified Resource tap, therefore
# the generated Activity contains four dispatchTouchEvent calls, not two.
p=Path('ci/generate_chatgpt_webview_v82_calibrated_actuator_resource.py')
s=p.read_text()
old="assert out.count('dispatchTouchEvent(')==2,out.count('dispatchTouchEvent(')"
new="assert out.count('dispatchTouchEvent(')==4,out.count('dispatchTouchEvent(')"
assert s.count(old)==1,s.count(old)
s=s.replace(old,new,1)
exec(compile(s,str(p), 'exec'), {'__name__':'__main__','__file__':str(p)})
print('PASS v0.80 fix1: mechanical dispatchTouchEvent audit count corrected; architecture unchanged')
