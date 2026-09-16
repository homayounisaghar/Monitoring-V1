import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
p = root / "app/src/main/java/com/pebblebridge/poc/NativeAdapterProofActivity.java"
s = p.read_text()

s = s.replace("import android.app.NotificationManager;\n", "")
s = s.replace("import android.os.Build;\n", "")
s = s.replace("import java.util.Set;\n", "")

old = '''    private boolean hasNotificationAccess() {\n        if (Build.VERSION.SDK_INT >= 27) {\n            Set<String> enabled = NotificationManager.getEnabledListenerPackages(this);\n            return enabled.contains(getPackageName());\n        }\n        String flat = Settings.Secure.getString(getContentResolver(), "enabled_notification_listeners");\n        return flat != null && flat.contains(getPackageName());\n    }\n'''
new = '''    private boolean hasNotificationAccess() {\n        String flat = Settings.Secure.getString(\n                getContentResolver(), Settings.Secure.ENABLED_NOTIFICATION_LISTENERS);\n        return flat != null && flat.contains(getPackageName());\n    }\n'''
if old not in s:
    raise SystemExit("notification access block not found")
s = s.replace(old, new, 1)
p.write_text(s)

assert "getEnabledListenerPackages" not in s
assert "ENABLED_NOTIFICATION_LISTENERS" in s
