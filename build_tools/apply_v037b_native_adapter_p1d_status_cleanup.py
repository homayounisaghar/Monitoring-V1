import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
activity_path = root / "app/src/main/java/com/pebblebridge/poc/NativeAdapterProofActivity.java"

s = activity_path.read_text()
old = '''        String semanticSendNode = NativeAdapterProofStore.semanticSendNode(this);\n        if (!semanticSendNode.isEmpty()) b.append("semantic Send node = ").append(semanticSendNode).append('\\n');\n        if (NativeAdapterProofStore.SEND_CONFIRMED.equals(state)) {\n            b.append("\\nPASS: marker left the editable composer and appeared as a non-editable native chat message after the strict semantic Send action.\\n");\n        } else if (NativeAdapterProofStore.SEND_DISPATCHED.equals(state)) {\n            b.append("\\nSemantic Send ACTION_CLICK was accepted. Waiting for read-only confirmation that the marker became a sent message.\\n");\n        } else if (NativeAdapterProofStore.WAITING_SEMANTIC_SEND.equals(state)) {\n            b.append("\\nWaiting for the injected marker plus the exact semantic Send message control. No coordinate fallback exists.\\n");\n        }\n'''
if old not in s:
    raise SystemExit("Inherited P1b status block not found for cleanup")
s = s.replace(old, '', 1)
activity_path.write_text(s)

s = activity_path.read_text()
assert s.count('String semanticSendNode = NativeAdapterProofStore.semanticSendNode(this);') == 1
assert 'Semantic Send ACTION_CLICK was accepted' not in s
assert 'Start P1d IME submit proof' in s
