# DEEPLINK_QUERY

## `defpackage/a570.java`
### line 27
```java
15:         a570 a570Var = new a570();
16:         a = a570Var;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("0cm-AKTJ2NW0VFFhKcy7vrBx5DbrXqkbOH2496CXYX0=", a570Var, 10);
18:         pluginGeneratedSerialDescriptor.k("title", false);
19:         pluginGeneratedSerialDescriptor.k("prompt", false);
20:         pluginGeneratedSerialDescriptor.k("schedule", false);
21:         pluginGeneratedSerialDescriptor.k("timingMode", false);
22:         pluginGeneratedSerialDescriptor.k("sourceTimezone", false);
23:         pluginGeneratedSerialDescriptor.k("importable", false);
24:         pluginGeneratedSerialDescriptor.k("ownerAutomationId", true);
25:         pluginGeneratedSerialDescriptor.k("sourceAutomationId", true);
26:         pluginGeneratedSerialDescriptor.k("conversationOrigin", true);
27:         pluginGeneratedSerialDescriptor.k("modelSelection", true);
28:         descriptor = pluginGeneratedSerialDescriptor;
29:     }
30: 
31:     @Override
32:     public final KSerializer[] childSerializers() {
33:         da90 da90Var = da90.a;
34:         ee5 ee5Var = ee5.a;
35:         return new KSerializer[]{da90Var, da90Var, da90Var, da90Var, da90Var, wh6.a, q2v.r0(ee5Var), q2v.r0(ee5Var), q2v.r0(da90Var), q2v.r0(m570.a)};
36:     }
37: 
38:     @Override
39:     public final Object deserialize(Decoder decoder) {
```

## `defpackage/bpk.java`
### line 98
```java
86: 
87:     @Override
88:     public final List g() {
89:         byte b = this.d;
90:         return vfn.a;
91:     }
92: 
93:     @Override
94:     public m350 n(m350 m350Var, Uri uri) {
95:         switch (this.d) {
96:             case 1:
97:                 fpk fpkVar = (fpk) m350Var;
98:                 Set<String> queryParameterNames = uri.getQueryParameterNames();
99:                 int iX0 = evv.x0(gke.r0(queryParameterNames, 10));
100:                 if (iX0 < 16) {
101:                     iX0 = 16;
102:                 }
103:                 LinkedHashMap linkedHashMap = new LinkedHashMap(iX0);
104:                 for (Object obj : queryParameterNames) {
105:                     String queryParameter = uri.getQueryParameter((String) obj);
106:                     if (queryParameter == null) {
107:                         queryParameter = "";
108:                     }
109:                     linkedHashMap.put(obj, queryParameter);
110:                 }
```

### line 117
```java
105:                     String queryParameter = uri.getQueryParameter((String) obj);
106:                     if (queryParameter == null) {
107:                         queryParameter = "";
108:                     }
109:                     linkedHashMap.put(obj, queryParameter);
110:                 }
111:                 return new fpk(fpkVar.a, linkedHashMap);
112:             case 5:
113:                 szk szkVar = (szk) m350Var;
114:                 return new szk(m95.n("m_", szkVar.a), szkVar.b, szkVar.c, szkVar.d, szkVar.e, szkVar.f, szkVar.g, szkVar.h, true);
115:             case 11:
116:                 hbl hblVar = (hbl) m350Var;
117:                 return new hbl(hblVar.a, uri.getQueryParameter("campaign"), hblVar.c);
118:             default:
119:                 return m350Var;
120:         }
121:     }
122: 
123:     @Override
124:     public boolean r() {
125:         switch (this.d) {
126:             case 13:
127:                 return false;
128:             case 14:
129:                 return false;
```

