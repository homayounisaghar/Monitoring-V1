package com.homayounisaghar.chatgptwebviewprobe;

import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

/**
 * Stable v0.34 launcher wrapper for the paid-account guarded model round-trip.
 * The actual v0.31 exactly-once claim/receipt logic is inherited through the
 * Auth-mode chain; the paid trigger resolver is injected deterministically by
 * the canonical build workflow from v0.33 census evidence.
 */
public class OrchestratorPaidModelRoundtripV36Activity extends OrchestratorAuthModeV34Activity {
    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        retitle36(getWindow().getDecorView());
    }

    private void retitle36(View v) {
        if (v instanceof Button) {
            Button b = (Button) v;
            String s = String.valueOf(b.getText());
            if (s.contains("RUN MODEL / TOOLS TEST")) {
                b.setText("RUN PAID MODEL ROUND-TRIP");
            }
        } else if (v instanceof TextView) {
            TextView t = (TextView) v;
            String s = String.valueOf(t.getText());
            if (s.startsWith("v0.31 capability picker test ready") || s.startsWith("v0.32.2 Controlled Google OAuth")) {
                t.setText("v0.34 paid model round-trip ready");
            }
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) retitle36(g.getChildAt(i));
        }
    }
}
