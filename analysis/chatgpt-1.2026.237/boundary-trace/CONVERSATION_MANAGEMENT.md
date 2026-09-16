# CONVERSATION_MANAGEMENT

## `defpackage/ba70.java`
### line 5
```java
1: package defpackage;
2: 
3: public enum ba70 {
4:     Post("post"),
5:     SharedConversation("shared_conversation");
6: 
7:     public final String a;
8: 
9:     ba70(String str) {
```

## `defpackage/bc80.java`
### line 34
```java
30:         pluginGeneratedSerialDescriptor.k("sessionId", true);
31:         pluginGeneratedSerialDescriptor.k("userId", true);
32:         pluginGeneratedSerialDescriptor.k("accountId", true);
33:         pluginGeneratedSerialDescriptor.k("conversationId", true);
34:         pluginGeneratedSerialDescriptor.k("isSharedConversation", true);
35:         pluginGeneratedSerialDescriptor.k("original_message_id", true);
36:         pluginGeneratedSerialDescriptor.k("appPackageName", true);
37:         pluginGeneratedSerialDescriptor.k("messages", true);
38:         pluginGeneratedSerialDescriptor.k("widgetStateCache", true);
```

## `defpackage/bqk.java`
### line 72
```java
68:                 break;
69:             case 11:
70:                 super(mwjVar2);
71:                 this.e = Collections.singletonList("s/c_{conversationId}");
72:                 this.f = Collections.singletonList("s/c_sample-shared-conversation-id");
73:                 break;
74:             case 12:
75:                 super(mwjVar2);
76:                 this.e = bvj.T("s/t_{postId}", "s/p_{postId}", "s/w_{postId}");
```

## `defpackage/btg.java`
### line 28
```java
24:         pluginGeneratedSerialDescriptor.k("currentLeafNodeId", true);
25:         pluginGeneratedSerialDescriptor.k("title", true);
26:         pluginGeneratedSerialDescriptor.k("moderationResults", true);
27:         pluginGeneratedSerialDescriptor.k("safeUrlMap", true);
28:         pluginGeneratedSerialDescriptor.k("sharedConversationId", true);
29:         pluginGeneratedSerialDescriptor.k("defaultModelSlug", true);
30:         pluginGeneratedSerialDescriptor.k("conversationOrigin", true);
31:         pluginGeneratedSerialDescriptor.k("gizmoId", true);
32:         pluginGeneratedSerialDescriptor.k("gizmoType", true);
```

## `defpackage/dja.java`
### line 19
```java
15:             iArr[ChatgptShareFlowContentType.CHATGPT_SHARE_FLOW_CONTENT_TYPE_POST_SLICE.ordinal()] = 2;
16:         } catch (NoSuchFieldError unused2) {
17:         }
18:         try {
19:             iArr[ChatgptShareFlowContentType.CHATGPT_SHARE_FLOW_CONTENT_TYPE_SHARED_CONVERSATION.ordinal()] = 3;
20:         } catch (NoSuchFieldError unused3) {
21:         }
22:         a = iArr;
23:     }
```

## `defpackage/drr.java`
### line 95
```java
91:         return arrayList;
92:     }
93: 
94:     public final void A(v4s v4sVar) {
95:         this.n.o(gls.p0(pat.x(vqi.d(this.m, "ImageDetailUseCase/stageImageForShare"), null, 0, new crr(this, v4sVar, null, (byte) 2), 3), cm7.k(v4sVar), this.k.e(new Object[0], R.plurals.conversations_image_share_intent_plural, 1)));
96:     }
97: 
98:     public final Object t(v4s v4sVar, rsg rsgVar) {
99:         zqr zqrVar;
```

## `defpackage/dwk.java`
### line 509
```java
505:         }
506:         if (l() != null) {
507:             return "Conversation (Gizmo)";
508:         }
509:         return this.d != null ? "Shared Conversation" : "Conversation";
510:     }
511: 
512:     @Override
513:     public final ldl b0() {
```

