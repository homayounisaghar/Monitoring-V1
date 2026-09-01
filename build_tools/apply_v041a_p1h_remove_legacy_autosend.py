import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
p = root / "app/src/main/java/com/pebblebridge/poc/NativeAdapterProofActivity.java"
s = p.read_text()

old = '                .appendQueryParameter("autosend", "true")\n'
if old not in s:
    raise SystemExit("P1h expected legacy autosend query line was not found")
s = s.replace(old, "", 1)
p.write_text(s)

assert 'appendQueryParameter("autosend"' not in s
assert 'appendQueryParameter("prompt", prompt)' in s
assert 'Start P1h conversationId binding proof' in s
