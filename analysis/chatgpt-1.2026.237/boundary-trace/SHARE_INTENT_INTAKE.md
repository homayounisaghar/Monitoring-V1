# SHARE_INTENT_INTAKE

## `com/openai/valdi/filesaver/MobileFileSaverNativeModuleFactoryImpl.java`
### line 3
```java
1: package com.openai.valdi.filesaver;
2: 
3: import android.content.ClipData;
4: import android.content.ContentResolver;
5: import android.content.ContentValues;
6: import android.content.Context;
7: import android.content.Intent;
```

### line 74
```java
70:                 }
71:                 if (wec0Var == null) {
72:                     throw new IllegalStateException("Unable to write " + request.get_filename());
73:                 }
74:                 Intent intent = new Intent("android.intent.action.SEND");
75:                 intent.setType(request.get_mimeType());
76:                 intent.setClipData(ClipData.newUri(contentResolver, request.get_filename(), uriInsert));
77:                 intent.putExtra("android.intent.extra.STREAM", uriInsert);
78:                 intent.putExtra("android.intent.extra.TITLE", request.get_filename());
```

## `defpackage/acg.java`
### line 3
```java
1: package defpackage;
2: 
3: import android.content.ClipData;
4: import android.media.metrics.LogSessionId;
5: import android.net.Uri;
6: import android.os.Bundle;
7: import android.view.ContentInfo;
```

### line 39
```java
35:         return (ContentInfo) this.b;
36:     }
37: 
38:     @Override
39:     public ClipData d() {
40:         return ((ContentInfo) this.b).getClip();
41:     }
42: 
43:     @Override
```

### line 78
```java
74:         contentInfo.getClass();
75:         this.b = contentInfo;
76:     }
77: 
78:     public acg(ClipData clipData, int i) {
79:         this.a = (byte) 0;
80:         this.b = au0.e(clipData, i);
81:     }
82: }
```

## `defpackage/asa0.java`
### line 3
```java
1: package defpackage;
2: 
3: import android.content.ClipData;
4: import android.content.Context;
5: import android.text.Editable;
6: import android.text.Selection;
7: import android.text.Spanned;
```

### line 23
```java
19:         dcg dcgVar = ecgVar.a;
20:         if (dcgVar.a() == 2) {
21:             return ecgVar;
22:         }
23:         ClipData clipDataD = dcgVar.d();
24:         int iF = dcgVar.f();
25:         TextView textView = (TextView) view;
26:         Editable editable = (Editable) textView.getText();
27:         Context context = textView.getContext();
```

### line 29
```java
25:         TextView textView = (TextView) view;
26:         Editable editable = (Editable) textView.getText();
27:         Context context = textView.getContext();
28:         boolean z = false;
29:         for (int i = 0; i < clipDataD.getItemCount(); i++) {
30:             ClipData.Item itemAt = clipDataD.getItemAt(i);
31:             if ((iF & 1) != 0) {
32:                 charSequenceCoerceToStyledText = itemAt.coerceToText(context);
33:                 if (charSequenceCoerceToStyledText instanceof Spanned) {
```

## `defpackage/c9t.java`
### line 3
```java
1: package defpackage;
2: 
3: import android.content.ClipData;
4: import android.content.Context;
5: import com.openai.chatgpt.R;
6: import com.openai.viewmodel.DisplayableException;
7: import io.sentry.w4;
```

### line 317
```java
313:                             wqi wqiVar = wqi.a;
314:                             if (z6) {
315:                                 lw80 lw80Var = (lw80) yw80Var;
316:                                 if (lw80Var.a() != null) {
317:                                     m8b m8bVarQ = n7g0.q(ClipData.newHtmlText("Copied text", lw80Var.b().b, lw80Var.a()));
318:                                     b9tVar.p = 1;
319:                                 } else {
320:                                     m8b m8bVarQ2 = n7g0.q(ClipData.newPlainText("Copied text", lw80Var.b().b));
321:                                     b9tVar.p = 2;
```