## `defpackage/e7t.java`
### line 9
```java
5:     public static final e7t b;
6:     public static final e7t[] c;
7: 
8:     static {
9:         e7t e7tVar = new e7t("ShareConversation", 0);
10:         a = e7tVar;
11:         e7t e7tVar2 = new e7t("DoNotShareConversation", 1);
12:         b = e7tVar2;
13:         c = new e7t[]{e7tVar, e7tVar2};
```

## `defpackage/eja.java`
### line 29
```java
25:             if (i != 3) {
26:                 d7y.b();
27:                 return;
28:             }
29:             str = "CHATGPT_SHARE_FLOW_CONTENT_TYPE_SHARED_CONVERSATION";
30:         }
31:         encoder.G(str);
32:     }
33: }
```

## `defpackage/ez60.java`
### line 24
```java
20:         this.U0 = o0iVar;
21:         this.V0 = p770Var;
22:         this.W0 = d470Var;
23:         this.X0 = q8iVar;
24:         this.Y0 = wnm.F(6, "SharedConversationViewModel");
25:         psg psgVar = null;
26:         w(d470Var, new el60((Object) this, (byte) 2), null);
27:         C(new kax(nyc0Var.f, (byte) 14), new av60(3, psgVar, (byte) 4));
28:         bvj.t(h2hVar.a(), this.X, new o710(this, psgVar, (byte) 29));
```

## `defpackage/fi40.java`
### line 20
```java
16: 
17:     static {
18:         fi40 fi40Var = new fi40("Conversation", 0);
19:         a = fi40Var;
20:         fi40 fi40Var2 = new fi40("SharedConversation", 1);
21:         b = fi40Var2;
22:         fi40 fi40Var3 = new fi40("CalpicoRoom", 2);
23:         c = fi40Var3;
24:         fi40 fi40Var4 = new fi40("CalpicoProfile", 3);
```

## `defpackage/fvw.java`
### line 81
```java
77:         return bfyVar;
78:     }
79: 
80:     public final Object c(String str, String str2, String str3, rsg rsgVar) {
81:         return f(dvv.D0(new g100("sharedConversationId", str), new g100("messageId", str2)), new bvw(this, str, str2, str3, null, (byte) 1), rsgVar);
82:     }
83: 
84:     public final Object d(String str, String str2, String str3, Map map, rsg rsgVar) {
85:         dvw dvwVar;
```

## `defpackage/ina.java`
### line 23
```java
19:             iArr[ChatgptThreadNavigationSource.CHATGPT_THREAD_NAVIGATION_SOURCE_FOR_YOU_FEEDBACK.ordinal()] = 3;
20:         } catch (NoSuchFieldError unused3) {
21:         }
22:         try {
23:             iArr[ChatgptThreadNavigationSource.CHATGPT_THREAD_NAVIGATION_SOURCE_SHARED_CONVERSATION.ordinal()] = 4;
24:         } catch (NoSuchFieldError unused4) {
25:         }
26:         try {
27:             iArr[ChatgptThreadNavigationSource.CHATGPT_THREAD_NAVIGATION_SOURCE_PROJECT_CONVERSATION.ordinal()] = 5;
```

## `defpackage/jna.java`
### line 30
```java
26:             case 3:
27:                 str = "CHATGPT_THREAD_NAVIGATION_SOURCE_FOR_YOU_FEEDBACK";
28:                 break;
29:             case 4:
30:                 str = "CHATGPT_THREAD_NAVIGATION_SOURCE_SHARED_CONVERSATION";
31:                 break;
32:             case 5:
33:                 str = "CHATGPT_THREAD_NAVIGATION_SOURCE_PROJECT_CONVERSATION";
34:                 break;
```

## `defpackage/kfa.java`
### line 27
```java
23:             iArr[ChatgptPinningOutcome.CHATGPT_PINNING_OUTCOME_MAX_PINS_REACHED.ordinal()] = 4;
24:         } catch (NoSuchFieldError unused4) {
25:         }
26:         try {
27:             iArr[ChatgptPinningOutcome.CHATGPT_PINNING_OUTCOME_SHARED_PROJECT_CONVERSATION.ordinal()] = 5;
28:         } catch (NoSuchFieldError unused5) {
29:         }
30:         a = iArr;
31:     }
```

