import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
activity_path = root / "app/src/main/java/com/pebblebridge/poc/NativeAdapterProofActivity.java"
gradle_path = root / "app/build.gradle"

s = activity_path.read_text()

# P1b intentionally removed Notification Access as a prerequisite while isolating
# semantic Send. P1h needs it again because notification capture is now part of the
# binding proof. Restore both read-side prerequisites BEFORE any marker creation or
# ChatGPT launch, so a missing permission cannot consume a real Send side effect.
anchor = '''        if (!hasExactChatGptBuild()) {\n            NativeAdapterProofStore.fail(this, "Fail closed: P1h requires installed ChatGPT versionName exactly 1.2026.237.");\n            refreshUi();\n            return;\n        }\n'''
if anchor not in s:
    raise SystemExit("P1h exact-build start gate anchor missing")

gates = anchor + '''        if (!hasNotificationAccess()) {\n            NativeAdapterProofStore.fail(this, "Notification access is not enabled for Native Chat Adapter P1h. Grant it, return here, reset, and start again. No ChatGPT Send was attempted.");\n            refreshUi();\n            return;\n        }\n        if (!isAccessibilityVerifierEnabled()) {\n            NativeAdapterProofStore.fail(this, "Accessibility is not enabled for Native Chat Adapter P1h. Enable it, return here, reset, and start again. No ChatGPT Send was attempted.");\n            refreshUi();\n            return;\n        }\n'''
s = s.replace(anchor, gates, 1)
s = s.replace('adapterVersion: 0.41-native-adapter-p1h-notification-binding', 'adapterVersion: 0.42-native-adapter-p1h-notification-binding-guarded')
activity_path.write_text(s)

g = gradle_path.read_text()
g, n1 = re.subn(r'versionCode\s+41', 'versionCode 42', g, count=1)
g, n2 = re.subn(r'versionName\s+"0\.41-native-adapter-p1h-notification-binding"', 'versionName "0.42-native-adapter-p1h-notification-binding-guarded"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("Could not bump guarded P1h version metadata")
gradle_path.write_text(g)

s = activity_path.read_text()
start = s.index('    private void startProof() {')
marker = s.index('        String marker = NativeAdapterProofStore.start(this);', start)
prefix = s[start:marker]
assert prefix.index('hasExactChatGptBuild()') < prefix.index('hasNotificationAccess()') < prefix.index('isAccessibilityVerifierEnabled()')
assert 'No ChatGPT Send was attempted.' in prefix
assert 'appendQueryParameter("autosend"' not in s
assert 'versionCode 42' in g
assert 'versionName "0.42-native-adapter-p1h-notification-binding-guarded"' in g