## `defpackage/bqk.java`
### line 194
```java
182:                 List<String> pathSegments = uri.getPathSegments();
183:                 if (pathSegments.size() != 3 || !ya90.K(pathSegments.get(0), "apps", true)) {
184:                     return null;
185:                 }
186:                 cqk cqkVar = dqk.Companion;
187:                 String str = pathSegments.get(2);
188:                 cqkVar.getClass();
189:                 if (!ya90.P(str, "app_", false) && !ya90.P(str, "asdk_app_", false) && !ya90.P(str, "connector_", false)) {
190:                     return null;
191:                 }
192:                 return new dqk("/apps/" + ((Object) pathSegments.get(1)) + "/" + ((Object) pathSegments.get(2)));
193:             case 4:
194:                 String queryParameter = uri.getQueryParameter("pairing_code");
195:                 if (queryParameter == null || (string = qa90.W0(queryParameter).toString()) == null || (strE = ra90.e(string)) == null) {
196:                     return null;
197:                 }
198:                 return new luk(strE);
199:             case 12:
200:                 u9l u9lVar = (u9l) m350Var;
201:                 String lastPathSegment = uri.getLastPathSegment();
202:                 return ((lastPathSegment == null || !ya90.P(lastPathSegment, "p_", false)) && (lastPathSegment == null || !ya90.P(lastPathSegment, "w_", false))) ? u9lVar : new u9l(lastPathSegment, u9lVar.b);
203:             case 16:
204:                 return new odl(UUID.randomUUID().toString());
205:             default:
206:                 return m350Var;
```

## `defpackage/df70.java`
### line 32
```java
20:     public static final String a(String str) {
21:         yxb0 txb0Var;
22:         Set set = a;
23:         if (qa90.W(str, '?')) {
24:             Uri uri = Uri.parse(str);
25:             if (!uri.isHierarchical()) {
26:                 return null;
27:             }
28:             String encodedQuery = uri.getEncodedQuery();
29:             if (encodedQuery != null) {
30:                 try {
31:                     URLDecoder.decode(encodedQuery, StandardCharsets.UTF_8.name());
32:                     Set<String> queryParameterNames = uri.getQueryParameterNames();
33:                     Set<String> set2 = queryParameterNames;
34:                     if (!(set2 instanceof Collection) || !set2.isEmpty()) {
35:                         Iterator<T> it = set2.iterator();
36:                         while (it.hasNext()) {
37:                             if (set.contains((String) it.next())) {
38:                                 Uri.Builder builderClearQuery = uri.buildUpon().clearQuery();
39:                                 for (String str2 : queryParameterNames) {
40:                                     if (!set.contains(str2)) {
41:                                         Iterator<T> it2 = uri.getQueryParameters(str2).iterator();
42:                                         while (it2.hasNext()) {
43:                                             builderClearQuery.appendQueryParameter(str2, (String) it2.next());
44:                                         }
```

## `defpackage/k390.java`
### line 11
```java
1: package defpackage;
2: 
3: import java.util.Map;
4: 
5: public final class k390 {
6:     public final ud40 a;
7:     public final qn c;
8:     public final d970 e;
9:     public final d970 f;
10:     public nc40 g;
11:     public final gev b = wnm.F(6, "StickyChatModelSelectionStore");
12:     public final f2y d = new f2y();
13: 
14:     public k390(pn pnVar, ud40 ud40Var) {
15:         this.a = ud40Var;
16:         this.c = new qn(pnVar, "selected_chat_model_version", h390.Companion.serializer(), new h390(null, null, null), 48);
17:         d970 d970VarD = xt0.d(1, 0, 0, 6);
18:         this.e = d970VarD;
19:         this.f = d970VarD;
20:         bvj.t(ud40Var.j, pnVar.b, new bj0(this, null, (byte) 9));
21:     }
22: 
23:     public final Object a(nc40 nc40Var, rsg rsgVar) throws Throwable {
```

