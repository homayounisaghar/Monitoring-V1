#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess

subprocess.run(['python3', 'ci/generate_chatgpt_webview_v44_aria_controls.py'], check=True)

root = Path('runtime_probes/chatgpt-webview-stable-probe')
gradle = root / 'app/build.gradle'

g = gradle.read_text()
g = g.replace("applicationId 'com.homayounisaghar.chatgptwebviewprobe.v44diag'", "applicationId 'com.homayounisaghar.chatgptwebviewprobe.v44compat'")
g = re.sub(r'minSdk\s+\d+', 'minSdk 23', g)
g = re.sub(r'versionCode\s+\d+', 'versionCode 46', g)
g = re.sub(r"versionName\s+'[^']+'", "versionName '0.42.1-compat-paid-model-effort-aria-controls-target-census'", g)
gradle.write_text(g)

print('V44_COMPAT_GENERATED package=com.homayounisaghar.chatgptwebviewprobe.v44compat minSdk=23 versionCode=46 signatures=v1+v2+v3')
