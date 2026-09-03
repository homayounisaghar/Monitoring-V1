package com.homayounisaghar.chatgptwebviewprobe;

import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;

public class ResourceSuiteV10FinalActivity extends ResourceSuiteV10Activity {
    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WebView web = findWebView(getWindow().getDecorView());
        if (web != null) {
            int screenHeight = getResources().getDisplayMetrics().heightPixels;
            web.setMinimumHeight(Math.max(1, screenHeight / 2));
        }
    }

    private WebView findWebView(View view) {
        if (view instanceof WebView) return (WebView) view;
        if (!(view instanceof ViewGroup)) return null;
        ViewGroup group = (ViewGroup) view;
        for (int i = 0; i < group.getChildCount(); i++) {
            WebView found = findWebView(group.getChildAt(i));
            if (found != null) return found;
        }
        return null;
    }
}