## `defpackage/kwk.java`
### line 26
```java
14:     static {
15:         kwk kwkVar = new kwk();
16:         a = kwkVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("s-rGmFROrBfkMeKiporfCw2bDCAUjsOHJa_0ehwCz4U=", kwkVar, 12);
18:         pluginGeneratedSerialDescriptor.k("prompt", false);
19:         pluginGeneratedSerialDescriptor.k("starterPromptId", true);
20:         pluginGeneratedSerialDescriptor.k("suggestionType", true);
21:         pluginGeneratedSerialDescriptor.k("suggestedAutomationType", true);
22:         pluginGeneratedSerialDescriptor.k("suggestionId", true);
23:         pluginGeneratedSerialDescriptor.k("isHiddenMessage", true);
24:         pluginGeneratedSerialDescriptor.k("messageMetadata", true);
25:         pluginGeneratedSerialDescriptor.k("submissionContext", true);
26:         pluginGeneratedSerialDescriptor.k("allowWhenLoggedIn", true);
27:         pluginGeneratedSerialDescriptor.k("imagePromptId", true);
28:         pluginGeneratedSerialDescriptor.k("modelSelection", true);
29:         pluginGeneratedSerialDescriptor.k("useAccountDefaultModel", true);
30:         descriptor = pluginGeneratedSerialDescriptor;
31:     }
32: 
33:     @Override
34:     public final KSerializer[] childSerializers() {
35:         da90 da90Var = da90.a;
36:         KSerializer kSerializerR0 = q2v.r0(da90Var);
37:         KSerializer kSerializerR1 = q2v.r0(da90Var);
38:         KSerializer kSerializerR2 = q2v.r0(da90Var);
```

## `defpackage/mm2.java`
### line 32
```java
20:         pluginGeneratedSerialDescriptor.k("title", true);
21:         pluginGeneratedSerialDescriptor.k("shortDescription", true);
22:         pluginGeneratedSerialDescriptor.k("prompt", true);
23:         pluginGeneratedSerialDescriptor.k("iconUrl", true);
24:         pluginGeneratedSerialDescriptor.k("iconUrlDark", true);
25:         pluginGeneratedSerialDescriptor.k("icon", true);
26:         pluginGeneratedSerialDescriptor.k("modelType", true);
27:         pluginGeneratedSerialDescriptor.k("thinkingEffort", true);
28:         pluginGeneratedSerialDescriptor.k("connectorId", true);
29:         pluginGeneratedSerialDescriptor.k("appId", true);
30:         pluginGeneratedSerialDescriptor.k("systemHints", true);
31:         pluginGeneratedSerialDescriptor.k("destinationMetadata", true);
32:         pluginGeneratedSerialDescriptor.k("autoSend", true);
33:         descriptor = pluginGeneratedSerialDescriptor;
34:     }
35: 
36:     @Override
37:     public final KSerializer[] childSerializers() {
38:         da90 da90Var = da90.a;
39:         KSerializer kSerializerR0 = q2v.r0(da90Var);
40:         KSerializer kSerializerR1 = q2v.r0(da90Var);
41:         lht lhtVar = lht.a;
42:         return new KSerializer[]{kSerializerR0, da90Var, kSerializerR1, da90Var, q2v.r0(lhtVar), q2v.r0(lhtVar), q2v.r0(pm2.a), q2v.r0(lhtVar), q2v.r0(lhtVar), q2v.r0(lhtVar), q2v.r0(lhtVar), q2v.r0(lhtVar), q2v.r0(xdl.a), wh6.a};
43:     }
44: 
```

## `defpackage/nj90.java`
### line 14
```java
2: 
3: @ii60
4: public final class nj90 {
5:     public static final mj90 Companion;
6:     public static final uzt a;
7:     public static final nj90 b;
8:     public static final nj90 c;
9:     public static final nj90[] d;
10: 
11:     static {
12:         nj90 nj90Var = new nj90("PrefillComposer", 0);
13:         b = nj90Var;
14:         nj90 nj90Var2 = new nj90("AutoSend", 1);
15:         c = nj90Var2;
16:         d = new nj90[]{nj90Var, nj90Var2};
17:         Companion = new mj90();
18:         a = f9t.F(2, new l990((byte) 28));
19:     }
20: 
21:     public static nj90 valueOf(String str) {
22:         return (nj90) Enum.valueOf(nj90.class, str);
23:     }
24: 
25:     public static nj90[] values() {
26:         return (nj90[]) d.clone();
```