### line 332
```java
328:                                     }
329:                                     d7y.b();
330:                                     return null;
331:                                 }
332:                                 m8b m8bVarQ3 = n7g0.q(ClipData.newUri(this.f.getContentResolver(), "Image", ((kw80) yw80Var).a()));
333:                                 b9tVar.p = 3;
334:                                 Object objB = o8bVar.b(m8bVarQ3, b9tVar);
335:                                 if (objB != wqiVar) {
336:                                     return objB;
```

## `defpackage/ccg.java`
### line 3
```java
1: package defpackage;
2: 
3: import android.content.ClipData;
4: import android.net.Uri;
5: import android.os.Bundle;
6: import android.view.ContentInfo;
7: 
```

### line 10
```java
6: import android.view.ContentInfo;
7: 
8: public final class ccg implements bcg, dcg {
9:     public final byte a = 0;
10:     public ClipData b;
11:     public byte c;
12:     public int d;
13:     public Uri e;
14:     public Bundle f;
```

### line 17
```java
13:     public Uri e;
14:     public Bundle f;
15: 
16:     public ccg(ccg ccgVar) {
17:         ClipData clipData = ccgVar.b;
18:         clipData.getClass();
19:         this.b = clipData;
20:         byte b = ccgVar.c;
21:         nvg0.v("source", b, 0, 5);
```

### line 54
```java
50:         return null;
51:     }
52: 
53:     @Override
54:     public ClipData d() {
55:         return this.b;
56:     }
57: 
58:     @Override
```

## `defpackage/dcg.java`
### line 3
```java
1: package defpackage;
2: 
3: import android.content.ClipData;
4: import android.view.ContentInfo;
5: 
6: public interface dcg {
7:     int a();
```

### line 11
```java
7:     int a();
8: 
9:     ContentInfo c();
10: 
11:     ClipData d();
12: 
13:     int f();
14: }
```

## `defpackage/e50.java`
### line 35
```java
31:             case 2:
32:                 return addressElementActivity.r;
33:             case 3:
34:                 int i3 = AddressElementActivity.u;
35:                 return (k50) addressElementActivity.getIntent().getParcelableExtra("com.stripe.android.paymentsheet.addresselement.AddressElementActivityContract.extra_args");
36:             default:
37:                 int i4 = AddressElementActivity.u;
38:                 w8y w8yVar = addressElementActivity.h().X;
39:                 x8y x8yVar = w8yVar.a;
```

## `defpackage/efg0.java`
### line 32
```java
28:             if (obj instanceof Intent) {
29:                 Intent intent = (Intent) obj;
30:                 intent.setExtrasClassLoader(new seh0());
31:                 if (intent.hasExtra("google.messenger")) {
32:                     Parcelable parcelableExtra = intent.getParcelableExtra("google.messenger");
33:                     if (parcelableExtra instanceof l0i0) {
34:                         p450Var.g = (l0i0) parcelableExtra;
35:                     }
36:                     if (parcelableExtra instanceof Messenger) {
```

## `defpackage/hwv.java`
### line 3
```java
1: package defpackage;
2: 
3: import android.content.ClipData;
4: import android.content.Intent;
5: import android.view.ActionMode;
6: import android.view.View;
7: 
```

### line 44
```java
40:     }
41: 
42:     public final Object c(rsg rsgVar) {
43:         gwv gwvVar;
44:         ClipData clipData;
45:         ClipData.Item itemAt;
46:         CharSequence text;
47:         String string;
48:         if (rsgVar instanceof gwv) {
```

### line 78
```java
74:             }
75:             ct40.j(objA);
76:         }
77:         m8b m8bVar = (m8b) objA;
78:         if (m8bVar != null && (clipData = m8bVar.a) != null) {
79:             if (clipData.getItemCount() <= 0) {
80:                 clipData = null;
81:             }
82:             if (clipData != null && (text = (itemAt = clipData.getItemAt(0)).getText()) != null && (string = text.toString()) != null) {
```

