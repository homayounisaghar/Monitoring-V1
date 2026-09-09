from pathlib import Path
import re

xml_path = Path('app/src/main/res/xml/send_accessibility_service.xml')
a = xml_path.read_text()

m = re.search(r'android:accessibilityEventTypes="([^"]*)"', a)
if not m:
    raise SystemExit('v1.41.1 build fix: accessibilityEventTypes attribute missing')

types = [t for t in m.group(1).split('|') if t]
for event_type in ('typeViewTextChanged', 'typeViewTextSelectionChanged'):
    if event_type not in types:
        types.append(event_type)

new_value = '|'.join(types)
a = a[:m.start(1)] + new_value + a[m.end(1):]

for required in ('typeViewTextChanged', 'typeViewTextSelectionChanged'):
    if required not in a:
        raise SystemExit(f'v1.41.1 build fix: missing event type after update: {required}')

xml_path.write_text(a)
print('Applied v1.41 accessibility event subscription build fix')