## `defpackage/nx1.java`
### line 20
```java
8: import kotlinx.serialization.internal.PluginGeneratedSerialDescriptor;
9: 
10: public final class nx1 implements dxp {
11:     public static final nx1 a;
12:     private static final SerialDescriptor descriptor;
13: 
14:     static {
15:         nx1 nx1Var = new nx1();
16:         a = nx1Var;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("prompt", nx1Var, 6);
18:         pluginGeneratedSerialDescriptor.k("prompt", false);
19:         pluginGeneratedSerialDescriptor.k("entrypoint", true);
20:         pluginGeneratedSerialDescriptor.k("autoSend", true);
21:         pluginGeneratedSerialDescriptor.k("developerMessage", true);
22:         pluginGeneratedSerialDescriptor.k("inputRequirements", true);
23:         pluginGeneratedSerialDescriptor.k("showPromptOnHover", true);
24:         pluginGeneratedSerialDescriptor.m(new v10((byte) 3));
25:         descriptor = pluginGeneratedSerialDescriptor;
26:     }
27: 
28:     @Override
29:     public final KSerializer[] childSerializers() {
30:         uzt[] uztVarArr = px1.g;
31:         da90 da90Var = da90.a;
32:         wh6 wh6Var = wh6.a;
```

## `defpackage/q6f0.java`
### line 146
```java
134: 
135:     public final void b(Uri uri) {
136:         Object txb0Var;
137:         Object xxb0Var;
138:         Throwable webAuthFailed;
139:         o6f0 o6f0Var = this.h;
140:         if (o6f0Var == null) {
141:             return;
142:         }
143:         Uri uri2 = Uri.parse(this.a.s.c);
144:         if (uri == null || !wnm.k(uri.getScheme(), uri2.getScheme()) || !wnm.k(uri.getHost(), uri2.getHost()) || !wnm.k(uri.getPath(), uri2.getPath())) {
145:             txb0Var = new txb0(new AuthError.WebAuthFailed("Authorization callback did not match the configured redirect URI", o6f0Var.c(), 4));
146:         } else if (wnm.k(uri.getQueryParameter("state"), o6f0Var.a().c())) {
147:             String queryParameter = uri.getQueryParameter("error");
148:             if (queryParameter != null) {
149:                 String queryParameter2 = uri.getQueryParameter("error_description");
150:                 ju4 ju4VarA = ju4.a(o6f0Var.c(), null, null, queryParameter, null, null, 223);
151:                 if (o6f0Var.d() == l8f0.b && i.contains(queryParameter)) {
152:                     webAuthFailed = new AuthError.NoCredentialsAvailable(ju4VarA);
153:                 } else {
154:                     String str = queryParameter.equalsIgnoreCase("access_denied") ? "Permissions were not granted. Try again." : "An unexpected error occurred.";
155:                     if (queryParameter2 == null) {
156:                         queryParameter2 = str;
157:                     }
158:                     webAuthFailed = new AuthError.WebAuthFailed(queryParameter2, ju4VarA, 4);
```

### line 162
```java
150:                 ju4 ju4VarA = ju4.a(o6f0Var.c(), null, null, queryParameter, null, null, 223);
151:                 if (o6f0Var.d() == l8f0.b && i.contains(queryParameter)) {
152:                     webAuthFailed = new AuthError.NoCredentialsAvailable(ju4VarA);
153:                 } else {
154:                     String str = queryParameter.equalsIgnoreCase("access_denied") ? "Permissions were not granted. Try again." : "An unexpected error occurred.";
155:                     if (queryParameter2 == null) {
156:                         queryParameter2 = str;
157:                     }
158:                     webAuthFailed = new AuthError.WebAuthFailed(queryParameter2, ju4VarA, 4);
159:                 }
160:                 xxb0Var = new txb0(webAuthFailed);
161:             } else {
162:                 String queryParameter3 = uri.getQueryParameter("code");
163:                 if (queryParameter3 == null || qa90.l0(queryParameter3)) {
164:                     txb0Var = new txb0(new AuthError.MissingResponse(o6f0Var.c()));
165:                 } else {
166:                     xxb0Var = new xxb0(new n6f0(queryParameter3, o6f0Var.c()));
167:                 }
168:             }
169:             txb0Var = xxb0Var;
170:         } else {
171:             txb0Var = new txb0(new AuthError.WebAuthFailed("The received state is invalid. Try again.", o6f0Var.c(), 4));
172:         }
173:         if (this.h == o6f0Var) {
174:             this.h = null;
```

