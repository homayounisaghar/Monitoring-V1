import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ci/src")
java_dir = root / "app/src/main/java/com/pebblebridge/poc"
activity_path = java_dir / "NativeAdapterProofActivity.java"
store_path = java_dir / "NativeAdapterProofStore.java"
service_path = java_dir / "NativeProbeAccessibilityService.java"
manifest_path = root / "app/src/main/AndroidManifest.xml"
gradle_path = root / "app/build.gradle"

# P1f keeps the P1e read-only manual-Send tracer but makes the evidence portable.
# It also preserves the click-source chain separately so high-volume content-change
# events cannot evict the most valuable evidence from the rolling trace buffer.

# ---- store: larger buffers + durable click summary ----------------------
store = store_path.read_text()
store = store.replace(
    '.putString("manualAfter", "")\n                .putBoolean("manualBaselineCaptured", false)',
    '.putString("manualAfter", "")\n                .putString("manualClickSummary", "")\n                .putBoolean("manualBaselineCaptured", false)',
    1,
)
store = store.replace(
    'if (next.length() > 30000) next = "...[older trace truncated]\\n" + next.substring(next.length() - 28000);',
    'if (next.length() > 240000) next = "...[older trace truncated]\\n" + next.substring(next.length() - 220000);',
    1,
)
store = store.replace(
    'if (safe.length() > 14000) safe = safe.substring(0, 14000) + "\\n...[truncated]";',
    'if (safe.length() > 80000) safe = safe.substring(0, 80000) + "\\n...[truncated]";',
    2,
)
getter_anchor = '    public static String manualAfter(Context c) { return p(c).getString("manualAfter", ""); }\n'
if getter_anchor not in store:
    raise SystemExit("P1f manualAfter getter anchor missing")
store = store.replace(
    getter_anchor,
    getter_anchor + '''    public static String manualClickSummary(Context c) { return p(c).getString("manualClickSummary", ""); }\n\n    public static void recordManualClickSummary(Context c, String summary) {\n        String safe = summary == null ? "" : summary;\n        if (safe.length() > 60000) safe = safe.substring(0, 60000) + "\\n...[truncated]";\n        p(c).edit().putString("manualClickSummary", safe).apply();\n    }\n''',
    1,
)
store_path.write_text(store)

# ---- service: persist the physical click chain outside rolling buffer ----
service = service_path.read_text()
click_anchor = '            NativeAdapterProofStore.appendManualTrace(this, click.toString());\n'
if click_anchor not in service:
    raise SystemExit("P1f manual click trace anchor missing")
service = service.replace(
    click_anchor,
    '''            String clickSummary = click.toString();\n            NativeAdapterProofStore.recordManualClickSummary(this, clickSummary);\n            NativeAdapterProofStore.appendManualTrace(this, clickSummary);\n''',
    1,
)
service_path.write_text(service)

# ---- activity: unified P1f naming + ACTION_CREATE_DOCUMENT TXT export ----
activity = activity_path.read_text()
activity = activity.replace('import android.widget.TextView;\n', 'import android.widget.TextView;\nimport android.widget.Toast;\n\nimport java.io.OutputStream;\nimport java.nio.charset.StandardCharsets;\n', 1)
activity = activity.replace(
    'public class NativeAdapterProofActivity extends Activity {\n',
    'public class NativeAdapterProofActivity extends Activity {\n    private static final int EXPORT_TRACE_REQUEST = 3917;\n',
    1,
)
activity = activity.replace('    private Button openCandidateButton;\n', '    private Button openCandidateButton;\n    private Button exportTraceButton;\n', 1)
activity = activity.replace('title.setText("Native Chat Adapter P1e");', 'title.setText("Native Chat Adapter P1f");', 1)
activity = activity.replace(
    'subtitle.setText("Manual Send black-box tracer. P1e opens a new native ChatGPT draft, then performs NO submit action. When the draft is visible, manually press ChatGPT Send exactly once. P1e records the real Accessibility click source, ancestor/action surface, composer transition and any ChatGPT notification, then returns with the trace.");',
    'subtitle.setText("Manual Send black-box tracer with portable TXT export. P1f performs NO submit action. When the draft is visible, manually press ChatGPT Send exactly once; after the trace returns, tap EXPORT TRACE TXT and upload that file for analysis.");',
    1,
)
activity = activity.replace('startButton.setText("Start P1e manual Send trace");', 'startButton.setText("Start P1f manual Send trace");', 1)
activity = activity.replace(
    'String prompt = "Native adapter P1e manual Send trace. Reply with exactly this marker and no other text: " + marker;',
    'String prompt = "Native adapter P1f manual Send trace. Reply with exactly this marker and no other text: " + marker;',
    1,
)

