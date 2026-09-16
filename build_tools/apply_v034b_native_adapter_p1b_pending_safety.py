import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
store_path = root / "app/src/main/java/com/pebblebridge/poc/NativeAdapterProofStore.java"
s = store_path.read_text()
old = '''    public static boolean isPending(Context c) {\n        String s = state(c);\n        return WAITING_NOTIFICATION.equals(s) || CANDIDATE_CAPTURED.equals(s) || VERIFYING.equals(s);\n    }\n'''
new = '''    public static boolean isPending(Context c) {\n        String s = state(c);\n        return WAITING_NOTIFICATION.equals(s) || CANDIDATE_CAPTURED.equals(s) || VERIFYING.equals(s) ||\n                WAITING_SEMANTIC_SEND.equals(s) || SEND_DISPATCHED.equals(s);\n    }\n'''
if old not in s:
    raise SystemExit("P1b isPending baseline not found")
s = s.replace(old, new, 1)
store_path.write_text(s)
assert 'WAITING_SEMANTIC_SEND.equals(s)' in s
assert 'SEND_DISPATCHED.equals(s)' in s
