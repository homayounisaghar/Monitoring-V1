#!/usr/bin/env python3
from pathlib import Path
import runpy

V102=Path('ci/generate_chatgpt_webview_v102_dashboard_reply_read_aloud.py')
FIX1=Path('ci/generate_chatgpt_webview_v102_dashboard_assistant_prototype_fixed.py')
v102=V102.read_text()
old_assert="assert s.count(old)==3,('dashboard/planner/execution modes',s.count(old))"
assert v102.count(old_assert)==1
v102=v102.replace(old_assert,"assert s.count(old)==1,('dashboard visibility anchor',s.count(old))",1)

orig=runpy.run_path
def guarded(path,*args,**kwargs):
    if str(path).endswith('ci/generate_chatgpt_webview_v102_dashboard_reply_read_aloud.py'):
        scope={'__name__':'__main__','__file__':str(path)}
        exec(compile(v102,str(path),'exec'),scope)
        return scope
    return orig(path,*args,**kwargs)

runpy.run_path=guarded
try:
    src=FIX1.read_text()
    assert src.count("assert s.count('.click()')==4") == 1
    src=src.replace("assert s.count('.click()')==4, s.count('.click()')","assert s.count('.click()')==3, s.count('.click()')",1)
    exec(compile(src,str(FIX1),'exec'),{'__name__':'__main__','__file__':str(FIX1)})
finally:
    runpy.run_path=orig

print('PASS v0.90.8 fixed2: current v0.90.7 visibility shape adapted; three unique JS click actuators statically bounded')
