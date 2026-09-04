import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
p = root / "app/src/main/java/com/pebblebridge/poc/NativeAdapterProofStore.java"
s = p.read_text()

# P1b already added semanticSendConfirmed(Context), backed by the exact same
# SharedPreferences key used by P1h. P1h only needs to write that existing key.
# Remove solely the duplicate reader inserted immediately before the new
# notificationBindArmedAt() accessor; keep the original P1b reader intact.
needle = '''    public static boolean semanticSendConfirmed(Context c) {\n        return p(c).getBoolean("semanticSendConfirmed", false);\n    }\n\n    public static long notificationBindArmedAt(Context c) {\n'''
replacement = '''    public static long notificationBindArmedAt(Context c) {\n'''
if needle not in s:
    raise SystemExit("P1h duplicate semanticSendConfirmed block not found at the expected notification binding anchor")
s = s.replace(needle, replacement, 1)
p.write_text(s)

assert s.count('public static boolean semanticSendConfirmed(Context c)') == 1
assert 'public static long notificationBindArmedAt(Context c)' in s
assert '.putBoolean("semanticSendConfirmed", true)' in s
assert '.putString("state", WAITING_NOTIFICATION)' in s