reset_anchor = '''        root.addView(reset, new LinearLayout.LayoutParams(-1, -2));\n\n        status = new TextView(this);\n'''
if reset_anchor not in activity:
    raise SystemExit("P1f reset/status UI anchor missing")
activity = activity.replace(
    reset_anchor,
    '''        root.addView(reset, new LinearLayout.LayoutParams(-1, -2));\n\n        exportTraceButton = new Button(this);\n        exportTraceButton.setText("EXPORT TRACE TXT");\n        exportTraceButton.setOnClickListener(v -> exportTraceText());\n        LinearLayout.LayoutParams exportLp = new LinearLayout.LayoutParams(-1, -2);\n        exportLp.topMargin = dp(12);\n        root.addView(exportTraceButton, exportLp);\n\n        status = new TextView(this);\n''',
    1,
)

refresh_anchor = '    private void refreshUi() {\n'
if refresh_anchor not in activity:
    raise SystemExit("P1f refreshUi anchor missing")
export_methods = r'''    private void exportTraceText() {
        String baseline = NativeAdapterProofStore.manualBaseline(this);
        String trace = NativeAdapterProofStore.manualTrace(this);
        String after = NativeAdapterProofStore.manualAfter(this);
        String click = NativeAdapterProofStore.manualClickSummary(this);
        if (baseline.isEmpty() && trace.isEmpty() && after.isEmpty() && click.isEmpty()) {
            Toast.makeText(this, "No trace captured yet", Toast.LENGTH_SHORT).show();
            return;
        }
        String marker = NativeAdapterProofStore.marker(this);
        String suffix = marker == null || marker.isEmpty() ? "trace" : marker;
        Intent create = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        create.addCategory(Intent.CATEGORY_OPENABLE);
        create.setType("text/plain");
        create.putExtra(Intent.EXTRA_TITLE, "native-chat-adapter-p1f-" + suffix + ".txt");
        try {
            startActivityForResult(create, EXPORT_TRACE_REQUEST);
        } catch (Exception e) {
            Toast.makeText(this, "Could not open Android file picker", Toast.LENGTH_LONG).show();
        }
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != EXPORT_TRACE_REQUEST || resultCode != RESULT_OK || data == null || data.getData() == null) return;
        Uri out = data.getData();
        try (OutputStream os = getContentResolver().openOutputStream(out, "wt")) {
            if (os == null) throw new IllegalStateException("null output stream");
            os.write(buildTraceExportText().getBytes(StandardCharsets.UTF_8));
            os.flush();
            Toast.makeText(this, "Trace TXT saved", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "Trace export failed: " + e.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
        }
    }

    private String buildTraceExportText() {
        StringBuilder out = new StringBuilder();
        out.append("Native Chat Adapter P1f - manual Send trace export\n");
        out.append("ChatGPT APK target: 1.2026.237\n");
        out.append("adapterVersion: 0.39-native-adapter-p1f-export-trace\n");
        out.append("state: ").append(NativeAdapterProofStore.state(this)).append('\n');
        out.append("marker: ").append(NativeAdapterProofStore.marker(this)).append('\n');
        out.append("startedAtEpochMs: ").append(NativeAdapterProofStore.startedAt(this)).append('\n');
        out.append("exportedAtEpochMs: ").append(System.currentTimeMillis()).append('\n');
        out.append("lastNotificationTag: ").append(NativeAdapterProofStore.lastNotificationTag(this)).append('\n');
        out.append("lastNotificationText: ").append(NativeAdapterProofStore.lastNotificationText(this)).append('\n');
        out.append("\n=== DURABLE MANUAL CLICK SUMMARY ===\n");
        String click = NativeAdapterProofStore.manualClickSummary(this);
        out.append(click.isEmpty() ? "<no TYPE_VIEW_CLICKED source captured>\n" : click).append('\n');
        out.append("\n=== BEFORE MANUAL SEND ===\n").append(NativeAdapterProofStore.manualBaseline(this)).append('\n');
        out.append("\n=== EVENT TRACE ===\n").append(NativeAdapterProofStore.manualTrace(this)).append('\n');
        out.append("\n=== AFTER MANUAL SEND ===\n").append(NativeAdapterProofStore.manualAfter(this)).append('\n');
        return out.toString();
    }

'''
activity = activity.replace(refresh_anchor, export_methods + refresh_anchor, 1)