### line 85
```java
81:             }
82:             if (clipData != null && (text = (itemAt = clipData.getItemAt(0)).getText()) != null && (string = text.toString()) != null) {
83:                 Intent intent = itemAt.getIntent();
84:                 if (intent != null) {
85:                     if (!clipData.getDescription().hasMimeType("application/vnd.openai.rich-text-editor.markdown")) {
86:                         intent = null;
87:                     }
88:                     if (intent != null) {
89:                         stringExtra = intent.getStringExtra("rich_markdown");
```

## `defpackage/ig90.java`
### line 151
```java
147:             tr0.l("call to 'resume' before 'invoke' with coroutine");
148:             return null;
149:         }
150:         ct40.j(obj);
151:         if (intent == null || (ok00Var = (ok00) intent.getParcelableExtra("extra_args")) == null) {
152:             ok00Var = new ok00((String) null, 0, (StripeException) null, false, (String) null, (String) null, 127);
153:         }
154:         eg90Var.p = 1;
155:         Object objE = this.e.e(ok00Var, eg90Var);
```

### line 185
```java
181:             tr0.l("call to 'resume' before 'invoke' with coroutine");
182:             return null;
183:         }
184:         ct40.j(obj);
185:         if (intent == null || (ok00Var = (ok00) intent.getParcelableExtra("extra_args")) == null) {
186:             ok00Var = new ok00((String) null, 0, (StripeException) null, false, (String) null, (String) null, 127);
187:         }
188:         fg90Var.p = 1;
189:         Object objE = this.f.e(ok00Var, fg90Var);
```

## `defpackage/is0.java`
### line 3
```java
1: package defpackage;
2: 
3: import android.content.ClipData;
4: import android.content.ClipboardManager;
5: import android.os.Build;
6: 
7: public final class is0 implements o8b {
```

### line 16
```java
12:     }
13: 
14:     @Override
15:     public final Object a(rsg rsgVar) {
16:         ClipData primaryClip = this.a.a().getPrimaryClip();
17:         if (primaryClip != null) {
18:             return new m8b(primaryClip);
19:         }
20:         return null;
```

### line 31
```java
27:             js0Var.a().setPrimaryClip(m8bVar.a());
28:         } else if (Build.VERSION.SDK_INT >= 28) {
29:             rd1.e(js0Var.a());
30:         } else {
31:             js0Var.a().setPrimaryClip(ClipData.newPlainText("", ""));
32:         }
33:         return wec0.a;
34:     }
35: 
```

## `defpackage/j4d0.java`
### line 3
```java
1: package defpackage;
2: 
3: import android.content.ClipData;
4: import android.content.ClipboardManager;
5: import android.view.View;
6: import android.view.ViewGroup;
7: import com.snap.valdi.context.ValdiContext;
```

### line 40
```java
36:                 String str = (String) obj;
37:                 Object systemService = ((m4d0) obj2).f.a.getSystemService("clipboard");
38:                 ClipboardManager clipboardManager = systemService instanceof ClipboardManager ? (ClipboardManager) systemService : null;
39:                 if (clipboardManager != null) {
40:                     clipboardManager.setPrimaryClip(ClipData.newPlainText("", str));
41:                     return wec0Var;
42:                 }
43:                 tr0.l("The Android clipboard is unavailable.");
44:                 return null;
```

## `defpackage/lh8.java`
### line 188
```java
184:         if (str == null) {
185:             return wec0.a;
186:         }
187:         Intent intent = new Intent();
188:         intent.setAction("android.intent.action.SEND");
189:         intent.setType("text/plain");
190:         intent.putExtra("android.intent.extra.TEXT", str);
191:         nw80 nw80Var = new nw80(Intent.createChooser(intent, null), null);
192:         kh8Var.p = 2;
```

