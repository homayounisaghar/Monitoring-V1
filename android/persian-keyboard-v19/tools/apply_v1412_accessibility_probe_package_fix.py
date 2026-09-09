from pathlib import Path

helper = Path('app/src/main/java/com/najme/perplexityprobe/SendAccessibilityService.java')
h = helper.read_text()

old = 'PersianKeyboardService.notifyAccessibilityProbe(pkg,type,event.getContentChangeTypes(),probeClass,probeId,'
new = 'PersianKeyboardService.notifyAccessibilityProbe(event.getPackageName()==null?null:event.getPackageName().toString(),type,event.getContentChangeTypes(),probeClass,probeId,'
count = h.count(old)
if count != 1:
    raise SystemExit(f'v1.41.2 build fix: expected one diagnostic package marker, found {count}')

h = h.replace(old, new, 1)
helper.write_text(h)
print('Applied v1.41 diagnostic accessibility package compile fix')
