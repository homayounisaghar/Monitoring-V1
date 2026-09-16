package com.openai.controlplane.capabilityprobe;

import android.app.Activity;
import android.content.ClipData;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import androidx.core.content.FileProvider;

import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.UUID;

public final class MainActivity extends Activity {
    private static final String CHATGPT_PACKAGE = "com.openai.chatgpt";
    private static final String EXPECTED_VERSION = "1.2026.237";
    private static final String CHATGPT_MAIN = "com.openai.chatgpt.MainActivity";
    private static final String CHATGPT_DEEPLINK = "com.openai.chatgpt.ChatGptDeeplinkActivity";
    private static final String CHATGPT_ASSISTANT = "com.openai.voice.assistant.AssistantActivity";
    private static final String CHATGPT_PROCESS_TEXT = "com.openai.chatgpt.TextProcessorActivity";

    private TextView status;
    private String lastLaunched = "none";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int p = dp(18);
        root.setPadding(p, p, p, p);
        scroll.addView(root);

        TextView title = new TextView(this);
        title.setText("Native Capability Probe P2");
        title.setTextSize(22f);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        root.addView(title);

        TextView desc = new TextView(this);
        desc.setText("Exact-build runtime proof for exported ChatGPT Android contracts found by the APK census. This probe NEVER presses Send, never uses Accessibility, and never calls private ChatGPT backend APIs. It only launches official exported Android intents/components.\n\nRun one test at a time and inspect what the official ChatGPT app opens. A shared test file is harmless local text and must remain unsent.");
        desc.setTextSize(15f);
        desc.setPadding(0, dp(10), 0, dp(14));
        root.addView(desc);

        status = new TextView(this);
        status.setTextSize(14f);
        status.setPadding(0, 0, 0, dp(14));
        root.addView(status);

        root.addView(button("1. Share ONE test file to ChatGPT", v -> runSafely("ACTION_SEND one file", this::shareOneFile)));
        root.addView(button("2. Share TWO test files to ChatGPT", v -> runSafely("ACTION_SEND_MULTIPLE two files", this::shareTwoFiles)));
        root.addView(button("3. Open official /voice deep link", v -> runSafely("/voice deep link", this::openVoiceDeepLink)));
        root.addView(button("4. Open exported AssistantActivity", v -> runSafely("AssistantActivity explicit", this::openAssistantActivity)));
        root.addView(button("5. PROCESS_TEXT marker with ChatGPT", v -> runSafely("PROCESS_TEXT", this::processText)));

        TextView rules = new TextView(this);
        rules.setText("PASS criteria\n• Share one/two: ChatGPT receives the exact local test attachment(s) through its native composer/intake UI. Do not send them.\n• /voice: native ChatGPT voice surface starts through the deep link.\n• AssistantActivity: native assistant/voice surface starts through the exported component.\n• PROCESS_TEXT: selected marker text reaches native ChatGPT through Android's process-text entry.\n\nIf a test does nothing, opens the wrong surface, or throws, return here; the status line will retain which contract was attempted.");
        rules.setTextSize(14f);
        rules.setPadding(0, dp(18), 0, dp(18));
        root.addView(rules);