## `defpackage/lzb.java`
### line 3
```java
1: package defpackage;
2: 
3: import android.content.ClipData;
4: import kotlin.jvm.functions.Function2;
5: 
6: public final class lzb extends gw90 implements Function2 {
7:     public final byte n;
```

### line 65
```java
61:             case 0:
62:                 boolean z = this.o;
63:                 if (!z) {
64:                     ct40.j(obj);
65:                     m8b m8bVar = new m8b(ClipData.newPlainText(str2, str));
66:                     this.o = true;
67:                     return o8bVar.b(m8bVar, this) == wqiVar ? wqiVar : wec0Var;
68:                 }
69:                 if (z) {
```

### line 79
```java
75:             case 1:
76:                 boolean z2 = this.o;
77:                 if (!z2) {
78:                     ct40.j(obj);
79:                     m8b m8bVar2 = new m8b(ClipData.newPlainText(str2, str));
80:                     this.o = true;
81:                     return o8bVar.b(m8bVar2, this) == wqiVar ? wqiVar : wec0Var;
82:                 }
83:                 if (z2) {
```

### line 93
```java
89:             case 2:
90:                 boolean z3 = this.o;
91:                 if (!z3) {
92:                     ct40.j(obj);
93:                     m8b m8bVar3 = new m8b(ClipData.newPlainText(str2, str));
94:                     this.o = true;
95:                     return o8bVar.b(m8bVar3, this) == wqiVar ? wqiVar : wec0Var;
96:                 }
97:                 if (z3) {
```

### line 114
```java
110:                     tr0.l("call to 'resume' before 'invoke' with coroutine");
111:                     return null;
112:                 }
113:                 ct40.j(obj);
114:                 m8b m8bVar4 = new m8b(ClipData.newPlainText(str2, str2 + ": " + str));
115:                 this.o = true;
116:                 return o8bVar.b(m8bVar4, this) == wqiVar ? wqiVar : wec0Var;
117:         }
118:     }
```

## `defpackage/m8b.java`
### line 3
```java
1: package defpackage;
2: 
3: import android.content.ClipData;
4: 
5: public final class m8b {
6:     public final ClipData a;
7: 
```

### line 9
```java
5: public final class m8b {
6:     public final ClipData a;
7: 
8:     public m8b(ClipData clipData) {
9:         this.a = clipData;
10:     }
11: 
12:     public final ClipData a() {
13:         return this.a;
```

## `defpackage/me30.java`
### line 36
```java
32:         }
33:         if (bundle == null) {
34:             Intent intent = proxyAmazonBillingActivity.getIntent();
35:             String stringExtra = intent.getStringExtra("sku");
36:             ResultReceiver resultReceiver = (ResultReceiver) intent.getParcelableExtra("result_receiver");
37:             bk30 bk30Var = (bk30) intent.getParcelableExtra("purchasing_service_provider");
38:             if (stringExtra == null || resultReceiver == null || bk30Var == null) {
39:                 cns.h0(new jj30(kj30.PurchaseInvalidError, String.format("Failed to make purchase. Arguments are invalid. \n Intent: %s", Arrays.copyOf(new Object[]{intent.toUri(0)}, 1))));
40:                 requestIdG = null;
```

## `defpackage/mey.java`
### line 155
```java
151:     public final String c(bul bulVar) {
152:         Intent intentRegisterReceiver;
153:         WifiInfo wifiInfo;
154:         String ssid;
155:         return (b(bulVar.b, bulVar.c, bulVar.a) != NetworkChangeDetector$ConnectionType.c || (intentRegisterReceiver = this.f.a.registerReceiver(null, new IntentFilter("android.net.wifi.STATE_CHANGE"))) == null || (wifiInfo = (WifiInfo) intentRegisterReceiver.getParcelableExtra("wifiInfo")) == null || (ssid = wifiInfo.getSSID()) == null) ? "" : ssid;
156:     }
157: 
158:     @Override
159:     public final void onReceive(Context context, Intent intent) {
```

