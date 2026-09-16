import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
activity_path = root / "app/src/main/java/com/pebblebridge/poc/NativeAdapterProofActivity.java"
gradle_path = root / "app/build.gradle"

s = activity_path.read_text()

# P1 real-device feedback showed that the deep link opened a new chat and
# populated the composer, but the harness forced itself back to foreground
# after 1.8 s. P1a removes that interference completely so autosend can be
# observed in isolation.
s = s.replace('    private static final long RETURN_DELAY_MS = 1800L;\n', '')

forced_return = '''        // Move ChatGPT out of the foreground shortly after the software-addressed
        // autosend is handed off, so its normal response notification path can fire.
        handler.postDelayed(() -> {
            if (!NativeAdapterProofStore.isAwaitingNotification(this)) return;
            try {
                Intent back = new Intent(this, NativeAdapterProofActivity.class);
                back.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_SINGLE_TOP);
                startActivity(back);
            } catch (Exception ignored) {
                // If Android blocks the short background return, the user can simply
                // return to the Bridge app manually; the notification listener remains active.
            }
        }, RETURN_DELAY_MS);
'''
if forced_return not in s:
    raise SystemExit("P1 forced-return block not found")
s = s.replace(
    forced_return,
    '''        // P1a intentionally leaves ChatGPT in the foreground. Do not interrupt
        // the app while its own deep-link autosend pipeline decides whether to submit.
        // The user returns to this companion manually after observing the result.
''',
    1,
)

s = s.replace('title.setText("Native Chat Adapter P1");', 'title.setText("Native Chat Adapter P1a");', 1)
s = s.replace(
    'subtitle.setText("APK-derived proof: deep-link autosend -> notification conversationId -> direct /c/<id> -> read-only receipt verification. No Search, coordinate tap, or write-side Accessibility is used.");',
    'subtitle.setText("Autosend-isolation proof. ChatGPT is opened by the APK-derived deep link and is NOT forced back to this app. Stay in ChatGPT long enough to see whether the draft actually sends, then return here manually.");',
    1,
)
s = s.replace('startButton.setText("Start native adapter proof");', 'startButton.setText("Start P1a autosend proof");', 1)
s = s.replace(
    'String prompt = "Native adapter proof. Reply with exactly this marker and no other text: " + marker;',
    'String prompt = "Native adapter P1a autosend proof. Reply with exactly this marker and no other text: " + marker;',
    1,
)

activity_path.write_text(s)

# Give the isolation build its own explicit version.
g = gradle_path.read_text()
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 33', g, count=1)
g, n2 = re.subn(r'versionName\s+["\'][^"\']+["\']', 'versionName "0.33-native-adapter-p1a"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("Could not update P1a version metadata")
gradle_path.write_text(g)

assert "RETURN_DELAY_MS" not in s
assert "handler.postDelayed(() ->" not in s
assert "Native Chat Adapter P1a" in s
assert "Start P1a autosend proof" in s
assert "versionCode 33" in g
assert 'versionName "0.33-native-adapter-p1a"' in g