# Put the portable evidence summary near the top of the on-screen report too.
status_anchor = '''        if (!manualAfter.isEmpty()) b.append("\\n=== AFTER MANUAL SEND ===\\n").append(manualAfter).append('\\n');\n'''
if status_anchor not in activity:
    raise SystemExit("P1f P1e status anchor missing")
activity = activity.replace(
    status_anchor,
    '''        String manualClickSummary = NativeAdapterProofStore.manualClickSummary(this);\n        if (!manualClickSummary.isEmpty()) b.append("\\n=== DURABLE MANUAL CLICK SUMMARY ===\\n").append(manualClickSummary).append('\\n');\n        if (!manualAfter.isEmpty()) b.append("\\n=== AFTER MANUAL SEND ===\\n").append(manualAfter).append('\\n');\n        if (!manualTrace.isEmpty() || !manualBaseline.isEmpty() || !manualAfter.isEmpty() || !manualClickSummary.isEmpty()) {\n            b.append("\\nTXT export available: tap EXPORT TRACE TXT.\\n");\n        }\n''',
    1,
)

enable_anchor = '        openCandidateButton.setEnabled(candidate != null && !candidate.isEmpty() && !NativeAdapterProofStore.verified(this));\n'
if enable_anchor not in activity:
    raise SystemExit("P1f export enable anchor missing")
activity = activity.replace(
    enable_anchor,
    enable_anchor + '        exportTraceButton.setEnabled(!NativeAdapterProofStore.manualTrace(this).isEmpty() || !NativeAdapterProofStore.manualBaseline(this).isEmpty() || !NativeAdapterProofStore.manualAfter(this).isEmpty() || !NativeAdapterProofStore.manualClickSummary(this).isEmpty());\n',
    1,
)
activity_path.write_text(activity)

# ---- visible naming ------------------------------------------------------
ANDROID_NS = 'http://schemas.android.com/apk/res/android'
ET.register_namespace('android', ANDROID_NS)
tree = ET.parse(manifest_path)
manifest = tree.getroot()
app = manifest.find('application')
if app is None:
    raise SystemExit("P1f manifest application missing")
label_key = '{%s}label' % ANDROID_NS
name_key = '{%s}name' % ANDROID_NS
app.set(label_key, 'Native Chat Adapter P1f')
for node in list(app):
    name = node.get(name_key, '')
    if name.endswith('NativeAdapterProofActivity') or name.endswith('NativeProbeAccessibilityService') or name.endswith('NativeAdapterNotificationListenerService'):
        node.set(label_key, 'Native Chat Adapter P1f')
tree.write(manifest_path, encoding='utf-8', xml_declaration=True)

# ---- version -------------------------------------------------------------
g = gradle_path.read_text()
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 39', g, count=1)
g, n2 = re.subn(r'versionName\s+["\'][^"\']+["\']', 'versionName "0.39-native-adapter-p1f-export-trace"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("Could not update P1f version metadata")
gradle_path.write_text(g)

# Build-time assertions: tracing remains read-only; only file export is new.
activity = activity_path.read_text()
service = service_path.read_text()
a = service.index('    private void observeNativeAdapterP1eManualSendTrace')
b = service.index('    private static final long P1D_STABILIZATION_MS', a)
manual_observer = service[a:b]
for forbidden in ('performAction(', 'dispatchGesture', 'performGlobalAction', 'GLOBAL_ACTION_'):
    assert forbidden not in manual_observer, forbidden
assert 'EXPORT TRACE TXT' in activity
assert 'Intent.ACTION_CREATE_DOCUMENT' in activity
assert 'buildTraceExportText' in activity
assert 'manualClickSummary' in activity
assert 'recordManualClickSummary' in service
assert '240000' in store_path.read_text()
assert 'Native Chat Adapter P1f' in manifest_path.read_text()
assert 'versionCode 39' in g
assert 'versionName "0.39-native-adapter-p1f-export-trace"' in g
