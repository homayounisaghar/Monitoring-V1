#!/usr/bin/env python3
from pathlib import Path
import runpy

runpy.run_path("ci/generate_chatgpt_webview_v48_transactional_receipt.py", run_name="__main__")

p=Path("runtime_probes/chatgpt-webview-stable-probe/app/src/main/java/com/homayounisaghar/chatgptwebviewprobe/OrchestratorPaidModelEffortTransactionalReceiptV48Activity.java")
s=p.read_text()

bad="    private int popupToggleDispatches47 = 0;\n        independentLightReceipt47 = false;\n    private boolean independentLightReceipt47 = false;"
good="    private int popupToggleDispatches47 = 0;\n    private boolean independentLightReceipt47 = false;"
assert bad in s, "expected misplaced independentLightReceipt47 reset not found"
s=s.replace(bad,good,1)

reset_anchor="        popupToggleDispatches47 = 0;\n        if (run47 != null)"
reset_fixed="        popupToggleDispatches47 = 0;\n        independentLightReceipt47 = false;\n        if (run47 != null)"
assert reset_anchor in s, "run reset anchor not found"
s=s.replace(reset_anchor,reset_fixed,1)

p.write_text(s)
print("PASS fixed v0.46 transactional generated Java reset placement")