        setContentView(scroll);
        refreshStatus();
    }

    @Override
    protected void onResume() {
        super.onResume();
        refreshStatus();
    }

    private Button button(String label, View.OnClickListener listener) {
        Button b = new Button(this);
        b.setText(label);
        b.setAllCaps(false);
        b.setOnClickListener(listener);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0, dp(5), 0, dp(5));
        b.setLayoutParams(lp);
        return b;
    }

    private void runSafely(String label, ThrowingRunnable action) {
        try {
            assertExactChatGptVersion();
            lastLaunched = label;
            refreshStatus();
            action.run();
        } catch (Throwable t) {
            status.setText("BLOCKED/FAILED before or during launch:\n" + label + "\n" + t.getClass().getSimpleName() + ": " + String.valueOf(t.getMessage()));
        }
    }

    private void assertExactChatGptVersion() throws Exception {
        PackageInfo info = getPackageManager().getPackageInfo(CHATGPT_PACKAGE, 0);
        String version = info.versionName == null ? "" : info.versionName;
        if (!EXPECTED_VERSION.equals(version)) {
            throw new IllegalStateException("Fail closed: expected ChatGPT " + EXPECTED_VERSION + " but found " + version);
        }
    }

    private void shareOneFile() throws Exception {
        Uri uri = createProbeFile("one", "P2 single attachment runtime proof");
        Intent i = new Intent(Intent.ACTION_SEND);
        i.setComponent(new ComponentName(CHATGPT_PACKAGE, CHATGPT_MAIN));
        i.setType("text/plain");
        i.putExtra(Intent.EXTRA_STREAM, uri);
        i.setClipData(ClipData.newRawUri("Native Capability Probe P2", uri));
        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivity(i);
    }

    private void shareTwoFiles() throws Exception {
        Uri a = createProbeFile("multi_a", "P2 first multi attachment runtime proof");
        Uri b = createProbeFile("multi_b", "P2 second multi attachment runtime proof");
        ArrayList<Uri> streams = new ArrayList<>();
        streams.add(a);
        streams.add(b);
        ClipData clip = ClipData.newRawUri("Native Capability Probe P2 A", a);
        clip.addItem(new ClipData.Item(b));

        Intent i = new Intent(Intent.ACTION_SEND_MULTIPLE);
        i.setComponent(new ComponentName(CHATGPT_PACKAGE, CHATGPT_MAIN));
        i.setType("text/plain");
        i.putParcelableArrayListExtra(Intent.EXTRA_STREAM, streams);
        i.setClipData(clip);
        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivity(i);
    }

    private void openVoiceDeepLink() {
        Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse("https://chatgpt.com/voice"));
        i.setComponent(new ComponentName(CHATGPT_PACKAGE, CHATGPT_DEEPLINK));
        startActivity(i);
    }

    private void openAssistantActivity() {
        Intent i = new Intent();
        i.setComponent(new ComponentName(CHATGPT_PACKAGE, CHATGPT_ASSISTANT));
        i.putExtra("isAssistant", true);
        startActivity(i);
    }

    private void processText() {
        String marker = "PB_NATIVE_P2_PROCESS_TEXT_" + UUID.randomUUID().toString().replace("-", "").substring(0, 12).toUpperCase();
        Intent i = new Intent(Intent.ACTION_PROCESS_TEXT);
        i.setComponent(new ComponentName(CHATGPT_PACKAGE, CHATGPT_PROCESS_TEXT));
        i.setType("text/plain");
        i.putExtra(Intent.EXTRA_PROCESS_TEXT, marker);
        i.putExtra(Intent.EXTRA_PROCESS_TEXT_READONLY, true);
        startActivity(i);
    }

    private Uri createProbeFile(String suffix, String purpose) throws Exception {
        String marker = "PB_NATIVE_P2_ATTACHMENT_" + UUID.randomUUID().toString().replace("-", "").substring(0, 12).toUpperCase();
        File file = new File(getCacheDir(), "native-capability-p2-" + suffix + "-" + marker + ".txt");
        String text = "Native Capability Probe P2\n" +
                "Marker: " + marker + "\n" +
                "Purpose: " + purpose + "\n" +
                "This harmless local file exists only to prove ChatGPT's exported Android attachment intake. Do not send it.\n";
        try (FileOutputStream out = new FileOutputStream(file)) {
            out.write(text.getBytes(StandardCharsets.UTF_8));
        }
        return FileProvider.getUriForFile(this, "com.openai.controlplane.capabilityprobe.files", file);
    }

    private void refreshStatus() {
        String version;
        try {
            PackageInfo info = getPackageManager().getPackageInfo(CHATGPT_PACKAGE, 0);
            version = info.versionName == null ? "<unknown>" : info.versionName;
        } catch (Throwable t) {
            version = "NOT INSTALLED / NOT VISIBLE";
        }
        if (status != null) {
            status.setText("Expected ChatGPT: " + EXPECTED_VERSION + "\nDetected ChatGPT: " + version + "\nLast launched contract: " + lastLaunched);
        }
    }

    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    private interface ThrowingRunnable { void run() throws Exception; }
}
