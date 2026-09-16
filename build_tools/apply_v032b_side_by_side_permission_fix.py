import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
p = root / "app/src/main/java/com/pebblebridge/poc/NativeAdapterProofActivity.java"
s = p.read_text()

old_notification = '''    private boolean hasNotificationAccess() {\n        String flat = Settings.Secure.getString(\n                getContentResolver(), Settings.Secure.ENABLED_NOTIFICATION_LISTENERS);\n        return flat != null && flat.contains(getPackageName());\n    }\n'''
new_notification = '''    private boolean hasNotificationAccess() {\n        String flat = Settings.Secure.getString(\n                getContentResolver(), "enabled_notification_listeners");\n        return flat != null && flat.contains(getPackageName());\n    }\n'''
if old_notification not in s:
    raise SystemExit("notification access block not found")
s = s.replace(old_notification, new_notification, 1)

old_accessibility = '''    private boolean isAccessibilityVerifierEnabled() {\n        String flat = Settings.Secure.getString(getContentResolver(), Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);\n        return flat != null && flat.contains(NativeProbeAccessibilityService.class.getName());\n    }\n'''
new_accessibility = '''    private boolean isAccessibilityVerifierEnabled() {\n        String flat = Settings.Secure.getString(\n                getContentResolver(), Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);\n        String exact = new ComponentName(this, NativeProbeAccessibilityService.class).flattenToString();\n        return flat != null && flat.contains(exact);\n    }\n'''
if old_accessibility not in s:
    raise SystemExit("accessibility verifier block not found")
s = s.replace(old_accessibility, new_accessibility, 1)

p.write_text(s)
assert '"enabled_notification_listeners"' in s
assert 'flattenToString()' in s
assert 'ENABLED_NOTIFICATION_LISTENERS' not in s
