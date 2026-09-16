# CONVERSATION_ID_READSIDE

## `defpackage/i3i.java`
### line 187
```java
183:             jygVar = jyg.Unknown;
184:         }
185:         this.c.b(jygVar, stringExtra);
186:         if (jygVar == jyg.ScreenShare && stringExtra != null) {
187:             String stringExtra3 = intent.getStringExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID");
188:             String str = stringExtra3 != null ? stringExtra3 : null;
189:             n3i n3iVar = this.b;
190:             n3iVar.e(stringExtra);
191:             if (str != null) {
```

## `defpackage/lt.java`
### line 62
```java
58:         this.s = mz80VarM4;
59:         psg psgVar = null;
60:         byte b = 2;
61:         yn ynVar = new yn(mz80VarM, mz80VarM3, new mm(3, psgVar, b), (byte) 2);
62:         asg asgVarD = vqi.d(asgVarA, "ActivelyStreamingConversationRepository/conversationIds");
63:         g6h g6hVar = zc70.a;
64:         this.t = cea0.R(ynVar, asgVarD, g6hVar, ggnVar);
65:         this.u = cea0.R(new jt(mz80VarM3, (byte) 0), vqi.d(asgVarA, "ActivelyStreamingConversationRepository/pollingIds"), g6hVar, ggnVar);
66:         this.v = mz80VarM4;
```

## `defpackage/ot.java`
### line 150
```java
146:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CHANNEL_ID", xxgVar.c);
147:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_NOTIFICATION_TAG", xxgVar.d);
148:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_NOTIFICATION_INT_ID", xxgVar.e);
149:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID", str4);
150:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID", str);
151:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_NOTIFICATION_ID", str2);
152:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SOURCE", jygVar.a);
153:         return PendingIntent.getBroadcast(application, iHashCode, intent, 201326592);
154:     }
```

### line 161
```java
157:         return Build.VERSION.SDK_INT >= 29 ? jtz.o(str, ".", str2) : str;
158:     }
159: 
160:     public static final PendingIntent d(Application application, Uri uri, String str, String str2, jyg jygVar, Bundle bundle) {
161:         Intent intentPutExtra = zc80.I(application, uri, true).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID", str).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID", str2).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SOURCE", jygVar.a);
162:         if (bundle != null) {
163:             intentPutExtra.putExtras(bundle);
164:         }
165:         return PendingIntent.getActivity(application, str2.hashCode(), intentPutExtra.addFlags(524288), 167772160);
```

### line 169
```java
165:         return PendingIntent.getActivity(application, str2.hashCode(), intentPutExtra.addFlags(524288), 167772160);
166:     }
167: 
168:     public static final Intent e(Application application, Uri uri, String str, String str2, jyg jygVar, Bundle bundle) {
169:         Intent intentPutExtra = zc80.I(application, uri, true).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID", str).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID", str2).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SOURCE", jygVar.a);
170:         if (bundle != null) {
171:             intentPutExtra.putExtras(bundle);
172:         }
173:         return intentPutExtra;
```

_files_with_hits=3; excerpts=5_
