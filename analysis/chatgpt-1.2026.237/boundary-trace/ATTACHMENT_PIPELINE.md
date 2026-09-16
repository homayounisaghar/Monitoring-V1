# ATTACHMENT_PIPELINE

## `com/openai/feature/conversations/impl/coordinator/PendingAttachmentPreparationHandler$PendingAttachmentRateLimitedException.java`
### line 5
```java
1: package com.openai.feature.conversations.impl.coordinator;
2: 
3: import kotlin.Metadata;
4: 
5: @Metadata(d1 = {"\u0000\f\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0001\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"com/openai/feature/conversations/impl/coordinator/PendingAttachmentPreparationHandler$PendingAttachmentRateLimitedException", "Ljava/lang/Exception;", "Lkotlin/Exception;", "impl"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: public final class PendingAttachmentPreparationHandler$PendingAttachmentRateLimitedException extends Exception {
7: }
```

## `defpackage/d4a.java`
### line 11
```java
7: 
8:     static {
9:         int[] iArr = new int[ChatgptFileUploadStepStatus.values().length];
10:         try {
11:             iArr[ChatgptFileUploadStepStatus.CHATGPT_FILE_UPLOAD_STEP_STATUS_UNSPECIFIED.ordinal()] = 1;
12:         } catch (NoSuchFieldError unused) {
13:         }
14:         try {
15:             iArr[ChatgptFileUploadStepStatus.CHATGPT_FILE_UPLOAD_STEP_STATUS_STARTED.ordinal()] = 2;
```

### line 19
```java
15:             iArr[ChatgptFileUploadStepStatus.CHATGPT_FILE_UPLOAD_STEP_STATUS_STARTED.ordinal()] = 2;
16:         } catch (NoSuchFieldError unused2) {
17:         }
18:         try {
19:             iArr[ChatgptFileUploadStepStatus.CHATGPT_FILE_UPLOAD_STEP_STATUS_SUCCEEDED.ordinal()] = 3;
20:         } catch (NoSuchFieldError unused3) {
21:         }
22:         try {
23:             iArr[ChatgptFileUploadStepStatus.CHATGPT_FILE_UPLOAD_STEP_STATUS_FAILED.ordinal()] = 4;
```

### line 27
```java
23:             iArr[ChatgptFileUploadStepStatus.CHATGPT_FILE_UPLOAD_STEP_STATUS_FAILED.ordinal()] = 4;
24:         } catch (NoSuchFieldError unused4) {
25:         }
26:         try {
27:             iArr[ChatgptFileUploadStepStatus.CHATGPT_FILE_UPLOAD_STEP_STATUS_CANCELLED.ordinal()] = 5;
28:         } catch (NoSuchFieldError unused5) {
29:         }
30:         a = iArr;
31:     }
```

## `defpackage/e4a.java`
### line 21
```java
17:     public final void serialize(Encoder encoder, Object obj) {
18:         String str;
19:         int i = d4a.a[((ChatgptFileUploadStepStatus) obj).ordinal()];
20:         if (i == 1) {
21:             str = "CHATGPT_FILE_UPLOAD_STEP_STATUS_UNSPECIFIED";
22:         } else if (i == 2) {
23:             str = "CHATGPT_FILE_UPLOAD_STEP_STATUS_STARTED";
24:         } else if (i == 3) {
25:             str = "CHATGPT_FILE_UPLOAD_STEP_STATUS_SUCCEEDED";
```

### line 27
```java
23:             str = "CHATGPT_FILE_UPLOAD_STEP_STATUS_STARTED";
24:         } else if (i == 3) {
25:             str = "CHATGPT_FILE_UPLOAD_STEP_STATUS_SUCCEEDED";
26:         } else if (i == 4) {
27:             str = "CHATGPT_FILE_UPLOAD_STEP_STATUS_FAILED";
28:         } else {
29:             if (i != 5) {
30:                 d7y.b();
31:                 return;
```

### line 33
```java
29:             if (i != 5) {
30:                 d7y.b();
31:                 return;
32:             }
33:             str = "CHATGPT_FILE_UPLOAD_STEP_STATUS_CANCELLED";
34:         }
35:         encoder.G(str);
36:     }
37: }
```

## `defpackage/fyk.java`
### line 17
```java
13:     static {
14:         fyk fykVar = new fyk();
15:         a = fykVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("IiDhd-FkyOiWjSD10dGGI7wTZOC1MgO371lS_ZWYa4c=", fykVar, 3);
17:         pluginGeneratedSerialDescriptor.k("attachmentUri", true);
18:         pluginGeneratedSerialDescriptor.l(new k3l());
19:         pluginGeneratedSerialDescriptor.k("attachmentAssetPointer", true);
20:         pluginGeneratedSerialDescriptor.k("focusKeyboard", true);
21:         descriptor = pluginGeneratedSerialDescriptor;
```

## `defpackage/jvg.java`
### line 37
```java
33:         mz80 mz80VarM = ykj.m(wfn.a);
34:         this.f = mz80VarM;
35:         this.g = new zj60(new evg(this, (byte) 0), obj);
36:         Class<jvg> cls = jvg.class;
37:         qzhVar.b("ConversationAttachmentsRegistry/abandonCleanupLeases", new tug(1, this, cls, "release", "release()V", 4, (byte) 1));
38:         this.h = new heh0((Object) new r2(1, this, cls, "entry", "entry(Ljava/lang/String;)Lcom/openai/feature/conversations/upload/UploadRegistryEntry;", 0, (byte) 9), (Object) new evg(this, (byte) 1), (byte) 16);
39:         this.i = new jt(mz80VarM, (byte) 5);
40:     }
41: 
```

