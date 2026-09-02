from pathlib import Path
import runpy

build = Path('runtime_probes/native-capability-lab/app/build.gradle')
text = build.read_text()
old = "versionName '0.16-native-capability-lab-stable-index-trigger-ladder'"
if old in text:
    text = text.replace(old, 'versionName "0.16-native-capability-lab-stable-index-trigger-ladder"', 1)
    build.write_text(text)
runpy.run_path('build_tools/apply_capability_lab_v17_fresh_history_binding.py', run_name='__main__')
