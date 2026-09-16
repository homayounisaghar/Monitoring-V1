# Selected first-party exported entry sources

## `com/openai/chatgpt/MainActivity.java`
_not decompiled at expected path_

## `com/openai/chatgpt/ChatGptDeeplinkActivity.java`
_not decompiled at expected path_

## `com/openai/feature/assistant/impl/AssistantProxyActivity.java`
_not decompiled at expected path_

## `com/openai/voice/assistant/AssistantActivity.java`
_not decompiled at expected path_

## `com/openai/feature/assistant/impl/AssistantVoiceInteractionService.java`
```java
package com.openai.feature.assistant.impl;

import android.service.voice.VoiceInteractionService;

public final class AssistantVoiceInteractionService extends VoiceInteractionService {
}

```

## `com/openai/feature/voice/impl/quicktile/QuickTileService.java`
_not decompiled at expected path_

## `com/openai/feature/conversations/screencontext/ConversationScreenAccessibilityService.java`
```java
package com.openai.feature.conversations.screencontext;

import android.accessibilityservice.AccessibilityService;
import android.graphics.Bitmap;
import android.os.Build;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.view.accessibility.AccessibilityWindowInfo;
import defpackage.a2i;
import defpackage.b2i;
import defpackage.bvj;
import defpackage.c2i;
import defpackage.ct40;
import defpackage.d2i;
import defpackage.e;
import defpackage.f2i;
import defpackage.fke;
import defpackage.fz8;
import defpackage.g2i;
import defpackage.gev;
import defpackage.h2i;
import defpackage.j0d0;
import defpackage.kfr;
import defpackage.pat;
import defpackage.q8z;
import defpackage.qa90;
import defpackage.rsg;
import defpackage.t1i;
import defpackage.tr0;
import defpackage.ug3;
import defpackage.vfn;
import defpackage.wnm;
import defpackage.wqi;
import defpackage.x1i;
import defpackage.y4i;
import defpackage.z4i;
import java.lang.ref.WeakReference;
import java.net.ConnectException;
import java.net.SocketTimeoutException;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.CancellationException;
import kotlinx.coroutines.TimeoutCancellationException;
import kotlinx.serialization.SerializationException;

public final class ConversationScreenAccessibilityService extends AccessibilityService {
    public static final int d = 0;
    public t1i a;
    public final gev b = wnm.F(6, "ConversationScreenAccessibilityService");
    public final c2i c = new c2i(this);

    public static x1i d(AccessibilityService.ScreenshotResult screenshotResult) {
        Bitmap bitmapWrapHardwareBuffer = Bitmap.wrapHardwareBuffer(screenshotResult.getHardwareBuffer(), screenshotResult.getColorSpace());
        if (bitmapWrapHardwareBuffer == null) {
            screenshotResult.getHardwareBuffer().close();
            return null;
        }
        try {
            Bitmap bitmapCopy = bitmapWrapHardwareBuffer.copy(Bitmap.Config.ARGB_8888, false);
            bitmapWrapHardwareBuffer.recycle();
            screenshotResult.getHardwareBuffer().close();
            if (bitmapCopy == null) {
                return null;
            }
            return new x1i(bitmapCopy);
        } catch (Throwable th) {
            bitmapWrapHardwareBuffer.recycle();
            screenshotResult.getHardwareBuffer().close();
            throw th;
        }
    }

    public final Object a(b2i b2iVar) {
        Integer numValueOf;
        List<AccessibilityWindowInfo> windows = getWindows();
        if (windows == null) {
            windows = vfn.a;
        }
        Iterator it = fke.v1(windows, new e(new d2i((byte) 0), (byte) 13)).iterator();
        while (true) {
            if (!it.hasNext()) {
                numValueOf = null;
                break;
            }
            AccessibilityWindowInfo accessibilityWindowInfo = (AccessibilityWindowInfo) it.next();
            try {
                if (accessibilityWindowInfo.getType() != 1) {
                    try {
                        try {
                            accessibilityWindowInfo.recycle();
                        } catch (CancellationException e) {
                            throw e;
                        }
                    } catch (ConnectException | SocketTimeoutException | UnknownHostException | TimeoutCancellationException | SerializationException | Exception unused) {
                    }
                } else {
                    AccessibilityNodeInfo root = accessibilityWindowInfo.getRoot();
                    if (root != null) {
                        try {
                            CharSequence packageName = root.getPackageName();
                            String string = packageName != null ? packageName.toString() : null;
                            if (string != null && !qa90.l0(string) && !string.equals(getPackageName())) {
                                numValueOf = Integer.valueOf(accessibilityWindowInfo.getId());
                                try {
                                    root.recycle();
                                } catch (ConnectException | SocketTimeoutException | UnknownHostException | TimeoutCancellationException | SerializationException | Exception unused2) {
                                }
                                try {
                                    accessibilityWindowInfo.recycle();
                                    break;
                                } catch (ConnectException | SocketTimeoutException | UnknownHostException | TimeoutCancellationException | SerializationException | Exception unused3) {
                                    break;
                                } catch (CancellationException e2) {
                                    throw e2;
                                }
                            }
                            try {
                                try {
                                    root.recycle();
                                } catch (ConnectException | SocketTimeoutException | UnknownHostException | TimeoutCancellationException | SerializationException | Exception unused4) {
                                }
                                try {
                                    accessibilityWindowInfo.recycle();
                                } catch (CancellationException e3) {
                                    throw e3;
                                }
                            } catch (CancellationException e4) {
                                throw e4;
                            }
                        } catch (Throwable th) {
                            try {
                                root.recycle();
                            } catch (ConnectException | SocketTimeoutException | UnknownHostException | TimeoutCancellationException | SerializationException | Exception unused5) {
                            }
                            throw th;
                        }
                        try {
                            accessibilityWindowInfo.recycle();
                        } catch (ConnectException | SocketTimeoutException | UnknownHostException | TimeoutCancellationException | SerializationException | Exception unused6) {
                        } catch (CancellationException e5) {
                            throw e5;
                        }
                        throw th;
                    }
                    try {
                        accessibilityWindowInfo.recycle();
                    } catch (CancellationException e6) {
                        throw e6;
                    }
                }
            } catch (Throwable th2) {
                accessibilityWindowInfo.recycle();
                throw th2;
            }
        }
        if (numValueOf == null) {
            return null;
        }
        int iIntValue = numValueOf.intValue();
        fz8 fz8Var = new fz8(1, kfr.Q(b2iVar));
        fz8Var.t();
        takeScreenshotOfWindow(iIntValue, getMainExecutor(), new a2i(fz8Var, this, iIntValue));
        return fz8Var.r();
    }

    public final Object b(rsg rsgVar) {
        b2i b2iVar;
        if (rsgVar instanceof b2i) {
            b2iVar = (b2i) rsgVar;
            int i = b2iVar.p;
            if ((i & Integer.MIN_VALUE) != 0) {
                b2iVar.p = i - Integer.MIN_VALUE;
            } else {
                b2iVar = new b2i(this, rsgVar);
            }
        } else {
            b2iVar = new b2i(this, rsgVar);
        }
        Object objA = b2iVar.n;
        int i2 = b2iVar.p;
        try {
            if (i2 == 0) {
                ct40.j(objA);
                if (Build.VERSION.SDK_INT >= 34) {
                    b2iVar.p = 1;
                    objA = a(b2iVar);
                    wqi wqiVar = wqi.a;
                    if (objA == wqiVar) {
                        return wqiVar;
                    }
                }
                return null;
            }
            if (i2 != 1) {
                tr0.l("call to 'resume' before 'invoke' with coroutine");
                return null;
            }
            ct40.j(objA);
            AccessibilityService.ScreenshotResult screenshotResult = (AccessibilityService.ScreenshotResult) objA;
            if (screenshotResult != null) {
                return d(screenshotResult);
            }
            return null;
        } catch (CancellationException e) {
            throw e;
        } catch (Exception e2) {
            gev.f(this.b, "Unable to capture accessibility screen screenshot", e2, null, 12);
            return null;
        }
    }

    public final f2i c(long j, h2i h2iVar) {
        y4i y4iVarD;
        boolean z = g2i.a;
        List<AccessibilityWindowInfo> windows = getWindows();
        if (windows == null) {
            windows = vfn.a;
        }
        String packageName = getPackageName();
        q8z q8zVar = new q8z((byte) 7);
        q8zVar.b = 120;
        byte b = 1;
        List<AccessibilityWindowInfo> listV1 = fke.v1(windows, new e(new d2i(b), (byte) 14));
        ArrayList arrayList = new ArrayList();
        for (AccessibilityWindowInfo accessibilityWindowInfo : listV1) {
            try {
                z4i z4iVarE = g2i.e(accessibilityWindowInfo, h2iVar, q8zVar, packageName);
                try {
                    accessibilityWindowInfo.recycle();
                } catch (ConnectException | SocketTimeoutException | UnknownHostException | TimeoutCancellationException | SerializationException | Exception unused) {
                } catch (CancellationException e) {
                    throw e;
                }
                if (z4iVarE != null) {
                    arrayList.add(z4iVarE);
                }
            } catch (Throwable th) {
                try {
                    accessibilityWindowInfo.recycle();
                    throw th;
                } catch (ConnectException | SocketTimeoutException | UnknownHostException | TimeoutCancellationException | SerializationException | Exception unused2) {
                    throw th;
                } catch (CancellationException e2) {
                    throw e2;
                }
            }
        }
        boolean zIsEmpty = arrayList.isEmpty();
        List listU = arrayList;
        if (zIsEmpty) {
            AccessibilityNodeInfo rootInActiveWindow = getRootInActiveWindow();
            z4i z4iVar = null;
            if (rootInActiveWindow != null) {
                try {
                    CharSequence packageName2 = rootInActiveWindow.getPackageName();
                    String string = packageName2 != null ? packageName2.toString() : null;
                    if (string == null || qa90.l0(string) || string.equals(packageName)) {
                        b = 0;
                    }
                    if (b != 0 && (y4iVarD = g2i.d(rootInActiveWindow, 0, h2iVar, q8zVar)) != null) {
                        z4iVar = new z4i(string, null, "active_window", true, true, y4iVarD);
                    }
                } finally {
                    g2i.c(rootInActiveWindow);
                }
            }
            listU = bvj.U(z4iVar);
        }
        ArrayList arrayList2 = new ArrayList();
        for (Object obj : listU) {
            z4i z4iVar2 = (z4i) obj;
            String str = z4iVar2.a;
            String str2 = z4iVar2.c;
            if (str != null && !str.equals(packageName) && (str2.equals("application") || str2.equals("active_window"))) {
                arrayList2.add(obj);
            }
        }
        return new f2i(arrayList2, j, h2iVar, getPackageName());
    }

    @Override
    public final void onDestroy() {
        t1i t1iVar = this.a;
        if (t1iVar != null) {
            c2i c2iVar = this.c;
            synchronized (t1iVar.a) {
                if (t1iVar.a() == c2iVar) {
                    t1iVar.b = null;
                }
            }
        }
        super.onDestroy();
    }

    @Override
    public final void onServiceConnected() {
        super.onServiceConnected();
        ug3 ug3VarM = pat.M(getApplicationContext());
        if (ug3VarM == null) {
            j0d0.h("null cannot be cast to non-null type com.openai.feature.conversations.screencontext.ConversationScreenAccessibilityServiceInjector");
            return;
        }
        t1i t1iVar = (t1i) ug3VarM.P2.invoke();
        this.a = t1iVar;
        c2i c2iVar = this.c;
        synchronized (t1iVar.a) {
            t1iVar.b = new WeakReference(c2iVar);
        }
        gev.d(this.b, "Accessibility service connected and context provider registered", null, null, 14);
    }

    @Override
    public final void onInterrupt() {
    }

    @Override
    public final void onAccessibilityEvent(AccessibilityEvent accessibilityEvent) {
    }
}

```