## `defpackage/nd3.java`
### line 4
```java
1: package defpackage;
2: 
3: import android.app.Activity;
4: import android.content.ClipData;
5: import android.content.ClipboardManager;
6: import android.content.Context;
7: import android.content.ContextWrapper;
8: import android.content.res.ColorStateList;
```

### line 211
```java
207:         if (i3 >= 31 || nnd0.g(this) == null || !(i == 16908322 || i == 16908337)) {
208:             return super.onTextContextMenuItem(i);
209:         }
210:         ClipboardManager clipboardManager = (ClipboardManager) getContext().getSystemService("clipboard");
211:         ClipData primaryClip = clipboardManager == null ? null : clipboardManager.getPrimaryClip();
212:         if (primaryClip != null && primaryClip.getItemCount() > 0) {
213:             if (i3 >= 31) {
214:                 acgVar = new acg(primaryClip, 1);
215:             } else {
```

## `defpackage/ud3.java`
### line 4
```java
1: package defpackage;
2: 
3: import android.app.Activity;
4: import android.content.ClipData;
5: import android.os.Build;
6: import android.text.Selection;
7: import android.text.Spannable;
8: import android.view.DragEvent;
```

### line 20
```java
16:         int offsetForPosition = textView.getOffsetForPosition(dragEvent.getX(), dragEvent.getY());
17:         textView.beginBatchEdit();
18:         try {
19:             Selection.setSelection((Spannable) textView.getText(), offsetForPosition);
20:             ClipData clipData = dragEvent.getClipData();
21:             if (Build.VERSION.SDK_INT >= 31) {
22:                 acgVar = new acg(clipData, 3);
23:             } else {
24:                 ccg ccgVar = new ccg();
```

### line 39
```java
35: 
36:     public static boolean b(DragEvent dragEvent, View view, Activity activity) {
37:         bcg acgVar;
38:         activity.requestDragAndDropPermissions(dragEvent);
39:         ClipData clipData = dragEvent.getClipData();
40:         if (Build.VERSION.SDK_INT >= 31) {
41:             acgVar = new acg(clipData, 3);
42:         } else {
43:             ccg ccgVar = new ccg();
```

## `defpackage/xd.java`
### line 447
```java
443:         return jh7.e0(createCredentialException.getMessage(), createCredentialException.getType());
444:     }
445: 
446:     public static owi d(Intent intent, String str) {
447:         CreateCredentialResponse createCredentialResponse = (CreateCredentialResponse) intent.getParcelableExtra("android.service.credentials.extra.CREATE_CREDENTIAL_RESPONSE", CreateCredentialResponse.class);
448:         if (createCredentialResponse == null) {
449:             return null;
450:         }
451:         return if7.o(createCredentialResponse.getData(), str);
```

### line 463
```java
459:         return jh7.f0(getCredentialException.getMessage(), getCredentialException.getType());
460:     }
461: 
462:     public static jyp f(Intent intent) {
463:         GetCredentialResponse getCredentialResponse = (GetCredentialResponse) intent.getParcelableExtra("android.service.credentials.extra.GET_CREDENTIAL_RESPONSE", GetCredentialResponse.class);
464:         if (getCredentialResponse == null) {
465:             return null;
466:         }
467:         Credential credential = getCredentialResponse.getCredential();
```

## `defpackage/xr3.java`
### line 3
```java
1: package defpackage;
2: 
3: import android.content.ClipData;
4: import android.content.ClipDescription;
5: import android.content.Intent;
6: import java.util.List;
7: import java.util.Map;
```

