package com.homayoun.mousebuttontoggle;

interface IMouseSettingsService {
    void destroy() = 16777114;
    int getSwapState() = 1;
    int toggleSwapState() = 2;
    String getDiagnostics() = 3;
}