## `defpackage/lfa.java`
### line 33
```java
29:             if (i != 5) {
30:                 d7y.b();
31:                 return;
32:             }
33:             str = "CHATGPT_PINNING_OUTCOME_SHARED_PROJECT_CONVERSATION";
34:         }
35:         encoder.G(str);
36:     }
37: }
```

## `defpackage/mdy.java`
### line 13
```java
9:     static {
10:         mdy mdyVar = new mdy();
11:         f = mdyVar;
12:         g = mdyVar.c("stream_response_bodies", 100, true);
13:         h = mdyVar.c("stream_shared_conversation_response_bodies", 100, false);
14:         i = mdyVar.d(0.3d, 100, "logging_sample_rate");
15:     }
16: }
```

## `defpackage/nja.java`
### line 23
```java
19:             iArr[ChatgptShareFlowSource.CHATGPT_SHARE_FLOW_SOURCE_MESSAGE_LONG_PRESS.ordinal()] = 3;
20:         } catch (NoSuchFieldError unused3) {
21:         }
22:         try {
23:             iArr[ChatgptShareFlowSource.CHATGPT_SHARE_FLOW_SOURCE_CONVERSATION_MENU.ordinal()] = 4;
24:         } catch (NoSuchFieldError unused4) {
25:         }
26:         try {
27:             iArr[ChatgptShareFlowSource.CHATGPT_SHARE_FLOW_SOURCE_IMAGE_VIEWER.ordinal()] = 5;
```

### line 43
```java
39:             iArr[ChatgptShareFlowSource.CHATGPT_SHARE_FLOW_SOURCE_MESSAGE_PROMPT_SHARE_LONG_PRESS.ordinal()] = 8;
40:         } catch (NoSuchFieldError unused8) {
41:         }
42:         try {
43:             iArr[ChatgptShareFlowSource.CHATGPT_SHARE_FLOW_SOURCE_IMAGE_LIGHTBOX_CONVERSATION.ordinal()] = 9;
44:         } catch (NoSuchFieldError unused9) {
45:         }
46:         try {
47:             iArr[ChatgptShareFlowSource.CHATGPT_SHARE_FLOW_SOURCE_IMAGE_LIBRARY_LIGHTBOX.ordinal()] = 10;
```

## `defpackage/oh40.java`
### line 25
```java
21:         pluginGeneratedSerialDescriptor.k("projectId", true);
22:         pluginGeneratedSerialDescriptor.k("calpicoRoomId", true);
23:         pluginGeneratedSerialDescriptor.k("calpicoMessageId", true);
24:         pluginGeneratedSerialDescriptor.k("conversationId", true);
25:         pluginGeneratedSerialDescriptor.k("sharedConversationId", true);
26:         pluginGeneratedSerialDescriptor.k("shareId", true);
27:         pluginGeneratedSerialDescriptor.k("productId", true);
28:         pluginGeneratedSerialDescriptor.k("profileId", true);
29:         pluginGeneratedSerialDescriptor.k("conversationOwnerId", true);
```

## `defpackage/oja.java`
### line 30
```java
26:             case 3:
27:                 str = "CHATGPT_SHARE_FLOW_SOURCE_MESSAGE_LONG_PRESS";
28:                 break;
29:             case 4:
30:                 str = "CHATGPT_SHARE_FLOW_SOURCE_CONVERSATION_MENU";
31:                 break;
32:             case 5:
33:                 str = "CHATGPT_SHARE_FLOW_SOURCE_IMAGE_VIEWER";
34:                 break;
```

### line 45
```java
41:             case 8:
42:                 str = "CHATGPT_SHARE_FLOW_SOURCE_MESSAGE_PROMPT_SHARE_LONG_PRESS";
43:                 break;
44:             case 9:
45:                 str = "CHATGPT_SHARE_FLOW_SOURCE_IMAGE_LIGHTBOX_CONVERSATION";
46:                 break;
47:             case 10:
48:                 str = "CHATGPT_SHARE_FLOW_SOURCE_IMAGE_LIBRARY_LIGHTBOX";
49:                 break;
```

