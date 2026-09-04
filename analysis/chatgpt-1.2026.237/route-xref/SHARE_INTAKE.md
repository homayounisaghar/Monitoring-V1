# SHARE_INTAKE

## `com/openai/valdi/filesaver/MobileFileSaverNativeModuleFactoryImpl.java`
### line 74
```java
62:                             throw th;
63:                         } catch (Throwable th2) {
64:                             lpf.s(outputStreamOpenOutputStream, th);
65:                             throw th2;
66:                         }
67:                     }
68:                 } else {
69:                     wec0Var = null;
70:                 }
71:                 if (wec0Var == null) {
72:                     throw new IllegalStateException("Unable to write " + request.get_filename());
73:                 }
74:                 Intent intent = new Intent("android.intent.action.SEND");
75:                 intent.setType(request.get_mimeType());
76:                 intent.setClipData(ClipData.newUri(contentResolver, request.get_filename(), uriInsert));
77:                 intent.putExtra("android.intent.extra.STREAM", uriInsert);
78:                 intent.putExtra("android.intent.extra.TITLE", request.get_filename());
79:                 intent.putExtra("android.intent.extra.SUBJECT", request.get_filename());
80:                 intent.addFlags(1);
81:                 intent.addFlags(268435456);
82:                 context.startActivity(Intent.createChooser(intent, request.get_filename()).addFlags(268435456));
83:             } else {
84:                 File externalFilesDir = context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
85:                 if (externalFilesDir == null) {
86:                     externalFilesDir = new File(context.getCacheDir(), Environment.DIRECTORY_DOWNLOADS);
```

## `defpackage/lh8.java`
### line 188
```java
176:                 ct40.j(objU);
177:                 return objU;
178:             }
179:             tr0.l("call to 'resume' before 'invoke' with coroutine");
180:             return null;
181:         }
182:         ct40.j(objU);
183:         String str = (String) objU;
184:         if (str == null) {
185:             return wec0.a;
186:         }
187:         Intent intent = new Intent();
188:         intent.setAction("android.intent.action.SEND");
189:         intent.setType("text/plain");
190:         intent.putExtra("android.intent.extra.TEXT", str);
191:         nw80 nw80Var = new nw80(Intent.createChooser(intent, null), null);
192:         kh8Var.p = 2;
193:         Object objS = this.d.s(nw80Var, kh8Var);
194:         return objS == obj ? obj : objS;
195:     }
196: 
197:     public final void w(Function1 function1) {
198:         mz80 mz80Var;
199:         Object value;
200:         oet oetVar = this.h;
```

## `defpackage/ud3.java`
### line 20
```java
8: import android.view.DragEvent;
9: import android.view.View;
10: import android.widget.TextView;
11: 
12: public abstract class ud3 {
13:     public static boolean a(DragEvent dragEvent, TextView textView, Activity activity) {
14:         bcg acgVar;
15:         activity.requestDragAndDropPermissions(dragEvent);
16:         int offsetForPosition = textView.getOffsetForPosition(dragEvent.getX(), dragEvent.getY());
17:         textView.beginBatchEdit();
18:         try {
19:             Selection.setSelection((Spannable) textView.getText(), offsetForPosition);
20:             ClipData clipData = dragEvent.getClipData();
21:             if (Build.VERSION.SDK_INT >= 31) {
22:                 acgVar = new acg(clipData, 3);
23:             } else {
24:                 ccg ccgVar = new ccg();
25:                 ccgVar.b = clipData;
26:                 ccgVar.c = (byte) 3;
27:                 acgVar = ccgVar;
28:             }
29:             nnd0.i(textView, acgVar.build());
30:             return true;
31:         } finally {
32:             textView.endBatchEdit();
```

### line 39
```java
27:                 acgVar = ccgVar;
28:             }
29:             nnd0.i(textView, acgVar.build());
30:             return true;
31:         } finally {
32:             textView.endBatchEdit();
33:         }
34:     }
35: 
36:     public static boolean b(DragEvent dragEvent, View view, Activity activity) {
37:         bcg acgVar;
38:         activity.requestDragAndDropPermissions(dragEvent);
39:         ClipData clipData = dragEvent.getClipData();
40:         if (Build.VERSION.SDK_INT >= 31) {
41:             acgVar = new acg(clipData, 3);
42:         } else {
43:             ccg ccgVar = new ccg();
44:             ccgVar.b = clipData;
45:             ccgVar.c = (byte) 3;
46:             acgVar = ccgVar;
47:         }
48:         nnd0.i(view, acgVar.build());
49:         return true;
50:     }
51: }
```

_files=3; excerpts=4_