#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'
PKG.mkdir(parents=True,exist_ok=True)
prims=Path('ci/v94_planner_dom_primitives.java.inc').read_text()
assert 'private String plannerReadJs()' in prims and 'private String plannerSetDraftJs' in prims and 'private String plannerSendJs' in prims
# The v94 generator's first v74 call exists only to read three methods. Supply those from the
# frozen primitive snapshot, but allow all later v74 calls made by the normal v93 lineage.
frozen=prims.replace('private String plannerReadJs()','private String readJs()',1).replace('private String plannerSetDraftJs(String text)','private String setDraftJs(String text)',1).replace('private String plannerSendJs(String expectedHash)','private String sendJs(String expectedHash)',1)
(PKG/'OrchestratorPlannerCoreV74Activity.java').write_text('class FrozenV74PlannerPrimitives {\n'+frozen+'\n    private void eval(\n')
orig=runpy.run_path
first_v74=True
def guarded(path,*args,**kwargs):
    global first_v74
    if str(path).endswith('ci/generate_chatgpt_webview_v74_planner_format_repair.py') and first_v74:
        first_v74=False
        return {}
    return orig(path,*args,**kwargs)
runpy.run_path=guarded
try:
    p=Path('ci/generate_chatgpt_webview_v94_dashboard_stateless_planner_recipe_only.py')
    exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
finally:
    runpy.run_path=orig
print('PASS fixed v0.90.0 generator: first v74 read frozen; v93 lineage runs normally')
