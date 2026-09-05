package com.capabilityfabric.tracepartsgrabber;

import android.graphics.Color;
import android.graphics.Insets;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.widget.Button;

/**
 * UI/safety wrapper for the generic viewer extractor.
 *
 * v1.2.1 changes:
 *  - explicitly lays out below the status bar / above the navigation bar;
 *  - removes the user-facing "FINISH NOW" early-abort path. Extraction is allowed
 *    to complete on the core timer and pending-download grace period instead.
 */
public class MainActivityV121 extends MainActivity {
    private final Handler ui = new Handler(Looper.getMainLooper());
    private Button extractButton;

    private final Runnable extractionButtonGuard = new Runnable() {
        @Override
        public void run() {
            if (extractButton == null) return;
            String text = String.valueOf(extractButton.getText());

            // The core activity temporarily exposes FINISH NOW while capturing.
            // Hide that early-abort action and make the state informational only.
            if ("FINISH NOW".equalsIgnoreCase(text)) {
                extractButton.setText("EXTRACTING...");
                extractButton.setEnabled(false);
            } else if ("EXTRACT ZIP".equalsIgnoreCase(text)) {
                // The core has finished packaging and restored its idle label.
                extractButton.setEnabled(true);
            }

            ui.postDelayed(this, 120L);
        }
    };

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        applySafeSystemBarInsets();
        installNoEarlyFinishGuard();
    }

    @Override
    protected void onDestroy() {
        ui.removeCallbacks(extractionButtonGuard);
        super.onDestroy();
    }

    private void applySafeSystemBarInsets() {
        final View content = findViewById(android.R.id.content);
        if (content == null) return;

        // Android 15 enforces edge-to-edge for targetSdk 35. Make that explicit so
        // the same inset handling is used consistently on supported Android versions.
        if (Build.VERSION.SDK_INT >= 30) {
            getWindow().setDecorFitsSystemWindows(false);
        } else {
            getWindow().getDecorView().setSystemUiVisibility(
                    View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
        }

        getWindow().setStatusBarColor(Color.WHITE);
        getWindow().setNavigationBarColor(Color.WHITE);

        content.setOnApplyWindowInsetsListener((v, insets) -> {
            int left;
            int top;
            int right;
            int bottom;

            if (Build.VERSION.SDK_INT >= 30) {
                Insets status = insets.getInsets(WindowInsets.Type.statusBars());
                Insets navigation = insets.getInsets(WindowInsets.Type.navigationBars());
                Insets cutout = insets.getInsets(WindowInsets.Type.displayCutout());
                left = Math.max(navigation.left, cutout.left);
                top = Math.max(status.top, cutout.top);
                right = Math.max(navigation.right, cutout.right);
                bottom = Math.max(navigation.bottom, cutout.bottom);
            } else {
                left = insets.getSystemWindowInsetLeft();
                top = insets.getSystemWindowInsetTop();
                right = insets.getSystemWindowInsetRight();
                bottom = insets.getSystemWindowInsetBottom();
            }

            v.setPadding(left, top, right, bottom);
            return insets;
        });
        content.requestApplyInsets();
    }

    private void installNoEarlyFinishGuard() {
        View content = findViewById(android.R.id.content);
        extractButton = findButtonByText(content, "EXTRACT ZIP");
        if (extractButton == null) return;

        // Preserve the core button's existing click listener for starting extraction.
        // Once its label changes away from EXTRACT ZIP, consume touches so a second
        // tap cannot prematurely stop capture before resources finish loading.
        extractButton.setOnTouchListener((v, event) -> {
            String text = String.valueOf(extractButton.getText());
            boolean idle = "EXTRACT ZIP".equalsIgnoreCase(text);
            if (!idle) return true;
            if (event.getAction() == MotionEvent.ACTION_UP) {
                ui.post(extractionButtonGuard);
            }
            return false;
        });

        ui.post(extractionButtonGuard);
    }

    private Button findButtonByText(View view, String wanted) {
        if (view == null) return null;
        if (view instanceof Button) {
            Button b = (Button) view;
            if (wanted.equalsIgnoreCase(String.valueOf(b.getText()))) return b;
        }
        if (view instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) view;
            for (int i = 0; i < g.getChildCount(); i++) {
                Button found = findButtonByText(g.getChildAt(i), wanted);
                if (found != null) return found;
            }
        }
        return null;
    }
}