## `defpackage/wko.java`
### line 258
```java
254:                     uri3 = vkoVar.o;
255:                     application3 = vkoVar.n;
256:                     ct40.j(obj2);
257:                 }
258:                 gev.d(gevVar, "Recovered content URI upload with unknown size", null, null, 14);
259:                 file3 = (File) obj2;
260:                 lC = l;
261:                 uri2 = uri3;
262:                 application2 = application3;
```

### line 283
```java
279:                 application2 = application;
280:                 uri2 = uri;
281:                 j2 = j;
282:                 if (i != 0) {
283:                     gev.d(gevVar, "Content URI upload has unknown size", null, Collections.singletonMap("recoveryEnabled", Boolean.valueOf(z)), 10);
284:                 }
285:                 if (z) {
286:                     long j4 = j2;
287:                     Uri uri4 = uri2;
```

### line 304
```java
300:                     if (objQ != obj3) {
301:                         Long l3 = lC;
302:                         obj2 = objQ;
303:                         l = l3;
304:                         gev.d(gevVar, "Recovered content URI upload with unknown size", null, null, 14);
305:                         file3 = (File) obj2;
306:                         lC = l;
307:                         uri2 = uri3;
308:                         application2 = application3;
```

### line 342
```java
338:             if (((Boolean) obj).booleanValue()) {
339:                 z = true;
340:             }
341:             if (i != 0) {
342:                 gev.d(gevVar, "Content URI upload has unknown size", null, Collections.singletonMap("recoveryEnabled", Boolean.valueOf(z)), 10);
343:             }
344:             if (z) {
345:                 long j5 = j2;
346:                 Uri uri5 = uri2;
```

### line 363
```java
359:                 if (objQ != obj3) {
360:                     Long l4 = lC;
361:                     obj2 = objQ;
362:                     l = l4;
363:                     gev.d(gevVar, "Recovered content URI upload with unknown size", null, null, 14);
364:                     file3 = (File) obj2;
365:                     lC = l;
366:                     uri2 = uri3;
367:                     application2 = application3;
```

## `defpackage/x3a.java`
### line 11
```java
7: 
8:     static {
9:         int[] iArr = new int[ChatgptFileUploadImageOrigin.values().length];
10:         try {
11:             iArr[ChatgptFileUploadImageOrigin.CHATGPT_FILE_UPLOAD_IMAGE_ORIGIN_UNSPECIFIED.ordinal()] = 1;
12:         } catch (NoSuchFieldError unused) {
13:         }
14:         try {
15:             iArr[ChatgptFileUploadImageOrigin.CHATGPT_FILE_UPLOAD_IMAGE_ORIGIN_SCREENSHOT_LIKE.ordinal()] = 2;
```

### line 19
```java
15:             iArr[ChatgptFileUploadImageOrigin.CHATGPT_FILE_UPLOAD_IMAGE_ORIGIN_SCREENSHOT_LIKE.ordinal()] = 2;
16:         } catch (NoSuchFieldError unused2) {
17:         }
18:         try {
19:             iArr[ChatgptFileUploadImageOrigin.CHATGPT_FILE_UPLOAD_IMAGE_ORIGIN_CAMERA_LIKE.ordinal()] = 3;
20:         } catch (NoSuchFieldError unused3) {
21:         }
22:         try {
23:             iArr[ChatgptFileUploadImageOrigin.CHATGPT_FILE_UPLOAD_IMAGE_ORIGIN_OTHER_IMAGE.ordinal()] = 4;
```

## `defpackage/y3a.java`
### line 21
```java
17:     public final void serialize(Encoder encoder, Object obj) {
18:         String str;
19:         int i = x3a.a[((ChatgptFileUploadImageOrigin) obj).ordinal()];
20:         if (i == 1) {
21:             str = "CHATGPT_FILE_UPLOAD_IMAGE_ORIGIN_UNSPECIFIED";
22:         } else if (i == 2) {
23:             str = "CHATGPT_FILE_UPLOAD_IMAGE_ORIGIN_SCREENSHOT_LIKE";
24:         } else if (i == 3) {
25:             str = "CHATGPT_FILE_UPLOAD_IMAGE_ORIGIN_CAMERA_LIKE";
```

### line 31
```java
27:             if (i != 4) {
28:                 d7y.b();
29:                 return;
30:             }
31:             str = "CHATGPT_FILE_UPLOAD_IMAGE_ORIGIN_OTHER_IMAGE";
32:         }
33:         encoder.G(str);
34:     }
35: }
```

## `defpackage/zb9.java`
### line 5
```java
1: package defpackage;
2: 
3: @ii60(with = tx4.class)
4: public final class zb9 {
5:     FileUploadDocument("actions"),
6:     Code("code"),
7:     CurrentEvent("current-event"),
8:     Dalle("dalle"),
9:     ImageGen("image-gen"),
```

### line 21
```java
17:     RankOrRate("rank-or-rate"),
18:     ReadOrAnalyze("read-or-analyze"),
19:     Shop("shop"),
20:     Travel("teach-or-explain"),
21:     FileUploadDocument("trending"),
22:     Travel("travel"),
23:     FileUploadDocument("weather"),
24:     Write("write"),
25:     FileUploadDocument("vision"),
```

### line 27
```java
23:     FileUploadDocument("weather"),
24:     Write("write"),
25:     FileUploadDocument("vision"),
26:     Browse("browse"),
27:     FileUploadDocument("file-upload-document"),
28:     Unknown("unknown");
29: 
30:     public static final hon h;
31:     public final String a;
```

_files_with_hits=9; excerpts=21_