### line 282
```java
278:                 }
279:                 if (str != null) {
280:                     mwuVarB.add("application/vnd.openai.rich-text-editor.markdown");
281:                 }
282:                 return hwvVar.a.b(new m8b(new ClipData(new ClipDescription("markdown_editor", (String[]) bvj.o(mwuVarB).toArray(new String[0])), new ClipData.Item(hvvVar.a, str2, str != null ? new Intent().putExtra("rich_markdown", str) : null, null))), psgVar2);
283:             case 11:
284:                 return ((wy20) this.receiver).H(((zch) obj).a, (psg) obj2);
285:             case 12:
286:                 Object objD = ((bj50) this.receiver).d((zm00) obj, (psg) obj2);
```

## `defpackage/zc4.java`
### line 3
```java
1: package defpackage;
2: 
3: import android.content.ClipData;
4: import android.content.ClipboardManager;
5: import kotlin.jvm.functions.Function1;
6: 
7: public final class zc4 implements o8b {
```

### line 23
```java
19:     }
20: 
21:     @Override
22:     public final Object b(m8b m8bVar, psg psgVar) {
23:         ClipData clipData;
24:         CharSequence text;
25:         String string;
26:         String string2;
27:         boolean z = this.c;
```

### line 31
```java
27:         boolean z = this.c;
28:         wec0 wec0Var = wec0.a;
29:         if (z) {
30:             this.c = false;
31:             if (m8bVar != null && (clipData = m8bVar.a) != null && clipData.getItemCount() != 0 && (text = clipData.getItemAt(0).getText()) != null && (string = text.toString()) != null && (string2 = qa90.W0(string).toString()) != null) {
32:                 if (string2.length() <= 0) {
33:                     string2 = null;
34:                 }
35:                 if (string2 != null) {
```

## `defpackage/zx6.java`
### line 3
```java
1: package defpackage;
2: 
3: import android.content.ClipData;
4: import kotlin.jvm.functions.Function2;
5: 
6: public final class zx6 extends gw90 implements Function2 {
7:     public final byte n;
```

### line 69
```java
65:             case 0:
66:                 boolean z = this.o;
67:                 if (!z) {
68:                     ct40.j(obj);
69:                     m8b m8bVar = new m8b(ClipData.newPlainText(str, str));
70:                     this.o = true;
71:                     return o8bVar.b(m8bVar, this) == wqiVar ? wqiVar : wec0Var;
72:                 }
73:                 if (z) {
```

### line 83
```java
79:             case 1:
80:                 boolean z2 = this.o;
81:                 if (!z2) {
82:                     ct40.j(obj);
83:                     m8b m8bVar2 = new m8b(ClipData.newPlainText(str, str));
84:                     this.o = true;
85:                     return o8bVar.b(m8bVar2, this) == wqiVar ? wqiVar : wec0Var;
86:                 }
87:                 if (z2) {
```

### line 97
```java
93:             case 2:
94:                 boolean z3 = this.o;
95:                 if (!z3) {
96:                     ct40.j(obj);
97:                     m8b m8bVar3 = new m8b(ClipData.newPlainText("codex_remote_thread", str));
98:                     this.o = true;
99:                     return o8bVar.b(m8bVar3, this) == wqiVar ? wqiVar : wec0Var;
100:                 }
101:                 if (z3) {
```

### line 111
```java
107:             case 3:
108:                 boolean z4 = this.o;
109:                 if (!z4) {
110:                     ct40.j(obj);
111:                     m8b m8bVar4 = new m8b(ClipData.newPlainText("Debug info", str));
112:                     this.o = true;
113:                     return o8bVar.b(m8bVar4, this) == wqiVar ? wqiVar : wec0Var;
114:                 }
115:                 if (z4) {
```

### line 125
```java
121:             default:
122:                 boolean z5 = this.o;
123:                 if (!z5) {
124:                     ct40.j(obj);
125:                     m8b m8bVar5 = new m8b(ClipData.newPlainText("Latex Formula", str));
126:                     this.o = true;
127:                     return o8bVar.b(m8bVar5, this) == wqiVar ? wqiVar : wec0Var;
128:                 }
129:                 if (z5) {
```

_files_with_hits=23; excerpts=58_
