#!/usr/bin/env python3
from pathlib import Path
import runpy

src=Path('ci/generate_chatgpt_webview_v73_planner_execution_hardening.py').read_text()
old="''',rettype='boolean')"
assert src.count(old)==1,src.count(old)
fixed=src.replace(old,"''')",1)
tmp=Path('/tmp/generate_chatgpt_webview_v73_planner_execution_hardening_fixed.py')
tmp.write_text(fixed)
runpy.run_path(str(tmp),run_name='__main__')
print('PASS v0.71 final wrapper')