## `defpackage/q5i.java`
### line 9
```java
5: public final class q5i implements Runnable {
6:     public final byte a;
7:     public final ConversationScreenShareSettingsGuideActivity b;
8: 
9:     public q5i(ConversationScreenShareSettingsGuideActivity conversationScreenShareSettingsGuideActivity, byte b) {
10:         this.a = b;
11:         this.b = conversationScreenShareSettingsGuideActivity;
12:     }
13: 
```

### line 17
```java
13: 
14:     @Override
15:     public final void run() {
16:         byte b = this.a;
17:         ConversationScreenShareSettingsGuideActivity conversationScreenShareSettingsGuideActivity = this.b;
18:         switch (b) {
19:             case 0:
20:                 int i = ConversationScreenShareSettingsGuideActivity.A;
21:                 conversationScreenShareSettingsGuideActivity.i();
```

## `defpackage/qqh.java`
### line 56
```java
52:             return;
53:         }
54:         byte b = 0;
55:         if (jqhVar instanceof wph) {
56:             vqi.c(this.m, "ConversationManagementUseCase/archiveConversation", null, 0, new mqh(b, psgVar, ((wph) jqhVar).b(), this), 6);
57:             return;
58:         }
59:         if (jqhVar instanceof xph) {
60:             vqi.c(this.m, "ConversationManagementUseCase/deleteConversation", null, 0, new mqh((byte) 1, psgVar, ((xph) jqhVar).b(), this), 6);
```

### line 69
```java
65:             boolean zD = cqhVar.d();
66:             Function0 function0B = cqhVar.b();
67:             le0 le0Var = new le0(this);
68:             zi0 zi0Var = this.n;
69:             vqi.c((lm) zi0Var.e, "ConversationPinningHandler/setConversationPinned", null, 0, new ef8((Object) function0B, (Object) zi0Var, (Serializable) le0Var, zD, (psg) null, (byte) 4), 6);
70:             return;
71:         }
72:         if (jqhVar instanceof dqh) {
73:             dqh dqhVar = (dqh) jqhVar;
```

### line 244
```java
240:         usv usvVar = new usv();
241:         usvVar.put("share_link_id", n970Var.a());
242:         String strC = n970Var.c();
243:         if (strC != null) {
244:             usvVar.put("shared_conversation_id", strC);
245:         }
246:         this.p.k(gn0Var, usvVar.b());
247:     }
248: 
```

## `defpackage/sw9.java`
### line 14
```java
10: 
11:     @Override
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptCodeBlockShareButtonClicked chatgptCodeBlockShareButtonClicked = (ChatgptCodeBlockShareButtonClicked) aVar;
14:         if (chatgptCodeBlockShareButtonClicked.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptCodeBlockShareButtonClicked.getConversation_id());
16:         }
17:         if (chatgptCodeBlockShareButtonClicked.getLanguage() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptCodeBlockShareButtonClicked.getLanguage());
```

## `defpackage/tsg.java`
### line 19
```java
15:         a = tsgVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("2bM-1LL9CmwrhVdngu9ymTDPF04SeBE_0pRKGcPxDlg=", tsgVar, 5);
17:         pluginGeneratedSerialDescriptor.k("displayName", false);
18:         pluginGeneratedSerialDescriptor.k("isAnonymous", true);
19:         pluginGeneratedSerialDescriptor.k("isFromSharedConversation", true);
20:         pluginGeneratedSerialDescriptor.k("picture", true);
21:         pluginGeneratedSerialDescriptor.k("isGizmo", true);
22:         descriptor = pluginGeneratedSerialDescriptor;
23:     }
```