## `defpackage/ru2.java`
### line 25
```java
13:     private static final SerialDescriptor descriptor;
14: 
15:     static {
16:         ru2 ru2Var = new ru2();
17:         a = ru2Var;
18:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("ErWaqu8nlLEPpDDX6O0ZNX9-vY0Ur_HTtftzlzHQFHU=", ru2Var, 17);
19:         pluginGeneratedSerialDescriptor.k("id", false);
20:         pluginGeneratedSerialDescriptor.k("title", false);
21:         pluginGeneratedSerialDescriptor.k("badgeText", true);
22:         pluginGeneratedSerialDescriptor.k("description", false);
23:         pluginGeneratedSerialDescriptor.k("oneliner", false);
24:         pluginGeneratedSerialDescriptor.k("prompt", false);
25:         pluginGeneratedSerialDescriptor.k("autoSend", true);
26:         pluginGeneratedSerialDescriptor.k("hideFirstMessage", true);
27:         pluginGeneratedSerialDescriptor.k("category", false);
28:         pluginGeneratedSerialDescriptor.k("theme", true);
29:         pluginGeneratedSerialDescriptor.k("emoji", true);
30:         pluginGeneratedSerialDescriptor.k("iconUrl", true);
31:         pluginGeneratedSerialDescriptor.k("icon", true);
32:         pluginGeneratedSerialDescriptor.k("destination", true);
33:         pluginGeneratedSerialDescriptor.k("destinationMetadata", true);
34:         pluginGeneratedSerialDescriptor.k("systemHints", true);
35:         pluginGeneratedSerialDescriptor.k("completed", true);
36:         descriptor = pluginGeneratedSerialDescriptor;
37:     }
```

## `defpackage/s7j.java`
### line 106
```java
94:             if ((i & Integer.MIN_VALUE) != 0) {
95:                 r7jVar.q = i - Integer.MIN_VALUE;
96:             } else {
97:                 r7jVar = new r7j(this, rsgVar);
98:             }
99:         } else {
100:             r7jVar = new r7j(this, rsgVar);
101:         }
102:         Object obj = r7jVar.o;
103:         int i2 = r7jVar.q;
104:         if (i2 == 0) {
105:             ct40.j(obj);
106:             if (szv.y(uri) && !wnm.k(uri.getQueryParameter("noauth"), "true") && (queryParameter = (uriI = szv.I(uri, "temporary_audio")).getQueryParameter("conversation_id")) != null) {
107:                 fnc0 fnc0VarH = ix40.h(uriI.toString());
108:                 r7jVar.n = queryParameter;
109:                 r7jVar.q = 1;
110:                 Serializable serializableI2 = this.c.i2(fnc0VarH, r7jVar);
111:                 wqi wqiVar = wqi.a;
112:                 if (serializableI2 == wqiVar) {
113:                     return wqiVar;
114:                 }
115:                 obj = serializableI2;
116:                 str = queryParameter;
117:             }
118:             return null;
```

## `defpackage/siw.java`
### line 5
```java
1: package defpackage;
2: 
3: @ii60(with = riw.class)
4: public final class siw {
5:     AutoSend("auto_send"),
6:     TargetedReply("targeted_reply"),
7:     FillComposer("fill_composer"),
8:     Unknown("unknown");
9: 
10:     public static final piw Companion = new piw();
11:     public static final hon e;
12:     public final String a;
13: 
14:     static {
15:         e = new hon(new siw[]{r0, r1, r2, r3});
16:     }
17: 
```

## `defpackage/xb70.java`
### line 14
```java
2: 
3: @ii60
4: public final class xb70 {
5:     public static final wb70 Companion;
6:     public static final uzt a;
7:     public static final xb70 b;
8:     public static final xb70 c;
9:     public static final xb70[] d;
10: 
11:     static {
12:         xb70 xb70Var = new xb70("PrefillOnly", 0);
13:         b = xb70Var;
14:         xb70 xb70Var2 = new xb70("AutoSend", 1);
15:         c = xb70Var2;
16:         d = new xb70[]{xb70Var, xb70Var2};
17:         Companion = new wb70();
18:         a = f9t.F(2, new us60((byte) 18));
19:     }
20: 
21:     public static xb70 valueOf(String str) {
22:         return (xb70) Enum.valueOf(xb70.class, str);
23:     }
24: 
25:     public static xb70[] values() {
26:         return (xb70[]) d.clone();
```

_files=14; excerpts=16_