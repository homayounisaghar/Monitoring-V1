package com.onshape.mousebridge.poc;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.graphics.Typeface;
import android.os.Bundle;
import android.provider.Settings;
import android.text.TextUtils;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private TextView status;
    private TextView zoomValue;
    private TextView uiScrollValue;
    private SeekBar zoomSeek;
    private SeekBar uiScrollSeek;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        int pad = dp(20);
        ScrollView scrollView = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(pad, pad, pad, pad);
        scrollView.addView(root, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView title = new TextView(this);
        title.setText("Onshape MouseBridge Test");
        title.setTextSize(24);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        root.addView(title, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView info = new TextView(this);
        info.setText("Android 14+ mouse-to-touch bridge for Onshape\n\n" +
                "Mouse mappings inside Onshape:\n" +
                "• Left click → single-finger tap\n" +
                "• Left drag → single-finger drag (rotate)\n" +
                "• Right click → two-finger tap (context menu)\n" +
                "• Wheel over workspace → radial safe pinch zoom\n" +
                "• Wheel over UI/menu → vertical touch scroll\n" +
                "• Middle drag → two-finger drag (pan)\n\n" +
                "This is a side-by-side test build. Sensitivity changes are saved immediately.");
        info.setTextSize(16);
        LinearLayout.LayoutParams infoLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        infoLp.topMargin = dp(16);
        root.addView(info, infoLp);

        TextView tuningTitle = new TextView(this);
        tuningTitle.setText("Mouse wheel tuning");
        tuningTitle.setTextSize(19);
        tuningTitle.setTypeface(Typeface.DEFAULT_BOLD);
        LinearLayout.LayoutParams tuningTitleLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        tuningTitleLp.topMargin = dp(24);
        root.addView(tuningTitle, tuningTitleLp);

        zoomValue = new TextView(this);
        zoomValue.setTextSize(16);
        LinearLayout.LayoutParams zoomValueLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        zoomValueLp.topMargin = dp(12);
        root.addView(zoomValue, zoomValueLp);

        zoomSeek = createSensitivitySeekBar();
        zoomSeek.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                float value = progress / 100f;
                updateZoomLabel(value);
                if (fromUser) MouseBridgeSettings.setZoomSensitivity(MainActivity.this, value);
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) {}
        });
        root.addView(zoomSeek, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        uiScrollValue = new TextView(this);
        uiScrollValue.setTextSize(16);
        LinearLayout.LayoutParams uiValueLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        uiValueLp.topMargin = dp(12);
        root.addView(uiScrollValue, uiValueLp);

        uiScrollSeek = createSensitivitySeekBar();
        uiScrollSeek.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                float value = progress / 100f;
                updateUiScrollLabel(value);
                if (fromUser) MouseBridgeSettings.setUiScrollSensitivity(MainActivity.this, value);
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) {}
        });
        root.addView(uiScrollSeek, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        Button reset = new Button(this);
        reset.setText("Reset wheel tuning");
        reset.setOnClickListener(v -> {
            MouseBridgeSettings.reset(this);
            loadSensitivityControls();
        });
        LinearLayout.LayoutParams resetLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        resetLp.topMargin = dp(8);
        root.addView(reset, resetLp);

        status = new TextView(this);
        status.setTextSize(16);
        status.setTypeface(Typeface.DEFAULT_BOLD);
        LinearLayout.LayoutParams statusLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        statusLp.topMargin = dp(24);
        root.addView(status, statusLp);

        Button accessibility = new Button(this);
        accessibility.setText("Open Accessibility Settings");
        accessibility.setOnClickListener(v -> startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));
        LinearLayout.LayoutParams buttonLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        buttonLp.topMargin = dp(16);
        root.addView(accessibility, buttonLp);

        Button onshape = new Button(this);
        onshape.setText("Launch Onshape");
        onshape.setOnClickListener(v -> launchOnshape());
        LinearLayout.LayoutParams button2Lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        button2Lp.topMargin = dp(8);
        root.addView(onshape, button2Lp);

        loadSensitivityControls();
        setContentView(scrollView);
    }

    @Override
    protected void onResume() {
        super.onResume();
        loadSensitivityControls();
        status.setText(isServiceEnabled()
                ? "Accessibility service: ENABLED"
                : "Accessibility service: DISABLED");
    }

    private SeekBar createSensitivitySeekBar() {
        SeekBar seek = new SeekBar(this);
        seek.setMin(Math.round(MouseBridgeSettings.MIN_SENSITIVITY * 100f));
        seek.setMax(Math.round(MouseBridgeSettings.MAX_SENSITIVITY * 100f));
        return seek;
    }

    private void loadSensitivityControls() {
        if (zoomSeek == null || uiScrollSeek == null) return;
        float zoom = MouseBridgeSettings.getZoomSensitivity(this);
        float ui = MouseBridgeSettings.getUiScrollSensitivity(this);
        zoomSeek.setProgress(Math.round(zoom * 100f));
        uiScrollSeek.setProgress(Math.round(ui * 100f));
        updateZoomLabel(zoom);
        updateUiScrollLabel(ui);
    }

    private void updateZoomLabel(float value) {
        zoomValue.setText("Workspace zoom sensitivity: " + Math.round(value * 100f) + "%");
    }

    private void updateUiScrollLabel(float value) {
        uiScrollValue.setText("Menu / UI scroll sensitivity: " + Math.round(value * 100f) + "%");
    }

    private boolean isServiceEnabled() {
        ComponentName expected = new ComponentName(this, MouseBridgeAccessibilityService.class);
        String enabled = Settings.Secure.getString(
                getContentResolver(), Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
        if (enabled == null) return false;
        TextUtils.SimpleStringSplitter splitter = new TextUtils.SimpleStringSplitter(':');
        splitter.setString(enabled);
        while (splitter.hasNext()) {
            ComponentName current = ComponentName.unflattenFromString(splitter.next());
            if (expected.equals(current)) return true;
        }
        return false;
    }

    private void launchOnshape() {
        Intent intent = getPackageManager().getLaunchIntentForPackage("com.onshape.app");
        if (intent == null) {
            Toast.makeText(this, "Onshape is not installed.", Toast.LENGTH_LONG).show();
            return;
        }
        startActivity(intent);
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
