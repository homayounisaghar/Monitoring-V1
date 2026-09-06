#!/usr/bin/env python3
from pathlib import Path
import runpy

# Generate the v0.60 source, then apply the one-line Java string-construction
# correction before compilation. This keeps the semantic contract unchanged.
runpy.run_path("ci/generate_chatgpt_webview_v62_temporary_chat_autonomous_roundtrip.py", run_name="__main__")

p=Path("runtime_probes/chatgpt-webview-stable-probe/app/src/main/java/com/homayounisaghar/chatgptwebviewprobe/OrchestratorTemporaryChatAutonomousRoundtripV62Activity.java")
s=p.read_text()
old='"const EL=\'"+expectedLabel+"\',ES=\'"+expectedStruct+"\',FROM=\'"+expectedFrom+"\',EU="+("+expectedUrl+"?\'true\':\'false\')+";"+'
new='"const EL=\'"+expectedLabel+"\',ES=\'"+expectedStruct+"\',FROM=\'"+expectedFrom+"\',EU="+(expectedUrl?"true":"false")+";"+'
assert old in s, "expected v0.60 Java string-construction line not found"
p.write_text(s.replace(old,new,1))