## `defpackage/vtl.java`
### line 7
```java
3: public abstract class vtl {
4:     public static final byte[] a = new byte[122784];
5: 
6:     static {
7:         String[] strArr = {"timedownlifeleftbackcodedatashowonlysitecityopenjustlikefreeworktextyearoverbodyloveformbookplaylivelinehelphomesidemorewordlongthemviewfindpagedaysfullheadtermeachareafromtruemarkableuponhighdatelandnewsevennextcasebothpostusedmadehandherewhatnameLinkblogsizebaseheldmakemainuser') +holdendswithNewsreadweresigntakehavegameseencallpathwellplusmenufilmpartjointhislistgoodneedwayswestjobsmindalsologorichuseslastteamarmyfoodkingwilleastwardbestfirePageknowaway.pngmovethanloadgiveselfnotemuchfeedmanyrockicononcelookhidediedHomerulehostajaxinfoclublawslesshalfsomesuchzone100%onescareTimeracebluefourweekfacehopegavehardlostwhenparkkeptpassshiproomHTMLplanTypedonesavekeep
8:         int length = 0;
9:         for (int i = 0; i < 3; i++) {
10:             length += strArr[i].length();
11:         }
```

## `defpackage/y46.java`
### line 26
```java
22:     OpenWorkTab("open_work_tab"),
23:     OpenWorkTabAndSendPrompt("open_work_tab_and_send_prompt"),
24:     OpenPcaConnectorAuthModal("open_pca_connector_auth_modal"),
25:     ConnectLedgerAccounts("connect_ledger_accounts"),
26:     ShareConversation("share_conversation"),
27:     ShareGroupChat("share_group_chat"),
28:     ShareMessageSlice("share_message_slice"),
29:     InstallWidget("install_mobile_widget"),
30:     ShowAds("show_ads"),
```

### line 43
```java
39:     public static final x46 Companion = new x46();
40:     public static final uzt b = f9t.F(2, new li5(17));
41: 
42:     static {
43:         f = new hon(new y46[]{r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, new y46("system_hint"), new y46("open_url"), new y46("open_local_url"), new y46("open_work_tab"), new y46("open_work_tab_and_send_prompt"), new y46("open_pca_connector_auth_modal"), new y46("connect_ledger_accounts"), new y46("share_conversation"), new y46("share_group_chat"), new y46("share_message_slice"), new y46("install_mobile_widget"), new y46("show_ads"), new y46("age_verification"), new y46("open_pepper_onboarding_modal"), new y46("update_personality_trait"), new y46("start_voice"), new y46("request_system_notification_permission")});
44:     }
45: 
46:     public y46(String str) {
47:         super(str, i);
```

## `defpackage/yc70.java`
### line 27
```java
23:         yc70 yc70Var = new yc70();
24:         f = yc70Var;
25:         g = yc70Var.c("enable_direct_conversation_share", 127, true);
26:         h = yc70Var.c("enable_conversation_share_image_alternatives", 127, true);
27:         i = yc70Var.c("use_v2_shared_conversation_endpoint", 127, false);
28:         j = yc70Var.c("skip-incomplete-share-nodes", 126, false);
29:         k = yc70Var.c("enable_screenshot_custom_share_sheet", 128, false);
30:         l = yc70Var.c("screenshot_share_include_link", 128, false);
31:         m = yc70Var.c("enable_prompt_share", 127, true);
```

### line 34
```java
30:         l = yc70Var.c("screenshot_share_include_link", 128, false);
31:         m = yc70Var.c("enable_prompt_share", 127, true);
32:         n = yc70Var.c("image_prompt_share_creation_enabled", MlKitException.MODEL_HASH_MISMATCH, false);
33:         o = yc70Var.c("image_prompt_share_consumption_enabled", MlKitException.MODEL_HASH_MISMATCH, false);
34:         p = yc70Var.c("skip_shared_conversation_preview", 3, false);
35:         q = yc70Var.c("land_shared_conversation_at_top", 3, false);
36:         r = yc70Var.c("is_enabled", 4, false);
37:         s = yc70Var.c("preserve_shared_conversation_on_continue", 3, true);
38:         t = yc70Var.c("disable_prompt_share", 3, false);
```

_files_with_hits=27; excerpts=34_
