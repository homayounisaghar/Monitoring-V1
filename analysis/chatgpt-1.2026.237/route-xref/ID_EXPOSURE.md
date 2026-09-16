# ID_EXPOSURE

## `defpackage/i3i.java`
### line 187
```java
175:             if (!it.hasNext()) {
176:                 next = null;
177:                 break;
178:             }
179:             next = it.next();
180:         } while (!((jyg) next).a.equals(stringExtra2));
181:         jyg jygVar = (jyg) next;
182:         if (jygVar == null) {
183:             jygVar = jyg.Unknown;
184:         }
185:         this.c.b(jygVar, stringExtra);
186:         if (jygVar == jyg.ScreenShare && stringExtra != null) {
187:             String stringExtra3 = intent.getStringExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID");
188:             String str = stringExtra3 != null ? stringExtra3 : null;
189:             n3i n3iVar = this.b;
190:             n3iVar.e(stringExtra);
191:             if (str != null) {
192:                 n3iVar.d(Collections.singletonList(new zch(str)));
193:             }
194:             lr50Var = new lr50(stringExtra, cm7.v(intent), str, 0);
195:         }
196:         if (lr50Var != null || intent.hasExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SOURCE") || intent.hasExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID")) {
197:             this.h = lr50Var;
198:         }
199:     }
```

## `defpackage/ot.java`
### line 150
```java
138:     }
139: 
140:     public static final PendingIntent b(Application application, xxg xxgVar, String str, String str2, jyg jygVar, zxg zxgVar) {
141:         String str3 = xxgVar.b;
142:         String str4 = xxgVar.a;
143:         int iHashCode = (str3 + ":" + str4).hashCode() ^ 95468318;
144:         Intent intent = new Intent(zxgVar.a, (Class<?>) ConversationBubbleDeletedReceiver.class);
145:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_PARENT_CHANNEL_ID", str3);
146:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CHANNEL_ID", xxgVar.c);
147:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_NOTIFICATION_TAG", xxgVar.d);
148:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_NOTIFICATION_INT_ID", xxgVar.e);
149:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID", str4);
150:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID", str);
151:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_NOTIFICATION_ID", str2);
152:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SOURCE", jygVar.a);
153:         return PendingIntent.getBroadcast(application, iHashCode, intent, 201326592);
154:     }
155: 
156:     public static final String c(String str, String str2) {
157:         return Build.VERSION.SDK_INT >= 29 ? jtz.o(str, ".", str2) : str;
158:     }
159: 
160:     public static final PendingIntent d(Application application, Uri uri, String str, String str2, jyg jygVar, Bundle bundle) {
161:         Intent intentPutExtra = zc80.I(application, uri, true).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID", str).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID", str2).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SOURCE", jygVar.a);
162:         if (bundle != null) {
```

### line 169
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
166:     }
167: 
168:     public static final Intent e(Application application, Uri uri, String str, String str2, jyg jygVar, Bundle bundle) {
169:         Intent intentPutExtra = zc80.I(application, uri, true).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID", str).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID", str2).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SOURCE", jygVar.a);
170:         if (bundle != null) {
171:             intentPutExtra.putExtras(bundle);
172:         }
173:         return intentPutExtra;
174:     }
175: 
176:     public static final void f(Context context, String str, String str2, String str3, String str4) {
177:         NotificationManager notificationManager;
178:         NotificationChannel notificationChannel;
179:         int i = Build.VERSION.SDK_INT;
180:         if (i < 29 || (notificationManager = (NotificationManager) context.getSystemService(NotificationManager.class)) == null || (notificationChannel = notificationManager.getNotificationChannel(str)) == null) {
181:             return;
```

_files=2; excerpts=3_