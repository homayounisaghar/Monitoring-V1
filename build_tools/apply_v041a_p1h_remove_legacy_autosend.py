import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
p = root / "app/src/main/java/com/pebblebridge/poc/NativeAdapterProofActivity.java"
s = p.read_text()

old = '                .appendQueryParameter("autosend", "true")\n'
if old in s:
    s = s.replace(old, "", 1)
    p.write_text(s)

# P1h must never depend on the rejected logged-in autosend contract.
assert 'appendQueryParameter("autosend"' not in s
assert 'appendQueryParameter("prompt", prompt)' in s
assert 'Start P1h conversationId binding proof' in s
